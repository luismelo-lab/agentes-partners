"""Crédito internacional · Scorecard de qualificação (planilha com fórmulas) + base pré-qualificada pelos dados.

Uso:  python3 qualificacao_planilha.py   -> grava a planilha na pasta do produto e no OneDrive (Gestão · Luis/Produtos)
Somente leitura nas fontes; nada vai ao HubSpot; não lê .env.
"""
import collections, json, os, shutil, subprocess, sys
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as CL
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qualificacao_dados import montar, PASTA, DOLAR

NOME = "Credito-Internacional-Scorecard-Qualificacao.xlsx"
AZUL, BRANCO = "1F3864", "FFFFFF"
F_HEAD = PatternFill("solid", fgColor=AZUL); F_SUB = PatternFill("solid", fgColor="D9E1F2")
F_IN = PatternFill("solid", fgColor="FFF2CC"); F_EX = PatternFill("solid", fgColor="F2F2F2")
F_OK = PatternFill("solid", fgColor="C6EFCE"); F_WARN = PatternFill("solid", fgColor="FFEB9C"); F_BAD = PatternFill("solid", fgColor="FFC7CE")
F_GREY = PatternFill("solid", fgColor="EDEDED")
BOLD = Font(bold=True); HFONT = Font(bold=True, color=BRANCO); TITLE = Font(bold=True, size=14, color=AZUL)
WRAP = Alignment(wrap_text=True, vertical="top"); CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
THIN = Border(*(Side(style="thin", color="BFBFBF"),) * 4)

# ---------------------------------------------------------------- critérios
KOS = [  # (código, cabeçalho curto)
    ("K1", "K1 Necessidade ≥ US$ 5 mi?"),
    ("K2", "K2 Garantia livre ≈ 2x (mín. 1,5x)?"),
    ("K3", "K3 Demonstrações de 2 anos (2024 e 2025)?"),
    ("K4", "K4 Aceita operação em moeda estrangeira?"),
    ("K5", "K5 Pode esperar 3 meses ou mais?"),
    ("K6", "K6 Sem restrição de compliance/PLD?"),
    ("K7", "K7 Fora de recuperação judicial/falência?"),
    ("K8", "K8 Faturamento comprovável ≥ R$ 30 mi?"),
    ("K9", "K9 Finalidade definida?"),
    ("K10", "K10 Aceita etapas com comprovação e o empresário participa?"),
]
KO_MOTIVO = ["necessidade abaixo de US$ 5 mi", "garantia livre insuficiente", "sem 2 anos de demonstrações", "não aceita moeda estrangeira",
             "precisa em menos de 3 meses", "restrição de compliance/PLD", "recuperação judicial/falência", "faturamento abaixo de R$ 30 mi",
             "sem finalidade definida", "não aceita etapas/empresário ausente"]

CRIT = [  # (chave, nome, peso, [(opção, pontos)])
    ("porte", "1 Porte comprovado", 12, [
        ("≥ R$ 100 mi/ano, com balanço e DRE", 12), ("R$ 50–100 mi/ano, com balanço e DRE", 10),
        ("≥ R$ 50 mi declarado, documento ainda não visto", 5), ("R$ 30–50 mi comprovado (exceção: validar com o João)", 3),
        ("Abaixo de R$ 30 mi ou não sabe", 0)]),
    ("nec", "2 Necessidade e finalidade", 12, [
        ("Troca de dívida cara, com dívidas listadas", 12), ("Expansão com projeto e números", 10),
        ("Capital de giro com ciclo claro (safra, estoque)", 8), ("Finalidade genérica (reforçar o caixa)", 2),
        ("Cobrir prejuízo sem plano de virada", 0)]),
    ("ticket", "3 Ticket", 8, [
        ("US$ 10 mi ou mais (cabe nas duas estruturas)", 8), ("US$ 5–10 mi (estrutura suíça)", 6),
        ("Perto de US$ 5 mi, valor ainda impreciso", 3), ("Abaixo de US$ 5 mi", 0)]),
    ("gar", "4 Garantias (tipo, liquidez, cobertura)", 15, [
        ("Imóveis ou fazendas livres, avaliados, ≥ 2x", 15), ("Livres ≥ 2x, sem avaliação ou mistas (recebíveis, equity, VGV)", 11),
        ("Entre 1,5x e 2x, ou de terceiros com anuência", 6), ("Com ônus a liberar (recompra de dívida)", 3),
        ("Menos de 1,5x ou só intangíveis sem avaliação", 0)]),
    ("info", "5 Qualidade da informação", 10, [
        ("Balanço auditado, DRE e receita 100% formalizada", 10), ("Balanço e DRE de 2 anos pelo contador, receita formalizada", 7),
        ("Demonstrações incompletas, o contador fecha em até 30 dias", 4), ("Parte da receita não formalizada (João e Jurídico)", 1),
        ("Sem demonstrações organizadas", 0)]),
    ("hedge", "6 Hedge natural (exportação)", 6, [
        ("Exporta 30% ou mais da receita", 6), ("Exporta menos de 30% ou preço atrelado ao dólar", 4),
        ("Sem receita em moeda forte, aceita discutir hedge", 2), ("Sem receita em moeda forte e resistente ao câmbio", 0)]),
    ("custo", "7 Custo da dívida atual", 8, [
        ("Acima de 20% ao ano em parte relevante da dívida", 8), ("Entre 15% e 20% ao ano", 6),
        ("Sem dívida relevante (projeto novo)", 3), ("Abaixo de 15% ao ano (linhas direcionadas)", 2), ("Não sabe informar", 0)]),
    ("gov", "8 Governança e decisor", 6, [
        ("Dono/decisor na conversa e sócios alinhados", 6), ("Decisor identificado, ainda fora da conversa", 3),
        ("Conflito societário ou decisor desconhecido", 0)]),
    ("urg", "9 Urgência compatível", 4, [
        ("Precisa em 3 a 12 meses, com planejamento", 4), ("Precisa em mais de 12 meses (nutrir)", 2), ("Precisa em menos de 3 meses", 0)]),
    ("hist", "10 Histórico do empresário", 7, [
        ("10 anos ou mais no setor, reputação conhecida", 7), ("5 a 10 anos no setor", 4),
        ("Menos de 5 anos ou eventos a explicar", 1), ("Restrições relevantes (processos, protestos recorrentes)", 0)]),
    ("ader", "11 Aderência à entrega", 12, [
        ("Parecido com os casos em teste; estrutura conhecida; time com capacidade", 12),
        ("Setor aderente, com um ponto novo a estruturar", 8), ("Fora dos casos em teste; estruturável com o João", 4),
        ("Fora do que a Save estrutura hoje ou sem capacidade do time", 0)]),
]
assert sum(c[2] for c in CRIT) == 100 and all(max(p for _, p in c[3]) == c[2] for c in CRIT)
PARAM = [("Corte de Qualificado (pontos)", 70), ("Corte de Em desenvolvimento (pontos)", 50),
         ("Mínimo em Porte para Qualificado", 10), ("Mínimo em Garantias para Qualificado", 11),
         ("Mínimo em Aderência à entrega para Qualificado", 8), ("Dólar de referência (R$, 02/10/2026)", DOLAR)]
