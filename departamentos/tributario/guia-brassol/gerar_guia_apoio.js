#!/usr/bin/env node
// Gera o Guia da reunião (Word, A4) a partir de conteudo.json, no padrão visual Save (Design System v0.5, modo claro).
// Uso: NODE_PATH=<node_modules com docx> node gerar_guia_docx.js [conteudo.json] [saida.docx]
// Só gera arquivo local; nada é enviado.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType, BorderStyle,
  Header, Footer, PageNumber, HeadingLevel, LevelFormat, PageBreak, TableLayoutType, VerticalAlign, ImageRun, InternalHyperlink, Bookmark,
} = require("docx");

const PADRAO = path.join(process.env.HOME, "agentes-partners/departamentos/marketing-marca/padrao");
const MARCA = JSON.parse(fs.readFileSync(path.join(PADRAO, "marca.json"), "utf8"));
const LOGO = fs.readFileSync(path.join(PADRAO, MARCA.logos.fundo_claro));
const logo = (w) => new ImageRun({ type: "png", data: LOGO, transformation: { width: w, height: Math.round(w * MARCA.logos.proporcao_logo) } });
const hex = (c) => c.replace("#", "");
const K = MARCA.claro;
const PRETO = hex(K.texto), OURO = hex(K.ouro_texto), OURO_FAIXA = hex(K.ouro), CINZA = hex(K.texto_2), BRANCO = "FFFFFF", ZEBRA = hex(K.fundo_2), BORDA = hex(K.borda), CAB = hex(MARCA.escuro.fundo), SUAVE = hex(K.ouro_suave);
const FONTE = MARCA.fontes.sans, MONO = MARCA.fontes.mono;
const ENTRADA = path.join(__dirname, "conteudo.json");
const SAIDA = process.argv[2] || path.join(__dirname, "Guia-de-Apoio-Brassol.docx");
const C = JSON.parse(fs.readFileSync(ENTRADA, "utf8"));
const LARGURA = 11906 - 2 * 1134;
const R = (o) => new TextRun({ font: FONTE, ...o });

function runs(texto, base = {}) {
  texto = String(texto == null ? "" : texto);
  const out = []; const re = /(\*\*[^*]+\*\*)/g; let i = 0, m;
  while ((m = re.exec(texto))) {
    if (m.index > i) out.push(R({ text: texto.slice(i, m.index), ...base }));
    out.push(R({ text: m[0].slice(2, -2), ...base, bold: true })); i = m.index + m[0].length;
  }
  if (i < texto.length) out.push(R({ text: texto.slice(i), ...base }));
  return out;
}
const P = (texto, o = {}) => new Paragraph({ spacing: { before: o.before ?? 40, after: o.after ?? 90, line: 276 }, alignment: o.align, keepNext: o.keepNext, children: runs(texto, o.run || {}) });
const H1 = (t, id, quebra = true) => new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: quebra, children: [new Bookmark({ id, children: [R({ text: t })] })] });
const H2 = (t) => new Paragraph({ spacing: { before: 220, after: 80 }, keepNext: true, children: [R({ text: t.toUpperCase(), font: MONO, size: 17, bold: true, color: OURO, characterSpacing: 40 })] });
const BUL = (t, nivel = 0) => new Paragraph({ numbering: { reference: "bolinha", level: nivel }, spacing: { before: 0, after: 60, line: 270 }, children: runs(t) });
const LISTA = (xs) => (xs || []).map((x) => BUL(x));
const GAP = (n = 80) => new Paragraph({ spacing: { before: 0, after: n }, children: [] });
const borda = (c = BORDA, s = 4) => ({ style: BorderStyle.SINGLE, size: s, color: c });
const NONE = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };

