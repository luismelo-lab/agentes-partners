#!/usr/bin/env python3
"""Dados de exemplo das 3 opções de layout da Central Partners v2 (23/10/2026).

Reais: áreas, especialistas, entregas, rotinas, pastas e pessoas (portal/diretorio.json, sem cliente), números
agregados por pessoa, alertas das áreas, decisões do Conselho sem nome de cliente e janelas de receita.
Fictícios e marcados como exemplo: pedidos, demandas, chamados, lote e arquivos do dia (sem nome de cliente).
Masters aparecem como "Master 1" a "Master 9".
Uso: python3 portal/opcoes/gerar_exemplo.py → portal/opcoes/exemplo-dados.js
"""
import json, os

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(AQUI))
DIR = json.load(open(os.path.join(REPO, "portal/diretorio.json")))
D = json.load(open(os.path.join(REPO, "portal/dados.json")))
J = json.load(open(os.path.join(REPO, "docs/lancamento-2026/janelas.json")))

DEC_OK = ["D9", "D11", "D15", "D30", "D31"]   # decisões sem nome de cliente
dec = [{"id": c["id"], "data": c["data"], "texto": c["texto"][:170]} for c in D.get("conselho", []) if c["id"] in DEC_OK]
masters = [{"parceiro": f"Master {i + 1}", "saude": m["saude"], "abertos": m["abertos"], "parados": m["parados"], "ganhos_90d": m["ganhos_90d"]}
           for i, m in enumerate(sorted(D["gestao"]["masters"], key=lambda m: m["saude"]))]
janelas = D.get("janelas") or [{"id": j["id"], "janela": j["janela"], "prazo": j["prazo"], "prazo_texto": j.get("prazo_texto") or "depende de ato sem data", "produto": j["produto_tese"].split(";")[0]}
                               for j in J["janelas"]]


def h(quando, evento, por, nota=""): return {"quando": quando, "evento": evento, "por": por, "nota": nota}


