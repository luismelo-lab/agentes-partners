# Operação eficiente · o que sobra e o que falta

Revisão de 13/10/2026 feita pelo Arquiteto de Agentes, por TI/Operações e por Resultados com a Qualidade, com dados de 30/09 a 13/10. Proposta para o Luis aprovar por bloco. Nada foi mudado ainda, exceto a correção do aviso repetido (item A1).

## Resumo
- **O que funciona e é usado:** a leitura e a triagem do WhatsApp (80 demandas, 94% resolvidas, mediana de 17 h, usada pelas três) e o registro único de demandas.
- **O que roda muito e entrega pouco:** a Central foi lida 385 vezes em 14 dias e trouxe 3 pedidos, todos do Luis. O WhatsApp é lido de 5 a 7 vezes por dia, e só 4 das 12 rodadas com IA geraram algo.
- **O que produz e não vira decisão:** o Recuperador (R$ 7,2 mi esperados, 0 decisões em 4 lotes), o Revisor (203 revisões, 0 decisões), as respostas sugeridas (23, nenhuma medida) e o Conselho (40 de 63 decisões pendentes, todas com o Luis).
- **O catálogo está grande demais para o acionamento automático:** são 21 skills e cerca de 19.500 caracteres de descrição. O catálogo corta pelo total, e 5 a 6 skills somem a cada sessão.
- **Causa comum:** tudo depende do Outlook do Mac, que está fora desde 06/10, e da aprovação do Luis.

## Bloco A · Cortar ruído e custo (sem impacto no time)
| # | Ação | Evidência | Ganho |
|---|---|---|---|
| A1 | Aviso de falha pelo 2º canal no máximo 1 vez por rotina por dia **(já feito)** | Com o Outlook fora, a Central gerava cerca de 40 notificações por dia | Fim da enxurrada de avisos |
| A2 | Central: leitura sem IA a cada 30 min (era a cada 15). Rotina com IA às 9h, 12h e 16h, e só se houver fila ou item novo no painel | 385 leituras e 3 pedidos; rodadas com IA travadas por até 6 dias | −50% de execuções e −80% de sessões de IA |
| A3 | WhatsApp: 3 leituras sem IA (7h30, 11h, 16h30), sem o horário de 7h45. Uma rodada com IA às 8h15, só se as regras acharem item novo | 121 leituras em 14 dias; 8 de 12 rodadas com IA não geraram nada | −40% de leituras e −1 rodada de IA por dia |
| A4 | HubSpot: 1 download completo de manhã; à tarde, só os negócios alterados, em arquivo próprio | Hoje a tarde sobrescreve a manhã | Metade do tráfego, dado da manhã preservado |
| A5 | Limpeza diária sem IA: JSON com mais de 14 dias, Excel diário com mais de 30, logs rotacionados (8 semanas) | `celulas` com 134 MB e logs sem rotação | Menos disco, backup menor |
| A6 | Trava (lockf) também em caixa, WhatsApp automático e Central | Hoje podem rodar juntas | Sem corrida |
| A7 | Vigia às 9h e 15h: roda o `partners teste` e avisa pelo 2º canal se algo falhar ou se uma rotina não rodou | A operação ficou muda de 06 a 08/10 | Falha percebida em horas, não em dias |
| A8 | Cada rotina do Claude confere se o arquivo esperado foi gerado e tem tempo máximo de 20 min | As rotinas de segunda terminaram "succeeded" em 4 a 8 s sem gerar deck nem ata | Fim do falso sucesso |

