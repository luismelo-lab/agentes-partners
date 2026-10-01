# Chamados automáticos no GLPI · pedido ao administrador
**De:** Luis Fernando de Melo (Área Partners) · **Data:** 01/10/2026 · **GLPI:** https://tributario.savecompany.com.br

## O que queremos
Os agentes da Área Partners leem as demandas que os parceiros mandam no WhatsApp. O que eles não conseguem resolver vira **chamado no GLPI** para o time certo: Jurídico, Técnico, Contratos, Pós-venda, Marketing, Financeiro ou TI. O chamado já vai com o que o parceiro pede, o que já foi levantado no HubSpot e na Receita e o que falta. Nada é enviado a parceiros ou clientes.

## O que já verificamos (sem login)
- **Versão:** GLPI 11, com a **API v2.1 (High-Level REST API) ativa**. É ela que será usada: `/api.php/v2/Assistance/Ticket`, `/Timeline/Followup` e `/TeamMember`.
- **Autenticação:** OAuth2 (fluxo *password*). A API antiga (`apirest.php`) está desativada e continua desativada.

## O que pedimos
1. **Cliente OAuth** (Configurar → Clientes OAuth): nome "Agentes Partners", fluxo *password*, escopo `api`. Precisamos do **Client ID** e do **Client Secret**.
2. **Conta de serviço** "Agentes Partners" (usuário local), com um perfil que só permita:
   - criar chamados e acompanhamentos;
   - ler os chamados que ela mesma abriu.
   Nada de excluir, fechar, atribuir técnico ou ver outras entidades.
3. **IDs** da entidade e, para cada área, da **categoria** e do **grupo** que recebe o chamado. As áreas são: Jurídico, Técnico Tributário, Contratos, Pós-venda, Marketing, Financeiro, TI e uma fila "Partners (triagem)". Se as categorias ainda não existirem, a sugestão está em `departamentos/ti/GLPI-pronto-para-agente.md`.
4. **Requerente:** o chamado sai em nome da conta de serviço. A descrição diz quem da Partners acompanha (Daniela, Jenifer ou Geovana). Se preferirem, podemos colocar a pessoa como observadora.

## Como os agentes usam
- **Credenciais:** ficam no arquivo local `.env` (`GLPI_CLIENT_ID`, `GLPI_CLIENT_SECRET`, `GLPI_USUARIO`, `GLPI_SENHA`), nunca no código.
- **Rodadas:** os agentes abrem chamados nas rodadas das 8h e 14h, dias úteis, com no máximo um chamado por demanda (sem duplicar).
- **Teste:** `python3 lib/glpi.py testar` (login e leitura). Depois, um chamado de teste numa categoria combinada com o TI.
- **Modo:** começa em `rascunho` (o chamado aparece pronto no e-mail da Partners, para copiar). Passa para `abrir` em `infra/glpi-config.json` quando o TI validar o teste.
