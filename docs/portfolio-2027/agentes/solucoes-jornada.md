# Jornada completa 2027 · desenho do Gerente de Contas e Soluções

> **22/10/2026 · `depto-solucoes` · rascunho para o Luis, sem aprovação de nenhuma área.** Interno. Não é oferta, preço, taxa, prazo ou promessa. Sem nome de cliente (`<EMPRESA>`). Estado dos produtos vale o de 19/10/2026 (Luis).
> **Marcas:** `[HIPÓTESE]` proposta minha, sem dono · `[VALIDAR JURÍDICO]` / `[VALIDAR TRIBUTÁRIO]` não sai desta pasta sem o humano · `[FONTE]` aponta o documento de origem. Sem marca = veio de `handoff-ecossistema-save.md`, `ecossistema-produtos-servicos.md`, `esteira.md`, `caracteristicas-*.md` ou `fichas-sem-reuniao.md`.
> **Estrutura:** 1 mapa da jornada v2 · 2 conexões entre produtos · 3 gatilhos ligados ao `mapa_conta` · 4 jornadas-tipo · 5 camada contínua · 6 papéis e rota de agentes · 7 lacunas e perguntas ao Luis · 8 registro de revisão.

---

## 0. Regras que governam tudo (resumo, para ler antes das tabelas)

1. **Três verbos:** Destravar caixa → Proteger e controlar → Crescer, mais a **camada contínua**. Os nomes antigos (Oxigenar, Estruturar, Escalar) valem só em documento interno.
2. **Passivo antes do crédito novo.** Débito bloqueia certidão; sem certidão não há funding nem FIDC.
3. **O crédito recuperado, quando efetivado, é a primeira entrada de caixa nova** e abre a conversa da etapa seguinte.
4. **No máximo 2 produtos novos por vez, por cliente** (definição operacional na seção 2.4).
5. **Produto em validação entra só como descoberta**, com a data do portão. Hoje: Crédito Internacional (CI), captação de capital (CAP), Maquila (MQ), estudo de viabilidade no Paraguai (EV-PY), governança no exterior (GEX) e internacionalização turnkey (INT), todos conduzidos pelo João Mattos. **G2 em 15/12/2026; decisão do G3 em 15/01/2027.** Antes do G2: sem taxa, prazo, fee, nome de instituição nem peça.
6. **A Save estrutura e indica. Nunca é credora, nunca antecipa, nunca distribui cotas** (CVM).
7. **Sem venda casada:** cada produto é contratado em separado. Estudo antes de proposta. O "não é agora" faz parte do produto.
8. **O parceiro é o dono da relação.** O produto novo do mesmo cliente segue o parceiro de origem; conflito de canal é do `depto-operacoes-canal`.
9. **Fora de escopo por decisão do Luis:** certificado digital e ART, home equity, programa de formalização. Aparecem só onde uma regra de outro produto depende deles (nota cheia para o FIDC, por exemplo), marcados como "fora".

---

## 1. Mapa da jornada v2

### 1.1 Códigos usados neste documento
Para não confundir o P01/P02 do catálogo tributário com o P1 a P17 do ecossistema v1.0, aqui valem só estes códigos:

| Código | O que é | Origem |
|---|---|---|
| **T01 a T19** | Teses de recuperação (T18 e T19: crédito presumido de PF e Funrural) | `caracteristicas-teses.md` |
| **REC** | Recorrência (novas competências de tese já executada) | ecossistema P2 |
| **P01 / P02** | Planejamento tributário e reforma / Planejamento estratégico | catálogo de base |
| **F1 a F23** | As 23 fichas de `fichas-sem-reuniao.md` (F1 Gestão de Contas … F23 Energia e carbono; F9 é a estruturação patrimonial; F16 é o FIDC; F19 é a preparação para investidor, que inclui o dossiê/kit de análise) | fichas |
| **CI** | Crédito Internacional (funding de dívida em moeda forte) | ecossistema P12 |
| **CAP** | Captação de capital: sócio, cotas, investidor | ecossistema P16, reunião de 24/09 |
| **MQ** | Maquila no Paraguai (inclui submaquila, selo de origem e o incentivo à importação de bens de capital como parte do mesmo estudo; Zona Franca e regime geral são alternativas comparadas no estudo) | R2 |
| **EV-PY** | Estudo de viabilidade de operação no Paraguai (primeiro serviço, independente de captação) | R2 §4 |
| **GEX** | Governança de operação no exterior (jurídico, administrativo, contábil; inclui o programa de capacitação de mão de obra como módulo) | N3 da matriz |
| **INT** | Internacionalização turnkey (abertura de mercado) | ecossistema P17 |
| **TI** | Tax internacional e comércio exterior (preço de transferência, não bitributação, DCBE) | ecossistema P18 |

### 1.2 Catálogo completo por etapa, estado e porta de entrada
**Portas:** M = média · G = grande · C = em crescimento (definições na seção 1.3). **Estado:** pronto · validação (só descoberta até o G2) · candidato (ficha em rascunho, sem dono ou sem decisão de próprio × parceiro) · definição.

#### Etapa 1 · Destravar caixa (janela 0 a 6 meses)
| Cód. | Produto | Estado | Portas | Dono humano | Observação de ordem |
|---|---|---|---|---|---|
| T01 | PIS/COFINS nas aquisições com alíquota zero (revenda) | pronto | M G | Time técnico | Caminho: pedido de ressarcimento (PER), não compensação; risco da tese registrado; fora supermercado e café |
| T02 | PIS/COFINS sobre insumos | pronto | M G | Time técnico | Real; exportador e indústria |
| T03 / T04 | ICMS e ICMS-ST fora da base do PIS/COFINS | pronto | M G | Time técnico | Via administrativa: caixa mais rápido |
| T08 / T09 | Conta gráfica de PIS/COFINS; gross up | pronto | G (M se Real) | Time técnico | **T08 tem urgência de 2027** (preservar saldo antes da CBS) |
| T10 / T11 | IPI nas aquisições de atacadista; IPI em conta gráfica | pronto | M G | Time técnico | Só indústria no Real |
| T12 | CPP: verbas indenizatórias | pronto | M G | Time técnico | Folha representativa; liga com F14 |
| T13 | Teto do Sistema S | pronto | M G | Time técnico | Só quem se enquadra na modulação |
| T05 / T06 / T07 | PIS/COFINS fora da própria base; ICMS na base do crédito; ISS fora da base | pronto | M G | Time técnico | **Via judicial: caixa mais lento**; entram depois das administrativas |
| T14 / T15 / T16 / T17 | Crédito presumido de ICMS (IRPJ/CSLL e PIS/COFINS); PIS/COFINS fora do IRPJ/CSLL (Presumido); ACT/CCT | pronto | M G | Time técnico | Judicial; T14 e T15 só com benefício estadual documentado |
| T18 / T19 | Crédito presumido de compras de PF; Funrural | pronto | M G | Time técnico | Agroindústria e cooperativa; Funrural: preço e consulta pendentes do Luis |
| REC | Recorrência | pronto | M G | Time técnico | Reabre a etapa 1 com 12 ou mais competências novas |
| F1 | Gestão de Contas (cobrança por IA, escrow, acesso ao e-CAC) | pronto | **M (porta)** G | Save Invest (Júnior) | Porta de confiança; abre DRE, SCR e e-CAC |
| F2 | Antecipação de recebíveis (instituição autorizada) | pronto | M G | Save Invest | Vendida como parte da F1; ver conflito de etapa na seção 7 (item 4) |
| F3 | Monetização de ICMS acumulado | candidato `[HIPÓTESE]` | G | A definir | Depende de regra estadual; só se T08/T11 e ICMS acumulado coexistirem |
| F4 | Precatórios (antecipar ou usar na compensação) | candidato `[HIPÓTESE]` | G | A definir | Risco reputacional alto; **não entra no roteiro padrão** |
| F5 | Seguro garantia para liberar depósito judicial e garantir dívida fiscal | candidato | G (M com execução) | Jurídico + corretora parceira | Save não é corretora sem habilitação `[VALIDAR JURÍDICO]` |

