# Projeto Agentes Partners — Estado

**Fase atual:** 1 — Diagnóstico (time) · em paralelo: Conselho do Luis em Fase 5 (construção v1 pronta, falta teste real)
**Última atualização:** 2026-09-29

## Checklist para 100% rodando (revisão de 29/09)
**Bloqueios de terceiros:** escopo `files` no HubSpot (CRM) · links públicos do Bitrix24 (TI) · obrigatoriedade dos campos de pagamento/% honorário (CRM, D18) · validação LGPD de contatos · marca-save.md (Marketing) · estrutura societária × remuneração de parceiros (Jurídico).
**Decisões do Luis:** D7-b a D15 (exceto D14) · e-mail/cópia/frequência da Geovana · honorários >50% · campos honorarios_vendedor/gestor/indicador · horário do Conselho semanal · rotina do Jornal · refresh mensal da Receita · plano G.S.H/JGM.
**Pessoas:** Semana 0 com a Geovana · mapa de tarefas do time (5 dias úteis) → Fase 2 · levantamento do GLPI.
**Construção:** células Daniela e Jenifer · deptos Partner Success, Operações de Canal & Comissionamento, TI/GLPI, Contratos, Pós-venda, Qualidade · Revisor de Diagnóstico (2ª onda Geovana) · agendamentos (Conselho, Jornal, Recuperador, Receita) · canal de acesso (WhatsApp/app/nuvem).
**Infra:** launchd com.savecompany.master-sync falhando (exit 127, ~/soe-agent apagado) · backup de ~/.claude/skills e ~/agentes-partners · agendamentos dependem do Mac ligado e do app aberto.

**Feito em 29/09 (tarde):** cockpit master-sync desligado (plist movido para ~/Library/LaunchAgents/desativados/, reversível) · backup diário 19h30 no OneDrive da Save (infra/backup.sh, 30 versões, sem .env e sem a base da Receita) · PDF residual removido (texto preservado) · agendadas: Conselho semanal (seg 7h30) e Recuperador lote semanal (seg 8h, rascunho só para o Luis até confirmar o e-mail da Geovana) · pareceres.py ganhou OCR local (Vision do macOS), Excel, texto puro e modo --todos (leitura de toda a base via Bitrix; os 625 hospedados no HubSpot continuam dependendo do escopo files) · células Daniela e Jenifer em construção (v1).

**Feito em 29/09 (noite):** construídos em v1 e testados com dados reais: `celula-daniela`, `celula-jenifer`, `revisor-diagnostico`, `depto-ti` (GLPI pronto para agente, inventário de agentes, chamados em rascunho), `depto-partner-success`, `depto-operacoes-canal`, `depto-contratos`, `depto-pos-venda`, `depto-qualidade`. Gabinete, matriz de roteamento, ARQUITETURA e DEPARTAMENTOS atualizados. **WhatsApp:** caminho escolhido = Eazybe (já conectado ao HubSpot). O token atual lê as atividades WHATS_APP (individuais e grupos, gravadas minutos depois); `whatsapp_hubspot.py --pessoa daniela|jenifer|geovana` monta a caixa local só de leitura. OpenWA descartado por enquanto (não oficial, risco de banimento). A Geovana tem só 1 registro em 30 dias: o WhatsApp dela provavelmente não está conectado ao Eazybe.

**Pareceres (30/09, 2ª checagem):** 4.526 textos lidos via Bitrix, 3.970 com conteúdo (556 são "Não tem.txt"); 1.865 negócios com parecer real. Os 2.241 arquivos no HubSpot (1.090 negócios) não têm equivalente em link do Bitrix; 486 deles têm id_bitrix → dá para ler pela API do Bitrix se o TI criar um webhook só de leitura. Os outros 604 dependem do escopo files.ui_hidden.read do HubSpot.

