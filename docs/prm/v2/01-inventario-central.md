# PRM Save v2 · 01 · Inventário da Central e mapa de migração

**Versão:** 1.0 · **Data:** 26/10/2026 · **Autor:** agente de arquitetura (Área Partners), para o Luis · **Status:** insumo para o desenho v2 do PRM
**Pergunta:** o que já foi construído na Central (pasta `central/`, Central de Agentes, caixa de entrada, demandas do WhatsApp, painel Central Partners e rotinas), onde está, quão maduro é, quem usa e para onde vai no PRM.
**Base lida:** `docs/prm/desenho-prm-save-2026-10-26.md`, `docs/prm/prm-save-prototipo.html` (estrutura de telas), `central/` (README, `web/`, `api/central_api/*`, `api/tests/*`, `dev_server.py`, `consulta_demo.py`), `skills/central-agentes/` (SKILL.md, `scripts/central.py`, `references/`), `lib/caixa.py`, `lib/historico.py`, `lib/registro_demandas.py`, `lib/chamados_painel.py`, `lib/painel_sync.py`, `lib/portal_contas.py`, `lib/protecao.py`, `lib/estado.py`, `lib/graph.py`, `lib/glpi.py`, `infra/portal_dados.py`, `infra/gestao.py`, `portal/index.html`, `rotinas/esteira-parceiro.md`, `rotinas/whatsapp-caixa-time.md`, `rotinas/central-agentes-email.md`, `.github/workflows/esteira-parceiro.yml`, `bin/partners`, `docs/sso-entra/`.
**Conferido na hora (26/10/2026):** `cd central/api && PYTHONPATH=../../lib python3 -m unittest` → **154 testes, OK** (o README ainda diz 28; ver lacuna L15). `cd lib && python3 -m unittest test_cnpj test_historico test_portal_fluxo` → **56 testes, OK**. Contagens de uso lidas só em número (sem conteúdo de cliente).

**Legenda de maturidade:** **Testado** (testes automáticos passando) · **Rodando** (rotina agendada ou launchd em uso) · **Demo** (só localhost, sem login ou com dado de exemplo) · **Desligado** (código pronto, interruptor desligado) · **Desenho** (só documento).
**Legenda de destino:** **P** = módulo do parceiro (portal externo) · **S** = módulo da Save (painel interno) · **B** = serviço de back-end compartilhado · **F** = fica fora do PRM.

---

## 1. Resumo

1. A Central tem **três peças separadas que ainda não se falam**: (a) a base SSO em `central/` (Azure SWA + Functions + Entra, só `/api/eu` e `/api/painel`, 28 testes); (b) a consulta de Lucro Real com esteira para o parceiro (regime, 1ª checagem HMAC, dossiê-base de 9 seções, auditor, aprovação, Word), **que só roda no `consulta_demo.py`, em localhost, sem login, com o usuário fixo `demo-local`** (126 testes); (c) o painel Central Partners, que é um **Artifact do claude.ai** com banco do Artifact, alimentado por rotinas no Mac via `ArtifactData`.
2. Quase tudo o que o PRM desenhou como módulo **já existe como motor**, mas no lado errado: as regras de registro, demanda, histórico, chamado, caixa e auditoria estão em scripts do Mac e em rotinas do Claude; nenhuma está exposta como API autenticada.
3. Há **sete duplicidades** entre o PRM desenhado e a Central (seção 4). As três maiores: registro de oportunidade × 1ª checagem × pedido de esteira × conflito de canal (quatro checagens da mesma raiz de CNPJ, com regras diferentes); demandas do parceiro × pedidos da Central de Agentes × demandas do WhatsApp × chamados (quatro filas, três numerações); caixa de entrada × notificações.
4. **Arquitetura-alvo:** confirmo que o PRM deve ser construído **sobre `central/`**, como um só produto com duas faces (parceiro e Save) e um pacote de API único (`central_api`). A evidência está na seção 5. Mas a pilha atual **não aguenta o parceiro como está**: faltam papéis e escopo de parceiro, persistência fora do disco local, tetos fora da memória, rotas autenticadas da esteira, Word sem Node e a troca do `ArtifactData` pela API. São 17 lacunas técnicas (seção 6), das quais 6 bloqueiam o piloto.

---

## 2. Inventário

### 2.A Plataforma `central/` (SSO, API e segurança)

| # | Item | O que faz | Onde | Maturidade | Quem usa hoje | Destino no PRM |
|---|---|---|---|---|---|---|
| A1 | Login Entra (SPA) | MSAL.js 5.24.0 hospedado no site, Authorization Code + PKCE, sessão em `sessionStorage`, telas entrar / sem acesso / erro, logout no Entra | `central/web/index.html`, `app.js`, `vendor/msal-browser-5.24.0.min.js`, `config.example.js` | **Testado local** (login real depende da TI cadastrar redirect e papéis no registro SAVE-SSO-MASTERS) | Luis, em teste local | **B** · login único das duas faces (Save e parceiro B2B) |
| A2 | Validação do token | JWT RS256 por JWKS com cache e rotação, `iss`, `aud`, `tid`, `exp/nbf/iat`, `oid`; escopo `Central.Acesso` para usuário; papel `Agentes.Processar` para rotina (client credentials) | `central/api/central_api/token.py` | **Testado** (`test_api.py`, 28 testes) | Ninguém em produção | **B** · núcleo de autenticação do PRM, sem mudança de lógica |
| A3 | Autorização por papel e dono | 5 papéis internos (`Partners.Gestor/Masters/BDR/Tecnica/Leitura`) + `Agentes.Processar`; 11 ações; regra de dono (`aprovar_chamado`, `marcar_demanda`, `decidir_recorrencia`) | `central/api/central_api/permissoes.py` | **Testado** | Ninguém em produção | **B** · base do RBAC; precisa ganhar papéis e escopo de parceiro (lacuna L2) |
| A4 | Rotas `/api/eu` e `/api/painel` | Identidade e papéis; `dados.json` filtrado por papel (Leitura só agregado; cada analista só a própria chave) | `central/api/central_api/rotas.py`, `function_app.py` (ponte Azure Functions Python v2) | **Testado** | Ninguém | **S** (`/painel`) e **B** (`/eu`) |
| A5 | Servidor local | Serve `web/` e `/api/*` com a mesma lógica e os mesmos cabeçalhos, só em localhost:4280 | `central/dev_server.py` | **Demo** | Luis | **F** · ferramenta de desenvolvimento; continua útil, não é produto |
| A6 | Cabeçalhos de segurança | CSP restrita (`'self'` + login.microsoftonline.com), HSTS, `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy: no-referrer`, fallback de navegação | `central/web/staticwebapp.config.json` | **Pronto** (aplicado também no servidor local) | — | **B** · reaproveitar; acrescentar `routes` com `allowedRoles` por face (L12) |
| A7 | Plano de SSO e roteiro da TI | Diagnóstico, arquitetura (SWA Standard + Functions + Entra), papéis, plano em 6 etapas (1–2 prontas; 3 gravações, 4 agentes pela API, 5 publicação de dados, 6 corte), roteiro de cliques da TI | `docs/sso-entra/diagnostico-e-plano.md`, `orientacoes-ti-2026-10-19.md` | **Desenho** (etapas 1–2 em código) | TI da Save (sem responsável nomeado) | **B** · as etapas 3–6 viram as fases técnicas do PRM |

