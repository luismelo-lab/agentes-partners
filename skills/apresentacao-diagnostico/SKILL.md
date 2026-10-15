---
name: apresentacao-diagnostico
description: Transforma um diagnóstico tributário pronto (PDF "Proposta de serviços de revisão tributária") na apresentação padrão ao cliente, depois de o time tributário avaliar cada tese (item de linha) e alterar o que não se sustenta. Gera PDF e PowerPoint no Design System Save, com o slide "Oxigenar, estruturar e escalar" (modelo Canex, com os produtos financeiros do ecossistema) e o case do segmento buscado na biblioteca de cases. Use quando o Luis ou a Geovana falarem em apresentação do diagnóstico, "deck do diagnóstico", "apresentar o diagnóstico da empresa X", revisão das teses do diagnóstico antes de ir ao cliente, case por segmento, ou "oxigenar, estruturar e escalar".
---

# Apresentação de diagnóstico (padrão Save)

Leia `~/agentes-partners/departamentos/tributario/apresentacao-diagnostico/FLUXO.md` e o `MODELO-OXIGENAR-ESTRUTURAR-ESCALAR.md` antes de começar. Tudo é pré-análise: nada vai ao cliente sem a aprovação do Luis e do técnico. Português do Brasil.

1. **Ler o diagnóstico** (o `.md` da pasta `00 · Entrada` costuma ser PDF; use `pypdf`). Pegar cliente, CNPJ, período, teses com valor, processos e a frase sobre débitos. Confirmar CNAE, regime, porte e UF na base da Receita (`depto-intel-comercial/scripts/receita_cnpj.py`, função `q` com `VIEW`).
2. **Time tributário em paralelo** (ferramenta Agent, `general-purpose`), com briefing curto de 1 página (modelo: o da Brassol em `departamentos/tributario/entregas/2026-10-14-brasol-*.md`): (a) PIS/COFINS e ICMS, linha a linha; (b) Previdenciário, passivo e processos já ajuizados; (c) segmento, reforma e o slide Oxigenar/Estruturar/Escalar; (d) Jurídico, só quando houver conteúdo novo (o parecer-padrão de 14/10 já vale). Vetos e regras do `revisor-diagnostico` (V1–V15, insumo no comércio, Temas 1093/1231) aplicam-se. Vereditos: MANTER, AJUSTAR, RETER ATÉ VALIDAR, RETIRAR.
3. **Montar `diagnostico.json`** em `departamentos/tributario/apresentacao-diagnostico/<cliente>/` a partir de `modelo-diagnostico.json` (o da Brassol). Só entra o que passou na revisão. Valor só onde há base; nunca somar linhas que se sobrepõem. Escolher os itens de Oxigenar/Estruturar/Escalar pelas perguntas do modelo e pelos critérios dos produtos financeiros (FIDC acima de R$ 10 mi/mês; funding acima de R$ 60 mi de ativos; Gestão de Contas se houver contas a receber/vencidos altos).
4. **Gerar (padrão comercial, com imagens):** escrever `deck.json` na pasta do cliente (modelo: `brasol/deck.json`; tipos: capa, imagem, numeros, grade, banner, lateral, timeline, roadmap, passos) e rodar `python3 departamentos/tributario/apresentacao-diagnostico/render_comercial.py <pasta>`. Usa fotos e slides da apresentação institucional (`assets-institucionais/`, extraídos do PowerPoint com `extrair_assets_pptx.py`). Antes de entregar, passe o deck pelos times (tributário, inteligência de negócio, jurídico, marketing/vendas) e aplique as edições. Linguagem de venda: o slide mostra **como a Save ajuda o cliente** com cada produto, não como o produto funciona. Teses no catálogo `departamentos/tributario/catalogo-teses-save.md`. A versão técnica em layout claro continua em `gerar_apresentacao.py`. Corrigir qualquer aviso de layout. Conferir a folha de contato (`marketing/kit/motor/folha_contato.py`) só na entrega final.
5. **Case do segmento:** vem de `biblioteca-cases/cases.json` (só aprovado; `--rascunho` inclui o não aprovado, marcado). Quando o Luis enviar cases, cadastrar seguindo o `README.md` da pasta (anonimizado, com data-base e fonte).
6. **Entrega:** PDF e PowerPoint na pasta do cliente em `06 · Marketing e Apresentações` do OneDrive, mais `REVISAO-time-tributario.md` (uso interno: antes × depois de cada linha). Resposta final com o link de cada arquivo.

Regras de texto: sem valor de mercado, offshores ou preço; "estruturação patrimonial" em vez de "holding"; sem "garantia"; rodapé de pré-análise e êxito; estatística de mercado não é dado Save; terceira etapa chama-se Escalar. Requer `pptxgenjs` em `~/.partners-node/node_modules` (ou NODE_PATH) e Playwright.

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
