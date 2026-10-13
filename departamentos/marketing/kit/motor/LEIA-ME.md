# Motor de apresentações e peças · Save Co.

O mesmo conteúdo em JSON gera o PDF (via HTML) e o PowerPoint editável, os dois no Design System Save v0.5.

```bash
python3 deck_html.py conteudo.json saida.pdf previas/   # PDF + prévias PNG + aviso de texto que passa do slide
NODE_PATH=<node_modules com pptxgenjs> node deck_pptx.js conteudo.json saida.pptx
python3 folha_contato.py previas/ contato.png            # conferência visual
python3 pecas.py pecas.json pasta_saida/                 # folder, flyer e WhatsApp
```

## JSON da apresentação

```json
{ "titulo_doc": "...", "rodape": "aviso legal curto", "slides": [ { "tipo": "...", ... , "notas": "roteiro do apresentador" } ] }
```

- Texto aceita `**negrito**`.
- Todo slide aceita `notas`, o roteiro do apresentador. No PowerPoint elas viram notas do orador.
- Slides claros aceitam `rotulo` (mono, em ouro), `titulo` (título-conclusão, até cerca de 85 caracteres), `subtitulo`, `nota` e `fonte`.

| tipo | campos | uso |
|---|---|---|
| `capa` | rotulo, titulo, subtitulo, linha | Capa preta. O título tem até cerca de 70 caracteres |
| `secao` | numero, titulo, texto | Divisória preta |
| `frase` | rotulo, texto (com **destaque** em ouro), apoio | Frase de impacto em fundo preto. A tese |
| `afirmacao` | paragrafos[] (2 a 3), destaque{valor, legenda, fonte} | Argumento com um número grande |
| `numeros` | itens[]{valor, unidade, legenda, fonte} (2 a 4) | Números grandes lado a lado |
| `barras` | itens[]{rotulo, valor (número), texto, destaque}, fonte | Comparativo de custo ou tamanho. O item `destaque` sai em ouro |
| `comparativo` | colunas[2], linhas[]{criterio, a, b} (até 6) | Mercado (a) contra Save (b). A coluna b fica destacada |
| `pares` | colunas[2], itens[]{pergunta, resposta} (até 6) | Objeções, perguntas e respostas, riscos e tratamento |
| `fluxo` | etapas[]{titulo, texto, quem, destaque} (4 a 6), escuro | Processo passo a passo |
| `pilares` | itens[]{titulo, texto} (3 ou 4), escuro | Diferenciais ou papéis |
| `duas_colunas` | esquerda{titulo, itens[]}, direita{titulo, itens[]} (até 5 cada) | Antes e depois, ou hoje e com a Save. A direita sai em preto |
| `diagrama` | nos[]{titulo, texto, destaque} (3 ou 4), setas[]{cima, baixo} | Estrutura: quem faz o quê |
| `caso` | linhas[]{rotulo, texto} (4 a 8, em pares) | Caso de referência ou caso ilustrativo |
| `fechamento` | rotulo, titulo, passos[] (2 a 4), contato | Próximos passos em fundo preto |

**Limites para caber:**
- Item de lista: até cerca de 90 caracteres.
- Texto de etapa ou pilar: até cerca de 150 caracteres.
- Parágrafo: até cerca de 260 caracteres.
- O `deck_html.py` avisa "slide N: passa Xpx" quando algo não cabe. Se aparecer, corte o texto.

## JSON das peças (`pecas.json`: folder, flyer e WhatsApp)

Todas as peças são opcionais: o motor gera só as que estiverem no arquivo. Os limites de caracteres são o espaço da arte.

```json
{ "id": "cafe", "area": "Crédito Internacional · Café", "rodape": "aviso legal curto",
  "fluxo": { "titulo": "(até 60)", "etapas": [ { "titulo": "(até 26)", "quem": "(até 22)", "texto": "(até 70)", "destaque": false } ] },
  "flyer": { "rotulo": "", "titulo": "(até 60)", "subtitulo": "(até 130)",
             "numero": { "valor": "", "unidade": "", "legenda": "(até 70)", "fonte": "" },
             "beneficios": [ { "titulo": "(até 30)", "texto": "(até 90)" } ],
             "perfil_titulo": "Para quem é", "perfil": [ "(até 60)" ], "cta": "(até 70)" },
  "folder": { "capa": {}, "problema": {}, "solucao": {}, "comparativo": {}, "perfil": {}, "nao_fazemos": {}, "contato": {} },
  "whatsapp": { "rotulo": "", "titulo": "(até 55)", "numero": { "valor": "", "legenda": "(até 70)", "fonte": "" }, "fecho": "(até 50)" },
  "mensagem": "texto de envio" }
```

**O fluxo** tem exatamente 5 etapas e aparece nas três peças:
- no flyer, como uma faixa horizontal;
- no folder, como uma linha do tempo no painel "Como funciona";
- no WhatsApp, como uma lista compacta.

Quando o arquivo traz o `fluxo`, o motor ignora os campos antigos `flyer.passos`, `folder.processo` e `whatsapp.pontos`. O fluxo das peças deve ser o mesmo da apresentação do mesmo kit.

**Quantidades:**
- `beneficios`: 3 itens;
- `perfil`: 4 itens;
- `folder.problema.numeros`: 2 itens;
- `folder.solucao.beneficios`: 4 itens;
- `folder.comparativo.linhas`: 5 itens;
- `folder.perfil.itens`: 5 itens;
- `folder.nao_fazemos.itens`: 4 itens.

## Ferramentas de consultoria (tipos de slide adicionados em 08/10/2026)

| tipo | campos | uso |
|---|---|---|
| `cascata` | unidade, itens[]{rotulo, valor, tipo: base, delta ou total, texto} | Ponte em cascata (*waterfall*): explica a passagem de um número a outro |
| `matriz` | eixo_x{rotulo, baixo, alto}, eixo_y{…}, quadrantes[4], quadrante_destaque (de 0 a 3), itens[]{nome, x, y (de 0 a 1), destaque} | Matriz 2×2: impacto × esforço, atratividade × capacidade (GE/McKinsey) ou Ansoff |
| `calor` | colunas[], linhas[]{nome, valores[], textos[]}, legenda | Mapa de calor: potencial e espaço em branco (*whitespace*) Masters × produtos |
| `organograma` | raiz{titulo, texto}, grupos[]{titulo, texto, itens[]{titulo, texto}} | Organograma com 3 a 5 grupos e até 4 itens por grupo |
| `tabela` | colunas[] (até 6), linhas[][] (até 7), destaque_coluna | Tabela genérica, com uma coluna destacada |

O briefing com os exemplos completos está em `departamentos/resultados/brainstorm-2027/BRIEFING.md`.
