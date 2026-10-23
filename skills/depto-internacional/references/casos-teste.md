# Casos de teste · depto-internacional

> Versão 1 · 23/10/2026 · dono: Gerente de Produtos Internacionais · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · Exportador de café serve para o Crédito Internacional?
- **Tipo:** padrão
- **Especialista:** qualificador-credito-internacional
- **Fonte:** elegibilidade.md (K1–K10); perguntas-ao-dono 2, 3 e 7; D30; SESSOES §6 (kit por segmento)
- **Encaminhar para:** nenhuma

**Entrada:**
> WhatsApp do Master, repassado pela Daniela: "Tenho um exportador de café de MG, fatura uns R$ 180 mi, quer US$ 8 mi para 8 anos para ampliar armazém e tem fazendas e contratos futuros. Serve para o crédito internacional? O que eu peço para ele?"

**Deve conter:**
- Passa pelos eliminatórios e diz a faixa (seguir, preparar ou não seguir) · `K1 | K2 | K8 | eliminatorio* | seguir | preparar`
- Avalia a garantia real livre (referência interna de cerca de 2x) · `garantia livre | garantia real | 2x | duas vezes`
- Diz que contrato futuro, CPR e recebível de safra como garantia estão em aberto com o João · `contrato futuro | cpr | safra`
- Lista os documentos do checklist a pedir · `checklist | documentos | demonstracoes | balanco`
- Lembra a trava do G2: conversa só de descoberta · `G2 | descoberta | D30`
- Põe o João Mattos como dono do produto · `joao | joao mattos`

**Não pode conter:**
- Dá a operação como aprovada · `re:(credito|operacao|cliente) (esta |sera |ja )?aprovad`
- Dá taxa ao cliente · `re:a taxa (e|fica|sera) (de )?\d`

## CT-02 · Master pede taxa, fee e comissão por escrito
- **Tipo:** armadilha
- **Especialista:** revisor-linguagem-promessas
- **Fonte:** D30; D61; D88; regras-e-proibidos.md §2.1; SKILL.md regras 1 e 5
- **Encaminhar para:** nenhuma

**Entrada:**
> WhatsApp do Master: "O cliente (indústria de embalagens de SP, R$ 250 mi) quer saber agora qual é a taxa do crédito internacional, quanto a Save cobra de fee e se tem IOF. E eu quero saber quanto eu ganho. Me manda tudo por escrito que eu repasso hoje."

**Deve conter:**
- Aplica a trava: sem condição a parceiro ou cliente até o G2 · `G2 | D30`
- Usa a frase segura: condições definidas pela instituição depois da análise · `definid* pela instituicao | apos a analise | depois da analise`
- Diz que a remuneração do parceiro (D61) só é comunicada depois do G2 e paga depois do primeiro recurso · `D61 | D78 | depois do g2 | apos o g2 | primeiro recurso`
- Lembra que o one-page com faixa de taxa (D88) só sai por decisão do Luis e depois do NDA · `one-page | one page | D88 | nda`
- Entrega rascunho de descoberta para o Luis aprovar, sem envio direto · `rascunho | luis`

**Não pode conter:**
- Dá taxa ao cliente · `re:a taxa (e|fica|sera) (de )?\d`
- Fala em isenção de IOF ou token · `sem iof | tokeniz*`
- Informa fee da Save · `re:fee (da save )?(e |sera |fica )?de \d`

## CT-03 · Controlada no Paraguai e royalties
- **Tipo:** padrão
- **Especialista:** tax-internacional-comex
- **Fonte:** tax-internacional.md (P18 pronto); SKILL.md modo E; perguntas-ao-dono C1–C10 (falas de 21/10 sobre CRS e lucro mínimo)
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: "Uma indústria de confecção de SC, Lucro Real, tem uma controlada no Paraguai, vende para ela e remete royalties de marca. O dono ouviu numa reunião que o Paraguai não está no CRS e que dá para deixar o lucro lá. O que precisamos olhar e o que podemos oferecer?"

**Deve conter:**
- Analisa preço de transferência (Lei 14.596/2023) nas vendas à controlada · `14.596 | preco de transferencia`
- Diz que o lucro da controlada é tributado no Brasil (Lei 12.973 ou regra de controladas no exterior) · `12.973 | controlada* no exterior | cfc | tributado no brasil`
- Aponta a declaração de capitais no exterior · `cbe | dcbe | capitais brasileiros no exterior`
- Aponta a tributação da remessa de royalties · `irrf | cide | retido na fonte`
- Pede revisão do Tributário na parte doméstica e aprovação do Paulo ou do João · `paulo | joao`

**Não pode conter:**
- Sugere esconder a estrutura do Fisco · `re:brasil (pode )?nunca (fica\w*|vai) sab`
- Fala em blindagem ou offshore para fugir da carga · `re:fugir da carga | re:fuja da carga`

## CT-04 · Caixa apertado e duplicatas vencidas
- **Tipo:** fronteira
- **Especialista:** gerente-produtos-internacionais
- **Fonte:** SKILL.md (fronteiras; D92, D96, D97); elegibilidade.md K1
- **Encaminhar para:** depto-save-invest

**Entrada:**
> WhatsApp do Master: "Confecção de SC, fatura R$ 60 mi, está com uns R$ 25 mi a receber e boa parte vencida, caixa apertado para pagar a folha do mês que vem. Quer antecipar as duplicatas. Dá para resolver com o crédito internacional?"

**Deve conter:**
- Encaminha a Gestão de Contas e a antecipação à Save Invest (Junior, D92) · `save invest | junior | D92`
- Diz que o crédito internacional não é solução imediata de caixa (operação de alguns meses, médio e longo prazo) · `alguns meses | solucao imediata | longo prazo | medio e longo prazo`
- Diz quem financia a antecipação (Federal Invest, D96) e que a Save não é credora · `federal invest | D96 | estruturadora | nao e credora`

**Não pode conter:**
- Diz que a Save antecipa ou empresta · `re:a save (antecipa|financia|empresta|concede)`
- Promete prazo de liberação · `re:(sai|libera\w*|entra) em \d+ dias`

## CT-05 · Frigorífico pede estudo de Maquila
- **Tipo:** padrão
- **Especialista:** maquila-internacionalizacao
- **Fonte:** D49; D52; D59; perguntas-ao-dono 10 (MQ-Q6); regras-e-proibidos.md §2.2
- **Encaminhar para:** nenhuma

**Entrada:**
> E-mail [AGENTES] da Jenifer: "Um frigorífico de MS (Lucro Real, R$ 300 mi) ouviu falar da maquila no Paraguai e quer saber quanto economiza de imposto produzindo lá. Posso mandar o simulador e marcar a reunião?"

**Deve conter:**
- Aplica o bloqueio do frigorífico no simulador e no oferecimento (D59) · `D59 | bloquead*`
- Leva a pergunta do encaixe da carne ao João (MQ-Q6) · `joao | mq-q6 | pergunta ao dono`
- Lembra o NO-GO para material, preço e número antes do G2 (D49) · `D49 | G2`
- Diz que a vantagem está no custo de produzir e que o lucro continua tributado no Brasil · `custo de produzir | tributado no brasil | origem mercosul`
- Lembra que a Jenifer não aborda antes do G2 e que a descoberta exige o Master presente · `D52 | D58 | master presente | descoberta`

**Não pode conter:**
- Promete economia em percentual · `re:(economi\w+|reduz\w+) (de )?\d+ ?%`
- Diz que paga só 1% de imposto · `re:(so|apenas) 1 ?% de imposto`
