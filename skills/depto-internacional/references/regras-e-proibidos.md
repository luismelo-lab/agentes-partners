# Regras, limites e o que não dizer

> Uso interno. Data-base: 16/10/2026.
> **PRÉ-ANÁLISE JURÍDICA E TRIBUTÁRIA: não substitui parecer.** Nenhuma norma abaixo foi conferida no texto oficial por humano. Todas são "referência a verificar", com vigência a confirmar na data de cada operação. Validadores humanos: advogado(a) e técnico tributário designados (nomes a preencher; D38, D55).
> Fontes: `06-faq.md` Parte 5; `21-documento-interno.md` v2.3; `09-revisao-juridica-tributaria.md`; `04-plano-comercial.md` §9; `07-comparativo-mercado.md` §4; `16-estudo-tomadores.md` §6; `06-documento-oficial-maquila.md` §11 e §13; `05-gtm-maquila.md` §10.4; revisões v10 do kit de 07/10/2026 (Jurídico, Produto/Tributário) e consolidação v11; `PADRAO-PRODUTO-NOVO.md`; reunião de 13/10/2026.

---

## 1. Regras de ouro (valem para todo produto do departamento)

1. **Nada sai antes do G2.** Sem parecer jurídico humano escrito, nenhuma conversa com parceiro ou cliente sobre condições (taxa, prazo de pagamento, custo, fee). Ninguém valida "por formação" (D30; Padrão, princípio 3).
2. **A Save é estruturadora, nunca credora.** Não concede crédito, não antecipa recebíveis, não distribui cotas.
3. **Agentes produzem rascunho; pessoas aprovam.** Nenhum agente fala com parceiro ou cliente, altera HubSpot ou GLPI, ou abre chamado sem aprovação.
4. **O comercial abre a porta; o especialista conduz.** Taxa, garantia, câmbio e tributo são do especialista.
5. **Canal privado e seletivo** no CI: sem redes sociais, anúncio ou material publicitário na validação.
6. **Toda fonte com data.** O resto leva `[HIPÓTESE]`, `[A DEFINIR COM <DONO>]`, `[VALIDAR JURÍDICO]` ou `[VALIDAR TRIBUTÁRIO]`.
7. **Sem dado pessoal.** Nenhum documento traz telefone, e-mail, CPF, dado bancário ou nome de cliente em análise. Use `<EMPRESA>`.
8. **Sem nome de instituição, representante ou autoridade estrangeira** em material. Não contar como o acesso aos fundos foi obtido.
9. **Material externo com zero alerta ALTO ou MÉDIO** nas regras do produto (auditor `auditar_texto.py`; regras CI pendentes, D39).
10. **Câmbio com honestidade:** o risco existe; não opinar sobre o rumo do dólar.

---

## 2. Frases proibidas → o que dizer

