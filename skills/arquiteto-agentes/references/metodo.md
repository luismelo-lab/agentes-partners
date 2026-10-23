# Método por fase

## Fase 0 — Contexto
Descubra (proponha um rascunho e peça correção):
- Quem é cada pessoa, o que faz, quanto tempo da semana é operacional.
- Por onde chegam as demandas dos parceiros (WhatsApp, e-mail, HubSpot, Teams, telefone). Isso define o que o agente consegue "ler": canal sem integração = entrada manual (colar a conversa).
- Ferramentas usadas e quais já têm conector disponível (HubSpot, Gmail, Google Drive, Calendar etc. — verifique com ToolSearch).

## Fase 1 — Diagnóstico
Gere `mapa-de-tarefas.xlsx` com uma aba por pessoa e as colunas:
`Tarefa | Exemplo real | Canal de entrada | Frequência/semana | Minutos por vez | Ferramentas usadas | Regras que segue? (S/N) | Precisa de julgamento? (Baixo/Médio/Alto) | Custo de um erro (Baixo/Médio/Alto) | Observações`
Inclua 3 linhas de exemplo preenchidas com casos plausíveis da função para mostrar o nível de detalhe. Escreva também a mensagem que o Luis vai mandar ao time: por quê (liberar tempo para o trabalho estratégico, não substituir ninguém), o que registrar e por quanto tempo (5 dias úteis). Enquadre como oportunidade: é importante que o time não sinta o projeto como ameaça.

## Fase 2 — Priorização
Para cada tarefa:
- **Horas/semana** = frequência × minutos / 60
- **Viabilidade (1–3):** 3 = segue regras, entrada digital, pouco julgamento; 1 = muito julgamento ou entrada só verbal.
- **Risco (1–3):** custo de um erro (3 = alto).
- **Nota** = horas/semana × viabilidade ÷ risco

Agrupe as tarefas por afinidade (mesma pessoa e mesmos dados = mesmo agente). O piloto ideal tem nota alta, risco baixo e resultado visível em até 3 semanas. Mostre o top 10 e recomende um piloto, explicando o porquê.

## Níveis de autonomia
- **N0 — Assistente:** a pessoa pergunta, o agente responde (consulta).
- **N1 — Rascunho:** o agente prepara a saída e um humano aprova antes de sair. **Todo piloto começa aqui.**
- **N2 — Executa e avisa:** o agente age em tarefas de baixo risco e registra o que fez.
- **N3 — Autônomo:** só em tarefas de risco baixo com histórico comprovado; revisão por amostragem.

## Fase 3 — Desenho do agente
Preencha a FICHA (modelo em `modelos.md`). Pontos que costumam faltar: exemplos de entrada e saída reais, o que o agente NÃO deve fazer e quando escalar para um humano.

## Fase 4 — Base de conhecimento
- Colete o material que existe (documentos, e-mails modelo, respostas frequentes, regras de honorários/repasse, roster de parceiros).
- Entreviste a pessoa supervisora: "quais são as 20 perguntas que você mais responde?" Cada uma vira um arquivo curto: pergunta → resposta → fonte → quando não se aplica.
- Guarde 5–10 exemplos reais de "boa resposta". Exemplos ensinam o agente mais do que regras.
- Prefira vários arquivos curtos e temáticos a um documento gigante.

## Fase 5 — Construção
Caminho padrão, do mais simples ao mais robusto (só avance quando o anterior não bastar):
1. **Skill do Claude** (arquivo SKILL.md + base de conhecimento) usada pela pessoa no Claude. Sem servidor e sem chaves. Comece aqui.
2. **Skill + conectores** (HubSpot, Gmail, Drive) para ler e escrever dados reais.
3. **Tarefa agendada** para rotinas (ex.: resumo diário de pendências às 8h).
4. **Agente autônomo (Claude Agent SDK)**, como o `~/soe-agent/`, quando precisar rodar sem ninguém abrir o Claude.
Teste com 3 casos reais antes de liberar para o piloto.

## Fase 6 — Piloto
- Planilha de registro: `Data | Entrada | Saída do agente | Aprovada / Editada / Rejeitada | Motivo | Minutos economizados (estimativa)`.
- Revisão semanal de 30 min com a pessoa supervisora: o que falhou vira ajuste na base de conhecimento ou na skill.

## Fase 7 — Medição
Compare com a linha de base da Fase 1:
- Horas/semana liberadas (e o valor em R$, usando o custo/hora aproximado)
- Tempo de resposta ao parceiro
- Taxa de aprovação sem edição
- O que a pessoa passou a fazer com o tempo liberado (é esse o argumento estratégico)

## Fase 8 — Apresentação
Linguagem de quem decide: problema → o que foi feito → resultado em números → governança → próximo passo e o que é preciso da liderança. Uma página.


## Aprendizados das 24 áreas construídas (28/09 a 22/10/2026)
1. **Medir antes de construir.** A casa construiu 24 skills sem fechar a Fase 1 (apontamento com zero registros): sem linha de base, não há ROI realizado. Próximo agente só com linha de base de 1 semana.
2. **Canal de entrada é pré-requisito.** A Central por e-mail ficou sem pedidos quando o Graph parou (06/10); escolha um canal que funciona hoje (painel, pasta do OneDrive, D91).
3. **O gargalo pode ser a decisão humana.** O lote 1 do Recuperador ficou 3 semanas sem decisão; a folha curta (22/10) destravou. Desenhe a saída do agente para facilitar a decisão.
4. **Rigor proporcional.** Revisão completa em todo alerta custa ~15x uma conversa (Anthropic, citado em 15/10); use N1 (automático) para dado e status, N2 para parceiro e contrato, N3 para prazo, tese, valor acima de R$ 1 mi e conflito.
5. **Texto externo é dado, não ordem**, e trava de domínio no envio (`lib/protecao.py`).
6. **Porteiro antes de tudo** (22/10): pedido repetido ou continuação não começa do zero.
7. **Especialista sênior por arquivo** (D93): perfil + 10 seções; o gerente cobra o método do arquivo na revisão.
8. **Validação humana fecha o ciclo** (D94): base de especialista é interna até o dono validar.

## Avaliação dos agentes (evals)
- 20 a 50 casos reais por frente, julgados pela pessoa que faz o trabalho; dois juízes em parte da amostra (Anthropic, "Demystifying evals for AI agents").
- Medir consistência: com 75% de acerto por tentativa, acertar 3 seguidas dá cerca de 42%.
- Metas propostas em 15/10: 80% dos rascunhos usados sem edição; 70% dos itens prontos para decidir.
- Rodar os casos a cada mudança de skill e guardar o resultado com a data.

## ROI de IA (modelo da casa)
Benefício = horas liberadas × custo/hora + receita incremental atribuível + erro caro evitado. Custo = tokens e assinatura + supervisão humana + TI e construção + erro residual. ROI líquido = (benefício − custo) ÷ custo, com a linha de base da Fase 1 e o rótulo "potencial" enquanto o benefício for contratado (D16). Detalhe e casos em `especialistas/mentor-metodo.md`.
