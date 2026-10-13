# Padrão visual Save (Design System Save v0.5)

Layout oficial de tudo o que a Área Partners produz, definido pelo Luis em 07/10/2026. A origem é o pacote do Marketing, guardado em `../design-system/`.

| Formato | Use |
|---|---|
| Valores (cores, fontes, logos) | `marca.json`, a fonte única. Python: `lib/marca.py` |
| Word (.docx) | `departamentos/produtos/credito-internacional/scripts/gerar_manual_docx.js`, que embute a IBM Plex Sans |
| PowerPoint (.pptx) | `pptx_save.js`: masters SAVE_CAPA, SAVE_CLARO e SAVE_ESCURO, mais `titulo()`, `kpi()` e as cores de gráfico |
| PDF e peças (HTML → Playwright) | `save.css` ou `lib/marca.py` (`marca.css_base()`, `marca.logo_uri()`) |
| Web e aplicativo | `save.css` (HTML puro) ou `tailwind-preset.js` (Next.js, React, NativeWind) |
| E-mail | `skills/depto-marketing/scripts/email_layout.py` |

## Regras
- **Fonte:** IBM Plex Sans para tudo. Use IBM Plex Mono para números, códigos e rótulos curtos. Não use serifa.
- **Cor:** o ouro é a única cor cromática.
  - Use `#F3CD60` em faixas, selos, botões e no modo escuro.
  - Para texto em ouro sobre fundo claro, use sempre `#B58A1F`.
- **Material para cliente ou parceiro:** modo claro, com texto `#0F1115` sobre branco ou `#F6F7F9`.
- **Painéis, capas e divisórias:** modo escuro, com fundo `#000000` e cartões `#171717`.
- **Logo:** `logo-save-fundo-claro.png` vai no fundo claro e `logo-save-fundo-escuro.png` no escuro. A marca é **Save Co.**; não se criam submarcas.
- **Raios e espaçamento:** raios de 4 a 24 px, nunca acima de 24. Espaçamento na base 4. Área de toque mínima de 44×44 no celular.
- **Sinalização:** cor nunca é o único sinal. Não use emoji, mascote ou tom de chatbot.

## Fontes
As fontes estão em `fontes/` (licença OFL) e também na pasta "Área Partners · Agentes/Marca/Fontes IBM Plex" do OneDrive.
- **Word:** a fonte vai embutida no arquivo.
- **PowerPoint:** quem abrir o arquivo precisa ter a fonte instalada.
- **Web:** a fonte é carregada do Google Fonts.
