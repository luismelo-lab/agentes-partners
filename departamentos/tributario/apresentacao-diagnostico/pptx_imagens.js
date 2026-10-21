// Monta o PowerPoint a partir das imagens dos slides (como a apresentação institucional da Save Co.), com o roteiro nas notas.
// Uso: node pptx_imagens.js <lista.json {imagens[], notas[]}> <saida.pptx>
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const [lista, saida] = process.argv.slice(2);
const { imagens, notas } = JSON.parse(fs.readFileSync(lista, "utf8"));
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Save Co. · Área Partners";
pres.company = "Save Co.";
imagens.forEach((img, i) => {
  const s = pres.addSlide();
  s.background = { color: "000000" };
  s.addImage({ path: img, x: 0, y: 0, w: 13.333, h: 7.5 });
  if (notas[i]) s.addNotes(notas[i]);
});
pres.writeFile({ fileName: saida }).then(() => console.log("ok", saida));
