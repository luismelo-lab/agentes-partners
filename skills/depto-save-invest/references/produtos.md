# Save Invest · Ficha de cada produto

> **Status (Luis, 19/10/2026):** Gestão de Contas, antecipação de recebíveis e FIDC (com FIDIC, multicedente e multissacado) são **produtos prontos para venda**, ofertados pela **Save Invest**. Dono humano: **Junior** (responsável pela Save Invest). **D92 (22/10/2026):** a Save Invest (`depto-save-invest`) fica com os três produtos; o `depto-solucoes` fica só com a esteira e o mapa da conta. Estes produtos **não têm a trava do G2** (que vale só para Crédito Internacional, Maquila, captação de capital e home equity, no `depto-internacional`).
>
> **Fonte principal:** resumo automático da reunião de 13/10/2026 (*Gestão de Contas, Produtos Financeiros e Modelo Consultivo*, OneDrive `00 · Entrada/`). O que o Junior disse é **fala do dono**, não regra, até virar decisão (D-número). Números internos marcados `[13/10, Junior]` precisam de confirmação escrita antes de ir a material externo (`perguntas-ao-dono.md`).
>
> Última revisão: 22/10/2026.

## 0. Quem é quem (o que a fonte diz e o que falta)

| Nome | O que é, segundo a fonte | Status |
|---|---|---|
| **Save Invest** | Vertical financeira do grupo Save. Oferta Gestão de Contas, antecipação e FIDC. O Junior a conduz "há anos" na Gestão de Contas (13/10, T32) | Razão social, CNPJ e enquadramento regulatório: **em aberto** (P1 em `perguntas-ao-dono.md`) |
| **SEI** | Nome usado no resumo de 13/10 para quem **desenvolveu a cobrança por IA** ("ecossistema SEI/Save Invest") | SEI é a mesma empresa que a Save Invest? **Em aberto** (P2) |
| **Federal Invest** | Base da **antecipação** (13/10, T12). Rede de franquias de agências financeiras que nasceu no fomento mercantil (factoring), fundada em 1994; 165 agências e R$ 2,4 bi movimentados em 2018 (Portal do Franchising, publieditorial de 15/05/2019, consulta em 22/10/2026). O Junior falou em "cerca de 100 agências" (13/10, T11) | Relação jurídica entre Save Invest e Federal Invest (franqueada? agência? indicadora?): **em aberto** (P3) |
| **"Júlia"** | Canal de atendimento ao devedor final (13/10, T9) | Quem opera e com qual base LGPD: em aberto (P9) |
| **Área Partners (Save Co.)** | Origina pelos parceiros Masters, qualifica e prepara. **Não antecipa, não concede crédito, não distribui cotas** | Regra da casa |

## 1. Gestão de Contas (cobrança automatizada por IA)

### O que é
Esteira de cobrança da carteira de recebíveis do cliente (boletos), feita por IA no WhatsApp, integrada a gateway de pagamento. Começa **antes do vencimento** e pode ir até negativação ou protesto, se o cliente quiser (13/10, T5 e T9). É a **porta de entrada do ecossistema**: resolve a dor de caixa causada pela inadimplência e cria a confiança que depois abre e-CAC, DRE e balanço (13/10, T1 e T2).

### Para quem
- Empresa com inadimplência relevante: contas a receber acima do faturamento mensal, vencidos altos, despesa financeira alta (13/10, T4).
- Emite boletos com volume e recorrência (B2B principalmente; B2C com regras do CDC, ver `regras-e-proibidos.md`).
- Corte numérico de porte: **não informado pela fonte** (P10). Ver `elegibilidade.md`.

### Como funciona (13/10, T5, T6, T9, T16)
1. Coleta de documentação e abertura de conta.
2. Registro dos boletos no banco da operação. O cliente continua emitindo boletos no próprio sistema: a rotina dele não muda.
3. Integração do banco ao sistema do cliente, **sem custo** para o cliente: API do cliente (a equipe desenvolve a conexão pela documentação dele), CNAB 240/400 (remessa e retorno, ainda com rotina manual diária) ou FTP/SFTP. SAP e ERPs complexos exigem análise individual.
4. A IA lê diariamente os títulos a vencer e dispara os contatos: **2 dias antes do vencimento** e **no dia do vencimento**, pelo WhatsApp, com botão para gerar Pix, pagar na hora ou gerar 2ª via do boleto.
5. Depois do vencimento: régua corretiva. Negativação segue para a Serasa; protesto para o cartório. Pagamento gera baixa.
6. Exceções (ex.: devedor manda recibo dizendo que já pagou) vão para atendimento humano, que liga. Cada exceção vira ajuste de programação; o objetivo é automação plena (13/10, T7).

