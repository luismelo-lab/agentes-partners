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

**Originação** sempre passa por quatro checagens antes de devolver:
- Receita (situação, regime, CNAE e UF);
- conflito de canal (mesma raiz de CNPJ no HubSpot, em qualquer pipeline);
- aderência ao ICP;
- pré-análise tributária (teses prováveis e documentos para o diagnóstico).

## 3. Devolve analisado
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
