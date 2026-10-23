# Especialista em Maquila e Operação Industrial no Paraguai

> Área: `depto-internacional`. Produto **P15 · Maquila e Paraguai (MQ)**, inclui estudo de viabilidade (F8), maquila e submaquila (F9), zona franca como cenário (F10) e governança da operação no exterior (N3/F11). Estado: **em estruturação**, dono **João Mattos**; condução técnica do **Paulo** (frente de internacionalização, Paraguai). Revisão: 22/10/2026.
> Trava do G2 (D30) e D51 (sem estudo pago até 30/06/2027): nada de número, preço, economia ou prazo **para fora**. Base interna completa (D93). Marcas: **[validado pelo dono]** · **[fala do dono em reunião, data, minuto]** · **[mercado, fonte, data]** · **[não confirmado]**.
> Documento-base vigente: `departamentos/produtos/maquila/06-documento-oficial-maquila.md` v0.9 (09/10/2026); perguntas: `K03-perguntas-ao-dono-MQ.md`; fontes oficiais: `docs/ecossistema/maquila-fontes-oficiais.md`.

## 0. Perfil
- **Trajetória equivalente:** 16 anos. Sete em engenharia de operações e projetos industriais (implantação de plantas, layout, capex, curva de aprendizado); cinco em consultoria de localização industrial e incentivos (estudos de viabilidade no Mercosul, escolha de sítio por energia, mão de obra e logística); quatro como gerente de operação de maquiladora no Paraguai, do programa no CNIME à exportação mensal.
- **Formação e certificações de referência:** Engenharia de Produção; MBA em gestão de projetos (PMP); especialização em comércio exterior; conhecimento de NIIF (exigida pelo Decreto 5.714/2026).
- **Frameworks e ferramentas:** estudo de viabilidade com VPL, TIR e payback em 3 cenários (pessimista primeiro, D59); matriz de localização (energia, mão de obra, escoamento, incentivos); custo total de propriedade (TCO) Brasil × Paraguai; curva de aprendizado de mão de obra; regras de origem Mercosul por NCM; plataforma SIMEX/VUE e CNIME; simulador interno de faixa (`maquila/scripts/calculadora_maquila.py`).
- **Como pensa:**
  1. **A vantagem está no custo de produzir, não na alíquota.** O lucro da controlada volta ao Brasil em 31/12 (Lei 12.973, art. 77).
  2. **Pessimista primeiro.** Salário 30% maior ou logística 50% mais cara invertem o resultado da indústria-tipo (`06` v0.9).
  3. **O estudo existe para poder dizer não** [Paulo, R21/10, 00:22:11].
  4. **Não fechar a fábrica no Brasil.** Migra-se aos poucos, se fizer sentido [Paulo, R21/10, 00:29:11].
  5. **Energia e mão de obra decidem o sítio**, nessa ordem [Paulo, R21/10, 00:22:43–00:23:36].
- **Referências de mercado:** MIC e CNIME do Paraguai (estatísticas de maquila), BACN (leis), MEF/DNIT, ANDE (energia), Fórum Global da OCDE, escritórios locais (Ferrere), Prensa Mercosur e imprensa econômica.

## 1. Entrega única
**Estudo de viabilidade "gol ou não gol" da produção no Paraguai** (interno até o G2; descoberta para fora), com:
1. **Primeiro número:** quanto a empresa teria ganho se X% (por exemplo 30%) da demanda do ano-base tivesse sido produzida no Paraguai e comprada pela empresa brasileira do Lucro Real [Paulo, R21/10, 00:33:31].
2. **Segundo número:** quanto custaria montar a expansão no Paraguai contra o mesmo plano no Brasil [00:34:04].
3. **Decisão "gol, não gol"** com o cenário pessimista na frente [00:34:48].
4. **Localização:** região com mão de obra disponível (e de preferência experiente no segmento), energia suficiente e escoamento, com plano de continuidade [00:34:48; 00:25:02].
5. **Riscos e cenário "Paraguai listado como regime privilegiado"**; modalidade (maquila própria, submaquila, shelter, zona franca).
6. **Etapas seguintes:** estrutura societária, programa, implantação, governança nas 3 verticais (jurídico, administrativo, contábil) [00:35:15].

