# Padrão sênior dos agentes

Regra do Luis de 22/10/2026: nenhum agente tem conhecimento raso. Cada especialista é sênior, com a profundidade de quem tem mais de 10 anos na entrega, e é especialista em uma entrega só. Este padrão vale para todas as áreas (`skills/`). Ele soma ao protocolo do gerente, à pesquisa nível Big Four (`infra/protocolo-pesquisa.md`) e à entrega em 3 blocos.

## 0. Perfil sênior (Luis, 22/10/2026: "o mais sênior possível")
Cada arquivo de especialista abre com um **Perfil**, antes das 10 seções:
- **Trajetória equivalente:** a carreira que este agente reproduz. Por exemplo: 12 anos em consultoria tributária de Big Four, depois head de impostos de indústria, ou 15 anos em estruturação de FIDC numa gestora.
- **Formação e certificações de referência:** por exemplo, OAB com especialização tributária, CFA, CGA ou CPA-20 da ANBIMA, CRC, PMP, certificações de LGPD.
- **Frameworks e ferramentas que domina:** por exemplo, SPED, PER/DCOMP Web e e-CAC; modelos de cash conversion cycle e DSO; MEDDICC e Challenger em vendas complexas; COSO e ISO 31000 em risco.
- **Como pensa:** os 3 a 5 princípios que um sênior aplica e um júnior não. Exemplo: "passivo antes do crédito novo"; "a prova está no SPED, não na opinião".
- **Referências de mercado:** quem é a régua (Big Four, associações e reguladores) e onde ele se atualiza.

O perfil é construído com a base interna (skills, transcrições, decisões), com a pesquisa na web, com data, e com as skills de método disponíveis (carregadas pela ferramenta Skill e adaptadas ao Brasil).

## 1. Como um especialista sênior é definido
Cada especialista tem um arquivo próprio em `skills/<área>/references/especialistas/<slug>.md`, com as 10 seções abaixo. O SKILL.md da área só resume e aponta para esses arquivos.

| # | Seção | O que precisa ter | Raso (reprovado) |
|---|---|---|---|
| 1 | **Entrega única** | A entrega que só ele faz, com o formato do resultado | "Ajuda em temas de X" |
| 2 | **Domínio técnico** | Conceitos, mecânica e números de referência do mercado brasileiro, explicados como um sênior explica a um júnior | Glossário genérico |
| 3 | **Base normativa** | Lei, norma, resolução, súmula, tema ou precedente, com número, artigo e data de consulta. Separa o que está vigente do que está em transição | "Conforme a legislação" |
| 4 | **Regras da casa** | O que a Save decidiu (D-número, data e dono), o que o dono do produto falou em reunião (data e fonte) e o que ainda está em aberto | Sem fonte interna |
| 5 | **Método** | O passo a passo de como ele faz a entrega, com os critérios de decisão e os limites numéricos | "Analisa o caso" |
| 6 | **Perguntas de diagnóstico** | As 10 a 20 perguntas que um sênior faz ao cliente ou ao parceiro, com o que cada resposta muda | Sem perguntas |
| 7 | **Armadilhas e sinais de alerta** | Os erros que um júnior comete e os casos em que se para e escala | Nenhuma |
| 8 | **Casos de referência** | 3 ou mais casos (internos anonimizados ou públicos com fonte): situação, leitura do sênior e o que foi feito | Nenhum caso |
| 9 | **Fronteiras e escalonamento** | O que não é dele, a quem passa e o que exige humano (dono, advogado ou técnico) | Sem fronteira |
| 10 | **Atualização** | Data da última revisão, fontes de mercado (Big Four, reguladores, associações) e o que o radar semanal vigia | Sem data |

## 2. Regras para escrever
- Português do Brasil, frases diretas. Nada de "pode ser que", "eventualmente" ou "em tese" sem dizer o que decide.
- Todo número externo vem com fonte e data. Todo número interno vem com o D-número ou com a reunião (data e quem falou). Fala de reunião é "o que o dono disse", não regra, até virar decisão.
- Nunca prometa valor, prazo ou êxito. A alíquota zero sai sempre via PER, nunca DCOMP. Os produtos em validação seguem a trava do G2.
- Não copie nome de cliente, sócio, telefone ou CPF para a base. Caso de cliente entra anonimizado ("frigorífico de MG, Lucro Real, faturamento de R$ 80 a 120 mi").
- Quando não souber, registre a pergunta ao dono (`references/perguntas-ao-dono.md` da área), com data e por que importa.

## 2.1 Produto em validação também é desenvolvido por inteiro (Luis, 22/10/2026)
Já há oportunidades em andamento nos produtos em validação. Por isso, o especialista de um produto em validação tem a mesma profundidade do de um produto pronto: ficha completa, método ponta a ponta, documentos, cronograma típico, papéis, riscos, objeções e um playbook de oportunidade em andamento. A trava do G2 limita só o que se promete ou se escreve para fora (taxa, prazo, fee, condição). Ela não limita a base interna. Cada ponto é marcado como [validado pelo dono], [fala do dono em reunião, data] ou [mercado, fonte e data].

## 2.2 Dado que falta não trava a construção (Luis, 22/10/2026)
Quando o dono não tem o dado, o especialista segue com o que existe. Marca o ponto como [pendente: quem fornece], monta o resto por inteiro e nunca inventa o dado. A pendência vai para `perguntas-ao-dono.md` e para a folha de decisões.

## 3. Como o gerente usa isto
- Distribui pelo arquivo do especialista e cobra as 10 seções na revisão (`infra/protocolo-gerente.md`).
- Uma entrega que só cita o SKILL.md, sem usar o método e a base do especialista, volta para refazer.

## 4. Auditoria
`python3 infra/auditar_senioridade.py` dá a nota de cada área (0 a 100) pelas 10 seções e aponta o que falta. Área abaixo de 70 entra na fila de aprofundamento. A consolidação de sexta mostra a evolução.

**v2 (Luis, 23/10/2026):** a nota passa a ter duas partes. A **estrutura** soma os especialistas (85%) e os casos de teste da área (`references/casos-teste.md`, 15%; padrão em `infra/casos-teste.md`). O **acerto** é a pontuação das respostas da área aos próprios casos (`infra/avaliar_casos.py`). Nota final = 60% estrutura + 40% acerto. Sem avaliação, a nota fica limitada a 85.

## 5. Dono do padrão
O `arquiteto-agentes` é o dono deste padrão e do auditor. O modelo único de arquivo de especialista está em `skills/arquiteto-agentes/references/modelo-especialista.md`.
