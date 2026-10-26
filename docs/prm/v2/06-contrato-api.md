# PRM Save v2 · 06 · Contrato da API

**Versão:** 1.1 (acompanhamento de negócios e dashboards, 26/10/2026) · **Data:** 26/10/2026 · **Código:** `central/api/central_api/prm/rotas.py` (tabela `P`) · **Testes:** `central/api/tests/test_prm_*.py`
**Transporte:** o mesmo código atende o servidor local (`central/dev_server.py --prm`) e a Azure (`central/api/function_app.py`, rota `prm/{*resto}`). Nenhuma rota do PRM existe fora do token (lacuna L1).

---

## 1. Convenções

| Tema | Regra |
|---|---|
| Base | `/api/prm/` · JSON UTF-8 · `Cache-Control: no-store` |
| POST | `Content-Type: application/json` obrigatório (415 sem ele: página de outro site não posta sem preflight); corpo ≤ 20 KB (413) |
| Autenticação | `Authorization: Bearer <token Entra>`. Face do parceiro: registro `SAVE-PRM-PARCEIROS`, escopo `Prm.Acesso` (`PRM_API_CLIENT_ID`/`PRM_SCOPE`); sem ele, o registro da Central com o papel `Parceiro.Portal`. Face da Save: `SAVE-SSO-MASTERS`, escopo `Central.Acesso`, papéis `Partners.*`. Rotinas: client credentials com `Agentes.Processar` |
| Login simulado | Só servidor de teste: cabeçalho `X-PRM-Dev-Usuario: <U-0001 \| daniela \| luis \| financeiro>`, aceito com `PRM_LOGIN_SIMULADO=1` + Host de teste + ausência de `WEBSITE_INSTANCE_ID`. Host de teste = `localhost/127.0.0.1/[::1]` ou, só com `CODESPACES=true`, exatamente `<CODESPACE_NAME>-<porta>.<GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN>` (porta = `PRM_PORTA`, padrão 4280; com ou sem `:443`); host de outro codespace é recusado. `function_app.py` apaga a variável na partida |
| Papéis | Parceiro: `titular`, `consultor` (da tabela `usuario_parceiro`, pelo `oid`). Save: `luis` (Partners.Gestor), `daniela` (Partners.Masters), `jenifer` (Partners.BDR), `geovana` (Partners.Tecnica), `financeiro` (Partners.Financeiro, **novo**), `contratos` (Partners.Contratos, **novo**), `leitura` (Partners.Leitura). Matriz: `identidade.ACOES` = 02 §2.2 |
| Escopo da linha | Titular vê o escritório; consultor só o que é dele (`usuario_id` e, nos negócios, `consultor_parceiro_id`). Fora do escopo: **404** (PRM-R02), nunca 403, e linha `negado` na trilha |
| Ids na URL | Opacos de 16 hex (`ref`), não sequenciais. O id legível (`R-2026-000001`, `D-2026-0001`) aparece no corpo |
| Termos de uso | Parceiro sem aceite da versão vigente recebe **428** `{codigo: "termos"}` em toda rota marcada (PRM-R107) |
| Erros | `{erro, campos?, codigo?}`. 400/415/413 corpo · 401 `codigo: sessao` · 403 papel/face (`codigo: sem_acesso` quando o usuário não está ativo) · 404 · 405 · 409 regra (`codigo`: `cedo`, `exige_conflito`, `cliente_save`, `estado_final`, `transicao_invalida`, `M-00`) · 422 validação (`campos`) e `codigo: M-90` (dado pessoal) ou `auditor` (promessa) · 428 termos · 500 texto neutro, sem rastro |
| Trilha | Toda leitura de dado do parceiro e toda gravação: `seg_acesso_log` (usuário, tela, ação, alvo opaco, HMAC do IP, resultado). Toda decisão: `prm_decisao` (ledger) |
| Tempo | Carimbos em UTC com milissegundos; textos ao parceiro em `dd/mm/aaaa hh:mm` de Brasília |

## 2. Comum

