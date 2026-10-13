#!/usr/bin/env python3
"""Simulador interno Brasil × Paraguai do Projeto Maquila (Resultados & Controladoria).

Até 09/10/2026 se chamava "Dinheiro na Mesa" (renomeado pela correção C21 da ata do Conselho de 05/10/2026).
Gera Maquila-Simulador-Interno-Brasil-x-Paraguai.xlsx com fórmulas vivas do Excel e confere:
  1. recalcula tudo em Python, de forma independente das fórmulas;
  2. avalia as fórmulas com scripts/avaliador_formulas.py;
  3. compara os dois e compara a indústria-tipo com o estudo 01 (seção 4.7).
Só lê a base priorizada; não envia nada.

Uso: python3 calculadora_maquila.py
"""
import os
import sys

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.dirname(AQUI)
SAIDA = os.path.join(PASTA, "Maquila-Simulador-Interno-Brasil-x-Paraguai.xlsx")
BASE = os.path.join(PASTA, "Maquila-Base-Priorizada.xlsx")
sys.path.insert(0, AQUI)
from avaliador_formulas import avaliar_tudo  # noqa: E402

AMARELO = PatternFill("solid", fgColor="FFF2CC")
CINZA = PatternFill("solid", fgColor="F2F2F2")
AZUL = PatternFill("solid", fgColor="1F3864")
DOURADO = PatternFill("solid", fgColor="FCE4D6")
VERDE = PatternFill("solid", fgColor="E2EFDA")
BRANCO_B = Font(bold=True, color="FFFFFF")
NEG = Font(bold=True)
TIT = Font(bold=True, size=14)
AVISO = Font(bold=True, color="C00000")
FINO = Side(style="thin", color="BFBFBF")
BORDA = Border(left=FINO, right=FINO, top=FINO, bottom=FINO)
WRAP = Alignment(wrap_text=True, vertical="top")
RS = '#,##0;[Red]-#,##0'
MI = '0.00;[Red]-0.00'
PCT = '0.0%;[Red]-0.0%'
PCT2 = '0.00%;[Red]-0.00%'

E = "Estudo 01, seção 4.7 (indústria-tipo) [HIPÓTESE]"

# ---------------------------------------------------------------- entradas (indústria-tipo do estudo 01)
# chave: (linha, rótulo, valor, unidade, formato, fonte)
ENTRADAS = [
    ("fat", "Faturamento bruto", 50_000_000, "R$/ano", RS, E),
    ("rl", "Receita líquida (depois de ICMS, PIS/COFINS, IPI; igual nos dois cenários)", 40_000_000, "R$/ano", RS,
     E + "; neutralidade da seção 2.2 [VALIDAR TRIBUTÁRIO]"),
    ("margem", "Margem operacional atual (lucro operacional ÷ faturamento)", 0.10, "% do faturamento", PCT,
     "Estudo 01, 4.7: lucro operacional de R$ 5,00 mi = 10% do faturamento"),
    ("folha", "Folha-base anual (salários-base, sem encargos)", 6_000_000, "R$/ano", RS,
     E + ": R$ 6 mi nos dois cenários (paridade)"),
    ("enc_br", "Encargos e provisões no Brasil (sobre o salário-base)", 0.70, "%", PCT,
     "Estudo 01, 4.2: 65–80% [ESTIMATIVA]; 4.7 usa 1,70"),
    ("enc_py", "Encargos e provisões no Paraguai (sobre o salário-base)", 0.28, "%", PCT,
     "Estudo 01, 4.2: 25–30% [ESTIMATIVA]; 4.7 usa 1,28"),
    ("rel_sal", "Salário no Paraguai ÷ salário no Brasil (mesma função)", 1.00, "relação", PCT,
     E + ": paridade. O mínimo PY é ~68% maior em US$ (4.3)"),
    ("mwh", "Consumo de energia", 4_000, "MWh/ano", '#,##0', E),
    ("tar_br", "Tarifa de energia no Brasil", 543.90, "R$/MWh", '#,##0.00',
     "FIRJAN via CanalEnergia (estudo 01, 4.4; data da medição a confirmar)"),
    ("tar_py", "Tarifa de energia no Paraguai", 49.5, "US$/MWh", '#,##0.00',
     "Tarifa média ANDE 2024, ABC Color 06/08/2026 (estudo 01, 4.4)"),
    ("area", "Área do galpão", 8_000, "m²", '#,##0', E),
    ("gal_br", "Custo do galpão no Brasil", 31.49, "R$/m²/mês", '#,##0.00', "SiiLA SP via Itaú BBA, 4T25 (20/02/2026)"),
    ("gal_py", "Custo do galpão no Paraguai", 4.50, "US$/m²/mês", '#,##0.00',
     "MIC, catálogo de parques (US$ 3,00–5,50; ponto médio, supondo mensal)"),
    ("log_br", "Logística atual no Brasil (entregas regionais)", 600_000, "R$/ano", RS, E),
    ("frete", "Frete adicional Brasil–Paraguai (R$/ano)", 2_390_000, "R$/ano", RS,
     "Estudo 01, 4.7: 350 viagens × R$ 7.400 + R$ 0,4 mi de despacho e fronteira = R$ 2,99 mi, menos R$ 0,6 mi da logística atual"),
    ("frete_pct", "Frete adicional (% do faturamento): usado só se a linha acima estiver vazia", None, "% do faturamento",
     PCT2, "Alternativa. Na indústria-tipo, R$ 2,39 mi ÷ R$ 50 mi = 4,78%"),
    ("estrut", "Estrutura no exterior (contabilidade, jurídico, preços de transferência, viagens)", 500_000, "R$/ano", RS,
     E + ": R$ 0,5 mi, já dentro dos R$ 3,5 mi de outros fixos"),
    ("pct_py", "% da produção levada ao Paraguai", 1.00, "%", PCT, E + ": produção toda no PY (100%)"),
    ("pct_fat", "Fatura de exportação (% da receita líquida da parte produzida no PY)", 1.00, "%", PCT,
     "Estudo 01, 4.7: base cheia de R$ 40 mi (cenário conservador da regra 'o que for maior')"),
    ("capex", "Investimento inicial (capex): máquinas, adequação, giro", None, "R$", RS,
     "PENDENTE: o estudo 01 não traz capex da indústria-tipo. Informe o do caso"),
    ("cambio", "Câmbio", 5.2238, "R$/US$", '0.0000', "PTAX/BCB de 02/10/2026"),
]
PARAMS = [
    ("trib", "Tributo único de maquila", 0.01, "% da base", PCT, "Lei 7.547/2025, art. 37 (base: o maior entre valor agregado e fatura)"),
    ("irpj", "IRPJ", 0.15, "% do lucro", PCT, "Lei 9.249/1995, art. 3º"),
    ("adic", "Adicional de IRPJ", 0.10, "% do lucro acima do limite", PCT, "Lei 9.249/1995, art. 3º, §1º"),
    ("lim", "Limite anual do adicional", 240_000, "R$/ano", RS, "Lei 9.249/1995, art. 3º, §1º"),
    ("csll", "CSLL", 0.09, "% do lucro", PCT, "Lei 7.689/1988"),
]