R3 = lambda resumo, secoes, tambem, falta: {"versao": 1, "resumo": resumo, "secoes": secoes, "tambem": tambem, "falta": falta}
PEDIDOS = [
    {"id": "P-0031", "area": "depto-operacoes-canal", "entrega": "Conferência de repasses", "solicitante": "daniela", "status": "aguardando_aprovacao", "criado_em": "2026-10-22T09:12",
     "precisa": "Conferir o repasse de outubro do Master 2 antes de responder ao parceiro.", "uso": "Resposta ao parceiro", "prazo": "2026-10-24",
     "historico": [h("2026-10-22T09:12", "Pedido direto à área", "daniela"), h("2026-10-22T09:40", "Em análise", "Operações de Canal"), h("2026-10-22T15:05", "Resposta v1 pronta", "Operações de Canal")],
     "resposta": R3("Dos 14 ganhos do mês, 11 batem com o percentual negociado. Três estão sem o campo de honorário preenchido e ficam fora do cálculo até o dado chegar.",
                    [{"titulo": "O que você pediu", "texto": "- 11 ganhos conferidos, sem divergência\n- 3 ganhos sem % de honorário no card\n- Rascunho de resposta ao parceiro pronto, sem valores finais"}],
                    "Os 3 ganhos sem dado também travam o extrato do mês; vale pedir o preenchimento ao Financeiro.", "% de honorário de 3 ganhos: quem fornece é o Financeiro.")},
    {"id": "P-0032", "area": "celula-jenifer", "entrega": "Lista de prospects por Master", "solicitante": "jenifer", "status": "em_analise", "criado_em": "2026-10-23T08:30",
     "precisa": "Lista de 40 empresas do Lucro Real em transporte, no PR, para o Master 5.", "uso": "Prospecção", "prazo": "2026-10-27",
     "historico": [h("2026-10-23T08:30", "Pedido direto à área", "jenifer"), h("2026-10-23T09:02", "Em análise", "Central BDR")]},
    {"id": "P-0033", "area": "depto-tributario", "entrega": "", "solicitante": "geovana", "status": "novo", "criado_em": "2026-10-23T10:15",
     "precisa": "Pré-análise de crédito de insumos para indústria de alimentos no Lucro Real.", "uso": "Reunião", "prazo": "",
     "historico": [h("2026-10-23T10:15", "Pedido direto à área", "geovana")]},
    {"id": "P-0034", "area": "depto-contratos", "entrega": "Controle de contratos", "solicitante": "daniela", "status": "concluido", "criado_em": "2026-10-20T11:00",
     "precisa": "Quais contratos do Master 1 estão parados na assinatura?", "uso": "Decisão interna", "prazo": "",
     "historico": [h("2026-10-20T11:00", "Pedido direto à área", "daniela"), h("2026-10-20T14:20", "Resposta v1 pronta", "Contratos"), h("2026-10-21T08:10", "Aprovado", "daniela")],
     "resposta": R3("Dois contratos estão sem assinatura há mais de 10 dias.", [{"titulo": "O que você pediu", "texto": "- 2 contratos parados na plataforma de assinatura\n- Lembrete ao signatário em rascunho"}],
                    "Um deles vence a proposta em 5 dias.", "nada")},
    {"id": "P-0035", "area": "", "entrega": "", "solicitante": "luis", "status": "em_analise", "criado_em": "2026-10-23T07:50",
     "precisa": "Quais áreas precisam participar do lançamento dos agentes ao time na semana que vem?", "uso": "Decisão interna", "prazo": "2026-10-26",
     "historico": [h("2026-10-23T07:50", "Pedido à Central", "luis"), h("2026-10-23T08:05", "Triagem: Pessoas, Qualidade e Marketing", "Central de Agentes")]},
    {"id": "P-0036", "area": "depto-juridico", "entrega": "Controle de prazos", "solicitante": "daniela", "status": "aguardando_aprovacao", "criado_em": "2026-10-22T16:40",
     "precisa": "Um cliente do Master 4 recebeu despacho decisório. Qual é o prazo e o que pedir ao advogado?", "uso": "Resposta ao parceiro", "prazo": "2026-10-23",
     "historico": [h("2026-10-22T16:40", "Pedido direto à área", "daniela"), h("2026-10-22T17:05", "Em análise", "Jurídico"), h("2026-10-23T09:30", "Resposta v1 pronta", "Jurídico")],
     "resposta": R3("O prazo de manifestação é contado da ciência. Pela data informada, faltam 12 dias; a contagem precisa ser confirmada pelo advogado.",
                    [{"titulo": "O que você pediu", "texto": "- Prazo estimado: 12 dias a partir de hoje\n- Documentos para o advogado: despacho, PER e memória de cálculo"}],
                    "Se a ciência foi por domicílio eletrônico, a data pode ser outra.", "Data de ciência no e-CAC: quem fornece é o cliente, pelo Master.")},
    {"id": "P-0037", "area": "depto-dados", "entrega": "Levantamento do HubSpot", "solicitante": "luis", "status": "aguardando_aprovacao", "criado_em": "2026-10-21T10:00",
     "precisa": "Quantos negócios estão parados há mais de 30 dias, por Master?", "uso": "Decisão interna", "prazo": "",
     "historico": [h("2026-10-21T10:00", "Pedido direto à área", "luis"), h("2026-10-21T12:30", "Resposta v1 pronta", "Dados & BI")],
     "resposta": R3("São 212 negócios parados há mais de 30 dias; 60% estão em 3 Masters.", [{"titulo": "O que você pediu", "texto": "- Planilha por Master e etapa\n- Os 20 maiores por valor de pipeline"}],
                    "Metade dos parados não tem próxima atividade no CRM.", "nada")},
    {"id": "P-0038", "area": "recuperador", "entrega": "Ficha de caso avulso (GT3)", "solicitante": "geovana", "status": "concluido", "criado_em": "2026-10-19T09:00",
     "precisa": "Reanálise de um negócio perdido de atacado em SC.", "uso": "Decisão interna", "prazo": "",
     "historico": [h("2026-10-19T09:00", "Pedido direto à área", "geovana"), h("2026-10-19T15:00", "Resposta v1 pronta", "Recuperador"), h("2026-10-20T10:00", "Aprovado", "geovana")]},
    {"id": "P-0039", "area": "depto-save-invest", "entrega": "", "solicitante": "daniela", "status": "novo", "criado_em": "2026-10-23T11:20",
     "precisa": "Cliente do Master 7 com caixa apertado pergunta sobre antecipação de duplicatas.", "uso": "Resposta ao parceiro", "prazo": "2026-10-28",
     "historico": [h("2026-10-23T11:20", "Pedido direto à área", "daniela")]},
    {"id": "P-0040", "area": "depto-marketing", "entrega": "Texto para WhatsApp", "solicitante": "jenifer", "status": "nova_analise", "criado_em": "2026-10-21T14:00",
     "precisa": "Mensagem curta de abordagem para escritórios contábeis.", "uso": "Prospecção", "prazo": "",
     "historico": [h("2026-10-21T14:00", "Pedido direto à área", "jenifer"), h("2026-10-21T17:00", "Resposta v1 pronta", "Marketing"), h("2026-10-22T09:00", "Pediu ajuste", "jenifer", "Mais curto e sem jargão")]},
    {"id": "P-0041", "area": "depto-solucoes", "entrega": "Mapa da conta", "solicitante": "luis", "status": "concluido", "criado_em": "2026-10-18T10:00",
     "precisa": "O que mais um cliente de logística pode contratar depois da recuperação?", "uso": "Reunião", "prazo": "",
     "historico": [h("2026-10-18T10:00", "Pedido direto à área", "luis"), h("2026-10-18T16:00", "Resposta v1 pronta", "Contas e Soluções"), h("2026-10-19T08:00", "Aprovado", "luis")]},
    {"id": "P-0042", "area": "depto-pos-venda", "entrega": "", "solicitante": "geovana", "status": "em_analise", "criado_em": "2026-10-22T13:00",
     "precisa": "Quanto falta receber de um PER de 2025 e se houve compensação de ofício.", "uso": "Resposta ao parceiro", "prazo": "",
     "reencaminhado": [{"de": "depto-tributario", "para": "depto-pos-venda", "motivo": "acompanhamento de recebimento é do Pós-venda", "quando": "2026-10-22T13:40"}],
     "historico": [h("2026-10-22T13:00", "Pedido direto à área", "geovana"), h("2026-10-22T13:40", "Reencaminhado ao Pós-venda", "Tributário"), h("2026-10-22T14:10", "Em análise", "Pós-venda")]},
]
nomes = {a["skill"]: a["nome"] for a in DIR["areas"]}
for p in PEDIDOS: p["area_nome"] = nomes.get(p["area"], "Central de Agentes"); p["direto"] = bool(p["area"])

