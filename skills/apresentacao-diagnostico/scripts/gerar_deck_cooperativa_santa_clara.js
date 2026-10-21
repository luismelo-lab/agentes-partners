// Apresentação ao presidente da Cooperativa Santa Clara (21/10/2026).
// Roteiro do Luis: dados de mercado > dificuldades do setor (fontes oficiais) > espelho na empresa > como ajudar > resultados possíveis.
// Foco: mais lucro e mais margem. Uso: NODE_PATH=<node_modules> node gerar_deck_cooperativa_santa_clara.js <dados_deck_ibge.json> <saida.pptx>
const fs = require("fs");
const path = require("path");
const S = require(path.join(__dirname, "../../../departamentos/marketing-marca/padrao/pptx_save.js"));
const { C, E, F, FM, W, H, MX, GRAFICO } = S;
const ibge = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const OUT = process.argv[3];

const pres = S.novaApresentacao("Mais lucro e mais margem · Cooperativa Santa Clara");
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
s.addText("APRESENTAÇÃO AO PRESIDENTE · OUTUBRO DE 2026", { x: MX, y: 2.3, w: 10, h: 0.35, fontFace: FM, fontSize: 12, color: E.ouro, charSpacing: 2, margin: 0 });
s.addText("Mais lucro e mais margem para a Cooperativa Santa Clara", { x: MX, y: 2.75, w: 11.2, h: 1.7, fontFace: F, fontSize: 40, bold: true, color: E.texto, margin: 0, valign: "top" });
s.addText("O mercado do leite, as dificuldades do setor, o espelho na cooperativa, como podemos ajudar e os resultados possíveis", { x: MX, y: 4.6, w: 10.5, h: 0.9, fontFace: F, fontSize: 16, color: E.texto_2, margin: 0, valign: "top" });
s.addText("PRÉ-ANÁLISE · ESTIMATIVAS PRELIMINARES SUJEITAS A VALIDAÇÃO TÉCNICA · SEM PROMESSA DE VALOR, PRAZO OU ÊXITO", { x: MX, y: 6.55, w: 11.5, h: 0.3, fontFace: FM, fontSize: 8.5, color: E.ouro, margin: 0 });

// ───────────── 2. OBJETIVO E ROTEIRO
s = nova("Nosso ponto de partida", "Todo o trabalho serve a um objetivo: mais lucro e mais margem");
const passos = [["1", "O mercado", "O que os dados oficiais mostram sobre o leite no Brasil"], ["2", "As dificuldades do setor", "Onde a margem de quem industrializa leite está sob pressão"],
  ["3", "O espelho na Santa Clara", "Como cada pressão chega à cooperativa, com o que é público"], ["4", "Como podemos ajudar", "Uma esteira em três movimentos, um passo abrindo o próximo"],
  ["5", "Os resultados possíveis", "O que cada fração de margem e de prazo representa para a cooperativa"]];
passos.forEach((p, i) => {
  const x = MX + i * 2.45;
  s.addShape("roundRect", { x, y: TOPO + 0.2, w: 2.3, h: 3.0, fill: { color: i === 4 ? C.ouro_suave : C.cartao }, line: { color: C.borda, width: 0.75 }, rectRadius: 0.08 });
  s.addText(p[0], { x: x + 0.2, y: TOPO + 0.35, w: 1, h: 0.6, fontFace: FM, fontSize: 28, bold: true, color: C.ouro_texto, margin: 0 });
  s.addText(p[1], { x: x + 0.2, y: TOPO + 1.05, w: 1.9, h: 0.8, fontFace: F, fontSize: 15, bold: true, color: C.texto, margin: 0, valign: "top" });
  s.addText(p[2], { x: x + 0.2, y: TOPO + 1.9, w: 1.9, h: 1.4, fontFace: F, fontSize: 10.5, color: C.texto_2, margin: 0, valign: "top" });
});
s.addText("Regra desta apresentação: dados de mercado e do setor só de fontes oficiais, com fonte e data. Informações da cooperativa só as públicas. Onde falta dado da empresa, mostramos o que precisamos ver para dimensionar.", { x: MX, y: 5.45, w: W - 2 * MX, h: 0.9, fontFace: F, fontSize: 13, color: C.texto, margin: 0, valign: "top" });