SETORES_SC = ["Café/agro", "Frigorífico/alimentos", "Construtora", "Indústria exportadora", "Hortifruti/atacado", "Outro"]

NLIN_SC = 300          # linhas do Scorecard
L0 = 5                 # primeira linha de dados (Scorecard e Base)


def cab(ws, row, cols, altura=45):
    for i, t in enumerate(cols, 1):
        c = ws.cell(row, i, t); c.fill = F_HEAD; c.font = HFONT; c.alignment = CENTER; c.border = THIN
    ws.row_dimensions[row].height = altura


def tabelas(wb):
    ws = wb.create_sheet("Tabelas")
    ws["A1"] = "Tabelas do scorecard (listas dos menus e pontos). Alterar aqui muda a pontuação de todas as linhas."; ws["A1"].font = BOLD
    ref = {}
    r = 3
    ws.cell(r, 1, "Parâmetros").font = BOLD; r += 1
    for nome, v in PARAM:
        ws.cell(r, 2, nome); c = ws.cell(r, 3, v); c.fill = F_IN; ref[nome] = f"Tabelas!$C${r}"; r += 1
    r += 1
    ws.cell(r, 1, "SIM/NÃO").font = BOLD; ws.cell(r, 2, "SIM"); ws.cell(r + 1, 2, "NÃO"); ref["simnao"] = f"Tabelas!$B${r}:$B${r+1}"; r += 3
    ws.cell(r, 1, "Setor").font = BOLD
    for i, s in enumerate(SETORES_SC): ws.cell(r + i, 2, s)
    ref["setor"] = f"Tabelas!$B${r}:$B${r+len(SETORES_SC)-1}"; r += len(SETORES_SC) + 1
    for chave, nome, peso, ops in CRIT:
        ws.cell(r, 1, f"{nome} (peso {peso})").font = BOLD
        for i, (o, p) in enumerate(ops):
            ws.cell(r + i, 2, o); ws.cell(r + i, 3, p)
        ref[chave] = f"Tabelas!$B${r}:$B${r+len(ops)-1}"; ref[chave + "_tab"] = f"Tabelas!$B${r}:$C${r+len(ops)-1}"
        r += len(ops) + 1
    ws.column_dimensions["A"].width = 42; ws.column_dimensions["B"].width = 70; ws.column_dimensions["C"].width = 10
    return ref