DEMANDAS = [
    {"id": "D-0412", "pessoa": "daniela", "titulo": "Master 2 pergunta o status de 3 negócios", "master": "Master 2", "o_que_pede": "Etapa atual e próximo passo de cada negócio", "status": "responder", "aberta_em": "2026-10-23T08:10", "urgente": False},
    {"id": "D-0415", "pessoa": "daniela", "titulo": "Master 6 quer o extrato de setembro", "master": "Master 6", "o_que_pede": "Extrato de repasse do mês", "status": "responder", "aberta_em": "2026-10-23T09:20", "urgente": True},
    {"id": "D-0417", "pessoa": "daniela", "titulo": "Documento do cliente chegou pelo grupo", "master": "Master 4", "o_que_pede": "Anexar ao negócio e avisar o técnico", "status": "responder", "aberta_em": "2026-10-23T10:45", "urgente": False},
    {"id": "D-0398", "pessoa": "daniela", "titulo": "Reunião trimestral do Master 1", "master": "Master 1", "o_que_pede": "Pauta e números da conta", "status": "acompanhar", "aberta_em": "2026-10-21T15:00", "urgente": False},
    {"id": "D-0420", "pessoa": "jenifer", "titulo": "Master 5 pediu nova lista", "master": "Master 5", "o_que_pede": "Lista de transporte no PR", "status": "responder", "aberta_em": "2026-10-23T08:40", "urgente": False},
    {"id": "D-0421", "pessoa": "geovana", "titulo": "Técnico pede revisão de diagnóstico", "master": "Master 3", "o_que_pede": "Segunda opinião antes do cliente", "status": "responder", "aberta_em": "2026-10-23T09:00", "urgente": False},
]
CHAMADOS = [
    {"id": "D-0409", "pessoa": "daniela", "grupo": "Técnico · Diagnóstico", "titulo": "Diagnóstico de cliente do Master 3 parado há 8 dias", "descricao": "O diagnóstico está sem movimentação desde 15/10. Pedimos previsão de entrega e o que falta do cliente.", "status": "proposto", "urgencia": 3},
    {"id": "D-0377", "pessoa": "daniela", "grupo": "Jurídico", "titulo": "Despacho decisório com prazo correndo", "descricao": "Despacho recebido em 14/10. Pedimos análise do prazo e da defesa.", "status": "aberto", "urgencia": 4, "glpi_id": "18233"},
    {"id": "D-0399", "pessoa": "geovana", "grupo": "Técnico · Parecer", "titulo": "Parecer de tese de insumos sem período apurado", "descricao": "O parecer não traz o período. Pedimos a revisão.", "status": "proposto", "urgencia": 2},
]
LOTE = [{"deal": f"L{i}", "negocio": f"Empresa {c}", "parceiro": f"Master {m}", "tipo": t, "segmento": s, "uf": u, "esperado": e}
        for i, (c, m, t, s, u, e) in enumerate([("A", 3, "Perdido", "Indústria de alimentos", "SP", 180000), ("B", 1, "Zerado", "Atacado", "SC", 95000),
                                                ("C", 5, "Parado", "Transporte", "PR", 120000), ("D", 2, "Perdido", "Frigorífico", "GO", 240000),
                                                ("E", 7, "Zerado", "Hortifrúti", "MG", 60000)])]
