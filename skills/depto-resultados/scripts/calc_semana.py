#!/usr/bin/env python3
"""Cálculo determinístico das métricas semanais da Área Partners.

Fontes: snapshot do cockpit Master (site publicado), modelo de margem do S&OE
(Firestore soe/main, leitura pública) e premissas-financeiras.xlsx (custos,
impostos, metas). Gera metricas-AAAA-MM-DD.json + resumo .md.

Uso: python3 calc_semana.py [--data AAAA-MM-DD] [--cockpit arquivo_ou_url]
"""
import argparse, json, os, re, sys
from collections import Counter, defaultdict
from datetime import date, datetime

BASE = os.path.expanduser("~/agentes-partners/departamentos/resultados")
COCKPIT_URL = "https://save-partner-soe.web.app/"
SOE_URL = "https://firestore.googleapis.com/v1/projects/save-partner-soe/databases/(default)/documents/soe/main"
PREMISSAS = os.path.join(BASE, "premissas-financeiras.xlsx")


def fetch(src):
    if src.startswith("http"):  # curl usa o repositório de certificados do sistema
        import subprocess
        return subprocess.run(["curl", "-sSfL", "-m", "30", src], check=True, capture_output=True).stdout.decode("utf-8")
    return open(os.path.expanduser(src), encoding="utf-8").read()


def fs_conv(v):
    k = next(iter(v)); x = v[k]
    if k == "mapValue": return {a: fs_conv(b) for a, b in x.get("fields", {}).items()}
    if k == "arrayValue": return [fs_conv(i) for i in x.get("values", [])]
    if k == "integerValue": return int(x)
    if k == "doubleValue": return float(x)
    return x


def ym_add(ym, n):
    y, m = int(ym[:4]), int(ym[5:7]) + n
    while m <= 0: y, m = y - 1, m + 12
    while m > 12: y, m = y + 1, m - 12
    return f"{y:04d}-{m:02d}"


def growth(cur, prev):
    if not prev: return {"atual": cur, "anterior": prev, "fator": None, "pct": None}
    f = cur / prev
    return {"atual": cur, "anterior": prev, "fator": round(f, 3), "pct": round((f - 1) * 100, 1)}


def load_premissas():
    out = {"custo_mensal": None, "carga_tributaria": None, "metas": {}, "pendencias": []}
    try:
        from openpyxl import load_workbook
        wb = load_workbook(PREMISSAS, data_only=True)
    except Exception as e:
        out["pendencias"].append(f"premissas-financeiras.xlsx ilegível ({e})"); return out
    out["custos_mensais"] = {}
    if "Custos BI (mensal)" in wb.sheetnames:
        for r in wb["Custos BI (mensal)"].iter_rows(min_row=5, values_only=True):
            if not r[0]: continue
            c = out["custos_mensais"].setdefault(str(r[0]), {"orcado": 0.0, "realizado": 0.0, "linhas": {}})
            c["orcado"] += r[3] or 0; c["realizado"] += r[4] or 0; c["linhas"][f"{r[1]} · {r[2]}"] = r[4] if r[4] is not None else None
    out["antes_de_impostos"] = False
    ws = wb["Impostos"]
    for r in ws.iter_rows(min_row=5, values_only=True):
        if r[0] and str(r[0]).startswith("Carga total") and r[3] and "ANTES de impostos" in str(r[3]): out["antes_de_impostos"] = True
    ws = wb["Custos da área"]; vals = [r[2] for r in ws.iter_rows(min_row=5, values_only=True) if r[1]]
    nums = [v for v in vals if isinstance(v, (int, float))]
    if nums: out["custo_mensal"] = float(sum(nums))
    if out["custos_mensais"]: pass
    elif len(nums) < len(vals): out["pendencias"].append(f"Custos da área: {len(vals)-len(nums)} de {len(vals)} itens sem valor")
    ws = wb["Impostos"]
    for r in ws.iter_rows(min_row=5, values_only=True):
        if r[0] and str(r[0]).startswith("Carga total") and isinstance(r[2], (int, float)):
            out["carga_tributaria"] = float(r[2]) / (100 if r[2] > 1 else 1)
    if out["carga_tributaria"] is None and not out["antes_de_impostos"]: out["pendencias"].append("Impostos: carga tributária da Save não informada")
    ws = wb["Metas"]
    for r in ws.iter_rows(min_row=5, values_only=True):
        if r[0] and any(isinstance(x, (int, float)) for x in r[1:]):
            out["metas"][r[0]] = {"criados_n": r[1], "criados_rs": r[2], "fechados_rs": r[3], "honorario_rs": r[4], "lucro_rs": r[5]}
    if not out["metas"]: out["pendencias"].append("Metas: nenhuma meta mensal informada")
    return out


