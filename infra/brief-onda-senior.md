# Brief comum: aprofundamento sênior de uma área (D93, 22/10/2026)

Você vai levar uma ou mais áreas de agentes da Área Partners da Save Co. (gestor: Luis Fernando de Melo, gerente comercial de Masters) ao padrão sênior. Português do Brasil.

## Onde trabalhar
- Somente no worktree `/Users/luisfernandomelo/agentes-partners/.claude/worktrees/amazing-kirch-442f46`, e só dentro das pastas `skills/<área>/` que o seu pedido indicar.
- Outros agentes editam outras áreas ao mesmo tempo. Não mexa fora da sua pasta: o que precisar mudar fora dela vai no relatório final.
- Não faça commit. Não altere scripts que já existem, a não ser que o pedido diga.
- Nunca leia `.env`. Não altere HubSpot nem GLPI.

## Leia primeiro
1. `infra/padrao-senior.md`: o perfil (seção 0), as 10 seções obrigatórias e a regra de que produto em validação também é desenvolvido por inteiro. **É o critério de aceite.**
2. `docs/revisao-2026-10-22/auditoria-senioridade.md`: a seção da sua área (lacunas concretas e equipe-alvo).
3. A skill atual inteira, junto com o que ela aponta em `departamentos/`, `docs/` e `infra/`.
4. As decisões do Luis em `conselho/decisoes.md` (D1 a D93) e o guia de temas em `~/agentes-partners/gabinete/SESSOES.md` (só leitura).
5. O portfólio: `docs/portfolio-2027/matriz-agentes.md` (P1 a P18, N1 a N5) e a esteira (`docs/ecossistema/racional-e-fechamento-ecossistema-save.md`: Destravar caixa → Proteger e controlar → Crescer).
   - Estado dos produtos:
     - **Prontos:** recuperação tributária, Gestão de Passivo, produtos jurídicos, estruturação patrimonial, tax internacional, e Gestão de Contas, antecipação e FIDC (estes três da Save Invest, dono Junior, D92).
     - **Em validação, com o João Mattos:** Crédito Internacional, Maquila, captação, home equity e turnkey.

## Fontes para construir o perfil o mais sênior possível
- **Base interna:** skills, transcrições de reunião em `~/Library/CloudStorage/OneDrive-SAVECOMPANY/00 · Entrada/` e `99 · Arquivo/Download/`, decisões, docs e dados agregados. Não use dado nominal de cliente.
- **Web, nível Big Four** (`infra/protocolo-pesquisa.md`): reguladores, legislação no texto oficial (planalto.gov.br, Receita, PGFN, CVM, Bacen, ANPD, STF e STJ), Big Four (Deloitte, PwC, EY, KPMG), McKinsey, BCG e Bain, associações (ANBIMA, Febraban, ABF, CFC, OAB) e pesquisas de mercado. Sempre com a data de consulta.
- **Skills de método**, carregadas pela ferramenta Skill quando ajudarem. Use como referência de método e adapte ao Brasil e à Save. Exemplos:
  - vendas: `sales:account-plan`, `sales:handle-objection`, `sales:deal-review`, `sales:forecast`, `sales:account-tiering`, `sales:competitive-intelligence`;
  - operações: `operations:process-doc`, `operations:risk-assessment`, `operations:runbook`, `operations:capacity-plan`;
  - dados: `data:validate-data`, `data:statistical-analysis`;
  - mercado e setor: `bigdata-com:bigdata-sector-playbook`, `bigdata-com:bigdata-risk-assessment`;
  - compliance: `claude-for-financial-advisors:compliance`.

## O que entregar
- `skills/<área>/references/especialistas/<slug>.md`, um arquivo por especialista da equipe-alvo da auditoria (ajuste a equipe se a pesquisa mostrar uma melhor). Cada arquivo traz o **Perfil** e as **10 seções** com conteúdo de sênior:
  - normas com artigo e data;
  - números de mercado com fonte;
  - método com critérios e limites;
  - 10 ou mais perguntas de diagnóstico;
  - armadilhas;
  - 3 ou mais casos de referência (anonimizados ou públicos, com fonte);
  - fronteiras;
  - data.
- `references/perguntas-ao-dono.md` da área: o que só o humano responde, com a data e por que importa.
- `SKILL.md` atualizado:
  - equipe e gatilhos da `description`;
  - aponta para os arquivos;
  - preserva o conhecimento que já existe (reorganize, não apague).
- **Validação:** `python3 infra/auditar_senioridade.py --area <área> --detalhe`. A meta é 85 ou mais por área.

## Regras
- Nada de memória. Toda norma, tema ou número é conferido na fonte. O que não for confirmado fica marcado como [não confirmado] e vira pergunta ao dono.
- Nunca prometa valor, prazo ou êxito. A alíquota zero sai sempre via PER, nunca DCOMP. A trava do G2 vale só para o que se diz ao cliente.
- Sem nome de cliente, sócio, CPF ou telefone. LGPD.
- Escrita direta, sem enchimento. Sênior quer dizer critério e decisão, não volume.

## Relatório final (responda com)
1. Arquivos criados ou alterados, com o número de linhas.
2. A nota do auditor por área.
3. As 5 capacidades novas mais úteis para a receita.
4. O que ficou [não confirmado] e as perguntas ao dono.
5. As mudanças necessárias fora da sua pasta.