def scorecard(wb, ref, fila):
    ws = wb.create_sheet("Scorecard", 1)
    ws["A1"] = "Scorecard de qualificação · Crédito internacional"; ws["A1"].font = TITLE
    ws["A2"] = ("Uma linha por cliente. Amarelo = você preenche (menus). Eliminatórios: SIM = atende, NÃO = elimina. "
                "Pontuação, faixa, lacunas e próximo passo são fórmulas. As 3 primeiras linhas são EXEMPLOS fictícios; "
                "depois vêm as empresas da base com prioridade para a camada 1 (aba Base pré-qualificada).")
    ws["A2"].alignment = WRAP; ws.merge_cells("A2:P2"); ws.row_dimensions[2].height = 45
    ws["A3"] = "Identificação"; ws["G3"] = "Eliminatórios (camada 1)"; ws["R3"] = "Critérios de pontuação (camada 2)"; ws["AC3"] = "Resultado (fórmulas)"; ws["AI3"] = "Pontos por critério (fórmulas)"
    for c in ("A3", "G3", "R3", "AC3", "AI3"): ws[c].font = BOLD; ws[c].fill = F_SUB
    cols = ["Empresa", "CNPJ", "Setor", "Parceiro / origem", "Data da camada 1", "Responsável Save"] + [k[1] for k in KOS] + ["Eliminatórios"] \
        + [f"{c[1]} ({c[2]})" for c in CRIT] + ["Pontuação (0–100)", "Critérios respondidos (de 11)", "Faixa", "Lacunas / motivo", "Próximo passo sugerido", "Observações"] \
        + [f"pts {c[1]}" for c in CRIT]
    cab(ws, 4, cols, 75)
    cq, cd, mp, mg, ma = (ref[n] for n, _ in PARAM[:5])
    # validações
    dv_sn = DataValidation(type="list", formula1="=" + ref["simnao"], allow_blank=True)
    dv_set = DataValidation(type="list", formula1="=" + ref["setor"], allow_blank=True)
    ws.add_data_validation(dv_sn); ws.add_data_validation(dv_set)
    last = L0 + NLIN_SC - 1
    dv_sn.add(f"G{L0}:P{last}"); dv_set.add(f"C{L0}:C{last}")
    for j, (chave, *_r) in enumerate(CRIT):
        dv = DataValidation(type="list", formula1="=" + ref[chave], allow_blank=True); ws.add_data_validation(dv)
        dv.add(f"{CL(18 + j)}{L0}:{CL(18 + j)}{last}")

    exemplos = [
        ["EXEMPLO 1 (fictício) · café exportador", "", "Café/agro", "Master", "", ""] + ["SIM"] * 10 + [None] + [
            CRIT[0][3][1][0], CRIT[1][3][0][0], CRIT[2][3][1][0], CRIT[3][3][0][0], CRIT[4][3][1][0], CRIT[5][3][0][0],
            CRIT[6][3][0][0], CRIT[7][3][0][0], CRIT[8][3][0][0], CRIT[9][3][0][0], CRIT[10][3][0][0]],
        ["EXEMPLO 2 (fictício) · construtora sem avaliação", "", "Construtora", "Master", "", ""] + ["SIM"] * 10 + [None] + [
            CRIT[0][3][2][0], CRIT[1][3][1][0], CRIT[2][3][0][0], CRIT[3][3][2][0], CRIT[4][3][2][0], CRIT[5][3][2][0],
            CRIT[6][3][1][0], CRIT[7][3][1][0], CRIT[8][3][0][0], CRIT[9][3][0][0], CRIT[10][3][1][0]],
        ["EXEMPLO 3 (fictício) · quer em reais", "", "Frigorífico/alimentos", "Master", "", ""] + ["SIM", "SIM", "SIM", "NÃO", "SIM", "SIM", "SIM", "SIM", "SIM", "SIM"] + [None] + [None] * 11,
    ]
    linhas = exemplos + [[f["empresa"], f["cnpj"], f["setor_sc"], f["parceiro"], "", ""] + [None] * 10 + [None] + [None] * 11 for f in fila]
    for i in range(NLIN_SC):
        r = L0 + i
        vals = linhas[i] if i < len(linhas) else [None] * 28
        for j, v in enumerate(vals[:28], 1):
            if j == 17: continue
            c = ws.cell(r, j, v); c.border = THIN
            if j >= 7: c.fill = F_IN
            if i < 3: c.fill = F_EX; c.font = Font(italic=True, color="595959")
        for j in range(18, 29): ws.cell(r, j).alignment = WRAP
        # pontos por critério (AI..AS = col 35..45)
        for j, (chave, *_r) in enumerate(CRIT):
            src = f"{CL(18 + j)}{r}"
            ws.cell(r, 35 + j, f'=IF({src}="","",IFERROR(VLOOKUP({src},{ref[chave + "_tab"]},2,FALSE),0))')
        ws.cell(r, 17, f'=IF(COUNTIF(G{r}:P{r},"NÃO")>0,"Elimina",IF(COUNTIF(G{r}:P{r},"SIM")=10,"Passa",IF(COUNTA(G{r}:P{r})=0,"","Incompleto")))')
        ws.cell(r, 30, f"=COUNTA(R{r}:AB{r})")
        ws.cell(r, 29, f'=IF(AD{r}=0,"",SUM(AI{r}:AS{r}))')
        ws.cell(r, 31, f'=IF($A{r}="","",IF(Q{r}="Elimina","Não qualificado",IF(Q{r}<>"Passa","Incompleto: camada 1",'
                       f'IF(AD{r}<11,"Incompleto: camada 2",IF(AND(AC{r}>={cq},AI{r}>={mp},AL{r}>={mg},AS{r}>={ma}),"Qualificado",'
                       f'IF(AC{r}>={cd},"Em desenvolvimento","Não qualificado"))))))')
        ko_txt = "&".join(f'IF({CL(7 + k)}{r}="NÃO","{KO_MOTIVO[k]}; ","")' for k in range(10))
        lac = (f'IF(AI{r}<{mp},"comprovar faturamento ≥ R$ 50 mi; ","")&IF(AL{r}<{mg},"garantia livre ≥ 2x avaliada; ","")'
               f'&IF(AS{r}<{ma},"aderência à entrega (validar com o João); ","")&IF(AM{r}<7,"demonstrações de 2 anos; ","")'
               f'&IF(AJ{r}<8,"finalidade com números; ","")&IF(AC{r}<{cq},"pontuação abaixo do corte de "&{cq}&"; ","")')
        ws.cell(r, 32, f'=IF($A{r}="","",IF(Q{r}="Elimina","Eliminatório: "&{ko_txt},IF(Q{r}<>"Passa","faltam "&(10-COUNTA(G{r}:P{r}))&" eliminatórios",'
                       f'IF(AD{r}<11,"faltam "&(11-AD{r})&" critérios",IF(AE{r}="Qualificado","",{lac})))))')
        ws.cell(r, 33, f'=IF($A{r}="","",IF(AE{r}="Qualificado","Camada 3: NDA e checklist documental; agendar o especialista (João)",'
                       f'IF(AE{r}="Em desenvolvimento","Nutrir: retomar em 60 a 90 dias com o que falta (coluna Lacunas)",'
                       f'IF(AE{r}="Não qualificado","Encerrar com o roteiro de saída (17-qualificacao, seção 9) e oferecer outro produto da Save",'
                       f'IF(AE{r}="Incompleto: camada 2","Agendar a reunião de 30 min (camada 2)","Fazer a ligação de 10 min (camada 1)")))))')
        for j in (17, 29, 30, 31, 32, 33): ws.cell(r, j).alignment = WRAP; ws.cell(r, j).border = THIN
    rng = f"AE{L0}:AE{last}"
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Qualificado"'], fill=F_OK))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Em desenvolvimento"'], fill=F_WARN))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Não qualificado"'], fill=F_BAD))
    ws.conditional_formatting.add(f"Q{L0}:Q{last}", CellIsRule(operator="equal", formula=['"Elimina"'], fill=F_BAD))
    ws.conditional_formatting.add(f"G{L0}:P{last}", CellIsRule(operator="equal", formula=['"NÃO"'], fill=F_BAD))
    larg = [38, 20, 18, 18, 12, 14] + [13] * 10 + [12] + [26] * 11 + [11, 11, 18, 40, 40, 30] + [7] * 11
    for i, w in enumerate(larg, 1): ws.column_dimensions[CL(i)].width = w
    for i in range(35, 46): ws.column_dimensions[CL(i)].outlineLevel = 1
    ws.freeze_panes = "B5"; ws.auto_filter.ref = f"A4:AH{last}"


