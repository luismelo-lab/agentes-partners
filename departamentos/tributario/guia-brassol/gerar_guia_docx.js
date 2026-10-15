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
const ENTRADA = process.argv[2] || path.join(__dirname, "conteudo.json");
const SAIDA = process.argv[3] || path.join(__dirname, "Guia-da-Reuniao-Brassol.docx");
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

// ---------- seções
const corpo = [];
const indiceItens = [];

// capa
const M = C.meta;
const capa = [
  new Paragraph({ spacing: { before: 0, after: 0 }, children: [logo(250)] }),
  new Paragraph({ spacing: { before: 120, after: 0 }, children: [R({ text: "ÁREA PARTNERS", size: 18, color: CINZA, characterSpacing: 60 })] }),
  new Paragraph({ spacing: { before: 2800, after: 0 }, children: [] }),
  new Paragraph({ spacing: { before: 0, after: 100 }, border: { top: { style: BorderStyle.SINGLE, size: 36, color: OURO_FAIXA, space: 18 } }, children: [R({ text: "Guia da reunião", bold: true, size: 72, color: PRETO })] }),
  new Paragraph({ spacing: { before: 0, after: 360 }, children: [R({ text: M.cliente_curto || "Brassol", bold: true, size: 72, color: PRETO })] }),
  new Paragraph({ spacing: { before: 0, after: 100 }, children: [R({ text: M.subtitulo, size: 28, color: CINZA })] }),
  new Paragraph({ spacing: { before: 0, after: 100 }, children: [R({ text: `${M.cliente} · CNPJ ${M.cnpj}`, size: 22, color: CINZA })] }),
  new Paragraph({ spacing: { before: 0, after: 400 }, children: [R({ text: M.data, size: 22, color: CINZA })] }),
  new Paragraph({ spacing: { before: 0, after: 0 }, children: [R({ text: "Uso interno do parceiro e do consultor · não entregar ao cliente", bold: true, size: 24, color: OURO })] }),
];

// como usar
const cu = C.como_usar;
const secUsar = [H1("Como usar este guia na reunião", "s_usar", false), P(cu.intro),
  H2("Mapa da apresentação: o que fazer em cada slide"),
  tabela(["Slide", "Tema", "Seção do guia", "O que o parceiro faz"], cu.mapa_slides.map((s) => [s.slide, s.tema, s.secao_do_guia, s.o_que_o_parceiro_faz]), [0.07, 0.2, 0.18, 0.55])];
indiceItens.push(["s_usar", "Como usar este guia na reunião"]);

// roteiro (opcional, escrito pelo comercial)
let secRoteiro = [];
if (C.roteiro) {
  const r = C.roteiro;
  secRoteiro = [H1("Roteiro da reunião", "s_roteiro"), ...(r.abertura ? [caixa("Abertura", r.abertura)] : []), GAP(),
    tabela(["Momento", "Slides", "O que dizer", "Abra a ficha"], (r.passos || []).map((x) => [x.momento, x.slides, x.o_que_dizer, x.abra_a_ficha]), [0.17, 0.09, 0.58, 0.16]),
    ...(r.fechamento ? [GAP(), caixa("Fechamento", r.fechamento)] : []), ...(r.se_perguntarem_do_que_nao_consta ? [GAP(), caixa("Se perguntarem por algo que não consta do parecer", r.se_perguntarem_do_que_nao_consta, ZEBRA, CINZA)] : [])];
  indiceItens.push(["s_roteiro", "Roteiro da reunião"]);
}