def carregar_hubspot(hoje, M):
    """Baixa do HubSpot e converte para o mesmo formato do cockpit. Retorna None se não houver credencial."""
    import importlib.util, subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    dia = os.path.expanduser(f"~/agentes-partners/departamentos/resultados/dados/hubspot-{hoje}.json")
    if os.path.exists(dia):  # um download por dia: reaproveita o do terminal (partners hubspot)
        class _R: returncode = 0; stdout = dia; stderr = ""
        r = _R()
    else:
        r = subprocess.run([sys.executable, os.path.join(here, "hubspot_fonte.py"), "--baixar"], capture_output=True, text=True)
    if r.returncode != 0:
        M["pendencias"].append("Acesso direto ao HubSpot: " + (r.stderr or r.stdout).strip().splitlines()[-1])
        return None
    norm = json.load(open(r.stdout.split()[0]))["negocios"]
    regras = json.load(open(os.path.expanduser("~/agentes-partners/departamentos/resultados/mapeamento-hubspot.json"))).get("regras", {})
    corte = regras.get("excluir_cafe_desde")
    if corte:
        kw = regras.get("cafe_palavras", []); cn = set(regras.get("cafe_cnae", []))
        def cafe(d):
            txt = f"{d.get('nome') or ''} {d.get('segmento') or ''}".lower()
            return any(k in txt for k in kw) or str(d.get("cnae") or "").lstrip("0") in {c.lstrip("0") for c in cn}
        ref = lambda d: (d["fechado"] if d["status"] != "aberto" else d["criado"])[:7]
        fora = [d for d in norm if cafe(d) and ref(d) >= corte]
        norm = [d for d in norm if d not in fora]
        M["regra_cafe"] = {"desde": corte, "excluidos_n": len(fora), "excluidos_ganhos_rs": round(sum(d["valor"] for d in fora if d["status"] == "ganho"))}
    # segmento agrupado a partir da descrição do CNAE
    GR = [("Carnes & Frigoríficos", ("carne", "frigor", "abate", "aves", "suín", "bovin")), ("Hortifrúti", ("hortifr", "frutas", "legume", "verdura", "hortali")),
          ("Grãos & Cereais", ("cereal", "grão", "grao", "soja", "milho", "arroz", "feijão", "feijao", "ração", "racao")), ("Café", ("café", "cafe")),
          ("Supermercados & Mercearias", ("supermercado", "hipermercado", "mercearia", "minimercado", "armazém")), ("Laticínios & Ovos", ("latic", "leite", "ovos", "queijo")),
          ("Padarias & Confeitarias", ("padaria", "panific", "confeit")), ("Bebidas", ("bebida",)), ("Combustíveis", ("combust",)), ("Transporte & Logística", ("transporte", "logíst"))]
    def grupo(t):
        t = (t or "").lower()
        if not t: return "Não informado"
        for g, ks in GR:
            if any(k in t for k in ks): return g
        return "Outros"
    for d in norm: d["segmento"] = grupo(d.get("segmento"))
    # mix por tese (negócios ganhos; um negócio pode ter várias teses)
    mix = defaultdict(lambda: [0, 0.0]); sem_tese = 0
    for d in norm:
        if d["status"] != "ganho": continue
        ts = [t.strip() for t in (d.get("variante") or "").split(";") if t.strip()]
        if not ts: sem_tese += 1
        for t in ts: mix[t][0] += 1; mix[t][1] += d["valor"] / len(ts)
    M["mix_teses"] = {"top": [(t, n, round(v)) for t, (n, v) in sorted(mix.items(), key=lambda x: -x[1][1])[:8]], "ganhos_sem_tese": sem_tese}
    P = sorted({d["parceiro"] or "Sem parceiro" for d in norm}); segs = sorted({d["segmento"] or "Não informado" for d in norm})
    st = {"aberto": 0, "ganho": 1, "perdido": 2}
    deals = [[P.index(d["parceiro"] or "Sem parceiro"), d["criado"][:7], (d["fechado"][:7] if d["status"] != "aberto" else ""), st[d["status"]],
              d["valor"], None, 0, None, None, None, None, segs.index(d["segmento"] or "Não informado")] for d in norm]
    # semana real (segunda a domingo anteriores à data do relatório)
    from datetime import timedelta
    fim = hoje - timedelta(days=hoje.weekday()); ini = fim - timedelta(days=7); ini0 = ini - timedelta(days=7)
    def sem(a, b):
        c = [d for d in norm if a.isoformat() <= d["criado"] < b.isoformat()]
        g = [d for d in norm if d["status"] == "ganho" and a.isoformat() <= (d["fechado"] or "") < b.isoformat()]
        return {"criados_n": len(c), "criados_rs": round(sum(d["valor"] for d in c)), "ganhos_n": len(g), "ganhos_rs": round(sum(d["valor"] for d in g))}
    w, w0 = sem(ini, fim), sem(ini0, ini)
    # mês até a data (mesmos dias do mês anterior), para não comparar mês parcial com mês cheio
    from datetime import date as _d
    m1 = hoje.replace(day=1); pm_fim = m1 - timedelta(days=1); pm1 = pm_fim.replace(day=1)
    pm_corte = min(pm1.replace(day=min(hoje.day, pm_fim.day)) + timedelta(days=1), m1)
    mtd, pmtd = sem(m1, hoje + timedelta(days=1)), sem(pm1, pm_corte)
    M["mes_ate_hoje"] = {"de": m1.isoformat(), "ate": hoje.isoformat(), **mtd, "mesmo_periodo_mes_anterior": pmtd,
                         "crescimento": {k: growth(mtd[k], pmtd[k]) for k in mtd}}
    M["semana_hubspot"] = {"de": ini.isoformat(), "ate": (fim - timedelta(days=1)).isoformat(), **w, "anterior": w0,
                           "crescimento": {k: growth(w[k], w0[k]) for k in w}}
    ganhos = [d for d in norm if d["status"] == "ganho"]
    com_hon = [d for d in ganhos if d["hContr"] is not None]
    M["cobertura_honorario_hubspot"] = {"ganhos": len(ganhos), "com_honorario": len(com_hon)}
    neg = None
    if com_hon:
        neg = [{"nome": d["nome"], "parceiro": d["parceiro"], "valor": d["valor"], "hContr": d["hContr"], "hParc": d["hParc"] or 0,
                "totalHon": d["valor"] * d["hContr"], "repasse": d["valor"] * d["hContr"] * (d["hParc"] or 0),
                "saldoSave": d["valor"] * d["hContr"] * (1 - (d["hParc"] or 0)), "dataFech": d["fechado"]} for d in com_hon]
        if len(com_hon) < len(ganhos):
            M["alertas"].append(f"Honorário preenchido no HubSpot em só {len(com_hon)} de {len(ganhos)} negócios ganhos: margem calculada sobre essa amostra.")
    else:
        M["pendencias"].append("HubSpot sem % de honorário/parceiro preenchidos: margem ainda vem do S&OE.")
    return {"generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M"), "deals": deals, "partners": P, "segmentos": segs,
            "escopo": "HubSpot: escopo de mapeamento-hubspot.json"}, neg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=date.today().isoformat())
    ap.add_argument("--cockpit", default=COCKPIT_URL)
    a = ap.parse_args()
    hoje = datetime.fromisoformat(a.data).date()
    os.makedirs(os.path.join(BASE, "dados"), exist_ok=True)
    M = {"data_relatorio": a.data, "alertas": [], "pendencias": []}

    # ---------- Fonte: HubSpot direto (principal) ou cockpit (secundária) ----------
    hs = carregar_hubspot(hoje, M)
    if hs:
        snap, hs_neg = hs
        M["fonte_principal"] = "HubSpot (API v3, leitura direta)"
    else:
        html = fetch(a.cockpit)
        snap = json.loads(re.search(r"const SNAP\s*=\s*(\{.*?\});\s*\n", html, re.S).group(1))
        hs_neg = None
        M["fonte_principal"] = "Cockpit Master (fonte SECUNDÁRIA)"
        M["alertas"].insert(0, "Fonte secundária: sem acesso ao HubSpot nesta execução; números vindos do cockpit publicado.")
    deals, P = snap["deals"], snap["partners"]
    gen = snap["generatedAt"]; idade = (hoje - datetime.fromisoformat(gen[:10]).date()).days
    M["fonte_cockpit"] = {"gerado_em": gen, "idade_dias": idade, "negocios": len(deals), "escopo": snap.get("escopo", "Parceiros Masters (Daniela ∪ roster)")}
    if idade > 3:
        M["alertas"].append(f"Dados desatualizados: {gen} ({idade} dias).")
    ref = hoje.strftime("%Y-%m") if idade <= 3 else gen[:7]   # mês de referência = último mês com dado
    M["mes_referencia"] = ref
    meses = [ym_add(ref, -i) for i in range(12, -1, -1)]
    serie = {m: {"criados_n": 0, "criados_rs": 0.0, "ganhos_n": 0, "ganhos_rs": 0.0, "perdidos_n": 0} for m in meses}
    for d in deals:
        pi, cm, xm, st, v = d[0], d[1], d[2], d[3], d[4] or 0
        if cm in serie: serie[cm]["criados_n"] += 1; serie[cm]["criados_rs"] += v
        if xm in serie and st == 1: serie[xm]["ganhos_n"] += 1; serie[xm]["ganhos_rs"] += v
        if xm in serie and st == 2: serie[xm]["perdidos_n"] += 1
    M["serie_mensal"] = serie
    cur, prev, yoy = serie[ref], serie[ym_add(ref, -1)], serie[ym_add(ref, -12)]
    M["crescimento"] = {k: {"MoM": growth(cur[k], prev[k]), "YoY": growth(cur[k], yoy[k])} for k in ["criados_n", "criados_rs", "ganhos_n", "ganhos_rs"]}
    ano, ano_ant = ref[:4], str(int(ref[:4]) - 1)
    ytd = lambda y, k: sum(1 if k.endswith("_n") else (d[4] or 0) for d in deals
                           if (d[1] if k.startswith("criados") else d[2]) and (d[1] if k.startswith("criados") else d[2])[:4] == y
                           and (d[1] if k.startswith("criados") else d[2])[5:7] <= ref[5:7] and (k.startswith("criados") or d[3] == 1))
    M["crescimento_acumulado_ano"] = {k: growth(ytd(ano, k), ytd(ano_ant, k)) for k in ["criados_n", "criados_rs", "ganhos_n", "ganhos_rs"]}
    ult3 = meses[-3:]
    g3 = sum(serie[m]["ganhos_n"] for m in ult3); l3 = sum(serie[m]["perdidos_n"] for m in ult3)
    M["win_rate_3m"] = round(g3 / (g3 + l3) * 100, 1) if g3 + l3 else None
    M["ticket_valor_3m"] = round(sum(serie[m]["ganhos_rs"] for m in ult3) / g3) if g3 else None
    # concentração e parceiros ativos (12 meses)
    won12 = defaultdict(float); ativos = set()
    for d in deals:
        if d[3] == 1 and d[2] in meses[1:]: won12[P[d[0]]] += d[4] or 0
        if d[1] in ult3: ativos.add(P[d[0]])
    tot = sum(won12.values()) or 1; rank = sorted(won12.items(), key=lambda x: -x[1])
    M["concentracao_12m"] = {"top3_pct": round(sum(v for _, v in rank[:3]) / tot * 100, 1), "top5_pct": round(sum(v for _, v in rank[:5]) / tot * 100, 1),
                             "top5": [(p, round(v)) for p, v in rank[:5]]}
    roster = [p for p in P if not p.startswith("Outros")]
    M["parceiros_ativos_90d"] = {"ativos": len([p for p in ativos if not p.startswith("Outros")]), "carteira": len(roster)}
    abertos = [d for d in deals if d[3] == 0]
    M["pipeline_aberto"] = {"n": len(abertos), "rs": round(sum(d[4] or 0 for d in abertos))}
    seg = snap.get("segmentos", [])
    sem_seg = [d for d in abertos if isinstance(d[11], int) and d[11] < len(seg) and seg[d[11]] == "Não informado"]
    M["qualidade_dados"] = {"abertos_sem_segmento_n": len(sem_seg), "abertos_sem_segmento_rs": round(sum(d[4] or 0 for d in sem_seg))}

    # ---------- Snapshot semanal (para diferença semana a semana) ----------
    agg = {"data": a.data, "gerado_em": gen, "total": len(deals), "ganhos": sum(1 for d in deals if d[3] == 1),
           "ganhos_rs": sum(d[4] or 0 for d in deals if d[3] == 1), "criados_rs": sum(d[4] or 0 for d in deals)}
    if M.get("semana_hubspot"):
        M["semana"] = {"desde": M["semana_hubspot"]["de"], **{k: M["semana_hubspot"][k] for k in ("criados_n", "criados_rs", "ganhos_n", "ganhos_rs")},
                       "nota": "Semana real (datas do HubSpot)."}
    snaps = [] if M.get("semana_hubspot") else sorted(f for f in os.listdir(os.path.join(BASE, "dados")) if f.startswith("agg-") and f < f"agg-{a.data}")
    if snaps:
        pa = json.load(open(os.path.join(BASE, "dados", snaps[-1])))
        if pa["gerado_em"] == gen:
            M["semana"] = {"nota": "Sem dado novo desde o último relatório (mesmo snapshot do cockpit)."}
        else:
            M["semana"] = {"desde": pa["data"], "criados_n": agg["total"] - pa["total"], "criados_rs": round(agg["criados_rs"] - pa["criados_rs"]),
                           "ganhos_n": agg["ganhos"] - pa["ganhos"], "ganhos_rs": round(agg["ganhos_rs"] - pa["ganhos_rs"]),
                           "nota": "Diferença entre snapshots (aproximação: não capta exclusões/reaberturas)."}
    elif not M.get("semana_hubspot"):
        M["semana"] = {"nota": "Primeiro relatório: a comparação semana a semana começa no próximo."}
    json.dump(agg, open(os.path.join(BASE, "dados", f"agg-{a.data}.json"), "w"))

    # ---------- Margem (HubSpot se os campos de honorário estiverem preenchidos; senão S&OE) ----------
    try:
        if hs_neg:
            neg, upd = hs_neg, hoje.isoformat()
            M["fonte_margem_origem"] = "HubSpot"
        else:
            raw = json.loads(fetch(SOE_URL))
            soe = {k: fs_conv(v) for k, v in raw["fields"].items()}
            upd = raw.get("updateTime", "")[:10]
            neg = soe.get("margemNegocios", [])
            M["fonte_margem_origem"] = "S&OE (fonte SECUNDÁRIA)"
        idade_s = (hoje - datetime.fromisoformat(upd).date()).days if upd else None
        M["fonte_margem"] = {"atualizado_em": upd, "idade_dias": idade_s, "negocios": len(neg), "escopo": "Base de margem do S&OE (pipelines Partners)"}
        if idade_s and idade_s > 14:
            M["alertas"].append(f"Base de margem do S&OE sem atualização desde {upd} ({idade_s} dias).")
        anom = []
        for x in neg:
            th = x.get("totalHon") or 0; rp = x.get("repasse") or 0
            if rp > th + 1:
                anom.append({"nome": x.get("nome"), "repasse_registrado": rp, "repasse_recalculado": round(th * (x.get("hParc") or 0), 2)})
                x["repasse"] = th * (x.get("hParc") or 0); x["saldoSave"] = th - x["repasse"]
        if anom:
            M["alertas"].append(f"{len(anom)} negócios com repasse maior que o honorário (% do parceiro acima de 100% ou erro de importação): recalculados como honorário × %parceiro.")
        M["anomalias_margem"] = anom
        alto = [x for x in neg if (x.get("hContr") or 0) > 0.5]
        if alto:
            M["alertas"].append(f"{len(alto)} negócios com honorário acima de 50% do crédito (atípico; provável erro de cadastro): R$ {sum(x.get('saldoSave') or 0 for x in alto)/1e6:.1f} mi de honorário líquido. Validar antes de usar a margem.")
        M["honorario_atipico"] = [{"nome": x.get("nome"), "hContr": x.get("hContr"), "valor": round(x.get("valor") or 0)} for x in alto]
        porm = defaultdict(lambda: {"n": 0, "valor": 0.0, "honorario": 0.0, "repasse": 0.0, "liquido": 0.0})
        for x in neg:
            m = (x.get("dataFech") or "")[:7]
            s = porm[m]; s["n"] += 1; s["valor"] += x.get("valor") or 0; s["honorario"] += x.get("totalHon") or 0
            s["repasse"] += x.get("repasse") or 0; s["liquido"] += x.get("saldoSave") or 0
        M["margem_mensal"] = {m: {k: round(v, 2) for k, v in s.items()} for m, s in sorted(porm.items()) if m}
        tv = sum(s["valor"] for s in porm.values()); th = sum(s["honorario"] for s in porm.values()); tl = sum(s["liquido"] for s in porm.values())
        M["margem_carteira"] = {"negocios": len(neg), "valor": round(tv), "honorario_bruto": round(th), "repasse": round(th - tl), "honorario_liquido": round(tl),
                                "margem_bruta_pct": round(th / tv * 100, 2) if tv else None, "margem_liquida_pct": round(tl / tv * 100, 2) if tv else None,
                                "repasse_pct_do_honorario": round((th - tl) / th * 100, 1) if th else None}
        top = sorted(neg, key=lambda x: -(x.get("saldoSave") or 0))[:10]
        M["margem_top10"] = [{"nome": x.get("nome"), "parceiro": x.get("parceiro"), "valor": round(x.get("valor") or 0), "hContr": x.get("hContr"),
                              "honorario": round(x.get("totalHon") or 0), "hParc": x.get("hParc"), "liquido": round(x.get("saldoSave") or 0),
                              "margem_liq_pct": round((x.get("saldoSave") or 0) / (x.get("valor") or 1) * 100, 2)} for x in top]
    except Exception as e:
        M["alertas"].append(f"Base de margem do S&OE indisponível: {e}")

    # ---------- Lucro e ROI ----------
    pr = load_premissas(); M["pendencias"] += pr["pendencias"]
    mm = M.get("margem_mensal", {})
    ult = sorted(mm)[-3:] if mm else []
    if ult:
        hon = sum(mm[m]["honorario"] for m in ult) / len(ult); liq = sum(mm[m]["liquido"] for m in ult) / len(ult)
        L = {"base": f"média mensal de {ult[0]} a {ult[-1]} (honorário contratado = potencial)", "honorario_bruto_mes": round(hon), "honorario_liquido_mes": round(liq)}
        if pr["custo_mensal"] is not None and pr["carga_tributaria"] is not None:
            imp = hon * pr["carga_tributaria"]; lucro = liq - imp - pr["custo_mensal"]
            L.update({"impostos_mes": round(imp), "custos_mes": round(pr["custo_mensal"]), "lucro_area_mes": round(lucro),
                      "roi_total_potencial": round((hon - pr["custo_mensal"]) / pr["custo_mensal"], 2),
                      "roi_liquido_potencial": round(lucro / pr["custo_mensal"], 2)})
        else:
            L["lucro_area_mes"] = "[PREMISSA PENDENTE: custos e impostos]"
            L["roi_total_potencial"] = L["roi_liquido_potencial"] = "[PREMISSA PENDENTE]"
        L["roi_realizado"] = "[sem dado de caixa: honorário recebido não está em nenhuma fonte]"
        M["lucro_roi"] = L
    # ---------- Lucro antes de impostos e ROI, mês a mês (custos do BI × honorário do HubSpot) ----------
    cm = pr.get("custos_mensais") or {}
    if cm and mm:
        ganhos_mes = {m: v["ganhos_rs"] for m, v in M["serie_mensal"].items()}
        linhas = []
        for m in sorted(cm):
            c = cm[m]; real = c["realizado"] > 0; custo = c["realizado"] if real else c["orcado"]
            hm = mm.get(m, {"valor": 0, "honorario": 0, "liquido": 0})
            cob = hm["valor"] / ganhos_mes[m] if ganhos_mes.get(m) else 0
            est = (lambda v: v / cob if cob else None)
            L2 = {"mes": m, "custo": round(custo), "custo_base": "realizado" if real else "ORÇADO (realizado ainda não lançado)",
                  "ganhos_rs": round(ganhos_mes.get(m, 0)), "cobertura_honorario_pct": round(cob * 100, 1),
                  "amostra": {"honorario_bruto": round(hm["honorario"]), "honorario_liquido": round(hm["liquido"]),
                              "lucro_antes_impostos": round(hm["liquido"] - custo),
                              "roi_total": round((hm["honorario"] - custo) / custo, 1) if custo else None,
                              "roi_liquido": round((hm["liquido"] - custo) / custo, 1) if custo else None}}
            if cob:
                hb, hl = est(hm["honorario"]), est(hm["liquido"])
                L2["estimado_100pct"] = {"honorario_bruto": round(hb), "honorario_liquido": round(hl), "lucro_antes_impostos": round(hl - custo),
                                         "roi_total": round((hb - custo) / custo, 1), "roi_liquido": round((hl - custo) / custo, 1)}
            linhas.append(L2)
        tc = sum(x["custo"] for x in linhas); th = sum(x["amostra"]["honorario_bruto"] for x in linhas); tl = sum(x["amostra"]["honorario_liquido"] for x in linhas)
        eb = sum(x.get("estimado_100pct", {}).get("honorario_bruto", 0) for x in linhas); el = sum(x.get("estimado_100pct", {}).get("honorario_liquido", 0) for x in linhas)
        M["lucro_roi_mensal"] = {"modo": "antes de impostos" if pr.get("antes_de_impostos") else "com impostos", "meses": linhas,
                                 "total": {"custo": tc, "amostra": {"honorario_bruto": th, "honorario_liquido": tl, "lucro_antes_impostos": tl - tc,
                                                                    "roi_total": round((th - tc) / tc, 1), "roi_liquido": round((tl - tc) / tc, 1)},
                                           "estimado_100pct": {"honorario_bruto": eb, "honorario_liquido": el, "lucro_antes_impostos": el - tc,
                                                               "roi_total": round((eb - tc) / tc, 1), "roi_liquido": round((el - tc) / tc, 1)}},
                                 "ressalvas": ["Honorário CONTRATADO (potencial), não recebido: sem dado de caixa no HubSpot.",
                                               "Custos só da área Partners (BI do Luis): não incluem Técnico Tributário, Jurídico, Contratos, Pós-venda nem rateios.",
                                               "'Estimado 100%' aplica a margem dos negócios com honorário preenchido aos demais ganhos do mês."]}
        L = M.get("lucro_roi", {}); ul = M["lucro_roi_mensal"]["total"]
        L.update({"base": f"{linhas[0]['mes']} a {linhas[-1]['mes']}, antes de impostos", "custos_mes": round(tc / len(linhas)),
                  "honorario_bruto_mes": round(th / len(linhas)), "honorario_liquido_mes": round(tl / len(linhas)),
                  "impostos_mes": "não considerado (antes de impostos)", "lucro_area_mes": round((tl - tc) / len(linhas)),
                  "roi_total_potencial": ul["amostra"]["roi_total"], "roi_liquido_potencial": ul["amostra"]["roi_liquido"]})
        M["lucro_roi"] = L
    M["pendencias"].append("Recebimentos (caixa): nenhuma fonte com honorário efetivamente recebido. Necessário para o ROI realizado e o backlog.")
    if M.get("mix_teses"):
        M["pendencias"].append(f"Tese não registrada em {M['mix_teses']['ganhos_sem_tese']} negócios ganhos (campo 'Teses tributárias aplicadas'). A variante A/B/C ainda não é um campo próprio.")
    else:
        M["pendencias"].append("Mix por variante (A/B/C): campo inexistente no HubSpot/S&OE.")

    out = os.path.join(BASE, "dados", f"metricas-{a.data}.json")
    json.dump(M, open(out, "w"), ensure_ascii=False, indent=1, default=str)
    print(out)


if __name__ == "__main__":
    main()
