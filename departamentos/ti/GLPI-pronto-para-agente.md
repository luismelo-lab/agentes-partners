# GLPI "pronto para agente" — Área Partners

**Versão 1.0 · 29/09/2026 · PROPOSTA para o TI da Save** (nada foi configurado)
Preparado pelo Departamento de TI virtual para o Luis Fernando de Melo levar ao TI. Planilha com o desenho completo (para o TI filtrar e responder): `GLPI-pronto-para-agente.xlsx`.

## Resumo em 5 linhas
1. **Categoria = área de apoio, subcategoria = tipo de pedido real** do time (35 tipos; 12 são novos, o resto já é usado pela Daniela no controle de pendências).
2. **Todo chamado de cliente leva o ID do negócio do HubSpot e o CNPJ.** É isso que deixa um agente conferir, resumir e acompanhar o chamado sem perguntar nada a ninguém.
3. **Campos obrigatórios por tipo**, via modelo de chamado por categoria, para o pedido chegar completo à área e não voltar.
4. **SLA (promessa ao parceiro) + OLA (promessa da área à Partners)**, com calendário de dias úteis e escalonamento automático; o tempo em "Pendente" não conta.
5. **Agentes: fase 1 só leitura; fase 2 só rascunho privado.** Conta de serviço própria, perfil mínimo, API restrita por IP. Atribuir, solucionar, fechar, aprovar e responder ao parceiro continuam sempre com uma pessoa.

## Por que isso importa agora
Hoje a Partners é uma central de "ponte": recebe no WhatsApp, encaminha, cobra e devolve. Se o GLPI nascer com categorias genéricas e texto livre, a ponte continua manual. Se nascer com **código de tipo, campos obrigatórios e vínculo com o HubSpot**, os agentes já prontos (célula da Daniela, Recuperador da Geovana, célula da Jenifer, departamentos virtuais) conseguem: montar o painel de pendências e SLA por Master, apontar o que falta no pedido, preparar a pré-análise para a área e rascunhar o retorno ao parceiro. A configuração custa o mesmo agora; depois, custa migração.

## 1. Estrutura
- **Entidade:** uma entidade "Partners" (ou a entidade da Save com os grupos abaixo). A decisão é do TI.
- **Categorias (nível 1 = área de apoio):** Técnico Tributário · Jurídico · Contratos · Pós-venda · Marketing · Comissionamento · Comercial & CRM (Partners) · Qualidade & Ouvidoria · TI & Sistemas · Outros.
- **Subcategorias (nível 2 = tipo de pedido):** o campo **código** da categoria recebe o código do tipo (ex.: `JUR-NOTIFICACAO`). Os agentes usam esse código para saber o que fazer, e ele é o mesmo da taxonomia da célula da Daniela (`sla.json`).
- **Tipo ITIL:** "Incidente" para o que é problema/urgência (notificação, contestação, reclamação, segurança); "Requisição" para o resto.
- **Título padrão:** `[CÓDIGO] Master · Cliente · pedido em 1 frase`.

## 2. Categorias e subcategorias
★ = tipo novo, proposto a partir do trabalho descrito para a Daniela (demandas dos 9 Masters, CRM, materiais), a Geovana (pareceres, revisão de diagnóstico, reanálises) e a Jenifer (prospecção, novos parceiros).

