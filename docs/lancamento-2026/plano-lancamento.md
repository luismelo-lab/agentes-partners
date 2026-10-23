# Lançamento dos agentes ao time · plano de 1 semana

Rascunho para o Luis, de 23/10/2026. Uso interno. **Data do D0: [a definir pelo Luis].**

> Regra do Luis (13/10/2026): os fluxos nunca foram lançados formalmente à Daniela, à Jenifer e à Geovana. Até o D0, uso zero é o esperado e não é motivo para pausar nada. A adoção passa a ser medida **a partir do D0**. Os critérios de pausa C2 (Recuperador) e C3 (Central) de `docs/revisao-2026-10-13/operacao-eficiente.md` ficam suspensos até lá e voltam a contar no D0, com o prazo novo proposto abaixo.

## O que já existe e entra no lançamento (reaproveitado)
- **Caixa oficial de cada uma:** a pasta da Central no OneDrive (`Área Partners · Agentes/<Central>`), pela D91 (22/10/2026), enquanto a TI não libera o Graph e o GLPI.
- **Plano do dia** (`lib/operacao.py plano`), **folha curta do lote do Recuperador** (`skills/recuperador/scripts/lote_decidir.py`), **Revisor de Diagnóstico**, **Central de Agentes** (painel e e-mail `[AGENTES]`), **registro único de demandas** (`lib/registro_demandas.py`) e **medição das respostas sugeridas** (`lib/medicao_respostas.py`).
- **Semana 0:** roteiros e apontamentos já estão em `celulas/<pessoa>/Semana0-*` e nas pastas do OneDrive. Servem de linha de base do tempo por caso.
- **Propostas guardadas de 13/10:** C1 (placar semanal), C2, C3, C5 (delegar aprovações), C6 (Semana 0 real) e C7 (plano com no máximo 10 itens).

## Pré-requisitos (antes do D0)
| # | O que | Quem | Por quê |
|---|---|---|---|
| P1 | Compartilhar com cada uma a pasta da Central dela e o painel Central Partners | Luis | Sem acesso não há lançamento |
| P2 | Gravar o **Plano do dia** na pasta de cada pessoa (`Plano do dia/Plano-do-dia-<Nome>-AAAA-MM-DD.xlsx`), com no máximo 10 itens (C7) | depto-ti, ajuste em `lib/operacao.py` (cerca de meio dia) | Hoje, com o e-mail pausado, o plano dela cai na `Caixa de saída (e-mail pausado)` da pasta do Luis, e a planilha fica só no Mac (`departamentos/operacao/<Nome>/`) |
| P3 | Coluna **"O que fiz com o rascunho"** (Usei / Ajustei / Não usei) no plano do dia | depto-ti, no mesmo ajuste | Mede o aproveitamento direto. A medição atual compara textos no WhatsApp: de 52 sugestões, 40 ficaram "sem resposta" e 12 sem resultado |
| P4 | Decidir C5: Daniela aprova os chamados dela e Geovana os lotes dela; o Luis fica com tese, valor e conflito de canal | Luis · **decidido na D98 (23/10/2026)**, aplicado em skills e rotinas (`infra/alcadas.md`) | Antes, o Luis aprovava os chamados uma vez por dia (D91), e tudo esperava por ele |
| P5 | Ligar o **placar de adoção** no relatório de segunda (C1), lendo as fontes da seção "Indicadores" | depto-resultados | Para o D5 já ter número |
| P6 | Decidir se a Central lê pedido salvo na pasta (pergunta CA3) | Luis; depto-ti ajusta `central.py` se for sim | Hoje a Central lê só o painel e o e-mail `[AGENTES]`, que está pausado |

## Semana do lançamento (D0 a D5)
| Dia | O que acontece | Quem | Saída |
|---|---|---|---|
| **D0** (segunda) | 15 min com as três juntas: por que, a regra "nada sai sem vocês" e o que muda. Depois, 30 min com cada uma, pelo roteiro dela (`roteiro-<pessoa>.md`). Cada uma faz **1 pedido-modelo ao vivo** no painel e marca **1 decisão ao vivo** na entrega dela. Entrega do one-page em Word | Luis | D0 registrado em `docs/lancamento-2026/lancamento.json`; 3 pedidos e 3 decisões no registro |
| **D1** (terça) | Primeiro dia com a entrega diária na pasta, às 8h. Cada uma abre, decide e marca. Check-in de 10 min às 17h: o que travou | as três; Luis no check-in | Ajustes anotados em `celulas/<pessoa>/aprendizados.md` |
| **D2** (quarta) | Segundo pedido de cada uma à Central, sobre um caso real dela. Geovana fecha os 5 primeiros casos do lote 1 do Recuperador. Daniela aprova os chamados dela no painel (C5, D98) | as três | Pedidos P-xxxx do time; decisões no lote |
| **D3** (quinta) | Jenifer usa a lista e os follow-ups do plano. Geovana marca as lacunas do Revisor nos diagnósticos que entraram. Daniela usa os rascunhos ao parceiro e marca Usei / Ajustei / Não usei | as três | Decisões do Revisor; coluna de aproveitamento preenchida |
| **D4** (sexta) | Retro de 30 min com as três: o que manter, cortar e mudar (no máximo 3 mudanças). Terceiro pedido de cada uma. A consolidação das 16h junta os aprendizados | Luis e as três | Lista de mudanças para a semana 2 |
| **D5** (segunda seguinte) | Primeiro **placar de adoção** (D0 a D4) no relatório de segunda. O Luis decide as mudanças. Os critérios de pausa voltam a contar | Luis; depto-resultados | Placar no relatório; decisões registradas |

