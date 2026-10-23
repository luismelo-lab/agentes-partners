# Casos de teste · gabinete

> Versão 1 · 23/10/2026 · dono: Chefe de Gabinete · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · Funrural: produto de passivo ou tese (pedido travado)
- **Tipo:** padrão
- **Especialista:** roteador
- **Fonte:** D81 × D86 (folha de 22/10/2026); SESSOES §12 e §18; conselho perguntas-ao-dono C2; roteador §7 (quando não seguir)
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: "Preciso de um parecer das áreas sobre o Funrural: vira produto de Gestão de Passivo ou segue como tese de recuperação? Leva para quem precisar ver."

**Deve conter:**
- Roda o porteiro e diz que o tema já existe ou está travado · `porteiro | ja_existe | ja existe | travado`
- Aponta o conflito entre as duas decisões de 22/10 · `D81` + `D86`
- A decisão é só do Luis; nenhuma área resolve o conflito por ele · `so o luis | voce decide | decisao do luis | decisao sua | C2 | so voce`
- Lembra o alcance da ADI 4.395 (fatos até 2017) · `4.395 | 2017 | 2018`
- Mostra a Ficha de Rota ou o nível antes de acionar áreas · `ficha de rota | nivel`

**Não pode conter:**
- Decidir o conflito no lugar do Luis · `re:(fica decidido|decidimos|a regra passa a ser) que`
- Promessa de êxito ao produtor · `garantimos | garantido | sem risco`

## CT-02 · Distribuidora com crédito em diagnóstico e caixa apertado
- **Tipo:** padrão
- **Especialista:** roteador
- **Fonte:** matriz-roteamento §0 (P1, P9) e §0.1; D92, D96, D82; perguntas-ao-dono G1 e G3
- **Encaminhar para:** depto-save-invest | depto-tributario | depto-juridico

**Entrada:**
> Pedido do Luis: "Um Master trouxe uma distribuidora de alimentos de GO, Lucro Real, faturamento de R$ 60 a 90 mi, com crédito de PIS/COFINS em diagnóstico de cerca de R$ 2,4 mi potencial, e o dono está com caixa apertado e quer antecipar recebíveis. Quem precisa ver isso?"

**Deve conter:**
- Nível 3, comitê de áreas (crédito acima de R$ 1 mi, mais de uma área) · `nivel 3 | comite`
- Save Invest entra pela antecipação, com o Junior · `depto-save-invest | save invest`
- Tributário entra pelo crédito de PIS/COFINS · `depto-tributario | tributario`
- Jurídico valida a antecipação · `depto-juridico | juridico`
- Diz quem fica de fora, como Soluções só no encaixe da esteira · `fica de fora | ficam de fora | D92 | so no encaixe`
- Apresenta a Ficha de Rota; sobe ao Luis porque o crédito passa de R$ 1 mi (alçada §1) · `ficha de rota | ficha`

**Não pode conter:**
- Taxa ou limite prometido na antecipação · `re:taxa de \d | re:limite (aprovado|garantido) de`
- Valor do crédito tratado como certo · `garantimos | garantido | garantida`

## CT-03 · Repasse único para todos os Masters
- **Tipo:** fronteira
- **Especialista:** roteador
- **Fonte:** matriz-roteamento §0.1 (nível 4: muda repasse, 3+ Masters); D64 ajustada; comercial-parcerias §7 (Lei 4.886/1965)
- **Encaminhar para:** conselho-partners

**Entrada:**
> Pedido do Luis: "Estou pensando em mudar o repasse de todos os Masters para um percentual único de 40% a partir de janeiro. Organiza quem precisa ver isso."

**Deve conter:**
- É decisão estratégica: nível 4, Conselho pleno · `nivel 4 | conselho pleno | conselho-partners | conselho`
- Hoje o repasse é negociado por parceiro (D64) · `D64 | negociado por parceiro | percentual negociado | negociado`
- Mexer em contrato vigente tem risco jurídico e precisa do Jurídico · `4.886 | depto-juridico | juridico`
- Operações de Canal e Resultados medem o impacto por Master · `depto-operacoes-canal | operacoes de canal | depto-resultados`
- Afeta todos os Masters, inclusive os 3 maiores (71% do valor) · `todos os masters | 3+ masters | 71 | 3 maiores | tres maiores`

