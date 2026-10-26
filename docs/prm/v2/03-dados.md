# PRM Save · 03 · Modelo de dados e integração

**Versão:** 2.0 · **Data:** 26/10/2026 · **Área:** Dados & BI (Gerente de Dados, com os 5 especialistas) · **Para:** o desenvolvedor do PRM e o Luis
**Base:** `docs/prm/desenho-prm-save-2026-10-26.md` (13 tabelas, 8 módulos, 5 fases), `docs/prm/contexto-interno-prm-2026-10-26.md` §4, `central/` (índice HMAC, esteira, consulta), `lib/` (demandas, histórico, caixa, CNPJ, proteção), `infra/portal_dados.py`.
**Números:** download do HubSpot de 26/10/2026 às 13h31 (5.051 negócios, escopo da Área Master), salvo indicação. Nenhum nome de cliente ou de parceiro neste documento.
**Arquivos desta entrega:**
| Arquivo | O que é |
|---|---|
| `docs/prm/v2/schema.sql` | Esquema T-SQL do Azure SQL: 41 tabelas em 6 esquemas, índices, RLS, cifragem, retenção, views das métricas |
| `docs/prm/v2/03-dados.md` | Este documento |
| `skills/depto-dados/scripts/prm_local.py` | Gerador do modo local (Fase 1): as mesmas tabelas em JSON em `registro/prm/`, com checagem de CNPJ na entrada |

---

## 1. Esquema do banco (Azure SQL)

### 1.1 Princípios
1. **O HubSpot é a fonte do negócio e é só leitura.** O esquema `hs` é um espelho: só a identidade da sincronização grava nele. Nenhuma tela, rotina ou pessoa edita `hs.*`, e não existe caminho de volta do PRM para o HubSpot.
2. **O PRM é a fonte do que nasce na relação com o parceiro:** parceiro, usuário, termo, registro, conflito, extrato, demanda, nível e material (esquema `prm`).
3. **O que a Central já faz entra como está** (esquema `central`): as mesmas chaves, os mesmos estados e a mesma mensagem neutra.
4. **A chave da relação comercial é a raiz do CNPJ** (8 posições, alfanumérica desde a IN RFB 2.229/2024), sempre como **HMAC-SHA256 com o sal `CENTRAL_SAL`**, igual ao `negocio_ativo.chave()`. Assim, o índice da Central, o registro do PRM e o espelho do HubSpot se cruzam sem que o CNPJ precise estar em claro.
5. **Mesmas colunas no JSON local e no SQL:** o que a Fase 1 grava em `registro/prm/` é carregado sem transformação na Fase 2.

### 1.2 Mapa: as 13 tabelas do desenho e as tabelas físicas
| Tabela do desenho | Tabela física | Esquema | Grão / chave | Origem |
|---|---|---|---|---|
| `parceiro` | `prm.parceiro` (temporal) + `prm.parceiro_alias` | prm | 1 por escritório, consultor ou indicador · `parceiro_id` (`P-0001`) | Carga inicial do roster e aliases; depois a Daniela |
| `usuario_parceiro` | `prm.usuario_parceiro` + `seg.aceite_termo_uso` | prm, seg | 1 por pessoa com login · `usuario_id`; `entra_oid` único | PRM (convite B2B) |
| `termo` | `prm.termo` (temporal) | prm | 1 vigente por parceiro · `termo_id` | Contratos (D65); carga do `percentual-parceiros.json` |
| `registro_oportunidade` | `prm.registro_oportunidade` | prm | 1 por registro · `registro_id` (`R-2026-000001`) | PRM |
| `registro_evento` | `prm.registro_evento` (ledger só de inclusão) | prm | 1 por mudança de estado | PRM |
| `conflito` | `prm.conflito` + `prm.conflito_parte` | prm | 1 por raiz em disputa · `conflito_id` | `conflito_canal.py` (herdados) e checagem do registro |
| `negocio` (espelho) | `hs.negocio` + `hs.negocio_etapa_hist` + `hs.negocio_tese` + `hs.negocio_stage` | hs | 1 por deal · `deal_id` | HubSpot, só leitura |
| `extrato_linha` | `prm.extrato_linha` (ledger) + `prm.extrato_lote` + `prm.extrato_retencao` + **`prm.recebimento`** | prm | 1 por deal × família × competência | PRM; recebido vem do Financeiro |
| `contestacao` | `prm.contestacao` | prm | 1 por contestação | PRM |
| `demanda` | `prm.demanda` + `prm.demanda_evento` | prm | 1 por demanda · `demanda_id` (`D-AAAA-NNNN`, o mesmo do registro único) | `lib/registro_demandas.py` e portal |
| `nivel_apuracao` | `prm.nivel_apuracao` | prm | parceiro × trimestre | `metricas_ps.py` |
| `material` | `prm.material` | prm | 1 por peça | Marketing |
| `acesso_log` | `seg.acesso_log` | seg | 1 por ação | Function (API) |

**Trazidas da Central (pedido do Luis):**
| Arquivo de hoje | Tabela física | Observação |
|---|---|---|
| `dados-publicos/receita/consultas-regime.jsonl` e `central-esteira/historico/*.json` | `central.consulta_regime` | Uma tabela serve à trilha e ao "histórico do parceiro" (últimas 30, `ix_consulta_parceiro`); o motivo real do bloqueio fica em `motivo_interno` |
| `central-esteira/pedidos/E-NNNN.json` | `central.esteira_pedido` + `central.esteira_evento` | Dossiê em JSON (9 seções); o Word não entra no banco (gerado sob demanda) |
| `central-esteira/indice-negocios-ativos.json` | `central.vw_indice_negocio_ativo` (view) | Na Fase 2 o índice deixa de ser arquivo: sai do próprio `hs.negocio` |
| `lib/historico.py avaliar` + `registro/medicao-respostas.json` | `central.resposta_historico` | Critério, confiança, fontes (sem trecho de conversa), rascunho cifrado, aprovação da Daniela, medição D28 |
| `registro/chamados-propostos.json` / `chamados-para-painel.json` | `central.chamado_proposto` | Proposto → aprovado/recusado no painel → GLPI (só com aprovação) |
| `registro/caixa/pendentes.jsonl`, `entregues.jsonl`, `lidas.json` | `central.caixa_mensagem` + `central.caixa_leitura` | Acrescenta `para = parceiro` para a caixa do portal (Fase 2) |
| `central-agentes/registro.json` (P-NNNN) | `central.pedido_agente` | `demanda_id` liga ao registro único |

