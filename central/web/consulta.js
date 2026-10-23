"use strict";
const $ = (id) => document.getElementById(id);
let ultimos = [];

function formatar(c) {
  return /^[0-9A-Z]{14}$/.test(c) ? c.replace(/^(.{2})(.{3})(.{3})(.{4})(.{2})$/, "$1.$2.$3/$4-$5") : c;
}

function el(tag, classe, texto) {
  const e = document.createElement(tag);
  if (classe) e.className = classe;
  if (texto !== undefined) e.textContent = texto;
  return e;
}

function cartao(r) {
  const c = el("article", "res " + r.faixa);
  c.append(el("div", "cnpj", formatar(r.cnpj)));
  if (r.empresa) {
    c.append(el("div", "razao", r.empresa.razao));
    c.append(el("div", "meta", [r.empresa.porte, r.empresa.uf, r.empresa.situacao && "situação " + r.empresa.situacao, r.empresa.matriz ? null : "filial"].filter(Boolean).join(" · ")));
  }
  c.append(el("div", "titulo", r.titulo + (r.ano_base ? " (ano-base " + r.ano_base + ")" : "")));
  if (r.detalhe) c.append(el("div", "meta", r.detalhe));
  if (r.fonte) c.append(el("div", "fonte", "Fonte: " + r.fonte));
  if (["confirmado_real", "provavel_real", "nao_real", "sem_dado"].includes(r.faixa)) c.append(areaEsteira(r.cnpj));
  return c;
}

const BLOCOS = [["fazer", "O que você pediu"], ["precisa", "O que você também precisa"], ["falta", "O que falta e quem fornece"]];

function mostrar(area, v) {
  area.replaceChildren();
  if (v.status !== "entregue") { area.append(el("p", "meta", v.andamento + ". Volte aqui: a página atualiza sozinha.")); return; }
  const r = v.resultado;
  BLOCOS.forEach(([k, t]) => { area.append(el("div", "titulo", t)); area.append(el("p", "meta", r[k])); });
  if ((r.esteira || []).length) {
    area.append(el("div", "titulo", "Esteira"));
    const ul = el("ul", "esteira");
    r.esteira.forEach((x) => ul.append(el("li", "", "Onda " + x.onda + " · " + x.produto + " (" + x.status + ")" + (x.nota ? ": " + x.nota : ""))));
    area.append(ul);
  }
}

function acompanhar(area, id) {
  const t = setInterval(async () => {
    try {
      const v = await (await fetch("/api/esteira?id=" + encodeURIComponent(id))).json();
      mostrar(area, v);
      if (v.status === "entregue") clearInterval(t);
    } catch (e) { /* tenta de novo no próximo ciclo */ }
  }, 15000);
}

function areaEsteira(cnpj) {
  const area = el("div", "area-esteira");
  const b = el("button", "botao-sec", "Pedir análise e esteira");
  b.type = "button";
  b.addEventListener("click", async () => {
    b.disabled = true;
    try {
      const resp = await fetch("/api/esteira", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ cnpj }) });
      const v = await resp.json();
      if (!resp.ok) throw new Error(v.erro || "Não foi possível pedir a análise.");
      b.remove(); mostrar(area, v); if (v.status !== "entregue") acompanhar(area, v.id);
    } catch (e) { b.disabled = false; area.append(el("p", "erro-msg", e.message)); }
  });
  area.append(b);
  return area;
}

function csv(linhas) {
  const q = (v) => '"' + String(v ?? "").replace(/"/g, '""') + '"';
  const cab = ["cnpj", "razao", "resultado", "ano_base", "fonte"];
  return "﻿" + [cab.join(";")].concat(linhas.map((r) => [formatar(r.cnpj), r.empresa?.razao, r.titulo, r.ano_base, r.fonte].map(q).join(";"))).join("\r\n");
}

$("cnpjs").addEventListener("input", () => {
  $("campo-fat").hidden = $("cnpjs").value.trim().split(/\r?\n/).filter(Boolean).length > 1;
});

$("form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  $("erro").hidden = true;
  const cnpjs = $("cnpjs").value.split(/[\r\n,;]+/).map((s) => s.trim()).filter(Boolean);
  if (!cnpjs.length) { $("erro").textContent = "Informe ao menos um CNPJ."; $("erro").hidden = false; return; }
  $("enviar").disabled = true;
  try {
    const resp = await fetch("/api/regime", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ cnpjs, faturamento: $("fat").value }) });
    const dados = await resp.json();
    if (!resp.ok) throw new Error(dados.erro || "Não foi possível consultar.");
    ultimos = dados.resultados;
    $("lista").replaceChildren(...ultimos.map(cartao));
    $("contagem").textContent = ultimos.length === 1 ? "Resultado" : ultimos.length + " resultados";
    $("uso").textContent = "Consultas hoje: " + dados.usadas + " de " + dados.limite + ".";
    $("baixar").hidden = ultimos.length < 2;
    $("saida").hidden = false;
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
