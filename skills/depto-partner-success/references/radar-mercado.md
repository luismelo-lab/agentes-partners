# Radar de Mercado: áreas comerciais (fonte compartilhada)

- **Data-base:** 16/10/2026 · **Próxima revisão:** 23/10/2026
- **Áreas que usam:** partner-success, operacoes-canal, intel-comercial, marketing, pos-venda, pessoas, celula-daniela, celula-jenifer
- **Como ler:** cada item traz dado/tendência (data) · implicação para a Save · ação do agente · fonte (URL, data de publicação, data de consulta) · confiança.
- **Confiança:** **alta** = fonte primária/oficial ou pesquisa com método publicado · **média** = pesquisa de fornecedor ou fonte secundária confiável · **baixa** = blog/agregador, número não conferido na origem.
- **Regras de uso:** dado de mercado não substitui o número do HubSpot (scripts de cada área). Citar sempre fonte e data. Sem fonte = "não localizado". Pesquisa de fornecedor (Omie, Salesforce, HubSpot, PartnerStack) tem viés comercial: usar como direção, não como meta.
- **Complementa, não repete:** `depto-partner-success/references/boas-praticas.md` (onboarding 90 dias, tiers, certificação, PRM leve) e `depto-operacoes-canal/references/boas-praticas.md` (registro de oportunidade, comissão sobre recebido, clawback).

---

## 1. Mercado contábil brasileiro 2025–2026

**1.1 Tamanho da base: 549.516 profissionais ativos**
- **Dado (16/10/2026):** 549.516 profissionais ativos nos CRCs: 416.316 contadores e 133.200 técnicos. Sudeste 50,4%; Sul 18,1%; Nordeste 16,7%; Centro-Oeste 8,7%; Norte 6,1%. SP 154.762; MG 55.709; RJ 55.353. Em jan/2023 eram 526.697 (+4% em 3,7 anos).
- **Implicação:** o universo de indicadores cresce devagar. A disputa é pela atenção do contador, não por novos contadores.
- **Ação do agente:** Intel Comercial usa a divisão por UF para dimensionar o recrutamento por Master. Atualizar todo mês.
- **Fonte:** CFC, Profissionais ativos por região — https://www3.cfc.org.br/SPW/crcs/ConsultaPorRegiao.aspx?Tipo=0 · atualização 16/10/2026 · consulta 16/10/2026. Série 2023: https://www.contabeis.com.br/noticias/16964/contabilidade-no-brasil-possui-490-mil-profissionais/ (citado em busca) · consulta 16/10/2026.
- **Confiança:** alta.

**1.2 Número de escritórios (organizações contábeis): cerca de 85–100 mil**
- **Dado (2024–2025):** total oficial do CFC para 2026 **não localizado** na consulta pública. Estimativas secundárias: "quase 100 mil" organizações em 2024; 98 mil escritórios ativos; mais de 99% micro ou pequenas.
- **Implicação:** base pulverizada. Programa de indicadores precisa de escala com baixo custo de atendimento (conteúdo, trilha e régua), não de gestão 1 a 1.
- **Ação do agente:** Intel Comercial conta CNAE 6920-6/01 ativo por UF na base da Receita (`receita_cnpj.py --prospectar`). Esse vira o número oficial da casa, com mês de referência.
- **Fonte:** Roberto Dias Duarte, *Evolução das Organizações Contábeis no Brasil* — https://www.robertodiasduarte.com.br/?p=90454 · s/d (dados até 2024) · consulta 16/10/2026. Contábeis/Bhub, mar/2025 — https://www.contabeis.com.br/artigos/70319/consolidacao-no-setor-contabil-brasileiro-oportunidades-e-desafios-para-investidores/ · consulta 16/10/2026.
- **Confiança:** baixa (estimativa secundária).

**1.3 Consolidação: roll-ups com dinheiro de fundo**
- **Dado (26/11/2025):** a BHub fez a 10ª aquisição (Agrocontar, maior escritório contábil do agro, cerca de R$ 40 mi de faturamento). Tem mais 10 escritórios parceiros de distribuição que podem ser comprados. Captou US$ 10 mi (pré-Série B) e planeja Série B em 2026. Em dez/2025 contratou CFO ex-Pátria para conduzir o roll-up. Nos EUA, M&A entre firmas contábeis cresceu 26% em 2025 (Capstone).
- **Implicação:** parte dos escritórios indicadores vai mudar de dono. Ao mudar de dono, a relação de indicação pode passar a ser decidida por um comprador com política própria de parceiros. Ao mesmo tempo, um consolidador é um "Master" em potencial com dezenas de carteiras.
- **Ação do agente:** Partner Success marca no HubSpot os indicadores adquiridos ou em negociação (sinal de risco de churn). Intel Comercial mapeia os consolidadores (BHub, Contabilizei e outros) como alvos de parceria Master.
- **Fonte:** Brazil Journal — https://braziljournal.com/bhub-compra-o-maior-escritorio-de-contabilidade-do-agro/ · 26/11/2025 · consulta 16/10/2026. Startups.com.br (CFO) — https://startups.com.br/danca-das-cadeiras/bhub-traz-ex-patria-investimentos-e-ex-latitud-para-a-diretoria/ · dez/2025 · consulta 16/10/2026. Capstone via R. D. Duarte — https://www.robertodiasduarte.com.br/?p=116963 · 2026 · consulta 16/10/2026.
- **Confiança:** alta (BHub) · média (dado dos EUA).

**1.4 Reforma tributária: o cliente pergunta, o contador não tem plano**
- **Dado (abr–mai/2026, publicado em 15/07/2026):** na 3ª Sondagem Omie (com Fenacon, Sescons e CRC-MG), 68% dos contadores já foram procurados por clientes sobre a reforma. 56% estão em estágio inicial, sem plano de ação. Só 5% têm estratégia estruturada. 70% esperam papel mais consultivo. A amostra é pequena (149 respostas). Na edição de 2025 (448 respostas), mais de 60% não se sentiam preparados, e metade estimava impacto em 90% ou mais da carteira.
- **Implicação:** o contador tem demanda e não tem tempo nem método. A Save pode chegar como "braço técnico" que gera receita ao escritório e o ajuda a responder o cliente, sem competir com ele.
- **Ação do agente:** Marketing monta o kit "reforma + créditos de PIS/COFINS antes de 2027" para o contador repassar (com Tributário e Revisor). A Jenifer usa o gancho "seu cliente já perguntou da reforma?" na cadência de recrutamento.
- **Fonte:** Fenacon — https://fenacon.org.br/reforma-tributaria/contadores-ja-sentem-impacto-da-reforma-tributaria-mas-maioria-ainda-nao-tem-plano/ · 15/07/2026 · consulta 16/10/2026. Relatório Omie 1S2026 — https://www.omie.com.br/assets/docs/report_sondagem_omie_contabil_1S2026.pdf · 2026 · consulta 16/10/2026. Edição 2025 — https://amdjus.com.br/pesquisa-revela-maioria-dos-contadores-nao-se-sente-preparada-para-a-reforma-tributaria/ · 2025 · consulta 16/10/2026.
- **Confiança:** média (pesquisa de fornecedor, amostra pequena).

