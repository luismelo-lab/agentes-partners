# Matriz de agentes · quem responde por qual parte do portfólio 2027

> Nomes das skills entre crases. **Dono humano** é quem decide; o agente só prepara. Estado dos produtos: Luis, 19/10/2026. Toda ficha passa por `infra/protocolo-gerente.md` (gerente distribui, revisa até 2 rodadas, registro `revisao`).

## 1. Produtos e serviços (P1 a P17 do ecossistema, mais os candidatos 2027)

| # | Produto ou serviço | Estado | Dono humano | Agente responsável | Revisores obrigatórios | Trava |
|---|---|---|---|---|---|---|
| P1 | Recuperação tributária (T01 a T17) | Pronto | Time técnico | `depto-tributario`, `recuperador` | Jurídico, Qualidade | Alíquota zero só via PER, nunca DCOMP; risco da tese A sempre registrado |
| P2 | Recorrência (novas competências) | Pronto | Time técnico | `depto-tributario` | Jurídico | Decadência de 5 anos |
| P3 | Crédito presumido de PF e Funrural (T18, T19) | Pronto | Time técnico | `depto-tributario` (Agro) | Jurídico | Funrural: preço e consulta e-CAC/PGFN pendentes do Luis |
| P4 | Gestão de Contas (cobrança, escrow, e-CAC) | Pronto (Save Invest) | Júnior (Save Invest) | `depto-save-invest` (D92) | Jurídico, Qualidade | Quem contrata e quem presta: em aberto |
| P5 | Gestão de Passivo | Pronto | Time jurídico | `depto-juridico`, `depto-tributario` | Qualidade | Passivo antes do crédito novo |
| P6 | Passivo bancário, alongamento, carência | Sem ficha | A definir | `depto-internacional` | Jurídico | Sem dono nem preço |
| P7 | Produtos jurídicos | Pronto | Time jurídico | `depto-juridico` | Qualidade | Marketing jurídico e OAB |
| P8 | Planejamento tributário e reforma (P01) | Pronto | Time técnico | `depto-tributario` (Reforma) | Jurídico | CBS plena em 2027; IBS em transição |
| P9 | Antecipação de recebíveis | Pronto (Save Invest) | Junior (Save Invest) | `depto-save-invest` (D92) | Jurídico | A Save indica; antecipar é de instituição autorizada |
| P10 | Estruturação patrimonial e empresarial | Pronto | Time jurídico | `depto-juridico` | Tributário | Dizer "estruturação patrimonial", não "holding" |
| P11 | Certificado digital e ART | Sem ficha | A definir | `depto-solucoes` | Jurídico | Sem preço e dono |
| P12 | Crédito Internacional | Validação, trava G2 | João Mattos | `depto-internacional` | Jurídico, Regulatório & Câmbio | Sem taxa, prazo ou fee antes do G2 |
| P13 | FIDC, FIDIC, multicedente e multissacado | Pronto (Save Invest) | Junior (Save Invest) | `depto-save-invest` (D92) | Jurídico (CVM) | Save não distribui cotas; piso de faturamento a validar |
| P14 | Home equity | Validação | João Mattos | `depto-internacional` | Jurídico | Só descoberta |
| P15 | Maquila e Paraguai | Validação | João Mattos | `depto-internacional` (Maquila & Internacionalização) | Tributário, Jurídico, Regulatório | D59 bloqueia frigorífico; só descoberta |
| P16 | Captação de capital (equity, investidores, sócio estratégico) | Validação | João Mattos | `depto-internacional` | Jurídico (CVM) | Valor mobiliário: Jurídico antes de qualquer conversa |
| P17 | Internacionalização turnkey (comercial) | Validação | João Mattos | `depto-internacional` | Jurídico | Rede de representantes a confirmar |
| P18 | Tax internacional e comércio exterior | Pronto | Paulo e João Mattos | `depto-internacional` | Tributário, Jurídico | Sem sigilo de capitais; DCBE e preço de transferência |
| N1 | Preparação para investidor (plano de negócio, projeção, dossiê) | **Candidato** | A definir | `depto-solucoes` | Internacional, Resultados | Pré-requisito do P12 e P16 |
| N2 | CFO terceirizado e controladoria | **Candidato** | A definir | `depto-solucoes`, `depto-resultados` | Qualidade | Sem dono; próprio ou parceiro |
| N3 | Governança de operação no exterior (jurídico, administrativo e contábil) | **Candidato** | João Mattos | `depto-internacional` | Jurídico | Só após P15 |
| N4 | Sucessão, governança familiar, compliance e LGPD | **Candidato** | Time jurídico | `depto-juridico` | Qualidade | Parceiro possível |
| N5 | Seguros (crédito, D&O, safra), hedge, M&A, trabalhista | **Candidato** | A definir | `depto-solucoes` | Jurídico | Via parceiro, a definir |

## 2. Camada de apoio (entra em todo produto)

| Função | Agente | Quando entra |
|---|---|---|
| Porta de entrada e roteiro | `gabinete` | Todo pedido novo; decide as áreas e a profundidade |
| Desenho da jornada e esteira | `depto-solucoes` | Sempre; é o dono do mapa da conta |
| Quem é o cliente de cada produto | `depto-intel-comercial` | Ficha de produto (ICP, sinais, território) |
| Fila de teses e diagnóstico | `recuperador`, `apresentacao-diagnostico`, `revisor-diagnostico` | Onda 1 e peça ao cliente |
| Texto, marca e peça | `depto-marketing` | Só peça para fora |
| Auditor de promessas e qualidade | `depto-qualidade` | Todo material para fora; `auditar_texto.py` |
| Contrato, minuta e distrato | `depto-contratos` | Produto vendido |
| Remuneração do parceiro | `depto-operacoes-canal` | Depois da validação do produto (MVP só após o primeiro recurso) |
| Pós-venda e recorrência | `depto-pos-venda`, `depto-partner-success` | Camada contínua |
| Números, margem e ROI | `depto-resultados`, `depto-dados` | Meta de 2027, preço, funil |
| Pedido de chamado e integrações | `depto-ti`, `central-agentes` | Quando o produto precisa de rotina |
| Parceiros Masters e prospecção | `celula-daniela`, `celula-jenifer` | Distribuição e indicação |
| Decisão de estratégia | `conselho-partners` | Próprio × parceiro, preço e meta |
| Pessoas e capacitação | `depto-pessoas` | Treino de consultores em DRE e balanço |

## 3. Regra de rota (resumo)
- **Produto pronto:** Solucoes + Tributário/Jurídico + Qualidade (consulta de uma área, sem Conselho).
- **Produto em validação:** Internacional + Jurídico + João Mattos (perguntas em `skills/depto-internacional/references/perguntas-ao-dono.md`); sem Marketing até o G2.
- **Candidato novo (N1 a N5):** Conselho decide próprio × parceiro; depois ficha.
- **Material externo:** todas as áreas envolvidas + auditor de promessas + exemplo ao Luis antes de escala.
