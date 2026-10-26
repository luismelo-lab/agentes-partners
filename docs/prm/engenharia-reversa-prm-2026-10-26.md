# Engenharia reversa dos PRMs de mercado, adaptada à Área Partners

**Versão:** 1.1 (inclui a opção Azure pedida pelo Luis) · **Data de consulta de todas as fontes web:** 26/10/2026, salvo indicação
**Autor:** analista de mercado (agente), para o Luis · **Status:** pesquisa, não é decisão
**Escopo:** Impartner, PartnerStack, Salesforce Partner Cloud (PRM/Experience Cloud), Channeltivity, Allbound (hoje Channelscaler), ZINFI, Mindmatrix Bridge, Crossbeam, Kiflo, apps de PRM para HubSpot (Partner Deals Portal, PartnerPortal.io, Introw), três referências brasileiras (Omie, Conta Azul, Cora) e a opção de construir na Azure, no tenant Microsoft da Save.

## Como ler este documento

- **Confiança:** alta = documentação oficial ou tabela de preço do próprio fornecedor; média = agregador (G2, Capterra, Vendr, TrustRadius) ou material do fornecedor sem método; baixa = estimativa de terceiro, texto truncado ou leitura indireta.
- **Viés comercial:** quase tudo o que existe publicamente sobre PRM é escrito por fornecedor de PRM. Os números de resultado (ROI, taxa de ganho) vêm, na maioria, de estudo pago pelo fornecedor ou de blog de concorrente. Isso está marcado com **[viés fornecedor]**.
- **Limites da pesquisa:** não criei contas, não pedi demonstração e não preenchi formulários. Algumas páginas bloquearam a leitura automática (impartner.com/prm, blog de scorecard da Impartner, cora.com.br). Nesses casos usei a listagem do HubSpot Marketplace, o G2 ou o resultado de busca, e marquei a confiança.
- **Câmbio:** os preços estão em dólar. Converta pela cotação do dia; não fixei taxa.

---

## Parte A. Os produtos por dentro

### A1. Impartner PRM

| Item | O que encontrei | Fonte · confiança |
|---|---|---|
| Posição | Líder no G2 Grid de PRM (Summer 2026, Enterprise), nota 4,5 com mais de 500 avaliações | Impartner, blog de anúncio do G2 Summer 2026 · média [viés fornecedor] |
| Módulos | Onboarding automatizado por gatilho; registro de oportunidade com autocotação do parceiro e transação em marketplace de hiperescala; atribuição de lead com taxa de fechamento; marketing com co-branding e MDF automatizado; Program Compliance Manager (calcula e atribui o nível); plano de negócio por parceiro com metas, notas e anexos; KPIs montados sobre qualquer objeto do CRM; scorecard com métricas e modelos prontos; automação de indicação (referral/afiliado) | HubSpot Marketplace, listagem Impartner PRM; impartner.com (páginas de tiering e business planning, via busca) · média |
| Objetos de dados (sincronia com HubSpot) | Deals→Deals; Leads→Contacts; Contact→Contacts; Company/Account→Companies; User→Contacts; Products→Products; objetos customizados | https://ecosystem.hubspot.com/marketplace/listing/impartner-prm · alta |
| Tiering automático | O Program Compliance Manager calcula os requisitos do nível e atribui o nível ao parceiro que qualifica; o parceiro vê os benefícios e o progresso até o próximo nível | impartner.com (resultado de busca) · média [viés fornecedor] |
| Tela do parceiro | Portal com pipeline dos seus negócios, registro, conteúdo co-branded, progresso de nível, plano de negócio | listagem HubSpot · média |
| Tela do gestor | Pipeline direto e indireto no CRM, conformidade do programa, scorecards, plano de negócio | idem · média |
| Integração CRM | HubSpot (100+ instalações, 0 avaliações na listagem), Salesforce, Microsoft | listagem HubSpot · alta |
| Preço | Emerge a partir de US$ 25.000/ano (G2 e HubSpot Marketplace). Vendr: mediana paga de US$ 53.352/ano (82 compras, faixa de US$ 17.472 a 136.321); preço por conta de parceiro ativa; 25 a 50 parceiros estimados em US$ 30 a 60 mil/ano de lista | G2; HubSpot Marketplace; https://www.vendr.com/marketplace/impartner-software · alta (piso) / média (Vendr) |
| Resultado divulgado | Forrester TEI encomendado pela Impartner: ROI de 296% em 3 anos, +30 a 50% de negócios originados por parceiro, +10% de taxa de ganho, payback em menos de 6 meses. É uma organização composta (modelo, não medição) | https://impartner.com/resources/blog/impartner-forrester-tei-study · média [viés fornecedor] |
| Ponto forte | O mais completo para programa formal com níveis e conformidade automatizada | — |
| Ponto fraco | Preço de empresa grande. Uma avaliação no AWS Marketplace relata que só há **um** formulário de registro de fábrica e que um segundo formulário por tipo de parceiro exige comprar um recurso extra ("Level") | https://aws.amazon.com/marketplace/reviews/reviews-list/prodview-l75vriw7iffmw · média |

### A2. PartnerStack

| Item | O que encontrei | Fonte · confiança |
|---|---|---|
| Posição | Líder no G2 Summer 2026 (nota 4,7) | press release da ZINFI citando o G2 · média |
| Módulos | Recrutamento via rede própria (PartnerStack Network), onboarding, links de afiliado, envio de leads, **envio de deals** (deal submission), recompensas, pagamento global, coleta de formulário fiscal (W-9/W-8BEN), atribuição multitoque | support.partnerstack.com; dupple.com; getapp.com · média |
| Objetos | Partner, Group (grupo de parceiros, que define regra e acesso), Lead, Deal (estágios e formulário por empresa), Customer (habilita comissão recorrente), Reward (comissão), Payout | https://support.partnerstack.com/hc/en-us/articles/6021325335699 · alta |
| Fluxo de registro | O envio de deals é ligado por grupo de parceiros. O parceiro cria o deal na aba "Deals" e o trabalha até o fechamento. Com aprovação manual ligada, o "Closed Won" do parceiro fica em "Closed Won – Pending" até a empresa aprovar, recusar ou devolver para "Working" | idem · alta |
| Comissão | Por estágio do deal (ex.: valor fixo no Closed Won), manual avulsa ou recorrente via registro de cliente. Tipos: fixo, % da receita, recorrente, bônus por faixa, regra por tipo de parceiro ou tamanho do negócio | support.partnerstack.com; dupple.com · média |
| Pagamento | O parceiro saca no próprio painel; a PartnerStack consolida o devido aos parceiros em uma fatura única para a empresa | dupple.com; creative-tim.com · média |
| Métrica pública | Parceiros da Network: mediana de 2 dias da aprovação até a 1ª parceria; mais de 1/3 em 24 h; cerca de 61% em 10 dias (jun/2024). Mede a entrada em um programa, não o 1º negócio | https://partnerstack.com/resources/research-lab/charts/most-network-partners-have-a-median-time-of-2-days-to-joining-their-first-partnership · alta (dado) / média (relevância) |
| Integração CRM | HubSpot, Salesforce, Stripe e outros | HubSpot Marketplace · alta |
| Preço | Não publicado; demo e cotação. Estimativa de terceiro: US$ 800 a 1.000/mês mais 3 a 5% da receita de parceiro | dupple.com · baixa |
| Ponto forte | Melhor motor de pagamento automático e rede de recrutamento para SaaS de alto volume | — |
| Ponto fraco | Desenhado para afiliado e indicação de SaaS com cartão e assinatura. Segundo avaliação, as mensagens com o parceiro são limitadas e as análises, rasas | HubSpot Marketplace (avaliação) · média |