// ───────────── 3. VOLUME (IBGE)
const qs = Object.keys(ibge.BR.vol).slice(-16);
const lab = (q) => q.replace("º trimestre ", "T/").replace(/^(\d)T\/(\d{4})$/, (m, a, b) => a + "T" + b.slice(2));
const a25 = Object.entries(ibge.BR.vol).filter(([k]) => k.endsWith("2025")).reduce((a, [, v]) => a + v, 0) / 1e6;
const a24 = Object.entries(ibge.BR.vol).filter(([k]) => k.endsWith("2024")).reduce((a, [, v]) => a + v, 0) / 1e6;
const r25 = Object.entries(ibge.RS.vol).filter(([k]) => k.endsWith("2025")).reduce((a, [, v]) => a + v, 0) / 1e6;
const r24 = Object.entries(ibge.RS.vol).filter(([k]) => k.endsWith("2024")).reduce((a, [, v]) => a + v, 0) / 1e6;
s = nova("1 · O mercado", "O Brasil nunca captou tanto leite: 2025 foi o maior volume da série");
s.addChart(pres.charts.BAR, [{ name: "Leite adquirido (bilhões de litros)", labels: qs.map(lab), values: qs.map(q => +(ibge.BR.vol[q] / 1e6).toFixed(2)) }],
  { x: MX, y: TOPO, w: 8.2, h: 4.3, barDir: "col", chartColors: [GRAFICO.claro[0]], showValue: true, dataLabelFontSize: 8, dataLabelFormatCode: "0.0", dataLabelColor: C.texto,
    catAxisLabelFontSize: 9, valAxisLabelFontSize: 9, catAxisLabelFontFace: F, valAxisLabelFontFace: F, valGridLine: { color: C.borda, size: 0.5 }, showLegend: false,
    showTitle: true, title: "Leite cru adquirido pelas indústrias, Brasil (bilhões de litros por trimestre)", titleFontSize: 11, titleFontFace: F, titleColor: C.texto_2, valAxisMinVal: 4 });
S.kpi(s, 9.1, TOPO, 3.6, "Brasil, 2025", fmt(a25) + " bi L", "+" + fmt((a25 / a24 - 1) * 100) + "% sobre 2024");
S.kpi(s, 9.1, TOPO + 1.5, 3.6, "Rio Grande do Sul, 2025", fmt(r25, 2) + " bi L", "+" + fmt((r25 / r24 - 1) * 100) + "% sobre 2024");
S.kpi(s, 9.1, TOPO + 3.0, 3.6, "4º tri de 2025", fmt(ibge.BR.vol["4º trimestre 2025"] / 1e6, 2) + " bi L", "maior trimestre da série consultada");
fonte(s, "IBGE, Pesquisa Trimestral do Leite (SIDRA, tabela 1086), série 3º tri/2021 a 2º tri/2026. Consulta em 21/10/2026.");

// ───────────── 4. PREÇO (IBGE)
const pq = Object.keys(ibge.BR.preco).slice(-16);
s = nova("1 · O mercado", "O preço pago ao produtor caiu 20% em nove meses de 2025 e voltou a oscilar em 2026");
s.addChart(pres.charts.LINE, [{ name: "Brasil", labels: pq.map(lab), values: pq.map(q => ibge.BR.preco[q]) }, { name: "Rio Grande do Sul", labels: pq.map(lab), values: pq.map(q => ibge.RS.preco[q]) }],
  { x: MX, y: TOPO, w: 8.2, h: 4.3, chartColors: [GRAFICO.claro[0], GRAFICO.claro[1]], lineSize: 2.5, lineDataSymbolSize: 7, showLegend: true, legendPos: "b", legendFontSize: 10, legendFontFace: F,
    catAxisLabelFontSize: 9, valAxisLabelFontSize: 9, catAxisLabelFontFace: F, valAxisLabelFontFace: F, valGridLine: { color: C.borda, size: 0.5 }, valAxisMinVal: 1.8, valAxisMaxVal: 3.2, valAxisLabelFormatCode: "0.00",
    showTitle: true, title: "Preço médio do leite adquirido (R$ por litro)", titleFontSize: 11, titleFontFace: F, titleColor: C.texto_2 });
