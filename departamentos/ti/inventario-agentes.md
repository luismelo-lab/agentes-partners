# Inventário de agentes e registro de governança de IA — Área Partners

**Versão 1.0 · 29/09/2026** · Mantido pelo Departamento de TI virtual (Governança de IA) · Aprovação: Luis Fernando de Melo
Referências: NIST AI RMF 1.0 + perfil de IA generativa (NIST AI 600-1); ISO/IEC 42001:2023 (aplicação proporcional). Método: `~/.claude/skills/depto-ti/references/governanca-ia.md`.
Levantado com `ls ~/.claude/skills ~/.claude/scheduled-tasks ~/Library/LaunchAgents` e leitura dos SKILL.md e scripts, em 29/09/2026 às ~18h. Vários itens estavam sendo construídos no mesmo dia: revisar na próxima atualização.

## Como ler
- **Autonomia:** todos em **N1** (o agente analisa e rascunha; uma pessoa aprova; nada é enviado nem gravado em sistema de terceiros). Nenhum item tem exceção aprovada.
- **Classes de dado:** C0 público · C1 interno · C2 confidencial (clientes, pareceres, honorários, parceiros) · C3 restrito (credenciais, dados bancários, CPF, SPED/folha). Ver `references/seguranca-lgpd.md`.
- **Onde roda:** "Mac" = Claude (Claude Code / app) no Mac do Luis, com arquivos locais em `~/agentes-partners` e `~/.claude`; backup diário no OneDrive da Save.

## Resumo
| Tipo | Quantidade | Observação |
|---|---|---|
| Skills (agentes) | 20 | 19 da área + `depto-ti` (novo); 8 em construção em 29/09 |
| Tarefas agendadas do Claude | 3 | Todas às segundas; dependem do Mac ligado e do app aberto |
| Scripts | 23 | Só leitura em sistemas externos; escrevem fora só o rascunho no Outlook local e o backup no OneDrive da Save |
| Jobs launchd | 2 | 1 ativo (backup), 1 desativado (master-sync) |
| Credenciais | 1 | Token do app privado do HubSpot em `~/agentes-partners/.env` (permissão 600, fora do backup). Não lido neste inventário |

