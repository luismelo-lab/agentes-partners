"""Pedido de análise e esteira para o parceiro (Originação do fluxo único, infra/fluxo-unico.md).

O site só grava o pedido e mostra o andamento. Quem analisa são os agentes (rotina `esteira-parceiro`, no GitHub
Actions, ver rotinas/esteira-parceiro.md): quatro checagens, esteira do cliente (depto-solucoes), rascunho em três
blocos (infra/padrao-entrega.md) e auditoria de promessas (depto-qualidade). O resultado só aparece ao parceiro
depois de `publicar`, que passa pela auditoria:

  CENTRAL_APROVACAO=obrigatoria (padrão)  → um aprovador libera (`aprovar`); é o modo do teste.
  CENTRAL_APROVACAO=autonoma              → entrega sozinha SE a auditoria não achar alerta ALTO/MÉDIO;
                                            com alerta, cai na revisão humana. Nunca entrega com alerta.

Estados: recebida → (agentes) → aguardando_aprovacao | revisao_humana | entregue.
A pasta de estado (CENTRAL_ESTEIRA) viaja pelo SharePoint com lib/estado.py; nunca vai para o GitHub.

Uso:  esteira.py fila | status --id E-0001 | publicar --id E-0001 --arquivo resultado.json | aprovar --id E-0001 --quem "Nome"
"""
import argparse, fcntl, hashlib, json, logging, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

sys.path.insert(0, os.path.expanduser("~/agentes-partners/lib"))
from cnpj import cnpj_valido, completar_cnpj  # noqa: E402
from . import dossie as DS  # noqa: E402
from . import dossie_base as DB  # noqa: E402
from . import negocio_ativo as NA  # noqa: E402

log = logging.getLogger("central_api.esteira")

DIR = NA.DIR
RAIZ_REPO = Path(__file__).resolve().parents[3]
REUSO_DIAS = 30           # pedido entregue há menos disso é reaproveitado (não refaz a mesma empresa)
CONSULTA_VALE_DIAS = 7    # consulta guardada vale este tempo sem nova chamada às APIs
HISTORICO_MAX = 30
TENTATIVAS_ENRIQUECER = 2  # o aprofundamento barrado (estado "alerta") pode ser refeito até esta contagem
BLOCOS = ("fazer", "precisa", "falta")
ABERTOS = ("recebida", "aguardando_aprovacao", "revisao_humana")
ROTULO = {"recebida": "Em análise pela Save", "aguardando_aprovacao": "Em revisão final", "revisao_humana": "Em revisão final",
          "entregue": "Pronta"}


_ID = re.compile(r"E-[0-9]{1,9}")
_CHAVES_PEDIDO = {"id", "cnpj", "parceiro", "criado", "status"}
_FMT = "%Y-%m-%dT%H:%M:%S"

# Segunda trava do portão (além do auditor de promessas): texto que nunca vai ao parceiro sem revisão humana.
# É a ÚNICA lista; para mudar a regra, mude aqui e em tests/test_esteira.py (um teste por item).
# Os "R$" só barram perto de palavras de ganho/remuneração: capital social e limites legais do perfil passam.
_PERTO = r"(?:recuper\w*|economi\w*|cr[eé]dito de|ganh\w*|honor[aá]ri\w*|\bfees?\b|comiss\w*)"
_VALOR = r"R\$\s*\d[\d.,]*(?:\s*(?:mil\b|mi\b|milh\w+|bi\b|bilh\w+))?"
TRAVA_REGEX = [
    ("percentual", r"\d+(?:[.,]\d+)?\s*%"),
    ("valor_em_reais_perto_de_ganho", r"%s[^.\n]{0,40}%s|%s[^.\n]{0,40}%s" % (_PERTO, _VALOR, _VALOR, _PERTO)),
    ("fee", r"\bfees?\b"),
    ("comissao", r"comiss(?:ão|ões|ao|oes)"),
    ("honorario", r"honor[aá]ri\w*"),
    ("taxa_de", r"\btaxas? de\b"),
    ("codigo_de_decisao", r"\bD\d{2,3}\b"),
    ("master", r"\bmasters?\b"),
    ("jgm", r"\bJGM\b"),
    ("d_e_s", r"\bD&S\b"),
    ("clientes_da_base", r"clientes da base|na base de clientes"),
    ("escrow", r"\bescrow\b"),
    ("venda_gerencial", r"venda gerencial"),
    ("blindagem", r"blindagem"),
    ("vai_recuperar", r"vai recuperar"),
    ("garantia", r"garantid\w*|\bgarante\b|\bgarantimos\b|garantia de (?:êxito|exito|resultado|retorno|recupera\w+|economia|ganho|R\$)"),  # "garantia" solta (ex.: "banco exige garantia") é dor legítima do playbook
    ("certeza", r"\bcerteza\b"),
]
_TRAVA_RE = [(n, re.compile(r, re.IGNORECASE)) for n, r in TRAVA_REGEX]


