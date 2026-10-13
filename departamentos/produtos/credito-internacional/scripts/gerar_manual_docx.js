#!/usr/bin/env node
// Gera o Manual Operacional Interno (.docx) a partir de 13-manual-operacional-interno.md.
// Uso: node gerar_manual_docx.js <saida.docx>
// Só converte o texto (sem cortar nem reescrever). Não envia nada.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, BorderStyle, Header, Footer, PageNumber, HeadingLevel, LevelFormat, PageBreak,
  TableLayoutType, VerticalAlign, ImageRun,
} = require("docx");
// Padrão visual: Design System Save v0.5 (marketing-marca/padrao/marca.json), adotado em 07/10/2026.
const PADRAO = path.join(process.env.HOME, "agentes-partners/departamentos/marketing-marca/padrao");
const MARCA = JSON.parse(fs.readFileSync(path.join(PADRAO, "marca.json"), "utf8"));
const LOGO = fs.readFileSync(path.join(PADRAO, MARCA.logos.fundo_claro));  // logo Save Co. para fundo claro (1600×281)
const logo = (w) => new ImageRun({ type: "png", data: LOGO, transformation: { width: w, height: Math.round(w * MARCA.logos.proporcao_logo) } });

const hex = (c) => c.replace("#", "");
const K = MARCA.claro;
const PRETO = hex(K.texto), OURO = hex(K.ouro_texto), OURO_FAIXA = hex(K.ouro), CINZA = hex(K.texto_2), BRANCO = "FFFFFF",
  ZEBRA = hex(K.fundo_2), BORDA = hex(K.borda), CAB_TABELA = hex(MARCA.escuro.fundo);
const FONTE = MARCA.fontes.sans;  // IBM Plex Sans; o Word troca por uma fonte parecida se ela não estiver instalada
const BASE = path.resolve(__dirname, "..");
const MD = fs.readFileSync(path.join(BASE, process.env.DOC_MD || "13-manual-operacional-interno.md"), "utf8");
const SAIDA = process.argv[2] || path.join(BASE, "Credito-Internacional-Manual-Operacional-Interno-v1.0.docx");

const LARGURA = 11906 - 2 * 1134; // A4, margens de 2 cm
const R = (o) => new TextRun({ font: FONTE, ...o });

// ---------- texto inline: **negrito**, *itálico*, `código`
function runs(texto, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)/g;
  let i = 0, m;
  while ((m = re.exec(texto))) {
    if (m.index > i) out.push(R({ text: texto.slice(i, m.index), ...base }));
    const t = m[0];
    if (t.startsWith("**")) out.push(R({ text: t.slice(2, -2), ...base, bold: true }));
    else if (t.startsWith("`")) out.push(R({ text: t.slice(1, -1), ...base, font: MARCA.fontes.mono }));
    else out.push(R({ text: t.slice(1, -1), ...base, italics: true }));
    i = m.index + t.length;
  }
  if (i < texto.length) out.push(R({ text: texto.slice(i), ...base }));
  return out;
}

// ---------- numeração: um "reference" por lista numerada (para manter o número inicial)
const numeracoes = [{
  reference: "bolinha",
  levels: [0, 1].map((n) => ({
    level: n, format: LevelFormat.BULLET, text: n === 0 ? "▪" : "–", alignment: AlignmentType.LEFT,
    style: { run: { color: OURO }, paragraph: { indent: { left: 360 + n * 360, hanging: 260 } } },
  })),
}];
function novaNumeracao(inicio, nivel) {
  const ref = `num${numeracoes.length}`;
  numeracoes.push({
    reference: ref,
    levels: [{
      level: 0, format: LevelFormat.DECIMAL, text: "%1.", start: inicio, alignment: AlignmentType.LEFT,
      style: { run: { bold: true, color: OURO }, paragraph: { indent: { left: 400 + nivel * 360, hanging: 320 } } },
    }],
  });
  return ref;
}

