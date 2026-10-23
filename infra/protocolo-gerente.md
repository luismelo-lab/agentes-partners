# Protocolo do Gerente: nada volta sem a revisão do gerente da área
**Regra do Luis (15/10/2026).** Toda área e toda célula tem um **gerente** e **especialistas** com focos diferentes. Os especialistas fazem o trabalho e o gerente revisa antes de qualquer retorno. Vale para pedido, demanda, originação, alerta do plano do dia, chamado, relatório e lote.

```
Demanda ─► Gerente da área A distribui ─► Especialistas de A trabalham ─► Gerente de A revisa
                                                  ▲                            │
                                                  └─── precisa de revisão ─────┤ (volta ao especialista responsável, com o que corrigir)
                                                                               │
                         precisa de outra área ─► Gerente da área B distribui ─► Especialistas de B ─► Gerente de B revisa ─► volta ao Gerente de A
                                                                               │
                                                                    aprovado ─► Gerente de A consolida e devolve (3 blocos)
```

## 1. Distribuir
O gerente lê a demanda e escolhe **os especialistas certos**: só os necessários, mas todos os necessários. A lista de especialistas está em `references/equipe.md` da skill da área ou no próprio SKILL.md. Cada especialista recebe o pedido, os dados de apoio e a pergunta que deve responder.

## 2. Revisar (checagem do gerente, item a item)
1. **Responde o que foi pedido?** Com dado conferido e fonte, e não suposição.
2. **Entrega o que a pessoa precisa?** Os três blocos de `infra/padrao-entrega.md`: o que você pediu, o que você também precisa, o que falta e quem fornece.
3. **Está correto?** Regra técnica, prazo (cálculo duplo no Jurídico) e números batendo com o HubSpot, o parecer e a Receita.
4. **Está pronto para usar?** Ação concreta e rascunho específico do caso, sem modelo genérico.
5. **Segue as regras da casa?**
   - não promete valor nem prazo de êxito;
   - alíquota zero só via PER;
   - LGPD;
   - nada vai a parceiro ou cliente sem a pessoa decidir.
6. **Precisa de outra área?** Se a resposta depende de outra área, encaminhe a ela (passo 4).

## 3. Revisão automática
- **Se algum item falhar,** o gerente devolve ao especialista responsável dizendo o que corrigir. O especialista refaz e o gerente reavalia.
- **No máximo 2 rodadas de revisão por especialista.** Se ainda faltar algo, o gerente entrega o que está certo e põe a lacuna em "o que falta e quem fornece". Ele nunca devolve trabalho inacabado como se estivesse pronto.

## 4. Passagem para outra área
- **O gerente de A encaminha ao gerente de B** com a pergunta exata.
- **O gerente de B distribui aos especialistas dele** e segue os passos 1 a 3. Depois devolve ao gerente de A, que faz a revisão final e consolida.
- **Cada área só responde pela sua parte.** A resposta final é uma só, no nome do gerente de A.
- **Exemplos:**
  - demanda de contrato com dúvida de tese: de Contratos ao Tributário;
  - recorrência com ação judicial: do Recuperador ao Jurídico;
  - originação com conflito: de Intel Comercial a Operações de Canal.

## 5. Registro da revisão (vai junto com toda entrega)
```json
"revisao": {"gerente": "Gerente de Contratos", "especialistas": ["Conferente de Dados", "Controle de Assinaturas"],
            "rodadas": 1, "areas_consultadas": ["Tributário"], "aprovado": true, "ajustes": "o que o gerente mandou corrigir, em 1 frase"}
```
Quando a entrega chega ao time, aparece com a linha "Revisado por <gerente> · <n> rodada(s) · consultou <áreas>".

### 5.1 Aprovação precisa de conteúdo (regra do Luis de 23/10/2026)
Das 188 análises registradas até 23/10/2026, todas foram aprovadas na 1ª rodada sem ajuste: a revisão não estava sendo aplicada. A partir de agora:
- **Toda revisão aprovada registra um ajuste concreto ou o motivo de não haver ajuste.**
  - Com ajuste, `ajustes` diz o que mudou e onde. Exemplo: "trocou 'compensar' por 'pedir ressarcimento (PER)' no bloco 1; acrescentou a LC 224, art. 4º, § 7º".
  - Sem ajuste, `sem_ajuste_motivo` diz o que o gerente conferiu e por que passou. Exemplo: "conferi as normas citadas (Lei 11.457, art. 24; D14) no arquivo do especialista e o texto no auditor de promessas, com 0 achados; o encaminhamento ao Jurídico está certo".
- **Aprovação "vazia" é defeito.** Isso vale para `ajustes` vazio, "ok", "nenhum", "aprovado" ou "sem ajustes", sem o motivo, e para o motivo genérico ("está bom", "segue o padrão"). O `depto-qualidade` conta esse defeito como "revisão não aplicada" na taxonomia de defeitos das entregas. Ele entra na amostragem da semana e volta ao gerente da área.
- **O motivo cita o que foi conferido.** Pelo menos um destes itens: a norma ou a decisão conferida, o número batido com a fonte, o auditor de promessas rodado, o encaminhamento checado ou o caso de teste parecido (`references/casos-teste.md`).
- **Sinal de alerta:** área com mais de 80% de aprovações na 1ª rodada sem ajuste por 2 semanas seguidas. O `depto-qualidade` amostra 3 entregas dela, e o `arquiteto-agentes` compara com o acerto nos casos de teste (`infra/avaliar_casos.py`).

```json
"revisao": {"gerente": "Gerente Tributário", "especialistas": ["Alíquota Zero e PER"], "rodadas": 1, "areas_consultadas": [],
            "aprovado": true, "ajustes": "",
            "sem_ajuste_motivo": "conferi D14 e a Lei 11.457, art. 24, no especialista; auditor de promessas com 0 achados; não precisa de outra área"}
```

## Como executar nas rotinas
- **Com a ferramenta Agent:** um subagente por área no papel de gerente. Ele cria subagentes para os especialistas, revisa, devolve e consolida. A passagem para outra área é outro subagente-gerente.
- **Sem a ferramenta Agent:** a mesma sequência, em papéis explícitos e numa ordem fixa:
  1. o gerente distribui;
  2. cada especialista responde;
  3. o gerente revisa pelo checklist;
  4. se for preciso, o especialista refaz;
  5. o gerente consolida.

  Não pule a revisão.

## Especialista sênior (Luis, 22/10/2026)
O gerente distribui pelo arquivo do especialista (`skills/<área>/references/especialistas/<slug>.md`) e, na revisão, confere se a entrega usou o método, a base normativa e as regras da casa dele (`infra/padrao-senior.md`). Uma entrega que só repete o SKILL.md volta para refazer.
