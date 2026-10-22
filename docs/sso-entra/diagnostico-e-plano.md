# Central Partners · Autenticação SSO Microsoft Entra ID
**Diagnóstico técnico e plano de implementação** · 16/10/2026 · Área Partners (Save Co.) · Para validação do Luis e da TI antes de qualquer alteração.
Aplicativo registrado pela TI: **SAVE-SSO-MASTERS**, contas "Somente minha organização". Os identificadores aparecem aqui como `<TENANT_ID>`, `<CLIENT_ID>` e `<API_CLIENT_ID>`; os valores reais ficam só nas variáveis de ambiente e no portal do Entra.

## 1. Arquitetura atual (diagnóstico)
| Camada | Como é hoje | Implicação para o SSO |
|---|---|---|
| **Frontend** | Página única HTML/JS (Central Partners) publicada como **Artifact no claude.ai**. Protótipo v8 em `portal/prototipo/modelo.html`; produção em `portal/index.html`. | O domínio é do claude.ai: não dá para registrar URI de redirecionamento nem controlar sessão, cookies ou cabeçalhos de segurança. **O SSO exige hospedar o painel num endereço da Save.** |
| **Backend** | Não existe API. Os dados são gerados no Mac (`dados.json`, scripts Python em `lib/`, `infra/`, `skills/`) e publicados junto com a página. | Sem backend, não há onde validar token nem aplicar permissão. **É preciso criar uma API.** |
| **Banco de dados** | Base do Artifact (coleções `pedidos`, `chamados`, `acoes_demandas`, `recuperador`, `conselho`, `apontamentos`), sincronizada pelas rotinas (`lib/painel_sync.py`, `lib/chamados_painel.py`) e por JSON locais em `registro/`. | As gravações vão para um repositório da Save, atrás da API. |
| **Autenticação atual** | Conta do Claude: quem abre o link compartilhado. A pessoa é identificada pelo **nome do perfil** (`user.me()`), e o dono do Artifact é tratado como Luis. No protótipo, "Ver como" troca de pessoa no navegador. | Identidade fraca, sem papéis e sem autorização no servidor. Substituída integralmente. |
| **Integrações** | HubSpot (leitura por token de app privado), GLPI (OAuth por pessoa), Microsoft Graph (e-mail e arquivos, em liberação), Eazybe (WhatsApp via HubSpot), rotinas no Mac (launchd) e no Claude (tarefas agendadas), GitHub (código). | Preservadas: a mudança afeta só a camada de acesso do painel e onde as decisões são gravadas. |

## 2. Arquitetura recomendada
```
Navegador (Daniela, Geovana, Jenifer, Luis)
   │  OIDC · Authorization Code + PKCE (MSAL.js / @azure/msal-browser)
   ▼
Microsoft Entra ID  ── emite ID token + access token (audiência = API da Central, roles nas claims)
   │
   ▼
Frontend SPA (painel atual) ── hospedado em Azure Static Web Apps (domínio da Save, HTTPS, CSP)
   │  Authorization: Bearer <access token>  (escopo api://<API_CLIENT_ID>/Central.Acesso)
   ▼
API da Central (Azure Functions, Python) ── valida JWT (assinatura via JWKS, iss, aud, tid, exp/nbf, scp, roles)
   │                                         autoriza por papel e por dono do registro; audita cada gravação
   ├── Armazenamento das decisões e dos dados do painel (Azure Table Storage ou Lista do SharePoint via Graph)
   └── Agentes (rotinas) ── fluxo client credentials, papel de aplicativo "Agentes.Processar" (sem usuário)
```
**Por que assim:**
- **Code + PKCE no navegador:** é o padrão atual da Microsoft para SPA, sem segredo no frontend.
- **API separada:** a validação e a permissão acontecem no servidor, como pede o item 9. A tela só esconde o que o servidor já recusaria.
- **Azure:** tudo no locatário da Save, o que resolve a pendência de LGPD do painel fora do ambiente da empresa.
- **Agentes:** continuam iguais. Só trocam a ferramenta `ArtifactData` por chamadas à API, com credencial de aplicativo.

