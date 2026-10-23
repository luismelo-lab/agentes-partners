# Matriz de roteamento: tema → áreas

> **Vigente desde 22/10/2026.** As seções 0 e 0.1 abaixo (portfólio P1 a P18 e limites de nível) prevalecem sobre as atualizações antigas quando divergirem. Mudanças: Save Invest dona de Gestão de Contas, antecipação e FIDC (D92); Soluções só com esteira e mapa da conta; produtos em validação só como descoberta (D83); cliente sem Master fora da Partners (D76). Método completo do Roteador: `especialistas/roteador.md`.

## 0. Portfólio 2027 → áreas (fonte: `docs/portfolio-2027/matriz-agentes.md`, com a D92)
| # | Produto | Estado | Constrói (O) | Valida (O) | Opcional (o) | Nível típico | Escalar a humano |
|---|---|---|---|---|---|---|---|
| P1 | Recuperação tributária (T01 a T17; T13 e T16 fora da vitrine, D80) | Pronto | `depto-tributario`, `recuperador` | `depto-juridico` (compensação), `depto-qualidade` (se sai para fora) | `revisor-diagnostico`, `apresentacao-diagnostico` | 1–2 | 👤 Técnico valida; alíquota zero só via PER |
| P2 | Recorrência (novas competências) | Pronto | `depto-tributario`, `depto-pos-venda` | `depto-juridico` | `recuperador` | 2 | 👤 Técnico; decadência de 5 anos |
| P3 | Crédito presumido de PF e Funrural (T18, T19) | Pronto (T19 a conciliar: D81 × D86) | `depto-tributario` (Agro) | `depto-juridico` | — | 2–3 | 👤 Luis decide D81 × D86 |
| P4 | Gestão de Contas (cobrança, escrow, e-CAC) | Pronto · Save Invest | `depto-save-invest` | `depto-juridico`, `depto-qualidade` | `depto-solucoes` (só encaixe na esteira) | 2 | 👤 Junior |
| P5 | Gestão de Passivo (inclui Funrural anterior a 2018, D86) | Pronto | `depto-juridico` | `depto-tributario` | `depto-pos-venda` (compensação de ofício) | 2–3 | 👤 Jurídico valida até 07/11/2026 (D94) |
| P6 | Passivo bancário, alongamento, carência | Sem ficha | `depto-internacional` | `depto-juridico` | `depto-save-invest` | 4 (próprio × parceiro) | 👤 Luis define dono |
| P7 | Produtos jurídicos | Pronto | `depto-juridico` | `depto-qualidade` | `depto-marketing` | 2 | 👤 Advogado; OAB |
| P8 | Planejamento tributário e reforma (P01) | Pronto | `depto-tributario` (Reforma) | `depto-juridico` | `depto-solucoes` | 2 | 👤 Técnico; CBS em 2027 |
| P9 | Antecipação de recebíveis | Pronto · Save Invest | `depto-save-invest` | `depto-juridico` | `depto-solucoes` | 2–3 | 👤 Junior; só instituição autorizada; venda gerencial e escrow só presencial (D82) |
| P10 | Estruturação patrimonial e empresarial | Pronto | `depto-juridico` | `depto-tributario` | `depto-solucoes` | 2 | 👤 Advogado; dizer "estruturação patrimonial" |
| P11 | Certificado digital e ART | Sem ficha | `depto-solucoes` | `depto-juridico` | — | 4 (próprio × parceiro) | 👤 Luis define dono |
| P12 | Crédito Internacional | Validação · trava G2 | `depto-internacional` | `depto-juridico` (Regulatório & Câmbio) | `depto-operacoes-canal` (conflito) | 3 (4 se for portão ou remuneração) | 👤 João Mattos; sem taxa, prazo ou fee antes de 15/12/2026 |
| P13 | FIDC, FIDIC, multicedente, multissacado | Pronto · Save Invest | `depto-save-invest` | `depto-juridico` (CVM) | `depto-solucoes` | 3 | 👤 Junior; Save não distribui cotas |
| P14 | Home equity | Validação | `depto-internacional` | `depto-juridico` | — | 3 | 👤 João Mattos; só descoberta |
| P15 | Maquila e Paraguai | Validação | `depto-internacional` | `depto-tributario`, `depto-juridico` | — | 3 | 👤 João Mattos; frigorífico bloqueado (D59) |
| P16 | Captação de capital | Validação | `depto-internacional` | `depto-juridico` (CVM) | `depto-solucoes` (N1) | 3 | 👤 Jurídico antes de qualquer conversa |
| P17 | Internacionalização turnkey | Validação | `depto-internacional` | `depto-juridico` | — | 3 | 👤 João Mattos |
| P18 | Tax internacional e comércio exterior | Pronto | `depto-internacional` | `depto-tributario`, `depto-juridico` | — | 2 | 👤 Paulo e João Mattos |
| N1–N5 | Candidatos (investidor, CFO terceirizado, governança no exterior, sucessão e LGPD, seguros e M&A) | Candidato | — | — | — | 4 | 👤 Conselho decide próprio × parceiro antes da ficha |

