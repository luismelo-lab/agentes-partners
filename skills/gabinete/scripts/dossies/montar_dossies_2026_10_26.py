#!/usr/bin/env python3
"""Monta os dossiês das decisões pendentes do Luis de 26/10/2026 (pedido do Luis de 26/10).

Conteúdo do Gabinete (o que decidir, contexto, opções, recomendação, execução) + pareceres das áreas
em registro/gestao/dossies/pareceres/2026-10-26/*.json (um arquivo por área; cada item: id, area,
especialista, parecer, motivo, base, condicao, ressalva, fatos).

Uso: python3 skills/gabinete/scripts/dossies/montar_dossies_2026_10_26.py
Saída: registro/gestao/dossies/<id>.json e indice.json (via dossies_decisao.py --indice).
"""
import glob, json, os, sys

AP = os.environ.get("PARTNERS_AP") or os.path.expanduser("~/agentes-partners")
PASTA = os.path.join(AP, "registro", "gestao", "dossies")
PARECERES = os.path.join(PASTA, "pareceres", "2026-10-26")
HOJE = "2026-10-26"

PAC = "registro/gestao/pacote-2026-10-26.json (HubSpot 26/10 06:53)"
PREV = "registro/gestao/previsao-2026-10-26.json"
CTRL = "registro/gestao/controle-2026-10-26.json"
ATA_S = "conselho/atas/2026-10-26-reuniao-semanal.md"
ATA_X = "conselho/atas/2026-10-26-extraordinaria-gestao.md"
ATA_CI = "conselho/atas/2026-10-02-credito-internacional.md"
ATA_MQ = "conselho/atas/2026-10-05-save-maquila.md"
DEC = "conselho/decisoes.md"

F, E, O = "fato", "estimativa", "opiniao"

# Contexto comum aos produtos em validação
CTX_PV = [
    ("D108 (ata extraordinária de 26/10) propõe 0 h do time em Crédito Internacional (CI) e Maquila (MQ) até o G2 de 15/12, com o Luis até 4 h/semana; 5 de 6 conselheiros a favor.", ATA_X + " §4 e §6", F),
    ("O núcleo caiu: outubro (01–26) fechou R$ 16,42 mi de crédito ganho, −61% sobre o mesmo período de setembro; criados −75%.", PAC, F),
    ("Produto em validação é alçada do Luis com o dono do produto (João Mattos), pela D98 de 23/10.", "infra/alcadas.md; " + DEC + " (D98)", F),
]

D = {}

def dz(id, **k):
    k["id"] = id
    D[id] = k

# ---------------- Gestão, meta e lançamento ----------------
dz("D105", titulo="Lote 1 do Recuperador decidido em 48 h e lotes de 5 depois",
   folha="", prazo="2026-10-30", padrao="vale por padrão em 29/10 se não houver resposta",
   o_que_decidir="Se a Geovana decide sozinha o lote 1 do Recuperador (20 casos) e passa a trabalhar em lotes de 5, sem reenvio da mesma folha.",
   por_que_agora="O lote 1 está no 3º envio sem decisão há 27 dias; a EFD de 2021 só pode ser retificada até 31/12/2026 e parte dos créditos sai do prazo de 5 anos a cada mês.",
   custo_nao_decidir="Estimativa: cerca de R$ 0,4 mi de crédito por semana sai do prazo de 5 anos na fila; em novembro saem R$ 1,78 mi da fila do Recuperador (previsão de 26/10). Confiança baixa.",
   contexto=[("Lote 1: 20 casos, R$ 2,08 mi esperados, 0 decisões, 3º envio; fila de 318 casos, R$ 5,6 mi esperados.", ATA_S + " (números da semana)", F),
             ("8 dos 20 casos do lote 1 não têm parecer porque dependem do escopo `files` do HubSpot (TI).", ATA_X + " pergunta 9", F),
             ("03/11 é terça (02/11 é Finados): as 48 h contadas de 26/10 caem antes das 1:1 e do D0.", "Lei 10.607/2002; parecer do Recuperador de 26/10", F)],
   opcoes=[{"nome": "A · 48 h para os 20 casos (texto original)", "pros": "Destrava o lote já.", "contras": "Cai antes da 1:1 e do D0; risco de decidir sem dado.", "risco": "Decisão apressada nos 8 casos sem parecer.", "efeito": "Lote 1 decidido até 28/10."},
           {"nome": "B · 5 casos em 48 h depois da 1:1 (até 30/10), por vencimento, e os 15 restantes em lotes de 5 até 13/11", "pros": "Ordem por decadência; respeita a 1:1; sem reenvio.", "contras": "Lote completo só em 13/11.", "risco": "Baixo; o padrão sem resposta é 'precisa de dado', nunca aprovar ou vetar sozinho.", "efeito": "Os créditos com prazo mais curto são decididos primeiro (corte de 30/11)."},
           {"nome": "C · Manter com o Luis", "pros": "Nenhum.", "contras": "Repete os 27 dias parados.", "risco": "Perda de prazo.", "efeito": "Nenhum."}],
   recomendacao="Aprovar com o ajuste B: Geovana decide 5 casos até 30/10, por competência mais antiga (não por honorário), e os 15 restantes em lotes de 5 até 13/11; os 8 casos sem parecer voltam sem travar os outros 12; sem resposta, o padrão do caso técnico é 'precisa de dado'.",
   se_reprovada="O lote segue com o Luis; o Gabinete leva à pauta de 03/11 a lista dos créditos com decadência até 31/12 e o valor que sai do prazo por semana.",
   divergencias="Sem divergência de mérito. Recuperador pede 5 casos até 30/10 (depois da 1:1) e Tributário pede ordem por vencimento: o Gabinete junta as duas na opção B.",
   execucao={"dono": "Geovana (Recuperador), com o time técnico tributário", "prazo": "30/10 (5 casos); 13/11 (20 casos)", "indicador": "casos decididos com competência mais antiga, tese e registro do SPED ÷ 20; minutos por caso"})

dz("D104", titulo="Coluna conservadora de tese desfavorável e ganho só com tese, variante e %",
   folha="", prazo="2026-10-29", padrao="vale por padrão em 29/10",
   o_que_decidir="Se o relatório e o forecast passam a ter uma coluna conservadora com a tese PIS/COFINS nas aquisições desfavorável, e se ganho sem tese, variante e % deixa de entrar no forecast.",
   por_que_agora="O forecast lê volume como se toda tese fosse ganhar; 99% do valor ganho com tese é PIS/COFINS nas aquisições e o EREsp 2.215.482 não foi julgado.",
   custo_nao_decidir="Estimativa de Resultados: R$ 172,8 mi de líquido potencial expostos ao julgamento sem leitura conservadora; diretoria lê um número sem a hipótese de perda.",
   contexto=[("53,4% dos ganhos estão sem tese e 57,3% sem % de honorário.", PAC + " (confiabilidade)", F),
             ("Aplicada ao realizado, a regra tiraria 34 dos 35 ganhos de outubro (R$ 16,3 mi de R$ 16,4 mi).", "parecer Dados & BI de 26/10 sobre HubSpot 26/10", F),
             ("A coluna 'tese desfavorável' fica em torno de R$ 1 mi de líquido no Q4.", "parecer Resultados de 26/10", E)],
   opcoes=[{"nome": "A · Regra em tudo (forecast, relatório e realizado da meta)", "pros": "Máximo rigor.", "contras": "Zera o realizado de outubro contra a meta da D111.", "risco": "Meta ilegível.", "efeito": "Realizado cai a ≈ R$ 0,2 mi."},
           {"nome": "B · Regra no forecast, no líquido e na margem; o realizado da meta (D111) segue em crédito ganho", "pros": "Previsão honesta sem distorcer a meta.", "contras": "Duas leituras no relatório.", "risco": "Baixo, com rótulo.", "efeito": "Coluna conservadora com número; meta legível."},
           {"nome": "C · Não adotar", "pros": "Nenhum trabalho.", "contras": "Forecast sem hipótese de perda.", "risco": "Glosa em 2028 sem aviso.", "efeito": "Nenhum."}],
   recomendacao="Aprovar a opção B, com o corte por variante e período proposto pelo Tributário (variante B integral; variante A zero no conservador; revenda, monofásico e variante A após 01/04/2026 zero em qualquer coluna; glosa do ICMS na base do crédito desde 05/2023).",
   se_reprovada="Previsão segue só com cenários de volume; o Controller marca no pacote que a coluna conservadora não existe.",
   divergencias="Dados e Resultados pedem que a regra não alcance o realizado da meta; Tributário pede corte por variante e período em vez de linear. Sem conflito: o Gabinete junta as duas na opção B.",
   execucao={"dono": "Controller (depto-resultados), com Tributário e Dados", "prazo": "30/10 (previsão) e relatório de 02/11", "indicador": "coluna conservadora com número no previsao.json; % dos ganhos novos com tese, variante e %"})

