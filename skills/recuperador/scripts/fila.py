#!/usr/bin/env python3
"""Recuperador — fila da célula da Geovana: perdidos zerados + abertos há mais de 90 dias, com look-alike.

Entrada: download do HubSpot (depto-resultados) + enriquecimento oficial da Receita (depto-intel-comercial)
         + texto dos pareceres, se já extraídos (recuperador/scripts/pareceres.py).
Saída:   ~/agentes-partners/celulas/geovana/recuperador/Fila-Recuperador-AAAA-MM-DD.xlsx

Look-alike: para cada caso, os ganhos mais parecidos (CNAE, regime, UF, porte, capital) dos últimos 36 meses
dão o potencial (mediana do crédito e do honorário líquido) e a taxa de sucesso dos casos parecidos
(ganhos ÷ fechados parecidos). Honorário esperado = taxa × honorário mediano dos parecidos.
Regras fixas: fora café (fora da meta desde abr/2026), Simples e CNPJ baixado/inapto; Presumido sem tese de crédito
nas aquisições; variante A nunca como hipótese principal (D14). Tudo é pré-análise: a Geovana decide.
"""
import argparse, glob, json, math, os, re, statistics
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

H = os.path.expanduser
SRC = H("~/agentes-partners/departamentos/resultados/dados")
ENR = H("~/agentes-partners/departamentos/intel-comercial/enriquecimento-receita.json")
PAR = H("~/agentes-partners/celulas/geovana/pareceres/resumos.json")
OUT = H("~/agentes-partners/celulas/geovana/recuperador")
LINK = "https://app.hubspot.com/contacts/47865021/deal/{}"
DOCS = "EFD-Contribuições (60 meses) · EFD ICMS/IPI · ECD/ECF · XMLs de entrada · PER/DCOMP já transmitidos · ações judiciais em curso"
SEG = [("Pescados", ("pescado", "peixe", "peixaria")), ("Carnes & Frigoríficos", ("carne", "frigor", "abate", "aves", "suín", "bovin")),
       ("Hortifrúti", ("hortifr", "frutas", "legume", "verdura", "hortali")), ("Café", ("café", "cafe")),
       ("Supermercados & Mercearias", ("supermercado", "hipermercado", "mercearia", "minimercado")), ("Laticínios & Ovos", ("latic", "leite", "ovos", "queijo")),
       ("Atacado de alimentos", ("atacadista de produtos alimentícios", "atacadista de alimentos", "predominância de produtos alimentícios")),
       ("Padarias & Confeitarias", ("padaria", "panific", "confeit"))]
ALVO = {"Carnes & Frigoríficos", "Hortifrúti", "Pescados", "Atacado de alimentos", "Laticínios & Ovos"}
MATRIZ = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "matriz.json")))["matriz"]
CORTE_URGENCIA = date(2026, 11, 30)  # saldo credor precisa ser escriturado antes de 31/12/2026 (LC 214 art. 378, leitura conservadora)


def linha_matriz(cnae, regime):
    reg = "Real" if regime.startswith("Lucro Real") else "Presumido" if regime.startswith("Lucro Presumido") else None
    if not reg: return None
    cands = [(len(pf), m) for m in MATRIZ if m["regime"] == reg for pf in m["prefixos"] if cnae.startswith(pf)]
    return max(cands, key=lambda x: x[0])[1] if cands else None


def raiz(d, E):
    c = re.sub(r"\D", "", str(E.get(d["id"], {}).get("cnpj") or d["extras"].get("cnpj") or ""))
    return c.zfill(14)[:8] if c else None  # sem CNPJ não tem grupo (antes todos viravam "00000000" e colidiam: falsa duplicidade)


DECISAO = ("decisão da Geovana", "motivo da decisão", "valor validado (R$)", "minutos no caso", "encaminhado ao técnico em")


