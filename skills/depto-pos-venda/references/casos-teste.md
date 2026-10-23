# Casos de teste · depto-pos-venda

> Versão 1 · 23/10/2026 · dono: Gerente de Pós-venda · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · Comunicação de compensação de ofício com prazo correndo
- **Tipo:** padrão
- **Especialista:** compensacao-de-oficio-e-recebimento
- **Fonte:** SKILL.md regra 3 e modo B; especialista compensacao-de-oficio-e-recebimento §5 A e §7; perguntas-ao-dono itens 7 e 8
- **Encaminhar para:** nenhuma

**Entrada:**
> E-mail [AGENTES] da Daniela: "Cliente de um Master (atacadista de alimentos de GO, Lucro Real, PER deferido) recebeu na caixa postal do e-CAC uma comunicação de compensação de ofício. A mensagem foi disponibilizada em 14/10/2026 e ninguém abriu ainda. O débito indicado é de uma filial, multa por atraso de declaração. Qual é o prazo e o que fazemos?"

**Deve conter:**
- O prazo de 15 dias da IN RFB 2.055, art. 92, § 3º · `15 dias | quinze dias` + `2.055 | 2055 | art. 92 | artigo 92`
- A ciência eletrônica é a abertura ou o 15º dia após a disponibilização, o que vier antes · `ciencia tacita | ciencia | cientificad* | abertura da mensagem`
- Cálculo do prazo em dupla checagem e prazo interno de 5 dias antes do fatal · `dupla checagem | calculo 2 | segundo calculo | prazo interno | d-5`
- A Receita verifica débitos de todos os estabelecimentos, inclusive filial (art. 92, § 7º), e o débito deve ser classificado (pago, parcelado, suspenso) antes de decidir · `todos os estabelecimentos | paragrafo 7 | parcelad* | ja pago | suspens*`
- Concordar ou discordar é decisão do cliente orientado pelo Jurídico, e a mensagem é rascunho para a Daniela · `juridico | advogad*` + `rascunho | minuta | daniela`

**Não pode conter:**
- Tratar a compensação de ofício como DCOMP ou sugerir compensar o crédito por DCOMP · `re:\bcompens\w* (via|por|com|em|numa|uma) (per/)?dcomp`
- Prometer data de pagamento · `re:(recebe|recebera|vai receber|cai|sera pago)\w*[^.\n]{0,30}em (ate )?\d+ dias`

## CT-02 · Master pede DCOMP enquanto o PER não sai e texto com prazo de 360 dias
- **Tipo:** armadilha
- **Especialista:** ressarcimento-e-prazos
- **Fonte:** D14 (29/09/2026); SKILL.md regras 2 e 5; especialista ressarcimento-e-prazos §7 (prazo de decisão × pagamento; DCOMP enquanto o PER não sai; Selic desde o protocolo); D92
- **Encaminhar para:** nenhuma

**Entrada:**
> WhatsApp de um Master, repassado pela Daniela: "Meu cliente, frigorífico de MG no Lucro Real, transmitiu o PER da alíquota zero há 8 meses e está apertado de caixa. Dá para fazer uma DCOMP com esse crédito para abater o PIS/COFINS do mês enquanto o PER não sai? E me manda um texto dizendo que em no máximo 360 dias o dinheiro cai, com correção, para eu tranquilizar ele."

**Deve conter:**
- Alíquota zero sai só por PER (ressarcimento), nunca por DCOMP · `D14 | nunca dcomp | nunca por dcomp | nunca via dcomp | nao por dcomp | nao via dcomp | sem dcomp | so via per | so por per | somente via per | sempre via per | sempre por per`
- Os 360 dias são o prazo para a Receita decidir, não o prazo de pagamento (Lei 11.457/2007, art. 24) · `11.457 | 11457 | art. 24 | prazo para a receita decidir | prazo de decisao | prazo para decidir | para a receita decidir`
- A Selic só corre a partir do mês seguinte ao 361º dia, não desde o protocolo (STJ Tema 1.003; IN 2.055, art. 152) · `1.003 | 1003 | 361 | art. 152 | artigo 152 | apos os 360 | depois dos 360 | apos 360 | depois de 360`
- Mensagem ao parceiro em linguagem de previsão, sem prazo nem valor · `em analise pela receita | previsao | assim que houver | sem prometer | sem promessa`
- O aperto de caixa vira sinal para a Save Invest (antecipação ou Gestão de Contas), levado pela Daniela · `save invest | junior | antecipa* | gestao de contas`
- A resposta é rascunho para a Daniela aprovar · `rascunho | minuta`

**Não pode conter:**
- Sugerir DCOMP ou compensação do crédito da alíquota zero · `re:\b(compens\w*|abat\w*|usar|utilizar)\b[^.\n]{0,40}\b(via|por|com|em|numa|uma) (per/)?dcomp`
- Prometer pagamento em 360 dias · `re:(dinheiro|valor|credito|ressarcimento) (cai|sera pago|e pago|e depositado|entra)[^.\n]{0,20}em (ate|no maximo) 360 | re:em (ate|no maximo) 360 dias,? (o cliente |voce |ele )?(recebe|vai receber)`
- Promessa de êxito · `garantimos | garantido | com certeza`

