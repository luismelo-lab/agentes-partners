# NPS / CSAT / CES — desenho da escuta (v1, 29/09/2026)

> Tudo aqui é desenho. **Nenhuma pesquisa é disparada pelo agente.** O disparo é humano, depois de o Luis aprovar o questionário, o público, o canal e a base legal (seção 6).

## 1. O que medir em cada momento (pesquisa de boas práticas)
Em B2B, dois tipos de pesquisa convivem (CustomerGauge, SurveySensum, 2025):
- **Relacional** (a relação como um todo): NPS + 3 a 5 perguntas. Taxa de resposta típica de 15–25%. Semestral.
- **Transacional** (um momento da jornada): 2 a 3 perguntas, enviada até 10 dias depois do evento. Taxa típica de 25–40%.
- A **relacional tem prioridade**: se uma transacional cair até 30 dias antes dela, pule a transacional (fadiga).
- **Remetente:** relacional sai de um remetente neutro (Qualidade/Save), para reduzir o viés de cortesia; a transacional pode sair de quem atendeu.

**Proposta de ajuste ao pedido do Luis:** ele sugeriu NPS nos três momentos. Proponho **NPS só onde faz sentido perguntar "recomendaria?"** e, nos momentos em que o resultado técnico contamina a nota, medir **clareza e esforço**:

| Momento (gatilho) | Público | Métrica principal | Por quê |
|---|---|---|---|
| **Relacional semestral** (abr e out) | Parceiros Masters + indicadores ativos | **NPS** + motivo + 4 drivers (seção 3) | Mede a lealdade ao programa; alimenta o Partner Success e o scorecard |
| **Pós-onboarding** (D+30 da assinatura do termo; repete em D+90) | Parceiro novo | **CSAT** do onboarding + **CES** ("foi fácil começar a indicar?") | Parceiro com 30 dias ainda não tem base para recomendar; o que importa é se destravou |
| **Pós-parecer / diagnóstico** (até 10 dias da apresentação) | Cliente (via parceiro, seção 6) + parceiro | **CSAT de clareza** + **CES** | Se o parecer der zero, o NPS mede a frustração com o resultado, não a qualidade do serviço. Clareza e esforço são controláveis |
| **Pós-ressarcimento** (PER deferido / 1ª ordem bancária, gatilho do depto-pos-venda) | Cliente + parceiro | **NPS** + CSAT do acompanhamento | Momento de "valor entregue": é quando a recomendação é honesta |
| **Pós-reclamação** (encerramento do caso na Ouvidoria) | Quem reclamou | **CSAT do tratamento** (ISO 10002, 8.3) | Mede o processo de reclamação, não o serviço |

Frequência máxima: **3 convites por conta a cada 12 meses**, somando todos os momentos. Parceiro que respondeu a relacional não recebe transacional nos 30 dias seguintes.

## 2. Pergunta NPS (texto padrão)
Parceiro: "De 0 a 10, qual a probabilidade de você **indicar a Save** a um colega contador/escritório?"
Cliente: "De 0 a 10, qual a probabilidade de você **recomendar a Save** a outra empresa?"
Sempre seguida de uma aberta: "Qual o principal motivo da sua nota?"

## 3. Drivers do NPS de parceiros (programa de canal)
Nota 1–5 em: (a) **retorno e prazo** das áreas de apoio; (b) **clareza do parecer** para explicar ao cliente; (c) **repasse** (previsibilidade, extrato, pontualidade); (d) **apoio para vender** (materiais, Academia, reunião técnica). Os drivers apontam onde agir; o NPS sozinho não diz o quê.

## 4. Cálculo (sempre pelo script)
`python3 ~/.claude/skills/depto-qualidade/scripts/calc_nps.py respostas.csv --por momento,publico`
- NPS = % promotores (9–10) − % detratores (0–6). Faixa −100 a +100.
- **Margem de erro (95%)** = 1,96 × √[(p + d − (p − d)²) / n] × 100. Com 9 Masters, o NPS dos Masters **nunca** sai como número (n < 10): leia a distribuição e os comentários.
- **NPS por conta** (B2B): média das notas de cada conta, depois o NPS sobre as contas. Evita que um escritório com 5 respondentes pese 5 vezes.
- CSAT = % de notas 4–5 (escala 1–5). CES = % de notas 5–7 (escala 1–7, 7 = muito fácil).
- **Taxa de resposta** entra no relatório (linha de controle `enviados`). Abaixo de 15%: o resultado é indicativo.
- Não compare o NPS da Save com benchmark genérico de mercado; compare com o semestre anterior da própria Save.

## 5. Fechar o ciclo (o que dá valor à pesquisa)
- **Detrator (0–6):** retorno humano em até **2 dias úteis** (Daniela para Masters; quem atendeu, para clientes via parceiro). O comentário vira ficha em `reclamacoes/` se houver fato concreto.
- **Neutro (7–8):** leitura mensal dos motivos.
- **Promotor (9–10):** agradecer; **não** pedir depoimento sem autorização escrita (regra P8 da auditoria; Prov. 205/2021 se aplicável).
- Relatório semestral: NPS, drivers, 5 temas mais citados (pela taxonomia de causa-raiz), ações e dono. Vai ao Luis e ao Partner Success; o índice de saúde do Dados & BI pode receber o NPS como insumo **se** o Dados aprovar a fórmula (proposta, não decidido).

## 6. LGPD e canal (condição para disparar)
- **Base legal proposta:** legítimo interesse (LGPD art. 7º, IX, e art. 10) para pesquisar quem já tem relação ativa com a Save, com **teste de balanceamento registrado** (LIA) e **opt-out** em todo convite. Consentimento só se o Jurídico preferir. [VALIDAR com depto-juridico / LGPD & Privacidade]
- **Clientes dos parceiros:** o cliente pertence à relação parceiro–Save. Proposta: convite **enviado pelo parceiro ou com a ciência dele**, nunca por lista extraída do HubSpot sem combinar com o Master (evita conflito de canal). [Decisão do Luis]
- **Mínimo de dados:** a resposta guarda `conta` (ID HubSpot do negócio/parceiro), momento, data e notas. Nome, telefone e e-mail do respondente **não** vão para a planilha de análise. Comentário aberto é pseudonimizado antes da análise (nomes → [PESSOA], CNPJ → [CNPJ]).
- **Retenção proposta:** respostas individuais 24 meses; depois, só agregados.
- **WhatsApp:** só pela conta oficial/Business com opt-in (ver depto-ti). Até lá, e-mail ou formulário.
- Ferramenta de formulário: a definir com o TI (Microsoft Forms do M365 da Save é o candidato natural, dados no tenant da empresa).
