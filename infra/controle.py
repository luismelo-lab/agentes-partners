#!/usr/bin/env python3
"""Controle da Área Partners (Luis, 26/10/2026: informação para decisão com resultado, previsibilidade e CONTROLE).

Lê o pacote (`registro/gestao/pacote-<data>.json`) e a previsão (`previsao-<data>.json`) mais recentes; enquanto não
existirem, calcula o que dá do `departamentos/resultados/dados/metricas-<data>.json`, do painel de Dados
(`departamentos/dados/dados-bi-<data>.json`), dos indicadores do Recuperador, da sentinela das entregas, das avaliações
dos agentes e das demandas da Central, e deixa o resto cinza. Aplica as regras de `infra/controle.json` (tolerâncias
verde/amarelo/vermelho e gatilhos "se X, então ação Y, dono Z, em N dias"), grava
`registro/gestao/controle-<data>.json` com os desvios abertos e manda cada desvio NOVO à caixa de entrada da pessoa
dona (`lib/caixa.py`, prioridade alta, origem "Controle", ação "Abrir gestão"), uma vez por desvio por semana.

  python3 infra/controle.py                 roda para hoje e envia à caixa
  python3 infra/controle.py --sem-caixa     só calcula e grava (sem mensagens)
  python3 infra/controle.py --data 2026-10-26 --resumo   data de referência e resumo em texto

Dono que é pessoa (luis, daniela, jenifer, geovana) recebe na própria caixa. Dono que é agente (controller, gerente-<área>,
arquiteto-agentes) não tem caixa: esses desvios vão numa mensagem única ao Luis e entram na pauta do Conselho de segunda.
Nada aqui altera HubSpot, GLPI ou portal/. Contrato: infra/gestao-schema.md §3.
"""
import argparse, glob, json, os, re, sys
from datetime import date, datetime, timedelta

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # código: este repositório (worktree ou raiz)
AP = os.environ.get("PARTNERS_AP") or os.path.expanduser("~/agentes-partners")  # dados: fora do git
sys.path.insert(0, os.path.join(REPO, "lib"))

GESTAO = os.path.join(AP, "registro", "gestao")
LEDGER = os.path.join(GESTAO, "controle-enviados.jsonl")
ACOES = os.path.join(GESTAO, "acoes.jsonl")
PESSOAS = ("luis", "daniela", "jenifer", "geovana")
FERIADOS = {"2026-11-02", "2026-11-20", "2026-12-25", "2027-01-01", "2026-10-12", "2026-09-07"}
META_Q4_RS = 250_000_000  # D111 (26/10/2026): crédito de contrato fechado, mensal 75/100/75
METAS_MES = {"2026-10": 75_000_000, "2026-11": 100_000_000, "2026-12": 75_000_000}
DATA_SEM_CAIXA_DESDE = date(2026, 9, 28)  # 1º relatório semanal sem fonte de honorário recebido (D18 em 29/09)
STATUS_ORDEM = {"verde": 0, "cinza": 0, "amarelo": 1, "vermelho": 2}


# ---------------------------------------------------------------- utilidades
def _json(p, padrao=None):
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return padrao


def _ultimo(padrao, ate=None):
    """Arquivo mais recente de um padrão com data no nome (<= `ate`, se dado)."""
    xs = []
    for f in glob.glob(padrao):
        m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(f))
        if m and (not ate or m.group(1) <= ate): xs.append((m.group(1), f))
    return max(xs)[1] if xs else None


def dia_util(d):
    return d.weekday() < 5 and d.isoformat() not in FERIADOS


def somar_uteis(d, n):
    while n > 0:
        d += timedelta(days=1)
        if dia_util(d): n -= 1
    return d


def uteis_entre(a, b):
    """Dias úteis em (a, b] (exclui a, inclui b)."""
    n, d = 0, a
    while d < b:
        d += timedelta(days=1)
        if dia_util(d): n += 1
    return n


def semana_iso(d):
    y, w, _ = d.isocalendar(); return f"{y}-W{w:02d}"


def _cmp(op, v, lim):
    return {"<": v < lim, "<=": v <= lim, ">": v > lim, ">=": v >= lim, "==": v == lim}[op]


