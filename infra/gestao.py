#!/usr/bin/env python3
"""Sistema de gestão · consolida os dados de decisão do Luis (resultado, previsibilidade e controle) em um só JSON.

Contrato: infra/gestao-schema.md (seção 4 define a saída). Entradas, todas em ~/agentes-partners (fora do git):
  registro/gestao/pacote-<data>.json     resultado e controle (Controller com Dados)        → "meta", "semaforo", "confiabilidade", "alertas"
  registro/gestao/previsao-<data>.json   previsibilidade (Resultados, Pós-venda, Tributário) → "previsao"
  registro/gestao/controle-<data>.json   regras, desvios e ritual (Gabinete)                → "desvios", "regras", "ritual"
  conselho/decisoes.md                   decisões "pendente" da alçada do Luis              → "decisoes"
  registro/gestao/acoes.jsonl            ações combinadas (uma por linha; opcional)         → "acoes"
  logs/painel-luis/acoes/*.json e logs/painel/acoes/*.json   o que as donas marcaram no painel (só a dona ou o Luis, por conta)
  logs/painel-luis/conselho/meta-q4-unidade.json             unidade da meta escolhida pelo Luis no painel ("credito" ou "liquido")
Cada arquivo ausente vira bloco vazio com um aviso em "avisos"; nada derruba a consolidação.
Saída: registro/gestao/gestao.json (ou --saida <arquivo>; --json imprime na tela). infra/portal_dados.py copia para portal/dados.json em "gestao".
Uso: python3 infra/gestao.py [--saida arquivo] [--json]
"""
import glob, json, os, re, sys
from datetime import date

AP = os.environ.get("PARTNERS_AP") or os.path.expanduser("~/agentes-partners")
BLOCOS = ("resultado", "caixa", "canal", "risco", "operacao")
STATUS = ("verde", "amarelo", "vermelho", "cinza")
PESSOAS = ("luis", "daniela", "jenifer", "geovana")


def _ultimo(pasta, padrao):
    xs = sorted(glob.glob(os.path.join(pasta, padrao)))
    return xs[-1] if xs else None


def _ler(caminho, avisos, nome):
    """JSON do arquivo mais recente; sem arquivo ou quebrado, {} e um aviso."""
    if not caminho:
        avisos.append(f"{nome}: nenhum arquivo em registro/gestao/; bloco vazio."); return {}
    try:
        d = json.load(open(caminho, encoding="utf-8"))
        if not isinstance(d, dict): raise ValueError("não é um objeto")
        return d
    except (OSError, ValueError) as e:
        avisos.append(f"{nome}: não consegui ler {os.path.basename(caminho)} ({str(e)[:80]}); bloco vazio."); return {}


def _int(v, padrao=0):
    try: return int(round(float(v)))
    except (TypeError, ValueError): return padrao


def _num(v):
    try: return float(v)
    except (TypeError, ValueError): return None


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s or "").lower()).strip("-")[:60] or "x"


# ---------- decisões do Conselho ----------
def decisoes_pendentes(caminho=None):
    """Linhas "pendente" de conselho/decisoes.md que são alçada do Luis (D98): as delegadas ou aplicadas por padrão já não estão
    "pendente"; uma linha pendente cuja observação diga que foi delegada ("delegad", "Dono:") fica de fora. D7 sai quando há D7-b."""
    caminho = caminho or os.path.join(AP, "conselho", "decisoes.md")
    try: linhas = open(caminho, encoding="utf-8").read().splitlines()
    except OSError: return None
    out = []
    for l in linhas:
        c = [x.strip() for x in l.split("|")]
        if len(c) > 6 and re.match(r"D\d", c[1]) and c[5] == "pendente":
            obs = c[6]
            if re.search(r"delegad|^Dono:", obs, re.I) and "Fica com o Luis" not in obs: continue
            out.append({"id": c[1], "texto": c[4].replace("**", ""), "dono": "luis", "prazo": "", "status": "pendente", "data": c[2], "ata": c[3], "obs": obs})
    ids = {d["id"] for d in out}
    out = [d for d in out if not (d["id"] == "D7" and "D7-b" in ids)]
    vistos, uniq = set(), []
    for d in out:
        if d["id"] not in vistos: vistos.add(d["id"]); uniq.append(d)
    return uniq