S.kpi(s, 9.1, TOPO, 3.6, "1º tri 2025 → 4º tri 2025", "R$ 2,76 → 2,21", "queda de 19,9% no Brasil");
S.kpi(s, 9.1, TOPO + 1.5, 3.6, "2º tri de 2026", "R$ " + fmt(ibge.BR.preco["2º trimestre 2026"], 2), "Brasil · RS: R$ " + fmt(ibge.RS.preco["2º trimestre 2026"], 2));
s.addText("Mais oferta e preço instável: quem industrializa precisa de margem que não dependa do ciclo do leite.", { x: 9.1, y: TOPO + 3.1, w: 3.6, h: 1.2, fontFace: F, fontSize: 12.5, bold: true, color: C.texto, margin: 0, valign: "top" });
fonte(s, "IBGE, Pesquisa Trimestral do Leite (SIDRA, tabela 1086), preço médio do leite adquirido. Consulta em 21/10/2026.");

// ───────────── 5. DIFICULDADES
s = nova("2 · Dificuldades do setor", "Cinco pressões, todas documentadas por fontes oficiais, apertam a margem de quem industrializa");
tabela(s, MX, TOPO, [2.5, 6.4, 3.23], ["Pressão", "O que os dados oficiais mostram", "Fonte"], [
  ["Preço instável do leite", "Preço médio ao produtor R$ 2,76 (1T25) → R$ 2,21 (4T25) → R$ 2,70 (2T26), com volume recorde de 7,4 bi L no 4T25", "IBGE, Pesquisa Trimestral do Leite"],
  ["Concorrência de importados", "Importação de lácteos +26% em volume no 1T26 sobre o 1T25, com queijos em cerca de 40% do total. O governo aplicou direito antidumping definitivo ao leite em pó da Argentina e do Uruguai (Res. Gecex 907, 03/06/2026)", "DERAL/SEAB-PR (boletim 18/2026); MDIC"],
  ["Custo de produção em alta", "O índice de custo de produção do leite (ICPLeite, Embrapa) subiu 6,5% em 2025 sobre 2024; energia, mão de obra e sanidade lideram", "Embrapa, em apresentação à Câmara Setorial do Leite (MAPA, 07/04/2026)"],
  ["Custo do capital", "Meta Selic em 13,75% ao ano; taxa média do capital de giro de pessoas jurídicas em 22,89% ao ano (agosto/2026)", "Banco Central, SGS 432 e 20725"],
  ["Tributação em transição", "O crédito presumido do leite passou a ser limitado a 90% desde 01/04/2026; a reforma traz CBS e IBS a partir de 2027, com alíquota zero para leite e queijos da cesta básica", "NT RFB 012/2026; LC 224/2025; LC 214/2025"]],
  { fs: 11.5 });
s.addText("Cenário do setor, nas palavras do presidente da cooperativa (2024): o número de produtores no RS caiu de 80 mil para 30 mil em oito anos e os juros consomem o resultado de quem toma crédito.", { x: MX, y: 5.95, w: W - 2 * MX, h: 0.55, fontFace: F, fontSize: 11, italic: true, color: C.texto_2, margin: 0, valign: "top" });
fonte(s, "IBGE; MDIC; DERAL/SEAB-PR; Embrapa/MAPA; Banco Central; Receita Federal; Planalto; Jornal do Comércio (16/08/2024). Detalhes e datas no último slide.");

// ───────────── 6. ONDE A PRESSÃO CHEGA NA MARGEM
s = nova("2 · Dificuldades do setor", "Cada pressão chega a um ponto diferente da conta que forma a margem");
const caixas = [["Preço de venda", "Importados e novas ofertas limitam o repasse", C.cartao], ["(−) Leite, a matéria-prima", "Preço ao produtor oscila e o custo de produção sobe", C.cartao], ["(−) Custo industrial e logística", "Energia, mão de obra, frete e distribuição", C.cartao],
  ["(−) Tributos", "Crédito presumido a 90% e reforma a partir de 2027", C.cartao], ["(−) Custo financeiro", "Capital de giro a 22,89% ao ano e prazo de recebimento", C.cartao], ["= Margem", "É aqui que o resultado aparece, ou desaparece", C.ouro_suave]];
