// Apresentação à presidência da Cooperativa Santa Clara, versão 2: todo o ecossistema (21/10/2026).
// Roteiro do Luis: dados de mercado > dificuldades do setor (fontes oficiais) > espelho na empresa > como ajudar > resultados possíveis.
// Foco: mais lucro e mais margem. Uso: NODE_PATH=<node_modules> node gerar_deck_santa_clara_ecossistema.js <deck_dados_v2.json> <saida.pptx>
const fs = require("fs");
const path = require("path");
const S = require(path.join(__dirname, "../../../departamentos/marketing-marca/padrao/pptx_save.js"));
const { C, E, F, FM, W, H, MX, GRAFICO } = S;
const DADOS = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const ibge = DADOS.leite;
const OUT = process.argv[3];

const pres = S.novaApresentacao("Mais lucro e mais margem · Ecossistema Santa Clara");
const TOPO = 2.0, FIM = 6.78;

function fonte(s, texto) {
  s.addText("Fonte: " + texto, { x: MX, y: 6.5, w: W - 2 * MX, h: 0.4, fontFace: F, fontSize: 8, color: C.texto_3, margin: 0, valign: "bottom", isTextBox: true });
}
function cartao(s, x, y, w, h, tit, corpo, op = {}) {
  s.addShape("roundRect", { x, y, w, h, fill: { color: op.fundo || C.cartao }, line: { color: C.borda, width: 0.75 }, rectRadius: 0.08 });
  s.addText(tit, { x: x + 0.2, y: y + 0.14, w: w - 0.4, h: 0.4, fontFace: F, fontSize: op.tt || 13, bold: true, color: C.texto, margin: 0, valign: "top", isTextBox: true });
  s.addText(corpo, { x: x + 0.2, y: y + 0.58, w: w - 0.4, h: h - 0.7, fontFace: F, fontSize: op.fs || 10.5, color: C.texto_2, margin: 0, valign: "top", isTextBox: true, paraSpaceAfter: 3 });
}
function tabela(s, x, y, colW, cab, linhas, op = {}) {
  const fs_ = op.fs || 10;
  const head = cab.map(c => ({ text: c, options: { bold: true, color: E.ouro, fill: { color: E.fundo }, fontFace: FM, fontSize: 8.5, valign: "middle" } }));
  const rows = [head].concat(linhas.map((l, i) => l.map((t, j) => ({ text: t, options: { bold: j === 0, color: C.texto, fill: { color: i % 2 ? C.fundo : C.cartao }, fontFace: F, fontSize: fs_, valign: "top" } }))));
  s.addTable(rows, { x, y, w: colW.reduce((a, b) => a + b, 0), colW, border: { type: "solid", pt: 0.5, color: C.borda }, margin: [0.05, 0.08, 0.05, 0.08], autoPage: false });
}
const nova = (rot, tit) => { const s = pres.addSlide({ masterName: "SAVE_CLARO" }); S.titulo(s, rot, tit); return s; };
const fmt = (n, d = 1) => n.toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });


// ───────────── 1. CAPA
let s = pres.addSlide({ masterName: "SAVE_CAPA" });
s.addText("APRESENTAÇÃO À PRESIDÊNCIA · OUTUBRO DE 2026", { x: MX, y: 2.3, w: 10, h: 0.35, fontFace: FM, fontSize: 12, color: E.ouro, charSpacing: 2, margin: 0 });
s.addText("Mais lucro e mais margem em todo o ecossistema da Cooperativa Santa Clara", { x: MX, y: 2.75, w: 11.4, h: 1.7, fontFace: F, fontSize: 38, bold: true, color: E.texto, margin: 0, valign: "top" });
s.addText("Do campo à gôndola: o mercado, as dificuldades de cada negócio, o espelho na cooperativa, como podemos ajudar e os resultados possíveis", { x: MX, y: 4.6, w: 10.8, h: 0.9, fontFace: F, fontSize: 16, color: E.texto_2, margin: 0, valign: "top" });
s.addText("PRÉ-ANÁLISE · ESTIMATIVAS PRELIMINARES SUJEITAS A VALIDAÇÃO TÉCNICA · SEM PROMESSA DE VALOR, PRAZO OU ÊXITO", { x: MX, y: 6.55, w: 11.5, h: 0.3, fontFace: FM, fontSize: 8.5, color: E.ouro, margin: 0 });

// ───────────── 2. ROTEIRO
s = nova("Nosso ponto de partida", "Todo o trabalho serve a um objetivo: mais lucro e mais margem");
const passos = [["1", "O mercado", "O que os dados oficiais mostram nos negócios em que a Santa Clara atua"], ["2", "As dificuldades", "Onde a margem está sob pressão, negócio por negócio"],
  ["3", "O espelho", "Como cada pressão chega ao ecossistema da cooperativa, com o que é público"], ["4", "Como podemos ajudar", "Uma esteira única, em que o fim de um passo abre o próximo e um negócio abre outro"],
  ["5", "Os resultados possíveis", "O que cada fração de margem, de prazo e de custo de capital representa"]];
