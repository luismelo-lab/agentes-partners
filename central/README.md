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

## Demo da consulta de Lucro Real (parceiros)
`python3 central/consulta_demo.py` → `http://localhost:4281/consulta.html`. Sem login, só localhost. **Sem base local:** consulta o Minha Receita e, se falhar, a BrasilAPI (mesma fonte, a segunda é reserva). O CNPJ digitado sai para essas APIs: `CENTRAL_API_EXTERNA=0` desliga; no piloto depende do ok do Jurídico e da TI. Regras em `api/central_api/regime.py`: faixas confirmado / provável / não é Real / sem dado / indisponível, ano-base e fonte em toda resposta, cache em memória de 24 h, lote de até 20 (4 em paralelo), teto diário, trilha em `dados-publicos/receita/consultas-regime.jsonl`. Testes (sem rede): `cd central/api && PYTHONPATH=../../lib python3 -m unittest tests.test_regime`.

### Esteira para o parceiro (agentes + aprovação, sem depender do Mac)
Fluxo: consulta → 1ª checagem (`negocio_ativo.py`: empresa com negócio aberto ou ganho no HubSpot, por raiz; a API só vê chaves HMAC, nunca a lista de clientes; sem índice falha fechada e não chama API externa) → botão "Pedir análise e esteira" (`esteira.py` grava o pedido em `central-esteira/pedidos/`) → agentes (`rotinas/esteira-parceiro.md`, rodada pelo workflow `.github/workflows/esteira-parceiro.yml`, **desligado**: liga com `AGENTES_NUVEM` e `AGENTES_IA`) → `publicar` passa pelo auditor de promessas → `CENTRAL_APROVACAO=obrigatoria` (teste, um aprovador: `python3 -m central_api.esteira aprovar --id E-0001 --quem Nome`, ou o campo `aprovar` do workflow) ou `autonoma` (entrega sozinha se a auditoria passar; com alerta vai à revisão humana). O estado viaja pelo SharePoint (`lib/estado.py`), nunca pelo GitHub. O índice é montado por `python3 -m central_api.negocio_ativo construir` (rodar na rotina Dados do dia, com `CENTRAL_SAL` como segredo). Testes: `tests.test_esteira`.

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