| Código | Subcategoria | Exemplo real | Fila | TTO | TTR | Obrigatórios | Agente que prepara → portão |
|---|---|---|---|---|---|---|---|
| TEC-DUVIDA | Dúvida tributária / tese | Parceiro pergunta se frigorífico no Lucro Real tem crédito sobre embalagens | G-Partners-Tecnico (Geovana, 1º nível) → G-Tecnico-Tributario | 4 h úteis | 3 dias úteis | F15, F04, F02, F12, F09 | depto-tributario (pré-análise com fonte) → Geovana valida → Geovana aprova a resposta; técnico humano valida se for nova |
| TEC-DOCUMENTOS | Documentos para diagnóstico (envio ou pendência) | Parceiro enviou SPED/EFD e quer saber se está completo | G-Tecnico-Tributario | 4 h úteis | 2 dias úteis | F15, F04, F01, F02, F09, F16 | Nenhum agente lê SPED/folha na fase 1 (D3); agente só confere a lista de documentos → Daniela encaminha |
| TEC-PARECER-STATUS | Status do diagnóstico / parecer em andamento ★ | Master cobra quando sai o parecer do cliente X | G-Tecnico-Tributario | 4 h úteis | 1 dia útil | F15, F04, F01 | celula-daniela (briefing_master --negocio) monta o status a partir do HubSpot → Daniela responde ao parceiro |
| TEC-REVISAO-DIAGNOSTICO | Revisão de diagnóstico antes da apresentação (2ª opinião) ★ | Geovana revisa negócio em 'apresentação de diagnóstico' e acha tese não levantada | G-Tecnico-Tributario (com Geovana observadora) | 1 dia útil | 3 dias úteis | F15, F01, F02, F12, F13 | Revisor de Diagnóstico (2ª onda da Geovana) → Geovana decide levar ao técnico (D5) |
| TEC-REANALISE | Reanálise de negócio perdido/zerado | Recuperador sugere reanálise; Geovana aprova e pede ao Técnico | G-Tecnico-Tributario | 1 dia útil | 5 dias úteis | F15, F01, F02, F22 | recuperador (ficha de reanálise) → Geovana aprova a ficha (D1/D5) |
| TEC-REUNIAO | Reunião técnica com parceiro/cliente ★ | Parceiro pede um técnico na reunião com o CFO do cliente | G-Partners-Tecnico (Geovana) | 4 h úteis | 2 dias úteis | F15, F04, F01, F14 | Preparador de Reunião Técnica (briefing, objeções com fonte) → Geovana |
| JUR-NOTIFICACAO | Notificação/intimação da Receita recebida pelo cliente | Cliente recebeu despacho decisório de não homologação | G-Juridico (+ G-Partners-Triagem observador) | 1 h útil | Mesmo dia (8 h úteis) para o 1º encaminhamento; solução até o prazo interno | F15, F04, F01, F02, F07, F10, F16 | depto-juridico (modo A, prazo com dupla checagem) → Advogado(a) no mesmo dia; Daniela avisa o parceiro |
| JUR-CONTRATO | Dúvida sobre contrato/cláusula (cliente ou parceiro) | Master pergunta se o êxito incide sobre crédito compensado de ofício | G-Juridico | 4 h úteis | 3 dias úteis | F15, F04, F01, F02 | depto-juridico (modo B) → Advogado(a) valida; Daniela responde |
| JUR-REUNIAO | Apoio jurídico em reunião | Cliente quer entender risco de multa antes de assinar | G-Juridico | 4 h úteis | 2 dias úteis | F15, F04, F01, F14 | depto-juridico (modo D) → Advogado(a) |
| JUR-LGPD | Dúvida de LGPD / uso de dados | Parceiro quer mandar lista de clientes por WhatsApp | G-Juridico | 1 dia útil | 5 dias úteis | F15, F04 | depto-juridico (LGPD) + depto-ti (LGPD técnica) → Jurídico real |
| CTR-ENVIO | Envio ou ajuste de contrato do cliente | Negócio ganho: enviar contrato para assinatura | G-Contratos | 4 h úteis | 2 dias úteis | F15, F04, F01, F02, F03, F11 | depto-contratos (conferente de dados: CNPJ, razão social, parceiro, honorário) → Daniela aprova o pedido; Contratos envia |
| CTR-ASSINATURA | Cobrança de assinatura pendente ★ | Contrato enviado há 10 dias e não assinado | G-Contratos | 1 dia útil | 3 dias úteis | F15, F04, F01 | depto-contratos (controle de assinaturas) → Daniela |
| CTR-DISTRATO | Distrato | Cliente quer encerrar o contrato | G-Contratos (+ G-Juridico se litígio) | 1 dia útil | 5 dias úteis | F15, F04, F01, F02, F11 | depto-contratos (distratos) + depto-juridico → Luis ciente; Jurídico se houver litígio |
| CTR-TERMO-PARCERIA | Termo de parceria (novo parceiro indicador ou Master) ★ | Jenifer ativou escritório contábil novo e precisa do termo | G-Contratos (+ G-Juridico) | 1 dia útil | 5 dias úteis | F15, F23, F04 | depto-operacoes-canal (termos) + depto-juridico → Luis aprova condições |
| POS-EXTRATO | Extrato de pagamento / saldo de créditos | Master precisa do saldo do cliente para reunião | G-Pos-venda | 4 h úteis | 2 dias úteis | F15, F04, F01, F02, F09 | Nenhum (área humana); agente só formata o pedido → Daniela |
| POS-GUIAS | Guias a compensar / aviso mensal de pagamento | Cliente não recebeu o aviso do mês | G-Pos-venda | 4 h úteis | 2 dias úteis | F15, F04, F01, F02, F09 | Nenhum (área humana) → Daniela |
| POS-COMPENSACAO | Compensação de ofício / dúvida sobre compensação | Receita compensou de ofício débito que o cliente contesta | G-Pos-venda (+ G-Juridico se houver risco) | 4 h úteis | 5 dias úteis | F15, F04, F01, F02, F07, F10 | depto-juridico (Recuperação de Créditos & Compensação) → Pós-venda + Jurídico |
| MKT-MATERIAL | Material que já existe | Parceiro pede a apresentação institucional atualizada | G-Partners-Triagem (Biblioteca de Materiais) | 4 h úteis | 1 dia útil | F15, F04, F17 | celula-daniela (Biblioteca de Materiais) → Daniela |
| MKT-NOVO | Material novo, personalizado ou co-branding | Master quer folder com a marca dele para evento | G-Marketing | 1 dia útil | 10 dias úteis | F15, F04, F17, F18, F19 | depto-marketing (+ revisão de compliance jurídico) → Marketing real + Daniela |
| REP-COMISSAO | Repasse / comissão do parceiro | Parceiro pergunta quando recebe o repasse do cliente X | G-Financeiro-Comissionamento | 4 h úteis | 5 dias úteis | F15, F04, F01, F09 | depto-operacoes-canal (conferência de repasse no HubSpot) → Financeiro; Luis se houver exceção |
| REP-CONTESTACAO | Contestação de valor de repasse ★ | Parceiro diz que o % pago está errado | G-Financeiro-Comissionamento | 4 h úteis | 5 dias úteis | F15, F04, F01, F11 | depto-operacoes-canal (extrato & contestações) → Luis + Financeiro |
| COM-STATUS | Status de negócio | Master quer saber em que etapa está o negócio | G-Partners-Triagem | 4 h úteis | 1 dia útil | F15, F04, F01 | celula-daniela (briefing_master --negocio) → Daniela |
| COM-NOVO-NEGOCIO | Registrar indicação / novo negócio | Parceiro indica empresa nova | G-Partners-Triagem | 4 h úteis | 1 dia útil | F15, F04, F02, F03, F12 | celula-daniela / celula-jenifer (crm_checagem: duplicidade, conflito de canal, Receita) → Daniela ou Jenifer cria no HubSpot |
| COM-CONFLITO-CANAL | Registro de oportunidade / conflito de canal ★ | Dois parceiros indicam a mesma empresa (mesma raiz de CNPJ) | G-Partners-Gestao (Luis) | 4 h úteis | 3 dias úteis | F15, F02, F04 | depto-operacoes-canal (registro & conflito) → Luis decide |
| COM-CONDICOES | Condições comerciais / exceção de honorário | Parceiro pede honorário acima da política | G-Partners-Gestao (Luis) | 4 h úteis | 3 dias úteis | F15, F04, F01, F11 | depto-resultados (margem) se preciso → Luis decide |
| COM-REUNIAO | Reunião de venda/pós-venda com cliente e parceiro | Agendar apresentação do diagnóstico | G-Partners-Triagem | 4 h úteis | 2 dias úteis | F15, F04, F01, F14 | celula-daniela (Reuniões: briefing e ata) → Daniela |
| COM-PROSPECCAO | Lista de prospecção / contas-alvo para um Master ★ | Master pede empresas-alvo de frigoríficos em GO | G-Partners-BDR (Jenifer) | 1 dia útil | 5 dias úteis | F15, F04 | celula-jenifer + depto-intel-comercial → Jenifer |
| COM-NOVO-PARCEIRO | Recrutamento/ativação de parceiro indicador ★ | Escritório contábil quer virar parceiro | G-Partners-BDR (Jenifer) | 1 dia útil | 5 dias úteis | F15, F23, F04 | celula-jenifer + depto-partner-success (onboarding 30/60/90) → Jenifer; Luis aprova o termo |
| CRM-CADASTRO | Atualizar dados de empresa/negócio no CRM | Parceiro informa que o cliente mudou de regime | G-Partners-Triagem | 4 h úteis | 1 dia útil | F15, F01, F02 | celula-daniela (proposta de atualização: campo, atual, sugerido, fonte) → Daniela aplica à mão no HubSpot |
| QLD-RECLAMACAO | Reclamação ou insatisfação | Master reclama de atraso recorrente no parecer | G-Partners-Gestao (Luis) + área envolvida | 2 h úteis | 3 dias úteis | F15, F04 | Qualidade & Ouvidoria (futuro); hoje o Luis → Luis no mesmo dia |
| QLD-SUGESTAO | Sugestão ou elogio de parceiro ★ | Parceiro sugere um material novo | G-Partners-Gestao (Luis) | 1 dia útil | 10 dias úteis | F15, F04 | — → Luis |
| TI-ACESSO | Acesso ou erro em sistema | Parceiro não consegue abrir o portal/GLPI | G-TI | 4 h úteis | 3 dias úteis | F15, F21 | depto-ti → TI |
| TI-AUTOMACAO | Pedido de integração, automação ou agente novo ★ | Ler chamados do GLPI por API para o painel de pendências | G-TI | 1 dia útil | A combinar (projeto) | F15, F21 | depto-ti (especificação de integração + ficha de avaliação de IA) → Luis + TI |
| TI-SEGURANCA | Incidente de segurança ou exposição de dados ★ | Link público com parecer de cliente; mensagem enviada ao destinatário errado | G-TI (+ G-Juridico/DPO) | 1 h útil | 1 dia útil para conter | F15, F21 | depto-ti (Segurança) + depto-juridico (LGPD: avaliar comunicação à ANPD) → TI + Jurídico no mesmo dia |
| OUT-OUTROS | Outros | Qualquer pedido que não se encaixa | G-Partners-Triagem | 1 dia útil | 5 dias úteis | F15, F04 | celula-daniela (triagem sugere a categoria certa) → Daniela reclassifica |