**Apoio:** `ref.*` (estado do parceiro, pipeline, etapa → estado, tese, produto, tipos de SLA, feriados, política de retenção) e `ops.*` (execuções de sincronização com trava de uma carga por fonte, achados de qualidade, procedimento de expurgo).

### 1.3 Dado pessoal e de cliente: classes e proteção
| Classe | O que é | Exemplos de coluna | Como protege |
|---|---|---|---|
| **P0** | Sem dado pessoal nem de cliente | etapa, estado, percentuais, valores, datas, ids | Permissão por esquema e RLS |
| **P1** | Pessoa do parceiro ou do time | `usuario_parceiro.nome`, `.email`, `hs.negocio.parceiro_bruto`, `.indicado_por_email`, `nome_exibicao` de indicador pessoa física | **Dynamic Data Masking** (`email()`, `partial()`); só a Function e o perfil Save com `UNMASK` veem em claro |
| **P2** | Dado de cliente | CNPJ, razão social, contato do decisor, texto livre de demanda, rascunho de resposta, descrição de chamado | **Always Encrypted aleatório** (`CEK_PRM`, chave mestra no Key Vault). Só a Function decifra. A busca usa a coluna `*_hmac` e a tela mostra `cnpj_mascara` (2 primeiras e 2 últimas posições). O painel interno não tem acesso à chave |
| **P3** | Proibido | CPF, RG, CNH, conta, PIX, senha | Não há coluna. A API passa todo texto por `lib/protecao.limpo` e recusa a gravação quando acha P3 (R24) |

**Outras camadas:**
- **Row-Level Security** (`seg.pol_parceiro`): a Function grava no `SESSION_CONTEXT` o perfil, o `parceiro_id` e o papel do token validado. O parceiro vê só o dele; o titular do escritório vê também os consultores (`master_id`); o perfil Save vê tudo. O predicado de bloqueio impede gravar registro em nome de outro parceiro (R12).
- **Ledger:** `prm.registro_evento` (só inclusão) prova o carimbo de hora do registro em caso de disputa; `prm.extrato_linha` (ledger atualizável) guarda o histórico de cada linha à prova de adulteração, para a contestação. Se o ledger trouxer limitação na implantação (chave estrangeira ou coluna), a alternativa é tabela temporal, com a mesma retenção.
- **Temporal:** `prm.parceiro` (5 anos) e `prm.termo` (10 anos) guardam quem mudou o quê e quando.
- **Classificação de sensibilidade** (`ADD SENSITIVITY CLASSIFICATION`) nas colunas P1 e P2, para auditoria do Azure SQL e o Microsoft Purview.
- **Troca do sal:** como o CNPJ está cifrado no banco, a Function recalcula as colunas `*_hmac` com o sal novo, e o índice da Central é refeito no mesmo dia.

### 1.4 Retenção (proposta, a validar com o Jurídico antes da Fase 2)
| Tabela | Ação | Prazo | Contado de | Base |
|---|---|---|---|---|
| `hs.negocio` | substituir | cada carga | — | Espelho; o HubSpot é a fonte |
| `hs.negocio_etapa_hist` | apagar | 5 anos | saída da etapa | Série do funil |
| `prm.registro_oportunidade` (não convertido) | anonimizar contato, evidência e "como conhece" | 24 meses | fim da validade | LGPD arts. 15 e 16; o carimbo e a raiz HMAC ficam para o desempate |
| `prm.registro_oportunidade` (convertido) | anonimizar contato | 12 meses | vínculo com o deal | O contato passa a viver no HubSpot |
| `prm.registro_evento` | manter | — | — | Sem dado pessoal; prova do registro |
| `prm.extrato_linha`, `contestacao` | manter / apagar | 5 anos | pagamento / resposta | CTN art. 173 e CC art. 206, §5º, I **[validar Jurídico]** |
| `prm.demanda` | apagar o texto cifrado | 24 meses | resolução | Os dados de SLA ficam |
| `central.consulta_regime`, `central.esteira_pedido` | apagar | 12 meses | consulta / criação | Minuta de termos da consulta (`departamentos/ti/minuta-termos-consulta-parceiros.md`) |
| `central.resposta_historico` | apagar o rascunho | 12 meses | avaliação | A medição D28 fica |
| `central.caixa_mensagem` | apagar | 180 dias | criação | Notificação operacional |
| `seg.acesso_log` | apagar | 12 meses | acesso | Marco Civil, art. 15 (mínimo de 6 meses) |
| `prm.usuario_parceiro` | anonimizar | 180 dias | desativação | O id fica para a trilha |

O `ops.usp_expurgar` aplica a tabela (agendado diariamente pela Function). Os prazos estão também em `ref.retencao`, para auditoria.

---

## 2. Mapeamento HubSpot → PRM

### 2.1 Escopo do download (igual ao de hoje)
`skills/depto-resultados/scripts/hubspot_fonte.py --baixar`: negócios da Daniela (owner da Área Master) **mais** negócios cujo `nome_do_parceiro` contém um nome do roster (busca `CONTAINS_TOKEN` e filtro do falso positivo), criados desde 01/01/2024, em todos os 9 funis. A Fase 2 mantém esse escopo e acrescenta os negócios com `id_registro_prm` preenchido (§3.5).

**Funis e volumes (26/10):** RT – Real & Presumido 4.733 · Gestão de Passivo 212 · RT – Simples Nacional 58 · Save Partners – BDR/SDR 25 · Produtos Tributários 7 · Produtos Jurídicos 6 · Planejamento Tributário 5 · Save Partners – Closer 4 · Enriquecimento 1. Situação: 1.696 ganhos, 2.985 perdidos, 370 abertos.

### 2.2 Campo a campo
Transformações comuns: `pct()` = percentual em fração (`30` e `0.3` viram 0,30); `dia_br()` = data UTC convertida para o dia de Brasília; `norm()` = maiúsculas, sem acento e com espaços simples; `hmac()` = `negocio_ativo.chave()`.

