# PRM Save v2 · 07 · Entrega do desenvolvimento (Fase 1 local, pronta para a Fase 2)

**Versão:** 1.0 · **Data:** 26/10/2026 · **Autor:** desenvolvedor do PRM (agente), para o gerente do PRM e o Luis · **Status:** funcionando em modo local; nada criado na nuvem; HubSpot e GLPI não tocados; sem commit (o gerente faz).
**Base:** `01-inventario-central.md` (U1–U7, L1–L17), `02-regras-de-negocio.md` (máquinas de estado, PRM-R01…R112, parâmetros, textos), `03-dados.md` + `schema.sql`, `04-ti-arquitetura.md`, `05-design.md` + `prm-componentes.css`, protótipo `docs/prm/prm-save-prototipo.html`, código de `central/`.

---

## 1. O que funciona

| Parte | Onde | O que faz |
|---|---|---|
| Back-end | `central/api/central_api/prm/` (17 módulos) | Registro de oportunidade com checagem única pela raiz, resposta neutra idêntica e piso de tempo; 9 máquinas de estado (registro, lead BDR, demanda, linha de extrato, contestação, usuário, apuração de nível, conflito); Meus negócios em 7 estados; extrato com ledger de movimentos, cálculo pelo incontroverso, lote com checklist e segregação; contestação; demandas com histórico antes do chamado e chamado só em rascunho; ação única `decidir` com trilha; notificações no formato da `lib/caixa.py`; nível em sombra; visão do canal; rotina diária |
| Repositório | `prm/repositorio.py` | `RepoJSON` (Fase 1, arquivos de `registro/prm/` com o envelope do `prm_local.py`) e `RepoSQL` (Fase 2, mesma interface, testado com sqlite); contador e sequência atômicos e persistentes |
| Autorização | `prm/identidade.py` | Token (Central e, na Fase 2, o registro do portal) → papel + escopo do escritório → dono da linha (404 fora do escopo); login simulado só em localhost |
| Rotas | `prm/rotas.py`, `central_api/rotas.py`, `function_app.py`, `dev_server.py` | 44 rotas `/api/prm/*` + as 5 rotas antigas da esteira agora com identidade. Contrato: `06-contrato-api.md` |
| Front-end | `central/web/prm.html`, `prm.js`, `prm.css`, `prm-componentes.css` | Face do parceiro (modo claro, barra inferior Início · Empresas · Registrar · Pedidos · Extrato, ficha com abas, primeiro acesso com aceite) e face da Save (modo escuro, seção Canal: visão, registros, conflitos, demandas, extratos, dossiês, acessos, níveis, parâmetros; barra inferior no celular) |
| Dados de teste | `prm/fixtures/demo.json` | Masters A–I, 3 consultores, 1 indicador, 4 usuários de parceiro, Empresas 01–21 com CNPJ alfanumérico fictício (dígito calculado na carga), 11 negócios, 9 registros em estados diferentes, 1 conflito, 1 pendência, extrato com linhas em todos os estados, 3 demandas e um histórico de respostas de teste |
| Testes | `central/api/tests/test_prm_*.py` | **177 testes novos** (331 no total com os 154 da Central), sem rede e sem Azure |

### 1.1 Como rodar
```
python3 central/dev_server.py --prm                       # http://localhost:4280/prm.html
cd central/api && PYTHONPATH=../../lib python3 -m unittest # 331 testes
node --check central/web/prm.js
```
A tela inicial do servidor local lista os usuários de teste (Titular do Master A, Consultor A1, Daniela, Luis, Financeiro) e os CNPJs de teste com o cenário de cada um (livre, cliente da Save, outro canal, empresa baixada, Simples, já é seu). Detalhes em `central/README.md`.

### 1.2 Verificações feitas
- `unittest`: 331 testes, OK (154 da Central intactos).
- `node --check central/web/prm.js`: OK.
- Navegador (servidor local), parceiro e Save, em 375 px e no desktop: todas as rotas abrem sem erro no console e sem rolagem lateral (`scrollWidth = 375`); registro enviado mostra o resultado na região viva, foco no título e, no celular, folha inferior; aprovação na fila da Save com modal e trilha.
- Auditor de promessas (`skills/depto-qualidade/scripts/auditar_texto.py`): catálogo `textos_parceiro.json` (teste automatizado) e 385 textos do `prm.js` → **0 alerta**.
- `infra/checar-dados.py` nos 47 arquivos novos e alterados: **0 achados** (nenhum CNPJ completo, CPF, telefone ou e-mail externo no repositório; os CPFs dos testes são gerados na hora).