passos.forEach((p, i) => {
  const x = MX + i * 2.45;
  s.addShape("roundRect", { x, y: TOPO + 0.2, w: 2.3, h: 3.0, fill: { color: i === 4 ? C.ouro_suave : C.cartao }, line: { color: C.borda, width: 0.75 }, rectRadius: 0.08 });
  s.addText(p[0], { x: x + 0.2, y: TOPO + 0.35, w: 1, h: 0.6, fontFace: FM, fontSize: 28, bold: true, color: C.ouro_texto, margin: 0 });
  s.addText(p[1], { x: x + 0.2, y: TOPO + 1.05, w: 1.9, h: 0.8, fontFace: F, fontSize: 15, bold: true, color: C.texto, margin: 0, valign: "top" });
  s.addText(p[2], { x: x + 0.2, y: TOPO + 1.85, w: 1.9, h: 1.3, fontFace: F, fontSize: 11, color: C.texto_2, margin: 0, valign: "top" });
});
s.addText("Regra desta apresentação: dados de mercado só de fontes oficiais, com fonte e data. Sobre a cooperativa, só informações públicas. Onde falta dado da empresa, mostramos o que precisamos ver para dimensionar.", { x: MX, y: 5.45, w: W - 2 * MX, h: 0.9, fontFace: F, fontSize: 13, color: C.texto, margin: 0, valign: "top" });

// ───────────── 3. O ECOSSISTEMA
s = nova("O ecossistema Santa Clara", "Do campo à gôndola: uma cooperativa com seis negócios que se alimentam entre si");
const elos = [
  ["Campo e associados", "Quase 5 mil famílias associadas; cerca de 2,4 mil fornecem leite em 166 municípios. Rebanho de 48 mil vacas em lactação (2024), genética própria e sete suinoculturas."],
  ["Laticínios", "3 indústrias que processam mais de 1 milhão de litros de leite por dia. Mais de 200 itens: leite UHT, 51 tipos de queijo, requeijão, bebidas lácteas e proteicas."],
  ["Frigorífico e charcutaria", "2 frigoríficos, com a unidade de Vila Lângaro assumida em 2025 (600 suínos por dia). Mais de 100 itens: embutidos, salames, presunto cru e carnes."],
  ["Rações, doces e food service", "2 fábricas de ração, doces de frutas e linha para food service (queijos, cremes, recheios, carnes)."],
  ["Distribuição e varejo", "7 centrais de distribuição e novo centro em Carlos Barbosa. 30 lojas de varejo, entre supermercados e 15 lojas agropecuárias. 60% da produção vai para fora do RS."]];
elos.forEach((e, i) => cartao(s, MX + i * 2.45, TOPO, 2.3, 4.3, e[0], e[1], { fs: 12, tt: 13.5 }));
fonte(s, "Cooperativa Santa Clara, site (quem somos, produtos e blog de jul e ago/2026); SuperVarejo (mar/2025: frigoríficos, suinoculturas, rações, lojas e centrais); Jornal do Comércio (ago/2024 e ago/2025). Números de estrutura variam entre publicações; a confirmar com a cooperativa.");

// ───────────── 4. MATRIZ DE PRESSÕES
s = nova("Visão geral · Pressões por negócio", "Cada negócio da Santa Clara enfrenta uma pressão diferente sobre a margem");
tabela(s, MX, TOPO, [2.3, 5.2, 4.63], ["Negócio", "O que os dados oficiais mostram", "Fonte"], [
  ["Campo e leite", "Preço pago ao produtor: R$ 2,76 (1T25) → R$ 2,21 (4T25) → R$ 2,70 (2T26), com volume recorde de leite no país", "IBGE, Pesquisa Trimestral do Leite"],
  ["Laticínios", "Importação de lácteos +26% no 1T26; antidumping ao leite em pó da Argentina e do Uruguai; preço ao consumidor: leites e derivados +6,3% em 12 meses", "DERAL/SEAB-PR; MDIC (Gecex 907/2026); IBGE, IPCA"],
  ["Frigorífico suíno", "Abate de suínos +4,3% no Brasil e +6,8% no RS em 2025; carne de porco ao consumidor −8,3% em 12 meses; ração pesa de 65% a 72% do custo de produção", "IBGE, abate de animais e IPCA; Embrapa Suínos e Aves"],
  ["Varejo e supermercados", "Nos supermercados, a receita nominal cresce muito mais do que o volume: +3,9% contra +0,6% em agosto/2026", "IBGE, Pesquisa Mensal de Comércio"],
  ["Insumos e lojas agropecuárias", "Crédito rural de custeio a 9% ao ano no Plano Safra 2026/27, contra 22,89% do capital de giro de mercado", "Governo federal (Plano Safra); Banco Central"],
  ["Capital e tributos (todos)", "Selic em 13,75%; crédito presumido do leite a 90% desde abril/2026; reforma tributária a partir de 2027", "Banco Central; NT RFB 012/2026; LC 214/2025"]],
  { fs: 12 });
fonte(s, "IBGE (SIDRA, tabelas 1086, 1093, 7060 e 8882); MDIC; DERAL/SEAB-PR; Embrapa; Banco Central; Receita Federal; Planalto. Datas e consultas no último slide.");

// ───────────── 5. LEITE: VOLUME
const qs = Object.keys(ibge.BR.vol).slice(-16);
const lab = (q) => q.replace("º trimestre ", "T/").replace(/^(\d)T\/(\d{4})$/, (m, a, b) => a + "T" + b.slice(2));
const sum = (o, y) => Object.entries(o).filter(([k]) => k.endsWith(String(y))).reduce((a, [, v]) => a + v, 0);
const a25 = sum(ibge.BR.vol, 2025) / 1e6, a24 = sum(ibge.BR.vol, 2024) / 1e6, r25 = sum(ibge.RS.vol, 2025) / 1e6, r24 = sum(ibge.RS.vol, 2024) / 1e6;
s = nova("1 · O mercado · Campo e laticínios", "A captação de leite bateu recorde em 2025, o maior volume da série do IBGE consultada");
s.addChart(pres.charts.BAR, [{ name: "Leite adquirido (bilhões de litros)", labels: qs.map(lab), values: qs.map(q => +(ibge.BR.vol[q] / 1e6).toFixed(2)) }],
  { x: MX, y: TOPO, w: 8.2, h: 4.3, barDir: "col", chartColors: [GRAFICO.claro[0]], showValue: true, dataLabelFontSize: 8, dataLabelFormatCode: "0.0", dataLabelColor: C.texto,
    catAxisLabelFontSize: 9, valAxisLabelFontSize: 9, catAxisLabelFontFace: F, valAxisLabelFontFace: F, valGridLine: { color: C.borda, size: 0.5 }, showLegend: false,
    showTitle: true, title: "Leite cru adquirido pelas indústrias, Brasil (bilhões de litros por trimestre)", titleFontSize: 11, titleFontFace: F, titleColor: C.texto_2, valAxisMinVal: 4 });