### 2.B Consulta de Lucro Real e esteira do parceiro (originação)

| # | Item | O que faz | Onde | Maturidade | Quem usa hoje | Destino no PRM |
|---|---|---|---|---|---|---|
| B1 | Consulta de regime | CNPJ (inclusive alfanumérico) → Minha Receita, BrasilAPI de reserva; faixas confirmado / provável / não é Real / sem dado / indisponível, com ano-base e fonte; cache 24 h; lote de 20 (4 em paralelo); teto diário por usuário; interruptor `CENTRAL_API_EXTERNA` | `central/api/central_api/regime.py`; tela `central/web/consulta.html`, `consulta.js`, `consulta.css` | **Testado** (`test_regime.py`, 20) · **Demo** na tela | Luis (teste); nenhum parceiro | **P** · passo 1 do **M2 Registro** ("esta empresa vale a pena?") e ferramenta de qualificação do parceiro |
| B2 | 1ª checagem de negócio ativo | Índice HMAC-SHA256 da raiz do CNPJ com sal secreto; negócio aberto ou ganho em qualquer pipeline e de qualquer idade bloqueia; falha fechada sem índice (não chama API externa); índice com idade máxima de 3 dias; mensagem neutra única para negócio ativo, índice ausente e tetos; motivo real só no log e na trilha; teto de acertos por dia (anti-varredura) | `central/api/central_api/negocio_ativo.py`; construção diária por `bin/partners indice-ativos` | **Testado** (23) · **Rodando** (índice atualizado em 26/10 13h31) | Só a demo | **B** · serviço "checagem de raiz" do **M2** (ver duplicidade U1) |
| B3 | Histórico de consultas do parceiro | Últimas 30 empresas por parceiro; mesma empresa em até 7 dias sai do histórico sem nova chamada nem desconto no teto | `esteira.registrar_consulta`, `consulta_guardada`, `historico` | **Testado** | Só a demo (1 histórico, `demo-local`) | **P** · lista "Minhas consultas" no **M2** e atalho no **M1 Início** |
| B4 | Pedido de análise e esteira | `solicitar` grava o pedido E-NNNN; reaproveita pedido aberto ou entregue há menos de 30 dias da mesma empresa e parceiro; estados recebida → aguardando_aprovacao / revisao_humana / entregue, com rótulo para o parceiro; leitura só do próprio pedido; expurgo por prazo | `central/api/central_api/esteira.py` | **Testado** (`test_esteira.py` 12 + `test_esteira_robusta.py` 60) | Só a demo (5 pedidos, todos `demo-local`) | **P + S** · vira o **registro de oportunidade** com dossiê anexado (U1); fila na tela **Fila de registros** da Save |
| B5 | Dossiê-base de 9 seções | Montado por código, sem IA, a partir do perfil da Receita, playbook do setor, objeções e cases aprovados: Resumo e aderência; Retrato; Setor e dores; Serviços aderentes; Esteira em três ondas; Cases e prova; Como abordar; O que falta e quem fornece; Avisos. Filtra tese por regime e CNAE (alíquota zero vedada por CNAE, só Real, fora da vitrine), barra vazamento (Master, honorário, ticket, nomes) | `central/api/central_api/dossie_base.py` (lê `skills/depto-solucoes/references/playbooks-setoriais.md`, `skills/celula-jenifer/references/especialistas/objecoes-tecnicas.md`, `departamentos/tributario/apresentacao-diagnostico/biblioteca-cases/cases.json`) | **Testado** (11) | Só a demo | **P** (entrega ao parceiro no registro) e **B** (motor de conteúdo compartilhado com o **M7 Biblioteca**, U6) |
| B6 | Aprofundamento pelos agentes | Rotina na nuvem troca o dossiê-base por versão específica, com 8 áreas (Intel, Operações de Canal, Tributário, Soluções, Save Invest, Internacional, Jurídico, Qualidade), checagem de conflito por raiz entre parceiros e aviso interno à Daniela | `rotinas/esteira-parceiro.md`; `.github/workflows/esteira-parceiro.yml`; `python3 -m central_api.esteira fila / enriquecer / publicar` | **Desligado** (liga com `AGENTES_NUVEM` e `AGENTES_IA`; não está nas tarefas agendadas do Mac) | Ninguém | **B** · trabalho assíncrono dos agentes sobre o registro; passa a ler e gravar pela API com `Agentes.Processar` (L7) |
| B7 | Portão de auditoria | Trava por regex (valor perto de recuperação, honorário, comissão, R$) + auditor de promessas da Qualidade sobre todo o texto; com alerta ALTO ou MÉDIO o parceiro fica com a versão-base; até 2 tentativas | `esteira.auditar`, `trava_regex`, `_conferir` | **Testado** | Só a demo | **B** · auditor único de todo texto que sai ao parceiro (U5) |
| B8 | Aprovação da esteira | `CENTRAL_APROVACAO=obrigatoria` (um aprovador) ou `autonoma` (entrega sozinha se a auditoria passar); aprovação hoje por linha de comando (`aprovar --id E-0001 --quem Nome`) ou campo do workflow | `esteira.aprovar`, `_decidir` | **Testado** (sem identidade: o "quem" é texto livre) | Ninguém | **S** · botão Aprovar na **Fila de registros**, com identidade Entra e auditoria (U4) |
| B9 | Word sob demanda | `.docx` no Design System Save gerado quando o parceiro clica em baixar, a partir do dossiê vigente; Node + biblioteca `docx` | `central/api/central_api/dossie.py` → `departamentos/produtos/credito-internacional/scripts/gerar_manual_docx.js`; rota `/api/esteira/arquivo` | **Testado** (lógica) · depende de Node no servidor | Só a demo | **P** · download do dossiê; precisa de outro caminho na Azure (L6) |
| B10 | Trilha de consultas | Quem consultou, o quê, quando, faixa e motivo interno (inclui acertos de negócio ativo), arquivo 600 | `regime.auditar` → `dados-publicos/receita/consultas-regime.jsonl` | **Testado** | Só a demo | **B** · vira a tabela `acesso_log` / trilha de consultas do PRM (L3) |
| B11 | Demo da consulta | Servidor sem login, só localhost:4281, recusa outro Host (DNS rebinding), exige `application/json`, limita corpo, erro neutro | `central/consulta_demo.py` | **Demo** | Luis | **F** · ferramenta de teste; as rotas dela migram para `rotas.py` atrás do token (L1) |

