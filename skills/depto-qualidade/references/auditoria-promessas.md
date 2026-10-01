# Auditoria de Promessas Comerciais (v1, 29/09/2026)

**Por que existe:** a Save vende um serviço com risco tributário (análise, PER, possível glosa). Toda frase que promete valor, êxito ou prazo cria expectativa que a Save não controla: vira reclamação (tema A3), pode vincular a oferta (CDC art. 30; Código Civil art. 427), pode ser publicidade enganosa (CDC art. 37, §1º) e, se a Save atuar como sociedade de advogados, fere o Código de Ética da OAB e o **Provimento CFOAB 205/2021** (vedação de promessa de resultado, de casos concretos para oferta, de referência a honorários/gratuidade/forma de pagamento e de expressões persuasivas ou de autoengrandecimento). O contrato com parceiros prevê proibição de publicidade que prometa resultado (`depto-juridico/references/riscos-chave.md`).

## Fronteira com as outras áreas (sem sobreposição)
| Quem | Quando atua | O que faz |
|---|---|---|
| **Revisor de Marca & Compliance** (depto-marketing) | **Antes** de publicar, em toda peça que o **Marketing** produz | 1ª linha: tom, identidade, proibições da marca |
| **Revisor de Promessas & Compliance** (depto-partner-success) | Antes de entregar trilhas, quizzes e materiais da Academia | 1ª linha dentro do Partner Success |
| **Qualidade — Auditoria de Promessas** (este) | (a) material que **não passa** pelo Marketing: propostas, mensagens de WhatsApp/e-mail do time e das células, modelos de mensagem, anexos de diagnóstico, materiais feitos pelos parceiros; (b) **auditoria por amostragem depois** (2ª linha), inclusive de peças já aprovadas; (c) **origem** de reclamação A3 | Detecta, mede e aponta a causa; **mantém a lista de regras** (`regras-promessas.json`) que os revisores de 1ª linha podem usar |
| **Compliance Ético & Marketing Jurídico** (depto-juridico) | Quando há dúvida de interpretação ou um alerta ALTO recorrente | Interpreta a norma e decide se pode; é a palavra final (com o advogado humano) |

Em uma frase: **os Revisores aprovam antes; a Qualidade confere depois e onde ninguém revisa; o Jurídico interpreta.** O script é compartilhável: o Revisor do Marketing pode rodá-lo, mas a lista de regras tem um dono só (Qualidade), para não divergir.

## Categorias de risco (detalhe no JSON) <!-- auditoria:ignorar -->
| Regra | Categoria | Severidade | Exemplos que o script marca |
|---|---|---|---|
| P1 | Promessa de êxito | 🔴 ALTO | "garantido", "garante", "assegura", "100% de êxito", "com certeza você vai receber" |
| P2 | Ausência de risco | 🔴 ALTO | "sem risco", "risco zero", "a Receita não questiona", "totalmente seguro", "blindado" |
| P3 | Promessa de valor | 🟠 MÉDIO | "recupere até R$ 500 mil", "você tem R$ X", "redução das contribuições entre 0,9 e 1,5%" |
| P4 | Promessa de prazo | 🟠 MÉDIO | "dinheiro na conta em 30 dias", "restituição imediata" |
| P5 | Mercantilização | 🟠/🟡 | "sem custo", "só paga se ganhar", "sem desembolso"; urgência artificial ("última chance") |
| P6 | Autoengrandecimento | 🟡 BAIXO | "somos a maior", "líder do mercado", "número 1 do Brasil" |
| P7 | Certeza jurídica | 🟠/🟡 | "tese pacificada", "o STF garantiu"; "direito líquido e certo" (BAIXO: termo técnico) |
| P8 | Caso concreto | 🟠 MÉDIO | "nosso cliente recuperou R$ 2 mi", "case de sucesso" |
| P9 | Pressão | 🟡 BAIXO | "você está perdendo dinheiro", "dinheiro parado" |

O script também reconhece:
- **Ressalva** (✅): termo negado ("não garantimos") não gera alerta.
- **Texto sobre a regra** (⚪ INFO): linhas como "Proibido: 'garantido'" ou seções "## Proibido" (manuais, skills) não contam como risco.
- **Alerta de documento** (⚠️): há promessa de êxito/valor/prazo e **nenhuma** ressalva no documento ("sujeito à análise", "não há garantia de resultado", "estimativa preliminar").

## Como rodar
```
python3 ~/.claude/skills/depto-qualidade/scripts/auditar_texto.py <arquivo ou pasta> \
   --saida ~/agentes-partners/departamentos/qualidade/auditorias/AAAA-MM-DD-<tema>.md \
   --marcado ~/agentes-partners/departamentos/qualidade/auditorias/marcados
```
- Aceita `.md`, `.txt` e `.docx` (lê corpo, tabelas, cabeçalho, rodapé, notas e comentários). Não altera o original.
- `--resumo`: só contagens, sem trechos → **use em material com dados de clientes** (pareceres, anexos), LGPD.
- `--json`: para outros scripts. Código de saída 1 = há ALTO/MÉDIO.
- Texto colado no chat (WhatsApp, proposta): salve em um `.txt` temporário no scratchpad e rode; não guarde a conversa na pasta de Qualidade.

## Como ler e o que entregar
1. O script **marca**; o auditor (agente) **julga o contexto**: citação, pergunta, negação que o script não pegou, termo técnico em parecer jurídico. Registre o falso positivo em `aprendizados.md` e proponha o ajuste da regra.
2. Para cada ALTO/MÉDIO real: trecho, por que é risco, **reescrita sugerida** (sem mudar o sentido comercial) e quem precisa aprovar a reescrita (Marketing para peça; Técnico para afirmação tributária; Jurídico para honorário/forma de pagamento).
3. **Modelo recorrente** (o mesmo texto em muitos documentos) vale mais que um caso isolado: corrija na origem (o modelo), não documento por documento.
4. O script não entende sentido. Ele **não substitui** a leitura humana do material e não pega promessa feita com outras palavras ("pode contar com esse dinheiro"). Amplie as regras quando aparecer um caso novo.

## Amostragem da auditoria de 2ª linha (proposta)
Mensal: 10 mensagens de WhatsApp/e-mail enviadas a parceiros/clientes (coladas pelo time, pseudonimizadas), todos os modelos novos das células, todas as peças novas do Marketing do mês e 5% dos anexos de diagnóstico emitidos. Indicador: **% de materiais sem ALTO/MÉDIO** e tempo até corrigir o modelo.
