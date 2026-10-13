#!/usr/bin/env python3
"""Dados do protótipo do novo Painel Central Partners: lê os arquivos reais das rotinas e anonimiza clientes
(nome de cliente vira código do negócio). Parceiros (Masters) aparecem pelo nome. Saída: dados.json ao lado."""
import collections, glob, json, os, re, sys
from datetime import date, datetime, timedelta

AP = os.path.expanduser("~/agentes-partners"); AQUI = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.dirname(AQUI)
ult = lambda p: sorted(glob.glob(os.path.join(AP, p)), key=os.path.getmtime)[-1]
J = lambda p: json.load(open(p, encoding="utf-8"))
HOJE = date(2026, 10, 13)
dias = lambda iso: (HOJE - date.fromisoformat(iso[:10])).days if iso else None
cod = lambda i: f"Negócio #{str(i)[-5:]}" if i else "Negócio"

# métricas recalculadas hoje com a data efetiva (corrige a inflação da importação)
M = J(os.path.join(SCR, "res/dados/metricas-2026-10-13.json"))
BI = J(ult("departamentos/dados/dados-bi-*.json"))
CF = J(ult("departamentos/operacoes-canal/conflito-canal-*.json"))
RP = J(ult("departamentos/operacoes-canal/conferencia-repasses-*.json"))
CT = J(ult("departamentos/contratos/controle-contratos-*.json"))
RI = J(ult("celulas/geovana/recuperador/indicadores-*.json"))
FI = J(ult("celulas/geovana/recuperador/fila-*.json"))
RV = J(ult("celulas/geovana/revisor/revisor-*.json"))
PO = J(os.path.join(AP, "portal/dados.json"))
EV = [e for e in J(os.path.join(AP, "registro/eventos.json")).values() if str(e.get("ativo")) == "True" or e.get("ativo") is True]
DM = list(J(os.path.join(AP, "registro/demandas.json"))["demandas"].values())
CR = J(os.path.join(AP, "central-agentes/registro.json"))["pedidos"]
HB = J(ult("departamentos/resultados/dados/hubspot-*.json"))["negocios"]

ROT = {"comercial_parado": "Negócio comercial parado", "apresentacao_parada": "Apresentação de diagnóstico parada", "contrato_parado": "Contrato sem assinatura",
       "assinado_parado": "Assinado e não fechado", "diagnostico_parado": "Diagnóstico parado", "entrou_diagnostico": "Entrou em diagnóstico",
       "crm_incompleto": "Cadastro incompleto no CRM", "ganho_sem_bitrix": "Ganho sem execução no Bitrix", "aprovacao_parada": "Aprovação parada",
       "demanda_atrasada": "Demanda atrasada", "rotina_falhou": "Rotina com falha", "conflito_novo": "Conflito de canal novo"}
URG = {"rotina_falhou", "conflito_novo", "demanda_atrasada", "contrato_parado", "assinado_parado"}
f = lambda x: float(x) if x not in (None, "", "None") else 0.0

# ---------- caixa de entrada (tudo que pede ação)
caixa = []
for e in EV:
    if e["tipo"] == "entrou_diagnostico" and dias(e.get("primeiro")) and dias(e["primeiro"]) > 1: continue  # aviso só no 1º dia
    m = re.search(r"parceiro ([^.]+)\.", e.get("texto") or ""); par = m.group(1).strip() if m else None
    if par == "sem parceiro": par = None
    caixa.append({"id": f"S-{str(e.get('negocio') or e['titulo'])[-5:]}-{e['tipo'][:4]}", "pessoa": e["pessoa"], "tipo": ROT.get(e["tipo"], e["tipo"]),
                  "grupo": "Sentinela", "titulo": cod(e.get("negocio")) if e.get("negocio") else ROT.get(e["tipo"], e["tipo"]), "master": par,
                  "valor": f(e.get("valor")), "dias": int(f(e.get("dias"))) if e.get("dias") else dias(e.get("primeiro")),
                  "urgente": e["tipo"] in URG, "novo": e.get("primeiro") == HOJE.isoformat(), "acao": "Abrir no HubSpot"})
for d in DM:
    if d["status"] == "resolvida": continue
    caixa.append({"id": d["id"], "pessoa": d["pessoa"], "tipo": "Demanda de parceiro" if d.get("origem", "").startswith("WhatsApp") or d.get("tipo") == "whatsapp" else "Pedido aos agentes",
                  "grupo": "Demanda", "titulo": f"{d['id']} · {d.get('origem') or d.get('tipo')}", "master": None, "valor": 0, "dias": dias(d.get("aberta_em")),
                  "urgente": (dias(d.get("aberta_em")) or 0) >= 3, "novo": False, "acao": "Respondi / Encaminhei"})
for p in CR.values():
    if p["status"] == "aguardando_aprovacao":
        caixa.append({"id": p["id"], "pessoa": p["pessoa"], "tipo": "Resposta pronta para aprovar", "grupo": "Pedido", "titulo": f"{p['id']} · {p.get('codigo')}",
                      "master": (p.get("campos") or {}).get("master") if isinstance(p.get("campos"), dict) else None, "valor": 0,
                      "dias": dias(p.get("recebido")), "urgente": (dias(p.get("recebido")) or 0) >= 3, "novo": False, "acao": "Aprovar / Nova análise"})
