"use strict";
const $ = (id) => document.getElementById(id);
const COM_ESTEIRA = ["confirmado_real", "provavel_real", "nao_real", "sem_dado"];
const BLOCOS = [["fazer", "O que você pediu"], ["precisa", "O que você também precisa"], ["falta", "O que falta e quem fornece"]];
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

function secao(titulo, paragrafos, itens) {
  const d = el("div", "secao");
  d.append(el("div", "titulo", titulo));
  (paragrafos || []).forEach((t) => d.append(el("p", "meta", t)));
  if ((itens || []).length) { const ul = el("ul", "esteira"); itens.forEach((t) => ul.append(el("li", "", t))); d.append(ul); }
  return d;
}

// ---------- pedido (dossiê) de uma empresa ----------
function mostrar(area, v) {
  area.replaceChildren();
  if (v.status !== "entregue") { area.append(el("p", "meta", v.andamento + ". A página atualiza sozinha.")); return; }
  const r = v.resultado;
  area.append(el("div", "selo-pronto", "Dossiê pronto"));
  if (v.arquivo) {
    const a = el("a", "botao-sec", "Baixar o dossiê em Word"); a.href = "/api/esteira/arquivo?id=" + encodeURIComponent(v.id); area.append(a);
  }
  if (v.aprofundando) area.append(el("p", "faixa-aprofundando", "Esta é a versão inicial, gerada na hora. Os agentes estão aprofundando a análise e a página atualiza quando terminar."));
  BLOCOS.forEach(([k, t]) => area.append(secao(t, [r[k]])));
  (r.dossie || []).forEach((s) => area.append(secao(s.titulo, s.paragrafos, s.itens)));
  if ((r.esteira || []).length) area.append(secao("Esteira", [], r.esteira.map((x) => "Onda " + x.onda + " · " + x.produto + " (" + x.status + ")" + (x.nota ? ": " + x.nota : ""))));
}

function acompanhar(area, id) {
  if (sondas.has(id)) clearInterval(sondas.get(id));
  let ultimo = "", tentativas = 0;
  const t = setInterval(async () => {
    tentativas += 1;
    if (!area.isConnected || tentativas > 240) { clearInterval(t); sondas.delete(id); return; }
    try {
      const resp = await fetch("/api/esteira?id=" + encodeURIComponent(id));
      if (!resp.ok) return;
      const v = await resp.json(), chave = JSON.stringify(v);
      if (chave !== ultimo) { ultimo = chave; mostrar(area, v); }
      if (v.status === "entregue" && !v.aprofundando) { clearInterval(t); sondas.delete(id); }
    } catch (e) { /* tenta de novo no próximo ciclo */ }
  }, 5000);
  sondas.set(id, t);
}

function seguir(area, v) {
  mostrar(area, v);
  if (v.status !== "entregue" || v.aprofundando) acompanhar(area, v.id);
}

function areaEsteira(cnpj, pedido) {
  const area = el("div", "area-esteira");
  if (pedido) { seguir(area, pedido); return area; }
  const b = el("button", "botao-sec", "Pedir análise e dossiê");
  b.type = "button";
  b.addEventListener("click", async () => {
    b.disabled = true; b.textContent = "Montando o dossiê…";
    try {
      const resp = await fetch("/api/esteira", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ cnpj }) });
      const v = await resp.json();
      if (!resp.ok) throw new Error(v.erro || "Não foi possível pedir a análise.");
      b.remove(); seguir(area, v); carregarHistorico();
    } catch (e) { b.disabled = false; b.textContent = "Pedir análise e dossiê"; area.append(el("p", "erro-msg", e.message)); }
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
}

function csv(linhas) {
  const q = (v) => '"' + String(v ?? "").replace(/"/g, '""') + '"';
  const cab = ["cnpj", "razao", "resultado", "ano_base", "fonte"];
  return "﻿" + [cab.join(";")].concat(linhas.map((r) => [formatar(r.cnpj), r.empresa?.razao, r.titulo, r.ano_base, r.fonte].map(q).join(";"))).join("\r\n");
}

// ---------- histórico ----------
let historico = [];
async function carregarHistorico() {
  try {
    const resp = await fetch("/api/esteira/historico");
    if (!resp.ok) return;
    historico = (await resp.json()).empresas || [];
  } catch (e) { return; }
  $("historico-lista").replaceChildren(...historico.map((h) => {
    const linha = el("div", "hist"), quem = el("div", "quem");
    quem.append(el("div", "razao", h.razao || formatar(h.cnpj)));
    quem.append(el("div", "meta", formatar(h.cnpj) + " · " + h.titulo + (h.pedido ? " · dossiê: " + h.pedido.andamento.toLowerCase() : "")));
    const b = el("button", "botao-sec", "Abrir"); b.type = "button";
    b.addEventListener("click", () => {
      exibir([h.resultado], h.pedido ? { [h.cnpj]: h.pedido } : {});
      $("uso").textContent = "Consulta guardada de " + h.quando.replace("T", " às ").slice(0, 16) + ". Não gastou consulta.";
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
    linha.append(quem, b);
    return linha;
  }));
  $("historico").hidden = !historico.length;
}

// ---------- formulário ----------
function mascara(v) {
  const t = v.toUpperCase().replace(/[^0-9A-Z]/g, "").slice(0, 14);
  return t.replace(/^(.{2})(.{0,3})(.{0,3})(.{0,4})(.{0,2}).*$/, (m, a, b, c, d, e) => a + (b ? "." + b : "") + (c ? "." + c : "") + (d ? "/" + d : "") + (e ? "-" + e : ""));
}

$("cnpj").addEventListener("input", (ev) => { ev.target.value = mascara(ev.target.value); });
$("alternar").addEventListener("click", () => {
  modoVarios = !modoVarios;
  $("modo-um").hidden = modoVarios; $("modo-varios").hidden = !modoVarios;
  $("alternar").textContent = modoVarios ? "Consultar uma empresa" : "Consultar várias de uma vez";
});

$("form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  $("erro").hidden = true;
  const cnpjs = modoVarios ? $("cnpjs").value.split(/[\r\n,;]+/).map((s) => s.trim()).filter(Boolean) : [$("cnpj").value.trim()].filter(Boolean);
  if (!cnpjs.length) { $("erro").textContent = "Informe o CNPJ."; $("erro").hidden = false; return; }
  $("enviar").disabled = true;
  try {
    const resp = await fetch("/api/regime", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ cnpjs, faturamento: modoVarios ? "" : $("fat").value }) });
    const dados = await resp.json();
    if (!resp.ok) throw new Error(dados.erro || "Não foi possível consultar.");
    await carregarHistorico();
    const pedidos = Object.fromEntries(historico.filter((h) => h.pedido).map((h) => [h.cnpj, h.pedido]));
    exibir(dados.resultados, pedidos);
    $("uso").textContent = "Consultas hoje: " + dados.usadas + " de " + dados.limite + ".";
  } catch (e) {
    $("erro").textContent = e.message; $("erro").hidden = false;
  } finally {
    $("enviar").disabled = false;
  }
});

$("baixar").addEventListener("click", () => {
  const a = el("a"); a.href = URL.createObjectURL(new Blob([csv(ultimos)], { type: "text/csv;charset=utf-8" }));
  a.download = "consulta-regime.csv"; a.click(); URL.revokeObjectURL(a.href);
});

carregarHistorico();