S.kpi(s, 9.1, TOPO, 3.6, "Brasil, 2025", fmt(a25) + " bi L", "+" + fmt((a25 / a24 - 1) * 100) + "% sobre 2024");
S.kpi(s, 9.1, TOPO + 1.5, 3.6, "Rio Grande do Sul, 2025", fmt(r25, 2) + " bi L", "+" + fmt((r25 / r24 - 1) * 100) + "% sobre 2024");
S.kpi(s, 9.1, TOPO + 3.0, 3.6, "4º tri de 2025", fmt(ibge.BR.vol["4º trimestre 2025"] / 1e6, 2) + " bi L", "maior trimestre da série consultada");
fonte(s, "IBGE, Pesquisa Trimestral do Leite (SIDRA, tabela 1086), série 3º tri/2021 a 2º tri/2026. Consulta em 21/10/2026.");

// ───────────── 6. LEITE: PREÇO
const pq = Object.keys(ibge.BR.preco).slice(-16);
s = nova("1 · O mercado · Campo e laticínios", "O preço ao produtor caiu 20% ao longo de 2025 e se recuperou em 2026, enquanto o consumidor paga mais");
s.addChart(pres.charts.LINE, [{ name: "Brasil", labels: pq.map(lab), values: pq.map(q => ibge.BR.preco[q]) }, { name: "Rio Grande do Sul", labels: pq.map(lab), values: pq.map(q => ibge.RS.preco[q]) }],
  { x: MX, y: TOPO, w: 8.2, h: 4.3, chartColors: [GRAFICO.claro[0], GRAFICO.claro[1]], lineSize: 2.5, lineDataSymbolSize: 7, showLegend: true, legendPos: "b", legendFontSize: 10, legendFontFace: F,
    catAxisLabelFontSize: 9, valAxisLabelFontSize: 9, catAxisLabelFontFace: F, valAxisLabelFontFace: F, valGridLine: { color: C.borda, size: 0.5 }, valAxisMinVal: 1.8, valAxisMaxVal: 3.2, valAxisLabelFormatCode: "0.00",
    showTitle: true, title: "Preço médio do leite adquirido (R$ por litro)", titleFontSize: 11, titleFontFace: F, titleColor: C.texto_2 });
S.kpi(s, 9.1, TOPO, 3.6, "Preço ao produtor, 1T25 → 4T25", "R$ 2,76 → 2,21", "queda de 19,9% no Brasil");
S.kpi(s, 9.1, TOPO + 1.5, 3.6, "Ao consumidor, em 12 meses", "+6,3%", "leites e derivados · leite longa vida: +10,8%");
S.kpi(s, 9.1, TOPO + 3.0, 3.6, "Queijo e leite fermentado", "+3,8% e +9,4%", "variação em 12 meses até set/2026");
fonte(s, "IBGE, Pesquisa Trimestral do Leite (SIDRA 1086) e IPCA (SIDRA 7060, variação em 12 meses até setembro/2026). Consulta em 21/10/2026.");

// ───────────── 7. SUÍNOS
const sq = Object.keys(DADOS.suinos.RS).slice(-12);
const sb25 = sum(DADOS.suinos.BR, 2025) / 1e6, sb24 = sum(DADOS.suinos.BR, 2024) / 1e6, sr25 = sum(DADOS.suinos.RS, 2025) / 1e6, sr24 = sum(DADOS.suinos.RS, 2024) / 1e6;
s = nova("1 · O mercado · Frigorífico e charcutaria", "Mais suínos no mercado e carne de porco mais barata ao consumidor: a margem exige eficiência");
s.addChart(pres.charts.BAR, [{ name: "Suínos abatidos no RS (milhões de cabeças)", labels: sq.map(lab), values: sq.map(q => +(DADOS.suinos.RS[q] / 1e6).toFixed(2)) }],
  { x: MX, y: TOPO, w: 8.2, h: 4.3, barDir: "col", chartColors: [GRAFICO.claro[0]], showValue: true, dataLabelFontSize: 8, dataLabelFormatCode: "0.00", dataLabelColor: C.texto,
    catAxisLabelFontSize: 9, valAxisLabelFontSize: 9, catAxisLabelFontFace: F, valAxisLabelFontFace: F, valGridLine: { color: C.borda, size: 0.5 }, showLegend: false,
    showTitle: true, title: "Suínos abatidos no Rio Grande do Sul (milhões de cabeças por trimestre)", titleFontSize: 11, titleFontFace: F, titleColor: C.texto_2, valAxisMinVal: 2 });
