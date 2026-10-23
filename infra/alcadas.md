# Matriz de alçada e recomendação que vale por padrão

Regra do Luis de 23/10/2026: as decisões estavam todas com ele. Havia 54 itens "pendente" em `conselho/decisoes.md` e cerca de 30 na folha por semana. Esta matriz diz quem decide o quê. Para o que é reversível e está dentro das regras, a recomendação das áreas vale se não houver resposta até o prazo.

## 1. Quem decide
| Tipo de decisão | Exemplos | Quem decide | Precisa do Luis? |
|---|---|---|---|
| **Operacional, reversível e dentro das regras** | Rascunho de resposta ao parceiro, ajuste de lista de prospecção, priorizar o lote, encaminhar a outra área, corrigir dado no rascunho do CRM, formato de relatório | A pessoa dona da entrega (Daniela, Jenifer, Geovana) com o gerente da área de agentes | Não. Vai no resumo semanal |
| **Técnica de caso** | Tese aplicável a um cliente, documento a pedir, prazo de um despacho | Time técnico ou advogado humano, com a pré-análise da área | Não, salvo se mudar regra |
| **Encaminhamento de produto pronto** | Mandar oportunidade à Save Invest, ao Jurídico ou ao Paulo | Contas e Soluções, com aviso ao dono do produto | Não |
| **Regra, preço, meta ou remuneração** | Honorário, repasse, meta, tese na vitrine, frase permitida | Luis (com o Conselho quando valer) | Sim |
| **Produto novo ou em validação** | Condição dita ao cliente, G0 a G4, parceria | Luis com o dono do produto (João, Paulo, Junior) | Sim |
| **Material externo em escala** | Campanha, kit, envio em massa | Luis vê um exemplo antes | Sim, só o exemplo |
| **Irreversível ou com exposição** | Envio a cliente, contrato, assinatura, publicação, gasto | A pessoa responsável, com aprovação explícita | Conforme a regra da casa |

**Limites para subir ao Luis:** muda regra; mais de R$ 1 mi de crédito com decisão; envolve 3 ou mais áreas em conflito; produto em validação; risco jurídico ou de LGPD sem precedente na base.

## 2. Recomendação que vale por padrão
- Cada item da folha de decisões traz `padrao: true` quando é **reversível e dentro das regras**. Esses itens mostram na coluna "Se não responder" a frase "vale a recomendação em <prazo>".
- Na consolidação de sexta, o item `padrao: true` sem resposta e com prazo vencido é aplicado com a recomendação das áreas. Ele é registrado como "aplicado por padrão" em `conselho/decisoes.md` e aparece no resumo para o Luis poder reverter.
- Não valem por padrão: preço, meta, remuneração, tese na vitrine, frase permitida, produto em validação, contrato, envio externo e qualquer coisa irreversível. Esses itens ficam na folha até a resposta.
- O Luis reverte a qualquer momento: basta marcar "Reprovar" no item.

## 3. Onde se aplica
- `infra/folha_decisoes.py`: coluna "Se não responder" e campo `padrao`.
- `rotinas/consolidacao-semanal.md`: passo 7 aplica os itens vencidos com `padrao: true`.
- `skills/gabinete` (matriz-roteamento §0.3) e `skills/central-agentes`: usam a seção 1 para decidir se o pedido sobe.
- Skills das áreas e células: cada uma diz o que é da dona da entrega e o que sobe (seção 4).

## 4. O que saiu do Luis em 23/10/2026 (D98)
Varredura das skills, rotinas, `infra/` e `lib/` em 23/10/2026. O Luis pode reverter qualquer linha: basta dizer qual. Fica com ele o que está na seção 1 (regra, preço, meta, remuneração, tese na vitrine, frase permitida, produto em validação, exemplo de material em escala, conflito de canal e os limites).