**1.5 Transição PIS/COFINS → CBS: janela e risco ao mesmo tempo**
- **Dado (LC 214/2025; atos de 2026):** PIS/COFINS deixam de existir a partir de 2027 (CBS plena). Pelos arts. 378–383 da LC 214/2025, saldos credores escriturados na EFD-Contribuições continuam válidos. Podem compensar CBS ou ser ressarcidos/compensados com outros tributos federais, mantido o prazo de uso. Pontos em discussão: o Decreto 12.955/2026 (art. 602) condiciona o uso a pedido nos termos de ato da RFB, e há debate sobre créditos extemporâneos após a EFD de dez/2026. A RFB criou equipes nacionais para auditar PER/DCOMP de PIS/COFINS: Portaria CODAR 316 (15/06/2026), 340 (04/08/2026) e 348 (17/08/2026).
- **Implicação:** "agora ou nunca" é argumento comercial forte, mas a fiscalização sobre o mesmo crédito aumentou. Cresce o peso de tese bem documentada e de linguagem sem promessa.
- **Ação do agente:** Tributário valida um parágrafo-padrão sobre a transição (sem prometer prazo nem êxito), e o Marketing só usa esse texto. Pós-venda acompanha intimações de PER/DCOMP dos clientes. Jurídico avalia o art. 602 do Decreto.
- **Fonte:** LC 214/2025 — https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm · 16/01/2025 · consulta 16/10/2026. Análise (art. 602 e portarias) — https://analise.com/opiniao/22747 · 2026 · consulta 16/10/2026. Portaria CODAR 316 — https://okai.com.br/documento/2026-06-16/portaria-codar-no-316-de-15-de-junho-de-2026 · 16/06/2026 · consulta 16/10/2026. Portarias 340/348 — https://atlaspublico.com.br/noticias/receita-federal-cria-equipes-para-auditoria-de-creditos-de-717694 · ago/2026 · consulta 16/10/2026.
- **Confiança:** alta (lei) · média (interpretação e portarias via fonte secundária; conferir no DOU).

**1.6 IA no escritório contábil: uso alto, preparo baixo**
- **Dado (abr–mai/2026, publicado em 02/09/2026):** pesquisa IOB/Fenacon/CFC com 393 profissionais. 78% usam IA ao menos uma vez por semana, e 53% todo dia. As maiores dores: retrabalho manual (34%) e falta de tempo para consultoria (20%). 58% acham que a IA aumenta o valor estratégico do contador; só 2% a veem como ameaça. 68% não recebem capacitação em IA. As maiores preocupações são vazamento de dados de clientes (33%) e uso indevido de informação confidencial (22%).
- **Implicação:** a IA tira tempo do operacional (escrituração, obrigações). O escritório quer vender consultoria e tem medo de expor dados do cliente. A Save entra como consultoria pronta, com tratamento seguro de dados.
- **Ação do agente:** Partner Success inclui na trilha um módulo "IA + créditos: como o escritório vira consultivo" e uma seção curta "como a Save trata os dados do seu cliente" (com o TI/LGPD).
- **Fonte:** Fenacon — https://fenacon.org.br/noticias/ia-avanca-na-contabilidade-78-dos-profissionais-ja-usam-tecnologia-no-trabalho-e-58-veem-ganho-de-valor-estrategico-na-profissao/ · 02/09/2026 · consulta 16/10/2026.
- **Confiança:** média-alta (com CFC; amostra de 393).

**1.7 Carteira dos escritórios: o Lucro Real é raro**
- **Dado (publicado em 16/09/2025, dados da Receita):** 16,29 mi de MEI (63,3%); 7,35 mi no Simples (28,6%); 1,51 mi no Lucro Presumido; 230 mil no Lucro Real.
- **Implicação:** a tese de PIS/COFINS não cumulativo (Lucro Real) está em cerca de 1% das empresas. Um escritório médio tem poucos clientes desse perfil. O indicador certo é o escritório com carteira de Real/Presumido, não qualquer escritório.
- **Ação do agente:** Intel Comercial prioriza o recrutamento de escritórios cuja carteira provável tenha Lucro Real/Presumido (porte, segmento e UF). Lead scoring de indicador pondera esse ponto.
- **Fonte:** ReformaTributaria.com — https://www.reformatributaria.com/brasil/286-das-empresas-estao-no-simples-so-230-mil-estao-no-lucro-real/ · 16/09/2025 · consulta 16/10/2026. Mapa de Empresas 2026 (MDIC): **não localizado** nesta consulta.
- **Confiança:** média (fonte secundária citando a Receita; data-base não informada).

**Proposta de valor para o contador (síntese da seção 1):** "Seu cliente já perguntou da reforma. A Save faz a revisão de créditos antes da virada para a CBS, com tese documentada. Seu escritório fica com o papel consultivo e uma receita nova, sem expor dados nem criar retrabalho." Linguagem sem promessa de valor ou êxito (passar pelo Revisor).

---

## 2. Programas de parceiros

**2.1 Investimento em parcerias continua subindo, mas pouco integrado**
- **Dado (29/09/2025):** PartnerStack/Wynter, 100 líderes de B2B SaaS (US$ 50 mi+). 69% vão aumentar o investimento em parcerias e nenhum vai reduzir. 99% dizem que parceria é parte-chave do go-to-market, mas só 26% a têm integrada à operação. 35% do novo pipeline é influenciado por parceiros (mid-market e enterprise). 48% dizem que o alinhamento com parceiros encurta o ciclo. Só 42% usam atribuição multitoque.
- **Implicação:** "sourced" (o parceiro originou) e "influenced" (o parceiro ajudou) são métricas diferentes. A Save hoje mede só a origem. Medir a influência mostra o valor do Master também nos negócios que ele não originou.
- **Ação do agente:** Operações de Canal propõe dois campos no HubSpot: origem (sourced) e participação (influenced: reunião conjunta, documento obtido via contador). Partner Success reporta os dois no QBR.
- **Fonte:** PartnerStack — https://partnerstack.com/resources/research-lab/the-state-of-partnerships-in-gtm-2026 · 29/09/2025 · consulta 16/10/2026.
- **Confiança:** média (fornecedor; amostra de SaaS dos EUA).

