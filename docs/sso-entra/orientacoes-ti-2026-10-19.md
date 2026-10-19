# Central Partners · SSO Entra ID · Orientações para a TI

Data: 19/10/2026. Esta orientação continua o registro **SAVE-SSO-MASTERS**, já criado pela TI. Ele é single-tenant, está ativado e tem o Luis como proprietário. O plano completo está em `Central-Partners-SSO-Entra-Diagnostico-e-Plano.docx`.

## 1. Resposta às pendências da validação
| Configuração | Resposta |
|---|---|
| Plataforma | **Aplicativo de página única (SPA).** Não usar "Web". O login roda no navegador com Authorization Code + PKCE (biblioteca oficial MSAL.js 5.24.0). Quem valida o token e as permissões é a API da Central. |
| URI de redirecionamento | **Agora:** `http://localhost:4280/` (ambiente de teste local do Luis). **Produção:** o endereço do Azure Static Web App, que é criado na etapa de hospedagem, com barra no fim (ex.: `https://central-partners.savecompany.com.br/`). |
| Certificado ou segredo | **Não criar** neste registro. SPA não guarda segredo. Segredo ou certificado só existirá depois, para as rotinas automáticas (etapa 4), guardado no Azure Key Vault. |
| Permissões de API | `openid`, `profile`, `offline_access`, `User.Read` (delegadas) e o escopo próprio `Central.Acesso` (item 3). |
| Controle de usuários | **Atribuição necessária = Sim** e papéis atribuídos só às pessoas autorizadas (itens 4 e 5). |

## 2. Authentication (Preview)
1. **Adicionar o URI de redirecionamento** → plataforma **Aplicativo de página única (SPA)** → `http://localhost:4280/`.
2. Em **Configurações**: deixe **desmarcados** "Tokens de acesso" e "Tokens de ID" (fluxo implícito). O PKCE já vem ativo na plataforma SPA.
3. **URL de logoff do canal frontal:** deixar em branco por enquanto.

## 3. Expor uma API (simplificação: um registro só)
O plano de 16/10 previa um segundo registro para a API. Para ficar mais simples de administrar, a proposta é usar o **mesmo** SAVE-SSO-MASTERS. Ele é o aplicativo do painel e expõe a própria API. A segurança é a mesma: a API confere o público (`aud`) do token, a assinatura e os papéis.
1. **Expor uma API → URI da ID do aplicativo → Adicionar:** aceitar o padrão `api://<ID do aplicativo>`.
2. **Adicionar um escopo:**
   - nome: `Central.Acesso`;
   - quem pode consentir: **somente administradores**;
   - nome de exibição: "Acessar a Central Partners";
   - estado: **Habilitado**.
3. **Permissões de APIs → Adicionar → Minhas APIs → SAVE-SSO-MASTERS → `Central.Acesso`** (delegada). Depois, **Conceder consentimento do administrador**.
4. **Manifesto:** `"requestedAccessTokenVersion": 2` (no manifesto novo fica em `api`; no antigo, `accessTokenAcceptedVersion: 2`).

## 4. Funções de aplicativo (papéis)
Criar em **Funções de aplicativo**. A coluna Valor deve ser idêntica à tabela, porque a API compara texto exato.

| Nome de exibição | Valor | Tipos de membro | Para quem |
|---|---|---|---|
| Gestor | `Partners.Gestor` | Usuários/Grupos | Luis |
| Masters | `Partners.Masters` | Usuários/Grupos | Daniela |
| BDR | `Partners.BDR` | Usuários/Grupos | Jenifer |
| Técnica | `Partners.Tecnica` | Usuários/Grupos | Geovana |
| Leitura | `Partners.Leitura` | Usuários/Grupos | Convidados da diretoria (só números agregados) |
| Agentes | `Agentes.Processar` | Aplicativos | Identidade das rotinas (etapa 4; pode criar já) |

## 5. Aplicativos empresariais → SAVE-SSO-MASTERS
1. **Propriedades → Atribuição necessária? = Sim.** Sem isso, qualquer conta da Save entraria.
2. **Visível para os usuários?** Pode ficar Sim, para aparecer no portal Meus Aplicativos.
3. **Usuários e grupos → Adicionar atribuição:** Luis = Gestor, Daniela = Masters, Jenifer = BDR, Geovana = Técnica. **Começar só com o Luis** para o teste local. Os outros três entram depois que o teste passar.
4. **Acesso Condicional:** aplicar a política da Save, com MFA obrigatório.

## 6. Identidade visual e Propriedades (opcional)
- Logotipo: o símbolo da Save (o Luis envia o PNG).
- URL da home page: deixar vazio até existir o endereço de produção.
- Termos e privacidade: usar os da Save, se existirem.
- Domínio do editor: `savecompany.com.br` (já está).

## 7. Hospedagem (decisão pendente, para a produção)
- **Azure Static Web Apps, plano Standard,** no locatário da Save, para o painel e a API (Azure Functions em Python).
- **Domínio próprio sugerido:** `central-partners.savecompany.com.br`. A TI cria o CNAME no DNS.
- Quando o Static Web App existir, adicionar o redirect de produção (item 2) e as variáveis `CENTRAL_TENANT_ID` e `CENTRAL_API_CLIENT_ID` nas configurações da API.

## 8. O que já está pronto do lado do projeto (19/10)
- **Painel:** tela de login no padrão Save, com MSAL.js 5.24.0 hospedado no próprio site (sem CDN). A sessão fica em `sessionStorage`, e o logout encerra a sessão no Entra.
- **API (`/api/eu`, `/api/painel`):**
  - valida assinatura (JWKS com cache e rotação), emissor, público, locatário, validade e escopo;
  - aplica papel e dono do registro;
  - quem não tem papel recebe 403.
- **28 testes automáticos passando:** assinatura falsa, token expirado, público, emissor ou locatário errado, sem escopo, sem papel e dono do registro.
- **Cabeçalhos de segurança:** CSP restrita, HSTS, `X-Frame-Options: DENY` e `nosniff`.
- **IDs:** ficam em arquivos locais fora do repositório. Nenhuma credencial vai no código.

## 9. Teste que o Luis faz depois dos itens 2 a 5
1. Rodar `python3 central/dev_server.py` e abrir `http://localhost:4280/`.
2. Clicar em "Entrar com a Microsoft". O resultado esperado é aparecer "Olá, Luis", com o papel **Partners.Gestor**.
3. Teste negativo: entrar com uma conta da Save **sem** papel. O resultado esperado é o Entra recusar o acesso.
