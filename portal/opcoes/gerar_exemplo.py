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
     "auditoria": {"ok": True, "achados": []}, "revisao": {"gerente": "Gerente da Central Masters", "aprovado": True, "rodadas": 1, "areas": []}, "rodada": "2026-10-23 08h", "chamado": None, "chamado_sugerido": None,
     "tipo": "Respondido pelo histórico", "historico": {"consultado": True, "suficiente": True, "criterio": "dado_do_caso", "confianca": 0.85, "faltou": "", "nota": "Etapas conferidas no download do dia.", "buscas": 2},
     "resposta_historico": {"resposta": "Oi! Segue o status: A em diagnóstico, B em execução e C aguardando os documentos do cliente (lista em anexo). Assim que chegarem, seguimos.", "auditado": True, "confianca": 0.85,
                            "criterio": "dado_do_caso", "area": "Central Masters", "especialista": "Retorno ao Parceiro",
                            "fontes": [{"fonte": "caso", "data": "2026-10-23", "trecho": "Empresa A: etapa Apresentação de Diagnóstico; Empresa B: Contrato Assinado"},
                                       {"fonte": "triagem", "data": "2026-10-16", "trecho": "Resposta aprovada ao Master 2 sobre a lista de documentos da Empresa C"}]}},
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
     "historico": {"consultado": True, "suficiente": False, "criterio": None, "confianca": 0.3, "buscas": 3, "faltou": "documento novo com prazo (despacho decisório): exige análise nova do Jurídico", "nota": "Concordo com a pré-avaliação: há casos parecidos, mas o prazo depende da ciência deste despacho."},
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

# ---------- Sistema de gestão (26/10/2026): exemplo no contrato infra/gestao-schema.md, montado pelo próprio infra/gestao.py ----------
import sys; sys.path.insert(0, os.path.join(REPO, "infra")); import gestao as G
MI = 1_000_000
def mt(id_, nome, bloco, valor, unidade, anterior, meta, status, confianca, nota, fonte="hubspot 26/10 06:53"):
    var = round((valor - anterior) / anterior * 100, 1) if anterior else None
    return {"id": id_, "nome": nome, "bloco": bloco, "valor": valor, "unidade": unidade, "anterior": anterior, "variacao_pct": var, "meta": meta,
            "tolerancia": {"verde": ">= 0.9*meta", "amarelo": ">= 0.7*meta"} if meta is not None else {"verde": "proposta: >= 0.9*meta", "amarelo": "proposta: >= 0.7*meta"},
            "status": status, "fonte": fonte, "confianca": confianca, "nota": nota}
def mes(m, nome, meta, real, dt, dd, status, situacao):
    dr = dt - dd; rn = round((meta - real) / dr) if dr else None; ra = round(real / dd) if dd else None
    return {"mes": m, "nome": nome, "meta_rs": meta, "realizado_rs": real, "ganhos_n": 35 if real else 0, "falta_rs": meta - real, "pct": round(real / meta * 100, 1),
            "dias_uteis_total": dt, "dias_uteis_decorridos": dd, "dias_uteis_restantes": dr, "ritmo_necessario_rs_dia": rn, "ritmo_atual_rs_dia": ra,
            "fator_ritmo": round(rn / ra, 1) if rn and ra else None, "situacao": situacao, "status": status}
MESES = [mes("2026-10", "outubro", 75 * MI, int(16.4 * MI), 21, 17, "vermelho", "em andamento"), mes("2026-11", "novembro", 100 * MI, 0, 19, 0, "cinza", "a iniciar"),
         mes("2026-12", "dezembro", 75 * MI, 0, 22, 0, "cinza", "a iniciar")]