# ---------- painel (gravações das pessoas, por conta) ----------
def _conferir(por, por_id, dono):
    """Autor do registro do painel: conta conhecida (infra/portal-contas.json) e a própria pessoa; dona da ação ou o Luis."""
    try:
        sys.path.insert(0, os.path.join(AP, "lib")); import portal_contas as PC
        ok, _ = PC.conferir(por, por_id)
    except Exception:
        return False
    return bool(ok) and (por == "luis" or (dono and por == dono))


def acoes_painel(desvios, avisos):
    """Aplica o status marcado no painel (acoes/<id> = {status, por, por_id, quando}) a cada desvio ou ação; só a dona ou o Luis."""
    docs = {}
    for pasta in ("logs/painel-luis/acoes", "logs/painel/acoes"):
        for f in sorted(glob.glob(os.path.join(AP, pasta, "*.json"))):
            try: d = json.load(open(f, encoding="utf-8"))
            except (OSError, ValueError): continue
            d = d["data"] if isinstance(d, dict) and isinstance(d.get("data"), dict) else d
            if isinstance(d, dict) and d.get("status") in ("aberto", "em_andamento", "resolvido"):
                i = os.path.basename(f)[:-5]
                if i not in docs or str(d.get("quando") or "") > str(docs[i].get("quando") or ""): docs[i] = d
    n = 0
    for x in desvios:
        d = docs.get(x.get("id"))
        if not d: continue
        if _conferir(d.get("por"), d.get("por_id"), x.get("dono")):
            x["status"] = d["status"]; x["marcado_por"] = d.get("por"); x["marcado_em"] = d.get("quando"); n += 1
        else:
            avisos.append(f"ação {x.get('id')}: marcação no painel descartada (conta ou dona não confere).")
    return n


def unidade_painel():
    """Unidade da meta escolhida pelo Luis no painel ("Definir unidade" grava conselho/meta-q4-unidade)."""
    f = os.path.join(AP, "logs", "painel-luis", "conselho", "meta-q4-unidade.json")
    try: d = json.load(open(f, encoding="utf-8"))
    except (OSError, ValueError): return None
    d = d["data"] if isinstance(d, dict) and isinstance(d.get("data"), dict) else d
    if not isinstance(d, dict) or not _conferir(d.get("por"), d.get("por_id"), "luis"): return None
    u = str(d.get("decisao") or "").lower()
    return "credito" if "cred" in u else "liquido" if "liq" in u else None


# ---------- montagem ----------
def _metrica(m):
    st = m.get("status") if m.get("status") in STATUS else "cinza"
    meta = _num(m.get("meta")); tol = m.get("tolerancia") if isinstance(m.get("tolerancia"), dict) else {}
    if _num(m.get("valor")) is None: st = "cinza"  # sem dado, cinza. Sem meta aprovada o Controller pode avaliar pela tolerância "proposta": o status vem dele e a meta fica null
    # tolerância: textos para mostrar; "_verde"/"_amarelo" são os limites numéricos calculados; "origem" diz se é proposta
    return {"id": str(m.get("id") or _slug(m.get("nome"))), "nome": str(m.get("nome") or m.get("id") or "—"),
            "bloco": m.get("bloco") if m.get("bloco") in BLOCOS else "operacao", "valor": _num(m.get("valor")), "unidade": str(m.get("unidade") or "n"),
            "anterior": _num(m.get("anterior")), "variacao_pct": _num(m.get("variacao_pct")), "meta": meta, "meta_unidade": str(m.get("meta_unidade") or ""),
            "meta_proposta": bool(m.get("meta_proposta")) or meta is None or str(tol.get("origem") or "") == "proposta",
            "limite_proposto": _num(tol.get("_verde")), "tolerancia": {k: str(v) for k, v in tol.items() if not k.startswith("_") and k != "origem" and v}, "status": st,
            "fonte": str(m.get("fonte") or ""), "confianca": m.get("confianca") if m.get("confianca") in ("alta", "media", "baixa") else "baixa", "nota": str(m.get("nota") or "")}