def num_fmt(c, f):
    c.number_format = f


def cab(ws, linha, textos, larg=None):
    for i, t in enumerate(textos, 1):
        c = ws.cell(linha, i, t)
        c.fill, c.font, c.alignment, c.border = AZUL, BRANCO_B, Alignment(wrap_text=True, vertical="center"), BORDA


def larguras(ws, ls):
    for i, l in enumerate(ls, 1):
        ws.column_dimensions[get_column_letter(i)].width = l


def construir():
    wb = openpyxl.Workbook()
    R = {}  # chave -> referência absoluta no Simulador

    # ============================================================ Simulador
    ws = wb.active
    ws.title = "Simulador"
    ws["A1"] = "Maquila · Simulador interno Brasil × Paraguai (faixa, não promessa) · USO INTERNO: NÃO SAI DA SAVE"
    ws["A1"].font = TIT
    ws["A2"] = ("Ilustrativo. Valores iniciais = indústria-tipo do estudo 01 (seção 4.7). Não é promessa de economia; "
                "cada caso exige estudo próprio. Células amarelas são editáveis; o resto é fórmula.")
    ws["A2"].font = AVISO
    cab(ws, 4, ["Entrada", "Valor", "Unidade", "Fonte e data"])
    lin = 5
    for chave, rot, val, uni, f, fonte in ENTRADAS:
        ws.cell(lin, 1, rot)
        c = ws.cell(lin, 2, val)
        c.fill, c.border = AMARELO, BORDA
        num_fmt(c, f)
        ws.cell(lin, 3, uni)
        ws.cell(lin, 4, fonte).alignment = WRAP
        R[chave] = f"$B${lin}"
        lin += 1
    lin += 1
    ws.cell(lin, 1, "Parâmetros legais (mude só se a lei mudar)").font = NEG
    lin += 1
    for chave, rot, val, uni, f, fonte in PARAMS:
        ws.cell(lin, 1, rot)
        c = ws.cell(lin, 2, val)
        c.fill, c.border = AMARELO, BORDA
        num_fmt(c, f)
        ws.cell(lin, 3, uni)
        ws.cell(lin, 4, fonte).alignment = WRAP
        R[chave] = f"$B${lin}"
        lin += 1

    # --- cálculos auxiliares
    lin += 1
    ws.cell(lin, 1, "Cálculos auxiliares (parte levada ao Paraguai)").font = NEG
    lin += 1
    aux = [
        ("frete_ef", "Frete adicional efetivo (100% da produção)",
         f"=IF(ISNUMBER({R['frete']}),{R['frete']},IF(ISNUMBER({R['frete_pct']}),{R['frete_pct']}*{R['fat']},0))"),
        ("folha_py", "Folha da parte no Paraguai (salário + encargos)",
         f"={R['folha']}*{R['pct_py']}*{R['rel_sal']}*(1+{R['enc_py']})"),
        ("ener_py", "Energia da parte no Paraguai",
         f"={R['mwh']}*{R['pct_py']}*{R['tar_py']}*{R['cambio']}"),
        ("gal_py_rs", "Galpão da parte no Paraguai",
         f"={R['area']}*{R['pct_py']}*{R['gal_py']}*{R['cambio']}*12"),
        ("estrut_ef", "Estrutura no exterior (só se houver produção no PY)", f"=IF({R['pct_py']}>0,{R['estrut']},0)"),
        ("log_py", "Logística ligada ao Paraguai (base da sensibilidade de logística)", None),
        ("va", "Valor agregado no Paraguai (folha + energia + galpão + estrutura)", None),
        ("fatura", "Fatura de exportação", f"={R['rl']}*{R['pct_py']}*{R['pct_fat']}"),
        ("base_trib", "Base do tributo único (o maior entre valor agregado e fatura)", None),
    ]
    for chave, rot, f in aux:
        R[chave] = f"$B${lin}"
        lin += 1
    # fórmulas que dependem de outras auxiliares
    fx = {
        "log_py": f"=({R['log_br']}+{R['frete_ef']})*{R['pct_py']}",
        "va": f"={R['folha_py']}+{R['ener_py']}+{R['gal_py_rs']}+{R['estrut_ef']}",
        "base_trib": f"=MAX({R['va']},{R['fatura']})",
    }
    for chave, rot, f in aux:
        r = int(R[chave].split("$")[-1])
        ws.cell(r, 1, rot)
        c = ws.cell(r, 2, f or fx[chave])
        c.fill, c.number_format = CINZA, RS
        ws.cell(r, 3, "R$/ano")

    # --- tabela de resultado
    lin += 1
    ws.cell(lin, 1, "Resultado anual").font = TIT
    lin += 1
    cab(ws, lin, ["Linha", "Brasil (antes) R$", "Com maquila PY (depois) R$", "Diferença R$",
                  "Antes R$ mi", "Depois R$ mi", "Estudo antes R$ mi", "Estudo depois R$ mi", "Dif. antes", "Dif. depois"])
    lin += 1
    t0 = lin
    linhas = ["rl", "folha_l", "ener_l", "gal_l", "log_l", "estr_l", "trib_l", "demais", "lop", "mg", "ir", "ll"]
    L = {k: t0 + i for i, k in enumerate(linhas)}
    p = R["pct_py"]
    B, C = {}, {}
    B["rl"], C["rl"] = f"={R['rl']}", f"={R['rl']}"
    B["folha_l"] = f"={R['folha']}*(1+{R['enc_br']})"
    C["folha_l"] = f"={R['folha']}*(1-{p})*(1+{R['enc_br']})+{R['folha_py']}"
    B["ener_l"] = f"={R['mwh']}*{R['tar_br']}"
    C["ener_l"] = f"={R['mwh']}*(1-{p})*{R['tar_br']}+{R['ener_py']}"
    B["gal_l"] = f"={R['area']}*{R['gal_br']}*12"
    C["gal_l"] = f"={R['area']}*(1-{p})*{R['gal_br']}*12+{R['gal_py_rs']}"
    B["log_l"] = f"={R['log_br']}"
    C["log_l"] = f"={R['log_br']}+{R['frete_ef']}*{p}"
    B["estr_l"], C["estr_l"] = "=0", f"={R['estrut_ef']}"
    B["trib_l"], C["trib_l"] = "=0", f"={R['trib']}*{R['base_trib']}"
    B["lop"] = f"={R['margem']}*{R['fat']}"
    B["demais"] = f"=B{L['rl']}-B{L['lop']}-SUM(B{L['folha_l']}:B{L['trib_l']})"
    C["demais"] = f"=B{L['demais']}"
    C["lop"] = f"=C{L['rl']}-SUM(C{L['folha_l']}:C{L['demais']})"
    for col, D in (("B", B), ("C", C)):
        D["mg"] = f"=IF({R['fat']}<>0,{col}{L['lop']}/{R['fat']},0)"
        lo = f"{col}{L['lop']}"
        D["ir"] = f"={R['irpj']}*MAX(0,{lo})+{R['adic']}*MAX(0,{lo}-{R['lim']})+{R['csll']}*MAX(0,{lo})"
        D["ll"] = f"={lo}-{col}{L['ir']}"
    rot = {
        "rl": "Receita líquida", "folha_l": "Folha (salário + encargos)", "ener_l": "Energia", "gal_l": "Galpão",
        "log_l": "Logística (atual + frete adicional Brasil–Paraguai)", "estr_l": "Estrutura no exterior",
        "trib_l": "Tributo único de maquila (1% sobre o maior entre valor agregado e fatura)",
        "demais": "Demais custos (insumos e outros fixos; resíduo da margem atual, iguais nos dois cenários)",
        "lop": "Lucro operacional", "mg": "Margem operacional (% do faturamento)",
        "ir": "IRPJ/CSLL 34% sobre todo o lucro, inclusive o da controlada no PY (Lei 12.973/2014, art. 77)",
        "ll": "Lucro líquido",
    }
    estudo = {"rl": (40, 40), "folha_l": (10.20, 7.68), "ener_l": (2.18, 1.03), "gal_l": (3.02, 2.26),
              "log_l": (0.60, 2.99), "estr_l": (0, 0.50), "trib_l": (0, 0.40), "demais": (19.00, 19.00),
              "lop": (5.00, 6.14), "ir": (1.68, 2.06), "ll": (3.32, 4.08)}
    for k in linhas:
        r = L[k]
        ws.cell(r, 1, rot[k]).alignment = WRAP
        for col, D in ((2, B), (3, C)):
            c = ws.cell(r, col, D[k])
            c.number_format = PCT if k == "mg" else RS
        if k != "mg":
            ws.cell(r, 4, f"=C{r}-B{r}").number_format = RS
            ws.cell(r, 5, f"=B{r}/1000000").number_format = MI
            ws.cell(r, 6, f"=C{r}/1000000").number_format = MI
        else:
            ws.cell(r, 4, f"=C{r}-B{r}").number_format = PCT
        if k in estudo:
            ws.cell(r, 7, estudo[k][0]).number_format = MI
            ws.cell(r, 8, estudo[k][1]).number_format = MI
            ws.cell(r, 9, f"=E{r}-G{r}").number_format = MI
            ws.cell(r, 10, f"=F{r}-H{r}").number_format = MI
        if k in ("lop", "ll"):
            for cc in range(1, 11):
                ws.cell(r, cc).font = NEG
        for cc in range(1, 11):
            ws.cell(r, cc).border = BORDA
    ws.cell(L["demais"], 7).comment = None
    lin = L["ll"] + 2
    R["ll_antes"], R["ll_depois"] = f"$B${L['ll']}", f"$C${L['ll']}"
    R["lop_depois"], R["trib_depois"] = f"$C${L['lop']}", f"$C${L['trib_l']}"
    R["ll_l"] = L["ll"]

    ws.cell(lin, 1, "Resultado da simulação (faixa, não promessa)").font = TIT
    lin += 1
    kp = [
        ("ganho", "Ganho anual (lucro líquido depois − antes)", f"=C{L['ll']}-B{L['ll']}", RS),
        ("ganho_mi", "Ganho anual em R$ mi (estudo: +0,75; o estudo arredondado dava +0,76)", None, MI),
        ("ganho_pct", "Ganho anual em % do faturamento", None, PCT2),
        ("ganho_ll", "Variação do lucro líquido (estudo: cerca de +23%)", f"=IF(B{L['ll']}<>0,(C{L['ll']}-B{L['ll']})/ABS(B{L['ll']}),0)", PCT),
        ("ganho_usd", "Ganho anual em US$", None, RS),
        ("payback", "Payback do capex (anos)", None, '0.0'),
    ]
    for chave, rot_, f, fm in kp:
        R[chave] = f"$B${lin}"
        lin += 1
    fk = {
        "ganho_mi": f"={R['ganho']}/1000000",
        "ganho_pct": f"=IF({R['fat']}<>0,{R['ganho']}/{R['fat']},0)",
        "ganho_usd": f"=IF({R['cambio']}<>0,{R['ganho']}/{R['cambio']},0)",
        "payback": (f"=IF(ISNUMBER({R['capex']}),IF({R['capex']}>0,IF({R['ganho']}>0,{R['capex']}/{R['ganho']},"
                    f"\"não se paga: ganho ≤ 0\"),\"informe o capex\"),\"informe o capex (PENDENTE)\")"),
    }
    for chave, rot_, f, fm in kp:
        r = int(R[chave].split("$")[-1])
        ws.cell(r, 1, rot_).font = NEG
        c = ws.cell(r, 2, f or fk[chave])
        c.number_format, c.fill, c.font, c.border = fm, VERDE, NEG, BORDA
    lin += 1
    notas = [
        "Leitura: o ganho vem de folha, energia e galpão; a logística consome boa parte dele; o IR não muda (estudo 01, 4.7).",
        "IR: o lucro da controlada no Paraguai entra no lucro real e na CSLL da matriz em 31/12, distribuído ou não "
        "(Lei 12.973/2014, art. 77). O 1% gera pouco ou nenhum crédito (art. 87) [VALIDAR TRIBUTÁRIO]. "
        "Não considera o crédito presumido de até 9% (art. 87, §10), que reduziria o IR em cerca de R$ 0,1 mi.",
        "Lucro operacional 'antes' = margem atual × faturamento. 'Demais custos' é o resíduo e fica igual nos dois cenários. "
        "Com % de produção menor que 100%, folha, energia, galpão, frete e tributo único são proporcionais; a estrutura no exterior é fixa.",
        "Conferência com o estudo: colunas G a J. As diferenças vêm do arredondamento do estudo (2 casas em R$ mi) e de a margem "
        "de 10% dar R$ 5,000 mi, contra R$ 5,001 mi das linhas do estudo.",
    ]
    for n in notas:
        ws.cell(lin, 1, n).alignment = WRAP
        ws.merge_cells(start_row=lin, start_column=1, end_row=lin, end_column=10)
        ws.row_dimensions[lin].height = 32
        lin += 1
    larguras(ws, [62, 18, 20, 16, 11, 11, 12, 12, 10, 10])
    ws.column_dimensions["D"].width = 60
    ws.freeze_panes = "A5"

    # ============================================================ Sensibilidade
    s = wb.create_sheet("Sensibilidade")
    s["A1"] = "Sensibilidade do ganho anual (uma premissa por vez e cenários combinados)"
    s["A1"].font = TIT
    s["A2"] = ("Choques sobre o cenário 'depois' do Simulador: salário no PY (relação PY/BR), logística ligada ao PY "
               "(atual + frete adicional, como no estudo) e tarifa de energia da ANDE. Tudo por fórmula.")
    s["A2"].alignment = WRAP
    s.merge_cells("A2:M2")
    s.row_dimensions[2].height = 30
    cab(s, 4, ["Premissa alterada", "Salário PY", "Logística", "Energia PY", "Custo adicional R$",
               "Tributo único R$", "Lucro operacional R$", "IRPJ/CSLL R$", "Lucro líquido depois R$",
               "Ganho anual R$", "Ganho % do faturamento", "Estudo: lucro líquido depois R$ mi", "Dif. R$ mi"])
    S = "'Simulador'!"
    cen = []
    for v in (-0.10, 0, 0.10, 0.20, 0.30):
        cen.append((f"Salário PY {v:+.0%}", v, 0, 0, 2.56 if v == 0.30 else None))
    for v in (-0.20, -0.10, 0, 0.10, 0.20, 0.30, 0.40, 0.50):
        cen.append((f"Logística {v:+.0%}", 0, v, 0, 3.09 if v == 0.50 else None))
    for v in (0, 0.15, 0.30, 0.45):
        cen.append((f"Energia ANDE {v:+.0%}", 0, 0, v, None))
    cen.append(("Energia ANDE +45,6% (projeção CEARE/BID, linha do estudo)", 0, 0, 0.456, 3.76))
    lin = 5
    s_rows = {}

    def linha_sens(r, rot_, a, b, c, est, amarelo=False):
        s.cell(r, 1, rot_)
        for col, v in ((2, a), (3, b), (4, c)):
            x = s.cell(r, col, v)
            x.number_format = '+0.0%;-0.0%;0.0%'
            if amarelo:
                x.fill = AMARELO
        s.cell(r, 5, f"=B{r}*{S}{R['folha_py']}+C{r}*{S}{R['log_py']}+D{r}*{S}{R['ener_py']}")
        s.cell(r, 6, f"={S}{R['trib']}*MAX({S}{R['va']}+B{r}*{S}{R['folha_py']}+D{r}*{S}{R['ener_py']},{S}{R['fatura']})")
        s.cell(r, 7, f"={S}{R['lop_depois']}+{S}{R['trib_depois']}-F{r}-E{r}")
        s.cell(r, 8, f"={S}{R['irpj']}*MAX(0,G{r})+{S}{R['adic']}*MAX(0,G{r}-{S}{R['lim']})+{S}{R['csll']}*MAX(0,G{r})")
        s.cell(r, 9, f"=G{r}-H{r}")
        s.cell(r, 10, f"=I{r}-{S}{R['ll_antes']}")
        s.cell(r, 11, f"=IF({S}{R['fat']}<>0,J{r}/{S}{R['fat']},0)")
        for col in range(5, 11):
            s.cell(r, col).number_format = RS
        s.cell(r, 11).number_format = PCT2
        s.cell(r, 10).font = NEG
        if est is not None:
            s.cell(r, 12, est).number_format = MI
            s.cell(r, 13, f"=I{r}/1000000-L{r}").number_format = MI
        for col in range(1, 14):
            s.cell(r, col).border = BORDA

    for rot_, a, b, c, est in cen:
        linha_sens(lin, rot_, a, b, c, est)
        lin += 1
    lin += 1
    s.cell(lin, 1, "Cenários combinados (pessimista primeiro). Choques editáveis em amarelo [HIPÓTESE Resultados]").font = NEG
    lin += 1
    cab(s, lin, ["Cenário", "Salário PY", "Logística", "Energia PY", "Custo adicional R$", "Tributo único R$",
                 "Lucro operacional R$", "IRPJ/CSLL R$", "Lucro líquido depois R$", "Ganho anual R$",
                 "Ganho % do faturamento", "Critério", ""])
    lin += 1
    combinados = [
        ("pess", "Pessimista", 0.10, 0.20, 0.45,
         "Salário PY +10% (mínimo PY maior e guarani forte, 4.3 e 7.4), logística +20% (filas na fronteira, 4.6), "
         "energia +45% (projeção CEARE/BID, 4.4)"),
        ("cent", "Central", 0, 0, 0, "Indústria-tipo do estudo 01, 4.7"),
        ("otim", "Otimista", -0.10, -0.20, 0, "Salário PY −10% e logística −20% (pisos dos intervalos pedidos); energia sem reajuste (ANDE descartou reajuste em 2026)"),
    ]
    for chave, rot_, a, b, c, crit in combinados:
        linha_sens(lin, rot_, a, b, c, None, amarelo=True)
        s.cell(lin, 12, crit).alignment = WRAP
        s.merge_cells(start_row=lin, start_column=12, end_row=lin, end_column=13)
        s.row_dimensions[lin].height = 45
        R["pct_" + chave] = f"'Sensibilidade'!$K${lin}"
        R["g_" + chave] = f"'Sensibilidade'!$J${lin}"
        lin += 1
    lin += 1
    # matriz salário × logística
    s.cell(lin, 1, "Matriz: ganho anual (R$) por salário PY (linhas) × logística (colunas), com a energia da célula amarela").font = NEG
    lin += 1
    s.cell(lin, 1, "Choque de energia na matriz")
    ce = s.cell(lin, 2, 0)
    ce.fill, ce.number_format = AMARELO, '+0.0%;-0.0%;0.0%'
    e_ref = f"$B${lin}"
    lin += 1
    logs = [-0.20, -0.10, 0, 0.10, 0.20, 0.30, 0.40, 0.50]
    sals = [-0.10, 0, 0.10, 0.20, 0.30]
    s.cell(lin, 1, "Salário PY \\ Logística").font = NEG
    for j, lv in enumerate(logs):
        x = s.cell(lin, 2 + j, lv)
        x.number_format, x.font, x.fill = '+0%;-0%;0%', NEG, DOURADO
    hdr = lin
    lin += 1
    for sv in sals:
        x = s.cell(lin, 1, sv)
        x.number_format, x.font, x.fill = '+0%;-0%;0%', NEG, DOURADO
        for j in range(len(logs)):
            col = get_column_letter(2 + j)
            sc, lc = f"$A{lin}", f"{col}${hdr}"
            extra = f"({sc}*{S}{R['folha_py']}+{lc}*{S}{R['log_py']}+{e_ref}*{S}{R['ener_py']})"
            trib = f"{S}{R['trib']}*MAX({S}{R['va']}+{sc}*{S}{R['folha_py']}+{e_ref}*{S}{R['ener_py']},{S}{R['fatura']})"
            lo = f"({S}{R['lop_depois']}+{S}{R['trib_depois']}-{trib}-{extra})"
            ir = f"({S}{R['irpj']}*MAX(0,{lo})+{S}{R['adic']}*MAX(0,{lo}-{S}{R['lim']})+{S}{R['csll']}*MAX(0,{lo}))"
            x = s.cell(lin, 2 + j, f"={lo}-{ir}-{S}{R['ll_antes']}")
            x.number_format, x.border = RS, BORDA
        lin += 1
    lin += 1
    s.cell(lin, 1, "Valores negativos (em vermelho) = a maquila piora o resultado. O estudo alerta que as contas mudam de sinal "
                   "com variações razoáveis das premissas.").alignment = WRAP
    s.merge_cells(start_row=lin, start_column=1, end_row=lin, end_column=13)
    larguras(s, [44, 12, 12, 12, 16, 15, 17, 15, 18, 16, 14, 18, 12])

    # ============================================================ Base priorizada
    b = wb.create_sheet("Base priorizada")
    b["A1"] = "Aderência da base (sem nomes e sem R$ por empresa). Uso interno: não sai da Save."
    b["A1"].font = Font(bold=True, size=13, color="C00000")
    b.merge_cells("A1:K1")
    b["A2"] = ("Ordenada por aderência (score). Sem nome, sem CNPJ e sem ganho em R$ por empresa (correção C22 da ata de 05/10/2026): "
               "a lista nominal fica só na Maquila-Base-Priorizada.xlsx. Setores com fator PENDENTE não devem ser simulados até a "
               "validação do técnico tributário. Fonte: Maquila-Base-Priorizada.xlsx, aba 'Base Maquila', faixas A e B (02/10/2026).")
    b["A2"].alignment = WRAP
    b.merge_cells("A2:K2")
    b.row_dimensions[2].height = 45

    wbb = openpyxl.load_workbook(BASE, read_only=True)
    rows = [r for r in wbb["Base Maquila"].iter_rows(min_row=2, values_only=True) if r[0] in ("A", "B")]
    wbb.close()
    rows.sort(key=lambda r: -(r[1] or 0))
    setores = sorted({r[5] for r in rows})

    MOI = {"Confecção e vestuário", "Têxtil", "Embalagens",
           "Produtos diversos (brinquedos, artigos esportivos, médicos)"}
    # tabela de setor
    b["A4"] = "Ajuste por setor (fator sobre o ganho da indústria-tipo; editável)"
    b["A4"].font = NEG
    cab(b, 5, ["Setor Maquila", "Perfil", "Fator", "Base no estudo"])
    lin = 6
    t_ini = lin
    for st in setores:
        moi = st in MOI
        b.cell(lin, 1, st)
        b.cell(lin, 2, "Mão de obra intensiva" if moi else "Capital ou matéria-prima intensiva")
        x = b.cell(lin, 3, 1.0)
        x.fill, x.number_format = AMARELO, '0.00'
        b.cell(lin, 4, (
            "Igual à indústria-tipo (intensiva em mão de obra). Estudo 01, seção 8: setor do perfil ideal."
            if moi else
            "PENDENTE: o estudo 01 lista o setor como aderente (seção 8: alimentos processados, alumínio, farmacêutico) "
            "mas não traz número para ajustar o ganho. Fator 1,00 até o estudo do caso; a faixa larga cobre a incerteza."
        )).alignment = WRAP
        for col in range(1, 5):
            b.cell(lin, col).border = BORDA
        lin += 1
    t_fim = lin - 1
    lin += 1
    lin += 1
    cols = ["Faixa", "Score", "Setor Maquila", "UF", "Faturamento estimado (R$/ano)", "Fonte do faturamento",
            "Perfil", "Fator do setor", "Confiança", "Parceiro", "Status na Save"]
    NC = len(cols)
    cab(b, lin, cols)
    b.row_dimensions[lin].height = 32
    h = lin
    lin += 1
    d_ini = lin
    tab = f"$A${t_ini}:$D${t_fim}"
    for r in rows:
        fat = r[9] if isinstance(r[9], (int, float)) else None
        fonte = r[10] or "sem dado"
        if fat is None:
            conf = "sem dado"
        elif str(fonte).lower().startswith("proxy"):
            conf = "baixa"
        else:
            conf = "média"
        vals = [r[0], r[1], r[5], r[7], fat, fonte]
        for i, v in enumerate(vals, 1):
            b.cell(lin, i, v)
        b.cell(lin, 5).number_format = RS
        b.cell(lin, 7, f"=VLOOKUP(C{lin},{tab},2,FALSE)")
        b.cell(lin, 8, f"=VLOOKUP(C{lin},{tab},3,FALSE)").number_format = '0.00'
        b.cell(lin, 9, conf)
        b.cell(lin, 10, r[17])
        b.cell(lin, 11, r[18])
        for col in range(1, NC + 1):
            b.cell(lin, col).border = BORDA
        lin += 1
    d_fim = lin - 1
    b.cell(lin, 1, "TOTAL").font = NEG
    b.cell(lin, 3, f"=COUNTIF(E{d_ini}:E{d_fim},\">0\")&\" de {d_fim - d_ini + 1} empresas com faturamento\"")
    for col in range(1, NC + 1):
        b.cell(lin, col).border = BORDA
        b.cell(lin, col).font = NEG
    R["tot_lin"] = lin
    R["base_rng"] = (d_ini, d_fim)
    lin += 2
    for n in [
        "Confiança: 'baixa' quando o faturamento é proxy (maior crédito recuperado ÷ 0,084, p75 da amostra), 'média' quando vem de "
        "parecer técnico, 'sem dado' quando não há faturamento (a empresa fica fora do total).",
        "Não há ganho em R$ por empresa nesta aba. A simulação de um caso usa o Simulador com a DRE e o capex do cliente, "
        "sempre como faixa e com o cenário pessimista mostrado primeiro.",
    ]:
        b.cell(lin, 1, n).alignment = WRAP
        b.merge_cells(start_row=lin, start_column=1, end_row=lin, end_column=NC)
        b.row_dimensions[lin].height = 30
        lin += 1
    larguras(b, [30, 9, 30, 6, 18, 34, 26, 9, 11, 22, 12])
    b.freeze_panes = b.cell(h + 1, 3)

    # ============================================================ Premissas e fontes
    pq = wb.create_sheet("Premissas e fontes")
    pq["A1"] = "Premissas e fontes (todas do estudo 01-estudo-maquila.md, v0.1 de 02/10/2026; fontes consultadas em 02/10/2026)"
    pq["A1"].font = TIT
    cab(pq, 3, ["#", "Premissa", "Valor usado", "Unidade", "Fonte", "Data da fonte", "Marca", "Seção do estudo"])
    P = [
        ("Faturamento bruto da indústria-tipo", f"='Simulador'!{R['fat']}", "R$/ano", "Hipótese ilustrativa do estudo", "02/10/2026", "[HIPÓTESE]", "4.7"),
        ("Receita líquida (igual nos dois cenários)", f"='Simulador'!{R['rl']}", "R$/ano", "Hipótese; neutralidade dos tributos indiretos na entrada no Brasil", "02/10/2026", "[HIPÓTESE] [VALIDAR TRIBUTÁRIO]", "4.7 e 2.2"),
        ("Insumos (iguais nos dois cenários; admissão temporária no PY)", 16_000_000, "R$/ano", "Hipótese do estudo; no Simulador ficam em 'demais custos'", "02/10/2026", "[HIPÓTESE]", "4.7"),
        ("Outros custos fixos no Brasil", 3_000_000, "R$/ano", "Hipótese do estudo; no Simulador ficam em 'demais custos'", "02/10/2026", "[HIPÓTESE]", "4.7"),
        ("Margem operacional atual", f"='Simulador'!{R['margem']}", "% fat.", "Lucro operacional de R$ 5,00 mi = 10% do faturamento", "02/10/2026", "[ESTIMATIVA]", "4.7"),
        ("Folha-base (salários)", f"='Simulador'!{R['folha']}", "R$/ano", "Hipótese de paridade de salários", "02/10/2026", "[HIPÓTESE]", "4.7"),
        ("Encargos e provisões no Brasil", f"='Simulador'!{R['enc_br']}", "% do salário", "Faixa 65–80%; estudos de 25,1% (DIEESE) a 102,6% (Pastore), Senado TD 287/2020; INSS 20% + RAT + terceiros ~5,8% + FGTS 8% (Lei 8.212/1991; Lei 8.036/1990)", "2020–2026", "[ESTIMATIVA]", "4.2"),
        ("Encargos e provisões no Paraguai", f"='Simulador'!{R['enc_py']}", "% do salário", "Faixa 25–30%; IPS patronal 16,5% (fonte secundária, conferir no IPS)", "2026", "[ESTIMATIVA]", "4.2"),
        ("Salário PY ÷ salário BR", f"='Simulador'!{R['rel_sal']}", "relação", "Paridade por hipótese", "02/10/2026", "[HIPÓTESE]", "4.7"),
        ("Salário mínimo Paraguai", 3_044_000, "Gs/mês (~R$ 2.719)", "Decreto 6.225/2026; Resolução MTESS 670/2026", "07/07/2026", "oficial", "4.3"),
        ("Salário mínimo Brasil", 1_621, "R$/mês", "Decreto 12.797/2025", "01/01/2026", "oficial", "4.3"),
        ("Consumo de energia", f"='Simulador'!{R['mwh']}", "MWh/ano", "Hipótese do estudo", "02/10/2026", "[HIPÓTESE]", "4.7"),
        ("Tarifa de energia Brasil (custo médio da indústria)", f"='Simulador'!{R['tar_br']}", "R$/MWh", "FIRJAN via CanalEnergia", "data da medição a confirmar", "fonte secundária", "4.4"),
        ("Tarifa média ANDE", f"='Simulador'!{R['tar_py']}", "US$/MWh", "ABC Color (tarifa média 2024: US$ 49,2–49,5)", "06/08/2026", "fonte secundária", "4.4"),
        ("Projeção de alta da ANDE (alta tensão)", 0.456, "%", "Estudo CEARE com apoio do BID, via ABC Color; não aprovada", "06/08/2026", "projeção", "4.4"),
        ("Área do galpão", f"='Simulador'!{R['area']}", "m²", "Hipótese do estudo", "02/10/2026", "[HIPÓTESE]", "4.7"),
        ("Galpão Brasil (São Paulo)", f"='Simulador'!{R['gal_br']}", "R$/m²/mês", "SiiLA via Itaú BBA, 4T25", "20/02/2026", "consultoria", "4.5"),
        ("Galpão Paraguai (parques industriais)", f"='Simulador'!{R['gal_py']}", "US$/m²/mês", "MIC, catálogo de parques industriais (US$ 3,00–5,50; supõe mensal)", "sem data", "[HIPÓTESE] sobre periodicidade", "4.5"),
        ("Logística atual no Brasil", f"='Simulador'!{R['log_br']}", "R$/ano", "Hipótese do estudo", "02/10/2026", "[HIPÓTESE]", "4.7"),
        ("Viagens de carreta por ano no cenário PY", 350, "viagens", "200 de produto + 150 de insumos; hipótese", "02/10/2026", "[HIPÓTESE]", "4.7"),
        ("Frete CDE → SP por carreta", 7_400, "R$/viagem", "Piso ANTT, Resolução 6.076 (DOU 20/01/2026): R$ 6,1604/km + R$ 635,08; ~1.050 km", "20/01/2026", "[ESTIMATIVA]", "4.6"),
        ("Despacho e fronteira", 400_000, "R$/ano", "Hipótese do estudo", "02/10/2026", "[HIPÓTESE]", "4.7"),
        ("Frete adicional Brasil–Paraguai", f"='Simulador'!{R['frete_ef']}", "R$/ano", "350 × 7.400 + 400.000 − 600.000 (cálculo nosso sobre o estudo)", "02/10/2026", "[ESTIMATIVA]", "4.7"),
        ("Estrutura no exterior", f"='Simulador'!{R['estrut']}", "R$/ano", "Contabilidade, jurídico, preços de transferência, viagens", "02/10/2026", "[HIPÓTESE]", "4.7"),
        ("% da produção levada ao PY", f"='Simulador'!{R['pct_py']}", "%", "Indústria-tipo: produção toda no PY", "02/10/2026", "[HIPÓTESE]", "4.7"),
        ("Tributo único de maquila", f"='Simulador'!{R['trib']}", "% da base", "Lei 7.547/2025, arts. 37–38 (base: o maior entre valor agregado e fatura)", "08/09/2025", "oficial", "1.2 e 4.1"),
        ("Base do tributo na indústria-tipo: fatura cheia", f"='Simulador'!{R['pct_fat']}", "% da receita líquida", "Cenário conservador da regra 'o que for maior'", "02/10/2026", "[HIPÓTESE] [VALIDAR TRIBUTÁRIO]", "4.7"),
        ("IRPJ + adicional + CSLL", 0.34, "% do lucro", "Lei 9.249/1995, art. 3º (15% + 10% acima de R$ 240 mil/ano); Lei 7.689/1988 (CSLL 9%)", "vigente", "oficial", "4.1"),
        ("Lucro da controlada tributado no Brasil todo ano", "art. 77", "", "Lei 12.973/2014, art. 77 (distribuído ou não); dedução do IR externo limitada (art. 87)", "vigente", "[VALIDAR TRIBUTÁRIO]", "7.1"),
        ("Crédito presumido de até 9% (não considerado)", 0.09, "% ", "Lei 12.973/2014, art. 87, §10 (Lei 15.079/2024), até 2029; reduziria o IR em ~R$ 0,1 mi", "vigente", "[VALIDAR TRIBUTÁRIO]", "4.7 e 7.1"),
        ("Câmbio R$/US$", f"='Simulador'!{R['cambio']}", "R$/US$", "PTAX/BCB", "02/10/2026", "oficial", "4"),
        ("Câmbio Gs/US$", 5_847.45, "Gs/US$", "Interbancário PY, La Nación", "29/09/2026", "fonte secundária", "4"),
        ("Capex da implantação", "PENDENTE", "R$", "O estudo 01 não estima capex para a indústria-tipo; informar no Simulador", "—", "PENDENTE", "8.1"),
        ("Choques da sensibilidade (salário −10% a +30%, logística −20% a +50%, energia 0% a +45%)", "ver aba", "", "Intervalos do pedido; pontos de checagem do estudo: salário +30% → 2,56; logística +50% → 3,09; ANDE +45,6% → 3,76", "02/10/2026", "[HIPÓTESE]", "4.7"),
        ("Cenários pessimista e otimista da base", "ver aba", "", "Combinação definida pelo Resultados (aba Sensibilidade, células amarelas)", "05/10/2026", "[HIPÓTESE Resultados]", "—"),
        ("Faturamento das empresas da base", "ver aba", "", "Maquila-Base-Priorizada.xlsx; proxy = maior crédito ÷ 0,084 (p75) com confiança muito baixa", "02/10/2026", "[ESTIMATIVA]", "03-base-maquila, seção 2"),
    ]
    for i, (prem, val, uni, fonte, data, marca, sec) in enumerate(P, 1):
        r = 3 + i
        vals = [i, prem, val, uni, fonte, data, marca, sec]
        for j, v in enumerate(vals, 1):
            x = pq.cell(r, j, v)
            x.border, x.alignment = BORDA, WRAP
        x = pq.cell(r, 3)
        if isinstance(val, float) and val < 1:
            x.number_format = PCT
        elif isinstance(val, str) and val.startswith("=") and any(k in val for k in (R['margem'], R['enc_br'], R['enc_py'], R['rel_sal'], R['pct_py'], R['pct_fat'], R['trib'])):
            x.number_format = PCT
        else:
            x.number_format = '#,##0.####'
    larguras(pq, [5, 46, 16, 16, 70, 16, 24, 14])
    return wb, R