STATUS_COLS = [("sit", "Situação cadastral (K6)"), ("rj", "Recuperação judicial (K7)"), ("doc", "2 anos de demonstrações (K3)"),
               ("fat", "Porte / faturamento (K8 e critério 1)"), ("nec", "Necessidade ≥ US$ 5 mi e finalidade (K1, K9)"),
               ("gar", "Garantia ≈ 2x (K2)"), ("moeda", "Moeda estrangeira e etapas (K4, K10)"), ("prazo", "Prazo ≥ 3 meses (K5)"),
               ("exp", "Hedge natural (critério 6)"), ("ader", "Aderência à entrega (critério 11)")]


def base(wb, linhas, meta):
    ws = wb.create_sheet("Base pré-qualificada", 2)
    ws["A1"] = "Base pré-qualificada pelos dados · Crédito internacional"; ws["A1"].font = TITLE
    ws["A2"] = (f"1 linha por empresa (raiz do CNPJ) da base priorizada de 02/10. Fontes: HubSpot {meta['hubspot_em']} ({meta['hubspot']}); "
                f"{meta['receita']}; pareceres (Faturamento-Clientes-Ganhos e Lookalike-Perdidos). Status por critério: CONFIRMADO (atende, elimina ou parcial) "
                "= documento ou cadastro oficial; ESTIMADO = proxy ou sinal (não qualifica sozinho); DESCONHECIDO = só a conversa responde. USO INTERNO: "
                "o cliente é do Master; não enviar a terceiros.")
    ws["A2"].alignment = WRAP; ws.merge_cells("A2:L2"); ws.row_dimensions[2].height = 60
    ws["M3"] = "Status por critério"; ws["W3"] = "Evidência por critério"
    for c in ("M3", "W3"): ws[c].font = BOLD; ws[c].fill = F_SUB
    cols = ["Resultado", "Motivo / o que falta", "Prioridade para a camada 1", "Empresa", "CNPJ", "UF", "Cidade", "Setor", "Parceiro",
            "Status no HubSpot (05/10)", "Último negócio", "Faixa da base (02/10)"] + [n for _, n in STATUS_COLS] + [f"Evidência: {n}" for _, n in STATUS_COLS] \
        + ["Sinais de atenção", "Nº CONFIRMADO", "Nº ESTIMADO", "Nº DESCONHECIDO", "Porte (Receita)", "Capital social (R$)", "Link do HubSpot"]
    cab(ws, 4, cols, 60)
    ordem = {"Pré-qualificada pelos dados": 0, "Depende da camada 1": 1, "Descartada por eliminatório já conhecido": 2}
    op = {"Camada 1 já": 0, "Alta": 1, "Média": 2, "Baixa": 3, "—": 4}
    linhas = sorted(linhas, key=lambda l: (ordem[l["resultado"]], op[l["prior"]], -(l["score_base"] or 0)))
    for i, l in enumerate(linhas):
        r = L0 + i
        vals = [l["resultado"], l["motivo"], l["prior"], l["empresa"], l["cnpj"], l["uf"], l["cidade"], l["setor"], l["parceiro"],
                l["status_hs"], l["ultimo"], l["faixa_base"]] + [l[k][0] for k, _ in STATUS_COLS] + [l[k][1] for k, _ in STATUS_COLS] + [l["sinais"]]
        for j, v in enumerate(vals, 1): ws.cell(r, j, v)
        ws.cell(r, 33, f'=COUNTIF(M{r}:V{r},"CONFIRMADO*")'); ws.cell(r, 34, f'=COUNTIF(M{r}:V{r},"ESTIMADO")'); ws.cell(r, 35, f'=COUNTIF(M{r}:V{r},"DESCONHECIDO")')
        ws.cell(r, 36, l["porte_rf"]); ws.cell(r, 37, l["capital"]).number_format = "#,##0"
        if l["link"]:
            c = ws.cell(r, 38, "abrir no HubSpot"); c.hyperlink = l["link"]; c.font = Font(color="0563C1", underline="single")
    last = L0 + len(linhas) - 1
    s = f"M{L0}:V{last}"
    ws.conditional_formatting.add(s, FormulaRule(formula=[f'LEFT(M{L0},20)="CONFIRMADO: elimina"'], fill=F_BAD))
    ws.conditional_formatting.add(s, FormulaRule(formula=[f'LEFT(M{L0},19)="CONFIRMADO: atende"'], fill=F_OK))
    ws.conditional_formatting.add(s, FormulaRule(formula=[f'LEFT(M{L0},19)="CONFIRMADO: parcial"'], fill=F_WARN))
    ws.conditional_formatting.add(s, CellIsRule(operator="equal", formula=['"ESTIMADO"'], fill=PatternFill("solid", fgColor="FCE4D6")))
    ws.conditional_formatting.add(s, CellIsRule(operator="equal", formula=['"DESCONHECIDO"'], fill=F_GREY))
    a = f"A{L0}:A{last}"
    ws.conditional_formatting.add(a, CellIsRule(operator="equal", formula=['"Pré-qualificada pelos dados"'], fill=F_OK))
    ws.conditional_formatting.add(a, CellIsRule(operator="equal", formula=['"Descartada por eliminatório já conhecido"'], fill=F_BAD))
    larg = [24, 50, 12, 38, 20, 5, 16, 22, 16, 11, 11, 8] + [14] * 10 + [40] * 10 + [40, 9, 9, 9, 12, 14, 16]
    for i, w in enumerate(larg, 1): ws.column_dimensions[CL(i)].width = w
    for col in range(1, 39):
        for r in range(L0, last + 1): ws.cell(r, col).alignment = Alignment(vertical="top", wrap_text=col in (2, 33) or 23 <= col <= 32)
    ws.freeze_panes = "E5"; ws.auto_filter.ref = f"A4:{CL(38)}{last}"
    return len(linhas)