// ---------- tabela
function celula(texto, largura, cab, zebra, alinhar) {
  return new TableCell({
    width: { size: largura, type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, color: "auto", fill: cab ? CAB_TABELA : zebra ? ZEBRA : BRANCO },
    margins: { top: 70, bottom: 70, left: 100, right: 100 },
    verticalAlign: cab ? VerticalAlign.CENTER : VerticalAlign.TOP,
    children: [new Paragraph({
      spacing: { before: 0, after: 0, line: 252 },
      alignment: alinhar || AlignmentType.LEFT,
      children: runs(texto, cab ? { color: BRANCO, bold: true, size: 18, font: FONTE } : { size: 18, font: FONTE }),
    })],
  });
}
function larguras(n, cab) {
  // proporções por tabela, conforme o conteúdo de cada coluna
  const chave = cab.join("|");
  const mapas = {
    "Peça|Quem é|Papel": [0.2, 0.3, 0.5],
    "|**Fundo americano (FNDC, Flórida)**|**Estrutura suíça**": [0.2, 0.4, 0.4],
    "#|Etapa|Quem conduz|O que acontece|Prazo de referência": [0.05, 0.15, 0.2, 0.4, 0.2],
    "O cliente diz|A resposta": [0.36, 0.64],
    "Alternativa|Custo de referência": [0.55, 0.45],
  };
  const p = mapas[chave] || Array(n).fill(1 / n);
  const w = p.map((x) => Math.floor(x * LARGURA));
  w[w.length - 1] += LARGURA - w.reduce((a, b) => a + b, 0);
  return w;
}
function tabela(linhas) {
  const parse = (l) => l.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
  const cab = parse(linhas[0]);
  const corpo = linhas.slice(2).map(parse);
  const w = larguras(cab.length, cab);
  const borda = { style: BorderStyle.SINGLE, size: 4, color: BORDA };
  return new Table({
    width: { size: LARGURA, type: WidthType.DXA },
    columnWidths: w,
    layout: TableLayoutType.FIXED,
    borders: { top: borda, bottom: borda, left: borda, right: borda, insideHorizontal: borda, insideVertical: borda },
    rows: [
      new TableRow({ tableHeader: true, cantSplit: true, children: cab.map((c, i) => celula(c, w[i], true)) }),
      ...corpo.map((r, k) => new TableRow({
        cantSplit: true,
        children: r.map((c, i) => celula(c, w[i], false, k % 2 === 1)),
      })),
    ],
  });
}

// ---------- conversão do markdown
const linhas = MD.split("\n");
const filhos = [];
let i = 0;
let refAtual = null, ultimoNum = null; // lista numerada em andamento
const espaco = () => new Paragraph({ spacing: { before: 0, after: 60 }, children: [] });

// a primeira linha (# título) vai para a capa
if (linhas[0].startsWith("# ")) i = 1;

while (i < linhas.length) {
  const l = linhas[i];
  const t = l.trim();
  if (t === "") { i++; continue; }

  if (t === "---") { // separador
    filhos.push(new Paragraph({
      spacing: { before: 120, after: 120 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: OURO, space: 1 } }, children: [],
    }));
    i++; continue;
  }
  if (t.startsWith("## ")) {
    refAtual = null;
    filhos.push(new Paragraph({ heading: HeadingLevel.HEADING_1, 
      children: [R({ text: t.slice(3) })] }));
    i++; continue;
  }
  if (t.startsWith("|")) {
    const bloco = [];
    while (i < linhas.length && linhas[i].trim().startsWith("|")) bloco.push(linhas[i++]);
    filhos.push(tabela(bloco));
    filhos.push(espaco());
    continue;
  }
  if (t.startsWith("> ")) {
    filhos.push(new Paragraph({
      spacing: { before: 120, after: 160, line: 300 },
      indent: { left: 300, right: 300 },
      shading: { type: ShadingType.CLEAR, color: "auto", fill: ZEBRA },
      border: { left: { style: BorderStyle.SINGLE, size: 24, color: OURO_FAIXA, space: 8 } },
      children: runs(t.slice(2), { italics: true, color: PRETO }),
    }));
    i++; continue;
  }
  let m;
  if ((m = l.match(/^(\s*)- (.*)$/))) {
    const nivel = m[1].length >= 2 ? 1 : 0;
    filhos.push(new Paragraph({ numbering: { reference: "bolinha", level: nivel },
      spacing: { before: 0, after: 70, line: 276 }, children: runs(m[2]) }));
    if (nivel === 0) refAtual = null;
    i++; continue;
  }
  if ((m = l.match(/^(\s*)(\d+)\. (.*)$/))) {
    const nivel = m[1].length >= 2 ? 1 : 0;
    const n = parseInt(m[2], 10);
    if (!refAtual || n !== ultimoNum + 1 || refAtual.nivel !== nivel) refAtual = { ref: novaNumeracao(n, nivel), nivel };
    ultimoNum = n;
    filhos.push(new Paragraph({ numbering: { reference: refAtual.ref, level: 0 },
      spacing: { before: 0, after: 70, line: 276 }, children: runs(m[3]) }));
    i++; continue;
  }
  // parágrafo comum (cada linha do .md vira um parágrafo; nenhuma junção)
  // listas numeradas continuam através de parágrafos apenas se o número seguir (ex.: seção 15)
  filhos.push(new Paragraph({ spacing: { before: 60, after: 120, line: 288 }, children: runs(t) }));
  i++;
}