dz("D107", titulo="D0 do lançamento ao time e regra de 3 dias úteis",
   folha="22", prazo="2026-10-30", padrao="",
   o_que_decidir="Se o time é lançado nos agentes em 03/11 (terça) e se decisão reversível sem resposta em 3 dias úteis aplica o padrão sozinha (irreversível vai à ata).",
   por_que_agora="O time nunca foi lançado (D0 nulo) e o atravessamento é de ≈ 80 dias contra ciclo de 22–49 dias; o plano de 2 semanas da ata extraordinária depende disso.",
   custo_nao_decidir="Uma das ~9 semanas úteis do Q4 por semana de atraso. Valor ligado: até R$ 5,6 mi de honorário líquido esperado na fila do Recuperador, R$ 2,08 mi no lote 1 (a ata dizia R$ 7,7 mi de crédito: soma em dobro, corrigida por Resultados). Efeito na meta do Q4: 1% a 2% (estimativa).",
   contexto=[("0 decisões no Recuperador e no Revisor (203 revisões) e 0 pedidos do time à Central.", ATA_X + " §1 item 8", F),
             ("02/11 é feriado (Finados); o D0 em 03/11 cai numa terça; 20/11 também é feriado nacional.", "Lei 10.607/2002; Lei 14.759/2023", F),
             ("O identificador 'C13' da ata colide com a regra C13 de duplicados do controle.json; hoje só a consolidação de sexta aplica padrões (atraso real de até 8 dias úteis).", "parecer TI de 26/10; infra/controle.json", F)],
   opcoes=[{"nome": "A · D0 em 03/11 e regra de 3 dias úteis com aplicação diária", "pros": "Destrava o ciclo de decisão já.", "contras": "Exige 1:1 até 30/10.", "risco": "Padrão aplicado sem contexto; mitigado pelas exceções abaixo.", "efeito": "Placar em 09/11."},
           {"nome": "B · D0 em 10/11", "pros": "Mais tempo para preparar.", "contras": "Perde uma semana do Q4.", "risco": "Uso zero se cristaliza.", "efeito": "Placar em 16/11."},
           {"nome": "C · D0 depois do G2 (15/12)", "pros": "Nenhum relevante.", "contras": "Q4 inteiro sem o time nos agentes.", "risco": "Alto.", "efeito": "Nenhum no Q4."}],
   recomendacao="Aprovar a opção A com quatro ajustes das áreas: (1) roteiro D0–D5 a partir de terça, retro em 06/11 e placar em 09/11; (2) a regra ganha outro número (C22) e roda na rotina diária; (3) o padrão nunca vale para decisão sobre pessoa (nota, meta, feedback, remuneração), conflito de canal, parado acima de R$ 1 mi, nem envia nada ao Master; (4) para caso técnico o padrão é 'precisa de dado' e para parado é 'aguardar com data', nunca 'perder' por silêncio.",
   se_reprovada="As regras de controle viram só alerta; o plano de 2 semanas é refeito pelo Gabinete com nova data de D0.",
   divergencias="Nenhuma de mérito (6 pareceres: 1 concorda, 5 com ressalva). As ressalvas se somam.",
   execucao={"dono": "Gabinete (regra) e Luis com Daniela, Jenifer e Geovana (D0); TI na automação", "prazo": "1:1 até 30/10; D0 03/11; regra diária até 05/11", "indicador": "3 pedidos e 3 decisões no D0; itens com o Luis > 3 dias úteis = 0; adoção na semana 2 (≥ 3 pedidos por pessoa)"})

dz("D101", titulo="Meta do Q4 à diretoria: meta oficial com três cenários",
   folha="", prazo="2026-10-30", padrao="",
   o_que_decidir="Como a meta do Q4 vai à diretoria: a D111 já fixou R$ 250 mi em crédito ganho (out 75, nov 100, dez 75); falta decidir se vai com os três cenários da previsão como leitura de probabilidade.",
   por_que_agora="Outubro fecha em 4 dias úteis com R$ 16,42 mi contra R$ 75 mi; a diretoria vai ler a distância de qualquer forma.",
   custo_nao_decidir="Sem leitura de probabilidade, a pressão vai para volume com margem ≈ 10% (setembro) e o semáforo fica vermelho até dezembro.",
   contexto=[("Faltam R$ 233,6 mi em 45 dias úteis: ritmo necessário R$ 5,19 mi por dia útil contra R$ 0,97 mi atual (5,4 vezes).", "parecer Resultados de 26/10 sobre " + PAC, F),
             ("Previsão do Q4: conservador R$ 29,7 mi, base R$ 46,8 mi, esforço R$ 65,9 mi; probabilidade de bater a meta 0% em 20.000 simulações.", PREV, E),
             ("O Conselho estimou R$ 46–50 / 70 / 105 mi com outras premissas (pipeline × win rate).", ATA_X + " §2.1", E),
             ("Melhor mês do ano: agosto, R$ 59,8 mi.", ATA_S, F)],
   opcoes=[{"nome": "A · Só a meta oficial (R$ 250 mi)", "pros": "Mensagem simples.", "contras": "Sem leitura de risco.", "risco": "Reputação na revisão de dezembro.", "efeito": "Nenhum no plano."},
           {"nome": "B · Meta oficial + três cenários com faixa e a distância explícita", "pros": "Diretoria lê probabilidade e alavancas; meta não muda.", "contras": "Expõe a distância.", "risco": "Baixo.", "efeito": "Revisão mensal 03/11 e 01/12 contra 75/100/75."},
           {"nome": "C · Renegociar a meta", "pros": "Meta alcançável.", "contras": "Contradiz a D111 de hoje.", "risco": "Leitura de recuo.", "efeito": "Nova meta."}],
   recomendacao="Aprovar a opção B: a meta é a da D111 e não se troca; o deck leva um só número por cenário (a soma mensal, dizendo qual), a distância em R$ e em ritmo, e as alavancas com dono. Antes do envio, regerar o previsao-2026-10-26.md (ainda cita R$ 200 mi) e o Luis dizer se o que outubro não fechar acumula em novembro (recomendação de Resultados: não acumula; o total do Q4 é a leitura).",
   se_reprovada="Vai só a meta; o Controller mantém os cenários no painel do Luis, sem envio.",
   divergencias="Só Resultados opinou (tema único da área). Divergência de número entre a previsão (base R$ 46,8 mi) e o Conselho (R$ 70 mi): o deck usa a previsão e cita a premissa do Conselho.",
   execucao={"dono": "Luis (envio) e Controller (deck)", "prazo": "30/10", "indicador": "realizado do mês ÷ meta mensal da D111; cenário em que o mês caiu"})

