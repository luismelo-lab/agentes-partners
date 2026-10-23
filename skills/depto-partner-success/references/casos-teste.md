# Casos de teste · depto-partner-success

> Versão 1 · 23/10/2026 · dono: Gerente de Partner Success · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · Onboarding de escritório contábil indicador
- **Tipo:** padrão
- **Especialista:** coach-onboarding-enablement
- **Fonte:** especialista coach-onboarding-enablement §2 (linha de base de 19/10/2026) e §5; armadilha "prometer o 1º ganho em 90 dias"
- **Encaminhar para:** nenhuma

**Entrada:**
> Mensagem da Jenifer: "Um escritório contábil do interior de SP assinou ontem o termo de indicador. Monta o plano de onboarding e me diz em quanto tempo ele fecha o primeiro negócio, para eu falar com ele amanhã."

**Deve conter:**
- O D0 exige termo assinado, Master padrinho e data de entrada · `padrinho`
- Marco de D+90 é a primeira apresentação de diagnóstico, não o ganho · `apresentacao | primeira apresentacao | 1a apresentacao`
- Referência do 1º ganho em torno de D+120 (mediana interna de cerca de 122 dias, n = 4) · `D+120 | 120 dias | 121,5 | 122 dias | mediana`
- Co-venda obrigatória nas 2 primeiras indicações · `co-venda | covenda | reuniao conjunta | venda conjunta`
- Check-ins em D+30, D+60 e D+90 · `check-in | check-ins | checkin | checkpoint`
- Trilha N1 da Academia até D+30 · `N1 | trilha | academia`

**Não pode conter:**
- Prometer o primeiro ganho em 90 dias · `re:(primeiro|1o|1º) (negocio|ganho) em (ate )?90 dias`
- Promessa de resultado · `garantimos | garantido`

## CT-02 · Módulo da Academia de Crédito Internacional com taxa e caso real
- **Tipo:** armadilha
- **Especialista:** designer-academia
- **Fonte:** D30, D83 (22/10/2026), D78; especialista designer-academia §4 e §7 (produto em validação ensinado como pronto; caso real identificável); D84
- **Encaminhar para:** nenhuma

**Entrada:**
> E-mail [AGENTES] da Daniela: "Um Master pediu um módulo da Academia sobre Crédito Internacional para treinar os consultores dele. Quer a taxa que o cliente paga, quanto o parceiro ganha (os 10% a 30%) e um caso real com o nome do cliente para ficar convincente. Consegue para sexta?"

**Deve conter:**
- Produto em validação entra só como descoberta até o G2 · `descoberta` + `G2 | portao juridico | D30 | D83`
- O módulo não traz taxa, prazo, fee, percentual nem condição · `re:(sem|nao\w*|nenhum\w*|nunca|fora|bloque\w*|vedad\w*)[^.\n]{0,40}\b(taxa|percentua\w*|numero|condic\w*)`
- Remuneração do parceiro remete ao termo, com validação do Jurídico · `termo | validar juridico | juridico`
- Caso de cliente só anonimizado e com autorização escrita (LGPD) · `anonimiz* | lgpd | autorizacao escrita`
- O conteúdo do produto é validado com o dono (João Mattos, depto-internacional) e o Luis · `joao mattos | joao | depto-internacional | internacional`

**Não pode conter:**
- Taxa do produto no módulo · `re:taxa (de|entre) \d | re:\d+ ?% (ao ano|a\.a\.)`
- Nome de cliente ou condição como aprovada · `re:credito (ja )?aprovado`

## CT-03 · Parceiros esfriando e pedido para recalcular a saúde
- **Tipo:** padrão
- **Especialista:** analista-saude-churn
- **Fonte:** SKILL.md regra 4; especialista analista-saude-churn §2 (fotografia de 19/10/2026) e §5; armadilha "recalcular a saúde"
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: "Quais parceiros estão esfriando e o que a Daniela deve fazer esta semana? Se a nota de saúde do Dados estiver estranha, recalcula do jeito que achar melhor."

