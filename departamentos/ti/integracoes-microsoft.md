# Integrações Microsoft 365 para os agentes da Área Partners
**Rascunho de pedido ao TI · 30/09/2026 · solicitante: Luis Fernando de Melo (Gerente Comercial · Parceiros Masters)**

## Contexto
A Área Partners usa agentes de IA (Claude) que leem o WhatsApp do time (Eazybe → HubSpot), recebem pedidos por e-mail, preparam análises e mandam os resultados por e-mail e OneDrive. Hoje isso roda no Mac do Luis: o Outlook é automatizado por AppleScript, os arquivos vão pela sincronização do OneDrive dele e os pedidos chegam na caixa pessoal dele. Por isso tudo para quando o Mac desliga e tudo sai em nome do Luis. As integrações abaixo resolvem esses dois pontos com o menor acesso possível. Nenhum agente envia nada para fora da Save nem responde parceiros ou clientes.

## Fase 1 · necessárias para os fluxos que já existem
| # | Pedido | Para quê | Acesso mínimo |
|---|---|---|---|
| 1 | **Caixa compartilhada** `agentes.partners@savecompany.com.br` | Receber os pedidos [AGENTES] e responder em nome da "Central de Agentes", não do Luis | Caixa compartilhada (sem licença). Luis com Acesso Total e Enviar Como |
| 2 | **Registro de aplicativo no Entra ID** ("Agentes Partners") | Os agentes lerem e enviarem e-mail sem depender do Outlook do Mac | Microsoft Graph: `Mail.ReadWrite` e `Mail.Send` de aplicativo, **restritos à caixa do item 1** por Application Access Policy (RBAC para aplicativos do Exchange). Certificado em vez de segredo |
| 3 | **Site do SharePoint** "Área Partners · Agentes" com biblioteca por célula (Masters, BDR, Técnica, Gestão) | Substituir a pasta do OneDrive pessoal: o time passa a ser dono, com permissão por pasta | `Sites.Selected` no mesmo aplicativo, com gravação só neste site |
| 4 | **Equipe no Teams** "Área Partners" com canais Central Masters, Central BDR, Central Técnica, Gestão e Alertas | Os agentes postarem os resumos (caixa do WhatsApp, lote do Recuperador, relatório semanal) onde o time já trabalha | Um fluxo do **Workflows** do Teams por canal ("postar em um canal quando receber um webhook"), só para postar. Abas com a biblioteca do SharePoint e o portal |
| 5 | **Microsoft Forms** "Pedido aos agentes" (código do catálogo em lista, campos obrigatórios) + fluxo do Power Automate que envia a resposta à caixa do item 1 | Garantir que o pedido chegue completo e no formato certo (hoje é texto livre no e-mail) | Forms e Power Automate padrão (conectores Standard) |

## Fase 2 · deixam a experiência melhor
| # | Pedido | Ganho |
|---|---|---|
| 6 | **Aprovações do Power Automate** (app Aprovações no Teams e no Outlook) | Aprovado, Não aprovado e Nova análise viram botões no Teams e no e-mail, em vez de resposta digitada |
| 7 | **Microsoft Lists** "Pedidos e pendências" no site do item 3 | Um quadro com status, responsável e prazo de cada pedido e pendência dos Masters, visível no Teams. Os agentes atualizam; o time acompanha |
| 8 | **Leitura de calendário** (`Calendars.Read`, delegada, só para Daniela, Jenifer e Geovana, com consentimento delas) | Briefing automático antes de cada reunião com parceiro ou cliente, enviado 1 hora antes |
| 9 | **Conector Microsoft 365 no Claude** (plano Empresarial, habilitado pelo administrador) | Cada pessoa usa o Claude com acesso aos próprios e-mails, arquivos do SharePoint e conversas do Teams |
| 10 | **Rótulos de retenção e DLP do Purview** no site do item 3 | Retenção definida (sugestão: 24 meses) e bloqueio de compartilhamento externo de arquivos com dados de clientes |

## Fase 3 · quando o uso crescer
| # | Pedido | Ganho |
|---|---|---|
| 11 | **Servidor para o motor dos agentes** (VM pequena no Azure ou servidor da Save) | Os agentes rodam 24h sem depender do Mac do Luis |
| 12 | **Bot no Teams** (Azure Bot ou Copilot Studio com modelo Claude) | O time conversa com os agentes dentro do Teams |
| 13 | **GLPI com API** e conta de serviço (já detalhado em `GLPI-pronto-para-agente.md`) | Os agentes abrem chamados na fila "Rascunhos IA" com o que já foi levantado e o que falta |

## Segurança (o que os agentes nunca terão)
- Acesso a outras caixas de e-mail, sites ou arquivos fora dos itens acima.
- Envio para fora de @savecompany.com.br: se possível, bloquear por regra de transporte na caixa do item 1.
- Permissões administrativas, ou leitura de Teams e chats de outras pessoas.
- O certificado do aplicativo fica só na máquina ou no servidor do motor. Os agentes nunca o leem nem o imprimem.

## Perguntas ao TI
1. Quem administra o Entra ID e o Exchange Online, e qual o prazo para o registro do aplicativo com consentimento de administrador?
2. A Save já usa Application Access Policy ou RBAC para aplicativos no Exchange?
3. Podemos criar o site do SharePoint e a equipe do Teams com o Luis como proprietário?
4. O Power Automate está liberado para usuários (conectores Standard)? Existe política de DLP do Power Platform?
5. Há licença de Copilot ou Copilot Studio na Save (para a Fase 3)?
