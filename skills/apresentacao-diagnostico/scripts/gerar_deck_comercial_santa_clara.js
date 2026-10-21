// Apresentação comercial da Save à Cooperativa Santa Clara: o ecossistema da Save como esteira (21/10/2026).
// Roteiro do Luis: dados de mercado > dificuldades do setor (fontes oficiais) > espelho na empresa > como ajudar > resultados possíveis.
// Foco: mais lucro e mais margem. Uso: NODE_PATH=<node_modules> node gerar_deck_santa_clara_ecossistema.js <saida.pptx>
const fs = require("fs");
const path = require("path");
const S = require(path.join(__dirname, "../../../departamentos/marketing-marca/padrao/pptx_save.js"));
const { C, E, F, FM, W, H, MX, GRAFICO } = S;
const OUT = process.argv[2];

const pres = S.novaApresentacao("Save Co. · Esteira completa para a Cooperativa Santa Clara");
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
s.addText("PROPOSTA À PRESIDÊNCIA · OUTUBRO DE 2026", { x: MX, y: 2.3, w: 10, h: 0.35, fontFace: FM, fontSize: 12, color: E.ouro, charSpacing: 2, margin: 0 });
s.addText("Uma esteira completa para mais lucro e mais margem na Santa Clara", { x: MX, y: 2.75, w: 11.4, h: 1.7, fontFace: F, fontSize: 38, bold: true, color: E.texto, margin: 0, valign: "top" });
s.addText("Como a Save resolve, em ordem, os problemas de caixa, tributos, crédito e crescimento, com um gestor de projeto que conduz tudo", { x: MX, y: 4.6, w: 10.8, h: 0.9, fontFace: F, fontSize: 16, color: E.texto_2, margin: 0, valign: "top" });
s.addText("PRÉ-ANÁLISE · ESTIMATIVAS PRELIMINARES SUJEITAS A VALIDAÇÃO TÉCNICA · SEM PROMESSA DE VALOR, PRAZO OU ÊXITO", { x: MX, y: 6.55, w: 11.5, h: 0.3, fontFace: FM, fontSize: 8.5, color: E.ouro, margin: 0 });

// ───────────── 2. O QUE PROPOMOS
s = nova("Em uma página", "Propomos uma esteira em que cada resultado vira margem");
cartao(s, MX, TOPO, 3.9, 4.3, "O problema", "Empresas do porte da Santa Clara resolvem um assunto de cada vez: um crédito tributário aqui, uma renegociação ali, um financiamento quando o caixa aperta. Cada decisão ignora as outras, e o resultado é retrabalho, custo e margem que escapa entre os negócios.", { fs: 14 });
cartao(s, MX + 4.1, TOPO, 3.9, 4.3, "A nossa resposta", "Uma esteira em 12 passos, em 3 movimentos. O fim de cada passo é o começo do próximo: o crédito recuperado alivia a dívida, a carteira organizada abre o capital, a empresa em dia abre o crescimento.", { fs: 14, fundo: C.ouro_suave });
cartao(s, MX + 8.2, TOPO, 3.93, 4.3, "O que muda para a cooperativa", "• Um gestor de projeto conduz tudo e conecta as nossas equipes tributária, jurídica, financeira e de crédito\n• Cada passo tem entrega clara e medida contra uma linha de base\n• Remuneração por resultado sempre que possível\n• A diretoria não coordena sete áreas: recebe um painel", { fs: 14 });

// ───────────── 3. ONDE A MARGEM ESTÁ SOB PRESSÃO
s = nova("O contexto da Santa Clara", "Seis negócios, quatro pressões sobre a margem. Dados oficiais, com fonte e data");
tabela(s, MX, TOPO, [2.6, 6.1, 3.43], ["Pressão", "O que os dados oficiais mostram", "Fonte"], [
  ["Preço do leite oscila", "Preço pago ao produtor: R$ 2,76 (1T25), R$ 2,21 (4T25), R$ 2,70 (2T26), com volume recorde no país", "IBGE, Pesquisa Trimestral do Leite"],
  ["Carne suína mais barata", "Carne de porco ao consumidor −8,3% em 12 meses; abate +4,3% no Brasil e +6,8% no RS em 2025; ração é de 65% a 72% do custo", "IBGE; Embrapa Suínos e Aves"],
  ["Capital caro", "Capital de giro de mercado a 22,89% ao ano; crédito rural de custeio a 9% no Plano Safra 2026/27", "Banco Central; Governo federal"],
  ["Tributos em transição", "Crédito presumido do leite a 90% desde abril/2026; reforma tributária a partir de 2027", "NT RFB 012/2026; LC 214/2025 e LC 224/2025"]], { fs: 12.5 });