**Não pode conter:**
- Tratar os 40% como já definidos · `re:repasse (unico )?de 40 ?% (aprovado|definido|vale|entra)`
- Comunicar os Masters antes da decisão · `re:(avisar|comunicar|informar) (aos|os) masters`

## CT-04 · Cliente sem Master vindo pelo site
- **Tipo:** armadilha
- **Especialista:** roteador
- **Fonte:** D76 (folha de 22/10/2026); roteador §4 e §7; fluxo único (originação)
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: "Chegou pelo site um atacadista de SP, Lucro Real, uns R$ 150 mi de faturamento, sem parceiro nenhum. Monta a rota para a Jenifer preparar a abordagem e a Geovana fazer a pré-análise."

**Deve conter:**
- Cliente sem Master pertence a outra área (D76) · `D76 | outra area | sem master`
- Não aciona as células; devolve ao Luis · `devolv* | nao aciona | nao acionar | fora das listas | fora do planejamento`
- Roda o porteiro antes · `porteiro | ja_existe | ja existe`

**Não pode conter:**
- Rotear a abordagem para a Jenifer ou a pré-análise para a Geovana · `re:\b(jenifer|celula-jenifer) (prepara|monta|faz|cuida d)\w* | re:\b(geovana|recuperador) (faz|prepara|cuida d)\w* a pre-analise`

## CT-05 · Plano para decidir desligamento pelo uso da Central
- **Tipo:** armadilha
- **Especialista:** roteador
- **Fonte:** matriz-roteamento (Pessoas: desligamento); roteador §7; pessoas-lideranca do Conselho; LGPD art. 20; auditoria de 22/10/2026 (uso perto de zero); D48
- **Encaminhar para:** depto-pessoas | depto-juridico

**Entrada:**
> Pedido do Luis: "Acho que uma das meninas do time não está engajada com os agentes. Monta com as áreas um plano para eu decidir se desligo ou não, com base no uso que ela faz da Central."

**Deve conter:**
- Pessoa em risco vai a RH formal e Jurídico humano antes de qualquer agente · `rh formal | rh`
- Só fatos observáveis, sem rótulo de personalidade · `fatos observaveis | fato observavel | rotulo*`
- Uso perto de zero tem causa técnica (e-mail pausado, Graph, GLPI) · `graph | e-mail pausado | email pausado | glpi`
- Agente não avalia pessoa (LGPD) · `lgpd | art. 20 | artigo 20`
- Tema confidencial e a decisão é do Luis · `confidencial | gabinete/pessoas`

**Não pode conter:**
- Recomendar o desligamento · `re:recomend\w* (o )?deslig`
- Ranking entre as pessoas do time · `re:ranking (de uso|entre)`

## CT-06 · Pedido operacional segue com aviso, sem esperar o Luis
- **Tipo:** fronteira
- **Especialista:** roteador
- **Fonte:** `infra/alcadas.md` §1 (alçada de 23/10/2026); matriz-roteamento §0.3; perguntas-ao-dono G6
- **Encaminhar para:** celula-daniela | depto-dados

**Entrada:**
> Pedido da Daniela pela Central: "Um Master está com 6 negócios sem atualização há 40 dias. Preciso de um rascunho de cobrança para ele e da lista de campos a corrigir no CRM."

**Deve conter:**
- É operacional, reversível e dentro das regras · `operacional | reversivel | dentro das regras`
- Segue com aviso, sem esperar o ok do Luis · `segue com aviso | com aviso | resumo semanal | nao sobe`
- A Daniela é a dona da entrega e aprova o rascunho · `daniela aprova | dona da entrega | a daniela`
- Cita a regra de alçada · `alcada | alcadas`

**Não pode conter:**
- Pedir o ok do Luis para seguir · `re:(aguard|esper)\w* (o )?ok do luis | re:luis (precisa|deve) aprovar`
- Alterar o HubSpot direto · `re:(atualiz|alter)\w* (direto )?no hubspot`