**Critério de pausa proposto (substitui o prazo de 31/10 de C2 e C3):** só se avalia depois de **2 semanas completas a partir do D0**. Pausa o que tiver, nessas 2 semanas, menos de 3 pedidos da pessoa à Central (C3) ou menos de 5 decisões por semana no Recuperador e no Revisor (C2).

## Indicadores de adoção (medidos a partir do D0)
Todos contam só o que aconteceu do D0 em diante (data em `docs/lancamento-2026/lancamento.json`). Antes do D0, os números ficam só como linha de base.

| Indicador | Como se calcula | Fonte | Linha de base (23/10/2026) | Meta proposta | Onde aparece |
|---|---|---|---|---|---|
| **Decisões no Recuperador** | Casos com decisão (Aprovar para reanálise, Vetar, Precisa de dado) por semana; também % de falsos positivos (vetadas ÷ decididas) e valor validado | Folha `Fila-Recuperador-Lote<N>-decidir-*.xlsx` na pasta da Geovana → lida por `fila.py` → `celulas/geovana/recuperador/indicadores-AAAA-MM-DD.json` (`decididas`, `aprovadas`, `vetadas`, `valor_validado`); decisões do painel em `celulas/geovana/recuperador/decisoes-painel.json` | 0 decisões em 4 lotes (lote 1 com 20 casos reenviado 2 vezes) | 5 ou mais por semana (C2) | Relatório de segunda (placar C1); quadro do supervisor no plano do Luis; aba Geovana do painel |
| **Decisões no Revisor** | Lacunas marcadas (Incluir tese, Não se aplica, Precisa de dado) por semana | Aba Lacunas de `Revisor-Diagnostico-*.xlsx` → `celulas/geovana/revisor/decisoes.json` (o arquivo nasce na primeira decisão) | 0 decisões em 203 revisões | Somadas às do Recuperador na meta de C2 | Relatório de segunda |
| **Respostas sugeridas aproveitadas** | % de sugestões marcadas Usei ou Ajustei (direto, com P3) e % "aproveitada" ou "parcial" na comparação automática | `registro/medicao-respostas.json` (campo `resultado`, por `lib/medicao_respostas.py atualizar` e `relatorio`) e, com P3, a coluna do plano do dia | 0 aproveitadas medidas: 52 sugestões (46 da Daniela), 40 "sem resposta" e 12 sem resultado | 50% ou mais Usei ou Ajustei na semana 2. Os 95% da D28 são outro critério: o de liberar envio automático | Relatório de segunda; relatório semanal da medição D28 |
| **Pedidos à Central** | Pedidos P-xxxx abertos por pessoa do time | `central-agentes/registro.json` (`pedidos`, campos `pessoa` e `recebido`) e `registro/demandas.json` (origem "E-mail (Central)" ou painel) | 0 do time; 5 do Luis | 3 ou mais por pessoa em 2 semanas (C3) | Relatório de segunda; aba Pedidos do painel |
| **Tempo por caso** | Minutos por caso no Recuperador e no Revisor (coluna "minutos no caso"); horas da abertura até a resolução da demanda | Colunas de minutos das folhas da Geovana → `indicadores-*.json`; `registro/demandas.json` (`aberta_em` até o evento de resolução); linha de base nos apontamentos `celulas/<pessoa>/Semana0-apontamento-<Pessoa>.xlsx` | Demandas do WhatsApp: mediana de 17 h (revisão de 13/10); Recuperador e Revisor sem medida | Abaixo da Semana 0, tarefa por tarefa | Relatório de segunda (horas economizadas, C1) |
| **Aprovações paradas** (apoio) | Pedidos e chamados esperando decisão há mais de 24 h | `registro/eventos.json` (tipo `aprovacao_parada`); `registro/chamados-propostos.json`; `registro/painel-aplicados.json` | Chamados à espera do Luis (D91) | Nenhum parado há mais de 3 dias úteis | Plano do dia de quem decide; quadro do supervisor |

**Leitura honesta:** só a medição das respostas e o registro de demandas estão em `registro/`. As decisões da Geovana ficam em `celulas/geovana/` e os pedidos em `central-agentes/`. O placar (P5) lê os três lugares; não é preciso mover nada.

## Riscos do lançamento
- **E-mail pausado:** o `[AGENTES]` por e-mail só volta com o Graph. Na semana do lançamento, pede-se pelo painel.
- **Excesso:** se a entrega diária passar de 10 itens, ela deixa de ser lida (planilhas de 125 e 80 linhas não foram lidas, C7).
- **Espera no Luis:** resolvido pela D98 (23/10/2026): a C5 vale, e só o que é alçada do Luis sobe a ele (`infra/alcadas.md`).
- **Promessa:** todo rascunho ao parceiro passa pelo auditor de promessas; quem envia é sempre a pessoa.