PESOS = [40.9, 18.2, 12.5, 9.8, 7.1, 5.0, 3.6, 2.9]
META_D111 = {"unidade": "credito_contrato_fechado", "decisao": "D111 (26/10/2026)", "q4_rs": 250 * MI, "realizado_rs": int(16.4 * MI), "falta_rs": int(233.6 * MI), "dias_uteis_restantes": 45,
    "ritmo_necessario_rs_dia": 5_190_656, "ritmo_atual_rs_dia": 965_910, "mes_atual": MESES[0], "meses": MESES,
    "total": {"meta_rs": 250 * MI, "realizado_rs": int(16.4 * MI), "falta_rs": int(233.6 * MI), "pct": 6.6, "dias_uteis_total": 62, "dias_uteis_decorridos": 17, "dias_uteis_restantes": 45,
              "ritmo_necessario_rs_dia": 5_190_656, "ritmo_atual_rs_dia": 965_910, "fator_ritmo": 5.4, "status": "vermelho"},
    "por_master": {"proposta": True, "status": "proposta (não aprovada; meta é alçada do Luis)", "metodo": "Peso = 50% da participação no pipeline aberto + 50% da participação no fechado de 12 meses no volume limpo. Meta do Master = peso × meta do mês.",
                   "alerta": "O pipeline concentra em poucos Masters: o desdobramento herda a concentração. A Daniela valida Master a Master antes de comunicar.",
                   "masters": [{"master": f"Master {i + 1}", "peso_pct": w, "meses": [{"mes": x["mes"], "meta_rs": round(x["meta_rs"] * w / 100), "realizado_rs": round(x["realizado_rs"] * w / 100 * (1.1 if i == 0 else .8))} for x in MESES],
                                "meta_q4_rs": round(250 * MI * w / 100), "realizado_q4_rs": round(16.4 * MI * w / 100 * (1.1 if i == 0 else .8))} for i, w in enumerate(PESOS)]}}
PACOTE = {"data": "2026-10-26", "periodo": {"semana_de": "2026-10-19", "mes": "2026-10", "trimestre": "2026-Q4"},
    "meta": META_D111,
    "metricas": [
        mt("ganhos_mes_rs", "Fechado no mês (limpo)", "resultado", int(18.4 * MI), "R$", int(22.1 * MI), 25 * MI, "amarelo", "alta", "Sem os 9 grupos de duplicidade; 3 ganhos sem honorário fora."),
        mt("ganhos_mes_n", "Contratos fechados no mês", "resultado", 14, "n", 19, 20, "amarelo", "alta", "Metade concentrada em 2 Masters."),
        mt("conversao_pct", "Conversão diagnóstico → contrato", "resultado", 9.8, "%", 12.4, 15, "vermelho", "media", "Queda nas safras de agosto e setembro."),
        mt("ticket_medio_rs", "Ticket médio do crédito", "resultado", int(1.3 * MI), "R$", int(1.2 * MI), None, "cinza", "alta", "Sem meta aprovada; tolerância proposta."),
        mt("recebido_mes_rs", "Recebido no mês", "caixa", int(4.1 * MI), "R$", int(3.6 * MI), 5 * MI, "amarelo", "alta", "PER de 2025 ainda em análise na Receita.", "financeiro 24/10"),
        mt("per_analise_rs", "PER em análise (crédito)", "caixa", 31 * MI, "R$", 28 * MI, None, "cinza", "media", "Prazo de 360 dias correndo em 11 pedidos.", "pós-venda 23/10"),
        mt("recebiveis_30d_rs", "A receber em 30 dias", "caixa", int(6.8 * MI), "R$", int(5.9 * MI), 6 * MI, "verde", "media", "Estimativa com base nas compensações previstas."),
        mt("masters_ativos_n", "Masters ativos no mês", "canal", 7, "n", 8, 9, "amarelo", "alta", "Dois Masters sem negócio novo há 45 dias."),
        mt("negocios_parados_n", "Negócios parados > 30 dias", "canal", 212, "n", 198, 120, "vermelho", "alta", "60% em 3 Masters; metade sem próxima atividade."),
        mt("demandas_sla_pct", "Demandas respondidas no prazo", "canal", 86, "%", 81, 90, "verde", "alta", "Rodadas de 8h e 14h do WhatsApp.", "registro de demandas 26/10"),
        mt("ganhos_sem_hon_pct", "Ganhos sem % de honorário", "risco", 21, "%", 24, 5, "vermelho", "alta", "Trava o repasse e o extrato do mês.", "conferência de repasses 26/10"),
        mt("qualidade_ganhos", "Índice de qualidade dos ganhos", "risco", 72, "n", 69, 85, "amarelo", "media", "Duplicidade e campos vazios pesam.", "dados-bi 26/10"),
        mt("decadencia_90d_rs", "Crédito que decai em 90 dias", "risco", int(19.2 * MI), "R$", int(14.8 * MI), None, "cinza", "media", "Pré-análise; validação do técnico por crédito.", "pós-venda 23/10"),
        mt("pedidos_sla_pct", "Pedidos à Central no prazo", "operacao", 91, "%", 88, 90, "verde", "alta", "12 pedidos na semana.", "central 26/10"),
        mt("entregas_atrasadas_n", "Entregas atrasadas hoje", "operacao", 1, "n", 0, 0, "amarelo", "alta", "Relatório semanal refeito pela Central.", "sentinela 26/10 07:30"),
        mt("rotinas_falhas_n", "Falhas de rotina na semana", "operacao", 3, "n", 1, 0, "vermelho", "alta", "Duas por queda de internet (19 e 26/10).", "sentinela 26/10"),
    ],
    "confiabilidade": {"indice_qualidade_ganhos": 72, "ganhos_sem_honorario_pct": 21, "duplicados_grupos": 9, "volume_bruto_rs": int(21.7 * MI), "volume_limpo_rs": int(18.4 * MI)},
    "alertas": [{"texto": "Volume bruto do mês tem 9 grupos de duplicidade; o painel usa o limpo.", "area": "Dados & BI", "severidade": "media"},
                {"texto": "Conversão caiu duas semanas seguidas.", "area": "Resultados", "severidade": "alta"}]}
