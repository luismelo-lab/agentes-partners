# Central Partners com SSO Microsoft Entra ID

Plano: `docs/sso-entra/diagnostico-e-plano.md`. Roteiro da TI: `docs/sso-entra/orientacoes-ti-2026-10-19.md`.

| Pasta | O que é |
|---|---|
| `web/` | Painel (SPA). Login com MSAL.js 5.24.0 (Authorization Code + PKCE), hospedado no próprio site. `staticwebapp.config.json` traz a CSP e os cabeçalhos de segurança. |
| `api/central_api/` | `token.py` valida o JWT (JWKS, iss, aud, tid, exp/nbf, scp ou roles). `permissoes.py` aplica papel e dono do registro. `rotas.py` tem `/api/eu` e `/api/painel`. |
| `api/function_app.py` | Ponte para o Azure Functions (Python v2). |
| `dev_server.py` | Servidor local em `http://localhost:4280/`, com a mesma lógica e os mesmos cabeçalhos. |

## Rodar local
1. Copie `api/local.settings.example.json` para `api/local.settings.json`. Copie também `web/config.example.js` para `web/config.js`. Preencha os dois com o Tenant ID e o Client ID. Esses arquivos ficam fora do repositório.
2. Rode `python3 central/dev_server.py` e abra `http://localhost:4280/`.

## Testes
`cd central/api && python3 -m unittest -v`

São 28 testes, sobre token e permissões, e não dependem do Azure.

## Etapas
| Etapa | O que | Situação |
|---|---|---|
| 1 | Login | Pronto local. Falta a TI cadastrar o redirect e os papéis. |
| 2 | API e validação | Pronta, com testes. |
| 3 | Gravações com permissão e auditoria | A fazer. |
| 4 | Rotinas pela API (client credentials) | A fazer. |
| 5 | Publicação de dados | A fazer. |
| 6 | Corte | A fazer. |
