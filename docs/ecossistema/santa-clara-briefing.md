# Cooperativa Santa Clara · briefing da conversa própria (21/10/2026)

Abra a conversa nova lendo este arquivo, o `CLAUDE.md` da raiz e a seção 13 de `~/agentes-partners/gabinete/SESSOES.md`. O tema da conversa é **só a apresentação à Cooperativa Santa Clara**, dentro do fluxo de agentes da Área Partners.

## Objetivo (roteiro do Luis)
Apresentação à presidência da cooperativa com foco em **mais lucro e mais margem** em todo o ecossistema: campo, laticínios, frigorífico, rações, varejo, lojas agropecuárias e logística. A ordem do roteiro é esta:
1. dados de mercado;
2. dificuldades do setor, com fontes oficiais;
3. espelho na cooperativa;
4. como a Save ajuda;
5. resultados possíveis.

## O que já existe (feito na sessão do Ecossistema, na nuvem, e juntado ao `main` em 21/10)
| Peça | Onde |
|---|---|
| Deck "Ecossistema Santa Clara" v2: mercado, dificuldades, espelho, ajuda, resultados | `skills/apresentacao-diagnostico/scripts/gerar_deck_santa_clara_ecossistema.js` (entrada: `deck_dados_v2.json`) |
| Deck comercial da Save: esteira de 12 passos aplicada ao ecossistema | `skills/apresentacao-diagnostico/scripts/gerar_deck_comercial_santa_clara.js` |
| Dados oficiais (IBGE, BCB, MDIC, Plano Safra, Receita) | `docs/ecossistema/dados-estudo/santa-clara-dados-oficiais.json` |
| Esteira para o cliente (12 passos em 3 movimentos), roteiro de conversa com o empresário, modelo do gestor de esteira | `docs/ecossistema/` e `skills/depto-solucoes/scripts/gerar_esteira_cliente.py` |
| Última versão gerada do PowerPoint | OneDrive `00 · Entrada/deck-santa-clara.pptx` (21/10, 11h13) |

O `deck_dados_v2.json` não está no repositório. Se a conversa precisar dele, regere a partir de `santa-clara-dados-oficiais.json` ou peça à sessão do Ecossistema que faça o push.

## Como os agentes trabalham nesta conversa
- **Dono da conta:** `depto-solucoes` (modo A2, dossiê de conta) com a esteira **Destravar caixa → Proteger e controlar → Crescer**.
- **Deck:** `apresentacao-diagnostico`, no Design System Save (`pptx_save.js`).
- **Revisão obrigatória antes de chegar ao Luis, por área:**
  - Tributário: teses do agro e cooperativa, ato cooperativo, Funrural (ADI 4.395), crédito presumido do leite (Lei 10.925), LC 224/2025.
  - Jurídico.
  - Produtos Internacionais: Crédito Internacional e Maquila, só como descoberta.
  - Resultados e Dados: números e fontes.
  - Qualidade, com o `auditar_texto.py`.
  - Marketing: narrativa e layout.
- **Estado dos produtos (Luis, 19/10):**
  - prontos: Gestão de Contas, antecipação e FIDC (Save Invest), estruturação patrimonial e tax internacional;
  - em validação com o João: Crédito Internacional, captação, home equity e Maquila.
- **Exemplo antes da versão final:** mostre ao Luis um PNG dos slides principais antes de gerar o PowerPoint inteiro.
- Sem promessa de valor, prazo ou êxito. Valor só em faixa, com premissa. Não citar clientes da Save.

## Pontos a confirmar com o Luis no início
- Data e formato da reunião (presencial ou online, tempo de fala).
- Quem estará na sala, além da presidência.
- Dados internos da cooperativa que já temos (CNPJ ou CNPJs, faturamento, parecer ou diagnóstico da Save, Master envolvido).
- Qual das duas versões do deck é a base (a de ecossistema v2 ou a comercial da esteira) e se vira uma só.

## Ao terminar
Publique em `06 · Marketing e Apresentações` no OneDrive, com o link da pasta. Atualize a seção 13 do guia de sessões. Faça commit na branch da conversa e avise o Luis para dar o merge.
