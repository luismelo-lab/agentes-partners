# PRM Save v2 · 02 · Especificação de regras de negócio

**Versão:** 2.0-rascunho · **Data:** 26/10/2026 · **Status:** especificação para codificar, com regras marcadas como aprovadas ou propostas
**Coordenação:** Gerente de Operações de Canal (regras de negócio), com os especialistas de Operações de Canal (registro e conflito, comissionamento, extrato, elegibilidade e retenções, política e níveis), Partner Success (níveis e jornada, onboarding, Academia), Contratos (termo do parceiro, distrato), Jurídico (perímetro regulatório e LGPD), Central Masters / célula da Daniela (triagem e SLA, retorno ao parceiro, higiene do CRM) e Qualidade (auditor de promessas).
**Base:** `docs/prm/desenho-prm-save-2026-10-26.md` (8 módulos, modelo de dados, fases), `docs/prm/contexto-interno-prm-2026-10-26.md` (regras R1 a R31), `docs/prm/engenharia-reversa-prm-2026-10-26.md`, `conselho/decisoes.md`, `infra/alcadas.md`, dossiês D102, D65, D109, D37 e F8 (`~/agentes-partners/registro/gestao/dossies/`), `departamentos/operacoes-canal/Proposta-Regra-Registro-e-Politica-Repasse-2026-09-29.md`, `central/README.md` (1ª checagem de negócio ativo e mensagem neutra), `skills/celula-daniela/references/sla.json` e as references das skills citadas.
**Público:** o desenvolvedor do PRM (Fase 1 no painel Central Partners; Fase 2 no portal na Azure). Tudo aqui deve poder virar código sem pergunta. Onde a regra ainda depende de decisão, o parâmetro tem valor padrão e uma chave de configuração, e a decisão está na seção 18.

---

## 0. Como ler

### 0.1 Marcação de cada regra
| Marca | Significado | O que o código faz |
|---|---|---|
| **[A]** | Aprovada (decisão citada) | Codificar como está |
| **[P · X]** | Proposta; depende da decisão X (seção 18) | Codificar com o valor padrão e a chave de configuração; a mudança de valor não exige deploy |
| **[O]** | Operacional, dentro da alçada da dona da entrega (`infra/alcadas.md`, D98) | Codificar; a dona pode ajustar o parâmetro |

### 0.2 Convenções técnicas (valem para todos os módulos)
1. **Fuso e carimbo:** `America/Sao_Paulo`; todo carimbo é gravado em UTC com milissegundos e exibido no fuso local no formato `dd/mm/aaaa hh:mm`.
2. **Dia útil (d.u.):** segunda a sexta, menos os feriados da tabela `calendario_feriados` (nacionais por padrão; municipais da sede da Save a incluir pelo Financeiro). Prazo em d.u. vence às 23h59 do último dia útil. Prazo em dias corridos vence às 23h59 do último dia, mesmo que caia em fim de semana.
3. **CNPJ:** aceitar o formato alfanumérico (IN RFB 2.229/2024) e validar os dígitos com `lib/cnpj.py`. **Raiz** = os 8 primeiros caracteres. Toda regra de registro, conflito e proteção usa a raiz (matriz e filiais juntas).
4. **Chave de privacidade:** a raiz só circula fora do banco do PRM como HMAC (mesmo sal `CENTRAL_SAL` do `central/api/central_api/negocio_ativo.py`). No painel interno o CNPJ aparece mascarado (`12.345.***/****-**`).
5. **Trilha:** toda transição de estado grava uma linha em `registro_evento` (ou equivalente do módulo) com `quando`, `quem` (usuário ou `sistema`), `de_estado`, `para_estado`, `motivo_interno`, `motivo_externo`. Nada é apagado; correção é nova linha.
6. **Textos ao parceiro:** todo texto que aparece ao parceiro sai do catálogo da seção 14 (chave `M-xx`), com variáveis entre chaves. Texto livre escrito por pessoa passa pelo auditor (`skills/depto-qualidade/scripts/auditar_texto.py`) antes de sair; com alerta ALTO ou MÉDIO, o botão de envio fica desabilitado.
7. **Origem das regras R1 a R31:** numeração do `contexto-interno-prm-2026-10-26.md`, seção 3.

---

## 1. Regras transversais (valem em todos os módulos)

| ID | Regra | Marca | Origem |
|---|---|---|---|
| PRM-R01 | O PRM **lê** o HubSpot (cópia diária em `departamentos/resultados/dados/hubspot-AAAA-MM-DD.json`) e **nunca escreve** nele nem no GLPI. Tudo que precisa ir ao CRM vira tarefa para a Daniela (ou o time de CRM) com o dado pronto. | [A] | CLAUDE.md §3; D18; D26; R26 |
| PRM-R02 | **Isolamento por parceiro no servidor.** Toda consulta do perfil externo filtra por `parceiro_id` (e por `usuario_id` no perfil Consultor) na API, nunca só na tela. Teste obrigatório: usuário de um parceiro tentando ler id de outro recebe 404 (não 403, para não confirmar existência). | [A] | R12; `formato-extrato.md` |
| PRM-R03 | **Nenhum texto promete valor, prazo ou êxito.** Proibido ao parceiro: estimativa de crédito, prazo de PER ou de ressarcimento, chance de êxito, "aprovado" para crédito. Alíquota zero: só via PER (DCOMP vedada, D14) em qualquer material ou resposta. | [A] | CLAUDE.md §3; R21; R22; D14; D28 |
| PRM-R04 | **Linguagem da remuneração:** nas telas externas usar "remuneração por indicação comercial e por serviços de apoio" (forma longa) ou "remuneração" (forma curta). É vedado "repasse de honorários", "divisão de honorários" ou "comissão sobre honorários" em texto externo. O termo "repasse" fica só nas telas internas. | [P · DL-14 (Jurídico)] | R13; Lei 8.906/1994, art. 34; `depto-operacoes-canal` regra 5 |
| PRM-R05 | **Mensagem neutra única** para todo caso em que a resposta revelaria a carteira da Save ou de outro parceiro: "Não foi possível seguir com esta consulta. Fale com a Área Partners." (texto `M-00`). O motivo real vai só para a trilha interna. | [A] | Decisão do Luis de 23/10 (SESSOES §22); `central/README.md`; R25 |
| PRM-R06 | **LGPD, mínimo necessário:** o PRM não guarda CPF, RG, CNH, dado bancário (do parceiro ou do cliente), telefone pessoal nem dado de sócio fora do cadastro público. Campos de texto livre passam por `lib/protecao.py` antes de gravar; se acharem um desses dados, o envio é bloqueado com o texto `M-90`. | [A] | R24; CLAUDE.md §3 |
| PRM-R07 | **Não retroage.** Regra nova vale para registros, negócios e linhas de extrato criados depois da data de vigência gravada na própria regra (`regra.vigencia_ini`). O legado é decidido caso a caso pelo Luis. | [A] | R14; LINDB art. 6º; proposta de 29/09 item 9 |
| PRM-R08 | **Escopo:** só entram parceiros com Master (o próprio Master, seus consultores e indicadores com Master padrinho). Clientes sem Master são de outra área e ficam fora do PRM. | [A] | D76; R18 |
| PRM-R09 | **Café fora** de métricas, níveis e metas (não de remuneração já devida). | [A] | R30 (regra do Luis de 20/08/2026) |
| PRM-R10 | **Alçada no código:** cada ação tem um papel dono (seção 2). Ao Luis só sobe regra, preço, meta, remuneração (percentual), conflito de canal, produto em validação e os limites (> R$ 1 mi de crédito com decisão; 3+ áreas em conflito; risco jurídico ou LGPD sem precedente). | [A] | D98; `infra/alcadas.md`; R31 |
| PRM-R11 | **Produtos em validação** (Crédito Internacional, Maquila, captação de capital, home equity, turnkey) aparecem só como "em descoberta": sem taxa, condição, simulação, prazo, percentual de remuneração ou peça. A família de remuneração do CI fica desligada (`familia_ci_ativa = false`) até o G2. | [A] | D83; D108 (pendente, efeito igual); R19; R3 |
| PRM-R12 | **Sem ranking** público de parceiros ou de pessoas. Nenhuma tela externa mostra dado agregado que permita comparar parceiros. | [A] | R27 |
| PRM-R13 | **Pessoa envia, agente prepara.** Nenhuma mensagem com texto livre sai ao parceiro sem aprovação da dona (Daniela, Jenifer, Geovana ou Financeiro). Mensagens de estado com texto fixo do catálogo (seção 14) saem pelo sistema se a DL-12 for aprovada. | [A] (texto livre) · [P · DL-12] (texto fixo) | D26; D28; D98 |
| PRM-R14 | **Contratado ≠ devido ≠ pago.** Nenhuma tela externa mostra valor "a pagar" sem recebimento do honorário registrado pelo Financeiro. | [A] | R5; `depto-operacoes-canal` regra 3 |

---

## 2. Papéis e permissões

### 2.1 Papéis
| Papel | Quem é | Lado | Como entra |
|---|---|---|---|
| `titular` | Sócio ou responsável do escritório parceiro (Master ou indicador). Assina o termo | Externo | Convite B2B após termo assinado e aceite dos Termos de Uso (seção 15) |
| `consultor` | Pessoa do escritório que indica (os 27 consultores dos Masters estão nesse papel) | Externo | Convite pedido pelo titular, aprovado pela Daniela |
| `master` | Atributo do parceiro (`parceiro.tipo = master`), não de pessoa. Dá ao titular do Master a visão dos seus consultores e, como padrinho, o andamento do onboarding dos indicadores apadrinhados | Externo | Cadastro do roster (`mapeamento-hubspot.json`) |
| `daniela` | Gestão de conta dos 9 Masters, demandas, registro, retorno ao parceiro | Interno | Entra ID da Save |
| `jenifer` | BDR, recrutamento de indicadores, leads para Master, onboarding | Interno | Entra ID |
| `geovana` | Suporte técnico, reuniões técnicas, Recuperador, curadoria técnica da Academia | Interno | Entra ID |
| `financeiro` | Recebimentos, aprovação do extrato, NF, retenções, pagamento | Interno | Entra ID |
| `contratos` | Termo do parceiro (percentual, vigência, anexo de remuneração), distrato | Interno | Entra ID |
| `luis` | Gerente comercial Masters: regra, percentual, conflito, nível, frases permitidas | Interno | Entra ID |
| `sistema` | Rotinas agendadas (expiração, alertas, cópia diária do HubSpot) | Técnico | Identidade de serviço (client credentials, etapa 4 do `central/`) |

### 2.2 Matriz de permissões (V = vê, A = age, — = sem acesso)
| Ação | titular | consultor | master (titular) | daniela | jenifer | geovana | financeiro | contratos | luis |
|---|---|---|---|---|---|---|---|---|---|
| Registrar oportunidade | A | A | A | A (em nome do parceiro, Fase 1) | A (lead BDR oferecido) | — | — | — | V |
| Ver registros | V (do escritório) | V (os próprios) | V (escritório + consultores) | V (todos) | V (todos) | V | — | — | V |
| Aprovar ou recusar registro sem conflito | — | — | — | A | — | — | — | — | V |
| Enviar registro a conflito | — | — | — | A | A | — | — | — | V |
| Decidir conflito | — | — | — | — | — | — | — | — | A |
| Prorrogar registro (manual) | pede | pede | pede | A | — | — | — | — | V |
| Ver Meus negócios | V (escritório) | V (os próprios) | V (escritório + consultores) | V | V | V | — | — | V |
| Marcar "Precisa de algo de você" | — | — | — | A | A | A | — | — | — |
| Ver Extrato | V (escritório) | — | V (escritório) | V | — | — | V | V | V |
| Registrar recebimento | — | — | — | — | — | — | A | — | V |
| Aprovar extrato e pagamento | — | — | — | — | — | — | A | — | V |
| Contestar linha | A | — | A | — | — | — | — | — | — |
| Responder contestação | — | — | — | rascunha envio | — | — | A (cálculo, retenção) | A (termo) | A (percentual, regra) |
| Abrir demanda | A | A | A | A (em nome do parceiro) | — | — | — | — | — |
| Responder demanda | — | — | — | A (aprova e envia) | A (as dela) | A (as dela) | A (remuneração) | A (contrato) | A (alçada) |
| Ver nível e jornada | V (o próprio, se DL-10) | V (jornada do escritório) | V | V | V | — | — | — | A (aprova carta) |
| Ver Biblioteca e Academia | V | V | V | A (curadora) | V | A (curadora técnica) | — | — | V |
| Publicar material | — | — | — | A (após auditor e validações) | — | — | — | — | A (exemplo em escala) |
| Convidar usuário do escritório | pede | — | pede | A | A (indicador novo) | — | — | — | — |
| Cadastrar termo, percentual e vigência | — | — | — | — | — | — | — | A | A (percentual) |
| Visão do canal | — | — | — | V | V | V | V (bloco extrato) | — | V |

**Regras de papel:**
- PRM-R15 [A] · O consultor nunca vê extrato nem percentual: a remuneração é do escritório (pessoa jurídica). Origem: R12; elegibilidade só PJ (seção 6.6).
- PRM-R16 [P · DL-11] · O Master padrinho vê do indicador apadrinhado só o andamento do onboarding (marcos), nunca os negócios nem a remuneração dele.
- PRM-R17 [O] · Saída de consultor do escritório: o titular pede a desativação; o acesso cai no mesmo dia; os registros e negócios ficam com o escritório (`parceiro_id`), e o titular pode redistribuir a atribuição interna (`usuario_id`) entre consultores.
- PRM-R18 [A] · Segregação: quem calcula (script de conferência + Operações de Canal) ≠ quem aprova (Financeiro; percentual com o Luis) ≠ quem paga (Financeiro). O código impede que o mesmo usuário registre recebimento e aprove o extrato da mesma competência. Origem: proposta de 29/09, Parte 2, item 9; D98.

---

## 3. Parâmetros configuráveis

Tabela `config` (chave, valor, unidade, marca, quem muda, vigência). Mudança gera evento na trilha.