**2.2 O parceiro quer co-venda, não treinamento**
- **Dado (04/03/2026):** Futurum, 400 decisores de parceiros (1S2026). O apoio em co-venda (co-sell) virou a prioridade nº 1: 39,2% (+14,6 p.p.). Gestão de conta dedicada: 38,2% (+13,3 p.p.). Treinamento caiu para o último lugar: 17,5% (−14,7 p.p.).
- **Implicação:** atualiza a ênfase da Academia. O indicador valoriza que alguém da Save vá junto à reunião e conduza a parte técnica, mais do que cursos.
- **Ação do agente:** Partner Success transforma a trilha em "certificação mínima + co-venda": a 1ª e a 2ª indicação de cada indicador novo têm reunião conjunta (Jenifer ou técnico). Mede o tempo até o 2º negócio.
- **Fonte:** Futurum Group — https://futurumgroup.com/press-release/co-sell-support-jumps-14-6-points-to-39-2-displacing-developer-tools-as-channel-partners-1-vendor-priority/ · 04/03/2026 · consulta 16/10/2026.
- **Confiança:** média (setor de TI; tendência transferível).

**2.3 Medir até o 2º negócio, não só o 1º**
- **Dado (Forrester, blog):** quanto mais rápido o parceiro fecha os dois primeiros negócios, maior a chance de virar parceiro ativo de longo prazo. A recomendação é acompanhar a conclusão do onboarding e o tempo do recrutamento ao 2º negócio.
- **Implicação:** o `metricas_ps.py` mede o tempo até o 1º ganho. Um parceiro com um único ganho pode ter sido sorte.
- **Ação do agente:** Partner Success acrescenta "tempo até o 2º negócio ganho" e "% de indicadores com 2 ou mais ganhos em 12 meses".
- **Fonte:** Forrester — https://www.forrester.com/blogs/actionable-insights-and-metrics-that-unlock-channel-sales-growth · data não confirmada · consulta 16/10/2026.
- **Confiança:** média.

**2.4 Menos parceiros, mais capazes; remunerar o ciclo inteiro**
- **Dado (2026):** Omdia (mai–jul/2026): os fornecedores migram para "menos parceiros e mais capazes" e para parceiros consultivos. A Canalys/Omdia (Alla Roiuk, jan/2026) defende reconhecer e remunerar o parceiro em todo o ciclo do cliente (créditos de co-venda), não só na transação final.
- **Implicação:** reforça a pirâmide Master → indicador. Abre a ideia de um bônus não financeiro ou SPIFF por etapa (documento entregue, reunião conjunta, cliente renovado), desde que validado pelo Jurídico.
- **Ação do agente:** Operações de Canal desenha o rascunho de "pontos por etapa" para o nível do parceiro (sem dinheiro na v1, conforme a base atual).
- **Fonte:** Omdia — https://omdia.tech.informa.com/blogs/2026/july/omdia-unveils-champions-in-the-2026-cloud-and-data-center-ecosystem-leadership-matrix · jul/2026 · consulta 16/10/2026. Dutch IT Channel (Canalys/Omdia) — https://www.dutchitchannel.nl/research/721643/it-markt-2026-groei-dwingt-tot-vernieuwing-partner-ecosystemen · 05/01/2026 · consulta 16/10/2026.
- **Confiança:** média.

**2.5 Registro de oportunidade fecha mais (dado de PRM)**
- **Dado (13/08/2026):** Channelscaler Scaler Index, mais de 30 mil parceiros (2016–2025). A taxa de fechamento de negócios levados por parceiros quase triplicou em três anos, e o valor dos registros fechados cresceu mais de 8 vezes.
- **Implicação:** confirma o registro de oportunidade com aprovação e prazo (base de Operações de Canal) como alavanca, não burocracia.
- **Ação do agente:** a célula da Daniela mede a conversão de negócios "registrados e aprovados" contra os "não registrados".
- **Fonte:** Channel Dive — https://www.channeldive.com/news/channelscaler-unveils-partner-program-performance-metrics/827862/ · 13/08/2026 · consulta 16/10/2026.
- **Confiança:** média (fornecedor; sem valores absolutos).

**2.6 IA nos times de parcerias**
- **Dado (2026):** Partnership Leaders: 96,5% das organizações de parcerias usam IA (sumário executivo). PartnerStack: 49% planejam IA para seleção de parceiros e contas e para gestão do programa. Forrester (fev/2026): 75% vão aumentar o investimento em tecnologia de marketing de parceiros.
- **Implicação:** o uso de agentes da Save está em linha com o mercado. O diferencial passa a ser a qualidade do dado e a revisão humana.
- **Ação do agente:** nenhuma nova. Manter portões humanos.
- **Fonte:** Partnership Leaders — https://lp.partnershipleaders.com/ai-partnerships-2026-executive-summary · 2026 · consulta 16/10/2026. Forrester — https://www.forrester.com/blogs/category/channel-marketing · fev/2026 · consulta 16/10/2026.
- **Confiança:** média.

**2.7 Benchmarks numéricos de programa: o que NÃO foi localizado**
- % de parceiros ativos (padrão de mercado), tempo médio até o 1º negócio com fonte primária, uso de MDF e SPIFF em serviços profissionais, percentuais de comissão de indicação para contadores: **não localizado** com fonte confiável 2025–2026. Os números que circulam ("80/20", "90 dias") são de modelos e blogs. Usar o próprio HubSpot como linha de base.
- **Big Four:** a KPMG atribuiu parte do crescimento de Advisory no FY2025 (US$ 39,8 bi, +5,1%) a projetos feitos com parceiros de aliança. A Deloitte (FY2025, US$ 70,5 bi) opera uma "rede de ecossistemas e alianças" e lançou a Global Agentic Network (mai/2025). Participação das alianças na receita: **não localizado**. Programas formais de indicação das Big Four no Brasil: **não localizado**. O padrão visível é aliança com dono executivo, plano conjunto e entrega conjunta, que corresponde ao JBP/QBR já previsto na base.
- **Fonte:** CPA Practice Advisor (KPMG) — https://www.cpapracticeadvisor.com/2025/12/17/kpmg-sees-global-revenue-rise-to-39-8-billion-in-2025/175177/ · 17/12/2025 · consulta 16/10/2026. Deloitte — https://www.cpapracticeadvisor.com/2025/10/01/deloitte-tops-70-billion-in-global-revenue/170024/ · 01/10/2025 · consulta 16/10/2026.
- **Confiança:** alta (receitas) · lacuna declarada.

