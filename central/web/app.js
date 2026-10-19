// Central Partners · login Microsoft Entra ID (OIDC, Authorization Code + PKCE via MSAL.js) e chamada à API.
// A sessão fica em sessionStorage. O navegador não guarda segredo. Quem decide o acesso é a API (papéis do token).
(function () {
  "use strict";
  const C = window.CENTRAL_CONFIG;
  const $ = (id) => document.getElementById(id);
  const mostrar = (id) => ["entrar", "carregando", "sem-acesso", "painel", "erro"].forEach((s) => { $(s).hidden = s !== id; });
  const erro = (msg) => { $("erro-texto").textContent = msg; mostrar("erro"); };

  if (!C || !C.clientId || C.clientId.startsWith("<")) { erro("Configuração ausente: crie o config.js a partir do config.example.js."); return; }

  const msal = new window.msal.PublicClientApplication({
    auth: { clientId: C.clientId, authority: "https://login.microsoftonline.com/" + C.tenantId,
            redirectUri: window.location.origin + "/", postLogoutRedirectUri: window.location.origin + "/" },
    cache: { cacheLocation: "sessionStorage" },
  });
  const pedido = { scopes: [C.apiScope] };

  async function token(conta) {
    try {
      return (await msal.acquireTokenSilent({ ...pedido, account: conta })).accessToken;
    } catch (e) {
      if (e instanceof window.msal.InteractionRequiredAuthError) { await msal.acquireTokenRedirect({ ...pedido, account: conta }); return null; }
      throw e;
    }
  }

  async function carregar(conta) {
    mostrar("carregando");
    const t = await token(conta);
    if (!t) return;
    const r = await fetch((C.apiBase || "/api") + "/eu", { headers: { Authorization: "Bearer " + t } });
    if (r.status === 403) { mostrar("sem-acesso"); return; }
    if (!r.ok) { erro("A API respondeu " + r.status + ". Tente de novo ou fale com o Luis."); return; }
    const eu = await r.json();
    $("ola").textContent = "Olá, " + (eu.nome || conta.name || "");
    $("pessoa").textContent = eu.pessoa || "leitura";
    $("papeis").textContent = eu.papeis.join(", ");
    $("pode").textContent = eu.pode.join(", ");
    mostrar("painel");
  }

  document.querySelectorAll(".sair").forEach((b) => b.addEventListener("click", () => msal.logoutRedirect({ account: msal.getActiveAccount() })));
  $("botao-entrar").addEventListener("click", () => msal.loginRedirect(pedido));

  msal.initialize()
    .then(() => msal.handleRedirectPromise())
    .then((res) => {
      const conta = (res && res.account) || msal.getActiveAccount() || msal.getAllAccounts()[0];
      if (!conta) { mostrar("entrar"); return; }
      msal.setActiveAccount(conta);
      return carregar(conta);
    })
    .catch((e) => erro("Não foi possível entrar: " + (e.errorCode || e.message)));
})();