ESP = {"agente": "Gerente Jurídico", "entendemos": "Cliente do Master 4 recebeu despacho decisório negando parte do PER de 2024. O parceiro quer saber se cabe defesa e o prazo.",
       "pedidos": ["Confirmar a data de ciência do despacho no e-CAC", "Calcular o prazo da manifestação de inconformidade", "Dizer se recomenda manifestação e o que o cliente precisa autorizar"],
       "anexos": ["Despacho decisório (PDF enviado no grupo)"], "faltam": ["Autorização do cliente para seguir: Daniela pede ao Master 4"],
       "prazo_motivo": "2026-10-31 · ciência estimada em 01/10, 30 dias; prazo interno 5 dias antes (a confirmar)", "entrega": "Orientação e decisão de defesa no card",
       "riscos": "Perda do prazo de manifestação", "checagens": ["Etapa no HubSpot: execução", "Parecer no card: sim"]}
WHATS = [
    {"id": "D-0412", "pessoa": "daniela", "chat": "Grupo Master 2 · Save", "grupo": "Master 2 · Save", "master": "Master 2", "status": "responder", "urgente": False, "aguardando_h": 3,
     "aberta_em": "2026-10-23T08:10", "o_que_pede": "Status de 3 negócios e o próximo passo de cada um", "rota": "Daniela responde com o status do HubSpot", "proximo_passo": "Enviar o status hoje", "prazo": "2026-10-23",
     "tipo": "Responder ao parceiro", "area_sugerida": "", "entrega": "- Empresa A: diagnóstico em andamento\n- Empresa B: contrato assinado, execução\n- Empresa C: aguardando documentos do cliente",
     "precisa": "A Empresa C está parada há 12 dias por falta de documento.", "falta": "nada", "rascunho": "Oi! Segue o status: A em diagnóstico, B em execução e C aguardando os documentos do cliente (lista em anexo). Assim que chegarem, seguimos.",
     "auditoria": {"ok": True, "achados": []}, "revisao": {"gerente": "Gerente da Central Masters", "aprovado": True, "rodadas": 1, "areas": []}, "rodada": "2026-10-23 08h", "chamado": None, "chamado_sugerido": None},
    {"id": "D-0415", "pessoa": "daniela", "chat": "Grupo Master 6 · Save", "grupo": "Master 6 · Save", "master": "Master 6", "status": "responder", "urgente": True, "aguardando_h": 26,
     "aberta_em": "2026-10-22T09:20", "o_que_pede": "Extrato de repasse de setembro", "rota": "Operações de Canal", "proximo_passo": "Pedir o extrato à área", "prazo": "2026-10-24",
     "tipo": "Responder ao parceiro", "area_sugerida": "depto-operacoes-canal", "entrega": "O extrato de setembro ainda não foi fechado pelo Financeiro.", "precisa": "Dois ganhos sem % de honorário travam o extrato.",
     "falta": "% de honorário de 2 ganhos: Financeiro.", "rascunho": "Oi! O extrato de setembro sai garantido até sexta, com o valor final.",
     "auditoria": {"ok": False, "achados": [{"termo": "garantido", "regra": "Promessa de prazo", "sugestao": "Troque por 'a previsão é'"}]}, "revisao": {"gerente": "Gerente de Operações de Canal", "aprovado": False, "rodadas": 2, "areas": []},
     "rodada": "2026-10-23 08h", "chamado": None, "chamado_sugerido": None},
    {"id": "D-0417", "pessoa": "daniela", "chat": "Grupo Master 4 · Save", "grupo": "Master 4 · Save", "master": "Master 4", "status": "responder", "urgente": True, "aguardando_h": 5,
     "aberta_em": "2026-10-23T10:45", "o_que_pede": "Cliente recebeu despacho decisório; quer saber se cabe defesa e o prazo", "rota": "Jurídico", "proximo_passo": "Aprovar o chamado ao Jurídico", "prazo": "2026-10-26",
     "tipo": "Chamado à área", "area_sugerida": "depto-juridico", "entrega": "O despacho nega parte do PER de 2024. A ciência parece ser de 01/10.", "precisa": "O prazo pode estar correndo desde a ciência.",
     "falta": "Autorização do cliente: Master 4.", "rascunho": "Recebemos o despacho e já encaminhamos ao Jurídico para avaliar a defesa e confirmar o prazo. Retornamos com a orientação.",
     "auditoria": {"ok": True, "achados": []}, "revisao": {"gerente": "Gerente Jurídico", "aprovado": True, "rodadas": 1, "areas": ["depto-juridico"]}, "rodada": "2026-10-23 14h", "chamado": None,
     "chamado_sugerido": {"area": "jur_comunicados", "grupo": "Juridico > Comunicados RFB", "titulo": "Demandas Diversas - Jurídico EMPRESA D x despacho decisório PER 2024", "urgencia": 4, "prazo": "2026-10-26",
                          "empresa": "Empresa D", "assunto": "despacho decisório", "documentos": "Despacho decisório (PDF)", "skill": "depto-juridico", "pronto": True, "agente": "Gerente Jurídico", "especialista": ESP,
                          "descricao": "**O que entendemos**\n" + ESP["entendemos"] + "\n\n**O que pedimos**\n" + "\n".join(f"{n}. {p}" for n, p in enumerate(ESP["pedidos"], 1)) + "\n\n**Prazo**\n" + ESP["prazo_motivo"]}},
    {"id": "D-0420", "pessoa": "jenifer", "chat": "Master 5", "grupo": "", "master": "Master 5", "status": "responder", "urgente": False, "aguardando_h": 2, "aberta_em": "2026-10-23T08:40",
     "o_que_pede": "Nova lista de transporte no PR", "rota": "Central BDR", "proximo_passo": "Fazer o pedido à área", "prazo": "2026-10-27", "tipo": "Responder ao parceiro", "area_sugerida": "celula-jenifer",
     "entrega": "", "precisa": "", "falta": "Critério de porte: Master 5.", "rascunho": "", "auditoria": {"ok": True, "achados": []}, "revisao": None, "rodada": "2026-10-23 08h", "chamado": None, "chamado_sugerido": None},
    {"id": "D-0421", "pessoa": "geovana", "chat": "Técnico · diagnósticos", "grupo": "Técnico · diagnósticos", "master": "Master 3", "status": "acompanhar", "urgente": False, "aguardando_h": 30,
     "aberta_em": "2026-10-22T09:00", "o_que_pede": "Segunda opinião antes do cliente", "rota": "Revisor de Diagnóstico", "proximo_passo": "Rodar o Revisor", "prazo": "", "tipo": "Chamado à área", "area_sugerida": "depto-tributario",
     "entrega": "", "precisa": "", "falta": "Parecer do técnico.", "rascunho": "", "auditoria": {"ok": True, "achados": []}, "revisao": None, "rodada": "2026-10-23 08h", "chamado": None,
     "chamado_sugerido": {"area": "trib_diagnostico", "grupo": "Tributário > Diagnóstico", "titulo": "", "urgencia": 2, "prazo": "", "skill": "depto-tributario", "pronto": False, "nao_abrir": "", "descricao": ""}},
]
ARQ = {"daniela": [{"nome": "Plano-do-dia-2026-10-23.xlsx", "hora": "07:42", "pasta": "Plano do dia"}, {"nome": "Controle-Pendencias-Masters.xlsx", "hora": "08:05", "pasta": ""},
                   {"nome": "Briefing-Master-1-QBR.docx", "hora": "09:30", "pasta": "Briefings"}],
       "jenifer": [{"nome": "Plano-do-dia-2026-10-23.xlsx", "hora": "07:42", "pasta": "Plano do dia"}, {"nome": "Lista-Master-5-transporte-PR.xlsx", "hora": "10:10", "pasta": "Listas"}],
       "geovana": [{"nome": "Plano-do-dia-2026-10-23.xlsx", "hora": "07:42", "pasta": "Plano do dia"}, {"nome": "Folha-do-lote-semana-43.xlsx", "hora": "09:00", "pasta": "Fichas do Recuperador"}],
       "luis": [{"nome": "Plano-do-dia-Luis-2026-10-23.xlsx", "hora": "07:42", "pasta": ""}, {"nome": "Decisoes-Pendentes-2026-10-23.xlsx", "hora": "07:50", "pasta": ""}]}

