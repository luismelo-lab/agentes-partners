"use strict";
const $ = (id) => document.getElementById(id);
const COM_ESTEIRA = ["confirmado_real", "provavel_real", "nao_real", "sem_dado"];
const BLOCOS = [["fazer", "O que você pediu"], ["precisa", "O que você também precisa"], ["falta", "O que falta e quem fornece"]];
const SECAO_ABERTA = "Resumo e aderência"; // as demais seções do dossiê começam recolhidas
const INTERVALO_MS = 5000, MAX_TENTATIVAS = 240, MAX_FALHAS = 6;
let ultimos = [];
let modoVarios = false;
const sondas = new Map(); // id do pedido → intervalo de atualização

function formatar(c) {
  return /^[0-9A-Z]{14}$/.test(c) ? c.replace(/^(.{2})(.{3})(.{3})(.{4})(.{2})$/, "$1.$2.$3/$4-$5") : c;
}

function el(tag, classe, texto) {
  const e = document.createElement(tag);
  if (classe) e.className = classe;
  if (texto !== undefined) e.textContent = texto;
  return e;
}

// Rótulo do andamento sem jargão ("agentes" vira "Save"); minúsculo para entrar no meio da frase.
function andamentoTexto(v) { return String((v && v.andamento) || "em análise").toLowerCase().replace("pelos agentes", "pela Save"); }

function avisar(texto) { $("status").textContent = texto; }

function mostrarErro(texto) { $("erro").textContent = texto; $("erro").hidden = false; }

// Corpo da seção: parágrafos e lista (sempre textContent, nunca innerHTML).
function corpo(paragrafos, itens) {
  const d = el("div", "corpo");
  (paragrafos || []).filter(Boolean).forEach((t) => d.append(el("p", "meta", t)));
  if ((itens || []).length) { const ul = el("ul", "esteira"); itens.forEach((t) => ul.append(el("li", "", t))); d.append(ul); }
  return d;
}

// Bloco de resumo: sempre aberto.
function bloco(titulo, paragrafos, itens) {
  const d = el("section", "secao");
  d.append(el("h4", "titulo", titulo), corpo(paragrafos, itens));
  return d;
}

// Seção longa do dossiê: recolhível; lembra o que o parceiro abriu quando a página atualiza.
function recolhivel(area, titulo, paragrafos, itens) {
  const d = el("details", "secao recolhivel");
  d.open = area._abertas.has(titulo);
  d.append(el("summary", "titulo", titulo), corpo(paragrafos, itens));
  d.addEventListener("toggle", () => { if (d.open) area._abertas.add(titulo); else area._abertas.delete(titulo); });
  return d;
}

// ---------- pedido (dossiê) de uma empresa ----------
function baixarWord(botao, v, cnpj, aviso) {
  botao.addEventListener("click", async () => {
    botao.disabled = true; botao.textContent = "Preparando o Word…"; aviso.hidden = true;
    try {
      const resp = await fetch("/api/esteira/arquivo?id=" + encodeURIComponent(v.id));
      if (!resp.ok) throw new Error("falhou");
      const a = el("a"); a.href = URL.createObjectURL(await resp.blob());
      a.download = "dossie-" + cnpj + ".docx"; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    } catch (e) {
      aviso.textContent = "Não foi possível baixar o Word agora. Tente de novo em instantes."; aviso.hidden = false;
    } finally { botao.disabled = false; botao.textContent = "Baixar o dossiê em Word"; }
  });
}

