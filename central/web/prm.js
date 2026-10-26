// PRM Save v2 · as duas faces do mesmo site (05-design.md): parceiro (claro, barra inferior) e Save (escuro, seção Canal).
// Sem biblioteca além do MSAL. Todo conteúdo entra por textContent (nunca innerHTML com dado). Quem decide acesso é a API.
// Login: em produção, MSAL (Entra). No servidor local, seletor de usuário de teste — só quando /api/prm/dev/usuarios
// responde, o que a API só faz no servidor de teste (localhost ou o próprio Codespace) com PRM_LOGIN_SIMULADO=1 e fora da Azure.
(function () {
  "use strict";

  // ------------------------------------------------------------------ utilitários de DOM
  const SVGNS = "http://www.w3.org/2000/svg";
  function h(tag, a, ...kids) {
    const e = document.createElement(tag);
    if (a) {
      for (const [k, v] of Object.entries(a)) {
        if (v === null || v === undefined || v === false) continue;
        if (k === "class") e.className = v;
        else if (k === "text") e.textContent = v;
        else if (k.startsWith("on") && typeof v === "function") e.addEventListener(k.slice(2), v);
        else if (k === "estilo") for (const [p, val] of Object.entries(v)) e.style.setProperty(p, val);
        else if (k === "valor") e.value = v;
        else if (v === true) e.setAttribute(k, "");
        else e.setAttribute(k, String(v));
      }
    }
    for (const k of kids.flat(Infinity)) {
      if (k === null || k === undefined || k === false) continue;
      e.append(k instanceof Node ? k : document.createTextNode(String(k)));
    }
    return e;
  }
  const ICONES = {
    inicio: ["M3 10.5 12 3l9 7.5", "M5 9.5V21h5v-6h4v6h5V9.5"],
    empresas: ["M3 21h18", "M5 21V7l7-4v18", "M19 21V11l-7-4", "M9 9h.01", "M9 13h.01", "M9 17h.01"],
    registrar: ["M12 5v14", "M5 12h14"],
    pedidos: ["M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"],
    extrato: ["M4 2v20l3-2 3 2 3-2 3 2 3-2 1 1V2l-1 1-3-2-3 2-3-2-3 2-3-2z", "M8 8h8", "M8 12h8", "M8 16h5"],
    sino: ["M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9", "M10.3 21a1.94 1.94 0 0 0 3.4 0"],
    usuario: ["M20 21a8 8 0 0 0-16 0", "M12 13a5 5 0 1 0 0-10 5 5 0 0 0 0 10z"],
    canal: ["M3 3v18h18", "M7 15l4-4 3 3 5-6"],
    lista: ["M8 6h13", "M8 12h13", "M8 18h13", "M3 6h.01", "M3 12h.01", "M3 18h.01"],
    alerta: ["M12 9v4", "M12 17h.01", "M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"],
    info: ["M12 16v-4", "M12 8h.01", "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z"],
    fechar: ["M18 6 6 18", "M6 6l12 12"],
    mais: ["M4 6h16", "M4 12h16", "M4 18h16"],
    livro: ["M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5v14z", "M20 17v4H6.5"],
    nivel: ["M12 15a6 6 0 1 0 0-12 6 6 0 0 0 0 12z", "M8.2 13.9 7 22l5-3 5 3-1.2-8.1"],
    chave: ["M15 7a4 4 0 1 1-4 4", "M11 11 3 19v2h3l1-1v-2h2v-2h2l1-1"],
    funil: ["M3 4h18", "M6 9h12", "M9 14h6", "M11 19h2"],
  };
  function icone(nome) {
    const s = document.createElementNS(SVGNS, "svg");
    s.setAttribute("viewBox", "0 0 24 24"); s.setAttribute("fill", "none"); s.setAttribute("stroke", "currentColor");
    s.setAttribute("stroke-width", "1.75"); s.setAttribute("stroke-linecap", "round"); s.setAttribute("stroke-linejoin", "round");
    s.setAttribute("aria-hidden", "true"); s.setAttribute("focusable", "false"); s.setAttribute("width", "20"); s.setAttribute("height", "20");
    for (const d of ICONES[nome] || []) { const p = document.createElementNS(SVGNS, "path"); p.setAttribute("d", d); s.append(p); }
    return s;
  }
  const chip = (texto, tipo) => h("span", { class: "prm-chip prm-chip--" + (tipo || "info") }, texto);
  const rotulo = (t) => h("span", { class: "prm-rotulo prm-rotulo--marca" }, t);
  const apoio = (t) => h("p", { class: "prm-texto-apoio" }, t);
  const limpar = (el) => { while (el.firstChild) el.firstChild.remove(); return el; };
  const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };
  const normCnpj = (s) => String(s || "").toUpperCase().replace(/[^0-9A-Z]/g, "");
  const celular = () => window.matchMedia("(max-width: 767px)").matches;
  let seq = 0;
  const uid = (p) => (p || "c") + "-" + (++seq);

  function anunciar(t) {
    const r = document.getElementById("anuncio");
    r.textContent = "";
    setTimeout(() => { r.textContent = t; }, 60);
  }

  function toast(titulo, texto, tipo, acao) {
    const area = document.getElementById("toasts");
    limpar(area);
    const t = h("div", { class: "prm-toast prm-toast--" + (tipo || "ok") },
      icone(tipo === "atencao" ? "alerta" : "info"),
      h("div", null, h("div", { class: "prm-toast__titulo" }, titulo), texto ? h("div", null, texto) : null),
      acao ? h("button", { class: "prm-btn prm-btn--texto prm-toast__acao", type: "button", onclick: () => { acao.fn(); t.remove(); } }, acao.rotulo) : null);
    area.append(t);
    let tempo = acao ? 8000 : 5000, timer = setTimeout(() => t.remove(), tempo);
    const pausa = () => clearTimeout(timer), segue = () => { timer = setTimeout(() => t.remove(), 2500); };
    t.addEventListener("mouseenter", pausa); t.addEventListener("mouseleave", segue);
    t.addEventListener("focusin", pausa); t.addEventListener("focusout", segue);
  }

  // modal de confirmação: foco preso, Esc cancela, foco volta a quem abriu (05 §4.2)
  function modal({ titulo, texto, corpo, verbo, perigo, cancelar = "Cancelar", aoConfirmar, soFechar }) {
    return new Promise((resolve) => {
      const antes = document.activeElement;
      const id = uid("modal");
      const erro = h("div", { class: "prm-aviso prm-aviso--erro", role: "alert", hidden: true });
      const ok = soFechar ? null : h("button", { class: "prm-btn" + (perigo ? " prm-btn--perigo" : ""), type: "button" }, verbo || "Confirmar");
      const fechar = (v) => { veu.remove(); caixa.remove(); document.removeEventListener("keydown", tecla, true); if (antes && antes.focus) antes.focus(); resolve(v); };
      const nao = h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => fechar(false) }, soFechar ? "Fechar" : cancelar);
      const caixa = h("div", { class: "prm-modal", role: "dialog", "aria-modal": "true", "aria-labelledby": id },
        h("h2", { id, tabindex: "-1" }, titulo), texto ? h("p", null, texto) : null, corpo || null, erro,
        h("div", { class: "prm-acoes prm-acoes--empilha prm-modal__acoes" }, nao, ok));
      const veu = h("div", { class: "prm-veu", onclick: () => fechar(false) });
      function tecla(e) {
        if (e.key === "Escape") { e.preventDefault(); fechar(false); }
        if (e.key === "Tab") {
          const f = [...caixa.querySelectorAll("button, input, select, textarea, a[href], [tabindex='0']")].filter((x) => !x.disabled && !x.hidden);
          if (!f.length) return;
          if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
          else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
        }
      }
      if (ok) ok.addEventListener("click", async () => {
        ok.setAttribute("aria-busy", "true"); ok.disabled = true;
        try { const r = aoConfirmar ? await aoConfirmar() : true; if (r !== false) fechar(r === undefined ? true : r); }
        catch (e) { erro.hidden = false; erro.textContent = e.message || "Não conseguimos concluir agora. Tente de novo em instantes."; }
        finally { ok.removeAttribute("aria-busy"); ok.disabled = false; }
      });
      document.addEventListener("keydown", tecla, true);
      document.body.append(veu, caixa);
      const primeiro = caixa.querySelector("input, select, textarea");
      (primeiro || caixa.querySelector("h2")).focus();
    });
  }

  // ------------------------------------------------------------------ sessão e API
  const S = { modo: null, dev: null, eu: null, msal: null, conta: null, inicio: null, cnpjsTeste: [], usuariosTeste: [] };
  const C = window.CENTRAL_CONFIG;

  async function token() {
    const pedido = { scopes: [C.prmScope || C.apiScope], account: S.conta };
    try { return (await S.msal.acquireTokenSilent(pedido)).accessToken; }
    catch (e) {
      if (e instanceof window.msal.InteractionRequiredAuthError) { await S.msal.acquireTokenRedirect(pedido); return null; }
      throw e;
    }
  }

  async function api(metodo, caminho, corpo, bruto) {
    const cab = { Accept: "application/json" };
    if (corpo !== undefined) cab["Content-Type"] = "application/json";
    if (S.modo === "dev" && S.dev) cab["X-PRM-Dev-Usuario"] = S.dev;
    if (S.modo === "msal") { const t = await token(); if (!t) return { st: 0, o: {} }; cab.Authorization = "Bearer " + t; }
    let r;
    try { r = await fetch((C && C.apiBase ? C.apiBase : "/api") + "/prm/" + caminho, { method: metodo, headers: cab, body: corpo !== undefined ? JSON.stringify(corpo) : undefined, cache: "no-store" }); }
    catch (e) { return { st: 0, o: { erro: "Sem conexão. Confira a internet e tente de novo." } }; }
    if (bruto) return { st: r.status, r };
    let o = {};
    try { o = await r.json(); } catch (e) { o = {}; }
    if (r.status === 401) { telaSessao(); }
    if (r.status === 428) { S.eu.termos_pendentes = true; telaBoasVindas(); }
    return { st: r.status, o };
  }

  // ------------------------------------------------------------------ casca (topo, menu, barra inferior)
  const MENU_P = [
    ["inicio", "Início", "inicio", (c) => c.pedem_voce],
    ["negocios", "Negócios", "funil", (c) => c.precisa],
    ["registrar", "Registrar", "registrar", null],
    ["pedidos", "Pedidos", "pedidos", (c) => c.respostas],
    ["extrato", "Extrato", "extrato", (c) => c.nf],
  ];
  const MAIS_P = [["empresas", "Empresas e registros", "empresas"], ["nivel", "Nível e jornada", "nivel"], ["biblioteca", "Biblioteca e Academia", "livro"], ["ajuda", "Ajuda e glossário", "info"]];
  const MENU_S = [
    ["canal", "Visão do canal", "canal"], ["canal/dashboard", "Dashboard comercial", "funil"], ["canal/negocios", "Negócios", "empresas"], ["canal/registros", "Registros", "lista"], ["canal/conflitos", "Conflitos", "alerta"],
    ["canal/demandas", "Demandas", "pedidos"], ["canal/extratos", "Extratos", "extrato"], ["canal/dossies", "Dossiês e esteira", "livro"],
    ["canal/acessos", "Acessos", "chave"], ["canal/niveis", "Níveis (em teste)", "nivel"], ["canal/parametros", "Parâmetros", "lista"],
  ];
  const contadores = () => {
    const c = (S.inicio && S.inicio.kpis) || {};
    return { pedem_voce: c.pedem_voce || 0, precisa: S.inicio ? (S.inicio.precisa_empresas || 0) : 0, respostas: c.respostas_novas || 0, nf: (S.inicio && S.inicio.nf_pendentes) || 0 };
  };
  const contador = (n, nome) => (n ? h("span", { class: "prm-contador", "aria-hidden": "true" }, n > 99 ? "99+" : String(n)) : null);
  const nomeComContador = (nome, n, oque) => (n ? nome + ", " + n + " " + oque : nome);

  function casca(rotaAtual) {
    const save = S.eu.face === "save";
    document.documentElement.classList.toggle("escuro", save);
    const app = limpar(document.getElementById("app"));
    app.removeAttribute("aria-busy");
    const logo = h("img", { src: save ? "logo-save-fundo-escuro.png" : "logo-save-fundo-claro.png", alt: "Save Co.", class: "prm-topo__logo" });
    const naoLidos = S.eu.avisos_nao_lidos || 0;
    const sino = h("button", { class: "prm-icbtn", type: "button", "aria-label": nomeComContador("Avisos", naoLidos, "não lidos"), onclick: abrirAvisos }, icone("sino"), contador(naoLidos));
    const conta = h("button", { class: "prm-icbtn prm-icbtn--texto", type: "button", "aria-haspopup": "dialog", onclick: menuConta },
      icone("usuario"), h("span", { class: "prm-so-desktop" }, S.eu.nome || "Conta"));
    const topo = h("header", { class: "prm-topo" }, h("a", { href: save ? "#/canal" : "#/inicio", class: "prm-topo__marca" }, logo),
      h("div", { class: "prm-topo__acoes" }, sino, conta));
    const ativa = (k) => rotaAtual === k || rotaAtual.startsWith(k + "/");
    const cont = contadores();
    let menu;
    if (save) {
      menu = h("nav", { class: "prm-menu", "aria-label": "Canal" }, h("div", { class: "prm-menu__grupo" }, rotulo("Canal")),
        MENU_S.map(([k, n, ic]) => h("a", { class: "prm-menu__item", href: "#/" + k, "aria-current": (k === "canal" ? rotaAtual === "canal" : ativa(k)) ? "page" : null }, icone(ic), n)),
        h("div", { class: "prm-menu__rodape" }, "Perfil: " + S.eu.papel));
    } else {
      menu = h("nav", { class: "prm-menu", "aria-label": "Principal" },
        h("a", { class: "prm-btn prm-menu__principal", href: "#/registrar" }, icone("registrar"), "Registrar oportunidade"),
        MENU_P.filter((m) => m[0] !== "registrar").map(([k, n, ic, f]) => h("a", { class: "prm-menu__item", href: "#/" + k, "aria-current": ativa(k) ? "page" : null,
          "aria-label": f ? nomeComContador(n, f(cont), k === "negocios" ? "pedem você" : k === "pedidos" ? "respostas novas" : k === "extrato" ? "pedem NF" : "pendências") : null },
          icone(ic), n, f ? contador(f(cont)) : null)),
        h("div", { class: "prm-menu__grupo" }, rotulo("Programa")),
        MAIS_P.map(([k, n, ic]) => h("a", { class: "prm-menu__item", href: "#/" + k, "aria-current": ativa(k) ? "page" : null }, icone(ic), n)),
        h("div", { class: "prm-menu__rodape" }, S.eu.escritorio || ""));
    }
    const main = h("main", { class: "prm-main", id: "conteudo", tabindex: "-1" });
    const corpo = h("div", null, main);
    const casca_ = h("div", { class: "prm-casca" }, menu, h("div", { class: "prm-coluna" }, topo, corpo));
    app.append(casca_);
    if (save) {  // celular: barra inferior da Save (05 §2.2), o resto do menu em "Mais"
      app.append(h("nav", { class: "prm-nav-m", "aria-label": "Navegação" }, [["canal", "Canal", "canal"], ["canal/registros", "Registros", "lista"], ["canal/demandas", "Demandas", "pedidos"],
        ["canal/extratos", "Extratos", "extrato"], ["canal/mais", "Mais", "mais"]].map(([k, n, ic]) => h("a", { class: "prm-nav-m__item", href: "#/" + k,
          "aria-current": (k === "canal" ? rotaAtual === "canal" : ativa(k)) ? "page" : null }, icone(ic), n))));
    }
    if (!save) {
      app.append(h("nav", { class: "prm-nav-m", "aria-label": "Navegação" }, MENU_P.map(([k, n, ic, f]) => k === "registrar"
        ? h("a", { class: "prm-nav-m__acao", href: "#/registrar", "aria-current": ativa(k) ? "page" : null }, icone(ic), n)
        : h("a", { class: "prm-nav-m__item", href: "#/" + k, "aria-current": ativa(k) ? "page" : null,
          "aria-label": f && f(cont) ? nomeComContador(n, f(cont), "pendências") : null }, icone(ic), n, f ? contador(f(cont)) : null))));
    }
    return main;
  }

  function cab(main, titulo, texto, acoes, rot) {
    document.title = titulo + " · PRM Save";
    const h1 = h("h1", { tabindex: "-1" }, titulo);
    main.append(h("div", { class: "prm-cab" }, h("div", null, rot ? rotulo(rot) : null, h1, texto ? h("p", null, texto) : null), acoes ? h("div", { class: "prm-acoes" }, acoes) : null));
    return h1;
  }

  function carregando(main, n) {
    main.setAttribute("aria-busy", "true");
    main.append(h("div", { class: "prm-pilha", "aria-hidden": "true" }, h("span", { class: "prm-esqueleto prm-esqueleto--titulo" }),
      [...Array(n || 3)].map(() => h("span", { class: "prm-esqueleto prm-esqueleto--cartao" }))));
  }
  const pronto = (main) => { main.removeAttribute("aria-busy"); limpar(main); };

  function erroBloco(main, o, st, tentar) {
    pronto(main);
    if (st === 403) {
      main.append(cab_(main, "Sem acesso"), h("div", { class: "prm-aviso prm-aviso--info" }, icone("info"), h("div", null, (o && o.erro) || "Esta tela é de outro perfil.")));
      return;
    }
    main.append(h("div", { class: "prm-aviso prm-aviso--erro", role: "alert" }, icone("alerta"),
      h("div", { class: "prm-pilha--peq" }, (o && o.erro) || "Não conseguimos carregar esta parte agora. Tente de novo em instantes.",
        tentar ? h("div", null, h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: tentar }, "Tentar de novo")) : null)));
  }
  const cab_ = (main, t) => { document.title = t + " · PRM Save"; return h("div", { class: "prm-cab" }, h("h1", { tabindex: "-1" }, t)); };

  async function carregar(main, caminho, desenhar, n) {
    carregando(main, n);
    const { st, o } = await api("GET", caminho);
    if (st === 401 || st === 428) return;
    if (st !== 200) return erroBloco(main, o, st, () => { limpar(main); carregar(main, caminho, desenhar, n); });
    pronto(main);
    desenhar(o);
  }

  // ------------------------------------------------------------------ campos de formulário acessíveis
  function campo({ id, rotulo: r, tipo = "text", dica, opcional, opcoes, valor, atributos, mono, area }) {
    id = id || uid("campo");
    const idDica = dica ? id + "-dica" : null, idMsg = id + "-msg";
    let entrada;
    const base = Object.assign({ id, name: id, class: "prm-campo__entrada" + (mono ? " prm-campo__entrada--mono" : ""), "aria-describedby": [idDica, idMsg].filter(Boolean).join(" ") }, atributos || {});
    if (opcoes) {
      entrada = h("select", base, h("option", { value: "" }, "Escolha"), opcoes.map(([v, t]) => h("option", { value: v, selected: v === valor ? true : null }, t)));
    } else if (area) {
      entrada = h("textarea", base);
      if (valor) entrada.value = valor;
    } else {
      entrada = h("input", Object.assign({ type: tipo }, base));
      if (valor) entrada.value = valor;
    }
    const msg = h("p", { class: "prm-campo__msg", id: idMsg, "aria-live": "polite", hidden: true });
    const el = h("div", { class: "prm-campo" }, h("label", { class: "prm-campo__rotulo", for: id }, r, opcional ? h("span", { class: "prm-campo__opcional" }, " (opcional)") : null),
      dica ? h("p", { class: "prm-campo__dica", id: idDica }, dica) : null, entrada, msg);
    el.entrada = entrada;
    el.estado = (estado, texto) => {
      el.dataset.estado = estado || "";
      if (estado === "erro") entrada.setAttribute("aria-invalid", "true"); else entrada.removeAttribute("aria-invalid");
      msg.hidden = !texto; msg.textContent = texto || "";
    };
    return el;
  }
  const checkbox = (id, texto) => { const i = h("input", { type: "checkbox", id }); const l = h("label", { class: "prm-check", for: id }, i, h("span", null, texto)); l.entrada = i; return l; };

  function aplicarErros(campos, erros) {
    let primeiro = null;
    for (const [k, c] of Object.entries(campos)) {
      if (erros && erros[k]) { c.estado("erro", erros[k]); primeiro = primeiro || c; }
      else if (c.estado) c.estado(c.dataset.estado === "ok" ? "ok" : "", c.dataset.estado === "ok" ? c.querySelector(".prm-campo__msg").textContent : "");
    }
    if (primeiro) primeiro.entrada.focus();
    return !!primeiro;
  }

  // ------------------------------------------------------------------ rotas
  const ROTAS_P = [
    [/^inicio$/, vInicio], [/^registrar$/, vRegistrar], [/^empresas$/, vEmpresas], [/^empresas\/([0-9a-f]{16})$/, vFicha],
    [/^negocios$/, vNegocios], [/^negocios\/([0-9a-f]{16})$/, vNegocio],
    [/^pedidos$/, vPedidos], [/^pedidos\/novo$/, vNovoPedido], [/^pedidos\/([0-9a-f]{16})$/, vPedido], [/^extrato$/, vExtrato],
    [/^avisos$/, vAvisosTela], [/^nivel$/, vNivel], [/^biblioteca$/, vBiblioteca], [/^ajuda$/, vAjuda], [/^mais$/, vMais],
  ];
  const ROTAS_S = [
    [/^canal$/, sCanal], [/^canal\/dashboard$/, sDashboard], [/^canal\/negocios$/, sNegocios], [/^canal\/negocios\/(\d{1,20})$/, sNegocio], [/^canal\/registros$/, sRegistros], [/^canal\/registros\/(R-\d{4}-\d{6})$/, sRegistros], [/^canal\/conflitos$/, sConflitos],
    [/^canal\/demandas$/, sDemandas], [/^canal\/demandas\/(D-\d{4}-\d{4})$/, sDemandas], [/^canal\/extratos$/, sExtratos], [/^canal\/dossies$/, sDossies],
    [/^canal\/acessos$/, sAcessos], [/^canal\/niveis$/, sNiveis], [/^canal\/parametros$/, sParametros], [/^avisos$/, vAvisosTela], [/^canal\/mais$/, sMais],
  ];

  function rota() {
    const bruto = (location.hash || "").replace(/^#\/?/, "");
    const [caminho, q] = bruto.split("?");
    return { caminho: caminho || (S.eu.face === "save" ? "canal" : "inicio"), params: new URLSearchParams(q || "") };
  }

  let primeira = true;
  async function navegar() {
    if (!S.eu) return;
    if (S.eu.face === "parceiro" && S.eu.termos_pendentes) return telaBoasVindas();
    const { caminho, params } = rota();
    const tabela = S.eu.face === "save" ? ROTAS_S : ROTAS_P;
    const achou = tabela.find(([rx]) => rx.test(caminho));
    const main = casca(caminho);
    if (!achou) { main.append(cab_(main, "Página não encontrada"), apoio("Este endereço não existe no portal.")); return; }
    const m = caminho.match(achou[0]);
    await achou[1](main, m[1], params);
    if (!primeira) { const atual = document.getElementById("conteudo"); const t = atual && atual.querySelector("h1"); if (t) t.focus(); window.scrollTo(0, 0); }
    primeira = false;
  }
  window.addEventListener("hashchange", navegar);

  // ------------------------------------------------------------------ telas de sessão
  function telaSimples(titulo, texto, botoes) {
    document.documentElement.classList.remove("escuro");
    const app = limpar(document.getElementById("app"));
    app.removeAttribute("aria-busy");
    document.title = titulo + " · PRM Save";
    app.append(h("main", { class: "prm-login", id: "conteudo", tabindex: "-1" }, h("img", { src: "logo-save-fundo-claro.png", alt: "Save Co.", class: "prm-topo__logo" }),
      h("div", { class: "prm-cartao prm-pilha--peq" }, h("h1", { class: "prm-titulo-secao" }, titulo), h("p", null, texto), h("div", { class: "prm-acoes" }, botoes || []))));
  }
  function telaSessao() {
    telaSimples("Sessão encerrada", "Sua sessão terminou por segurança. Entre de novo para continuar de onde parou.",
      [h("button", { class: "prm-btn", type: "button", onclick: () => { if (S.modo === "dev") { sessionStorage.removeItem("prm-dev"); location.reload(); } else S.msal.loginRedirect({ scopes: [C.prmScope || C.apiScope] }); } },
        S.modo === "dev" ? "Escolher usuário de teste" : "Entrar com a Microsoft")]);
  }
  function sair() {
    if (S.modo === "dev") { sessionStorage.removeItem("prm-dev"); location.hash = ""; location.reload(); return; }
    S.msal.logoutRedirect({ account: S.conta });
  }

  function telaLoginTeste() {
    const app = limpar(document.getElementById("app"));
    app.removeAttribute("aria-busy");
    document.title = "Entrar (teste local) · PRM Save";
    const escolher = (u) => { sessionStorage.setItem("prm-dev", u.id); S.dev = u.id; location.hash = u.face === "save" ? "#/canal" : "#/inicio"; iniciarSessao(); };
    app.append(h("main", { class: "prm-login", id: "conteudo", tabindex: "-1" },
      h("img", { src: "logo-save-fundo-claro.png", alt: "Save Co.", class: "prm-topo__logo" }),
      h("div", { class: "prm-aviso prm-aviso--atencao" }, icone("alerta"), h("div", null, "Servidor de teste, com dados fictícios. Este seletor só existe no servidor de teste (no computador ou no Codespace do time); em produção o login é pela conta Microsoft (Entra).")),
      h("div", { class: "prm-pilha--peq" }, h("h1", { class: "prm-titulo-secao" }, "Entrar como"),
        h("div", { class: "prm-login__opcoes" }, S.usuariosTeste.map((u) => h("button", { class: "prm-login__opcao", type: "button", onclick: () => escolher(u) },
          h("strong", null, u.nome), h("span", { class: "prm-texto-apoio" }, u.face === "save" ? "Save · " + u.papel : (u.escritorio || "") + " · " + u.papel))))),
      S.cnpjsTeste.length ? h("div", { class: "prm-cartao prm-pilha--peq" }, h("h2", { class: "prm-titulo-secao" }, "CNPJs de teste (fictícios)"),
        h("table", { class: "prm-tabela-simples" }, h("caption", { class: "prm-so-leitor" }, "CNPJs de teste e o que acontece com cada um"),
          h("thead", null, h("tr", null, h("th", { scope: "col" }, "CNPJ"), h("th", { scope: "col" }, "Cenário"))),
          h("tbody", null, S.cnpjsTeste.map((c) => h("tr", null, h("td", { class: "prm-mono" }, c.cnpj), h("td", null, c.cenario)))))) : null));
  }

  function telaBoasVindas() {
    const app = limpar(document.getElementById("app"));
    document.documentElement.classList.remove("escuro");
    app.removeAttribute("aria-busy");
    document.title = "Boas-vindas · PRM Save";
    const aceite = checkbox("aceite", "Li e aceito os Termos de Uso e o Aviso de Privacidade do portal.");
    const erro = h("p", { class: "prm-campo__msg", "aria-live": "polite", id: "aceite-msg" });
    const bloco = (ic, t, x) => h("div", { class: "prm-cartao prm-pilha--peq" }, icone(ic), h("h2", { class: "prm-titulo-secao" }, t), h("p", null, x));
    const btn = h("button", { class: "prm-btn", type: "button" }, "Começar");
    btn.addEventListener("click", async () => {
      if (!aceite.entrada.checked) { erro.textContent = "Marque o aceite para continuar."; aceite.entrada.focus(); return; }
      btn.setAttribute("aria-busy", "true");
      const { st, o } = await api("POST", "parceiro/termos/aceitar", { versao: S.eu.versao_termos, aceito: true });
      btn.removeAttribute("aria-busy");
      if (st !== 200) { erro.textContent = o.erro || "Não conseguimos registrar o aceite agora. Tente de novo."; return; }
      S.eu.termos_pendentes = false; location.hash = "#/inicio"; navegar();
    });
    const h1 = h("h1", { tabindex: "-1" }, "Bem-vindo ao portal de parceiros da Save, " + (S.eu.nome || "") + ".");
    app.append(h("main", { class: "prm-login", id: "conteudo", tabindex: "-1" }, h("img", { src: "logo-save-fundo-claro.png", alt: "Save Co.", class: "prm-topo__logo" }), h1,
      h("div", { class: "prm-grade prm-grade--3" },
        bloco("registrar", "Registre", "Registre a empresa antes de começar a conversa. A data e a hora ficam guardadas."),
        bloco("empresas", "Acompanhe", "Veja em que etapa está cada empresa e o que falta de você."),
        bloco("pedidos", "Peça", "Pergunte à Save por aqui; a resposta fica guardada junto da empresa.")),
      h("div", { class: "prm-cartao prm-pilha--peq" }, h("p", null, "Versão dos termos: " + (S.eu.versao_termos || "")),
        apoio("Os textos completos dos Termos de Uso e do Aviso de Privacidade estão em validação pelo Jurídico e aparecem aqui na versão final."),
        aceite, erro, h("div", null, btn))));
    h1.focus();
  }

  function menuConta() {
    const itens = [];
    if (S.eu.face === "parceiro") MAIS_P.forEach(([k, n]) => itens.push(h("a", { class: "prm-menu__item", href: "#/" + k }, n)));
    if (S.modo === "dev") itens.push(h("button", { class: "prm-menu__item", type: "button", onclick: () => { sessionStorage.removeItem("prm-dev"); location.hash = ""; location.reload(); } }, "Trocar usuário de teste"));
    itens.push(h("button", { class: "prm-menu__item", type: "button", onclick: sair }, "Sair"));
    modal({ titulo: S.eu.nome || "Conta", texto: S.eu.face === "save" ? "Perfil: " + S.eu.papel : (S.eu.escritorio || "") + " · " + S.eu.papel,
      corpo: h("nav", { "aria-label": "Conta", class: "prm-pilha--peq" }, itens), soFechar: true });
    document.querySelectorAll(".prm-modal a").forEach((a) => a.addEventListener("click", () => { document.querySelector(".prm-veu").click(); }));
  }

  // ------------------------------------------------------------------ avisos (gaveta no desktop, tela no celular)
  const FILTROS_AVISO = [["", "Todos"], ["pede_voce", "Pede você"], ["resposta", "Respostas"], ["empresa", "Empresas"], ["extrato", "Extrato"], ["programa", "Programa"]];
  function listaAvisos(itens, filtro, aoAbrir) {
    const xs = itens.filter((n) => !filtro || n.tipo === filtro);
    if (!xs.length) return h("div", { class: "prm-vazio" }, h("p", null, "Nenhum aviso por enquanto."));
    const hoje = new Date().toDateString();
    const grupos = {};
    xs.forEach((n) => { const d = new Date(n.quando); const g = d.toDateString() === hoje ? "Hoje" : (Date.now() - d) < 7 * 864e5 ? "Esta semana" : "Antes"; (grupos[g] = grupos[g] || []).push(n); });
    return ["Hoje", "Esta semana", "Antes"].filter((g) => grupos[g]).map((g) => h("div", null, h("div", { class: "prm-aviso-grupo" }, rotulo(g)),
      grupos[g].map((n) => h("a", { class: "prm-aviso-item", href: "#/" + (n.go || ""), "data-lido": String(n.lido), onclick: () => aoAbrir(n) },
        h("div", null, h("div", { class: "prm-aviso-item__titulo" }, n.titulo), h("div", { class: "prm-aviso-item__texto" }, n.texto),
          h("div", { class: "prm-aviso-item__quando" }, new Date(n.quando).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" })))))));
  }
  const rotaAvisos = () => (S.eu.face === "save" ? "save/avisos" : "parceiro/avisos");
  const marcar = (ids) => api("POST", rotaAvisos() + "/lidos", ids ? { ids } : {});

  async function abrirAvisos() {
    if (celular()) { location.hash = "#/avisos"; return; }
    const antes = document.activeElement;
    const { st, o } = await api("GET", rotaAvisos());
    if (st !== 200) return toast("Avisos", "Não conseguimos carregar os avisos agora.", "atencao");
    let filtro = "";
    const corpo = h("div", { class: "prm-gaveta__corpo" });
    const filtros = h("div", { class: "prm-filtros", role: "group", "aria-label": "Filtrar avisos" });
    const desenhar = () => { limpar(corpo).append(...[].concat(listaAvisos(o.itens, filtro, (n) => { marcar([n.id]); fechar(); }))); };
    FILTROS_AVISO.forEach(([k, n]) => filtros.append(h("button", { class: "prm-filtro", type: "button", "aria-pressed": String(k === filtro), onclick: (e) => {
      filtro = k; filtros.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", "false")); e.currentTarget.setAttribute("aria-pressed", "true"); desenhar(); } }, n)));
    const id = uid("gaveta");
    const fecharBtn = h("button", { class: "prm-icbtn", type: "button", "aria-label": "Fechar avisos", onclick: () => fechar() }, icone("fechar"));
    const gaveta = h("div", { class: "prm-gaveta", role: "dialog", "aria-modal": "true", "aria-labelledby": id },
      h("div", { class: "prm-gaveta__cab" }, h("h2", { id }, "Avisos"), fecharBtn), filtros, corpo,
      h("div", { class: "prm-gaveta__rodape" }, h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: async () => { await marcar(); S.eu.avisos_nao_lidos = 0; fechar(); navegar(); } }, "Marcar todos como lidos")));
    const veu = h("div", { class: "prm-veu", onclick: () => fechar() });
    function tecla(e) { if (e.key === "Escape") fechar(); }
    function fechar() { veu.remove(); gaveta.remove(); document.removeEventListener("keydown", tecla); if (antes) antes.focus(); }
    document.addEventListener("keydown", tecla);
    desenhar();
    document.body.append(veu, gaveta);
    fecharBtn.focus();
  }

  async function vAvisosTela(main) {
    await carregar(main, rotaAvisos(), (o) => {
      cab(main, "Avisos", null, [h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: async () => { await marcar(); S.eu.avisos_nao_lidos = 0; navegar(); } }, "Marcar todos como lidos")]);
      let filtro = "";
      const lista = h("div");
      const filtros = h("div", { class: "prm-filtros", role: "group", "aria-label": "Filtrar avisos" });
      const desenhar = () => limpar(lista).append(...[].concat(listaAvisos(o.itens, filtro, (n) => marcar([n.id]))));
      FILTROS_AVISO.forEach(([k, n]) => filtros.append(h("button", { class: "prm-filtro", type: "button", "aria-pressed": String(!k), onclick: (e) => {
        filtro = k; filtros.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", "false")); e.currentTarget.setAttribute("aria-pressed", "true"); desenhar(); } }, n)));
      main.append(filtros, lista); desenhar();
    });
  }

  // ================================================================== FACE DO PARCEIRO
  function abasInicio(main, atual) {
    main.append(h("nav", { class: "prm-abas", "aria-label": "Início" }, [["resumo", "Resumo", "#/inicio"], ["painel", "Painel de vendas", "#/inicio?aba=painel"]].map(([k, n, go]) =>
      h("a", { class: "prm-aba", href: go, "aria-current": k === atual ? "page" : null }, n))));
  }

  async function vInicio(main, _x, params) {
    if (params && params.get("aba") === "painel") {
      cab(main, "Painel de vendas", "Pipeline, conversão e resultados do seu escritório.");
      abasInicio(main, "painel");
      painelParceiro(main, params);
      return;
    }
    await carregar(main, "parceiro/inicio", (o) => {
      S.inicio = o;
      casca("inicio");  // contadores atualizados
      main = document.getElementById("conteudo");
      cab(main, "Olá, " + (o.nome || ""), null);
      abasInicio(main, "resumo");
      if (!o.kpis.empresas && !o.pede_voce.length) {
        main.append(h("div", { class: "prm-vazio" }, h("h2", null, "Você ainda não registrou empresas"),
          h("p", null, "Comece pela que você conhece melhor: o registro leva poucos minutos e protege a sua indicação por um prazo."),
          h("div", { class: "prm-acoes" }, h("a", { class: "prm-btn", href: "#/registrar" }, "Registrar empresa"), h("a", { class: "prm-btn prm-btn--sec", href: "#/ajuda" }, "Ver como funciona"))));
      }
      const pede = h("section", { class: "prm-cartao prm-cartao--acao", "aria-labelledby": "t-pede" }, h("h2", { id: "t-pede" }, "Pede você"));
      if (!o.pede_voce.length) pede.append(apoio("Nada pendente com você agora."));
      else pede.append(h("ul", { class: "prm-lista" }, o.pede_voce.map((p) => h("li", { class: "prm-lista__item" },
        h("div", null, h("div", { class: "prm-lista__titulo" }, p.titulo), h("div", { class: "prm-lista__apoio" }, p.texto)),
        h("a", { class: "prm-btn prm-btn--sec", href: "#/" + p.go }, p.acao)))),
        o.pede_voce_total > o.pede_voce.length ? h("a", { class: "prm-btn prm-btn--texto", href: "#/empresas?aba=precisa_de_voce" }, "Ver tudo (" + o.pede_voce_total + ")") : null);
      const k = o.kpis;
      const kpi = (r, v, a, go) => h("a", { class: "prm-cartao prm-kpi prm-kpi-link", href: go }, h("span", { class: "prm-rotulo" }, r), h("span", { class: "prm-kpi__valor" }, String(v)), h("span", { class: "prm-kpi__apoio" }, a));
      const kpis = h("section", { "aria-label": "Resumo" }, h("div", { class: "prm-grade prm-grade--kpi" },
        kpi("Pedem você", k.pedem_voce, "itens com ação sua", "#/empresas?aba=precisa_de_voce"), kpi("Em andamento", k.em_andamento, "de " + k.empresas + " empresas", "#/negocios"),
        kpi("Registros válidos", k.registros_validos, "proteção em vigor", "#/empresas?aba=registros"), kpi("Respostas novas", k.respostas_novas, "dos seus pedidos", "#/pedidos")));
      const mudou = h("section", { class: "prm-cartao", "aria-labelledby": "t-mudou" }, h("h2", { id: "t-mudou" }, "O que mudou"),
        o.mudou.length ? h("ul", { class: "prm-lista" }, o.mudou.map((m) => h("li", { class: "prm-lista__item" }, h("div", null,
          h("div", { class: "prm-linha" }, m.novo ? h("span", { class: "prm-novo" }, "Novo") : null, h("span", { class: "prm-lista__titulo" }, m.titulo)),
          h("div", { class: "prm-lista__apoio" }, m.quando)), m.go ? h("a", { class: "prm-btn prm-btn--texto", href: "#/" + m.go, "aria-label": "Abrir: " + m.titulo }, "Abrir") : null))) : apoio("Nada novo nos últimos 7 dias."));
      const vencer = h("section", { class: "prm-cartao", "aria-labelledby": "t-vencer" }, h("h2", { id: "t-vencer" }, "Registros a vencer"),
        o.a_vencer.length ? h("ul", { class: "prm-lista" }, o.a_vencer.map((r) => h("li", { class: "prm-lista__item" }, h("div", null,
          h("div", { class: "prm-lista__titulo" }, r.razao_social || r.cnpj_mascara), h("div", { class: "prm-lista__apoio" }, "Válido até " + r.valido_ate)),
          chip(r.rotulo, r.chip)))) : apoio("Nenhum registro vence nos próximos 30 dias."));
      const nivel = h("section", { class: "prm-cartao", "aria-labelledby": "t-nivel" }, h("h2", { id: "t-nivel" }, "Seu nível"),
        h("div", { class: "prm-linha" }, h("span", { class: "prm-selo" }, o.nivel.selo), h("span", null, "Etapa da jornada: " + o.nivel.etapa)), h("a", { class: "prm-btn prm-btn--texto", href: "#/nivel" }, "Ver jornada"));
      const passos = o.primeiros_passos ? h("section", { class: "prm-cartao", "aria-labelledby": "t-passos" }, h("h2", { id: "t-passos" }, "Primeiros passos"),
        h("ul", { class: "prm-lista" }, o.primeiros_passos.map((p) => h("li", { class: "prm-lista__item" }, h("span", null, p.texto), chip(p.feito ? "Feito" : "A fazer", p.feito ? "ok" : "neutro")))),
        h("button", { class: "prm-btn prm-btn--texto", type: "button", onclick: async () => { await api("POST", "parceiro/primeiros-passos/dispensar", {}); navegar(); } }, "Dispensar")) : null;
      main.append(h("div", { class: "prm-pilha" }, pede, kpis, h("div", { class: "prm-grade prm-grade--2" }, mudou, vencer), h("div", { class: "prm-grade prm-grade--2" }, nivel, passos)));
    }, 4);
  }

  // ---------------- P-3 Registrar: CNPJ uma vez → Receita e regime → registro (ou consulta de várias)
  const INTERESSES = [["recuperacao", "Recuperação tributária (PIS/COFINS e outras teses)"], ["recorrencia", "Recorrência das novas competências"],
    ["passivo", "Gestão de Passivo (transação, CND, dívida ativa)"], ["juridico", "Produtos jurídicos"], ["planejamento", "Planejamento tributário e reforma"],
    ["patrimonial", "Estruturação patrimonial e sucessória"], ["gestao_contas", "Gestão de Contas e cobrança (Save Invest)"], ["antecipacao", "Antecipação de recebíveis e FIDC (Save Invest)"],
    ["tax_internacional", "Tax internacional e comércio exterior"], ["nao_sei", "Ainda não sei"], ["descoberta", "Outro tema (em descoberta)"]];
  const COMO = [["cliente_escritorio", "Cliente do meu escritório"], ["relacionamento", "Relacionamento comercial"], ["indicacao_terceiro", "Indicação de terceiro"], ["outro", "Outro"]];
  const EVID = [["declaracao", "Declaração de relacionamento"], ["reuniao", "Reunião marcada"], ["documento", "Documento recebido"], ["procuracao", "Procuração ou e-CAC"]];

  async function vRegistrar(main, _x, params) {
    cab(main, "Registrar oportunidade", "Digite o CNPJ uma vez: trazemos os dados da Receita e o regime, e você registra a indicação.");
    const abas = h("div", { class: "prm-abas", role: "tablist", "aria-label": "Modo" });
    const painel1 = h("div", { role: "tabpanel", id: "p-uma" }), painel2 = h("div", { role: "tabpanel", id: "p-varias", hidden: true });
    const aba = (id, t, p, sel) => h("button", { class: "prm-aba", role: "tab", id: "a-" + id, "aria-controls": p.id, "aria-selected": String(sel), type: "button",
      onclick: () => { abas.querySelectorAll("[role=tab]").forEach((b) => b.setAttribute("aria-selected", "false")); abas.querySelector("#a-" + id).setAttribute("aria-selected", "true");
        painel1.hidden = p !== painel1; painel2.hidden = p !== painel2; } }, t);
    abas.append(aba("uma", "Uma empresa", painel1, true), aba("varias", "Várias empresas (só consulta)", painel2, false));
    main.append(abas, painel1, painel2);
    formRegistro(painel1, params.get("cnpj") || "");
    formVarias(painel2, (cnpj) => { abas.querySelector("#a-uma").click(); limpar(painel1); formRegistro(painel1, cnpj); });
  }

  function formRegistro(alvo, cnpjInicial) {
    const fCnpj = campo({ rotulo: "CNPJ", dica: "CNPJ com ou sem pontuação. Pode ser numérico ou com letras.", mono: true,
      atributos: { inputmode: "text", autocapitalize: "characters", autocomplete: "off", spellcheck: "false", maxlength: "20" }, valor: cnpjInicial });
    const empresa = h("div", { "aria-live": "polite" });
    const fRazao = campo({ rotulo: "Razão social", atributos: { autocomplete: "organization", readonly: true } });
    const fNome = campo({ rotulo: "Nome do decisor na empresa", dica: "Não precisamos de CPF.", atributos: { autocomplete: "off" } });
    const fCargo = campo({ rotulo: "Cargo do decisor", atributos: { autocomplete: "off" } });
    const fEmail = campo({ rotulo: "E-mail corporativo do decisor", tipo: "email", dica: "Informe o e-mail ou o telefone da empresa (um dos dois).", atributos: { autocomplete: "off" } });
    const fTel = campo({ rotulo: "Telefone da empresa", tipo: "tel", dica: "Telefone da empresa, não o pessoal.", opcional: true, atributos: { autocomplete: "off", inputmode: "tel" } });
    const fInt = campo({ rotulo: "Interesse", opcoes: INTERESSES });
    const fComo = campo({ rotulo: "Como você conhece a empresa", opcoes: COMO });
    const fEvid = campo({ rotulo: "Evidência da relação", opcoes: EVID, valor: "declaracao" });
    const fData = campo({ rotulo: "Data da reunião", tipo: "date" }); fData.hidden = true;
    const fNota = campo({ rotulo: "Observação", area: true, opcional: true, dica: "Ex.: o sócio pediu a revisão por e-mail. Até 500 caracteres. Não escreva CPF, RG, CNH ou dados bancários.", atributos: { maxlength: "500" } });
    const dLgpd = checkbox(uid("lgpd"), "Declaro que tenho autorização ou base legal para compartilhar este contato com a Save para esta finalidade.");
    const dProm = checkbox(uid("prom"), "Não prometi à empresa valor, prazo ou resultado.");
    const msgDecl = h("p", { class: "prm-campo__msg", "aria-live": "polite", hidden: true });
    fEvid.entrada.addEventListener("change", () => { fData.hidden = fEvid.entrada.value !== "reuniao"; });
    const btn = h("button", { class: "prm-btn", type: "submit", disabled: true }, "Registrar oportunidade");
    const motivoBtn = h("p", { class: "prm-texto-apoio", id: uid("motivo") }, "Digite um CNPJ válido para liberar o registro.");
    btn.setAttribute("aria-describedby", motivoBtn.id);
    const secaoC = h("fieldset", { class: "prm-form", hidden: true, disabled: true }, h("legend", { class: "prm-titulo-secao" }, "Sobre a oportunidade"),
      fRazao, h("div", { class: "prm-campos" }, fNome, fCargo), h("div", { class: "prm-campos" }, fEmail, fTel), h("div", { class: "prm-campos" }, fInt, fComo),
      h("div", { class: "prm-campos" }, fEvid, fData), fNota, dLgpd, S.eu.primeira_declaracao ? dProm : null, msgDecl);
    const secaoCartao = h("section", { class: "prm-cartao", hidden: true }, secaoC);
    const resultado = h("div", { id: "resultado-registro", "aria-live": "polite" });
    const soDossie = h("button", { class: "prm-btn prm-btn--texto", type: "button", hidden: true }, "Só quero o dossiê, sem registrar");
    const form = h("form", { class: "prm-form", novalidate: true }, h("section", { class: "prm-cartao prm-pilha--peq", "aria-labelledby": "t-a" },
      h("h2", { id: "t-a", class: "prm-titulo-secao" }, "Empresa"), fCnpj, empresa, soDossie), secaoCartao,
      h("div", { class: "prm-form__rodape" }, h("div", { class: "prm-pilha--peq" }, btn, motivoBtn)));
    alvo.append(form, resultado, recentes());
    let atual = null, chave = crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random();
    const liberar = (ok, motivo) => { btn.disabled = !ok; secaoC.hidden = !ok; secaoCartao.hidden = !ok; secaoC.disabled = !ok; motivoBtn.textContent = ok ? "" : motivo; motivoBtn.hidden = ok; };
    const declarar = (t) => { msgDecl.textContent = t || ""; msgDecl.hidden = !t; };

    const checar = debounce(async () => {
      const c = normCnpj(fCnpj.entrada.value);
      limpar(empresa); soDossie.hidden = true; atual = null;
      if (c.length < 14) { fCnpj.estado("", ""); liberar(false, "Digite um CNPJ válido para liberar o registro."); return; }
      const r1 = await api("POST", "parceiro/empresa/checar", { cnpj: c });
      if (r1.st !== 200) { fCnpj.estado("erro", r1.o.erro || "Não conseguimos conferir agora. Tente de novo."); return; }
      if (r1.o.estado === "erro_formato") { fCnpj.estado("erro", r1.o.mensagem); liberar(false, "Revise o CNPJ."); return; }
      if (r1.o.estado === "ja_e_seu") {
        fCnpj.estado("ok", r1.o.mensagem);
        const ref = (r1.o.registro || r1.o.negocio || {}).ref;
        empresa.append(h("div", { class: "prm-resultado prm-resultado--seu" }, h("h3", null, r1.o.titulo), h("p", null, r1.o.mensagem), ref ? h("div", null, h("a", { class: "prm-btn prm-btn--sec", href: "#/empresas/" + ref }, "Abrir empresa")) : null));
        liberar(false, "Esta empresa já está com você."); return;
      }
      fCnpj.estado("consultando", "Buscando na Receita Federal…");
      const r2 = await api("POST", "parceiro/empresa/consultar", { cnpjs: [c] });
      const r = r2.st === 200 ? r2.o.resultados[0] : null;
      if (!r) { fCnpj.estado("erro", r2.o.erro || "A Receita não respondeu agora. Você pode seguir e preencher o nome da empresa."); return; }
      atual = r;
      fRazao.entrada.readOnly = true;
      if (r.neutra) {
        fCnpj.estado("", r.titulo);
        fRazao.entrada.readOnly = false; fRazao.entrada.value = "";
        liberar(true);
      } else if (!r.empresa) {
        fCnpj.estado("", "A Receita não respondeu agora. Você pode seguir e preencher o nome da empresa.");
        fRazao.entrada.readOnly = false; fRazao.entrada.value = "";
        liberar(true);
      } else if (r.situacao_ativa === false) {
        fCnpj.estado("erro", "Na Receita, esta empresa aparece como " + (r.empresa.situacao || "inativa").toLowerCase() + ". Só registramos empresas ativas.");
        liberar(false, "Só registramos empresas ativas.");
      } else {
        fCnpj.estado("ok", "Empresa encontrada.");
        empresa.append(h("div", { class: "prm-empresa" }, h("div", { class: "prm-empresa__nome" }, r.empresa.razao),
          h("div", { class: "prm-empresa__meta" }, [r.empresa.uf, r.cnae, r.empresa.situacao].filter(Boolean).join(" · ")),
          h("div", null, chip(r.titulo, r.faixa === "confirmado_real" ? "ok" : r.faixa === "provavel_real" ? "info" : "neutro"), r.ano_base ? " Ano-base " + r.ano_base : ""),
          r.detalhe ? h("div", { class: "prm-texto-apoio" }, r.detalhe) : null));
        fRazao.entrada.value = r.empresa.razao || "";
        soDossie.hidden = false;
        liberar(true);
      }
    }, 400);
    fCnpj.entrada.addEventListener("input", () => { fCnpj.estado("", ""); checar(); });
    if (cnpjInicial) checar();

    soDossie.addEventListener("click", async () => {
      soDossie.setAttribute("aria-busy", "true");
      const r = await fetchLegado("POST", "esteira", { cnpj: normCnpj(fCnpj.entrada.value) });
      soDossie.removeAttribute("aria-busy");
      mostrarResultado(resultado, r.st === 200 ? { titulo: "Pedido de dossiê " + r.o.id, texto: "Andamento: " + r.o.andamento + ". O dossiê aparece aqui quando estiver pronto.", tipo: "recebido" }
        : { titulo: "Não foi possível pedir o dossiê", texto: r.o.erro || "Tente de novo em instantes.", tipo: "bloqueado" });
    });

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const campos = { cnpj: fCnpj, razao_social: fRazao, contato_nome: fNome, contato_cargo: fCargo, contato_email: fEmail, contato_tel: fTel, interesse: fInt,
        como_conhece: fComo, evidencia_tipo: fEvid, evidencia_data: fData, evidencia_nota: fNota };
      declarar("");
      const corpo = { cnpj: normCnpj(fCnpj.entrada.value), razao_social: fRazao.entrada.value, contato_nome: fNome.entrada.value, contato_cargo: fCargo.entrada.value,
        contato_email: fEmail.entrada.value, contato_tel: fTel.entrada.value, interesse: fInt.entrada.value, como_conhece: fComo.entrada.value,
        evidencia_tipo: fEvid.entrada.value, evidencia_data: fData.entrada.value, evidencia_nota: fNota.entrada.value,
        declaracao_lgpd: dLgpd.entrada.checked, declaracao_sem_promessa: S.eu.primeira_declaracao ? dProm.entrada.checked : undefined, chave_idempotencia: chave };
      btn.setAttribute("aria-busy", "true"); btn.disabled = true;
      const { st, o } = await api("POST", "parceiro/registros", corpo);
      btn.removeAttribute("aria-busy"); btn.disabled = false;
      if (st === 422) {
        const errs = o.campos || {};
        if (errs.declaracao_lgpd || errs.declaracao_sem_promessa) declarar(errs.declaracao_lgpd || errs.declaracao_sem_promessa);
        if (!aplicarErros(campos, errs)) { declarar(o.erro); (errs.declaracao_lgpd ? dLgpd : dProm).entrada.focus(); }
        anunciar(o.erro || "Revise os campos destacados.");
        return;
      }
      if (st === 0 || st >= 500) {
        mostrarResultado(resultado, { titulo: "O registro não foi enviado", texto: "Seus dados continuam no formulário.", tipo: "erro", tentar: () => form.requestSubmit() });
        return;
      }
      if (st === 403) { mostrarResultado(resultado, { titulo: "Sem permissão", texto: o.erro, tipo: "bloqueado" }); return; }
      if (st !== 200 && st !== 201) { mostrarResultado(resultado, { titulo: "Não foi possível registrar", texto: o.erro || "", tipo: "bloqueado" }); return; }
      S.eu.primeira_declaracao = false;
      chave = crypto.randomUUID ? crypto.randomUUID() : String(Date.now());
      if (o.resultado === "ja_e_seu") {
        const ref = (o.registro || o.negocio || {}).ref;
        mostrarResultado(resultado, { titulo: o.titulo, texto: o.mensagem, tipo: "seu", acoes: ref ? [h("a", { class: "prm-btn prm-btn--sec", href: "#/empresas/" + ref }, "Abrir empresa")] : [] });
        return;
      }
      const ref = o.registro.ref;
      form.reset(); limpar(empresa); soDossie.hidden = true; liberar(false, "Digite um CNPJ válido para liberar o registro."); fCnpj.estado("", "");
      mostrarResultado(resultado, { titulo: o.titulo + " · " + o.registro.registro_id, texto: o.mensagem, tipo: "recebido",
        acoes: [h("button", { class: "prm-btn", type: "button", onclick: async (ev) => {
          ev.currentTarget.setAttribute("aria-busy", "true");
          const r = await api("POST", "parceiro/empresas/" + ref + "/dossie", {});
          ev.currentTarget.removeAttribute("aria-busy");
          if (r.st === 200) toast("Dossiê pedido", "Andamento: " + r.o.andamento + ". Acompanhe na ficha da empresa.");
          else toast("Dossiê", r.o.erro || "Não conseguimos pedir agora.", "atencao");
        } }, "Pedir dossiê desta empresa"),
        h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => { limpar(resultado); fCnpj.entrada.focus(); } }, "Registrar outra"),
        h("a", { class: "prm-btn prm-btn--sec", href: "#/empresas" }, "Ir para Empresas")] });
    });
  }

  // resultado do envio: região viva que já existe, foco no título e rolagem até ele; no celular, folha inferior (P0-5)
  function mostrarResultado(regiao, { titulo, texto, tipo, acoes, tentar }) {
    limpar(regiao);
    const t = h("h2", { tabindex: "-1" }, titulo);
    const bloco = tipo === "erro"
      ? h("div", { class: "prm-aviso prm-aviso--erro", role: "alert" }, icone("alerta"), h("div", { class: "prm-pilha--peq" }, t, h("p", null, texto),
        tentar ? h("div", null, h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: tentar }, "Tentar de novo")) : null))
      : h("div", { class: "prm-resultado prm-resultado--" + tipo }, t, h("p", null, texto), acoes && acoes.length ? h("div", { class: "prm-acoes prm-acoes--empilha" }, acoes) : null);
    regiao.append(bloco);
    if (celular() && tipo !== "erro") {
      const copia = (acoes || []).map((a) => { const c = a.cloneNode(true); c.addEventListener("click", () => { a.click(); }); return c; });
      modal({ titulo, texto, corpo: copia.length ? h("div", { class: "prm-acoes prm-acoes--empilha" }, copia) : null, soFechar: true });
      document.querySelectorAll(".prm-modal a, .prm-modal .prm-acoes button").forEach((x) => x.addEventListener("click", () => { const v = document.querySelector(".prm-veu"); if (v) v.click(); }));
    } else {
      t.focus(); regiao.scrollIntoView({ block: "center", behavior: "smooth" });
    }
  }

  async function fetchLegado(metodo, caminho, corpo) {
    const cab = { Accept: "application/json", "Content-Type": "application/json" };
    if (S.modo === "dev") cab["X-PRM-Dev-Usuario"] = S.dev;
    if (S.modo === "msal") cab.Authorization = "Bearer " + (await token());
    try {
      const r = await fetch("/api/" + caminho, { method: metodo, headers: cab, body: corpo ? JSON.stringify(corpo) : undefined, cache: "no-store" });
      return { st: r.status, o: await r.json().catch(() => ({})) };
    } catch (e) { return { st: 0, o: {} }; }
  }

  function recentes() {
    const s = h("section", { class: "prm-cartao", "aria-labelledby": "t-rec", hidden: true }, h("h2", { id: "t-rec", class: "prm-titulo-secao" }, "Consultadas recentemente"));
    fetchLegado("GET", "esteira/historico").then((r) => {
      if (r.st !== 200 || !r.o.empresas || !r.o.empresas.length) return;
      s.hidden = false;
      s.append(h("ul", { class: "prm-lista" }, r.o.empresas.slice(0, 5).map((x) => h("li", { class: "prm-lista__item" },
        h("div", null, h("div", { class: "prm-lista__titulo" }, x.razao || "Empresa"), h("div", { class: "prm-lista__apoio" }, x.titulo || "")),
        h("a", { class: "prm-btn prm-btn--texto", href: "#/registrar?cnpj=" + encodeURIComponent(x.cnpj), "aria-label": "Registrar " + (x.razao || "empresa") }, "Registrar")))));
    });
    return s;
  }

  function formVarias(alvo, aoRegistrar) {
    const f = campo({ rotulo: "CNPJs (até 20, um por linha)", area: true, mono: true, dica: "Consulta o regime de cada empresa. Não registra em lote: cada registro precisa do contexto da relação." });
    const btn = h("button", { class: "prm-btn", type: "submit" }, "Consultar");
    const res = h("div", { "aria-live": "polite" });
    const form = h("form", { class: "prm-form prm-cartao", novalidate: true }, f, h("div", null, btn));
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const lista = f.entrada.value.split(/[\s,;]+/).map(normCnpj).filter((x) => x.length >= 12);
      if (!lista.length) { f.estado("erro", "Informe ao menos um CNPJ."); f.entrada.focus(); return; }
      if (lista.length > 20) { f.estado("erro", "No máximo 20 CNPJs por consulta."); return; }
      f.estado("", ""); btn.setAttribute("aria-busy", "true");
      const { st, o } = await api("POST", "parceiro/empresa/consultar", { cnpjs: lista });
      btn.removeAttribute("aria-busy");
      limpar(res);
      if (st !== 200) { res.append(h("div", { class: "prm-aviso prm-aviso--erro", role: "alert" }, icone("alerta"), h("div", null, o.erro || "Não conseguimos consultar agora."))); return; }
      const t = h("h2", { class: "prm-titulo-secao", tabindex: "-1" }, o.resultados.length + " empresa(s) consultada(s)");
      res.append(h("section", { class: "prm-cartao" }, t, h("ul", { class: "prm-lista" }, o.resultados.map((r, i) => h("li", { class: "prm-lista__item" },
        h("div", null, h("div", { class: "prm-lista__titulo" }, r.ja_e_seu ? "Empresa já é sua" : (r.empresa && r.empresa.razao) || r.cnpj_mascara),
          h("div", { class: "prm-lista__apoio" }, r.ja_e_seu ? r.ja_e_seu.mensagem : r.titulo + (r.ano_base ? " · ano-base " + r.ano_base : ""))),
        !r.ja_e_seu && r.pode_registrar !== false ? h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => aoRegistrar(lista[i]) }, "Registrar") : null)))));
      t.focus();
    });
    alvo.append(form, res);
  }

  // ---------------- P-4 Empresas
  async function vEmpresas(main, _x, params) {
    await carregar(main, "parceiro/empresas" + (params.get("consultor") ? "?consultor=" + encodeURIComponent(params.get("consultor")) : ""), (o) => {
      cab(main, "Empresas", "Registros e negócios juntos, com o próximo passo de cada empresa.", [h("a", { class: "prm-btn", href: "#/registrar" }, "Registrar empresa")]);
      let aba = params.get("aba") || (o.abas.precisa_de_voce ? "precisa_de_voce" : "andamento");
      const ABAS = [["precisa_de_voce", "Precisa de você"], ["andamento", "Em andamento"], ["registros", "Registros"], ["encerradas", "Encerradas"]];
      const VAZIO = { precisa_de_voce: "Nenhuma empresa espera algo de você.", andamento: "Nenhuma empresa em andamento.", registros: "Nenhum registro em análise ou válido.", encerradas: "Nenhuma empresa encerrada." };
      const busca = h("input", { class: "prm-campo__entrada", type: "search", "aria-label": "Buscar por nome ou CNPJ", placeholder: "Buscar por nome ou CNPJ" });
      const barra = h("div", { class: "prm-barra-filtro" }, busca);
      if (o.equipe && o.equipe.length) {
        const sel = h("select", { class: "prm-campo__entrada", "aria-label": "Consultor" }, h("option", { value: "" }, "Consultor: todos"), o.equipe.map((u) => h("option", { value: u.id, selected: params.get("consultor") === u.id ? true : null }, u.nome)));
        sel.addEventListener("change", () => { location.hash = "#/empresas" + (sel.value ? "?consultor=" + sel.value : ""); });
        barra.append(sel);
      }
      const filtros = h("div", { class: "prm-filtros", role: "group", "aria-label": "Filtrar empresas" });
      const lista = h("div", { "aria-live": "polite" });
      const desenhar = () => {
        const q = busca.value.trim().toLowerCase();
        const xs = o.itens.filter((i) => i.aba === aba && (!q || (i.nome || "").toLowerCase().includes(q) || (i.cnpj_mascara || "").toLowerCase().includes(q)));
        limpar(lista);
        if (!xs.length) { lista.append(h("div", { class: "prm-vazio" }, h("p", null, q ? "Nenhuma empresa encontrada." : VAZIO[aba]), aba === "registros" ? h("a", { class: "prm-btn", href: "#/registrar" }, "Registrar empresa") : null)); return; }
        lista.append(h("ul", { class: "prm-lista prm-cartao" }, xs.map((i) => h("li", { class: "prm-lista__item" }, h("a", { class: "prm-lista__link", href: "#/empresas/" + i.ref },
          h("div", null, h("div", { class: "prm-lista__titulo" }, i.nome || "Empresa indicada"), h("div", { class: "prm-lista__apoio prm-mono" }, i.cnpj_mascara || ""),
            h("div", { class: "prm-lista__apoio" }, i.proximo_passo), h("div", { class: "prm-lista__apoio" }, "Com: " + i.com + " · desde " + i.desde)),
          chip(i.rotulo, i.chip))))));
      };
      ABAS.forEach(([k, n]) => filtros.append(h("button", { class: "prm-filtro", type: "button", "aria-pressed": String(k === aba), onclick: (e) => {
        aba = k; filtros.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", "false")); e.currentTarget.setAttribute("aria-pressed", "true"); desenhar(); } },
        n + " " + (o.abas[k] || 0))));
      busca.addEventListener("input", debounce(desenhar, 200));
      main.append(barra, filtros, lista);
      desenhar();
    });
  }

  // ---------------- P-5 Ficha da empresa
  async function vFicha(main, ref) {
    await carregar(main, "parceiro/empresas/" + ref, (o) => {
      const est = o.negocio || o.registro;
      cab(main, o.nome, null, [h("a", { class: "prm-btn prm-btn--sec", href: "#/pedidos/novo?empresa=" + ref }, "Perguntar sobre esta empresa")], "Empresa");
      main.querySelector(".prm-cab p") || main.querySelector(".prm-cab > div").append(h("p", { class: "prm-mono" }, o.cnpj_mascara || ""),
        h("div", { class: "prm-linha" }, chip(est.rotulo, est.chip), o.negocio ? apoio("Com: " + o.negocio.com + " desde " + o.negocio.desde) : null));
      if (o.negocio && o.negocio.pendencias.length) {
        main.append(h("section", { class: "prm-cartao prm-cartao--acao", "aria-labelledby": "t-pend" }, h("h2", { id: "t-pend" }, "Precisa de você"),
          o.negocio.pendencias.map((p) => h("p", null, (p.texto || p.tipo) + " (desde " + p.desde + ")")), h("p", null, "Se já enviou, avise em Pedidos."),
          h("a", { class: "prm-btn", href: "#/pedidos/novo?empresa=" + ref }, "Avisar a Save")));
      }
      if (o.registro && o.registro.aguarda_resposta) {
        const f = campo({ rotulo: "Sua resposta", area: true, atributos: { maxlength: "500" } });
        const b = h("button", { class: "prm-btn", type: "button" }, "Enviar resposta");
        b.addEventListener("click", async () => {
          b.setAttribute("aria-busy", "true");
          const r = await api("POST", "parceiro/registros/" + o.registro.ref + "/complemento", { resposta: f.entrada.value });
          b.removeAttribute("aria-busy");
          if (r.st === 200) { toast("Resposta enviada", "O registro voltou para análise com a data e a hora originais."); navegar(); } else f.estado("erro", r.o.erro || "Não conseguimos enviar agora.");
        });
        main.append(h("section", { class: "prm-cartao prm-cartao--acao" }, h("h2", null, "A Save precisa de uma informação"), h("p", null, o.registro.mensagem), f, h("div", null, b)));
      }
      const abas = [["andamento", "Andamento"], ["registro", "Registro"], ["dossie", "Dossiê"], ["pedidos", "Pedidos (" + o.pedidos.length + ")"]];
      if (S.eu.papel === "titular") abas.push(["extrato", "Extrato"]);
      const lista = h("div", { class: "prm-abas", role: "tablist", "aria-label": "Seções da empresa" });
      const paineis = {};
      abas.forEach(([k, n], i) => {
        paineis[k] = h("div", { role: "tabpanel", id: "pn-" + k, "aria-labelledby": "ab-" + k, hidden: i !== 0, class: "prm-cartao" });
        lista.append(h("button", { class: "prm-aba", role: "tab", id: "ab-" + k, type: "button", "aria-controls": "pn-" + k, "aria-selected": String(i === 0), onclick: () => {
          abas.forEach(([x]) => { paineis[x].hidden = x !== k; lista.querySelector("#ab-" + x).setAttribute("aria-selected", String(x === k)); }); } }, n));
      });
      main.append(lista, ...Object.values(paineis));
      // Andamento
      if (o.negocio) {
        paineis.andamento.append(h("a", { class: "prm-btn prm-btn--sec", href: "#/negocios/" + o.negocio.ref }, "Ver o acompanhamento completo do negócio"));
        paineis.andamento.append(h("ol", { class: "prm-tempo" }, o.negocio.passos.map((p) => h("li", { class: "prm-tempo__passo", "data-estado": p.situacao, "aria-current": p.situacao === "atual" || p.situacao === "bloqueado" ? "step" : null },
          h("span", { class: "prm-tempo__titulo" }, p.titulo), h("span", { class: "prm-tempo__quando" }, { feito: "concluído", atual: "atual", bloqueado: "esperando você", futuro: "próximo" }[p.situacao])))),
          h("p", null, h("strong", null, "Próximo passo: "), o.negocio.proximo_passo));
      } else paineis.andamento.append(h("p", null, o.registro.mensagem), apoio("O andamento aparece aqui quando o atendimento da empresa começar."));
      // Registro
      if (o.registro) {
        const r = o.registro;
        const acoes = [];
        if (r.pode_prorrogar) acoes.push(h("button", { class: "prm-btn", type: "button", onclick: () => pedirProrrogacao(r) }, "Pedir prorrogação"));
        if (r.pode_cancelar) acoes.push(h("button", { class: "prm-btn prm-btn--perigo", type: "button", onclick: () => modal({ titulo: "Cancelar o registro " + r.registro_id + "?",
          texto: "A empresa deixa de ficar registrada para você e pode ser registrada de novo. Esta ação não pode ser desfeita.", verbo: "Cancelar registro", perigo: true, cancelar: "Voltar",
          aoConfirmar: async () => { const x = await api("POST", "parceiro/registros/" + r.ref + "/cancelar", {}); if (x.st !== 200) throw new Error(x.o.erro); toast("Registro cancelado", ""); navegar(); } }) }, "Cancelar registro"));
        paineis.registro.append(h("dl", { class: "prm-dl prm-dl--esq" }, h("dt", null, "Registro"), h("dd", null, r.registro_id), h("dt", null, "Data e hora do registro"), h("dd", null, r.carimbo),
          h("dt", null, "Situação"), h("dd", null, r.rotulo), r.valido_ate ? [h("dt", null, "Válido até"), h("dd", null, r.valido_ate)] : null, h("dt", null, "Interesse"), h("dd", null, r.interesse || "")),
          h("p", null, r.mensagem), acoes.length ? h("div", { class: "prm-acoes prm-acoes--empilha" }, acoes) : null);
      } else paineis.registro.append(apoio("Esta empresa chegou à Save antes do registro pelo portal."));
      // Dossiê
      if (o.dossie) {
        const d = o.dossie;
        paineis.dossie.append(h("div", { class: "prm-linha" }, chip(d.andamento, d.status === "entregue" ? "ok" : "info"), d.aprofundando ? apoio("Os agentes estão aprofundando esta versão.") : null));
        if (d.resultado && d.resultado.dossie) {
          const [primeiro, ...resto] = d.resultado.dossie;
          paineis.dossie.append(h("h3", { class: "prm-titulo-secao" }, primeiro.titulo), (primeiro.paragrafos || []).map((p) => h("p", null, p)),
            resto.map((s) => h("details", { class: "prm-detalhe" }, h("summary", null, s.titulo), (s.paragrafos || []).map((p) => h("p", null, p)), s.itens && s.itens.length ? h("ul", null, s.itens.map((i) => h("li", null, i))) : null)),
            h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => baixarWord(ref) }, "Baixar em Word"));
        } else paineis.dossie.append(apoio("O dossiê aparece aqui depois da revisão da Save."));
      } else if (o.pode_pedir_dossie) {
        const b = h("button", { class: "prm-btn", type: "button" }, "Pedir dossiê desta empresa");
        b.addEventListener("click", async () => { b.setAttribute("aria-busy", "true"); const r = await api("POST", "parceiro/empresas/" + ref + "/dossie", {}); b.removeAttribute("aria-busy");
          if (r.st === 200) { toast("Dossiê pedido", "Andamento: " + r.o.andamento); navegar(); } else toast("Dossiê", r.o.erro || "Não conseguimos pedir agora.", "atencao"); });
        paineis.dossie.append(apoio("Briefing da empresa, serviços aderentes e como abordar, montado a partir dos dados públicos da Receita."), h("div", null, b));
      } else paineis.dossie.append(apoio("O dossiê fica disponível para empresas registradas por você e ainda sem atendimento aberto."));
      // Pedidos
      paineis.pedidos.append(o.pedidos.length ? h("ul", { class: "prm-lista" }, o.pedidos.map((p) => h("li", { class: "prm-lista__item" }, h("a", { class: "prm-lista__link", href: "#/pedidos/" + p.ref },
        h("div", null, h("div", { class: "prm-lista__titulo" }, p.id + " · " + p.tipo), h("div", { class: "prm-lista__apoio" }, p.aberta_em)), chip(p.rotulo, p.chip))))) : apoio("Nenhum pedido sobre esta empresa."),
        h("a", { class: "prm-btn prm-btn--sec", href: "#/pedidos/novo?empresa=" + ref }, "Perguntar sobre esta empresa"));
      // Extrato
      if (paineis.extrato) paineis.extrato.append(o.extrato.length ? o.extrato.map(linhaExtrato) : apoio("Sem linhas de extrato para esta empresa."));
    });
  }

  function pedirProrrogacao(r) {
    const f = campo({ rotulo: "O que aconteceu com a empresa", area: true, dica: "Conte o avanço: reunião feita, documento recebido, conversa com o decisor.", atributos: { maxlength: "500" } });
    modal({ titulo: "Pedir prorrogação de " + (r.razao_social || r.registro_id), texto: "O registro vale até " + r.valido_ate + ". A Área Partners responde aqui.", corpo: f, verbo: "Enviar pedido",
      aoConfirmar: async () => { const x = await api("POST", "parceiro/registros/" + r.ref + "/prorrogacao", { fato: f.entrada.value });
        if (x.st !== 200) { f.estado("erro", x.o.erro || "Não conseguimos enviar."); return false; } toast("Pedido de prorrogação enviado", x.o.mensagem); navegar(); } });
  }

  async function baixarWord(ref) {
    const r = await api("GET", "parceiro/empresas/" + ref + "/dossie/arquivo", undefined, true);
    if (!r.r || r.st !== 200) { toast("Word do dossiê", "Não conseguimos gerar o Word agora. Tente de novo em instantes.", "atencao"); return; }
    const blob = await r.r.blob(); const url = URL.createObjectURL(blob);
    const a = h("a", { href: url, download: "dossie.docx" }); document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 2000);
  }

  // ---------------- P-6 Pedidos
  async function vPedidos(main) {
    await carregar(main, "parceiro/pedidos", (o) => {
      cab(main, "Pedidos", "Peça à Save por aqui e acompanhe a resposta.", [h("a", { class: "prm-btn", href: "#/pedidos/novo" }, "Novo pedido")]);
      if (!o.itens.length) { main.append(h("div", { class: "prm-vazio" }, h("p", null, "Você ainda não fez pedidos por aqui."), h("a", { class: "prm-btn", href: "#/pedidos/novo" }, "Novo pedido"))); return; }
      main.append(h("ul", { class: "prm-lista prm-cartao" }, o.itens.map((p) => h("li", { class: "prm-lista__item" }, h("a", { class: "prm-lista__link", href: "#/pedidos/" + p.ref },
        h("div", null, h("div", { class: "prm-lista__titulo" }, p.id + " · " + p.tipo), h("div", { class: "prm-lista__apoio" }, (p.empresa_nome ? p.empresa_nome + " · " : "") + "aberto em " + p.aberta_em),
          p.prazo ? h("div", { class: "prm-lista__apoio" }, p.prazo) : null), chip(p.rotulo, p.chip))))));
    });
  }

  async function vNovoPedido(main, _x, params) {
    carregando(main, 2);
    const [t, e] = await Promise.all([api("GET", "parceiro/tipos-pedido"), api("GET", "parceiro/empresas")]);
    pronto(main);
    if (t.st !== 200) return erroBloco(main, t.o, t.st, () => navegar());
    cab(main, "Novo pedido", null);
    const tipoMsg = h("p", { class: "prm-campo__msg", "aria-live": "polite", id: "tipo-msg" });
    const grupo = h("fieldset", { class: "prm-escolhas", "aria-describedby": "tipo-msg" }, h("legend", { class: "prm-campo__rotulo" }, "Sobre o quê"),
      t.o.tipos.map((x, i) => h("label", { class: "prm-escolha" }, h("input", { type: "radio", name: "tipo", value: x.tipo, required: i === 0 ? true : null }), x.rotulo)));
    const empresas = (e.st === 200 ? e.o.itens : []).map((i) => [i.ref, (i.nome || "Empresa indicada") + (i.cnpj_mascara ? " · " + i.cnpj_mascara : "")]);
    const fEmp = campo({ rotulo: "Empresa", opcoes: empresas, opcional: true, valor: params.get("empresa") || "" });
    const fTexto = campo({ rotulo: "Seu pedido", area: true, dica: "Não escreva CPF, RG, CNH ou dados bancários.", atributos: { maxlength: "2000" } });
    fTexto.entrada.addEventListener("input", debounce(() => {
      const v = fTexto.entrada.value;
      if (/(\d{3}\.\d{3}\.\d{3}-\d{2})|(^|\D)\d{11}(\D|$)|\b(rg|cnh|pix|ag[eê]ncia|conta corrente)\b/i.test(v)) fTexto.estado("erro", "O texto parece ter um dado pessoal. Retire antes de enviar.");
      else fTexto.estado("", "");
    }, 300));
    const btn = h("button", { class: "prm-btn", type: "submit" }, "Enviar pedido");
    const form = h("form", { class: "prm-form prm-cartao", novalidate: true }, grupo, tipoMsg, fEmp, fTexto,
      h("div", { class: "prm-aviso prm-aviso--info" }, icone("info"), h("div", null, t.o.aviso_anexo)), h("div", { class: "prm-form__rodape" }, btn));
    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const tipo = (form.querySelector("input[name=tipo]:checked") || {}).value;
      if (!tipo) { tipoMsg.textContent = "Escolha sobre o que é o pedido."; form.querySelector("input[name=tipo]").focus(); return; }
      tipoMsg.textContent = "";
      btn.setAttribute("aria-busy", "true"); btn.disabled = true;
      const { st, o } = await api("POST", "parceiro/pedidos", { tipo, texto: fTexto.entrada.value, empresa_ref: fEmp.entrada.value || undefined });
      btn.removeAttribute("aria-busy"); btn.disabled = false;
      if (st === 201) { toast("Pedido " + o.id + " enviado.", o.prazo || ""); location.hash = "#/pedidos/" + o.ref; return; }
      const errs = o.campos || { texto: o.erro };
      if (errs.tipo) tipoMsg.textContent = errs.tipo;
      if (errs.texto) { fTexto.estado("erro", errs.texto); fTexto.entrada.focus(); }
      anunciar(o.erro || "Revise o pedido.");
    });
    main.append(form);
  }

  async function vPedido(main, ref) {
    await carregar(main, "parceiro/pedidos/" + ref, (p) => {
      cab(main, "Pedido " + p.id, p.tipo + (p.empresa_nome ? " · " + p.empresa_nome : ""), null, "Pedido");
      main.append(h("div", { class: "prm-linha" }, chip(p.rotulo, p.chip), p.prazo ? apoio(p.prazo) : null, p.atrasada ? apoio("Levando mais tempo que o previsto. Já cobramos a área.") : null));
      main.append(h("ol", { class: "prm-conversa", "aria-label": "Conversa" }, p.mensagens.map((m) => h("li", { class: "prm-msg prm-msg--" + (m.de === "parceiro" ? "parceiro" : "save") },
        h("p", null, m.texto), h("div", { class: "prm-msg__meta" }, (m.de === "parceiro" ? "Você" : "Resposta da Save") + " · " + m.quando + (m.selo ? " · " + m.selo : ""))))));
      const acoes = h("div", { class: "prm-acoes prm-acoes--empilha" });
      const enviar = async (rota, corpo, ok) => { const r = await api("POST", "parceiro/pedidos/" + ref + "/" + rota, corpo || {}); if (r.st === 200) { toast(ok, ""); navegar(); } else toast("Pedido", r.o.erro || "Não conseguimos agora.", "atencao"); };
      if (p.pode_complementar) {
        const f = campo({ rotulo: "Sua resposta", area: true, dica: "Não escreva CPF, RG, CNH ou dados bancários." });
        main.append(h("div", { class: "prm-cartao prm-pilha--peq" }, f, h("button", { class: "prm-btn", type: "button", onclick: () => enviar("complemento", { texto: f.entrada.value }, "Resposta enviada") }, "Enviar")));
      }
      if (p.pode_concluir) acoes.append(h("button", { class: "prm-btn", type: "button", onclick: () => enviar("concluir", {}, "Pedido concluído") }, "Marcar como resolvido"));
      if (p.pode_reabrir) acoes.append(h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => enviar("reabrir", {}, "Pedido reaberto") }, "Reabrir pedido"));
      main.append(acoes);
    });
  }

  // ---------------- P-7 Extrato
  function linhaExtrato(l) {
    const tempo = h("ol", { class: "prm-tempo prm-tempo--horizontal", "aria-label": "Etapas da remuneração" }, l.passos.map((p) => h("li", { class: "prm-tempo__passo", "data-estado": p.situacao, "aria-current": p.situacao === "atual" ? "step" : null },
      h("span", { class: "prm-tempo__titulo" }, p.titulo), h("span", { class: "prm-tempo__quando" }, { feito: "concluído", atual: "atual", futuro: "próximo", bloqueado: "em conferência" }[p.situacao]))));
    const det = l.detalhe ? h("dl", { class: "prm-dl" }, h("dt", null, "Base (honorário recebido pela Save)"), h("dd", null, l.detalhe.base || "—"), h("dt", null, "Percentual do seu termo"), h("dd", null, l.detalhe.percentual),
      h("dt", null, "Bruto"), h("dd", null, l.detalhe.bruto || "—"), (l.detalhe.retencoes || []).map((r) => [h("dt", null, r.nome), h("dd", null, "− " + r.valor)]),
      l.detalhe.liquido ? [h("dt", { class: "prm-dl__total" }, "Líquido"), h("dd", { class: "prm-dl__total" }, l.detalhe.liquido)] : null, l.detalhe.nf ? [h("dt", null, "Nota fiscal"), h("dd", null, l.detalhe.nf)] : null) : null;
    return h("article", { class: "prm-cartao prm-extrato__linha" }, h("div", { class: "prm-extrato__cab" }, h("h3", { class: "prm-titulo-secao" }, l.empresa), chip(l.rotulo, l.chip)),
      l.valor ? h("div", { class: "prm-extrato__valor", "aria-label": "Valor: " + l.valor }, l.valor) : h("div", { class: "prm-extrato__sem-valor" }, "Sem valor nesta etapa."),
      h("p", null, l.mensagem), tempo, det,
      l.pode_contestar ? h("div", null, h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => contestar(l) }, "Contestar (até " + l.contestacao_ate + ")")) : null);
  }
  function contestar(l) {
    const f = campo({ rotulo: "O que não bate", area: true, atributos: { maxlength: "800" } });
    modal({ titulo: "Contestar a linha de " + l.empresa, texto: "A parte não contestada do extrato segue o calendário normal.", corpo: f, verbo: "Enviar contestação",
      aoConfirmar: async () => { const x = await api("POST", "parceiro/extrato/" + l.ref + "/contestar", { motivo: f.entrada.value });
        if (x.st !== 200) { f.estado("erro", x.o.erro || "Não conseguimos enviar."); return false; }
        toast(x.o.fora_da_janela ? "Pedido de remuneração aberto" : "Contestação recebida", x.o.mensagem || ""); navegar(); } });
  }
  async function vExtrato(main) {
    await carregar(main, "parceiro/extrato", (o) => {
      cab(main, "Extrato", "Previsto quer dizer contrato assinado, ainda sem pagamento do cliente. A remuneração só é calculada depois que a Save recebe o honorário.");
      main.append(h("div", { class: "prm-extrato__resumo", role: "group", "aria-label": "Resumo" },
        h("div", { class: "prm-kpi" }, h("span", { class: "prm-rotulo" }, "Pago no ano"), h("span", { class: "prm-kpi__valor" }, o.resumo.pago_no_ano)),
        h("div", { class: "prm-kpi" }, h("span", { class: "prm-rotulo" }, "Liberado, aguardando sua NF"), h("span", { class: "prm-kpi__valor" }, o.resumo.liberado_aguardando_nf)),
        h("div", { class: "prm-kpi" }, h("span", { class: "prm-rotulo" }, "Em conferência"), h("span", { class: "prm-kpi__valor" }, String(o.resumo.em_conferencia_linhas)), h("span", { class: "prm-kpi__apoio" }, "linhas"))));
      if (o.aviso_fonte) main.append(h("div", { class: "prm-aviso prm-aviso--info" }, icone("info"), h("div", null, "Os valores aparecem conforme os recebimentos forem confirmados pelo Financeiro da Save.")));
      main.append(apoio("Em conferência contratual: o time da Save está conferindo esta linha com o contrato. Avisamos aqui quando terminar."));
      main.append(o.linhas.length ? h("div", { class: "prm-pilha" }, o.linhas.map(linhaExtrato))
        : h("div", { class: "prm-vazio" }, h("p", null, "Ainda não há linhas no seu extrato. Elas aparecem quando um contrato de empresa indicada por você é assinado.")));
    });
  }

  async function vNivel(main) {
    await carregar(main, "parceiro/nivel", (o) => {
      cab(main, "Nível e jornada", null);
      main.append(h("div", { class: "prm-pilha" }, h("div", { class: "prm-aviso prm-aviso--marca" }, icone("info"), h("div", null, h("span", { class: "prm-selo" }, o.selo), " ", o.aviso)),
        h("section", { class: "prm-cartao", "aria-labelledby": "t-j" }, h("h2", { id: "t-j" }, "Sua jornada"), h("ol", { class: "prm-passos" }, o.jornada.map((p) => h("li", { class: "prm-passos__item", "data-estado": p.situacao, "aria-current": p.situacao === "atual" ? "step" : null }, p.titulo)))),
        o.equipe ? h("section", { class: "prm-cartao", "aria-labelledby": "t-e" }, h("h2", { id: "t-e" }, "Sua equipe"), o.equipe.length ? h("ul", { class: "prm-lista" }, o.equipe.map((u) => h("li", { class: "prm-lista__item" }, h("span", null, u.nome), chip(u.etapa, "neutro")))) : apoio("Nenhum consultor cadastrado.")) : null));
    });
  }

  async function vBiblioteca(main) {
    await carregar(main, "parceiro/biblioteca", (o) => {
      cab(main, "Biblioteca e Academia", "Materiais aprovados para a conversa com a empresa.");
      main.append(h("div", { class: "prm-aviso prm-aviso--info" }, icone("info"), h("div", null, o.aviso_cobranded)),
        h("h2", { class: "prm-titulo-secao" }, "Produtos prontos"), h("div", { class: "prm-grade prm-grade--3" }, o.prontos.map((p) => h("article", { class: "prm-cartao" }, h("h3", { class: "prm-titulo-secao" }, p.nome), h("p", null, p.texto)))),
        h("h2", { class: "prm-titulo-secao" }, "Em descoberta"), h("div", { class: "prm-grade prm-grade--3" }, o.descoberta.map((p) => h("article", { class: "prm-cartao prm-pilha--peq" }, h("span", { class: "prm-selo" }, "Em descoberta"),
          h("h3", { class: "prm-titulo-secao" }, p.nome), h("p", null, p.texto), h("a", { class: "prm-btn prm-btn--sec", href: "#/pedidos/novo" }, "Registrar interesse")))));
    });
  }

  function vAjuda(main) {
    cab(main, "Ajuda e glossário", null);
    const g = [["A empresa toda (matriz e filiais)", "O registro vale para a empresa inteira, não só para um estabelecimento."],
      ["Data e hora do registro", "É o que vale para saber quem registrou primeiro."], ["Proteção temporária da indicação", "O registro protege a sua indicação por um prazo. Não cria exclusividade sobre a empresa."],
      ["Previsto", "Contrato assinado, ainda sem pagamento do cliente. Não tem valor definido."], ["Em conferência contratual", "O time da Save está conferindo a linha com o contrato."],
      ["Em teste", "O programa de níveis está em definição; o que aparece é uma simulação."]];
    main.append(h("section", { class: "prm-cartao" }, h("h2", null, "Glossário"), h("dl", { class: "prm-dl prm-dl--esq" }, g.map(([t, d]) => [h("dt", null, t), h("dd", null, d)]))),
      h("section", { class: "prm-cartao" }, h("h2", null, "Como funciona o registro"), h("p", null, "Você digita o CNPJ, confere os dados da Receita e conta como conhece a empresa. O time da Save analisa e responde aqui. A proteção começa quando o registro é aprovado.")),
      h("section", { class: "prm-cartao" }, h("h2", null, "Como ler o extrato"), h("p", null, "A remuneração nasce de cada recebimento do honorário pela Save. Antes disso, a linha aparece como prevista, sem valor.")));
  }

  function vMais(main) {
    cab(main, "Mais", null);
    main.append(h("nav", { "aria-label": "Mais", class: "prm-cartao" }, h("ul", { class: "prm-lista" }, MAIS_P.map(([k, n]) => h("li", { class: "prm-lista__item" }, h("a", { class: "prm-lista__link", href: "#/" + k }, n))))));
  }

  // ================================================================== FACE DA SAVE (seção Canal, modo escuro)
  function tabela(caption, colunas, linhas, aoClicar, ativa) {
    const t = h("div", { class: "prm-tabela prm-tabela--vira-lista" }, h("table", null, h("caption", { class: "prm-so-leitor" }, caption),
      h("thead", null, h("tr", null, colunas.map((c) => h("th", { scope: "col", class: c.num ? "num" : null }, c.t)))),
      h("tbody", null, linhas.map((l) => h("tr", { class: ativa && ativa(l) ? "prm-ativa" : null }, colunas.map((c, i) => h("td", { class: c.num ? "num" : null },
        i === 0 && aoClicar ? h("button", { class: "prm-btn prm-btn--texto", type: "button", onclick: () => aoClicar(l) }, c.v(l)) : c.v(l))))))));
    const lista = h("ul", { class: "prm-lista prm-so-celular prm-cartao", "aria-label": caption }, linhas.map((l) => h("li", { class: "prm-lista__item" },
      h("div", null, h("div", { class: "prm-lista__titulo" }, colunas[0].v(l)), colunas.slice(1).map((c) => h("div", { class: "prm-lista__apoio" }, c.t + ": ", c.v(l)))),
      aoClicar ? h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => aoClicar(l) }, "Abrir") : null)));
    return [t, lista];
  }
  const CHECAGEM = { livre: ["Livre", "ok"], proprio_usuario: ["Já é do parceiro", "info"], proprio_escritorio: ["Já é do escritório", "info"], outro_parceiro: ["Outro canal", "atencao"],
    cliente_save: ["Cliente da Save", "atencao"], indice_ausente: ["Índice indisponível", "erro"] };
  const decidir = (c) => api("POST", "save/decidir", c);
  const confirmarDecisao = (titulo, texto, corpo, verbo, perigo, montar) => modal({ titulo, texto, corpo, verbo, perigo, aoConfirmar: async () => {
    const c = montar(); if (!c) return false;
    const r = await decidir(c); if (r.st !== 200) throw new Error(r.o.erro || "Não conseguimos concluir.");
    toast("Feito", "Decisão registrada na trilha (" + r.o.trilha + ")."); navegar(); } });

  function sMais(main) {
    cab(main, "Canal", null);
    main.append(h("nav", { "aria-label": "Canal", class: "prm-cartao" }, h("ul", { class: "prm-lista" }, MENU_S.map(([k, n]) => h("li", { class: "prm-lista__item" }, h("a", { class: "prm-lista__link", href: "#/" + k }, n))))));
  }

  async function sCanal(main) {
    await carregar(main, "save/canal", (o) => {
      cab(main, "Visão do canal", "Saúde do canal e filas de ação. Nada desta tela vai ao parceiro.", S.eu.papel === "luis" ? [h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: async () => {
        const r = await api("POST", "save/rotina", {}); if (r.st === 200) { toast("Rotina diária executada", "Registros, negócios e pedidos conferidos."); navegar(); } else toast("Rotina", r.o.erro || "", "atencao"); } }, "Rodar rotina diária agora")] : null, "Canal");
      main.append(h("section", { "aria-label": "Indicadores" }, h("div", { class: "prm-grade prm-grade--kpi" }, o.kpis.map((k) => h("a", { class: "prm-cartao prm-kpi prm-kpi-link", href: "#/" + k.go },
        h("span", { class: "prm-rotulo" }, k.rotulo), h("span", { class: "prm-kpi__valor" }, String(k.valor)), h("span", { class: "prm-kpi__apoio" }, k.apoio))))));
      main.append(h("section", { class: "prm-cartao", "aria-labelledby": "t-al" }, h("h2", { id: "t-al" }, "Alertas"), o.alertas.length ? h("ul", { class: "prm-lista" }, o.alertas.map((a) => h("li", { class: "prm-lista__item" },
        h("div", null, h("div", { class: "prm-lista__titulo" }, a.assunto), h("div", { class: "prm-lista__apoio" }, a.resumo)), a.prioridade === "alta" ? chip("Alta", "erro") : chip("Normal", "neutro")))) : apoio("Nenhum alerta aberto.")));
      const [t, l] = tabela("Saúde por parceiro", [{ t: "Parceiro", v: (s) => s.nome }, { t: "Abertos", v: (s) => String(s.abertos), num: true }, { t: "Ganhos 12 m", v: (s) => String(s.ganhos_12m), num: true },
        { t: "Registros vivos", v: (s) => String(s.registros_vivos), num: true }, { t: "Leitura", v: (s) => s.leitura }, { t: "Ação sugerida", v: (s) => s.acao }], o.saude);
      main.append(h("section", { "aria-labelledby": "t-sa", class: "prm-pilha--peq" }, h("h2", { id: "t-sa", class: "prm-titulo-secao" }, "Saúde por parceiro"), t, l),
        h("section", { class: "prm-cartao", "aria-labelledby": "t-co" }, h("h2", { id: "t-co" }, "Concentração (crédito ganho em 12 meses, sem café)"),
          h("dl", { class: "prm-dl" }, h("dt", null, "Maior Master"), h("dd", null, o.concentracao.top1_pct === null ? "—" : o.concentracao.top1_pct + "%"), h("dt", null, "5 maiores"), h("dd", null, o.concentracao.top5_pct === null ? "—" : o.concentracao.top5_pct + "%")),
          apoio("Métrica de guarda, sem meta.")));
    }, 4);
  }

  async function sRegistros(main, id, params) {
    await carregar(main, "save/registros", (o) => {
      cab(main, "Registros", "Fila por ordem de chegada. A checagem real aparece só aqui; o parceiro vê sempre “Registro recebido · em análise”.", null, "Canal");
      const fila = o.itens.filter((r) => ["em_analise", "aguardando_parceiro", "em_conflito"].includes(r.estado) || r.pedido_prorrogacao);
      const outros = o.itens.filter((r) => !fila.includes(r));
      const detalhe = h("div", { "aria-live": "polite" });
      const abrir = (r) => { location.hash = "#/canal/registros/" + r.registro_id; };
      const col = [{ t: "Registro", v: (r) => r.registro_id }, { t: "Parceiro", v: (r) => r.parceiro || r.parceiro_id }, { t: "Empresa", v: (r) => r.razao_social || "" },
        { t: "Checagem", v: (r) => chip(...(CHECAGEM[r.checagem] || [r.checagem || "—", "neutro"])) }, { t: "Estado", v: (r) => r.estado.replace(/_/g, " ") }, { t: "Data e hora", v: (r) => r.carimbo }];
      const [t1, l1] = tabela("Registros esperando decisão", col, fila, abrir, (r) => r.registro_id === id);
      const [t2, l2] = tabela("Demais registros", col, outros, abrir, (r) => r.registro_id === id);
      main.append(h("div", { class: "prm-duas" }, h("div", { class: "prm-pilha" }, h("section", { class: "prm-pilha--peq" }, h("h2", { class: "prm-titulo-secao" }, "Esperando decisão (" + fila.length + ")"),
        fila.length ? [t1, l1] : h("div", { class: "prm-vazio" }, h("p", null, "Nenhum registro esperando decisão."))),
        h("details", { class: "prm-detalhe" }, h("summary", null, "Demais registros (" + outros.length + ")"), t2, l2), formEmNome(o)), detalhe));
      const r = id && o.itens.find((x) => x.registro_id === id);
      if (r) detalheRegistro(detalhe, r, o.motivos);
      else detalhe.append(h("div", { class: "prm-vazio" }, h("p", null, "Escolha um registro para ver os fatos e decidir.")));
    }, 3);
  }

  function detalheRegistro(alvo, r, motivos) {
    const titulo = h("h2", { tabindex: "-1" }, r.registro_id + " · " + (r.razao_social || ""));
    const acoes = h("div", { class: "prm-acoes prm-acoes--empilha" });
    const vivo = r.estado === "em_analise";
    if (vivo) {
      const ap = h("button", { class: "prm-btn", type: "button", "aria-disabled": r.pode_decidir_agora ? null : "true" }, "Aprovar");
      ap.addEventListener("click", () => {
        if (!r.pode_decidir_agora) return toast("Ainda não", "A decisão só pode sair depois do tempo mínimo de análise.", "atencao");
        const chk = r.checagem === "cliente_save" || r.checagem === "indice_ausente" ? checkbox(uid("mp"), "O negócio existente é do mesmo parceiro, com cadastro incompleto (vou corrigir pela higiene do CRM).") : null;
        confirmarDecisao("Aprovar o registro " + r.registro_id + "?", "A proteção vale até " + (r.valido_se_aprovar || "a data do tipo de parceiro") + ". O card no HubSpot continua pelo fluxo atual.", chk, "Aprovar", false,
          () => ({ objeto: "registro", id: r.registro_id, decisao: "aprovar", mesmo_parceiro_cadastro_incompleto: chk ? chk.entrada.checked : undefined }));
      });
      const recusar = h("button", { class: "prm-btn prm-btn--perigo", type: "button", onclick: () => {
        const f = campo({ rotulo: "Motivo que o parceiro vai ver", opcoes: motivos.map((m) => [String(m.n), m.texto]), valor: "4" });
        const prev = h("p", { class: "prm-texto-apoio" }, "Para outro canal ou cliente da Save, o motivo é sempre o genérico (PRM-R23).");
        confirmarDecisao("Não aprovar o registro " + r.registro_id + "?", "O parceiro recebe o texto M-11 com o motivo escolhido.", h("div", null, f, prev), "Não aprovar", true,
          () => ({ objeto: "registro", id: r.registro_id, decisao: "nao_aprovar", motivo: Number(f.entrada.value || 4) }));
      } }, "Não aprovar");
      const conf = h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => confirmarDecisao("Enviar " + r.registro_id + " a conflito?", "A validade fica pausada e o Luis decide em até 10 d.u. Nenhum parceiro é avisado do outro.", null, "Enviar a conflito", false,
        () => ({ objeto: "registro", id: r.registro_id, decisao: "enviar_conflito" })) }, "Enviar a conflito");
      const pergunta = h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => {
        const f = campo({ rotulo: "Pergunta ao parceiro", area: true, atributos: { maxlength: "300" } });
        confirmarDecisao("Pedir esclarecimento", "O parceiro tem 3 d.u. para responder e manter a data e a hora do registro.", f, "Enviar pergunta", false,
          () => ({ objeto: "registro", id: r.registro_id, decisao: "pedir_complemento", pergunta: f.entrada.value }));
      } }, "Pedir esclarecimento");
      acoes.append(ap, recusar, conf, pergunta);
      if (!r.pode_decidir_agora) acoes.append(h("p", { class: "prm-texto-apoio" }, "Decisão liberada a partir do tempo mínimo de análise (4 horas úteis)."));
    }
    if (r.pedido_prorrogacao) {
      acoes.append(h("p", null, "Pedido de prorrogação: " + r.pedido_prorrogacao.fato),
        h("button", { class: "prm-btn", type: "button", onclick: () => confirmarDecisao("Prorrogar " + r.registro_id + "?", "Mais 60 dias, uma vez.", null, "Prorrogar", false, () => ({ objeto: "registro", id: r.registro_id, decisao: "prorrogar" })) }, "Prorrogar"),
        h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => confirmarDecisao("Negar a prorrogação?", null, null, "Negar", true, () => ({ objeto: "registro", id: r.registro_id, decisao: "negar_prorrogacao" })) }, "Negar"));
    }
    const hist = r.historico_raiz;
    alvo.append(h("section", { class: "prm-cartao prm-pilha--peq", "aria-labelledby": titulo.id || null }, titulo,
      h("div", { class: "prm-linha" }, chip(...(CHECAGEM[r.checagem] || [r.checagem || "—", "neutro"])), chip(r.estado.replace(/_/g, " "), "neutro"), (r.flags || []).map((f) => chip(f, "erro"))),
      h("dl", { class: "prm-dl prm-dl--esq" }, h("dt", null, "CNPJ"), h("dd", { class: "prm-mono" }, r.cnpj_mascara), h("dt", null, "Parceiro"), h("dd", null, r.parceiro_id),
        h("dt", null, "Canal"), h("dd", null, r.canal_entrada + " (" + r.carimbo_origem + ")"), h("dt", null, "Data e hora"), h("dd", null, r.carimbo),
        h("dt", null, "Decisor"), h("dd", null, r.contato_cargo || ""), h("dt", null, "Como conhece"), h("dd", null, r.como_conhece || ""), h("dt", null, "Evidência"), h("dd", null, (r.evidencia || "") + (r.evidencia_nota ? " · " + r.evidencia_nota : "")),
        r.conflito_id ? [h("dt", null, "Conflito"), h("dd", null, h("a", { href: "#/canal/conflitos" }, r.conflito_id))] : null),
      h("h3", { class: "prm-titulo-secao" }, "Histórico da raiz"),
      h("ul", { class: "prm-lista" }, hist.registros.map((x) => h("li", { class: "prm-lista__item" }, h("span", null, x.registro_id + " · " + x.parceiro_id + " · " + x.estado), h("span", { class: "prm-mono" }, (x.carimbo || "").slice(0, 10)))),
        hist.negocios.map((n) => h("li", { class: "prm-lista__item" }, h("span", null, "Negócio " + n.deal_id + " · " + (n.escritorio || "sem parceiro") + " · " + n.etapa), chip(n.status, n.status === "ganho" ? "ok" : "info")))),
      acoes));
    titulo.focus();
  }

  function formEmNome(o) {
    const sec = h("details", { class: "prm-detalhe" }, h("summary", null, "Registrar em nome do parceiro (Fase 1, pelo WhatsApp)"));
    const fPar = campo({ rotulo: "Parceiro", opcoes: o.parceiros.map((p) => [p.id, p.nome + " (" + p.tipo + ")"]) });
    const fCnpj = campo({ rotulo: "CNPJ", mono: true, atributos: { autocapitalize: "characters", autocomplete: "off" } });
    const fRazao = campo({ rotulo: "Razão social" }); const fNome = campo({ rotulo: "Nome do decisor" }); const fCargo = campo({ rotulo: "Cargo do decisor" });
    const fEmail = campo({ rotulo: "E-mail corporativo", tipo: "email" }); const fInt = campo({ rotulo: "Interesse", opcoes: INTERESSES }); const fComo = campo({ rotulo: "Como conhece", opcoes: COMO });
    const fEvid = campo({ rotulo: "Evidência", opcoes: EVID, valor: "declaracao" });
    const fHora = campo({ rotulo: "Hora da mensagem completa no WhatsApp", tipo: "datetime-local", dica: "É o carimbo do registro na Fase 1." });
    const lg = checkbox(uid("lg"), "O parceiro declarou ter autorização ou base legal para compartilhar o contato.");
    const btn = h("button", { class: "prm-btn", type: "submit" }, "Registrar");
    const res = h("div", { "aria-live": "polite" });
    const form = h("form", { class: "prm-form", novalidate: true }, fPar, fCnpj, fRazao, h("div", { class: "prm-campos" }, fNome, fCargo), fEmail, h("div", { class: "prm-campos" }, fInt, fComo), fEvid, fHora, lg, h("div", null, btn), res);
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      btn.setAttribute("aria-busy", "true");
      const { st, o: r } = await api("POST", "save/registros", { em_nome_de: { parceiro_id: fPar.entrada.value }, cnpj: normCnpj(fCnpj.entrada.value), razao_social: fRazao.entrada.value,
        contato_nome: fNome.entrada.value, contato_cargo: fCargo.entrada.value, contato_email: fEmail.entrada.value, interesse: fInt.entrada.value, como_conhece: fComo.entrada.value,
        evidencia_tipo: fEvid.entrada.value, declaracao_lgpd: lg.entrada.checked, carimbo_whatsapp: fHora.entrada.value ? fHora.entrada.value + ":00-03:00" : undefined });
      btn.removeAttribute("aria-busy");
      limpar(res);
      if (st === 201 || st === 200) { res.append(h("div", { class: "prm-resultado prm-resultado--recebido" }, h("h3", null, r.titulo), h("p", null, r.mensagem))); form.reset(); }
      else { aplicarErros({ cnpj: fCnpj, razao_social: fRazao, contato_nome: fNome, contato_cargo: fCargo, contato_email: fEmail, interesse: fInt, como_conhece: fComo, evidencia_tipo: fEvid, parceiro_id: fPar }, r.campos || {});
        res.append(h("div", { class: "prm-aviso prm-aviso--erro", role: "alert" }, icone("alerta"), h("div", null, r.erro || "Não foi possível registrar."))); }
    });
    sec.append(form);
    return sec;
  }

  async function sConflitos(main) {
    await carregar(main, "save/conflitos", (o) => {
      cab(main, "Conflitos", "Fatos para o Luis decidir (R15). O sistema não atribui o cliente.", null, "Canal");
      if (!o.itens.length) { main.append(h("div", { class: "prm-vazio" }, h("p", null, "Nenhum conflito aberto."))); return; }
      main.append(h("div", { class: "prm-pilha" }, o.itens.map((c) => {
        const sel = c.pode_decidir ? campo({ rotulo: "Registro vencedor", opcoes: c.registros_det.map((r) => [r.registro_id, r.registro_id + " · " + r.parceiro_id]) }) : null;
        return h("article", { class: "prm-cartao prm-pilha--peq" }, h("div", { class: "prm-linha prm-linha--entre" }, h("h2", { class: "prm-titulo-secao" }, c.conflito_id + " · " + c.cnpj_mascara),
          h("div", { class: "prm-linha" }, chip("Severidade " + c.severidade, c.severidade === "alta" ? "erro" : "atencao"), chip(c.estado, c.estado === "aberto" ? "acao" : "ok"))),
          h("p", null, "Partes: " + c.partes_nomes.join(" × ")), apoio(c.regra), apoio("Prazo: " + new Date(c.prazo).toLocaleDateString("pt-BR")),
          h("ul", { class: "prm-lista" }, c.fatos.registros.map((x) => h("li", { class: "prm-lista__item" }, h("span", null, "Registro " + x.registro_id + " · " + x.parceiro_id + " · " + x.estado + " · " + (x.evidencia_tipo || "")), h("span", { class: "prm-mono" }, (x.carimbo || "").slice(0, 16)))),
            c.fatos.negocios.map((n) => h("li", { class: "prm-lista__item" }, h("span", null, "Negócio " + n.deal_id + " · " + (n.escritorio || "sem parceiro") + " · " + n.etapa + " · criado " + (n.criado_em || "")), chip(n.status, "info")))),
          c.pode_decidir ? h("div", { class: "prm-pilha--peq" }, sel, h("div", { class: "prm-acoes prm-acoes--empilha" },
            h("button", { class: "prm-btn", type: "button", onclick: () => confirmarDecisao("Decidir o conflito " + c.conflito_id + "?", "O registro escolhido fica com a empresa; os demais recebem o motivo genérico.", null, "Registrar decisão", false,
              () => sel.entrada.value ? { objeto: "conflito", id: c.conflito_id, decisao: "decidir", vencedor: sel.entrada.value, tipo_decisao: "primeiro_registro" } : (sel.estado("erro", "Escolha o vencedor."), null)) }, "Registrar decisão"),
            h("button", { class: "prm-btn prm-btn--perigo", type: "button", onclick: () => confirmarDecisao("Venda direta da Save?", "Todos os registros desta raiz são recusados com o motivo genérico.", null, "Confirmar", true,
              () => ({ objeto: "conflito", id: c.conflito_id, decisao: "decidir", tipo_decisao: "save_direto" })) }, "Save direto"))) : apoio(c.estado === "aberto" ? "Só o perfil Luis registra a decisão." : "Decidido por " + c.decidido_por));
      })));
    });
  }

  async function sDemandas(main, id) {
    await carregar(main, "save/demandas", (o) => {
      cab(main, "Demandas", "Fila única por prazo: portal e registro único (WhatsApp, e-mail). Histórico antes do chamado; o GLPI só recebe o que for aprovado.", null, "Canal");
      const det = h("div", { "aria-live": "polite" });
      const col = [{ t: "Pedido", v: (d) => d.id }, { t: "Parceiro", v: (d) => d.parceiro_id }, { t: "Tipo", v: (d) => d.tipo }, { t: "Origem", v: (d) => d.origem },
        { t: "Prazo", v: (d) => chip(d.sla.texto, d.sla.chip) }, { t: "Caminho", v: (d) => d.estado === "resposta_historico" ? "Histórico" : d.chamado ? "Chamado (" + d.chamado.estado + ")" : d.rotulo }];
      const [t, l] = tabela("Pedidos do portal por prazo", col, o.itens, (d) => { location.hash = "#/canal/demandas/" + d.id; }, (d) => d.id === id);
      const outras = o.registro_unico.length ? h("details", { class: "prm-detalhe" }, h("summary", null, "Registro único (WhatsApp e e-mail): " + o.registro_unico.length),
        h("ul", { class: "prm-lista" }, o.registro_unico.map((d) => h("li", { class: "prm-lista__item" }, h("span", null, d.id + " · " + d.origem + " · " + d.tipo), chip(d.estado, "neutro"))))) : null;
      main.append(h("div", { class: "prm-duas" }, h("div", { class: "prm-pilha" }, o.itens.length ? [t, l] : h("div", { class: "prm-vazio" }, h("p", null, "Nenhuma demanda aberta.")), outras), det));
      const d = id && o.itens.find((x) => x.id === id);
      if (!d) { det.append(h("div", { class: "prm-vazio" }, h("p", null, "Escolha um pedido para ver a sugestão do histórico ou o chamado em rascunho."))); return; }
      const titulo = h("h2", { tabindex: "-1" }, d.id + " · " + d.tipo);
      const bloco = h("section", { class: "prm-cartao prm-pilha--peq" }, titulo, h("div", { class: "prm-linha" }, chip(d.sla.texto, d.sla.chip), chip(d.estado.replace(/_/g, " "), "neutro"), d.urgente ? chip("Urgente", "erro") : null),
        h("ol", { class: "prm-conversa" }, d.mensagens.map((m) => h("li", { class: "prm-msg prm-msg--" + (m.de === "parceiro" ? "parceiro" : "save") }, h("p", null, m.texto), h("div", { class: "prm-msg__meta" }, m.quando + (m.selo ? " · " + m.selo : ""))))));
      const fechado = ["respondida", "concluida"].includes(d.estado);
      if (d.historico) bloco.append(h("h3", { class: "prm-titulo-secao" }, "Histórico (" + (d.historico.suficiente ? "tem resposta, confiança " + d.historico.confianca : "sem resposta suficiente") + ")"),
        d.historico.faltou ? apoio("O que faltou: " + d.historico.faltou) : null, h("ul", { class: "prm-lista" }, (d.historico.fontes || []).map((f) => h("li", { class: "prm-lista__item" }, h("span", null, f.trecho), h("span", { class: "prm-mono" }, f.data || "")))));
      if (!fechado) {
        const resp = campo({ rotulo: "Resposta ao parceiro", area: true, valor: (d.historico && d.historico.rascunho) || "", dica: "Passa pelo auditor de promessas antes de sair." });
        const msg = h("p", { class: "prm-texto-apoio", "aria-live": "polite" });
        const enviar = h("button", { class: "prm-btn", type: "button", onclick: async () => {
          enviar.setAttribute("aria-busy", "true");
          const r = await decidir({ objeto: "demanda", id: d.id, decisao: "aprovar_envio", texto: resp.entrada.value, editada: d.historico && resp.entrada.value !== d.historico.rascunho });
          enviar.removeAttribute("aria-busy");
          if (r.st === 200) { toast("Resposta enviada", ""); navegar(); } else { resp.estado("erro", r.o.erro); msg.textContent = r.o.erro || ""; }
        } }, "Aprovar e enviar");
        const dados = h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => { const f = campo({ rotulo: "O que falta", area: true });
          confirmarDecisao("Pedir dados ao parceiro", "O relógio do prazo para enquanto o parceiro não responde.", f, "Pedir", false, () => ({ objeto: "demanda", id: d.id, decisao: "pedir_dados", itens: f.entrada.value })); } }, "Pedir dados");
        bloco.append(resp, msg, h("div", { class: "prm-acoes prm-acoes--empilha" }, enviar, dados));
        if (d.chamado && d.chamado.estado === "rascunho") {
          const ft = campo({ rotulo: "Título do chamado", valor: d.chamado.titulo }); const fd = campo({ rotulo: "Descrição", area: true, valor: d.chamado.descricao });
          bloco.append(h("h3", { class: "prm-titulo-secao" }, "Chamado sugerido (rascunho · área " + d.chamado.area + ")"), ft, fd,
            h("div", { class: "prm-acoes prm-acoes--empilha" }, h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => confirmarDecisao("Aprovar o chamado?", "O PRM registra a aprovação e marca para abrir manualmente no GLPI (o sistema não escreve no GLPI).", null, "Aprovar chamado", false,
              () => ({ objeto: "demanda", id: d.id, decisao: "encaminhar", titulo: ft.entrada.value, descricao: fd.entrada.value })) }, "Aprovar chamado (abrir no GLPI)"),
              h("button", { class: "prm-btn prm-btn--perigo", type: "button", onclick: () => { const f = campo({ rotulo: "Motivo", area: true }); confirmarDecisao("Recusar o chamado sugerido?", null, f, "Recusar", true, () => ({ objeto: "demanda", id: d.id, decisao: "recusar_chamado", motivo: f.entrada.value })); } }, "Recusar chamado")));
        } else if (d.chamado) bloco.append(apoio("Chamado: " + d.chamado.estado + (d.chamado.glpi === "abrir_manualmente" ? " · abrir manualmente no GLPI" : "")));
      }
      det.append(bloco);
      titulo.focus();
    }, 3);
  }

  async function sExtratos(main) {
    await carregar(main, "save/extratos", (o) => {
      cab(main, "Extratos", "Libera só o recebido e conferido. Quem registra o recebimento não aprova o extrato da mesma competência.", o.pode_agir ? [h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: async () => {
        const r = await decidir({ objeto: "extrato", id: "mes", decisao: "calcular" }); if (r.st === 200) { toast("Cálculo do mês", r.o.objeto.calculadas + " linha(s) calculada(s)."); navegar(); } else toast("Cálculo", r.o.erro, "atencao"); } }, "Calcular o mês")] : null, "Canal");
      main.append(h("h2", { class: "prm-titulo-secao" }, "Lotes"), o.lotes.length ? h("div", { class: "prm-grade prm-grade--2" }, o.lotes.map((l) => {
        const motivoId = uid("mot");
        return h("article", { class: "prm-cartao prm-pilha--peq" }, h("h3", { class: "prm-titulo-secao" }, (l.parceiro || l.parceiro_id) + " · " + l.competencia),
          apoio(l.calculadas + " calculada(s) de " + l.linhas + " · bruto " + l.bruto + " · liberadas " + l.liberadas),
          h("ul", { class: "prm-lista" }, l.checklist.map((c) => h("li", { class: "prm-lista__item" }, h("span", null, c.item), chip(c.ok ? "Ok" : "Pendente", c.ok ? "ok" : "erro"), h("span", { class: "prm-texto-apoio" }, c.texto)))),
          o.pode_agir ? h("div", null, h("button", { class: "prm-btn", type: "button", "aria-disabled": l.pode_liberar ? null : "true", "aria-describedby": motivoId, onclick: () => {
            if (!l.pode_liberar) return;
            confirmarDecisao("Liberar o lote de " + (l.parceiro || "") + "?", "As linhas calculadas vão ao parceiro com o prazo de NF e a janela de contestação de 10 dias.", null, "Liberar lote", false, () => ({ objeto: "extrato_lote", id: l.lote, decisao: "liberar" }));
          } }, "Liberar lote"), h("p", { class: "prm-texto-apoio", id: motivoId }, l.motivo_bloqueio || "")) : null);
      })) : h("div", { class: "prm-vazio" }, h("p", null, "Nenhum lote neste mês.")));
      if (o.pode_agir) {
        const linhasRec = o.linhas.filter((x) => x.estado === "previsto");
        main.append(h("h2", { class: "prm-titulo-secao" }, "Registrar recebimento"), linhasRec.length ? h("ul", { class: "prm-lista prm-cartao" }, linhasRec.map((x) => h("li", { class: "prm-lista__item" },
          h("span", null, x.linha_id + " · " + (x.parceiro || "")), h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => {
            const v = campo({ rotulo: "Valor recebido (R$)", tipo: "number", atributos: { step: "0.01", min: "0" } }); const c = campo({ rotulo: "Competência", tipo: "month" });
            confirmarDecisao("Registrar recebimento", "Recebimento da parcela do honorário (inclui compensação de ofício).", h("div", null, v, c), "Registrar", false,
              () => ({ objeto: "extrato_linha", id: x.linha_id, decisao: "registrar_recebimento", valor: Number(v.entrada.value), competencia: c.entrada.value }));
          } }, "Registrar recebimento")))) : apoio("Nenhuma linha prevista."),
        h("h2", { class: "prm-titulo-secao" }, "Aguardando NF"), o.aguardando_nf.length ? h("ul", { class: "prm-lista prm-cartao" }, o.aguardando_nf.map((x) => h("li", { class: "prm-lista__item" },
          h("span", null, x.linha_id + " · " + (x.parceiro || "") + " · " + x.bruto), h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => {
            const n = campo({ rotulo: "Número da NF" });
            confirmarDecisao("Registrar pagamento", "Com a NF conferida. O IRRF é retido conforme o parâmetro vigente.", n, "Registrar pagamento", false, () => ({ objeto: "extrato_linha", id: x.linha_id, decisao: "registrar_pagamento", nf: n.entrada.value }));
          } }, "Registrar pagamento")))) : apoio("Nenhuma linha aguardando NF."));
      }
      main.append(h("h2", { class: "prm-titulo-secao" }, "Contestações"), o.contestacoes.length ? h("div", { class: "prm-pilha" }, o.contestacoes.map((c) => h("article", { class: "prm-cartao prm-pilha--peq" },
        h("h3", { class: "prm-titulo-secao" }, c.contestacao_id + " · " + (c.parceiro || "")), h("p", null, c.motivo), apoio("Responder até " + new Date(c.resposta_ate).toLocaleDateString("pt-BR")),
        o.pode_agir ? h("div", { class: "prm-acoes prm-acoes--empilha" }, ["procedente", "improcedente"].map((d) => h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => {
          const causa = campo({ rotulo: "Causa-raiz", opcoes: [["cadastro", "Cadastro"], ["percentual", "Percentual"], ["duplicidade", "Duplicidade"], ["recebimento", "Recebimento"], ["retencao", "Retenção"], ["conflito", "Conflito"]] });
          const ex = campo({ rotulo: "Explicação ao parceiro", area: true, dica: "Passa pelo auditor de promessas." });
          confirmarDecisao("Contestação " + d, null, h("div", null, causa, ex), "Responder", d === "improcedente", () => ({ objeto: "contestacao", id: c.contestacao_id, decisao: d, causa_raiz: causa.entrada.value, explicacao: ex.entrada.value }));
        } }, d === "procedente" ? "Procedente" : "Improcedente"))) : null))) : apoio("Nenhuma contestação aberta."));
    });
  }

  async function sDossies(main) {
    await carregar(main, "save/dossies", (o) => {
      cab(main, "Dossiês e esteira", "Dossiê-base na hora; o parceiro só vê depois da aprovação e do auditor de promessas.", null, "Canal");
      if (!o.itens.length) { main.append(h("div", { class: "prm-vazio" }, h("p", null, "Nenhum dossiê pedido."))); return; }
      main.append(h("div", { class: "prm-pilha" }, o.itens.map((d) => h("article", { class: "prm-cartao prm-pilha--peq" }, h("div", { class: "prm-linha prm-linha--entre" },
        h("h2", { class: "prm-titulo-secao" }, d.id + " · " + (d.empresa || "")), chip(d.andamento, d.status === "entregue" ? "ok" : d.status === "revisao_humana" ? "atencao" : "info")),
        apoio("Registro " + d.registro_id + " · " + d.cnpj_mascara + " · nível " + (d.nivel || "—") + " · auditoria " + (d.auditoria ? (d.auditoria.ok ? "sem alerta" : d.auditoria.alertas + " alerta(s)") : "—")),
        d.secoes.length ? apoio("Seções: " + d.secoes.join(" · ")) : null,
        d.pode_aprovar ? h("div", null, h("button", { class: "prm-btn", type: "button", onclick: () => confirmarDecisao("Aprovar e publicar " + d.id + "?", "O parceiro passa a ver o dossiê na ficha da empresa.", null, "Aprovar e publicar", false,
          () => ({ objeto: "dossie", id: d.id, decisao: "aprovar" })) }, "Aprovar e publicar")) : null))));
    });
  }

  async function sAcessos(main) {
    await carregar(main, "save/acessos", (o) => {
      cab(main, "Acessos", "Usuários do parceiro, último acesso e respostas neutras do dia (teto: " + o.teto_neutras + ").", null, "Canal");
      const [t, l] = tabela("Usuários do parceiro", [{ t: "Usuário", v: (u) => u.nome + " (" + u.usuario_id + ")" }, { t: "Escritório", v: (u) => u.parceiro || "" }, { t: "Papel", v: (u) => u.papel },
        { t: "Estado", v: (u) => chip(u.estado, u.estado === "ativo" ? "ok" : "erro") }, { t: "Último acesso", v: (u) => u.ultimo_acesso }, { t: "Neutras hoje", v: (u) => String(u.neutras_hoje), num: true },
        { t: "Ação", v: (u) => u.estado === "ativo" ? h("button", { class: "prm-btn prm-btn--perigo", type: "button", onclick: () => confirmarDecisao("Suspender o acesso de " + u.nome + "?", "O acesso cai na hora; os registros ficam com o escritório.", null, "Suspender", true, () => ({ objeto: "usuario", id: u.usuario_id, decisao: "suspender" })) }, "Suspender")
          : u.estado === "suspenso" ? h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: () => confirmarDecisao("Reativar " + u.nome + "?", null, null, "Reativar", false, () => ({ objeto: "usuario", id: u.usuario_id, decisao: "reativar" })) }, "Reativar") : "—" }], o.usuarios);
      main.append(t, l, h("h2", { class: "prm-titulo-secao" }, "Trilha de acesso (últimos 40)"));
      const [t2, l2] = tabela("Trilha de acesso", [{ t: "Quando", v: (a) => a.quando }, { t: "Quem", v: (a) => a.quem || "" }, { t: "Tela", v: (a) => a.tela }, { t: "Ação", v: (a) => a.acao }, { t: "Resultado", v: (a) => chip(a.resultado, a.resultado === "ok" ? "ok" : "atencao") }], o.trilha);
      main.append(t2, l2);
    });
  }

  async function sNiveis(main) {
    await carregar(main, "save/niveis", (o) => {
      cab(main, "Níveis (em teste)", "Leitura-sombra: só a Save vê. O parceiro vê a jornada e o selo “Em teste” até a decisão do programa (F8).", null, "Canal");
      const [t, l] = tabela("Apuração em sombra", [{ t: "Parceiro", v: (x) => x.nome }, { t: "Faixa simulada", v: (x) => x.faixa_simulada }, { t: "% do próximo", v: (x) => x.pct_do_proximo + "%", num: true }, { t: "Trimestre", v: (x) => x.trimestre }], o.itens);
      main.append(t, l);
    });
  }

  async function sParametros(main) {
    await carregar(main, "save/parametros", (o) => {
      cab(main, "Parâmetros", "Valores padrão da especificação (02 §3). Mudar não exige deploy; cada mudança fica na trilha.", null, "Canal");
      const [t, l] = tabela("Parâmetros do PRM", [{ t: "Chave", v: (p) => p.chave }, { t: "Valor", v: (p) => JSON.stringify(p.valor) }, { t: "Unidade", v: (p) => p.unidade }, { t: "Marca", v: (p) => p.marca }, { t: "Dona", v: (p) => p.quem_muda }], o.itens);
      main.append(t, l);
    });
  }

  // ================================================================== NEGÓCIOS, PAINEL DE VENDAS E DASHBOARD COMERCIAL (PRM-R113 a R118)
  // Gráficos próprios em HTML (skill dataviz): barras finas com ponta arredondada, um eixo, dica no hover e no foco, legenda quando há
  // mais de uma série, tabela alternativa em "Ver como tabela". Cor = rampa de ouro (--prm-serie-1..4) + cinza; estado nunca só por cor.
  const reais = (v) => (v === null || v === undefined ? "—" : "R$ " + new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 }).format(v));
  const reaisC = (v) => {
    if (v === null || v === undefined) return "—";
    const a = Math.abs(v);
    if (a >= 1e6) return "R$ " + (v / 1e6).toLocaleString("pt-BR", { maximumFractionDigits: 1 }) + " mi";
    if (a >= 1e3) return "R$ " + Math.round(v / 1e3).toLocaleString("pt-BR") + " mil";
    return reais(v);
  };
  const pctTxt = (v) => (v === null || v === undefined ? "—" : String(v).replace(".", ",") + "%");
  const fracTxt = (v) => (v === null || v === undefined ? "—" : (v * 100).toLocaleString("pt-BR", { maximumFractionDigits: 1 }) + "%");
  const dataBR = (iso) => { if (!iso) return "—"; const p = String(iso).slice(0, 10).split("-"); return p.length === 3 ? p[2] + "/" + p[1] + "/" + p[0] : String(iso); };
  const mono = (t) => h("span", { class: "prm-mono" }, t);
  const nTxt = (n, um, varios) => n + " " + (n === 1 ? um : varios);

  let dicaEl = null;
  function dica(alvo, texto) {
    const mostrar = (x, y) => {
      if (!dicaEl) { dicaEl = h("div", { class: "prm-dica", role: "tooltip" }); document.body.append(dicaEl); }
      dicaEl.textContent = texto; dicaEl.hidden = false;
      const r = dicaEl.getBoundingClientRect();
      dicaEl.style.left = Math.max(8, Math.min(window.innerWidth - r.width - 8, x + 12)) + "px";
      dicaEl.style.top = Math.max(8, y - r.height - 12) + "px";
    };
    const esconder = () => { if (dicaEl) dicaEl.hidden = true; };
    alvo.addEventListener("mousemove", (e) => mostrar(e.clientX, e.clientY));
    alvo.addEventListener("mouseleave", esconder);
    alvo.addEventListener("focus", () => { const r = alvo.getBoundingClientRect(); mostrar(r.left + r.width / 2, r.top); });
    alvo.addEventListener("blur", esconder);
    return alvo;
  }
  window.addEventListener("hashchange", () => { if (dicaEl) dicaEl.hidden = true; });

  function tabelaAlt(cols, linhas) {
    return h("details", { class: "prm-graf__tabela" }, h("summary", null, "Ver como tabela"),
      h("table", null, h("thead", null, h("tr", null, cols.map((c) => h("th", { scope: "col", class: c.num ? "num" : null }, c.t)))),
        h("tbody", null, linhas.map((l) => h("tr", null, cols.map((c, i) => i === 0 ? h("th", { scope: "row" }, c.v(l)) : h("td", { class: c.num ? "num" : null }, c.v(l))))))));
  }

  function legenda(series, meta) {
    return h("ul", { class: "prm-legenda", "aria-label": "Legenda" }, series.map((s) => h("li", null, h("span", { class: "prm-legenda__amostra", "data-serie": String(s.serie) }), s.rotulo)),
      meta ? h("li", null, h("span", { class: "prm-legenda__meta" }), meta) : null);
  }

  // barras horizontais; itens [{rotulo, valor (escala), texto (à direita), dica, serie, partes?[{valor, serie, rotulo}], aoClicar}]
  function barras({ titulo, apoio: ap, itens, cols, series, vazio, idTitulo }) {
    const max = Math.max(0, ...itens.map((i) => (i.partes ? i.partes.reduce((a, p) => a + (p.valor || 0), 0) : i.valor || 0)));
    const id = idTitulo || uid("graf");
    const corpo = itens.length && max > 0 ? h("div", { class: "prm-barras" }, itens.map((i) => {
      const segs = (i.partes || [{ valor: i.valor, serie: i.serie || 2 }]).filter((p) => p.valor > 0)
        .map((p) => h("span", { class: "prm-barras__barra", "data-serie": String(p.serie), estilo: { width: (100 * p.valor / max).toFixed(2) + "%" } }));
      const filhos = [h("span", { class: "prm-barras__rotulo" }, i.rotulo), h("span", { class: "prm-barras__trilho", "aria-hidden": "true" }, segs), h("span", { class: "prm-barras__valor" }, i.texto)];
      const el = i.aoClicar
        ? h("button", { class: "prm-barras__linha", type: "button", onclick: i.aoClicar, "aria-label": i.rotulo + ": " + (i.dica || i.texto).replace(/\n/g, ", ") + ". Abrir a lista." }, filhos)
        : h("div", { class: "prm-barras__linha", tabindex: "0", role: "group", "aria-label": i.rotulo + ": " + (i.dica || i.texto).replace(/\n/g, ", ") }, filhos);
      return dica(el, i.rotulo + "\n" + (i.dica || i.texto));
    })) : apoio(vazio || "Sem dados no período.");
    return h("figure", { class: "prm-graf", "aria-labelledby": id }, h("figcaption", null, h("h3", { id }, titulo), ap ? apoio(ap) : null),
      series && series.length > 1 ? legenda(series) : null, corpo, cols && itens.length ? tabelaAlt(cols, itens.map((i) => i.linha || i)) : null);
  }

  // colunas empilhadas por mês contra a meta (um eixo em R$)
  function colunasMeta({ titulo, apoio: ap, meses, series, aoClicar }) {
    const id = uid("graf");
    const topo = Math.max(1, ...meses.map((m) => Math.max(m.meta || 0, series.reduce((a, s) => a + (m[s.chave] || 0), 0)))) * 1.08;
    const area = h("div", { class: "prm-colunas__area", "aria-hidden": "true" }, meses.map((m) => {
      const col = h("div", { class: "prm-colunas__col" }, series.filter((s) => m[s.chave] > 0).map((s) => dica(h("button", { class: "prm-colunas__seg", type: "button", tabindex: "-1",
        "data-serie": String(s.serie), estilo: { height: (100 * m[s.chave] / topo).toFixed(2) + "%" }, onclick: () => aoClicar && aoClicar(m, s) }),
        m.rotulo + " · " + s.rotulo + "\n" + reais(m[s.chave]) + (m["n_" + s.n] !== undefined ? " (" + nTxt(m["n_" + s.n], "negócio", "negócios") + ")" : ""))));
      if (m.meta) col.append(h("span", { class: "prm-colunas__meta", estilo: { bottom: (100 * m.meta / topo).toFixed(2) + "%" } }));
      return col;
    }));
    const eixo = h("div", { class: "prm-colunas__eixo", "aria-hidden": "true" }, h("span", null, reaisC(topo)), h("span", null, reaisC(topo / 2)), h("span", null, "0"));
    const rotulos = h("div", { class: "prm-colunas__rotulos", "aria-hidden": "true" }, meses.map((m) => h("span", null, m.rotulo)));
    const resumo = h("ul", { class: "prm-lista" }, meses.map((m) => h("li", { class: "prm-lista__item" },
      h("div", null, h("div", { class: "prm-lista__titulo" }, m.rotulo), h("div", { class: "prm-lista__apoio" },
        "Realizado " + reais(m.realizado) + (m.meta ? " de " + reais(m.meta) + " (" + pctTxt(m.pct_meta_realizado) + " da meta)" : ""))),
      aoClicar ? h("button", { class: "prm-btn prm-btn--texto", type: "button", onclick: () => aoClicar(m, series[0]) }, "Ver ganhos") : null)));
    return h("figure", { class: "prm-graf", "aria-labelledby": id }, h("figcaption", null, h("h3", { id }, titulo), ap ? apoio(ap) : null),
      legenda(series, "Meta do mês"), h("div", { class: "prm-colunas" }, eixo, area, rotulos), resumo,
      tabelaAlt([{ t: "Mês", v: (m) => m.rotulo }].concat(series.map((s) => ({ t: s.rotulo, v: (m) => reais(m[s.chave]), num: true })), [{ t: "Meta", v: (m) => reais(m.meta), num: true }]), meses));
  }

  function kpiComp(rot, valor, apoioTxt, comp, fmt, sentido) {
    let delta = null;
    if (comp && comp.delta !== null && comp.delta !== undefined && comp.anterior !== null) {
      const d = comp.delta, txt = fmt ? fmt(Math.abs(d)) : String(Math.abs(d)).replace(".", ",");
      delta = d === 0 ? "= igual ao anterior" : (d > 0 ? "▲ +" : "▼ −") + txt + " vs. anterior";
    }
    return h("div", { class: "prm-cartao prm-kpi" }, h("span", { class: "prm-rotulo" }, rot), h("span", { class: "prm-kpi__valor prm-kpi__valor--compacto prm-mono" }, valor),
      apoioTxt ? h("span", { class: "prm-kpi__apoio" }, apoioTxt) : null, delta ? h("span", { class: "prm-kpi__delta" }, delta) : null);
  }

  const taxaTxt = (c) => (c.base_pequena ? "base pequena" : pctTxt(c.pct));
  const SERIES_AGING = [{ serie: 1, rotulo: "até 15 dias" }, { serie: 2, rotulo: "16 a 30 dias" }, { serie: 3, rotulo: "31 a 60 dias" }, { serie: 4, rotulo: "mais de 60 dias" }];

  function grafAging(ag, aoClicar) {
    return barras({ titulo: "Tempo na etapa atual (negócios em andamento)", apoio: "Parado = mais de " + ag.limite_dias + " dias na mesma etapa.", series: SERIES_AGING,
      itens: ag.por_estado.map((e) => ({ rotulo: e.rotulo, partes: e.faixas.map((f, i) => ({ valor: f.n, serie: i + 1 })), texto: nTxt(e.n, "negócio", "negócios"),
        dica: e.faixas.map((f) => f.faixa + ": " + f.n).join("\n") + "\nParados: " + e.parados, aoClicar: aoClicar ? () => aoClicar(e) : null, linha: e })),
      cols: [{ t: "Etapa", v: (e) => e.rotulo }].concat(ag.faixas.map((f, i) => ({ t: f, v: (e) => String(e.faixas[i].n), num: true })), [{ t: "Parados", v: (e) => String(e.parados), num: true }]) });
  }

  function grafFunil(f, apoioTxt) {
    return barras({ titulo: "Funil de conversão", apoio: apoioTxt || ("Negócios que entraram no período (" + f.coorte + ") e até onde chegaram."),
      itens: f.etapas.map((e) => ({ rotulo: e.rotulo, valor: e.n, serie: 2, texto: e.n + " · " + pctTxt(e.pct_do_inicio),
        dica: e.n + " negócio(s) · " + pctTxt(e.pct_do_inicio) + " do início" + (e.pct_da_anterior !== undefined ? " · " + pctTxt(e.pct_da_anterior) + " da etapa anterior" : ""), linha: e })),
      cols: [{ t: "Etapa", v: (e) => e.rotulo }, { t: "Negócios", v: (e) => String(e.n), num: true }, { t: "% do início", v: (e) => pctTxt(e.pct_do_inicio), num: true },
        { t: "% da anterior", v: (e) => pctTxt(e.pct_da_anterior), num: true }], vazio: "Nenhum negócio entrou no período." });
  }

  function grafPipeline(pipe, comValor, aoClicar) {
    return barras({ titulo: "Pipeline por etapa", apoio: comValor ? "Crédito estimado dos negócios em andamento. Barra = valor; texto = quantidade e valor." : "Negócios em andamento por etapa.",
      itens: pipe.map((p) => ({ rotulo: p.rotulo, valor: comValor ? p.valor : p.n, serie: 2, texto: comValor ? p.n + " · " + reaisC(p.valor) : String(p.n),
        dica: nTxt(p.n, "negócio", "negócios") + (comValor ? "\n" + reais(p.valor) + (p.sem_valor ? "\n" + p.sem_valor + " sem valor no CRM" : "") : ""),
        aoClicar: aoClicar ? () => aoClicar(p) : null, linha: p })),
      cols: [{ t: "Etapa", v: (p) => p.rotulo }, { t: "Negócios", v: (p) => String(p.n), num: true }].concat(comValor ? [{ t: "Crédito estimado", v: (p) => reais(p.valor), num: true },
        { t: "Sem valor", v: (p) => String(p.sem_valor), num: true }] : []), vazio: "Nenhum negócio em andamento." });
  }

  function avisoRessalva(r) {
    if (!r || !r.valor_credito) return null;
    return h("div", { class: "prm-aviso prm-aviso--info" }, icone("info"), h("div", null, h("strong", null, "Valores: "), r.valor_credito + " Não há probabilidade de êxito nem prazo de restituição nesta tela."));
  }

  // ---------------- cartão de negócio (lista e quadro)
  function cartaoNegocio(i, save, compacto) {
    const go = save ? "#/canal/negocios/" + i.deal_id : "#/negocios/" + i.ref;
    const meta = [];
    if (i.etapa_crm) meta.push(h("span", null, "Etapa: " + i.etapa_crm));
    if (i.dias_na_etapa !== null && i.dias_na_etapa !== undefined) meta.push(h("span", null, "há " + nTxt(i.dias_na_etapa, "dia", "dias") + " na etapa"));
    if (!compacto) meta.push(h("span", null, i.produto));
    if (i.valor_credito !== undefined) meta.push(h("span", null, "Crédito estimado* ", h("span", { class: "prm-neg__valor" }, i.valor_credito === null ? "sem valor no CRM" : reais(i.valor_credito))));
    if (i.remuneracao_prevista) meta.push(h("span", null, "Remuneração prevista* ", h("span", { class: "prm-neg__valor" }, reais(i.remuneracao_prevista))));
    if (i.previsao_fechamento_em) meta.push(h("span", null, "Previsão de assinatura: ", mono(dataBR(i.previsao_fechamento_em))));
    if (i.fechado_em) meta.push(h("span", null, "Encerrado em ", mono(dataBR(i.fechado_em))));
    if (save && i.master) meta.push(h("span", null, "Master: " + i.master));
    if (i.consultor) meta.push(h("span", null, "Consultor: " + i.consultor));
    const topo = h("div", { class: "prm-neg__topo" }, h("div", null, h("div", { class: "prm-lista__titulo" }, i.nome), h("div", { class: "prm-lista__apoio prm-mono" }, i.cnpj_mascara || "")),
      h("div", { class: "prm-linha" }, i.parado ? h("span", { class: "prm-tag-parado" }, icone("alerta"), "Parado") : null, compacto ? null : chip(i.rotulo, i.chip)));
    if (compacto) return h("a", { class: "prm-quadro__cartao", href: go }, topo, h("div", { class: "prm-neg__meta" }, meta));
    return h("li", { class: "prm-lista__item" }, h("a", { class: "prm-lista__link prm-neg", href: go }, topo, h("div", { class: "prm-neg__meta" }, meta)));
  }

  // ---------------- lista + quadro (parceiro e Save)
  async function telaNegocios(main, params, save) {
    const base = save ? "canal/negocios" : "negocios";
    const st = Object.fromEntries(params.entries());
    st.situacao = st.situacao || "andamento"; st.visao = st.visao || "lista"; st.pagina = st.pagina || "1";
    const consulta = () => { const q = new URLSearchParams(); for (const [k, v] of Object.entries(st)) if (v && k !== "visao") q.set(k, v); if (st.visao === "quadro") { q.set("por_pagina", "200"); q.set("pagina", "1"); } return q.toString(); };
    carregando(main, 4);
    const r0 = await api("GET", (save ? "save/negocios" : "parceiro/negocios") + "?" + consulta());
    if (r0.st === 401 || r0.st === 428) return;
    if (r0.st !== 200) return erroBloco(main, r0.o, r0.st, () => navegar());
    pronto(main);
    const f = r0.o.filtros;
    cab(main, "Negócios", save ? "Negócios do canal com parceiro, com filtros. Nada desta tela vai ao parceiro." : "Cada negócio que veio da sua indicação, do primeiro contato ao contrato.",
      save ? [h("a", { class: "prm-btn prm-btn--sec", href: "#/canal/dashboard" }, "Voltar ao dashboard")] : [h("a", { class: "prm-btn prm-btn--sec", href: "#/inicio?aba=painel" }, "Ver painel"), h("a", { class: "prm-btn", href: "#/registrar" }, "Registrar empresa")], save ? "Canal" : null);
    const ress = avisoRessalva(r0.o.ressalvas);
    if (ress) main.append(ress);
    const sel = (rot, chave, opcoes, todos) => {
      const s = h("select", { class: "prm-campo__entrada" }, todos ? h("option", { value: "" }, todos) : null, opcoes.map(([v, t]) => h("option", { value: v, selected: st[chave] === v ? true : null }, t)));
      s.addEventListener("change", () => { st[chave] = s.value; st.pagina = "1"; atualizar(); });
      return h("label", null, rot, s);
    };
    const busca = h("input", { class: "prm-campo__entrada", type: "search", placeholder: "Nome ou CNPJ", valor: st.q || "" });
    busca.addEventListener("input", debounce(() => { st.q = busca.value.trim(); st.pagina = "1"; atualizar(); }, 300));
    const data = (rot, chave) => { const i = h("input", { class: "prm-campo__entrada", type: "date", valor: st[chave] || "" }); i.addEventListener("change", () => { st[chave] = i.value; st.pagina = "1"; atualizar(); }); return h("label", null, rot, i); };
    const mais = ["tese", "etapa", "consultor", "master", "de", "ate"].some((k) => st[k]);
    const filtros = h("div", { class: "prm-filtros-neg", role: "group", "aria-label": "Filtros dos negócios" },
      h("label", null, "Buscar", busca),
      sel("Situação", "situacao", f.situacoes.map((s) => [s.chave, s.rotulo])),
      sel("Estado", "estado", f.estados.map((e) => [e.estado, e.rotulo]), "Todos"),
      sel("Ordenar por", "ordem", f.ordens.map((o) => [o.chave, o.rotulo])));
    const filtros2 = h("div", { class: "prm-filtros-neg", role: "group", "aria-label": "Mais filtros" },
      sel("Produto", "produto", f.produtos.map((p) => [p, p]), "Todos"),
      f.teses.length ? sel("Tese", "tese", f.teses.map((t) => [t, t]), "Todas") : null,
      f.etapas && f.etapas.length ? sel("Etapa no CRM", "etapa", f.etapas.map((t) => [t, t]), "Todas") : null,
      f.consultores && f.consultores.length ? sel("Consultor", "consultor", f.consultores.map((u) => [u.id, u.nome]), "Todos") : null,
      f.masters ? sel("Master", "master", f.masters.map((m) => [m.id, m.nome]), "Todos") : null,
      data("Entrada desde", "de"), data("Entrada até", "ate"));
    const visoes = h("div", { class: "prm-filtros", role: "group", "aria-label": "Visão" }, [["lista", "Lista"], ["quadro", "Quadro por estado"]].map(([k, n]) =>
      h("button", { class: "prm-filtro", type: "button", "aria-pressed": String(st.visao === k), onclick: (e) => { st.visao = k; visoes.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b === e.currentTarget))); atualizar(); } }, n)));
    const extras = h("div", { class: "prm-linha" }, st.parado ? h("button", { class: "prm-btn prm-btn--texto", type: "button", onclick: () => { delete st.parado; atualizar(); } }, "Tirar o filtro de parados") : null,
      ["registrado", "mes_previsao", "mes_fechamento"].filter((k) => st[k]).map((k) => h("button", { class: "prm-btn prm-btn--texto", type: "button", onclick: (e) => { delete st[k]; e.currentTarget.remove(); atualizar(); } }, "Tirar o filtro: " + k.replace(/_/g, " ") + " " + st[k])));
    const resumo = h("p", { class: "prm-texto-apoio", "aria-live": "polite" });
    const res = h("div");
    main.append(filtros, h("details", { class: "prm-detalhe prm-filtros-mais", open: mais || st.produto ? true : null }, h("summary", null, "Mais filtros"), filtros2),
      h("div", { class: "prm-linha prm-linha--entre" }, visoes, extras), resumo, res);
    function desenhar(o) {
      limpar(res);
      resumo.textContent = nTxt(o.total, "negócio", "negócios") + (o.valor_total !== null && o.valor_total !== undefined ? " · " + reais(o.valor_total) + " em crédito estimado*" : "");
      if (!o.total) { res.append(h("div", { class: "prm-vazio" }, h("p", null, "Nenhum negócio com estes filtros."))); return; }
      if (st.visao === "quadro") {
        res.append(h("div", { class: "prm-quadro", role: "region", "aria-label": "Quadro por estado", tabindex: "0" }, o.colunas.map((c, idx) => {
          const xs = o.itens.filter((i) => i.estado === c.estado);
          return h("section", { class: "prm-quadro__col", "aria-label": c.rotulo }, h("div", { class: "prm-quadro__cab", "data-serie": String(Math.min(4, idx + 1)) },
            h("h2", null, c.rotulo), h("span", { class: "prm-texto-apoio prm-mono" }, nTxt(c.n, "negócio", "negócios") + (c.valor !== null && c.valor !== undefined ? " · " + reaisC(c.valor) : ""))),
            xs.length ? h("ul", { class: "prm-quadro__lista" }, xs.map((i) => h("li", null, cartaoNegocio(i, save, true)))) : apoio("Nenhum."));
        })));
        if (o.total > o.itens.length) res.append(apoio("Mostrando " + o.itens.length + " de " + o.total + ". Use os filtros para ver o restante."));
      } else {
        res.append(h("ul", { class: "prm-lista prm-cartao" }, o.itens.map((i) => cartaoNegocio(i, save))));
        if (o.paginas > 1) {
          const ir = (p) => { st.pagina = String(p); atualizar(); main.querySelector("h1").scrollIntoView(); };
          res.append(h("nav", { class: "prm-paginacao", "aria-label": "Páginas" }, h("button", { class: "prm-btn prm-btn--sec", type: "button", disabled: o.pagina <= 1 ? true : null, onclick: () => ir(o.pagina - 1) }, "Anterior"),
            h("span", { class: "prm-texto-apoio prm-mono" }, "Página " + o.pagina + " de " + o.paginas),
            h("button", { class: "prm-btn prm-btn--sec", type: "button", disabled: o.pagina >= o.paginas ? true : null, onclick: () => ir(o.pagina + 1) }, "Próxima")));
        }
      }
      if (o.ressalvas && o.ressalvas.valor_credito) res.append(h("p", { class: "prm-ressalva" }, "* " + o.ressalvas.valor_credito));
    }
    async function atualizar() {
      const q = new URLSearchParams(Object.entries(st).filter(([, v]) => v)).toString();
      history.replaceState(null, "", "#/" + base + (q ? "?" + q : ""));
      res.setAttribute("aria-busy", "true");
      const r = await api("GET", (save ? "save/negocios" : "parceiro/negocios") + "?" + consulta());
      res.removeAttribute("aria-busy");
      if (r.st !== 200) { limpar(res).append(h("div", { class: "prm-aviso prm-aviso--erro", role: "alert" }, icone("alerta"), h("div", null, r.o.erro || "Não conseguimos carregar agora."))); return; }
      desenhar(r.o);
    }
    desenhar(r0.o);
  }

  // ---------------- ficha completa do negócio
  function valorCampo(c) {
    if (c.tipo === "reais") return mono(reais(c.valor));
    if (c.tipo === "pct") return mono(fracTxt(c.valor));
    if (c.tipo === "data") return mono(dataBR(c.valor));
    if (c.tipo === "lista") return h("span", null, c.valor.join(" · "));
    return h("span", null, String(c.valor));
  }

  function telaFicha(main, o, save) {
    const voltar = save ? "#/canal/negocios" : "#/negocios";
    cab(main, o.nome, null, save ? [h("a", { class: "prm-btn prm-btn--sec", href: voltar }, "Voltar à lista")]
      : [h("a", { class: "prm-btn prm-btn--sec", href: "#/pedidos/novo?empresa=" + o.ref }, "Perguntar sobre este negócio")], save ? "Canal · negócio " + o.deal_id : "Negócio");
    main.querySelector(".prm-cab > div").append(h("p", { class: "prm-mono" }, o.cnpj_mascara || ""),
      h("div", { class: "prm-linha" }, chip(o.rotulo, o.chip), apoio("Com: " + o.com + (o.desde ? " desde " + o.desde : "")),
        o.dias_na_etapa !== null && o.dias_na_etapa !== undefined ? apoio("há " + nTxt(o.dias_na_etapa, "dia", "dias") + " na etapa atual") : null));
    const pend = (o.pendencias || []).filter((p) => !p.resolvida_em);
    if (pend.length && !save) main.append(h("section", { class: "prm-cartao prm-cartao--acao", "aria-labelledby": "t-npend" }, h("h2", { id: "t-npend" }, "Precisa de você"),
      pend.map((p) => h("p", null, (p.texto || p.tipo) + " (desde " + p.desde + ")")), h("a", { class: "prm-btn", href: "#/pedidos/novo?empresa=" + o.ref }, "Avisar a Save")));
    main.append(h("section", { class: "prm-cartao", "aria-labelledby": "t-nand" }, h("h2", { id: "t-nand" }, "Andamento"),
      h("ol", { class: "prm-tempo" }, o.passos.map((p) => h("li", { class: "prm-tempo__passo", "data-estado": p.situacao, "aria-current": p.situacao === "atual" || p.situacao === "bloqueado" ? "step" : null },
        h("span", { class: "prm-tempo__titulo" }, p.titulo), h("span", { class: "prm-tempo__quando" }, { feito: "concluído", atual: "atual", bloqueado: "esperando você", futuro: "próximo" }[p.situacao])))),
      h("p", null, h("strong", null, "Próximo passo: "), o.proximo_passo)));
    main.append(h("div", { class: "prm-campos-neg" }, o.secoes.map((s) => h("section", { class: "prm-cartao", "aria-label": s.titulo }, h("h2", null, s.titulo),
      h("dl", null, s.campos.map((c) => [h("dt", null, c.rotulo + (c.ressalva ? "*" : "")), h("dd", null, valorCampo(c), c.ressalva ? h("p", { class: "prm-ressalva" }, "* " + c.ressalva) : null)]))))));
    if (o.linha_do_tempo) main.append(h("section", { class: "prm-cartao", "aria-labelledby": "t-nlt" }, h("h2", { id: "t-nlt" }, "Linha do tempo das etapas"),
      h("ol", { class: "prm-linha-tempo" }, o.linha_do_tempo.map((x) => h("li", { "data-atual": String(x.atual), "aria-current": x.atual ? "step" : null }, h("span", { class: "prm-linha-tempo__ponto", "aria-hidden": "true" }),
        h("div", null, h("div", { class: "prm-lista__titulo" }, x.etapa + (x.atual ? " (atual)" : "")), x.estado ? h("div", { class: "prm-lista__apoio" }, x.estado) : null),
        h("div", { class: "prm-lista__apoio prm-mono" }, x.desde + (x.dias !== null ? " · " + nTxt(x.dias, "dia", "dias") : "")))))));
    const blocos = [];
    if (o.documentos) blocos.push(h("section", { class: "prm-cartao", "aria-labelledby": "t-ndoc" }, h("h2", { id: "t-ndoc" }, "Documentos e acessos pedidos"),
      o.documentos.length ? h("ul", { class: "prm-lista" }, o.documentos.map((d) => h("li", { class: "prm-lista__item" }, h("span", null, d.item),
        chip({ recebido: "Recebido", liberado: "Liberado", pendente: "Pendente" }[d.situacao] || d.situacao, d.situacao === "pendente" ? "atencao" : "ok")))) : apoio("Nenhum documento pedido.")));
    if (o.pendencias) blocos.push(h("section", { class: "prm-cartao", "aria-labelledby": "t-npe" }, h("h2", { id: "t-npe" }, "Pendências"),
      o.pendencias.length ? h("ul", { class: "prm-lista" }, o.pendencias.map((p) => h("li", { class: "prm-lista__item" }, h("div", null, h("div", { class: "prm-lista__titulo" }, p.texto || p.tipo),
        h("div", { class: "prm-lista__apoio" }, "Aberta em " + p.desde + (p.resolvida_em ? " · resolvida em " + p.resolvida_em : ""))), chip(p.resolvida_em ? "Resolvida" : "Aberta", p.resolvida_em ? "ok" : "acao")))) : apoio("Nenhuma pendência.")));
    if (o.registro !== undefined) blocos.push(h("section", { class: "prm-cartao", "aria-labelledby": "t-nreg" }, h("h2", { id: "t-nreg" }, "Registro de oportunidade"),
      o.registro ? [h("dl", { class: "prm-dl prm-dl--esq" }, h("dt", null, "Registro"), h("dd", null, o.registro.registro_id), h("dt", null, "Situação"), h("dd", null, o.registro.rotulo),
        o.registro.carimbo ? [h("dt", null, "Data e hora"), h("dd", null, o.registro.carimbo)] : null, o.registro.valido_ate ? [h("dt", null, "Válido até"), h("dd", null, o.registro.valido_ate)] : null),
        !save && o.registro.ref ? h("a", { class: "prm-btn prm-btn--texto", href: "#/empresas/" + o.registro.ref }, "Abrir a empresa") : null] : apoio("Este negócio chegou à Save sem registro pelo portal.")));
    else if (!save) blocos.push(h("section", { class: "prm-cartao" }, h("h2", null, "Registro de oportunidade"), apoio("Este negócio chegou à Save sem registro pelo portal.")));
    if (o.pedidos) blocos.push(h("section", { class: "prm-cartao", "aria-labelledby": "t-nped" }, h("h2", { id: "t-nped" }, "Pedidos ligados"),
      o.pedidos.length ? h("ul", { class: "prm-lista" }, o.pedidos.map((p) => h("li", { class: "prm-lista__item" }, save ? h("span", null, p.id + " · " + p.aberta_em) : h("a", { class: "prm-lista__link", href: "#/pedidos/" + p.ref },
        h("div", null, h("div", { class: "prm-lista__titulo" }, p.id), h("div", { class: "prm-lista__apoio" }, p.aberta_em))), chip(p.rotulo, p.chip)))) : apoio("Nenhum pedido sobre este negócio.")));
    if (o.extrato) blocos.push(h("section", { class: "prm-cartao", "aria-labelledby": "t-next" }, h("h2", { id: "t-next" }, "Extrato ligado"),
      o.extrato.length ? o.extrato.map(linhaExtrato) : apoio("Sem linha de extrato para este negócio.")));
    main.append(h("div", { class: "prm-grade prm-grade--2" }, blocos));
  }

  async function vNegocios(main, _x, params) { await telaNegocios(main, params, false); }
  async function vNegocio(main, ref) { await carregar(main, "parceiro/negocios/" + ref, (o) => telaFicha(main, o, false), 4); }
  async function sNegocios(main, _x, params) { await telaNegocios(main, params, true); }
  async function sNegocio(main, id) { await carregar(main, "save/negocios/" + id, (o) => telaFicha(main, o, true), 4); }

  // ---------------- P-1b Painel de vendas do parceiro (aba do Início)
  function painelParceiro(alvo, params) {
    const periodo = params.get("periodo") || "90", consultor = params.get("consultor") || "";
    const q = "?periodo=" + encodeURIComponent(periodo) + (consultor ? "&consultor=" + encodeURIComponent(consultor) : "");
    const area = h("div", { class: "prm-pilha" });
    alvo.append(area);
    carregar(area, "parceiro/painel" + q, (o) => {
      const ir = (extra) => { location.hash = "#/negocios?" + new URLSearchParams(Object.assign({ situacao: "andamento" }, consultor ? { consultor } : {}, extra)).toString(); };
      const per = h("select", { class: "prm-campo__entrada" }, [["30", "Últimos 30 dias"], ["90", "Últimos 90 dias"], ["180", "Últimos 180 dias"], ["365", "Últimos 12 meses"]].map(([v, t]) => h("option", { value: v, selected: v === periodo ? true : null }, t)));
      const muda = () => { const p = new URLSearchParams({ aba: "painel", periodo: per.value }); if (cs && cs.value) p.set("consultor", cs.value); location.hash = "#/inicio?" + p.toString(); };
      per.addEventListener("change", muda);
      let cs = null;
      if (o.consultores && o.consultores.length) { cs = h("select", { class: "prm-campo__entrada" }, h("option", { value: "" }, "Escritório inteiro"), o.consultores.map((u) => h("option", { value: u.id, selected: u.id === consultor ? true : null }, u.nome))); cs.addEventListener("change", muda); }
      area.append(h("div", { class: "prm-filtros-neg", role: "group", "aria-label": "Período do painel" }, h("label", null, "Período", per), cs ? h("label", null, "Consultor", cs) : null),
        apoio("Período de " + dataBR(o.periodo.de) + " a " + dataBR(o.periodo.ate) + ", comparado com " + dataBR(o.periodo.anterior_de) + " a " + dataBR(o.periodo.anterior_ate) + ". Só os números do seu escritório: o portal não compara parceiros."));
      const ress = avisoRessalva(o.ressalvas); if (ress) area.append(ress);
      const pa = o.periodo_atual, c = o.comparacao;
      const comValor = pa.ganhos.valor !== null && pa.ganhos.valor !== undefined;
      const abertoN = o.pipeline.reduce((a, p) => a + p.n, 0), abertoV = o.pipeline.reduce((a, p) => a + (p.valor || 0), 0);
      area.append(h("section", { "aria-label": "Indicadores do período" }, h("div", { class: "prm-grade prm-grade--kpi prm-grade--kpi-auto" },
        kpiComp("Em andamento", String(abertoN), comValor ? reaisC(abertoV) + " em crédito estimado*" : "negócios abertos", null),
        kpiComp("Contratos assinados", String(pa.ganhos.n), comValor ? reaisC(pa.ganhos.valor) + "*" : "no período", c.ganhos_n),
        kpiComp("Taxa de conversão", taxaTxt(pa.conversao), "ganhos sobre encerrados (" + pa.conversao.n + ")", pa.conversao.base_pequena ? null : c.conversao_pct, (v) => String(v).replace(".", ",") + " p.p."),
        kpiComp("Ciclo médio", pa.ciclo.media_dias === null ? "—" : String(Math.round(pa.ciclo.media_dias)), "dias, da entrada ao contrato", c.ciclo_dias, (v) => Math.round(v) + " dias"))));
      area.append(h("div", { class: "prm-grade prm-grade--2" },
        h("section", { class: "prm-cartao" }, grafPipeline(o.pipeline, comValor, (p) => ir({ estado: p.estado }))),
        h("section", { class: "prm-cartao" }, grafFunil(o.funil))));
      const parados = h("section", { class: "prm-cartao", "aria-labelledby": "t-ppar" }, h("h2", { id: "t-ppar" }, "Negócios parados (" + o.aging.total_parados + ")"),
        o.aging.parados.length ? h("ul", { class: "prm-lista" }, o.aging.parados.map((i) => cartaoNegocio(i, false))) : apoio("Nenhum negócio parado há mais de " + o.aging.limite_dias + " dias."),
        o.aging.total_parados ? h("button", { class: "prm-btn prm-btn--texto", type: "button", onclick: () => ir({ parado: "1", ordem: "parado" }) }, "Ver todos os parados") : null);
      area.append(h("div", { class: "prm-grade prm-grade--2" }, h("section", { class: "prm-cartao" }, grafAging(o.aging, (e) => ir({ estado: e.estado, ordem: "parado" }))), parados));
      const ganhosPerd = barras({ titulo: "Contratos assinados e encerrados sem contrato", apoio: "No período, comparado com o período anterior.",
        series: [{ serie: 2, rotulo: "Período atual" }, { serie: 0, rotulo: "Período anterior" }],
        itens: [["Contratos assinados", "ganhos"], ["Encerrados sem contrato", "perdidos"], ["Negócios novos", "novos"]].flatMap(([r, k]) => [
          { rotulo: r, valor: pa[k].n, serie: 2, texto: String(pa[k].n) + (pa[k].valor ? " · " + reaisC(pa[k].valor) : ""), dica: "Período atual: " + pa[k].n, linha: { r, k } },
          { rotulo: r + " (anterior)", valor: o.periodo_anterior[k].n, serie: 0, texto: String(o.periodo_anterior[k].n), dica: "Período anterior: " + o.periodo_anterior[k].n, linha: { r: r + " (anterior)", k } }]),
        cols: [{ t: "Indicador", v: (l) => l.r }, { t: "Quantidade", v: (l) => String((l.r.endsWith("(anterior)") ? o.periodo_anterior : pa)[l.k].n), num: true }] });
      const ativ = h("section", { class: "prm-cartao", "aria-labelledby": "t-pativ" }, h("h2", { id: "t-pativ" }, "Atividade"),
        h("dl", { class: "prm-dl" }, h("dt", null, "Registros neste mês"), h("dd", null, String(o.atividade.registros_no_mes)), h("dt", null, "Registros no período"), h("dd", null, String(o.atividade.registros_no_periodo)),
          h("dt", null, "Pedidos em aberto"), h("dd", null, String(o.atividade.demandas_abertas)), h("dt", null, "Negócios em andamento"), h("dd", null, String(o.atividade.negocios_abertos))));
      area.append(h("div", { class: "prm-grade prm-grade--2" }, h("section", { class: "prm-cartao" }, ganhosPerd), ativ));
      if (o.remuneracao) {
        const r = o.remuneracao;
        area.append(h("section", { class: "prm-cartao" }, barras({ titulo: "Sua remuneração", apoio: "Percentual do seu termo: " + fracTxt(r.percentual_termo) + ". " + (r.ganhos_sem_calculo ? r.ganhos_sem_calculo + " contrato(s) ainda sem dado para calcular." : ""),
          series: [{ serie: 1, rotulo: "Prevista*" }, { serie: 3, rotulo: "Recebida pela Save" }, { serie: 4, rotulo: "Paga a você" }],
          itens: [{ rotulo: "Prevista*", valor: r.prevista, serie: 1, texto: reais(r.prevista), linha: { r: "Prevista*", v: r.prevista } },
            { rotulo: "Recebida pela Save", valor: r.recebida_pela_save, serie: 3, texto: reais(r.recebida_pela_save), linha: { r: "Recebida pela Save", v: r.recebida_pela_save } },
            { rotulo: "Paga a você", valor: r.paga, serie: 4, texto: reais(r.paga), linha: { r: "Paga a você", v: r.paga } }],
          cols: [{ t: "Situação", v: (l) => l.r }, { t: "Valor", v: (l) => reais(l.v), num: true }] }), h("p", { class: "prm-ressalva" }, "* " + r.ressalva),
          h("a", { class: "prm-btn prm-btn--texto", href: "#/extrato" }, "Ver extrato")));
      }
      const linhaC = (rot, k, fmt) => ({ rot, a: c[k].atual, b: c[k].anterior, d: c[k].delta, fmt });
      const comp = [linhaC("Contratos assinados", "ganhos_n", String), linhaC("Crédito dos contratos assinados*", "ganhos_valor", reaisC), linhaC("Encerrados sem contrato", "perdidos_n", String),
        linhaC("Negócios novos", "novos_n", String), linhaC("Taxa de conversão", "conversao_pct", pctTxt), linhaC("Ciclo médio (dias)", "ciclo_dias", (v) => (v === null ? "—" : String(Math.round(v))))].filter((l) => l.a !== null || l.b !== null);
      area.append(h("section", { class: "prm-cartao", "aria-labelledby": "t-pcomp" }, h("h2", { id: "t-pcomp" }, "Comparação com o período anterior"),
        h("div", { class: "prm-tabela prm-tabela--compacta" }, h("table", null, h("caption", { class: "prm-so-leitor" }, "Comparação com o período anterior"),
          h("thead", null, h("tr", null, h("th", { scope: "col" }, "Indicador"), h("th", { scope: "col", class: "num" }, "Período atual"), h("th", { scope: "col", class: "num" }, "Anterior"), h("th", { scope: "col", class: "num" }, "Variação"))),
          h("tbody", null, comp.map((l) => h("tr", null, h("td", null, l.rot), h("td", { class: "num" }, l.fmt(l.a)), h("td", { class: "num" }, l.fmt(l.b)),
            h("td", { class: "num" }, l.d === null || l.d === undefined ? "—" : (l.d > 0 ? "▲ +" : l.d < 0 ? "▼ −" : "= ") + l.fmt(Math.abs(l.d))))))))));
      if (o.ressalvas && o.ressalvas.valor_credito) area.append(h("p", { class: "prm-ressalva" }, "* " + o.ressalvas.valor_credito));
    }, 4);
  }

  // ---------------- Save · Dashboard comercial
  async function sDashboard(main, _x, params) {
    const periodo = params.get("periodo") || "90", master = params.get("master") || "";
    await carregar(main, "save/dashboard?periodo=" + encodeURIComponent(periodo) + (master ? "&master=" + encodeURIComponent(master) : ""), (o) => {
      cab(main, "Dashboard comercial", "Pipeline, conversão e previsão do canal. Sem café e sem negócio fora do roster. Nada desta tela vai ao parceiro.", [h("a", { class: "prm-btn prm-btn--sec", href: "#/canal/negocios" }, "Ver negócios")], "Canal");
      const drill = (f) => { location.hash = "#/canal/negocios?" + new URLSearchParams(Object.assign({}, master ? { master } : {}, f)).toString(); };
      const per = h("select", { class: "prm-campo__entrada" }, [["30", "Últimos 30 dias"], ["90", "Últimos 90 dias"], ["180", "Últimos 180 dias"], ["365", "Últimos 12 meses"]].map(([v, t]) => h("option", { value: v, selected: v === periodo ? true : null }, t)));
      const ms = h("select", { class: "prm-campo__entrada" }, h("option", { value: "" }, "Canal inteiro"), o.masters.map((m) => h("option", { value: m.id, selected: m.id === master ? true : null }, m.nome)));
      const muda = () => { const p = new URLSearchParams({ periodo: per.value }); if (ms.value) p.set("master", ms.value); location.hash = "#/canal/dashboard?" + p.toString(); };
      per.addEventListener("change", muda); ms.addEventListener("change", muda);
      main.append(h("div", { class: "prm-filtros-neg", role: "group", "aria-label": "Filtros do dashboard" }, h("label", null, "Período", per), h("label", null, "Master", ms)),
        apoio("Período de " + dataBR(o.periodo.de) + " a " + dataBR(o.periodo.ate) + " (comparado com os " + o.periodo.dias + " dias anteriores). Espelho do HubSpot até " + (o.fonte.espelho_ate ? dataBR(o.fonte.espelho_ate) : "—") + "."));
      const k = o.kpis, c = o.comparacao;
      main.append(h("section", { "aria-label": "Indicadores" }, h("div", { class: "prm-grade prm-grade--kpi prm-grade--kpi-auto" },
        kpiComp("Pipeline em andamento", reaisC(k.pipeline_valor), nTxt(k.pipeline_n, "negócio", "negócios"), null),
        kpiComp("Ganhos no período", reaisC(k.ganhos_valor), nTxt(k.ganhos_n, "contrato", "contratos"), c.ganhos_valor, reaisC),
        kpiComp("Win rate", taxaTxt(k.conversao), k.conversao.ganhos + " de " + k.conversao.n + " encerrados", k.conversao.base_pequena ? null : c.conversao_pct, (v) => String(v).replace(".", ",") + " p.p."),
        kpiComp("Ciclo médio", k.ciclo.media_dias === null ? "—" : String(Math.round(k.ciclo.media_dias)), "dias · mediana " + (k.ciclo.mediana_dias === null ? "—" : Math.round(k.ciclo.mediana_dias) + " dias"), c.ciclo_dias, (v) => Math.round(v) + " dias"),
        kpiComp("Parados", String(k.parados), "mais de " + o.aging.limite_dias + " dias na etapa", null),
        kpiComp("Dormentes", String(k.dormentes), "parceiros com ganho em 12 meses e sem negócio novo", null),
        kpiComp("Negócios novos", String(k.novos_n), "no período", c.novos_n),
        kpiComp("Concentração top 5", o.concentracao.top5_pct === null ? "—" : pctTxt(o.concentracao.top5_pct), "crédito ganho em 12 meses (guarda)", null))));
      const f = o.forecast;
      main.append(h("section", { class: "prm-cartao" }, colunasMeta({ titulo: "Previsão por mês contra a meta" + (master ? "" : " (D111)"), apoio: f.nota + " Fonte da meta: " + f.fonte_meta + ".",
        meses: f.meses, series: [{ chave: "realizado", rotulo: "Realizado (ganhos)", serie: 4, n: "realizado" }, { chave: "em_contrato", rotulo: "Em contrato, previsão no mês", serie: 2, n: "contrato" },
          { chave: "demais_abertos", rotulo: "Demais abertos, previsão no mês", serie: 1, n: "demais" }],
        aoClicar: (m, s) => drill(s.chave === "realizado" ? m.drill : Object.assign({}, m.drill_previsao, s.chave === "em_contrato" ? { estado: "contrato" } : {})) })));
      main.append(h("div", { class: "prm-grade prm-grade--2" },
        h("section", { class: "prm-cartao" }, barras({ titulo: "Pipeline por Master", apoio: "Crédito estimado em andamento (ordem alfabética, não é ranking).",
          itens: o.por_master.map((m) => ({ rotulo: m.nome, valor: m.valor_aberto, serie: 2, texto: m.abertos + " · " + reaisC(m.valor_aberto),
            dica: nTxt(m.abertos, "aberto", "abertos") + " · " + reais(m.valor_aberto) + "\nGanhos no período: " + m.ganhos_n + " · " + reais(m.ganhos_valor) + "\nWin rate: " + taxaTxt(m.conversao) + "\nParados: " + m.parados,
            aoClicar: () => drill({ master: m.master_id, situacao: "andamento" }), linha: m })),
          cols: [{ t: "Master", v: (m) => m.nome }, { t: "Abertos", v: (m) => String(m.abertos), num: true }, { t: "Valor aberto", v: (m) => reais(m.valor_aberto), num: true },
            { t: "Ganhos", v: (m) => String(m.ganhos_n), num: true }, { t: "Valor ganho", v: (m) => reais(m.ganhos_valor), num: true }, { t: "Win rate", v: (m) => taxaTxt(m.conversao), num: true },
            { t: "Ciclo (dias)", v: (m) => (m.ciclo_medio_dias === null ? "—" : String(Math.round(m.ciclo_medio_dias))), num: true }, { t: "Parados", v: (m) => String(m.parados), num: true }] })),
        h("section", { class: "prm-cartao" }, grafPipeline(o.pipeline, true, (p) => drill(p.drill)))));
      main.append(h("div", { class: "prm-grade prm-grade--2" }, h("section", { class: "prm-cartao" }, grafFunil(o.funil)),
        h("section", { class: "prm-cartao" }, grafAging(o.aging, (e) => drill(e.drill)))));
      const cr = o.conversao_registro;
      main.append(h("div", { class: "prm-grade prm-grade--2" },
        h("section", { class: "prm-cartao" }, barras({ titulo: "Conversão: registrado × não registrado", apoio: cr.nota + " Grupo com menos de 20 encerrados aparece como base pequena.",
          itens: [["Com registro no portal", cr.registrado], ["Sem registro", cr.nao_registrado]].map(([r, x]) => ({ rotulo: r, valor: x.pct || 0, serie: 2,
            texto: taxaTxt(x) + " (" + x.ganhos + "/" + x.n + ")", dica: x.ganhos + " ganhos e " + x.perdidos + " perdidos", aoClicar: () => drill(x.drill), linha: Object.assign({ r }, x) })),
          cols: [{ t: "Grupo", v: (l) => l.r }, { t: "Ganhos", v: (l) => String(l.ganhos), num: true }, { t: "Perdidos", v: (l) => String(l.perdidos), num: true }, { t: "Taxa", v: (l) => taxaTxt(l), num: true }] })),
        h("section", { class: "prm-cartao" }, barras({ titulo: "Concentração (crédito ganho em 12 meses)", apoio: "Top 1: " + pctTxt(o.concentracao.top1_pct) + " · Top 5: " + pctTxt(o.concentracao.top5_pct) + ". Métrica de guarda, sem meta.",
          itens: o.concentracao.top5.map((x) => ({ rotulo: x.nome, valor: x.pct, serie: 3, texto: pctTxt(x.pct), dica: reais(x.valor), linha: x })),
          cols: [{ t: "Master", v: (x) => x.nome }, { t: "Crédito ganho", v: (x) => reais(x.valor), num: true }, { t: "% do total", v: (x) => pctTxt(x.pct), num: true }] }))));
      main.append(h("div", { class: "prm-grade prm-grade--2" },
        h("section", { class: "prm-cartao" }, barras({ titulo: "Produtos", apoio: "Crédito estimado em andamento por produto.",
          itens: o.por_produto.map((p) => ({ rotulo: p.produto, valor: p.valor_aberto, serie: 2, texto: p.abertos + " · " + reaisC(p.valor_aberto),
            dica: "Ganhos no período: " + p.ganhos_n + " · " + reais(p.ganhos_valor) + "\nWin rate: " + taxaTxt(p.conversao), aoClicar: () => drill(p.drill), linha: p })),
          cols: [{ t: "Produto", v: (p) => p.produto }, { t: "Abertos", v: (p) => String(p.abertos), num: true }, { t: "Valor aberto", v: (p) => reais(p.valor_aberto), num: true }, { t: "Ganhos", v: (p) => String(p.ganhos_n), num: true }] })),
        h("section", { class: "prm-cartao" }, barras({ titulo: "Teses nos negócios em andamento", apoio: "Um negócio pode ter mais de uma tese.",
          itens: o.por_tese.map((t) => ({ rotulo: t.tese, valor: t.abertos, serie: 2, texto: String(t.abertos), dica: reais(t.valor_aberto) + "\nGanhos em 12 meses: " + t.ganhos_12m, aoClicar: () => drill(t.drill), linha: t })),
          cols: [{ t: "Tese", v: (t) => t.tese }, { t: "Abertos", v: (t) => String(t.abertos), num: true }, { t: "Valor aberto", v: (t) => reais(t.valor_aberto), num: true }, { t: "Ganhos 12 m", v: (t) => String(t.ganhos_12m), num: true }] }))));
      const [tc, lc] = tabela("Pipeline por consultor e indicador", [{ t: "Parceiro", v: (x) => x.nome }, { t: "Master", v: (x) => x.master }, { t: "Abertos", v: (x) => String(x.abertos), num: true },
        { t: "Valor aberto", v: (x) => reais(x.valor_aberto), num: true }, { t: "Ganhos no período", v: (x) => String(x.ganhos_n), num: true }, { t: "Valor ganho", v: (x) => reais(x.ganhos_valor), num: true }], o.por_consultor);
      const [td, ld] = tabela("Parceiros dormentes", [{ t: "Parceiro", v: (x) => x.nome }, { t: "Tipo", v: (x) => x.tipo }, { t: "Dias sem negócio novo", v: (x) => String(x.dias_sem_negocio), num: true },
        { t: "Ganhos em 12 meses", v: (x) => String(x.ganhos_12m), num: true }], o.dormentes);
      main.append(h("section", { class: "prm-pilha--peq", "aria-labelledby": "t-dcons" }, h("h2", { id: "t-dcons", class: "prm-titulo-secao" }, "Por consultor e indicador"), o.por_consultor.length ? [tc, lc] : apoio("Sem consultores com negócio.")),
        h("section", { class: "prm-pilha--peq", "aria-labelledby": "t-ddor" }, h("h2", { id: "t-ddor", class: "prm-titulo-secao" }, "Dormentes"), o.dormentes.length ? [td, ld] : apoio("Nenhum parceiro dormente.")),
        h("section", { class: "prm-pilha--peq", "aria-labelledby": "t-dpar" }, h("h2", { id: "t-dpar", class: "prm-titulo-secao" }, "Parados há mais tempo"),
          o.aging.parados.length ? h("ul", { class: "prm-lista prm-cartao" }, o.aging.parados.map((i) => cartaoNegocio(i, true))) : apoio("Nenhum negócio parado.")));
    }, 6);
  }

  // ------------------------------------------------------------------ início
  async function iniciarSessao() {
    const { st, o } = await api("GET", "eu");
    if (st === 401) return telaSessao();
    if (st === 403) return telaSimples("Acesso não liberado", (o && o.erro) || "Seu acesso ao portal ainda não foi liberado. Fale com o time da Save que atende você.",
      [h("button", { class: "prm-btn prm-btn--sec", type: "button", onclick: sair }, "Sair")]);
    if (st !== 200) return telaSimples("Não conseguimos carregar", "Não conseguimos carregar esta parte agora. Tente de novo em instantes.", [h("button", { class: "prm-btn", type: "button", onclick: () => location.reload() }, "Tentar de novo")]);
    S.eu = o;
    if (o.face === "parceiro" && !o.termos_pendentes) { const r = await api("GET", "parceiro/inicio"); if (r.st === 200) S.inicio = r.o; }
    primeira = true;
    navegar();
  }

  async function init() {
    try {
      const r = await fetch("/api/prm/dev/usuarios", { headers: { Accept: "application/json" }, cache: "no-store" });
      if (r.status === 200) {
        const o = await r.json();
        S.modo = "dev"; S.usuariosTeste = o.usuarios || []; S.cnpjsTeste = o.cnpjs_de_teste || [];
        S.dev = sessionStorage.getItem("prm-dev");
        if (!S.dev) return telaLoginTeste();
        return iniciarSessao();
      }
    } catch (e) { /* sem servidor local: segue para o login da Microsoft */ }
    if (!C || !C.clientId || String(C.clientId).startsWith("<") || !window.msal) {
      return telaSimples("Configuração ausente", "O login da Microsoft ainda não foi configurado neste ambiente.", []);
    }
    S.modo = "msal";
    S.msal = new window.msal.PublicClientApplication({ auth: { clientId: C.prmClientId || C.clientId, authority: "https://login.microsoftonline.com/" + C.tenantId,
      redirectUri: window.location.origin + "/prm.html", postLogoutRedirectUri: window.location.origin + "/prm.html" }, cache: { cacheLocation: "sessionStorage" } });
    try {
      await S.msal.initialize();
      const res = await S.msal.handleRedirectPromise();
      S.conta = (res && res.account) || S.msal.getActiveAccount() || S.msal.getAllAccounts()[0];
      if (!S.conta) {
        return telaSimples("Portal de parceiros da Save", "Você vai para a página da Microsoft para confirmar seu e-mail. Isso protege os dados das empresas que você indica.",
          [h("button", { class: "prm-btn", type: "button", onclick: () => S.msal.loginRedirect({ scopes: [C.prmScope || C.apiScope] }) }, "Entrar com a Microsoft")]);
      }
      S.msal.setActiveAccount(S.conta);
      iniciarSessao();
    } catch (e) {
      telaSimples("Não foi possível entrar", "Não conseguimos concluir o login agora. Tente de novo.", [h("button", { class: "prm-btn", type: "button", onclick: () => location.reload() }, "Tentar de novo")]);
    }
  }
  window.addEventListener("online", () => { const a = document.querySelector(".prm-aviso--offline"); if (a) a.remove(); });
  window.addEventListener("offline", () => { const m = document.getElementById("conteudo"); if (m) m.prepend(h("div", { class: "prm-aviso prm-aviso--atencao prm-aviso--offline", role: "status" }, icone("alerta"), h("div", null, "Sem conexão. Mostramos os dados da última atualização."))); });
  init();
})();