**MVP ambiente do time (30/09):** pasta OneDrive "Área Partners · Agentes" (4 subpastas por pessoa; `infra/publicar_onedrive.py`, planilhas de trabalho em sincronia nos dois sentidos, md→docx) + portal Central Partners (artifact https://claude.ai/artifact/7fgGfrK7zVqzjcXCscJmwb, dados de `infra/portal_dados.py`). Ambos atualizados pela rotina do WhatsApp 4x ao dia. Falta: Luis compartilhar pastas/portal; validação do Comitê (TI, Jurídico, Dados, Pessoas) aprovada na Ficha de Rota.

**Chatbot de pedidos (30/09):** aba "Pedidos" no portal: assistente com o Claude da conta de quem usa (capacidade sample, sem custo de servidor), registro compartilhado (db, coleção `pedidos`), status Aceitar/Em andamento/Concluir/Não é comigo. A rotina do WhatsApp 4x ao dia lê os pedidos abertos e inclui no e-mail de cada responsável. Sem dados bancários/CPF no chat.

**Central de Agentes por e-mail (30/09, D24):** skill `central-agentes` + rotina a cada 30 min (dias úteis 8h–18h). Pedido: e-mail para luis.melo@ com [AGENTES] no assunto, modelo de 8 campos (Modelo de pedido aos agentes.eml e catálogo .docx em cada pasta do OneDrive); 20 tipos no catálogo (DM, JB, GT, GE). Resposta no layout da área; aprovação por "Aprovado / Não aprovado / Nova análise". Chatbot do portal desativado.

**Operação pelo terminal (30/09):** comando `bin/partners` + 5 jobs launchd (`com.savecompany.partners.*`: manha 7h30, caixa 7h45/13h45, whatsapp-auto 11h/17h sem IA, central a cada 15 min, segunda 6h). Rotinas do Claude enxugadas: Central de hora em hora só com fila; WhatsApp com IA 8h e 14h; relatório, Recuperador e Conselho às segundas usando o que o terminal preparou. `claude -p` (Claude pelo terminal) bloqueado por crédito da conta: pedir ao admin. Mapa em README.md, operação em RUNBOOK.md.

**Revisão de redundância (01/10, TI + Dados):** feito: 1 download HubSpot/dia (calc_semana reaproveita), espera de rede + retry, corrente para se o download falhar, alerta de falha por e-mail, caixa sem leitura dupla, rodadas sem IA só com novidade e sem resumo geral, 1 credencial HubSpot (whatsapp_hubspot importa hubspot_fonte), sem chamadas de contatos, trava na fila da Central, Central em horários fixos de 15 min, Recuperador às 9h, relatórios das áreas na segunda, alerta de Qualidade lido da auditoria, lib/partners_dados.py (fonte única, migração gradual), registro único de demandas (lib/registro_demandas.py → Demandas.xlsx por pessoa + portal). Pendente (Dados): migrar os demais scripts para lib/partners_dados.py (roster/aliases únicos, conflito de canal único, café, segmento, data efetiva), decisões persistentes na fila do Recuperador com nome fixo, painel semanal único do Luis. Pendente (Luis/TI): desligar Control Chrome, Bright Data e Google; `pmset`; URLs públicas dos anexos do Eazybe; Microsoft 365; escopo de arquivos do HubSpot (ainda MISSING_SCOPES em 01/10).

**Preparação para a nuvem (01/10):** repositório git local só de código (2 commits, 166 arquivos, barreira de LGPD no pre-commit), lib/graph.py (e-mail e SharePoint pelo Graph, desligado), lib/estado.py (memória entre rodadas no SharePoint), OCR Tesseract fora do Mac, 7 workflows do GitHub Actions desligados (AGENTES_NUVEM/AGENTES_IA), trava .nuvem-ligada no Mac. Passo a passo em docs/NUVEM.md. Falta: repositório privado na organização da Save no GitHub, Microsoft Graph/SharePoint (TI), crédito do Claude para as partes com IA.

## Próximo passo
- Luis fecha a planilha antiga e envia `mapa-de-tarefas-v2.xlsx` (abas com nomes e exemplos de cada uma) + mensagem ao time.
- Primeiro teste real do Departamento de Marketing (ex.: cronograma de datas festivas 2027).
- Validar `marca-save.md` com a área de Marketing da Save (dono humano do departamento).
- ✅ 28/09: HubSpot conectado (token em `~/agentes-partners/.env`, validado). Edição 2 do relatório gerada 100% com HubSpot (4.857 negócios, regra do café aplicada). Campos mapeados: nome_do_parceiro (via roster de consultores), descricao_do_cnae, honorarios_contratuais, honorarios_parceiro, teses_tributarias_aplicadas_neste_negocio_. Achados: 99% do valor ganho com tese = PIS/COFINS nas aquisições; % honorário em só 42% dos ganhos; campos de pagamento 100% vazios; 61 honorários acima de 50%. Custos da área vindos do BI do Luis (aba 'Custos BI (mensal)' da premissas-financeiras.xlsx; jul–ago realizado, set orçado); relatório calcula ANTES de impostos (decisão do Luis 28/09). Jul–set: lucro a.i. R$ 17,7 mi, ROI líquido 65x (potencial). Pendente: Luis confirmar escopo/roster e o significado dos campos honorarios_vendedor/gestor_comercial/indicador (descontar da margem?). Descoberto em 28/09: a pasta `~/soe-agent` foi apagada (código + .env); o launchd `com.savecompany.master-sync` segue rodando e falhando → o cockpit parou em 31/08.
- ✅ Depto Resultados & Controladoria (28/09): skill `depto-resultados` (calc_semana.py determinístico + gen_deck.js) + premissas-financeiras.xlsx; edição 1 do relatório semanal em `departamentos/resultados/relatorios/`. Pendências: Luis preencher premissas; religar automação do cockpit (parado desde 31/08); atualizar base de margem do S&OE (parada desde 25/05; 10 repasses com erro ×10.000); fonte de recebimentos com o Financeiro; aprovar agendamento semanal (proposta: segunda 06h30, antes do Conselho às 07h).
- ✅ 2º teste (28/09): plano Q4 "Feche 2026, prepare 2027" → viabilidade de 4 frentes (Tributário, Jurídico, Intel+Marketing, células) → Conselho com Rodada 2 → ata `conselho/atas/2026-09-28-q4-mercados.md`, decisões D7–D13 pendentes → Word `Plano-Q4-2026-Feche2026-Prepare2027.docx`.
- ✅ 1º teste do Conselho feito (28/09): consulta sobre o piloto da Geovana → ata `conselho/atas/2026-09-28-piloto-geovana.md`, decisões D1–D6 pendentes e 3 dúvidas bloqueantes para o Luis.
- Luis aprova dia/horário da reunião semanal automática (proposta: segunda 07h) → criar tarefa agendada.
- Luis confirma o retrato da operação abaixo (Fase 0) e envia `mensagem-time.md` + `mapa-de-tarefas.xlsx` ao time.
- Time registra tarefas por 5 dias úteis.
- Em paralelo: Luis levanta como o GLPI está sendo configurado (categorias, campos, filas por área, quem é o responsável, se tem API). Decidir se o desenho do GLPI deve já nascer "pronto para agente".
- Depois: Fase 2 (priorização) com as planilhas preenchidas.

## Retrato da operação (Fase 0)
A área Partners funciona como **central de recepção e roteamento**: recebe a demanda do parceiro, encaminha para a área de apoio, acompanha diariamente e devolve o status ao parceiro. O trabalho do time é majoritariamente de "ponte", braçal.

### Time
| Pessoa | Função (confirmada 2026-09-28) | Formação | Célula de agentes | Curadora de departamento |
|---|---|---|---|---|
| Daniela Maciel | Ponto focal dos 9 parceiros Masters; mais tempo de casa e relacionamento; apoio em necessidades gerais | Advogada | Central Masters (Gestão de Contas) | Jurídico, Partner Success |
| Geovana Gonçalves | Suporte técnico comercial: reuniões técnicas, dúvidas fiscais; revisa negócios em apresentação de diagnóstico (oportunidades não pegas) e perdidos/zerados (reanálise) | Contadora | Central Técnica | Tributário & Contábil |
| Jenifer Carvalho | BDR dos Masters: prospecta clientes em segmentos-chave e novos parceiros indicadores | — | Central BDR | Inteligência Comercial |
| Luis | Gerente comercial Masters: gestão das 3 + relacionamento com parceiros estratégicos | — | Conselho Consultivo | — |

### Canais de entrada das demandas
- **WhatsApp** (canal atual, principal). Sem integração: o agente só "lê" se a conversa for colada/exportada.
- **GLPI** (em estruturação). Sistema de chamados: se tiver API, o agente pode ler e registrar chamados. Durante a transição as demandas chegarão pelos dois canais.

### Áreas de apoio (para onde as demandas são roteadas)
| Área | O que faz pelos parceiros |
|---|---|
| Técnico tributário | Análise das empresas, pareceres e relatórios para os clientes; execução dos trabalhos fechados |
| Jurídico | Contratos, notificações da RFB, apoio jurídico em reuniões |
| Contratos | Envio e controle de contratos e distratos |
| Pós-venda | Avisos mensais de pagamento, compensações de ofício, controle de guias a compensar, extrato de pagamento e saldo de créditos |
| Marketing | Materiais comerciais |

### Ferramentas
WhatsApp, GLPI (novo), HubSpot (portal 47865021), dashboard S&OE, cockpit Master, save-crm, ~/soe-agent/.

## Aprendizados do 1º teste (28/09)
- Fluxo completo funcionou: dossiê → embasamento Tributário + Jurídico (fontes oficiais) → 6 pareceres independentes → ata com decisões.
- Achado de maior valor veio do embasamento: janela até dez/2026 (fim do PIS/COFINS) + decadência mensal.
- 2º teste: pedir a cada conselheiro o "argumento mais forte contra a própria posição" gerou divergência real e Rodada 2 útil (Estratégia e Finanças mudaram de posição). Incorporar ao formato do parecer.
- Ajustes a considerar: conselheiros convergiram muito (avaliar um papel de "advogado do diabo"); falta HubSpot ao vivo; KPIs manuais vazios limitam a análise.

## Hipóteses (a validar na Fase 2 com dados)
- **Candidatos a piloto:** (a) Geovana: Revisor de Diagnóstico + Recuperador de Perdidos/Zerados → impacto direto em receita, KPIs já existem no cockpit (valor recuperado, taxa de reversão); (b) Daniela: Triagem & Acompanhamento → horas liberadas. Tendência: (a), porque receita convence a liderança mais que horas.
- O maior ganho está no fluxo de "ponte" (recepção → encaminhamento → acompanhamento → retorno), comum às 3 pessoas. Isso sugere um **agente de Triagem e Acompanhamento de Demandas** como piloto, em vez de um agente por pessoa.
- A implantação do GLPI é a oportunidade de desenhar categorias e campos que já sirvam ao agente (ex.: categoria = área de apoio; campos obrigatórios por tipo de pedido).

## Decisões tomadas
- 2026-09-28 — Objetivo: escalar a operação e tornar o time estratégico; motivação: posicionamento como HIC (High-Impact Individual Contributor).
- 2026-09-28 — Estrutura proposta inicial: 4 agentes (Suporte Técnico, Operacional, Prospecção, Gestor) sobre uma base de conhecimento comum. **Revisitar na Fase 2** à luz do modelo de roteamento.
- 2026-09-28 — Criado o agente-mentor `arquiteto-agentes` (skill do Claude) para conduzir o projeto.
- 2026-09-28 — A 4ª pessoa é o próprio Luis (gerente comercial Masters).
- 2026-09-28 — **Governança:** nenhum agente ou subagente executa nada sem validação humana. Todos em N1, sem exceção, até decisão explícita do Luis.
- 2026-09-28 — **Estrutura por organograma:** cada pessoa (Daniela, Geovana, Jenifer) tem uma célula = agente orquestrador + subagentes especialistas nas áreas de apoio; Luis gestor de toda a operação. Base de conhecimento das áreas de apoio é compartilhada entre as células.
- 2026-09-28 — **Conselho Consultivo do Luis:** Presidente + 6 conselheiros (Estratégia, Comercial & Parcerias, Operações & Tecnologia, Pessoas & Liderança, Finanças, Risco Tributário/Jurídico). Modos: reunião semanal automática e consulta sob demanda. Pareceres independentes → debate → ata com decisões para aprovação. Construído primeiro por ser risco zero.
- 2026-09-28 — **Departamentos virtuais:** cada área de apoio ganha Gerente (orquestrador) + especialistas. Não substituem a área real; preparam trabalho para validação. Portão 0 (plano) + Portão final (entrega). Tributário/Contábil/Jurídico = só pré-análise para o especialista humano validar. Cada departamento precisa de um dono humano na área real. Marketing construído primeiro.
- 2026-09-28 — **Princípio:** exemplos do Luis são ponto de partida; toda área é desenhada a partir de pesquisa de boas práticas, com proposta de incluir/substituir/fundir.
- 2026-09-28 — Técnico Contábil fundido ao Tributário (a equipe real já é fiscal + contábil + planejamento). Áreas novas: Partner Success & Enablement, Inteligência Comercial, Operações de Canal & Comissionamento, Dados & BI, TI/Automação & Gov. IA, Qualidade & Ouvidoria. Marketing v2 (marketing de canal).
- 2026-09-28 — Conselho passa a pedir embasamento técnico ao Tributário/Jurídico antes da Rodada 1.
- 2026-09-28 — Mapa de tarefas ganhou as colunas "Etapa do fluxo" e "Área de apoio envolvida" para medir o peso do trabalho de ponte.

## Arquivos gerados
- ARQUITETURA.md: organograma de agentes (3 células com orquestrador + subagentes; Conselho do Luis; portões de aprovação)
- agentes/conselho/FICHA.md
- conselho/ (pauta-da-semana.md, decisoes.md, atas/, consultas/)
- DEPARTAMENTOS.md: organogramas dos departamentos virtuais (Marketing, Téc. Tributário, Téc. Contábil, Jurídico, Contratos, Pós-venda)
- DEPARTAMENTOS.md v2 (pesquisa de boas práticas; 12 departamentos; ordem de construção)
- Skills `depto-tributario` (12 especialistas, fontes oficiais, reforma) e `depto-juridico` (10 especialistas, riscos-chave, prazos com dupla checagem) + pastas departamentos/tributario e /juridico
- Skill `depto-marketing` em ~/.claude/skills/depto-marketing/ (Gerente + 7 especialistas; marca, datas, jornal) + pasta departamentos/marketing/
- Skill `conselho-partners` em ~/.claude/skills/conselho-partners/ (SKILL.md + references/)
- ESTADO.md (este arquivo)
- mapa-de-tarefas-v2.xlsx: abas Daniela (Masters), Geovana (Suporte Técnico), Jenifer (BDR), Luis, com exemplos reais de cada função (substitui a v1)
- mapa-de-tarefas.xlsx (v1, obsoleta): abas "Como preencher", "Resumo" (automático), Suporte Técnico, Suporte Dia a Dia, Prospecção, Luis (Gestão Masters)
- mensagem-time.md: mensagem pronta para o time

## Pendências / dúvidas em aberto
- Validar com o Jurídico real: estrutura societária da Save × remuneração de parceiros (indicação comercial vs. honorários).
- Validar dados da reforma e dos riscos-chave (levantados por pesquisa web em 28/09/2026) com os técnicos humanos.
- Luis escolhe o próximo departamento a construir (sugestão: TI/GLPI ou Partner Success).
- Confirmar se Técnico Contábil é área própria na Save e quais outras áreas de apoio existem.
- Aprovar rotina diária do Jornal (proposta: dias úteis 07h30, salvo como rascunho).
- Fontes de dados da reunião semanal: HubSpot exige autorizar o conector; até lá, snapshot do cockpit + pauta-da-semana.md.
- Detalhes do GLPI: quem configura, prazo de entrada em produção, se tem API, categorias previstas.
- Conector HubSpot do plugin `hubspot-sales` precisa de autorização (configurações de conectores do claude.ai). Necessário só a partir da Fase 5.