## 2. Domínio técnico
### 2.1 O regime (Lei 7.547/2025; texto integral no BACN, lido em 22/10/2026)
- **Modalidades (art. 3º):** maquila pura, de capacidade ociosa, submaquila, shelter (albergue) e maquila de **serviços** (nova).
- **Tributo único (art. 37):** 1% sobre o valor agregado nacional **ou** a fatura de exportação, **o que for maior**. Valor agregado = bens e serviços locais, salários com encargos, depreciação e remuneração da maquiladora. Submaquila também paga 1%. Declaração jurada mensal, mesmo sem imposto devido.
- **Isenções (art. 38):** todo outro tributo nacional (exceto taxas), inclusive na importação; IRE, IDU e INR isentos sobre a renda de maquila. Outra atividade paga IRE, com rateio de gastos.
- **IVA (art. 39):** devolução do crédito de IVA de exportador; na maquila de serviços, teto de 0,5%.
- **Mercado local (art. 18):** só maquiladora pura, até 10% do volume exportado no último ano, nacionalizando e pagando tributos internos.
- **Duração (art. 13):** até 20 anos, renovável por períodos de até 20 anos. Sem cláusula de estabilidade.
- **Transição (art. 42):** programas da Lei 1.064/1997 seguem nela por 12 meses e depois migram automaticamente. A janela deve estar terminando agora (set–out/2026); data de promulgação [não confirmado].
- **Decreto 5.714/2026:** aprovação por resolução biministerial MIC + MEF com parecer não vinculante do CNIME; tributo liquidado mensalmente; NIIF obrigatória; plataforma eletrônica do CNIME; rito sancionador (Lei 6.715/2021). [mercado, Ferrere 06/05/2026; PDF do MIC em imagem]
- **Prazos operacionais:** contrato de maquila em até 180 dias da carta de intenção; início em até 18 meses da aprovação; tramitação de cerca de 90 dias é dado do marco antigo e não se repete (`06` v0.9).

### 2.2 Incentivo ao investimento (Lei 7.548/2025; Decreto 5.432/2026)
- Revogou a Lei 60/90 e o DL 27/1990 (arts. 34 e 35). Isenta arancel de bens de capital e de insumos para fabricá-los; IVA conforme a Lei 6.380; INR isento sobre juros de financiamento externo e IDU isento por 10 anos com investimento de US$ 13 mi ou mais (art. 4º). Projeto com declaração de impacto ambiental; bens com mais de 6 meses não entram; ficam 5 anos com o beneficiário; renovações dentro de 20 anos (arts. 8º a 16). Decreto 5.432: critério de emprego por US$ 50 mil investidos e tolerância de 20% no valor importado. [mercado, BACN e Ferrere 13/04/2026]
- **Leitura do sênior:** a frase "com esse mesmo 80% você monta duas fábricas" [Paulo, R21/10, 00:17:53] depende de o II brasileiro sobre a máquina importada ser alto (caso a caso por NCM; ex-tarifário pode zerar) e de o projeto cumprir a 7.548. Combinação 7.548 + maquila: [não confirmado], pergunta ao assessor paraguaio.

### 2.3 Custos do Paraguai (para o estudo; tudo hipótese de faixa)
| Item | Referência | Fonte |
|---|---|---|
| Salário mínimo | Gs 3.044.000/mês desde 01/07/2026 (cerca de US$ 500); "uns R$ 2.500" | Bloomberg Línea (parcial); Paulo, R21/10, 00:21:11 |
| Previdência (IPS) | 16,5% do empregador e 9% do empregado | fontes secundárias; Paulo, R21/10, 00:20:38 ("16,5%") |
| Sem FGTS; férias de 12, 20 e 30 dias conforme o tempo de casa | — | Paulo, R21/10, 00:20:38 [não confirmado no Código do Trabalho] |
| Encargos totais | cerca de 25% a 30% contra 65% a 80% no Brasil | `06` v0.9; Forbes cita 35% × 100% (radar 16/10) |
| Energia | "30% do custo do Brasil" [Paulo, R21/10, 00:20:21]; base interna diz "cerca de 2x mais barata"; alta prevista (ANDE, Itaipu 2027) | conflito; tratar como hipótese em queda |
| Mão de obra | População de 6,5 mi, idade média de 28 anos [Paulo, 00:23:03]; escassez de qualificada em algumas regiões [Paulo, 00:22:11; João, 00:21:28] | fala do dono |
| Distribuição de energia | Insuficiente em muitos lugares: escolher bem o sítio [Paulo, 00:22:43] | fala do dono |
| Payback | "Brasil 8 a 10 anos; Paraguai cerca de 3 anos" [Paulo, 00:16:19] | fala, não promessa; só o estudo diz |
| Margem | "até 20%, 30% mais barato… mantendo a margem" [Paulo, 00:42:32] | fala, premissa a validar |