---

## 2. Unificações (01 §4)

| # | Como ficou no código |
|---|---|
| **U1** registro × checagem × esteira × conflito | Uma entidade (`registro`) e um serviço (`checagem.classificar`) com as fontes na ordem da 02 §4.2: registros vivos → espelho do HubSpot → índice HMAC. O pedido de dossiê da esteira virou anexo do registro (`registro.dossie_id`, o E-NNNN fica como id de origem). A consulta de Lucro Real usa a mesma regra (`regime.consultar(protegido=…)`). `crm_checagem.py` e `conflito_canal.py` continuam como ferramentas internas (não foram tocados) |
| **U2** quatro filas de demanda | Uma fila (`demanda`) com `canal`/`origem` e o mesmo ID D-AAAA-NNNN; catálogo único `prm/catalogo.py` junta `sla.json` (23 tipos) e `catalogo.json` (29 pedidos da Central, como `CA-…`) com os 10 tipos que o parceiro vê. A tela da Save mostra as do portal e, só leitura, as do registro único (WhatsApp, e-mail) |
| **U3** caixa × notificações | `prm/notificacoes.py` grava no formato da `lib/caixa.py` (`para, assunto, resumo, origem, tipo, prioridade, anexos, acoes.go, lido_por, auditoria`) com `para = usuario:U-…`; idempotente; e-mail com a janela de 07h–20h (`email_apos`); `PRM_ESPELHAR_CAIXA=1` também põe o alerta interno na fila do painel |
| **U4** cinco botões de aprovar | `POST /api/prm/save/decidir`: registro, conflito, demanda, chamado, extrato, contestação, dossiê, usuário, pendência e parâmetro; cada decisão grava `prm_decisao` (quem, oid, papel, antes, depois, resultado padronizado) |
| **U5** quatro auditores | `prm/auditoria.py`: bloqueio de dado pessoal (CPF, rótulos de documento, banco, PIX, senha da `lib/protecao.py`) na entrada → `M-90`; auditor de promessas na saída de todo texto livre; lista de bloqueio da esteira no rigor "dossiê"; máscara `protecao.limpo` no que fica guardado |
| **U6** dossiê × biblioteca | O dossiê continua no `dossie_base.py`; a Biblioteca (P-10) mostra o catálogo pronto/em descoberta. O serviço de conteúdo único (kits por tese) fica para a Fase 3 |
| **U7** visão do canal × gestão × mesa | A visão do canal é a seção Canal (S-1) da face da Save; os alertas entram na caixa do papel. A integração com a Mesa e a Gestão do `portal/index.html` (Artifact) fica para o corte da Fase 2 (L8) |

## 3. Lacunas (01 §6)

