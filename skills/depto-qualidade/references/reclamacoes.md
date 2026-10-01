# Análise de Reclamações — taxonomia de causa-raiz (v1, 29/09/2026)

Serve hoje para conversas de **WhatsApp coladas** e amanhã para os chamados do **GLPI**. A mesma ficha e os mesmos códigos valem para os dois, para a série histórica não quebrar na troca de canal.

## 1. O que é reclamação (e o que não é)
**Reclamação** = expressão de insatisfação com a Save, seus serviços ou o tratamento de uma reclamação anterior, em que uma resposta ou solução é esperada, explícita ou implicitamente (definição da ISO 10002, 3.2).
Não é reclamação: pedido normal de status (vai para a Triagem da célula da Daniela), dúvida técnica (Geovana/Tributário), sugestão (registrar como "elogio/sugestão").
**Na dúvida, registre.** Cobrança repetida do mesmo pedido (3ª vez ou mais) **vira reclamação** mesmo sem a palavra "reclamação".

Código de entrada: `QLD-RECLAMACAO` (já usado na célula da Daniela, SLA "mesmo dia").

## 2. Três eixos de classificação
Cada caso recebe **um** código de cada eixo.

### Eixo A — Tema (o que o reclamante sentiu)
| Código | Tema | Exemplos |
|---|---|---|
| A1 | **Prazo / retorno** | "Ninguém me responde", parecer atrasado, contrato não chegou |
| A2 | **Comunicação** | Informação divergente entre áreas, status confuso, linguagem técnica demais |
| A3 | **Expectativa comercial** | "Me disseram que ia dar R$ X / sair em 30 dias" → **dispara auditoria de promessa** do material/mensagem de origem |
| A4 | **Resultado técnico** | Crédito abaixo do diagnóstico, zerado, indeferimento, glosa |
| A5 | **Repasse / comissão** | Atraso, valor divergente, falta de extrato (encaminha ao depto-operacoes-canal) |
| A6 | **Cobrança de honorário** | Boleto, valor, momento da cobrança ao cliente (depto-pos-venda) |
| A7 | **Contrato** | Minuta errada, dados errados, distrato (depto-contratos) |
| A8 | **Conflito de canal** | "Esse cliente é meu" (depto-operacoes-canal) |
| A9 | **Atendimento / conduta** | Tom, falta de cortesia, promessa pessoal |
| A10 | **Dados / privacidade** | Dado enviado à pessoa errada, uso indevido → **incidente LGPD: escala no mesmo dia ao depto-juridico** |
| A11 | **Sistemas / acesso** | GLPI, portal, links (depto-ti) |

### Eixo B — Onde nasceu (etapa da jornada)
B1 Prospecção/abordagem · B2 Onboarding do parceiro · B3 Diagnóstico/parecer · B4 Contrato · B5 Execução/PER · B6 Pós-venda (ressarcimento, compensação de ofício, guias) · B7 Repasse ao parceiro · B8 Atendimento/ponte da área Partners

### Eixo C — Causa-raiz (por que aconteceu), depois dos "5 porquês"
| Código | Causa | Controlável pela Save? |
|---|---|---|
| C1 | **Processo**: etapa sem dono, sem SLA, passagem de bastão falha | Sim |
| C2 | **Informação**: dado errado/ausente no HubSpot, documento faltante não pedido a tempo | Sim |
| C3 | **Promessa**: expectativa criada por material, mensagem ou fala (Save ou parceiro) | Sim (Save) / Parcial (parceiro) |
| C4 | **Capacidade**: fila, volume acima da equipe | Sim |
| C5 | **Competência / critério técnico**: erro ou divergência técnica | Sim |
| C6 | **Sistema / ferramenta** | Sim |
| C7 | **Cliente / parceiro**: documento não enviado, dado incorreto fornecido | Não (mas dá para prevenir com checklist) |
| C8 | **Externo**: Receita Federal (prazo do PER, intimação), mudança de norma, Judiciário | Não (mas a comunicação é controlável) |

