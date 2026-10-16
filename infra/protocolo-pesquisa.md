# Protocolo de pesquisa e atualização: padrão Big Four
**Regra do Luis (16/10/2026):** os agentes não se limitam ao material compartilhado nas conversas. Eles coletam o máximo de informação disponível nas skills, nas bases internas e no mercado. Usam sempre a informação mais recente e entregam com a visão, o entendimento e o rigor de uma Big Four (Deloitte, PwC, EY, KPMG).

Vale para todo departamento, célula, Gabinete e Conselho, junto com `protocolo-gerente.md`, `padrao-entrega.md` e `fluxo-unico.md`.

## 1. As quatro camadas de conhecimento (nesta ordem, em toda entrega)
1. **Base interna.** `references/` da skill, `aprendizados.md`, decisões do Conselho e documentos do produto. Diz o que a Save decidiu.
2. **Dados da Save.** HubSpot (leitura), pareceres, Receita local, Bitrix e planilhas, sempre por script. Diz o que acontece de fato.
3. **Radar da área.** `references/radar-mercado.md`, atualizado toda semana pela rotina `radar-mercado`. Diz o que mudou no mercado.
4. **Pesquisa na hora.** WebSearch e WebFetch (carregue com ToolSearch) quando o pedido toca em norma, julgado, taxa, número de mercado, concorrente ou tendência. Também quando o radar da área tem mais de 7 dias sobre o tema, ou quando a base interna está "a confirmar".

A decisão interna **não muda** por causa da pesquisa: o que a Save decidiu continua valendo até o dono decidir de novo. Se o mercado contradiz a base, o agente **sinaliza o conflito** no bloco "o que você também precisa" e propõe a pergunta ao dono.

## 2. Recência
- Toda afirmação de mercado leva **data da informação** e **data da consulta**.
- Norma: confira a vigência no dia (vigente, revogada, alterada ou em transição).
- Número de mercado (taxa, juros, câmbio, estatística): use o dado mais recente publicado. Se tiver mais de 90 dias, diga isso.
- Julgado: confira se houve embargos, modulação ou revisão.
- Nunca afirme "atual" sem a data.

## 3. Hierarquia de fontes
1. Fonte primária oficial: lei, decreto, norma do regulador (Receita, BCB, CVM, ANPD, CGIBS), julgado no site do tribunal, estatística oficial (BCB, IBGE, ANBIMA, CFC).
2. Dado de mercado reconhecido: B3, ANBIMA, Serasa, Bloomberg/Reuters citados em imprensa, associações setoriais.
3. Publicações das Big Four e de grandes escritórios e consultorias (tax alerts, pesquisas, guias). Elas mostram **como o mercado lê** a norma e quais são as boas práticas. Servem de benchmark, não de prova.
4. Imprensa e artigos: só como pista; confirme na fonte primária.

Sem fonte, escreva "não localizado". Nunca invente número, norma ou julgado.

## 4. Visão Big Four (como pensar a entrega)
- **Do problema ao negócio:** comece pela pergunta de negócio do cliente ou do parceiro (caixa, margem, risco, crescimento), não pela norma.
- **Estruturada (MECE):** situação → implicação → recomendação. Três a cinco pontos, sem sobreposição.
- **Quantificada:** faixa em R$ ou em %, com premissas explícitas. Se não houver dado, diga qual dado falta e de onde ele vem.
- **Comparada:** mostre a alternativa de mercado, o que os pares fazem e o benchmark. Por exemplo, PPE e ACC ao lado do crédito internacional, ou FIDC ao lado da cessão.
- **Risco explícito:** matriz probabilidade × impacto, risco regulatório, risco de reputação e plano de mitigação.
- **Setorial:** use a lente do setor do cliente (agro, café, indústria, construção), com o dado setorial mais recente.
- **Próximo passo acionável:** quem faz, o quê, até quando.
- **Qualidade:** revisão do gerente (protocolo do gerente) e, para fora, auditoria do `depto-qualidade`.

## 5. Skills e ferramentas a aproveitar
- **Skills da casa:** antes de responder, verifique se outra área já tem a resposta. Leia o `radar-mercado.md` e o `references/` dela, em vez de repetir a pesquisa.
- **Skills e plugins disponíveis na sessão** (financeiro, dados, vendas, documentos): use o que se aplica. Por exemplo, leitura de planilhas e PDFs, geração de Excel e Word no padrão Save, e análise de dados.
- **Conector do HubSpot:** só leitura.

## 6. Radar semanal (rotina `radar-mercado`)
Toda semana, cada área atualiza o `references/radar-mercado.md` da sua skill:
- novidades desde a última data-base;
- impacto para a Save;
- ação do agente;
- fonte e data;
- conflitos com a base;
- perguntas novas ao dono.

O resumo vai ao Luis. Itens que mudam regra, tese ou produto viram proposta ao Conselho; nada muda sozinho.

| Área | Radar (arquivo) |
|---|---|
| Tributário | `depto-tributario/references/radar-mercado.md` |
| Jurídico, Contratos, Qualidade | `depto-juridico/references/radar-mercado.md` |
| Produtos Internacionais | `depto-internacional/references/radar-mercado-credito.md` e `radar-mercado-financeiro-maquila.md` |
| Áreas comerciais (Partner Success, Operações de Canal, Intel Comercial, Marketing, Pós-venda, Pessoas, células) | `depto-partner-success/references/radar-mercado.md` |
| Dados, Resultados, TI | seguem o radar comercial e o jurídico (LGPD e IA) |

## 7. No registro da entrega
O log de cada entrega acrescenta:
- as fontes externas consultadas, com data;
- a idade do radar usado;
- os conflitos encontrados entre o mercado e a base.

Sem isso, o gerente devolve a entrega.