caixas.forEach((c, i) => {
  const x = MX + i * 2.05;
  s.addShape("roundRect", { x, y: TOPO + 0.4, w: 1.95, h: 2.6, fill: { color: c[2] }, line: { color: C.borda, width: 0.75 }, rectRadius: 0.08 });
  s.addText(c[0], { x: x + 0.12, y: TOPO + 0.55, w: 1.71, h: 0.8, fontFace: F, fontSize: 12.5, bold: true, color: C.texto, margin: 0, valign: "top" });
  s.addText(c[1], { x: x + 0.12, y: TOPO + 1.4, w: 1.71, h: 1.5, fontFace: F, fontSize: 10.5, color: C.texto_2, margin: 0, valign: "top" });
});
s.addText("Margem não se defende em um só ponto. Por isso olhamos a conta inteira, na ordem em que o dinheiro e o risco pedem.", { x: MX, y: 5.4, w: W - 2 * MX, h: 0.9, fontFace: F, fontSize: 17, bold: true, color: C.texto, margin: 0, valign: "top" });

// ───────────── 7. DIVISÓRIA
s = pres.addSlide({ masterName: "SAVE_ESCURO" });
s.addText("3 · O ESPELHO", { x: MX, y: 2.6, w: 8, h: 0.4, fontFace: FM, fontSize: 13, color: E.ouro, charSpacing: 2, margin: 0 });
s.addText("Como isso aparece na Santa Clara", { x: MX, y: 3.1, w: 11, h: 1.2, fontFace: F, fontSize: 38, bold: true, color: E.texto, margin: 0 });
s.addText("Com o que é público. Onde falta dado da cooperativa, mostramos a pergunta que os números dela respondem.", { x: MX, y: 4.4, w: 10, h: 0.8, fontFace: F, fontSize: 15, color: E.texto_2, margin: 0, valign: "top" });

// ───────────── 8. SANTA CLARA HOJE
s = nova("3 · O espelho", "Uma cooperativa de 114 anos, em escala e em crescimento");
const k = [["Faturamento projetado 2026", "R$ 3 bi", "projeção divulgada em jul/2026"], ["Famílias associadas", "quase 5 mil", "cerca de 2,3 mil produzem leite"], ["Colaboradores", "mais de 2,3 mil", "site institucional"],
  ["Unidades industriais", "3", "Carlos Barbosa, Getúlio Vargas e Casca"], ["Coleta de leite", "153 municípios", "Serra, Alto Uruguai, Alto Jacuí e Taquari"], ["Vendas fora do RS", "60%", "da produção, segundo a diretoria (2025)"]];
k.forEach((c, i) => S.kpi(s, MX + (i % 3) * 4.1, TOPO + Math.floor(i / 3) * 1.7, 3.9, c[0], c[1], c[2]));
s.addText("Casca (UHT): investimento de R$ 130 milhões e capacidade de 600 mil litros por dia · Getúlio Vargas: 150 mil litros por dia · Investimentos de R$ 35 milhões previstos para 2025 · Mix de cerca de 350 itens (2022): laticínios, frigorífico e doces · Marca de queijos mais lembrada entre os gaúchos.", { x: MX, y: TOPO + 3.55, w: W - 2 * MX, h: 0.95, fontFace: F, fontSize: 11, color: C.texto_2, margin: 0, valign: "top" });
fonte(s, "Cooperativa Santa Clara, site institucional (quem somos); Jornal do Comércio (jul/2026 e 17/08/2025). Números de faturamento e de pessoas variam entre publicações; usamos os mais recentes.");

