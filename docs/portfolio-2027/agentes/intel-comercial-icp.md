# Inteligência Comercial · quem é o cliente de cada produto e como o portfólio 2027 chega ao parceiro

> **22/10/2026 · rascunho do Gerente de Inteligência Comercial (`depto-intel-comercial`), com apoio do Gerente de Marketing de canal (`depto-marketing`: Enablement e Co-branding).** Nada aqui é oferta, taxa, prazo ou promessa. Sem dado de cliente: `<EMPRESA>`. Estado dos produtos vale o de 19/10 do Luis. Marcas: `[BASE]` dado da Save (HubSpot de 19/10 e Receita de set/2026), `[WEB]` fonte pública datada na seção 6, `[HIPÓTESE]` proposta minha sem dono, `[VALIDAR JURÍDICO]`, `[VALIDAR JOÃO]`.

## 0. Antes de ler: o que os dados da Save conseguem e não conseguem dizer
| Ponto | Consequência |
|---|---|
| A base de ICP (`icp-2026-10-19.json`, 3.709 negócios fechados desde 19/10/2024) mede **só recuperação tributária**. Não há conversão, ticket nem honorário de Gestão de Contas, FIDC, crédito internacional, Maquila etc. | ICP dos produtos financeiros e jurídicos abaixo vem de **regra documentada** (ecossistema v1.0, fichas, elegibilidade do Internacional), não de conversão medida. É hipótese até haver 90 dias de funil por produto. |
| Café está **fora da meta** de recuperação desde abr/2026 (regra do Luis), mas tem o maior honorário esperado por caso da base (R$ 396 mil, 41% de conversão, 657 fechados) e é o núcleo dos casos de FIDC e funding. | Decisão pedida na seção 7 (P1): a regra vale só para recuperação ou para todo o portfólio? |
| O CNAE só é preenchido após o ganho em muitos negócios; a Receita corrigiu 1.819 deles. Faturamento da Receita dá só **piso** (porte "Demais" = acima de R$ 4,8 mi/ano). Regime só vem do parceiro ou da consulta a prospects. | O score usa faturamento **estimado** e marca a origem. |
| UF: o ranking por honorário esperado (ES R$ 547 mil; BA R$ 270 mil; PR R$ 186 mil; SP R$ 183 mil; DF R$ 174 mil; MG R$ 86 mil, com 2.370 fechados) está contaminado pelo café (ES é o território de JGM em café). | UF entra com peso baixo e sempre cruzado com segmento e Master (seção 2.3). |
| Amostra mínima: 15 fechados. Bebidas (30), Grãos e Cereais (32), Pescados (8) são pequenas. | Não promover Bebidas a "segmento nº 1" só pelo lead scoring v1 (30 pontos). |
| Sem dados de parceiro novo (M&A, corporate): nada medido. | Perfil de parceiro ideal é hipótese. |

**Base de referência `[BASE]` (recuperação, 19/10/2026):** média da base sem café: conversão 32,4%, honorário esperado R$ 72.854 por caso. Por regime: Lucro Real 34,5% e R$ 142.584; Presumido 38,5% e R$ 36.303; Simples 18,2% e R$ 10.242. Por segmento (honorário esperado): Bebidas R$ 723 mil (23%, amostra pequena em valor); Grãos e Cereais R$ 166 mil (25%); Carnes e Frigoríficos R$ 109 mil (54%, 663 fechados); Outros R$ 70 mil; Hortifrúti R$ 70 mil (47%); Supermercados R$ 36 mil (30%); Padarias R$ 17 mil; Combustíveis R$ 15 mil (10%); Transporte R$ 7 mil; Laticínios e Ovos R$ 4,7 mil (18,5%, 54 fechados). Território dos Masters (valor ganho em 12 meses): D&S em Carnes MG e SP e Hortifrúti MG; AGILE em Carnes SP; G.S.H, Orteconte e Costa e Gaudêncio em Café MG; JGM em Café ES; Assecont em Supermercados SC; Gerson em RS.

---

## 1. ICP por produto

Convenções: **Porte** em faturamento anual, com o piso econômico de R$ 4,8 mi/ano como corte prático de recuperação `[HIPÓTESE]` (abaixo disso o honorário raramente paga a análise). **UF:** só onde há base (recuperação); nos demais, "sem base" e a UF vem do Master e do Estado do incentivo. "Contraindicação" é o que tira a empresa da conversa agora.

### 1.1 Teses e serviços de base (T01 a T19, P01, P02), agrupadas por perfil idêntico
| Teses | Porte | Regime | Setor | UF | Sinais de compra | Contraindicações |
|---|---|---|---|---|---|---|
| **T01** alíquota zero na revenda (via PER) | Acima de R$ 4,8 mi/ano | Real (não cumulativo) | Atacado, distribuição, frigorífico, hortifrúti, grãos. Carnes: 54% de conversão `[BASE]` | SP e MG têm Master e histórico; ES, DF, PR, BA com honorário alto e amostra a ler com café fora | Compras de produto de alíquota zero para revenda; margem curta; saldo na EFD-Contribuições | Mercado e supermercado, cafeeira e atividade incompatível (catálogo). Nunca DCOMP; risco da posição contrária da Receita registrado |
| **T02, T08, T11** insumos, conta gráfica de PIS/COFINS, conta gráfica de IPI | Média e grande | Real | Indústria, exportador, logística, agroindústria | Sem base por tese | Saldo credor recorrente; saídas sem débito (exportação, suspensão, isenção); preservar saldo antes da CBS (urgência 2027) | Presumido ou Simples; saldo imaterial. Café: alta aderência em T02/T08 (exportador), mas fora da meta de recuperação |
| **T03, T04, T09** ICMS e ICMS-ST fora da base; gross up | Faturamento mensal acima de R$ 300 mil | Real ou Presumido | Revenda com ICMS-ST: alimentos, bebidas, combustíveis, farmacêuticos. Combustíveis têm 10% de conversão `[BASE]` | Sem base | Muita nota com ICMS; ST destacado | T09: divergência de mercado, informar cenário. Estados com diferimento ou isenção (café, grãos) exigem validar antes |
| **T05, T07, T16** PIS/COFINS fora da própria base; ISS fora da base; PIS/COFINS fora do IRPJ/CSLL (Presumido) | T07: mensal acima de R$ 150 mil | Presumido ou Real (T16 só Presumido) | Serviços (T07); qualquer recolhimento regular | Sem base | Recolhimento mensal relevante e histórico de 5 anos | Via judicial: custas e prazo longo; cliente sem apetite a ação. Presumido: honorário esperado baixo (R$ 36 mil), priorizar só com recolhimento alto |
| **T06** ICMS na base do crédito de entrada | Alto volume de compras | Real | Indústria, varejo, agroindústria, distribuição | Sem base | Compras tributadas por ICMS em volume | Não confundir com T03 (saída). Só judicial |
| **T10** crédito presumido de IPI (compras de atacadista) | Média e grande | Real | Indústria que compra de atacadista não contribuinte | Sem base | Insumos comprados de atacadistas | Quem não é indústria ou equiparado |
| **T12, T13** CPP, verbas indenizatórias; Sistema S | Folha representativa | Real ou Presumido | Indústria, comércio e serviços | Sem base | Folha grande e várias rubricas; T13 só com decisão favorável anterior a 15/12/2020 | T13 fora da modulação: não segue |
| **T14, T15** crédito presumido de ICMS fora do IRPJ/CSLL e do PIS/COFINS | Qualquer com incentivo | Qualquer | Beneficiária de crédito presumido estadual | Estados com regime (ex.: torrefação em MG, a validar) | Documento do incentivo disponível | Sem documento do incentivo |
| **T17** ACT/CCT | Faturamento e folha relevantes | Real | Setores com convenção que impõe despesas (alimentação, EPI, uniformes) | Sem base | ACT/CCT vigente com despesa recorrente | Sem ACT/CCT |
| **T18, T19** crédito presumido de compras de PF; Funrural | Agroindústria e cooperativa com compra de produtor PF; produtor e adquirente de produção rural | T18 Real; T19 PF, PJ e cooperativa | Agroindústria, cooperativa, frigorífico, laticínio, congelados de origem agrícola | Sem base | Compras de PF ou cooperado e saldo acumulado; NCM do art. 8º; DCTFWeb e eSocial | T19: preço e consulta e-CAC/PGFN ainda pendentes do Luis (hoje sem preço); T18 só com NCM do art. 8º |
| **P01** planejamento tributário e reforma | Acima de R$ 1 mi/ano | Real, Presumido ou Simples | Todos; urgência em quem tem saldo credor e mix por NCM (varejo alimentar, café com alíquota zero em 2027) | Sem base | CBS plena em 2027; saldo de PIS/COFINS a escriturar; mudança de regime | Empresa sem contador que entregue dados |
| **P02** planejamento estratégico | Empresa em expansão, reestruturação ou profissionalização | Qualquer | Qualquer | Sem base | Meta de crescimento, novo sócio, diretoria sem indicadores | Sem decisor presente |
| **P2** recorrência (novas competências) | Cliente já recuperado | Qualquer | Qualquer | — | 12 meses depois do primeiro ciclo; tese nova; decadência de 5 anos correndo | Cliente com FIDC na Save tende a não cotar fora (não usar como promessa) |

