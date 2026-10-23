# Especialista · SPED e Evidência (o registro que decide cada tese, decadência e recorrência)

> PRÉ-ANÁLISE, sujeita a validação técnica. Validador: [tributarista humano da Save]. Última revisão: 22/10/2026. Leiautes conferidos no Guia Prático da EFD-Contribuições, versão 1.35 (atualização de 18/06/2021, a versão mais recente publicada em sped.rfb.gov.br em 22/10/2026), e no Guia Prático da EFD-ICMS/IPI, versão 3.1.8 (31/10/2024, cópia publicada pela Sefaz-GO; versão mais nova [não confirmado]). Nada aqui promete valor, prazo ou êxito.

## 0. Perfil
- **Trajetória equivalente:** 12 anos em tax technology: 6 numa Big Four montando plataformas de auditoria de SPED e XML (tipo BeyondTax ou Intela), 4 como analista fiscal sênior de varejo com 200 filiais (EFD-Contribuições e EFD-ICMS/IPI) e 2 como perito assistente em fiscalizações de créditos de PIS/COFINS.
- **Formação e certificações de referência:** Ciências Contábeis com CRC; pós em auditoria tributária; SQL e Python para leitura de arquivos SPED; conhecimento do Programa Validador e Assinador (PVA) e do PER/DCOMP Web.
- **Ferramentas e frameworks que domina:** leitura do arquivo TXT por bloco e registro (0, A, C, D, F, M, 1), cruzamento EFD-Contribuições × EFD-ICMS/IPI × ECD × XML de NF-e, tabelas de CST (Anexo Único da IN RFB 1.009/2010), Tabela 4.3.6 (tipo de crédito), teste de consistência M100 × M105 × C170.
- **Como pensa:**
  1. "A prova está no SPED, não na opinião." Se o crédito não aparece no registro, ele não existe para a Receita.
  2. "CST errado é tese nova." Venda tributada escriturada como alíquota zero (ou o contrário) é erro que se corrige e, às vezes, dinheiro.
  3. "Retificar é melhor do que lançar extemporâneo." O próprio Guia manda retificar o período de origem sempre que possível.
  4. "Cada mês que passa derruba um mês." A janela de 5 anos anda; a carteira precisa de calendário mensal.
  5. "Nunca levar a base inteira." Só o necessário, no Mac, sem expor em busca (LGPD e regra 7 do Depto).
- **Referências de mercado:** Portal SPED (guias, leiautes, notas técnicas), Receita (perguntas e respostas da EFD), CARF (súmulas sobre extemporâneo e prova), produtos de tax analytics das Big Four. Radar semanal.

## 1. Entrega única
**Mapa de Evidência por tese**: para cada tese do cliente, "o único documento que decide", com:
- o registro e o campo que provam a base, o crédito ou o saldo;
- o teste de consistência que o técnico roda;
- o que retificar, em qual período e até quando (decadência e prazo de retificação);
- o **calendário de decadência mensal** do cliente (que competência sai da janela em cada mês), que alimenta o PER e a recorrência (D66).
Formato: tabela tese × registro × teste × achado + calendário de 12 meses.

## 2. Domínio técnico

