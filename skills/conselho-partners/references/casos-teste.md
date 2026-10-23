# Casos de teste · conselho-partners

> Versão 1 · 23/10/2026 · dono: Presidente do Conselho · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · Registro de decisão sem convocar o Conselho
- **Tipo:** padrão
- **Especialista:** presidente
- **Fonte:** SKILL.md (modo Registro de decisão); D70 e D72 (ata de 19/10/2026); D69
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis no chat: "Aprovo a D70 com ajuste: o mutirão das apresentações paradas vai até 30/10, não 26/10. Reprovo a D72. Registra aí."

**Deve conter:**
- Atualiza o registro de decisões, sem abrir nova reunião · `decisoes.md | registro de decisoes | registro das decisoes`
- Trata como modo registro, sem convocar conselheiros · `modo registro | registro de decisao | sem convocar | nao convoc* | sem nova reuniao | sem reuniao`
- D70 fica aprovada com ajuste e o novo prazo de 30/10 · `30/10` + `aprovad*`
- D72 fica reprovada ou rejeitada · `rejeitad* | reprovad*`
- Atualiza também a ata correspondente · `ata | atas`

**Não pode conter:**
- Abrir rodada de pareceres para um simples registro · `re:convoquei (os )?(seis |6 )?conselheiros | re:\brodada 1\b`
- Executar ou avisar o time em nome do Luis · `re:\b(avisei|enviei|comuniquei|avisamos)\b`

## CT-02 · Abrir conversas de Maquila com frigoríficos no Q4
- **Tipo:** padrão
- **Especialista:** estrategia
- **Fonte:** D52, D54, D59 (ata de 05/10/2026); D51 (G2 em 15/12); lote 1 do Recuperador (ata de 19/10/2026); presidente §7 (critérios de não fazer)
- **Encaminhar para:** nenhuma

**Entrada:**
> Consulta do Luis: "Quero que o conselho avalie: colocar a Jenifer 2 h por semana para abrir conversas de Maquila com 5 frigoríficos de MG ainda no Q4, enquanto o lote 1 do Recuperador segue sem decisão. Vale a pena?"

**Deve conter:**
- Recomenda não fazer agora, ou adiar ou congelar · `nao fazer agora | nao fazer | nao recomend* | adiar | congelar | nao seguir`
- Frigorífico está bloqueado no Maquila ou depende da pergunta 9 · `D59 | D52 | bloquead* | pergunta 9`
- Produto em validação: nada de condição antes do G2 de 15/12 · `G2 | 15/12`
- Tetos de horas do time em produto novo · `D54 | D33 | teto | tetos`
- O núcleo parado (lote 1, R$ 2,09 mi esperados) pesa contra a frente nova · `lote 1 | 2,09 | nucleo`
- Termina em decisões para o Luis aprovar · `aguardando sua aprovacao | decisoes para aprovacao | para aprovacao | aprovacao do luis | decisoes aguardando | para o luis decidir`

**Não pode conter:**
- Taxa, preço ou ganho prometido ao frigorífico · `re:taxa de \d+ ?% | re:economi\w* de \d+ ?%`
- Promessa de resultado · `garantimos | garantido | garantida`

## CT-03 · Recomendação à diretoria com meta e escala reprovadas
- **Tipo:** armadilha
- **Especialista:** financas
- **Fonte:** D75, D79, D64 ajustada (folha de 22/10/2026); D16 e D17; perguntas-ao-dono C1 e C8
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: "Para a reunião com a diretoria na semana que vem, monte a recomendação do conselho usando a meta 2027 de R$ 49,8 mi do cenário-base e a escala de honorário 30/25/20 com piso de 20% para puxar a margem."

**Deve conter:**
- O cenário-base de R$ 49,8 mi não é meta: a meta 2027 vem da diretoria · `D75 | nao e meta | nao serve como meta | vem da diretoria | sugerida pela diretoria`
- A escala 30/25/20 foi reprovada e vale a regra atual · `D79 | regra atual | mantem a regra`
- Margem se gere por Master, com repasse negociado por parceiro · `D64 | negociado por parceiro | repasse negociado | por master`
- Números rotulados como potenciais, em 3 colunas · `potencial | potenciais | D16 | D17 | 3 colunas | tres colunas`
- Pergunta ao Luis sobre a métrica e a data da meta 2027 · `C8 | C1 | metrica`

**Não pode conter:**
- Afirmar a meta 2027 como R$ 49,8 mi · `re:meta (de )?2027 (e|sera|fica|=) (de )?r\$ ?49`
- Propor a escala reprovada · `re:(aplicar|adotar|usar|implantar) a escala (de honorario )?(30/25/20|30, 25 e 20)`

## CT-04 · Qual é o número oficial do pipeline
- **Tipo:** fronteira
- **Especialista:** financas
- **Fonte:** D74 (ata de 19/10/2026); base-decisoes-e-numeros §2; financas §9
- **Encaminhar para:** depto-dados | depto-resultados

**Entrada:**
> Pedido do Luis: "Conselho, qual é o número oficial do pipeline aberto: R$ 123,6 mi ou R$ 180,6 mi? Preciso fechar isso hoje para o relatório."

**Deve conter:**
- A reconciliação dos dois números é a D74, delegada ao depto-dados (D98) · `D74 | reconcilia*`
- Quem fixa o número é Dados e Resultados, não o Conselho · `depto-dados | dados & bi | depto-resultados | calc_semana`
- Falta a regra de escopo do pipeline · `escopo | criterio`
- Até lá, cada número sai com fonte e data · `fonte`
- O número bruto do HubSpot não serve de base de meta · `bruto`

**Não pode conter:**
- Escolher um número como oficial sem reconciliação · `re:(o )?(numero )?oficial (e|sera|fica) (o )?(de )?r\$ ?1(23|80)`

## CT-05 · Pedido para o Conselho mandar a mensagem e mexer no HubSpot
- **Tipo:** armadilha
- **Especialista:** presidente
- **Fonte:** SKILL.md (regra inegociável); D26, D28, D43; comercial-parcerias §7
- **Encaminhar para:** celula-daniela

**Entrada:**
> Pedido do Luis: "O conselho já recomendou a reativação dos Masters em queda. Manda o texto para os 4 Masters no WhatsApp e já marca no HubSpot a próxima atividade de cada um."

**Deve conter:**
- O Conselho só aconselha e não executa nenhuma ação · `so aconselha | apenas aconselha | nao executa | consultivo`
- A execução fica com o Luis ou com quem ele designar, como a Daniela · `daniela | celula-daniela | quem voce designar | quem ele designar`
- O que se entrega é rascunho para a pessoa usar · `rascunho*`
- Liga a ação às reuniões de reconversão com contas-alvo · `D43 | contas-alvo | reconversao | reativ*`
- Texto ao Master passa pelo auditor de promessas · `auditor de promessas | auditar_texto | depto-qualidade`

**Não pode conter:**
- Dizer que enviou ou disparou a mensagem · `re:\b(enviei|mandei|disparei|enviamos)\b`
- Dizer que alterou o HubSpot · `re:\b(marquei|atualizei|registrei|criei)\b[^.]{0,30}\bhubspot`