// ───────────── 9. ESPELHO: PRESSÕES x COOPERATIVA
s = nova("3 · O espelho", "Cada pressão do setor tem um ponto de verificação na conta da Santa Clara");
tabela(s, MX, TOPO, [2.2, 5.2, 4.73], ["Pressão", "O que já se sabe da cooperativa (público)", "A pergunta que os números dela respondem"], [
  ["Preço do leite", "Rede de cerca de 2,3 mil produtores associados, captação em 153 municípios e compra de leite de outras cooperativas", "O preço pago ao produtor acompanhou o preço de venda em cada linha de produto?"],
  ["Importados e concorrência", "A diretoria cita a importação e as empresas nacionais como o grande desafio de competitividade; UHT de Casca está em 5º lugar no Sul (AGAS)", "Qual a margem por categoria (UHT, queijos, bebidas, requeijão) contra o preço do concorrente?"],
  ["Custo do capital", "Planta de Casca (R$ 130 mi), nova central de distribuição e R$ 35 mi de investimentos em 2025", "Qual o custo médio, o prazo e o tamanho da dívida, e quanto vai a juros por ano?"],
  ["Tributação", "Cooperativa com ato cooperativo e ato não cooperativo; crédito presumido do leite a 90%; reforma em 2027", "O crédito do leite e o saldo credor estão integralmente aproveitados? A apuração separa corretamente os dois atos?"],
  ["Prazo e logística", "60% da produção sai do Rio Grande do Sul, para grandes redes", "Qual o prazo médio de recebimento e quanto do capital fica parado na carteira?"]],
  { fs: 11.5 });
fonte(s, "Jornal do Comércio (17/08/2025); site da cooperativa; Lei 5.764/1971 (ato cooperativo); NT RFB 012/2026.");

// ───────────── 10. RÉGUA
s = nova("5 · O tamanho do que está em jogo", "Com R$ 3 bilhões de faturamento, cada fração de margem e cada dia de prazo pesam");
const dia = 3e9 / 365 / 1e6;
S.kpi(s, MX, TOPO, 2.95, "1 ponto de margem", "R$ 30 mi", "por ano, sobre R$ 3 bi");
S.kpi(s, MX + 3.05, TOPO, 2.95, "0,1 ponto de margem", "R$ 3 mi", "por ano");
S.kpi(s, MX + 6.1, TOPO, 2.95, "1 dia de prazo de recebimento", "R$ " + fmt(dia) + " mi", "de caixa parado na carteira");
S.kpi(s, MX + 9.15, TOPO, 2.95, "R$ 0,01 por litro", "R$ 3,7 mi", "por ano, em 365 mi de litros");
cartao(s, MX, TOPO + 1.8, 5.95, 2.6, "Como lemos o número", "Margem: variação em pontos percentuais sobre a receita projetada de R$ 3 bilhões.\nPrazo: o caixa liberado por dia de recebimento a menos é a receita diária. Ao custo de capital de giro de 22,89% ao ano, cada dia vale cerca de R$ 1,9 milhão por ano em juros.", { fs: 12.5 });
cartao(s, MX + 6.1, TOPO + 1.8, 6.0, 2.6, "Premissas", "Faturamento: projeção de R$ 3 bilhões para 2026, divulgada pela imprensa.\nVolume: 1 milhão de litros por dia, premissa ilustrativa a confirmar com a cooperativa.\nCusto de capital: média de mercado do capital de giro de pessoas jurídicas (Banco Central), não o custo da cooperativa.", { fs: 12.5 });
fonte(s, "Cálculos Save sobre dados públicos: Jornal do Comércio (jul/2026), Banco Central (SGS 20725, agosto/2026). Estimativas preliminares sujeitas a validação técnica.");

// ───────────── 11. ESTEIRA
s = nova("4 · Como podemos ajudar", "Uma esteira em três movimentos: o fim de cada passo é o começo do próximo");
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
s.addText("Um gestor de projeto conduz a esteira, conecta as equipes tributária, jurídica, financeira e de crédito e só avança quando o passo anterior entregou o que o próximo precisa.", { x: MX, y: 6.0, w: W - 2 * MX, h: 0.6, fontFace: F, fontSize: 13, bold: true, color: C.texto, margin: 0, valign: "top" });

