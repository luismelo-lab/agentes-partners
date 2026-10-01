# Checklist de conferência — contrato com cliente (v1, 29/09/2026)

> Preencha cada linha com ✅ ok · ⚠️ ajustar · ❌ bloqueia · — não se aplica, **com a fonte e a data da consulta**.
> ❌ em qualquer linha da Parte A ou C → o pedido **não** segue para a área de Contratos.

## Parte A — Cadastro do cliente (fonte oficial)
| # | Item | Como conferir | Fonte |
|---|---|---|---|
| A1 | CNPJ com 14 dígitos e dígito verificador válido | script (`cnpj_valido`); HubSpot às vezes perde os zeros à esquerda (61 casos em 29/09) | cálculo módulo 11 |
| A2 | Situação cadastral **Ativa** | base local da Receita (script) ou comprovante oficial | Receita Federal · Dados Abertos do CNPJ · mês de referência |
| A3 | Razão social idêntica à oficial (não o nome fantasia, não o nome do negócio no HubSpot) | script: similaridade < 0,5 = conferir; copie a razão **da Receita** | idem |
| A4 | Matriz ou filial: o contrato está no CNPJ certo? (crédito de PIS/COFINS é apurado de forma centralizada pela matriz — confirmar com o Tributário) | coluna Matriz/Filial | idem · `depto-tributario` |
| A5 | Endereço da sede conforme o cadastro oficial | comprovante oficial | Receita |
| A6 | Regime tributário compatível com a tese (ex.: alíquota zero em Lucro Real) | HubSpot × Tributário | `depto-tributario` |

## Parte B — Quem assina (conferência humana)
| # | Item | Como conferir |
|---|---|---|
| B1 | Signatário é sócio-administrador no **QSA** ou tem procuração com poderes | QSA (site da Receita) ou contrato social/última alteração — **a base local não tem sócios** |
| B2 | Assinatura conjunta exigida pelo contrato social? | contrato social |
| B3 | E-mail/telefone do signatário confirmados com o parceiro (não usar dado de terceiros) | parceiro, por escrito |
| B4 | Testemunhas, se o modelo exigir | modelo aprovado |

## Parte C — Negócio e parceiro (HubSpot)
| # | Item | Campo HubSpot | Observação |
|---|---|---|---|
| C1 | Parceiro correto (roster dos 9 Masters ou indicador identificado) | `nome_do_parceiro` | o campo traz às vezes a empresa, às vezes o consultor; roster em `departamentos/resultados/mapeamento-hubspot.json` |
| C2 | Sem conflito de canal (a mesma conta não está com outro parceiro) | busca por CNPJ no HubSpot | `celula-daniela` / Intel Comercial |
| C3 | % de honorário contratual preenchido e igual ao aprovado | `honorarios_contratuais` | > 50% → conferir (61 casos em 29/09) |
| C4 | % de repasse ao parceiro preenchido, ≤ 100% | `honorarios_parceiro` | 7 casos com 125% em 29/09 (erro provável) |
| C5 | Tese/escopo registrado e igual ao do diagnóstico | `teses_tributarias_aplicadas_neste_negocio_` | vazio em 52% dos ganhos |
| C6 | Via do pedido coerente: alíquota zero **sempre PER**, nunca DCOMP | escopo / minuta | `depto-juridico/references/riscos-chave.md` |
| C7 | Parecer/diagnóstico anexado | `parecer_complementar` / `anexo_do_diagnostico` | |

## Parte D — Minuta (se houver)
| # | Item |
|---|---|
| D1 | Minuta feita a partir do modelo aprovado **vigente** (versão e data do modelo registradas) |
| D2 | Todos os campos variáveis preenchidos; nenhum `[PREENCHER]` sobrando |
| D3 | Texto novo só como `[SUGESTÃO — VALIDAR JURÍDICO]` |
| D4 | Lista "pontos para o Jurídico" anexada (`montador-minuta.md`) |
| D5 | Prazos da minuta (vigência, aviso prévio, pagamento) com dupla checagem |

## Selo do Revisor
`Conferência: ✅ pronto para a área | ⚠️ segue com ressalvas (listar) | ❌ bloqueado (motivo)` · Conferido em AAAA-MM-DD · Fontes: …