#### Etapa 2 · Proteger e controlar (janela 3 a 18 meses)
| Cód. | Produto | Estado | Portas | Dono humano | Observação de ordem |
|---|---|---|---|---|---|
| F6 | Gestão de Passivo e transação tributária | pronto | M G | Time jurídico | **Precede toda etapa 3**; o crédito recuperado abate o débito |
| F8 | Produtos jurídicos (defesa, intimação, ação) | pronto | M G | Time jurídico | Camada de segurança de toda a esteira |
| P01 | Planejamento tributário e reforma | pronto | M G | Time técnico | CBS plena em 2027; IBS em transição |
| F10 | Programa de preparação para a reforma (CBS, IBS, split payment) | candidato `[HIPÓTESE]` | M G | Time técnico | Projeto de caixa e crédito em 2027; pode ser módulo do P01 |
| F7 | Passivo bancário, alongamento, carência, reestruturação e recuperação extrajudicial | definição | M G | A definir | Sem dono nem ficha de elegibilidade; extrajudicial é caso de advogado |
| F9 | Estruturação patrimonial e empresarial (dizer assim, nunca "holding") | pronto | G (M com patrimônio) | Time jurídico | Gera a garantia real que o CI e o F16 pedem |
| F12 | Sucessão e governança familiar | candidato | G M | Jurídico + parceiro | Integra F9; parceiro especializado |
| F11 | CFO terceirizado e controladoria | candidato | M G C | A definir | Dado confiável é requisito de CI, CAP, F16 e F20 |
| F13 | Compliance, integridade e LGPD | candidato | G C | Jurídico | Requisito de investidor, fundo e M&A |
| F14 | Passivo trabalhista e folha | candidato | M G | Parceiro trabalhista | Save só estrutura |
| F15 | Gestão de riscos: seguros e hedge | candidato | G | Internacional + corretora | Hedge obrigatório na conversa de CI e F21 |
| P02 | Planejamento estratégico | pronto | C M | Time técnico | Metas e plano; insumo do F19 |
| TI | Tax internacional e comércio exterior | pronto | G | Paulo e João Mattos | Para quem já opera fora; também precede MQ e INT |

#### Etapa 3 · Crescer (janela 6 a 24 meses e além)
| Cód. | Produto | Estado | Portas | Dono humano | Observação de ordem |
|---|---|---|---|---|---|
| F19 | Preparação para investidor (plano, projeção, dossiê/kit de análise) | candidato | **C (porta)** G | A definir | **Ponte da etapa 2 para a 3**; pré-requisito de CI, CAP e F20; honorário separado do funding |
| F16 | FIDC e FIDC multicedente/multissacado | pronto | G | Save Invest | Piso de cerca de R$ 10 mi/mês de faturamento; só com nota; multicedente a aprofundar |
| CI | Crédito Internacional (funding) | validação, G2 | G | João Mattos | Descoberta; garantia real; critério v2.3 × 13/10 em aberto |
| CAP | Captação de capital (sócio, cotas, investidor) | validação | C G | João Mattos | Descoberta; valor mobiliário: Jurídico antes de qualquer conversa |
| EV-PY | Estudo de viabilidade no Paraguai | validação | G C | João Mattos | Descoberta; sem estudo pago até 30/06/2027 |
| MQ | Maquila no Paraguai | validação | G | João Mattos | Descoberta; frigorífico bloqueado (D59) |
| GEX | Governança de operação no exterior | validação | G | João Mattos | Só após MQ ou operação instalada |
| INT | Internacionalização turnkey | validação | G C | João Mattos | **Segunda rodada**; rede de representantes a confirmar |
| F17 | CPR e CRA para o agro | candidato | G | Internacional (Café e Agro) | Quem emite e distribui: em aberto |
| F18 | Sale-leaseback | candidato | G | Tributário + Jurídico | Gasta o ativo que serviria de garantia ao CI; ver 2.2 |
| F20 | M&A | candidato | G C | Parceiro de M&A | Via parceiro (sugestão do handoff) |
| F21 | Financiamento à exportação (ACC, ACE, seguro de crédito) | candidato | G | Internacional | Instrumentos de instituição; a Save conecta |
| F22 | Subvenções e incentivos à inovação | candidato | G C | Tributário (Incentivos) | Também alimenta T14/T15 ao contrário (benefício estadual) |
| F23 | Energia e créditos de carbono | candidato | G | Internacional (Café e Agro) | Uso do capital; retorno estimado nunca vai ao cliente |

#### Camada contínua (sempre)
| Cód. | Componente | Estado | Dono |
|---|---|---|---|
| CC1 | Revisão tributária anual | pronto na prática, formalizar `[HIPÓTESE]` | Time técnico + `depto-solucoes` |
| CC2 | Painel DRE × SCR × e-CAC | a construir | `depto-dados` + `depto-resultados` |
| CC3 | Consultor no conselho do cliente (rito trimestral, Mapa de Valor) | modelo proposto | Gestor de esteira |

### 1.3 As três portas de entrada
| Porta | Perfil (critério do Luis) | Primeiro passo | O que o cliente dá em troca | Etapa 1 típica | Para onde vai |
|---|---|---|---|---|---|
| **Média** | Até cerca de R$ 10 mi/mês, sem grandes garantias | Gestão de Contas **ou** diagnóstico tributário (a dor decide) | Confiança, e-CAC, depois DRE, balanço e SCR | F1 + T-teses administrativas, REC | Etapa 2 inteira; etapa 3 só se mudar de porte ou ganhar garantia |
| **Grande** | Acima de R$ 10 mi/mês ou garantias acima de cerca de R$ 60 mi | Diagnóstico 360 `[HIPÓTESE]`: tributário + estrutura patrimonial + leitura do SCR, em paralelo (a porta clássica era "estruturação patrimonial, FIDC e funding" direto) | Balanço, ativos, matrícula, plano de expansão | T01/T02/T08/T11 e F2; depois F6 se houver débito | Etapa 3 mais cedo; ainda assim com passivo e certidão em ordem |
| **Em crescimento** | Demanda acima da capacidade, EBITDA negativo por investimento (caso da indústria de alimentos, cerca de R$ 8 mi/ano) | F19 (preparação para investidor) | Plano, projeção, destino do recurso | Só o que o regime permitir; caixa de tese é bônus, não requisito | CAP → CI se o ticket couber → INT na 2ª rodada |

**Subfaixa da porta média `[HIPÓTESE]`:** o `mapa_conta.py` usa R$ 4,8 mi/ano como corte de entrada (Gestão de Contas, antecipação, planejamento), e a porta média do Luis vai até cerca de R$ 120 mi/ano (R$ 10 mi/mês). Proponho **média-baixa (R$ 4,8 a 30 mi/ano)** e **média-alta (R$ 30 a 120 mi/ano)**. A média-alta é onde F2 e a descoberta de F16/CI começam a fazer sentido. Pedir validação do Luis (item 8 da seção 7).