### 1.2 Fichas 1 a 23 (`fichas-sem-reuniao.md`) e produtos do João Mattos e de Paulo
| # | Produto | Estado | Porte | Regime e setor | Sinais de compra | Contraindicações |
|---|---|---|---|---|---|---|
| 1 | **Gestão de Contas** (cobrança por IA, escrow) | Pronto, Save Invest | Média: de R$ 4,8 mi/ano até cerca de R$ 10 mi/mês | Qualquer; vende a prazo a empresas (B2B): atacado, indústria, agro | Contas a receber acima do faturamento mensal; vencidos altos; mês de aperto de caixa | Venda só a consumidor final; carteira sem documento. Escrow nunca como forma de escapar de bloqueio judicial. Quem contrata e quem presta: em aberto |
| 2 | **Antecipação de recebíveis** | Pronto, Save Invest (instituição autorizada) | R$ 4,8 mi/ano em diante | Qualquer com título | Antecipação cara no banco; sazonalidade; recebível de safra | Venda gerencial sem nota; sem lastro documental |
| 3 | **Monetização de ICMS acumulado** | Candidato `[HIPÓTESE]` | Média e grande | Real; indústria e exportadora | Saldo credor recorrente; CIAP | Regra estadual desfavorável; deságio fora do alvo |
| 4 | **Precatórios** | Candidato `[HIPÓTESE]` | Grande | Real | Débito alto com ente federativo | **Não oferecer em 2027**: risco de nulidade e de parecer de planejamento abusivo; sem dono |
| 5 | **Seguro garantia** (depósito judicial, dívida fiscal) | Candidato | Média e grande | Qualquer com litígio | Depósitos judiciais altos; execução fiscal | Sem parceiro habilitado; Save não é corretora `[VALIDAR JURÍDICO]` |
| 6 | **Gestão de Passivo e transação tributária** | Pronto | Média e grande | Qualquer | Débito sem certidão; dívida ativa; autuação; CND vencida | Prometer desconto. Passivo vem **antes** do crédito novo |
| 7 | **Passivo bancário, alongamento, reestruturação** | Sem ficha e sem dono | Média e grande | Qualquer | Despesa financeira alta com resultado baixo; dívida de curto prazo de 3 a 4 faturamentos; covenant quebrado | Não sugerir "pré-quebra"; recuperação extrajudicial tem efeito de mercado |
| 8 | **Produtos jurídicos** | Pronto | Qualquer | Qualquer | Glosa, despacho decisório, autuação, contencioso | Regras da OAB sobre captação e honorário (repasse ao contador só como indicação comercial) `[VALIDAR JURÍDICO]` |
| 9 | **Estruturação patrimonial e empresarial** | Pronto | A partir de R$ 50 mi/ano ou patrimônio relevante | Família com terra, imóveis, armazém, empresas em nome de PF | Sucessão; garantia para funding; expansão com ativos; mudança do ITCMD | Dizer "holding", "blindagem" ou uso contra credor |
| 10 | **Preparação para a reforma** | Pronto (P01) | Real e Presumido relevantes | Todos; mais urgente com saldo credor e exportação | CBS e IBS a partir de 2027; saldo de PIS/COFINS a escriturar; split payment (opcional em 2027, a confirmar nos atos da RFB) | Cliente sem escrituração fiscal organizada |
| 11 | **CFO terceirizado e controladoria** | Candidato, sem dono | R$ 30 mi/ano em diante `[HIPÓTESE]` | Qualquer | Banco ou investidor pediu relatório que a empresa não entregou; DRE inexistente | Sem sponsor no dono. Próprio × parceiro em aberto |
| 12 | **Sucessão e governança familiar** | Candidato (jurídico) | Média e grande familiar | Qualquer | Fundador acima de 60; sucessor definido ou em disputa | Sem abertura da família; parceiro especializado a definir |
| 13 | **Compliance, integridade, LGPD** | Candidato | Média e grande | Quem contrata com governo, investidor ou fundo | Exigência de investidor, de fundo ou de contratante; incidente | Venda isolada sem gatilho |
| 14 | **Passivo trabalhista e folha** | Candidato, via parceiro | Folha grande | Indústria, comércio, serviços | Rubricas atípicas; terceirização; eSocial | Save só estrutura, contencioso é de advogado trabalhista |
| 15 | **Seguros e hedge** | Candidato, via corretora parceira | Média e grande | Exportador, dívida em moeda forte, agro, carteira concentrada | Dívida ou receita em moeda forte; safra | Opinar sobre o câmbio; Save não é corretora |
| 16 | **FIDC, multicedente e multissacado** | Pronto, Save Invest | **A partir de R$ 10 mi/mês** (custo de implantação alto) | Cadeia grande: supermercado, café, agro, congelados | Antecipação cara; cadeia de fornecedores ou clientes; carteira organizada | Título sem nota (a formalização vem antes); cotas são valor mobiliário (Save não distribui) |
| 17 | **CPR e CRA** | Candidato | Agroindústria e trading | Agro, café | Financia safra ou produtor | Sem dono e sem parceiro; contrato futuro como garantia está em aberto |
| 18 | **Sale-leaseback** | Candidato | Imóvel próprio quitado | Qualquer | Imóvel quitado e caixa apertado | Perde o ativo como lastro do crédito internacional |
| 19 | **Preparação para investidor (N1)** | Candidato, pré-requisito de captação e crédito internacional | Qualquer, inclusive abaixo de R$ 10 mi/ano | Indústria em crescimento | Demanda acima da capacidade com EBITDA negativo por investimento; sócio ou fundo na mesa | Sem decisor; sem contabilidade confiável |
| 20 | **M&A** | Candidato, via parceiro de perfil alto | Média e grande | Qualquer | Sucessão sem sucessor; sócio que quer sair; aquisição; sócio estratégico | Valor mobiliário (CVM); conflito se a Save também financia |
| 21 | **Financiamento à exportação** | Candidato | Exportador | Café, carnes, agro | ACC e ACE; contrato de exportação novo | Sem parceiro bancário |
| 22 | **Subvenções e Lei do Bem** | Candidato | Real, com P&D e lucro (Lei do Bem) | Indústria, agroindústria | Gasto em P&D; edital aberto | Sem lucro tributável (Lei do Bem); sem regularidade fiscal |
| 23 | **Energia e créditos de carbono** | Candidato | Agro e indústria | — | Conta de energia alta | **Não oferecer em 2027**: retorno estimado não vai a cliente |
| P12 | **Crédito Internacional** (nunca "fundo") | Validação, trava G2 (15/12/2026) | Faturamento comprovável acima de cerca de R$ 50 mi; necessidade acima de US$ 5 mi (R$ 26 mi); garantia livre cerca de 2x `[v2.3]`; 1,5x e R$ 30 mi ficam "Em desenvolvimento" `[VALIDAR JOÃO]` | Real; empresa com 2024 e 2025 completos; café, agro com terra, construtora com VGV | Ativos acima de R$ 60 mi; troca de dívida; expansão com projeto | Eliminatórios K1 a K10: necessidade abaixo de US$ 5 mi, garantia abaixo de 1,5x, RJ, Simples, dinheiro em menos de 3 meses, sem finalidade, recusa de KYC |
| P15 | **Maquila e Paraguai** (estudo de viabilidade) | Validação; D59 bloqueia frigorífico | Real, indústria intensiva em mão de obra, energia e capital | Têxtil, confecção, alimentos processados. Ciclo de cerca de 24 meses até o faturamento em produto de cura longa | Demanda acima da capacidade; custo de energia e folha pesado | Frigorífico (D59); Presumido ou Simples; faturamento pequeno demais para a planta; sem fábrica local para submaquila |
| P16 | **Captação de capital** (sócio, equity) | Validação | Qualquer com projeto | Indústria em crescimento | Meta de crescimento forte; sócio ou fundo na mesa | Valor mobiliário: Jurídico antes de qualquer conversa; sem plano de negócio |
| P17 | **Internacionalização turnkey** | Validação | Média e grande | Exportador ou indústria com mercado latino | Mercado interno saturado; reforma torna exportação mais vantajosa `[a validar]` | Sem capacidade e caixa no Brasil primeiro (ordem das reuniões) |
| P18 | **Tax internacional e comércio exterior** | Pronto (Paulo e João Mattos) | Grande | Operação entre países | Operação com Paraguai ou outro país; preço de transferência; DCBE | Sigilo de capitais; não bitributação só com especialista |
| N3 | **Governança de operação no exterior** | Candidato (só após P15) | Quem já opera fora | — | Planta ou escritório no exterior | Sem operação instalada |
| P14 | Home equity | Fora do escopo desta rodada (decisão do Luis, 22/10) | — | — | — | — |