| Método e caminho | Quem | Resposta |
|---|---|---|
| `GET /api/prm/eu` | todos | `{tipo, papel, nome, usuario_id, parceiro_id, face, pode[], escritorio?, termos_pendentes?, versao_termos?, primeira_declaracao?, avisos_nao_lidos}` |
| `GET /api/prm/dev/usuarios` | só servidor local | `{usuarios[], cnpjs_de_teste[]}`; 404 fora de localhost ou sem login simulado |

## 3. Face do parceiro (`/api/prm/parceiro/…`)

| Método e caminho | Corpo / consulta | Resposta | Regras |
|---|---|---|---|
| `POST termos/aceitar` | `{versao, aceito: true}` | `{ok}` | grava `seg_aceite_termo_uso` |
| `GET inicio` | — | `{nome, pede_voce[≤3], pede_voce_total, kpis{pedem_voce, em_andamento, registros_validos, respostas_novas, empresas}, mudou[], a_vencer[], nivel, primeiros_passos?, avisos_nao_lidos, nf_pendentes, precisa_empresas}` | P-1 |
| `POST primeiros-passos/dispensar` | `{}` | `{ok}` | — |
| `GET empresas` | `?consultor=U-…` (titular) | `{itens[{ref, tipo, nome, cnpj_mascara, chip, rotulo, proximo_passo, com, desde, aba}], abas{precisa_de_voce, andamento, registros, encerradas}, equipe[]}` | registros + negócios do escopo |
| `GET empresas/{ref}` | — | `{ref, nome, cnpj_mascara, registro?, negocio?{estado, rotulo, chip, proximo_passo, com, desde, passos[], pendencias[]}, pedidos[], extrato[] (titular), dossie?, pode_pedir_dossie}` | 404 fora do escopo; nunca valor, honorário, tese, parecer ou prazo de PER (PRM-R44) |
| `POST empresas/{ref}/dossie` | `{}` | visão da esteira `{id, status, andamento, nivel, resultado?}` | dossiê-base na hora; aprovação obrigatória; empresa já cliente da Save → 409 `M-00` |
| `GET empresas/{ref}/dossie/arquivo` | — | `.docx` (anexo) ou 503 | só o dono do registro |
| `POST empresa/checar` | `{cnpj}` | `{estado: incompleto \| erro_formato \| ja_e_seu \| ok_formato, mensagem?}` | tempo real: só formato, dígito e "já é seu"; **nunca olha a carteira** |
| `POST empresa/consultar` | `{cnpj}` ou `{cnpjs[≤20]}` | `{resultados[{faixa, titulo, detalhe, ano_base, fonte, empresa{razao, porte, uf, situacao}, cnae, cnpj_mascara, neutra, situacao_ativa, pode_registrar} \| {cnpj_mascara, ja_e_seu}]}` | regra única de proteção (L14); teto persistente `consulta.teto_diario_usuario`; mesma resposta neutra (`M-00`) para cliente da Save, outro canal, índice ausente e teto; piso de tempo |
| `POST registros` | `{cnpj, razao_social, contato_nome, contato_cargo, contato_email \| contato_tel, interesse, como_conhece, evidencia_tipo, evidencia_data?, evidencia_nota?, declaracao_lgpd, declaracao_sem_promessa (1ª vez), chave_idempotencia?}` | **201** `{resultado: "recebido", titulo, mensagem (M-01), registro{ref, registro_id, carimbo}}` · **200** `{resultado: "ja_e_seu", titulo, mensagem (M-03a/b/c), registro? \| negocio?}` · 422 `campos` / `M-90` | PRM-R21: o 201 é idêntico para livre, outro canal, cliente da Save, índice ausente e teto; piso `registro.piso_resposta_ms`; reenvio com a mesma chave devolve o mesmo registro |
| `POST registros/{ref}/cancelar` | `{}` | visão do registro | só `aprovado`, `convertido`, `prorrogado` |
| `POST registros/{ref}/prorrogacao` | `{fato}` | `{mensagem}` | 30 dias antes do vencimento, uma vez |
| `POST registros/{ref}/complemento` | `{resposta}` | visão do registro | dentro de `registro.complemento_mantem_carimbo_du` |
| `GET tipos-pedido` | — | `{tipos[{tipo, rotulo, urgente}], aviso_anexo (M-34)}` | catálogo único (U2) |
| `GET pedidos` | — | `{itens[visão]}` | — |
| `POST pedidos` | `{tipo, texto, empresa_ref?, apoio_juridico?}` | **201** `{ref, id (D-AAAA-NNNN), tipo, estado, rotulo, chip, prazo, mensagens[], …}` | M-30; histórico antes do chamado; `M-90` bloqueia |
| `GET pedidos/{ref}` | — | visão | 404 fora do escopo |
| `POST pedidos/{ref}/concluir` · `reabrir` · `complemento` | `{}` · `{texto?}` · `{texto}` | visão | reabrir até `demanda.reabertura_dias` |
| `GET extrato` | — | `{resumo{pago_no_ano, liberado_aguardando_nf, em_conferencia_linhas}, linhas[{ref, estado, rotulo, chip, mensagem, competencia, empresa, passos[], pode_contestar, contestacao_ate, valor?, detalhe?}], aviso_fonte}` | só titular (consultor 403, PRM-R15); valor só a partir de "Recebido pela Save" (DL-09) |
| `POST extrato/{ref}/contestar` | `{motivo}` | `{fora_da_janela: false, contestacao_id, mensagem (M-21)}` ou `{fora_da_janela: true, demanda}` | PRM-R65, R67 |
| `GET avisos` · `POST avisos/lidos` | — · `{ids?}` | `{itens[{id, titulo, texto, tipo, quando, lido, go}]}` · `{marcados}` | só os próprios |
| `GET nivel` | — | `{modo, selo: "Em teste", aviso, jornada[], etapa, equipe? (titular)}` | sem faixa, barra ou R$ (PRM-R81) |
| `GET biblioteca` | — | `{prontos[], descoberta[], aviso_cobranded}` | produtos em validação só "em descoberta" (R11) |
| `GET negocios` | `?situacao=andamento\|ganhos\|perdidos\|todos` (padrão andamento) `&estado=a,b&etapa=&produto=&tese=&de=AAAA-MM-DD&ate=&consultor=U-…(titular)&q=&parado=1&registrado=1\|0&mes_previsao=AAAA-MM&ordem=recente\|antigo\|valor\|parado\|nome\|previsao&pagina=&por_pagina≤200` | `{itens[{ref, nome, cnpj_mascara, estado, rotulo, chip, com, situacao, produto, teses[], dias_na_etapa, parado, criado_em, ultima_movimentacao_em, registrado, etapa_crm?, valor_credito?, previsao_fechamento_em?, fechado_em?, consultor?, remuneracao_prevista? (titular)}], total, pagina, por_pagina, paginas, colunas[{estado, rotulo, n, valor?}], valor_total?, filtros{estados, produtos, teses, etapas, situacoes, ordens, consultores? (titular)}, ressalvas{campo: texto}, parado_dias}` | escopo `ve_negocio` (titular: escritório; consultor: os dele); campos pela matriz `negocio.visibilidade_campos` (PRM-R113/R114); 422 situação inválida |
| `GET negocios/{ref}` | — | `{ref, nome, cnpj_mascara, estado, rotulo, chip, com, desde, proximo_passo, passos[], situacao, dias_na_etapa, secoes[{titulo, campos[{campo, rotulo, valor, tipo: texto\|reais\|pct\|data\|lista, ressalva}]}], ressalvas, linha_do_tempo?[{etapa, estado, desde, dias, atual}], pendencias?[], documentos?[{item, situacao}], registro?{registro_id, rotulo, chip, carimbo, valido_ate, ref}, pedidos?[], extrato? (titular)}` | 404 fora do escopo, com trilha `negado`; próximo passo do CRM auditado (PRM-R115); nunca campo travado |
| `GET painel` | `?periodo=30\|90\|180\|365` (dias) ou `?de=&ate=`; `&consultor=U-…` (titular) | `{periodo{de, ate, dias, anterior_de, anterior_ate}, pipeline[{estado, rotulo, n, valor?, sem_valor}], funil{coorte, etapas[{etapa, rotulo, n, pct_do_inicio, pct_da_anterior}]}, periodo_atual{ganhos, perdidos, novos, conversao{ganhos, perdidos, n, pct, base_pequena}, ciclo{n, media_dias, mediana_dias}}, periodo_anterior, comparacao{…{atual, anterior, delta}}, aging{limite_dias, faixas[], por_estado[{estado, n, media_dias, parados, faixas[]}], total_parados, parados[itens]}, atividade{registros_no_mes, registros_no_periodo, demandas_abertas, negocios_abertos}, remuneracao?{prevista, recebida_pela_save, paga, ganhos_sem_calculo, percentual_termo, ressalva} (titular), consultores[] (titular), ressalvas}` | só o próprio escopo; nunca ranking (R27, PRM-R116); 422 período invertido |

