#!/usr/bin/env python3
"""Previsibilidade (Resultados com Pós-venda e Tributário) · registro/gestao/previsao-<data>.json

Contrato: infra/gestao-schema.md, seção 2. Tudo aqui é estimativa com premissa escrita; nada promete valor, prazo ou êxito.

Fontes (só leitura):
  departamentos/resultados/dados/hubspot-<data>.json   download do HubSpot (hubspot_fonte.py), escopo e regra do café de mapeamento-hubspot.json
  celulas/geovana/pareceres/resumos.json                período de apuração e data de análise por negócio (decadência)
  celulas/geovana/recuperador/fila-<data>.json          fila do Recuperador (decadência da fila)
  docs/lancamento-2026/janelas.json                     janelas de receita (base em clientes); o R$ sai do HubSpot pelo mesmo perfil

Métodos:
  Cenários   realizado no mês + pipeline aberto por safra (conversão real por safra de criação, não a probabilidade da etapa;
             curva de dias até o ganho dos ganhos de 2026; negócio parado acima de 2 ciclos vale metade; sazonalidade de nov/dez
             medida nos anos anteriores do download) + negócios que ainda vão ser criados (média móvel de 4 semanas, ticket, win rate).
  Caixa      para cada ganho, honorário líquido Save (crédito × % honorário × (1 − % parceiro)) e o mês provável do recebimento pelo
             prazo típico da variante: PER (Lei 11.457/2007, art. 24: 360 dias para decidir), compensação/conta gráfica em parcelas,
             judicial só depois do trânsito (CTN, art. 170-A). O campo `recebido` está vazio em 100% dos negócios: confiança baixa.
  Decadência cada mês que passa, a competência mais antiga da janela de 5 anos sai (CTN, art. 168; Decreto 20.910/1932). Crédito por
             competência = crédito ÷ meses analisados no parecer; sem parecer, estima pela data de fechamento (confiança baixa).

Uso:
  python3 previsao_gestao.py                 # data de hoje
  python3 previsao_gestao.py --data 2026-10-26
  python3 previsao_gestao.py --data 2026-10-26 --saida /caminho/previsao.json
"""
import argparse, bisect, glob, json, os, re, statistics as st
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

H = os.path.expanduser
AP = H("~/agentes-partners")
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DADOS = os.path.join(AP, "departamentos/resultados/dados")
MAPA = os.path.join(AP, "departamentos/resultados/mapeamento-hubspot.json")
PARECERES = os.path.join(AP, "celulas/geovana/pareceres/resumos.json")
FILA_DIR = os.path.join(AP, "celulas/geovana/recuperador")
OUT_DIR = os.path.join(AP, "registro/gestao")
# Meta D111 (Luis, 26/10/2026): crédito de contrato fechado (ganho), mensal 75/100/75 = R$ 250 mi no Q4 (substitui D64 e D106)
METAS_MES = {"2026-10": ("outubro", 75_000_000), "2026-11": ("novembro", 100_000_000), "2026-12": ("dezembro", 75_000_000)}
META_Q4 = sum(v for _, v in METAS_MES.values())
FERIADOS = {date(2026, 10, 12), date(2026, 11, 2), date(2026, 11, 20), date(2026, 12, 25)}
N_SIM = 20_000  # simulações de Monte Carlo para a probabilidade de cada mês

# ---------------------------------------------------------------- premissas (todas aparecem no JSON)
PREMISSAS = {
    "hContr_padrao": None,      # preenchido com o honorário efetivo ponderado dos ganhos dos últimos 4 meses com % registrado
    "hParc_padrao": None,       # idem para o repasse
    "hContr_teto_caixa": 0.30,  # honorário acima de 50% do crédito é atípico (alerta do calc_semana): no caixa entra com teto de 30%
    "ciclo_estoque_x": 2,       # parado acima de 2 × ciclo mediano sem atividade: probabilidade pela metade
    "sazonal_fechamento": {"conservador": None, "base": None, "meta": 1.0},   # medido em nov/dez dos anos anteriores
    "sazonal_criacao": {"conservador": {"11": 0.70, "12": 0.45}, "base": {"11": 0.80, "12": 0.60}, "meta": {"11": 1.0, "12": 1.0}},
    "glosa": {"conservador": 0.20, "base": 0.0, "meta": 0.0},
    "prazos_caixa_dias": {  # Pós-venda (ressarcimento-e-prazos.md, compensacao-de-oficio-e-recebimento.md)
        "base": {"per_protocolo": 90, "per_decisao": 360, "per_ordem_bancaria": 45, "per_parcelas": 4,
                 "comp_inicio": 120, "comp_parcelas": 12, "jud_inicio": 730, "jud_parcelas": 12},
        "conservador": {"per_protocolo": 150, "per_decisao": 540, "per_ordem_bancaria": 60, "per_parcelas": 6,
                        "comp_inicio": 180, "comp_parcelas": 18, "jud_inicio": 1095, "jud_parcelas": 12}},
    "glosa_caixa": {"base": {"per": 0.0, "comp": 0.0, "jud": 0.0}, "conservador": {"per": 0.25, "comp": 0.15, "jud": 0.30}},
    "mix_sem_tese": None,       # proporção A (PER) × compensação aplicada aos ganhos sem tese registrada, medida nos ganhos com tese
}


def ym(d): return d[:7]
def add_m(y, m, k):
    t = (y * 12 + m - 1) + k; return t // 12, t % 12 + 1
def ym_str(y, m): return f"{y:04d}-{m:02d}"
def dt(s):
    try: return date.fromisoformat(s[:10])
    except Exception: return None
def iso_week(d): y, w, _ = d.isocalendar(); return f"{y}-W{w:02d}"


def carregar(data):
    arqs = sorted(glob.glob(os.path.join(DADOS, "hubspot-*.json")))
    arqs = [a for a in arqs if os.path.basename(a)[8:18] <= data] or arqs
    arq = arqs[-1]; J = json.load(open(arq))
    N = J["negocios"]; fonte = f"hubspot {os.path.basename(arq)[8:18]} {J.get('baixado_em', '')[11:16]}".strip()
    regras = json.load(open(MAPA)).get("regras", {}) if os.path.exists(MAPA) else {}
    corte = regras.get("excluir_cafe_desde")
    if corte:  # regra do Luis (20/08/2026): café fora da meta a partir de abr/2026
        kw = regras.get("cafe_palavras", []); cn = {c.lstrip("0") for c in regras.get("cafe_cnae", [])}
        def cafe(d):
            t = f"{d.get('nome') or ''} {d.get('segmento') or ''}".lower()
            return any(k in t for k in kw) or str(d.get("cnae") or "").lstrip("0") in cn
        ref = lambda d: (d["fechado"] if d["status"] != "aberto" else d["criado"])[:7]
        N = [d for d in N if not (cafe(d) and ref(d) >= corte)]
    return N, fonte


def ok_data(d):  # importações regravaram a criação: ganho "fechado antes de criado" não entra em taxa nem em ciclo
    return not (d["status"] != "aberto" and d["fechado"] and d["criado"] and d["fechado"] < d["criado"])


def tipo_tese(d):
    t = (d.get("variante") or "").lower()
    if not t: return "sem"
    if "(jud)" in t or "(msc)" in t: return "jud"
    if "aquisi" in t or "insumo" in t or "diesel" in t: return "per"     # crédito escritural: ressarcimento por PER (variante A/B)
    return "comp"                                                          # exclusões, verbas: compensação / conta gráfica


def dias_uteis(a, b):
    n, d = 0, a
    while d <= b:
        if d.weekday() < 5 and d not in FERIADOS: n += 1
        d += timedelta(days=1)
    return n


