# Manual Oficial dos Agentes · Área Partners

> Versão 2.0, 23/10/2026. Substitui o Manual dos Agentes v1.0 (13/10/2026). Uso interno. O conteúdo das áreas é lido das próprias skills (`infra/manual_oficial.py`), então este manual se regera quando uma área muda.

## 1. Para que serve este manual
Este é o documento oficial da operação de agentes de IA da Área Partners da Save Co. Ele diz:
- **as regras** que todo agente segue;
- **os fluxos** por onde passa cada pedido, demanda e originação;
- **quem é responsável** por cada área, humano e agente;
- **o que cada área e cada especialista entrega**;
- **onde a entrega fica** (OneDrive, repositório, e-mail ou painel).

A operação tem **25 áreas e 130 especialistas sêniores**, todos no padrão da D93 (nota 100 no auditor em 23/10/2026). Os agentes preparam; quem decide e envia são as pessoas.

## 2. Regras da casa (valem para todos os agentes)
| # | Regra | Fonte |
|---|---|---|
| 1 | Nada é enviado, assinado ou gravado em sistema sem aprovação humana. Os agentes entregam rascunho. | CLAUDE.md §3 |
| 2 | HubSpot e GLPI: só leitura e rascunho. Nunca ler `.env`. | CLAUDE.md §3 |
| 3 | Nunca prometer valor, prazo ou êxito. Todo material externo passa pelo auditor de promessas e pelas áreas envolvidas, e o Luis vê um exemplo antes da execução em massa. | CLAUDE.md §2 |
| 4 | Alíquota zero sai sempre via PER, nunca DCOMP. | D14 |
| 5 | Produtos em validação (Crédito Internacional, Maquila, captação, home equity, turnkey) seguem a trava do G2: sem taxa, prazo, fee ou condição para fora. Exceção: one-page com 7% a 10% como exemplo, definido pelo fundo (D88). | D77, D88 |
| 6 | Produto em validação é desenvolvido por inteiro na base interna, porque já há oportunidades em andamento. A trava vale só para o que se diz ao cliente. | D93 |
| 7 | O dado que falta não trava a construção: segue-se com o que existe, marca-se [pendente: quem fornece] e nunca se inventa o dado. | D97 |
| 8 | LGPD: dado de cliente fica no Mac. Dados de sócios e contatos só em `dados-publicos/receita/prospects-contatos.json`. Não se busca celular pessoal fora do cadastro público. | CLAUDE.md §3 |
| 9 | Não citar cliente pelo nome em material. Casos entram anonimizados. | Regra do Luis |
| 10 | Venda gerencial e conta escrow: só presencial, com o Junior. Os agentes não descrevem a mecânica. | D82 |
| 11 | Visual: Design System Save v0.5 (IBM Plex, ouro como única cor, modo claro para cliente). | Regra do Luis |
| 12 | Toda norma é conferida no texto oficial, com data. O que não foi conferido fica marcado [não confirmado]. | D93 |

## 3. Fluxo único: como um pedido anda
Todo pedido, demanda ou originação segue o mesmo caminho (`infra/fluxo-unico.md`).
1. **Entrada.** Pedido (painel ou e-mail [AGENTES]), demanda (WhatsApp dos Masters e das caixas do time) ou originação (indicação de empresa).
2. **Porteiro.** Antes de produzir, confere se o pedido já existe, é continuação, está travado ou é novo (`infra/ja_existe.py`). Se for repetido, devolve ao Luis o que já existe.
3. **Triagem.** O Gabinete ou a Central identifica o produto (P1 a P18) e a onda da esteira e decide as áreas e a profundidade: consulta rápida, parecer de uma área, comitê de áreas ou Conselho.
4. **Áreas.** O gerente da área distribui ao especialista certo, que trabalha pelo seu arquivo (método, normas, regras da casa).
5. **Revisão do gerente.** Até 2 rodadas. A revisão aprovada registra ajustes concretos ou o motivo de não haver ajuste (`infra/protocolo-gerente.md`).
6. **Devolução em 3 blocos.** O que você pediu; o que você também precisa; o que falta e quem fornece (`infra/padrao-entrega.md`).
7. **Se a área não resolve com os dados,** o especialista escreve o chamado ideal e ele vai para aprovação no painel antes de abrir no GLPI. Contrato vai ao time de Contratos; repasse vai ao Financeiro.

**Quando sobe de nível:** 3 ou mais áreas envolvidas, mudança de regra, mais de R$ 1 mi de crédito com decisão ou produto em validação.

## 4. Portfólio e esteira
A esteira tem três movimentos: **Destravar caixa → Proteger e controlar → Crescer** (D1). O dono da esteira e do mapa da conta é Contas e Soluções.

| Produto | Estado | Dono humano | Área de agentes |
|---|---|---|---|
| Recuperação tributária e recorrência (P1, P2) | Pronto | Time técnico | Tributário, Recuperador, Revisor, Pós-venda |
| Crédito presumido e Funrural (P3) | Pronto (Funrural como passivo, D86) | Time técnico | Tributário, Jurídico |
| Gestão de Contas, antecipação e FIDC (P4, P9, P13) | Pronto | Junior (Save Invest) | Save Invest (D92) |
| Gestão de Passivo (P5) | Pronto | Jurídico | Jurídico, Tributário |
| Passivo bancário (P6) | Em validação | A definir | Internacional |
| Produtos jurídicos (P7) | Pronto | Jurídico | Jurídico |
| Planejamento e reforma (P8) | Pronto | Time técnico | Tributário |
| Estruturação patrimonial (P10) | Pronto | Jurídico | Jurídico |
| Crédito Internacional (P12) | Em validação (G2) | João Mattos | Internacional |
| Home equity (P14) | Em validação | João Mattos | Internacional |
| Maquila e Paraguai (P15) | Em validação | João Mattos | Internacional |
| Captação de capital (P16) | Em validação | João Mattos | Internacional |
| Internacionalização turnkey (P17) | Em validação | João Mattos | Internacional |
| Tax internacional e comércio exterior (P18) | Pronto | Paulo e João Mattos | Internacional |

## 5. Padrão sênior dos especialistas
Cada especialista tem um arquivo próprio (`skills/<área>/references/especialistas/`) com o **perfil** (trajetória equivalente, formação, frameworks, como pensa) e **10 seções**: entrega única, domínio técnico, base normativa com artigo e data, regras da casa, método, perguntas de diagnóstico, armadilhas, casos de referência, fronteiras e atualização (`infra/padrao-senior.md`). O dono do padrão é o Arquiteto de Agentes, e a nota sai de `infra/auditar_senioridade.py`.

