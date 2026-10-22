# Porteiro de pedidos: validar antes de executar
**Regra do Luis (22/10/2026):** antes de executar, valide se o que ele pede é repetido, é continuação de algo ou está travado. Use tudo o que já foi feito. Não execute no automático.

## Quando
Em todo pedido novo do Luis, em qualquer conversa, fork, worktree ou rotina que receba pedido. Fazem parte disso a Central, o Gabinete, o WhatsApp do Luis e as conversas de tema. Ficam de fora as perguntas rápidas e os ajustes num material que já está sendo feito na mesma conversa.

## Como (4 passos, antes de qualquer outra coisa)
1. **Consultar:** rode `python3 ~/agentes-partners/infra/ja_existe.py "<pedido em uma frase>"`. O índice cobre documentos, skills, guia de sessões, decisões do Conselho, commits de todas as branches (inclusive as da nuvem), entregas no OneDrive e o catálogo da Central.
2. **Classificar:**
   - **Repetido** (nota 0,60 ou mais, mesmo objeto): não crie de novo. Diga onde está, de quando é e o que falta nele. Proponha atualizar ou continuar.
   - **Continuação** (o tema tem conversa ou seção própria): diga em qual conversa ou seção ele vive. Se a conversa for outra, proponha seguir lá ou trazer o tema para cá, juntando a branch.
   - **Relacionado** (nota de 0,35 a 0,60): reaproveite. Cite os itens que entram como insumo (dados, decisões, scripts, playbooks) e as conexões com as outras frentes.
   - **Travado:** se uma decisão pendente ou uma pendência de terceiro bloqueia o pedido, diga qual é antes de produzir.
   - **Novo:** só quando nada acima se aplica. Aí o tema ganha seção no `gabinete/SESSOES.md`.
3. **Devolver ao Luis antes de executar** quando for repetido, continuação em outra conversa ou travado. Mande uma linha por item com o que existe, o que proponho e a pergunta. Quando for relacionado ou novo, siga e diga no início da resposta o que foi reaproveitado.
4. **Registrar:** rode `ja_existe.py "<pedido>" --registrar novo|atualizacao|repetido --destino "<arquivo ou conversa>"`. O registro fica em `registro/pedidos-luis.jsonl` e mostra, na consolidação semanal, onde os pedidos se repetem.

## Usar tudo o que já fizemos (o racional das conexões)
Todo pedido passa por quatro perguntas, que a resposta deve explicitar:
1. Qual **área** é dona? Veja a tabela do `infra/fluxo-unico.md`.
2. Qual **onda da esteira** é: Destravar caixa, Proteger e controlar ou Crescer (`docs/ecossistema/racional-e-fechamento-ecossistema-save.md`)?
3. Que **dados e entregas** já existem para reaproveitar? Por exemplo: o mapa da conta, a prospecção do Master, os radares, os playbooks e as fichas do portfólio 2027.
4. Que **decisão** do Luis ou do Conselho vale aqui, ou está pendente?
