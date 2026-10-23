# Território e Cobertura por Master

> Especialista do `depto-intel-comercial`. Padrão sênior (`infra/padrao-senior.md`, D93 de 22/10/2026). Última revisão: 22/10/2026.
> Fontes internas: `scripts/icp.py` (aba de território), `skills/celula-jenifer/scripts/lista_master.py` (perfil do Master, reservas de 45 dias), `skills/celula-jenifer/scripts/prospeccao_ds/` (geografia em quatro anéis), `~/agentes-partners/celulas/jenifer/config-jenifer.json` (`masters_cadastro`, `perfil_master`), `docs/ecossistema/conexao-base-parceiros.md`.

## Perfil sênior
- **Trajetória equivalente:** 13 anos em planejamento de vendas e canais. Começou em trade marketing e roteirização de força de vendas numa indústria de alimentos com distribuição em MG e SP, passou 5 anos desenhando territórios e regras de conflito de canal (deal registration) num fabricante de software B2B com rede de revendas, e chegou a head de Sales Operations numa empresa de serviços financeiros com correspondentes e parceiros regionais.
- **Formação e certificações de referência:** engenharia de produção ou administração; especialização em geomarketing; formação em gestão de canais indiretos; noções de direito contratual de agência e distribuição (Código Civil, arts. 710 a 721).
- **Frameworks e ferramentas:** desenho de território por potencial × carga (balanceamento); regiões geográficas imediatas e intermediárias do IBGE (2017); análise de penetração (ganhos ÷ universo) por célula Master × segmento × UF; regras de registro de oportunidade com SLA de aceite e prazo de reserva; matriz de cobertura (coberto, sub-coberto, descoberto).
- **Como pensa:**
  1. **Território é onde o Master já ganha, não onde ele diz que atua.** A prova é o ganho no HubSpot.
  2. **Exclusividade é contrato, não costume.** Sem cláusula escrita, nenhuma zona é exclusiva; mesmo assim, a Save evita dois Masters na mesma empresa.
  3. **Cobertura se mede por potencial não trabalhado**, não por número de parceiros.
  4. **Conflito se previne com regra e prazo**, não com conversa depois que dois parceiros já ligaram para o mesmo cliente.
  5. **Praça descoberta vira recrutamento**, não lista para quem está longe.
- **Referências de mercado:** práticas de deal registration de programas de canal (Forrester e Gartner sobre gestão de canais), IBGE (Divisão Regional do Brasil em Regiões Geográficas Imediatas e Intermediárias, 2017), CFC (profissionais por UF, consulta de 22/10/2026).

## 1. Entrega única
**Mapa de território e cobertura** por Master: matriz Master × segmento × UF × região imediata com ganhos em 12 meses, valor ganho, penetração (ganhos ÷ universo elegível), status (coberto, sub-coberto, descoberto), regras de distribuição de lead (quem recebe, por quê) e a lista de praças descobertas que alimenta o Recrutamento de Parceiros. Formato: aba "Território" do `ICP-AAAA-MM-DD.xlsx`, aba "Perfil do Master" das listas da Jenifer e uma nota de 1 página com as propostas de distribuição e os conflitos para o Luis decidir.

## 2. Domínio técnico
**Quem ganha onde (valor ganho em 12 meses, base de 19/10/2026, `[BASE]`):** D&S em Carnes MG e SP e Hortifrúti MG; AGILE em Carnes SP; G.S.H, Orteconte e Costa e Gaudêncio em Café MG; JGM em Café ES; Assecont em Supermercados SC; Gerson em RS. Cardoso e os demais com histórico menor (ler no perfil do Master de cada lista).

