# Boas práticas de programas de parceiros → o que entrou no departamento

Pesquisa de 29/09/2026 (fontes de mercado sobre PRM, tiering e enablement; lista no fim). Síntese aplicada à Save, onde o "parceiro" é um escritório contábil que **indica** (não executa) e o produto é técnico e tem risco.

## O que a pesquisa diz
1. **Os primeiros 90 dias decidem a produtividade.** Sem onboarding estruturado, um parceiro leva de 6 a 12 meses para produzir; com onboarding, de 60 a 90 dias. Padrão de mercado: D1–30 administrativo + certificação; D31–60 plano conjunto e mapeamento de carteira; D61–90 1º negócio registrado e 1ª venda conjunta; depois, QBR trimestral.
2. **Tempo até o 1º negócio é o indicador de ativação.** Programas maduros acompanham indicadores antecedentes (treino concluído, leads registrados) e consequentes (receita via parceiro, conversão, tempo até o 1º negócio, retenção).
3. **Níveis (tiers) combinam três eixos:** desempenho (receita/negócios), capacidade (certificações) e engajamento/qualidade (registro de oportunidades, dados, satisfação). Critérios **públicos**, com o parceiro vendo o próprio progresso; revisão periódica e regra clara de rebaixamento.
4. **Certificação como porta:** trilhas modulares por função, curtas (a certificação de vendas deve caber em menos de um dia) e ligadas a benefícios (ex.: só parceiro certificado acessa X).
5. **PRM:** portal, registro de oportunidade, biblioteca, trilhas e scorecard num só lugar. Na Save, o "PRM leve" é o **HubSpot** (propriedades de nível, entrada e certificação) + a biblioteca da célula da Daniela.

## Decisões de desenho (incluir · fundir · não duplicar)
| Proposta | Decisão | Por quê |
|---|---|---|
| Analista de Saúde "recalcula" saúde | **Não duplicar:** lê o `dados_bi.py`; soma só a ativação (`metricas_ps.py`) | O índice já existe no Depto Dados; duas fórmulas geram dois números |
| Enablement de vendas em dois lugares | **Separar por natureza:** PS = capacidade (trilha, certificação, roleplay); Marketing = peça (pitch, one-pager, card de objeções) | Evita dois donos do mesmo material; a Academia aponta para a peça do Marketing |
| ★ Revisor de Promessas & Compliance | **Incluído** | Regra 3 dos departamentos (revisor em todo departamento) + risco de promessa de êxito em serviço tributário |
| ★ Plano de negócios conjunto (JBP) para Master Estratégico | **Incluído como modelo, executado pela célula da Daniela** (fundido ao "Plano de Conta" dela) | Boa prática para o topo da pirâmide; não criar papel novo |
| ★ Conselho Consultivo de Parceiros (PAC), semestral | **Incluído como benefício** do nível Estratégico, conduzido pelo Gerente | Escuta estruturada dos melhores parceiros; custo baixo |
| ★ QBR trimestral com cada Master | **Incluído** na régua do Gerente (pauta automática com os números do script) | Padrão pós-90 dias |
| Coach de Onboarding + Academia | **Mantidos separados** | Um desenha o conteúdo (uma vez); o outro acompanha cada parceiro (sempre) |
| Níveis & Benefícios + incentivos | **Desenho aqui** (inclusive SPIFF, como o `depto-operacoes-canal` já declarou); **cálculo, pagamento e política de repasse** no `depto-operacoes-canal`; incentivo financeiro só com Jurídico | Remuneração tem risco jurídico (art. 34 da Lei 8.906/94); v1 fica só com benefícios não financeiros |
| NPS do parceiro e auditoria de promessas | **Não duplicar:** `depto-qualidade` (NPS pós-onboarding e `auditar_texto.py`); o Revisor daqui roda o script deles | Já construído lá |
| Recrutamento de indicadores | **Fora:** Intel Comercial + célula Jenifer; PS começa na assinatura | Evita dois donos do funil |
| MDF (verba de marketing para parceiro) | **Não incluir na v1** | Sem orçamento definido; revisitar com Marketing/Resultados |
| Gamificação/ranking público de parceiros | **Não incluir na v1** | Os Masters têm portes muito diferentes; ranking público pode desmotivar. Nível é comunicado individualmente |

## Fontes
- Magentrix, *Partner Onboarding: The Complete Guide to Ramping Channel Partners* — https://www.magentrix.com/blog/partner-onboarding-the-complete-guide-to-ramping-channel-partners-fast
- Unifyr, *Partner onboarding best practices* — https://www.unifyr.com/blog/9-partner-onboarding-best-practices/ · *Partner Tiers* — https://www.unifyr.com/atlas/partner-tiers/
- Introw, *Partner Enablement Best Practices* — https://www.introw.io/blog/partner-enablement-best-practices · *Certification programs* — https://www.introw.io/blog/how-certification-programs-improve-partner-engagement
- Kiflo, *Partner program tiers* — https://www.kiflo.com/blog/partner-program-tiers
- PartnerStack, *Programmatic partner tiering* — https://partnerstack.com/glossary/programmatic-partner-tiering
- Impartner, *90-Day Partner Manager Onboarding Plan* — https://impartner.com/resources/i/1540553-90-day-partner-manager-onboarding-plan-template
