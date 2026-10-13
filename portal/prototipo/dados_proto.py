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
}
json.dump(P, open(os.path.join(AQUI, "dados.json"), "w", encoding="utf-8"), ensure_ascii=False, default=str)
print("caixa:", len(P["caixa"]), collections.Counter(x["pessoa"] for x in P["caixa"]), "· masters:", len(masters), "· lote:", len(lote), "· bytes:", os.path.getsize(os.path.join(AQUI, "dados.json")))