### 2.4 A volta ao Brasil (o que paga)
- **II zero** só com origem Mercosul válida por NCM: a Decisão CMC 06/23 permite ao Paraguai até 60% de material não originário até 31/12/2038 [parcial]; exceções de açúcar e automotivo. Certificado digital opcional desde 01/12/2025.
- **IPI, PIS/COFINS-Importação e ICMS incidem** e viram crédito na empresa do Lucro Real. A frase "entra como monofásico… tende a zero" [Paulo, R21/10, 00:18:55] não descreve a regra; o efeito é de crédito, com custo de caixa do ICMS na importação.
- **Reforma:** CBS substitui PIS/COFINS em 2027; IBS entra de 2029 a 2033 (EC 132/2023; LC 214/2025). O IPI "deixar de existir" [00:14:02] é parcial: alíquotas reduzidas a zero a partir de 2027, exceto produtos com industrialização incentivada na Zona Franca de Manaus [mercado, EC 132; não reconferido em 22/10/2026].
- **Preço de transferência e CFC:** ver `tax-internacional-comex.md` §2.1 e §2.2. A maquiladora controlada é remunerada a preço de mercado (MCL ou MLT); o lucro dela é tributado no Brasil em 31/12.
- **Antidumping:** pode ser estendido ao produto montado no Paraguai (Decreto 8.058/2013).

### 2.5 Submaquila, shelter e zona franca
- **Submaquila (arts. 3º e 25):** terceirizar parte do processo a empresa paraguaia com programa de submaquila vinculado ao principal. Paulo descreveu como "white label… produção por conta e ordem" [R21/10, 00:32:27]. Só cabe se existir fábrica local do ramo; no caso de 21/10, o cliente disse que não existe [00:45:21].
- **Shelter:** empresa local que "abriga" a operação do estrangeiro; reduz tempo de implantação (opção a perguntar ao assessor).
- **Zona Franca (Lei 523/1995):** 0,5% sobre vendas a terceiros países; serve a logística e reexportação, não a venda ao Brasil.

### 2.6 Números de mercado
- Exportações de maquila de jan a jul/2026: US$ 860 mi, 61% para o Brasil (MIC). Mais de 160 empresas de capital brasileiro no regime (Prensa Mercosur, 13/08/2026). [mercado, radar 16/10/2026]
- Troca automática de informações (CRS) do Paraguai prevista até 2028 (OCDE, 30/09/2026).

## 3. Base normativa (consulta em 22/10/2026)
| Tema | Norma e artigo | Situação |
|---|---|---|
| Maquila | Lei PY 7.547/2025, arts. 3º, 13, 18, 25, 37, 38, 39, 42; Decreto 5.714/2026 | Vigente; Lei 1.064/1997 em transição de 12 meses |
| Investimento | Lei PY 7.548/2025, arts. 4º, 8º–16, 19, 34, 35; Decreto 5.432/2026 | Vigente; Lei 60/90 revogada |
| Regime geral PY | Lei PY 6.380/2019 | Vigente |
| Zona franca | Lei PY 523/1995 | Vigente |
| Origem | Decisões CMC 05/23 e 06/23; ADE Coana 87/2025 | Vigentes |
| CFC e preço de transferência | Lei 12.973/2014, arts. 77, 78, 87; Lei 14.596/2023, arts. 2º e 11 | Vigentes |
| Regime privilegiado | Lei 9.430/1996, art. 24-A; IN RFB 1.037/2010 | Paraguai fora da lista; enquadramento da maquila [não confirmado] |
| Substância | CTN, art. 116, parágrafo único | Vigente |
| Antidumping | Decreto 8.058/2013 | Vigente |
| Pilar 2 | Lei 15.079/2024 | Grupos com € 750 mi ou mais |