dz("D102", titulo="Repasse: liberar o conferido e não pagar atípico sem contrato",
   folha="", prazo="2026-10-30", padrao="",
   o_que_decidir="Se o repasse já conferido (R$ 69,2 mi) é liberado para pagamento e se atípico (honorário > 50%, café a 70%, % do parceiro > 100%) só é pago com contrato conferido.",
   por_que_agora="1.047 de 1.696 ganhos estão com repasse bloqueado; repasse retido é o risco ao canal mais citado pelo Conselho e pago sem contrato é difícil de reaver.",
   custo_nao_decidir="Confiança dos 9 Masters por semana; risco de mora; R$ 49,7 mi seguem retidos como passivo potencial.",
   contexto=[("Repasse conferido OK R$ 69,2 mi de R$ 118,9 mi calculáveis; R$ 49,7 mi retidos, dos quais ≈ R$ 43,7 mi em 'Revisar'.", ATA_S + "; parecer Operações de Canal de 26/10", F),
             ("O campo de recebimento está vazio em 0 de 1.696 ganhos preenchidos: 'liberar' só pode ser à medida que o honorário for recebido.", "parecer Operações de Canal de 26/10", F),
             ("Pagar indevido é de difícil restituição (CC arts. 876–877); reter o devido pode ser justa causa se o vínculo for lido como representação (Lei 4.886/1965, arts. 32 §1º e 36 'd').", "parecer Jurídico de 26/10 (pré-análise)", O)],
   opcoes=[{"nome": "A · Liberar o conferido à medida do recebimento e reter só o excedente atípico, com aviso escrito", "pros": "Protege canal e lastro.", "contras": "Exige checklist por lote.", "risco": "Baixo.", "efeito": "432 ganhos OK marcados até 07/11."},
           {"nome": "B · Reter tudo até conferir tudo", "pros": "Máximo lastro.", "contras": "Mora e canal.", "risco": "Rescisão por justa causa.", "efeito": "Repasse parado."},
           {"nome": "C · Pagar tudo, inclusive atípico", "pros": "Canal satisfeito.", "contras": "Sem lastro.", "risco": "Irreversível.", "efeito": "Perda potencial."}],
   recomendacao="Aprovar a opção A: liberar o conferido para pagamento à medida do recebimento, com checklist de elegibilidade; pagar a parte incontroversa e reter só o excedente atípico; cada atípico ganha ficha de conferência (confere, erro de campo ou exceção a aprovar) até 05/12; aprovar junto a frase ao Master 'em conferência contratual', sem valor nem prazo. Conferir os grupos duplicados antes de liberar.",
   se_reprovada="Repasse segue bloqueado; Daniela responde aos Masters sem data, e o risco de canal sobe na pauta de 03/11.",
   divergencias="Operações de Canal aponta conflito: a regra C14 da ata extraordinária bloquearia repasse de ganho sem tese ou %, contra as D45, D62, D71 e D73 (não reter repasse). O Gabinete resolve pela regra vigente: C14 bloqueia só forecast e relatório.",
   execucao={"dono": "Operações de Canal e Financeiro; Contratos nas fichas; Daniela no retorno ao Master", "prazo": "07/11 (liberação); 05/12 (143 fichas)", "indicador": "ganhos bloqueados (1.047 → ≤ 840 em 2 semanas); atípico pago sem ficha = 0"})

dz("D109", titulo="% de honorário preenchido pelo contrato, sem aprovação caso a caso",
   folha="24", prazo="2026-11-06", padrao="vale por padrão (folha 24)",
   o_que_decidir="Se Financeiro e Contratos preenchem o % de honorário dos ganhos sem o campo a partir do contrato assinado, sem passar pelo Luis caso a caso; atípico sobe pela D65/D102.",
   por_que_agora="966 ganhos sem % travam repasse e margem; a margem calculável cobre só 35% do valor ganho.",
   custo_nao_decidir="Margem segue amostra (43% dos ganhos); confiança do canal cai a cada semana; risco não quantificável sem o caixa.",
   contexto=[("Os 200 maiores sem % somam R$ 2,47 bi (≈ 87% do crédito sem honorário); 199 vêm da migração e 24 estão em grupo de duplicidade.", "parecer Dados & BI e Operações de Canal de 26/10 (Conferencia-Repasses-2026-10-26.xlsx)", F),
             ("116 dos 200 maiores são café (R$ 1,03 bi); café a 70% é atípico e sobe ao Luis de qualquer jeito.", "parecer Resultados de 26/10", F),
             ("Ritmo viável: ≈ 34 contratos por semana se o documento estiver na Clicksign; 78 dos 200 são de 2023–2024.", "parecer Contratos de 26/10", E)],
   opcoes=[{"nome": "A · 200 maiores em 6 semanas (texto original)", "pros": "Maior volume de crédito.", "contras": "Muito café, que sobe de qualquer jeito.", "risco": "Esforço em casos que não liberam margem.", "efeito": "Margem calculável ≈ 69% do valor."},
           {"nome": "B · Em ondas: 1ª os 32 de outubro e os 58 dos últimos 12 meses, depois os não-café dos 200 maiores; café direto como atípico", "pros": "Margem recente primeiro; menos atrito.", "contras": "Menos crédito coberto na 1ª onda.", "risco": "Baixo.", "efeito": "Margem de outubro calculável em 2 semanas."},
           {"nome": "C · Aprovação do Luis por caso", "pros": "Controle.", "contras": "Gargalo de 966 itens.", "risco": "Nada anda.", "efeito": "Nenhum."}],
   recomendacao="Aprovar a regra (preencher pelo contrato assinado e aditivos, com registro de quem preencheu e quando) na ordem da opção B, com saneamento dos duplicados antes; sem contrato localizado o caso fica 'sem lastro' e fora do repasse; contrato com % por componente, aditivo ou honorário > 50% não se preenche e sobe como atípico. Meta: 100 até 16/11 e 200 até 07/12; abaixo de 25 contratos na 1ª semana, o prazo passa a 8 semanas.",
   se_reprovada="O % segue vazio; o Gabinete leva ao Luis a lista dos 90 ganhos recentes para aprovação em bloco.",
   divergencias="Ordem do trabalho: Operações de Canal e Contratos propõem os 200 maiores em ondas; Resultados propõe começar pelos recentes e não-café. Resolvido pelo Gabinete (opção B), sem mudar a regra.",
   execucao={"dono": "Contratos (localiza e lê) e Financeiro (preenche e confere); Dados saneia duplicados", "prazo": "16/11 (100) e 07/12 (200)", "indicador": "ganhos sem % (57,3% → ≤ 46%); margem calculável em 9 de 9 Masters"})

