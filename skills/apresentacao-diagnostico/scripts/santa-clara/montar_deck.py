#!/usr/bin/env python3
"""Monta o deck.json da apresentação à Cooperativa Santa Clara (padrão comercial, igual à Brasol), com fotos da cooperativa em fotos/.
Uso: python3 montar_deck.py && python3 ../render_comercial.py . Santa-Clara-Apresentacao"""
import json, sys
from pathlib import Path
LEG = "Estimativas preliminares sujeitas a validação técnica. Sem promessa de valor, prazo ou êxito."
S = []
A = S.append
A(dict(tipo="capa", foto="laticinios", rotulo="Apresentação à presidência · Outubro de 2026", titulo="Mais lucro e mais margem em todo o ecossistema da Santa Clara", subtitulo="Do campo à gôndola: o mercado, as dificuldades de cada negócio, o espelho na cooperativa, como podemos ajudar e o que cada fração vale.", linha="Pré-análise · estimativas preliminares · sem promessa de valor, prazo ou êxito", notas="Abertura (1 min): o objetivo é mais lucro e mais margem, negócio por negócio. Tudo que vem de mercado tem fonte e data; sobre a cooperativa usamos só o que é público."))
A(dict(tipo="imagem", arquivo="save.jpg", notas="Quem somos (1 min): slide institucional da Save Co. Sem citar clientes nem resultados."))
A(dict(tipo="passos", foto="racoes", rotulo="Nosso ponto de partida", titulo="Todo o trabalho serve a um objetivo: mais lucro e mais margem", passos=[
    dict(titulo="O mercado", texto="O que os dados oficiais mostram nos negócios em que a Santa Clara atua."),
    dict(titulo="As dificuldades", texto="Onde a margem está sob pressão, negócio por negócio."),
    dict(titulo="O espelho", texto="Como cada pressão chega à cooperativa, com o que é público."),
    dict(titulo="Como podemos ajudar", texto="Uma esteira única: o fim de um passo abre o próximo."),
    dict(titulo="O que cada fração vale", texto="Valor de cada ponto de margem, de prazo e de custo de capital.")], altura=420,
    leg="Dados de mercado de fontes oficiais ou, quando indicado, da imprensa, sempre com fonte e data. Sobre a cooperativa, só informações públicas.", notas="Roteiro (1 min)."))
A(dict(tipo="painel", foto="varejo", rotulo="O ecossistema Santa Clara", titulo="Do campo à gôndola: cinco frentes que se alimentam entre si", tit=44, topo=290, wval=1, pad=12, fh3=26, ftx=19, blocos=[
    dict(tag="Campo e associados", titulo="Quase 5 mil famílias; cerca de 2,4 mil fornecem leite", texto="166 municípios; rebanho de 48 mil vacas em lactação (2024); genética própria e sete suinoculturas."),
    dict(tag="Laticínios", titulo="3 indústrias, mais de 1 milhão de litros por dia", texto="Mais de 200 itens: leite UHT, 51 tipos de queijo, requeijão, bebidas lácteas e proteicas."),
    dict(tag="Frigorífico e charcutaria", titulo="2 frigoríficos; Vila Lângaro assumida em 2025", texto="600 suínos por dia na unidade; mais de 100 itens, entre embutidos, salames, presunto cru e carnes."),
    dict(tag="Rações, doces e food service", titulo="2 fábricas de ração e linha para food service", texto="Doces de frutas, queijos, cremes, recheios e carnes para o food service."),
    dict(tag="Distribuição e varejo", titulo="7 centrais, novo centro em Carlos Barbosa, 30 lojas", texto="Entre supermercados e 15 lojas agropecuárias; 60% da produção vai para fora do RS.")],
    leg="Fontes: Cooperativa Santa Clara (site, jul e ago/2026); SuperVarejo (mar/2025); Jornal do Comércio (ago/2024 e ago/2025). Números de estrutura variam entre publicações e estão sujeitos a confirmação.", notas="Ecossistema (2 min). Números públicos, sujeitos a confirmação com a cooperativa."))