**Camada de apoio (entra conforme o caso):** esteira e mapa da conta `depto-solucoes`; ICP `depto-intel-comercial`; peça `depto-marketing`; auditor de promessas `depto-qualidade`; contrato `depto-contratos`; remuneração do parceiro `depto-operacoes-canal`; pós-venda `depto-pos-venda`, `depto-partner-success`; números `depto-resultados`, `depto-dados`; rotina e integração `depto-ti`, `central-agentes`; Masters e prospecção `celula-daniela`, `celula-jenifer`; pessoas `depto-pessoas`.

**Regra de rota por estado:** produto pronto = área dona + validadora + Qualidade se sair para fora, sem Conselho. Em validação = Internacional + Jurídico + perguntas ao João, sem Marketing até o G2, só descoberta. Sem ficha ou candidato = Conselho decide próprio × parceiro. Material externo = todas as áreas envolvidas + auditor + exemplo ao Luis antes da escala.

**Esteira:** Destravar caixa (P1, P2, P3, P4, P5, P9) · Proteger e controlar (P5, P7, P8, P10, P11) · Crescer (P12 a P17, N1) · tax internacional P18 atravessa Proteger e Crescer.

## 0.1 Limites para subir de nível (proposta do Gabinete de 22/10/2026, pergunta G1; vale a recomendação em 28/10/2026 se não houver resposta, `infra/alcadas.md` §2)
| Nível | Qualquer um destes leva a este nível |
|---|---|
| 1 · Consulta | Pergunta de uma especialidade, interna, reversível; sem R$ ou crédito abaixo de R$ 100 mil |
| 2 · Área | Uma área constrói ou valida; crédito até R$ 1 mi ou honorário até R$ 250 mil; um parceiro, sem mudar regra |
| 3 · Comitê | 2 a 4 áreas; crédito acima de R$ 1 mi (régua do rigor N3 de 15/10); contrato, aditivo, distrato; sai para parceiro ou cliente; prazo da Receita; conflito de canal; produto em validação; dado pessoal novo |
| 4 · Conselho | Crédito acima de R$ 10 mi num caso ou honorário líquido acima de R$ 1 mi; 3+ Masters ou um dos 3 maiores (71% do valor); muda repasse, honorário, meta, preço ou dono de produto; portão G0 a G4 (D36); candidato N1 a N5; vai à diretoria |
Âncoras: ticket médio R$ 0,88 mi e win rate de 28,1% (ata de 19/10/2026); concentração top 3 de 71,0%. Pessoa em risco (desligamento, assédio, conflito grave) vai a RH formal e Jurídico humano antes de qualquer agente.

## 0.3 O que sobe ao Luis (alçada de 23/10/2026, `infra/alcadas.md` §1)
O nível (§0.1) diz quantas áreas trabalham; esta tabela diz quem decide. A coluna "Escalar a humano" das tabelas abaixo segue esta regra: onde diz Luis, é porque o caso cai numa linha "Sim".
| Tipo de decisão | Quem decide | Sobe ao Luis? |
|---|---|---|
| Operacional, reversível e dentro das regras (rascunho ao parceiro, lista de prospecção, priorizar lote, encaminhar a outra área, rascunho de CRM, formato de relatório) | Dona da entrega (Daniela, Jenifer, Geovana) com o gerente da área de agentes | Não. Vai no resumo semanal |
| Técnica de caso (tese aplicável, documento a pedir, prazo de despacho) | Time técnico ou advogado humano, com a pré-análise da área | Não, salvo se mudar regra |
| Encaminhamento de produto pronto (Save Invest, Jurídico, tax internacional) | Contas e Soluções, com aviso ao dono do produto | Não |
| Regra, preço, honorário, meta, remuneração de parceiro ou do time, tese na vitrine, frase permitida | Luis (com o Conselho quando valer) | Sim |
| Produto novo ou em validação (condição ao cliente, G0 a G4, parceria) | Luis com o dono do produto | Sim |
| Material externo em escala | Luis vê um exemplo antes | Sim, só o exemplo |
| Irreversível ou com exposição (envio, contrato, assinatura, publicação, gasto) | A pessoa responsável, com aprovação explícita | Conforme a regra da casa |