dz("D65", titulo="Registro único de exceções de honorário",
   folha="20", prazo="2026-11-06", padrao="",
   o_que_decidir="Se toda exceção de honorário (ex.: café a 70%) passa a constar num registro único, aprovada pelo Luis e validada pelo Jurídico; a conferência dos atípicos contra o contrato fica com Financeiro e Contratos.",
   por_que_agora="143 atípicos e 61 honorários acima de 50% inflam a margem da carteira e travam o repasse; a D102 e a D109 dependem deste registro.",
   custo_nao_decidir="Atípicos sem regra continuam fora do repasse ou pagos sem lastro; margem da carteira (17,35%) segue viesada.",
   contexto=[("143 atípicos; 61 com honorário > 50% (R$ 56,3 mi de líquido); 9 com % do parceiro > 100%.", ATA_S + " (qualidade)", F),
             ("60 dos 61 honorários acima de 50% parecem inversão 70/30 ou erro de escala, não exceção.", "parecer Operações de Canal de 26/10", E),
             ("O validador humano do Jurídico (D94, até 07/11) ainda não tem nome; não se confirmou que os 9 Masters têm termo escrito.", "pareceres Jurídico e Contratos de 26/10", F)],
   opcoes=[{"nome": "A · Registro com três tipos: exceção aprovada (Luis), erro de campo (corrige pelo contrato) e sem lastro (retido)", "pros": "Só a exceção real consome a alçada do Luis.", "contras": "Exige ficha por caso.", "risco": "Baixo.", "efeito": "Registro completo até 07/12."},
           {"nome": "B · Todo atípico ao Luis", "pros": "Controle total.", "contras": "143 itens ao Luis.", "risco": "Gargalo.", "efeito": "Lento."},
           {"nome": "C · Sem registro", "pros": "Nenhum.", "contras": "Sem lastro.", "risco": "Alto.", "efeito": "Nenhum."}],
   recomendacao="Aprovar a opção A. A exceção aprovada vira anexo de remuneração assinado, sem retroagir; enquanto não houver validador humano, a exceção fica registrada e não é paga, e o resto do repasse segue. Contratos faz o inventário dos 9 termos de Master em 2 semanas.",
   se_reprovada="Atípicos ficam retidos sem rito; o Gabinete reapresenta com a lista dos 143.",
   divergencias="Nenhuma de mérito; as três áreas pedem a separação em tipos e o validador humano.",
   execucao={"dono": "Operações de Canal (registro), Contratos (fichas e termos), Jurídico (validação)", "prazo": "09/11 (inventário dos termos); 07/12 (registro completo)", "indicador": "% de exceções vigentes no registro com lastro; atípico pago fora do registro = 0"})

dz("D110", titulo="Custo/hora provisório e pedido de caixa ao Financeiro",
   folha="25", prazo="2026-11-07", padrao="vale por padrão (folha 25)",
   o_que_decidir="Se a área adota R$ 141/h como custo/hora provisório (rótulo 'parcial') para ROI de agentes e pede ao Financeiro o recebido por negócio de set/out, o aging e os impostos até 07/11.",
   por_que_agora="Sem o custo da área e sem o recebido, nenhum ROI é auditável e o caixa de 13 semanas fica cinza.",
   custo_nao_decidir="Caixa de 13 semanas vai de R$ 19,3 mi a R$ 94,1 mi sem o recebido (faixa inútil para decisão); ROI de 67,8x segue calculado só com o custo da área.",
   contexto=[("R$ 90,4 mil por mês × 3 = R$ 271,2 mil por trimestre ÷ 1.920 h = R$ 141/h; custo só da área Partners.", "parecer Resultados de 26/10; " + ATA_X + " D110", F),
             ("O campo de valor recebido está vazio nos 1.696 ganhos.", "parecer Resultados de 26/10 sobre HubSpot 26/10", F),
             ("Com encargos e rateios, o custo/hora pode chegar perto do dobro (≈ R$ 282/h).", ATA_X + " pergunta 5", E)],
   opcoes=[{"nome": "A · Aprovar o provisório com rótulo 'parcial' e pedir o dado", "pros": "ROI auditável já.", "contras": "Número parcial.", "risco": "Baixo com rótulo.", "efeito": "Caixa sai do cinza em novembro."},
           {"nome": "B · Esperar o Financeiro", "pros": "Número completo.", "contras": "Sem prazo.", "risco": "Cinza até 2027.", "efeito": "Nenhum."},
           {"nome": "C · Custo completo primeiro", "pros": "Rigor.", "contras": "Depende de outras áreas.", "risco": "Atraso.", "efeito": "Nenhum no Q4."}],
   recomendacao="Aprovar a opção A, com os ROIs mostrados também a R$ 282/h (sensibilidade) e o pedido ao Financeiro ampliado para impostos e custo das áreas de apoio.",
   se_reprovada="ROI de agentes sai sem a referência de custo por hora, marcado 'não auditável'.",
   divergencias="Só Resultados opinou (tema da área).",
   execucao={"dono": "Controller; Luis faz o pedido ao Financeiro", "prazo": "07/11", "indicador": "caixa_13_semanas sem cinza; ROI com custo/hora rotulado"})

dz("F26", titulo="Tolerâncias do semáforo de gestão",
   folha="26", prazo="2026-11-03", padrao="vale por padrão (folha 26)",
   o_que_decidir="Se as tolerâncias propostas do semáforo (verde, amarelo, vermelho por métrica, infra/controle.md §1) viram oficiais na revisão mensal de 03/11.",
   por_que_agora="Sem tolerância aprovada a métrica fica 'proposta' e os gatilhos de controle avisam sem força.",
   custo_nao_decidir="Painel com cores provisórias; com a meta da D111, o semáforo ficaria vermelho até dezembro e a regra C02 dispararia toda semana.",
   contexto=[("Há duas tabelas diferentes: índice de qualidade 85/70 no controle.md e 90/75 no pacote; duplicados 20/100 × 0/20.", "parecer Dados & BI e Resultados de 26/10", F),
             ("O controle.md ainda cita a meta de R$ 200 mi.", "infra/controle.md (26/10)", F),
             ("Número de grupos duplicados diverge entre Dados (349) e Operações de Canal (81).", PAC + "; " + ATA_S, F)],
   opcoes=[{"nome": "A · Aprovar como estão", "pros": "Rápido.", "contras": "Duas réguas e meta antiga.", "risco": "Mesma métrica com duas cores.", "efeito": "Confusão."},
           {"nome": "B · Unificar no controle.json, reescrever as linhas de meta para a D111 e adotar régua contra cenários (verde ≥ base, amarelo ≥ conservador)", "pros": "Uma régua só; semáforo útil.", "contras": "Uma semana de trabalho.", "risco": "Baixo.", "efeito": "Aprovação em 03/11 já unificada."}],
   recomendacao="Aprovar a opção B em 03/11; Dados e Operações de Canal fecham um número único de duplicados antes.",
   se_reprovada="Tolerâncias seguem 'propostas'; o Gabinete reapresenta na revisão de dezembro.",
   divergencias="Nenhuma de mérito; as duas áreas pedem unificação antes de aprovar.",
   execucao={"dono": "Gabinete com Dados e Controller", "prazo": "03/11", "indicador": "uma tabela de tolerâncias; métricas com status divergente = 0"})

