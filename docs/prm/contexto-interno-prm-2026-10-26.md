# PRM da Área Partners · contexto interno que o PRM precisa respeitar e reaproveitar

> 26/10/2026 · uso interno · levantamento só de leitura (repositório, decisões do Conselho, dados locais do HubSpot de 26/10/2026 06h53). Nada foi alterado, enviado ou gravado no HubSpot/GLPI. Sem nome de cliente. Masters aparecem como **Master A a I** (o de-para está nos arquivos-fonte citados, `departamentos/dados/dados-bi-*.json` e `registro/gestao/pacote-*.json`). Caminhos relativos a `~/agentes-partners/`; código das skills conferido na branch `claude/amazing-kirch-442f46` (mais nova que o `main`).
>
> Antecedente: em 13/10/2026 houve uma proposta de PRM em 4 fases (1. PRM interno no painel Central Partners: ficha 360, registro de oportunidade com checagem de conflito, alertas; 2. ciclo de vida, níveis, extrato, biblioteca; 3. HubSpot como sistema oficial do parceiro; 4. portal externo, construir × comprar: HubSpot sem PRM nativo; apps Partner Deals Portal, Channeltivity, Impartner). O Luis pôs em stand-by no mesmo dia e retomou em 26/10/2026 ("uma das minhas maiores dores"). A proposta só existe na memória do projeto, não em arquivo.

---

## 1. Quem são os parceiros

### 1.1 Tipos e quantidades (HubSpot de 26/10/2026, `metricas_ps.py` → `departamentos/partner-success/metricas/metricas-ps-2026-10-26.json`)
| Tipo | Quantos | O que faz | Quem atende na Save | Fonte |
|---|---|---|---|---|
| **Master** (escritório, em regra contábil, com rede própria de consultores) | **9** no roster oficial (`departamentos/resultados/mapeamento-hubspot.json`, `escopo.parceiros_roster`) | Indica e qualifica; abre o decisor e os documentos (e-CAC, EFD). **Não executa**: a Save faz diagnóstico, apresentação, contrato, PER | Daniela (ponto focal dos 9; célula `celula-daniela`) | ESTADO.md (Fase 0); `gestor-contas-chave.md` §2 |
| **Consultor do Master** (pessoa dentro do escritório Master que de fato indica) | **27** nomes identificados nos negócios dos Masters | Conversa com o cliente; o nome entra como texto livre em `nome_do_parceiro` | Daniela, via o Master | `metricas-ps` (grupo `consultores_dos_masters`) |
| **Parceiro fora do roster / indicador** (escritório ou pessoa ligada a um Master, ou avulso) | **12** nomes com negócio | Indica; trilha "Indicador" do programa | Jenifer recruta; Daniela atende | `metricas-ps` (`fora_do_roster`); `celula-jenifer` subagente 8 |
| **Indicador novo recrutado** (escritório contábil, CNAE 6920-6/01, na região de um Master) | em recrutamento (sem cadastro próprio) | Termo de indicação; Master "padrinho" | Jenifer (recrutamento + toques 30/60/90) | `celula-jenifer/SKILL.md`; `coach-onboarding-enablement.md` |

Papéis internos ao redor do parceiro: **Daniela** (gestão de conta, demandas, CRM, retorno ao parceiro), **Jenifer** (BDR: listas de prospects por Master, recrutamento de indicadores, distribuição e registro do lead no Master), **Geovana** (suporte técnico, reuniões técnicas, Recuperador), **Luis** (gerente comercial Masters; decide conflito de canal, remuneração, regra). Donos de produto: Junior (Save Invest), João Mattos e Paulo (Internacional), time técnico e Jurídico.

### 1.2 Como o parceiro entra hoje
- **Master:** relação antiga; quase todos são anteriores ao início da base (fev/2023), por isso o onboarding de Master não é medido. Não se confirmou que os 9 têm **termo escrito** (dossiê D65, parecer de Contratos de 26/10/2026; inventário dos termos proposto em 2 semanas).
- **Indicador:** Jenifer acha o escritório (`lista_master.py --parceiros`), convida (modelo M8), o termo é assinado (Contratos/Jurídico), D0 = assinatura; plano 30/60/90 com Master padrinho (`entregas/2026-09-29-v1/onboarding-30-60-90.md`). A **data de entrada não existe no HubSpot** (pergunta 11 de `depto-partner-success/references/perguntas-ao-dono.md`); o D0 vem de `scripts/datas-entrada-parceiros.json` ou do 1º negócio.
- **Promoção a Master:** jornada Registrado → Certificado → Pleno (N2 + ≥ 5 ganhos + conversão ≥ 20%) → **decisão do Luis** (território, sem conflito de canal) (`gestor-niveis-jornada.md` §2).
- **Natureza jurídica em aberto:** o Master é indicador ou condutor? Risco de requalificação como **representante comercial** (Lei 4.886/1965, arts. 1º, 27, 31, 32 §§1º e 7º) e vedação de "divisão de honorários" com não advogado (Lei 8.906/1994, art. 34). Perguntas 16 e 4 em `depto-operacoes-canal/references/perguntas-ao-dono.md` e PS-4.

### 1.3 Retrato dos Masters (saúde do `depto-dados`, 22/10/2026; margem do pacote de 26/10/2026)
| Master | Saúde (0–100) | Leitura | Repasse negociado | Margem líquida 12 m |
|---|---|---|---|---|
| A | 98 🟢 | Grande e regular; dependência de PIS/COFINS (termina em 2027) | 50% | 12,3% |
| B | 80 🟢 | Ticket baixo; conversão é o ponto de trabalho | 50% | 15,0% |
| C | 69 🟡 | Entrada subiu, valor caiu (−67,9%) | 50% | **7,6%** (menor da carteira) |
| D | 58 🟡 | Dependência de café (fora das contas desde abr/2026) | 40% | 18,2% |
| E | 55 🟡 | Entrada caiu 66,7%: reativação | 30% | 17,5% |
| F | 48 🟡 | Entrada e valor caindo juntos (−81,8%) | 50% (inferido nos negócios: 30%) | 15,2% |
| G | 48 🟡 | Quase parado fora do café | 25% | 19,5% |
| H | ⚪ base pequena | Em rampa (+671% de entrada) | 30% | 14,9% |
| I | ⚪ base pequena | Base pequena | 30% (inferido, a confirmar) | 16,7% |

