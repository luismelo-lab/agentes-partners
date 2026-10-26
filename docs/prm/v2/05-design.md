# PRM Save v2 · 05 · Especificação de design

**Versão:** 2.0 · **Data:** 26/10/2026 · **Área:** Design/UX (depto-marketing e marca, especialista do Design System Save v0.5) · **Para:** gerente do PRM v2 e Luis · **Status:** especificação para revisão das áreas
**Base lida:** Design System Save v0.5 (`departamentos/marketing-marca/padrao/`: LEIA-ME, marca.json, save.css, tailwind-preset.js, logos; `design-system/`: handoff, Components Library, Mobile and Data Viz, Tokens Apps and A11y); `docs/prm/desenho-prm-save-2026-10-26.md`; `docs/prm/engenharia-reversa-prm-2026-10-26.md`; `docs/prm/contexto-interno-prm-2026-10-26.md` (R25); `docs/prm/prm-save-prototipo.html`, percorrido no navegador nas duas visões, em 375 px e no desktop; `central/web/` (login MSAL, consulta de Lucro Real, dossiê da esteira); `central/README.md`; `portal/index.html` (painel interno escuro: caixa, mesa, gestão, pedidos, demandas, paleta ⌘K).
**Entrega junto:** `docs/prm/v2/prm-componentes.css` (componentes do PRM sobre o `save.css`, só com tokens).

---

## 0. Decisões de design em uma página

1. **Três toques valem mais que oito módulos.** No celular, o parceiro tem uma barra inferior com 5 destinos: **Início · Empresas · Registrar (centro, em ouro) · Pedidos · Extrato**. Registrar uma empresa, ver o andamento e pedir algo ficam a 1 toque de qualquer tela.
2. **"Empresas" junta Registros e Meus negócios.** Para o contador, a unidade é a empresa do cliente, não o objeto do sistema. A ficha da empresa mostra o registro, o estado do negócio, o dossiê e os pedidos ligados a ela.
3. **Consulta de Lucro Real e registro viram um fluxo só.** O parceiro digita o CNPJ uma vez. A tela traz os dados da Receita e o regime, e oferece **Registrar oportunidade** e **Pedir dossiê**. Hoje são dois produtos separados (`central/web/consulta.html` e o protótipo).
4. **Checagem em tempo real só do que é seguro mostrar.** Enquanto o parceiro digita, a tela confere o formato e o dígito do CNPJ (inclusive o alfanumérico), a situação na Receita e os **registros do próprio parceiro**. A checagem contra a carteira da Save só roda no envio e devolve **uma única resposta** para "livre", "outro canal" e "cliente da Save" (R25). O protótipo diferencia "livre" de "em análise" e, com isso, entrega a carteira a quem testar CNPJs (P0-1).
5. **Claro para o parceiro, escuro para a Save,** sem botão de tema no portal do parceiro. A visão da Save entra no painel interno (`portal/`) como a seção **Canal**, com o mesmo menu lateral, a caixa e a paleta ⌘K que o time já usa.
6. **O ouro marca o que pede ação.** Botão principal, chip "Precisa de você", cartão de pendência e contador. Ele não serve para decorar nem para texto pequeno: o `#B58A1F` dá **3,17:1** sobre branco, e não 4,5:1, como diz o handoff do Marketing (item A-1).

---

## 1. Avaliação crítica do protótipo atual

**Método.** Percorri as 11 telas (7 do parceiro e 4 da Save) em 375×812 e no desktop. Fiz um registro em cada um dos três resultados, abri um pedido e conferi a fila, os lotes e as demandas. Medi o contraste pela fórmula de luminância da WCAG 2.2 e li o código (ARIA, foco, estrutura). A régua tem três partes: as 10 heurísticas de Nielsen (H1 a H10), a WCAG 2.2 AA (critério entre parênteses) e a aderência ao DS Save v0.5.

### 1.1 O que fica (acertos que a v2 mantém)
- Os 7 estados do negócio estão em linguagem do parceiro, com **próximo passo** e **"com quem está"**. Isso responde à pergunta mais frequente do parceiro e fica igual na v2.
- O extrato tem 4 estados e mostra a linha "em conferência contratual" sem valor nem data. A frase "não há valor até o cliente pagar o honorário" protege contra a leitura de cobrança.
- O selo "Respondido pelo histórico" / "Chamado aberto · área" deixa visível o caminho da demanda.
- A fila da Save mostra o motivo real da checagem, e o parceiro vê só a mensagem neutra. Conflito vai "com o Luis".
- Na base técnica, o HTML é semântico na maior parte (`nav`, `main`, `section`, `caption` nas tabelas), tem `:focus-visible`, `prefers-reduced-motion`, área de toque de 44 px no menu e CNPJ mascarado.

### 1.2 Problemas priorizados

Severidade: **P0** bloqueia o piloto (risco de LGPD, regra da casa ou WCAG A); **P1** corrigir antes do piloto; **P2** corrigir na v2; **P3** melhoria.