### O que o cliente paga
- **Sem mensalidade e sem implantação.** A remuneração vem da **multa e dos juros cobrados do inadimplente** (pagamento no êxito). O Junior estimou em média **cerca de 1,5% do valor total da carteira** `[13/10, Junior]`.
- Em aberto: a base do 1,5% (carteira total ou vencida), se há piso, e o que acontece quando o contrato do cliente com o devedor não prevê multa e juros (P5, P6).

### Números que o Junior citou (são de mercado, não da Save Invest: não há BI próprio, 13/10, T8)
| Indicador | B2B | Pessoa física |
|---|---|---|
| Não paga até o vencimento | ~20% | 35% a 40% |
| Recuperado em até 90 dias | metade do inadimplente | metade |
| Montante total recebido | ~90% | ~80% |
| Vai para o judicial | ~10% | ~20% |
Sul costuma performar melhor que o Nordeste. Principal causa da inadimplência até o vencimento: **esquecimento**. O Junior disse que a eficiência subiu **80%** em relação ao modelo anterior por SMS e e-mail (dado do dono, sem estudo publicado). **Nunca apresentar esses números como dado próprio nem como promessa.**

### Status operacional
A cobrança ficou pronta cerca de um mês antes de 13/10 e entrou em produção na semana anterior, com a carteira de uma agência da rede rodando e o 1º cliente externo em implantação (13/10, T12). Produto novo na tecnologia, maduro no método (o Junior opera Gestão de Contas há anos, 13/10, T32).

### Em aberto
Empresa que contrata e presta (P1, P2); base e piso do 1,5% (P5); régua completa depois do vencimento (dias, canais, quando negativa e quando protesta) (P7); opt-in do WhatsApp e enquadramento na política da Meta (P8); operador do canal "Júlia" e DPA (P9); B2C ou só B2B (P11); SLA de repasse do valor recebido (P12).

## 2. Antecipação de recebíveis e limite especial

### O que é
Adiantamento de caixa sobre a carteira de títulos registrada, **operado com base na Federal Invest** (13/10, T12). Vem junto com a Gestão de Contas: ao registrar os títulos no banco da operação, o cliente recebe um limite.

### Como funciona (13/10, T10, T11, T14)
- **Limite automático de 30% do valor registrado**, liberado com garantia da própria carteira e aval, sem garantia real. Cresce com a carteira registrada (os bancos costumam dar limite fixo em reais).
- **Até 100% da carteira só com garantia real.** Não priorizar cliente que quer 100% sem garantia.
- O limite serve para **antecipar títulos** ou para **limite especial ("trustee")**: funciona como um cheque especial, com custo pró-rata diário. Exemplo do Junior: quem precisa pagar hoje e recebe amanhã usa o limite especial por poucos dias em vez de antecipar um título inteiro.
- **Análise de crédito:** comitê de 4 pessoas de lugares diferentes; o voto do originador tem peso dobrado. Operação **em pool**: em Gestão de Contas, normalmente 3 ou 4 agências dividem o risco e acompanham.
- **Antifraude:** críticas sistêmicas para pagamento em dinheiro, pagamento pela conta do próprio cedente, pagamento em praça diferente do endereço do sacado e comportamento fora do padrão. Alertas repetidos reduzem o volume com o cliente. O próprio limite de 30% é mitigador.

### O que o cliente paga
Taxa da antecipação e custo do limite especial: **não informados** (P13). A referência de mercado é a série do Bacen: desconto de duplicatas PJ a **1,43% a.m. (18,60% a.a.) em ago/2026** (SGS 25438 e 20719), mais IOF (ver `radar-mercado.md`). Nunca citar taxa da operação antes da proposta formal de quem antecipa.

### Temas sensíveis (D82, 22/10/2026)
A **antecipação sobre venda gerencial** e a **conta escrow (conta garantia)** **continuam no portfólio**, mas são tema da Save Invest (Junior) e **só são tratados presencialmente**, por serem sensíveis. Os agentes **não os descrevem** em material, mensagem, FAQ ou rascunho, não explicam mecânica, preço ou efeito, e não respondem dúvidas sobre eles. Se o tema surgir: "Esse ponto é tratado diretamente pelo Junior, da Save Invest, em conversa presencial." O Jurídico já registrou ressalvas sobre os dois temas (`docs/portfolio-2027/agentes/juridico-revisao.md` §2.1 e §2.2); ver o conflito em `regras-e-proibidos.md` §5.