### 2.C Central de Agentes (pedidos do time aos agentes)

| # | Item | O que faz | Onde | Maturidade | Quem usa hoje | Destino no PRM |
|---|---|---|---|---|---|---|
| C1 | Pedidos por e-mail `[AGENTES]` | Lê a caixa (Outlook do Mac; Graph quando ligado), só aceita remetentes do time, grava entrada, responde por e-mail no layout da área, numera P-NNNN | `skills/central-agentes/scripts/central.py` (`ler`, `fila`, `responder`, `confirmar`, `registro`, `modelos`) | **Rodando** (rotina `central-agentes-email`, dias úteis a cada 2 h) | Time (5 pedidos no registro) | **F** para o parceiro · **S** como canal interno; o motor é **B** (U2) |
| C2 | Pedidos pelo painel | Aba Pedidos: pedido livre ou **direto a uma área** (sem triagem); `importar-portal` só aceita conta conhecida (A3); `conferir-decisao` só aceita decisão de quem pediu | `central.py importar-portal`, `conferir-decisao`; `portal/index.html` (rotas `pedidos`, `pedido/<id>`, `novo`, `area/<id>/pedido`) | **Rodando** · **Testado** (`lib/test_portal_fluxo.py`) | Time | **S** · tela "Pedidos aos agentes" do painel interno |
| C3 | Catálogo de pedidos | 29 tipos com código (DM/JB/GT/GE/PI/SC), skill que atende e o que a resposta traz | `skills/central-agentes/references/catalogo.json` | **Pronto** (o painel não usa mais o catálogo; a triagem deduz pelo texto) | Agentes | **B** · tabela única de tipos de demanda (U2, junto com os 23 tipos do `sla.json`) |
| C4 | Ciclo Aprovado / Não aprovado / Nova análise | Quem pediu decide; Nova análise refaz com a nota e versiona (`mudou`); aprendizados registrados | `central.py confirmar`, `decisao_do_painel`; rotina passo 2 | **Rodando** · **Testado** | Time | **B** · mesmo ciclo para a resposta à demanda do parceiro (a Daniela aprova antes de sair) (U4) |
| C5 | Resposta em 3 blocos com revisão do gerente | `resposta.json` com resumo, seções, "também precisa", "falta", `conferido`, `revisao`; trava `infra/validar_saidas.py resposta` | `references/especialistas/redator-resposta.md`, `infra/padrao-entrega.md`, `infra/protocolo-gerente.md` | **Rodando** | Agentes | **B** · formato único das respostas, interno e ao parceiro |
| C6 | SLA da Central | Triagem 1 h útil, status no dia, análise 1 dia útil, lembrete de aprovação 3 d.u., aviso ao Luis 5 d.u. | `skills/central-agentes/SKILL.md` | **Desenho** (proposta, pergunta CA1) | — | **B** · unificar com `sla.json` (U3) |
| C7 | Sentinela de entregas | Refaz etapas mecânicas faltantes e lista o que precisa de IA | `infra/entregas_esperadas.py --reparar` | **Rodando** | Rotina | **F** · operação dos agentes, não do canal |

### 2.D Demandas do WhatsApp, histórico e GLPI

