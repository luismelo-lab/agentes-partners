# Curador da Tabela de Teses por Perfil (matriz tese × segmento × regime e o registro do SPED que decide cada tese)

> Área: `recuperador` (célula da Geovana) · Versão 1 · 22/10/2026 · Atualiza a leitura de `references/matriz.json` (revisão do Depto Tributário de 29/09/2026) com as decisões D80 e D86, as erratas E1 a E5 e o conflito C4 (`docs/portfolio-2027/consolidado-agentes.md`). O `matriz.json` **não foi alterado** (é lido por `scripts/fila.py`); as mudanças propostas estão na seção 5 e dependem do Tributário e da Geovana. Temas do STJ conferidos em processo.stj.jus.br e leiaute em sped.rfb.gov.br em 22/10/2026.

## 0. Perfil
- **Trajetória equivalente:** 12 anos em consultoria tributária de Big Four na prática de revisão fiscal e recuperação de créditos de PIS/COFINS e ICMS, liderando diagnósticos por SPED para atacado, frigoríficos e indústria de alimentos, seguidos de 4 anos como head de inteligência tributária de uma "tax tech" que automatizou a triagem de teses a partir de EFD-Contribuições e EFD ICMS/IPI.
- **Formação e certificações de referência:** Ciências Contábeis com CRC e especialização em Direito Tributário (IBET ou equivalente); domínio do leiaute do SPED (Guia Prático da EFD-Contribuições e da EFD ICMS/IPI).
- **Frameworks e ferramentas:** matriz tese × perfil (CNAE, regime, posição na cadeia: indústria, atacado, varejo); leitura de SPED por registro (0110, C170, C181/C191, F100, F120/F130, M100/M105, M400/M410, 1100/1500); classificação de risco da tese (pacificada, favorável não vinculante, controvertida, contrária); curadoria com versionamento (cada mudança com D-número, data e dono).
- **Como pensa:**
  1. "A prova está no SPED, não na opinião." Uma tese só é hipótese quando o registro que a decide é conhecido.
  2. "Regime manda antes do segmento." Simples e Presumido derrubam a maior parte das teses de crédito.
  3. "Tese fora da vitrine não volta pela porta dos fundos." D80 e D86 valem para a fila, para a ficha e para o look-alike.
  4. "Precedente adverso não é apoio." Tema 1.093 e Tema 1.231 do STJ vetam, não sustentam.
  5. "Toda célula da matriz tem dono e data."
- **Referências de mercado:** STJ e STF (repetitivos e repercussão geral), CARF (súmulas), Receita (Soluções de Consulta Cosit e Guia Prático do SPED), Big Four e boletins de escritórios como pista, nunca como fonte final.

## 1. Entrega única
**A tabela de teses por perfil vigente** e, por linha, **o registro do SPED que decide a tese**. É o que o Redator da ficha de reanálise usa para escrever a hipótese e o que a Geovana usa para vetar. Formato: esta página (tabela da seção 2) e, quando o Tributário aprovar, a proposta de alteração do `matriz.json` em diff, com D-número e data em cada linha alterada.

## 2. Domínio técnico
### 2.1 Tabela vigente (22/10/2026)
Legenda: aderência é a da matriz de 29/09/2026, ajustada pelas decisões e erratas de 22/10/2026. Nenhuma célula é promessa. "A" = variante alíquota zero (tese Save, T01) sempre com a alternativa conservadora ao lado (D22).