### 1.4 Mapa resumido: etapa × porta (sequência recomendada)
| Etapa | Média | Grande | Em crescimento |
|---|---|---|---|
| **1 · Destravar caixa** | F1 → T administrativas (T01, T02, T03/T04, T10/T11, T12) → REC → F2 | T08/T11 (urgência 2027), T01/T02 → T judiciais → F2 → F3 (se couber) | P02 + F19 em 90 dias; tese só se Real e com crédito evidente |
| **Ponte (1→2)** | Dinheiro entrou e há dados: DRE, balanço, SCR | Idem, mais matrícula dos ativos | Plano e projeção prontos |
| **2 · Proteger e controlar** | F6 (se houver débito) → P01/F10 → F8 → F11 | F6 → F9 → P01/F10 → F12 → F13 → TI; F15 se houver câmbio | F11 (dado confiável) → F13 (exigência de investidor) |
| **Ponte (2→3)** | CND ou CPEN, passivo tratado | Idem, 2 anos de demonstrações, garantia livre | Dossiê auditável (F19 fechado) |
| **3 · Crescer** | Só se virar porte: F16 (≥ ~R$ 10 mi/mês) | F16 e/ou CI (descoberta) → F17/F21/F23 conforme setor → EV-PY → MQ → GEX → INT → F20 | CAP (ou CI) → INT na 2ª rodada |
| **Contínua** | CC1 + CC2 + CC3 | CC1 + CC2 + CC3 | CC1 + CC2 + CC3 |

---

## 2. Matriz de conexões produto → produto

### 2.1 Conexões que amarram (o que destrava o quê)
Tipos: **DESTRAVA** (A dá condição a B) · **LASTRO** (A vira garantia ou lastro de B) · **PRÉ-REQ** (B exige A) · **TRAVA** (A em aberto bloqueia B) · **EXCLUI** (A e B não andam juntos) · **REFORÇA** (ganho, sem ser requisito) · **CONFLITO** (restrição jurídica ou de independência).

| De | Para | Tipo | Condição e porquê |
|---|---|---|---|
| T01, T02, T08, T11, T18 (crédito acumulado) | F1, F2 | LASTRO | Crédito a compensar ou ressarcir vira caixa e lastro |
| Etapa 1 (qualquer tese) | F6 | DESTRAVA | O crédito recuperado abate o débito (compensação) |
| F1 (Gestão de Contas) | T (diagnóstico), F2, F11, CC2 | DESTRAVA | Acesso ao e-CAC e aos dados; a confiança abre o diagnóstico |
| F1 | F16 | DESTRAVA | Carteira organizada e histórico de pagamento são a base do FIDC |
| F2 (antecipação) | F16 | DESTRAVA | Evolução natural: de antecipar a ter o próprio fundo |
| F6 (passivo resolvido, certidão) | CI, F16, F5, F2 | PRÉ-REQ | Sem certidão não há funding; débito em aberto é trava |
| F6 | F5 | REFORÇA | Seguro garantia é a modalidade (iii) da transação (a confirmar `[VALIDAR JURÍDICO]`) |
| F5 (depósito liberado) | T judiciais, F6 | REFORÇA | Caixa liberado financia a defesa e a transação |
| T08, T11 | P01, F10 | DESTRAVA | Saldo credor só preserva se tratado antes da CBS (urgência de 2027) |
| P01 / F10 | F16 | DESTRAVA | FIDC só aceita título com nota; o planejamento viabiliza nota cheia (a formalização em si está fora do escopo por ora) |
| F10 | F2, F16 | REFORÇA | O split payment muda o capital de giro; o programa antecipa o efeito |
| T14, T15 (benefício estadual) | F22, P01 | REFORÇA | Incentivo fiscal e subvenção compartilham a base documental |
| T12, T13, T19 | F14, P01 | REFORÇA | Previdência e Funrural puxam folha e planejamento ampliado |
| T05–T07, T14–T18 (judicial recorrente) | F8 | DESTRAVA | Judicial precisa de acompanhamento contratado |
| F9 (estruturação) | CI | LASTRO | Garantia real livre (cerca de 2x no critério v2.3) |
| F9 | F12, F16, MQ | REFORÇA | Sucessão, estrutura de grupo, societário da operação externa |
| F11 (CFO) | CI, CAP, F16, F20 | PRÉ-REQ | Dado confiável e controle são exigência do financiador |
| F13 (compliance e LGPD) | CAP, F20, CI | PRÉ-REQ `[HIPÓTESE]` | Investidor e comprador pedem integridade; reduz risco do funding |
| F19 (plano, projeção, dossiê) | CI, CAP, F20 | **PRÉ-REQ** | O financiador exige plano com destino do recurso, dossiê e contabilidade auditada |
| F19 | MQ, EV-PY | REFORÇA | Plano de expansão com custos é insumo do estudo |
| P02 (planejamento estratégico) | F19 | REFORÇA | Metas e plano de crescimento alimentam o plano de negócio |
| CI ou CAP (recurso entrou) | F1 (escrow), F11, GEX | DESTRAVA | O fundo pede controle do uso: escrow, gestão de contas, controladoria |
| CI ou CAP | F15 | PRÉ-REQ | Dívida indexada em dólar: hedge entra na conversa |
| CI | F16 | REFORÇA | Funding pode estruturar o FIDC (uso previsto em ecossistema) |
| CI | F7 | REFORÇA | Trocar dívida cara é a tese mais forte do CI; F7 é a leitura do passivo bancário antes |
| CAP | CI | EXCLUI parcial | Equity × dívida: são alternativas comparadas (diluição × taxa); **não ofertar as duas na mesma rodada** `[HIPÓTESE]` |
| EV-PY | MQ | PRÉ-REQ | Estudo antes de proposta; pode concluir que "não é agora" |
| MQ | TI | PRÉ-REQ | Preço de transferência, não bitributação, DCBE |
| MQ | GEX | DESTRAVA | Operação instalada precisa de governança local |
| MQ (importação) | F2 | DESTRAVA | ICMS na importação puxa antecipação |
| MQ | F9 | REFORÇA | Societário da operação externa |
| MQ | CAP, CI | REFORÇA | Planta no exterior pode ser financiada em segunda fase (investidor, funding) |
| MQ ou INT | F21, F15 | REFORÇA | Exportação traz ACC/ACE e hedge |
| MQ | INT | **TRAVA** | Primeiro capacidade e caixa; só depois mercado externo (ordem recomendada na reunião) |
| F16 (FIDC na Save) | T (recuperação com terceiros) | REFORÇA a retenção | Cliente com FIDC na Save tende a não cotar recuperação fora; é recorrência, não cláusula |
| F17 (CPR/CRA) | F16, CI | REFORÇA | Instrumentos do agro; produtor como cedente ou cotista mezanino |
| F23 (energia) | CI | REFORÇA | Uso do capital; retorno estimado nunca vai ao cliente |
| Qualquer venda | CC1, CC2, CC3 | DESTRAVA | Revisão anual e painel apontam o produto seguinte |

