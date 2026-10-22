# Produtos financeiros e internacionais · fichas completas, elegibilidade, esteira de capital e conflitos

> **USO INTERNO · rascunho para o Luis e o João Mattos · 22/10/2026.** Nada aqui é oferta, taxa, prazo, fee ou promessa. Produto em validação (Crédito Internacional, captação de capital, Maquila e derivados) entra só como **descoberta** até o G2 (alvo 15/12/2026). Números de taxa e prazo que aparecem abaixo são **referência interna ou fala de reunião, para conferir**, e não saem desta pasta.
> **Autor:** Gerente de Produtos Internacionais e Financeiros (`depto-internacional`), com os perfis do Qualificador, Estruturador, Café & Agro, Maquila, Ecossistema, Regulatório & Câmbio, Guardião G0–G4 e Revisor de Linguagem. Sem aprovação de Jurídico, Tributário ou João.
> **Fontes internas:** `docs/portfolio-2027/caracteristicas-produtos.md` (R1 = reunião de 24/09; R2 = de 21/10), `fichas-sem-reuniao.md`, `matriz-agentes.md`, `docs/ecossistema/*`, `skills/depto-internacional/references/*` (produtos, elegibilidade, regras, FAQ, radares de 16/10, perguntas ao dono) e `departamentos/produtos/PADRAO-PRODUTO-NOVO.md`.
> **Marcas:** `[WEB 22/10]` conferido em busca de hoje, sempre a confirmar no texto oficial · `[RADAR 16/10]` vem do radar da área · `[AGENTES]` base interna · `[HIPÓTESE]` proposta sem dono · `[VALIDAR JURÍDICO]` · `[VALIDAR TRIBUTÁRIO]` · `[NÃO CONFIRMEI]` pesquisei e não achei fonte.

---

## 0. Panorama (um quadro só)

| # | Produto | Estado (Luis, 19/10) | Dono humano | Portão | Entra ao cliente como |
|---|---|---|---|---|---|
| F1 | Gestão de Contas (cobrança IA, escrow, e-CAC) | Pronto | Save Invest (Júnior) | Fora do Padrão de Produto Novo | Produto, com travas jurídicas |
| F2 | Antecipação de recebíveis | Pronto | Save Invest | Fora do Padrão | Indicação a instituição autorizada |
| F3 | FIDC e multicedente/multissacado | Pronto | Save Invest | Fora do Padrão | Produto (estudo de viabilidade primeiro) |
| F4 | Crédito Internacional (CI) | Validação | João Mattos | G1 em andamento; G2 e G3 em 15/12 | **Descoberta** |
| F5 | Captação de capital (equity, sócio, fundos) | Validação | João Mattos | Sem G0 escrito | **Descoberta** |
| F6 | Kit de análise / dossiê | Candidato (parte de F4 e F5) | A definir | Sem G0 | Etapa do F4 e F5; avulso só com decisão |
| F7 | Preparação para investidor | Candidato N1 | A definir | Sem G0 | Produto próprio a decidir |
| F8 | Estudo de viabilidade Paraguai | Em estruturação (MQ) | João Mattos | G0 do MQ com alvo 16/10 | **Descoberta** (estudo pago só após 30/06/2027, D51) |
| F9 | Maquila e submaquila | Em estruturação | João Mattos | G0 16/10, G1 04/12, G2 15/12 | **Descoberta** |
| F10 | Zona Franca (Paraguai) | Sem ficha, sem dono | A definir | Sem G0 | Só como alternativa dentro do estudo |
| F11 | Governança no exterior (3 verticais) | Candidato N3 | João Mattos | Só após F9 | Não oferecer ainda |
| F12 | Internacionalização turnkey | Validação | João Mattos | Sem G0 | **Descoberta**, 2ª rodada |
| F13 | Tax internacional e comércio exterior | Pronto | Paulo e João Mattos | Fora do Padrão | Produto, com Tributário e Jurídico |
| F14 | Financiamento à exportação (ACC, ACE, seguro de crédito) | Candidato | A definir | Sem G0 | Cotação com parceiros, sem dono |
| F15 | Hedge | Candidato N5 | A definir | Sem G0 | Serviço correlato do F4 e F14 |
| F16 | CPR e CRA | Candidato | A definir | Sem G0 | Estruturação no agro com parceiro |

Home equity (P14) e certificado digital/ART ficam **fora desta rodada**, por decisão do Luis. Aparecem só como saída na matriz de elegibilidade.

**Regras que valem para todas as fichas:** a Save é estruturadora e facilitadora, nunca credora, nunca quem antecipa, nunca distribui cotas; cada produto é contratado em separado, sem venda casada; estudo antes de proposta; no máximo 2 produtos novos por vez por cliente; frases proibidas em `regras-e-proibidos.md` (não dizer "fundo internacional", "holding", "blindagem", "via token, sem IOF", faixa de taxa).

---

## 1. Fichas por produto

### F1. Gestão de Contas (cobrança por IA, conta escrow, leitura do e-CAC)
| Item | Conteúdo |
|---|---|
| **O que é** | Porta de entrada financeira: cobrança automatizada de carteira vencida por IA (WhatsApp, gateway de Pix e boleto), conta escrow para segregar recebíveis e leitura do fluxo consolidado do e-CAC como alerta preliminar. Abre o acesso a DRE, balanço e SCR [AGENTES, reunião 13/10] |
| **Para quem e gatilhos** | Empresa com venda a prazo B2B; contas a receber acima de 1 faturamento mensal; vencidos altos; despesa financeira alta; dívida de curto prazo de 3 a 4 faturamentos; mês em que o caixa aperta. Corte de faturamento: não informado |
| **Entregas** | Diagnóstico da carteira; régua (2 dias antes e no vencimento; negativação e protesto a critério do cliente); relatório de recuperação; canal de atendimento ao devedor; antifraude; conta escrow; painel mensal; integração com ERP (API, CNAB 240/400, SFTP; SAP em análise) |
| **Como funciona** | Diagnóstico da carteira → NDA e cessão de acesso → procuração eletrônica do e-CAC → régua por IA → repasse → painel mensal → ponte para antecipação, planejamento e demais produtos |
| **Dados do cliente** | Carteira a receber com aging, contratos, histórico de inadimplência, natureza do devedor (empresa ou consumidor), ERP, procuração do e-CAC |
| **Base legal e de mercado** | Cobrança entre empresas: multa contratual livre (CC arts. 412 e 413); juros de mora sem taxa no contrato = Selic menos IPCA (CC art. 406, Lei 14.905/2024). Devedor consumidor: CDC art. 42 (sem constrangimento) e multa até 2% (art. 52 §1º). LGPD: execução de contrato, exercício regular de direitos e legítimo interesse (art. 7º V, VI e IX). PL 2338/2023 (IA) ainda em tramitação na Câmara [RADAR 16/10]. Escrow reduz bloqueio automático, não bloqueio por ofício |
| **Travas e riscos** | Escrow não é blindagem e nunca vai à frente de credor; a receita "multa e juros dos inadimplentes" cai a quase nada se o devedor for consumidor ou se o contrato não prever multa; "cerca de 1,5% da carteira" e "2% do valor de face" são números do handoff, sem teste; estatísticas de mercado não são dado da Save; cobrança (SEI) e antecipação (Federal Invest) são entidades distintas |
| **Conexões** | Abre dados para recuperação tributária (P1) e gestão de passivo (P5); alimenta a antecipação (F2) e o FIDC (F3); o e-CAC e o SCR sinalizam o próximo produto; o escrow é peça do FIDC |
| **Responsáveis** | Dono: Save Invest (Júnior). Agentes: `depto-solucoes` e Analista do Ecossistema (`depto-internacional`); revisores: Jurídico (CDC, LGPD, OAB) e Qualidade |
| **Estado e portão** | Pronto para venda; cobrança em produção desde outubro, 1 carteira interna rodando, 1º cliente externo previsto. Sem kit nem portão |
| **A validar** | Quem contrata e quem presta; habilitação; remuneração do parceiro; contrato com multa e juros previstos; teste do 1,5% contra B2C; escopo do "gestão de contas" |