| # | Situação | Como |
|---|---|---|
| **L1** rotas da esteira sem token | **Fechada** | `/api/regime`, `/api/esteira`, `/api/esteira/historico`, `/api/esteira/arquivo` em `rotas.py` e `function_app.py`, com o usuário vindo da identidade; PRM inteiro atrás de `autenticar` |
| **L2** papel e escopo de parceiro | **Fechada** | `titular`/`consultor` da tabela `usuario_parceiro` pelo `oid`; gate `Parceiro.Portal`; matriz 02 §2.2; filtro por linha em toda leitura; 404 fora do escopo; papéis novos `Partners.Financeiro` e `Partners.Contratos` (TI cria) |
| **L3** persistência no disco local | **Fechada no código** | Repositório com dois adaptadores; o SQL usa colunas promovidas (`parceiro_id`, `usuario_id`, `estado`, `cnpj_raiz_hmac`, `deal_id`) para filtro e RLS e o documento em `dados` |
| **L4** tetos em memória | **Fechada** | `repo.contar` persistente: consultas, registros e respostas neutras por usuário e dia; reincidência suspende o usuário; teste de reinício |
| **L5** caminhos fixos | **Fechada** | `central_api/caminhos.py`; `regime`, `negocio_ativo` e `esteira` não fazem mais `~/agentes-partners/lib`; tudo por variável (lista no README) |
| **L6** Word depende de Node | Aberta (Fase 2) | A rota existe e devolve 503 neutro sem Node; a recomendação (Function Node) segue |
| **L7** agentes pela API | Parcial | `Agentes.Processar` roda `POST /api/prm/save/rotina` (testado); `processar_pendencias`/`gravar_resultado` da esteira ainda pelo CLI |
| **L8** painel interno no Artifact | Aberta (Fase 2) | A face da Save existe em `central/web/prm.html`; a troca da camada `Fonte` do `portal/index.html` fica para o corte |
| **L9** índice HMAC no Mac | Aberta (Fase 2) | O índice continua o mesmo arquivo (falha fechada); na demo é montado das fixtures |
| **L10** histórico com dado de cliente | Mantida no Mac | `demandas.avaliador_lib()` usa `lib/historico.py` só no modo `--dados` (Mac); a demo usa um histórico fictício; o portal nunca consulta o índice |
| **L11** consulta externa de CNPJ | Desligada na demo | `CENTRAL_API_EXTERNA=0` no servidor local (`--externa` liga); parecer do Jurídico pendente |
| **L12** SWA sem regra por papel | Não se aplica ao MSAL | Com login pelo MSAL, `allowedRoles` do SWA não enxerga os papéis; a autorização fica na API. CSP ganhou `object-src 'none'`, `upgrade-insecure-requests` e `Cross-Origin-Opener-Policy` (04 §2.5) |
| **L13** chat com IA | Fora do PRM | — |
| **L14** duas regras de "ativo" | **Fechada** | Uma regra (`checagem.negocio_protege`) com o parâmetro `protecao.regra_ativo`: padrão `contrato_12m` (recomendação da DL-01), com falha fechada sem recebimento registrado; `qualquer_idade` mantém a regra do índice de 23/10 |
| **L15** README desatualizado | **Fechada** | `central/README.md` |
| **L16** trilha de acesso | **Fechada** | `seg_acesso_log` em toda leitura de dado do parceiro, gravação e negação (sem CNPJ em claro; IP só como HMAC) |
| **L17** timers fora do SWA | Aberta (Fase 2) | A rotina diária é uma função (`rotas.rotina`) chamável por timer; hoje roda por botão ou por `Agentes.Processar` |

## 4. P0 e P1 do design (05 §1.2)
- **P0-1/P0-2** resposta única: o envio do registro devolve o mesmo corpo e o mesmo texto `M-01` para livre, outro canal, cliente da Save, índice ausente e teto, com o mesmo piso de tempo (`registro.piso_resposta_ms`); a consulta usa `M-00` (frase da Central). Testado.
- **P0-3** contraste: rótulos em `--texto-2` com traço ouro (`.prm-rotulo--marca`); ouro só em botão, chip "pede você" e contador.
- **P0-4** campo e foco: borda do campo em `--texto-3`; anel duplo de foco (`.prm :focus-visible`).
- **P0-5** resultado anunciado: região viva que já existe (`#resultado-registro`, `aria-live`), foco no título, rolagem até ele; no celular, folha inferior (`.prm-modal`) com foco preso e Esc.
- **P1** barra inferior com Registrar no centro; KPIs 2×2 com "Pede você" antes; sem troca de tema/perfil no produto; chips com forma e texto; checagem em tempo real só do que é seguro (formato, dígito, "já é seu", situação na Receita); tabelas viram listas no celular; ações irreversíveis com modal; botões de 44 px. P2: "Pular para o conteúdo", título por tela, estados vazio/erro/carregando, `autocomplete`.

## 5. Decisões do Luis que o código deixou em parâmetro
Arquivo: `central/api/central_api/prm/parametros.json` (81 chaves: as 62 da 02 §3 mais as operacionais do código). Mudar não exige deploy (`PRM_PARAMETROS` ou a decisão `parametro/alterar`, com trilha e dona). Padrão = recomendação da área (02 §18 e `00-decisoes-luis.md`).