for c in PO.get("conselho", []):
    caixa.append({"id": c["id"], "pessoa": "luis", "tipo": "Decisão do Conselho", "grupo": "Conselho", "titulo": f"{c['id']} · {c['texto'][:110]}",
                  "master": None, "valor": 0, "dias": dias(c.get("data")), "urgente": (dias(c.get("data")) or 0) > 3, "novo": False, "acao": "Aprovar / Rejeitar"})

# triagem do WhatsApp (o que o parceiro pede, Master, rota e rascunho dos agentes), ligada à demanda pela chave
sys.path.insert(0, os.path.join(AP, "lib")); import protecao
EMP = re.compile(r"\b[A-ZÀ-Ý0-9&.\-]+(?:\s+[A-ZÀ-Ý0-9&.\-]+)*\s+(?:LTDA|S/?A|EIRELI|ME|EPP)\b\.?")
anon = lambda t: EMP.sub("<EMPRESA>", protecao.limpo(t)) if t else ""
TRI = {}
for ft in sorted(glob.glob(os.path.join(AP, "celulas/whatsapp-triagem-*.json")), key=os.path.getmtime):
    for pp, PP in J(ft)["pessoas"].items():
        for i in PP.get("itens", []): TRI[f"whatsapp|{pp}|{i['chat']}"] = i
for x in caixa:
    d = next((d for d in DM if d["id"] == x["id"]), None)
    if d: x["_chave"] = d.get("chave")

# ---------- pacote pronto para encaminhar (regras reais do GLPI em infra/glpi-regras.md)
ODG = "https://gruposave-my.sharepoint.com/my?id=%2Fpersonal%2Fluis_melo_savecompany_com_br%2FDocuments%2F01%20%C2%B7%20Comercial%20e%20Parceiros%2FRelat%C3%B3rios%20das%20%C3%A1reas"
EVX = {f"S-{str(e.get('negocio') or e['titulo'])[-5:]}-{e['tipo'][:4]}": e for e in EV}
def form_trib(urg, emp, desc, bitrix, prazo):
    return (f"1) Urgência: {urg}\n2) Empresa: {emp}\n3) Descrição: {desc}\n"
            f"4) Link do Card: {bitrix or 'card do Bitrix não encontrado no HubSpot (conferir o campo ID Bitrix)'}\n5) Prazo de Entrega: {prazo}")