s.addText("O mercado grande e crescente não protege a margem. A margem se constrói dentro de casa: no caixa, no imposto, no custo do capital e na conexão entre os negócios. Mostramos como a partir do slide 4.", { x: MX, y: 5.2, w: W - 2 * MX, h: 0.9, fontFace: F, fontSize: 13.5, bold: true, color: C.texto, margin: 0, valign: "top" });
fonte(s, "IBGE (SIDRA 1086, 1093 e 7060); Embrapa; Banco Central (SGS 20725, ago/2026); Governo federal (Plano Safra 2026/27); Receita Federal. Análise completa de mercado: deck de dados oficiais da Santa Clara.");

// ───────────── 4. A ESTEIRA
s = nova("A proposta", "Uma esteira de 12 passos em 3 movimentos: o fim de cada passo é o começo do próximo");
const mov = [["Destravar caixa", ["1 · Enxergar a empresa por inteiro", "2 · Recuperar o que já é seu", "3 · Receber o que lhe devem, e mais cedo", "4 · Aliviar a dívida que pesa"], "Onde está o dinheiro que já é nosso e como fazemos o caixa respirar?"],
  ["Proteger e controlar", ["5 · Deixar a empresa em dia", "6 · Pagar o imposto certo e se preparar para 2027", "7 · Dar governança ao dinheiro", "8 · Proteger o patrimônio"], "Como organizamos a casa para o problema não voltar?"],
  ["Crescer", ["9 · Capital para crescer", "10 · Financiar a sua cadeia", "11 · Vender e produzir além da fronteira", "12 · Manter a esteira rodando"], "Como financiamos e expandimos com segurança?"]];
mov.forEach((m, i) => {
  const x = MX + i * 4.1;
  s.addShape("roundRect", { x, y: TOPO, w: 3.95, h: 0.6, fill: { color: E.fundo }, line: { color: E.fundo }, rectRadius: 0.08 });
  s.addText(m[0], { x: x + 0.2, y: TOPO, w: 3.5, h: 0.6, fontFace: F, fontSize: 15, bold: true, color: E.ouro, margin: 0, valign: "middle" });
  m[1].forEach((p, j) => {
    s.addShape("roundRect", { x, y: TOPO + 0.72 + j * 0.7, w: 3.95, h: 0.6, fill: { color: C.cartao }, line: { color: C.borda, width: 0.75 }, rectRadius: 0.06 });
    s.addText(p, { x: x + 0.2, y: TOPO + 0.72 + j * 0.7, w: 3.6, h: 0.6, fontFace: F, fontSize: 11.5, color: C.texto, margin: 0, valign: "middle" });
  });
  s.addText(m[2], { x, y: TOPO + 3.55, w: 3.95, h: 0.6, fontFace: F, fontSize: 11, italic: true, color: C.texto_2, margin: 0, valign: "top" });
});
s.addText("Cada passo só avança quando o anterior entregou o que o próximo precisa. A esteira se adapta ao ponto de partida de cada negócio.", { x: MX, y: 6.1, w: W - 2 * MX, h: 0.5, fontFace: F, fontSize: 13, bold: true, color: C.texto, margin: 0, valign: "top" });

