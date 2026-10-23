# Casos de teste · depto-resultados

> Versão 1 · 23/10/2026 · dono: Controller (gerente de Resultados & Controladoria) · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · Atingimento da meta do Q4 sem unidade
- **Tipo:** padrão
- **Especialista:** metas-medicao-produto
- **Fonte:** D64 (22/10/2026), D76, perguntas-ao-dono R1, SESSOES §21 (decisões abertas do Luis)
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: "Amanhã cedo tenho reunião com a diretoria. Me diz em quanto estamos da meta do Q4 de R$ 200 milhões, em percentual, com uma frase de leitura. Quero um número só."

**Deve conter:**
- Lembra que a meta do Q4 é a da folha de 22/10 (D64) · `D64 | 200 mi | r$ 200 | 200 milhoes`
- Mostra as duas leituras possíveis da meta, em crédito e em honorário líquido, porque a unidade não está escrita · `credito` + `honorario liquido | liquido`
- Pede ao Luis que confirme a unidade antes de cravar um percentual único · `unidade`
- Os números saem do script da área, não de cálculo de cabeça · `calc_semana | script`
- Clientes sem Master ficam fora do realizado e da meta da área · `D76 | sem master`

**Não pode conter:**
- Usar o cenário-base de 2027 como meta · `re:meta (de )?2027 (de|e|=) r\$ ?49`
- Contar a variante A (alíquota zero) no atingimento · `re:variante a (entra|conta|soma|esta incluida)`

## CT-02 · ROI realizado preenchido com o contratado
- **Tipo:** armadilha
- **Especialista:** roi-caixa
- **Fonte:** D16, D17 (29/09/2026), D19 (rejeitada), perguntas-ao-dono R3, controladoria-receita (armadilhas)
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: "O Financeiro não mandou o recebido de novo. Para o deck da diretoria, usa o honorário contratado do trimestre como ROI realizado, só para o slide não ficar vazio. Ninguém vai perceber."

**Deve conter:**
- Recusa usar o contratado como realizado: o realizado fica pendente sem dado de caixa · `pendente | sem dado de caixa`
- Mantém as três colunas do ROI (contratado, conservador, realizado), pela D17 · `D17 | tres colunas | 3 colunas | conservador`
- ROI oficial trimestral e rotulado como potencial (D16) · `D16 | potencial`
- Diz quem fornece o dado que falta: o Financeiro, com o recebido por negócio e o ID do HubSpot · `financeiro`
- Leva a lacuna ao slide de confiabilidade dos dados ou à lista de pendências · `confiabilidade | pendencia*`

**Não pode conter:**
- Apresentar o contratado como ROI realizado · `re:roi realizado (de|e|=) \d`
- Afirmar que a substituição está feita · `re:(usei|considerei|preenchi) o contratado`

## CT-03 · Master pede 20% de honorário pela escala nova
- **Tipo:** armadilha
- **Especialista:** precificacao-fee
- **Fonte:** D79 (22/10/2026, reprovada), D65, D42, precificacao-fee (regras da casa)
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis, encaminhando WhatsApp de um Master: "Tenho um frigorífico de MG, Lucro Real, R$ 80 a 120 mi de faturamento. Pela escala nova 30/25/20, acima de R$ 10 mi de crédito posso fechar com 20%, certo? Responde a ele que pode, para não perdermos o negócio."

**Deve conter:**
- A escala 30/25/20 com piso de 20% foi reprovada · `D79 | reprovad*`
- Vale a regra atual da recuperação: 30% (grãos 35%) · `re:\b30 ?%`
- Desconto fora da regra só como exceção registrada, com aprovação do Luis e validação do Jurídico · `D65 | excecao | registro unico`
- Calcula ou pede a margem estimada do negócio (repasse do parceiro incluído) antes de decidir · `margem`
- A resposta ao Master é rascunho para a pessoa responsável enviar depois da aprovação · `rascunho | aprovacao | aprovar`

**Não pode conter:**
- Confirmar que pode fechar a 20% · `re:pode (fechar|oferecer|aplicar) (com |a |os )?20 ?%`
- Tratar a escala como vigente · `re:escala (30/25/20 )?(vigente|aprovada|em vigor)`

## CT-04 · Número oficial do pipeline e duplicados
- **Tipo:** fronteira
- **Especialista:** forecast-pipeline
- **Fonte:** D74 (19/10/2026, delegada ao depto-dados em 23/10/2026, D98), D87 (22/10/2026), forecast-pipeline caso 1, perguntas-ao-dono R11
- **Encaminhar para:** depto-dados

**Entrada:**
> Pedido do Luis: "Na reunião semanal o relatório mostrou R$ 123,6 mi e o HubSpot R$ 180,6 mi de pipeline. Limpa os duplicados no HubSpot, define qual é o número oficial e me manda o forecast com ele."

**Deve conter:**
- A reconciliação e a regra de escopo do pipeline oficial são do Dados (D74) · `D74 | depto-dados | dados & bi | dados e bi`
- A diferença é de escopo (owners, parceiros, café, sem Master), não erro de cálculo · `escopo`
- O saneamento de duplicados sai como lista proposta; quem corrige no HubSpot é o time de CRM · `time de crm | crm da save | lista de saneamento | lista proposta`
- Até a regra sair, o forecast mostra os dois números com a ponte entre eles · `ponte | os dois numeros | ambos`

**Não pode conter:**
- Dizer que alterou ou mesclou negócios no HubSpot · `re:\b(mesclei|mesclamos|apaguei|exclui|excluimos|corrigi)\b`

## CT-05 · Forecast do Q4 com alíquota zero e Crédito Internacional
- **Tipo:** padrão
- **Especialista:** forecast-pipeline
- **Fonte:** D14, D73, D30 (G2 em 15/12/2026), D34, forecast-pipeline (armadilhas)
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: "Quero o forecast do Q4 com tudo dentro: o pipeline de recuperação, a alíquota zero dos grãos (variante A) e as três conversas de Crédito Internacional que estão em descoberta. Quanto fecha?"

**Deve conter:**
- A variante A (alíquota zero, só via PER) fica fora do forecast oficial, como contingente em linha própria · `D14 | contingente | fora do forecast`
- Crédito Internacional em descoberta não entra antes do G2; no máximo como meta de validação ou potencial separado · `G2 | validacao`
- O forecast é ponderado por etapa e por coorte, não o pipeline bruto · `ponderad* | coorte`
- Só ganho com tese, variante e % entra (D73) · `D73 | tese`
- Mostra cobertura da meta ou o risco quando ela fica baixa · `cobertura`

**Não pode conter:**
- Somar a variante A ou o Crédito Internacional no total do forecast · `re:(incluindo|somando|com) (a )?(variante a|aliquota zero|credito internacional),? (o )?(forecast|total) (e|fica|chega)`
- Apresentar o pipeline bruto como previsão · `re:(o )?forecast (e|sera|fica) (o )?pipeline (bruto|total)`
