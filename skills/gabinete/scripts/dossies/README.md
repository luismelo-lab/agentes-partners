# Dossiês de decisão do Luis

Pedido do Luis (26/10/2026): as decisões chegam com o contexto do que precisa ser decidido e com a validação dos agentes responsáveis.

## Passos
1. Listar as pendentes e ver o que falta: `python3 skills/gabinete/scripts/dossies_decisao.py` (saída 1 se houver pendente sem dossiê, sem validação ou com dossiê de mais de 7 dias; `--max-dias N` muda o limite).
2. Para cada área dona do tema, acionar um subagente que lê `skills/<área>/SKILL.md` e o especialista certo em `references/especialistas/` e grava os pareceres em `registro/gestao/dossies/pareceres/<data>/<área>.json`: lista de `{id, area, especialista, parecer (concorda | concorda com ressalva | discorda), motivo, base, condicao, ressalva, fatos[{fato, fonte, tipo}]}`.
3. Montar os dossiês com o conteúdo do Gabinete e os pareceres (modelo: `montar_dossies_2026_10_26.py`; copie para a data nova e ajuste o conteúdo).
4. `python3 skills/gabinete/scripts/dossies_decisao.py --indice` grava `registro/gestao/dossies/indice.json`.
5. Word: `dossies_decisao.py --md <md absoluto>`, auditor `python3 skills/depto-qualidade/scripts/auditar_texto.py <md>` (0 ALTO, 0 MÉDIO), depois
   `NODE_PATH=~/.partners-node/node_modules DOC_MD=<md> DOC_VERSAO="<dd/mm/aaaa>" DOC_CABECALHO="Dossiê de decisões" DOC_SELO="Uso interno" node departamentos/produtos/credito-internacional/scripts/gerar_manual_docx.js "<caminhos.luis('central')>/Dossie-de-Decisoes-<data>.docx"`.

## Schema de `registro/gestao/dossies/<id>.json`
`id, titulo, urgencia (1 = mais urgente), prazo (AAAA-MM-DD), folha_item, padrao, o_que_decidir, por_que_agora, custo_nao_decidir, contexto[{fato, fonte, tipo: fato|estimativa|opiniao}], opcoes[{nome, pros, contras, risco, efeito}], recomendacao, se_reprovada, validacoes[{area, especialista, parecer, motivo, base, condicao, ressalva}], divergencias, execucao{dono, prazo, indicador}, atualizado_em, fonte_pareceres, revisao`.

Os dossiês e os pareceres ficam fora do git (`registro/`). Sem nome de cliente; valores são potenciais; norma é pré-análise para validação humana.