---

## 2. Sinais → produto → pergunta de abordagem, e score proposto

### 2.1 Mapa (alinhado à seção 5 do ecossistema v1.0 e às 8 perguntas de `conexao-base-parceiros.md`)
Regra de fala: **problema e resultado, nunca nome de produto**, uma pergunta aberta por vez, sem número nem taxa (`roteiro-conversa-empresario.md`). As perguntas abaixo são do **parceiro indicador** na primeira conversa.

| Sinal (onde se vê) | Produto principal | Segundo da fila | Pergunta de abordagem |
|---|---|---|---|
| Contas a receber acima do faturamento mensal; vencidos altos (carteira, e-CAC) | Gestão de Contas | Antecipação, depois FIDC | "Em que mês do ano o seu caixa mais aperta e o que acontece com os clientes que atrasam?" |
| Despesa financeira alta com resultado baixo (DRE, SCR) | Passivo bancário (descoberta) | Crédito internacional, se houver ativo | "Com quantos bancos você trabalha e quanto sai de parcela por mês?" |
| Dívida de curto prazo de 3 a 4 faturamentos | Passivo bancário, depois Gestão de Passivo | — | "Se um banco reduzisse o limite amanhã, o que você faria?" |
| Débito fiscal ou sem certidão | Gestão de Passivo | Produtos jurídicos | "Hoje você consegue emitir certidão negativa quando precisa?" |
| Saldo credor; compras com alíquota zero; alimentos no Real (EFD) | Recuperação (T01, T02, T08) | Recorrência, reforma | "Já passou por uma revisão de crédito de PIS e COFINS dos últimos cinco anos? Quem fez?" |
| Antecipa recebível com banco | Antecipação | FIDC (acima de R$ 10 mi/mês) | "Você antecipa recebível hoje? A que custo, e quanto da carteira?" |
| Cadeia grande de fornecedores ou clientes (supermercado, café, congelados) | FIDC multicedente | Gestão de Contas antes, para organizar a carteira | "Como funciona a relação com os produtores ou fornecedores e quem financia a safra?" |
| Ativos acima de cerca de R$ 60 mi (fazenda, silo, galpão, lojas quitadas) | Estruturação patrimonial | Crédito internacional (descoberta) | "Há imóvel, terra ou ativo livre que hoje não trabalha para a empresa?" |
| Crescimento acima da capacidade; EBITDA negativo por investimento | Preparação para investidor (N1) | Captação de capital, crédito internacional se o ticket couber | "Existe demanda que você não atende? O que impede de crescer hoje?" |
| Indústria de mão de obra e energia no Real | Recuperação (folha: T12) | Maquila (descoberta) | "Já pensou em produzir parte da operação fora do Brasil? Por quê?" |
| Fundador acima de 60; sócio quer sair; família numerosa | Sucessão e estruturação | M&A (via parceiro) | "Como será a sucessão? Já houve conversa formal na família?" |
| Dívida ou receita em moeda forte; exportação | Seguros e hedge (via corretora) | Financiamento à exportação | "Há dívida ou receita em dólar ou euro? Como lida com a variação?" |
| Ano de 2027 na porta: saldo de PIS/COFINS parado, contratos longos | Reforma e planejamento | T08 e T11 (preservar saldo) | "O que você sabe sobre como o crédito acumulado será tratado a partir de 2027?" |
| Exigência de banco ou investidor por relatório | CFO terceirizado, N1 | Compliance | "O banco ou um investidor já pediu algo que foi difícil entregar?" |
| Fluxo do e-CAC com taxa bancária e maquininha altas | Alerta preliminar de Gestão de Contas | Aprofundar com DRE | (dado, não pergunta; nunca substitui análise) |
| Pergunta fixa de fechamento | — | — | "Se resolvêssemos uma coisa nos próximos 90 dias, qual seria?" |

### 2.2 Eliminatórios (nunca entram na lista de abordagem do produto)
CNPJ não ativo ou fora da matriz · cliente com negócio fechado, em negociação ou de outro parceiro (conflito de canal: decisão do Luis, pela raiz do CNPJ no HubSpot, somente leitura) · RJ, RE ou falência para crédito internacional (K7) · Simples ou MEI para crédito internacional e Maquila · frigorífico para Maquila (D59) · necessidade abaixo de US$ 5 mi para crédito internacional (K1) · sem nota fiscal para antecipação e FIDC · débito sem certidão para qualquer crédito novo (primeiro passivo).

### 2.3 Score proposto de conta (0 a 100) `[HIPÓTESE]`, para o Luis validar e a Jenifer usar depois
O lead scoring v1 de 19/10 (Regime 17, Segmento até 30, UF até 30 pontos) foi calibrado só em honorário de recuperação e tem pesos de UF e Bebidas que a amostra não sustenta. Proponho um score que leia **todo o portfólio** e mantenha o v1 como uma das dimensões.

