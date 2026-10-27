# Requisitos da VPS dos agentes · Área Partners

> 27/10/2026 · rascunho para o Luis e para a TI, nada contratado. Complementa o pedido único à TI (`docs/pedidos-ti-2026-10-27.md`). A VPS é o item "servidor para o motor dos agentes" da onda 3, e pode ser antecipado.

## 1. Para que serve
Tirar do Mac do Luis o que hoje depende dele ligado e acordado:
- **as 7 rotinas do terminal** (`bin/partners`, hoje no launchd do Mac): manhã às 7h30, tarde, segunda, caixa, Central a cada 15 minutos, WhatsApp sem IA e backup;
- **as 8 rotinas com IA** (hoje agendadas no app do Claude): Central de Agentes, Conselho, consolidação semanal, operação das áreas, radar de mercado, lote do Recuperador, relatório de resultados e caixa do WhatsApp;
- **a base mensal da Receita** (cerca de 7,7 GB baixados por mês, filtrados num banco local);
- **o PRM e o painel em homologação**, enquanto a Azure da onda 2 não existe.

O portal dos parceiros em produção continua no desenho da onda 2 (Static Web Apps, Functions e SQL). A VPS não recebe acesso de parceiro.

## 2. Máquina
| Item | Mínimo | Recomendado | Por quê |
|---|---|---|---|
| vCPU | 2 | 2 a 4 | As rotinas são leves. O pico é a carga mensal da Receita, a transcrição de áudio (Whisper) e a geração de PDF |
| Memória | 4 GB | **8 GB** | Whisper e Chromium (PDF e prévias) juntos com as rotinas |
| Disco | 64 GB SSD | **128 GB SSD** | Download mensal da Receita (7,7 GB) mais descompactação; dados atuais de cerca de 1 GB (`departamentos/`, `dados-publicos/`, `registro/`) e 30 versões de backup |
| Sistema | Ubuntu Server 24.04 LTS | Idem | Suporte até 2029 e pacotes de todas as dependências |
| Região | **Brasil** (São Paulo) | Idem | Dado de cliente e de parceiro (LGPD), igual à regra da onda 2 |
| Rede | IP fixo de saída | Idem | Liberar a VPS no GLPI e no Bitrix, se a TI restringir por IP |

**Custo de referência (Azure, Brazil South, Linux, preço de lista da API de preços em 27/10/2026, sem impostos):**
- Standard_B2as_v2 (2 vCPU e 8 GB): cerca de US$ 88 a 95/mês;
- disco Standard SSD E10 (128 GB): cerca de US$ 18/mês;
- **total: cerca de US$ 110/mês**, ou US$ 1.300/ano.

A reserva de 1 ou 3 anos reduz o preço; a TI cota. Um provedor nacional pode sair mais barato, desde que cumpra a seção 6.

**Recomendação:** VM na Azure, no tenant da Save. Assim ficam um contrato só, o mesmo Entra, o Key Vault e a mesma região do PRM, e a VPS pode ser desligada quando a onda 2 absorver as rotinas.

## 3. Software
| Pacote | Versão | Uso |
|---|---|---|
| Python | 3.12 | Todos os scripts; bibliotecas `openpyxl`, `python-docx`, `numpy`, `PyJWT[crypto]`, `azure-functions`, `playwright` |
| Node.js | 20 LTS | Word no padrão Save (`docx`), PowerPoint (`pptxgenjs`) e Claude Code |
| Claude Code (CLI) | atual | Rotinas com IA (`claude -p`), com a chave da API da conta da Save |
| Chromium (via Playwright) | atual | PDF, prévias e relatórios |
| Tesseract com idioma `por` | 5.x | OCR dos pareceres; substitui o Vision do macOS |
| ffmpeg e Whisper | atual | Transcrição de áudio do WhatsApp |
| zsh, git, curl, sqlite3, util-linux (`flock`) | do sistema | `bin/partners` é zsh; `flock` substitui o `lockf` do Mac |
| Fontes IBM Plex Sans e Mono | — | Padrão visual Save nos documentos |

