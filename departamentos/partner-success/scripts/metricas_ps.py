#!/usr/bin/env python3
"""Partner Success & Enablement — métricas de ativação do canal (cálculo determinístico).

Lê o download mais recente do HubSpot (gerado por depto-resultados/scripts/hubspot_fonte.py)
e calcula, por parceiro:
  1. tempo até o 1º negócio ganho (a partir do 1º negócio registrado ou da data de entrada informada);
  2. parceiros ativos (definição explícita abaixo, a mesma do depto-resultados);
  3. atividade por trimestre (criados, ganhos, perdidos, valor ganho, conversão).
Também simula a proposta de níveis (tiers) para os Masters, lendo o scorecard do depto-dados
(não recalcula o índice de saúde).

Não chama a API. Não altera o HubSpot. Saída:
  ~/agentes-partners/departamentos/partner-success/metricas/Metricas-PS-AAAA-MM-DD.xlsx (+ .json)

Uso: python3 metricas_ps.py [--fonte arquivo.json] [--hoje AAAA-MM-DD]

DEFINIÇÕES (dicionário — manter igual ao depto-resultados/references/metricas.md)
- Data efetiva do negócio = menor entre 'criado' e 'fechado'. Motivo: as importações em massa
  (nov/2025 e fev/2026) regravaram a data de criação; 1.396 negócios têm fechamento anterior à criação.
- Parceiro = nome do roster (9 Masters, mapeamento-hubspot.json). Fora do roster, o nome bruto
  normalizado (aliases em aliases-parceiros.json). Sem nome ou nome numérico = "(sem parceiro informado)".
- ATIVO = ≥ 1 negócio com data efetiva nos últimos 90 dias (mesma regra do relatório semanal).
- PRODUTIVO = ≥ 1 negócio ganho com fechamento nos últimos 365 dias.
- Classe: Ativo e produtivo · Ativo em rampa (ativo, sem ganho em 12m) · Dormente (sem negócio
  em 90d, com ganho em 12m) · Inativo (nem um nem outro).
- Tempo até o 1º negócio = dias entre o início (data de entrada informada em datas-entrada-parceiros.json;
  se vazia, o 1º negócio registrado) e o fechamento do 1º negócio ganho.
  "Anterior à base" = 1º registro nos primeiros 90 dias da base: o número não mede onboarding.
  "Data estimada" = o 1º registro vem de negócio importado com data regravada.
"""
import argparse, glob, json, os, re, statistics, unicodedata
from collections import Counter, defaultdict
from datetime import date, timedelta

HOME = os.path.expanduser("~/agentes-partners/departamentos")
SRC = os.path.join(HOME, "resultados/dados")
MAP = os.path.join(HOME, "resultados/mapeamento-hubspot.json")
PS = os.path.join(HOME, "partner-success")
ALIASES = os.path.join(PS, "scripts/aliases-parceiros.json")
ENTRADAS = os.path.join(PS, "scripts/datas-entrada-parceiros.json")
DADOS_BI = os.path.join(HOME, "dados")
SEM = "(sem parceiro informado)"

# ---- Proposta de níveis v1 (rascunho para o Luis aprovar; calibrado com os dados de 29/09/2026) ----
NIVEIS_MASTER = [  # avaliados em ordem; o primeiro que o parceiro cumpre é o nível
    ("Master Estratégico", {"ganhos_12m": 30, "conversao_12m_pct": 20, "honorario_preenchido_pct": 85, "ativo": True}),
    ("Master", {"ganhos_12m": 10, "conversao_12m_pct": 15, "honorario_preenchido_pct": 75, "ativo": True}),
    ("Master em desenvolvimento", {"ativo": True}),
    ("Master em observação", {}),
]
NIVEIS_INDICADOR = [
    ("Indicador Pleno (candidato a Master)", {"ganhos_12m": 5, "ativo": True}),
    ("Indicador Certificado", {"ganhos_12m": 1, "ativo": True}),  # + certificação da Academia (fora do HubSpot)
    ("Indicador Registrado", {}),
]