| # | Item | O que faz | Onde | Maturidade | Quem usa hoje | Destino no PRM |
|---|---|---|---|---|---|---|
| D1 | Leitura e triagem do WhatsApp | Lê as caixas (Eazybe → HubSpot), transcreve áudios, OCR, cruza CNPJ com Receita e HubSpot; triagem com IA às 8h e 14h (11h e 17h sem IA); itens responder / acompanhar / encaminhar; dono do pedido de grupo de Master é a Daniela | `rotinas/whatsapp-caixa-time.md`; `skills/celula-daniela/scripts/` (`demandas_whatsapp.py`, `email_whatsapp.py`, `triagem_basica.py`, `whatsapp_hubspot.py`); launchd `caixa`, `whatsapp-auto` | **Rodando** (62 triagens guardadas) | Daniela, Jenifer, Geovana (por e-mail e painel) | **S** · fila de demandas da Save; a demanda entra também pelo portal (**P**, M5) |
| D2 | Registro único de demandas | Uma lista com ID D-AAAA-NNNN, origem (WhatsApp, E-mail-Central, depois GLPI), pessoa, Master, negócio, status, prazo e eventos; P-NNNN vira demanda | `lib/registro_demandas.py` → `registro/demandas.json` | **Rodando** (125 demandas) | Time, painel | **B** · vira a tabela `demanda` do PRM (já prevista no desenho) |
| D3 | Busca no histórico antes do GLPI | BM25 + cobertura sobre 8 fontes (triagens, medição D28, demandas, pares pergunta-resposta do WhatsApp, chamados, Central, base de conhecimento, dado do caso); `avaliar` diz se há resposta suficiente, por qual critério, e o que faltou; índice em cache 700/600 | `lib/historico.py` (7.407 documentos, segundo o desenho); `infra/historico-antes-do-glpi.md` | **Testado** (`lib/test_historico.py`, 15) · **Rodando** na triagem | Agentes da triagem | **B** · serviço "resposta pelo histórico" do **M5**; **fica no Mac** enquanto o índice tiver dado de cliente (L10) |
| D4 | Medição das respostas (D28) | Compara a sugestão com o que a dona do número respondeu (aproveitada, parcial, diferente, sem resposta); critério do degrau 2: 20+ casos em 2 semanas e 95%+ | `lib/medicao_respostas.py` | **Rodando** | Rotina, Luis | **S** · indicador da fila de demandas e porta da resposta automática (M5, fase 4) |
| D5 | Chamado ideal pelo especialista | O gerente da área escreve o chamado (O que o parceiro pede, O que já levantamos, O que falta), no formulário da área | `infra/chamado-ideal.md`, `lib/chamado_modelo.py`, `skills/celula-daniela/scripts/chamados_whatsapp.py` | **Rodando** | Agentes | **B** |
| D6 | Aprovação do chamado no painel → GLPI | Proposta → painel (coleção `chamados`) → a dona aprova (edita título e descrição) ou recusa com motivo → `aplicar` abre no GLPI com o usuário de quem atendeu ou marca "abrir manualmente" | `lib/chamados_painel.py`, `lib/glpi.py` (API v2, OAuth por pessoa) | **Rodando** · **Testado** (13 propostas registradas) | Daniela, Geovana, Jenifer | **S** · ação "Aprovar e abrir no GLPI" da fila de demandas; o PRM **não escreve no GLPI** sem a aprovação (regra R26) |
| D7 | Proteções de texto | Trava de domínio (@savecompany), máscara de CPF, CNPJ, RG, CNH, conta, PIX, senha; auditor de promessas | `lib/protecao.py` | **Rodando** | Todos os envios | **B** · obrigatório em toda gravação vinda do parceiro e em toda resposta (U5) |
| D8 | Checagem de CNPJ do CRM | Duplicidade, conflito, Receita, Simples para a originação no WhatsApp | `skills/celula-daniela/scripts/crm_checagem.py`; `skills/depto-operacoes-canal/scripts/conflito_canal.py` | **Rodando** | Daniela, Jenifer | **B** · fundir com B2 (U1) |

### 2.E Caixa de entrada e notificações

| # | Item | O que faz | Onde | Maturidade | Quem usa hoje | Destino no PRM |
|---|---|---|---|---|---|---|
| E1 | Fila da caixa | Scripts gravam mensagens com id estável em `registro/caixa/pendentes.jsonl`; `lote` prepara documentos para o `ArtifactData batch`; `entregue` marca; idempotente pelo id; separa painel do Luis e do time (D100); texto sem HTML e sem dado sensível; anexo é só o nome e o link da pasta do OneDrive; ação é rota interna | `lib/caixa.py`; rotina `central-agentes-email` passo 1c e `whatsapp-caixa-time` passo 5b | **Rodando** desde 26/10 (11 entregues) · **Testado** (`test_portal_fluxo.py`) | Luis, Daniela, Jenifer, Geovana | **B** · serviço único de notificação (U3) |
| E2 | Marcar como lida | A página grava `caixa_lidas/<conta>`; a rotina confere a conta (A3) e guarda em `lidas.json` | `lib/caixa.py lidas`, `lib/portal_contas.py` | **Rodando** | Time | **B** · vira campo `lida_em` por destinatário no banco |
| E3 | E-mail interno no layout da área | Relatórios e respostas por e-mail, também levados à caixa | `skills/depto-marketing/scripts/email_layout.py` | **Rodando** | Time | **B** · canal secundário da notificação (só @savecompany; parceiro só por portal na v1) |

### 2.F Painel Central Partners (Artifact)

Duas publicações do mesmo `portal/index.html`: **time** (`https://claude.ai/artifact/7fgGfrK7zVqzjcXCscJmwb`) e **Luis** (`https://claude.ai/artifact/2jaMEsooxVMjCGDCQEwYdy`). Dados por `infra/portal_dados.py` (`dados.json` e `diretorio.json`; perfil `time` sem Conselho e sem pastas do Luis). Gravações no banco do Artifact (coleções `pedidos`, `chamados`, `acoes_demandas`, `recuperador`, `conselho`, `apontamentos`, `caixa`, `caixa_lidas`, `acoes`), levadas ao Mac por `lib/painel_sync.py` e pelas rotinas. Identidade pela conta do Claude (`user.me()`, dono do Artifact = Luis), conferida contra `infra/portal-contas.json`. Design "cockpit escuro" v3, Design System Save v0.5. **Maturidade:** **Rodando** e **Testado** (`lib/test_portal_fluxo.py`, 31 testes); lançamento formal ao time pendente (D107, D0 proposto para 03/11).