### 2.1 Crédito Internacional
| Não diga | Diga no lugar |
|---|---|
| "Depois do contrato assinado, o dinheiro é garantido" | "Os recursos são liberados na forma e no cronograma definidos pela instituição credora." |
| "Aprovado", "aprovação garantida", "sai em 90 dias", "sem risco" | "A decisão é da instituição, depois da análise." |
| "A taxa é de 8%" / "6% a 10%" / "11% a 12% no café" / "8% a 12%" | "A taxa é definida pela instituição após a análise de crédito." |
| "Dinheiro barato", "mais barato que o banco", "metade do custo do banco" | "Crédito de longo prazo, com custo que pode ser competitivo frente ao crédito nacional, e com exigências sérias." |
| "Precisa de garantia de 220% a 250%" / "duas vezes" ao cliente | "Garantia real robusta, avaliada caso a caso." (A referência de 2x pode entrar na pergunta de qualificação P3, que é interna ao roteiro.) |
| "Carência de 2 a 3 anos e 12 anos para pagar" | "Há estruturas com e sem carência; o prazo é definido pela instituição." |
| "Não tem taxa de análise" / "tem investimento para a análise" | "As condições de custo vêm por escrito antes de qualquer compromisso." |
| "Pagamento antecipado relevante" (dá a entender que há algum) | "Não há pagamento antecipado ao fundo." (só depois da confirmação escrita do dono) |
| "A análise sai em 15 a 20 dias" / "em 6 meses o dinheiro entra" | "É uma operação de alguns meses; não é solução imediata de caixa." |
| "É tokenizado, via blockchain, e não paga IOF" | Não tocar no assunto. Se perguntarem: "Entrada dos recursos e tributos são tratados pelos especialistas e pelo jurídico na etapa técnica." |
| "Hedge custa 1% ao ano" | "Existe opção de proteção cambial, com custo, avaliada com o seu assessor financeiro." Exceção (D77, 22/10/2026): só na proposta do originador sucroenergético (Canex), a resposta aprovada é "o hedge acrescenta cerca de 1% sobre o valor solicitado" (fala do João). |
| "O dólar não vai subir" / "não há risco de câmbio" | "O risco cambial existe. Para quem exporta, a receita em moeda forte ajuda." |
| "O acesso ao Brasil é só por nós" / exclusividade | Não falar em exclusividade. |
| "O fundo já aceitou fluxo futuro como garantia" | "Recebíveis podem ser avaliados." |
| "Fundo internacional" como nome de produto; "investidores" | "Crédito internacional"; "instituições credoras". |
| "A Save leva crédito" / "estrutura projetos **para** instituições" | "A Save estrutura projetos dos clientes para a análise de instituições dos Estados Unidos e da Suíça." |
| Nome da instituição, do representante, de autoridade estrangeira ou de cliente | "Instituições parceiras nos EUA e na Suíça." Exceção: a UBS no one-page confidencial e na proposta Canex (D77 e D88). |
| Percentual de fee ou de remuneração do comercial ou do parceiro | "Os detalhes vão no contrato, por escrito." |
| "Já fizemos várias operações" / usar o caso da construtora como prova | "O produto está em fase inicial, com poucos casos selecionados." |
| "Reorganize a dívida antes do crédito" / "contrate X para ter o crédito" | "Cada serviço é contratado em separado; nenhum é condição para o crédito." |
| "O fundo recusou" (sem análise) / "talvez dê, vamos tentar" | Usar o roteiro de saída (`17-qualificacao.md` §9). |
| Números de recuperação judicial para pressionar o cliente | Esse dado é só para a qualificação interna. |

### 2.2 Maquila
| Não diga | Diga no lugar |
|---|---|
| "Com a maquila você paga só 1% de imposto." | "O regime tem tributo único de 1% no Paraguai; para a empresa brasileira, o lucro continua tributado no Brasil." |
| "Você vai economizar 28%." | "Só o estudo com os seus números mostra se faz sentido." |
| "Economia garantida." / "Sem risco." | "O estudo mostra o saldo e os riscos antes de qualquer decisão." |
| "O produto entra no Brasil sem imposto." | "Com origem Mercosul válida, o imposto de importação é zero; os demais tributos seguem a regra normal." |
| "A mão de obra no Paraguai é mais barata." | "Os encargos sobre a folha são menores e há mais disponibilidade de mão de obra." |
| "A empresa X fez com a gente." | Não citar casos públicos como se fossem da Save. |
| "O fundo financia a sua fábrica no Paraguai." | "O financiamento é avaliado caso a caso pelo especialista." |
| "Aprovação em 90 dias." | "O cronograma é definido no estudo." |
| "A regra é estável por 20 anos." | "O programa dura até 20 anos; as regras podem mudar." |
| "Já temos vários clientes no Paraguai." | "O produto é novo; o diferencial é o estudo com fonte oficial." |
| "A Save tem escritório próprio no Paraguai." | "A forma de atuação no Paraguai é apresentada pelo especialista." (até a confirmação escrita, MQ-Q1) |
| "Centenas de empresas brasileiras já produzem lá." | "Mais de 160 empresas com capital brasileiro operam hoje no regime (Prensa Mercosur, 13/08/2026)." |
| "Quanto custaria produzir a sua linha no Paraguai?" | "Vale a pena produzir parte da sua linha no Paraguai? O estudo responde, inclusive quando a resposta é não." |
| "Fuja da carga brasileira" / "estrutura offshore" | Não usar. |
| "Exportar e produzir fora do Brasil" (como se a Save fizesse) / "dezenas de países" | "Apoio para abrir mercados e estruturar a exportação" (11 países citados). |
| "A carga no Paraguai é menor" (sem estudo) | "Depende de análise tributária específica." |

