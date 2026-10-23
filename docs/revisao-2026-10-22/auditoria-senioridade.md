# Auditoria de senioridade dos agentes · Área Partners

22/10/2026. Regra do Luis da mesma data: cada área é composta por especialistas sêniores, cada um dono de uma entrega, sem conhecimento raso (`infra/padrao-senior.md`). Esta auditoria leu o SKILL.md e as references de 23 áreas e o conhecimento que elas usam fora da skill (`departamentos/`, `docs/`, `infra/`). Ficaram fora `depto-internacional` e `depto-save-invest`, que estão sendo refeitas. Nada foi alterado nas skills.

**Duas notas, com papéis diferentes:**
- **Nota do script** (`python3 infra/auditar_senioridade.py`): mede a conformidade com o padrão (arquivo por especialista, 10 seções, normas, datas, D-números, perguntas e casos). Hoje nenhuma área tem `references/especialistas/`, então todas caem na heurística, que tem teto de 40. Média de 17.
- **Nota qualitativa** (esta leitura): mede a profundidade real do que o agente sabe hoje, onde quer que esteja escrito. Serve para ordenar o aprofundamento.

**Conclusão em uma frase:** nenhuma área está no padrão sênior. Quatro têm base de domínio de verdade (Tributário, Jurídico, Soluções e o par Recuperador/Revisor), mas o conhecimento está no radar e nos documentos do portfólio, e não em especialistas com método, perguntas e casos. As demais são orquestração bem desenhada (regras, scripts, portões) com conhecimento de domínio raso.

---

## 1. Tabela-resumo

Legenda do veredito (nota qualitativa): **sênior** 70 ou mais · **intermediário** 45 a 69 · **raso** abaixo de 45. "Papéis hoje" são os especialistas descritos no SKILL.md ou em `equipe.md`; nenhum tem arquivo próprio.

