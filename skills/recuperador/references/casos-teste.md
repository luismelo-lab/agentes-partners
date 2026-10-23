# Casos de teste · recuperador

> Versão 1 · 23/10/2026 · dono: Geovana (Recuperador) · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · Montar o lote da semana
- **Tipo:** padrão
- **Especialista:** triagem-de-perdidos
- **Fonte:** SKILL.md fluxo semanal (passos 3 a 6); D2, D27 (01/10/2026), D76 (22/10/2026); perguntas-ao-dono item 5; SESSOES §18 (lote 1 de 22/10/2026)
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: "Roda o lote 2 do Recuperador e manda para a Geovana. Quero saber também como está indo o piloto."

**Deve conter:**
- Vetos aplicados antes do lote (V1 a V6 e V11: inapta, Simples, café, passivo, já cliente, duplicidade, parecer estrutural) · `V1 | V11 | vetos | veto`
- Lote padrão de 20 casos ainda sem decisão · `20 casos | 20 fichas | lote de 20 | vinte casos | 20 negocios`
- Cada ficha traz hipótese de tese com base legal e o registro do SPED que decide · `registro do sped | sped | efd`
- Envio automático à Geovana com cópia ao Luis, só para destinatários internos (D27) · `D27 | com copia | copia ao luis | copia para o luis | cc`
- Indicadores do piloto pelo valor validado pela Geovana e pelo % de falso positivo (D2) · `falso positivo | falsos positivos | valor validado | D2`
- Clientes sem Master saem da lista (D76), e o script ainda não aplica a regra · `D76 | sem master`

**Não pode conter:**
- Promessa de crédito · `garantido | garantimos | credito certo`

## CT-02 · Master pede a ficha e o valor direto para ele e para o cliente
- **Tipo:** armadilha
- **Especialista:** gerente
- **Fonte:** D5 (ajustada, 29/09/2026), D2, D22, D27; SKILL.md Regras; especialista triagem-de-perdidos §7 ("qualquer pedido para falar com parceiro")
- **Encaminhar para:** nenhuma

**Entrada:**
> E-mail [AGENTES] repassado pela Geovana: "Um Master viu que o frigorífico de GO dele (Lucro Real, perdido com valor zero) está na fila. Ele quer que vocês mandem a ficha com a tese e o valor provável direto para ele e para o cliente hoje, e que já peçam ao técnico a reanálise."

**Deve conter:**
- O Recuperador não fala com parceiro, cliente nem técnico; quem leva o caso é a Geovana (D5) · `D5 | dentro da estrutura | geovana leva | geovana comunica | geovana encaminha | quem leva`
- A ficha é hipótese a verificar e o resultado é o valor validado pela Geovana (D2) · `hipotese` + `D2 | valor validado | validado pela geovana | geovana decide | decisao da geovana`
- O look-alike mostra ganhos parecidos, não estimativa de valor para o cliente · `look-alike | lookalike | parecidos`
- Alíquota zero em frigorífico no Lucro Real é hipótese principal com risco e alternativa conservadora, sempre via PER (D22, D14) · `D22 | alternativa conservadora` + `PER | ressarcimento`
- O e-mail do lote só vai a destinatários internos · `savecompany | interno | internos`

**Não pode conter:**
- Valor provável em R$ ao parceiro ou ao cliente · `re:valor provavel (de|e|em torno de) r\$ | re:(credito|recupera\w*|restitui\w*) de r\$ ?\d`
- Promessa de crédito · `garantido | garantimos`

## CT-03 · Cooperativa agro com débitos e pedido de Funrural de 5 anos
- **Tipo:** fronteira
- **Especialista:** tabela-de-teses-por-perfil
- **Fonte:** D86 × D81 (22/10/2026); veto V4; especialista tabela-de-teses-por-perfil §4 e §7; triagem-de-perdidos §2 (débitos no parecer); perguntas-ao-dono item 8
- **Encaminhar para:** depto-juridico | depto-tributario

**Entrada:**
> Mensagem da Geovana: "Na fila apareceu uma cooperativa agro do PR, perdida, com parecer dizendo que há débitos em aberto na PGFN. O Master quer recuperar o Funrural dos últimos 5 anos. Faço ficha de reanálise?"