A(dict(tipo="painel", foto="centro-distribuicao", rotulo="Visão geral · pressões por negócio", titulo="Cada negócio enfrenta uma pressão diferente sobre a margem", tit=44, topo=290, wval=340, fval=22, pad=11, fh3=26, ftx=19, blocos=[
    dict(tag="Campo e leite", titulo="Preço pago ao produtor em queda e recuperação", texto="Com volume recorde de leite no país. IBGE, Pesquisa Trimestral do Leite.", valor="R$ 2,76 → 2,21 → 2,70", valor_leg="1T25 → 4T25 → 2T26"),
    dict(tag="Laticínios", titulo="Importação de lácteos em alta", texto="Antidumping ao leite em pó da Argentina e do Uruguai. DERAL/SEAB-PR; MDIC.", valor="+26%", valor_leg="importação no 1T26"),
    dict(tag="Frigorífico suíno", titulo="Mais suínos, carne de porco mais barata", texto="Ração de 65% a 72% do custo de produção. IBGE; Embrapa.", valor="+4,3%", valor_leg="abate no Brasil em 2025"),
    dict(tag="Varejo", titulo="A receita cresce mais que o volume", texto="Supermercados, agosto/2026. IBGE, Pesquisa Mensal de Comércio.", valor="+3,9% × +0,6%", valor_leg="receita × volume"),
    dict(tag="Insumos e lojas", titulo="Crédito rural oficial custa menos que o de mercado", texto="Plano Safra 2026/27; Banco Central. Elegibilidade caso a caso.", valor="9% × 22,89%", valor_leg="custeio × capital de giro")],
    leg="Fontes: IBGE (SIDRA 1086, 1093, 7060 e 8882); MDIC; DERAL/SEAB-PR; Embrapa; Banco Central; Governo federal. Datas de consulta no anexo.", notas="Visão geral (2 min): uma pressão por negócio, todas com fonte oficial. Detalhes no anexo."))
A(dict(tipo="numeros", foto="associados", rotulo="1 · O mercado · Campo e laticínios", titulo="Em 12 meses o produtor ficou estável e o consumidor pagou 6,3% a mais", itens=[
    dict(valor="−19,9", unidade="%", legenda="no preço ao produtor ao longo de 2025: de R$ 2,76 (1T25) a R$ 2,21 (4T25), Brasil"),
    dict(valor="−1,5", unidade="%", legenda="no preço ao produtor em 12 meses: R$ 2,74 (2T25) para R$ 2,70 (2T26)"),
    dict(valor="+6,3", unidade="%", legenda="no preço ao consumidor de leites e derivados em 12 meses até set/2026; leite longa vida +10,8%")],
    dor="A margem está no meio: entre o preço que o produtor recebe e o que o consumidor paga.",
    leg="Fonte: IBGE, Pesquisa Trimestral do Leite (SIDRA 1086) e IPCA (SIDRA 7060, 12 meses até setembro/2026). Consulta em 21/10/2026.", notas="Preço do leite (3 min): o slide mais forte. Em 2025 o produtor perdeu 20% do primeiro ao último trimestre; em 12 meses ficou estável. Quem captura a diferença em cada linha?"))
A(dict(tipo="banner", foto="frigorifico", rotulo="2 · Dificuldades dos negócios", titulo="Três pressões atravessam todos os negócios", topo=400, cols=[
    dict(tag="Capital caro", titulo="Selic a 13,75% e capital de giro a 22,89%", texto="Capital de giro de pessoas jurídicas em agosto/2026. A cooperativa investe de forma contínua (Casca, R$ 130 milhões; novo centro de distribuição; Vila Lângaro). Cada ponto de custo pesa em todos os negócios."),
    dict(tag="Tributação em transição", titulo="Crédito presumido e reforma", texto="Desde 01/04/2026 a LC 224/2025 limita a 90% os créditos presumidos do art. 8º da Lei 10.925; a aplicação ao leite e queijos será confirmada. Em 2027, CBS plena e fim do PIS/COFINS. Ato cooperativo e não cooperativo têm tratamentos distintos."),
    dict(tag="Concorrência", titulo="Importação de lácteos +26% no 1T26", texto="Antidumping ao leite em pó da Argentina e do Uruguai desde junho/2026. Na leitura da diretoria (2025), a importação e as empresas nacionais são o grande desafio de competitividade.")],
    leg="Fontes: Banco Central; LC 224/2025; LC 214/2025; Lei 10.925/2004; Lei 5.764/1971; DERAL/SEAB-PR; MDIC (Gecex 907/2026); Jornal do Comércio (17/08/2025).", notas="Três pressões (2 min). Leite e queijos estão na cesta básica da LC 214; o corte de 90% e o Anexo I por NCM serão confirmados pelo tributário no diagnóstico."))
