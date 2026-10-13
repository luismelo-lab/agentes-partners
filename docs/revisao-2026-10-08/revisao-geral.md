# Revisão geral · Área Partners

Revisão feita em 08/10/2026 pelo Arquiteto de Agentes e pela Qualidade. Fontes: documentação do repositório, código, registros, logs dos últimos 7 dias, jobs do launchd e rotinas agendadas do Claude. Nada foi alterado, enviado ou apagado.

## Resumo executivo

- **A operação está parada para o time desde 06/10, 14h30, e ninguém foi avisado.** O Microsoft Outlook não está mais instalado no Mac. Todo e-mail dos agentes sai pelo Outlook. Por isso, desde então, não saíram plano do dia, aviso da tarde, caixa do WhatsApp nem respostas da Central. O alerta de falha também usa o Outlook e não saiu.
- **O plano do dia não sai há 3 dias úteis (06, 07 e 08/10).** O download do HubSpot das 7h30 falha toda manhã. Um erro de rede passageiro derruba a rotina, porque o código não tenta de novo nesse caso.
- **Não há backup válido desde 02/10.** O backup das 19h30 falha todo dia por falta de permissão do macOS na pasta do OneDrive. O repositório git não tem cópia remota. Hoje, o código e os registros existem só neste Mac.
- **As rotinas com IA estão travadas.** A triagem do WhatsApp está "em andamento" desde 07/10, 8h14. A Central está assim desde 07/10, 12h20. Rodada travada impede as seguintes.
- **O desenho é bom e o código é sólido.** Os 58 scripts Python compilam. A barreira de LGPD não acha dado sensível nos 182 arquivos versionados. A governança N1 com trava de domínio está bem implementada.
- **O ponto fraco é a operação, não a arquitetura.** Faltam monitoramento independente do e-mail, testes automáticos, cópia remota e um ambiente que não dependa do Mac do Luis.

## Placar por componente

| Componente | Estado | Evidência (08/10) |
|---|---|---|
| Envio de e-mail (Outlook) | Vermelho | 66 falhas "syntax error -2741" na Central desde 06/10 14h30. Plano, avisos e WhatsApp com "FALHOU". Outlook ausente de /Applications |
| Plano do dia (7h30) | Vermelho | Último plano completo em 05/10. Em 06, 07 e 08/10 o HubSpot falhou de manhã e a corrente parou |
| Download do HubSpot | Amarelo | Falha 3 vezes por manhã ("Erro HubSpot 000"). Funciona à tarde. 4.939 negócios em 07/10 |
| Backup diário | Vermelho | Último backup bom: 02/10, 09h59 (manual). 6 falhas seguidas, "Operation not permitted" |
| Repositório git | Amarelo | 182 arquivos, 0 achados de dados sensíveis. Sem remoto. 6 arquivos alterados e 2 novos sem commit |
| Rotinas do Claude (agendadas) | Vermelho | WhatsApp e Central travadas em "running" desde 07/10. Rotinas de segunda rodaram às 14h40, não às 6h30–9h |
| Jobs do launchd | Amarelo | 7 instalados. 5 com último código de saída 1 (segunda, backup, central, manha, tarde) |
| Leitura do WhatsApp (sem IA) | Verde | "caixa" e "demandas" ok em todas as rodadas, inclusive hoje às 7h51 |
| Sentinelas | Amarelo | Rodam quando o HubSpot baixa. 309 eventos; 106 são "entrou em diagnóstico" (ruído). Só 3 eventos de "rotina falhou" apesar das falhas desta semana |
| Registro único de demandas | Verde | 69 demandas (64 WhatsApp, 5 Central). 56 resolvidas |
| Central de Agentes (e-mail e painel) | Vermelho | Leitura falha desde 06/10. Só 5 pedidos desde 30/09. Ações do painel aplicadas: 0 |
| Recuperador (piloto D1) | Amarelo | Fila de 323 casos. 343 pareceres esperam o escopo de arquivos do HubSpot. 0 baixados |
| Medição das respostas (D28) | Amarelo | 4 casos medidos, 0% aproveitados. Amostra pequena, mas é um sinal |
| GLPI | Amarelo | Modo rascunho. 6 chamados propostos, nenhum aberto. Aguarda o cliente OAuth da TI |
| Bitrix | Amarelo | Desligado. Aguarda o webhook da TI. 2 sentinelas desligadas |
| Microsoft Graph e Teams | Amarelo | Código pronto e desligado. Aguarda a TI |
| OneDrive (pasta ativa) | Amarelo | O atalho oficial aponta para uma pasta que não existe mais. O código caiu na alternativa e acertou, mas por sorte |
| Proteções (domínio, máscara, auditor) | Verde | Trava de domínio no único ponto de envio. Mascaramento e auditor ativos |
| Design System Save | Amarelo | Padrão definido em 07/10. Ainda não está nos scripts em uso; 3 geradores usam o logo antigo |
| Decisões do Conselho | Amarelo | 63 linhas: 19 aprovadas, 41 pendentes. Prazos da D40 (06 e 08/10) vencidos |
| Testes automáticos | Vermelho | Nenhum teste no repositório |
| Documentação | Amarelo | Completa até 02/10. Desatualizada em OneDrive, Outlook e fase do projeto |

