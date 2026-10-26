# Histórico antes do GLPI

**Regra do Luis (26/10/2026):** "Sobre as demandas das meninas, quero que os agentes responsáveis já avaliem em todo o histórico que temos das fontes disponíveis a resposta de acordo com a demanda. Somente caso elas não tenham a resposta, você sugira a abertura pelo GLPI."

Vale para as demandas do WhatsApp (`rotinas/whatsapp-caixa-time.md`), para os pedidos da Central (`skills/central-agentes`) e para qualquer especialista que vá propor chamado (`infra/chamado-ideal.md`). Completa o fluxo único (`infra/fluxo-unico.md`): a área tenta responder com os dados **e com o histórico** antes de escrever chamado.

## Passo a passo do especialista da área responsável
1. **Consulta o histórico primeiro:**
   `python3 ~/agentes-partners/lib/historico.py avaliar "<o_que_pede + trecho da conversa>" --master "<Master>" --empresa "<razão social>" --cnpj "<CNPJ>" --chat "<conversa>" --antes "<AAAA-MM-DDTHH:MM da demanda>" --json`
   O script procura em todas as fontes locais, sem rede, e devolve os melhores trechos com fonte, data e aderência. Também devolve uma pré-avaliação: suficiente ou não, o critério, a confiança, as buscas feitas e o que faltou. `--antes` e `--chat` tiram da busca a própria demanda e a resposta já dada depois dela.
2. **Consulta a base da área:** skill, references, FAQ validado e perguntas ao dono. O histórico já indexa esses arquivos, mas o especialista lê a seção citada antes de usar.
3. **Decide.** A pré-avaliação é um ponto de partida. O especialista confirma ou discorda e registra o motivo em `historico.nota`.
   - **Suficiente:** a rota vira `responder`, sem GLPI. O especialista preenche `resposta_historico` (formato abaixo). A `resposta` é um rascunho ao parceiro escrito pelo especialista, sem copiar o trecho antigo, e precisa passar pelo auditor de promessas (`lib/protecao.auditar`).
   - **Insuficiente:** a rota sugere GLPI com o chamado ideal (`infra/chamado-ideal.md`). O que foi encontrado entra no chamado como contexto ("O que já levantamos" e `especialista.checagens`). `historico.buscas` e `historico.faltou` mostram o que foi procurado e o que faltou. "Fora do GLPI" e `nao_abrir` continuam valendo.
   - **Sem pedido de área** (agenda, recado, cumprimento): fica com a dona do número, sem GLPI.

## Critério de "resposta suficiente"
Basta um dos critérios abaixo. Na dúvida entre suficiente e insuficiente, fica insuficiente.

| Critério | Quando vale | Validade |
|---|---|---|
| `dado_do_caso` | A empresa foi identificada (CNPJ ou razão social) e o dado pedido está no caso: etapa, status ou assinatura no HubSpot (download do dia); parecer ou diagnóstico no resumo do parecer ou no card. | Download do dia |
| `chamado_existente` | Já existe chamado escrito para o mesmo pedido e a mesma empresa. Não se abre outro: a resposta traz o andamento. Se o chamado ainda está como `proposto`, o próximo passo é aprovar no painel. Se foi `recusado`, não vale. | Enquanto o chamado está aberto |
| `mesma_pergunta_respondida` | A mesma pergunta já foi respondida, para o mesmo Master ou a mesma empresa, com aderência de pelo menos 0,55. Vale rascunho aprovado em triagem, resposta do time no WhatsApp ou resposta da Central. A medição D28 não pode ter marcado a resposta como `diferente`. | Status e assinatura: 7 dias. Compensação: 7 dias. Parecer e contrato: 30 dias. Regra: 120 dias. |
| `regra_da_casa` | Há regra explícita da casa: decisão do Conselho, regras do GLPI ("Fora do GLPI"), FAQ validado, padrão de resposta ou alçada, com aderência de pelo menos 0,5. Só vale para pergunta de regra ou processo que não depende de dado novo do caso. | Enquanto a regra está vigente |

