# Pedido ao TI: consulta de Lucro Real e esteira para parceiros, rodando na nuvem
**Rascunho de pedido · 23/10/2026 · solicitante: Luis Fernando de Melo (Gerente Comercial · Parceiros Masters) · NADA FOI ENVIADO.** O Luis revisa e envia pelo canal oficial (GLPI, e-mail ou reunião).

## Contexto
A Área Partners construiu um site em que os parceiros (Masters e indicadores) consultam se uma empresa está no Lucro Real e recebem um dossiê com a análise da Save. O código está pronto e testado (154 testes) no repositório `agentes-partners`, pasta `central/`. Hoje só roda no Mac do Luis, em modo de demonstração e sem login. Para o piloto com parceiros reais, e para não depender de um computador ligado, precisamos dos itens abaixo. O passo a passo técnico está em `docs/NUVEM.md` e `central/README.md`.

Fica **fora deste pedido** qualquer token de API (Claude, HubSpot e o token de disparo do GitHub). O Luis trata esses separadamente.

## 1. GitHub
**Já feito pelo Luis em 23/10/2026 (repositório `luismelo-lab/agentes-partners`, privado):** Actions habilitado com permissão padrão **somente leitura** e só ações do próprio GitHub permitidas (`checkout`, `cache`, `setup-node`); variáveis `AGENTES_NUVEM=desligado`, `AGENTES_IA=desligado`, `CENTRAL_APROVACAO=obrigatoria` e `GRAPH_PASTA`. Os fluxos continuam desligados.

**Fica para o TI:**
| # | Pedido | Detalhe |
|---|---|---|
| 1.1 | Repositório **privado** `agentes-partners` na organização da Save | Acesso só para o Luis e o TI. O repositório hoje está na conta pessoal do Luis e deve migrar (Settings → Transfer ownership). Mantém histórico, variáveis e fluxos. |
| 1.2 | **Plano da organização com recursos de segurança** | No plano gratuito de conta pessoal o GitHub **não oferece** proteção de branch nem secret scanning para repositório privado (testado em 23/10: erro 403 e 422). Na organização, ativar secret scanning com push protection e proteção da `main` (sem push direto; merge por pull request com o Luis como revisor). Até lá, vale o hook `infra/checar-dados.py` antes de cada commit. |
| 1.3 | Variáveis ainda em branco | `AGENTES_CAIXA` e `GRAPH_SITE_ID` (vêm dos itens 2.1 e 2.3). |

## 2. Microsoft 365 e SharePoint (já detalhado em `integracoes-microsoft.md`, itens 1 a 3)
| # | Pedido | Para quê |
|---|---|---|
| 2.1 | Caixa compartilhada `agentes.partners@savecompany.com.br` | Central de Agentes por e-mail. |
| 2.2 | Aplicativo no Entra ID com `Mail.ReadWrite` e `Mail.Send` restritos à caixa 2.1 e `Sites.Selected` só no site 2.3 | Os agentes lerem e escreverem sem o Outlook do Mac. Credenciais do aplicativo (ID do locatário, ID do cliente e segredo) entram como segredos do GitHub: `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`. |
| 2.3 | Site do SharePoint "Área Partners · Agentes" com a pasta restrita **"Estado dos agentes"** | Guardar o estado entre as rodadas: pedidos dos parceiros, dossiês e Word, histórico de consultas e o índice de clientes. **Nunca no GitHub.** Acesso: o aplicativo 2.2 e o Luis. |
| 2.4 | **Controle de versão** ligado na biblioteca da pasta 2.3 | Evita que uma rodada dos agentes sobrescreva um pedido criado pelo site no mesmo momento. |
| 2.5 | Rótulo de retenção de **12 meses** na pasta 2.3 com exclusão ao fim do prazo | Política de retenção sugerida pelo Jurídico. A pasta guarda a carteira de prospecção de cada parceiro. |

## 3. Hospedagem do site e login dos parceiros (Azure e Entra ID)
| # | Pedido | Detalhe |
|---|---|---|
| 3.1 | **Azure Static Web Apps** (plano Standard) para o site e **Azure Functions** (Python) para a API | O plano está em `docs/sso-entra/diagnostico-e-plano.md`. Domínio da Save com HTTPS (sugestão: `consulta.partners.savecompany.com.br`). Os cabeçalhos de segurança já estão em `central/web/staticwebapp.config.json`. |
| 3.2 | Cadastro do **redirect** do site no aplicativo `SAVE-SSO-MASTERS` e criação do papel **"Parceiro"** (acesso só à consulta e ao dossiê próprios) | Hoje o aplicativo só tem papéis do time interno. |
| 3.3 | **Como os parceiros entram?** | O aplicativo foi registrado como "Somente minha organização". Os Masters e os indicadores são empresas externas. Precisamos de uma das opções: convidados B2B no nosso Entra ID com o papel 3.2, ou Entra External ID para clientes. Pedimos a recomendação do TI. |
| 3.4 | Segredo `CENTRAL_SAL` | Sal (valor aleatório de 64 caracteres hexadecimais) da chave que protege o índice de clientes. Gerar com `openssl rand -hex 32`, guardar no cofre e usar o **mesmo valor** no GitHub (segredo do repositório) e no Azure (configuração da Function). Se mudar, o índice precisa ser reconstruído; a consulta falha fechada enquanto isso. |
| 3.5 | Node 20 no ambiente da Function | O Word do dossiê é gerado sob demanda com a biblioteca `docx` (Node). Alternativa: gerar o Word só nos fluxos do GitHub. |

## 4. Rotinas
| # | Pedido | Detalhe |
|---|---|---|
| 4.1 | Revisão do fluxo `Dados do dia` (`.github/workflows/diario.yml`) | A rotina agora também reconstrói todos os dias o índice de negócios ativos (comando `partners indice-ativos`, já programado no `manha` e no `tarde`). Precisa do segredo `CENTRAL_SAL` (3.4). O índice com mais de 3 dias gera aviso no log, e o site continua funcionando. |
| 4.2 | Alertas de log | Encaminhar ao TI os avisos `acertos de negócio ativo acima do teto` (possível varredura da carteira) e `índice … com N dias`. |

## Segurança
- A consulta de empresas que são clientes da Save **não sai** para serviços de terceiros: a primeira checagem usa só chaves criptografadas (HMAC) e, havendo acerto, a resposta ao parceiro é uma mensagem neutra, igual para os casos de índice ausente e de teto de uso.
- O processo do Claude nos fluxos da nuvem **não herda** as credenciais do SharePoint nem o sal do índice.
- Para um CNPJ de prospect, o número é enviado às APIs públicas Minha Receita e BrasilAPI. O Jurídico precisa aceitar isso por escrito antes do piloto (ver minuta de termos).

## Perguntas ao TI
1. Quem administra o Entra ID e o Azure, e qual o prazo para os itens 2.2, 3.1 e 3.2?
2. Qual a opção recomendada para os parceiros externos entrarem (3.3)?
3. A Save já tem política de domínio e certificado para um endereço novo do site (3.1)?
4. A organização do GitHub já existe? Quem faz a migração do repositório (1.1)?
5. O Azure Static Web Apps tem restrição de região (dados no Brasil) na política de LGPD da Save?
