# PRM Save · desenho do produto

**Versão:** 1.0 · **Data:** 26/10/2026 · **Autor:** arquiteto de produto da Área Partners (agente), para o Luis · **Status:** desenho para decisão
**Base:** `docs/prm/engenharia-reversa-prm-2026-10-26.md` (mercado) e `docs/prm/contexto-interno-prm-2026-10-26.md` (parceiros, regras R1–R31, dados). Números do HubSpot de 26/10/2026, salvo indicação. Masters aparecem como A a I.
**Definido na conversa:** construir, não comprar. Fase 1 dentro do painel Central Partners, lendo o HubSpot, sem TI. Fase 2 com portal do parceiro na Azure do tenant Save (Static Web Apps Standard, Function App, Azure SQL serverless em Brazil South, login B2B no Entra da Save). O HubSpot é sempre só leitura. O registro de oportunidade mora no banco do PRM.
**Protótipo navegável:** `prm-save-prototipo.html` (dados fictícios, perfis "Parceiro" e "Save").

---

## 1. Visão e os 3 resultados

**Visão:** o parceiro registra, acompanha e entende a própria remuneração sozinho, num só lugar, e a Save enxerga o canal inteiro sem depender do WhatsApp nem da memória de uma pessoa.

| # | Resultado que o PRM tem que mover | Métrica atual | De onde vem | Como o PRM mexe |
|---|---|---|---|---|
| 1 | **Mais parceiros indicando de novo** (capacidade parada dentro dos Masters) | 18 de 27 consultores dormentes ou inativos; 16 consultores com 1 só ganho; tempo até o 1º ganho com mediana de 121,5 dias (n = 4) | `registro/gestao/pacote-2026-10-26.json` (`consultores_dormentes`, `consultores_sem_2o_ganho`); `metricas-ps-2026-10-26.json` | Registro em 2 minutos pelo celular, status visível, nível com barra de progresso, kit por tese. Medida: consultores ativos em 90 dias e % com 2º ganho |
| 2 | **Menos espera e menos despacho pelo time** | 96% das demandas chegam pelo WhatsApp (120 de 125); espera do parceiro com mediana de 7,9 h e p90 de 23,6 h; 67% dos chamados GLPI abertos pela Daniela e pela Geovana | `registro/demandas.json`; `celulas/whatsapp-triagem-*.json`; `infra/glpi-regras.md` | "Meus negócios" responde o status sem pergunta; a demanda entra estruturada e passa pelo histórico (`lib/historico.py`) antes de virar chamado. Medida: % de demandas pelo portal, % respondidas pelo histórico, p90 de espera |
| 3 | **Confiança na remuneração e no registro** | 0 de 1.696 ganhos com recebido registrado; 1.047 ganhos com repasse bloqueado; 82 raízes de CNPJ com mais de um canal (19 de severidade alta, 3 Master × Master) | `departamentos/operacoes-canal/conferencia-repasses-2026-10-26.json`; `conflito-canal-2026-10-26.json` | Extrato com estados e motivo visível; registro com carimbo de hora por raiz de CNPJ, checado na entrada. Medida: % de ganhos com linha de extrato visível, contestações por lote, conflitos novos depois do registro |

**Métrica de guarda (não é meta do PRM, mas ele não pode piorar):** concentração dos 5 maiores Masters em 90,6% do fechado 12 m; win rate de 3 meses em 26,0% (pacote de 26/10).

---

## 2. Módulos (8)

Legenda de lacuna: **[TI]** depende da TI da Save · **[CRM]** do dono do CRM · **[Fin]** do Financeiro · **[Jur]** do Jurídico · **[Luis]** de decisão do Luis.

### M1. Início do parceiro
| | |
|---|---|
| Parceiro vê | Resumo da semana: registros e validade, negócios que pedem algo dele (documento, e-CAC, reunião), últimas respostas às demandas, linha do extrato que mudou de estado, posição no nível, um kit sugerido pela tese mais comum na carteira dele |
| Save vê | O mesmo resumo por parceiro, na ficha 360 do painel (pipeline, pendências, saúde) |
| Regra codificada | Só dados do próprio parceiro (R12); sem ranking (R27); textos sem promessa de valor, prazo ou êxito (R21, CLAUDE.md §3) |
| Dado que alimenta | `briefing_master.py --master X` (pipeline e pendências), `pendencias.py`, `metricas_ps.py` |
| Lacuna | Usuário do parceiro (pessoa do escritório) não existe no HubSpot; nasce no PRM **[TI]** |
| Inspiração | Impartner (página inicial com pipeline e progresso). **Copiamos:** um só lugar com "o que pede ação". **Adaptamos:** a ação é do parceiro (documento, acesso), não de cotação |