### 2.2 Travas, exclusões e conflitos
| Regra | Entre | Efeito | Fonte |
|---|---|---|---|
| Passivo antes de crédito novo | F6 × CI, F16, F2 | Débito aberto bloqueia a etapa 3 | `esteira.md` |
| Escrow **não** é blindagem | F1 × F6, F8 | Não vender escrow como proteção contra bloqueio judicial; prática sinalizada, só dentro da lei `[VALIDAR JURÍDICO]` | ecossistema |
| Antecipação sobre venda gerencial (sem nota) | F2, F16 | Prática sinalizada; FIDC só aceita título com nota | ecossistema |
| Sale-leaseback consome o ativo | F18 × CI, F9 | Perde-se a garantia real; decidir **antes** se o ativo vai para garantia ou para venda | F18 |
| Frigorífico bloqueado | MQ, EV-PY | D59; não oferecer | `produtos.md` |
| Supermercado e café fora da alíquota zero | T01 | Perfil incompatível; não segue em T01 | `caracteristicas-teses.md` |
| Cliente sem Lucro Real | T02, T08, T10, T11, T17, T18, MQ | Aderência cai ou zera; conferir regime antes | catálogo |
| Administrador/gestor de FIDC não pode ceder ou originar crédito para o fundo em que atua | F1/F2 (originação Save Invest) × F16 | **CONFLITO** de independência; entidades separadas por linha `[VALIDAR JURÍDICO]` (Res. CVM 175, a conferir no texto) | `estudo-jornada-anexo-interno.md` |
| Sociedade empresária e serviço jurídico ao cliente | F8, F9, F12 × consultoria | Risco OAB (art. 34 da Lei 8.906/94; consulta OAB/BA) | idem |
| M&A com a Save também financiadora | F20 × CI, CAP | CONFLITO de interesse; divulgação por escrito `[VALIDAR JURÍDICO]` | F20 |
| CAP e CI na mesma rodada | CAP × CI | Alternativas; apresentar uma de cada vez `[HIPÓTESE]` | R1 |
| CVM e valor mobiliário | CAP, F16, F20 | Jurídico antes de qualquer conversa | matriz de agentes |
| Hedge e seguro sem habilitação | F15, F5 | Save não é corretora de seguros; só via parceiro habilitado | F15 |
| Taxas de 8% a 12% e carência de até 3 anos | CI, CAP | Dito em reunião; **não repetir ao cliente** | `pendencias.md` |

### 2.3 Pré-requisitos duros por produto (para o gestor de esteira conferir a passagem)
| Produto | Pré-requisitos duros | Dados mínimos |
|---|---|---|
| T-teses | Etapa 0: análise de aptidão; Real/Presumido conforme a tese; decadência de 5 anos | SPED (EFD-Contribuições, ICMS), folha, documento do incentivo, ACT/CCT, notas de PF |
| REC | Tese executada + 12 ou mais competências novas | Último fechamento |
| F1 | Venda a prazo B2B, procuração do e-CAC, definição de quem contrata | Carteira, vencidos, contratos |
| F2 | F1 ativa ou carteira B2B registrada; instituição autorizada | Notas, duplicatas, histórico por sacado |
| F6 | Parecer ou consulta com débito | Débitos Receita, PGFN, estado, município |
| P01 / F10 | Real ou Presumido; faturamento acima de cerca de R$ 4,8 mi | Cadastro de NCM, regime, saldos credores |
| F9 | Porte e patrimônio; consulta ao Tributário (ITCMD) | Matrículas, contrato social, quadro societário |
| F16 | Cerca de R$ 10 mi/mês de faturamento, recebíveis com nota, passivo organizado | Carteira por sacado, balanço, nota fiscal |
| CI | Critério a conciliar (v2.3 × 13/10); garantia real livre; 2 anos de demonstrações; certidão; F19 pronto | Dossiê, matrícula, plano |
| CAP | F19 pronto; Jurídico (CVM) aprovou a conversa | Plano, projeção, data de entrada e saída do investidor |
| MQ | EV-PY aceito; Lucro Real; indústria intensiva em mão de obra, energia e capital; fora frigorífico | Balancete, custos, DRE, plano de expansão |
| INT | Capacidade e caixa no Brasil resolvidos (MQ ou CI concluído) | Plano comercial |

### 2.4 "No máximo 2 produtos novos por vez" (definição operacional) `[HIPÓTESE]`
- **Conta como novo:** cada produto com contrato e entrega próprios, que exige tempo, dados ou decisão do cliente (T-teses juntas contam como **um** produto, "Recuperação tributária"; F1, F2, F6, P01, F9 e cada produto da etapa 3 contam um cada).
- **Não conta:** descoberta (conversa sem contrato), REC, acompanhamento de produto já em curso, a camada contínua (CC1 a CC3), F8 reativo (defesa de intimação que chegou) e um produto da etapa 1 já em fase de acompanhamento (depois do pedido protocolado).
- **Pares recomendados:** F1 + Recuperação · Recuperação + F6 · F6 + P01 · P01 + F9 · F19 + F11 · F19 + CAP/CI.
- **Pares vetados:** CAP + CI na mesma rodada · F18 + CI sem decisão de garantia · F20 + CI/CAP (conflito) · qualquer dupla com produto em validação **e** outro produto novo da mesma etapa 3 · EV-PY + MQ (o MQ só depois do estudo).
- **Exceção que exige o Luis:** cliente grande com três frentes em paralelo (por exemplo, urgência de 2027 em T08 + F6 + descoberta de CI). Descoberta não gasta vaga, então a combinação cabe; mas o limite de capacidade das áreas continua valendo.

---

## 3. Gatilhos e sinais por produto, ligados ao `mapa_conta`

O `mapa_conta.py` hoje cobre 10 produtos (RT, GC, PAS, JUR, PLAN, EP, ANT, FIDC, CI, MQ) e lê estes campos: `setor`, `cnae`, `regime`, `faturamento`/`faixa`, `capital`, `passivo_debitos`, `passivo_suspenso`, `acao_judicial`, `competencias_novas`, `rt_ganho`, `rt_recebido`, `teses`, `ja_tem` (cards em outros funis). **Campos novos propostos `[HIPÓTESE]`** marcados com `+`: o que depende de DRE, balanço, SCR ou e-CAC ainda não existe na máquina e deve nascer do painel CC2.

### 3.1 Campos novos a criar (para o `depto-ti` e o `depto-dados`)
| Campo | Fonte | Para que serve |
|---|---|---|
| `+contas_receber_x_fat_mensal` | DRE/balanço (F1) | Gatilho de F1, F2, F16 |
| `+vencidos_pct` | Carteira (F1) | F1, F2 |
| `+despesa_financeira_x_resultado` | DRE | F7, CI, F11 |
| `+divida_cp_x_fat_mensal` | Balanço, SCR | F7 (3 a 4 faturamentos = risco de insolvência) |
| `+n_bancos`, `+parcela_mensal` | SCR | F7 (pergunta do mês de aperto) |
| `+mes_aperto_caixa` | Conversa registrada | F7, F2, F15 (sazonalidade) |
| `+saldo_credor_pis_cofins`, `+saldo_credor_icms`, `+saldo_ipi` | SPED | T08, T11, F3, F10 |
| `+depositos_judiciais`, `+execucao_fiscal` | Parecer, consulta | F5, F6 |
| `+ativos_reais_livres_valor` | Matrícula, balanço | CI, F9, F18, F5 |
| `+exporta`, `+divida_moeda_estrangeira` | Receita, SISCOMEX, SCR | F21, F15, TI, CI |
| `+empresa_familiar_sucessao` | Conversa, quadro societário | F9, F12 |
| `+crescimento_x_capacidade`, `+ebitda_negativo_por_investimento` | Plano, DRE | F19, CAP |
| `+compras_pf_pct`, `+beneficio_icms_estadual`, `+acordo_coletivo` | SPED, documento | T18, T19, T14, T15, T17 |
| `+folha_representativa` | eSocial, DCTFWeb | T12, T13, F14 |
| `+certidao_status` | e-CAC, PGFN | Passagem 2→3 |

