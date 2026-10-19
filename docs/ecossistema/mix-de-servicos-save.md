# Mix de serviços da Save, a partir das linhas de serviço das Big Four

> 19/10/2026 · Uso interno · Dono: Luis. Base: o quadro das Big Four colado pelo Luis (descrições aceitas como recebidas, **não conferi cada afirmação** nas fontes das firmas), os produtos da Save (`ecossistema-produtos-servicos.md`), as reuniões de 13/10 e 24/09 e os playbooks setoriais.
> Regra: o mix é **inspirado** na estrutura das Big Four, não uma cópia. A Save só oferece o que tem produto, dono e trava jurídica resolvidos. Produto em validação ou definição segue como **descoberta**.

## 1. Leitura do quadro das Big Four
| Linha das Big Four | Quem destaca (no quadro) | Aplica-se à Save? |
|---|---|---|
| **Tax** (direto, indireto, conformidade, comércio exterior, preço de transferência, automação fiscal) | todas | **Sim, é o núcleo** |
| **Legal** (onde a regulação permite) | Deloitte, EY | **Sim**, com a trava da OAB (indicação, não divisão de honorário) |
| **Financial Advisory / Deals / Strategy and Transactions** (M&A, reestruturação de dívida, financiamento, estratégia de capital, IPO) | Deloitte, PwC, EY, KPMG | **Em parte**: reestruturação de dívida, funding e captação de capital sim; M&A, valuation e IPO só por parceiro |
| **Consulting de finanças e operações** (melhoria de desempenho, finanças, cadeia de suprimentos) | PwC, KPMG, EY | **Em parte**: caixa, cobrança e capital de giro; não operações nem tecnologia |
| **Risk / governança / compliance / LGPD** | Deloitte, KPMG | **Leve**: governança tributária, LGPD e prazos; sem cibersegurança |
| **Assurance / Audit** | todas | **Não**: exige independência e registro; conflita com consultoria e crédito |
| **Tecnologia, nuvem, IA, pessoas, experiência do cliente** | Deloitte, EY | **Não** como linha; só a integração gratuita da cobrança e a automação interna |
| **Foco setorial** (KPMG: agro, financeiro, energia, infraestrutura) | KPMG | **Sim**: já temos 7 playbooks setoriais; é o diferencial para o agro |

## 2. As seis linhas de serviço da Save
| # | Linha Save | Equivalente nas Big Four | Serviços (ids do motor) | Estado | Quem sustenta |
|---|---|---|---|---|---|
| L1 | **Tributário e Reforma** | Tax | Recuperação por tese e recorrência (RT), crédito presumido agro, planejamento e reforma CBS/IBS (PLAN), tax tech e SPED | Pronto | `depto-tributario`, `recuperador`, `revisor-diagnostico` |
| L2 | **Passivo e Reestruturação** | Financial Advisory (reestruturação) + Legal | Gestão de passivo e transação (PAS), defesa e contencioso (JUR), alongamento e carência de dívida bancária (ALONG) | PAS e JUR prontos; ALONG em definição | `depto-juridico`, `depto-tributario`, `depto-internacional` |
| L3 | **Caixa e Capital de Giro** | Consulting (finanças) | Gestão de Contas, cobrança com IA (GC), antecipação por instituição autorizada (ANT), FIDC e multicedente (FIDC) | GC em implantação; ANT e FIDC em definição | `depto-internacional` (ecossistema) |
| L4 | **Capital e Transações** | Deals / Strategy and Transactions | Crédito internacional (CI), captação de capital: dívida, equity, sócio (CAP), home equity (HE) | CI em validação; CAP e HE em definição | `depto-internacional` |
| L5 | **Estrutura e Patrimônio** | Tax e Legal (estruturação) | Estruturação patrimonial e sucessória (EP), certificado digital | EP em definição | `depto-juridico` |
| L6 | **Mercados Externos** | Tax internacional e comércio exterior | Maquila no Paraguai (MQ), internacionalização turnkey | MQ em estruturação | `depto-internacional` |

**Camadas transversais (não vendidas à parte, como nas Big Four):**
- **Inteligência setorial** (KPMG): 7 playbooks e especialistas por setor, que dizem qual serviço faz sentido.
- **Escritório de Valor da Conta** (PwC e McKinsey): baseline, KPI, Mapa de Valor e encontro trimestral.
- **Governança e conduta:** revisão de promessas, `depto-qualidade`, LGPD, conflito de canal.