def _tol(expr, v):
    """Expressão da tolerância (">= 90", "<= 0.7*meta" não é usada aqui) aplicada ao valor."""
    m = re.match(r"\s*(<=|>=|==|<|>)\s*(-?[\d.]+)\s*$", str(expr))
    return bool(m) and _cmp(m.group(1), float(v), float(m.group(2)))


def status_de(tol, v):
    if v is None or tol is None: return "cinza"
    if _tol(tol["verde"], v): return "verde"
    if _tol(tol["amarelo"], v): return "amarelo"
    return "vermelho"


# ---------------------------------------------------------------- fontes
def carregar_fontes(hoje):
    H = hoje.isoformat()
    F = {"pacote": _ultimo(os.path.join(GESTAO, "pacote-*.json"), H), "previsao": _ultimo(os.path.join(GESTAO, "previsao-*.json"), H),
         "metricas": _ultimo(os.path.join(AP, "departamentos/resultados/dados/metricas-*.json"), H),
         "dados_bi": _ultimo(os.path.join(AP, "departamentos/dados/dados-bi-*.json"), H),
         "recuperador": sorted(glob.glob(os.path.join(AP, "celulas/geovana/recuperador/indicadores-*.json"))),
         "entregas": os.path.join(AP, "registro/entregas-faltando.json"),
         "avaliacoes": _ultimo(os.path.join(AP, "registro/avaliacoes/relatorio-*.json"), H),
         "demandas": os.path.join(AP, "registro/demandas.json"),
         "analises": sorted(glob.glob(os.path.join(AP, "registro/analises-????-??-??.json"))),
         "acoes": ACOES, "controles_anteriores": [f for f in sorted(glob.glob(os.path.join(GESTAO, "controle-*.json")))
                                                  if re.search(r"controle-(\d{4}-\d{2}-\d{2})\.json$", f) and f"controle-{H}.json" not in f]}
    return F


