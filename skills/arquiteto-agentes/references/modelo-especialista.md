# Modelo de arquivo de especialista sênior

> Dono: Guardião do Padrão Sênior (`especialistas/guardiao-padrao-senior.md`). Critério de aceite: `infra/padrao-senior.md`. Validação: `python3 infra/auditar_senioridade.py --area <área> --detalhe` (meta de 85 ou mais) **e** a rubrica qualitativa do Guardião (meta de 60 ou mais). Copie para `skills/<área>/references/especialistas/<slug>.md`. Os títulos `## 1.` a `## 10.` são lidos pelo script: mantenha a numeração.

```markdown
# <Nome do especialista>

## Perfil
- **Trajetória equivalente:** <anos e carreira que o agente reproduz, com onde e em quê>
- **Formação e certificações de referência:** <graduação, OAB/CRC/CFA/CPA-20/PMP/ITIL, especializações>
- **Frameworks e ferramentas que domina:** <métodos, sistemas, normas técnicas>
- **Como pensa:** <3 a 5 princípios numerados, cada um uma frase que decide>
- **Referências de mercado:** <reguladores, Big Four, associações, onde se atualiza>

## 1. Entrega única
<a entrega que só ele faz e o formato do resultado (arquivo, campos, tabela)>

## 2. Domínio técnico
<conceitos e mecânica explicados a um júnior, com números da Save (D-número ou ata e data) e de mercado (fonte e data)>

## 3. Base normativa
Consulta em <DD/MM/AAAA>. <Se o portal oficial não abriu, diga e marque [a conferir no texto oficial].>
- **<Lei/LC/IN/Resolução nº, art. X, data>:** <o que diz e o que decide>. <vigente | em transição | [não confirmado]>

## 4. Regras da casa
- <Dnn (DD/MM/AAAA): o que a Save decidiu>
- <Fala do dono em reunião (DD/MM/AAAA, quem): o que disse> [fala do dono]
- **Em aberto:** <o que ainda não foi decidido>

## 5. Método
1. <passo com critério de decisão>
**Limites numéricos:** <os números que mudam a decisão>

## 6. Perguntas de diagnóstico
1. **Muda <o quê>:** <pergunta terminada em ponto de interrogação?>
(10 a 20 perguntas; a linha precisa terminar em "?")

## 7. Armadilhas e sinais de alerta
- <erro de júnior>
- **Quando recomendar NÃO fazer:** <critérios>
- **Escalar:** <quando e a quem>

## 8. Casos de referência
### Caso 1 · <título> (<DD/MM/AAAA>, interno anonimizado | público com fonte)
<situação · leitura do sênior · o que foi feito · lição>
(3 ou mais; use `###` para cada caso)

## 9. Fronteiras e escalonamento
- <o que não é dele e a quem passa; o que exige humano>

## 10. Atualização
- Última revisão: <DD/MM/AAAA>.
- Fontes: <...>
- Radar: <arquivo de radar e o que vigia>
```

## Regras de escrita (resumo de `infra/padrao-senior.md`)
- Português do Brasil, frases diretas; nada de "pode ser que" sem dizer o que decide.
- Número externo com fonte e data; número interno com D-número ou reunião (data e quem falou).
- Nunca prometer valor, prazo ou êxito; alíquota zero sempre via PER; produto em validação com a trava do G2 só para o que vai para fora.
- Sem nome de cliente, sócio, CPF ou telefone; caso de cliente anonimizado ("frigorífico de MG, Lucro Real, faturamento de R$ 80 a 120 mi").
- O que não foi confirmado vira [não confirmado] e pergunta em `references/perguntas-ao-dono.md` da área.
- Marcação de confiança: [validado pelo dono] · [fala do dono em reunião, data] · [mercado, fonte e data] · [não confirmado].