| Área | Papéis hoje | Script | Nota | Veredito | As 3 maiores lacunas de conhecimento |
|---|---|---|---|---|---|
| `depto-tributario` | 12, em uma linha de tabela cada | 30 | 58 | intermediário | (1) Cada especialista é uma linha: sem método, perguntas nem casos por tese (T01 a T19); o melhor conteúdo está em `docs/portfolio-2027/agentes/tributario-revisao.md` (50 kB), fora da skill. (2) Reforma em 1,9 kB: falta o pacote 2027 (LC 214 arts. 378 a 383, Decreto 12.955 arts. 602 a 608, crédito de estoque, aditivo CBS/IBS do G0-B), que é o produto pronto P8. (3) SPED sem leiaute: nenhum registro da EFD-Contribuições ou da EFD ICMS/IPI que "decide" cada tese; ICMS sem RICMS por UF |
| `depto-juridico` | 10 | 29 | 45 | intermediário | (1) **Não cobre estruturação patrimonial (P10, produto pronto):** sem LC 227/2026 (ITCMD de cotas a valor de mercado), Temas 796 e 1.214 do STF, Lei 15.270/2025 nem alíquota de ITCMD por estado. (2) **Não cobre Gestão de Passivo (P5, pronto):** sem Lei 13.988/2020, editais da PGFN (Edital 6 prorrogado até 29/01/2027), parcelamentos, CND, seguro garantia (LC 236/2026), nem o Funrural como passivo (D86). (3) Perímetro CVM/BCB/OAB dos produtos do ecossistema existe só em `docs/portfolio-2027/agentes/juridico-revisao.md`; nenhuma pergunta de diagnóstico, nenhum caso, nenhum D-número |
| `depto-solucoes` | 7 | 36 | 55 | intermediário | (1) Sem analista financeiro do cliente: os sinais da reunião de 13/10 (despesa financeira alta, contas a receber acima do faturamento, dívida de curto prazo de 3 a 4 faturamentos, SCR) não viraram método. (2) Gestão de Contas e antecipação (P4, P9, prontos) sem especialista: a skill aponta para o `depto-internacional`, que está em reconstrução. (3) O especialista setorial é um papel só para 7 setores; a jornada v2 (`solucoes-jornada.md`, 51 kB) e a divergência C7 não entraram na esteira |
| `recuperador` | agente único | 15 | 52 | intermediário | (1) Matriz tese × perfil (`matriz.json`) desatualizada frente às erratas E1 a E5: supermercado em "alta" contra o catálogo (C4), T13/T16 fora da vitrine (D80), T19 virou passivo (D86). (2) Fase 1 sem SPED (D3): a hipótese de reanálise não tem o registro que decide. (3) Recorrência (P2, pronto) é regra de fila, não especialista com método de decadência mensal |
| `revisor-diagnostico` | agente único | 15 | 50 | intermediário | (1) `teses.json` tem itens "confirmar" citados de memória técnica. (2) Teses que a Save faz e a matriz não classifica (DIFAL Tema 1.372, própria base, ISS, ICMS-ST) nunca viram lacuna. (3) Pareceres em arquivo do HubSpot sem escopo `files`: nenhuma lacuna é "confirmada" |
| `apresentacao-diagnostico` | 4 frentes ad hoc | 28 | 38 | raso | (1) Só procedimento: sem método de narrativa e de objeções por persona (dono, CFO, contador). (2) Biblioteca de cases sem regra de anonimização e de prova na skill (está em `biblioteca-cases/README.md`). (3) Os critérios dos produtos financeiros citados (FIDC acima de R$ 10 mi/mês, funding acima de R$ 60 mi) vêm de reunião, sem D-número |
| `celula-daniela` | 8 subagentes | 18 | 42 | raso | (1) SLA e tipos de demanda ainda "proposta a validar" (Semana 0 não fechada). (2) Sem especialista de Partner Account Management: plano de conta, QBR e JBP sem método nem metas por Master. (3) Apoio jurídico delega tudo ao `depto-juridico`, que não cobre passivo nem estruturação patrimonial, temas que os Masters trazem |
| `celula-jenifer` | 9 subagentes | 19 | 45 | intermediário | (1) Sem base de legítimo interesse (LIA) validada: contatos pessoais desligados limitam a prospecção. (2) Objeções por persona e por segmento sem base técnica (o que dizer ao contador que resiste). (3) Referências de cadência "de mercado" sem fonte nem data |
| `central-agentes` | 1 (orquestrador) | 7 | 30 | raso | (1) Sem critério escrito de triagem por tipo de pedido (o catálogo saiu do painel). (2) Sem casos de pedidos bons e reprovados (só `aprendizados.md`). (3) Sem regra de quando um pedido sobe ao Gabinete |
| `conselho-partners` | 6 conselheiros + presidente | 16 | 25 | raso | (1) Cada conselheiro é um parágrafo de persona, sem frameworks nem números de mercado. (2) Conselheiro Financeiro sem a economia da Save (honorário realizado de 25%, repasse de 30,7%, meta 2027 de R$ 49,8 mi). (3) Conselheiro de Risco sem a pré-análise do portfólio (CVM, OAB, BCB) |
| `depto-contratos` | 6 | 20 | 32 | raso | (1) **Pasta `departamentos/contratos/modelos/` vazia:** nenhum modelo aprovado; o Montador não pode montar nada. (2) Sem contratos dos produtos 2027 (mandato de cobrança, indicação à instituição, DPA, contrato do escritório para P10), descritos em `juridico-revisao.md`. (3) Assinatura eletrônica marcada "VALIDAR" (Lei 14.063/2020, MP 2.200-2/2001) |
| `depto-dados` | 6 | 3 | 22 | raso | (1) Só o SKILL.md: sem dicionário de campos do HubSpot próprio nem modelo de dados. (2) Sem método de deduplicação para os ~295 ganhos duplicados (decisão pendente 10). (3) Sem campo "produto de entrada" para medir conversão por produto (pedido do portfólio) |
| `depto-intel-comercial` | 7 | 8 | 35 | raso | (1) O ICP por produto (`intel-comercial-icp.md`, 55 kB, 22/10) não está ligado à skill. (2) Sem tamanho de mercado por CNAE × UF × regime com fonte (Receita, IBGE, CONAB). (3) Concorrência sem base: fees e modelos de concorrentes só como hipótese |
| `depto-marketing` | 11 | 15 | 30 | raso | (1) Publicidade sem base própria: Provimento 205/2021 da OAB, CONAR e regras da Meta para WhatsApp ficam com o Jurídico. (2) `datas.md` genérico (dias comemorativos), sem calendário fiscal datado. (3) Enablement por tese sem conteúdo técnico; nenhum caso aprovado |
| `depto-operacoes-canal` | 7 | 17 | 40 | raso | (1) Boas práticas "sem pesquisa web" e sem data de fonte. (2) Sem Lei 4.886/1965 (representação comercial) nem Res. CMN 4.935/2021 (correspondente), levantadas no conflito C1. (3) Sem a política vigente: D78 (10% do líquido Save nos produtos 2027) e D61 não estão na skill; retenções sobre a NF do parceiro sem regra |
| `depto-partner-success` | 6 | 26 | 45 | intermediário | (1) Academia sem módulo por tese (o currículo não existe). (2) Níveis L1 a L10 pendentes de decisão (folha de 22/10, item 8). (3) Sem casos de ativação medidos; a data de entrada do parceiro não existe no HubSpot |
| `depto-pessoas` | 9 | 13 | 30 | raso | (1) Variável e comissão sem base: CLT art. 457 (natureza da verba), Lei 10.101/2000 (PLR) só citados por nome. (2) Sem referência salarial de mercado com fonte e data. (3) Modelos de 2 kB: PDI, metas e 1:1 sem exemplos preenchidos |
| `depto-pos-venda` | 6 | 17 | 45 | intermediário | (1) **Ressarcimento (o caixa da tese principal) sem base:** prazo de 360 dias para análise (Lei 11.457/2007, art. 24) e correção pela Selic depois dele (STJ, Tema 1.003) [conferir]. (2) Sem fonte de valor recebido: o campo do HubSpot está 100% vazio. (3) Calendário mensal sem agendamento nem validação da área real |
| `depto-qualidade` | 6 | 19 | 48 | intermediário | (1) Auditoria de promessas por regex sem casos de falso positivo catalogados por tipo de material. (2) Ouvidoria ISO 10002 sem série histórica (GLPI fora de produção). (3) Sem base de publicidade (OAB e CONAR) própria para julgar o contexto |
| `depto-resultados` | 9 | 16 | 42 | raso | (1) Preço e fee (`precos-fees.md`, 49 kB) não ligados: escala 30/25/20% com piso de 20%, cestas e margem mínima. (2) Sem base de reconhecimento de receita de êxito (contratado × recebido × reconhecido) nem tributos sobre o honorário da Save. (3) `premissas-financeiras.xlsx` vazio: custo técnico e imposto pendentes |
| `depto-ti` | 8 | 19 | 45 | intermediário | (1) Boa base (API do GLPI, NIST AI RMF, ISO/IEC 42001, CIS), mas sem data de consulta em boa parte. (2) Sem casos de incidente registrados (123 e-mails retidos e 11 chamados parados em 22/10). (3) Microsoft Graph e WhatsApp oficial sem especificação fechada |
| `gabinete` | 1 (roteador) | 12 | 35 | raso | (1) Matriz de roteamento não tem os produtos 2027 (P1 a P18) como temas. (2) Sem critério numérico de nível (R$ ou risco que sobe para o Conselho). (3) Sem casos de rota boa e rota ruim |
| `arquiteto-agentes` | 1 (mentor) | 12 | 25 | raso | (1) Contexto parado em 29/09 ("time de 4 pessoas, 4ª função não informada"). (2) Não conhece o padrão sênior nem a auditoria, que deveria ser dele. (3) `metodo.md` de 4 kB sem os aprendizados das 23 áreas |