function mostrar(area, v, cnpj) {
  area.replaceChildren();
  if (v.status !== "entregue") {
    area.append(el("p", "meta andamento", "Dossiê em preparo: " + andamentoTexto(v) + ". Esta tela atualiza sozinha."));
    return;
  }
  const r = v.resultado || {};
  const topo = el("div", "topo-dossie");
  topo.append(el("span", "selo-pronto", "Dossiê pronto"));
  const aviso = el("p", "erro-msg", ""); aviso.hidden = true; aviso.setAttribute("role", "alert");
  if (v.arquivo) {
    const b = el("button", "botao-sec", "Baixar o dossiê em Word"); b.type = "button";
    baixarWord(b, v, cnpj, aviso); topo.append(b);
  }
  area.append(topo, aviso);
  if (v.aprofundando) area.append(el("p", "faixa-aprofundando", "Esta é a versão inicial. A Save está aprofundando a análise e esta tela atualiza quando terminar."));

  // seções do dossiê com o mesmo nome de um bloco de resumo substituem o texto corrido (evita repetir)
  const dossie = r.dossie || [], titulosBloco = BLOCOS.map((b) => b[1]);
  const doBloco = new Map(dossie.filter((s) => titulosBloco.includes(s.titulo)).map((s) => [s.titulo, s]));
  BLOCOS.forEach(([k, t]) => {
    const s = doBloco.get(t);
    area.append(s ? bloco(t, s.paragrafos, s.itens) : bloco(t, [r[k]]));
  });
  const longas = dossie.filter((s) => !titulosBloco.includes(s.titulo));
  const esteira = (r.esteira || []).map((x) => "Onda " + x.onda + " · " + x.produto + (x.status ? " (" + x.status + ")" : "") + (x.nota ? ": " + x.nota : ""));
  if (longas.length || esteira.length) {
    area.append(el("h4", "titulo titulo-dossie", "Dossiê completo"));
    longas.forEach((s) => area.append(recolhivel(area, s.titulo, s.paragrafos, s.itens)));
    if (esteira.length) area.append(recolhivel(area, "Esteira", [], esteira));
  }
}

function acompanhar(area, id, cnpj) {
  if (sondas.has(id)) clearInterval(sondas.get(id));
  let ultimo = "", tentativas = 0, falhas = 0, voando = false;
  const parar = () => { clearInterval(t); sondas.delete(id); };
  const t = setInterval(async () => {
    if (!area.isConnected) { parar(); return; }
    if (document.hidden || voando) return; // aba em segundo plano ou resposta ainda pendente
    tentativas += 1;
    if (tentativas > MAX_TENTATIVAS) { parar(); desistir(area, id, cnpj, "A atualização automática parou."); return; }
    voando = true;
    try {
      const resp = await fetch("/api/esteira?id=" + encodeURIComponent(id));
      if (!resp.ok) throw new Error("http " + resp.status);
      const v = await resp.json(); falhas = 0;
      if (!area.isConnected) { parar(); return; }
      const chave = JSON.stringify(v);
      if (chave !== ultimo) {
        ultimo = chave; mostrar(area, v, cnpj);
        if (v.status === "entregue") avisar(v.aprofundando ? "A versão inicial do dossiê está pronta. A análise continua." : "Dossiê pronto.");
      }
      if (v.status === "entregue" && !v.aprofundando) parar();
    } catch (e) {
      falhas += 1;
      if (falhas >= MAX_FALHAS) { parar(); desistir(area, id, cnpj, "Perdemos a conexão com o andamento do dossiê."); }
    } finally { voando = false; }
  }, INTERVALO_MS);
  sondas.set(id, t);
}

function desistir(area, id, cnpj, motivo) {
  if (!area.isConnected) return;
  const p = el("p", "erro-msg", motivo + " ");
  const b = el("button", "link", "Atualizar agora"); b.type = "button";
  b.addEventListener("click", async () => {
    try {
      const resp = await fetch("/api/esteira?id=" + encodeURIComponent(id));
      if (!resp.ok) throw new Error("http");
      const v = await resp.json(); mostrar(area, v, cnpj); seguir(area, v, cnpj);
    } catch (e) { p.textContent = "Ainda sem conexão. Tente novamente em instantes. "; p.append(b); }
  });
  p.append(b); area.append(p); avisar(motivo);
}

function seguir(area, v, cnpj) {
  mostrar(area, v, cnpj);
  avisar(v.status === "entregue" ? (v.aprofundando ? "A versão inicial do dossiê está pronta. A análise continua." : "Dossiê pronto.") : "Dossiê em preparo: " + andamentoTexto(v) + ".");
  if (v.status !== "entregue" || v.aprofundando) acompanhar(area, v.id, cnpj);
}

