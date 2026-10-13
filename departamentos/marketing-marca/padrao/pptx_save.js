// Save Co. · Design System Save v0.5 · base de PowerPoint (pptxgenjs). Todo deck novo começa por aqui.
// Uso:
//   const S = require(path.join(HOME, "agentes-partners/departamentos/marketing-marca/padrao/pptx_save.js"));
//   const pres = S.novaApresentacao("Título do deck");
//   const s = pres.addSlide({ masterName: "SAVE_CLARO" });   // ou "SAVE_ESCURO" (capa, divisória, painel) / "SAVE_CAPA"
//   S.titulo(s, "Rótulo", "Título do slide");
// Fonte: IBM Plex Sans (o PowerPoint não embute; instalar de "Área Partners · Agentes/Marca/Fontes IBM Plex").
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const PASTA = __dirname;
const M = JSON.parse(fs.readFileSync(path.join(PASTA, "marca.json"), "utf8"));
const h = (c) => c.replace("#", "");
const C = Object.fromEntries(Object.entries(M.claro).filter(([k]) => !k.startsWith("_")).map(([k, v]) => [k, h(v)]));
const E = Object.fromEntries(Object.entries(M.escuro).filter(([k]) => !k.startsWith("_")).map(([k, v]) => [k, h(v)]));
const F = M.fontes.sans, FM = M.fontes.mono;
const LOGO_CLARO = path.join(PASTA, M.logos.fundo_claro), LOGO_ESCURO = path.join(PASTA, M.logos.fundo_escuro);
const W = 13.333, H = 7.5, MX = 0.6;  // LAYOUT_WIDE, margem lateral
const LW = 1.6, LH = +(LW * M.logos.proporcao_logo).toFixed(3);

function novaApresentacao(titulo) {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.author = "Save Co. · Área Partners";
  pres.company = "Save Co.";
  pres.title = titulo || "Save Co.";
  pres.theme = { headFontFace: F, bodyFontFace: F };
  const rodape = (cor) => ({ text: { text: "Save Co.", options: { x: MX, y: H - 0.42, w: 4, h: 0.25, fontFace: F, fontSize: 9, color: cor, margin: 0 } } });
  pres.defineSlideMaster({
    title: "SAVE_CLARO", background: { color: "FFFFFF" },
    objects: [
      { image: { path: LOGO_CLARO, x: W - MX - LW, y: 0.38, w: LW, h: LH } },
      { line: { x: MX, y: H - 0.55, w: W - 2 * MX, h: 0, line: { color: C.borda, width: 0.75 } } },
      rodape(C.texto_2),
    ],
    slideNumber: { x: W - MX - 0.6, y: H - 0.42, w: 0.6, h: 0.25, fontFace: FM, fontSize: 9, color: C.ouro_texto, align: "right" },
  });
  pres.defineSlideMaster({
    title: "SAVE_ESCURO", background: { color: E.fundo },
    objects: [
      { image: { path: LOGO_ESCURO, x: W - MX - LW, y: 0.38, w: LW, h: LH } },
      { line: { x: MX, y: H - 0.55, w: W - 2 * MX, h: 0, line: { color: E.borda, width: 0.75 } } },
      rodape(E.texto_2),
    ],
    slideNumber: { x: W - MX - 0.6, y: H - 0.42, w: 0.6, h: 0.25, fontFace: FM, fontSize: 9, color: E.ouro, align: "right" },
  });
  pres.defineSlideMaster({
    title: "SAVE_CAPA", background: { color: E.fundo },
    objects: [
      { image: { path: LOGO_ESCURO, x: MX, y: 0.6, w: 2.4, h: +(2.4 * M.logos.proporcao_logo).toFixed(3) } },
      { rect: { x: MX, y: H - 1.25, w: 1.4, h: 0.06, fill: { color: E.ouro } } },
    ],
  });
  return pres;
}

// Rótulo (mono, ouro) + título do slide; escuro=true para os masters escuros
function titulo(s, rotulo, texto, escuro = false) {
  if (rotulo) s.addText(rotulo.toUpperCase(), { x: MX, y: 0.45, w: 9, h: 0.3, fontFace: FM, fontSize: 11, color: escuro ? E.ouro : C.ouro_texto, charSpacing: 2, margin: 0, isTextBox: true });
  s.addText(texto, { x: MX, y: 0.8, w: W - 2 * MX - 2, h: 0.9, fontFace: F, fontSize: 30, bold: true, color: escuro ? E.texto : C.texto, margin: 0, valign: "top", isTextBox: true });
}

// Cartão de KPI: rótulo, número grande, apoio
function kpi(s, x, y, w, rot, valor, apoio, escuro = false) {
  const K = escuro ? E : C;
  s.addShape("roundRect", { x, y, w, h: 1.5, fill: { color: escuro ? E.cartao : C.cartao }, line: { color: K.borda, width: 0.75 }, rectRadius: 0.1 });
  s.addText(rot.toUpperCase(), { x: x + 0.25, y: y + 0.18, w: w - 0.5, h: 0.25, fontFace: FM, fontSize: 9, color: K.texto_2, charSpacing: 1, margin: 0, isTextBox: true });
  s.addText(valor, { x: x + 0.25, y: y + 0.45, w: w - 0.5, h: 0.6, fontFace: F, fontSize: 26, bold: true, color: K.texto, margin: 0, fit: "shrink", isTextBox: true });
  if (apoio) s.addText(apoio, { x: x + 0.25, y: y + 1.08, w: w - 0.5, h: 0.3, fontFace: F, fontSize: 10, color: K.texto_2, margin: 0, isTextBox: true });
}

// Cores para gráficos nativos: ouro primeiro, depois neutros (uma única cor cromática)
const GRAFICO = { claro: [C.ouro_texto, C.texto, C.texto_3, C.borda_3], escuro: [E.ouro, E.texto, E.texto_2, E.texto_3] };

module.exports = { novaApresentacao, titulo, kpi, C, E, F, FM, W, H, MX, GRAFICO, LOGO_CLARO, LOGO_ESCURO };