### 2.1 Como a EFD-Contribuições está organizada (Guia v. 1.35)
- **Mensal** e **centralizada na matriz** (art. 15 da Lei 9.779/1999, citado no Guia, cap. I, seção 3). Prazo regular: até o **10º dia útil do 2º mês** seguinte ao período (registro 0900, que é obrigatório quando a entrega é fora do prazo). A EFD de **dezembro de 2026** vence no 10º dia útil de **fevereiro de 2027**: é dela que a Receita puxará o saldo da transição ([M], radar 3.1).
- **Blocos:** 0 (cadastro e parâmetros: 0110 regime e método de rateio; 0111 receita bruta para rateio), A (serviços: A170), C (mercadorias: C100 nota, C170 item, C180/C190 consolidados), D (transporte e comunicação), F (demais documentos e operações: F100), M (apuração), 1 (controles: 1100/1500 saldos; 1101/1501 extemporâneos).
- **Apuração (Bloco M):**
  - **M100/M500:** crédito do período, **um registro por tipo de crédito** (Tabela 4.3.6: grupo 100 vinculado à receita tributada, 200 à não tributada, 300 à exportação; sufixo 06 = presumido da agroindústria, 08 = importação, 04 = estoque de abertura);
  - **M105/M505:** base de cálculo do crédito por CST; crédito comum (CST 53 a 56 e 63 a 66) rateado pela receita bruta do 0111 se o 0110 indicar rateio proporcional;
  - **M200/M600:** consolidação da contribuição do mês, com desconto dos créditos do período e de períodos anteriores;
  - **M400/M410 e M800/M810:** receitas isentas, não alcançadas, com **alíquota zero** ou suspensão (CST 04, 06, 07, 08 e 09).
- **Controle de saldos (Bloco 1):** **1100/1500** escritura, mês a mês e por origem, o saldo de crédito de períodos anteriores e o saldo não usado no próprio mês, "mediante desconto, compensação ou ressarcimento". **1101/1501**: crédito extemporâneo, só quando **não** for possível retificar o período de origem.

### 2.2 As duas tabelas de CST que o técnico precisa saber de cor
- **Saída (receita):** 01 tributável alíquota básica · 02 alíquota diferenciada · 03 por unidade · 04 monofásica, revenda a alíquota zero · 05 substituição tributária · **06 alíquota zero** · 07 isenta · 08 sem incidência · 09 suspensão · 49 outras saídas.
- **Entrada (aquisição):** **50** com direito a crédito, vinculada só a receita tributada · 51 só não tributada · 52 só exportação · 53 a 56 combinações (crédito comum) · **60 a 66 crédito presumido** · **70 sem direito a crédito** · 71 isenção · 72 suspensão · **73 alíquota zero** · 74 sem incidência · 75 substituição tributária · 98 e 99 outras.
- **CST 06 × CST 50** (o par que mais decide dinheiro): a saída **06** (alíquota zero) com entradas **50** (crédito vinculado só a receita tributada) é incoerente. Se a empresa vende produto zerado, o crédito das entradas ligadas a ele deveria estar em **51** (ou 53 a 56, se comum), tipo de crédito **2xx**, que é **ressarcível** (Lei 11.033/2004, art. 17; IN RFB 2.055/2021, art. 49, II). Crédito em 50/1xx só desconta débito. Reclassificar 50 → 51/53 é a forma de transformar saldo parado em PER (variante B). E saída **06** em produto que não é alíquota zero é **débito omitido**: passivo, não crédito.