---

## 3. Vendas B2B e BDR

**3.1 Comprador quer se virar sozinho, mas valida com o vendedor**
- **Dado (09/03/2026 e 20/05/2026):** Gartner, 646 compradores B2B (ago–set/2025): 67% preferem uma compra sem vendedor, e 45% usaram IA numa compra recente. Release de maio/2026: 69% voltam ao vendedor para validar o que a IA disse. Compradores confiantes têm 2 vezes mais chance de fechar um negócio de qualidade.
- **Implicação:** o empresário vai pesquisar "crédito de PIS/COFINS" numa IA antes de falar com a Save. O papel do BDR e do técnico é validar e dar clareza de valor, não apresentar o básico.
- **Ação do agente:** Marketing publica conteúdo técnico citável (FAQ e páginas com base legal) para aparecer nas respostas de IA. A célula da Jenifer abre a reunião com "o que você já pesquisou?" e um mini-diagnóstico.
- **Fonte:** Gartner — https://www.gartner.com/en/newsroom/press-releases/2026-03-09-gartner-sales-survey-finds-67-percent-of-b2b-buyers-prefer-a-rep-free-experience · 09/03/2026 · consulta 16/10/2026. Gartner — https://www.gartner.com/en/newsroom/press-releases/2026-05-20-gartner-survey-finds-sixty-nine-percent-of-b-two-b-buyers-turn-to-sales-reps-to-validate-ai-generated-insights · 20/05/2026 · consulta 16/10/2026 (página bloqueada; números via buscador).
- **Confiança:** alta (67%) · média (69%).

**3.2 IA economiza tempo, mas a maioria desperdiça o ganho**
- **Dado (19/05/2026):** Gartner, 210 CSOs (jan–fev/2026). A IA poupa quase 5 horas por semana por vendedor, mas 72% das organizações não reinvestem esse tempo em atividades de alto valor. Quem reinveste tem 2,2 vezes mais chance de superar a meta de clientes e 3,1 vezes de superar a conversão lead→oportunidade. 25% têm retorno de IA de 50% ou mais; 20% têm retorno negativo de 50% ou mais.
- **Implicação:** o ganho dos agentes da Jenifer e da Daniela só aparece se o tempo liberado virar ligação, reunião e visita.
- **Ação do agente:** Pessoas e Resultados acompanham "horas liberadas → reuniões a mais por semana" (antes e depois de cada agente). Esse é o KPI de ROI dos agentes.
- **Fonte:** Gartner — https://www.gartner.com/en/newsroom/press-releases/2026-05-19-gartner-survey-finds-ai-saves-sellers-nearly-five-hours-per-week-yet-seventy-two-percent-of-sales-organizations-fail-to-reinvest-time-in-high-value-activities · 19/05/2026 · consulta 16/10/2026.
- **Confiança:** alta.

**3.3 Vendedor vende 40% do tempo; agentes de prospecção já são maioria**
- **Dado (03/02/2026):** Salesforce State of Sales, 4.050 profissionais (ago–set/2025). Vendedores passam 40% do tempo vendendo. 54% já usaram agentes de IA, e quase 9 em 10 vão usar até 2027. Expectativa: −34% no tempo de pesquisa de prospects e −36% na redação de e-mails. Top performers usam agentes de prospecção 1,7 vez mais. 79% dos top performers priorizam a higiene de dados, contra 54% dos fracos. 48% não têm tempo para prospecção fria.
- **Implicação:** confirma o desenho da célula da Jenifer (pesquisa, lista e rascunho por agente). A higiene de CRM é o diferencial, não um acessório.
- **Ação do agente:** a célula da Jenifer mede o tempo por lista e por rascunho. A Higiene de CRM roda toda semana antes da cadência.
- **Fonte:** Salesforce — https://www.salesforce.com/news/stories/state-of-sales-report-announcement-2026/ · 03/02/2026 · consulta 16/10/2026.
- **Confiança:** média-alta (fornecedor; amostra grande).

**3.4 Taxa de resposta de e-mail frio: cerca de 3–4%**
- **Dado (2026):** Instantly (dados de 2025): média de 3,43%; quartil superior 5,5%+; top 10% acima de 10,7%. Saleshandy (jan–jun/2026, 53 mi de e-mails): 3,7%. As metodologias variam até 7,6 vezes. A Belkins, contando só respostas humanas, chega a 0,45%. Mensagem personalizada por sinal de compra: 15–25% (Autobound; não conferido).
- **Implicação:** e-mail frio em massa rende pouco. O ganho vem da relevância (sinal de compra, segmento, tese provável), não do volume.
- **Ação do agente:** a célula da Jenifer define a meta de resposta por canal com o histórico próprio. Toda mensagem cita um sinal concreto (filial nova, regime, segmento). Nada de disparo em massa.
- **Fonte:** Instantly — https://instantly.ai/blog/ai-sales-agent-benchmarks-2026-the-complete-performance-report/ · atualizado em 16/09/2026 · consulta 16/10/2026. Saleshandy — https://saleshandy.com/blog/cold-email-statistics/ · 2026 · consulta 16/10/2026.
- **Confiança:** média.

**3.5 WhatsApp é o 1º contato, mas pela API oficial**
- **Dado (2026):** Panorama RD Station 2026 (resumo de jun/2026): WhatsApp é o principal canal de 1º contato para 75% das equipes de vendas, mas 57% não usam a API oficial. 75% das empresas não bateram a meta de vendas em 2025, e 62% não acompanham a conversão do funil. A Meta proíbe chatbots de IA "de uso geral" na API do WhatsApp Business desde 15/01/2026. Atendimento e vendas com IA da própria empresa continuam permitidos.
- **Implicação:** o uso do WhatsApp pela Save (Eazybe, leitura) está alinhado. O agente nunca deve responder sozinho no WhatsApp. Se houver automação de envio, ela vai pela API oficial e com template aprovado.
- **Ação do agente:** TI registra a política da Meta na governança de IA. As células mantêm "o agente rascunha, a pessoa envia".
- **Fonte:** Portal Tela (RD Station 2026) — https://www.portaltela.com/noticias/economia/2026/06/01/panoramas-rd-station-2026-indicam-gestao-marcada-pelo-improviso/ · 01/06/2026 · consulta 16/10/2026. RD Station — https://www.rdstation.com/pesquisas/panorama-marketing-vendas/edicao-2026/vendas/ · 2026 · consulta 16/10/2026. Olhar Digital (Meta) — https://olhardigital.com.br/2025/10/18/pro/whatsapp-business-vai-proibir-chatbots-de-ia-entenda/ · 18/10/2025 · consulta 16/10/2026.
- **Confiança:** média (RD) · alta (política da Meta, várias fontes).