def pacote(x):
    e = EVX.get(x["id"]); emp = x["titulo"] if x["titulo"].startswith("Negócio") else "a empresa"; m = x.get("master") or "parceiro"
    d = x.get("dias") or 0; prazo = (HOJE + timedelta(days=2 if x["urgente"] else 5)).isoformat()
    etapa = ((e or {}).get("texto") or "").split(" · ")[1] if e and " · " in (e.get("texto") or "") else ""
    docs = []
    if e and e.get("link"): docs.append({"nome": "Card no HubSpot", "link": e["link"]})
    if e and e.get("bitrix"): docs.append({"nome": "Card no Bitrix", "link": e["bitrix"]})
    t = (e or {}).get("tipo") or x["grupo"]; P = {"glpi": None, "mensagem": None, "encaminhar": None, "docs": docs, "checklist": []}
    if t == "contrato_parado":
        P["mensagem"] = (f"Olá, tudo bem? O contrato de {emp} foi enviado há {d} dias e ainda não aparece como assinado. Você consegue confirmar com o cliente "
                         f"se ficou alguma dúvida ou se ele precisa de um novo envio? Assim que assinar, a gente segue com as próximas etapas.")
        P["checklist"] = ["Conferir na plataforma de assinatura antes de cobrar", "Se o cliente já assinou: mover o card para Contrato Assinado"]
        P["docs"].append({"nome": "Controle de Contratos (planilha)", "link": ODG})
    elif t == "assinado_parado":
        P["checklist"] = ["Mover o negócio para Negócio Fechado no HubSpot", "Conferir honorário e % do parceiro antes de fechar", "Confirmar o card de execução no Bitrix"]
    elif t == "ganho_sem_bitrix":
        P["glpi"] = {"categoria": "Tributário > Execução", "titulo": f"Execução {emp} x abrir card de execução", "urgencia": "Média",
                     "descricao": form_trib("Média", emp, f"Negócio ganho há {d} dias sem card de execução no Bitrix · o parceiro aguarda o início da execução · falta criar o card e vincular o ID Bitrix no HubSpot", None, prazo)}
    elif t in ("diagnostico_parado", "apresentacao_parada"):
        P["glpi"] = {"categoria": "Tributário > Diagnóstico", "titulo": f"Diagnóstico {emp} x andamento ({etapa or 'parado'} há {d} dias)", "urgencia": "Alta" if d > 30 else "Média",
                     "descricao": form_trib("Alta" if d > 30 else "Média", emp, f"Negócio em {etapa or 'diagnóstico'} sem movimentação há {d} dias · o parceiro {m} acompanha · pedir previsão e o que falta (documento ou análise)", (e or {}).get("bitrix"), prazo)}
        P["mensagem"] = (f"Olá, tudo bem? Sobre {emp}: o caso está em {etapa.lower() or 'análise'} e já pedimos ao time técnico a previsão. "
                         f"Assim que tivermos o retorno, te aviso. Se o cliente tiver enviado algum documento novo, me encaminha por aqui.")
        P["checklist"] = ["Conferir a etapa no HubSpot antes de abrir (muitos chamados voltam com 'já está em apresentação')", "Conferir se o parecer já está anexado ao card"]
    elif t == "comercial_parado":
        P["mensagem"] = (f"Olá, tudo bem? Passando para saber como está a conversa com {emp}. O caso está parado há {d} dias no nosso pipeline. "
                         f"Quer que a gente prepare algum material ou marque uma conversa com o cliente?")
    elif t == "crm_incompleto":
        falta = re.sub(r"\s*\(raz[aã]o oficial:[^)]*\)", "", anon(((e or {}).get("texto") or "").split(". ", 1)[-1]))[:160]
        P["checklist"] = [f"Completar no HubSpot: {falta}" if falta else "Completar os campos obrigatórios no HubSpot", "Usar a Receita (CNPJ) como fonte de segmento, CNAE e UF"]
    elif t == "aprovacao_parada":
        P["checklist"] = ["Abrir a resposta em Pedidos aos agentes", "Aprovar, pedir nova análise ou não aprovar"]
    elif x["grupo"] == "Demanda" and x["tipo"] != "Demanda de parceiro":
        P["checklist"] = ["Ver a resposta dos agentes em Pedidos aos agentes", "Aprovar, pedir nova análise ou não aprovar"]
    elif x["grupo"] == "Demanda":
        it = TRI.get(x.get("_chave")) or {}
        m = it.get("master") or m; x["master"] = x.get("master") or it.get("master")
        pede = "[pedido do parceiro, extraído da conversa: no painel real o texto aparece aqui, depois do parecer de LGPD]"; rota = it.get("rota") or ""
        P["mensagem"] = "Olá, tudo bem? Recebi o seu pedido e já encaminhei ao time responsável. Te retorno com a posição até amanhã."
        if it.get("entrega"): P["checklist"].append("Os agentes já levantaram o histórico da conversa (no painel real, o texto aparece aqui depois do parecer de LGPD)")
        if re.search(r"contrat|distrat|aditivo", rota, re.I) and not re.search(r"jur[ií]dico", rota, re.I):
            P["encaminhar"] = {"equipe": "Contratos", "texto": f"Olá, time de Contratos! O parceiro {m} pede: {pede[:300]}. Podem verificar e me retornar? Obrigada."}
        elif re.search(r"financeiro|repasse|p[oó]s-venda|faturamento", rota, re.I):
            P["encaminhar"] = {"equipe": "Financeiro", "texto": f"Olá, Financeiro! O parceiro {m} pede: {pede[:300]}. Podem verificar e me retornar? Obrigada."}
        elif re.search(r"jur[ií]dico", rota, re.I) or not rota:
            P["glpi"] = {"categoria": "Jurídico > Demandas Diversas", "titulo": "Demandas Diversas - Jurídico <EMPRESA> x <assunto do pedido>", "urgencia": "Alta" if x["urgente"] else "Média",
                         "descricao": f"DADOS\n1) Setor Solicitante: MASTER\n2) Parceiro Solicitante: {m}\nINFORMAÇÕES GERAIS\n1) Assunto: {pede[:120]}\n2) Classe: Interna\n3) Informações Adicionais: {pede[:400]}\n4) Documentos: anexar o que veio na conversa"}
        elif re.search(r"t[eé]cnic|geovana|tribut|diagn", rota, re.I):
            P["glpi"] = {"categoria": "Tributário > Diagnóstico", "titulo": "Diagnóstico <EMPRESA> x <assunto do pedido>", "urgencia": "Alta" if x["urgente"] else "Média",
                         "descricao": form_trib("Alta" if x["urgente"] else "Média", "<EMPRESA>", pede[:400], None, prazo)}
        if rota: P["checklist"].insert(0, f"Rota sugerida pelos agentes: {anon(rota)[:120]}")
        P["checklist"] += ["Conferir o texto da conversa antes de enviar", "Contrato ou distrato do parceiro vai a Contratos e repasse vai ao Financeiro, sem chamado"]
    elif x["grupo"] == "Conselho":
        P["checklist"] = ["Ler a recomendação na ata", "Aprovar, aprovar com ajuste ou rejeitar"]
    return P

# ---------- Masters
masters = [{k: r.get(k) for k in ("parceiro", "saude", "criados_90d", "ganhos_90d", "fechado_90d_rs", "ritmo_valor_vs_media_trimestral_pct",
            "ritmo_entrada_vs_media_pct", "ganhos_12m", "fechado_12m_rs", "conversao_12m_pct", "ticket_12m_rs", "ciclo_mediano_dias",
            "honorario_liquido_12m_rs", "abertos", "abertos_rs", "abertos_parados", "ultimo_negocio_criado")} for r in BI["scorecard"]]
for m in masters:
    nome = m["parceiro"]
    m["demandas"] = sum(1 for x in caixa if x["grupo"] == "Demanda" and x.get("master") == nome)
    m["alertas"] = sum(1 for x in caixa if x["grupo"] == "Sentinela" and x.get("master") == nome)
    rp = next((r for r in RP.get("por_parceiro", []) if r.get("Parceiro") == nome), {})
    m["repasse"] = {"ok": rp.get("OK"), "revisar": rp.get("Revisar"), "bloqueado": rp.get("Bloqueados"), "calculado": round(rp.get("Repasse calculado (R$)") or 0)}
    m["dias_sem_negocio"] = dias(m.get("ultimo_negocio_criado"))