| Chave | Padrão | Unidade | Marca | Quem muda | Origem |
|---|---|---|---|---|---|
| `registro.unidade` | `raiz` (alternativa `raiz_tese`) | — | [P · DL-01] | Luis | R14; proposta R1 |
| `registro.validade_master_dias` | 120 | dias corridos | [P · DL-02] | Luis | desenho §7 item 1; IGEL 120 para níveis altos |
| `registro.validade_indicador_dias` | 90 | dias corridos | [P · DL-02] | Luis | proposta R2; 80,8% dos ganhos em até 90 dias |
| `registro.prorrogacao_dias` | 60 | dias corridos | [P · DL-02] | Luis | proposta R2 |
| `registro.prorrogacoes_max` | 1 | vezes | [P · DL-02] | Luis | proposta R2 |
| `registro.atividade_para_prorrogar_dias` | 30 | dias corridos | [P · DL-02] | Luis | proposta item 4 |
| `registro.validade_conta_de` | `carimbo_completo` | — | [P · DL-01] | Luis | proposta item 3 |
| `registro.protecao_pos_contrato_meses` | 12 | meses após o último recebimento | [P · DL-01] | Luis | proposta item 5 |
| `registro.preferencia_tese_nova_dias` | 15 | dias corridos | [P · DL-01] | Luis | proposta item 6 |
| `registro.cauda_mediacao_meses` | 6 | meses após expiração ou perda | [P · DL-04] | Luis + Jurídico | CC art. 727 |
| `registro.sla_decisao_du` | 1 | d.u. | [O] | Daniela | `sla.json` COM-NOVO-NEGOCIO |
| `registro.resposta_minima_horas` | 4 | horas úteis | [O] | Daniela | anti-canal lateral (PRM-R27) |
| `registro.sla_conflito_du` | 10 | d.u. | [P · DL-01] | Luis | pauta semanal |
| `registro.pausa_validade_em_conflito` | `true` | — | [P · DL-01] | Luis | — |
| `registro.complemento_mantem_carimbo_du` | 3 | d.u. | [P · DL-01] | Luis | — |
| `registro.teto_diario_usuario` | 10 | registros por dia | [O] | Daniela com TI | `central/` (teto diário) |
| `registro.teto_neutros_dia_usuario` | 3 | respostas neutras por dia | [O] | Daniela com TI | `CENTRAL_LIMITE_ATIVO` |
| `registro.aviso_vencimento_dias` | [15, 3] | dias antes | [O] | Daniela | — |
| `lead_bdr.reserva_dias` | 45 | dias corridos | [A] | Jenifer | R17 |
| `lead_bdr.aceite_du` | 3 | d.u. | [A] (vale por padrão desde 28/10) | Jenifer e Daniela | R17; D98 |
| `negocio.alerta_pendencia_parceiro_dias` | 7 | dias corridos | [O] | Daniela | desenho M3 |
| `negocio.ecac_pendente_alerta_du` | 2 | d.u. | [O] | Daniela | — |
| `extrato.percentual_fonte` | `termo` (fallback `percentual-parceiros.json` com selo "termo a localizar") | — | [A] fonte · [P · D65] termo | Contratos; Luis no percentual | D64; R1; D65 |
| `extrato.base_recuperacao` | `honorario_recebido` (inclui compensação de ofício com Selic) | — | [A] gatilho e base de ofício · [P · DL-07] bruto × líquido | Financeiro + Luis | R5; D95; OC-4 |
| `extrato.pct_produtos_2027` | 10 | % do líquido Save recebido | [A] | Luis (Gilberto) | D78; D97 |
| `extrato.deducao_antes_10pct` | `nenhuma` | — | [P · OC-1] | Financeiro + Gilberto | D97 ("a confirmar") |
| `familia_ci_ativa` | `false` | — | [A] | Luis após G2 | D61; D108; R3 |
| `extrato.corte` | último dia do mês | — | [P · OC-18] | Financeiro | R11 |
| `extrato.calculo_du` | 5 | º d.u. de M+1 | [P · OC-18] | Financeiro | R11 |
| `extrato.aprovacao_du` | 7 | º d.u. de M+1 | [P · OC-18] | Financeiro | R11; D98 |
| `extrato.publicacao_du` | 8 | º d.u. de M+1 | [P · OC-18] | Financeiro | R11 |
| `extrato.contestacao_dias` | 10 | dias corridos após publicação | [P · OC-18] | Financeiro | R11 |
| `extrato.resposta_contestacao_du` | 5 | d.u. | [P · OC-18] | Financeiro | R11 |
| `extrato.pagamento_dia` | 20 (15 se DL-15 = representação) | dia de M+1 | [P · OC-18 / DL-15] | Financeiro | R11; Lei 4.886 art. 32 §1º |
| `extrato.nf_limite_dia` | 15 | dia de M+1 para a NF entrar no ciclo | [P · OC-18] | Financeiro | — |
| `extrato.tolerancia_conciliacao` | 0,01 | R$ | [A] | — | `extrato-prestacao-contas.md` §5 |
| `extrato.estorno_limite_pct_ciclo` | 50 | % do bruto do ciclo | [P · DL-08] | Luis + Jurídico | proposta Parte 2 item 7 |
| `extrato.estorno_prazo_meses` | 24 | meses para compensar | [P · DL-08] | Luis + Jurídico | idem |
| `extrato.contestacao_procedente_alerta_pct` | 10 | % do valor do mês | [O] | Financeiro | `extrato-prestacao-contas.md` §5 |
| `extrato.mostra_valor_previsto` | `false` | — | [P · DL-09] | Luis | R5; desenho §7 item 6 |
| `retencao.irrf_pct` | 1,5 | % | [P · Tributário] | Tributário | RIR/2018 art. 718 |
| `retencao.csrf_pct` | 4,65 (só se o código da NF estiver na lista do art. 30) | % | [P · Tributário] | Tributário | Lei 10.833 arts. 30 e 31 |
| `retencao.csrf_dispensa_ate` | 10,00 | R$ | [A] | — | Lei 10.833 art. 31 §3º |
| `retencao.regra_2027` | `a_validar` (bloqueia cálculo de retenção a partir de 01/01/2027 até validar) | — | [P · Tributário] | Tributário | LC 214/2025 |
| `demanda.reabertura_dias` | 7 | dias corridos | [O] | Daniela | `triagem-sla.md` |
| `demanda.fecha_sem_reacao_du` | 5 | d.u. | [O] | Daniela | — |
| `demanda.escala_du` | [1, 3, 5] | d.u. vencidos → área, gestor, Luis | [A] (vale por padrão desde 28/10) | Daniela | D98; CD2 |
| `demanda.anexos_habilitados` | `false` | — | [P · DL-13] | Jurídico + TI | LGPD art. 46 |
| `nivel.modo` | `sombra` | — | [P · F8] | Luis | F8; R28 |
| `nivel.janela_meses` | 12 | meses | [P · F8] | Luis | R28 |
| `nivel.patamares` | Estratégico sobe R$ 8 mi e 4/4 trimestres ≥ R$ 1 mi, mantém R$ 6 mi e 3/4; Avançado sobe R$ 1,5 mi e 3/4 ≥ R$ 250 mil, mantém R$ 1,1 mi e 2/4; Master: ganho em 1 dos 2 últimos trimestres | líquido Save sem café | [P · F8 e D75] | Luis | `25-programa-partners-2027.md` v1.1 |
| `nivel.limite_por_negocio` | 50% do patamar (Estratégico); R$ 750 mil (Avançado) | — | [P · F8] | Luis | idem |
| `nivel.so_sobe_apuracoes` | 4 | apurações após a adesão | [P · F8] | Luis | R28 |
| `nivel.observacao_trimestres` | 2 | trimestres | [P · F8 (L6 opção 2)] | Luis | F8 |
| `academia.nota_minima` | 80 | % (e 100% nas questões do módulo 7) | [O] | Partner Success | `designer-academia.md` |
| `academia.recertificacao_meses` | 12 (ou gatilho normativo) | meses | [O] | Partner Success | idem |
| `onboarding.marcos` | N1 até D+30; ≥ 3 registros até D+30; ≥ 1 diagnóstico até D+60; 1ª apresentação até D+90; ≥ 5 registros até D+90; 1º ganho até D+120 | — | [O] | Partner Success, Jenifer | `coach-onboarding-enablement.md` |
| `canal.dormente_dias` | 90 | dias sem negócio novo, com ganho em 12 m | [A] | — | métrica do pacote |
| `canal.saude_alerta` | 50 | índice 0–100 | [O] | Daniela | `dados_bi.py` |
| `retencao_dados.contato_decisor_dias` | 90 | dias após recusa, expiração ou perda | [P · DL-13] | Jurídico | LGPD art. 6º III; art. 16 |
| `retencao_dados.registro_anos` | 5 | anos após o fim da relação | [P · DL-13] | Jurídico | CC art. 206 §5º I; Lei 4.886 art. 44 parágrafo único |
| `retencao_dados.acesso_log_meses` | 12 | meses (mínimo legal 6) | [P · DL-13] | Jurídico + TI | Lei 12.965/2014, art. 15 |
| `negocio.visibilidade_campos` | matriz campo → {parceiro, so_titular, rotulo, ressalva, auditar, travado}; padrão: tudo visível, menos os campos travados (§11A) | — | [A · Luis 26/10/2026] | Luis | PRM-R113, R114 |
| `negocio.parado_dias` | 30 | dias na mesma etapa (aging) | [O·dev] | Daniela | PRM-R116 |
| `negocio.produto_por_pipeline` | funil do HubSpot → produto | — | [O·dev] | Daniela | 03 §2.4 (lacuna "produto") |
| `painel.base_pequena` | 5 | n mínimo para mostrar taxa | [O·dev] | — | PRM-R118; 03 §5 |
| `canal.base_pequena_conversao_registro` | 20 | n mínimo por grupo | [O·dev] | — | 03 §5 |
| `canal.meta_mensal` | out R$ 75 mi · nov R$ 100 mi · dez R$ 75 mi | R$ de crédito de contrato fechado | [A · D111] | Luis | vale quando `registro/gestao/gestao.json` não está disponível |

**Percentuais por parceiro:** nunca no código nem nesta especificação. A fonte é `termo.percentual_recuperacao` (cadastrado por Contratos, D65); enquanto o termo não estiver no cadastro, a carga inicial vem de `departamentos/operacoes-canal/percentual-parceiros.json` (informado pelo Luis em 13/10/2026) com o selo interno "termo a localizar". O percentual do card do HubSpot (`honorarios_parceiro`) só serve para alerta de divergência (PRM-R60).

---

## 3A. Fases: o que muda entre Fase 1 e Fase 2

| Tema | Fase 1 (painel interno, sem TI) | Fase 2 (portal do parceiro na Azure) |
|---|---|---|
| Quem registra | A Daniela, a partir do WhatsApp, em nome do parceiro | O próprio parceiro (titular ou consultor) |
| Carimbo do registro | Hora da mensagem que completou os dados no WhatsApp, anotada pela Daniela (`carimbo_origem = whatsapp`) | Hora do envio completo no portal (`carimbo_origem = portal`) |
| Textos ao parceiro | Rascunho pronto (catálogo `M-xx`) que a Daniela envia pelo WhatsApp | Na tela e por e-mail (DL-12) |
| Dados | `registro/prm/` no Mac (JSON), painel com CNPJ mascarado | Azure SQL em Brazil South (depende da DL-16) |
| Extrato | Só interno, em "previsto" e "em conferência" | Externo com os estados da seção 6, quando houver fonte de recebimentos |

As regras de estado são as mesmas nas duas fases; só muda quem dispara a transição de entrada.

---

## 4. Módulo 1 · Registro de oportunidade

### 4.1 Formulário e validação
| Campo | Obrigatório | Validação | Observação |
|---|---|---|---|
| `cnpj` | Sim | 14 caracteres, alfanumérico aceito, dígitos válidos (`lib/cnpj.py`) | Grava `cnpj_raiz` e `cnpj_hmac` |
| `razao_social` | Sim | Preenchida pela consulta pública quando a DL-16 permitir a chamada externa; senão digitada | Empresário individual: mascarar o nome civil na tela interna (pendência do Jurídico, minuta de 23/10 item 3) |
| `contato_decisor_nome` e `contato_decisor_cargo` | Sim | Texto, sem CPF (`lib/protecao.py`) | — |
| `contato_decisor_canal` | Sim, um dos dois | E-mail corporativo ou telefone comercial da empresa | Telefone celular pessoal: não pedir (CLAUDE.md §3) |
| `interesse` | Sim | Lista fechada: teses da vitrine (T01 a T17, sem T13 e T16), produtos prontos (R20) e "Outro tema (em descoberta)" | Produtos em validação nunca aparecem pelo nome com condição (PRM-R11) |
| `como_conhece` | Sim | Lista: "cliente do meu escritório"; "relacionamento comercial"; "indicação de terceiro"; "outro" | — |
| `evidencia_tipo` | Sim | Lista: "declaração de relacionamento" (padrão para cliente do escritório); "reunião marcada" (com data); "documento recebido"; "procuração ou e-CAC" | Evidência mínima do registro válido (proposta item 2) |
| `evidencia_nota` | Não | Até 500 caracteres, sem dado pessoal | — |
| `declaracao_lgpd` | Sim | Caixa de seleção: "Declaro que tenho autorização ou base legal para compartilhar este contato com a Save para esta finalidade." | LGPD arts. 7º e 42 |
| `declaracao_sem_promessa` | Sim (1ª vez por usuário) | Caixa de seleção: "Não prometi à empresa valor, prazo ou resultado." | R21 |

PRM-R20 [P · DL-01] · **Registro válido** = todos os campos obrigatórios preenchidos e válidos. Registro incompleto não é enviado (o botão fica desabilitado) e não tem carimbo. Origem: proposta item 2.

### 4.2 Checagem na entrada (algoritmo, roda no envio, antes de qualquer resposta)
1. Validar o formulário (4.1). Falhou: fica em `rascunho`.
2. Conferir tetos do usuário: `registro.teto_diario_usuario` e `registro.teto_neutros_dia_usuario`. Passou do teto: estado `em_analise` com o texto `M-01`, flag interna `teto` e alerta à Daniela (possível varredura). Origem: `central/README.md`.
3. Procurar a raiz no índice HMAC (negócio aberto ou ganho no HubSpot, em **todos os funis**, inclusive Gestão de Passivo) e na tabela `registro_oportunidade` (registros vivos: `aprovado`, `prorrogado`, `em_analise`, `em_conflito`, `protegido_cliente`).
4. Classificar (resultado interno `checagem_resultado`):
   - `livre`: nenhum registro vivo e nenhum negócio aberto ou ganho na raiz.
   - `proprio_usuario`: registro vivo do mesmo usuário.
   - `proprio_escritorio`: registro vivo de outro usuário do mesmo `parceiro_id`.
   - `outro_parceiro`: registro vivo ou negócio de outro parceiro.
   - `cliente_save`: negócio aberto ou ganho sem parceiro ou de venda direta, ou cliente de outra área.
   - `indice_ausente`: índice indisponível (falha fechada; não consulta API externa).
5. Responder:
   - `proprio_usuario` → mostra o registro existente com `M-03a`; não cria registro novo.
   - `proprio_escritorio` → `M-03b`; não cria registro novo.
   - `livre`, `outro_parceiro`, `cliente_save`, `indice_ausente` → cria o registro em `em_analise` e mostra **o mesmo texto** `M-01`. O resultado real fica só em `checagem_resultado`.
6. Rodar em segundo plano `crm_checagem.py --cnpj` (duplicidade, conflito, situação na Receita, Simples) e anexar o parecer ao registro para a Daniela.