| # | Sev. | Régua | Onde | Problema | Correção na v2 |
|---|---|---|---|---|---|
| P0-1 | P0 | R25 · H5 | Registrar | As respostas "Livre" ("Registro recebido") e "Em análise pela Área Partners" ("precisa de uma análise antes do registro") são diferentes. Quem testar CNPJs descobre quem já é cliente ou tem outro canal: é a varredura da carteira que o desenho quer evitar | No envio, uma resposta única para todos os casos que não são do próprio parceiro: **"Registro recebido · em análise"**, com o mesmo texto, o mesmo chip e o mesmo prazo de retorno. A diferença só aparece depois da decisão humana (aprovado / não aprovado com motivo genérico). Teto diário e alerta de acertos seguem como no `central/` |
| P0-2 | P0 | R25 · consistência | Registrar × Consulta | São dois textos neutros diferentes: no registro, "Em análise pela Área Partners"; no `central/`, "Não foi possível seguir com esta consulta. Fale com a Área Partners." | Uma frase por contexto, guardada no glossário (seção 6): na consulta, a do `central/`; no registro, a do P0-1. Nenhuma tela inventa outra variação |
| P0-3 | P0 | 1.4.3 · DS | Todas | O rótulo (`.rot`) em ouro de texto 11 px dá 3,17:1 sobre branco e 2,96:1 sobre o fundo; aparece em todo cabeçalho e KPI. O texto fraco (`.fraco`, `#838892`, 13 px) dá 3,56:1 e carrega informação (validade, "com quem está", datas) | Rótulo em `--texto-2` com traço ouro antes (`.prm-rotulo--marca`); texto 3 só para desabilitado. Informação nunca em texto 3 |
| P0-4 | P0 | 1.4.11 · 2.4.7 | Formulários e foco | A borda do campo (`--borda-3`) dá 1,61:1: o campo "some" no fundo branco. O anel de foco ouro dá 1,53:1 sobre branco | Borda do campo em `--texto-3` (3,56:1). Foco em anel duplo: traço na cor do texto mais halo ouro (`.prm :focus-visible`) |
| P0-5 | P0 | 4.1.3 · H1 | Registrar, Demandas | O resultado do envio aparece via `innerHTML` de toda a tela: o leitor de tela não anuncia (a região `role=status` nasce junto com o conteúdo), o foco se perde e, no celular, o resultado fica 1.220 px abaixo, fora da vista (medido) | Envio sem recarregar a tela. O resultado entra numa região viva que já existe, o foco vai para o título do resultado e a tela rola até ele. No celular, o resultado abre em folha inferior (`.prm-modal`) |
| P1-1 | P1 | H7 · Mobile | Casca do parceiro | O menu de 7 itens rola de lado no topo e, a 375 px, só 2,5 itens aparecem. Registrar, que é a ação mais frequente, fica atrás de um deslize | Barra inferior com 5 destinos e Registrar no centro (seção 2.1) |
| P1-2 | P1 | H8 · Mobile | Início (375 px) | Os 4 KPIs se empilham um por linha: "Pede ação sua" começa em y = 923 px, fora da primeira tela (medido) | KPIs em grade 2×2 compacta, com o cartão **"Pede você"** antes deles; o primeiro item pendente aparece na primeira dobra |
| P1-3 | P1 | H4 · DS | Topo | O protótipo tem botão de tema claro/escuro e troca o perfil Parceiro/Save no topo. No produto, o parceiro nunca vê a Save, e o DS manda modo claro para parceiro | Tirar os dois no produto. O perfil vem do login (papel no Entra). A troca fica só no protótipo de revisão |
| P1-4 | P1 | 1.3.1 · 4.1.2 | Barra de nível | `role="img"` com aria-label em vez de barra de progresso; o valor não é lido como progresso | `role="progressbar"` com `aria-valuenow` e `aria-valuetext` (componente `.prm-nivel`) |
| P1-5 | P1 | 1.4.1 · DS | Chips | O chip comunica pelo ponto colorido, mas todos os pontos têm a mesma forma; em cinza, ok e alerta são iguais. O verde claro (4,21:1) e o âmbar (3,68:1) não servem para texto | Forma por estado (círculo, losango, quadrado, anel) mais texto em `--texto`. A cor fica no ponto e na borda (`.prm-chip--*`) |
| P1-6 | P1 | H5 · 3.3.1 | Registrar | A checagem só roda no envio. O CNPJ errado só aparece depois, numa linha `.fraco`, sem ligação com o campo (`aria-describedby` = 0, medido). A empresa inativa ou baixada não é detectada | Checagem em tempo real (seção 3, P-3): formato, dígito, situação na Receita e "já é seu", com mensagem ligada ao campo |
| P1-7 | P1 | H3 · H5 | Registrar | Os botões de exemplo ("Testar: 11.111.111/… já seu") estão no formulário | Só no protótipo; sai no produto |
| P1-8 | P1 | H2 | Toda a visão do parceiro | Há jargão interno na tela: "leitura-sombra", "raiz do CNPJ (os 8 primeiros caracteres)", "Central Masters", "carimbo de hora", "volume ativo", "CSRF" | Glossário (seção 6): "nível em teste até a decisão do programa", "a empresa toda (matriz e filiais)", "time da Save que atende você", "data e hora do registro". Termo técnico só com ajuda ao lado |
| P1-9 | P1 | 1.4.10 · Mobile | Visão do canal, Demandas por SLA | Tabela de 811 px numa tela de 341 px: rola de lado (medido) | No celular, a tabela vira lista de cartões (`.prm-tabela--vira-lista` mais `.prm-lista`). A Save também usa o celular (Daniela entre reuniões) |
| P1-10 | P1 | H3 · H5 | Fila, Extratos a liberar | Aprovar, Recusar, Enviar a conflito, Liberar lote e "Marcar NF recebida" agem com 1 clique, sem confirmar e sem desfazer | Ação irreversível com modal de confirmação que resume o efeito; ação reversível com toast "Desfazer" por 8 s |
| P1-11 | P1 | 2.5.8 | Botões pequenos | `.btn.peq` tem 36 px e os chips de exemplo 32 px. A WCAG 2.2 pede 24 px e passa, mas o DS manda 44 px no celular | `.prm-btn` com 44 px sempre; 48 px no botão principal do celular |
| P2-1 | P2 | H6 | Meus negócios | 7 contadores por estado, um por cartão, ocupam meia tela e não filtram nada | Abas-filtro com contador ("Precisa de você 1 · Em andamento 6 · Encerrados 1") |
| P2-2 | P2 | H1 | Início, Negócios | "O que mudou desde a última visita" está no subtítulo, mas a tela não marca o que mudou | Marca "Novo" nas linhas alteradas desde o último acesso, mais a caixa de avisos (sino) |
| P2-3 | P2 | H9 | Erros | Não há tela de erro de rede, sessão expirada, sem permissão nem carregamento | Estados obrigatórios em cada tela (seção 3) |
| P2-4 | P2 | H10 | Todas | Não há ajuda contextual (por que "previsto" não tem valor, o que é prorrogação) | Ícone "?" com ajuda curta em linha e glossário em Ajuda |
| P2-5 | P2 | 2.4.1 · 2.4.2 | Casca | Não há "Pular para o conteúdo"; o `<title>` não muda por tela | `.prm-pular`; título "Tela · PRM Save" a cada rota |
| P2-6 | P2 | 1.3.5 | Formulários | Sem `autocomplete` adequado (`organization`, `email`, `tel`) | Atributos conforme a tabela da P-3 |
| P2-7 | P2 | DS | Logo | A linha "Portal de Parceiros" ao lado do logo, com separador, é quase uma submarca | Só o logo Save Co.; o nome da tela vai no `<h1>` (sem submarca, regra do DS) |
| P2-8 | P2 | H4 | Save | Dois vocabulários para o mesmo estado: "Pronto para liberar", "OK", "Pendente" e "Fora · 24 h" | Estados da Save padronizados (seção 4.3) |
| P2-9 | P2 | R12 · H5 | Nível (parceiro titular) | "Jornada dos seus consultores" mostra "Sem indicação em 90 dias" com o nome do consultor. Isso é avaliação de pessoa, e o titular pode usar como cobrança | Mostrar só a etapa da jornada (Registrado, Certificado, Pleno). Atividade individual vai para a ficha 360 da Save |
| P3-1 | P3 | DS | Cartões | Raio de 10 px em `.passo`, `.nota` e `.toast`, fora da escala (4, 8, 12, 16, 24) | Escala oficial |
| P3-2 | P3 | DS | Tipografia | Tamanhos fora da escala (13,5 / 14,5 / 15 / 23 / 28 px) | Escala `--t-*` do `save.css` |
| P3-3 | P3 | DS | Cores | Tokens redefinidos à mão no próprio HTML (cópia do marca.json) | Carregar `save.css` e `prm-componentes.css`; nenhum valor no HTML |

### 1.3 Contraste medido (26/10/2026)

| Par | Razão | Veredito para o PRM |
|---|---|---|
| Texto `--texto` sobre branco | 18,9:1 | qualquer texto |
| `--texto-2` sobre branco / sobre `--fundo-2` | 8,23 / 7,36:1 | qualquer texto |
| `--texto-3` sobre branco / sobre `--fundo` | 3,56 / 3,32:1 | só desabilitado; serve de borda de campo (≥ 3:1 sobre branco) |
| `--ouro-texto` sobre branco / `--fundo` / `--ouro-suave` | 3,17 / 2,96 / 2,82:1 | só texto ≥ 24 px (ou 18,66 px em negrito) sobre branco; nunca sobre o ouro suave |
| `--sucesso` claro sobre branco | 4,21:1 | ponto, borda e ícone; não serve para texto pequeno |
| `--alerta` claro sobre branco | 3,68:1 | ponto, borda e ícone |
| `--erro` claro / `--info` claro sobre branco | 5,80 / 6,18:1 | texto ok |
| `--texto` sobre `--ouro` | 12,34:1 | botão e chip "pede você" |
| `--borda-3` sobre branco | 1,61:1 | só divisória; não delimita campo |
| `--texto-2` escuro sobre `--cartao` escuro | 6,94:1 | qualquer texto |
| `--texto-3` escuro sobre `--cartao` escuro | 3,36:1 | **não usar** para texto; o PRM troca por `--texto-2` |
| `--erro` escuro sobre `--cartao` escuro | 4,09:1 | não serve para texto pequeno; botão de perigo usa texto `--texto` e borda `--erro` |
| `--ouro` / `--alerta` / `--info` escuros sobre `--cartao` escuro | 11,71 / 9,37 / 5,92:1 | ok |