A planilha traz mais colunas: quem abre, tipo ITIL, urgência, OLA da área, campos opcionais, vínculo com o HubSpot e origem de cada tipo.

## 3. Campos
Nativos do GLPI: título, descrição, categoria, origem da requisição, requerente/observador, grupo atribuído, urgência, anexos, datas de SLA. Os campos de negócio precisam do **plugin Fields (campos adicionais)**, que continua necessário no GLPI 11 para campos em chamados. Alternativa se o TI não quiser o plugin: formulário nativo (GLPI 11) com as respostas gravadas na descrição no formato `Campo: valor` (o agente lê do mesmo jeito, mas não dá para filtrar relatórios por esses campos).

| Código | Campo | Tipo / onde | Regra |
|---|---|---|---|
| F01 | ID do negócio no HubSpot | Texto (só dígitos) · Plugin Fields — bloco 'Negócio' | 10–12 dígitos; agente monta o link app.hubspot.com/contacts/47865021/deal/<ID> e confere se existe |
| F02 | CNPJ do cliente | Texto (14 dígitos) · Plugin Fields — bloco 'Negócio' | Dígito verificador; agente confere na base da Receita e no HubSpot (duplicidade/conflito de canal) |
| F03 | Razão social do cliente | Texto · Plugin Fields — bloco 'Negócio' | Conferida com a Receita |
| F04 | Parceiro Master | Lista (9 Masters + 'Indicador/sem Master' + 'Interno') · Plugin Fields — bloco 'Negócio' | Lista fechada: D&S, AGILE, G.S.H, Empresarial Cardoso, JGM, Costa e Gaudêncio, Assecont, Orteconte, Gerson |
| F05 | Contato no parceiro (nome) | Texto · Requerente nativo (se o parceiro tiver usuário) ou Fields | Só nome; telefone e e-mail ficam no cadastro de usuário, não no texto |
| F06 | Origem da requisição | Lista nativa (Origem) · Nativo | WhatsApp · E-mail · Portal/Formulário · Telefone · Reunião · Agente IA (rascunho) |
| F07 | Data de ciência | Data · Plugin Fields — bloco 'Prazos' | Obrigatória em notificação da Receita; não pode ser futura |
| F08 | Prazo fatal | Data · Plugin Fields — bloco 'Prazos' | Calculado pelo Jurídico (dupla checagem); o TTR do chamado nunca passa do prazo interno (5 dias antes) |
| F09 | Competência / período | Texto AAAA-MM ou AAAA-MM a AAAA-MM · Plugin Fields | Formato validado pelo agente |
| F10 | Nº PER/DCOMP ou despacho | Texto · Plugin Fields — bloco 'Prazos' | Formato da RFB |
| F11 | Valor envolvido (R$) | Decimal · Plugin Fields | > 0 |
| F12 | Regime tributário | Lista · Plugin Fields | Lucro Real · Lucro Presumido · Simples · Não sei |
| F13 | Tese / variante | Lista · Plugin Fields | Mesma lista do HubSpot (teses_tributarias_aplicadas_neste_negocio_) |
| F14 | Data e hora da reunião | Data/hora · Plugin Fields | Futura |
| F15 | O que o parceiro precisa (1 frase) | Título nativo · Nativo (título) | Padrão do título: [CÓDIGO] Master · Cliente · pedido |
| F16 | Documentos | Anexo nativo · Nativo | Anexo no GLPI (nunca link público); sem CPF/dados bancários no texto |
| F17 | Público e canal do material | Texto · Plugin Fields | Ex.: clientes do agro via WhatsApp |
| F18 | Leva a marca do parceiro? | Sim/Não · Plugin Fields | — |
| F19 | Para quando precisa | Data · Nativo (data de vencimento sugerida) ou Fields | Não substitui o SLA; se menor que o SLA, justificar |
| F20 | Preparado com IA? | Sim/Não · Plugin Fields — bloco 'Governança' | Marcado pelo agente ou por quem abriu; permite medir o piloto |
| F21 | Sistema afetado | Lista · Plugin Fields | GLPI · HubSpot · Outlook · WhatsApp · Portal/links · Agente IA · Outro |
| F22 | O que mudou desde a análise | Texto · Plugin Fields | Obrigatório na reanálise (documento novo, período, regime) |
| F23 | CNPJ do parceiro | Texto (14 dígitos) · Plugin Fields | Dígito verificador |