## A. Skills (agentes)
| ID | Agente | Finalidade | Dados que toca | Sistemas / serviços | Dono humano | Riscos principais | Controles | Status |
|---|---|---|---|---|---|---|---|---|
| S01 | `gabinete` | Porta de entrada: decide áreas e profundidade | C1–C2 (o que o Luis traz) | — | Luis | Rota errada; área necessária fora | Ficha de Rota (Portão 0) | Em uso |
| S02 | `conselho-partners` | Conselho consultivo: pareceres e ata | C1–C2 (números, decisões) | Relatório semanal local | Luis | Convergência excessiva; número sem fonte | Pareceres independentes; decisões só "pendente" | Em uso |
| S03 | `arquiteto-agentes` | Mentor do projeto de agentes | C1 | — | Luis | Desatualização do método | — | Em uso |
| S04 | `depto-pessoas` | Rascunhos de gestão de pessoas (PDI, feedback, metas) | **Pessoais** do time (desempenho) | — | Luis (+ RH formal) | Decisão sobre pessoa sem RH; rótulos | Só fatos observáveis; pasta confidencial do Gabinete | Em uso |
| S05 | `depto-tributario` | Pré-análise tributária com fonte oficial | C0 (normas) + C2 (perfil do cliente) | Web (fontes oficiais) | Técnico Tributário (Geovana curadora) | **Alucinação de norma/julgado**; tese desatualizada | Fonte datada obrigatória; validação humana | Em uso |
| S06 | `depto-juridico` | Pré-análise jurídica, prazos com dupla checagem | C2 (notificações, contratos) | Web (fontes oficiais) | Advogado(a) responsável (Daniela curadora) | **Prazo calculado errado**; citação inexistente | Dupla checagem independente; "não localizado" | Em uso |
| S07 | `depto-marketing` | Calendário, textos, kits, jornal | C0–C1 | Web | Marketing da Save | Promessa de resultado; marca não validada | Revisor de marca & compliance | Em uso |
| S08 | `depto-resultados` | Relatório semanal (deck + one-pager) | C2 (honorários, margens, custos) | HubSpot (leitura), Firestore do cockpit | Luis | Número errado para a liderança | Números só por script; rótulo "potencial" | Em uso (agendado) |
| S09 | `depto-dados` | Qualidade do CRM, scorecard de parceiros | C2 | HubSpot (leitura) | Time de CRM / Luis | Scorecard lido como nota de pessoa | Sem ranking de pessoas; só leitura | Em uso |
| S10 | `depto-intel-comercial` | ICP, território, prospects | C0 (Receita aberta) + C2 (HubSpot) | Receita (download oficial), minhareceita.org (só prospects) | Jenifer (curadora) / Luis | CNPJ de prospect enviado a serviço de terceiro; contatos sem validação LGPD | Script bloqueia CNPJ de cliente no serviço externo; sócios não baixados; contatos desligados | Em uso |
| S11 | `recuperador` | Fila e fichas de reanálise de perdidos/zerados | C2 (pareceres, valores) | HubSpot (leitura), **links públicos do Bitrix24**, OCR local, Outlook (rascunho) | **Geovana** | Falso positivo; leitura de links públicos; e-mail enviado sem revisão | D1–D6; pasta 700; só texto guardado; rascunho, nunca envio; D2 mede falso positivo | Em uso (agendado) |
| S12 | `revisor-diagnostico` | 2ª opinião antes da apresentação do diagnóstico (2ª onda da Geovana) | C2 | HubSpot, pareceres | Geovana | Mesmos do S05 | Em construção | Em construção |
| S13 | `celula-daniela` | Triagem, pendências/SLA, retorno ao parceiro, CRM, briefings | C2 + **pessoais** (nomes de contatos) | HubSpot (leitura), Receita | **Daniela** | Resposta ao parceiro com dado errado; telefone no chat | Tudo rascunho; CRM só como proposta; sem telefone no chat | Em construção (v1) |
| S14 | `celula-jenifer` | Listas, cadência, follow-up, novos parceiros | C0 + C2 + **pessoais** (contatos de prospects) | Receita, minhareceita.org, HubSpot (leitura) | **Jenifer** | Abordagem sem base legal; conflito de canal | Nada enviado; dedupe no HubSpot; contatos só após LGPD | Em construção (v1) |
| S15 | `depto-contratos` | Conferência de dados e minutas de contrato/distrato | C2 | HubSpot, Receita | Contratos + Jurídico | Minuta com dado errado | Conferente de dados; Jurídico valida | Em construção |
| S16 | `depto-operacoes-canal` | Conferência de repasses, conflito de canal | C2 (repasses) | HubSpot | Financeiro / Luis | Valor de repasse errado comunicado | Revisor de controle; nada enviado | Em construção |
| S17 | `depto-partner-success` | Onboarding, academia, saúde de parceiros | C1–C2 | HubSpot (via depto-dados) | Luis / Daniela | Promessa ao parceiro | Revisor de promessas | Em construção |
| S18 | `depto-pos-venda` | Avisos, compensações de ofício, guias, extrato | C2 (créditos, pagamentos) | — (sem script) | Pós-venda da Save | Prazo de 15 dias errado; valor errado ao cliente | Dupla checagem; nada transmitido | Em construção |
| S19 | `depto-qualidade` | NPS, auditoria de promessas | C1–C2 + **pessoais** (respostas de pesquisa) | Local | Luis | Pesquisa sem base legal | A definir | Em construção |
| S20 | `depto-ti` | Este departamento: GLPI, integrações, segurança, governança | C1 (metadados); nunca credenciais | Web (documentação oficial) | **TI da Save** (nome a confirmar) | Recomendação técnica errada | Fonte oficial; Revisor Técnico | Novo (29/09) |

