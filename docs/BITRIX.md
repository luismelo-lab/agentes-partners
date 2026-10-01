# Pedido à TI: acesso de consulta ao Bitrix24 para os agentes da Área Partners

**Para quê:** saber, todo dia, se cada negócio ganho entrou em execução e em que fase está. Isso alimenta o plano do dia do time Partners e as respostas de status aos parceiros (pós-venda).
Os agentes **só consultam**. Não criam, não editam e não movem cards.

## O que pedimos
Um **webhook de entrada** (Aplicativos → Recursos de desenvolvedor → Outro → Webhook de entrada) com:

| Item | Valor |
|---|---|
| Permissão | **CRM** (`crm`) |
| Usuário dono do webhook | um usuário técnico com papel de acesso **somente leitura** em Negócios, **Execução Lucro Real** e **Execução Holding** (o webhook herda as permissões do usuário) |
| Nome | `Agentes Partners - consulta execução` |

Envie o endereço gerado (`https://save.bitrix24.com.br/rest/<usuário>/<código>/`) **só ao Luis**, por canal interno. Ele grava a chave no Mac dele (arquivo `.env`, fora do repositório e do backup em texto). Os agentes nunca imprimem nem registram esse endereço.

## Métodos que os agentes usam (o programa bloqueia qualquer outro)
`crm.item.list` e `crm.item.get` (processos 162 e 152), `crm.deal.get`, `crm.status.list`, `crm.category.list`.

## Volume
Uma consulta por dia (7h30), cerca de 60 chamadas em lote de 40 negócios, bem abaixo do limite do Bitrix.

## Como testar depois de criado
```
python3 ~/agentes-partners/lib/bitrix.py testar
python3 ~/agentes-partners/lib/bitrix.py baixar
```