### M2. Registro de oportunidade
| | |
|---|---|
| Parceiro vê | Formulário curto (CNPJ, contato do decisor, tese ou produto de interesse, como conhece a empresa, evidência opcional). Resposta da checagem por raiz de CNPJ em um de três estados: **livre** (registro recebido, em análise), **já registrado por você** (mostra o registro e a validade) ou **em análise pela Área Partners** (mensagem neutra única). Lista dos registros com validade, prorrogação e expiração |
| Save vê | Fila de registros com carimbo de hora, resultado da checagem, histórico da raiz (1º registro, canais, ganhos, teses) e as ações Aprovar, Recusar com motivo e Enviar a conflito. Conflito vai ao Luis com os fatos; o agente não atribui cliente |
| Regra codificada | Unidade = raiz do CNPJ; vale data e hora do registro completo; validade **90 dias + 60** de prorrogação com avanço (proposta R14; 120 dias para Master em decisão; 180 dias no material jurídico em conflito) **[Luis]**; ganho protegido enquanto houver contrato + 12 meses; nunca duas remunerações integrais; não retroage (R14). Proteção temporária, nunca território exclusivo (R16). Conflito é do Luis (R15, D98). A resposta ao parceiro não revela se a empresa é cliente da Save (R25, mensagem neutra do `central/`). Lead da BDR reservado 45 dias ao Master com aceite em 3 d.u. (R17). Clientes sem Master ficam fora (R18) |
| Dado que alimenta | `crm_checagem.py --cnpj` (duplicidade, conflito, Receita, Simples), `conflito_canal.py`, índice HMAC de `central/api/central_api/negocio_ativo.py`, `lib/cnpj.py` (CNPJ alfanumérico, IN RFB 2.229/2024) |
| Lacuna | Regra R1–R3 não aprovada **[Luis]**; o registro aprovado entra no HubSpot pela Daniela (fluxo atual), porque o PRM não escreve no CRM **[CRM]** |
| Inspiração | Channeltivity (etapas abertas e fechadas, etapa padrão de entrada, expiração automática, destino do vencido); Salesforce (carimbo de hora, checagem de duplicidade); PartnerPortal.io (trava com aprovação). **Adaptamos:** a chave é a raiz do CNPJ, não o nome da conta; a resposta de conflito é neutra para não expor a carteira |

### M3. Meus negócios
| | |
|---|---|
| Parceiro vê | Cada negócio indicado em **7 estados em linguagem do parceiro**: Recebido · Em diagnóstico · Precisa de algo de você · Apresentação marcada · Contrato em andamento · Em execução · Encerrado. Para cada um: o próximo passo e quem está com a bola. Sem valor estimado de crédito, sem prazo de PER, sem chance de êxito |
| Save vê | O mapa entre as 12 etapas do RT (e os outros funis) e os 7 estados, e quais negócios estão "Precisa de algo de você" há mais de 7 dias |
| Regra codificada | Só dado objetivo (etapa, assinatura, execução, parecer pronto), como em D28; valor, prazo, tese e cobrança ficam com uma pessoa. Nunca prometer valor, prazo ou êxito (R21); alíquota zero só via PER (R22) |
| Dado que alimenta | `dealstage`, `hs_v2_date_entered_current_stage`, `e_cac_liberado_`, `parecer_complementar`, `id_bitrix` (HubSpot, download diário); fase do Bitrix por `lib/bitrix.py` quando o webhook ligar |
| Lacuna | Fase do Bitrix desligada **[TI]**; `nome_do_parceiro` é texto livre e precisa do roster e dos aliases para ligar o negócio ao usuário certo (consultor) **[CRM]** |
| Inspiração | Impartner e Salesforce (pipeline do parceiro visível). **Adaptamos:** o parceiro não edita etapa; vê o pós-ganho (execução), que os PRMs de software quase não mostram |