| Dimensão | Pontos | Regra |
|---|---|---|
| Porte (faturamento estimado, com origem marcada) | até 20 | Abaixo de R$ 4,8 mi: 0 · até R$ 30 mi: 8 · até R$ 120 mi: 14 · acima (R$ 10 mi/mês): 20 |
| Regime | até 15 | Real 15 · Presumido 6 · Simples 2 (proporção do honorário esperado: R$ 143 mil, R$ 36 mil, R$ 10 mil) · sem dado: 5 e marcado |
| Setor de aderência | até 15 | Tier 1 (carnes, hortifrúti, indústria de alimentos, grãos e cereais): 15 · Tier 2 (varejo alimentar, café e cadeia, laticínio e cooperativa): 10 · Tier 3: 5. Bebidas entra em Tier 1 só com 15 fechados de amostra confirmada |
| Território | até 10 | Master já ganha no mesmo segmento e UF: 10 · UF de honorário alto sem Master: 5 · sem história: 0 (e entra na lista de recrutamento de parceiro) |
| Sinais de dor financeira (seção 2.1) | até 20 | 5 por sinal confirmado (receber alto, despesa financeira alta, dívida de 3 a 4 faturamentos, débito sem certidão, antecipação cara, mês de aperto), máximo 20 |
| Gatilho de calendário ou evento | até 10 | Reforma 2027 com saldo credor, colheita, sucessão, contrato de exportação novo, expansão, EUDR em 30/12/2026 (café, soja e gado): 5 por gatilho, máximo 10 |
| Prontidão | até 10 | Decisor acessível via indicador 4 · dado disponível (e-CAC, SPED, DRE) 4 · sem restrição de certidão 2 |

**Faixas:** A (70 a 100): o condutor chama em 5 dias úteis, com o produto de entrada da seção 2.1. B (45 a 69): o indicador faz a pergunta de abertura e devolve as respostas; revisa em 30 dias. C (abaixo de 45): carteira, só em campanha. **Revisão trimestral** com a conversão real por produto; hoje esse campo não existe no HubSpot (precisa de campo "produto de entrada", pedido ao `depto-dados`).

---

## 3. Priorização 2027

### 3.1 Critério
Índice = **Valor** (0 a 5: honorário ou recorrência esperados e tamanho da base) + **Facilidade** (0 a 5: dono, preço, processo e agente prontos) + **Alavanca** (0 a 2: abre outros produtos) − **Dependências** (0 a 2 cada: **D** dado do cliente, **V** validação de Jurídico, Tributário ou João Mattos, **P** parceiro externo). Notas `[HIPÓTESE]` do Gerente, a calibrar com o Luis e com os donos.

| Produto | Valor | Facilidade | Alavanca | D | V | P | Índice |
|---|---|---|---|---|---|---|---|
| Recuperação T01 a T19 | 5 | 5 | 2 | 1 | 0 | 0 | **11** |
| Recorrência | 4 | 5 | 1 | 1 | 0 | 0 | **9** |
| Planejamento tributário P01 | 4 | 4 | 2 | 1 | 0 | 0 | **9** |
| Reforma (ficha 10) | 4 | 4 | 2 | 1 | 1 | 0 | **8** |
| Gestão de Contas | 4 | 4 | 2 | 2 | 1 | 0 | **7** |
| Gestão de Passivo | 3 | 4 | 2 | 2 | 1 | 0 | **6** |
| Estruturação patrimonial | 4 | 3 | 2 | 2 | 1 | 0 | **6** |
| Produtos jurídicos | 3 | 4 | 0 | 1 | 1 | 0 | **5** |
| Sucessão e governança | 3 | 3 | 2 | 1 | 1 | 1 | **5** |
| Planejamento estratégico P02 | 2 | 3 | 1 | 1 | 0 | 0 | **5** |
| Antecipação | 4 | 3 | 1 | 2 | 1 | 1 | **4** |
| FIDC | 5 | 2 | 1 | 2 | 1 | 1 | **4** |
| CFO terceirizado | 4 | 2 | 2 | 2 | 1 | 1 | **4** |
| Preparação para investidor (N1) | 4 | 2 | 2 | 2 | 1 | 1 | **4** |
| Tax internacional (P18) | 3 | 3 | 1 | 2 | 1 | 0 | **4** |
| Funrural (T19) | 3 | 3 | 1 | 1 | 1 | 0 | **4** |
| Subvenções e Lei do Bem | 3 | 3 | 1 | 2 | 1 | 1 | **3** |
| Passivo bancário | 4 | 2 | 1 | 2 | 2 | 1 | **2** |
| Crédito internacional | 5 | 1 | 1 | 2 | 2 | 1 | **2** |
| Compliance e LGPD | 2 | 3 | 0 | 1 | 1 | 1 | **2** |
| Seguro garantia | 3 | 2 | 1 | 1 | 1 | 2 | **2** |
| CPR e CRA | 4 | 2 | 1 | 2 | 1 | 2 | **2** |
| M&A | 4 | 2 | 1 | 1 | 2 | 2 | **2** |
| Financiamento à exportação | 3 | 2 | 1 | 1 | 1 | 2 | **2** |
| Captação de capital | 4 | 1 | 1 | 2 | 2 | 1 | **1** |
| Maquila | 4 | 1 | 1 | 2 | 2 | 1 | **1** |
| Trabalhista | 2 | 3 | 0 | 1 | 1 | 2 | **1** |
| Seguros e hedge | 3 | 2 | 1 | 1 | 2 | 2 | **1** |
| Monetização de ICMS | 4 | 2 | 1 | 2 | 2 | 2 | **1** |
| Internacionalização turnkey | 3 | 1 | 0 | 2 | 2 | 1 | **−1** |
| Governança no exterior (N3) | 2 | 1 | 0 | 1 | 2 | 1 | **−1** |
| Sale-leaseback | 2 | 2 | 0 | 1 | 2 | 2 | **−1** |
| Precatórios | 2 | 1 | 0 | 1 | 2 | 2 | **−2** |
| Energia e carbono | 2 | 1 | 0 | 1 | 2 | 2 | **−2** |

**Leitura:** o índice mede **prontidão para ir ao parceiro**, não importância estratégica. FIDC e crédito internacional têm valor 5 e índice baixo por dependências: a ordem de lançamento os coloca depois, mas o trabalho de preparação começa antes. Gestão de Contas sobe porque abre dado (e-CAC), e a esteira de passivo antes do crédito condiciona o resto.

### 3.2 Ordem de lançamento ao parceiro, em ondas trimestrais de 2027 `[HIPÓTESE]`
Regra transversal: no máximo **2 produtos novos por vez por cliente**; passivo antes do crédito novo; produto em validação só como **descoberta**, sem taxa, prazo ou fee, e só depois do G2.

| Onda | Janela | Entra | Por quê | Condição para abrir |
|---|---|---|---|---|
| **0 · preparo** | 02/11 a 31/12/2026 | Enablement do que já está pronto; kit do parceiro; filtro de qualificação; campo "produto de entrada" no HubSpot; piloto de perguntas da seção 2.1 com 2 Masters | Nada vai a cliente novo antes de o filtro e o enablement existirem | Luis aprova seções 2 e 4; Qualidade audita o texto; respostas escritas do João até 31/10; G2 e G3 em 15/12/2026 |
| **1 · Q1/2027** | jan a mar | Recuperação (T01 a T19) e recorrência; reforma e planejamento (P01); Gestão de Contas como porta média; Gestão de Passivo | Produtos prontos, com dono e agente; CBS entra em 2027 e as competências mais antigas continuam vencendo (decadência de 5 anos) | Quem contrata a Gestão de Contas e a habilitação definidos; preço do Funrural |
| **2 · Q2/2027** | abr a jun | Estruturação patrimonial e sucessão (venda conjunta, uma conversa); produtos jurídicos; antecipação e FIDC (via Save Invest) para a porta grande; tax internacional; Lei do Bem (janela de prazo anual: em 2026 foi até 31/08, conferir a de 2027) | Porta grande exige confiança e dado das ondas anteriores; FIDC só aceita título com nota | Piso de faturamento do FIDC validado; regra de remuneração de parceiro em produto maduro; parecer sobre CVM e OAB |
| **3 · Q3/2027** | jul a set | Preparação para investidor (N1) e CFO terceirizado, com decisão próprio × parceiro tomada; crédito internacional e captação **como descoberta**, se o G2 abriu e os 10 primeiros casos foram qualificados; estudo de viabilidade do Paraguai | N1 é pré-requisito de capital; só chega ao parceiro depois de caso piloto | G2 aprovado; critério v2.3 × 13/10 conciliado; MQ-Q1 e MQ-Q6 respondidos; D59 mantido para frigorífico |
| **4 · Q4/2027** | out a dez | Maquila e internacionalização turnkey (só descoberta); financiamento à exportação; CPR e CRA, seguros e hedge via parceiro habilitado; M&A com os parceiros recrutados | Dependem de parceiro externo e de rede no exterior ainda a confirmar | Parceiros contratados; Jurídico valida CVM e BCB |
| **Fora de 2027 sem decisão nova** | — | Precatórios, sale-leaseback, energia e carbono, monetização de ICMS | Risco reputacional ou sem dono e sem parceiro | Conselho decide |