S.kpi(s, 9.1, TOPO, 3.6, "Abate no Brasil, 2025", fmt(sb25) + " mi cab.", "+" + fmt((sb25 / sb24 - 1) * 100) + "% · RS: " + fmt(sr25) + " mi (+" + fmt((sr25 / sr24 - 1) * 100) + "%)");
S.kpi(s, 9.1, TOPO + 1.5, 3.6, "Carne de porco ao consumidor", "−8,3%", "em 12 meses até set/2026 (IPCA)");
S.kpi(s, 9.1, TOPO + 3.0, 3.6, "Exportação jan–set/2026", "+4,8% em volume", "1,03 mi t · receita +0,4% (US$ 2,53 bi)");
fonte(s, "IBGE, Pesquisa Trimestral do Abate de Animais (SIDRA 1093) e IPCA (SIDRA 7060); Secex/MDIC, dados consolidados jan–set/2026; Embrapa Suínos e Aves: ração responde por 64,8% (GO) a 72,1% (SC) do custo de produção no 1T26.");

// ───────────── 8. VAREJO
const mq = Object.keys(DADOS.pmc["Índice de volume de vendas no comércio varejista"]);
const mlab = (m) => m.replace(" 20", "/");
s = nova("1 · O mercado · Varejo e lojas", "Nos supermercados, a receita cresce bem mais que o volume: margem vem de preço e mix");
s.addChart(pres.charts.LINE, [{ name: "Receita nominal", labels: mq.map(mlab), values: mq.map(m => +DADOS.pmc["Índice de receita nominal de vendas no comércio varejista"][m]) }, { name: "Volume de vendas", labels: mq.map(mlab), values: mq.map(m => +DADOS.pmc["Índice de volume de vendas no comércio varejista"][m]) }],
  { x: MX, y: TOPO, w: 8.2, h: 4.3, chartColors: [GRAFICO.claro[0], GRAFICO.claro[1]], lineSize: 2.5, lineDataSymbolSize: 7, showLegend: true, legendPos: "b", legendFontSize: 10, legendFontFace: F,
    catAxisLabelFontSize: 8, valAxisLabelFontSize: 9, catAxisLabelFontFace: F, valAxisLabelFontFace: F, valGridLine: { color: C.borda, size: 0.5 }, valAxisLabelFormatCode: "0.0",
    showTitle: true, title: "Hipermercados e supermercados: variação sobre o mesmo mês do ano anterior (%)", titleFontSize: 11, titleFontFace: F, titleColor: C.texto_2 });
S.kpi(s, 9.1, TOPO, 3.6, "Agosto/2026 sobre agosto/2025", "+3,9% × +0,6%", "receita nominal × volume");
S.kpi(s, 9.1, TOPO + 1.5, 3.6, "Acumulado em 12 meses", "+3,8% × +1,1%", "receita nominal × volume");
S.kpi(s, 9.1, TOPO + 3.0, 3.6, "Alimentação no domicílio", "+4,2%", "IPCA em 12 meses até set/2026");
fonte(s, "IBGE, Pesquisa Mensal de Comércio (SIDRA 8882), hipermercados e supermercados; IPCA (SIDRA 7060). Consulta em 21/10/2026.");

// ───────────── 9. CAMPO E INSUMOS
s = nova("1 · O mercado · Insumos, lojas agropecuárias e associados", "O crédito rural oficial custa menos da metade do capital de giro de mercado");
S.kpi(s, MX, TOPO, 2.95, "Plano Safra 2026/27", "R$ 525,1 bi", "agricultura empresarial (+R$ 9 bi)");
S.kpi(s, MX + 3.05, TOPO, 2.95, "Cooperativas e demais produtores", "R$ 452,5 bi", "recursos programados");
S.kpi(s, MX + 6.1, TOPO, 2.95, "Custeio (Pronamp)", "9% ao ano", "investimentos: 8,5% a 12,5%");
S.kpi(s, MX + 9.15, TOPO, 2.95, "Capital de giro PJ (mercado)", "22,89% ao ano", "agosto/2026");
cartao(s, MX, TOPO + 1.8, 5.95, 2.45, "O que isso significa para a cadeia", "A diferença entre o capital de giro de mercado e o crédito rural de custeio é de 13,9 pontos percentuais ao ano. Quem tem acesso organizado às linhas oficiais, no associado e na cooperativa, protege margem.", { fs: 12.5 });
cartao(s, MX + 6.1, TOPO + 1.8, 6.0, 2.45, "O campo sob pressão", "Em 2024, o presidente da cooperativa disse que os juros consomem o resultado do produtor e que o número de produtores no RS caiu de 80 mil para 30 mil em oito anos. As cheias de maio/2024 atingiram, segundo a cooperativa, 20% dos produtores com perdas graves e 50% com perdas moderadas.", { fs: 12 });
fonte(s, "Governo federal, lançamento do Plano Safra 2026/2027 (30/06/2026); Banco Central (SGS 20725); Jornal do Comércio (ago/2024). Elegibilidade às linhas a confirmar caso a caso.");