def resumo(wb, n):
    ws = wb.create_sheet("Resumo da base", 3)
    B = "'Base pré-qualificada'"; a, c = f"{B}!$A${L0}:$A${L0+n-1}", f"{B}!$C${L0}:$C${L0+n-1}"
    bcol = lambda col: f"{B}!${col}${L0}:${col}${L0+n-1}"
    ws["A1"] = "Resumo da base e funil realista"; ws["A1"].font = TITLE
    ws["A3"] = "Resultado da pré-qualificação pelos dados"; ws["A3"].font = BOLD
    cab_r = lambda r, cols: [setattr(ws.cell(r, i + 1, t), "font", HFONT) or setattr(ws.cell(r, i + 1), "fill", F_HEAD) for i, t in enumerate(cols)]
    cab_r(4, ["Resultado", "Empresas", "% da base"])
    res = ["Pré-qualificada pelos dados", "Depende da camada 1", "Descartada por eliminatório já conhecido"]
    for i, t in enumerate(res):
        r = 5 + i; ws.cell(r, 1, t); ws.cell(r, 2, f'=COUNTIF({a},A{r})'); ws.cell(r, 3, f"=B{r}/B$8").number_format = "0.0%"
    ws.cell(8, 1, "Total").font = BOLD; ws.cell(8, 2, "=SUM(B5:B7)").font = BOLD; ws.cell(8, 3, f"=B8/COUNTA({bcol('D')})").number_format = "0.0%"
    ws["E3"] = "Depende da camada 1, por prioridade"; ws["E3"].font = BOLD
    for i, t in enumerate(["Prioridade", "Empresas"]): ws.cell(4, 5 + i, t).font = HFONT; ws.cell(4, 5 + i).fill = F_HEAD
    for i, p in enumerate(["Alta", "Média", "Baixa"]):
        ws.cell(5 + i, 5, p); ws.cell(5 + i, 6, f'=COUNTIFS({a},"Depende da camada 1",{c},E{5+i})')
    ws.cell(8, 5, "Total").font = BOLD; ws.cell(8, 6, "=SUM(F5:F7)").font = BOLD

    ws["A10"] = "Descartadas: motivos (uma empresa pode ter mais de um)"; ws["A10"].font = BOLD
    cab_r(11, ["Motivo (texto procurado na coluna Motivo)", "Empresas"])
    mot = [("situação cadastral não ativa", "*situação cadastral*"), ("menos de 2 anos de demonstrações (aberta em 2024 ou depois)", "*menos de 2 anos*"),
           ("Simples Nacional/MEI (receita até R$ 4,8 mi)", "*Simples Nacional/MEI*"), ("faturamento comprovado abaixo de R$ 30 mi", "*faturamento comprovado*"),
           ("recuperação judicial/falência no nome", "*recuperação judicial/falência*")]
    for i, (t, pat) in enumerate(mot):
        r = 12 + i; ws.cell(r, 1, t); ws.cell(r, 2, f'=COUNTIFS({a},"Descartada*",{bcol("B")},"{pat}")')

    ws["A18"] = "Status por critério (quantas empresas em cada status)"; ws["A18"].font = BOLD
    st = ["CONFIRMADO: atende", "CONFIRMADO: parcial", "CONFIRMADO: elimina", "ESTIMADO", "DESCONHECIDO"]
    cab_r(19, ["Critério"] + st)
    for i, (k, nome) in enumerate(STATUS_COLS):
        r = 20 + i; ws.cell(r, 1, nome); col = CL(13 + i)
        for j, s in enumerate(st): ws.cell(r, 2 + j, f'=COUNTIF({bcol(col)},"{s}")')

    ws["A31"] = "Faixa da base de 02/10 × resultado de hoje"; ws["A31"].font = BOLD
    cab_r(32, ["Faixa da base"] + res + ["Total"])
    for i, fx in enumerate(["A", "B", "C"]):
        r = 33 + i; ws.cell(r, 1, fx)
        for j, t in enumerate(res): ws.cell(r, 2 + j, f'=COUNTIFS({bcol("L")},$A{r},{a},"{t}")')
        ws.cell(r, 5, f"=SUM(B{r}:D{r})")

    ws["A38"] = "Funil realista (hipóteses em amarelo: edite e o funil recalcula)"; ws["A38"].font = BOLD
    cab_r(39, ["Grupo", "Empresas", "% com conversa (Master consegue a ligação)", "% que passa nos eliminatórios da camada 1",
               "Passam na camada 1 (esperado)", "% qualificada na camada 2", "Qualificadas (esperado)"])
    ws.row_dimensions[39].height = 45
    grupos = [("Pré-qualificadas pelos dados", "=B5", 0.70, 0.40), ("Camada 1 · prioridade Alta", "=F5", 0.70, 0.15),
              ("Camada 1 · prioridade Média", "=F6", 0.50, 0.05), ("Camada 1 · prioridade Baixa (não ligar sem sinal novo)", "=F7", 0.0, 0.01)]
    for i, (g, f, pc, pk) in enumerate(grupos):
        r = 40 + i; ws.cell(r, 1, g); ws.cell(r, 2, f)
        for col, v in ((3, pc), (4, pk), (6, 0.5)):
            x = ws.cell(r, col, v); x.fill = F_IN; x.number_format = "0%"
        ws.cell(r, 5, f"=B{r}*C{r}*D{r}").number_format = "0.0"; ws.cell(r, 7, f"=E{r}*F{r}").number_format = "0.0"
    ws.cell(44, 1, "Total").font = BOLD
    for col in (2, 5, 7): ws.cell(44, col, f"=SUM({CL(col)}40:{CL(col)}43)").number_format = "0.0"
    ws["A46"] = "Cenários (multiplicam só a taxa de passagem na camada 1)"; ws["A46"].font = BOLD
    cab_r(47, ["Cenário", "Fator", "Passam na camada 1", "Qualificadas"])
    for i, (nome, fat) in enumerate([("Conservador", 0.5), ("Base", 1.0), ("Otimista", 1.5)]):
        r = 48 + i; ws.cell(r, 1, nome); x = ws.cell(r, 2, fat); x.fill = F_IN
        ws.cell(r, 3, f"=SUMPRODUCT($B$40:$B$43,$C$40:$C$43,$D$40:$D$43)*B{r}").number_format = "0.0"
        ws.cell(r, 4, f"=SUMPRODUCT($B$40:$B$43,$C$40:$C$43,$D$40:$D$43,$F$40:$F$43)*B{r}").number_format = "0.0"
    ws["A52"] = ("Leitura: 'pré-qualificada pelos dados' NÃO é qualificada. Os dados só confirmam cadastro, idade e faturamento; necessidade, "
                 "garantia, moeda e prazo só a conversa confirma. Estimativa por proxy nunca qualifica sozinha.")
    ws["A52"].alignment = WRAP; ws.merge_cells("A52:G53"); ws.row_dimensions[52].height = 40
    for i, w in enumerate([52, 14, 18, 20, 16, 16, 16], 1): ws.column_dimensions[CL(i)].width = w