**Bibliotecas oficiais:**
- Frontend: `@azure/msal-browser`, ou `@azure/msal-react` se migrarmos para React; não é necessário agora.
- API: `msal` para Python no fluxo dos agentes. A validação do JWT usa as chaves públicas do Entra (`https://login.microsoftonline.com/<TENANT_ID>/discovery/v2.0/keys`) com `PyJWT[crypto]`, a mesma lógica do Microsoft.Identity.Web.
- Alternativa de API em .NET com `Microsoft.Identity.Web`, se a TI preferir.

## 3. Configurações no Microsoft Entra ID (TI)
**Registro 1: SAVE-SSO-MASTERS (frontend, já criado)**
- **Plataforma "Aplicativo de página única (SPA)":**
  - redirect `https://<dominio-da-central>/` e `https://<dominio-da-central>/auth/redirect`;
  - em desenvolvimento, `http://localhost:4280/`.
  - PKCE já vem ativado na plataforma SPA.
- **Sem segredo de cliente:** SPA não guarda segredo. O link "Adicionar um certificado ou segredo" não deve ser usado neste registro.
- **Fluxo implícito:** desligado (nem token de acesso nem token de ID).
- **Permissões de API delegadas:**
  - `openid`, `profile`, `email`, `offline_access`, `User.Read`;
  - `api://<API_CLIENT_ID>/Central.Acesso` (do registro 2).
- **Tipos de conta:** "Somente minha organização", single-tenant, como está.

> **Atualização de 19/10/2026:** para simplificar a administração, a proposta passa a ser **um registro só**. O SAVE-SSO-MASTERS expõe a própria API (`api://<CLIENT_ID>/Central.Acesso`) e os papéis abaixo. A API aceita `aud` = `<CLIENT_ID>` ou `api://<CLIENT_ID>`. Roteiro da TI em `orientacoes-ti-2026-10-19.md`. O registro 2 abaixo fica como alternativa.

**Registro 2: SAVE-SSO-MASTERS-API (backend, a criar)**
- **Expor uma API:** URI `api://<API_CLIENT_ID>`, escopo delegado `Central.Acesso` ("Acessar a Central Partners").
- **Funções de aplicativo (App roles), atribuíveis a usuários e grupos:**

| Valor (claim `roles`) | Quem | O que pode |
|---|---|---|
| `Partners.Gestor` | Luis | Tudo, inclusive "ver como", aprovar chamados e Conselho, liberar envios |
| `Partners.Masters` | Daniela | A própria caixa e os chamados dela; parceiros e contratos; leitura de resultados |
| `Partners.BDR` | Jenifer | A própria caixa, as indicações e a prospecção; leitura de parceiros |
| `Partners.Tecnica` | Geovana | A própria caixa, recorrência, Recuperador, Revisor e decisões técnicas |
| `Partners.Leitura` | Convidados da diretoria | Só leitura agregada, sem dado de cliente |
| `Agentes.Processar` (tipo Aplicativo) | Identidade das rotinas | Ler as decisões pendentes e gravar resultados; sem tela |

- **Aplicativos empresariais → SAVE-SSO-MASTERS-API → Propriedades → "Atribuição necessária?" = Sim.** Quem não recebeu um papel não entra, mesmo com e-mail corporativo (item 10).
- **Credencial só para as rotinas:** certificado de preferência (ou segredo com validade curta) no Azure Key Vault, nunca no código.
- **Configuração do token:** versão 2 do token de acesso (`accessTokenAcceptedVersion: 2`) e claim `roles`. Grupos não são necessários.
- **Acesso Condicional (TI):** MFA obrigatório e bloqueio de países fora do Brasil, se for política da Save.