PRM-R21 [A] · Os casos `livre`, `outro_parceiro`, `cliente_save` e `indice_ausente` recebem o mesmo texto e o mesmo tempo mínimo de resposta. Origem: R25; decisão do Luis de 23/10.
PRM-R22 [A] · O registro é feito pela raiz; matriz e filiais são a mesma unidade. Origem: R14; proposta item 1.

### 4.3 Máquina de estados

| Estado (código) | Entra quando | Quem dispara | Prazo | O que o parceiro vê (texto exato) |
|---|---|---|---|---|
| `rascunho` | Formulário salvo sem todos os campos | parceiro | Some após 30 dias sem edição | "Rascunho salvo. Complete os campos obrigatórios para enviar." |
| `em_analise` | Envio completo (carimbo gravado) | sistema | Decisão em até `registro.sla_decisao_du` (1 d.u.); nunca antes de `registro.resposta_minima_horas` (4 h úteis) | `M-01`: "Registro recebido em {carimbo}. A Área Partners confere os dados e responde aqui." |
| `aguardando_parceiro` | A Daniela pede esclarecimento sobre a evidência | daniela | O parceiro responde em até `registro.complemento_mantem_carimbo_du` (3 d.u.) e mantém o carimbo; depois disso o registro vai a `recusado` (motivo "faltam dados") | `M-02`: "Precisamos de uma informação para concluir o registro: {pergunta}. Responda até {data_limite} para manter a data e a hora do registro." |
| `em_conflito` | A checagem acha `outro_parceiro` com registro vivo ou negócio ativo, e a Daniela confirma que não é cadastro incompleto | daniela | Decisão do Luis em até `registro.sla_conflito_du` (10 d.u.); a validade fica pausada | Igual a `em_analise` (`M-01`). Depois de 1 d.u.: `M-04`: "A análise deste registro precisa de mais tempo. Avisaremos você aqui." |
| `aprovado` | Daniela aprova (`livre`), ou Luis decide o conflito a favor | daniela ou luis | Vale até `valido_ate` = carimbo + validade do tipo de parceiro | `M-05`: "Registro aprovado. A empresa fica registrada para você até {valido_ate}. O registro é uma proteção temporária desta oportunidade e não cria exclusividade sobre a empresa." |
| `convertido` | O negócio do registro aparece na cópia do HubSpot (`deal_id` ligado) | sistema | — | `M-06`: "Negócio aberto para esta empresa. Acompanhe em Meus negócios. O registro vale até {valido_ate}." |
| `prorrogado` | No vencimento, o negócio avançou de etapa ou teve atividade nos últimos 30 dias; ou a Daniela aceita o pedido do parceiro | sistema ou daniela | Vale até `prorrogado_ate` = `valido_ate` + 60 dias; só 1 vez | `M-07`: "Registro prorrogado até {prorrogado_ate} porque houve avanço no atendimento desta empresa." |
| `protegido_cliente` | O negócio da raiz vira ganho (Negócio Fechado) com este parceiro | sistema | Enquanto houver contrato vigente e por mais 12 meses após o último recebimento | `M-08`: "Contrato assinado com esta empresa a partir da sua indicação. A empresa segue registrada para você enquanto o contrato estiver vigente e por mais 12 meses depois do último recebimento da Save." |
| `expirado` | Venceu `valido_ate` (ou `prorrogado_ate`) sem ganho e sem critério de prorrogação | sistema (rotina diária às 06h00) | Final | `M-09`: "O registro desta empresa terminou em {data} pelo fim do prazo. A empresa pode ser registrada de novo." |
| `encerrado_sem_contrato` | O negócio ligado foi para Negócio Perdido | sistema | Final | `M-10`: "O atendimento desta empresa foi encerrado sem contrato em {data}, e o registro terminou. A empresa pode ser registrada de novo. Se você tiver informação nova sobre ela, abra um pedido em Demandas." |
| `recusado` | Daniela recusa, ou Luis decide o conflito contra, ou o complemento não chegou | daniela ou luis ou sistema | Final | `M-11`: "Não foi possível aceitar este registro. Motivo: {motivo_externo}. Se quiser conversar sobre o caso, abra um pedido em Demandas." |
| `cancelado` | O parceiro desiste | parceiro | Final | "Registro cancelado por você em {data}." |
| `encerrado_fim_parceria` | O termo do parceiro terminou (seção 12, caso 8) | contratos | Final | `M-12`: "O registro terminou em {data} com o encerramento da parceria." |

**Motivos externos de recusa (lista fechada, `motivo_externo`):**
1. "faltam dados obrigatórios: {campos}";
2. "a situação cadastral do CNPJ não permite o atendimento";
3. "a empresa está fora do perfil atendido pela Área Partners neste momento";
4. "não foi possível seguir com este registro" (genérico; obrigatório para `outro_parceiro`, `cliente_save`, conflito decidido contra e venda direta).

PRM-R23 [A] · O motivo 4 é o único permitido quando a recusa decorre de outro parceiro ou de cliente da Save. Origem: R25; PRM-R05.
PRM-R24 [P · DL-03] · Quando o parceiro pergunta o motivo de uma recusa genérica, a Daniela usa o texto `M-13` e, se o parceiro trouxer evidência de relacionamento anterior, abre o caso como `contestacao_registro` para o Luis (vira `em_conflito` com o registro original preservado).

**Transições proibidas (o código rejeita):** `expirado`, `recusado`, `cancelado`, `encerrado_*` → qualquer estado (final é final; novo registro é nova linha); `aprovado` → `em_analise`; qualquer transição externa feita por `consultor` ou `titular` que não seja `rascunho → em_analise`, `aprovado → cancelado` e o pedido de prorrogação.

### 4.4 Regras do registro
| ID | Regra | Marca | Origem |
|---|---|---|---|
| PRM-R25 | Precedência = carimbo do registro completo (data e hora do envio no portal, ou da mensagem completa no WhatsApp na Fase 1). A data informada pelo parceiro não conta. | [P · DL-01] | Proposta item 3 |
| PRM-R26 | Validade: 120 dias para Master e seus consultores, 90 dias para indicador, contados do carimbo; 1 prorrogação de 60 dias se, na véspera do vencimento, o negócio avançou de etapa ou teve atividade registrada nos últimos 30 dias. A rotina diária aplica a prorrogação sozinha; sem critério, avisa em 15 e 3 dias antes (`M-14`) e o parceiro pode pedir a prorrogação com o fato novo (a Daniela decide em 1 d.u.). | [P · DL-02] | Proposta item 4; desenho §7 item 1 |
| PRM-R27 | Nenhuma aprovação é instantânea. Mesmo o caso `livre` espera `registro.resposta_minima_horas` antes da decisão, para que o tempo de resposta não revele o resultado da checagem. | [O] | R25 (anti-varredura) |
| PRM-R28 | Aprovar um registro `livre` é da Daniela; recusar por dados ou por perfil também. Registro com `outro_parceiro` vai a conflito. Registro com `cliente_save` é recusado com o motivo 4, salvo se a Daniela achar que o negócio existente é do mesmo parceiro com cadastro incompleto (aí corrige pela higiene do CRM e aprova). | [A] alçada · [P · DL-01] regra | D98; R15 |
| PRM-R29 | Aprovado o registro, o sistema cria a tarefa "Criar card no HubSpot" para a Daniela, com os dados prontos e SLA de 1 d.u. Se o `deal_id` não aparecer na cópia diária em 3 d.u., sai alerta interno. O registro não depende do card para valer: o carimbo é do registro. | [A] PRM não escreve no CRM · [O] prazos | R26; desenho M2 |
| PRM-R30 | Conflito de canal é decisão do Luis. O sistema monta a ficha com os fatos (carimbo de cada registro, etapas, ganhos e abertos por canal, teses, evidências, quem levou à reunião de diagnóstico) e o que a regra proposta diria; não atribui o cliente. A decisão gravada traz `decisao`, `decidido_por`, `decidido_em` e, se houver divisão, os percentuais. | [A] | D98; R15; `registro-conflito-canal.md` |
| PRM-R31 | Desempate, nesta ordem: (1) registro válido mais antigo e ainda dentro da validade; (2) mesmo dia, ou nenhum válido: quem comprovou primeiro o relacionamento (reunião, documento, procuração); (3) quem levou a empresa à reunião de diagnóstico; (4) decisão do Luis, com divisão só como exceção documentada. | [P · DL-01] | Proposta item 7 |
| PRM-R32 | Nunca duas remunerações integrais sobre o mesmo honorário. Divisão gravada soma no máximo 100% do percentual de um único termo (o do parceiro vencedor, salvo decisão). | [A] princípio · [P · DL-01] cálculo | Proposta item 7.4; CC art. 728 |
| PRM-R33 | O registro é proteção temporária de oportunidade, **não** território nem exclusividade. Nenhuma tela usa "exclusivo", "território" ou "carteira protegida". | [A] | R16; CC art. 726; Lei 4.886 art. 31 |
| PRM-R34 | Tese nova em empresa já `protegido_cliente`: o dono do registro tem preferência de 15 dias para trabalhar a tese; se recusar ou não responder, outro parceiro pode registrar para aquela tese (só vale se DL-01 escolher `raiz_tese`; com `raiz`, a raiz inteira segue protegida). | [P · DL-01] | Proposta item 6 |
| PRM-R35 | Empresa que procurou a Save diretamente: venda direta, sem remuneração, salvo registro válido anterior de um parceiro. | [P · DL-01] | Proposta item 8 |
| PRM-R36 | Cauda de mediação: até 6 meses depois de `expirado` ou `encerrado_sem_contrato`, se a mesma raiz virar ganho com outro canal, o sistema abre ficha para o Luis com a evidência do parceiro anterior (o direito pode existir se o negócio for "fruto da mediação"). Não há remuneração automática. | [P · DL-04] | CC art. 727; `registro-conflito-canal.md` §3 |
| PRM-R37 | Legado: os conflitos abertos antes da vigência (82 raízes, 19 de severidade alta, 3 Master × Master em 26/10/2026) não passam pela regra nova; entram como fila herdada para decisão caso a caso do Luis antes do piloto. | [A] não retroage · [P · DL-01] fila | R14; proposta item 9 |
| PRM-R38 | Validade fica pausada enquanto o registro estiver `em_conflito`; o tempo pausado é devolvido a quem vencer. | [P · DL-01] | — |
| PRM-R39 | Empresa no Simples Nacional, com CNPJ ativo: registro aceito; a Daniela recebe a ressalva do `crm_checagem.py` (olhar passivo e reforma, não PIS/COFINS não cumulativo). CNPJ baixado, inapto ou nulo: recusa com o motivo 2. | [O] | `higiene-crm-registro.md` |
| PRM-R40 | Interesse marcado como "Outro tema (em descoberta)": o registro protege a raiz como qualquer outro; o tema é encaminhado ao dono do produto como descoberta, sem condição ao parceiro; até o G2, 0 h do time no tema (D108). | [A] D83 · [P · D108] horas | D83; D108 |

### 4.5 Subfluxo · lead da BDR oferecido ao Master
| Estado | Entra quando | Quem dispara | Prazo | O que o parceiro vê |
|---|---|---|---|---|
| `oferecido` | A Jenifer distribui o lead a um Master (`lista_master.py`) | jenifer | Aceite em 3 d.u.; reserva interna de 45 dias | `M-15`: "A Área Partners separou uma empresa para você avaliar: {razao_social}. Aceite em até {data_limite_aceite} para seguir com o atendimento." |
| `aceito` | O Master aceita | titular do Master | Vira registro `aprovado` com carimbo = aceite e `origem = bdr` | `M-05` |
| `devolvido` | O Master recusa ou não responde em 3 d.u. | parceiro ou sistema | O lead volta à Jenifer | "Esta empresa voltou para a Área Partners." |

PRM-R41 [A] · Reserva de 45 dias e aceite em 3 d.u. Origem: R17.
PRM-R42 [P · DL-05] · Percentual de remuneração de negócio originado pela BDR da Save: o mesmo do termo do Master até decisão em contrário (campo `registro.origem = bdr` gravado para permitir regra diferente sem migração).

---

## 5. Módulo 2 · Meus negócios

### 5.1 Os 7 estados e o mapa das etapas (RT – Real & Presumido e RT – Simples Nacional)
| Estado ao parceiro (código) | Etapas do HubSpot | Com a bola | Texto exato ao parceiro |
|---|---|---|---|
| Recebido (`recebido`) | Novo Negócio · Em Contato · Agendamento · Contato Futuro | Save | "Recebemos a indicação. A Área Partners organiza o primeiro contato com a empresa." (Contato Futuro acrescenta: "A empresa pediu para retomar a conversa mais adiante.") |
| Em diagnóstico (`em_diagnostico`) | Em Diagnóstico · Autorização Equipe Senior LR | Save | "O time técnico está analisando os documentos da empresa. Avisaremos aqui quando houver novidade." |
| Precisa de algo de você (`precisa_de_voce`) | Análise com Pendência; ou qualquer etapa aberta com pendência ativa do parceiro (5.2) | Você | "Para seguir, precisamos de: {pendencia}. Se já enviou, avise em Demandas." |
| Apresentação marcada (`apresentacao`) | Apresentação de Diagnóstico | Save e empresa | "A análise foi concluída e o próximo passo é apresentar o resultado à empresa. A Área Partners combina a data com você." |
| Contrato em andamento (`contrato`) | Negociação · Contrato Enviado · Pendência Fechamento · Contrato Assinado | Empresa | "A proposta está com a empresa. Acompanhamos a assinatura do contrato." |
| Em execução (`execucao`) | Negócio Fechado (sem distrato) | Save | "Contrato assinado. O time da Save está executando o trabalho. Os prazos dependem da análise da Receita Federal." |
| Encerrado (`encerrado`) | Negócio Perdido; ou Negócio Fechado com distrato registrado | — | Perdido: "Atendimento encerrado sem contrato." Distrato: "O contrato com a empresa foi encerrado." |

PRM-R43 [O] · O mapa acima é a tabela `mapa_etapas (pipeline, etapa, estado_parceiro)`; a Daniela valida e pode ajustar sem deploy. Outros funis (Gestão de Passivo, Produtos Jurídicos, Produtos Tributários, Planejamento Tributário, Save Partners – BDR/SDR e Closer) entram com mapa próprio antes de aparecer ao parceiro. Etapa sem mapa: o negócio mantém o último estado conhecido (ou `recebido` se nunca teve) e sai alerta "etapa sem mapa" para o Dados.
PRM-R44 [A] · O parceiro vê só dado objetivo: estado, data de entrada no estado, próximo passo e quem está com a bola. Nunca vê valor do crédito, honorário, tese técnica aplicada, parecer, prazo de PER, chance de êxito nem o motivo interno da perda. Origem: D28; R21; desenho §7 item 6. **Alterada em 26/10/2026 pela PRM-R113 (instrução do Luis):** na tela Negócios o parceiro vê os valores e a tese conforme a matriz `negocio.visibilidade_campos`, sempre com a ressalva; continuam proibidos chance de êxito, prazo de PER e o motivo interno da perda (§11A).
PRM-R45 [A] · Ligação negócio ↔ parceiro: `nome_do_parceiro` normalizado pelo roster e pelos aliases (`config-canal.json`, `aliases-parceiros.json`); ligação ao consultor por `email_de_quem_esta_indicando_o_leadcliente` ou pelo alias do nome. Negócio sem ligação segura vai à "fila de vínculo" da Daniela e não aparece a ninguém do lado externo.
PRM-R46 [A] · Clientes sem Master e café não aparecem (D76; R30 vale para métricas; o negócio de café do próprio parceiro aparece normalmente em Meus negócios, mas fora de nível e metas).

