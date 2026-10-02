# Quando uma demanda vira chamado no GLPI (aprendido da base real)
**Fonte:** exportação do GLPI com 1.115 chamados, de 25/11/2025 a 01/10/2026. 67% foram abertos pela Daniela (565) e pela Geovana (184). Entidade única: Escritório - Czerniewicz. A base traz título, categoria, requerente, técnico, status e datas. **v2 (01/10):** 152 chamados lidos por dentro (descrição, solução e acompanhamentos), em amostra por categoria, com a visão ampliada do Luis no GLPI.
**Uso:** a triagem do WhatsApp lê este arquivo para decidir (1) se o pedido vira chamado e (2) em qual categoria. Os exemplos não trazem nomes de clientes: `<EMPRESA>` é a razão social.

## Padrão de título (seguir sempre)
`<Subcategoria> <EMPRESA> x <assunto curto>`, por exemplo `Execução <EMPRESA> x ajuste de dados bancários`. No Jurídico: `Demandas Diversas - Jurídico <EMPRESA> x <assunto>`. "URGENTE" só quando há prazo hoje ou risco de multa.

## Formulário da descrição (como as áreas recebem)
O script `chamados_whatsapp.py` monta a descrição neste formato; a triagem só preenche os campos.

**Tributário (Diagnóstico, Execução, Compensação)**
```
1) Urgência: Baixa | Média | Alta | Muito alta
2) Empresa: <razão social>
3) Descrição: o que o parceiro pede · o que já levantamos · o que falta
4) Link do Card: https://save.bitrix24.com.br/crm/deal/details/<id_bitrix>/   (campo "ID Bitrix" do negócio no HubSpot)
5) Prazo de Entrega: AAAA-MM-DD
```
**Jurídico (todas as subcategorias)**
```
DADOS
1) Setor Solicitante: MASTER
2) Parceiro Solicitante: <Master>
INFORMAÇÕES GERAIS
1) Assunto: <1 frase>
2) Classe: Interna
3) Informações Adicionais: o que o parceiro pede · o que já levantamos · o que falta
4) Documentos: o que vai anexo (despacho, intimação, contrato, print)
```
Sem o link do card, a área de Tributário costuma devolver pedindo o card: a triagem usa `card_bitrix` das evidências; se não houver, avisa na descrição.

## Checar antes de propor
- **Prioridade ou reanálise de diagnóstico:** conferir a etapa do negócio no HubSpot. Boa parte desses chamados volta com "já se encontra em apresentação de diagnóstico" ou "parecer já anexado ao card". Se o negócio já passou do diagnóstico ou o parecer está no card, **não propor**: entregar o status e o parecer na resposta.
- **Pendência de documento:** dizer qual documento falta e se já está no card. A área responde "documento já anexado" quando não é conferido antes.
- **Despacho decisório ou comunicado da RFB:** o Jurídico pede a **autorização do parceiro/cliente para seguir (ou não) com a manifestação de inconformidade**. Se a conversa já tem a autorização, dizer isso no assunto ("… autorizado seguir com manifestação de inconformidade"); se não tem, o chamado registra o comunicado e a Partners busca a autorização.
- **Prazo:** despacho e intimação têm prazo de defesa (em geral 30 dias da ciência). Informar a data de ciência quando aparecer no print; com menos de 10 dias, urgência 5.

## Fora do GLPI (encaminhar para outra equipe, sem chamado)
- **Contrato do parceiro, aditivo do parceiro e distrato do parceiro:** time de Contratos (o Jurídico só entra em distrato com litígio ou análise de cláusula).
- **Prestação de contas, repasse, faturamento e detalhe de compensação de ofício para cobrança:** Financeiro.
- **Sistema S (Sesi, Senai, Sesc, Senac, Sebrae…):** não é compensável. Responder ao parceiro com a regra; não abrir chamado de compensação.

## LGPD
Os formulários do Jurídico às vezes pedem dados do representante legal. **O agente não preenche CPF, RG, CNH nem dados bancários** de ninguém, e esses dados **nunca são digitados no painel** (o time inteiro e os agentes leem o painel). Quem atende completa direto no GLPI depois da abertura, se a área exigir. Descrição e nome da conversa passam pelo mascaramento (lib/protecao.py) antes de ir ao painel e ao GLPI.