| Chave | Padrão | Unidade | Marca | Dona |
|---|---|---|---|---|
| `registro.unidade` | "raiz" | raiz \| raiz_tese | P · DL-01 | luis |
| `registro.validade_master_dias` | 120 | dias corridos | P · DL-02 | luis |
| `registro.validade_indicador_dias` | 90 | dias corridos | P · DL-02 | luis |
| `registro.prorrogacao_dias` | 60 | dias corridos | P · DL-02 | luis |
| `registro.prorrogacoes_max` | 1 | vezes | P · DL-02 | luis |
| `registro.atividade_para_prorrogar_dias` | 30 | dias corridos | P · DL-02 | luis |
| `registro.validade_conta_de` | "carimbo_completo" | — | P · DL-01 | luis |
| `registro.protecao_pos_contrato_meses` | 12 | meses após o último recebimento | P · DL-01 | luis |
| `protecao.regra_ativo` | "contrato_12m" | contrato_12m (sem recebimento registrado, protege) \| qualquer_idade | P · DL-01 (L14) | luis |
| `registro.preferencia_tese_nova_dias` | 15 | dias corridos | P · DL-01 | luis |
| `registro.cauda_mediacao_meses` | 6 | meses após expiração ou perda | P · DL-04 | luis |
| `registro.sla_conflito_du` | 10 | d.u. | P · DL-01 | luis |
| `registro.pausa_validade_em_conflito` | true | — | P · DL-01 | luis |
| `registro.complemento_mantem_carimbo_du` | 3 | d.u. | P · DL-01 | luis |
| `extrato.percentual_fonte` | "termo" | termo (fallback com selo) | A · P · D65 | contratos |
| `extrato.base_recuperacao` | "honorario_recebido" | — | A · P · DL-07 | financeiro |
| `extrato.deducao_antes_10pct` | "nenhuma" | — | P · OC-1 | financeiro |
| `extrato.corte` · `calculo_du` · `aprovacao_du` · `publicacao_du` | último dia · 5 · 7 · 8 | d.u. de M+1 | P · OC-18 | financeiro |
| `extrato.contestacao_dias` · `resposta_contestacao_du` | 10 · 5 | dias corridos · d.u. | P · OC-18 | financeiro |
| `extrato.pagamento_dia` · `nf_limite_dia` | 20 · 15 | dia de M+1 | P · OC-18 / DL-15 | financeiro |
| `extrato.estorno_limite_pct_ciclo` · `estorno_prazo_meses` | 50 · 24 | % · meses | P · DL-08 | luis |
| `extrato.mostra_valor_previsto` | false | — | P · DL-09 | luis |
| `retencao.irrf_pct` · `csrf_pct` · `regra_2027` | 1,5 · 4,65 · "a_validar" | % | P · Tributário | tributário |
| `demanda.anexos_habilitados` | false | — | P · DL-13 | jurídico |
| `nivel.modo` · `janela_meses` · `patamares` · `limite_por_negocio` · `so_sobe_apuracoes` · `observacao_trimestres` | "sombra" · 12 · (02 §3) · (02 §3) · 4 · 2 | — | P · F8 e D75 | luis |
| `academia.porta_ativa` | false | — | P · DL-18 | luis |
| `retencao_dados.contato_decisor_dias` · `registro_anos` · `acesso_log_meses` | 90 · 5 · 12 | — | P · DL-13 | jurídico |
| `termos_uso.versao` | "2026-10-rascunho" | versão vigente | A (R107) | jurídico |

Operacionais criados pelo código (a dona valida): `registro.piso_resposta_ms` = 900 ms; `registro.reincidencias_para_suspender` = 2; `calendario.expediente` = 8h–18h; `calendario.carnaval_feriado` = sim; `consulta.teto_diario_usuario` = 30 (04 §2.2).

**Parâmetros só catalogados (a regra ainda não roda):** `registro.unidade = raiz_tese` e `preferencia_tese_nova_dias` (só faz sentido se a DL-01 escolher raiz + tese), `cauda_mediacao_meses` (PRM-R36), estorno (`extrato.estorno_*`, PRM-R68–R70), calendário do extrato por d.u. (o cálculo e a liberação são por ação do Financeiro), CSRF (só o IRRF é retido), `retencao_dados.*` (expurgo), `lead_bdr.*`, `onboarding.marcos`, `academia.*`, `negocio.ecac_pendente_alerta_du`, `canal.saude_alerta`, `nivel.so_sobe_apuracoes`/`observacao_trimestres`. Ficam para a Fase 2/3 com os testes correspondentes.

## 6. Divergências entre as especificações (resolvidas assim no código)