## 4. Autorização no backend (regra de ouro: o servidor decide)
Cada requisição passa por três checagens:
1. **Token:** assinatura pelas chaves do Entra (JWKS, com cache e rotação), `iss` = `https://login.microsoftonline.com/<TENANT_ID>/v2.0`, `aud` = `<API_CLIENT_ID>`, `tid` = `<TENANT_ID>`, `exp`, `nbf`, e `scp` contendo `Central.Acesso`. Para aplicativo, `roles` contendo `Agentes.Processar`. Se falhar: 401.
2. **Papel:** a ação exige o papel da tabela. Se faltar: 403, com registro em log.
3. **Dono do registro:** a analista só altera itens em que `pessoa` = ela mesma, comparada pelo `oid` do token, nunca pelo nome. Só o Gestor altera qualquer item. "Ver como" vira consulta do Gestor no servidor, e não troca de identidade no navegador.

**Auditoria:** cada gravação registra `oid`, papel, ação, item, antes e depois e data e hora. Exemplos: aprovar chamado, decidir recorrência, marcar demanda.

**Sessão:**
- O token de acesso dura 60–90 minutos.
- O MSAL renova em silêncio e guarda em `sessionStorage`, nunca em `localStorage`.
- No logout, o MSAL encerra a sessão local e chama o endpoint de logout do Entra.
- O SSO no navegador segue a política de sessão da Save no Entra.

**Proteções do frontend:**
- Content-Security-Policy restrita (scripts só da própria origem e da biblioteca oficial).
- Sem `innerHTML` com dado não escapado; o painel já escapa tudo com `esc()`.
- HTTPS, HSTS e `X-Frame-Options: DENY` pelo `staticwebapp.config.json`.

## 5. Plano incremental (cada etapa com testes e critério de pronto)
| Etapa | O que | Testes | Pronto quando |
|---|---|---|---|
| **0 · Preparar (TI + Luis)** | Criar o registro 2, os papéis, a atribuição obrigatória e o Static Web App (plano Standard, por causa do provedor Entra personalizado e da API própria) | Conferência das configurações da seção 3 | Papéis atribuídos às 4 pessoas |
| **1 · Login (frontend)** | Hospedar o painel no SWA; MSAL com Code + PKCE; tela "Entrar com a Microsoft"; logout; sem papel = tela "sem acesso" | Login real com cada uma; usuário da Save sem papel recusado; token expirado renovado; logout | As 4 entram e um usuário sem papel não entra |
| **2 · API e validação** | API mínima `GET /api/eu` (identidade e papéis) e `GET /api/painel` (dados por papel) com validação completa do JWT | Testes automáticos: token válido; assinatura inválida; `aud`, `iss` ou `tid` errados; expirado; sem `scp`; sem papel (403); cada papel vê só o que pode | 100% dos testes passam e o painel carrega pela API |
| **3 · Gravações com permissão** | Mover as ações (aprovar chamado, recorrência, Conselho, demandas, pedidos, tarefa) do banco do Artifact para a API, com regra de dono e auditoria | Para cada ação: o dono grava; outra analista recebe 403; o Gestor grava; tudo vai para a auditoria | Nenhuma ação depende mais do banco do Artifact |
| **4 · Agentes pela API** | As rotinas usam client credentials (`Agentes.Processar`) para ler pendências e gravar resultados, no lugar do ArtifactData | Rodada completa em ambiente de teste; credencial do agente não acessa endpoint de usuário | Rotinas de um dia inteiro sem erro |
| **5 · Publicação de dados** | O `dados.json` sai do Mac (ou do GitHub Actions) direto para o armazenamento da Save, sem passar pelo repositório | Dado novo aparece no painel; o repositório continua sem dados de cliente (trava `checar-dados.py`) | Atualização diária automática |
| **6 · Corte** | O painel novo vira o oficial e o Artifact fica só leitura por 2 semanas, depois sai | Uso real de uma semana com as 4 pessoas | O Luis aprova o corte |

