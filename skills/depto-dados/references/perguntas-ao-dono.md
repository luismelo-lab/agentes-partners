# Perguntas ao dono · Departamento de Dados & BI

Data: 22/10/2026. Dono da área: gerente de Dados; o Luis responde só o que é regra, preço, meta ou repasse. Reclassificado em 23/10/2026 (`infra/alcadas.md`). O que só o humano responde, por que importa e quem mais precisa ser ouvido. Ao responder, registre a data e, se virar regra, o D-número.

| # | Pergunta | Por que importa | Quem responde | Especialista |
|---|---|---|---|---|
| 1 | Quem no time de CRM da Save executa a mescla dos duplicados e em que lotes por semana? | A lista de saneamento (D87) só vira dado limpo com quem execute; define o ritmo e quando a carteira do dossiê pode rodar | Time de CRM | Qualidade e Saneamento |
| 2 | Matriz e filial com a mesma tese contam como um negócio ou dois? | Muda o bloqueio por raiz de CNPJ e o número de excedentes (hoje 321 a 332 candidatos contra os ~295 da folha) | Time técnico (Geovana) com o gerente de Dados | Qualidade e Saneamento |
| 3 | Mesclar no HubSpot preserva atividades e anexos? Se não, arquivar o perdedor em vez de mesclar? | Mescla mal feita perde histórico de parecer e diagnóstico | Time de CRM | Qualidade e Saneamento |
| 4 | Os 143 honorários atípicos e os 9 % de parceiro acima de 100% têm exceções aprovadas registradas (D65)? | Separa exceção válida de erro; sem isso a lista mistura os dois | Luis + Jurídico | Qualidade e Saneamento |
| 5 | Qual a definição oficial de pipeline para a diretoria (R$ 180,6 mi × R$ 123,6 mi, D74)? | Sem regra de escopo, cada relatório mostra um número | Gerente de Dados com o gerente de Resultados (vale a recomendação em 28/10/2026; o Luis pode reverter) | Governança e Dicionário |
| 6 | A propriedade "Produto" fica no negócio (opção A) ou em pipeline próprio (B), e "produto de entrada" fica na Empresa? (D37, D57) | Sem o campo não há funil por produto em 2027 nem medição de cross-sell | Time de CRM com o gerente de Dados (vale a recomendação em 28/10/2026; o Luis pode reverter) | Governança e Dicionário |
| 7 | O Financeiro tem fonte de valor recebido por negócio? Vai virar campo no HubSpot? | Sem ela o ROI realizado segue "[sem dado de caixa]" (D17) | Financeiro | Engenharia de Dados |
| 8 | O roster de parceiros e consultores do `mapeamento-hubspot.json` está confirmado ("CONFIRMAR" no arquivo)? | Define o escopo da Área Master e todas as contagens por parceiro | Daniela | Engenharia de Dados |
| 9 | O HubSpot já aceita CNPJ alfanumérico no campo de CNPJ? Quem ajusta os scripts que limpam "só dígitos"? | Desde julho de 2026 (IN RFB 2.229/2024) a raiz pode ter letras; o dedupe por raiz quebra | Time de CRM + depto-ti | Engenharia de Dados |
| 10 | Qual retenção das fotos diárias do HubSpot (proposta: diárias 90 dias, semanais 24 meses)? | LGPD (necessidade) e capacidade de recalcular o passado | depto-juridico com o gerente de Dados | Engenharia de Dados |
| 11 | Os pesos do índice de saúde (30/25/25/20) continuam ou a conversão passa a pesar mais no Q4 (D20)? | Muda as cores do scorecard e as conversas com os Masters | Gerente de Dados com a Daniela (vale a recomendação em 28/10/2026; o Luis pode reverter) | BI e Visualização |
| 12 | Qual valor mínimo para um negócio parado entrar na lista acionável da Daniela (D47)? | Corta ruído; hoje são 100 parados, R$ 52,6 mi | Daniela | BI e Visualização |
| 13 | O NPS dos parceiros entra no índice de saúde? | Proposta da Qualidade; exige base de respostas que ainda não existe | Gerente de Dados com o `depto-qualidade` (vale a recomendação em 28/10/2026; o Luis pode reverter) | BI e Visualização |
| 14 | Qual peso da prior (m) e qual trimestre serve de validação fora da amostra do look-alike? | Sem validação, o lift do Recuperador e das listas da Jenifer é desconhecido | Gerente de Dados com a Geovana | Estatística Aplicada |
| 15 | Os números de tema (Tema 69 STF, Tema 779 STJ) e a probabilidade por tese que o modelo usa são validados pelo Técnico? | O look-alike carrega o risco de cada tese; precisa de dono técnico | Técnico tributário | Estatística Aplicada |

**Itens [não confirmado] nesta base (conferir no texto oficial):** texto integral da IN RFB 2.119/2022 com a redação da IN RFB 2.229/2024 (Anexo XV); faixa de mercado de 10% a 30% de duplicidade em migrações de CRM; acórdãos dos Temas 69 e 779 (não relidos nesta rodada); art. 6º e art. 10 da Resolução CD/ANPD nº 15/2024 (conferidos só em fontes secundárias); número de US$ 12,9 mi da Gartner (citação secundária).
