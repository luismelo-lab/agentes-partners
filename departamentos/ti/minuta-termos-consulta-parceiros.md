# Minuta de termos de uso, aviso de privacidade e retenção · consulta de Lucro Real para parceiros
**Rascunho da Área Partners · 23/10/2026 · PRÉ-ANÁLISE, não substitui parecer.** Validação: advogado(a) responsável [nome a preencher]. As normas abaixo foram citadas sem consulta ao texto oficial nesta sessão: [VALIDAR] com o advogado. Nada foi publicado.

## 1. Termos de uso (texto para a tela)
**O que é.** Uma consulta de apoio para você avaliar se uma empresa que pretende atender está no Lucro Real, e receber um dossiê com a análise da Save.

**Quem pode usar.** Parceiros cadastrados e autorizados pela Save. O acesso é pessoal e não pode ser compartilhado.

**O que você se compromete a não fazer.**
1. Usar a consulta para levantar ou reconstituir a carteira de clientes da Save ou de outros parceiros.
2. Repassar o dossiê a quem não vá atender a empresa consultada.
3. Fazer consultas em volume para formar lista de prospecção. Há limite diário de uso, e o uso é registrado.
4. Apresentar o dossiê como promessa de valor, de prazo ou de êxito.

**O que a consulta não garante.** O regime tributário vem da ECF e reflete o ano-base indicado, não necessariamente o regime de hoje. As fontes são serviços públicos de consulta, sem garantia de disponibilidade. Quando não for possível seguir com a consulta, você verá uma mensagem padrão e deve falar com a Área Partners. O dossiê é informação de apoio e não substitui a análise técnica da Save sobre os documentos da empresa.

**Suspensão.** A Save pode suspender o acesso em caso de uso fora destes termos.

## 2. Aviso de privacidade (texto para a tela)
**Quais dados.** O CNPJ que você digita, o resultado da consulta, o dossiê gerado, a data e o seu usuário. Não coletamos dados de sócios, telefone, e-mail ou endereço da empresa consultada.

**Para quê.** Entregar a consulta e o dossiê, evitar que você repita pedidos (histórico das suas últimas empresas), registrar o uso e proteger o serviço contra uso indevido.

**Com quem compartilhamos.** O CNPJ é enviado a serviços públicos de consulta (Minha Receita e BrasilAPI). O dossiê é processado em ambiente de nuvem da Save (GitHub, Microsoft e Azure) e por ferramentas de inteligência artificial contratadas pela Save, que atuam como operadoras.

**Por quanto tempo.** O histórico e os dossiês ficam guardados por 12 meses. Depois, são excluídos. Você pode pedir a exportação ou a exclusão antes disso, falando com a Área Partners.

**Seu histórico é confidencial.** A lista de empresas que você consultou não é vista por outros parceiros.

## 3. Política de retenção (uso interno)
| Dado | Onde fica | Prazo | Como exclui |
|---|---|---|---|
| Pedidos, dossiês e Word | pasta restrita "Estado dos agentes" (SharePoint) e `central-esteira/pedidos/` | 12 meses | rótulo de retenção do SharePoint; no Mac, `python3 -m central_api.esteira expurgar --dias 365` (não apaga as cópias do SharePoint) |
| Histórico de consultas por parceiro | `central-esteira/historico/` | 12 meses | mesmo comando |
| Trilha de uso e de motivos de bloqueio | `dados-publicos/receita/consultas-regime.jsonl` (permissão 600, fora do git) | 12 meses | rotina do TI (a definir) |
| Índice de clientes (chaves HMAC) | `central-esteira/indice-negocios-ativos.json` | regravado a cada dia | substituído pela rotina "Dados do dia" |

## 4. Pontos para o advogado decidir
1. **Base legal do tratamento** do CNPJ e do histórico do parceiro (legítimo interesse, LGPD art. 7º, IX e art. 10?) e se é preciso registrar a avaliação do legítimo interesse. [VALIDAR]
2. **Operadores e transferência internacional** (LGPD arts. 33 e 39): GitHub, provedores de inteligência artificial e Azure. Se há cláusula contratual suficiente ou é preciso aditivo.
3. **Empresário individual:** a razão social pode ser o nome civil, que é dado pessoal. Avaliar se a consulta deve mascarar ou recusar esses CNPJs.
4. **OAB:** as "aberturas sugeridas" do dossiê orientam o parceiro a abordar o empresário. Pedir parecer de perímetro (Código de Ética, art. 7º; Provimento 205/2021) antes de liberar a seção "Como abordar" a parceiros que não sejam advogados. [VALIDAR]
5. **Modo autônomo:** a entrega sem aprovação humana só deve ser ligada depois de 30 dias de amostra humana de 20% e com a responsabilidade do dono do pedido registrada por escrito.
6. **Mensagem neutra:** confirmar que o texto padrão da tela cumpre o dever de transparência sem revelar a carteira de clientes da Save.
