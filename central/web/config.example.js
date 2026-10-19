// Copie para config.js (fora do repositório) e preencha com os IDs do registro SAVE-SSO-MASTERS.
// Client ID e Tenant ID não são segredos, mas ficam fora do código. Não há segredo no navegador (SPA + PKCE).
window.CENTRAL_CONFIG = {
  tenantId: "<TENANT_ID>",
  clientId: "<CLIENT_ID>",
  apiScope: "api://<CLIENT_ID>/Central.Acesso",  // escopo exposto em "Expor uma API"
  apiBase: "/api",
};