### 5.2 Pendência do parceiro (tabela `negocio_pendencia`, nasce no PRM)
| Campo | Regra |
|---|---|
| `tipo` | Lista fechada: documento fiscal; acesso ao e-CAC; procuração; reunião com o decisor; assinatura do cliente; outro (texto curto auditado) |
| `aberta_por` | daniela, jenifer ou geovana |
| `aberta_em`, `resolvida_em`, `resolvida_por` | Trilha |
| Gatilhos automáticos | Etapa "Análise com Pendência"; `e_cac_liberado_` = não por mais de 2 d.u. em "Em Diagnóstico"; demanda ligada ao negócio em `aguardando_parceiro` |

PRM-R47 [O] · Pendência aberta há mais de 7 dias gera alerta à Daniela e o texto `M-16` ao parceiro (uma vez).
PRM-R48 [O] · A pendência fecha quando a dona marca resolvida ou quando a etapa muda para outra que não seja de pendência.

### 5.3 Casos de borda de Meus negócios
1. **Negócio duplicado no HubSpot** (mesma raiz e valor): aparece uma só linha ao parceiro (a mais antiga), e o par vai à lista de saneamento do Dados (D87).
2. **Negócio com outro parceiro na mesma raiz:** cada parceiro vê só o próprio negócio; o par vai ao conflito (PRM-R30).
3. **Negócio reaberto depois de perdido** (volta para etapa aberta): volta ao estado do mapa; o registro, se já `encerrado_sem_contrato`, não reabre; vale novo registro ou a cauda (PRM-R36).
4. **Contato Futuro por mais de 180 dias:** alerta à Daniela para decidir perda ou retomada.

---

## 6. Módulo 3 · Extrato

### 6.1 Máquina de estados da linha de extrato (`extrato_linha.estado`)
| Estado | Entra quando | Quem dispara | Prazo | O que o parceiro vê (texto exato) |
|---|---|---|---|---|
| `previsto` | Negócio ganho com percentual conhecido, sem recebimento | sistema | — | "Contrato assinado. A remuneração nasce de cada recebimento do honorário pela Save. Percentual do seu termo: {pct}%. Ainda sem valor definido." (com DL-09 = sim, mostra também "Base contratada: {valor}" e o selo "estimativa, sujeita a recebimento") |
| `em_conferencia` | Atípico (honorário acima de 50%, café a 70%, percentual do parceiro acima de 100%), duplicidade (I05), percentual de honorário vazio, divergência termo × card acima do incontroverso, ou status Bloqueado na conferência | sistema | Ficha de conferência até 05/12/2026 para o estoque (D102); casos novos em até 30 dias | `M-20`: "Em conferência contratual. Avisaremos aqui quando a conferência terminar." (sem valor e sem data) |
| `recebido_pela_save` | O Financeiro registra o recebimento da parcela do honorário (inclui compensação de ofício) | financeiro | Até o corte do mês | "A Save recebeu uma parcela do honorário desta empresa em {competencia}. A remuneração entra no extrato de {competencia}." |
| `retida_conflito` | A raiz está `em_conflito` | sistema | Até a decisão do Luis | "Linha retida até a conclusão de uma análise da Área Partners." |
| `calculado` (interno) | Rotina de cálculo do mês (5º d.u.) | sistema + Operações de Canal | Revisor confere | Parceiro não vê |
| `liberado` | O Financeiro aprova o extrato (7º d.u.) e a linha passou na elegibilidade (6.5) | financeiro | Publicação até o 8º d.u. | "Remuneração de {competencia}: {valor_bruto}. Emita a nota fiscal de {valor_nf} até o dia {nf_limite} para pagamento no dia {dia_pagamento}." |
| `contestada` | O parceiro contesta dentro de 10 dias corridos da publicação | parceiro | Resposta em 5 d.u. | "Contestação recebida em {data}. Resposta da Save até {data_resposta}." |
| `aguardando_nf` | Liberada, sem NF recebida | sistema | NF até o dia 15 de M+1 entra no ciclo; depois, ciclo seguinte | "Aguardando a sua nota fiscal." |
| `pago` | O Financeiro registra o pagamento | financeiro | — | "Pago em {data_pagamento}. Valor líquido: {valor_liquido} (retenções: {retencoes})." |
| `estornada` | Linha negativa ligada a uma linha paga (6.7) | financeiro | Compensação nos ciclos seguintes | `M-23`: "Ajuste de {valor} referente a {motivo_externo} na empresa {cnpj_mascarado}. Será compensado nos próximos extratos." |
| `cancelada` | Distrato ou perda do contrato antes de qualquer recebimento | sistema | Final | "Contrato encerrado antes de recebimento. Sem remuneração nesta linha." |

**Sequência normal:** `previsto` → `recebido_pela_save` → `calculado` → `liberado` → `aguardando_nf` → `pago`. Com problema: qualquer estado antes de `liberado` → `em_conferencia` ou `retida_conflito`; `liberado` → `contestada` → `liberado` (com ajuste) ou mantém.

PRM-R50 [A] · Nenhuma linha passa de `previsto` sem recebimento registrado pelo Financeiro. Origem: R5; PRM-R14.
PRM-R51 [P · D102] · Liberar o conferido à medida do recebimento; atípico só com contrato conferido; pagar a parte incontroversa e reter só o excedente atípico. Até a D102: linhas atípicas ficam em `em_conferencia`; as linhas OK seguem o fluxo assim que houver recebimento. Origem: D102 (opção A recomendada).
PRM-R52 [A] · Campo vazio do cliente (tese, variante) bloqueia forecast e relatório, **não** o pagamento. Só o percentual de honorário vazio impede o cálculo (sem base não há número), e a linha fica `em_conferencia` até o preenchimento pelo contrato (D109). Origem: R7; D45; D62; D71; D73.

### 6.2 Cálculo (por parcela recebida)
```
base = honorario_recebido_parcela                     # inclui compensação de ofício com Selic (D95)
pct  = termo.percentual_recuperacao                   # família recuperação (D64)
     | config.extrato.pct_produtos_2027 (10)          # família produtos 2027, base = líquido Save recebido (D78, D97)
     | (CI desligado até G2)                          # D61, R3
pct_incontroverso = min(pct_termo, pct_card) se ambos existirem e divergirem; senão pct_termo
valor_bruto_linha = arredonda_centavo(base × pct_incontroverso / 100)     # meia para cima, por linha
excedente = base × (pct_termo − pct_incontroverso) / 100 → linha separada em_conferencia
```
- PRM-R53 [A] · Família recuperação usa o percentual do termo do parceiro, nunca o do card. Origem: D64; R1.
- PRM-R54 [A] · Família produtos 2027 usa 10% do líquido Save (valor do contrato × % do honorário, apurado sobre o recebido). Exemplo de leitura: contrato de R$ 1.000.000 com honorário de 20% dá líquido Save de R$ 200.000 e remuneração do parceiro de R$ 20.000 ao longo dos recebimentos. Dedução de tributos antes dos 10%: [P · OC-1], padrão `nenhuma`. Origem: D78; D97.
- PRM-R55 [A] · Save Invest: quem paga o parceiro é sempre a Save, nunca a financiadora. Origem: D96; D97; R4.
- PRM-R56 [P · DL-07] · Base da recuperação: honorário recebido sem dedução de tributos da Save (padrão), até o Financeiro e o Luis decidirem bruto × líquido (OC-4).
- PRM-R57 [A] · Cada família fica numa seção própria do extrato (base diferente). Origem: `extrato-prestacao-contas.md`.
- PRM-R58 [A] · Conciliação: soma do detalhe = resumo; acumulado anterior + mês = acumulado novo; diferença acima de R$ 0,01 bloqueia a publicação. Origem: idem §5.
- PRM-R59 [A] · O extrato não mostra comissões internas (vendedor, gestor comercial, coordenador, indicador interno) nem margem da Save. Origem: R12.
- PRM-R60 [O] · Divergência entre o percentual do termo e o do card gera alerta "Revisar" para Contratos e Daniela; não bloqueia a parte incontroversa (PRM-R51).
- PRM-R61 [P · D65] · Exceção de honorário (ex.: café a 70%) só é paga se estiver no registro único de exceções, aprovada pelo Luis e com anexo de remuneração assinado; erro de campo corrige-se pelo contrato; sem lastro, fica retido. Origem: D65 (opção A recomendada).
- PRM-R62 [P · D109] · Percentual de honorário vazio é preenchido por Financeiro e Contratos a partir do contrato assinado, com registro de quem preencheu e quando; contrato com percentual por componente, aditivo ou honorário acima de 50% sobe como atípico. Origem: D109 (ordem da opção B recomendada).

### 6.3 Retenções (sobre a NF do parceiro PJ)
| Item | Regra no código | Marca |
|---|---|---|
| IRRF | 1,5% sobre o valor da NF (mediação, RIR/2018 art. 718; serviço profissional, art. 714, também 1,5%); dispensado para optante do Simples com declaração | [P · Tributário] |
| CSRF | 4,65% só se o código de serviço da NF estiver na lista do art. 30 da Lei 10.833; dispensa até R$ 10,00 (art. 31 §3º); dispensa para Simples com declaração | [P · Tributário] |
| ISS | Só se a lei do município atribuir a retenção ao tomador; alíquota de 2% a 5% conforme o item da NF (10.09, 10.02 ou 17.01) | [P · Tributário] |
| 2027 (CBS e IBS) | `retencao.regra_2027 = a_validar`: a partir de 01/01/2027 o cálculo de retenção fica bloqueado até o Tributário validar | [P · Tributário] |
| Item "a validar" | Mostrado ao parceiro como "retenção conforme a nota fiscal, em validação"; nunca ganha número final sem validação | [A] método |

Origem: `elegibilidade-retencoes.md`; R10; OC-7 a OC-10.

### 6.4 Calendário mensal
| Quando | Etapa | Dono | Marca |
|---|---|---|---|
| Último dia de M | Corte dos recebimentos | Financeiro | [P · OC-18] |
| Até o 5º d.u. de M+1 | Cálculo por script (`conferencia_repasses.py`) e conferência por 2ª pessoa | Operações de Canal + Revisor | [P · OC-18] |
| Até o 7º d.u. | Aprovação do extrato | Financeiro (percentual segue com o Luis) | [A] alçada D98 · [P · OC-18] data |
| Até o 8º d.u. | Publicação ao parceiro | sistema (Fase 2) ou Daniela (Fase 1) | [P · OC-18] |
| Publicação + 10 dias corridos | Janela de contestação | parceiro | [P · OC-18] |
| Até o dia 15 de M+1 | NF do parceiro recebida para o ciclo | parceiro | [P · OC-18] |
| Até o dia 20 de M+1 (ou 1º d.u. seguinte) | Pagamento da parte não contestada, contra NF | Financeiro | [P · OC-18; DL-15] |

O OC-18 vale pela recomendação em 28/10/2026 se o Financeiro não responder (alçada do Financeiro; o Luis pode reverter).

### 6.5 Elegibilidade para pagamento (checklist por parceiro e por lote)
1. Termo vigente assinado (ou percentual informado pelo Luis com selo "termo a localizar" até o inventário da D65).
2. CNPJ do parceiro ativo na Receita.
3. CNAE compatível com intermediação, representação ou consultoria.
4. Regime tributário confirmado.
5. NF com o código de serviço esperado e valor bruto igual ao extrato.
6. Linha sem conflito aberto.
7. Linha fora de `em_conferencia`.

PRM-R63 [P · proposta de 29/09 item 6] · Falhou o item 2 ou o 5: a linha fica `aguardando_nf` (NF divergente volta ao parceiro com `M-24`). Falhou o 1: segue com selo enquanto durar o inventário da D65 (não retém pagamento já conferido, PRM-R52). Falhou o 6 ou o 7: só aquela linha fica retida.
PRM-R64 [P · DL-17] · Parceiro só PJ. Pessoa física e MEI não recebem pelo PRM até decisão (risco previdenciário, de vínculo e de ocupação não permitida ao MEI).

### 6.6 Contestação
| Estado (`contestacao.estado`) | Entra quando | Dono | Prazo | Parceiro vê |
|---|---|---|---|---|
| `aberta` | Parceiro contesta uma linha dentro da janela | parceiro | — | `M-21` |
| `em_analise` | Triagem pelo tipo: cálculo → Operações de Canal; percentual → Luis; retenção → Tributário; conflito → Registro; recebimento → Financeiro | sistema | Resposta em 5 d.u. | Igual a `M-21` |
| `procedente` | Dono confirma o erro | dono do tipo | Ajuste no ciclo seguinte | `M-22` (procedente) |
| `improcedente` | Dono mantém, com explicação | dono do tipo | Final; o parceiro pode reabrir 1 vez com fato novo em 10 dias | `M-22` (improcedente) |

PRM-R65 [A] · A contestação não segura a parte incontroversa: o resto do extrato segue para pagamento. Origem: proposta Parte 2 item 4.
PRM-R66 [A] · Toda contestação recebe causa-raiz codificada (cadastro, percentual, duplicidade, recebimento, retenção, conflito) e correção na fonte. Procedente acima de R$ 5 mil exige aprovação humana do Financeiro; procedente acima de 10% do valor do mês dispara análise de causa-raiz. Origem: `extrato-prestacao-contas.md`.
PRM-R67 [O] · Contestação fora da janela vira demanda do tipo REP-COMISSAO, sem efeito no ciclo em curso.

### 6.7 Estorno e compensação (clawback)
PRM-R68 [P · DL-08] · Se a Save devolver honorário ao cliente (distrato com devolução, glosa com restituição, pagamento em duplicidade, cancelamento), a remuneração correspondente vira linha `estornada` (negativa), ligada à linha paga de origem.
PRM-R69 [P · DL-08] · A compensação desconta no máximo 50% do bruto de cada ciclo seguinte, por até 24 meses; saldo não compensado nesse prazo vai a Contratos e Financeiro para tratamento conforme o termo. Nunca se compensa contra linha `em_conferencia`.
PRM-R70 [P · DL-08] · O estorno só vale para quem tem cláusula de estorno no termo (`termos-parceria-checklist.md`); sem cláusula, o caso vai a Contratos e Jurídico antes de qualquer lançamento.