function areaEsteira(cnpj, pedido) {
  const area = el("div", "area-esteira");
  area._abertas = new Set([SECAO_ABERTA]);
  if (pedido) { seguir(area, pedido, cnpj); return area; }
  const b = el("button", "botao-sec", "Pedir análise e dossiê");
  b.type = "button";
  b.addEventListener("click", async () => {
    b.disabled = true; b.textContent = "Montando o dossiê…";
    area.querySelectorAll(".erro-msg").forEach((n) => n.remove());
    try {
      const resp = await fetch("/api/esteira", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ cnpj }) });
      const v = await resp.json().catch(() => ({}));
      if (!resp.ok) throw new Error(v.erro || "Não foi possível pedir a análise.");
      b.remove(); seguir(area, v, cnpj); carregarHistorico();
    } catch (e) {
      b.disabled = false; b.textContent = "Pedir análise e dossiê";
      const aviso = el("p", "erro-msg", e instanceof TypeError ? "Sem conexão. Verifique a internet e tente de novo." : e.message);
      aviso.setAttribute("role", "alert"); area.append(aviso);
    }
  });
  area.append(b);
  return area;
}

// ---------- resultado da consulta ----------
function cartao(r, pedido) {
  const c = el("article", "res " + r.faixa);
  c.append(el("div", "cnpj", formatar(r.cnpj)));
  if (r.empresa) {
    c.append(el("div", "razao", r.empresa.razao));
    c.append(el("div", "meta", [r.empresa.porte, r.empresa.uf, r.empresa.situacao && "situação " + r.empresa.situacao, r.empresa.matriz ? null : "filial"].filter(Boolean).join(" · ")));
  }
  c.append(el("div", "titulo", r.titulo + (r.ano_base ? " (ano-base " + r.ano_base + ")" : "")));
  if (r.detalhe) c.append(el("div", "meta", r.detalhe));
  if (r.fonte) c.append(el("div", "fonte", "Fonte: " + r.fonte));
  if (COM_ESTEIRA.includes(r.faixa)) c.append(areaEsteira(r.cnpj, pedido));
  return c;
}

function exibir(resultados, pedidos) {
  ultimos = resultados;
  $("lista").replaceChildren(...resultados.map((r) => cartao(r, (pedidos || {})[r.cnpj])));
  $("contagem").textContent = resultados.length === 1 ? "Resultado" : resultados.length + " resultados";
  $("baixar").hidden = resultados.length < 2;
  $("saida").hidden = false;
  $("saida").scrollIntoView({ behavior: "smooth", block: "start" });
  $("contagem").focus({ preventScroll: true });
}