A(dict(tipo="painel", foto="expoagas", rotulo="3 · O espelho", titulo="Cada negócio tem um ponto de verificação na conta", tit=44, topo=280, wval=1, pad=9, fh3=24, ftx=17, blocos=[
    dict(tag="Campo e leite", titulo="O preço pago ao produtor acompanhou o preço de venda em cada linha?", texto="Público: cerca de 2,4 mil fornecedores em 166 municípios; pagamento do leite pela qualidade; compra de outras cooperativas."),
    dict(tag="Laticínios", titulo="Qual a margem por categoria e contra o importado?", texto="Público: UHT em Casca; queijos em Carlos Barbosa e Getúlio Vargas; 51 tipos de queijo."),
    dict(tag="Frigorífico e charcutaria", titulo="Qual a margem por produto e quanto custa a ração?", texto="Público: 2 frigoríficos, 7 suinoculturas; Vila Lângaro (600 suínos por dia) assumida em 2025."),
    dict(tag="Rações", titulo="O custo da ração acompanha o preço do milho e do farelo?", texto="Público: 2 fábricas de ração, que sustentam a suinocultura e o leite."),
    dict(tag="Varejo e lojas", titulo="Qual a margem por categoria e o prazo de venda a associados?", texto="Público: 30 lojas, entre supermercados e 15 lojas agropecuárias."),
    dict(tag="Logística e financeiro", titulo="Qual o custo por tonelada, o prazo de recebimento e o custo da dívida?", texto="Público: 7 centrais e novo centro em Carlos Barbosa; 60% da produção fora do RS.")],
    leg="Fontes: Cooperativa Santa Clara (site, jul e ago/2026); SuperVarejo (mar/2025); Jornal do Comércio (ago/2024 e ago/2025).", notas="Espelho (4 min): o que é público e a pergunta que só os números da cooperativa respondem. Convite para a diretoria dizer onde dói mais."))
A(dict(tipo="numeros", foto="varejo", rotulo="3 · O espelho · O tamanho do que está em jogo", titulo="Sobre a projeção de R$ 3 bi, cada fração de margem e cada dia de prazo pesam", itens=[
    dict(valor="R$ 30", unidade="mi", legenda="por ano em cada 1 ponto de margem (0,1 ponto = R$ 3 mi)"),
    dict(valor="R$ 8,2", unidade="mi", legenda="de caixa parado na carteira a cada dia de prazo de recebimento"),
    dict(valor="R$ 3,7", unidade="mi", legenda="por ano em cada R$ 0,01 por litro de leite, em 365 milhões de litros")],
    dor="Faturamento: projeção de R$ 3 bi para 2026 (imprensa, jul/2026). Custo de capital: média de mercado, não o da cooperativa.",
    leg="Cálculos Save sobre dados públicos: Jornal do Comércio (jul/2026); Cooperativa Santa Clara (jul/2026); Banco Central (SGS 20725, agosto/2026). A divisão da receita entre negócios não é pública. " + LEG, notas="Tamanho do jogo (2 min): régua para dimensionar. A 22,89% ao ano, 1 dia vale cerca de R$ 1,9 mi por ano em juros. Pedir o faturamento realizado de 2025."))
