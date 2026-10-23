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
import argparse, fcntl, hashlib, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

sys.path.insert(0, os.path.expanduser("~/agentes-partners/lib"))
from cnpj import cnpj_valido, normalizar_cnpj  # noqa: E402
from . import dossie as DS  # noqa: E402
from . import dossie_base as DB  # noqa: E402
from . import negocio_ativo as NA  # noqa: E402

DIR = NA.DIR
RAIZ_REPO = Path(__file__).resolve().parents[3]
REUSO_DIAS = 30           # pedido entregue há menos disso é reaproveitado (não refaz a mesma empresa)
CONSULTA_VALE_DIAS = 7    # consulta guardada vale este tempo sem nova chamada às APIs
HISTORICO_MAX = 30
BLOCOS = ("fazer", "precisa", "falta")
ABERTOS = ("recebida", "aguardando_aprovacao", "revisao_humana")
ROTULO = {"recebida": "Em análise pelos agentes", "aguardando_aprovacao": "Em revisão final", "revisao_humana": "Em revisão final",
          "entregue": "Pronta"}


class Recusa(Exception):
    """Pedido que não pode seguir; a mensagem é segura para mostrar ao parceiro."""


def _arq(id_):
    return os.path.join(DIR, "pedidos", id_ + ".json")


def _trava():
    os.makedirs(DIR, exist_ok=True)
    f = open(os.path.join(DIR, ".trava"), "w")
    fcntl.flock(f, fcntl.LOCK_EX)
    return f


def _ler(id_):
    try:
        with open(_arq(id_)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _gravar(p):
    os.makedirs(os.path.join(DIR, "pedidos"), exist_ok=True)
    tmp = _arq(p["id"]) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
    os.replace(tmp, _arq(p["id"]))


def _todos():
    pasta = os.path.join(DIR, "pedidos")
    return [p for p in (_ler(n[:-5]) for n in sorted(os.listdir(pasta)) if n.endswith(".json")) if p] if os.path.isdir(pasta) else []


def _agora():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def solicitar(cnpj, parceiro, consulta=None):
    """Cria o pedido e já entrega o dossiê-base (milissegundos). Os agentes aprofundam depois (enriquecer).
    Reaproveita o pedido aberto, ou o entregue há menos de REUSO_DIAS, da mesma empresa e do mesmo parceiro."""
    c = normalizar_cnpj(cnpj)
    if not cnpj_valido(c):
        raise Recusa("CNPJ inválido.")
    ativo = NA.tem_negocio_ativo(c)
    if ativo is None:
        raise Recusa("Não foi possível conferir a base agora. Tente de novo mais tarde.")
    if ativo:
        raise Recusa("Empresa com negócio ativo na base Save Company.")
    corte = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() - REUSO_DIAS * 86400))
    with _trava():
        todos = _todos()
        for p in todos:
            if p["cnpj"] == c and p["parceiro"] == parceiro and (p["status"] in ABERTOS or (p["status"] == "entregue" and p["criado"] >= corte)):
                return p
        n = 1 + max([int(p["id"][2:]) for p in todos] or [0])
        p = {"id": "E-%04d" % n, "cnpj": c, "parceiro": parceiro, "criado": _agora(), "status": "recebida", "nivel": None,
             "enriquecer": "pendente" if os.environ.get("CENTRAL_ENRIQUECER", "1") == "1" else "nao",
             "consulta": {k: (consulta or {}).get(k) for k in ("faixa", "titulo", "ano_base", "fonte", "perfil")}, "resultado": None,
             "historico": [{"quando": _agora(), "evento": "recebida"}]}
        _gravar(p)
    perfil = p["consulta"].get("perfil")
    if perfil:  # dossiê-base na hora; se falhar, o pedido segue "recebida" para os agentes
        try:
            return publicar(p["id"], DB.montar(perfil, p["consulta"].get("faixa")), origem="base")
        except Recusa:
            pass
    return p


def visao_parceiro(p):
    """O que o parceiro pode ver: andamento e, só depois de entregue, o resultado."""
    v = {"id": p["id"], "status": p["status"], "andamento": ROTULO.get(p["status"], p["status"]), "nivel": p.get("nivel"),
         "aprofundando": p.get("enriquecer") == "pendente" and p["status"] == "entregue"}
    if p["status"] == "entregue":
        v["resultado"] = p["resultado"]
        v["arquivo"] = True  # o Word é gerado na hora do download, se ainda não existir
    return v


