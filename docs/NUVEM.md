# Rodar os agentes na nuvem (GitHub Actions + Microsoft 365)

**Para quê:** as rotinas param de depender do Mac do Luis ligado. Tudo já está pronto neste repositório. Falta só configurar as contas e ligar.

## O que já está pronto
| Peça | Onde |
|---|---|
| Rotinas da nuvem, **desligadas** | `.github/workflows/`: dados do dia, segunda, leitura do WhatsApp, rodada sem IA, leitura da Central, Receita mensal, rotinas com IA |
| Preparação do ambiente | `.github/actions/preparar/`: monta as pastas iguais às do Mac, instala OCR em português e baixa o estado |
| E-mail e SharePoint pelo Microsoft Graph | `lib/graph.py`: o envio de e-mail, a Central e o OneDrive passam a usá-lo quando `AGENTES_EMAIL=graph` e `AGENTES_ARQUIVOS=sharepoint` |
| Memória entre rodadas | `lib/estado.py`: registro de demandas, Central, triagens e métricas ficam numa pasta restrita do SharePoint, nunca no GitHub |
| OCR fora do Mac | Tesseract (português), com o mesmo resultado esperado do leitor do Mac, um pouco menos preciso em fotos ruins |
| Barreira de LGPD | `.gitignore` só libera código. `infra/checar-dados.py` barra o commit se achar CNPJ, CPF, telefone, token ou chave |
| Trava contra rodar em dobro | Com o arquivo `~/agentes-partners/.nuvem-ligada` no Mac, as rotinas automáticas do Mac param e os comandos manuais continuam |

## Passo a passo
**1. TI · GitHub (1 dia)**
- Criar na **organização da Save** um repositório **privado** `agentes-partners`, com acesso só para o Luis e o TI.
- Ativar o *secret scanning* e a proteção da branch `main`.
- No Mac do Luis: `git remote add origin <url>` e `git push -u origin main`. Antes de cada push, rodar `infra/repo-sincronizar.sh`.

**2. TI · Microsoft 365** (pedido em `departamentos/ti/integracoes-microsoft.md`)
- Caixa compartilhada `agentes.partners@savecompany.com.br`.
- Aplicativo no Entra ID com `Mail.ReadWrite` e `Mail.Send` restritos a essa caixa e `Sites.Selected` só no site da área.
- Site do SharePoint "Área Partners · Agentes", com a pasta restrita "Estado dos agentes".

**3. Configurar o repositório** (Settings → Secrets and variables → Actions)
- **Segredos:** `HUBSPOT_TOKEN`, `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET` e, para as rotinas com IA, `ANTHROPIC_API_KEY` ou `CLAUDE_CODE_OAUTH_TOKEN`.
- **Variáveis:** `AGENTES_CAIXA`, `GRAPH_SITE_ID`, `GRAPH_PASTA` (= `Área Partners · Agentes`).

**4. Testar sem ligar os horários**
- No Mac, com as credenciais no ambiente: `python3 lib/graph.py testar` (login, caixa e site).
- No GitHub (Actions → *Run workflow*): rodar uma vez **Dados do dia** e **WhatsApp · leitura**, com `AGENTES_NUVEM=ligado` só durante o teste. Conferir os arquivos no SharePoint.

**5. Virar a chave**
1. No GitHub: `AGENTES_NUVEM=ligado`.
2. No Mac: `touch ~/agentes-partners/.nuvem-ligada`. As rotinas do launchd passam a ser puladas e registradas em `partners status`.
3. Atualizar `REMETENTES` em `central.py` se a caixa mudar, e trocar no catálogo e nos modelos o endereço para a caixa compartilhada (`central.py modelos`).

**6. Partes com IA**, quando houver crédito ou token de uso automático do Claude:
1. `AGENTES_IA=ligado` no GitHub.
2. No app do Claude, pausar as rotinas equivalentes: WhatsApp com IA, Central, relatório semanal e Recuperador.

## O que continua no Mac por enquanto
- **Portal Central Partners:** só uma sessão do Claude publica o portal. Alternativa: página no SharePoint.
- **Reunião do Conselho:** usa vários agentes em paralelo. Pode ir para a nuvem depois, como `conselho-reuniao-semanal` em `ia-rotinas.yml`.
- **Backup:** fica dispensável com o repositório (código) e o SharePoint (dados).

## Custos
- **GitHub Actions:** as rotinas usam cerca de 900 a 1.200 minutos por mês. O plano gratuito de repositório privado tem 2.000.
- **Claude:** cobrado por uso, só nas rotinas com IA. A Central só chama o Claude quando há fila.