### A3. Salesforce Partner Cloud (antigo Salesforce PRM, sobre Experience Cloud)

| Item | O que encontrei | Fonte · confiança |
|---|---|---|
| Edições e preço | PRM a US$ 25/membro/mês; Partner Ecosystem Management (PEM) a US$ 50/membro/mês, cobrança anual. Existe preço por login, sem valor publicado | https://www.salesforce.com/sales/partner-relationship-management/pricing/ · alta |
| Módulos | Lead Inbox (distribuição de lead ao parceiro sem e-mail), registro de oportunidade com carimbo de hora e checagem de duplicidade, MDF, scorecards e acesso por nível, Partner Tracks (capacitação), incentivos e fidelidade (PEM), deal scoring (Enterprise), Agentforce for Partners (créditos) | página de preço; Trailhead "Accelerate Channel Sales" · alta |
| Objetos | Account de parceiro, Partner User, Lead, Opportunity, Deal Registration, Fund Request/Claim (MDF), Price Book por nível | Trailhead · alta |
| Tela do parceiro | Accounts, Leads e Opportunities estendidas; Sales Path com etapas; cotação com marca e pedido de desconto; só vê a tabela de preço do seu programa e nível | Trailhead · alta |
| Tela do gestor | Relatórios e dashboards prontos com leads e negócios dos parceiros, tempo parado no funil e taxa de fechamento; aprovação de desconto pelo celular | Trailhead · alta |
| Integração CRM | É o próprio Salesforce; não serve a quem tem HubSpot como CRM | — · alta |
| Ponto forte | Dado único (parceiro e venda direta na mesma base), com o conflito resolvido na origem | — |
| Ponto fraco | Exige Salesforce como CRM e implantação por consultoria; cobra por membro do portal | — |

### A4. Channeltivity

| Item | O que encontrei | Fonte · confiança |
|---|---|---|
| Edições | Growth (cerca de 100 parceiros), Mid-Market (centenas), Enterprise (milhares); preço sob consulta | https://www.channeltivity.com/pricing · alta |
| Preço de terceiro | TrustRadius: Standard a US$ 1.599 e HubSpot Edition a US$ 1.899 (periodicidade não clara, provavelmente mensal), sem taxa de implantação | https://www.trustradius.com/products/channeltivity · baixa |
| Módulos | Registro de oportunidade, distribuição de leads, indicação (referral), sincronia de parceiros, conteúdo, capacitação, MDF | HubSpot Marketplace; channeltivity.com · média |
| Fluxo de registro | Status de registro configurável: cada etapa é marcada como aberta ou fechada, e uma etapa padrão recebe os registros novos. O parceiro vê o status, mas só o usuário interno edita. Registros pendentes **expiram automaticamente** após N dias; a data de validade é preenchida quando o registro entra em "Open: Pre-approved"; o vencido vai para uma etapa definida, salvo se já estiver ganho, perdido ou arquivado | help.channeltivity.com (artigos 3000069985, 3000020045, 3000069981) · alta |
| HubSpot | Certificada no Marketplace. Cria uma cópia ligada do deal no HubSpot (automática ou por botão), com sincronia bidirecional por mapeamento de campos. Exige criar uma caixa de seleção no objeto Deal. Importa deals do HubSpot como registros | https://help.channeltivity.com/support/solutions/articles/3000092116 · alta |
| Ponto forte | Melhor documentação pública de registro e expiração; edição dedicada a HubSpot | — |
| Ponto fraco | **Exige escrita no HubSpot** (campo novo e criação de deals) | — |

### A5. Allbound (Channelscaler desde 2024)

| Item | O que encontrei | Fonte · confiança |
|---|---|---|
| Situação | A Allbound comprou a Channel Mechanics (mar/2024), e a empresa combinada passou a usar a marca Channelscaler. É controlada pela Invictus Growth Partners | allbound.com; privsource.com · média |
| Módulos | Portal, conteúdo, análises de canal, registro de oportunidade. Da Channel Mechanics vieram rebates, incentivos, MDF, nivelamento de parceiro, renovações, SPIFF e monitoramento de desempenho | allbound.com (anúncio da aquisição); Capterra · média |
| Métrica pública | Channelscaler Scaler Index (mais de 30 mil parceiros, 2016–2025): a taxa de fechamento de negócios trazidos por parceiro quase triplicou em 3 anos, e o valor dos registros fechados cresceu mais de 8 vezes | Channel Dive, 13/08/2026 (registrado no radar de Partner Success em 16/10/2026) · média [viés fornecedor] |
| Preço | Capterra: a partir de US$ 3.495/mês, sem teste grátis | https://www.capterra.com/p/141976/Allbound/ · média |
| Ponto forte | Automação de programa (incentivo, nível, SPIFF) depois da fusão | — |
| Ponto fraco | Preço alto para 36 parceiros; produto em consolidação pós-fusão | — |

### A6. ZINFI Unified Partner Management (UPM)

| Item | O que encontrei | Fonte · confiança |
|---|---|---|
| Posição | Líder no G2 Summer 2026; afirma nota 4,9 com 587 avaliações e NPS 94 | press releases da ZINFI · baixa [viés fornecedor] |
| Módulos | Oito módulos vendidos separadamente, em seis blocos: Onboard, Enable, Market, Sell, Incentivize e Accelerate. Inclui registro de oportunidade ligado ao CRM, pedido de preço especial com aprovação e Channel Data Management (dados de ponto de venda do distribuidor) | https://www.zinfi.com/products/partner-relationship-management/overview · média |
| Preço | Sob consulta. Diretórios citam cerca de US$ 1.899/mês (Standard) e 2.199/mês (CRM), e uma faixa de mercado de US$ 1.500 a 5.000+/mês; teste de 30 dias | rfp.wiki · baixa (há indício de confusão com os preços da Channeltivity) |
| Ponto forte | Modularidade (compra só o que usa) e serviço de marketing terceirizado | — |
| Ponto fraco | Pensado para fabricante com distribuidor e revenda (POS, preço especial) | — |

### A7. Mindmatrix Bridge

| Item | O que encontrei | Fonte · confiança |
|---|---|---|
| Módulos | Habilitação de ecossistema, de canal e de venda direta; registro de oportunidade (pelo próprio parceiro ou em nome dele); conteúdo co-branded; construtor de jornada de onboarding; LMS; **pontuação de engajamento do parceiro** e KPIs; painéis por persona; automação de processo | https://ecosystem.hubspot.com/marketplace/listing/bridge-5-0-powered-by-mindmatrix · alta |
| Objetos (HubSpot) | Contacts; Opportunities→Deals; Contact Companies→Companies; Users→Contacts; Lead e objetos customizados; sincronia bidirecional configurável | idem · alta |
| Preço | Por quantidade de parceiros, com usuários ilimitados. Core (20 a 500 parceiros) e Enterprise (500+); BridgeAI e Concierge são adicionais. O TrustRadius cita a partir de US$ 499/mês | G2 (atualizado em 19/02/2026); TrustRadius · média (modelo) / baixa (valor) |
| Base instalada no HubSpot | 10+ instalações, 0 avaliações | listagem · alta |
| Ponto forte | Habilitação e marketing pelo canal (o parceiro dispara campanhas com a marca dele) | — |
| Ponto fraco | Pouca tração no HubSpot e avaliações escassas | — |

