# O que falta para o melhor modelo · Área Partners

Proposta do Arquiteto de Agentes e da Qualidade, de 08/10/2026. Parte da "Revisão geral" do mesmo dia. É uma proposta: cada item com responsável humano e critério de pronto, para o Luis aprovar.

## Resumo executivo

- **Primeiro, estabilizar, e só depois expandir.** Em 10 dias de operação houve 3 dias úteis sem plano, 6 dias sem backup e 2 dias sem e-mail, sem nenhum aviso. Se o time perceber a falha antes dos agentes, perde a confiança no sistema. Nas próximas 2 semanas, o foco é confiabilidade, sem construir agentes novos.
- **Os 5 pilares que faltam.** (1) Observabilidade independente do e-mail. (2) Cópia remota e backup que funcione. (3) Testes de fumaça antes de mudar código. (4) Medição de valor por agente (D28 ampliada). (5) Operação fora do Mac do Luis.
- **As dependências externas são o caminho crítico do Q4.** O Microsoft Graph destrava o e-mail sem Outlook, o Teams e a nuvem. O escopo de arquivos do HubSpot destrava o Recuperador, que é o piloto que mostra receita. Os dois precisam de um dono e de uma data cobrada toda semana.
- **Reduzir a fila de decisões.** Há 41 decisões pendentes, e a agenda da D40 venceu. A proposta é uma regra de 72 horas: o que não for decidido volta ao Conselho como "arquivar ou decidir".
- **Meta para 1º/2027.** Operação na nuvem da Save (GitHub Actions + Microsoft 365), painel no Teams, cada agente com indicador de valor e custo, e o time treinado como dono das próprias células.

## Lacunas, em ordem de impacto

| # | Lacuna | Por que importa | Impacto | Esforço |
|---|---|---|---|---|
| L1 | Um só canal (Outlook do Mac) para entrega e para alerta | A falha do canal deixa tudo mudo, como desde 06/10 | Muito alto | Baixo |
| L2 | Sem cópia remota e backup falhando | Perder o Mac é perder o projeto | Muito alto | Baixo |
| L3 | Chamadas ao HubSpot sem nova tentativa em falha de rede | Plano do dia perdido 3 manhãs seguidas | Alto | Baixo |
| L4 | Rotinas do Claude travam e bloqueiam as seguintes | Triagem com IA e Central param sem aviso | Alto | Médio |
| L5 | Sem testes e sem verificação de saúde | Mudança de layout ou de caminho quebra o envio em silêncio | Alto | Médio |
| L6 | Repositório e skills em uso divergem; padrão de marca fora do git | Risco de perder trabalho e de quebrar a nuvem | Alto | Baixo |
| L7 | Valor dos agentes não é medido de forma contínua | Sem números não há ROI defensável para a liderança | Alto | Médio |
| L8 | Dependência do Mac ligado e do app aberto | Sem 24/7; segundas atrasaram até as 14h40 | Alto | Alto (depende da TI) |
| L9 | Integrações pendentes (Graph, GLPI OAuth, Bitrix, arquivos do HubSpot) | Bloqueiam o Recuperador, o GLPI, as sentinelas de execução e o Teams | Alto | Externo |
| L10 | Sentinelas com ruído (106 de 309 eventos são informativos) | Plano longo demais vira ruído e ninguém lê | Médio | Baixo |
| L11 | Adoção baixa pelo time (5 pedidos na Central; 0 ações do painel aplicadas; 0% das respostas aproveitadas em 4 casos) | Sistema bom e pouco usado não gera valor | Alto | Médio |
| L12 | Fila de 41 decisões pendentes | Trava produtos e o Q4 | Médio | Baixo |
| L13 | Segurança e LGPD: nomes de terceiros no git; telefone sem máscara em registro; sem inventário de quem acessa o quê | Exposição jurídica e reputacional | Médio | Baixo |
| L14 | Custo de IA não é medido | Sem teto e sem custo por entrega | Médio | Baixo |
| L15 | Documentação desatualizada e sem treinamento formal | O time não sabe operar sozinho; o Luis vira gargalo | Médio | Médio |

## Princípios do melhor modelo

- **Orquestração.** Terminal sem IA faz o mecânico. IA só interpreta e escreve. Toda rodada tem tempo máximo, trava e repetição segura (idempotente).
- **Observabilidade.** Cada rotina grava um sinal de vida. Um vigia independente confere os sinais e avisa por um segundo canal, como Teams ou celular. "Ok" só vale se a entrega foi conferida.
- **Humano no circuito.** N1 continua a regra. A autonomia sobe por degraus medidos (D28): uma tarefa só sobe de degrau com taxa de aproveitamento acima de um limite, por 4 semanas.
- **Qualidade de dados.** Contrato de dados do HubSpot (campos obrigatórios D18) com placar semanal. Sentinela só vira tarefa se tiver dono e ação clara.
- **Segurança.** Menor privilégio por integração. Segredos no cofre do GitHub ou do Azure, nunca no código. Trava de domínio mantida. Revisão de acesso trimestral.
- **Custo.** Orçamento mensal de IA com teto. Modelo leve na triagem e modelo forte só no Conselho e nas pré-análises técnicas.