### 6.8 Casos de borda do extrato
| Caso | Regra | Marca |
|---|---|---|
| **Honorário parcial** (cliente paga em parcelas ou só parte) | Uma linha por parcela recebida; o acumulado mostra "recebido até agora" sem projetar o restante | [A] R5 |
| **Compensação de ofício** pela Receita | Conta como recebimento do honorário com Selic, na data em que o Financeiro registrar | [A] D95 |
| **Distrato do cliente antes de qualquer recebimento** | Linhas `previsto` → `cancelada` | [A] R5 |
| **Distrato do cliente com parcelas já recebidas** | Linhas pagas ficam; parcelas futuras canceladas; estorno só se houver devolução de honorário (6.7) | [P · DL-08] |
| **Duplicidade** (I05) | Linhas do grupo vão a `em_conferencia` até o saneamento; nenhuma é paga em dobro | [A] D102 contexto |
| **Percentual acima de 100% ou "125"** | `em_conferencia`; pagamento só do incontroverso conforme o termo | [A] D102 |
| **Conflito decidido com divisão** | Linhas recalculadas com os percentuais da decisão; diferença paga a mais vira estorno | [A] PRM-R32 |
| **Troca de parceiro no meio do contrato** | Ver seção 12, caso 6 | [P · DL-06] |
| **Termo do parceiro encerrado** | Ver seção 12, caso 8 | [P · DL-15] |
| **Atraso no pagamento pela Save** | Linha mostra "pagamento em processamento"; se o vínculo for lido como representação, há correção monetária (Lei 4.886 art. 32 §2º) | [P · DL-15] |

---

## 7. Módulo 4 · Demandas

### 7.1 Tipos ao parceiro e códigos internos
| Tipo na tela | Código (`sla.json`) | 1ª resposta / solução (d.u.) | Dono |
|---|---|---|---|
| Status de um negócio | COM-STATUS | 0 / 1 | Daniela |
| Documento | TEC-DOCUMENTOS | 0 / 2 | Técnico |
| Parecer ou dúvida técnica | TEC-DUVIDA (ou TEC-REANALISE se o negócio estiver Encerrado) | 0 / 3 (1 / 5) | Geovana |
| Reunião | COM-REUNIAO (JUR-REUNIAO se o parceiro marcar "precisa de apoio jurídico") | 0 / 2 | Daniela (+ Geovana) |
| Contrato | CTR-ENVIO, JUR-CONTRATO ou CTR-DISTRATO (subtipo) | 0 / 2 a 1 / 5 | Contratos |
| Material | MKT-MATERIAL (existe) ou MKT-NOVO | 0 / 1 ou 1 / 10 | Daniela ou Marketing |
| Remuneração | REP-COMISSAO | 0 / 5 | Financeiro / Operações de Canal |
| Notificação da Receita recebida pela empresa | JUR-NOTIFICACAO (urgente) | mesmo dia / prazo legal | Jurídico |
| Reclamação | QLD-RECLAMACAO (urgente) | 0 / 3 | Daniela com Qualidade, aviso ao Luis |
| Outro | OUT-OUTROS | 1 / 5 | Daniela classifica |

PRM-R71 [P · Semana 0] · Os prazos de `sla.json` são proposta não validada com as áreas. Enquanto um tipo não tiver `validado = true`, o parceiro vê só a 1ª resposta ("Retorno com a previsão em até {primeira_resposta} dia útil") e não a previsão de solução. Origem: `sla.json` (_status); `triagem-sla.md` ("SLA não validado com a área é desejo").

### 7.2 Máquina de estados da demanda
| Estado | Entra quando | Quem dispara | Prazo | Parceiro vê (texto exato) |
|---|---|---|---|---|
| `aberta` | Parceiro envia (ID `D-AAAA-NNNN`, `lib/registro_demandas.py`) | parceiro ou daniela | 1ª resposta conforme o tipo | `M-30`: "Pedido {id} recebido. Tipo: {tipo}. Retorno com a previsão em até {primeira_resposta}." |
| `triada` | Tipo confirmado, dados mínimos conferidos, histórico consultado (`lib/historico.py avaliar`) | sistema + daniela | — | Igual a `M-30` |
| `aguardando_parceiro` | Faltam dados mínimos | daniela | Relógio do SLA para; prazo legal não para | `M-31`: "Para seguir com o pedido {id}, precisamos de: {itens}." |
| `resposta_historico` | O histórico tem resposta; rascunho pronto | sistema | Daniela confere e envia dentro do SLA | Parceiro não vê o rascunho |
| `encaminhada_area` | Precisa de área; chamado sugerido "Aprovar e abrir no GLPI" aprovado pela Daniela (abertura manual até a liberação do GLPI) | daniela | Solução conforme o tipo; escala 1, 3 e 5 d.u. | `M-32`: "Pedido {id} encaminhado à área {area}. Previsão de retorno: {data}." (sem previsão se o tipo não for validado) |
| `respondida` | A dona envia a resposta | daniela (ou dona do tipo) | — | A resposta, com o selo "Respondido pelo histórico" ou "Respondido pela área {area}" |
| `concluida` | Parceiro marca "Resolvido" ou 5 d.u. sem reação | parceiro ou sistema | Final, com reabertura em 7 dias | "Pedido {id} concluído. Se precisar, reabra em até 7 dias." |
| `reaberta` | Parceiro reabre em até 7 dias | parceiro | Volta a `triada`, mesmo número | "Pedido {id} reaberto." |
| `atrasada` (flag) | Prazo vencido | sistema | Escala: 1 d.u. → responsável da área; 3 → gestor; 5 → Luis | `M-33`: "O pedido {id} está levando mais tempo que o previsto. Já cobramos a área e avisaremos aqui." |

PRM-R72 [A] · Fluxo único: histórico antes do chamado; o agente rascunha, a pessoa envia; o chamado é aprovado pela Daniela (Luis só se tocar regra, preço, conflito ou produto em validação). Origem: D29; D98; `infra/fluxo-unico.md`.
PRM-R73 [A] · Resposta automática (sem conferência) só no degrau 2 da D28: tipo de dado objetivo com 20+ casos em 2 semanas e 95%+ de acerto, depois de o Luis ver os números; valor, prazo de êxito, tese e cobrança ficam sempre com pessoa. Até lá, todo `resposta_historico` passa pela Daniela. Origem: D28; SESSOES §22 (30 dias com amostra de 20%).
PRM-R74 [A] · Demanda pelo portal e demanda pelo WhatsApp entram no mesmo registro (`registro/demandas.json`, campo `canal`), com o mesmo ID e o mesmo SLA. Origem: desenho §5 (riscos).
PRM-R75 [A] · Texto da demanda passa por `lib/protecao.py`; CPF, RG, CNH e dados bancários bloqueiam o envio (`M-90`). Origem: R24.
PRM-R76 [P · DL-13] · Anexo de documento fiscal do cliente pelo portal fica desligado até o parecer de LGPD e segurança; até lá, `M-34` orienta o canal atual de documentos.
PRM-R77 [A] · Reclamação vai à Daniela com o `depto-qualidade` e aviso ao Luis; o Luis decide só exposição pública ou saída de Master Estratégico. Origem: D98.

---

## 8. Módulo 5 · Nível e jornada

### 8.1 Jornada do parceiro (estado do parceiro, `parceiro.etapa_jornada`)
| Estado | Entra quando | Sai quando | Dono | Parceiro vê |
|---|---|---|---|---|
| `recrutado` | Aceita conversar (célula Jenifer) | Assina o termo | Jenifer | Sem acesso ao portal |
| `registrado` (D0) | Termo assinado + Master padrinho + data de entrada | N1 concluído e 1º registro | Jenifer + padrinho | "Bem-vindo ao Programa Partners. Seu primeiro passo é a trilha N1 da Academia." |
| `certificado` | N1 + ≥ 1 ganho em 12 meses + ativo | N2 + ≥ 5 ganhos | Jenifer | "Você concluiu a trilha N1 e já tem um contrato assinado a partir da sua indicação." |
| `pleno` | N2 + ≥ 5 ganhos + conversão ≥ 20% | Decisão do Luis (território sem conflito de canal) | Luis | "Você cumpriu os critérios para ser avaliado como Master. A Área Partners conversa com você sobre os próximos passos." |
| `master` (com faixa Master, Avançado, Estratégico) | Roster dos 9 ou decisão do Luis | Apuração trimestral | Daniela | Ver 8.2 |
| `observacao` (situação, não nível) | Não sustenta a permanência na apuração | Retoma em até 2 trimestres ou ajusta 1 faixa | Daniela | `M-41` (carta individual) |
| `dormente` (situação) | Ganho em 12 meses e nenhum negócio novo em 90 dias | Novo registro aprovado | Daniela (Master) ou Jenifer (indicador) | Nada automático; contato de reativação por pessoa (`M-52`) |
| `inativo` (situação) | Mais de 12 meses sem negócio | Sinal novo | — | Nada |

Origem: `gestor-niveis-jornada.md` §2; `coach-onboarding-enablement.md` §5.
PRM-R80 [O] · Passagem de indicador a Master só por decisão do Luis, registrada; o sistema só sinaliza "candidato" (`pleno`).

### 8.2 Faixas do Programa Partners 2027 (apuração trimestral)
| Estado da apuração | Regra | Quem dispara |
|---|---|---|
| `apurado` | Rotina trimestral calcula volume ativo (líquido Save de 12 meses, todos os produtos, sem café, com limite por negócio) e trimestres acima do patamar | sistema (`metricas_ps.py`) |
| `proposta_nivel` | Lista "nível de partida × leitura do trimestre × o que falta" vai ao Luis | sistema → luis |
| `aprovado` | Luis aprova; carta individual em rascunho passa pelo auditor | luis |
| `comunicado` | Carta enviada por pessoa (Daniela) | daniela |

| ID | Regra | Marca | Origem |
|---|---|---|---|
| PRM-R81 | Modo `sombra`: o sistema apura e mostra só à Save. O parceiro não vê faixa, barra nem patamar até a F8 ser decidida e a carta individual ser enviada. Na tela externa aparece só a jornada (8.1). | [P · F8] | F8; desenho M6 |
| PRM-R82 | Ninguém começa abaixo do nível de partida (v1 de 29/09); só sobe nas 4 primeiras apurações; ajuste de 1 faixa por vez; observação de 2 trimestres antes de qualquer ajuste. | [P · F8 (L2, L6 opção 2)] | R28; F8 |
| PRM-R83 | Em 2027, faixa dá só benefícios não financeiros (opção A); o nível não muda o percentual de remuneração, o honorário do cliente nem a fila técnica. | [P · F8 (L10)] · [A] honorário (D79) e fila técnica (L4) | D79; F8 |
| PRM-R84 | Barra de progresso (quando liberada) em percentual do patamar, sem valor em R$, para não expor o líquido da Save. | [P · DL-10] | R12 |
| PRM-R85 | Patamares em R$ são recalibrados quando a meta 2027 da diretoria sair. | [P · D75] | D75 |
| PRM-R86 | Benefícios por faixa (lista para a matriz): validade de registro de 120 dias (se DL-02), plano de conta e QBR, listas de contas da BDR (≥ 60% para Masters fora dos 3 maiores, P37), co-venda nas primeiras indicações dos consultores novos, convite ao Conselho de Parceiros. | [P · F8] | `gestor-niveis-jornada.md`; P37 |
| PRM-R87 | Sem ranking, sem comparação entre parceiros, carta só individual. | [A] | R27 |

---

## 9. Módulo 6 · Biblioteca e Academia

### 9.1 Estado do produto no catálogo (`produto.estado_vitrine`)
| Estado | Produtos (26/10/2026) | O que o parceiro vê |
|---|---|---|
| `pronto` | Recuperação T01–T17 (sem T13 e T16), recorrência, Gestão de Passivo, produtos jurídicos, planejamento e reforma, estruturação patrimonial, Gestão de Contas, antecipação e FIDC (Save Invest), tax internacional | Kit completo: o que é, para quem serve, perguntas de qualificação, o que não dizer, peça aprovada |
| `descoberta` | Crédito Internacional, Maquila, captação de capital, home equity, turnkey | Nome e "Em descoberta: se a empresa tiver interesse, registre e a Área Partners conversa com ela." Sem taxa, condição, simulação nem peça |
| `fora_vitrine` | T13 (vira triagem de passivo), T16; Funrural em conciliação | Nada |

Origem: R19; R20; R23; D80; D83; D92; CLAUDE.md §3.

### 9.2 Máquina de estados do material (`material.estado`)
| Estado | Entra quando | Quem dispara | Saída |
|---|---|---|---|
| `rascunho` | Marketing ou área cria | marketing | `em_validacao` |
| `em_validacao` | Pede validação técnica (Tributário ou dono do produto) e jurídica quando tocar remuneração, perímetro ou advocacia | marketing | `auditado` ou volta a `rascunho` |
| `auditado` | `auditar_texto.py` com 0 ALTO e 0 MÉDIO | sistema | `aprovado` |
| `aprovado` | Daniela (curadora) aprova; material em escala: o Luis vê um exemplo antes | daniela; luis (exemplo) | `publicado` |
| `publicado` | Visível ao parceiro conforme o estado do produto e a trilha exigida | sistema | `em_revisao` por gatilho; `suspenso` |
| `em_revisao` | Gatilho: norma nova no radar, decisão nova da Save (D que mude via ou vitrine) ou 12 meses | sistema | `publicado` ou `arquivado` |
| `suspenso` | Achado de promessa, erro técnico ou produto saiu da vitrine | qualquer interno | `em_revisao` |
| `arquivado` | Final | daniela | — |

| ID | Regra | Marca | Origem |
|---|---|---|---|
| PRM-R90 | Nenhum material é publicado sem passar por `auditado`. | [A] | R21 |
| PRM-R91 | Peça co-branded traz o selo de parceiro remunerado ("Parceiro indicador remunerado pela Save"), com texto validado pelo Jurídico. | [P · DL-14] | R29 (guia do CONAR de 12/05/2026) |
| PRM-R92 | Na v1 o parceiro baixa a peça; não dispara campanha pelo portal. | [A] | Desenho §5 (o que não faremos) |
| PRM-R93 | Case de cliente só com autorização escrita e aprovação de Marketing e Jurídico; hoje nenhum case está aprovado, então a seção de cases fica oculta. | [A] | SESSOES §22 (23/10); Provimento CFOAB 205/2021 art. 6º |
| PRM-R94 | Antecipação sobre venda gerencial e escrow não têm material escrito; só tratamento presencial pela Save Invest. | [A] | D82 |
| PRM-R95 | Material que toca serviço jurídico é do escritório e não é distribuído como peça conjunta pelo contador. | [A] | `perimetro-regulatorio.md` (Lei 8.906 art. 34, IV) |

### 9.3 Academia
| Estado da trilha do usuário (`academia_progresso.estado`) | Regra |
|---|---|
| `nao_iniciada` → `em_andamento` → `concluida` | Concluída = todos os módulos vistos e quiz com nota ≥ 80%, com 100% nas questões do módulo 7 ("o que não prometer") |
| `concluida` → `vencida` | 12 meses ou gatilho normativo (módulo alterado reabre o quiz) |

