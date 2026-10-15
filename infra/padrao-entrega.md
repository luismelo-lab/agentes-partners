# Padrão de entrega: o que a pessoa precisa, não só o que ela pediu
**Regra do Luis (15/10/2026):** o objetivo não é entregar só o que foi pedido. É entregar o que a pessoa **precisa**. Se faltar dado, os agentes pedem o dado de forma objetiva. Vale para toda resposta: pedido, demanda, originação, alerta do plano do dia, relatório e chamado.

## Os três blocos (obrigatórios)
1. **O que você pediu / o que fazer:** a resposta conferida ("já vem conferido"), com a ação concreta e o rascunho pronto quando há parceiro ou cliente envolvido.
2. **O que você também precisa:** o que o especialista vê e a pessoa não pediu, como próximo passo, risco, prazo, oportunidade (recorrência, outra tese, passivo, outro produto) e o impacto em R$ quando houver.
3. **O que falta e quem fornece:** o dado que impede uma resposta completa, em uma frase. Diga de onde vem (HubSpot, Bitrix, e-CAC, parceiro, cliente, área) e quem pede ou fornece (Daniela, Geovana, parceiro, TI). Se nada falta, escreva "nada".

Formato nos arquivos: `fazer`, `precisa`, `falta` e `rascunho` (alertas do plano, `registro/analises-areas.json`). Na Central (`resposta.json`): `secoes` com o que foi pedido, mais `tambem` e `falta`.

## Quem responde cada assunto (sempre o agente da área, nunca texto de modelo)
| Assunto ou alerta | Agente da área (skill) |
|---|---|
| Contrato enviado ou assinado e parado | `depto-contratos` (com `depto-pos-venda` no assinado) |
| Ganho sem execução ou card no Bitrix, execução parada | `depto-pos-venda` (+ `depto-tributario` na execução técnica) |
| Conflito de canal, repasse bloqueado, % do parceiro | `depto-operacoes-canal` |
| Parceiro sem indicar, esfriando | `depto-partner-success` + `depto-marketing` (reativação) |
| Entrou em Apresentação de Diagnóstico | `revisor-diagnostico` + `apresentacao-diagnostico` |
| Diagnóstico parado, dúvida de tese | `depto-tributario` |
| Comercial ou apresentação parada | célula da dona (`celula-jenifer` ou `celula-daniela`) + `depto-marketing` |
| Cadastro incompleto | `depto-dados` + `depto-intel-comercial` (Receita) |
| Comunicado, despacho, intimação, prazo | `depto-juridico` (Controle de Prazos, com dupla checagem) |
| Originação | `depto-intel-comercial` + `depto-operacoes-canal` (conflito) + `depto-tributario` (pré-análise) |
| Recorrência, perdidos e zerados | `recuperador` + `depto-tributario` |
| Rascunho para parceiro ou cliente | passa por `depto-qualidade` (auditoria) antes de sair |

## O que não se faz mais
- Rascunho de modelo fixo ("Oi! Passando para alinhar…").
- Repetir a mensagem do parceiro como se fosse análise.
- Lista de "confira".
- Responder "só o que foi perguntado".