def previsao_mensal(hoje, data, N, abertos, cen, c_deal, S, ciclos, esperado_novos, gt, ticket_med, ticket_apar, conv_pool, cria_sem, real, liq_fator, h_q4):
    """Cenários por mês contra 75/100/75 (D111), probabilidade de cada mês por Monte Carlo e o que novembro precisa para recuperar outubro.
    Mesma base do modelo do trimestre; o que muda: a sazonalidade de nov/dez só vale para nov/dez (outubro com 1,0) e o estoque fora da curva
    (P = 25% até 31/12) se distribui pelos dias de cada mês. Estimativa com premissa escrita; não é promessa."""
    import numpy as np
    meses = list(METAS_MES)
    fins = {m: date(int(m[:4]), int(m[5:]) % 12 + 1, 1) - timedelta(days=1) if m[5:] != "12" else date(int(m[:4]), 12, 31) for m in meses}
    hs = [max((fins[m] - hoje).days, 0) for m in meses]
    # realizado por mês: volume limpo do pacote do mesmo dia, se houver (duplicidade de alta confiança fora); senão bruto
    pac = os.path.join(OUT_DIR, f"pacote-{data}.json"); real_m = {m: 0.0 for m in meses}; fonte_real = "bruto (HubSpot; pacote do dia ausente)"
    try:
        for x in json.load(open(pac))["meta"]["meses"]: real_m[x["mes"]] = float(x["realizado_rs"])
        fonte_real = f"volume limpo do pacote-{data}.json"
    except Exception:
        for d in real: real_m[d["fechado"][:7]] = real_m.get(d["fechado"][:7], 0) + d["valor"]
    def pf(idade, h):  # P(fechar até h | aberto, vai ganhar); estoque fora da curva: 25% até 31/12, distribuído pelos dias
        sa = S(idade)
        if sa < 0.03 or len(ciclos) < 15: return 0.25 * min(h, h_q4) / h_q4 if h_q4 else 0.25
        return (sa - S(idade + h)) / sa
    saz_cen = {"conservador": PREMISSAS["sazonal_fechamento"]["conservador"], "base": PREMISSAS["sazonal_fechamento"]["base"], "esforco": 1.0}
    modelo = {"conservador": "conservador", "base": "base", "esforco": "meta"}
    vals = np.array([d["valor"] for d in abertos], dtype=float)
    trim = np.array(sorted(gt)[:max(1, int(len(gt) * .95))], dtype=float)  # tickets dos ganhos de 6 meses sem os 5% maiores
    rng = np.random.default_rng(20261026)
    R = {}
    for k, mod in modelo.items():
        P = np.zeros((len(abertos), 3))
        for i, d in enumerate(abertos):
            c = c_deal(mod, d); idade = (hoje - dt(d["criado"])).days; cum = [pf(idade, h) for h in hs]
            inc = [cum[0], cum[1] - cum[0], cum[2] - cum[1]]
            P[i] = [c * inc[0], c * inc[1] * saz_cen[k], c * inc[2] * saz_cen[k]]
        esp_ab = P.T @ vals
        nov_cum, nov_n = [], []
        for m in meses:
            t, _ = esperado_novos(mod, fins[m]) if fins[m] > hoje else (0.0, 0); nov_cum.append(t); nov_n.append(esperado_novos.ganhos_n if fins[m] > hoje else 0.0)
        esp_nov = [nov_cum[0], nov_cum[1] - nov_cum[0], nov_cum[2] - nov_cum[1]]; lam = [nov_n[0], nov_n[1] - nov_n[0], nov_n[2] - nov_n[1]]
        # Monte Carlo: cada aberto ganha no máximo uma vez (out, nov ou dez); novos ganhos ~ Poisson com ticket sorteado do histórico
        U = rng.random((N_SIM, len(abertos))); C = np.cumsum(P, axis=1)
        sim = np.zeros((N_SIM, 3))
        for j in range(3):
            lo = C[:, j - 1] if j else 0.0
            sim[:, j] = ((U >= lo) & (U < C[:, j])).astype(float) @ vals
        esc_tk = (ticket_med / ticket_apar) if k == "conservador" and ticket_apar else 1.0
        for j in range(3):
            n_g = rng.poisson(max(lam[j], 0), N_SIM); mx = int(n_g.max()) if len(n_g) else 0
            if mx:
                tk = rng.choice(trim, size=(N_SIM, mx)) * esc_tk
                sim[:, j] += (tk * (np.arange(mx) < n_g[:, None])).sum(axis=1)
        R[k] = {"esp_ab": esp_ab, "esp_nov": esp_nov, "sim": sim, "lam": lam}
    out_meses = []
    for j, m in enumerate(meses):
        nome, meta = METAS_MES[m]; ini = date(int(m[:4]), int(m[5:]), 1)
        linha = {"mes": m, "nome": nome, "meta_rs": meta, "realizado_ate_hoje_rs": int(real_m[m]), "dias_uteis": dias_uteis(ini, fins[m]),
                 "dias_uteis_restantes": dias_uteis(max(ini, hoje + timedelta(days=1)), fins[m]), "cenarios": {}}
        for k in modelo:
            e = real_m[m] + R[k]["esp_ab"][j] + R[k]["esp_nov"][j]; tot = real_m[m] + R[k]["sim"][:, j]
            linha["cenarios"][k] = {"esperado_rs": int(e), "pct_da_meta": round(100 * e / meta, 1), "gap_rs": int(meta - e),
                                   "decomposicao_rs": {"realizado": int(real_m[m]), "pipeline_aberto": int(R[k]["esp_ab"][j]), "negocios_novos": int(R[k]["esp_nov"][j])},
                                   "faixa_p10_p90_rs": [int(np.percentile(tot, 10)), int(np.percentile(tot, 90))],
                                   "probabilidade_meta_pct": round(100 * float((tot >= meta).mean()), 1)}
        out_meses.append(linha)
    total = {"meta_rs": META_Q4, "realizado_ate_hoje_rs": int(sum(real_m.values())), "cenarios": {}}
    for k in modelo:
        tot = sum(real_m.values()) + R[k]["sim"].sum(axis=1); e = sum(x["cenarios"][k]["esperado_rs"] for x in out_meses)
        out_acum = sum(real_m[m] for m in meses[:2]) + R[k]["sim"][:, :2].sum(axis=1)
        total["cenarios"][k] = {"esperado_rs": int(e), "pct_da_meta": round(100 * e / META_Q4, 1), "gap_rs": int(META_Q4 - e), "liquido_estimado_rs": int(e * liq_fator),
                                "faixa_p10_p90_rs": [int(np.percentile(tot, 10)), int(np.percentile(tot, 90))], "probabilidade_meta_pct": round(100 * float((tot >= META_Q4).mean()), 1),
                                "probabilidade_out_nov_175mi_pct": round(100 * float((out_acum >= 175_000_000).mean()), 1)}
    # o que novembro precisaria para recuperar o gap de outubro (base)
    out_b = out_meses[0]["cenarios"]["base"]["esperado_rs"]; gap_out = max(METAS_MES["2026-10"][1] - out_b, 0)
    nov_alvo = METAS_MES["2026-11"][1] + gap_out; du_nov = out_meses[1]["dias_uteis"]; sem_nov = du_nov / 5
    out_ini = date(hoje.year, 10, 1); sem_out = max(dias_uteis(out_ini, hoje), 1) / 5
    g_out = [d for d in real if d["fechado"][:7] == "2026-10"]; gps = len(g_out) / sem_out; tk_out = (sum(d["valor"] for d in g_out) / len(g_out)) if g_out else ticket_apar
    nov_b = out_meses[1]["cenarios"]["base"]["esperado_rs"]; aberto_rs = float(vals.sum())
    precisa = {"gap_outubro_base_rs": int(gap_out), "novembro_alvo_rs": int(nov_alvo), "novembro_base_rs": int(nov_b), "distancia_rs": int(nov_alvo - nov_b),
               "semanas_uteis_novembro": round(sem_nov, 1),
               "ganhos_por_semana_necessarios_ticket_aparado": round(nov_alvo / ticket_apar / sem_nov, 1), "ticket_aparado_rs": int(ticket_apar),
               "ganhos_por_semana_outubro": round(gps, 1), "ticket_medio_outubro_rs": int(tk_out),
               "ticket_necessario_no_ritmo_de_outubro_rs": int(nov_alvo / (gps * sem_nov)) if gps else None,
               "conversao_do_pipeline_aberto_necessaria_pct": round(100 * nov_alvo / aberto_rs, 1) if aberto_rs else None, "conversao_pool_pct": round(conv_pool * 100, 1),
               "pipeline_maduro_necessario_rs": int(nov_alvo / conv_pool) if conv_pool else None, "pipeline_aberto_rs": int(aberto_rs),
               "leitura": []}
    precisa["leitura"] = [
        f"Outubro fecha perto de R$ {out_b/1e6:.1f} mi no cenário base: gap de R$ {gap_out/1e6:.1f} mi. Para recuperá-lo em novembro, o mês precisaria de R$ {nov_alvo/1e6:.1f} mi (meta R$ 100 mi + gap); o base de novembro é R$ {nov_b/1e6:.1f} mi.",
        f"Em ganhos: com o ticket aparado de R$ {ticket_apar/1e3:.0f} mil, {nov_alvo/ticket_apar/sem_nov:.0f} ganhos por semana em {sem_nov:.1f} semanas úteis, contra {gps:.1f}/semana em outubro (ticket médio de outubro R$ {tk_out/1e3:.0f} mil).",
        f"Em ticket: mantendo {gps:.1f} ganhos/semana, o ticket médio teria de ser R$ {(nov_alvo / (gps * sem_nov) if gps else 0)/1e6:.1f} mi por ganho, {(nov_alvo / (gps * sem_nov) if gps else 0)/ticket_apar:.0f} vezes o ticket aparado de 6 meses.",
        f"Só a meta de novembro (R$ 100 mi, sem recuperar outubro) já pede {100e6/ticket_apar/sem_nov:.0f} ganhos por semana no ticket aparado, ou {100e6/aberto_rs*100:.0f}% do pipeline aberto com valor fechando no mês.",
        f"Em conversão: R$ {nov_alvo/1e6:.0f} mi equivalem a {100*nov_alvo/aberto_rs:.0f}% de todo o pipeline aberto com valor (R$ {aberto_rs/1e6:.1f} mi); com a conversão real de {conv_pool*100:.0f}%, seria preciso R$ {nov_alvo/conv_pool/1e6:.0f} mi de pipeline maduro decidindo em novembro.",
        "Sem promessa: o que mais aproxima novembro são entradas grandes já identificadas (contratos enviados, diagnósticos de alto crédito) e dar valor aos abertos sem valor; ver `alavancas`. Nenhum desses números é compromisso de resultado.",
    ]
    return {"meses": out_meses, "total": total, "novembro_precisa": precisa,
            "metodo": [f"Realizado por mês: {fonte_real}.",
                       "Cenários: mesmo modelo do trimestre (conversão por safra, curva de ciclo, parados pela metade, sazonalidade medida de nov/dez), separado por mês pela data provável de fechamento; a queda sazonal só vale para nov/dez. Esforço = conversão >= pool, parados cheios, sem queda sazonal.",
                       f"Probabilidade: {N_SIM:,} simulações; cada aberto ganha no máximo uma vez, no mês sorteado pela curva; novos ganhos por Poisson com ticket sorteado dos ganhos de 6 meses (sem os 5% maiores; conservador escala para o ticket mediano). Negócios tratados como independentes: a faixa real é mais larga (Masters grandes fecham em bloco).".replace(",", "."),
                       "Estimativa com premissa escrita. Nada aqui promete valor, prazo ou êxito."],
            "confianca": "media"}


