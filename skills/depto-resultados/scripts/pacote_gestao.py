#!/usr/bin/env python3
"""Pacote de gestão semanal (Controller com Dados & BI), no contrato de infra/gestao-schema.md, seção 1.

Gera ~/agentes-partners/registro/gestao/pacote-AAAA-MM-DD.json com as métricas de resultado, caixa, canal, risco e
operação que têm dado, cada uma com fonte, confiança, tolerância (proposta até o Luis aprovar) e status semáforo.
Métrica sem dado entra em cinza, com a nota de quem fornece. Nada aqui altera HubSpot, GLPI ou Financeiro.

Fontes (todas locais, só leitura):
  departamentos/resultados/dados/metricas-<data>.json e hubspot-<data>.json (download do HubSpot, escopo do mapeamento)
  skills/depto-dados/scripts/saneamento_duplicados.py (volume limpo) · departamentos/dados/dados-bi-*.json (qualidade, scorecard)
  departamentos/partner-success/metricas/metricas-ps-*.json · registro/demandas.json · registro/medicao-respostas.json
  registro/avaliacoes/relatorio-*.json · registro/entregas-faltando.json · registro/decisoes-respostas.json
  celulas/geovana/recuperador/indicadores-*.json · docs/lancamento-2026/janelas.json · celulas/geovana/pareceres/resumos.json

Uso: python3 pacote_gestao.py [--data AAAA-MM-DD] [--sem-saneamento]
"""
import argparse, glob, importlib.util, json, os, re, statistics, sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

AP = os.path.expanduser("~/agentes-partners")
AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AP, "departamentos/resultados/dados")
SAIDA = os.path.join(AP, "registro/gestao")
META_Q4_RS = 200_000_000  # D64 (22/10/2026); unidade indefinida (pergunta R1)
MARGEM_LIQ_REF = None  # preenchida com a carteira (metricas margem_carteira)
# Feriados nacionais do Q4/2026 (Lei 662/1949, Lei 6.802/1980, Lei 14.759/2023). 15/11 cai no domingo. 24 e 31/12 não são feriado.
FERIADOS = {date(2026, 10, 12), date(2026, 11, 2), date(2026, 11, 20), date(2026, 12, 25)}
PIPELINES_PRODUTO = {"RT - Real & Presumido": "Recuperação (Real e Presumido)", "RT - Simples Nacional": "Recuperação (Simples)",
                     "Gestão de Passivo": "Gestão de Passivo", "Produtos Tributários": "Produtos tributários",
                     "Produtos Jurídicos": "Produtos jurídicos", "Planejamento Tributário": "Planejamento tributário"}
PRODUTO_DE = {"Gestão de Passivo": "Gestão de Passivo", "Produtos Jurídicos": "Jurídico", "Planejamento Tributário": "Planejamento",
              "Produtos Tributários": "Produtos tributários"}  # os demais pipelines RT contam como "Recuperação"


# ----------------------------------------------------------------------------- utilitários
def dias_uteis(a, b):
    """Dias úteis de a até b, inclusive os dois (segunda a sexta, sem feriado nacional)."""
    n, d = 0, a
    while d <= b:
        if d.weekday() < 5 and d not in FERIADOS: n += 1
        d += timedelta(days=1)
    return n


def ym_add(ym, n):
    y, m = int(ym[:4]), int(ym[5:7]); t = y * 12 + (m - 1) + n
    return f"{t // 12:04d}-{t % 12 + 1:02d}"


def dt(s):
    try: return datetime.fromisoformat((s or "")[:10]).date()
    except ValueError: return None


def ult(padrao, ate=None):
    """Arquivo mais recente do padrão (com data no nome), até a data pedida."""
    fs = sorted(glob.glob(padrao))
    if ate: fs = [f for f in fs if re.search(r"\d{4}-\d{2}-\d{2}", f) and re.search(r"\d{4}-\d{2}-\d{2}", f).group(0) <= ate]
    return fs[-1] if fs else None


def ler(f):
    return json.load(open(f)) if f and os.path.exists(f) else None


def pct(a, b):
    return round(a / b * 100, 1) if b else None


def var(atual, anterior):
    if atual is None or anterior in (None, 0): return None
    return round((atual / anterior - 1) * 100, 1)


def ri(x):
    return int(round(x)) if isinstance(x, (int, float)) else x


def brl(x):
    return "R$ " + f"{ri(x):,}".replace(",", ".") if x is not None else "n/d"


