# Prospecção de novos clientes para um Master (piloto: D&S, 20/10/2026)

Os dados ficam em `~/agentes-partners/departamentos/intel-comercial/prospeccao-ds/`, fora do repositório (variável `PROSPECCAO_DS`).

| Passo | Script | O que faz |
|---|---|---|
| 1 | `base.py` | Lê a planilha de clientes do Master e cruza com a Receita local e com o HubSpot (todos os funis). Monta o universo de prospects: ativos, matriz, fora do Simples e do MEI, nos segmentos e nas regiões imediatas (IBGE) dos ganhos. Tira toda raiz de CNPJ do Master e do HubSpot. |
| 2 | `regime.py` | Consulta o regime tributário no Minha Receita, só de prospects, com cache. Lê `modelo-completo.pkl`, que é o universo inteiro gerado por `SO_LUCRO_REAL=0 python3 modelo.py`. |
| 3 | `modelo.py` | Aplica o filtro de Lucro Real (padrão) e tira empresas em recuperação judicial ou falência. Calcula a similaridade com cada ganho, a empresa exemplo, o cliente mais próximo (bairro, região da cidade, cidade ou cidades vizinhas) e o potencial. |
| 4 | `previa.py` | Gera a prévia em PNG para aprovação. |
| 5 | `planilha_bdr.py <pasta> --lote N` | Gera a planilha de ligações da BDR. `lotes-ds.json` guarda o que já foi entregue: o lote N traz só empresas novas, para não perder as anotações da BDR. |

O bairro vem de `receita_cnpj.py --bairros`. Telefone e e-mail não entram até a validação de LGPD pelo Jurídico (`incluir_contatos`).