# ---------- histórico do parceiro (últimas empresas, sem chamar a API de novo) ----------
def _arq_hist(parceiro):
    return os.path.join(DIR, "historico", hashlib.sha256(parceiro.encode()).hexdigest()[:16] + ".json")


def _hist_ler(parceiro):
    try:
        with open(_arq_hist(parceiro)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def registrar_consulta(parceiro, resultado):
    """Guarda a consulta feita (a mais recente de cada CNPJ, no máximo HISTORICO_MAX). CNPJ inválido ou indisponível não entra."""
    if resultado.get("faixa") in ("invalido", "indisponivel") or not resultado.get("cnpj"):
        return
    with _trava():
        h = [x for x in _hist_ler(parceiro) if x["cnpj"] != resultado["cnpj"]]
        h.insert(0, {"cnpj": resultado["cnpj"], "quando": _agora(), "resultado": resultado})
        os.makedirs(os.path.join(DIR, "historico"), exist_ok=True)
        tmp = _arq_hist(parceiro) + ".tmp"
        with open(tmp, "w") as f:
            json.dump(h[:HISTORICO_MAX], f, ensure_ascii=False)
        os.replace(tmp, _arq_hist(parceiro))


def consulta_guardada(parceiro, cnpj, dias=CONSULTA_VALE_DIAS):
    """Consulta já feita por este parceiro há menos de `dias` (evita nova chamada às APIs)."""
    corte = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() - dias * 86400))
    return next((x["resultado"] for x in _hist_ler(parceiro) if x["cnpj"] == normalizar_cnpj(cnpj) and x["quando"] >= corte), None)


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


def arquivo_do_parceiro(id_, parceiro):
    """Caminho do Word, só para o dono do pedido e só depois de entregue."""
    p = _ler(id_)
    if not (p and p["parceiro"] == parceiro and p["status"] == "entregue"):
        return None
    if not os.path.exists(_docx(id_)):  # dossiê-base: o Word só é montado quando alguém pede
        perfil = (p["consulta"] or {}).get("perfil") or {}
        md = DS.para_markdown("Dossiê da empresa: %s" % (perfil.get("razao") or id_), "Briefing, como a Save pode ajudar, serviços aderentes e abordagem", p["resultado"]["dossie"])
        try:
            DS.gerar_docx(md, _docx(id_))
        except (RuntimeError, OSError, subprocess.SubprocessError):
            return None
    return _docx(id_)


def ler_do_parceiro(id_, parceiro):
    p = _ler(id_)
    return visao_parceiro(p) if p and p["parceiro"] == parceiro else None


def _texto(r):
    partes = [DS.texto(r.get("dossie") or [])] + [str(r.get(b, "")) for b in BLOCOS] + [str(x.get(k, "")) for x in r.get("esteira", []) for k in ("produto", "nota")]
    return "\n".join(partes)


def auditar(texto):
    """(ok, achados). ok = sem alerta ALTO/MÉDIO no auditor de promessas do depto-qualidade."""
    script = RAIZ_REPO / "skills/depto-qualidade/scripts/auditar_texto.py"
    if not script.exists():
        script = Path(os.path.expanduser("~/.claude/skills/depto-qualidade/scripts/auditar_texto.py"))
    with tempfile.TemporaryDirectory() as d:
        arq = os.path.join(d, "entrega.md")
        with open(arq, "w") as f:
            f.write(texto)
        r = subprocess.run([sys.executable, "-I", str(script), arq, "--json"], capture_output=True, text=True, timeout=60)
    if r.returncode == 2:
        return False, [{"erro": "auditor indisponível"}]  # falha fechada: sem auditoria não entrega
    try:
        achados = [a for res in json.loads(r.stdout).values() for a in (res.get("achados") if isinstance(res, dict) else res or [])]
    except (ValueError, AttributeError):
        achados = []
    return r.returncode == 0, achados


def _decidir(p, ok):
    if not ok:
        return "revisao_humana"
    return "entregue" if os.environ.get("CENTRAL_APROVACAO", "obrigatoria") == "autonoma" else "aguardando_aprovacao"