**Média qualitativa: 40 (raso). Áreas no padrão: 0 de 23. Todas entram na fila de aprofundamento (limiar de 70).**

---

## 2. Área por área: equipe-alvo, conhecimento que falta e fontes que já existem

Regra de leitura: "Equipe-alvo" lista os arquivos que devem existir em `references/especialistas/`. "Falta" é conhecimento de domínio (norma, método, número de mercado), não forma. Norma marcada `[conferir]` foi lembrada por esta auditoria e precisa ser aberta no texto oficial antes de entrar na base. "Fontes internas" é o que já está no repositório e deveria alimentar o especialista.

### 2.1 `depto-tributario` (58, intermediário)
**Equipe-alvo (10):**
| Especialista | Entrega única |
|---|---|
| Alíquota Zero e PER | Ficha de aptidão T01/T09 por perfil (CNAE, CFOP, mercadoria), com risco do EREsp 2.215.482 e alternativa conservadora |
| Insumos PIS/COFINS | Matriz de essencialidade e relevância por item de custo (Tema 779 do STJ), com o registro da EFD que comprova |
| Exclusões da Base | Ficha de exclusão (ICMS Tema 69, ICMS-ST Tema 1.125, DIFAL Tema 1.372, ISS, própria base) com período e modulação |
| ICMS Estadual | Ficha de ST pago a maior, crédito acumulado e CIAP por UF, com a regra de monetização (LC 227/2026, arts. 132 a 141) |
| Previdenciário e Folha | Lista de verbas com tema (CPP verbas, T12) e período, pela folha e pelo eSocial |
| Agro | Crédito presumido de PF (Lei 10.925/2004, art. 8º) e triagem de Funrural como passivo (ADI 4.395, D86) |
| Reforma e Saldos Credores | Plano de saldos até 31/12/2026 e aditivo CBS/IBS (LC 214/2025 arts. 378 a 383; Decreto 12.955/2026 arts. 602 a 608) |
| Planejamento e Regimes (P8) | Simulação Real × Presumido × Simples híbrido, subvenções (Lei 14.789/2023), JCP, dividendos (Lei 15.270/2025) |
| SPED e Evidência | "O único documento que decide" por tese: registros da EFD-Contribuições, EFD ICMS/IPI, ECF e ECD |
| Jurisprudência e Modulação | Radar semanal com grau de risco e efeito na carteira (pauta da 1ª Seção, temas novos) |

**Falta:** método por tese (passo a passo e limites numéricos, como "faturamento mensal acima de R$ 300 mil" para Tema 69, que hoje só existe no catálogo); perguntas de diagnóstico ao contador do cliente; casos anonimizados das entregas de 14/10 (folha, passivo, PIS/COFINS, segmento) como referência; leiautes SPED; RICMS dos estados onde os Masters ganham (MG, SP, GO, MT, a confirmar no território); números de mercado (arrecadação por setor, carga média) com fonte. Corrigir o catálogo (Tema 1.079 no Funrural, já apontado).
**Fontes internas:** `references/radar-mercado.md` (40 kB, com confiança A/M/B) · `docs/portfolio-2027/agentes/tributario-revisao.md` (correções, calendário, riscos por tese, perguntas ao tributarista) · `departamentos/tributario/catalogo-teses-save-completo.md` (37 kB) · `docs/teses/funrural-adi-4395-estrategia.md` · `references/entendimento-save.md` (D14, D22) · entregas de 14 e 15/10 em `departamentos/tributario/entregas/` · decisões D80, D81 e D86.

### 2.2 `depto-juridico` (45, intermediário)
**Equipe-alvo (9):**
| Especialista | Entrega única |
|---|---|
| Prazos e PAF | Cálculo de prazo com dupla checagem (LC 227/2026 art. 173: 20 dias úteis; DTE; suspensão de 20/12 a 20/01) |
| Contencioso Administrativo | Estrutura da manifestação de inconformidade contra PER indeferido e do recurso ao CARF (voto de qualidade, Lei 14.689/2023) |
| Contencioso Judicial e MS | Parecer de via (MS individual, MS coletivo, ação) para as teses JUD do catálogo |
| Gestão de Passivo e Transação (P5) | Diagnóstico de passivo: débitos, modalidade (transação Lei 13.988/2020, editais PGFN, parcelamento), CND e garantia (LC 236/2026) |
| Estruturação Patrimonial e Sucessão (P10, N4) | Pré-análise de estrutura lícita: ITCMD a valor de mercado (LC 227/2026), ITBI na integralização (Tema 796), VGBL (Tema 1.214), dividendos (Lei 15.270/2025), fraude a credores (CC 158 a 165, CTN 185) |
| Perímetro Regulatório | Papel permitido da Save por produto (CVM 175, Lei 4.595/1964, Lei 7.492/1986, Res. CMN 4.935/2021, PLD Lei 9.613/1998) |
| Contratos, OAB e Canal | Estrutura da remuneração do parceiro (Lei 8.906/1994 art. 34, Provimento 205/2021, Lei 4.886/1965) e natureza jurídica da Save |
| LGPD e IA | Base legal, DPA e regras do WhatsApp; ANPD como agência |
| Apoio Jurídico Comercial | Briefing de reunião: o que pode e o que não pode ser dito, com a frase de uso externo |

