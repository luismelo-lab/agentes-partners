#!/usr/bin/env python3
"""Mapa de aderência da conta: o que mais cada cliente pode consumir da Save, em que ordem e com que evidência.

Somente leitura e local. Cruza o download do HubSpot do dia (todos os funis, pela raiz do CNPJ), os pareceres
lidos (celulas/geovana/pareceres/resumos.json) e a base local da Receita (cnpj.sqlite, read-only).
Nenhum CNPJ sai da máquina; não lê .env; não grava no HubSpot.

As regras estão na tabela PRODUTOS, uma linha por produto, explícitas para o time revisar. O playbook do setor
(references/playbooks-setoriais.md) explica o porquê; o script só aponta o sinal que existe nos dados.

Uso:
  python3 mapa_conta.py --negocio <id>            mapa de um cliente (JSON na tela)
  python3 mapa_conta.py --cnpj <cnpj>
  python3 mapa_conta.py --carteira [--master X]   todos os clientes ganhos → JSON agregado + Excel por Master
"""
import argparse, collections, glob, json, os, re, sqlite3, sys
from datetime import date

AP = os.path.expanduser("~/agentes-partners")
OUT = os.path.join(AP, "departamentos", "solucoes")
HOJE = date.today()

# ── setores (cluster pelo CNAE de 4 dígitos) ─────────────────────────────────────────────────────────────
SETORES = [
    ("Proteína animal", ("1011", "1012", "1013", "4634", "4722")),
    ("Café e grãos", ("4621", "4622", "4623", "1061", "1081")),
    ("Varejo alimentar", ("4711", "4712", "4721", "4724", "4729", "4633", "4637", "4639", "4691")),
    ("Combustíveis e GLP", ("4731", "4732", "4681", "4682", "4784")),
    ("Confecção e têxtil", ("1311", "1321", "1330", "1340", "1351", "1352", "1353", "1354", "1359", "1411", "1412", "1413", "1414", "1421", "1422", "1531", "1532", "1533", "1539", "1540")),
    ("Transporte de carga", ("4930", "5211", "5212", "5250")),
    ("Panificação e alimentos", ("1091", "1092", "1093", "1094", "1095", "1096", "1099", "1052", "1053")),
]
INDUSTRIA = lambda c: c[:2].isdigit() and 10 <= int(c[:2]) <= 33
ATACADO = lambda c: c[:2] == "46"
VAREJO = lambda c: c[:2] == "47"


def setor(cnae):
    c = (cnae or "")[:4]
    for nome, cs in SETORES:
        if c in cs: return nome
    if INDUSTRIA(c): return "Indústria (outros)"
    if ATACADO(c): return "Atacado (outros)"
    if VAREJO(c): return "Varejo (outros)"
    return "Outros"


# faturamento anual: faixa do HubSpot (limite inferior) ou valor informado; None = desconhecido
FAIXA = {"R$81K - R$360K": 81e3, "R$360K - R$1M": 360e3, "R$1M - R$4.8M": 1e6, "R$4.8M - R$10M": 4.8e6, "R$10M - R$30M": 10e6,
         "R$30M - R$100M": 30e6, "R$100M - R$300M": 100e6, "R$300M+": 300e6}


def fat(ex):
    try:
        v = float(ex.get("faturamento") or 0)
        if v > 0: return v
    except Exception: pass
    return FAIXA.get(str(ex.get("faixa_faturamento") or ""))


SEM_DEB = re.compile(r"n[ãa]o (possui|consta|tem)|sem d[ée]bitos|n[ãa]o foi necess", re.I)
COM_DEB = re.compile(r"possui d[ée]bitos|d[ée]bitos? (em aberto|com exigibilidade|inscrit)|parcelamento|PGFN|d[íi]vida ativa|transa[çc][ãa]o", re.I)

# ── produtos: (id, nome, onda da esteira, status, área/skill, regra(s) → (aderência, motivo) ou None) ─────────
# onda: 1 Oxigenar (caixa rápido, risco baixo) · 2 Estruturar (passivo, carga, governança) · 3 Expandir (funding, novos mercados)
# status: pronto · em validação (trava do G2: sem taxa/prazo/fee) · em estruturação · em definição


def r_recorrencia(s):
    n = s["competencias_novas"]
    if s["rt_ganho"] and n and n >= 12: return ("alta", f"{n} competências novas desde a última análise")
    if s["rt_ganho"] and n and n >= 6: return ("média", f"{n} competências novas; reavaliar quando chegar a 12")