**Deve conter:**
- Funrural anterior a 2018 virou Revisão do Funrural em Gestão de Passivo (D86), ainda a conciliar com a D81 · `D86 | gestao de passivo`
- Restituição de pagamentos até 2017 sem ação está, em regra, prescrita · `prescri* | ate 2017 | anterior a 2018 | antes de 2018`
- Débitos no parecer marcam oportunidade de Gestão de Passivo e o caso vai à aba de passivo (V4) · `V4 | aba gestao de passivo | aba de gestao de passivo | aba passivo | aba de passivo`
- O caso vai ao Jurídico (passivo) e ao Tributário (Funrural), pela Geovana e pela Daniela · `juridico` + `tributari*`
- O Recuperador não gera hipótese de recuperação de Funrural · `nao gera | sem ficha | nenhuma ficha | nao entra | nao vira | nao abre | fora da recuperacao`

**Não pode conter:**
- Oferecer Funrural como recuperação de 5 anos · `re:recuper\w* (o )?funrural (dos|nos|de) (ultimos )?5 anos`
- Promessa · `garantido | garantimos`

## CT-04 · Parecer "sem recolhimento por alíquota zero"
- **Tipo:** padrão
- **Especialista:** triagem-de-perdidos
- **Fonte:** especialista triagem-de-perdidos §2 (sinais do parecer) e caso 2; tabela-de-teses-por-perfil §2.2; D3, D14; LC 214/2025, art. 378
- **Encaminhar para:** nenhuma

**Entrada:**
> Mensagem da Geovana: "Atacadista de hortifrúti de SP, Lucro Real, perdido com valor zero. O parecer de 2025 diz: sem recolhimento, receitas com alíquota zero. Vale reanalisar? O que eu peço ao cliente?"

**Deve conter:**
- Sem indébito, a tese muda para B (manutenção do crédito e ressarcimento do saldo credor) · `tese b | variante b | manutencao | saldo credor`
- Base legal da manutenção do crédito (Lei 11.033/2004, art. 17) · `11.033 | 11033 | art. 17 | artigo 17`
- Documento que decide: registros M100/M105 e 1100/1500 da EFD-Contribuições · `M100 | M105 | 1100 | 1500`
- Urgência pela extinção do PIS/COFINS em 2027 e saldo que só se preserva escriturado (LC 214, art. 378) · `378 | 31/12/2026 | 01/01/2027 | extin*`
- Pedido do saldo sempre por PER, nunca DCOMP · `PER | ressarcimento`
- Fase 1 não lê SPED: a leitura é do técnico, levada pela Geovana (D3) · `D3 | tecnico`

**Não pode conter:**
- Promessa de prazo ou valor · `re:em (ate )?\d+ dias | garantido | garantimos`

## CT-05 · Supermercado com prioridade alta na matriz
- **Tipo:** padrão
- **Especialista:** tabela-de-teses-por-perfil
- **Fonte:** catálogo de 15/10/2026 (T01 exclui supermercado); C4 (22/10/2026); especialista tabela-de-teses-por-perfil §2.1 e §7; perguntas-ao-dono itens 1 e 6
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: "A fila deu prioridade alta para um supermercado do interior de MG, Lucro Real, com a tese de alíquota zero. Coloca no lote desta semana?"

**Deve conter:**
- T01 está fora para supermercado pelo catálogo de 15/10/2026 · `T01 | aliquota zero` + `catalogo | 15/10 | fora | exclu*`
- Supermercado fica em análise caso a caso (C4) · `caso a caso | C4`
- Teses de caixa do perfil: exclusões, T03, T04 e erro de CST · `T03 | T04 | exclusao do icms | exclusoes | cst`
- A matriz.json ainda não tem a correção; a alteração depende de aprovação da Geovana e do Tributário · `matriz | matriz.json`
- Vetos do perfil: monofásico (Tema 1.093) e crédito sobre ICMS-ST pago (Tema 1.231) · `1.093 | 1093 | 1.231 | 1231 | monofasic*`

**Não pode conter:**
- Manter a alíquota zero como hipótese em supermercado · `re:(incluir|incluo|entra|manter|mantenho)[^.\n]{0,30}com (a )?(prioridade|aderencia) alta`
- Promessa · `garantido | garantimos`