def modulo(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m


class Pacote:
    def __init__(s, hoje):
        s.hoje = hoje; s.metricas = []; s.alertas = []; s.divergencias = []

    def add(s, id, nome, bloco, valor, unidade, fonte, confianca, tolerancia=None, status=None, anterior=None, meta=None,
            nota="", detalhe=None, melhor="maior"):
        """Adiciona métrica. status: calculado pela tolerância proposta (verde/amarelo/vermelho) ou 'cinza' sem dado."""
        m = {"id": id, "nome": nome, "bloco": bloco, "valor": ri(valor) if unidade == "R$" else valor, "unidade": unidade,
             "anterior": ri(anterior) if unidade == "R$" else anterior, "variacao_pct": var(valor, anterior), "meta": meta,
             "tolerancia": dict(tolerancia or {}, origem="proposta"), "status": status or s.status(valor, tolerancia, melhor),
             "fonte": fonte, "confianca": confianca, "nota": nota}
        if detalhe is not None: m["detalhe"] = detalhe
        s.metricas.append(m); return m

    @staticmethod
    def status(valor, tol, melhor):
        if valor is None or not tol or "verde" not in tol: return "cinza"
        v, a = tol.get("_verde"), tol.get("_amarelo")
        if v is None: return "cinza"
        if melhor == "maior": return "verde" if valor >= v else "amarelo" if (a is not None and valor >= a) else "vermelho"
        return "verde" if valor <= v else "amarelo" if (a is not None and valor <= a) else "vermelho"

    def alerta(s, texto, area, sev="media"):
        s.alertas.append({"texto": texto, "area": area, "severidade": sev})


def tol(verde, amarelo, texto_v, texto_a):
    return {"verde": texto_v, "amarelo": texto_a, "_verde": verde, "_amarelo": amarelo}


# ----------------------------------------------------------------------------- carga do HubSpot no escopo da área
def carregar_negocios(data):
    f = os.path.join(DADOS, f"hubspot-{data}.json")
    if not os.path.exists(f): f = ult(os.path.join(DADOS, "hubspot-*.json"), data)
    D = json.load(open(f)); N = D["negocios"]
    mapa = json.load(open(os.path.join(AP, "departamentos/resultados/mapeamento-hubspot.json")))
    regras = mapa.get("regras", {}); corte = regras.get("excluir_cafe_desde")
    roster = set(mapa["escopo"]["parceiros_roster"])
    if corte:  # mesma regra do calc_semana.py: café fora desde abr/2026
        kw = regras.get("cafe_palavras", []); cn = {c.lstrip("0") for c in regras.get("cafe_cnae", [])}
        def cafe(d):
            txt = f"{d.get('nome') or ''} {d.get('segmento') or ''}".lower()
            return any(k in txt for k in kw) or str(d.get("cnae") or "").lstrip("0") in cn
        ref = lambda d: (d["fechado"] if d["status"] != "aberto" else d["criado"])[:7]
        N = [d for d in N if not (cafe(d) and ref(d) >= corte)]
    for d in N:
        d["_raiz"] = (re.sub(r"[^0-9A-Z]", "", str(d["extras"].get("cnpj") or "").upper()))[:8]
        d["_roster"] = d["parceiro"] in roster
        d["_hon"] = d["valor"] * d["hContr"] if d.get("hContr") is not None else None
        d["_liq"] = d["valor"] * d["hContr"] * (1 - min(d.get("hParc") or 0, 1)) if d.get("hContr") is not None else None
    return N, D["baixado_em"], f, roster


# ----------------------------------------------------------------------------- blocos
def bloco_resultado(P, M, N, fonte_hs):
    mes = M["mes_ate_hoje"]; pm = mes["mesmo_periodo_mes_anterior"]; sem = M["semana_hubspot"]
    P.add("criados_mes_rs", "Negócios criados no mês (R$ crédito)", "resultado", mes["criados_rs"], "R$", fonte_hs, "media",
          tol(0.9 * pm["criados_rs"], 0.7 * pm["criados_rs"], ">= 90% do mesmo período do mês anterior", ">= 70%"), anterior=pm["criados_rs"],
          nota="Valor dos criados é preenchido dias depois: parte da queda é atraso de cadastro (D71). Mesmo período de setembro.")
    P.add("criados_mes_n", "Negócios criados no mês (nº)", "resultado", mes["criados_n"], "n", fonte_hs, "alta",
          tol(0.9 * pm["criados_n"], 0.7 * pm["criados_n"], ">= 90% do mesmo período do mês anterior", ">= 70%"), anterior=pm["criados_n"])
    P.add("ganhos_mes_rs", "Fechado no mês (R$ crédito, bruto)", "resultado", mes["ganhos_rs"], "R$", fonte_hs, "alta",
          tol(0.9 * pm["ganhos_rs"], 0.7 * pm["ganhos_rs"], ">= 90% do mesmo período do mês anterior", ">= 70%"), anterior=pm["ganhos_rs"],
          nota="Sem meta mensal aprovada; a tolerância compara com setembro, que teve fechamentos grandes na última semana.")
    P.add("ganhos_mes_n", "Fechado no mês (nº)", "resultado", mes["ganhos_n"], "n", fonte_hs, "alta",
          tol(0.9 * pm["ganhos_n"], 0.7 * pm["ganhos_n"], ">= 90% do mesmo período do mês anterior", ">= 70%"), anterior=pm["ganhos_n"])
    P.add("ganhos_semana_rs", "Fechado na semana (R$ crédito)", "resultado", sem["ganhos_rs"], "R$", fonte_hs, "alta",
          tol(sem["anterior"]["ganhos_rs"], 0.7 * sem["anterior"]["ganhos_rs"], ">= semana anterior", ">= 70% da semana anterior"),
          anterior=sem["anterior"]["ganhos_rs"], nota=f"Semana {sem['de']} a {sem['ate']}: {sem['ganhos_n']} ganhos.")
    P.add("win_rate_3m", "Win rate (3 meses)", "resultado", M["win_rate_3m"], "%", fonte_hs, "alta",
          tol(30, 25, ">= 30%", ">= 25%"), nota="Ganhos ÷ (ganhos + perdidos) nos últimos 3 meses.")
    P.add("ticket_3m", "Ticket médio (R$ crédito por ganho, 3 meses)", "resultado", M["ticket_valor_3m"], "R$", fonte_hs, "alta",
          tol(1_000_000, 700_000, ">= R$ 1,0 mi", ">= R$ 0,7 mi"))
    # funil por produto (proxy: pipeline; a propriedade Produto ainda não existe: D37/D57)
    ab = [d for d in N if d["status"] == "aberto"]; g26 = [d for d in N if d["status"] == "ganho" and (d["fechado"] or "") >= "2026-01-01"]
    fun = {}
    for pipe, nome in PIPELINES_PRODUTO.items():
        a = [d for d in ab if d["pipeline"] == pipe]; g = [d for d in g26 if d["pipeline"] == pipe]
        fun[nome] = {"abertos_n": len(a), "abertos_rs": ri(sum(d["valor"] for d in a)), "ganhos_2026_n": len(g), "ganhos_2026_rs": ri(sum(d["valor"] for d in g))}
    P.add("funil_por_produto", "Funil por produto 2027 (proxy: pipeline do HubSpot)", "resultado", None, "n", fonte_hs, "baixa",
          status="cinza", detalhe=fun,
          nota="Sem a propriedade 'Produto' (D37/D57, time de CRM), só o pipeline separa os produtos; todo ganho em RT lê-se como recuperação. Fornece: TI/CRM cria a propriedade; Dados & BI testa no calc_semana.py.")
    # clientes com 2+ produtos
    por_raiz = defaultdict(set)
    for d in N:
        if d["status"] in ("ganho", "aberto") and d["_raiz"] and d["pipeline"] in PIPELINES_PRODUTO:
            por_raiz[d["_raiz"]].add(PRODUTO_DE.get(d["pipeline"], "Recuperação"))
    n2 = sum(1 for v in por_raiz.values() if len(v) >= 2); tot = len(por_raiz)
    P.add("clientes_2mais_produtos", "Clientes com 2+ produtos (raiz de CNPJ)", "resultado", pct(n2, tot), "%", fonte_hs, "media",
          tol(10, 5, ">= 10% da carteira", ">= 5%"), detalhe={"clientes_2mais": n2, "carteira_raizes": tot,
          "combinacoes": dict(Counter(" + ".join(sorted(v)) for v in por_raiz.values() if len(v) >= 2))},
          nota="Produto lido pelo pipeline (ganho ou aberto). Esteira Destravar caixa → Proteger e controlar → Crescer (depto-solucoes).")


def bloco_meta(P, M, N, hoje):
    q4 = [d for d in N if d["status"] == "ganho" and "2026-10-01" <= (d["fechado"] or "") <= "2026-12-31"]
    credito = sum(d["valor"] for d in q4); com_hon = [d for d in q4 if d["_liq"] is not None]
    liq_inf = sum(d["_liq"] for d in com_hon); margem = M["margem_carteira"]["margem_liquida_pct"] / 100
    liq_est = liq_inf + sum(d["valor"] for d in q4 if d["_liq"] is None) * margem
    du_tot = dias_uteis(date(2026, 10, 1), date(2026, 12, 31)); du_pass = dias_uteis(date(2026, 10, 1), hoje); du_rest = du_tot - du_pass
    def leitura(unidade, realizado):
        falta = max(META_Q4_RS - realizado, 0)
        return {"unidade": unidade, "meta_rs": META_Q4_RS, "realizado_rs": ri(realizado), "falta_rs": ri(falta), "pct_realizado": pct(realizado, META_Q4_RS),
                "ritmo_necessario_rs_dia": ri(falta / du_rest) if du_rest else None, "ritmo_atual_rs_dia": ri(realizado / du_pass) if du_pass else None,
                "fator_ritmo": round((falta / du_rest) / (realizado / du_pass), 1) if du_rest and realizado else None}
    cred, liq = leitura("credito", credito), leitura("liquido", liq_est)
    meta = {"q4_rs": META_Q4_RS, "unidade": "indefinida", "decisao": "D64 (22/10/2026)", "pergunta_ao_luis": "A meta de R$ 200 mi do Q4 está em crédito, honorário bruto ou honorário líquido? (pergunta R1)",
            "realizado_rs": ri(credito), "falta_rs": ri(max(META_Q4_RS - credito, 0)), "dias_uteis_restantes": du_rest, "dias_uteis_decorridos": du_pass,
            "dias_uteis_trimestre": du_tot, "ritmo_necessario_rs_dia": cred["ritmo_necessario_rs_dia"], "ritmo_atual_rs_dia": cred["ritmo_atual_rs_dia"],
            "leituras": {"credito": cred, "liquido": liq},
            "nota": f"Realizado = ganhos com fechamento em out–dez/2026 no escopo da área (café fora, D76 aplicada no mapeamento). Líquido: {len(com_hon)} de {len(q4)} ganhos têm honorário informado ({brl(liq_inf)}); o restante é estimado pela margem líquida da carteira ({M['margem_carteira']['margem_liquida_pct']}%). Feriados: 12/10, 02/11, 20/11, 25/12."}
    P.add("meta_q4_credito_pct", "Meta Q4 realizada (leitura crédito)", "resultado", cred["pct_realizado"], "%", "hubspot + D64", "alta",
          tol(100 * du_pass / du_tot, 70 * du_pass / du_tot, ">= proporcional aos dias úteis decorridos", ">= 70% do proporcional"), meta=META_Q4_RS,
          nota=f"{brl(credito)} de R$ 200 mi. Ritmo atual {brl(cred['ritmo_atual_rs_dia'])}/dia útil × necessário {brl(cred['ritmo_necessario_rs_dia'])}/dia útil ({cred['fator_ritmo']}x).")
    P.add("meta_q4_liquido_pct", "Meta Q4 realizada (leitura honorário líquido)", "resultado", liq["pct_realizado"], "%", "hubspot + margem carteira + D64", "media",
          tol(100 * du_pass / du_tot, 70 * du_pass / du_tot, ">= proporcional aos dias úteis decorridos", ">= 70% do proporcional"), meta=META_Q4_RS,
          nota=f"{brl(liq_est)} estimados de R$ 200 mi. Em líquido, a meta exige cerca de R$ 1,15 bi de crédito no trimestre.")
    return meta


def bloco_confiabilidade(P, M, N, sem_saneamento, hoje):
    g = [d for d in N if d["status"] == "ganho"]; ini12 = ym_add(hoje.isoformat()[:7], -11) + "-01"
    g12 = [d for d in g if (d["fechado"] or "") >= ini12]; gm = [d for d in g if (d["fechado"] or "")[:7] == hoje.isoformat()[:7]]
    bruto12, brutom = sum(d["valor"] for d in g12), sum(d["valor"] for d in gm)
    conf = {"volume_bruto_rs": ri(bruto12), "volume_limpo_rs": ri(bruto12), "volume_bruto_mes_rs": ri(brutom), "volume_limpo_mes_rs": ri(brutom),
            "duplicados_grupos": None, "duplicados_grupos_alta": None, "excedente_alta_rs": None, "periodo_12m_desde": ini12}
    grupos = None
    if not sem_saneamento:
        try:
            cand = [os.path.join(AQUI, "../../depto-dados/scripts/saneamento_duplicados.py"), os.path.join(AP, "skills/depto-dados/scripts/saneamento_duplicados.py")]
            san = modulo("saneamento", next(c for c in cand if os.path.exists(c)))
            grupos, _, meta = san.montar()
        except Exception as e:  # noqa: BLE001
            P.alerta(f"Saneamento de duplicados não rodou ({e}); volume limpo = bruto.", "depto-dados", "media")
    if grupos is not None:
        alta = [x for x in grupos if x["alta"]]
        saem12 = [d for x in alta for d in x["cards"][1:] if (d.get("fechado") or "") >= ini12]
        saemm = [d for x in alta for d in x["cards"][1:] if (d.get("fechado") or "")[:7] == hoje.isoformat()[:7]]
        conf.update({"duplicados_grupos": len(grupos), "duplicados_grupos_alta": len(alta), "excedente_alta_rs": ri(sum(x["excedente"] for x in alta)),
                     "excedente_total_rs": ri(sum(x["excedente"] for x in grupos)), "cards_que_saem_alta": sum(x["n_saem"] for x in alta),
                     "volume_limpo_rs": ri(bruto12 - sum(d["valor"] for d in saem12)), "volume_limpo_mes_rs": ri(brutom - sum(d["valor"] for d in saemm)),
                     "grupos_acima_10mi": sum(x["grande"] for x in grupos)})
    bi = ler(ult(os.path.join(AP, "departamentos/dados/dados-bi-*.json"), hoje.isoformat()))
    conf["indice_qualidade_ganhos"] = bi["indice_qualidade_ganhos"] if bi else None
    ch = M["cobertura_honorario_hubspot"]; conf["ganhos_sem_honorario_pct"] = pct(ch["ganhos"] - ch["com_honorario"], ch["ganhos"])
    conf["ganhos_sem_tese_pct"] = pct(M["mix_teses"]["ganhos_sem_tese"], ch["ganhos"])
    P.add("volume_limpo_12m_rs", "Fechado 12 meses, limpo × bruto (R$ crédito)", "resultado", conf["volume_limpo_rs"], "R$", "hubspot + saneamento_duplicados.py", "media" if grupos is not None else "baixa",
          tol(0.95 * bruto12, 0.85 * bruto12, "limpo >= 95% do bruto", ">= 85%"), anterior=None,
          detalhe={"bruto_rs": ri(bruto12), "excedente_alta_12m_rs": ri(bruto12 - conf["volume_limpo_rs"]), "mes": {"bruto_rs": conf["volume_bruto_mes_rs"], "limpo_rs": conf["volume_limpo_mes_rs"]}},
          nota="Limpo = bruto sem os cards que saem dos grupos de duplicidade de alta confiança (D87). Decisão da mescla é do time de CRM com a Daniela.")
    P.add("indice_qualidade_ganhos", "Índice de qualidade dos ganhos (campos essenciais)", "risco", conf["indice_qualidade_ganhos"], "%", "dados_bi.py", "alta",
          tol(90, 75, ">= 90%", ">= 75%"), nota="Média de preenchimento de valor, % honorário, % parceiro, tese, CNAE e CNPJ nos ganhos.")
    P.add("ganhos_sem_honorario_pct", "Ganhos sem % de honorário", "risco", conf["ganhos_sem_honorario_pct"], "%", "hubspot", "alta",
          tol(10, 30, "<= 10%", "<= 30%"), melhor="menor", nota=f"{ch['ganhos'] - ch['com_honorario']} de {ch['ganhos']} ganhos. Daniela e Masters preenchem no HubSpot (D71/D73).")
    if conf["duplicados_grupos"] is not None:
        P.add("duplicados_grupos", "Grupos de ganhos possivelmente duplicados", "risco", conf["duplicados_grupos"], "n", "saneamento_duplicados.py", "media",
              tol(0, 20, "0 grupos", "<= 20 grupos"), melhor="menor",
              detalhe={"alta": conf["duplicados_grupos_alta"], "excedente_alta_rs": conf["excedente_alta_rs"], "excedente_total_rs": conf.get("excedente_total_rs"), "acima_10mi": conf.get("grupos_acima_10mi")},
              nota="Valor em duplicidade é crédito estimado, não honorário. Grupo com card acima de R$ 10 mi vai ao Luis antes da mescla.")
    return conf


def bloco_caixa(P, M, N, hoje, janelas, resumos):
    g = [d for d in N if d["status"] == "ganho"]; ini12 = ym_add(hoje.isoformat()[:7], -11) + "-01"
    g12h = [d for d in g if (d["fechado"] or "") >= ini12 and d["_hon"] is not None]
    contratado = sum(d["_hon"] for d in g12h)
    P.add("recebido_x_contratado", "Honorário recebido × contratado (12 meses)", "caixa", None, "R$", "sem fonte", "baixa", status="cinza",
          detalhe={"contratado_12m_rs": ri(contratado), "ganhos_com_honorario_12m": len(g12h), "recebido_rs": None},
          nota="Campo 'recebido' vazio em todos os negócios e nenhuma fonte do Financeiro. Fornece: Financeiro (Luis define onde registrar o recebimento, decisão pedida em 26/10). Sem ele o ROI realizado e o backlog ficam pendentes.")
    # aging do backlog contratado (proxy do aging do PER)
    ag = Counter(); agv = Counter()
    for d in g12h + [d for d in g if (d["fechado"] or "") < ini12 and d["_hon"] is not None]:
        f = dt(d["fechado"]); m = (hoje - f).days / 30.4 if f else None
        b = "sem data" if m is None else "< 6 meses" if m < 6 else "6 a 12 meses" if m < 12 else "1 a 3 anos" if m < 36 else "> 3 anos"
        ag[b] += 1; agv[b] += d["_hon"]
    P.add("aging_per", "Aging do PER (dias desde o protocolo até a decisão)", "caixa", None, "dias", "sem fonte", "baixa", status="cinza",
          detalhe={"proxy_backlog_contratado": {b: {"n": ag[b], "honorario_rs": ri(agv[b])} for b in ag}},
          nota="Data de protocolo e situação do PER não estão no HubSpot nem em arquivo local. Fornece: Pós-venda com o time técnico (e-CAC), calendário D66. Proxy: aging do honorário contratado desde o ganho (CPC 47: potencial, não recebido).")
    P.add("glosa_por_tese", "Glosa ou indeferimento por tese", "caixa", None, "%", "sem fonte", "baixa", status="cinza",
          nota="Sem histórico de despachos decisórios por tese. Fornece: Pós-venda (despachos e manifestações de inconformidade) com o Tributário; 6 eventos 'prazo_receita' ativos no registro são o começo da série.")
    # decadência mensal (proxy pelos pareceres do técnico: período de apuração)
    dec = defaultdict(lambda: [0.0, set()]); usados = 0
    for d in N:
        if d["status"] not in ("ganho", "aberto") or not d["pipeline"].startswith("RT"): continue
        r = resumos.get(d["id"]) if resumos else None
        if not r or not r.get("periodo_apuracao") or not d["valor"]: continue
        m = re.findall(r"(\d{2})/(\d{4})", r["periodo_apuracao"])
        if len(m) < 2: continue
        a, b = int(m[0][1]) * 12 + int(m[0][0]) - 1, int(m[-1][1]) * 12 + int(m[-1][0]) - 1
        if b < a: a, b = b, a
        meses = max(b - a + 1, 1); por_mes = d["valor"] / meses; usados += 1
        for k in range(1, 4):
            ym = ym_add(hoje.isoformat()[:7], k); t = int(ym[:4]) * 12 + int(ym[5:7]) - 1 - 60  # competência que completa 5 anos neste mês
            if a <= t <= b: dec[ym][0] += por_mes; dec[ym][1].add(d["_raiz"] or d["id"])
    prox = ym_add(hoje.isoformat()[:7], 1)
    P.add("decadencia_mensal_rs", f"Crédito que decai no mês seguinte ({prox})", "caixa", ri(dec[prox][0]) if dec else None, "R$", "pareceres do técnico (resumos.json) + hubspot", "baixa",
          tol(1_000_000, 3_000_000, "<= R$ 1 mi/mês sem PER protocolado", "<= R$ 3 mi"), melhor="menor", status="cinza",
          detalhe={ym: {"credito_que_sai_rs": ri(v[0]), "clientes_n": len(v[1])} for ym, v in sorted(dec.items())} | {"negocios_com_periodo": usados},
          nota="Cinza: proxy de baixa confiança não aciona o semáforo. Crédito do negócio dividido pelos meses do período de apuração do parecer; a competência sai 5 anos depois (CTN art. 168). Não considera PER já protocolado. Fornece: Pós-venda com o time técnico (calendário D66).")
    # valor em janelas
    jan = [j for j in (janelas or {}).get("janelas", []) if j.get("prazo") and j["prazo"] >= hoje.isoformat() and (dt(j["prazo"]) - hoje).days <= 90]
    P.add("valor_em_janelas", "Valor em janelas de receita (prazo em até 90 dias)", "caixa", None, "R$", "docs/lancamento-2026/janelas.json", "baixa", status="cinza",
          detalhe={"janelas_abertas_90d": [{"id": j["id"], "prazo": j["prazo"], "janela": j["janela"][:80], "area": j.get("area_agentes"), "base_rs": None} for j in jan]},
          nota=f"{len(jan)} janelas com prazo em até 90 dias; 'base_save' sem R$ no arquivo. Fornece: Marketing (janelas_receita.py, base por Master) com o Tributário e o Jurídico.")


def bloco_risco(P, M, N, hoje, bi):
    ab = [d for d in N if d["status"] == "aberto"]; ini12 = ym_add(hoje.isoformat()[:7], -11) + "-01"
    fech12 = [d for d in N if d["status"] in ("ganho", "perdido") and (d["fechado"] or "") >= ini12]
    # probabilidade real × configurada
    wr = defaultdict(lambda: [0, 0])
    for d in fech12: wr[d["pipeline"]][0 if d["status"] == "ganho" else 1] += 1
    conf_rs = sum(d["valor"] * (d.get("prob") or 0) for d in ab)
    real_rs = sum(d["valor"] * (wr[d["pipeline"]][0] / sum(wr[d["pipeline"]]) if sum(wr[d["pipeline"]]) else 0) for d in ab)
    razao = round(real_rs / conf_rs, 2) if conf_rs else None
    P.add("prob_real_x_configurada", "Pipeline ponderado: probabilidade real ÷ configurada", "risco", razao, "x", "hubspot", "media",
          tol(0.8, 0.6, ">= 0,8 (a configurada superestima menos de 25%)", ">= 0,6"),
          detalhe={"ponderado_configurado_rs": ri(conf_rs), "ponderado_real_rs": ri(real_rs), "pipeline_aberto_rs": ri(sum(d["valor"] for d in ab)),
                   "win_rate_12m_por_pipeline": {p: pct(v[0], sum(v)) for p, v in wr.items() if sum(v) >= 10}},
          nota="Real = win rate de 12 meses do pipeline (nº) aplicado ao valor aberto; configurada = probabilidade da etapa no HubSpot. Abaixo de 1, o forecast do CRM está otimista.")
    # pipeline parado > 90 dias
    def ultima(d):  # mesma régua do dados_bi.py: última atividade (notes); sem atividade, conta desde a criação
        return dt(d["extras"].get("ultima_atividade")) or dt(d["criado"])
    par = [d for d in ab if ultima(d) and (hoje - ultima(d)).days > 90]
    P.add("pipeline_parado_90d_rs", "Pipeline parado há mais de 90 dias (R$ crédito)", "risco", sum(d["valor"] for d in par), "R$", "hubspot", "alta",
          tol(0.10 * sum(d["valor"] for d in ab), 0.25 * sum(d["valor"] for d in ab), "<= 10% do pipeline aberto", "<= 25%"), melhor="menor",
          detalhe={"n": len(par), "pct_do_aberto": pct(sum(d["valor"] for d in par), sum(d["valor"] for d in ab)), "pct_n": pct(len(par), len(ab)),
                   "por_etapa": dict(Counter(d["etapa"] for d in par).most_common(6))},
          nota="Última atividade (notes), senão a criação (a entrada na etapa foi regravada pela importação). Fila do Recuperador recebe os que couberem.")
    # concentração
    g12 = [d for d in fech12 if d["status"] == "ganho"]; tot = sum(d["valor"] for d in g12)
    porp = Counter(); [porp.update({d["parceiro"]: d["valor"]}) for d in g12]
    top = porp.most_common(5); top1 = top[0] if top else ("", 0)
    P.add("dependencia_top1_pct", "Dependência de um Master (share do fechado 12 meses)", "risco", pct(top1[1], tot), "%", "hubspot", "alta",
          tol(35, 50, "<= 35%", "<= 50%"), melhor="menor", detalhe={"master": top1[0], "fechado_12m_rs": ri(top1[1]), "top5_pct": pct(sum(v for _, v in top), tot)},
          nota="Um Master acima de 50% torna a meta refém de uma conta. Conferir com concentracao_12m do metricas.json.")
    # Masters com líquido em queda
    sc = (bi or {}).get("scorecard", [])
    queda = [s for s in sc if (s.get("ritmo_valor_vs_media_trimestral_pct") or 0) <= -20 and not s["parceiro"].startswith("Outros")]
    P.add("masters_liquido_em_queda_rs", "Líquido potencial 12m dos Masters com ritmo em queda (> 20%)", "risco", sum(s["honorario_liquido_12m_rs"] for s in queda), "R$", "dados_bi.py (scorecard)", "media",
          tol(0.25 * sum(s["honorario_liquido_12m_rs"] for s in sc), 0.5 * sum(s["honorario_liquido_12m_rs"] for s in sc), "<= 25% do líquido 12m da carteira", "<= 50%"), melhor="menor",
          detalhe={"masters_n": len(queda), "masters": [{"parceiro": s["parceiro"], "ritmo_pct": s["ritmo_valor_vs_media_trimestral_pct"], "liquido_12m_rs": s["honorario_liquido_12m_rs"], "saude": s["saude"]} for s in queda]},
          nota="Ritmo = fechado em 90 dias contra a média trimestral de 12 meses. Plano de conta com a Daniela (QBR) para cada Master em queda.")


def bloco_canal(P, M, N, hoje, bi, ps, roster):
    sc = (bi or {}).get("scorecard", []); ini12 = ym_add(hoje.isoformat()[:7], -11) + "-01"
    masters = [s for s in sc if s["parceiro"] in roster and s.get("fechado_12m_rs")]
    mg = {s["parceiro"]: pct(s["honorario_liquido_12m_rs"], s["fechado_12m_rs"]) for s in masters}
    minm = min(mg.items(), key=lambda x: x[1]) if mg else (None, None)
    P.add("margem_liquida_por_master_min", "Margem líquida por Master (menor da carteira, 12 meses)", "canal", minm[1], "%", "dados_bi.py (scorecard) + hubspot", "media",
          tol(12, 8, ">= 12% em todos os Masters", ">= 8%"), detalhe={"por_master": mg, "carteira_pct": M["margem_carteira"]["margem_liquida_pct"], "menor": minm[0]},
          nota="Líquido 12m ÷ fechado 12m, só nos ganhos com honorário informado. Repasse é o negociado por Master (D64); margem baixa pede revisão de preço, não de parceiro.")
    cons = (ps or {}).get("ativos", {}).get("consultores_dos_masters", {})
    P.add("consultores_dormentes", "Consultores dos Masters dormentes ou inativos", "canal", (cons.get("Dormente") or 0) + (cons.get("Inativo") or 0), "n", "metricas-ps (Partner Success)", "alta",
          tol(0.3 * (cons.get("consultores") or 1), 0.5 * (cons.get("consultores") or 1), "<= 30% dos consultores", "<= 50%"), melhor="menor",
          detalhe=cons, nota="Dormente = sem negócio em 90 dias com histórico; inativo = sem negócio em 180 dias. Reativação é do Partner Success com a Daniela.")
    # 2º ganho: consultores de Masters com exatamente 1 ganho
    gc = Counter(d["parceiro_bruto"] for d in N if d["status"] == "ganho" and d["_roster"] and d.get("parceiro_bruto"))
    um = [c for c, n in gc.items() if n == 1]
    P.add("consultores_sem_2o_ganho", "Consultores com um só ganho (esperando o 2º)", "canal", len(um), "n", "hubspot", "media",
          tol(3, 6, "<= 3", "<= 6"), melhor="menor", detalhe={"consultores_com_ganho": len(gc), "com_1_ganho": len(um), "com_2_ou_mais": len(gc) - len(um)},
          nota="Consultor = nome bruto do parceiro no HubSpot dentro do roster. O 2º ganho em 90 dias é o marco do onboarding (Partner Success).")
    at = M["parceiros_ativos_90d"]
    P.add("masters_ativos_90d", "Masters ativos em 90 dias", "canal", at["ativos"], "n", "hubspot", "alta", tol(at["carteira"], at["carteira"] - 1, "todos os Masters", "no máximo 1 fora"),
          detalhe=at)


def bloco_operacao(P, hoje):
    dem = ler(os.path.join(AP, "registro/demandas.json")) or {"demandas": {}}; L = list(dem["demandas"].values())
    res = [v for v in L if v.get("status") == "resolvida" and v.get("aguardando_h") is not None]
    abertas = [v for v in L if v.get("status") in ("responder", "acompanhar", "aguardando_aprovacao")]
    med = round(statistics.median(v["aguardando_h"] for v in res), 1) if res else None
    P.add("tempo_resposta_parceiro_h", "Tempo até a resposta pronta ao parceiro (mediana, horas)", "operacao", med, "dias" if False else "h", "registro/demandas.json", "media",
          tol(4, 24, "<= 4h", "<= 24h"), melhor="menor",
          detalhe={"demandas_resolvidas": len(res), "abertas": len(abertas), "maior_espera_aberta_h": max((v.get("aguardando_h") or 0) for v in abertas) if abertas else 0, "total": len(L)},
          nota="Mede a resposta preparada pelos agentes (WhatsApp e Central), não a resposta efetiva da Daniela/Jenifer/Geovana ao parceiro, que não é registrada.")
    med_r = ler(os.path.join(AP, "registro/medicao-respostas.json")) or {}
    usadas = sum(1 for v in med_r.values() if v.get("resultado") not in (None, "sem_resposta"))
    dec = ler(os.path.join(AP, "registro/decisoes-respostas.json")) or {"respostas": []}
    decididas = sum(1 for r in dec["respostas"] if r.get("resposta") and r["resposta"] != "Decidir depois")
    P.add("adocao_time_pct", "Adoção pelo time (sugestões dos agentes usadas)", "operacao", pct(usadas, len(med_r)), "%", "registro/medicao-respostas.json", "media",
          tol(50, 25, ">= 50%", ">= 25%"), status="cinza", detalhe={"sugestoes": len(med_r), "usadas": usadas, "decisoes_no_painel": len(dec["respostas"]), "decididas": decididas,
                                                                     "adiadas": len(dec["respostas"]) - decididas},
          nota="Cinza até o lançamento dos fluxos ao time (uso zero é esperado antes; 13/10). Vira semáforo na semana do lançamento. Decisões do painel: 'Decidir depois' conta como não decidida.")
    ef = ler(os.path.join(AP, "registro/entregas-faltando.json")) or {}
    esperadas = None
    try:  # lê a tabela ESPERADAS do sentinela pelo texto (importar o módulo exige o OneDrive montado)
        cand = [os.path.join(AQUI, "../../../infra/entregas_esperadas.py"), os.path.join(AP, "infra/entregas_esperadas.py")]
        src = open(next(c for c in cand if os.path.exists(c))).read()
        hora_ref = int((ef.get("hora") or datetime.now().strftime("%H:%M"))[:2])
        itens = re.findall(r'\(\s*"([\w-]+)",\s*"[^"]+",\s*(range\(0, 5\)|\[[\d, ]+\]),\s*(\d+),', src)
        esperadas = sum(1 for _, dias, hora in itens if hoje.weekday() in (range(0, 5) if dias.startswith("range") else json.loads(dias)) and hora_ref >= int(hora))
    except Exception:  # noqa: BLE001
        pass
    falt = len(ef.get("faltando", []))
    P.add("entregas_no_prazo_pct", "Entregas das rotinas no prazo (hoje)", "operacao", pct(esperadas - falt, esperadas) if esperadas else None, "%", "infra/entregas_esperadas.py (sentinela)", "alta",
          tol(100, 80, "100%", ">= 80%"), detalhe={"esperadas_ate_agora": esperadas, "faltando": [x["nome"] for x in ef.get("faltando", [])], "falhas_hoje": len(ef.get("falhas_hoje", [])), "conferido_em": f"{ef.get('data')} {ef.get('hora')}"},
          nota="Sentinela confere por dia e hora; a Central refaz o que precisa de IA. Série histórica começa em 26/10.")
    av = ler(ult(os.path.join(AP, "registro/avaliacoes/relatorio-*.json"), hoje.isoformat())) or {"areas": {}}
    A = av["areas"]; casos = sum(a["casos"] for a in A.values()); apr = sum(a["aprovados"] for a in A.values())
    media = round(statistics.mean(a["acerto"] for a in A.values()), 1) if A else None
    P.add("acerto_agentes_pct", "Acerto dos agentes nos casos de teste (média das áreas)", "operacao", media, "%", f"registro/avaliacoes/relatorio-{av.get('data')}.json", "alta",
          tol(85, 70, ">= 85%", ">= 70%"), detalhe={"areas": len(A), "casos": casos, "aprovados": apr, "aprovados_pct": pct(apr, casos), "criticos": sum(a["criticos"] for a in A.values()),
                                                   "abaixo_de_70": {k: v["acerto"] for k, v in A.items() if v["acerto"] < 70}},
          nota="Nota do auditor (infra/casos-teste.md): conteúdo 50, limpeza 30, encaminhamento 20; aprovado >= 70. Área abaixo de 70 volta ao Arquiteto de Agentes.")
    rec = ler(ult(os.path.join(AP, "celulas/geovana/recuperador/indicadores-*.json"), hoje.isoformat()))
    if rec:
        P.add("recuperador_decididos", "Recuperador: casos do lote decididos pela Geovana", "operacao", rec.get("decididas", rec.get("decididos")), "n", f"indicadores-{rec.get('data')}.json", "alta",
              tol(rec.get("casos_lote") or 20, 0.5 * (rec.get("casos_lote") or 20), "lote inteiro decidido na semana", ">= metade"),
              detalhe={"casos_lote": rec.get("casos_lote"), "honorario_esperado_lote_rs": rec.get("honorario_esperado_lote"), "fila_total": rec.get("fila_total"), "lote_enviado": rec.get("lote_enviado"), "reenvio": rec.get("reenvio")},
              nota="; ".join(rec.get("alertas", [])[:2]))


# ----------------------------------------------------------------------------- comparação com as fontes
def conferir(P, M, conf, meta, N, hoje):
    """Confere cada número recalculado contra o metricas.json do dia. Divergência vai para 'divergencias'."""
    ab = [d for d in N if d["status"] == "aberto"]
    chk = [("pipeline_aberto.n", M["pipeline_aberto"]["n"], len(ab)), ("pipeline_aberto.rs", ri(M["pipeline_aberto"]["rs"]), ri(sum(d["valor"] for d in ab))),
           ("ganhos_mes_rs", ri(M["mes_ate_hoje"]["ganhos_rs"]), meta["realizado_rs"] if hoje.month == 10 else None),
           ("cobertura_honorario.ganhos", M["cobertura_honorario_hubspot"]["ganhos"], sum(1 for d in N if d["status"] == "ganho")),
           ("fonte_cockpit.negocios", M["fonte_cockpit"]["negocios"], len(N))]
    ini12 = ym_add(hoje.isoformat()[:7], -11) + "-01"; g12 = [d for d in N if d["status"] == "ganho" and (d["fechado"] or "") >= ini12]
    top5 = {p: ri(v) for p, v in M["concentracao_12m"]["top5"]}; tot = sum(d["valor"] for d in g12)
    porp = Counter(); [porp.update({d["parceiro"]: d["valor"]}) for d in g12]
    chk.append(("concentracao_12m.top5_pct", M["concentracao_12m"]["top5_pct"], pct(sum(v for _, v in porp.most_common(5)), tot)))
    for nome, ref, calc in chk:
        if calc is None: continue
        if ref != calc and not (isinstance(ref, (int, float)) and isinstance(calc, (int, float)) and abs(ref - calc) <= max(1, abs(ref) * 0.005)):
            P.divergencias.append({"metrica": nome, "metricas_json": ref, "pacote": calc, "nota": "escopo ou janela de 12 meses diferente; conferir"})
    if conf.get("duplicados_grupos") is not None:  # Operações de Canal (29/09, aprendizados.md) contou 81 grupos por CNPJ completo + mesmo valor
        P.divergencias.append({"metrica": "duplicados_grupos", "operacoes_canal_29_09": 81, "pacote": conf["duplicados_grupos"],
                               "nota": "Métodos diferentes: Operações de Canal usa CNPJ completo + mesmo valor (R2); o saneamento do Dados & BI usa raiz do CNPJ com R1 a R4 e inclui ganhos fora do escopo. Dados & BI e Operações de Canal fecham um número único antes da mescla (D87)."})
    return {"conferido": [c[0] for c in chk], "divergencias": P.divergencias}


# ----------------------------------------------------------------------------- principal
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", default=date.today().isoformat()); ap.add_argument("--sem-saneamento", action="store_true")
    a = ap.parse_args(); hoje = date.fromisoformat(a.data)
    fm = os.path.join(DADOS, f"metricas-{a.data}.json")
    if not os.path.exists(fm): fm = ult(os.path.join(DADOS, "metricas-*.json"), a.data)
    M = json.load(open(fm)); N, baixado, fhs, roster = carregar_negocios(a.data)
    fonte_hs = f"hubspot {baixado}"
    bi = ler(ult(os.path.join(AP, "departamentos/dados/dados-bi-*.json"), a.data))
    ps = ler(ult(os.path.join(AP, "departamentos/partner-success/metricas/metricas-ps-*.json"), a.data))
    janelas = ler(os.path.join(AP, "docs/lancamento-2026/janelas.json")); resumos = ler(os.path.join(AP, "celulas/geovana/pareceres/resumos.json")) or {}
    P = Pacote(hoje)
    bloco_resultado(P, M, N, fonte_hs); meta = bloco_meta(P, M, N, hoje)
    conf = bloco_confiabilidade(P, M, N, a.sem_saneamento, hoje)
    bloco_caixa(P, M, N, hoje, janelas, resumos); bloco_risco(P, M, N, hoje, bi); bloco_canal(P, M, N, hoje, bi, ps, roster); bloco_operacao(P, hoje)
    # alertas automáticos (semáforo vermelho e dados velhos)
    for m in P.metricas:
        if m["status"] == "vermelho":
            P.alerta(f"{m['nome']}: {m['valor']} {m['unidade']} (tolerância proposta: {m['tolerancia'].get('amarelo')})", m["bloco"], "alta" if m["bloco"] in ("resultado", "caixa") else "media")
    if M["fonte_cockpit"].get("idade_dias", 0) > 1: P.alerta(f"HubSpot com {M['fonte_cockpit']['idade_dias']} dias de idade.", "dados", "media")
    for p in M.get("pendencias", []): P.alerta(p, "resultados", "baixa")
    confer = conferir(P, M, conf, meta, N, hoje)
    seg = hoje - timedelta(days=hoje.weekday())
    out = {"data": a.data, "gerado_em": datetime.now().strftime("%Y-%m-%d %H:%M"),
           "_leia_me": "Contrato: infra/gestao-schema.md §1. Status calculado pela tolerância proposta de cada métrica (origem 'proposta') até o Luis aprovar as tolerâncias; cinza = sem dado. Valores em R$ inteiros; nada de nome de cliente.",
           "periodo": {"semana_de": seg.isoformat(), "mes": a.data[:7], "trimestre": f"{hoje.year}-Q{(hoje.month - 1) // 3 + 1}"},
           "fontes": {"metricas": os.path.basename(fm), "hubspot": os.path.basename(fhs), "dados_bi": os.path.basename(bi["fonte"]) if bi else None,
                      "partner_success": ps.get("referencia") if ps else None, "negocios_no_escopo": len(N)},
           "meta": meta, "metricas": P.metricas, "confiabilidade": conf, "alertas": P.alertas, "conferencia": confer,
           "resumo_status": dict(Counter(m["status"] for m in P.metricas)),
           "revisao": {"gerente": "Controller de Resultados", "especialistas": ["Controller de Receita Reconhecida", "Analista de Margem e DRE", "Analista de Metas e Medição por Produto 2027", "Dados & BI (qualidade e saneamento)"],
                       "rodadas": 1, "areas_consultadas": ["depto-dados", "depto-partner-success", "depto-pos-venda (decadência)", "recuperador"], "aprovado": True,
                       "ajustes": "métricas sem fonte entram em cinza com quem fornece"}}
    os.makedirs(SAIDA, exist_ok=True); f = os.path.join(SAIDA, f"pacote-{a.data}.json")
    json.dump(out, open(f, "w"), ensure_ascii=False, indent=1, default=str)
    print(f); print("status:", out["resumo_status"])
    for m in P.metricas: print(f"  {m['status']:<8} {m['id']:<32} {m['valor']} {m['unidade']}")
    if P.divergencias: print("divergências:", json.dumps(P.divergencias, ensure_ascii=False))


if __name__ == "__main__":
    main()
