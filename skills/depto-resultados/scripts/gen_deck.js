// Gera o deck semanal de resultados a partir de metricas-AAAA-MM-DD.json + texto-AAAA-MM-DD.json
// Uso: node gen_deck.js <metricas.json> <texto.json> <saida.pptx> [pacote-gestao.json]
const fs = require('fs');
const pptxgen = require('pptxgenjs');
const [, , fMet, fTxt, out] = process.argv;
const M = JSON.parse(fs.readFileSync(fMet, 'utf8'));
const T = JSON.parse(fs.readFileSync(fTxt, 'utf8'));

// Design System Save v0.5, modo escuro (marketing-marca/padrao/marca.json), padrão desde 07/10/2026
const DS = JSON.parse(fs.readFileSync(require('path').join(process.env.HOME, 'agentes-partners/departamentos/marketing-marca/padrao/marca.json'), 'utf8'));
const h = c => c.replace('#', ''), E = DS.escuro;
const C = { bg: h(E.fundo), card: h(E.cartao), line: h(E.borda), gold: h(E.ouro), text: h(E.texto), mute: h(E.texto_2), red: h(E.erro), green: h(E.sucesso), amber: h(E.alerta) };
const F = DS.fontes.sans;  // IBM Plex Sans (instalar a partir de marketing-marca/padrao/fontes)
const mi = v => (typeof v !== 'number') ? String(v) : Math.abs(v) < 1e6 ? 'R$ ' + Math.round(v / 1e3).toLocaleString('pt-BR') + ' mil' : 'R$ ' + (v / 1e6).toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + ' mi';
const pct = v => (typeof v === 'number') ? (v > 0 ? '+' : '') + v.toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + '%' : '—';
const fx = v => (typeof v === 'number') ? v.toLocaleString('pt-BR', { maximumFractionDigits: 2 }) + 'x' : '—';
const nf = v => (typeof v === 'number') ? v.toLocaleString('pt-BR') : String(v);
const col = v => (typeof v !== 'number') ? C.mute : v >= 0 ? C.green : C.red;
const mesLbl = ym => ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'][+ym.slice(5, 7) - 1] + '/' + ym.slice(2, 4);

const pres = new pptxgen(); pres.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5
pres.title = T.titulo; pres.author = 'Área Partners · Save Company';

function base(title, kicker) {
  const s = pres.addSlide(); s.background = { color: C.bg };
  s.addText(kicker || 'RESULTADO SEMANAL · ÁREA PARTNERS', { x: 0.6, y: 0.35, w: 9, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: C.gold, charSpacing: 2, margin: 0, isTextBox: true });
  s.addText(title, { x: 0.6, y: 0.7, w: 12.1, h: 0.9, fontFace: F, fontSize: 26, bold: true, color: C.text, margin: 0, valign: 'top', isTextBox: true });
  s.addText(`${T.periodo} · fonte: ${M.fonte_principal || 'cockpit'} (${M.fonte_cockpit.gerado_em}) · margem: ${M.fonte_margem_origem || 'S&OE'}`,
    { x: 0.6, y: 7.05, w: 12.1, h: 0.25, fontFace: F, fontSize: 9, color: C.mute, margin: 0, isTextBox: true });
  return s;
}
function card(s, x, y, w, h) { s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: C.card }, line: { color: C.line, width: 0.75 }, rectRadius: 0.08 }); }
function stat(s, x, y, w, h, label, value, sub, subColor) {
  card(s, x, y, w, h);
  s.addText(label.toUpperCase(), { x: x + 0.25, y: y + 0.2, w: w - 0.5, h: 0.3, fontFace: F, fontSize: 10, bold: true, color: C.mute, margin: 0, isTextBox: true });
  s.addText(value, { x: x + 0.25, y: y + 0.5, w: w - 0.5, h: 0.75, fontFace: F, fontSize: 28, bold: true, color: C.text, margin: 0, fit: 'shrink', isTextBox: true });
  if (sub) s.addText(sub, { x: x + 0.25, y: y + h - 0.5, w: w - 0.5, h: 0.35, fontFace: F, fontSize: 11, color: subColor || C.mute, margin: 0, isTextBox: true });
}
// Pacote de gestão (4º argumento) e previsão do mesmo dia: meta D111 abre o deck (slide 2) e alimenta o semáforo (último slide)
const fPac = process.argv[5];
const G = fPac && fs.existsSync(fPac) ? JSON.parse(fs.readFileSync(fPac, 'utf8')) : null;
const fPrev = fPac ? fPac.replace(/pacote-(\d{4}-\d{2}-\d{2})\.json$/, 'previsao-$1.json') : null;
const PV = fPrev && fPrev !== fPac && fs.existsSync(fPrev) ? JSON.parse(fs.readFileSync(fPrev, 'utf8')) : null;
const cr = M.crescimento, ytd = M.crescimento_acumulado_ano, mg = M.margem_carteira || {}, L = M.lucro_roi || {};

