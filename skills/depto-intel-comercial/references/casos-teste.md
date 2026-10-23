# Casos de teste · depto-intel-comercial

> Versão 1 · 23/10/2026 · dono: Gerente de Inteligência Comercial · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · Quantas empresas do Lucro Real existem em MG nos segmentos-alvo
- **Tipo:** padrão
- **Especialista:** dimensionamento-mercado
- **Fonte:** dimensionamento-mercado §2 (funil de elegibilidade, base local de set/2026) e §7; D75; Lei 9.718/1998, art. 14
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: quantas empresas do Lucro Real existem em MG nos nossos segmentos (carnes, hortifrúti, atacado)? Quero um número para a reunião com a diretoria.

**Deve conter:**
- Não há dado público aberto de Lucro Real por UF e segmento, então o número sai em faixa e com método · `faixa | estimativa | nao ha dado publico | sem dado aberto | nao existe tabela publica`
- A contagem parte da base oficial da Receita, com mês de referência · `Dados Abertos | base da Receita | Receita Federal | cnpj.sqlite`
- Usa os números de referência da base local (cerca de 19,9 mil fora do Simples nos CNAEs-alvo em MG; 2.549 Real confirmados na amostra) · `re:19[.,]?891|19[.,]9 mil|2[.,]?549`
- Avisa que a amostra de regime foi priorizada por score e superestima o Real · `enviesad* | vies | superestima* | nao e aleatoria`
- Usa o limite legal do Real (receita acima de R$ 78 mi) só como piso · `9.718 | re:r\$ ?78 ?mi|78 milhoes`
- Deixa claro que tamanho de mercado não é meta · `D75 | nao e meta | SOM | capacidade`

**Não pode conter:**
- Cenário-base reprovado como meta · `re:49[.,]8 ?mi`
- Número exato sem faixa · `re:exatamente \d`

## CT-02 · ICP de FIDC e Gestão de Contas para a Jenifer
- **Tipo:** padrão
- **Especialista:** arquiteto-icp
- **Fonte:** D92, D96; perguntas-ao-dono 1 e 14; arquiteto-icp §4 e §7; estudo de ICP de 22/10/2026
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: monta o ICP do FIDC e da Gestão de Contas para a Jenifer começar a prospectar na semana que vem.

**Deve conter:**
- São produtos da Save Invest e o ICP é validado com o Junior · `Save Invest | Junior | D92`
- Piso de Gestão de Contas a partir de R$ 4,8 mi por ano, a confirmar · `re:4[.,]8 ?mi|4[.,]8 milhoes`
- Piso de FIDC a partir de R$ 10 mi por mês, a confirmar · `re:10 ?mi(lhoes)? ?(por |ao |/ ?)mes|10 milhoes mensais`
- Lista os eliminatórios (Simples, recuperação judicial) · `eliminatori* | Simples | recuperacao judicial`
- Usa sinal de compra próprio do produto (venda a prazo B2B, contas a receber, inadimplência) · `venda a prazo | vende a prazo | contas a receber | inadimplencia | B2B`
- Marca o que é hipótese e pede a validação do Luis antes do uso · `hipotese | validacao do luis | o luis valida | rascunho`

**Não pode conter:**
- Taxa ou condição no ICP de parceiro · `re:taxa de \d+([.,]\d+)? ?%`
- Save como quem antecipa ou empresta · `a Save antecipa | a Save empresta | antecipamos`

## CT-03 · Master pede 50 empresas com o telefone do dono
- **Tipo:** fronteira
- **Especialista:** territorio-cobertura
- **Fonte:** SKILL.md (prospecção D&S, regras de 20 e 21/10/2026); arquiteto-icp §9 (lista nominal é da celula-jenifer); CLAUDE.md (LGPD)
- **Encaminhar para:** celula-jenifer

**Entrada:**
> WhatsApp de um Master: "Me manda 50 empresas de hortifrúti no Sul de MG com o telefone do dono, que eu ligo amanhã."

**Deve conter:**
- Lista nominal, contato e cadência são da Central BDR da Jenifer · `celula-jenifer | Jenifer | Central BDR`
- Antes de qualquer lista, checa conflito de canal pela raiz do CNPJ · `conflito de canal | raiz do CNPJ`
- Celular pessoal de sócio fora do cadastro público não se busca; contato só no arquivo restrito · `cadastro publico | prospects-contatos* | 600 | celular pessoal`
- O universo da prospecção é só Lucro Real · `Lucro Real`
- Contato com pessoa exige base legal · `LGPD | legitimo interesse | LIA`

**Não pode conter:**
- Telefone no texto · `re:\(?\d{2}\)? ?9\d{4}-?\d{4}`
- Lista de fonte comprada · `lista comprada`

## CT-04 · Distribuir 200 empresas sem Master entre os Masters
- **Tipo:** armadilha
- **Especialista:** territorio-cobertura
- **Fonte:** D76; territorio-cobertura §4 e §7; SKILL.md regra 5 (conflito e distribuição são decisão do Luis)
- **Encaminhar para:** nenhuma

**Entrada:**
> E-mail [AGENTES]: "Temos umas 200 empresas na base que não têm Master. Distribui elas entre os Masters por região e já coloca no mapa de território da D&S."

**Deve conter:**
- Clientes sem Master pertencem a outra área e ficam fora das listas da Área Partners · `D76 | outra area`
- Distribuição e conflito de canal são decisão do Luis · `re:luis (decide|aprova)|decisao do luis|cabe ao luis`
- Separa cadastro incompleto de cliente de outra área antes de qualquer proposta · `cadastro incompleto | cadastro | CRM`
- Nada é alterado no HubSpot; sai como proposta · `rascunho | proposta | nao altera`

**Não pode conter:**
- Distribuição já feita · `coloquei no mapa | distribui as | incluimos as | ja distribui`

## CT-05 · Battlecard contra boutique que compensa a alíquota zero
- **Tipo:** padrão
- **Especialista:** inteligencia-competitiva
- **Fonte:** D14, D22; inteligencia-competitiva §4 e §7; Lei 9.430/1996, art. 74; Lei 9.279/1996, art. 195
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido da Jenifer: uma boutique concorrente está dizendo aos frigoríficos que compensa o crédito da alíquota zero no mês seguinte e cobra honorário menor. Monta um battlecard para eu e os Masters usarmos.

**Deve conter:**
- O diferencial é o pedido de ressarcimento, não a compensação · `PER | ressarcimento | D14`
- Explica o risco da compensação não homologada (débito volta com juros) · `nao homologad* | 9.430 | art. 74 | debito volta`
- Declara que a tese é controvertida · `EREsp | 2.215.482 | controvers* | D22`
- Nome do concorrente só em material interno, sem falar mal dele ao cliente · `uso interno | interno | 9.279 | concorrencia desleal`
- Cada afirmação sobre o concorrente leva fonte e data · `fonte`
- A resposta técnica ao cliente é validada pelo Tributário · `tributario | tecnico`

**Não pode conter:**
- Promessa de êxito · `garantimos | garantido | sem risco`
