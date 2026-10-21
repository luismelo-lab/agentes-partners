#!/usr/bin/env python3
"""Santa Clara, recomeço (21/10/2026): como o ecossistema Save ajuda diante das maiores dores do segmento. 9 slides, linguagem simples.
As versões anteriores ficam em arquivo-morto/ e não são reaproveitadas. Uso: python3 montar_ppt.py && python3 render_ppt.py"""
import json
from pathlib import Path
S = []
A = S.append
A(dict(tipo="capa", foto="pex-13340333.jpg", titulo="Margem, caixa e imposto: do campo à gôndola", sub="Como o ecossistema Save ajuda diante das maiores dores do seu segmento. Apresentação à presidência · outubro de 2026",
       notas="Abertura (1 min). Conversa em quatro dores e uma pergunta para cada. Pré-análise com dados públicos, sem acesso aos números internos; não substitui parecer tributário; nenhuma promessa de valor, prazo ou êxito."))
A(dict(tipo="numeros", big=True, fs=94, titulo="Quatro pressões sobre a margem de quem produz leite e carne.", itens=[
    ("−19,9%", "Preço → Oxigenar", "no preço pago ao produtor de leite, 4º tri/2025 contra 4º tri/2024"),
    ("+22%", "Dinheiro caro → Oxigenar", "ao ano: média de mercado no capital de giro (não é o custo da cooperativa)"),
    ("2027", "Imposto → Estruturar", "CBS em alíquota cheia e fim do PIS/COFINS"),
    ("+6,2%", "Exportação → Escalar", "no volume exportado de carne suína; a receita subiu só 1,3% (jan–set/2026)")],
    fonte="IBGE (SIDRA 1086, estatística experimental); Banco Central (SGS 20725, ago/2026); LC 214/2025; ABPA (jan–set/2026). Consulta em 21/10/2026.",
    notas="As quatro maiores dores do segmento, uma por coluna. Em 12 meses o preço do leite ao produtor ficou em −1,5% (2T25 a 2T26): dizer isso se perguntarem. A taxa de capital de giro de mercado aparece como mais de 22% porque as bases consultadas trazem 22,55% e 22,89%: confirmar no SGS 20725 antes de citar o número exato; é média de mercado, não o custo da cooperativa. Ração (64,8% a 72,1% do custo do suíno) e varejo (receita +3,9% contra volume +0,6%) são apoio de fala."))
A(dict(tipo="esteira", titulo="Três frentes, uma só conversa.", etapas=[
    ("Oxigenar · dores 1 e 2", ("Mais caixa e menos dívida cara, por instituições autorizadas.", "quando o caixa aperta ou o prazo de recebimento é longo.")),
    ("Estruturar · dor 3", ("Imposto e estrutura em ordem, com análise caso a caso.", "quando é preciso manter o ganho e a reforma se aproxima.")),
    ("Escalar · dor 4", ("Crescer e vender mais longe.", "quando há projeto de investimento ou de venda fora do RS."))],
    barra="Um gestor de projeto conduz as três frentes e conecta as equipes tributária, jurídica e financeira.",
    notas="O ecossistema em uma tela (2 min). As frentes se encadeiam: respirar, organizar, crescer. Cada dor a seguir mostra em qual frente a Save entra."))
A(dict(tipo="dor", foto="pex-66400.jpg", pos="center", rotulo="DOR 1 · PREÇO", titulo="O preço do leite caiu e a margem sente primeiro.", numero="−19,9%", legenda="no preço pago ao produtor, 4º trimestre de 2025 contra o de 2024 (R$ 2,76 para R$ 2,21). Em 12 meses, até o 2º tri/2026, −1,5%. Média Brasil.",
    frente="COMO AJUDAMOS · OXIGENAR", entrega="Olhamos os números de cada negócio com vocês para achar onde a margem escapa, do leite à loja.", pergunta="O preço pago ao produtor acompanhou o preço de venda em cada linha?",
    fonte="IBGE, Pesquisa Trimestral do Leite (SIDRA 1086, estatística experimental). Consulta em 21/10/2026.",
    notas="Dor 1. A Save não mexe no preço de mercado; entra onde a cooperativa tem controle. Pedir a margem por produto, planta e loja."))
