# Conectar o ecossistema Save à base de clientes dos parceiros

> 19/10/2026 · Uso interno · Dono: Luis. Protótipo: `skills/depto-solucoes/scripts/mapa_base_parceiro.py`; exemplo fictício em `docs/ecossistema/exemplo/`.

## 1. O objetivo, como entendi
Cada parceiro (escritório contábil ou consultor) tem uma **carteira de empresas** que a Save ainda não atende. O ecossistema (recuperação, contas, passivo, planejamento, estruturação, crédito e capital) precisa **chegar a essas empresas pelo parceiro**: saber **quais** empresas cabem em **quais** produtos, **por onde abrir** a conversa, **quem conduz** e **o que o parceiro ganha**. O estudo em Word ajuda na conversa, mas o que falta é o **motor** que liga produto, empresa e parceiro.

## 2. O que já existe e o que faltava
| Peça | Estado |
|---|---|
| Regras de aderência produto × empresa (`mapa_conta.py`, tabela `PRODUTOS`, teses por segmento) | Existe, mas só para **clientes já ganhos** (usa parecer e HubSpot) |
| ICP, lead scoring e prospecção pela Receita (`depto-intel-comercial`) | Existe, centrado em **recuperação tributária** |
| Playbooks de 7 setores, esteira em 3 ondas, ficha dos produtos financeiros | Existe |
| **Modo prospect: a carteira do parceiro, empresa por empresa, contra todo o ecossistema** | **Não existia.** O protótipo cobre isso |
| Produtos que dependem de resposta do dono (alongamento, home equity, captação) | Sem regra; entram por questionário |
| Visão para o parceiro ("sua carteira") e rotina de convite | Não existia |

## 3. O motor em quatro camadas
1. **Entrada:** CSV do parceiro com CNPJ (obrigatório) e o que ele souber: regime, faturamento, vende a prazo a empresas, tem imóvel quitado, exporta, quantos bancos, mês em que o caixa aperta.
2. **Enriquecimento local:** base da Receita (CNAE, porte, capital, situação). **Faturamento da Receita só dá um piso** (porte "Demais" = acima de R$ 4,8 mi) e é marcado como estimado. Regime só vem do parceiro ou da consulta a prospects já prevista no `depto-intel-comercial`.
3. **Aderência:** as mesmas regras do cliente ganho, mais três produtos por questionário (alongamento de dívida bancária, home equity, captação de capital). Cada oportunidade sai com **motivo**, **onda** e **estado do produto**.
4. **Porta de entrada:** primeiro produto **pronto** com aderência média ou alta (por onda). Se só houver produto em definição, vira **descoberta**, sem taxa, prazo ou fee. Para quem não abre e-CAC, DRE e balanço, a alternativa é **Gestão de Contas** (regra de 13/10).

## 4. Qual produto abre qual empresa
| Perfil da empresa na base | Entrada | Depois |
|---|---|---|
| Lucro Real, alimentos ou agro, com compras com alíquota zero | Recuperação tributária | Passivo, planejamento e reforma, depois conta e capital |
| Vende a prazo a empresas (B2B), a partir de R$ 4,8 mi/ano | Gestão de Contas (cobrança, pago no êxito) | Antecipação por instituição autorizada, depois FIDC |
| Débito fiscal ou sem certidão | Gestão de passivo | Crédito só depois da certidão |
| Muitos bancos e despesa financeira alta | Alongamento e carência (descoberta) | Funding, se houver ativo |
| Ativo relevante e projeto de uso (a partir de R$ 50 mi/ano) | Estruturação patrimonial | Crédito internacional (descoberta) |
| Indústria intensiva em mão de obra, no Real | Recuperação (folha) | Maquila (descoberta; frigoríficos bloqueados) |
| Cresce acima da capacidade | Captação de capital (descoberta) | Exportação, em segunda rodada |

## 5. Questionário de descoberta do parceiro (8 perguntas, 10 minutos)
Preenche o que o dado público não mostra e alimenta o CSV: (1) vende a prazo a empresas? (2) quanto está vencido hoje? (3) em que mês do ano o caixa aperta? (4) quantos bancos e quanto paga de parcelas por mês? (5) antecipa recebível, e a que custo? (6) tem débito ou certidão pendente? (7) tem imóvel ou terra quitados? (8) exporta, ou a demanda é maior do que a capacidade?

## 6. O que o parceiro recebe
- **"Mapa da sua carteira"** (Excel, padrão Save): empresas ordenadas por aderência, produto de entrada e pergunta de abertura por empresa; quantas empresas cabem em cada produto; dados a pedir.
- **Roteiro de abordagem pelo próprio parceiro**, com a pergunta de abertura e a frase de valor. A Save não aborda a empresa por fora.
- **Acompanhamento:** estado de cada empresa no HubSpot e Mapa de Valor quando houver resultado.
- **Remuneração:** como hoje na recuperação (Operações de Canal). Em produto novo, só depois da validação (D61 e regra de 13/10).

## 7. Regras de proteção
1. **LGPD:** a carteira é do parceiro. Antes de o CSV entrar, o Jurídico define o papel (parceiro controlador, Save operadora) e o contrato. Sem lista comprada e sem contato de sócio sem a base de legítimo interesse validada.
2. **Canal:** o motor consulta o HubSpot pela raiz do CNPJ e sinaliza empresa já cliente, em negociação ou de outro parceiro. A decisão de conflito é do Luis.
3. **Travas de produto:** crédito internacional, FIDC, Maquila, antecipação, Gestão de Contas e estruturação patrimonial saem como **descoberta**. A Save é estruturadora, nunca credora.
4. **Nada é gravado no HubSpot.** O resultado é rascunho; o técnico confirma as teses; o `depto-qualidade` audita o material antes de sair.

## 8. Métricas do funil por parceiro
Empresas na carteira · com CNPJ válido e ativo · com aderência média ou alta · conversas abertas · diagnósticos pedidos · primeiro negócio ganho · produtos por cliente (alvo: dois) · tempo até o primeiro negócio. Compara parceiros e mostra onde o canal trava.

## 9. Limites do protótipo (testado só com base fictícia)
- Não rodou com dados reais: a base da Receita e o HubSpot estão na máquina do Luis, não no ambiente em nuvem.
- Os motivos reaproveitados de `mapa_conta.py` falam em "parecer" e "débitos no parecer"; para prospect, o dado veio do parceiro. Ajustar o texto.
- As regras de alongamento, home equity e captação são **provisórias** (ficha sem dono nem critério). Validar com o João e o Júnior.
- Hoje quase toda empresa entra por recuperação tributária, porque o catálogo cobre o perfil; o peso dos demais produtos precisa de calibragem com dados reais de conversão.
- Não há ainda o Excel do parceiro nem o roteiro de abordagem gerados automaticamente.

## 10. Perguntas para você
1. A base dos parceiros hoje está **onde**: planilha que o parceiro envia, empresas no HubSpot associadas ao parceiro, ou outro lugar?
2. O parceiro costuma saber só o CNPJ, ou também faturamento e regime?
3. A entrada padrão para empresa sem dado deve ser **recuperação** (catálogo) ou **Gestão de Contas**?
4. Posso montar o "Mapa da sua carteira" em Excel e o roteiro de abordagem como próximo passo e rodar com uma carteira real, na sua máquina?