A nota mede se o especialista está completo. A qualidade se fecha com a validação humana (D94: Jurídico para Passivo e Patrimonial até 07/11; time técnico para Alíquota Zero e Reforma), com o radar semanal e com a Qualidade medindo os acertos.

## 6. As áreas: missão, responsáveis, especialistas e onde entregam
Cada área tem um gerente, que distribui e revisa, e especialistas sêniores com uma entrega única. As perguntas que só as pessoas respondem ficam em `references/perguntas-ao-dono.md` de cada área.

### Bloco: Orquestração

**6.1 Gabinete** (`gabinete`)

- **Missão:** Porta de entrada única do Luis: confere se o pedido já existe, decide quais áreas entram e com que profundidade e consolida um parecer único.
- **Dono humano:** Luis
- **Onde entrega:** Na conversa; parecer consolidado em 3 blocos
- **Especialistas (2):**

| Especialista | Entrega única |
|---|---|
| Consolidador do Gabinete | O parecer consolidado do Gabinete: um documento em gabinete/pedidos/AAAA-MM-DD-<tema>.md com (1) a entrega principal pronta para usar, (2) o que cada área validou ou apontou (✅ ⚠️ ❌), (3) conflitos entre áreas e a resolução… |
| Roteador do Gabinete | A Ficha de Rota (Portão 0) de cada pedido do Luis: classificação do porteiro, tipo de entrega, nível (1 a 4) com o motivo e o limite que o justifica, áreas em ordem com por que entram e o que entregam, quem fica de fora e por… |

**6.2 Central de Agentes** (`central-agentes`)

- **Missão:** Recebe os pedidos do time pelo painel e pelo e-mail [AGENTES], tria, aciona a área certa e responde.
- **Dono humano:** Luis (o time pede)
- **Onde entrega:** E-mail ao solicitante; enquanto o Graph não volta, `04 · Gestão/Central de Agentes/Caixa de saída` (D91)
- **Especialistas (2):**

