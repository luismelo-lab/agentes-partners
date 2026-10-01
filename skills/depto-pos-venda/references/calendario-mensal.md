# Calendário mensal proposto — Pós-venda (v1, 29/09/2026)

> **Proposta** para validar com a área real (datas, donos, sistemas). **Não há tarefa agendada**: cada etapa roda quando alguém pede, até o Luis aprovar um agendamento.
> "DU" = dia útil do mês. Prazos legais (compensação de ofício) **não esperam o calendário**: são tratados no dia em que a comunicação chega (Modo B).

| Quando | Etapa | Especialista | Entrada (de quem/qual sistema) | Saída (rascunho) | Aprova |
|---|---|---|---|---|---|
| **Diário** (dias úteis) | Verificar se chegou comunicação de compensação de ofício ou intimação | Compensações de Ofício | Área real informa o que viu na caixa postal e-CAC/DTE dos clientes (procuração) | Tabela de prazos com dupla checagem + alerta 🔴 se o prazo interno for ≤ 5 dias | Daniela → área / Jurídico |
| **DU 1–2** | Fechar o mês anterior: PER deferidos, ordens bancárias, compensações de ofício efetivadas | Extrato & Saldo | Planilha/sistema da área (status dos PER no PER/DCOMP Web; crédito em conta informado pelo cliente/parceiro) | Posição por cliente (pedido × deferido × compensado × pago × saldo) | Área real |
| **DU 3** | Calcular honorário devido sobre o que foi pago/compensado no mês, conforme contrato | Avisos de Pagamento | Extrato do DU 1–2 + % e base do contrato (HubSpot `honorarios_contratuais` + contrato) | Planilha de avisos + rascunho M1 por cliente | Área real + Financeiro |
| **DU 4** | Avisos de pagamento prontos para envio pela área | Comunicação Pós-venda | Planilha de avisos aprovada | Rascunho M1 (cliente) e M3 (parceiro) | Daniela / área |
| **DU 5** | Controle de guias: conciliar guias do mês (vencimento × origem × situação) | Controle de Guias | Lista de guias da área (DARF/DCTFWeb do cliente, fornecida pelo parceiro contador) | Conciliação + pendências (guia sem origem, vencida, divergente) | Área real |
| **DU 8** | Honorários: faturado × recebido × em atraso | Extrato & Saldo | Financeiro/ERP (títulos, pagamentos) | Lista de atrasos + rascunho de lembrete M6 (tom cordial) | Área / Financeiro |
| **DU 10** | Status mensal ao parceiro Master (por carteira) | Comunicação Pós-venda | Extratos aprovados | Rascunho M5 (resumo por Master) | Daniela |
| **DU 12** | Informar receita recebida ao `depto-operacoes-canal` (repasse) e ao `depto-resultados` | Gerente | Extrato aprovado | Arquivo de recebidos do mês | Luis |
| **Último DU** | Aprendizados do mês + perguntas pendentes às áreas | Gerente | — | `aprendizados.md`, `perguntas-areas.md` | — |

## Sobre "guias a compensar" (a confirmar com a área)
Na tese de alíquota zero a Save **não faz DCOMP** (sempre PER). Hipóteses do que a área chama de "guias a compensar", para confirmar:
1. guias (DARF) de **débitos do cliente** que a Receita pode compensar de ofício com o ressarcimento (art. 92 da IN RFB 2.055/2021);
2. guias de **outras teses/produtos** em que a compensação por DCOMP é a via prevista (fora da alíquota zero);
3. guias de **honorário** (boletos) do cliente à Save.
Até a resposta, o Controle de Guias só concilia e aponta divergências; **nunca** sugere compensar por DCOMP.

## Alertas de prazo (padrão)
Prazo interno = fatal − 5 dias · alertas D-10, D-5, D-2 · divergência entre os dois cálculos = 🔴 no mesmo dia.
