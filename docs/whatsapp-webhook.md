# WhatsApp direto do Eazybe (webhook) → agentes
O Eazybe não tem API de consulta. Ele **envia** cada mensagem, recebida ou enviada, para um endereço (webhook). O receptor precisa ficar **no ambiente Microsoft da Save**, para as mensagens de parceiros e clientes não passarem por sites de terceiros. **Não use o webhook.site** que aparece de exemplo na página do Eazybe: é público.

## Receptor (TI) · opção A: Power Automate
Precisa da licença Premium por causa do gatilho HTTP. Crie um fluxo:
1. **Gatilho:** "Quando uma solicitação HTTP é recebida" (método POST).
2. **Condição:** o cabeçalho `Authorization` (ou o campo de token que o Eazybe envia) é igual ao token combinado. Se não for, responda 401 e pare.
3. **Ação:** OneDrive for Business (conta do Luis) ou SharePoint → "Criar arquivo"
   - Pasta: `Área Partners · Agentes/WhatsApp · Eazybe/entrada`
   - Nome: `@{utcNow('yyyyMMdd-HHmmssfff')}-@{guid()}.json`
   - Conteúdo: `@{triggerBody()}`
4. **Resposta:** 200.
5. Salve o fluxo e copie a **URL HTTP POST** gerada.

## Receptor (TI) · opção B: Azure Function
Função HTTP com a mesma lógica (confere o token, grava o corpo como .json na mesma pasta pelo Microsoft Graph).

## No Eazybe (Luis)
1. Integrations → Custom webhook → "Trigger actions for WhatsApp messages (both send and receive)" → cole a URL do receptor.
2. Em "Auth token", cole um token criado por você. No Terminal, gere com:
   ```bash
   openssl rand -hex 24
   ```
   Passe o mesmo token para a TI pôr no passo 2 do fluxo.
3. Clique em **Save**. O Eazybe manda uma mensagem de teste; ela deve aparecer como arquivo na pasta.

## Nos agentes (automático depois disso)
- Para conferir:
  ```bash
  ~/agentes-partners/bin/partners integracoes verificar
  ```
  O item "WhatsApp (Eazybe direto)" mostra quantas conversas chegaram.
- Para ver a caixa de uma pessoa (só mostra, não grava):
  ```bash
  python3 ~/agentes-partners/lib/eazybe.py caixa --pessoa daniela
  ```
- Para cada pessoa receber só a dela, informe o canal de cada uma em `celulas/whatsapp-config.json` → `"eazybe_canais"`.
- A leitura pelo HubSpot continua como reserva até a fonte direta ser confirmada.