## CT-03 · Master pergunta o próprio repasse depois do PER pago
- **Tipo:** fronteira
- **Especialista:** compensacao-de-oficio-e-recebimento
- **Fonte:** SKILL.md Interfaces (repasse é de Operações de Canal); especialista compensacao-de-oficio-e-recebimento §4 (D64, D78, D79) e §9; D64 (22/10/2026)
- **Encaminhar para:** depto-operacoes-canal

**Entrada:**
> WhatsApp de um Master: "O PER do meu cliente (distribuidora de hortifrúti de SP) foi pago mês passado. Quanto é o meu repasse e em que dia cai na minha conta?"

**Deve conter:**
- Repasse e extrato do parceiro são de Operações de Canal · `operacoes de canal | depto-operacoes-canal`
- O repasse nasce do honorário efetivamente recebido do cliente, não do valor deferido · `honorario recebido | recebido do cliente | apos o recebimento | depois do recebimento | cliente pagar | pagamento do honorario | recebimento do honorario`
- O percentual é o negociado com cada parceiro (D64), não uma regra única · `D64 | negociado | percentual do contrato | percentual do parceiro | % do parceiro | termo do parceiro | contrato do parceiro`
- O Pós-venda fornece o extrato do cliente e o arquivo de recebidos, com fonte e data, sem número de memória · `extrato | arquivo de recebidos | recebidos`
- A resposta ao Master passa pela Daniela · `daniela`

**Não pode conter:**
- Informar percentual ou valor de repasse sem extrato · `re:repasse (e|sera|fica|de) (de )?\d+ ?% | re:repasse (e|sera|fica|de) (de )?r\$`
- Prometer data de crédito · `re:(cai|pago|depositado|creditado) (em|ate|no dia) \d`

## CT-04 · Honorário sobre o valor compensado de ofício
- **Tipo:** padrão
- **Especialista:** compensacao-de-oficio-e-recebimento
- **Fonte:** D95 (22/10/2026); perguntas-ao-dono item 9 (respondida); especialista compensacao-de-oficio-e-recebimento §5 B e caso 2
- **Encaminhar para:** nenhuma

**Entrada:**
> E-mail [AGENTES] da área de Pós-venda: "Laticínio do PR teve o PER deferido: parte paga em conta e parte usada pela Receita para quitar um débito de IRPJ por compensação de ofício. O cliente reclamou do boleto de honorário sobre a parte compensada, diz que não recebeu dinheiro nenhum. Como montamos o aviso e o que respondemos?"

**Deve conter:**
- O honorário de êxito incide também sobre o valor compensado de ofício, considerando a Selic (D95) · `D95 | incide | incidencia`
- O aviso mostra em linhas separadas o pago em conta e o usado pela Receita para quitar o débito · `linhas separadas | separad* | pago em conta | usado pela receita`
- A base é conferida na cláusula de honorário do contrato (Contratos) antes de avisar · `clausula | depto-contratos`
- A explicação ao cliente e ao parceiro vem antes do faturamento, e o boleto é do Financeiro · `financeiro | antes do faturamento | explica*`
- Tudo é rascunho para a área real e a Daniela aprovarem · `rascunho | minuta | aprova*`

**Não pode conter:**
- Calcular o honorário sobre o valor deferido · `re:honorario (incide|e calculado|sera calculado) sobre o (valor )?deferido`
- Promessa ao cliente · `garantimos | garantido`

## CT-05 · Lista de recorrência do mês, com clientes sem Master
- **Tipo:** padrão
- **Especialista:** recorrencia
- **Fonte:** especialista recorrencia §4 (D76, D11, D66) e §5; perguntas-ao-dono item 10; LC 214/2025, art. 378
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: "Quero a lista de recorrência deste mês para levar aos Masters. Comece pelo frigorífico do RS, Lucro Real, cujo último PER foi do 2º trimestre de 2025, e inclua também os clientes da carteira direta que não têm Master."

**Deve conter:**
- Recorrência só com 6 ou mais competências novas depois do último período ressarcido · `6 ou mais | seis ou mais | 6 competencias | seis competencias | minimo de 6 | 6 novas`
- Crédito novo de PIS/COFINS só até dez/2026 e o saldo precisa estar escriturado (LC 214, art. 378) · `378 | 31/12/2026 | dez/2026 | dezembro de 2026 | 12/2026`
- Calendário pela decadência de 5 anos, competência mais antiga primeiro · `decadencia | 5 anos | cinco anos | prescri*`
- Clientes sem Master ficam fora da lista da Área Partners (D76) · `D76 | outra area`
- A lista vai à Daniela, dentro da capacidade do técnico (D11) · `daniela`

**Não pode conter:**
- Prometer novo ressarcimento ou valor · `re:(vai|vao) (receber|recuperar) | garantido | garantimos`