// 1. Capa + manchete
{
  const s = pres.addSlide(); s.background = { color: C.bg };
  s.addText('SAVE · ÁREA PARTNERS', { x: 0.6, y: 0.5, w: 8, h: 0.35, fontFace: F, fontSize: 12, bold: true, color: C.gold, charSpacing: 3, margin: 0, isTextBox: true });
  s.addText(T.titulo, { x: 0.6, y: 0.95, w: 12, h: 0.7, fontFace: F, fontSize: 34, bold: true, color: C.text, margin: 0, isTextBox: true });
  s.addText(T.periodo, { x: 0.6, y: 1.65, w: 12, h: 0.4, fontFace: F, fontSize: 16, color: C.mute, margin: 0, isTextBox: true });
  card(s, 0.6, 2.35, 12.1, 1.35);
  s.addText(T.manchete, { x: 0.9, y: 2.45, w: 11.5, h: 1.15, fontFace: F, fontSize: 19, bold: true, color: C.text, margin: 0, valign: 'middle', isTextBox: true });
  const W = M.semana_hubspot, MT = M.mes_ate_hoje;
  const k = [
    W ? ['Fechado na semana', mi(W.ganhos_rs), `${pct(W.crescimento.ganhos_rs.pct)} vs semana anterior`, col(W.crescimento.ganhos_rs.pct)]
      : ['Fechado no mês', mi(cr.ganhos_rs.MoM.atual), `${pct(cr.ganhos_rs.MoM.pct)} vs mês anterior`, col(cr.ganhos_rs.MoM.pct)],
    ...(MT ? [['Fechado no mês até hoje', mi(MT.ganhos_rs), `${pct(MT.crescimento.ganhos_rs.pct)} vs mesmo período`, col(MT.crescimento.ganhos_rs.pct)]] : []),
    ...(MT ? [] : [['Fechado no ano', mi(ytd.ganhos_rs.atual), `${pct(ytd.ganhos_rs.pct)} vs ano anterior*`, col(ytd.ganhos_rs.pct)]]),
    ['Margem líquida', (mg.margem_liquida_pct ?? '—').toLocaleString('pt-BR') + '%', 'sobre o valor dos negócios', C.mute],
    ['Lucro antes de impostos', typeof L.lucro_area_mes === 'number' ? mi(M.lucro_roi_mensal ? M.lucro_roi_mensal.total.amostra.lucro_antes_impostos : L.lucro_area_mes) : 'pendente', typeof L.lucro_area_mes === 'number' ? (M.lucro_roi_mensal ? `jul–set · ROI líquido ${fx(M.lucro_roi_mensal.total.amostra.roi_liquido)}` : 'potencial/mês') : 'faltam custos e impostos', typeof L.lucro_area_mes === 'number' ? C.mute : C.amber],
  ];
  k.forEach((r, i) => stat(s, 0.6 + i * 3.08, 4.05, 2.86, 1.85, ...r));
  s.addText(T.nota_capa || '', { x: 0.6, y: 6.15, w: 12.1, h: 0.6, fontFace: F, fontSize: 11, color: C.mute, margin: 0, isTextBox: true });
}

