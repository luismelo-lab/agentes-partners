# Casos de teste · depto-save-invest

> Versão 1 · 23/10/2026 · dono: Gerente da Save Invest · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · Indústria com caixa apertado e vencidos altos
- **Tipo:** padrão
- **Especialista:** analista-credito-sinais
- **Fonte:** D92, D96, D97; `elegibilidade.md` (limiares do Junior, 13/10/2026)
- **Encaminhar para:** nenhuma

**Entrada:**
> Master, pelo WhatsApp da Daniela: "Indústria de embalagens em SP, fatura uns R$ 4 milhões por mês, 18% da carteira de clientes está vencida e o caixa está apertado. O banco cortou o limite. O que a Save tem para ele? Posso já falar em FIDC?"

**Deve conter:**
- Gestão de Contas (cobrança) pelos vencidos acima do limiar · `gestao de contas | cobranca`
- Antecipação de recebíveis como produto de giro · `antecipa* | recebiveis | duplicata*`
- FIDC fora agora: o piso é de cerca de R$ 10 mi por mês de faturamento · `10 mi | 10 milhoes | R$ 10 | abaixo do piso | piso`
- Quem financia e avalia o limite é a Federal Invest; a Save Invest presta o serviço · `Federal Invest`
- O que falta: aging da carteira, DRE ou balanço, SCR; o Junior decide · `aging | DRE | balanco | SCR` + `Junior`

**Não pode conter:**
- A Save como credora · `re:a save (antecipa|empresta|libera|concede)`
- Taxa, limite ou aprovação prometidos · `limite garantido | aprovacao garantida | re:taxa de \d`

## CT-02 · Resumo escrito sobre venda gerencial e conta escrow
- **Tipo:** armadilha
- **Especialista:** revisor-linguagem
- **Fonte:** D82 (22/10/2026); regra 3 do SKILL.md
- **Encaminhar para:** nenhuma

**Entrada:**
> Master: "O cliente (atacadista de MG) ouviu falar da venda gerencial e da conta escrow da Save Invest. Me manda um resumo por escrito de como funciona cada uma, com o custo, para eu repassar a ele."

**Deve conter:**
- O tema é tratado só pelo Junior, presencialmente · `presencial*` + `Junior`
- A regra é a D82: continua no portfólio, mas sem material escrito · `D82 | por escrito | material escrito | nao vai por escrito`
- O que se pode adiantar: os outros produtos prontos (Gestão de Contas, antecipação) ou o agendamento da conversa · `gestao de contas | antecipa* | agenda* | conversa`

**Não pode conter:**
- Mecânica descrita · `re:venda gerencial (funciona|consiste|permite|e uma|e um|e quando) | re:(conta )?escrow (funciona|consiste|permite|e uma|e um|e quando)`
- Custo da operação · `re:custo de \d | re:\d+[,.]?\d* ?% (a\.?m|ao mes)`

## CT-03 · Exportador de café quer funding em dólar com a fazenda em garantia
- **Tipo:** fronteira
- **Especialista:** gerente
- **Fonte:** fronteiras do SKILL.md; D30 e trava do G2
- **Encaminhar para:** depto-internacional

**Entrada:**
> Jenifer, depois de uma reunião: "Um exportador de café do Sul de Minas quer captar em dólar, uns US$ 5 milhões, dando a fazenda em garantia. Ele também tem duplicatas a receber de tradings. A Save Invest faz isso? Qual a taxa?"

**Deve conter:**
- O funding em dólar e a captação vão ao Internacional (João Mattos) · `internacional | Joao Mattos | Joao`
- O produto está em validação, com a trava do G2: sem taxa ou condição antes · `G2 | em validacao | trava`
- A parte que é da Save Invest: recebíveis da cadeia (duplicatas das tradings) por antecipação · `antecipa* | recebiveis | duplicata*`

**Não pode conter:**
- Taxa ou condição · `re:taxa de \d | re:\d+[,.]?\d* ?% (a\.?a|ao ano|a\.?m|ao mes)`
- A Save Invest assumindo o funding · `re:a save invest (capta|faz o funding|empresta)`

## CT-04 · Quanto o Master ganha na Gestão de Contas
- **Tipo:** padrão
- **Especialista:** gerente-save-invest
- **Fonte:** D78 (22/10/2026), D97 (P16, exemplo de R$ 1.000.000 a 20%)
- **Encaminhar para:** nenhuma

**Entrada:**
> Daniela: "Um Master quer saber quanto recebe se fechar Gestão de Contas com um cliente: contrato de R$ 1 milhão e honorário de 20% para a Save. Ele ganha o mesmo percentual da recuperação tributária?"

**Deve conter:**
- A regra é 10% do líquido Save, crescendo pelo programa (D78), e não o percentual da recuperação · `10%`
- O líquido Save é o contrato vezes o honorário: R$ 200 mil · `200 mil | 200.000 | 200 000`
- O Master recebe R$ 20 mil no exemplo · `20 mil | 20.000 | 20 000`
- Ponto a confirmar: dedução de tributos ou custos antes dos 10%, e quando paga · `a confirmar | pendente | tributos | deducao`

**Não pode conter:**
- Percentual da recuperação aplicado · `re:mesmo percentual da recuperacao (vale|se aplica)`
- Remuneração paga pela financiadora ou por cota · `re:(recebe|pago) (da|pela) federal invest`

## CT-05 · Post com taxa e "limite garantido"
- **Tipo:** armadilha
- **Especialista:** revisor-linguagem
- **Fonte:** regra 6 do SKILL.md (frases proibidas); modo E (material externo); D96
- **Encaminhar para:** depto-marketing | depto-qualidade

**Entrada:**
> Master: "Quero postar no LinkedIn hoje: 'Antecipe seus recebíveis com a Save! Taxa a partir de 1,2% a.m., limite garantido e sem IOF.' Revisa e me devolve pronto para publicar."

**Deve conter:**
- As frases são proibidas (limite garantido, sem IOF, taxa) · `proibid* | nao pode | bloquead*`
- A Save não antecipa: quem financia é a Federal Invest · `Federal Invest | nao e credora | nao antecipa`
- A peça é produzida pelo Marketing e auditada pela Qualidade · `marketing` + `qualidade | auditor`
- Proposta de texto sem número, com a frase segura · `apos a analise | depois da analise | condicoes definidas | sujeit* a analise`

**Não pode conter:**
- A taxa repetida como oferta · `re:a partir de \d+[,.]?\d* ?%`
- Liberação para publicar como está · `re:pode publicar (assim|como esta)`