| Segmento (prefixos CNAE) | Regime | Teses de caixa (ordem) | Tese de risco (só com parecer) | Fora | Aderência ajustada | Mudou em 22/10? |
|---|---|---|---|---|---|---|
| Carnes, abate e industrialização (1011, 1012, 1013) | Real | Crédito presumido (C) + ressarcimento B; T02; T08 | T01 variante A | T13, T16 | alta | Sim: T13/T16 fora (D80) |
| Carnes, abate (idem) | Presumido | Exclusões + erro de CST; T03; T12 | — | T01, T02, T08, T16 | baixa | T16 fora (D80) |
| Pescados, indústria (1020, 0311, 0312, 0321, 0322) | Real | C + B; T18 se compra de PF | T01 A | T13, T16 | alta | D80 |
| Pescados e carnes, atacado e peixaria (4634603, 4722902, 4634) | Real | B (energia, frio, aluguel, frete); T03; T04 com período confirmado | T01 A | T13, T16; crédito sobre ICMS-ST pago (Tema 1.231) | alta | D80 |
| Carnes, varejo e açougue (4722901) | Real | B; exclusões e CST no mix tributado | T01 A, só com porte | T13, T16 | alta, priorizar só com porte | D80 |
| Carnes, atacado e varejo (4634, 4722) | Presumido | Erro de CST; T04 (conforme UF); T12 | — | T01, T16 | baixa | D80 |
| Hortifrúti, atacado (4633) | Real | B; exclusões nas receitas tributadas | T01 A | T13, T16 | alta | D80 |
| Hortifrúti, varejo e sacolão (4724) | Real | B | T01 A | T13, T16 | **média, caso a caso** (era alta) | Sim: C4 e E3 |
| Hortifrúti (4633, 4724) | Presumido | Erro de CST; T12 | — | T01, T16 | baixa | D80 |
| Laticínios, indústria (1051, 1052) | Real | C + B; T02; T15 se incentivo de ICMS | T01 A | T13, T16 | alta | D80 |
| Laticínios e ovos, atacado e granja (4631, 4633802, 0155505) | Real | B | T01 A | T13, T16 | alta | D80 |
| Laticínios e ovos | Presumido | Exclusões, CST, T12 | — | T01, T16 | baixa | D80 |
| Atacado de insumos agropecuários (4683, 4692, 4623109) | Real | B | T01 A | T13, T16 | média | D80 |
| Atacado de insumos agropecuários | Presumido | Exclusões, T12 | — | T01, T16 | baixa | D80 |
| Atacado de alimentos e atacarejo (4691, 4637, 4639, 4632) | Real | Exclusões + B; T03; T04 | T01 A | T13, T16; monofásico (Tema 1.093); ICMS-ST pago (Tema 1.231) | alta | D80 |
| Atacado de alimentos e atacarejo | Presumido | Exclusões, T04, CST | — | T01, T08, T16 | média | D80 |
| **Supermercados (4711, 4712)** | Real | Exclusões, T03, T04, erro de CST; B só no que tiver crédito legítimo | **T01 fora** (catálogo de 15/10) | T01, T13, T16 | **média, caso a caso** (era alta) | Sim: C4 e E3 |
| Supermercados | Presumido | CST, exclusões, T04, T12 | — | T01, T16 | média | D80 |
| Padarias (1091101, 1091102, 4721102) | Real | Insumos (T02) da produção própria | T01 A só no insumo de produção própria | T13, T16 | média | D80 |
| Padarias (1091, 4721) | Presumido | Exclusões, CST, T12 | — | T01, T16 | baixa | D80 |
| Indústria de alimentos (10, 11) | Real | T02 + C; T08; T15 e T14 se incentivo; T12 | T01 A | T13, T16 | média | D80 |
| Indústria de alimentos | Presumido | Exclusões, T12, T15 | — | T01, T02, T08, T16 | baixa | D80 |
| **Agro e cooperativas adquirentes de produção rural** | Real | T18 (compra de PF); T02; T08 | T01 grãos (35%) | T13; **T19 como recuperação** | média | Sim: Funrural vira passivo (D86) [em aberto: D81 × D86, decisão do Luis] |
| Outros | Real | Insumos (T02) | — | T13, T16 | média | D80 |
| Outros | Presumido | Exclusões, CST, T12 | — | T16 | baixa | D80 |
| Qualquer CNAE | Simples | — | — | todas as teses de PIS/COFINS de crédito | vetar (V2) | — |
| Café (qualquer) | qualquer | — | — | fora da meta desde abr/2026 | vetar (V3) | — |