// 2. Meta do mês e Meta do Q4 (D111: crédito de contrato fechado; out 75, nov 100, dez 75 = R$ 250 mi). Só com o pacote de gestão.
if (G && G.meta && G.meta.meses) {
  const mt = G.meta, ma = mt.mes_atual, tt = mt.total, cor = { verde: C.green, amarelo: C.amber, vermelho: C.red, cinza: C.mute };
  const s = base(T.titulo_meta || `Meta do mês: ${nf(ma.pct)}% de ${mi(ma.meta_rs)} em ${ma.nome}; Q4 em ${nf(tt.pct)}% de ${mi(tt.meta_rs)}`, 'META DO MÊS E META DO Q4 · D111 · CRÉDITO DE CONTRATO FECHADO');
  stat(s, 0.6, 1.75, 3.9, 1.75, `Meta do mês · ${ma.nome}`, `${mi(ma.realizado_rs)} de ${mi(ma.meta_rs)}`,
       `${nf(ma.pct)}% · faltam ${mi(ma.falta_rs)} em ${ma.dias_uteis_restantes} dias úteis`, cor[ma.status]);
  stat(s, 0.6, 3.65, 3.9, 1.75, 'Meta do Q4', `${mi(tt.realizado_rs)} de ${mi(tt.meta_rs)}`, `${nf(tt.pct)}% · faltam ${mi(tt.falta_rs)} em ${tt.dias_uteis_restantes} dias úteis`, cor[tt.status]);
  s.addText(`Ritmo do mês: ${mi(ma.ritmo_atual_rs_dia)}/dia útil × necessário ${mi(ma.ritmo_necessario_rs_dia)}\nRitmo do Q4: ${mi(tt.ritmo_atual)}/dia útil × necessário ${mi(tt.ritmo_necessario)}`,
    { x: 0.6, y: 5.55, w: 3.9, h: 0.6, fontFace: F, fontSize: 10, color: C.text, margin: 0, isTextBox: true });
  const pm = PV && PV.por_mes ? PV.por_mes : null, cen = (i, k) => pm ? pm.meses[i].cenarios[k] : null;
  const Hd = ['Mês', 'Meta', 'Realizado', 'Falta', 'Ritmo nec. × atual', 'Status', ...(pm ? ['Base (prob.)'] : [])].map(t => ({ text: t, options: { bold: true, color: C.gold, fill: { color: C.card } } }));
  const linhas = mt.meses.map((x, i) => [x.nome, mi(x.meta_rs), mi(x.realizado_rs), mi(x.falta_rs), `${mi(x.ritmo_necessario_rs_dia)} × ${x.ritmo_atual_rs_dia == null ? '—' : mi(x.ritmo_atual_rs_dia)}`, x.situacao === 'a iniciar' ? 'a iniciar' : x.status,
    ...(pm ? [`${mi(cen(i, 'base').esperado_rs)} (${nf(cen(i, 'base').probabilidade_meta_pct)}%)`] : [])]
    .map((t, j) => ({ text: String(t), options: { color: j === 5 ? cor[x.status] : C.text, bold: j === 5, fill: { color: C.bg } } })));
  const tot = ['Q4', mi(tt.meta_rs), mi(tt.realizado_rs), mi(tt.falta_rs), `${mi(tt.ritmo_necessario)} × ${mi(tt.ritmo_atual)}`, tt.status, ...(pm ? [`${mi(pm.total.cenarios.base.esperado_rs)} (${nf(pm.total.cenarios.base.probabilidade_meta_pct)}%)`] : [])]
    .map((t, j) => ({ text: String(t), options: { bold: true, color: j === 5 ? cor[tt.status] : C.text, fill: { color: C.card } } }));
  const cw = pm ? [1.0, 0.95, 1.05, 1.0, 1.9, 0.75, 1.35] : [1.2, 1.1, 1.2, 1.2, 2.2, 1.1];
  s.addTable([Hd, ...linhas, tot], { x: 4.75, y: 1.75, w: 8.0, colW: cw, fontFace: F, fontSize: 9, border: { type: 'solid', color: C.line, pt: 0.5 }, rowH: 0.3 });
  const pmM = (mt.por_master || {}).masters || [];
  if (pmM.length) {
    s.addText(`POR MASTER · PROPOSTA (não aprovada): ${mt.por_master.metodo}`, { x: 4.75, y: 3.45, w: 8.0, h: 0.45, fontFace: F, fontSize: 8, bold: true, color: C.gold, margin: 0, isTextBox: true });
    const H2 = ['Master', 'Peso', `Meta ${ma.nome}`, `Realizado ${ma.nome}`, 'Meta Q4 (proposta)'].map(t => ({ text: t, options: { bold: true, color: C.gold, fill: { color: C.card } } }));
    const iM = mt.meses.findIndex(x => x.mes === ma.mes);
    const r2 = pmM.slice(0, 8).map(x => [x.master, nf(x.peso_pct) + '%', mi(x.meses[iM].meta_rs), mi(x.meses[iM].realizado_rs), mi(x.meta_q4_rs)].map(t => ({ text: String(t), options: { color: C.text, fill: { color: C.bg } } })));
    s.addTable([H2, ...r2], { x: 4.75, y: 3.95, w: 8.0, colW: [2.6, 0.9, 1.5, 1.5, 1.5], fontFace: F, fontSize: 8, border: { type: 'solid', color: C.line, pt: 0.5 }, rowH: 0.25 });
  }
  s.addText(`Status: realizado ÷ proporcional aos dias úteis (verde >= 90%, amarelo >= 70%). Volume limpo: sem duplicidade de alta confiança (${mi(tt.duplicidade_rs || 0)} fora no Q4).${pm ? ' Probabilidade: Monte Carlo da previsão do dia; estimativa, não promessa.' : ''}`,
    { x: 0.6, y: 6.6, w: 12.1, h: 0.35, fontFace: F, fontSize: 8.5, color: C.mute, margin: 0, isTextBox: true });
}