sem = ["2026-W44", "2026-W45", "2026-W46", "2026-W47", "2026-W48", "2026-W49", "2026-W50", "2026-W51", "2026-W52", "2027-W01", "2027-W02", "2027-W03", "2027-W04"]
base = [1.1, 1.4, 0.9, 2.2, 1.6, 1.3, 2.8, 1.9, 0.7, 0.6, 1.2, 1.5, 1.8]; cons = [0.8, 1.0, 0.7, 1.4, 1.1, 0.9, 1.7, 1.2, 0.5, 0.4, 0.8, 1.0, 1.1]
def cen(v, meta=None):
    return {"esperado_rs": int(v * MI), "pct_da_meta": None if meta is None else round(v / meta * 100, 1), "faixa_p10_p90_rs": [int(v * .85 * MI), int(v * 1.2 * MI)], "probabilidade_meta_pct": 0.0}
PREVISAO = {"data": "2026-10-26", "horizonte_semanas": 13,
    "cenarios": {"conservador": {"fechamento_q4_rs": 128 * MI, "liquido_q4_rs": 19 * MI, "premissas": ["Conversão das safras de agosto e setembro segue em 9,8%", "Só os 7 Masters ativos fecham negócio", "Nenhum PER de 2025 pago no Q4"]},
                 "base": {"fechamento_q4_rs": 156 * MI, "liquido_q4_rs": 24 * MI, "premissas": ["Conversão volta a 12%, média de 2026", "Lote 1 do Recuperador recupera 6 negócios perdidos", "Metade das compensações previstas entra em dezembro"]},
                 "esforco": {"fechamento_q4_rs": 66 * MI, "liquido_q4_rs": int(9.7 * MI), "premissas": ["Lote 1 do Recuperador decidido até 03/11", "60% dos contratos enviados assinam até 31/12", "Criação volta ao ritmo de setembro"]},
                 "meta": {"fechamento_q4_rs": 250 * MI, "liquido_q4_rs": 30 * MI, "o_que_precisa": ["Conversão em 15% nas 3 safras abertas", "Os 9 Masters com pelo menos 2 contratos até 15/12", "Negócios parados abaixo de 120 até 30/11"]}},
    "por_mes": {"meses": [{"mes": m, "nome": n, "meta_rs": mt_, "cenarios": {"conservador": cen(c, mt_ / MI), "base": cen(b, mt_ / MI), "esforco": cen(e, mt_ / MI)}} for m, n, mt_, c, b, e in
                          [("2026-10", "outubro", 75 * MI, 18.8, 20.0, 20.6), ("2026-11", "novembro", 100 * MI, 5.8, 12.8, 21.3), ("2026-12", "dezembro", 75 * MI, 6.5, 15.6, 24.0)]],
                "total": {"meta_rs": 250 * MI, "cenarios": {"conservador": cen(31.2, 250), "base": cen(48.5, 250), "esforco": cen(65.9, 250)}}},
    "caixa_13_semanas": [{"semana": s, "entrada_rs_base": int(b * MI), "entrada_rs_conservador": int(c * MI), "fonte": "PER/compensação/parcelamento"} for s, b, c in zip(sem, base, cons)],
    "pipeline_por_safra": [{"safra": "2026-08", "aberto_rs": 42 * MI, "conversao_real_pct": 9.1, "esperado_rs": int(3.8 * MI)}, {"safra": "2026-09", "aberto_rs": 57 * MI, "conversao_real_pct": 10.4, "esperado_rs": int(5.9 * MI)},
                           {"safra": "2026-10", "aberto_rs": 38 * MI, "conversao_real_pct": None, "esperado_rs": int(4.6 * MI)}],
    "decadencia_mensal": [{"mes": "2026-11", "credito_que_sai_rs": int(4.2 * MI), "clientes_n": 6}, {"mes": "2026-12", "credito_que_sai_rs": int(12.5 * MI), "clientes_n": 14},
                          {"mes": "2027-01", "credito_que_sai_rs": int(2.1 * MI), "clientes_n": 3}, {"mes": "2027-02", "credito_que_sai_rs": 800_000, "clientes_n": 2}, {"mes": "2027-03", "credito_que_sai_rs": int(3.4 * MI), "clientes_n": 5}],
    "janelas": [{"janela": "Decadência de novembro de 2021 (créditos de nov/2021)", "prazo": "2026-11-30", "base_rs": int(4.2 * MI), "clientes_n": 6, "area": "Pós-venda"},
                {"janela": "Saldos credores da reforma: opção até 31/12", "prazo": "2026-12-31", "base_rs": int(12.5 * MI), "clientes_n": 14, "area": "Tributário"},
                {"janela": "Prazo de manifestação em despacho decisório", "prazo": "2026-10-31", "base_rs": int(1.6 * MI), "clientes_n": 1, "area": "Jurídico"}],
    "riscos": [{"risco": "Compensação de ofício engolir o PER de 2025", "probabilidade": "media", "impacto_rs": int(2.4 * MI), "mitigacao": "Conferir débitos em aberto antes do pedido", "dono": "geovana", "prazo": "2026-11-05"},
               {"risco": "Dois Masters saírem do programa", "probabilidade": "baixa", "impacto_rs": 18 * MI, "mitigacao": "Plano de conta e QBR em novembro", "dono": "daniela", "prazo": "2026-11-14"}]}
