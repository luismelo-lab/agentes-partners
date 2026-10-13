# Pedidos à TI · Área Partners · 13/10/2026

Texto pronto para o Luis enviar à TI (copiar e colar no chamado ou no e-mail). Cada pedido diz o que destrava.

## 1. Repositório privado no GitHub da Save (prioridade alta)
Preciso de um repositório **privado** na organização da Save no GitHub, chamado `agentes-partners`, com acesso de escrita para luis.melo@savecompany.com.br.
- **Por quê:** hoje o código dos agentes da Área Partners existe só no meu Mac. Se o Mac falhar, perdemos o trabalho.
- **O que vai para lá:** só código e documentação. Dados de clientes ficam fora; uma barreira no commit bloqueia CNPJ, CPF, telefone e token.
- **Depois:** o mesmo repositório permite rodar as rotinas no GitHub Actions, sem depender do Mac ligado.

## 2. Microsoft Outlook clássico no Mac do Luis (prioridade alta)
O Outlook deixou de estar instalado no Mac em 06/10. Peço a reinstalação do Microsoft 365 com o **Outlook clássico** (o "novo Outlook" não aceita a automação) e a confirmação da licença.
- **Por quê:** todos os e-mails dos agentes (plano do dia, avisos, WhatsApp, Central de Agentes) saem por ele. Estão parados desde 06/10.

## 3. Microsoft Graph e Teams (prioridade média)
Registro de aplicativo no Entra ID com Mail.Send e Mail.Read da caixa do Luis e Sites.ReadWrite da pasta "Área Partners · Agentes".
- **Por quê:** tira a dependência do Outlook instalado no Mac e permite o painel no Teams.

## Pendências já pedidas antes (cobrar prazo)
- Cliente OAuth do GLPI (docs/GLPI.md).
- Webhook do Bitrix, só leitura (docs/BITRIX.md).
- Escopo de arquivos na Private App do HubSpot (dono do CRM): destrava 343 pareceres do Recuperador.