### M4. Extrato
| | |
|---|---|
| Parceiro vê | Linhas por negócio ganho em **4 estados: previsto → recebido pela Save → liberado → pago**, com linha do tempo, base de cálculo (honorário recebido), percentual do termo, retenções (IRRF, CSRF, ISS conforme o enquadramento) e a NF que ele emitiu. Linha "em conferência contratual" sem valor nem data quando o caso é atípico. Botão de contestação (10 dias corridos) |
| Save vê | Lote mensal por parceiro, checklist de elegibilidade (termo vigente, CNPJ ativo, NF, retenções, sem Bloqueado, conflito resolvido), status Bloqueado / Revisar / OK, fila de contestação com prazo de resposta de 5 d.u. |
| Regra codificada | Contratado ≠ devido ≠ pago: nada "a pagar" sem recebido (R5); liberar o conferido à medida do recebimento, atípico só com contrato (R6, D102); campo vazio bloqueia forecast, não pagamento (R7); base inclui compensação de ofício (R8); percentual do termo, não do card (R1, D64); produtos 2027 a 10% do líquido Save (R2, D78/D97); retenções (R10); calendário com corte no fim do mês e pagamento até o dia 20 de M+1 contra NF (R11, proposta); só dados do próprio parceiro, sem comissões internas nem margem (R12); linguagem "remuneração por indicação comercial e por serviços de apoio" (R13) **[Jur]** |
| Dado que alimenta | `conferencia_repasses.py` (status por ganho, códigos C/O/I), `percentual-parceiros.json`, `formato-extrato.md`, `extrato-prestacao-contas.md`, `elegibilidade-retencoes.md` |
| Lacuna | **Recebido não existe** (0 de 1.696) **[Fin]** **[CRM]**; termos dos 9 Masters com % e vigência **[Jur]** (D65); D102, D65 e D109 pendentes **[Luis]**. Até lá, o extrato mostra só "previsto" e "em conferência" |
| Inspiração | PartnerStack (estados do pagamento, ganho pendente até aprovação, saque visível). **Adaptamos:** o gatilho é o recebimento do honorário, não o "Closed Won"; NF e retenções brasileiras; sem saque automático (o Financeiro paga) |

### M5. Demandas
| | |
|---|---|
| Parceiro vê | "Abrir pedido" com tipo (status, documento, parecer, reunião, contrato, material, remuneração, outro) e o negócio ligado. A resposta aparece na própria demanda, marcada como **"Respondido pelo histórico"** (resposta pronta, conferida pela Daniela antes de sair) ou **"Chamado aberto na área"** (com a área e o prazo de retorno da Save) |
| Save vê | Fila por SLA (23 tipos de `sla.json`), sugestão de resposta do histórico, chamado sugerido "Aprovar e abrir no GLPI" (aprovação da Daniela, D98) |
| Regra codificada | Fluxo único: histórico antes do GLPI; o agente rascunha e a pessoa envia; frases permitidas (D28, D39); GLPI só leitura e rascunho até a liberação (R26); CPF, RG, CNH e dados bancários nunca no texto (R24, `lib/protecao.py`) |
| Dado que alimenta | `lib/historico.py avaliar` (7.407 documentos), `lib/registro_demandas.py`, `celula-daniela/references/sla.json`, `lib/chamados_painel.py`, `lib/medicao_respostas.py` |
| Lacuna | O WhatsApp segue aberto: o PRM substitui parte, não todo **[Luis]**; resposta automática sem revisão só depois de 30 dias com amostra de 20% (SESSOES §22) |
| Inspiração | Introw e Salesforce Agentforce (IA como 1º atendimento). **Adaptamos:** a IA prepara, a Daniela aprova; nada de valor, prazo ou tese em resposta automática |