### 2.2-A Novas frases (transcrição de 21/10/2026; detalhe em `especialistas/revisor-linguagem-promessas.md` §2.2)
| Não diga | Diga no lugar |
|---|---|
| "O Paraguai não está no CRS; o Brasil pode nunca ficar sabendo" | "A estrutura é declarada no Brasil (IRPF, CBE); a vantagem está no custo de produzir." |
| "Deixe o lucro no Paraguai; no Brasil, lucro mínimo" | "O lucro da controlada continua tributado no Brasil, e o preço entre as empresas segue o valor de mercado." |
| "Lei 6090: com o mesmo dinheiro você monta duas fábricas" | "Há incentivo à importação de bens de capital no Paraguai (Lei 7.548/2025), com requisitos; o estudo diz se cabe." |
| "Entra como monofásico; o imposto tende a zero" | "Com origem Mercosul válida, o II é zero; os demais tributos seguem a regra e geram crédito." |
| "Nos EUA o Brasil paga 40% e o Paraguai 10%" | "As tarifas dos EUA mudam; analisamos a NCM do seu produto na data." |
| "Payback de 3 anos"; "20% a 30% mais barato" | "Só o estudo com os seus números mostra o retorno." |
| "Isso é uma garantia que eu dou" | "O estudo mapeia os riscos antes de qualquer decisão." |
| "Temos investidores para isso"; "fundos que aceitam valores menores" | "Apresentamos a quem faz sentido, e o investidor decide." |
| "Seu imóvel cobre"; "dá para ficar dois anos sem pagar" | "A instituição avalia e decide; primeiro mapeamos a dívida e o caixa." |

### 2.3 Ecossistema e institucional
| Não diga | Diga no lugar |
|---|---|
| "A Save antecipa recebíveis" / "antecipação de recebíveis da Save" | "A antecipação é operada pela Federal Invest; a Save (SEI) cuida da cobrança." [VALIDAR JURÍDICO: confirmar a autorização e o regime de quem antecipa] |
| "Gestão de contas" como serviço financeiro da Save sem escopo | "Gestão financeira (BPO): contas a pagar e a receber organizadas para decidir" [confirmar escopo e quem presta] |
| "Patrimônios protegidos", "blindagem", "holding para proteger bens" | "Estruturação patrimonial." Nunca diante de credor ou antes de um crédito com garantia. |
| "Holding" | "Estruturação patrimonial" (13/10). |
| "Carry Trade" fora do sentido técnico | Não usar. |
| "Conta escrow blinda contra bloqueio" | "Reduz o bloqueio automático; não impede bloqueio por ofício." |
| "A partir de 2027, PIS e Cofins dão lugar à CBS e ao IBS" | "Em 2027, a CBS substitui PIS e Cofins; o IBS substitui ICMS e ISS aos poucos, até 2033." |
| "Créditos acumulados na exportação" para trading comercial exportadora | "Avaliar, caso a caso, se há tributos a recuperar." (a usina mantém créditos; a trading com fim específico, em regra, não) [VALIDAR TRIBUTÁRIO] |
| "+800 parceiros", "+250 colaboradores" sem fonte confirmada | Só com fonte e data; número do site como "segundo o site da Save, <data>". |
| Estatística de mercado como dado próprio | Citar a fonte e a data. |