function csv(linhas) {
  const q = (v) => '"' + String(v ?? "").replace(/"/g, '""') + '"';
  const cab = ["cnpj", "razao", "resultado", "ano_base", "fonte"];
  return "﻿" + [cab.join(";")].concat(linhas.map((r) => [formatar(r.cnpj), r.empresa?.razao, r.titulo, r.ano_base, r.fonte].map(q).join(";"))).join("\r\n");
}

// ---------- histórico ----------
let historico = [];
function quandoLegivel(q) {
  const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(String(q || ""));
  return m ? m[3] + "/" + m[2] + "/" + m[1] + " às " + m[4] + "h" + m[5] : "";
}

async function carregarHistorico() {
  try {
    const resp = await fetch("/api/esteira/historico");
    if (!resp.ok) return;
    historico = (await resp.json()).empresas || [];
  } catch (e) { return; }
  $("historico-lista").replaceChildren(...historico.map((h) => {
    const linha = el("div", "hist"), quem = el("div", "quem");
    const nome = h.razao || formatar(h.cnpj);
    quem.append(el("div", "razao", nome));
    quem.append(el("div", "meta", [formatar(h.cnpj), h.titulo, quandoLegivel(h.quando), h.pedido && "dossiê: " + andamentoTexto(h.pedido)].filter(Boolean).join(" · ")));
    const b = el("button", "botao-sec", "Abrir"); b.type = "button";
    b.setAttribute("aria-label", "Abrir a consulta de " + nome);
    b.addEventListener("click", () => {
      $("erro").hidden = true;
      exibir([h.resultado], h.pedido ? { [h.cnpj]: h.pedido } : {});
      $("uso").textContent = "Consulta guardada" + (quandoLegivel(h.quando) ? " de " + quandoLegivel(h.quando) : "") + ". Abrir de novo não gasta consulta.";
    });
    linha.append(quem, b);
    return linha;
  }));
  $("historico").hidden = !historico.length;
}

// ---------- formulário ----------
// CNPJ alfanumérico: 12 primeiros caracteres letras ou números, 2 últimos (dígitos verificadores) só números.
function limpar(v) {
  const t = v.toUpperCase().replace(/[^0-9A-Z]/g, "");
  let s = "";
  for (const ch of t) { if (s.length >= 14) break; if (s.length >= 12 && !/[0-9]/.test(ch)) continue; s += ch; }
  return s;
}

function mascara(t) {
  return t.replace(/^(.{2})(.{0,3})(.{0,3})(.{0,4})(.{0,2}).*$/, (m, a, b, c, d, e) => a + (b ? "." + b : "") + (c ? "." + c : "") + (d ? "/" + d : "") + (e ? "-" + e : ""));
}

// Reaplica a máscara sem jogar o cursor para o fim (apagar ou digitar no meio funciona).
$("cnpj").addEventListener("input", (ev) => {
  const i = ev.target, pos = i.selectionStart ?? i.value.length;
  const antes = limpar(i.value.slice(0, pos)).length;
  i.value = mascara(limpar(i.value));
  let n = 0, novo = i.value.length;
  if (antes === 0) novo = 0;
  else for (let k = 0; k < i.value.length; k++) { if (/[0-9A-Z]/.test(i.value[k])) n += 1; if (n === antes) { novo = k + 1; break; } }
  if (document.activeElement === i) i.setSelectionRange(novo, novo);
});

$("alternar").addEventListener("click", () => {
  modoVarios = !modoVarios;
  $("modo-um").hidden = modoVarios; $("modo-varios").hidden = !modoVarios;
  $("alternar").textContent = modoVarios ? "Consultar uma empresa" : "Consultar várias de uma vez";
  $("erro").hidden = true;
  $(modoVarios ? "cnpjs" : "cnpj").focus();
});

$("form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  $("erro").hidden = true; avisar("");
  const cnpjs = modoVarios ? $("cnpjs").value.split(/[\r\n,;]+/).map((s) => s.trim()).filter(Boolean) : [$("cnpj").value.trim()].filter(Boolean);
  if (!cnpjs.length) { mostrarErro(modoVarios ? "Informe ao menos um CNPJ." : "Informe o CNPJ."); (modoVarios ? $("cnpjs") : $("cnpj")).focus(); return; }
  if (cnpjs.length > 20) { mostrarErro("Informe até 20 CNPJs por vez. Você colou " + cnpjs.length + "."); return; }
  const botao = $("enviar");
  botao.disabled = true; botao.textContent = "Consultando…"; $("form").setAttribute("aria-busy", "true"); avisar("Consultando…");
  try {
    const resp = await fetch("/api/regime", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ cnpjs, faturamento: modoVarios ? "" : $("fat").value }) });
    const dados = await resp.json().catch(() => ({}));
    if (!resp.ok) throw new Error(dados.erro || "Não foi possível consultar agora. Tente de novo em instantes.");
    await carregarHistorico();
    const pedidos = Object.fromEntries(historico.filter((h) => h.pedido).map((h) => [h.cnpj, h.pedido]));
    exibir(dados.resultados, pedidos);
    $("uso").textContent = "Consultas hoje: " + dados.usadas + " de " + dados.limite + ".";
    avisar(dados.resultados.length === 1 ? "Consulta concluída." : "Consulta concluída: " + dados.resultados.length + " resultados.");
  } catch (e) {
    avisar("");
    mostrarErro(e instanceof TypeError ? "Sem conexão. Verifique a internet e tente de novo." : e.message);
  } finally {
    botao.disabled = false; botao.textContent = "Consultar"; $("form").removeAttribute("aria-busy");
  }
});

$("baixar").addEventListener("click", () => {
  const a = el("a"); a.href = URL.createObjectURL(new Blob([csv(ultimos)], { type: "text/csv;charset=utf-8" }));
  a.download = "consulta-regime.csv"; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);
});

carregarHistorico();