**3.6 Produtividade de SDR/BDR (referência fraca)**
- **Dado (2026, blogs de fornecedores):** mediana de cerca de 11 reuniões por mês (8–15). SDR com 70% ou mais de outbound: 6–10 reuniões por mês. Conversa → reunião: 15–18% na mediana (atribuído à Bridge Group, não conferido). Reunião marcada por IA tem comparecimento de 60–70%, contra 75–85% quando marcada por humano (não conferido).
- **Implicação:** serve só de régua grosseira para a Jenifer (outbound via Master). Não usar como meta sem histórico do HubSpot.
- **Ação do agente:** Resultados calcula a linha de base própria (reuniões por mês, comparecimento, reunião → diagnóstico).
- **Fonte:** GrowthSpree — https://www.growthspreeofficial.com/blogs/b2b-saas-sdr-ae-quota-productivity-benchmarks-2026-by-acv-segment-motion · 2026 · consulta 16/10/2026. Laxis — https://www.laxis.com/es/blog/state-of-ai-sdr-2026/ · 2026 · consulta 16/10/2026.
- **Confiança:** baixa.

**3.7 Qualificação adaptada (MEDDICC/BANT) e ciclo**
- **Dado:** benchmark 2025–2026 de ciclo e conversão para serviços profissionais de recuperação tributária no Brasil: **não localizado**. O SPI 2026 traz utilização e margem, não vendas.
- **Implicação e ação:** prática recomendada (não é pesquisa). Qualificação "MEDDICC leve" para a Save: **M**étrica (crédito potencial estimado e honorário esperado) · **E**conomic buyer (sócio/CFO) · **D**ecisão (quem assina, se o contador participa) · **D**ocumentos (EFD, SPED, acesso ao e-CAC) · **I**dentificar dor (caixa, reforma, auditoria) · **C**ampeão (contador indicador) · **C**ompetição (outra consultoria ou o próprio contador). O BANT entra só no 1º filtro: regime Real/Presumido + porte + decisor. A célula da Jenifer usa esses campos no briefing. O Depto Dados mede o ciclo por etapa no HubSpot.
- **Fonte:** SPI/Deltek — https://www.deltek.com/resources/articles/professional-services-benchmarks/ · 2026 · consulta 16/10/2026.
- **Confiança:** baixa (adaptação metodológica).

---

## 4. Marketing de canal e conteúdo B2B no Brasil

**4.1 Orçamento sobe; geração de leads e marca lideram**
- **Dado (jun/2026):** Intelligenzia: 61,5% das empresas esperam aumentar o orçamento de marketing em 2026. No Brasil, 66,2% alocam em geração de leads, 64,9% em branding e 40,3% em geração de demanda. Edição 2025: aquisição de clientes (65%) e experiência do cliente B2B (61%) como prioridades.
- **Implicação:** concorrência maior por atenção do contador e do CFO. O conteúdo da Save precisa ser útil para o contador repassar ao cliente.
- **Ação do agente:** Marketing prioriza o "conteúdo para o parceiro repassar" (WhatsApp e LinkedIn do contador) acima do conteúdo institucional.
- **Fonte:** Portal Tela (Intelligenzia) — https://www.portaltela.com/noticias/economia/2026/06/05/industrias-brasileiras-ampliam-foco-em-estrategias-de-marketing/ · 05/06/2026 · consulta 16/10/2026. Propmark — https://propmark.com.br/mercado/pesquisa-da-intelligenzia-mostra-que-ha-linha-tenue-entre-marketing-b2b-e-o-b2c/ · 2025 · consulta 16/10/2026.
- **Confiança:** média.

**4.2 Webinars: cerca de 40–60% dos inscritos assistem**
- **Dado (2026, dados de 2025):** ON24 registra média de 239 participantes por webinar (+11%), 60% de conversão inscrito → participante (somando ao vivo e gravação) e cerca de 49 minutos de engajamento. Mediana multiplataforma só ao vivo: 41,6%.
- **Implicação:** webinar com contadores funciona se houver gravação e corte curto para WhatsApp. Meta realista: 40% ao vivo.
- **Ação do agente:** Marketing (Eventos) planeja o webinar mensal "reforma + créditos" para indicadores, com corte de 2 minutos para o parceiro repassar. Medir inscrito → presente → indicação em 30 dias.
- **Fonte:** ON24 — https://www.on24.com/blog/key-takeaways-from-the-webinar-benchmarks-report/ · 2026 · consulta 16/10/2026.
- **Confiança:** média.

**4.3 LinkedIn segue como canal B2B de maior valor percebido**
- **Dado:** 85% dos profissionais de marketing B2B apontam o LinkedIn como a plataforma de melhor valor (CMI, via agregador). Pesquisa LinkedIn Brasil 2026 sobre vídeo e eventos: **não localizado**.
- **Ação do agente:** Marketing (Autoridade Digital) mantém o LinkedIn do Luis e dos técnicos com conteúdo técnico. Mede reunião gerada, não curtida.
- **Fonte:** Snov.io (agregador) — https://snov.io/blog/br/estatisticas-do-linkedin/ · 2026 · consulta 16/10/2026.
- **Confiança:** baixa.

**4.4 CONAR: novo guia de influência vale desde 01/06/2026**
- **Dado (12/05/2026):** o novo Guia de Publicidade por Influenciadores Digitais do CONAR caracteriza a publicidade pela relação com o anunciante (contraprestação, benefício ou conexão material), não mais pelo controle editorial. Vale para conteúdo feito com IA e avatares. Anunciante e agência respondem pelo resultado. Recomenda governança como prova de diligência.
- **Implicação:** se o contador indicador (que recebe pela indicação) posta conteúdo da Save, isso é publicidade e precisa de identificação clara. Vale também para co-branding.
- **Ação do agente:** o Revisor de Marca & Compliance inclui a regra "parceiro remunerado que posta = identificar como publicidade/parceria". O Jurídico valida o texto-padrão de identificação.
- **Fonte:** KLA Advogados — https://www.klalaw.com.br/conar-atualiza-guia-de-publicidade-com-influenciadores/ · mai/2026 · consulta 16/10/2026. Contábeis — https://www.contabeis.com.br/artigos/77061/conar-novas-regras-para-influenciadores-e-ia-a-partir-de-1o-de-junho/ · mai/2026 · consulta 16/10/2026.
- **Confiança:** média-alta (escritórios de advocacia; conferir no texto do CONAR).

