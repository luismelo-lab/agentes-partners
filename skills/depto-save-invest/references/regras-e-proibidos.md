# Save Invest · Regras e proibidos

Última revisão: 22/10/2026. Vale para todo especialista da área e para todo rascunho a parceiro ou cliente. Em divergência entre esta lista e uma fala de reunião, vale a decisão registrada (D-número); a fala vira pergunta ao Junior.

## 1. Regras inegociáveis
1. **A Save não é credora.** A Área Partners e a Save Co. não concedem crédito, **não antecipam recebíveis** e **não distribuem cotas**. Quem antecipa é quem tem o enquadramento: instituição autorizada pelo Bacen (Lei 4.595/1964), FIDC (Res. CVM 175/2022), securitizadora (Lei 14.430/2022) ou fomento mercantil com capital próprio. Diga sempre quem opera.
2. **Nunca prometa** taxa, valor, limite, prazo de liberação, aprovação de crédito, percentual de recuperação ou economia. "Condições definidas por quem opera, depois da análise."
3. **Venda gerencial e conta escrow (D82, 22/10/2026):** existem no portfólio, são sensíveis e **só o Junior trata, presencialmente**. Os agentes não descrevem mecânica, preço, efeito ou exemplo em nenhuma peça, mensagem, FAQ, ata ou rascunho. Frase única: "Esse ponto é tratado diretamente pelo Junior, da Save Invest, em conversa presencial."
4. **Remuneração do parceiro (D78, 22/10/2026):** começa em **10% do líquido Save**, crescendo pelo programa (Gilberto). Na antecipação e no FIDC, o parceiro nunca recebe da instituição ou do fundo: recebe da Save, se e quando a Save receber. Ninguém recebe por cota vendida ou por "trazer investidor" (distribuição de valor mobiliário, Res. CVM 160/2022 e Lei 6.385/1976, art. 27-E).
5. **Estatística de mercado não é dado próprio** (Junior, 13/10, T8). Os números de inadimplência e recuperação citados são de mercado; a Save Invest não tem BI. Cada cliente exige estudo individual.
6. **Nada é gravado nem enviado.** Não alterar HubSpot nem GLPI. Tudo é rascunho para o Luis aprovar. Material para fora passa pelo `depto-qualidade` (`depto-qualidade/scripts/auditar_texto.py`).
7. **Dados de cliente ficam no Mac (LGPD).** Não levar CNPJ, DRE, SCR, carteira ou nome de devedor para busca web. Nos arquivos, use `<EMPRESA>`. Nunca ler `.env`.
8. **Multicedente/multissacado e FIDC com cadeia de terceiros:** os fornecedores e clientes da cadeia não são clientes da Save até contratarem; não se aborda a cadeia sem o cliente-âncora autorizar.

## 2. Frases proibidas → o que dizer
| Proibido | Por quê | Diga |
|---|---|---|
| "A Save antecipa" / "a Save libera 30% na hora" | Antecipar é operação de crédito de quem tem enquadramento; "na hora" promete prazo | "A antecipação é feita por quem opera a carteira (rede Federal Invest ou instituição parceira), depois da análise de crédito. O limite de referência parte de 30% da carteira registrada." |
| "Limite garantido de 30%" | Há comitê de crédito (13/10, T11) | "O limite automático de referência é de 30% da carteira registrada, sujeito ao comitê de crédito." |
| "Recuperamos 90% da inadimplência" / "eficiência 80% maior" | Dado de mercado e fala do dono, não resultado próprio | "No mercado B2B, cerca de 20% dos títulos não são pagos até o vencimento; o resultado de cada carteira depende de estudo." |
| "Custo zero" / "de graça" para a cobrança | O devedor paga multa e juros; a remuneração existe | "Sem mensalidade e sem implantação: a remuneração vem da multa e dos juros pagos pelo inadimplente." |
| "Invista no fundo" / "rendimento de X%" / "fundo da Save" | Oferta de valor mobiliário (CVM) | "O FIDC é estruturado com administrador, gestor e custodiante habilitados; a distribuição de cotas é feita por instituição do sistema de distribuição." |
| "FIDC para qualquer empresa" | Custo de ~R$ 80 mil/mês (13/10) | "O FIDC faz sentido a partir de uma escala de recebíveis; avaliamos caso a caso." |
| "Blindagem", "proteção contra bloqueio", "à prova de penhora" | Risco de fraude contra credores e à execução (CC arts. 158–165; CPC art. 792) e D82 | Não tratar. Encaminhar ao Junior (presencial). |
| "IA decide quem paga" / "cobrança 100% automática sem humano" | Exceções têm humano (13/10, T7); LGPD art. 20 | "A IA faz os lembretes e a régua; exceções são tratadas por uma pessoa." |
| "Negativamos e protestamos todo mundo" | CDC art. 42 e 71 (B2C); abuso de direito (CC art. 187) | "Negativação e protesto só quando o cliente decide, com aviso prévio ao devedor." |
| "Sem IOF" | Antecipação e factoring têm IOF (Decreto 6.306/2007, art. 7º) | "O IOF incide conforme a operação e entra no custo total informado na proposta." |
| "Holding" | Termo impreciso (13/10, T28) | "Estruturação patrimonial" (produto do jurídico) |

