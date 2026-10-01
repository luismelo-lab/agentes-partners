# Critérios de qualificação — Central BDR (proposta v1, 29/09/2026)

> Tudo aqui é proposta para o Luis validar. Os pesos do score ficam em `config-jenifer.json` (chave `score`) e o lead scoring de segmento/regime vem da Inteligência Comercial (`icp-*.json`, pendente de validação).

## 1. Encaixe (fit) — antes do contato, pela lista (automático, `lista_master.py`)
| Critério | Regra | Por quê |
|---|---|---|
| Situação cadastral | Ativa na Receita | Baixada/inapta não tem crédito a pedir |
| Estabelecimento | Matriz (uma linha por raiz do CNPJ) | A tese é por empresa; evita duplicar filiais |
| Regime | Lucro Real (principal) · Presumido (aderência baixa/média) · **Simples = descarta** | Crédito não cumulativo depende do regime |
| Porte e capital | EPP ou Demais; capital ≥ R$ 100 mil; acima de R$ 500 mi → Contas estratégicas | Honorário esperado × esforço |
| Segmento | Classes CNAE em que o Master já ganha + prioridades do Q4 (parâmetro, D7-b pendente) · **café fora** | Onde a Save e o Master já sabem ganhar |
| Território | UF e municípios onde o Master já ganha | Respeita a base do Master e facilita a apresentação |
| Aderência à matriz | alta / média / baixa (matriz tese × perfil do Tributário) | Probabilidade de haver tese |
| Sinais | Filial aberta nos últimos 12 meses | Crescimento = mais créditos e mais apetite |
| Alertas | "Recuperação judicial"/"falida" no nome → avaliar com o Jurídico | Risco de receber |

## 2. Conflito de canal (bloqueia a sugestão)
Checagem pela **raiz do CNPJ** (8 dígitos) no último download do HubSpot e no registro interno de reservas:
- **Já é cliente** (negócio ganho, qualquer parceiro) → não abordar.
- **Negócio aberto** com qualquer parceiro → não abordar.
- **Perdido há menos de 12 meses** → não abordar como novo; avaliar com a Geovana (Recuperador) e o Luis.
- **Desqualificado no pipeline BDR/SDR há menos de 180 dias** → não reabordar.
- **Sugerido a outro Master** nos últimos 45 dias (`listas/reservas.json`) → o Luis decide.
- **Sem CNPJ no card, mas nome igual** → "possível conflito: conferir".
Limite conhecido: o download cobre a Área Master desde 2024 (Daniela + roster). Negócios de outros canais fora desse recorte não aparecem: na dúvida, a Jenifer pergunta à Daniela antes do toque 1.

## 3. Qualificação na conversa (SQL) — a Jenifer marca depois da reunião
Adaptado de BANT/MEDDIC para recuperação de crédito:
| Letra | Pergunta | Qualifica quando |
|---|---|---|
| **R** Regime | Qual o regime hoje e nos últimos 5 anos? | Lucro Real (ou Presumido com tese específica) |
| **D** Decisor | Quem decide contratar? Quem precisa aprovar? | Sócio/CFO participou ou está agendado |
| **A** Arquivos | Tem EFD-Contribuições dos últimos 5 anos? e-CAC/procuração? | Sim ou consegue em até 15 dias |
| **C** Contador | O contador apoia ou resiste? | Apoia ou é neutro |
| **H** Histórico | Já fez recuperação? Com quem, qual período e tese? | Não, ou ficou período/tese de fora |
| **U** Urgência | Há motivo para agir agora? (caixa, fim do PIS/COFINS em dez/2026, decadência mensal) | Sim |

**SQL = R + D + A** e nenhum veto. **C, H e U** entram como prioridade. Com SQL, o lead vai ao Master com a ficha (SLA de aceite: 3 dias úteis, proposta).

## 4. Motivos padronizados de descarte
Simples/regime sem tese · Já é cliente/conflito de canal · Sem interesse · Já recuperou com outra empresa · Porte/valor baixo · Sem documentos (EFD) · Pediu para não contatar (opt-out) · Master não aceitou · Outro.
(Iguais à lista do `Controle-Followup-Jenifer.xlsx`, para medir onde o funil perde.)

## 5. Etapas do funil da Jenifer
Conta-alvo → Aguardando apresentação do Master → Em cadência → Respondeu → Reunião agendada → Reunião realizada → Qualificado (SQL) → Enviado ao Master/Técnico · (Nutrição) · (Descartado).