---

## 3. Regras regulatórias e jurídicas (referências a verificar)

| Tema | Regra / risco | Mitigação | Referência |
|---|---|---|---|
| **Intermediação de crédito (Bacen)** | Originar, estruturar e receber fee em crédito de instituição estrangeira pode ser visto como intermediação, que pode exigir autorização. Risco ALTO (J1) | Parecer antes do G2; contrato dizendo que a credora é a instituição estrangeira e a Save presta assessoria; comercial limitado à indicação | Lei 4.595/1964 (art. 17); Lei 7.492/1986; regras de correspondente (Res. CMN 4.935/2021) |
| **Registro do crédito externo (Bacen)** | Quem registra ou informa a operação (J2) | Definir no checklist do cliente | Lei 14.286/2021 e regulamentação do BCB |
| **Token / ativo virtual** | Estrutura "via token" pode ter regras de câmbio e de prestador de serviço de ativo virtual (J3). Risco ALTO | Fora de qualquer conversa até parecer | Lei 14.478/2022 e regulamentação do BCB |
| **CVM** | "Fundo internacional", "investidores", equity com recompra, token e Forma 2 podem configurar oferta de valor mobiliário ou fundo (J10). FIDC: cotas são valor mobiliário | Não usar "fundo" como nome; parecer antes de caso com equity; Save não distribui cotas | Lei 6.385/1976; Res. CVM 160/2022, 175/2022, 21/2021 |
| **Antecipação de recebíveis** | É operação de crédito, privativa de instituição autorizada (exceção: fomento mercantil com recursos próprios) | Save não se apresenta como quem antecipa; dizer quem opera | Lei 4.595/1964 |
| **Due diligence das instituições** | Risco de fraude no mercado (J4) | Registro no regulador (SEC/FINRA nos EUA; FINMA na Suíça), contrato ou mandato com a Save, ≥ 1 liberação documentada a empresa brasileira. Critério do G2 | K11 do Padrão |
| **PLD / KYC** | Origem das garantias e dos garantidores terceiros (J8). Se a Save é pessoa obrigada: em aberto | KYC de 100% dos clientes e garantidores; beneficiário final; garantidor que não se identifica = caso não segue | Lei 9.613/1998 |
| **Receita não formalizada** | Risco ALTO (J7) | Projeto só com números da contabilidade; recusar o caso se preciso; tratar com o dono e o Jurídico | Parecer pendente |
| **Garantia de terceiro** | Anuência, outorga do cônjuge, nulidade | Documentar anuência e KYC | Código Civil |
| **Troca de dívida e garantias** | Sequência segura: quitação → baixa → nova garantia (J12); dívida ativa pode presumir fraude na oneração | Checar CND e dívida ativa antes de oferecer garantia | CTN, art. 185 |
| **LGPD** | Uso da base de clientes para produto novo pede base legal (legítimo interesse) e opção de não receber. Envio de dados de sócios ao exterior = transferência internacional (J9). Dados coletados para o crédito não servem para vender outros serviços sem pedido | NDA com cláusula de finalidade e de transferência internacional; mínimo de dados; sem dado financeiro por WhatsApp | Lei 13.709/2018, arts. 6º (I e III), 7º e 33 |
| **CDC / oferta vinculante** | Promessa de taxa, prazo ou aprovação pode vincular (J6) | Material auditado; nada de condição por escrito antes do G2 | CDC, arts. 30 e 37 |
| **OAB** | Serviços jurídicos não podem ser anunciados junto com serviços financeiros ou tributários, nem por escritório parceiro. Divisão de honorários com não advogado é vedada se a contratante for sociedade de advogados (J5) | Serviços jurídicos só em peça própria do escritório que presta; remuneração do parceiro como indicação comercial por entidade não advocatícia; parecer | Lei 8.906/1994 (art. 1º §3º; art. 34); Provimento CFOAB 205/2021 (arts. 3º, 4º, 8º) |
| **Empresa contratante** | Qual empresa do grupo assina NDA e contrato (J11; MQ-Q18) | Definir antes do G2 | — |
| **Conflito de interesses** | Save dos dois lados (originador credor × usina devedora) | Participação do originador limitada ao crédito; nenhum serviço é condição para o crédito | CC, art. 422 |
| **Maquila · substância** | Estrutura sem gente e ativos reais pode ser requalificada | Operação real como condição do pacote | CTN, art. 116, parágrafo único |
| **Maquila · Paraguai** | Estrutura societária no exterior, comércio exterior, planejamento abusivo (J14); matriz do mesmo grupo na lei nova | Escalar ao técnico humano; agentes não analisam planejamento agressivo | Lei PY 7.547/2025 |

