# Novo Painel Central Partners · Proposta para análise

## 1. Resumo
- **Por que o painel parece fraco:** ele mostra só 11 blocos pequenos de dados, e muito do que já é gerado nem aparece. O painel já recebe, e não exibe, a análise do WhatsApp por pessoa, o Revisor da Geovana inteiro, o tamanho da fila do Recuperador, o sinal de cada Master e a idade das demandas.
- **Há muito mais pronto, sem coleta nova:**
  - série de 12 meses;
  - win rate, que é a taxa de conversão de negócios em ganhos;
  - ciclo de venda, margem e ROI;
  - scorecard completo dos Masters;
  - conflitos de canal, repasses e contratos;
  - qualidade do CRM;
  - 377 alertas das sentinelas e 85 demandas com tempos.
- **Usabilidade:**
  - todo mundo abre na tela do Luis;
  - os números não dizem idade, valor nem urgência;
  - o formulário de pedido esconde as respostas;
  - o lote do Recuperador vem em 20 cartões seguidos;
  - os botões ficam pequenos no celular;
  - o visual está fora do Design System Save.
- **Recomendação:** cada pessoa abre o **seu cockpit**, com os números dela, o bloco "Fazer agora" e o detalhe. O "Fazer agora" funciona como uma caixa de entrada única de ações, filtrada para a pessoa. O visual passa a seguir o padrão Save de painel (fundo preto, ouro, IBM Plex). A plataforma fica a mesma por agora, porque é rápida, não tem custo nem depende da TI. A visão de gestão vai para o Microsoft 365 quando a TI liberar a integração.

## 2. O que está errado hoje
| Problema | Evidência | Efeito |
|---|---|---|
| Dados gerados e não exibidos | Análise do WhatsApp, Revisor, fila do Recuperador, sinal dos Masters, idade das demandas | Painel "vazio" com dados prontos |
| Primeira tela errada | Todo mundo abre na Visão geral do Luis | Cada pessoa precisa procurar o que é dela |
| Números sem contexto | "Daniela: 3 para responder", sem idade, valor nem urgência | Não ajuda a priorizar |
| Alertas fracos | Frases sem número, todas com a mesma gravidade e sem botão para agir | Ninguém age |
| Pedidos | Formulário de 9 campos antes da lista de respostas | Quem vem aprovar não acha a resposta |
| Recuperador | 20 cartões seguidos com 3 botões cada | Cansa e não mostra o próximo a decidir |
| Aba da Jenifer | Igual às outras, nada de BDR | Não serve ao dia dela |
| Identidade | Qualquer pessoa pode se dizer outra no seletor "Quem é você?" | Risco de registro errado |
| Acessibilidade e celular | Botões de 32 px (o mínimo é 44), chips de 11 px, tabela que rola de lado | Ruim no celular |
| Fora do padrão Save | Logo em texto, paleta própria, números sem IBM Plex Mono | Não parece Save |

## 3. Três opções de layout
| Opção | Como é | Prós | Contras |
|---|---|---|---|
| **A · Cockpit por pessoa** | Tela inicial de cada um: números, "Fazer agora" e detalhe | Cada pessoa entra direto no que é dela; a mais fácil de fazer | O Luis troca de tela para ver o detalhe do time |
| **B · Caixa de entrada única** | Uma lista com tudo que pede ação (demandas, conversas, chamados, pedidos, Conselho, lote), com filtros e detalhe ao lado | Nada escondido; ótimo no celular | Perde a visão analítica |
| **C · Painel analítico** | Indicadores e gráficos com filtros de período, Master e pessoa | Responde ao "fraco de dados" | Serve pouco à operação da Daniela e da Geovana |

**Recomendação: A + B, com C dentro do cockpit do Luis.**
- Os menus passam a ser: **Início** (o cockpit), **Caixa de entrada**, **Pedidos aos agentes** e **Masters**.
- O cockpit do Luis ganha a parte analítica, com gráficos e filtros.

## 4. A primeira tela de cada pessoa
**Luis (gestão).**
- Números: itens esperando por ele, demandas do time com a mais antiga em dias, R$ aberto nos Masters, Masters em risco e potencial do Recuperador.
- Depois: a lista "Decidir hoje" (Conselho, pedidos prontos, chamados) com o botão de ação no próprio item, a tabela dos Masters e a carga por pessoa.
- Gráficos: ganhos dos últimos 12 meses, win rate, funil por etapa, ciclo de venda, pipeline por parceiro, margem e ROI, concentração nos maiores parceiros.

