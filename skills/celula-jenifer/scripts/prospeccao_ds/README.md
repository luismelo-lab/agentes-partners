# Prospecção de novos clientes para um Master (piloto: D&S, 20 e 21/10/2026)

Os dados ficam fora do repositório, em `~/agentes-partners/departamentos/intel-comercial/prospeccao-ds/` (variável `PROSPECCAO_DS`). Para outro Master, aponte `PROSPECCAO_DS` para uma pasta nova e `PLANILHA_MASTER` para a planilha de clientes dele.

| Passo | Comando | O que faz |
|---|---|---|
| 1 | `python3 base.py` | Lê a planilha de clientes do Master e cruza com a Receita local e com o HubSpot (todos os funis). Monta o universo de prospects: ativos, matriz, fora do Simples e do MEI, nos segmentos e nas regiões imediatas (IBGE) dos ganhos. Tira toda raiz de CNPJ do Master e do HubSpot. |
| 2 | `SO_LUCRO_REAL=0 python3 modelo.py && cp $PROSPECCAO_DS/modelo.pkl $PROSPECCAO_DS/modelo-completo.pkl` | Gera o universo completo, para o passo 3 |
| 3 | `UFS=MG python3 regime.py` | Consulta o regime no Minha Receita, só de prospects, em ordem de prioridade, com cache em `dados-publicos/receita/regime-cache.json`. Se houver falhas (tempo esgotado), rode de novo: só consulta o que falta |
| 4 | `python3 contatos.py` | Grava em `dados-publicos/receita/prospects-contatos.json` (permissão 600, fora do repositório e do OneDrive) os sócios do QSA (nome, qualificação, entrada; sem CPF) e os telefones e o e-mail da empresa. Uso aprovado pelo Luis em 20/10/2026 |
| 5 | `python3 modelo.py` | Filtra o Lucro Real e tira recuperação judicial e falência. Calcula a similaridade com cada ganho, a empresa exemplo, o cliente mais próximo (bairro, região da cidade, cidade, cidades vizinhas) e o potencial |
| 6 | `python3 previa.py` | Gera a prévia em PNG para a Jenifer conferir antes do Excel (lista interna; alçada de 23/10/2026) |
| 7 | `LOTE="Lote 1" UFS=MG python3 planilha_bdr.py "<destino>.xlsx"` | Gera a planilha de ligações da BDR |

## Lotes (não perder as anotações da BDR)
- Cada lote é um arquivo novo. Nunca regrave um lote em que a BDR já anotou.
- Depois de gerar o lote N, salve os CNPJs dele em `loteN-cnpjs.txt`. O lote seguinte usa `SO_CNPJS=<arquivo com os CNPJs novos>`. Exemplo do Lote 2: as empresas de MG no Lucro Real que não estão em `lote1-cnpjs.txt`.
- Entregues para a D&S: Lote 1, com 755 empresas (20/10, refeito só com MG em 21/10), e Lote 2, com 1.688 (21/10). Os dois estão em `Área Partners · Agentes/Central BDR · Jenifer/Listas`.

## Regras
- Só Minas Gerais (`UFS=MG`), por decisão do Luis de 21/10/2026.
- Fora da lista: clientes do Master (qualquer fase), toda raiz com negócio no HubSpot (qualquer parceiro), Simples, MEI, recuperação judicial ou falência.
- Empresa que já estava em lista anterior da BDR (`Listas/Lista-*.xlsx` ou `Controle-Followup-Jenifer.xlsx`) vem marcada em Anotações.
- Não cite clientes ao prospect. Potencial e crédito de referência são internos. Nunca prometa valor, prazo ou êxito.
- Celular pessoal de sócio não é buscado em outras fontes. O contato vem só do cadastro público da empresa (CNPJ).