// ───────────── 12-14. OS MOVIMENTOS NA SANTA CLARA
function movimento(rot, tit, itens, rodape) {
  const sl = nova(rot, tit);
  itens.forEach((it, i) => {
    const x = MX + i * 3.08;
    sl.addShape("roundRect", { x, y: TOPO, w: 2.95, h: 4.4, fill: { color: C.cartao }, line: { color: C.borda, width: 0.75 }, rectRadius: 0.08 });
    sl.addText(it[0], { x: x + 0.15, y: TOPO + 0.12, w: 2.65, h: 0.65, fontFace: F, fontSize: 12.5, bold: true, color: C.texto, margin: 0, valign: "top" });
    sl.addText("NA SANTA CLARA", { x: x + 0.15, y: TOPO + 0.82, w: 2.65, h: 0.2, fontFace: FM, fontSize: 8, color: C.ouro_texto, margin: 0 });
    sl.addText(it[1], { x: x + 0.15, y: TOPO + 1.05, w: 2.65, h: 2.1, fontFace: F, fontSize: 11, color: C.texto_2, margin: 0, valign: "top" });
    sl.addText("EFEITO NA MARGEM", { x: x + 0.15, y: TOPO + 3.2, w: 2.65, h: 0.2, fontFace: FM, fontSize: 8, color: C.ouro_texto, margin: 0 });
    sl.addText(it[2], { x: x + 0.15, y: TOPO + 3.42, w: 2.65, h: 0.95, fontFace: F, fontSize: 11, bold: true, color: C.texto, margin: 0, valign: "top" });
  });
  if (rodape) fonte(sl, rodape);
  return sl;
}
movimento("4 · Como podemos ajudar · Destravar caixa", "Destravar caixa: o primeiro passo é saber onde a margem escapa", [
  ["1 · Enxergar a empresa por inteiro", "Mapa fiscal e financeiro por linha (UHT, queijos, bebidas, requeijão, frigorífico, lojas) e linha de base de margem, prazo e custo da dívida.", "Mostra onde a margem escapa e o que atacar primeiro."],
  ["2 · Recuperar o que já é seu", "Conferir o aproveitamento integral do crédito presumido do leite e do saldo credor; créditos de insumos, energia e embalagens; contribuição sobre a folha; e a separação correta entre ato cooperativo e não cooperativo.", "Caixa liberado e menor carga tributária efetiva."],
  ["3 · Receber o que lhe devem, e mais cedo", "Prazo de recebimento das grandes redes, cobrança organizada com automação e, quando fizer sentido, receber antes por instituição autorizada.", "Menos capital parado: cada dia a menos libera cerca de R$ 8 mi."],
  ["4 · Aliviar a dívida que pesa", "Perfil e custo do endividamento; alongar prazos e trocar dívida cara. O crédito recuperado no passo 2 pode abater o que for mais caro.", "Menor custo financeiro, com parcelas que cabem no fluxo."]],
  "Lei 10.925/2004, art. 8º; NT RFB 012/2026; Lei 5.764/1971; Banco Central (SGS 20725). Estimativas preliminares sujeitas a validação técnica.");
movimento("4 · Como podemos ajudar · Proteger e controlar", "Proteger e controlar: manter a margem conquistada e preparar 2027", [
  ["5 · Deixar a empresa em dia", "Certidões, autos e processos mapeados, com prazos sob dupla checagem e compensação com créditos quando cabe.", "Sem risco escondido; certidão em dia é pré-requisito de crédito de longo prazo."],
  ["6 · Pagar o imposto certo e se preparar para 2027", "Simular CBS e IBS por produto até 2033; tratar o saldo credor e o crédito presumido reduzido a 90%; leite e queijos da cesta básica passam a ter alíquota zero.", "Margem previsível por produto e créditos antigos usados antes da transição."],
  ["7 · Dar governança ao dinheiro", "Painel mensal de margem por linha de produto, endividamento, carteira e fluxo, com conferência regular.", "Decisão de preço e de mix com dado, e controle que quem financia exige."],
  ["8 · Proteger o patrimônio", "Organização das estruturas e dos ativos (unidades, lojas, participações) e das regras de governança.", "Base sólida para captar capital com prazo e custo adequados."]],
  "LC 214/2025 (Anexo I, cesta básica); LC 224/2025; Lei 5.764/1971. Estimativas preliminares sujeitas a validação técnica.");