def decisoes_anteriores():
    """link → decisões já marcadas. Lê todas as Fila-Recuperador-*.xlsx do Mac e da pasta da Geovana no OneDrive; a mais recente vence.
    Antes cada fila nova saía em branco e o que a Geovana marcava no arquivo da semana anterior se perdia (TI, 13/10/2026)."""
    from openpyxl import load_workbook
    fs = glob.glob(os.path.join(OUT, "Fila-Recuperador-*.xlsx"))
    try:
        import sys; sys.path.insert(0, H("~/agentes-partners/lib")); import caminhos
        fs += glob.glob(os.path.join(caminhos.area(), "Central Técnica · Geovana", "Fila-Recuperador-*.xlsx"))
    except (SystemExit, Exception):
        pass  # sem OneDrive: usa só as do Mac
    out = {}
    for f in sorted(fs, key=os.path.getmtime):
        try: rows = list(load_workbook(f, read_only=True, data_only=True)["Fila"].iter_rows(values_only=True))
        except Exception: continue
        if not rows: continue
        h = list(rows[0])
        for r in rows[1:]:
            g = dict(zip(h, r)); d = {k: g.get(k) for k in DECISAO if g.get(k) not in (None, "")}
            if d and g.get("link"): out.setdefault(g["link"], {}).update(d)
    return out


def seg(t):
    t = (t or "").lower()
    for g, ks in SEG:
        if any(k in t for k in ks): return g
    return "Outros" if t else "Sem CNAE"


def dt(s):
    try: return datetime.fromisoformat((s or "")[:10]).date()
    except ValueError: return None


def perfil(d, E):
    e = E.get(d["id"], {})
    cn = str(e.get("cnae_oficial") or d.get("cnae") or "")
    return {"cnae": cn, "classe": cn[:4], "seg": seg(e.get("cnae_desc_oficial") or d.get("segmento")), "regime": (d["extras"].get("regime") or "").strip(),
            "uf": e.get("uf_oficial") or d["extras"].get("uf"), "porte": e.get("porte_oficial"), "capital": e.get("capital_social") or 0,
            "situacao": e.get("situacao"), "simples": e.get("simples"), "cnae_desc": e.get("cnae_desc_oficial") or d.get("segmento")}


CAFE_NOME = ("cafe", "café", "coffee", "torref")


def eh_cafe(d, p):
    return p["seg"] == "Café" or any(k in (d.get("nome") or "").lower() for k in CAFE_NOME)


