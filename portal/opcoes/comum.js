/* Central Partners v2 · lógica comum das 3 opções de layout (mesmas funções, só o visual muda).
   Dados: window.EX (exemplo-dados.js). Botões de gravar são simulados nesta fase. */
const C = (() => {
  const X = window.EX;
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
  const url = u => /^https:\/\//i.test(String(u || "")) ? esc(u) : "";
  const sem = s => String(s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const data = iso => { if (!iso) return ""; const [d, h] = iso.split("T"); const [, m, dd] = d.split("-"); return `${dd}/${m}${h ? " " + h.slice(0, 5) : ""}` };
  const mi = v => !v ? "—" : v >= 1e6 ? "R$ " + (v / 1e6).toFixed(1).replace(".", ",") + " mi" : "R$ " + Math.round(v / 1e3) + " mil";
  const PESSOAS = {luis: "Luis", daniela: "Daniela", jenifer: "Jenifer", geovana: "Geovana"};
  const FASES = [["fila", "Na fila"], ["analise", "Em análise"], ["aprovar", "Pronto para aprovar"], ["concluido", "Concluído"]];
  const FASE = {novo: "fila", nova_analise: "fila", em_analise: "analise", aguardando_aprovacao: "aprovar", aprovado: "concluido", concluido: "concluido", nao_aprovado: "concluido"};
  const fase = p => FASE[p.status] || "fila";
  const rotFase = p => p.status === "nova_analise" ? "Na fila · ajuste pedido" : FASES.find(f => f[0] === fase(p))[1];
  const area = sk => X.areas.find(a => a.skill === sk);
  const nomeArea = sk => sk ? (area(sk)?.nome || sk) : "Central de Agentes";
  const md = t => { let h = "", l = false;
    for (const x of String(t || "").split("\n")) { const s = esc(x.trim()).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
      if (s.startsWith("- ")) { if (!l) { h += "<ul>"; l = true } h += `<li>${s.slice(2)}</li>`; continue }
      if (l) { h += "</ul>"; l = false } if (s) h += `<p>${s}</p>` } return h + (l ? "</ul>" : "") };

  const st = {eu: "daniela"};
  const mesa = (p = st.eu) => {
    const dem = X.demandas.filter(d => d.pessoa === p);
    return {
      prontos: X.pedidos.filter(x => x.solicitante === p && x.status === "aguardando_aprovacao"),
      responder: dem.filter(d => d.status === "responder"), acompanhar: dem.filter(d => d.status !== "responder"),
      chamados: X.chamados.filter(c => c.pessoa === p && c.status === "proposto"),
      lote: p === "geovana" ? X.lote : [],
      andamento: X.pedidos.filter(x => x.solicitante === p && ["fila", "analise"].includes(fase(x))),
      decisoes: p === "luis" ? X.decisoes : [],
      arquivos: X.arquivos[p] || [],
      pasta: X.pessoas.find(x => x.chave === p) || {},
    };
  };
  const pendentes = (p = st.eu) => { const m = mesa(p); return m.prontos.length + m.responder.length + m.chamados.length + m.lote.length + (p === "luis" ? X.decisoes_total : 0) };

  // Índice da busca "Onde está"
  let IDX = null;
  const indice = () => {
    if (IDX) return IDX; const R = [];
    for (const a of X.areas) {
      R.push({tipo: "Área", titulo: a.nome, sub: a.bloco + " · dono: " + a.dono, det: a.missao, onde: a.onde, links: a.links, area: a.skill});
      for (const e of a.entregas) R.push({tipo: "Entrega", titulo: e.entrega, sub: a.nome + (e.quando ? " · " + e.quando : ""), det: e.conteudo, onde: e.onde, quem: e.quem_recebe, links: e.links, area: a.skill});
      for (const e of a.especialistas) R.push({tipo: "Especialista", titulo: e.nome, sub: a.nome, det: e.entrega, onde: "", links: [], area: a.skill});
    }
    for (const r of X.rotinas) R.push({tipo: "Rotina", titulo: r.nome, sub: r.quando, det: r.entrega, onde: r.onde, links: r.links});
    for (const p of X.pastas) R.push({tipo: "Pasta", titulo: p.rotulo, sub: p.caminho, det: p.uso, onde: p.caminho, links: url(p.url) ? [{rotulo: p.rotulo, url: p.url}] : []});
    for (const p of X.pessoas) R.push({tipo: "Pessoa", titulo: p.nome, sub: p.pasta, det: p.papel, onde: p.pasta, links: url(p.url) ? [{rotulo: "de " + p.nome, url: p.url}] : []});
    for (const r of R) { r.t = sem(r.titulo); r.all = sem([r.tipo, r.titulo, r.sub, r.det, r.onde, r.quem].join(" ")) }
    return IDX = R;
  };
  const peso = {Entrega: 3, Pasta: 2, Rotina: 2, "Área": 2, Pessoa: 1, Especialista: 0};
  const buscar = (q, n = 30) => { const ts = sem(q).trim().split(/\s+/).filter(Boolean); if (!ts.length) return [];
    return indice().filter(r => ts.every(t => r.all.includes(t))).map(r => ({r, s: (ts.every(t => r.t.includes(t)) ? 10 : 0) + peso[r.tipo]})).sort((a, b) => b.s - a.s).slice(0, n).map(x => x.r) };
  const foraOneDrive = o => /^(Mac:|na conversa|repositório|pasta confidencial|~\/)/i.test(o || "");
  const linkPastas = (ls, cls = "") => (ls || []).filter(l => url(l.url)).map(l => `<a class="${cls}" href="${url(l.url)}" target="_blank" rel="noopener">Abrir pasta ${esc(l.rotulo)}</a>`).join(" ");

  // Ícones (traço 1.8, 24x24)
  const P = {
    mesa: "M3 10.5 12 4l9 6.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z",
    pedidos: "M4 4h16v16H4zM8 9h8M8 13h8M8 17h5",
    areas: "M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z",
    onde: "M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM20 20l-4-4",
    rotinas: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 7v5l3 3",
    decisoes: "M5 12l4 4 10-10",
    sino: "M6 16V11a6 6 0 1 1 12 0v5l2 2H4zM10 20a2 2 0 0 0 4 0",
    mais: "M12 5v14M5 12h14",
    fechar: "M6 6l12 12M18 6 6 18",
    seta: "M9 6l6 6-6 6",
    voltar: "M15 6l-6 6 6 6",
    menu: "M4 7h16M4 12h16M4 17h16",
    pasta: "M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",
    alerta: "M12 4 2 20h20zM12 10v4M12 17v.5",
    raio: "M13 3 5 14h6l-1 7 8-11h-6z",
  };
  const icone = (n, cls = "ic") => `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="${P[n]}"/></svg>`;

  const toast = t => { let el = document.getElementById("toast"); if (!el) { el = document.createElement("div"); el.id = "toast"; el.setAttribute("role", "status"); document.body.appendChild(el) }
    el.textContent = t + " (simulação: nesta prévia nada é gravado)"; el.className = "toast mostra"; clearTimeout(el._t); el._t = setTimeout(() => el.className = "toast", 3200) };

  // Roteador por hash: #rota/param
  const rota = () => { const h = decodeURIComponent((location.hash || "").slice(1)); const [r, ...p] = h.split("/"); return {r: r || "", p: p.join("/")} };

  return {X, esc, url, sem, data, mi, md, PESSOAS, FASES, fase, rotFase, area, nomeArea, st, mesa, pendentes, buscar, foraOneDrive, linkPastas, icone, toast, rota};
})();
