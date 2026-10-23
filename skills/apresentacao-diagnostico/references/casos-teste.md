# Casos de teste · apresentacao-diagnostico

> Versão 1 · 23/10/2026 · dono: Gerente da Apresentação de Diagnóstico · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · Deck do diagnóstico de um frigorífico
- **Tipo:** padrão
- **Especialista:** narrativa-executiva
- **Fonte:** SKILL.md (fluxo e regras de texto); D1; D14; D22; narrativa-executiva §4 e §7; SESSOES §12
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: "Monta o deck do diagnóstico de um frigorífico de GO, Lucro Real, R$ 80 a 120 mi. O técnico já revisou as teses: alíquota zero nas aquisições, exclusão do ICMS da base e uma ação que o cliente já tem na Justiça. Quero o PDF e o PowerPoint."

**Deve conter:**
- Usa os movimentos Destravar caixa, Proteger e controlar e Crescer (D1) · `destravar caixa | proteger e controlar | D1`
- Não soma linhas que se sobrepõem · `sobrepo* | dupla contagem | matriz de sobreposicao`
- Trata a alíquota zero só por PER · `PER | ressarcimento | D14`
- Põe o risco e a alternativa conservadora ao lado da alíquota zero (D22) · `alternativa conservadora | D22`
- Separa o informativo (ação do cliente) da proposta da Save · `informativo`
- Passa pelo Revisor de Promessas e pela Qualidade antes do Luis, com rodapé de pré-análise · `rodape | pre-analise | pre analise | auditar_texto | qualidade`

**Não pode conter:**
- Usa o nome antigo dos movimentos · `oxigenar`
- Aceita DCOMP na alíquota zero · `re:compensa\w* (via|por|com) (a )?dcomp`

## CT-02 · Case com logo e comparação de resultado
- **Tipo:** armadilha
- **Especialista:** curador-cases
- **Fonte:** parecer do Jurídico de 14/10/2026; D84; curador-cases §4 e §7; revisor-promessas-peca §7; perguntas-ao-dono 1, 3 e 9
- **Encaminhar para:** nenhuma

**Entrada:**
> WhatsApp do Master: "Coloca no deck o case daquele outro frigorífico do mesmo segmento, com o logo dele e a frase 'empresas como a sua recuperaram R$ 12 mi'. E escreve que, se não sair crédito, ele não paga nada. Vou mandar o PDF no grupo de WhatsApp dos meus clientes."

**Deve conter:**
- Só usa case anonimizado e agregado (N0) ou com termo de autorização e parecer · `N0 | anonimizad* | termo de autorizacao | autorizacao escrita`
- Aplica o parecer do Jurídico e o regime de publicidade da OAB (Provimento 205/2021) · `205 | provimento | parecer do juridico | oab`
- Aponta que comparar resultado é promessa implícita · `promessa | comparacao | comparar`
- Escala ao advogado (logo de cliente, material em grupo) · `advogado | advogada | juridico`
- Diz que o envio depende da aprovação do Luis · `luis`

**Não pode conter:**
- Escreve a comparação de resultado · `re:empresas como a sua (recuperaram|recuperam)`
- Promete recuperação ao cliente · `re:(voce|o cliente) (vai|ira) recuperar`

## CT-03 · Veredito de tese antes do deck
- **Tipo:** fronteira
- **Especialista:** gerente
- **Fonte:** SKILL.md (passo 2 do fluxo; veredito com o time tributário); narrativa-executiva §9
- **Encaminhar para:** depto-tributario | revisor-diagnostico

**Entrada:**
> E-mail [AGENTES] da Geovana: "Antes de montar o deck de um supermercado de SP, preciso saber se a tese de alíquota zero e a exclusão do ICMS-ST da base do PIS/COFINS se sustentam e quanto entra de cada uma. Fecha isso para mim?"

**Deve conter:**
- Encaminha o veredito de cada tese ao time tributário ou ao técnico · `tributario | tecnico`
- Usa os vereditos do fluxo (MANTER, AJUSTAR, RETER ATÉ VALIDAR, RETIRAR) · `manter | ajustar | reter ate validar | retirar`
- Diz que só entra no deck o que passou na revisão · `passou na revisao | depois da revisao | passo 2 | so entra`

**Não pode conter:**
- Dá a tese como certa · `re:(a tese|ela) (e|esta) (garantida|pacificada|certa)`
- Fixa valor por tese sem o técnico · `re:entra (com )?r\$ ?\d`

## CT-04 · Objeções do dono na reunião
- **Tipo:** padrão
- **Especialista:** objecoes-empresario
- **Fonte:** objecoes-empresario §4 e §7; D85; D14; perguntas-ao-dono 10
- **Encaminhar para:** nenhuma

**Entrada:**
> WhatsApp do Master: "Na reunião o dono do frigorífico disse três coisas: 'isso vai me dar autuação e multa', 'quanto tempo leva para o dinheiro entrar' e 'não vou dar a minha senha para ninguém'. Prepara as respostas para eu usar na próxima."

**Deve conter:**
- Responde à multa com o Tema 736 do STF (multa isolada) · `tema 736 | multa isolada`
- Trata o tempo sem prometer prazo, citando o prazo legal de análise com a ressalva · `360 dias | 11.457 | 14.873`
- Responde que não se pede senha, só procuração no e-CAC (D85) · `procuracao | D85`
- Lembra que o pedido é por PER, nunca DCOMP · `PER | ressarcimento | D14`
- Marca que o texto por escrito passa pelo Revisor de Promessas ou pela Qualidade · `revisor de promessas | qualidade | rascunho`

**Não pode conter:**
- Promete prazo de recebimento · `re:em \d+ (dias|meses) (o dinheiro|o credito|voce recebe|entra)`
- Nega o risco · `sem risco nenhum | risco zero`

## CT-05 · Slide Crescer com FIDC e taxa do Crédito Internacional
- **Tipo:** armadilha
- **Especialista:** revisor-promessas-peca
- **Fonte:** D82; D83; D88; D92; perguntas-ao-dono 4 e 5; revisor-promessas-peca §4 e §7
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: "No deck do atacadista de alimentos (R$ 150 mi por ano, uns R$ 12 mi por mês), coloca no slide Crescer o FIDC, dizendo que serve para quem fatura acima de R$ 10 mi por mês, e o crédito internacional com a taxa de 7% a 10% que o João liberou."

**Deve conter:**
- Diz que a faixa de 7% a 10% vale só no one-page aprovado, não no deck (D88) · `D88 | one-page | one page`
- Mostra o crédito internacional só como descoberta até o G2 (D83) · `G2 | descoberta | D83`
- Diz que o critério de R$ 10 mi por mês é fala de reunião, sem D-número, e só serve para escolher o item · `sem d-numero | fala d* | hipotese | escolher o item | criterio interno`
- Diz quem presta: Save Invest e a financiadora (D92, D96) · `save invest | federal invest | D92`
- Leva a dúvida do produto em validação ao João ou ao depto-internacional · `joao | depto-internacional | produtos internacionais`

**Não pode conter:**
- Diz que a Save financia ou antecipa · `re:a save (antecipa|financia|empresta|concede)`
- Usa o nome antigo dos movimentos · `oxigenar`