**A-1 · Achado para o dono do DS (Marketing).** Em "Acessibilidade", o handoff do v0.5 diz que o `#B58A1F` dá "4.5:1 ✓ AA" sobre branco. A medição dá **3,17:1**, a mesma do especialista em 22/10/2026. O `prm-componentes.css` contorna o problema sem criar cor. A sugestão vai para a decisão do Marketing: criar um token `ouro-texto` de corpo mais escuro (um tom na faixa de `#8A6A14` dá cerca de 5:1 sobre branco e 4,5:1 sobre o ouro suave). Até lá, o PRM não usa ouro como texto pequeno.
**A-2.** O tema escuro do `portal/index.html` usa tokens próprios (`--linha #1C1C20`, `--texto-3 #A3A3AB`), fora do DS. O cinza mais claro dele corrige um contraste que o DS reprova (3,36:1). Proposta ao Marketing: levar ao DS v0.6 um `texto-3` escuro de pelo menos 4,5:1 e alinhar o portal ao `save.css`. A seção Canal do PRM usa o `.escuro` do `save.css` com o apelido `--prm-texto-mudo` = `--texto-2`.

---

## 2. Arquitetura de informação

### 2.1 Parceiro (portal externo, modo claro)

**Persona-guia.** Contador ou consultor, no celular, entre um cliente e outro, com 2 minutos e uma mão livre. Ele vem com três perguntas: *"Essa empresa já está registrada comigo?"*, *"Em que pé está o cliente X?"* e *"Preciso que a Save me responda Y."*

**Navegação no celular (barra inferior fixa, 56 px mais a área segura):**

| Posição | Destino | Ícone (Lucide) | Contador | Tarefa que resolve em 1 toque |
|---|---|---|---|---|
| 1 | **Início** | `home` | itens que pedem você | o que pede ação hoje |
| 2 | **Empresas** | `building-2` | negócios em "Precisa de você" | ver andamento |
| 3 (centro, ouro) | **Registrar** | `plus` | — | registrar empresa |
| 4 | **Pedidos** | `message-square` | respostas não lidas | pedir algo |
| 5 | **Extrato** | `receipt` | linhas que pedem NF | remuneração |

**Topo (56 px):** logo Save Co. à esquerda; à direita, busca (`search`), sino (`bell`, com contador) e avatar. O avatar abre o menu **Mais**: Nível e jornada · Biblioteca e Academia · Ajuda e glossário · Meu perfil · Minha equipe (só o titular) · Sair.

**Desktop (≥ 768 px):** menu lateral de 248 px com os mesmos destinos, na mesma ordem, mais o grupo "Programa" (Nível, Biblioteca) e o rodapé com o perfil. O botão "Registrar oportunidade" fica fixo no topo do menu.

**Mapa de telas e rotas** (rota com `#/` para funcionar no Static Web Apps sem servidor):

```
#/inicio                      P-1  Início
#/registrar                   P-3  Nova empresa (consulta + registro)
#/empresas                    P-4  Empresas (abas: Precisa de você · Em andamento · Registros · Encerradas)
#/empresas/{id}               P-5  Ficha da empresa (registro, estado, linha do tempo, dossiê, pedidos)
#/pedidos                     P-6  Pedidos (lista)
#/pedidos/novo?empresa={id}   P-6a Novo pedido (pré-preenchido quando vem da ficha)
#/pedidos/{id}                P-6b Pedido (conversa e resposta)
#/extrato                     P-7  Extrato (resumo + linhas)
#/extrato/{id}                P-7a Linha do extrato (cálculo, NF, contestação)
#/avisos                      P-8  Caixa de avisos (gaveta no desktop, tela no celular)
#/nivel                       P-9  Nível e jornada
#/biblioteca  · /{kit}        P-10 Biblioteca e Academia
#/perfil · #/equipe · #/ajuda P-11 Perfil, equipe, ajuda
#/boas-vindas                 P-0  Primeiro acesso (seção 5)
```

**Atalhos que cortam caminho:**
- Na ficha da empresa, os botões **"Perguntar sobre esta empresa"** (abre P-6a já ligado) e **"Ver no extrato"**.
- No aviso, o toque leva direto ao item: o aviso "Documento pedido" abre a ficha com o pedido em destaque.
- Link direto do e-mail ou WhatsApp de aviso para `#/empresas/{id}`. Sem sessão, o login devolve ao mesmo destino.
- A busca do topo procura empresa (nome ou CNPJ), pedido (D-AAAA-NNNN) e kit.

### 2.2 Save (seção "Canal" dentro do painel interno `portal/`, modo escuro)

A Fase 1 nasce no painel. A seção Canal **não cria um segundo aplicativo**: entra como item do `MENU` do `portal/index.html`, com subtelas e a mesma casca (menu lateral, topo com caminho, ⌘K, gaveta, caixa).

```
Canal
├── Visão do canal            S-1  (KPIs, saúde por parceiro, concentração, filas)
├── Parceiros                 S-2  lista → ficha 360 S-2a (pipeline, registros, extrato, demandas, nível, acessos)
├── Registros                 S-3  fila → detalhe S-3a (histórico da raiz, decisão)
├── Conflitos                 S-4  (fatos, regra, decisão do Luis)
├── Demandas                  S-5  (fila por SLA; é a tela "WhatsApp · Demandas" do portal, com filtro Origem)
├── Dossiês e esteira         S-6  (pedidos de dossiê, auditoria, aprovação)
├── Extratos                  S-7  lotes por parceiro → linha; contestações S-7a
├── Níveis                    S-8  (simulação trimestral, cartas)
├── Biblioteca                S-9  (catálogo, estado do produto, uso)
└── Acessos e convites        S-10 (usuários do parceiro, convites, últimos acessos, bloqueio)
```

No celular, a barra inferior do portal (Caixa · Mesa · Pedidos · Demandas · Áreas) ganha **Canal** no lugar de **Áreas**, e Áreas vai para o menu "Mais".

### 2.3 Onde entram os módulos que vêm da Central

| Módulo da Central | Hoje | No parceiro | Na Save |
|---|---|---|---|
| **Consulta de Lucro Real** (`central/web/consulta.html`, `regime.py`) | Página solta, sem login, com histórico próprio | É o **primeiro passo de P-3 (Registrar)**: o CNPJ traz Receita, regime e ano-base. "Consultar várias de uma vez" (até 20) fica em P-3, na aba "Várias empresas", que só consulta e não registra em lote. O histórico das últimas 30 consultas aparece como "Consultadas recentemente" em P-3 | Trilha de consultas (`consultas-regime.jsonl`) na ficha 360 (S-2a), com o alerta de varredura em S-1 |
| **Dossiê do cliente e esteira** (`esteira.py`, `dossie_base.py`, Word sob demanda) | Botão "Pedir análise e esteira" na consulta | Na **ficha da empresa (P-5)**, aba **Dossiê**, com os estados *Em preparo · Pronto · Em revisão*. O resumo aparece aberto e as seções vêm recolhidas, como no `central/`; "Baixar em Word" fica ao lado. Em P-3, depois do registro, a tela oferece "Pedir dossiê desta empresa" | **S-6 Dossiês e esteira**: fila com auditoria de promessas (alerta ALTO/MÉDIO), "Aprovar e publicar" e "Manter versão-base" |
| **Central de Agentes** (pedidos do time pelo painel, `[AGENTES]`) | Tela Pedidos do portal | O parceiro não vê agentes. O que ele pede entra em **Pedidos (P-6)**; a resposta sai em nome da Save ("Resposta da Save"), nunca de "agente" ou "IA" (DS: IA é executiva, não chatbot) | Pedido do parceiro que precisa de área vira **pedido à Central de Agentes**, que prepara a pré-análise e devolve em 3 blocos. A tela S-5 mostra o vínculo "Pré-análise da área pronta" |
| **Caixa de entrada / notificações** (`#caixa` do portal: Não lidas, Relatórios, Alertas, Pedidos) | Só interno | **Sino e caixa de avisos (P-8)** com 5 tipos: Pede você · Resposta · Empresa · Extrato · Programa. Resumo diário por e-mail só se o parceiro ligar (o padrão é desligado) | A Caixa do portal ganha o filtro **Canal** (registro novo, conflito, contestação, demanda fora do SLA, convite aceito) |
| **Demandas com resposta pelo histórico** (`lib/historico.py`, 7.407 documentos) | Tela WhatsApp · Demandas | Em **P-6**, o chip **"Resposta pelo histórico"**, sempre conferida pela Save antes de sair. O parceiro nunca vê a resposta antes da conferência | Em **S-5**, a sugestão do histórico aparece ao lado do pedido, com os botões "Aprovar e enviar", "Editar" e "Abrir chamado (rascunho GLPI)" |