**Vínculo com o HubSpot (regra de ouro):** F01 (ID do negócio) + F02 (CNPJ) obrigatórios em todo tipo ligado a um cliente. Exceções: registro de indicação (o negócio ainda não existe: F01 entra depois de criado), materiais, prospecção, parceiro e TI. O agente monta o link `https://app.hubspot.com/contacts/47865021/deal/<ID>`, confere se o CNPJ e o Master do chamado batem com o negócio e aponta divergência. Futuro (a decidir com o time de CRM): uma propriedade no negócio do HubSpot com os números dos chamados do GLPI.

**O que não entra em chamado:** CPF, dados bancários, senhas, SPED e folha no texto (anexos só quando a área precisar, nunca por link público).

## 4. Filas e grupos
| Grupo | Membros | Papel | Categorias |
|---|---|---|---|
| G-Partners-Triagem | Daniela (+ conta de serviço agente.partners, só leitura) | Porta de entrada: recebe, classifica, encaminha, acompanha e devolve ao parceiro. Observador de todos os chamados abertos pela Partners | COM-*, CRM-CADASTRO, MKT-MATERIAL, OUT-OUTROS |
| G-Partners-Tecnico | Geovana | 1º nível técnico, revisão de diagnóstico, reanálise, reuniões técnicas | TEC-DUVIDA (1º nível), TEC-REUNIAO, observador de TEC-* |
| G-Partners-BDR | Jenifer | Prospecção e novos parceiros | COM-PROSPECCAO, COM-NOVO-PARCEIRO |
| G-Partners-Gestao | Luis | Decisões comerciais, conflito de canal, reclamações | COM-CONDICOES, COM-CONFLITO-CANAL, QLD-* |
| G-Tecnico-Tributario | Time Técnico (área real) | Pareceres, diagnósticos, documentos, reanálises | TEC-* |
| G-Juridico | Jurídico (área real) | Notificações, contratos, LGPD, reuniões | JUR-*, apoio em CTR-DISTRATO, POS-COMPENSACAO, TI-SEGURANCA |
| G-Contratos | Contratos (área real) | Envio, assinatura, distrato, termo de parceria | CTR-* |
| G-Pos-venda | Pós-venda (área real) | Extrato, guias, avisos, compensações | POS-* |
| G-Marketing | Marketing (área real) | Materiais novos e co-branding | MKT-NOVO |
| G-Financeiro-Comissionamento | Financeiro (área real) | Repasses e contestações | REP-* |
| G-TI | TI da Save | Acessos, integrações, segurança | TI-* |
| G-Rascunhos-IA (fase 2) | Conta de serviço agente.partners + Daniela/Geovana/Jenifer | Fila de rascunhos criados por agente, sem notificação ao requerente; só sai daqui quando uma pessoa revisa e reclassifica | Qualquer (temporário) |