### M6. Nível e jornada
| | |
|---|---|
| Parceiro vê | Nível atual com selo, barra de progresso até o próximo nível em **volume ativo** (líquido Save de 12 meses, sem café), benefícios do nível (não financeiros em 2027) e os passos da jornada (Registrado → Certificado → Pleno). Carta de nível individual |
| Save vê | Simulação trimestral por parceiro, quem está perto de subir, quem está em risco, em "leitura-sombra" até a decisão |
| Regra codificada | Programa Partners 2027: Master Estratégico / Avançado / Master; janela de 12 m; apuração trimestral; 2027 só benefícios não financeiros (opção A); ninguém começa abaixo; só sobe nas 4 primeiras apurações (R28); sem ranking público (R27); café fora (R30); escala de honorário 30/25/20 reprovada, nível não mexe no honorário do cliente (R9); o 120 dias de validade pode ser benefício de nível (R14) |
| Dado que alimenta | `metricas_ps.py` (aba Simulação de níveis), `25-programa-partners-2027.md` v1.1, `24-programa-crescimento-parceiro.md` |
| Lacuna | **F8 pendente** (prazo 14/11) **[Luis]**; patamares em R$ dependem de D75 (meta 2027 da diretoria); `nivel_parceiro` e `data_entrada_parceiro` não existem no HubSpot e nascem no PRM |
| Inspiração | Impartner (Program Compliance Manager: nível por regra e barra de progresso); Conta Azul e Omie (nível com nome reconhecível e selo, por volume ativo). **Adaptamos:** sem desconto por nível (o parceiro não cota) e sem leaderboard |

### M7. Biblioteca e Academia
| | |
|---|---|
| Parceiro vê | Kits por tese (T01–T17 na vitrine) e por produto pronto: o que é, para quem serve, perguntas de qualificação, o que não dizer, peça co-branded com a relação identificada. Trilha N1/N2 com certificação como porta de produto complexo (ex.: Gestão de Passivo). Produtos em validação aparecem só como **"em descoberta"**: sem taxa, condição, simulação nem peça |
| Save vê | Catálogo com dono por produto, estado (pronto, em descoberta, fora da vitrine), material pedido e não existente, uso por parceiro |
| Regra codificada | Produtos prontos (R20); em validação só como descoberta até o G2 (R19, D83, D108); T13 e T16 fora da vitrine, Funrural em conciliação (R23); publicidade identifica parceiro remunerado (R29, CONAR 12/05/2026); toda peça passa pelo auditor (R21); alíquota zero só via PER (R22) |
| Dado que alimenta | `celula-daniela/references/biblioteca-materiais.md`, `academia-trilha-v1.md`, kits do `depto-marketing`, `docs/portfolio-2027/matriz-agentes.md` |
| Lacuna | Cases aprovados para uso externo: nenhum; Academia com `[VALIDAR TÉCNICO]` e sem dono humano (PS-6) **[Jur]**; propriedade Produto no HubSpot (D37) **[CRM]** |
| Inspiração | Mindmatrix (conteúdo co-branded e LMS); Conta Azul (certificação). **Adaptamos:** o parceiro não dispara campanha com a marca dele na v1 (risco de promessa e LGPD) |

### M8. Visão do canal (só Save)
| | |
|---|---|
| Save vê | Saúde por parceiro (0–100), consultores dormentes, concentração (top 1 e top 5), ritmo de entrada e de valor, registros a vencer, conflitos abertos por severidade, extratos a liberar, demandas fora do SLA, adoção do portal |
| Parceiro vê | Nada desta tela |
| Regra codificada | Sem margem nem comissões internas fora da Save (R12); conflito decidido pelo Luis (R15); clientes sem Master fora (R18); café fora (R30); alçada (R31, `infra/alcadas.md`) |
| Dado que alimenta | `dados_bi.py` (saúde), `pacote-*.json` (bloco canal), `conflito_canal.py`, `lib/operacao.py` (sentinelas `parceiro_inativo`, `conflito_novo`), `lib/caixa.py` |
| Lacuna | Adoção do painel interno depende do lançamento ao time (D107, D0 proposto para 03/11) **[Luis]** |
| Inspiração | Impartner e Mindmatrix (scorecard e pontuação de engajamento). **Adaptamos:** o índice já existe (`dados_bi.py`), o PRM só o expõe com a fila de ação |

---

## 3. Modelo de dados mínimo

**Princípio:** o HubSpot é a fonte do negócio (só leitura, cópia diária). O PRM é a fonte do que nasce na relação com o parceiro: registro, usuário, termo, extrato, demanda, nível. Fase 1 grava no Mac (`registro/prm/`) e o painel mostra; Fase 2 grava no Azure SQL em Brazil South.