### Em aberto
Quem é juridicamente o antecipador (agência de fomento mercantil da rede, instituição autorizada ou fundo) (P3, P4); taxa e custo total (P13); se o limite especial é crédito rotativo e quem o concede (P14); papel da Save Invest no pool e se ela assume risco (P15); remuneração da Save Invest e do parceiro (P16).

## 3. FIDC (FIDIC, multicedente e multissacado)

### O que é
Fundo de investimento em direitos creditórios (Res. CVM 175/2022, Anexo Normativo II) que compra recebíveis da empresa ou da cadeia dela. Na fala do Junior: a empresa cria **o próprio mecanismo de bancarização**, captura a receita financeira que hoje fica com bancos e fundos, antecipa dentro do grupo e melhora a lucratividade (13/10, T20). "FIDIC" é a grafia usada na reunião para o mesmo produto.

### Para quem (13/10, T21 e T35)
- **Faturamento a partir de cerca de R$ 10 milhões por mês** (mensal, não anual). Empresa com R$ 25 milhões por ano "provavelmente não sustenta" o fundo.
- Empresa que antecipa recebíveis com bancos a taxa alta, ou que tem cadeia grande de fornecedores ou clientes.
- Quem já tem FIDC ainda pode ter oportunidade em **multicedente/multissacado**.

### Custo (13/10, T21) `[13/10, Junior]`
- **Cerca de R$ 80 mil por mês** para manter o fundo (gestor, administrador, estruturador, auditoria, consultoria, exigências CVM).
- Só o gestor pode cobrar **cerca de R$ 30 mil por mês**.
- Referência de mercado para comparar (não é preço da Save Invest): ver `radar-mercado.md` §1.

### Como a Save Invest ganha (13/10, T21 e T26)
FIDC gera **receita recorrente** por administração e gestão operacional; funding internacional gera receita pontual. A Save Invest se posiciona como **operadora e gestora de estruturas financeiras** para clientes de alto volume; no modelo do café, o "banco" é do cliente (a trade) e a Save Invest opera. **Atenção:** administrar e gerir fundo exige registro na CVM (Res. CVM 21/2021). Qual entidade do grupo (ou parceiro) ocupa cada papel está **em aberto** (P17).

### Benefício: o que se pode e o que não se pode dizer
- O Junior disse que o ganho financeiro é cerca de **3 vezes** o benefício tributário (13/10, T20). É fala do dono, sem estudo. Não usar em material.
- Exemplo público citado na reunião (varejista que lucra com operações financeiras): não usar como prova sem fonte publicada.

### Multicedente e multissacado (13/10, T35)
Exemplo do supermercado: cerca de 80% da receita é custo da mercadoria; os fornecedores poderiam antecipar recebíveis contra o varejista, que capturaria a receita financeira que hoje vai aos bancos. Também se aplica a café (trade financia o produtor; contrato de compra futura como recebível), produtores e cadeias de fornecedores. **A reunião deixou o detalhamento para depois.** Café e agro com funding internacional: `depto-internacional`.

### Em aberto
Quem estrutura, administra, gere e custodia (P17); se a Save Invest é consultora especializada (P18); fee de estruturação e de gestão (P19); piso de faturamento e PL mínimo (P20); casos já estruturados (P21); política de remuneração do parceiro no FIDC (D78 vale, ver `regras-e-proibidos.md`).

## 4. Como os três se encadeiam (esteira Destravar caixa → Proteger e controlar → Crescer)
- **Destravar caixa:** Gestão de Contas (cobrança) + antecipação/limite especial. Porta de entrada.
- **Proteger e controlar:** carteira registrada, antifraude, dados de DRE, balanço e SCR que a confiança destrava.
- **Crescer:** FIDC próprio ou multicedente quando há escala (≥ R$ 10 mi/mês); funding internacional e home equity ficam no `depto-internacional`.
- Ordem de abordagem (13/10, T3): começar pela base de **leads perdidos, do mais recente ao mais antigo**; planilha de sensibilização (ICP) → apresentação comercial → se não houver aderência, outro produto do ecossistema.

## 5. Remuneração do parceiro
**D78 (22/10/2026, Gilberto):** nos produtos 2027, a remuneração do parceiro começa em **10% do líquido Save**, crescendo pelo programa. Vale para os três produtos. Detalhes de base de cálculo e quando paga: P16 e P22.