---

## 4. Go-to-market por canal

### 4.1 Quem faz o quê `[HIPÓTESE]`, dentro das decisões D8 e D11 (indicação × condução adiada)
| Canal | Quem é | Papel | Produtos onde atua |
|---|---|---|---|
| **Parceiro indicador** | Escritório contábil ou consultor com carteira B2B (os parceiros atuais e os novos de CNAE 6920) | Faz a pergunta de abertura, envia CNPJ e as respostas das 8 perguntas; acompanha o cliente; **não** faz proposta, não fala de taxa, não conduz capital | Porta de entrada: recuperação, reforma, Gestão de Contas, Gestão de Passivo; indica o restante |
| **Masters** (D&S, AGILE, G.S.H, Cardoso, JGM, Costa e Gaudêncio, Assecont, Orteconte, Gerson) | Nove parceiros com Célula e BDR | Conduzem as conversas dos produtos **prontos** (onda 1) no território onde já ganham; indicam à Save o que é estruturado | Recuperação, recorrência, reforma, Gestão de Contas; tese T18/T19 onde há agroindústria |
| **Condutor** | Luis, sócios, gestor de esteira (PO) e times internos | Conduz tudo que exige análise de capital, garantia, estrutura societária ou valor mobiliário; escuta com o empresário; aciona João Mattos, Jurídico e Tributário | FIDC, antecipação (via Save Invest), estruturação patrimonial, crédito internacional, captação, Maquila, N1, CFO |
| **Parceiro de perfil mais alto** (a recrutar) | Assessor de M&A, ex-gerente corporate de banco, boutique de reestruturação | Abre empresas de R$ 30 mi/ano em diante e a porta grande, que o contador não alcança | M&A, captação, FIDC, crédito internacional, passivo bancário, sucessão |

**Divisão por faixa de porte:** média (até cerca de R$ 10 mi/mês): indicador e Master abrem, Gestão de Contas e diagnóstico tributário são a primeira conversa. Grande (acima de R$ 10 mi/mês ou garantias acima de R$ 60 mi): condutor abre, em geral com o parceiro de perfil alto; o parceiro atual **mantém a relação** e a recorrência.

### 4.2 Perfil de parceiro ideal `[HIPÓTESE]`
| Tipo | Perfil | Sinais de qualidade | Onde achar | Cuidado |
|---|---|---|---|---|
| **Contador (indicador)** | Escritório com carteira B2B no Real ou Presumido, setores Tier 1 e 2, onde ainda não há Master no segmento e UF (4.203 prospects em praças sem histórico, na lista de 29/09) | Cliente com faturamento de R$ 4,8 mi/ano em diante; entrega SPED em dia; confia em abrir o e-CAC; aceita que a Save conduza | Base da Receita (CNAE 6920) nas UFs-alvo; indicações dos Masters; praças com lacuna do mapa de território | Não vender como "complemento do contador": é **complementaridade** (o contador conhece o cliente, a Save traz profundidade técnica) `[WEB, contabeis]`. Honorário de advogado ao contador só como indicação comercial `[VALIDAR JURÍDICO]` |
| **Assessor de M&A** | Boutique ou sócio com 3 a 5 mandatos por ano em médias empresas; sucessão como gatilho | Mandatos recentes; relação com fundos; aceita que a Save estruture a parte tributária, patrimonial e de capital | Rede do Luis e dos sócios; eventos de M&A de médias; boutiques como a descrita na seção 6 | Valor mobiliário e confidencialidade; conflito se a Save também financia |
| **Ex-gerente corporate (banco)** | Quem carrega carteira de empresas de R$ 30 a 300 mi e conhece os cortes de crédito | Carteira real de relacionamento; conhece covenant e garantia | Rede do Luis; indicação dos Masters | Não pode prometer taxa nem aprovação; vedações de não concorrência do banco de origem |

**Meta de piloto** `[HIPÓTESE]`: 3 parceiros de perfil alto (1 de cada tipo) até o fim do Q2/2027, antes de falar em escala. Escala = qualidade, não volume (decisão da conversa de 20/10).

### 4.3 Filtro de qualificação das indicações (3 portas)
| Porta | Pergunta | Quem decide | Saída |
|---|---|---|---|
| **1. Cadastro e canal** | CNPJ ativo e matriz? Já cliente, em negociação ou de outro parceiro (raiz do CNPJ no HubSpot, só leitura)? Autorização do parceiro para falar da empresa (LGPD)? | Intel Comercial, com conflito decidido pelo Luis | Segue, devolve ao parceiro com motivo, ou vai a conflito de canal |
| **2. Aderência** | Qual o score (2.3) e o produto de entrada (2.1)? Algum eliminatório (2.2)? | Intel Comercial (agente, rascunho) e consultor | Faixa A, B ou C com o produto e a pergunta |
| **3. Prontidão** | O decisor aceita a conversa? Há dado (e-CAC, SPED, DRE, carteira) ou a promessa de entregar? Certidão ok? | Consultor ou condutor | Reunião; ou nutrição por 30 a 60 dias |

O que o indicador envia: CNPJ, nome do decisor (com a autorização), as respostas às 8 perguntas (vende a prazo a empresas · quanto está vencido · mês de aperto · bancos e parcela · antecipa e a que custo · débito ou certidão · imóvel ou terra quitados · exporta ou demanda acima da capacidade) e o que ele já sabe de regime e faturamento. A Save **não aborda a empresa por fora**. Métricas por parceiro: empresas na carteira, CNPJ válido, aderência média ou alta, conversas abertas, diagnósticos, primeiro ganho, produtos por cliente (alvo 2), tempo até o primeiro negócio.

### 4.4 Enablement: o que o parceiro precisa saber de cada produto e o que NÃO dizer
Base: `skills/depto-internacional/references/regras-e-proibidos.md`, `docs/ecossistema/racional-e-fechamento-ecossistema-save.md` seção 5 e fichas. Peça para fora só depois de Marketing, Qualidade (`auditar_texto.py`, zero alerta alto ou médio) e Jurídico.

