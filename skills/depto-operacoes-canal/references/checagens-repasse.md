# Checagens da conferência de repasses (v1 · 29/09/2026)

Fonte da verdade dos códigos: dicionário `REGRAS` em `scripts/conferencia_repasses.py` (esta página explica o porquê). Limites em `config-canal.json`.

## Fórmulas
- **Honorário contratado (R$)** = valor do negócio (crédito) × `honorarios_contratuais`
- **Repasse calculado (R$)** = honorário contratado × `honorarios_parceiro`
- Mesma fórmula do `depto-resultados/calc_semana.py` (confere com a margem da carteira).
- Escala: o download divide por 100 todo valor > 1 (30 → 0,30). Consequências: `1` é ambíguo (1% ou 100%?) e `125` vira 125%.

## Status da linha
| Status | Significa | O que fazer |
|---|---|---|
| **Bloqueado** | Não dá para calcular o repasse com segurança (algum código que "bloqueia") | Corrigir no CRM antes de qualquer extrato |
| **Revisar** | Calculável, mas com ponto a confirmar | Confirmar com o dono indicado |
| **OK (aguarda dado de pagamento)** | Nenhum achado | Ainda não é "a pagar": falta o recebimento |

## Códigos (resumo)
- **C — campos vazios:** C01 % honorário · C02 % parceiro (com parceiro) · C03 % parceiro (sem parceiro) · C04 CNPJ vazio/inválido · C05 sem data de fechamento
- **O — outliers:** O01 honorário > 50% · O02 honorário = 0 · O03 parceiro > 100% · O04 parceiro > 50% · O05 crédito ≤ 0 · O06 crédito > R$ 50 mi · O07 outra comissão > 100% · O08 parceiro = 1 (ambíguo)
- **I — inconsistências:** I01 soma das comissões > 100% · I02 Master com 0% · I03 % parceiro sem parceiro · I04 nome do parceiro numérico · I05 mesmo CNPJ + mesmo valor em 2+ ganhos · I06 indicador e parceiro ao mesmo tempo

## Hipóteses que o script escreve (não são conclusões)
- **Inversão 70/30:** quando honorário > 50% e honorário + parceiro ≈ 100%, o campo de honorário provavelmente guarda a *parte da Save* e não o % sobre o crédito. Achado de 29/09: 60 dos 61 casos > 50% são 70% + 30% (ou 60% + 40%), todos fechados em 2025, JGM e fora do roster.
- **"125":** 7 ganhos com 1,25 em % parceiro **e** em % gestor comercial ao mesmo tempo — digitação de 12,5% ou 1,25%.
- **Duplicidade (I05):** na amostra de 29/09 os pares têm o mesmo CNPJ, valor e data, geralmente um com tese e outro sem — cara de card duplicado, não de dois créditos.

## Pontos em aberto (não resolvidos pelo script)
- Base de `honorarios_vendedor / gestor_comercial / indicador / coordenador` (% do honorário? do crédito?) e se descontam do parceiro. I01 assume a mesma base do % do parceiro.
- Nenhum campo de pagamento/recebimento preenchido → não há conferência contra caixa.
- O S&OE tinha 10 repasses com erro ×10.000 (escala % aplicada duas vezes); a conferência lê só o HubSpot. Quando o S&OE voltar, comparar os dois.
