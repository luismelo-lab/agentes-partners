#!/usr/bin/env python3
"""Conteúdo macro da apresentação Santa Clara (21/10/2026): dificuldades do mercado e as 3 frentes, no layout do PPT institucional.
Roteiro do agente de Soluções + Marketing, ajustado. Uso: python3 montar_ppt.py && python3 render_ppt.py"""
import json
from pathlib import Path
S = []
A = S.append
A(dict(tipo="capa", foto="pex-13340333.jpg", titulo="Margem, do campo à gôndola", sub="Apresentação à presidência da Cooperativa Santa Clara · outubro de 2026",
       notas="Abertura (1 min). O objetivo é conversar sobre margem negócio por negócio: primeiro o mercado de vocês, depois como a Save atua em três frentes. Pré-análise, sem acesso aos dados internos; nenhuma promessa de valor, prazo ou êxito."))
A(dict(tipo="numeros", titulo="A Santa Clara em números: uma cadeia inteira, do campo à gôndola", itens=[
    ("R$ 3 bi", "projeção de faturamento em 2026", "divulgada pela imprensa; não é balanço"),
    ("~5 mil", "famílias associadas", "cerca de 2,3 mil fornecem leite"),
    ("360 mi L", "de leite por ano", "mais de 1 milhão por dia, em 3 indústrias"),
    ("419", "itens com a marca", "291 de laticínios e 128 de carnes e embutidos"),
    ("7 · 2 · 2", "suinoculturas, frigoríficos e fábricas de ração", "do grão ao embutido, dentro de casa"),
    ("30", "lojas próprias", "supermercados e 15 lojas agropecuárias"),
    ("60%", "da produção vendida fora do RS", "7 centrais de distribuição e um novo centro"),
    ("2,3 mil+", "colaboradores", "unidades com FSSC 22000 (2025)")],
    fonte="Cooperativa Santa Clara (site e blog, 2025-26); Jornal do Comércio (jul/2026 e ago/2025); SuperVarejo; Jornal Novo Tempo (ago/2026). Números públicos; variam entre publicações.",
    notas="A Santa Clara em números (2 min): a cadeia inteira, não só o leite. Dados públicos; divergem entre fontes (colaboradores 2,3 a 2,7 mil; lojas 30 ou 31; centrais 7 ou 8): usar faixas e pedir a confirmação. O 360 mi L/ano e o 1 mi L/dia são o mesmo número. Não há balanço público: faturamento realizado, sobras e patrimônio, abate real, produção de ração, exportação por produto e país e investimentos aprovados entram na lista de documentos. Perguntar: qual a divisão do faturamento entre laticínios, carnes, ração e varejo?"))
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
    ("Vendas além do RS", "60% da produção já sai do estado: o que mais pode ir ao exterior?"),
    ("Capital para crescer", "Em avaliação: que investimento pede capital de longo prazo?"),
    ("Crédito da cadeia", "Em avaliação: como organizar, com instituições, o crédito ao produtor.")],
    nota="Itens em avaliação são perguntas, não oferta.", fonte="Sem promessa de valor, prazo ou êxito. Câmbio e financiamento à exportação só como pergunta; itens em avaliação não são oferta.",
    notas="Escalar (3 min). Capital para crescer e crédito da cadeia só como pergunta (descoberta até o G2). Maquila, Paraguai e home equity ficaram de fora: sem aderência a cooperativa de leite e suínos ou em validação."))
A(dict(tipo="numeros", fs=68, titulo="Exportação de carne suína: o volume cresce e o preço pressiona.", itens=[
    ("1,19 mi t", "exportadas de jan a set/2026", "+6,2% sobre o mesmo período de 2025"),
    ("US$ 2,74 bi", "de receita no período", "+1,3%: cresce bem menos que o volume"),
    ("−21,5%", "na receita de setembro", "US$ 289 mi; volume de 135 mil t (−11%)"),
    ("2º", "Rio Grande do Sul entre os estados", "33,8 mil t em setembro; SC lidera com 64,5 mil t"),
    ("Filipinas", "principal destino em setembro", "25,7 mil t, −47,7%; Japão +38,9% e Chile +72%"),
    ("1,51 mi t", "exportadas em 2025", "US$ 3,6 bi; produção de 5,59 mi t"),
    ("1,6 mi t", "projeção ABPA de exportação em 2026, no máximo", "produção projetada de 5,87 mi t"),
    ("3º", "maior exportador mundial de carne suína", "4º maior produtor (ABPA, 2025)")],
    fonte="ABPA: balanço de set/2026 (divulgado em 07/10/2026) e Relatório Anual 2026 (dados de 2025). Consulta em 21/10/2026.",
    notas="Exportação de carne suína (2 min): dados ABPA. Volume cresce 6,2% e a receita só 1,3%: o preço internacional pressiona a margem de quem exporta; setembro caiu 11% em volume e 21,5% em receita (base alta e preços médios menores, segundo a ABPA). RS é o segundo estado exportador. Os números do briefing (1,03 mi t, US$ 2,53 bi) podem ser só in natura; usar o da ABPA, que cobre todos os produtos. Não há acumulado por estado ou destino nas matérias consultadas: baixar do relatório da ABPA se a presidência pedir."))