function celula(texto, w, o = {}) {
  const filhos = (Array.isArray(texto) ? texto : [texto]).map((t) => new Paragraph({ spacing: { before: 0, after: 30, line: 250 }, children: runs(t, { size: o.size || 18, color: o.cor || PRETO, bold: o.bold, font: o.mono ? MONO : FONTE }) }));
  return new TableCell({ width: { size: w, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: "auto", fill: o.fill || BRANCO }, margins: { top: 70, bottom: 50, left: 100, right: 100 }, verticalAlign: VerticalAlign.TOP, children: filhos });
}
function tabela(cab, linhas, pesos, o = {}) {
  const w = pesos.map((x) => Math.floor(x * LARGURA)); w[w.length - 1] += LARGURA - w.reduce((a, b) => a + b, 0);
  const b = borda();
  return new Table({
    width: { size: LARGURA, type: WidthType.DXA }, columnWidths: w, layout: TableLayoutType.FIXED,
    borders: { top: b, bottom: b, left: b, right: b, insideHorizontal: b, insideVertical: b },
    rows: [new TableRow({ tableHeader: true, cantSplit: true, children: cab.map((c, i) => celula(c, w[i], { fill: CAB, cor: BRANCO, bold: true, size: 17 })) }),
      ...linhas.map((r, k) => new TableRow({ cantSplit: true, children: r.map((c, i) => celula(c, w[i], { fill: k % 2 ? ZEBRA : BRANCO, bold: i === 0 && o.negritoPrimeira })) }))],
  });
}
function caixa(rotulo, texto, fill = SUAVE, faixa = OURO_FAIXA) {
  return new Table({
    width: { size: LARGURA, type: WidthType.DXA }, columnWidths: [LARGURA], layout: TableLayoutType.FIXED,
    borders: { top: NONE, bottom: NONE, right: NONE, left: { style: BorderStyle.SINGLE, size: 36, color: faixa }, insideHorizontal: NONE, insideVertical: NONE },
    rows: [new TableRow({ cantSplit: true, children: [new TableCell({ width: { size: LARGURA, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: "auto", fill }, margins: { top: 110, bottom: 100, left: 200, right: 160 },
      children: [new Paragraph({ spacing: { before: 0, after: 40 }, children: [R({ text: rotulo.toUpperCase(), font: MONO, size: 16, bold: true, color: OURO, characterSpacing: 40 })] }),
        ...(Array.isArray(texto) ? texto : [texto]).map((t) => new Paragraph({ spacing: { before: 0, after: 40, line: 276 }, children: runs(t, { size: 21 }) }))] })] })],
  });
}