Fontes: `skills/celula-daniela/references/especialistas/gestor-contas-chave.md` §2; `departamentos/operacoes-canal/percentual-parceiros.json` (informado pelo Luis em 13/10/2026; consistência do % nos negócios de 51% a 100%); `registro/gestao/pacote-2026-10-26.json` (`margem_liquida_por_master_min`, carteira 17,35%).

---

## 2. Jornada atual do parceiro, ponta a ponta, e onde dói

### 2.1 A jornada como ela roda hoje
| Etapa | Como acontece | Sistema | Dor (evidência) |
|---|---|---|---|
| 1. Recrutamento / ativação | Jenifer lista e convida; termo; 30/60/90 | Excel da Jenifer, Word | Sem data de entrada nem nível no HubSpot; certificação/trilha **não existem** como dado (`depto-partner-success/SKILL.md`, "Limites conhecidos") |
| 2. Indicação / registro da empresa | Parceiro manda pelo **WhatsApp** (grupo do Master ou individual); a Daniela cria o card. Há também o formulário HubSpot "Novas Oportunidades" (portal 47865021, com `id_do_parceiro`; hoje usado pelos agentes só para recorrência, envio bloqueado até o Luis liberar, `lib/oportunidade_form.py`) | WhatsApp → HubSpot | **4.891 de 5.051 negócios (97%) têm a Daniela como dona**: o parceiro não registra nada sozinho. Registro só "protege" quando a Daniela cria o card (proposta de regra, item 3). Checagem de conflito é manual (`crm_checagem.py --cnpj`) |
| 3. Diagnóstico | Técnico analisa; parceiro consegue e-CAC/EFD | HubSpot + Bitrix (execução) + GLPI | Parceiro pergunta status pelo WhatsApp; boa parte dos chamados de "prioridade/reanálise" volta com "já está em apresentação" ou "parecer já no card" (`infra/glpi-regras.md`) |
| 4. Apresentação / contrato | Reunião com cliente e parceiro; Contratos envia | HubSpot, assinatura eletrônica | 164 negócios em "Apresentação de Diagnóstico" e 23 em "Contrato Enviado" no RT em 26/10; sentinelas de parado (`lib/operacao.py`) |
| 5. Execução / PER / pós-venda | Técnico protocola PER; pós-venda acompanha | Bitrix (processo 162), e-CAC | Aging do PER, glosa e recebido **sem dado** (métricas cinza no pacote de 26/10) |
| 6. Remuneração do parceiro | Financeiro paga; sem extrato padronizado | Planilhas / HubSpot | **0 de 1.696 ganhos com valor recebido**; 1.047 ganhos com repasse **bloqueado**; nenhum extrato real possível (`conferencia-repasses-2026-10-26.json`) |
| 7. Relacionamento / crescimento | Conversas ad hoc; sem QBR formal; sem nível comunicado | WhatsApp | QBR e metas por Master pendentes (D75); 5 Masters com ritmo em queda > 20% (R$ 101,8 mi de líquido potencial 12 m) |

### 2.2 Onde dói, com números
- **Tudo passa pelo WhatsApp e por uma pessoa.** Registro de demandas (`registro/demandas.json`, 30/09 a 23/10/2026): **125 demandas, 120 pelo WhatsApp (96%)**; 68 da Daniela, 34 da Geovana, 18 da Jenifer. Triagens do WhatsApp (61 rodadas de 29/09 a 26/10): **375 pedidos distintos** com ação (234 na caixa da Daniela). Pelo texto do pedido (classificação por palavra-chave, aproximada; 139 ficaram sem classe): parecer/diagnóstico/análise ~119, documentos/e-CAC/procuração ~47, reunião ~34, contrato/assinatura ~30, status ~26, compensação/guias ~23, Receita/notificação/jurídico ~23, cadastro/indicação ~13, material ~9, repasse ~3.
- **Espera do parceiro.** Tempo "aguardando resposta do time" nas triagens: mediana **7,9 h**, p75 20 h, p90 23,6 h (444 medições). Pacote de 26/10: tempo até a resposta **pronta** (pelos agentes) mediana 7,2 h; a resposta efetiva enviada pelo time **não é registrada**.
- **GLPI como ponte.** 1.115 chamados (25/11/2025 a 01/10/2026), **67% abertos pela Daniela (565) e pela Geovana (184)** (`infra/glpi-regras.md`): o time vira despachante entre parceiro e áreas.
- **Sem visão do negócio para o parceiro.** O parceiro não vê etapa, parecer, contrato, execução nem PER: pergunta. Em D28 o Luis aprovou respostas automáticas só para "dado objetivo" (etapa, assinatura, execução, parecer) com 20+ casos e 95%+ de acerto; valor, prazo, tese e cobrança ficam sempre com uma pessoa.
- **Extrato e repasse.** Conferência de 26/10/2026: 1.696 ganhos; **1.047 Bloqueados, 217 Revisar, 432 OK**; repasse calculável R$ 118,9 mi, só OK R$ 69,2 mi; % de honorário preenchido em 730; 60 inversões 70/30; **81 grupos de duplicidade** (R$ 212,2 mi de crédito em excesso); recebido 0. Dossiê D102: "repasse retido é o risco ao canal mais citado pelo Conselho".
- **Conflito de canal sem regra aprovada.** 82 raízes de CNPJ com mais de um canal, 305 negócios, R$ 483,6 mi de crédito; 19 de severidade Alta; **3 Master × Master**; R$ 8,6 mi abertos de quem chegou depois (`conflito-canal-2026-10-26.json`). Regra de registro proposta em 29/09 (R1–R3) **não aprovada**.
- **Capacidade de indicação parada dentro dos Masters.** 18 de 27 consultores dormentes ou inativos; 16 consultores com 1 só ganho (pacote de 26/10).
- **Concentração.** Top 5 Masters = **90,6%** do fechado 12 m (crédito); o maior = 34,8% (pacote de 26/10). Em líquido Save (12 m sem café, HubSpot de 07/10): 3 maiores = 81,1%, 3,3 parceiros efetivos.
- **Monoproduto.** Clientes com 2+ produtos = **1,4%** (14 de 1.026 raízes); funil por produto cinza (sem propriedade "Produto", D37).
- **Material.** Pedidos sem material vão para `celulas/daniela/materiais/pedidos-sem-material.md`; a Academia N1 existe só como rascunho com `[VALIDAR TÉCNICO]` (PS-8); cases aprovados para uso externo: nenhum (SESSOES §22, 23/10).

