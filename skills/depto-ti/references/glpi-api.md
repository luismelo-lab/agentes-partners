# O que a API do GLPI permite (para agentes N1)

Pesquisa: 29/09/2026. Confirmar a versão instalada na Save (GLPI 10.0.x ou 11.0.x) antes de qualquer desenho.

## Duas APIs
| | API legada ("v1") | API de alto nível ("v2", só GLPI 11) |
|---|---|---|
| Endereço | `/apirest.php/...` (no GLPI 11 também `/api.php/v1/...`) | `/api.php/v2/...` (ou `/api.php/v2.x`; sem versão = mais recente) |
| Documentação | `apirest.md` no repositório do GLPI (e em `/apirest.php` da instalação) | Swagger em `/api.php/doc` (JSON com `.json`) |
| Autenticação | `initSession` com usuário/senha (Basic) **ou** `user_token` (chave de acesso remoto do usuário) → devolve `Session-Token`; `App-Token` do cliente de API; `killSession` ao final | OAuth2: cliente cadastrado em Configurar > Clientes OAuth; *password grant* (scripts) ou *authorization code* (apps de usuário); *client credentials* só para inventário; escopos `api`, `graphql`, `user`, `email`, `status`, `inventory`; token de 1 h (padrão) |
| Leitura | `GET /:itemtype/:id`, `GET /:itemtype/` (paginação `range`, padrão 0-49), sub-itens `GET /Ticket/:id/ITILFollowup` (e `TicketTask`, `ITILSolution`, `TicketValidation`, `Document_Item`, `Log`), `GET /search/Ticket` com `criteria` (IDs de campo obtidos em `GET /listSearchOptions/Ticket`), `getMultipleItems`, `expand_dropdowns=true` para nomes em vez de IDs | REST com filtro RSQL (`filter=status==1;category.id==12`, operadores `==`, `!=`, `=in=`, `=like=`, `=gt=`, `=isnull=`…) e **GraphQL somente leitura** em `/api.php/GraphQL` |
| Escrita | `POST/PUT/PATCH/DELETE` exigem sessão com `session_write=true` (a sessão é **somente leitura por padrão**) | POST/PATCH existem, mas há relato de campos não gravados (atores/requerente) no 11.0.6 — issue #23485, fechada como "not planned". Testar antes de usar para escrita. |
| Anexos | Upload `multipart/form-data` com `uploadManifest`; download `GET /Document/:id` com `Accept: application/octet-stream` | Ver Swagger |
| Permissões | **As do perfil do usuário da sessão.** Sem direito → `ERROR_RIGHT_MISSING`. Cliente de API pode ser restrito por **faixa de IP** e registrar conexões (Configurar > Geral > API) | As do usuário do token + escopo do cliente OAuth |

## Recursos do GLPI que o desenho usa
- **Categorias ITIL** hierárquicas, com campo **código** (usamos o código do tipo de demanda, ex.: `JUR-NOTIFICACAO`) e visibilidade por tipo (requisição/incidente) e por interface.
- **Modelos de chamado** por categoria: campo obrigatório, oculto ou pré-definido (inclusive SLA/OLA).
- **SLA e OLA** (níveis de serviço) com calendário e feriados: TTO (tempo até a 1ª resposta) e TTR (tempo até a solução); **níveis de escalonamento** (ex.: X horas antes do vencimento, notificar/reatribuir). O tempo em status **Pendente** não conta.
- **Regras de negócio para chamados**: categoria → grupo atribuído, observador, SLA, urgência.
- **Aprovação (TicketValidation)**: pedido de validação a um usuário ou grupo; status aguardando/aceito/recusado. Útil como "Portão" formal dentro do GLPI.
- **Acompanhamentos privados** (`is_private=1`): visíveis só para quem tem o direito de ver privados. Base para o "rascunho do agente" sem o parceiro ver.
- **Motivos de pendência** (GLPI 10+): pendência com lembrete automático.
- **Formulários nativos e catálogo de serviços** (GLPI 11; no 10, plugin Formcreator): perguntas mapeadas para campos do chamado.
- **Webhooks nativos** (GLPI 11): avisam um sistema externo quando um chamado é criado/alterado. Exige um endereço acessível pela internet; não serve para o Mac do Luis sem uma ponte.
- **Campos personalizados em chamado**: exigem o plugin **Fields (Campos adicionais)** também no GLPI 11 (a "genericidade" do 11 só cobre ativos personalizados). Há relato de valores de Fields não gravados via API no 11.0.2 com Fields 1.23.0 → testar leitura e escrita pela API antes de depender deles.

## Regras para os agentes (N1)
1. **Fase 1 — só leitura.** Conta de serviço `agente.partners` com perfil próprio (ver o xlsx, aba "API-Agentes"); sessão sem `session_write`; App-Token restrito ao IP de saída autorizado; `killSession` ao final de cada execução.
2. **Fase 2 — rascunho dentro do GLPI** (só com aprovação do Luis e do TI): o agente escreve **acompanhamento privado** marcado `[RASCUNHO IA — não enviado]` ou cria chamado no grupo "Rascunhos IA" sem notificação ao requerente; a pessoa revisa, edita e publica. O agente nunca soluciona, fecha, atribui a outra área, aprova validação nem apaga.
3. Nunca baixar anexos em massa: só o anexo do chamado em análise, quando a tarefa exigir.
4. Paginar (range/limit), respeitar limites, registrar cada execução (quantos chamados lidos, o que foi rascunhado).
5. IDs de campos de busca (`criteria`) variam por instalação e plugins: descobrir com `listSearchOptions/Ticket`, nunca fixar sem conferir.

## Fontes (consultadas em 29/09/2026)
- apirest.md (GLPI 10): https://github.com/glpi-project/glpi/blob/10.0/bugfixes/apirest.md
- API v2 (GLPI 11): https://help.glpi-project.org/documentation/modules/configuration/general/api/restful-api-v2
- Documentação do desenvolvedor (HL API): https://glpi-developer-documentation.readthedocs.io/en/master/devapi/hlapi/index.html
- Issue #23485 (v2, campos não gravados): https://github.com/glpi-project/glpi/issues/23485
- Modelos de chamado: https://help.glpi-project.org/tutorials/helpdesk/create_templates
- Níveis de serviço: https://help.glpi-project.org/faq/glpi/service_levels
- Formulários (GLPI 11): https://help.glpi-project.org/documentation/modules/administration/forms
- Lançamento do GLPI 11: https://www.glpi-project.org/en/glpi-11-is-out/
- Plugin Fields: https://help.glpi-project.org/doc-plugins/plugins-glpi/fields · Fields no GLPI 11: https://tic.gal/do-i-still-need-the-additional-fields-plugin-in-glpi-11-the-genericity-clarification/