| # | Tela (rota) | O que faz | Quem usa | Destino no PRM |
|---|---|---|---|---|
| F1 | Caixa de entrada (`caixa`) | Relatórios, alertas e pedidos por pessoa, lidas e não lidas, ações que abrem telas | Time e Luis | **S** · e o mesmo serviço alimenta o "o que mudou" do **M1** do parceiro (U3) |
| F2 | Minha mesa (`mesa`, gavetas `demanda`, `chamado`, `lote`, `decisao`) | O que pede ação da pessoa: demandas (Respondi / Encaminhei / Não é demanda), chamados para aprovar, lote do Recuperador (Aprovar reanálise / Vetar / Precisa de dado), decisões | Time e Luis | **S** · a mesa ganha as filas novas do PRM: registros a decidir, contestações de extrato, demandas do portal |
| F3 | Gestão (`gestao`, `gestao/farol/<id>`, `gestao/decisao/<id>`) | Meta do mês e do Q4 (D111), ritmo, semáforo por bloco, cenários, caixa de 13 semanas, desvios com dono, pré-análise da área em cada farol, dossiê validado em cada decisão | Luis (o time vê só o semáforo) | **S** · o **M8 Visão do canal** entra como bloco desta tela, não como tela solta (U7) |
| F4 | Pedidos (`pedidos`, `pedido/<id>`, `novo`) | Pedido aos agentes, andamento, resposta em 3 blocos, Aprovado / Não aprovado / Nova análise | Time | **S** (C2) |
| F5 | WhatsApp · Demandas (`whatsapp`, `wa/<id>`, `wachamado/<id>`) | Demandas da triagem com resposta pelo histórico ou chamado sugerido; pedir chamado ideal | Daniela, Jenifer, Geovana | **S** · vira **Demandas por SLA** com as demandas de todas as origens (U2) |
| F6 | Áreas (`areas`, `area/<id>`, `area/<id>/conversa`, `area/<id>/pedido`) | 25 áreas com missão, dono, especialistas, entregas e pasta; "Fale com esta área" (chat com IA via `claude.use("sample")`); pedido direto | Time | **S** (diretório) · o **chat fica fora do PRM na Azure** enquanto não houver chave da API do Claude aprovada (L13) |
| F7 | Onde está (`onde`) e busca ⌘K | Busca em áreas, entregas, pastas, rotinas e pedidos | Time | **S** |
| F8 | Rotinas (`rotinas`) | Lista das rotinas, horários e estado | Luis, time | **S** (aba de operação) |
| F9 | Decisões (`decisoes`) | Pauta do Conselho e decisões pendentes do Luis com dossiê | Luis | **F** do PRM · fica no painel do Luis (decisão de gestão, não de canal) |
| F10 | Camada `Fonte` | Isola tudo o que depende do Artifact (`db`, `user`, `sample`); o comentário no código já prevê: "Para migrar ao host com SSO (central/), troque este objeto por chamadas à API, com os mesmos nomes de coleção e campos" | `portal/index.html`, linhas 474–531 | **Pronto para migrar** | — | **B** · ponto de troca Artifact → API (L8) |

### 2.G Rotinas e infraestrutura que sustentam a Central

| # | Item | O que faz | Onde | Maturidade | Destino no PRM |
|---|---|---|---|---|---|
| G1 | `central-agentes-email` | Sincroniza o painel (ArtifactData), sentinela, caixa, chamados aprovados → GLPI, pedidos do painel e do e-mail, recorrência aprovada → formulário do HubSpot | `rotinas/central-agentes-email.md`, `~/.claude/scheduled-tasks/central-agentes-email/` | **Rodando** | **B** · passa a ler e gravar pela API (etapa 4 do SSO) |
| G2 | `whatsapp-caixa-time` | Triagem com IA, chamados, e-mails, republicação dos dois painéis às 8h, caixa, medição D28 | `rotinas/whatsapp-caixa-time.md` | **Rodando** | **B** · idem; a republicação do Artifact some quando o painel for para a Azure |
| G3 | `esteira-parceiro` | Aprofundamento do dossiê a cada 15 min em dias úteis | `rotinas/esteira-parceiro.md`, workflow | **Desligado** | **B** (B6) |
| G4 | Índice de negócios ativos | `partners indice-ativos` após o download diário do HubSpot | `bin/partners`, launchd `manha` | **Rodando** | **B** · publica o índice para a API (blob), sem lista de clientes (L9) |
| G5 | Estado entre execuções | Baixa e sobe do SharePoint (pasta "Estado dos agentes") o registro de demandas, a fila da Central, os pedidos E-NNNN, o índice e o histórico | `lib/estado.py`, `lib/graph.py` (Graph desligado até a TI liberar) | **Testado** · Graph **Desligado** | **F** no alvo · substituído pelo banco do PRM; fica como cópia de segurança |
| G6 | Contas do painel e alertas | Lista de contas Claude válidas por pessoa; descarta gravação de conta desconhecida e alerta o Luis | `lib/portal_contas.py`, `infra/portal-contas.json` | **Rodando** | **F** no alvo · o Entra (oid + papel) substitui |
| G7 | Recorrência aprovada → HubSpot | Envia o formulário público "Novas Oportunidades" só para recorrência aprovada pela Geovana | `lib/oportunidade_form.py` | **Rodando** (com trava de liberação) | **F** do portal do parceiro · fica como rotina interna (o PRM não escreve no CRM) |

---

## 3. Mapa de migração por módulo do PRM

| Módulo do desenho | O que já existe e entra | O que é novo |
|---|---|---|
| **M1 Início do parceiro** (P) | B3 histórico de consultas; E1 notificações (filtradas por parceiro); B4 estado do pedido de dossiê | Usuário do parceiro, resumo de registros e extrato |
| **M2 Registro de oportunidade** (P + S) | B1 consulta de regime; B2 checagem de raiz com mensagem neutra e anti-varredura; B4 pedido e reaproveitamento; B5 dossiê-base; B7 auditor; B8 aprovação; B9 Word; B10 trilha; D8 conflito de canal | Tabela `registro_oportunidade` com validade, prorrogação, expiração, 3 estados de resposta; fila de conflito ao Luis |
| **M3 Meus negócios** (P) | Nada pronto na Central (só o espelho do HubSpot que alimenta o índice) | Mapa 12 etapas → 7 estados; ligação negócio ↔ usuário |
| **M4 Extrato** (P + S) | Nada na Central (motor em `conferencia_repasses.py`, fora do escopo deste inventário) | Tudo |
| **M5 Demandas** (P + S) | D2 registro único; D3 histórico; D4 medição; D5 chamado ideal; D6 aprovação → GLPI; D7 proteções; C4 ciclo de aprovação; C5 resposta em 3 blocos; F5 tela | Entrada pelo portal com tipo e negócio; resposta visível ao parceiro depois da aprovação da Daniela |
| **M6 Nível e jornada** (P) | Nada na Central | Tudo (F8 pendente) |
| **M7 Biblioteca e Academia** (P) | B5 fontes do dossiê (playbook, objeções, cases aprovados) e suas travas de vitrine | Kits por tese, trilha, certificação |
| **M8 Visão do canal** (S) | F3 Gestão (meta, semáforo, desvios); F2 Mesa; E1 alertas | Saúde por parceiro, registros a vencer, adoção do portal |
| **Serviços compartilhados** (B) | A1–A3, A6 (identidade e RBAC); B2 (checagem); B5/B7 (conteúdo e auditor); C3/C6 + `sla.json` (tipos e SLA); D3 (histórico); E1 (notificação); F10 (camada de dados) | Banco (Azure SQL), trilha de acesso, API para os agentes |