### F2. Antecipação de recebíveis
| Item | Conteúdo |
|---|---|
| **O que é** | Adiantamento de caixa sobre vendas a prazo, feito por instituição autorizada em pool. A Save organiza o diagnóstico e a cobrança; **não antecipa** [AGENTES] |
| **Para quem e gatilhos** | Contas a receber alto, prazo de recebimento longo, banco antecipando com deságio caro, sazonalidade, ICMS na importação (puxado pelo Paraguai). Sinal: ciclo de caixa acima de 90 dias; PMR acima de 60 dias |
| **Entregas** | Triagem e elegibilidade da carteira; encaminhamento à instituição parceira; acompanhamento; limite automático de cerca de 30% da carteira registrada, até 100% com garantia real; limite especial pró-rata; antecipação de venda gerencial só com formalização [reunião 13/10, a confirmar] |
| **Como funciona** | Carteira registrada → elegibilidade por sacado → limite → operação → repasse. Comitê da instituição decide |
| **Dados do cliente** | Notas e duplicatas, carteira por sacado, concentração, inadimplência, cessões e travas já existentes |
| **Base legal e de mercado** | Antecipar é operação de crédito, privativa de instituição autorizada (Lei 4.595/1964); exceções: FIDC, securitizadora, factoring com recursos próprios, ESC só para MEI/ME/EPP (LC 167/2019) [RADAR 16/10]. Duplicata escritural: Lei 13.775/2018 e Res. BCB 339/2023 (escrituração); Res. CMN 4.815/2020 trata da negociação pelas instituições financeiras [WEB 22/10, Lefosse]. CERC e B3 autorizadas em 25/06/2026; produção assistida desde 15/07/2026. **Obrigatoriedade por porte diverge entre fontes** (grandes entre abril e junho/2027; médios entre out/2027 e jan/2028; pequenos em abr–jun/2028) [WEB 22/10, não confirmei no BCB]. Desconto de duplicatas, média BCB: 18,60% a.a. em ago/2026, que não é o preço da média empresa [RADAR 16/10] |
| **Travas e riscos** | Antecipação sobre venda gerencial (sem nota) é prática sinalizada: só com formalização; a Save nunca se apresenta como quem antecipa; cessão já feita a outro credor derruba o limite |
| **Conexões** | Recebe o crédito recuperado como lastro; vem depois da Gestão de Contas; evolui para FIDC; alternativa a F3 abaixo de R$ 10 mi/mês |
| **Responsáveis** | Dono: Save Invest. `depto-internacional`; revisores: Jurídico e Qualidade |
| **Estado e portão** | Pronto; fora do Padrão |
| **A validar** | Taxa e habilitação (com o Júnior); em qual linha regulatória a instituição se enquadra; impacto da duplicata escritural na elegibilidade; remuneração do parceiro |

### F3. FIDC e multicedente/multissacado
| Item | Conteúdo |
|---|---|
| **O que é** | Fundo de investimento em direitos creditórios que compra os recebíveis da empresa (cedente único) ou de uma cadeia (multicedente: vários fornecedores; multissacado: vários clientes), capta de investidores e devolve ao grupo a receita financeira. A Save estrutura e conduz com a Save Invest; **não distribui cotas** |
| **Para quem e gatilhos** | Faturamento (ou recebíveis cedíveis) acima de cerca de R$ 10 mi por mês; antecipação cara no banco; cadeia grande (supermercado, café, agro); desejo de bancarizar a própria cadeia. Quem tem FIDC na Save não cota recuperação fora |
| **Entregas** | Estudo de viabilidade (data tape, perdas, concentração); desenho da estrutura (cedente único, multicedente, multissacado); política de crédito; escolha de administrador, gestor, custodiante, auditoria; operação e gestão recorrente |
| **Como funciona** | Diagnóstico da carteira → estudo de viabilidade → estruturação → registro dos direitos em registradora → captação com investidores → operação mensal |
| **Dados do cliente** | Carteira com histórico de 12 a 24 meses, NF-e, aceite e entrega, sacados, concentração, inadimplência, regime tributário, garantias |
| **Base legal e de mercado** | Res. CVM 175 e Anexo Normativo II; Res. CVM 240/2026 (crédito performado de empresa em RJ passa a ser padronizado); Ofício-Circular CVM/SSE 8/2025 (lastro, conta do fundo) [RADAR 16/10, WEB]. Mercado: patrimônio de R$ 902 bi em set/2026 [RADAR 16/10, ANBIMA via imprensa]. Custo: R$ 80 mil/mês é número interno (13/10); a fonte pública traz só implantação de R$ 100 mil a R$ 300 mil e originação de cerca de R$ 10 mi/mês para compensar. **Cota é valor mobiliário (CVM)** |
| **Travas e riscos** | Só título com nota; venda gerencial não entra; carteira concentrada ou curta não fecha a conta; "recebível futuro" e Forma 2 com CVM 160 pedem parecer; multicedente de cadeia exige aprofundamento em reunião futura |
| **Conexões** | Crédito recuperado vira lastro; planejamento viabiliza nota cheia (formalização); escrow e cobrança (F1); Paraguai puxa antecipação; seguro de crédito reduz risco; FIDC pode ser destino do CI no caso do café |
| **Responsáveis** | Dono: Save Invest. `depto-internacional`, Resultados (conta de receita), Jurídico (CVM) |
| **Estado e portão** | Pronto; sem portão. Antes (13/10) tratado como MVP; vale a atualização de 19/10 |
| **A validar** | Custo de R$ 80 mil/mês em 3 propostas reais; quem é o parceiro de administração e gestão; piso de volume; remuneração recorrente e do parceiro; reunião de multicedente |

### F4. Crédito Internacional (CI)
| Item | Conteúdo |
|---|---|
| **O que é** | Crédito de médio e longo prazo, em moeda forte, de instituições estrangeiras (uma estrutura americana e uma suíça), estruturado caso a caso pela Save com garantia real e projeto de uso. Consultivo e seletivo. Em reais, só banco nacional |
| **Para quem e gatilhos** | Faturamento comprovado a partir de cerca de R$ 50 mi/ano; necessidade a partir de US$ 5 mi (suíça) ou US$ 10 mi (americana); garantia livre de cerca de 2 vezes; 2 anos de demonstrações; setores: café, agro com terra, usinas, indústria exportadora, construção, frigoríficos. Gatilho forte: dívida a 20% a.a. ou mais em reais, receita em dólar |
| **Entregas** | Qualificação (K1–K10 e pontuação); kit e NDA; projeto de uso e capacidade de pagamento; garantias; apresentação à instituição; acompanhamento até a liberação e do uso |
| **Como funciona** | 10 etapas: originação → conversa de 30 min → NDA e kit → estruturação → apresentação → análise da instituição → contrato → liberação (forma e cronograma definidos pela instituição) → acompanhamento → pagamento. Mínimo realista de cerca de 3 meses |
| **Dados do cliente** | Balanço e DRE de 2024 e 2025; ECD e ECF; SCR; matrículas e ônus; anuência de garantidor; certidões; DU-E e câmbio; projeto; KYC com beneficiário final |
| **Base legal e de mercado** | Lei 14.286/2021 e Res. BCB 278/2022: credora no CDNR, código SCE-Crédito antes do ingresso, cronograma em 30 dias; informar a partir de US$ 1 mi; Res. BCB 575/2026 (conta em moeda estrangeira, vigência 01/10/2026). IOF câmbio zero acima de 364 dias de prazo médio e 3,5% até 364 (Decreto 12.499/2025, restabelecido por liminar do STF de 16/07/2025). IR na fonte de 15%, com gross-up usual; Suíça: 10% só para banco, prazo de 5 anos ou mais, equipamento ou projeto; EUA sem tratado. Credora LLC transparente pode ser regime fiscal privilegiado (SC Cosit 56/2026): limite de 30% do PL. PLD: Lei 9.613 art. 9º XIV provavelmente alcança a Save [RADAR 16/10; não conferi no texto oficial] |
| **Travas e riscos** | Nada de taxa, prazo, fee ou aprovação antes do G2; sem pagamento antecipado ao fundo; receita não formalizada, RJ e garantia alienada eliminam; hedge custa perto do diferencial de juros (não 1 p.p.); fraude de "advance fee" é o risco reputacional (K11); intermediação de crédito (Bacen) e CVM sem parecer; nenhuma liberação registrada nas fontes |
| **Conexões** | Exige passivo organizado e demonstrações (F6, F7); usa garantias de estruturação patrimonial; hedge (F15); café liga com F16 e F3; em Paraguai financia capex só se o dono confirmar (MQ-Q7 a Q12) |
| **Responsáveis** | Dono: João Mattos. `depto-internacional` (Qualificador, Estruturador, Café & Agro, Regulatório & Câmbio); Jurídico e Tributário; Luis é ponto focal (até 4 h/semana, D54 pendente) |
| **Estado e portão** | Em validação. G0 na prática, G1 em andamento, respostas escritas até 31/10, G2 e G3 em 15/12/2026. NO-GO para condições com parceiro ou cliente até o G2 (D30) |
| **A validar** | As 7 críticas do CI (seção 6); forma jurídica da credora; critério único de corte; taxa por moeda; Coaf; empresa que contrata |

