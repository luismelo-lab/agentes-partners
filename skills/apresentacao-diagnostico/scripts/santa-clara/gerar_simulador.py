#!/usr/bin/env python3
"""Simulador de cenários (sensibilidades) para a reunião com a Cooperativa Santa Clara. Premissas editáveis; cores e fonte de marca.json.
Uso: python3 gerar_simulador.py [saida.xlsx]"""
import json, sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
M = json.load(open(Path.home() / "agentes-partners/departamentos/marketing-marca/padrao/marca.json"))["claro"]
SAIDA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "agentes-partners/departamentos/tributario/apresentacao-diagnostico/santa-clara/Santa-Clara-Simulador-Cenarios.xlsx"
F = "IBM Plex Sans"; FM = "IBM Plex Mono"
ouro, suave, borda, txt, txt2 = M["ouro"].lstrip("#"), M["ouro_suave"].lstrip("#"), M["borda_2"].lstrip("#"), M["texto"].lstrip("#"), M["texto_2"].lstrip("#")
fino = Side(style="thin", color=borda); box = Border(left=fino, right=fino, top=fino, bottom=fino)
wb = Workbook(); ws = wb.active; ws.title = "Simulador"; ws.sheet_view.showGridLines = False
for col, w in zip("ABCDEF", (46, 18, 18, 18, 4, 62)): ws.column_dimensions[col].width = w


def put(cell, v, bold=False, size=11, color=txt, fill=None, fmt=None, mono=False, align="left", wrap=False, border=False):
    c = ws[cell]; c.value = v; c.font = Font(name=FM if mono else F, bold=bold, size=size, color=color)
    c.alignment = Alignment(horizontal=align, vertical="center", wrap_text=wrap)
    if fill: c.fill = PatternFill("solid", fgColor=fill)
    if fmt: c.number_format = fmt
    if border: c.border = box
    return c


put("A1", "Santa Clara · simulador de cenários", True, 20); put("A2", "Sensibilidades, não metas: cada linha é independente e não se soma. Células douradas são premissas editáveis.", color=txt2)
ws.row_dimensions[1].height = 30
put("A4", "Premissas gerais", True, 12, fill=ouro)
for c in "BCD": ws[f"{c}4"].fill = PatternFill("solid", fgColor=ouro)
rows = [("Receita anual (R$ mi)", 3000, "#,##0", "Projeção de R$ 3 bi para 2026 (Jornal do Comércio, jul/2026); não é balanço"),
        ("Vendas a prazo (% da receita)", 0.70, "0%", "Premissa do Luis (21/10/2026); trocar pela carteira a receber real"),
        ("Custo de capital (% ao ano)", 0.2289, "0.00%", "Capital de giro de pessoas jurídicas, Banco Central SGS 20725, ago/2026; média de mercado, não o da cooperativa"),
        ("Dívida de referência (R$ mi)", 100, "#,##0", "Cenário por R$ 100 mi; trocar pelo extrato de dívidas")]
for i, (a, v, f, n) in enumerate(rows):
    r = 5 + i; put(f"A{r}", a); put(f"B{r}", v, True, fill=suave, fmt=f, mono=True, align="right", border=True); put(f"F{r}", n, color=txt2, size=10, wrap=True)
put("A10", "Cenários", True, 12, fill=ouro)
for c, t in zip("BCD", ("Conservador", "Base", "Ambicioso")): put(f"{c}10", t, True, fill=ouro, align="right")
ws["A10"].fill = PatternFill("solid", fgColor=ouro)
ent = [("Redução do prazo de recebimento (dias)", (1, 3, 5), "0"), ("Ganho de margem (pontos percentuais)", (0.1, 0.3, 0.5), "0.0"), ("Redução do custo da dívida (pontos percentuais)", (2, 4, 6), "0")]
for i, (a, vs, f) in enumerate(ent):
    r = 11 + i; put(f"A{r}", a)
    for c, v in zip("BCD", vs): put(f"{c}{r}", v, True, fill=suave, fmt=f, mono=True, align="right", border=True)
put("A15", "Resultados (R$ mi)", True, 12, fill=ouro)
for c in "BCD": ws[f"{c}15"].fill = PatternFill("solid", fgColor=ouro)
res = [("Caixa liberado, uma única vez (não é lucro)", "=$B$5/365*$B$6*{c}11", "0.0", "Receita diária × % a prazo × dias a menos"),
       ("Juros evitados sobre esse caixa, por ano", "={c}16*$B$7", "0.0", "Caixa liberado × custo de capital"),
       ("Valor da margem, por ano", "=$B$5*{c}12/100", "0.0", "Receita × pontos de margem"),
       ("Valor da redução do custo da dívida, por ano", "=$B$8*{c}13/100", "0.0", "Dívida de referência × pontos de custo"),
       ("Crédito do leite", "a dimensionar", None, "Depende de habilitação, regime e separação entre ato cooperativo e não cooperativo; só após o tributarista")]
for i, (a, fm, f, n) in enumerate(res):
    r = 16 + i; put(f"A{r}", a)
    for c in "BCD": put(f"{c}{r}", fm.format(c=c) if fm.startswith("=") else fm, True, fmt=f, mono=True, align="right", border=True)
    put(f"F{r}", n, color=txt2, size=10, wrap=True)
put("A22", "As linhas não se somam, não são metas nem promessa de resultado. Valor, prazo e êxito só se confirmam depois do diagnóstico com os documentos da cooperativa. A Save não concede crédito; antecipação e FIDC são operados por instituições autorizadas.", color=txt2, size=10, wrap=True)
ws.merge_cells("A22:F22"); ws.row_dimensions[22].height = 44
ws2 = wb.create_sheet("Fontes")
ws2.column_dimensions["A"].width = 120
linhas = ["Fontes e premissas", "Receita: projeção de R$ 3 bi em 2026, Jornal do Comércio (jul/2026). Não existe balanço público; trocar por DRE por negócio.",
          "Custo de capital: Banco Central, SGS 20725 (capital de giro de pessoas jurídicas), agosto/2026.",
          "Vendas a prazo de 70%: premissa de trabalho; trocar pela carteira a receber por canal.",
          "Dívida de referência: R$ 100 mi por convenção; o valor real vem do extrato de dívidas.",
          "Crédito do leite: fluxo teórico a dimensionar com o tributário (Lei 10.925/2004; LC 224/2025; ato cooperativo, Lei 5.764/1971).",
          "Cálculos Save. Consulta em 21/10/2026."]
for i, l in enumerate(linhas, 1):
    c = ws2[f"A{i}"]; c.value = l; c.font = Font(name=F, bold=(i == 1), size=14 if i == 1 else 11, color=txt); c.alignment = Alignment(wrap_text=True)
ws2.sheet_view.showGridLines = False
wb.save(SAIDA); print(SAIDA)
# conferência numérica
rec, pr, k = 3000, .7, .2289
for d, mg, dv in ((1, .1, 2), (3, .3, 4), (5, .5, 6)):
    cx = rec / 365 * pr * d; print(f"{d}d: caixa {cx:.1f} | juros {cx * k:.2f} | margem {rec * mg / 100:.1f} | dívida {100 * dv / 100:.1f}")