CONTROLE = {"data": "2026-10-26",
    "regras": [{"id": "C01", "metrica": "ganhos_mes_rs", "condicao": "status == vermelho por 2 semanas", "acao": "Conselho revisa o plano da semana", "dono": "luis", "prazo_dias": 3, "alcada": "luis"},
               {"id": "C02", "metrica": "negocios_parados_n", "condicao": "valor > 120", "acao": "Daniela cobra próxima atividade dos 3 Masters com mais parados", "dono": "daniela", "prazo_dias": 5, "alcada": "dona"},
               {"id": "C03", "metrica": "ganhos_sem_hon_pct", "condicao": "valor > 5%", "acao": "Controller pede o % ao Financeiro e trava o extrato", "dono": "controller", "prazo_dias": 3, "alcada": "gerente"},
               {"id": "C04", "metrica": "conversao_pct", "condicao": "valor < 10,5% (amarelo)", "acao": "Geovana revisa os diagnósticos sem contrato das 2 safras", "dono": "geovana", "prazo_dias": 7, "alcada": "dona"},
               {"id": "C05", "metrica": "rotinas_falhas_n", "condicao": "valor > 0", "acao": "TI refaz e registra a causa", "dono": "gerente-ti", "prazo_dias": 1, "alcada": "gerente"}],
    "desvios": [{"regra": "C02", "metrica": "negocios_parados_n", "valor": 212, "limite": 120, "desde": "2026-10-12", "acao": "Cobrar próxima atividade dos Masters 2, 5 e 7", "dono": "daniela", "prazo": "2026-10-29", "status": "em_andamento"},
                {"regra": "C03", "metrica": "ganhos_sem_hon_pct", "valor": 21, "limite": 5, "desde": "2026-10-05", "acao": "Pedir o % de 3 ganhos ao Financeiro", "dono": "controller", "prazo": "2026-10-28", "status": "aberto"},
                {"regra": "C04", "metrica": "conversao_pct", "valor": 9.8, "limite": 10.5, "desde": "2026-10-19", "acao": "Revisar 11 diagnósticos sem contrato (safras 08 e 09)", "dono": "geovana", "prazo": "2026-11-02", "status": "aberto"},
                {"regra": "C05", "metrica": "rotinas_falhas_n", "valor": 3, "limite": 0, "desde": "2026-10-26", "acao": "Registrar a causa das 2 quedas de internet e testar o reparo automático", "dono": "gerente-ti", "prazo": "2026-10-27", "status": "resolvido"}],
    "ritual": [{"quando": "segunda 7h30", "quem": "Conselho", "o_que": "pacote + previsão + desvios", "saida": "ata com decisões"}, {"quando": "sexta 16h", "quem": "Gabinete", "o_que": "consolidação e folha de decisões", "saida": "folha única"}]}