| Produto | O parceiro precisa saber (1 frase) | NÃO dizer |
|---|---|---|
| Recuperação | A Save analisa se a empresa tem crédito de PIS, COFINS e outros tributos dos últimos 5 anos; pagamento só no êxito, depois de diagnóstico | Resultado assegurado, valor ou percentual de recuperação ao cliente sem o técnico; compensar alíquota zero por outro caminho que não o PER |
| Reforma | Preparar 2027: preservar saldos, rever preço e caixa | Data e alíquota como certezas (conferir nos atos da RFB); split payment obrigatório em janeiro de 2027 |
| Gestão de Contas | Organiza cobrança e recebimento, abre o caminho para os demais produtos; escrow é camada de proteção | "Blindagem", "escapar de bloqueio", "gratuito" sem condição por escrito |
| Antecipação | Quem antecipa é instituição autorizada; a Save indica | "A Save antecipa"; antecipação sobre venda sem nota |
| FIDC | Estrutura para financiar a cadeia; exige nota e volume; cotas têm regra própria | "A Save distribui cotas"; "desconta imposto" sem a tese validada; valores do custo |
| Gestão de Passivo | Regulariza débitos e a certidão **antes** de qualquer crédito novo | Prometer desconto ou perdão; "pré-quebra" |
| Estruturação patrimonial | Organiza imóveis e empresas para sucessão, garantia e planejamento | "Holding" como nome, "blindagem", uso contra credor |
| Sucessão e governança | Acordo de sócios, protocolo e conselho; começa por escuta | Opinar sobre a família ou o inventário |
| N1 e CFO | Plano, projeção e controle que um financiador exige | Apresentar como "garantia de aprovação"; como produto contratado antes de a decisão próprio × parceiro |
| Crédito internacional (descoberta) | A Save **estrutura o projeto** para análise de instituições nos EUA e na Suíça; operação de alguns meses | "Fundo", "dinheiro barato", taxa, carência, prazo, "aprovado", nome da instituição, "já fizemos várias" |
| Captação de capital (descoberta) | Alternativa de sócio ou investidor; Jurídico entra primeiro | Preço, retorno, diluição como se fosse certo; oferta pública |
| Maquila e Paraguai (descoberta) | O estudo mostra, com os números da empresa, se faz sentido; pode concluir que não | "1% de imposto", "economia de 28%", ausência de risco; frigorífico (D59); simulações de frigorífico do Mapa de Entregas |
| Tax internacional | Preço de transferência, não bitributação, DCBE: tratamento do especialista | "Paraguai não tem troca de informação", sigilo de capitais |
| Seguros, hedge, M&A, trabalhista (via parceiro) | A Save encaminha para parceiro habilitado | Recomendar apólice; opinar sobre câmbio; contencioso trabalhista |
| Todos | Cada produto é contratado em separado; estudo antes da proposta | Venda casada; nome de cliente; "estamos em todas as áreas" |

---

## 5. Segmentos prioritários e playbooks dos 4 casos

### 5.1 Segmentos prioritários `[BASE + HIPÓTESE]`
| Ordem | Segmento | Por quê (dado) | Produtos de entrada e segundo passo | Atenção |
|---|---|---|---|---|
| 1 | **Carnes, frigoríficos e atacado de carnes** | 54% de conversão, R$ 109 mil de honorário esperado, 663 fechados; prospects de Lucro Real em SP (501) e MG (257) na lista de 29/09 | T01 e T02 → reforma → antecipação | Maquila bloqueada (D59); Master já em SP (AGILE) e MG (D&S) |
| 2 | **Hortifrúti, congelados e indústria de alimentos** | 47% de conversão, R$ 70 mil; indústria de alimentos com base pequena (16 clientes) mas aderência a reforma, Gestão de Contas e antecipação | T01 e T18 se agroindústria → reforma → FIDC da cadeia | Base de indústria é pequena: validar com pilotos |
| 3 | **Café e cadeia (trading, exportador, torrefação)** | Maior honorário esperado da base (R$ 396 mil); território de 4 Masters; núcleo de FIDC e funding | T02/T08 em exportador; estruturação, FIDC, CPR; crédito internacional como descoberta | Fora da meta de recuperação; EUDR em 30/12/2026; T01 não serve a café |
| 4 | **Grãos e cereais** | R$ 166 mil, 25%, 32 fechados | T01 com ticket diferenciado; antecipação de safra | Amostra pequena |
| 5 | **Cooperativas e laticínios** | Laticínios têm 18,5% de conversão e R$ 4,7 mil de honorário esperado em recuperação `[BASE]`: **ruim para a tese geral**; cooperativa com compra de PF muda o quadro (T18, T19) | T19 e T18 na cooperativa; FIDC da cadeia | Tratar cooperativa à parte do laticínio privado; caso próprio em conversa separada |
| 6 | **Supermercados e varejo alimentar** | 30% e R$ 36 mil: baixo em recuperação; alto em reforma por NCM | Reforma → Gestão de Contas → Passivo | T01 não serve a mercado e supermercado |
| Baixa | Combustíveis (10%), transporte (R$ 7 mil), padarias (R$ 17 mil) | Honorário esperado baixo | Passivo e Gestão de Contas | Não priorizar para recuperação |

### 5.2 Playbook 1 · Indústria de alimentos em crescimento (cerca de R$ 8 mi/ano, demanda acima da capacidade, EBITDA negativo por investimento)
| Item | Conteúdo |
|---|---|
| Porta | **Em crescimento** (nem média nem grande) |
| Hipóteses de perfil | Necessidade de cerca de R$ 20 mi; garantia real já validada no caso de origem; meta de R$ 50 mi em 4 a 5 anos. **Regime e faturamento a confirmar**: com R$ 8 mi/ano, provável Presumido, o que reduz a recuperação e exclui Maquila |
| Sequência (máximo 2 por vez) | **N1** (plano, projeção, dossiê) → **captação de capital** (descoberta, depois do Jurídico) → crédito internacional **só se** o ticket e o faturamento passarem K1 e K8 (hoje não passam: US$ 2 mi e R$ 8 mi) → internacionalização na 2ª rodada; Maquila só como descoberta e provável "não agora" |
| Também considerar | Gestão de Contas e antecipação se vende a prazo; T01 se Real e compra com alíquota zero; Passivo, se houver certidão pendente, **antes** de qualquer capital |
| Perguntas de abertura | "Existe demanda que você não atende?" · "Quanto custa e quanto tempo leva ampliar a capacidade?" · "Quem já viu os seus números fora da empresa?" · "Qual sua meta de faturamento em 5 anos?" |
| Dados a pedir (depois do NDA) | DRE, balancete, custos, plano de expansão com custos, garantias, contabilidade confiável |
| Quem conduz | Condutor (Luis e João Mattos para capital) com o parceiro que indicou mantendo a relação |
| Travas | Sem taxa, prazo ou retorno; valor mobiliário (CVM); prejuízo inicial não elimina, mas exige payback e plano |
| Sucesso | Dossiê pronto em semanas; decisão informada "capital × diluição"; **não** convencer o cliente a tomar crédito |

### 5.3 Playbook 2 · Indústria de hortifrúti congelado (cerca de R$ 150 mi/ano, tributário já recuperado)
| Item | Conteúdo |
|---|---|
| Porta | **Grande** (R$ 12,5 mi/mês, acima de R$ 10 mi/mês), entra em **Proteger e controlar**, não em recuperação |
| Hipóteses (da conversa de 20/10, a confirmar) | Sucessão e governança; exposição a moeda forte (hedge); troca de dívida; cadeia de produtores sem mecanismo próprio de recebíveis; produção no Paraguai; conversa presencial na semana de 16/11 serve para **escutar**, não vender |
| Sequência | 1) Sucessão e estruturação patrimonial (+ recorrência anual de teses, T18 e T19 se compra de produtor PF) → 2) FIDC multicedente da cadeia, **depois de** a carteira e as notas estarem organizadas (Gestão de Contas) → 3) crédito internacional como troca de dívida, **se** o G2 abrir e passar K1 a K10 → 4) estudo do Paraguai como descoberta. Hedge via corretora parceira |
| Eliminatórios a checar | Débito e certidão; RJ no grupo; ciclo da planta de 24 meses; fábrica de congelados é intensiva em energia (aderente) mas é cadeia fria: custo real só no estudo |
| Perguntas de abertura | "Como funciona a relação com os produtores e quem financia a safra?" · "Há dívida ou receita em euro?" · "Como será a sucessão?" · "Quem acompanha os números e com que frequência?" |
| Quem conduz | Condutor (Luis, gestor de esteira, João Mattos na parte de capital); parceiro do primeiro movimento preserva a relação |
| Travas | Nada de número, taxa ou prazo na conversa; autorização escrita antes de usar como case anonimizado |
| Sucesso | Mapa da empresa em 48 h; um produto escolhido pelo dono para 90 dias |