def _meta(p, unidade_luis):
    m = p.get("meta") if isinstance(p.get("meta"), dict) else {}
    u = m.get("unidade")  # D111: "credito_contrato_fechado" vale sobre a escolha antiga do painel
    u = "credito" if str(u).startswith("credito") else (unidade_luis or u)
    return {"q4_rs": _int(m.get("q4_rs")), "unidade": u if u in ("credito", "liquido") else "indefinida", "unidade_detalhe": str(m.get("unidade") or ""), "decisao": str(m.get("decisao") or ""),
            "mes_atual": m.get("mes_atual") if isinstance(m.get("mes_atual"), dict) else {}, "meses": [x for x in m.get("meses", []) if isinstance(x, dict)],
            "total": m.get("total") if isinstance(m.get("total"), dict) else {}, "por_master": m.get("por_master") if isinstance(m.get("por_master"), dict) else {},
            "realizado_rs": _int(m.get("realizado_rs")),
            "falta_rs": _int(m.get("falta_rs")), "dias_uteis_restantes": _int(m.get("dias_uteis_restantes")), "ritmo_necessario_rs_dia": _int(m.get("ritmo_necessario_rs_dia")),
            "ritmo_atual_rs_dia": _int(m.get("ritmo_atual_rs_dia")), "leituras": m.get("leituras") if isinstance(m.get("leituras"), dict) else {},
            "unidade_definida_no_painel": bool(unidade_luis) and not str(m.get("unidade") or "").startswith("credito"), "periodo": p.get("periodo") if isinstance(p.get("periodo"), dict) else {}}


def _desvios(c):
    regras = {r.get("id"): r for r in c.get("regras", []) if isinstance(r, dict)}
    out = []
    for d in c.get("desvios", []):
        if not isinstance(d, dict): continue
        r = regras.get(d.get("regra"), {})
        out.append({"id": _slug(f"{d.get('regra')}-{d.get('metrica')}-{d.get('desde')}"), "regra": str(d.get("regra") or ""), "condicao": str(r.get("condicao") or ""),
                    "metrica": str(d.get("metrica") or r.get("metrica") or ""), "valor": _num(d.get("valor")), "limite": _num(d.get("limite")), "desde": str(d.get("desde") or ""),
                    "acao": str(d.get("acao") or r.get("acao") or ""), "dono": str(d.get("dono") or r.get("dono") or ""), "prazo": str(d.get("prazo") or ""),
                    "alcada": str(r.get("alcada") or d.get("alcada") or ""), "status": d.get("status") if d.get("status") in ("aberto", "em_andamento", "resolvido") else "aberto", "origem": "controle",
                    "texto": str(d.get("texto") or ""), "vencido": bool(d.get("vencido")), "escalado_para": str(d.get("escalado_para") or ""), "bloco": str(d.get("bloco") or "")})
    return out


def _acoes(caminho, avisos):
    out = []
    if not os.path.exists(caminho): return out
    try:
        for n, l in enumerate(open(caminho, encoding="utf-8"), 1):
            l = l.strip()
            if not l: continue
            try: a = json.loads(l)
            except ValueError: avisos.append(f"acoes.jsonl: linha {n} inválida, ignorada."); continue
            if not isinstance(a, dict) or not a.get("acao"): continue
            out.append({"id": str(a.get("id") or _slug(f"{a.get('origem') or 'acao'}-{a.get('acao')}-{a.get('prazo')}")), "acao": str(a["acao"]), "dono": str(a.get("dono") or ""),
                        "prazo": str(a.get("prazo") or ""), "origem": a.get("origem") if a.get("origem") in ("conselho", "controle") else "conselho",
                        "status": a.get("status") if a.get("status") in ("aberto", "em_andamento", "resolvido") else "aberto", "metrica": str(a.get("metrica") or "")})
    except OSError as e:
        avisos.append(f"acoes.jsonl: não consegui ler ({str(e)[:60]}).")
    return out