// 2. Confiabilidade dos dados
{
  const s = base(T.titulo_dados || 'Antes dos números: o que limita a leitura desta semana', 'CONFIABILIDADE DOS DADOS');
  const items = M.alertas.concat(T.ressalvas || []);
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: { indent: 14 }, breakLine: i < items.length - 1 } })),
    { x: 0.6, y: 1.8, w: 7.4, h: 4.9, fontFace: F, fontSize: 14, color: C.text, paraSpaceAfter: 10, valign: 'top', isTextBox: true });
  card(s, 8.4, 1.8, 4.3, 4.9);
  s.addText('PENDÊNCIAS PARA FECHAR O RELATÓRIO', { x: 8.65, y: 2.0, w: 3.9, h: 0.35, fontFace: F, fontSize: 10, bold: true, color: C.gold, margin: 0, isTextBox: true });
  s.addText(M.pendencias.map((t, i) => ({ text: t, options: { bullet: { indent: 14 }, breakLine: i < M.pendencias.length - 1 } })),
    { x: 8.65, y: 2.4, w: 3.9, h: 4.1, fontFace: F, fontSize: 11, color: C.text, paraSpaceAfter: 6, valign: 'top', isTextBox: true });
}

// 3. Volume criado x fechado (13 meses)
{
  const s = base(T.titulo_volume, 'VOLUME DE NEGÓCIOS');
  const ms = Object.keys(M.serie_mensal);
  s.addChart(pres.charts.BAR, [{ name: 'Fechado (R$ mi)', labels: ms.map(mesLbl), values: ms.map(m => +(M.serie_mensal[m].ganhos_rs / 1e6).toFixed(1)) }], {
    x: 0.6, y: 1.8, w: 8.2, h: 4.9, barDir: 'col', chartColors: [C.gold], showValue: true, dataLabelPosition: 'outEnd', dataLabelColor: C.text, dataLabelFontSize: 9,
    showTitle: true, title: 'Valor fechado por mês (R$ mi)', titleColor: C.text, titleFontSize: 12, catAxisLabelColor: C.mute, valAxisLabelColor: C.mute,
    valGridLine: { color: C.line, size: 0.5 }, catGridLine: { style: 'none' }, showLegend: false, valAxisLabelFontSize: 9, catAxisLabelFontSize: 9 });
  const MT3 = M.mes_ate_hoje;
  if (MT3) {
    stat(s, 9.1, 1.8, 3.6, 1.5, 'Criados no mês até hoje', `${nf(MT3.criados_n)} · ${mi(MT3.criados_rs)}`, `${pct(MT3.crescimento.criados_n.pct)} em nº vs mesmo período`, col(MT3.crescimento.criados_n.pct));
    stat(s, 9.1, 3.5, 3.6, 1.5, 'Fechados no mês até hoje', `${nf(MT3.ganhos_n)} · ${mi(MT3.ganhos_rs)}`, `${pct(MT3.crescimento.ganhos_rs.pct)} em R$ vs mesmo período`, col(MT3.crescimento.ganhos_rs.pct));
  } else {
  stat(s, 9.1, 1.8, 3.6, 1.5, 'Criados no mês', nf(cr.criados_n.MoM.atual), `${pct(cr.criados_n.MoM.pct)} MoM · ${pct(cr.criados_n.YoY.pct)} YoY`, col(cr.criados_n.MoM.pct));
  stat(s, 9.1, 3.5, 3.6, 1.5, 'Fechados no mês', `${nf(cr.ganhos_n.MoM.atual)} · ${mi(cr.ganhos_rs.MoM.atual)}`, `${pct(cr.ganhos_rs.MoM.pct)} MoM em R$`, col(cr.ganhos_rs.MoM.pct));
  }
  stat(s, 9.1, 5.2, 3.6, 1.5, 'Semana', M.semana.criados_n != null ? `${nf(M.semana.criados_n)} criados · ${nf(M.semana.ganhos_n)} ganhos` : '—', M.semana_hubspot ? `${M.semana_hubspot.de} a ${M.semana_hubspot.ate} · fechado ${pct(M.semana_hubspot.crescimento.ganhos_rs.pct)}` : (M.semana.criados_n != null ? `desde ${M.semana.desde}` : 'comparação semanal começa na próxima edição'), C.mute);
}

