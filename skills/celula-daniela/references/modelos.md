# Modelos da Central Masters (célula da Daniela)

Todos os modelos são **rascunhos**. Nada sai para parceiro, área, HubSpot ou GLPI sem a Daniela aprovar (🔒).
Regras de conteúdo que valem para todos:
- **LGPD, mínimo necessário:** razão social e ID do negócio bastam na maioria dos casos. CNPJ só quando a área precisa. Nunca CPF, telefone, e-mail pessoal, dados de sócios ou valores de crédito em mensagem de WhatsApp.
- **Não prometer:** nunca afirmar valor de crédito, êxito, prazo de ressarcimento ou resultado de tese. Usar "estimativa", "a confirmar pelo técnico", "previsão da área".
- **Não presumir:** o que não se sabe vira pergunta (campo "O que falta").

---

## 1. Ficha de triagem (Triagem & Roteamento)
Salvar em `~/agentes-partners/celulas/daniela/demandas/AAAA-MM-DD-<master>-<assunto>.md`.

```
# Ficha de triagem — <Master> — <assunto em 5 palavras>
Recebida em: <data/hora> · Canal: <WhatsApp | GLPI nº | e-mail | reunião> · Contato no parceiro: <nome>
Pedido do parceiro (em 1 frase, sem dados sensíveis): <...>
Trecho relevante da conversa: "<até 3 linhas>"

Tipo de demanda: <código do sla.json> — <rótulo>   (confiança: alta | média | baixa → se baixa, perguntar à Daniela)
Categoria: Jurídico | Comercial | Técnico | Contratos | Pós-venda | Marketing | Comissionamento | CRM | Qualidade | TI | Outros
Negócio(s) HubSpot: <ID + link> · Cliente: <razão social>
Urgência: normal | urgente (motivo: prazo legal, reunião marcada, reclamação)

Dados mínimos (do sla.json):          Situação
- <dado 1>                             ✅ veio na conversa | ❌ falta
- <dado 2>                             ...
O que falta pedir ao parceiro: <lista>  → rascunho de pedido de dados no modelo 3 (variação "pedir dados")

Rota proposta: <depto virtual (skill) | área humana | Daniela resolve | Luis decide>
Por quê: <1 linha>
Prazos (PROPOSTA sla.json): 1ª resposta até <data> · solução até <data>
Foi ponte? (a Daniela só recebe, repassa e devolve): S | N

🔒 Portão 1 — Daniela: [ ] aprovar rota  [ ] ajustar: ____  [ ] ela mesma resolve
Depois da aprovação: registrar com `pendencias.py --adicionar ... --aprovado-por Daniela`.
```

## 2. Pedido para a área de apoio (formatado)
Usado quando a rota é uma **área humana** (Contratos, Pós-venda, Técnico, Financeiro/Operações de Canal, TI, Qualidade) ou quando a pré-análise do depto virtual precisa ir ao humano.

```
Assunto: [Partners · <Master>] <tipo> — <cliente> — prazo <dd/mm>

Olá, <nome/área>,
Pedido do parceiro <Master> referente ao cliente <razão social> (negócio HubSpot <ID/link>).

O que precisamos: <entrega esperada em 1–2 frases>
Para quando: <data> — motivo: <reunião com o cliente em dd/mm | prazo legal | rotina>
Informações já disponíveis:
- <dado> 
- <anexo/link>
O que ainda não temos (se for impeditivo, me avise): <...>
Referência interna: <ID da pendência PM-AAAA-NNNN> <· chamado GLPI nº, se houver>

Obrigada,
Daniela Maciel · Gestora de Contas Masters
```
Variação GLPI: mesmo conteúdo nos campos do chamado (Categoria = área; Título = assunto acima; Descrição = corpo; campos obrigatórios conforme a área definir).

## 3. Resposta ao parceiro (Retorno ao Parceiro)
Tom: próximo, direto, sem juridiquês, uma ideia por parágrafo. WhatsApp: até ~6 linhas; e-mail quando houver anexo, número ou histórico que o parceiro vá reencaminhar.