**4.5 LGPD: ANPD fiscaliza publicidade com perfilamento e IA em 2026–2027**
- **Dado (Res. CD/ANPD 30, 23/12/2025):** o Mapa de Temas Prioritários 2026–2027 prevê ao menos 75 ações de fiscalização. Inclui uso secundário de dados para publicidade direcionada com perfilamento e 20 ações sobre IA e tecnologias emergentes.
- **Implicação:** listas de prospecção com dados de sócios, enriquecimento e mensagens personalizadas por perfil estão no radar. Legítimo interesse precisa de teste documentado (LIA) e opt-out.
- **Ação do agente:** Intel Comercial e a célula da Jenifer só usam contato pessoal com o LIA aprovado pelo Jurídico (regra 4 da Intel, mantida). TI registra cada agente que trata dado pessoal no inventário.
- **Fonte:** Teletime — https://teletime.com.br/23/01/2026/anpd-define-75-fiscalizacoes-para-bienio-2026-2027-confira-prioridades/ · 23/01/2026 · consulta 16/10/2026. Lefosse — https://lefosse.com/noticias/alerta/anpd-sinaliza-prioridades-de-fiscalizacao-e-regulacao-para-os-proximos-anos/ · 2026 · consulta 16/10/2026.
- **Confiança:** alta.

**4.6 Marco legal da IA (PL 2.338/2023) ainda não aprovado**
- **Dado (28/05/2026):** aprovado no Senado em dez/2024. Na Câmara, comissão especial; o presidente da Câmara previa votar em 2026. Aprovação final ou sanção até 16/10/2026: **não localizado**.
- **Ação do agente:** TI e Jurídico acompanham. As boas práticas atuais (inventário, risco, revisão humana) já antecipam o texto.
- **Fonte:** Teletime — https://teletime.com.br/28/05/2026/motta-votacao-pl-da-ia-junho/ · 28/05/2026 · consulta 16/10/2026.
- **Confiança:** média (status pode ter mudado).

---

## 5. Pós-venda e customer success

**5.1 NPS em serviços profissionais: mediana de 35–55**
- **Dado (2026, agregadores):** serviços profissionais e consultoria com mediana entre cerca de 35 e 55 conforme a fonte. Quartil superior acima de 55–65. Um agregador cita 68, um valor fora da curva. Benchmark primário (Bain, ClearlyRated) 2025–2026 para contabilidade/tributário no Brasil: **não localizado**.
- **Implicação:** usar o NPS próprio (Depto Qualidade) por momento (pós-parecer, pós-ressarcimento). Comparar com o mercado só como faixa.
- **Ação do agente:** Pós-venda e Qualidade adotam a faixa 35–55 como referência provisória e acompanham a tendência própria.
- **Fonte:** PM Toolkit — https://pmtoolkit.ai/benchmarks/nps-benchmarks-by-industry · jan/2026 · consulta 16/10/2026. Koji — https://www.koji.so/docs/nps-benchmarks-by-industry-2026 · 2026 · consulta 16/10/2026.
- **Confiança:** baixa.

**5.2 Expansão na base pesa mais que aquisição**
- **Dado:** Gradient Works (2025, via agregador): expansão em clientes existentes já é 52% da nova receita B2B. A referência clássica (não é de 2025) é Bain: +5% de retenção → +25–95% de lucro. PartnerStack (09/2025): 74% envolvem parceiros em expansão e retenção.
- **Implicação:** o cliente que já recuperou crédito é a melhor conta para o produto financeiro (antecipação, gestão de contas, crédito internacional) e para nova revisão após a reforma.
- **Ação do agente:** Pós-venda gera a lista "cliente ganho + 6 meses" para cross-sell, com a regra do canal (o Master original participa).
- **Fonte:** Komo (agregador) — https://komo.ai/glossary/cross-sell · 2025 · consulta 16/10/2026. PartnerStack (2.1).
- **Confiança:** baixa (agregador) · média (PartnerStack).

**5.3 Risco pós-venda novo: auditoria de PER/DCOMP**
- **Dado:** ver 1.5 (equipes nacionais de auditoria de PIS/COFINS desde jun/2026).
- **Implicação:** o momento de maior risco de NPS negativo é a intimação ou glosa. Comunicar antes reduz a reclamação.
- **Ação do agente:** Pós-venda cria a régua "PER/DCOMP sob auditoria", com aviso ao cliente e ao parceiro e prazos do Jurídico.
- **Confiança:** média.

---

## 6. Pessoas

**6.1 Agentes vão superar vendedores 10 para 1; a percepção de ganho fica abaixo de 40%**
- **Dado (28/07/2026):** Gartner prevê que, até 2028, os agentes de IA superem os vendedores em 10 para 1, mas menos de 40% dos vendedores dirão que os agentes melhoraram a produtividade. 60% dos CSOs dizem que a meta depende de fatores fora do controle deles. CSOs que reformularem dados, automação e experiência têm 5 vezes mais chance de ROI.
- **Implicação:** mais agentes não significam um time melhor. Para um time pequeno (Daniela, Jenifer, Geovana), a experiência de uso decide: poucos agentes, bem integrados, com entrada única.
- **Ação do agente:** Pessoas faz um pulso mensal de 3 perguntas ("o agente me poupou tempo? o rascunho saiu usável? o que eu faria com o tempo?"). O Gabinete mantém o fluxo único.
- **Fonte:** Gartner — https://gcom.pdo.aws.gartner.com/en/newsroom/press-releases/2026-07-28-gartner-predicts-ai-agents-will-outnumber-sellers-10-to-1-by-2028-yet-fewer-than-40-percent-of-sellers-will-say-agents-improved-productivity · 28/07/2026 · consulta 16/10/2026.
- **Confiança:** alta.

**6.2 Brasil usa IA no trabalho acima da média; a empresa fica para trás**
- **Dado (2026):** Microsoft Work Trend Index (05/05/2026; 20 mil pessoas em 10 países): 27% dos brasileiros que usam IA estão em nível avançado, e 72% fazem tarefas que não faziam há um ano. Cultura e liderança pesam mais de 2 vezes mais que fatores individuais na adoção. Datafolha (jun/2026): 24% usaram IA no trabalho (eram 17%). Randstad Workmonitor (jan/2026): 60% temem perder o emprego, e 87% querem aprender. IOB/CFC: 68% dos contadores sem capacitação (1.6).
- **Implicação:** o time vai usar IA de qualquer jeito. O risco é o uso "por fora", sem governança. A capacitação também é benefício para o parceiro.
- **Ação do agente:** Pessoas inclui uma trilha curta de "trabalhar com agentes" no PDI de cada pessoa. Partner Success avalia oferecer a capacitação em IA como benefício do nível do parceiro.
- **Fonte:** Olhar Digital (WTI 2026) — https://olhardigital.com.br/2026/05/11/inteligencia-artificial/brasil-e-destaque-no-uso-avancado-de-ia-no-trabalho-segundo-microsoft/ · 11/05/2026 · consulta 16/10/2026. Portal Tela (Datafolha) — https://www.portaltela.com/noticias/economia/2026/06/27/uso-de-ia-no-trabalho-cresce-medo-de-substituicao-cai-entre-brasileiros/ · 27/06/2026 · consulta 16/10/2026. SBT News (Workmonitor) — https://sbtnews.sbt.com.br/noticia/tecnologia/pesquisa-revela-que-60-dos-brasileiros-tem-medo-de-perder-emprego-para-a-inteligencia-artifical · jan/2026 · consulta 16/10/2026.
- **Confiança:** média-alta.