Regra: C8 raramente é a causa-raiz inteira. "O PER demorou" (C8) + "ninguém avisou o prazo médio" (C1/C3) → registre a controlável como causa principal e a externa como contribuinte.

## 3. Severidade
| Nível | Critério | Primeira resposta | Plano / solução |
|---|---|---|---|
| **S1 Crítica** | Risco jurídico, LGPD, ameaça de saída de Master, impacto > R$ 100 mil, exposição pública | **mesmo dia** (Luis + Jurídico se for o caso) | plano em 2 d.u. |
| **S2 Alta** | Master ou cliente com dinheiro atrasado/errado; 3ª cobrança | 1 d.u. | 5 d.u. |
| **S3 Média** | Insatisfação com prazo/comunicação sem perda financeira | 1 d.u. | 10 d.u. |
| **S4 Baixa** | Incômodo pontual, sugestão | 2 d.u. | 15 d.u. |
Os valores de R$ e os prazos são proposta; validar com o Luis (perguntas-luis.md).

## 4. Ficha da reclamação (uma por caso)
Salvar em `~/agentes-partners/departamentos/qualidade/reclamacoes/AAAA-MM-DD-<id>.md`:
```
ID: QLD-AAAA-NNN · Canal: WhatsApp colado | GLPI #__ | e-mail | pesquisa (detrator)
Recebida em: AAAA-MM-DD · Reclamante: [PARCEIRO-A] / [CLIENTE-A] (tipo: Master | indicador | cliente)
Negócio HubSpot: <ID> (se houver)
Fatos (sem adjetivos): ...
O que o reclamante espera: ...
Tema A_ · Etapa B_ · Causa C_ (principal) + C_ (contribuinte) · Severidade S_
5 porquês: 1) ... 2) ... 3) ...
Área responsável pela solução: ...   Dono humano: ...
Prazos: 1ª resposta até __ · solução até __
Ação corretiva (o caso) · Ação preventiva (o processo): ...
Encerramento: data · reclamante confirmou? · CSAT do tratamento
```

## 5. WhatsApp colado (enquanto o GLPI não entra)
1. Quem colar a conversa (Luis/Daniela) confirma que ela veio de um canal de trabalho.
2. O agente **pseudonimiza antes de analisar**: nomes → [PESSOA-1], telefones/e-mails → removidos, CNPJ → [CNPJ] (fica só o ID do negócio no HubSpot, se houver).
3. Extrai **só os trechos de insatisfação** e preenche a ficha. **A conversa bruta não é salva** na pasta de Qualidade.
4. Classifica nos três eixos, sugere severidade e dono e rascunha a **resposta de acolhimento** (sem prometer prazo que a área não confirmou). Ninguém envia nada: o rascunho vai para a Daniela/Luis.
5. Registra uma linha em `reclamacoes/registro.csv` (colunas iguais aos campos que se propõe criar no GLPI).

## 6. Quando o GLPI entrar (proposta ao depto-ti, não decidido)
Categoria **Qualidade** com subcategorias = Eixo A (`QLD-A1` … `QLD-A11`); campos obrigatórios no encerramento: etapa (B), causa (C), severidade (S), ação preventiva (texto), "reclamante confirmou" (sim/não). Com isso, o relatório mensal sai por script direto da API.

## 7. Análise mensal (Pareto)
- Volume por tema, etapa e causa; % controlável; tempo médio de 1ª resposta e de solução vs. prazo; reincidência (mesmo reclamante ou mesma causa em 90 dias); CSAT do tratamento.
- **Pareto:** as 2–3 causas que explicam ~80% dos casos viram proposta de ação preventiva com dono (vai ao Luis; se cruza áreas, ao Gabinete).
- Com poucos casos (< 20/mês), mostre a lista e os padrões; não calcule percentuais que enganam.