// ───────────── 10. PRESSÕES QUE ATRAVESSAM
s = nova("2 · Dificuldades dos negócios", "Três pressões atravessam todos os negócios: capital, tributos e concorrência");
cartao(s, MX, TOPO, 3.95, 4.3, "Capital caro", "Meta Selic em 13,75% ao ano e capital de giro de pessoas jurídicas em 22,89% ao ano (agosto/2026).\n\nA cooperativa investe de forma contínua: planta de Casca (R$ 130 milhões), nova central de distribuição, frigorífico de Vila Lângaro e lojas. Cada ponto de custo financeiro pesa em todos os negócios.", { fs: 12 });
cartao(s, MX + 4.1, TOPO, 3.95, 4.3, "Tributação em transição", "Crédito presumido do leite limitado a 90% desde 01/04/2026 (LC 224/2025).\n\nReforma tributária: CBS e IBS a partir de 2027, com alíquota zero para leite, queijos e carnes da cesta básica (Anexo I da LC 214/2025). Embutidos dependem da classificação do produto.\n\nCooperativa: o resultado do ato cooperativo e do não cooperativo tem tratamento distinto (Lei 5.764/1971).", { fs: 11.5 });
cartao(s, MX + 8.2, TOPO, 3.95, 4.3, "Concorrência", "Importação de lácteos +26% no 1T26, com direito antidumping para o leite em pó da Argentina e do Uruguai desde junho/2026.\n\nA diretoria da cooperativa cita a importação e as empresas nacionais como o grande desafio de competitividade (2025).\n\nNo varejo, a receita sobe mais que o volume: ganhar espaço exige preço, mix e serviço.", { fs: 12 });
fonte(s, "Banco Central; Receita Federal (NT RFB 012/2026); LC 214/2025 e LC 224/2025; Lei 5.764/1971; DERAL/SEAB-PR; MDIC (Gecex 907/2026); IBGE; Jornal do Comércio (17/08/2025).");

// ───────────── 11. DIVISÓRIA
s = pres.addSlide({ masterName: "SAVE_ESCURO" });
s.addText("3 · O ESPELHO", { x: MX, y: 2.6, w: 8, h: 0.4, fontFace: FM, fontSize: 13, color: E.ouro, charSpacing: 2, margin: 0 });
s.addText("Como isso aparece em cada negócio da Santa Clara", { x: MX, y: 3.1, w: 11.5, h: 1.3, fontFace: F, fontSize: 38, bold: true, color: E.texto, margin: 0 });
s.addText("Com o que é público. Onde falta dado da cooperativa, mostramos a pergunta que os números dela respondem.", { x: MX, y: 4.5, w: 10, h: 0.8, fontFace: F, fontSize: 15, color: E.texto_2, margin: 0, valign: "top" });

// ───────────── 12. ESPELHO
s = nova("3 · O espelho", "Cada negócio tem um ponto de verificação na conta da Santa Clara");
tabela(s, MX, TOPO, [2.1, 5.1, 4.93], ["Negócio", "O que já se sabe da cooperativa (público)", "A pergunta que os números dela respondem"], [
  ["Campo e leite", "Cerca de 2,4 mil fornecedores em 166 municípios; pagamento do leite pela qualidade desde os anos 1990; compra de outras cooperativas", "O preço pago ao produtor acompanhou o preço de venda em cada linha?"],
  ["Laticínios", "UHT em Casca, queijos em Carlos Barbosa e Getúlio Vargas; 51 tipos de queijo; metade da produção em leite longa vida e metade em queijos e derivados", "Qual a margem por categoria e contra o importado?"],
  ["Frigorífico e charcutaria", "2 frigoríficos, 7 suinoculturas; Vila Lângaro (600 suínos por dia) assumida em 2025; integração de desossa em estudo", "Qual a margem por produto e quanto custa a ração?"],
  ["Rações", "2 fábricas de ração, que sustentam a suinocultura e o leite", "O custo da ração acompanha o preço do milho e do farelo de soja?"],
  ["Varejo e lojas", "30 lojas, entre supermercados (novos em Barão, Salvador do Sul e Carlos Barbosa) e 15 lojas agropecuárias", "Qual a margem por categoria e o prazo de venda a associados?"],
  ["Logística e financeiro", "7 centrais de distribuição e novo centro em Carlos Barbosa; 60% da produção fora do RS", "Qual o custo por tonelada, o prazo de recebimento e o custo da dívida?"]],
  { fs: 12 });
fonte(s, "Cooperativa Santa Clara (site, jul e ago/2026); SuperVarejo (mar/2025); Jornal do Comércio (ago/2024 e ago/2025).");

// ───────────── 13. RÉGUA
s = nova("3 · O espelho · O tamanho do que está em jogo", "Com R$ 3 bilhões de faturamento, cada fração de margem e cada dia de prazo pesam");
const dia = 3e9 / 365 / 1e6;
S.kpi(s, MX, TOPO, 2.95, "1 ponto de margem", "R$ 30 mi", "por ano, sobre R$ 3 bi");
S.kpi(s, MX + 3.05, TOPO, 2.95, "0,1 ponto de margem", "R$ 3 mi", "por ano");
S.kpi(s, MX + 6.1, TOPO, 2.95, "1 dia de prazo de recebimento", "R$ " + fmt(dia) + " mi", "de caixa parado na carteira");
S.kpi(s, MX + 9.15, TOPO, 2.95, "R$ 0,01 por litro de leite", "R$ 3,7 mi", "por ano, em 365 mi de litros");
cartao(s, MX, TOPO + 1.8, 5.95, 2.45, "Como lemos o número", "Margem: pontos percentuais sobre a receita projetada de R$ 3 bilhões. Para qualquer negócio, basta aplicar sobre a receita dele: cada R$ 1 bilhão de receita rende R$ 10 milhões por ponto de margem.\nPrazo: o caixa liberado por dia de recebimento a menos é a receita diária; a 22,89% ao ano, vale cerca de R$ 1,9 milhão por ano em juros.", { fs: 11.5 });
cartao(s, MX + 6.1, TOPO + 1.8, 6.0, 2.45, "Premissas", "Faturamento: projeção de R$ 3 bilhões para 2026, divulgada pela imprensa (jul/2026).\nVolume: mais de 1 milhão de litros por dia, conforme a cooperativa (jul/2026).\nCusto de capital: média de mercado (Banco Central), não o custo da cooperativa.\nA divisão da receita entre os negócios não é pública: fica para o diagnóstico.", { fs: 12 });
fonte(s, "Cálculos Save sobre dados públicos: Jornal do Comércio (jul/2026); Cooperativa Santa Clara (jul/2026); Banco Central (SGS 20725, agosto/2026). Estimativas preliminares sujeitas a validação técnica.");