### 3.2 Gatilhos por produto
| Produto | Sinal que abre | Fonte hoje | No `mapa_conta` | Aderência sugerida | Descarta |
|---|---|---|---|---|---|
| T01 | Revenda com alíquota zero, Real, NCM elegível | Parecer, CNAE | existe (`r_aliquota_zero`) | alta se tese de aquisições não aparece | Supermercado, café, Simples |
| T02 | Indústria ou serviço estruturado no Real, exportação ou suspensão | Parecer, CNAE | existe (RT) | alta no Real | Presumido |
| T03/T04/T05/T09 | ICMS na base; ICMS-ST na revenda; faturamento acima de R$ 300 mil/mês | Parecer | existe (RT) | média | Receita de alíquota zero (nada a excluir) |
| T06/T07 | Alto volume de compras com ICMS (T06); serviço com ISS (T07) | Parecer | existe parcial | média | Sem Real (T06) |
| T08/T11 | Saldo credor acumulado + saídas sem débito + **2027** | SPED | `+saldo_credor_*` | **alta com urgência** | Sem Real |
| T10 | Indústria no Real com compras de atacadista | Parecer | existe | média | Carne com IPI zero ou NT |
| T12/T13 | Folha relevante, setor intensivo em folha; Sistema S só com modulação | Parecer | existe (`r_previdenciaria`) | alta em confecção e transporte | T13 sem decisão anterior a 15/12/2020 |
| T14/T15 | Benefício estadual com documento | SPED | `+beneficio_icms_estadual` | alta com documento | Sem documento |
| T16/T17 | Presumido regular (T16); ACT/CCT (T17) | Parecer, convenção | `+acordo_coletivo` | média | — |
| T18/T19 | Agroindústria ou cooperativa com compras de PF e saldo acumulado | SPED, DCTFWeb | existe parcial (`r_agro_pf`) | média | Cerealista pura; bovino mercado interno (judicial, risco alto) |
| REC | 12 ou mais competências novas desde a análise | Parecer | existe | alta ≥ 12, média ≥ 6 | — |
| F1 | Contas a receber acima do faturamento mensal, vencidos altos, caixa que aperta | Carteira, conversa | existe (`r_gestao_contas`) | alta se B2B e ≥ R$ 10 mi; média se ≥ R$ 4,8 mi | Varejo à vista |
| F2 | Banco antecipando com deságio, sazonalidade, carteira B2B | Carteira | existe (`r_antecipacao`) | média | Sem nota (venda gerencial) |
| F3 | Saldo credor de ICMS recorrente (exportador, incentivo, ST), CIAP | EFD ICMS | `+saldo_credor_icms` | média `[HIPÓTESE]` | Estado sem regra de transferência |
| F4 | Credor ou devedor de precatório | Conversa | novo | baixa; **não proativo** | Risco reputacional |
| F5 | Depósito judicial alto, execução fiscal, penhora em dinheiro | Parecer, consulta | `+depositos_judiciais` | média | Sem apólice viável |
| F6 | Débito no parecer; CND positiva com efeito de negativa ou vencida | Parecer | existe (`r_passivo`) | alta se ≥ R$ 500 mil | Débito abaixo de R$ 100 mil: sem produto à parte |
| F7 | Despesa financeira alta + resultado baixo; dívida CP = 3 a 4 faturamentos; muitos bancos | DRE, SCR | `+divida_cp_*`, `+n_bancos` | alta nos dois sinais juntos | Insolvente (caso de advogado de insolvência) |
| F8 | Débito com exigibilidade suspensa, intimação, ação judicial | Parecer | existe (`r_juridico`) | média | — |
| P01 | Real ou Presumido, faturamento ≥ R$ 4,8 mi | Receita, HubSpot | existe (`r_planejamento`) | alta ≥ R$ 30 mi ou alimento | Simples (avaliar híbrido) |
| F10 | Real ou Presumido + saldo credor + varejo/atacado/alimento | SPED | `+saldo_credor_*` | média `[HIPÓTESE]` | — |
| F9 | Faturamento ≥ R$ 20 mi ou capital ≥ R$ 5 mi; família com terra e planta | Receita | existe (`r_patrimonial`) | média; alta com sucessão | Estrutura antiga sem revisão ITCMD (revisar) |
| F11 | Dado inconsistente, pedido de banco ou fundo por DRE auditado | Conversa | novo | média `[HIPÓTESE]` | — |
| F12 | Sócio mais velho, filhos na operação, entrada de sócio | Conversa | `+empresa_familiar_sucessao` | média | — |
| F13 | Investidor ou comprador à vista; dado de cliente em volume | Conversa | novo | baixa até haver CAP/F20 | — |
| F14 | Passivo trabalhista, terceirização, folha grande | Parecer | `+folha_representativa` | média | Contencioso (advogado trabalhista) |
| F15 | Dívida em moeda estrangeira, exportação, commodity | SCR, SISCOMEX | `+divida_moeda_estrangeira` | média | Opinião sobre o câmbio: proibido |
| F16 | Cerca de R$ 10 mi/mês de faturamento, antecipa com banco, cadeia grande | Receita, carteira | existe (`r_fidc`, ≥ R$ 120 mi/ano) | média | Faturamento abaixo do piso; sem nota |
| F17 | Produtor com produção e garantia; trading com cadeia de produtores | Conversa | novo | média no agro `[HIPÓTESE]` | Café sem garantia definida |
| F18 | Imóvel próprio quitado e necessidade de caixa sem perder a operação | Balanço | `+ativos_reais_livres_valor` | baixa `[HIPÓTESE]` | Ativo que vai para garantia de CI |
| F19 | Crescimento acima da capacidade, EBITDA negativo por investimento, pedido de capital | Conversa, DRE | `+crescimento_x_capacidade` | alta | Sem plano e sem dono disposto a abrir dado |
| CI | Faturamento ≥ R$ 50 mi/ano, ativos ou garantias > ~R$ 60 mi, necessidade a partir de US$ 5 mi; setor do ICP | Receita, balanço | existe (`r_ci`) | descoberta apenas | Sem garantia real; débito aberto |
| CAP | Ticket abaixo do piso do CI ou preferência por sócio; plano de expansão | Conversa | novo | descoberta apenas | Sem permissão do Jurídico (CVM) |
| EV-PY / MQ | Indústria intensiva em mão de obra, energia e capital, no Real; custo de produzir como dor | CNAE, regime | existe (`r_maquila`) | descoberta apenas | Frigorífico (D59), perecível sem submaquila |
| GEX / INT / TI | Operação instalada fora; plano de exportação; DCBE | Conversa | novo | só depois de MQ/CI | MQ não concluído |
| F20 | Sócio querendo sair, interesse de comprador, sucessão sem herdeiro | Conversa | novo | baixa `[HIPÓTESE]` | Save financiadora no mesmo caso |
| F21 | Exportador com contrato novo | SISCOMEX, DRE | `+exporta` | média | — |
| F22 | Indústria ou agro com P&D, energia, projeto de inovação | Conversa | novo | baixa `[HIPÓTESE]` | — |
| F23 | Agro ou indústria com custo de energia e capital para investir | Conversa | novo | baixa `[HIPÓTESE]` | — |

**Regra de despacho do mapa `[HIPÓTESE]`:** o mapa devolve até 6 produtos ordenados por etapa e aderência; o gestor de esteira escolhe os 2 que entram, **aplicando a seção 2.4**. Produtos em validação aparecem em linha separada: "descoberta, portão G2".