---

## 3. Regras da casa que o PRM tem que codificar

| # | Regra | Como vira requisito no PRM | Origem |
|---|---|---|---|
| R1 | **Repasse da recuperação negociado por parceiro**, sem regra única de ≥ 50%; será revisto com os novos produtos | Campo de % por parceiro vindo do termo (fonte única), não do card; alerta quando o % do negócio diverge do cadastro | D64 (22/10); `percentual-parceiros.json`; Proposta de política (29/09) item 1 |
| R2 | **Produtos 2027: 10% do líquido Save**, crescendo pelo programa. Líquido Save = valor do contrato × % honorário (ex.: R$ 1 mi × 20% = R$ 200 mil → parceiro R$ 20 mil). Dedução de tributos/custos antes dos 10%: a confirmar | Regra de cálculo por família de produto | D78, D97; perguntas OC-1 e OC-2 |
| R3 | **Crédito Internacional: 10% a 30%** por programa de desenvolvimento (nível = teto; escopo executado = pagamento); só vale após o G2. D61 × D78 (o teto de 30% vale para os demais produtos 2027?) em aberto | Família CI desligada até o G2 | D61; F8 (L1–L10); D108 |
| R4 | Save Invest: o parceiro é remunerado **pela Save**, nunca pela financiadora (Federal Invest) sem enquadramento | Pagador sempre Save | D96, D97; OC-17 |
| R5 | **Contratado ≠ devido ≠ pago.** Repasse nasce do **recebimento** do honorário (pay-on-collection); nenhuma linha "a pagar" sem recebido | Extrato mostra contratado e "em andamento"; "a pagar" só com recebido | `depto-operacoes-canal/SKILL.md` regra 3; Proposta de política item 3; D102 |
| R6 | **Liberar o repasse conferido** (R$ 69,2 mi) à medida do recebimento; **atípico** (honorário > 50%, café a 70%, % parceiro > 100%) só com contrato conferido; pagar a parte incontroversa | Status por ganho (Bloqueado / Revisar / OK) e ficha de atípico | D102 (pendente), D65 (pendente), D109 (pendente) |
| R7 | **Não reter repasse** por campo vazio (tese, variante, %): a falta de campo bloqueia forecast e relatório, não o pagamento | Bloqueio de forecast ≠ bloqueio de pagamento | D45, D62, D71, D73; divergência C14 resolvida no dossiê D102 |
| R8 | Honorário de êxito incide sobre o valor **compensado de ofício**, com Selic | Base do extrato inclui compensação de ofício | D95 |
| R9 | Escala de honorário 30/25/20 **reprovada**; o programa não mexe no honorário do cliente | Sem regra de desconto por nível | D79 |
| R10 | **Retenções** sobre a NF do parceiro PJ (IRRF 1,5% RIR/2018 art. 718; CSRF 4,65% Lei 10.833 art. 30; ISS; Simples/MEI; transição CBS 2027), a validar com o Tributário | Checklist de elegibilidade por lote: termo vigente, CNPJ ativo, NF, retenções, sem Bloqueado, conflito resolvido | `elegibilidade-retencoes.md`; Proposta de política item 6; OC-7 a OC-10 |
| R11 | **Calendário e extrato** (proposta): corte no fim do mês; cálculo até o 5º d.u.; aprovação; extrato até o 8º d.u.; **contestação em 10 dias corridos**, resposta em 5 d.u.; pagamento até o dia 20 de M+1 contra NF. Se a relação for representação, até o dia 15 (Lei 4.886, art. 32 §1º) | Módulo de extrato + fila de contestação com SLA e causa-raiz | `formato-extrato.md`; `extrato-prestacao-contas.md`; OC-18 (vale a recomendação desde 28/10 se o Financeiro não responder) |
| R12 | Extrato mostra **só dados do próprio parceiro**; não expõe comissões internas (vendedor, gestor, coordenador) nem margem da Save | Isolamento por parceiro (filtro no servidor) | `formato-extrato.md` |
| R13 | Linguagem: "**remuneração por indicação comercial e por serviços de apoio**", nunca "divisão/repasse de honorários" em texto externo `[VALIDAR JURÍDICO]` | Glossário fixo nas telas externas | Lei 8.906/94, art. 34; `depto-operacoes-canal/SKILL.md` regra 5 |
| R14 | **Registro de oportunidade** (proposta v1, não aprovada): unidade = raiz do CNPJ; registro válido = card completo com evidência; vale data/hora do card; **90 dias + 60** de prorrogação com avanço; ganho protegido enquanto houver contrato **+ 12 meses**; tese nova com preferência de 15 dias; desempate em 4 níveis; divisão só como exceção, **nunca duas remunerações integrais**; não retroage. Conflita com "180 dias" citado em `juridico-revisao.md` | Fluxo de registro com status, validade, prorrogação e desempate | `departamentos/operacoes-canal/Proposta-Regra-Registro-e-Politica-Repasse-2026-09-29.md`; R1–R3 pendentes do Luis |
| R15 | **Conflito de canal é decisão do Luis**; o agente mostra fatos (1º registro, ganhos, teses) e a regra proposta, não atribui cliente | Fila de conflito com decisão humana registrada | D98 (alçada); `depto-operacoes-canal` regra 6 |
| R16 | Registro é **proteção temporária de oportunidade, não zona exclusiva** (exclusividade não se presume; CC arts. 726–728; Lei 4.886, art. 31) | Sem "território exclusivo" no PRM; textos do termo revisados | `registro-conflito-canal.md` §3 |
| R17 | **Reserva interna de 45 dias** do lead da BDR para um Master e **SLA de aceite de 3 d.u.** (lead parado volta à Jenifer) | Distribuição de leads com aceite | `celula-jenifer/SKILL.md`, subagente 9 |
| R18 | **Clientes sem Master** pertencem a outra área: fora das listas e do PRM da Partners | Filtro de escopo | D76 |
| R19 | **Produtos em validação** (Crédito Internacional, Maquila, captação, home equity, turnkey) só como **descoberta** até o G2: sem taxa, prazo, fee, condição, simulação ou material ao parceiro; 0 h do time até o G2 | Catálogo do PRM com estado "descoberta"; peças bloqueadas | D83, D30, D35, D49, D52, D108 (pendente); `equipe.md` (checklist do Revisor) |
| R20 | Produtos **prontos** ao parceiro: recuperação (T01–T17), recorrência, Gestão de Passivo, produtos jurídicos, planejamento e reforma, estruturação patrimonial ("não holding"), Gestão de Contas, antecipação e FIDC (Save Invest), tax internacional | Catálogo com dono por produto | `docs/portfolio-2027/matriz-agentes.md`; CLAUDE.md §3 (Luis, 19/10); D92 |
| R21 | **Nunca prometer valor, prazo ou êxito**; todo texto externo passa pelo auditor (`skills/depto-qualidade/scripts/auditar_texto.py`; `lib/protecao.py`, erro = reprovado) | Portão do auditor em toda mensagem, dossiê e peça que o PRM gerar | CLAUDE.md §3; D28; `lib/protecao.py` |
| R22 | **Alíquota zero só via PER, nunca DCOMP**; tese com risco declarado ao lado | Regra do auditor e dos módulos da Academia | D14, D22; `depto-tributario/references/entendimento-save.md` |
| R23 | T13 e T16 fora da vitrine; Funrural (T19 × Gestão de Passivo) em conciliação; antecipação sobre venda gerencial e escrow só presencialmente | Catálogo e frases permitidas por produto | D80, D81/D86/D103, D82; D39 (pendente) |
| R24 | **LGPD:** dado de cliente fica no Mac; contatos de sócios só em `dados-publicos/receita/prospects-contatos.json` (600); CPF, RG, CNH e dados bancários **nunca** no painel nem no chat; dado bancário do parceiro é do Financeiro; mínimo necessário; mascaramento | PRM sem campos bancários/pessoais sensíveis; trilha de acesso; retenção definida | CLAUDE.md §3; `infra/glpi-regras.md` (LGPD); `lib/protecao.py`; `depto-operacoes-canal` regra 7 |
| R25 | **Cliente da Save consultado por parceiro não é revelado**: checagem por HMAC; resposta neutra única ("Não foi possível seguir com esta consulta. Fale com a Área Partners.") | Mesmo padrão no registro de oportunidade externo (evitar enumeração da carteira) | `central/README.md`; decisão do Luis de 23/10 (SESSOES §22) |
| R26 | **HubSpot e GLPI: só leitura e rascunho**; nada enviado sem aprovação; criação de campo é do time de CRM | PRM lê o HubSpot; escrita só por proposta aprovada (ou após liberação do dono do CRM) | CLAUDE.md §3; D18; D26; D29 |
| R27 | **Sem ranking público** de parceiros nem de pessoas do time; nível comunicado individualmente (decisão do Luis) | Carta de nível individual; nada de leaderboard | `depto-partner-success/references/boas-praticas.md`; `gestor-niveis-jornada.md` §4 |
| R28 | Programa Partners 2027: níveis **Master Estratégico / Avançado / Master** em líquido Save de todos os produtos, sem café, janela de 12 m, apuração trimestral; **2027 só benefícios não financeiros (opção A)**; repasse e fila técnica não mudam; ninguém começa abaixo; só sobe nas 4 primeiras apurações | Módulo de níveis em "leitura-sombra" | `departamentos/produtos/credito-internacional/25-programa-partners-2027.md` v1.1; F8 (pendente) |
| R29 | Publicidade de parceiro remunerado identifica a relação (guia do CONAR de 12/05/2026), texto validado pelo Jurídico | Kit co-branded com selo | PS-15; `equipe.md` |
| R30 | **Café fora** da meta e das contas desde abr/2026 | Filtro em métricas e níveis | Regra do Luis (20/08/2026); `mapeamento-hubspot.json` |
| R31 | Alçada: a Daniela aprova o que é dela (demandas, retorno ao parceiro dentro das frases permitidas, plano de conta, QBR); sobe ao Luis preço, repasse, meta, conflito, frase nova, produto em validação, > R$ 1 mi de crédito com decisão | Papéis e aprovações no PRM | D98; `infra/alcadas.md`; `celula-daniela/SKILL.md` |