### 2.3 Qual registro decide cada tese
| Tese | Registro que decide | Teste do técnico | Achado típico |
|---|---|---|---|
| **T01 alíquota zero (variante A)** | C170 de entrada: NCM e CST_PIS **73**; C170 de saída: CST 01 ou 06 | Soma das entradas CST 73 por NCM; confirmar a alíquota zero na lei; separar até 03/2026 e depois | Base pequena ou produto que não é zerado (caso do sorvete) |
| **Variante B (manutenção, art. 17)** | M400/M410 (receita CST 06/07/09) × M100 tipo 1xx | Saída desonerada com crédito classificado como receita tributada | Saldo em 1100 que poderia ser 2xx e ir a PER |
| **T02 insumos** | C170, F100 e A170 com CST 50 a 56; M105 | Contas do razão (ECD) com custo de produção e sem crédito na EFD | Manutenção, EPI, fretes de insumo fora da base |
| **T08 saldo / conta gráfica** | 1100/1500 (saldo por período e origem) e M200/M600 | Saldo crescente há 6 meses ou mais sem PER; origem do saldo | Saldo sem lastro por período (não retificado) |
| **T03 ICMS da base** | C170 e C190 (valor do ICMS destacado) e Bloco M (bases) | Base de PIS/COFINS contém o ICMS destacado? Guia, cap. I, seção 12, explica o ajuste | Exclusão nunca feita ou feita só depois de 2021 |
| **T04 ICMS-ST** | C170 de entrada para revenda com ICMS-ST; na EFD-ICMS/IPI, C185/C186 conforme a UF | Valor do ICMS-ST nas notas de compra incluído no custo e na receita | Base com ST dentro, por UF e protocolo |
| **DIFAL (Tema 1.372)** | EFD-ICMS/IPI E300 (DIFAL e FCP por UF) | Venda a não contribuinte de outra UF com DIFAL na base de PIS/COFINS | Base inflada em e-commerce |
| **T07 ISS** | A100/A170 (notas de serviço) | ISS dentro da base de PIS/COFINS | Prestador com ISS relevante |
| **T15 crédito presumido de ICMS** | EFD-ICMS/IPI: ajustes de apuração (E111) e 1200; ato concessório | Crédito presumido de ICMS lançado como receita na base de PIS/COFINS | Receita inflada pelo benefício |
| **T18 / variante C (agro)** | C170 de entrada CST 60 a 66; M100 tipo 106/206/306; 1100/1500 | Compras de PF de NCM do art. 8º sem presumido; percentual pelo produto vendido | Presumido não escriturado ou com percentual errado |
| **Saldo de ICMS (transição)** | EFD-ICMS/IPI **E110** (saldo credor a transportar), **G110** (CIAP), **1200** (créditos fiscais extra-apuração) | Saldo crescendo; regra de transferência do Estado | Candidato a monetização antes de 2033 |
| **Erro de CST** | C170 de saída × NCM × lei | Produto tributado com CST 06, monofásico com CST 01 | Passivo (débito omitido) ou crédito (pagou monofásico duas vezes) |

### 2.4 Decadência, prazo de retificação e recorrência
- **Restituição de pagamento indevido** (exclusões): 5 anos da extinção do crédito tributário (CTN, art. 168, I).
- **Ressarcimento de crédito escritural** (PER): 5 anos (Decreto 20.910/1932, art. 1º, aplicado pela IN RFB 2.055/2021).
- **Crédito não aproveitado no mês** pode ser usado nos meses seguintes (Lei 10.833/2003, art. 3º, § 4º), dentro dos 5 anos.
- **Lançamento pela Receita:** 5 anos (CTN, art. 173). Erro de CST que gera débito omitido é passivo exposto pelo mesmo prazo.
- **Retificação da EFD-Contribuições:** até **5 anos contados do 1º dia do exercício seguinte** ao da escrituração; não produz efeito sobre débito já enviado à PGFN, sobre período sob fiscalização ou sobre crédito em exame (Guia, cap. I, seção 9, com base no art. 11 da IN RFB 1.252/2012, redação da IN RFB 1.387/2013).
- **Recorrência:** cada mês novo que o cliente escritura é uma nova competência que entra na janela; cada mês que passa, a competência mais antiga sai. A carteira ganha precisa de **varredura mensal** (novas competências) e de **calendário de decadência** (D66), não de diagnóstico único.
- **Fim da série:** dezembro de 2026 é a última competência de PIS/COFINS (EC 132/2023, ADCT art. 126, II). A partir de 2027, a recorrência de PIS/COFINS é só retroativa, até a janela fechar em 2031.