## 5. Status
| Status | ID | Significado | SLA | Observação |
|---|---|---|---|---|
| Novo | 1 | Chamado aberto, ainda sem responsável | Conta TTO | — |
| Em atendimento (atribuído) | 2 | Área de apoio recebeu e está trabalhando | Conta TTR | — |
| Em atendimento (planejado) | 3 | Tarefa com data marcada (ex.: reunião agendada) | Conta TTR | — |
| Pendente | 4 | Aguardando alguém de fora da área (usar motivo de pendência) | PAUSA o SLA | Motivos: Aguardando documento do parceiro/cliente · Aguardando outra área · Aguardando Receita/terceiro · Aguardando aprovação do Luis |
| Solucionado | 5 | Resposta/entrega registrada; Daniela confere e devolve ao parceiro | Para o TTR | Parceiro (ou Daniela) aprova ou recusa a solução |
| Fechado | 6 | Encerrado (automático após N dias sem recusa) | — | Sugestão: 3 dias úteis |
| (Aprovação) Aguardando / Aceita / Recusada | validação | Portão formal: o que precisa de ok do Luis ou do advogado antes de seguir | Não pausa por si | Usar TicketValidation nativo |


## 6. SLA e OLA propostos
Valores de partida = os prazos que a célula da Daniela já propôs (`sla.json`, ainda a validar com ela na Semana 0). Serão ajustados com o histórico real dos primeiros 60 dias.

