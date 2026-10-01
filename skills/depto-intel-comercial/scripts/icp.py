#!/usr/bin/env python3
"""Inteligência Comercial — ICP medido nos dados, mapa de território e lead scoring calibrado.

Base: negócios FECHADOS (ganhos + perdidos) dos últimos 24 meses no download do HubSpot.
Regra do Luis: café fora da meta desde abr/2026 → aparece marcado e fica fora do ranking.
Saída: ~/agentes-partners/departamentos/intel-comercial/ICP-AAAA-MM-DD.xlsx + icp-AAAA-MM-DD.json
"""
import glob, json, os
from collections import defaultdict
from datetime import date, timedelta

BASE = os.path.expanduser("~/agentes-partners/departamentos")
SRC = os.path.join(BASE, "resultados/dados"); OUT = os.path.join(BASE, "intel-comercial")
MIN_N = 15  # amostra mínima para um grupo entrar no ranking

GR = [("Pescados", ("pescado", "peixe", "peixaria", "frutos do mar")), ("Carnes & Frigoríficos", ("carne", "frigor", "abate", "aves", "suín", "bovin")), ("Hortifrúti", ("hortifr", "frutas", "legume", "verdura", "hortali")),
      ("Café", ("café", "cafe")), ("Grãos & Cereais", ("cereal", "grão", "grao", "soja", "milho", "arroz", "feijão", "feijao", "ração", "racao")),
      ("Supermercados & Mercearias", ("supermercado", "hipermercado", "mercearia", "minimercado", "armazém")), ("Laticínios & Ovos", ("latic", "leite", "ovos", "queijo")),
      ("Padarias & Confeitarias", ("padaria", "panific", "confeit")), ("Bebidas", ("bebida",)), ("Combustíveis", ("combust",)), ("Transporte & Logística", ("transporte", "logíst"))]


def grupo(t):
    t = (t or "").lower()
    if not t: return "Não informado"
    for g, ks in GR:
        if any(k in t for k in ks): return g
    return "Outros"


def agrega(L, chave):
    A = defaultdict(lambda: {"ganhos": 0, "perdidos": 0, "valor_ganho": 0.0, "liq": 0.0, "liq_n": 0})
    for d in L:
        k = chave(d); a = A[k]
        if d["status"] == "ganho":
            a["ganhos"] += 1; a["valor_ganho"] += d["valor"]
            if d["hContr"] is not None: a["liq"] += d["valor"] * d["hContr"] * (1 - min(d["hParc"] or 0, 1)); a["liq_n"] += 1
        else: a["perdidos"] += 1
    out = []
    for k, a in A.items():
        n = a["ganhos"] + a["perdidos"]; conv = a["ganhos"] / n if n else 0
        ticket = a["valor_ganho"] / a["ganhos"] if a["ganhos"] else 0
        liq_medio = a["liq"] / a["liq_n"] if a["liq_n"] else None
        out.append({"grupo": k if isinstance(k, str) else " · ".join(k), "fechados": n, "ganhos": a["ganhos"], "conversao_pct": round(conv * 100, 1),
                    "ticket_rs": round(ticket), "valor_esperado_por_caso_rs": round(conv * ticket),
                    "honorario_liquido_medio_rs": round(liq_medio) if liq_medio is not None else None,
                    "honorario_esperado_por_caso_rs": round(conv * liq_medio) if liq_medio is not None else None,
                    "amostra": "ok" if n >= MIN_N else f"pequena (< {MIN_N})"})
    return sorted(out, key=lambda x: -(x["honorario_esperado_por_caso_rs"] or 0))