def main(data, saida):
    hoje = dt(data); N, fonte = carregar(data)
    fim_q4 = date(hoje.year, 12, 31); fim_jan = date(hoje.year + 1, 1, 31)
    h_q4 = (fim_q4 - hoje).days; h_jan = (fim_jan - hoje).days
    sem_rest = h_q4 / 7

    # ------------------------------------------------------------ honorário efetivo
    ini4 = ym_str(*add_m(hoje.year, hoje.month, -3))
    g4 = [d for d in N if d["status"] == "ganho" and d["fechado"][:7] >= ini4 and d.get("hContr") and 0 < d["hContr"] <= 0.5 and d["valor"] > 0]
    hC = sum(d["valor"] * d["hContr"] for d in g4) / sum(d["valor"] for d in g4) if g4 else 0.233
    hP = sum(d["valor"] * d["hContr"] * (d["hParc"] or 0) for d in g4) / sum(d["valor"] * d["hContr"] for d in g4) if g4 else 0.364
    PREMISSAS["hContr_padrao"] = round(hC, 4); PREMISSAS["hParc_padrao"] = round(hP, 4)
    liq_fator = hC * (1 - hP)
    def liquido(d, teto=None):
        hc = d.get("hContr") if d.get("hContr") else hC
        if teto and hc > 0.5: hc = teto
        hp = d.get("hParc") if d.get("hParc") is not None else hP
        if hp > 1: hp = hP
        return d["valor"] * hc * (1 - hp)

    # ------------------------------------------------------------ ciclo e curva de sobrevivência (ganhos de 2026, sem importados)
    ciclos = sorted((dt(d["fechado"]) - dt(d["criado"])).days for d in N if d["status"] == "ganho" and ok_data(d) and d["criado"] and d["fechado"] >= f"{hoje.year}-01-01")
    ciclo_med = st.median(ciclos) if ciclos else 28
    def S(t):  # fração dos ganhos que levou mais de t dias
        return 1 - bisect.bisect_right(ciclos, t) / len(ciclos) if ciclos else 0.5
    def p_fecha(idade, h):  # P(fechar em até h dias | ainda aberto com `idade` dias), dado que vai ganhar
        sa = S(idade)
        if sa < 0.03 or len(ciclos) < 15: return 0.25  # fora da curva observada: estoque
        return (sa - S(idade + h)) / sa

    # ------------------------------------------------------------ conversão real por safra (mês de criação)
    saf = defaultdict(Counter); safv = defaultdict(lambda: defaultdict(float))
    for d in N:
        if not d["criado"] or not ok_data(d): continue
        s = ym(d["criado"]); saf[s][d["status"]] += 1; safv[s][d["status"]] += d["valor"]
    def conv(s):
        c = saf[s]; f = c["ganho"] + c["perdido"]
        return (c["ganho"] / f) if f else None, f
    maduras = [s for s in sorted(saf) if s < ym_str(*add_m(hoje.year, hoje.month, -2)) and s >= ym_str(*add_m(hoje.year, hoje.month, -9))]
    pool_g = sum(saf[s]["ganho"] for s in maduras); pool_f = sum(saf[s]["ganho"] + saf[s]["perdido"] for s in maduras)
    conv_pool = pool_g / pool_f if pool_f else 0.28
    conv_pior = min((conv(s)[0] for s in maduras if conv(s)[1] >= 30), default=conv_pool)

    # ------------------------------------------------------------ sazonalidade de nov/dez (ganhos por mês dos anos anteriores)
    gm = Counter(ym(d["fechado"]) for d in N if d["status"] == "ganho" and d["fechado"])
    fatores = []
    for y in range(2024, hoje.year):
        base = (gm[f"{y}-08"] + gm[f"{y}-09"] + gm[f"{y}-10"]) / 3
        if base: fatores.append(((gm[f"{y}-11"] + gm[f"{y}-12"]) / 2) / base)
    saz_cons = round(min(fatores), 2) if fatores else 0.45
    saz_base = round(sum(fatores) / len(fatores), 2) if fatores else 0.55
    saz_base = max(saz_base, saz_cons)
    PREMISSAS["sazonal_fechamento"]["conservador"] = saz_cons; PREMISSAS["sazonal_fechamento"]["base"] = saz_base
    PREMISSAS["sazonal_fechamento"]["_medido"] = {str(2024 + i): round(f, 2) for i, f in enumerate(fatores)}

    # ------------------------------------------------------------ realizado no mês/trimestre
    tri_ini = f"{hoje.year}-10-01"
    real = [d for d in N if d["status"] == "ganho" and tri_ini <= d["fechado"] <= data]
    real_rs = sum(d["valor"] for d in real); real_liq = sum(liquido(d, PREMISSAS["hContr_teto_caixa"]) for d in real)

    # ------------------------------------------------------------ pipeline aberto por safra e por cenário
    abertos = [d for d in N if d["status"] == "aberto" and d["valor"] > 0]
    sem_valor = sum(1 for d in N if d["status"] == "aberto" and not d["valor"])
    def c_deal(cen, d, parado_fator=0.5):  # conversão do negócio no cenário (safra, pior safra, parado vale metade)
        c, f = conv(ym(d["criado"])); c = c if (c is not None and f >= 30) else conv_pool
        if cen == "conservador": c = min(c, conv_pior)
        if cen == "meta": c = max(c, conv_pool)
        idade = (hoje - dt(d["criado"])).days; ua = dt((d.get("extras") or {}).get("ultima_atividade") or "")
        parado = idade > PREMISSAS["ciclo_estoque_x"] * ciclo_med and (ua is None or (hoje - ua).days > PREMISSAS["ciclo_estoque_x"] * ciclo_med)
        return c * parado_fator if (parado and cen != "meta") else c
    def esperado_aberto(cen, h, saz=None, parado_fator=0.5, etapa_fixa=None):
        saz = PREMISSAS["sazonal_fechamento"][cen] if saz is None else saz; tot = 0.0; por_safra = defaultdict(float); por_parc = defaultdict(float); por_etapa = defaultdict(float)
        for d in abertos:
            s = ym(d["criado"]); c = c_deal(cen, d, parado_fator); idade = (hoje - dt(d["criado"])).days
            p = c * p_fecha(idade, h) * (saz if cen != "meta" else 1.0)
            if etapa_fixa and d["etapa"] == etapa_fixa[0]: p = etapa_fixa[1]
            v = d["valor"] * p; tot += v; por_safra[s] += v; por_parc[d["parceiro"]] += v; por_etapa[d["etapa"]] += v
        return tot, por_safra, por_parc, por_etapa

    # ------------------------------------------------------------ criação futura
    cria = []
    for w in range(4):
        a = hoje - timedelta(days=7 * (w + 1)); b = hoje - timedelta(days=7 * w)
        cria.append(sum(1 for d in N if d["criado"] and a.isoformat() <= d["criado"] < b.isoformat()))
    cria_sem = sum(cria) / 4
    gt = sorted(d["valor"] for d in N if d["status"] == "ganho" and d["valor"] > 0 and d["fechado"][:7] >= ym_str(*add_m(hoje.year, hoje.month, -5)))
    ticket_med = st.median(gt) if gt else 0; ticket_apar = (sum(gt[:int(len(gt) * .95)]) / int(len(gt) * .95)) if len(gt) > 20 else ticket_med
    def esperado_novos(cen, fim, cria=None):
        tk = {"conservador": ticket_med, "base": ticket_apar, "meta": ticket_apar}[cen]
        c = {"conservador": conv_pior, "base": conv_pool, "meta": conv_pool}[cen]
        tot = 0.0; n = 0.0; d0 = hoje + timedelta(days=1); cria = cria_sem if cria is None else cria; ganhos_n = 0.0
        while d0 <= fim:
            f = PREMISSAS["sazonal_criacao"][cen].get(f"{d0.month:02d}", 1.0)
            n_dia = cria / 7 * f; n += n_dia
            tot += n_dia * tk * c * (1 - S((fim - d0).days))   # só o que fecha dentro do horizonte
            ganhos_n += n_dia * c * (1 - S((fim - d0).days))
            d0 += timedelta(days=1)
        esperado_novos.ganhos_n = ganhos_n
        return tot, n

    cen = {}
    for nome in ("conservador", "base", "meta"):
        ea, ps, pp, pe = esperado_aberto(nome, h_q4); en, nn = esperado_novos(nome, fim_q4)
        ea2, _, _, _ = esperado_aberto(nome, h_jan); en2, _ = esperado_novos(nome, fim_jan)
        glosa = PREMISSAS["glosa"][nome]
        fech = real_rs + ea + en; liq = (real_liq + (ea + en) * liq_fator) * (1 - glosa)
        cen[nome] = {"fechamento_q4_rs": int(fech), "liquido_q4_rs": int(liq),
                     "decomposicao_rs": {"realizado_ate_hoje": int(real_rs), "pipeline_aberto": int(ea), "negocios_novos": int(en)},
                     "ate_31_01_rs": {"fechamento": int(real_rs + ea2 + en2), "liquido": int((real_liq + (ea2 + en2) * liq_fator) * (1 - glosa))},
                     "por_parceiro_rs": {k: int(v) for k, v in sorted(pp.items(), key=lambda x: -x[1])[:6]},
                     "por_etapa_rs": {k: int(v) for k, v in sorted(pe.items(), key=lambda x: -x[1])[:6]},
                     "_por_safra": ps}
    cob = cen["base"]["decomposicao_rs"]["pipeline_aberto"] + cen["base"]["decomposicao_rs"]["negocios_novos"]
    falta = META_Q4 - real_rs
    aberto_rs = sum(d["valor"] for d in abertos)
    prem_comuns = [
        f"Escopo: Área Partners (owner da Daniela + roster), café fora desde abr/2026; {len(abertos)} abertos com valor (R$ {aberto_rs/1e6:.1f} mi) e {sem_valor} sem valor (não entram).",
        f"Conversão real por safra de criação (ganho ÷ fechados, sem importados), não a probabilidade de 40% da etapa: pool das safras maduras = {conv_pool*100:.0f}%; pior safra com 30+ fechados = {conv_pior*100:.0f}%.",
        f"Ciclo: mediana de {ciclo_med:.0f} dias entre criação e ganho (ganhos de {hoje.year}, n={len(ciclos)}); P(fechar até 31/12 | aberto) sai da curva observada por idade do negócio.",
        f"Negócio parado (> {PREMISSAS['ciclo_estoque_x']}× o ciclo sem atividade) vale metade da conversão (método do forecast; não se aplica na meta).",
        f"Sazonalidade de nov/dez medida nos ganhos de {', '.join(PREMISSAS['sazonal_fechamento']['_medido'])} (média mensal de nov e dez ÷ média de ago a out, em número de ganhos): {PREMISSAS['sazonal_fechamento']['_medido']}.",
        f"Criação: média móvel de 4 semanas = {cria_sem:.0f} negócios/semana (R$ chega só no diagnóstico, por isso a contagem manda); ticket mediano R$ {ticket_med/1e3:.0f} mil, média aparada 5% R$ {ticket_apar/1e3:.0f} mil.",
        f"Líquido Save = crédito × honorário efetivo {hC*100:.1f}% × (1 − repasse {hP*100:.1f}%) = {liq_fator*100:.1f}% do crédito (ganhos dos últimos 4 meses com % registrado, n={len(g4)}); honorário acima de 50% entra com teto de 30%.",
        "Variante A (alíquota zero, só via PER) não está separada no HubSpot: cerca de 9 em cada 10 reais com tese registrada são 'PIS/COFINS nas aquisições'. D14 (parcial) manda tratá-la como contingente: o líquido aqui é potencial contratado, não caixa.",
    ]
    cen["conservador"]["premissas"] = prem_comuns + [f"Conservador: pior safra ({conv_pior*100:.0f}%), sazonalidade {saz_cons}, criação a {PREMISSAS['sazonal_criacao']['conservador']}, ticket mediano, glosa de 20% no líquido."]
    cen["base"]["premissas"] = prem_comuns + [f"Base: conversão por safra (pool {conv_pool*100:.0f}%), sazonalidade {saz_base}, criação a {PREMISSAS['sazonal_criacao']['base']}, ticket aparado, sem glosa."]
    wins_need = falta / ticket_apar if ticket_apar else 0
    modelo_meta = cen["meta"]["fechamento_q4_rs"]
    cen["meta"] = {"fechamento_q4_rs": META_Q4, "liquido_q4_rs": int(META_Q4 * liq_fator),
                   "modelo_sem_sazonalidade_rs": modelo_meta, "decomposicao_rs": cen["meta"]["decomposicao_rs"], "ate_31_01_rs": cen["meta"]["ate_31_01_rs"],
                   "o_que_precisa": [
                       f"Faltam R$ {falta/1e6:.1f} mi em {h_q4} dias ({sem_rest:.1f} semanas): R$ {falta/sem_rest/1e6:.1f} mi fechados por semana, contra R$ {real_rs/((hoje-dt(tri_ini)).days/7)/1e6:.1f} mi/semana em outubro.",
                       f"Com ticket aparado de R$ {ticket_apar/1e3:.0f} mil: {wins_need:.0f} ganhos ({wins_need/sem_rest:.0f}/semana) contra {len(real)/((hoje-dt(tri_ini)).days/7):.1f}/semana em outubro.",
                       f"Com win rate de {conv_pool*100:.0f}%: {wins_need/conv_pool:.0f} negócios criados E fechados dentro do trimestre ({wins_need/conv_pool/sem_rest:.0f}/semana, contra {cria_sem:.0f}/semana hoje), ou R$ {falta/conv_pool/1e6:.0f} mi de pipeline novo com ciclo de {ciclo_med:.0f} dias.",
                       f"Converter 100% do pipeline aberto com valor (R$ {aberto_rs/1e6:.1f} mi) até 31/12 ainda deixaria R$ {(falta-aberto_rs)/1e6:.1f} mi faltando: a meta em crédito não é alcançável no Q4 sem entrada atípica; mesmo sem sazonalidade e sem corte de parados, o modelo chega a R$ {modelo_meta/1e6:.1f} mi.",
                       f"Unidade decidida (D111): crédito de contrato fechado, mensal 75/100/75. Em líquido Save, R$ {META_Q4/1e6:.0f} mi de crédito equivalem a cerca de R$ {META_Q4*liq_fator/1e6:.0f} mi ({liq_fator*100:.1f}%). A leitura por mês está em `por_mes`.",
                   ]}

    # ------------------------------------------------------------ por mês (D111): cenários, probabilidade e o que novembro precisa
    por_mes = previsao_mensal(hoje, data, N, abertos, cen, c_deal, S, ciclos, esperado_novos, gt, ticket_med, ticket_apar, conv_pool, cria_sem, real, liq_fator, h_q4)
    cen["esforco"] = {"fechamento_q4_rs": por_mes["total"]["cenarios"]["esforco"]["esperado_rs"], "liquido_q4_rs": int(por_mes["total"]["cenarios"]["esforco"]["esperado_rs"] * liq_fator),
                      "decomposicao_rs": cen["meta"]["decomposicao_rs"], "ate_31_01_rs": cen["meta"]["ate_31_01_rs"],
                      "premissas": prem_comuns + ["Esforço: conversão no mínimo a do pool, parados com conversão cheia, sem queda sazonal de nov/dez no fechamento nem na criação, ticket aparado, sem glosa. É o teto plausível do modelo com o canal de hoje, não promessa."]}

    # ------------------------------------------------------------ pipeline por safra
    pipeline_safra = []
    for s in sorted({ym(d["criado"]) for d in abertos}):
        ab = [d for d in abertos if ym(d["criado"]) == s]; c, f = conv(s)
        pipeline_safra.append({"safra": s, "aberto_rs": int(sum(d["valor"] for d in ab)), "aberto_n": len(ab) + sum(1 for d in N if d["status"] == "aberto" and not d["valor"] and ym(d["criado"]) == s),
                               "conversao_real_pct": round(100 * (c if c is not None else conv_pool), 1), "fechados_n": f, "conversao_fonte": "safra" if (c is not None and f >= 30) else "pool (safra com menos de 30 fechados)",
                               "esperado_rs": int(cen["base"]["_por_safra"].get(s, 0)), "esperado_conservador_rs": int(cen["conservador"]["_por_safra"].get(s, 0)),
                               "esperado_sem_prazo_rs": int(sum(d["valor"] for d in ab) * (c if (c is not None and f >= 30) else conv_pool))})
    for c_ in cen.values(): c_.pop("_por_safra", None)

    # ------------------------------------------------------------ caixa de 13 semanas
    ganhos = [d for d in N if d["status"] == "ganho" and d["valor"] > 0 and d["fechado"]]
    mix = Counter();
    for d in ganhos:
        if d["fechado"][:4] >= str(hoje.year - 1): mix[tipo_tese(d)] += d["valor"]
    tot_mix = mix["per"] + mix["comp"] + mix["jud"]
    PREMISSAS["mix_sem_tese"] = {k: round(mix[k] / tot_mix, 3) for k in ("per", "comp", "jud")} if tot_mix else {"per": .85, "comp": .15, "jud": 0}
    semanas = [iso_week(hoje + timedelta(days=7 * i)) for i in range(13)]
    sem_ini = hoje - timedelta(days=hoje.weekday()); sem_fim = sem_ini + timedelta(days=7 * 13)
    caixa = {s: {"base": 0.0, "conservador": 0.0, "fontes": Counter()} for s in semanas}
    n_est = 0; n_reg = 0
    def lancar(cen, d, tipo, valor_liq):
        P = PREMISSAS["prazos_caixa_dias"][cen]; g = PREMISSAS["glosa_caixa"][cen]; f = dt(d["fechado"])
        if tipo == "per": ini = f + timedelta(days=P["per_protocolo"] + P["per_decisao"] + P["per_ordem_bancaria"]); n = P["per_parcelas"]
        elif tipo == "comp": ini = f + timedelta(days=P["comp_inicio"]); n = P["comp_parcelas"]
        else: ini = f + timedelta(days=P["jud_inicio"]); n = P["jud_parcelas"]
        v = valor_liq * (1 - g[tipo]) / n
        for k in range(n):
            dia = ini + timedelta(days=30 * k)
            if sem_ini <= dia < sem_fim:
                w = iso_week(dia)
                if w in caixa: caixa[w][cen] += v; caixa[w]["fontes"][{"per": "PER", "comp": "compensação/conta gráfica", "jud": "judicial"}[tipo]] += v
    TETO_ATIPICO = 50_000_000
    atipicos = [d for d in ganhos if d["valor"] >= TETO_ATIPICO]
    for d in ganhos:
        if d["valor"] >= TETO_ATIPICO: continue  # crédito acima de R$ 50 mi: café de 2024/2025, duplicidades e importações; validar antes de somar
        if d.get("hContr"): n_reg += 1
        else: n_est += 1
        vl = liquido(d, PREMISSAS["hContr_teto_caixa"]); t = tipo_tese(d)
        partes = {t: 1.0} if t != "sem" else PREMISSAS["mix_sem_tese"]
        for cen_ in ("base", "conservador"):
            for tipo, fr in partes.items():
                if fr: lancar(cen_, d, tipo, vl * fr)
    caixa_13 = [{"semana": s, "entrada_rs_base": int(caixa[s]["base"]), "entrada_rs_conservador": int(caixa[s]["conservador"]),
                 "fonte": " · ".join(f"{k} {int(100*v/max(1,sum(caixa[s]['fontes'].values())))}%" for k, v in caixa[s]["fontes"].most_common()) or "sem lançamento",
                 "confianca": "baixa"} for s in semanas]
    caixa_nota = [f"Nenhum negócio tem `recebido` preenchido (0 de {len(ganhos)}): a curva é modelo de prazo típico, não extrato. Confiança baixa em todas as semanas. Use a forma da curva (quando o dinheiro tende a chegar), não o valor absoluto.",
                  f"{len(atipicos)} ganhos com crédito acima de R$ 50 mi (R$ {sum(d['valor'] for d in atipicos)/1e6:.0f} mi; café de 2024/2025, duplicidades e importações) ficaram fora da curva: líquido potencial de R$ {sum(liquido(d, PREMISSAS['hContr_teto_caixa']) for d in atipicos)/1e6:.1f} mi a validar com o Financeiro antes de somar.",
                  f"Honorário registrado em {n_reg} ganhos; nos outros {n_est} usa-se {hC*100:.1f}% e repasse de {hP*100:.1f}%.",
                  f"Prazos base: PER = fechamento + {PREMISSAS['prazos_caixa_dias']['base']['per_protocolo']} dias (documentos e escrituração) + 360 dias (Lei 11.457/2007, art. 24) + {PREMISSAS['prazos_caixa_dias']['base']['per_ordem_bancaria']} dias de ordem bancária, em {PREMISSAS['prazos_caixa_dias']['base']['per_parcelas']} parcelas mensais (um PER por trimestre); compensação/conta gráfica = fechamento + {PREMISSAS['prazos_caixa_dias']['base']['comp_inicio']} dias em {PREMISSAS['prazos_caixa_dias']['base']['comp_parcelas']} parcelas; judicial só {PREMISSAS['prazos_caixa_dias']['base']['jud_inicio']} dias depois (CTN, art. 170-A).",
                  f"Conservador: protocolo em 150 dias, decisão em 540 (a pré-análise da Save fala em 3 a 6 anos no ressarcimento), glosa de 25% no PER, 15% na compensação e 30% no judicial, parcelas mais longas.",
                  f"Mix aplicado aos ganhos sem tese: {PREMISSAS['mix_sem_tese']} (medido nos ganhos com tese de {hoje.year-1} e {hoje.year}).",
                  "O que corrigiria a curva: fonte de recebimentos do Financeiro (D18) e o controle mestre de PER do Pós-venda (pergunta 8)."]

    # ------------------------------------------------------------ decadência mensal
    PR = json.load(open(PARECERES)) if os.path.exists(PARECERES) else {}
    def periodo(p):
        m = re.findall(r"(\d{2})/(\d{4})", p.get("periodo_apuracao") or "")
        if len(m) >= 2: return (int(m[0][1]), int(m[0][0])), (int(m[-1][1]), int(m[-1][0]))
        return None, None
    meses = [ym_str(*add_m(hoje.year, hoje.month, k)) for k in range(1, 7)]
    dec = {m: {"ganhos": 0.0, "ganhos_n": set(), "fila": 0.0, "fila_n": set(), "ganhos_baixa": 0.0} for m in meses}
    def lancar_dec(chave, pid, valor, ref_data, bucket):
        p = PR.get(str(pid)) or {}; ini, fim = periodo(p); conf_baixa = False
        if not ini:
            r = dt(ref_data) or hoje; fim = add_m(r.year, r.month, -2); ini = add_m(fim[0], fim[1], -59); conf_baixa = True
        n_m = (fim[0] * 12 + fim[1]) - (ini[0] * 12 + ini[1]) + 1
        if n_m <= 0 or not valor: return
        por_comp = valor / n_m
        for m in meses:
            y, mo = int(m[:4]), int(m[5:]); comp = add_m(y, mo, -60)
            if ini <= comp <= fim:
                dec[m][bucket] += por_comp; dec[m][bucket + "_n"].add(chave)
                if conf_baixa and bucket == "ganhos": dec[m]["ganhos_baixa"] += por_comp
    for d in ganhos:
        if d["fechado"][:7] >= ym_str(*add_m(hoje.year, hoje.month, -12)):  # ganhos dos últimos 12 meses: PER pode ainda não estar protocolado; os mais antigos presumem-se pedidos
            lancar_dec(d["id"], d["id"], d["valor"], d["fechado"], "ganhos")
    fila_n = 0; L = []
    xl = sorted(glob.glob(os.path.join(FILA_DIR, "Fila-Recuperador-*.xlsx")))
    if xl:
        try:
            import openpyxl
            ws = openpyxl.load_workbook(xl[-1], read_only=True)["Fila"]; rows = ws.iter_rows(values_only=True); cab = next(rows)
            L = [dict(zip(cab, r)) for r in rows if any(r)]
        except Exception: L = []
    if not L:
        fila_arqs = sorted(glob.glob(os.path.join(FILA_DIR, "fila-*.json")))
        if fila_arqs: F = json.load(open(fila_arqs[-1])); L = next((v for v in F.values() if isinstance(v, list)), [])
    if L:
        for r in L:
            pid = (r.get("link") or "").rstrip("/").split("/")[-1]; v = r.get("valor_no_hubspot") or r.get("crédito mediano dos parecidos") or 0
            fila_n += 1; lancar_dec(pid, pid, float(v), r.get("data_ref") or data, "fila")
    decadencia = [{"mes": m, "credito_que_sai_rs": int(dec[m]["ganhos"] + dec[m]["fila"]), "clientes_n": len(dec[m]["ganhos_n"] | dec[m]["fila_n"]),
                   "ganhos_rs": int(dec[m]["ganhos"]), "ganhos_n": len(dec[m]["ganhos_n"]), "ganhos_estimado_sem_parecer_rs": int(dec[m]["ganhos_baixa"]),
                   "fila_recuperador_rs": int(dec[m]["fila"]), "fila_n": len(dec[m]["fila_n"]),
                   "confianca": "baixa"} for m in meses]
    dec_nota = ["Método (recorrencia.md e sped-evidencia.md): a cada mês a competência mais antiga da janela de 5 anos sai (CTN, art. 168, I; Decreto 20.910/1932, art. 1º). Crédito por competência = crédito do negócio ÷ meses do período analisado no parecer.",
                f"Ganhos: só os fechados nos últimos 12 meses (o PER pode não estar protocolado; os anteriores presumem-se pedidos); pareceres com período por negócio: {sum(1 for d in ganhos if str(d['id']) in PR)} de {len(ganhos)}. Sem parecer, período estimado como 60 meses terminando 2 meses antes do fechamento (confiança baixa).",
                f"Fila do Recuperador: {fila_n} casos da aba Fila, crédito = valor no HubSpot ou mediana dos parecidos (look-alike). Tudo é exposição máxima: vale só para competência ainda não pedida; sem o controle mestre de PER (pergunta 8 do Pós-venda) não há como confirmar. Confiança baixa.",
                "Dezembro de 2026 é a última competência de PIS/COFINS (EC 132/2023, ADCT art. 126, II); a partir de 2027 a recorrência é só retroativa."]

    # ------------------------------------------------------------ janelas de receita
    jan_arq = next((p for p in (os.path.join(RAIZ, "docs/lancamento-2026/janelas.json"), os.path.join(AP, "docs/lancamento-2026/janelas.json")) if os.path.exists(p)), None)
    janelas = []
    if jan_arq:
        JJ = json.load(open(jan_arq)); bs = JJ.get("base_save") or {}
        serv = {41, 42, 43, 52, 53} | set(range(58, 64)) | set(range(68, 76)) | set(range(77, 83)) | set(range(85, 89)) | set(range(90, 97))
        mono = ("4731", "4771", "4530", "4635", "4723", "4772"); dv = lambda c: int(c[:2]) if c[:2].isdigit() else -1
        perf = {"iss": lambda b: dv(b["cnae"]) in serv and "Simples" not in b["regime"],
                "t843": lambda b: (10 <= dv(b["cnae"]) <= 33 or dv(b["cnae"]) == 46) and b["regime"] == "Lucro Real",
                "saldo": lambda b: b["regime"] == "Lucro Real" and dv(b["cnae"]) in (1, 2, 3, 10, 11, 46),
                "estoque381": lambda b: (b["regime"].startswith("Lucro Presumido") and 45 <= dv(b["cnae"]) <= 47) or b["cnae"][:4] in mono,
                "peqvalor": lambda b: b["porte"] in ("Microempresa", "Empresa de Pequeno Porte") and "Simples" not in b["regime"],
                "agro": lambda b: dv(b["cnae"]) in (1, 2, 3), "todos": lambda b: True}
        def perfil(d):
            e = d.get("extras") or {}; return {"cnae": str(d.get("cnae") or ""), "regime": e.get("regime") or "", "porte": str(e.get("porte") or "")}
        rs_perfil = {}
        for k, f in perf.items():
            ab = sum(d["valor"] for d in abertos if f(perfil(d))); g12 = sum(d["valor"] for d in ganhos if f(perfil(d)) and d["fechado"][:7] >= ym_str(*add_m(hoje.year, hoje.month, -12)))
            rs_perfil[k] = (int(ab), int(g12))
        for w in JJ["janelas"]:
            p = w.get("base_perfil"); n = sum((bs.get(p) or {}).values()) if p else 0; ab, g12 = rs_perfil.get(p, (0, 0))
            janelas.append({"janela": w["janela"], "id": w["id"], "prazo": w.get("prazo"), "prazo_texto": w.get("prazo_texto"), "status": w.get("status"),
                            "base_rs": (ab + g12) if p not in ("peqvalor", "agro", None) else None, "base_aberto_rs": ab, "base_ganhos_12m_rs": g12, "clientes_n": n, "area": w.get("area_agentes"),
                            "responsavel": w.get("responsavel"), "proximo_passo": w.get("proximo_passo"),
                            "confianca": "media" if p not in ("peqvalor", "agro", None) else "baixa",
                            "nota": "base_rs = crédito dos abertos + ganhos de 12 meses no perfil (HubSpot, CNAE e regime do cadastro); null quando o perfil depende do porte da Receita (não está no HubSpot). clientes_n vem do janelas.json (raízes por Master, Receita local). Base é tamanho de carteira, não receita."})

    # ------------------------------------------------------------ riscos
    def liq_rs(v): return int(v * liq_fator)
    g24 = [d for d in ganhos if d["fechado"][:7] >= ym_str(*add_m(hoje.year, hoje.month, -24)) and d["valor"] < 50_000_000]
    share_a = PREMISSAS["mix_sem_tese"]["per"]
    backlog_a = sum(d["valor"] * (1 if tipo_tese(d) == "per" else share_a if tipo_tese(d) == "sem" else 0) for d in g24)
    base_pipe = cen["base"]["decomposicao_rs"]["pipeline_aberto"] + cen["base"]["decomposicao_rs"]["negocios_novos"]
    pp = cen["base"]["por_parceiro_rs"]; top_parc = max(pp.items(), key=lambda x: x[1]) if pp else ("", 0)
    g12 = [d for d in ganhos if d["fechado"][:7] >= ym_str(*add_m(hoje.year, hoje.month, -12))]; conc = Counter()
    for d in g12: conc[d["parceiro"]] += d["valor"]
    top12 = conc.most_common(1)[0] if conc else ("", 0); tot12 = sum(conc.values()) or 1
    atip = [d for d in ganhos if (d.get("hContr") or 0) > 0.5]
    atip_dif = sum(d["valor"] * d["hContr"] * (1 - (d["hParc"] or 0)) - d["valor"] * 0.3 * (1 - (d["hParc"] or 0)) for d in atip)
    sem_hon = sum(1 for d in ganhos if not d.get("hContr"))
    sens_hon = sum(d["valor"] for d in g12) * 0.03 * (1 - hP)
    apres = cen["base"]["por_etapa_rs"].get("Apresentação de Diagnóstico", 0)
    iss_n = sum((bs.get("iss") or {}).values()) if jan_arq else 0
    riscos = [
        {"risco": "EREsp 2.215.482 (STJ, 1ª Seção) desfavorável à alíquota zero: PER da variante A indeferido ou retido", "probabilidade": "media",
         "impacto_rs": liq_rs(backlog_a * 0.5 + base_pipe * share_a), "impacto_nota": f"metade do líquido potencial dos ganhos de 24 meses na tese de aquisições, sem os atípicos acima de R$ 50 mi (R$ {liq_rs(backlog_a)/1e6:.1f} mi) mais {share_a*100:.0f}% do esperado do Q4",
         "mitigacao": "Diagnóstico com variante B/C e exclusões separadas (aliquota-zero-per.md, situação 1 a 5); termo de ciência do risco (D22); conservador sem variante A (D14); parecer do advogado ao sair o acórdão", "dono": "Tributário (técnico) com o advogado validador; Luis decide a vitrine", "prazo": "2026-11-30"},
        {"risco": "Modulação do Tema 118 (ISS fora da base) corta o retroativo de quem não tinha ação", "probabilidade": "media",
         "impacto_rs": liq_rs(iss_n * ticket_med), "impacto_nota": f"{iss_n} raízes de serviço na carteira × ticket mediano R$ {ticket_med/1e3:.0f} mil × {liq_fator*100:.1f}% (é o upside que some, não uma perda de carteira)",
         "mitigacao": "Luis decide T07 na vitrine e quem conduz a ação; nota técnica aos Masters antes da ata; nenhum PER/DCOMP antes da manifestação da PGFN", "dono": "Tributário (exclusões) e Jurídico; decisão do Luis", "prazo": "2026-11-10"},
        {"risco": f"Concentração: {top12[0]} = {100*top12[1]/tot12:.0f}% dos ganhos de 12 meses; {top_parc[0]} = {100*top_parc[1]/max(1,cen['base']['decomposicao_rs']['pipeline_aberto']):.0f}% do esperado do pipeline aberto no Q4", "probabilidade": "media",
         "impacto_rs": int(top_parc[1]), "impacto_nota": "crédito esperado do pipeline aberto no Q4 que depende de um único Master no cenário base (D&S tem metade do pipeline aberto em R$)",
         "mitigacao": "Plano de conta e QBR com os 3 Masters seguintes; fila de conversão por Master (D41); ativar os dormentes (Partner Success)", "dono": "Daniela", "prazo": "2026-11-15"},
        {"risco": f"Repasse e honorário atípicos: {len(atip)} ganhos com honorário acima de 50% do crédito; 7 com repasse maior que o honorário", "probabilidade": "alta",
         "impacto_rs": int(atip_dif), "impacto_nota": "diferença de líquido entre o % registrado e um teto de 30%: margem que pode não existir",
         "mitigacao": "Dados valida os 61 cadastros com o Canal (percentual negociado por Master, D64); até lá, teto de 30% em todo cálculo", "dono": "Dados com Operações de Canal", "prazo": "2026-11-05"},
        {"risco": f"Dados sem honorário: {sem_hon} de {len(ganhos)} ganhos sem % registrado; tese ausente em 899 ganhos; variante A/B/C não é campo", "probabilidade": "alta",
         "impacto_rs": int(sens_hon), "impacto_nota": "cada 3 pontos de erro no honorário efetivo mudam o líquido dos ganhos de 12 meses nesse valor",
         "mitigacao": "Campo obrigatório no ganho (D73: ganho só entra com tese, variante e %); mutirão de preenchimento dos 12 últimos meses", "dono": "Dados e Daniela", "prazo": "2026-11-20"},
        {"risco": "Dependência da TI: sem credenciais do Graph e do GLPI nada chega ao time (123 e-mails retidos e 11 chamados parados em 22/10)", "probabilidade": "alta",
         "impacto_rs": int(apres * 0.25), "impacto_nota": "um quarto do esperado das apresentações de diagnóstico paradas, que dependem do mutirão (D70) e dos avisos",
         "mitigacao": "Pedido formal ao TI da Save com prazo; enquanto isso, Daniela aprova os chamados no painel uma vez por dia e o plano do dia sai por WhatsApp", "dono": "TI da Save (pedido pelo depto-ti); Luis cobra", "prazo": "2026-11-05"},
        {"risco": f"Capacidade do Técnico: 47 em diagnóstico sem valor e 189 apresentações (R$ {sum(d['valor'] for d in abertos if d['etapa']=='Apresentação de Diagnóstico')/1e6:.1f} mi) na mesma fila; capacidade semanal não informada (D11)", "probabilidade": "media",
         "impacto_rs": int(apres * 0.5), "impacto_nota": "metade do esperado da etapa de apresentação escorrega para 2027 se a fila não couber na capacidade",
         "mitigacao": "Fila ordenada pelo líquido potencial (D44) dentro da capacidade; tetos de horas dos produtos novos (D33/D54); Técnico informa capacidade semanal", "dono": "Geovana com o Técnico", "prazo": "2026-11-15"},
    ]

    # ------------------------------------------------------------ alavancas (efeito sobre o cenário base até 31/12)
    ea_base = cen["base"]["decomposicao_rs"]["pipeline_aberto"]; en_base = cen["base"]["decomposicao_rs"]["negocios_novos"]
    cria_set = max(cria_sem, sum(1 for d in N if d["criado"] and f"{hoje.year}-09-01" <= d["criado"] <= f"{hoje.year}-09-30") / 4.3)
    env_n = sum(1 for d in abertos if d["etapa"] == "Contrato Enviado"); env_rs = sum(d["valor"] for d in abertos if d["etapa"] == "Contrato Enviado")
    alav = [
        ("Fechar os contratos enviados", f"{env_n} negócios com contrato enviado (R$ {env_rs/1e6:.1f} mi): se 60% assinarem até 31/12 em vez do que a curva prevê",
         esperado_aberto("base", h_q4, etapa_fixa=("Contrato Enviado", 0.6))[0] - ea_base, "Daniela com os Masters", "2026-11-30"),
        ("Manter em nov/dez o ritmo de fechamento de ago-out", f"sazonalidade neutra (1,0) em vez de {saz_base}: mutirão (D70) e agenda de assinaturas antes do recesso",
         esperado_aberto("base", h_q4, saz=1.0)[0] - ea_base, "Daniela e Geovana", "2026-12-15"),
        ("Destravar os parados", f"negócios acima de 2 ciclos sem atividade voltam a valer a conversão cheia (hoje valem metade); fila por líquido potencial (D44)",
         esperado_aberto("base", h_q4, parado_fator=1.0)[0] - ea_base, "Daniela com o Técnico", "2026-11-15"),
        ("Voltar a criar como em setembro", f"de {cria_sem:.0f} para {cria_set:.0f} negócios/semana (Jenifer e Masters), com a mesma conversão e ticket",
         esperado_novos("base", fim_q4, cria=cria_set)[0] - en_base, "Jenifer e Daniela", "2026-11-10"),
        ("Dar valor aos abertos sem valor", f"{sem_valor} abertos sem crédito estimado (diagnóstico, agendamento): ao ticket mediano e à conversão do pool, metade fechando no prazo",
         sem_valor * ticket_med * conv_pool * 0.5, "Geovana (técnico) e Dados", "2026-11-20"),
    ]
    alavancas = [{"alavanca": a, "como": c, "efeito_credito_rs": int(e), "efeito_liquido_rs": int(e * liq_fator), "dono": dn, "prazo": pz} for a, c, e, dn, pz in sorted(alav, key=lambda x: -x[2])]
    alavancas.append({"alavanca": "Registrar honorário e corrigir repasse", "como": "cada 3 pontos de honorário efetivo (ou de repasse) mudam o líquido dos ganhos de 12 meses", "efeito_credito_rs": 0, "efeito_liquido_rs": int(sens_hon), "dono": "Dados com Operações de Canal", "prazo": "2026-11-20"})

    out = {"data": data, "horizonte_semanas": 13, "fonte": fonte, "gerado_em": datetime.now().strftime("%Y-%m-%d %H:%M"),
           "meta": {"q4_rs": META_Q4, "unidade": "credito_contrato_fechado", "decisao": "D111 (26/10/2026)", "realizado_rs": int(real_rs), "realizado_liquido_rs": int(real_liq), "falta_rs": int(falta), "dias_restantes": h_q4,
                    "cobertura_base_x": round(cob / falta, 2) if falta else None, "leitura_liquido": {"meta_em_liquido_exige_credito_rs": int(META_Q4 / liq_fator), "liquido_se_meta_em_credito_rs": int(META_Q4 * liq_fator)}},
           "cenarios": cen, "por_mes": por_mes, "metodo_resumo": {"conversao_pool_pct": round(conv_pool * 100, 1), "conversao_pior_pct": round(conv_pior * 100, 1), "ciclo_mediano_dias": ciclo_med,
                                               "criacao_semana_mm4": round(cria_sem, 1), "ticket_mediano_rs": int(ticket_med), "ticket_aparado_rs": int(ticket_apar),
                                               "honorario_efetivo_pct": round(hC * 100, 1), "repasse_pct": round(hP * 100, 1), "liquido_fator_pct": round(liq_fator * 100, 1),
                                               "pipeline_aberto_rs": int(aberto_rs), "pipeline_aberto_n": len(abertos), "abertos_sem_valor_n": sem_valor},
           "caixa_13_semanas": caixa_13, "caixa_nota": caixa_nota, "pipeline_por_safra": pipeline_safra,
           "decadencia_mensal": decadencia, "decadencia_nota": dec_nota, "janelas": janelas, "riscos": riscos, "alavancas": alavancas, "premissas": PREMISSAS,
           "confianca": {"cenarios": "media", "caixa": "baixa", "pipeline_por_safra": "media", "decadencia": "baixa", "janelas": "media", "riscos": "media"}}
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    json.dump(out, open(saida + ".tmp", "w", encoding="utf-8"), ensure_ascii=False, indent=1); os.replace(saida + ".tmp", saida)
    print(saida)
    for x in por_mes["meses"] + [dict(por_mes["total"], nome="Q4")]:
        print(f"{x['nome']:9s} meta R$ {x['meta_rs']/1e6:5.0f} mi · " + " · ".join(f"{k} R$ {c['esperado_rs']/1e6:5.1f} mi (P {c['probabilidade_meta_pct']}%)" for k, c in x["cenarios"].items()))
    for k, v in cen.items(): print(f"{k:12s} crédito R$ {v['fechamento_q4_rs']/1e6:7.1f} mi · líquido R$ {v['liquido_q4_rs']/1e6:6.1f} mi · {v['decomposicao_rs']}")
    print("caixa 13 semanas base R$ %.1f mi · conservador R$ %.1f mi" % (sum(c["entrada_rs_base"] for c in caixa_13) / 1e6, sum(c["entrada_rs_conservador"] for c in caixa_13) / 1e6))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--data", default=date.today().isoformat()); ap.add_argument("--saida")
    a = ap.parse_args(); main(a.data, a.saida or os.path.join(OUT_DIR, f"previsao-{a.data}.json"))
