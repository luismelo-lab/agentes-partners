# Sistema de controle da Área Partners (26/10/2026)

Pedido do Luis (26/10/2026): "informações de tomada de decisão que gerem resultado, previsibilidade e controle". O pacote (`pacote-<data>.json`) diz o que aconteceu, a previsão (`previsao-<data>.json`) diz o que vem; este documento diz **o que fazer quando o número sai da faixa, quem faz e em quantos dias**. As regras estão em `infra/controle.json` (lidas por `infra/controle.py`), o contrato em `infra/gestao-schema.md` §3 e a alçada em `infra/alcadas.md`. Gabinete com Qualidade, Operações de Canal e Dados.

Princípios: a fórmula não muda entre semanas (dicionário de métricas); todo desvio tem dono, prazo e ação concreta; o que é reversível vale a recomendação no prazo; só regra, preço, meta, remuneração e produto em validação sobem ao Luis; nunca se promete valor, prazo ou êxito.

## 1. Tolerâncias por métrica
Status: **verde** dentro da faixa, **amarelo** fora da verde, **vermelho** fora da amarela, **cinza** sem dado ou sem meta aprovada. Tolerância "proposta" vale até o Luis aprovar na revisão mensal; a métrica fica no semáforo, mas o gatilho avisa que a faixa é proposta.

| Bloco | Métrica (id) | Verde | Amarelo | Por quê (justificativa curta) |
|---|---|---|---|---|
| Resultado | Ritmo de criação ÷ ritmo necessário da meta do mês (`criados_ritmo_pct`) e do Q4 (`criados_ritmo_q4_pct`) | ≥ 90% | ≥ 70% | Meta D111 em crédito de contrato fechado: out R$ 75 mi, nov R$ 100 mi, dez R$ 75 mi (Q4 R$ 250 mi). Criação da semana por dia útil contra o necessário. |
| Resultado | Ritmo de fechamento ÷ ritmo necessário da meta do mês (`ganhos_ritmo_pct`) e do Q4 (`ganhos_ritmo_q4_pct`) | ≥ 90% | ≥ 70% | Ritmo atual = fechado limpo (sem duplicidade de alta confiança) ÷ dias úteis decorridos; necessário = falta ÷ dias úteis restantes. Tolerância do Luis (D111). |
| Resultado | Win rate 3 meses (`win_rate_3m`) | ≥ 30% | ≥ 20% | 26% em 26/10; abaixo de 20% o pipeline precisa dobrar para a mesma meta; 30% foi o patamar de 2025. *Proposta.* |
| Resultado | Fator do mês sobre o mesmo período do anterior (`ganhos_mom_fator`) | ≥ 0,9× | ≥ 0,7× | Queda acima de 30% exige causa escrita (safra, Master, tese, sazonalidade). *Proposta.* |
| Caixa | Semanas sem fonte de honorário recebido (`semanas_sem_fonte_caixa`) | 0 | ≤ 4 | D18 (29/09) aprovou a fonte de recebimentos; sem ela ROI realizado e backlog ficam cinza. |
| Caixa | Entrada prevista 4 semanas ÷ líquido médio mensal (`caixa_4_semanas_pct`) | ≥ 80% | ≥ 50% | Líquido médio jul–set: R$ 6,2 mi/mês. Abaixo de 50% o caixa do trimestre não se sustenta. *Proposta.* |
| Caixa | Ganhos sem % de honorário (`ganhos_sem_honorario_pct`) | ≤ 10% | ≤ 30% | 57% em 26/10. Sem o % não há margem, repasse nem meta em líquido; 10% é a higiene da D18. |
| Caixa | Índice de qualidade dos ganhos (`indice_qualidade_ganhos`) | ≥ 85 | ≥ 70 | 74,6 em 26/10. Abaixo de 70 o pacote sai com confiança baixa. |
| Canal | Concentração top 5 (`concentracao_top5_pct`) | ≤ 50% | ≤ 85% | Dicionário: alerta acima de 50%. 90,6% em 26/10: a saída de um Master derruba o trimestre. |
| Canal | Masters com ritmo < −50% (`masters_em_queda_n`) | ≤ 1 | ≤ 2 | Três ou mais é tendência do canal, não caso isolado. *Proposta.* |
| Canal | Parceiros ativos em 90 dias (`parceiros_ativos_pct`) | ≥ 80% | ≥ 60% | 9 de 9 em 26/10. Abaixo de 60% metade do canal está dormente. *Proposta.* |
| Risco | Pipeline aberto parado (`abertos_parados_pct`) | ≤ 20% | ≤ 35% | 32% em 26/10. Acima de 35% o forecast por etapa perde valor. *Proposta.* |
| Risco | Grupos de duplicidade nos ganhos, alta confiança (`duplicados_grupos`) | ≤ 20 | ≤ 100 | 346 em 26/10 (R$ 825 mi de excedente). Acima de 100 o bruto não serve para meta nem forecast. *Proposta.* |
| Risco | Ganhos com honorário atípico (`honorario_atipico_n`) | ≤ 30 | ≤ 100 | 143 em 26/10 inflam a margem da carteira. *Proposta.* |
| Risco | Crédito prescrevendo no mês seguinte (`decadencia_proximo_mes_rs`) | 0 | ≤ R$ 1 mi | Acima de R$ 1 mi sobe ao Luis pelo limite da alçada. *Proposta.* |
| Operação | Lote do Recuperador sem decisão (`lote_sem_decisao_h`) | ≤ 48 h | ≤ 120 h | Lote parado trava a fila (lote 1 reenviado 3 vezes). |
| Operação | Entregas do dia que não saíram (`entregas_atrasadas_n`) | 0 | ≤ 1 | Mais de uma é falha de infraestrutura. |
| Operação | Acerto da área nos casos de teste (`acerto_area`) | ≥ 80 | ≥ 70 | 70 é a aprovação do padrão sênior. |
| Operação | Pedido parado (`pedido_parado_dias`) | ≤ 1 dia útil | ≤ 2 | SLA da Central. |
| Operação | Aprovações vazias por área (`aprovacoes_vazias_pct`) | ≤ 50% | ≤ 80% | Protocolo do gerente §5.1: acima de 80% por 2 semanas é revisão não aplicada. |
| Operação | Ações do Conselho e do Controle vencidas (`acoes_vencidas_n`) | 0 | ≤ 2 | Mais de duas é o ritual falhando. |