dz("D103", titulo="Funrural: conciliar D81 e D86",
   folha="", prazo="2026-11-07", padrao="",
   o_que_decidir="Como fica o Funrural no catálogo: a D81 (manter só como tese) foi reprovada e a D86 (produto 'Revisão do Funrural anterior a 2018' em Gestão de Passivo) foi aprovada; falta escrever a conciliação.",
   por_que_agora="Catálogo e material estão com duas regras; o Funrural vai a mercado antes de CI e Maquila.",
   custo_nao_decidir="Material contraditório ao parceiro e risco de promessa de restituição prescrita.",
   contexto=[("D81 reprovada e D86 aprovada em 22/10 ('a conciliar').", DEC + " (D81, D86)", F),
             ("Quem pagou até 2017 e nunca discutiu está fora do prazo de 5 anos para restituir (CTN art. 168, I).", "pareceres Jurídico e Tributário de 26/10 (pré-análise)", O),
             ("Acórdão e modulação da ADI 4.395 seguem em aberto; o catálogo cita o Tema 1.079 no lugar da ADI.", "parecer Tributário de 26/10; docs/teses/funrural-adi-4395-estrategia.md", F)],
   opcoes=[{"nome": "A · Produto em Gestão de Passivo; T19 só como remissão e diagnóstico", "pros": "Coerente com a D86; sem promessa de restituição prescrita.", "contras": "Tira a tese da vitrine de recuperação.", "risco": "Baixo.", "efeito": "Catálogo único."},
           {"nome": "B · Duas portas (passivo e restituição como tese)", "pros": "Mais oferta.", "contras": "Restituição a quem não discutiu está prescrita.", "risco": "Promessa indevida.", "efeito": "Atrito com cliente."}],
   recomendacao="Aprovar a opção A: o Funrural antigo é produto de Gestão de Passivo (dono Jurídico); a T19 fica no catálogo do Tributário só como remissão e diagnóstico (planejamento de 2018 em diante, LC 224/2025 a validar); restituição só dentro de ação ajuizada a tempo ou depósito judicial, como serviço de advogado; o catálogo cita a ADI 4.395; nada vai ao cliente antes do acórdão e da modulação e do validador humano (D94).",
   se_reprovada="O catálogo segue com a nota 'a conciliar' e o material de Funrural fica congelado.",
   divergencias="Ajuste das duas áreas à proposta do Gabinete: a restituição não vira tese ativa (prescrição). Aceito.",
   execucao={"dono": "Jurídico (produto) e Tributário (catálogo)", "prazo": "07/11, com o validador humano", "indicador": "catálogo corrigido; material de Funrural com 0 achados ALTO no auditor"})

# ---------------- Produtos em validação ----------------
dz("D108", titulo="Zero hora do time em produtos em validação até o G2",
   folha="23 (inclui 14 e 18)", prazo="2026-11-06", padrao="",
   o_que_decidir="Se o time fica com 0 h em Crédito Internacional e Maquila até o G2 de 15/12 (Luis até 4 h/semana), se D30–D39 e D49–D60 passam a 'congeladas até o G2' e se a J03 (estoque do art. 381) fica para 2027 salvo dono e preço até 06/11.",
   por_que_agora="O núcleo caiu 4 semanas seguidas e há 28 decisões pendentes com o Luis; a J03 depende do inventário de 31/12/2026.",
   custo_nao_decidir="Dispersão das 3 prioridades por pessoa; 4+ h/semana do Luis com dezenas de decisões paradas (estimativa do Conselho).",
   contexto=CTX_PV + [("J03 = LC 214/2025, art. 381: crédito presumido sobre o estoque, só contra a CBS, com inventário em 31/12/2026 (Decreto 12.955/2026, arts. 605–609); apuração até 30/06/2027, a conferir.", "pareceres Jurídico e Tributário de 26/10 (pré-análise)", F)],
   opcoes=[{"nome": "A · Confirmar 0 h e congelar; J03 decidida em 06/11", "pros": "Foco no núcleo.", "contras": "Janeiro sem produto novo (contra-argumento da Estratégia).", "risco": "Médio; gatilho de 30/06/2027.", "efeito": "3 prioridades por pessoa intactas."},
           {"nome": "B · Manter o calendário de CI e Maquila", "pros": "Produto novo mais cedo.", "contras": "Horas do time fora do núcleo.", "risco": "Q4 abaixo do conservador.", "efeito": "Dispersão."},
           {"nome": "C · Decidir a J03 agora (dono e preço)", "pros": "Inventário com dono.", "contras": "Exige Técnico com capacidade.", "risco": "Capacidade desconhecida.", "efeito": "Serviço novo no Q4."}],
   recomendacao="Aprovar a opção A, explicitando: (1) o piloto do originador sucroenergético (D77) e a one-page (D88) seguem com Luis e João dentro das 4 h; (2) o prazo de 31/10 das respostas do João não congela; (3) pergunta de Master sobre CI ou Maquila vai direto ao João; (4) a J02 (saldos credores até 30/11 e 31/12) não congela; (5) em 06/11 o Luis escolhe na J03 entre serviço com dono e preço, aviso técnico único sem promessa à carteira elegível (material em escala, com validador) ou congelar sem aviso.",
   se_reprovada="CI e Maquila seguem os calendários das atas de 02/10 e 05/10, e o Gabinete refaz a carga de cada pessoa antes do D0.",
   divergencias="Estratégia (Conselho) registra o contra-argumento de janeiro sem produto novo; mantido o gatilho de 30/06/2027. Na J03, Jurídico propõe três saídas e Tributário prefere o aviso único: fica para o Luis em 06/11.",
   execucao={"dono": "Luis com João Mattos (produtos); Pessoas (comunicação na 1:1); Tributário e Jurídico (J03)", "prazo": "06/11 (J03); 15/12 (G2)", "indicador": "horas do time em produto em validação = 0; horas do Luis ≤ 4/semana medidas no pacote"})

dz("D54", titulo="Teto único de horas em produtos novos",
   folha="19", prazo="2026-11-06", padrao="",
   o_que_decidir="Se vale o teto único de horas em produtos novos (Luis até 4 h/semana; time 0 h até as 1:1; depois Daniela até 1 h, Jenifer até 2 h e Geovana 0), absorvendo a D33.",
   por_que_agora="É a regra que a D108 confirma; os gatilhos de pausa da D54 (outubro sem ganhos até 17/10) venceram.",
   custo_nao_decidir="Carga do time em produto em validação sem limite escrito.",
   contexto=CTX_PV[:2] + [("Os gatilhos de pausa já dispararam (outubro −61%), e as 4 h do Luis não são medidas.", "parecer Internacional de 26/10", F)],
   opcoes=[{"nome": "A · Aprovar ajustada pela D108: 0 h até o G2; envelopes pós-G2 só se o G2 der GO", "pros": "Coerente com a D108.", "contras": "Nenhum relevante.", "risco": "Baixo.", "efeito": "Regra única."},
           {"nome": "B · Aprovar o texto original", "pros": "Já discutido.", "contras": "Gatilho vencido; conflita com a D108.", "risco": "Duas regras.", "efeito": "Confusão."}],
   recomendacao="Aprovar a opção A; trocar o gatilho de pausa pela meta da D111 (pausa se os ganhos do mês ficarem abaixo de 0,7 × meta por 2 semanas); Daniela só terá 1 h pós-G2 se os parados estiverem em até 40 e os bloqueios do repasse tiverem caído 50%; medir as 4 h do Luis no pacote.",
   se_reprovada="Vale a D33 (superada) por omissão; o Gabinete reapresenta com a D108.",
   divergencias="Nenhuma (5 pareceres).",
   execucao={"dono": "depto-pessoas (rascunho) e Luis", "prazo": "06/11, junto com a D108", "indicador": "horas por pessoa em produto em validação no pacote semanal"})

def pv(id, titulo, folha, o_que, rec, opcoes=None, ctx=None, prazo="2026-12-15", custo="Perto de zero até o G2 (15/12): o produto está em validação e sem horas do time.", por_que="Está pendente desde a ata de origem e entra na D108 (congelar até o G2).", se_rep="Fica pendente como hoje; volta no G2 de 15/12 com critério escrito.", div="Nenhuma.", exe=None):
    dz(id, titulo=titulo, folha=folha, prazo=prazo, padrao="",
       o_que_decidir=o_que, por_que_agora=por_que, custo_nao_decidir=custo,
       contexto=(ctx or []) + CTX_PV[:1],
       opcoes=opcoes or [{"nome": "A · Congelar até o G2 (D108)", "pros": "Sem horas do time; decide com evidência.", "contras": "Adia o produto.", "risco": "Baixo.", "efeito": "Volta em 15/12."},
                         {"nome": "B · Aprovar agora", "pros": "Avança o produto.", "contras": "Conflita com a D108.", "risco": "Horas do time fora do núcleo.", "efeito": "Produto anda no Q4."}],
       recomendacao=rec, se_reprovada=se_rep, divergencias=div,
       execucao=exe or {"dono": "João Mattos (dono do produto) com o Luis", "prazo": "15/12 (G2)", "indicador": "decisão no G2 com critério escrito"})