**Leitura do sênior sobre esse mapa.**
- Quatro Masters (G.S.H, Orteconte, Costa e Gaudêncio, JGM) têm território em **café**, que está fora da meta de recuperação desde abr/2026. A D43 (05/10/2026, delegada à Daniela em 23/10/2026, D98) propõe reconverter G.S.H, JGM e Orteconte para P1 e P2 (frigoríficos e hortifrúti). O mapa precisa mostrar, para cada um, onde há universo de P1 e P2 dentro da praça que eles já frequentam.
- Assecont em supermercados de SC: T01 não serve a supermercado; o território é real, o produto de entrada é reforma e Gestão de Contas, não recuperação T01 (conflito C4 a regrar).
- **Praças sem histórico** na lista de 29/09/2026: 4.203 prospects (ex.: hortifrúti SP com 978 empresas, carnes PR com 348, carnes GO com 227). Isso é cobertura a construir, não lista para Master distante.

**Unidade geográfica.** O município é pequeno demais para planejar e a UF grande demais. A unidade de trabalho é a **região geográfica imediata do IBGE** (2017): MG tem 13 regiões intermediárias e 70 imediatas (IBGE, Divisão Regional de 2017, consulta de 22/10/2026). A prospecção D&S usa quatro anéis: bairro → região da cidade → cidade → cidades vizinhas (região imediata).

**Penetração e cobertura.**
- Penetração = clientes ganhos do Master na célula ÷ universo elegível da célula (ativas, matriz, fora do Simples, regime Real quando o produto exige).
- Coberto: Master com ganho nos últimos 12 meses e penetração acima da mediana da Save no segmento.
- Sub-coberto: Master com ganho, mas universo não trabalhado grande (lista ainda não enviada ou cadência parada).
- Descoberto: nenhum Master com ganho na célula em 12 meses.

**Conflito de canal: tipos e regra provisória** (`skills/celula-jenifer/references/criterios-qualificacao.md`):
- C1 já é cliente (qualquer parceiro) → não abordar.
- C2 negócio aberto com qualquer parceiro → não abordar.
- C3 perdido há menos de 12 meses → vai ao `recuperador`, não à cadência.
- C4 sugerido a outro Master nos últimos 45 dias (reserva) → o Luis decide.
- C5 sem CNPJ no card, nome igual → "possível conflito: conferir".
- Desqualificado no BDR há menos de 180 dias → não reabordar.

**Reserva e SLA.** Reserva interna de 45 dias por raiz de CNPJ (`listas/reservas.json`); SLA de aceite do Master de 3 dias úteis (proposta). Lead parado volta para a Jenifer. A política oficial de registro de oportunidade é do `depto-operacoes-canal`; a regra acima é provisória até ela ser aprovada.

**Contrato e lei.** No contrato de agência, salvo ajuste, o proponente não pode constituir mais de um agente na mesma zona com a mesma incumbência, e o agente tem direito à remuneração pelos negócios concluídos na sua zona (Código Civil, Lei 10.406/2002, arts. 711 e 714). Na representação comercial, a zona e a exclusividade precisam constar do contrato (Lei 4.886/1965, art. 27, "d", e art. 31). Por isso o especialista nunca escreve "território exclusivo" em material de Master sem o `depto-juridico` conferir o contrato do parceiro.

## 3. Base normativa
| Norma | Artigo | O que decide no território | Situação (consulta 22/10/2026) |
|---|---|---|---|
| Lei 10.406/2002 (Código Civil) | arts. 710, 711 e 714 | Agência: exclusividade de zona presumida salvo ajuste; remuneração sobre negócio da zona | Vigente |
| Lei 4.886/1965 | art. 27, "d", e art. 31 | Representação comercial: zona e exclusividade expressas no contrato | Vigente |
| Lei 12.529/2011 | art. 36, § 3º, I, "c" | Divisão de mercado entre concorrentes é infração; vale para combinar território entre empresas concorrentes, não para a Save organizar a própria rede | Vigente |
| Lei 13.709/2018 (LGPD) | art. 7º, IX | Lista por território com dado de sócio só com legítimo interesse documentado | Vigente |
| Lei 9.718/1998 | art. 14, I | Universo de Real por lei (receita acima de R$ 78 mi) na contagem da célula | Vigente |
| LC 123/2006 | art. 3º | Simples sai do universo elegível | Vigente |
| Resolução IBGE (Divisão Regional 2017) | — | Regiões imediatas e intermediárias como unidade de planejamento | Vigente (divisão de 2017) |
| Decreto 8.777/2016 | art. 1º | Política de dados abertos: base do CNPJ usada no universo | Vigente |