// ───────────── 5-7. PASSO A PASSO POR MOVIMENTO
function passos(rot, tit, linhas, rodape) {
  const sl = nova(rot, tit);
  tabela(sl, MX, TOPO, [2.3, 3.7, 3.0, 3.13], ["Passo", "O que fazemos na Santa Clara", "O que a cooperativa recebe", "O que isso libera no próximo passo"], linhas, { fs: 12.5 });
  fonte(sl, rodape);
}
passos("A esteira passo a passo · Destravar caixa", "Destravar caixa: ver a margem de cada negócio e liberar o que está parado", [
  ["1 · Enxergar por inteiro", "Lemos a documentação fiscal e financeira e montamos um mapa único dos seis negócios: margem por linha, planta e loja, prazo e dívida", "Mapa com prioridades e linha de base assinada pela diretoria", "Define o ponto de partida certo e deixa a medição pronta para provar o resultado de cada etapa"],
  ["2 · Recuperar o que já é seu", "Conferimos o aproveitamento do crédito presumido do leite e dos suínos, saldos credores, créditos de energia, frio e embalagem, e a separação do ato cooperativo", "Crédito apurado e acompanhado, com relatório do valor recuperado", "O crédito vira caixa e pode abater débitos (passo 5) ou parcelas caras (passo 4)"],
  ["3 · Receber mais cedo", "Organizamos prazo de redes e food service e a conta corrente do associado nas lojas agropecuárias", "Carteira organizada e previsibilidade de caixa", "A carteira em ordem é a base de qualquer crédito (passo 9) e da cadeia (passo 10)"],
  ["4 · Aliviar a dívida", "Estudamos alongar prazos e trocar dívida cara por uma que cabe no fluxo, incluindo capital de giro da safra e aquisições recentes", "Plano de dívida com parcelas compatíveis", "O fôlego permite regularizar pendências (passo 5) e investir (passos 9 a 11)"]],
  "Lei 10.925/2004; NT RFB 012/2026; Lei 5.764/1971. Estimativas preliminares sujeitas a validação técnica; sem promessa de valor ou prazo.");
passos("A esteira passo a passo · Proteger e controlar", "Proteger e controlar: manter a margem conquistada e preparar 2027", [
  ["5 · Deixar em dia", "Mapeamos débitos, certidões e autos de todas as unidades e escolhemos o caminho adequado, com prazos sob dupla checagem", "Empresa regular e certidão em dia", "A certidão é pré-requisito para crédito de longo prazo e grandes clientes (passos 9 e 10)"],
  ["6 · Imposto certo e 2027", "Simulamos a nova tributação (CBS e IBS) produto a produto, de leite e queijos a carnes e embutidos, e usamos saldos credores antes da transição", "Plano tributário com cenários e menor carga dentro da lei", "A previsibilidade alimenta o plano de crescimento e a organização do patrimônio"],
  ["7 · Governança", "Montamos um painel mensal de margem por linha, planta, loja, associado e região", "Números em que a diretoria e as instituições confiam", "O painel vira a linguagem comum com bancos e investidores (passos 9 e 10)"],
  ["8 · Patrimônio", "Organizamos estruturas, imóveis das lojas e centrais e participações", "Patrimônio protegido e base de garantia clara", "Imóveis organizados viram garantia para capital (passo 9)"]],
  "LC 214/2025; LC 224/2025. Reduz a carga quando há espaço legal; não promete percentual.");
passos("A esteira passo a passo · Crescer", "Crescer: capital certo, produtor forte e mais valor por quilo vendido", [
  ["9 · Capital para crescer", "Preparamos projetos de investimento (centro de distribuição, expansão do abate, varejo) com prazo e custo compatíveis, por instituições autorizadas", "Projeto pronto para a instituição, com dados que o passo 7 já organizou", "Capital certo financia o passo 10 e a expansão (passo 11)"],
  ["10 · Financiar a cadeia", "Estruturamos crédito ao produtor contra entrega futura de leite e ao suinocultor integrado, com a conta do associado organizada", "Produtor com margem e menos capital parado na cooperativa", "Cadeia financiada entrega mais volume e qualidade aos negócios de indústria"],
  ["11 · Além da fronteira", "Avaliamos exportação de queijos nobres, carne suína e charcutaria premium e, quando fizer sentido, produzir em outro país", "Estudo de viabilidade com tributos, logística e regras sanitárias", "Novos mercados voltam como receita e pedem de novo os passos 6 e 9"],
  ["12 · Esteira rodando", "Revisão anual, captura mensal de novas competências e encontro trimestral com a diretoria", "Painel de valor acompanhado e novas oportunidades", "Fecha o ciclo e reabre a esteira onde houver novo ganho"]],
  "Avaliado caso a caso; sem condição definida antes da análise. Operações de crédito são realizadas por instituições autorizadas; a decisão e as condições são delas.");

