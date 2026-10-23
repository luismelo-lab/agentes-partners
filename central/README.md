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

### Esteira para o parceiro (dossiê instantâneo + agentes + aprovação, sem depender do Mac)
Fluxo:
1. **Consulta** de regime (Minha Receita, BrasilAPI de reserva). Cada consulta vai para o **histórico do parceiro** (últimas 30 empresas, `esteira.registrar_consulta`); a mesma empresa consultada de novo em até 7 dias sai do histórico, sem nova chamada às APIs.
2. **1ª checagem** (`negocio_ativo.py`): empresa com negócio aberto ou ganho no HubSpot, por raiz do CNPJ. A API só vê chaves HMAC, nunca a lista de clientes. Sem índice, falha fechada: não chama API externa. **Negócio ativo, índice ausente e tetos (diário e de acertos) devolvem a mesma mensagem neutra** ("Não foi possível seguir com esta consulta. Fale com a Área Partners.", faixa `indisponivel`, sem empresa nem detalhe); o parceiro não distingue um caso do outro. O motivo real (`negocio_ativo`, `indice_ausente`, `teto_diario`, `negocio_ativo_acima_do_teto`) vai só para o log e para a trilha `consultas-regime.jsonl`, nunca para a resposta. Passado `CENTRAL_LIMITE_ATIVO` acertos por dia, sai alerta no log (possível varredura da carteira).
3. **"Pedir análise e esteira"** (`esteira.solicitar`): grava o pedido em `central-esteira/pedidos/` e **entrega na hora o dossiê-base** (`dossie_base.py`, montado por código a partir do perfil da Receita, do playbook do setor, das objeções e dos cases aprovados; 9 seções, sem chamar o Claude). Pedido aberto, ou entregue há menos de 30 dias, da mesma empresa e do mesmo parceiro é reaproveitado.
4. **Aprofundamento:** com `CENTRAL_ENRIQUECER=1` (padrão), o pedido fica `enriquecer=pendente` e os agentes da nuvem (`rotinas/esteira-parceiro.md`, workflow `.github/workflows/esteira-parceiro.yml`, **desligado**: liga com `AGENTES_NUVEM` e `AGENTES_IA`) trocam o base por uma versão mais específica com `python3 -m central_api.esteira fila | enriquecer | publicar`. Pedido sem perfil (sem base) é montado do zero e sai por `publicar`.
5. **Portão de auditoria** (auditor de promessas, `depto-qualidade`): `enriquecer` só substitui o dossiê se não houver alerta ALTO ou MÉDIO; com alerta, o parceiro continua com a versão-base e o pedido fica `alerta` (sem nova tentativa; a rotina pré-checa antes). `CENTRAL_APROVACAO=obrigatoria` (padrão, teste com um aprovador: `python3 -m central_api.esteira aprovar --id E-0001 --quem Nome`, ou o campo `aprovar` do workflow) exige um aprovador para o que sai de `publicar`; `autonoma` entrega sozinha se a auditoria passar, e com alerta vai à revisão humana.
6. **Word sob demanda:** o `.docx` (Design System Save) é gerado quando o parceiro pede o download, a partir do dossiê vigente. Exige Node com a biblioteca `docx` (`NODE_PATH=~/.partners-node/node_modules`).

O estado viaja pelo SharePoint (`lib/estado.py`), nunca pelo GitHub. O índice é montado por `python3 -m central_api.negocio_ativo construir` (rotina "Dados do dia", com `CENTRAL_SAL` como segredo). Variáveis: `CENTRAL_ESTEIRA` (pasta de estado), `CENTRAL_SAL`, `CENTRAL_APROVACAO`, `CENTRAL_ENRIQUECER` (`0` desliga o aprofundamento). Testes: `tests.test_esteira`.

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