**Falta:** tudo de P5 e P10 dentro da skill; alíquotas de ITCMD por estado (progressividade obrigatória pela EC 132/2023, a depender de lei estadual); quórum e prazos da recuperação extrajudicial (E9); 10 a 20 perguntas de diagnóstico de passivo e de patrimônio; casos (despacho decisório, compensação de ofício contestada, estrutura patrimonial refeita pela mudança do ITCMD); registro das decisões da casa (D14 PER, D80, D86) e da pergunta aberta sobre a natureza jurídica da Save (parecer previsto para 31/10).
**Fontes internas:** `references/radar-mercado.md` (37 kB) · `references/riscos-chave.md` · `docs/portfolio-2027/agentes/juridico-revisao.md` (56 kB: produto a produto, práticas proibidas, frases de uso externo) · `docs/portfolio-2027/fichas-sem-reuniao.md` (fichas 6, 7, 9 e 12) · `docs/portfolio-2027/consolidado-agentes.md` (E6 a E12, C1 e C2) · `celula-daniela/references/glpi-regras.md` (o que o Jurídico real pede) · entregas de 14 e 15/10 em `departamentos/juridico/entregas/`.

### 2.3 `depto-solucoes` (55, intermediário)
**Equipe-alvo (9):** Arquiteto de Esteira (mapa da conta em ondas) · Analista Financeiro do Cliente (leitura de DRE, balanço e SCR com os sinais de 13/10) · Especialista de Recebíveis e Gestão de Contas (elegibilidade P4 e P9, DSO, duplicata escritural, papel de indicadora; fronteira com a Save Invest reconstruída) · cinco especialistas setoriais com arquivo próprio (proteína animal, café e grãos, varejo alimentar, combustíveis e GLP, confecção e transporte) · Analista de Valor e QBR.
**Falta:** método do analista financeiro (índices, limites: FIDC acima de ~R$ 10 mi/mês de faturamento, custo do fundo de ~R$ 80 mil/mês, funding com ativos acima de ~R$ 60 mi, todos de reunião de 13/10 e sem D-número); taxa média de desconto de duplicatas e de capital de giro do BCB com data; jornada v2 e voto da seção 7 de `solucoes-jornada.md` para fechar o C7; regras D82 e D83 aplicadas a cada especialista; casos (o dossiê-modelo de 16/10, anonimizado).
**Fontes internas:** `references/playbooks-setoriais.md` (58 kB) · `references/esteira.md` e `demonstracao-valor.md` · `docs/portfolio-2027/agentes/solucoes-jornada.md` · `docs/ecossistema/` (racional e fechamento D1, handoff, modelo gestor de esteira, conexão com a base dos parceiros, roteiro de conversa com o empresário) · `departamentos/produtos/ecossistema-financeiro-reuniao-2026-10-13.md` · `docs/big-four/relatorio-big-four-x-save.md`.

### 2.4 `recuperador` (52, intermediário)
**Equipe-alvo (3):** Analista de Fila e Look-alike (fila priorizada) · Redator da Ficha de Reanálise (motivo provável, hipótese e documento que decide) · Analista de Recorrência (P2: competências novas e decadência mês a mês).
**Falta:** alinhar `matriz.json` às erratas E1 a E5 e às decisões D80 e D86 (com o Tributário); taxonomia dos motivos de perda com frequência real (dos vetos registrados em `aprendizados.md`); casos de reanálise aprovada e vetada; regra de urgência pós-31/12/2026 (fim do PIS/COFINS).
**Fontes internas:** SKILL.md (D1 a D6, D27) · `references/matriz.json` · `celulas/geovana/recuperador/aprendizados.md` · `tributario-revisao.md` (seções 2.3 e 4) · `consolidado-agentes.md` (E1 a E5, C4).

### 2.5 `revisor-diagnostico` (50, intermediário)
**Equipe-alvo (2):** Revisor de Lacunas por Perfil (planilha e fichas) · Curador da Matriz Tese × Perfil (dono das regras V1 a V15, com o Tributário).
**Falta:** confirmar no oficial os itens "confirmar" de `teses.json`; incluir DIFAL (Tema 1.372), ICMS-ST, própria base e ISS como lacunas possíveis; sinais financeiros no diagnóstico (pedido da reunião de 13/10); casos de "Incluir tese" e "Não se aplica".
**Fontes internas:** `references/teses.json` · `recuperador/references/matriz.json` · `celulas/geovana/revisor/aprendizados.md` e `decisoes.json` · `tributario-revisao.md` (seção 3, elegibilidade por segmento × regime).

### 2.6 `apresentacao-diagnostico` (38, raso)
**Equipe-alvo (3):** Editor Técnico do Diagnóstico (veredito MANTER, AJUSTAR, RETER ou RETIRAR por linha) · Roteirista Comercial (narrativa Destravar caixa, Proteger e controlar, Crescer, D1, e objeções por persona) · Curador de Cases (biblioteca anonimizada, com data-base e fonte).
**Falta:** método de narrativa e de objeções; regras de texto consolidadas com o Jurídico (parecer de 14/10) e o auditor; critérios dos produtos financeiros com D-número; casos das apresentações já feitas (anonimizados).
**Fontes internas:** `departamentos/tributario/apresentacao-diagnostico/FLUXO.md` e `MODELO-OXIGENAR-ESTRUTURAR-ESCALAR.md` · `biblioteca-cases/` · `departamentos/juridico/entregas/2026-10-14-padrao-apresentacao-diagnostico-compliance.md` · `docs/ecossistema/roteiro-conversa-empresario.md`.