---

## 4. Dados disponíveis hoje para cada módulo, e lacunas

### 4.1 Fonte: HubSpot (só leitura, download diário em `departamentos/resultados/dados/hubspot-AAAA-MM-DD.json`; 5.051 negócios em 26/10)
**Funis (negócios):** RT – Real & Presumido (4.733: 1.691 ganhos, 2.714 perdidos, cerca de 328 abertos em 12 etapas, de "Novo Negócio" a "Contrato Assinado"), Gestão de Passivo (212), RT – Simples Nacional (58), Save Partners – BDR/SDR (25), Produtos Tributários (7), Produtos Jurídicos (6), Planejamento Tributário (5), Save Partners – Closer (4), Enriquecimento (1).

**Campos usados** (`mapeamento-hubspot.json`; dicionário em `skills/depto-dados/references/especialistas/governanca-dicionario.md` §2):
| Uso no PRM | Campo | Situação |
|---|---|---|
| Parceiro | `nome_do_parceiro` (texto livre: empresa **ou** consultor) | Normalizado por roster e aliases (`aliases-parceiros.json`, `config-canal.json`); deveria ser lista |
| Quem indicou | `email_de_quem_esta_indicando_o_leadcliente`, `nome_de_quem_esta_indicando_o_lead_cliente` | Existe; preenchimento não medido |
| Empresa | `cnpj_` (aceitar alfanumérico, IN RFB 2.229/2024; `lib/cnpj.py`), `estado`, `cidade`, `porte_da_empresa`, `qual_e_o_regime_tributario_da_empresa_`, `faturamento`, `descricao_do_cnae`, `cnae` | Existe |
| Etapa e tempo | `dealstage`, `hs_v2_date_entered_current_stage`, `notes_last_updated`, `closedate`, `createdate` (regravada nas importações de nov/2025 e fev/2026: usar "data efetiva") | Existe |
| Remuneração | `honorarios_contratuais` (% honorário, só no ganho), `honorarios_parceiro` (% parceiro), `honorarios_vendedor/gestor_comercial/indicador`, `honorariosdo_coordenador` | % honorário vazio em 57,3% dos ganhos; outras comissões sem regra (OC-5) |
| Tese | `teses_tributarias_aplicadas_neste_negocio_` | Obrigatória no ganho (D73); incompleta |
| Execução e documentos | `id_bitrix`, `e_cac_liberado_`, `parecer_complementar`, `anexo_do_diagnostico`, `parecer_juridico` | Existe; arquivos do HubSpot sem escopo `files` |
| Formulário de oportunidade | "Novas Oportunidades" (form 71224d09…; `id_do_parceiro` de 7 dos 9 Masters em `infra/oportunidade-form.json`) | Existe; envio pelos agentes bloqueado até o Luis liberar |
| WhatsApp | Atividades WHATS_APP gravadas pelo Eazybe | Leitura pelos scripts da célula |