// ───────────── 14. ESTEIRA
s = nova("4 · Como podemos ajudar", "Uma esteira única para todo o ecossistema: o fim de cada passo é o começo do próximo");
const mov = [["Destravar caixa", ["1 · Enxergar a empresa por inteiro", "2 · Recuperar o que já é seu", "3 · Receber o que lhe devem, e mais cedo", "4 · Aliviar a dívida que pesa"]],
  ["Proteger e controlar", ["5 · Deixar a empresa em dia", "6 · Pagar o imposto certo e se preparar para 2027", "7 · Dar governança ao dinheiro", "8 · Proteger o patrimônio"]],
  ["Crescer", ["9 · Capital para crescer", "10 · Financiar a sua cadeia", "11 · Vender e produzir além da fronteira", "12 · Manter a esteira rodando"]]];
mov.forEach((m, i) => {
  const x = MX + i * 4.1;
  s.addShape("roundRect", { x, y: TOPO, w: 3.95, h: 0.6, fill: { color: E.fundo }, line: { color: E.fundo }, rectRadius: 0.08 });
  s.addText(m[0], { x: x + 0.2, y: TOPO, w: 3.5, h: 0.6, fontFace: F, fontSize: 15, bold: true, color: E.ouro, margin: 0, valign: "middle" });
  m[1].forEach((p, j) => {
    s.addShape("roundRect", { x, y: TOPO + 0.75 + j * 0.76, w: 3.95, h: 0.64, fill: { color: C.cartao }, line: { color: C.borda, width: 0.75 }, rectRadius: 0.06 });
    s.addText(p, { x: x + 0.2, y: TOPO + 0.75 + j * 0.76, w: 3.6, h: 0.64, fontFace: F, fontSize: 11.5, color: C.texto, margin: 0, valign: "middle" });
  });
});
s.addText("Um gestor de projeto conduz a esteira em todos os negócios, conecta as equipes tributária, jurídica, financeira e de crédito e só avança quando o passo anterior entregou o que o próximo precisa.", { x: MX, y: 6.0, w: W - 2 * MX, h: 0.6, fontFace: F, fontSize: 13, bold: true, color: C.texto, margin: 0, valign: "top" });

// ───────────── 15. A ESTEIRA CONECTA OS NEGÓCIOS
s = nova("4 · Como podemos ajudar", "A esteira também conecta os negócios entre si, e é aí que a margem se multiplica");
const lig = [
  ["Conta do associado", "A loja agropecuária vende insumo e ração a prazo, o leite entregue paga a conta e o crédito rural financia a safra.", "Organizar a conta corrente do associado e o crédito da cadeia: menos capital parado e produtor com margem."],
  ["Compras de leite e de suínos", "Cada litro e cada suíno comprado gera crédito tributário possível e saldo credor.", "Conferir o aproveitamento integral do crédito presumido e do saldo credor nos laticínios e no frigorífico."],
  ["Varejo próprio como canal", "30 lojas vendem o que a indústria produz e geram dados de venda por categoria.", "Usar o dado de venda para decidir mix e preço e organizar o prazo entre indústria e varejo."],
  ["Logística e centrais", "7 centrais e um novo centro em Carlos Barbosa servem leite, queijos e carnes.", "Medir o custo por tonelada e liberar capital de giro no estoque e no prazo."],
  ["Rações e suinocultura", "A ração é de 65% a 72% do custo do suíno e abastece também o leite.", "Margem por produto e por planta, e compras de milho e farelo com governança."],
  ["Genética e qualidade", "Genética própria, concurso de qualidade e pagamento do leite pela qualidade.", "Transformar produtividade do associado em margem da cooperativa, com crédito certo para o investimento."]];
lig.forEach((l, i) => {
  const x = MX + (i % 3) * 4.1, y = TOPO + Math.floor(i / 3) * 2.2;
  s.addShape("roundRect", { x, y, w: 3.95, h: 2.05, fill: { color: C.cartao }, line: { color: C.borda, width: 0.75 }, rectRadius: 0.08 });
  s.addText(l[0], { x: x + 0.18, y: y + 0.1, w: 3.6, h: 0.35, fontFace: F, fontSize: 12.5, bold: true, color: C.texto, margin: 0, valign: "top" });
  s.addText(l[1], { x: x + 0.18, y: y + 0.45, w: 3.6, h: 0.7, fontFace: F, fontSize: 10.5, color: C.texto_2, margin: 0, valign: "top" });
  s.addText("NA ESTEIRA", { x: x + 0.18, y: y + 1.15, w: 3.6, h: 0.2, fontFace: FM, fontSize: 8, color: C.ouro_texto, margin: 0 });
  s.addText(l[2], { x: x + 0.18, y: y + 1.33, w: 3.6, h: 0.7, fontFace: F, fontSize: 10.5, bold: true, color: C.texto, margin: 0, valign: "top" });
});
fonte(s, "Cooperativa Santa Clara (site e imprensa); Embrapa Suínos e Aves; Governo federal (Plano Safra). Hipóteses a validar com os números da cooperativa.");