### A8. Crossbeam (account mapping; fundiu-se com a Reveal em jun/2024)

| Item | O que encontrei | Fonte · confiança |
|---|---|---|
| O que faz | Cruza as bases de CRM de duas empresas sem expor a base inteira. Cada lado define "Populations" (prospects, oportunidades abertas, clientes), e o sistema mostra só as sobreposições | crossbeam.com/use-cases/account-mapping · alta |
| Planos | Free (até 3 assentos, mapeamento de até 50 registros, 1 parceiro offline); Connector a US$ 4.800/ano (1 assento, extra a US$ 1.800/ano, exporta 5 mil registros); Supernode e Enterprise sob consulta (atribuição de receita, objetos customizados) | https://www.crossbeam.com/pricing · alta |
| Fusão | Crossbeam e Reveal (jun/2024), somando mais de 25 mil empresas; manteve a marca Crossbeam | orrick.com; crossbeam.com · alta |
| Métrica pública | "Taxa de ganho 25% maior" em contas sobrepostas com parceiro, sem método | crossbeam.com · baixa [viés fornecedor] |
| Pressuposto | **Os dois lados precisam ter a carteira num CRM.** O escritório contábil brasileiro não tem; a carteira dele está no sistema contábil (Domínio, Alterdata, Questor etc.) | inferência do analista · média |
| Ponto forte | Responde "quais clientes do parceiro já são meus ou estão no meu funil" com privacidade | — |
| Ponto fraco | Inútil sem CRM do outro lado; não é PRM (não tem registro, comissão nem portal) | — |

### A9. Kiflo

| Item | O que encontrei | Fonte · confiança |
|---|---|---|
| Planos | Core a US$ 399/mês para 25 parceiros, escalando com parceiros ativos até 50, com até 3 gestores; Plus e Premier sob consulta. Todos com contrato de 12 meses pago adiantado | https://www.kiflo.com/pricing · alta |
| Core | Portal e registro de lead e deal, cálculo automático de comissão (pagamento disparado à mão), sincronia com HubSpot e Salesforce, onboarding, central de ajuda, certificações, 1.000 GB de ativos | idem · alta |
| Plus | **Detecção de conflito de canal**, plano de negócio do parceiro, **qualificação automática de nível** (novo), autofaturamento e pagamento automático, gestores ilimitados | idem · alta |
| Premier | SSO, conteúdo co-branded, gerente de sucesso dedicado | idem · alta |
| Avaliações | 5,0 com 4 avaliações (amostra pequena demais para concluir) | Capterra/GetApp · alta |
| Ponto forte | Cabe no tamanho da Save (25 a 50 parceiros) e tem os módulos certos | — |
| Ponto fraco | Conflito e nível automático só no Plus, sem preço público; base pequena de clientes | — |

### A10. Apps de PRM para HubSpot

| App | O que faz | Preço | Fonte · confiança |
|---|---|---|---|
| **Partner Deals Portal (AppoByte)** | Portal nativo do HubSpot para registro de deal. O parceiro não precisa de assento nem de HubSpot; o admin escolhe os campos obrigatórios; o envio cai direto nos Deals do HubSpot | Assinatura própria; requer HubSpot Starter ou Professional; 100+ instalações | https://ecosystem.hubspot.com/marketplace/listing/partner-deal-portal-263089 · média |
| **PartnerPortal.io** | Registro de lead com **trava e aprovação**, **detecção de duplicidade**, fases do lead, comissão e relatório de pagamento, níveis por recompensa e por grupo com condições flexíveis, LMS com quiz e certificação, sincronia de lead e importação de deals do HubSpot (escolhe o pipeline) | Free (5 parceiros); Professional a US$ 249/mês (100 parceiros); Enterprise a US$ 399/mês (ilimitado); "todo plano tem todo recurso" | https://www.partnerportal.io/pricing · alta |
| **Introw** | PRM "nativo" para HubSpot: registro de deal e lead, formulários sem código, planos de comissão, níveis e portal. O parceiro pode registrar pelo próprio HubSpot (Partner Connect Card). Tem IA para conflito de canal, agente de suporte ao parceiro 24/7 e coaching de deal, além de integração com Claude e MCP (plano Scale). MDF, LMS e afiliado são adicionais | Starter grátis (1 parceiro); Pro, Scale e Enterprise sob consulta, por número de parceiros | https://www.introw.com/pricing; support.introw.io · alta (recursos) / [viés fornecedor] no blog |
| **Impartner, Channeltivity, Mindmatrix, PartnerStack, Allbound** | Integrações certificadas, descritas acima | — | HubSpot Marketplace · alta |

**O HubSpot não tem PRM nativo para os próprios clientes.** O recurso "shared deals" da base de conhecimento do HubSpot serve ao programa de parceiros **do próprio HubSpot**: agências que revendem HubSpot registram negócios com um vendedor do HubSpot. Não serve a uma empresa que queira gerir os próprios parceiros. Fonte: https://knowledge.hubspot.com/partner-tools/create-shared-partner-deals · confiança média (leitura do analista sobre o texto, que fala em "HubSpot sales representative").

### A11. Referências brasileiras (o que o contador já conhece)

| Programa | Estrutura | Fonte · confiança |
|---|---|---|
| **Conta Azul (Conta Azul Mais e Portal da Parceria)** | Aspirante → Bronze → Prata → Ouro → Platina → Diamante. Entrada no Bronze com 3 licenças CA Pro (ou 15 de Automação Fiscal) ativas. Desconto em licença de 25% (Prata) a 50% (Diamante); suporte por telefone e atendimento dedicado a partir do Ouro; marketing conjunto no Platina; selo, diretório de parceiros, certificação, Prêmio Constelação, mentoria e visita à sede; envio de empresas que procuram contador. O blog de 2024 descreve pontuação por real faturado: 1 ponto por real no ERP do escritório e 1,2 ponto por real no ERP dos clientes | https://contaazul.com/mais/parceria/ · alta (níveis e descontos); https://contaazul.com/blog/parceiros/programa-de-parceria-conta-azul/ · média (pontos, 2024) |
| **Omie (Conexão Contadores)** | Cinco níveis (Bronze, Prata, Ouro, Platina, Diamante) por faixa de comissão ou pontos. O texto extraído mostra faixas de até 300, de 301 a 700, de 701 a 1.500, de 1.501 a 2.300 e acima de 2.301. O enquadramento depende do uso do software pelos clientes indicados e pelo próprio contador. Há **comissão mensal enquanto o cliente indicado seguir ativo**, troca de comissão por viagem (Omie Club Infinity), cursos (Omie.Educação) e suporte dedicado | omie.com.br/termos-e-condicoes-conexao-contadores (via busca; a leitura direta veio sem as regras); omie.com.br/programa-parceria-contadores · média |
| **Cora** | Ao chegar a **25 indicações ativas**, o contador vira nível Esmeralda e passa a **receber indicações de clientes** da Cora todo mês, além de ganhar pelas próprias indicações | cora.com.br/blog/cora-indica-contabilidades (via busca; a página bloqueou a leitura) · média |
| **Nibo** | Não localizei programa de indicação com comissão publicado | — · lacuna declarada |

**Leitura para a Save:** o contador brasileiro está acostumado a cinco coisas:

1. Nível com nome de metal e selo público.
2. Progressão por **volume ativo**, não por treinamento.
3. **Reciprocidade:** o fornecedor manda cliente para o contador (Conta Azul e Cora).
4. Comissão recorrente enquanto o cliente fica.
5. Reconhecimento e experiência (viagem, prêmio, visita) além do dinheiro.

Nenhum dos três tem registro de oportunidade com prazo de proteção, porque vendem software de baixo valor. A Save vende serviço de alto valor e ciclo longo, e aí o registro faz sentido.

---

## Parte B. Matriz de funcionalidades

Legenda: ● nativo e documentado · ◐ parcial, adicional pago ou só no plano alto · ○ não tem ou não é o foco · ? não confirmado publicamente. **★ = estado da arte** naquela linha.

| Funcionalidade | Impartner | PartnerStack | SF Partner Cloud | Channeltivity | Channelscaler (Allbound) | ZINFI | Mindmatrix | Crossbeam | Kiflo | PartnerPortal.io | Introw | Conta Azul / Omie |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Portal do parceiro com marca | ● | ● | ● | ● | ● | ● | ● | ○ | ● | ● | ● | ● |
| Onboarding com trilha e gatilhos | ● ★ | ● | ◐ | ● | ● | ● | ● ★ | ○ | ● | ◐ | ● | ◐ |
| Registro de oportunidade | ● | ● | ● | ● ★ | ● | ● | ● | ○ | ● | ● | ● | ○ |
| Checagem de duplicidade e conflito | ● | ? | ● ★ | ? | ● | ● | ? | ◐ (sobreposição) | ◐ (Plus) | ● | ● (IA) | ○ |
| Prazo de proteção com expiração automática | ? | ○ | ● | ● ★ | ● | ● | ? | ○ | ? | ● (trava) | ? | ○ |
| Aprovação do ganho declarado pelo parceiro | ● | ● ★ | ● | ● | ● | ● | ● | ○ | ● | ● | ● | ○ |
| Distribuição de lead ao parceiro (aceite ou recusa) | ● | ○ | ● ★ | ● | ● | ● | ◐ | ○ | ◐ | ◐ | ? | ◐ (Conta Azul e Cora mandam cliente) |
| Cálculo de comissão | ● | ● ★ | ◐ (PEM) | ◐ | ● | ● | ◐ | ○ | ● | ● | ● | ● |
| Extrato e pagamento ao parceiro | ◐ | ● ★ | ◐ | ○ | ● | ● | ○ | ○ | ◐ (Plus) | ● | ● | ● |
| Nível (tier) automático por regra | ● ★ | ◐ (grupos) | ● | ● | ● | ● | ● | ○ | ◐ (Plus) | ● | ● | ● ★ (volume ativo) |
| Scorecard e saúde do parceiro | ● ★ | ◐ | ● | ● | ● | ● | ● (engajamento) | ○ | ◐ | ◐ | ● | ○ |
| Plano de negócio conjunto (JBP) | ● ★ | ○ | ◐ | ? | ● | ● | ? | ○ | ◐ (Plus) | ○ | ● (metas) | ○ |
| LMS e certificação | ● | ◐ | ● (Tracks) | ● | ● | ● | ● ★ | ○ | ● | ● | ◐ (adicional) | ● |
| Biblioteca de conteúdo co-branded | ● | ◐ | ◐ | ● | ● | ● | ● ★ | ○ | ◐ (Premier) | ● | ◐ | ● |
| MDF (fundos de marketing) | ● | ○ | ● | ● | ● | ● | ● | ○ | ○ | ○ | ◐ | ○ |
| Account mapping (cruzamento de carteiras) | ◐ | ○ | ○ | ○ | ○ | ○ | ○ | ● ★ | ○ | ○ | ○ | ○ |
| Atribuição de influência (não só originação) | ● | ● ★ (multitoque) | ● | ◐ | ● | ● | ◐ | ◐ (Supernode) | ○ | ○ | ● | ○ |
| IA (agente de suporte ao parceiro, conflito, coaching) | ● | ◐ | ● (Agentforce) | ? | ● | ● | ◐ (BridgeAI) | ◐ | ○ | ○ | ● ★ | ○ |
| Sincronia com HubSpot | ● | ● | ○ | ● ★ (edição dedicada) | ● | ● | ● | ● | ● | ● | ● ★ (nativo) | n/a |
| Preço de entrada público | US$ 25 mil/ano | não | US$ 25/membro/mês | não | cerca de US$ 3.495/mês | não | cerca de US$ 499/mês | US$ 4.800/ano | US$ 399/mês | US$ 249/mês | grátis ou sob consulta | grátis para o contador |

Fontes: as das tabelas A1 a A11. Célula "?" quer dizer que não encontrei evidência pública, não que o recurso não exista.

---

## Parte C. As funcionalidades que mais pesam em resultado de canal

Há pouca evidência independente sobre qual recurso de PRM gera resultado; a maior parte vem de fornecedor. Por isso a lista combina dado externo (com o viés marcado) e **dado da própria Save**, que é o mais confiável para o desenho.