def montar(pacote, previsao, controle, decisoes, acoes, avisos=None, unidade_luis=None, hoje=None):
    """Monta o gestao.json (seção 4 do contrato) a partir dos dicionários já lidos. Puro: não lê disco."""
    avisos = list(avisos or [])
    p, v, c = pacote or {}, previsao or {}, controle or {}
    if decisoes is None: avisos.append("conselho/decisoes.md: não encontrado; sem decisões."); decisoes = []
    sem = [m for m in p.get("metricas", []) if isinstance(m, dict)]
    pv = {"data": v.get("data"), "horizonte_semanas": _int(v.get("horizonte_semanas"), 13),
          "cenarios": {k: x for k, x in (v.get("cenarios") or {}).items() if isinstance(x, dict)},
          "caixa_13_semanas": [x for x in v.get("caixa_13_semanas", []) if isinstance(x, dict)], "pipeline_por_safra": [x for x in v.get("pipeline_por_safra", []) if isinstance(x, dict)],
          "decadencia_mensal": [x for x in v.get("decadencia_mensal", []) if isinstance(x, dict)], "janelas": [x for x in v.get("janelas", []) if isinstance(x, dict)],
          "riscos": [x for x in v.get("riscos", []) if isinstance(x, dict)], "por_mes": v.get("por_mes") if isinstance(v.get("por_mes"), dict) else {}}
    return {"data": p.get("data") or v.get("data") or c.get("data") or (hoje or date.today().isoformat()), "gerado_em": hoje or date.today().isoformat(),
            "fontes": {"pacote": p.get("data"), "previsao": v.get("data"), "controle": c.get("data")},
            "meta": _meta(p, unidade_luis), "semaforo": [_metrica(m) for m in sem],
            "confiabilidade": p.get("confiabilidade") if isinstance(p.get("confiabilidade"), dict) else {},
            "alertas": [a for a in p.get("alertas", []) if isinstance(a, dict)],
            "previsao": pv, "desvios": _desvios(c), "regras": [r for r in c.get("regras", []) if isinstance(r, dict)], "ritual": [r for r in c.get("ritual", []) if isinstance(r, dict)],
            "decisoes": [{"id": d["id"], "texto": d["texto"], "dono": "luis", "prazo": d.get("prazo") or "", "status": "pendente", "data": d.get("data") or "", "ata": d.get("ata") or "", "obs": d.get("obs") or ""} for d in decisoes],
            "acoes": acoes or [], "avisos": avisos}


def consolidar(ap=None):
    """Lê os arquivos (tolerante a ausência) e devolve o consolidado."""
    ap = ap or AP; pasta = os.path.join(ap, "registro", "gestao"); avisos = []
    p = _ler(_ultimo(pasta, "pacote-*.json"), avisos, "pacote")
    v = _ler(_ultimo(pasta, "previsao-*.json"), avisos, "previsão")
    c = _ler(_ultimo(pasta, "controle-*.json"), avisos, "controle")
    dec = decisoes_pendentes(os.path.join(ap, "conselho", "decisoes.md"))
    ac = _acoes(os.path.join(pasta, "acoes.jsonl"), avisos)
    g = montar(p, v, c, dec, ac, avisos, unidade_luis=unidade_painel() if ap == AP else None)
    if ap == AP: acoes_painel(g["desvios"] + g["acoes"], g["avisos"])
    return g


def main():
    args = sys.argv[1:]
    saida = args[args.index("--saida") + 1] if "--saida" in args else os.path.join(AP, "registro", "gestao", "gestao.json")
    g = consolidar()
    if "--json" in args: print(json.dumps(g, ensure_ascii=False, indent=1)); return
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    json.dump(g, open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{saida}: {len(g['semaforo'])} métricas, {len(g['desvios'])} desvios, {len(g['decisoes'])} decisões, {len(g['acoes'])} ações"
          + (f" · avisos: {' '.join(g['avisos'])}" if g["avisos"] else ""))


if __name__ == "__main__":
    main()
