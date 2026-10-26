# PRM Save v2 · decisões do Luis (26/10/2026)

Esta folha reúne as decisões que as cinco frentes (Regras, Dados, TI, Design e o inventário da Central) deixaram para a alçada do Luis. Cada uma traz a recomendação já validada pela área dona. O código da Fase 1 sai com o padrão da recomendação em parâmetro: se o Luis decidir diferente, muda o parâmetro e não o código. Responda pelo número, por exemplo "1 ok, 4 ajuste: …".

## 1. Até 30/10
| # | Decisão | Recomendação | Origem |
|---|---|---|---|
| 1 | **D102 · repasse:** liberar o valor conferido à medida do recebimento; atípico só com contrato | Opção A | Regras §18.1; dossiê D102 |

## 2. Até 06/11
| # | Decisão | Recomendação | Origem |
|---|---|---|---|
| 2 | **D65 · registro único de exceções de honorário** | Opção A, com o inventário dos 9 termos em 2 semanas | Regras |
| 3 | **D109 · % de honorário preenchido pelo contrato** | Ordem da opção B | Regras |
| 4 | **DL-07 · base da recuperação:** honorário recebido bruto ou líquido de tributos | Bruto, até o Financeiro mostrar a prática; mudança só para contratos novos | Regras |

## 3. Até 14/11 (fase 0 · regras)
| # | Decisão | Recomendação | Origem |
|---|---|---|---|
| 5 | **DL-01 · regra de registro R1–R3:** pela raiz do CNPJ; precedência pelo registro completo; desempate em 4 níveis; nunca duas remunerações integrais; cliente ganho protegido pelo contrato + 12 meses; conflito decidido em 10 dias úteis | Aprovar como v1 e revisar em 90 dias com os dados da fila; o legado fica caso a caso | Regras, Dados |
| 6 | **DL-02 · validade do registro** | 120 dias para Master e consultores e 90 para indicador, + 60 de prorrogação com avanço; os 180 dias só onde o termo assinado já disser | Regras, desenho |
| 7 | **DL-03 · sigilo:** "livre" e "em análise" com o mesmo texto e o mesmo tempo mínimo (4 horas úteis); recusa por outro parceiro ou por cliente da Save só com motivo genérico e contestação por evidência | Aprovar. Estende ao registro a regra de 23/10 da consulta. Sem isso, quem testar CNPJs descobre a carteira (P0 do Design) | Regras, Design |
| 8 | **DL-04 · cauda de mediação** de 6 meses depois de o registro expirar ou o negócio ser perdido, com ficha ao Luis e sem remuneração automática | Aprovar; o Jurídico valida frente ao CC art. 727 | Regras |
| 9 | **DL-09 · valor previsto no extrato** antes do recebimento | Não mostrar o valor; só o percentual e o estado | Regras |
| 10 | **F8 · programa de níveis**, com DL-10 (barra em % do patamar, sem R$) | Opção A; nível só em leitura interna até a carta individual | Regras, dossiê F8 |
| 11 | **DL-11 · Master padrinho** vê só os marcos de onboarding do indicador | Aprovar | Regras |
| 12 | **Fase 1 no painel com os dados no Mac** (registro em `registro/prm/`, CNPJ mascarado) | Aprovar; é reversível | Desenho |

## 4. Até 30/11
| # | Decisão | Recomendação | Origem |
|---|---|---|---|
| 13 | **DL-05 · % em lead gerado pela BDR** | O % do termo em 2026, revisto na política 2027 | Regras |
| 14 | **DL-06 · troca de parceiro** a pedido da empresa | O original mantém o que já foi assinado; o novo só em contratos novos; sem retroagir | Regras |
| 15 | **DL-08 · estorno:** linha negativa de até 50% por ciclo, por até 24 meses, só com cláusula no termo | Aprovar; Contratos escreve a cláusula | Regras |
| 16 | **DL-17 · parceiro só pessoa jurídica** (sem PF nem MEI) | Aprovar | Regras |

## 5. Antes do pedido à TI e do piloto (Fase 2, Azure)
| # | Decisão | Recomendação | Origem |
|---|---|---|---|
| 17 | **DL-16 · guardar CNPJ e contato do decisor no Azure SQL** e consultar CNPJ fora do Mac. É exceção à regra "dado de cliente fica no Mac" | Aprovar condicionado ao parecer LGPD do Jurídico: Brazil South, tenant da Save, mínimo necessário, campos cifrados e retenção definida | Regras, Dados, TI |
| 18 | **Orçamento de nuvem** | Até US$ 90/mês na produção e US$ 25 na homologação, com alertas. A estimativa é de US$ 31 a 54/mês | TI |
| 19 | **Banco de produção** | S0 (US$ 17,81/mês, com SLA). O serverless sairia de US$ 116 a 362/mês | TI |
| 20 | **Rede privada na produção** (+cerca de US$ 23/mês) | Sim, porque o banco guarda dado de cliente indicado | TI |
| 21 | **D89 · decisões da Central** no mesmo banco do PRM, no lugar do Table Storage | Sim: uma trilha e um filtro só | TI |
| 22 | **Domínio** | `parceiros.savecompany.com.br` para o portal e `central-partners.savecompany.com.br` para o time | TI |
| 23 | **Backup mensal guardado por 12 meses** | Sim, declarado no aviso de privacidade; o Jurídico confirma | TI |
| 24 | **Piloto** | 1 Master com seus consultores na homologação; o 2º só na produção; indicadores na Fase 4 | TI, desenho |
| 25 | **DL-12 · textos-modelo como frases permitidas**, com envio automático só dos textos fixos de estado | Aprovar; texto livre segue com uma pessoa | Regras |
| 26 | **Pedido à TI da Save** (assinatura no tenant, registros de aplicativo, convites B2B, DNS) | Autorizar o envio do rascunho (`04-ti-arquitetura.md` §5) depois do item 17, com um responsável nomeado na TI | TI |

## 6. Depois de pareceres
- **DL-15 · natureza jurídica do Master:** decidir com o parecer do Jurídico de 31/10. Até lá, pagamento no dia 20 e pós-rescisão conforme o termo.
- **DL-18 · certificação N2** como porta de Gestão de Passivo: aprovar o desenho e ligar em 2027, quando os módulos estiverem validados.

## 7. Pedidos a outros donos (não sobem ao Luis)
- **Financeiro:** arquivo mensal de recebimentos. Sem ele, o extrato não passa de "previsto".
- **Dono do CRM:** propriedades `id_registro_prm` e Produto (D37), e o `hs_merged_object_ids` no download antes da mescla dos 357 cards duplicados.
- **Daniela:**
  - confirmar o cadastro de consultores (17 no roster × 27 no Partner Success);
  - definir os motivos de "não aprovado" e de "encerrado".
- **Marketing:** corrigir no Design System o token de ouro para texto. O `#B58A1F` mede 3,17:1 sobre o branco e só serve para texto grande.
- **Jurídico:** Termo de Uso e aviso de privacidade do portal (rascunho em `02-regras-de-negocio.md`), parecer LGPD e cauda de mediação.
- **Partner Success:** teste no celular com 3 a 5 consultores antes do piloto.