### F5. Captação de capital (equity, sócio, fundos)
| Item | Conteúdo |
|---|---|
| **O que é** | Preparar a empresa e abrir portas para dinheiro de investidor ou fundo, nacional ou estrangeiro, em duas formas: **dívida** (sem ceder cotas, em dólar) ou **equity** (entra sócio ou fundo e recebe cotas, todo o valor vai para a empresa). Alternativa comparável ao banco: taxa × diluição [R1]. **Equity não é crédito e não é o CI** |
| **Para quem e gatilhos** | Demanda acima da capacidade com EBITDA negativo por investimento; meta de crescimento forte; sócio ou grupo do setor na mesa. Prejuízo não elimina se plano, payback e colateral convencerem (fala de R1, a validar) |
| **Entregas** | Kit de análise e NDA; plano de negócio e projeção; apresentação a fundos, bancos e investidores; comparativo dívida × equity; consolidação com a contabilidade; acompanhamento dos marcos de desembolso |
| **Como funciona** | Conversa de dor → kit → NDA → estudo preliminar → feedback de viabilidade → apresentação → consolidação → busca do recurso. Desembolso por marcos; data de entrada e saída do investidor |
| **Dados do cliente** | Contabilidade e administração auditadas; dossiê bancário; plano com destino do recurso; garantias e colaterais; datas de entrada e saída |
| **Base legal e de mercado** | Res. CVM 160: oferta é pública se a comunicação é dirigida a vários ou a indeterminados, e a dispensa não é geral; consulta pública CVM SDM 03/25 sugere limitar a oferta privada a quem tem relação prévia e habitual [WEB 22/10; texto oficial não aberto]. Cotas de Ltda e S.A. podem ser valor mobiliário; **intermediar investidor mediante remuneração pode exigir agente autorizado: NÃO CONFIRMEI, vai ao Jurídico**. Dividendos a não residente: IR na fonte de 10% desde 2026 (Lei 15.270/2025) [RADAR 16/10]. Preço de transferência se o investidor for parte relacionada |
| **Travas e riscos** | Valor mobiliário: Jurídico antes de qualquer conversa; Save não distribui cotas nem faz oferta pública; remuneração em aberto; taxas de 8% a 12% e carência de até 3 anos da R1 não constam do documento v2.3: não repetir ao cliente |
| **Conexões** | Precisa de F6 e F7; compete com F4 em ticket baixo; alimenta a planta no Paraguai (F9, segunda fase); precede M&A |
| **Responsáveis** | João Mattos; Paulo para investidor brasileiro. `depto-internacional`, `depto-solucoes`; Jurídico (CVM) obrigatório |
| **Estado e portão** | Em validação, sem linha própria formalizada; G0 ausente |
| **A validar** | Ticket mínimo de cada fundo e se existe fundo abaixo de US$ 10 mi; enquadramento CVM e intermediação; remuneração da Save e do parceiro; quem são os fundos (nomes ficam fora de material) |

### F6. Kit de análise e dossiê bancário
| Item | Conteúdo |
|---|---|
| **O que é** | Primeiro entregável do funding: pacote de informações, documentos contábeis e fiscais, plano de negócio, uso do recurso e garantias, com NDA bilateral. Resulta em parecer preliminar de viabilidade antes de procurar financiador [R1] |
| **Para quem e gatilhos** | Todo cliente que passou da conversa de dor para F4 ou F5, depois de qualificado nos eliminatórios |
| **Entregas** | Checklist documental fechado; NDA com cláusula de finalidade e de transferência internacional; dossiê organizado; parecer preliminar |
| **Como funciona** | Qualificação → NDA → documentos → conferência (Geovana) → parecer preliminar → decisão de seguir ou "não é agora" |
| **Dados do cliente** | Os 12 itens da camada 3: balanço e DRE de 2 anos, ECD e ECF, impostos, kit bancário, dívidas e SCR, matrículas, anuência, certidões, exportação, projeto, KYC |
| **Base legal e de mercado** | LGPD arts. 6º, 7º e 33 (dado de sócio ao exterior é transferência internacional); Lei 9.613 (KYC); NDA revisado pelo jurídico do cliente |
| **Travas e riscos** | Receita não formalizada vai ao dono e ao Jurídico antes; o projeto usa só números da contabilidade; dado coletado para crédito não serve para vender outro serviço sem pedido; idioma e auditoria independente em aberto (K07) |
| **Conexões** | Requisito de F4 e F5; é a versão curta de F7 |
| **Responsáveis** | `depto-internacional` (Estruturador), `depto-tributario` (curadoria Geovana), `depto-juridico` (NDA) |
| **Estado e portão** | Parte do F4 (K07, portão G3). Cobrança avulsa: sem decisão |
| **A validar** | Lista fechada (K07); se o kit é cobrado separado (risco de venda casada); idioma e tradução |

### F7. Preparação para investidor (plano, projeção, dossiê)
| Item | Conteúdo |
|---|---|
| **O que é** | Pacote que torna a empresa candidata a funding e capital: plano de negócio com destino do recurso, modelo financeiro em 3 cenários, dossiê contábil, fiscal e jurídico, garantias e materiais ao financiador. É o padrão de debt advisory (memorando de informação, modelo, data room) |
| **Para quem e gatilhos** | Empresa que quer F4 ou F5 e não tem plano, contabilidade confiável ou projeção; demanda acima da capacidade; sócio ou fundo na mesa |
| **Entregas** | Plano; modelo de 3 cenários com estresse; dossiê; data room; comparativo de alternativas (PPE, ACC, crédito rural, CPR, FIDC, banco); apresentação ao credor |
| **Como funciona** | Diagnóstico da estrutura de capital → modelo → memorando e teaser → sondagem → comparativo de propostas → documentação e data room |
| **Dados do cliente** | Os do F6 mais projeções, orçamento do capex, covenants esperados (DSCR, dívida líquida/EBITDA, LTV) |
| **Base legal e de mercado** | Prática de mercado; faixas de honorário de debt advisory **não localizadas**; benchmark de M&A 1% a 3% de êxito [RADAR 16/10, pista fraca]. Sem norma específica; se houver captação, aplica-se F5 |
| **Travas e riscos** | Honorário fixo, sem vínculo com funding (evitar venda casada) `[HIPÓTESE]`; dependência de CFO e controladoria (N2); capacidade de entrega da equipe |
| **Conexões** | Pré-requisito de F4, F5 e M&A; usa CFO terceirizado e `depto-resultados` |
| **Responsáveis** | `depto-solucoes`, `depto-internacional`, `depto-resultados`, Qualidade |
| **Estado e portão** | Candidato N1; Conselho decide próprio × parceiro; sem G0 |
| **A validar** | Escopo mínimo, preço, modelo do plano, quem executa |

### F8. Estudo de viabilidade da operação no Paraguai
| Item | Conteúdo |
|---|---|
| **O que é** | Primeiro serviço da frente de internacionalização, independente da captação e sem venda casada. Responde "vale a pena produzir parte da linha no Paraguai?", **inclusive quando a resposta é não** [R2] |
| **Para quem e gatilhos** | Média e grande indústria no Lucro Real, intensiva em mão de obra ou energia, produto de valor médio ou alto por quilo, clientes no Sul, SP ou Centro-Oeste. Gatilhos: falta de gente, expansão em 24 meses, perda de incentivo de ICMS até 2032, concorrência de importado |
| **Entregas** | (1) simulação do lucro adicional se parte da produção (por exemplo 30%) for feita no Paraguai e comprada pela empresa brasileira; (2) custo da expansão no Paraguai × Brasil; (3) escolha de local por energia, mão de obra e escoamento, com plano de continuidade; cenário pessimista primeiro; cenário "Paraguai ou maquila listados" |
| **Como funciona** | Descoberta (até 10 conversas no Q4, sem peça, preço ou número, Master presente) → diagnóstico → estudo → decisão. Origem Mercosul por NCM antes do estudo |
| **Dados do cliente** | Balancete, custos, notas, DRE, demanda do ano-base, plano de expansão com custos, NCMs e insumos, UF dos clientes, benefícios fiscais, CND |
| **Base legal e de mercado** | Lucro da controlada tributado no Brasil todo ano (Lei 12.973/2014 art. 77); crédito do imposto pago fora limitado (art. 87); preços de transferência (Lei 14.596/2023); origem Mercosul (Decisão CMC 06/23; até 60% de não originários, só REOs com asterisco, até 2038); sem tratado de bitributação em vigor [RADAR 16/10]. Salário mínimo PY: Gs 3.044.000 (US$ 500) desde 01/07/2026; energia industrial deve subir (ANDE, Itaipu 2027). Em exportações da maquila, frigoríficos são 705 empregos (sinal fraco) |
| **Travas e riscos** | Simulador só de faixa (D59), frigorífico bloqueado, nenhum R$ por CNPJ; resultado inverte com salário 30% maior ou logística 50% maior; simulações do Mapa de Entregas não vão a parceiro ou cliente |
| **Conexões** | Porta de F9, F10, F11, F12; financiamento da planta por F4 ou F5 (hipótese); importação puxa F2 |
| **Responsáveis** | Dono: João Mattos. Frente de internacionalização (Paulo) e escritório no Paraguai **sem confirmação escrita (MQ-Q1)**; assessor paraguaio a designar (MQ-Q16); Tributário e Jurídico |
| **Estado e portão** | Em estruturação. G0 alvo 16/10 (exige K00, K01 e 3 linhas do dono sobre o escritório); **estudo pago só após 30/06/2027 (D51)**, o que contradiz a fala de R2 de ser "o primeiro serviço" |
| **A validar** | Preço R2 (MQ-Q3); quem executa; critérios mínimos (MQ-Q2); se o estudo será pago antes de 06/2027 |