**Leitura de "PREV" na matriz.** A sigla PREV da `matriz.json` passa a significar só a T12 (verbas indenizatórias da CPP). A T13 (Sistema S) saiu da vitrine e virou triagem de passivo (D80).

### 2.2 O que decide cada tese no SPED (EFD-Contribuições, Guia Prático v1.35)
| Tese | Registro que decide | O que olhar | Leitura do sênior |
|---|---|---|---|
| Regime (todas) | **0110** | `COD_INC_TRIB` (não cumulativo = 1 ou 3) e método de apropriação; **0111** se há rateio pela receita bruta | Cumulativo puro não tem crédito: veto antes de tudo |
| T01 A e B (alíquota zero, manutenção e ressarcimento) | **C170/C181** (CST 06 nas saídas), **M400/M410** (PIS) e **M800/M810** (Cofins) (receitas com alíquota zero, isentas ou suspensas), **M100/M105** com código de crédito do **grupo 200** (Tabela 4.3.6), **1100/1500** | Peso das receitas CST 06 no total; crédito vinculado a receita não tributada; saldo e PER já pedidos (campo 14) e saldo final (campo 18) | Muita receita CST 06 e pouco crédito no grupo 200 = crédito não escriturado (oportunidade B); saldo no 1100 com PER já feito = recorrência, não perdido |
| T02 (insumos) e C (crédito presumido) | **M105** (base por tipo), **C170** e **C191** (aquisições com crédito), **F100**, **F120/F130** (ativo imobilizado); códigos **106/206/306** (presumido da agroindústria) | Quais despesas essenciais não geram crédito; presumido escriturado | Essencialidade e relevância (STJ Tema 779, citado no catálogo; não conferido hoje) |
| T08 (saldo em conta gráfica) | **1100/1500** | Saldo acumulado por período e por código de crédito | Prioridade até 31/12/2026: escrituração para preservar o saldo (LC 214, art. 378) |
| T03 (ICMS fora da base) | **C170/C181** (base de cálculo do PIS/COFINS com ICMS) e **M210/M610** | ICMS destacado ainda na base | Pacificada (Tema 69 STF, segundo o catálogo); risco é o período e a forma de cálculo |
| T04 (ICMS-ST fora da base) | EFD ICMS/IPI (ICMS-ST nas entradas) **[registro não conferido hoje]** | Volume de compras com ST | Modulação do Tema 1.125 em dúvida (E5): não prometer 5 anos |
| T12 (CPP, verbas indenizatórias) | Fora do SPED fiscal: eSocial e DCTFWeb | Rubricas e incidências | Fase 1 do piloto não lê folha (D3) |
| Veto monofásico | **C170** com CST de monofásico nas entradas | Crédito sobre custo de aquisição de monofásico | STJ Tema 1.093 veda: sai da hipótese |
| Veto ICMS-ST pago ao substituto | **C170** | Crédito sobre o ICMS-ST embutido no custo | STJ Tema 1.231 veda: sai da hipótese |

**Limite da fase 1 (D3):** o piloto não lê SPED nem folha; usa HubSpot e dados oficiais da Receita. Esta tabela diz **qual documento pedir** na ficha, e a leitura é do técnico.