### 2.7 `celula-daniela` (42, raso)
**Equipe-alvo (5):** Triagem e GLPI (ficha e categoria) · Gestor de SLA (cobrança agrupada) · Partner Account Manager (plano de conta, QBR e JBP por Master) · Registro de Oportunidade e CRM (proposta checada na Receita) · Apoio Jurídico ao Master (tradução de pré-análise).
**Falta:** SLA validado (Semana 0); método de plano de conta com metas por Master (dependem da meta 2027); perguntas de diagnóstico de saúde do Master; casos de demanda bem e mal roteada (do GLPI real); regra de clientes sem Master (folha de 22/10, item 3).
**Fontes internas:** `references/glpi-regras.md` (1.115 chamados lidos) · `references/sla.md` · `celulas/daniela/aprendizados.md` e `padroes-resposta.md` · `depto-partner-success/references/boas-praticas.md` (JBP, QBR) · `depto-dados` (scorecard).

### 2.8 `celula-jenifer` (45, intermediário)
**Equipe-alvo (5):** Pesquisador de Contas-Alvo (lista por Master, segmento e UF) · Qualificador R-D-A-C-H-U (SQL) · Redator de Cadência por Persona (com objeções) · Recrutador de Indicadores (escritórios contábeis) · Distribuição e Registro no Master.
**Falta:** LIA de legítimo interesse validada pelo Jurídico; objeções técnicas por persona com base (contador que resiste, CFO que já recuperou); referências de cadência com fonte e data; ICP por produto (2027) além da recuperação; D7-b e a regra do café formalizadas.
**Fontes internas:** `references/criterios-qualificacao.md`, `cadencia.md`, `modelos-mensagem.md` · `intel-comercial-icp.md` (seções 2, 4 e 5) · `depto-partner-success/references/radar-mercado.md` (seção 3, BDR) · `celulas/jenifer/config-jenifer.json` e `aprendizados.md`.

### 2.9 `central-agentes` (30, raso)
**Equipe-alvo (2):** Triador de Pedidos por E-mail (rota para a área) · Redator da Resposta em 3 Blocos.
**Falta:** critério de triagem por tipo de pedido; casos de resposta aprovada e reprovada; regra de escalonamento ao Gabinete. Não precisa de domínio técnico próprio: o domínio é das áreas.
**Fontes internas:** `references/catalogo.json` · `infra/fluxo-unico.md`, `infra/padrao-entrega.md`, `infra/chamado-ideal.md` · `central-agentes/aprendizados.md`.

### 2.10 `conselho-partners` (25, raso)
**Equipe-alvo (7):** Presidente (ata e decisões) e seis conselheiros com arquivo sênior: Estratégia (portfólio e sequência), Comercial e Canal (economia do programa de parceiros), Operações e Tecnologia (SLA, GLPI, IA), Pessoas, Finanças (unit economics da Save), Risco Tributário e Jurídico.
**Falta:** frameworks e números por conselheiro (por exemplo, para Finanças: honorário realizado de 25,0% do crédito, repasse de 30,7%, receita por cliente em 24 meses por porte, meta 2027 de R$ 49,8 mi, todos de `consolidado-agentes.md`, marcados como hipótese); histórico de decisões D1 a D91 resumido por tema; casos de decisão revista.
**Fontes internas:** `conselho/decisoes.md` e atas · `docs/revisao-2026-10-22/decisoes-pendentes.md` · `docs/portfolio-2027/consolidado-agentes.md` · `docs/big-four/relatorio-big-four-x-save.md` · radares das áreas.

### 2.11 `depto-contratos` (32, raso)
**Equipe-alvo (5):** Biblioteca de Modelos por Produto (modelo aprovado P1 a P18, com versão e aprovador) · Conferente de Dados · Controle de Assinaturas · Distratos e Honorário sobre PER transmitido · Aditivos (CBS/IBS, escopo de tese).
**Falta:** os modelos em si (pedido à área real); contratos dos produtos 2027 (mandato de cobrança, indicação, DPA, contrato do escritório para P10, termo de ciência da antecipação); base de assinatura eletrônica conferida; perguntas da conferência; casos de distrato.
**Fontes internas:** `references/montador-minuta.md`, `distratos.md`, `checklist-conferencia.md` · `juridico-revisao.md` (coluna "Contratos" de cada produto) · `departamentos/contratos/perguntas-areas.md` e os três controles de 29/09, 12/10 e 19/10.

### 2.12 `depto-dados` (22, raso)
**Equipe-alvo (4):** Guardião de Qualidade do CRM (lista de correção com link) · Arquiteto do Modelo de Dados (dicionário de campos, propriedades novas como "produto de entrada") · Analista de Saúde do Parceiro (índice e componentes) · Analista de Forecast.
**Falta:** dicionário próprio dos campos do HubSpot; método de deduplicação por raiz de CNPJ com regra de sobrevivência; boas práticas de governança de dados (DAMA-DMBOK) aplicadas; casos (importações de nov/2025 e fev/2026 que regravaram datas).
**Fontes internas:** `departamentos/resultados/mapeamento-hubspot.json` · `depto-resultados/references/metricas.md` · `scripts/ganhos_a_completar.py` (D62, D71, D73) · `solucoes-jornada.md` (seção 3.1, campos novos).