| # | Funcionalidade | Evidência (dado · fonte · data) | Confiança |
|---|---|---|---|
| 1 | **Registro de oportunidade com aprovação** | Channelscaler Scaler Index (mais de 30 mil parceiros): a taxa de fechamento de negócios de parceiro quase triplicou em 3 anos, e o valor dos registros fechados cresceu mais de 8 vezes · Channel Dive, 13/08/2026. A Forrester (2018, relatório pago) chama o registro de "elemento crucial", sobretudo por reduzir conflito. Canalys 2014 (130 parceiros): o registro é o 2º benefício mais valorizado, atrás do rebate | média [viés fornecedor] |
| 2 | **Prazo de proteção calibrado pelo ciclo real** | Save: mediana de 35 dias até o ganho, p75 de 69 e p90 de 162; **80,8% dos ganhos em até 90 dias** (HubSpot da Save, em `skills/depto-operacoes-canal/references/especialistas/registro-conflito-canal.md`). Mercado: janela comum de 60 a 120 dias, com 90 dias como padrão (Anchore, Morphisec; baramundi com 3 meses mais 3) e 180 dias em ciclos longos (Isovalent, Quadrant) · consulta 26/10/2026 | alta (Save) · média (mercado) |
| 3 | **Checagem de conflito na entrada, antes de aprovar** | Salesforce: carimbo de hora, checagem de duplicidade e bloqueio de outro parceiro ou da venda direta (Trailhead). Kiflo e Introw vendem "conflito de canal" como recurso premium. Pesquisa GCLC (2015): manter registros pesa administrativamente para o parceiro | alta (o recurso existe) · baixa (efeito medido) |
| 4 | **Exigência de atividade para manter a proteção** | Quadrant encerra no dia 90 sem reunião com o cliente; Esri Indonésia encerra sem atualização a cada 2 semanas; Anchore cancela com aviso de 5 dias úteis se o parceiro não trabalha o negócio · consulta 26/10/2026 | média |
| 5 | **SLA de resposta ao registro** | Prática comum: aprovar ou recusar em 2 a 5 dias úteis (getreditus, glossário). Pedowitz: um ISV reduziu em 38% o tempo até o 1º negócio com trilhas por papel e SLA de registro (caso único) | baixa a média |
| 6 | **Ativação rápida (tempo até o 1º e o 2º negócio)** | Forrester (blog): quanto mais rápido os dois primeiros negócios, maior a chance de o parceiro ficar ativo no longo prazo. Unifyr 2026 (via Introw): ativação de 30 a 50% em programa gerido, contra menos de 20% sem gestão; quem fecha o 1º negócio em 90 dias tem 3 a 4 vezes mais chance de seguir ativo em 1 ano | média (Forrester) · baixa (secundária) |
| 7 | **Extrato de comissão visível e no prazo** | A PartnerStack pôs o pagamento automático e o saque no painel no centro do produto. A Impartner afirma que 78% das equipes suspeitam pagar até 20% a mais a parceiros [viés fornecedor]. Na Save, a comissão é sobre o **recebido**, e o PER leva até 360 dias: saber "onde está meu dinheiro" é o que segura o indicador | média |
| 8 | **Nível automático por regra** | Impartner Program Compliance Manager (redução de tempo administrativo, segundo depoimento). Conta Azul e Omie: nível por volume ativo com benefício crescente | média |
| 9 | **Benefício de nível barato e valorizado** | IGEL: validade do registro de 90 dias, 120 para Gold e Platinum. Conta Azul: atendimento dedicado no Ouro e marketing conjunto no Platina. A Save já propôs 120 dias para Masters e 90 para indicadores `[decisão do Luis]` | média |
| 10 | **Reciprocidade: mandar cliente ao parceiro** | Cora: com 25 indicações ativas, o contador passa a receber clientes. Conta Azul: "acesso a empresas que buscam contabilidade". Salesforce: Lead Inbox | média |
| 11 | **Scorecard de saúde do parceiro** | Impartner, Mindmatrix (pontuação de engajamento) e Salesforce (scorecards) têm o recurso; não há dado de efeito independente | baixa (efeito) |
| 12 | **Plano de negócio conjunto (JBP e QBR) para os Masters** | Impartner (plano com metas, notas e anexos). A KPMG atribui parte do crescimento de Advisory no FY2025 a alianças com dono executivo e plano conjunto (CPA Practice Advisor, 17/12/2025) | média |
| 13 | **Capacitação por tese com certificação** | Todos os líderes têm LMS; Conta Azul e Omie usam certificação como porta de nível. O efeito em receita não é medido publicamente | baixa (efeito) |
| 14 | **Biblioteca de kits por tese e produto** | Mindmatrix e Impartner (co-branding). Para o indicador, o kit certo vale mais que automação de campanha | baixa |
| 15 | **Pipeline do parceiro visível para ele (status do cliente indicado)** | Impartner: "dar visibilidade do pipeline ao parceiro" é o 2º recurso listado na integração com o HubSpot. Salesforce dá ao parceiro a Opportunity estendida | média |
| 16 | **Atribuição de influência, não só de originação** | PartnerStack (multitoque). Canalys/Omdia (jan/2026): remunerar o parceiro em todo o ciclo do cliente (créditos de co-venda) | média |
| 17 | **Facilidade de registrar (formulário curto, celular, WhatsApp)** | A Introw permite registrar sem sair do CRM do parceiro; a CRMJetty recomenda poucos campos obrigatórios (conta, contato, oportunidade) para checar duplicidade. Microsoft: "facilidade de fazer negócio é o pedido nº 1 dos parceiros" (slide sem data) | baixa a média |
| 18 | **IA como primeiro atendimento ao parceiro** | Introw (agente 24/7) e Salesforce (Agentforce for Partners). Partnership Leaders 2026: 96,5% das organizações de parcerias usam IA (sumário executivo, já no radar de 16/10/2026) | média (adoção) · baixa (efeito) |

---

## Parte D. O que NÃO se aplica a uma consultoria tributária com parceiros indicadores

| Recurso de PRM | Por que não se aplica (ou só em parte) |
|---|---|
| **MDF (fundos de marketing com pedido e comprovação)** | Pressupõe revenda com orçamento de marketing próprio e fabricante que reembolsa campanha. O indicador contábil não faz campanha paga, e o Master recebe kit pronto. Além disso, a publicidade de serviço tributário passa pelas regras do Jurídico (OAB, CONAR). Substituto: kit por tese e campanha do Marketing da Save. |
| **CPQ, tabela de preço por nível, autocotação e pedido de desconto (deal desk)** | O parceiro não cota nem fecha preço: o honorário é de êxito e definido pela Save depois do diagnóstico. Deixar o parceiro cotar viola a regra "nunca prometer valor". |
| **Rebates, ship-and-debit, dados de ponto de venda (POS), Channel Data Management** | É o modelo de fabricante com distribuidor e estoque. Na Save não há estoque nem revenda. |
| **Marketplaces de hiperescala (AWS, Azure)** | Irrelevante para serviço tributário brasileiro. |
| **Afiliado com link e cookie, rede de recrutamento (PartnerStack Network)** | A venda não acontece por clique: a indicação é relacional e depende de diagnóstico. A atribuição por cookie não mede nada aqui. |
| **Formulários fiscais W-9/W-8BEN, pagamento global em dólar** | O pagamento é em real, com nota fiscal do parceiro PJ e retenções (base de Operações de Canal, D64). Exige um motor brasileiro (NF, IRRF e retenções, base no recebido). |
| **Comissão disparada no "Closed Won"** | Na Save, a comissão nasce do **honorário recebido**, que pode chegar meses depois do ganho (PER de até 360 dias, compensação). O gatilho certo é o recebimento, com clawback. |
| **Account mapping tipo Crossbeam** | O escritório contábil não tem a carteira em CRM. O equivalente brasileiro é cruzar a **lista de CNPJs** do parceiro com o HubSpot e a Receita, o que a área de Dados já faz, sem plataforma. |
| **Through-channel marketing automation (o parceiro dispara e-mail com a marca dele)** | Traz risco de promessa e de LGPD (a base é do contador). Só com texto auditado pelo `auditar_texto.py`, e não em escala na v1. |
| **Programas com milhares de parceiros (segmentação por região, idioma, distribuidor)** | A Save tem cerca de 36 parceiros. A complexidade dos líderes (Impartner, ZINFI) é custo sem retorno nesse tamanho. |
| **Treinamento como requisito de nível (modelo Microsoft e Cisco)** | Os programas que o contador conhece (Conta Azul, Omie) sobem de nível por **volume ativo**. A certificação serve de porta para produto complexo (ex.: Gestão de Passivo), não de degrau geral. |

---

## Parte E. Comprar x construir

### E1. Restrições da casa que decidem a conta

1. **O HubSpot é só leitura para a Área Partners** (CLAUDE.md, regra 3). Todo PRM comprado (Channeltivity, Impartner, Kiflo, PartnerPortal.io, Partner Deals Portal, Introw) **escreve no HubSpot**: cria deals, contatos ou campos. A Channeltivity, por exemplo, exige criar uma caixa de seleção no objeto Deal. Comprar exige que o dono do CRM autorize uma integração com escrita. Sem isso, o PRM comprado vira uma ilha.
2. **LGPD:** o dado de cliente fica no Mac, e os contatos de sócios ficam num arquivo com permissão 600. Um PRM SaaS guarda CNPJ, contato e valor do cliente no servidor do fornecedor, nos EUA na maioria dos casos. Isso exige parecer de Jurídico e TI e contrato de operador.
3. **Comissão sobre o recebido, com retenções e NF,** não vem pronta em nenhum dos produtos: todos calculam sobre o ganho ou a assinatura. A regra de comissão por Master (D64) e os 10% do líquido Save dos produtos 2027 (D78/D97) teriam de ficar fora do PRM de qualquer jeito.
4. **Tamanho:** cerca de 36 parceiros. Os produtos de empresa cobram por parceiro ativo, com piso alto.
5. **Já existe painel interno** (Central Partners) com dados do HubSpot, caixa de entrada, tela de Gestão e cálculo de métricas. A proposta de 13/10/2026 previa o PRM em 4 fases sobre ele.