---

## 4. Jornadas-tipo

Tempos em meses desde o aceite do primeiro produto (M0). Marcam o que o cliente **vê**, não prazos prometidos. `[HIPÓTESE]` em todas as durações: a Save não tem série histórica de ponta a ponta; o piloto da seção 7 mede.

### 4.1 Por perfil
**Média-baixa (R$ 4,8 a 30 mi/ano).**
| Meses | Passo | Produto (novos do período) |
|---|---|---|
| M0 a M1 | Entrada pela dor: caixa ou diagnóstico; acesso ao e-CAC | F1 **ou** diagnóstico (T-teses) |
| M1 a M6 | Teses administrativas, depois judiciais; REC no fim | Recuperação (1 novo) + F1 (2º) |
| M4 a M12 | Passivo se houver débito; planejamento e reforma | F6 → P01 (1 a 2 novos por vez) |
| M12 em diante | Revisão anual; se cresceu de porte, reavalia a porta | CC1, CC2; F11 se pedirem dado |

**Média-alta (R$ 30 a 120 mi/ano).** Igual à média-baixa, com **F2 em M3 a M9** e **descoberta de F16 e CI** a partir de M9, sem proposta. Etapa 3 só com certidão e dados. Passagem para a grande acontece por faturamento ou por ativo: o mapa reavalia a porta a cada revisão anual.

**Grande (acima de R$ 10 mi/mês ou garantias > ~R$ 60 mi).**
| Meses | Passo | Produto |
|---|---|---|
| M0 a M2 | Diagnóstico 360 em paralelo: tributário, matrícula dos ativos, leitura do SCR | T08/T11 (urgência 2027), T01/T02 |
| M2 a M8 | Teses administrativas; judiciais; F2 se carteira | Recuperação + F2 |
| M4 a M12 | F6 se houver débito; F9; P01/F10 | F6 → F9 (2 novos) |
| M9 a M18 | F11, F13, TI; descoberta de CI e F16 | Descoberta (não gasta vaga) |
| M12 a M24+ | F16 e/ou CI **se o G2 e o G3 permitirem**; EV-PY → MQ → GEX; INT na 2ª rodada | 1 produto de etapa 3 por vez |

**Em crescimento (indústria de alimentos, caso do presunto cru).**
| Meses | Passo | Produto |
|---|---|---|
| M0 a M3 | Plano de negócio, projeção, destino do recurso; kit de análise e NDA; parecer preliminar de viabilidade | P02 + F19 |
| M3 a M9 | Equity ou sócio estratégico; CI só se o ticket e a estrutura couberem (a pergunta "estrutura abaixo de US$ 5 mi" segue aberta) | CAP **ou** CI (descoberta até o G2) |
| M6 a M12 | Controladoria e integridade que o investidor pede | F11, F13 |
| M12 a M24 | Recurso caiu: escrow, hedge; mercado externo na 2ª rodada | F1 (escrow), F15, INT (descoberta) |
Tributário entra quando o regime e o crédito permitirem; EBITDA negativo por investimento não impede F19.

### 4.2 Por setor
Cada setor segue o playbook em `playbooks-setoriais.md`. Aqui está só a **trilha de jornada** (etapa 1 → 2 → 3).

**Agro e café (trading, exportador, cerealista, produtor).**
| Etapa | Trilha |
|---|---|
| 1 · M0–M6 | Exportador: **T08 (conta gráfica), T02 (insumos)**, T18/T19 se houver compra de PF; cerealista de grãos: T01 (café fora); F2 sobre recebível de safra |
| 2 · M3–M12 | Defesa de glosas e ressarcimento negado (F8); F6 se houver débito; P01 com regime agro; F9 (família com terra, armazém, estoque); F5 se depósito judicial |
| 3 · M12–M24 | **CI** (fazendas, galpões e silos em garantia; contrato futuro e CPR como garantia estão **em aberto**); **F16 multicedente** (trading financiando produtor); F17 CPR/CRA; F21 (ACC/ACE); F15 hedge e seguro de safra; F23 energia como uso do capital |
| Ordem do caso trading | Funding com as fazendas em garantia (se aprovado no portão) → FIDC financiando produtor e trading |
| Cuidados | MQ não se aplica; café fora de T01; compromisso do Luis: mapear exportadores com ativos > R$ 60 mi |

**Indústria de alimentos.**
| Etapa | Trilha |
|---|---|
| 1 · M0–M6 | T02 e T03/T04 → T10/T11 → T12 → T14/T15 (se houver incentivo) → T17 (ACT/CCT) → F1; T18 se agroindústria |
| 2 · M3–M12 | P01 com mix por NCM (alíquota zero em 2027) → F2 → F6; F11 se pedirem dado |
| 3 · M12–M24 | Grande: F16 ou CI. Em crescimento: **F19 → CAP → INT** (caso do presunto cru). MQ tem baixa aderência (perecível, pouco intensivo em mão de obra) e sem estudo pago até 30/06/2027; frigorífico bloqueado |
| Caso do hortifrúti congelado (R$ 150 mi/ano, tributário feito) | Entra na etapa 2: F12 (sucessão), F15 (hedge do euro), F7 (troca de dívida) → etapa 3: F16 da cadeia de produtores, EV-PY |

**Varejo e atacado.**
| Etapa | Trilha |
|---|---|
| 1 · M0–M6 | Supermercado: T04/T03 (ICMS-ST e ICMS) → T12. Hortifrúti: T01 (PER) → T03. Atacado: F1 + T01 |
| 2 · M3–M12 | P01/F10 (mix por NCM e split payment) → F6 → F2 |
| 3 · M12–M24 | F16 se rede grande (≥ R$ 10 mi/mês); **multicedente de fornecedores** (supermercado, a aprofundar em reunião futura); CI só atacado de hortifrúti com porte |
| Cuidados | T01 fora para supermercado; MQ sem aderência; varejo recebe à vista ou no cartão, F1 só se houver venda a prazo |

**Construtora e imobiliário** (sem playbook setorial: **lacuna**).
| Etapa | Trilha `[HIPÓTESE]` |
|---|---|
| 1 · M0–M6 | Diagnóstico tributário com regime a confirmar `[VALIDAR TRIBUTÁRIO]`; F5 se houver execução fiscal ou depósito judicial |
| 2 · M3–M12 | F6 → F9 (patrimônio, estrutura das empresas do grupo) → F10 (regra do setor imobiliário na reforma `[VALIDAR TRIBUTÁRIO]`) → F11 (controle de obra e caixa) |
| 3 · M12–M24 | **CI avaliado pelo ativo monetizável e retorno do projeto (VGV)**, não só pelo balanço (descoberta); F18 só para imóvel próprio fora da garantia; F15 seguros |
| Cuidados | Faltam playbook, ICP, gatilhos e lista de teses aplicáveis; pedir ao `depto-intel-comercial` |

**Cooperativa** (agro e laticínios; **Santa Clara fica na conversa própria**, aqui só o modelo).
| Etapa | Trilha `[HIPÓTESE]` |
|---|---|
| 1 · M0–M6 | **T18** (cooperativas no Lucro Real são elegíveis), **T19 Funrural**, T02; REC; F1 se vender a prazo |
| 2 · M3–M12 | F6 → P01 com regime de cooperativas `[VALIDAR TRIBUTÁRIO]` → F12 governança (conselho, sucessão de diretoria; estruturação patrimonial clássica pode não caber `[VALIDAR JURÍDICO]`) → F13 |
| 3 · M12–M24 | F16 multicedente com **cooperados como cedentes** (a aprofundar); F17 CPR/CRA; CI com ativos industriais (descoberta); F23 energia |
| Cuidados | T18 e T19 têm judicial na primeira fase (MS), depois PER/DCOMP; preço do Funrural pendente |