### F9. Maquila e submaquila
| Item | Conteúdo |
|---|---|
| **O que é** | **Maquila:** programa do Paraguai (Lei 7.547/2025, Decreto 5.714/2026) em que a empresa instalada lá industrializa sob contrato com matriz no exterior e exporta, com tributo único de 1% e demais tributos nacionais do programa isentos. **Submaquila:** terceirizar a produção a fábrica local do ramo, em modelo de marca própria: compra o insumo, a fábrica beneficia, armazena e remete ao Brasil. Só cabe se existir fábrica local [R2] |
| **Para quem e gatilhos** | Ver F8. Núcleo setorial: têxtil, confecção, couro e calçados, plásticos e borracha, embalagens, cabos, alumínio, móveis. Anti-perfil: Simples, comércio sem planta, açúcar e automotivo de produto final, busca só pagar menos IR, grupo com receita de € 750 mi ou mais |
| **Entregas** | Estrutura societária; programa no SIMEX (carta de intenção, resolução biministerial MIC e MEF); contrato de maquila; implantação; operação; recorrência (compliance e contabilidade no Paraguai) |
| **Como funciona** | 7 etapas ao cliente: diagnóstico, decisão, estruturação societária, implantação e capex, operação, exportação e venda ao Brasil, expansão. Prazos legais: contrato em até 180 dias da carta; início em até 18 meses da aprovação; tramitação de cerca de 90 dias (dado do marco antigo, não repetir). Ciclo de produto de cura longa: cerca de 24 meses até faturar |
| **Dados do cliente** | Os de F8 mais contrato social, organograma e capex |
| **Base legal e de mercado** | Tributo único: o **maior** entre valor agregado e fatura de exportação (art. 37), não só valor agregado [MIC e Res. SE-CNIME 14/2026, `maquila-fontes-oficiais.md`]; até 20 anos; venda local até 10% do volume exportado no ano anterior, com tributos internos (Decreto 5.714, lido em 21/10); transição dos programas da Lei 1.064 por 12 meses, depois migram à lei nova [RADAR 16/10]; exportações jan–jul/2026: US$ 860 mi, 61% para o Brasil [MIC]; mais de 160 empresas de capital brasileiro [Prensa Mercosur 13/08/2026, citado nas regras]. Texto integral da Lei 7.547 e do Anexo da Res. 14/2026 **ainda não lido** |
| **Travas e riscos** | Não é planejamento de IR; estrutura sem substância pode ser requalificada (CTN art. 116 par. único); Paraguai fora da IN RFB 1.037, mas regime privilegiado a conferir (1% e IRE de 10% abaixo de 17%); antidumping estendido; Pilar 2; sem estabilidade da regra |
| **Conexões** | Segue F8; capex financiado por F4 ou F5; importação de máquinas puxa F2 e o incentivo à importação de bens de capital (Lei 7.548); recorrência vira F11; produtos de recuperação tributária e planejamento entram por cross-sell |
| **Responsáveis** | João Mattos; Maquila & Internacionalização; Tributário, Jurídico, Regulatório; Luis dono comercial na Partners |
| **Estado e portão** | Em estruturação; G1 em 04/12, G2 em 15/12, G3 em 15/01/2027; geladeira de 90 dias sem passar portão; sem cliente ativo |
| **A validar** | MQ-Q1 a Q6 (críticas); base do 1% (valor agregado × fatura) com especialista paraguaio; prazos de tramitação da lei nova; submaquila: fornecedor local real e responsabilidade pela qualidade |

### F10. Zona Franca (Paraguai)
| Item | Conteúdo |
|---|---|
| **O que é** | Regime da Lei 523/1995 (Ciudad del Este e outras): importação sem imposto e imposto único de 0,5% sobre a receita bruta para quem se dedica **exclusivamente** a exportar para terceiros países (art. 14); vendas ao território aduaneiro pagam renda geral proporcional, com teto de 10% (arts. 15 e 16) [BACN e MEF, `maquila-fontes-oficiais.md`] |
| **Para quem e gatilhos** | Operação de logística, armazenagem, reexportação e montagem leve; quem não precisa vender ao território paraguaio. Alternativa à maquila dentro do estudo |
| **Entregas** | Comparativo maquila × zona franca × regime geral no estudo; estrutura local; logística |
| **Como funciona** | Sem processo próprio na Save; entra como cenário do F8 |
| **Dados do cliente** | Os do F8 mais fluxo de importação e reexportação |
| **Base legal e de mercado** | Regime geral para comparação: IVA de 10%, IRE de 10%, dividendos: 8% residente e 15% não residente (Lei 6.380/2019) [WEB 22/10, fontes de 2019 a 2020; atualização não confirmada]. Reunião R2 diz tributação territorial e Paraguai fora do CRS: **NÃO CONFIRMEI**; DCBE continua obrigação do contribuinte brasileiro com ativos no exterior de US$ 1 mi ou mais (trimestral a partir de US$ 100 mi; multa de 1% limitada a R$ 25 mil no atraso simples) [WEB 22/10, fontes de 02 a 03/2026; ciclo do ano-base 2026 no início de 2027] |
| **Travas e riscos** | A casa não tem ficha, dono ou preço; "cerca de 0,5% para exportação" só vale para exclusividade; CFC no Brasil vale também aqui |
| **Conexões** | F8, F9, F12, F13 |
| **Responsáveis** | Maquila & Internacionalização, Tributário |
| **Estado e portão** | Sem dono; sem G0. Não é produto, é cenário do estudo |
| **A validar** | Se a Save quer oferecer a zona franca como serviço de implantação; assessor paraguaio |

### F11. Governança e suporte à operação no exterior (3 verticais)
| Item | Conteúdo |
|---|---|
| **O que é** | Depois de instalada a operação, a Save atua como prestadora e depois como auditora em **três verticais: jurídico, administrativo e contábil**. Modelo de multinacional: diretoria local de executores e transparência total ao dono brasileiro [R2]. Inclui o programa de capacitação de funcionários paraguaios (cerca de 6 meses de imersão no Brasil, por convênio) como módulo opcional |
| **Para quem e gatilhos** | Cliente que já tem programa de maquila aprovado ou controlada no Paraguai |
| **Entregas** | Compliance e declaração mensal do tributo único (obrigatória mesmo sem exportar); contabilidade local; relatórios ao dono; auditoria; DCBE; preço de transferência |
| **Como funciona** | Contrato recorrente após a operação; prestação e depois auditoria (risco de independência: prestar e auditar o mesmo serviço) |
| **Dados do cliente** | Contabilidade local, folha, contratos, declarações |
| **Base legal e de mercado** | Declaração mensal do Tributo Único (art. 37; Decreto 5.714); Lei 14.596/2023; CFC (Lei 12.973); OAB: serviço jurídico só por escritório habilitado e sem divisão de honorários com não advogado (Lei 8.906/1994 art. 34) |
| **Travas e riscos** | Só após F9; conflito de independência entre prestador e auditor; serviço jurídico local depende de advogado habilitado no Paraguai; capacidade local sem confirmação |
| **Conexões** | Recorrência do F9; conversa com o Tributário (preço de transferência) |
| **Responsáveis** | João Mattos; escritório no Paraguai (não confirmado); Jurídico |
| **Estado e portão** | Candidato N3; sem G0; não oferecer |
| **A validar** | Quem presta (Save, associado local ou parceiro); responsabilidade; modelo de preço recorrente |

### F12. Internacionalização turnkey
| Item | Conteúdo |
|---|---|
| **O que é** | Da obtenção de recursos no exterior à abertura de mercado para o produto do cliente, com acompanhamento de obrigações no Brasil e fora. Tese: o mesmo esforço comercial que vende no Brasil serve à América Latina; escala, menos dependência do mercado interno, receita em dólar [R1 e R2] |
| **Para quem e gatilhos** | Indústria com capacidade e caixa organizados que quer vender fora. **Ordem recomendada: primeiro capacidade e caixa no Brasil, depois mercado externo.** Não lidera a primeira conversa |
| **Entregas** | Captação (F4 ou F5); estruturação; abertura de mercado por representantes comerciais; obrigações no Brasil; exportação |
| **Como funciona** | Segunda rodada, depois de F8 a F9 ou de F4 a F5 |
| **Dados do cliente** | Produto, NCM, mercados-alvo, capacidade, custo |
| **Base legal e de mercado** | Exportação: ACC e ACE (F14); câmbio (Lei 14.286); reforma tributária torna a exportação mais vantajosa (afirmação de reunião; CBS e IBS em transição, a validar com Tributário) |
| **Travas e riscos** | Cobertura citada: escritório próprio no Paraguai; apoio em Argentina, Uruguai, Chile, Peru, Bolívia, México, EUA, Portugal, Espanha e França (11 países; não dizer "dezenas de países"); **rede de representantes sem confirmação**; risco de prometer mercado |
| **Conexões** | Depende de F4, F5, F9; liga com F13, F14 e F15 |
| **Responsáveis** | João Mattos e frente de internacionalização; `depto-internacional`; Marketing só depois do G2 |
| **Estado e portão** | Validação; sem G0 |
| **A validar** | O que existe de fato da rede; modelo de remuneração dos representantes; escopo e preço |