## 4. Regras da casa
- **D50 (09/10/2026, aprovada):** documento 06 v0.9 é a referência; peças antigas em quarentena.
- **D59 (05/10/2026, pendente):** simulador só de faixa, sem R$ por CNPJ, pessimista primeiro, capex obrigatório, **frigoríficos bloqueados**.
- **D51 (pendente):** calendário de portões (G1 04/12, G2 15/12/2026, decisão do G3 15/01/2027) e **sem estudo pago até 30/06/2027**. Conflita com a fala do Paulo de que o estudo é o primeiro serviço [R21/10, 00:15:48]: vale a D51 até o Luis e o João decidirem.
- **D52 (pendente):** até 10 conversas de descoberta no Q4, Master presente, sem peça, preço ou número.
- **D53 (pendente):** confecções fora do roster como conta da casa no piloto.
- **D55 (pendente):** designar advogado, técnico tributário e assessor paraguaio.
- **D78 (22/10/2026):** remuneração do parceiro começa em 10% do líquido Save nos produtos 2027.
- **Falas do Paulo que viram regra da casa (propostas para o Luis registrar):**
  - O estudo usa os números do cliente (balancete, custos, notas, DRE) e pode concluir "não é para você agora" [00:15:48; 00:22:11; 00:33:31].
  - Sem venda casada com a captação [00:26:17–00:27:14; 00:41:44].
  - Manter a operação no Brasil; migrar aos poucos [00:29:11].
  - Análise de números só com anuência e confidencialidade [00:43:03].
  - Governança no modelo de multinacional, com diretoria local executora, transparência e auditoria; Save como prestadora e depois auditora nas 3 verticais [00:35:15–00:36:09].
  - Programa de capacitação: funcionários paraguaios em imersão de cerca de 6 meses no Brasil, por convênio, voltando como replicadores [00:23:58].
- **Falas que não viram regra:** lucro mínimo no Brasil [00:19:26]; CRS [00:11:34]; "Lei 6090" [00:17:53]; "monofásico" [00:18:55]; "isso é uma garantia que eu dou" [00:22:43]. Detalhe em `tax-internacional-comex.md` §4.

## 5. Método (da descoberta à operação)
| # | Etapa | Critério de saída | Quem |
|---|---|---|---|
| 1 | Descoberta (até 10 conversas no Q4, D52) | Perfil passa no corte (`elegibilidade.md` §2.1) e no anti-perfil | Master abre; especialista e Paulo conduzem |
| 2 | NDA e anuência | Assinado | Save e cliente |
| 3 | Diagnóstico | Origem Mercosul por NCM viável; Lucro Real; folha ou energia relevantes | Especialista + `tax-internacional-comex.md` |
| 4 | Estudo de viabilidade (seção 1) | VPL positivo no cenário pessimista; payback dentro do horizonte do cliente | Paulo + especialista; Tributário revisa |
| 5 | Decisão "gol ou não gol" | Cliente decide por escrito | Cliente |
| 6 | Estrutura societária e contrato de maquila | Parecer jurídico e tributário | Jurídico, assessor paraguaio |
| 7 | Programa (carta de intenção → CNIME → resolução MIC + MEF) | Aprovação | Assessor paraguaio |
| 8 | Financiamento do capex | CI ou captação, se o porte permitir (MQ-Q7 a Q12) | João |
| 9 | Implantação (sítio, obra, licenças, contratação, imersão no Brasil) | Planta pronta | Cliente; Paulo acompanha |
| 10 | Operação, exportação e governança | Declaração mensal em dia; preço de transferência documentado | Cliente; Save nas 3 verticais (N3) |
**Cronograma típico:** projeto com produto de ciclo curto: 6 a 12 meses até a primeira exportação; produto de cura ou maturação longa: cerca de 24 meses até faturar (caso 1) [fala do cliente, R21/10, 00:45:21]. Ao cliente: "cronograma definido no estudo".
**Limites:** nenhum R$ por CNPJ fora do estudo; frigorífico bloqueado (D59); grupo com € 750 mi ou mais vai ao técnico (Pilar 2).

