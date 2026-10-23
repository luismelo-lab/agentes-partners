# Matriz de alçada e recomendação que vale por padrão

Regra do Luis de 23/10/2026: as decisões estavam todas com ele. Havia 54 itens "pendente" em `conselho/decisoes.md` e cerca de 30 na folha por semana. Esta matriz diz quem decide o quê. Para o que é reversível e está dentro das regras, a recomendação das áreas vale se não houver resposta até o prazo.

## 1. Quem decide
| Tipo de decisão | Exemplos | Quem decide | Precisa do Luis? |
|---|---|---|---|
| **Operacional, reversível e dentro das regras** | Rascunho de resposta ao parceiro, ajuste de lista de prospecção, priorizar o lote, encaminhar a outra área, corrigir dado no rascunho do CRM, formato de relatório | A pessoa dona da entrega (Daniela, Jenifer, Geovana) com o gerente da área de agentes | Não. Vai no resumo semanal |
| **Técnica de caso** | Tese aplicável a um cliente, documento a pedir, prazo de um despacho | Time técnico ou advogado humano, com a pré-análise da área | Não, salvo se mudar regra |
| **Encaminhamento de produto pronto** | Mandar oportunidade à Save Invest, ao Jurídico ou ao Paulo | Contas e Soluções, com aviso ao dono do produto | Não |
| **Regra, preço, meta ou remuneração** | Honorário, repasse, meta, tese na vitrine, frase permitida | Luis (com o Conselho quando valer) | Sim |
| **Produto novo ou em validação** | Condição dita ao cliente, G0 a G4, parceria | Luis com o dono do produto (João, Paulo, Junior) | Sim |
| **Material externo em escala** | Campanha, kit, envio em massa | Luis vê um exemplo antes | Sim, só o exemplo |
| **Irreversível ou com exposição** | Envio a cliente, contrato, assinatura, publicação, gasto | A pessoa responsável, com aprovação explícita | Conforme a regra da casa |

**Limites para subir ao Luis:** muda regra; mais de R$ 1 mi de crédito com decisão; envolve 3 ou mais áreas em conflito; produto em validação; risco jurídico ou de LGPD sem precedente na base.

## 2. Recomendação que vale por padrão
- Cada item da folha de decisões traz `padrao: true` quando é **reversível e dentro das regras**. Esses itens mostram na coluna "Se não responder" a frase "vale a recomendação em <prazo>".
- Na consolidação de sexta, o item `padrao: true` sem resposta e com prazo vencido é aplicado com a recomendação das áreas. Ele é registrado como "aplicado por padrão" em `conselho/decisoes.md` e aparece no resumo para o Luis poder reverter.
- Não valem por padrão: preço, meta, remuneração, tese na vitrine, frase permitida, produto em validação, contrato, envio externo e qualquer coisa irreversível. Esses itens ficam na folha até a resposta.
- O Luis reverte a qualquer momento: basta marcar "Reprovar" no item.

## 3. Onde se aplica
- `infra/folha_decisoes.py`: coluna "Se não responder" e campo `padrao`.
- `rotinas/consolidacao-semanal.md`: passo 7 aplica os itens vencidos com `padrao: true`.
- `skills/gabinete` e `skills/central-agentes`: usam a seção 1 para decidir se o pedido sobe.