**Daniela (Masters).**
- Números: para responder, urgentes, a mais antiga e chamados para aprovar.
- Depois: a fila "Responder agora", ordenada por urgência e tempo de espera, com as conversas de WhatsApp e as demandas juntas.
- Ao lado, um resumo por Master: demandas abertas, saúde, negócios parados, contratos pendentes, repasses com problema e conflitos de canal.

**Jenifer (BDR).**
- Números: negócios novos no funil BDR na semana, entradas em diagnóstico, cadastros incompletos e conflitos a checar antes de abordar.
- Depois: a fila de demandas, os pedidos ao BDR e a cobertura por segmento e UF de cada Master.
- Depende de dado novo: atividades (ligações e reuniões) e follow-ups vencendo.

**Geovana (técnica).**
- Números: lote decidido "x de y" com barra de progresso, potencial do lote e da fila, Revisor (revisados, alta prioridade, lacunas) e diagnósticos parados.
- Depois: a tabela do lote ordenada por valor esperado, com a decisão ao abrir a linha, e o Revisor por tese em barras.

## 5. Dados: o que entra já e o que falta
**Entra já** (o gerador do painel só precisa ler arquivos que as rotinas já produzem):
- série mensal, crescimento, win rate, ticket e concentração;
- margem e ROI;
- scorecard completo dos Masters;
- qualidade do CRM;
- conflito de canal e ciclo;
- conferência de repasses;
- controle de contratos;
- métricas de Partner Success;
- alertas por tipo e pessoa;
- tempos das demandas;
- indicadores do Recuperador e do Revisor;
- mix de teses.

**Falta, e o que destrava:**
| Dado que falta | Destrava |
|---|---|
| Recebido do Financeiro (vazio nos 4.950 negócios) | Receita contratada × recebida, repasse a pagar de fato, ROI de caixa |
| Metas mensais da área e por Master | Realizado × meta, previsão e atingimento por Master |
| Honorário e % do parceiro (preenchidos em ~19% da base) | Margem, repasse e ROI com a base inteira, não só uma amostra |
| Execução no Bitrix | Acompanhar o ganho até a entrega |
| Histórico de mudança de etapa no HubSpot | Funil e tempo por etapa exatos |
| Motivo de perda | Análise de perda por Master e tese; alimenta o Recuperador |
| Atividades do BDR | Produtividade da Jenifer |

## 6. Caminho técnico
| | A · Painel atual (Artifact) | B · Power BI ou Excel Online | C · SharePoint ou aba no Teams | D · Aplicação própria |
|---|---|---|---|---|
| Esforço | Baixo (dias) | Médio (2 a 4 semanas) | Baixo a médio | Alto (2 a 3 meses) |
| Custo | Zero | Licença Power BI por leitor (confirmar se a Save já tem) | Incluso no Microsoft 365 | Hospedagem e manutenção |
| Registrar ações no painel | Sim (ponto forte) | Fraco (exigiria Power Apps) | Sim, com listas | Sim |
| Acesso | Conta do Claude da Save | Conta Microsoft que o time já tem | Conta Microsoft | Login Microsoft |
| Dados de clientes (LGPD) | Saem do ambiente Save: precisa do aval do Jurídico | Ficam no ambiente Save | Ficam no ambiente Save | Depende da hospedagem |
| Depende da TI | Não | Sim | Sim | Sim |

**Por fase:**
1. **Agora:** evoluir o painel atual. Novo layout, dados ampliados, filtros, gráficos, aviso de "dados de X horas atrás" e só o dado de cliente necessário. Em paralelo, pedir o parecer de LGPD ao Jurídico.
2. **Quando a TI liberar a integração com o Office:** a atualização vai para a nuvem e para de depender do Mac. Os dados passam a ficar no SharePoint, e a visão de gestão vai para o Power BI ou para uma aba no Teams. O painel atual fica como painel de ações do time.
3. **Evitar a aplicação própria:** custo e manutenção não se justificam para 4 usuários.

## 7. Decisões para o Luis
1. **Layout:** aprova a recomendação A + B, com C dentro do cockpit do Luis?
2. **LGPD:** aceita levar ao Jurídico o pedido de parecer sobre dados de clientes no painel? Até lá, o painel mostra só o código do negócio e números agregados.
3. **Acesso:** Daniela, Jenifer e Geovana têm conta do Claude da Save?
4. **Metas:** o painel deve ter realizado × meta? Se sim, quais metas (do Planejamento 2027 e por Master)?
5. **TI:** perguntar se a Save já tem licença do Power BI e qual o prazo da integração com o Office.
6. **Próximo passo:** um protótipo navegável da opção recomendada, com dados de exemplo e no padrão Save, para você testar antes de construir.