**Limites que levam ao Luis em qualquer nível:** muda regra; mais de R$ 1 mi de crédito com decisão; 3 ou mais áreas em conflito; produto em validação; risco jurídico ou de LGPD sem precedente na base; nova fonte de dado pessoal; conflito de canal entre Masters ou parceiros; pessoas do time (remuneração, metas, desempenho). Decisão reversível sem dono natural: vale a recomendação da área em 3 dias úteis se não houver resposta (§2); o Luis pode reverter.

## 0.2 Porteiro antes da matriz (regra do Luis de 22/10/2026)
Antes de usar esta matriz: `python3 ~/agentes-partners/infra/ja_existe.py "<pedido>"`. Repetido (nota ≥ 0,60), continuação em outra conversa ou travado → a Ficha de Rota começa dizendo isso e para para o Luis decidir. Relacionado (0,35 a 0,60) → reaproveitar e citar. Novo → seguir e abrir seção no `gabinete/SESSOES.md`. Registrar com `--registrar`.

Legenda: **O** = obrigatória · o = opcional (entra se a condição valer) · 👤 = exige humano antes de agir

## Pessoas
| Necessidade | Nível típico | Áreas | Escalar a humano |
|---|---|---|---|
| PDI, feedback, preparação de 1:1, conversa difícil, reconhecimento | 2 | **O** Pessoas · o Resultados (dados de desempenho) | — |
| Avaliação de desempenho, metas individuais | 2–3 | **O** Pessoas · **O** Resultados (métricas e metas coerentes com a área) · o Comercial (conselheiro) | — |
| Descrição de cargo, plano de carreira, sucessão | 2 | **O** Pessoas · o Jurídico (equiparação salarial, se mexer em cargo/salário) | 👤 RH formal para oficializar |
| Remuneração variável, bônus, comissão | 3 | **O** Pessoas · **O** Resultados (custo e ROI) · **O** Jurídico (CLT, natureza da verba) | 👤 RH + Financeiro |
| Nova vaga / contratação / onboarding | 2–3 | **O** Pessoas · o Resultados (custo × retorno) | 👤 RH formal |
| Desligamento, baixo desempenho grave, conflito, suspeita de assédio | 3–4 | **O** Pessoas · **O** Jurídico (trabalhista) | 👤 **sempre** RH formal + Jurídico real antes de qualquer ação |
| Clima, engajamento, carga do time | 2 | **O** Pessoas · o Resultados (carga por pessoa) | — |

## Comercial e parceiros
| Necessidade | Nível típico | Áreas | Escalar a humano |
|---|---|---|---|
| Plano de ação comercial, direcionamento de mercado | 3–4 | **O** Tributário (teses) · **O** Resultados (números) · o Marketing · o Jurídico (promessas/contratos) · Conselho se for estratégico | — |
| Problema ou renegociação com um parceiro específico | 3 | **O** célula Daniela (histórico do Master) · **O** Resultados (números do parceiro) · o Jurídico (contrato) | 👤 Daniela conduz (operacional); Luis se mexer em repasse, honorário ou conflito entre Masters (§0.3) |
| Recrutar novos parceiros indicadores | 2–3 | **O** Inteligência Comercial · o Marketing · o Jurídico (termo de parceria) | — |
| ICP, segmento/região para prospectar, lead scoring, território | 2 | **O** Inteligência Comercial · o Dados & BI | — |
| Saúde de parceiro, parceiro esfriando, qualidade do HubSpot | 2 | **O** Dados & BI · o célula Daniela | — |

## Técnico e jurídico
| Necessidade | Nível típico | Áreas | Escalar a humano |
|---|---|---|---|
| Dúvida de tese, norma, julgamento | 1 | **O** Tributário | — |
| Pré-análise de oportunidade de cliente | 2 | **O** Tributário · o Jurídico (compensação/risco) | 👤 Técnico Tributário valida |
| Contrato, aditivo, distrato | 2–3 | **O** Jurídico · o Tributário (escopo técnico) · o Resultados (honorário/repasse) | 👤 Advogado valida |
| Notificação/intimação da Receita | 2 | **O** Jurídico (prazos com dupla checagem) · **O** Tributário | 👤 Advogado **no mesmo dia** |

## Comunicação, resultados e operação
| Necessidade | Nível típico | Áreas | Escalar a humano |
|---|---|---|---|
| Material, campanha, post, kit para parceiros | 2 | **O** Marketing · o Tributário (se houver afirmação técnica) · o Jurídico (promessa/captação) | — |
| Relatório ou apresentação de resultados para a liderança | 2 | **O** Resultados · o Conselho (conselheiro de Finanças como revisor) | — |
| Orçamento, custos, ROI de uma iniciativa | 2–3 | **O** Resultados · o conselheiro de Finanças | — |
| Processo, ferramenta, GLPI, automação, IA | 2 | **O** `depto-ti` (desde 29/09) · o conselheiro de Operações & Tecnologia · o Jurídico (LGPD) · o `arquiteto-agentes` (desenho, avaliação e padrão sênior de agentes) | — |

