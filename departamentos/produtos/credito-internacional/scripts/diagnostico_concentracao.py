"""Diagnóstico de concentração, dependência de tese e volatilidade do canal Partners (base do 24a).

Uso:  python3 diagnostico_concentracao.py [--data 2026-09-30] [--nomes]
--data: último dia do corte (fim de trimestre). As janelas (12 meses, 4 e 8 trimestres, 24 meses) são derivadas dela.
--nomes: mostra o nome bruto dos indicadores fora do roster. Sem a opção, eles saem por código ("Indicador 1", "Indicador 2"...),
  em ordem decrescente de líquido histórico, para que o JSON e o 24a não exponham nomes de pessoas físicas (LGPD).
Lê o download mais recente do HubSpot (departamentos/resultados/dados/hubspot-*.json), somente leitura.
Grava diagnostico-concentracao.json nesta pasta. Não lê .env, não chama API, não altera nada.

Regras de cálculo (as mesmas do depto-resultados, calc_semana.py):
- Crédito = valor do negócio ganho; honorário bruto = crédito × % de honorário; repasse = honorário × % do parceiro;
  líquido Save = honorário − repasse. Data = data de fechamento.
- % de honorário vazio: usa a mediana do próprio parceiro em todo o histórico ganho (ou a mediana geral); % acima de 50% é tratado como erro
  de cadastro e substituído do mesmo jeito. % do parceiro vazio ou acima de 100%: mediana do parceiro (ou geral).
- Parceiros fora do roster ("Outros") são separados pelo nome bruto (variações de grafia unificadas).
- Tese: família pela 1ª tese do campo "variante"; negócio sem tese fica em "Sem tese registrada". Café pela regra do
  mapeamento-hubspot.json (CNAE e palavras), a mesma que tirou o café das contas desde abr/2026.
"""
import argparse, datetime as DT, json, os, re, statistics, sys
from collections import defaultdict

sys.path.insert(0, os.path.expanduser("~/agentes-partners/lib"))
import partners_dados as PD

AQUI = os.path.dirname(os.path.abspath(__file__))
MASTERS = {"D&S", "AGILE", "G.S.H", "JGM", "EMPRESARIAL CARDOSO", "COSTA e GAUDENCIO", "ASSECONT", "ORTECONTE", "GERSON"}


def parceiro(d):
    p = d.get("parceiro") or ""
    if p in MASTERS: return p
    b = PD.norm(d.get("parceiro_bruto"))
    if not b or re.fullmatch(r"[\d\s.,%]*", b): return "Sem parceiro identificado"
    if "ataliba" in b or "valutare" in b: return "Indicador: Ataliba/Valutare"
    return "Indicador: " + " ".join(w.capitalize() for w in b.split())


def familia(d):
    v = PD.norm(d.get("variante"))
    if not v: return "Sem tese registrada"
    t = v.split(";")[0]
    if "aquisic" in t: return "PIS/COFINS nas aquisições"
    if "sistema s" in t: return "Sistema S"
    if "diesel" in t or "glp" in t: return "Diesel/GLP"
    if "insumo" in t: return "Insumos (PIS/COFINS)"
    if "verba" in t: return "Verbas indenizatórias"
    if "exclus" in t: return "Exclusões da base do PIS/COFINS (ICMS, ISS, própria base)"
    return "Outras teses"


def trimestre(dt):
    return f"{(int(dt[5:7]) - 1) // 3 + 1}T{dt[2:4]}"


def mediana(xs, padrao):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else padrao


def share(vals, k):
    tot = sum(vals) or 1
    return sum(sorted(vals, reverse=True)[:k]) / tot