## 4. Face da Save (`/api/prm/save/…`)

| Método e caminho | Quem | Resposta |
|---|---|---|
| `GET canal` | daniela, jenifer, geovana, financeiro, luis, leitura | `{kpis[8], saude[], alertas[], concentracao{top1_pct, top5_pct}, fonte}` |
| `GET registros` | ver_registros | `{itens[visão Save: checagem, flags, histórico da raiz, pode_decidir_agora, valido_se_aprovar…], motivos[], parceiros[]}` |
| `GET registros/{R-…}` | ver_registros | visão Save |
| `POST registros` | daniela, jenifer | o mesmo corpo do parceiro + `em_nome_de{parceiro_id, usuario_id?}` + `carimbo_whatsapp?` (Fase 1) |
| `GET conflitos` | ver_registros | `{itens[{…, partes_nomes, registros_det, fatos, regra, prazo, pode_decidir}]}` |
| `GET demandas` · `POST demandas` | responder_demanda · abrir_demanda | `{itens[visão Save com sla, historico, chamado], registro_unico[]}` · abrir em nome do parceiro |
| `GET extratos` | ver_extrato | `{lotes[{lote, checklist[], pode_liberar, motivo_bloqueio}], linhas[], aguardando_nf[], contestacoes[], pode_agir}` |
| `GET dossies` | ver_registros | `{itens[{id, registro_id, status, auditoria, secoes, pode_aprovar}]}` |
| `GET acessos` | daniela, luis | `{usuarios[], trilha[40], teto_neutras}` |
| `GET niveis` | ver_canal | `{modo, itens[{faixa_simulada, volume_12m, pct_do_proximo, trimestre}]}` (sombra) |
| `GET parametros` | ver_canal | `{itens[{chave, valor, padrao, unidade, marca, quem_muda}]}` |
| `GET dashboard?periodo=&de=&ate=&master=P-…` | ver_canal_agregado (daniela, jenifer, geovana, financeiro, luis, leitura) | `{periodo, master, masters[], kpis{pipeline_n, pipeline_valor, ganhos_n, ganhos_valor, conversao, ciclo, parados, dormentes, novos_n}, comparacao, pipeline[+drill], funil, aging{…, por_estado[+drill], parados[]}, por_master[{master_id, nome, abertos, valor_aberto, ganhos_n, ganhos_valor, conversao, ciclo_medio_dias, parados, drill}], por_consultor[], forecast{meses[{mes, rotulo, meta, realizado, em_contrato, demais_abertos, n_*, pct_meta_realizado, drill, drill_previsao}], fonte_meta, nota}, concentracao{total_12m, top1_pct, top5_pct, top5[]}, dormentes[], conversao_registro{registrado, nao_registrado, nota}, por_produto[+drill], por_tese[+drill], fonte}` · sem café e sem negócio fora do roster (PRM-R117); meta D111 de `registro/gestao/gestao.json` (ou `PRM_GESTAO`), senão `canal.meta_mensal`; com filtro de Master a meta do canal sai `null`; cada bloco traz `drill` = consulta pronta para `GET save/negocios` |
| `GET negocios` | ver_negocios (daniela, jenifer, geovana, luis) | mesma consulta do parceiro + `master=P-…` e `cafe=1`; itens com `deal_id, master, master_id, consultor, cafe` |
| `GET negocios/{deal_id}` | ver_negocios | ficha completa + seção "Interno da Save" (probabilidade, notas internas, motivo interno da perda, id Bitrix; comissões internas só luis e financeiro, R111) |
| `GET avisos` · `POST avisos/lidos` | todos da Save | caixa do papel + `time` |
| `GET trilha?objeto=&id=` | daniela, luis | `{itens[decisões]}` |
| `POST rotina` | luis, `Agentes.Processar` | `{registros{…}, negocios{…}, demandas{…}}` (expiração, prorrogação automática, M-14, M-04, reconciliação, M-16, escala 1/3/5 d.u.) |
| `POST decidir` | conforme a decisão | `{ok, resultado (aprovado \| nao_aprovado \| nova_analise \| recusado), trilha (DEC-…), objeto}` |

