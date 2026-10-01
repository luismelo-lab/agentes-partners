# Modelos de mensagem — Pós-venda (v1)

> Rascunhos para a Daniela/área aprovar e enviar. Linguagem clara, sem jargão desnecessário, **sem prometer** prazo, valor ou resultado.
> Palavras proibidas: "garantido", "certo", "com certeza vai cair", "em X dias você recebe". Use: "previsão", "em análise pela Receita", "assim que houver movimentação".
> Valores só com fonte (sistema + data). Dados fiscais do cliente não vão em grupo com terceiros.

## M1 — Aviso mensal de pagamento (ao cliente; enviado pela área)
```
Assunto: <RAZÃO SOCIAL> — aviso de honorário referente a <mês/ano>

Olá, <nome>.
Em <mês/ano> houve a seguinte movimentação no seu pedido de ressarcimento de PIS/COFINS:
• Valor ressarcido pela Receita: R$ <…> (<data da ordem bancária | compensado de ofício em <data>>)
• Honorário conforme contrato (<x%>, cláusula <n>): R$ <…>
• Vencimento: <data> · Forma: <boleto/PIX conforme o Financeiro>
O extrato completo segue anexo. Qualquer dúvida, fale com a gente ou com <parceiro>.
<assinatura da área>
```
Checagem antes de enviar: base do honorário confere com o contrato? A parcela compensada de ofício entra na base? (ver `compensacao-de-oficio.md`, pontos para o Jurídico).

## M2 — Compensação de ofício: consulta ao cliente (via parceiro)
```
Oi, <parceiro>! A Receita enviou à <empresa> uma comunicação dizendo que pretende usar parte do ressarcimento para quitar um débito que consta em nome da empresa:
• Débito indicado: <tributo> · <período> · R$ <…>
• Prazo para a empresa responder: até <data> (15 dias da ciência — IN RFB 2.055/2021, art. 92, § 3º). Sem resposta, a Receita entende que a empresa concorda.
Precisamos saber do cliente, até <prazo interno>: esse débito está correto e em aberto, ou já foi pago/parcelado?
Se concordar, a Receita quita o débito e paga o saldo. Se discordar, o valor fica retido até o débito ser resolvido. A área de Pós-venda orienta o próximo passo.
```

## M3 — Status do crédito ao parceiro (resposta pontual)
```
Oi, <nome>! Status da <empresa> em <data>:
• Pedido(s) de ressarcimento: <n> transmitido(s), período <…>
• Situação: <em análise pela Receita | deferido em <data> | pago em <data> | compensado de ofício em <data>>
• Próximo passo: <o que a área está fazendo / o que precisamos do cliente>
Ainda não há previsão oficial de data de pagamento: o prazo é da Receita. Assim que houver movimentação, te aviso.
```

## M4 — Extrato de pagamento e saldo de créditos (anexo, por cliente)
| Período do crédito | PER nº | Transmitido em | Valor pedido | Situação | Deferido | Compensado de ofício | Pago (OB) | Saldo em análise | Honorário faturado | Honorário recebido | Fonte / data |
|---|---|---|---|---|---|---|---|---|---|---|---|
Rodapé obrigatório: `Extrato gerado em <data> com base em <sistema/planilha> extraído em <data>. Valores sujeitos à análise da Receita Federal.`

## M5 — Resumo mensal ao Master (carteira)
```
Oi, <nome>! Resumo de <mês> da sua carteira na Save:
• Clientes com pagamento da Receita no mês: <n> (R$ <…>)
• Em análise: <n> · Com pendência do cliente: <n> (lista abaixo)
• Pendências que dependem de vocês: <empresa — o que falta>
Obrigado pela parceria! Qualquer dúvida sobre um cliente específico, é só chamar.
```
(O repasse ao parceiro é comunicado pelo `depto-operacoes-canal`, não aqui.)

## M6 — Lembrete de honorário em atraso (ao cliente; tom cordial)
```
Olá, <nome>. Não identificamos ainda o pagamento do honorário de <mês> (R$ <…>, vencido em <data>), referente ao ressarcimento recebido em <data>.
Se já pagou, desconsidere e, se puder, nos envie o comprovante. Se precisar de uma nova via, é só responder.
```
Nunca ameaçar, nunca citar protesto/negativação sem decisão do Jurídico/Financeiro.

## M7 — Pedido interno à área de Pós-venda (quando falta dado)
```
[PEDIDO · PÓS-VENDA] <RAZÃO SOCIAL> — Master <parceiro> — negócio <link HubSpot>
Preciso de: <status dos PER | extrato | saldo | comunicação de compensação de ofício | guia>
Motivo: <pergunta do parceiro em <data>>   ·   Prazo desejado: <data> (<normal | urgente: prazo legal em <data>>)
```
