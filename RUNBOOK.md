# Runbook · como operar

## Horários (dias úteis, salvo indicação)
| Hora | Onde | O quê | Tokens |
|---|---|---|---|
| 8h–18h45, de 15 em 15 min | terminal (`partners central`) | Lê os e-mails [AGENTES] e enfileira | 0 |
| de hora em hora, 8h05–18h05 | Claude (`central-agentes-email`) | Processa a fila; se vazia, termina na hora | só quando há pedido |
| 7h30 | terminal (`partners manha`) | HubSpot → Bitrix (pula sem webhook) → caixa do WhatsApp → sentinelas → **plano do dia** (e-mail por pessoa, planilha anexa) → Dados & BI → portal → OneDrive | 0 |
| 7h45 e 13h45 | terminal (`partners caixa`) | Lê caixas e demandas do WhatsApp (OCR, CNPJs, anexos) | 0 |
| 8h e 14h | Claude (`whatsapp-caixa-time`) | Triagem com IA: interpreta, entrega, envia e-mails; 8h atualiza o portal | sim |
| 8h e 14h | Claude (`whatsapp-caixa-time`) | Propõe chamados do GLPI no painel (abertos só depois da aprovação) | (mesma rodada) |
| 11h e 17h | terminal (`partners whatsapp-auto`) | Rodada sem IA: e-mail **só para quem tem pedido novo** (sem resumo geral) | 0 |
| 13h30 | terminal (`partners tarde`) | HubSpot de novo → sentinelas → **aviso da tarde** só com o que é novo e urgente (conflito, falha de rotina, entrada em apresentação) | 0 |
| 19h30 (todo dia) | terminal (`partners backup`) | Backup no OneDrive, com log e alerta | 0 |
| **segunda** 6h | terminal (`partners segunda`) | Métricas da semana, pareceres, fila do Recuperador, Revisor e relatórios das áreas (conflito de canal, repasses, contratos, Partner Success, ICP) | 0 |
| **segunda** 6h30 | Claude (`relatorio-semanal-resultados`) | Texto, deck e one-pager do relatório | sim |
| **segunda** 7h30 | Claude (`conselho-reuniao-semanal`) | Reunião do Conselho (ata) | sim |
| **segunda** 9h | Claude (`recuperador-lote-semanal`) | Fichas do lote; **envia** à Geovana com cópia para o Luis (D27). Se o Outlook falhar, vira rascunho | sim |

As rotinas do Claude aparecem em **Agendadas** na barra lateral do app. As do terminal: `partners status`. Jobs do launchd (7, em `infra/launchd/`): backup, caixa, central, manha, segunda, tarde e whatsapp-auto; `instalar.sh` religa todos.

## Plano do dia e avisos (D26)
- **Sentinelas sem IA** (`lib/operacao.py`): contrato parado (5 dias), contrato assinado parado (3 dias), entrou em apresentação (7 dias; o Revisor roda sozinho nos novos), conflito novo (regra de canal do `conflito_canal.py`), CRM incompleto (inclui CNPJ fora da base da Receita e regime que diverge do Simples), comercial parado (15 dias; Contato Futuro 60), diagnóstico parado (15), apresentação parada (30), parceiro inativo (1,5 × o maior intervalo normal do parceiro, entre 30 e 90 dias), ganho sem Bitrix, demanda atrasada (só a confirmada pela triagem com IA), aprovação parada (24 h; com 5 dias sobe para o Luis) e rotina com falha. Ganho sem execução e execução parada ficam desligadas até haver dados do Bitrix.
- **"Parado"** = dias desde a última atividade, não desde a última modificação (a sincronização com o Bitrix mexe nela). A data de entrada na etapa vem do campo `hs_v2_date_entered_current_stage` do HubSpot.
- **Quem recebe:** o dono do negócio no HubSpot (Jenifer ou Daniela) e o pipeline BDR. Parceiro fora do roster vai para o Luis.
- **Formato (opção B do Luis):** nos dias normais, os blocos grandes (apresentação parada e comercial parado) mostram o total e os 3 de maior valor; às segundas, até 10 por bloco. A lista completa vai sempre na planilha anexa, com "Abrir no HubSpot" e "Abrir no Bitrix".
- **Aviso da tarde:** não repete o que já foi no plano.
- **Assunto:** "[Partners · automático] ...". A Central ignora esses e-mails.
- **Trava:** manha, tarde e segunda usam `lockf` e não rodam juntas quando o Mac acorda.

## Painel Central Partners (entrada única do time)
https://claude.ai/artifact/7fgGfrK7zVqzjcXCscJmwb · compartilhar com o time como **Colaborador** (Viewer só lê).
| Fluxo | No painel | Quem processa |
|---|---|---|
| Pedidos aos agentes | Aba Pedidos: formulário com o catálogo; resposta e Aprovado / Não aprovado / Nova análise | Rotina da Central, de hora em hora |
| Chamados do GLPI | Aba de cada pessoa: aprovar (pode editar) ou recusar com motivo | Propostos às 8h e 14h; abertos na rodada da Central seguinte à aprovação (D25) |
| Demandas do WhatsApp | Aba de cada pessoa: Respondi / Encaminhei / Não é demanda | Central (sincroniza) e triagem das 8h/14h (lista) |
| Decisões do Recuperador | Aba Geovana: Aprovar / Vetar / Precisa de dado | Central (sincroniza) e lote de segunda |
| Decisões do Conselho | Aba Decisões (só o Luis grava) | Central (atualiza `conselho/decisoes.md`) |
| Apontamento (Semana 0) | Aba de cada pessoa: registrar tarefa | Central (salva em `registro/apontamentos.json`) |
O painel atualiza os dados às 8h (rotina com IA). As ações do time aparecem na hora para todos; os agentes aplicam na rodada seguinte.