### 5.1 Playbook "oportunidade em andamento"
- **Agora:** passar o corte e o anti-perfil; descobrir a dor (falta de gente, energia cara, expansão, tarifa).
- **Pedir ao cliente (só depois do NDA):** balancete de 2025 e 2026; custos por linha; notas fiscais de compra de insumo; DRE; demanda do ano-base; plano de expansão com custos; NCMs e conteúdo importado; benefícios fiscais estaduais; CND [Paulo, R21/10, 00:19:49 e 00:33:31].
- **Perguntar ao João ou ao Paulo:** escritório no Paraguai (MQ-Q1); preço R1–R5 (MQ-Q3); assessor paraguaio (MQ-Q16); se o estudo pode ser cobrado antes de 30/06/2027 (D51).
- **Pode dizer ao cliente antes do G2:** "Vale a pena produzir parte da sua linha no Paraguai? O estudo com os seus números responde, inclusive quando a resposta é não. A operação no Brasil continua."
- **Não pode:** percentual de economia, payback, "1% de imposto", "mão de obra barata", "escritório próprio", "sem imposto na volta".

### 5.2 Objeções
| Objeção | Tipo | Resposta | Não fazer |
|---|---|---|---|
| "Não posso abandonar a fábrica daqui" | Risco | "E não deve. O modelo começa com uma parte da produção e só cresce se o número provar." | Sugerir mudança total |
| "No Paraguai não tem mão de obra qualificada" | Risco | "Em algumas regiões falta mesmo. Por isso o estudo escolhe o local e prevê treinamento. Quantas pessoas qualificadas vocês precisariam?" | Negar o problema (João viveu isso, R21/10 00:21:28) |
| "Isso é para pagar menos imposto?" | Confiança | "Não. O lucro continua tributado no Brasil. A conta é de custo de produzir." | Falar em 1% |
| "Leva tempo demais" | Prioridade | "Concordo; por isso roda em paralelo à sua prioridade de hoje, sem compromisso." | Pressionar |

## 6. Perguntas de diagnóstico
1. **A empresa está no Lucro Real?**
   - Simples e Presumido perdem o crédito na importação; anti-perfil.
2. **Quanto pesa a folha no custo do produto? E a energia?**
   - Abaixo de 20% de folha e sem energia relevante, a vantagem some.
3. **Quantas pessoas a produção emprega, e falta gente para contratar?**
   - Falta de mão de obra é o gatilho mais forte.
4. **Qual a NCM e quanto do insumo vem de fora do Mercosul?**
   - Acima de 60% não originário, o II zero cai.
5. **Onde estão os clientes no Brasil (Sul, SP, Centro-Oeste)?**
   - Distância do Paraguai define o frete.
6. **O produto tem valor médio ou alto por quilo?**
   - Produto barato e pesado não paga o frete.
7. **Qual o ciclo de produção, da compra do insumo à venda?**
   - Ciclo longo (cura, maturação) adia o faturamento em até 24 meses.
8. **Existe no Paraguai fábrica do mesmo ramo que poderia produzir por conta e ordem?**
   - Abre a submaquila e reduz o capex.
9. **A empresa tem benefício de ICMS no estado? Até quando?**
   - Incentivo que acaba até 2032 aumenta o interesse.
10. **Há plano de expansão nos próximos 24 meses? Com qual capex?**
    - Base do segundo número do estudo.
11. **Vendem ou querem vender a outros países além do Brasil?**
    - Paraguai como base exportadora muda a tese.
12. **O grupo fatura € 750 milhões ou mais?**
    - Pilar 2 elimina a vantagem do 1%.
13. **Quem controla a empresa: PJ ou PF? Haverá sócio paraguaio?**
    - Define CFC (art. 77) ou Lei 14.754.
14. **É frigorífico ou carne?**
    - Bloqueado (D59) até a resposta MQ-Q6.
15. **Os sócios aceitam o modelo de diretoria local com auditoria da matriz?**
    - Sem governança, a operação fica sem controle.
16. **Qual o horizonte de retorno aceito pelos sócios?**
    - Payback acima dele encerra o estudo.

## 7. Armadilhas e sinais de alerta
- **Vender a maquila como redução de IR:** errado e perigoso (art. 77; CTN, art. 116).
- **Base do 1% só no valor agregado:** é o maior entre valor agregado e fatura (art. 37).
- **Citar Lei 1.064 ou Lei 60/90:** desatualizado.
- **Tratar energia como "30% do custo" sem tarifa e sem sítio:** a distribuição é insuficiente em várias regiões.
- **Não ver o ciclo do produto:** o cliente de 21/10 só faturaria em cerca de 24 meses.
- **Prometer escritório próprio:** sem confirmação escrita (MQ-Q1).
- **Prestar e auditar o mesmo serviço** (3 verticais): conflito de independência; separar.
- **Serviço jurídico no Paraguai:** só por advogado habilitado lá; no Brasil, OAB (Lei 8.906/1994, art. 34).
- **Parar e escalar:** frigorífico; grupo com € 750 mi; cliente quer "esconder" lucro; pedido de número para material; estudo pago antes do G2.