// 4. Crescimento
{
  const s = base(T.titulo_crescimento, 'FATOR E % DE CRESCIMENTO');
  const hdr = ['Métrica', 'Atual', 'Fator MoM', '% MoM', 'Fator YoY', '% YoY', 'Acum. ano', '% acum.'].map(t => ({ text: t, options: { bold: true, color: C.bg, fill: { color: C.gold } } }));
  const lin = [['Negócios criados (nº)', 'criados_n', nf], ['Negócios criados (R$)', 'criados_rs', mi], ['Negócios fechados (nº)', 'ganhos_n', nf], ['Negócios fechados (R$)', 'ganhos_rs', mi]];
  const rows = [hdr].concat(lin.map(([n, k, f]) => [n, f(cr[k].MoM.atual), fx(cr[k].MoM.fator), pct(cr[k].MoM.pct), fx(cr[k].YoY.fator), pct(cr[k].YoY.pct), f(ytd[k].atual), pct(ytd[k].pct)]
    .map((t, j) => ({ text: String(t), options: { color: [3, 5, 7].includes(j) ? col(parseFloat(String(t).replace(',', '.'))) : C.text, fill: { color: C.card } } }))));
  s.addTable(rows, { x: 0.6, y: 1.8, w: 12.1, colW: [2.9, 1.7, 1.1, 1.1, 1.1, 1.1, 1.9, 1.2], fontFace: F, fontSize: 12, border: { type: 'solid', color: C.line, pt: 0.75 }, rowH: 0.5 });
  s.addText(T.leitura_crescimento, { x: 0.6, y: 4.3, w: 12.1, h: 2.2, fontFace: F, fontSize: 13, color: C.text, margin: 0, valign: 'top', isTextBox: true });
}

// 5. Margem
{
  const s = base(T.titulo_margem, 'MARGEM E MARGEM LÍQUIDA');
  s.addChart(pres.charts.BAR, [{ name: 'R$ mi', labels: ['Valor dos negócios', 'Honorário bruto Save', 'Repasse ao parceiro', 'Honorário líquido Save'],
    values: [mg.valor, mg.honorario_bruto, mg.repasse, mg.honorario_liquido].map(v => +(v / 1e6).toFixed(1)) }], {
    x: 0.6, y: 1.8, w: 6.3, h: 4.9, barDir: 'bar', chartColors: [C.gold], showValue: true, dataLabelPosition: 'outEnd', dataLabelColor: C.text, dataLabelFontSize: 10,
    showTitle: true, title: `Carteira de margem: ${nf(mg.negocios)} negócios (R$ mi)`, titleColor: C.text, titleFontSize: 12, catAxisLabelColor: C.text, valAxisLabelColor: C.mute,
    valGridLine: { color: C.line, size: 0.5 }, catGridLine: { style: 'none' }, showLegend: false, catAxisLabelFontSize: 10, valAxisLabelFontSize: 9 });
  stat(s, 7.2, 1.8, 2.7, 1.5, 'Margem bruta', `${(mg.margem_bruta_pct ?? 0).toLocaleString('pt-BR')}%`, 'honorário ÷ valor');
  stat(s, 10.0, 1.8, 2.7, 1.5, 'Margem líquida', `${(mg.margem_liquida_pct ?? 0).toLocaleString('pt-BR')}%`, 'após repasse');
  const top = (M.margem_top10 || []).slice(0, 5);
  const rows = [['Maiores margens líquidas', 'Hon.', 'Parc.', 'Líquido'].map(t => ({ text: t, options: { bold: true, color: C.bg, fill: { color: C.gold } } }))]
    .concat(top.map(x => [String(x.nome).replace(/^Negócio - /, '').slice(0, 40), `${Math.round((x.hContr || 0) * 100)}%`, `${Math.round((x.hParc || 0) * 100)}%`, mi(x.liquido)]
      .map(t => ({ text: t, options: { color: C.text, fill: { color: C.card } } }))));
  s.addTable(rows, { x: 7.2, y: 3.5, w: 5.5, colW: [3.1, 0.7, 0.7, 1.0], fontFace: F, fontSize: 9, border: { type: 'solid', color: C.line, pt: 0.5 }, rowH: 0.36 });
  s.addText(T.leitura_margem, { x: 7.2, y: 5.8, w: 5.5, h: 1.0, fontFace: F, fontSize: 11, color: C.mute, margin: 0, valign: 'top', isTextBox: true });
}

