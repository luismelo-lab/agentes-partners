# Perguntas ao dono · TI, Automação & Governança de IA

O que o TI da Save, o time de CRM, o Jurídico ou o Luis (só alçada dele: orçamento, política, autonomia) respondem. Reclassificado em 23/10/2026 (`infra/alcadas.md`). Aberta em 23/10/2026 (aprofundamento sênior, D93). Quando a resposta vier, registrar data e quem respondeu, levar a regra para o arquivo do especialista e riscar a linha.

| # | Data | Para quem | Pergunta | Por que importa | Especialista |
|---|---|---|---|---|---|
| T1 | 23/10/2026 | TI | Quem é o responsável no TI e qual o prazo escrito para o Graph (caixa compartilhada + aplicativo) e o cliente OAuth do GLPI? (D46 já pedia prazo escrito) | Em 22/10/2026: 123 e-mails retidos e 11 chamados parados | Arquiteto, Incidentes |
| T2 | 23/10/2026 | TI | O escopo do aplicativo no Exchange será feito por RBAC for Applications (substituto das Application Access Policies)? | O pedido de 30/09 cita Application Access Policy, em descontinuação | Arquiteto, Identidade |
| T3 | 23/10/2026 | TI | Quando sai a etapa 0 do SSO (redirect, escopo `Central.Acesso`, papéis, atribuição obrigatória, Acesso Condicional com MFA)? | Etapas 1 e 2 prontas desde 19/10 com 28 testes; D89 aprovada | Identidade |
| T4 | 23/10/2026 | Jurídico | Quem é o controlador e o encarregado (DPO) que decidem a comunicação de incidente à ANPD? A Save é agente de pequeno porte? | Prazo de 3 dias úteis (Res. CD/ANPD 15/2024) e prazo em dobro para pequeno porte | Incidentes, Identidade |
| T5 | 23/10/2026 | Luis / Jurídico / TI | A política de uso de IA v1 (no inventário) está aprovada? | Base de toda ficha de avaliação e da transparência ("Preparado com IA?") | Governança de IA |
| T6 | 23/10/2026 | Luis | Qual o orçamento de nuvem e quem paga (Static Web Apps Standard, Table Storage, Power Automate Premium ou Azure Function, GitHub)? | Preços não confirmados na consulta; sem orçamento a nuvem não liga | Operação e Custos |
| T7 | 23/10/2026 | TI | Quando sai o repositório privado na organização da Save no GitHub? | Destrava as rotinas na nuvem (fim do Mac como ponto único) | Operação e Custos |
| T8 | 23/10/2026 | Gerente de TI (vale a recomendação em 28/10/2026; o Luis pode reverter) | Que RTO e RPO valem para plano do dia, relatório de segunda, lote do Recuperador e chamados? | Define a prioridade da continuidade | Operação e Custos |
| T9 | 23/10/2026 | TI | O GLPI terá homologação? As áreas de apoio trabalham dentro do GLPI? Plugin Fields ou formulários nativos? Política de retenção de chamados e anexos? | Teste de escrita na API v2, OLA e LGPD (art. 16) | Administrador GLPI |
| T10 | 23/10/2026 | CRM da Save | Quando entra o escopo de leitura de arquivos (`files.ui_hidden.read`) no app privado do HubSpot? | Destrava ~2.241 pareceres e substitui os 4.748 links públicos do Bitrix24 | Arquiteto, Identidade |
| T11 | 23/10/2026 | TI | O webhook de consulta do Bitrix24 (usuário técnico só leitura) e o receptor do Eazybe serão criados? | Execução dos ganhos e WhatsApp direto | Arquiteto |
| T12 | 23/10/2026 | TI | O documento do cockpit no Firestore está com leitura pública? | Achado de 29/09/2026 ainda sem resposta | Identidade |
| T13 | 23/10/2026 | Gerente de TI (define a data e avisa no resumo semanal) | Quando acontece a primeira revisão trimestral de governança (inventário × `ls`, escopos, conectores sem uso)? | Inventário v1.1 (02/10) lista 5 tarefas; o Mac tem 8 | Governança de IA |
| T14 | 23/10/2026 | Gerente de TI com a área dona da rotina (vale a recomendação em 28/10/2026; o Luis pode reverter) | D46, D67 e D72 (pmset, dono por sentinela, alerta do relatório às 07h30) seguem pendentes. Quando entram? | Alertas de falha são a regra nova do incidente do `master-sync` | Incidentes, Operação |
