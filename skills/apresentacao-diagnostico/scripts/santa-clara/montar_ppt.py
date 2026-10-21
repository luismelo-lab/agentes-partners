#!/usr/bin/env python3
"""Conteúdo macro da apresentação Santa Clara (21/10/2026): dificuldades do mercado e as 3 frentes, no layout do PPT institucional.
Roteiro do agente de Soluções + Marketing, ajustado. Uso: python3 montar_ppt.py && python3 render_ppt.py"""
import json
from pathlib import Path
S = []
A = S.append
A(dict(tipo="capa", foto="pex-13340333.jpg", titulo="Margem, do campo à gôndola", sub="Apresentação à presidência da Cooperativa Santa Clara · outubro de 2026",
       notas="Abertura (1 min). O objetivo é conversar sobre margem negócio por negócio: primeiro o mercado de vocês, depois como a Save atua em três frentes. Pré-análise, sem acesso aos dados internos; nenhuma promessa de valor, prazo ou êxito."))
A(dict(tipo="frase", foto="pex-2771640.jpg", titulo="Cada ponto de margem pesa.", numero="R$ 30", unidade="mi por ano", legenda="para cada ponto de margem sobre R$ 3 bi de receita projetada. Não é meta nem estimativa de ganho", fs=110, top=170,
       fonte="Estimativa Save sobre a projeção divulgada pela imprensa (Jornal do Comércio, jul/2026). Não é meta.",
       notas="Régua (1 min). Margem: R$ 30 mi por ponto sobre R$ 3 bi; 0,1 ponto = R$ 3 mi. É aritmética sobre a projeção pública, não estimativa de ganho. Pedir o faturamento realizado de 2025."))
A(dict(tipo="frase", foto="pex-2887112.jpg", pos="center 40%", titulo="O leite oscila, e o produtor sente primeiro.", numero="−19,9", unidade="%", legenda="no preço ao produtor de 1T25 a 4T25 (R$ 2,76 para R$ 2,21); em 12 meses até o 2T26, −1,5%. Média Brasil", fs=92, top=210,
       fonte="IBGE, Pesquisa Trimestral do Leite (SIDRA 1086). Consulta em 21/10/2026.",
       notas="Dificuldade 1. Média Brasil. Em 12 meses (2T25 a 2T26) o preço ficou em −1,5%: R$ 2,74 para R$ 2,70; o 2T26 já voltou a R$ 2,70. Apoio: importação de lácteos +26% no 1T26 (DERAL/SEAB-PR). Pergunta: o preço pago ao produtor acompanhou o preço de venda em cada linha?"))
A(dict(tipo="frase", foto="racoes.jpg", titulo="No suíno, a ração decide a margem.", numero="65% a 72%", unidade="", legenda="do custo de produção do suíno é ração, de 64,8% (GO) a 72,1% (SC), no 1T26", fs=96, top=210,
       fonte="Embrapa Suínos e Aves (CIAS), custo de produção, 1T26.",
       notas="Dificuldade 2. Apoio: carne de porco ao consumidor −8,3% em 12 meses até set/2026 (IPCA). Pergunta: qual a margem por produto e por planta, e quanto pesa a ração?"))
A(dict(tipo="frase", foto="varejo.jpg", titulo="No varejo, a receita sobe mais que o volume.", numero="+3,9% × +0,6%", unidade="", legenda="receita nominal × volume nos supermercados do Brasil, agosto/2026", fs=92, top=210,
       fonte="IBGE, Pesquisa Mensal de Comércio (SIDRA 8882). Consulta em 21/10/2026.",
       notas="Dificuldade 3. A diferença reflete em boa parte preços (alimentação no domicílio +4,2% em 12 meses). Pergunta: qual a margem por categoria e por loja, e o prazo de venda ao associado?"))