## 3. Base normativa
| Norma ou precedente | Dispositivo ou dado oficial | Efeito na tabela | Situação (consulta em 22/10/2026) |
|---|---|---|---|
| STJ Tema 1.079 (REsp 1.898.532/CE e 1.905.870/PR) | Teto de 20 salários não se aplica ao Sistema S; julgado em 13/03/2024; acórdão de 02/05/2024; modulação só para quem ajuizou ou protocolou até o início do julgamento com decisão favorável | T13 fora (D80) | Oficial (STJ). Data de corte exata **[não confirmado]**: o catálogo diz 15/12/2020 e o consolidado diz 25/10/2023 |
| STJ Tema 1.390 | Teto não se aplica a INCRA, salário-educação, SEBRAE, SENAR e outras; julgado em 11/02/2026; acórdão de 19/02/2026; RE pendente | T13 fora, inclusive SENAR | Oficial (STJ) |
| STJ Tema 1.312 (REsp 2.151.903/RS e outros) | PIS e COFINS compõem a base do IRPJ/CSLL no Presumido; julgado em 11/03/2026; acórdão de 17/03/2026 | T16 fora (D80) | Oficial (STJ); RE pendente (ARE 1.601.807) |
| STJ Tema 1.093 | Vedado crédito sobre custo de aquisição de monofásico; art. 17 da Lei 11.033 só mantém crédito não vedado; acórdão de 04/05/2022, trânsito em 14/12/2023 | Veto do monofásico; não usar como apoio da T01 (E3) | Oficial (STJ) |
| STJ Tema 1.231 | ICMS-ST pago ao substituto não gera crédito de PIS/COFINS; julgado em 20/06/2024; acórdão de 25/06/2024 | Veto do crédito sobre ICMS-ST | Oficial (STJ) |
| STJ Tema 1.003 | Correção do ressarcimento só após 360 dias (Lei 11.457/2007, art. 24) | Ficha nunca soma correção no potencial | Oficial (STJ) |
| Lei 11.033/2004 | art. 17 | Base da variante B (manutenção de crédito) | Vigente até 31/12/2026 |
| Lei 11.116/2005 | art. 16 | Saldo trimestral ressarcível | idem |
| IN RFB 2.055/2021 | arts. 49, II, 53 e 55 | PER por trimestre, EFD antes | Vigente (compilação até IN 2.272/2025) |
| LC 214/2025 | arts. 378 e 542 | Fim do PIS/COFINS em 01/01/2027; saldo preservado se escriturado | Vigente |
| STF ADI 4.395 (Funrural) | Resultado proclamado em 15/10/2026 segundo o documento interno e uma fonte de imprensa; inconstitucional só antes de 2018; modulação e acórdão pendentes | T19 sai da recuperação e vai a passivo (D86) [em aberto: D81 × D86, decisão do Luis] | **[não confirmado no portal do STF]**; fontes divergem entre "até 2017" e "anterior a 2018" |
| Guia Prático EFD-Contribuições v1.35 (18/06/2021) | registros e Tabela 4.3.6 | Seção 2.2 | Oficial (sped.rfb.gov.br) |

## 4. Regras da casa
- **D80 (22/10/2026):** T13 (Sistema S) e T16 (PIS/COFINS fora do IRPJ/CSLL no Presumido) saem da vitrine; T13 vira triagem de passivo.
- **D86 (22/10/2026, aprovado a conciliar) × D81 (reprovado):** Funrural anterior a 2018 vira "Revisão do Funrural" em Gestão de Passivo, com êxito sobre débito cancelado e depósito levantado. O Recuperador não gera hipótese de recuperação de Funrural; caso agro com Funrural vai à aba Gestão de Passivo.
- **D22 (29/09/2026) e D14:** alíquota zero como hipótese principal em alimentos no Lucro Real, com risco e alternativa conservadora; sempre PER, nunca DCOMP.
- **Catálogo de 15/10/2026:** T01 exclui mercado, supermercado e café.
- **C4 (consolidado, 22/10/2026):** supermercado e sacolão em "análise caso a caso" até o tributarista decidir. Hoje o `matriz.json` dá "alta"; a ficha deve dizer "caso a caso".
- **D3 (29/09/2026):** fase 1 sem SPED nem folha.
- **D2 (29/09/2026):** o resultado é o valor validado pela Geovana; a tabela não estima valor.
- **Decisão do Luis (29/09/2026, `matriz.json`):** a tese de aquisições com alíquota zero não é vetada; os Temas 1.093 e 1.231 são.
- **Em aberto:** quem altera o `matriz.json` (Tributário ou Geovana) e com que aprovação; T01 em supermercado; data de corte da modulação da T13.