---

## 4. Regras tributárias (referências a verificar)

**Crédito Internacional**
- **IOF:** alíquota no ingresso de empréstimo externo acima de 364 dias (zero ou 0,38%) e efeito de estrutura "via token" (T1). Alíquotas mudaram em 2025. Decreto 6.306/2007; Decreto 12.499/2025. **Atualização de 22/10/2026:** até 364 dias de prazo médio, 3,5% (art. 15-B, XII); acima disso, o art. 15-B não traz alíquota específica e a regra residual de entrada é 0,38% (inferência) [VALIDAR TRIBUTÁRIO; pergunta J7].
- **IR retido na fonte sobre juros remetidos ao exterior:** em regra 15%; 25% se credor em país de tributação favorecida. Contratos costumam prever *gross-up* (o tomador paga o imposto e o custo sobe). A convenção Brasil–Suíça (Decreto 10.714/2021) pode reduzir a alíquota em certos casos (T2).
- **Variação cambial** no Lucro Real (caixa ou competência) (T3).
- **Tributação do fee** recebido pela Save e retenções sobre a remuneração do parceiro (T4).
- **Reforma tributária:** 2026 ano-teste (CBS 0,9%, IBS 0,1%); 2027 CBS plena e extinção de PIS/Cofins; IBS substitui ICMS e ISS de 2029 a 2032; extinção em 2033 (EC 132/2023; LC 214/2025) (T5).
- **Crédito tributário a recuperar como garantia:** fora, salvo parecer (T6).
- **Dedutibilidade** de juros, variação cambial e fee para o cliente (T7).
- **"RED" para exportador:** mecanismo a identificar (T8).
- Toda comparação de custo inclui câmbio, hedge, spread, fee e IR na fonte. Simulação para cliente só com aviso de que é ilustrativa e **não é recomendação de investimento**.

**Maquila**
- Lucro da controlada tributado no Brasil todo ano (Lei 12.973/2014, art. 77); crédito do imposto pago lá fora limitado (art. 87); crédito presumido de até 9% até 2029, com renda ativa própria ≥ 80% (arts. 87 §10 e 91).
- Controladora pessoa física: Lei 14.754/2023, art. 5º.
- Regime privilegiado / país de tributação favorecida: 1% e IRE de 10% ficam abaixo de 17% (Lei 9.430/1996, arts. 24 e 24-A). Hoje o Paraguai não está na IN RFB 1.037/2010. Todo estudo traz o cenário "Paraguai ou maquila listados".
- Preços de transferência na remuneração da maquiladora e na propriedade das máquinas (Lei 14.596/2023).
- Regra de origem Mercosul por NCM (Dec. CMC 05/23; Decreto 12.058/2024); regime especial do Paraguai até 60% de não originários, só nos REOs com asterisco, até 2038.
- Tratado de bitributação Brasil–Paraguai assinado em 2000, **não está em vigor**.
- Pilar 2 (Lei 15.079/2024) para grupos com receita ≥ €750 mi.
- Antidumping pode ser estendido ao produto montado no Paraguai (Decreto 8.058/2013).

---

## 5. Limites de promessa