## Comandos úteis
```
partners status          # últimas execuções, fila da Central, pedidos em aberto, jobs ligados
partners logs central    # log de uma rotina (central, caixa, demandas, whatsapp-auto, hubspot, onedrive...)
partners caixa           # ler o WhatsApp agora
partners central agora   # ler os e-mails de pedido agora (fora do horário)
partners manha           # dados do dia e plano do dia agora
partners tarde           # rodada da tarde agora (aviso só do que é novo e urgente)
partners backup          # backup agora
partners instalar        # religar os horários do terminal (depois de mudar um .plist)
```
Para ter o comando no terminal: `echo 'export PATH="$HOME/agentes-partners/bin:$PATH"' >> ~/.zprofile` e abrir um terminal novo.

## Regras de robustez (01/10/2026)
- **Um download do HubSpot por dia:** todas as rotinas usam o mesmo arquivo; `partners hubspot forcar` baixa de novo.
- **Espera pela internet:** até 10 minutos ao acordar o Mac. Se o download falhar, nada que depende dele roda com dado velho.
- **Aviso de falha:** e-mail automático para o Luis, uma vez por rotina por dia.
- **Caixa do WhatsApp:** lida no máximo a cada 20 minutos; fila da Central protegida contra gravação simultânea.
- **WhatsApp (regras):** a rodada sem IA não traz de volta o que a IA julgou "sem ação" sem mensagem nova. Pedido em grupo de Master vai para a Daniela, mesmo quando chega na caixa da Jenifer ou da Geovana. E-mail sem nada a responder ou acompanhar não é enviado. Rascunhos passam pelo auditor de promessas.
- **Registro único de demandas:** atualizado a cada triagem e a cada pedido da Central (`python3 lib/registro_demandas.py abertas`). Demanda reaberta em até 7 dias mantém o mesmo número; com chamado em andamento, fica em "acompanhar".
- **OneDrive (02/10):** todas as rotinas (publicar_onedrive, central, registro_demandas, backup) pegam a pasta por `lib/caminhos.py`, que acha a ativa pela marca de sincronização do macOS. Para conferir: `python3 lib/caminhos.py`.
- **Envios:** só para @savecompany.com.br (`lib/protecao.py`), com dados pessoais mascarados e auditor de promessas.

## Quando algo falha
- **Uma rotina do Claude fica "em andamento" parada:** ela está esperando uma permissão. Abra a rodada em Agendadas e clique em "Sempre permitir".
- **`partners status` mostra ERRO:** rode `partners logs <nome>` para ver a mensagem.
- **O Outlook não envia:** confira se o Outlook clássico está aberto. Na primeira execução pelo launchd, o macOS pode pedir para autorizar o controle do Outlook: aceite.
- **Mac acordar sozinho (recomendado):** no Terminal, rode `sudo pmset repeat wakeorpoweron MTWRF 07:25:00` e deixe o Mac na tomada.
- **Backup (10/10):** um `.tar.gz` por dia em `Backups/agentes-partners/`, montado fora do OneDrive e conferido antes de entrar. Restaurar: `tar -xzf <arquivo> -C ~/restaurado`.
- **Teste de fumaça (13/10):** `partners teste` confere em menos de 1 minuto se scripts, OneDrive, marca, Outlook, HubSpot, backup e skills estão de pé, sem enviar nada. Rode antes de cada commit e sempre que algo parecer parado.
- **OneDrive no padrão 00–99 (13/10):** o que é do Luis fica nas pastas por área (04 Gestão, 01 Comercial, 03 Produtos, 06 Marketing); a pasta "Área Partners · Agentes" guarda só as Centrais do time. Destinos: `python3 lib/caminhos.py <chave>`.
- **Duplicados no OneDrive:** `python3 infra/organizar_onedrive.py duplicados` mostra o que sairia; `... duplicados executar` manda para a Lixeira (recuperável) e grava o manifesto em `logs/`. Nunca toca Área Partners · Agentes, Backups, Teams, Gravações e Whiteboards.
- **Backup das 19h30 falhou:** veja `partners logs backup`. Se for permissão, dê Acesso Total ao Disco para zsh e python (Ajustes do Sistema → Privacidade e Segurança).
- **Mac desligado ou app fechado:** os jobs do terminal rodam quando o Mac liga; as rotinas do Claude rodam quando o app abre.
- **Restaurar do backup:** copie `OneDrive/Backups/agentes-partners/<data>/agentes-partners` para `~/agentes-partners` e `.../skills` para `~/.claude/skills`. Recrie o `.env` com o token do HubSpot e rode `partners receita`.

## Para economizar ainda mais
- **Tudo pelo terminal:** o Claude também pode rodar pelo terminal, no modo automático (`claude -p`, com modelo mais leve na triagem). Hoje esse modo está bloqueado na conta ("Credit balance is too low") e depende de o administrador do Claude na Save liberar créditos de uso no terminal. Liberado isso, as rotinas com IA passam para o launchd e só chamam o Claude quando houver trabalho.
- **Menos rodadas com IA:** a triagem com IA pode ficar só às 8h e a Central pode rodar a cada 2 horas. É só ajustar o horário em Agendadas.