A(dict(tipo="frase", foto="centro-distribuicao.jpg", titulo="O dinheiro de mercado custa mais que o dobro do crédito rural.", numero="22,89% × 9%", unidade="ao ano", legenda="capital de giro de mercado (média) × taxa de custeio rural oficial, quando elegível. Não é o custo da cooperativa", fs=80, top=190, w=1150,
       fonte="Banco Central (SGS 20725, ago/2026); Plano Safra 2026/27 (30/06/2026). Média de mercado, não o custo da cooperativa.",
       notas="Dificuldade 4. Elegibilidade às linhas oficiais analisada caso a caso; a Save não concede crédito. Pergunta: quanto custa hoje a dívida média e em quantos dias a cooperativa recebe?"))
A(dict(tipo="frase", foto="pex-221369.jpg", titulo="O imposto muda em 2026 e de novo em 2027.", numero="90%", unidade="", legenda="teto do crédito presumido de PIS/COFINS desde 01/04/2026, a confirmar para leite e queijos (cesta básica) · CBS plena em 2027", fs=92, top=210,
       fonte="LC 224/2025 (art. 4º, §8º, III); LC 214/2025; Lei 10.925/2004. A aplicação a leite e queijos será confirmada no diagnóstico.",
       notas="Dificuldade 5. Ressalva obrigatória: leite e queijos estão na cesta básica da LC 214 e o corte de 90% pode não alcançá-los; o tributário confirma. Em 2027 a CBS é plena e o PIS/COFINS acaba. Pergunta: o crédito do leite e dos suínos está sendo aproveitado por inteiro e a cooperativa está pronta para 2027?"))
A(dict(tipo="espelho", titulo="Cinco perguntas que só os números de vocês respondem.", itens=[
    ("O preço do leite", "O preço pago ao produtor acompanhou o preço de venda em cada linha?"),
    ("O custo da ração", "Quanto pesa a ração na margem por produto e por planta?"),
    ("A margem por loja", "Qual a margem por categoria e o prazo de venda ao associado?"),
    ("O custo da dívida", "Quanto custa a dívida hoje e em quantos dias a cooperativa recebe?"),
    ("O crédito de 2026 e 2027", "Os créditos do leite e dos suínos são aproveitados por inteiro? Estamos prontos para a reforma?")],
    fonte="Perguntas a partir de informações públicas da cooperativa (site, SuperVarejo, Jornal do Comércio).",
    notas="Espelho (3 min): é aqui que conduzimos a conversa perguntando. As respostas viram a lista de documentos do próximo passo."))
A(dict(tipo="frase", foto="pex-12380134.jpg", titulo="Oxigenar olha o caixa de hoje. Estruturar ajuda a manter o ganho. Escalar prepara o crescimento.", fs=76, top=250, w=1250, br=.5,
       notas="Transição para as três frentes (1 min). Um gestor de projeto conduz as três. As frentes se encadeiam: o que for liberado pode ajudar a organizar o que está atrasado e vira base para estruturar; com controle e margem por negócio, qualquer investimento pode ser medido e apresentado a quem financia."))
A(dict(tipo="frente", titulo="Oxigenar: liberar o caixa que está parado.", intro="Olhar o caixa e o custo da dívida sem depender só da safra. Entra quando o caixa aperta ou o prazo de recebimento é longo.", itens=[
    ("Revisão tributária", "Levantamento de créditos possíveis (leite, suínos, saldo credor), sujeito a análise e validação."),
    ("Gestão de Contas", "Visão de recebíveis, vencidos e prazo para destravar o caixa."),
    ("Antecipação e FIDC", "Operados por instituições autorizadas (Save Invest); a Save não concede crédito. Sujeito a análise jurídica e do estatuto."),
    ("Passivo tributário", "Avaliar transação e parcelamento, se houver.")],
    nota="Em avaliação: a cooperativa considera trocar dívida cara por capital de longo prazo? Liberar caixa não é lucro.", fonte="Sem promessa de valor, prazo ou êxito. A Save Co. não é instituição financeira.",
    notas="Oxigenar (3 min). 1 dia de prazo = R$ 8,2 mi de caixa sobre R$ 3 bi (uma vez; a 22,89% ao ano, cerca de R$ 1,9 mi por ano em juros). Crédito Internacional só como pergunta, até o G2 com o João Mattos; nunca 'fundo'."))