**Lacunas no HubSpot (bloqueiam módulos):** `recebido` (R$) **não existe** (0 de 1.696; P5/D18) → sem extrato real; **Produto** não existe (D37/D57) → sem funil por produto nem cross-sell; `data_entrada_parceiro`, `master_padrinho`, `nivel_parceiro`, certificações, `motivo_dormencia` não existem (PS-11); cadastro do parceiro como **objeto/empresa** com termo, % e vigência não existe (o % vive no card); data de protocolo e situação do PER fora do HubSpot; contato do parceiro e dados bancários fora (por regra).

### 4.2 Scripts e arquivos que já calculam o que o PRM precisa
| Módulo do PRM | Script / arquivo existente | Saída |
|---|---|---|
| Ficha 360 do parceiro | `skills/celula-daniela/scripts/briefing_master.py --master X [--negocio id]` | Pipeline por etapa, ganhos/perdidos, parados, qualidade do CRM, pendências |
| Saúde do parceiro | `skills/depto-dados/scripts/dados_bi.py` → `departamentos/dados/dados-bi-*.json` | Índice 0–100 com 4 componentes (ritmo de entrada 30, conversão 25, ritmo de valor 25, qualidade do dado 20) |
| Ativação, classes, tempo até o 1º ganho, níveis simulados | `departamentos/partner-success/scripts/metricas_ps.py` | `metricas-ps-*.json/xlsx` (abas Conferência e Simulação de níveis) |
| Repasse / comissionamento | `skills/depto-operacoes-canal/scripts/conferencia_repasses.py` (+ `references/checagens-repasse.md`, códigos C/O/I) | `departamentos/operacoes-canal/conferencia-repasses-*.json/xlsx` por parceiro |
| Conflito de canal / registro | `skills/depto-operacoes-canal/scripts/conflito_canal.py`; `skills/celula-daniela/scripts/crm_checagem.py --cnpj` (duplicidade, conflito, Receita, Simples) | `conflito-canal-*.json/xlsx`; proposta de CRM |
| Demandas e SLA | `lib/registro_demandas.py` (ID D-AAAA-NNNN); `celula-daniela/scripts/pendencias.py` + `references/sla.json` (23 tipos, proposta); `demandas_whatsapp.py`, `whatsapp_hubspot.py`, `lib/eazybe.py` | `registro/demandas.json`, `Controle-Pendencias-Masters.xlsx` |
| Resposta antes do chamado | `lib/historico.py avaliar` (7.407 documentos) | Resposta do histórico sem GLPI |
| Chamados às áreas | `chamados_whatsapp.py` → `lib/chamados_painel.py` → `lib/glpi.py` (rascunho até o OAuth) | Chamado aprovado no painel |
| Medição de respostas ao parceiro | `lib/medicao_respostas.py` (D28) | `registro/medicao-respostas.json` |
| Alertas e plano do dia | `lib/operacao.py` (sentinelas contrato_parado, parceiro_inativo, conflito_novo, crm_incompleto…); `lib/caixa.py` (caixa de entrada nos painéis) | `registro/eventos.json`; coleção `caixa` |
| Prospecção e leads para o parceiro | `skills/celula-jenifer/scripts/lista_master.py` (lista por Master × segmento × UF, reservas, conflito); `followup.py`; piloto em `skills/celula-jenifer/scripts/prospeccao_ds/` | `Lista-<Master>-*.xlsx` |
| "Mapa da sua carteira" do parceiro | `skills/depto-solucoes/scripts/mapa_base_parceiro.py` (CSV do parceiro × ecossistema; questionário de 8 perguntas); `mapa_conta.py` (clientes ganhos) | Excel por parceiro (protótipo, exemplo fictício em `docs/ecossistema/exemplo/`) |
| Consulta de Lucro Real + dossiê para o parceiro | `central/` (`consulta_demo.py`, `api/central_api/regime.py`, `negocio_ativo.py`, `esteira.py`, `dossie_base.py`; 154 testes) | Dossiê de 9 seções em tela e Word |
| Recuperação de perdidos (oferta ao parceiro) | skill `recuperador` | Fila (318) e lote semanal |
| Metas e gestão do canal | `infra/gestao.py`, `infra/controle.py`; `registro/gestao/pacote-*.json` (meta por Master como proposta, não aprovada) | Semáforo, desvios |
| Saneamento | `skills/depto-dados/scripts/ganhos_a_completar.py`, `saneamento_duplicados.py` | Listas para o CRM |
| Visual | `lib/marca.py`, `departamentos/marketing-marca/padrao/` (Design System Save v0.5) | — |