def r_aliquota_zero(s):
    if s["setor"] in ("Varejo alimentar",) and s["cnae"][:4] in ("4711", "4712"): return None  # catálogo: fora supermercado
    if s["cnae"][:4] == "4621": return None  # catálogo: fora café
    if s["setor"] in ("Proteína animal", "Varejo alimentar", "Café e grãos") or ATACADO(s["cnae"]):
        if not s["teses"]: return ("média", "perfil do catálogo (revenda com alíquota zero); parecer não lido: confirmar se a tese já foi feita")
        if "Teses de aquisições" not in s["teses"]: return ("alta", "perfil do catálogo (revenda com alíquota zero) e tese de aquisições não aparece nos pareceres. Risco: EREsp 2.215.482 pendente na 1ª Seção do STJ e LC 224/2025 (radar tributário, 16/10)")
        if s["teses"]["Teses de aquisições"] in ("não analisada", "None", ""): return ("média", "tese de aquisições sem desfecho no parecer")


def r_previdenciaria(s):
    if not s["teses"]: return None
    if "Teses previdenciárias" not in s["teses"] and s["regime"] in ("Lucro Real", "Lucro Presumido"):
        return ("média", "CPP sobre verbas indenizatórias e Sistema S não aparecem nos pareceres (confirmar folha)")


def r_agro_pf(s):
    if s["cnae"][:4] in ("1011", "1012", "1013", "1052", "1061", "1081"):
        return ("alta", "agroindústria que compra de produtor PF: crédito presumido sobre aquisições de PF e Funrural (catálogo)")


def r_icms_st(s):
    if s["setor"] in ("Combustíveis e GLP",) or s["cnae"][:4] in ("4635", "4723", "4644", "4771", "4530"):
        return ("média", "revenda com ICMS-ST: exclusão do ICMS-ST da base (Tema 1.125 STJ); combustível é monofásico, conferir")


def r_passivo(s):
    if s["passivo_debitos"]: return ("alta", "o parecer aponta débitos (Receita/PGFN): transação, parcelamento ou compensação com o próprio crédito")


def r_juridico(s):
    if s["passivo_suspenso"]: return ("média", "débito com exigibilidade suspensa: acompanhar a defesa e os prazos (Produtos Jurídicos)")
    if s["acao_judicial"]:
        return ("baixa", "ação judicial em alguma tese: conferir se há acompanhamento contratado")


def r_planejamento(s):
    f = s["faturamento"] or 0
    if s["regime"] in ("Lucro Real", "Lucro Presumido") and f >= 4.8e6:
        a = "alta" if (f >= 30e6 or s["setor"] in ("Proteína animal", "Varejo alimentar", "Panificação e alimentos")) else "média"
        return (a, "Real/Presumido com faturamento ≥ R$ 4,8 mi: regime, reforma (CBS/IBS desde 2027; cesta básica no alimento) e créditos antigos antes da transição")


def r_gestao_contas(s):
    f = s["faturamento"] or 0
    b2b = ATACADO(s["cnae"]) or INDUSTRIA(s["cnae"]) or s["setor"] == "Transporte de carga"
    if b2b and f >= 4.8e6: return ("alta" if f >= 10e6 else "média", "vende a prazo para empresas (B2B): cobrança com IA paga no êxito e porta para DRE e balanço")
    if VAREJO(s["cnae"]) and f >= 4.8e6: return ("baixa", "varejo recebe à vista ou no cartão: só se houver venda a prazo relevante")


def r_antecipacao(s):
    f = s["faturamento"] or 0
    if (ATACADO(s["cnae"]) or INDUSTRIA(s["cnae"])) and f >= 4.8e6: return ("média", "carteira a receber B2B: antecipação por instituição autorizada (a Save não antecipa)")


def r_fidc(s):
    f = s["faturamento"] or 0
    if f >= 120e6 and (ATACADO(s["cnae"]) or INDUSTRIA(s["cnae"])): return ("média", "faturamento ≥ ~R$ 10 mi por mês com recebíveis B2B (critério de 13/10)")


def r_ci(s):
    f = s["faturamento"] or 0
    if f >= 50e6 and (s["setor"] in ("Proteína animal", "Café e grãos") or INDUSTRIA(s["cnae"]) or ATACADO(s["cnae"])):
        return ("média", "faturamento ≥ R$ 50 mi/ano em setor do apetite; falta confirmar garantia livre (~2x) e necessidade ≥ US$ 5 mi")
    if f >= 30e6 and s["setor"] in ("Proteína animal", "Café e grãos"): return ("baixa", "agro entre R$ 30 e 50 mi: só com ativos > R$ 60 mi (a confirmar com o dono)")