| Propriedade interna (HubSpot) | Chave no download | Coluna no PRM | Transformação | Funis | Preenchimento hoje |
|---|---|---|---|---|---|
| `hs_object_id` | `id` | `hs.negocio.deal_id` | inteiro | todos | 100% |
| `pipeline` | `pipeline` | `pipeline_id` → `ref.pipeline` | id interno; o nome vem de `/crm/v3/pipelines/deals` | todos | 100% |
| `dealstage` | `etapa`, `status`, `prob` | `etapa_id`, `status_hs`, `estado_id` | `isClosed` e probabilidade definem aberto, ganho ou perdido; `ref.etapa` define o estado do parceiro (§2.3) | todos | 100% |
| `dealname` | `nome` | `empresa_nome_cif` (P2) | cifrado; **não vai ao JSON local** | todos | 100% |
| `amount` | `valor` | `valor_credito` | decimal; é crédito estimado, não honorário | todos | ganho 94,1% · aberto 62,9% |
| `createdate` | `criado` | `criado_em` | `dia_br()`; regravada nas importações → usar `data_efetiva` | todos | 100% |
| `closedate` | `fechado` | `fechado_em` | data escolhida no CRM, sem conversão | ganho/perdido | 100% dos ganhos |
| (calculado) | — | `data_efetiva` | menor entre criação e fechamento, se fechado | — | — |
| `hs_lastmodifieddate` | `extras.ultima_modificacao` | `hs_modificado_em` | marca d'água da carga incremental | todos | 100% |
| `hs_v2_date_entered_current_stage` | `extras.entrou_etapa` | `entrou_etapa_em` | UTC | todos | 100% |
| `notes_last_updated` | `extras.ultima_atividade` | `ultima_atividade_em` | UTC | todos | ganho 27,8% · aberto 96,0% |
| `hubspot_owner_id` | `owner` | `owner_id` | texto | todos | 100% |
| `nome_do_parceiro` | `parceiro_bruto` (+ `parceiro` canônico) | `parceiro_bruto` (P1), `parceiro_id`, `master_id` | `norm()` → `prm.parceiro_alias` (roster, consultores e `aliases-parceiros.json`); inválidos (`0`, `-`, `N/A`, numéricos) → sem parceiro | todos | ganho 75,6% · aberto 82,0%; 70 grafias distintas; 465 negócios sem nome |
| `email_de_quem_esta_indicando_o_leadcliente` | `extras.indicado_por_email` | `indicado_por_email` (P1, mascarado) | minúsculas | RT, BDR | ganho 7,7% (130) · aberto 60,5% (224) |
| `nome_de_quem_esta_indicando_o_lead_cliente` | `extras.indicado_por_nome` | ajuda na resolução do `parceiro_id` (não é gravado) | `norm()` | RT, BDR | igual ao anterior |
| `cnpj_` | `extras.cnpj` | `cnpj_cif` (P2), `cnpj_hmac`, `cnpj_raiz_hmac`, `cnpj_mascara`, `cnpj_situacao` | `normalizar_cnpj` → `cnpj_valido` (DV, alfanumérico) → `raiz_cnpj` → `hmac()` | todos | 4.938 válidos · 66 vazios · 47 inválidos · 0 alfanuméricos |
| `estado`, `cidade` | `extras.uf`, `extras.cidade` | `uf`, `cidade` | UF com 2 letras | todos | UF: ganho 99,5% |
| `qual_e_o_regime_tributario_da_empresa_` | `extras.regime` | `regime` | lista | todos | ganho 99,6% |
| `porte_da_empresa`, `faixa_de_faturamento_anual_estimado`, `faturamento` | `extras.porte`, `extras.faixa_faturamento`, `extras.faturamento` | `porte`, `faixa_faturamento` | lista; o faturamento em R$ não entra no PRM (não é preciso) | RT | faturamento: ganho 80,8% |
| `cnae`, `descricao_do_cnae` | `cnae`, `segmento` | `cnae`, `segmento`, `cafe` | 7 dígitos; `cafe` = regra do café (CNAE ou palavra, ganhos fechados desde abr/2026) | RT | ganho 91,3% |
| `honorarios_contratuais` | `hContr` | `honorario_pct` | `pct()` | ganho | **43,0% dos ganhos (966 vazios)** |
| `honorarios_parceiro` | `hParc` | `parceiro_pct_card` | `pct()`; o % oficial é o do `prm.termo` (R1, D64) | ganho | 72,9% dos ganhos; 451 vazios com parceiro; 7 acima de 100% |
| `honorarios_vendedor`, `_gestor_comercial`, `_indicador`, `honorariosdo_coordenador` | `outras_comissoes.*` | `vendedor_pct`, `gestor_comercial_pct`, `indicador_pct`, `coordenador_pct` | `pct()`; **nunca vão à visão do parceiro** (R12) | ganho | sem regra (OC-5) |
| `teses_tributarias_aplicadas_neste_negocio_` | `variante` | `teses_hs` → `hs.negocio_tese` | divide a multisseleção por `;` e casa com `ref.tese.valor_hubspot` | RT | ganho 46,5% (908 sem tese) |
| `e_cac_liberado_` | `extras.ecac` | `ecac_liberado` | `true`/`false`/vazio | RT | 285 de 5.051 |
| `parecer_complementar`, `anexo_do_diagnostico`, `parecer_juridico` | `extras.parecer_rt`, `anexo_diagnostico`, `parecer_juridico` | `tem_parecer`, `tem_anexo_diagnostico` | só "tem ou não tem"; o arquivo não entra (sem escopo `files`) | RT, Passivo | — |
| `id_bitrix` | `extras.id_bitrix` | `id_bitrix` | texto; chave da execução e do dedupe (R1 do saneamento) | RT | ganho 67,3% (1.142) |
| `hs_was_imported` | `extras.importado` | `importado` | booleano | todos | 1.230 dos ganhos (72,5%) |
| `hs_forecast_amount` | `extras.forecast` | — (fica no depto-resultados) | — | — | — |
| `hs_merged_object_ids` | **não baixado hoje** | `ops` (mapa de deal mesclado) | a acrescentar no download: religa o registro quando o CRM mescla cards | todos | — |

### 2.3 Etapa → estado do parceiro (proposta para a fase 0)
Aplicado em `ref.etapa` (SQL) e em `ESTADO_ETAPA` no `prm_local.py`. Abertos em 26/10: Recebido 67 · Em diagnóstico 52 · Precisa de algo de você 9 · Apresentação marcada 186 · Contrato em andamento 56.

| Estado (o que o parceiro vê) | Etapas do HubSpot |
|---|---|
| 1 Recebido | Novo Negócio · Lead Novo – Prospecção · Agendamento · Em Contato · Contato Futuro · Follow-Up |
| 2 Em diagnóstico | Em Diagnóstico · Análise de Documentos · Estudo Inicial · Autorização Equipe Senior LR |
| 3 Precisa de algo de você | Análise com Pendência · Documentação Pendente |
| 4 Apresentação marcada | Apresentação de Diagnóstico · Em Apresentação |
| 5 Contrato em andamento | Negociação · Contrato Enviado · Pendência Fechamento · Contrato Assinado |
| 6 Em execução | Negócio Fechado (ganho); com o Bitrix ligado, a fase da execução refina o próximo passo |
| 7 Encerrado | Negócio Perdido · Desqualificado; ganho com execução concluída no Bitrix |