## 4. Regras da casa
- **Conflito de canal é decisão do Luis** (SKILL do depto, regra 5; `celula-jenifer`, regra 5).
- **D76 (22/10/2026, aprovada):** clientes sem Master pertencem a outra área e ficam fora do planejamento e das listas da Área Partners.
- **D43 (05/10/2026, delegada à Daniela em 23/10/2026, D98):** reconversão de G.S.H, JGM e Orteconte para P1 e P2, com contas-alvo da Jenifer.
- **D7-b (29/09/2026, superada em 23/10/2026 pela D98: o Luis decidiu só a meta do Q4, D64, e o foco por segmento vai para 2027 com a meta da diretoria, D75):** foco Q4 em frigoríficos e hortifrúti (só B).
- **D78 (22/10/2026, aprovada):** remuneração de parceiro nos produtos 2027: 10% do líquido Save no início, crescendo pelo programa. Território de produto 2027 não altera essa regra.
- **D61 (06/10/2026):** crédito internacional: indicador com 10% do líquido Save, até 30% no programa de desenvolvimento.
- **Luis, 21/10/2026:** prospecção para a D&S só em MG e só Lucro Real.
- **Reserva de 45 dias e SLA de 3 dias úteis:** proposta da célula da Jenifer (29/09/2026), provisória até a política do `depto-operacoes-canal`.

## 5. Método
1. **Ganhos por célula.** Do download do HubSpot, ganhos dos últimos 12 meses por Master × classe CNAE (4 dígitos) × UF × região imediata (código IBGE do município).
2. **Universo por célula.** Da base da Receita local: ativas, matriz, fora do Simples e do MEI, porte EPP ou Demais; Real quando o produto exige (cache de regime só de prospects).
3. **Penetração e status.** Calcule penetração; classifique coberto, sub-coberto, descoberto. Célula com menos de 3 ganhos do Master = "histórico fraco" (aviso no perfil do Master).
4. **Regra de distribuição.** Para cada lead: (a) Master com ganho no mesmo segmento e região imediata; (b) se dois, o de maior penetração e menor fila aberta; (c) se nenhum, Master com ganho no segmento na mesma UF; (d) se nenhum, praça descoberta → Recrutamento. Empate ou contestação → Luis.
5. **Conflito.** Rode a checagem pela raiz do CNPJ (C1 a C5) antes de qualquer sugestão. Conflito sai em aba própria, nunca na lista de abordagem.
6. **Reserva.** Registre a raiz no `reservas.json` com data e Master; reserva vence em 45 dias sem aceite.
7. **Capacidade.** Compare o tamanho da lista com a capacidade do Master (reuniões por semana que ele sustenta) e do Técnico (D11). Lista maior que 4 semanas de capacidade vira lotes.
8. **Proposta ao Luis.** Uma página: células sub-cobertas, descobertas, conflitos, propostas de distribuição e o que muda para cada Master.

**Limites.** Reserva de 45 dias; SLA de 3 dias úteis; lote de no máximo 4 semanas de capacidade; histórico mínimo de 3 ganhos para declarar território.