## B. Tarefas agendadas (Claude)
| ID | Tarefa | Quando | O que faz | Dados | Dono | Risco | Controle |
|---|---|---|---|---|---|---|---|
| T01 | `relatorio-semanal-resultados` | Seg 06h30 | Baixa o HubSpot, calcula métricas, gera deck e one-pager | C2 | Luis | Falha silenciosa se o Mac estiver desligado; número desatualizado | Rascunho; avisa fonte secundária |
| T02 | `conselho-reuniao-semanal` | Seg 07h30 | Ata do Conselho sobre o relatório | C2 | Luis | Usa dado velho se T01 falhar | Declara a data do dado |
| T03 | `recuperador-lote-semanal` | Seg 08h | Atualiza fila, lê pareceres, fichas do lote, rascunho no Outlook | C2 | Geovana / Luis | Leitura de links públicos; e-mail indo a destinatário errado | Rascunho só para o Luis até confirmar o e-mail da Geovana |

## C. Scripts
| Script | Finalidade | Sistemas externos | Escreve fora da máquina? |
|---|---|---|---|
| `depto-resultados/scripts/hubspot_fonte.py` | Download dos negócios do HubSpot (fonte única dos demais) | HubSpot API v3 (GET e *search*, só leitura; token lido do `.env` e passado por stdin ao curl, fora dos logs) | Não |
| `depto-resultados/scripts/calc_semana.py` | Métricas do relatório | HubSpot; Firestore do cockpit (`save-partner-soe`) **lido sem credencial** | Não |
| `depto-resultados/scripts/gen_deck.js` | Deck PowerPoint | — | Não |
| `depto-dados/scripts/dados_bi.py` | Qualidade do CRM e scorecard | HubSpot (via hubspot_fonte) | Não |
| `depto-intel-comercial/scripts/icp.py` | ICP e território | — (dados locais) | Não |
| `depto-intel-comercial/scripts/receita_cnpj.py` | Base oficial do CNPJ (download mensal ~7,7 GB); regime via minhareceita.org só para prospects | arquivos.receitafederal.gov.br; minhareceita.org | Não (envia CNPJs de prospects como consulta) |
| `recuperador/scripts/fila.py` | Fila priorizada | — | Não |
| `recuperador/scripts/pareceres.py` + `ocr.swift`/`ocr` | Lê pareceres (Word, PDF, Excel, imagem com OCR local do macOS) | **cdn.bitrix24.com.br (links públicos)**; arquivos do HubSpot pendentes do escopo | Não |
| `recuperador/scripts/email_outlook.py` | Rascunho do e-mail do lote | Outlook do Mac (AppleScript) ou arquivo .eml | Cria rascunho (não envia) |
| `celula-daniela/scripts/comum.py`, `briefing_master.py`, `crm_checagem.py`, `pendencias.py` | Briefing de conta, checagem de CRM, controle de pendências/SLA | HubSpot (via arquivo local), Receita local | Não |
| `celula-jenifer/scripts/lista_master.py`, `followup.py` | Listas por Master, follow-up | minhareceita.org (só prospects; bloqueia clientes) | Não |
| `depto-contratos/scripts/controle_contratos.py` | Controle de contratos parados | HubSpot (arquivo local) | Não |
| `depto-operacoes-canal/scripts/_comum.py`, `conferencia_repasses.py`, `conflito_canal.py` | Repasses e conflito de canal | HubSpot (arquivo local) | Não |
| `depto-qualidade/scripts/calc_nps.py`, `auditar_texto.py` | NPS e auditoria de promessas em textos | — | Não |
| `infra/backup.sh` | Backup diário | OneDrive da Save (pasta sincronizada) | Sim: cópia para o OneDrive corporativo (sem `.env` e sem a base da Receita) |

## D. Jobs launchd
| Job | Estado | O que faz | Observação |
|---|---|---|---|
| `com.savecompany.agentes-backup` | Ativo, 19h30 diário | `infra/backup.sh` (30 versões) | Testar uma restauração (nunca testada) |
| `com.savecompany.master-sync` | **Desativado** (movido para `~/Library/LaunchAgents/desativados/`) | Sincronizava o cockpit Master | Falhava (exit 127) porque `~/soe-agent` foi apagado; cockpit parado desde 31/08 |