# ---------------------------------------------------------------- recálculo independente em Python
def modelo(fat=50e6, rl=40e6, margem=0.10, folha=6e6, enc_br=0.70, enc_py=0.28, rel=1.0, mwh=4000, tbr=543.90,
           tpy=49.5, area=8000, gbr=31.49, gpy=4.50, log_br=600e3, frete=2.39e6, estrut=500e3, p=1.0, pfat=1.0,
           cambio=5.2238, ds=0.0, dl=0.0, de=0.0):
    def ir(l):
        return 0.15 * max(0, l) + 0.10 * max(0, l - 240e3) + 0.09 * max(0, l)
    folha_b = folha * (1 + enc_br)
    lop_b = margem * fat
    ener_b, gal_b = mwh * tbr, area * gbr * 12
    demais = rl - lop_b - folha_b - ener_b - gal_b - log_br
    folha_py = folha * p * rel * (1 + enc_py) * (1 + ds)
    ener_py = mwh * p * tpy * cambio * (1 + de)
    gal_py = area * p * gpy * cambio * 12
    est = estrut if p > 0 else 0
    log_d = log_br + frete * p + (log_br + frete) * p * dl
    va = folha_py + ener_py + gal_py + est
    trib = 0.01 * max(va, rl * p * pfat)
    custos_d = (folha * (1 - p) * (1 + enc_br) + folha_py + mwh * (1 - p) * tbr + ener_py
                + area * (1 - p) * gbr * 12 + gal_py + log_d + est + trib + demais)
    lop_d = rl - custos_d
    ll_b, ll_d = lop_b - ir(lop_b), lop_d - ir(lop_d)
    return dict(lop_b=lop_b, lop_d=lop_d, ir_b=ir(lop_b), ir_d=ir(lop_d), ll_b=ll_b, ll_d=ll_d, ganho=ll_d - ll_b,
                folha_d=folha_py, ener_d=ener_py, gal_b=gal_b, gal_d=gal_py, log_d=log_d, trib=trib, ener_b=ener_b)