pv("D30", "CI: GO condicional à Preparação e NO-GO externo até o G2", "18",
   "Se o Crédito Internacional segue em Preparação no Q4 com NO-GO para qualquer conversa com parceiro ou cliente sobre condições até o G2, e GO/NO-GO do piloto em 15/12.",
   "Congelar; o NO-GO externo segue valendo (D98/D108); a preparação fica só com João e Luis dentro das 4 h.",
   ctx=[("As 7 perguntas críticas do CI estão abertas e não há parecer humano.", "parecer Internacional de 26/10; " + ATA_CI, F)])
pv("D31", "CI: critérios de go/no-go por fase", "18",
   "Se valem os critérios objetivos de go/no-go por fase (piloto: 8 critérios; expansão; escala) e o timebox de 90 dias.",
   "Congelar; os 8 critérios do G2 já estão escritos (ata de 02/10, seção A6): o João confirma ou ajusta até 01/12 e acrescenta um critério financeiro.",
   ctx=[("Os 8 critérios do piloto estão na seção A6 da ata de 02/10; o timebox de 90 dias começou em 02/10.", ATA_CI, F)], prazo="2026-12-01")
pv("D34", "CI: metas 2027 preliminares", "18",
   "Se as metas de validação do Crédito Internacional viram oficiais para 2027, com receita só como potencial e sem meta individual de crédito para o time.",
   "Congelar até o G2; a regra de medição já pode valer (metas de validação; receita zero na meta oficial). Ao descongelar, recalcular com o repasse de 10% da D78.",
   ctx=[("Com o repasse de 10% da D78, o potencial passa de R$ 2,2 mi para cerca de R$ 2,6 mi.", "parecer Resultados de 26/10", E)])
pv("D35", "CI: correções do material e divisão 03a/03b", "18",
   "Se as correções 03-1 a 03-9 e 04-1 a 04-9 são aprovadas e o material fica dividido em 03a (interno) e 03b (parceiro), sem turnkey e equity na versão ao parceiro.",
   "Congelar; nenhum material ao parceiro antes do G2; o 03b não circula nem como rascunho; incluir no congelamento o 22-material-externo-cliente-v2.md; ordem para destravar: D39 primeiro, depois as correções.",
   ctx=[("A divisão 03a/03b já foi feita em 02/10; o 03b cita token, IOF e 'aprovado' e hoje passa no auditor sem achado ALTO.", "pareceres Partner Success e Qualidade de 26/10", F)])
pv("D36", "Padrão de Produto Novo (v1)", "18",
   "Se a Save adota o Padrão de Produto Novo (Kit K00–K20, portões G0–G4, donos, prefixo de IDs, timebox de 90 dias) como regra para qualquer produto novo.",
   "Aprovar agora como regra interna, junto com a D60 (v1.1): não consome horas do time e define o que o G2 exige. O Gabinete atualiza o arquivo para a v1.1 até 06/11 e registra o início do timebox de cada produto (CI 02/10, MQ 05/10).",
   opcoes=[{"nome": "A · Aprovar como regra interna (v1.1 com a D60)", "pros": "Define o G2; sem despesa.", "contras": "Nenhum relevante.", "risco": "Baixo.", "efeito": "Portões com critério escrito."},
           {"nome": "B · Congelar com o resto", "pros": "Uniformidade.", "contras": "G2 sem regra escrita.", "risco": "G2 vira opinião.", "efeito": "Nenhum."}],
   ctx=[("O arquivo departamentos/produtos/PADRAO-PRODUTO-NOVO.md ainda está na v1.", "parecer Internacional de 26/10", F)], prazo="2026-11-06",
   exe={"dono": "Gabinete (arquivo) e João Mattos (aplicação)", "prazo": "06/11", "indicador": "v1.1 publicada; timebox registrado por produto"})
pv("D37", "Produto no HubSpot: propriedade 'Produto' ou pipeline próprio", "18",
   "Como registrar produtos no HubSpot: (A) propriedade 'Produto' em pipeline existente ou (B) pipeline próprio; criação pelo time de CRM antes do 1º negócio.",
   "Aprovar a opção A para todos os produtos, separada da D108: lista fechada só com os produtos prontos agora (CI e MQ entram depois do G2); sem migrar pipelines existentes; definir antes do 1º negócio se o 'valor' é operação ou fee; o Dados testa o filtro (código novo no calc_semana.py) antes.",
   opcoes=[{"nome": "A · Propriedade 'Produto' em lista fechada", "pros": "Destrava o funil por produto (hoje cinza) e o cross-sell.", "contras": "Exige filtro novo.", "risco": "Baixo.", "efeito": "Métrica sai do cinza."},
           {"nome": "B · Pipeline próprio por produto", "pros": "Separação visual.", "contras": "Multiplica pipelines; mesmo trabalho de filtro.", "risco": "Fragmentação.", "efeito": "Igual, com mais manutenção."}],
   ctx=[("A métrica 'funil por produto' está cinza por falta da propriedade; clientes com 2+ produtos = 1,4%.", PAC + " (semáforo)", F),
        ("O calc_semana.py não filtra por pipeline: A ou B exigem código novo.", "parecer Dados & BI de 26/10", F)], prazo="2026-11-06",
   custo="A métrica de funil por produto segue cinza e o cross-sell (meta de clientes com 2+ produtos) não se mede.",
   por_que="Vale também para os produtos prontos (Gestão de Passivo, Save Invest); não depende das horas do time.",
   exe={"dono": "time de CRM (cria) e Dados & BI (testa)", "prazo": "06/11", "indicador": "funil_por_produto fora do cinza"})
pv("D38", "CI: pacote de verificação do G2", "18",
   "Se o G2 do Crédito Internacional exige o pacote de verificação: pareceres jurídicos e tributários humanos, due diligence dos fundos e respostas escritas do João até 31/10, com custo orçado.",
   "Aprovar o escopo, com pareceres externos (sem horas do time técnico) e em etapas: J1 (intermediação de crédito sem autorização) e J4 (fundos) primeiro; se J1 der impedimento, o resto não se contrata. Incluir J5 (remuneração do parceiro), J9 (LGPD), juros (Lei 12.249) e preço de transferência (Lei 14.596). O João traz o orçamento até 31/10 e a contratação volta ao Luis; lembrete único ao João até 28/10.",
   opcoes=[{"nome": "A · Escopo aprovado, pareceres externos em etapas, custo volta ao Luis", "pros": "G2 possível em 15/12 sem horas do time.", "contras": "Custo externo.", "risco": "Orçamento acima do esperado.", "efeito": "G2 com evidência."},
           {"nome": "B · Congelar o pacote", "pros": "Nenhuma despesa nova.", "contras": "G2 de 15/12 fica impossível.", "risco": "Produto parado.", "efeito": "G2 em 2027."},
           {"nome": "C · Exceção de horas do técnico interno com teto", "pros": "Nenhuma despesa externa.", "contras": "Conflita com a D108.", "risco": "Fila do núcleo.", "efeito": "Parecer interno."}],
   ctx=[("As 7 perguntas críticas do CI seguem abertas a 5 dias de 31/10.", "parecer Internacional de 26/10", F)], prazo="2026-10-31",
   custo="Sem o pacote, o G2 de 15/12 não tem como decidir; o timebox de 90 dias vence em 31/12.",
   por_que="As respostas escritas do João vencem em 31/10 e o G2 é em 15/12.",
   div="Tributário: o parecer do 'técnico tributário' é hora do time e conflita com a D108; resolvido pela opção A (externo). Jurídico pede J5 e J9 e contratação em etapas; aceito.",
   exe={"dono": "João Mattos (orçamento e respostas); Luis (contratação)", "prazo": "31/10 (respostas e orçamento); 15/12 (G2)", "indicador": "pareceres J1 e J4 entregues antes de 01/12"})
