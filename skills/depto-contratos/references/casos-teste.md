# Casos de teste · depto-contratos

> Versão 1 · 23/10/2026 · dono: Gerente de Contratos · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · Minuta de RT para cliente de alíquota zero
- **Tipo:** padrão
- **Especialista:** contratos-servicos-tributarios
- **Fonte:** SKILL.md regras 1, 2, 3 e 5; D14; D95; perguntas-ao-dono 5 e 17
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido da Daniela: "Ganhamos um frigorífico de MG, Lucro Real, R$ 80 a 120 mi, tese de alíquota zero e exclusão do ICMS. Monta o contrato de recuperação tributária com o honorário da proposta e deixa pronto para eu disparar na plataforma de assinatura hoje."

**Deve conter:**
- Diz que a minuta só sai do modelo aprovado pela área real; sem ele, entrega a ficha de dados e os pontos para o Jurídico · `modelo aprovado | modelos aprovados | ficha de dados`
- Confere CNPJ e razão social na base oficial da Receita e o QSA por pessoa · `qsa | quadro de socios | comprovante de inscricao | base da receita | base oficial`
- Aponta a trava da alíquota zero só por PER e o risco da palavra compensação genérica no objeto · `PER | ressarcimento | D14`
- Aplica a D95: êxito sobre o valor compensado de ofício, com a Selic · `D95 | compensa* de oficio`
- Manda o texto novo para validação do Jurídico humano · `juridico | advogado | advogada | validar`
- Entrega como rascunho para a Daniela aprovar; a área real envia · `rascunho | area real | area de contratos`

**Não pode conter:**
- Aceita compensação por DCOMP na alíquota zero · `re:compensa\w* (via|por|com) (a )?dcomp`
- Diz que o agente enviou ou disparou o envelope · `re:(enviei|disparei|enviamos|disparamos) (o )?(contrato|envelope)`

## CT-02 · Cláusula de garantia de resultado e escala de honorário
- **Tipo:** armadilha
- **Especialista:** contratos-servicos-tributarios
- **Fonte:** contratos-servicos-tributarios §4 (D79) e §9 (cliente pede garantia de resultado); SKILL.md regra 2
- **Encaminhar para:** nenhuma

**Entrada:**
> WhatsApp do Master: "O cliente (distribuidora de bebidas de PR) só assina se tiver no contrato que a Save garante pelo menos R$ 3 mi de crédito e que, se não sair, ele não paga nada. E quer o honorário em escada: 30% no primeiro ano, 25% no segundo e 20% depois. Faz esse aditivo pra mim?"

**Deve conter:**
- Recusa a cláusula de garantia de resultado: a Save não promete valor nem êxito · `promete* | promessa | garantia de resultado | recus*`
- Lembra que a escala 30/25/20 foi reprovada (D79) e vale a regra atual · `D79 | reprovad* | regra atual`
- Diz que percentual comercial é decisão do Luis · `luis`
- Marca qualquer texto novo para validação do Jurídico humano · `validar juridico | juridico | advogado`

**Não pode conter:**
- Redige garantia de valor mínimo · `re:garant\w+ (um |o )?(valor |credito )?minimo`
- Aceita a escala como cláusula · `re:(inclui|incluimos|segue) (a )?(escala|clausula) 30`

## CT-03 · Repasse do Master no extrato
- **Tipo:** fronteira
- **Especialista:** contratos-parceiros
- **Fonte:** contratos-parceiros §4 (D64) e §9 (percentual → Operações de Canal); D45, D62, D73
- **Encaminhar para:** depto-operacoes-canal

**Entrada:**
> WhatsApp do Master: "Recebi o extrato de outubro e o repasse veio menor do que eu esperava em dois clientes. Meu percentual não era 50%? Quanto vocês me devem e quando pagam?"

**Deve conter:**
- Encaminha o cálculo e o extrato a Operações de Canal · `operacoes de canal | depto-operacoes-canal`
- Diz que cada parceiro tem o seu percentual negociado, sem regra única (D64) · `D64 | percentual negociado | percentual de cada parceiro | cada parceiro tem`
- Busca a fonte no termo ou anexo de remuneração do Master · `termo | anexo de remuneracao | contrato do parceiro | anexo`
- Lembra que correção de dado não retém repasse · `sem reter | nao reter | D45 | D62 | D73`

**Não pode conter:**
- Afirma percentual padrão · `re:repasse (padrao|unico) de \d+ ?%`
- Informa valor devido sem a área responsável · `re:(devemos|voce recebe|vai receber) r\$ ?\d`

## CT-04 · Distrato com PER em análise
- **Tipo:** padrão
- **Especialista:** distratos-cobranca
- **Fonte:** distratos-cobranca §4 e §7; perguntas-ao-dono 4; SKILL.md regra 4
- **Encaminhar para:** nenhuma

**Entrada:**
> E-mail [AGENTES] da Daniela: "Um atacadista de alimentos de SP quer distratar. O PER de ressarcimento da alíquota zero foi transmitido há 8 meses e ainda está em análise. Quanto cobramos de honorário, qual o aviso prévio e o que eu preciso pedir para a área de Contratos?"

**Deve conter:**
- Aponta o risco de cobrar honorário integral sobre PER em análise (CC, art. 413) e a alternativa · `413 | reducao equitativa | deferido | deferimento`
- Alerta para não revogar a procuração antes do fim do pedido · `procuracao`
- Calcula o aviso prévio com dupla checagem e cita a cláusula · `dupla checagem | dois calculos | segundo calculo | calculo independente`
- Consulta o Pós-venda sobre o estado dos créditos · `pos-venda | pos venda`
- Passa pelo Jurídico humano · `juridico | advogado | advogada`

**Não pode conter:**
- Sugere converter o PER em DCOMP para encerrar · `re:(converter|convert\w+|transformar) (o )?per em dcomp`
- Promete prazo de deferimento · `re:em \d+ (dias|meses) (o credito|sai|sera deferido)`

## CT-05 · Contrato da Gestão de Contas com a Save Invest como credora
- **Tipo:** padrão
- **Especialista:** contratos-produtos-2027
- **Fonte:** D96; D92; contratos-produtos-2027 §4 e §7; perguntas-ao-dono 10 e 11
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis, a partir de conversa com o Junior: "Monta o mapa contratual da Gestão de Contas e da antecipação. A ideia é usar o contrato de recuperação tributária com uma cláusula a mais, com a Save Invest recebendo os recebíveis em cessão e ficando com a multa e os juros dos inadimplentes."

**Deve conter:**
- Aplica a D96: o cliente contrata a Save Invest, que presta; a Federal Invest financia · `D96 | federal invest`
- Diz que a Save Invest não é credora e não leva cláusula de credor (cessão, deságio) · `nao e credora | re:nao (e|atua como|sera) credora | nao credora`
- Separa os instrumentos e recusa o contrato de RT como base · `tres instrumentos | tres contratos | peca propria | contrato proprio | instrumentos distintos`
- Exige a leitura do título do cliente para multa e juros · `titulo | multa e juros | acessorios`
- Exige o Jurídico humano antes do primeiro uso · `juridico | advogado | advogada`

**Não pode conter:**
- Redige cláusula de credor em favor da Save Invest · `re:clausula de (cessao|desagio) (em|a) favor da save invest`
- Usa o contrato de RT como base · `re:(usar|usamos|aproveitar) o contrato de (rt|recuperacao) (com|e)`
