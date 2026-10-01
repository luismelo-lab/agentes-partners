# Dicionário de métricas — Área Partners (v1, 28/09/2026)

> Regra de ouro: **a fórmula não muda entre semanas.** Se precisar mudar, registre a versão e recalcule o histórico.
> Todo número tem **fonte, data do dado e cobertura** (quantos negócios entraram no cálculo).
> Separe sempre **potencial** (contratado) de **realizado** (reconhecido/recebido). Nunca some crédito estimado do cliente como se fosse receita da Save.

## Glossário dos campos (modelo de margem do S&OE, por negócio)
| Campo | Significado |
|---|---|
| `valor` | Valor do negócio no HubSpot = crédito estimado/recuperável do cliente |
| `hContr` | % de honorário contratual da Save sobre o valor |
| `totalHon` | Honorário bruto da Save = valor × hContr |
| `hParc` | % do honorário que vai ao parceiro |
| `repasse` | Honorário do parceiro = totalHon × hParc |
| `saldoSave` | Honorário líquido da Save = totalHon − repasse |
| `margem` | Margem líquida sobre o valor = saldoSave ÷ valor |

---

## Nível 1: as 9 métricas pedidas pelo Luis (semanal)
| # | Métrica | Fórmula | Base de comparação |
|---|---|---|---|
| 1 | **Volume de negócio criado** | Nº e R$ (Σ valor) de negócios criados no período | Semana anterior · mesmo período do mês anterior · meta |
| 2 | **Volume de negócio fechado** | Nº e R$ de negócios **ganhos** no período (e, ao lado, perdidos) | Idem |
| 3 | **Margem de cada negócio** | Honorário bruto Save (R$) = totalHon; % = hContr | Média ponderada da carteira |
| 4 | **Margem líquida de cada negócio** | saldoSave = totalHon − repasse; % = saldoSave ÷ valor | Idem |
| 5 | **Lucro da área** | Σ saldoSave − impostos sobre a receita (alíquota × Σ totalHon) − custos da área do período. IR/CSLL mostrados à parte (dependem do regime da empresa) | Meta de lucro |
| 6 | **Fator de crescimento** | Valor do período ÷ valor do período anterior (ex.: 1,25x) | Semana, mês (MoM), ano (YoY), acumulado no ano |
| 7 | **% de crescimento** | (Fator − 1) × 100 | Idem |
| 8 | **ROI total** | (Σ totalHon − custos da área) ÷ custos da área | Em 3 versões: potencial · ajustado ao risco · realizado |
| 9 | **ROI líquido** | Lucro da área ÷ custos da área | Idem |

**ROI em 3 versões (obrigatório):**
- **Potencial:** sobre o honorário **contratado** (negócios ganhos).
- **Ajustado ao risco:** contratado × (1 − taxa de glosa da tese) × probabilidade de êxito.
- **Realizado (oficial):** sobre o honorário **recebido** no período. Enquanto não houver dado de recebimento, marque "[sem dado de caixa]", nunca substitua pelo potencial.

## Nível 2: recomendadas (o que todo dono olha)
| Métrica | Fórmula | Por que o dono olha | Frequência |
|---|---|---|---|
| **Receita em 4 camadas** | Contratado · ajustado ao risco · reconhecido · recebido | Mostra se volume vira dinheiro | Semanal / mensal |
| **Backlog** | Honorário contratado ainda não recebido (com aging: < 6m, 6–12m, 1–3a, > 3a) | Caixa futuro e seu risco | Mensal |
| **Prazo médio até o caixa** | Dias entre ganho e recebimento, por variante de tese | Capital de giro; na variante A pode levar de 3 a 6 anos | Mensal |
| **Mix por variante** | % do contratado nas variantes A / B / C / conta gráfica / fixo CBS | Risco e prazo de caixa da carteira | Mensal |
| **Win rate** | Ganhos ÷ (ganhos + perdidos) no período | Eficiência do funil | Semanal (média de 4 semanas) |
| **Ciclo de venda** | Mediana de dias da criação ao ganho | Velocidade | Mensal |
| **Ticket médio** | Σ totalHon ÷ nº de ganhos (e Σ valor ÷ nº) | Qualidade do negócio | Semanal |
| **Cobertura de pipeline** | Pipeline ponderado ÷ (meta − realizado) | A meta é alcançável? (referência: 3x) | Semanal |
| **Acurácia do forecast** | 1 − \|previsto − realizado\| ÷ previsto | Credibilidade do gestor | Mensal |
| **Concentração** | % do honorário nos top 3 e top 5 parceiros e clientes | Dependência (alerta: > 50% no top 5) | Mensal |
| **Parceiros ativos** | Parceiros com ≥ 1 negócio criado em 90 dias ÷ total da carteira | Saúde do canal | Mensal |
| **Receita por parceiro ativo** | Σ saldoSave ÷ parceiros ativos | Produtividade do canal | Mensal |
| **Margem por colaborador** | Σ saldoSave ÷ FTE da área | Escalabilidade | Mensal |
| **Margem de contribuição** | Receita − impostos − repasse − custos variáveis (horas do Técnico por caso) | Quanto cada negócio contribui | Mensal |
| **EBITDA da área** | Margem de contribuição − custos fixos − rateio acordado | A área se paga? | Mensal |
| **Custo por oportunidade** | Custos da área ÷ oportunidades criadas | Eficiência comercial | Mensal |
| **CAC e payback** | Custos de aquisição ÷ clientes novos; payback = CAC ÷ margem mensal por cliente | Retorno do investimento comercial | Trimestral |
| **Glosa/indeferimento** | % do crédito pleiteado indeferido ou glosado, por tese | Principal risco do modelo de êxito | Mensal |
| **Qualidade de dados** | % de negócios sem segmento, sem honorário, com anomalia | Confiança no relatório | Semanal |

## Nível 3: trimestral/semestral
Churn de parceiros · NPS de parceiros e clientes · LTV por cliente (cross-sell de teses) · retenção de indicadores.

## Regras de reconhecimento (CPC 47 / IFRS 15, para exibição)
- Honorário de êxito = **contraprestação variável**: só é "reconhecido" quando for altamente provável que não haverá reversão (ex.: crédito homologado/compensado). Antes disso é **contratado/potencial**.
- **Provisão de glosa:** aplique ao backlog a taxa histórica de indeferimento da tese. Enquanto não houver taxa, use `[PREMISSA PENDENTE]` e mostre o ajuste como faixa (ex.: 10% a 30%).
- **Variante A** (honorário no ressarcimento; via administrativa de risco contrário): fica **fora da meta e do ROI oficial**, como receita contingente.
- **Honorário fixo (aditivo CBS 2027):** reconhecido conforme a prestação; mostrar em linha separada.
- A data em que o repasse ao parceiro é devido deve ser confirmada com o Financeiro.

## Impostos (premissa da Save, na planilha `premissas-financeiras.xlsx`)
Referência de mercado, **não é o dado da Save**: Lucro Presumido ≈ 11,3% a 16,5% da receita (PIS/COFINS 3,65% + ISS 2–5% + IRPJ/CSLL sobre presunção de 32%); Lucro Real: PIS/COFINS 9,25% com créditos e IRPJ/CSLL de 34% sobre o lucro. A partir de 2027 entram CBS/IBS.