- **Taxa:** nenhuma, nem faixa, nem "referência", antes da análise da instituição.
- **Prazo:** só "alguns meses" e "pelo menos cerca de 3 meses"; nunca prazo de aprovação.
- **Aprovação:** nunca. A decisão é sempre da instituição.
- **Liberação:** "na forma e no cronograma definidos pela instituição". Nunca "garantido".
- **Garantia:** "real, robusta, avaliada caso a caso". Garantias alternativas (contratos futuros, recebíveis de safra, VGV) sempre "a validar".
- **Custo:** fee de sucesso depois da liberação; custos ordinários do cliente, separados. Sem percentual.
- **Histórico:** o produto está em validação; não há operação liberada registrada.
- **Maquila:** nenhum percentual de ganho antes do estudo; caso público nunca vira referência da Save.
- **Ecossistema:** sem meta de receita de MVP antes do 1º recurso; estatística de mercado não é dado próprio.
- **Material externo:** só depois do G2, com aviso legal validado pelo Jurídico e zero alerta alto ou médio.

---

## 6. Remuneração do parceiro em produto novo

1. **Só depois da validação.** Remuneração de parceiro em produto MVP fica para depois do 1º recurso liberado (reunião de 13/10/2026). Nada é comunicado antes do G2 e do aditivo validado (Padrão, K08).
2. **CI (D61, aprovada em 06/10/2026):** não segue o repasse da recuperação tributária. Entrada como indicador com **10% sobre o valor líquido Save**; teto de **30%** pelo Programa de Crescimento do Parceiro (níveis N1 a N5; % intermediários 15/20/25 são hipótese; documento 24 v2.3, pendente de decisões L1 a L10 do Luis).
3. **Base:** valor efetivamente **recebido** pela Save (não o contratado). Valor líquido Save = o que a Save recebe depois da divisão com os demais participantes.
4. **Momento:** proporcional a cada parcela liberada e recebida. Não "na cabeça" do contrato.
5. **Estorno:** se o fee for devolvido ou cancelado, a fatia do parceiro é estornada.
6. **Extrato e contestação:** no ciclo da política de repasse (janela de 10 dias).
7. **Enquadramento:** "remuneração por indicação comercial", paga por entidade não advocatícia; nunca "divisão de honorários" [VALIDAR JURÍDICO; condição P13 do G2]. O nome não resolve: vale a substância.
8. **Registro de oportunidade:** pela raiz do CNPJ no HubSpot; validade proposta de 180 dias no CI, prorrogável enquanto houver etapa ativa com a instituição; Master dono da conta tem preferência.
9. **Fee padrão e divisão entre participantes:** por escrito do dono do produto antes de fixar valores (condição P15 do G2; CI-D3).
10. **MQ:** percentual a definir (MQ-Q4). Contas fora do roster: conta da casa no piloto, com preferência de 10 dias úteis ao parceiro de origem (D53, pendente).
11. **Originador com participação (ex.: trading no kit de 07/10):** participação definida em contrato próprio e limitada ao crédito. Se valesse para serviço jurídico, seria captação remunerada, vedada.
12. **Conta de receita:** sempre líquida da fatia do parceiro, em 3 colunas (contratado · conservador · realizado), rotulada como potencial (D16/D17).

## Exceção registrada (22/10/2026, decisão do Luis)
Só no one-page confidencial do cliente (`scripts/one_page_cliente.py`) é permitido:
- citar "taxas médias de referência de 7% a 10% ao ano, em moeda estrangeira, apenas como exemplo", sempre com a frase de que a taxa é definida pela instituição credora (o fundo) após a análise, sem câmbio, hedge, impostos e custos;
- citar a UBS como a instituição suíça.

**Confirmado em 22/10/2026 (D77 e D88):** o João confirmou a faixa de 7% a 10% como exemplo, e a UBS foi aprovada em ligação por vídeo. O one-page pode ser usado. A UBS também pode aparecer na proposta Canex. Em qualquer outro material, valem as regras acima.