---

## 3. Especificação tela a tela

**Convenções.** *Componentes* citam as classes do `prm-componentes.css` (prefixo `prm-`) e do `save.css`. *Estados* obrigatórios em toda tela: **carregando** (esqueleto no formato do conteúdo, nunca spinner de página inteira), **vazio**, **erro** (o que houve, o que fazer e "Tentar de novo") e **sem permissão**. Os textos entre aspas são o microcopy final proposto, a validar pelo Jurídico onde a seção 6 indica. Nenhum texto promete valor, prazo ou êxito.

**Estados comuns (valem para todas as telas do parceiro):**
| Estado | Texto |
|---|---|
| Sessão expirada | "Sua sessão terminou por segurança. Entre de novo para continuar de onde parou." [Entrar com a Microsoft] |
| Sem permissão (perfil sem papel) | "Seu acesso ao portal ainda não foi liberado. Fale com o time da Save que atende você." [Sair] |
| Sem permissão (consultor tenta ver empresa de outro consultor) | "Esta empresa está com outra pessoa do seu escritório. Peça ao titular, se precisar." |
| Sem conexão | aviso no topo, `.prm-aviso--atencao`: "Sem conexão. Mostramos os dados da última atualização, de {data hora}." |
| Erro do servidor | `.prm-aviso--erro`: "Não conseguimos carregar esta parte agora. Tente de novo em instantes." [Tentar de novo] |
| Manutenção da fonte (HubSpot do dia não chegou) | `.prm-aviso--info`: "Os estados das empresas são de {data}. A atualização de hoje ainda não chegou." |

### P-1 Início (parceiro)
- **Objetivo:** em 5 segundos, saber o que pede ação e o que mudou.
- **Conteúdo, em ordem:** (1) saudação curta "Olá, {nome}"; (2) cartão **Pede você** (`.prm-cartao--acao`) com até 3 itens: documento, acesso ao e-CAC, NF a emitir, prorrogação a pedir, cada um com o botão do próprio item, mais "Ver tudo (n)"; (3) grade 2×2 de KPIs: *Pedem você · Em andamento · Registros válidos · Respostas novas*; (4) **O que mudou** (últimos 7 dias, até 5 linhas com marca "Novo"); (5) **Registros a vencer** (30 dias); (6) **Seu nível** (barra compacta); (7) **Kit sugerido** (1 cartão).
- **Componentes:** `.prm-cartao--acao`, `.prm-grade--kpi`, `.prm-kpi`, `.prm-lista`, `.prm-chip`, `.prm-nivel`.
- **Vazio (sem nenhuma empresa):** `.prm-vazio`: "Você ainda não registrou empresas. Comece pela que você conhece melhor: o registro leva poucos minutos e protege a sua indicação por um prazo." [Registrar empresa] [Ver como funciona]. *(O prazo exato só entra depois da decisão da validade.)*
- **Vazio do "Pede você":** "Nada pendente com você agora."
- **Carregando:** esqueleto de 1 cartão alto mais 4 KPIs.
- **Mobile:** "Pede você" entra antes dos KPIs; os KPIs ficam em 2×2 com valor em 18 px; o resto vem em lista. O botão "Registrar" não se repete no corpo, porque já está na barra.

### P-3 Nova empresa: consulta + registro
- **Objetivo:** registrar uma empresa em até 2 minutos, com o mínimo de digitação e sem expor a carteira da Save.
- **Fluxo:** um passo só, com seções que se revelam. **(A) CNPJ** → **(B) Empresa encontrada** (Receita: razão social, situação, UF, CNAE, regime e ano-base) → **(C) Sobre a oportunidade** → **[Registrar oportunidade]** → **(D) Resultado**. Abaixo de (B) aparece também o link "Só quero o dossiê, sem registrar", que leva ao pedido de dossiê da esteira.
- **Campos:**

| Campo | Tipo | Obrigatório | Atributos | Regra |
|---|---|---|---|---|
| CNPJ | texto, Mono, máscara | sim | `inputmode="text"`, `autocapitalize="characters"`, `autocomplete="off"`, `spellcheck="false"`, `aria-describedby` dica+mensagem | Aceita numérico e alfanumérico (IN RFB 2.229/2024); aceita colar com ou sem pontuação |
| Razão social | preenchido pela Receita, editável só se a Receita falhar | sim | `autocomplete="organization"` | — |
| Decisor: nome e cargo | texto | sim | `autocomplete="off"` | Sem CPF (o campo bloqueia a sequência de 11 dígitos com a dica "Não precisamos de CPF") |
| Decisor: e-mail corporativo | e-mail | um dos dois | `type="email"`, `autocomplete="off"` | — |
| Decisor: telefone da empresa | tel | um dos dois | `type="tel"` | Dica "Telefone da empresa, não o pessoal" (regra da casa) |
| Interesse | seleção | sim | — | Produtos prontos + "Ainda não sei". Produto em validação não aparece |
| Como você conhece a empresa | texto longo | sim (mín. 20 caracteres) | — | Exemplo no placeholder |
| Evidência | arquivo | não | PDF/imagem até 10 MB | "Ex.: e-mail do sócio pedindo a revisão" |
| Declaração | caixa de seleção | sim | — | "Tenho relação com esta empresa e autorização para apresentá-la à Save." *[texto a validar com o Jurídico]* |

- **Checagem em tempo real no campo CNPJ** (`.prm-campo[data-estado]`, mensagem em `.prm-campo__msg` com `aria-live="polite"` e espera de 400 ms depois da última tecla):

| Estado do campo | Gatilho | Mensagem | Efeito |
|---|---|---|---|
| vazio | — | dica: "CNPJ com ou sem pontuação. Pode ser numérico ou com letras." | — |
| incompleto | < 14 caracteres válidos | (nenhuma enquanto digita) | — |
| erro de formato | caractere inválido ou dígito verificador não confere | "Este CNPJ não confere. Revise os números." | botão desabilitado |
| consultando | 14 válidos | "Buscando na Receita Federal…" | — |
| já é seu | raiz com registro ou negócio **do próprio parceiro** | "Você já registrou esta empresa em {data}. Registro {id} · {estado} · válido até {data}." [Abrir empresa] | não deixa registrar de novo |
| inativa | situação ≠ ativa | "Na Receita, esta empresa aparece como {situação}. Só registramos empresas ativas." | botão desabilitado |
| ok | ativa e não é do parceiro | "{Razão social} · {UF} · {regime} no ano-base {ano}" (cartão `.prm-empresa`) | libera a seção C |
| Receita fora | API indisponível | "A Receita não respondeu agora. Você pode seguir e preencher o nome da empresa." | razão social vira editável |
| limite diário | teto por usuário | mensagem neutra do `central/`: "Não foi possível seguir com esta consulta. Fale com a Área Partners." | — |

  O tempo real **nunca consulta a carteira da Save**: o "já é seu" usa só os dados do próprio parceiro.