def r_maquila(s):
    if s["setor"] == "Confecção e têxtil" or s["cnae"][:2] in ("22", "15"):
        return ("média" if s["regime"] == "Lucro Real" else "baixa", "indústria intensiva em mão de obra (corte do MQ)")
    if s["cnae"][:4] in ("1011", "1012", "1013"): return ("bloqueado", "frigoríficos bloqueados no piloto do MQ (D59, pergunta MQ-Q6)")


def r_patrimonial(s):
    f = s["faturamento"] or 0; cap = s["capital"] or 0
    if f >= 20e6 or cap >= 5e6: return ("média", "porte e patrimônio indicam estruturação patrimonial e sucessória")


PRODUTOS = [
    ("RT-REC", "Recuperação tributária · recorrência (novas competências)", 1, "pronto", "recuperador", r_recorrencia),
    ("RT-AZ", "Recuperação tributária · alíquota zero na revenda (via PER)", 1, "pronto", "depto-tributario + revisor-diagnostico", r_aliquota_zero),
    ("RT-AGRO", "Recuperação tributária · crédito presumido de compras de PF e Funrural", 1, "pronto", "depto-tributario", r_agro_pf),
    ("RT-PREV", "Recuperação tributária · previdenciárias (CPP e Sistema S)", 1, "pronto", "depto-tributario", r_previdenciaria),
    ("RT-ST", "Recuperação tributária · exclusão do ICMS-ST", 1, "pronto", "depto-tributario", r_icms_st),
    ("GC", "Gestão de Contas (cobrança com IA, paga no êxito)", 1, "em definição", "depto-internacional (ecossistema)", r_gestao_contas),
    ("PAS", "Gestão de Passivo (transação, parcelamento, compensação)", 2, "pronto", "depto-juridico + depto-tributario", r_passivo),
    ("JUR", "Produtos Jurídicos (defesa e acompanhamento)", 2, "pronto", "depto-juridico", r_juridico),
    ("PLAN", "Planejamento tributário e reforma (CBS/IBS)", 2, "pronto", "depto-tributario", r_planejamento),
    ("EP", "Estruturação patrimonial", 2, "em definição", "depto-juridico", r_patrimonial),
    ("ANT", "Antecipação de recebíveis (instituição autorizada)", 2, "em definição", "depto-internacional (ecossistema)", r_antecipacao),
    ("FIDC", "FIDC", 3, "em definição", "depto-internacional (ecossistema)", r_fidc),
    ("CI", "Crédito Internacional (funding)", 3, "em validação", "depto-internacional", r_ci),
    ("MQ", "Maquila no Paraguai", 3, "em estruturação", "depto-internacional", r_maquila),
]
ONDA = {1: "1 · Oxigenar", 2: "2 · Estruturar", 3: "3 · Expandir"}
PESO = {"alta": 3, "média": 2, "baixa": 1, "bloqueado": 0}
FUNIL_PRODUTO = {"Gestão de Passivo": "PAS", "Produtos Jurídicos": "JUR", "Planejamento Tributário": "PLAN"}


def carregar():
    f = sorted(glob.glob(os.path.join(AP, "departamentos/resultados/dados/hubspot-*.json")))[-1]
    neg = json.load(open(f))["negocios"]
    try: res = json.load(open(os.path.join(AP, "celulas/geovana/pareceres/resumos.json")))
    except Exception: res = {}
    db = sqlite3.connect("file:" + os.path.join(AP, "dados-publicos/receita/cnpj.sqlite") + "?mode=ro", uri=True)
    return os.path.basename(f), neg, res, db


def cnpj_de(n): return re.sub(r"\D", "", str((n.get("extras") or {}).get("cnpj") or "")).zfill(14) if (n.get("extras") or {}).get("cnpj") else ""