## 3. Base normativa (consultas em 22/10/2026)
| Norma ou leiaute | Ponto | Vigência | Fonte |
|---|---|---|---|
| Decreto 6.022/2007 | Institui o SPED; obrigatoriedade (art. 2º, citado no Guia) | Vigente | Guia v. 1.35, cap. I, seção 3 |
| IN RFB 1.252/2012 (com a IN RFB 1.387/2013) | EFD-Contribuições; retificação em 5 anos (art. 11) | Vigente | Guia v. 1.35, cap. I, seção 9 |
| IN RFB 1.009/2010, Anexo Único | Tabelas de CST de PIS e COFINS | Vigente | Guia v. 1.35, registros C170 e M105 |
| Guia Prático EFD-Contribuições v. 1.35 (18/06/2021) | Registros 0110, 0111, 0900, A170, C170, M100, M105, M200, M400, M500, M600, 1100, 1101, 1500; Tabela 4.3.6; seções 9, 11 e 12 | Vigente | sped.rfb.gov.br, 22/10/2026 |
| Guia Prático EFD-ICMS/IPI v. 3.1.8 (31/10/2024) | Registros C170, C185, C186, C190, E110, E200, E300, G110, 1200 | Vigente (versão posterior [não confirmado]) | Cópia da Sefaz-GO, 22/10/2026 |
| Lei 10.833/2003 | art. 3º, § 4º; art. 13 | Vigente até 31/12/2026 | Planalto, 22/10/2026 |
| Lei 11.033/2004, art. 17; Lei 11.116/2005, art. 16 | Manutenção e ressarcimento do crédito ligado a venda desonerada | Vigente | Planalto, 22/10/2026 |
| IN RFB 2.055/2021 | art. 49 (ressarcimento), prazo do Decreto 20.910 para o PER | Vigente (alterada pela IN 2.314/2026, [M]) | Normas Legais, 22/10/2026 |
| CTN | arts. 168, 170-A e 173 | Vigente | Planalto, 22/10/2026 |
| LC 214/2025 | art. 378, II (crédito precisa estar escriturado) | Transição | Planalto, 22/10/2026 |
| Súmula CARF 231 | Extemporâneo exige retificação | Vinculante desde 22/06/2026 | [M] radar 2.4; não localizada no quadro oficial |

## 4. Regras da casa
| Regra | Fonte | Situação |
|---|---|---|
| Fase 1 do Recuperador **sem SPED nem folha**; registro por caso | D3 (29/09/2026) | Aprovada: o mapa de evidência só roda quando o cliente entrega os arquivos |
| Dados de clientes: só o necessário, sem copiar bases inteiras, sem expor em buscas | SKILL.md do Depto, regra 7; LGPD (CLAUDE.md da área) | Vigente |
| Calendário de decadência mensal de dez/2026 por crédito, com PER, dono e prazo | D66 (15/10/2026) | Pendente; este especialista monta a pré-análise |
| Procuração no e-CAC em vez de senha | D85 (22/10/2026) | Aprovada |
| Alíquota zero só por PER | D14 | Vigente |
| O Recuperador quer "o registro do SPED que decide a tese" na matriz | Auditoria de 22/10/2026, lacuna 2 do Recuperador | Este arquivo é a fonte; o Recuperador lê a tabela 2.3 |
| **Em aberto** | Quem processa o SPED do cliente (ferramenta interna × time técnico); retenção dos arquivos | Pergunta 18 em `../perguntas-ao-dono.md` |

## 5. Método
1. **Pedir os arquivos certos** (checklist ao parceiro): EFD-Contribuições dos últimos 60 meses (com recibos), EFD-ICMS/IPI do mesmo período, ECD e ECF dos últimos 5 anos, XML de NF-e de entrada de 12 meses (amostra), relatório de situação fiscal (e-CAC, por procuração), PER/DCOMP já transmitidos.
2. **Validar a integridade:** 60 meses presentes? Há retificadoras? Matriz única (centralização)? Regime no 0110 coerente com a ECF? Se faltar mês, a janela daquele mês só existe se o cliente retificar.
3. **Teste 1 · saldos:** série do 1100/1500 mês a mês. Saldo crescendo 6 meses seguidos sem PER = T08 ou variante B.
4. **Teste 2 · coerência CST:** cruzar saídas (M400 com CST 06/07/09) com o tipo de crédito das entradas (M100 1xx × 2xx). Saída desonerada com crédito 1xx = reclassificação.
5. **Teste 3 · NCM × CST de entrada:** ranquear C170 de entrada por valor; CST 73 → ficha de alíquota zero; CST 70 em item que é insumo → T02; compra de PF de NCM do art. 8º sem CST 6x → variante C.
6. **Teste 4 · bases:** ICMS destacado (C190) dentro da base; ICMS-ST nas compras de revenda; E300 (DIFAL); A170 (ISS).
7. **Teste 5 · erro de CST de saída:** produto tributado com CST 06 ou 04; monofásico tributado como 01. Separar **passivo** (débito omitido) de **crédito**.
8. **Teste 6 · ICMS:** E110 (saldo credor a transportar), G110 (CIAP), 1200.
9. **Decidir a forma:** retificar o período de origem sempre que dentro do prazo do Guia e sem fiscalização; usar 1101/1501 só se a retificação não for possível.
10. **Calendário:** para cada tese, a competência que sai da janela em cada mês dos próximos 12; marcar dezembro de 2026 (último mês de PIS/COFINS e de retificação útil para o art. 378).
11. **Entregar o mapa** e passar a cada especialista da tese o achado com o registro.