**6.3 Remuneração variável em vendas B2B: "no escuro"**
- **Dado (2026):** a Pesquisa Nacional de Vendas B2B 2026 (SalesHunter; 1.300+ profissionais, 2.300 empresas, 8 anos) mostra operações parecidas com modelos de salário e variável muito diferentes, por falta de critério. Percentuais de mercado para serviços tributários: **não localizado**.
- **Implicação:** o plano de variável do time Partners deve ter critério escrito: meta sobre receita recebida (coerente com a comissão de parceiros), parte individual e parte de equipe.
- **Ação do agente:** Pessoas propõe um modelo com 3 componentes (resultado recebido, qualidade de CRM, atividade de canal), validado por Resultados e Jurídico.
- **Fonte:** Startups.com.br — https://startups.com.br/artigo/empresas-b2b-operam-com-o-mesmo-cenario-e-ainda-tomam-decisoes-muito-diferentes-sobre-remuneracao/ · 2026 · consulta 16/10/2026.
- **Confiança:** baixa-média.

**6.4 Coaching e treino faltam**
- **Dado (03/02/2026):** Salesforce: 46% recebem pouco feedback sobre as conversas de vendas, e 47% têm pouco roleplay antes de reuniões.
- **Ação do agente:** Pessoas e Partner Success criam um roleplay quinzenal com agente (objeções do empresário e do contador) para a Jenifer e a Daniela.
- **Fonte:** Salesforce (3.3).
- **Confiança:** média.

---

## 7. Agentes de IA em operações comerciais

**7.1 Adoção ampla, impacto financeiro raro**
- **Dado (McKinsey, nov/2025):** 88% usam IA em ao menos uma função. 62% ao menos experimentam agentes. Quase dois terços ainda não escalaram. Só 39% veem impacto no EBIT, e na maioria desses casos o impacto é inferior a 5%. Bain (Tech Report 2025) mapeou 25 casos de uso em vendas, com a maioria das empresas no início.
- **Implicação:** o ROI dos agentes da Save precisa ser medido em poucas métricas duras (horas, reuniões, valor validado, erros evitados), como o piloto do Recuperador já faz.
- **Ação do agente:** Resultados consolida um "placar de agentes" mensal: custo, horas poupadas, uso real e resultado.
- **Fonte:** McKinsey — https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-2025 · nov/2025 · consulta 16/10/2026. Bain — https://www.bain.com/insights/ai-transforming-productivity-sales-remains-new-frontier/ · set/2025 · consulta 16/10/2026.
- **Confiança:** alta.

**7.2 Mais de 40% dos projetos de agentes serão cancelados até 2027**
- **Dado (jun/2025):** Gartner prevê o cancelamento de mais de 40% dos projetos de IA agêntica até o fim de 2027, por custo, valor incerto e controle de risco fraco. Estima só cerca de 130 fornecedores "reais".
- **Implicação:** a carteira de agentes da Save (muitos departamentos) corre o mesmo risco. Cortar ou fundir os agentes sem uso é sinal de maturidade, não de fracasso.
- **Ação do agente:** TI (Governança de IA) faz uma revisão trimestral do inventário: agente sem uso em 60 dias ou sem métrica vai para "pausar ou fundir". Exceção: fluxos ainda não lançados ao time (memória do Luis).
- **Fonte:** Outlook Business (Gartner) — https://www.outlookbusiness.com/artificial-intelligence/over-40-of-agentic-ai-projects-will-be-scrapped-by-2027-says-gartner · jun/2025 · consulta 16/10/2026.
- **Confiança:** alta.

**7.3 Casos públicos de agente SDR (todos de fornecedor)**
- **Dado:** Simpro com o agente Piper (Qualified), em teste A/B: 4,2 vezes mais reuniões marcadas. Salesforce (jul/2026, uso interno): conversão de 6% e 60+ reuniões por semana, implantado em 30 dias. HubSpot Prospecting Agent (página do produto): +14% de leads qualificados, +14% de reuniões, +5% de win rate, a US$ 1 por lead, com modo "revisar antes de enviar". Teste não identificado (Laxis 2026): só IA → 847 reuniões a 11% de conversão; híbrido → 312 reuniões a 38%, com cerca de 2,3 vezes mais receita.
- **Implicação:** o modelo híbrido (agente pesquisa e rascunha, pessoa decide e envia) é o que melhor se sustenta. É o desenho atual das células.
- **Ação do agente:** a célula da Jenifer avalia o Prospecting Agent do HubSpot em modo de revisão, com piloto pequeno e comparação com a cadência atual. A decisão é do Luis, e TI e Jurídico revisam LGPD e escopo.
- **Fonte:** Casestudies.com (Simpro) — https://www.casestudies.com/company/qualified-com/case-study/simpro-books-42x-more-meetings-with-qualified · 2025 · consulta 16/10/2026. Salesforce — https://www.salesforce.com/salesforce-on-salesforce/agentic-presales-qualified-piper/ · jul/2026 · consulta 16/10/2026. HubSpot — https://www.hubspot.com/products/artificial-intelligence · 2026 · consulta 16/10/2026. Laxis — https://www.laxis.com/es/blog/state-of-ai-sdr-2026/ · 2026 · consulta 16/10/2026.
- **Confiança:** média (fornecedor) · baixa (teste sem nome).

**7.4 Risco de automação excessiva: o caso Klarna**
- **Dado (mai/2025):** a Klarna voltou a contratar atendentes humanos após admitir "qualidade inferior" do atendimento só com IA.
- **Implicação:** em serviço técnico e de risco (crédito tributário), a conversa com o parceiro e o cliente continua humana.
- **Ação do agente:** manter a regra "tudo é rascunho" em todas as células.
- **Fonte:** Entrepreneur — https://www.entrepreneur.com/business-news/klarna-ceo-reverses-course-by-hiring-more-humans-not-ai/ · mai/2025 · consulta 16/10/2026.
- **Confiança:** alta.

