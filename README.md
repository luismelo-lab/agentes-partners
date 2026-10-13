# Agentes da Área Partners · mapa geral

Estrutura de agentes da Área Partners da Save Company (gestor: Luis Fernando de Melo). Este arquivo diz **onde está cada coisa**. Como operar no dia a dia: [RUNBOOK.md](RUNBOOK.md). Estado e pendências: [ESTADO.md](ESTADO.md). Nuvem (GitHub + Microsoft 365): [docs/NUVEM.md](docs/NUVEM.md). Organograma: [ARQUITETURA.md](ARQUITETURA.md) e [DEPARTAMENTOS.md](DEPARTAMENTOS.md).

## Como a estrutura funciona
- **Terminal (sem tokens):** o comando `bin/partners` faz o trabalho mecânico: baixar o HubSpot, ler o WhatsApp e os anexos, ler os e-mails de pedido, rodar as sentinelas, mandar o plano do dia e os avisos, publicar no OneDrive e fazer backup. O macOS (launchd) chama esse comando nos horários (7 jobs em `infra/launchd/`).
- **Operação contínua (D26):** `lib/operacao.py` roda sentinelas sem IA sobre o HubSpot, o WhatsApp, a Central, os chamados e as rotinas. Cada evento vai para o dono do negócio (Jenifer ou Daniela; pipeline BDR com a Jenifer; parceiro fora do roster com o Luis). Resultado: plano do dia às 7h30 e aviso da tarde às 13h30.
- **Claude (com tokens):** entra só para interpretar e escrever (triagem do WhatsApp, respostas da Central, texto do relatório, fichas do Recuperador, Conselho). Sempre lê o que o terminal já preparou.
- **Governança:** tudo é pré-análise (N1). Exceções aprovadas pelo Luis, todas só com e-mail interno: caixa do WhatsApp (D23), respostas da Central (D24), plano do dia e avisos (D26) e lote do Recuperador (D27). Chamado no GLPI só depois de aprovado no painel (D25). Nenhum agente fala com parceiro ou cliente nem altera o HubSpot.
- **Proteções (02/10, Qualidade + Jurídico):** `lib/protecao.py` trava todo envio em @savecompany.com.br, mascara telefone, CPF, CNPJ sem pontuação e RG/conta/PIX/senha rotulados, e passa os textos pelo auditor de promessas (um erro conta como reprovado).

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
| `lib/` | Fonte única: `partners_dados.py` (download do dia, CNPJ, Receita, café, data efetiva, parceiro ativo), `registro_demandas.py` (registro único de demandas D-AAAA-NNNN), `operacao.py` (sentinelas, plano do dia e avisos), `caminhos.py` (pasta ativa do OneDrive), `protecao.py` (trava de domínio, mascaramento, auditor), `glpi.py` e `chamados_painel.py` (chamados, em rascunho), `bitrix.py` (só consulta, desligado) e `graph.py` (Microsoft, desligado) |
| `registro/` | `demandas.json` (registro único: WhatsApp + Central; GLPI quando chegar; visão por pessoa em `Demandas.xlsx` no OneDrive), `eventos.json` (eventos das sentinelas) e `chamados-propostos.json` |
| `infra/` | Backup, publicação no OneDrive, dados do portal, regras do GLPI (`glpi-regras.md` v2), jobs do launchd (`infra/launchd/`) |
| `logs/` | Log de cada execução (`partners.log` resume ok/erro) |
| `celulas/<pessoa>/` | Trabalho de cada célula: WhatsApp (caixas, demandas, anexos), briefings, listas, fila do Recuperador, Revisor, Semana 0 |
| `central-agentes/` | Registro dos pedidos por e-mail, fila de entrada, entregas por pedido, aprendizados |
| `departamentos/<área>/` | Entregas e aprendizados de cada departamento |
| `conselho/` | Atas, consultas e o registro de decisões (`decisoes.md`, D1–D27) |
| `gabinete/` | Pedidos roteados e registro |
| `dados-publicos/receita/` | Base oficial do CNPJ (SQLite, recriável com `partners receita`) |
| `portal/` | Portal Central Partners (artifact) e seus dados |
| `integracoes/` | Análises de integração (WhatsApp/Eazybe, OpenWA) |
| `docs/` | Pedidos à TI: `GLPI.md` (cliente OAuth), `BITRIX.md` (webhook), `NUVEM.md` |
| `.env` | Credencial do HubSpot (nunca é lida pelos agentes nem vai para o backup) |

## Onde o time vê o trabalho
- **E-mail:** plano do dia (7h30, com planilha anexa) e aviso da tarde (13h30), caixa do WhatsApp (8h e 14h com IA; 11h e 17h sem IA), respostas da Central, lote do Recuperador (segunda 9h). Os automáticos têm o assunto "[Partners · automático] ..." e a Central os ignora.
- **OneDrive:** `Área Partners · Agentes/` com uma pasta por pessoa (planilhas de trabalho sincronizadas nos dois sentidos). A pasta local ativa é achada por `lib/caminhos.py` (desde 10/10: "OneDrive-SAVECOMPANY"; os atalhos "OneDrive - SAVE COMPANY" não são confiáveis e só valem se apontarem para a pasta que sincroniza).
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
- **Backup:** diário às 19h30 (`com.savecompany.partners.backup` → `partners backup`, com log e alerta) no OneDrive (`Backups/agentes-partners/agentes-partners-<data>.tar.gz`, um arquivo por dia, 14 dias). Guarda skills, rotinas e esta pasta, exceto `.env`, worktrees do Claude, a base da Receita e o Whisper. Antes de 10/10 eram ~7 mil arquivos soltos por dia (48 mil no OneDrive).
- **Dados pessoais:** RG, CPF, CNH, CTPS, IRPF, passaporte, comprovante de endereço e extrato bancário não são lidos nem copiados. CPF, RG e dados bancários nunca vão para o painel: quem atende completa direto no GLPI. As pastas com conteúdo de clientes ficam com permissão 700.