// ───────────── 16-18. OS MOVIMENTOS POR NEGÓCIO
function mov3(rot, tit, linhas, rodape) {
  const sl = nova(rot, tit);
  tabela(sl, MX, TOPO, [2.2, 3.3, 3.3, 3.33], ["Passo", "Campo, leite e laticínios", "Frigorífico, charcutaria e rações", "Varejo, lojas e logística"], linhas, { fs: 12 });
  fonte(sl, rodape);
}
mov3("4 · Como podemos ajudar · Destravar caixa", "Destravar caixa: ver a margem de cada negócio e liberar o que está parado", [
  ["1 · Enxergar por inteiro", "Margem por linha (UHT, queijos, bebidas, requeijão) e por região de captação; linha de base de prazo e dívida", "Margem por produto (carne, charcutaria, presunto cru) e por planta; custo da ração", "Margem por loja e por categoria; custo logístico por tonelada"],
  ["2 · Recuperar o que já é seu", "Crédito presumido do leite e saldo credor; créditos de energia, frio e embalagem; ato cooperativo e não cooperativo", "Crédito presumido na compra de suínos; créditos de insumos e energia; saldo credor", "ICMS e ICMS-ST na base do PIS/COFINS; créditos de energia e aluguel; contribuição sobre a folha"],
  ["3 · Receber mais cedo", "Prazo das grandes redes e do food service; cobrança organizada", "Carteira de atacado e redes; receber antes por instituição autorizada", "Conta corrente do associado nas lojas agropecuárias; recebíveis de cartão"],
  ["4 · Aliviar a dívida", "Custo das plantas e do capital de giro da safra", "Financiamento da aquisição de Vila Lângaro e do capital de giro", "Financiamento de lojas e do novo centro de distribuição"]],
  "Lei 10.925/2004; NT RFB 012/2026; Lei 5.764/1971. Estimativas preliminares sujeitas a validação técnica.");
mov3("4 · Como podemos ajudar · Proteger e controlar", "Proteger e controlar: manter a margem conquistada e preparar 2027", [
  ["5 · Deixar em dia", "Certidões, autos e processos de todas as unidades, com prazos sob dupla checagem", "Idem, incluindo a unidade assumida em 2025", "Idem, por loja e por central"],
  ["6 · Imposto certo e 2027", "Leite e queijos com alíquota zero em 2027; crédito presumido a 90%; saldos credores antes da transição", "Carnes in natura com alíquota zero; embutidos conforme a classificação; créditos de insumos", "Mix por NCM nas lojas; tratamento de ICMS-ST; preços e sistemas para CBS e IBS"],
  ["7 · Governança", "Painel mensal de margem por linha, associado e região", "Painel por planta e por produto, com custo de ração", "Painel por loja e categoria; conferência de estoque e prazo"],
  ["8 · Patrimônio", "Organização das estruturas e das participações da cooperativa", "Estrutura das suinoculturas, frigoríficos e fábricas de ração", "Imóveis das lojas e centrais, base de garantia para capital"]],
  "LC 214/2025 (Anexo I, cesta básica); LC 224/2025. Estimativas preliminares sujeitas a validação técnica.");
mov3("4 · Como podemos ajudar · Crescer", "Crescer: capital certo, produtor forte e mais valor por quilo vendido", [
  ["9 · Capital para crescer", "Investimentos anuais (R$ 28 mi em 2024, R$ 35 mi em 2025) com prazo e custo compatíveis", "Expansão do abate e integração da desossa, com projeto preparado para instituições", "Novo centro de distribuição e expansão do varejo"],
  ["10 · Financiar a cadeia", "Crédito ao produtor contra a entrega futura de leite", "Crédito ao suinocultor integrado contra a entrega de animais", "Crédito ao associado nas lojas agropecuárias, com a conta corrente organizada"],
  ["11 · Além da fronteira", "Queijos nobres, bebidas proteicas e whey: mais valor por litro", "Exportação de carne suína e charcutaria premium (presunto cru, jamón serrano)", "Vendas fora do RS (60% da produção): tributação interestadual e logística"],
  ["12 · Esteira rodando", "Revisão anual, novas competências e encontro trimestral com a diretoria", "Margem por planta acompanhada a cada trimestre", "Painel de valor por loja e por central"]],
  "Cooperativa Santa Clara; Jornal do Comércio. Avaliado caso a caso; sem condição definida antes da análise.");

// ───────────── 19. RESULTADOS POSSÍVEIS
s = nova("5 · Resultados possíveis", "O que a esteira pode representar em lucro e margem: faixas ilustrativas, com premissas à vista");
tabela(s, MX, TOPO, [2.4, 5.0, 4.73], ["Alavanca", "Premissa", "Faixa ilustrativa por ano"], [
  ["Prazo de recebimento", "Redução de 1, 3 ou 5 dias sobre R$ 3 bi de receita; custo de capital de 22,89% ao ano", "Caixa liberado: R$ 8, 25 e 41 mi. Juros evitados: R$ 1,9, 5,6 e 9,4 mi"],
  ["Custo da dívida", "Cada R$ 100 mi de dívida com custo menor em 2, 4 ou 6 pontos percentuais", "R$ 2, 4 ou 6 mi por R$ 100 mi"],
  ["Crédito rural na cadeia", "Cada R$ 100 mi de capital de giro da cadeia a 22,89% que passe a custeio a 9% (Pronamp, se elegível)", "Até R$ 13,9 mi por R$ 100 mi, na margem do associado e da cooperativa"],
  ["Crédito do leite (fluxo em jogo)", "Compra de leite de cerca de R$ 0,9 bi (1 mi L/dia a R$ 2,59/L); créditos de 1,85% a 4,625% do valor, a 90%", "Fluxo teórico de R$ 16 a 39 mi; o diagnóstico mostra quanto já está capturado"],
  ["Margem por negócio", "Ganho de 0,1, 0,3 ou 0,5 ponto percentual na receita de cada negócio", "R$ 1, 3 ou 5 mi por R$ 1 bi de receita; R$ 3, 9 ou 15 mi em R$ 3 bi"],
  ["Frigorífico, varejo e lojas", "Créditos de insumos, ICMS-ST, folha e saldo credor", "A dimensionar no diagnóstico, com os documentos de cada negócio"]], { fs: 11.5 });
