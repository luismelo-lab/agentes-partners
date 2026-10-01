# Aprendizados — TI, Automação & Governança de IA

| Data | Entrega | O que foi corrigido / descoberto | Regra para as próximas vezes |
|---|---|---|---|
| 2026-09-29 | v1 do departamento | Campos de arquivo do HubSpot: os anexos de registros do CRM são arquivos "ocultos"; o escopo `files` sozinho pode não bastar e o `files.ui_hidden.read` é só leitura | Pedir sempre o escopo de leitura mais específico primeiro (`files.ui_hidden.read`), `files` só se o teste falhar |
| 2026-09-29 | v1 do departamento | GLPI 11: campos personalizados em chamado ainda exigem o plugin Fields; a API v2 tem relatos de campos não gravados (atores, Fields) | Ler pela v2 ou legada; escrever só pela legada e depois de testar em homologação |
| 2026-09-29 | v1 do departamento | Links do Bitrix24 contados sem imprimir URL (só domínio, tipo e parâmetros) | Nunca imprimir URL de arquivo de cliente, nem em log de trabalho |
| 2026-09-29 | Inventário | 8 skills estavam sendo criadas no mesmo dia por outras sessões | Refazer o `ls` no fim de cada levantamento e marcar "em construção" |
| 2026-09-29 | GLPI | Os códigos de subcategoria seguem o `sla.json` da célula da Daniela; 12 tipos novos foram propostos | Tipo novo aprovado → avisar o dono da célula para incluir no `sla.json` (não editar skill de outro) |