def texto(wb, nome, pos, linhas, larg=(34, 110)):
    ws = wb.create_sheet(nome, pos)
    for i, (a, b) in enumerate(linhas, 1):
        ws.cell(i, 1, a); ws.cell(i, 2, b); ws.cell(i, 2).alignment = WRAP; ws.cell(i, 1).alignment = WRAP
        if a and not b: ws.cell(i, 1).font = TITLE if i == 1 else BOLD
        elif a: ws.cell(i, 1).font = BOLD
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = larg


COMO_USAR = [
    ("Como usar · Scorecard de qualificação do crédito internacional", None), ("", ""),
    ("Para que serve", "Trocar volume de indicações por volume de clientes QUALIFICADOS. Cada cliente passa por 3 camadas e só chega ao especialista (João) quem passou nos eliminatórios e pontuou."),
    ("Camada 1 (10 min)", "Ligação do parceiro ou do comercial com 5 perguntas (17-qualificacao.md, seção 5). Marque os 10 eliminatórios (K1 a K10) com SIM (atende) ou NÃO (elimina). Um NÃO encerra: a coluna Faixa mostra 'Não qualificado' e o próximo passo é o roteiro de saída."),
    ("Camada 2 (30 min)", "Reunião com a Save, cerca de 12 perguntas. Escolha nos menus amarelos as respostas dos 11 critérios. A pontuação (0 a 100) e a faixa saem sozinhas."),
    ("Camada 3", "Pré-análise documental com o checklist (17-qualificacao.md, seção 7). Só para quem saiu 'Qualificado'. NDA antes dos documentos detalhados."),
    ("Faixas", "Qualificado: ≥ 70 pontos E porte ≥ 10, garantias ≥ 11 e aderência ≥ 8 (mínimos na aba Tabelas) → segue para o especialista. Em desenvolvimento: 50 a 69, ou ≥ 70 sem os mínimos → nutrir com o que falta. Não qualificado: algum eliminatório NÃO ou menos de 50 pontos."),
    ("Colunas automáticas", "Eliminatórios · Pontuação · Critérios respondidos · Faixa · Lacunas / motivo · Próximo passo. Não digite nelas. Os pontos por critério ficam agrupados no fim (AI:AS)."),
    ("Linhas já preenchidas", "As 3 primeiras são exemplos fictícios (cinza). Depois vêm as empresas pré-qualificadas pelos dados e as de prioridade Alta da aba Base pré-qualificada, prontas para a camada 1."),
    ("Base pré-qualificada", "Mostra, para as 1.007 empresas da base, o que os dados JÁ confirmam, o que é estimativa e o que é desconhecido, por critério. Use o filtro em 'Resultado' e 'Prioridade para a camada 1'."),
    ("Resumo da base", "Contagens por resultado, motivos de descarte, status por critério e o funil realista com as hipóteses em amarelo (edite para simular)."),
    ("Regras", "Uso interno. O cliente é do parceiro Master: a abordagem passa por ele. Não prometer taxa, prazo nem aprovação (D30: sem conversa sobre condições até o portão jurídico G2). Nada desta planilha vai para o HubSpot sem aprovação do Luis (D37)."),
    ("Como atualizar", "python3 ~/agentes-partners/departamentos/produtos/credito-internacional/scripts/qualificacao_planilha.py (relê HubSpot, Receita e pareceres e regrava as duas cópias). Atenção: regravar apaga o que foi digitado no Scorecard; copie as linhas antes."),
]