A(dict(tipo="dor", foto="centro-distribuicao.jpg", rotulo="DOR 2 · CAIXA E DÍVIDA", titulo="O dinheiro fica preso e custa caro.", numero="+22%", legenda="ao ano: média de mercado no capital de giro (não é o custo da cooperativa). Linhas rurais oficiais dependem de enquadramento e são analisadas caso a caso.",
    frente="COMO AJUDAMOS · OXIGENAR", entrega="Gestão de Contas, antecipação e FIDC, por instituições autorizadas (Save Invest). A Save não concede crédito nem garante aprovação.", pergunta="Quanto custa hoje a dívida e em quantos dias a cooperativa recebe?",
    fonte="Banco Central (SGS 20725, ago/2026).",
    notas="Dor 2. O Plano Safra aparece só como contexto: o 9% é do Pronamp (médio produtor, pessoa física) e não se aplica a cooperativa; não comparar taxa. Crédito Internacional, captação e home equity só como pergunta."))
A(dict(tipo="dor", foto="laticinios.jpg", rotulo="DOR 3 · IMPOSTO", titulo="O imposto muda em 2027, e as regras de crédito já mudaram em 2026.", numero="2027", legenda="CBS em alíquota cheia e fim do PIS/COFINS (IBS e ICMS em transição até 2032). Desde 01/04/2026, a LC 224 limita créditos presumidos da agroindústria; o efeito depende de cada produto.",
    frente="COMO AJUDAMOS · ESTRUTURAR", entrega="Análise dos créditos e da transição, separando ato cooperativo e não cooperativo, com o jurídico da cooperativa.", pergunta="Os créditos do leite e dos suínos estão apurados e documentados? Estão prontos para 2027?",
    fonte="LC 214/2025 (transição); LC 224/2025; Lei 10.925/2004. Legislação consultada em 21/10/2026.",
    notas="Dor 3. Leite e queijos podem estar na cesta básica da LC 214 (art. 4º, §8º, III da LC 224 exclui a cesta do corte de 90%) e a carne suína (art. 8º da Lei 10.925) pode ser afetada: o Tributário confirma antes. O crédito de PIS/COFINS escriturado até 31/12/2026 é preservado (LC 214, art. 378). Respeitar a Lei 5.764 e o ato cooperativo, com o Jurídico. Sem 'holding'."))
A(dict(tipo="dor", foto="frigorifico.jpg", rotulo="DOR 4 · EXPORTAÇÃO", titulo="Exportar mais não está trazendo mais receita.", numero="+6,2% × +1,3%", nf=100, legenda="a carne suína exportada cresceu 6,2% em volume e só 1,3% em receita (jan–set/2026). Em setembro: −11% e −21,5%.",
    frente="COMO AJUDAMOS · ESCALAR", entrega="Avaliamos o imposto das vendas externas e, caso a caso, alternativas de operação fora do Brasil com especialistas locais. Sem conclusão antes da análise.", pergunta="O que mudaria se parte da operação fosse fora do Brasil?",
    fonte="ABPA, balanço de set/2026 (divulgado em 07/10/2026).",
    notas="Dor 4. Paraguai só como dor, entrega e pergunta (autorizado pelo Luis em 21/10); sem mecânica, percentuais, leis ou simulações. Pendências internas: MQ-Q1, MQ-Q6 e D59 com o João Mattos. Usar o número da ABPA."))
A(dict(tipo="fim", titulo="Vamos começar pelos números de vocês?", a="<b>Próximo passo</b><br>Reunião com a diretoria financeira e fiscal.", b="<b>Confidencialidade</b><br>NDA antes de abrir qualquer dado.", c="<b>Documentos</b><br>Lista do que precisamos ver em cada negócio.",
    notas="Usamos os documentos só para esta análise (LGPD). Nunca pedimos senhas; certificado digital só mediante contrato e procuração. Simulador de cenários em Excel (Santa-Clara-Simulador-Cenarios.xlsx) só depois do NDA."))
A(dict(tipo="fontes", texto="<b>IBGE</b> · SIDRA 1086, preço do leite ao produtor (estatística experimental), e IPCA<br><b>Banco Central</b> · SGS 20725, capital de giro de pessoas jurídicas (ago/2026)<br><b>ABPA</b> · balanço de set/2026 (divulgado em 07/10/2026) e Relatório Anual 2026<br><b>Legislação</b> · LC 214/2025, LC 224/2025, Lei 10.925/2004 e Lei 5.764/1971, consultadas em 21/10/2026<br><b>Imagens ilustrativas</b> · acervo do site da Cooperativa Santa Clara e banco de imagens Pexels (licença gratuita); não representam necessariamente a operação<br><br>Consulta em 21/10/2026. Pré-análise com dados públicos; não substitui parecer.", notas="Fontes: fora da fala; vai no PDF."))
S = [S[i] for i in (0, 1, 3, 4, 5, 6, 2, 7, 8)]
dest = Path.home() / "agentes-partners/departamentos/tributario/apresentacao-diagnostico/santa-clara/deck_ppt.json"
json.dump({"slides": S}, open(dest, "w"), ensure_ascii=False, indent=1); print(len(S), "slides ->", dest)