| Tabela | Campos principais | Origem |
|---|---|---|
| `parceiro` | id, tipo (Master, consultor, indicador), nome, cnpj, master_padrinho, data_entrada, situacao | **PRM** (roster de `mapeamento-hubspot.json` e aliases como carga inicial) |
| `usuario_parceiro` | id, parceiro_id, nome, email, papel (titular, consultor), id_entra (B2B), ativo, ultimo_acesso | **PRM** |
| `termo` | parceiro_id, tipo_relacao, percentual_recuperacao, regra_produtos_2027, vigencia_ini, vigencia_fim, arquivo_ref | **PRM** (Contratos, D65) |
| `registro_oportunidade` | id, parceiro_id, usuario_id, cnpj_raiz, cnpj_hmac, contato_decisor, interesse (tese ou produto), evidencia, criado_em, estado (recebido, aprovado, recusado, em conflito, expirado, convertido), valido_ate, prorrogado_ate, motivo, deal_id | **PRM** (deal_id ligado depois que a Daniela cria o card) |
| `registro_evento` | registro_id, quando, quem, de_estado, para_estado, nota | **PRM** (trilha de auditoria) |
| `conflito` | id, cnpj_raiz, registros envolvidos, severidade, fatos, decisao, decidido_por, decidido_em | **PRM** (fatos de `conflito_canal.py`) |
| `negocio` (espelho) | deal_id, cnpj_raiz, parceiro_id, pipeline, dealstage, estado_parceiro (7 estados), data_etapa, ganho_em, teses, honorario_pct, parceiro_pct_card | **HubSpot** (cópia diária, só leitura) |
| `extrato_linha` | id, deal_id, parceiro_id, competencia, base_recebida, percentual, valor_bruto, retencoes, valor_liquido, estado (previsto, recebido pela Save, liberado, pago, em conferência), nf_numero, pago_em, motivo | **PRM** (cálculo de `conferencia_repasses.py`; recebido vem do Financeiro) |
| `contestacao` | extrato_linha_id, aberta_em, texto, resposta, respondida_em, causa_raiz | **PRM** |
| `demanda` | id (D-AAAA-NNNN), parceiro_id, usuario_id, deal_id, tipo, texto, canal (portal, WhatsApp), estado, via (histórico, chamado), area, chamado_glpi_id, sla_ate, respondida_em | **PRM** (`lib/registro_demandas.py`) |
| `nivel_apuracao` | parceiro_id, trimestre, volume_ativo_12m, nivel, nivel_simulado, carta_enviada_em | **PRM** (`metricas_ps.py`) |
| `material` | id, produto, tese, estado (pronto, descoberta, fora), arquivo, auditado_em, dono | **PRM** (Marketing) |
| `acesso_log` | usuario_id, quando, tela, acao, ip_hash | **PRM** (LGPD e segurança) |

**O que nunca entra no PRM:** CPF, RG, CNH, dado bancário do parceiro (é do Financeiro), contato de sócio fora do cadastro público (R24); margem da Save e comissões internas na visão do parceiro (R12).

---

## 4. Fases