def d_(s):
    try: return date.fromisoformat((s or "")[:10])
    except ValueError: return None


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()
    s = re.sub(r"[^A-Z0-9&() ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def trimestre(x):
    return f"{x.year}-T{(x.month - 1) // 3 + 1}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonte", help="arquivo hubspot-*.json (padrão: o mais recente)")
    ap.add_argument("--hoje", help="data de referência (padrão: data do download)")
    a = ap.parse_args()
    fonte = a.fonte or sorted(glob.glob(os.path.join(SRC, "hubspot-*.json")))[-1]
    D = json.load(open(fonte)); N = D["negocios"]
    hoje = d_(a.hoje) if a.hoje else d_(D["baixado_em"])
    roster = list(json.load(open(MAP))["escopo"]["parceiros_roster"].keys())
    AL = json.load(open(ALIASES)) if os.path.exists(ALIASES) else {}
    ali = {norm(k): v for k, v in AL.get("aliases", {}).items() if not k.startswith("_")}
    ENT = json.load(open(ENTRADAS)) if os.path.exists(ENTRADAS) else {}
    entradas = {k: d_(v) for k, v in ENT.get("datas", {}).items() if d_(v)}
    master_tokens = {m: norm(m).replace("(", "").replace(")", "") for m in roster}

    def unidade_fora(bruto):
        n = norm(bruto)
        if not n or n.replace(" ", "").isdigit(): return SEM
        m = re.search(r"\(([^)]+)\)", n)
        if m and re.search(r"\b(LTDA|ME|EIRELI|SA|EPP)\b", n): n = m.group(1).strip()
        n = re.sub(r"\([^)]*\)", "", n).strip()
        n = re.sub(r"\b(LTDA|ME|EIRELI|EPP|S A)\b", "", n).strip()
        return ali.get(n, n)

    def consultor(d):  # nível abaixo do Master: consultor/escritório indicador
        n = norm(d["parceiro_bruto"])
        n = re.sub(r"\([^)]*\)", "", n).strip()
        if not n or n.startswith(master_tokens[d["parceiro"]]) or re.search(r"\b(LTDA|ASSESSORIA|CONSULTORIA|CONTABE|ORGANIZA|ADVOCACIA)", n):
            n = "(escritório)"
        return ali.get(n, n)

    base_ini = min(min(d_(x["criado"]), d_(x["fechado"]) or d_(x["criado"])) for x in N)
    R = {"fonte": fonte, "baixado_em": D["baixado_em"], "referencia": hoje.isoformat(), "negocios": len(N),
         "base_inicio": base_ini.isoformat()}
    rows = []
    for d in N:
        cr, fe = d_(d["criado"]), d_(d["fechado"])
        ef = min(cr, fe) if fe and cr and fe < cr else cr
        master = d["parceiro"] in roster
        uni = d["parceiro"] if master else unidade_fora(d["parceiro_bruto"])
        rows.append({"d": d, "ef": ef, "fe": fe, "regravada": bool(fe and cr and fe < cr),
                     "unidade": uni, "grupo": "Master (roster)" if master else "Fora do roster",
                     "consultor": consultor(d) if master else None})

    d90, d365 = hoje - timedelta(days=90), hoje - timedelta(days=365)
    lim_base = base_ini + timedelta(days=90)

    def perfil(chave_fn, grupo_fn, entrada_fn=lambda k: None):
        G = defaultdict(list)
        for r in rows:
            k = chave_fn(r)
            if k: G[k].append(r)
        out = []
        for k, L in G.items():
            L.sort(key=lambda r: (r["ef"], r["d"]["id"]))
            prim = L[0]; ini_hs = prim["ef"]; ent = entrada_fn(k)
            ini = ent or ini_hs
            ganhos = sorted([r for r in L if r["d"]["status"] == "ganho" and r["fe"]], key=lambda r: (r["fe"], r["d"]["id"]))
            g_val = [r for r in ganhos if r["d"]["valor"] > 0]
            n90 = sum(1 for r in L if r["ef"] >= d90 and r["ef"] <= hoje)
            g12 = [r for r in ganhos if d365 <= r["fe"] <= hoje]
            p12 = sum(1 for r in L if r["d"]["status"] == "perdido" and r["fe"] and d365 <= r["fe"] <= hoje)
            ativo, prod = n90 > 0, len(g12) > 0
            classe = ("Ativo e produtivo" if ativo and prod else "Ativo em rampa" if ativo else
                      "Dormente" if prod else "Inativo")
            ult = max(r["ef"] for r in L)
            if ent: origem = "data de entrada informada"
            elif ini_hs < lim_base: origem = "anterior à base (não mede onboarding)"
            elif prim["regravada"] or prim["d"]["extras"].get("importado") == "true": origem = "estimada (negócio importado)"
            else: origem = "1º negócio no HubSpot"
            out.append({"parceiro": k, "grupo": grupo_fn(L[0]), "negocios": len(L), "inicio_considerado": ini.isoformat(),
                        "origem_do_inicio": origem, "pipeline_do_1o_registro": prim["d"]["pipeline"], "primeiro_ganho": ganhos[0]["fe"].isoformat() if ganhos else None,
                        "primeiro_ganho_negocio": ganhos[0]["d"]["nome"] if ganhos else None,
                        "dias_ate_1o_ganho": (ganhos[0]["fe"] - ini).days if ganhos else None,
                        "dias_ate_1o_ganho_com_valor": (g_val[0]["fe"] - ini).days if g_val else None,
                        "sem_ganho_ha_dias": None if ganhos else (hoje - ini).days,
                        "negocios_90d": n90, "ganhos_12m": len(g12), "perdidos_12m": p12,
                        "conversao_12m_pct": round(len(g12) / (len(g12) + p12) * 100, 1) if (g12 or p12) else None,
                        "valor_ganho_12m_rs": round(sum(r["d"]["valor"] for r in g12)),
                        "ultimo_negocio": ult.isoformat(), "dias_sem_negocio": (hoje - ult).days,
                        "ativo_90d": "sim" if ativo else "não", "produtivo_12m": "sim" if prod else "não", "classe": classe})
        out.sort(key=lambda x: (x["grupo"] != "Master (roster)", -x["ganhos_12m"], -x["negocios"]))
        return out

    P = perfil(lambda r: r["unidade"], lambda r: r["grupo"], lambda k: entradas.get(k))
    C = perfil(lambda r: f'{r["d"]["parceiro"]} · {r["consultor"]}' if r["consultor"] else None, lambda r: r["d"]["parceiro"],
               lambda k: entradas.get(k))

    # ---------- resumo de tempo até o 1º negócio ----------
    def med(L, campo, filtro):
        v = [x[campo] for x in L if x[campo] is not None and filtro(x)]
        return {"n": len(v), "mediana": statistics.median(v) if v else None, "p75": (sorted(v)[int(len(v) * .75) - 1] if len(v) >= 4 else None)}
    medido = lambda x: x["origem_do_inicio"] in ("1º negócio no HubSpot", "data de entrada informada") and x["parceiro"] != SEM
    # consultores: só pessoas nomeadas; "(escritório)" é variação de grafia do próprio Master, não um indicador novo
    pessoa = lambda x: medido(x) and not x["parceiro"].endswith("(escritório)")
    R["tempo_ate_1o_ganho"] = {"parceiros_medidos": med(P, "dias_ate_1o_ganho", medido),
                               "parceiros_medidos_detalhe": {x["parceiro"]: x["dias_ate_1o_ganho"] for x in P if medido(x)},
                               "consultores_medidos": med(C, "dias_ate_1o_ganho", pessoa),
                               "consultores_medidos_detalhe": {x["parceiro"]: x["dias_ate_1o_ganho"] for x in C if pessoa(x)},
                               "consultores_sem_ganho_medidos": sum(1 for x in C if pessoa(x) and x["dias_ate_1o_ganho"] is None)}
    # ---------- ativos ----------
    def conta(L):
        return {c: sum(1 for x in L if x["classe"] == c) for c in ["Ativo e produtivo", "Ativo em rampa", "Dormente", "Inativo"]}
    Mst = [x for x in P if x["grupo"] == "Master (roster)"]
    Fora = [x for x in P if x["grupo"] != "Master (roster)" and x["parceiro"] != SEM]
    R["ativos"] = {"masters": {"carteira": len(roster), "com_negocios": len(Mst), "ativos_90d": sum(1 for x in Mst if x["ativo_90d"] == "sim"), **conta(Mst)},
                   "fora_do_roster": {"parceiros": len(Fora), "ativos_90d": sum(1 for x in Fora if x["ativo_90d"] == "sim"), **conta(Fora)},
                   "consultores_dos_masters": {"consultores": len(C), "ativos_90d": sum(1 for x in C if x["ativo_90d"] == "sim"), **conta(C)}}

    # ---------- atividade por trimestre ----------
    T = defaultdict(lambda: {"criados": 0, "criados_importados": 0, "ganhos": 0, "perdidos": 0, "valor_ganho_rs": 0.0})
    for r in rows:
        u = r["unidade"]; q = trimestre(r["ef"])
        T[(u, q)]["criados"] += 1
        if r["d"]["extras"].get("importado") == "true": T[(u, q)]["criados_importados"] += 1
        if r["fe"] and r["d"]["status"] in ("ganho", "perdido"):
            qf = trimestre(r["fe"]); k = "ganhos" if r["d"]["status"] == "ganho" else "perdidos"
            T[(u, qf)][k] += 1
            if k == "ganhos": T[(u, qf)]["valor_ganho_rs"] += r["d"]["valor"]
    grupo_de = {x["parceiro"]: x["grupo"] for x in P}
    trims = sorted({q for (_, q) in T})
    atual = trimestre(hoje)
    ativ = []
    for (u, q), v in sorted(T.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        ativ.append({"trimestre": q + (" (parcial)" if q == atual else ""), "parceiro": u, "grupo": grupo_de.get(u), **v,
                     "valor_ganho_rs": round(v["valor_ganho_rs"]),
                     "conversao_pct": round(v["ganhos"] / (v["ganhos"] + v["perdidos"]) * 100, 1) if v["ganhos"] + v["perdidos"] else None,
                     "ativo_no_trimestre": "sim" if v["criados"] > 0 else "não"})
    # canal por trimestre: parceiros ativos (≥1 negócio com data efetiva no trimestre)
    canal = []
    for q in trims:
        us = [u for (u, qq), v in T.items() if qq == q and v["criados"] > 0 and u != SEM]
        canal.append({"trimestre": q + (" (parcial)" if q == atual else ""),
                      "masters_ativos": sum(1 for u in us if u in roster),
                      "fora_roster_ativos": sum(1 for u in us if u not in roster),
                      "criados": sum(v["criados"] for (u, qq), v in T.items() if qq == q),
                      "criados_importados": sum(v["criados_importados"] for (u, qq), v in T.items() if qq == q),
                      "ganhos": sum(v["ganhos"] for (u, qq), v in T.items() if qq == q),
                      "perdidos": sum(v["perdidos"] for (u, qq), v in T.items() if qq == q),
                      "valor_ganho_rs": round(sum(v["valor_ganho_rs"] for (u, qq), v in T.items() if qq == q))})
    R["canal_por_trimestre"] = canal

    # ---------- conferência (os totais precisam fechar com a base) ----------
    conf = [{"checagem": "Negócios na base = soma dos criados por trimestre", "base": len(N), "calculado": sum(c["criados"] for c in canal)},
            {"checagem": "Ganhos com data de fechamento = soma dos ganhos por trimestre", "base": sum(1 for r in rows if r["d"]["status"] == "ganho" and r["fe"]), "calculado": sum(c["ganhos"] for c in canal)},
            {"checagem": "Perdidos com data de fechamento = soma dos perdidos por trimestre", "base": sum(1 for r in rows if r["d"]["status"] == "perdido" and r["fe"]), "calculado": sum(c["perdidos"] for c in canal)},
            {"checagem": "Negócios na base = soma por parceiro", "base": len(N), "calculado": sum(x["negocios"] for x in P)},
            {"checagem": "Negócios dos Masters = soma por consultor", "base": sum(1 for r in rows if r["grupo"] == "Master (roster)"), "calculado": sum(x["negocios"] for x in C)},
            {"checagem": "Negócios com data regravada pela importação (fechado < criado)", "base": sum(1 for r in rows if r["regravada"]), "calculado": sum(1 for r in rows if r["regravada"])}]
    for c in conf: c["ok"] = "✔" if c["base"] == c["calculado"] else "✘ DIVERGE"
    R["conferencia"] = conf

    # ---------- pendências de cadastro (nomes fora do roster que lembram um Master) ----------
    pend = []
    toks = {m: [set(norm(a).split()) for a in al] for m, al in json.load(open(MAP))["escopo"]["parceiros_roster"].items()}
    for x in Fora:
        s = set(x["parceiro"].split())
        for m, L in toks.items():
            if any(len(t) >= 2 and t <= s for t in L):
                pend.append({"nome_fora_do_roster": x["parceiro"], "negocios": x["negocios"], "parece_ser": m,
                             "acao": "Dados & BI confirmar e, se for, incluir o alias no mapeamento-hubspot.json"}); break

    # ---------- simulação de níveis (lê o scorecard do depto-dados; não recalcula saúde) ----------
    sim = []
    sb = sorted(glob.glob(os.path.join(DADOS_BI, "dados-bi-*.json")))
    ativo_de = {x["parceiro"]: x["ativo_90d"] == "sim" for x in P}
    if sb:
        S = json.load(open(sb[-1])); R["scorecard_usado"] = {"arquivo": sb[-1], "baixado_em": S["baixado_em"], "negocios": S["negocios"]}
        for s in S["scorecard"]:
            if s["parceiro"] not in roster: continue
            v = {"ganhos_12m": s["ganhos_12m"], "conversao_12m_pct": s["conversao_12m_pct"] or 0,
                 "honorario_preenchido_pct": s["honorario_preenchido_pct"] or 0, "ativo": ativo_de.get(s["parceiro"], False)}
            nivel = next(n for n, crit in NIVEIS_MASTER if all((v[c] is True) if isinstance(t, bool) else v[c] >= t for c, t in crit.items()))
            falta = []
            for n, crit in NIVEIS_MASTER:
                if n == nivel: break
                falta = [f"{c} ≥ {t}" if not isinstance(t, bool) else "ativo em 90 dias" for c, t in crit.items()
                         if not ((v[c] is True) if isinstance(t, bool) else v[c] >= t)]
            sim.append({"parceiro": s["parceiro"], "nivel_simulado": nivel, **v, "ativo": "sim" if v["ativo"] else "não",
                        "saude_depto_dados": s["saude"], "sinal_saude": s["sinal"],
                        "falta_para_o_nivel_acima": "; ".join(falta) if falta else "—"})
    for x in Fora:
        v = {"ganhos_12m": x["ganhos_12m"], "ativo": x["ativo_90d"] == "sim"}
        nivel = next(n for n, crit in NIVEIS_INDICADOR if all((v[c] is True) if isinstance(t, bool) else v[c] >= t for c, t in crit.items()))
        sim.append({"parceiro": x["parceiro"], "nivel_simulado": nivel + " (sem certificação: dado não existe no HubSpot)",
                    "ganhos_12m": x["ganhos_12m"], "conversao_12m_pct": x["conversao_12m_pct"], "honorario_preenchido_pct": None,
                    "ativo": x["ativo_90d"], "saude_depto_dados": None, "sinal_saude": None, "falta_para_o_nivel_acima": None})
    R["niveis_simulados"] = dict(Counter(s["nivel_simulado"] for s in sim))

    # ---------- saída ----------
    os.makedirs(os.path.join(PS, "metricas"), exist_ok=True)
    stamp = hoje.isoformat()
    R["parceiros"] = P
    json.dump(R, open(os.path.join(PS, "metricas", f"metricas-ps-{stamp}.json"), "w"), ensure_ascii=False, indent=1, default=str)
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = Workbook(); H = Font(bold=True, color="FFFFFF"); HF = PatternFill("solid", fgColor="1F1F1F")

    def aba(nome, linhas, primeira=False):
        ws = wb.active if primeira else wb.create_sheet(nome); ws.title = nome
        if not linhas: ws["A1"] = "Nada a listar."; return ws
        cols = list(linhas[0].keys())
        for j, c in enumerate(cols, 1):
            x = ws.cell(row=1, column=j, value=c); x.font = H; x.fill = HF
            ws.column_dimensions[x.column_letter].width = min(max(12, len(c) + 2), 50)
        for i, l in enumerate(linhas, 2):
            for j, c in enumerate(cols, 1):
                v = l.get(c); x = ws.cell(row=i, column=j, value=v)
                if c.endswith("_rs") and isinstance(v, (int, float)): x.number_format = '#,##0'
        ws.freeze_panes = "A2"; return ws

    t1 = R["tempo_ate_1o_ganho"]; at = R["ativos"]
    resumo = [
        {"indicador": "Referência", "valor": f"{stamp} · base {fonte.rsplit('/', 1)[-1]} ({len(N)} negócios, desde {R['base_inicio']})"},
        {"indicador": "Masters ativos (≥1 negócio em 90 dias) / carteira", "valor": f"{at['masters']['ativos_90d']} / {at['masters']['carteira']}"},
        {"indicador": "Masters: ativos e produtivos · em rampa · dormentes · inativos", "valor": f"{at['masters']['Ativo e produtivo']} · {at['masters']['Ativo em rampa']} · {at['masters']['Dormente']} · {at['masters']['Inativo']}"},
        {"indicador": "Parceiros fora do roster: ativos 90d / total", "valor": f"{at['fora_do_roster']['ativos_90d']} / {at['fora_do_roster']['parceiros']}"},
        {"indicador": "Consultores/escritórios dos Masters: ativos 90d / total", "valor": f"{at['consultores_dos_masters']['ativos_90d']} / {at['consultores_dos_masters']['consultores']}"},
        {"indicador": "Tempo até o 1º ganho — consultores/indicadores nomeados dos Masters (mediana, dias)", "valor": f"{t1['consultores_medidos']['mediana']} (n = {t1['consultores_medidos']['n']}; p75 = {t1['consultores_medidos']['p75']})"},
        {"indicador": "Consultores medidos que ainda não ganharam", "valor": t1["consultores_sem_ganho_medidos"]},
        {"indicador": "Tempo até o 1º ganho — parceiros que entraram depois do início da base (mediana, dias)", "valor": f"{t1['parceiros_medidos']['mediana']} (n = {t1['parceiros_medidos']['n']}: " + ", ".join(f"{k} {v if v is not None else 'sem ganho'}" for k, v in t1['parceiros_medidos_detalhe'].items()) + ")"},
        {"indicador": "Atenção", "valor": "A maioria dos Masters é anterior à base: o HubSpot não guarda a data de entrada do parceiro. Preencha scripts/datas-entrada-parceiros.json para medir o onboarding de verdade."},
        {"indicador": "Conferência", "valor": "todas ok" if all(c["ok"] == "✔" for c in conf) else "HÁ DIVERGÊNCIA — ver aba Conferência"},
    ]
    ws = aba("Resumo", resumo, primeira=True); ws.column_dimensions["A"].width = 62; ws.column_dimensions["B"].width = 110
    defs = [{"termo": k, "definição": v} for k, v in [
        ("Data efetiva", "Menor entre criação e fechamento (as importações regravaram a criação)."),
        ("Ativo", "≥ 1 negócio com data efetiva nos últimos 90 dias (igual ao relatório semanal do depto-resultados)."),
        ("Produtivo", "≥ 1 negócio ganho com fechamento nos últimos 365 dias."),
        ("Ativo em rampa", "Ativo, mas sem ganho em 12 meses (novo ou travado)."),
        ("Dormente", "Sem negócio em 90 dias, mas com ganho em 12 meses: risco de abandono, prioridade da conversa."),
        ("Inativo", "Sem negócio em 90 dias e sem ganho em 12 meses."),
        ("Tempo até o 1º ganho", "Dias do início (data de entrada informada ou 1º negócio) até o fechamento do 1º negócio ganho."),
        ("Anterior à base", "1º registro nos primeiros 90 dias da base: o parceiro já existia; o número não mede onboarding."),
        ("Nível simulado", "Proposta v1 de níveis (rascunho). Critérios no topo do script (NIVEIS_MASTER / NIVEIS_INDICADOR)."),
    ]]
    aba("Definições", defs)
    aba("Parceiros ativos", [{k: x[k] for k in ["parceiro", "grupo", "classe", "ativo_90d", "produtivo_12m", "negocios_90d", "ganhos_12m", "perdidos_12m", "conversao_12m_pct", "valor_ganho_12m_rs", "ultimo_negocio", "dias_sem_negocio"]} for x in P])
    aba("Tempo 1º negócio - parceiro", [{k: x[k] for k in ["parceiro", "grupo", "inicio_considerado", "origem_do_inicio", "primeiro_ganho", "primeiro_ganho_negocio", "dias_ate_1o_ganho", "dias_ate_1o_ganho_com_valor", "sem_ganho_ha_dias", "negocios"]} for x in P])
    aba("Consultores dos Masters", C)
    aba("Canal por trimestre", canal)
    aba("Atividade por trimestre", ativ)
    # matriz Master × trimestre (criados | ganhos)
    mat = []
    for m in roster:
        l = {"parceiro": m}
        for q in trims:
            v = T.get((m, q), {"criados": 0, "ganhos": 0})
            l[f"{q} criados"] = v["criados"]; l[f"{q} ganhos"] = v["ganhos"]
        mat.append(l)
    aba("Masters x trimestre", mat)
    aba("Simulação de níveis", sim)
    aba("Pendências de cadastro", pend)
    aba("Conferência", conf)
    x = os.path.join(PS, "metricas", f"Metricas-PS-{stamp}.xlsx"); wb.save(x); print(x)
    print(json.dumps({k: R[k] for k in ["ativos", "tempo_ate_1o_ganho", "niveis_simulados"]}, ensure_ascii=False, indent=1))
    for c in conf: print(c["ok"], c["checagem"], c["base"], c["calculado"])


if __name__ == "__main__":
    main()