A(dict(tipo="frente", titulo="Estruturar: manter o ganho e chegar pronto a 2027.", intro="Ajudar a manter o ganho e os números sob controle. Entra quando o caixa respira ou a reforma bate à porta.", itens=[
    ("Planejamento tributário e reforma", "Enquadramento tributário correto e preparação para a CBS em 2027."),
    ("Estruturação patrimonial e societária", "Com o jurídico da cooperativa, respeitando a Lei 5.764/1971."),
    ("Prazos e contencioso", "Controle de prazos e certidões fiscais; contencioso administrativo com advogado habilitado."),
    ("BPO fiscal e contábil", "Rotina organizada, com acesso por procuração eletrônica, sem entrega de senhas.")],
    nota="Com controle e margem por negócio, qualquer investimento pode ser medido.", fonte="Sem promessa de valor, prazo ou êxito.",
    notas="Estruturar (3 min). Para cooperativa, o ato cooperativo e a Lei 5.764 exigem validação do Jurídico antes de qualquer fala além do nome do serviço. Sem 'holding'."))
A(dict(tipo="frente", titulo="Escalar: preparar o crescimento com custo de capital e imposto sob controle.", intro="Investir e vender mais longe com custo de capital e imposto sob controle. Só entra depois das outras duas.", itens=[
    ("Tax internacional", "Se houver exportação ou importação: tributação e comércio exterior."),
    ("Vendas além do RS", "60% da produção sai do estado: logística e tributação interestadual."),
    ("Capital para crescer", "Em avaliação: que investimento pede capital de longo prazo?"),
    ("Crédito da cadeia", "Em avaliação: como organizar, com instituições, o crédito ao produtor.")],
    nota="Itens em avaliação são perguntas, não oferta.", fonte="Sem promessa de valor, prazo ou êxito. Itens em avaliação são perguntas, não oferta.",
    notas="Escalar (3 min). Capital para crescer e crédito da cadeia só como pergunta (descoberta até o G2). Maquila, Paraguai e home equity ficaram de fora: sem aderência a cooperativa de leite e suínos ou em validação."))
A(dict(tipo="fim", a="<b>Próximo passo</b><br>Reunião com a diretoria financeira e fiscal.", b="<b>Confidencialidade</b><br>Assinatura do NDA antes de abrir qualquer dado.", c="<b>Documentos</b><br>Lista do que precisamos ver em cada negócio.",
       notas="Chamada para ação: peço a reunião com a diretoria financeira e fiscal, o NDA e a lista de documentos. Usamos os documentos só para esta análise, conforme a LGPD; nunca pedimos senhas; certificado digital só mediante contrato e procuração."))
A(dict(tipo="fontes", texto="IBGE, SIDRA: Pesquisa Trimestral do Leite (1086), Pesquisa Mensal de Comércio (8882) e IPCA (7060), consulta em 21/10/2026. Banco Central, SGS 20725 (capital de giro de pessoas jurídicas, ago/2026). Embrapa Suínos e Aves, CIAS (1T26). Governo federal, Plano Safra 2026/27 (30/06/2026). DERAL/SEAB-PR (importação de lácteos, 1T26). LC 214/2025, LC 224/2025, Lei 10.925/2004 e Lei 5.764/1971. Cooperativa Santa Clara (site, jul e ago/2026: 60% da produção fora do RS, estrutura), SuperVarejo (mar/2025), Jornal do Comércio (jul/2026). Cesta básica: LC 214/2025, Anexo I. Imagens ilustrativas: acervo do site da cooperativa e banco de imagens Pexels (licença gratuita); não representam necessariamente a operação.<br><br>Pré-análise de caráter geral, sem acesso aos dados internos da cooperativa. Não constitui parecer jurídico ou tributário nem oferta de crédito. Valores são ilustrativos e dependem de documentos e validação técnica. Valor, prazo e êxito não são prometidos; não há garantia de resultado.", notas="Fontes e avisos: fora da fala; vai no PDF enviado depois."))
Path(__file__).resolve()
dest = Path.home() / "agentes-partners/departamentos/tributario/apresentacao-diagnostico/santa-clara/deck_ppt.json"
json.dump({"slides": S}, open(dest, "w"), ensure_ascii=False, indent=1); print(len(S), "slides ->", dest)
