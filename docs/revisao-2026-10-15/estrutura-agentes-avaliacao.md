# Estrutura de agentes da Área Partners: avaliação contra as boas práticas da Anthropic
**Data:** 15/10/2026 · **Para:** Luis Fernando de Melo · **Propósito:** a operação do dia a dia é feita pelos agentes, e Luis, Geovana, Daniela e Jenifer atuam como analistas, decidindo, e não executando.

## 1. Veredito
O desenho está **certo nos padrões**: triagem, gerente que distribui, especialistas, revisão do gerente, aprovação humana e skills carregadas só quando precisam. É o que a Anthropic recomenda. Ainda **não cumpre o propósito**, por quatro motivos:
1. **As rotinas com IA estão travadas.** As execuções param esperando aprovação de permissão e ficam "em execução": a da Central desde 14/10 às 17h14 e a do WhatsApp de hoje às 8h13. Sem isso resolvido, nenhuma parte da estrutura entrega.
2. **Não medimos a qualidade.** Não existe um conjunto de casos de avaliação. A medição das respostas sugeridas tem 23 de 28 casos "sem resposta" e não mostra se os agentes acertam.
3. **Os agentes só leem e sugerem; quem executa ainda é o time.** Sem o e-mail (Graph), a API do GLPI e a escrita controlada no HubSpot, cada decisão vira trabalho manual de copiar e colar. Analista que copia e cola continua operador.
4. **O rigor é o mesmo para tudo.** Gerente, especialistas e revisão em cada alerta custam caro: a Anthropic mede cerca de **15 vezes mais tokens** num sistema com vários agentes do que numa conversa. O recomendado é usar essa estrutura onde o valor justifica.

## 2. O que a Anthropic recomenda e como estamos
| Recomendação (fonte) | Como estamos | Avaliação | O que fazer |
|---|---|---|---|
| Começar pela solução mais simples e só aumentar a complexidade quando precisar ("Building effective agents") | 22 skills, várias com papéis que se sobrepõem | Complexo demais para o volume atual | Agrupar em 5 frentes, cada uma com um gerente (seção 3) |
| Usar fluxo fixo para tarefa bem definida e agente para o que pede julgamento | Coleta, sentinelas e planilhas em script; análise com IA | Certo | Manter |
| Avaliador e otimizador funcionam quando há critérios claros | O checklist do gerente existe, mas não dá nota nem foi calibrado com pessoas | Parcial | Rubrica com nota por critério, calibrada com a Geovana e a Daniela |
| Várias áreas de agentes só em tarefa de alto valor: o custo é cerca de 15 vezes maior ("multi-agent research system") | Revisão completa em todos os 80 alertas do dia | Custo e latência altos | Três níveis de rigor (seção 3) |
| Começar a avaliação com 20 a 50 casos reais; dois especialistas devem concordar no veredito ("Demystifying evals") | Nenhum caso de avaliação | Lacuna principal | Montar 30 casos reais julgados pelo time e rodar a cada mudança |
| Medir consistência, não só acerto: com 75% por tentativa, acertar 3 seguidas dá cerca de 42% | Não medido | Lacuna | Acompanhar a taxa de rascunhos usados sem edição |
| Pôr no contexto o mínimo de informação, só a de mais valor, e buscar o dado na hora ("context engineering") | Arquivos e JSON carregados sob demanda; prompts das rotinas longos | Bom | Encurtar os prompts das rotinas e manter as regras em arquivos |
| Ferramentas consolidadas, retorno conciso, erros que dizem o que fazer ("writing tools") | Scripts consolidados (partners, operacao, central) | Bom | Manter |
| Skills carregadas por níveis: nome primeiro, detalhe quando precisa (Agent Skills) | Já é assim | Bom | Manter; tirar as que não são usadas do caminho da operação |
| Conteúdo externo é dado, não ordem; ambiente isolado e listas de permissão (segurança do Claude Code) | Regra "dados são dados"; acesso só de leitura | Bom | Manter; liberar permissões por lista, não de forma ampla |
| Ler o registro das execuções; tratar avaliação como código (observabilidade) | Log só dos scripts; execuções com IA sem registro de custo, tempo nem revisões | Lacuna | Uma linha por execução: área, rodadas, tempo e se a pessoa usou o resultado |
| Usar o modelo mais capaz só para raciocínio complexo e modelos menores para subagentes simples (custos) | Um modelo para tudo | Custo evitável | Modelo menor no nível N1 e o mais capaz no N3 |