def sinais(cnpj, negs, res, db):
    """Junta tudo o que a Save sabe da empresa (todos os negócios da mesma raiz de CNPJ)."""
    raiz = cnpj[:8]
    r = db.execute("select cnae, cnaes_sec, situacao, uf, inicio from estab where cnpj=?", (cnpj,)).fetchone() or ("", "", "", "", "")
    e = db.execute("select capital, porte from empresa where basico=?", (raiz,)).fetchone() or (None, None)
    ganhos = [n for n in negs if n["status"] == "ganho" and n["pipeline"].startswith("RT")]
    ex = next((n.get("extras") or {} for n in sorted(negs, key=lambda n: n.get("criado") or "", reverse=True)), {})
    teses, passivo, acao, comp = {}, "", False, None
    for n in sorted(negs, key=lambda n: n.get("criado") or ""):
        p = res.get(str(n["id"])) or {}
        t = p.get("teses")
        if isinstance(t, dict):
            for k, v in t.items(): teses[k] = (v or {}).get("desfecho") if isinstance(v, dict) else str(v)
        if p.get("passivo"): passivo = str(p["passivo"])
        if "há ação judicial" in str(p.get("acoes_judiciais") or ""): acao = True
        if p.get("competencias_novas_desde_analise") not in (None, "None"):
            try: comp = int(p["competencias_novas_desde_analise"])
            except Exception: pass
    ja = {FUNIL_PRODUTO[n["pipeline"]]: n["status"] for n in negs if n["pipeline"] in FUNIL_PRODUTO}
    return {"cnpj": cnpj, "nome": negs[0]["nome"], "cnae": r[0] or "", "setor": setor(r[0]), "uf": r[3] or ex.get("uf"), "situacao": r[2],
            "regime": ex.get("regime"), "faturamento": fat(ex), "faixa": ex.get("faixa_faturamento"), "capital": e[0], "porte_receita": e[1],
            "master": next((n.get("parceiro") for n in ganhos or negs if n.get("parceiro")), None),
            "rt_ganho": bool(ganhos), "rt_ganhos": len(ganhos), "rt_valor": sum(float(n.get("valor") or 0) for n in ganhos),
            "rt_recebido": sum(float(n.get("recebido") or 0) for n in ganhos if str(n.get("recebido")) not in ("None", "")),
            "ultimo_ganho": max((n.get("fechado") or "" for n in ganhos), default=None),
            "teses": teses, "passivo_debitos": bool(passivo and COM_DEB.search(passivo) and not SEM_DEB.search(passivo)),
            "passivo_suspenso": "exigibilidade suspensa" in passivo.lower(), "acao_judicial": acao, "competencias_novas": comp,
            "ja_tem": ja, "negocios": [str(n["id"]) for n in negs]}


def mapa(s):
    ops = []
    for pid, nome, onda, status, area, regra in PRODUTOS:
        if pid in s["ja_tem"]:
            ops.append({"id": pid, "produto": nome, "aderencia": "já contratado" if s["ja_tem"][pid] == "ganho" else "em andamento",
                        "motivo": f"negócio no funil ({s['ja_tem'][pid]})", "onda": ONDA[onda], "status": status, "area": area}); continue
        try: x = regra(s)
        except Exception: x = None
        if x: ops.append({"id": pid, "produto": nome, "aderencia": x[0], "motivo": x[1], "onda": ONDA[onda], "status": status, "area": area})
    ops.sort(key=lambda o: (o["onda"], -PESO.get(o["aderencia"], -1)))
    falta = [k for k, v in (("faturamento real (só há faixa)", s["faturamento"] in (None, 3.6e6, 4.8e6)), ("parecer lido", not s["teses"]),
                            ("regime", not s["regime"]), ("CNAE na Receita", not s["cnae"])) if v]
    pontos = sum(PESO.get(o["aderencia"], 0) for o in ops if o["aderencia"] in PESO)
    return {**{k: s[k] for k in ("nome", "cnpj", "setor", "cnae", "uf", "regime", "faixa", "master", "rt_ganhos", "rt_valor", "rt_recebido", "ultimo_ganho")},
            "oportunidades": ops, "indice_aderencia": pontos, "falta": falta, "negocios": s["negocios"]}


def por_cnpj(neg):
    g = collections.defaultdict(list)
    for n in neg:
        c = cnpj_de(n)
        if c: g[c].append(n)
    return g