def metodologia(meta):
    m = [("Metodologia", None), ("", ""),
         ("Gerado em", f"{meta['gerado']} · Intel Comercial, Dados e Partner Success (rascunho para o Luis)"),
         ("Referência do produto", "15-documento-oficial.md v2.1 (06/10/2026), dono do produto João Mattos. Pendências da seção 14 não entram como regra."),
         ("Fontes", f"Credito-Internacional-Base-Priorizada.xlsx (1.007 empresas, 02/10); Faturamento-Clientes-Ganhos.xlsx e Lookalike-Perdidos.xlsx (pareceres); "
                    f"HubSpot local {meta['hubspot']} ({meta['hubspot_em']}); {meta['receita']} via partners_dados.receita(). Tudo local, nenhum CNPJ saiu da máquina."),
         ("Universo", "As 1.007 empresas (raiz do CNPJ) da base priorizada: ganhos e abertos de 02/10. Filial é lida pela matriz (idade e porte)."),
         ("", ""), ("O que os dados confirmam", None),
         ("Situação cadastral (K6)", "Receita: Ativa = atende; Baixada, Inapta, Suspensa ou Nula = elimina. Não encontrada = desconhecido."),
         ("Recuperação judicial (K7)", "Elimina se a razão social na Receita traz 'em recuperação judicial', 'falida' ou 'em liquidação'. A ausência NÃO comprova: pergunta na camada 1 e certidão na camada 3."),
         ("2 anos de demonstrações (K3)", "Elimina se a empresa (matriz) abriu depois de 01/01/2024: não tem 2024 e 2025 completos. Antes disso, a idade é condição necessária, não prova: o documento é desconhecido. Reabre se o tomador for outra empresa do grupo com 2 anos."),
         ("Faturamento (K8 e critério 1)", "CONFIRMADO só com parecer técnico (documento lido pela Save), confiança alta ou média, ano 2023 ou depois, sem leitura ambígua. ≥ R$ 50 mi atende; R$ 30–50 mi parcial (exceção só com o João); < R$ 30 mi elimina. Optante do Simples/MEI na Receita elimina (limite legal de R$ 4,8 mi). Proxy pelo crédito recuperado, HubSpot preenchido à mão e parecer antigo ou ambíguo = ESTIMADO."),
         ("Hedge natural", "Parecer técnico que cita exportação = confirmado (percentual desconhecido). Razão social ou CNAE de cadeia exportadora = estimado."),
         ("Aderência à entrega", "Sempre ESTIMADO pelo setor: alta para café, agro, construtora, frigorífico, usina e hortifruti (parecidos com os casos em teste); média para indústria de alimentos, máquinas, carnes no atacado e combustíveis; baixa para varejo, atacado, transporte e outros."),
         ("Sempre desconhecido", "Necessidade ≥ US$ 5 mi e finalidade, garantia ≈ 2x, aceite de moeda estrangeira e de etapas, prazo, governança, histórico do empresário e custo da dívida: nenhuma base tem esses dados."),
         ("", ""), ("Classificação", None),
         ("Descartada por eliminatório já conhecido", "Algum critério CONFIRMADO: elimina."),
         ("Pré-qualificada pelos dados", "Nenhum eliminatório conhecido E situação Ativa E faturamento CONFIRMADO ≥ R$ 50 mi. Ainda falta a camada 1 inteira: não é cliente qualificado."),
         ("Depende da camada 1", "O resto. Prioridade Alta: faturamento confirmado de R$ 30–50 mi, ou estimado ≥ R$ 50 mi com setor de aderência alta/média e porte Demais, ou faixa A da base. Média: estimado ≥ R$ 30 mi, faixa B, porte Demais em setor de aderência alta ou capital ≥ R$ 1 mi. Baixa: os demais (não ligar sem sinal novo)."),
         ("Rigor", "Estimativa por proxy NÃO qualifica sozinha e também NÃO elimina sozinha (o porte da Receita é declaratório e costuma estar desatualizado; há cliente 'ME' na Receita com R$ 60 mi de faturamento no parecer)."),
         ("", ""), ("Scorecard", None),
         ("Pesos (100)", " · ".join(f"{c[1]} {c[2]}" for c in CRIT)),
         ("Fórmulas", "Pontos = VLOOKUP da resposta na aba Tabelas; Pontuação = soma; Faixa = eliminatórios → respondidos → cortes e mínimos da aba Tabelas. Conferidas por recálculo em Python (scripts/conferir_planilha.py)."),
         ("Hipóteses a validar com o João", "Piso de R$ 30 mi como eliminatório (o critério oficial é 'cerca de R$ 50 mi'); garantia mínima de 1,5x para não eliminar (referência oficial: cerca de 2x); cortes 70/50 e mínimos por critério; taxas do funil."),
         ("Limites", f"{meta['sem_receita']} CNPJs sem cadastro na base local da Receita. Faturamento de parecer é de 2023/2024: o de 2025 pode ser maior (reabre com DRE nova). A Receita é de 2026-09."),
         ("LGPD e canal", "Uso interno, sem sócios nem CPF. O cliente é do Master: abordagem pelo Master. Não enviar a terceiros nem ao fundo."),
         ]
    return m


