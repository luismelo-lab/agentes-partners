---
name: apresentacao-diagnostico
description: 'Apresentação do Diagnóstico: transforma o diagnóstico tributário revisado no deck ao cliente (PDF e PowerPoint no padrão Save), com narrativa, objeções do empresário, case do segmento, esteira Destravar caixa → Proteger e controlar → Crescer e revisão de promessas. Use para deck do diagnóstico, apresentar o diagnóstico, case por segmento, objeção do cliente.'
---

## Quando usar (gatilhos completos)
Transforma um diagnóstico tributário pronto (PDF "Proposta de serviços de revisão tributária") na apresentação padrão ao cliente, depois de o time tributário avaliar cada tese (item de linha) e alterar o que não se sustenta. Gera PDF e PowerPoint no Design System Save, com o slide "Destravar caixa, proteger e controlar, crescer" (D1, 21/10; antes "Oxigenar, estruturar e escalar") (modelo Canex, com os produtos financeiros do ecossistema) e o case do segmento buscado na biblioteca de cases. Use quando o Luis ou a Geovana falarem em apresentação do diagnóstico, "deck do diagnóstico", "apresentar o diagnóstico da empresa X", revisão das teses do diagnóstico antes de ir ao cliente, case por segmento, ou "oxigenar, estruturar e escalar" (nome antigo da esteira), "destravar caixa, proteger e controlar, crescer". Equipe sênior: Roteirista de Narrativa Executiva (Pyramid Principle, SCQA, informativo × proposta), Especialista em Objeções do Empresário (dono, CFO, contador, com base técnica), Curador de Cases (anonimização N0–N3, prova, OAB, LGPD) e Revisor de Promessas da Peça (auditor, rodapé, 9 avisos, D82, trava G2). Use também quando falarem em roteiro ou storyline do deck, "o que dizer na reunião", objeção do cliente ("a Receita vai me fiscalizar", "meu contador já fez", "e se perder no STJ", "não quero DCOMP"), case do segmento ou autorização de logo, ou revisão de promessas e linguagem do deck.


# Apresentação de diagnóstico (padrão Save)

Leia `~/agentes-partners/departamentos/tributario/apresentacao-diagnostico/FLUXO.md` e o `MODELO-OXIGENAR-ESTRUTURAR-ESCALAR.md` antes de começar. Tudo é pré-análise: nada vai ao cliente sem a aprovação do técnico do caso e da dona da entrega (Daniela, que conduz com o Master); o Luis aprova quando o deck sai do modelo aprovado (slide novo, case nominal ou com logo, produto em validação, honorário, tese fora da vitrine), quando o crédito passa de R$ 1 mi ou quando o material vai em escala (aí ele vê o exemplo) (alçada de 23/10/2026, `infra/alcadas.md`). Português do Brasil.


## Equipe sênior (padrão de 22/10/2026, `infra/padrao-senior.md`)
O gerente distribui pelo arquivo do especialista; entrega que não usa o método do arquivo volta.
| Especialista | Entrega única | Arquivo |
|---|---|---|
| Roteirista de Narrativa Executiva | Roteiro do deck: resposta em 1 frase, SCQA, ghost deck com títulos-conclusão, notas de fala, leitura por persona | `references/especialistas/narrativa-executiva.md` |
| Especialista em Objeções do Empresário | Mapa de objeções do caso com resposta técnica (Tema 736, EREsp 2.215.482, PER × DCOMP, Lei 14.873/2024, art. 168 do CTN, reforma 2027, êxito) | `references/especialistas/objecoes-empresario.md` |
| Curador de Cases | Ficha de case aprovada ou vetada (prova, data-base, N0–N3, LGPD, OAB) | `references/especialistas/curador-cases.md` |
| Revisor de Promessas da Peça | Parecer de linguagem slide a slide (auditor + passada humana, rodapé, 9 avisos, D82, D83, D88, trava G2) | `references/especialistas/revisor-promessas-peca.md` |
O veredito técnico de cada tese (MANTER, AJUSTAR, RETER ATÉ VALIDAR, RETIRAR) continua com o time tributário (passo 2). Perguntas que só o dono responde: `references/perguntas-ao-dono.md`.

**Ordem no fluxo:** passo 2 (Tributário) → Roteirista (antes do `deck.json`) → Objeções (notas de fala) e Curador (slide de case) em paralelo → `deck.json` e render → Revisor de Promessas → `depto-qualidade` → aprovação (técnico e dona da entrega; Luis só nos casos da alçada, acima).

## Fluxo