### 2.13 `depto-intel-comercial` (35, raso)
**Equipe-alvo (5):** Arquiteto de ICP por Produto · Minerador de Dados Públicos (tamanho de mercado por CNAE × UF × regime) · Analista de Sinais (financeiros e regulatórios) · Analista de Concorrência e Benchmarks de Fee · Planejador de Territórios e Recrutamento.
**Falta:** ligar o ICP de 22/10 à skill; número de empresas no Lucro Real por segmento e UF (Receita, dados abertos) com data; dados de safra e de setor (CONAB, IBGE); base de concorrentes com fonte pública; regra do conflito C4 (supermercado).
**Fontes internas:** `docs/portfolio-2027/agentes/intel-comercial-icp.md` · `departamentos/intel-comercial/receita-config.json` e ICPs gerados · `docs/ecossistema/conexao-base-parceiros.md` · `depto-partner-success/references/radar-mercado.md` (mercado contábil).

### 2.14 `depto-marketing` (30, raso)
**Equipe-alvo (6):** Estrategista de Campanha · Redator Técnico-Comercial · Designer do Design System Save · Enablement por Tese (peça) · Compliance de Publicidade (OAB, CONAR, Meta) · Curador do Jornal.
**Falta:** Provimento 205/2021 e Código de Ética da OAB aplicados a peça; CONAR; política de modelos e opt-in do WhatsApp Business; calendário fiscal datado (ECD, ECF, DCTFWeb, IRPF) com fonte; métricas de marketing de canal com benchmark; casos de peça reprovada pelo auditor.
**Fontes internas:** `references/marca-save.md`, `equipe.md`, `jornal.md` · `departamentos/marketing-marca/padrao/` (Design System Save v0.5) · `juridico-revisao.md` (frases proibidas e permitidas) · `depto-qualidade/references/regras-promessas.json` · radar comercial (seção 4).

### 2.15 `depto-operacoes-canal` (40, raso)
**Equipe-alvo (4):** Analista de Comissionamento (conferência e provisão) · Política do Programa e Termos (regra de registro, D78, D61) · Elegibilidade e Retenções (termo, NF, retenções) · Registro e Conflito de Canal.
**Falta:** fontes datadas para as boas práticas; Lei 4.886/1965 e Res. CMN 4.935/2021 (C1); retenções sobre a NF do parceiro por tipo de serviço e regime, validadas pelo Tributário; a política vigente e o histórico de repasse (inversão 70/30); casos de contestação.
**Fontes internas:** `references/boas-praticas.md`, `checagens-repasse.md`, `config-canal.json` · `departamentos/operacoes-canal/percentual-parceiros.json` e proposta de regra · `consolidado-agentes.md` (C1, C2) · `precos-fees.md` (remuneração).

### 2.16 `depto-partner-success` (45, intermediário)
**Equipe-alvo (4):** Designer da Academia (módulo por tese e por produto) · Coach de Onboarding 30/60/90 · Gestor de Níveis e Benefícios · Analista de Ativação.
**Falta:** currículo por tese com o conteúdo do Tributário; decisão dos níveis L1 a L10; casos de parceiro ativado e reativado; enablement dos produtos 2027 (o que o parceiro pode e não pode dizer).
**Fontes internas:** `references/radar-mercado.md` (47 kB) · `references/boas-praticas.md` · `entregas/2026-09-29-v1/programa-niveis-v1.md` · `intel-comercial-icp.md` (seção 4.4) · `departamentos/produtos/fontes-produtos-guia-parceiro.md`.

### 2.17 `depto-pessoas` (30, raso)
**Equipe-alvo (4):** Metas e Variável · Feedback e PDI · Cargos e Carreira · Guardião CLT e LGPD.
**Falta:** CLT arts. 457 e 461, Lei 10.101/2000 e Lei 14.611/2023 com artigo e risco; referência salarial com fonte e data; exemplos preenchidos de PDI, metas e 1:1; casos. Mantém a regra: decisão sobre pessoas é do Luis e do RH formal.
**Fontes internas:** `references/equipe.md` e `modelos.md` · `ESTADO.md` (funções) · radar comercial (seção 6, pessoas) · `mapa-de-tarefas-v2.xlsx` (carga).

### 2.18 `depto-pos-venda` (45, intermediário)
**Equipe-alvo (4):** Ressarcimento e PER (do pedido à ordem bancária) · Compensação de Ofício · Extrato e Saldo · Aviso de Honorário.
**Falta:** prazo de 360 dias e Selic (Lei 11.457/2007 art. 24; STJ Tema 1.003) [conferir]; procedimento especial de ressarcimento e motivos comuns de indeferimento; fonte de valor recebido; casos de compensação de ofício contestada.
**Fontes internas:** `references/compensacao-de-oficio.md` (base normativa boa) · `calendario-mensal.md`, `sistemas-e-dados.md` · `depto-juridico/references/riscos-chave.md` · `celula-daniela/references/glpi-regras.md` (categorias Execução e Compensação).

### 2.19 `depto-qualidade` (48, intermediário)
**Equipe-alvo (4):** Auditor de Promessas · Analista de Reclamações e Causa-raiz · Pesquisador de NPS, CSAT e CES · Ouvidor (ISO 10002).
**Falta:** catálogo de falsos positivos por tipo de material; base de publicidade compartilhada com Marketing; casos de reclamação tratada; série histórica (depende do GLPI).
**Fontes internas:** `references/auditoria-promessas.md`, `regras-promessas.json`, `reclamacoes.md`, `ouvidoria.md`, `nps-csat.md` · `juridico-revisao.md` (frases).