## Categorias que mais recebem chamados da Partners
| Categoria | Chamados | Solução (mediana) | Abre quando o parceiro… | Assuntos típicos (títulos reais) |
|---|---|---|---|---|
| **Tributário > Diagnóstico** | 256 | 1 dia | pede diagnóstico de uma empresa, prioridade de diagnóstico, cobra pendência de documento do diagnóstico ou tem dúvida sobre o diagnóstico/parecer | "Diagnóstico <EMPRESA>", "… x PRIORIDADE", "… x pendente documento do diagnóstico no card", "… x dúvida referente ao parecer", "… x exclusão ICMS/ST na BC", "… x previdenciário" |
| **Tributário > Execução** | 218 | 1 dia | precisa que o crédito siga para execução, pede cálculo, memória ou relatório de execução, **dados bancários** para restituição/ressarcimento, suspender execução ou resolver pendência (DCTF) | "Execução <EMPRESA>", "… x relatório de execução", "… x memória de cálculo", "… x cadastro/ajuste de dados bancários", "… x chave PIX CNPJ", "… x mensagem e-CAC ajustar dado bancário", "Suspender execução x <EMPRESA>" |
| **Tributário > Compensação** | 157 | menos de 1 dia | fala de compensação: fazer, cancelar ou reverter, compensação de ofício, saldo, relatório de PER/DCOMP, caixa postal ou situação fiscal no e-CAC | "Compensação <EMPRESA>", "… x cancelar", "… x reverter compensação", "… x faturamento sobre a compensação de ofício", "… x relatório de PER/DCOMPs", "… x e-CAC caixa postal" |
| **Jurídico > Demandas Diversas** | 187 | 4 dias | pede parecer jurídico, parecer atualizado de compensação diante de despacho decisório, análise de intimação (inclusive NCM), modelo de contrato (ex.: indicador externo), avaliação de tese nova, contador "interpretando errado" o trabalho, parcelamento de passivo | "Demandas Diversas - Jurídico <EMPRESA> x parecer atualizado compensação x despacho decisório", "… x intimação", "… contrato de indicador externo – modelo", "… tese de crédito presumido de ICMS – <UF>" |
| **Jurídico > Comunicados RFB** | 81 | 3 dias | recebeu despacho decisório, intimação, comunicado ou movimentação no e-CAC; precisa de **autorização para seguir (ou não) com manifestação de inconformidade**; CND com urgência | "Comunicados RFB Despacho Decisório PER/DCOMP – <EMPRESA>", "… autorizado seguir com manifestação de inconformidade", "… movimentação no e-CAC, verificar", "… CND – documentação comprovando urgência" |
| Jurídico > Contencioso Adm > Manifestações de Inconformidade | 8 | 8 dias | precisa da **defesa** (manifestação de inconformidade) | "Manifestações de Inconformidade – Contencioso Adm <EMPRESA>" |
| Jurídico > Contencioso Adm | 9 | 9 dias | pede para verificar e-processo ou intimação já em processo | "… VERIFICAR e-processo nº …", "… VERIFICAR INTIMAÇÃO – <EMPRESA>" |
| Jurídico > Contencioso Judicial (+ Demandas Diversas) | 7 | — | quer entrar com **mandado de segurança** ou ação judicial | — |
| Jurídico > Gestão de Passivo (+ Parecer de Acompanhamento, Dúvidas) · Jurídico > Passivo > Parecer | 37 | 1 a 3 dias | tem débitos: proposta de passivo, parecer de passivo, prioridade | "Proposta <EMPRESA> (Passivo)", "Parecer – Passivo <EMPRESA>" |
| Jurídico > Transação (Reanálise, Análise CAPAG, Dúvidas) | 8 | — | quer transação tributária ou reanálise de CAPAG | — |
| Jurídico > RT > Aditivo · Distrato · Alterações de Cláusulas | 10 | — | pede **aditivo, distrato ou mudança de cláusula** no contrato do cliente | — |
| Jurídico > Parceiro > Distrato · Jurídico > Análise de Contratos | 6 | — | distrato do parceiro; análise de um contrato | — |
| Jurídico > Holding (Pré-diagnóstico, Reunião, Dúvidas, Execução) | 31 | 2 a 10 dias | holding familiar: pré-diagnóstico, reunião, dúvidas | "Pré-Diagnóstico <FAMÍLIA/PESSOA>" |
| Jurídico > Compliance (Dossiê, Dúvidas, Parecer) | 23 | 1 dia | dossiê de compliance de um cliente ou dúvida de compliance | "Dossiê – Compliance <EMPRESA>" |
| Jurídico > Consulta Processual (Conferir consulta, Dúvidas) | 8 | — | conferir uma consulta processual | — |
| (sem categoria) "Contrato Padrão – Recuperação Tributária", "Proposta – Passivo", "Dúvidas" | 20 | 3 dias | gerar **contrato padrão** do cliente ou proposta de passivo | "Contrato Padrão – Recuperação Tributária <EMPRESA>" |

**Prioridade usada na prática:** Diagnóstico, Execução e Compensação saem com Alta em cerca de 45–50% dos casos. O Jurídico sai quase sempre com Média. Muito alta ou Crítica é raro (8 de 1.115): só com prazo de defesa ou multa.

## O que NÃO vira chamado
A base só tem chamados abertos. Os casos abaixo não aparecem nela, o que mostra que se resolvem fora do GLPI:
- **Status de negócio, contrato ou diagnóstico:** os agentes respondem pelo HubSpot (ex.: "assinaram?", "como está o pedido?"). Só vira chamado se o card estiver parado e a área precisar agir; aí entra na categoria do assunto ("… x pendente documento do diagnóstico no card").
- **Assinatura e envio de contrato padrão já emitido:** é acompanhamento na plataforma de assinatura e no CRM, feito pela Daniela. Vira chamado só para gerar o contrato padrão ou para aditivo, distrato ou cláusula.
- **Material, apresentação, modelo comercial que já existe:** biblioteca de materiais.
- **Conversa informal, agradecimento, "bom dia", promoções, combinados de agenda.**
- **Assunto ainda em avaliação pelo parceiro** ("estou validando se vamos entrar com o MS"): aguardar o pedido.
- **Dúvida que a Geovana responde na hora** (enquadramento, tese provável): ela responde. Vira "Tributário > Diagnóstico" só se for pedir diagnóstico.

## Reclassificação dos casos de teste de 01/10
| Demanda | Antes (suposição) | Pela base real |
|---|---|---|
| "Assinaram?" (status de contrato) | Contratos | **Não é chamado:** status. Conferir na plataforma de assinatura e responder |
| Contrato assinado enviado pelo parceiro (recorrência) | Contratos | **Não é chamado de contrato.** Atualizar o CRM. Se o crédito já pode seguir, **Tributário > Execução** ("Execução <EMPRESA> x recorrência – contrato assinado") |
| Defesa e próximos passos de um cliente | Técnico | **Jurídico > Comunicados RFB** (decidir se segue com manifestação de inconformidade) ou **Contencioso Adm > Manifestações de Inconformidade** (se a defesa já está em curso) |