## Causa dos erros de log

São quatro causas independentes. A primeira explica quase todo o vermelho dos logs desde 06/10.

## Causa 1 · Central, plano, avisos e WhatsApp: Outlook ausente

- **Sintoma.** Desde 06/10, 14h30, toda chamada ao Outlook dá erro de sintaxe do AppleScript (-2741), nas posições 79:87 (leitura) e 213:220 (envio).
- **Causa.** O AppleScript não reconhece termos como "time received" e "outgoing message". Isso acontece quando o aplicativo não existe no Mac, porque o macOS não acha o dicionário dele. Conferido: não há nenhum aplicativo da Microsoft em /Applications. Os recibos de instalação continuam no sistema, então os apps não foram desinstalados pelo instalador. A pasta /Applications foi alterada em 06/10 às 14h17. Às 14h15, apareceram na raiz do OneDrive dois atalhos, "Microsoft Outlook" e "Microsoft Teams", que apontam para /Applications. O mais provável é que os apps tenham sido arrastados ou apagados durante a limpeza de pastas daquela tarde. O organizador do OneDrive não mexe em /Applications.
- **Efeito.** A Central não lê pedidos. Plano, avisos e e-mails do WhatsApp não saem. O alerta de falha também não sai.
- **Falha de projeto.** O canal que avisa da falha é o mesmo que falhou. Além disso, a rodada sem IA do WhatsApp registra "ok" mesmo quando o envio falha.
- **Correção.** Reinstalar o Microsoft 365 (ou recuperar os apps da Lixeira) e abrir o Outlook clássico uma vez. Depois, rodar "partners central agora" e "partners manha".

## Causa 2 · Plano do dia: download do HubSpot sem nova tentativa

- **Sintoma.** "Erro HubSpot 000 em /crm/v3/objects/deals/search" às 7h43, 7h58 e 8h09 em 06, 07 e 08/10. À tarde funciona.
- **Causa.** O código "000" significa que o curl não recebeu resposta: rede instável logo depois que o Mac acorda, conexão interrompida ou tempo esgotado (60 s). A função de chamada só tenta de novo nos códigos 429 e 5xx. No "000", ela desiste na hora. O download tem dezenas de páginas, então basta uma falha para perder tudo. O motivo do erro do curl também não vai para o log. Em 07/10, 13h34, houve outra falha parecida: a resposta veio cortada e o JSON não foi lido.
- **Efeito.** Como a regra é "sem dado novo, não segue", as sentinelas, o plano, o portal e o OneDrive não rodam de manhã.
- **Correção.** Tentar de novo com espera crescente também no "000" e no JSON cortado. Gravar a mensagem do curl. Rodar o download sob "caffeinate" para o Mac não dormir no meio.

## Causa 3 · Backup: permissão do macOS e pasta do OneDrive

- **Sintoma.** "Operation not permitted" no rsync e no find dentro de ~/Library/CloudStorage desde 02/10, 19h33.
- **Causa.** Pela proteção de privacidade do macOS, o zsh chamado pelo launchd não pode acessar a pasta do provedor de arquivos do OneDrive. Em sessão interativa funciona; no agendamento, não. O RUNBOOK já previa isso (Acesso Total ao Disco), mas nunca foi feito.
- **Agravante.** A pasta do OneDrive mudou 3 vezes em 5 dias ("... 2 2", "OneDrive - SAVE COMPANY", "OneDrive-SAVECOMPANY"). Os backups anteriores a 02/10 estavam na pasta "... 2 2", que não existe mais neste Mac. As pastas de 03 a 07/10 têm cópias parciais.
- **Correção.** Dar Acesso Total ao Disco ao /bin/zsh e ao python3, ou mover o backup para um destino sem essa proteção, como um repositório privado no GitHub da Save. Checar o tamanho e o conteúdo do backup depois de copiar.

## Causa 4 · Rotinas do Claude travadas

- **Sintoma.** A triagem do WhatsApp está "em andamento" desde 07/10, 8h14. A Central está assim desde 07/10, 12h20. Hoje às 8h, a triagem não rodou.
- **Causa provável.** Pedido de permissão parado na sessão (o RUNBOOK cita esse caso) ou a sessão esperando o Outlook. Uma rodada travada impede as seguintes.
- **Correção.** Abrir as duas rodadas em Agendadas e encerrar ou permitir. Médio prazo: mover para `claude -p` com tempo máximo e permissões fixas.