ACOES = [{"id": "A-2026-10-26-1", "acao": "Validar o desdobramento da meta por Master antes de comunicar", "dono": "daniela", "prazo": "2026-10-30", "origem": "conselho", "status": "aberto"},
         {"id": "A-2026-10-26-2", "acao": "Aprovar as metas das 4 métricas cinza do semáforo", "dono": "luis", "prazo": "2026-11-03", "origem": "conselho", "status": "aberto"},
         {"id": "A-2026-10-19-3", "acao": "QBR com os 2 Masters sem negócio novo", "dono": "daniela", "prazo": "2026-11-14", "origem": "conselho", "status": "em_andamento"}]
# Pré-análise das áreas por farol (formato de registro/gestao/pre-analise-<data>.json), exemplo sem cliente.
def pa(mid, area, esp, leitura, fatos, hips, acoes, dec, efeito, conf, melhorar, pendente=False):
    return {"metrica_id": mid, "area": area, "especialista": esp, "leitura": leitura, "causa": {"fatos": fatos, "hipoteses": hips},
            "acoes": [{"acao": a, "dono": d, "prazo": pz} for a, d, pz in acoes], "decisao_sugerida": dec, "efeito": efeito, "confianca": conf, "melhorar_confianca": melhorar, "pendente": pendente}