A regra "Em diagnóstico sem e-CAC liberado → Precisa de algo de você" só entra quando o `e_cac_liberado_` for obrigatório na etapa: hoje ele está preenchido em 285 de 5.051 negócios, e a regra mandaria 46 abertos a mais para "Precisa de algo de você" sem motivo real.

### 2.4 Lacunas e de onde viria cada uma
| Lacuna | Para quê | Onde nasce | Dono | Até lá |
|---|---|---|---|---|
| **Recebido** (R$ por negócio e competência) | Extrato real (R5, R8), ROI realizado | `prm.recebimento`, com carga mensal do arquivo do Financeiro (deal_id, competência, tipo, valor, data, NF), idempotente por `chave_fonte`. Inclui compensação de ofício (R8). **Não** criar no HubSpot como número solto: a série precisa de competência | Financeiro (P5, D18); formato: Dados | Extrato mostra só "previsto" e "em conferência" (0 de 1.696 com recebido) |
| **Produto** (D37/D57) | Funil por produto, regra de repasse (10% do líquido Save), vitrine | Propriedade `produto` (lista fechada de `ref.produto`) no negócio, obrigatória na criação; `produto_de_entrada` no objeto Empresa | Dono do CRM, com Dados | `pipeline` como substituto: RT = recuperação; Passivo; Planejamento; Produtos Tributários e Jurídicos sem produto exato |
| **Data de entrada do parceiro** | Tempo até o 1º ganho, onboarding 30/60/90 | `prm.parceiro.data_entrada`, da data de assinatura do termo (`data_entrada_origem = termo`) ou informada pela Daniela | Contratos; Partner Success | 0 de 39: o `datas-entrada-parceiros.json` tem 1 data, de um parceiro fora do roster e sem negócio no escopo |
| **Nível do parceiro** | M6 | `prm.nivel_apuracao` (leitura-sombra) e `prm.parceiro.nivel_atual` | Partner Success (F8, D75) | Simulação do `metricas_ps.py` |
| **Termo e %** com vigência | Fonte única do % (R1, D64), validade do registro | `prm.termo` (temporal): % da recuperação, regra 2027, validade do registro, vigência, caminho do PDF | Contratos (D65) | Carga do `percentual-parceiros.json`: 9 Masters com %, 8 confirmados, 0 com vigência ou arquivo |
| **Master padrinho** do indicador | Hierarquia e remuneração | `prm.parceiro.master_id` | Daniela | Só os consultores do roster têm o vínculo (por heurística) |
| **Vínculo registro ↔ negócio** | Reconciliação determinística (§3.5) | Propriedade nova `id_registro_prm` (texto) no negócio; a Daniela cola o id ao criar o card | Dono do CRM | Reconciliação por raiz + parceiro |
| **Usuário do parceiro** | Login, "quem registrou" | `prm.usuario_parceiro` (Entra B2B) | TI e Daniela | Não existe |
| **Motivo de dormência, certificações** | Partner Success | Fora do escopo v1 (Fase 4) | Partner Success | — |
| **Protocolo e situação do PER** | Pós-venda | Fora do PRM v1; vem do Bitrix ou do Pós-venda | Pós-venda | — |
| **Contato do parceiro e dados bancários** | — | **Não entram no PRM** (regra R24): ficam com o Financeiro | — | — |

---

## 3. Sincronização

### 3.1 Quem roda, quando
| Fase | Executor | Quando | Modo | O que faz |
|---|---|---|---|---|
| Hoje | Rotina **"Dados do dia"**: `bin/partners manha` (7h30) e `tarde` (13h30), dias úteis, no Mac (launchd) ou no GitHub Actions (`.github/workflows/diario.yml`, quando `AGENTES_NUVEM` está ligado) | 2× por dia | **total** (≈ 5 mil negócios, cerca de 2 min) | `hubspot_fonte.py --baixar` → `negocio_ativo construir` → sentinelas → `dados_bi.py` → painel |
| **Fase 1** | A mesma rotina, com um passo novo depois do `dados-bi`: `python3 ~/.claude/skills/depto-dados/scripts/prm_local.py gerar` | 2× por dia | total | Gera `registro/prm/*.json` (§4) a partir do download do dia; o painel lê só as colunas publicáveis |
| **Fase 2** | **Function agendada** (`prm-sync`, timer trigger) na Function App do PRM, com identidade gerenciada; token do HubSpot no Key Vault | incremental a cada 30 min, das 7h às 20h, dias úteis; total às 6h todo dia | incremental + total de reconciliação | Grava em `hs.negocio` pelo `hs.negocio_stage`; refaz `central.vw_indice_negocio_ativo`; roda a reconciliação de registros (§3.5) e os achados de qualidade (§6) |

Durante a transição, a Function e a rotina do Mac rodam em paralelo por 2 semanas. O `ops.sync_execucao` de cada lado é comparado (contagens e hash por deal). Só depois a rotina do Mac deixa de gerar o `registro/prm/`.

### 3.2 Incremental e total
- **Incremental:** busca `POST /crm/v3/objects/deals/search` com `hs_lastmodifieddate >= marca anterior − 15 min` (a sobreposição cobre o relógio e a consistência eventual da busca), ordenada por `hs_lastmodifieddate` crescente, 100 por página, com as mesmas propriedades do `mapeamento-hubspot.json`. Se a janela passar do limite de 10 mil resultados por busca, ela é dividida ao meio até caber (o `_buscar` já faz isso por mês de criação). A marca só avança quando a execução termina com `ok`.
- **Total de reconciliação (6h):** baixa o escopo inteiro como hoje e marca `excluido_no_hs = 1` no que sumiu, sem apagar. A incremental não enxerga exclusões nem mesclas. `hs_merged_object_ids` religa registros e extratos ao id que sobreviveu.
- **Limites da API:** respeitar o limite de requisições por segundo da busca e o teto diário do aplicativo privado; o `call()` atual já faz até 6 tentativas com espera. **[conferir os números vigentes na documentação do HubSpot na implantação]**
- **Histórico de etapas:** quando o `etapa_id` muda entre duas cargas, fecha a linha aberta de `hs.negocio_etapa_hist` e abre outra (`origem = sync_diff`). A carga inicial pode usar o histórico de propriedades do HubSpot (`propertiesWithHistory=dealstage`), com `origem = hs_historico`.