def hhi(vals):
    tot = sum(vals) or 1
    return sum((v / tot) ** 2 for v in vals)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", default="2026-09-30"); ap.add_argument("--nomes", action="store_true")
    a = ap.parse_args()
    fim = a.data  # último dia considerado (fim de trimestre; padrão: fecha o 3T26)
    F = DT.date.fromisoformat(fim)
    ini12 = (DT.date(F.year - 1, F.month, F.day) + DT.timedelta(days=1)).isoformat()

    def tri_de(y, q):  # (rótulo, início, fim) do trimestre q de y
        ini = DT.date(y, 3 * q - 2, 1); prox = DT.date(y + (q == 4), 1 if q == 4 else 3 * q + 1, 1)
        return (f"{q}T{str(y)[2:]}", ini.isoformat(), (prox - DT.timedelta(days=1)).isoformat())

    def tris_ate(n):  # os n trimestres que terminam no trimestre do corte
        y, q = F.year, (F.month - 1) // 3 + 1; out = []
        for _ in range(n):
            out.append(tri_de(y, q)); q -= 1
            if q == 0: y, q = y - 1, 4
        return out[::-1]
    arq, base = PD.ultimo_download(); R = PD.regras()
    ganhos = [d for d in base["negocios"] if d["status"] == "ganho" and d.get("fechado") and d["fechado"][:10] <= fim]
    for d in ganhos:
        d["_p"] = parceiro(d); d["_f"] = familia(d); d["_cafe"] = PD.e_cafe(d, R); d["_t"] = trimestre(d["fechado"])
        d["_m"] = d["fechado"][:7]; d["_master"] = d["_p"] in MASTERS
    # ---- percentuais: imputação pela mediana do parceiro (cálculo único, sobre toda a base ganha) ----
    hc_ok = lambda x: x is not None and 0 < x <= 0.5
    hp_ok = lambda x: x is not None and 0 <= x <= 1
    med_hc_g = mediana([d["hContr"] for d in ganhos if hc_ok(d["hContr"])], 0.25)
    med_hp_g = mediana([d["hParc"] for d in ganhos if hp_ok(d["hParc"])], 0.30)
    porp = defaultdict(list)
    for d in ganhos: porp[d["_p"]].append(d)
    imput = {"hContr": 0, "hParc": 0}
    for p, ds in porp.items():
        mh = mediana([d["hContr"] for d in ds if hc_ok(d["hContr"])], med_hc_g)
        mp = mediana([d["hParc"] for d in ds if hp_ok(d["hParc"])], med_hp_g)
        for d in ds:
            hc = d["hContr"] if hc_ok(d["hContr"]) else None
            hp = d["hParc"] if hp_ok(d["hParc"]) else None
            if hc is None: hc = mh; d["_imp_hc"] = True
            if hp is None: hp = mp; d["_imp_hp"] = True
            d["_cred"] = d["valor"] or 0; d["_hon"] = d["_cred"] * hc; d["_rep"] = d["_hon"] * hp; d["_liq"] = d["_hon"] - d["_rep"]

    # ---- indicadores fora do roster por código (LGPD), salvo --nomes ----
    if not a.nomes:
        tot = defaultdict(float)
        for d in ganhos:
            if d["_p"].startswith("Indicador: "): tot[d["_p"]] += d["_liq"]
        cod = {p: f"Indicador {i}" for i, p in enumerate(sorted(tot, key=lambda k: (-tot[k], k)), 1)}
        for d in ganhos: d["_p"] = cod.get(d["_p"], d["_p"])

    def janela(ini, fim_):
        return [d for d in ganhos if ini <= d["fechado"][:10] <= fim_]

    def resumo(ds, chave="_p"):
        agg = defaultdict(lambda: {"n": 0, "cred": 0.0, "hon": 0.0, "liq": 0.0, "rep": 0.0})
        for d in ds:
            s = agg[d[chave]]; s["n"] += 1; s["cred"] += d["_cred"]; s["hon"] += d["_hon"]; s["liq"] += d["_liq"]; s["rep"] += d["_rep"]
        return agg

    def conc(ds):
        agg = resumo(ds)
        out = {"ganhos": len(ds), "credito": round(sum(d["_cred"] for d in ds)), "liquido": round(sum(d["_liq"] for d in ds)),
               "honorario": round(sum(d["_hon"] for d in ds)), "parceiros_com_ganho": len(agg)}
        for m in ("cred", "liq"):
            v = [s[m] for s in agg.values()]
            out[m] = {"top1": round(share(v, 1) * 100, 1), "top3": round(share(v, 3) * 100, 1), "top5": round(share(v, 5) * 100, 1),
                      "hhi": round(hhi(v), 3), "parceiros_efetivos": round(1 / hhi(v), 1) if v else 0,
                      "ranking": [(p, round(s[m]), round(s[m] / (sum(v) or 1) * 100, 1)) for p, s in sorted(agg.items(), key=lambda x: -x[1][m])[:6]]}
        # quantos parceiros fazem 80% do líquido
        v = sorted((s["liq"] for s in agg.values()), reverse=True); acc, k = 0, 0
        for x in v:
            acc += x; k += 1
            if acc >= 0.8 * sum(v): break
        out["parceiros_para_80pct_liquido"] = k
        # maior negócio
        if ds:
            top = max(ds, key=lambda d: d["_cred"])
            out["maior_negocio_pct_credito"] = round(top["_cred"] / (out["credito"] or 1) * 100, 1)
            out["maior_negocio_parceiro"] = top["_p"]
            top5 = sorted(ds, key=lambda d: -d["_cred"])[:5]
            out["5_maiores_negocios_pct_credito"] = round(sum(d["_cred"] for d in top5) / (out["credito"] or 1) * 100, 1)
        return out

    J = {"fonte": os.path.basename(arq), "baixado_em": base.get("baixado_em"), "corte": fim,
         "premissas": {"mediana_honorario": med_hc_g, "mediana_parceiro": med_hp_g}}
    j12 = janela(ini12, fim)
    J["imputacao_12m"] = {"ganhos": len(j12), "honorario_imputado": sum(1 for d in j12 if d.get("_imp_hc")),
                          "parceiro_imputado": sum(1 for d in j12 if d.get("_imp_hp"))}
    J["12m"] = conc(j12)
    J["12m_sem_cafe"] = conc([d for d in j12 if not d["_cafe"]])
    J["12m_so_masters"] = conc([d for d in j12 if d["_master"]])
    trims = tris_ate(4)
    J["trimestres"] = {t: conc(janela(i, f)) for t, i, f in trims}
    # histórico longo por ano (crédito e líquido)
    J["anos"] = {y: conc(janela(f"{y}-01-01", min(f"{y}-12-31", fim))) for y in [str(x) for x in range(2023, F.year + 1)]}
    # ---- tese e café ----
    def mix(ds, chave):
        agg = resumo(ds, chave); tc = sum(s["cred"] for s in agg.values()) or 1; tl = sum(s["liq"] for s in agg.values()) or 1
        return [(k, s["n"], round(s["cred"]), round(s["cred"] / tc * 100, 1), round(s["liq"]), round(s["liq"] / tl * 100, 1))
                for k, s in sorted(agg.items(), key=lambda x: -x[1]["liq"])]
    J["tese_12m"] = mix(j12, "_f")
    com_tese = [d for d in j12 if d["_f"] != "Sem tese registrada"]
    J["tese_12m_so_registrada"] = mix(com_tese, "_f")
    for d in ganhos: d["_cafe_s"] = "Café" if d["_cafe"] else "Fora do café"
    J["cafe_12m"] = mix(j12, "_cafe_s")
    J["cafe_trimestres"] = {t: mix(janela(i, f), "_cafe_s") for t, i, f in trims}
    for d in ganhos: d["_prod"] = d["pipeline"]
    J["produto_historico"] = mix(ganhos, "_prod")
    J["produto_12m"] = mix(j12, "_prod")
    J["tese_historico"] = mix(ganhos, "_f")
    # ---- volatilidade mensal (24 meses até o mês do corte) ----
    meses = []
    y, m = F.year - 2, F.month + 1
    if m == 13: y, m = y + 1, 1
    while (y, m) <= (F.year, F.month):
        meses.append(f"{y}-{m:02d}"); m += 1
        if m == 13: y, m = y + 1, 1
    serie = {k: {"n": 0, "cred": 0.0, "liq": 0.0, "liq_sem_cafe": 0.0} for k in meses}
    for d in ganhos:
        if d["_m"] in serie:
            s = serie[d["_m"]]; s["n"] += 1; s["cred"] += d["_cred"]; s["liq"] += d["_liq"]
            if not d["_cafe"]: s["liq_sem_cafe"] += d["_liq"]
    J["serie_mensal"] = {k: {kk: round(vv) for kk, vv in v.items()} for k, v in serie.items()}

    def vol(xs):
        mu = statistics.mean(xs); sd = statistics.pstdev(xs)
        return {"media": round(mu), "desvio": round(sd), "cv": round(sd / mu, 2) if mu else None, "min": round(min(xs)), "max": round(max(xs)),
                "max_sobre_min": round(max(xs) / min(xs), 1) if min(xs) > 0 else None,
                "meses_abaixo_50pct_media": sum(1 for x in xs if x < 0.5 * mu),
                "maior_mes_pct_total": round(max(xs) / (sum(xs) or 1) * 100, 1)}
    u12 = meses[-12:]
    J["volatilidade_12m"] = {"liq": vol([serie[k]["liq"] for k in u12]), "cred": vol([serie[k]["cred"] for k in u12]),
                             "n": vol([serie[k]["n"] for k in u12]), "liq_sem_cafe_abr_set26": vol([serie[k]["liq_sem_cafe"] for k in meses if k >= "2026-04"])}
    J["volatilidade_24m"] = {"liq": vol([serie[k]["liq"] for k in meses])}
    # ---- regularidade por Master: 8 trimestres (4T24 a 3T26) ----
    t8 = [t for t, _, _ in tris_ate(8)]
    porpt = defaultdict(lambda: defaultdict(float)); porpt_sc = defaultdict(lambda: defaultdict(float))
    porp_f = defaultdict(lambda: defaultdict(float))
    for d in ganhos:
        if d["_t"] in t8:
            porpt[d["_p"]][d["_t"]] += d["_liq"]
            if not d["_cafe"]: porpt_sc[d["_p"]][d["_t"]] += d["_liq"]
        if ini12 <= d["fechado"][:10] <= fim:
            porp_f[d["_p"]][d["_f"]] += d["_liq"]
    reg = {}
    for p in sorted(MASTERS | {k for k in porpt if sum(porpt[k].values()) > 0}, key=lambda k: -sum(porpt[k].values())):
        xs = [porpt[p][t] for t in t8]
        if sum(xs) <= 0 and p not in MASTERS: continue
        u4 = xs[-4:]; mu = statistics.mean(u4); sd = statistics.pstdev(u4)
        fam = porp_f[p]; tl = sum(fam.values()) or 1
        fam_reg = {k: v for k, v in fam.items() if k != "Sem tese registrada"}; tr = sum(fam_reg.values()) or 1
        reg[p] = {"liq_trimestres": {t: round(porpt[p][t]) for t in t8}, "liq_sem_cafe_trimestres": {t: round(porpt_sc[p][t]) for t in t8},
                  "trimestres_com_ganho_8": sum(1 for x in xs if x > 0), "trimestres_com_ganho_4": sum(1 for x in u4 if x > 0),
                  "liq_12m": round(sum(u4)), "media_trim_12m": round(mu), "cv_trim_12m": round(sd / mu, 2) if mu else None,
                  "maior_trim_pct_12m": round(max(u4) / (sum(u4) or 1) * 100, 1),
                  "liq_12m_sem_cafe": round(sum(porpt_sc[p][t] for t in t8[-4:])),
                  "teses_12m": {k: round(v) for k, v in sorted(fam.items(), key=lambda x: -x[1])},
                  "maior_tese_pct_registrada": round(max(fam_reg.values()) / tr * 100, 1) if fam_reg else None,
                  "teses_registradas_12m": len(fam_reg),
                  "maior_negocio_pct_liq_12m": round(max([d["_liq"] for d in j12 if d["_p"] == p] or [0]) / (sum(u4) or 1) * 100, 1)}
    J["regularidade"] = reg
    J["trimestres_8"] = t8
    # distribuição do líquido trimestral dos Masters com ganho (para calibrar pisos)
    xs = sorted(v for p in MASTERS for t, v in porpt[p].items() if t in t8[-4:] and v > 0)
    if xs:
        q = statistics.quantiles(xs, n=4) if len(xs) >= 4 else [xs[0]] * 3
        J["dist_liq_trim_masters_12m"] = {"n": len(xs), "p25": round(q[0]), "mediana": round(q[1]), "p75": round(q[2]), "min": round(xs[0]), "max": round(xs[-1])}

    # ---- simulação do mecanismo de sustentação no Programa Partners (sem café, 12 meses) ----
    sc = [d for d in j12 if not d["_cafe"]]
    sim = {}
    for p in sorted(MASTERS):
        ds = [d for d in sc if d["_p"] == p]
        vs = sum(d["_liq"] for d in ds)
        qt = {t: sum(d["_liq"] for d in ds if d["_t"] == t) for t in t8[-4:]}
        fam = defaultdict(float)
        for d in ds:
            if d["_f"] != "Sem tese registrada": fam[d["_f"]] += d["_liq"]
        tr = sum(fam.values())
        sim[p] = {"vs": round(vs), "trimestres": {t: round(v) for t, v in qt.items()},
                  "trim_ge_1mi": sum(1 for v in qt.values() if v >= 1_000_000), "trim_ge_250mil": sum(1 for v in qt.values() if v >= 250_000),
                  "trim_com_ganho": sum(1 for v in qt.values() if v > 0),
                  "maior_tese_pct": round(max(fam.values()) / tr * 100, 1) if tr else None, "teses": len(fam),
                  "tese_registrada_pct_do_vs": round(tr / vs * 100, 1) if vs else None,
                  "maior_negocio_pct": round(max([d["_liq"] for d in ds] or [0]) / (vs or 1) * 100, 1)}
    J["programa_partners_sem_cafe_12m"] = sim
    out = os.path.join(AQUI, "diagnostico-concentracao.json")
    json.dump(J, open(out, "w"), ensure_ascii=False, indent=1)
    print("ok", out)


if __name__ == "__main__":
    main()