## 2. Gatilhos: se X, então ação Y, dono Z, em N dias úteis
Persistência "por 2 semanas" = status fora da tolerância em dois controles seguidos (na 1ª rodada, o valor anterior da própria fonte conta como a semana anterior). "Conselho" marca o que entra na pauta de segunda. Alçada pela matriz: **dona** (Daniela, Jenifer ou Geovana decide e executa), **gerente** (gerente da área de agentes recomenda; vale por padrão no prazo), **Luis**.

| Regra | Se… | Então… | Dono | Prazo | Alçada |
|---|---|---|---|---|---|
| C01 | criação de negócios < 70% do ritmo necessário da meta do mês ou do Q4 por 2 semanas | Jenifer e Daniela revisam a cadência e os Masters em queda; Conselho na segunda | Jenifer (com Daniela) | 5 | dona · Conselho |
| C02 | ritmo de fechamento < 70% do ritmo necessário da meta do mês ou do Q4 por 2 semanas | Conselho revisa o plano da semana; Daniela revisa o funil de cada Master com o técnico | Daniela (com Luis) | 3 | Luis · Conselho |
| C03 | win rate 3 meses < 20% | Jenifer e Daniela revisam a qualificação (SQL) e os motivos de perda | Jenifer | 10 | dona |
| C04 | fechado do mês < 0,7× o mesmo período do mês anterior | Controller explica a causa no pacote e diz se o Q4 muda de cenário | Controller | 3 | gerente |
| C05 | sem fonte de honorário recebido há mais de 4 semanas | TI e Operações de Canal redigem o pedido ao Financeiro e ao CRM (D18) | Gerente de TI | 10 | Luis |
| C06 | entrada prevista em 4 semanas < 50% do líquido mensal | Pós-venda lista PER vencendo e compensações; Geovana cobra o técnico | Geovana | 5 | dona |
| C07 | ganhos sem % de honorário > 30% | Daniela completa o % dos ganhos (lista de Dados) | Daniela | 5 | dona |
| C08 | índice de qualidade dos ganhos < 70 | Dados abre o saneamento da semana; pacote marcado confiança baixa | Gerente de Dados | 5 | gerente |
| C09 | concentração top 5 > 85% | Plano de diversificação (3 praças ou escritórios novos; reativar Masters pequenos); vai ao Conselho | Jenifer (Intel Comercial, Partner Success) | 10 | dona · Conselho |
| C10 | 3 ou mais Masters com ritmo < −50% | Daniela revisa o plano de conta de cada um (causa e próximo passo) | Daniela | 5 | dona |
| C11 | parceiros ativos < 60% | Partner Success monta a lista de reativação; Daniela escolhe por quem começar | Gerente de Partner Success | 10 | gerente |
| C12 | pipeline parado > 35% | Daniela e Masters limpam: ganhar, perder ou Recuperador; Dados entrega a lista | Daniela | 10 | dona |
| C13 | > 100 grupos de duplicidade nos ganhos | Dados saneia (grupos acima de R$ 10 mi primeiro); meta e forecast só com volume limpo | Gerente de Dados (com Daniela) | 5 | gerente |
| C14 | > 100 ganhos com honorário atípico | Dados lista, Daniela valida com o Master; margem sai com e sem eles | Gerente de Dados | 10 | gerente |
| C15 | crédito prescrevendo no mês seguinte sem PER | Geovana e técnico priorizam na fila; acima de R$ 1 mi sobe ao Luis | Geovana → Luis | 5 | dona |
| C16 | lote do Recuperador sem decisão > 48 h | Sobe ao gerente; Geovana decide ou diz o que falta; 5 dias úteis sem decisão vai ao Luis | Geovana → Luis | 2 | gerente |
| C17 | entrega esperada do dia não saiu | Sentinela refaz o mecânico; Central refaz o que precisa de IA; 2 dias seguidos, TI abre incidente | Gerente da Central | 1 | gerente |
| C18 | acerto da área < 70 | Área entra na fila do Arquiteto; corrigir o especialista do caso crítico primeiro | Arquiteto de Agentes | 7 | gerente |
| C19 | pedido ou demanda parada > 2 dias úteis | Cobrança à pessoa dona (responder, aprovar ou descartar); Central reprocessa se estiver com os agentes | pessoa dona | 1 | dona |
| C20 | > 80% de aprovações vazias por 2 semanas | Qualidade amostra 3 entregas; Arquiteto compara com o acerto; gerente refaz a revisão | Gerente de Qualidade | 5 | gerente |
| C21 | ação do Conselho ou do Controle com prazo vencido | Cobrança ao dono; na segunda o Conselho mantém, muda o prazo ou encerra | dono da ação | 2 | dona · Conselho |