### 3.3 Idempotência
1. **Uma carga por fonte de cada vez:** o índice único filtrado `ux_sync_um_por_vez` impede duas execuções `rodando` da mesma fonte.
2. **Pouso e MERGE:** a Function trunca `hs.negocio_stage`, pousa o lote e roda um `MERGE` por `deal_id`, que só atualiza quando muda o `hash_linha` (SHA-256 das colunas de negócio). Rodar duas vezes a mesma janela dá o mesmo banco; `sem_mudanca` conta o que veio igual.
3. **Transação por lote** (`XACT_ABORT`): ou entra o lote inteiro, ou nada. A marca d'água só avança no fim.
4. **Chaves naturais em tudo o que vem de fora:** `deal_id` (HubSpot), `chave_fonte` (Financeiro), `chave_origem` (demanda: pessoa+conversa, P-NNNN ou uuid do portal), `mensagem_id` (caixa), `chave_idempotencia` (formulário de registro: reenvio não cria registro novo).
5. **Modo local:** `prm_local.py gerar` grava cada arquivo de forma atômica (temporário com permissão 600 e `os.replace`). Rodado duas vezes sobre o mesmo download, gera arquivos idênticos, salvo `gerado_em` (conferido em 26/10). Os arquivos de autoria nunca são sobrescritos.

### 3.4 Por que o espelho é só leitura do HubSpot
- **Token:** aplicativo privado com escopos só de leitura (`crm.objects.deals.read`, `crm.schemas.deals.read`; `crm.objects.companies.read` quando houver `produto_de_entrada`). Não há escopo de escrita, então não existe caminho técnico de volta.
- **Banco:** só a identidade `prm-sync` tem `INSERT/UPDATE` em `hs.*`. A API do portal e o painel têm `SELECT` (com RLS) e `DENY INSERT, UPDATE, DELETE ON SCHEMA::hs`.
- **Correção de dado:** o PRM aponta o problema (achado de qualidade com o link do negócio) e quem corrige é o time de CRM, no HubSpot. A correção chega na carga seguinte. Nunca se corrige o espelho à mão.
- **Registro aprovado:** continua entrando no HubSpot pela Daniela, pelo fluxo atual. O PRM não cria card nem envia o formulário "Novas Oportunidades" (o envio pelos agentes segue bloqueado até o Luis liberar, `lib/oportunidade_form.py`).

### 3.5 Reconciliação: registro do PRM × negócio criado pela Daniela
**Chave:** `cnpj_raiz_hmac` + parceiro (o próprio `parceiro_id` ou o mesmo escritório, `master_id`). Roda em toda carga e no botão "Ligar ao negócio" da fila.

| Passo | Regra | Resultado |
|---|---|---|
| 0 | O negócio traz `id_registro_prm` igual a um registro aprovado | `vinculo_deal = automatico`, registro `convertido` (caminho preferido, quando a propriedade existir) |
| 1 | Candidatos: negócios em `hs.negocio` com a mesma raiz, `criado_em ≥ dia do registro completo − 2 dias`, não ligados a outro registro, em funil que aparece no PRM | — |
| 2 | Exatamente 1 candidato do mesmo parceiro ou do mesmo escritório | `automatico` → `convertido`; evento no ledger |
| 3 | Mais de 1 candidato do mesmo parceiro (matriz e filial, ou dois funis) | `sugerido`: a Daniela escolhe na fila. Sugestão: o funil que casa com o interesse (tese → RT; produto → funil do produto) e o mais antigo |
| 4 | Candidato da mesma raiz com **outro** parceiro ou sem parceiro | abre `prm.conflito` do tipo `registro_x_negocio`, com os fatos (datas, etapas e canais). Ninguém liga sozinho: decide o Luis (R15) |
| 5 | Negócio da mesma raiz criado **antes** do registro e ainda aberto ou ganho | não liga (o registro não retroage, R14). Esse caso deveria ter parado na checagem de entrada; se passou (índice velho), vira conflito com severidade alta |
| 6 | Nenhum candidato até `ISNULL(prorrogado_ate, valido_ate)` | registro `expirado` (evento no ledger; aviso ao parceiro pela caixa) |
| 7 | Negócio ligado e depois mesclado no CRM | `hs_merged_object_ids` troca o `deal_id` do registro e das linhas de extrato |

**Garantias no banco:** um deal liga a no máximo um registro (`ux_registro_deal`); um parceiro tem no máximo um registro vivo por raiz (`ux_registro_vivo_parceiro`); uma raiz tem no máximo um registro aprovado (`ux_registro_aprovado_raiz`). Nunca há duas remunerações integrais.

### 3.6 Outras cargas
| Fonte | Frequência | Chave | Destino |
|---|---|---|---|
| Financeiro (recebimentos) | mensal, no corte; manual até haver integração | `chave_fonte` | `prm.recebimento` → recalcula `extrato_linha.base_recebida` |
| Registro único de demandas | a cada triagem do WhatsApp (Fase 1: arquivo; Fase 2: a API grava direto) | `chave_origem` | `prm.demanda` |
| Central (consultas, esteira, caixa, pedidos) | Fase 2: a API grava direto; migração única dos arquivos atuais, com CNPJ → HMAC e máscara | ids atuais (E-NNNN, P-NNNN, id da caixa) | `central.*` |
| Bitrix (fase da execução) | quando o webhook ligar | `id_bitrix` | refina o estado 6/7 |

---

## 4. Modo local da Fase 1 (`registro/prm/`)

