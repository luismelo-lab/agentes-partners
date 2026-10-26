#!/usr/bin/env python3
"""Caixa de entrada da Central Partners (pedido do Luis, 26/10/2026: "ao invés de subirmos para pasta, uma caixa de entrada
na Central para o envio dos relatórios e outras notificações").

Os scripts do terminal não falam com o db do Artifact. Eles gravam aqui, numa fila local; a rotina da Central (sessão Claude
com a ferramenta ArtifactData) leva a fila ao painel certo e marca o que foi entregue.

  registro/caixa/pendentes.jsonl   uma mensagem por linha, com id estável (gravada por enviar())
  registro/caixa/entregues.jsonl   {id, painel, em} de cada mensagem já gravada no db (idempotente pelo id)
  registro/caixa/lote/<id>.json    o documento pronto para o ArtifactData batch (file_path de cada entrada)
  registro/caixa/lidas.json        o que cada pessoa marcou como lido (conferido pela conta, lib/portal_contas.py)

Documento no db (coleção `caixa`, doc_id = id):
  {para, assunto, resumo, origem, tipo, prioridade, anexos: [{nome, pasta_link}], acoes: [{rotulo, go}], criado_em, lido_por: {}, auditoria}
  para: luis | daniela | jenifer | geovana | time. As de luis vão só ao painel do Luis; as demais, só ao link do time (D100).
  tipo (filtro da tela): relatorio | alerta | pedido. resumo: texto puro (linhas e listas "- "), sem HTML e sem dado sensível.
  anexos: o nome do arquivo e o link da PASTA no OneDrive (caminhos.web), nunca o conteúdo; arquivo fora do OneDrive (dado do Mac)
  não entra. acoes.go: rota interna do portal (pedido/<id>, lote/<deal>, whatsapp, mesa, decisoes...), nunca link externo.
  Marcar como lida: a página grava em caixa_lidas/<id da conta> {pessoa, por_id, lidas: {<id>: {em}}} (subárvore {self} de cada
  pessoa; ninguém altera a mensagem em si). A rotina lê caixa_lidas, confere a conta e guarda em lidas.json.

Uso (rotina):
  python3 lib/caixa.py lote --painel luis|time [--max 50]   prepara até 50 documentos e imprime o `writes` do ArtifactData batch
  python3 lib/caixa.py entregue --painel luis|time <ids…>   marca como entregues (depois que o batch deu certo)
  python3 lib/caixa.py lidas <pasta baixada>                 registra as leituras (caixa_lidas baixada com out_dir)
  python3 lib/caixa.py status                               pendentes por painel, entregues, se a pasta antiga ainda recebe
  python3 lib/caixa.py enviar <para> "<assunto>" "<resumo>" [--origem X] [--prioridade alta]   mensagem avulsa (teste)
"""
import hashlib, html as _html, json, os, re, sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PESSOAS = ("luis", "daniela", "jenifer", "geovana")
DESTINOS = PESSOAS + ("time",)
EMAIL = {"luis.melo@savecompany.com.br": "luis", "daniela.maciel@savecompany.com.br": "daniela",
         "jenifer.carvalho@savecompany.com.br": "jenifer", "geovana.goncalves@savecompany.com.br": "geovana"}
PRIORIDADES = ("alta", "normal", "baixa")
TIPOS = ("relatorio", "alerta", "pedido")
LIMITE_RESUMO = 1500
ROTAS = re.compile(r"^(mesa|pedidos|whatsapp|areas|onde|rotinas|decisoes|caixa|novo)$|^(pedido|lote|decisao|chamado|demanda|wa|area|caixa)/[A-Za-z0-9_.:-]{1,80}$")
DIAS_TRANSICAO = 7  # depois de 1 semana com a caixa entregando, a pasta "Caixa de saída (e-mail pausado)" para de receber


def _ap():
    return os.environ.get("PARTNERS_AP") or os.path.expanduser("~/agentes-partners")


def _dir():
    d = os.path.join(_ap(), "registro", "caixa"); os.makedirs(d, exist_ok=True); return d