### 5.4 Playbook 3 · Trading de café
| Item | Conteúdo |
|---|---|
| Porta | **Grande** |
| Hipóteses | Trade funciona como "banco" do produtor (financia insumo, trava compra futura); tem ou conhece fazendas com ativos acima de R$ 60 mi; exportador usa ACC |
| Sequência | 1) Gestão de Contas e organização da carteira (se o recebimento é desorganizado) → 2) **funding com lastro em fazenda** (crédito internacional, descoberta, depois do G2) com estruturação patrimonial para a garantia → 3) **FIDC multicedente e multissacado** financiando produtor e trade → 4) CPR e CRA, hedge e exportação como ondas 3 e 4 |
| Recuperação | T02 e T08 em exportador com saldo credor (conta gráfica e insumos); **T01 não serve a café**; dentro da regra de abr/2026, café sai do ranking de recuperação (decisão P1, seção 7) |
| Calendário | Colheita de mai a set (pico de caixa); EUDR em 30/12/2026 para grandes operadores; café com alíquota zero de IBS e CBS a partir de 2027 `[playbooks-setoriais, conferido em 16/10]` |
| Território | JGM (ES), G.S.H, Orteconte e Costa e Gaudêncio (MG) já ganham em café |
| Perguntas de abertura | "Como funciona a relação com o produtor e quem financia a safra?" · "Quanto fica em estoque e por quanto tempo?" · "Há dívida ou receita em dólar?" · "Há fazenda ou ativo livre?" |
| Travas | Taxa de 8% a 12% e carência de 3 anos da reunião de 24/09 **não** vão ao parceiro nem ao cliente; contrato futuro e CPR como garantia estão em aberto; Maquila não se aplica |
| Sucesso | Lista de exportadores e tradings com ativo acima de R$ 60 mi (compromisso do Luis de 13/10); um primeiro caso qualificado nos critérios K1 a K10 |

### 5.5 Playbook 4 · Cooperativa láctea e de suínos
Caso próprio, em conversa separada (jornada, seção 5): aqui só o que a Inteligência Comercial precisa para o ICP.
| Item | Conteúdo |
|---|---|
| Porta | Grande, pelo porte de cooperativa agroindustrial |
| Hipóteses de produto | T18 e T19 (cooperativa com compra de produtor PF e cooperado), T02 e T08, reforma (regime agro), FIDC da cadeia de cooperados, estruturação e sucessão de produtor |
| Alerta de ICP | O segmento **laticínios e ovos** tem 18,5% de conversão e R$ 4,7 mil de honorário esperado `[BASE]`: o ICP geral **não** serve de referência; a conta vale pelo ticket de T18 e T19, a medir em dados da própria cooperativa |
| Perguntas de abertura | "Como é composta a compra de leite e de suíno: de cooperados PF ou de terceiros?" · "Quem financia o cooperado e em que prazo?" · "Há crédito acumulado que não vira caixa?" |
| Travas | Detalhe, dado e peça ficam na conversa própria; nada de nome na pasta compartilhada |

---

## 6. Concorrência e benchmarks (consulta em 22/10/2026)
Fontes oficiais das firmas valem como o que a firma **diz** vender (autodeclarado). Onde só li o resumo da busca, está marcado "página não aberta". Benchmark anterior de 19/10 sobre implementação (McKinsey, BCG, Bain, Deloitte, PwC, EY, KPMG) está em `docs/ecossistema/benchmark-implementacao-consultorias.md` e não é repetido.