| Nível | Tempos | Categorias | Escalonamento |
|---|---|---|---|
| SLA-P1 Crítico | TTO 1 h útil · TTR mesmo dia | JUR-NOTIFICACAO, TI-SEGURANCA | Escalonar a 50% e 80% do tempo: notificar Luis e grupo; a 100%: notificar gestor da área |
| SLA-P2 Alto | TTO 2–4 h úteis · TTR 3–5 dias úteis | CTR-DISTRATO, POS-COMPENSACAO, REP-CONTESTACAO, COM-CONFLITO-CANAL, QLD-RECLAMACAO | Escalonar a 80%: notificar Daniela e Luis |
| SLA-P3 Padrão | TTO 4 h úteis · TTR 1–3 dias úteis | TEC-DUVIDA, TEC-PARECER-STATUS, JUR-CONTRATO, JUR-REUNIAO, CTR-ENVIO, POS-EXTRATO, POS-GUIAS, COM-*, CRM-CADASTRO, MKT-MATERIAL | Escalonar a 100%: notificar Daniela |
| SLA-P4 Planejado | TTO 1 dia útil · TTR 5–10 dias úteis | TEC-REANALISE, TEC-REVISAO-DIAGNOSTICO, JUR-LGPD, CTR-TERMO-PARCERIA, MKT-NOVO, REP-COMISSAO, COM-PROSPECCAO, COM-NOVO-PARCEIRO, QLD-SUGESTAO, OUT-OUTROS | Escalonar a 100%: notificar responsável do grupo |
| OLA por área | Tempo da área de apoio para devolver à Partners (coluna 'OLA área' das categorias) | Todas com área de apoio | O SLA é a promessa ao parceiro; a OLA é a promessa da área à Partners. Se a OLA estourar, a Partners ainda tem folga para avisar o parceiro |
| Calendário | Dias úteis 08h–18h, feriados nacionais + locais da sede | Todos | Confirmar horário e feriados com o TI/RH |


## 7. Regras de negócio (automação dentro do próprio GLPI)
Automação determinística fica no GLPI (regras, modelos, SLA). O agente de IA só entra onde é preciso ler e escrever texto: conferir, resumir, rascunhar.