A(dict(tipo="frente", titulo="Internacionalização: vender mais longe pede imposto e câmbio sob controle.", intro="Para uma cooperativa com carnes e lácteos, o mercado externo pesa. Começa pelo imposto e pela pergunta certa.", itens=[
    ("Tributação das vendas externas", "Imposto das operações fora do país, avaliado caso a caso."),
    ("Exportação de suínos e charcutaria", "Quais produtos e mercados fazem sentido para o frigorífico."),
    ("Câmbio e caixa", "Quanto da receita e da dívida está em moeda estrangeira."),
    ("Financiamento da exportação", "Em avaliação: como organizar o dossiê para instituições autorizadas.")],
    nota="Quanto do crescimento da Santa Clara depende de vender fora do país, e em que moeda estão o caixa e a dívida hoje?", fonte="Sem promessa de valor, prazo ou êxito; itens em avaliação são perguntas, não oferta.",
    notas="Internacionalização (3 min). Autorizada pelo Luis em 21/10 por ser central ao segmento. Pronto: tax internacional e comércio exterior. Descoberta (só pergunta): câmbio, financiamento à exportação (ACC/ACE e seguro de crédito, sem ficha nem condição), Crédito Internacional (até o G2, alvo 15/12/2026; nunca 'fundo'). Maquila e Paraguai fora: frigorífico bloqueado (D59) e baixa aderência a perecíveis. Lei 60/90 foi substituída pela 7.548/2025. Antidumping de leite em pó: Camex reconheceu o dumping mas suspendeu as tarifas; não falar como proteção em vigor. Número suíno: ABPA 1,192 mi t (todos os produtos); o 1,03 mi t do briefing pode ser só in natura (Comex Stat). Frase: 'Pela importância da exportação, incluímos o tema como pergunta e como tributação das vendas externas, que já temos pronta; crédito internacional e maquila estão em validação e aparecem só como perguntas.'"))
A(dict(tipo="frase", foto="pex-8291490.jpg", titulo="Uma resposta para a margem de quem exporta: a Save atua no Paraguai.", fs=82, top=170, w=1300, br=.4, linhas=[
    ("A dor", "Carga tributária e custo de produção comprimem a margem na exportação."),
    ("A nossa entrega", "Presença da Save no Paraguai, com escritório e parceiros em Assunção, para avaliar onde produzir ou industrializar faz sentido."),
    ("A pergunta", "Qual parte da produção ou da logística da Santa Clara ganharia competitividade fora do Brasil?")],
    fonte="Sem promessa de valor, prazo ou êxito. Avaliação caso a caso, com especialistas locais.",
    notas="Paraguai, o diferencial da Save (2 min). Autorizado pelo Luis em 21/10/2026: apresentar como entrega que resolve a dor, sem explicar como funciona. Não citar percentuais, leis, regime ou simulações (as simulações do handoff são ilustrativas e não vão a cliente; números precisam de validação com especialista paraguaio). Se perguntarem como funciona: o regime de maquila é um caminho possível (Lei 1.064/97); a Lei 60/90 foi substituída pela Lei 7.548/2025, conferir antes de citar; o lucro de controlada no exterior segue tributado no Brasil (Lei 12.973, art. 77). Pendências internas: frigorífico bloqueado no simulador (D59) e MQ-Q6 (encaixe da carne) sem resposta do João Mattos; confirmação escrita do escritório em Assunção (MQ-Q1). Por isso a frase é 'avaliar onde faz sentido'. Fonte interna: handoff-ecossistema-save.md, seção 6."))
A(dict(tipo="fim", a="<b>Próximo passo</b><br>Reunião com a diretoria financeira e fiscal.", b="<b>Confidencialidade</b><br>Assinatura do NDA antes de abrir qualquer dado.", c="<b>Documentos</b><br>Lista do que precisamos ver em cada negócio.",
       notas="Chamada para ação: peço a reunião com a diretoria financeira e fiscal, o NDA e a lista de documentos. Usamos os documentos só para esta análise, conforme a LGPD; nunca pedimos senhas; certificado digital só mediante contrato e procuração."))
A(dict(tipo="fontes", texto="IBGE, SIDRA: Pesquisa Trimestral do Leite (1086), Pesquisa Mensal de Comércio (8882) e IPCA (7060), consulta em 21/10/2026. Banco Central, SGS 20725 (capital de giro de pessoas jurídicas, ago/2026). Embrapa Suínos e Aves, CIAS (1T26). Governo federal, Plano Safra 2026/27 (30/06/2026). DERAL/SEAB-PR (importação de lácteos, 1T26). LC 214/2025, LC 224/2025, Lei 10.925/2004 e Lei 5.764/1971. Cooperativa Santa Clara (site, jul e ago/2026: 60% da produção fora do RS, estrutura), SuperVarejo (mar/2025), Jornal do Comércio (jul/2026). Cesta básica: LC 214/2025, Anexo I. Imagens ilustrativas: acervo do site da cooperativa e banco de imagens Pexels (licença gratuita); não representam necessariamente a operação.<br><br>Pré-análise de caráter geral, sem acesso aos dados internos da cooperativa. Não constitui parecer jurídico ou tributário nem oferta de crédito. Valores são ilustrativos e dependem de documentos e validação técnica. Valor, prazo e êxito não são prometidos; não há garantia de resultado.", notas="Fontes e avisos: fora da fala; vai no PDF enviado depois."))
Path(__file__).resolve()
dest = Path.home() / "agentes-partners/departamentos/tributario/apresentacao-diagnostico/santa-clara/deck_ppt.json"
json.dump({"slides": S}, open(dest, "w"), ensure_ascii=False, indent=1); print(len(S), "slides ->", dest)
