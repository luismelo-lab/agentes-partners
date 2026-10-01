# O que vem de qual sistema — Pós-venda (v1, 29/09/2026)

> Legenda: ✅ disponível para o departamento · 🟡 existe, mas o agente não tem acesso (a área real fornece extração) · ❌ não existe / não localizado.
> O agente **nunca** acessa e-CAC, DTE, PER/DCOMP Web, banco ou ERP: recebe planilhas/exportações da área real.

| Dado | Sistema de origem | Situação para o agente | Observação |
|---|---|---|---|
| Cliente, CNPJ, parceiro, % honorário, % parceiro, tese | HubSpot (extrato local `departamentos/resultados/dados/hubspot-*.json`) | ✅ | % honorário vazio em 57% dos ganhos; tese vazia em 52% (29/09) |
| Situação cadastral oficial do cliente | Receita · Dados Abertos do CNPJ (base local, `receita_cnpj.py --enriquecer` / `controle_contratos.py`) | ✅ | 82 ganhos com CNPJ baixado/inapto/suspenso em 29/09 → conferir com o Técnico o efeito no pedido |
| Procuração e-CAC liberada | HubSpot `e_cac_liberado_` | ✅ | preenchido só em 145 de 1.635 ganhos |
| Valor recebido / honorário recebido | HubSpot `recebido` (mapeado como null) | ❌ | 100% vazio; fonte provável: Financeiro/ERP — **pedir** |
| Pedidos de ressarcimento (nº, período, valor, data de transmissão) | PER/DCOMP Web (e-CAC, via procuração) · planilha da área | 🟡 | Qual é o controle mestre da área? |
| Situação do PER (em análise, deferido, indeferido, despacho decisório) | e-CAC / PER-DCOMP Web · caixa postal | 🟡 | |
| Comunicação de compensação de ofício (débito, valor, data) | Caixa postal e-CAC / DTE do cliente | 🟡 | Registrar data de disponibilização **e** de abertura (ciência) |
| Ordem bancária (pagamento do ressarcimento) | Extrato bancário do cliente / comunicação da Receita | 🟡 | Quem informa: cliente, parceiro ou área? |
| Débitos do cliente (situação fiscal) | Relatório de situação fiscal (e-CAC) | 🟡 | Dado sensível: mínimo necessário |
| Guias (DARF) a compensar/quitar | Área real / parceiro contador (DCTFWeb, SicalcWeb) | 🟡 | Confirmar o que a área chama de "guias a compensar" |
| Boletos/títulos de honorário, pagamentos, atrasos | Financeiro / ERP (qual?) | 🟡 | |
| Contrato (base e momento do honorário) | Área de Contratos · `depto-contratos` | 🟡 | Modelos ainda não entregues |
| Documentos antigos (pareceres, diagnósticos) | Bitrix24 (links nos campos do HubSpot) | 🟡 | Links públicos em pendência com TI |
| Demandas do parceiro | WhatsApp (colado) · GLPI (em implantação) | 🟡 | Sugerir ao `depto-ti` categoria "Pós-venda" com subcategorias = 5 frentes |

## Formato mínimo que a área real precisaria exportar (proposta)
`extrato-pos-venda-AAAA-MM.xlsx`, uma linha por PER: `cnpj · razão social · negócio HubSpot (id) · PER nº · período · transmitido em · valor pedido · situação · data da situação · deferido · compensado de ofício (valor, débito, data) · pago (valor, data OB) · honorário faturado · vencimento · honorário recebido (valor, data)`.
Com isso, Avisos, Extrato & Saldo e o repasse ao parceiro podem ser montados por script (a construir na v2), e o `depto-resultados` passa a ter a camada "recebida" da receita.