**Fica fora do PRM:** F9 Decisões do Conselho (gestão do Luis), C7 sentinela, G5 estado no SharePoint e G6 contas do Artifact (substituídos), G7 recorrência → HubSpot (o PRM não escreve no CRM), F6 chat com IA na Azure (até haver decisão sobre chave e LGPD), A5 e B11 (ferramentas de desenvolvimento).

---

## 4. Duplicidades e unificação proposta

| # | Duplicidade | Onde aparece | Problema | Unificação proposta |
|---|---|---|---|---|
| **U1** | **Registro de oportunidade × 1ª checagem × pedido de esteira × conflito de canal** | M2 (desenho); B2 `negocio_ativo.py`; B4 `esteira.solicitar` (E-NNNN); passo 2.1 da rotina `esteira-parceiro` (grep da raiz nos pedidos); D8 `crm_checagem.py` e `conflito_canal.py`; originação na triagem do WhatsApp | Quatro checagens da mesma raiz com **regras diferentes**: B2 bloqueia qualquer aberto ou ganho de qualquer idade; M2 protege o registro por 90 + 60 dias e o ganho por contrato + 12 meses; a rotina só olha pedidos da esteira; `crm_checagem` olha o HubSpot. Dois identificadores para a mesma intenção (E-NNNN e o futuro registro) | **Uma entidade só: `registro_oportunidade`.** A consulta de regime (B1) vira o passo 1 do formulário; o pedido de dossiê (B4) vira um anexo do registro (o E-NNNN passa a ser o id do registro ou um campo dele). **Um serviço só de checagem de raiz** com três respostas (livre · já registrado por você · mensagem neutra única), alimentado por duas fontes: o índice HMAC do HubSpot (B2) e a própria tabela de registros (conflito entre parceiros). `crm_checagem` e `conflito_canal` continuam como ferramentas internas da Save, mas leem a mesma regra (R1–R3) escrita num único módulo. A regra de "ativo" de B2 tem de ser trocada pela regra aprovada na fase 0 (decisão do Luis). |
| **U2** | **Demandas do parceiro × pedidos da Central de Agentes × demandas do WhatsApp × chamados** | M5; C1/C2 (P-NNNN); D1/D2 (D-AAAA-NNNN); D6 (chamados); tipos em `catalogo.json` (29) e `sla.json` (23) | Quatro filas, três numerações, dois catálogos de tipo. `registro_demandas.py` já junta P-NNNN e WhatsApp, mas o portal criaria uma quinta origem | **Uma tabela `demanda`** (a do desenho) com `origem` (portal-parceiro · WhatsApp · painel-time · e-mail) e `via` (histórico · área · chamado GLPI). Pedido interno do time aos agentes continua existindo, mas é uma demanda com `origem = painel-time` e `solicitante` interno, sem visão do parceiro. **Um catálogo de tipos** (fundir `catalogo.json` e `sla.json`, com a tradução para os 8 tipos que o parceiro vê). Numeração única D-AAAA-NNNN; P-NNNN e E-NNNN ficam como `id_origem`. |
| **U3** | **Caixa de entrada × notificações do PRM × SLA** | E1 `lib/caixa.py`; M1 "últimas respostas"; M8 alertas; SLA da Central (C6) × `sla.json` × prazo da esteira | Mesma necessidade ("avise a pessoa certa do que mudou") com destinatários diferentes; três tabelas de prazo | **Um serviço de notificação** com o formato que `caixa.py` já usa (`para`, `assunto`, `resumo`, `tipo`, `prioridade`, `acoes.go`, `lido`), estendido para `para = usuario_parceiro`. Escreve direto no banco pela API (some o relé `ArtifactData`). **Um SLA** por tipo de demanda, usado pela fila, pela notificação de atraso e pelo M8. |
| **U4** | **Aprovações** | B8 esteira (`--quem` texto livre); D6 chamado; C4 pedido; M2 Aprovar / Recusar / Enviar a conflito; M4 liberar lote | Cinco botões de aprovar, três jeitos de saber quem aprovou (texto, conta Claude, nenhum) | **Uma ação `decidir`** na API, com identidade Entra (`oid`), papel e dono (`permissoes.exigir`), estados padronizados (aprovado · não aprovado · nova análise · recusado com motivo) e trilha `registro_evento`. É exatamente a etapa 3 do plano SSO. |
| **U5** | **Auditores e travas de texto** | B7 `esteira.auditar` + `trava_regex`; D7 `protecao.auditar` e `limpo`; `infra/validar_saidas.py`; `dossie_base.VAZA` | Quatro listas de padrão que podem divergir | **Um módulo `auditoria`** no pacote `central_api` que importa `protecao` e as travas da esteira; toda resposta ao parceiro passa por ele antes de gravar. |
| **U6** | **Dossiê-base × kits da Biblioteca** | B5 (playbook, objeções, cases aprovados, travas de vitrine); M7 kits por tese | As mesmas fontes e as mesmas travas (alíquota zero, T13/T16 fora, produto em validação só como descoberta) em dois lugares | **Um serviço de conteúdo** que lê as fontes uma vez, aplica as travas e serve o dossiê (por empresa) e o kit (por tese). |
| **U7** | **Visão do canal × Gestão × Mesa** | M8; F3 Gestão; F2 Mesa | Três telas internas com semáforo e fila de ação | **M8 entra como bloco "Canal" da Gestão** (saúde, concentração, registros a vencer, conflitos, demandas fora do SLA) e as filas novas entram na **Mesa** de cada pessoa. Nada de tela nova solta. |
| — | Identidade e papéis | A3 (Entra) × G6 (contas do Artifact) × papéis de parceiro do desenho | Três modelos | Entra para todos: papéis internos atuais + `Parceiro.Titular` e `Parceiro.Consultor` (B2B), com o `oid` ligado a `usuario_parceiro`. `portal-contas.json` some no corte. |

---

## 5. Arquitetura-alvo recomendada

### 5.1 Veredito: **confirmo** que o PRM deve ser construído sobre `central/`, como um produto com duas faces