// 6. Lucro e ROI
{
  const s = base(T.titulo_lucro, 'LUCRO DA ÁREA E ROI');
  const step = [['Honorário bruto/mês', L.honorario_bruto_mes], ['(−) Repasse ao parceiro', typeof L.honorario_bruto_mes === 'number' ? L.honorario_bruto_mes - L.honorario_liquido_mes : '—'],
    ['(−) Impostos sobre a receita', L.impostos_mes ?? 'pendente'], ['(−) Custos da área', L.custos_mes ?? 'pendente'], [String(L.impostos_mes || '').includes('antes') ? '= Lucro antes de impostos' : '= Lucro da área', L.lucro_area_mes]];
  step.forEach(([lbl, v], i) => {
    const y = 1.85 + i * 0.95; card(s, 0.6, y, 6.3, 0.8);
    s.addText(lbl, { x: 0.85, y, w: 3.6, h: 0.8, fontFace: F, fontSize: 14, bold: i === 4, color: C.text, margin: 0, valign: 'middle', isTextBox: true });
    const ai = String(v).includes('antes'); const pend = typeof v !== 'number' && !ai;
    s.addText(ai ? 'não considerado' : pend ? 'PENDENTE' : mi(v), { x: 4.4, y, w: 2.3, h: 0.8, fontFace: F, fontSize: ai ? 12 : 16, bold: true, color: ai ? C.mute : pend ? C.amber : (i === 4 ? C.gold : C.text), margin: 0, align: 'right', valign: 'middle', isTextBox: true });
  });
  const rows = [['ROI', 'Potencial', 'Ajustado ao risco', 'Realizado (oficial)'].map(t => ({ text: t, options: { bold: true, color: C.bg, fill: { color: C.gold } } })),
    ['ROI total', L.roi_total_potencial, 'pendente (glosa)', 'sem dado de caixa'], ['ROI líquido', L.roi_liquido_potencial, 'pendente (glosa)', 'sem dado de caixa']]
    .map((r, i) => i === 0 ? r : r.map((t, j) => ({ text: typeof t === 'number' ? fx(t) : String(t).replace(/^\[|\]$/g, ''), options: { color: (j === 0 || typeof t === 'number') ? C.text : C.amber, fill: { color: C.card } } })));
  s.addTable(rows, { x: 7.2, y: 1.85, w: 5.5, colW: [1.2, 1.3, 1.5, 1.5], fontFace: F, fontSize: 11, border: { type: 'solid', color: C.line, pt: 0.5 }, rowH: 0.45 });
  const LM = M.lucro_roi_mensal;
  if (LM) {
    const H = ['Mês', 'Custo', 'Hon. líquido', 'Lucro a.i.', 'ROI líq.'].map(t => ({ text: t, options: { bold: true, color: C.bg, fill: { color: C.gold } } }));
    const rr = LM.meses.map(x => [mesLbl(x.mes) + (x.custo_base.startsWith('ORÇ') ? '*' : ''), mi(x.custo), mi(x.amostra.honorario_liquido), mi(x.amostra.lucro_antes_impostos), fx(x.amostra.roi_liquido)])
      .concat([['Total', mi(LM.total.custo), mi(LM.total.amostra.honorario_liquido), mi(LM.total.amostra.lucro_antes_impostos), fx(LM.total.amostra.roi_liquido)]])
      .map((r, i, a) => r.map(t => ({ text: t, options: { color: C.text, bold: i === a.length - 1, fill: { color: C.card } } })));
    s.addTable([H].concat(rr), { x: 7.2, y: 3.55, w: 5.5, colW: [0.9, 1.05, 1.25, 1.25, 1.05], fontFace: F, fontSize: 10, border: { type: 'solid', color: C.line, pt: 0.5 }, rowH: 0.3 });
  }
  s.addText(T.leitura_lucro, { x: 7.2, y: LM ? 5.25 : 3.8, w: 5.5, h: LM ? 1.6 : 3.0, fontFace: F, fontSize: 12, color: C.text, margin: 0, valign: 'top', isTextBox: true });
}