pv("D39", "Regras de auditoria por produto ('o que não dizer')", "18",
   "Se o auditor de promessas ganha regras próprias do Crédito Internacional (token/IOF, % de taxa, 'aprovado', taxa de análise) e uma regra geral de 'o que não dizer' por produto.",
   "Aprovar agora (só restringe e reduz risco): regras de CI, Maquila (financiamento, escritório, '1%') e Funrural na primeira lista; as formas já aprovadas nas D77 e D88 entram como exceção; a lista de nomes de cliente fica fora do git. Qualidade faz pela D98, sem horas do time.",
   opcoes=[{"nome": "A · Aprovar agora", "pros": "Fecha a brecha do auditor.", "contras": "Nenhum.", "risco": "Falso positivo, tratável.", "efeito": "Material de CI e MQ barrado pelo auditor."},
           {"nome": "B · Congelar", "pros": "Nenhum.", "contras": "Auditor cego para CI e MQ.", "risco": "Promessa indevida.", "efeito": "Nenhum."}],
   ctx=[("O auditor tem 16 regras e 0 menções a token, IOF, Funrural, Maquila ou internacional; o prazo da ata (23/10) venceu.", "pareceres Jurídico e Qualidade de 26/10 (regras-promessas.json)", F)], prazo="2026-11-06",
   custo="Material de CI e MQ passa no auditor sem achado mesmo citando token, IOF e 'aprovado'.",
   por_que="O prazo da ata de 02/10 (23/10) venceu e o Funrural vai a mercado antes.",
   exe={"dono": "depto-qualidade", "prazo": "06/11", "indicador": "03b com achados ALTO detectados pelo auditor"})
pv("D49", "MQ: GO condicional ao G0 (vencido)", "14",
   "Se a Maquila mantém o GO condicional ao G0 de 16/10, com 7 critérios e NO-GO para material, preço ou condição até o G2.",
   "Dar como superada (data vencida). A Maquila não entra no G2 de 15/12: nessa data decide o G0 ou vai à geladeira (sem estudo pago até 30/06/2027).",
   ctx=[("A Maquila nunca passou do G0; os validadores (D55) estão congelados.", "parecer Internacional de 26/10; " + ATA_MQ, F)],
   div="A área Internacional contesta a proposta inicial do Gabinete (Maquila no G2 único): sem G0 e sem validadores, não há G2. O Gabinete adota a posição da área.")
pv("D51", "MQ: calendário e critérios dos portões", "14",
   "Se vale o calendário G1 04/12, G2 15/12, G3 15/01/2027 e G4 com margem positiva, com geladeira sem estudo pago até 30/06/2027.",
   "Congelar o calendário (ficou impossível) e recalendar até 06/11 depois das respostas do João; a regra da geladeira e o critério do G4 valem desde já.",
   prazo="2026-11-06")
pv("D52", "MQ: 10 conversas de descoberta no Q4", "14",
   "Se a Maquila faz 10 conversas de descoberta no Q4, com Master presente e roteiro auditado.",
   "Reprovar para o Q4 (conflita com 0 h do time e com o foco no núcleo); demanda espontânea de Master é registrada e vai ao João e ao Paulo; reavaliar após o G2.",
   opcoes=[{"nome": "A · Reprovar para o Q4", "pros": "Coerente com a D108.", "contras": "Sem evidência de demanda.", "risco": "Baixo.", "efeito": "Time no núcleo."},
           {"nome": "B · Aprovar", "pros": "Evidência de mercado.", "contras": "Horas da Jenifer e da Daniela.", "risco": "Fila do núcleo.", "efeito": "10 conversas."}])
pv("D53", "MQ: conta da casa no piloto", "14",
   "Se, no piloto da Maquila, a conta é da casa com preferência ao parceiro de origem (consulta às 5–7 contas, 10 dias úteis).",
   "Congelar (só tem objeto com piloto). Registrar o pedido de Operações de Canal: transformar em regra geral de 'conta da casa e preferência ao parceiro de origem' para todos os produtos 2027 até 15/12.",
   ctx=[("68 das 90 contas-alvo já compraram recuperação; 82 raízes de CNPJ com mais de um canal.", "parecer Operações de Canal de 26/10", F)],
   div="Operações de Canal quer a regra geral para os produtos 2027; não conflita com o congelamento. Fica como item novo para o Luis (conflito de canal é alçada dele).")
pv("D55", "MQ: designar advogado, técnico e assessor paraguaio", "14",
   "Se a Maquila designa advogado(a), técnico tributário e assessor paraguaio, com escopo do G2 e custo orçado.",
   "Congelar a contratação até as respostas do João; o orçamento sai junto com o da D38 e a contratação volta ao Luis; assessor habilitado no Paraguai; definir antes qual empresa da Save contrata.")
pv("D57", "MQ: propriedade 'Produto = MQ'", "14",
   "Se a Maquila usa a propriedade 'Produto = MQ', com descoberta registrada como atividade e sem negócio até diagnóstico aceito pós-G2.",
   "Decidir junto com a D37 (opção A): a Maquila vira um valor da mesma propriedade, sem negócio antes do G2.")
pv("D58", "MQ: carga da Receita", "14",
   "Se a TI faz a carga da Receita para a Maquila (núcleo industrial + RS).",
   "Congelar: sem abordagem antes do G2; a carga é uma extração nova (≈ 5 GB), a fazer depois do G2 em janela noturna, sem rotina nova.",
   ctx=[("A base local da Receita é de setembro e cobre 12 estados; o RS tem só 191 estabelecimentos.", "parecer Dados & BI de 26/10", F)])
pv("D59", "MQ: calculadora como simulador interno", "14",
   "Se a calculadora da Maquila vira simulador interno de faixa: sem R$ por CNPJ, setores com fator PENDENTE bloqueados, pessimista primeiro, capex obrigatório.",
   "Aprovar as restrições (só protegem) e o bloqueio efetivo dos setores PENDENTE com aviso fixo no topo, feito pelo agente sem horas do time; abas novas congeladas.",
   ctx=[("Os setores com fator PENDENTE aparecem com fator 1,00 no simulador, sem bloqueio; não há tributos do retorno ao Brasil nem preço de transferência.", "parecer Tributário de 26/10", F)],
   prazo="2026-11-06",
   div="Internacional diz que a restrição 'já está aplicada em parte'; Tributário mostra que o bloqueio dos setores PENDENTE não funciona. O Gabinete adota o bloqueio efetivo.",
   exe={"dono": "depto-internacional (agente)", "prazo": "06/11", "indicador": "setores PENDENTE sem número no simulador"})
pv("D60", "Padrão de Produto Novo v1.1 (11 lições do MQ)", "18",
   "Se o Padrão de Produto Novo ganha a v1.1 com as 11 lições da Maquila (bloqueio de peça antes do G2, envelope de horas, custo de oportunidade, fonte única de números, entre outras).",
   "Aprovar junto com a D36 como regra interna; o Gabinete publica a v1.1 até 06/11.", prazo="2026-11-06",
   exe={"dono": "Gabinete", "prazo": "06/11", "indicador": "v1.1 publicada"})