# ---------- série mensal (12 meses) e financeiro
serie = [{"mes": k, **{kk: round(vv) for kk, vv in v.items()}} for k, v in sorted(M["serie_mensal"].items())]
lucro = [{"mes": x["mes"], "custo": x["custo"], "base": x["custo_base"], "hb": x["amostra"]["honorario_bruto"], "hl": x["amostra"]["honorario_liquido"]}
         for x in (M.get("lucro_roi_mensal") or {}).get("meses", [])]
# win rate mensal
wr = {}
for n in HB:
    if n["status"] in ("ganho", "perdido") and n.get("fechado"):
        k = n["fechado"][:7]; wr.setdefault(k, [0, 0]); wr[k][0 if n["status"] == "ganho" else 1] += 1
winrate = [{"mes": k, "pct": round(100 * g / (g + p), 1)} for k, (g, p) in sorted(wr.items()) if k >= serie[0]["mes"] and g + p]
# funil atual (abertos por etapa) e envelhecimento
ab = [n for n in HB if n["status"] == "aberto"]
funil = collections.Counter(n["etapa"] for n in ab).most_common(10)
faixas = collections.Counter()
for n in ab:
    d = dias((n.get("extras") or {}).get("entrou_etapa") or n.get("criado")) or 0
    faixas["0–30" if d <= 30 else "31–60" if d <= 60 else "61–90" if d <= 90 else "91–180" if d <= 180 else "> 180"] += 1
# BDR: novos por semana (8 semanas) e entrada em diagnóstico
sem = lambda iso: (date.fromisoformat(iso[:10]) - timedelta(days=date.fromisoformat(iso[:10]).weekday())).isoformat()
ini8 = (HOJE - timedelta(days=HOJE.weekday() + 7 * 7)).isoformat()
bdr = collections.Counter(sem(n["criado"]) for n in HB if n.get("pipeline") == "Save Partners - BDR/SDR" and n.get("criado", "") >= ini8)
novos = collections.Counter(sem(n["criado"]) for n in HB if n.get("criado", "") >= ini8)
diag = collections.Counter(sem(e["primeiro"]) for e in J(os.path.join(AP, "registro/eventos.json")).values() if e["tipo"] == "entrou_diagnostico" and e.get("primeiro", "") >= ini8)
semanas = sorted({(date.fromisoformat(ini8) + timedelta(days=7 * i)).isoformat() for i in range(8)})
cobertura = {}
for n in HB:
    if n["status"] == "ganho" and n.get("parceiro") in {m["parceiro"] for m in masters}:
        uf = (n.get("extras") or {}).get("uf")
        if uf: cobertura.setdefault(n["parceiro"], collections.Counter())[uf] += 1
cobertura = {k: v.most_common(4) for k, v in cobertura.items()}

# ---------- Recuperador (lote anonimizado) e Revisor
lote = [{"caso": cod(re.sub(r"\D", "", r.get("link") or "")), "parceiro": r.get("parceiro"), "tipo": r.get("tipo"), "segmento": r.get("segmento (matriz)") or r.get("segmento"),
         "uf": r.get("uf"), "esperado": r.get("honorário esperado (look-alike)"), "taxa": r.get("taxa de sucesso dos parecidos"), "aderencia": r.get("aderência"),
         "saldo": r.get("saldo credor (urgente até 30/11)"), "docs": r.get("documentos a pedir"), "sinal": r.get("sinal do parecer")}
        for r in FI["top"] if r.get("lote") == 1][:20]
por_tese = sorted([{"tese": k, "n": v.get("n", 0), "alta": v.get("alta", 0)} for k, v in (RV["resumo"].get("por_tese") or {}).items()], key=lambda x: -x["n"])
NT = {"B": "Manutenção e ressarcimento", "CST": "Erro de CST", "EX_ICMS": "Exclusão do ICMS", "C": "Crédito presumido", "ST_REST": "Restituição de ICMS-ST", "PREV": "Previdenciárias", "EX_ST": "Exclusão do ICMS-ST"}
for t in por_tese: t["tese"] = NT.get(t["tese"], t["tese"])

for x in caixa: x["pacote"] = pacote(x)
# ================= ampliação: tudo o que já temos de dados =================
import hashlib
_pp = [os.path.join(AP, "departamentos/operacoes-canal/percentual-parceiros.json"), os.path.join(AP, ".claude/worktrees/amazing-kirch-442f46/departamentos/operacoes-canal/percentual-parceiros.json")]
PCT = J(next(x for x in _pp if os.path.exists(x)))["parceiros"]  # % oficial de repasse (cadastro dos parceiros)
pc = lambda v: (float(v) * (100 if float(v) <= 1 else 1)) if v not in (None, "") else None
NOMES_M = {m["parceiro"] for m in masters}
def comissao(n):
    """Honorário contratado (valor × % Save) × % do parceiro. Faltando, usa o típico do cadastro (marcado como estimado)."""
    p = PCT.get(n.get("parceiro") or "", {}); v = n.get("valor") or 0
    hs = pc(n.get("hContr")); est = False
    if not hs: hs = p.get("honorario_save_tipico_pct"); est = True
    hp_neg = pc(n.get("hParc"))
    if p.get("confirmado"): hp = p["pct_parceiro"]                  # % oficial do cadastro vale para todos os negócios
    else:
        hp = hp_neg
        if not hp: hp = p.get("pct_parceiro"); est = True
    if not (v and hs and hp): return None, None, est
    hon = v * hs / 100; return hon, hon * hp / 100, est