- **(D) Resultado do envio** (região viva; o foco vai para o título):
  - **Recebido** (todos os casos que não são do parceiro, inclusive outro canal ou cliente da Save): `.prm-resultado--recebido` · título "Registro recebido · {id}" · texto "Data e hora: {dd/mm/aaaa hh:mm}. O time da Save analisa e responde aqui e no seu e-mail. A proteção da indicação começa quando o registro for aprovado." · ações [Pedir dossiê desta empresa] [Registrar outra] [Ir para Empresas].
  - **Não enviado** (erro de rede): `.prm-aviso--erro` "O registro não foi enviado. Seus dados continuam no formulário." [Tentar de novo].
- **Aba "Várias empresas":** só consulta (até 20 CNPJs, como no `central/`), devolve a lista com regime e o botão "Registrar" em cada linha. **Não há registro em lote**: cada registro exige o contexto da relação.
- **Mobile:** uma coluna; o botão de envio fica em `.prm-form__rodape`, fixo acima da barra inferior; o teclado alfanumérico abre já em maiúsculas; o resultado abre em folha inferior.
- **Sem permissão:** o indicador sem termo vigente vê "Para registrar empresas, seu termo de parceria precisa estar ativo. Fale com o time da Save que atende você."

### P-4 Empresas
- **Objetivo:** ver o andamento de todas as empresas e achar uma em segundos.
- **Conteúdo:** busca no topo (nome ou CNPJ); abas-filtro com contador **Precisa de você · Em andamento · Registros · Encerradas**; lista de cartões com nome, CNPJ mascarado (`12.•••.•34/••••-••`), chip de estado (seção 4.3), próximo passo em 1 linha, "Com: {quem}" e "desde {data}". No registro, o chip mostra o estado e a validade.
- **Ordenação padrão:** "Precisa de você" primeiro, depois a mudança mais recente. Seletor: Mais recentes · Nome · Validade.
- **Titular do escritório:** filtro "Consultor: Todos | {nome}".
- **Vazio por aba:** *Precisa de você*: "Nenhuma empresa espera algo de você." · *Registros*: "Nenhum registro em análise ou válido." [Registrar empresa] · *Encerradas*: "Nenhuma empresa encerrada."
- **Mobile:** a linha inteira é tocável (`.prm-lista__link`, 56 px); as abas rolam de lado com a ativa sempre visível.

### P-5 Ficha da empresa
- **Objetivo:** responder "em que pé está" sem precisar perguntar.
- **Cabeçalho:** nome, CNPJ mascarado, chip de estado e "Com: {quem} desde {data}". Ações: [Perguntar sobre esta empresa] [Enviar documento] (só quando o estado for "Precisa de você").
- **Abas:** **Andamento** (linha do tempo vertical `.prm-tempo` com os 7 estados, a data de cada passo e o próximo passo em destaque) · **Registro** (data e hora, validade, prorrogação: "Pedir prorrogação" só quando faltam 30 dias ou menos e há avanço) · **Dossiê** (da esteira) · **Pedidos** (desta empresa) · **Extrato** (linhas desta empresa).
- **Estado "Precisa de você":** cartão `.prm-cartao--acao` no topo com o pedido exato ("O técnico precisa da procuração do e-CAC assinada pelo cliente.") e o botão de envio.
- **O que nunca aparece:** valor estimado de crédito, chance de êxito, prazo de PER ou de restituição, tese "provável".
- **Encerrado:** "Encerrado em {data}. Motivo: {motivo padronizado}." Se o parceiro quiser entender, [Perguntar sobre esta empresa].
- **Mobile:** as abas viram segmentos roláveis; a linha do tempo mostra o passo atual e os 2 anteriores, com "Ver tudo".

### P-6 Pedidos (lista, novo, conversa)
- **Objetivo:** pedir algo à Save sem WhatsApp e acompanhar a resposta.
- **Novo pedido (P-6a):** 3 campos: **Sobre o quê** (botões grandes: Andamento de empresa · Documento · Contrato · Dúvida técnica · Remuneração · Material · Reunião · Outro), **Empresa** (busca; vem preenchida quando o pedido nasce da ficha) e **Seu pedido** (texto). Aviso fixo abaixo do texto: "Não escreva CPF, RG, CNH ou dados bancários." Se o texto tiver um padrão desses, o campo avisa antes do envio (`lib/protecao.py`).
- **Depois de enviar:** toast "Pedido {id} enviado." e a conversa abre. O estado inicial é "Recebido".
- **Estados do pedido (chips):** Recebido · Em preparo (a Save está conferindo uma resposta) · **Respondido** · Com a área ({área}) · Concluído. A resposta sai com o selo "Resposta pelo histórico de casos, conferida pela Save" ou "Resposta da área {área}".
- **Prazo:** "Retorno previsto da Save: até {data hora}" só quando o SLA do tipo existir; nunca prazo de resultado do cliente.
- **Vazio:** "Você ainda não fez pedidos por aqui. Andamento, documento e contrato costumam ter resposta rápida." [Novo pedido]
- **Mobile:** a conversa em tela cheia, com o campo de resposta fixo embaixo; "Novo pedido" abre a partir da barra.

### P-7 Extrato
- **Objetivo:** "onde está minha remuneração", sem confundir previsto com devido.
- **Topo:** faixa `.prm-extrato__resumo` com **Pago no ano** · **Liberado, aguardando sua NF** · **Em conferência** (contagem de linhas, sem soma de "previsto").
- **Lista:** um cartão por linha: empresa, chip de estado (Previsto · Recebido pela Save · Liberado · Pago · Em conferência contratual), valor líquido só a partir de "Recebido pela Save", linha do tempo `.prm-tempo--horizontal` (vertical no celular) e a ação do estado: [Enviar NF] em Liberado, [Contestar] a partir de Recebido, por 10 dias corridos, com o prazo visível.
- **Detalhe da linha (P-7a):** `.prm-dl` com base (honorário recebido pela Save), percentual do seu termo, bruto, cada retenção com nome por extenso ("Imposto de Renda retido (IRRF)"), líquido e NF. Ajuda "?" em cada termo.
- **Texto fixo de leitura:** "Previsto quer dizer contrato assinado, ainda sem pagamento do cliente. A remuneração só é calculada depois que a Save recebe o honorário." "Em conferência contratual: o time da Save está conferindo esta linha com o contrato. Avisamos aqui quando terminar."
- **Até existir a fonte de recebimentos (Fase 2):** o extrato mostra só Previsto e Em conferência, com o aviso `.prm-aviso--info`: "Os valores aparecem conforme os recebimentos forem confirmados pelo Financeiro da Save."
- **Vazio:** "Ainda não há linhas no seu extrato. Elas aparecem quando um contrato de empresa indicada por você é assinado."
- **Sem permissão:** o consultor que não é titular vê só as linhas dele, se o termo do escritório permitir; senão, "O extrato do escritório fica com o titular."
- **Mobile:** cartões empilhados; valores em Mono 24 px; ações em largura total.

