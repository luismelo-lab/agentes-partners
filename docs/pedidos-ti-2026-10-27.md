# Necessidades e aprovações da TI · Área Partners

> 27/10/2026 · rascunho para o Luis, nada foi enviado. Junta e substitui os pedidos de 13/10 (`docs/pedidos-ti-2026-10-13.md`), 19/10 (`docs/sso-entra/orientacoes-ti-2026-10-19.md`), 23/10 (`docs/pedidos-ti-2026-10-23.md` e `departamentos/ti/pedido-esteira-parceiros-nuvem.md`) e a seção 5 do PRM (`docs/prm/v2/04-ti-arquitetura.md`). Onde os pedidos antigos divergiam, vale este.

## 1. Resumo
Os projetos da área estão prontos e testados no Mac, mas 1 de 4 integrações funciona (verificação de 27/10: só o HubSpot). O que falta depende da TI em três ondas:

| Onda | O que destrava | Custo | Aprovação antes |
|---|---|---|---|
| **1 · Agora** (nada a contratar) | E-mail da Central de Agentes (parado desde 06/10), chamados no GLPI, fase da execução no Bitrix e login do painel do time | Zero | Só a TI |
| **2 · Nuvem** (Azure) | Painel, consulta de Lucro Real e PRM fora do Mac, com login de parceiro, mais o WhatsApp direto do Eazybe | Cerca de US$ 10/mês em homologação e US$ 31 a 54/mês em produção, mais o plano da organização no GitHub | Luis (orçamento) e Jurídico (parecer LGPD) |
| **3 · Melhorias** (Microsoft 365) | Teams, Forms, Lists, retenção e conector do Claude | Dentro das licenças atuais, salvo o que a TI apontar | TI e Luis |

Pedimos à TI um responsável e uma data para cada item da onda 1 e uma reunião de 30 minutos para a onda 2.

## 2. Onda 1 · destrava o que já existe (nada a contratar)
| # | Projeto | Pedido à TI | Escopo mínimo | Situação em 27/10 |
|---|---|---|---|---|
| 1.1 | Central de Agentes (e-mail) | Caixa compartilhada `agentes.partners@savecompany.com.br` | Sem licença; Luis com Acesso Total e Enviar Como | Pedido em 13/10 e 23/10, sem retorno |
| 1.2 | Central de Agentes e OneDrive | Aplicativo **"Agentes Partners"** no Entra ID (Microsoft Graph) | `Mail.ReadWrite` e `Mail.Send` de aplicativo, restritos à caixa 1.1 por **RBAC for Applications** do Exchange; `Sites.Selected` só no site 2.6; certificado no lugar de segredo | Faltam no Mac os 4 dados (locatário, cliente, credencial e caixa). Em 22/10 havia 123 mensagens retidas |
| 1.3 | Chamados (GLPI 11) | Cliente OAuth **"Agentes Partners"** na API v2.1 de `tributario.savecompany.com.br` | Authorization code, escopos `api` e `user`; cada pessoa autoriza com o próprio usuário; sem conta de serviço | 11 chamados aprovados no painel esperam a abertura |
| 1.4 | Pós-venda (Bitrix24) | Webhook de entrada **"Agentes Partners - consulta execução"** | Permissão `crm`; usuário técnico só leitura em Negócios, Execução Lucro Real e Execução Holding; o programa só chama 5 métodos de leitura | Pedido em `docs/BITRIX.md`; as sentinelas de execução estão desligadas sem ele |
| 1.5 | Painel do time (SSO) | Concluir o registro **SAVE-SSO-MASTERS** conforme o roteiro de 19/10 | Redirect SPA `http://localhost:4280/`; expor a API com o escopo `Central.Acesso`; os 6 papéis; atribuição obrigatória; MFA por Acesso Condicional; começar só com o Luis | Registro criado pela TI; confirmar se as seções 2 a 5 do roteiro foram feitas |

**Devolver ao Luis:** os IDs públicos (locatário, cliente e caixa) por e-mail interno. Certificado, segredo e endereço do webhook só pessoalmente ou pelo cofre, nunca por e-mail ou chat. Fazer um teste conjunto de 15 minutos: um e-mail na caixa da área, um chamado em rascunho no GLPI e uma consulta ao Bitrix.