// ---------- fontes literais (texto exato enviado pelo Luis)
const CAT = fs.readFileSync(path.join(__dirname, "../catalogo-teses-save-completo.md"), "utf8");
const FONTES = fs.readFileSync(path.join(__dirname, "../../produtos/fontes-produtos-guia-parceiro.md"), "utf8");
function bloco(md, inicio) {
  const i = md.indexOf(inicio); if (i < 0) throw new Error("não achei: " + inicio);
  const resto = md.slice(i);
  const fim = resto.slice(3).search(/\n(## |---)/);
  return (fim < 0 ? resto : resto.slice(0, fim + 3)).split("\n").slice(1).map((l) => l.trim()).filter(Boolean);
}
function textoExato(linhas) {
  return linhas.map((l) => {
    const m = l.match(/^(\d)\.\s+\*\*([^*]+):\*\*\s*(.*)$/);
    if (!m) return P(l, { after: 70, run: { size: 20 } });
    const interno = /^Ticket/.test(m[2]);
    return new Paragraph({ spacing: { before: 0, after: 70, line: 264 }, children: [R({ text: m[1] + ". " + m[2] + (interno ? " (interno, não citar ao cliente)" : "") + ": ", bold: true, size: 20, color: interno ? CINZA : PRETO }), ...runs(m[3], { size: 20, color: interno ? CINZA : PRETO })] });
  });
}
const tituloTese = (t, sub) => new Paragraph({ spacing: { before: 300, after: 40 }, keepNext: true, border: { top: { style: BorderStyle.SINGLE, size: 6, color: OURO_FAIXA, space: 6 } }, children: [R({ text: t, bold: true, size: 26 })] });
const subTese = (t) => new Paragraph({ spacing: { before: 0, after: 80 }, keepNext: true, children: [R({ text: t, size: 18, color: CINZA, font: MONO })] });

// itens da parte 1, na ordem do parecer
const ITENS = [
  { cod: "T01", ini: "## T01", titulo: "Crédito de PIS e COFINS nas aquisições", parecer: "Linha do parecer: PIS/COFINS · Aquisições (ADM) · R$ 5.692.410,47", f: "F1" },
  { cod: "T08", ini: "## T08", titulo: "Crédito de PIS e COFINS em conta gráfica", parecer: "Linha do parecer: Crédito de PIS/Cofins acumulado em conta gráfica (ADM) · R$ 1.103.564,10", f: "F2" },
  { cod: "T02", ini: "## T02", titulo: "Crédito de PIS e COFINS sobre insumos", parecer: "Linha do parecer: PIS/COFINS · Insumos (ADM) · R$ 237.110,65", f: "F3" },
  { cod: "T01", nota: true, titulo: "Aquisições de produtos industrializados (mesma tese T01)", parecer: "Linha do parecer: PIS/COFINS · Aquisições de Produtos Industrializados (ADM) · R$ 29.849,44", f: "F4",
    aviso: "É a mesma tese T01, aplicada às aquisições de produtos industrializados. A tese T01 vale tanto para produtos apenas comercializados quanto para industrializados, e as mesmas regras se aplicam: texto, fundamento, análise de aptidão, período e perfil são os da T01, na página anterior. O parecer separa a linha só para mostrar o valor de cada grupo." },
  { cod: "T04", ini: "## T04", titulo: "Exclusão do ICMS-ST da base de cálculo do PIS e da COFINS", parecer: "Linha do parecer: PIS/COFINS · Exclusão do ICMS/ST da Base de Cálculo (ADM) · R$ 96.409,47", f: "F5" },
  { cod: "T12", ini: "## T12", titulo: "Revisão da Contribuição Previdenciária Patronal (CPP): verbas indenizatórias", parecer: "Linha do parecer: Previdenciário · Verbas Indenizatórias (PREV) · R$ 312.823,97", f: "F6" },
];
const ACOES = [
  { cod: "T05", ini: "## T05", titulo: "Exclusão do PIS e da COFINS de suas próprias bases", parecer: "Ações já ajuizadas pela Brassol (2009, trânsito em julgado em 10/03/2022, e 2024, aguardando decisão). Informativo, fora da proposta.", f: "F7" },
  { cod: "T03", ini: "## T03", titulo: "Exclusão do ICMS da base de cálculo do PIS e da COFINS", parecer: "Ação já ajuizada pela Brassol (2007, trânsito em julgado em 19/07/2023). Informativo, fora da proposta.", f: "F7" },
];
const itemPT = (it) => [tituloTese(`${it.cod !== "—" ? it.cod + " · " : ""}${it.titulo}`), subTese(it.parecer), ...(it.aviso ? [caixa("Mesma regra da T01", it.aviso)] : textoExato(bloco(CAT, it.ini)))];

const VISAO = bloco(CAT, "## Visão geral: recuperação tributária");
const P01 = bloco(CAT, "## P01");
const PASSIVO = bloco(FONTES, "## Gestão de Passivo (institucional)");

// ---------- documento
const M = C.meta;
const capa = [
  new Paragraph({ spacing: { before: 0, after: 0 }, children: [logo(250)] }),
  new Paragraph({ spacing: { before: 120, after: 0 }, children: [R({ text: "ÁREA PARTNERS", size: 18, color: CINZA, characterSpacing: 60 })] }),
  new Paragraph({ spacing: { before: 2600, after: 0 }, children: [] }),
  new Paragraph({ spacing: { before: 0, after: 100 }, border: { top: { style: BorderStyle.SINGLE, size: 36, color: OURO_FAIXA, space: 18 } }, children: [R({ text: "Guia de apoio", bold: true, size: 72 })] }),
  new Paragraph({ spacing: { before: 0, after: 360 }, children: [R({ text: "Brassol", bold: true, size: 72 })] }),
  new Paragraph({ spacing: { before: 0, after: 100 }, children: [R({ text: "Teses, produtos e serviços do parecer, no texto do time técnico, e quebra de objeções", size: 28, color: CINZA })] }),
  new Paragraph({ spacing: { before: 0, after: 100 }, children: [R({ text: `${M.cliente} · CNPJ ${M.cnpj}`, size: 22, color: CINZA })] }),
  new Paragraph({ spacing: { before: 0, after: 400 }, children: [R({ text: "Parecer de 13/10/2026 · Para uso junto com a apresentação", size: 22, color: CINZA })] }),
  new Paragraph({ children: [R({ text: "Uso interno do parceiro · não entregar ao cliente", bold: true, size: 24, color: OURO })] }),
];

const usar = [
  H1("Como usar", "s_usar", false),
  P("**Parte 1** traz, sem alteração, o texto do time técnico de cada tese e produto que aparece no parecer da Brassol. É para estudar antes da reunião e para consultar quando o cliente perguntar. **Parte 2** traz as objeções mais prováveis e como responder, com base nesses mesmos textos."),
  tabela(["Linha do parecer", "Valor estimado", "Texto na Parte 1", "Objeções (Parte 2)"],
    [["PIS/COFINS · Aquisições", "R$ 5.692.410,47", "T01", "página da Parte 2"], ["PIS/COFINS · Crédito acumulado em conta gráfica", "R$ 1.103.564,10", "T08", ""], ["PIS/COFINS · Insumos", "R$ 237.110,65", "T02", ""], ["PIS/COFINS · Aquisições de produtos industrializados", "R$ 29.849,44", "T01 (mesma tese)", ""], ["PIS/COFINS · Exclusão do ICMS/ST da base", "R$ 96.409,47", "T04", ""], ["Previdenciário · Verbas indenizatórias", "R$ 312.823,97", "T12", ""], ["Ações já ajuizadas (informativo)", "sem valor", "T05, T03 e T12", ""], ["Passivo federal e economia futura", "sem valor no parecer", "Gestão de Passivo e P01", ""]].map((r, i) => [r[0], r[1], r[2], ["Aquisições", "Conta gráfica", "Insumos", "Prod. industrializados", "ICMS/ST", "Previdenciário", "Ações ajuizadas", "Passivo e serviço"][i]]), [0.38, 0.17, 0.25, 0.2]),
  GAP(),
  caixa("Três cuidados em qualquer resposta", ["Os valores são **estimativas de análise parcial** (10/2021 a 08/2026), sujeitas a ajuste na execução. Não são promessa.", "Não prometer resultado nem prazo de recebimento. Preço e percentual de êxito só em campo interno (item 8 de cada texto).", "O que for jurídico (ações, autos, prazos) é com advogado habilitado. Crédito e funding são com instituição autorizada."]),
];

const parte1 = [
  H1("Parte 1 · Texto do time técnico", "s_p1"),
  P("Texto fiel aos resumos enviados pelo time técnico. Os itens seguem a numeração original (1 O que é, 2 Fundamento, 3 Impacto, 4 Benefícios, 5 Atuação, 6 Período, 7 Perfil, 8 Ticket).", { run: { color: CINZA } }),
  H2("Base de todas as teses: recuperação tributária"), ...textoExato(VISAO),
  H2("Teses com valor no parecer"), ...ITENS.flatMap(itemPT),
  H2("Ações já ajuizadas pela Brassol (informativo)"), ...ACOES.flatMap(itemPT),
  P("A verba indenizatória da ação de 2009 é a mesma tese da T12, acima.", { run: { color: CINZA, size: 19 } }),
  H2("Passivo federal"), tituloTese("Gestão de Passivo (texto institucional)"), subTese("Parecer: pendências ativas na Receita e na PGFN; possibilidade de redução do passivo, sem valor"), ...PASSIVO.map((l) => P(l, { after: 70, run: { size: 20 } })),
  H2("Economia futura e parametrização da contabilidade"), tituloTese("P01 · Planejamento Tributário"), subTese("Parecer: redução das contribuições futuras (0,9% a 1,5%) e parametrização da contabilidade"), ...textoExato(P01),
];

// parte 2: 3 objeções por ficha, as mais prováveis
const QTD = { F1: 3, F2: 3, F3: 3, F4: 2, F5: 3, F6: 3, F7: 3, F8: 3, F9: 3 };
const parte2 = [
  H1("Parte 2 · Objeções e como responder", "s_p2"),
  P("Respostas curtas, apoiadas nos textos da Parte 1. Admitir o limite quando ele existe, não prometer valor e terminar com uma pergunta ou próximo passo.", { run: { color: CINZA } }),
  ...C.fichas.map((f) => f.id !== "F4" ? f : { ...f, objecoes: [
    { o: "Por que essa linha é separada de Aquisições?", r: "É a mesma tese, aplicada às compras de produtos industrializados. O parecer mostra o valor de cada grupo em separado, e as regras são as mesmas. Só seguimos se a análise das notas confirmar." },
    { o: "O valor é pequeno, vale a pena?", r: "É estimativa preliminar, e o valor final só sai depois de conferir as notas. A análise é a mesma das Aquisições, então não acrescenta trabalho. Posso pedir o relatório de entradas?" },
    { o: "Sorvete é industrializado, então não dá crédito?", r: "A tese olha as compras para revenda sem PIS/COFINS, sejam comercializadas ou industrializadas. Sorvete é tributado e já gera crédito comum, então não é o foco. O time confere quais produtos entram na linha." }] }).flatMap((f) => [
    H2(`${f.nome}`),
    tabela(["O cliente diz", "Como responder"], f.objecoes.slice(0, QTD[f.id] || 3).map((x) => [`“${x.o}”`, x.r]), [0.3, 0.7]),
  ]),
  GAP(160),
  caixa("Se perguntarem algo que não consta do parecer", C.roteiro && C.roteiro.se_perguntarem_do_que_nao_consta ? C.roteiro.se_perguntarem_do_que_nao_consta : "Anotar a pergunta e responder depois com o time técnico."),
];

const doc = new Document({
  creator: "Área Partners · Save Company", title: "Guia de apoio · Brassol",
  fonts: [{ name: FONTE, data: fs.readFileSync(path.join(PADRAO, "fontes/IBMPlexSans-Regular.ttf")) }], embedFonts: true,
  styles: { default: { document: { run: { font: FONTE, size: 21, color: PRETO } } },
    paragraphStyles: [{ id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 30, bold: true, color: PRETO, font: FONTE },
      paragraph: { spacing: { before: 120, after: 160 }, outlineLevel: 0, keepNext: true, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: OURO_FAIXA, space: 4 } } } }] },
  numbering: { config: [{ reference: "bolinha", levels: [0, 1].map((n) => ({ level: n, format: LevelFormat.BULLET, text: "▪", alignment: AlignmentType.LEFT, style: { run: { color: OURO }, paragraph: { indent: { left: 360 + n * 360, hanging: 260 } } } })) }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1300, bottom: 1200, left: 1134, right: 1134, header: 560, footer: 560 } }, titlePage: true },
    headers: { default: new Header({ children: [new Paragraph({ border: { bottom: borda(OURO, 4) }, tabStops: [{ type: "right", position: LARGURA }], children: [logo(78), R({ text: "   Guia de apoio · Brassol", size: 16, color: CINZA }), R({ text: "\tUso interno · não entregar ao cliente", size: 16, color: CINZA })] })] }), first: new Header({ children: [new Paragraph({ children: [] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [R({ children: ["Página ", PageNumber.CURRENT, " de ", PageNumber.TOTAL_PAGES], size: 16, color: CINZA })] })] }), first: new Footer({ children: [new Paragraph({ children: [] })] }) },
    children: [...capa, ...usar, ...parte1, ...parte2],
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(SAIDA, b); console.log("ok", SAIDA); });