### E2. Opção pedida pelo Luis: construir na Azure, no tenant Microsoft da Save

**Pilha:** Static Web Apps (front) · Azure Functions (API e leitura do HubSpot) · Azure SQL Database no nível gratuito serverless (dados do PRM) · login do parceiro externo por Entra ID B2B (convidado no tenant da Save) ou External ID (tenant externo) · região Brazil South.

**O que a documentação oficial diz (consulta em 26/10/2026):**

| Ponto | Free | Standard | Fonte · confiança |
|---|---|---|---|
| Autenticação com provedor personalizado (Entra ID do tenant da Save, External ID ou qualquer OIDC) | **Não**: só os provedores pré-configurados | **Sim**: "Custom authentication is only available in the Azure Static Web Apps Standard plan" | https://learn.microsoft.com/en-us/azure/static-web-apps/authentication-custom (atualizado em 30/09/2026); https://learn.microsoft.com/en-us/azure/static-web-apps/plans · alta |
| Usuários com papel personalizado **por convite** | **25 por app** | **25 por app** (o mesmo limite) | https://learn.microsoft.com/en-us/azure/static-web-apps/quotas (atualizado em 28/09/2026) · alta |
| Papéis atribuídos **por função** (a API consulta o banco e devolve o papel no login) | Indisponível | **Ilimitado**; exige autenticação personalizada; quando ligado, os convites são ignorados | idem · alta |
| Functions | Só "gerenciadas": **apenas gatilho HTTP**, sem identidade gerenciada e sem referência ao Key Vault | Gerenciadas ou **"traga sua própria Function App"** (todos os gatilhos, incluindo o temporizador, identidade gerenciada e Key Vault) | https://learn.microsoft.com/en-us/azure/static-web-apps/apis-functions · alta |
| SLA, endpoint privado, restrição por IP | Sem SLA; sem endpoint privado | SLA; 1 endpoint privado; 25 faixas de IP | plans e quotas · alta |
| Banda | 100 GB/mês; acima disso o site para | 100 GB/mês; excedente a US$ 0,20/GB | quotas · alta |
| Preço do Standard | — | A página oficial de preço não exibiu o valor na leitura automática. O valor de lista conhecido é **US$ 9 por app por mês** | azure.microsoft.com/pricing/details/app-service/static · **média** (confirmar na calculadora) |

**Consequência para o desenho:** com cerca de 36 parceiros mais o time, o limite de 25 convites estoura. Por isso o portal precisa do **plano Standard**, com autenticação personalizada e papel atribuído por função lendo a tabela de parceiros no SQL. Pelo mesmo motivo, a leitura agendada do HubSpot precisa de uma Function App própria (gatilho de temporizador e token do HubSpot no Key Vault), o que também só o Standard permite ligar ao site.

**Login do parceiro externo (External ID e B2B):**
- O External ID cobra por usuário ativo no mês (MAU). Os **primeiros 50 mil MAU são gratuitos**. A regra vale também para **convidados B2B** no tenant da Save (UserType = Guest). Os adicionais (SMS como segundo fator, Go-Local) não têm faixa gratuita · https://learn.microsoft.com/en-us/entra/external-id/external-identities-pricing (atualizado em 19/06/2026); https://learn.microsoft.com/en-us/entra/external-id/customers/faq-customers · alta.
- **Acima de 50 mil MAU:** a API pública de preços da Azure (prices.azure.com, consultada em 26/10/2026) mostra o medidor "Basic Monthly Active Users" a **US$ 0,03 por MAU** a partir de 50.000. Mostra também um medidor "Core Monthly Active Users" a US$ 0,01625, cuja aplicação não ficou clara. A documentação remete o valor a aka.ms/ExternalIDPricing, sem citar número · média. Com 36 parceiros, a Save fica três ordens de grandeza abaixo da faixa gratuita: o custo de login é zero.
- SMS como segundo fator no External ID custa de US$ 0,03 a 0,35 por envio, conforme o país (mesma API) · média. Prefira o aplicativo autenticador ou o código por e-mail.
- **Residência do dado de identidade:** o Go-Local só existe na Austrália e no Japão (documentação acima). O tenant externo **não** garante que o cadastro de login fique no Brasil · alta. Com **B2B no tenant da Save**, o convidado fica no mesmo diretório que o time, sob as políticas já existentes. Recomendo o B2B para cerca de 36 parceiros e o External ID só se houver cadastro aberto (autoatendimento) no futuro.

**Banco (Azure SQL, nível gratuito):** cada banco tem **100 mil segundos de vCore, 32 GB de dados e 32 GB de backup por mês, enquanto a assinatura existir**, até 10 bancos por assinatura. Ao esgotar o limite, há duas opções: **pausar até o mês seguinte** (o banco fica inacessível) ou **cobrar o excedente** no preço serverless (escolha irreversível). **Não há SLA**, e a Microsoft o recomenda "principalmente para desenvolvimento e prova de conceito". Uma conexão aberta impede a pausa automática · https://learn.microsoft.com/en-us/azure/azure-sql/database/free-offer (atualizado em 21/10/2026) · alta. Para o PRM, use a opção "cobrar o excedente", porque um portal de parceiro que some no dia 25 do mês é pior que alguns dólares. Faça a leitura do HubSpot em lote (não a cada minuto) e programe um alerta quando restarem 10 mil segundos.

**Functions em Brazil South (API pública de preços, 26/10/2026):** no plano Consumption, os primeiros 400 mil GB-s e 1 milhão de execuções por mês são gratuitos. No Flex Consumption, os primeiros 100 mil GB-s e 250 mil execuções são gratuitos · média (leitura do medidor; confirmar na calculadora). O volume de um PRM de 36 parceiros cabe na faixa gratuita.

**Região:** Functions, SQL e Key Vault podem ficar em Brazil South. **Não confirmei que o próprio recurso Static Web Apps aceite Brazil South**: a documentação de funções distribuídas fala em "região inicial" escolhida na criação, e as Functions gerenciadas seguem a região do site. Isso não pesa no LGPD, porque o front é só HTML e JavaScript distribuídos globalmente, sem dado de cliente; o dado fica na Function App própria e no SQL em Brazil South · média (conferir no portal ao criar).

**Custo, prazo e limitação: Azure x Impartner x PartnerStack x app do HubSpot**