## 3. Onda 2 · tirar do Mac e abrir aos parceiros (Azure)
Um pedido só cobre o painel do time, a consulta de Lucro Real e o PRM. O PRM foi construído sobre a Central e usa o mesmo banco, a mesma API e o mesmo login. O detalhe e o código de implantação (Bicep) estão em `docs/prm/v2/04-ti-arquitetura.md` e `docs/prm/v2/infra/main.bicep`.

| # | Pedido à TI | Escopo mínimo | Para quê |
|---|---|---|---|
| 2.1 | Assinatura (nova ou existente) e grupos `rg-prm-save-hml` e `rg-prm-save-prd` | Reader para o Luis | Separar homologação de produção |
| 2.2 | Rodar o `main.bicep` (what-if, depois create) primeiro em homologação | Static Web Apps Standard; Function App Flex em Brazil South; Azure SQL só com login Entra; Key Vault; Blob; Application Insights; orçamento com alerta em 50, 80 e 100% | Hospedar painel, consulta e PRM |
| 2.3 | Registro **SAVE-PRM-PARCEIROS** (SPA, escopo `Prm.Acesso`, papel `Parceiro.Portal`, atribuição obrigatória) e os redirects de produção no SAVE-SSO-MASTERS | Single-tenant, sem segredo | Login do parceiro separado do login do time |
| 2.4 | Registros **PRM-ROTINAS** (papel `Agentes.Processar`, certificado no Key Vault) e **PRM-IMPLANTACAO-GITHUB** (credencial federada OIDC, Website Contributor só na Function) | Sem segredo no GitHub | Rotinas e implantação sem senha guardada |
| 2.5 | Convites **B2B** do piloto: titular e consultores de 1 Master (cerca de 5 pessoas) no grupo `PRM-Parceiros-Piloto`, com MFA | Política de convidados da Save | Parceiro externo entrar com segurança |
| 2.6 | Site do SharePoint **"Área Partners · Agentes"** com a pasta restrita "Estado dos agentes", controle de versão e retenção de 12 meses | Acesso só do aplicativo 1.2 e do Luis | Estado das rotinas na nuvem, nunca no GitHub |
| 2.7 | Segredo `CENTRAL_SAL` no Key Vault e no GitHub (mesmo valor) | Gerado pela TI com `openssl rand -hex 32` | Índice cifrado de clientes da consulta |
| 2.8 | Grupo administrador do SQL e o usuário da Function no banco (o comando vem pronto) | — | Banco sem usuário e senha |
| 2.9 | Receptor do **webhook do Eazybe** (WhatsApp) como mais uma função na Function App de 2.2 | Confere o token e grava a mensagem na pasta privada do Luis pelo Graph | Mensagens de parceiros sem passar por site de terceiro. Evita a licença Premium do Power Automate (opção A de `docs/whatsapp-webhook.md`) |
| 2.10 | Com o dono do CRM: aplicativo privado **"PRM leitura"** no HubSpot, com o token gravado pela TI no Key Vault | Só escopos de leitura | Sincronização dos negócios na nuvem (hoje é feita pelo token do Mac) |
| 2.11 | Repositório `agentes-partners` transferido para a **organização da Save no GitHub**, com secret scanning, push protection e proteção da `main` | Acesso só do Luis e da TI | No plano pessoal o GitHub não oferece essas proteções em repositório privado (testado em 23/10) |
| 2.12 | DNS: `central-partners.savecompany.com.br` e `parceiros.savecompany.com.br` (CNAME e certificado gerenciado) | — | Endereço da Save no lugar do endereço da Azure |
| 2.13 | Revisão de segurança antes do primeiro parceiro, depois a produção | Teste negativo: convidado sem papel não entra | Abrir ao piloto |

**Custo (preço de lista em US$, API de preços da Azure, 26/10/2026; estimativa):**
- homologação: cerca de US$ 10/mês;
- produção: US$ 31 a 54/mês, conforme haja ou não rede privada (+US$ 23/mês);
- GitHub: o preço do plano da organização a TI confirma.