**Nunca é suficiente, mesmo com histórico parecido:** pedidos que exigem ação nova da área. São eles:
- documento novo com prazo (intimação, despacho, ciência, caixa postal do e-CAC, indeferimento);
- cálculo ou levantamento novo (planilha, relatório, valores a pagar);
- conferência em sistema (procuração ativa, acesso, empresas ocultas no Bitrix).

Nesses casos, o histórico entra como contexto no chamado. A exceção é quando já existe chamado do mesmo pedido.

**Pergunta ao dono em aberto** (`references/perguntas-ao-dono.md` sem resposta) não é resposta. O especialista registra em `faltou` que a decisão está pendente com o dono.

## Campos no item da triagem (WhatsApp) e na resposta da Central
```json
"historico": {
  "consultado": true,
  "suficiente": true,
  "criterio": "dado_do_caso | chamado_existente | mesma_pergunta_respondida | regra_da_casa | null",
  "confianca": 0.8,
  "buscas": [{"consulta": "termos usados", "fontes": ["triagem", "whatsapp", "caso", "base"], "filtros": {"master": "…"}, "casos": ["empresa achada"], "melhores": ["fonte data grau (aderência)"]}],
  "faltou": "o que não foi achado (vazio se suficiente)",
  "nota": "por que o especialista concordou ou discordou da pré-avaliação"
},
"resposta_historico": {
  "resposta": "rascunho ao parceiro, curto, sem promessa (auditado)",
  "auditado": true,
  "fontes": [{"fonte": "caso | chamado | triagem | whatsapp | central | base", "data": "AAAA-MM-DD", "trecho": "até 220 caracteres, sem CPF, telefone ou e-mail"}],
  "confianca": 0.8,
  "criterio": "dado_do_caso",
  "area": "Central Masters | Tributário | Jurídico | …",
  "especialista": "Retorno ao Parceiro | …"
}
```
- Com `resposta_historico`, o `rascunho` do item é o mesmo texto de `resposta_historico.resposta`, a rota é `responder` e não há `encaminhar`.
- Sem resposta suficiente, `historico.suficiente` é false e `encaminhar` traz o chamado ideal. Em `encaminhar.especialista.checagens`, entra a linha "Histórico consultado: <fontes> · <o que faltou>".

## Fontes que o histórico consulta
Para ver o volume de cada uma: `python3 ~/agentes-partners/lib/historico.py inventario`.
- **triagem:** respostas preparadas nas triagens. Traz o acerto medido pela D28.
- **demanda:** registro de demandas.
- **whatsapp:** pares pergunta do parceiro → resposta do time nas caixas lidas (Daniela, Geovana, Jenifer).
- **chamado:** chamados já escritos (propostos, no painel e rascunhos).
- **central:** pedidos e respostas da Central.
- **base:** skills, references, FAQ, perguntas ao dono, decisões do Conselho, regras do GLPI, aprendizados, padrões de resposta, teses e entregas das áreas.
- **caso:** negócio no HubSpot, resumo do parecer e análises das áreas. Entra só quando a empresa é identificada.

O índice fica em cache em `registro/historico-indice/`, fora do git, com permissão 600, e é refeito quando alguma fonte muda.

**Fora do índice:**
- a exportação bruta do GLPI (os 1.115 chamados), que não está no Mac. Só os padrões aprendidos em `infra/glpi-regras.md` entram. Se a TI liberar a exportação, ela vira uma fonte nova;
- as notas e atividades do HubSpot: o download local traz só os negócios;
- o OCR dos anexos do WhatsApp, que já vai como evidência para a triagem.

## Modo de teste
`python3 ~/agentes-partners/lib/historico.py lote --saida <pasta fora de registro/> [--dias N]` roda o histórico sobre as demandas abertas e sobre a última triagem. Com `--dias`, faz um retroteste dos itens "responder" dos últimos N dias. Não grava nada no registro.
