# Ouvidoria — fluxo de tratamento e prazos propostos (v1, 29/09/2026)

Base: **ISO 10002:2018** (tratamento de reclamações). Princípios da norma adotados: compromisso, acessibilidade, transparência, capacidade de resposta, objetividade, **confidencialidade**, tempestividade, competência, melhoria contínua. Os prazos abaixo são **proposta**; referências usadas para calibrar: SAC (Decreto 11.034/2022: solução em até 7 dias corridos) e ouvidorias do sistema financeiro (Res. CMN 4.860/2020: até 10 dias úteis). Nenhuma das duas obriga a Save (serviço B2B); servem de régua. [VALIDAR com o Luis e o Jurídico]

## Dois níveis (proposta)
1. **1ª instância — atendimento:** quem já cuida da conta resolve (Daniela para os Masters; a área de apoio responsável). A maioria das reclamações termina aqui.
2. **2ª instância — Ouvidoria:** para quem não ficou satisfeito com a 1ª resposta, para reclamação **sobre** a própria área Partners, ou S1. O ouvidor precisa ser **alguém que não participou do caso** (independência — ISO 10002, objetividade). Quem é o ouvidor humano: pergunta aberta ao Luis.

## Fluxo (as 9 etapas da ISO 10002, cláusula 7, adaptadas)
```
1 Receber (WhatsApp colado · GLPI · e-mail · detrator da pesquisa)
2 Registrar → ficha QLD (references/reclamacoes.md), ID único
3 Acusar recebimento → rascunho em linguagem simples: "recebemos, o caso é QLD-…, o responsável é …, voltamos até …"
4 Avaliação inicial → tema, severidade, dono; S1 sobe no mesmo dia à dona do caso, com aviso ao Luis; Luis + Jurídico se jurídico ou LGPD sem precedente, exposição pública, compensação ou repasse (alçada de 23/10/2026)
5 Investigar → fatos, documentos, HubSpot, áreas envolvidas; 5 porquês
6 Responder → proposta de solução (humano decide; o agente rascunha)
7 Comunicar a decisão → rascunho da resposta final; se negar o pedido, explicar o motivo e o caminho de recurso (2ª instância)
8 Encerrar → só com a confirmação do reclamante ou, sem retorno, após 5 d.u. do último contato (registrar "encerrado sem confirmação")
9 Aprender → CSAT do tratamento, ação preventiva, análise mensal (Pareto)
```

## Prazos propostos
| Etapa | S1 Crítica | S2 Alta | S3 Média | S4 Baixa |
|---|---|---|---|---|
| Acuse de recebimento | até 4 h úteis | 1 d.u. | 1 d.u. | 2 d.u. |
| Plano / 1ª resposta de mérito | 2 d.u. | 3 d.u. | 5 d.u. | 10 d.u. |
| Solução (1ª instância) | 5 d.u. | 5 d.u. | 10 d.u. | 15 d.u. |
| Resposta da 2ª instância (Ouvidoria) | 5 d.u. | 10 d.u. | 10 d.u. | 10 d.u. |
| Prorrogação | uma vez, com aviso e justificativa ao reclamante antes do vencimento |
| Status sem novidade | a cada 5 d.u. o reclamante recebe atualização, mesmo que "ainda em análise" |

Quando a demora é da Receita Federal (PER, intimação), o prazo de **solução** não é da Save, mas o de **comunicação** é: acuse, explique o que depende da RFB e combine a data do próximo status.

## Regras da resposta (o agente rascunha, o humano envia)
- Fatos, sem adjetivos e sem culpar o cliente/parceiro.
- **Nunca prometer valor, êxito ou prazo que depende da RFB** (a resposta passa pelo `auditar_texto.py`).
- Reconhecer o erro quando houver; dizer o que muda no processo (ação preventiva).
- Compensação financeira, desconto de honorário, mudança de repasse: **só com o Luis** (e Jurídico/Operações de Canal). O agente não oferece.
- Dados: citar só o necessário; nada de dados de outros clientes.

## Indicadores da Ouvidoria (mensais)
Volume por tema/etapa/causa · % no prazo (acuse, mérito, solução) · tempo médio · % resolvido na 1ª instância · reincidência em 90 dias · CSAT do tratamento · nº de ações preventivas concluídas.

## Confidencialidade
Pasta `departamentos/qualidade/reclamacoes/` é restrita (Luis + ouvidor). Reclamação sobre uma pessoa do time vai **só ao Luis** e é tratada como tema de pessoas (depto-pessoas / RH formal), fatos observáveis, sem rótulos.