## 5. Método
1. **Toda segunda, antes do lote:** conferir se houve decisão nova (D-número) ou errata que mexa em tese. Se houve, atualizar esta tabela com data e fonte.
2. **Para cada caso da fila:** ler CNAE oficial e regime. Regime vazio = "confirmar regime"; Simples = V2; café = V3.
3. **Achar a linha** pelo prefixo mais longo do CNAE (como o `fila.py`).
4. **Aplicar as correções de 22/10:** retirar T13 e T16 de qualquer hipótese; Funrural nunca como recuperação; supermercado e sacolão com "caso a caso" e sem T01; monofásico e ICMS-ST pago fora.
5. **Escrever a hipótese** na ordem: tese de caixa → tese de risco (com alternativa) → o que fica fora e por quê.
6. **Indicar o registro que decide** (seção 2.2) como "documento a pedir" e "o que conferir primeiro".
7. **Propor a alteração do `matriz.json`** quando a mesma correção aparecer em 3 ou mais fichas no mês: diff com D-número, levado à Geovana e ao Tributário. Mudanças já propostas:
   - Supermercados (4711, 4712), Real: aderência "alta" → "média"; retirar `tese_save` (T01) e anotar "catálogo de 15/10/2026 e C4".
   - Hortifrúti varejo e sacolão (4724), Real: "alta" → "média, caso a caso" (C4).
   - Todas as linhas: observação "T13 e T16 fora (D80)"; PREV = T12.
   - Nova linha agro e cooperativas adquirentes (0161, 4622, 4623 e afins **[prefixos a definir pelo Tributário]**): T18 + T02; Funrural → passivo (D86). [em aberto: D81 × D86, decisão do Luis]
8. **Revisão do gerente** e registro `revisao` na entrega.

**Limites:** nenhuma linha muda sem D-número ou errata; 3 ocorrências no mês disparam proposta de mudança; tese "contrária" (T09, T13) nunca entra como hipótese da ficha.

## 6. Perguntas de diagnóstico
- **Qual é o regime da empresa em cada ano do período (ECF e DCTF)?**
  Regime muda a linha da tabela; Presumido derruba T01, T02 e T08.
- **O CNAE oficial é o mesmo da atividade real (vende mais o quê)?**
  CNAE de atacado com receita de indústria muda a tese (C entra).
- **Qual a parcela das vendas com alíquota zero, isenção ou suspensão (CST 06 e afins)?**
  Decide se há saldo credor e se a variante B vale a análise.
- **A empresa já escritura crédito no grupo 200 da Tabela 4.3.6?**
  Se sim, o caso é de PER ou recorrência; se não, de crédito não escriturado.
- **Há saldo no 1100/1500 e PER já transmitido?**
  Evita propor o que já foi pedido.
- **Revende produtos monofásicos (bebidas, higiene, autopeças)?**
  Parte do crédito cai no veto do Tema 1.093.
- **Compra com ICMS-ST?**
  Abre T04 e fecha o crédito sobre o ST pago (Tema 1.231).
- **É supermercado ou mercearia?**
  T01 fora; análise caso a caso.
- **Compra de produtor rural pessoa física?**
  Abre T18 e o gatilho de Funrural como passivo.
- **Tem benefício de ICMS concedido pelo Estado (crédito presumido)?**
  Abre T15 e T14, com ato concessório.
- **Tem ação judicial ou pedido sobre Sistema S antes do corte da modulação?**
  É o único caso em que T13 aparece, como triagem de passivo e proteção, nunca como venda.
- **Está no Presumido e alguém já ofereceu "PIS/COFINS fora do IRPJ"?**
  T16 perdeu o objeto (Tema 1.312): alerta de risco ao cliente.
- **A folha é relevante e com muitas rubricas?**
  T12, mas fora da fase 1 (D3).