// ───────────── 8. CONEXÃO ENTRE NEGÓCIOS
s = nova("O diferencial no ecossistema", "A esteira também conecta os negócios entre si, e é aí que a margem se multiplica");
const lig = [
  ["Conta do associado", "A loja agropecuária vende insumo a prazo, o leite entregue paga a conta e o crédito financia a safra.", "Organizar a conta corrente do associado e o crédito da cadeia."],
  ["Compras de leite e de suínos", "Cada litro e cada suíno comprado gera crédito tributário possível e saldo credor.", "Conferir o aproveitamento integral nos laticínios e no frigorífico."],
  ["Varejo próprio como canal", "30 lojas vendem o que a indústria produz e geram dado de venda por categoria.", "Usar o dado para decidir mix e preço e organizar o prazo entre indústria e varejo."],
  ["Logística e centrais", "7 centrais e um novo centro servem leite, queijos e carnes.", "Medir o custo por tonelada e liberar capital de giro em estoque e prazo."],
  ["Rações e suinocultura", "A ração pesa de 65% a 72% do custo do suíno e abastece também o leite.", "Margem por produto e por planta, e compras de milho e farelo com governança."],
  ["Genética e qualidade", "Genética própria, concurso de qualidade e pagamento do leite pela qualidade.", "Transformar produtividade do associado em margem, com o crédito certo."]];
lig.forEach((l, i) => {
  const x = MX + (i % 3) * 4.1, y = TOPO + Math.floor(i / 3) * 2.2;
  s.addShape("roundRect", { x, y, w: 3.95, h: 2.05, fill: { color: C.cartao }, line: { color: C.borda, width: 0.75 }, rectRadius: 0.08 });
  s.addText(l[0], { x: x + 0.18, y: y + 0.1, w: 3.6, h: 0.35, fontFace: F, fontSize: 12.5, bold: true, color: C.texto, margin: 0, valign: "top" });
  s.addText(l[1], { x: x + 0.18, y: y + 0.45, w: 3.6, h: 0.7, fontFace: F, fontSize: 10.5, color: C.texto_2, margin: 0, valign: "top" });
  s.addText("NA ESTEIRA", { x: x + 0.18, y: y + 1.15, w: 3.6, h: 0.2, fontFace: FM, fontSize: 8, color: C.ouro_texto, margin: 0 });
  s.addText(l[2], { x: x + 0.18, y: y + 1.33, w: 3.6, h: 0.7, fontFace: F, fontSize: 10.5, bold: true, color: C.texto, margin: 0, valign: "top" });
});
fonte(s, "Cooperativa Santa Clara (site e imprensa); Embrapa Suínos e Aves; Governo federal (Plano Safra). Hipóteses a validar com os números da cooperativa.");

// ───────────── 9. COMO TRABALHAMOS
s = nova("Como trabalhamos", "Um gestor de projeto conduz a esteira e conecta todas as nossas equipes à sua");
const eq = [["Gestor da esteira", "Seu único ponto de contato. Conduz o plano, cobra prazos, garante que cada passo entregue o que o próximo precisa e apresenta o painel à diretoria."],
  ["Equipes técnicas", "Tributária, jurídica, financeira e de crédito trabalham em um só projeto, com revisão antes de cada entrega. Nada vai à cooperativa sem dupla checagem."],
  ["Seus times", "Contabilidade, fiscal, financeiro e comercial da cooperativa indicam responsáveis por passo. Ensinamos a rotina de cobrança, a leitura de DRE e a conferência de créditos, para o ganho permanecer."],
  ["Remuneração", "Sempre que possível, por resultado. Sem cobrança antecipada em operações de crédito. Condições definidas por passo, depois do diagnóstico e antes da execução."]];