### 4.3 Lacunas que nenhum script cobre
Fonte de recebimentos por negócio (Financeiro); termos dos 9 Masters digitalizados com % e vigência (Contratos); cadastro de contatos do parceiro com base legal; biblioteca de materiais aprovada (Marketing; cases aprovados = nenhum); conteúdo validado da Academia (Tributário/Jurídico); data de entrada e certificação; identidade externa dos parceiros (Entra B2B × External ID); NPS do parceiro (`depto-qualidade` tem o método, sem coleta).

---

## 5. O que já existe e pode virar módulo do PRM; decisões que travam

### 5.1 Painel Central Partners (interno; nenhum parceiro acessa)
- **Links:** painel do time https://claude.ai/artifact/7fgGfrK7zVqzjcXCscJmwb (perfil `time`) e painel próprio do Luis (D100, 23/10/2026). Código: `portal/opcoes/combinada.html` → `portal/opcoes/gerar_index.py` → `portal/index.html`; dados por `infra/portal_dados.py` (`portal/dados.json`, `diretorio.json`; versão time em `portal/time/`). Visual "cockpit escuro" no Design System Save v0.5.
- **Telas (menu):** Caixa de entrada · Minha mesa · Gestão (meta do Q4, semáforo, previsão, desvios, decisões) · Pedidos (catálogo de pedidos aos agentes; Aprovar / Pedir ajuste / Não aprovado) · WhatsApp · Demandas (Respondi / Encaminhei à área / Não é demanda; chamado sugerido "Aprovar e abrir no GLPI") · Áreas ("Fale com esta área") · Onde está · Rotinas · Decisões (Luis). Também o lote do Recuperador (Aprovar para reanálise / Vetar / Precisa de dado) e o scorecard dos Masters nos dados publicados.
- **Base (db do Artifact):** coleções `pedidos`, `acoes_demandas`, `chamados`, `recuperador`, `conselho`, `decisoes`, `apontamentos`, `caixa`, `leituras`; sincronização no Mac por `lib/painel_sync.py`.
- **Quem acessa:** 4 contas (Luis, Daniela, Jenifer, Geovana). `infra/portal-contas.json` hoje tem **só a conta do Luis**; as outras três são confirmadas quando cada uma abrir o painel (`lib/portal_contas.py registrar`; ids desconhecidos viram alerta). Perímetro regulatório: "uso interno, só funcionárias da Save" (`docs/portal/avaliacao-publicacao-2026-10-23.md`). Adoção: 0% até o lançamento (D107 pendente, D0 proposto para 03/11).
- **Destino técnico:** `central/` (Azure Static Web Apps + Functions + Entra ID, D89; 28 testes de token/permissão; etapas 1–2 prontas, 3–6 a fazer). A camada de dados do portal (`Fonte`) foi escrita para trocar o db do Artifact pela API sem mudar telas. Prazo realista de 4 a 8 semanas a partir do dia em que a TI nomear responsável (sem resposta aos pedidos de 30/09, 13/10 e 23/10).

### 5.2 Peças que viram módulos (reaproveitamento direto)
| Módulo de PRM (padrão de mercado) | Peça existente | Estado |
|---|---|---|
| Ficha 360 / gestão de conta (interno) | `briefing_master.py` + saúde `dados_bi.py` + plano de conta e QBR (`gestor-contas-chave.md`: QBR de 60 min, 3 compromissos datados) | Pronto como script; sem tela |
| Registro de oportunidade (deal registration) | Proposta de regra (R14) + `crm_checagem.py --cnpj` + `conflito_canal.py` + checagem HMAC e mensagem neutra do `central/` + formulário HubSpot "Novas Oportunidades" | Regra pendente (R1–R3); código de checagem pronto |
| Portal do parceiro (externo) | `central/`: consulta de Lucro Real, histórico das últimas 30 empresas por parceiro, "Pedir análise e esteira", dossiê de 9 seções, Word sob demanda, portão do auditor, papel "Parceiro" previsto | Demo local; pedido à TI em rascunho (`departamentos/ti/pedido-esteira-parceiros-nuvem.md`); minuta de termos e retenção de 12 meses (`departamentos/ti/minuta-termos-consulta-parceiros.md`) para o advogado |
| Status do negócio para o parceiro ("onde está meu cliente") | Etapa do HubSpot + fase do Bitrix (`lib/bitrix.py`, desligado sem webhook) + respostas de dado objetivo (D28) | Dado existe; exposição externa não decidida |
| Extrato e comissões | `formato-extrato.md` + `conferencia_repasses.py` + calendário e contestação (`extrato-prestacao-contas.md`) + checklist de elegibilidade | Bloqueado pela fonte de recebimentos e por D102/D65 |
| Níveis e jornada (tiering) | `25-programa-partners-2027.md` v1.1, `24-programa-crescimento-parceiro.md` v2.3, simulador; `metricas_ps.py` (Simulação em 26/10: 1 Estratégico, 4 Master, 4 em desenvolvimento, 11 Indicador Registrado, 1 Certificado) | Bloqueado por F8 |
| Onboarding 30/60/90 | `departamentos/partner-success/entregas/2026-09-29-v1/onboarding-30-60-90.md`; metas: D+90 = 1ª apresentação de diagnóstico, 1º ganho em D+120; co-venda nas 2 primeiras indicações | Rascunho; capacidade da Jenifer/Geovana em aberto (PS-12) |
| Academia / certificação (LMS) | `entregas/2026-09-29-v1/academia-trilha-v1.md` (N1/N2, por tese T01–T19 e produto) | Conteúdo com `[VALIDAR TÉCNICO]`; dono humano em aberto (PS-6) |
| Biblioteca de materiais (content hub) | `skills/celula-daniela/references/biblioteca-materiais.md`; kits do `depto-marketing`; Design System | Catálogo como hipótese; cases aprovados = 0 |
| Distribuição de leads (lead sharing) | `lista_master.py` (listas por Master, reserva de 45 d, SLA de aceite de 3 d.u.) | Rodando com a Jenifer |
| Mapa da carteira / cross-sell via parceiro | `mapa_base_parceiro.py`, esteira Destravar caixa → Proteger e controlar → Crescer (`docs/portfolio-2027/jornada-2027.md`, `docs/ecossistema/conexao-base-parceiros.md`) | Protótipo |
| Atendimento / tickets (partner support) | Triagem do WhatsApp + `sla.json` + histórico antes do GLPI + chamados com aprovação | Rodando internamente |
| Comunicação e alertas | `lib/caixa.py`, `lib/operacao.py` (sentinela `parceiro_inativo`) | Rodando internamente |
| Comunidade / Conselho de Parceiros | `skills/depto-partner-success/references/especialistas/gestor-comunidade-eventos.md` (Conselho semestral, webinar "Antes da CBS") | Desenho; orçamento e mandato em aberto (PS-13, PS-14) |
| Métricas do programa | `registro/gestao/pacote-*.json` (bloco "canal"), `metricas_ps.py` | Rodando |