O repositório já tem as variáveis do modo nuvem: `AGENTES_EMAIL=graph`, `AGENTES_ARQUIVOS=sharepoint`, `OD_RAIZ` e `TZ=America/Sao_Paulo` (`.github/workflows/_ambiente.txt`).

## 4. O que precisa estar pronto antes (dependências)
| # | Dependência | Por quê | Onde está |
|---|---|---|---|
| 1 | **Microsoft Graph** (caixa compartilhada e aplicativo, itens 1.1 e 1.2) | Sem o Mac não há Outlook nem OneDrive sincronizado; e-mail e arquivos passam a ir pelo Graph | Pedido à TI, onda 1 |
| 2 | **Site do SharePoint** "Área Partners · Agentes" (item 2.6) | Pastas do time e estado das rotinas fora do OneDrive pessoal | Pedido à TI, onda 2 |
| 3 | **Chave da API do Claude** com crédito | Rotinas com IA fora do app do Mac | Aprovação A6 |
| 4 | Token do HubSpot só leitura, segredos do GLPI e do Bitrix e o `CENTRAL_SAL` | Mesmas integrações de hoje | Key Vault ou cofre da VPS |
| 5 | **Parecer LGPD** | Dado de cliente sai do Mac (exceção à regra da casa, mesma da DL-16) | Aprovação A3 |

**Ajustes de código (Dados e TI, cerca de 2 dias):**
- trocar os 7 jobs do launchd por timers do systemd;
- usar `flock` no lugar do `lockf`;
- usar Tesseract no lugar do Vision do macOS;
- desligar o caminho do Outlook e do OneDrive local, fixando `AGENTES_EMAIL=graph`;
- passar as 8 rotinas com IA para `claude -p`, como o `ia-rotinas.yml` já faz;
- validar com o teste de fumaça (`partners teste`) e uma semana em paralelo com o Mac.

## 5. Segurança
- **Acesso administrativo:** só por SSH com chave, sem senha e sem root direto; ou pelo Azure Bastion ou pelo login Entra da VM. Só Luis e TI.
- **Firewall:** nenhuma porta aberta para a internet. As rotinas só fazem saída (HubSpot, Graph, GLPI, Bitrix, Receita e Anthropic). A homologação do PRM é vista por túnel SSH ou VPN da Save.
- **Segredos:** no Key Vault, lidos pela identidade gerenciada da VM. Na falta dele, num arquivo `.env` com permissão 600, fora do git e do backup em texto. Nunca no código.
- **Disco e atualizações:** disco cifrado e atualizações automáticas de segurança (`unattended-upgrades`).
- **Proteção contra invasão:** `fail2ban`, se houver SSH exposto.
- **Regras que continuam valendo:** a barreira de dados no commit (`infra/checar-dados.py`), a trava de domínio nos envios (só @savecompany.com.br) e a aprovação humana antes de qualquer envio externo.
- **Monitoramento:** a sentinela `rotina_falhou` já existente avisa por e-mail; uma checagem externa de vida (heartbeat) alerta se a VPS parar.

## 6. Requisitos do provedor (se não for a Azure)
- data center no Brasil e contrato em nome da Save, com cláusula de tratamento de dados (LGPD, art. 39);
- snapshot ou backup diário com retenção mínima de 30 dias;
- disponibilidade de 99,9% ou mais e suporte em português;
- IP fixo e console de emergência;
- exclusão comprovada dos dados ao fim do contrato.

## 7. Backup e continuidade
- **Snapshot:** diário da VM, guardado por 30 dias.
- **Backup próprio:** o `infra/backup.sh` continua, com 30 versões e sem o `.env` e sem a base da Receita, gravando no SharePoint.
- **Reconstrução:** a VPS precisa poder ser recriada do zero em menos de 1 dia, pelo repositório mais o backup. O roteiro fica no `RUNBOOK.md`.
- **Plano B:** se a VPS cair, o Mac do Luis continua apto a rodar tudo durante a transição.

## 8. Decisões do Luis
1. Azure (recomendado) ou provedor nacional.
2. Antecipar a VPS antes da onda 2 ou esperar o Azure do PRM.
3. Orçamento de cerca de US$ 110/mês (US$ 1.300/ano), somado ao da onda 2.
