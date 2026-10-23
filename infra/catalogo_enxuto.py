#!/usr/bin/env python3
"""Catálogo enxuto das skills (Luis, 23/10/2026). O catálogo de skills corta pelo tamanho total das descrições:
com ~38 mil caracteres, várias áreas sumiam da sessão e o agente certo não era chamado. Cada descrição fica com
até ~600 caracteres (o que faz + gatilhos principais). O texto longo anterior vai para o corpo da skill, na seção
"Quando usar (gatilhos completos)", sem perder conhecimento.

  python3 infra/catalogo_enxuto.py            aplica nas skills do repositório (idempotente)
  python3 infra/catalogo_enxuto.py --medir    só mede o tamanho do catálogo
"""
import glob, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIMITE = 650
CURTA = {
 "gabinete": "Porta de entrada do Luis: confere se o pedido já existe (porteiro), decide quais áreas entram e com que profundidade (consulta, área, comitê ou Conselho) e consolida um parecer único. Use quando o Luis trouxer uma necessidade sem área clara: \"preciso de apoio em…\", \"valida isso\", \"quem precisa ver isso?\", \"isso já foi feito?\", \"leva para as áreas\".",
 "central-agentes": "Central de Agentes: pedidos do time pelo painel ou por e-mail [AGENTES]; tria, aciona a área, responde em 3 blocos e trata Aprovado/Não aprovado/Nova análise. Use quando a rotina da Central disparar ou se falar em pedido aos agentes, catálogo de pedidos, SLA da Central, pedido parado ou reprocessar pedido.",
 "conselho-partners": "Conselho Consultivo do Luis: seis conselheiros e um presidente analisam estratégia, meta, preço, remuneração de parceiro e produto novo, com pré-mortem e valor esperado, e entregam ata com o que fazer e o que NÃO fazer. Use para \"reunião do conselho\", \"vale a pena fazer?\", \"leve ao conselho\", triagem de pendências ou registrar decisões.",
 "arquiteto-agentes": "Arquiteto de Agentes: dono do padrão sênior e do auditor; desenha, avalia (casos de teste) e evolui os agentes, mede ROI de IA e conduz o Luis na estrutura de agentes do time. Use para criar, avaliar, fundir ou desligar agentes, padrão sênior, nota do auditor, Semana 0, piloto, autonomia ou ROI de IA.",
 "celula-daniela": "Central Masters (Daniela, 9 Masters): triagem e SLA de demandas, retorno ao parceiro, plano de conta e QBR, apoio jurídico ao canal, higiene do CRM e ganhos a completar. Tudo é rascunho para a Daniela. Use para demanda de Master, \"responder parceiro\", cobrar área, briefing ou saúde de conta, reunião com cliente e parceiro, atualizar CRM.",
 "celula-jenifer": "Central BDR (Jenifer): listas de prospects por Master, segmento e UF, qualificação, cadência e abordagem por persona, objeções técnicas, LGPD na prospecção, preparação e pós-reunião, recrutamento de escritórios contábeis. Use para \"lista de prospects\", \"prospectar para o Master X\", follow-up, mensagem de abordagem, briefing de reunião.",
 "recuperador": "Recuperador (Geovana): fila semanal dos negócios perdidos e parados com chance de reanálise, folha curta de decisão do lote, fichas com hipótese de tese e documento que decide, recorrência e passivo na fila, indicadores do piloto. Use para perdidos, zerados, reanálise, lote da semana, tabela de teses por perfil, vetos, look-alike.",
 "revisor-diagnostico": "Revisor de Diagnóstico (Geovana): segunda opinião antes do cliente; aponta teses esperadas e não analisadas pelo perfil oficial da empresa, lê o parecer do técnico e diz o registro do SPED que decide. Use para revisar diagnóstico, \"o que o técnico não pegou\", teses faltando, DIFAL, ICMS-ST, ISS, IPI não recuperável.",
 "apresentacao-diagnostico": "Apresentação do Diagnóstico: transforma o diagnóstico tributário revisado no deck ao cliente (PDF e PowerPoint no padrão Save), com narrativa, objeções do empresário, case do segmento, esteira Destravar caixa → Proteger e controlar → Crescer e revisão de promessas. Use para deck do diagnóstico, apresentar o diagnóstico, case por segmento, objeção do cliente.",
 "depto-tributario": "Tributário & Contábil: teses de recuperação (PIS/COFINS, insumos, exclusões da base: ICMS, ICMS-ST, ISS Tema 118, Tema 843), alíquota zero só via PER, reforma e saldos credores até 31/12/2026, agro e Funrural, evidência no SPED, decadência. Pré-análise para validação do técnico. Use para qualquer dúvida tributária, tese, PER, CBS/IBS, SPED.",
 "depto-juridico": "Jurídico: Gestão de Passivo (transação PGFN e RFB, CAPAG, dívida ativa, CND, Funrural antigo), estruturação patrimonial e sucessória (ITCMD, holding, dividendos), prazos e contencioso administrativo (intimação, despacho, manifestação de inconformidade, CARF) e o que a Save pode fazer (CVM, Bacen, OAB, LGPD). Pré-análise para o advogado. Use para qualquer dúvida jurídica.",
 "depto-save-invest": "Save Invest (dono: Junior): Gestão de Contas e cobrança, antecipação de recebíveis e FIDC. O cliente contrata, a Save Invest presta, a Federal Invest financia. Use para cobrança, inadimplência, contas a receber, régua de cobrança, antecipar duplicata, limite sobre a carteira, capital de giro, caixa apertado, FIDC, multicedente, Federal Invest.",
 "depto-internacional": "Produtos Internacionais (João Mattos e Paulo): tax internacional e comércio exterior (pronto: preço de transferência, offshore, remessas, câmbio, CBE, drawback) e, em validação, Crédito Internacional, Maquila no Paraguai, captação de capital, home equity, passivo bancário e turnkey. Use para crédito internacional, funding, dólar, café e agro, Paraguai, investidor, exportação.",
 "depto-solucoes": "Contas e Soluções: dono da esteira (Destravar caixa → Proteger e controlar → Crescer) e do mapa da conta; lê DRE, balanço e SCR, playbooks de 6 setores, business case e cross-sell com encaminhamento ao dono de cada produto. Use para \"o que mais esse cliente pode contratar?\", cross-sell, mapa da conta, dossiê, ROI do cliente, QBR com o Master.",
 "depto-pos-venda": "Pós-venda: acompanha o crédito até o dinheiro — prazo de 360 dias do PER, Selic, intimações, compensação de ofício, guias, extrato e saldo de créditos, aviso de pagamento e recorrência das novas competências. Rascunhos para a área e para a Daniela. Use para pós-venda, ressarcimento, compensação de ofício, \"quanto falta receber\", recorrência.",
 "depto-intel-comercial": "Inteligência Comercial: perfil de cliente ideal por produto, tamanho de mercado (empresas no Lucro Real por UF e segmento), lead scoring e look-alike, território por Master, concorrência e recrutamento de escritórios contábeis. Use para ICP, segmento ou região para prospectar, scoring, território, conflito de canal, battlecard, novos parceiros indicadores.",
 "depto-operacoes-canal": "Operações de Canal: repasse e comissão do parceiro (percentual negociado por Master, D64; produtos 2027 a 10% do líquido Save, D78/D97), retenções no pagamento, extrato e prestação de contas, registro de oportunidade e conflito de canal, política e níveis do programa. Use para repasse, comissão, quanto devemos ao parceiro, extrato, conflito de canal.",
 "depto-contratos": "Contratos: lê e prepara contratos de recuperação tributária, de parceiro (indicação × representação × correspondente) e dos produtos 2027; assinatura eletrônica, distrato, cobrança de honorário e conferência de dados na Receita. Nunca envia nem assina. Use para contrato, minuta, cláusula, aditivo, distrato, assinatura pendente, honorário de êxito.",
 "depto-partner-success": "Partner Success: Academia de parceiros por tese e por produto 2027, onboarding 30/60/90, níveis e jornada do Programa Partners 2027, saúde, ativação e churn de parceiro, comunidade e eventos. Use para capacitação, certificação, \"o parceiro não sabe vender\", parceiros dormentes, níveis do programa, reativação.",
 "depto-resultados": "Resultados & Controladoria: relatório semanal (deck e one-pager) com receita contratada, reconhecida e recebida, margem e DRE da área, forecast por etapa e por coorte, ROI e caixa, preço e fee, metas e medição por produto 2027. Use para resultado da semana ou do mês, números da área, margem, forecast, pipeline, meta, ROI, deck para a diretoria.",
 "depto-dados": "Dados & BI: download diário do HubSpot (só leitura), painel de qualidade do CRM, saneamento de duplicados, dicionário de campos e métricas, scorecard e saúde dos Masters, estatística (look-alike, coortes). Use para qualidade de dados, limpeza do HubSpot, duplicados, negócios parados, ranking de parceiros, painel ou BI.",
 "depto-qualidade": "Qualidade & Ouvidoria: auditor de promessas em todo material externo, controle das entregas dos agentes, incidentes e reclamações, NPS e voz do parceiro, melhoria contínua. Use para \"isso pode prometer?\", revisar material, reclamação de parceiro ou cliente, causa-raiz, NPS, qualidade das respostas dos agentes.",
 "depto-marketing": "Marketing de canal: calendário de campanhas com datas fiscais reais, ABM por Master, kits de venda por produto e tese, textos para WhatsApp, e-mail e LinkedIn, peças no padrão Save, conformidade publicitária (OAB, CONAR, CVM) e jornal diário. Use para campanha, post, kit para parceiro, peça visual, \"pode publicar?\", datas comemorativas.",
 "depto-pessoas": "Pessoas: remuneração variável e comissões (CLT), metas e desempenho, capacitação técnica do time, recrutamento e carreira, clima, 1:1 e conversas difíceis, conformidade CLT e LGPD. Rascunhos confidenciais para o Luis. Use para PDI, feedback, metas individuais, bônus, comissão, PLR, perfil de vaga, onboarding, clima.",
 "depto-ti": "TI & Automação: integrações (Graph, HubSpot, GLPI, WhatsApp, Bitrix), Entra ID/SSO e acessos, segurança e LGPD técnica, incidentes, rotinas agendadas, custos e capacidade, governança de IA. Redige pedidos e especificações para o TI da Save. Use para GLPI, API, e-mail parado, SSO, token, falha de rotina, backup, custo de ferramenta, inventário de agentes.",
}