### 5.3 Decisões pendentes que travam partes do PRM
| Decisão | O que trava | Estado e recomendação das áreas | Fonte |
|---|---|---|---|
| **F8** · Programa de Parceiros L1–L10 | Módulo de níveis, carta de nível, regra do CI | Pendente; prazo 14/11. Recomendação: opção A (L4, L8, L10 já; L1–L3, L6 opção 2 e L7 como desenho interno com efeito após o G2; L5 no G2). Também PS-1, PS-2, PS-3, PS-5, PS-16 | `registro/gestao/dossies/F8.json` |
| **D102** · liberar repasse conferido; atípico só com contrato | Extrato, status de pagamento, frase ao Master | Pendente; prazo 30/10. Recomendação: opção A, liberar à medida do recebimento, fichas dos atípicos até 05/12, frase "em conferência contratual" sem valor nem prazo | `dossies/D102.json` |
| **D65** · registro único de exceções de honorário | Regra de cálculo por exceção (ex.: café a 70%) | Pendente; prazo 06/11. Opção A: três tipos (exceção aprovada, erro de campo, sem lastro); inventário dos termos dos 9 Masters | `dossies/D65.json` |
| **D109** · % de honorário preenchido pelo contrato | Completude do repasse | Pendente; prazo 06/11 | `dossies/D109.json` |
| **D37** (e D57) · propriedade "Produto" | Funil por produto, cross-sell, catálogo multiproduto no PRM | Pendente; prazo 06/11. Opção A: lista fechada só com prontos; CI/MQ depois do G2 | `dossies/D37.json` |
| **R1–R3** · regra de registro de oportunidade | Módulo de registro e conflito | Pendente do Luis desde 29/09 (mais 90+60 × 180 dias com o Jurídico) | `Proposta-Regra-Registro-e-Politica-Repasse-2026-09-29.md`; OC-11 a OC-13 |
| **P1–P5** · natureza jurídica, base bruto × líquido, retenções, outras comissões, fonte de recebimentos | Extrato e pagamento | Pendentes (Jurídico, Financeiro, Tributário, Luis) | mesma proposta; OC-1 a OC-10, OC-16 |
| **G2** (15/12) e D108 (0 h do time até o G2) | Família CI e produtos em validação no catálogo do PRM | D30–D39 e D49–D60 congelados; D108 pendente | `dossies/D108.json`, `D38.json` |
| **D39** · "o que não dizer" por produto | Frases permitidas nas telas externas | Pendente; recomendação: aprovar | `dossies/D39.json` |
| **Contas e acessos** | Uso real do painel e do PRM | 3 contas do time a confirmar (D100); TI sem responsável para Entra/SWA; login dos parceiros (convidado B2B × External ID) a decidir com a TI | `infra/portal-contas.json`; pedido à TI, item 3.3 |
| **Consulta do parceiro** (SESSOES §22) | Portal externo | O CNPJ digitado pode sair para API externa?; só 9 Masters ou também indicadores; modo autônomo só após 30 dias com amostra de 20%; parecer de perímetro da OAB; termos de uso e retenção | `gabinete/SESSOES.md` §22 |
| **D75** · meta 2027 da diretoria | Patamares em R$ dos níveis e metas por Master | Pendente da diretoria | PS-3 |
| **D107** · D0 do lançamento ao time | Adoção do painel interno (base da fase 1 do PRM) | Pendente; D0 proposto 03/11 | `dossies/D107.json` |
| Escrita no HubSpot | Registro feito pelo próprio parceiro / sincronização | Só leitura e rascunho; liberação do dono do CRM | CLAUDE.md §3; D18 |

---

## 6. Métricas de canal atuais (valor e data)