**Evidência a favor (no código):**
1. **A pilha já é a do desenho da Fase 2.** `docs/sso-entra/orientacoes-ti-2026-10-19.md` §7 pede Azure Static Web Apps Standard + Functions Python no tenant Save; o desenho do PRM (Fase 2) pede o mesmo, mais Azure SQL. `function_app.py` já é a ponte Functions Python v2.
2. **A autenticação aceita convidado B2B sem mudança de lógica.** `token.py` valida `tid == CENTRAL_TENANT_ID`; o convidado B2B recebe token emitido pelo tenant da Save (mesmo `tid`), e os papéis vêm do claim `roles`, que pode ser atribuído a convidados. Identidade é o `oid`, nunca o e-mail.
3. **A lógica é separada do transporte.** `rotas.py` recebe cabeçalhos e devolve `(status, corpo)`; `function_app.py` e `dev_server.py` só fazem a ponte. Isso deixa testar tudo sem Azure (154 testes rodam em 12 s, sem rede).
4. **O motor do M2 já foi construído com as travas que o desenho exige:** mensagem neutra única (R25), falha fechada, HMAC com sal (a API nunca vê a carteira), teto diário e alerta de varredura, trilha de consultas, auditor antes de qualquer texto ao parceiro, aprovação obrigatória por padrão.
5. **O painel interno já está preparado para trocar de casa.** A camada `Fonte` em `portal/index.html` isola o Artifact e o comentário manda trocar por chamadas à API "com os mesmos nomes de coleção e campos".
6. **O caminho dos agentes já está previsto.** `token.py` aceita token de aplicativo com o papel `Agentes.Processar`; `permissoes.py` já tem `processar_pendencias` e `gravar_resultado`.

**O que refuto da leitura literal "é só pôr o parceiro na Central":** a pilha está pronta para o login, não para o parceiro. A esteira só existe atrás do `consulta_demo.py`, sem token, com o usuário fixo `demo-local`, guardando tudo em arquivos no disco do Mac e os tetos em memória. As seis lacunas marcadas **[bloqueia piloto]** na seção 6 precisam ser fechadas antes do primeiro convidado.

### 5.2 Desenho recomendado

```
Navegador ── Entra ID (tenant Save) ── Save: membros com Partners.*  ·  Parceiro: convidado B2B com Parceiro.* + MFA
   │
   ▼
Azure Static Web Apps Standard (um site, domínio da Save)
   ├── /save/*      painel interno (portal/index.html com a camada Fonte trocada pela API)
   └── /parceiro/*  portal do parceiro (telas do protótipo: Início, Registrar, Meus negócios, Demandas, Biblioteca)
   │   staticwebapp.config.json: allowedRoles por rota + a CSP atual
   ▼
API central_api (Functions Python, ligada ao SWA) ── token.py → permissoes.py (papel + dono + escopo do parceiro)
   ├── identidade, registro, checagem de raiz, consulta de regime, dossiê, demanda, notificação, decisão, trilha
   ├── Azure SQL serverless (Brazil South): tabelas do desenho + demanda, notificação, consulta, contador de teto
   └── Blob privado: índice HMAC do dia, dossiês, Word gerado
Function App separada (timers): cópia diária do HubSpot (só leitura, token no Key Vault), índice HMAC, expiração de registros
Agentes (GitHub Actions ou Mac) ── client credentials (Agentes.Processar) ── mesmas rotas, sem ArtifactData
Fica no Mac: índice do histórico (lib/historico.py) e tudo com dado de cliente fora do mínimo necessário
```

**Por que um site com duas faces e uma API só:** as regras (raiz do CNPJ, mensagem neutra, auditor, aprovação) precisam ser as mesmas para quem registra e para quem decide; duas APIs duplicariam o que este inventário mostra que já está duplicado. A separação entre parceiro e Save é feita por papel no servidor (o que `permissoes.py` já faz), não por código separado. Se a TI preferir isolar o convidado (Conditional Access próprio), a alternativa é um segundo registro de app só para o portal do parceiro apontando para a mesma API; o custo é um `aud` a mais em `token.Config.publicos`.

---

## 6. Lacunas técnicas