def _arq(nome):
    return os.path.join(_dir(), nome)


def _jsonl(nome):
    out = []
    try:
        for l in open(_arq(nome), encoding="utf-8"):
            l = l.strip()
            if not l: continue
            try: out.append(json.loads(l))
            except ValueError: pass  # linha quebrada (queda no meio da gravação) não derruba a fila
    except OSError: pass
    return out


def _anexar(nome, d):
    with open(_arq(nome), "a", encoding="utf-8") as f: f.write(json.dumps(d, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- texto
def texto_de_html(h):
    """HTML do e-mail → texto puro curto: parágrafos em linhas, itens de lista com "- ", sem tags nem estilos."""
    t = str(h or "")
    t = re.sub(r"(?is)<(head|style|script|title)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?i)<li[^>]*>", "\n- ", t)
    t = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|h\d|li|ul|ol|table)>", "\n", t)
    t = re.sub(r"(?s)<[^>]*>", " ", t)
    t = _html.unescape(t).replace("\xa0", " ")
    linhas = [re.sub(r"[ \t]+", " ", l).strip() for l in t.split("\n")]
    out = []
    for l in linhas:
        if not l or l == "-":
            if out and out[-1] != "": out.append("")
            continue
        out.append(l)
    return "\n".join(out).strip()


def _limpar(t, limite):
    import protecao
    t = protecao.limpo(t)
    t = re.sub(r"[<>]", "", t)  # nenhum resto de marcação chega ao painel
    if len(t) > limite: t = t[:limite - 1].rsplit(" ", 1)[0] + "…"
    return t


def _auditar(t):
    if os.environ.get("CAIXA_AUDITAR") == "0": return "nao_auditado"
    try:
        import protecao
        return "ok" if protecao.auditar(t) else "conferir"
    except Exception:
        return "conferir"


# ---------------------------------------------------------------- destinatário, origem, anexos
def pessoa_de(x):
    """luis|daniela|jenifer|geovana|time a partir da chave ou do e-mail; None se não for de ninguém do portal."""
    s = str(x or "").strip().lower()
    if s in DESTINOS: return s
    return EMAIL.get(s)


def origem_de(assunto):
    a = str(assunto or "").lower()
    for chave, o in (("falha", "alerta"), ("[agentes]", "central"), ("[painel]", "central"), ("plano do dia", "plano"), ("aviso da tarde", "plano"),
                     ("recuperador", "recuperador"), ("whatsapp", "whatsapp"), ("radar", "radar"), ("resultado", "resultados"), ("conselho", "conselho")):
        if chave in a: return o
    return "agentes"


def tipo_de(origem, prioridade):
    if origem in ("alerta", "sentinela") or prioridade == "alta": return "alerta"
    if origem in ("central", "pedido"): return "pedido"
    return "relatorio"


def _onedrive():
    import caminhos
    try: return os.path.realpath(caminhos.onedrive())
    except SystemExit: return None


def anexo_de(caminho, pessoa=None):
    """{nome, pasta_link}: link da pasta do OneDrive onde o arquivo está. Fora do OneDrive (dado que fica no Mac),
    procura uma cópia com o mesmo nome na pasta da pessoa (ex.: Plano do dia); se não houver, devolve None e o anexo não
    entra na caixa (arquivo que só existe no Mac, como print ou documento de parceiro, não vai ao painel nem pelo nome)."""
    import caminhos
    nome = os.path.basename(str(caminho or "")) or "arquivo"
    od = _onedrive()
    real = os.path.realpath(str(caminho or ""))
    if od and real.startswith(od + os.sep): return {"nome": nome, "pasta_link": caminhos.web(real)}
    if od and pessoa in PESSOAS:
        try:
            base = caminhos.pasta(pessoa)
            for d in [base] + [os.path.join(base, x) for x in sorted(os.listdir(base)) if os.path.isdir(os.path.join(base, x))]:
                if os.path.isfile(os.path.join(d, nome)): return {"nome": nome, "pasta_link": caminhos.web(d)}
        except (OSError, SystemExit): pass
    return None


def _anexos(xs, pessoa):
    out = []
    for a in xs or []:
        if isinstance(a, dict):
            link = str(a.get("pasta_link") or "")
            out.append({"nome": _limpar(os.path.basename(str(a.get("nome") or "arquivo")), 120),
                        "pasta_link": link if link.startswith("https://") else ""})
        elif a:
            x = anexo_de(a, pessoa)
            if x: out.append(x)
    return out[:10]


def _acoes(xs):
    return [{"rotulo": _limpar(a.get("rotulo") or "Abrir", 40), "go": a["go"]} for a in (xs or [])
            if isinstance(a, dict) and ROTAS.match(str(a.get("go") or ""))][:3]


# ---------------------------------------------------------------- fila
def _id(para, assunto, origem, resumo, criado):
    h = hashlib.sha1("|".join([para, assunto, origem, resumo[:400], criado[:16]]).encode()).hexdigest()[:12]
    return f"cx-{criado[:10].replace('-', '')}-{para[:3]}-{h}"


def enviar(para, assunto, resumo, origem=None, prioridade="normal", anexos=None, acoes=None, tipo=None, criado_em=None):
    """Grava uma mensagem por destinatário na fila. `para`: pessoa, e-mail ou lista. Devolve os ids gravados.
    Mensagem repetida (mesmo destinatário, assunto, origem, texto e minuto) não entra duas vezes."""
    ps = para if isinstance(para, (list, tuple, set)) else [para]
    alvo = []
    for x in ps:
        k = pessoa_de(x)
        if k and k not in alvo: alvo.append(k)
    if not alvo: return []
    criado = criado_em or datetime.now().astimezone().isoformat(timespec="seconds")
    prioridade = prioridade if prioridade in PRIORIDADES else "normal"
    assunto_l = _limpar(re.sub(r"\s+", " ", texto_de_html(assunto)), 160) or "(sem assunto)"
    resumo_l = _limpar(texto_de_html(resumo) if "<" in str(resumo or "") else str(resumo or "").strip(), LIMITE_RESUMO)
    origem = re.sub(r"[^a-z0-9_-]", "", str(origem or origem_de(assunto)).lower())[:30] or "agentes"
    tipo = tipo if tipo in TIPOS else tipo_de(origem, prioridade)
    auditoria = _auditar(assunto_l + "\n" + resumo_l)
    conhecidos = {m.get("id") for m in _jsonl("pendentes.jsonl")}
    ids = []
    for k in alvo:
        i = _id(k, assunto_l, origem, resumo_l, criado)
        ids.append(i)
        if i in conhecidos: continue
        _anexar("pendentes.jsonl", {"id": i, "para": k, "assunto": assunto_l, "resumo": resumo_l, "origem": origem, "tipo": tipo,
                                    "prioridade": prioridade, "anexos": _anexos(anexos, k), "acoes": _acoes(acoes),
                                    "criado_em": criado, "lido_por": {}, "auditoria": auditoria})
    return ids


def painel_de(para):
    return "luis" if para == "luis" else "time"


def entregues():
    return {e.get("id"): e for e in _jsonl("entregues.jsonl")}


def pendentes(painel):
    ja = entregues()
    return [m for m in _jsonl("pendentes.jsonl") if painel_de(m.get("para")) == painel and m.get("id") not in ja]


def documento(m):
    return {k: m.get(k) for k in ("para", "assunto", "resumo", "origem", "tipo", "prioridade", "anexos", "acoes", "criado_em", "lido_por", "auditoria")}


def lote(painel, maximo=50):
    """Prepara até `maximo` documentos (o batch aceita 50) e devolve as entradas `writes` do ArtifactData batch."""
    d = os.path.join(_dir(), "lote"); os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        if f.endswith(".json"): os.unlink(os.path.join(d, f))
    writes = []
    for m in pendentes(painel)[:maximo]:
        f = os.path.join(d, m["id"] + ".json"); json.dump(documento(m), open(f, "w", encoding="utf-8"), ensure_ascii=False)
        writes.append({"op": "set", "collection": "caixa", "doc_id": m["id"], "file_path": f})
    return writes


def marcar_entregues(ids, painel):
    ja, pend = entregues(), {m["id"]: m for m in _jsonl("pendentes.jsonl")}
    n = 0
    for i in ids:
        if i in ja or i not in pend or painel_de(pend[i]["para"]) != painel: continue
        _anexar("entregues.jsonl", {"id": i, "painel": painel, "em": datetime.now().astimezone().isoformat(timespec="seconds")}); n += 1
    return n


def registrar_lidas(pasta):
    """Lê caixa_lidas/<conta>.json (baixado com out_dir) e guarda as leituras de contas conhecidas em lidas.json.
    Conta fora da lista, ou que diz ser outra pessoa, vai para os alertas do Luis (A3) e não conta."""
    import portal_contas as PC
    f = _arq("lidas.json")
    try: L = json.load(open(f))
    except (OSError, ValueError): L = {}
    base = os.path.join(pasta, "caixa_lidas")
    n = 0
    for nome in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        if not nome.endswith(".json"): continue
        conta = nome[:-5]
        try: d = json.load(open(os.path.join(base, nome)))
        except (OSError, ValueError): continue
        ok, motivo = PC.conferir(d.get("pessoa"), d.get("por_id"))
        if ok and d.get("por_id") != conta: ok, motivo = False, "documento de leitura fora da conta de quem gravou"
        if not ok: PC.alertar("caixa_lidas", conta, motivo, d.get("pessoa"), d.get("por_id")); continue
        for i, v in (d.get("lidas") or {}).items():
            chave = f"{i}|{d['pessoa']}"
            if chave not in L: L[chave] = {"em": (v or {}).get("em"), "por_id": conta}; n += 1
    json.dump(L, open(f, "w"), ensure_ascii=False, indent=1)
    return n


def manter_pasta():
    """A pasta "Caixa de saída (e-mail pausado)" continua recebendo? CAIXA_PASTA=1/0 manda; sem a chave, recebe até
    completar 1 semana desde a primeira entrega da caixa a um painel (transição pedida no item 7). A pasta nunca é apagada."""
    v = os.environ.get("CAIXA_PASTA")
    if v in ("0", "1"): return v == "1"
    if os.path.exists(os.path.join(_ap(), ".caixa-sem-pasta")): return False
    es = sorted(e.get("em") or "" for e in entregues().values() if e.get("em"))
    if not es: return True
    try: primeira = datetime.fromisoformat(es[0])
    except ValueError: return True
    return datetime.now(primeira.tzinfo) - primeira < timedelta(days=DIAS_TRANSICAO)


def status():
    return {"pendentes": {p: len(pendentes(p)) for p in ("luis", "time")}, "entregues": len(entregues()), "pasta_antiga_recebe": manter_pasta()}


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(0)
    def opt(n, padrao=None):
        return a[a.index(n) + 1] if n in a and a.index(n) + 1 < len(a) else padrao
    if a[0] == "lote":
        print(json.dumps(lote(opt("--painel", "time"), int(opt("--max", 50))), ensure_ascii=False, indent=1))
    elif a[0] == "entregue":
        p = opt("--painel"); ids = [x for x in a[1:] if x.startswith("cx-")]
        if p not in ("luis", "time"): sys.exit("--painel luis|time")
        print(marcar_entregues(ids, p), "marcada(s) como entregue(s)")
    elif a[0] == "lidas" and len(a) > 1:
        print(registrar_lidas(a[1]), "leitura(s) nova(s)")
    elif a[0] == "status":
        print(json.dumps(status(), ensure_ascii=False))
    elif a[0] == "enviar" and len(a) >= 4:
        print(enviar(a[1], a[2], a[3], opt("--origem"), opt("--prioridade", "normal")))
    else: print(__doc__)