| Quem | Como entrega a médias e familiares (o que a fonte diz) | Data da fonte | Link | Leitura para a Save |
|---|---|---|---|---|
| **Deloitte Private** | Soluções sob medida para empresas familiares e de médio porte: governança, sucessão, estrutura de conselho, riscos, ERP, incentivos fiscais, M&A, IPO, recuperação e reorganização. Entrada por contato ou pedido de orçamento (RFP); relacionamento não detalhado | s/d; lida em 22/10/2026 | [Deloitte Brasil](https://www.deloitte.com/br/pt/services/deloitte-private/services/empresas-familiares-capital-fechado.html) | Menu largo, venda por proposta. A Save entra por diagnóstico e êxito, sem RFP |
| **KPMG Private Enterprise** | Família, patrimônio e empresa como um conjunto; times integrados; centro de especialistas (FABEX); organiza por ciclo: governança, crescimento, eficiência, legado; inclui family office, planejamento tributário internacional e fundos exclusivos | s/d; lida em 22/10/2026 | [KPMG Brasil](https://kpmg.com/br/pt/services/private-enterprise/family-business.html) | Melhor referência de **portfólio integrado** (ciclo de vida). A esteira dos 12 passos e o gestor de esteira cumprem o papel, com execução e êxito |
| **KPMG Global Family Business Report 2026** | 122 líderes brasileiros ouvidos; 80% implementando IA; 45% sem governança de IA | ago/2026; resumo de busca, página não aberta | [KPMG](https://kpmg.com/br/pt/insights/2026/08/kpmg-global-family-business-report-2026.html) | Argumento de abertura (governança), não dado próprio da Save |
| **PwC Brasil** | Governança empresarial e familiar em três eixos: família (conselho), negócio (controles e compliance), propriedade (acordo de sócios, estrutura, sucessão, family office) | s/d; resumo de busca, página não aberta | [PwC](https://www.pwc.com.br/pt/setores-atividade/empresas-familiares/governanca-empresarial-e-familiar.html) | Sucessão e governança são oferta clara das Big Four; a Save deve entrar por **crédito e caixa** e levar governança junto |
| **EY Brasil** | Família no middle market vê M&A como evento estrutural, mas raramente está preparada; gestão concentrada no dono; sócios têm dificuldade para entender o valor da empresa | abr/2025; resumo de busca, página não aberta | [EY](https://www.ey.com/pt_br/newsroom/2025/04/empresas-familiares-desafios-governanca-alinhamento-socios) | Sucessão como gatilho de M&A; sustenta a hipótese do parceiro de M&A |
| **Boutiques de M&A** (ex.: uma com mais de 50 transações, majoritariamente com exterior, que prepara esteira de dívida e IPO em 2026) | Mandato sucesso ou transação; médias empresas pouco atendidas pelos grandes bancos | jan/2026; resumo de busca | [Capital Aberto](https://capitalaberto.com.br/alem-do-capital/guilherme-steagall-socio-fundador-da-44-capital-no-alem-do-capital/) | Perfil de **parceiro** (não só concorrente) para a onda 4 |
| **Boutiques de reestruturação e dívida** | Estruturação de FIDC, CRI, CRA, debêntures e reestruturação: 65% das operações de uma casa nos últimos dois anos (autodeclarado) | s/d; resumo de busca | [Brazil Journal](https://braziljournal.com/io5o) | Concorre em passivo bancário e FIDC; confirma demanda |
| **Mercado de FIDC** (Bloxs, 1T26) | FIDCs foram o principal motor do crescimento das emissões de dívida (+38% no trimestre) e são "a porta de entrada do middle market" | 1T26; resumo de busca | [Lets Money](https://www.letsmoney.com.br/noticias/fidcs-mercado-divida-1t26-middle-market/) | Valida FIDC como produto de porta grande, mas o mercado está cheio: diferencial é a **cadeia + formalização + tributário** |
| **Boutiques de recuperação tributária** | Indicam via contador, diagnóstico gratuito, compartilham resultado; argumento de prazo (créditos de PIS/COFINS de 2021 vencem em 2026) | 2025 e 2026; conteúdo comercial | [Contábeis](https://www.contabeis.com.br/artigos/7628/recuperacao-tributaria-parceria-entre-advogados-e-contadores/) · [Economic News Brasil, BMS](https://economicnewsbrasil.com.br/2025/07/24/recuperacao-de-credito-tributario-bms-consultoria/) | O programa de indicação do contador é **padrão de mercado**: o diferencial da Save é a **esteira depois da recuperação** (caixa, passivo, capital), não a recuperação em si |

**Conclusões (hipóteses para o Luis):**
1. **Nas páginas lidas**, as Big Four vendem governança, sucessão, M&A e ERP a empresas familiares por menu e por proposta; **não** aparecem recuperação de crédito a êxito nem FIDC de cadeia para a PME. É o espaço da Save, mas é achado de duas páginas e três resumos, não pesquisa exaustiva.
2. **Integração é o discurso** (KPMG: times integrados e ciclo de vida). A Save precisa mostrar a **conexão entre produtos com execução** (crédito recuperado que vira caixa e lastro), que o portfólio das Big Four não mostra.
3. **O contador como indicador é o padrão** das boutiques de recuperação. Para o parceiro não migrar, a oferta dele deve incluir o que a boutique de recuperação não tem: produtos de capital, passivo e estruturação.
4. **Preço público é raro** (nenhuma das páginas lidas traz tabela). Manter valores fora do material de parceiro é coerente com o mercado.
5. Estatísticas de firmas (percentuais de sucessão, governança, IA) são autodeclaradas: usar só com fonte primária e nunca como dado da Save.

---

## 7. Perguntas ao Luis

**As cinco decisões de priorização (responder primeiro):**
1. **Escopo 2027 no parceiro:** só produtos prontos nas ondas 1 e 2 e descobertas somente depois do G2 de 15/12/2026, ou prontos mais descobertas já no Q1? (recomendação: a primeira)
2. **Porta de entrada do Q1:** abrir pela porta média (Gestão de Contas, recuperação e reforma pelo Master e indicador) e só depois a porta grande, ou abrir as duas em paralelo com condutor dedicado à grande?
3. **Regra do café:** "fora da meta" vale só para recuperação ou para todo o portfólio? O café tem o maior honorário esperado da base e é o núcleo de FIDC e funding; sugiro separar: fora do ranking de recuperação, **dentro** do ICP de produtos financeiros e de estruturação.
4. **Parceiro de perfil alto:** aprova o piloto de 3 parceiros (M&A, ex-corporate, contador) até o Q2/2027, com a condução na Save e a remuneração de indicação × condução ainda adiada (D11)? Ou antecipa a definição?
5. **N1 e CFO terceirizado:** próprio ou parceiro, decidido até jan/2027 (a onda 3 e o caso "em crescimento" dependem disso)?

**Demais perguntas:**
6. Aprova o **score da seção 2.3** (pesos e faixas) como versão para rodar 90 dias com a Jenifer, e o campo "produto de entrada" no HubSpot (`depto-dados`)?
7. Quem contrata e quem presta a Gestão de Contas, e há habilitação? (bloqueia a onda 1.)
8. Preço e consulta do Funrural (T19) estão pendentes seus: sem isso, T19 sai do kit do Q1.
9. A lista de prospects de 29/09 cobre só carnes, hortifrúti e pescados. Autoriza ampliar para indústria de alimentos, café e cadeia, e regime por Minha Receita só para esses prospects (mesma regra: nunca consultar CNPJ de cliente)?
10. O critério de elegibilidade do crédito internacional é o v2.3 (R$ 50 mi, US$ 5 mi, garantia 2x) ou o da reunião de 13/10 (ativos acima de R$ 60 mi)? Muda a lista de qualificados e o playbook do café. Pergunta ao João até 31/10.
11. A lista de exportadores e tradings de café com ativo acima de R$ 60 mi (compromisso de 13/10): quer que a Inteligência Comercial monte a primeira versão a partir da base da Receita, em máquina local?
12. Autoriza uma segunda rodada de pesquisa de concorrência com abertura das páginas da PwC e da EY, e levantamento de preço de FIDC e de CFO terceirizado em 3 prestadores?

---

## 8. Os três blocos da entrega (`infra/padrao-entrega.md`)
**O que você pediu:** seções 1 a 7 acima.
**O que você também precisa:** (a) a conversão do funil por produto não existe: sem o campo "produto de entrada" no HubSpot, o score e a priorização seguem hipótese por pelo menos 90 dias; (b) o ICP do cooperativo e do laticínio contradiz a ideia de "segmento lácteo" na recuperação; (c) o piso de R$ 30 mi (K8) e de US$ 5 mi (K1) do crédito internacional deixa de fora o caso da indústria de R$ 8 mi/ano; vale dizer ao parceiro desde já que esse caso é N1 e capital, não crédito internacional; (d) a janela de 2027: decadência de 5 anos corrói as competências mais antigas todo mês (ponto de urgência da onda 1, que boutiques concorrentes já usam).
**O que falta e quem fornece:** conversão por produto (Dados, após o campo novo); decisão do Luis nas perguntas 1 a 5; quem contrata a Gestão de Contas (Júnior, Save Invest); respostas do João Mattos até 31/10; parecer do Jurídico sobre CVM, OAB e BCB; ficha de P6, P10, P11, P16 no modelo de `produtos.md` (Solucoes e Internacional); lista de exportadores de café (Intel Comercial, com a base da Receita); páginas da PwC e da EY abertas (nova rodada de pesquisa).

## 9. Registro `revisao`
```json
{"gerente":"depto-intel-comercial","especialistas":["Arquiteto de ICP & Segmentação","Analista de Sinais de Compra","Lead Scoring","Planejador de Territórios","Analista de Concorrência","Recrutamento de Parceiros","depto-marketing (Enablement e Co-branding)"],
 "rodadas":2,
 "areas_consultadas":[],
 "aprovado":false,
 "ajustes":["Rodada 1: nomes de clientes do handoff trocados por <EMPRESA>; heurísticas de piso de porte e de score marcadas como HIPÓTESE; café destacado como decisão; conflito do segmento lácteo sinalizado.","Rodada 2: conferido contra regras-e-proibidos (taxa, 'fundo', holding, blindagem fora do material de parceiro), D59 e K1 a K10; fontes da seção 6 com data e marca de página não aberta.","auditar_texto.py em 22/10: restam 2 alertas altos e 2 médios, todos na coluna 'NÃO dizer' (frases proibidas citadas de propósito) e na descrição do concorrente; é documento interno, não peça para fora.","Pendente: validação do Jurídico (OAB, CVM, BCB), da Qualidade (auditar_texto.py) e do Tributário (T18, T19, reforma) antes de qualquer peça para fora; pesquisa web limitada a duas páginas abertas e resumos de busca."]}
```
Fontes internas: `docs/portfolio-2027/*`, `docs/ecossistema/*`, `skills/depto-solucoes/references/playbooks-setoriais.md`, `skills/depto-internacional/references/{elegibilidade,regras-e-proibidos}.md`, e os dados locais `departamentos/intel-comercial/icp-2026-10-19.json` e `Leitura-Receita-2026-09-29.md` (só agregados, sem CNPJ). Nenhum `.env` lido, nenhuma chamada a API do HubSpot.