## Bloco B · Catálogo enxuto (21 → 18 skills)
| # | Ação | Por quê |
|---|---|---|
| B1 | Descrições com até 300 caracteres em todas as skills | É o que mais melhora o acionamento: de ~19.500 para ~6.000 caracteres, e nenhuma skill some |
| B2 | Fundir Recuperador e Revisor numa **celula-geovana** (modos Recuperador, Revisor e dúvida técnica) | Mesma dona, mesma matriz, mesmos vetos; o `revisor.py` já mora no Recuperador |
| B3 | Aposentar o **arquiteto-agentes** (contexto vencido); a governança do catálogo vai para o depto-ti | Mentor da fase de construção, já superada |
| B4 | Deixar **pós-venda** em espera, até o Financeiro passar a planilha de recebidos, e depois juntar a Operações de Canal ("Financeiro do Canal") | Só texto, sem script, sem entregas; o dado "recebido" está 100% vazio |
| B5 | Um dono por número: saúde do parceiro com o depto-dados, conflito de canal com Operações de Canal, auditor de promessas com a Qualidade, download do HubSpot em `lib/`. As demais skills só consomem | Hoje cada tema aparece em 3 ou 4 skills, com risco de número divergente |
| B6 | Roteamento único: a Central usa a matriz do Gabinete | Hoje existem duas tabelas de rota |

## Bloco C · Valor e adoção (decisões do Luis)
| # | Ação | Critério |
|---|---|---|
| C1 | Placar semanal no relatório de segunda: tempo de resposta ao parceiro, demandas abertas/resolvidas/reabertas, decisões e R$ validado do Recuperador/Revisor, % de sugestões aproveitadas, horas economizadas, custo de IA | 4 segundas seguidas |
| C2 | Recuperador em lotes de 5, com decisão rápida da Geovana (sim, não ou falta dado). Sem decisões até 31/10, pausa | ≥ 5 decisões por semana |
| C3 | Central reapresentada ao time com 3 pedidos-modelo por pessoa. Menos de 3 pedidos do time até 31/10, pausa | Pedidos de Daniela, Jenifer e Geovana |
| C4 | Conselho: regra de 72 h, no máximo 5 decisões por ata, lote semanal com recomendação ("aprovo o lote, exceto X"), sem atas novas enquanto houver mais de 15 pendentes | Fila abaixo de 15 |
| C5 | Delegar aprovações: chamados da Daniela com a Daniela, lotes da Geovana com a Geovana; o Luis fica só com tese, valor e conflito de canal | Menos espera no Luis |
| C6 | Semana 0 real: 1 semana de apontamento das 3 tarefas mais frequentes de cada pessoa | Linha de base para horas economizadas |
| C7 | Plano do dia com no máximo 10 itens por pessoa, com valor e prazo; o da Jenifer vai junto do aviso da tarde | Planilhas de 125 e 80 linhas não são lidas |

## Bloco D · Falta e depende de terceiros
- **E-mail sem Outlook (Microsoft Graph):** código pronto (`lib/graph.py`); falta o registro do app pela TI. Destrava Central, plano, WhatsApp, alertas e Recuperador.
- **Operação fora do Mac:** 7 workflows prontos em `.github`; falta o repositório privado da Save e os secrets.
- **Planilha de recebidos do Financeiro:** destrava o pós-venda e os repasses.
- Texto dos pedidos: `docs/pedidos-ti-2026-10-13.md`.

## Calendário enxuto proposto (dias úteis)
| Hora | Rotina | IA |
|---|---|---|
| 7h30 | Manhã: HubSpot, caixa, sentinelas, plano, Dados & BI, portal, OneDrive | Não |
| 8h15 | Triagem do WhatsApp, só com novidade | Sim |
| 8h às 18h, a cada 30 min | Leitura da Central | Não |
| 9h, 12h e 16h | Central com IA, só com fila; 20 min no máximo | Sim |
| 9h e 15h | Vigia (`partners teste`) | Não |
| 11h e 16h30 | WhatsApp automático | Não |
| 13h30 | Tarde: HubSpot (só alterados), sentinelas, avisos urgentes | Não |
| 19h30 | Backup e limpeza | Não |
| Seg 6h / 7h / 8h / 9h | Segunda (terminal) / relatório / Conselho / lote do Recuperador | Não / Sim / Sim / Sim |