### P-8 Caixa de avisos
- **Objetivo:** um lugar para tudo o que mudou, que leva ao item.
- **Desktop:** gaveta à direita (`.prm-gaveta`), aberta pelo sino. **Celular:** tela cheia.
- **Filtros:** Todos · Pede você · Respostas · Empresas · Extrato · Programa. Grupos: Hoje · Esta semana · Antes.
- **Item:** ponto de "não lido" (ouro com contorno), título, 1 linha de apoio e hora em Mono. O toque marca como lido e abre o destino. No rodapé, [Marcar todos como lidos] e [Preferências].
- **Preferências:** resumo por e-mail (Desligado · Diário · Semanal; o padrão é desligado). Aviso imediato por e-mail só para "Pede você".
- **Vazio:** "Nenhum aviso por enquanto."

### P-9 Nível e jornada
- **Objetivo:** mostrar o nível, o caminho até o próximo e os benefícios, sem ranking.
- **Conteúdo:** selo do nível (`.prm-nivel__selo`), barra `.prm-nivel` ("{n}% do caminho até {próximo nível}, pela soma dos últimos 12 meses"), benefícios do nível atual e do próximo, passos da jornada (`.prm-passos`) e a próxima apuração.
- **Enquanto o F8 não for decidido:** selo com o texto "Em teste" e aviso: "O programa de níveis está em definição. O que você vê aqui é uma simulação e pode mudar." Sem patamar em R$ até a D75.
- **Titular:** "Sua equipe" mostra cada consultor só com a etapa da jornada, sem atividade nem dias sem indicar (P2-9).
- **Nunca:** ranking, posição entre parceiros, comparação com outro escritório.

### P-10 Biblioteca e Academia
- **Objetivo:** achar o kit certo para a conversa com o cliente.
- **Conteúdo:** filtro por produto pronto e por tese; cartão do kit (o que é, para quem serve, perguntas de qualificação, o que não dizer, peça co-branded); Academia (N1, N2, certificação como porta de produto).
- **Produto em validação:** cartão com selo "Em descoberta" e o texto "Produto em estudo pela Save. Ainda não há material, condição nem simulação. Se o cliente perguntar, registre o interesse." [Registrar interesse], que abre um pedido do tipo Outro.
- **Peça co-branded:** antes do download, o aviso "A peça identifica que você é parceiro remunerado da Save (CONAR)." O botão baixa o arquivo; não há envio pelo portal.

### P-11 Perfil, equipe e ajuda
- **Perfil:** nome, e-mail (do Entra, sem edição), telefone da empresa, preferências de aviso, termos aceitos com data. Sem dado bancário: esse dado é do Financeiro.
- **Equipe (titular):** lista de consultores e [Pedir acesso para um consultor], que abre um pedido à Save. O titular não convida sozinho, porque o convite B2B é da TI e da Save.
- **Ajuda:** glossário da seção 6, "Como funciona o registro", "Como ler o extrato" e o contato do time que atende o parceiro.

### Visão da Save (seção Canal do painel, modo escuro)

Estados comuns: os do painel (`portal/`). **Sem permissão:** "Esta tela é do papel {papel}. Peça acesso ao Luis." Toda ação irreversível pede confirmação em modal; toda ação reversível mostra o toast "Desfazer" por 8 s.

| Tela | Objetivo | Conteúdo e componentes | Vazio / erro | Celular |
|---|---|---|---|---|
| **S-1 Visão do canal** | Ver a saúde do canal e as filas de ação | Faixa de 8 KPIs (`.prm-grade--kpi`) que levam à fila correspondente; tabela "Saúde por parceiro" com saúde 0–100, leitura em texto e ação sugerida; concentração (barras com rótulo); alertas: varredura (acertos acima do teto), registros a vencer, demandas fora do SLA | Fonte do dia atrasada: aviso com a data da última cópia | KPIs 2×2; a tabela vira lista |
| **S-2 Parceiros → S-2a Ficha 360** | Tudo de um parceiro numa página | Abas Resumo · Empresas · Registros · Extrato · Pedidos · Nível · Acessos · Consultas. O Resumo traz o mesmo "Pede você" que o parceiro vê ("Ver como o parceiro") | — | Abas roláveis |
| **S-3 Registros → S-3a** | Decidir cada registro com os fatos | Fila por ordem de chegada; chip da checagem (Livre · Já é do parceiro · Outro canal · Cliente da Save · Índice indisponível), visível só aqui; histórico da raiz (1º registro, canais, ganhos, teses); ações **Aprovar** (modal: "Aprovar o registro {id}? A proteção vale até {data}. O card no HubSpot continua pelo fluxo atual."), **Não aprovar** (motivo de uma lista, com o texto que o parceiro vai ver) e **Enviar a conflito** | "Nenhum registro esperando decisão." | Cartões; as ações ficam em folha inferior |
| **S-4 Conflitos** | Levar o conflito ao Luis com os fatos | Linha do tempo da raiz, partes, regra aplicável (R14–R16), severidade com texto; só o perfil Luis vê "Registrar decisão" | "Nenhum conflito aberto." | Lista |
| **S-5 Demandas** | Fila única por SLA (portal + WhatsApp) | Tabela: pedido, parceiro, tipo, origem, aberta há, SLA (chip com texto "No prazo · 8 h" ou "Fora do prazo · 24 h"), caminho; painel lateral com a sugestão do histórico ou a pré-análise da área; "Aprovar e enviar", "Editar", "Abrir chamado (rascunho)" | "Nenhuma demanda aberta." | A tabela vira lista; o painel vira tela |
| **S-6 Dossiês e esteira** | Publicar dossiê auditado | Fila com estado (Em preparo · Com alerta · Aguardando aprovação · Publicado), resultado do auditor por trecho, "Aprovar e publicar" ou "Manter versão-base" | — | Lista |
| **S-7 Extratos → S-7a Contestações** | Liberar só o recebido e conferido | Lote por parceiro com checklist (termo, CNPJ, NF, retenções, sem bloqueio, conflito resolvido), cada item com chip de texto; "Liberar lote" desabilitado com o motivo escrito ao lado (não só em `title`); contestações com prazo de 5 d.u. | "Nenhum lote neste mês." | Cartões |
| **S-8 Níveis** | Simular e preparar cartas | Tabela por parceiro: nível atual, simulado, distância, risco; "Gerar carta" (rascunho Word do DS) | — | Lista |
| **S-9 Biblioteca** | Governar o catálogo | Produto, dono, estado (Pronto · Em descoberta · Fora da vitrine), auditado em, uso por parceiro | — | Lista |
| **S-10 Acessos e convites** | Controlar quem entra | Usuários por parceiro, papel (titular, consultor), último acesso, convite (Enviado · Aceito · Expirado), "Reenviar convite" e "Suspender acesso" (modal) | — | Lista |

---

## 4. Biblioteca de componentes do PRM

Arquivo: `docs/prm/v2/prm-componentes.css`. Carrega depois do `save.css`. Prefixo `prm-`. O parceiro usa o `:root` (claro); a Save usa `.escuro`. **Nenhuma cor escrita à mão:** os tokens `--prm-*` são apelidos de papel sobre os do `save.css` (conferido por busca: zero hexadecimais e zero `rgba`, e cada `var()` existe no `save.css`).

### 4.1 Tokens de papel
| Token | Claro | Escuro | Para quê |
|---|---|---|---|
| `--prm-acao` / `--prm-sobre-ouro` | `--ouro` / `--texto` | `--ouro` / `--fundo` | botão principal, chip "pede você", contador |
| `--prm-campo-borda` | `--texto-3` (3,56:1) | `--borda-3` | contorno de campo, botão secundário |
| `--prm-texto-apoio` | `--texto-2` | `--texto-2` | todo texto de apoio |
| `--prm-texto-mudo` | `--texto-3` | `--texto-2` | desabilitado |
| `--prm-ok`, `--prm-atencao`, `--prm-erro`, `--prm-info` | funcionais | funcionais | só ponto, borda e ícone (exceto erro e info no claro) |
| `--prm-veu` | `--texto` a 48% | `--fundo` a 72% | fundo atrás de gaveta e modal (`color-mix`) |
| `--prm-nav-m`, `--prm-toque`, `--prm-toque-primario` | 56 / 44 / 48 px | idem | barra inferior e áreas de toque |