movimento("4 · Como podemos ajudar · Crescer", "Crescer: capital barato, produtor forte e margem maior por produto", [
  ["9 · Capital para crescer", "Os investimentos anuais (R$ 35 mi em 2025; planta de Casca com R$ 130 mi) com prazo e custo compatíveis; projeto preparado para instituições e investidores.", "Menor custo de capital sobre investimentos de longo prazo."],
  ["10 · Financiar a sua cadeia", "Mecanismo próprio para dar crédito ao produtor associado contra a entrega futura de leite, pois os juros consomem o resultado do produtor (declaração do presidente, 2024).", "Produtor com margem protege o volume e a qualidade da captação."],
  ["11 · Vender e produzir além da fronteira", "Linhas de maior valor (queijos nobres, whey) e vendas fora do RS (60% da produção); tributação interestadual e, se fizer sentido, exportação.", "Mais valor por litro industrializado."],
  ["12 · Manter a esteira rodando", "Revisão anual, novas competências, encontro trimestral com a diretoria e painel de valor.", "Margem acompanhada e protegida ao longo do tempo."]],
  "Cooperativa Santa Clara; Jornal do Comércio (16/08/2024 e 17/08/2025). Avaliado caso a caso; sem condição definida antes da análise.");

// ───────────── 15. RESULTADOS POSSÍVEIS
s = nova("5 · Resultados possíveis", "O que a esteira pode representar em lucro e margem: faixas ilustrativas, com premissas à vista");
tabela(s, MX, TOPO, [2.5, 4.9, 4.73], ["Alavanca", "Premissa", "Faixa ilustrativa por ano"], [
  ["Prazo de recebimento", "Redução de 1, 3 ou 5 dias sobre receita de R$ 3 bi; custo de capital de 22,89% ao ano", "Caixa liberado: R$ 8, 25 e 41 mi. Economia em juros: R$ 1,9, 5,6 e 9,4 mi"],
  ["Custo da dívida", "Cada R$ 100 mi de dívida com custo menor em 2, 4 ou 6 pontos percentuais", "R$ 2, 4 ou 6 mi por R$ 100 mi de dívida"],
  ["Crédito do leite (fluxo em jogo)", "Compra de leite de cerca de R$ 0,9 bi (1 mi L/dia a R$ 2,59/L, preço médio do RS no 2T26); créditos de 1,85% a 4,625% do valor, a 90%", "Fluxo teórico de R$ 16 a 39 mi. O diagnóstico mostra quanto já está capturado e quanto é aproveitável"],
  ["Margem consolidada", "Ganho de 0,1, 0,3 ou 0,5 ponto percentual sobre R$ 3 bi de receita", "R$ 3, 9 ou 15 mi"]], { fs: 11.5 });
s.addText("As linhas não se somam: algumas se sobrepõem. O crédito do leite é o teto teórico do fluxo; a parte aproveitável depende da habilitação no programa, do regime de apuração, da separação entre ato cooperativo e não cooperativo e do que a cooperativa já aproveita. Valor, prazo e êxito só se confirmam depois do diagnóstico com os documentos.", { x: MX, y: 5.6, w: W - 2 * MX, h: 0.9, fontFace: F, fontSize: 10.5, italic: true, color: C.texto_2, margin: 0, valign: "top" });
fonte(s, "Cálculos Save. Banco Central (SGS 20725); IBGE (preço do leite, RS, 2º tri/2026); Receita Federal (alíquotas do crédito presumido, página do programa Mais Leite Saudável: confirmar vigência) e NT RFB 012/2026. Estimativa preliminar sujeita a validação técnica.");