O Codespaces e o GitHub Actions já usados no desenvolvimento ficam na conta atual e não pedem nada à TI.

## 4. Onda 3 · melhorias no Microsoft 365
| # | Pedido | Ganho |
|---|---|---|
| 3.1 | Equipe no Teams "Área Partners", com canais por célula e um fluxo do Workflows por canal, só para postar | Resumos e alertas onde o time já trabalha |
| 3.2 | Microsoft Forms "Pedido aos agentes" com fluxo para a caixa 1.1 | Pedido chega completo |
| 3.3 | Aprovações do Power Automate e Microsoft Lists "Pedidos e pendências" | Aprovar com um clique e ver o quadro no Teams |
| 3.4 | Leitura de calendário delegada (`Calendars.Read`), só para Daniela, Jenifer e Geovana, com o consentimento delas | Briefing 1 hora antes da reunião com parceiro |
| 3.5 | Conector Microsoft 365 no Claude (plano Empresarial, habilitado pelo administrador) | Cada pessoa usa o Claude com os próprios arquivos |
| 3.6 | Rótulos de retenção e DLP do Purview no site 2.6 | Bloqueio de compartilhamento externo de arquivo com dado de cliente |

## 5. Aprovações fora da TI (precisam vir antes)
| # | Aprovação | De quem | Trava | Prazo sugerido |
|---|---|---|---|---|
| A1 | Orçamento de nuvem: até US$ 90/mês em produção e US$ 25/mês em homologação, com alertas | Luis (folha do PRM, item 18) | Onda 2 | Antes da reunião com a TI |
| A2 | Banco S0, rede privada, domínio e piloto (itens 19, 20, 22 e 24 da folha do PRM) | Luis | Onda 2 | Idem |
| A3 | Parecer LGPD: guardar CNPJ e contato do decisor no Azure SQL (exceção à regra "dado de cliente fica no Mac", DL-16) e enviar CNPJ de prospect às APIs públicas da consulta | Jurídico | Itens 2.2 a 2.10 com dado real | Antes de chamar a TI para a onda 2 |
| A4 | Termo de Uso e aviso de privacidade do portal | Jurídico | 2.5 e 2.13 (piloto) | Antes do piloto |
| A5 | Aplicativo "PRM leitura" no HubSpot | Dono do CRM | 2.10 | Com a onda 2 |
| A6 | Crédito da API do Claude para as rotinas com IA na nuvem (`AGENTES_IA`) | Administrador da conta Claude da Save | Rotinas com IA fora do Mac | Com a onda 2 |
| A7 | Regras de negócio do PRM: registro, validade e sigilo (DL-01 a DL-03) | Luis | Abrir o PRM ao parceiro | 14/11 |

## 6. Segurança (vale para todos os itens)
- **Credenciais:** ficam no Key Vault (nuvem) ou no cofre do Mac (`.env` com acesso restrito), nunca no código, no GitHub, no e-mail ou no chat.
- **Barreira no commit:** bloqueia token, CNPJ, CPF e telefone.
- **Escopo mínimo:** cada acesso tem o menor escopo possível: uma caixa só, um site só, webhook só de leitura e HubSpot só de leitura.
- **Envios:** todo envio passa pela trava de domínio, só para @savecompany.com.br. Nada vai a cliente ou parceiro sem aprovação humana.
- **Dados em nuvem:** ficam no tenant da Save, em Brazil South. O parceiro vê só o que é dele: o banco filtra por linha.
- **Desligamento:** tudo pode ser desligado na hora, revogando o aplicativo, o cliente OAuth, o webhook ou a atribuição do papel.

## 7. Perguntas à TI
1. Quem é o responsável por Entra ID, Exchange, Azure, GLPI e Bitrix, e qual a data de cada item da onda 1?
2. A Save já tem assinatura Azure e organização no GitHub? Quem faz a transferência do repositório?
3. Há política de região (dados no Brasil) e de convidados B2B que mude o desenho?
4. Qual o canal oficial para entregar certificado e segredo ao Luis?