### 4.3 Casos para testar (sem nome de cliente)
| Caso | Porta | Trilha |
|---|---|---|
| Indústria de alimentos em crescimento (cerca de R$ 8 mi/ano) | C | P02 + F19 → CAP ou CI (se o ticket couber) → F11 e F13 → INT na 2ª rodada |
| Indústria de hortifrúti congelado (cerca de R$ 150 mi/ano, tributário feito) | G | Etapa 2: F12, F15, F7 → etapa 3: F16, EV-PY |
| Trading de café | G | CI (descoberta) com fazenda → F16 multicedente → F21 |
| Cooperativa láctea e de suínos | Conversa própria | Referência de deck e dados; não tratar aqui |

---

## 5. Camada contínua

### 5.1 Revisão tributária anual (CC1)
| Item | Proposta `[HIPÓTESE]` |
|---|---|
| Quando | Aniversário do primeiro negócio ganho, ou fechamento do ano fiscal, o que vier antes; e a cada marco regulatório do radar |
| O que revisa | Teses novas do catálogo que o parecer não cobriu; REC (12 competências); decadência de 5 anos; saldos credores antes da CBS; novos benefícios estaduais; mudança de regime |
| Quem | `depto-tributario` + `revisor-diagnostico` + `recuperador`; `depto-solucoes` consolida o mapa |
| Saída | Mapa da conta atualizado, Mapa de Valor, próximo produto sugerido (máximo 2) |
| Gatilho automático | Rotina C da skill: ganho de RT, parecer novo com débito, recorrência, mudança regulatória |

### 5.2 Painel DRE × SCR × e-CAC (CC2)
| Bloco | Indicadores | Alerta que gera | Produto sugerido |
|---|---|---|---|
| DRE | Margem, despesa financeira ÷ resultado, receita por tipo, carga efetiva | Despesa financeira alta com resultado baixo | F7, CI, F11 |
| Balanço e carteira | Contas a receber ÷ faturamento mensal, vencidos, dívida de curto prazo ÷ faturamento | CP = 3 a 4 faturamentos; vencidos acima da média | F1, F2, F6, F7 |
| SCR | Nº de bancos, prazo, carência, taxa, endividamento | Muitos bancos com parcela pesada | F7, CI |
| e-CAC | Débitos, parcelamentos, certidão, fluxo consolidado | Débito novo; CND vencida; indício de taxa de maquininha | F6, F8, F1 |
| SPED | Saldos credores, mix de NCM, benefício estadual | Saldo acumulado; 2027 próximo | T08, T11, P01, F3 |
| Estado do plano | Produtos contratados e abertos, passagens cumpridas, valor entregue | Passagem pendente | Quadro do gestor |
- **Regra:** o painel **aponta**, não decide. O e-CAC é fluxo consolidado, serve de alerta preliminar; nunca substitui a análise com DRE.
- **Dono e entrega:** `depto-dados` modela, `depto-resultados` mede valor, Cátia automatiza alertas (ecossistema, seção 7). Dado de cliente fica no Mac (LGPD).

### 5.3 Consultor no conselho do cliente (CC3)
| Item | Proposta `[HIPÓTESE]` |
|---|---|
| Papel | O consultor (gestor de esteira nível 3) senta com o dono: negócio, não produto |
| Rito | Encontro trimestral de 45 minutos: Mapa de Valor, resultados, passagens, os 90 dias seguintes; retrospectiva mensal interna |
| Carteira | 15 a 30 clientes por consultor, ponderada por porte |
| Medidas (por carteira, nunca por pessoa) | Tempo entre passos, passagens no prazo, serviços por cliente (alvo: dois), taxa de implementação, valor realizado × previsto, satisfação |
| Risco | OAB: a sociedade empresária não oferece serviço jurídico a cliente; o consultor **conecta** ao advogado, não presta `[VALIDAR JURÍDICO]` |
| Retenção | Cada ciclo termina propondo o próximo produto com base no painel |

---

## 6. Papéis e rota de agentes por etapa

### 6.1 Papéis humanos
| Papel | O que faz | Limite |
|---|---|---|
| **Consultor de negócio** (gestor de esteira, níveis 1 a 3) | Dono do projeto do cliente; conduz a esteira; confere a condição de passagem; presta contas | Não promete valor, prazo, taxa ou êxito; não aprova tese nem parecer; escala ao Luis, ao João Mattos ou ao Jurídico |
| **PO / dono do projeto** | Traduz a demanda e aciona áreas; pode ser o mesmo que o gestor de esteira; **quem é hoje segue em aberto** | A definir (item 5 da seção 7) |
| **Time tributário** | Teses, planejamento, reforma, incentivos | Validação humana de toda pré-análise |
| **Time jurídico** | F6, F8, F9, F12, F13; prazos; LGPD | Advogado valida; OAB |
| **Save Invest** (Júnior) | F1, F2, F16 | A Save não antecipa nem distribui cotas |
| **João Mattos e Paulo** | CI, CAP, EV-PY, MQ, GEX, INT, TI | Portões G0 a G4; resposta às perguntas críticas até 31/10 |
| **Parceiro externo** | Seguros, M&A, trabalhista, sucessão, energia, parceiro técnico de inovação | Definido caso a caso (decisão do Luis) |
| **Master ou indicador** | Dono da relação | Remuneração de indicação × condução: adiada |

### 6.2 Rota de agentes por etapa
| Passo | Agente líder | Agentes que atuam | Revisores | Saída |
|---|---|---|---|---|
| **Entrada** (pedido ou demanda) | `gabinete` | `depto-solucoes`, `depto-intel-comercial` (ICP e conflito de canal), `depto-operacoes-canal` | `depto-qualidade` | Rota aprovada, porta definida |
| **Diagnóstico e mapa** | `depto-solucoes` (Analista de Sinais) | `recuperador`, `revisor-diagnostico`, `depto-dados` (e-CAC, SPED), especialista setorial | Tributário, Jurídico | `mapa_conta` + Mapa de Valor |
| **Etapa 1** | `depto-tributario` / Save Invest | `recuperador`, `apresentacao-diagnostico`, `depto-contratos` | Jurídico, Qualidade | Pedido protocolado, carteira em operação |
| **Passagem 1→2** | Gestor de esteira (humano) | `depto-solucoes` (Planejador), `depto-dados` | `depto-resultados` | Registro de passagem: caixa entrou, dados ok |
| **Etapa 2** | `depto-juridico`, `depto-tributario` | `depto-resultados` (CFO), `depto-pessoas` (governança), `depto-internacional` (F7, F15, TI) | Qualidade | Passivo tratado, certidão, plano pós-reforma |
| **Passagem 2→3** | Gestor de esteira | `depto-internacional` (Guardião do Produto Novo), Jurídico | João Mattos | Conferência de certidão, demonstrações, garantia |
| **Etapa 3, prontos** (F16) | `depto-internacional` | Save Invest, Jurídico (CVM) | Qualidade | Estrutura com a Save Invest, sem distribuir cotas |
| **Etapa 3, em validação** (CI, CAP, MQ, EV-PY, INT) | `depto-internacional` | Qualificador, Estruturador de Garantias, Maquila, Regulatório & Câmbio | Jurídico, **Revisor de linguagem**, João Mattos | **Descoberta**; nada sai antes do G2 |
| **Camada contínua** | `depto-solucoes` | `depto-pos-venda`, `depto-partner-success`, `depto-dados`, `depto-resultados` | Qualidade | Revisão anual, painel, encontro trimestral |
| **Material para fora** | `depto-marketing` | Áreas envolvidas | `depto-qualidade` (`auditar_texto.py`), Luis vê um exemplo antes da escala | Peça aprovada |
| **Decisão de estratégia** | `conselho-partners` | Presidente e conselheiros | Luis | Ata e decisão (próprio × parceiro, preço, meta) |

