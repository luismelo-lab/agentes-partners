# Sistema de gestão · contrato dos dados (26/10/2026)

Pedido do Luis: "utilizar toda a capacidade dos agentes e do Conselho para gerar informações de tomada de decisão que gerem resultado, previsibilidade e controle". Quatro frentes produzem JSON em `~/agentes-partners/registro/gestao/`, com este contrato, e o painel do Luis lê o `gestao.json` consolidado. Todo valor em R$ é inteiro; toda métrica traz fonte e confiança; nada de nome de cliente.

## 1. `pacote-<AAAA-MM-DD>.json` (Resultado e controle · Controller com Dados)
```json
{"data": "2026-10-26", "periodo": {"semana_de": "2026-10-19", "mes": "2026-10", "trimestre": "2026-Q4"},
 "meta": {"unidade": "credito_contrato_fechado", "decisao": "D111",
          "mes_atual": {<item de meses>},
          "meses": [{"mes": "2026-10", "nome", "meta_rs": 75000000, "realizado_rs", "realizado_bruto_rs", "duplicidade_rs", "falta_rs", "pct", "pct_do_proporcional",
                     "dias_uteis_total", "dias_uteis_decorridos", "dias_uteis_restantes", "ritmo_planejado_rs_dia", "ritmo_necessario_rs_dia", "ritmo_atual_rs_dia",
                     "situacao": "a iniciar|em andamento|encerrado", "status": "verde|amarelo|vermelho|cinza"}],   // out 75, nov 100, dez 75 mi
          "total": {"meta_rs": 250000000, "realizado_rs", "falta_rs", "pct", "ritmo_necessario", "ritmo_atual", "status", ...},
          "por_master": {"proposta": true, "metodo", "masters": [{"master", "peso_pct", "meses": [{"mes", "meta_rs", "realizado_rs", "pct"}], "meta_q4_rs"}]},
          // compatibilidade (derivadas do total):
          "q4_rs": 250000000, "realizado_rs": 0, "falta_rs": 0, "dias_uteis_restantes": 0, "ritmo_necessario_rs_dia": 0, "ritmo_atual_rs_dia": 0, "leituras": {"credito", "liquido"}},
 "metricas": [{"id": "ganhos_mes_rs", "nome": "Fechado no mês (limpo)", "bloco": "resultado|caixa|canal|risco|operacao",
   "valor": 0, "unidade": "R$|%|n|dias", "anterior": 0, "variacao_pct": 0, "meta": null, "tolerancia": {"verde": ">= 0.9*meta", "amarelo": ">= 0.7*meta"},
   "status": "verde|amarelo|vermelho|cinza", "fonte": "hubspot 26/10 06:53", "confianca": "alta|media|baixa", "nota": "texto curto"}],
 "confiabilidade": {"indice_qualidade_ganhos": 0, "ganhos_sem_honorario_pct": 0, "duplicados_grupos": 0, "volume_bruto_rs": 0, "volume_limpo_rs": 0},
 "alertas": [{"texto": "", "area": "", "severidade": "alta|media|baixa"}]}
```
Status: verde dentro da tolerância, amarelo fora da verde, vermelho fora da amarela, cinza sem dado ou sem meta.

## 2. `previsao-<AAAA-MM-DD>.json` (Previsibilidade · Resultados com Pós-venda e Tributário)
```json
{"data": "2026-10-26", "horizonte_semanas": 13,
 "cenarios": {"conservador": {"fechamento_q4_rs": 0, "liquido_q4_rs": 0, "premissas": ["..."]},
              "base": {"fechamento_q4_rs": 0, "liquido_q4_rs": 0, "premissas": ["..."]},
              "meta": {"fechamento_q4_rs": 250000000, "liquido_q4_rs": 0, "o_que_precisa": ["..."]}},
 "caixa_13_semanas": [{"semana": "2026-W44", "entrada_rs_base": 0, "entrada_rs_conservador": 0, "fonte": "PER/compensação/parcelamento"}],
 "pipeline_por_safra": [{"safra": "2026-08", "aberto_rs": 0, "conversao_real_pct": 0, "esperado_rs": 0}],
 "decadencia_mensal": [{"mes": "2026-11", "credito_que_sai_rs": 0, "clientes_n": 0}],
 "janelas": [{"janela": "", "prazo": "2026-10-30", "base_rs": 0, "clientes_n": 0, "area": ""}],
 "riscos": [{"risco": "", "probabilidade": "alta|media|baixa", "impacto_rs": 0, "mitigacao": "", "dono": "", "prazo": "2026-11-05"}]}
```

## 3. `controle-<AAAA-MM-DD>.json` (Controle · Gabinete com Qualidade, Canal e Dados)
```json
{"data": "2026-10-26",
 "regras": [{"id": "C01", "metrica": "ganhos_mes_rs", "condicao": "status == vermelho por 2 semanas", "acao": "Conselho revisa o plano da semana", "dono": "luis|daniela|jenifer|geovana|controller|gerente-<area>", "prazo_dias": 3, "alcada": "luis|dona|gerente"}],
 "desvios": [{"regra": "C01", "metrica": "", "valor": 0, "limite": 0, "desde": "2026-10-19", "acao": "", "dono": "", "prazo": "2026-10-29", "status": "aberto|em_andamento|resolvido"}],
 "ritual": [{"quando": "segunda 7h30", "quem": "Conselho", "o_que": "pacote + previsão + desvios", "saida": "ata com decisões"}]}
```

## 4. `gestao.json` (consolidado para o painel · `infra/gestao.py`)
`{"data", "meta", "semaforo": [metricas com status], "previsao": {cenarios, caixa_13_semanas}, "desvios": [...], "decisoes": [{"id": "D101", "texto", "dono", "prazo", "status"}], "acoes": [{"acao", "dono", "prazo", "origem": "conselho|controle", "status"}]}`. O `infra/portal_dados.py` copia para `portal/dados.json` em `gestao`; a tela "Gestão" do painel do Luis mostra.

Desde 26/10/2026 (tela v3): `semaforo[i].pre_analise` vem de `pre-analise-<data>.json` (por `metrica_id`: leitura, causa {fatos, hipoteses}, acoes, decisao_sugerida, efeito, confianca, melhorar_confianca, area, especialista, pendente); `decisoes_sugeridas` vem de `decisoes_luis` do mesmo arquivo; `decisoes[i].dossie` vem de `dossies/<id>.json` (o `indice.json` é ignorado) e `dossies` traz os dossiês de decisões fora da lista acima. Tudo opcional: sem arquivo, `null` e um aviso. No perfil time, nada disso vai ao painel.

## Regras
- Métrica sem meta aprovada: status cinza e `meta: null`, mas com `tolerancia` sugerida e marcada "proposta".
- Meta do Q4 (D111, 26/10/2026): crédito de contrato fechado, mensal 75/100/75 = R$ 250 mi; mostrar primeiro a meta do mês (`mes_atual`), depois a total. Realizado no volume limpo. A previsão traz `por_mes` (cenários conservador/base/esforço por mês, probabilidade e `novembro_precisa`); o cenário `esforco` entra ao lado de `meta` em `cenarios`.
- Volume limpo = volume sem os grupos de duplicidade de alta confiança (`saneamento_duplicados.py`).
- Nunca prometer: cenários são estimativas com premissas escritas.