eq.forEach((e, i) => cartao(s, MX + (i % 2) * 6.1, TOPO + Math.floor(i / 2) * 2.2, 5.95, 2.05, e[0], e[1], { fs: 12 }));
fonte(s, "Modelo de trabalho Save. Operações de crédito: realizadas por instituições autorizadas. Sem promessa de valor, prazo ou êxito.");

// ───────────── 10. TAMANHO DO QUE ESTÁ EM JOGO
s = nova("Os resultados possíveis", "Com R$ 3 bilhões de faturamento, cada fração de margem e cada dia de prazo pesam");
S.kpi(s, MX, TOPO, 2.95, "1 ponto de margem", "R$ 30 mi", "por ano, sobre R$ 3 bi");
S.kpi(s, MX + 3.05, TOPO, 2.95, "0,1 ponto de margem", "R$ 3 mi", "por ano");
S.kpi(s, MX + 6.1, TOPO, 2.95, "1 dia de prazo de recebimento", "R$ " + fmt(3e9 / 365 / 1e6) + " mi", "de caixa parado na carteira");
S.kpi(s, MX + 9.15, TOPO, 2.95, "R$ 0,01 por litro de leite", "R$ 3,7 mi", "por ano, em 365 mi de litros");
tabela(s, MX, TOPO + 1.8, [2.4, 5.0, 4.73], ["Alavanca", "Premissa", "Faixa ilustrativa por ano"], [
  ["Prazo de recebimento", "Redução de 1, 3 ou 5 dias; custo de capital de 22,89% ao ano", "Caixa liberado de R$ 8, 25 e 41 mi; juros evitados de R$ 1,9, 5,6 e 9,4 mi"],
  ["Custo da dívida", "Cada R$ 100 mi com custo menor em 2, 4 ou 6 pontos", "R$ 2, 4 ou 6 mi por R$ 100 mi"],
  ["Crédito rural na cadeia", "Cada R$ 100 mi de capital de giro a 22,89% que passe a custeio a 9% (se elegível)", "Até R$ 13,9 mi por R$ 100 mi"],
  ["Crédito do leite", "Compra de leite de cerca de R$ 0,9 bi; créditos de 1,85% a 4,625% do valor, a 90%", "Fluxo teórico de R$ 16 a 39 mi; o diagnóstico mostra o que já está capturado"]], { fs: 10.5 });
s.addText("As linhas não se somam: algumas se sobrepõem. Valor, prazo e êxito só se confirmam depois do diagnóstico com os documentos da cooperativa.", { x: MX, y: 5.95, w: W - 2 * MX, h: 0.5, fontFace: F, fontSize: 10, italic: true, color: C.texto_2, margin: 0, valign: "top" });
fonte(s, "Cálculos Save sobre dados públicos: Jornal do Comércio (jul/2026); Cooperativa Santa Clara (jul/2026); Banco Central (SGS 20725, ago/2026); IBGE; Governo federal (Plano Safra 2026/27); NT RFB 012/2026. Estimativa preliminar sujeita a validação técnica.");

// ───────────── 11. 90 DIAS
s = nova("Como começamos", "Os primeiros 90 dias e o que precisamos ver em cada negócio");
cartao(s, MX, TOPO, 5.95, 4.3, "O que precisamos ver (sob confidencialidade)", "• DRE e balanço dos dois últimos anos, por negócio quando houver\n• Apuração de PIS/COFINS e do crédito presumido (leite e suínos); EFD-Contribuições\n• Separação do ato cooperativo e não cooperativo\n• Extrato de dívidas e custo médio\n• Carteira a receber com prazos, por canal\n• Composição das compras de leite, suínos, milho e farelo\n• Margem por linha, planta e loja, se houver", { fs: 12.5 });
cartao(s, MX + 6.1, TOPO, 6.0, 4.3, "O caminho em 90 dias", "Semanas 1–2: conversa com a diretoria, confidencialidade e documentos.\nSemanas 3–4: mapa do ecossistema e linha de base de margem, prazo e dívida (passo 1).\nSemanas 5–8: primeiro passo de execução, no negócio de maior retorno.\nSemanas 9–10: primeiro mapa de valor e desenho do passo seguinte.\nSemanas 11–13: encontro trimestral com a diretoria.\n\nVocês terão um gestor de projeto que conduz tudo.", { fs: 12.5 });