### 4.2 Catálogo
| Componente | Classes | Anatomia e regras | Acessibilidade |
|---|---|---|---|
| Casca | `.prm-casca`, `.prm-topo`, `.prm-menu`, `.prm-menu__item`, `.prm-main`, `.prm-nav-m`, `.prm-nav-m__item`, `.prm-nav-m__acao`, `.prm-pular` | Topo com faixa ouro de 3 px (sombra interna), menu lateral ≥ 768 px, barra inferior < 768 px com Registrar no centro | `nav` com `aria-label`; item ativo com `aria-current="page"`; "Pular para o conteúdo" |
| Contador | `.prm-contador` | Mono 11 px sobre ouro; acima de 99 vira "99+" | O número vai no nome acessível do link ("Empresas, 2 pedem você") |
| Botões | `.prm-btn`, `--sec`, `--perigo`, `--texto`, `--bloco`, `[aria-busy]`, `.prm-acoes--empilha` | Um botão principal por área; o de perigo nunca é o principal | `aria-disabled` com motivo escrito ao lado; `aria-busy` durante envio |
| Cartão e KPI | `.prm-cartao`, `--acao`, `--clicavel`, `.prm-kpi`, `.prm-grade--kpi` | KPI: rótulo + valor Mono + apoio; sempre com base ("de 8 indicadas") | Cartão clicável é `<a>`, não `div` com clique |
| Lista | `.prm-lista`, `__item`, `__link`, `__titulo`, `__apoio` | Linha tocável de 56 px no celular | Uma ação por linha; a linha inteira é o link |
| Chips de estado | `.prm-chip` + `--ok`, `--atencao`, `--erro`, `--info`, `--neutro`, `--acao`, `--suave` | Texto sempre em `--texto`; forma do ponto por estado | Cor nunca sozinha (1.4.1) |
| Selo | `.prm-selo` | Produto, nível, "Em teste", "Em descoberta" | — |
| Linha do tempo | `.prm-tempo`, `__passo[data-estado]`, `__titulo`, `__quando`, `__bola`, `--horizontal` | Vertical no celular e na ficha; horizontal no extrato desktop | `<ol>`, passo atual com `aria-current="step"`; estado também em texto ("concluído", "atual") |
| Extrato | `.prm-extrato__linha`, `__cab`, `__valor`, `__sem-valor`, `__resumo`, `.prm-dl` | Valor só depois de "Recebido pela Save"; retenções por extenso | `<dl>`; valor com moeda por extenso no nome acessível |
| Barra de nível | `.prm-nivel`, `__trilho`, `__barra` (`--prm-progresso`), `__marcos`, `__texto`, `__selo`, `__medalha`; `.prm-passos` | Borda escura no fim da barra, para ler em cinza | `role="progressbar"` + `aria-valuetext` |
| Formulário | `.prm-form`, `.prm-campo[data-estado]`, `__rotulo`, `__opcional`, `__dica`, `__entrada`, `--mono`, `__msg`, `.prm-campos`, `.prm-empresa`, `.prm-resultado--*`, `.prm-form__rodape` | Rótulo acima do campo; "(opcional)" escrito; mensagem logo abaixo do campo | `aria-describedby` (dica + mensagem), `aria-invalid`, mensagem com `aria-live="polite"`; foco no 1º campo com erro |
| Avisos em linha | `.prm-aviso` + `--info`, `--atencao`, `--erro`, `--marca` | Ícone + texto; borda esquerda funcional | Erro com `role="alert"`; o resto sem papel vivo |
| Vazio, esqueleto | `.prm-vazio`, `.prm-esqueleto--*` | Vazio diz o que é e o próximo passo | Esqueleto com `aria-hidden` e a região com `aria-busy="true"` |
| Toast | `.prm-toasts`, `.prm-toast` + `--ok`, `--info`, `--atencao`, `__titulo`, `__acao` | 1 por vez, 5 s (8 s com "Desfazer"); pausa com o mouse em cima ou com foco; no celular, acima da barra | Região `role="status"`. Erro que pede ação não vai em toast |
| Caixa de avisos | `.prm-veu`, `.prm-gaveta`, `__cab`, `__corpo`, `__rodape`, `.prm-filtros`, `.prm-filtro[aria-pressed]`, `.prm-aviso-item[data-lido]`, `.prm-aviso-grupo` | Gaveta de 440 px; tela cheia no celular | `role="dialog"` + `aria-modal`, foco preso, Esc fecha, foco volta ao sino |
| Modal | `.prm-modal` | Título que diz o efeito; botões "Cancelar" e "{Verbo do efeito}"; folha inferior no celular | Foco preso; Esc cancela |
| Tabela densa (Save) | `.prm-tabela`, `--vira-lista`, `.prm-so-celular`, `.prm-so-desktop`, `.prm-barra-filtro` | `<caption>` sempre; números em Mono à direita | `aria-sort` nas colunas ordenáveis |

### 4.3 Estados e chips padronizados
| Objeto | Estado (texto exato) | Chip |
|---|---|---|
| Registro (parceiro) | Recebido · em análise | `--neutro` |
| | Aprovado · válido até {data} | `--ok` |
| | Vence em {n} dias | `--atencao` |
| | Não aprovado | `--neutro` |
| | Expirado | `--neutro` |
| | Virou negócio | `--ok` |
| Empresa (7 estados) | Recebido · Em diagnóstico · Apresentação marcada · Contrato em andamento · Em execução | `--info` (padrão) |
| | **Precisa de você** | `--acao` (o único em ouro) |
| | Encerrado | `--neutro` |
| Extrato | Previsto · Recebido pela Save | `--info` |
| | Liberado · envie a NF | `--acao` |
| | Pago | `--ok` |
| | Em conferência contratual | `--atencao` |
| Pedido | Recebido · Em preparo · Com a área | `--info` |
| | Respondido | `--acao` enquanto não for lido; `--ok` depois |
| | Concluído | `--ok` |
| SLA (Save) | No prazo · {h} h | `--ok` |
| | Perto do prazo · {h} h | `--atencao` |
| | Fora do prazo · {h} h | `--erro` |

### 4.4 Ícones
Lucide (recomendação do DS), SVG embutido, traço de 1,75, 20 a 24 px, `aria-hidden="true"` quando há texto ao lado. Sem emoji.

---

## 5. Onboarding do primeiro acesso e convite

### 5.1 Fluxo
1. **Convite** por e-mail (o B2B do Entra envia o link de resgate) mais uma mensagem de WhatsApp enviada **por uma pessoa do time da Save**, nunca por disparo automático.
2. **Entrar com a Microsoft.** O parceiro aceita o convite e configura o MFA por aplicativo. A tela da Save antes do redirecionamento diz: "Você vai para a página da Microsoft para confirmar seu e-mail. Isso protege os dados das empresas que você indica."
3. **Boas-vindas (P-0),** uma tela só, sem carrossel:
   - "Bem-vindo ao portal de parceiros da Save, {nome}."
   - Três blocos com ícone: **Registre** ("Registre a empresa antes de começar a conversa. A data e a hora ficam guardadas.") · **Acompanhe** ("Veja em que etapa está cada empresa e o que falta de você.") · **Peça** ("Pergunte à Save por aqui; a resposta fica guardada junto da empresa.").
   - **Aceite dos termos de uso e do aviso de privacidade** (link para o texto completo e caixa de seleção). *[Textos do Jurídico, com a linguagem de "remuneração por indicação comercial e por serviços de apoio" (R13).]*
   - [Começar].