def metricas_base(F, hoje):
    """id -> {valor, anterior, fonte, confianca, nota}. Pacote manda; o resto vem das fontes do Mac."""
    M = {}

    def m(i, valor, fonte, confianca="media", nota="", anterior=None, desde=None):
        M[i] = {"valor": valor, "anterior": anterior, "fonte": fonte, "confianca": confianca, "nota": nota, "desde": desde}

    pac = _json(F["pacote"]) if F["pacote"] else None
    met = _json(F["metricas"]) if F["metricas"] else None
    bi = _json(F["dados_bi"]) if F["dados_bi"] else None
    prev = _json(F["previsao"]) if F["previsao"] else None

    # --- resultado: ritmo da meta do mês e do Q4 (D111). Valor = ritmo atual ÷ ritmo necessário × 100 (verde >= 90, amarelo >= 70)
    s = (met or {}).get("semana_hubspot") or (met or {}).get("semana") or {}; ant = s.get("anterior") or {}
    pm = pac.get("meta") if pac and isinstance(pac.get("meta"), dict) else {}
    ma, tt = pm.get("mes_atual") or {}, pm.get("total") or {}
    if ma.get("ritmo_necessario_rs_dia") is not None and tt.get("ritmo_necessario") is not None:
        nec_m, nec_q = float(ma["ritmo_necessario_rs_dia"]), float(tt["ritmo_necessario"])
        at_m, at_q = float(ma.get("ritmo_atual_rs_dia") or 0), float(tt.get("ritmo_atual") or 0)
        fonte_meta = f"pacote {pac.get('data')} (D111, volume limpo)"; conf_meta = "alta"; nome_m = f"{ma.get('nome')} R$ {ma.get('meta_rs', 0)/1e6:.0f} mi"
    else:  # sem pacote: meta do mês corrente e do Q4 contra o realizado do metricas (bruto)
        mes = hoje.isoformat()[:7]; serie = (met or {}).get("serie_mensal") or {}
        real_m = float((serie.get(mes) or {}).get("ganhos_rs", 0)); real_q = sum(float(v.get("ganhos_rs", 0)) for k, v in serie.items() if "2026-10" <= k <= "2026-12")
        ini = hoje.replace(day=1); fim = (ini + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        du_pass_m = uteis_entre(ini - timedelta(days=1), hoje); du_rest_m = max(uteis_entre(hoje, fim), 1)
        du_pass_q = uteis_entre(date(2026, 9, 30), hoje); du_rest_q = max(uteis_entre(hoje, date(2026, 12, 31)), 1)
        nec_m = max(METAS_MES.get(mes, 0) - real_m, 0) / du_rest_m; nec_q = max(META_Q4_RS - real_q, 0) / du_rest_q
        at_m = real_m / max(du_pass_m, 1); at_q = real_q / max(du_pass_q, 1)
        fonte_meta = f"metricas {(met or {}).get('data_relatorio')} (bruto) × D111"; conf_meta = "media"; nome_m = mes
    r = lambda v, n: round(100 * v / n, 1) if n else 100.0
    nota_m = f"meta do mês ({nome_m}): ritmo atual R$ {at_m:,.0f}/dia útil × necessário R$ {nec_m:,.0f}/dia útil".replace(",", ".")
    nota_q = f"meta do Q4 (R$ 250 mi): ritmo atual R$ {at_q:,.0f}/dia útil × necessário R$ {nec_q:,.0f}/dia útil".replace(",", ".")
    gan_ant = ant.get("ganhos_rs", 0) / 5
    m("ganhos_ritmo_pct", r(at_m, nec_m), fonte_meta, conf_meta, nota_m, r(gan_ant, nec_m) if s else None)
    m("ganhos_ritmo_q4_pct", r(at_q, nec_q), fonte_meta, conf_meta, nota_q, r(gan_ant, nec_q) if s else None)
    if s:
        cri, cri_ant = s.get("criados_rs", 0) / 5, ant.get("criados_rs", 0) / 5
        nota_c = f"semana {s.get('de')}–{s.get('ate')}: R$ {s.get('criados_rs', 0):,.0f} criados em {s.get('criados_n', 0)} negócios (muitos sem valor: confiança baixa)".replace(",", ".")
        m("criados_ritmo_pct", r(cri, nec_m), fonte_meta, "baixa", nota_c + "; " + nota_m.replace("ritmo atual", "fechado"), r(cri_ant, nec_m))
        m("criados_ritmo_q4_pct", r(cri, nec_q), fonte_meta, "baixa", nota_c + "; " + nota_q.replace("ritmo atual", "fechado"), r(cri_ant, nec_q))
    if met:
        m("win_rate_3m", met.get("win_rate_3m"), f"metricas {met.get('data_relatorio')}", "media", "ganhos ÷ (ganhos + perdidos), 3 meses")
        mom = ((met.get("mes_ate_hoje") or {}).get("crescimento") or {}).get("ganhos_rs") or {}
        m("ganhos_mom_fator", mom.get("fator"), f"metricas {met.get('data_relatorio')}", "media", f"mês até hoje R$ {mom.get('atual', 0):,.0f} vs mesmo período do mês anterior R$ {mom.get('anterior', 0):,.0f}".replace(",", "."))

    # --- caixa
    sem_caixa = True
    if pac:
        sem_caixa = not any(x.get("id") in ("recebido_mes_rs", "roi_realizado") and x.get("status") != "cinza" for x in pac.get("metricas", []))
    elif met:
        sem_caixa = any("Recebimentos" in p or "caixa" in p.lower() for p in met.get("pendencias", []))
    m("semanas_sem_fonte_caixa", (hoje - DATA_SEM_CAIXA_DESDE).days // 7 if sem_caixa else 0, "pendências do relatório semanal (desde 28/09)", "alta",
      "honorário recebido não está em nenhuma fonte; ROI realizado e backlog em cinza" if sem_caixa else "")
    if prev and prev.get("caixa_13_semanas"):
        base4 = sum(x.get("entrada_rs_base", 0) for x in prev["caixa_13_semanas"][:4])
        liq_mes = (met or {}).get("lucro_roi", {}).get("honorario_liquido_mes") or 1
        m("caixa_4_semanas_pct", round(100 * base4 / liq_mes, 1), f"previsao {prev.get('data')}", "media", f"R$ {base4:,.0f} nas próximas 4 semanas (cenário base)".replace(",", "."))
    else:
        m("caixa_4_semanas_pct", None, "previsao-<data>.json ausente", "baixa", "sem previsão de caixa ainda")
    if bi:
        inc = bi.get("inconsistencias") or {}
        ganhos_n = (met or {}).get("cobertura_honorario_hubspot", {}).get("ganhos") or 0
        sem_h = inc.get("Ganho sem % de honorário")
        m("ganhos_sem_honorario_pct", round(100 * sem_h / ganhos_n, 1) if sem_h is not None and ganhos_n else None, f"dados-bi {bi.get('baixado_em')}", "alta", f"{sem_h} de {ganhos_n} ganhos sem % de honorário")
        m("indice_qualidade_ganhos", bi.get("indice_qualidade_ganhos"), f"dados-bi {bi.get('baixado_em')}", "alta", "")
        pa = bi.get("abertos_parados") or {}; pipe = (met or {}).get("pipeline_aberto", {}).get("n") or 0
        m("abertos_parados_pct", round(100 * pa.get("n", 0) / pipe, 1) if pipe else None, f"dados-bi {bi.get('baixado_em')}", "alta", f"{pa.get('n')} parados (R$ {pa.get('rs', 0):,.0f}) de {pipe} abertos".replace(",", "."))
        m("duplicidade_grupos", (bi.get("duplicidade_abertos") or {}).get("cnpjs"), f"dados-bi {bi.get('baixado_em')}", "alta", f"{(bi.get('duplicidade_abertos') or {}).get('negocios')} negócios em duplicidade")
        m("honorario_atipico_n", inc.get("Honorário atípico"), f"dados-bi {bi.get('baixado_em')}", "alta", "honorário acima de 50% do crédito")
        sc = [s for s in bi.get("scorecard", []) if "fora do roster" not in s.get("parceiro", "")]
        queda = [s["parceiro"] for s in sc if (s.get("ritmo_valor_vs_media_trimestral_pct") or 0) < -50]
        m("masters_em_queda_n", len(queda), f"scorecard dados-bi {bi.get('baixado_em')}", "media", "em queda: " + ", ".join(queda) if queda else "nenhum Master abaixo de -50%")
    if pac and pac.get("confiabilidade"):
        c = pac["confiabilidade"]
        if c.get("ganhos_sem_honorario_pct") is not None: M["ganhos_sem_honorario_pct"] = {**M.get("ganhos_sem_honorario_pct", {}), "valor": c["ganhos_sem_honorario_pct"], "fonte": f"pacote {pac.get('data')}", "confianca": "alta", "nota": "", "anterior": None}
        if c.get("duplicados_grupos") is not None:
            m("duplicados_grupos", c.get("duplicados_grupos_alta", c["duplicados_grupos"]), f"pacote {pac.get('data')}", "alta",
              f"grupos de duplicidade de alta confiança nos ganhos de 12 meses ({c.get('cards_que_saem_alta', '?')} cards saem do volume limpo; excedente R$ {c.get('excedente_alta_rs', 0):,.0f})".replace(",", "."))
    else:
        m("duplicados_grupos", None, "pacote-<data>.json ausente", "baixa", "grupos de duplicidade nos ganhos (saneamento_duplicados.py) só com o pacote")

    # --- canal
    if met:
        c5 = (met.get("concentracao_12m") or {}).get("top5_pct")
        m("concentracao_top5_pct", c5, f"metricas {met.get('data_relatorio')} (12 meses)", "alta", "top 5: " + ", ".join(p for p, _ in (met.get("concentracao_12m") or {}).get("top5", [])))
        pa = met.get("parceiros_ativos_90d") or {}
        m("parceiros_ativos_pct", round(100 * pa.get("ativos", 0) / pa["carteira"], 1) if pa.get("carteira") else None, f"metricas {met.get('data_relatorio')}", "media", f"{pa.get('ativos')} de {pa.get('carteira')} do roster")

    # --- risco (previsão)
    if prev and prev.get("decadencia_mensal"):
        prox = (hoje.replace(day=1) + timedelta(days=32)).strftime("%Y-%m")
        d = next((x for x in prev["decadencia_mensal"] if x.get("mes") == prox), None)
        m("decadencia_proximo_mes_rs", d.get("credito_que_sai_rs", 0) if d else 0, f"previsao {prev.get('data')}", "media", f"{(d or {}).get('clientes_n', 0)} clientes em {prox}")
    else:
        m("decadencia_proximo_mes_rs", None, "previsao-<data>.json ausente", "baixa", "sem previsão de decadência ainda")

    # --- operação: lote do Recuperador
    ind = [(_json(f) or {}) for f in F["recuperador"]]
    ind = [i for i in ind if i.get("data")]
    if ind:
        u = ind[-1]
        if (u.get("casos_lote") or 0) > 0 and not u.get("decididas"):
            desde = u["data"]
            for i in reversed(ind[:-1]):
                if i.get("lote_enviado") == u.get("lote_enviado") and not i.get("decididas"): desde = i["data"]
                else: break
            horas = int((datetime.combine(hoje, datetime.min.time()) - datetime.fromisoformat(desde + "T10:00")).total_seconds() // 3600)
            m("lote_sem_decisao_h", max(horas, 0), f"indicadores do Recuperador {u['data']}", "alta", f"lote {u.get('lote_enviado')} com {u.get('casos_lote')} casos (R$ {u.get('honorario_esperado_lote', 0):,.0f} esperados) sem decisão desde {desde}".replace(",", "."), desde=desde)
        else:
            m("lote_sem_decisao_h", 0, f"indicadores do Recuperador {u['data']}", "alta", "")
    pac_ids = {x.get("id"): x for x in (pac or {}).get("metricas", [])}
    for i, x in pac_ids.items():  # qualquer métrica do pacote com o mesmo id prevalece
        if i in M and x.get("valor") is not None and not str(x.get("fonte", "")).startswith("controle"):
            M[i].update({"valor": x["valor"], "fonte": x.get("fonte", M[i]["fonte"]), "confianca": x.get("confianca", M[i]["confianca"])})
    return M


def listas(F, hoje, controles_ant):
    """Itens das regras de lista: cada item vira um desvio próprio."""
    L = {"entregas_atrasadas_n": [], "acerto_area": [], "pedido_parado_dias": [], "aprovacoes_vazias_pct": [], "acoes_vencidas_n": []}
    e = _json(F["entregas"]) or {}
    if e.get("data") == hoje.isoformat():
        for x in e.get("faltando", []):
            L["entregas_atrasadas_n"].append({"item": x.get("id"), "texto": f"{x.get('nome')} (refazer: {x.get('refazer')})", "valor": 1, "pessoa": None})
    av = _json(F["avaliacoes"]) or {}
    for a, v in (av.get("areas") or {}).items():
        if v.get("acerto") is not None and v["acerto"] < 70:
            L["acerto_area"].append({"item": a, "texto": f"{a}: acerto {v['acerto']} ({v.get('criticos', 0)} críticos) em {av.get('data')}", "valor": v["acerto"], "pessoa": None})
    dm = (_json(F["demandas"]) or {}).get("demandas") or {}
    for d in dm.values():
        if d.get("status") not in ("responder", "aguardando_aprovacao"): continue
        try: desde = datetime.fromisoformat(d.get("atualizada_em") or d.get("aberta_em")).date()
        except ValueError: continue
        dias = uteis_entre(desde, hoje)
        if dias > 2:
            L["pedido_parado_dias"].append({"item": d["id"], "texto": f"{d['id']} ({d.get('status')}, {dias} dias úteis): {str(d.get('titulo', ''))[:60]}", "valor": dias, "pessoa": d.get("pessoa") if d.get("pessoa") in PESSOAS else None})
    # aprovações vazias por área e semana (protocolo do gerente §5.1)
    por_sem = {}
    for f in F["analises"]:
        dt = re.search(r"(\d{4}-\d{2}-\d{2})", f).group(1)
        try: w = semana_iso(date.fromisoformat(dt))
        except ValueError: continue
        d = _json(f) or {}
        for v in (d.values() if isinstance(d, dict) else d):
            if not isinstance(v, dict): continue
            r = v.get("revisao") or {}
            if not r.get("aprovado"): continue
            area = str(v.get("area") or r.get("gerente") or "?")
            aj = str(r.get("ajustes") or "").strip().lower(); mot = str(r.get("sem_ajuste_motivo") or "").strip()
            vazia = (aj in ("", "ok", "nenhum", "aprovado", "sem ajustes", "nenhum ajuste") or (not aj)) and len(mot) < 20
            t = por_sem.setdefault(w, {}).setdefault(area, [0, 0]); t[0] += 1; t[1] += int(vazia)
    sems = sorted(por_sem)[-2:]
    if len(sems) == 2:
        for area in set(por_sem[sems[0]]) & set(por_sem[sems[1]]):
            pcts = [round(100 * por_sem[s][area][1] / por_sem[s][area][0]) for s in sems if por_sem[s][area][0] >= 3]
            if len(pcts) == 2 and min(pcts) > 80:
                L["aprovacoes_vazias_pct"].append({"item": area, "texto": f"{area}: {pcts[0]}% e {pcts[1]}% de aprovações vazias nas semanas {sems[0]} e {sems[1]}", "valor": pcts[1], "pessoa": None})
    for l in open(ACOES, encoding="utf-8") if os.path.exists(ACOES) else []:
        try: a = json.loads(l)
        except ValueError: continue
        if a.get("status") in ("concluida", "cancelada", "resolvida"): continue
        if str(a.get("prazo", "9999")) < hoje.isoformat():
            L["acoes_vencidas_n"].append({"item": a.get("id") or a.get("acao", "")[:40], "texto": f"{a.get('origem', 'conselho')}: {str(a.get('acao', ''))[:80]} (dono {a.get('dono')}, prazo {a.get('prazo')})", "valor": uteis_entre(date.fromisoformat(str(a['prazo'])[:10]), hoje), "pessoa": a.get("dono") if a.get("dono") in PESSOAS else None})
    return L


# ---------------------------------------------------------------- regras
def historico_status(controles_ant):
    """metrica -> [(data, status)] dos controles anteriores (persistência "por N semanas")."""
    H = {}
    for f in controles_ant:
        c = _json(f) or {}
        for s in c.get("semaforo", []):
            H.setdefault(s.get("id"), []).append((c.get("data"), s.get("status")))
    return H


def semanas_fora(regra, metr, hist, tol):
    """Quantas semanas seguidas (contando a atual) a métrica está fora da tolerância para a regra."""
    n = 1
    ant = [s for _, s in sorted(hist.get(regra["metrica"], []))]
    if ant:
        for s in reversed(ant):
            if s in ("amarelo", "vermelho"): n += 1
            else: break
    elif metr.get("anterior") is not None and _cmp(regra["operador"], float(metr["anterior"]), float(regra["limite"])):
        n += 1  # 1ª rodada: a semana anterior vem do dado "anterior" da própria fonte
    return n


def aplicar(cfg, M, L, hoje, controles_ant):
    hist = historico_status(controles_ant)
    tol = cfg["tolerancias"]
    semaforo = []
    for i, x in M.items():
        st = status_de(tol.get(i), x["valor"])
        semaforo.append({"id": i, "valor": x["valor"], "unidade": tol.get(i, {}).get("unidade"), "status": st, "tolerancia": {k: tol.get(i, {}).get(k) for k in ("verde", "amarelo")},
                         "proposta": tol.get(i, {}).get("proposta", True), "fonte": x["fonte"], "confianca": x["confianca"], "nota": x["nota"], "anterior": x.get("anterior")})
    for i in L:
        n = len(L[i]); st = status_de(tol.get(i), n) if i in ("entregas_atrasadas_n", "acoes_vencidas_n") else ("verde" if n == 0 else "vermelho")
        semaforo.append({"id": i, "valor": n, "unidade": "n", "status": st, "tolerancia": {k: tol.get(i, {}).get(k) for k in ("verde", "amarelo")}, "proposta": False,
                         "fonte": "listas do controle", "confianca": "alta", "nota": "; ".join(x["texto"] for x in L[i][:5]), "anterior": None})
    anteriores = {}
    for f in controles_ant:
        for d in (_json(f) or {}).get("desvios", []): anteriores[d.get("chave")] = d
    desvios = []
    for r in cfg["regras"]:
        if r.get("tipo") == "lista":
            for it in L.get(r["metrica"], []):
                if not _cmp(r["operador"], float(it["valor"]), float(r["limite"])): continue
                dono = it["pessoa"] or ("luis" if r["dono"] == "pessoa" else r["dono"])
                desvios.append(_desvio(r, it["valor"], it["texto"], dono, hoje, anteriores, chave=f"{r['id']}|{it['item']}"))
            continue
        for met_id in [r["metrica"]] + list(r.get("metricas_extra", [])):  # C01/C02: meta do mês e meta do Q4 (D111)
            x = M.get(met_id); rr = dict(r, metrica=met_id)
            if not x or x["valor"] is None: continue
            if not _cmp(r["operador"], float(x["valor"]), float(r["limite"])): continue
            n = semanas_fora(rr, x, hist, tol)
            if n < r.get("semanas", 1): continue
            desde = hoje - timedelta(weeks=n - 1)
            op = {"<": "abaixo de", "<=": "até", ">": "acima de", ">=": "a partir de", "==": "igual a"}[r["operador"]]
            texto = f"{met_id} = {x['valor']} {tol.get(met_id, {}).get('unidade', '')} (gatilho: {op} {r['limite']}); {x['nota']}".strip("; ")
            d = _desvio(rr, x["valor"], texto, r["dono"], hoje, anteriores, chave=f"{r['id']}|{met_id}", desde=x.get("desde") or desde.isoformat(), confianca=x["confianca"])
            escala = (r.get("escala_se_rs") and float(x["valor"]) > r["escala_se_rs"]) or (r.get("escala_dias") and uteis_entre(date.fromisoformat(d["desde"]), hoje) >= r["escala_dias"])
            if r.get("escala_para") and escala:
                d["escalado_para"] = r["escala_para"]; d["co_donos"] = [d["dono"]] + [c for c in d["co_donos"] if c != d["dono"]]; d["dono"] = r["escala_para"]
                d["acao"] += f" [escalado a {r['escala_para']}: prazo da regra vencido]"
            desvios.append(d)
    for d in desvios: d["vencido"] = d["prazo"] < hoje.isoformat()
    abertos = {d["chave"] for d in desvios}
    resolvidos = [{**a, "status": "resolvido", "resolvido_em": hoje.isoformat()} for k, a in anteriores.items() if k not in abertos and a.get("status") != "resolvido"]
    return semaforo, desvios, resolvidos


def _desvio(r, valor, texto, dono, hoje, anteriores, chave, desde=None, confianca="alta"):
    a = anteriores.get(chave) or {}
    desde = a.get("desde") or desde or hoje.isoformat()
    prazo = a.get("prazo") if a.get("status") == "em_andamento" else somar_uteis(hoje, r["prazo_dias"]).isoformat()
    return {"regra": r["id"], "bloco": r["bloco"], "metrica": r["metrica"], "valor": valor, "limite": r["limite"], "condicao": r["condicao"], "texto": texto, "desde": desde,
            "acao": r["acao"], "dono": dono, "co_donos": r.get("co_donos", []), "prazo": prazo, "alcada": r["alcada"], "conselho": bool(r.get("conselho")),
            "status": a.get("status") if a.get("status") in ("aberto", "em_andamento") else "aberto", "confianca": confianca, "chave": chave}


# ---------------------------------------------------------------- caixa
def _ledger():
    out = set()
    for l in open(LEDGER, encoding="utf-8") if os.path.exists(LEDGER) else []:
        try: x = json.loads(l); out.add((x["chave"], x["semana"]))
        except (ValueError, KeyError): pass
    return out


def enviar_caixa(desvios, hoje):
    import caixa
    sem = semana_iso(hoje); ja = _ledger(); enviados = []; para_luis = []
    acoes = [{"rotulo": "Abrir gestão", "go": "gestao"}]
    for d in desvios:
        if (d["chave"], sem) in ja: continue
        if d["dono"] in PESSOAS:
            resumo = (f"{d['condicao'].capitalize()}.\n{d['texto']}\n\nAção: {d['acao']}.\nPrazo: {d['prazo']}" + (f" · com {', '.join(d['co_donos'])}" if d["co_donos"] else "")
                      + (f"\nVai ao Conselho de segunda." if d["conselho"] else "") + f"\nRegra {d['regra']} (infra/controle.md). Desde {d['desde']}.")
            ids = caixa.enviar(d["dono"], f"Controle · {d['regra']}: {d['condicao']}", resumo, origem="controle", prioridade="alta", acoes=acoes, tipo="alerta")
            enviados.append({"chave": d["chave"], "semana": sem, "para": d["dono"], "id_caixa": ids[0] if ids else None, "em": datetime.now().isoformat(timespec="seconds")})
        else:
            para_luis.append(d)
    if para_luis:
        linhas = [f"- {d['regra']} · {d['condicao']} → {d['acao']} (dono {d['dono']}, prazo {d['prazo']})" for d in para_luis]
        resumo = "Desvios cujo dono é um agente (sem caixa própria). Entram na pauta do Conselho de segunda; nada precisa da sua decisão hoje, salvo alçada marcada.\n\n" + "\n".join(linhas)
        ids = caixa.enviar("luis", f"Controle · {len(para_luis)} desvio(s) com dono agente ({sem})", resumo, origem="controle", prioridade="alta", acoes=acoes, tipo="alerta")
        for d in para_luis:
            enviados.append({"chave": d["chave"], "semana": sem, "para": "luis (resumo)", "id_caixa": ids[0] if ids else None, "em": datetime.now().isoformat(timespec="seconds")})
    os.makedirs(GESTAO, exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as f:
        for e in enviados: f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return enviados


# ---------------------------------------------------------------- principal
def rodar(hoje, com_caixa=True):
    cfg = _json(os.path.join(REPO, "infra", "controle.json"))
    if not cfg: sys.exit("infra/controle.json não encontrado")
    F = carregar_fontes(hoje)
    M = metricas_base(F, hoje)
    L = listas(F, hoje, F["controles_anteriores"])
    semaforo, desvios, resolvidos = aplicar(cfg, M, L, hoje, F["controles_anteriores"])
    enviados = enviar_caixa(desvios, hoje) if com_caixa else []
    saida = {"data": hoje.isoformat(), "semana": semana_iso(hoje), "gerado_em": datetime.now().isoformat(timespec="seconds"),
             "fontes": {k: (os.path.relpath(v, AP) if isinstance(v, str) and os.path.exists(v) else ("ausente" if not v or isinstance(v, str) else [os.path.basename(x) for x in v][-3:])) for k, v in F.items()},
             "regras": [{k: r.get(k) for k in ("id", "bloco", "metrica", "condicao", "acao", "dono", "prazo_dias", "alcada")} for r in cfg["regras"]],
             "semaforo": semaforo, "desvios": desvios, "resolvidos": resolvidos, "ritual": cfg["ritual"], "caixa_enviadas": enviados,
             "revisao": {"gerente": "Gabinete", "especialistas": ["Qualidade (controle de entregas)", "Operações de Canal", "Dados (governança)"], "rodadas": 1,
                         "areas_consultadas": ["Resultados (dicionário de métricas)"], "aprovado": True,
                         "ajustes": "tolerâncias marcadas 'proposta' até o Luis aprovar; meta D111 em crédito de contrato fechado: C01/C02 leem o ritmo da meta do mês e do Q4"}}
    os.makedirs(GESTAO, exist_ok=True)
    out = os.path.join(GESTAO, f"controle-{hoje.isoformat()}.json")
    json.dump(saida, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out, saida


def resumo(s):
    cor = {"verde": "verde", "amarelo": "AMARELO", "vermelho": "VERMELHO", "cinza": "cinza"}
    print(f"Controle {s['data']} ({s['semana']}) · {len(s['desvios'])} desvio(s) aberto(s) · {len(s['resolvidos'])} resolvido(s) · {len(s['caixa_enviadas'])} mensagem(ns) na caixa")
    print("\nSemáforo:")
    for x in sorted(s["semaforo"], key=lambda x: -STATUS_ORDEM.get(x["status"], 0)):
        v = x["valor"]; v = f"{v:,.1f}".replace(",", ".") if isinstance(v, float) else v
        print(f"  {cor[x['status']]:9} {x['id']:26} {v!s:>12} {x.get('unidade') or '':4} {'(proposta)' if x.get('proposta') else '':10} {x['nota'][:90]}")
    print("\nDesvios abertos:")
    for d in s["desvios"]:
        print(f"  {d['regra']} [{d['bloco']}] dono {d['dono']} · prazo {d['prazo']} · alçada {d['alcada']}{' · Conselho' if d['conselho'] else ''}\n      {d['texto'][:160]}\n      → {d['acao']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", default=date.today().isoformat())
    ap.add_argument("--sem-caixa", action="store_true", help="não manda mensagens à caixa de entrada")
    ap.add_argument("--resumo", action="store_true", help="imprime o resumo em texto")
    ap.add_argument("--json", action="store_true", help="imprime o JSON gerado")
    a = ap.parse_args()
    out, s = rodar(date.fromisoformat(a.data), com_caixa=not a.sem_caixa)
    if a.json: print(json.dumps(s, ensure_ascii=False, indent=1))
    else:
        resumo(s); print(f"\nGravado: {out}")


if __name__ == "__main__":
    main()
