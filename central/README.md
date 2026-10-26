# Central Partners com SSO Microsoft Entra ID

Plano: `docs/sso-entra/diagnostico-e-plano.md`. Roteiro da TI: `docs/sso-entra/orientacoes-ti-2026-10-19.md`.

| Pasta | O que é |
|---|---|
| `web/` | Painel (SPA). Login com MSAL.js 5.24.0 (Authorization Code + PKCE), hospedado no próprio site. `staticwebapp.config.json` traz a CSP e os cabeçalhos de segurança. |
| `api/central_api/` | `token.py` valida o JWT (JWKS, iss, aud, tid, exp/nbf, scp ou roles). `permissoes.py` aplica papel e dono do registro. `rotas.py` tem `/api/eu`, `/api/painel`, as rotas da esteira com login (`/api/regime`, `/api/esteira*`) e a porta do PRM (`/api/prm/*`). `caminhos.py`: todo caminho por variável (L5). |
| `api/central_api/prm/` | **PRM Save v2**: regras, máquinas de estado, autorização por linha, repositório (JSON e SQL), rotas. Contrato: `docs/prm/v2/06-contrato-api.md`. Entrega: `docs/prm/v2/07-entrega-dev.md`. |
| `api/function_app.py` | Ponte para o Azure Functions (Python v2): `eu`, `painel`, `prm/{*resto}`, `regime`, `esteira*`. |
| `dev_server.py` | Servidor local em `http://localhost:4280/`, com a mesma lógica e os mesmos cabeçalhos. `--prm` liga o PRM em modo local. |
| `web/prm.html`, `prm.js`, `prm.css`, `prm-componentes.css` | As duas faces do PRM: parceiro (claro, barra inferior) e Save (escuro, seção Canal). |

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

## PRM Save em modo local (Fase 1, sem Azure)
```
python3 central/dev_server.py --prm                 # http://localhost:4280/prm.html · dados fictícios · login simulado
python3 central/dev_server.py --prm --manter        # continua a demo de onde parou (sem recarregar as fixtures)
python3 central/dev_server.py --dados ~/agentes-partners/registro/prm   # sobre o registro/prm/ real (gerado pelo prm_local.py)
```
- **Login simulado:** a tela inicial lista os usuários de teste (Titular do Master A, Consultor A1, Daniela, Luis, Financeiro) e os CNPJs de teste com o cenário de cada um. Só existe com `PRM_LOGIN_SIMULADO=1`, Host localhost e fora da Azure; em produção o login é o MSAL (Entra).
- **Dados:** `central/api/central_api/prm/fixtures/demo.json` (Masters A–I, Empresas 01–21, CNPJs alfanuméricos fictícios com o dígito calculado na carga). O estado da demo fica em `registro/prm-demo/` (fora do git) e é refeito a cada início.
- **Sem rede:** a Receita de teste responde às empresas fictícias; outro CNPJ cai em "a Receita não respondeu" (use `--externa` para consultar as APIs públicas, o que manda o CNPJ para fora).
- **Não lê** `local.settings.json` nem o `config.js` real (serve um `config.js` vazio).
- **Rotina diária** (expiração, prorrogação, avisos M-14/M-04/M-16, escala de prazo): botão "Rodar rotina diária agora" na Visão do canal (perfil Luis) ou `POST /api/prm/save/rotina`.
- **Parâmetros:** `central/api/central_api/prm/parametros.json` (padrões da especificação); `PRM_PARAMETROS=<arquivo.json>` sobrepõe sem deploy.

Variáveis: `PRM_REPO` (`json` | `sql`), `PRM_DADOS` (pasta do modo local), `PRM_SQL` (Fase 2), `PRM_API_CLIENT_ID` e `PRM_SCOPE` (registro do portal do parceiro na Fase 2), `PRM_REGISTRO_DEMANDAS` (numera pelo registro único `registro/demandas.json`), `PRM_ESPELHAR_CAIXA=1` (alerta interno também na fila do `lib/caixa.py`), `PRM_AUDITOR`, `PRM_SLA_JSON`, `PRM_CATALOGO_CENTRAL`, `CENTRAL_LIB`, `CENTRAL_REPO`, `PARTNERS_AP`.

## Testes
```
cd central/api && PYTHONPATH=../../lib python3 -m unittest                         # tudo: 331 testes
cd central/api && PYTHONPATH=../../lib python3 -m unittest discover -p 'test_prm*'  # só o PRM: 177 testes
node --check central/web/prm.js
```
Os 154 testes da Central (token, permissões, regime, negócio ativo, esteira, dossiê) seguem passando. Os 177 do PRM cobrem calendário e dias úteis, catálogo de textos com o auditor de promessas, auditor único, os dois repositórios, autorização por linha (404 fora do escopo), login simulado e token, resposta neutra idêntica com piso de tempo, estados e prazos do registro, conflito, prorrogação e expiração, anti-varredura persistente, regra única de proteção, consulta de Lucro Real, dossiê, extrato e contestação, demandas com histórico e chamado em rascunho, decidir com trilha, notificações, nível em sombra e visão do canal. Nenhum depende do Azure nem de rede.

## Etapas
| Etapa | O que | Situação |
|---|---|---|
| 1 | Login | Pronto local. Falta a TI cadastrar o redirect e os papéis. |
| 2 | API e validação | Pronta, com testes. |
| 3 | Gravações com permissão e auditoria | PRM: `POST /api/prm/save/decidir` com trilha (`prm_decisao`) e trilha de acesso; Fase 1 local. |
| 4 | Rotinas pela API (client credentials) | A fazer. |
| 5 | Publicação de dados | A fazer. |
| 6 | Corte | A fazer. |