**Passagens: condições que o gestor confere `[HIPÓTESE]`**
1. **Entrada → etapa 1:** cliente certo (ICP), conflito de canal resolvido, linha de base assinada, procuração do e-CAC, NDA.
2. **Etapa 1 → 2:** primeiro caixa efetivo (compensado, restituído ou cobrado), DRE e balanço recebidos, débitos mapeados.
3. **Etapa 2 → 3:** CND ou CPEN, passivo tratado ou em transação regular, duas demonstrações, garantia real livre com matrícula, plano de negócio (F19), Jurídico ciente (CVM, se houver cotas).
4. **Etapa 3 → contínua:** recurso efetivamente caiu (marco de produto validado), controle do uso (escrow, F11), revisão anual agendada.

---

## 7. Lacunas e perguntas ao Luis

### 7.1 Decisões que dependem do Luis (as 5 mais importantes em **negrito**)
1. **Próprio × parceiro** dos candidatos (F3, F4, F5, F11 a F15, F17, F18, F20 a F23, GEX). Sugestão do handoff: próprio = tributário, financeiro estruturado e coordenação; parceiro = seguros, M&A, trabalhista. **Define o escopo do portfólio de 2027.**
2. **Caso-piloto** para medir tempos e passagens (indústria de alimentos em crescimento é o mais completo; hortifrúti congelado cobre a porta grande).
3. **Escopo do que vai ao parceiro em 2027:** só prontos, ou prontos mais descobertas; formato (catálogo, jornada, deck). Etapa 3 em validação não pode ser exposta antes do G2.
4. **Etapa de F2 (antecipação) e de F7:** a `esteira.md` põe a antecipação na onda 2 e o passivo bancário em definição; as fichas e o handoff os põem em destravar caixa (F2) e em oxigenar (troca de dívida). Decidir onde ficam. Meu voto `[HIPÓTESE]`: F2 em destravar caixa **apenas como parte da F1**; F7 em proteger e controlar, com a troca de dívida via CI virando etapa 3.
5. **Quem é o PO hoje**, e se o gestor de esteira serve por cliente ou por carteira de Master (pergunta 2 do modelo do gestor).
6. Escala da porta média: aceitar média-baixa e média-alta (seção 1.3)?
7. Limite de "2 produtos novos por vez": aceitar a definição da seção 2.4 (descoberta, REC, camada contínua e defesa reativa não contam)?
8. Programa de formalização: segue fora. Mas o F16 só aceita título com nota; confirmar que a regra "FIDC exige nota cheia" basta, sem programa, por ora.
9. Setor construtora: abrir playbook e ICP? Hoje não há nada setorial.
10. Remuneração de indicação × condução e do parceiro em produto maduro e em MVP (adiada).

### 7.2 Perguntas a outros donos (para a jornada ficar fechada)
| A quem | Pergunta |
|---|---|
| João Mattos | Critério do CI (v2.3 × 13/10); estrutura abaixo de US$ 5 mi; o que pode aparecer de CAP e FIDC antes do G2; rede de representantes que existe de fato; MQ-Q1 e MQ-Q6; lei do regime de bens de capital; governança no exterior (GEX) como serviço recorrente |
| Júnior / Save Invest | Quem contrata e quem presta a F1; habilitação; entidades separadas por linha para originar e para estruturar FIDC (independência CVM 175); piso do FIDC; multicedente |
| Jurídico | Risco OAB sobre consultoria + serviço jurídico ao mesmo cliente; valor mobiliário em CAP, F16 e F20; práticas sinalizadas (antecipação sobre venda gerencial, escrow contra bloqueio); linha do parceiro sobre sigilo e CRS; seguro garantia na transação (LC 236/2026); precatórios |
| Tributário | Regra estadual de F3; F10 como módulo do P01; regime de cooperativas e de construtora; T18 e T19 na cooperativa |
| `depto-dados` / `depto-ti` | Criar os campos `+` da seção 3.1; construir o CC2 |
| `depto-intel-comercial` | ICP e território de F3, F5, F17, F18, F22, F23, construtora |

### 7.3 Inconsistências encontradas nas fontes (para o Luis saber o que não bate)
| # | Onde | O que não bate |
|---|---|---|
| 1 | `esteira.md`, playbooks setoriais e `estudo-jornada-anexo-interno.md` | Ainda chamam F1, F2 e F16 de "descoberta" ou "em definição". A decisão de 19/10 diz **prontos**. A `esteira.md` também chama o FIDC de "MVP". Atualizar os playbooks antes de usar em material |
| 2 | `jornada-2027.md` × `esteira.md` | A antecipação aparece em etapas diferentes (destravar × proteger) |
| 3 | `jornada-2027.md` | P6 (passivo bancário) na etapa 1; fichas o põem na 2; o handoff o chama de "oxigenar" |
| 4 | CI | Critério v2.3 × reunião de 13/10 |
| 5 | Porta média | Corte do `mapa_conta` (R$ 4,8 mi/ano) × porta do Luis (até R$ 10 mi/mês) |
| 6 | Pasta `docs/portfolio-2027/` | O LEIA-ME fala de "fichas de onda 1" e as fichas rascunho cobrem 23 itens sem dono |

### 7.4 Lacunas desta entrega
- Durações das jornadas (seção 4) são `[HIPÓTESE]`; o piloto precisa medir.
- Nenhum número de mercado foi usado; nada foi pesquisado na web nesta rodada. Os dados vêm da base interna com data de 19 a 22/10/2026.
- A aderência de F3, F4, F17, F18, F22 e F23 depende de ICP, que não existe.
- A camada contínua (CC2) depende de campos que ainda não existem na máquina.
- Falta o `radar` de 2027 (CBS e IBS) atualizado para o painel e para F10.

---

## 8. Registro de revisão (gerente)

```json
"revisao": {
  "gerente": "depto-solucoes",
  "especialistas": ["Arquiteto de Soluções", "Planejador da Esteira", "Analista de Sinais", "Revisor de Promessas"],
  "rodadas": 2,
  "areas_consultadas": [],
  "aprovado": false,
  "ajustes": [
    "Rodada 1: unifiquei os códigos (T, REC, P01/P02, F1 a F23, CI, CAP, MQ, EV-PY, GEX, INT, TI) para evitar a colisão P1 a P17 × P01/P02; retirei preços e percentuais de remuneração que vinham das fichas; marquei [HIPÓTESE] em durações, subfaixas e regras de contagem.",
    "Rodada 2: conferi a ordem das etapas contra a esteira e o handoff e listei as divergências na seção 7.3; incluí as travas jurídicas (CVM 175, OAB, valor mobiliário) como CONFLITO; produtos em validação ficaram só como descoberta; sem nome de cliente.",
    "Não consultei Tributário, Jurídico, Internacional nem Qualidade: este documento é interno e depende da validação deles antes de qualquer uso externo."
  ]
}
```