// ───────────── 16. PRÓXIMOS PASSOS
s = nova("Como começamos", "Os primeiros 90 dias e o que precisamos para dimensionar o resultado");
cartao(s, MX, TOPO, 5.95, 4.3, "O que precisamos ver (sob confidencialidade)", "• DRE e balanço dos dois últimos anos, por linha de produto quando houver\n• Apuração de PIS/COFINS e do crédito presumido do leite; EFD-Contribuições\n• Separação do ato cooperativo e não cooperativo\n• Extrato de dívidas (inclusive consulta ao histórico de crédito) e custo médio\n• Carteira a receber com prazos (aging) e inadimplência\n• Composição das compras de leite (associados, outras cooperativas)", { fs: 11.5 });
cartao(s, MX + 6.1, TOPO, 6.0, 4.3, "O caminho em 90 dias", "Semanas 1–2: conversa com a diretoria, confidencialidade e documentos.\nSemanas 3–4: mapa da empresa e linha de base de margem, prazo e dívida (passo 1).\nSemanas 5–8: primeiro passo de execução, no ponto de maior retorno.\nSemanas 9–10: primeiro mapa de valor e desenho do passo seguinte.\nSemanas 11–13: encontro trimestral com a diretoria.\n\nVocê terá um gestor de projeto que conduz tudo e conecta as nossas equipes.", { fs: 13 });

// ───────────── 17. FONTES
s = nova("Fontes e avisos", "Fontes oficiais e públicas, com data de consulta");
s.addText([
  { text: "Oficiais\n", options: { bold: true, fontFace: F, fontSize: 10, color: C.texto } },
  { text: "IBGE, Pesquisa Trimestral do Leite, SIDRA tabela 1086 (série até o 2º tri/2026), consulta em 21/10/2026.\nBanco Central do Brasil, SGS 432 (meta Selic) e 20725 (taxa média do capital de giro de pessoas jurídicas, % a.a.), consulta em 21/10/2026.\nMDIC, Resolução Gecex nº 907, de 03/06/2026 (direito antidumping, leite em pó, Argentina e Uruguai), gov.br/mdic.\nMAPA, Câmara Setorial do Leite e Derivados, 76ª reunião, 07/04/2026, “Conjuntura do mercado de leite” (dados Embrapa/ICPLeite).\nDERAL/SEAB-PR, boletim semanal nº 18/2026 (importação de lácteos no 1º tri/2026); a conferir no Comex Stat do MDIC.\nReceita Federal: Nota Técnica RFB nº 012/2026 (crédito presumido do art. 8º da Lei 10.925/2004 e LC 224/2025) e página do programa Mais Leite Saudável (alíquotas; confirmar vigência).\nLei Complementar nº 214/2025 (Anexo I, cesta básica) e Lei Complementar nº 224/2025, Planalto. Lei nº 5.764/1971 (ato cooperativo).\n", options: { fontFace: F, fontSize: 10.5, color: C.texto_2, breakLine: true } },
  { text: "Públicas, sobre a cooperativa\n", options: { bold: true, fontFace: F, fontSize: 10, color: C.texto } },
  { text: "Cooperativa Santa Clara, site institucional (coopsantaclara.com.br/quem-somos), consulta em 21/10/2026.\nJornal do Comércio: 17/08/2025 (investimentos, associados, vendas fora do RS), 16/08/2024 (declarações do presidente) e jul/2026 (projeção de R$ 3 bilhões).\n", options: { fontFace: F, fontSize: 10.5, color: C.texto_2, breakLine: true } },
  { text: "Avisos\n", options: { bold: true, fontFace: F, fontSize: 10, color: C.texto } },
  { text: "Pré-análise de caráter geral, sem acesso aos dados internos da cooperativa. Não constitui parecer jurídico ou tributário nem oferta de crédito. As faixas são ilustrativas, com premissas indicadas, e dependem de documentos e de validação técnica. Valor, prazo e êxito não são prometidos.", options: { fontFace: F, fontSize: 10.5, color: C.texto_2 } },
], { x: MX, y: TOPO - 0.1, w: W - 2 * MX, h: 4.9, margin: 0, valign: "top", isTextBox: true, paraSpaceAfter: 2 });

pres.writeFile({ fileName: OUT }).then(() => console.log("ok", OUT));