## 3. Regulação que limita o produto (resumo; detalhe no especialista Regulatório)
| Tema | Regra | Norma |
|---|---|---|
| Antecipação | Operação de crédito; operar sem autorização é crime | Lei 4.595/1964; Lei 7.492/1986, art. 16 |
| Fomento mercantil | Compra com capital próprio, não capta do público, não faz empréstimo nem cheque especial | Lei 9.249/1995, art. 15, §1º, III, "d"; Decreto 6.306/2007, art. 2º, I, "b" (IOF) |
| Cessão do crédito | Notificar o devedor; cedente responde pela existência, não pela solvência (salvo cláusula) | Código Civil, arts. 286–298 (290, 295, 296) |
| Duplicata | Só com venda ou serviço efetivo; duplicata simulada é crime | Lei 5.474/1968, art. 2º; Código Penal, art. 172 |
| Registro | FIDC registra direitos creditórios registráveis em registradora; duplicata escritural em escrituradora | Res. CVM 175/2022, Anexo II; Lei 13.775/2018; Res. BCB 339/2023 |
| FIDC | Cotas são valor mobiliário; administrador e gestor são prestadores essenciais registrados | Res. CVM 175/2022; Res. CVM 21/2021; Res. CVM 160/2022 |
| Cobrança B2C | Sem ridículo, constrangimento ou ameaça; repetição em dobro; crime | CDC, arts. 42, 42-A e 71 |
| Negativação | Comunicação prévia escrita; exclusão em 5 dias úteis após pagamento | CDC, art. 43, §2º; Súmulas STJ 359, 404, 548 |
| Dados | Base legal, operador com contrato, decisão automatizada | LGPD, arts. 7º, 20, 37, 39, 42, 46 |
| WhatsApp | Opt-in obrigatório; template aprovado; "cobrança de dívidas" listada como uso proibido | Política de Mensagens do WhatsApp Business (versão de 23/09/2026) |

## 4. O que exige humano antes de seguir
- **Junior:** venda gerencial, escrow, taxa, limite acima de 30%, garantia real, qualquer caso de FIDC.
- **Jurídico (`depto-juridico` + advogado):** contrato de cobrança, DPA (LGPD), política do WhatsApp, enquadramento de quem antecipa, papéis no FIDC, cliente em recuperação judicial, devedor pessoa física.
- **Tributário (`depto-tributario`):** IOF, tributação do FIDC e do cotista, efeito tributário da cessão.

## 5. Conflitos conhecidos (registrar, não resolver sozinho)
| # | Conflito | Fontes | Quem decide |
|---|---|---|---|
| C1 | **Venda gerencial e escrow.** O Junior apresentou os dois como diferencial comercial, e o resumo pôs o Luis para "apresentar" a venda gerencial (13/10, T13 e T15). A pré-análise jurídica de 22/10 recomendou não estruturar nem indicar o primeiro tema e registrou ressalvas ao segundo (`docs/portfolio-2027/agentes/juridico-revisao.md` §2.1 e §2.2; os agentes não reproduzem o conteúdo). A D82 manteve os dois no portfólio, só presencial com o Junior | 13/10; juridico-revisao 22/10; D82 | Luis com Junior e advogado. Até lá, vale a D82 (agente não descreve) |
| C2 | **"A Save não antecipa" × fala do Junior.** O Junior disse que créditos antecipados "pertencem à agência/Save Invest" e que 3 a 4 agências dividem o risco em pool, com voto do originador em dobro (13/10, T11 e T13). Se a Save Invest é agência da rede, ela compra crédito e assume risco: o enquadramento é fomento mercantil (capital próprio) e o limite especial "tipo cheque especial" seria empréstimo, que factoring não pode fazer | 13/10; Lei 4.595/1964; Lei 7.492/1986 | Junior + Jurídico (P3, P14, P15) |
| C3 | **FIDC pronto × MVP.** O Luis classificou FIDC como pronto em 19/10. Na reunião de 13/10, o FIDC foi tratado como MVP ("validado só quando o 1º recurso cai") e o multicedente ficou "a aprofundar". Não há caso de FIDC estruturado pela Save Invest nas fontes | 19/10; 13/10 T32 e T35; `ecossistema-financeiro-reuniao-2026-10-13.md` | Luis com Junior (P21) |
| C4 | **Remuneração do parceiro.** A D78 fixa 10% do líquido Save. Em 13/10 ficou "remuneração de parceiro em MVP só depois da validação"; o estudo de preços propôs faixas de 10 a 20% para produto financeiro maduro (`precos-fees.md`, proposta, não decisão) | D78; 13/10 T32 | Vale a D78. Falta base de cálculo (P16, P22) |
| C5 | **"Cobrança de dívidas" no WhatsApp.** A política da Meta lista cobrança de dívidas entre usos proibidos; o produto é cobrança por WhatsApp | Política WhatsApp Business 23/09/2026; 13/10 T6 | Jurídico + Junior (P8) |

## 6. Confirmado pelo Luis em 22/10/2026 (D96)
- O cliente contrata a Save Invest, que presta o serviço. A **Federal Invest é a financiadora**: ela antecipa, avalia o limite especial e tem o registro na CVM. A Save Invest não é credora, não antecipa e não concede limite.
- O conflito C2 (§5) está resolvido nesse sentido. Os conflitos C1, C3, C4 e C5 continuam abertos.

## 7. WhatsApp sem a API oficial (D97, 22/10/2026)
- A cobrança roda hoje **fora da API oficial do WhatsApp**. Riscos: o número pode ser bloqueado, os termos do WhatsApp proíbem automação não oficial, a política de 23/09/2026 proíbe "cobrança de dívidas" e há exposição na LGPD quanto à base legal e ao opt-out.
- O que os agentes fazem: não prometem canal "garantido" e não descrevem o envio como "oficial". Na qualificação, perguntam se o cliente aceita outros canais de reserva (e-mail, SMS, boleto registrado, Pix Cobrança). Registram o risco no parecer para o Junior.
- O que só o Junior e o Jurídico decidem: a migração para a API oficial, o enquadramento como lembrete de fatura e o plano de contingência. O produto segue enquanto isso.