// 7. Funil e canal
{
  const s = base(T.titulo_funil, 'FUNIL, CANAL E RISCO DE CONCENTRAÇÃO');
  const c = M.concentracao_12m, pa = M.parceiros_ativos_90d, q = M.qualidade_dados;
  stat(s, 0.6, 1.8, 2.9, 1.6, 'Win rate (3 meses)', `${(M.win_rate_3m ?? 0).toLocaleString('pt-BR')}%`, 'ganhos ÷ (ganhos + perdidos)');
  stat(s, 3.65, 1.8, 2.9, 1.6, 'Ticket médio (3m)', mi(M.ticket_valor_3m), 'valor do negócio');
  stat(s, 6.7, 1.8, 2.9, 1.6, 'Pipeline aberto', mi(M.pipeline_aberto.rs), `${nf(M.pipeline_aberto.n)} negócios`);
  stat(s, 9.75, 1.8, 2.95, 1.6, 'Parceiros ativos (90d)', `${pa.ativos} de ${pa.carteira}`, 'com negócio criado');
  s.addChart(pres.charts.DOUGHNUT, [{ name: 'Concentração', labels: c.top5.map(p => p[0].split(' ')[0]).concat(['Demais']),
    values: c.top5.map(p => p[1]).concat([Math.max(0, c.top5.reduce((a, p) => a + p[1], 0) / (c.top5_pct / 100) - c.top5.reduce((a, p) => a + p[1], 0))]) }], {
    x: 0.6, y: 3.65, w: 4.6, h: 3.2, holeSize: 60, showPercent: true, showLegend: true, legendPos: 'r', legendColor: C.text, legendFontSize: 9, dataLabelColor: C.bg, dataLabelFontSize: 9,
    chartColors: [C.gold, 'C9A227', '9C7F1E', '6E5A17', '4A3D10', '3A3B41'], showTitle: true, title: 'Valor fechado em 12 meses por parceiro', titleColor: C.text, titleFontSize: 11 });
  card(s, 5.5, 3.65, 7.2, 3.2);
  s.addText(T.leitura_funil + `\n\nQualidade de dados: ${nf(q.abertos_sem_segmento_n)} negócios abertos sem segmento (${mi(q.abertos_sem_segmento_rs)}).`,
    { x: 5.75, y: 3.85, w: 6.7, h: 2.85, fontFace: F, fontSize: 12, color: C.text, margin: 0, valign: 'top', isTextBox: true });
}

// 8. Decisões
{
  const s = base(T.titulo_decisoes || 'O que precisa de decisão ou ação', 'DESTAQUES, RISCOS E DECISÕES');
  const blocos = [['DESTAQUES', T.destaques], ['RISCOS', T.riscos], ['DECISÕES / AÇÕES PEDIDAS', T.decisoes]];
  blocos.forEach(([h, arr], i) => {
    const x = 0.6 + i * 4.1; card(s, x, 1.8, 3.9, 5.0);
    s.addText(h, { x: x + 0.25, y: 2.0, w: 3.4, h: 0.35, fontFace: F, fontSize: 11, bold: true, color: C.gold, margin: 0, isTextBox: true });
    s.addText(arr.map((t, j) => ({ text: t, options: { bullet: { indent: 14 }, breakLine: j < arr.length - 1 } })),
      { x: x + 0.25, y: 2.45, w: 3.45, h: 4.2, fontFace: F, fontSize: 12, color: C.text, paraSpaceAfter: 8, valign: 'top', isTextBox: true });
  });
}