# ficha 360 por parceiro: série 12m, abertos por etapa, honorário e comissão (real × estimada)
ini12 = (HOJE.replace(day=1) - timedelta(days=330)).replace(day=1).isoformat()[:7]
ficha = {}
for nome in NOMES_M:
    ns = [n for n in HB if n.get("parceiro") == nome]
    s = collections.Counter(); hon = com = com_est = pot = 0.0; n_est = n_real = diverg = 0
    for n in ns:
        if n["status"] == "ganho" and (n.get("fechado") or "")[:7] >= ini12:
            s[n["fechado"][:7]] += n.get("valor") or 0
            h, c, e = comissao(n)
            if c: hon += h; com += c; n_est += e; n_real += not e
            hn = pc(n.get("hParc")); po = PCT.get(nome, {})
            if po.get("confirmado") and hn and abs(hn - po["pct_parceiro"]) > 0.5: diverg += 1
        if n["status"] == "aberto":
            h, c, e = comissao(n); pot += c or 0
    ficha[nome] = {"serie": [[k, round(s.get(k, 0))] for k in sorted({x["mes"] for x in serie})[-12:]],
                   "etapas": collections.Counter(n["etapa"] for n in ns if n["status"] == "aberto").most_common(6),
                   "honorario_12m": round(hon), "comissao_12m": round(com), "comissao_potencial_aberto": round(pot), "base_real": n_real, "base_estimada": n_est, "divergencias": diverg,
                   "pct": PCT.get(nome, {}).get("pct_parceiro"), "pct_confirmado": PCT.get(nome, {}).get("confirmado"), "pct_consistencia": PCT.get(nome, {}).get("consistencia_pct"),
                   "uf": cobertura.get(nome, []), "contratos": sum(1 for n in ns if n["status"] == "aberto" and n["etapa"] in ("Contrato Enviado", "Contrato Assinado", "Pendência Fechamento")),
                   "conflitos": sum(v for k, v in CF.get("pares_de_canais", {}).items() if nome in k)}
# parceiros esfriando: Masters com ritmo muito abaixo ou sem negócio novo; indicadores fora do roster que pararam
esfriando = [{"parceiro": m["parceiro"], "tipo": "Master", "dias": m["dias_sem_negocio"], "ritmo": m["ritmo_valor_vs_media_trimestral_pct"], "ganhos_12m": m["ganhos_12m"],
              "uf": [u for u, _ in cobertura.get(m["parceiro"], [])][:3]}
             for m in masters if (m["ritmo_valor_vs_media_trimestral_pct"] or 0) < -50 or (m["dias_sem_negocio"] or 0) > 30]
ind = collections.defaultdict(list)
for n in HB:
    pb = n.get("parceiro_bruto") or ""
    if n.get("parceiro", "").startswith("Outros") and pb: ind[pb].append(n)
for pb, ns in ind.items():
    g12 = [n for n in ns if n["status"] == "ganho" and (n.get("fechado") or "") >= (HOJE - timedelta(days=365)).isoformat()]
    ult = max((n.get("criado") or "") for n in ns)
    if len(g12) >= 2 and dias(ult) and dias(ult) > 60:
        esfriando.append({"parceiro": "Indicador #" + hashlib.sha1(pb.encode()).hexdigest()[:4].upper(), "tipo": "Indicador", "dias": dias(ult), "ritmo": None, "ganhos_12m": len(g12), "uf": []})
esfriando.sort(key=lambda x: -(x["dias"] or 0))
# agenda de prazos (assunto de Receita detectado na triagem; data exata a confirmar no documento)
prazos = []
for k, i in TRI.items():
    t = (i.get("o_que_pede") or "") + " " + (i.get("entrega") or "")
    mt = re.search(r"despacho|intima|manifesta|cnd|certid|per/?dcomp|indeferi|compensa[çc][ãa]o de of", t, re.I)
    if not mt: continue
    tipo = {"despacho": "Despacho decisório", "intima": "Intimação", "manifesta": "Manifestação de inconformidade", "cnd": "CND", "certid": "CND", "indeferi": "PER indeferido"}.get(mt.group(0).lower()[:8].rstrip(), "Comunicado da Receita")
    prazos.append({"id": "R-" + hashlib.sha1(k.encode()).hexdigest()[:5].upper(), "pessoa": k.split("|")[1], "master": i.get("master"), "tipo": tipo,
                   "prazo_txt": i.get("prazo") or "a confirmar no documento", "rota": anon(i.get("rota") or "")[:80]})
vistos_p = {}; [vistos_p.setdefault((p["master"], p["tipo"]), p) for p in prazos]; prazos = list(vistos_p.values())
prazos.insert(0, {"id": "R-CAFE", "pessoa": "geovana", "master": "—", "tipo": "PER indeferido · manifestação de inconformidade", "prazo_txt": "≈ 04/11/2026 (backlog)", "data": "2026-11-04", "rota": "Jurídico > Comunicados RFB"})
for p in prazos:
    if p.get("data"): p["restam"] = (date.fromisoformat(p["data"]) - HOJE).days