def main():
    f = sorted(glob.glob(os.path.join(SRC, "hubspot-*.json")))[-1]; N = json.load(open(f))["negocios"]
    hoje = date.today(); desde = (hoje - timedelta(days=730)).isoformat()
    F = [d for d in N if d["status"] in ("ganho", "perdido") and (d["fechado"] or "") >= desde]
    # CNAE oficial da Receita (receita_cnpj.py --enriquecer) preenche perdidos e abertos sem CNAE no HubSpot
    enr_p = os.path.join(OUT, "enriquecimento-receita.json"); ENR = json.load(open(enr_p))["negocios"] if os.path.exists(enr_p) else {}
    usados = 0
    for d in F:
        e = ENR.get(d["id"])
        if e and e.get("cnae_desc_oficial"):
            if not d.get("segmento"): usados += 1
            d["segmento"] = d.get("segmento") or e["cnae_desc_oficial"]
            d["extras"]["uf"] = d["extras"].get("uf") or e.get("uf_oficial")
    for d in F:
        d["seg"] = grupo(d.get("segmento")); d["regime"] = (d["extras"].get("regime") or "Não informado").strip()
        d["uf"] = (d["extras"].get("uf") or "—").strip()
    R = {"fonte": f, "base": f"{len(F)} negócios fechados desde {desde} (ganhos + perdidos)", "cnae_oficial_receita_usado_em": usados,
         "ressalvas": ["Segmento só é preenchido após o ganho em muitos negócios: perdidos sem CNAE caem em 'Não informado' e inflam a conversão dos segmentos conhecidos.",
                       "'Grãos' no HubSpot é quase todo 'Comércio atacadista de café em grão' (284 ganhos): classificado como Café, fora da meta. Cereais de fato têm amostra mínima.",
                       "Café fora da meta desde abr/2026 (regra do Luis): aparece marcado e fica fora do ranking.",
                       f"Grupos com menos de {MIN_N} negócios fechados são marcados como amostra pequena."]}
    R["por_segmento"] = agrega(F, lambda d: d["seg"])
    R["por_regime"] = agrega(F, lambda d: d["regime"])
    R["por_uf"] = agrega(F, lambda d: d["uf"])
    R["segmento_x_regime"] = [x for x in agrega(F, lambda d: (d["seg"], d["regime"])) if x["fechados"] >= MIN_N]
    R["segmento_x_uf"] = [x for x in agrega(F, lambda d: (d["seg"], d["uf"])) if x["fechados"] >= MIN_N]
    for tab in ("por_segmento", "segmento_x_regime", "segmento_x_uf"):
        for x in R[tab]:
            x["conversao_confiavel"] = "sim (CNAE oficial da Receita)" if ENR else "não (perdidos sem CNAE)"
            if x["grupo"].startswith("Café"): x["amostra"] = "FORA DA META (regra do café)"
    # ---------- Território: onde cada parceiro já ganha (12 meses) ----------
    d365 = (hoje - timedelta(days=365)).isoformat(); T = defaultdict(lambda: defaultdict(float))
    for d in F:
        if d["status"] == "ganho" and d["fechado"] >= d365 and not d["parceiro"].startswith("Outros"):
            T[d["parceiro"]][(d["seg"], d["uf"])] += d["valor"]
    terr = []
    for p, m in T.items():
        tot = sum(m.values()) or 1
        for (sg, uf), v in sorted(m.items(), key=lambda x: -x[1])[:5]:
            terr.append({"parceiro": p, "segmento": sg, "uf": uf, "valor_ganho_12m_rs": round(v), "participacao_no_parceiro_pct": round(v / tot * 100, 1)})
    R["territorio"] = terr
    # ---------- Lead scoring v1: pontos pelo honorário esperado por caso (conversão × honorário líquido) ----------
    # Café fica fora da base (fora da meta). Segmento usa honorário médio do ganho (conversão por segmento não é confiável).
    Fm = [d for d in F if d["seg"] != "Café"]
    gan = [d for d in Fm if d["status"] == "ganho" and d["hContr"] is not None]
    liq_medio = sum(d["valor"] * d["hContr"] * (1 - min(d["hParc"] or 0, 1)) for d in gan) / len(gan)
    conv_m = sum(1 for d in Fm if d["status"] == "ganho") / len(Fm)
    esp_medio = conv_m * liq_medio
    pts = lambda lift: max(0, min(30, round(min(lift, 2) / 2 * 30)))
    SC = []
    for nome, tab, chave in [("Regime", agrega(Fm, lambda d: d["regime"]), "honorario_esperado_por_caso_rs"),
                             ("UF", agrega(Fm, lambda d: d["uf"]), "honorario_esperado_por_caso_rs"),
                             ("Segmento", agrega(Fm, lambda d: d["seg"]), "honorario_liquido_medio_rs")]:
        ref = esp_medio if chave == "honorario_esperado_por_caso_rs" else liq_medio
        for x in tab:
            if x["amostra"] != "ok" or x["grupo"] in ("Não informado", "—") or x[chave] is None: continue
            lift = x[chave] / ref
            SC.append({"dimensao": nome, "valor": x["grupo"], "base_do_calculo": "conversão × honorário" if nome != "Segmento" else "honorário médio do ganho",
                       "valor_rs": x[chave], "lift_vs_media": round(lift, 2), "pontos_sugeridos": pts(lift)})
    R["media_referencia"] = {"conversao_pct": round(conv_m * 100, 1), "honorario_liquido_medio_rs": round(liq_medio), "honorario_esperado_por_caso_rs": round(esp_medio)}
    R["lead_scoring_v1"] = sorted(SC, key=lambda x: (x["dimensao"], -x["pontos_sugeridos"]))
    os.makedirs(OUT, exist_ok=True); stamp = hoje.isoformat()
    json.dump(R, open(os.path.join(OUT, f"icp-{stamp}.json"), "w"), ensure_ascii=False, indent=1)
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    wb = Workbook(); H = Font(bold=True, color="FFFFFF"); HF = PatternFill("solid", fgColor="1F1F1F"); first = True
    for nome, key in [("Segmento", "por_segmento"), ("Regime", "por_regime"), ("UF", "por_uf"), ("Segmento x Regime", "segmento_x_regime"),
                      ("Segmento x UF", "segmento_x_uf"), ("Território parceiros", "territorio"), ("Lead scoring v1", "lead_scoring_v1")]:
        ws = wb.active if first else wb.create_sheet(nome); ws.title = nome; first = False; L = R[key]
        if not L: continue
        cols = list(L[0].keys())
        for j, c in enumerate(cols, 1):
            x = ws.cell(row=1, column=j, value=c); x.font = H; x.fill = HF; ws.column_dimensions[x.column_letter].width = max(14, min(40, len(c) + 4))
        for i, l in enumerate(L, 2):
            for j, c in enumerate(cols, 1): ws.cell(row=i, column=j, value=l[c])
        ws.freeze_panes = "A2"
    ws = wb.create_sheet("Ressalvas")
    for i, t in enumerate([R["base"]] + R["ressalvas"], 1): ws.cell(row=i, column=1, value=t)
    ws.column_dimensions["A"].width = 140
    x = os.path.join(OUT, f"ICP-{stamp}.xlsx"); wb.save(x); print(x)


if __name__ == "__main__":
    main()
