# Modelo de registro no HubSpot — PROPOSTA (nada é gravado pelo agente)

> v1, 29/09/2026. A Central BDR só **rascunha**: a Jenifer confere e registra (ou aprova) no HubSpot. Nomes internos dos campos vêm de `~/agentes-partners/departamentos/resultados/mapeamento-hubspot.json`.

## Onde registrar
- Pipeline existente **"Save Partners - BDR/SDR"** (já usado: etapas vistas no download de 29/09 = "Follow - Up" e "Desqualificado"). **[CONFIRMAR com o time de CRM a lista completa de etapas e o ID de owner da Jenifer — no download aparece o owner 79401410 nos negócios BDR.]**
- Pipeline **"Save Partners - Closer"** (Agendamento, Negócio perdido) aparece para alguns Masters. **[CONFIRMAR se a reunião agendada pela Jenifer passa para o Closer ou direto para "RT - Real & Presumido · Agendamento".]**

## Campos do negócio (rascunho)
| Campo (interno) | Conteúdo | Fonte |
|---|---|---|
| `dealname` | Razão social (sem prefixos tipo "[MILENE] -") | Receita |
| `pipeline` / `dealstage` | Save Partners - BDR/SDR · etapa conforme o funil | Controle de follow-up |
| `nome_do_parceiro` | Nome do Master (como no roster) | Distribuição |
| `cnpj_` | CNPJ da matriz, só dígitos | Receita |
| `estado` / `cidade` | UF e município | Receita |
| `qual_e_o_regime_tributario_da_empresa_` | Lucro Real / Lucro Presumido | Minha Receita ou conversa (confirmar) |
| `descricao_do_cnae` / `cnae` | Descrição e código do CNAE principal | Receita |
| `porte_da_empresa` | Porte da Receita | Receita |
| `hubspot_owner_id` | Jenifer **[CONFIRMAR ID]** | — |
| Nota do negócio | Resumo: origem (lista de DD/MM), persona, teses prováveis (indicativo), próximo passo, data | Central BDR |

**Não registrar:** e-mail/telefone pessoal (LGPD, até validação), valores estimados, promessas.

## Mapa etapa do controle → HubSpot (proposta)
| Controle (Jenifer) | HubSpot |
|---|---|
| Em cadência / Respondeu | BDR/SDR · Follow - Up |
| Reunião agendada / realizada | BDR/SDR · [CONFIRMAR etapa] |
| Qualificado (SQL) | passa para RT - Real & Presumido · Agendamento (ou Closer) [CONFIRMAR] |
| Descartado | BDR/SDR · Desqualificado (+ motivo padronizado) |

## Higiene de CRM — formato das propostas de correção
Cada proposta é uma linha: **negócio (link) · campo · valor atual · valor proposto · fonte · motivo · aprovado? (Jenifer)**. Exemplos do que a Higiene procura nos negócios do pipeline BDR/SDR e dos Masters dela:
- CNPJ vazio ou fora do padrão (65 negócios sem CNPJ no download de 29/09);
- nome com prefixo interno ("[MILENE] - …") ou nome de pessoa no lugar da empresa;
- regime, UF, cidade ou CNAE vazios que a Receita preenche;
- duplicidade da mesma raiz de CNPJ em negócios abertos;
- negócio "Follow - Up" sem atividade há mais de 30 dias.
Para correções em massa, usar o painel do `depto-dados` (Guardião de Qualidade) como fonte.