# documentos por negócio (diagnóstico e apresentação): o que já está no card e o documento que decide cada lacuna
lac = collections.defaultdict(list)
for l in RV.get("lacunas", []):
    if l.get("documento que decide"): lac[re.sub(r"\D", "", l.get("link") or "")[-11:]].append((l.get("tese"), l.get("documento que decide"), l.get("prioridade")))
docs_neg = []
for n in HB:
    if n["status"] != "aberto" or n["etapa"] not in ("Apresentação de Diagnóstico", "Em Diagnóstico", "Análise de Documentos", "Documentação Pendente", "Análise com Pendência", "Estudo Inicial"): continue
    x = n.get("extras") or {}
    tem = {"Procuração e-CAC": bool(x.get("ecac")), "Anexo de diagnóstico": bool(x.get("anexo_diagnostico")), "Parecer RT": bool(x.get("parecer_rt")), "Parecer jurídico": bool(x.get("parecer_juridico"))}
    falta = [k for k, v in tem.items() if not v and k != "Parecer jurídico"]
    decide = lac.get(str(n["id"])[-11:], [])[:3]
    if falta or decide:
        docs_neg.append({"caso": cod(n["id"]), "parceiro": n.get("parceiro"), "etapa": n["etapa"], "dias": dias(x.get("entrou_etapa") or n.get("criado")), "tem": tem, "falta": falta,
                         "decide": [{"tese": t, "doc": d, "prio": pr} for t, d, pr in decide], "valor": n.get("valor") or 0})
docs_neg.sort(key=lambda d: (-len(d["decide"]), -(d["dias"] or 0)))
# busca única: código, parceiro, etapa e raiz do CNPJ em hash (o CNPJ não vai para a página)
H8 = lambda r: hashlib.sha256(("save:" + r).encode()).hexdigest()[:16]
busca = []
for n in HB:
    c = re.sub(r"\D", "", str((n.get("extras") or {}).get("cnpj") or "")); r8 = c.zfill(14)[:8] if c else None
    busca.append([str(n["id"])[-5:], n.get("parceiro") or "", n.get("etapa") or "", n["status"], round(n.get("valor") or 0), (n.get("extras") or {}).get("uf") or "", (n.get("segmento") or "")[:40], (n.get("criado") or "")[:10], H8(r8) if r8 else ""])
# histórico: demandas resolvidas e tempo até resolver
hist = []
for d in DM:
    if d["status"] != "resolvida": continue
    fim = next((e["quando"] for e in reversed(d.get("eventos") or []) if "resolv" in e.get("evento", "")), d.get("atualizada_em"))
    if not fim or not d.get("aberta_em"): continue
    h = (datetime.fromisoformat(fim[:16]) - datetime.fromisoformat(d["aberta_em"][:16])).total_seconds() / 3600
    hist.append({"id": d["id"], "pessoa": d["pessoa"], "origem": d.get("origem"), "aberta": d["aberta_em"][:10], "resolvida": fim[:10], "horas": round(max(h, 0), 1)})