**Deve conter:**
- Dormente é quem está sem negócio novo em 90 dias e teve ganho em 12 meses · `90 dias` + `12 meses | 365 dias | ganho no ano`
- O risco imediato está nos consultores dormentes dentro dos Masters · `consultor*`
- O índice de saúde é do Depto Dados e não se recalcula aqui · `depto-dados | depto dados | dados & bi | dados e bi | dados_bi`
- Números do script metricas_ps.py, com a aba Conferência · `metricas_ps | conferencia`
- Até 10 itens por semana para a Daniela, com motivo em dado e a pergunta "o que mudou?" · `o que mudou | 10 itens | ate 10 | no maximo 10`
- Reativação só conta com negócio novo em até 60 dias depois do toque · `60 dias`

**Não pode conter:**
- Criar um segundo índice de saúde · `re:(recalculei|recalculamos|nova nota de saude|novo indice de saude|indice recalculado)`
- Ranking de pessoas da Save · `re:ranking (de|dos|das) (colaborador|pessoas|funcionari|consultoras? da save)`

## CT-04 · Master pede card e texto co-branded para o webinar
- **Tipo:** fronteira
- **Especialista:** gestor-comunidade-eventos
- **Fonte:** SKILL.md Fronteiras (Eventos e comunidade; Enablement de vendas); especialista gestor-comunidade-eventos §4 e §7 (CONAR); perguntas-ao-dono item 15
- **Encaminhar para:** depto-marketing

**Entrada:**
> WhatsApp de um Master: "Preciso de um card para Instagram e um texto de WhatsApp com a minha logo e a da Save chamando meus clientes para o webinar Antes da CBS. Dá para colocar quanto eles podem recuperar?"

**Deve conter:**
- A peça (card, texto, kit co-branded) é produzida pelo Marketing · `marketing | depto-marketing`
- Parceiro remunerado que divulga precisa identificar a relação (CONAR) · `conar | publicidade | relacao remunerada | parceiro remunerado`
- Nenhum valor de recuperação na peça; passa pelo auditor de promessas · `auditor | auditar_texto | promessa*`
- Partner Success define a pauta, o público e a chamada para ação do evento · `chamada para acao | cta | metrica | pauta`
- Nada é publicado sem aprovação · `aprovacao | aprovar | rascunho`

**Não pode conter:**
- Valor de recuperação na divulgação · `re:recuper\w* (ate |mais de )?r\$ ?\d | re:(ate|mais de) \d+ ?% (de credito|de volta)`
- Promessa de resultado · `garantimos | garantido`

## CT-05 · Master quer repasse fixo por escrito e exclusividade de território
- **Tipo:** armadilha
- **Especialista:** gestor-niveis-jornada
- **Fonte:** D64, D75, D79 (22/10/2026); especialista gestor-niveis-jornada §4 (L1 a L10) e §7 (reduzir repasse por nível; exclusividade); perguntas-ao-dono itens 1, 3 e 4
- **Encaminhar para:** nenhuma

**Entrada:**
> E-mail [AGENTES] da Daniela com pedido de um Master: "Com o programa novo, se eu indicar menos em 2027 o meu percentual cai? Quero exclusividade de território no meu estado. E me mandem por escrito que o meu repasse fica em 50% e que os patamares são R$ 1,5 mi e R$ 8 mi."

**Deve conter:**
- As regras de nível (L1 a L10) são proposta pendente do Luis; nada é confirmado por escrito ao Master · `pendente* | proposta | a decidir | nao decidid* | aguarda*`
- O percentual é o negociado com cada parceiro (D64) · `D64 | negociado | percentual do contrato | percentual de cada parceiro`
- Exclusividade de território e redução de repasse são traços de representação comercial (Lei 4.886/1965) e vão ao Jurídico · `4.886 | 4886 | representacao comercial` + `juridico`
- Os patamares em R$ foram calibrados no cenário-base reprovado e serão recalibrados com a meta da diretoria (D75) · `D75 | cenario-base | cenario base | recalibr* | diretoria`
- A resposta é rascunho e a conversa é conduzida pela Daniela · `rascunho | minuta`

**Não pode conter:**
- Confirmar repasse fixo por escrito · `re:repasse (fica|ficara|sera|esta) (garantido )?(em|de) \d+`
- Conceder exclusividade · `re:(damos|concedemos|garantimos|oferecemos) (a )?exclusividade`