A(dict(tipo="roadmap", foto="laticinios", rotulo="4 · Como podemos ajudar", titulo="Uma esteira única: o fim de cada passo é o começo do próximo", etapas=[
    dict(titulo="Destravar caixa", texto="Ver a margem e liberar o que está parado.", ganho="Mais caixa e menos peso", produtos=["1 · Enxergar a empresa por inteiro", "2 · Conferir o que pode ser aproveitado", "3 · Receber mais cedo", "4 · Aliviar a dívida que pesa"]),
    dict(titulo="Proteger e controlar", texto="Manter a margem conquistada e preparar 2027.", ganho="Previsibilidade e controle", produtos=["5 · Deixar a empresa em dia", "6 · Conferir o imposto e preparar 2027", "7 · Dar governança ao dinheiro", "8 · Proteger o patrimônio"]),
    dict(titulo="Crescer", texto="Capital certo, produtor forte e mais valor por quilo.", ganho="Crescimento sustentável", destaque=True, produtos=["9 · Avaliar capital para crescer", "10 · Organizar o crédito da cadeia", "11 · Exportação e tax internacional", "12 · Manter a esteira rodando"])],
    leg="Um gestor de projeto conduz a esteira e só avança quando o passo anterior entregou o que o próximo precisa. Crédito, antecipação e fundos são realizados por instituições autorizadas; a Save Co. não é instituição financeira. Sem promessa de resultado.", notas="Esteira (4 min): 12 passos em 3 movimentos. Passos 9 a 11 são avaliação: sem oferta de captação, Crédito Internacional ou Maquila nesta etapa (só descoberta, até o G2 com o João)."))
A(dict(tipo="painel", foto="frigorifico", rotulo="4 · Como podemos ajudar", titulo="A esteira conecta os negócios entre si, e a margem pode crescer aí", tit=42, topo=280, wval=1, pad=9, fh3=24, ftx=17, blocos=[
    dict(tag="Conta do associado", titulo="Organizar a conta corrente e o crédito da cadeia", texto="A loja agropecuária vende a prazo, o leite entregue paga a conta e o crédito rural financia a safra: menos capital parado e produtor com margem."),
    dict(tag="Compras de leite e de suínos", titulo="Conferir o aproveitamento do crédito", texto="Cada compra pode gerar crédito, conforme o fornecedor, o regime e o enquadramento da cooperativa."),
    dict(tag="Varejo próprio como canal", titulo="Usar o dado de venda para mix, preço e prazo", texto="30 lojas vendem o que a indústria produz e geram dados de venda por categoria."),
    dict(tag="Logística e centrais", titulo="Medir o custo por tonelada e liberar capital de giro", texto="7 centrais e um novo centro servem leite, queijos e carnes."),
    dict(tag="Rações e suinocultura", titulo="Margem por produto e compras com governança", texto="A ração é de 65% a 72% do custo de produção do suíno (GO a SC, 1T26, Embrapa) e abastece também o leite."),
    dict(tag="Genética e qualidade", titulo="Transformar produtividade em margem da cooperativa", texto="Genética própria, concurso de qualidade e pagamento do leite pela qualidade.")],
    leg="Cooperativa Santa Clara (site e imprensa); Embrapa Suínos e Aves. Hipóteses a validar com os números da cooperativa.", notas="Conexões (2 min): um negócio abre o outro. Hipóteses a validar."))
A(dict(tipo="painel", foto="expointer", rotulo="5 · Quanto vale cada fração", titulo="Sensibilidades com premissas à vista, não metas", tit=44, topo=285, wval=380, fval=24, pad=12, fh3=25, ftx=18, blocos=[
    dict(tag="Prazo de recebimento", titulo="Redução de 1, 3 ou 5 dias sobre R$ 3 bi", texto="Custo de capital de mercado de 22,89% ao ano (Banco Central, ago/2026), não o da cooperativa.", valor="R$ 8, 25 e 41 mi", valor_leg="caixa liberado, uma única vez"),
    dict(tag="Prazo de recebimento", titulo="Juros evitados sobre esse caixa", texto="Mesmas premissas; caixa liberado não é lucro.", valor="R$ 1,9, 5,6 e 9,4 mi", valor_leg="por ano"),
    dict(tag="Custo da dívida", titulo="Valor de cada ponto de custo: 2, 4 ou 6 pontos", texto="Sobre R$ 100 mi de dívida, como sensibilidade.", valor="R$ 2, 4 e 6 mi", valor_leg="por R$ 100 mi, ao ano"),
    dict(tag="Margem por negócio", titulo="Valor de cada fração: 0,1, 0,3 ou 0,5 ponto", texto="Sobre a receita de cada negócio: R$ 1, 3 e 5 mi por R$ 1 bi.", valor="R$ 3, 9 e 15 mi", valor_leg="em R$ 3 bi de receita"),
    dict(tag="Crédito do leite e demais teses", titulo="Dimensionado no diagnóstico, com os documentos", texto="Depende de habilitação, regime de apuração e separação entre ato cooperativo e não cooperativo.", valor="a dimensionar")],
    leg="As linhas não se somam e não são metas nem promessa. Taxas e elegibilidade a linhas oficiais são das instituições e dos programas. Cálculos Save; Banco Central (SGS 20725); Lei 10.925/2004 (art. 8º); LC 224/2025. Valor, prazo e êxito só se confirmam depois do diagnóstico; não há garantia de resultado.", notas="Quanto vale cada fração (4 min): sensibilidades, não metas. Caixa liberado é estoque (uma vez); juros evitados e margem são anuais. Não somar. Sem faixa em R$ para o crédito do leite até o tributário confirmar o corte de 90% e o regime."))