| ID | Condição | Ação |
|---|---|---|
| R1 | Categoria = X (na criação) | Atribuir ao grupo da fila da categoria; adicionar G-Partners-Triagem como observador; aplicar SLA/OLA da categoria |
| R2 | Categoria começa com JUR-NOTIFICACAO ou TI-SEGURANCA | Urgência 'Muito alta'; notificar Luis e o grupo por e-mail; exigir anexo (modelo de chamado) |
| R3 | Origem = Agente IA | Atribuir a G-Rascunhos-IA; NÃO notificar requerente; campo F20 = Sim; título recebe prefixo [RASCUNHO IA] |
| R4 | Campo F01 (ID do negócio) preenchido | Nada automático no GLPI; o agente confere se o negócio existe no HubSpot e aponta divergência de CNPJ/Master em acompanhamento privado (fase 2) |
| R5 | Status = Pendente por mais de 3 dias úteis | Lembrete automático ao requerente (motivo de pendência com lembrete) |
| R6 | Solucionado sem recusa em 3 dias úteis | Fechar automaticamente |
| R7 | Coletor de e-mail (caixa da Partners) | Criar chamado com Origem = E-mail, categoria OUT-OUTROS, grupo G-Partners-Triagem (a Daniela reclassifica) |


## 8. O que a API REST do GLPI permite para os agentes
Pesquisa na documentação oficial em 29/09/2026 (detalhes e links em `~/.claude/skills/depto-ti/references/glpi-api.md`).