SP = "https://gruposave-my.sharepoint.com/my?id=%2Fpersonal%2Fexemplo%2FDocuments%2FExemplo"  # link de exemplo (não abre pasta real)
def cx(i, para, assunto, resumo, origem, tipo, quando, prioridade="normal", anexos=(), acoes=(), lido=False):
    return {"id": f"cx-20261023-{para[:3]}-{i}", "para": para, "assunto": assunto, "resumo": resumo, "origem": origem, "tipo": tipo, "prioridade": prioridade,
            "anexos": [{"nome": n, "pasta_link": SP} for n in anexos], "acoes": [{"rotulo": r, "go": g} for r, g in acoes], "criado_em": quando,
            "lido_por": {para: {"em": quando}} if lido else {}, "auditoria": "ok"}
CAIXA = [  # mensagens de exemplo da caixa de entrada (sem cliente)
    cx("a1", "luis", "Falha na rotina areas:icp", "A rotina areas:icp falhou agora. As etapas que dependem dela foram puladas para não usar dado desatualizado.\n\nÚltimas linhas do log:\n- Timeout ao baixar a base do HubSpot (só leitura)\n- Nova tentativa na próxima rodada\n\nPara ver tudo: partners logs areas.",
       "alerta", "alerta", "2026-10-23T10:12:00-03:00", "alta", acoes=[("Ver rotinas", "rotinas")]),
    cx("a2", "luis", "Entrega atrasada hoje: Relatório semanal de resultados", "O que não saiu até agora:\n- Relatório semanal de resultados: esperada desde as 8h. A Central refaz na próxima rodada.",
       "sentinela", "alerta", "2026-10-23T09:05:00-03:00", "alta", acoes=[("Abrir minha mesa", "mesa"), ("Ver rotinas", "rotinas")]),
    cx("a3", "luis", "Plano do dia · Luis · 23/10", "18 item(ns) no plano de hoje, 3 urgente(s).\n- Prazo da Receita: 1\n- Contrato sem assinatura: 4\n- Comercial parado: 13\n\nA lista completa, com os links do HubSpot e do Bitrix, está na planilha, na sua pasta do OneDrive (Plano do dia).",
       "plano", "relatorio", "2026-10-23T07:42:00-03:00", anexos=["Plano-do-dia-Luis-2026-10-23.xlsx"], acoes=[("Abrir minha mesa", "mesa")], lido=True),
    cx("d1", "daniela", "Plano do dia · Daniela · 23/10", "12 item(ns) no plano de hoje, 2 urgente(s).\n- Demanda atrasada: 2\n- Contrato sem assinatura: 3\n- Comercial parado: 7\n\nA lista completa está na planilha, na sua pasta do OneDrive (Plano do dia).",
       "plano", "relatorio", "2026-10-23T07:42:00-03:00", anexos=["Plano-do-dia-2026-10-23.xlsx"], acoes=[("Abrir minha mesa", "mesa")]),
    cx("d2", "daniela", "[AGENTES] #P-0031 · Conferência de repasses do Master 2 · resposta v1", "A conferência de repasses do Master 2 está pronta para a sua aprovação. O percentual vem do que foi negociado com o Master (D64); dois ganhos ficaram fora por falta do % de honorário no card.\n\nOs arquivos estão na sua pasta do OneDrive, em Pedidos / P-0031.",
       "central", "pedido", "2026-10-23T11:20:00-03:00", anexos=["Conferencia-Repasses-Master-2.xlsx"], acoes=[("Abrir pedido", "pedido/P-0031")]),
    cx("d3", "daniela", "WhatsApp · 3 demandas para responder", "Rodada das 8h: 3 demandas para responder, 1 urgente (despacho decisório com prazo hoje). Os rascunhos conferidos pelas áreas estão na tela de demandas.",
       "whatsapp", "relatorio", "2026-10-23T08:35:00-03:00", "alta", acoes=[("Abrir demandas", "whatsapp")], lido=True),
    cx("t1", "time", "Radar de mercado da semana", "Três mudanças da semana que afetam a esteira:\n- Prazo de opção da reforma: sem alteração\n- Nova IN sobre compensação: só leitura, sem efeito imediato\n- Agenda de capacitação dos Masters publicada\n\nTudo é pré-análise, sem promessa de valor.",
       "radar", "relatorio", "2026-10-23T10:00:00-03:00", anexos=["radar-2026-10-23.md"], acoes=[("Ver as áreas", "areas")]),
    cx("g1", "geovana", "Recuperador · Lote 43 da semana", "Lote da semana com 8 casos para decidir. Para cada caso, a folha traz a hipótese de tese, o que o técnico concluiu e os documentos a pedir. Hipóteses a verificar, sem promessa de valor.",
       "recuperador", "relatorio", "2026-10-23T09:00:00-03:00", anexos=["Fila-Recuperador-2026-10-23.xlsx"], acoes=[("Abrir lote", "mesa")]),
    cx("j1", "jenifer", "Plano do dia · Jenifer · 23/10", "6 item(ns) no plano de hoje, nenhum urgente.\n- Comercial parado: 6", "plano", "relatorio", "2026-10-23T07:42:00-03:00",
       anexos=["Plano-do-dia-2026-10-23.xlsx"], acoes=[("Abrir minha mesa", "mesa")]),
]

EX = {"atualizado": D["atualizado"], "hoje": "2026-10-23", "blocos": DIR["blocos"], "areas": DIR["areas"], "rotinas": DIR["rotinas"], "pastas": DIR["pastas"], "pessoas": DIR["pessoas"], "regras_casa": DIR.get("regras_casa", []),
      "demandas_num": D.get("demandas", {}), "alertas": D["gestao"]["alertas"], "manchete": D["gestao"]["manchete"], "masters": masters, "decisoes": dec,
      "decisoes_total": len(D.get("conselho", [])), "janelas": janelas, "pedidos": PEDIDOS, "demandas": DEMANDAS, "chamados": CHAMADOS, "lote": LOTE, "arquivos": ARQ, "whatsapp": WHATS, "caixa": CAIXA}
open(os.path.join(AQUI, "exemplo-dados.js"), "w").write("/* Gerado por gerar_exemplo.py. Pedidos, demandas, chamados, lote e arquivos são EXEMPLOS fictícios. */\nwindow.EX = "
                                                        + json.dumps(EX, ensure_ascii=False) + ";\n")
print("exemplo-dados.js:", len(PEDIDOS), "pedidos de exemplo,", len(DIR["areas"]), "áreas")