PRM-R96 [O] · N1 (cerca de 2 h) até D+30 do onboarding; módulos com `[VALIDAR TÉCNICO]` não aparecem ao parceiro até a validação (curadoria: Daniela e Geovana; vale a recomendação desde 28/10).
PRM-R97 [P · DL-18] · Certificação como porta: N2 específica exigida para registrar interesse em Gestão de Passivo e em estruturação patrimonial. Até a Academia ter esses módulos validados, a porta fica desligada (`academia.porta_ativa = false`) e o registro segue livre.
PRM-R98 [A] · Certificação não é degrau geral de nível. Origem: desenho §5.

---

## 10. Módulo 7 · Onboarding do parceiro

### 10.1 Máquina de estados (`onboarding.estado`)
| Estado | Entra quando | Quem dispara | Prazo | Parceiro vê |
|---|---|---|---|---|
| `convidado` | Jenifer convida (modelo M8 da célula) | jenifer | — | Sem acesso |
| `termo_em_assinatura` | Contratos envia o termo (assinatura eletrônica) | contratos | 15 dias; depois volta a `convidado` | Sem acesso |
| `ativo_d0` | Termo assinado + Master padrinho definido + data de entrada gravada; usuário titular convidado e Termos de Uso aceitos | contratos + daniela + jenifer | — | `M-50` (boas-vindas) |
| `rampa_d30` | D+1 a D+30: N1, mapa de 20 clientes, ≥ 3 registros | sistema | Check-in de 20 min em D+30 | Lista de marcos com ✔ e o que falta |
| `rampa_d60` | D+31 a D+60: ≥ 1 diagnóstico com e-CAC liberado; co-venda na 1ª reunião | sistema | Check-in em D+60 | Idem |
| `rampa_d90` | D+61 a D+90: 1ª apresentação; ≥ 5 registros; co-venda na 2ª indicação | sistema | Check-in de graduação em D+90 | Idem |
| `graduado` | Marcos de D+90 cumpridos | jenifer | — | `M-51` |
| `reforco_30` | Marcos não cumpridos com sinal de avanço | jenifer | 30 dias | "Combinamos mais 30 dias de apoio." |
| `pausado` | Sem sinal de avanço | jenifer | Reavaliação em 90 dias | Nada automático |
| `encerrado` | Termo encerrado | contratos | Final | `M-12` nos registros vivos |

| ID | Regra | Marca | Origem |
|---|---|---|---|
| PRM-R100 | Sem termo assinado, Master padrinho e data de entrada não há plano nem acesso ao portal. | [A] | `coach-onboarding-enablement.md` §5 |
| PRM-R101 | Alertas internos: nenhum registro até D+21; N1 pendente em D+30; nenhum diagnóstico até D+60; 45 dias sem negócio novo depois de D+90. | [O] | Idem |
| PRM-R102 | Co-venda obrigatória na 1ª e na 2ª indicação: o parceiro abre a porta e consegue o decisor e os documentos; a Save conduz a parte técnica; ninguém fala de valor, prazo ou êxito. | [O] | Idem §2 |
| PRM-R103 | Os marcos são metas internas de acompanhamento, não obrigação contratual do parceiro, sem meta imposta nem exclusividade (para não caracterizar representação). | [A] | Lei 4.886 art. 1º; `coach-onboarding-enablement.md` §3 |
| PRM-R104 | Master novo: kick-off com Luis e Daniela em D0–D15; 100% dos consultores com N1 até D+30; ≥ 3 diagnósticos apresentados até D+90; 1º QBR em D+90. | [O] | Idem §5 item 8 |
| PRM-R105 | Mapa de carteira só conta clientes que vão para um Master (D76) e fica no escritório do parceiro (o PRM guarda só raiz e HMAC dos que viraram registro). | [A] D76 · [P · DL-13] guarda | D76; LGPD |
| PRM-R106 | Indicador disputado por dois Masters como padrinho é conflito de canal e vai ao Luis. | [A] | `coach-onboarding-enablement.md` §4 |

### 10.2 Acesso ao portal (ciclo de vida do usuário)
| Estado (`usuario_parceiro.estado`) | Regra |
|---|---|
| `convidado` | Convite B2B só após `ativo_d0` (titular) ou pedido do titular aprovado pela Daniela (consultor) |
| `ativo` | Aceitou os Termos de Uso (versão gravada) e configurou MFA por aplicativo |
| `suspenso` | Uso fora dos Termos (varredura, compartilhamento de acesso, promessa a cliente), por decisão da Daniela com aviso ao Luis |
| `desativado` | Saída do escritório (pedido do titular) ou fim do termo; acesso cai no mesmo dia |
| `ex_parceiro_extrato` | Fim do termo com linhas ainda a receber: acesso só ao Extrato e a demandas de remuneração até a última linha paga [P · DL-15] |

PRM-R107 [A] · Mudança de versão dos Termos de Uso exige novo aceite no próximo acesso.

---

## 11. Módulo 8 · Visão do canal (só Save)

### 11.1 Indicadores e alertas
| Indicador | Fonte | Limite de alerta | Dono do alerta |
|---|---|---|---|
| Saúde por parceiro (0–100) | `dados_bi.py` | < 50 | Daniela |
| Consultores dormentes | `pacote-*.json` | ganho em 12 m e 90 dias sem negócio | Daniela |
| Concentração top 1 e top 5 (fechado 12 m) | `pacote-*.json` | métrica de guarda, sem meta | Luis |
| Registros a vencer | `registro_oportunidade` | ≤ 15 dias | Daniela |
| Registros sem card no HubSpot | idem | > 3 d.u. após aprovação | Daniela |
| Conflitos abertos por severidade | `conflito` + `conflito_canal.py` | Alta > 0; fora do SLA de 10 d.u. | Luis |
| Respostas neutras por usuário | trilha | ≥ teto diário | Daniela (possível varredura) |
| Extratos a liberar e linhas em conferência | `extrato_linha` | linha em conferência > 30 dias | Financeiro |
| Contestações abertas | `contestacao` | > 5 d.u. | Financeiro |
| Demandas fora do SLA | `demanda` | escala 1, 3, 5 d.u. | Daniela |
| "Precisa de algo de você" | `negocio_pendencia` | > 7 dias | Daniela |
| Adoção do portal | `acesso_log` | % de demandas pelo portal | Luis (pacote semanal) |
| Etapas sem mapa | `mapa_etapas` | > 0 | Dados |

### 11.2 Estado do alerta
`aberto` → `com_dono` (atribuído) → `resolvido` ou `risco_aceito` (com justificativa; só Luis ou a dona dentro da alçada).

| ID | Regra | Marca | Origem |
|---|---|---|---|
| PRM-R110 | Nenhuma informação desta tela vai ao lado externo. | [A] | R12 |
| PRM-R111 | Margem e comissões internas só aparecem aos perfis `luis` e `financeiro`. | [A] | R12; D100 (perfis do painel) |
| PRM-R112 | Clientes sem Master e café ficam fora dos indicadores. | [A] | D76; R30 |

---

## 11A. Acompanhamento de negócios e dashboards de vendas (Luis, 26/10/2026)

Pedido do Luis: "Quero que o parceiro tenha visão dos negócios em andamento, e todas as informações que constam nela. Quero também que construa dashboards como um CRM de vendas." Decisão do Luis na mesma conversa: o parceiro vê os valores, o que supera a recomendação da DL-09 (decisão 6) **nesta tela**. O parâmetro `extrato.mostra_valor_previsto` do extrato continua como está até o Luis mudar.

| ID | Regra | Marca | Origem |
|---|---|---|---|
| PRM-R113 | **Visibilidade de valores.** O parceiro vê, nos negócios do seu escopo, os campos do card do HubSpot listados na matriz `negocio.visibilidade_campos` (padrão: todos). Todo valor de crédito sai com o rótulo "Estimativa do diagnóstico · sujeita à análise e homologação da Receita; não é valor garantido." A remuneração estimada do escritório sai como "Previsto", com a mesma ressalva, e só ao titular (como o extrato, PRM-R15). Nunca há chance de êxito, probabilidade nem prazo de restituição. | [A] | Instrução do Luis, 26/10/2026 |
| PRM-R114 | Campos travados nunca vão ao parceiro, mesmo que a matriz diga sim: notas internas da Save, motivo interno da perda, motivo de conflito, dados de outro parceiro, probabilidade e forecast do CRM, comissões internas (R111) e dado pessoal de sócio do cliente. Campo fora da matriz também não sai (falha fechada). | [A] | R12; R21; LGPD art. 6º III |
| PRM-R115 | Texto livre do CRM (próximo passo combinado) só vai ao parceiro depois do auditor de promessas e do bloqueio de dado pessoal; reprovado, o campo some da ficha e o parceiro vê o próximo passo padrão do estado. | [A] | 02 §17 |
| PRM-R116 | Os agregados (pipeline, funil, aging, conversão, ciclo, forecast) são calculados no servidor. O parceiro recebe só os do próprio escopo (titular: escritório; consultor: os dele); nunca comparação ou ranking com outro parceiro (R27). | [A] | R27; 04 §2.1 |
| PRM-R117 | O dashboard comercial é só da Save (`ver_canal_agregado`); a lista de drill-down exige `ver_negocios`. Café e negócio sem Master ficam fora (R112). Master aparece em ordem alfabética, nunca como ranking. | [A] | R110, R112 |
| PRM-R118 | Taxa com base pequena (menos de `painel.base_pequena` encerrados; 20 por grupo na conversão registrado × não registrado) aparece como "base pequena", sem número. | [A] | 03 §5 |

**Definições usadas nos dashboards.** Pipeline = negócios abertos por estado, com o crédito estimado (`amount`). Funil = coorte dos negócios que entraram no período e a etapa mais alta a que chegaram (histórico de etapas + estado atual; ganho = contrato assinado). Conversão (win rate) = ganhos ÷ (ganhos + perdidos) com fechamento no período. Ciclo = dias da entrada ao contrato, nos ganhos do período (média e mediana). Aging = dias na etapa atual, em quatro faixas (até 15, 16–30, 31–60, mais de 60); parado = mais de `negocio.parado_dias`. Comparação = mesmo indicador no período anterior de mesmo tamanho. Forecast (só Save) = ganhos do mês + abertos com data de assinatura prevista no mês, sem ponderar por probabilidade, contra a meta D111. Remuneração prevista = crédito × honorário do contrato × percentual do termo, nos ganhos sem recebimento; recebida e paga vêm do extrato.

## 12. Casos de borda transversais

| # | Caso | Regra no sistema | Marca | Origem |
|---|---|---|---|---|
| 1 | **Conflito Master × Master** (dois Masters registram ou têm negócio na mesma raiz) | Registro do segundo vai a `em_conflito`; validade pausada; ficha de fatos ao Luis (PRM-R30); nenhum parceiro é avisado do outro; decisão gravada; quem perde recebe `M-11` (motivo 4); quem ganha recebe `M-05`; divisão só como exceção, sem duas remunerações integrais. Os 3 casos herdados ficam na fila de legado (PRM-R37) | [A] alçada · [P · DL-01] desempate | D98; R15; proposta item 7 |
| 2 | **Registro que expira** | Rotina diária: prorroga se houver critério; senão `expirado` e `M-09`; a raiz fica livre; durante 6 meses, ganho de outro canal abre ficha de cauda (PRM-R36) | [P · DL-02, DL-04] | Proposta item 4; CC art. 727 |
| 3 | **Empresa que já é cliente da Save** (negócio aberto ou ganho, de venda direta ou de outra área) | Mesmo texto `M-01`; recusa com motivo 4; nunca revelar que é cliente; parceiro com evidência anterior pode contestar (PRM-R24) | [A] neutro · [P · DL-03] contestação | R25; decisão de 23/10 |
| 4 | **Empresa cliente do próprio parceiro com negócio antigo ganho** (nova tese) | `proprio_usuario` ou `proprio_escritorio`: mostra o registro ou a proteção vigente (`M-03a/b`); a tese nova entra como demanda ligada ao negócio | [A] | — |
| 5 | **Índice indisponível** | Falha fechada: `M-01`, sem chamada externa; a Daniela confere à mão quando o índice voltar | [A] | `central/README.md` |
| 6 | **Troca de parceiro** a pedido da empresa cliente | Decisão do Luis. Proposta: o parceiro original mantém a remuneração dos recebimentos de contratos assinados com ele até o fim desses contratos; o novo parceiro só em contratos novos, assinados depois da decisão; nada retroage | [P · DL-06] | CC art. 727; PRM-R07 |
| 7 | **Consultor muda de escritório** | Registros e negócios ficam com o escritório de origem (`parceiro_id`); o consultor perde o acesso no mesmo dia; no novo escritório, só registros novos | [O] | PRM-R17 |
| 8 | **Distrato do parceiro** (fim do termo) | Registros vivos → `encerrado_fim_parceria` (`M-12`); negócios abertos seguem com a Save sem parceiro; remuneração sobre recebimentos de contratos assinados durante a vigência segue conforme a cláusula de pós-rescisão do termo; acesso passa a `ex_parceiro_extrato`. Rescisão por descumprimento (promessa a cliente, varredura, uso indevido de dados): suspensão imediata e caso a Contratos e Jurídico | [P · DL-15] | Contratos; Lei 4.886 arts. 27 "j" e 34 (se representação) |
| 9 | **Distrato do cliente** | Negócio → Encerrado ("O contrato com a empresa foi encerrado."); linhas futuras canceladas; estorno só com devolução de honorário (6.7); o parceiro é avisado por pessoa antes de saber pelo cliente (`M-53`) | [A] aviso · [P · DL-08] estorno | `distratos-cobranca.md` |
| 10 | **Honorário parcial** | Linha por parcela; acumulado sem projeção (6.8) | [A] | R5 |
| 11 | **Estorno / clawback** | 6.7 (limite de 50% por ciclo, 24 meses, só com cláusula) | [P · DL-08] | Proposta Parte 2 item 7 |
| 12 | **Indicador sem Master padrinho** | Não entra no PRM até ter padrinho (cliente sem Master é outra área) | [A] | D76 |
| 13 | **Raiz que muda** (incorporação, cisão) | A Daniela liga as raízes na tabela `raiz_vinculo`; registros das duas raízes passam pela checagem como uma só; disputa vai a conflito | [O] | — |
| 14 | **Lead da BDR já registrado por outro parceiro** | `lista_master.py` já exclui raízes com conflito; se escapar, o lead não é oferecido e volta à Jenifer | [A] | R17 |
| 15 | **Varredura** (muitos CNPJs em pouco tempo) | Tetos diários; ao passar, respostas neutras e alerta; reincidência leva a `suspenso` | [O] | `central/README.md`; Termos de Uso 15.4 |
| 16 | **Empresário individual** (nome civil como razão social) | Na tela interna, nome mascarado; ao parceiro, só o que ele mesmo digitou | [P · DL-13] | Minuta de 23/10 item 3 |
| 17 | **Parceiro pessoa física ou MEI** | Não recebe pelo PRM até decisão (PRM-R64) | [P · DL-17] | `elegibilidade-retencoes.md` |
| 18 | **Remuneração de produto em validação** | Sem linha de extrato até o G2 (família desligada) | [A] | R11 |