## E. Outros componentes fora do inventário de skills
- **Cockpit Master / S&OE** (Firebase `save-partner-soe`, página pública `save-partner-soe.web.app`): o script lê o documento do Firestore sem autenticação → **confirmar com o TI se as regras do Firestore liberam leitura pública** (ver chamado 3).
- **save-crm** e **master-dashboard.html** (OneDrive): fora deste levantamento; incluir na próxima revisão.
- **Plugins e conectores instalados no Claude do Luis** que não são usados pela área (ex.: Bright Data, Bigdata.com, DataRobot, S&P Global, pacote para assessores financeiros com Gmail/Drive/Calendar e dezenas de conectores). Risco: uma skill de plugin pode mandar buscas (com nome de cliente) a um serviço de terceiro; uma delas se declara substituta obrigatória das ferramentas de web. **Recomendação: desativar o que não é usado** (decisão do Luis; o TI pode definir a lista permitida no plano Enterprise).

## F. Riscos transversais (registro)
| # | Risco | Prob. | Impacto | Tratamento proposto | Dono |
|---|---|---|---|---|---|
| R1 | Pareceres de clientes acessíveis por link público do Bitrix24 (4.748 links) | Alta (já existe) | Alto (sigilo, LGPD, reputação) | Chamado 1 ao TI | TI |
| R2 | Tudo roda no Mac do Luis: sem Mac/app, as tarefas não rodam; perda do Mac = perda do trabalho do dia | Média | Médio | Backup diário existe; testar restauração; avaliar ambiente corporativo para os agentes | Luis + TI |
| R3 | Alucinação em norma, prazo ou valor | Média | Alto | Fonte obrigatória, dupla checagem de prazos, scripts para números, teste de alucinação antes de uso real | Donos de cada depto |
| R4 | Envio indevido (e-mail/WhatsApp) | Baixa | Alto | Só rascunho; nenhum agente com permissão de envio | Luis |
| R5 | Credencial exposta | Baixa | Alto | `.env` 600, fora do backup e do texto; token só leitura; rotação a definir com o TI | TI |
| R6 | Dados de clientes em serviço de IA fora do contrato (conta pessoal, plugin de terceiro) | Média | Alto | Política abaixo; confirmar que o Claude usado aqui é a conta Enterprise; desativar plugins sem uso | Luis + TI |
| R7 | Dados pessoais de contatos (Jenifer, Daniela, Qualidade) sem base legal validada | Média | Médio | Contatos desligados até validação do Jurídico | Jurídico |
| R8 | Falha silenciosa de automação (como o master-sync) | Média | Médio | Revisão semanal do log das tarefas; alerta de falha a desenhar | Operação & Continuidade |

## G. Incidentes
| Data | Agente | O que aconteceu | Dado afetado | Correção | Regra nova |
|---|---|---|---|---|---|
| 31/08–28/09/2026 | launchd `master-sync` | Falhou por ~4 semanas sem alerta (pasta do soe-agent apagada) | Nenhum vazamento; cockpit desatualizado | Job desativado em 29/09 | Todo job automático precisa de alerta de falha |
| 28/09/2026 | Base de margem do S&OE | 10 repasses com erro ×10.000 | Números internos | Sinalizado pelo depto-resultados | Número só por script com checagem de outlier |

---

# Política de uso de IA — Área Partners (v1, proposta)
*Para aprovação do Luis e validação do Jurídico e do TI da Save. Curta de propósito.*

