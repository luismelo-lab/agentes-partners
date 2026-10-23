# Pedido único à TI · Graph e GLPI

> Área Partners · 23/10/2026. Substitui os pedidos soltos de 30/09 e 13/10 (`docs/pedidos-ti-2026-10-13.md`). Rascunho para o Luis enviar. O escopo de arquivos do HubSpot já foi resolvido (Luis, 23/10/2026).

## O que pedimos
Dois acessos técnicos, cada um com um responsável e uma data por escrito. Nenhum deles dá aos agentes acesso a senhas ou a outras caixas.

| # | Item | O que a TI faz | Escopo mínimo |
|---|---|---|---|
| 1 | **Microsoft Graph (e-mail e OneDrive)** | Registrar um aplicativo no Entra ID para a Área Partners e limitar o acesso a uma caixa só. Pode ser a do Luis ou uma caixa compartilhada da área. | Permissões `Mail.Read` e `Mail.Send`, restritas a essa caixa por **RBAC for Applications** do Exchange Online (a Microsoft recomenda isso no lugar das Application Access Policies); `Sites.ReadWrite` só da pasta "Área Partners · Agentes" |
| 2 | **GLPI 11 (chamados)** | Criar um cliente OAuth "Agentes Partners" na API v2.1 | Fluxo authorization code, escopos `api` e `user`. Testamos primeiro em modo rascunho |

## Por que importa
- Os e-mails da Central de Agentes estão parados desde 06/10. Em 22/10 havia **123 mensagens retidas**: respostas ao time, plano do dia, lote do Recuperador e alertas.
- **11 chamados** já aprovados no painel esperam o GLPI para abrir.
- Hoje o contorno é a pasta de cada pessoa no OneDrive (D91). Ele funciona, mas o time precisa ir buscar as entregas em vez de recebê-las.

## Segurança
- As credenciais ficam no cofre do Mac (`.env` com acesso restrito), não no código. Uma barreira no commit bloqueia token, CNPJ, CPF e telefone.
- Todo envio passa pela trava de domínio: só para endereços @savecompany.com.br.
- Nada é enviado a cliente ou parceiro sem aprovação humana.
- O acesso pode ser desligado a qualquer momento: basta revogar o aplicativo e o cliente OAuth.

## O que precisamos de volta
1. Nome do responsável na TI e data para cada item.
2. O ID do aplicativo e o ID do locatário (item 1) e o ID do cliente OAuth (item 2). Os segredos são entregues ao Luis pessoalmente, nunca por e-mail ou chat.
3. Um teste conjunto de 15 minutos: um e-mail para a caixa da área e um chamado em rascunho no GLPI.