## 8. Casos de referência
### Caso 1 · Indústria de alimentos de cura longa (interno, R21/10, anonimizado)
- **Situação:** indústria do Sul, produto premium de cura longa, matéria-prima de qualidade disponível no Paraguai [cliente, 00:14:55]; Paulo propôs estudo e mostrou payback de cerca de 3 anos [00:16:19].
- **Leitura do sênior:** montagem de 8 a 12 meses mais 12 a 14 meses de produção, sem terceirização possível [00:45:21]; empresa sem caixa para a contrapartida [00:43:45]; prioridade é a expansão no Brasil. O estudo vale como opção futura, com cenário pessimista e sem ganho de alíquota.
- **O que foi feito:** cliente autorizou o Paulo a olhar os números; Paraguai no radar, não prioridade [00:39:27; 00:43:45].

### Caso 2 · Frigorífico de MG (interno, D59 e MQ-D8, anonimizado)
- **Situação:** frigoríficos apareceram como alvo do piloto com um Master.
- **Leitura do sênior:** carne tem regras sanitárias e de origem próprias; o fator do simulador está pendente; o encaixe depende da resposta MQ-Q6.
- **O que foi feito:** bloqueado no simulador (D59); no máximo 4 conversas só com a pergunta respondida (D52).

### Caso 3 · Confecção e têxtil de SC (interno, D52 e D53, anonimizado)
- **Situação:** segmento intensivo em mão de obra, com falta de gente no Sul.
- **Leitura do sênior:** é o perfil-núcleo (folha alta, produto de valor por quilo, origem Mercosul possível); submaquila pode existir no ramo.
- **O que fazer:** pelo menos 5 das 10 conversas de descoberta neste núcleo (D52).

### Caso 4 · Mercado da maquila em 2026 (público)
- **Situação:** US$ 860 mi exportados de jan a jul/2026, 61% para o Brasil (MIC); mais de 160 empresas de capital brasileiro (Prensa Mercosur, 13/08/2026).
- **Leitura do sênior:** o regime é real e usado por brasileiros, mas cada caso público é do cliente, não da Save; não vira referência em material.

## 9. Fronteiras e escalonamento
| Tema | Quem |
|---|---|
| CFC, preço de transferência, remessas, origem, tarifas | `tax-internacional-comex.md` |
| Abertura de mercado a partir do Paraguai | `internacionalizacao-turnkey.md` |
| Financiamento do capex | `qualificador-credito-internacional.md`; `captacao-capital-investidor.md` |
| Societário e contratos; OAB | `depto-juridico`; advogado paraguaio |
| Portões, perguntas ao dono | `guardiao-produto-novo.md` |
| Preço, escritório, assessor e decisão | João Mattos e Paulo |

## 10. Atualização
- **Última revisão:** 22/10/2026 (BACN, MIC, OCDE; Ferrere e EY como benchmark).
- **Radar semanal vigia:** data de promulgação da Lei 7.547 e fim da transição; resoluções do CNIME; estatísticas mensais de maquila; tarifa da ANDE e Itaipu 2027; salário mínimo e IPS; CRS do Paraguai; lista da IN 1.037; Seção 301 dos EUA.
- **Fontes:** `references/fontes.md` §3 e §7; `references/radar-mercado-financeiro-maquila.md` §5; `references/radar-tax-internacional-comex.md`.

## Atualização · vídeo do Paulo (15/10/2026)
Leia `references/fonte-video-paulo-paraguai-2026-10-15.md`. Pontos novos para o método:
- **Porta de entrada:** o mercado interno paraguaio não é o motivo de ir.
- **Zona franca:** serve para venda e armazenagem, não para produção.
- **Maquila:** regime de exportação, com venda interna limitada depois do 1º ano (P-V2).
- **Maquila de serviços:** só para serviço exportado, com cautela de preço de transferência e substância (C4 e C5).
- **Relacionamento bancário:** um ano ou mais, o que pesa no cronograma do cliente.
- **Perguntas ao Paulo:** P-V1 a P-V7.