### F13. Tax internacional e comércio exterior
| Item | Conteúdo |
|---|---|
| **O que é** | Assessoria em tributação de operações entre países, preço de transferência, não bitributação, estrutura jurídica local e comércio exterior. Perfil do especialista: advogado com mestrado em comércio internacional, ligado à comunidade empresarial do Paraguai [R2]. Canal de networking com grandes empresários |
| **Para quem e gatilhos** | Empresa com controlada, filial ou parte relacionada no exterior; importador ou exportador; cliente do F4, F9 ou F12 |
| **Entregas** | Estudo de preço de transferência; DCBE; análise de CFC e crédito do imposto pago fora; enquadramento de regime privilegiado; estrutura societária; parecer de não bitributação |
| **Como funciona** | Diagnóstico da estrutura → parecer → implantação → recorrência anual |
| **Dados do cliente** | Contratos intragrupo, balanços, cadeia societária, fluxo de remessas |
| **Base legal e de mercado** | Lei 14.596/2023 (obrigatória desde 01/01/2024); Lei 12.973 arts. 77 e 87; IN RFB 1.037/2010; Lei 12.249/2010 (subcapitalização); Brasil–Paraguai sem convenção em vigor (assinada em 2000, sem decreto de promulgação) [RADAR 16/10]; DCBE [WEB 22/10] |
| **Travas e riscos** | **Sem sigilo de capitais**: a Save não vende opacidade; planejamento agressivo vai a técnico humano; o parceiro cita "networking com o presidente do país", que não entra em material |
| **Conexões** | Condição de F8, F9, F11; suporte do F4 (IOF, IR na fonte, Cosit 56) |
| **Responsáveis** | Paulo e João Mattos; Tributário e Jurídico |
| **Estado e portão** | Pronto (Luis, 19/10); fora do Padrão |
| **A validar** | Cardápio e preço; quem emite o parecer (OAB); linha do parceiro sobre sigilo e CRS |

### F14. Financiamento à exportação (ACC, ACE, seguro de crédito)
| Item | Conteúdo |
|---|---|
| **O que é** | Linhas e instrumentos do exportador: ACC antes do embarque, ACE depois, pré-pagamento de exportação (PPE) e seguro de crédito à exportação. Operados por bancos e seguradoras; a Save diagnostica e encaminha |
| **Para quem e gatilhos** | Exportador de café, proteína, açúcar, indústria; receita em moeda forte; quer alongar ou baratear o giro. **Pergunta de entrada: já tem PPE, ACC ou crédito rural?** Exportador com PPE barato não é alvo do F4 |
| **Entregas** | Diagnóstico da exposição; cotação de linhas com bancos parceiros; hedge (F15); documentação; seguro de crédito |
| **Como funciona** | Diagnóstico → cotação → contratação pelo banco → acompanhamento |
| **Dados do cliente** | Contratos de venda externa, DU-E, volume e destino, linhas existentes, SCR |
| **Base legal e de mercado** | ACC até 360 dias antes do embarque e ACE até 750 dias, segundo guia de 2026; Res. CMN 3.844/2010, Circ. BCB 3.691/2013, Lei 11.371/2006 [fichas-sem-reuniao; a conferir]. Seguro de Crédito à Exportação: Fundo de Garantia à Exportação administrado pela ABGF; pós-embarque retomado em 2024; COFIG de 22/05/2026 aprovou novo produto para MPMEs e nova resolução do Proex [WEB 22/10, gov.br; limites de enquadramento divergem entre fontes (R$ 300 mi de faturamento, R$ 600 mi, US$ 5 mi de exportação)]. Custo de ACC e PPE em 2026: **NÃO CONFIRMEI** |
| **Travas e riscos** | A Save não é banco nem corretora de seguro; PIS/COFINS e tributação de venda externa vão ao Tributário; ACC em recuperação judicial é debate |
| **Conexões** | Concorre com F4 no exportador de café; hedge natural; Paraguai (reexportação) |
| **Responsáveis** | Regulatório & Câmbio, Tributário; banco ou corretora parceira (a definir) |
| **Estado e portão** | Candidato, sem dono, parceiro ou G0 |
| **A validar** | Parceiros; remuneração; Proex vigente |

### F15. Hedge (proteção cambial e de commodities)
| Item | Conteúdo |
|---|---|
| **O que é** | Diagnóstico de exposição e política de proteção contra câmbio e preço de commodity, com cotação em instituição autorizada. Serviço correlato do F4, F9 e F14 |
| **Para quem e gatilhos** | Dívida em moeda forte; custo em dólar com receita em reais; exportação; carteira indexada |
| **Entregas** | Mapa de exposição; política; cotação (swap, NDF, dólar futuro); revisão periódica |
| **Como funciona** | Diagnóstico → política aprovada pelo cliente → contratação pelo banco ou corretora |
| **Dados do cliente** | Fluxo de caixa por moeda, contratos, dívidas |
| **Base legal e de mercado** | Paridade de juros: travar o dólar por anos custa perto do diferencial DI × SOFR, cerca de 9,7% a.a. em dólar e 14% em franco suíço, no cálculo interno de 16/10 [RADAR 16/10]; NDF de balcão tem spread maior que o dólar futuro listado (0,20% a 0,50% contra 0,01% a 0,02% do nocional, Exame, ago/2026) [WEB 22/10]. Normas de derivativos e contabilidade de hedge: **NÃO CONFIRMEI** |
| **Travas e riscos** | Nunca opinar sobre o rumo do câmbio; "hedge de 1 p.p. ao ano" é erro provável da base; custo do hedge muda a economia do CI; chamada de margem |
| **Conexões** | Parte da conta do F4 e do F14 |
| **Responsáveis** | Regulatório & Câmbio; corretora ou banco parceiro |
| **Estado e portão** | Candidato N5; sem dono nem G0 |
| **A validar** | Parceiro; escopo; remuneração; resposta do João sobre o "1 p.p." |

### F16. CPR e CRA para o agro
| Item | Conteúdo |
|---|---|
| **O que é** | CPR (física ou financeira) como instrumento de crédito do produtor com garantia na produção ou em bem real; CRA como securitização de recebíveis do agro. A Save desenha e liga com parceiro emissor e securitizador |
| **Para quem e gatilhos** | Produtor e agroindústria que financiam safra; trading de café que financia produtor ("banco do produtor"); contrato futuro como recebível |
| **Entregas** | Desenho da CPR (financeira, com limite de crédito); garantias; registro; ponte com FIDC, fundos e F4 |
| **Como funciona** | Diagnóstico da safra e do caixa → desenho → registro → emissão e distribuição por terceiros |
| **Dados do cliente** | CAR, áreas, contratos de venda, estoque, SCR, projeção de caixa com preço estressado (menos 20% a 30%) |
| **Base legal e de mercado** | Lei 8.929/1994 com Lei 14.421/2022 (registro em entidade autorizada pelo BCB, CPR financeira com limite de crédito); CRA: Lei 14.430/2022 e Res. CMN 5.118/2024, ajustada pela 5.121/2024 e 5.212/2025 (endureceu o vínculo do lastro com o agro e deslocou operações para a CPR-F); CRA em CPR-F registrado na CVM em 01/06/2026 [WEB 22/10; nada de 2026 do CMN localizado]. Mercado travado: emissões de CRA caíram 77% no 1S2026; calote de CRA de cooperativa em jul/2026 [RADAR 16/10]. Funcafé 26/27 a 11,5% a.a. em custeio e Pronamp a 9% [RADAR 16/10] |
| **Travas e riscos** | Quem emite e distribui é terceiro autorizado; garantia em contrato futuro de café é volátil; mercado local em estresse; CPR sob RJ do produtor |
| **Conexões** | Café e agro; liga com F3 e F4; estruturação patrimonial fornece garantia |
| **Responsáveis** | Café & Agro (`depto-internacional`), Jurídico, Tributário (Agro) |
| **Estado e portão** | Candidato, sem dono nem parceiro |
| **A validar** | Parceiro securitizador; remuneração; se a Save assessora a emissão (CVM) |

---

## 2. Matriz de elegibilidade e porte

### 2.1 Por porte (faturamento anual) e produto
Linhas de porte usadas: **em crescimento** = até cerca de R$ 50 mi/ano (ou receita pequena com plano de expansão); **média** = R$ 50 a 120 mi/ano; **grande** = acima de R$ 120 mi/ano (R$ 10 mi/mês) ou ativos acima de R$ 60 mi. **Conflito:** o handoff chama de "média" tudo até R$ 10 mi/mês, o que inclui quem já passa no corte do CI. Esta matriz adota o corte por produto, e a seção 5 pede decisão.

| Produto | Em crescimento (< R$ 50 mi/ano) | Média (R$ 50 a 120 mi/ano) | Grande (> R$ 120 mi/ano ou ativos > R$ 60 mi) |
|---|---|---|---|
| F1 Gestão de Contas | Cabe, se tem venda B2B a prazo | Cabe (prioridade) | Cabe |
| F2 Antecipação | Cabe, carteira registrada | Cabe | Cabe; avaliar F3 |
| F3 FIDC | **Não cabe** (custo fixo) | Só se recebíveis cedíveis acima de R$ 10 mi/mês | Cabe |
| F4 CI | **Não cabe** (piso de faturamento e de ticket) | Cabe se tiver garantia livre de 2x e necessidade de US$ 5 mi ou mais | Cabe |
| F5 Captação | Cabe (equity ou fundo, ticket depende do fundo) | Cabe | Cabe |
| F6 e F7 Kit e preparação | Cabe (pré-requisito) | Cabe | Cabe |
| F8 e F9 Paraguai | Corte de R$ 20 mi/ano, no Lucro Real, 100 empregados na produção ou folha de 20% do custo | Cabe | Cabe; atenção ao Pilar 2 (€ 750 mi) |
| F10 Zona Franca | Só logística e reexportação | Cabe como cenário | Cabe como cenário |
| F11 Governança exterior | Só com operação ativa | Idem | Idem |
| F12 Turnkey | Só após capacidade e caixa | Cabe em 2ª rodada | Cabe em 2ª rodada |
| F13 Tax internacional | Só com controlada ou remessa | Cabe | Cabe |
| F14 Fin. exportação | Cabe (exportador) | Cabe | Cabe |
| F15 Hedge | Se tem dívida em moeda forte | Cabe | Cabe |
| F16 CPR e CRA | CPR cabe; CRA não | CPR e CRA se houver parceiro | Cabe |