def parecido(a, b):
    """Pontuação de semelhança (0–14). Regime diferente derruba: a tese depende do regime."""
    if a["regime"] and b["regime"] and a["regime"].split()[0:2] != b["regime"].split()[0:2]: return 0
    s = 0
    if a["cnae"] and a["cnae"] == b["cnae"]: s += 5
    elif a["classe"] and a["classe"] == b["classe"]: s += 3
    elif a["seg"] == b["seg"] and a["seg"] not in ("Outros", "Sem CNAE"): s += 2
    else: return 0
    s += 3 if a["regime"] == b["regime"] and a["regime"] else 0
    s += 2 if a["uf"] and a["uf"] == b["uf"] else 0
    s += 1 if a["porte"] and a["porte"] == b["porte"] else 0
    if a["capital"] and b["capital"]:
        r = a["capital"] / b["capital"]; s += 3 if 0.5 <= r <= 2 else 1 if 0.2 <= r <= 5 else 0
    return s


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--desde", default="2026-01-01"); ap.add_argument("--lote", type=int, default=20)
    ap.add_argument("--dias-aberto", type=int, default=90); a = ap.parse_args()
    N = json.load(open(sorted(glob.glob(os.path.join(SRC, "hubspot-*.json")))[-1]))["negocios"]
    E = json.load(open(ENR))["negocios"] if os.path.exists(ENR) else {}
    PR = json.load(open(PAR)) if os.path.exists(PAR) else {}
    hoje = date.today(); d36 = (hoje - timedelta(days=1095)).isoformat()
    # referência do look-alike: fechados dos últimos 36 meses, fora café
    ref = []
    for d in N:
        if d["status"] in ("ganho", "perdido") and (d["fechado"] or "") >= d36:
            p = perfil(d, E)
            if eh_cafe(d, p): continue
            liq = d["valor"] * d["hContr"] * (1 - min(d["hParc"] or 0, 1)) if (d["status"] == "ganho" and d["hContr"] is not None and d["valor"] > 0) else None
            ref.append((d, p, liq))
    ganhos_ref = [(d, p, l) for d, p, l in ref if d["status"] == "ganho" and d["valor"] > 0]
    GANHOS_RAIZ = {raiz(d, E) for d, p, l in ganhos_ref} - {None}
    ABERTOS_RAIZ = {raiz(d, E) for d in N if d["status"] == "aberto"} - {None}
    casos = [("Perdido zerado", d) for d in N if d["status"] == "perdido" and d["valor"] <= 0 and (d["fechado"] or "") >= a.desde]
    casos += [("Aberto > %d dias" % a.dias_aberto, d) for d in N if d["status"] == "aberto" and dt(d["criado"]) and (hoje - dt(d["criado"])).days > a.dias_aberto]
    fila, fora = [], []
    for tipo, d in casos:
        p = perfil(d, E)
        base = {"tipo": tipo, "negócio": d["nome"], "parceiro": d["parceiro"], "etapa": d.get("etapa") or d["status"], "regime": p["regime"] or "não informado",
                "segmento": p["seg"], "cnae_oficial": f"{p['cnae']} {p['cnae_desc'] or ''}".strip(), "porte_receita": p["porte"], "capital_social": p["capital"] or None,
                "uf": p["uf"], "data_ref": d["fechado"] if tipo.startswith("Perdido") else d["criado"],
                "dias_aberto": (hoje - dt(d["criado"])).days if tipo.startswith("Aberto") else None, "valor_no_hubspot": round(d["valor"]) or None, "link": LINK.format(d["id"])}
        motivo = None
        if p["situacao"] and p["situacao"] != "Ativa": motivo = f"CNPJ {p['situacao'].lower()} na Receita"
        elif p["regime"].startswith("Simples") or p["simples"] == "S": motivo = "Simples Nacional: sem crédito de PIS/COFINS não cumulativo"
        elif eh_cafe(d, p): motivo = "Café: fora da meta desde abr/2026"
        rz = raiz(d, E); par = PR.get(d["id"], {}); sp = par.get("sinal_reanalise") or ""
        if not motivo and ("passivo" in (d.get("pipeline") or "").lower() or "(passivo" in (d.get("nome") or "").lower()): motivo = "V4 Gestão de Passivo: outro produto, o valor zero não mede crédito"
        if not motivo and rz in GANHOS_RAIZ: motivo = "V5 já é cliente (ganho no mesmo grupo): tratar como recorrência com o parceiro"
        if not motivo and tipo.startswith("Perdido") and rz in ABERTOS_RAIZ: motivo = "V6 duplicidade: o grupo já tem negócio aberto"
        if not motivo and sp.startswith(("Vetar", "Não reanalisar, salvo")): motivo = "V11 parecer: " + sp
        if motivo: fora.append({"motivo": motivo, **base}); continue
        # look-alike
        rz = raiz(d, E); vistos_r = set(); viz = []
        for v in sorted(((parecido(p, q), dd, l) for dd, q, l in ref if rz is None or raiz(dd, E) != rz), key=lambda x: -x[0]):
            r_ = raiz(v[1], E)
            if v[0] < 8 or (r_ is not None and r_ in vistos_r): continue   # exige CNAE/classe igual + regime; uma empresa conta uma vez
            vistos_r.add(r_); viz.append(v)
            if len(viz) >= 40: break
        vg = [v for v in viz if v[1]["status"] == "ganho" and v[1]["valor"] > 0]
        taxa = len(vg) / len(viz) if len(viz) >= 8 else None
        cred_med = statistics.median(v[1]["valor"] for v in vg) if vg else None
        liqs = [v[2] for v in vg if v[2]]
        hon_med = statistics.median(liqs) if liqs else None
        esperado = taxa * hon_med if (taxa is not None and hon_med) else None
        mz = linha_matriz(p["cnae"], p["regime"])
        if mz:
            ader = mz["aderencia"]; docs = mz["documentos"]; saldo = mz["saldo_credor"]; segf = mz["segmento"]
            if mz.get("tese_save"):  # entendimento da Save como hipótese principal (decisão do Luis, 29/09/2026)
                hip = f"PRINCIPAL (tese Save): {mz['tese_save']}. ALTERNATIVA conservadora: {mz['tese']} [{mz['variante']}]. {mz['observacao']} {mz['risco_tese_save']}".strip()
            else:
                hip = f"{mz['tese']} [{mz['variante']}] — {mz['observacao']}"
        else:
            ader, hip, docs, saldo, segf = "a verificar", "Regime não informado: confirmar o regime antes de reanalisar.", DOCS, False, p["seg"]
        if sp.startswith("Mudar a tese para B"): hip = "Manutenção e ressarcimento de créditos ligados a vendas com alíquota zero [B] (parecer: sem recolhimento por alíquota zero)"
        fila.append({**base, "segmento (matriz)": segf, "aderência": ader, "saldo credor (urgente até 30/11)": "sim" if saldo else "não",
                     "honorário esperado (look-alike)": round(esperado) if esperado else None,
                     "taxa de sucesso dos parecidos": f"{taxa*100:.0f}% ({len(vg)} de {len(viz)})" if taxa is not None else f"amostra pequena ({len(viz)})",
                     "crédito mediano dos parecidos": round(cred_med) if cred_med else None, "honorário mediano dos parecidos": round(hon_med) if hon_med else None,
                     "ganhos parecidos (exemplos)": " · ".join(f"{v[1]['nome'][:40]} ({v[1]['parceiro']})" for v in vg[:3]),
                     "sinal do parecer": par.get("sinal_reanalise"),
                     "parecer do técnico": par.get("resumo") or ("não extraído" if not PR else "sem parecer no card"),
                     "motivo no parecer": par.get("motivo"), "hipótese preliminar": hip, "documentos a pedir": docs,
                     "decisão da Geovana": "", "motivo da decisão": "", "valor validado (R$)": "", "minutos no caso": "", "encaminhado ao técnico em": ""})
    # uma linha por CNPJ e tipo (a empresa pode ter mais de um negócio no HubSpot)
    vistos, unicos = {}, []
    for r in sorted(fila, key=lambda r: -(r["honorário esperado (look-alike)"] or 0)):
        cn = re.sub(r"\D", "", str(E.get(r["link"].rsplit("/", 1)[1], {}).get("cnpj") or "")) or r["negócio"]
        k = (cn, r["tipo"])
        if k in vistos: vistos[k]["negócios no HubSpot"] += 1; continue
        r["negócios no HubSpot"] = 1; vistos[k] = r; unicos.append(r)
    fila = unicos
    # prioridade: honorário esperado; sem look-alike, cai para o fim do seu grupo de aderência
    urgente = date.today() <= CORTE_URGENCIA
    for r in fila:  # parecer do técnico e urgência ajustam a prioridade (revisão do Tributário, 29/09)
        e_ = r["honorário esperado (look-alike)"]
        if not e_: continue
        sp = r.get("sinal do parecer") or ""
        f = 1.25 if sp.startswith("Reanalisar") else 1.1 if sp.startswith(("Mudar a tese", "Recorrência")) else 0.2 if sp.startswith("Não reanalisar") else 1.0
        if urgente and r["saldo credor (urgente até 30/11)"] == "sim": f *= 1.25
        if r["aderência"] == "vetar": f = 0
        r["honorário esperado (look-alike)"] = round(e_ * f)
    ordem = {"alta": 0, "média": 1, "a verificar": 2, "baixa": 3, "vetar": 4}
    fila.sort(key=lambda r: (-(r["honorário esperado (look-alike)"] or 0), ordem[r["aderência"]]))
    for i, r in enumerate(fila, 1): r["lote"] = (i - 1) // a.lote + 1; r["prioridade"] = i
    os.makedirs(OUT, exist_ok=True)
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.worksheet.datavalidation import DataValidation
    wb = Workbook(); H1 = Font(bold=True, color="FFFFFF"); HF = PatternFill("solid", fgColor="1F1F1F")
    largos = {"hipótese preliminar", "documentos a pedir", "negócio", "cnae_oficial", "ganhos parecidos (exemplos)", "parecer do técnico", "motivo no parecer"}
    def aba(ws, L, cols):
        ws.append(cols)
        for j, c in enumerate(cols, 1):
            x = ws.cell(row=1, column=j); x.font = H1; x.fill = HF; ws.column_dimensions[x.column_letter].width = 46 if c in largos else 16
        for i, l in enumerate(L, 2):
            ws.append([l.get(c) for c in cols])
            if "link" in cols: x = ws.cell(row=i, column=cols.index("link") + 1); x.hyperlink = l["link"]; x.font = Font(color="1F5FBF", underline="single")
        ws.freeze_panes = "C2"
    cols = ["prioridade", "lote", "tipo", "aderência", "honorário esperado (look-alike)", "taxa de sucesso dos parecidos", "crédito mediano dos parecidos",
            "honorário mediano dos parecidos", "saldo credor (urgente até 30/11)", "negócio", "negócios no HubSpot", "parceiro", "etapa", "dias_aberto", "regime", "segmento (matriz)", "cnae_oficial", "porte_receita", "capital_social", "uf",
            "sinal do parecer", "parecer do técnico", "motivo no parecer", "ganhos parecidos (exemplos)", "hipótese preliminar", "documentos a pedir",
            "decisão da Geovana", "motivo da decisão", "valor validado (R$)", "minutos no caso", "encaminhado ao técnico em", "link"]
    ant = decisoes_anteriores()  # decisões da Geovana marcadas em qualquer planilha anterior (Mac ou OneDrive) vêm para a fila nova
    for l in fila:
        for k, v in (ant.get(l.get("link")) or {}).items():
            if not l.get(k): l[k] = v
    ws = wb.active; ws.title = "Fila"; aba(ws, fila, cols)
    dv = DataValidation(type="list", formula1='"Aprovar para reanálise,Vetar,Precisa de dado"', allow_blank=True); ws.add_data_validation(dv)
    col = ws.cell(row=1, column=cols.index("decisão da Geovana") + 1).column_letter; dv.add(f"{col}2:{col}{len(fila) + 1}")
    cf = ["motivo", "tipo", "negócio", "parceiro", "etapa", "regime", "segmento", "cnae_oficial", "uf", "data_ref", "link"]
    aba(wb.create_sheet("Recorrência (já clientes)"), [r for r in fora if r["motivo"].startswith("V5")], cf)
    aba(wb.create_sheet("Gestão de Passivo"), [r for r in fora if r["motivo"].startswith("V4")], cf)
    aba(wb.create_sheet("Fora da fila"), [r for r in fora if not r["motivo"].startswith(("V4", "V5"))], cf)
    rs = wb.create_sheet("Resumo"); esp = [r["honorário esperado (look-alike)"] or 0 for r in fila]
    linhas = [["Casos na fila", len(fila)], ["Fora da fila", len(fora)]] + [[f"Tipo: {k}", v] for k, v in Counter(r["tipo"] for r in fila).most_common()] + \
             [[f"Aderência {k}", v] for k, v in Counter(r["aderência"] for r in fila).most_common()] + \
             [["Honorário esperado somado (look-alike, potencial)", round(sum(esp))], ["Honorário esperado do 1º lote", round(sum(esp[:a.lote]))]] + \
             [[f"Fora: {k}", v] for k, v in Counter(r["motivo"].split(":")[0] for r in fora).most_common()] + \
             [["Matriz", "Hipótese, aderência e documentos vêm da matriz tese × perfil do Depto Tributário (references/matriz.json, 29/09/2026). Look-alike exclui a própria empresa (raiz do CNPJ). +25% só para saldo credor até 30/11/2026. Vetos V4 (passivo), V5 (já cliente), V6 (duplicidade), V11 (parecer estrutural)."]] + \
             [["Parecer do técnico", "Quando há parecer: 'Reanalisar' (abaixo do mínimo/já ressarcido + 6 meses novos) aumenta a prioridade em 25%; 'regime não permite' reduz a 20%."]] + \
             [["Método", "Look-alike: ganhos parecidos (CNAE, regime, UF, porte, capital) dos últimos 36 meses, fora café. Honorário esperado = taxa de sucesso dos parecidos × honorário líquido mediano dos parecidos. Potencial, não promessa."]]
    for l in linhas: rs.append(l)
    rs.column_dimensions["A"].width = 52; rs.column_dimensions["B"].width = 110
    f = os.path.join(OUT, f"Fila-Recuperador-{hoje.isoformat()}.xlsx"); wb.save(f)
    json.dump({"fila": len(fila), "fora": len(fora), "tipos": Counter(r["tipo"] for r in fila), "aderencia": Counter(r["aderência"] for r in fila),
               "esperado_total": round(sum(esp)), "esperado_lote1": round(sum(esp[:a.lote])), "top": fila[:a.lote]},
              open(os.path.join(OUT, f"fila-{hoje.isoformat()}.json"), "w"), ensure_ascii=False, indent=1, default=str)
    print(f, "| fila", len(fila), "| fora", len(fora), "|", dict(Counter(r["tipo"] for r in fila)), "| esperado total R$", round(sum(esp)), "| 1º lote R$", round(sum(esp[:a.lote])))


if __name__ == "__main__":
    main()