4. **Primeiros passos** no Início, num cartão com uma lista de 4 itens que se marca sozinha e some quando estiver completa ou quando o parceiro clicar em "Dispensar":
   - Confirmar o telefone da empresa no perfil
   - Registrar a primeira empresa
   - Abrir a ficha de uma empresa indicada (se já houver)
   - Conhecer o kit da tese mais comum na sua carteira
5. **Empresas que já existem:** se o parceiro já tem negócios no HubSpot, eles aparecem em Empresas desde o primeiro acesso, com o aviso "Trouxemos as empresas que você já indicou à Save."
6. **Lembrete:** se o convite não for aceito em 5 dias úteis, a S-10 sinaliza ao time, que decide se reenvia. Não há lembrete automático ao parceiro.

### 5.2 E-mail de convite (texto)
> **Assunto:** Seu acesso ao portal de parceiros da Save
>
> Olá, {nome},
>
> Você foi convidado para o portal de parceiros da Save Co. Por ele, você registra as empresas que pretende indicar, acompanha a etapa de cada uma e fala com o nosso time sem depender do WhatsApp.
>
> **Para entrar:**
> 1. Clique em "Aceitar convite" no e-mail da Microsoft que chega junto com este.
> 2. Confirme seu e-mail e configure o aplicativo de autenticação.
> 3. Pronto: o portal abre na página inicial.
>
> O acesso é pessoal. Cada pessoa do seu escritório recebe o próprio convite.
>
> Dúvidas sobre o acesso: responda a este e-mail ou fale com {nome do responsável na Save}.
>
> Time de Parceiros · Save Co.
>
> *Você recebeu este e-mail porque tem uma relação de parceria com a Save Co. Tratamos seus dados conforme o aviso de privacidade do portal.*

(Layout pelo `skills/depto-marketing/scripts/email_layout.py`: modo claro, logo de fundo claro, botão em ouro com texto escuro.)

### 5.3 WhatsApp de convite (enviado por uma pessoa do time)
> {Nome}, aqui é {pessoa} da Save. Liberamos seu acesso ao portal de parceiros. Por ele você registra empresas, acompanha a etapa de cada uma e faz pedidos à Save. O convite chegou no seu e-mail {e-mail}, com o remetente da Microsoft. Se não aparecer, olhe o lixo eletrônico ou me avise por aqui.

### 5.4 Mensagem de primeiro registro aprovado (aviso no portal e e-mail)
> **Registro aprovado · {empresa}.** A indicação fica registrada em seu nome até {data}. Quando houver conversa com a empresa, a etapa aparece em Empresas.

---

## 6. Glossário de microcopy (fonte única dos textos)

| Em vez de | Use | Por quê |
|---|---|---|
| Central Masters / Área Partners (para o parceiro) | "o time da Save que atende você" ou o nome da pessoa | O parceiro não conhece a estrutura interna |
| Raiz do CNPJ (8 primeiros caracteres) | "a empresa toda (matriz e filiais)" | Jargão |
| Carimbo de hora | "data e hora do registro" | Jargão |
| Leitura-sombra | "em teste até a decisão do programa" | Jargão |
| Volume ativo dos últimos 12 meses | "a soma dos últimos 12 meses" + ajuda "?" com a regra | Jargão |
| CSRF | "Contribuições retidas (PIS, COFINS e CSLL)" | Sigla |
| Comissão / divisão de honorários | "remuneração por indicação" | R13 e risco de requalificação *[Jurídico valida]* |
| Exclusividade / território | "proteção temporária da indicação" | R16 |
| Você vai receber R$ X / em X dias | (não existe) | Regra da casa: sem valor, prazo ou êxito |
| Agente / IA respondeu | "Resposta da Save" | DS: IA executiva, não chatbot |
| Em análise pela Área Partners (registro) | "Registro recebido · em análise" | P0-1 e P0-2 |
| Erro! / Ops! | "Não conseguimos {ação} agora. {O que fazer}." | Tom sóbrio |

**Frases neutras fixas (não variar):**
- Consulta indisponível ou bloqueada: "Não foi possível seguir com esta consulta. Fale com a Área Partners." (texto atual do `central/`; o Jurídico pode propor trocar "Área Partners" por "o time da Save que atende você" nas duas telas de uma vez)
- Registro enviado: "Registro recebido · em análise."
- Não aprovado: "Este registro não foi aprovado. Se quiser entender, fale com o time da Save que atende você." (motivo detalhado só pela pessoa)

---

## 7. Entrega em 3 blocos

**1. O que você pediu**
- Avaliação crítica do protótipo com 28 problemas priorizados (5 P0, 11 P1, 9 P2, 3 P3), mais 2 achados para o dono do DS, tabela de contraste medida e os acertos que ficam.
- Arquitetura de informação do parceiro (barra inferior com Registrar, Empresas e Pedidos a 1 toque), da Save (seção Canal dentro do `portal/`) e o encaixe dos 5 módulos da Central.
- Especificação de 11 telas do parceiro e 10 da Save, com estados, microcopy e comportamento no celular.
- Biblioteca de componentes em `docs/prm/v2/prm-componentes.css` (claro e escuro, só tokens do DS), com o catálogo e os estados padronizados.
- Onboarding do primeiro acesso, e-mail e WhatsApp de convite e aviso de primeiro registro aprovado.

**2. O que você também precisa**
- **P0-1 é decisão de produto, não só de tela:** unificar a resposta do registro muda o que o parceiro sabe na hora. A proposta mantém o "já é seu" (dado do próprio parceiro) e adia todo o resto para a decisão humana. Vale levar ao gerente e ao Luis junto com a regra R1–R3.
- **Contraste do ouro de texto (A-1):** o handoff do Marketing traz um número que não confere. O PRM contorna o problema; quem corrige a origem é o Marketing.
- O protótipo atual precisa de uma rodada de ajuste antes de ser mostrado a Masters: os P0 e o P1-3 (tirar o tema e o perfil do topo).
- O microcopy deste documento passou pelo auditor de promessas (registro abaixo). Os textos de termos, privacidade e declaração do registro são do Jurídico.

**3. O que falta e quem fornece**
| Falta | Quem |
|---|---|
| Validade do registro (prazo no texto do Início e do resultado) | Luis (R1–R3) |
| Termos de uso, aviso de privacidade, declaração do registro e linguagem de remuneração | Jurídico |
| Token `ouro-texto` de corpo e `texto-3` escuro no DS v0.6 | Marketing (dono do DS) |
| Lista de motivos de "não aprovado" e de "encerrado" em linguagem do parceiro | Operações de Canal com a Daniela |
| Tipos de pedido com SLA visível ao parceiro (`sla.json`) | Central Masters (Daniela) |
| Redirect e textos da página de convite do Entra (marca da Save na tela da Microsoft) | TI da Save |
| Teste de usabilidade com 3 a 5 consultores de 2 Masters no celular, antes do piloto | Partner Success, com o Design/UX |

**Decisões pendentes do Luis tocadas aqui:** validade do registro (R1–R3); o que o parceiro vê do negócio (item 6 do desenho, mantido); F8 (nível "em teste").

---

**Registro `revisao`:** autor Design/UX (especialista DS Save v0.5) · revisão própria contra WCAG 2.2 AA, Nielsen e DS v0.5 · contraste recalculado no navegador em 26/10/2026 · CSS conferido (0 cores à mão; todas as variáveis existem no `save.css`) · auditor de promessas rodado sobre este arquivo (resultado na resposta ao gerente) · pendente: revisão do gerente do PRM, do Jurídico (textos marcados) e de Operações de Canal (estados e motivos).
