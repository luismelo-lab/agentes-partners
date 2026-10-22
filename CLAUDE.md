# Área Partners · padrão único de operação dos agentes

Vale para toda conversa, fork, worktree e rotina neste repositório. O objetivo é que todas as sessões trabalhem do mesmo jeito e que nenhuma referência se perca entre elas (regra do Luis de 21/10/2026). Português do Brasil.

## 1. Antes de começar
0. **Porteiro de pedidos (obrigatório):** antes de executar um pedido novo do Luis, siga `infra/porteiro.md`. Rode `python3 ~/agentes-partners/infra/ja_existe.py "<pedido>"`, classifique o pedido (repetido, continuação, relacionado, travado ou novo) e, se for repetido, continuação em outra conversa ou travado, devolva ao Luis antes de produzir. Registre com `--registrar`.
1. Leia `ESTADO.md` e a seção do seu tema em `~/agentes-partners/gabinete/SESSOES.md`. É uma conversa por tema. Tema novo ganha uma seção.
2. Rode `git fetch && git branch -a --no-merged main` e veja se outra sessão já mexeu nos mesmos arquivos. Isso inclui as sessões na nuvem, que publicam em `origin/claude/*`. Se mexeu, junte a branch dela à sua antes de alterar, em vez de refazer. Sessão na nuvem sempre faz push da branch, para o trabalho não ficar só lá.
3. Use a skill da área (`skills/`). Toda demanda passa pelo fluxo único (`infra/fluxo-unico.md`).

## 2. Como os agentes trabalham (obrigatório)
- **Gerente e especialistas:** `infra/protocolo-gerente.md`. O gerente distribui, revisa antes de devolver (até 2 rodadas) e aciona outra área quando precisa. Toda entrega leva o registro `revisao`.
- **Entrega em 3 blocos:** `infra/padrao-entrega.md` (o que você pediu, o que você também precisa, o que falta e quem fornece).
- **Pesquisa nível Big Four:** `infra/protocolo-pesquisa.md`. Usa base interna, dados por script, radar da área e pesquisa na hora, com data. A decisão interna só muda com o dono.
- **Material para fora:** passa por todas as áreas envolvidas e pelo auditor de promessas (`depto-qualidade/scripts/auditar_texto.py`). O Luis vê um exemplo antes da execução em massa.

## 3. Regras da casa
- Nunca leia `.env`. Não altere HubSpot nem GLPI: só leitura e rascunho. Nada é enviado sem aprovação.
- Nunca prometa valor, prazo ou êxito. A alíquota zero sai sempre via PER, nunca DCOMP. Produtos em validação (Crédito Internacional, Maquila, captação de capital e home equity, com o João Mattos) só entram como descoberta até o G2. Gestão de Contas, antecipação e FIDC (Save Invest), estruturação patrimonial e tax internacional são produtos prontos (Luis, 19/10/2026).
- LGPD: dado de cliente fica no Mac. Dados de sócios e contatos ficam só em `dados-publicos/receita/prospects-contatos.json` (permissão 600). Não se busca celular pessoal fora do cadastro público da empresa.
- Visual: Design System Save v0.5 (`departamentos/marketing-marca/padrao/`). Word pelo `departamentos/produtos/credito-internacional/scripts/gerar_manual_docx.js`, que aceita `DOC_MD`, `DOC_VERSAO`, `DOC_CABECALHO` e `DOC_SELO`; rode com `NODE_PATH=~/.partners-node/node_modules`, a pasta fixa de bibliotecas (a pasta temporária da sessão é apagada).

## 4. Onde as coisas ficam (fonte da verdade)
- **Código e skills:** este repositório. Ao alterar uma skill ou rotina, copie também para a cópia viva (`~/.claude/skills/<skill>/` e `~/.claude/scheduled-tasks/<rotina>/SKILL.md`). Antes, confira que a cópia viva é igual ao `HEAD`; se for diferente, junte as duas.
- **Processos:** nunca deixe um processo que gerou entrega só na pasta temporária da sessão (scratchpad). Leve os scripts para `skills/<área>/scripts/<tema>/`, com README dos passos, e os dados para `departamentos/<área>/<tema>/` (fora do git).
- **OneDrive:** o destino sai de `lib/caminhos.py` (`luis(<chave>)` ou `pasta(<pessoa>)`). O link vem de `caminhos.web()`, que para arquivo devolve a pasta (só o link de pasta abre). Na resposta, dê o nome do arquivo junto do link.

## 5. Git
- Trabalhe na branch do seu worktree. Commit com mensagem em português e as linhas de atribuição pedidas. O hook `infra/checar-dados.py` precisa dar 0 achados.
- O Luis faz o merge e o push (`cd ~/agentes-partners && git merge --no-edit <branch> && git push`). Não deixe branch com trabalho sem dizer a ele.
- Uma mudança só entra uma vez: se outra branch já trouxe a mesma alteração, não a refaça.

## 6. Consolidação semanal
Toda sexta, às 16h, a rotina `consolidacao-semanal` junta as branches, resgata arquivos dos worktrees, atualiza o `SESSOES.md`, aponta repetições e conflitos e atualiza a folha de decisões (`docs/revisao-2026-10-22/decisoes-pendentes.md`).

## 7. Ao terminar
Atualize a seção do tema em `gabinete/SESSOES.md`: estado, onde estão os arquivos, próximo passo e decisões pendentes do Luis. A resposta final leva o link de cada documento publicado.
