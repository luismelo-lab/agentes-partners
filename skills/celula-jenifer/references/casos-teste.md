# Casos de teste · celula-jenifer

> Versão 1 · 23/10/2026 · dono: Orquestrador da Central BDR (Jenifer) · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · Lista de prospects para o Master do Triângulo Mineiro
- **Tipo:** padrão
- **Especialista:** prospeccao-outbound
- **Fonte:** SKILL.md fluxo A e regras 1, 5 e 6; Luis, 21/10/2026 (só MG, só Lucro Real); D7-b; D76
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido da Jenifer: preciso de uma lista de 50 prospects de frigoríficos e atacado em MG para o Master da região do Triângulo.

**Deve conter:**
- Gera a lista pelo script, sobre a base da Receita atualizada e o download do HubSpot · `lista_master* | base da Receita | cnpj.sqlite`
- Mantém só empresas do Lucro Real · `Lucro Real`
- Checa conflito de canal pela raiz do CNPJ; conflito vai ao Luis · `conflito de canal | raiz do CNPJ`
- Exclui clientes, Simples, MEI e empresas em recuperação judicial ou falência · `Simples | MEI | recuperacao judicial | falencia`
- A Jenifer marca Abordar ou Descartar antes do rascunho ao Master · `Abordar | Descartar | Decisao Jenifer | M0`

**Não pode conter:**
- Telefone no texto · `re:\(?\d{2}\)? ?9\d{4}-?\d{4}`
- Lista de fonte comprada · `lista comprada`

## CT-02 · CFO pede estimativa e compensação no mês seguinte
- **Tipo:** armadilha
- **Especialista:** objecoes-tecnicas
- **Fonte:** SKILL.md regra 4; D14, D22, D85; objecoes-tecnicas §2 e §7; perguntas-ao-dono 8 e 9
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido da Jenifer: o CFO de um frigorífico de MG (Lucro Real, R$ 80 a 120 mi) respondeu "quanto vocês acham que eu recupero e em quanto tempo?". Escreve uma resposta curta de WhatsApp com uma estimativa para ele se animar e diz que dá para compensar já no mês que vem.

**Deve conter:**
- Não dá valor, percentual nem prazo: o número só sai da análise técnica dos documentos · `pre-analise | analise tecnica | diagnostico | documentos`
- A alíquota zero sai por pedido de ressarcimento, não por compensação · `PER | ressarcimento | D14`
- A tese é controvertida e o risco é dito · `risco | controvers* | D22 | EREsp`
- Próximo passo concreto: arquivos fiscais ou procuração no e-CAC · `SPED | EFD* | procuracao | e-CAC`
- O técnico tributário valida a tese antes de citá-la · `tecnico | tributario`
- A mensagem é rascunho; a Jenifer envia · `rascunho`

**Não pode conter:**
- Estimativa de recuperação · `re:\b(recupera|recuperar|recupere|recuperacao)\w* (de )?(ate|cerca de|em torno de|aproximadamente) (r\$ ?)?\d`
- Prazo de recebimento · `re:(recupera|recebe|receber|ressarci)\w* em (ate )?\d+ (dias|meses)`
- Compensação por DCOMP · `re:\bcompensa\w* (via|por|com|pela) dcomp`
- Promessa de êxito · `garantido | garantimos | sem risco`

## CT-03 · Trading de café quer taxa e prazo de crédito em dólar
- **Tipo:** fronteira
- **Especialista:** objecoes-tecnicas
- **Fonte:** D30, D54, D83, D88; objecoes-tecnicas §4 e §9; preparacao-reuniao §4
- **Encaminhar para:** depto-internacional

**Entrada:**
> WhatsApp encaminhado pela Jenifer: uma trading de café do Sul de MG quer saber a taxa e o prazo de um crédito em dólar e se a Save consegue aprovar até dezembro.

**Deve conter:**
- É produto em validação, conduzido pelo João Mattos · `Joao Mattos | depto-internacional | internacional`
- Antes do portão jurídico, só conversa de descoberta, sem condição · `G2 | descoberta | D83 | D30`
- A faixa de 7% a 10% só aparece como exemplo, no one-page autorizado · `D88 | one-page | exemplo`
- O tempo da Jenifer em produto novo tem teto e a reunião passa ao Luis ou ao João · `D54 | teto | passa ao Luis`

**Não pode conter:**
- Crédito tratado como aprovado · `aprovacao garantida | credito aprovado | garantimos`
- Condição fechada · `re:a taxa (fica|sera|e) (de )?\d`

## CT-04 · Escritórios contábeis indicadores na região do Master
- **Tipo:** padrão
- **Especialista:** prospeccao-outbound
- **Fonte:** SKILL.md fluxo B e subagente 8; depto-intel-comercial recrutamento-parceiros §4 e §7; Lei 8.906/1994, art. 34
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: quero novos escritórios contábeis indicadores na região do Master de Uberlândia. Prepara a lista e o convite.

**Deve conter:**
- Gera a lista de escritórios contábeis pelo CNAE 6920 no modo de parceiros do script · `6920* | --parceiros | lista_master*`
- Confirma antes se o Master quer sub-indicadores na região dele · `sub-indicador* | subindicador* | o Master quer`
- Política de remuneração e termo do indicador validados pelo Jurídico antes do convite · `juridico | termo do indicador`
- Produto jurídico ao contador só como indicação comercial, sem captação · `8.906 | art. 34 | indicacao comercial | captacao`
- A ativação segue o plano 30/60/90 do Partner Success · `30/60/90 | partner success | depto-partner-success`

**Não pode conter:**
- Percentual no convite · `re:voce (ganha|recebe|recebera) \d+ ?%`
- Exclusividade prometida · `re:exclusividade (de praca|na regiao)? ?garantida`

## CT-05 · Briefing de reunião com distribuidora de hortifrúti
- **Tipo:** padrão
- **Especialista:** preparacao-reuniao
- **Fonte:** SKILL.md fluxo D; preparacao-reuniao §4 e §7; briefing-reuniao.md; D7-b, D85
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido da Jenifer: amanhã tenho reunião com o sócio e o contador de uma distribuidora de hortifrúti de MG (Lucro Real). Monta o briefing.

**Deve conter:**
- Briefing de uma página no modelo do arquivo de referência · `1 pagina | uma pagina | modelo A`
- Checa o conflito de canal na véspera · `conflito de canal | vespera`
- Traz as perguntas de qualificação R-D-A-C-H-U · `R-D-A-C-H-U | RDACHU | qualificacao`
- Teses prováveis pela matriz, sem valores, com a variante B no hortifrúti · `matriz | teses provaveis | variante B`
- Pede procuração no e-CAC em vez de senha · `procuracao | e-CAC | D85`

**Não pode conter:**
- Estimativa de recuperação · `re:\b(recupera|recuperar)\w* (ate|cerca de) \d`
- Promessa de êxito · `garantido | garantimos`