| Métrica | Valor | Data da base | Fonte |
|---|---|---|---|
| Masters no roster / ativos em 90 dias | 9 / 9 | 26/10/2026 | `pacote-2026-10-26.json` (`masters_ativos_90d`) |
| Consultores dos Masters (total / ativos e produtivos / dormentes / inativos) | 27 / 9 / 10 / 8 → **18 dormentes ou inativos** | 26/10/2026 | `pacote` (`consultores_dormentes`) |
| Consultores com 1 só ganho (esperando o 2º) | 16 de 45 com ganho (29 com 2+) | 26/10/2026 | `pacote` (`consultores_sem_2o_ganho`) |
| Parceiros fora do roster (total / ativos 90 d / dormentes / inativos) | 12 / 2 / 3 / 7 | 26/10/2026 | `metricas-ps-2026-10-26.json` |
| Tempo até o 1º ganho (parceiros medidos) | n = 4, mediana 121,5 dias, p75 152 | 26/10/2026 | `metricas-ps` |
| Concentração: maior Master no fechado 12 m (crédito) | 34,8% | 26/10/2026 | `pacote` (`dependencia_top1_pct`) |
| Concentração: **top 5 Masters** no fechado 12 m | **90,6%** | 26/10/2026 | idem |
| Concentração em líquido Save (12 m, sem café): 3 maiores / parceiros efetivos / CV trimestral | 81,1% / 3,3 / 0,58 | HubSpot de 07/10/2026 | `departamentos/produtos/credito-internacional/24a-diagnostico-concentracao.md` |
| Masters com ritmo de valor em queda > 20% | 5 Masters, R$ 101,8 mi de líquido potencial 12 m | 26/10/2026 | `pacote` (`masters_liquido_em_queda_rs`) |
| Margem líquida por Master (menor / carteira) | 7,6% / 17,35% | 26/10/2026 | `pacote` (`margem_liquida_por_master_min`) |
| **Win rate** (3 meses) | **26,0%** (amarelo; verde ≥ 30%) | 26/10/2026 | `pacote` (`win_rate_3m`) |
| Win rate 12 m por pipeline | RT Real & Presumido 27,4%; Gestão de Passivo 1,1%; Simples 0%; BDR/SDR 0% | 26/10/2026 | `pacote` (`prob_real_x_configurada`) |
| Probabilidade real ÷ configurada no CRM | 0,56× (forecast do CRM otimista) | 26/10/2026 | idem |
| Ticket médio (crédito por ganho, 3 m) | R$ 845 mil | 26/10/2026 | `pacote` |
| Negócios criados no mês × mesmo período de setembro | 148 × 261 (−43,3%) | 26/10/2026 | `pacote` |
| Fechado no mês (crédito) / meta de outubro (D111) | R$ 16,4 mi de R$ 75 mi (21,9%); Q4 em 6,6% de R$ 250 mi | 26/10/2026 | `pacote` (`meta_mes_pct`, `meta_q4_pct`) |
| Pipeline aberto / parado > 90 dias | R$ 123,7 mi / R$ 3,9 mi (22 negócios) | 26/10/2026 | `pacote` |
| Clientes com 2+ produtos | 1,4% (14 de 1.026 raízes) | 26/10/2026 | `pacote` |
| Ganhos sem % de honorário | 57,3% (965 de 1.685) | 26/10/2026 | `pacote` |
| Índice de qualidade dos ganhos | 74,6% | 26/10/2026 | `pacote` |
| Repasse: ganhos Bloqueado / Revisar / OK | 1.047 / 217 / 432 (de 1.696) | 26/10/2026 06h53 | `conferencia-repasses-2026-10-26.json` |
| Repasse calculável / só OK | R$ 118,9 mi / R$ 69,2 mi | 26/10/2026 | idem |
| Ganhos com recebimento registrado | 0 | 26/10/2026 | idem |
| Conflito de canal: raízes com > 1 canal / Alta / Master × Master | 82 / 19 / 3 (R$ 483,6 mi envolvidos) | 26/10/2026 | `conflito-canal-2026-10-26.json` |
| Ciclo do ganho (criação → ganho) | mediana 35 dias, p75 69, p90 161; 81,0% em até 90 dias | 26/10/2026 | idem (`ciclo`) |
| Demandas registradas (30/09–23/10) | 125, 96% pelo WhatsApp | 23/10/2026 | `registro/demandas.json` |
| Espera do parceiro por resposta (mediana / p90) | 7,9 h / 23,6 h | 29/09–26/10/2026 | `celulas/whatsapp-triagem-*.json` |
| Tempo até a resposta pronta (agentes) | mediana 7,2 h; 13 abertas; maior espera 24,7 h | 26/10/2026 | `pacote` (`tempo_resposta_parceiro_h`) |
| Chamados GLPI abertos pelo time | 749 de 1.115 (67%) | 25/11/2025–01/10/2026 | `infra/glpi-regras.md` |

**Benchmarks já levantados internamente** (para a pesquisa de mercado não repetir): onboarding de 60–90 dias com estrutura × 6–12 meses sem (`boas-praticas.md`, 29/09); registro de oportunidade quase triplicou a taxa de fechamento (Channelscaler, 13/08/2026; radar 2.5); deal registration de 90 dias (Veeam, IGEL, CTOUCH; `registro-conflito-canal.md`); Canalys (benefícios mais valorizados: rebates, registro, leads, gestão de conta); Futurum 1S2026 (co-venda prioridade nº 1, 39,2%); Cora (R$ 200 por conta ativada; níveis 9/25/50/150); níveis da Microsoft e da AWS. Não localizados com fonte confiável: % de parceiros ativos, tempo até o 1º negócio, comissão de indicação para contadores (radar 2.7).

---

## O que você também precisa (para o desenho)
- O PRM da Save não é de revenda: o parceiro **indica e abre a porta**; a Save executa. O negócio vive meses depois do ganho (PER, compensação, recebimento), então o PRM precisa de **pós-ganho** (execução e remuneração), que os PRMs de software tratam pouco.
- Duas audiências com dados diferentes: **interno** (todo o canal, margem, conflito) e **externo** (só o próprio parceiro, sem margem, sem comissões internas, sem revelar cliente da Save).
- Primeira fase viável sem TI: interna, no painel atual, lendo scripts que já existem. O portal externo depende de TI (Entra/SWA), Jurídico (termos, OAB, LGPD) e das decisões R1–R3, D102, D65 e F8.

## O que falta e quem fornece
| Falta | Quem |
|---|---|
| Fonte de recebimentos por negócio | Financeiro + time de CRM (P5, D18) |
| Termos dos 9 Masters com % e vigência | Contratos (D65) |
| Regra de registro R1–R3 e conflito | Luis (+ Jurídico na validade) |
| Natureza jurídica (indicação × representação) e linguagem | Jurídico (P1, OC-16) |
| Propriedades Produto, data de entrada, nível, certificação | Time de CRM com Dados (D37, PS-11) |
| Identidade externa dos parceiros e hospedagem | TI (pedido 3.3; D89) |
| Programa L1–L10 e comunicação de nível | Luis (F8, PS-5) |
