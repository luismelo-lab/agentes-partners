# Dicionário de métricas — Partner Success

Calculadas por `~/agentes-partners/departamentos/partner-success/scripts/metricas_ps.py` sobre o download do HubSpot. Data de referência = data do download.

| Métrica | Definição | Observação |
|---|---|---|
| **Data efetiva do negócio** | Menor entre criação e fechamento | As importações de nov/2025 e fev/2026 regravaram a criação (1.396 negócios com fechamento anterior à criação) |
| **Parceiro** | Roster dos 9 Masters (`mapeamento-hubspot.json`); fora do roster, nome bruto normalizado (`~/agentes-partners/departamentos/partner-success/scripts/aliases-parceiros.json`) | Nome vazio ou numérico = "(sem parceiro informado)", fora das contagens de parceiros |
| **Consultor/indicador do Master** | Nome bruto dentro de um Master; variações da razão social do próprio Master = "(escritório)" | Proxy de indicador enquanto não existe cadastro próprio |
| **Ativo** | ≥ 1 negócio com data efetiva nos últimos 90 dias | **Mesma regra** do relatório semanal (`depto-resultados/references/metricas.md`) |
| **Produtivo** | ≥ 1 ganho com fechamento nos últimos 365 dias | |
| **Classe** | Ativo e produtivo · Ativo em rampa (ativo sem ganho em 12m) · Dormente (sem negócio em 90d, com ganho em 12m) · Inativo | Dormente = prioridade de conversa |
| **Tempo até o 1º negócio ganho** | Dias do início até o fechamento do 1º ganho. Início = data de entrada informada (`~/agentes-partners/departamentos/partner-success/scripts/datas-entrada-parceiros.json`) ou, se vazia, o 1º negócio registrado | "Anterior à base" (1º registro nos 90 primeiros dias da base) e "estimada (importado)" ficam fora da mediana |
| **Atividade por trimestre** | Criados (data efetiva), criados importados, ganhos e perdidos (data de fechamento), valor ganho, conversão = ganhos ÷ (ganhos + perdidos) | Trimestre corrente marcado "(parcial)" |
| **Parceiros ativos no trimestre** | Parceiros com ≥ 1 negócio com data efetiva no trimestre | Trimestres até 2025 são quase todos importados (histórico do Bitrix) |
| **Nível simulado** | Proposta v1 de níveis aplicada aos dados (critérios no topo do script) | Rascunho; usa o scorecard do Depto Dados para conversão e qualidade do dado |
| **Índice de saúde** | **Não calculado aqui.** Ver `depto-dados` | |