## 6. O que será entregue ao final (previsto, a confirmar a cada etapa)
**Arquivos:**
- `central/frontend/` (o painel atual adaptado, mais `auth.js` com MSAL e `staticwebapp.config.json`);
- `central/api/` (Azure Functions em Python: `validar_token.py`, `permissoes.py`, `rotas_*.py`, `auditoria.py`, testes em `tests/`);
- `lib/central_api.py` (cliente das rotinas, em client credentials);
- ajustes em `lib/painel_sync.py`, `lib/chamados_painel.py`, `rotinas/central-agentes-email.md` e `.github/workflows/central-deploy.yml`.

**Dependências:**
- frontend: `@azure/msal-browser`, carregada de CDN com versão fixa e integridade SRI;
- API: `azure-functions`, `PyJWT[crypto]`, `requests`, `msal` (só nas rotinas), `azure-data-tables` (se Table Storage).

**Variáveis de ambiente:**
- **Frontend (públicas):** `ENTRA_TENANT_ID`, `ENTRA_CLIENT_ID`, `ENTRA_API_SCOPE`, `CENTRAL_API_URL`.
- **API:** `ENTRA_TENANT_ID`, `ENTRA_API_CLIENT_ID`, `ENTRA_ISSUER`, `STORAGE_CONNECTION` (por identidade gerenciada, de preferência).
- **Rotinas:** `ENTRA_TENANT_ID`, `ENTRA_AGENTE_CLIENT_ID`, mais o certificado ou segredo no Key Vault ou no `.env` local, nunca no repositório.

## 7. Riscos
1. **Dependência da TI:** sem o registro 2, os papéis e o SWA, nada avança. Mitigação: a etapa 0 tem lista fechada.
2. **Dois painéis em paralelo durante a migração:** pode haver decisão gravada no lugar errado. Mitigação: o corte é por ação, na etapa 3, com o Artifact em modo só leitura para cada ação já migrada.
3. **Token no navegador (XSS):** mitigação com CSP, escape já existente, `sessionStorage` e sem bibliotecas de terceiros fora da oficial.
4. **Credencial das rotinas vazada:** mitigação com certificado, papel mínimo (`Agentes.Processar`), rotação e Key Vault.
5. **Custo:** SWA Standard e Functions de consumo; a TI confirma o valor atual.
6. **Mac como ponto único:** continua até as rotinas irem para a nuvem; não piora com o SSO.
7. **Usuário sem papel no primeiro dia:** mitigação: atribuir os papéis antes da etapa 1 e manter o "sem acesso" com o contato do Luis.

## 8. Implantação
1. A TI conclui a etapa 0.
2. Publicar o frontend e a API num ambiente de homologação (slot de preview do SWA).
3. Rodar os testes da etapa.
4. O Luis valida com as 4 pessoas.
5. Promover para produção.
6. Atualizar a URI de redirecionamento de produção.
7. Comunicar o novo endereço.

Cada etapa só começa com a anterior aprovada.

## 9. Rollback
- **Frontend e API:** o SWA mantém as versões; volta-se para a anterior pelo portal ou pelo `git revert` do workflow de deploy.
- **Gravações:** cada ação migrada mantém, até o corte, a gravação espelhada no fluxo antigo. Para voltar, aponta-se a ação de novo para o banco do Artifact (chave de configuração `CENTRAL_FONTE=artifact`).
- **Entra:** desativar o registro ou tirar a atribuição de papéis bloqueia o acesso na hora, sem apagar nada.
- **Rotinas:** a variável `CENTRAL_FONTE=artifact` faz voltar ao `ArtifactData`.

> **22/10/2026 (D89):** aprovados o Azure Static Web Apps (Standard) e o Table Storage.

## 10. Decisões para começar
1. **Hospedagem:** aprovar Azure Static Web Apps (Standard) e Azure Functions no locatário da Save. A alternativa é App Service, que custa mais e não traz ganho para este uso.
2. **Armazenamento:** Azure Table Storage (simples e barato) ou Lista do SharePoint (o time vê também pelo SharePoint).
3. **Papéis:** aprovar a tabela da seção 3 e quem recebe cada um.
4. **Quem faz a etapa 0:** a TI, com esta seção 3 como roteiro.