def publicar(id_, resultado, anexo=None, origem="agentes"):
    faltam = [b for b in BLOCOS if not str(resultado.get(b, "")).strip()]
    if faltam:
        raise Recusa("Faltam blocos: " + ", ".join(faltam))
    if not DS.valido(resultado.get("dossie")):
        raise Recusa("O dossiê precisa de %d seções ou mais, cada uma com título e conteúdo." % DS.SECOES_MINIMAS)
    ok, achados = auditar(_texto(resultado))
    with _trava():
        p = _ler(id_)
        if not p or p["status"] != "recebida":
            raise Recusa("Pedido inexistente ou já tratado.")
        p["resultado"] = resultado
        if anexo:
            shutil.copyfile(anexo, _docx(id_))
        p["auditoria"] = {"ok": ok, "alertas": len(achados)}
        p["status"] = _decidir(p, ok)
        p["nivel"] = "base" if origem == "base" else "agentes"
        if origem != "base" and p.get("enriquecer") == "pendente":
            p["enriquecer"] = "feito"
        p["historico"].append({"quando": _agora(), "evento": p["status"], "origem": origem, "auditoria_ok": ok})
        _gravar(p)
        return p


def enriquecer(id_, resultado, anexo=None):
    """Troca o dossiê-base pelo dossiê aprofundado pelos agentes. Só substitui se a auditoria passar; com alerta, mantém
    a versão atual e registra o alerta (nunca entrega texto com promessa)."""
    faltam = [b for b in BLOCOS if not str(resultado.get(b, "")).strip()]
    if faltam or not DS.valido(resultado.get("dossie")):
        raise Recusa("Resultado incompleto: três blocos e dossiê com %d seções ou mais." % DS.SECOES_MINIMAS)
    ok, achados = auditar(_texto(resultado))
    with _trava():
        p = _ler(id_)
        if not p or p.get("enriquecer") != "pendente" or p["status"] not in ("entregue", "aguardando_aprovacao", "revisao_humana"):
            raise Recusa("Nada a aprofundar neste pedido.")
        p["enriquecer"] = "feito" if ok else "alerta"
        if ok:
            p["resultado"] = resultado; p["nivel"] = "agentes"; p["auditoria"] = {"ok": True, "alertas": len(achados)}
            if anexo:
                shutil.copyfile(anexo, _docx(id_))
        p["historico"].append({"quando": _agora(), "evento": "aprofundado" if ok else "aprofundamento_barrado", "auditoria_ok": ok, "alertas": len(achados)})
        _gravar(p)
        return p


def aprovar(id_, quem):
    with _trava():
        p = _ler(id_)
        if not p or p["status"] not in ("aguardando_aprovacao", "revisao_humana"):
            raise Recusa("Nada a aprovar neste pedido.")
        p["status"] = "entregue"
        p["historico"].append({"quando": time.strftime("%Y-%m-%dT%H:%M:%S"), "evento": "aprovado", "por": quem})
        _gravar(p)
        return p


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["fila", "status", "publicar", "enriquecer", "aprovar"])
    ap.add_argument("--id"); ap.add_argument("--arquivo"); ap.add_argument("--quem"); ap.add_argument("--anexo", help="Word do dossiê (opcional)")
    ap.add_argument("--gerar-docx", action="store_true", help="gera o Word do dossiê a partir do resultado e anexa")
    a = ap.parse_args()
    if a.cmd == "fila":
        # "recebida" (sem dossiê-base) e "enriquecer pendente" (dossiê-base já entregue; os agentes aprofundam)
        print(json.dumps([{k: p.get(k) for k in ("id", "cnpj", "parceiro", "criado", "consulta", "status", "enriquecer", "resultado")} for p in _todos()
                          if p["status"] == "recebida" or p.get("enriquecer") == "pendente"], ensure_ascii=False, indent=1))
    elif a.cmd == "status":
        print(json.dumps([{k: p[k] for k in ("id", "status", "parceiro", "criado")} for p in _todos() if not a.id or p["id"] == a.id], ensure_ascii=False, indent=1))
    elif a.cmd in ("publicar", "enriquecer"):
        with open(a.arquivo) as f:
            res = json.load(f)
        anexo = a.anexo
        if a.gerar_docx:
            ped = _ler(a.id) or {}
            emp = (ped.get("consulta") or {}).get("perfil") or {}
            md = DS.para_markdown("Dossiê da empresa: %s" % (emp.get("razao") or a.id), "Briefing, como a Save pode ajudar, serviços aderentes e abordagem", res.get("dossie") or [])
            anexo = DS.gerar_docx(md, os.path.join(tempfile.mkdtemp(), a.id + ".docx"))
        p = (publicar if a.cmd == "publicar" else enriquecer)(a.id, res, anexo)
        print(p["id"], p["status"], p.get("enriquecer"), p.get("auditoria"))
    else:
        print(aprovar(a.id, a.quem or "")["status"])


if __name__ == "__main__":
    try:
        main()
    except Recusa as e:
        sys.exit("ERRO: %s" % e)