A(dict(tipo="passos", foto="racoes", rotulo="Como começamos", titulo="Os primeiros 90 dias e o que precisamos ver", passos=[
    dict(titulo="Ver os documentos (semanas 1–2)", texto="Sob confidencialidade: DRE e balanço dos dois últimos anos por negócio; apuração de PIS/COFINS e crédito presumido, com os créditos escriturados até dez/2026; separação do ato cooperativo; dívidas e custo médio; carteira a receber por canal; compras de leite, suínos, milho e farelo."),
    dict(titulo="Mapa e primeiro passo (semanas 3–8)", texto="Mapa do ecossistema e linha de base de margem, prazo e dívida (passo 1). Primeiro passo de execução, no negócio em que os documentos mostrarem maior potencial."),
    dict(titulo="Valor e diretoria (semanas 9–13)", texto="Primeiro mapa de valor e encontro trimestral com a diretoria. Um gestor de projeto conduz tudo. **Próximo passo:** reunião com a diretoria financeira e fiscal para assinar a confidencialidade e listar os documentos.")], altura=600,
    leg="Usamos os documentos só para esta análise, conforme a LGPD, com acesso restrito. Nunca pedimos senhas nem certificado digital. Pré-análise sujeita a validação técnica e jurídica.", notas="Chamada para ação: reunião com a diretoria financeira e fiscal, confidencialidade e lista de documentos. Data a combinar."))
A(dict(tipo="imagem", arquivo="encerramento.jpg", notas="Encerramento institucional."))
# ANEXO
A(dict(tipo="banner", foto="frigorifico", rotulo="Anexo", titulo="Dados de apoio e detalhamento por negócio", topo=480, cols=[dict(tag="Para abrir se a conversa pedir", titulo="Mercado, esteira por negócio e fontes", texto="Volume de leite, suínos e varejo; crédito rural; os passos da esteira em cada negócio; fontes e avisos.")], notas="Divisória do anexo: não projetar; abrir só se a presidência pedir detalhe."))
A(dict(tipo="numeros", foto="associados", rotulo="Anexo · Leite · Volume", titulo="Captação de leite recorde em 2025, o maior volume da série do IBGE consultada", itens=[
    dict(valor="27,6", unidade="bi L", legenda="de leite adquirido no Brasil em 2025, +8,9% sobre 2024"),
    dict(valor="3,62", unidade="bi L", legenda="no Rio Grande do Sul em 2025, +16,5% sobre 2024, ano das cheias"),
    dict(valor="7,37", unidade="bi L", legenda="no 4º trimestre de 2025, o maior trimestre da série consultada (3T21 a 2T26)")],
    leg="Fonte: IBGE, Pesquisa Trimestral do Leite (SIDRA 1086), série 3º tri/2021 a 2º tri/2026. Consulta em 21/10/2026.", notas="Anexo: volume do leite."))