---

## 13. Notificações e SLAs

**Canais:** aviso na tela (sempre) e e-mail ao usuário (Fase 2, se DL-12). WhatsApp não é automatizado: na Fase 1 a Daniela envia o texto do catálogo. Nenhum envio automático fora das 07h00–20h00 de dias úteis; o que nascer fora disso sai às 07h00 do próximo dia útil.

| Evento | Destinatário | Canal | Quando | Modelo |
|---|---|---|---|---|
| Registro enviado | usuário que registrou | tela | na hora | M-01 |
| Registro já existe (próprio) | usuário | tela | na hora | M-03a / M-03b |
| Esclarecimento pedido | usuário | tela + e-mail | na hora | M-02 |
| Registro aprovado | usuário + titular | tela + e-mail | na decisão | M-05 |
| Registro recusado | usuário + titular | tela + e-mail | na decisão | M-11 |
| Análise demorando (conflito) | usuário | tela | 1 d.u. após o envio | M-04 |
| Negócio aberto | usuário | tela | cópia diária | M-06 |
| Registro a vencer | usuário + titular | tela + e-mail | 15 e 3 dias antes | M-14 |
| Registro prorrogado | usuário | tela + e-mail | na rotina diária | M-07 |
| Registro expirado | usuário + titular | tela + e-mail | na rotina diária | M-09 |
| Contrato assinado (proteção do cliente) | usuário + titular | tela + e-mail | cópia diária | M-08 |
| Negócio mudou de estado | usuário | tela (e-mail só para "Precisa de algo de você" e "Em execução") | cópia diária | texto do estado (5.1) |
| Pendência há mais de 7 dias | usuário + Daniela | tela + e-mail; alerta interno | dia 8 | M-16 |
| Lead da BDR oferecido | titular do Master | tela + e-mail | na oferta | M-15 |
| Extrato publicado | titular | tela + e-mail | 8º d.u. | M-21a |
| Linha em conferência | titular | tela | na mudança | M-20 |
| Contestação recebida / respondida | titular | tela + e-mail | na hora / até 5 d.u. | M-21 / M-22 |
| NF divergente | titular | e-mail (Financeiro) | na conferência | M-24 |
| Pagamento feito | titular | tela + e-mail | no registro do pagamento | M-25 |
| Estorno lançado | titular | e-mail por pessoa (Financeiro) + tela | antes do extrato que desconta | M-23 |
| Demanda recebida / encaminhada / atrasada | quem abriu | tela + e-mail | na hora / na decisão / no vencimento | M-30 / M-32 / M-33 |
| Boas-vindas, D+30, D+60, D+90 | titular | e-mail por pessoa (Jenifer) | marcos | M-50, M-51 |
| Carta de nível | titular | e-mail por pessoa (Daniela) | após aprovação do Luis | M-41 |
| Distrato do cliente | titular | por pessoa (Daniela), antes de qualquer outro aviso | no registro do distrato | M-53 |
| Fim da parceria | titular | por pessoa (Contratos/Daniela) | na data do fim | M-12 |
| Alertas internos | dona do alerta | caixa do painel (`lib/caixa.py`) | conforme 11.1 | — |

**SLAs internos (resumo):** decisão de registro 1 d.u.; conflito 10 d.u. (Luis); card no HubSpot 1 d.u. após aprovação; demandas conforme `sla.json` com escala 1, 3 e 5 d.u.; contestação 5 d.u.; extrato no 8º d.u.; ficha de atípico 30 dias (estoque até 05/12/2026).

---

## 14. Textos-modelo das mensagens (catálogo `M-xx`)

Todos em linguagem do parceiro, sem valor, prazo de êxito ou promessa. Variáveis entre chaves. Mudança de texto é frase permitida e sobe ao Luis (DL-12). Auditados em 26/10/2026 (seção 17).

| Código | Texto |
|---|---|
| M-00 | Não foi possível seguir com esta consulta. Fale com a Área Partners. |
| M-01 | Registro recebido em {carimbo}. A Área Partners confere os dados e responde aqui. |
| M-02 | Precisamos de uma informação para concluir o registro: {pergunta}. Responda até {data_limite} para manter a data e a hora do registro. |
| M-03a | Você já registrou esta empresa em {data}. O registro vale até {valido_ate}. |
| M-03b | Esta empresa já foi registrada pelo seu escritório em {data}, por {nome_consultor}. O registro vale até {valido_ate}. |
| M-04 | A análise deste registro precisa de mais tempo. Avisaremos você aqui. |
| M-05 | Registro aprovado. A empresa fica registrada para você até {valido_ate}. O registro é uma proteção temporária desta oportunidade e não cria exclusividade sobre a empresa. |
| M-06 | Negócio aberto para esta empresa. Acompanhe em Meus negócios. O registro vale até {valido_ate}. |
| M-07 | Registro prorrogado até {prorrogado_ate} porque houve avanço no atendimento desta empresa. |
| M-08 | Contrato assinado com esta empresa a partir da sua indicação. A empresa segue registrada para você enquanto o contrato estiver vigente e por mais 12 meses depois do último recebimento da Save. |
| M-09 | O registro desta empresa terminou em {data} pelo fim do prazo. A empresa pode ser registrada de novo. |
| M-10 | O atendimento desta empresa foi encerrado sem contrato em {data}, e o registro terminou. A empresa pode ser registrada de novo. Se você tiver informação nova sobre ela, abra um pedido em Demandas. |
| M-11 | Não foi possível aceitar este registro. Motivo: {motivo_externo}. Se quiser conversar sobre o caso, abra um pedido em Demandas. |
| M-12 | O registro terminou em {data} com o encerramento da parceria. |
| M-13 (Daniela, quando o parceiro pergunta o motivo genérico) | Por regra de sigilo, a Save não comenta a situação de empresas com outros parceiros ou com a própria Save. Se você já tinha relação com esta empresa antes do seu registro, me envie o que comprova isso (por exemplo, data de reunião ou documento recebido) e eu levo o caso para análise da Área Partners. |
| M-14 | Seu registro de {razao_social} vence em {dias} dias, em {valido_ate}. Se houve avanço com a empresa, use o botão Pedir prorrogação e conte o que aconteceu. |
| M-15 | A Área Partners separou uma empresa para você avaliar: {razao_social}. Aceite até {data_limite_aceite} para seguir com o atendimento. Depois dessa data, a empresa volta para a Área Partners. |
| M-16 | O negócio de {razao_social} está parado esperando: {pendencia}. Se você já enviou, avise em Demandas para atualizarmos. |
| M-20 | Em conferência contratual. Avisaremos aqui quando a conferência terminar. |
| M-21a | Seu extrato de {competencia} está disponível. Confira as linhas e, se algo não bater, conteste até {data_limite_contestacao}. A parte não contestada segue o calendário normal. |
| M-21 | Contestação recebida em {data}. Resposta da Save até {data_resposta}. A parte não contestada do extrato segue o calendário normal. |
| M-22 (procedente) | Revisamos a linha contestada e você tem razão: {explicacao}. O ajuste entra no extrato de {competencia_seguinte}. |
| M-22 (improcedente) | Revisamos a linha contestada e o cálculo está de acordo com o seu termo: {explicacao}. Se tiver um fato novo, você pode reabrir a contestação até {data_limite}. |
| M-23 | Ajuste de {valor} referente a {motivo_externo} na empresa {cnpj_mascarado}. Ele será compensado nos próximos extratos, limitado a metade da remuneração de cada mês. Se tiver dúvida, fale com a Área Partners. |
| M-24 | Recebemos sua nota fiscal de {competencia}, mas {divergencia}. Por favor, emita uma nova nota com {correcao} até o dia {nf_limite} para entrar neste ciclo. |
| M-25 | Remuneração de {competencia} paga em {data_pagamento}. Valor líquido: {valor_liquido}. Retenções: {retencoes}. |
| M-30 | Pedido {id} recebido. Tipo: {tipo}. Retorno com a previsão em até {primeira_resposta}. |
| M-31 | Para seguir com o pedido {id}, precisamos de: {itens}. |
| M-32 | Pedido {id} encaminhado à área {area}. Previsão de retorno: {data}. |
| M-33 | O pedido {id} está levando mais tempo que o previsto. Já cobramos a área e avisaremos aqui. |
| M-34 | Por enquanto, os documentos da empresa continuam pelo canal de sempre com a Área Partners. Avisaremos quando o envio pelo portal estiver disponível. |
| M-41 (carta de nível, esqueleto) | {nome_escritorio}, esta é a leitura do trimestre {trimestre} do Programa Partners. Seu nível: {nivel}. O que sustenta o nível: {criterios_cumpridos}. O que falta para o próximo: {criterios_faltantes}. Os benefícios do seu nível estão na página do programa. Este nível não altera o percentual do seu termo nem o atendimento técnico das suas indicações. |
| M-50 | Bem-vindo ao Programa Partners da Save. Seu acesso ao portal está ativo. Primeiros passos: trilha N1 da Academia (cerca de 2 horas) e uma conversa de 30 minutos com {nome_jenifer} e {nome_padrinho}. Nas duas primeiras indicações, a reunião com a empresa é conjunta. |
| M-51 | Você concluiu os primeiros 90 dias do programa. A partir daqui, a reunião conjunta fica disponível quando você pedir. |
| M-52 (reativação, por pessoa) | {nome}, faz um tempo que não falamos de novas empresas. Mudou algo na sua carteira ou na forma de trabalhar? Posso te mandar uma lista curta de empresas com perfil para conversar. |
| M-53 (distrato do cliente, por pessoa) | {nome}, queremos te avisar antes de qualquer outra conversa: a empresa {razao_social} pediu o encerramento do contrato com a Save. Vou te explicar o que muda no atendimento e na sua remuneração. Podemos falar hoje? |
| M-90 | O texto tem um dado pessoal que não pode ser enviado por aqui (CPF, documento ou dado bancário). Retire esse dado e envie de novo. |

---

## 15. Termo de Uso do Portal do Parceiro Save (rascunho para o Jurídico)

> **Rascunho da Área Partners, 26/10/2026. Pré-análise, não substitui parecer.** Validação: advogado(a) responsável [a preencher]. Base: minuta de 23/10/2026 (`departamentos/ti/minuta-termos-consulta-parceiros.md`), ampliada para o portal inteiro. Pontos `[VALIDAR JURÍDICO]` listados em 15.10.

**15.1 O que é o Portal.** O Portal do Parceiro Save é o ambiente em que parceiros autorizados registram oportunidades, acompanham os negócios que indicaram, consultam o extrato de remuneração, abrem pedidos à Área Partners e acessam materiais e trilhas de capacitação.

**15.2 Quem pode usar.** Pessoas indicadas pelo escritório parceiro que tem termo de parceria vigente com a Save e que foram autorizadas pela Área Partners. O acesso é pessoal, com autenticação em dois fatores, e não pode ser compartilhado. O titular do escritório responde pelos usuários que indicar e deve pedir a desativação de quem sair do escritório.

**15.3 Relação com o termo de parceria.** Este Termo de Uso trata só do uso do Portal. Percentual, base, condições e prazos da remuneração são os do termo de parceria assinado e seus anexos; o Portal mostra essas informações e não as altera. Em caso de diferença, vale o termo de parceria.

**15.4 O que você se compromete a fazer e a não fazer.**
1. Registrar só empresas com as quais tem relação real e informar dados corretos.
2. Compartilhar dados de contato de pessoas da empresa só quando tiver autorização ou outra base legal para isso, e só os dados pedidos.
3. Não usar o registro ou a consulta para levantar ou reconstituir a carteira de clientes da Save ou de outros parceiros. Há limite diário de uso, e o uso é registrado.
4. Não prometer à empresa valor, prazo ou resultado, nem apresentar material ou informação do Portal como promessa.
5. Usar só os materiais aprovados disponíveis no Portal, sem alterar o conteúdo, e identificar-se como parceiro remunerado pela Save quando divulgar algum deles.
6. Não apresentar produtos marcados como "em descoberta" com taxa, condição ou simulação.
7. Não inserir no Portal CPF, documentos pessoais ou dados bancários de terceiros.
8. Manter sigilo sobre informações da Save e das empresas que conhecer pelo Portal.

**15.5 Registro de oportunidade.** O registro é uma proteção temporária da oportunidade, com prazo e regras publicados na página do programa, e não cria exclusividade, zona ou território sobre a empresa ou sobre qualquer região ou segmento. A Save pode não aceitar um registro e, por sigilo, nem sempre informa o motivo.

**15.6 Informações do Portal.** O estado dos negócios reflete as informações disponíveis nos sistemas da Save na data indicada na tela. O Portal não informa estimativa de crédito, prazo de procedimentos na Receita Federal nem chance de resultado, que dependem da análise técnica e das autoridades. O extrato mostra valores só depois do recebimento do honorário pela Save, conforme o termo de parceria.

**15.7 Disponibilidade.** A Save busca manter o Portal disponível, mas ele pode passar por manutenção ou ficar indisponível. Pedidos urgentes, como notificações da Receita recebidas pela empresa, devem ser comunicados também pelo canal habitual com a Área Partners.

**15.8 Suspensão e encerramento.** A Save pode suspender o acesso em caso de uso fora deste Termo, inclusive de forma preventiva quando houver indício de uso indevido, e encerrá-lo com o fim do termo de parceria. Encerrada a parceria, o acesso ao extrato pode ser mantido até o pagamento das remunerações pendentes, conforme o termo de parceria.

**15.9 Mudanças neste Termo.** A Save pode atualizar este Termo. A versão nova será apresentada no próximo acesso e o uso do Portal depende do aceite.

**15.10 Pontos para o Jurídico** `[VALIDAR JURÍDICO]`
1. Se o Termo de Uso deve ser anexo do termo de parceria (aceite único) ou aceite eletrônico separado, e como provar o aceite (versão, data, usuário).
2. Cláusula 15.5 frente ao CC arts. 726 a 728 e à Lei 4.886, art. 31: suficiente para afastar exclusividade presumida?
3. Cláusula 15.8 (suspensão preventiva) frente ao CC art. 422 e, se a relação for lida como representação, à Lei 4.886, arts. 34 a 36.
4. Linguagem "remuneração por indicação comercial e por serviços de apoio" frente à Lei 8.906, art. 34, III e IV.
5. Identificação de parceiro remunerado (guia do CONAR de 12/05/2026) e texto do selo.
6. Foro, legislação aplicável e se cabe cláusula de limitação de responsabilidade por indisponibilidade.

---

## 16. Aviso de privacidade do Portal (rascunho para o Jurídico)

> **Rascunho, 26/10/2026.** Base: minuta de 23/10/2026. Pontos `[VALIDAR JURÍDICO]` em 16.9.