**7.5 Big Four: agentes como "colegas digitais"**
- **Dado (2025):** a PwC lançou o Agent OS (mar/2025) e relata 25 mil agentes em operações de clientes. O Workbench da KPMG (com Microsoft) conecta 50 agentes, com cerca de mil em desenvolvimento. A meta é que juniores virem gestores de times de agentes. A Deloitte lançou a Global Agentic Network (mai/2025).
- **Implicação:** o modelo "pessoa + célula de agentes" da Save segue o mesmo desenho. O papel de cada pessoa passa a incluir supervisionar agentes (entra no PDI).
- **Fonte:** Business Insider via AOL — https://www.aol.com/articles/4-key-ways-ai-changed-122826506.html · dez/2025 · consulta 16/10/2026. Deloitte — https://www.deloitte.com/au/en/about/press-room/deloitte-launches-global-agentic-network-to-power-digital-workforce-solutions-030625.html · mai/2025 · consulta 16/10/2026.
- **Confiança:** média (números autodeclarados).

**7.6 Práticas recomendadas pela Anthropic (docs públicos)**
- **Dado:**
  - *Building effective agents* (19/12/2024): começar pelo mais simples e só aumentar a complexidade com ganho medido. Preferir workflows previsíveis (encadeamento, roteamento, orquestrador-trabalhadores, avaliador-otimizador) a agentes autônomos em tarefas bem definidas. Projetar as ferramentas com o mesmo cuidado dos prompts. Testar em sandbox, pôr checkpoints humanos e limites de iteração, e dar transparência ao plano do agente.
  - *Effective context engineering for AI agents* (29/09/2025): o contexto é finito. Usar o menor conjunto de informação com alto sinal, buscar dados sob demanda e poucas ferramentas sem sobreposição. Em tarefas longas: compactação, notas estruturadas fora do contexto e subagentes que devolvem só um resumo.
  - *Writing effective tools for agents* (2025): ferramentas desenhadas para o agente, não como API comum. Nomes claros, respostas econômicas e avaliação com casos reais.
- **Implicação:** valida o desenho atual: scripts determinísticos para números, subagentes com perfil curto, revisão do gerente e portões humanos. Também alerta contra excesso de departamentos e ferramentas sobrepostas.
- **Ação do agente:** TI (Governança) adota um checklist Anthropic em toda skill nova: (1) dá para ser workflow em vez de agente? (2) ferramentas sem sobreposição? (3) contexto mínimo? (4) checkpoint humano? (5) avaliação com casos reais antes de ir ao time?
- **Fonte:** https://www.anthropic.com/engineering/building-effective-agents · 19/12/2024 · consulta 16/10/2026. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents · 29/09/2025 · consulta 16/10/2026. https://www.anthropic.com/engineering/writing-tools-for-agents · 2025 · consulta 16/10/2026.
- **Confiança:** alta.

---

## O que contradiz ou atualiza a base atual

1. **Treinamento → co-venda** (atualiza `boas-praticas.md` do PS): a base dá peso à certificação e à Academia. O mercado de 2026 (Futurum) põe a co-venda e a gestão de conta dedicada no topo, e o treinamento por último. Manter a certificação mínima e dar prioridade à reunião conjunta nas 2 primeiras indicações.
2. **Tempo até o 1º negócio → até o 2º** (atualiza `metricas.md`): o indicador de ativação deve incluir o 2º ganho (Forrester).
3. **Só "sourced" → "sourced + influenced"** (atualiza o registro de oportunidade em Operações de Canal): o mercado mede as duas coisas.
4. **"Sem pesquisa web nesta versão"** (`depto-operacoes-canal/references/boas-praticas.md`): este radar é a referência datada. As regras de registro e de comissão sobre o recebido seguem válidas. Benchmark numérico de comissão para contadores: **não localizado**.
5. **Urgência da reforma** (novo para Marketing, Jenifer e Tributário): PIS/COFINS acabam em 2027. Há janela comercial, mas a RFB montou equipes de auditoria de PER/DCOMP de PIS/COFINS (jun–ago/2026). O discurso "agora ou nunca" precisa de tese documentada e linguagem sem promessa.
6. **WhatsApp** (novo para TI e células): desde 15/01/2026 a Meta proíbe chatbots de uso geral na API. 57% do mercado nem usa a API oficial. Reforça "o agente rascunha, a pessoa envia".
7. **CONAR 2026** (novo para Marketing e Revisor): o parceiro remunerado que divulga a Save faz publicidade e deve identificar isso.
8. **Universo de contadores**: 549.516 profissionais ativos (CFC, 16/10/2026). Substitui qualquer número antigo (490 mil ou 530 mil) usado em materiais.
9. **Excesso de agentes** (atualiza a governança): Gartner prevê mais de 40% de cancelamentos e menos de 40% de vendedores percebendo ganho. Sem métrica de uso, um agente deve ser pausado ou fundido. Os fluxos ainda não lançados ao time continuam protegidos.

## 10 ideias para o Luis

1. **Campanha "Antes da CBS"** para indicadores (out/2026–mar/2027), com texto validado pelo Tributário e sem promessa. É o gancho de maior urgência do ano.
2. **Co-venda garantida:** toda 1ª e 2ª indicação de um indicador novo tem reunião conjunta com a Save. Medir o tempo até o 2º ganho.
3. **Campo "influenced" no HubSpot:** mostrar ao Master o valor que ele gera além das próprias indicações (QBR).
4. **Lista de consolidadores** (BHub, Contabilizei e similares) como alvos de parceria Master, mais alerta de indicador adquirido como risco de churn.
5. **Recrutamento focado em carteira de Lucro Real/Presumido** (só cerca de 230 mil empresas no Real): qualidade do indicador acima de volume.
6. **Benefício "IA para o escritório contábil"** no nível do parceiro: workshop curto (68% dos contadores não têm capacitação).
7. **Régua "PER/DCOMP em auditoria"** no pós-venda, avisando cliente e parceiro antes da intimação.
8. **Placar mensal de agentes** (horas poupadas → reuniões a mais). Pausar ou fundir o que não é usado, preservando os fluxos ainda não lançados.
9. **Piloto do HubSpot Prospecting Agent** em modo "revisar antes de enviar" para a Jenifer, com comparação A/B e revisão de LGPD.
10. **Conteúdo citável por IA:** páginas e FAQs técnicas com base legal, porque 67% dos compradores pesquisam sozinhos e 45% usam IA na compra.
