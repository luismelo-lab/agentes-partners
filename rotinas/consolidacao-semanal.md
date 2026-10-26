---
name: consolidacao-semanal
description: Toda sexta 16h, junta o trabalho das conversas da semana (branches, worktrees, nuvem), resgata arquivos soltos, atualiza o guia de sessões, aponta pedidos repetidos e conflitos de regra e manda ao Luis a folha de decisões atualizada.
---

Rotina semanal de consolidação da Área Partners (sexta, 16h). O objetivo é que nenhuma referência se perca entre as conversas (regras do Luis de 21 e 22/10/2026). Siga `~/agentes-partners/CLAUDE.md` e `~/agentes-partners/infra/porteiro.md`. Português do Brasil. A fonte deste texto é `~/agentes-partners/rotinas/consolidacao-semanal.md`: se ela existir e for diferente, siga a do arquivo. Nunca leia `.env`. Não altere HubSpot nem GLPI. Não faça merge no `main`: só prepare e informe.

1. **Branches:** rode `cd ~/agentes-partners && git fetch && git branch -a --no-merged main`. Para cada branch com commits:
   - diga a conversa de origem, o que ela traz e se conflita com o `main` (`git merge-tree`);
   - junte as que não conflitam na branch desta rotina, com commit;
   - liste as que conflitam, com os arquivos em conflito.
2. **Trabalho sem commit:** em cada worktree de `.claude/worktrees/`, rode `git status --short` e procure arquivos novos fora do git (pdf, docx, pptx, xlsx, md) modificados nos últimos 7 dias. Não apague nada. Copie o que for entrega para a pasta de dados da área (`departamentos/<área>/<tema>/`) e liste o que precisa de commit pela conversa de origem.
2b. **Limpeza de worktrees (Luis, 23/10/2026):** remova com `git worktree remove` (sem `--force`) e `git branch -d` os worktrees de `.claude/worktrees/` cuja branch já está no `main`, sem arquivo solto (`git status --porcelain` vazio) e sem nada modificado há 3 dias ou mais. Nunca remova o worktree desta rotina nem o de uma conversa ativa. Rode `git worktree prune` e informe quantos saíram e o espaço liberado.
3. **Cópias vivas:** compare `skills/` com `~/.claude/skills/` e `rotinas/` com `~/.claude/scheduled-tasks/*/SKILL.md`, ignorando `node_modules`, `ocr` e `__pycache__`. Liste o que diverge, sem sobrescrever.
4. **Coerência:** procure nos arquivos alterados na semana:
   - nome antigo da esteira (Oxigenar, Estruturar, Expandir ou Escalar fora de atas);
   - produto pronto tratado como "em definição" ou com a trava do G2 (Gestão de Contas, antecipação, FIDC, estruturação patrimonial, tax internacional);
   - frases proibidas do Crédito Internacional fora da exceção registrada em `skills/depto-internacional/references/regras-e-proibidos.md`;
   - rotas que não citam `depto-solucoes` ou `depto-internacional`.
4b. **Senioridade e acerto (Luis, 23/10/2026):**
   - Rode `python3 ~/agentes-partners/infra/avaliar_casos.py --validar`.
   - A rodada da semana cobre 9 áreas: as 3 do piloto (tributário, Save Invest, Daniela) e mais 6 em rodízio, para que todas sejam avaliadas a cada 3 semanas (a avaliação vale 21 dias).
   - Para cada área, rode `--preparar --area <área>` e acione um subagente que lê só `skills/<área>/`, nunca `casos-teste.md`. Ele grava as respostas em `registro/avaliacoes/<área>/CT-nn.md`.
   - Rode `--pontuar` e depois `python3 ~/agentes-partners/infra/auditar_senioridade.py --json`.
   - No resumo ao Luis, mostre estrutura × acerto, os casos críticos e as aprovações vazias da semana (§5.1 do protocolo do gerente).
   - Caso que a área erra 2 semanas seguidas volta ao gerente como correção no especialista.
5. **Repetições:** leia `registro/pedidos-luis.jsonl` da semana. Junte pedidos parecidos, aponte os temas pedidos mais de uma vez e diga o que estava repetido.
6. **Guia de sessões:** atualize `~/agentes-partners/gabinete/SESSOES.md`:
   - estado, local dos arquivos e próximo passo de cada tema mexido na semana;
   - seção nova para tema novo;
   - seção de tema parado há mais de 14 dias marcada como "parado desde <data>".
7. **Decisões:** a fonte é `docs/revisao-2026-10-22/decisoes.json`, e a folha com campos de seleção está em `04 · Gestão/Central de Agentes/Decisoes-Pendentes-<data>.xlsx`.
   - Rode `python3 ~/agentes-partners/infra/folha_decisoes.py ler <última folha>`.
   - Para cada resposta "Aprovar" ou "Aprovar com ajuste", acione a área da coluna "Quem aplica" para aplicar no material de origem, com revisão do gerente. Registre a decisão em `conselho/decisoes.md` quando for do Conselho e tire o item do JSON.
   - "Reprovar" vai para o histórico do JSON, com o motivo. "Decidir depois" continua na folha.
   - Item com `padrao: true`, sem resposta e com prazo vencido: aplique a recomendação, registre em `conselho/decisoes.md` como "aplicado por padrão (infra/alcadas.md)" e liste no resumo para o Luis poder reverter. Nunca aplique por padrão preço, meta, remuneração, tese na vitrine, frase permitida, produto em validação, contrato ou envio externo.
   - Decisão nova da semana entra na folha só se a matriz de alçada (`infra/alcadas.md`) disser que é do Luis.
   - Acrescente as decisões novas da semana, cada uma com a conversa de origem e o prazo.
   - Gere a folha de novo com `folha_decisoes.py gerar`. As respostas ainda não aplicadas são mantidas.

7b. **Controle (Luis, 26/10/2026; `infra/controle.md`):** rode `python3 ~/agentes-partners/infra/controle.py --resumo`. Ele lê o pacote e a previsão mais recentes, aplica as regras de `infra/controle.json`, grava `registro/gestao/controle-<hoje>.json` e manda cada desvio novo à caixa de entrada da pessoa dona (uma vez por semana). No resumo ao Luis, liste os desvios abertos (regra, dono, prazo, alçada), os vencidos e os escalados a ele, e as ações de `registro/gestao/acoes.jsonl` com prazo vencido (C21). Desvio com dono agente vai para a pauta do Conselho de segunda; não crie decisão nova na folha para o que a alçada diz que é da dona ou do gerente.

8. **Resumo ao Luis:** e-mail pelo caminho da Central (Graph ligado; se não estiver, grave em `04 · Gestão/Central de Agentes/Caixa de saída`). O resumo traz:
   - branches a juntar, com o comando de merge;
   - desvios do controle (abertos, vencidos, escalados) e ações vencidas;
   - arquivos resgatados;
   - divergências;
   - inconsistências;
   - temas repetidos;
   - as 5 decisões mais urgentes;
   - o link da pasta.