| | Construir na Azure (tenant Save) | Impartner | PartnerStack | App do HubSpot (PartnerPortal.io / Partner Deals Portal / Kiflo) |
|---|---|---|---|---|
| **Licença e infra por ano (US$)** | Cerca de **108** (Static Web Apps Standard, a confirmar) + 0 (SQL gratuito, Functions na faixa gratuita, login abaixo de 50 mil MAU) + centavos (Key Vault, Application Insights). Ordem de grandeza: **menos de 500/ano** | **≥ 25.000** de lista; mediana real de **53.352** (Vendr) | Não publicado; estimativa de terceiro de 9.600 a 12.000 mais 3 a 5% da receita de parceiro | PartnerPortal.io: **2.988** (100 parceiros); Kiflo Core: **4.788** (25 parceiros, pago adiantado); Partner Deals Portal: não publicado + HubSpot Starter/Pro |
| **Custo escondido** | Horas de desenvolvimento e manutenção (agentes e TI); quem mantém o código depois | Implantação e administração; recurso extra para um 2º formulário de registro | Taxa sobre a receita do parceiro, cara para honorário de êxito alto | Customização limitada; o motor de comissão sobre o recebido fica fora de qualquer jeito |
| **Prazo até o parceiro usar** | Estimativa do analista, **sem fonte externa**: 6 a 10 semanas para a v1 do portal (registro, status do cliente indicado, extrato só para leitura, nível), **depois** que o núcleo existir no painel interno. Depende do TI da Save (assinatura, registro do app no Entra, convites B2B) | Não publicado; programa enterprise com implantação assistida | Não publicado; rápido para afiliado SaaS, mas o modelo não encaixa | Dias a poucas semanas, se o dono do CRM liberar a escrita |
| **Escrita no HubSpot** | **Não precisa**: as Functions leem o HubSpot com token de leitura; o registro do parceiro fica no SQL e a Daniela leva ao HubSpot pelo fluxo atual | Precisa | Precisa (sincronia de deal e cliente) | Precisa (é o modo de funcionamento) |
| **Onde fica o dado** | Tenant e assinatura da Save, **Brazil South** (SQL e Functions); identidade dos convidados no tenant da Save | Servidor do fornecedor (EUA) | Servidor do fornecedor (Canadá e EUA) | Servidor do fornecedor e HubSpot |
| **Regra da Save (90 + 60 dias, Master 120, comissão sobre recebido, D64, retenções, NF)** | **Exata**, porque é código nosso | Configurável em parte; o recebido e a NF brasileira, não | Não | Não |
| **Limitação principal** | Banco gratuito sem SLA; limite mensal de vCore; se o Static Web Apps cair para Free, perde-se o login corporativo e o papel por função; manutenção nossa; segurança (OWASP, LGPD técnica) por nossa conta | Preço e excesso de recursos para 36 parceiros | Feito para outro negócio | Escrita no HubSpot; produto pequeno e fornecedor frágil |

### E3. Comparativo geral dos caminhos

| Caminho | Custo anual aproximado (US$) | O que resolve | O que limita | Confiança do custo |
|---|---|---|---|---|
| **Impartner** (Emerge) | ≥ 25.000 de lista; mediana real de 53.352 (Vendr) | Programa completo, nível automático, JBP, scorecard | Preço desproporcional a 36 parceiros; 1 formulário de registro de fábrica; implantação; escrita no HubSpot; dado fora do Brasil | alta (piso) |
| **PartnerStack** | não publicado; estimativa de 9.600 a 12.000 mais 3 a 5% da receita de parceiro | Pagamento automático | Feito para SaaS e afiliado; taxa sobre receita | baixa |
| **Salesforce Partner Cloud** | 25 por membro por mês, **mais trocar o CRM** | Tudo na mesma base | Exige migrar do HubSpot; descartado | alta |
| **Channeltivity HubSpot Edition** | não publicado; o TrustRadius cita 1.899 (provavelmente mensal, cerca de 22.800/ano) | Melhor registro com expiração e sincronia com o HubSpot | Escrita no HubSpot; preço de mid-market | baixa |
| **Kiflo Core / Plus** | Core: 4.788/ano (25 parceiros, adiantado); Plus sob consulta | Portal, registro, comissão calculada; conflito e nível no Plus | A comissão não entende "recebido"; escrita no HubSpot | alta (Core) |
| **PartnerPortal.io Professional** | 2.988/ano (100 parceiros, todos os recursos) | Registro com trava, duplicidade, nível, LMS, comissão | Produto pequeno; escrita no HubSpot | alta |
| **Construir no painel interno (fases 1 a 3) + portal externo na Azure (fase 4)** | Menos de 500/ano de infraestrutura, mais as horas do time e dos agentes | Regra exata da Save, dado no tenant da Save, mesma lógica da Central, HubSpot só leitura | Manutenção nossa; banco gratuito sem SLA; depende do TI da Save para o tenant | média (preço do Static Web Apps a confirmar) |

### E4. Recomendação

**Construir.** Primeiro, o núcleo no painel interno, lendo o HubSpot. Depois, o portal externo do parceiro na Azure, no tenant da Save, em vez de comprar um PRM ou um app do HubSpot. Motivos, em ordem:

1. **O que gera resultado (Parte C, itens 1 a 9) é regra, não software:** registro com prazo calibrado, checagem de conflito, atividade mínima, SLA, extrato no prazo e nível automático. A Save já tem a regra desenhada e o dado (80,8% dos ganhos em até 90 dias). Os PRMs vendem um fluxo genérico, e o fluxo da Save é específico: comissão sobre o recebido, PER de 360 dias, Master e indicador.
2. **Nenhum produto calcula comissão sobre o honorário recebido com retenção e NF brasileira.** O extrato, que é a peça mais sensível para o parceiro, ficaria fora do PRM comprado de qualquer forma.
3. **Comprar não elimina a dependência do dono do CRM, e a Azure elimina:** todo app escreve no HubSpot, enquanto a pilha na Azure só lê. O registro do parceiro fica no SQL e entra no HubSpot pelo fluxo que a Daniela já usa.
4. **Custo e LGPD:** menos de US$ 500/ano de infraestrutura, contra US$ 3 a 53 mil/ano das licenças, e o dado fica em Brazil South, no tenant da Save. O custo real é o tempo do time e a manutenção.
5. **Escala:** reavaliar a compra se o programa passar de cerca de 100 parceiros ativos, ou se o time não conseguir manter o código. Nesse caso, PartnerPortal.io ou Kiflo são as opções baratas, desde que a escrita no HubSpot seja liberada.

**Condições para a opção Azure funcionar:** plano Standard do Static Web Apps (autenticação corporativa e papéis por função), Function App própria em Brazil South com o token de leitura do HubSpot no Key Vault, banco gratuito com "cobrar o excedente" e alerta de consumo, login por B2B no tenant da Save com MFA por aplicativo, e revisão de segurança pelo TI antes de abrir para o primeiro Master.

**O que copiar dos líderes ao construir:**
- Da **Channeltivity:** status de registro com etapas abertas e fechadas, etapa padrão de entrada, expiração automática e etapa de destino do vencido.
- Da **Salesforce:** carimbo de hora no registro e checagem de duplicidade por CNPJ. No Brasil, o CNPJ raiz resolve o problema "Acme Corp × Acme Corporation".
- Da **PartnerStack:** o ganho declarado pelo parceiro fica pendente até a aprovação; o extrato tem estados (previsto → recebido pela Save → liberado → pago).
- Da **Impartner:** nível calculado por regra, com barra de progresso até o próximo nível, e plano de negócio do Master com metas e notas.
- Da **Mindmatrix:** pontuação de engajamento (registros, reuniões, documentos entregues) como sinal de saúde.
- Da **Conta Azul e da Cora:** nível por **volume ativo**, com nome reconhecível, selo e **reciprocidade** (a Save indica clientes ao escritório parceiro, ex.: empresas do Lucro Real sem contador adequado), além de benefícios não financeiros.
- Da **Introw:** IA como primeiro atendimento ao parceiro ("onde está meu cliente?", "quanto vou receber?"), com a regra da casa de que o agente rascunha e a pessoa envia.