| Fase | Entregável | Depende de | Quem fornece |
|---|---|---|---|
| **0 · Regras** (até 14/11) | Regra de registro R1–R3 com validade; F8 opção A; D102, D65, D109; propriedade Produto (D37); mapa das 12 etapas para os 7 estados | Decisões do Luis | Luis; Jurídico na validade (120/90 × 180 dias); Operações de Canal prepara |
| **1 · PRM interno no painel Central** (sem TI) | Telas da Save: Visão do canal, Fila de registros, Extratos em conferência, Demandas por SLA, ficha 360. Registro entra pela Daniela (vindo do WhatsApp) e é checado por raiz de CNPJ; dados em `registro/prm/` no Mac, publicados no painel com CNPJ mascarado | D107 (lançamento do painel ao time); regra de registro da fase 0 | Agentes (código); Daniela (uso); Dados (`dados_bi.py`, `conferencia_repasses.py`) |
| **2 · Portal do parceiro, piloto** | Azure no tenant Save: Static Web Apps Standard, Function App própria (leitura agendada do HubSpot com token no Key Vault), Azure SQL serverless em Brazil South, login B2B no Entra com MFA por aplicativo. Telas: Início, Registrar, Meus negócios, Demandas, Biblioteca; extrato só com "previsto" e "em conferência". Piloto com 2 Masters | TI (assinatura, registro do app, convites B2B, revisão de segurança); Jurídico e LGPD (termos de uso, base legal, retenção, parecer OAB sobre o perímetro, guarda de CNPJ e contato no SQL) | TI da Save; Jurídico; dono do CRM (token de leitura e escopo); base técnica em `central/` (etapas 1–2 prontas) |
| **3 · Extrato real e nível** | Extrato com os 4 estados, NF, retenções e contestação; nível com barra de progresso e carta individual | Fonte de recebimentos por negócio (P5, D18); D102, D65, D109; F8; retenções validadas | Financeiro; Contratos (termos dos 9 Masters); Tributário (retenções); Luis |
| **4 · Escala** | Os 9 Masters e seus consultores, depois os indicadores; Academia com certificação; produtos 2027 na vitrine só depois do G2 (15/12) e da propriedade Produto; resposta automática de dado objetivo só depois de 30 dias com amostra de 20% | G2; D108; D37; resultado do piloto | Donos de produto (João Mattos, Paulo, Junior); Partner Success; Marketing |

**Ordem de grandeza de custo** (pesquisa, Parte E2): menos de US$ 500/ano de infraestrutura na Azure, contra US$ 3 mil a 53 mil/ano das licenças. O custo real é o tempo do time e a manutenção.

---

## 5. Riscos e o que não faremos

### Riscos
| Risco | Mitigação |
|---|---|
| A TI não nomeia responsável (sem resposta aos pedidos de 30/09, 13/10 e 23/10) | A Fase 1 não depende da TI; a Fase 2 só começa com responsável nomeado |
| O extrato aparece antes do recebido e vira cobrança | Sem fonte de recebimentos, o portal mostra só "previsto" e "em conferência", sem valor a pagar (R5) |
| Varredura da carteira pelo registro (o parceiro testa CNPJs para descobrir clientes) | Mensagem neutra única, teto diário por usuário, alerta de acertos acima do limite, trilha em `acesso_log` (R25) |
| Requalificação do Master como representante comercial (Lei 4.886/1965) e "divisão de honorários" (Lei 8.906/1994, art. 34) | Glossário fixo nas telas (R13), sem território exclusivo (R16), textos do termo e do portal revisados pelo Jurídico antes do piloto |
| Dado de cliente fora do Mac (CNPJ e contato no SQL) | Parecer LGPD antes da Fase 2; Brazil South; tenant Save; mínimo necessário; retenção definida |
| Portal vira canal paralelo ao WhatsApp e duplica trabalho | Demanda pelo portal entra no mesmo `registro/demandas.json`; métrica de % pelo portal no pacote semanal |
| Banco serverless pausado ou sem SLA | Plano serverless com cobrança do excedente (não a oferta de nível inicial), alerta de consumo, cópia diária |
| Manutenção depende dos agentes | Código no repositório com testes, como em `central/`; reavaliar compra acima de cerca de 100 parceiros ativos |

### O que não faremos (Parte D da pesquisa e regras da casa)
- MDF, CPQ, tabela de preço por nível, autocotação, pedido de desconto: o parceiro não cota (honorário é de êxito e definido pela Save).
- Rebates, POS, Channel Data Management, marketplaces de hiperescala.
- Link de afiliado e cookie; rede de recrutamento aberta; cadastro aberto (autoatendimento) de parceiro.
- Comissão disparada no ganho: o gatilho é o recebimento.
- Account mapping tipo Crossbeam: usamos a lista de CNPJs do parceiro (`mapa_base_parceiro.py`).
- Parceiro disparando campanha com a marca dele na v1.
- Ranking público, leaderboard, território exclusivo.
- Treinamento como degrau geral de nível: certificação só como porta de produto complexo.
- Escrita no HubSpot ou no GLPI pelo PRM.
- Resposta automática com valor, prazo, tese ou chance de êxito; simulação de crédito no portal.
- Produto em validação com taxa, condição ou peça antes do G2.

---

## 6. Entrega em 3 blocos

