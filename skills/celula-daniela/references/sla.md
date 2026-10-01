# Tabela de SLA por tipo de demanda — PROPOSTA A VALIDAR

> **Status:** proposta do agente (29/09/2026), **não combinada** com as áreas. Validar na Semana 0 com a Daniela (roteiro, bloco 3) e depois com cada área de apoio antes de cobrar alguém por esses prazos. Fonte de máquina: `sla.json` (o `pendencias.py` calcula os prazos a partir dele; ao mudar aqui, mude lá).

**Como ler:** prazos em dias úteis a partir da abertura (0 = no mesmo dia). *1ª resposta* = o parceiro fica sabendo que o pedido foi recebido e encaminhado, com previsão. *Solução* = o parceiro recebe a resposta/entrega. Feriados não são descontados pelo script.

**Referência de mercado usada para a proposta:** em programas de parceiros B2B, a prática comum é separar o *prazo de reconhecimento* (horas) do *prazo de solução* (dias) e ter prazo mais curto para o que trava venda ou tem prazo legal. Os números abaixo são ponto de partida, não benchmark medido.

| Código | Tipo de demanda | Categoria | Área de destino | Rota | 1ª resposta | Solução | Dados mínimos para encaminhar |
|---|---|---|---|---|---|---|---|
| `JUR-CONTRATO` | Dúvida sobre contrato/cláusula (cliente ou parceiro) | Jurídico | Jurídico | virtual: depto-juridico (modo B) → advogado(a) valida | mesmo dia | 3 d.u. | qual contrato (cliente ou termo de parceria); cláusula ou trecho em dúvida; pergunta do parceiro em 1 frase; negócio/cliente relacionado |
| `JUR-NOTIFICACAO` | Notificação/intimação da Receita recebida pelo cliente ⚠️ | Jurídico | Jurídico | virtual: depto-juridico (modo A, prazo com dupla checagem) + Jurídico real NO MESMO DIA | mesmo dia | prazo legal: calculado pelo depto-juridico com dupla checagem e preenchido à mão pela Daniela | cópia integral da notificação; data de ciência (quando o cliente foi notificado); CNPJ do cliente; negócio/PER-DCOMP relacionado |
| `JUR-REUNIAO` | Apoio jurídico em reunião com cliente | Jurídico | Jurídico | virtual: depto-juridico (modo D, Apoio Jurídico Comercial) | mesmo dia | 2 d.u. | data e horário; pauta / dúvida do cliente; negócio relacionado; quem participa |
| `JUR-LGPD` | Dúvida de LGPD / uso de dados de clientes | Jurídico | Jurídico | virtual: depto-juridico (LGPD & Privacidade) | 1 d.u. | 5 d.u. | situação concreta; quais dados e de quem; para que serão usados |
| `COM-STATUS` | Status de negócio / diagnóstico | Comercial | Daniela (HubSpot) → Técnico se preciso | script: briefing_master.py --negocio | mesmo dia | 1 d.u. | cliente (razão social ou CNPJ) ou ID do negócio |
| `COM-NOVO-NEGOCIO` | Registrar indicação / novo negócio | Comercial | Daniela (CRM) | script: crm_checagem.py --cnpj (duplicidade, conflito de canal, Receita) | mesmo dia | 1 d.u. | CNPJ; razão social; regime tributário; UF/cidade; quem é o contato no cliente (sem telefone no chat); documentos já enviados |
| `COM-CONDICOES` | Condições comerciais, honorário ou exceção de proposta | Comercial | Luis (decisão) | humana: Luis · apoio depto-resultados (margem) se preciso | mesmo dia | 3 d.u. | negócio; o que o parceiro pede; justificativa; valor/percentual envolvido |
| `COM-REUNIAO` | Reunião de venda ou pós-venda com cliente e parceiro | Comercial | Daniela (+ Geovana se técnica) | subagente Reuniões (briefing antes, ata depois) | mesmo dia | 2 d.u. | data e horário; objetivo; negócio/cliente; participantes |
| `TEC-DUVIDA` | Dúvida tributária / tese | Técnico | Técnico tributário (1º nível: Geovana) | virtual: depto-tributario → técnico humano valida | mesmo dia | 3 d.u. | pergunta; regime e atividade do cliente; período; negócio relacionado |
| `TEC-DOCUMENTOS` | Documentos para diagnóstico (envio ou pendência) | Técnico | Técnico tributário | humana: pedido formatado | mesmo dia | 2 d.u. | negócio; quais documentos/períodos; onde estão (link/anexo) |
| `TEC-REANALISE` | Pedido de reanálise de negócio perdido/zerado | Técnico | Geovana (Recuperador) | skill recuperador (decisão da Geovana) | 1 d.u. | 5 d.u. | negócio; o que mudou (documento novo, período, regime) |
| `CTR-ENVIO` | Envio ou ajuste de contrato do cliente | Contratos | Contratos | humana: pedido formatado | mesmo dia | 2 d.u. | negócio; razão social e CNPJ; representante legal que assina; honorário e condições aprovadas; e-mail de assinatura (vai só no pedido à área) |
| `CTR-DISTRATO` | Distrato | Contratos | Contratos + Jurídico | humana: pedido formatado + depto-juridico se houver litígio | 1 d.u. | 5 d.u. | negócio/contrato; motivo; quem pediu; valores já faturados/compensados |
| `POS-EXTRATO` | Extrato de pagamento / saldo de créditos | Pós-venda | Pós-venda | humana: pedido formatado | mesmo dia | 2 d.u. | cliente (razão social e CNPJ); período; para quando precisa (ex.: reunião) |
| `POS-GUIAS` | Guias a compensar / aviso de pagamento | Pós-venda | Pós-venda | humana: pedido formatado | mesmo dia | 2 d.u. | cliente; competência; guias/tributos envolvidos |
| `POS-COMPENSACAO` | Compensação de ofício / dúvida sobre compensação | Pós-venda | Pós-venda (+ Jurídico se houver risco) | humana + virtual: depto-juridico (Recuperação de Créditos & Compensação) | mesmo dia | 5 d.u. | cliente; PER/DCOMP ou despacho; data de ciência; valores |
| `MKT-MATERIAL` | Material/documento que já existe | Marketing | Daniela (Biblioteca de Materiais) | subagente Biblioteca de Materiais | mesmo dia | 1 d.u. | o que o parceiro vai fazer com o material (público, canal) |
| `MKT-NOVO` | Material novo, personalizado ou co-branding | Marketing | Marketing | virtual: depto-marketing → Marketing real | 1 d.u. | 10 d.u. | objetivo e público; canal (WhatsApp, evento, e-mail); prazo; se leva a marca do parceiro |
| `REP-COMISSAO` | Repasse / comissão do parceiro | Comissionamento | Financeiro / Operações de Canal (área humana) | humana: pedido formatado (depto Operações de Canal ainda não construído) | mesmo dia | 5 d.u. | negócio(s); competência; valor esperado pelo parceiro; nota fiscal do parceiro, se houver |
| `CRM-CADASTRO` | Atualizar dados de empresa/negócio no CRM | CRM | Daniela (CRM) | script: crm_checagem.py → proposta de atualização | mesmo dia | 1 d.u. | negócio; campo e valor novo; de onde veio a informação |
| `QLD-RECLAMACAO` | Reclamação ou insatisfação (parceiro ou cliente) ⚠️ | Qualidade | Luis (+ área envolvida) | humana: Luis no mesmo dia (depto Qualidade ainda não construído) | mesmo dia | 3 d.u. | o que aconteceu (fatos); negócio/cliente; o que o parceiro espera; desde quando |
| `TI-ACESSO` | Acesso ou sistema (GLPI, portal, links) | TI | TI | humana: chamado no GLPI (depto TI ainda não construído) | 1 d.u. | 3 d.u. | sistema; erro ou print; usuário afetado |
| `OUT-OUTROS` | Outros | Outros | a definir pela Daniela | Daniela decide | 1 d.u. | 5 d.u. | pedido em 1 frase; para quando precisa |

⚠️ = urgente: avisar a Daniela na hora e, no caso de notificação da Receita, o Jurídico real no mesmo dia (o prazo que vale é o legal, calculado com dupla checagem pelo `depto-juridico`).

## Perguntas para validar cada prazo
- A área de destino consegue cumprir? (perguntar à área, não presumir)
- O parceiro precisa disso para uma reunião ou um prazo legal? Então o prazo é o da reunião/lei, não o da tabela.
- Esse tipo acontece com que frequência? (vem do apontamento da Semana 0)
- Quando atrasar, quem a Daniela aciona? (escala: responsável na área → gestor da área → Luis)