### 4.1 `POST /api/prm/save/decidir` (U4)
| objeto | decisao | campos | ação exigida |
|---|---|---|---|
| registro | `aprovar` | `mesmo_parceiro_cadastro_incompleto?` | decidir_registro (daniela); 409 `cedo` antes de 4 h úteis; 409 `exige_conflito` para outro canal |
| registro | `nao_aprovar` | `motivo` 1–4, `campos?` | decidir_registro; outro canal e cliente da Save → sempre motivo 4 |
| registro | `enviar_conflito` | `motivo_interno?` | enviar_conflito (daniela, jenifer) |
| registro | `pedir_complemento` | `pergunta` (auditada) | decidir_registro |
| registro | `prorrogar` · `negar_prorrogacao` | — | decidir_prorrogacao |
| conflito | `decidir` | `vencedor`, `tipo_decisao` (`primeiro_registro`, `divisao_excecao`, `save_direto`, `sem_conflito`) | decidir_conflito (só luis) |
| demanda | `aprovar_envio` | `texto` (auditado; vazio = rascunho do histórico), `editada?` | responder_demanda |
| demanda | `encaminhar` · `recusar_chamado` · `pedir_dados` | `titulo?`, `descricao?` · `motivo` · `itens` | aprovar_chamado · aprovar_chamado · responder_demanda |
| extrato_linha | `registrar_recebimento` · `registrar_pagamento` | `valor`, `competencia` · `nf` | financeiro |
| extrato | `calcular` | `competencia?` | financeiro |
| extrato_lote | `liberar` | id = `P-0001\|AAAA-MM` | financeiro; 403 segregação (PRM-R18) |
| contestacao | `procedente` · `improcedente` | `causa_raiz`, `explicacao` (auditada) | financeiro, contratos, luis |
| dossie | `aprovar` | id = `E-NNNN` | daniela, luis (grava quem no pedido da esteira) |
| usuario | `suspender` · `reativar` · `desativar` | `motivo_interno?` | daniela, luis |
| pendencia | `abrir` · `resolver` | id = deal (abrir) ou `PD-…`; `tipo`, `texto` | daniela, jenifer, geovana |
| parametro | `alterar` | id = chave, `valor` | a dona da chave (`quem_muda`) ou luis |

## 5. Rotas antigas da esteira, agora com identidade (L1)
`POST /api/regime {cnpjs}` · `POST /api/esteira {cnpj}` · `GET /api/esteira?id=E-NNNN` · `GET /api/esteira/historico` · `GET /api/esteira/arquivo?id=E-NNNN` — mesmas respostas do `consulta_demo.py`, com o usuário do token (`usuario_id` do parceiro ou papel da Save), teto persistente e trilha com HMAC. O `consulta_demo.py` continua como ferramenta de teste sem login (só localhost).