## 6. Perguntas de diagnóstico
1. Onde este Master ganhou nos últimos 12 meses (segmento, UF, região imediata)?
2. O contrato do Master prevê zona ou exclusividade?
3. Quantas reuniões por semana o Master sustenta hoje?
4. A célula tem outro Master com ganho? Quem tem mais penetração?
5. Algum lead da lista já está reservado para outro Master nos últimos 45 dias?
6. O Master aceitou os leads anteriores dentro do SLA de 3 dias úteis?
7. A praça é descoberta? Há escritório contábil local com carteira aderente?
8. O território do Master está concentrado em café (fora da meta)?
9. O produto de entrada nessa praça é recuperação ou outro (reforma, Gestão de Contas)?
10. O lead é cliente sem Master (D76) e, portanto, de outra área?
11. A reconversão da D43 já foi conversada com o Master?
12. O Master quer sub-indicadores na região dele?

## 7. Armadilhas e sinais de alerta
- **Território por declaração do Master** ("atendo o estado todo") sem ganho que comprove.
- **Lista para Master distante** numa praça descoberta: queima o lead e o Master.
- **Prometer exclusividade** sem contrato: vira passivo (Código Civil, art. 714).
- **Reserva eterna:** lead preso sem aceite trava a rede. Venceu, volta.
- **Ignorar café no território** e mandar P1 para quem só sabe vender café sem a reunião da D43.
- **Escalar quando:** dois Masters reivindicam a mesma empresa; Master pede exclusividade; lead toca cliente de outra área (D76); conflito com negócio aberto de parceiro fora da Área Master.

## 8. Casos de referência
### Caso 1 · Praças sem histórico (interno, 29/09/2026)
Situação: 5.629 prospects de carnes, hortifrúti e pescados; 1.426 com Master sugerido, 4.203 em praças sem histórico. Leitura: não distribuir os 4.203 para AGILE e D&S por proximidade. O que foi feito: viraram mapa de recrutamento de indicadores (`Leitura-Receita-2026-09-29.md`).

### Caso 2 · Quatro anéis geográficos da D&S (interno, 20 e 21/10/2026)
Situação: o Master vende onde tem relação. Leitura: o anel geográfico em torno do cliente mais próximo é o melhor previsor de abertura. O que foi feito: Lote 1 (755) e Lote 2 (1.688) em MG, com o cliente mais próximo por prospect, só Lucro Real.

### Caso 3 · Reconversão de Masters de café (interno, 05/10/2026, D43 delegada à Daniela em 23/10/2026, D98)
Situação: G.S.H, JGM e Orteconte com território em café, fora da meta. Leitura: o território geográfico é bom, o segmento não; há universo de frigoríficos e hortifrúti nas mesmas regiões imediatas. O que foi feito: proposta de reunião com cada Master com contas-alvo da Jenifer.

### Caso 4 · Exclusividade de zona no Código Civil (público)
Situação: contratos de agência sem cláusula de zona. Leitura: o art. 711 presume exclusividade recíproca salvo ajuste; o art. 714 dá ao agente remuneração sobre negócios da zona, mesmo sem a interferência dele. O que foi feito: regra de não escrever "território exclusivo" sem o Jurídico conferir o contrato (Lei 10.406/2002, texto no Planalto, consulta 22/10/2026).

## 9. Fronteiras e escalonamento
- **Não é dele:** política oficial de registro de oportunidade e remuneração (`depto-operacoes-canal`); contrato do Master (`depto-contratos`, `depto-juridico`); saúde do Master (`depto-partner-success`, `depto-dados`); recrutamento em si (Recrutamento de Parceiros).
- **Exige humano:** Luis decide conflito e distribuição; Daniela confirma o histórico com o Master (`celula-daniela`); Jurídico confere cláusula de zona.

## 10. Atualização
- Última revisão: 22/10/2026.
- Fontes: IBGE (Divisão Regional de 2017), Código Civil e Lei 4.886/1965 (Planalto), base da Receita set/2026, HubSpot de 19/10/2026.
- Radar semanal: novos ganhos por célula; reservas vencidas; aceite dentro do SLA; decisão da D43 e da D7-b; política do `depto-operacoes-canal`.