## 3. O que fica de fora ou vai por parceiro
| Serviço | Decisão | Motivo |
|---|---|---|
| Auditoria e asseguração | **Não oferecer** | Independência, regulação e conflito com consultoria e crédito (a pesquisa de 19/10 aponta as regras de independência como referência) |
| Cibersegurança, nuvem, ERP, IA como projeto | Não oferecer | Fora do núcleo; só a integração gratuita da cobrança |
| M&A, valuation, IPO | **Por parceiro**, depois do G2 | Sem produto nem dono; pode nascer da linha L4 |
| Perícia e forense | Por parceiro | Fora do núcleo |
| ESG e rastreabilidade (ex.: EUDR no agro) | Por parceiro, como descoberta | Relevante para exportador de carne e café; sem produto |
| People advisory, cadeia de suprimentos | Não oferecer | Fora do negócio |
| Compliance e LGPD do cliente | Opcional, via `depto-juridico` | Já existe na casa; cuidado com a OAB |

## 4. Pacotes de mix por perfil (o que oferecer junto)
| Pacote | Perfil | Serviços, em ordem | Entrada |
|---|---|---|---|
| **A · Oxigenar** | Lucro Real, alimentos ou agro, com crédito a recuperar | L1 (RT, recorrência, crédito presumido) → L2 (PAS se houver débito) | Recuperação tributária |
| **B · Caixa B2B** | Vende a prazo a empresas, R$ 4,8 mi/ano ou mais | L3 (cobrança → antecipação) → L1 (planejamento e reforma) | Gestão de Contas; serve a quem ainda não abre dados |
| **C · Organizar para crescer** | Débito fiscal, muitos bancos, pouca certidão | L2 (PAS, JUR, ALONG) → L1 (créditos abatem débito) → L3 | Gestão de passivo |
| **D · Escalar com ativos** | Faturamento ≥ R$ 50 mi, ativos relevantes, projeto de uso | L5 (estruturação patrimonial) → L4 (CI em descoberta) → L3 (FIDC, ≥ R$ 10 mi/mês) | Estruturação e conversa de descoberta |
| **E · Crescer e exportar** | Demanda acima da capacidade, EBITDA pressionado por investimento | L4 (CAP: dívida, equity, sócio) → L6 (exportação, 2ª rodada) | Captação de capital em descoberta |
| **F · Indústria de mão de obra** | Confecção, têxtil, calçados no Real | L1 (CPP e folha) → L6 (MQ, descoberta) | Recuperação (folha) |

**Mix por setor (resumo dos playbooks):** proteína animal e café: A, B, D · varejo alimentar: A, C, e FIDC multicedente em escala · combustíveis e transporte: C, B · confecção: B, F · panificação e alimentos: A, B, E.

## 5. Como o mix entra no motor da base dos parceiros
- Cada produto do motor ganha sua **linha (L1 a L6)** e cada empresa recebe o **pacote** que melhor a descreve. O parceiro vê "sua carteira por linha", como um relatório de portfólio de Big Four.
- O índice de aderência soma por linha, e a regra "máximo de 2 produtos novos por vez" limita a proposta.
- Implementado no protótipo `mapa_base_parceiro.py` (campo `linha`) e no catálogo `docs/ecossistema/catalogo-mix-servicos.json`.

## 6. Prioridades para fechar o mix
| Prioridade | Ação | Dono sugerido |
|---|---|---|
| P1 | Pacotes A e B prontos para o parceiro (produtos prontos ou em implantação) | Contas e Soluções, Luis |
| P1 | Ficha própria de ALONG, CAP e HE (sem dono, critério nem preço) | João, Júnior |
| P1 | Definir quem contrata e quem presta a Gestão de Contas e a antecipação | Júnior, Jurídico |
| P2 | Pacotes D e E para o café e agro (primeiro case real do Luis) | Luis, Júnior |
| P2 | Parecer externo sobre OAB (L1 e L2), CVM (L3 e L4) e BCB | Jurídico |
| P3 | Parceiros para M&A, valuation, ESG e perícia | Luis |
| P3 | Ponte M&A: transformar a captação de capital em linha de transações | Diretoria |

## 7. Pendências
- O texto das teses e dos serviços colado na conversa "Operação agentes" ainda não foi conciliado com a linha L1.
- As descrições do quadro das Big Four são as que o Luis colou; vale conferir nas páginas das firmas antes de citar a cliente.
- O fechamento do quadro que o Luis colou perguntava se queria aprofundar Cybersecurity, M&A ou o domínio no mercado brasileiro. Tratei como parte do texto colado, não como pergunta, e não aprofundei nenhum dos três.