def main():
    linhas, meta = montar()
    mapa = {"Café": "Café/agro", "Agro, produtores e insumos agropecuários": "Café/agro", "Usinas (açúcar/etanol)": "Café/agro",
            "Frigoríficos (abate/indústria de carnes)": "Frigorífico/alimentos", "Indústria de alimentos e bebidas": "Frigorífico/alimentos",
            "Carnes · atacado": "Frigorífico/alimentos", "Construtoras e incorporadoras": "Construtora", "Máquinas e equipamentos": "Indústria exportadora",
            "Atacado de alimentos e mercadorias": "Hortifruti/atacado"}
    for l in linhas: l["setor_sc"] = "Hortifruti/atacado" if "HORTIFRUTI" in (l["empresa"] or "").upper() else mapa.get(l["setor"], "Outro")
    fila = sorted([l for l in linhas if l["prior"] in ("Camada 1 já", "Alta")], key=lambda l: (l["prior"] != "Camada 1 já", -(l["score_base"] or 0)))
    wb = Workbook(); wb.remove(wb.active)
    texto(wb, "Como usar", 0, COMO_USAR)
    ref = tabelas(wb)
    scorecard(wb, ref, fila)
    n = base(wb, linhas, meta)
    resumo(wb, n)
    texto(wb, "Metodologia", 4, metodologia(meta))
    local = os.path.join(PASTA, NOME)
    wb.save(local)
    area = subprocess.run(["python3", os.path.expanduser("~/agentes-partners/lib/caminhos.py"), "area"], capture_output=True, text=True).stdout.strip()
    destino = os.path.join(area, "Gestão · Luis", "Produtos")
    os.makedirs(destino, exist_ok=True); shutil.copy2(local, os.path.join(destino, NOME))
    agreg = dict(meta=meta, resultado=collections.Counter(l["resultado"] for l in linhas),
                 prioridade=collections.Counter(l["prior"] for l in linhas if l["resultado"] == "Depende da camada 1"),
                 fila_scorecard=len(fila))
    json.dump(agreg, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "qualificacao-agregados.json"), "w"), ensure_ascii=False, indent=1)
    print(local); print(os.path.join(destino, NOME)); print(json.dumps(agreg, ensure_ascii=False))


if __name__ == "__main__":
    main()
