# Chamados automáticos no GLPI · pedido ao administrador
**De:** Luis Fernando de Melo (Área Partners) · **Data:** 01/10/2026 · **GLPI:** https://tributario.savecompany.com.br

## O que queremos
Os agentes da Área Partners leem as demandas que os parceiros mandam no WhatsApp. O que eles não conseguem resolver vira **chamado no GLPI** para o time certo: Jurídico, Técnico, Contratos, Pós-venda, Marketing, Financeiro ou TI. O chamado já vai com o que o parceiro pede, o que já foi levantado no HubSpot e na Receita e o que falta. Ele é aberto **com o usuário de quem atendeu o parceiro** (Daniela, Geovana ou Jenifer). **Não é preciso criar usuário nem perfil novo.** Nada é enviado a parceiros ou clientes.

## O que já verificamos (sem login)
- **Versão e API:** GLPI 11, com a **API v2.1 (High-Level REST API) ativa**. É ela que será usada: `/api.php/v2/Assistance/Ticket`, `/Timeline/Followup` e `/TeamMember`.
- **Autenticação:** OAuth2. A API antiga (`apirest.php`) está desativada e continua desativada.

## O único pedido: um cliente OAuth
Em Configurar → Clientes OAuth:
- **Nome:** Agentes Partners
- **Fluxo:** *Authorization code*
- **URI de redirecionamento:** `http://127.0.0.1:8765/glpi`
- **Escopos:** `api` e `user`
- **Precisamos de volta:** o **Client ID** e o **Client Secret**. Ficam no arquivo local `.env` do Mac do Luis, nunca no código.

E, se puderem, os **IDs** da entidade e, para cada área, da **categoria** e do **grupo** que recebe o chamado: Jurídico, Técnico Tributário, Contratos, Pós-venda, Marketing, Financeiro, TI e "Partners (triagem)". Sem os IDs o chamado é aberto mesmo assim, só sem categoria e sem grupo, e a triagem do GLPI direciona.

## Como cada pessoa autoriza (uma vez)
1. No Mac do Luis: `python3 lib/glpi.py autorizar daniela` (ou `geovana`, `jenifer`).
2. Abre a tela de login do próprio GLPI. A pessoa entra com o **usuário dela** e clica em **Autorizar**.
3. Os agentes guardam só a chave de acesso que o GLPI fornece, em `~/agentes-partners/.glpi/`, com acesso restrito e fora do backup e do repositório. A senha nunca passa pelos agentes. A autorização pode ser revogada a qualquer momento no GLPI.

Se alguém ainda não autorizou, o chamado é aberto pela conta do Luis com a pessoa como **requerente** (opção B). Se ninguém autorizou, o chamado sai pronto no e-mail para ser copiado.

## Regras
- **Um chamado por demanda:** sem duplicar. Se a demanda já tem chamado, as novidades entram como acompanhamento.
- **Rodadas:** os agentes abrem chamados às 8h e 14h, dias úteis.
- **Teste:** `python3 lib/glpi.py testar daniela` (login e leitura). Depois, um chamado de teste numa categoria combinada com o TI.
- **Modo:** começa em `rascunho` e passa para `abrir` em `infra/glpi-config.json` quando o TI validar o teste.