| # | Lacuna | Evidência | O que fazer | Bloqueia piloto? | Quem |
|---|---|---|---|---|---|
| L1 | Rotas da esteira e da consulta não estão na API autenticada | `function_app.py` só expõe `eu` e `painel`; `/api/regime` e `/api/esteira*` só existem em `consulta_demo.py`, com `USUARIO = "demo-local"` | Levar `lote`, `pedir_esteira`, `andamento`, `historico` e `arquivo` para `rotas.py` atrás de `_autenticar`, com o usuário vindo do `oid` | **Sim** | Agentes (código) |
| L2 | Não há papel nem escopo de parceiro | `permissoes.py` só tem 5 papéis internos e o dono é a "pessoa" da Central (luis, daniela, jenifer, geovana) | Papéis `Parceiro.Titular` e `Parceiro.Consultor`; tabela `usuario_parceiro` (oid → parceiro); filtro por linha (consultor vê os próprios, titular vê o escritório); ações novas (`registrar`, `abrir_demanda`, `ver_extrato`, `decidir_registro`) | **Sim** | Agentes; TI cria os papéis no registro do app |
| L3 | Persistência em disco local | `esteira.py` grava JSON em `~/agentes-partners/central-esteira/` com `fcntl.flock`; `regime.auditar` grava em `~/agentes-partners/dados-publicos/`; Functions tem disco efêmero e várias instâncias | Camada de repositório com Azure SQL (pedido/registro, histórico, trilha); manter a interface atual das funções para não reescrever os testes | **Sim** | Agentes; TI provisiona o SQL |
| L4 | Tetos e anti-varredura em memória | `regime._uso` e `_ativos` são dicionários do processo ("contagem em memória na demo"); com duas instâncias ou um reinício, o teto zera | Contador por usuário e dia no SQL, com atualização atômica | **Sim** (é a defesa da carteira, R25) | Agentes |
| L5 | Caminhos fixos do Mac no código | `sys.path.insert(0, "~/agentes-partners/lib")` em `esteira.py` e `negocio_ativo.py`; `dossie_base.py` lê `skills/` e `departamentos/` pela raiz do repositório | Empacotar `lib/cnpj.py`, `lib/protecao.py` e as fontes do dossiê dentro do pacote publicado (ou no Blob), com caminho por variável | **Sim** | Agentes |
| L6 | Word depende de Node | `dossie.py` chama `gerar_manual_docx.js` com `NODE_PATH`; a Function é Python | Opção A: Function Node só para o Word (mesmo gerador, fonte embutida). Opção B: gerar o Word de forma assíncrona pelos agentes e guardar no Blob. Recomendo A | **Sim**, se o Word estiver no piloto; senão adiar | Agentes |
| L7 | Agentes ainda falam com o Artifact e o SharePoint | Rotinas usam `ArtifactData` e `lib/estado.py`; etapa 4 do SSO "a fazer"; Graph desligado | Rotas de agente (`processar_pendencias`, `gravar_resultado`) e segredo do app no Key Vault / GitHub Secrets | Não para o piloto do parceiro (a Fase 1 pode seguir no Artifact); sim para o corte | Agentes; TI emite a credencial |
| L8 | Painel interno ainda é Artifact | Gravações no `db` do Artifact, identidade pela conta do Claude; etapas 3, 5 e 6 do SSO "a fazer" | Trocar a camada `Fonte` pela API e publicar `dados.json` no Blob pela rotina | Não (as faces podem migrar em momentos diferentes) | Agentes |
| L9 | Índice HMAC é montado e guardado no Mac | `bin/partners indice-ativos`; arquivo em `central-esteira/`; `sal.key` local quando não há `CENTRAL_SAL` | Rotina publica o índice no Blob privado; `CENTRAL_SAL` só no Key Vault; idade máxima de 3 dias continua (falha fechada) | **Sim** para a checagem funcionar na Azure | Agentes; TI (Key Vault) |
| L10 | Histórico com dado de cliente só no Mac | `lib/historico.py` guarda o índice em `registro/historico-indice/` (700/600) | Manter no Mac: a sugestão de resposta é feita pelos agentes e gravada na demanda pela API; o portal nunca consulta o índice | Não | — |
| L11 | Consulta externa manda o CNPJ para terceiros | `regime.FONTES` (Minha Receita, BrasilAPI) por `curl` em subprocesso | Parecer do Jurídico e da TI (já pendente no README); na Azure, trocar `curl` por `urllib` com certificados do sistema; manter o interruptor | Depende do parecer | Jurídico; TI |
| L12 | SWA sem regra por papel | `staticwebapp.config.json` só tem cabeçalhos e fallback | `routes` com `allowedRoles` para `/save/*` e `/parceiro/*` (defesa extra; a API continua decidindo) | Não | Agentes |
| L13 | Chat "Fale com esta área" depende do Artifact | `claude.use("sample")` em `portal/index.html` | Fica no Artifact até haver decisão sobre a API do Claude na Azure (chave no Key Vault, custo, LGPD); não entra no portal do parceiro | Não | Luis decide |
| L14 | Regra de "ativo" diverge da regra de registro | B2 bloqueia aberto ou ganho de qualquer idade; M2 propõe proteção por validade e ganho + 12 meses | Escrever a regra R1–R3 uma vez, num módulo, depois da decisão da fase 0 | **Sim** (o portal não pode abrir com duas regras) | Luis decide; agentes codificam |
| L15 | Documentação desatualizada | `central/README.md` diz "28 testes" (hoje são 154) e "etapa 3 a fazer" sem citar a esteira | Atualizar o README ao começar a Fase 2 | Não | Agentes |
| L16 | Sem trilha de acesso por tela | Só existe a trilha de consultas (B10) e os logs 401/403 de `rotas.py` | Tabela `acesso_log` do desenho, gravada pela API em toda leitura de dado do parceiro | **Sim** para LGPD do piloto | Agentes |
| L17 | Timers não cabem nas Functions gerenciadas do SWA | As Functions ligadas ao SWA são só HTTP; o desenho já prevê "Function App própria" para a leitura do HubSpot | Function App separada para os timers (HubSpot, índice, expiração de registro, lembretes de SLA) | Não para o 1º dia; sim para a expiração automática | TI provisiona |

**Dependências fora do código (já registradas no desenho, confirmadas aqui):** a TI cadastrar o redirect de produção, os papéis e o Static Web App (sem responsável nomeado desde 30/09); o parecer LGPD para guardar CNPJ e contato no SQL; a regra R1–R3 (L14).

---

## 7. Entrega em 3 blocos

**1. O que você pediu**
Inventário de 53 itens construídos na Central (plataforma SSO, consulta e esteira, Central de Agentes, demandas e GLPI, caixa, painel e suas 10 telas, rotinas), com o que faz, onde está, maturidade, quem usa e destino no PRM; mapa por módulo; 7 duplicidades com a unificação proposta; veredito sobre a arquitetura (confirmado, com ressalvas) e 17 lacunas técnicas.

**2. O que você também precisa**
- O que está mais maduro para o parceiro é justamente o que ninguém de fora usou: os 5 pedidos da esteira e o único histórico são do usuário `demo-local`. O piloto vai ser o primeiro uso real; vale tratá-lo como teste do motor, não só da tela.
- A unificação U1 depende da regra de registro (fase 0). Enquanto ela não sai, o portal teria duas regras de "cliente protegido" convivendo: a do índice (qualquer ganho, de qualquer idade) e a do registro (validade). É a decisão que mais trava o código.
- A Fase 1 do desenho (PRM interno no painel, sem TI) não é afetada por este inventário: pode seguir no Artifact e reaproveitar `registro_demandas`, `caixa` e a Mesa. As lacunas L1–L6, L9, L14 e L16 só pesam na Fase 2.

**3. O que falta e quem fornece**
| Falta | Quem |
|---|---|
| Regra R1–R3 e validade do registro (fecha L14 e U1) | Luis, com o Jurídico |
| Registro do app com papéis de parceiro, convites B2B, SWA Standard, Function App, Azure SQL, Key Vault | TI da Save (responsável a nomear) |
| Parecer sobre a consulta externa de CNPJ (L11) e sobre a guarda no SQL | Jurídico e TI |
| Decisão sobre o chat com IA fora do Artifact (L13) | Luis |
| Código das lacunas L1–L6, L9, L12, L15, L16 | Agentes (`depto-ti` com o arquiteto) |