## Achados de código e repositório

- **Fonte da verdade invertida.** O Design System foi aplicado em 07/10 nas cópias do repositório (`skills/depto-marketing/scripts/email_layout.py`, `email_whatsapp.py`, `gen_deck.js`, `marca-save.md`). As cópias em uso, em ~/.claude/skills, continuam antigas. O `repo-sincronizar.sh` copia de ~/.claude/skills para o repositório com --delete. Se for rodado antes do commit, essas mudanças se perdem.
- **Dependência fora do repositório.** O novo `email_layout.py` importa `lib/marca.py`, que lê `departamentos/marketing-marca/padrao/marca.json`. Esse arquivo está bloqueado pelo .gitignore. Na nuvem, todo e-mail quebraria. Não há valor padrão se o arquivo faltar.
- **Código sem versão.** Os scripts de produtos (`departamentos/produtos/*/scripts`, incluindo o `gerar_manual_docx.js`, gerador oficial de Word do Design System) não entram no git, porque a regra só libera `departamentos/*/scripts`. O padrão de marca (`marca.json`, `save.css`, `pptx_save.js`) também não entra.
- **Logo antigo.** Três geradores do Crédito Internacional (`gerar_apresentacao_cliente.py`, `gerar_apresentacao_cliente_v2.py`, `gerar_peca_institucional.py`) usam `marketing-marca/logo-saveco.png`, e não os logos do padrão v0.5.
- **Caminho quebrado.** O atalho `OneDrive - SAVE COMPANY` aponta para "OneDrive-SAVECOMPANY 2 2", que não existe. O `caminhos.py` caiu na alternativa e funciona. O `organizar_onedrive.py` usa o atalho fixo e quebraria. O `lookalike-agregados.json` guarda caminhos absolutos da pasta antiga.
- **Nomes de terceiros no git.** `conselho/decisoes.md` (versionado) cita uma empresa em negociação (D32) e o nome de um contato externo. Os parceiros Masters aparecem nas descrições das skills. A barreira de LGPD não procura razão social.
- **Telefone sem máscara em registro local.** `registro/medicao-respostas.json` usa um telefone completo como chave. Ele não está no git, mas vai para o backup.
- **Falha que parece sucesso.** `email_whatsapp.py` termina com código 0 mesmo quando o envio falha. O `partners.log` mostra "ok".
- **Skills pouco visíveis.** Cinco skills (pós-venda, qualidade, resultados, TI e revisor) aparecem sem descrição no catálogo. As descrições passam de 1.000 caracteres. Isso reduz o acionamento automático.
- **Sem testes.** Não há teste unitário nem de fumaça. O `py_compile` passou nos 58 scripts, mas isso só pega erro de sintaxe.
- **Gerador genérico em pasta de produto.** O gerador de Word fica dentro do Crédito Internacional. Ele deveria ficar em `marketing-marca/padrao` ou em `lib/`.

## Entregas por frente

| Frente | O que entregou | Estado |
|---|---|---|
| Gabinete e Conselho | Roteamento por níveis; atas semanais; D1–D61 | Verde no desenho; 41 decisões pendentes |
| Célula Daniela | Caixa do WhatsApp, demandas, retorno, chamados propostos | Amarelo (envio parado) |
| Célula Jenifer | Listas por Master, cadência, Semana 0 | Amarelo (pouco uso medido) |
| Célula Geovana | Recuperador (fila de 323), Revisor, lote semanal | Amarelo (pareceres bloqueados) |
| Dados & BI, Intel. Comercial | Painel de qualidade do CRM, scorecard, ICP, base da Receita | Verde |
| Operações de Canal, Contratos | Conflito de canal, repasses, controle de contratos | Verde (relatórios de segunda) |
| Partner Success | Métricas de parceiros, níveis, onboarding | Verde |
| Qualidade, Jurídico, Tributário | Auditor de promessas, regras, pré-análises | Verde |
| TI | GLPI pronto para agente, inventário, pedidos à TI | Amarelo (dependências externas) |
| Marketing e Marca | Kit, jornal, Design System v0.5 | Amarelo (padrão fora dos scripts em uso) |
| Produtos | Crédito Internacional (24 documentos) e Maquila (7 documentos e calculadora) | Amarelo (D30–D60 pendentes) |

## O que funciona bem

- Separação clara entre terminal sem IA e Claude com IA. É o desenho certo para custo e previsibilidade.
- Registro único de demandas com número fixo e regra de reabertura em 7 dias.
- Trava de domínio num só ponto de envio, mascaramento e auditor de promessas.
- Barreira de LGPD no pre-commit e .gitignore por lista de permissão.
- Corrente que não segue com dado velho. Ela estava certa ao parar; faltou tentar de novo e avisar por outro canal.
- Preparação para a nuvem (workflows e Graph) já escrita e desligada.