| Item | Novo dono | Onde mudou |
|---|---|---|
| Aprovar os chamados das demandas da Daniela (kit C5; antes D91) | Daniela, no painel; o Luis só chamado que toque regra, preço, conflito de canal ou produto em validação | `infra/fluxo-unico.md` §5; `skills/celula-daniela/references/especialistas/triagem-sla.md`; `skills/depto-ti/references/especialistas/administrador-glpi-automacao.md`; `skills/conselho-partners/references/especialistas/operacoes-tecnologia.md` |
| Decidir os lotes do Recuperador e as lacunas do Revisor, e aprovar os chamados que saem deles (kit C5) | Geovana | `skills/recuperador/SKILL.md`; `skills/revisor-diagnostico/SKILL.md`; `rotinas/recuperador-lote-semanal.md` |
| Canal e frequência da entrega do Revisor | Geovana (pasta dela, D91; e-mail como a D27 quando o Graph ligar) | `skills/revisor-diagnostico/SKILL.md`, `references/perguntas-ao-dono.md` (7), `lacunas-por-perfil.md` |
| Plano de conta e QBR de todos os Masters, inclusive os Estratégicos | Daniela; o Luis só em meta, repasse, condição comercial ou compromisso financeiro | `skills/celula-daniela/references/especialistas/gestor-contas-chave.md`; `perguntas-ao-dono.md` (CD4, por padrão em 28/10) |
| Reclamação de parceiro (`QLD-RECLAMACAO`) e S1 | Daniela com o `depto-qualidade`, com aviso ao Luis; ele decide só exposição pública ou saída de Master Estratégico | `skills/celula-daniela/SKILL.md`; `skills/depto-qualidade/` (SKILL, reclamacoes, ouvidoria, equipe, casos-teste) |
| Lista "vai para o Luis" da Central Masters | Reduzida à alçada; o resto fica com a Daniela | `skills/celula-daniela/references/roteamento.md` |
| Escala de cobrança das áreas (1, 3 e 5 dias úteis) | Daniela (vale por padrão em 28/10) | `skills/celula-daniela/references/perguntas-ao-dono.md` (CD2) |
| Liberar contato direto quando o Master não responde no SLA | Daniela com o Master, caso a caso (a regra geral segue com o Luis) | `skills/celula-jenifer/references/` (cadencia, qualificacao, prospeccao-outbound) |
| Cadência v1, SLA de aceite, definição de SQL, Master na 1ª reunião | Jenifer e Daniela (valem por padrão em 28/10) | `skills/celula-jenifer/references/perguntas-ao-dono.md` (5, 11, 15), `criterios-qualificacao.md`, `cadencia.md`, `scripts/followup.py` |
| Master quer atuar em segmento novo ou quer sub-indicadores | Daniela confirma com o Master (remuneração do sub-indicador segue com o Luis) | `skills/celula-jenifer/SKILL.md`, `scripts/lista_master.py`; `skills/depto-intel-comercial/references/especialistas/recrutamento-parceiros.md` |
| Prévia da lista de prospecção D&S | Jenifer | `skills/celula-jenifer/scripts/prospeccao_ds/README.md` |
| Etapas do pipeline BDR e owner ID; campos novos no HubSpot | Time de CRM | `skills/celula-jenifer/references/registro-hubspot.md`; perguntas de Dados, Marketing, Partner Success e Resultados |
| ICP de recuperação, pesos do scoring, ordem de praças | Gerente da Inteligência Comercial com a Jenifer (por padrão em 3 dias úteis) | `skills/depto-intel-comercial/` (SKILL, arquiteto-icp, lead-scoring-lookalike, receita_cnpj.py) |
| ICP e limiares de FIDC e Gestão de Contas; aprovação dos rascunhos da Save Invest | Junior | `skills/depto-save-invest/`; `skills/depto-intel-comercial/references/casos-teste.md` |
| Tax internacional e comex (produtos prontos): rascunho, honorário dentro do cardápio, escalonamento | Paulo e João Mattos (com o Jurídico em risco) | `skills/depto-internacional/` (SKILL, tax-internacional, equipe, gerente-produtos-internacionais) |
| Encaminhar produto pronto (Save Invest, tax internacional, cross-sell) | Contas e Soluções, com aviso ao dono do produto; a Daniela aprova o chamado | `skills/depto-solucoes/`, `skills/depto-save-invest/SKILL.md`, `skills/depto-internacional/references/tax-internacional.md` |
| Mapa de valor e ordem das ondas da conta antes de ir ao Master | Daniela com o gerente de Contas e Soluções | `skills/depto-solucoes/` (SKILL, gestor-de-valor, arquiteto-esteira-mapa-conta, casos-teste) |
| Deck do diagnóstico de um cliente | Técnico do caso e Daniela; o Luis só fora do modelo, acima de R$ 1 mi de crédito ou em escala | `skills/apresentacao-diagnostico/` |
| Aprovar pedido de contrato e de distrato; negociação dentro da regra de honorário | Daniela; área de Contratos (desconto e valor fixo seguem com o Luis) | `skills/depto-contratos/` (SKILL, modelo-pedido, distratos-cobranca) |
| Medida judicial de cobrança (degrau D4) | Advogado com Contratos; sobe ao Luis acima de R$ 1 mi, com conflito com o Master ou sem precedente | `skills/depto-contratos/references/especialistas/distratos-cobranca.md` |
| Conferência, aprovação do extrato e pagamento de repasse já definido | Financeiro (o percentual segue com o Luis) | `skills/depto-operacoes-canal/` (SKILL, analista-comissionamento, extrato-prestacao-contas, conferencia_repasses.py); `skills/depto-pos-venda/references/calendario-mensal.md` |
| Rascunhos do Pós-venda e dono da recorrência | Daniela e Geovana | `skills/depto-pos-venda/` |
| Tese aplicável ao caso, materialidade, fundamento no catálogo, ajuste da matriz do Recuperador | Time técnico tributário; a Geovana na matriz | `skills/depto-tributario/references/perguntas-ao-dono.md` |
| Monitorar a Caixa Postal do e-CAC | Advogado, com Contratos e Pós-venda | `skills/depto-juridico/references/perguntas-ao-dono.md` |
| Especificações e chamados de TI, papéis de acesso previstos, rotina que já existe, regra técnica do GLPI | Gerente de TI com a área dona; TI da Save | `skills/depto-ti/` |
| Escopo `files` do HubSpot e Private App | TI da Save (administrador do HubSpot) | `skills/recuperador/references/perguntas-ao-dono.md`, `scripts/pareceres.py` |
| Mapa de campos, roster, retenção de fotos, definição do pipeline (D12, D74) | Gerente de Dados com o CRM, o Controller, a Daniela e o Jurídico | `skills/depto-dados/`; `skills/depto-resultados/` |
| Formato e método do relatório de resultados | Controller (`depto-resultados`); meta e envio à diretoria seguem com o Luis | `skills/depto-resultados/SKILL.md` |
| Peça avulsa, peça interna, ajuste de calendário e jornal interno | Dona da entrega e gerente de Marketing (o Luis vê só o exemplo em escala) | `skills/depto-marketing/` |
| Academia, Master padrinho, propriedades no HubSpot, devolutiva do Conselho de Parceiros | Gerente de Partner Success, Daniela, Jenifer, técnico e advogado | `skills/depto-partner-success/` |
| "Ok" da Ficha de Rota e conflito sem regra entre 2 áreas | Dona da entrega; recomendação do Consolidador por padrão em 3 dias úteis | `skills/gabinete/` (SKILL, matriz-roteamento §0.3, roteador, consolidador, casos-teste CT-06) |
| Recomendação operacional da ata do Conselho | Dono da entrega ("Encaminhado ao dono"); reversível sem dono leva `padrao: true` | `skills/conselho-partners/` (SKILL Passo 5, formato-ata, presidente); `rotinas/conselho-reuniao-semanal.md` |
| Correção técnica do auditor (sem mudar o critério) | Arquiteto de Agentes | `skills/arquiteto-agentes/` |
| Ação de qualidade, defeito recorrente, mudar skill de outra área | Gerente da área dona da causa | `skills/depto-qualidade/` |
| 30 decisões pendentes do Conselho | 11 delegadas, 4 aplicadas por padrão, 15 superadas (ficam 19 com o Luis) | `conselho/decisoes.md` (D98); `docs/revisao-2026-10-22/decisoes.json` (itens 18 a 20) |

**Continuam iguais:** nada sai a cliente ou parceiro sem aprovação humana (agora pode ser a dona da entrega); HubSpot e GLPI só leitura e rascunho; merge e push do git com o Luis; resumo semanal e cópias informativas ao Luis.