### 4.1 Formato
Pasta `~/agentes-partners/registro/prm/` (fora do git, permissão 700; arquivos 600). **Um arquivo por tabela**, com o nome da tabela e as mesmas colunas do SQL, num envelope:
```json
{"esquema": "prm-local/1", "tabela": "hs.negocio", "gerado_em": "2026-10-26T15:58:00", "fonte": "hubspot-2026-10-26.json",
 "hs_baixado_em": "2026-10-26 13:31", "linhas": [ {"deal_id": "...", "estado_parceiro": "Apresentação marcada", "cnpj_raiz_hmac": "…", "cnpj_mascara": "…", ...} ]}
```
| Arquivo | Tabela | Tipo | Linhas em 26/10 |
|---|---|---|---|
| `hs_negocio.json` | `hs.negocio` | gerado | 5.051 |
| `parceiro_alias.json` | `prm.parceiro_alias` | gerado | aliases do roster, dos consultores e dos nomes livres |
| `prm_extrato_linha.json` | `prm.extrato_linha` | gerado | 1.644 (438 previsto, 1.206 em conferência) |
| `prm_demanda.json` | `prm.demanda` (visão do `registro/demandas.json`) | gerado | 125 |
| `metricas.json` | `prm.vw_metricas` | gerado | 1 |
| `qualidade.json` | `ops.qualidade_execucao` | gerado | 1 |
| `manifesto.json` | `ops.sync_execucao` | gerado | 1 (fonte, data do download, contagens) |
| `prm_parceiro.json` | `prm.parceiro` | **autoria** (o gerador só acrescenta parceiro novo; nunca renumera nem altera) | 39 (9 Masters, 17 consultores por heurística, 13 indicadores), todos com `confirmado = false` |
| `prm_termo.json` | `prm.termo` | autoria (carga inicial do `percentual-parceiros.json`) | 9 |
| `prm_registro_oportunidade.json`, `prm_registro_evento.json`, `prm_conflito.json`, `prm_usuario_parceiro.json` | idem | autoria (nascem vazios) | 0 |

**Diferenças em relação ao SQL, de propósito:** no espelho local não entram o nome da empresa nem o CNPJ completo, só `cnpj_hmac`, `cnpj_raiz_hmac` e `cnpj_mascara`; o painel liga ao negócio pelo link do HubSpot. O CNPJ completo e o contato do decisor só existem em `prm_registro_oportunidade.json` (no Mac, permissão 600), gravados pela Daniela. As tabelas da Central continuam nos arquivos de hoje na Fase 1 (uma fonte só); a migração acontece na Fase 2 (§3.6).

### 4.2 Script gerador
`skills/depto-dados/scripts/prm_local.py` (usa `lib/cnpj.py` e o sal de `central_api.negocio_ativo`, então as chaves batem com o índice da Central):
```
prm_local.py gerar  [--fonte hubspot-AAAA-MM-DD.json] [--saida <pasta>] [--hoje AAAA-MM-DD]
prm_local.py status                         # idade do espelho; sai com 1 se tiver mais de 3 dias
prm_local.py checar-cnpj <cnpj> [--parceiro P-0001]   # validação de entrada do registro (§6.1)
```
`checar-cnpj` devolve um de três resultados: `livre`, `ja_registrado_por_voce` ou `em_analise_area_partners`. Para o terceiro, devolve a mensagem neutra da Central. As contagens que acompanham a resposta são só da visão Save.

### 4.3 O que o painel pode publicar
O `infra/portal_dados.py` lê do `registro/prm/` só: ids, estado, etapa, funil, `cnpj_mascara`, datas, percentuais e valores agregados por parceiro, métricas e qualidade. Nunca publica `cnpj_hmac` (evita que alguém teste chaves), `parceiro_bruto` nem colunas de contato.

### 4.4 Passagem para o Azure
Cada arquivo vira um `INSERT` em lote na tabela de mesmo nome (`OPENJSON(@json, '$.linhas') WITH (...)`). As colunas P2 são cifradas pelo driver com Always Encrypted durante a carga feita pela Function, nunca em T-SQL puro. Os ids (`P-`, `R-`, `C-`, `D-`) são mantidos.

---

## 5. Métricas do PRM

Grão, fonte e versão seguem o glossário do Dados (`governanca-dicionario.md`). A fórmula numérica oficial de resultado continua no `depto-resultados/references/metricas.md`. "Gerador" é o valor do `prm_local.py` em 26/10; "oficial" é o do script dono, quando existe. Quando os dois divergem, vale o oficial, e a divergência está explicada.

| Métrica | Definição | Fórmula | Fonte | Valor em 26/10 |
|---|---|---|---|---|
| **Ativação** | Parceiro com pelo menos 1 negócio com data efetiva nos últimos 90 dias. O Master conta o escritório inteiro (dele e dos consultores) | ativos 90 d ÷ parceiros ativos cadastrados, por tipo (Master, consultor, indicador) | `prm.vw_ativacao`; local: `metricas.json` → `ativacao`; oficial: `metricas_ps.py` | Masters 9 de 9 (100%). Consultores: oficial 9 de 27 ativos; gerador 2 de 13 (só os consultores do roster, por heurística) |
| **Dormentes** | Sem negócio em 90 dias **e** com ganho em 12 meses (inativo = nem um nem outro) | contagem da classe `dormente` por tipo | mesma | Oficial: 10 consultores dormentes e 8 inativos (18 de 27); gerador: 9 dormentes e 2 inativos |
| **Tempo até o 1º ganho** | Dias entre a data de entrada do parceiro (termo ou informada) e o fechamento do 1º ganho | mediana e p75 por coorte trimestral de entrada; publicar só com n ≥ 5 | `prm.parceiro.data_entrada` × `hs.negocio` | PRM: n = 0 (sem data de entrada). Oficial, com o 1º negócio como substituto: mediana de 121,5 dias (n = 4). Só fica mensurável depois da lacuna "data de entrada" |
| **Conversão registrado × não registrado** | Taxa de ganho dos negócios ligados a registro aprovado ou convertido, contra a dos negócios com parceiro e sem registro | ganhos ÷ (ganhos + perdidos), criados em 12 meses, por coorte mensal de criação; intervalo de Wilson de 95%; publicar com n ≥ 20 por grupo | `prm.registro_oportunidade` × `hs.negocio` | Registrado: n = 0. Não registrado: 35,6% (975 de 2.740). A comparação começa no piloto, e mede **associação, não causa** (os parceiros que registram já são os mais organizados) |
| **SLA de demandas** | % resolvidas dentro do prazo do tipo (dias úteis, `ref.feriado`); p50 e p90 até a 1ª resposta e até a solução; % pelo portal; % respondidas pelo histórico | resolvidas no prazo ÷ resolvidas com prazo; percentis das horas | `prm.demanda`, `ref.sla_tipo`, `central.resposta_historico` | 125 demandas (120 WhatsApp, 5 e-mail, 0 portal). Tipo de SLA em só 3, então **o SLA por tipo ainda não é mensurável**. Prazo em texto em 55; no prazo 63,2% (n = 19); solução p50 19,1 h e p90 185,4 h; espera do parceiro p50 7,9 h e p90 23,6 h (contexto §1) |
| **Conflitos** | Raiz com mais de um canal (escritório) em aberto ou ganho; registros em conflito; conflitos novos depois do registro; dias até a decisão | contagem por severidade e por envolvidos | `prm.vw_conflito_raiz`, `prm.conflito`; oficial: `conflito_canal.py` | Oficial: 82 raízes (19 de severidade alta; 3 Master × Master). Gerador: 85 (diferença de grafia dos nomes fora do roster) |
| **Concentração** | Participação do maior Master e dos 5 maiores no valor de crédito ganho em 12 meses, sem café; o que está fora do roster conta como um balde só | top 1 ÷ total; top 5 ÷ total | `hs.negocio`; oficial: `calc_semana.py` (`concentracao_12m`) | Top 5: 90,6% (oficial) e 90,9% (gerador, janela de 365 dias contra 12 meses fechados); top 1: 33,8%. É métrica de guarda: o PRM não pode piorá-la |
| **Extrato pendente** | Linhas de ganho com parceiro ainda sem recebido: `previsto` (calculável e sem bloqueio) e `em_conferencia` (com código C/O/I ou % divergente do termo) | contagem e valor previsto por estado e parceiro; idade média | `prm.extrato_linha`; regra de bloqueio do `conferencia_repasses.py` | 1.644 linhas: 438 previsto e 1.206 em conferência; 0 com recebido. O valor previsto não aparece ao parceiro enquanto não houver recebido (R5) |
| Adoção (guarda) | Usuários com acesso em 30 dias; % dos registros e das demandas pelo portal | — | `seg.acesso_log`, `prm.registro_oportunidade.canal_entrada`, `prm.demanda.canal` | 0 (portal não existe) |

