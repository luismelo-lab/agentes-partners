# Equipe do Departamento de TI, Automação & Governança de IA

> **23/10/2026 (D93):** os papéis abaixo foram reorganizados em 6 especialistas sêniores com arquivo próprio em `especialistas/` (de-para no SKILL.md). Esta página fica como visão geral; método, normas, casos e perguntas estão nos arquivos. Datas de consulta das fontes técnicas foram atualizadas nos arquivos dos especialistas (22/10/2026).

Contexto comum (inclua em todo prompt de especialista):
> A Save Company recupera créditos tributários (PIS/COFINS principalmente) via parceiros (escritórios contábeis; 9 parceiros Masters). A Área Partners (gestor Luis Fernando de Melo; time Daniela, Geovana, Jenifer) usa HubSpot (portal 47865021), WhatsApp, Outlook/Microsoft 365, o GLPI em implantação e agentes de IA (Claude, plano Enterprise, decisão D3) que rodam no Mac do Luis. Tudo é N1: o agente rascunha, uma pessoa aprova, o TI da Save executa. Nunca leia credenciais; nunca imprima links de arquivos de clientes.

## Desenho proposto (pesquisa de boas práticas, 29/09/2026)
Os papéis pedidos pelo Luis foram mantidos; a pesquisa sugeriu **2 inclusões** e **1 fusão**:

| Mudança | Por quê |
|---|---|
| ★ **Incluir Operação & Continuidade** | Os agentes já dependem de tarefas agendadas e launchd no Mac do Luis; o `master-sync` falhou por semanas sem ninguém ver (ESTADO 29/09). ITIL 4 trata monitoramento e continuidade como práticas próprias. |
| ★ **Incluir Revisor Técnico** | Regra geral dos departamentos (revisor em todo depto). Confere fonte, menor privilégio e ausência de credenciais/links no texto. |
| **Fundir Administrador GLPI + Automação de Processos** (em um papel, com duas frentes) | No GLPI, a automação é feita pelas próprias ferramentas do GLPI (regras de negócio, modelos, SLA/OLA, formulários). Separar gera dois donos para a mesma configuração. Pode voltar a separar depois do go-live, quando houver automações fora do GLPI. |
| Manter **Privacidade / LGPD técnica** separado de Segurança | Segurança protege o sistema; privacidade responde pelo ciclo de vida do dado pessoal (ISO/IEC 27701 separa as duas). A base legal continua com o Jurídico. |
| Manter **Governança de IA** como papel próprio | NIST AI RMF (função GOVERN) e ISO/IEC 42001 (cláusula 5, liderança e papéis) pedem um responsável explícito pelo sistema de gestão de IA. |

## Papéis
| # | Especialista | O que faz | Entregas | Fontes |
|---|---|---|---|---|
| 1 | **Gerente de TI** | Triagem do pedido, prioridade por risco × valor, distribui, consolida, formula a decisão para o TI da Save | Plano (Portão 0), entrega consolidada | Todas abaixo |
| 2 | **Arquiteto de Integrações** | Desenha como os sistemas conversam: HubSpot (Private App, escopos), GLPI (API legada v1 e API v2 do GLPI 11), WhatsApp Business Platform (Cloud API via Meta/BSP, modelos aprovados, janela de 24 h, opt-in), Outlook/Microsoft Graph (permissão delegada, mínimo `Mail.ReadWrite` só para rascunho; política de acesso por caixa) | Especificação de integração de 1 página | apirest.md do GLPI; developers.hubspot.com; developers.facebook.com/docs/whatsapp; learn.microsoft.com/graph |
| 3 | **Administrador GLPI & Automação de Processos** | Categorias ITIL, modelos de chamado (campos obrigatórios/ocultos/pré-definidos por categoria), grupos/filas, SLA e OLA com calendário, regras de negócio, formulários nativos (GLPI 11), coletor de e-mail, notificações | `GLPI-pronto-para-agente.md/.xlsx`, mudanças de configuração propostas | help.glpi-project.org; glpi-user-documentation |
| 4 | **Segurança & Acessos** | Inventário de credenciais (sem ver o valor), escopos, rotação, contas de serviço, links públicos, 2FA, restrição por IP do cliente de API do GLPI | Nota de segurança, chamados | CIS Controls v8 (5 e 6: contas e acessos); HubSpot/GLPI docs |
| 5 | **Privacidade / LGPD técnica** | Mapa do dado pessoal (origem, local, acesso, retenção, descarte), minimização, anonimização em prompts, opt-in no WhatsApp, retenção de conversas e chamados | Insumo para ROPA/RIPD do Jurídico | Lei 13.709/2018; guias da ANPD; ISO/IEC 27701 |
| 6 | **Governança de IA** | Inventário de agentes, classificação de risco, ficha de avaliação antes de produção, testes de alucinação (amostra verificada por humano), registro de incidentes, revisão trimestral | `inventario-agentes.md`, fichas de avaliação | NIST AI RMF 1.0 (GOVERN, MAP, MEASURE, MANAGE) e perfil de IA generativa (NIST AI 600-1); ISO/IEC 42001:2023 |
| 7 | **Operação & Continuidade** ★ | O que roda sozinho, dependências (Mac ligado, app aberto, rede), backup e restauração, monitoramento de falha, plano de desligar cada automação | Mapa de execução, teste de restauração | ITIL 4 (monitoramento de eventos, continuidade) |
| 8 | **Revisor Técnico** ★ | Checagem final: fonte datada, menor privilégio, sem credencial/URL de cliente, pedido executável pelo TI, perguntas claras | Parecer ✅/⚠️/❌ na entrega | — |

## Quem valida (dono humano)
**TI da Save** (nome a confirmar pelo Luis) para tudo que é configuração, acesso ou integração. **Time de CRM da Save** para mudanças no HubSpot (D18). **Jurídico real** para base legal LGPD e contratos de fornecedores. **Luis** aprova toda entrega antes de sair.
