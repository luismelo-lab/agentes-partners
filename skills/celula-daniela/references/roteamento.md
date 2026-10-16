# Roteamento das demandas dos Masters

Segue a matriz do Gabinete (`~/.claude/skills/gabinete/references/matriz-roteamento.md`), aplicada à rotina da Daniela.
Princípio do Gabinete: **só entra quem agrega**. Na dúvida, a Daniela decide.

## Departamentos virtuais (preparam pré-análise/rascunho; o humano valida)
| Tema da demanda | Skill | Modo / especialista | Humano que valida |
|---|---|---|---|
| Contrato, cláusula, termo de parceria | `depto-juridico` | B · Contratos (+ Compliance Ético se envolver remuneração do parceiro) | Daniela (advogada) e, se for além da pré-análise, o Jurídico real |
| Notificação/intimação da Receita | `depto-juridico` | A · Controle de Prazos (dupla checagem) + Contencioso Administrativo | Jurídico real **no mesmo dia** |
| Compensação, PER/DCOMP, multa | `depto-juridico` | Recuperação de Créditos & Compensação | Jurídico real + Pós-venda |
| LGPD (WhatsApp, dados de clientes, listas) | `depto-juridico` | LGPD & Privacidade | Jurídico real |
| Apoio jurídico em reunião | `depto-juridico` | D · Apoio Jurídico Comercial | Daniela |
| Dúvida de tese, norma, julgamento | `depto-tributario` | especialista da linha | Técnico tributário (1º nível: Geovana) |
| Crédito internacional, fundo, funding, FIDC, antecipação, gestão de contas, home equity, maquila, Paraguai, internacionalização | `depto-internacional` | Qualificador, Maquila ou Ecossistema (modo A ou B) | Luis (ponto focal) e o João Mattos (dono do produto) |
| Reanálise de perdido/zerado | `recuperador` | fila e ficha | Geovana |
| Material novo, co-branding, kit | `depto-marketing` | Enablement de Vendas do Parceiro / Co-branding | Marketing real |
| Números do parceiro, saúde, qualidade do CRM | `depto-dados` | Performance de Canal / Guardião de Qualidade | Daniela / Luis |
| Margem, honorário, repasse (análise) | `depto-resultados` | Analista de Margem | Luis |
| Território, conflito de canal, ICP | `depto-intel-comercial` | Planejador de Territórios | Luis decide |

Como acionar: ferramenta Agent (`general-purpose`), mandando ler o SKILL.md do departamento, dizendo o modo, o que entregar, o limite de palavras e que o Portão 0 do departamento já foi aprovado pela Daniela. Passar só o mínimo de dado do cliente.

## Áreas ainda não construídas como departamento virtual → pedido formatado (modelo 2) para a área humana
| Área humana | Tipos (sla.json) | Observação |
|---|---|---|
| Contratos | `CTR-ENVIO`, `CTR-DISTRATO` | distrato com litígio: + depto-juridico |
| Pós-venda | `POS-EXTRATO`, `POS-GUIAS`, `POS-COMPENSACAO` | |
| Partner Success | onboarding, capacitação de parceiro | até existir: Luis |
| Operações de Canal & Comissionamento (Financeiro) | `REP-COMISSAO` | repasse atrasado destrói confiança: prioridade |
| TI / GLPI | `TI-ACESSO` | |
| Qualidade & Ouvidoria | `QLD-RECLAMACAO` | até existir: Luis no mesmo dia |

## Vai para o Luis (decisão, não roteamento)
Condições comerciais e exceções de honorário (`COM-CONDICOES`) · conflito de canal · reclamação grave · qualquer coisa que envolva promessa ao parceiro, renegociação ou mudança de termo de parceria · tema que cruze 2+ áreas com impacto relevante (sugerir ao Luis levar ao `gabinete`).

## Não roteia: a Daniela resolve com apoio dos scripts
`COM-STATUS` (briefing_master.py --negocio) · `COM-NOVO-NEGOCIO` (crm_checagem.py --cnpj) · `CRM-CADASTRO` (crm_checagem.py) · `MKT-MATERIAL` (Biblioteca) · `COM-REUNIAO` (Reuniões).