// ───────────── 12. PRÓXIMOS PASSOS
s = nova("Próximos passos", "Três decisões para começarmos");
const prox = [["1", "Escolher o primeiro negócio", "Onde o retorno tende a ser maior e o dado está mais acessível: laticínios, frigorífico ou varejo."], ["2", "Assinar a confidencialidade", "Para receber os documentos e montar o mapa e a linha de base (passo 1)."], ["3", "Indicar o responsável na cooperativa", "Um nome da diretoria e um do fiscal e financeiro, para o gestor da esteira trabalhar com eles."]];
prox.forEach((p, i) => {
  const x = MX + i * 4.1;
  s.addShape("roundRect", { x, y: TOPO + 0.2, w: 3.95, h: 3.4, fill: { color: i === 0 ? C.ouro_suave : C.cartao }, line: { color: C.borda, width: 0.75 }, rectRadius: 0.08 });
  s.addText(p[0], { x: x + 0.25, y: TOPO + 0.35, w: 1, h: 0.7, fontFace: FM, fontSize: 32, bold: true, color: C.ouro_texto, margin: 0 });
  s.addText(p[1], { x: x + 0.25, y: TOPO + 1.2, w: 3.45, h: 0.8, fontFace: F, fontSize: 16, bold: true, color: C.texto, margin: 0, valign: "top" });
  s.addText(p[2], { x: x + 0.25, y: TOPO + 2.0, w: 3.45, h: 1.4, fontFace: F, fontSize: 12.5, color: C.texto_2, margin: 0, valign: "top" });
});
s.addText("Mais lucro e mais margem, um passo de cada vez, com o resultado de cada passo abrindo o seguinte.", { x: MX, y: 5.9, w: W - 2 * MX, h: 0.5, fontFace: F, fontSize: 14, bold: true, color: C.texto, margin: 0, valign: "top" });

// ───────────── 13. FONTES
s = nova("Fontes e avisos", "Fontes oficiais e públicas, com data de consulta");
s.addText([
  { text: "Oficiais\n", options: { bold: true, fontFace: F, fontSize: 10.5, color: C.texto } },
  { text: "IBGE, SIDRA: Pesquisa Trimestral do Leite (1086), Abate de Animais (1093), IPCA (7060). Banco Central, SGS 20725 (capital de giro de pessoas jurídicas). Embrapa Suínos e Aves (custo de produção, 1T26). Governo federal: Plano Safra 2026/27. Receita Federal, NT RFB 012/2026. LC 214/2025, LC 224/2025, Lei 10.925/2004 e Lei 5.764/1971. Consultas em 21/10/2026.\n", options: { fontFace: F, fontSize: 10, color: C.texto_2, breakLine: true } },
  { text: "Públicas, sobre a cooperativa\n", options: { bold: true, fontFace: F, fontSize: 10.5, color: C.texto } },
  { text: "Cooperativa Santa Clara: site (jul e ago/2026). SuperVarejo (mar/2025). Jornal do Comércio (ago/2024, ago/2025 e jul/2026). Números de estrutura variam entre publicações; a confirmar com a cooperativa.\n", options: { fontFace: F, fontSize: 10, color: C.texto_2, breakLine: true } },
  { text: "Avisos\n", options: { bold: true, fontFace: F, fontSize: 10.5, color: C.texto } },
  { text: "Pré-análise de caráter geral, sem acesso aos dados internos da cooperativa. Não constitui parecer jurídico ou tributário nem oferta de crédito. As faixas são ilustrativas, com premissas indicadas, e dependem de documentos e de validação técnica. Valor, prazo e êxito não são prometidos. Operações de crédito são realizadas por instituições autorizadas.", options: { fontFace: F, fontSize: 10, color: C.texto_2 } },
], { x: MX, y: TOPO - 0.1, w: W - 2 * MX, h: 4.9, margin: 0, valign: "top", isTextBox: true, paraSpaceAfter: 2 });

pres.writeFile({ fileName: OUT }).then(() => console.log("ok", OUT));