### 2.2 Pisos de ticket e de volume por fonte de funding
| Fonte | Piso | Observação | Situação |
|---|---|---|---|
| CI, estrutura suíça | US$ 5 mi (cerca de R$ 25,4 mi ao PTAX de R$ 5,0826 de 16/10; a base usa R$ 26 mi a R$ 5,22) | Abaixo disso não há estrutura confirmada | Oficial v2.3 |
| CI, estrutura americana | US$ 10 mi (cerca de R$ 50,8 mi) | Exige garantia livre de cerca de 2x (cerca de R$ 100 mi) | Oficial v2.3 |
| Fundos de equity ou dívida da R1 | Alguns com piso de US$ 10 mi; "um aceita ticket menor" | Qual e quanto: sem resposta (B17) | Fala de reunião |
| FIDC | Recebíveis cedíveis acima de cerca de R$ 10 mi/mês; custo de R$ 80 mil/mês | Benchmark público confirma a ordem de grandeza | Interno, a confirmar |
| Antecipação | Sem piso informado | Limite de 30% da carteira registrada | A confirmar |
| Maquila | Cerca de R$ 20 mi/ano de faturamento sem fundo; cerca de R$ 50 mi no pacote com o CI | Hipótese (MQ-Q2) | A validar |
| Atalho 13/10 para funding | Ativos ou garantias acima de R$ 60 mi e operação acima de R$ 30 mi | Só filtro de lista; vale o v2.3 para qualificar | Conflito, seção 5 |
| Debt: bonds | Mercado de empresa acima de cerca de US$ 100 mi já acessa bonds e multilaterais | Fora do alcance de empresa de R$ 50 a 500 mi | Radar |

### 2.3 Casos em que não cabe (e para onde ir)
| Caso | Por que não cabe | Saída |
|---|---|---|
| Necessidade abaixo de US$ 5 mi (por exemplo R$ 20 mi, cerca de US$ 3,9 mi) | Abaixo do piso do CI (K1) | F5 (equity ou sócio), F2, home equity, crédito nacional; pergunta ao João sobre estrutura menor |
| Receita 100% em reais, sem hedge natural | Economia do CI vira carry cambial | Crédito nacional, F2, F3; ou F14 se exportar |
| Precisa do recurso em menos de 3 meses | Ciclo mínimo de cerca de 3 meses (K5) | F2, F1, passivo |
| RJ, extrajudicial ou falência no grupo (K7) | Elimina CI | Passivo e reestruturação; FIDC pode comprar recebível performado de empresa em RJ (CVM 240) |
| Débito tributário relevante sem certidão | Bloqueia garantia e diligência; dívida ativa pode presumir fraude na oneração (CTN art. 185) | Gestão de Passivo antes |
| Receita não formalizada | Risco alto; só números da contabilidade | Planejamento para nota cheia; sem F3 |
| Garantia já alienada a banco ou estoque como garantia principal | K2 | F2, F16 |
| Já usa crédito rural dentro dos limites | CI só entra no que exceder | Manter e complementar |
| Frigorífico no MQ | D59 bloqueia; encaixe da carne em aberto (MQ-Q6) | CI e recuperação |
| Maquila só para pagar menos IR | Lucro da controlada é tributado no Brasil | Planejamento tributário (P8) |
| FIDC com carteira concentrada, curta ou sem nota | Não fecha a conta | F2 ou cessão a FIDC existente, CR, nota comercial |
| Produtor de grãos muito alavancado em MT, GO, PR, MS ou MG | Sinal de não candidato | CPR e reestruturação |

### 2.4 Fluxo de decisão: qual produto para qual caso
1. **Há débito fiscal, RJ ou protesto?** Sim: Gestão de Passivo e Produtos Jurídicos primeiro; volta ao fluxo depois da certidão. Não: segue.
2. **Qual é a dor principal?**
   - Caixa apertado, vencidos, antecipação cara: F1, depois F2.
   - Dívida bancária cara, parcelas pesadas: passivo bancário e alongamento (P6, sem ficha), depois F4 se houver garantia.
   - Precisa de capital para crescer: ir ao passo 3.
   - Quer produzir ou vender fora: ir ao passo 5.
3. **Capital para crescer. A empresa tem demonstrações de 2 anos, plano e controle?** Não: F6 e F7 antes. Sim: passo 4.
4. **Dívida ou equity?** Faturamento comprovado de R$ 50 mi ou mais, garantia livre de cerca de 2x e necessidade de US$ 5 mi ou mais: F4 (descoberta, até o G2). Garantia agro: F16 também. Ticket abaixo do piso ou sem garantia: F5. Recebíveis acima de R$ 10 mi/mês: F3. Pode combinar F3 com F4 na cadeia do café.
5. **Produzir fora.** Indústria no Lucro Real com mão de obra ou energia pesada e origem Mercosul viável: F8 (estudo). Se o estudo for favorável: F9, com F13 e depois F11. Só logística: F10. Vender fora, com capacidade pronta: F12, F14, F15.
6. **Tem moeda forte (dívida ou exportação)?** F15 e F14.
7. **Limites:** no máximo 2 produtos novos por vez; produto em validação só como descoberta, com a data do portão.

---

## 3. Esteira de capital: o que vem antes de quê

| Etapa | O que precisa estar pronto | Produtos | Abre a próxima porque |
|---|---|---|---|
| 0. Diagnóstico | Parecer fiscal, DRE, balanço, SCR, e-CAC | F1 (abre o acesso), P1 | Gera dados e confiança |
| 1. Destravar caixa (0 a 6 meses) | Carteira B2B e débitos mapeados | F1, F2, recuperação tributária | O crédito recuperado é o primeiro dinheiro novo e vira lastro |
| 2. Passivo organizado | Certidão negativa; dívida cara renegociada | Gestão de Passivo, alongamento (P6) | Sem certidão e sem passivo claro não há garantia nem diligência |
| 3. Plano e controle | Contabilidade confiável, plano, projeção, nota cheia | F6, F7, planejamento, CFO (N2) | O funding e o FIDC exigem plano, controle e título com nota |
| 4. Funding | Etapas 2 e 3, garantia livre, ticket acima do piso | F4, F5, F3, F16 | Dá capital para o investimento planejado |
| 5. Expansão | Capital contratado e capacidade organizada | Capex, F8 e F9 (planta), F3 da cadeia | Aumenta capacidade e margem |
| 6. Internacional | Capacidade e caixa no Brasil; operação ativa fora | F9 em operação, F12, F13, F11, F14, F15 | Escala em mercado externo e receita em dólar |
| Camada contínua | Cliente ativo | Revisão tributária anual, painel DRE × SCR × e-CAC, recorrência do FIDC, F11 | Mantém o cliente por anos |

Regras de sequência: (1) passivo antes de crédito novo; (2) plano antes de funding; (3) funding antes de expansão; (4) expansão antes de internacional (capacidade e caixa primeiro); (5) estudo antes de proposta e número do cliente antes de benchmark; (6) cada serviço é contratado em separado e nenhum é condição para o crédito; (7) reorganizar dívida **antes** do crédito só como sequência técnica (quitação, baixa, nova garantia), nunca como exigência comercial.

---

## 4. Verificação da pesquisa de hoje (22/10/2026)
Ferramenta: busca web padrão, sem acesso ao texto integral dos atos. Tudo abaixo continua "a conferir no texto oficial".