s.addText("As linhas não se somam: algumas se sobrepõem. O crédito do leite é o teto teórico do fluxo; a parte aproveitável depende da habilitação no programa, do regime de apuração, da separação entre ato cooperativo e não cooperativo e do que a cooperativa já aproveita. Valor, prazo e êxito só se confirmam depois do diagnóstico com os documentos.", { x: MX, y: 5.85, w: W - 2 * MX, h: 0.7, fontFace: F, fontSize: 10, italic: true, color: C.texto_2, margin: 0, valign: "top" });
fonte(s, "Cálculos Save. Banco Central (SGS 20725); IBGE (preço do leite, RS, 2º tri/2026); Governo federal (Plano Safra 2026/27); Receita Federal (alíquotas do crédito presumido: confirmar vigência) e NT RFB 012/2026. Estimativa preliminar sujeita a validação técnica.");

// ───────────── 20. 90 DIAS
s = nova("Como começamos", "Os primeiros 90 dias e o que precisamos ver em cada negócio");
cartao(s, MX, TOPO, 5.95, 4.3, "O que precisamos ver (sob confidencialidade)", "• DRE e balanço dos dois últimos anos, por negócio quando houver\n• Apuração de PIS/COFINS e do crédito presumido (leite e suínos); EFD-Contribuições\n• Separação do ato cooperativo e não cooperativo\n• Extrato de dívidas e custo médio\n• Carteira a receber com prazos, por canal\n• Composição das compras de leite, suínos, milho e farelo\n• Margem por linha, planta e loja, se houver", { fs: 12.5 });
cartao(s, MX + 6.1, TOPO, 6.0, 4.3, "O caminho em 90 dias", "Semanas 1–2: conversa com a diretoria, confidencialidade e documentos.\nSemanas 3–4: mapa do ecossistema e linha de base de margem, prazo e dívida (passo 1).\nSemanas 5–8: primeiro passo de execução, no negócio de maior retorno.\nSemanas 9–10: primeiro mapa de valor e desenho do passo seguinte.\nSemanas 11–13: encontro trimestral com a diretoria.\n\nVocês terão um gestor de projeto que conduz tudo e conecta as nossas equipes aos seis negócios.", { fs: 12.5 });

// ───────────── 21. FONTES
s = nova("Fontes e avisos", "Fontes oficiais e públicas, com data de consulta");
s.addText([
  { text: "Oficiais\n", options: { bold: true, fontFace: F, fontSize: 10.5, color: C.texto } },
  { text: "IBGE, SIDRA: Pesquisa Trimestral do Leite (tabela 1086), Pesquisa Trimestral do Abate de Animais (1093), IPCA (7060, variação em 12 meses até set/2026) e Pesquisa Mensal de Comércio (8882, até ago/2026). Consulta em 21/10/2026.\nBanco Central do Brasil, SGS 432 (meta Selic) e 20725 (capital de giro de pessoas jurídicas, % a.a.), consulta em 21/10/2026.\nMDIC/Secex, dados consolidados do comércio exterior, jan–set/2026 (carne suína); MDIC, Resolução Gecex nº 907/2026 (antidumping, leite em pó).\nDERAL/SEAB-PR, boletim nº 18/2026 (importação de lácteos no 1º tri/2026), a conferir no Comex Stat. MAPA, Câmara Setorial do Leite (07/04/2026).\nEmbrapa Suínos e Aves, CIAS (custo de produção, 1º tri/2026).\nGoverno federal: Plano Safra 2026/2027 (lançamento em 30/06/2026).\nReceita Federal, NT RFB 012/2026 e programa Mais Leite Saudável (alíquotas: confirmar vigência). LC 214/2025, LC 224/2025 e Lei 5.764/1971 (Planalto).\n", options: { fontFace: F, fontSize: 10, color: C.texto_2, breakLine: true } },
  { text: "Públicas, sobre a cooperativa\n", options: { bold: true, fontFace: F, fontSize: 10.5, color: C.texto } },
  { text: "Cooperativa Santa Clara: site (quem somos, produtos, blog de 29/07 e 14/08/2026). SuperVarejo (mar/2025). Jornal do Comércio: ago/2024, 17/08/2025 e jul/2026.\n", options: { fontFace: F, fontSize: 10, color: C.texto_2, breakLine: true } },
  { text: "Avisos\n", options: { bold: true, fontFace: F, fontSize: 10.5, color: C.texto } },
  { text: "Pré-análise de caráter geral, sem acesso aos dados internos da cooperativa. Não constitui parecer jurídico ou tributário nem oferta de crédito. As faixas são ilustrativas, com premissas indicadas, e dependem de documentos e de validação técnica. Valor, prazo e êxito não são prometidos.", options: { fontFace: F, fontSize: 10, color: C.texto_2 } },
], { x: MX, y: TOPO - 0.1, w: W - 2 * MX, h: 4.9, margin: 0, valign: "top", isTextBox: true, paraSpaceAfter: 2 });

pres.writeFile({ fileName: OUT }).then(() => console.log("ok", OUT));