**Regra da casa nas métricas:** sem ranking de pessoas nem leaderboard (R27); o parceiro vê só as próprias métricas; base pequena (n < 5) aparece como "base pequena", sem número.

---

## 6. Qualidade

### 6.1 Validação na entrada do registro
| # | Regra | Dimensão | Se falhar |
|---|---|---|---|
| Q01 | CNPJ normalizado (maiúsculas, sem pontuação), 14 posições, DV válido, aceita alfanumérico (`lib/cnpj.py`) | validade | recusa com motivo de formato (o único motivo que o parceiro vê) |
| Q02 | Raiz = 8 primeiras posições; matriz e filiais são a mesma relação | consistência | — |
| Q03 | Situação cadastral ativa na base da Receita (`dados-publicos/receita/cnpj.sqlite`); baixada, inapta ou nula → registro em análise | exatidão | `em_analise_area_partners` (mensagem neutra) |
| Q04 | Mesmo parceiro, registro vivo na mesma raiz | unicidade | `ja_registrado_por_voce`, com a validade do registro existente (`ux_registro_vivo_parceiro`) |
| Q05 | Outro parceiro com registro vivo, ou negócio aberto ou ganho na raiz (índice HMAC) | unicidade | `em_analise_area_partners` + aviso interno; abre conflito só se o parceiro insistir com evidência |
| Q06 | Teto diário de checagens por usuário e alerta de acertos acima do limite (`CENTRAL_LIMITE_ATIVO`) | segurança (varredura da carteira, R25) | resposta neutra + alerta ao Luis |
| Q07 | Campos mínimos: contato do decisor (nome e mais um canal), interesse (tese, produto ou "não sei"), como conhece a empresa | completude | não grava |
| Q08 | Todo texto livre passa por `lib/protecao.limpo`; CPF, RG, CNH, conta ou PIX → recusa | LGPD (P3) | não grava |
| Q09 | Produto em validação só como "descoberta" (`ref.produto.situacao`); sem simulação | regra R19 | grava com marca "descoberta" |
| Q10 | Parceiro ativo e com termo vigente para **aprovar** (para receber, não precisa) | consistência | fica `recebido` até o termo |
| Q11 | Reenvio com a mesma `chave_idempotencia` | unicidade | devolve o registro existente |
| Q12 | Índice da Central com mais de 3 dias ou ausente | atualidade | falha fechada: `em_analise_area_partners` (igual à consulta da Central) |

### 6.2 Regras sobre o espelho (achados em `ops.qualidade_achado`, com o link do negócio para o CRM)
Q13 deal aberto ou ganho sem CNPJ válido (fica fora do registro e do conflito) · Q14 % do parceiro do card diferente do termo · Q15 % do parceiro acima de 100% ou exatamente 1 · Q16 ganho sem % de honorário · Q17 ganho sem tese (D73) · Q18 `nome_do_parceiro` que não casa com nenhum alias · Q19 ganhos duplicados (regras R1–R5 do `saneamento_duplicados.py`) · Q20 negócio ligado a registro e mesclado no CRM.

### 6.3 Saneamento antes do go-live (volumes de 26/10)
| # | Problema | Volume | Por que trava | Dono | Critério para o piloto |
|---|---|---|---|---|---|
| S1 | **Ganhos duplicados** (D87, `saneamento_duplicados.py`) | 349 grupos; **357 cards a sair** (352 de alta confiança); R$ 834 mi de crédito em duplicidade; **21 grupos acima de R$ 10 mi** vão ao Luis | Extrato em dobro e conflito falso | Time de CRM (lista pronta, nada alterado pelos agentes) | 0 grupos de alta confiança nos ganhos dos Masters do piloto |
| S2 | Mesmo CNPJ e mesmo valor em mais de um ganho (I05) | 81 grupos (162 negócios), dentro do S1 | idem | CRM e Financeiro | idem |
| S3 | Abertos duplicados | 3 grupos (6 negócios) na mesma raiz e no mesmo funil; 15 CNPJs (34 negócios) no critério do `dados_bi.py` | Registro e conflito falsos | CRM | 0 no piloto |
| S4 | CNPJ vazio ou inválido | 66 vazios, 47 inválidos (de 5.051) | Sem raiz, não há registro nem checagem | CRM, com o cadastro da Receita ao lado (sentinela `crm_incompleto`) | 0 em aberto e ganho |
| S5 | **Sem % de honorário** nos ganhos | 966 de 1.696 (57,0%) | Extrato "em conferência" | CRM e Contratos | 100% dos ganhos de 24 meses dos Masters do piloto |
| S6 | Sem % do parceiro com parceiro identificado; % acima de 100% | 451; 7 | idem | CRM; o termo resolve a maioria (R1) | termo vigente substitui o card |
| S7 | **Sem recebido** | 1.696 de 1.696 | Extrato real impossível (R5) | Financeiro (P5, D18) | carga do `prm.recebimento` dos Masters do piloto, últimos 24 meses |
| S8 | Termos sem vigência e sem arquivo | 9 com % (8 confirmados), 0 com vigência | Validade do registro e % oficial | Contratos (D65) | termo dos Masters do piloto |
| S9 | Parceiro sem cadastro confirmado | 39 carregados, 0 confirmados; 70 grafias no `nome_do_parceiro`; 465 negócios sem nome; consultores: 17 no roster contra 27 no Partner Success | "Meus negócios" do consultor errado | Daniela (confirma tipo, vínculo e aliases) | 100% dos consultores dos Masters do piloto confirmados |
| S10 | Sem data de entrada | 39 de 39 | Tempo até o 1º ganho | Contratos e Partner Success | data do termo dos Masters do piloto |
| S11 | Conflitos herdados | 82 raízes; 19 de severidade alta; 3 Master × Master | Registro nasce com fila herdada | Luis (D98) | as 19 de severidade alta decididas |
| S12 | Ganho sem tese | 908 | Biblioteca, nível e funil por tese | CRM (D73) | não trava o piloto |
| S13 | Data de criação regravada por importação | 1.230 ganhos importados | Coorte e tempo de ciclo | — | usar `data_efetiva` (já no esquema) |