def medir():
    tot = 0
    for f in glob.glob(os.path.join(REPO, "skills/*/SKILL.md")):
        m = re.search(r"^description:\s*(.*?)\n(?=[a-z_-]+:|---)", open(f, encoding="utf-8").read(), re.S | re.M)
        tot += len(m.group(1)) if m else 0
    return tot


def aplicar():
    for area, curta in CURTA.items():
        f = os.path.join(REPO, "skills", area, "SKILL.md")
        if not os.path.exists(f): print("sem", area); continue
        s = open(f, encoding="utf-8").read()
        m = re.search(r"^description:\s*(.*?)\n(?=[a-z_-]+:|---)", s, re.S | re.M)
        if not m: print("sem description", area); continue
        longa = m.group(1).strip()
        q = "'" + curta.replace("'", "''") + "'"
        if longa == q: continue
        assert len(curta) <= LIMITE, (area, len(curta))
        s = s[:m.start(1)] + q + s[m.end(1):]
        if longa != curta and "## Quando usar (gatilhos completos)" not in s:
            fim = s.index("---", s.index("---") + 3) + 3
            s = s[:fim] + "\n\n## Quando usar (gatilhos completos)\n" + longa + "\n" + s[fim:]
        open(f, "w", encoding="utf-8").write(s)
    print("catálogo:", medir(), "caracteres")


if __name__ == "__main__":
    print(medir()) if "--medir" in sys.argv else aplicar()