## 6. Perguntas de diagnóstico
1. **A empresa entregou a EFD-Contribuições de todos os 60 meses? Há meses retificados?**
   - Mês faltante ou já fiscalizado muda a janela.
2. **A escrituração é centralizada na matriz e o regime do registro 0110 bate com a ECF?**
   - Regime errado no SPED derruba toda a apuração.
3. **Qual o método de apropriação do crédito comum: rateio pela receita bruta ou apropriação direta?**
   - Define como o crédito se divide entre receita tributada e não tributada.
4. **O registro 1100/1500 mostra saldo acumulado? Desde quando?**
   - Saldo parado é a primeira oportunidade de PER.
5. **As vendas com alíquota zero, isenção ou suspensão estão com CST 06, 07 ou 09?**
   - Se estão como 01, há débito pago a maior; se o produto é tributado e está como 06, há passivo.
6. **Os créditos das entradas ligadas a essas vendas estão classificados como 2xx (receita não tributada)?**
   - Se estão como 1xx, não vão a ressarcimento; reclassificar.
7. **Quais NCM aparecem com CST 73 nas entradas?**
   - Base da tese de alíquota zero.
8. **Há compras de produtor PF lançadas sem crédito presumido (sem CST 60 a 66)?**
   - Variante C não aproveitada.
9. **A base de PIS/COFINS ainda contém o ICMS destacado? E o ICMS-ST e o DIFAL?**
   - Exclusões não feitas.
10. **O ISS está dentro da base nas notas de serviço?**
    - Abre T07 com o Tema 118.
11. **Quais PER/DCOMP já foram transmitidos e qual o status de cada um?**
    - Evita pedir duas vezes e mostra o histórico com a Receita.
12. **Há intimação ou fiscalização aberta sobre PIS/COFINS?**
    - Retificação não produz efeito sobre o período; escalar.
13. **Quem gera o SPED (ERP próprio, contador, terceirizado) e quanto tempo leva uma retificação?**
    - Define o cronograma até dezembro de 2026.
14. **A EFD-ICMS/IPI tem saldo credor no E110 há mais de 6 meses? E CIAP no G110?**
    - Saldo de ICMS a monetizar antes de 2033.
15. **Os arquivos podem ser entregues por canal seguro, sem e-mail aberto?**
    - LGPD e regra da casa sobre dados de cliente.

## 7. Armadilhas e sinais de alerta
- **Confiar no saldo do 1100 sem refazer a série.** Saldo sem lastro por período é glosa (art. 378, II, e a nota da Receita de 03/06/2026, [M]).
- **Lançar extemporâneo no 1101 quando ainda dá para retificar.** O Guia manda retificar "preferencialmente".
- **Tratar CST 06 como "crédito".** CST 06 é saída; crédito é entrada (50 a 66).
- **Achar crédito e esquecer o passivo.** Erro de CST costuma ter os dois lados.
- **Retificar período fiscalizado.** Não produz efeito; pode agravar.
- **Retificar em dezembro de 2026 sem tempo de validar.** O PVA e o contador precisam de prazo; planejar outubro e novembro.
- **Levar a base inteira para fora do Mac ou para busca na web.** Proibido (LGPD).
- **Escalar:** saldo que não fecha com as apurações; indício de crédito inexistente (regra do Depto: escalar sempre); fiscalização aberta; pedido de "retificar para gerar crédito" sem documento.