A(dict(tipo="numeros", foto="frigorifico", rotulo="Anexo · Suínos", titulo="Mais suínos e carne de porco mais barata: a margem exige eficiência", itens=[
    dict(valor="60,7", unidade="mi cab.", legenda="abatidas no Brasil em 2025, +4,3%; no RS, 10,9 milhões (+6,8%)"),
    dict(valor="−8,3", unidade="%", legenda="no preço da carne de porco ao consumidor em 12 meses até set/2026 (IPCA)"),
    dict(valor="+4,8", unidade="%", legenda="em volume exportado, jan–set/2026: 1,03 mi t; receita +0,4% (US$ 2,53 bi)")],
    dor="A ração responde por 64,8% (GO) a 72,1% (SC) do custo de produção do suíno, no 1T26.",
    leg="IBGE, Pesquisa Trimestral do Abate de Animais (SIDRA 1093) e IPCA (SIDRA 7060); Secex/MDIC, jan–set/2026; Embrapa Suínos e Aves. Consulta em 21/10/2026.", notas="Anexo: suínos."))
A(dict(tipo="numeros", foto="varejo", rotulo="Anexo · Varejo", titulo="Nos supermercados, a receita cresce mais que o volume, reflexo sobretudo de preços", itens=[
    dict(valor="+3,9", unidade="%", legenda="receita nominal em agosto/2026 sobre agosto/2025"),
    dict(valor="+0,6", unidade="%", legenda="volume de vendas no mesmo período"),
    dict(valor="+4,2", unidade="%", legenda="alimentação no domicílio (IPCA) em 12 meses até set/2026")],
    leg="IBGE, Pesquisa Mensal de Comércio (SIDRA 8882), hipermercados e supermercados; IPCA (SIDRA 7060). Consulta em 21/10/2026.", notas="Anexo: varejo."))
A(dict(tipo="numeros", foto="racoes", rotulo="Anexo · Crédito rural", titulo="O crédito rural oficial custa menos da metade do capital de giro de mercado", itens=[
    dict(valor="9", unidade="% a.a.", legenda="custeio (Pronamp) no Plano Safra 2026/27, para quem é elegível"),
    dict(valor="22,89", unidade="% a.a.", legenda="capital de giro de pessoas jurídicas no mercado, agosto/2026"),
    dict(valor="13,9", unidade="pontos", legenda="de diferença ao ano; elegibilidade analisada caso a caso")],
    dor="Informativo: diferença de custo entre linhas, sem estimativa de ganho para a cooperativa.",
    leg="Governo federal, Plano Safra 2026/2027 (30/06/2026); Banco Central (SGS 20725). Custo de mercado: média do Banco Central, não o da cooperativa.", notas="Anexo: crédito rural."))
def mov(rot, tit, c1, c2, c3, leg):
    return dict(tipo="banner", foto="frigorifico", rotulo=rot, titulo=tit, topo=360, cols=[
        dict(tag="Campo, leite e laticínios", titulo="", texto=c1), dict(tag="Frigorífico, charcutaria e rações", titulo="", texto=c2), dict(tag="Varejo, lojas e logística", titulo="", texto=c3)], leg=leg, notas="Anexo: esteira por negócio.")
A(mov("Anexo · Destravar caixa", "Destravar caixa: ver a margem de cada negócio e liberar o que está parado",
    "**1** Margem por linha e por região de captação; linha de base de prazo e dívida.\n**2** Crédito presumido do leite e saldo credor, conforme o regime; créditos de energia, frio e embalagem.\n**3** Prazo das grandes redes e do food service; cobrança organizada.\n**4** Perfil da dívida das plantas e do capital de giro da safra.",
    "**1** Margem por produto e por planta; custo da ração.\n**2** Crédito presumido na compra de suínos; créditos de insumos e energia; saldo credor.\n**3** Carteira de atacado e redes; antecipação e gestão de contas, por instituições autorizadas.\n**4** Perfil da dívida da aquisição de Vila Lângaro e do capital de giro.",
    "**1** Margem por loja e categoria; custo logístico por tonelada.\n**2** Exclusão do ICMS e do ICMS-ST da base do PIS/COFINS (STF Tema 69; STJ Tema 1.125); créditos de energia e aluguel.\n**3** Conta corrente do associado; recebíveis de cartão.\n**4** Perfil da dívida de lojas e do novo centro; alongamento a discutir.",
    "Lei 10.925/2004 (art. 8º); LC 224/2025; Lei 5.764/1971. Pré-análise: possibilidades a validar. " + LEG))
