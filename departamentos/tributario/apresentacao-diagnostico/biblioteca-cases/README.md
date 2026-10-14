# Biblioteca de cases por segmento

O diagnóstico que fica pronto busca aqui o case do **segmento** da empresa (pelo CNAE principal) e o coloca no slide "Quem já fez" da apresentação. Sem case aprovado para o segmento, o slide não entra e o gerador avisa.

## Como o Luis sobe os cases
Mande os cases (planilha, PDF ou texto) numa conversa e peça "cadastrar cases na biblioteca". Cada case vira um item de `cases.json`. Não grave arquivos soltos: logo em `logos/<case_id>.png`, só se houver autorização.

## Campos de cada case
| Campo | Regra |
|---|---|
| `id` | slug único, ex. `alimenticio-001` |
| `segmento` | chave de `segmentos` (alimenticio, agro, industria, saude, transporte, folha_alta) |
| `cnae_principal` | 7 dígitos, para casar o mais parecido dentro do segmento |
| `regime` | Lucro Real, Presumido etc. |
| `uf` | opcional |
| `teses` | lista de códigos de tese (ver `teses.json` do revisor-diagnostico): AQ_SAVE, EX_ICMS, EX_ST, PREV… O gerador prefere o case que tem as mesmas teses do diagnóstico |
| `valor` | número em R$ efetivamente recuperado (ressarcido, restituído ou compensado), nunca estimado |
| `valor_tipo` | `recuperado` ou `reconectado` (se "reconectado", a definição vai em `definicao_valor`) |
| `periodo` | período recuperado, ex. "01/2019 a 12/2023" |
| `data_base` | data do número, ex. "30/09/2026" |
| `fonte` | de onde vem (HubSpot, contrato, extrato, termo do cliente) |
| `identificacao` | **`anonimo`** (padrão e regra). Nome ou logo de cliente não entram no diagnóstico: parecer do Jurídico de 14/10/2026 (`departamentos/juridico/entregas/2026-10-14-padrao-apresentacao-diagnostico-compliance.md`) aponta que a vedação ética da OAB permanece mesmo com autorização do cliente. Exceção só com parecer do Jurídico humano |
| `autorizacao_uso` | referência do termo escrito do cliente (arquivo, data). Vazio = só anônimo |
| `resumo_cliente` | 2 a 3 frases em linguagem de dono de empresa, sem promessa |
| `aprovado` | true só depois do checklist abaixo |
| `aprovado_por`, `aprovado_em` | quem e quando |

## Checklist de aprovação (Jurídico e Tributário)
1. O valor é de dinheiro que o cliente de fato recebeu ou compensou, com data-base e fonte?
2. Case anonimizado e agregado (ex.: "Atacadista de alimentos, Lucro Real, Centro-Oeste"), valor arredondado, sem nome, logo, número de processo ou dado que identifique. Termo de autorização do cliente guardado de qualquer forma (LGPD e contrato).
3. Sem promessa de resultado e sem comparação que induza o novo cliente a esperar valor parecido; a frase "resultados passados não garantem resultado futuro" fica no rodapé.
4. Tese descrita bate com a base legal vigente (o Tributário confere).
5. Nenhum dado pessoal, número de processo ou dado que identifique o cliente quando for anônimo.