| Especialista | Entrega única |
|---|---|
| Redator da Resposta em 3 Blocos | O resposta.json de cada pedido, pronto para central.py responder: resumo (2 frases com a conclusão), secoes (o que foi pedido, resultado primeiro), tambem e falta (obrigatórios), conferido (item e resultado, com onde foi… |
| Triador de Pedidos da Central | A triagem de cada pedido da Central: uma linha "o que a pessoa quer · para que · quem responde", o código do catálogo (dado ou deduzido), as áreas acionadas e a ordem, o que falta (com quem fornece), o nível (resolve na… |

**6.3 Conselho Consultivo** (`conselho-partners`)

- **Missão:** Analisa decisões de estratégia, meta, preço e produto com seis conselheiros e um presidente; diz também o que não fazer.
- **Dono humano:** Luis
- **Onde entrega:** Ata em `04 · Gestão/Conselho`; decisões em `conselho/decisoes.md`
- **Especialistas (7):**

| Especialista | Entrega única |
|---|---|
| Conselheiro Comercial & Parcerias | O parecer comercial e de canal do Conselho: efeito de cada ponto da pauta em pipeline, conversão, ativação dos 9 Masters, concentração e experiência do parceiro, com o valor esperado por Master e a ação de conta que move o número. |
| Conselheiro de Estratégia & Crescimento | O parecer de estratégia do Conselho: para cada ponto da pauta, se aproxima da meta (Q4 de R$ 200 mi, D64; meta 2027 da diretoria, D75) ou só ocupa tempo; qual a sequência; o que fazer, o que adiar e o que não fazer, com o… |
| Conselheiro de Finanças & Resultado | O parecer financeiro do Conselho: para cada ponto da pauta, quanto custa, quanto retorna, em quanto tempo e com que confiança, em 3 colunas (contratado, conservador, realizado), com a margem por Master ou por tese quando o… |
| Conselheiro de Operações, Processos & Tecnologia | O parecer operacional do Conselho: onde o fluxo trava, quanto custa a espera, qual é o ponto único de falha, que dado falta na origem e que automação ou regra resolve, com dono, SLA e indicador. |
| Conselheira de Pessoas & Liderança | O parecer de pessoas e liderança do Conselho: efeito de cada ponto da pauta em carga, desenvolvimento e engajamento de Daniela, Geovana e Jenifer e na liderança do Luis, com 1 sugestão de conversa ou de ação concreta por… |
| Presidente do Conselho | A ata do Conselho com recomendação consolidada e decisões para aprovação, no formato de references/formato-ata.md. Só o Presidente: monta o dossiê comum, escolhe quem entra, conduz a Rodada 1 (independente) e a Rodada 2 (só… |
| Conselheiro de Risco, Tributário & Jurídico | O parecer de risco do Conselho: para cada ponto da pauta, o que pode dar errado (fiscal, regulatório, contratual, LGPD, reputação), probabilidade, impacto em R$ ou em consequência, e a mitigação que permite seguir, além da… |

**6.4 Arquiteto de Agentes** (`arquiteto-agentes`)

- **Missão:** Dono do padrão sênior e do auditor; desenha, avalia e evolui os agentes e mede o ROI de IA.
- **Dono humano:** Luis
- **Onde entrega:** `infra/padrao-senior.md`, auditoria semanal e pacote de validação (D94)
- **Especialistas (2):**

| Especialista | Entrega única |
|---|---|
| Guardião do Padrão Sênior | O controle de qualidade do padrão sênior em toda a casa: o modelo de especialista (references/modelo-especialista.md), a auditoria semanal (nota do script + leitura qualitativa por amostragem), a fila de aprofundamento, o mapa… |
| Mentor do Método | A condução do Luis pelo método, fase a fase, com o entregável de cada fase em arquivo (ESTADO.md atualizado, mapa de tarefas, ranking, FICHA do agente, base de conhecimento, piloto, resultados-piloto.md, one-pager para a… |

### Bloco: Produtos

**6.5 Tributário & Contábil** (`depto-tributario`)

- **Missão:** Teses de recuperação, alíquota zero via PER, reforma e saldos credores, insumos, exclusões da base, agro e evidência no SPED.
- **Dono humano:** Time técnico (validação humana, D94)
- **Onde entrega:** Pré-análise na conversa ou no pedido; catálogo em `departamentos/tributario/`
- **Especialistas (6):**

| Especialista | Entrega única |
|---|---|
| Agro e Funrural | Diagnóstico Agro da conta, em duas folhas |
| Alíquota Zero e PER | Ficha de aptidão T01 (alíquota zero) por cliente, uma página, que só este especialista assina como pré-análise |
| Exclusões da Base de PIS/COFINS | Ficha de exclusão por tese e por cliente: para cada exclusão aplicável, uma linha com |
| Insumos PIS/COFINS | Matriz de essencialidade e relevância por item de custo, por cliente, que só este especialista monta |
| Reforma Tributária e Saldos Credores | Plano de Transição do Cliente até 31/12/2026 e para 2027, com duas partes |
| SPED e Evidência | Mapa de Evidência por tese: para cada tese do cliente, "o único documento que decide", com |

**6.6 Jurídico** (`depto-juridico`)

- **Missão:** Gestão de Passivo, estruturação patrimonial, prazos e contencioso administrativo e o perímetro do que a Save pode fazer.
- **Dono humano:** Advogado humano (validação até 07/11, D94)
- **Onde entrega:** Pré-análise na conversa ou no pedido
- **Especialistas (4):**

| Especialista | Entrega única |
|---|---|
| Estruturação Patrimonial e Sucessória | Pré-análise de Estruturação Patrimonial e Sucessória da família empresária |
| Gestão de Passivo Tributário | Diagnóstico de Passivo Tributário com rota de regularização, por cliente, em uma página e um anexo |
| Perímetro Regulatório | Parecer de perímetro por produto, peça ou parceria (uma página) |
| Controle de Prazos e Contencioso Administrativo Tributário | Ficha de prazo e defesa, para cada intimação, despacho decisório ou auto de infração |

**6.7 Save Invest** (`depto-save-invest`)

- **Missão:** Gestão de Contas, antecipação de recebíveis e FIDC (D92). O cliente contrata, a Save Invest presta e a Federal Invest financia (D96).
- **Dono humano:** Junior
- **Onde entrega:** Parecer ao Junior; encaminhamento pela esteira
- **Especialistas (7):**

| Especialista | Entrega única |
|---|---|
| Analista de Crédito e Sinais Financeiros | Leitura de aderência financeira: a partir de DRE, balanço, SCR, aging ou, na falta deles, de sinais preliminares (fluxo do e-CAC, Receita, parecer do diagnóstico), diz qual produto da Save Invest resolve a dor do cliente… |
| Antecipação e Recebíveis | Parecer de elegibilidade e custo da antecipação para um cliente: a carteira dele é antecipável, quanto de limite de referência faz sentido pedir, que garantia levar ao comitê e quanto a operação custa comparada ao que ele paga… |
| FIDC e Estruturação | Tese de viabilidade de FIDC para um cliente ou uma cadeia: (1) o FIDC é o veículo certo? (2) qual modelo (proprietário, multicedente, multissacado); (3) business case em faixa (custo fixo × ganho financeiro); (4) desenho… |
| Gerente da Save Invest | A resposta única da Save Invest, revisada: recebe o pedido (oportunidade, dúvida, reunião, varredura, material), decide quais especialistas entram e em que profundidade, revisa pelo checklist e devolve um texto nos 3 blocos,… |
| Gestão de Contas e Cobrança | Diagnóstico de carteira e desenho da régua de Gestão de Contas para um cliente específico. |
| Especialista Regulatório | Mapa de enquadramento e riscos regulatórios de uma operação ou de uma peça: para cada atividade (cobrar, comprar título, conceder limite, estruturar fundo, falar com devedor, usar WhatsApp), diz quem pode fazer, sob qual… |
| Revisor de Linguagem e Promessas | Texto revisado e liberado (ou bloqueado): recebe qualquer rascunho da área (mensagem ao parceiro, roteiro de reunião, one-page, template de WhatsApp para o devedor, e-mail ao cliente) e devolve: (1) o texto corrigido; (2) a… |

**6.8 Produtos Internacionais** (`depto-internacional`)

- **Missão:** Tax internacional e comércio exterior (pronto); Crédito Internacional, Maquila, captação, home equity, passivo bancário e turnkey (em validação).
- **Dono humano:** João Mattos e Paulo
- **Onde entrega:** `03 · Produtos e Projetos/Crédito Internacional` e `PROJETO MAQUILA`
- **Especialistas (12):**

| Especialista | Entrega única |
|---|---|
| Especialista Café e Agro | Leitura agro do caso de CI: (1) ciclo de caixa da safra e mês crítico; (2) dívida rural atual por linha (Pronamp, Funcafé, custeio livre, trading, CPR) e custo; (3) o que o CI pode trocar ou complementar; (4) garantias agro… |
| Captação de Capital e Preparação para Investidor | Dossiê de prontidão e rota de capital (interno, para o João ou o Paulo decidir) |
| Estruturador de Garantias e Projeto | Dossiê para o dono do produto levar à instituição: (1) resumo executivo da empresa e do empresário; (2) necessidade e plano de aplicação com cronograma; (3) capacidade de pagamento em 3 cenários (base, estresse, câmbio… |
| Gerente de Produtos Internacionais | Resposta única ao pedido, nos 3 blocos de infra/padrao-entrega.md: (1) o que você pediu (produto certo, faixa, próximo passo, quem conduz, rascunho de mensagem só de descoberta); (2) o que você também precisa (outro produto… |
| Guardião do Produto Novo | Quadro de portões e pendências (uma tela por produto): portão atual, o que o portão libera e o que não libera, documentos do kit (existe, rascunho, falta), perguntas críticas abertas com dono e prazo, decisões do Luis que… |
| Home Equity e Passivo Bancário | Diagnóstico de passivo bancário e rota de fôlego (interno, para validação do dono do produto) |
| Internacionalização Turnkey e Abertura de Mercado | Plano de entrada em mercado externo (go-to-market internacional), em 3 blocos, com |
| Maquila e Operação Industrial no Paraguai | Estudo de viabilidade "gol ou não gol" da produção no Paraguai (interno até o G2; descoberta para fora), com |
| Qualificador de Crédito Internacional | Ficha de qualificação do CI por oportunidade: eliminatórios K1–K10 (cada um com "sim/não/desconhecido" e a prova), pontuação de 0 a 100 pelos 11 critérios, faixa (Qualificado, Em desenvolvimento, Não qualificado), lacunas e o… |
| Especialista Regulatório e Câmbio | Mapa de perímetro regulatório da operação (uma página): para cada ato (originar, estruturar, receber fee, indicar investidor, receber dado, câmbio, registro), quem faz, se exige autorização (Bacen, CVM, Coaf, OAB), qual… |
| Revisor de Linguagem e Promessas | Parecer de linguagem do texto: lista de trechos com problema (frase original → motivo → frase segura), checagem dos 8 itens do checklist, resultado do auditor (zero alerta alto ou médio para material externo) e veredito:… |
| Tax Internacional e Comércio Exterior | Diagnóstico de tax internacional e comércio exterior (pré-análise para validação do Paulo ou do João e do técnico tributário). |

### Bloco: Venda e esteira

**6.9 Contas e Soluções** (`depto-solucoes`)

- **Missão:** Dono da esteira (Destravar caixa → Proteger e controlar → Crescer) e do mapa da conta: diz o que mais cada cliente pode contratar e encaminha ao dono do produto.
- **Dono humano:** Luis e Daniela
- **Onde entrega:** `01 · Comercial e Parceiros/Relatórios das áreas/Contas e Soluções`
- **Especialistas (10):**

| Especialista | Entrega única |
|---|---|
| Analista de Demonstrações Financeiras | Leitura Financeira da Conta (1 a 2 páginas, interna). |
| Arquiteto de Esteira e Mapa da Conta | Mapa da Conta com a Esteira em ondas para um cliente (ou a carteira de um Master). |
| Gestor de Valor | Mapa de Valor da Conta (one-pager, Word no padrão Save, references/demonstracao-valor.md) e o business case interno que o sustenta. |
| Orquestrador de Cross-sell | Ficha de Encaminhamento de Cross-sell, uma por gatilho. |
| Especialista Setorial · Agro e Cooperativas | Lente setorial do agro sobre o mapa da conta: para um cliente do grupo, o especialista devolve em uma página |
| Especialista Setorial · Construção, Imobiliário e Serviços | Lente setorial de construção e serviços sobre o mapa da conta, em uma página |
| Especialista Setorial · Indústria de Transformação | Lente setorial da indústria sobre o mapa da conta, em uma página |
| Especialista Setorial · Proteína Animal e Indústria de Alimentos | Lente setorial de proteína e alimentos sobre o mapa da conta, em uma página |
| Especialista Setorial · Transporte e Logística | Lente setorial de transporte sobre o mapa da conta, em uma página |
| Especialista Setorial · Varejo, Atacado e Combustíveis | Lente setorial de varejo, atacado e combustíveis sobre o mapa da conta, em uma página |

**6.10 Apresentação do Diagnóstico** (`apresentacao-diagnostico`)

- **Missão:** Transforma o diagnóstico tributário revisado na apresentação ao cliente, com narrativa, objeções, case do segmento e revisão de promessas.
- **Dono humano:** Luis e Geovana
- **Onde entrega:** `06 · Marketing e Apresentações/Diagnósticos`
- **Especialistas (4):**

| Especialista | Entrega única |
|---|---|
| Curador da Biblioteca de Cases por Segmento | A ficha de case aprovada (ou o veto motivado) para o slide "Quem já fez" de um diagnóstico. |
| Roteirista de Narrativa Executiva do Diagnóstico | O roteiro do deck do diagnóstico de um cliente, antes de qualquer imagem. |
| Objeções do Empresário | O mapa de objeções do caso, anexo às notas de fala do deck. |
| Revisor de Promessas da Peça do Diagnóstico | O parecer de linguagem do deck do diagnóstico, slide a slide, antes de ir ao Luis. |

**6.11 Revisor de Diagnóstico** (`revisor-diagnostico`)

- **Missão:** Segunda opinião antes do cliente: aponta as teses esperadas que o técnico não analisou e o registro do SPED que decide.
- **Dono humano:** Geovana
- **Onde entrega:** `Área Partners · Agentes/Central Técnica · Geovana`
- **Especialistas (3):**

| Especialista | Entrega única |
|---|---|
| Evidência no SPED | Para cada lacuna ou tese, o único documento que decide e o pedido mínimo ao cliente. |
| Revisor de Lacunas por Perfil e Curador da Matriz Tese × Perfil | A lista de lacunas por negócio em "Apresentação de Diagnóstico", com a decisão pronta para a Geovana: Incluir tese, Não se aplica ou Precisa de dado. |
| Leitor de Pareceres e Diagnósticos | A leitura padronizada de cada parecer: para cada tese do catálogo, o status (apurada com valor, analisada sem valor, citada, ausente), o período, a via (administrativa ou judicial), o motivo de não aplicação quando houver, os… |

**6.12 Recuperador de Perdidos** (`recuperador`)

- **Missão:** Fila semanal dos negócios perdidos e parados com chance de reanálise, com folha curta de decisão para a Geovana.
- **Dono humano:** Geovana
- **Onde entrega:** `Central Técnica · Geovana` (fila, folha do lote e fichas)
- **Especialistas (2):**

| Especialista | Entrega única |
|---|---|
| Curador da Tabela de Teses por Perfil | A tabela de teses por perfil vigente e, por linha, o registro do SPED que decide a tese. É o que o Redator da ficha de reanálise usa para escrever a hipótese e o que a Geovana usa para vetar. |
| Analista de Triagem de Perdidos | A fila priorizada e o lote semanal de 20 casos para a Geovana decidir, com motivo de entrada, vetos aplicados, sinal do parecer e potencial pelo look-alike. |

**6.13 Pós-venda** (`depto-pos-venda`)

- **Missão:** Acompanha o crédito até o dinheiro: prazo de 360 dias do PER, compensação de ofício, recebimento e recorrência.
- **Dono humano:** Área de Pós-venda e Daniela
- **Onde entrega:** Calendário e rascunhos ao parceiro; `Relatórios das áreas`
- **Especialistas (3):**

| Especialista | Entrega única |
|---|---|
| Compensação de Ofício e Recebimento | O extrato do crédito por cliente e o aviso de honorário do mês, conciliados. |
| Recorrência | O calendário de recorrência da carteira ganha e a lista mensal de gatilhos. |
| Ressarcimento e Prazos | A ficha de acompanhamento do PER (uma por pedido) e a tabela de prazos do mês de toda a carteira com PER em análise. |

### Bloco: Canal

**6.14 Central Masters (Daniela)** (`celula-daniela`)

- **Missão:** Atende os 9 Masters: triagem e SLA, retorno ao parceiro, plano de conta e reunião trimestral, apoio jurídico ao canal e higiene do CRM.
- **Dono humano:** Daniela
- **Onde entrega:** `Área Partners · Agentes/Central Masters · Daniela`
- **Especialistas (5):**

| Especialista | Entrega única |
|---|---|
| Apoio Jurídico ao Canal | O encaminhamento jurídico do canal: a ficha que leva o tema certo ao especialista certo do depto-juridico, e depois a versão para o parceiro. |
| Gestor de Contas-Chave de Canal | O plano de conta trimestral de cada Master, com o QBR que o revisa. É a única entrega que liga números, relacionamento e compromisso com cada um dos 9 Masters. |
| Higiene de CRM e Registro de Oportunidade | A proposta de atualização do CRM e o parecer de registro de oportunidade. Dois formatos, gerados com scripts/crm_checagem.py e completados pelo especialista |
| Retorno ao Parceiro | O rascunho da mensagem ao parceiro, pronto para a Daniela enviar. Uma por demanda e por momento (recebido, pedir dados, status, entrega, atraso), no canal certo (WhatsApp até cerca de 6 linhas; e-mail quando houver anexo,… |
| Triagem e SLA das demandas dos Masters | A ficha de triagem de cada demanda, com tipo, rota, dados mínimos, prazo e cobrança. Tudo o que chega dos Masters (WhatsApp, GLPI, e-mail, reunião) vira uma ficha no modelo 1 de references/modelos.md e uma linha no controle… |

**6.15 Central BDR (Jenifer)** (`celula-jenifer`)

- **Missão:** Prospecção para os Masters: listas, qualificação, abordagem por persona, objeções, LGPD na prospecção e preparação de reunião.
- **Dono humano:** Jenifer
- **Onde entrega:** `Área Partners · Agentes/Central BDR · Jenifer/Listas`
- **Especialistas (5):**

| Especialista | Entrega única |
|---|---|
| LGPD na Prospecção | Pacote de conformidade da prospecção, mantido por versão: (a) LIA da prospecção B2B (finalidade, necessidade, balanceamento, salvaguardas) para o Jurídico assinar; (b) linha do registro de operações (art. 37): dados, fonte,… |
| Objeções com Base Técnica | Mapa de objeções por tese e por produto, com resposta pronta e prova: para cada objeção frequente, (a) o que está sendo dito de verdade, (b) a pergunta de exploração, (c) a resposta curta para a Jenifer ou o Master usar (até… |
| Preparação de Reunião | Briefing de 1 página pronto na véspera + roteiro de 30 minutos + confirmação (M6), para cada reunião agendada pela Jenifer: retrato da empresa (Receita), histórico com a Save (raiz do CNPJ no HubSpot) e conflito, 2 a 3… |
| Prospecção Outbound B2B | Plano de cadência por conta e por persona, com os rascunhos do dia: para cada empresa marcada "Abordar" pela Jenifer, o caminho (apresentação pelo Master ou contato institucional), a persona-alvo (sócio, CFO ou controller,… |
| Qualificação | Ficha de qualificação por oportunidade depois de cada conversa: R-D-A-C-H-U marcado com evidência, vetos checados, produto de entrada, decisão (SQL → Master/Técnico, Nutrição ou Descartado com motivo padronizado), próximo… |

**6.16 Inteligência Comercial** (`depto-intel-comercial`)

- **Missão:** Perfil de cliente ideal por produto, tamanho de mercado, lead scoring, território por Master, concorrência e recrutamento de parceiros.
- **Dono humano:** Luis e Jenifer
- **Onde entrega:** `Relatórios das áreas`; listas na Central BDR
- **Especialistas (6):**

| Especialista | Entrega única |
|---|---|
| Arquiteto de ICP por Produto | Ficha de ICP por produto, uma linha por produto do portfólio 2027 (P1 a P18, N1 a N5, teses T01 a T19), com: porte (faixa de faturamento e origem do dado), regime, setores (tier 1, 2, 3), UF e Master com histórico, sinais de… |
| Dimensionamento de Mercado | Dimensionamento por produto × UF × segmento, com o funil de elegibilidade e três números: TAM (empresas e valor potencial em que o produto pode existir), SAM (onde a Save consegue atender: segmentos do ICP, UFs com Master,… |
| Inteligência Competitiva | Mapa competitivo por produto com battlecard: para cada produto do portfólio (recuperação, Gestão de Passivo, Gestão de Contas, antecipação, FIDC, estruturação patrimonial, produtos em validação), a lista de concorrentes por… |
| Lead Scoring e Look-alike | Modelo de score de conta versionado (v1, v2…), com: dimensões e pesos, regra de cada ponto em uma frase, faixas A/B/C com a ação de cada faixa, métricas de validação (AUC, calibração por faixa, conversão por faixa no trimestre… |
| Recrutamento de Parceiros | Mapa de recrutamento por praça com perfil de parceiro ideal: para cada praça descoberta ou sub-coberta (do Território), a lista de escritórios contábeis-alvo (CNAE 6920-6/01 e 6920-6/02, ativos, matriz, com porte e capital), a… |
| Território e Cobertura por Master | Mapa de território e cobertura por Master: matriz Master × segmento × UF × região imediata com ganhos em 12 meses, valor ganho, penetração (ganhos ÷ universo elegível), status (coberto, sub-coberto, descoberto), regras de… |

**6.17 Operações de Canal** (`depto-operacoes-canal`)

- **Missão:** Repasse e comissão do parceiro (D64, D78, D97), retenções, extrato, registro de oportunidade e conflito de canal.
- **Dono humano:** Luis e Financeiro
- **Onde entrega:** `Relatórios das áreas` (Conferência de Repasses, Conflito de Canal)
- **Especialistas (5):**

| Especialista | Entrega única |
|---|---|
| Analista de Comissionamento | Conferência de repasses e provisão por parceiro. Inclui |
| Elegibilidade e Retenções do Pagamento a Parceiro | Checklist de elegibilidade e quadro de retenções por lote de pagamento. Para cada parceiro do lote, traz |
| Extrato, Prestação de Contas e Contestações do Parceiro | Rascunho do extrato mensal por parceiro mais o registro de contestações com SLA. O extrato traz |
| Política do Programa de Parceiros, Termos e Níveis | Política do programa de parceiros versionada. Ela traz |
| Registro de Oportunidade e Conflito de Canal | Relatório de conflito de canal com pauta de decisão. Traz |

**6.18 Contratos** (`depto-contratos`)

- **Missão:** Lê e prepara contratos de serviço, de parceiro e dos produtos 2027; assinatura, distrato e cobrança. Nunca envia nem assina.
- **Dono humano:** Área de Contratos e Jurídico
- **Onde entrega:** Pedido à área real; `Relatórios das áreas` (Controle de Contratos)
- **Especialistas (5):**

| Especialista | Entrega única |
|---|---|
| Assinatura Eletrônica e Validade do Contrato | Parecer de formalização do contrato, de uma página. Ele traz |
| Contratos com Parceiros | Ficha de enquadramento e de cláusulas do termo com o parceiro. Ela traz |
| Contratos dos Produtos 2027 | Mapa contratual do produto, uma folha por produto. Ela traz |
| Contratos de Prestação de Serviços Tributários | Ficha de cláusulas do contrato de prestação de serviços tributários, por tese e por pipeline (RT Real e Presumido, Simples, Gestão de Passivo), com |
| Distratos, Rescisões e Cobrança de Honorário | Dossiê de distrato ou de cobrança, com |

**6.19 Partner Success** (`depto-partner-success`)

- **Missão:** Academia de parceiros, onboarding, níveis do programa, saúde e churn de parceiro e comunidade.
- **Dono humano:** Luis e Daniela
- **Onde entrega:** `01 · Comercial e Parceiros/Programa de Parceiros`; Métricas PS
- **Especialistas (5):**

| Especialista | Entrega única |
|---|---|
| Analista de Saúde, Ativação e Churn de Parceiro | A lista priorizada de risco e de oportunidade de ativação do canal: quem está em rampa, dormente, travado no onboarding ou em risco de churn, com o motivo em dado, a data da base, o dono do toque e a pergunta para a conversa;… |
| Coach de Onboarding e Enablement | O plano de ativação individual de cada parceiro novo (indicador ou Master) e o plano de reativação de quem travou: 30/60/90 com marcos mensuráveis no HubSpot, roteiro dos check-ins D+30, D+60 e D+90, regra de co-venda das duas… |
| Designer da Academia de Parceiros | O currículo da Academia de Parceiros Save: trilhas por tese (T01 a T19 e P01/P02) e por produto 2027, cada módulo com objetivo, conteúdo-base validado, "o que fazer amanhã", "o que não dizer", 5 a 10 questões de quiz com… |
| Gestor de Comunidade, Eventos e Conselho de Parceiros | O calendário e o roteiro de comunidade do canal: Conselho Consultivo de Parceiros (semestral), webinars técnicos (mensal), encontros regionais e o encontro anual, cada um com objetivo, público, pauta, convite (rascunho),… |
| Gestor de Níveis, Benefícios e Jornada do Parceiro | O desenho e a apuração do programa de níveis e da jornada do parceiro: critérios por nível (trilha Master e trilha Indicador), simulação com dados reais, matriz de benefícios, rito de observação e mudança de nível, carta de… |

### Bloco: Gestão

**6.20 Resultados & Controladoria** (`depto-resultados`)

- **Missão:** Relatório semanal: receita contratada, reconhecida e recebida, margem, forecast, ROI, preço e metas por produto.
- **Dono humano:** Luis
- **Onde entrega:** `04 · Gestão/Resultado semanal`
- **Especialistas (6):**

| Especialista | Entrega única |
|---|---|
| Controller de Receita Reconhecida | A ponte de receita da Área Partners em quatro colunas, por negócio e por mês: contratado · ajustado ao risco (conservador) · reconhecido · recebido, com o backlog e o aging. |
| Analista de Forecast e Pipeline | O forecast do trimestre e do ano em honorário (bruto e líquido), em três versões (contratado, conservador e realizado), com a cobertura de pipeline sobre a meta e a acurácia do forecast anterior. |
| Analista de Margem e DRE da Área | A DRE gerencial da Área Partners e a margem por negócio, por parceiro e por tese, com a explicação da variação (preço, volume, mix e repasse). |
| Analista de Metas e Medição por Produto 2027 | O desdobramento da meta (Q4/2026 e 2027) por produto, Master e mês, e o painel de funil por produto, com o realizado em três colunas e o status das metas de validação. |
| Analista de Preço e Fee | A recomendação de preço e de fee por produto e por negócio: modelo de cobrança, faixa interna (mínimo, típico, máximo), alçada de desconto, efeito na margem e o que está vedado. Formatos |
| Analista de ROI e Caixa | O ROI da área em três versões (contratado, conservador e realizado), trimestral móvel, e a curva de caixa esperada da carteira ganha, com backlog e prazo médio até o caixa; mais o business case de cada iniciativa nova (payback… |

**6.21 Dados & BI** (`depto-dados`)

- **Missão:** Download diário do HubSpot (só leitura), qualidade e saneamento do CRM, dicionário, painel e estatística.
- **Dono humano:** Luis
- **Onde entrega:** `Relatórios das áreas` (Dados-BI diário)
- **Especialistas (5):**

| Especialista | Entrega única |
|---|---|
| Analista de BI, Visualização e Saúde do Parceiro | O painel de qualidade do CRM e o scorecard de saúde dos parceiros, prontos para decisão. |
| Engenheiro de Dados do HubSpot | O arquivo-fonte do dia, completo e auditável: ~/agentes-partners/departamentos/resultados/dados/hubspot-AAAA-MM-DD.json, gerado por depto-resultados/scripts/hubspot_fonte.py --baixar (somente leitura), com: data e hora do… |
| Estatístico de Look-alike, Coortes e Inferência | Estimativas com incerteza declarada para decidir onde pôr esforço: (a) look-alike dos clientes ganhos (taxa de sucesso e honorário esperado dos parecidos) para priorizar filas do Recuperador e listas da Jenifer; (b) coortes de… |
| Arquiteto de Governança e Dicionário de Dados | O dicionário oficial de dados e métricas da Área Partners, versionado. Duas partes |
| Guardião de Qualidade e Saneamento do CRM | Lista de saneamento do CRM, com evidência e decisão proposta por linha. Formatos |

**6.22 Qualidade & Ouvidoria** (`depto-qualidade`)

- **Missão:** Auditor de promessas, controle das entregas dos agentes, incidentes e reclamações, voz do parceiro e melhoria contínua.
- **Dono humano:** Luis
- **Onde entrega:** Revisão de todo material externo; `Relatórios das áreas`
- **Especialistas (5):**

| Especialista | Entrega única |
|---|---|
| Auditor de Promessas Comerciais | Parecer de auditoria de promessas de um material, de um modelo ou de uma amostra mensal: para cada marcação ALTO ou MÉDIO, o trecho, a regra (P1 a P10), o veredito (risco real, falso positivo ou termo técnico aceito), a… |
| Controlador de Qualidade das Entregas dos Agentes | Boletim mensal de qualidade das entregas dos agentes: amostra por área e por classe de risco, defeitos encontrados por tipo (taxonomia abaixo), taxa de defeito por área com limite de controle, taxa de retrabalho (rodadas de… |
| Gestor de Incidentes, Reclamações e Ouvidoria | Para cada caso, a ficha única de ocorrência (reclamação ou incidente) com classificação (tema A, etapa B, causa C, severidade S; ou tipo de incidente I1 a I4), linha do tempo, contenção, prazos, rascunho do acuse e da… |
| Analista de Melhoria Contínua e Causa-raiz | Registro de CAPA e revisão mensal de melhoria: para cada não conformidade relevante (S1/S2, defeito A das entregas, I4, falso positivo recorrente, driver de NPS repetido), a ficha CAPA com descrição, correção imediata, análise… |
| Pesquisador de Voz do Parceiro e do Cliente | Plano e leitura da escuta: para cada ciclo, o questionário por momento (gatilho, público, remetente, canal, base legal declarada), o cálculo por script (NPS, CSAT, CES, taxa de resposta, margem de erro ou "base pequena"), a… |

### Bloco: Suporte

**6.23 Marketing** (`depto-marketing`)

- **Missão:** Campanhas de canal com calendário fiscal, ABM, kits por produto, redação, design no padrão Save e conformidade publicitária.
- **Dono humano:** Luis e Marketing da Save
- **Onde entrega:** `06 · Marketing e Apresentações`
- **Especialistas (7):**

| Especialista | Entrega única |
|---|---|
| Demanda e ABM de Canal | Plano de conta-alvo por território, entregue ao parceiro dono. |
| Autoridade Digital | A pauta de autoridade da semana, alimentada pelo jornal diário. |
| Conformidade Publicitária | O parecer de conformidade de cada peça. |
| Designer do Design System Save v0.5 | A peça visual pronta no Design System Save v0.5, com o briefing visual. |
| Enablement de Vendas do Parceiro | O kit de vendas do parceiro por produto ou por tese. |
| Estrategista de Campanhas de Canal & Calendário Fiscal | Plano trimestral de campanhas de canal com calendário datado. |
| Redator B2B Tributário e Financeiro | O texto final de cada peça, em rascunho, com a tabela de afirmações. |

**6.24 Pessoas** (`depto-pessoas`)

- **Missão:** Remuneração variável, metas e desempenho, capacitação técnica, recrutamento, clima e conformidade com a CLT e a LGPD.
- **Dono humano:** Luis
- **Onde entrega:** Rascunhos confidenciais na conversa (dado de pessoas fica no Mac)
- **Especialistas (6):**

| Especialista | Entrega única |
|---|---|
| Capacitação Técnica e PDI | A trilha técnica por função e o PDI de capacitação de cada pessoa. |
| Clima, Liderança e Conversas | O roteiro da conversa (1:1, feedback, conversa difícil ou de clima) e o plano de ação de clima do time. |
| Guardião CLT e LGPD | A checagem de conformidade de toda entrega do departamento de Pessoas, mais os indicadores agregados do time. |
| Metas e Desempenho | O desdobramento de metas por função e por pessoa, com a régua de avaliação e o roteiro de calibração. |
| Recrutamento, Perfis e Carreira | O pacote de perfil e seleção de uma vaga (ou a descrição de cargo e o degrau de carreira de uma função existente). |
| Remuneração Variável e Comissões | O rascunho do plano de remuneração variável (ou da mudança no plano), pronto para o RH, o Financeiro e o Jurídico trabalhista avaliarem. |

**6.25 TI & Automação** (`depto-ti`)

- **Missão:** Integrações (Graph, HubSpot, GLPI, WhatsApp), segurança e SSO, incidentes, rotinas agendadas, custos e governança de IA.
- **Dono humano:** TI da Save
- **Onde entrega:** Pedidos e especificações em `04 · Gestão/Central de Agentes`
- **Especialistas (6):**

| Especialista | Entrega única |
|---|---|
| Administrador do GLPI e Automação de Processos | A mudança de configuração do GLPI (ou de um processo automatizado) especificada para o TI executar. |
| Arquiteto de Integrações | A especificação de integração de 1 página, pronta para o TI da Save executar. |
| Gestão de Incidentes e Registro | A ficha do incidente, do registro à regra nova. |
| Governança de IA | O registro de governança de cada agente: linha do inventário, ficha de avaliação antes do uso real e decisão de autonomia. |
| Identidade, Segurança e LGPD Técnica | A nota de segurança e acesso de um sistema ou fluxo, com o rascunho do chamado ao TI. |
| Operação, Rotinas Agendadas, Continuidade, Custos e Capacidade | O mapa de execução das rotinas com o plano de continuidade e o quadro de custo e capacidade. |

## 7. Rotinas automáticas
| Rotina | Quando | O que entrega | Onde |
|---|---|---|---|
| Operação das áreas | Dias úteis, 7h40 | Cada área analisa os alertas do dia em 3 blocos; às segundas, carteira de cross-sell | Plano do dia em `04 · Gestão/Central de Agentes` |
| WhatsApp · triagem | Dias úteis, 8h e 14h (11h e 17h sem IA) | Lê os grupos dos Masters e as caixas do time, interpreta e devolve analisado | Pastas das Centrais em `Área Partners · Agentes` |
| Central de Agentes | Dias úteis, de hora em hora (8h às 18h) | Processa pedidos do painel e do e-mail [AGENTES] e aplica as decisões do painel | E-mail ou `Caixa de saída` |
| Relatório semanal de resultados | Segunda, 6h30 | Deck e one-pager de resultados | `04 · Gestão/Resultado semanal` |
| Conselho · reunião semanal | Segunda, 7h30 | Ata com recomendação, o que não fazer e decisões para aprovar | `04 · Gestão/Conselho` |
| Recuperador · lote semanal | Segunda, 9h | Fila, folha curta do lote e fichas para a Geovana | `Central Técnica · Geovana` |
| Radar de mercado | Sexta, 7h | Cada área pesquisa o que mudou (normas, julgados, taxas) e atualiza o radar | Branch `radar/<data>` e resumo em `Central de Agentes/Radar de mercado` |
| Consolidação semanal | Sexta, 16h | Junta as conversas, resgata arquivos, aponta repetições e atualiza a folha de decisões | `gabinete/SESSOES.md` e `Decisoes-Pendentes-<data>.xlsx` |

## 8. Onde ficam as coisas
| O quê | Onde |
|---|---|
| Código, skills, regras e decisões | Repositório `~/agentes-partners` (GitHub `luismelo-lab/agentes-partners`, privado) |
| Cópia viva que os agentes usam | `~/.claude/skills/` e `~/.claude/scheduled-tasks/` |
| Decisões do Luis e do Conselho | `conselho/decisoes.md` (D1 a D97) |
| Folha de decisões para aprovar ou reprovar | `04 · Gestão, Metas e Estratégia/Central de Agentes/Decisoes-Pendentes-<data>.xlsx` |
| Guia das conversas por tema | `gabinete/SESSOES.md` |
| Pedidos do Luis (porteiro) | `registro/pedidos-luis.jsonl` |
| Pastas do time | `Área Partners · Agentes/` (Central Masters · Daniela, Central BDR · Jenifer, Central Técnica · Geovana) |
| Relatórios das áreas | `01 · Comercial e Parceiros/Relatórios das áreas` |
| Gestão, Conselho e resultado | `04 · Gestão, Metas e Estratégia` (Central de Agentes, Conselho, Resultado semanal, Planejamento 2027) |
| Produtos | `03 · Produtos e Projetos` (Crédito Internacional, Maquila) |
| Apresentações e marca | `06 · Marketing e Apresentações` |
| Dados de clientes e fontes oficiais baixadas | `departamentos/<área>/` no Mac, fora do git |

Links do OneDrive saem de `lib/caminhos.py`: só o link de pasta abre, então toda resposta dá o nome do arquivo e o link da pasta.

## 9. Responsabilidades das pessoas
| Pessoa | Responde por |
|---|---|
| **Luis** | Decide e aprova; faz o merge e o push; responde a folha de decisões; aprova chamados no painel uma vez por dia |
| **Daniela** | Masters: demandas, retorno ao parceiro, ganhos a completar no HubSpot, plano de conta |
| **Jenifer** | Prospecção e listas para os Masters |
| **Geovana** | Decisões do Recuperador e do Revisor; diagnóstico |
| **Junior** | Save Invest: Gestão de Contas, antecipação, FIDC; venda gerencial e escrow presencialmente |
| **João Mattos** | Produtos em validação: Crédito Internacional, Maquila, captação, home equity, turnkey |
| **Paulo** | Tax internacional e comércio exterior, com o João |
| **Advogado humano** | Valida Gestão de Passivo e Estruturação Patrimonial (até 07/11) e as minutas |
| **Time técnico** | Valida Alíquota Zero e PER e Reforma; parecer das teses |
| **TI da Save** | Credenciais do Graph e do GLPI, SSO, escopo de arquivos do HubSpot |

## 10. Governança
- **Uma conversa por tema.** Cada tema tem sua seção em `gabinete/SESSOES.md`. Pedido novo passa pelo porteiro.
- **Git.** Cada conversa trabalha na sua branch; o hook `infra/checar-dados.py` precisa dar 0 achados; o Luis faz o merge (`cd ~/agentes-partners && git merge --no-edit <branch> && git push`).
- **Cópia viva.** Ao alterar uma skill ou rotina, copiar para `~/.claude/` depois de conferir que a cópia viva é igual ao HEAD.
- **Decisões.** Viram D-número em `conselho/decisoes.md`. As pendentes vão para a folha com campos de seleção (Aprovar, Aprovar com ajuste, Reprovar, Decidir depois), e a consolidação de sexta aplica as respostas.
- **Perguntas ao dono.** Cada área mantém `references/perguntas-ao-dono.md`, com data e por que importa.

## 11. Pendências abertas (23/10/2026)
| # | Pendência | Quem resolve |
|---|---|---|
| 1 | T07 (ISS fora da base, Tema 118 julgado em 21/10) volta à vitrine? Via da T15 (Tema 843) | Luis e time técnico |
| 2 | Meta do Q4 de R$ 200 mi: crédito ou líquido? | Luis |
| 3 | Transação de pequeno valor da Receita até 30/10: triagem da carteira | Luis |
| 4 | WhatsApp da cobrança sem a API oficial (D97) | Junior e Jurídico |
| 5 | Dono do passivo bancário; regras do Paulo de 21/10 como D-número | Luis |
| 6 | Nomes dos validadores do Jurídico e do time técnico (D94) | Luis |
| 7 | Papel da Federal Invest na CVM; razão social e CNPJ da Save Invest | Junior |
| 8 | Credenciais do Graph e do GLPI | TI |
| 9 | CNPJ alfanumérico nos scripts | Conversa própria, em andamento |
| 10 | Contraste do ouro #B58A1F em texto corrido (3,17:1) | Luis e Marketing |

## 12. Glossário
- **Área:** grupo de agentes com um gerente e especialistas (uma skill).
- **Especialista sênior:** agente com uma entrega única e arquivo próprio no padrão D93.
- **Porteiro:** checagem de repetição antes de executar um pedido.
- **Esteira:** Destravar caixa → Proteger e controlar → Crescer.
- **G2:** portão do produto novo; antes dele, nada de taxa, prazo ou fee para fora.
- **PER:** pedido eletrônico de ressarcimento. **DCOMP:** declaração de compensação.
- **3 blocos:** o que você pediu; o que você também precisa; o que falta e quem fornece.
- **Cópia viva:** a versão das skills e rotinas que os agentes executam, em `~/.claude/`.