PRE = {"data": "2026-10-26", "itens": [
    pa("conversao_pct", "depto-resultados", "forecast-pipeline", "Conversão de 9,8% contra 12,4% no período anterior; a queda está nas safras de agosto e setembro, com 11 diagnósticos sem contrato.",
       ["Safra de agosto: 9,1% de conversão real (ganho ÷ fechados)", "Safra de setembro: 10,4%", "11 diagnósticos apresentados sem retorno há mais de 20 dias"],
       ["Parte dos diagnósticos foi apresentada sem o Master na reunião", "Proposta enviada sem a coluna conservadora da tese"],
       [("Revisar os 11 diagnósticos sem contrato e marcar o motivo de cada um", "geovana", "2026-10-30"), ("Reunião de retomada com os 3 Masters de maior volume parado", "daniela", "2026-11-04")],
       "Levar ao Conselho a leitura da conversão por safra no deck da diretoria (sem promessa de recuperação).", "Estimativa: recuperar 3 dos 11 diagnósticos soma cerca de R$ 3 mi de crédito no Q4, com a premissa de ticket mediano. Não é previsão de resultado.",
       "media", "Motivo de perda preenchido nos 11 casos (Geovana) e data da apresentação no card (Daniela)."),
    pa("negocios_parados_n", "celula-daniela", "gestor-contas-chave", "212 negócios parados há mais de 30 dias, acima do limite proposto de 120; 60% estão em 3 Masters.",
       ["Metade dos parados não tem próxima atividade no CRM", "3 Masters concentram 127 dos 212"], ["Masters com carteira grande não priorizam os negócios menores"],
       [("Cobrar próxima atividade dos Masters 2, 5 e 7", "daniela", "2026-10-29"), ("Lista dos 20 parados de maior valor para o Recuperador", "geovana", "2026-11-03")],
       None, "Estimativa: tirar 90 negócios da lista de parados devolve o indicador ao amarelo.", "alta", "Data da última atividade confiável no HubSpot (gerente de Dados)."),
    pa("ganhos_sem_hon_pct", "depto-dados", "governanca-dados", "21% dos ganhos sem % de honorário; o campo vazio trava o repasse e o extrato do mês.",
       ["3 ganhos de outubro sem o campo", "Regra C03 aberta desde 05/10"], ["O campo não é obrigatório na etapa de ganho"],
       [("Pedir o % dos 3 ganhos ao Financeiro", "controller", "2026-10-28")], "Tornar obrigatório o % de honorário na etapa de ganho do HubSpot (pedido de rascunho à TI da Save).", "Sem efeito em R$; libera o extrato do mês.", "alta", ""),
    pa("rotinas_falhas_n", "depto-ti", "rotinas-agendadas", "3 falhas de rotina na semana, duas por queda de internet.", ["Quedas em 19 e 26/10", "Reparo automático refez 2 das 3"], ["Roteador reinicia de madrugada"],
       [("Registrar a causa e testar o reparo automático", "gerente-ti", "2026-10-27")], None, "", "media", "Log do roteador (TI da Save).", True)],
  "decisoes_luis": [{"chave": "D30", "decisao": "Responder D30 (congelar até o G2) para tirar o tema da pauta do Q4.", "efeito": "Leitura única da conversão para a diretoria.", "metricas": ["conversao_pct"], "area": "depto-resultados", "status": "vermelho"}]}
# Dossiês das decisões (formato de registro/gestao/dossies/<id>.json). A 1ª decisão do exemplo usa o dossiê real dela quando existe (decisões escolhidas
# sem nome de cliente); sem o arquivo, um dossiê fictício. A 2ª fica sem dossiê, para a prévia mostrar a ausência.
def val(area, esp, parecer, motivo, condicao="", base="ata do Conselho de 26/10 (exemplo)", ressalva=""):
    return {"area": area, "especialista": esp, "parecer": parecer, "motivo": motivo, "base": base, "condicao": condicao, "ressalva": ressalva}