### 2.20 `depto-resultados` (42, raso)
**Equipe-alvo (5):** Controller de Margem · Analista de Preço e Fee · Analista de Receita Reconhecida e Caixa · Analista de Forecast e Meta 2027 · Redator Executivo.
**Falta:** tabela de preço (escala 30/25/20%, piso de 20%, cestas com teto de 10% e 15%, margem mínima de 20%, todos [HIPÓTESE] de 22/10); reconhecimento de receita de êxito e tributos sobre o honorário; premissas financeiras preenchidas; benchmarks de fee de mercado.
**Fontes internas:** `references/metricas.md` (D16, D17) · `docs/portfolio-2027/agentes/precos-fees.md` · `departamentos/resultados/planejamento-2027/` · `consolidado-agentes.md` (seção 2.4).

### 2.21 `depto-ti` (45, intermediário)
**Equipe-alvo (5):** Arquiteto de Integrações (Graph, GLPI, Eazybe, Bitrix) · Administrador do GLPI · Segurança e Acessos · Governança de IA · Operação e Continuidade.
**Falta:** datas de consulta nas fontes técnicas; casos de incidente (e-mails retidos, chamados parados, `master-sync`); especificação fechada do Graph e do WhatsApp oficial.
**Fontes internas:** `references/glpi-api.md`, `governanca-ia.md`, `seguranca-lgpd.md` · `departamentos/ti/` (GLPI pronto, inventário, aprendizados, integrações Microsoft) · `docs/GLPI.md`, `docs/sso-entra/`, `docs/whatsapp-webhook.md`.

### 2.22 `gabinete` (35, raso)
**Equipe-alvo (2):** Roteador (Ficha de Rota) · Consolidador (parecer único).
**Falta:** produtos P1 a P18 na matriz de roteamento; limite numérico para subir de nível; casos de rota.
**Fontes internas:** `references/matriz-roteamento.md` · `docs/portfolio-2027/matriz-agentes.md` · `infra/porteiro.md` · `gabinete/SESSOES.md`.

### 2.23 `arquiteto-agentes` (25, raso)
**Equipe-alvo (2):** Mentor do Método (fases 0 a 7) · Guardião do Padrão Sênior (dono desta auditoria e do modelo de especialista).
**Falta:** atualizar o contexto do time; incorporar o padrão sênior, o protocolo do gerente e a auditoria; casos das 23 áreas construídas.
**Fontes internas:** `infra/padrao-senior.md`, `protocolo-gerente.md`, `protocolo-pesquisa.md` · `docs/revisao-2026-10-15/estrutura-agentes-avaliacao.md` · `docs/revisao-2026-10-08/` · `DEPARTAMENTOS.md`, `ARQUITETURA.md`.

---

## 3. Cruzamento com o portfólio 2027 (`docs/portfolio-2027/matriz-agentes.md`)

Produto **pronto** sem especialista sênior responsável (todos, porque nenhum arquivo de especialista existe). A coluna "Gravidade" diz o quanto a base atual cobre o produto.

| # | Produto pronto | Agente responsável na matriz | Especialista que deveria responder | Gravidade |
|---|---|---|---|---|
| P1 | Recuperação tributária (T01 a T19) | `depto-tributario`, `recuperador` | Alíquota Zero e PER; Insumos; Exclusões; ICMS; Previdenciário | **Média:** base existe no radar e no catálogo, sem método por tese; matriz do Recuperador desatualizada (E1 a E5) |
| P2 | Recorrência | `depto-tributario` | Analista de Recorrência (`recuperador`) | Média: regra de fila, sem dono |
| P3 | Crédito presumido de PF e Funrural | `depto-tributario` (Agro) | Agro; Gestão de Passivo (Funrural, D86) | **Alta:** Agro é uma linha; Funrural mudou de classe e nenhum especialista do Jurídico o recebeu |
| P4 | Gestão de Contas | `depto-solucoes`, `depto-internacional` | Especialista de Recebíveis e Gestão de Contas | **Alta:** um dono em reconstrução e outro que só aponta; quem contrata e quem presta segue em aberto |
| P5 | Gestão de Passivo | `depto-juridico`, `depto-tributario` | Gestão de Passivo e Transação | **Crítica:** nenhum conteúdo na skill; editais da PGFN vencem em 20/12/2026 e 29/01/2027 |
| P7 | Produtos jurídicos | `depto-juridico` | Contencioso Administrativo e Judicial | Alta: produto sem ficha definida; os especialistas existem só como linha |
| P8 | Planejamento tributário e reforma | `depto-tributario` (Reforma) | Reforma e Saldos Credores; Planejamento e Regimes | **Alta:** 1,9 kB de base para o produto com urgência até 31/12/2026 |
| P9 | Antecipação de recebíveis | `depto-internacional` | Especialista de Recebíveis (Soluções) + Perímetro Regulatório (Jurídico) | Alta: depende da reconstrução da Save Invest |
| P10 | Estruturação patrimonial e empresarial | `depto-juridico` | Estruturação Patrimonial e Sucessão | **Crítica:** zero de conteúdo na skill; mudança do ITCMD (LC 227/2026) e dos dividendos (Lei 15.270/2025) mexe em toda estrutura antiga |
| P13 | FIDC | `depto-internacional` | (reconstrução) + Perímetro Regulatório | Alta: depende da reconstrução; art. 42 do Anexo II da CVM 175 (E13) só no consolidado |
| P18 | Tax internacional e comércio exterior | `depto-internacional` | (reconstrução) + Tributário (preço de transferência é só triagem) | Alta: o Tributário declara preço de transferência "fora" |

