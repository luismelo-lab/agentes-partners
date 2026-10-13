#!/usr/bin/env node
// Apresentação Save (16:9) a partir do mesmo JSON de deck_html.py → PowerPoint editável (pptxgenjs), no Design System Save v0.5.
// Uso: node deck_pptx.js conteudo.json saida.pptx      (NODE_PATH precisa enxergar o pptxgenjs)
// Só gera arquivos locais. Não envia nada.
const fs = require("fs");
const path = require("path");
const PADRAO = path.join(process.env.HOME, "agentes-partners/departamentos/marketing-marca/padrao");
const S = require(path.join(PADRAO, "pptx_save.js"));
const M = JSON.parse(fs.readFileSync(path.join(PADRAO, "marca.json"), "utf8"));
const { C, E, F, FM, W, H } = S;
const MX = 0.75, CW = W - 2 * MX;              // margem e largura útil (≈ 72px no HTML)
const CONTORNO = path.join(PADRAO, M.logos.simbolo_contorno_ouro);
const doc = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const SAIDA = process.argv[3];

// **negrito** → runs do pptxgenjs
function runs(txt, o = {}) {
  const out = []; const re = /\*\*(.+?)\*\*/g; let i = 0, m; const s = String(txt || "");
  while ((m = re.exec(s))) { if (m.index > i) out.push({ text: s.slice(i, m.index), options: { ...o } }); out.push({ text: m[1], options: { ...o, bold: true, ...(o.corNegrito ? { color: o.corNegrito } : {}) } }); i = m.index + m[0].length; }
  if (i < s.length) out.push({ text: s.slice(i), options: { ...o } });
  return out.length ? out : [{ text: "", options: o }];
}
const tx = (s, txt, o) => s.addText(runs(txt, { fontFace: F, ...o.run }), { margin: 0, isTextBox: true, valign: "top", fit: "shrink", ...o.box });

const pres = S.novaApresentacao(doc.titulo_doc);
const total = doc.slides.length;

function base(escuro) {
  const s = pres.addSlide();
  s.background = { color: escuro ? E.fundo : "FFFFFF" };
  return s;
}
function marcaDagua(s) { s.addImage({ path: CONTORNO, x: W - 4.9, y: H - 4.6, w: 6.45, h: 6.45 * M.logos.proporcao_simbolo, transparency: 78 }); }
// co-branding: doc.parceiro = { logo_claro, logo_escuro, proporcao } (caminhos relativos ao JSON; PNG)
const PARC = doc.parceiro ? { claro: path.resolve(path.dirname(process.argv[2]), doc.parceiro.logo_claro), escuro: path.resolve(path.dirname(process.argv[2]), doc.parceiro.logo_escuro), r: doc.parceiro.proporcao || 0.162 } : null;
function logo(s, escuro) {
  s.addImage({ path: escuro ? S.LOGO_ESCURO : S.LOGO_CLARO, x: W - MX - 1.45, y: 0.52, w: 1.45, h: 1.45 * M.logos.proporcao_logo });
  if (PARC) {
    const pw = 1.5, ph = pw * PARC.r, px = W - MX - 1.45 - 0.35 - pw;
    s.addImage({ path: escuro ? PARC.escuro : PARC.claro, x: px, y: 0.52 + (1.45 * M.logos.proporcao_logo - ph) / 2, w: pw, h: ph });
    s.addShape("line", { x: W - MX - 1.45 - 0.17, y: 0.48, w: 0, h: 0.34, line: { color: escuro ? E.borda : C.borda_3, width: 0.75 } });
  }
}
function rotulo(s, txt, escuro, y = 0.6) {
  if (!txt) return;
  s.addShape("rect", { x: MX, y: y + 0.05, w: 0.085, h: 0.085, fill: { color: escuro ? E.ouro : C.ouro }, line: { type: "none" } });
  s.addText(String(txt).toUpperCase(), { x: MX + 0.17, y, w: 8, h: 0.2, fontFace: FM, fontSize: 9, color: escuro ? E.ouro : C.ouro_texto, charSpacing: 2, margin: 0, isTextBox: true });
}
function cabecalho(s, sl, escuro) {
  logo(s, escuro); rotulo(s, sl.rotulo, escuro);
  let y = 0.92;
  if (sl.titulo) { tx(s, sl.titulo, { run: { fontSize: 29, color: escuro ? E.texto : C.texto }, box: { x: MX, y, w: 10.4, h: 1.05 } }); y += 1.1; }
  if (sl.subtitulo) { tx(s, sl.subtitulo, { run: { fontSize: 14, color: escuro ? E.texto_2 : C.texto_2 }, box: { x: MX, y, w: 9.4, h: 0.55 } }); y += 0.6; }
  return y + 0.15;
}
function rodape(s, n, escuro) {
  s.addShape("line", { x: MX, y: H - 0.5, w: CW, h: 0, line: { color: escuro ? E.borda : C.borda, width: 0.75 } });
  s.addText(doc.rodape || "", { x: MX, y: H - 0.42, w: CW - 1, h: 0.25, fontFace: F, fontSize: 7.5, color: escuro ? E.texto_3 : C.texto_3, margin: 0, isTextBox: true });
  s.addText(`${String(n).padStart(2, "0")} / ${String(total).padStart(2, "0")}`, { x: W - MX - 1, y: H - 0.42, w: 1, h: 0.25, fontFace: FM, fontSize: 8.5, color: escuro ? E.ouro : C.ouro_texto, align: "right", margin: 0, isTextBox: true });
}
function notaFonte(s, sl, y, escuro) {
  if (sl.nota) { tx(s, sl.nota, { run: { fontSize: 10, color: escuro ? E.texto_3 : C.texto_3 }, box: { x: MX, y, w: CW, h: 0.35 } }); y += 0.35; }
  if (sl.fonte) s.addText("Fonte: " + sl.fonte, { x: MX, y, w: CW, h: 0.25, fontFace: FM, fontSize: 8.5, color: C.texto_3, margin: 0, isTextBox: true });
}
const LIM = H - 0.75; // limite inferior do conteúdo