DOSSIES = {d["id"]: {"id": d["id"], "titulo": t, "prazo": "2026-10-30", "o_que_decidir": o, "por_que_agora": pq, "custo_nao_decidir": cu,
                     "contexto": [{"fato": "Conversão do mês em 9,8%, contra 12,4% no período anterior.", "fonte": "pacote de gestão de 26/10", "tipo": "fato"},
                                  {"fato": "O cenário base do Q4 fecha perto de R$ 48 mi; a meta da D111 é R$ 250 mi.", "fonte": "previsão de 26/10", "tipo": "estimativa"},
                                  {"fato": "Os Masters preferem receber a leitura por safra, não por mês.", "fonte": "conversa da Daniela com 3 Masters", "tipo": "opiniao"}],
                     "opcoes": [{"nome": "A · Manter como está", "pros": "Nada muda para o time.", "contras": "O problema continua.", "risco": "Médio.", "efeito": "Nenhum."},
                                {"nome": "B · Aprovar com o corte por safra", "pros": "Leitura única para a diretoria e para os Masters.", "contras": "Exige uma rodada a mais dos Dados.", "risco": "Baixo.", "efeito": "Deck de 30/10 sai com a leitura nova."},
                                {"nome": "C · Adiar para dezembro", "pros": "Menos trabalho agora.", "contras": "Perde a janela do Q4.", "risco": "Alto.", "efeito": "Decisão volta em 01/12."}],
                     "recomendacao": "Aprovar a opção B, com a revisão mensal no 1º dia útil de cada mês.", "se_reprovada": "Fica a opção A; o Controller registra o motivo e o tema volta ao Conselho em 30 dias.",
                     "validacoes": vs, "divergencias": dv, "execucao": {"dono": "Controller", "prazo": "2026-10-30", "indicador": "deck enviado com a leitura por safra"}, "atualizado_em": "2026-10-26",
                     "revisao": {"gerente": "Gabinete (Consolidador)", "aprovado": True, "rodadas": 1}}
           for d, t, o, pq, cu, vs, dv in [
               (dec[0], "Leitura da conversão por safra no deck da diretoria", "Se a conversão vai à diretoria por safra de criação, com a coluna conservadora.", "O deck sai em 30/10.", "A diretoria lê uma conversão que mistura safras e não mostra a queda.",
                [val("Resultados", "forecast-pipeline", "concorda", "A leitura por safra é a que a previsão já usa."), val("Dados & BI", "governanca-dados", "concorda com ressalva", "Precisa de uma rodada a mais para limpar os duplicados.", "Lista conciliada até 29/10.", ressalva="Sem a conciliação, o número muda depois do envio."),
                 val("Central Masters", "gestor-contas-chave", "concorda com ressalva", "Os Masters entendem melhor a leitura por safra.", "Daniela apresenta antes aos 3 maiores."), val("Qualidade", "auditor-promessas", "discorda", "O deck não pode trazer número de êxito por cliente.", "Tirar a coluna por cliente.")],
                ["Qualidade discorda da coluna por cliente; Resultados mantém a coluna agregada por safra."]),
               ({"id": "EX-2"}, "Campo de % de honorário obrigatório na etapa de ganho", "Se o campo vira obrigatório no HubSpot ao marcar o negócio como ganho.", "21% dos ganhos estão sem o campo e travam o repasse.", "O extrato do mês continua travado e o repasse atrasa.",
                [val("Dados & BI", "governanca-dados", "concorda", "Resolve na origem."), val("Operações de Canal", "repasse", "concorda", "Destrava o extrato.")], [])]}
_real = os.path.expanduser(f"~/agentes-partners/registro/gestao/dossies/{dec[0]['id']}.json")
if os.path.exists(_real): DOSSIES[dec[0]["id"]] = json.load(open(_real, encoding="utf-8"))
GESTAO = G.montar(PACOTE, PREVISAO, CONTROLE, [{"id": d["id"], "texto": d["texto"], "data": d["data"]} for d in dec], ACOES, [], hoje="2026-10-26", pre_analise=PRE, dossies={k: G._dossie(v) for k, v in DOSSIES.items()})

EX = {"atualizado": D["atualizado"], "hoje": "2026-10-23", "gestao": GESTAO, "blocos": DIR["blocos"], "areas": DIR["areas"], "rotinas": DIR["rotinas"], "pastas": DIR["pastas"], "pessoas": DIR["pessoas"], "regras_casa": DIR.get("regras_casa", []),
      "demandas_num": D.get("demandas", {}), "alertas": D["gestao"]["alertas"], "manchete": D["gestao"]["manchete"], "masters": masters, "decisoes": dec,
      "decisoes_total": len(D.get("conselho", [])), "janelas": janelas, "pedidos": PEDIDOS, "demandas": DEMANDAS, "chamados": CHAMADOS, "lote": LOTE, "arquivos": ARQ, "whatsapp": WHATS, "caixa": CAIXA}
open(os.path.join(AQUI, "exemplo-dados.js"), "w").write("/* Gerado por gerar_exemplo.py. Pedidos, demandas, chamados, lote e arquivos são EXEMPLOS fictícios. */\nwindow.EX = "
                                                        + json.dumps(EX, ensure_ascii=False) + ";\n")
print("exemplo-dados.js:", len(PEDIDOS), "pedidos de exemplo,", len(DIR["areas"]), "áreas")