hist.sort(key=lambda x: x["resolvida"], reverse=True)
med = lambda xs: sorted(xs)[len(xs) // 2] if xs else None
tempo = {p: {"mediana_h": med([x["horas"] for x in hist if x["pessoa"] == p]), "n": sum(1 for x in hist if x["pessoa"] == p)} for p in ("daniela", "jenifer", "geovana", "luis")}
# saúde da operação (logs das rotinas nas últimas 24 h)
saude_op = {}
desde = (datetime(2026, 10, 13, 15, 0) - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
for l in open(os.path.join(AP, "logs/partners.log"), errors="ignore"):
    m_ = re.match(r"(\S+ \S+) \[([^\]:]+)[^\]]*\] (.*)", l.strip())
    if m_ and m_.group(1) >= desde: saude_op[m_.group(2)] = {"quando": m_.group(1)[5:16], "ok": "ERRO" not in m_.group(3), "msg": m_.group(3)[:80]}
operacao = {"rotinas": saude_op, "email_pausado": os.path.exists(os.path.join(AP, ".email-pausado")), "hubspot": BI.get("baixado_em"),
            "backup": re.search(r"(\d{4}-\d{2}-\d{2})", sorted(glob.glob(os.path.expanduser("~/Library/CloudStorage/OneDrive-SAVECOMPANY/Backups/agentes-partners/*.tar.gz")))[-1]).group(1)}
# biblioteca: respostas-modelo e materiais
import urllib.parse
web = lambda rel: "https://gruposave-my.sharepoint.com/my?id=" + urllib.parse.quote("/personal/luis_melo_savecompany_com_br/Documents/" + rel, safe="")
biblioteca = {"respostas": [
    {"situacao": "Contrato enviado e não assinado", "texto": "Olá, tudo bem? O contrato de <EMPRESA> foi enviado há <N> dias e ainda não aparece como assinado. Você consegue confirmar com o cliente se ficou alguma dúvida ou se ele precisa de um novo envio?"},
    {"situacao": "Diagnóstico em andamento", "texto": "Olá, tudo bem? Sobre <EMPRESA>: o caso está em análise e já pedimos ao time técnico a previsão. Assim que tivermos o retorno, te aviso."},
    {"situacao": "Pedido recebido e encaminhado", "texto": "Olá, tudo bem? Recebi o seu pedido e já encaminhei ao time responsável. Te retorno com a posição até amanhã."},
    {"situacao": "Documento pendente", "texto": "Olá, tudo bem? Para seguirmos com <EMPRESA>, precisamos de: <DOCUMENTOS>. Consegue pedir ao cliente e me encaminhar por aqui?"},
    {"situacao": "Reativação de parceiro", "texto": "Olá, tudo bem? Faz um tempo que não falamos sobre novos casos. Separamos algumas empresas da sua região com perfil parecido com clientes que já ganhamos juntos. Podemos marcar 20 minutos esta semana?"},
    {"situacao": "Comunicado da Receita recebido", "texto": "Olá, tudo bem? Recebemos o comunicado da Receita de <EMPRESA>. Para o Jurídico seguir (ou não) com a manifestação, precisamos da autorização do cliente e da data de ciência. Consegue confirmar?"}],
  "materiais": [{"nome": "Kit Crédito Internacional (rascunho)", "link": web("03 · Produtos e Projetos/Crédito Internacional/Marketing")},
                {"nome": "Programa de Parceiros", "link": web("01 · Comercial e Parceiros/Programa de Parceiros")},
                {"nome": "Manual dos Agentes", "link": web("04 · Gestão, Metas e Estratégia/Central de Agentes")},
                {"nome": "Relatórios das áreas", "link": web("01 · Comercial e Parceiros/Relatórios das áreas")},
                {"nome": "Padrão de marca (logos e modelos)", "link": web("06 · Marketing e Apresentações/Marca")}]}

# ================= recorrência (regras V5, L11, L13 e parecer "já aproveitado" — Tributário 29/09; Revisor "grupo já é cliente")
def raiz(n):
    c = re.sub(r"\D", "", str((n.get("extras") or {}).get("cnpj") or "")); return c.zfill(14)[:8] if c else None
meses = lambda a, b: (b.year - a.year) * 12 + (b.month - a.month)
grupos = collections.defaultdict(list)
for n in HB:
    r8 = raiz(n)
    if r8: grupos[r8].append(n)
CAFE = re.compile(r"caf[eé]", re.I)
recorr = []
for r8, ns in grupos.items():
    gs = [n for n in ns if n["status"] == "ganho" and n.get("fechado")]
    if not gs: continue
    ult = max(gs, key=lambda n: n["fechado"]); x = ult.get("extras") or {}
    if x.get("regime") == "Simples Nacional" or CAFE.search(ult.get("segmento") or ""): continue          # V2 Simples · V3 café
    if any(n["status"] == "aberto" for n in ns): continue                                              # V6: já há negócio aberto no grupo
    mn = meses(date.fromisoformat(ult["fechado"][:10]), HOJE)
    teses = sorted({str(n.get("variante")) for n in gs if n.get("variante")})
    cred = sum(n.get("valor") or 0 for n in gs if n["fechado"] == ult["fechado"]) or (ult.get("valor") or 0)
    pot_cred = cred / 60 * min(mn, 60) if mn >= 6 else 0
    p = PCT.get(ult.get("parceiro") or "", {})
    hs = pc(ult.get("hContr")) or p.get("honorario_save_tipico_pct") or 0
    hp = p["pct_parceiro"] if p.get("confirmado") else (pc(ult.get("hParc")) or p.get("pct_parceiro") or 0)
    sinais = []
    if any(re.search(r"aquisi|insumo|cr[eé]dito", t, re.I) for t in teses): sinais.append("Saldo credor até 31/12/2026 (L13)")
    if x.get("regime") == "Lucro Real": sinais.append("Lucro Real: revisão CBS/IBS (Planejamento 2027)")
    if mn > 54: sinais.append("Risco de decadência: períodos antigos saindo da janela")
    if re.search(r"hortifr|frutas|verduras|legumes|carnes|pescado|latic|ovos", ult.get("segmento") or "", re.I): sinais.append("Revende produto de alíquota zero: só tese B, conferir (L7)")
    if not teses: sinais.append("Tese do ganho anterior não registrada no HubSpot: conferir no parecer o que já foi feito")
    recorr.append({"caso": cod(ult["id"]), "parceiro": ult.get("parceiro") or "—", "regime": x.get("regime"), "uf": x.get("uf"), "segmento": (ult.get("segmento") or "")[:40],
                   "ultimo_ganho": ult["fechado"][:10], "meses_novos": mn, "elegivel": mn >= 6, "faltam": max(0, 6 - mn), "teses": teses[:4], "n_ganhos": len(gs),
                   "credito_anterior": round(cred), "potencial_credito": round(pot_cred), "potencial_honorario": round(pot_cred * hs / 100), "potencial_repasse": round(pot_cred * hs / 100 * hp / 100),
                   "sinais": sinais, "regra": "V5/L11: ≥ 6 meses novos desde o último período recuperado" if mn >= 6 else f"V5: menos de 6 meses novos (faltam {6 - mn})"})
recorr.sort(key=lambda r: (not r["elegivel"], -r["potencial_honorario"]))
# Revisor: diagnósticos em andamento de grupos que já são clientes (recorrência já em curso)
rev_rec = [{"caso": cod(re.sub(r"\D", "", r.get("link") or "")[-11:]), "parceiro": r.get("parceiro"), "etapa": r.get("etapa"), "lacunas": r.get("lacunas"),
            "lacunas_alta": r.get("lacunas alta"), "teses_grupo": str(r.get("grupo já é cliente"))[:120]}
           for r in RV.get("revisao", []) if r.get("grupo já é cliente") not in (None, "", False, "não", "Não")]
rec_parc = {}
for r in recorr:
    a = rec_parc.setdefault(r["parceiro"], {"elegiveis": 0, "aguardar": 0, "pot_credito": 0, "pot_honorario": 0, "pot_repasse": 0, "em_diagnostico": 0})
    if r["elegivel"]: a["elegiveis"] += 1; a["pot_credito"] += r["potencial_credito"]; a["pot_honorario"] += r["potencial_honorario"]; a["pot_repasse"] += r["potencial_repasse"]
    else: a["aguardar"] += 1
for r in rev_rec:
    rec_parc.setdefault(r["parceiro"] or "—", {"elegiveis": 0, "aguardar": 0, "pot_credito": 0, "pot_honorario": 0, "pot_repasse": 0, "em_diagnostico": 0})["em_diagnostico"] += 1
for nome in ficha:
    ficha[nome]["recorrencia"] = rec_parc.get(nome, {})
    ficha[nome]["recorrencia_top"] = [r for r in recorr if r["parceiro"] == nome and r["elegivel"]][:5]

ev_por = collections.Counter((e["pessoa"], e["tipo"]) for e in EV)
P = {
    "atualizado": "13/10/2026 07:32", "exemplo": True,
    "caixa": sorted(caixa, key=lambda x: (not x["urgente"], -(x["dias"] or 0))),
    "masters": sorted(masters, key=lambda m: m["saude"] or 0),
    "serie": serie, "winrate": winrate, "lucro": lucro, "funil": funil, "idade_abertos": [[k, faixas[k]] for k in ("0–30", "31–60", "61–90", "91–180", "> 180")],
    "kpi": {"win_rate_3m": M.get("win_rate_3m"), "ticket_3m": M.get("ticket_valor_3m"), "pipeline": M.get("pipeline_aberto"), "concentracao": M.get("concentracao_12m"),
            "mes": M.get("mes_ate_hoje"), "ano": M.get("crescimento_acumulado_ano"), "ciclo": CF.get("ciclo"), "mix": (M.get("mix_teses") or {}).get("top", [])[:8],
            "sem_tese": (M.get("mix_teses") or {}).get("ganhos_sem_tese"), "qualidade": BI.get("indice_qualidade_ganhos"), "inconsistencias": BI.get("inconsistencias"),
            "conflito": {"alta": CF["por_severidade"].get("Alta"), "mxm": CF.get("master_x_master"), "valor": CF.get("valor_em_conflito_rs"), "raizes": CF.get("raizes_com_mais_de_um_canal")},
            "repasse": RP.get("status"), "repasse_calc": RP.get("repasse_calculado_rs"), "contratos": CT.get("em_contrato"),
            "conselho": len(PO.get("conselho", [])), "pedidos_prontos": sum(1 for p in CR.values() if p["status"] == "aguardando_aprovacao"), "chamados": 5},
    "jenifer": {"semanas": semanas, "bdr": [bdr.get(s, 0) for s in semanas], "novos": [novos.get(s, 0) for s in semanas], "diag": [diag.get(s, 0) for s in semanas],
                "crm_incompleto": sum(1 for e in EV if e["tipo"] == "crm_incompleto"), "duplicidade": BI.get("duplicidade_abertos"), "cobertura": cobertura,
                "conflitos_alta": CF["por_severidade"].get("Alta")},
    "geovana": {"lote": lote, "fila": RI.get("fila_total"), "esperado_fila": RI.get("honorario_esperado_fila_rs"), "esperado_lote": RI.get("honorario_esperado_lote_rs"),
                "decididas": RI.get("decididas"), "revisor": {k: RV["resumo"].get(k) for k in ("selecionados", "revisados", "lacunas")} | {"alta": sum(t["alta"] for t in por_tese)},
                "por_tese": por_tese, "diag_parado": ev_por[("geovana", "diagnostico_parado")], "aprov_parada": sum(v for (p, t), v in ev_por.items() if t == "aprovacao_parada")},
    "ficha": ficha, "esfriando": esfriando, "prazos": prazos, "docs": docs_neg[:120], "n_docs": len(docs_neg), "busca": busca, "hist": hist[:80], "tempo": tempo,
    "recorrencia": {"fila": [r for r in recorr if r["elegivel"]][:150], "aguardar": [r for r in recorr if not r["elegivel"]][:40],
                    "n_elegiveis": sum(r["elegivel"] for r in recorr), "n_aguardar": sum(not r["elegivel"] for r in recorr),
                    "pot_credito": sum(r["potencial_credito"] for r in recorr), "pot_honorario": sum(r["potencial_honorario"] for r in recorr), "pot_repasse": sum(r["potencial_repasse"] for r in recorr),
                    "revisor": rev_rec[:60], "n_revisor": len(rev_rec)},
    "operacao": operacao, "biblioteca": biblioteca, "conselho": [{"id": c["id"], "data": c["data"], "texto": c["texto"][:160]} for c in PO.get("conselho", [])],
}
json.dump(P, open(os.path.join(AQUI, "dados.json"), "w", encoding="utf-8"), ensure_ascii=False, default=str)
print("caixa:", len(P["caixa"]), collections.Counter(x["pessoa"] for x in P["caixa"]), "· masters:", len(masters), "· lote:", len(lote), "· bytes:", os.path.getsize(os.path.join(AQUI, "dados.json")))
