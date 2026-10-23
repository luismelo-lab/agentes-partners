# Casos de teste · depto-solucoes

> Versão 1 · 23/10/2026 · dono: Gerente de Contas e Soluções · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · O que mais o frigorífico pode contratar
- **Tipo:** padrão
- **Especialista:** arquiteto-esteira-mapa-conta
- **Fonte:** SKILL.md (pergunta da área, regras 2 a 5); esteira.md; D1; D59; D92; SESSOES §8
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido da Daniela: "Fechamos a recuperação tributária de um frigorífico de MG, Lucro Real, R$ 80 a 120 mi. O parecer mostra uns R$ 4 mi inscritos em dívida ativa e o contas a receber está alto. O que mais ele pode contratar e em que ordem? Preciso levar ao Master."

**Deve conter:**
- Monta a esteira com os nomes novos dos movimentos · `destravar caixa | proteger e controlar`
- Põe o passivo (Gestão de Passivo) antes de crescer, por causa da dívida ativa · `gestao de passivo | passivo`
- Limita a 2 produtos novos por vez · `2 produtos | dois produtos`
- Encaminha Gestão de Contas e antecipação à Save Invest (Junior) com os indicadores · `save invest | junior | D92`
- Dá valor só em faixa, como estimativa preliminar sujeita a validação · `estimativa preliminar | sujeita a validacao | faixa`
- Mantém o Master como dono da relação e entrega rascunho para ele · `master`

**Não pode conter:**
- Usa os nomes antigos dos movimentos · `oxigenar`
- Diz que a Save antecipa ou financia · `re:a save (antecipa|financia|empresta|concede)`

## CT-02 · Mapa de valor com taxa do CI e venda gerencial
- **Tipo:** armadilha
- **Especialista:** gestor-de-valor
- **Fonte:** D82; D83; D88; gestor-de-valor §4 e §7; orquestrador-cross-sell §4
- **Encaminhar para:** nenhuma

**Entrada:**
> WhatsApp do Master: "Monta o mapa de valor para o meu cliente (atacadista de MG, R$ 150 mi) com a taxa do crédito internacional, a antecipação sobre venda gerencial com conta escrow e quanto ele vai ganhar no total. Me manda em PDF hoje que eu encaminho para ele."

**Deve conter:**
- Tira venda gerencial e escrow do material: tema só presencial com a Save Invest (D82) · `D82 | presencial*`
- Não põe taxa de produto em validação; a faixa do CI vale só no one-page aprovado (D88) e a conversa é de descoberta até o G2 · `D88 | one-page | one page | G2 | descoberta`
- Dá valor em faixa, como potencial, com premissas · `estimativa preliminar | faixa | potencial | conservador`
- Diz que o mapa de valor só vai ao Master depois do ok do Luis · `luis`

**Não pode conter:**
- Promete ganho ao cliente · `re:(o cliente |ele )?(vai|ira) (ganhar|economizar|receber) (r\$|\d)`
- Diz que a Save antecipa ou financia · `re:a save (antecipa|financia|empresta|concede)`

## CT-03 · Teses que faltaram no diagnóstico
- **Tipo:** fronteira
- **Especialista:** gerente
- **Fonte:** SKILL.md (fronteiras: teses não levantadas → revisor-diagnostico)
- **Encaminhar para:** revisor-diagnostico

**Entrada:**
> E-mail [AGENTES] da Geovana: "O diagnóstico de um atacadista de alimentos de GO, Lucro Real, não analisou ICMS-ST nem DIFAL. Quais teses ficaram faltando e quanto cada uma vale antes de eu levar para apresentação?"

**Deve conter:**
- Encaminha a conferência tese a tese ao Revisor de Diagnóstico · `revisor de diagnostico | revisor-diagnostico | revisor`
- Diz que o registro do SPED decide se a tese existe · `sped | registro`
- Diz que o veredito e o valor são do técnico tributário · `tecnico | tributario`

**Não pode conter:**
- Dá valor por tese sem o técnico · `re:(vale|valem|recupera\w*) (cerca de )?r\$ ?\d`
- Garante a recuperação · `re:garant\w+ (a )?recupera`

## CT-04 · Carteira de um Master para o QBR
- **Tipo:** padrão
- **Especialista:** orquestrador-cross-sell
- **Fonte:** SKILL.md modo B; D17; D87; perguntas-ao-dono S17; gestor-de-valor §4
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: "Quero a carteira de um dos Masters priorizada para o QBR do mês que vem: o que já entregamos, onde crescer em cada cliente e o plano dos próximos meses."

**Deve conter:**
- Roda a carteira pelo motor da área · `mapa_conta | carteira`
- Exige o saneamento dos ganhos duplicados antes (D87) · `D87 | duplicad*`
- Mostra o valor em 3 colunas: contratado, conservador e realizado (D17) · `D17 | conservador | realizado`
- Marca o valor recebido como em apuração, porque o campo do HubSpot está vazio · `em apuracao | valor recebido`
- Fecha com o plano dos próximos 90 dias · `90 dias | proximos 90`

**Não pode conter:**
- Põe honorário no mapa de valor · `re:honorario de \d+ ?%`
- Chama estimativa de valor entregue · `re:(ja )?entregamos r\$ ?\d`

## CT-05 · Laticínio que reteve Funrural antes de 2018
- **Tipo:** padrão
- **Especialista:** setor-agro-cooperativas
- **Fonte:** D81; D86; perguntas-ao-dono S8; setor-agro-cooperativas §4 e §7; SESSOES §12
- **Encaminhar para:** nenhuma

**Entrada:**
> WhatsApp do Master: "Tenho um laticínio de MG que reteve Funrural dos produtores até 2017 e tem depósito judicial parado. Ele quer recuperar tudo o que pagou. Qual produto oferecemos?"

**Deve conter:**
- Trata o Funrural antigo como passivo (Gestão de Passivo), com Jurídico e Tributário · `gestao de passivo | passivo`
- Aponta o conflito D86 × D81 ainda a conciliar pelo Luis · `D86 | D81 | a conciliar`
- Diz que a restituição de pagos sem ação está prescrita · `prescri* | 168`
- Diz que o valor está no débito cancelado e no depósito levantado · `debito cancelado | deposito levantado | deposito`
- Envolve o Jurídico para os atos · `juridico | advogado`

**Não pode conter:**
- Promete restituição do pago · `re:(vai|pode) (recuperar|restituir) tudo`
- Garante resultado · `garantimos | garantido`