**3a. Recebido e encaminhado (1ª resposta)**
```
Oi, <nome>! Recebi o seu pedido sobre <assunto> do cliente <nome curto>.
Já encaminhei para <área> e a previsão de retorno é <dd/mm>.
Assim que tiver novidade, te aviso por aqui.
```
**3b. Pedir dados que faltam**
```
Oi, <nome>! Para dar andamento a <assunto> do <cliente>, preciso de:
1. <dado>
2. <dado>
Pode me enviar por aqui mesmo (ou por e-mail, se tiver documento)? Assim que chegar, encaminho no mesmo dia.
```
**3c. Status / andamento**
```
Oi, <nome>! Atualização sobre <cliente>: <etapa atual em linguagem simples>.
Próximo passo: <o que falta e com quem está>. Previsão: <data | "a área ainda não informou; cobrei hoje">.
```
**3d. Entrega**
```
Oi, <nome>! Segue <entrega> do <cliente>. <1 frase do que o parceiro precisa saber.>
Qualquer dúvida, estou à disposição. (Se for levar ao cliente: <ponto de atenção, ex.: "o valor é estimativa até a conclusão do técnico">.)
```
**3e. Atraso (sem culpar a área)**
```
Oi, <nome>! Sobre <assunto>: ainda não tenho o retorno de <área>, que estava previsto para <data>.
Já cobrei e a nova previsão é <data>. Se isso afetar a sua reunião com o cliente, me avisa que busco uma alternativa.
```
Checklist antes de a Daniela enviar (🔒 Portão 3): [ ] sem promessa de valor/êxito [ ] sem dado sensível [ ] prazo confirmado pela área [ ] se jurídico/técnico: texto validado pelo humano responsável.

## 4. Proposta de atualização de CRM
Gerada por `scripts/crm_checagem.py` (Receita + conversa). Formato:

| Campo HubSpot | Valor atual | Valor sugerido | Fonte (com data) | Ação | Decisão da Daniela |
|---|---|---|---|---|---|
| `estado` | vazio | MG | Receita · Dados Abertos do CNPJ · 2026-09 | Atualizar | ✅ / ✏️ / ❌ |
| `faturamento` | vazio | R$ 12 mi/ano | WhatsApp D&S 29/09 (informado pelo parceiro) | Atualizar se confirmar | |

Regras: valor sugerido **só com fonte**; campo sem fonte oficial vira "obter em: <quem tem o dado>"; regime tributário nunca é sugerido pela Receita aberta (ela não informa LR/LP), só sinalizado; a Daniela aplica à mão no HubSpot.

## 5. Briefing de reunião (pré-reunião)
Base numérica: `briefing_master.py --master <Master> [--negocio <id>]`. O agente acrescenta o qualitativo abaixo.

```
# Briefing — reunião <venda | pós-venda> — <cliente> com <Master> — <dd/mm hh:mm>
Participantes: <Save: Daniela, Geovana?> · <parceiro> · <cliente: cargos, sem contato pessoal>
Objetivo da reunião (1 frase): <...>   ·   Resultado esperado: <decisão, documento, próximo passo>

1. Negócio em 5 linhas: etapa, idade, valor estimado (é estimativa), tese, o que já foi entregue ao cliente.
2. Histórico do grupo (mesma raiz de CNPJ): negócios anteriores, ganhos, perdidos e por quê.
3. O parceiro: saúde (sinal do depto-dados), pendências abertas com ele, último atrito ou elogio.
4. Pendências que afetam esta reunião (do controle): <ID, área, prazo>.
5. Pontos de atenção: CNPJ/regime divergente, documentos faltando, prazo (decadência, fim do PIS/COFINS em dez/2026), conflito de canal.
6. Perguntas prováveis do cliente e quem responde (técnico → Geovana/depto-tributario; jurídico → Daniela/depto-juridico).
7. **O que não prometer:** valor final, êxito, prazo de ressarcimento/compensação.
8. Materiais para levar: <da Biblioteca>.
```

## 6. Ata e próximos passos (pós-reunião)
A partir das anotações/transcrição coladas pela Daniela. Salvar em `~/agentes-partners/celulas/daniela/atas/AAAA-MM-DD-<cliente>.md`.

```
# Ata — <cliente> · <Master> · <dd/mm/aaaa>
Participantes: <...>   ·   Tipo: venda | pós-venda
Resumo (3 linhas): <...>
Decisões tomadas: <...>
Dúvidas que ficaram em aberto: <...> → responsável
Próximos passos:
| # | O quê | Quem | Até quando | Vira pendência? (tipo sla.json) |
Atualizações de CRM sugeridas (modelo 4): <etapa, próximo passo, campos>
Mensagem de follow-up ao parceiro (modelo 3d/3c): <rascunho>
Compromissos assumidos pela Save: <listar para não esquecer — conferir se nada prometido fere a regra de não prometer valor/êxito>
```
🔒 A Daniela revisa a ata; só então as pendências entram no controle e o follow-up é enviado por ela.