Como funciona na prática: `controle.py` roda todo dia útil (sentinela, C17 e C19) e na sexta (consolidação, todas as regras). Cada desvio novo vai à **caixa de entrada** da pessoa dona (prioridade alta, origem "Controle", ação "Abrir gestão"), uma vez por semana. Desvio com dono agente (Controller, gerentes, Arquiteto) vai numa única mensagem ao Luis e entra na pauta do Conselho. O desvio fica aberto até a métrica voltar à faixa; o status passa a `em_andamento` quando a pessoa registra a ação e a `resolvido` quando a regra deixa de disparar. Desvio com prazo vencido vem marcado `vencido` e é cobrado pela C21.

## 3. Ritual de gestão e quem decide
| Ritmo | Quando e quem | O que acontece | Saída | Quem decide |
|---|---|---|---|---|
| **Diário** | 7h, Central (rotina `operacao-areas`) e sentinela | Plano do dia; caixa de entrada; entregas do dia (C17); pedidos parados (C19) | Plano do dia e mensagens na caixa | Dona da entrega: o que é operacional e reversível |
| **Semanal** | Segunda, 7h30, 30 minutos: Conselho (presidente) com o Luis; Daniela, Jenifer e Geovana leem a ata | Pauta fixa: 1) pacote, 10 min; 2) previsão, 5 min; 3) desvios abertos e vencidos, 10 min; 4) decisões com dono e prazo, 5 min | Ata; cada decisão vira entrada em `registro/gestao/acoes.jsonl` e é cobrada na semana seguinte (C21) | Luis: regra, preço, meta, remuneração, produto em validação. O resto vale a recomendação no prazo |
| | Sexta, 16h: consolidação semanal | Roda `controle.py`, aplica itens vencidos com `padrao: true`, reporta desvios e ações vencidas | Resumo ao Luis e folha de decisões | Aplicação por padrão do que é reversível |
| **Mensal** | 1º dia útil: Controller com Dados e Operações de Canal | Fechamento do mês; DRE da área (margem de contribuição, EBITDA); backlog e aging; revisão das tolerâncias "proposta" | Pacote mensal e proposta de tolerâncias | Luis aprova as tolerâncias; o Controller decide o formato |
| **Trimestral** | 1ª segunda do trimestre: Conselho com o Luis | Metas do trimestre (unidade e valor por produto), acurácia do forecast, revisão das regras de controle | Meta em `conselho/decisoes.md`; `controle.json` atualizado | Luis (meta e regra) |

Formato de `acoes.jsonl` (uma linha por ação): `{"id": "A-2026-001", "acao": "...", "dono": "daniela", "prazo": "2026-11-03", "origem": "conselho|controle", "ata": "conselho/atas/<data>.md", "regra": "C09", "status": "aberta|em_andamento|concluida|cancelada", "registrado_em": "..."}`. Só o Conselho e a consolidação escrevem; `controle.py` só lê (C21).

## 4. O que ainda depende do Luis (26/10/2026)
1. ~~Unidade da meta do Q4~~ resolvida pela **D111** (26/10/2026): crédito de contrato fechado, mensal 75/100/75 = R$ 250 mi. C01 e C02 leem o ritmo da meta do mês e do Q4 (cada uma vira desvio próprio). Falta o Luis aprovar o desdobramento por Master (proposta no pacote, `meta.por_master`).
2. **Tolerâncias marcadas "proposta"**: aprovar ou ajustar na revisão mensal de 03/11.
3. **Fonte de recebimentos** (C05, D18): pedido ao Financeiro e ao CRM a partir de 02/11.