| Tema | O que encontrei | Link | Confirmei? |
|---|---|---|---|
| Lei 7.548/2025 e Lei 60/90 | Lei 7.548 promulgada em 08/09/2025; **revoga integralmente a Lei 60/90 e o Decreto-Lei 27/90**; regulamentada pelo Decreto 5.432/2026; bens de capital listados em anexo de resolução biministerial; tolerância de 20% no valor de importação; inclui ativos intangíveis; parâmetro de emprego de 1 por US$ 50 mil de investimento. Mínimo geral de investimento e lista de bens: não localizei | [Bloomberg Tax](https://news.bloombergtax.com/daily-tax-report/paraguay-gazettes-law-introducing-tax-incentive-regime-for-national-foreign-investments) · [Ferrere](https://www.ferrere.com/es/novedades/se-reglamento-la-nueva-ley-de-incentivos-fiscales/) · [MIC, Decreto 5432](https://www.mic.gov.py/wp-content/uploads/2026/06/DECRETO5432_compr.pdf) · [BACN, Lei 7.548](https://www.bacn.gov.py/leyes-paraguayas/12854/ley-n-7548-2025-que-establece-el-nuevo-r-gimen-de-incentivos-fiscales-para-la-inversi-n-nacional-y-extranjera) | Parcial (não abri o texto) |
| DCBE | Obrigatória com ativos no exterior de US$ 1 mi ou mais em 31/12; trimestral a partir de US$ 100 mi; multa de 1% até R$ 25 mil no atraso simples; datas do ciclo 2026 divergem (2, 5 ou 6 de abril) | [Demarest](https://www.demarest.com.br/?p=165961) · [NetCPA](https://netcpa.com.br/colunas/dcbe-2026-saiba-quem-deve-declarar-ativos-no-exterior-e-os-prazos/27343) | Parcial; sem fonte do BCB |
| Duplicata escritural | Base: Lei 13.775/2018 e Res. BCB 339/2023 (art. 39); Res. CMN 4.815/2020 trata da negociação pelas instituições. **A ficha anterior citava "Res. BCB 4.815/2020": o órgão correto é o CMN.** Cronograma de obrigatoriedade diverge em 3 versões | [Lefosse](https://lefosse.com/noticias/alerta/duplicatas-escriturais-o-que-muda-na-emissao-no-registro-e-na-negociacao-de-recebiveis) · [CERC](https://www.cerc.com/wp-content/uploads/2026/07/Inicio-da-Operacao-em-Producao-Assistida-das-Duplicatas-Escriturais.pdf) · [Finsiders](https://finsidersbrasil.com.br/?p=361516) | Parcial |
| CRA e CPR | Res. CMN 5.118/2024 com 5.121/2024 e 5.212/2025; deslocamento para a CPR-F; CRA em CPR-F registrado na CVM em 01/06/2026. Nada de 2026 do CMN | [Capital Aberto](https://capitalaberto.com.br/artigos/entre-o-cra-e-a-cpr-f-como-a-regulamentacao-redesenha-o-financiamento-do-agronegocio/) · [Voto CMN 57/2024](https://normativos.bcb.gov.br/Votos/CMN/202457/Voto_do_CMN_57_2024.pdf) | Parcial |
| Seguro de crédito à exportação | FGE administrado pela ABGF; pós-embarque retomado em 2024; COFIG de 22/05/2026 aprovou novo produto para MPMEs; limites de enquadramento divergem. ACC e ACE: não achei fonte nova | [Tesouro Nacional](https://www.gov.br/tesouronacional/pt-br/execucao-orcamentaria-e-financeira/operacoes-oficiais-de-credito/fomento-a-exportacao) · [Legisweb](https://www.legisweb.com.br/noticia/?id=30461) | Parcial |
| CVM 160 | Oferta pública conforme o alcance da comunicação; consulta SDM 03/25 sobre oferta privada; intermediação por remuneração: não achei | [Demarest, quadro CVM 160](https://demarest.com.br/wp-content/uploads/2024/07/DEMAREST_Quadro_Comparativo_Resolucao_CVM160_vs_FACIL_v1.pdf) · [Capital Aberto](https://capitalaberto.com.br/insights/vortx/2026/07/safe-harbor-e-o-rito-aliviado-liberdade-dentro-e-fora-da-regulacao) | **Não** (lacuna para o Jurídico) |
| Tributos do Paraguai | IRE de 10%, IVA de 10% (5% cesta), dividendos de 8% (residente) e 15% (não residente), INR de 15% (Lei 6.380/2019); fontes de 2019 a 2020 | [Ferrere](https://www.ferrere.com/en/news/paraguay-promulgan-ley-de-modernizacion-y-simplificacion-del-sistema-tributario-nacional/) | Parcial; atualização não confirmada |
| Hedge | NDF de balcão com spread maior que o listado (Exame, ago/2026); normas de derivativos: não confirmei | [Exame](https://exame.com/lideres-extraordinarios/os-custos-invisiveis-do-hedge-cambial/) | Não |

Não confirmei: CRS do Paraguai; custo de ACC e PPE em 2026; honorários de debt advisory; parceiro de administração do FIDC; texto da Lei 7.547 (BACN fora do ar em 21/10).

---

## 5. Conflitos entre fontes internas e recomendação

| # | Conflito | Fontes | Recomendação |
|---|---|---|---|
| 1 | **Critério do CI:** v2.3 (faturamento de R$ 50 mi/ano, US$ 5 mi ou 10 mi, garantia de 2x) × reunião de 13/10 (ativos acima de R$ 60 mi e operação acima de R$ 30 mi) × R$ 30 mi como filtro de base (02/10) | `elegibilidade.md`, `produtos.md`, B18 | **Qualificar pela v2.3.** Usar R$ 30 mi só para filtrar lista e R$ 60 mi só como sinal de porte. O João escolhe um critério por escrito (pergunta 7). Cortes de 1,5x de garantia e R$ 30 mi de faturamento ("em desenvolvimento") ficam como proposta interna |
| 2 | **Linhas de porte:** "média" até R$ 10 mi/mês (handoff) × CI a partir de R$ 50 mi/ano (R$ 4,2 mi/mês) × FIDC acima de R$ 10 mi/mês | handoff, v2.3 | Corte **por produto**, como na seção 2.1; o Luis decide se mantém "média/grande" no material do parceiro |
| 3 | **Taxas ditas em reunião:** 8% a 12% e carência de até 3 anos (R1, frente de internacionalização); 6% a 10% e 11% a 12% no café (02/10); referência interna de cerca de 8% em moeda forte; carência "2 a 3 anos" para tudo | R1, 02/10, v2.3 | **Nenhuma taxa vale ao cliente.** A v2.3 é a única fonte; carência: só na suíça (até 3 anos, bullet de até 6 em casos específicos), não na americana. Em franco suíço, 8% seria spread de cerca de 800 bps (SARON perto de 0%), o que não parece coerente: perguntar a taxa **por moeda** |
| 4 | **Hedge:** "cerca de 1 p.p. ao ano" (base) × 9,7% a.a. em dólar e 14% em franco (paridade, 16/10); com gross-up e hedge, o custo em reais fica perto de 19% a 20% a.a. | `produtos.md`, radar | Tratar "1 p.p." como erro provável até o João explicar o instrumento; nunca citar; toda comparação de custo em 3 cenários: sem hedge, com hedge, com hedge natural |
| 5 | **Lei 60/90 × Lei 7.548/2025:** o handoff e o parceiro (R2, "Lei 6090") falam da Lei 60/90 combinável com a maquila; a pesquisa mostra que a 7.548 **revogou** a Lei 60/90 em 08/09/2025, regulamentada pelo Decreto 5.432/2026 | handoff, R2, `maquila-fontes-oficiais.md`, [WEB 22/10] | **Citar a Lei 7.548/2025 e o Decreto 5.432/2026.** Corrigir o Mapa de Entregas. A frase "combina com a maquila" vira hipótese: ler o anexo de bens de capital, o prazo de 5 anos de propriedade e o limite de 5 anos de uso do bem, e pedir ao assessor paraguaio |
| 6 | **Lei da maquila:** Lei 1.064/97 (handoff, R2) × Lei 7.547/2025 e Decreto 5.714/2026 | `produtos.md`, fontes oficiais | Vale a 7.547. Todo material com a 1.064 está desatualizado |
| 7 | **Base do 1%:** "sobre valor agregado" (R2, handoff, simulação do frigorífico) × "o maior entre valor agregado e fatura de exportação" (art. 37) | `maquila-fontes-oficiais.md` | Usar o texto da lei; refazer qualquer simulação com a fatura como base alternativa; simulações do Mapa de Entregas ficam fora de parceiro e cliente |
| 8 | **Estudo do Paraguai:** "primeiro serviço" (R2) × sem estudo pago até 30/06/2027 (D51, geladeira) | R2, `produtos.md` | Manter a regra D51: descoberta no Q4; o estudo pago depende de G2 e G3 do MQ. Decisão do Luis e do João |
| 9 | **Salário mínimo PY:** cerca de 68% maior (base) × cerca de 57% (câmbio de 16/10); encargos 25% a 30% × 65% a 80% (base) × 35% × 100% (Forbes); energia "cerca de 30% do custo brasileiro" (R2) ou "2x mais barata" (base) sem tarifa geral localizada e com alta prevista | R2, radar | Citar uma fonte e a data do câmbio; tratar energia como hipótese em queda; só em estudo individual |
| 10 | **Cenário do caso de R1:** o ecossistema diz "R$ 20 mi, cerca de US$ 2 mi"; ao PTAX de 16/10, R$ 20 mi são cerca de US$ 3,9 mi | `ecossistema-produtos-servicos.md` | Corrigir. Continua abaixo do piso de US$ 5 mi, mas a distância é menor do que parecia: reforça a pergunta B17 |
| 11 | **Fee do CI:** exemplo de 10% (30/09) × orientação de não citar percentual (06/10) × benchmark de assessoria de 1% a 3% | B8, radar | Não citar percentual; pedir ao João o racional e se o fee entra no custo total que a credora analisa; cuidado com cobrança dupla CI e MQ (MQ-Q13) |
| 12 | **IOF:** "zero ou 0,38%" × zero acima de 364 dias e 3,5% até 364 (Decreto 12.499) × "via token, sem IOF" | regras §4, radar | Corrigir regras §4 [VALIDAR TRIBUTÁRIO]; fechar a tese do token como sem benefício e risco alto |
| 13 | **Duplicata escritural:** citação "Res. BCB 4.815/2020" e cronograma 2027 a 2028 com 3 versões | `fichas-sem-reuniao.md`, [WEB 22/10] | Citar Res. BCB 339/2023 (escrituração) e Res. CMN 4.815/2020 (negociação); confirmar o cronograma no art. 39 |
| 14 | **Estado de GC, antecipação e FIDC:** MVP e sem portão (13/10) × pronto (19/10) | `produtos.md`, ecossistema | Vale 19/10. Manter as cautelas e a regra "validado só quando o 1º recurso cai" apenas para o CI |
| 15 | **Gestão de Contas:** receita "multa e juros" e "1,5% da carteira" × teto de 2% de multa no consumidor e juros pela taxa legal | radar, handoff | Testar o 1,5% contra B2C; contrato com multa e juros previstos; segmentar por tipo de devedor |
| 16 | **Garantia:** "2x" (v2.3) × "220% a 250%" (02/10) | B2 | "Garantia real robusta, avaliada caso a caso" ao cliente; 2x só na pergunta interna |
| 17 | **Fundos menores que US$ 10 mi** (R1) × piso suíço de US$ 5 mi (v2.3) e "abaixo de US$ 5 mi não segue" | R1, B17 | Pergunta ao João: existe estrutura abaixo de US$ 5 mi? Se não, o caso de R1 vai por F5 |
| 18 | **Lei 60/90 na ficha de bens de capital:** a reunião diz isenção "ou redução" de imposto de importação; a 7.548 isenta tarifas e IVA, com exigências | R2, [WEB 22/10] | Não prometer isenção; aguardar leitura do anexo |

---

## 6. Perguntas ao João Mattos, em ordem de prioridade
Respostas escritas até 31/10/2026 (D38 e D56). Reaproveita `perguntas-ao-dono.md` e acrescenta as novas (marcadas **NOVA**).

### Prioridade 1: destravam G1 e G2 (até 31/10)
1. **CI · cobrança de análise:** confirmação escrita de que não há cobrança para análise (B9, A20).
2. **CI · garantias não aceitas** e exigência de liquidez (B3).
3. **CI · recebíveis de safra, contrato futuro de café e recompra de dívida como garantia** (B15, B16).
4. **CI · regra do fee:** percentual padrão, base (contratado ou liberado), por parcela, quem paga, divisão com o parceiro (B8; D61).
5. **CI · entrada dos recursos no Brasil:** moeda, câmbio, spread, CDNR, mandatário no SCE-Crédito, conta em moeda estrangeira (Res. 575), IR na fonte com gross-up e a tese "via token".
6. **CI · empresa do grupo que assina** com cliente, instituição e parceiro; enquadramento regulatório da Save (Bacen, Coaf).
7. **CI · critério oficial de corte:** R$ 50 mi de faturamento, ou ativos acima de R$ 60 mi e operação acima de R$ 30 mi (B18).
8. **MQ · escritório no Paraguai:** existência, escopo e capacidade em 3 linhas escritas (MQ-Q1).
9. **MQ · critérios mínimos, preço R1 a R5 e rateio** (MQ-Q2 a Q4).
10. **MQ · dono de cada etapa e encaixe dos frigoríficos** (MQ-Q5 e Q6).

### Prioridade 2: protegem o G2 e a economia do produto
11. **NOVA · Captação (F5):** quais fundos e bancos existem na rede, com ticket mínimo de cada um; existe fundo abaixo de US$ 10 mi e estrutura abaixo de US$ 5 mi (B17); quem enquadra o equity na CVM e como a remuneração da Save é feita sem ser oferta pública nem intermediação não autorizada.
12. **NOVA · Hedge:** o "1 p.p. ao ano" é cotação de qual instrumento, prazo e contraparte? (radar P1).
13. **NOVA · Forma da credora americana:** banco com licença, fundo registrado ou LLC? Regime fiscal nos EUA (Cosit 56/2026). E a credora suíça é banco licenciado, com uso que caiba no art. 11 do tratado (radar P2 e P4).
14. **NOVA · Taxa por moeda:** a referência de cerca de 8% vale para dólar e franco? Fixa ou SOFR/SARON mais spread? (radar P3).
15. **NOVA · Diligência da credora (K11):** podem mostrar ao menos 1 operação com empresa brasileira, com código SCE-Crédito?
16. **NOVA · Fee × mercado:** qual o racional do fee frente ao benchmark de 1% a 3% de assessoria?
17. **NOVA · Estudo do Paraguai (F8):** o estudo pode ser cobrado antes de 30/06/2027 (D51)? Quem o executa e com que preço (R2)?
18. **NOVA · Bens de capital (F9):** a Lei 7.548/2025 e o Decreto 5.432/2026 substituem a "Lei 60/90" que o parceiro citou? Há combinação com a maquila? Quem lê o anexo de bens?
19. **NOVA · Base do 1% da maquila:** valor agregado ou fatura de exportação, por modelo (art. 37)? A simulação do frigorífico será refeita?
20. **MQ · o fundo do CI financia capex no Paraguai?** Quem é o tomador, ativos no Paraguai servem de garantia, carência suíça vale para greenfield (MQ-Q7 a Q12).

### Prioridade 3: antes do material e da escala
21. **NOVA · Submaquila (F9):** existe fábrica local do ramo com capacidade? Quem responde pela qualidade e pela perda?
22. **NOVA · Governança no exterior (F11):** quem presta as 3 verticais (Save, associado local ou parceiro)? Como evitar o conflito entre prestar e auditar? Quem é o advogado habilitado?
23. **NOVA · Turnkey (F12):** o que existe de fato na rede de representantes dos 11 países? Há contrato, modelo de remuneração e capacidade?
24. **NOVA · Tax internacional (F13):** qual é a linha do parceiro sobre sigilo e CRS, e o que a Save diz e proíbe em material? O Paraguai está mesmo fora do CRS?
25. **NOVA · Zona Franca (F10):** a Save quer oferecer como serviço de implantação, com quem?
26. **NOVA · Café:** haircut sobre estoque, CPR e contrato futuro com o café oscilando; exige conformidade com a EUDR (30/12/2026) e CAR?
27. **CI · demais (G2):** exclusividade de estrutura, prazo total da suíça, equipe do banco, pós-contrato e suspensão de parcela, inadimplência, papel do family office, Save Bank, usinas e máquinas, prejuízo, receita não formalizada.
28. **MQ · Q13 a Q24:** cobrança combinada com o CI, menção do fundo ao cliente, assessor paraguaio, prazos, empresa contratante, escopo de compliance e contencioso, nome e canais, piloto, uso da base, maquila de terceiros, ordem de grandeza de preços.

### Ao Júnior e à Save Invest (não ao João)
Contratante e habilitação da Gestão de Contas e da antecipação; taxa da antecipação; remuneração do parceiro; parceiro de administração e gestão do FIDC; custo de R$ 80 mil/mês em propostas reais; piso de volume; reunião de multicedente; teste do 1,5% contra devedor consumidor; enquadramento regulatório da instituição que antecipa.

### Ao Jurídico e ao Tributário
CVM em equity, FIDC e Forma 2; intermediação de crédito (Lei 4.595 e Lei 7.492); PLD e Coaf (Lei 9.613 art. 9º XIV); OAB e remuneração de parceiro; regime privilegiado do Paraguai e da LLC; IOF por tranche; subcapitalização; preço de transferência; sigilo e CRS na linha do parceiro.

---

## 7. As 5 lacunas que travam a validação
1. **Quem contrata, quem presta e qual enquadramento regulatório** (Save, Save Invest, SEI, Federal Invest, empresa do grupo; Bacen, CVM, Coaf, OAB). Trava G2 do CI e a venda de F1 a F3.
2. **Critério único de elegibilidade e de ticket** (R$ 50 mi × R$ 60 mi e R$ 30 mi; piso de US$ 5 mi; fundos de equity). Sem ele, a qualificação e a varredura da base não fecham.
3. **Fee, remuneração e economia do crédito** (regra do fee, D61 só no CI, MQ-Q3 e Q4, o hedge de 1 p.p. contra 9,7%, gross-up). Trava aditivo do parceiro e a conta de receita.
4. **Base do Paraguai** (escritório e assessor local sem confirmação, texto da Lei 7.547 e 7.548 não lido, base do 1%, estudo pago só após 30/06/2027). Trava G0 e G1 do MQ.
5. **Parecer jurídico escrito e diligência do credor** (CVM em captação e FIDC, PLD, token, K11 com ao menos 1 liberação documentada). Trava G2 e G3 de 15/12.

---

## 8. Registro de revisão
```json
{"revisao": {"gerente": "Gerente de Produtos Internacionais e Financeiros",
 "especialistas": ["Qualificador de Crédito", "Estruturador de Garantias & Projeto", "Café & Agro", "Maquila & Internacionalização", "Analista do Ecossistema Financeiro", "Regulatório & Câmbio", "Guardião G0-G4", "Revisor de Linguagem"],
 "rodadas": 2,
 "areas_consultadas": [],
 "aprovado": false,
 "ajustes": ["R1: layout igualado nas 16 fichas; taxas e prazos tirados dos campos de ficha e mantidos só como conflito interno",
             "R2: conferidas as frases proibidas (fundo internacional, holding, blindagem, via token) e a trava do G2; citação de duplicata corrigida (CMN 4.815 e BCB 339); US$ 2 mi do caso de R1 recalculado para US$ 3,9 mi",
             "Pendente: Jurídico e Tributário não revisaram; auditor de promessas (`auditar_texto.py`) não rodado; textos oficiais não abertos"]}}
```
**Por que "areas_consultadas" está vazio:** esta entrega é rascunho interno; passa por Jurídico, Tributário e Qualidade antes de qualquer peça para fora, e o Luis vê um exemplo antes da escala.
