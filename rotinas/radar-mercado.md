---
name: radar-mercado
description: Toda sexta 7h: cada área pesquisa o que mudou no mercado (normas, julgados, taxas, regulação, concorrentes, tendências), atualiza o radar-mercado.md da sua skill com fonte e data, aponta conflitos com a base e manda o resumo ao Luis.
---

Rotina semanal (sexta-feira, 7h) da Área Partners. Ela mantém os agentes atualizados com a informação mais recente do mercado e com o rigor de uma Big Four, conforme a regra do Luis de 16/10/2026. Siga `~/agentes-partners/infra/protocolo-pesquisa.md`. Responda em português do Brasil. A fonte deste texto é `~/agentes-partners/rotinas/radar-mercado.md`: se ela existir e for diferente deste texto, siga o arquivo.

1. **Para cada radar da tabela do §6 do protocolo,** acione o GERENTE da área. Use uma ferramenta Agent por radar, em paralelo; sem a ferramenta Agent, assuma o papel lendo o `~/.claude/skills/<skill>/SKILL.md`. Não há Portão 0. Os radares são:
   - Tributário;
   - Jurídico;
   - Produtos Internacionais (crédito e câmbio; financeiro e Maquila);
   - Comercial.

   Cada gerente:
   - lê o radar atual e a base da área (`references/`, decisões, aprendizados);
   - pesquisa com WebSearch e WebFetch (carregue com ToolSearch) **o que mudou desde a data-base do radar**: normas e regulação, julgados, dados e taxas de mercado, concorrentes, publicações das Big Four e tendências do setor. Usa a fonte primária para afirmar e a Big Four como benchmark;
   - atualiza o arquivo do radar:
     - data-base de hoje e próxima revisão em +7 dias;
     - itens novos no topo de cada seção, cada um com: o que mudou (data), impacto para a Save, ação do agente, fonte (URL, data de publicação, data de consulta), vigência e confiança;
     - itens superados marcados como "superado em <data>", não apagados;
     - seção "Conflitos com a base interna";
     - seção "Perguntas novas ao dono";
   - revisa antes de devolver, pelo protocolo do gerente: tudo tem fonte e data, nada foi inventado, não há dado de cliente.
2. **Trava de qualidade.** Item sem URL ou sem data volta ao gerente, no máximo 2 rodadas. Se continuar sem fonte, sai do radar.
3. **Não muda regra sozinho.** Item que altera tese, produto, regra de remuneração ou frase permitida vira proposta. Ele vai para `~/agentes-partners/registro/achados-areas-<AAAA-MM-DD>.json`, no formato `{area, achado, impacto, acao, falta, fonte}`, e o Conselho lê esse arquivo na reunião semanal. Pergunta para o dono do produto internacional entra em `~/.claude/skills/depto-internacional/references/perguntas-ao-dono.md`.
4. **Grave o radar numa branch própria, nunca no checkout principal** (Luis, 23/10/2026: arquivo alterado e sem commit no principal trava o merge das outras conversas). Rode `cd ~/agentes-partners && git worktree add -B radar/<AAAA-MM-DD> .claude/worktrees/radar-<AAAA-MM-DD> main` (se já existir, reuse). Copie para lá os radares atualizados (`skills/<skill>/references/`, iguais à cópia viva em `~/.claude/skills/`) e faça commit em português, com 0 achados no `infra/checar-dados.py`. O resumo ao Luis traz o comando de merge: `cd ~/agentes-partners && git merge --no-edit radar/<AAAA-MM-DD> && git push`.
5. **Mande o resumo ao Luis pelo caminho de e-mail da Central** (Graph ligado; se não estiver, grave em `04 · Gestão, Metas e Estratégia/Central de Agentes/Radar de mercado/radar-<AAAA-MM-DD>.md`). O resumo traz:
   - os 10 achados da semana que mais mudam a operação;
   - os conflitos com a base;
   - as perguntas novas;
   - a idade de cada radar.

   Use o layout único de e-mail do `depto-marketing` (padrão Save).
