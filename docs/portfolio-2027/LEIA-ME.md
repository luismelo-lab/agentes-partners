# Portfólio Save 2027 · janela de contexto própria

> **Aberta em 22/10/2026 · dono: Luis Fernando de Melo.** Tema único desta conversa: produtos e serviços da Save para 2027, montados como portfólio de ecossistema, com os agentes responsáveis ligados e a jornada completa do cliente. Santa Clara, Brassol e demais clientes ficam nas conversas próprias; aqui entram só como caso de teste do portfólio.

## 1. O que esta conversa entrega
1. **Portfólio de ecossistema 2027:** cada produto e serviço com ficha (o que é, para quem, estado, dono humano, agente responsável, trava).
2. **Jornada completa** Destravar caixa → Proteger e controlar → Crescer, com as conexões entre as peças (o que uma entrega destrava na seguinte) e a camada contínua que mantém o cliente.
3. **Matriz de agentes:** quem responde por quê, quem revisa, quando o Jurídico, o Tributário e a Qualidade entram, e qual portão (G0 a G4) vale.
4. **Peças para fora** (deck, one-pager, guia do parceiro), só depois da validação dos donos.

## 2. Fontes (leia nesta ordem, sem reler tudo)
| Fonte | Onde | O que traz |
|---|---|---|
| Handoff do ecossistema | `docs/ecossistema/handoff-ecossistema-save.md` | Visão 360, mapa de conexão, jornada no tempo, pendências |
| Ecossistema v1.0 (19/10) | `docs/ecossistema/ecossistema-produtos-servicos.md` | P1 a P17, sinais, regras e travas |
| Teses de base (T01 a T19, P01, P02) | `departamentos/tributario/catalogo-teses-save-completo.md` (fonte) e `teses-indice.md` (índice) | Texto técnico fiel ao time; fecha a lacuna nº 1 da seção 9 do ecossistema |
| Reunião de 24/09 (indústria de presunto cru) | transcrição no iCloud do Luis (não vai ao git); resumo em `insights-transcricoes.md` | Dor do cliente, captação, modelo dos fundos |
| Reunião de 21/10 (Paraguai e expansão industrial) | transcrição em `00 · Entrada` do OneDrive (não vai ao git); resumo em `insights-transcricoes.md` | Maquila, custo de produção, ciclo, objeções |
| Esteira, sinais, playbooks | `skills/depto-solucoes/references/` | Regras de sequência e setores |
| Produtos financeiros e portões | `skills/depto-internacional/references/` | Elegibilidade, G0 a G4, proibidos, perguntas ao João |

## 3. Arquivos desta pasta
- `insights-transcricoes.md`: o que as duas reuniões ensinam ao portfólio, com o que não pode virar promessa.
- `teses-indice.md`: índice das 21 fichas de base.
- `matriz-agentes.md`: produto × dono × agente × revisores × trava.
- `jornada-2027.md`: esqueleto da jornada e das conexões, com as lacunas a fechar.
- `pendencias.md`: decisões do Luis e perguntas aos donos, em uma lista só.

## 4. Regras desta conversa
- Nada aqui é oferta, taxa, prazo ou promessa. Estado dos produtos vale o de 19/10 do Luis (CLAUDE.md, seção 3).
- Produto em validação entra só como **descoberta**, com a data do portão. No máximo 2 produtos novos por vez por cliente.
- Cada ficha passa pelo fluxo do gerente (`infra/protocolo-gerente.md`) e leva o registro `revisao`. Material para fora passa pelas áreas envolvidas e pelo auditor de promessas (`depto-qualidade/scripts/auditar_texto.py`).
- Pesquisa nível Big Four, com data (`infra/protocolo-pesquisa.md`). Dado de cliente fica no Mac; os arquivos desta pasta usam `<EMPRESA>`.
- Visual: Design System Save v0.5 (`departamentos/marketing-marca/padrao/`).

## 5. Como a conversa trabalha
1. **Gabinete** recebe o pedido, decide as áreas e a profundidade, e consolida o parecer.
2. **Solucoes** é a dona da esteira e do desenho da jornada; **Internacional** responde pelos produtos financeiros e portões; **Tributario** e **Juridico** validam toda tese e toda estrutura; **Intel Comercial** diz quem é o cliente de cada produto; **Marketing** e **Qualidade** só entram em peça para fora.
3. **Conselho** só para decisão de estratégia (por exemplo: o que é próprio da Save e o que vai por parceiro).
4. Ao fim de cada rodada: atualizar `pendencias.md` e a seção 14 de `~/agentes-partners/gabinete/SESSOES.md`.

## 6. Estado
- **22/10:** estrutura criada, índice das teses gerado, resumo das transcrições, matriz de agentes e jornada em esqueleto. Nenhuma ficha de produto fechada.
- **Próximo passo:** o Luis responde as três perguntas de `pendencias.md` (próprio × parceiro, caso-piloto, escopo 2027) e o gabinete abre a rodada de fichas pelos produtos da onda 1.
