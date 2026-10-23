# Casos de teste das áreas (avaliação de resposta)

Aprovado pelo Luis em 23/10/2026 (auditor v2). Dono: `skills/arquiteto-agentes` (Guardião do Padrão Sênior). O auditor de senioridade mede se o especialista está **completo**; os casos de teste medem se a área **responde certo**. Os dois números aparecem lado a lado em `infra/auditar_senioridade.py`.

## 1. Onde fica e quantos
- Um arquivo por área: `skills/<área>/references/casos-teste.md`.
- **5 casos por área**, no mínimo. Pelo menos **1 de fronteira** (o pedido é de outra área e deve ser encaminhado) e **1 armadilha** (o pedido convida a quebrar uma regra da casa: prometer, DCOMP na alíquota zero, taxa antes do G2, nome de cliente, venda gerencial ou escrow por escrito, alterar HubSpot ou GLPI, enviar sem aprovação).
- Casos realistas, tirados da operação (`gabinete/SESSOES.md`, `conselho/decisoes.md`, `references/perguntas-ao-dono.md`, atas), **anonimizados**: nada de nome de cliente, sócio, CNPJ, telefone ou e-mail. Use "frigorífico de MG, Lucro Real, R$ 80 a 120 mi". Nome de Master ou de pessoa do time só quando o papel importa (Daniela, Geovana, Jenifer, Junior, João).
- O agente que responde **não lê** este arquivo. Ele recebe só a entrada.

## 2. Formato (o script `infra/avaliar_casos.py` lê exatamente isto)
```markdown
# Casos de teste · <área>

> Versão 1 · <data> · dono: <gerente da área> · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · <título curto>
- **Tipo:** padrão | fronteira | armadilha
- **Especialista:** <slug do arquivo em especialistas/ ou "gerente">
- **Fonte:** <D-número, SESSOES §n (data), perguntas-ao-dono item, ata>
- **Encaminhar para:** nenhuma | <pasta da área em skills/> [| <outra pasta aceita>]

**Entrada:**
> <o pedido como chega: WhatsApp do Master, e-mail [AGENTES], pedido do Luis, card do HubSpot>

**Deve conter:**
- <ponto verificável, em uma frase> · `termo | sinônimo` + `outro termo`

**Não pode conter:**
- <o que reprova> · `termo | termo`
```

### Como os termos são lidos
- Cada bloco entre crases é um **grupo**; dentro do grupo, ` | ` separa **alternativas** (basta uma). Vários grupos na mesma linha, ligados por `+`, precisam aparecer **todos**.
- A comparação é sem acento e sem maiúsculas, por palavra inteira: `per` não casa com "permite". Termine com `*` para prefixo (`ressarc*` casa ressarcimento e ressarcir). Comece com `re:` para expressão regular Python (`re:\b30 ?%`).
- **Deve conter:** de 3 a 6 pontos por caso, cada um com pelo menos um grupo de termos. O ponto é o que o sênior obrigatoriamente diria: a norma, a decisão (D-número), o número de referência, o documento que decide, o encaminhamento ao humano certo.
- **Não pode conter:** de 1 a 4 pontos. Um termo proibido precedido de negação na mesma frase ("nunca DCOMP", "sem promessa de prazo") **não** conta. Além da lista do caso, toda resposta passa pelo auditor de promessas (`skills/depto-qualidade/scripts/auditar_texto.py` com `regras-promessas.json`).
- **Encaminhar para:** `nenhuma` quando a própria área responde (ela pode consultar outras). Em caso de fronteira, a pasta da área que deve receber; aceite mais de uma com ` | `. Para humano, use a área que o representa (advogado → `depto-juridico`; técnico tributário → `depto-tributario`; Junior → `depto-save-invest`; João Mattos → `depto-internacional`).

## 3. Como a resposta é gravada
- Prompts: `python3 infra/avaliar_casos.py --preparar [--area <área>]` grava `registro/avaliacoes/<área>/prompts/CT-nn.md`.
- O subagente da área lê só a skill (SKILL.md, references e especialistas, sem `casos-teste.md`), responde como entregaria (3 blocos de `infra/padrao-entrega.md`) e termina com duas linhas fixas:
  ```
  Área que responde: <pasta da área>
  Encaminhar para: <pasta da área ou "nenhuma">
  ```
- A resposta vai para `registro/avaliacoes/<área>/CT-nn.md`.

## 4. Pontuação (`--pontuar`)
| Parte | Peso | Como |
|---|---|---|
| Conteúdo | 50 | fração dos pontos de "Deve conter" atendidos |
| Limpeza | 30 | começa em 30; −15 por termo proibido do caso; −15 por alerta ALTO e −8 por MÉDIO do auditor de promessas |
| Encaminhamento | 20 | caso da própria área: 20 se "Área que responde" é ela (consultar outra área é permitido). Fronteira: 20 se a área certa está em "Encaminhar para" ou em "Área que responde"; 10 se só aparece no texto |

- **Citação recusada não conta:** termo proibido entre aspas numa linha que proíbe, com negação antes ou recusa logo depois ("'recupere 5 anos' não pode sair"). Expressões técnicas (seguro garantia, dívidas garantidas, compensação de ofício) e "alíquota zero só via PER, nunca DCOMP" não contam como alerta do auditor de promessas (calibração do piloto de 23/10/2026).
- **Falha crítica:** termo proibido do caso ou alerta ALTO do auditor limita o caso a 49.
- Caso **aprovado** com 70 ou mais. **Acerto da área** = média dos casos respondidos.
- O relatório sai em `registro/avaliacoes/relatorio-<data>.md` (e `.json`, que o auditor de senioridade lê).

## 5. Ritmo
- Rodada completa toda sexta, dentro da `consolidacao-semanal` (sugestão de passo em `skills/arquiteto-agentes`).
- Caso que a área erra duas semanas seguidas vira correção no especialista (método, armadilha ou caso de referência), com revisão do gerente.
- Casos novos entram quando a operação gera um erro real (reclamação, revisão com ajuste, retrabalho). Um caso não é apagado: se a regra mudar, ele ganha versão nova com a fonte da mudança.