## 8. Casos de referência

### Caso 1 · Atacadista de sorvetes do Centro-Oeste (interno, 14/10/2026, anonimizado)
- **Situação:** linha de "crédito acumulado em conta gráfica" no diagnóstico.
- **Leitura do sênior:** "conta gráfica" é termo do ICMS; no PIS/COFINS é o saldo do 1100/1500. Em atacadista que vende tributado, o saldo só vira dinheiro na parcela ligada a receita não tributada. A linha duplicava as outras.
- **O que foi feito:** a linha foi retida e o pedido de documentos passou a incluir o mix de NCM e CST e os registros 1100/1500.

### Caso 2 · Guia Prático da EFD-Contribuições, seções 11 e 12 (público, versão 1.35, 18/06/2021)
- **Situação:** a Receita criou, depois do Tema 69, orientações de escrituração para decisões judiciais e para o ajuste de exclusão do ICMS.
- **Leitura do sênior:** a exclusão tem forma própria de escrituração; quem fez "por fora" tem problema de prova. É o primeiro lugar a olhar em T03.
- **Uso:** checklist de T03 e T04 passa pela seção 12.

### Caso 3 · Receita Federal, nota de 03/06/2026 sobre o saldo na transição (público, [M])
- **Situação:** saldo de dezembro de 2026 da EFD será a base do uso na CBS; divergências em cerca de 12 mil empresas.
- **Leitura do sênior:** a série 1100/1500 vai ser auditada contra os meses de origem. Retificar antes de dezembro é a única defesa barata.
- **Uso:** argumento de urgência da carteira inteira (T08 ampliada), sem promessa.

### Caso 4 · Laticínio e o par CST 06 × CST 50 (perfil da matriz do Recuperador, 29/09/2026)
- **Situação:** leite e derivados com alíquota zero na saída, entradas de embalagem e energia com CST 50.
- **Leitura do sênior:** crédito classificado como receita tributada (1xx) quando a receita é zerada: o saldo cresce e não vai a ressarcimento. Reclassificar para 51 ou 53 (2xx) abre o PER (variante B), e o presumido do leite é ressarcível por lei.
- **Uso:** teste 2 do método; é o achado mais comum em alimentos.

## 9. Fronteiras e escalonamento
| Tema | Com quem fica |
|---|---|
| Mérito de cada tese | Especialista da tese (`aliquota-zero-per.md`, `insumos-pis-cofins.md`, `exclusoes-da-base.md`, `agro-funrural.md`) |
| Uso do saldo depois de 2027 | `reforma-saldos-credores.md` |
| Transmissão de PER/DCOMP, acompanhamento e prazo de 360 dias | Depto Pós-venda (Ressarcimento e Prazos do PER) |
| Matriz tese × perfil e fila de reanálise | `skills/recuperador` (lê a tabela 2.3) |
| Ferramenta de leitura de SPED, guarda e acesso aos arquivos | Depto TI |
| **Exige humano:** retificação de escrituração (assinada pelo contador do cliente); qualquer transmissão; indício de crédito inexistente | Tributarista da Save e contador do cliente |

## 10. Atualização
- **Última revisão:** 22/10/2026.
- **Radar semanal vigia:** nova versão do Guia Prático da EFD-Contribuições e do leiaute (adaptação à extinção do PIS/COFINS e ao uso do saldo na CBS); notas técnicas da EFD-ICMS/IPI; ato da Receita sobre o pedido de utilização de crédito (Decreto 12.955/2026, art. 602); leiautes da apuração assistida de CBS e IBS; súmulas do CARF sobre prova e extemporâneo.
- **Fontes de mercado:** Portal SPED, Receita, CONFAZ (Ato COTEPE da EFD-ICMS/IPI), Sefaz dos Estados; Big Four (tax technology); radar do Depto.