# ---------------- Folha ----------------
dz("F8", titulo="Programa de Parceiros: decisões L1–L10",
   folha="8", prazo="2026-11-14", padrao="",
   o_que_decidir="Se o Luis decide em bloco L1–L4, L6–L8 e L10 do Programa de Crescimento do Parceiro e do Programa Partners 2027, conforme a proposta de 09/10 (L5 no comentário).",
   por_que_agora="O programa está parado desde 09/10 e o Word não pode ser regerado sem essas respostas; parte não depende do G2.",
   custo_nao_decidir="Programa Partners 2027 sem texto final para o planejamento de 2027; nenhum efeito no repasse da recuperação (não muda em 2027).",
   contexto=[("Proposta de 09/10: L1 cinco níveis de 10% a 30% (nível é teto; escopo executado define o pagamento; mínimo 10%); L2 nenhum ajuste para baixo em 2027; L3 patamares sem R$ até a P15; L4 fila técnica não muda; L6 anti-oscilação; L7 Daniela como CS dos parceiros de CI até 8; L8 Programa Partners 2027 em documento próprio; L10 aprovar o 25 como projeto, opção A em 2027, sem reduzir repasse.", "departamentos/produtos/credito-internacional/24, 24b e 25 (09/10)", F),
             ("L5 = teto de entrada de 20% nas 2 primeiras operações para quem tiver a trilha T3 certificada; a trilha ainda não existe; muda a leitura da D61.", "24b-anexos-programa.md (P35); pareceres de 26/10", F),
             ("L9 já decidida em 09/10.", "gabinete/SESSOES.md §2", F)],
   opcoes=[{"nome": "A · Aprovar L4, L8 e L10 já; L1–L3, L6 (opção 2 do Conselho) e L7 como desenho interno com efeito após o G2; L5 no G2 com diretoria e Jurídico", "pros": "Destrava o Word sem conflitar com a D108.", "contras": "Programa do CI só vale após o G2.", "risco": "Baixo.", "efeito": "Word regerado."},
           {"nome": "B · Tudo em bloco agora", "pros": "Simples.", "contras": "Dá efeito a regra de produto em validação.", "risco": "Conflito com a D108.", "efeito": "Programa completo."},
           {"nome": "C · Adiar tudo para o G2", "pros": "Nenhum trabalho.", "contras": "Partners 2027 parado sem motivo.", "risco": "Planejamento 2027 sem programa.", "efeito": "Nenhum."}],
   recomendacao="Aprovar a opção A. Na L6, a opção 2 do Conselho (2 trimestres de observação para todos; amortecedor multiproduto em 3 trimestres), mais simples.",
   se_reprovada="O Word segue parado; o Gabinete reapresenta no G2.",
   divergencias="Nenhuma: Partner Success e Operações de Canal chegam à mesma divisão.",
   execucao={"dono": "depto-partner-success (texto e Word) e Operações de Canal (regras)", "prazo": "14/11 (Word regerado)", "indicador": "Word do 25 republicado; L5 na pauta do G2"})

dz("F11", titulo="Publicar o relatório Big Four × Save",
   folha="11", prazo="2026-11-06", padrao="",
   o_que_decidir="Se o relatório Big Four × Save é publicado como uso interno, com as lacunas marcadas.",
   por_que_agora="Parado desde 19/10; serve de base ao portfólio 2027.",
   custo_nao_decidir="Baixo: pesquisa envelhece (radar mensal) e o portfólio 2027 perde a referência.",
   contexto=[("Auditor de promessas: 3 achados MÉDIO (regra P5.1), todos descrevendo como as Big Four vendem; 0 ALTO.", "parecer Qualidade de 26/10 (auditar_texto.py, regras v1.0)", F),
             ("O texto usa a esteira antiga (Oxigenar → Estruturar → Expandir), prende FIDC e antecipação ao G2 (prontos desde 19/10) e cita '7 setores' e '831 clientes ganhos' sem data.", "parecer Contas e Soluções de 26/10", F)],
   opcoes=[{"nome": "A · Publicar como uso interno depois das correções", "pros": "Base coerente com as decisões atuais.", "contras": "Uma rodada de ajuste.", "risco": "Baixo.", "efeito": "Publicado até 06/11."},
           {"nome": "B · Publicar como está", "pros": "Rápido.", "contras": "Erros de fato e esteira antiga.", "risco": "Leitura errada do portfólio.", "efeito": "Ruído."}],
   recomendacao="Aprovar a opção A: corrigir esteira (Destravar caixa → Proteger e controlar → Crescer), produtos prontos, setores e datas; reescrever o item 5 do sumário sem valor ou prazo; rótulo 'Uso interno'; os 3 MÉDIO registrados como falso positivo.",
   se_reprovada="O relatório segue parado com a nota 'ajustes pedidos'.",
   divergencias="Nenhuma de mérito. A recomendação preliminar do Gabinete dizia '0 achados'; o auditor deu 3 MÉDIO (falso positivo).",
   execucao={"dono": "depto-solucoes, com Qualidade", "prazo": "06/11", "indicador": "relatório publicado com 0 ALTO no auditor"})

ORDEM_PV = {"D108": 0}

def carregar_pareceres():
    out = {}
    for f in sorted(glob.glob(os.path.join(PARECERES, "*.json"))):
        for p in json.load(open(f, encoding="utf-8")):
            out.setdefault(p["id"], []).append(p)
    return out

MAPA = {"D60": ["D36"], "D57": ["D57", "D37"], "D36": ["D36"], "D37": ["D37"]}

def montar():
    par = carregar_pareceres()
    os.makedirs(PASTA, exist_ok=True)
    ordem = sorted(D.values(), key=lambda d: (d["prazo"], 0 if d.get("padrao") else 1, d["id"]))
    for n, d in enumerate(ordem, 1):
        vals, extras = [], []
        for pid in MAPA.get(d["id"], [d["id"]]):
            for p in par.get(pid, []):
                vals.append({"area": p["area"], "especialista": p.get("especialista", ""), "parecer": p["parecer"],
                             "motivo": p.get("motivo", ""), "base": p.get("base", ""), "condicao": p.get("condicao", ""),
                             "ressalva": p.get("ressalva", "") or ""})
                for fa in (p.get("fatos") or [])[:2]:
                    extras.append({"fato": fa.get("fato", ""), "fonte": f"{fa.get('fonte','')} (via parecer {p['area']})", "tipo": fa.get("tipo", "fato")})
        ctx = [{"fato": a, "fonte": b, "tipo": c} for a, b, c in d["contexto"]]
        vistos = {c["fato"] for c in ctx}
        ctx += [e for e in extras if e["fato"] and e["fato"] not in vistos][:4]
        doc = {"id": d["id"], "titulo": d["titulo"], "urgencia": n, "prazo": d["prazo"], "folha_item": d.get("folha", ""),
               "padrao": d.get("padrao", ""),
               "o_que_decidir": d["o_que_decidir"], "por_que_agora": d["por_que_agora"], "custo_nao_decidir": d["custo_nao_decidir"],
               "contexto": ctx, "opcoes": d["opcoes"], "recomendacao": d["recomendacao"], "se_reprovada": d["se_reprovada"],
               "validacoes": vals, "divergencias": d["divergencias"], "execucao": d["execucao"],
               "atualizado_em": HOJE, "fonte_pareceres": os.path.relpath(PARECERES, AP),
               "revisao": {"gerente": "Gabinete (Consolidador)", "areas_consultadas": sorted({v["area"] for v in vals}), "rodadas": 1, "aprovado": True}}
        json.dump(doc, open(os.path.join(PASTA, f"{d['id']}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(ordem)} dossiês em {PASTA}")

if __name__ == "__main__":
    montar()