**Decisões que sobem ao Luis (alçada):**
- A validade por nível (120 dias para Masters, 90 para indicadores), já pendente, e o conflito com os 180 dias do material jurídico.
- Autorizar o TI da Save a criar a assinatura e os recursos na Azure (Static Web Apps Standard, Function App, SQL, Key Vault) e a convidar parceiros como B2B no tenant.
- O parecer LGPD para guardar registros de oportunidade (CNPJ e contato do cliente indicado) no SQL da Azure, que é diferente da regra atual "dado de cliente fica no Mac".

---

## Fontes principais (consulta em 26/10/2026)

- Impartner no HubSpot Marketplace: https://ecosystem.hubspot.com/marketplace/listing/impartner-prm
- Impartner no AWS Marketplace (avaliações): https://aws.amazon.com/marketplace/reviews/reviews-list/prodview-l75vriw7iffmw?page=46
- Vendr, Impartner: https://www.vendr.com/marketplace/impartner-software
- Forrester TEI da Impartner [viés fornecedor]: https://impartner.com/resources/blog/impartner-forrester-tei-study
- Impartner no G2 Summer 2026: https://impartner.com/resources/blog/impartner-recognized-as-a-leader-in-g2-summer-2026-enterprise-grid-for-partner-relationship-management
- G2 Summer 2026 (via ZINFI): https://www.martechcube.com/g2-names-zinfi-a-prm-leader-in-summer-2026-grid-report/
- PartnerStack, deal submission: https://support.partnerstack.com/hc/en-us/articles/6021325335699
- PartnerStack Research Lab: https://partnerstack.com/resources/research-lab/charts/most-network-partners-have-a-median-time-of-2-days-to-joining-their-first-partnership
- PartnerStack, estimativa de preço (terceiro): https://dupple.com/reviews/partnerstack
- Salesforce Partner Cloud, preço: https://www.salesforce.com/sales/partner-relationship-management/pricing/
- Salesforce Trailhead, PRM: https://trailhead.salesforce.com/content/learn/modules/partner-relationship-management/accelerate-channel-sales
- Channeltivity, preço: https://www.channeltivity.com/pricing · TrustRadius: https://www.trustradius.com/products/channeltivity
- Channeltivity, HubSpot e registro: https://help.channeltivity.com/support/solutions/articles/3000092116 · https://help.channeltivity.com/support/solutions/articles/3000020045 · https://help.channeltivity.com/solution/articles/3000069985-registration-status-workflow-
- Allbound/Channelscaler: https://www.allbound.com/resources/exciting-news-channel-mechanics-has-joined-allbound · https://www.capterra.com/p/141976/Allbound/
- Channelscaler Scaler Index: https://www.channeldive.com/news/channelscaler-unveils-partner-program-performance-metrics/827862/ (13/08/2026)
- ZINFI: https://www.zinfi.com/products/partner-relationship-management/overview · rfp.wiki (estimativas)
- Mindmatrix Bridge: https://ecosystem.hubspot.com/marketplace/listing/bridge-5-0-powered-by-mindmatrix · https://www.g2.com/products/mindmatrix-prm/pricing · https://www.trustradius.com/products/mindmatrix
- Crossbeam: https://www.crossbeam.com/pricing · https://crossbeam.com/use-cases/account-mapping · https://orrick.com/news/2024/06/crossbeam-and-reveal-join-forces-to-disrupt-go-to-market-strategy
- Kiflo: https://www.kiflo.com/pricing
- PartnerPortal.io: https://www.partnerportal.io/pricing
- Introw: https://www.introw.com/pricing · https://support.introw.io/en/articles/15039830-partner-connect-a-2-way-crm-integration-with-hubspot
- Partner Deals Portal: https://ecosystem.hubspot.com/marketplace/listing/partner-deal-portal-263089
- HubSpot shared deals (programa do próprio HubSpot): https://knowledge.hubspot.com/partner-tools/create-shared-partner-deals
- Conta Azul: https://contaazul.com/mais/parceria/ · https://contaazul.com/blog/parceiros/programa-de-parceria-conta-azul/
- Omie: https://www.omie.com.br/termos-e-condicoes-conexao-contadores/ · https://www.omie.com.br/programa-parceria-contadores/
- Cora: https://www.cora.com.br/blog/cora-indica-contabilidades/
- Prazos de proteção: https://anchore.com/wp-content/uploads/2025/03/Anchore-Deal-Registration-Form-v.Feb-2025.pdf · https://www.baramundi.com/fileadmin/Partner/2026-04-08_Partner-Project-Registration_EN.pdf · https://isovalent.com/dealreg · https://wiki.quadrantsec.com/deal-registration · https://getreditus.com/resources/glossary/deal-registration
- Canalys 2014: https://www.canalys.com/newsroom/partner-programs-prove-key-channel-relationships · Forrester (2018, pago): https://www.forrester.com/report/building-an-effective-deal-registration-program/RES172205
- Ativação (fonte secundária, Unifyr via Introw): https://www.introw.io/blog/partner-activation · Pedowitz: https://www.pedowitzgroup.com/measure-partner-enablement-success
- **Azure:** Static Web Apps, planos: https://learn.microsoft.com/en-us/azure/static-web-apps/plans · cotas: https://learn.microsoft.com/en-us/azure/static-web-apps/quotas · autenticação personalizada: https://learn.microsoft.com/en-us/azure/static-web-apps/authentication-custom · APIs com Functions: https://learn.microsoft.com/en-us/azure/static-web-apps/apis-functions · preço: https://azure.microsoft.com/en-us/pricing/details/app-service/static/
- **Entra External ID:** preço e cobrança: https://learn.microsoft.com/en-us/entra/external-id/external-identities-pricing · FAQ: https://learn.microsoft.com/en-us/entra/external-id/customers/faq-customers · medidores: https://prices.azure.com/api/retail/prices (filtro "External ID", consulta em 26/10/2026)
- **Azure SQL, nível gratuito:** https://learn.microsoft.com/en-us/azure/azure-sql/database/free-offer
- Dados internos: `skills/depto-operacoes-canal/references/especialistas/registro-conflito-canal.md` (ciclo de ganho da Save) e `skills/depto-partner-success/references/radar-mercado.md` (itens 2.3 a 2.7, consulta de 16/10/2026).

## Lacunas declaradas

- Sem preço oficial de PartnerStack, Channeltivity, ZINFI, Introw (planos pagos), Kiflo Plus e Partner Deals Portal.
- Preço do Static Web Apps Standard não exibido na leitura automática da página oficial (valor de lista conhecido: US$ 9/app/mês; confirmar na calculadora). O medidor "Core MAU" do External ID (US$ 0,01625) não foi explicado na documentação.
- Não confirmei que o recurso Static Web Apps aceite Brazil South como região; Functions e SQL aceitam.
- O prazo de 6 a 10 semanas da opção Azure é estimativa do analista, sem fonte externa.
- Não há estudo independente que meça o efeito de cada recurso de PRM em receita; os números de efeito são de fornecedor ou de fonte secundária.
- As regras completas de Omie e Conta Azul (percentual de comissão, validade da indicação) não estão nas páginas públicas lidas, e não localizei programa de indicação da Nibo.
- Não vi as telas internas dos produtos (sem demonstração, por regra). As descrições de tela vêm de documentação e listagens.