def excel(linhas, destino):
    sys.path.insert(0, os.path.join(AP, "lib"))
    import openpyxl, marca  # noqa
    from openpyxl.styles import Font, PatternFill, Alignment
    M = marca.MARCA if hasattr(marca, "MARCA") else json.load(open(os.path.join(AP, "departamentos/marketing-marca/padrao/marca.json")))
    fonte, ouro = M["fontes"]["sans"], M["claro"]["ouro"].lstrip("#")
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Carteira"
    cab = ["Master", "Cliente", "Setor", "UF", "Regime", "Faixa de faturamento", "Índice de aderência", "Onda 1 · Oxigenar", "Onda 2 · Estruturar", "Onda 3 · Expandir", "Falta", "Link"]
    ws.append(cab)
    for c in ws[1]: c.font = Font(name=fonte, bold=True, color="000000"); c.fill = PatternFill("solid", fgColor=ouro); c.alignment = Alignment(wrap_text=True, vertical="center")
    for m in linhas:
        onda = lambda o: "; ".join(f"{x['produto'].split(' · ')[-1]} ({x['aderencia']})" for x in m["oportunidades"] if x["onda"].startswith(o) and x["aderencia"] in ("alta", "média"))
        ws.append([m["master"] or "Fora do roster", m["nome"], m["setor"], m["uf"], m["regime"], m["faixa"], m["indice_aderencia"], onda("1"), onda("2"), onda("3"),
                   ", ".join(m["falta"]) or "nada", f"https://app.hubspot.com/contacts/47865021/deal/{m['negocios'][-1]}"])
    for r in ws.iter_rows(min_row=2):
        for c in r: c.font = Font(name=fonte, size=10); c.alignment = Alignment(wrap_text=True, vertical="top")
    for col, w in zip("ABCDEFGHIJKL", (16, 34, 18, 5, 14, 14, 10, 42, 42, 34, 26, 16)): ws.column_dimensions[col].width = w
    ws.freeze_panes = "C2"; ws.auto_filter.ref = ws.dimensions
    l = wb.create_sheet("Como ler")
    for t in ["Mapa de aderência da carteira (Desenvolvimento de Contas e Soluções). Uso interno.",
              "Onda 1 Oxigenar: caixa rápido e risco baixo. Onda 2 Estruturar: passivo, carga e governança. Onda 3 Expandir: funding e novos mercados.",
              "Aderência alta ou média aparece aqui; o motivo de cada uma está no mapa individual (mapa_conta.py --negocio <id>).",
              "Produtos em validação, estruturação ou definição (Crédito Internacional, Maquila, Gestão de Contas, antecipação, FIDC): só descoberta, sem taxa, prazo ou fee.",
              "Índice de aderência: alta = 3, média = 2, baixa = 1. Serve para priorizar a conversa com o Master, não é valor em R$."]:
        l.append([t]); l.cell(l.max_row, 1).font = Font(name=fonte, size=11)
    l.column_dimensions["A"].width = 120
    wb.save(destino)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--negocio"); ap.add_argument("--cnpj"); ap.add_argument("--carteira", action="store_true"); ap.add_argument("--master")
    ap.add_argument("--excel", help="caminho do Excel da carteira (padrão: departamentos/solucoes/carteira-<data>.xlsx)")
    a = ap.parse_args()
    base, neg, res, db = carregar(); G = por_cnpj(neg)
    if a.negocio or a.cnpj:
        c = re.sub(r"\D", "", a.cnpj).zfill(14) if a.cnpj else next((cnpj_de(n) for n in neg if str(n["id"]) == a.negocio), "")
        if not c or c not in G: sys.exit("Negócio ou CNPJ sem CNPJ no HubSpot.")
        raiz = [n for k, v in G.items() if k[:8] == c[:8] for n in v]
        print(json.dumps(mapa(sinais(c, raiz, res, db)), ensure_ascii=False, indent=1, default=str)); sys.exit()
    clientes = {c: v for c, v in G.items() if any(n["status"] == "ganho" and n["pipeline"].startswith("RT") for n in v)}
    M = [mapa(sinais(c, v, res, db)) for c, v in clientes.items()]
    if a.master: M = [m for m in M if (m["master"] or "").lower() == a.master.lower()]
    M.sort(key=lambda m: (m["master"] or "~", -m["indice_aderencia"]))
    os.makedirs(OUT, exist_ok=True)
    cont = collections.Counter(o["id"] for m in M for o in m["oportunidades"] if o["aderencia"] in ("alta", "média"))
    agg = {"gerado": HOJE.isoformat(), "fonte": base, "clientes": len(M), "por_produto": dict(cont),
           "por_setor": dict(collections.Counter(m["setor"] for m in M)), "mapas": M}
    json.dump(agg, open(os.path.join(OUT, f"carteira-{HOJE}.json"), "w"), ensure_ascii=False, indent=1, default=str)
    x = a.excel or os.path.join(OUT, f"carteira-{HOJE}.xlsx"); excel(M, x)
    print(f"{len(M)} clientes · oportunidades (alta/média) por produto: {dict(cont.most_common())}\n{x}")