// resumo
const rp = C.resumo_do_parecer;
const secResumo = [H1("O parecer em uma página", "s_resumo"),
  tabela(["Campo", "Dado"], rp.empresa.map((e) => [e.campo, e.valor]), [0.3, 0.7], { negritoPrimeira: true }), GAP(),
  H2("As seis teses do parecer"),
  tabela(["Tese (nome do parecer)", "Valor", "Via", "Em uma linha"], [...rp.teses.map((t) => [t.nome, t.valor, t.via, t.em_uma_linha]), ["**Soma das linhas**", `**${rp.total}**`, "", rp.o_que_o_parecer_diz_sobre_o_total]], [0.3, 0.14, 0.08, 0.48]), GAP(),
  H2("Ações já ajuizadas pela Brassol"),
  tabela(["Ação", "Tese", "Situação", "Prazo estimado"], rp.processos.map((x) => [x.acao, x.tese, x.situacao, x.prazo_estimado]), [0.16, 0.3, 0.34, 0.2]),
  P(rp.litispendencia, { before: 80 }),
  H2("Passivo federal"), P(rp.passivo),
  H2("Modelo do serviço"), P(rp.modelo_do_servico),
  H2("O que a revisão técnica confirma antes do valor final"), ...LISTA(rp.o_que_a_revisao_tecnica_confirma_antes_do_valor_final)];
indiceItens.push(["s_resumo", "O parecer em uma página"]);

// conceitos
const cc = C.conceitos;
const secConceitos = [H1("Base: vias, tipos de pedido e período", "s_conceitos"),
  H2("Por qual via a Save atua"), tabela(["Via", "Em 20 segundos"], cc.vias.map((v) => [`**${v.sigla}** · ${v.nome}`, v.em_20_segundos]), [0.3, 0.7]),
  H2("Como o dinheiro volta para o caixa"), tabela(["Tipo de pedido", "Em 20 segundos"], cc.especies.map((e) => [e.nome, e.em_20_segundos]), [0.3, 0.7]),
  H2("Período"), P(cc.periodo)];
indiceItens.push(["s_conceitos", "Base: vias, tipos de pedido e período"]);

// fichas
const secFichas = [];
for (const f of C.fichas) {
  const id = "f_" + f.id;
  indiceItens.push([id, `${f.id} · ${f.nome}`]);
  secFichas.push(new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new Bookmark({ id, children: [R({ text: `${f.id} · ${f.nome}` })] })] }));
  secFichas.push(new Paragraph({ spacing: { before: 0, after: 100 }, children: [R({ text: "VALOR NO PARECER  ", font: MONO, size: 16, color: OURO, bold: true }), R({ text: f.valor_no_parecer, bold: true, size: 24 }), R({ text: `     ·     ${f.slides}`, size: 18, color: CINZA })] }));
  secFichas.push(caixa("Em 20 segundos", f.em_20_segundos), GAP(60));
  secFichas.push(H2("O que o parecer diz"), P(f.o_que_o_parecer_diz));
  secFichas.push(H2("Técnico, em linguagem comercial"), tabela(["Termo", "O técnico diz", "Você diz"], f.tecnico_traduzido.map((t) => [`**${t.termo}**`, t.tecnico, t.comercial]), [0.2, 0.34, 0.46]));
  secFichas.push(H2("Leitura para a Brassol"), ...LISTA(f.leitura_para_a_brassol));
  secFichas.push(H2("O que o time técnico confirma antes do valor final"), ...LISTA(f.o_que_confirmar));
  secFichas.push(H2("Riscos e vetos"), ...LISTA(f.riscos_e_vetos));
  secFichas.push(H2("Documentos para pedir"), ...LISTA(f.documentos));
  secFichas.push(H2("Perguntas para fazer ao dono"), ...LISTA(f.perguntas));
  secFichas.push(H2("Quebra de objeções"), tabela(["O cliente diz", "Você responde"], f.objecoes.map((o) => [`“${o.o}”`, o.r]), [0.32, 0.68], { negritoPrimeira: true }), GAP(60));
  secFichas.push(caixa("Uso interno · não mostrar ao cliente", f.remuneracao_interna, ZEBRA, CINZA));
  if (f.cuidados && f.cuidados.length) { secFichas.push(H2("Cuidados"), ...LISTA(f.cuidados)); }
  secFichas.push(P(`Fonte: ${f.fonte}`, { run: { size: 16, color: CINZA }, before: 100 }));
}