## Roadmap · próximas 2 semanas (09/10 a 22/10)

| # | Ação | Responsável | Critério de pronto | Prazo |
|---|---|---|---|---|
| 1 | Reinstalar o Microsoft 365 (ou recuperar os apps da Lixeira), abrir o Outlook clássico, autorizar a automação e reprocessar o dia com "partners central agora" e "partners manha" | Luis (TI se precisar) | Central sem erro por 1 dia útil inteiro; plano do dia recebido pelas 3 | 09/10 |
| 2 | Destravar as rotinas do Claude em "running" (WhatsApp e Central) e conferir as permissões | Luis | As duas rotinas rodam no horário seguinte com status "succeeded" | 09/10 |
| 3 | Dar Acesso Total ao Disco ao /bin/zsh e ao python3; rodar o backup manual e conferir o tamanho | Luis | Backup das 19h30 com "ok" por 3 dias seguidos; tamanho acima de 50 MB | 10/10 |
| 4 | Criar repositório privado na organização da Save no GitHub e enviar o código (push) | Luis + TI | Remoto configurado; último commit visível no GitHub | 14/10 |
| 5 | Nova tentativa no "000" e no JSON cortado (hubspot_fonte.call); log do erro do curl; "caffeinate" nas rotinas manha, tarde e segunda | Agente TI (código) + Luis aprova | 5 manhãs seguidas com download ok antes das 7h50 | 14/10 |
| 6 | Sinal de vida e vigia: cada rotina grava o último sucesso; um vigia às 8h15 e às 14h15 confere e avisa por um 2º canal (aviso do macOS e, quando houver, Teams). E-mail com falha deve encerrar com erro | Agente TI + Qualidade | Teste: com o Outlook fechado, o vigia avisa em até 15 min | 16/10 |
| 7 | Acertar o repositório: aplicar o Design System nas skills em uso; versionar marca.json, save.css, pptx_save.js e os scripts de produtos; valor padrão no marca.py; trocar logo-saveco.png pelos logos v0.5 | Agente Marketing + TI | Diferença zero entre repositório e skills em uso; e-mail de teste no novo layout; git status limpo | 16/10 |
| 8 | Teste de fumaça (`partners teste`): importa cada lib, monta um e-mail de teste sem enviar, confere o caminho do OneDrive, o token do HubSpot (sem imprimir) e o dicionário do Outlook | Agente TI | Comando roda em menos de 60 s e é obrigatório antes de cada commit | 18/10 |
| 9 | Corrigir o atalho do OneDrive em caminhos.py e organizar_onedrive.py (validar o destino do atalho) | Agente TI | "python3 lib/caminhos.py" mostra a pasta certa com o atalho quebrado e com o atalho certo | 16/10 |
| 10 | Tirar nomes de terceiros de decisoes.md versionado (usar código) e mascarar o telefone em medicao-respostas.json | Qualidade + Jurídico | A barreira de LGPD passa a checar uma lista de nomes proibidos; 0 achados | 18/10 |
| 11 | Sessão de decisões: fechar D7-b, D8, D10, D12, D13, D15 (Q4) e D46–D48 (operação) | Luis com o Conselho | Cada uma aprovada, rejeitada ou arquivada; fila abaixo de 25 | 15/10 |
| 12 | Cobrar as dependências externas com dono e data: Graph/Teams, GLPI OAuth, webhook do Bitrix, escopo de arquivos do HubSpot, crédito do `claude -p` | Luis | Cada pedido com protocolo, responsável na TI ou no CRM e data prometida | 15/10 |
| 13 | Sentinelas: "entrou em diagnóstico" vira informativo (D47); resumo diário com até 15 itens | Agente Dados | Plano da Daniela com no máximo 15 itens acionáveis | 21/10 |
| 14 | Atualizar ESTADO, RUNBOOK e README (Outlook, OneDrive, vigia, teste de fumaça) | Agente Gabinete | Documentos com data de 22/10 e sem informação vencida | 22/10 |

## Roadmap · Q4/2026 (até dezembro)

