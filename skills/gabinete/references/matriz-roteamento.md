# Matriz de roteamento: tema → áreas

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
| Problema ou renegociação com um parceiro específico | 3 | **O** célula Daniela (histórico do Master) · **O** Resultados (números do parceiro) · o Jurídico (contrato) | 👤 Luis conduz |
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
| Processo, ferramenta, GLPI, automação, IA | 2 | conselheiro de Operações & Tecnologia (provisório até existir o depto de TI) · o Jurídico (LGPD) | — |

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
| Caixa apertado, dívida cara, carteira a receber (Gestão de Contas, antecipação, FIDC, home equity) | 2 | **O** Produtos Internacionais (Analista do Ecossistema) · o Resultados | — |
| Material ou comunicação de produto novo | 2 | **O** Produtos Internacionais (Guardião do portão) · **O** Marketing · **O** Qualidade · o Jurídico | 👤 só depois do G2 |
| Remuneração do parceiro em produto novo | 3 | **O** Operações de Canal · **O** Produtos Internacionais · **O** Jurídico | 👤 Luis decide |

## Atualização 16/10: Contas e Soluções
| Necessidade | Nível típico | Áreas | Escalar a humano |
|---|---|---|---|
| O que mais o cliente pode contratar, esteira, mapa de valor | 2 | **O** Contas e Soluções · o Tributário · o Jurídico · o Produtos Internacionais (conforme a onda) | — |
| Carteira do Master, QBR, onde crescer | 2 | **O** Contas e Soluções · **O** Resultados · o célula Daniela | 👤 Daniela conduz com o Master |
| Oferta integrada por setor | 3 | **O** Contas e Soluções · **O** Tributário · o Marketing · o Qualidade · o Jurídico | 👤 Luis aprova |
