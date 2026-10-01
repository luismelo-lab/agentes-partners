# Agentes da Área Partners · mapa geral

Estrutura de agentes da Área Partners da Save Company (gestor: Luis Fernando de Melo). Este arquivo diz **onde está cada coisa**. Como operar no dia a dia: [RUNBOOK.md](RUNBOOK.md). Estado e pendências: [ESTADO.md](ESTADO.md). Nuvem (GitHub + Microsoft 365): [docs/NUVEM.md](docs/NUVEM.md). Organograma: [ARQUITETURA.md](ARQUITETURA.md) e [DEPARTAMENTOS.md](DEPARTAMENTOS.md).

## Como a estrutura funciona
- **Terminal (sem tokens):** o comando `bin/partners` faz o trabalho mecânico: baixar o HubSpot, ler o WhatsApp e os anexos, ler os e-mails de pedido, calcular, publicar no OneDrive e fazer backup. O macOS (launchd) chama esse comando nos horários.
- **Claude (com tokens):** entra só para interpretar e escrever (triagem do WhatsApp, respostas da Central, texto do relatório, fichas do Recuperador, Conselho). Sempre lê o que o terminal já preparou.
- **Governança:** tudo é pré-análise (N1). As exceções aprovadas pelo Luis são o envio de e-mails internos da caixa do WhatsApp (D23) e da Central de Agentes (D24). Nenhum agente fala com parceiro ou cliente nem altera o HubSpot.

## Skills (em `~/.claude/skills/`)
| Skill | Papel |
|---|---|
| `gabinete` | Porta de entrada do Luis: decide quais áreas entram (níveis 1–4) |
| `conselho-partners` | Conselho Consultivo: reunião semanal e consultas |
| `central-agentes` | Pedidos do time por e-mail [AGENTES]; aprovação por Aprovado / Não aprovado / Nova análise |
| `celula-daniela` | Central Masters: triagem, retorno ao parceiro, CRM, reuniões, conta Master, **caixa e demandas do WhatsApp** |
| `celula-jenifer` | Central BDR: listas de prospects, qualificação, cadência, follow-up, indicadores |
| `recuperador` | Central Técnica (Geovana): perdidos zerados e abertos > 90 dias, pareceres, fila e fichas |
| `revisor-diagnostico` | Central Técnica: teses não levantadas nos diagnósticos |
| `depto-tributario` · `depto-juridico` | Núcleo técnico (pré-análise com fonte oficial) |
| `depto-marketing` | Marketing de canal; guarda o **layout único dos e-mails** (`scripts/email_layout.py`) |
| `depto-resultados` | Relatório semanal (métricas por script, deck e one-pager) |
| `depto-dados` · `depto-intel-comercial` | Qualidade do CRM, saúde dos parceiros, ICP, base da Receita |
| `depto-partner-success` · `depto-operacoes-canal` | Onboarding, Academia, níveis · repasses e conflito de canal |
| `depto-contratos` · `depto-pos-venda` · `depto-qualidade` | Contratos, pós-venda, NPS, reclamações e auditoria de promessas |
| `depto-ti` | GLPI pronto para agente, inventário de agentes, segurança e LGPD técnica |
| `depto-pessoas` · `arquiteto-agentes` | Pessoas e o mentor do projeto |

## Pastas (em `~/agentes-partners/`)
| Pasta | O que tem |
|---|---|
| `bin/partners` | Comando único do terminal |
| `lib/` | Fonte única: `partners_dados.py` (download do dia, CNPJ, Receita, café, data efetiva, parceiro ativo) e `registro_demandas.py` (registro único de demandas D-AAAA-NNNN) |
| `registro/demandas.json` | Registro único de demandas (WhatsApp + Central; GLPI quando chegar). Visão por pessoa: `Demandas.xlsx` no OneDrive |
| `infra/` | Backup, publicação no OneDrive, dados do portal, jobs do launchd (`infra/launchd/`) |
| `logs/` | Log de cada execução (`partners.log` resume ok/erro) |
| `celulas/<pessoa>/` | Trabalho de cada célula: WhatsApp (caixas, demandas, anexos), briefings, listas, fila do Recuperador, Revisor, Semana 0 |
| `central-agentes/` | Registro dos pedidos por e-mail, fila de entrada, entregas por pedido, aprendizados |
| `departamentos/<área>/` | Entregas e aprendizados de cada departamento |
| `conselho/` | Atas, consultas e o registro de decisões (`decisoes.md`, D1–D24) |
| `gabinete/` | Pedidos roteados e registro |
| `dados-publicos/receita/` | Base oficial do CNPJ (SQLite, recriável com `partners receita`) |
| `portal/` | Portal Central Partners (artifact) e seus dados |
| `integracoes/` | Análises de integração (WhatsApp/Eazybe, OpenWA) |
| `.env` | Credencial do HubSpot (nunca é lida pelos agentes nem vai para o backup) |

## Onde o time vê o trabalho
- **E-mail:** caixa do WhatsApp (8h e 14h com IA; 11h e 17h sem IA), respostas da Central, lote do Recuperador.
- **OneDrive:** `Área Partners · Agentes/` com uma pasta por pessoa (planilhas de trabalho sincronizadas nos dois sentidos).
- **Portal:** https://claude.ai/artifact/7fgGfrK7zVqzjcXCscJmwb

## Conectores (revisão do TI, 01/10/2026)
| Conector | Uso |
|---|---|
| Gamma | Só materiais de Marketing sem dados de clientes ou honorários (o deck semanal continua no `gen_deck.js`) |
| Excalidraw | Diagramas de fluxo e arquitetura, sem nomes de clientes |
| hubspot-api (skill) · data (skills) | Referência de API e análises pontuais locais |
| Contentsquare | Não usar por enquanto (nenhum fluxo da área depende de analytics do site) |
| Control Chrome · Bright Data · Google (Gmail, Agenda, Drive) | **Não usar**: risco de executar texto de terceiros no Chrome logado, envio de dados a terceiros e mistura de contas fora do Microsoft 365 da Save |
| Microsoft 365 | Aguardando o TI (ver `departamentos/ti/integracoes-microsoft.md`); não autorizar com consentimento pessoal antes |

## Versionamento
Esta pasta é um repositório git **só de código** (o `.gitignore` bloqueia dados). Antes de cada commit: `infra/repo-sincronizar.sh` (copia skills e rotinas). O commit é barrado se `infra/checar-dados.py` achar CNPJ, CPF, telefone, token ou chave.

## Segurança e backup
- **Backup:** diário às 19h30 no OneDrive (`Backups/agentes-partners/<data>`, 30 dias). Guarda skills, rotinas e esta pasta, exceto `.env` e a base da Receita.
- **Dados pessoais:** CNH, RG, CPF e dados bancários não são lidos nem copiados. As pastas com conteúdo de clientes ficam com permissão 700.