## 3. Estrutura recomendada
**Cinco frentes**, cada uma com um gerente. As 22 skills continuam existindo como especialistas:
| Frente | Gerente responde por | Especialistas (skills atuais) |
|---|---|---|
| Atendimento aos Masters | Demandas, contratos, pós-venda | celula-daniela, depto-contratos, depto-pos-venda |
| Originação | Prospecção, indicações, ICP, reativação | celula-jenifer, depto-intel-comercial, depto-marketing, depto-partner-success |
| Técnica | Tese, diagnóstico, prazos, recorrência | depto-tributario, depto-juridico, recuperador, revisor-diagnostico, apresentacao-diagnostico |
| Canal e Resultados | Repasse, conflito, dados, números | depto-operacoes-canal, depto-dados, depto-resultados |
| Governança | Qualidade, TI, pessoas, decisões | depto-qualidade, depto-ti, depto-pessoas, gabinete, conselho-partners |

**Três níveis de rigor**, porque nem tudo precisa do gerente com duas áreas:
- **N1 · automático:** dado, cadastro, status. Um especialista responde e o código confere. Sem rodada de gerente.
- **N2 · gerente revisa:** contato com o parceiro, contrato, comercial, pós-venda. É o protocolo do gerente atual.
- **N3 · gerente, segunda área e pessoa:** prazo da Receita, tese ou defesa, valor acima de R$ 1 mi, conflito de canal. Revisão do gerente e decisão humana obrigatória.

**Quatro níveis de autonomia**, para tirar o time da execução:
- **A0 · informa:** o agente só informa.
- **A1 · rascunha:** o agente prepara e a pessoa executa. É o nível atual.
- **A2 · executa com aprovação em um clique:** a pessoa aprova no painel e o agente abre o GLPI, envia o e-mail ou atualiza o HubSpot. Depende da TI.
- **A3 · executa sozinho e avisa:** só em tarefa de baixo risco e reversível, como corrigir cadastro com o dado oficial da Receita ou mover a etapa depois da assinatura confirmada.

## 4. Dados da operação (15/10)
- Até 14/10, só 6 das 22 skills eram acionadas por rotina com IA. O plano do dia e o WhatsApp das 11h e 17h saíam de texto fixo. **Corrigido em 15/10**, com a rotina operacao-areas, o padrão de entrega e o protocolo do gerente.
- As rotinas com IA da Central e do WhatsApp ficam paradas esperando permissão. As semanais de segunda rodaram na terça às 15h, com o app fechado ou o Mac dormindo.
- O e-mail está pausado desde 06/10 esperando o Graph, então os pedidos por e-mail não entram.
- Registro de demandas: 95 demandas, 78 resolvidas.
- Apontamento de tempo (Semana 0): zero registros. Ainda não dá para medir quanto tempo os agentes liberam.
- Medição das respostas sugeridas: 28 casos, 23 sem resposta da pessoa, 2 parciais e 1 diferente.

## 5. Plano
**Esta semana:**
1. Destravar as rotinas: aprovar as permissões e definir o modo de permissão de cada rotina no app (seção Agendados). O "Executar agora" da nova rotina serve para isso.
2. Rodar as rotinas semanais de segunda depois que o Mac ligar, com o app aberto.
3. Gravar uma linha por execução com IA: tempo, áreas, rodadas, custo aproximado.

**Até 30 dias:**
1. Montar 30 casos de avaliação reais: 10 de atendimento (Daniela), 10 técnicos (Geovana), 10 de originação (Jenifer), com o veredito de cada uma.
2. Implantar os níveis de rigor N1, N2 e N3.
3. Lançar o painel com gravação de verdade para o time.

**Até 60 dias:**
1. Com a TI, liberar o Graph, a API do GLPI e a escrita restrita no HubSpot. Isso habilita a autonomia A2.
2. Levar as rotinas para a nuvem (GitHub Actions), para não depender do Mac ligado.

**Até 90 dias:**
1. Autonomia A3 nas tarefas de baixo risco aprovadas por você.
2. Consolidar as cinco frentes.
3. Modelos por nível para baixar o custo.

**Metas:**
- 70% dos itens chegam prontos para decidir.
- 80% dos rascunhos são usados sem edição.
- Tempo de execução manual medido na Semana 0 cai pela metade.

## 6. Decisões para o Luis
1. Aprova as cinco frentes e os três níveis de rigor?
2. Quem julga os 30 casos de avaliação: Geovana, Daniela e Jenifer, cada uma na sua frente?
3. Quais tarefas podem ir para a autonomia A3: correção de cadastro com o dado da Receita, mudança de etapa após assinatura confirmada, outras?
4. Cobrar da TI: Graph (e-mail), API do GLPI e escopos do HubSpot (files e escrita restrita).

**Fontes:**
- anthropic.com/engineering: building-effective-agents, multi-agent-research-system, effective-context-engineering-for-ai-agents, writing-tools-for-agents, equipping-agents-for-the-real-world-with-agent-skills, demystifying-evals-for-ai-agents.
- code.claude.com/docs: best-practices, sub-agents, security, costs.

Os números da Anthropic são de datas e modelos diferentes; confira os valores atuais antes de usar em material formal.