**Duas APIs.** A **legada** (`/apirest.php`, documentada no `apirest.md`) existe no GLPI 10 e continua no 11. Autenticação por `initSession` (usuário/senha ou *user_token*) mais `App-Token` do cliente de API; a sessão é **somente leitura por padrão** (escrever exige `session_write=true`); tudo respeita os direitos do **perfil** do usuário; o cliente de API pode ser **restrito por faixa de IP** e ter as conexões registradas. Permite ler chamados, sub-itens (acompanhamentos, tarefas, soluções, aprovações, documentos, histórico), buscar com critérios (`/search/Ticket`, com IDs obtidos em `listSearchOptions`) e criar/alterar itens. A **API v2** (só no GLPI 11, `/api.php/v2`) usa OAuth2 (*password grant* para scripts; escopos `api` e `graphql`), filtro RSQL, documentação Swagger em `/api.php/doc` e **GraphQL somente leitura**. Na v2 há relato (11.0.6, issue #23485) de campos de requerente/atores não gravados em POST/PATCH, e há relato de valores do plugin Fields não gravados pela API no 11.0.2. **Conclusão: ler pela v2 ou pela legada; escrever (fase 2) pela legada, depois de testar em homologação.**

| O que o agente faz | API legada | API v2 (GLPI 11) | Fase | Permitido (N1)? |
|---|---|---|---|---|
| Ler chamados abertos da Partners (painel de pendências e SLA) | GET /apirest.php/search/Ticket?criteria[...] (status, categoria, grupo; IDs via listSearchOptions/Ticket) | GET /api.php/v2/Assistance/Ticket?filter=... ou GraphQL (somente leitura) | Fase 1 | Sim (leitura) |
| Ler um chamado com histórico | GET /Ticket/:id?expand_dropdowns=true + /Ticket/:id/ITILFollowup, /TicketTask, /ITILSolution, /TicketValidation | GET /api.php/v2/Assistance/Ticket/:id e timeline | Fase 1 | Sim (leitura) |
| Ler campos do negócio (F01–F23) | GET do item do plugin Fields ligado ao chamado (itemtype do container, ex.: PluginFieldsTicketnegocio) | Depende de o plugin expor na v2 — testar | Fase 1 | Sim, após teste |
| Ler categorias, grupos, SLA (para validar a taxonomia) | GET /ITILCategory, /Group, /SLA, /OLA | GET equivalentes na v2 | Fase 1 | Sim (leitura) |
| Baixar anexo de um chamado específico | GET /Document/:id (Accept: application/octet-stream) | Ver Swagger | Fase 1 (restrito) | Só o do chamado em análise; nunca em massa |
| Rascunhar resposta dentro do chamado | POST /Ticket/:id/ITILFollowup com is_private=1 e texto '[RASCUNHO IA — não enviado]' (sessão com session_write=true) | POST na v2 — testar (issue #23485) | Fase 2 (decisão do Luis + TI) | Sim, só privado |
| Rascunhar chamado novo (ex.: a partir de conversa de WhatsApp colada) | POST /Ticket com Origem = Agente IA, grupo G-Rascunhos-IA, sem notificação | POST /api.php/v2/Assistance/Ticket — testar | Fase 2 | Sim, só no grupo de rascunhos |
| Pedir aprovação (portão) | POST /TicketValidation (users_id_validate = aprovador) | Ver Swagger | Fase 2 | Sim (pedir, nunca aprovar) |
| Atribuir a outra área, solucionar, fechar, aprovar, apagar | PUT/DELETE | PATCH/DELETE | — | NÃO (sempre humano) |
| Enviar mensagem ao parceiro (notificação/e-mail) | — | — | — | NÃO (sempre humano) |


**Webhooks (GLPI 11):** o GLPI pode avisar um sistema externo quando um chamado é criado ou alterado, mas precisa de um endereço acessível pela internet. Hoje os agentes rodam no Mac do Luis, então a fase 1 usa **consulta periódica (leitura)**. Webhook fica para quando houver um ambiente corporativo para os agentes.

## 9. Plano de implantação sugerido
| Etapa | O quê | Quem | Critério de pronto |
|---|---|---|---|
| 0 | TI responde às perguntas abaixo; Luis e Daniela validam os tipos e prazos (Semana 0) | TI + Luis + Daniela | Taxonomia aprovada |
| 1 | Configurar categorias, grupos, modelos de chamado, SLA/OLA, regras R1–R7 em homologação | TI | 5 chamados de teste por área passam sem campo faltando |
| 2 | Conta de serviço `agente.partners` só leitura + cliente de API restrito por IP | TI | Agente lê os chamados de teste; nada além dos grupos da Partners |
| 3 | Produção; WhatsApp e GLPI em paralelo (a Daniela abre no GLPI o que chega no WhatsApp, origem = WhatsApp) | Daniela | 100% das demandas novas com chamado |
| 4 | Painel de pendências e SLA lido do GLPI (célula da Daniela) | Luis aprova | 4 semanas sem divergência com o controle manual |
| 5 | Fase 2 (rascunho privado) só se o Luis e o TI aprovarem por escrito | Luis + TI | Ficha de avaliação de IA aprovada |

## 10. Perguntas para o TI
1. Qual versão do GLPI está sendo implantada (10.0.x ou 11.0.x)? Hospedagem própria ou nuvem (GLPI Network Cloud/parceiro)? Onde ficam os dados?
2. Quem é o responsável no TI pela configuração do GLPI e qual o prazo de produção? Há ambiente de teste (homologação)?
3. A API REST (legada) e/ou a API v2 com OAuth podem ser habilitadas? Pode-se restringir o cliente de API por IP e registrar as conexões?
4. Aceitam criar uma conta de serviço 'agente.partners' com perfil só de leitura nos grupos da Partners (fase 1)? Quem guarda a credencial?
5. O plugin Fields (campos adicionais) pode ser instalado? Se não, aceitam formulários nativos (GLPI 11) com as respostas mapeadas no texto do chamado em formato 'Campo: valor'?
6. Os parceiros Masters terão usuário no GLPI (portal self-service) ou a Daniela abre em nome deles? Se tiverem usuário, cada Master vê só os próprios chamados?
7. Haverá entidades separadas (ex.: Save > Partners) ou uma entidade única com grupos?
8. As áreas de apoio (Técnico, Jurídico, Contratos, Pós-venda, Marketing, Financeiro) vão trabalhar dentro do GLPI (receber e solucionar) ou só a Partners usa?
9. Qual o calendário de atendimento (horário, feriados) para o SLA? O TI aceita SLA (promessa ao parceiro) + OLA (promessa da área à Partners)?
10. Haverá coletor de e-mail? Qual caixa? E integração com WhatsApp — o TI pretende usar a WhatsApp Business Platform oficial (Cloud API/BSP) ou algum plugin de terceiros?
11. Qual a política de retenção de chamados e anexos? Anexos de pareceres podem ficar no GLPI em vez de links públicos?
12. Os webhooks nativos do GLPI 11 podem ser usados no futuro (exigem um endpoint acessível; hoje os agentes rodam no Mac do Luis)?

## Perguntas para o Luis (antes de levar ao TI)
1. Quem é o responsável do TI pelo GLPI (nome), para constar como dono humano do departamento?
2. Os tipos ★ novos fazem sentido para o time? Algum tipo real ficou de fora?
3. Os parceiros Masters vão abrir chamado direto (portal) ou tudo passa pela Daniela no começo?
4. Os prazos de partida (SLA-P1 a P4) podem ser apresentados ao TI como proposta, antes da validação com a Daniela?