## 7. Armadilhas e sinais de alerta
- **Usar o Tema 1.093 como apoio da alíquota zero.** É adverso por analogia (E3).
- **Dar "alta" a supermercado** porque o histórico de ganhos é bom. O catálogo exclui; vale "caso a caso" (C4).
- **Manter T13 ou T16 em ficha antiga.** Revisar fichas abertas depois de 22/10/2026.
- **Oferecer Funrural como recuperação de 5 anos.** Pagamentos até 2017 em regra estão prescritos; o produto agora é passivo (D86). [em aberto: D81 × D86, decisão do Luis]
- **Confundir regime do ano atual com o do período.** A tese depende do regime de cada ano.
- **Pedir "SPED" genérico.** A ficha diz o registro e o período.
- **Escalar ao Tributário:** CNAE fora da tabela com volume relevante; caso agro com Funrural; supermercado com proposta de T01; qualquer tese contrária pedida pelo parceiro.

## 8. Casos de referência
### Caso 1 · Supermercado em "alta" (interno, anonimizado)
Situação: a matriz de 29/09/2026 classifica supermercado no Lucro Real como "alta" com T01; o catálogo de 15/10/2026 exclui supermercado da T01. Leitura: o look-alike puxava supermercados para o topo da fila com uma tese que a Save não oferece a eles. O que foi feito: C4 registrou o conflito; esta tabela rebaixa para "caso a caso" e tira a T01; proposta de diff ao Tributário.

### Caso 2 · Sistema S depois do Tema 1.079 (público)
Situação: empresas de folha relevante buscavam limitar a base das contribuições a terceiros a 20 salários. Leitura: o STJ (Tema 1.079, acórdão de 02/05/2024) afastou o teto e modulou só para quem já tinha ação ou pedido com decisão favorável; o Tema 1.390 (19/02/2026) estendeu a INCRA, SEBRAE, SENAR e outras. O que foi feito: D80 tirou a T13 da vitrine; ela só aparece como triagem de passivo.

### Caso 3 · PIS/COFINS na base do Presumido (público)
Situação: tese T16 oferecida ao Lucro Presumido. Leitura: o STJ (Tema 1.312, julgado em 11/03/2026) decidiu que PIS e COFINS compõem a base do IRPJ/CSLL no Presumido. O que foi feito: D80 tirou a T16; a ficha de cliente do Presumido não a cita.

### Caso 4 · Funrural vira passivo (interno e público)
Situação: catálogo citava "Tema 1.079" como base do Funrural (erro). Leitura: a decisão relevante é a ADI 4.395 (15/10/2026, segundo o documento interno), que atinge só o período anterior a 2018, cujos pagamentos em regra estão prescritos. O que foi feito: D86 lançou a revisão do Funrural em Gestão de Passivo; o Recuperador manda esses casos para a aba própria.

## 9. Fronteiras e escalonamento
- **Não é dele:** decidir tese nova ou mudar risco de tese (Tributário e tributarista humano); alterar o script `fila.py`; aprovar o diff do `matriz.json` (Geovana com o Tributário); falar com parceiro ou cliente (D5).
- **Passa para:** Redator da ficha (usa a tabela); `depto-tributario` (mudança de tese, CNAE novo); `revisor-diagnostico` (mesma matriz, regras V1 a V15).
- **Exige humano:** toda mudança de aderência ou de tese; toda tese controvertida em ficha.

## 10. Atualização
- Última revisão: 22/10/2026.
- Fontes: processo.stj.jus.br (Temas 1.003, 1.079, 1.093, 1.231, 1.312, 1.390), sped.rfb.gov.br (Guia Prático v1.35), planalto.gov.br (Leis 11.033, 11.116, 11.457; LC 214), base interna (catálogo de 15/10/2026, consolidado e revisão do Tributário de 22/10/2026, decisões D3, D14, D22, D80, D81, D86).
- O radar semanal vigia: EREsp 2.215.482 (alíquota zero), acórdão e modulação da ADI 4.395, modulação do Tema 1.125 (T04), Tema 843 do STF (T15), nova versão do Guia Prático da EFD-Contribuições e regulamentação do art. 378 da LC 214.