A(mov("Anexo · Proteger e controlar", "Proteger e controlar: manter a margem conquistada e preparar 2027",
    "**5** Certidões, autos e processos de todas as unidades.\n**6** 2026: crédito presumido de PIS/COFINS limitado a 90%, a confirmar para leite e queijos. 2027: alíquota zero de CBS e IBS conforme a classificação; saldos de PIS/COFINS preservados se escriturados.\n**7** Painel mensal de margem por linha, associado e região.\n**8** Estrutura societária e patrimonial avaliada com o jurídico da cooperativa, respeitando a Lei 5.764/1971.",
    "**5** Idem, incluindo a unidade assumida em 2025.\n**6** Carnes in natura da cesta (Anexo I) com alíquota zero; embutidos conforme a classificação; créditos de insumos.\n**7** Painel por planta e produto, com custo de ração.\n**8** Estrutura das suinoculturas, frigoríficos e fábricas de ração.",
    "**5** Idem, por loja e por central.\n**6** Mix por classificação fiscal (NCM); tratamento de ICMS-ST; preços e sistemas para CBS e IBS.\n**7** Painel por loja e categoria; conferência de estoque e prazo.\n**8** Organização dos imóveis das lojas e centrais.",
    "LC 214/2025 (Anexo I, cesta básica; conferência por NCM); LC 224/2025. " + LEG))
A(mov("Anexo · Crescer", "Crescer: capital certo, produtor forte e mais valor por quilo vendido",
    "**9** Que investimentos a cooperativa projeta e com que prazo? (R$ 28 mi em 2024 e R$ 35 mi em 2025, segundo a imprensa)\n**10** Como organizar, com instituições, o crédito ao produtor com base na entrega de leite.\n**11** Queijos nobres, bebidas proteicas e whey: mais valor por litro.\n**12** Revisão anual e encontro trimestral com a diretoria.",
    "**9** Expansão do abate e da desossa: qual o projeto e o capital necessário?\n**10** Idem para o suinocultor integrado, com base na entrega de animais.\n**11** Exportação de carne suína e charcutaria premium.\n**12** Margem por planta acompanhada a cada trimestre.",
    "**9** Novo centro de distribuição e expansão do varejo: qual o plano?\n**10** Conta corrente do associado nas lojas agropecuárias organizada.\n**11** Vendas fora do RS (60% da produção): tributação interestadual e logística.\n**12** Painel de valor por loja e por central.",
    "Cooperativa Santa Clara; Jornal do Comércio. Etapa em descoberta: avaliado caso a caso, após a análise dos documentos."))
A(dict(tipo="banner", foto="frigorifico", rotulo="Anexo · Fontes e avisos", titulo="Fontes oficiais e públicas, com data de consulta", topo=330, cols=[
    dict(tag="Oficiais", titulo="IBGE, Banco Central, MDIC, Governo federal", texto="IBGE, SIDRA: leite (1086), abate (1093), IPCA (7060, até set/2026) e comércio (8882, até ago/2026). Banco Central, SGS 432 e 20725. MDIC/Secex, jan–set/2026; Gecex 907/2026. DERAL/SEAB-PR, boletim 18/2026. Embrapa Suínos e Aves (1T26). Plano Safra 2026/27 (30/06/2026). LC 214/2025, LC 224/2025, Lei 5.764/1971. Consulta em 21/10/2026."),
    dict(tag="Públicas, sobre a cooperativa", titulo="Site, imprensa setorial e regional", texto="Cooperativa Santa Clara: site (quem somos, produtos, blog de 29/07 e 14/08/2026). SuperVarejo (mar/2025). Jornal do Comércio: ago/2024, 17/08/2025 e jul/2026."),
    dict(tag="Avisos", titulo="Pré-análise de caráter geral", texto="Sem acesso aos dados internos da cooperativa. Não constitui parecer jurídico ou tributário nem oferta de crédito. As faixas são ilustrativas, com premissas indicadas, e dependem de documentos e de validação técnica. Valor, prazo e êxito não são prometidos; não há garantia de resultado.")], notas="Anexo: fontes e avisos."))
PASTA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "agentes-partners/departamentos/tributario/apresentacao-diagnostico/santa-clara"
json.dump({"nome": "Santa-Clara-Apresentacao", "slides": S}, open(PASTA / "deck.json", "w"), ensure_ascii=False, indent=1)
print(len(S), "slides")
