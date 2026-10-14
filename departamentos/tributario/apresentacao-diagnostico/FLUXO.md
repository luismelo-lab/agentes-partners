# Fluxo: diagnóstico pronto → apresentação ao cliente

Padrão definido pelo Luis em 14/10/2026. Base visual e de conteúdo: a apresentação institucional da Save (`06 · Marketing e Apresentações/APRESENTAÇÃO BRASSOL.pdf` e `00 · Entrada/01. Save Co. (1).pptx`). Aqui a base vira **apresentação do diagnóstico**, no Design System Save v0.5 (capa e fechamento em preto, miolo claro, como é cliente), pelo motor do Marketing.

## Etapas

| # | Quem | O que faz | Saída |
|---|---|---|---|
| 1 | Técnico (Marcos) | Fecha o diagnóstico (PDF "Proposta de serviços de revisão tributária") | PDF em `00 · Entrada` |
| 2 | Gabinete | Lê o PDF e monta `diagnostico.json` (cliente, CNAE, teses, processos, passivo) | `diagnostico.json` na pasta do cliente |
| 3 | **Time tributário** (`depto-tributario`, em paralelo) | Avalia **cada linha de tese** para o perfil do cliente: PIS/COFINS e ICMS; Previdenciário, passivo e processos; segmento e reforma. Veredito por linha: MANTER · AJUSTAR · RETER ATÉ VALIDAR · RETIRAR, com base legal, risco e documento que decide | `departamentos/tributario/entregas/AAAA-MM-DD-<cliente>-*.md` |
| 4 | Jurídico | Confere promessas, números, avisos e o uso de cases (parecer-padrão em `juridico/entregas/2026-10-14-padrao-apresentacao-diagnostico-compliance.md`) | Ajustes de texto |
| 5 | Gabinete | Preenche `diagnostico.json` só com o que passou na etapa 3: tese retirada sai; tese retida mostra "a validar", sem valor; **nunca soma o total do 1º relatório** se houver sobreposição | `diagnostico.json` revisado |
| 6 | Gabinete | `python3 gerar_apresentacao.py <pasta> [--rascunho]` → PDF, PowerPoint editável e prévias; busca o **case do segmento** na biblioteca | `<Cliente>-Apresentacao.pdf/.pptx` |
| 7 | Luis / Geovana | Aprova. Nada vai ao cliente nem ao parceiro sem a aprovação | Envio pelo Luis |

## Esqueleto da apresentação (13 slides)
Capa · Quem é a Save · Como chegamos aqui · Resumo · **Teses revisadas** · **Processos já ajuizados** · Débitos em aberto · Reforma tributária · **Oxigenar, estruturar e escalar** · **Quem já fez (case do segmento)** · Jornada · O que precisamos de vocês · Próximos passos.
Os blocos em negrito mudam em todo diagnóstico; os demais são a base fixa. Slides que o diagnóstico não justifica saem (ex.: sem passivo, sem processo).

## Regras de conteúdo (do parecer do Jurídico e da revisão tributária)
- Sem valor de mercado, "offshores", "estruturas preservadas" e preço de honorário ou de serviço.
- "Holding" vira **estruturação patrimonial**. Sem "garantia", sem "você só paga o que é devido".
- Valor só onde há base confirmada; resto "a validar". Faixas de resultado ("2% a 8%") não entram.
- Case anonimizado e agregado, sem logo nem nome de cliente; valor "reconectado" só com definição e data-base.
- Rodapé fixo: pré-análise sujeita a validação técnica e jurídica; êxito sem desembolso inicial; resultados passados não garantem futuros.
- Estatística de mercado nunca aparece como dado da Save.

## Oxigenar, estruturar e escalar
Modelo do slide e perguntas do diagnóstico que ativam cada item: `MODELO-OXIGENAR-ESTRUTURAR-ESCALAR.md`. A terceira etapa se chama **Escalar** (no Canex era "Expandir").

## Biblioteca de cases
`biblioteca-cases/` (README com campos e checklist). Hoje tem os seis totais por segmento da apresentação institucional, como **rascunho** (`aprovado=false`). Quando o Luis subir os cases individuais, eles passam à frente do agregado.

## Pendências
- Definição de "reconectado" e data-base dos números de segmento (João ou Depto Dados).
- Quem presta cada serviço do slide "Oxigenar, estruturar e escalar" (Save ou parceiro) e o enquadramento na OAB (Jurídico humano).
- Fontes oficiais: o Planalto e o portal da Receita não abriram durante a revisão de 14/10; dispositivos de lei marcados "conferir".
- Descrição de Save ID e AssinePro na base de conhecimento.