// Último slide: semáforo de gestão (pacote_gestao.py → registro/gestao/pacote-AAAA-MM-DD.json; 4º argumento, opcional)
if (G) {
  const s = base('Semáforo de gestão: resultado, previsibilidade e controle', 'SEMÁFORO DE GESTÃO · TOLERÂNCIAS PROPOSTAS');
  const cor = { verde: C.green, amarelo: C.amber, vermelho: C.red, cinza: C.mute };
  const val = m => m.valor === null || m.valor === undefined ? 'sem dado' : m.unidade === 'R$' ? mi(m.valor) : m.unidade === '%' ? nf(m.valor) + '%' : m.unidade === 'x' ? fx(m.valor) : nf(m.valor) + (m.unidade === 'n' ? '' : ' ' + m.unidade);
  const ordem = { vermelho: 0, amarelo: 1, verde: 2, cinza: 3 };
  const lista = G.metricas.filter(m => !m.id.startsWith('meta_')).sort((a, b) => ordem[a.status] - ordem[b.status]).slice(0, 22);
  const H = ['Métrica', 'Valor', 'Status', 'Tolerância (proposta)'].map(t => ({ text: t, options: { bold: true, color: C.gold, fill: { color: C.card } } }));
  const rows = lista.map(m => [m.nome, val(m), m.status === 'cinza' ? 'sem dado' : m.status, m.tolerancia.verde || '—']
    .map((t, j) => ({ text: t, options: { color: j === 2 ? cor[m.status] : C.text, bold: j === 2, fill: { color: C.bg } } })));
  s.addTable([H].concat(rows), { x: 0.6, y: 1.75, w: 8.3, colW: [4.0, 1.4, 0.9, 2.0], fontFace: F, fontSize: 8, border: { type: 'solid', color: C.line, pt: 0.5 }, rowH: 0.22 });
  const mt = G.meta, ma = mt.mes_atual || {}, tt = mt.total || {};
  card(s, 9.2, 1.75, 3.5, 5.1);
  s.addText(`META · ${mi(mt.q4_rs).toUpperCase()} NO Q4 (D111)`, { x: 9.4, y: 1.9, w: 3.1, h: 0.3, fontFace: F, fontSize: 10, bold: true, color: C.gold, margin: 0, isTextBox: true });
  const linhas = [
    'Unidade: crédito de contrato fechado (ganho), volume limpo',
    `Meta do mês (${ma.nome}): ${mi(ma.realizado_rs)} de ${mi(ma.meta_rs)} (${nf(ma.pct)}%) · ritmo ${mi(ma.ritmo_atual_rs_dia)}/dia útil × necessário ${mi(ma.ritmo_necessario_rs_dia)}`,
    `Meta do Q4: ${mi(tt.realizado_rs)} de ${mi(tt.meta_rs)} (${nf(tt.pct)}%) · ritmo ${mi(tt.ritmo_atual)}/dia útil × necessário ${mi(tt.ritmo_necessario)}`,
    `Dias úteis do Q4: ${tt.dias_uteis_decorridos} decorridos · ${tt.dias_uteis_restantes} restantes`,
    `Qualidade: índice ${nf(G.confiabilidade.indice_qualidade_ganhos)}% · ${nf(G.confiabilidade.ganhos_sem_honorario_pct)}% dos ganhos sem honorário · ${nf(G.confiabilidade.duplicados_grupos)} grupos duplicados`,
    `Status: ${Object.entries(G.resumo_status).map(([k, v]) => `${v} ${k}`).join(' · ')}`,
    'Tolerâncias são propostas do Controller até o Luis aprovar; cinza = sem dado (quem fornece está na nota de cada métrica).'];
  s.addText(linhas.map((t, j) => ({ text: t, options: { bullet: { indent: 12 }, breakLine: j < linhas.length - 1 } })),
    { x: 9.4, y: 2.3, w: 3.15, h: 4.4, fontFace: F, fontSize: 9.5, color: C.text, paraSpaceAfter: 6, valign: 'top', isTextBox: true });
}

pres.writeFile({ fileName: out }).then(f => console.log('ok', f));