// ---------- capa
const titulo = linhas[0].replace(/^# /, "");
const [tit1, tit2] = titulo.split(" · ");
const capa = [
  new Paragraph({ spacing: { before: 0, after: 0 }, children: [logo(250)] }),
  new Paragraph({ spacing: { before: 120, after: 0 }, children: [R({ text: "ÁREA PARTNERS", size: 18, color: CINZA, characterSpacing: 60 })] }),
  new Paragraph({ spacing: { before: 3200, after: 0 }, children: [] }),
  new Paragraph({ spacing: { before: 0, after: 120 }, border: { top: { style: BorderStyle.SINGLE, size: 36, color: OURO_FAIXA, space: 18 } },
    children: [R({ text: tit1 + " ·", bold: true, size: 64, color: PRETO })] }),
  new Paragraph({ spacing: { before: 0, after: 480 }, children: [R({ text: tit2, bold: true, size: 64, color: PRETO })] }),
  new Paragraph({ spacing: { before: 0, after: 120 }, children: [R({ text: process.env.DOC_VERSAO || "Versão 1.0 · 02/10/2026", size: 28, color: CINZA })] }),
  new Paragraph({ spacing: { before: 0, after: 0 }, children: [R({ text: "Uso interno · Confidencial", bold: true, size: 28, color: OURO })] }),
  new Paragraph({ children: [new PageBreak()] }),
];

// ---------- índice (lista fixa das 16 seções, tirada dos títulos do .md)
const secoes = linhas.filter((x) => /^## \d+\. /.test(x)).map((x) => x.slice(3));
const indice = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [R({ text: "Índice" })] }),
  ...secoes.map((s) => {
    const [, n, nome] = s.match(/^(\d+)\. (.*)$/);
    return new Paragraph({
      spacing: { before: 0, after: 110 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: BORDA, space: 4 } },
      children: [R({ text: n.padStart(2, "0") + "   ", bold: true, color: OURO }), R({ text: nome })],
    });
  }),
  new Paragraph({ children: [new PageBreak()] }),
];

const doc = new Document({
  creator: "Área Partners · Save Company",
  // IBM Plex Sans vai embutida no arquivo: abre no padrão mesmo em máquina sem a fonte instalada
  fonts: [{ name: FONTE, data: fs.readFileSync(path.join(PADRAO, "fontes/IBMPlexSans-Regular.ttf")) }],
  embedFonts: true,
  title: titulo,
  styles: {
    default: { document: { run: { font: FONTE, size: 21, color: PRETO } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 30, bold: true, color: PRETO, font: FONTE },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0, keepNext: true,
          border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: OURO_FAIXA, space: 4 } } } },
    ],
  },
  numbering: { config: numeracoes },
  sections: [{
    properties: {
      page: { size: { width: 11906, height: 16838 }, margin: { top: 1300, bottom: 1200, left: 1134, right: 1134, header: 560, footer: 560 } },
      titlePage: true,
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: OURO, space: 4 } },
        tabStops: [{ type: "right", position: LARGURA }],
        children: [
          logo(78),
          R({ text: "   " + (process.env.DOC_CABECALHO || "Crédito Internacional · Manual Operacional Interno"), size: 16, color: CINZA }),
          R({ text: "\tUso interno · Confidencial", size: 16, color: CINZA }),
        ] })] }),
      first: new Header({ children: [new Paragraph({ children: [] })] }),
    },
    footers: {
      default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
        children: [
          R({ children: ["Página ", PageNumber.CURRENT, " de ", PageNumber.TOTAL_PAGES], size: 16, color: CINZA }),
        ] })] }),
      first: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
        children: [R({ children: ["Página ", PageNumber.CURRENT, " de ", PageNumber.TOTAL_PAGES], size: 16, color: CINZA })] })] }),
    },
    children: [...capa.slice(0, -1), ...indice.slice(0, -1), new Paragraph({ pageBreakBefore: true, spacing: { before: 0, after: 0 }, children: [] }), ...filhos],
  }],
});

Packer.toBuffer(doc).then((b) => { fs.writeFileSync(SAIDA, b); console.log("ok", SAIDA, "secoes:", secoes.length); });