1. **Ler o diagnóstico** (o `.md` da pasta `00 · Entrada` costuma ser PDF; use `pypdf`). Pegar cliente, CNPJ, período, teses com valor, processos e a frase sobre débitos. Confirmar CNAE, regime, porte e UF na base da Receita (`depto-intel-comercial/scripts/receita_cnpj.py`, função `q` com `VIEW`).
2. **Time tributário em paralelo** (ferramenta Agent, `general-purpose`), com briefing curto de 1 página (modelo: o da Brassol em `departamentos/tributario/entregas/2026-10-14-brasol-*.md`): (a) PIS/COFINS e ICMS, linha a linha; (b) Previdenciário, passivo e processos já ajuizados; (c) segmento, reforma e o slide Oxigenar/Estruturar/Escalar; (d) Jurídico, só quando houver conteúdo novo (o parecer-padrão de 14/10 já vale). Vetos e regras do `revisor-diagnostico` (V1–V15, insumo no comércio, Temas 1093/1231) aplicam-se. Vereditos: MANTER, AJUSTAR, RETER ATÉ VALIDAR, RETIRAR.
3. **Montar `diagnostico.json`** em `departamentos/tributario/apresentacao-diagnostico/<cliente>/` a partir de `modelo-diagnostico.json` (o da Brassol). Só entra o que passou na revisão. Valor só onde há base; nunca somar linhas que se sobrepõem. Escolher os itens de Oxigenar/Estruturar/Escalar pelas perguntas do modelo e pelos critérios dos produtos financeiros (FIDC acima de R$ 10 mi/mês; funding acima de R$ 60 mi de ativos; Gestão de Contas se houver contas a receber/vencidos altos); são fala do Junior e do João em 13/10/2026, sem D-número: servem para escolher o item, nunca para escrever no slide, ver `revisor-promessas-peca.md`).
4. **Gerar (padrão comercial, com imagens):** escrever `deck.json` na pasta do cliente (modelo: `brasol/deck.json`; tipos: capa, imagem, numeros, valores, painel, grade, banner, timeline, roadmap, passos; use painel (foto do PowerPoint à esquerda) e valores (valor total e barras por tese)) e rodar `python3 departamentos/tributario/apresentacao-diagnostico/render_comercial.py <pasta>`. Usa fotos e slides da apresentação institucional (`assets-institucionais/`, extraídos do PowerPoint com `extrair_assets_pptx.py`). Antes de entregar, passe o deck pelos times (tributário, inteligência de negócio, jurídico, marketing/vendas) e aplique as edições. Separe o INFORMATIVO (o que o cliente já fez, ex. ações na Justiça) da PROPOSTA (o que a Save levantou, com R$ por tese do diagnóstico, marcado como potencial a validar). Linguagem de venda: o slide mostra **como a Save ajuda o cliente** com cada produto, não como o produto funciona. Teses no catálogo `departamentos/tributario/catalogo-teses-save.md`. A versão técnica em layout claro continua em `gerar_apresentacao.py`. Corrigir qualquer aviso de layout. Conferir a folha de contato (`marketing/kit/motor/folha_contato.py`) só na entrega final.
5. **Case do segmento:** vem de `biblioteca-cases/cases.json` (só aprovado; `--rascunho` inclui o não aprovado, marcado). Quando o Luis enviar cases, cadastrar seguindo o `README.md` da pasta (anonimizado, com data-base e fonte).
6. **Entrega:** PDF e PowerPoint na pasta do cliente em `06 · Marketing e Apresentações` do OneDrive, mais `REVISAO-time-tributario.md` (uso interno: antes × depois de cada linha). Resposta final com o link de cada arquivo.

Regras de texto: sem valor de mercado, offshores ou preço; "estruturação patrimonial" em vez de "holding"; sem "garantia"; rodapé de pré-análise e êxito; estatística de mercado não é dado Save; os movimentos chamam-se Destravar caixa, Proteger e controlar e Crescer (D1, 21/10). Requer `pptxgenjs` em `~/.partners-node/node_modules` (ou NODE_PATH) e Playwright.

## Revisão do Gerente (obrigatória, regra do Luis de 15/10/2026)
Siga `~/agentes-partners/infra/protocolo-gerente.md`.
- **Distribuir:** o gerente desta área distribui o trabalho aos especialistas certos.
- **Revisar:** antes de qualquer retorno, o gerente revisa pelo checklist do protocolo:
  - responde o pedido;
  - entrega os 3 blocos de `infra/padrao-entrega.md`;
  - está correto e pronto para usar;
  - segue as regras da casa;
  - diz se precisa de outra área.
- **Devolver:** se algo falhar, devolve ao especialista responsável com o que corrigir e reavalia, no máximo 2 rodadas. Se ainda faltar algo, a lacuna vai em "o que falta e quem fornece".
- **Outra área:** se a demanda precisar dela, o gerente encaminha ao gerente da outra área. Lá, o gerente distribui aos especialistas e revisa da mesma forma. Depois, o gerente desta área faz a revisão final e consolida uma resposta única.
- **Registro:** toda entrega leva o registro `"revisao": {gerente, especialistas, rodadas, areas_consultadas, aprovado, ajustes}`.

## Pesquisa e atualização (padrão Big Four, regra do Luis de 16/10/2026)
Siga `~/agentes-partners/infra/protocolo-pesquisa.md`. Não se limite ao material compartilhado.
- **Quatro camadas, em ordem:** base interna (`references/`, aprendizados, decisões) · dados da Save por script · radar da área (`depto-tributario/references/radar-mercado.md` e o radar comercial (`depto-partner-success/references/radar-mercado.md`)) · pesquisa na hora (WebSearch/WebFetch via ToolSearch) quando o tema envolve norma, julgado, taxa, número de mercado ou concorrente, ou quando o radar tem mais de 7 dias.
- **Recência:** toda afirmação de mercado leva a data da informação e a data da consulta; norma com vigência conferida no dia; fonte primária oficial acima de Big Four, escritórios e imprensa (que servem de benchmark e pista).
- **Visão Big Four:** pergunta de negócio → situação, implicação e recomendação · faixa quantificada com premissas · alternativa de mercado e benchmark · risco explícito · lente do setor · próximo passo com dono e prazo.
- **Conflito com a base interna:** a decisão da Save continua valendo; sinalize no bloco "o que você também precisa" e proponha a pergunta ao dono.
- **Registro:** o log da entrega lista as fontes externas (com data), a idade do radar usado e os conflitos encontrados.