## Regra geral para temas novos
1. Qual área **constrói**? (a mais próxima do tema)
2. Qual área precisa **validar** para não haver erro caro? (dinheiro → Resultados; lei/contrato/pessoas em risco → Jurídico; afirmação técnica → Tributário)
3. Alguma decisão é **irreversível** ou vai à liderança? → nível 3 ou 4.


## Atualização 29/09: áreas novas (v1)
| Tema | Obrigatória | Opcional |
|---|---|---|
| GLPI, integrações, WhatsApp, acessos, segurança, LGPD técnica, inventário de agentes | `depto-ti` | `depto-juridico` (LGPD) |
| Onboarding, capacitação, Academia, níveis de parceiro, parceiro dormente | `depto-partner-success` | `depto-dados`, `depto-marketing` |
| Repasse, comissão, extrato do parceiro, conflito de canal, registro de oportunidade | `depto-operacoes-canal` | `depto-juridico`, `depto-resultados` |
| Contrato, aditivo, distrato, assinatura, conferência de dados | `depto-contratos` | `depto-juridico` |
| Aviso de pagamento, PER deferido, compensação de ofício, guias, saldo de créditos | `depto-pos-venda` | `depto-tributario` |
| NPS, reclamação, ouvidoria, auditoria de promessas em material/mensagem | `depto-qualidade` | `depto-juridico`, `depto-marketing` |
| Demanda de Master, caixa do WhatsApp, briefing de conta | `celula-daniela` | conforme a demanda |
| Prospecção, listas, follow-up, novos indicadores | `celula-jenifer` | `depto-intel-comercial` |
| Revisão de diagnóstico (teses não levantadas) | `revisor-diagnostico` | `depto-tributario` |

## Atualização 16/10: Produtos Internacionais e Financeiros
| Necessidade | Nível típico | Áreas | Escalar a humano |
|---|---|---|---|
| Cliente serve para crédito internacional, funding ou maquila? | 2 | **O** Produtos Internacionais · o Tributário (recuperação que encaixa) · o Operações de Canal (conflito) | 👤 Luis antes de levar ao João |
| Dúvida de produto (garantia, prazo, moeda, IOF, papel da Save) | 1 | **O** Produtos Internacionais · o Jurídico/Tributário (se exigir parecer) | 👤 João quando estiver "a confirmar" |
| Caixa apertado, dívida cara, carteira a receber (Gestão de Contas, antecipação, FIDC: prontos na Save Invest) | 2 | **O** `depto-save-invest` (desde a D92, 22/10) · o Contas e Soluções (só esteira e mapa da conta) · o Resultados | 👤 Junior |
| Home equity, captação de capital | 2 | **O** Produtos Internacionais (em validação com o João) | 👤 João |
| Material ou comunicação de produto novo | 2 | **O** Produtos Internacionais (Guardião do portão) · **O** Marketing · **O** Qualidade · o Jurídico | 👤 só depois do G2 |
| Remuneração do parceiro em produto novo | 3 | **O** Operações de Canal · **O** Produtos Internacionais · **O** Jurídico | 👤 Luis decide |

## Atualização 16/10: Contas e Soluções
| Necessidade | Nível típico | Áreas | Escalar a humano |
|---|---|---|---|
| O que mais o cliente pode contratar, esteira, mapa de valor | 2 | **O** Contas e Soluções · o Tributário · o Jurídico · o Produtos Internacionais (conforme a onda) | — |
| Carteira do Master, QBR, onde crescer | 2 | **O** Contas e Soluções · **O** Resultados · o célula Daniela | 👤 Daniela conduz com o Master |
| Oferta integrada por setor | 3 | **O** Contas e Soluções · **O** Tributário · o Marketing · o Qualidade · o Jurídico | 👤 Luis aprova preço e o exemplo do material em escala (§0.3); o resto fica com Contas e Soluções |

## Atualização 22/10: Central e pedidos do time
| Necessidade | Nível típico | Áreas | Escalar a humano |
|---|---|---|---|
| Pedido do time que a Central não resolve com uma área (cruza 3+ áreas, muda regra, envolve R$ acima de R$ 1 mi ou produto em validação com condição) | 3–4 | sobe da `central-agentes` ao Gabinete (critério em `skills/central-agentes/references/especialistas/triador-pedidos.md`) | 👤 Luis quando bater um limite da §0.3; se for só cruzar áreas sem conflito, o Gabinete consolida e segue com aviso |
| Desenhar, avaliar ou evoluir um agente; padrão sênior; ROI de IA | 2 | **O** `arquiteto-agentes` · o `depto-ti` · o `depto-resultados` (ROI) | — |