**1. O que você pediu**
Desenho do PRM próprio da Save em 8 módulos (Início, Registro, Meus negócios, Extrato, Demandas, Nível e jornada, Biblioteca e Academia, Visão do canal), cada um com regra da casa codificada, dado de origem, lacuna e inspiração de mercado; modelo de dados de 13 tabelas separando HubSpot (espelho só leitura) e PRM; 5 fases com dependências; riscos; lista do que não faremos. Protótipo navegável com os perfis Parceiro e Save.

**2. O que você também precisa**
- A Fase 1 pode começar logo depois do lançamento do painel ao time (D107), sem TI, e já ataca o resultado 3 (registro e conflito) e parte do 2 (demandas).
- O extrato é a tela que mais pesa para o parceiro e a que mais depende de terceiros: sem a fonte de recebimentos do Financeiro, ele não sai de "previsto". Vale abrir esse pedido ao Financeiro agora, em paralelo.
- O 3º estado do registro ("em análise pela Área Partners") cobre de propósito, com a mesma frase, três casos diferentes (outro parceiro, cliente da Save, índice indisponível); isso evita expor a carteira.
- Os 3 conflitos Master × Master e as 19 raízes de severidade alta pedem decisão antes de o registro valer; senão o portal nasce com fila herdada.

**3. O que falta e quem fornece**
| Falta | Quem |
|---|---|
| Regra de registro R1–R3 e validade (90 + 60, 120 para Master × 180 dias) | Luis, com o Jurídico |
| Fonte de recebimentos por negócio | Financeiro e dono do CRM (P5, D18) |
| Termos dos 9 Masters com percentual e vigência | Contratos (D65) |
| Recursos na Azure, registro do app no Entra, convites B2B, revisão de segurança | TI da Save |
| Parecer LGPD e OAB do portal, termos de uso, retenção, linguagem de remuneração | Jurídico |
| Programa de níveis (F8) e patamares (D75) | Luis; diretoria |
| Propriedade Produto (D37), data de entrada e nível do parceiro | Dono do CRM com Dados |
| Cases aprovados e Academia validada | Marketing, Tributário e Jurídico |

---

## 7. Decisões do Luis

1. **Validade do registro.** Opções: 90 dias + 60 de prorrogação para todos; 120 para Master e 90 para indicador; 180 dias (material jurídico). **Recomendação:** 120 para Master e 90 para indicador, ambos com + 60 de prorrogação mediante avanço, porque 81% dos ganhos saem em até 90 dias (p90 de 161 dias); o Jurídico ajusta o texto dos termos e os 180 dias só valem onde o termo assinado já disser isso.
2. **Regra de registro R1–R3** (raiz do CNPJ, card completo, desempate em 4 níveis, nunca duas remunerações integrais, não retroage). **Recomendação:** aprovar como v1, revisão em 90 dias com os dados da fila.
3. **Fase 1 no painel com dados no Mac** (registro em `registro/prm/`, CNPJ mascarado no painel). **Recomendação:** aprovar; é reversível e dentro das regras (vale por padrão no prazo da folha).
4. **Pedido à TI dos recursos Azure e dos convites B2B**, com piloto em 2 Masters. **Recomendação:** autorizar o pedido agora, com início condicionado a responsável nomeado na TI e ao parecer do item 5.
5. **Guarda de CNPJ e contato do decisor no Azure SQL** (exceção à regra "dado de cliente fica no Mac"). **Recomendação:** aprovar condicionado ao parecer LGPD do Jurídico, com Brazil South, tenant Save, mínimo necessário e retenção definida.
6. **O que o parceiro vê do negócio.** **Recomendação:** os 7 estados com o próximo passo; valor só no extrato e só depois do contrato assinado; nunca estimativa de crédito, prazo de PER ou chance de êxito.
7. **D102 (liberar repasse conferido à medida do recebimento; atípico só com contrato).** **Recomendação:** opção A, já recomendada pelas áreas, porque é a base do extrato.
8. **F8 (programa de níveis).** **Recomendação:** opção A; no PRM o nível fica em leitura-sombra até a decisão e a carta é individual.
9. **Quem entra no piloto do portal.** **Recomendação:** 2 Masters com seus consultores (cada consultor vê só os próprios negócios; o titular vê os do escritório); indicadores só na Fase 4.