| Frente | Ação | Responsável | Critério de pronto |
|---|---|---|---|
| Continuidade | E-mail e arquivos pelo Microsoft Graph (caixa compartilhada e SharePoint). O Outlook do Mac fica como reserva | TI + Agente TI | Uma semana sem usar AppleScript |
| Continuidade | Rotinas sem IA no GitHub Actions (OD_BASE/SharePoint), com o Mac como reserva (.nuvem-ligada) | Agente TI | 10 dias úteis com plano às 7h30 mesmo com o Mac desligado |
| Continuidade | IA pelo terminal (`claude -p`) com tempo máximo e permissões fixas, no lugar das rotinas do app | Luis (crédito) + Agente TI | Nenhuma rodada travada em 2 semanas |
| Painel e Teams | Painel no Teams (aba ou cartões adaptáveis) com as mesmas ações do painel atual | TI + Agente TI | Time usa o Teams; painel antigo só como reserva |
| Medição (D28) | Placar semanal por agente: uso, aproveitamento, horas economizadas, valor validado, falsos positivos | Agente Resultados + Qualidade | Placar no relatório de segunda por 4 semanas seguidas |
| Recuperador | Leitura dos 343 pareceres bloqueados; 1º relatório do piloto com valor validado | CRM (escopo) + Geovana | Relatório do piloto com valor validado e taxa de falso positivo |
| GLPI | OAuth por pessoa; chamados abertos depois da aprovação (D29) | TI + Daniela | 20 chamados abertos pelos agentes com 0 retrabalho |
| Bitrix | Webhook só leitura; ligar as sentinelas de execução | TI + Agente Dados | Ganho sem execução e execução parada no plano |
| Qualidade de dados | Campos obrigatórios D18 no HubSpot; placar de completude por dono | CRM + Agente Dados | Completude acima de 90% nos ganhos do Q4 |
| Adoção | Semana 0 mínima e 1:1 (D48); treinamento de 45 min por célula; guia de 1 página por pessoa | Luis + Agente Pessoas | 3 pessoas fazendo pedidos à Central toda semana; 10 pedidos ou mais por semana |
| Segurança | Inventário de acessos por integração; revisão de segredos; rotação do token do HubSpot | Agente TI + TI | Planilha de acessos aprovada; token rotacionado |
| Custo | Registro do custo de IA por rodada e teto mensal | Agente Resultados | Custo por entrega no relatório mensal |

## Roadmap · 1º semestre de 2027

| Frente | Ação | Responsável | Critério de pronto |
|---|---|---|---|
| Autonomia medida | Degrau 2 da D28 para os tipos de resposta com aproveitamento acima de 80% por 4 semanas (envio interno automático; externo continua humano) | Luis + Qualidade | Decisão registrada por tipo, com os números |
| Plataforma | Uma só orquestração na nuvem: fila de tarefas, novas tentativas, painel de saúde e histórico | Agente TI + TI | Painel de saúde com todas as rotinas; disponibilidade acima de 98% |
| Avaliação | Conjunto de casos de teste (avaliação) por agente crítico: triagem, Recuperador, Revisor, auditor | Qualidade | Avaliação roda a cada mudança de prompt; queda acima de 5% bloqueia |
| Dados | Base analítica única (HubSpot + Bitrix + GLPI + Receita) com dicionário de métricas | Agente Dados | Relatório semanal 100% a partir da base única |
| Produtos | Padrão de Produto Novo aplicado ao Crédito Internacional e à Maquila, com portões G0–G3 | Luis + áreas reais | Cada produto com portão aprovado ou encerrado |
| Pessoas | Cada pessoa vira dona da própria célula: ajusta regras, aprova degraus e treina a próxima | Luis + Agente Pessoas | Cada célula com 1 melhoria proposta pela dona por mês |
| Escala | Modelo replicável para outra área da Save (kit de implantação) | Luis | Kit documentado e apresentado à liderança |

## Dependências externas e donos

| Dependência | Destrava | Dono sugerido | Situação em 08/10 |
|---|---|---|---|
| Microsoft Graph, SharePoint e Teams | E-mail sem Outlook, nuvem, painel no Teams | TI da Save | Pedido feito; sem data |
| Cliente OAuth do GLPI | Abertura de chamados | Administrador do GLPI | Pedido em docs/GLPI.md |
| Webhook do Bitrix (só leitura) | Sentinelas de execução e pareceres | TI | Pedido em docs/BITRIX.md |
| Escopo de arquivos do HubSpot | 343 pareceres do Recuperador | Dono do CRM | Pendente desde 29/09 |
| Crédito do `claude -p` | IA pelo terminal e na nuvem | Administrador do Claude na Save | Bloqueado |
| Repositório privado no GitHub da Save | Cópia remota e Actions | TI | Não criado |

## Riscos se nada mudar

- Uma nova falha silenciosa no envio derruba a confiança do time nos agentes.
- Perda do Mac sem backup válido nem cópia remota.
- O piloto do Recuperador não mostra valor no Q4 porque os pareceres estão bloqueados.
- A fila de decisões cresce, e o Conselho vira burocracia em vez de acelerar.