// objeções gerais, glossário, pendências
const secFim = [H1("Quebra de objeções gerais", "s_gerais"), tabela(["O cliente diz", "Você responde"], C.objecoes_gerais.map((o) => [`“${o.o}”`, o.r]), [0.3, 0.7], { negritoPrimeira: true }),
  H1("Glossário", "s_glossario"), tabela(["Termo", "Em português de dono de empresa"], C.glossario.map((g) => [`**${g.termo}**`, g.significa]), [0.26, 0.74]),
  H1("Pendências para validar", "s_pendencias"), P("Pré-análise: nada aqui substitui a validação do técnico e do advogado responsáveis. O valor final só existe depois dela."),
  tabela(["Tema", "Quem valida", "O que falta"], C.pendencias_para_validar.map((p) => [p.tema, p.quem, p.o_que]), [0.28, 0.17, 0.55], { negritoPrimeira: true })];
indiceItens.push(["s_gerais", "Quebra de objeções gerais"], ["s_glossario", "Glossário"], ["s_pendencias", "Pendências para validar"]);

// índice com links
const indice = [new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [R({ text: "Índice" })] }),
  ...indiceItens.map(([id, nome], k) => new Paragraph({ spacing: { before: 0, after: 90 }, border: { bottom: borda(BORDA, 2) },
    children: [R({ text: String(k + 1).padStart(2, "0") + "   ", bold: true, color: OURO }), new InternalHyperlink({ anchor: id, children: [R({ text: nome, color: PRETO })] })] }))];

const doc = new Document({
  creator: "Área Partners · Save Company", title: "Guia da reunião · " + (M.cliente_curto || ""),
  fonts: [{ name: FONTE, data: fs.readFileSync(path.join(PADRAO, "fontes/IBMPlexSans-Regular.ttf")) }], embedFonts: true,
  styles: { default: { document: { run: { font: FONTE, size: 21, color: PRETO } } },
    paragraphStyles: [{ id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 30, bold: true, color: PRETO, font: FONTE },
      paragraph: { spacing: { before: 120, after: 160 }, outlineLevel: 0, keepNext: true, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: OURO_FAIXA, space: 4 } } } }] },
  numbering: { config: [{ reference: "bolinha", levels: [0, 1].map((n) => ({ level: n, format: LevelFormat.BULLET, text: n === 0 ? "▪" : "–", alignment: AlignmentType.LEFT, style: { run: { color: OURO }, paragraph: { indent: { left: 360 + n * 360, hanging: 260 } } } })) }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1300, bottom: 1200, left: 1134, right: 1134, header: 560, footer: 560 } }, titlePage: true },
    headers: { default: new Header({ children: [new Paragraph({ border: { bottom: borda(OURO, 4) }, tabStops: [{ type: "right", position: LARGURA }],
      children: [logo(78), R({ text: "   Guia da reunião · " + (M.cliente_curto || ""), size: 16, color: CINZA }), R({ text: "\tUso interno · não entregar ao cliente", size: 16, color: CINZA })] })] }), first: new Header({ children: [new Paragraph({ children: [] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [R({ children: ["Página ", PageNumber.CURRENT, " de ", PageNumber.TOTAL_PAGES], size: 16, color: CINZA })] })] }),
      first: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [R({ children: ["Página ", PageNumber.CURRENT, " de ", PageNumber.TOTAL_PAGES], size: 16, color: CINZA })] })] }) },
    children: [...capa, ...indice, ...secUsar, ...secRoteiro, ...secResumo, ...secConceitos, ...secFichas, ...secFim],
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(SAIDA, b); console.log("ok", SAIDA, "fichas:", C.fichas.length); });
