# Montador de Minuta — como trabalhar (v1)

## Princípio
O Montador **preenche**; não **cria**. A Save ainda não entregou os modelos aprovados a este departamento (29/09/2026). Até lá, a entrega é **ficha de dados + pontos para o Jurídico**, não minuta.

## Onde ficam os modelos
`~/agentes-partners/departamentos/contratos/modelos/` — um arquivo por modelo, com nome `AAAA-MM-DD-<tipo>-v<N>.<docx|md>` e, no topo, **quem aprovou e quando**. Tipos esperados (confirmar com a área real): contrato de prestação de serviços com cliente (êxito) · aditivo de escopo/tese · distrato · termo de parceria/indicação com o parceiro · procuração/autorização e-CAC (se for anexo).
Modelo sem aprovação registrada = não usar.

## Passo a passo
1. Confirme o **modelo vigente** para o tipo de pedido (tese, pipeline, parceiro). Registre versão e data.
2. Monte a **ficha de dados** (só com itens ✅ do checklist):
   `razão social (Receita) · CNPJ formatado · endereço da sede · signatário e qualificação (conferido no QSA por pessoa) · parceiro · tese/escopo · % de honorário · base de cálculo do êxito conforme o modelo · forma e momento de pagamento conforme o modelo · período de apuração · negócio HubSpot (link)`.
3. Substitua **somente** os campos variáveis do modelo. O que não tiver dado fica `[PREENCHER: <o quê> — <quem informa>]`.
4. Se o caso pedir algo que o modelo não cobre, **não escreva a cláusula**: registre em "pontos para o Jurídico" e, se ajudar, uma sugestão marcada `[SUGESTÃO — VALIDAR JURÍDICO]`.
5. Rode a Parte D do checklist e entregue ao Revisor.

## Pontos que o Jurídico real precisa validar (lista-base; inclua os que se aplicam)
| Tema | Por que importa | Referência |
|---|---|---|
| Remuneração/repasse ao parceiro | Se a Save atua como sociedade de advogados, dividir honorários com não advogado é vedado; estruturar como indicação comercial | art. 34 da Lei 8.906/94 · `depto-juridico/references/riscos-chave.md` [VALIDAR estrutura societária] |
| Base de cálculo do êxito | Incide sobre ressarcimento **recebido**? E quando a Receita faz **compensação de ofício** (o cliente não recebe o dinheiro, mas quita débito)? | modelo + `depto-pos-venda/references/compensacao-de-oficio.md` |
| Momento do pagamento | Na ordem bancária do ressarcimento, na ciência do despacho, mensal? Define o aviso de pagamento do Pós-venda | modelo |
| Via do pedido | Alíquota zero: **PER (ressarcimento), nunca DCOMP** — o escopo não pode prever compensação por DCOMP nessa tese | riscos-chave.md |
| Responsabilidade por glosa/indeferimento e multa | Limite, contrapartida do cliente (documentos corretos), não promessa de resultado | riscos-chave.md |
| Rescisão/distrato e créditos já pedidos | Honorário sobre PER transmitido antes do distrato | art. 472 e 473 do Código Civil |
| Procuração e-CAC e acesso a dados fiscais | Poderes, prazo, revogação | — |
| LGPD | Dados fiscais do cliente; parceiro como operador/controlador | Lei 13.709/2018 |
| Assinatura eletrônica | Tipo de assinatura aceito e validade | MP 2.200-2/2001, art. 10, § 2º · Lei 14.063/2020 [VALIDAR aplicabilidade a contratos privados] |
| Foro e lei aplicável | — | modelo |

> Referências legais acima foram listadas pelo departamento virtual em 29/09/2026 para orientar a validação; não são parecer. Confirmar texto vigente no Planalto (https://www.planalto.gov.br).

## Formato da entrega
```
PRÉ-MINUTA — rascunho do Depto Contratos virtual. Não enviar. Validação: Jurídico [nome] · Área de Contratos [nome]
Modelo usado: <arquivo> (aprovado por <nome> em <data>)
Ficha de dados: … (fonte e data de cada item)
Campos em aberto: [PREENCHER …]
Pontos para o Jurídico: 1. … 2. …
Checklist: Parte A ✅ · B ⚠️ (signatário a confirmar no QSA) · C ✅ · D ✅
```