const T = {
  capa(sl) {
    const s = base(true); marcaDagua(s);
    s.addImage({ path: S.LOGO_ESCURO, x: MX, y: 0.6, w: 2.1, h: 2.1 * M.logos.proporcao_logo });
    if (PARC) {
      s.addShape("line", { x: MX + 2.1 + 0.25, y: 0.55, w: 0, h: 0.48, line: { color: E.borda, width: 0.75 } });
      s.addImage({ path: PARC.escuro, x: MX + 2.1 + 0.5, y: 0.6 + (2.1 * M.logos.proporcao_logo - 2.2 * PARC.r) / 2, w: 2.2, h: 2.2 * PARC.r });
    }
    rotulo(s, sl.rotulo, true, 2.75);
    tx(s, sl.titulo, { run: { fontSize: 44, color: E.texto }, box: { x: MX, y: 3.05, w: 9.6, h: 1.75 } });
    tx(s, sl.subtitulo, { run: { fontSize: 15, color: E.texto_2 }, box: { x: MX, y: 4.9, w: 8.2, h: 0.75 } });
    s.addShape("rect", { x: MX, y: 5.8, w: 1.0, h: 0.045, fill: { color: E.ouro }, line: { type: "none" } });
    s.addShape("line", { x: MX, y: H - 0.72, w: CW, h: 0, line: { color: E.borda, width: 0.75 } });
    s.addText(String(sl.linha || "").toUpperCase(), { x: MX, y: H - 0.55, w: CW, h: 0.25, fontFace: FM, fontSize: 9, color: E.texto_2, charSpacing: 1.5, margin: 0, isTextBox: true });
  },
  secao(sl) {
    const s = base(true); marcaDagua(s); logo(s, true);
    s.addText(sl.numero || "", { x: MX, y: 2.2, w: 4, h: 1.6, fontFace: F, fontSize: 110, color: E.ouro, margin: 0, isTextBox: true });
    tx(s, sl.titulo, { run: { fontSize: 34, color: E.texto }, box: { x: MX, y: 4.0, w: 10, h: 1.2 } });
    tx(s, sl.texto, { run: { fontSize: 14, color: E.texto_2 }, box: { x: MX, y: 5.3, w: 9, h: 0.7 } });
  },
  frase(sl) {
    const s = base(true); marcaDagua(s); logo(s, true); rotulo(s, sl.rotulo, true);
    tx(s, sl.texto, { run: { fontSize: 34, color: E.texto, corNegrito: E.ouro }, box: { x: MX, y: 2.7, w: 10.5, h: 2.3 } });
    tx(s, sl.apoio, { run: { fontSize: 13, color: E.texto_2 }, box: { x: MX, y: 5.2, w: 8.6, h: 0.8 } });
  },
  afirmacao(sl, n) {
    const s = base(false); let y = cabecalho(s, sl, false) + 0.2;
    const ps = (sl.paragrafos || []).map((p) => runs(p, { fontFace: F, fontSize: 16, color: C.texto_2, breakLine: true, paraSpaceAfter: 8 }));
    s.addText(ps.flatMap((r, i) => (i < ps.length - 1 ? [...r, { text: "", options: { breakLine: true } }] : r)), { x: MX, y, w: 7.4, h: LIM - y - 0.5, margin: 0, valign: "top", fit: "shrink", isTextBox: true });
    const d = sl.destaque;
    if (d) {
      const dx = MX + 8.0;
      s.addShape("rect", { x: dx, y, w: 0.05, h: 2.3, fill: { color: C.ouro }, line: { type: "none" } });
      s.addText(d.valor, { x: dx + 0.3, y, w: 3.8, h: 1.0, fontFace: F, fontSize: String(d.valor).length <= 6 ? 62 : String(d.valor).length <= 9 ? 46 : 36, color: C.texto, margin: 0, isTextBox: true, fit: "shrink" });
      tx(s, d.legenda, { run: { fontSize: 13, color: C.texto_2 }, box: { x: dx + 0.3, y: y + 1.1, w: 3.8, h: 0.8 } });
      if (d.fonte) s.addText("Fonte: " + d.fonte, { x: dx + 0.3, y: y + 1.95, w: 3.8, h: 0.3, fontFace: FM, fontSize: 8.5, color: C.texto_3, margin: 0, isTextBox: true });
    }
    notaFonte(s, sl, LIM - 0.55, false); rodape(s, n, false);
  },
  numeros(sl, n) {
    const s = base(false); let y = cabecalho(s, sl, false) + 0.6;
    const k = sl.itens.length, w = CW / k;
    s.addShape("line", { x: MX, y, w: CW, h: 0, line: { color: C.borda_3, width: 0.75 } });
    sl.itens.forEach((it, i) => {
      const x = MX + i * w;
      if (i) s.addShape("line", { x: x - 0.15, y: y + 0.25, w: 0, h: 2.2, line: { color: C.borda, width: 0.75 } });
      s.addText([{ text: it.valor, options: { fontSize: k >= 4 ? 44 : 58, color: C.texto } }, ...(it.unidade ? [{ text: " " + it.unidade, options: { fontSize: 22, color: C.texto_2 } }] : [])],
        { x, y: y + 0.3, w: w - 0.3, h: 1.0, fontFace: F, margin: 0, isTextBox: true, fit: "shrink" });
      tx(s, it.legenda, { run: { fontSize: 14, color: C.texto_2 }, box: { x, y: y + 1.4, w: w - 0.4, h: 0.85 } });
      if (it.fonte) s.addText(it.fonte, { x, y: y + 2.3, w: w - 0.4, h: 0.3, fontFace: FM, fontSize: 8, color: C.texto_3, margin: 0, isTextBox: true });
    });
    notaFonte(s, sl, LIM - 0.55, false); rodape(s, n, false);
  },
  barras(sl, n) {
    const s = base(false); let y = cabecalho(s, sl, false) + 0.3;
    const mx = Math.max(...sl.itens.map((i) => i.valor)), hl = Math.min(0.62, (LIM - y - 0.8) / sl.itens.length);
    const bx = MX + 3.9, bw = CW - 3.9 - 1.4;
    sl.itens.forEach((it, i) => {
      const yy = y + i * hl, d = !!it.destaque;
      s.addText(it.rotulo, { x: MX, y: yy, w: 3.7, h: hl - 0.1, fontFace: F, fontSize: 14, bold: d, color: d ? C.texto : C.texto_2, valign: "middle", margin: 0, isTextBox: true });
      s.addShape("rect", { x: bx, y: yy + hl / 2 - 0.15, w: bw, h: 0.3, fill: { color: C.fundo_2 }, line: { type: "none" } });
      s.addShape("rect", { x: bx, y: yy + hl / 2 - 0.15, w: Math.max(0.05, bw * it.valor / mx), h: 0.3, fill: { color: d ? C.ouro : C.borda_3 }, line: { type: "none" } });
      s.addText(String(it.texto ?? it.valor), { x: W - MX - 1.25, y: yy, w: 1.25, h: hl - 0.1, fontFace: FM, fontSize: 14, color: d ? C.texto : C.texto_2, align: "right", valign: "middle", margin: 0, isTextBox: true });
      s.addShape("line", { x: MX, y: yy + hl - 0.04, w: CW, h: 0, line: { color: C.borda, width: 0.5 } });
    });
    notaFonte(s, sl, Math.min(LIM - 0.55, y + sl.itens.length * hl + 0.15), false); rodape(s, n, false);
  },
  comparativo(sl, n) {
    const s = base(false); const y = cabecalho(s, sl, false) + 0.2;
    const head = (t, ouro) => ({ text: String(t).toUpperCase(), options: { fontFace: FM, fontSize: 9, color: ouro ? C.ouro_texto : C.texto_2, charSpacing: 1.5, border: [{ type: "none" }, { type: "none" }, { pt: 0.75, color: C.borda_3 }, { type: "none" }] } });
    const cel = (t, o = {}) => ({ text: runs(t, { fontFace: F, fontSize: 13, color: C.texto_2, ...o }), options: { fill: o.fill ? { color: o.fill } : undefined, border: [{ type: "none" }, { type: "none" }, { pt: 0.5, color: C.borda }, { type: "none" }], valign: "top" } });
    const rows = [[head(""), head(sl.colunas[0]), head(sl.colunas[1], true)],
      ...sl.linhas.map((l) => [cel(l.criterio, { bold: true, color: C.texto }), cel(l.a), cel(l.b, { color: C.texto, fill: C.ouro_suave })])];
    s.addTable(rows, { x: MX, y, w: CW, colW: [CW * 0.24, CW * 0.38, CW * 0.38], margin: [0.08, 0.15, 0.08, 0.1], autoPage: false });
    notaFonte(s, sl, LIM - 0.55, false); rodape(s, n, false);
  },
  fluxo(sl, n) {
    const esc = !!sl.escuro, K = esc ? E : C; const s = base(esc); const y = cabecalho(s, sl, esc) + 0.5;
    const k = sl.etapas.length, g = 0.18, w = (CW - g * (k - 1)) / k;
    sl.etapas.forEach((e, i) => {
      const x = MX + i * (w + g);
      s.addShape("rect", { x, y, w, h: 0.035, fill: { color: e.destaque ? K.ouro : K.texto }, line: { type: "none" } });
      s.addText(String(i + 1).padStart(2, "0"), { x, y: y + 0.18, w, h: 0.22, fontFace: FM, fontSize: 10, color: esc ? E.ouro : C.ouro_texto, margin: 0, isTextBox: true });
      tx(s, e.titulo, { run: { fontSize: 16, bold: true, color: K.texto }, box: { x, y: y + 0.5, w, h: 0.62 } });
      tx(s, e.texto, { run: { fontSize: 12, color: K.texto_2 }, box: { x, y: y + 1.15, w, h: 1.6 } });
      if (e.quem) s.addText(String(e.quem).toUpperCase(), { x, y: y + 2.8, w, h: 0.3, fontFace: FM, fontSize: 8, color: K.texto_3, charSpacing: 1, margin: 0, isTextBox: true });
    });
    notaFonte(s, sl, LIM - 0.55, esc); rodape(s, n, esc);
  },
  pilares(sl, n) {
    const esc = !!sl.escuro, K = esc ? E : C; const s = base(esc); const y = cabecalho(s, sl, esc) + 0.3;
    const k = sl.itens.length, g = 0.22, w = (CW - g * (k - 1)) / k, h = Math.min(3.4, LIM - y - 0.5);
    sl.itens.forEach((p, i) => {
      const x = MX + i * (w + g);
      s.addShape("roundRect", { x, y, w, h, fill: { color: esc ? E.cartao : C.fundo }, line: { type: "none" }, rectRadius: 0.12 });
      s.addText(String(i + 1).padStart(2, "0"), { x: x + 0.3, y: y + 0.3, w: 1, h: 0.22, fontFace: FM, fontSize: 10, color: esc ? E.ouro : C.ouro_texto, margin: 0, isTextBox: true });
      tx(s, p.titulo, { run: { fontSize: 18, bold: true, color: K.texto }, box: { x: x + 0.3, y: y + 0.7, w: w - 0.6, h: 0.75 } });
      tx(s, p.texto, { run: { fontSize: 13, color: K.texto_2 }, box: { x: x + 0.3, y: y + 1.5, w: w - 0.6, h: h - 1.75 } });
    });
    notaFonte(s, sl, LIM - 0.4, esc); rodape(s, n, esc);
  },
  duas_colunas(sl, n) {
    const s = base(false); const y = cabecalho(s, sl, false) + 0.3; const w = (CW - 0.3) / 2, h = Math.min(3.7, LIM - y - 0.4);
    [[sl.esquerda, false], [sl.direita, true]].forEach(([c, o], i) => {
      const x = MX + i * (w + 0.3), K = o ? E : C;
      s.addShape("roundRect", { x, y, w, h, fill: { color: o ? E.fundo : C.fundo }, line: { type: "none" }, rectRadius: 0.12 });
      s.addText(String(c.titulo).toUpperCase(), { x: x + 0.35, y: y + 0.32, w: w - 0.7, h: 0.25, fontFace: FM, fontSize: 9, color: o ? E.ouro : C.texto_2, charSpacing: 1.5, margin: 0, isTextBox: true });
      const its = c.itens.map((t, j) => runs(t, { fontFace: F, fontSize: 15, color: K.texto, bullet: { code: "2013" }, paraSpaceAfter: 10, breakLine: j < c.itens.length - 1 }));
      s.addText(its.flat(), { x: x + 0.35, y: y + 0.75, w: w - 0.7, h: h - 1.0, margin: 0, valign: "top", fit: "shrink", isTextBox: true });
    });
    notaFonte(s, sl, LIM - 0.4, false); rodape(s, n, false);
  },
  diagrama(sl, n) {
    const s = base(false); const y = cabecalho(s, sl, false) + 0.55;
    const k = sl.nos.length, sw = 1.25, w = (CW - sw * (k - 1)) / k, h = 2.4;
    sl.nos.forEach((no, i) => {
      const x = MX + i * (w + sw), o = !!no.destaque;
      s.addShape("roundRect", { x, y, w, h, fill: { color: o ? E.fundo : "FFFFFF" }, line: { color: o ? E.fundo : C.borda_3, width: 0.75 }, rectRadius: 0.12 });
      tx(s, no.titulo, { run: { fontSize: 16, bold: true, color: o ? E.texto : C.texto }, box: { x: x + 0.22, y: y + 0.25, w: w - 0.44, h: 0.62 } });
      tx(s, no.texto, { run: { fontSize: 11.5, color: o ? E.texto_2 : C.texto_2 }, box: { x: x + 0.22, y: y + 0.9, w: w - 0.44, h: h - 1.1 } });
      if (i < k - 1) {
        const sx = x + w + 0.08, st = (sl.setas || [])[i] || {};
        s.addShape("line", { x: sx, y: y + h / 2, w: sw - 0.16, h: 0, line: { color: C.ouro, width: 1.5, endArrowType: "triangle" } });
        if (st.cima) s.addText(String(st.cima).toUpperCase(), { x: sx - 0.05, y: y + h / 2 - 0.5, w: sw - 0.06, h: 0.42, fontFace: FM, fontSize: 7.5, color: C.ouro_texto, align: "center", valign: "bottom", margin: 0, isTextBox: true });
        if (st.baixo) s.addText(String(st.baixo).toUpperCase(), { x: sx - 0.05, y: y + h / 2 + 0.08, w: sw - 0.06, h: 0.42, fontFace: FM, fontSize: 7.5, color: C.ouro_texto, align: "center", valign: "top", margin: 0, isTextBox: true });
      }
    });
    notaFonte(s, sl, Math.min(LIM - 0.55, y + h + 0.3), false); rodape(s, n, false);
  },
  pares(sl, n) {
    const s = base(false); const y = cabecalho(s, sl, false) + 0.2;
    const [a, b] = sl.colunas || ["", ""];
    const head = (t, o) => ({ text: String(t).toUpperCase(), options: { fontFace: FM, fontSize: 9, color: o ? C.ouro_texto : C.texto_2, charSpacing: 1.5, border: [{ type: "none" }, { type: "none" }, { pt: 0.75, color: C.borda_3 }, { type: "none" }] } });
    const bd = [{ type: "none" }, { type: "none" }, { pt: 0.5, color: C.borda }, { type: "none" }];
    const rows = [[head(a), head(b, true)], ...sl.itens.map((x) => [
      { text: runs(x.pergunta, { fontFace: F, fontSize: 13.5, bold: true, color: C.texto }), options: { border: bd, valign: "top" } },
      { text: runs(x.resposta, { fontFace: F, fontSize: 13.5, color: C.texto }), options: { border: bd, valign: "top", fill: { color: C.ouro_suave } } }])];
    s.addTable(rows, { x: MX, y, w: CW, colW: [CW * 0.4, CW * 0.6], margin: [0.1, 0.18, 0.1, 0.12], autoPage: false });
    notaFonte(s, sl, LIM - 0.4, false); rodape(s, n, false);
  },

  cascata(sl, n) {
    const s = base(false); const y = cabecalho(s, sl, false) + 0.3;
    const its = sl.itens; let run = 0; const bs = [];
    its.forEach((it) => { const v = +it.valor, tp = it.tipo || "delta";
      if (tp === "base" || tp === "total") { bs.push([0, v, tp, it]); run = v; }
      else { const a = Math.min(run, run + v), b = Math.max(run, run + v); bs.push([a, b, v >= 0 ? "pos" : "neg", it]); run += v; } });
    const mx = Math.max(...bs.map((b) => b[1])) * 1.12 || 1, mn = Math.min(0, ...bs.map((b) => b[0]));
    const H0 = LIM - y - 1.0, k = its.length, g = 0.18, w = (CW - g * (k - 1)) / k, yb = y + H0;
    const Y = (v) => yb - (v - mn) / (mx - mn) * H0;
    const cor = { base: C.texto, total: C.texto, pos: C.ouro, neg: C.borda_3 };
    bs.forEach(([a, b, c, it], i) => {
      const x = MX + i * (w + g);
      s.addShape("rect", { x: x + w * 0.08, y: Y(b), w: w * 0.84, h: Math.max(Y(a) - Y(b), 0.02), fill: { color: cor[c] }, line: { type: "none" } });
      const v = +it.valor, lab = it.texto || ((it.tipo || "delta") === "delta" && v > 0 ? "+" : v < 0 ? "−" : "") + String(Math.abs(v)).replace(".", ",");
      s.addText(lab, { x, y: Y(b) - 0.32, w, h: 0.28, fontFace: FM, fontSize: 11, color: C.texto, align: "center", margin: 0, isTextBox: true });
      s.addText(it.rotulo, { x, y: yb + 0.08, w, h: 0.45, fontFace: F, fontSize: 10.5, bold: c === "base" || c === "total", color: C.texto_2, align: "center", valign: "top", margin: 0, isTextBox: true });
    });
    s.addShape("line", { x: MX, y: yb, w: CW, h: 0, line: { color: C.borda_3, width: 0.75 } });
    if (sl.unidade) s.addText("Valores em " + sl.unidade, { x: MX, y: y - 0.25, w: 4, h: 0.22, fontFace: FM, fontSize: 8.5, color: C.texto_3, margin: 0, isTextBox: true });
    notaFonte(s, sl, LIM - 0.4, false); rodape(s, n, false);
  },
  matriz(sl, n) {
    const s = base(false); const y = cabecalho(s, sl, false) + 0.15;
    const px = MX + 0.45, pw = CW - 0.45, ph = LIM - y - 0.85, ex = sl.eixo_x || {}, ey = sl.eixo_y || {}, qs = sl.quadrantes || [];
    const hl = sl.quadrante_destaque ?? 1;
    [[0, 0], [1, 0], [0, 1], [1, 1]].forEach(([cx, cy], i) => {
      s.addShape("rect", { x: px + cx * pw / 2, y: y + cy * ph / 2, w: pw / 2, h: ph / 2, fill: { color: i === hl ? C.ouro_suave : "FFFFFF" }, line: { color: C.borda_2, width: 0.5, dashType: "dash" } });
      if (qs[i]) s.addText(String(qs[i]).toUpperCase(), { x: px + cx * pw / 2 + 0.12, y: y + cy * ph / 2 + (cy ? ph / 2 - 0.35 : 0.1), w: pw / 2 - 0.24, h: 0.25, fontFace: FM, fontSize: 8, color: i === hl ? C.ouro_texto : C.texto_3, align: cx ? "right" : "left", margin: 0, isTextBox: true });
    });
    s.addShape("line", { x: px, y, w: 0, h: ph, line: { color: C.texto, width: 1.5 } });
    s.addShape("line", { x: px, y: y + ph, w: pw, h: 0, line: { color: C.texto, width: 1.5 } });
    s.addText(`${(ex.baixo || "").toUpperCase()}`, { x: px, y: y + ph + 0.06, w: 2, h: 0.22, fontFace: FM, fontSize: 8, color: C.texto_2, margin: 0, isTextBox: true });
    s.addText(`${(ex.rotulo || "").toUpperCase()}`, { x: px + pw / 2 - 1.5, y: y + ph + 0.06, w: 3, h: 0.22, fontFace: FM, fontSize: 8, color: C.texto_2, align: "center", margin: 0, isTextBox: true });
    s.addText(`${(ex.alto || "").toUpperCase()}`, { x: px + pw - 2, y: y + ph + 0.06, w: 2, h: 0.22, fontFace: FM, fontSize: 8, color: C.texto_2, align: "right", margin: 0, isTextBox: true });
    s.addText(`${(ey.rotulo || "").toUpperCase()} ↑`, { x: MX - 0.05, y: y + ph / 2 - 0.15, w: 0.45, h: 0.3, fontFace: FM, fontSize: 7.5, color: C.texto_2, margin: 0, isTextBox: true, rotate: 270 });
    sl.itens.forEach((it) => {
      const cx = px + (+it.x) * pw, cy = y + (1 - (+it.y)) * ph, d = !!it.destaque, esq = +it.x > 0.72;
      s.addShape("ellipse", { x: cx - 0.08, y: cy - 0.08, w: 0.16, h: 0.16, fill: { color: d ? C.ouro : C.texto }, line: { color: C.texto, width: d ? 1.5 : 0 } });
      s.addText(it.nome, { x: esq ? cx - 2.62 : cx + 0.14, y: cy - 0.14, w: 2.5, h: 0.28, fontFace: F, fontSize: 10.5, bold: true, color: C.texto, align: esq ? "right" : "left", margin: 0, isTextBox: true });
    });
    notaFonte(s, sl, LIM - 0.3, false); rodape(s, n, false);
  },
  calor(sl, n) {
    const s = base(false); const y = cabecalho(s, sl, false) + 0.2;
    const vals = sl.linhas.flatMap((l) => l.valores.filter((v) => typeof v === "number")); const mx = Math.max(...vals, 1);
    const mix = (a) => { const o = [243, 205, 96], wv = [255, 255, 255]; return o.map((c, i) => Math.round(wv[i] + (c - wv[i]) * a).toString(16).padStart(2, "0")).join("").toUpperCase(); };
    const bd = [{ pt: 2, color: "FFFFFF" }, { pt: 2, color: "FFFFFF" }, { pt: 2, color: "FFFFFF" }, { pt: 2, color: "FFFFFF" }];
    const rows = [[{ text: "", options: { border: bd } }, ...sl.colunas.map((c) => ({ text: String(c).toUpperCase(), options: { fontFace: FM, fontSize: 8.5, color: C.texto_2, align: "center", border: bd } }))],
      ...sl.linhas.map((l) => [{ text: l.nome, options: { fontFace: F, fontSize: 12, bold: true, color: C.texto, border: bd } },
        ...l.valores.map((v, i) => { const tx = (l.textos || [])[i]; const ok = typeof v === "number" && v !== 0;
          return { text: tx != null && tx !== "" ? String(tx) : ok ? String(v).replace(".", ",") : "—", options: { fontFace: FM, fontSize: 12, color: ok ? C.texto : C.texto_3, align: "center", valign: "middle", fill: { color: ok ? mix(0.12 + 0.88 * v / mx) : C.fundo_2 }, border: bd } }; })])];
    const cw0 = 2.4; s.addTable(rows, { x: MX, y, w: CW, colW: [cw0, ...sl.colunas.map(() => (CW - cw0) / sl.colunas.length)], rowH: 0.48, autoPage: false });
    if (sl.legenda) s.addText("Intensidade: " + sl.legenda, { x: MX, y: Math.min(LIM - 0.75, y + 0.5 * (sl.linhas.length + 1) + 0.15), w: CW, h: 0.25, fontFace: F, fontSize: 9.5, color: C.texto_3, margin: 0, isTextBox: true });
    notaFonte(s, sl, LIM - 0.4, false); rodape(s, n, false);
  },
  organograma(sl, n) {
    const s = base(false); const y = cabecalho(s, sl, false) + 0.1;
    const rz = sl.raiz, gs = sl.grupos, k = gs.length, g = 0.18, w = (CW - g * (k - 1)) / k;
    s.addShape("roundRect", { x: W / 2 - 1.6, y, w: 3.2, h: 0.62, fill: { color: E.fundo }, line: { type: "none" }, rectRadius: 0.08 });
    s.addText([{ text: rz.titulo, options: { fontSize: 13, bold: true, color: E.texto, breakLine: true } }, { text: rz.texto || "", options: { fontSize: 9, color: E.texto_2 } }], { x: W / 2 - 1.6, y, w: 3.2, h: 0.62, fontFace: F, align: "center", valign: "middle", margin: 0, isTextBox: true });
    const yb = y + 0.62, yg = yb + 0.42;
    s.addShape("line", { x: W / 2, y: yb, w: 0, h: 0.2, line: { color: C.ouro, width: 1.5 } });
    s.addShape("line", { x: MX + w / 2, y: yb + 0.2, w: CW - w, h: 0, line: { color: C.ouro, width: 1.5 } });
    gs.forEach((gr, i) => {
      const x = MX + i * (w + g);
      s.addShape("line", { x: x + w / 2, y: yb + 0.2, w: 0, h: 0.22, line: { color: C.ouro, width: 1.5 } });
      s.addShape("rect", { x, y: yg, w, h: 0.05, fill: { color: C.ouro }, line: { type: "none" } });
      s.addShape("rect", { x, y: yg + 0.05, w, h: 0.62, fill: { color: C.fundo }, line: { type: "none" } });
      s.addText([{ text: gr.titulo, options: { fontSize: 11.5, bold: true, color: C.texto, breakLine: true } }, { text: gr.texto || "", options: { fontSize: 8.5, color: C.texto_2 } }], { x: x + 0.1, y: yg + 0.08, w: w - 0.2, h: 0.56, fontFace: F, valign: "top", margin: 0, isTextBox: true, fit: "shrink" });
      (gr.itens || []).forEach((it, j) => {
        const yy = yg + 0.78 + j * 0.62;
        s.addShape("roundRect", { x, y: yy, w, h: 0.54, fill: { color: "FFFFFF" }, line: { color: C.borda, width: 0.75 }, rectRadius: 0.06 });
        s.addText([{ text: it.titulo, options: { fontSize: 10, bold: true, color: C.texto, breakLine: true } }, { text: it.texto || "", options: { fontSize: 8.5, color: C.texto_2 } }], { x: x + 0.1, y: yy + 0.04, w: w - 0.2, h: 0.48, fontFace: F, valign: "top", margin: 0, isTextBox: true, fit: "shrink" });
      });
    });
    notaFonte(s, sl, LIM - 0.3, false); rodape(s, n, false);
  },
  tabela(sl, n) {
    const s = base(false); const y = cabecalho(s, sl, false) + 0.2; const dc = sl.destaque_coluna;
    const bdH = [{ type: "none" }, { type: "none" }, { pt: 0.75, color: C.borda_3 }, { type: "none" }], bd = [{ type: "none" }, { type: "none" }, { pt: 0.5, color: C.borda }, { type: "none" }];
    const rows = [sl.colunas.map((c, i) => ({ text: String(c).toUpperCase(), options: { fontFace: FM, fontSize: 8.5, color: i === dc ? C.ouro_texto : C.texto_2, charSpacing: 1, border: bdH } })),
      ...sl.linhas.map((l) => l.map((c, i) => ({ text: runs(c, { fontFace: F, fontSize: 11.5, bold: i === 0, color: i === 0 || i === dc ? C.texto : C.texto_2 }), options: { border: bd, valign: "top", fill: i === dc ? { color: C.ouro_suave } : undefined } })))];
    s.addTable(rows, { x: MX, y, w: CW, margin: [0.07, 0.12, 0.07, 0.08], autoPage: false });
    notaFonte(s, sl, LIM - 0.4, false); rodape(s, n, false);
  },

  mandala(sl, n) {
    const s = base(false); const y = cabecalho(s, sl, false) + 0.1;
    const D = Math.min(4.9, LIM - y - 0.45);
    // desenho da mandala como imagem (mesmo traço do PDF); a legenda ao lado continua editável
    const png = path.join(require("os").tmpdir(), `mandala-${process.pid}-${n}.png`);
    require("child_process").execFileSync("python3", [path.join(__dirname, "mandala_png.py"), process.argv[2], String(n - 1), png]);
    s.addImage({ path: png, x: MX, y, w: D, h: D });
    const fases = sl.fases;
    const lx = MX + D + 0.45, lw = W - MX - lx; let ly = y + 0.5;
    fases.forEach((f, i) => {
      s.addShape("line", { x: lx, y: ly, w: lw, h: 0, line: { color: C.borda, width: 0.75 } });
      s.addText(String(i + 1).padStart(2, "0"), { x: lx, y: ly + 0.14, w: 0.4, h: 0.25, fontFace: FM, fontSize: 10, color: C.ouro_texto, margin: 0, isTextBox: true });
      tx(s, f.titulo, { run: { fontSize: 13.5, bold: true, color: C.texto }, box: { x: lx + 0.45, y: ly + 0.12, w: lw - 0.45, h: 0.3 } });
      tx(s, f.texto || "", { run: { fontSize: 11, color: C.texto_2 }, box: { x: lx + 0.45, y: ly + 0.45, w: lw - 0.45, h: 0.5 } });
      ly += 1.05;
    });
    notaFonte(s, sl, LIM - 0.3, false); rodape(s, n, false);
  },

  etapas(sl, n) {
    const s = base(false); const y = cabecalho(s, sl, false) + 0.05;
    const et = sl.etapas, k = et.length, ga = 0.38, w = (CW - ga * (k - 1)) / k, h = LIM - y - 0.4;
    et.forEach((e, i) => {
      const x = MX + i * (w + ga), d = !!e.destaque, K = d ? E : C;
      s.addShape("roundRect", { x, y, w, h, fill: { color: d ? E.fundo : C.fundo }, line: { type: "none" }, rectRadius: 0.1 });
      s.addText(String(i + 1).padStart(2, "0"), { x: x + 0.18, y: y + 0.14, w: 1, h: 0.2, fontFace: FM, fontSize: 9, color: d ? E.ouro : C.ouro_texto, margin: 0, isTextBox: true });
      s.addText(e.titulo, { x: x + 0.18, y: y + 0.36, w: w - 0.36, h: 0.36, fontFace: F, fontSize: 17, bold: true, color: K.texto, margin: 0, isTextBox: true });
      tx(s, e.texto || "", { run: { fontSize: 9.5, color: K.texto_2 }, box: { x: x + 0.18, y: y + 0.74, w: w - 0.36, h: 0.36 } });
      const its = e.itens || [], ih = Math.min(0.5, (h - 1.25) / Math.max(1, its.length));
      its.forEach((it, j) => {
        const yy = y + 1.17 + j * ih;
        s.addShape("line", { x: x + 0.18, y: yy, w: w - 0.36, h: 0, line: { color: d ? E.borda : C.borda_3, width: 0.5 } });
        s.addText([{ text: String(it.produto).toUpperCase(), options: { fontFace: FM, fontSize: 7.5, color: d ? E.ouro : C.ouro_texto, breakLine: true } }, { text: it.impacto, options: { fontFace: F, fontSize: 10.5, color: K.texto } }],
          { x: x + 0.18, y: yy + 0.03, w: w - 0.36, h: ih - 0.04, valign: "top", margin: 0, isTextBox: true, fit: "shrink" });
      });
      if (i < k - 1) s.addShape("rightArrow", { x: x + w + 0.08, y: y + h / 2 - 0.13, w: ga - 0.16, h: 0.26, fill: { color: C.ouro }, line: { type: "none" } });
    });
    notaFonte(s, sl, LIM - 0.3, false); rodape(s, n, false);
  },
  caso(sl, n) {
    const s = base(false); const y = cabecalho(s, sl, false) + 0.2; const w = (CW - 0.5) / 2;
    const linhas = Math.ceil(sl.linhas.length / 2), hl = Math.min(0.95, (LIM - y - 0.5) / linhas);
    s.addShape("line", { x: MX, y, w: CW, h: 0, line: { color: C.borda_3, width: 0.75 } });
    sl.linhas.forEach((l, i) => {
      const x = MX + (i % 2) * (w + 0.5), yy = y + Math.floor(i / 2) * hl + 0.15;
      s.addText(String(l.rotulo).toUpperCase(), { x, y: yy, w, h: 0.22, fontFace: FM, fontSize: 8.5, color: C.ouro_texto, charSpacing: 1.2, margin: 0, isTextBox: true });
      tx(s, l.texto, { run: { fontSize: 13.5, color: C.texto }, box: { x, y: yy + 0.26, w, h: hl - 0.4 } });
      s.addShape("line", { x, y: yy + hl - 0.12, w, h: 0, line: { color: C.borda, width: 0.5 } });
    });
    notaFonte(s, sl, LIM - 0.4, false); rodape(s, n, false);
  },
  fechamento(sl, n) {
    const s = base(true); marcaDagua(s); const y = cabecalho(s, sl, true) + 0.5;
    const ps = sl.passos || [], k = Math.max(1, ps.length), g = 0.25, w = (CW - g * (k - 1)) / k;
    ps.forEach((p, i) => {
      const x = MX + i * (w + g);
      s.addShape("line", { x, y, w, h: 0, line: { color: E.borda, width: 0.75 } });
      s.addText(String(i + 1).padStart(2, "0"), { x, y: y + 0.18, w: 1, h: 0.22, fontFace: FM, fontSize: 10, color: E.ouro, margin: 0, isTextBox: true });
      tx(s, p, { run: { fontSize: 15, color: E.texto }, box: { x, y: y + 0.5, w, h: 1.5 } });
    });
    if (sl.contato) tx(s, sl.contato, { run: { fontSize: 12, color: E.texto_2 }, box: { x: MX, y: LIM - 0.55, w: CW, h: 0.4 } });
    rodape(s, n, true);
  },
};

doc.slides.forEach((sl, i) => {
  if (!T[sl.tipo]) throw new Error("tipo de slide desconhecido: " + sl.tipo);
  T[sl.tipo](sl, i + 1);
  if (sl.notas) pres._slides[pres._slides.length - 1].addNotes(sl.notas);
});
pres.writeFile({ fileName: SAIDA }).then((f) => console.log("ok", f, "slides:", total));