**16.1 Quem trata os dados.** [Razão social da entidade Save responsável, a preencher], como controladora dos dados tratados no Portal. Encarregado: [nome e canal, a preencher] (LGPD, art. 41).

**16.2 Quais dados.**
- **Seus dados de usuário:** nome, e-mail profissional, escritório, papel, data de aceite deste aviso e do Termo de Uso, registros de acesso (data, hora, tela, ação e um código derivado do endereço de rede).
- **Dados das empresas que você registra:** CNPJ, razão social, tema de interesse, como você conhece a empresa e a evidência informada.
- **Contato na empresa:** nome, cargo e um canal profissional (e-mail corporativo ou telefone comercial) da pessoa com quem a Save vai falar.
- **Remuneração:** linhas do extrato, notas fiscais emitidas pelo escritório e retenções. Dados bancários do escritório ficam com o Financeiro da Save, fora do Portal.

Não coletamos pelo Portal CPF, documentos pessoais, dados bancários de terceiros, dados de sócios fora do cadastro público da empresa nem telefone pessoal.

**16.3 Para quê.** Operar o programa de parceiros: registrar e conferir oportunidades, atender as empresas indicadas, mostrar o andamento e a remuneração, responder pedidos, oferecer capacitação, proteger o Portal contra uso indevido e cumprir obrigações legais e fiscais.

**16.4 Bases legais (proposta).** Execução do termo de parceria (LGPD, art. 7º, V) para os dados do escritório e dos usuários; legítimo interesse (art. 7º, IX, e art. 10) para o contato na empresa registrada e para a segurança do Portal, com avaliação registrada; cumprimento de obrigação legal (art. 7º, II) para notas fiscais, retenções e registros de acesso (Lei 12.965/2014, art. 15).

**16.5 Com quem compartilhamos.** Prestadores de tecnologia contratados pela Save que atuam como operadores (nuvem Microsoft Azure no Brasil, ferramentas de inteligência artificial contratadas pela Save e o sistema de gestão comercial da Save), sempre para as finalidades acima. Quando a consulta pública de CNPJ estiver ligada, o CNPJ digitado é enviado a serviços públicos de consulta. Seus dados e os das empresas que você registra não são mostrados a outros parceiros.

**16.6 Por quanto tempo (proposta).**
| Dado | Prazo |
|---|---|
| Contato na empresa em registro recusado, expirado ou encerrado sem contrato | 90 dias após o encerramento; depois fica só o CNPJ e a data do registro |
| Registros de oportunidade, extratos, notas e contestações | Enquanto durar a parceria e por 5 anos depois |
| Registros de acesso | 12 meses |
| Dados de usuário desativado | 5 anos após a desativação, para prova de aceite e de uso |

**16.7 Seus direitos.** Você pode pedir confirmação, acesso, correção, anonimização, portabilidade, informação sobre compartilhamento e eliminação dos dados tratados com base no consentimento, nos termos da LGPD (art. 18), pelo canal do encarregado. Alguns dados precisam ser guardados pelos prazos acima por obrigação legal ou para defesa de direitos.

**16.8 Segurança.** Acesso com autenticação em dois fatores, dados guardados em ambiente da Save no Brasil, isolamento por escritório, registro de acessos e acesso interno só por quem precisa.

**16.9 Pontos para o Jurídico** `[VALIDAR JURÍDICO]`
1. Bases legais de 16.4, em especial o legítimo interesse para o contato na empresa (teste de balanceamento e registro, art. 37).
2. Papel do parceiro ao compartilhar o contato: controlador próprio que comunica dados à Save (responsabilidade do art. 42) e se a declaração do formulário é suficiente.
3. Prazos de 16.6 frente ao CC art. 206 §5º, I, à Lei 4.886 art. 44 parágrafo único e ao Marco Civil art. 15.
4. Operadores de IA e eventual transferência internacional (arts. 33 e 39): cláusulas-padrão da ANPD.
5. Empresário individual (nome civil como razão social): mascarar ou recusar.
6. Exceção à regra da casa "dado de cliente fica no Mac" para guardar CNPJ e contato no Azure SQL (desenho §7 item 5).

---

## 17. Auditoria de promessas (Qualidade)

Comando: `python3 skills/depto-qualidade/scripts/auditar_texto.py docs/prm/v2/02-regras-de-negocio.md --resumo`.
Resultado em 26/10/2026 (2ª rodada): **0 ALTO, 0 MÉDIO, 0 BAIXO, 1 INFO** (linha da regra PRM-R03 que cita alíquota zero e PER; falso positivo previsto). Na 1ª rodada houve 1 ALTO (verbo de certeza na PRM-R102) e 1 BAIXO (termo de varejo na PRM-R80), corrigidos na redação. Verificação de dados do repositório (`infra/checar-dados.py`): 0 achados. Critério: 0 ALTO e 0 MÉDIO no documento inteiro, incluindo o catálogo da seção 14 e os rascunhos das seções 15 e 16. Alertas INFO são linhas que descrevem a própria regra (falso positivo previsto pelo `contexto_de_regra` do auditor).

**Regra para o código:** o catálogo da seção 14 é carregado de um arquivo de dados (`textos_parceiro.json`); o teste automatizado roda o auditor sobre esse arquivo e falha o build com qualquer ALTO ou MÉDIO.

---

## 18. Decisões que ainda travam regras

### 18.1 Do Luis (alçada: regra, remuneração, conflito, frase permitida)
| # | Decisão | O que trava | Recomendação | Prazo sugerido |
|---|---|---|---|---|
| DL-01 | **Regra de registro R1–R3**: unidade = raiz inteira; precedência pelo carimbo do registro completo; desempate em 4 níveis; divisão só como exceção, sem duas remunerações integrais; proteção do cliente ganho = contrato + 12 meses; tese nova com 15 dias de preferência; venda direta sem remuneração; validade pausada em conflito; conflito decidido em 10 d.u. | Todo o módulo de registro e o conflito | Aprovar como v1, com revisão em 90 dias usando os dados da fila; legado caso a caso | 14/11 (fase 0 do desenho) |
| DL-02 | **Validade:** 120 dias para Master e consultores, 90 para indicador, + 60 de prorrogação automática com avanço | `valido_ate`, rotina de expiração, benefício de nível | Aprovar; os 180 dias do material jurídico só onde o termo assinado já disser isso (o Jurídico ajusta o texto) | 14/11 |
| DL-03 | **Sigilo na recusa:** recusa por outro parceiro ou por cliente da Save sempre com o motivo genérico, com caminho de contestação por evidência (M-13) | Texto da recusa e fila de contestação de registro | Aprovar: estende ao registro a decisão de 23/10 sobre a consulta | 14/11 |
| DL-04 | **Cauda de mediação** de 6 meses após expiração ou perda, com ficha ao Luis e sem remuneração automática | PRM-R36 | Aprovar, com o Jurídico validando o prazo frente ao CC art. 727 | 14/11 |
| DL-05 | **Percentual em lead gerado pela BDR** da Save | PRM-R42 | Manter o percentual do termo em 2026 e rever junto da política 2027 (campo `origem` já separa) | 30/11 |
| DL-06 | **Troca de parceiro a pedido da empresa** | Seção 12, caso 6 | Parceiro original mantém a remuneração dos contratos já assinados até o fim deles; o novo só em contratos novos; sem retroagir | 30/11 |
| D102 | Liberar o conferido à medida do recebimento; atípico só com contrato | Estado `em_conferencia` × fluxo normal | Opção A (já recomendada pelas áreas) | 30/10 |
| D65 | Registro único de exceções de honorário | PRM-R61 | Opção A; inventário dos 9 termos em 2 semanas | 06/11 |
| D109 | Percentual de honorário preenchido pelo contrato | PRM-R62 | Regra na ordem da opção B | 06/11 |
| DL-07 | **Base da recuperação: honorário recebido bruto × líquido de tributos** (com o Financeiro, OC-4) | PRM-R56 | Bruto do honorário recebido até o Financeiro mostrar a prática atual; mudança só para contratos novos | 06/11 |
| DL-08 | **Estorno e compensação:** linha negativa, até 50% por ciclo, por até 24 meses, só com cláusula no termo | PRM-R68 a R70 | Aprovar e pedir a Contratos a cláusula no anexo de remuneração | 30/11 |
| DL-09 | **Valor previsto no extrato** antes do recebimento | `extrato.mostra_valor_previsto` | Não mostrar valor antes do recebimento (só percentual e estado) | 14/11 |
| F8 | Programa de níveis (opção A) | Módulo de nível sai do modo sombra | Opção A; L6 opção 2; nível em sombra até a carta individual | 14/11 |
| DL-10 | **Barra de nível em percentual do patamar, sem R$** | PRM-R84 | Aprovar | junto da F8 |
| DL-11 | **Visão do Master padrinho:** só marcos de onboarding do indicador, sem negócios nem remuneração | PRM-R16 | Aprovar | 14/11 |
| DL-12 | **Catálogo M-xx como frases permitidas** e envio automático por tela e e-mail dos textos fixos de estado (fora do degrau 2 da D28, que trata de respostas a perguntas) | PRM-R13; seção 13 | Aprovar o catálogo; texto livre segue com pessoa | antes do piloto |
| DL-15 | **Natureza jurídica do Master** (indicador × condutor; OC-16) e cláusula de pós-rescisão | Dia de pagamento (15 × 20), caso 8, correção por atraso | Decidir com o parecer do Jurídico de 31/10; até lá, dia 20 e pós-rescisão conforme o termo | após 31/10 |
| DL-16 | **Guarda de CNPJ e contato no Azure SQL** e chamada externa de CNPJ no portal | Fase 2 inteira | Aprovar condicionado ao parecer de LGPD (Brazil South, tenant Save, mínimo necessário, prazos da 16.6) | antes do pedido à TI |
| DL-17 | **Parceiro só PJ** (sem PF e MEI) | PRM-R64 | Aprovar | 30/11 |
| DL-18 | **Certificação N2 como porta** de Gestão de Passivo e estruturação patrimonial | PRM-R97 | Aprovar o desenho e ligar só quando os módulos estiverem validados | 2027 |

### 18.2 De outros donos (não sobem ao Luis)
| # | Decisão | Dono | Trava |
|---|---|---|---|
| OC-18 | Calendário do extrato | Financeiro (vale a recomendação em 28/10) | Seção 6.4 |
| P5 / D18 | Fonte de recebimentos por negócio | Financeiro + time de CRM | Todo o extrato além de `previsto` |
| OC-1 | Dedução antes dos 10% dos produtos 2027 | Financeiro + Gilberto | PRM-R54 |
| OC-7 a OC-10 | Entidade pagadora, CSRF, regra 2027, PF/MEI | Financeiro + Tributário | Seção 6.3 |
| DL-13 | Anexos, prazos de guarda, empresário individual, bases legais | Jurídico + TI | PRM-R76, 16.6, caso 16 |
| DL-14 | Linguagem da remuneração e selo de parceiro remunerado | Jurídico | PRM-R04, PRM-R91 |
| Semana 0 | Prazos do `sla.json` validados com as áreas | Daniela | PRM-R71 |
| Mapa de etapas | Validar 5.1 e mapear os outros funis | Daniela + Dados | PRM-R43 |

---

## 19. Entrega em 3 blocos e revisão

**1. O que você pediu**
Especificação executável das regras do PRM em 8 módulos: máquinas de estado com quem dispara, prazo e texto exato ao parceiro; 103 regras numeradas (PRM-R01 a PRM-R112, com lacunas de numeração reservadas por módulo) com origem e marca [A], [P] ou [O]; 62 parâmetros configuráveis (prazos 120/90 + 60, percentuais vindos do cadastro, retenções, calendário); 18 casos de borda transversais; matriz de papéis e permissões com 10 papéis; notificações e SLAs; catálogo de 37 textos-modelo; rascunhos do Termo de Uso e do aviso de privacidade do portal para o Jurídico; auditoria de promessas; decisões que travam regras, com recomendação.

**2. O que você também precisa**
- O 3º estado do registro da versão 1 ("livre" com texto diferente do neutro) deixava o parceiro distinguir cliente livre de cliente da Save. Aqui livre e neutro recebem o mesmo texto e o mesmo tempo mínimo de resposta (PRM-R21 e PRM-R27); só a decisão final difere, e a recusa genérica cobre vários motivos.
- Nada do extrato passa de "previsto" sem a fonte de recebimentos do Financeiro (P5). O pedido ao Financeiro pode sair agora, em paralelo à D102.
- Dos itens que travam o piloto, quatro vencem até 14/11 (DL-01, DL-02, DL-03, F8). Os demais podem seguir com o valor padrão do parâmetro, porque mudam sem deploy.
- O Termo de Uso e o aviso de privacidade ampliam a minuta de 23/10 (consulta de Lucro Real) para o portal inteiro; vale mandar os dois juntos ao advogado.

**3. O que falta e quem fornece**
| Falta | Quem |
|---|---|
| Decisões DL-01 a DL-12, DL-15 a DL-18, D102, D65, D109, F8 | Luis |
| Fonte de recebimentos, calendário, base, entidade pagadora | Financeiro (com o time de CRM) |
| Termos dos 9 Masters com percentual, vigência, cláusula de estorno e pós-rescisão | Contratos (D65) |
| Parecer de natureza jurídica, linguagem, Termo de Uso, aviso de privacidade, prazos de guarda | Jurídico |
| Retenções 2026 e regra de 2027 | Tributário |
| Validação do mapa de etapas e dos prazos do `sla.json` | Daniela (com Dados) |
| Módulos da Academia validados | Geovana e time técnico |

**Registro de revisão**
```json
"revisao": {
  "gerente": "Gerente de Operações de Canal (coordenação das regras de negócio)",
  "especialistas": ["Registro de Oportunidade e Conflito de Canal", "Analista de Comissionamento", "Extrato e Prestação de Contas", "Elegibilidade e Retenções", "Política do Programa e Níveis", "Gestor de Níveis e Jornada", "Coach de Onboarding e Enablement", "Designer da Academia", "Contratos de Parceiros", "Distratos e Cobrança", "Perímetro Regulatório", "Triagem e SLA", "Retorno ao Parceiro", "Higiene de CRM e Registro", "Auditor de Promessas"],
  "rodadas": 2,
  "areas_consultadas": ["depto-operacoes-canal", "depto-partner-success", "depto-contratos", "depto-juridico", "celula-daniela", "depto-qualidade"],
  "aprovado": true,
  "ajustes": ["livre e neutro com o mesmo texto e o mesmo tempo mínimo (anti-varredura)", "valor previsto oculto até o recebimento (DL-09)", "barra de nível sem R$ (DL-10)", "auditor de promessas: ajustes de redação até 0 ALTO e 0 MÉDIO"],
  "auditor_promessas": "2ª rodada: 0 ALTO, 0 MÉDIO, 0 BAIXO, 1 INFO; checar-dados: 0 achados"
}
```
