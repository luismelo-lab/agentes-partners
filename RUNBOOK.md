# Runbook · como operar

## Horários (dias úteis, salvo indicação)
| Hora | Onde | O quê | Tokens |
|---|---|---|---|
| 8h–18h45, de 15 em 15 min | terminal (`partners central`) | Lê os e-mails [AGENTES] e enfileira | 0 |
| de hora em hora, 8h05–18h05 | Claude (`central-agentes-email`) | Processa a fila; se vazia, termina na hora | só quando há pedido |
| 7h30 | terminal (`partners manha`) | HubSpot, Dados & BI, dados do portal, OneDrive | 0 |
| 7h45 e 13h45 | terminal (`partners caixa`) | Lê caixas e demandas do WhatsApp (OCR, CNPJs, anexos) | 0 |
| 8h e 14h | Claude (`whatsapp-caixa-time`) | Triagem com IA: interpreta, entrega, envia e-mails; 8h atualiza o portal | sim |
| 11h e 17h | terminal (`partners whatsapp-auto`) | Rodada sem IA: e-mail **só para quem tem pedido novo** (sem resumo geral) | 0 |
| 19h30 (todo dia) | terminal (backup) | Backup no OneDrive | 0 |
| **segunda** 6h | terminal (`partners segunda`) | Métricas da semana, pareceres, fila do Recuperador, Revisor e relatórios das áreas (conflito de canal, repasses, contratos, Partner Success, ICP) | 0 |
| **segunda** 6h30 | Claude (`relatorio-semanal-resultados`) | Texto, deck e one-pager do relatório | sim |
| **segunda** 7h30 | Claude (`conselho-reuniao-semanal`) | Reunião do Conselho (ata) | sim |
| **segunda** 9h | Claude (`recuperador-lote-semanal`) | Fichas do lote e rascunho do e-mail da Geovana | sim |

As rotinas do Claude aparecem em **Agendadas** na barra lateral do app. As do terminal: `partners status`.

## Comandos úteis
```
partners status          # últimas execuções, fila da Central, pedidos em aberto, jobs ligados
partners logs central    # log de uma rotina (central, caixa, demandas, whatsapp-auto, hubspot, onedrive...)
partners caixa           # ler o WhatsApp agora
partners central agora   # ler os e-mails de pedido agora (fora do horário)
partners manha           # atualizar dados do dia agora
partners instalar        # religar os horários do terminal (depois de mudar um .plist)
```
Para ter o comando no terminal: `echo 'export PATH="$HOME/agentes-partners/bin:$PATH"' >> ~/.zprofile` e abrir um terminal novo.

## Regras de robustez (01/10/2026)
- **Um download do HubSpot por dia:** todas as rotinas usam o mesmo arquivo; `partners hubspot forcar` baixa de novo.
- **Espera pela internet:** até 10 minutos ao acordar o Mac. Se o download falhar, nada que depende dele roda com dado velho.
- **Aviso de falha:** e-mail automático para o Luis, uma vez por rotina por dia.
- **Caixa do WhatsApp:** lida no máximo a cada 20 minutos; fila da Central protegida contra gravação simultânea.
- **Registro único de demandas:** atualizado a cada triagem e a cada pedido da Central (`python3 lib/registro_demandas.py abertas`).

## Quando algo falha
- **Uma rotina do Claude fica "em andamento" parada:** ela está esperando uma permissão. Abra a rodada em Agendadas e clique em "Sempre permitir".
- **`partners status` mostra ERRO:** rode `partners logs <nome>` para ver a mensagem.
- **O Outlook não envia:** confira se o Outlook clássico está aberto. Na primeira execução pelo launchd, o macOS pode pedir para autorizar o controle do Outlook: aceite.
- **Mac acordar sozinho (recomendado):** no Terminal, rode `sudo pmset repeat wakeorpoweron MTWRF 07:20:00` e deixe o Mac na tomada.
- **Mac desligado ou app fechado:** os jobs do terminal rodam quando o Mac liga; as rotinas do Claude rodam quando o app abre.
- **Restaurar do backup:** copie `OneDrive/Backups/agentes-partners/<data>/agentes-partners` para `~/agentes-partners` e `.../skills` para `~/.claude/skills`. Recrie o `.env` com o token do HubSpot e rode `partners receita`.

## Para economizar ainda mais
- **Tudo pelo terminal:** o Claude também pode rodar pelo terminal, no modo automático (`claude -p`, com modelo mais leve na triagem). Hoje esse modo está bloqueado na conta ("Credit balance is too low") e depende de o administrador do Claude na Save liberar créditos de uso no terminal. Liberado isso, as rotinas com IA passam para o launchd e só chamam o Claude quando houver trabalho.
- **Menos rodadas com IA:** a triagem com IA pode ficar só às 8h e a Central pode rodar a cada 2 horas. É só ajustar o horário em Agendadas.