1. **Para que usamos IA:** analisar, organizar e **rascunhar**. Quem decide, aprova e envia é sempre uma pessoa (N1). Mudar o nível de um agente exige decisão escrita do Luis, para aquela tarefa.
2. **Ferramenta autorizada:** o **Claude no plano Enterprise da Save** (decisão D3: dados não usados para treinar modelos). Não usar conta pessoal, versão gratuita ou outra IA com dados de clientes, parceiros ou do time.
3. **Dados de clientes (C2):** entram só o necessário para a tarefa; preferir ID do negócio a nome; nunca em buscas na web nem em serviços de terceiros sem contrato. Pareceres e valores ficam em pasta local protegida ou em sistema com controle de acesso, nunca em link público.
4. **Fora da fase 1 (D3):** SPED, folha de pagamento, dados bancários, CPF e documentos pessoais não entram em agente.
5. **Credenciais:** nenhum agente lê, mostra ou pede senha ou token. Credenciais ficam com o TI e em arquivo protegido.
6. **LGPD:** dado pessoal (nome, telefone, e-mail de contato) só com finalidade clara e base legal validada pelo Jurídico; telefone não entra no chat; mensagens ativas no WhatsApp só pela API oficial, com opt-in, quando houver.
7. **Fonte e verificação:** afirmação técnica, jurídica ou numérica sem fonte não sai. Números vêm de script. Tributário e Jurídico são sempre pré-análise para validação humana. Nada é prometido ao cliente ou ao parceiro.
8. **Transparência:** o que for preparado com IA é marcado (campo "Preparado com IA?" no GLPI; registro por caso no Recuperador). Se o cliente ou o parceiro perguntar, dizemos que houve apoio de IA com revisão humana (Recomendação CFOAB 001/2024).
9. **Novo agente ou automação:** só entra em uso real depois da ficha de avaliação (finalidade, dados, credencial, teste de alucinação, plano de desligar, dono) e da aprovação do Luis; entra neste inventário.
10. **Incidentes:** erro relevante, dado no lugar errado ou envio indevido é comunicado ao Luis no mesmo dia e registrado na seção G; se envolver dado pessoal, o Jurídico avalia a comunicação à ANPD.

*Revisão: trimestral, ou quando entrar ferramenta, sistema ou tipo de dado novo.*

## Acréscimo 30/09 · Portal Central Partners e chatbot de pedidos
| Item | Finalidade | Dados que toca | Onde roda | Autonomia | Dono humano | Riscos e controles |
|---|---|---|---|---|---|---|
| Portal Central Partners (artifact 7fgGfrK7zVqzjcXCscJmwb) | Painéis por pessoa + aba Pedidos | Resumos agregados (dados.json), pedidos internos | claude.ai (privado; acesso pelo compartilhamento do Luis) | Leitura; pedidos registrados pelo próprio usuário | Luis | Compartilhar só com o time; não é público |
| Assistente de pedidos (capacidade `sample`) | Conversa e monta a ficha do pedido | Texto digitado pelo usuário | Claude da conta de quem usa | Só registra o pedido depois do clique em "Registrar" | Luis | Proíbe dados bancários/CPF/senhas; não fala com parceiros |
| Coleção `pedidos` (capacidade `db`) | Registro compartilhado dos pedidos e status | Título, descrição, responsável, status | claude.ai | Colaboradores escrevem; leitores só leem | Luis | Conteúdo do time é dado, nunca instrução para os agentes |
| Rotina whatsapp-caixa-time (passo 2b) | Inclui pedidos abertos nos e-mails | Leitura da coleção `pedidos` | Mac do Luis | Não altera pedidos | Luis | Depende do Mac ligado |
| (30/09) Chatbot de pedidos do portal | **Desativado** a pedido do Luis; substituído pela Central de Agentes por e-mail (skill central-agentes, D24) | — | — | — | Luis | — |

## Atualização 01/10/2026 (revisão de arquitetura)
- Rotinas do Claude: 5 (relatório semanal, Conselho, Recuperador às 9h, WhatsApp com IA 8h/14h, Central de hora em hora). Jobs do launchd: 6 (`com.savecompany.partners.{manha,segunda,caixa,whatsapp-auto,central}` + `com.savecompany.agentes-backup`); os .plist estão versionados em `infra/launchd/`.
- Exceções aprovadas à N1: D23 (e-mails internos do WhatsApp) e D24 (respostas internas da Central). Alertas de falha por e-mail ao Luis.
- Novos componentes: `lib/partners_dados.py` (fonte única), `lib/registro_demandas.py` (registro único, pasta 700).
- Risco novo R9: anexos do WhatsApp em URLs públicas do armazenamento do Eazybe (Backblaze), baixados sem credencial. Pergunta ao TI/Eazybe: as URLs são assinadas e expiram?
- Conectores: ver a tabela de conectores no README (Control Chrome, Bright Data e Google não usar).
