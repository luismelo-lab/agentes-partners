# Segurança & LGPD técnica — checklists

## Classificação de dados (uso nos agentes)
| Classe | Exemplos | Regra |
|---|---|---|
| **C0 Público** | Dados abertos do CNPJ (Receita), normas, jurisprudência | Pode ir para ferramentas externas |
| **C1 Interno** | Pipeline agregado, métricas da área, taxonomia do GLPI | Só em ferramentas corporativas (Claude Enterprise, OneDrive da Save) |
| **C2 Confidencial** | Pareceres, diagnósticos, valores de crédito, honorários, dados de clientes e parceiros, chamados | Só local ou em sistema com controle de acesso; nunca em link público, busca web ou serviço de terceiros sem contrato; mínimo necessário no prompt |
| **C3 Restrito** | Credenciais, dados bancários, CPF/documentos pessoais, SPED e folha (fora da fase 1 pela D3), dados sensíveis (art. 5º, II, LGPD) | Agente não lê nem grava; fica fora de prompts, chamados e planilhas de trabalho |

## Checklist de acesso (todo pedido de credencial ou escopo)
- [ ] Escopo mínimo nomeado (ex.: `files.ui_hidden.read`, não "acesso total")
- [ ] Somente leitura, salvo decisão escrita do Luis + TI
- [ ] Conta de serviço (não a conta pessoal de alguém), com dono humano
- [ ] Onde a credencial fica (ex.: `.env` com permissão 600, fora do backup e do Git) e quem pode vê-la
- [ ] Rotação (sugestão: 90 dias) e como revogar em 1 minuto
- [ ] Registro de uso (log de chamadas da API, quando o sistema oferece)
- [ ] Credencial nunca trafega por e-mail, WhatsApp ou chat

## Checklist LGPD técnica (todo fluxo novo)
- [ ] Quais dados pessoais (nome, telefone, e-mail de contato de parceiro/cliente; sócios)
- [ ] Origem e finalidade (a base legal é validada pelo Jurídico)
- [ ] Onde ficam, quem acessa, por quanto tempo (retenção) e como são descartados
- [ ] Minimização: o agente precisa mesmo desse dado? (ex.: telefone não entra no chat)
- [ ] Operadores/terceiros envolvidos e se há contrato (Anthropic via plano Enterprise; Meta/BSP no WhatsApp; Microsoft; HubSpot; GLPI hospedado onde?)
- [ ] WhatsApp Business API oficial: opt-in registrado antes de mensagem ativa; mensagens fora da janela de 24 h só com modelo aprovado pela Meta; nada de disparo por automação não oficial
- [ ] Direitos do titular: como localizar e apagar os dados de uma pessoa se ela pedir

## Achados abertos (29/09/2026) — ver `~/agentes-partners/departamentos/ti/chamados-rascunho.md`
1. Links públicos do Bitrix24 nos campos de arquivo do HubSpot (4.748 links, sem expiração).
2. Falta de escopo de leitura de arquivos no app privado do HubSpot (625 arquivos dos ganhos; 2.241 na base).
3. Documento do cockpit S&OE no Firestore lido sem autenticação (a confirmar pelo TI).
4. Muitos plugins/conectores de terceiros instalados no Claude do Luis sem uso na área (ver inventário).