def conferir(R):
    vals, erros = avaliar_tudo(SAIDA)
    print(f"Fórmulas avaliadas: {len(vals)} · erros do avaliador: {len(erros)}")
    for e in erros[:20]:
        print("  ERRO", e)
    ruins = [(k, v) for k, v in vals.items() if isinstance(v, str) and v.startswith("#")]
    print(f"Células com #REF/#DIV/0/#N/A: {len(ruins)}")

    def V(aba, ref):
        return vals[(aba, ref.replace("$", "").split("!")[-1])]

    m = modelo()
    print("\n== Indústria-tipo: Python × fórmulas × estudo (R$ mi)")
    pares = [("Lucro operacional antes", m["lop_b"], "B", "lop", 5.00), ("Lucro operacional depois", m["lop_d"], "C", "lop", 6.14),
             ("IR antes", m["ir_b"], "B", "ir", 1.68), ("IR depois", m["ir_d"], "C", "ir", 2.06),
             ("Lucro líquido antes", m["ll_b"], "B", "ll", 3.32), ("Lucro líquido depois", m["ll_d"], "C", "ll", 4.08)]
    ws = openpyxl.load_workbook(SAIDA)["Simulador"]
    linha_de = {}
    for row in ws.iter_rows(min_col=1, max_col=1):
        t = row[0].value
        if t == "Lucro operacional":
            linha_de["lop"] = row[0].row
        elif isinstance(t, str) and t.startswith("IRPJ/CSLL 34%"):
            linha_de["ir"] = row[0].row
        elif t == "Lucro líquido":
            linha_de["ll"] = row[0].row
    maxdif = 0
    for nome, py, col, k, est in pares:
        fx = vals[("Simulador", f"{col}{linha_de[k]}")]
        maxdif = max(maxdif, abs(fx - py))
        print(f"  {nome:26s} Python {py/1e6:8.4f} · fórmula {fx/1e6:8.4f} · estudo {est:5.2f} · dif. estudo {fx/1e6-est:+.4f}")
    g = V("Simulador", R["ganho"])
    print(f"  Ganho anual: Python {m['ganho']/1e6:.4f} · fórmula {g/1e6:.4f} · documentos: +0,75 (fonte única: esta calculadora)")
    print(f"  Ganho % fat: {V('Simulador', R['ganho_pct']):.4%} · variação LL {V('Simulador', R['ganho_ll']):.2%}"
          f" · payback: {V('Simulador', R['payback'])}")

    print("\n== Sensibilidade: Python × fórmulas")
    sw = openpyxl.load_workbook(SAIDA)["Sensibilidade"]
    out = []
    for row in sw.iter_rows(min_row=5):
        a, b_, c, d = (x.value for x in row[:4])
        e5 = row[4].value
        if isinstance(a, str) and isinstance(e5, str) and e5.startswith("=B"):
            r = row[0].row
            mm = modelo(ds=b_, dl=c, de=d)
            fx_ll, fx_g = vals[("Sensibilidade", f"I{r}")], vals[("Sensibilidade", f"J{r}")]
            maxdif = max(maxdif, abs(fx_g - mm["ganho"]), abs(fx_ll - mm["ll_d"]))
            est = row[11].value if isinstance(row[11].value, (int, float)) else None
            out.append((a, fx_ll, fx_g, vals[("Sensibilidade", f"K{r}")], mm["ganho"], est))
            print(f"  {a:58s} LL {fx_ll/1e6:6.3f} · ganho {fx_g/1e6:+7.3f} mi ({vals[('Sensibilidade', f'K{r}')]:+.2%})"
                  f" · Python {mm['ganho']/1e6:+7.3f}" + (f" · estudo LL {est:.2f} (dif {fx_ll/1e6-est:+.3f})" if est else ""))
    # galpão US$ 5,50 (linha do estudo, só em Python)
    mg = modelo(gpy=5.50)
    print(f"  (só Python) Galpão US$ 5,50: LL depois {mg['ll_d']/1e6:.3f} · estudo 3,74")

    # matriz salário × logística
    for row in sw.iter_rows(min_row=5):
        if isinstance(row[0].value, (int, float)) and isinstance(row[1].value, str) and row[1].value.startswith("="):
            r = row[0].row
            hdr = next(rr for rr in range(r, 0, -1) if sw.cell(rr, 1).value == "Salário PY \\ Logística")
            e_ch = sw.cell(hdr - 1, 2).value
            for j in range(2, 10):
                mm = modelo(ds=row[0].value, dl=sw.cell(hdr, j).value, de=e_ch)
                maxdif = max(maxdif, abs(vals[("Sensibilidade", sw.cell(r, j).coordinate)] - mm["ganho"]))
    print("  Matriz salário × logística conferida contra o Python.")
    print("\n== Base priorizada (sem R$ por empresa)")
    d0, d1 = R["base_rng"]
    bw = openpyxl.load_workbook(SAIDA)["Base priorizada"]
    n_fat = sum(isinstance(bw.cell(r, 5).value, (int, float)) for r in range(d0, d1 + 1))
    print(f"  empresas: {d1-d0+1} (com faturamento: {n_fat}); colunas: {[c.value for c in bw[d0-1]]}")
    print(f"\nMaior diferença absoluta Python × fórmula: R$ {maxdif:.6f}")
    return erros, ruins, maxdif


if __name__ == "__main__":
    wb, R = construir()
    wb.calculation.fullCalcOnLoad = True  # o Excel recalcula tudo ao abrir
    wb.save(SAIDA)
    print("Salvo:", SAIDA)
    erros, ruins, md = conferir(R)
    sys.exit(1 if (erros or ruins or md > 0.01) else 0)