---

## 7. Entrega em 3 blocos

**1. O que você pediu**
- Esquema T-SQL completo em `docs/prm/v2/schema.sql`: 41 tabelas em 6 esquemas, com chaves, índices (inclusive os únicos filtrados que garantem um registro aprovado por raiz), RLS por parceiro e escritório, Always Encrypted no dado de cliente, máscara no dado do parceiro, ledger no registro e no extrato, retenção com procedimento de expurgo e views de métricas. Inclui as tabelas da Central (consulta de regime, esteira e dossiê, respostas pelo histórico, chamados propostos, caixa, pedidos aos agentes).
- Mapeamento campo a campo com transformação e preenchimento atual, mapa de etapas para os 7 estados e lacunas com origem e dono.
- Sincronização em três tempos (hoje, Fase 1, Fase 2), idempotência, garantia de só leitura e algoritmo de reconciliação do registro com o negócio por raiz HMAC + parceiro.
- Modo local pronto: `prm_local.py`, testado sobre o download de 26/10 (5.051 negócios; idempotente; checagem de CNPJ).
- 8 métricas com definição, fórmula, fonte e valor de hoje; 20 regras de qualidade; 13 itens de saneamento com volume e dono.

**2. O que você também precisa**
- A propriedade `id_registro_prm` no negócio (a Daniela cola o id ao criar o card) deixa a reconciliação determinística e custa um campo de texto. Recomendo pedir junto com a propriedade Produto (D37).
- Acrescentar `hs_merged_object_ids` ao download agora: o saneamento S1 vai mesclar cerca de 357 cards, e sem esse campo registros e extratos ficariam ligados a ids que deixaram de existir.
- O SLA por tipo não é mensurável hoje (3 de 125 demandas com tipo). A triagem do WhatsApp precisa gravar o `tipo` do `sla.json` em toda demanda nova; sem isso, a métrica de SLA do PRM nasce vazia.
- A contagem de consultores diverge entre o roster (17) e o Partner Success (27). No PRM, consultor é cadastro confirmado pela Daniela, e isso resolve a divergência na fonte.
- O passo `prm` na rotina "Dados do dia" (`bin/partners`, depois do `dados-bi`) e a cópia do `prm_local.py` para `~/.claude/skills/depto-dados/scripts/` ficam para a sessão que fizer o merge. Esta sessão só escreveu no worktree.
- O esquema não foi executado num Azure SQL (não há instância). Ele deve ser aplicado primeiro num banco de teste, criando antes a CMK e a CEK.

**3. O que falta e quem fornece**
| Falta | Quem |
|---|---|
| Arquivo mensal de recebimentos por negócio (formato do `prm.recebimento`) | Financeiro (P5, D18) |
| Termos dos Masters com %, vigência, validade do registro e PDF | Contratos (D65) |
| Propriedades `produto`, `produto_de_entrada` e `id_registro_prm`; token de leitura com escopo mínimo | Dono do CRM |
| Confirmação de parceiros, consultores e aliases; data de entrada | Daniela; Partner Success |
| Key Vault, CMK/CEK, Function App, identidade gerenciada, Azure SQL de teste | TI da Save |
| Prazos de retenção, base legal da guarda de CNPJ e contato no Azure, empresário individual (razão social = nome civil) | Jurídico |
| Mapa etapa → estado (§2.3) e validade do registro (R14) | Luis (fase 0) |
| Decisão dos 21 grupos duplicados acima de R$ 10 mi e das 19 raízes de severidade alta | Luis |

---

## 8. Registro da revisão
```json
{"revisao": {"gerente": "Gerente de Dados & BI",
  "especialistas": ["Engenheiro de Dados do HubSpot (mapeamento, sincronização, prm_local.py)",
                    "Guardião de Qualidade e Saneamento (seção 6, volumes do saneamento_duplicados.py)",
                    "Arquiteto de Governança e Dicionário (esquema, classes de dado, retenção, glossário)",
                    "Analista de BI e Saúde do Parceiro (métricas e colunas publicáveis no painel)",
                    "Estatístico (regras de base pequena, Wilson, associação × causa na conversão)"],
  "rodadas": 2, "areas_consultadas": [], "aprovado": true,
  "ajustes": ["concentração e conflito recalculados no grão do escritório para bater com calc_semana.py e conflito_canal.py (85 × 82; 90,9% × 90,6%)",
              "regra do e-CAC retirada do mapa de estados: o campo está preenchido em 285 de 5.051 negócios",
              "tempo até o 1º ganho só com data de entrada (sem substituto), para não medir a base no lugar do onboarding",
              "nome da empresa e CNPJ completo fora do espelho local; hmac não publicado no painel"],
  "fontes": ["hubspot-2026-10-26.json (13h31)", "dados-bi-2026-10-26.json", "conflito-canal-2026-10-26.json", "conferencia-repasses-2026-10-26.json",
             "metricas-ps-2026-10-26.json", "metricas-2026-10-26.json", "saneamento_duplicados.py (rodado em 26/10)", "registro/demandas.json"],
  "pendente_de_outras_areas": ["Jurídico: retenção e base legal", "TI: chaves e infraestrutura", "Operações de Canal: regra de bloqueio do extrato unificada com conferencia_repasses.py"]}}
```