class Recusa(Exception):
    """Pedido que não pode seguir; a mensagem é segura para mostrar ao parceiro."""


def _id_ok(id_):
    return isinstance(id_, str) and _ID.fullmatch(id_) is not None


def _arq(id_):
    if not _id_ok(id_):
        raise ValueError("id inválido")  # nunca monta caminho com texto do navegador
    return os.path.join(DIR, "pedidos", id_ + ".json")


def _trava():
    os.makedirs(DIR, exist_ok=True)
    f = open(os.path.join(DIR, ".trava"), "w")
    try:
        fcntl.flock(f, fcntl.LOCK_EX)
    except BaseException:
        f.close()
        raise
    return f


def _ler(id_):
    if not _id_ok(id_):
        return None
    try:
        with open(_arq(id_), encoding="utf-8") as f:
            p = json.load(f)
    except (OSError, ValueError):
        return None
    return p if isinstance(p, dict) and _CHAVES_PEDIDO <= p.keys() and p["id"] == id_ else None


def _gravar_json(caminho, obj, **kw):
    """Escrita atômica: arquivo temporário no mesmo diretório, fsync e rename."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(caminho), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, **kw)
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp, caminho)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _gravar(p):
    _gravar_json(_arq(p["id"]), p, indent=1)


def _todos():
    pasta = os.path.join(DIR, "pedidos")
    if not os.path.isdir(pasta):
        return []
    return [p for p in (_ler(n[:-5]) for n in sorted(os.listdir(pasta)) if n.endswith(".json")) if p]


def _agora():
    return time.strftime(_FMT)


def _corte(dias):
    return time.strftime(_FMT, time.localtime(time.time() - dias * 86400))


def _cnpj(c):
    return completar_cnpj(c)  # zeros à esquerda perdidos (HubSpot, Excel) voltam: uma só forma por empresa


def solicitar(cnpj, parceiro, consulta=None):
    """Cria o pedido e já entrega o dossiê-base (milissegundos). Os agentes aprofundam depois (enriquecer).
    Reaproveita o pedido aberto, ou o entregue há menos de REUSO_DIAS, da mesma empresa e do mesmo parceiro.
    (A chave é o CNPJ completo: filial e matriz da mesma raiz são pedidos distintos, por decisão de produto.)"""
    c = _cnpj(cnpj)
    if not cnpj_valido(c):
        raise Recusa("CNPJ inválido.")
    if not isinstance(parceiro, str) or not parceiro:
        raise Recusa("Parceiro não identificado.")
    ativo = NA.tem_negocio_ativo(c)
    if ativo is None:
        log.info("pedido recusado: motivo=indice_ausente")
        raise Recusa(NA.MSG_NEUTRA)
    if ativo:
        log.info("pedido recusado: motivo=negocio_ativo")
        raise Recusa(NA.MSG_NEUTRA)
    corte = _corte(REUSO_DIAS)
    consulta = consulta if isinstance(consulta, dict) else {}
    with _trava():
        todos = _todos()
        for p in todos:
            if p["cnpj"] == c and p["parceiro"] == parceiro and (p["status"] in ABERTOS or (p["status"] == "entregue" and p["criado"] >= corte)):
                return p
        n = 1 + max([int(p["id"][2:]) for p in todos] or [0])
        p = {"id": "E-%04d" % n, "cnpj": c, "parceiro": parceiro, "criado": _agora(), "status": "recebida", "nivel": None,
             "enriquecer": "pendente" if os.environ.get("CENTRAL_ENRIQUECER", "1") == "1" else "nao",
             "consulta": {k: consulta.get(k) for k in ("faixa", "titulo", "ano_base", "fonte", "perfil")}, "resultado": None,
             "historico": [{"quando": _agora(), "evento": "recebida"}]}
        _gravar(p)
    perfil = p["consulta"].get("perfil")
    if isinstance(perfil, dict):  # dossiê-base na hora; qualquer falha deixa o pedido "recebida" para os agentes (nunca derruba o pedido)
        try:
            return publicar(p["id"], DB.montar(perfil, p["consulta"].get("faixa")), origem="base")
        except Exception as e:  # noqa: BLE001
            sys.stderr.write("dossiê-base não montado (%s); pedido segue para os agentes\n" % type(e).__name__)
    return p


def visao_parceiro(p):
    """O que o parceiro pode ver: andamento e, só depois de entregue, o resultado."""
    v = {"id": p["id"], "status": p["status"], "andamento": ROTULO.get(p["status"], p["status"]), "nivel": p.get("nivel"),
         "aprofundando": p.get("enriquecer") == "pendente" and p["status"] == "entregue"}
    if p["status"] == "entregue":
        v["resultado"] = p.get("resultado")
        v["arquivo"] = True  # o Word é gerado na hora do download, se ainda não existir
    return v


# ---------- histórico do parceiro (últimas empresas, sem chamar a API de novo) ----------
def _arq_hist(parceiro):
    return os.path.join(DIR, "historico", hashlib.sha256(str(parceiro).encode()).hexdigest()[:16] + ".json")


def _hist_ler(parceiro):
    """Lista de entradas válidas; arquivo corrompido ou de outro formato vale como histórico vazio."""
    try:
        with open(_arq_hist(parceiro), encoding="utf-8") as f:
            h = json.load(f)
    except (OSError, ValueError):
        return []
    return [x for x in h if isinstance(x, dict) and isinstance(x.get("cnpj"), str) and isinstance(x.get("quando"), str) and isinstance(x.get("resultado"), dict)] if isinstance(h, list) else []


def registrar_consulta(parceiro, resultado):
    """Guarda a consulta feita (a mais recente de cada CNPJ, no máximo HISTORICO_MAX). CNPJ inválido ou indisponível não entra."""
    if not isinstance(resultado, dict) or resultado.get("faixa") in ("invalido", "indisponivel") or not resultado.get("cnpj"):
        return
    with _trava():
        h = [x for x in _hist_ler(parceiro) if x["cnpj"] != resultado["cnpj"]]
        h.insert(0, {"cnpj": resultado["cnpj"], "quando": _agora(), "resultado": resultado})
        _gravar_json(_arq_hist(parceiro), h[:HISTORICO_MAX])


def consulta_guardada(parceiro, cnpj, dias=CONSULTA_VALE_DIAS):
    """Consulta já feita por este parceiro há menos de `dias` (evita nova chamada às APIs).
    Só vale resultado com dados da empresa, e só se a empresa continua fora da base de negócios ativos: a checagem
    local é refeita a cada uso (um cliente novo não pode sair do histórico como se fosse livre)."""
    c = _cnpj(cnpj)
    corte = _corte(dias)
    r = next((x["resultado"] for x in _hist_ler(parceiro) if x["cnpj"] == c and x["quando"] >= corte), None)
    if not r or not r.get("empresa") or NA.tem_negocio_ativo(c) is not False:
        return None
    return r


def historico(parceiro):
    """Últimas empresas do parceiro, da mais recente para a mais antiga, com o andamento do dossiê de cada uma."""
    pedidos = {p["cnpj"]: p for p in sorted(_todos(), key=lambda p: p["criado"]) if p["parceiro"] == parceiro}
    out = []
    for x in _hist_ler(parceiro):
        r, p = x["resultado"], pedidos.get(x["cnpj"])
        out.append({"cnpj": x["cnpj"], "quando": x["quando"], "razao": (r.get("empresa") or {}).get("razao"), "faixa": r.get("faixa"), "titulo": r.get("titulo"),
                    "ano_base": r.get("ano_base"), "pedido": visao_parceiro(p) if p else None, "resultado": r})
    return out


def _docx(id_):
    return os.path.join(DIR, "pedidos", id_ + ".docx")


def _guardar_docx(origem, id_):
    """Copia o Word para a pasta do pedido de forma atômica (ninguém baixa arquivo pela metade)."""
    destino = _docx(id_)
    tmp = destino + ".%d.part" % os.getpid()
    try:
        shutil.copyfile(origem, tmp)
        os.replace(tmp, destino)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise Recusa("Não foi possível guardar o Word do dossiê.")


def arquivo_do_parceiro(id_, parceiro):
    """Caminho do Word, só para o dono do pedido e só depois de entregue."""
    p = _ler(id_)
    if not (p and p["parceiro"] == parceiro and p["status"] == "entregue" and isinstance(p.get("resultado"), dict)):
        return None
    if not os.path.exists(_docx(id_)):  # dossiê-base: o Word só é montado quando alguém pede
        perfil = ((p.get("consulta") or {}).get("perfil")) or {}
        md = DS.para_markdown("Dossiê da empresa: %s" % (perfil.get("razao") or id_), "Briefing, como a Save pode ajudar, serviços aderentes e abordagem", p["resultado"].get("dossie") or [])
        try:
            DS.gerar_docx(md, _docx(id_))
        except (RuntimeError, OSError, subprocess.SubprocessError, KeyError, TypeError):
            return None
    return _docx(id_)


def ler_do_parceiro(id_, parceiro):
    p = _ler(id_)
    return visao_parceiro(p) if p and p["parceiro"] == parceiro else None


def _folhas(x):
    """Todos os textos do resultado (qualquer campo, qualquer profundidade): é isto que o portão confere."""
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for k, v in x.items():
            yield from _folhas(v)
    elif isinstance(x, (list, tuple)):
        for v in x:
            yield from _folhas(v)
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        yield str(x)


def _texto(r):
    return "\n".join(_folhas(r))


def trava_regex(texto):
    """Nomes das regras da lista de bloqueio (TRAVA_REGEX) que o texto aciona."""
    return [n for n, rx in _TRAVA_RE if rx.search(texto)]


def auditar(texto):
    """(ok, achados). ok = sem alerta ALTO/MÉDIO no auditor de promessas do depto-qualidade E sem acionar a lista de
    bloqueio. Falha fechada em qualquer erro do auditor."""
    bloqueios = trava_regex(texto)
    script = RAIZ_REPO / "skills/depto-qualidade/scripts/auditar_texto.py"
    if not script.exists():
        script = Path(os.path.expanduser("~/.claude/skills/depto-qualidade/scripts/auditar_texto.py"))
    try:
        with tempfile.TemporaryDirectory() as d:
            arq = os.path.join(d, "entrega.md")
            with open(arq, "w", encoding="utf-8") as f:
                f.write(texto)
            r = subprocess.run([sys.executable, "-I", str(script), arq, "--json"], capture_output=True, text=True, encoding="utf-8", timeout=60)
    except (subprocess.SubprocessError, OSError, ValueError):
        return False, [{"erro": "auditor indisponível"}] + [{"trava": n} for n in bloqueios]
    if r.returncode == 2:
        return False, [{"erro": "auditor indisponível"}] + [{"trava": n} for n in bloqueios]  # falha fechada
    try:
        achados = [a for res in json.loads(r.stdout).values() for a in ((res.get("achados") if isinstance(res, dict) else res) or [])]
    except (ValueError, AttributeError, TypeError):
        achados = []
    achados += [{"trava": n} for n in bloqueios]
    return r.returncode == 0 and not bloqueios, achados


def _decidir(p, ok):
    if not ok:
        return "revisao_humana"
    return "entregue" if os.environ.get("CENTRAL_APROVACAO", "obrigatoria") == "autonoma" else "aguardando_aprovacao"


def _conferir(resultado):
    if not isinstance(resultado, dict):
        raise Recusa("Resultado inválido.")
    faltam = [b for b in BLOCOS if not str(resultado.get(b, "")).strip()]
    if faltam:
        raise Recusa("Faltam blocos: " + ", ".join(faltam))
    if not DS.valido(resultado.get("dossie")):
        raise Recusa("O dossiê precisa de %d seções ou mais, cada uma com título e conteúdo." % DS.SECOES_MINIMAS)


def publicar(id_, resultado, anexo=None, origem="agentes"):
    _conferir(resultado)
    ok, achados = auditar(_texto(resultado))
    with _trava():
        p = _ler(id_)
        if not p or p["status"] != "recebida":
            raise Recusa("Pedido inexistente ou já tratado.")
        if anexo:
            _guardar_docx(anexo, id_)
        elif origem != "base" and os.path.exists(_docx(id_)):
            os.unlink(_docx(id_))  # Word antigo não acompanha texto novo
        p["resultado"] = resultado
        p["auditoria"] = {"ok": ok, "alertas": len(achados)}
        p["status"] = _decidir(p, ok)
        p["nivel"] = "base" if origem == "base" else "agentes"
        if origem != "base" and p.get("enriquecer") == "pendente":
            p["enriquecer"] = "feito"
        p.setdefault("historico", []).append({"quando": _agora(), "evento": p["status"], "origem": origem, "auditoria_ok": ok})
        _gravar(p)
        return p


def simular(resultado):
    """Roda os mesmos portões de publicar/enriquecer (blocos, dossiê, auditor e lista de bloqueio) SEM gravar nada.
    Devolve (ok, motivos): motivos é a lista de problemas (texto seguro, sem o trecho do cliente)."""
    try:
        _conferir(resultado)
    except Recusa as e:
        return False, [str(e)]
    ok, achados = auditar(_texto(resultado))
    return ok, [("regra %s" % a["trava"]) if "trava" in a else a["erro"] if "erro" in a else "auditor: %s" % (a.get("nivel") or a.get("tipo") or a.get("regra") or "alerta") for a in achados]


def enriquecer(id_, resultado, anexo=None):
    """Troca o dossiê-base pelo dossiê aprofundado pelos agentes. Só substitui se a auditoria passar; com alerta, mantém
    a versão atual e registra o alerta (nunca entrega texto com promessa)."""
    try:
        _conferir(resultado)
    except Recusa:
        raise Recusa("Resultado incompleto: três blocos e dossiê com %d seções ou mais." % DS.SECOES_MINIMAS)
    ok, achados = auditar(_texto(resultado))
    with _trava():
        p = _ler(id_)
        if not p:
            raise Recusa("Nada a aprofundar neste pedido.")
        tent = int(p.get("tentativas_enriquecer") or 0)
        pode = p.get("enriquecer") == "pendente" or (p.get("enriquecer") == "alerta" and tent < TENTATIVAS_ENRIQUECER)
        if not pode or p["status"] not in ("entregue", "aguardando_aprovacao", "revisao_humana"):
            raise Recusa("Nada a aprofundar neste pedido.")
        p["tentativas_enriquecer"] = tent + 1
        p["enriquecer"] = "feito" if ok else "alerta"
        if ok:
            if anexo:
                _guardar_docx(anexo, id_)
            elif os.path.exists(_docx(id_)):
                os.unlink(_docx(id_))  # o Word do dossiê-base ficou velho: será refeito sob demanda
            p["resultado"] = resultado; p["nivel"] = "agentes"; p["auditoria"] = {"ok": True, "alertas": len(achados)}
        p.setdefault("historico", []).append({"quando": _agora(), "evento": "aprofundado" if ok else "aprofundamento_barrado", "auditoria_ok": ok, "alertas": len(achados)})
        _gravar(p)
        return p


def aprovar(id_, quem):
    with _trava():
        p = _ler(id_)
        if not p or p["status"] not in ("aguardando_aprovacao", "revisao_humana"):
            raise Recusa("Nada a aprovar neste pedido.")
        p["status"] = "entregue"
        p.setdefault("historico", []).append({"quando": _agora(), "evento": "aprovado", "por": quem})
        _gravar(p)
        return p


def expurgar(dias, agora=None):
    """Retenção (LGPD): apaga pedidos, Words e histórico de consultas mais velhos que `dias`. Só código: o agendamento é
    decisão do Luis. Devolve {"pedidos", "words", "historico"}. Cópias no SharePoint (estado.py) não são apagadas aqui."""
    if not isinstance(dias, int) or dias < 1:
        raise Recusa("Informe um prazo de pelo menos 1 dia.")
    corte = time.strftime(_FMT, time.localtime((agora or time.time()) - dias * 86400))
    n = {"pedidos": 0, "words": 0, "historico": 0}
    with _trava():
        pasta = os.path.join(DIR, "pedidos")
        vivos = set()
        for p in _todos():
            if p["criado"] < corte:
                for ext, chave in ((".json", "pedidos"), (".docx", "words")):
                    try:
                        os.unlink(os.path.join(pasta, p["id"] + ext)); n[chave] += 1
                    except OSError:
                        pass
            else:
                vivos.add(p["id"])
        if os.path.isdir(pasta):
            limite = (agora or time.time()) - dias * 86400
            for nome in os.listdir(pasta):  # Word sem pedido (órfão) e restos de gravação interrompida
                m = re.fullmatch(r"(E-[0-9]{1,9})\.docx", nome)
                velho = os.path.getmtime(os.path.join(pasta, nome)) < limite if os.path.exists(os.path.join(pasta, nome)) else False
                if (m and m.group(1) not in vivos) or (nome.endswith((".tmp", ".part")) and velho):
                    try:
                        os.unlink(os.path.join(pasta, nome)); n["words"] += bool(m)
                    except OSError:
                        pass
        hpasta = os.path.join(DIR, "historico")
        if os.path.isdir(hpasta):
            for nome in sorted(os.listdir(hpasta)):
                if not nome.endswith(".json"):
                    continue
                caminho = os.path.join(hpasta, nome)
                try:
                    with open(caminho, encoding="utf-8") as f:
                        h = json.load(f)
                except (OSError, ValueError):
                    continue
                if not isinstance(h, list):
                    continue
                ficam = [x for x in h if isinstance(x, dict) and str(x.get("quando", "")) >= corte]
                n["historico"] += len(h) - len(ficam)
                if not ficam:
                    os.unlink(caminho)
                elif len(ficam) != len(h):
                    _gravar_json(caminho, ficam)
    return n


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["fila", "status", "publicar", "enriquecer", "aprovar", "expurgar"])
    ap.add_argument("--id"); ap.add_argument("--arquivo"); ap.add_argument("--quem"); ap.add_argument("--anexo", help="Word do dossiê (opcional)")
    ap.add_argument("--simular", action="store_true", help="publicar/enriquecer: roda os portões e imprime os motivos, sem gravar")
    ap.add_argument("--dias", type=int, help="expurgar: apaga o que for mais velho que isto (ex.: 365)")
    ap.add_argument("--gerar-docx", action="store_true", help="gera o Word do dossiê a partir do resultado e anexa")
    a = ap.parse_args()
    if a.cmd == "fila":
        # "recebida" (sem dossiê-base) e "enriquecer pendente" (dossiê-base já entregue; os agentes aprofundam)
        print(json.dumps([{k: p.get(k) for k in ("id", "cnpj", "parceiro", "criado", "consulta", "status", "enriquecer", "resultado")} for p in _todos()
                          if p["status"] == "recebida" or p.get("enriquecer") == "pendente"
                          or (p.get("enriquecer") == "alerta" and int(p.get("tentativas_enriquecer") or 0) < TENTATIVAS_ENRIQUECER)], ensure_ascii=False, indent=1))
    elif a.cmd == "status":
        print(json.dumps([{k: p[k] for k in ("id", "status", "parceiro", "criado")} for p in _todos() if not a.id or p["id"] == a.id], ensure_ascii=False, indent=1))
    elif a.cmd == "expurgar":
        if a.dias is None:
            raise Recusa("Informe --dias.")
        print(json.dumps(expurgar(a.dias)))
    elif a.cmd in ("publicar", "enriquecer"):
        if not a.id or not a.arquivo:
            raise Recusa("Informe --id e --arquivo.")
        try:
            with open(a.arquivo, encoding="utf-8") as f:
                res = json.load(f)
        except (OSError, ValueError):
            raise Recusa("Arquivo de resultado ilegível ou inválido.")
        if a.simular:
            ok, motivos = simular(res)
            print(json.dumps({"ok": ok, "motivos": motivos}, ensure_ascii=False)); sys.exit(0 if ok else 1)
        anexo = a.anexo
        if a.gerar_docx:
            ped = _ler(a.id) or {}
            emp = (ped.get("consulta") or {}).get("perfil") or {}
            md = DS.para_markdown("Dossiê da empresa: %s" % (emp.get("razao") or a.id), "Briefing, como a Save pode ajudar, serviços aderentes e abordagem", res.get("dossie") or [])
            with tempfile.TemporaryDirectory() as d:
                anexo = DS.gerar_docx(md, os.path.join(d, "dossie.docx"))
                p = (publicar if a.cmd == "publicar" else enriquecer)(a.id, res, anexo)
        else:
            p = (publicar if a.cmd == "publicar" else enriquecer)(a.id, res, anexo)
        print(p["id"], p["status"], p.get("enriquecer"), p.get("auditoria"))
    else:
        print(aprovar(a.id, a.quem or "")["status"])


if __name__ == "__main__":
    try:
        main()
    except Recusa as e:
        sys.exit("ERRO: %s" % e)