| # | Divergência | Escolha | Quem confirma |
|---|---|---|---|
| 1 | `schema.sql` tem 7 estados de registro (`recebido`, `aprovado`, …) e 3 resultados de checagem; a 02 tem 13 estados e 6 resultados | Código segue a **02** (fonte das regras). O `schema.sql` precisa ser atualizado antes da Fase 2 (estados e `resultado_checagem`) | Dados |
| 2 | "Como você conhece": lista fechada na 02 §4.1, texto de 20+ caracteres na 05 §3 | Lista da 02 + observação livre opcional (500) | Design + Operações de Canal |
| 3 | Negócio próprio sem registro (caso 4 da 02 §12) não tem texto no catálogo | Texto novo `M-03c` "Esta empresa já está com o seu escritório desde {data}. Acompanhe em Empresas.", marcado como proposta (`_propostas`) | Luis (DL-12) |
| 4 | Papéis `financeiro` e `contratos` da 02 não existem no Entra (04 lista só `Partners.Gestor/Masters/BDR/Tecnica/Leitura`) | Papéis novos `Partners.Financeiro` e `Partners.Contratos` | TI |
| 5 | A consulta neutra (`M-00`) acontece antes do registro e, para cliente da Save, revela "não consegui consultar" | A tela deixa seguir e preencher a razão social à mão (igual a "Receita fora"), e o envio devolve o mesmo `M-01`. Mesmo piso de tempo na consulta | Luis (DL-03) |
| 6 | Na Fase 1 o `prm_local.py` refaz `prm_demanda.json` e `prm_extrato_linha.json` a cada rodada | O portal grava em tabelas de autoria (`prm_demanda_portal`, `prm_extrato_movimento`) e lê as geradas só para leitura; `PRM_REGISTRO_DEMANDAS` numera pela sequência do registro único | Dados |
| 7 | Validade a partir da aprovação ou do carimbo | Do carimbo (`registro.validade_conta_de = carimbo_completo`), com os dias em conflito devolvidos (PRM-R38) | Luis (DL-01) |

## 7. O que ficou para a Fase 2
1. Infra (TI): registros `SAVE-PRM-PARCEIROS` e `PRM-ROTINAS`, papéis novos, SWA Standard, Function App, Azure SQL, Key Vault (04 §4).
2. SQL real: `RepoSQL` com pyodbc + token da identidade gerenciada; RLS por `SESSION_CONTEXT`; contador com `UPDATE … SET n = n + 1 OUTPUT` (hoje o incremento é transacional, testado em sqlite); alinhar `schema.sql` (divergência 1).
3. Timers: rotina diária às 06h00 e sincronização do HubSpot na Function App separada (L17).
4. Word sem Node (L6); índice HMAC publicado no Blob (L9); consulta externa com parecer (L11).
5. Regras só catalogadas (seção 5): cauda de mediação, estorno, lead da BDR (`LEAD_BDR` já tem a máquina), onboarding e Academia, expurgo LGPD.
6. Painel interno: trocar a camada `Fonte` do `portal/index.html` pela API ou adotar `prm.html` como seção Canal (L8, U7).
7. Anexos de documento (DL-13) e e-mail ao parceiro (DL-12).

---

## 8. Entrega em 3 blocos

**1. O que você pediu**
PRM Save v2 funcionando em modo local sobre `central/`: back-end com repositório JSON/SQL, checagem única com resposta neutra idêntica e piso de tempo, máquinas de estado, `decidir` com trilha, auditor único, notificações, parâmetros com os padrões da spec e autorização em 3 camadas (L1, L2, L4, L5, L14, L16 fechadas); 44 rotas documentadas em `06-contrato-api.md`; as duas faces do site com os P0 do design corrigidos; fixtures fictícias; 177 testes novos (331 no total).

**2. O que você também precisa**
- A regra de proteção já sai com a recomendação da DL-01 (`contrato_12m`), mas, sem a fonte de recebimentos do Financeiro (P5), todo ganho continua protegido. A regra só muda o comportamento quando os recebimentos chegarem.
- `M-03c` é frase nova e precisa do ok do Luis (DL-12).
- O `schema.sql` está desalinhado dos estados da 02: corrigir antes do pedido à TI.
- Os papéis `Partners.Financeiro` e `Partners.Contratos` entram no pedido à TI.

**3. O que falta e quem fornece**
| Falta | Quem |
|---|---|
| Decisões DL-01…DL-18, F8, D102, D65, D109 (padrões já em parâmetro) | Luis |
| Fonte de recebimentos (P5) para o extrato sair de "previsto" | Financeiro |
| Infra e papéis da Fase 2 | TI da Save |
| Textos finais do Termo de Uso e do Aviso de Privacidade (a tela de aceite mostra a versão `2026-10-rascunho`) | Jurídico |
| Alinhamento do `schema.sql` | Dados |

**Registro `revisao`:** desenvolvedor do PRM (agente); revisão própria contra 02 (regras e textos), 04 (autorização) e 05 (P0/P1); 331 testes; auditor de promessas 0 alerta; `checar-dados` 0 achados; navegador em 375 px e desktop sem erro de console. Pendente: revisão do gerente do PRM.