**Camada de apoio com lacuna que trava produto pronto:** `depto-contratos` não tem modelo aprovado de nenhum produto; `depto-operacoes-canal` não tem a política dos produtos 2027 (D78); `depto-resultados` não ligou a tabela de preço. Os três precisam entrar junto com os produtos na Onda 2.

**Recomendação para a reconstrução de `depto-internacional` e `depto-save-invest`:** nascer já com `references/especialistas/` no padrão e cobrir P4, P9, P13 e P18, com fronteira escrita com Soluções (esteira) e Jurídico (perímetro regulatório).

---

## 4. Ordem de aprofundamento em ondas

Critério: impacto em receita e risco primeiro; depois o que trava a venda dos produtos prontos; por último a gestão e a orquestração. Estimativa por arquivo de especialista: cerca de 2,5 h de agente nas áreas técnicas (pesquisa no oficial + redação das 10 seções) e 1,5 h nas demais, mais 30 a 45 min de validação do dono humano. Tudo que for norma lembrada passa pelo texto oficial antes de entrar.

| Onda | Quando | Áreas e especialistas | Arquivos | Esforço de agente | Esforço humano | Por que agora |
|---|---|---|---|---|---|---|
| **0 · Base comum** | 23 e 24/10 | Modelo `_modelo.md` do especialista; `perguntas-ao-dono.md` por área; ligar às skills os 6 documentos de `docs/portfolio-2027/agentes/`; o `arquiteto-agentes` vira dono do padrão | 1 modelo + 23 listas | 4 h | Luis 30 min | Sem modelo, cada área escreve diferente e a auditoria não compara |
| **1 · Receita e risco imediatos** | 27/10 a 07/11 | **Jurídico:** Gestão de Passivo, Estruturação Patrimonial, Prazos e PAF, Contencioso Administrativo, Perímetro Regulatório · **Tributário:** Alíquota Zero e PER, Reforma e Saldos Credores, Insumos, Exclusões, Agro, SPED e Evidência · **Pós-venda:** Ressarcimento e PER, Compensação de Ofício · **Recuperador e Revisor:** Curador da Matriz, Analista de Recorrência | 15 | ~38 h (2 semanas, áreas em paralelo) | Tributarista 4 h · advogado 4 h · Geovana 2 h | P5 e P10 são produtos prontos sem base; prazo de crédito de PIS/COFINS em 31/12/2026; editais da PGFN; EREsp 2.215.482 define ~99% do valor ganho; o ressarcimento é o caixa |
| **2 · Vender os produtos prontos pelo canal** | 10 a 28/11 | Restante do Tributário (ICMS, Previdenciário, Planejamento e Regimes, Jurisprudência) e do Jurídico (Contencioso Judicial, Contratos e OAB, LGPD, Apoio Comercial) · Soluções (9) · Contratos (5) · Operações de Canal (4) · Intel Comercial (5) · Apresentação do Diagnóstico (3) · restantes do Recuperador e do Revisor (3) | 37 | ~80 h | Luis 4 h · Daniela 2 h · Júnior (Save Invest) 2 h · área de Contratos 2 h | Sem modelo de contrato, política de remuneração e ICP por produto, o produto pronto não chega ao parceiro; janela de 2027 |
| **3 · Canal, pós-venda e gestão** | 01 a 19/12 | Célula Daniela (5) · Célula Jenifer (5) · Partner Success (4) · Resultados (5) · Dados (4) · Qualidade (4) · Pós-venda restante (2) | 29 | ~45 h | Luis 3 h · Daniela 2 h · Jenifer 2 h | Ativa a rede para 2027 e fecha preço, margem e dado confiável |
| **4 · Suporte e orquestração** | jan/2027 | Marketing (6) · TI (5) · Pessoas (4) · Conselho (7) · Gabinete (2) · Central (2) · Arquiteto (2) | 28 | ~42 h | Luis 3 h · TI 1 h | Áreas que dependem do conteúdo das ondas anteriores (peça, roteamento, conselho) |

**Total:** cerca de 109 arquivos de especialista, perto de 210 h de agente e 35 h de pessoas, em 10 semanas. Meta de controle: Onda 1 com nota de script acima de 70 em Tributário, Jurídico e Pós-venda até 07/11; consolidação de sexta mostra a evolução (`python3 infra/auditar_senioridade.py --json`).

**Perguntas que destravam a Onda 1 (para o Luis):**
1. O Jurídico real valida Gestão de Passivo e Estruturação Patrimonial nesta ordem, até 07/11?
2. Quem do time técnico revisa os especialistas de Alíquota Zero e de Reforma (30 a 45 min cada)?
3. A Save Invest reconstruída assume P4, P9 e P13, e Soluções fica só com a esteira e a elegibilidade? (define a fronteira antes de escrever)

---

## Registro
- Script: `infra/auditar_senioridade.py` (rodado em 22/10/2026; 23 áreas; média 17; 0 no padrão).
- Leitura: SKILL.md e references das 23 áreas; `docs/portfolio-2027/` (matriz, consolidado e os 6 documentos dos agentes); `docs/revisao-2026-10-22/decisoes-pendentes.md`; `departamentos/produtos/ecossistema-financeiro-reuniao-2026-10-13.md`; catálogo de teses; listagem das pastas de trabalho em `~/agentes-partners/departamentos/` (só nomes e contagens, sem abrir dado de cliente).
- Limites: as normas citadas nesta auditoria não foram abertas no texto oficial hoje; as marcadas `[conferir]` vieram da memória do auditor. As notas qualitativas são julgamento desta leitura, para ordenar o trabalho, e não substituem a nota do script.
