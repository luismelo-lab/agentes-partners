# Fluxo único: tudo passa pelo agente que analisa
**Regra do Luis (14/10/2026).** Todo pedido, demanda e originação segue o mesmo caminho. Ninguém do time recebe mensagem crua do parceiro nem pedido sem análise.

```
Entrada ──► 1. Agente de triagem ──► 2. Áreas responsáveis ──► 3. Devolve analisado ──► (se não resolveu) 4. Chamado no GLPI
            interpreta                 agentes de departamento    resposta pronta e            escrito pelo especialista,
                                       respondem com dados        "já vem conferido"           aprovado no painel
```

## Entradas
| Entrada | De onde vem | Rotina que analisa |
|---|---|---|
| **Pedido** | Painel (aba Pedidos) ou e-mail `[AGENTES]` | `central-agentes-email` (skill `central-agentes`) |
| **Demanda** | WhatsApp dos grupos dos Masters e das caixas do time | `whatsapp-caixa-time` |
| **Originação** | Indicação de empresa pelo parceiro, pelo BDR ou nas análises (WhatsApp, e-mail ou painel) | `whatsapp-caixa-time` ou `central-agentes-email`, conforme a origem |

## 1. Triagem
Antes de tudo, passe o pedido pelo porteiro (`infra/porteiro.md`, `infra/ja_existe.py`). Se for repetido, continuação ou travado, a resposta parte do que já existe.
O agente lê a mensagem e as evidências (áudio transcrito, print, documento, CNPJ). Em 1 frase, ele diz o que a pessoa quer, quem é o dono do pedido e qual área responde.

## 2. Áreas responsáveis
O agente aciona o agente da área com o caso, sem Portão 0 (o pedido vem de outro departamento):

| Assunto | Agente da área (skill) |
|---|---|
| Tese, diagnóstico, execução, compensação, saldo credor | `depto-tributario` |
| Comunicado da Receita, defesa, contrato do cliente, passivo, LGPD | `depto-juridico` |
| Contrato do parceiro, aditivo, distrato | `depto-contratos` |
| Conflito de canal, repasse, cadastro de parceiro | `depto-operacoes-canal` |
| Números do HubSpot, relatórios | `depto-dados` / `depto-resultados` |
| ICP, Receita, prospecção | `depto-intel-comercial` |
| Recorrência, reanálise de casos | `recuperador` / `revisor-diagnostico` |
| O que mais o cliente pode contratar, cross-sell, esteira, mapa de valor, carteira do Master | `depto-solucoes` |
| Crédito internacional, fundo, funding, captação de capital, home equity, maquila, Paraguai, internacionalização | `depto-internacional` (sem taxa, prazo ou fee antes do G2) |
| Gestão de Contas, cobrança, antecipação de recebíveis, FIDC (Save Invest, prontos, D92) | `depto-save-invest` (dono humano: Junior) |
| Estruturação patrimonial (pronto) | `depto-juridico` |
| Tax internacional e comércio exterior (pronto) | `depto-internacional` |
| "O que mais o cliente pode contratar" | `depto-solucoes` (esteira e mapa da conta) |

**Originação** sempre passa por quatro checagens antes de devolver:
- Receita (situação, regime, CNAE e UF);
- conflito de canal (mesma raiz de CNPJ no HubSpot, em qualquer pipeline);
- aderência ao ICP;
- pré-análise tributária (teses prováveis e documentos para o diagnóstico).

## 3. Devolve analisado
No formato de três blocos de `infra/padrao-entrega.md`: o que você pediu, o que você também precisa e o que falta e quem fornece.
A resposta chega à pessoa pronta para usar:
- o que foi encontrado;
- a resposta ou o rascunho para o parceiro;
- o próximo passo.

A resposta "já vem conferida": o que o agente conferiu vai em `conferido`. Em `conferir` fica só o que depende de uma fonte sem acesso, sempre com o motivo.

## 4. Se a área não consegue responder com os dados: chamado no GLPI
- O especialista escreve o chamado ideal (`infra/chamado-ideal.md`), sem repetir a mensagem do parceiro.
- O chamado vai para aprovação no painel (aba Caixa de entrada). Nada abre sem aprovação.
- Ferramentas:
  - Demanda do WhatsApp: `chamados_whatsapp.py`.
  - Pedido ou originação pela Central: `python3 ~/agentes-partners/lib/chamados_painel.py propor --arquivo <chamado.json>`.
- Fora do GLPI, sem chamado:
  - contrato, aditivo ou distrato do parceiro vão para o time de Contratos;
  - repasse e prestação de contas vão para o Financeiro.

## 5. Enquanto a TI não libera o Graph e o GLPI (Luis, 22/10/2026)
- **Caixa oficial:** a pasta de cada pessoa no OneDrive (`Área Partners · Agentes/<Central>`), pela chave `caminhos.pasta(<pessoa>)`. O plano do dia, a triagem e as respostas são gravados lá, e o e-mail que não sai fica em `Caixa de saída`.
- **Chamados:** o Luis aprova no painel uma vez por dia. Quando o GLPI for liberado, os aprovados abrem sozinhos.
