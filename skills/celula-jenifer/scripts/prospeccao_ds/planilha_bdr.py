"""Planilha de ligações da BDR (Jenifer) · prospecção de novos clientes para a D&S.

Lê modelo.pkl (só Lucro Real, sem clientes da D&S nem negócios do HubSpot) e gera o lote em Excel no padrão Save.
Lotes: o registro `lotes-ds.json` guarda os CNPJs já entregues; o lote seguinte traz só empresas novas, para não
sobrescrever as anotações da BDR.

    python3 planilha_bdr.py <pasta-de-saída> [--lote N]
"""
import datetime as dt, json, os, pickle, re, sys, urllib.parse
from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

S = os.environ.get("PROSPECCAO_DS", os.path.expanduser("~/agentes-partners/departamentos/intel-comercial/prospeccao-ds"))  # dados (fora do repositório); AP = os.path.expanduser("~/agentes-partners")
REPO = os.environ.get("REPO", os.path.expanduser("~/agentes-partners"))
sys.path.insert(0, os.path.join(REPO, "skills/depto-solucoes/scripts"))
from mapa_conta import setor, teses_segmento  # noqa: E402

M = json.load(open(os.path.join(AP, "departamentos/marketing-marca/padrao/marca.json")))
FONTE = M["fontes"]["sans"]; MONO = M["fontes"]["mono"]; K = M["claro"]
OURO, OURO_SUAVE, PRETO, CINZA, BORDA, FUNDO2 = (K["ouro"][1:], K["ouro_suave"][1:], K["texto"][1:], K["texto_2"][1:], K["borda_2"][1:], K["fundo_2"][1:])
f = lambda **k: Font(name=FONTE, **k)
fill = lambda c: PatternFill("solid", fgColor=c)
LINHA = Border(bottom=Side(style="thin", color=BORDA))
HOJE = dt.date.today()

STATUS = ["A ligar", "Sem resposta (tentar de novo)", "Retornar na data", "Pediu e-mail ou material", "Reunião marcada",
          "Pedir apresentação à D&S", "Não é Lucro Real", "Já fez com outra empresa", "Sem interesse", "Não contatar (opt-out)"]

GANCHO = {
    "Proteína animal": "Em frigoríficos, atacados de carne e açougues no Lucro Real, é comum haver créditos de PIS/COFINS nas compras que ficam fora da rotina fiscal. Queremos verificar se é o caso de vocês.",
    "Varejo alimentar": "Hortifrútis, mercados e atacados de alimentos trabalham com muitos itens de tributação diferenciada. Isso costuma deixar créditos de PIS/COFINS sem aproveitar. Queremos verificar se há no caso de vocês.",
    "Combustíveis e GLP": "Revendas de combustível e GLP têm regras próprias de PIS/COFINS e ICMS-ST. Vale conferir se há valores pagos a mais nos últimos 5 anos.",
    "Café e grãos": "Atacados e cerealistas no Lucro Real costumam ter créditos nas compras, no frete e na armazenagem que ficam para trás. Queremos verificar se há no caso de vocês.",
    "Panificação e alimentos": "Indústrias de alimentos e padarias no Lucro Real costumam ter créditos de PIS/COFINS sobre insumos que não são aproveitados. Queremos verificar se há no caso de vocês.",
    "Transporte de carga": "Transportadoras no Lucro Real costumam ter créditos de PIS/COFINS sobre diesel, pneus e manutenção, e pontos a revisar na folha. Queremos verificar se há no caso de vocês.",
    "Confecção e têxtil": "Confecções no Lucro Real costumam ter créditos sobre insumos e pontos a revisar na contribuição sobre a folha. Queremos verificar se há no caso de vocês.",
}
GANCHO_PADRAO = "Empresas do seu segmento no Lucro Real costumam ter créditos de PIS/COFINS dos últimos 5 anos que ficam fora da rotina. Queremos verificar se há no caso de vocês."
URGENCIA = "Com a reforma tributária, o PIS/COFINS sai de cena em 2027: é um bom momento para revisar os últimos 5 anos."


def nome(p): return (p.get("fantasia") or "").strip() or (p.get("razao") or "").strip()
def cnpj_fmt(c): return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}"
def cep_fmt(c): return f"{c[:5]}-{c[5:]}" if c and len(c) == 8 else (c or "")
def anos(ab):
    try: return HOJE.year - int(ab[:4]) - ((HOJE.month, HOJE.day) < (int(ab[4:6]), int(ab[6:8])))
    except Exception: return None
def prioridade(p): return "A" if p["similaridade"] >= 90 else "B" if p["similaridade"] >= 85 else "C"
def busca(p):
    q = f'{p.get("razao") or nome(p)} {p.get("municipio") or ""} telefone'
    return "https://www.google.com/search?q=" + urllib.parse.quote_plus(q)
def titulo(t): return (t or "").title().replace(" De ", " de ").replace(" Da ", " da ").replace(" Do ", " do ").replace(" Dos ", " dos ").replace(" Das ", " das ").replace(" E ", " e ")


def cabecalho(ws, grupos, colunas, larguras):
    """Linha 1: faixas dos grupos; linha 2: nome das colunas."""
    c = 1
    for g, n, cor in grupos:
        ws.merge_cells(start_row=1, start_column=c, end_row=1, end_column=c + n - 1)
        cel = ws.cell(1, c, g); cel.font = f(bold=True, size=10, color=PRETO if cor == OURO else "FFFFFF"); cel.fill = fill(cor)
        cel.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        for j in range(c, c + n): ws.cell(1, j).fill = fill(cor)
        c += n
    for j, (nomecol, w) in enumerate(zip(colunas, larguras), 1):
        cel = ws.cell(2, j, nomecol); cel.font = f(bold=True, size=10, color=PRETO); cel.fill = fill(OURO_SUAVE)
        cel.alignment = Alignment(wrap_text=True, vertical="center"); cel.border = Border(bottom=Side(style="medium", color=OURO))
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.row_dimensions[1].height = 22; ws.row_dimensions[2].height = 36


def gerar(saida, lote):
    D = pickle.load(open(S + "/modelo.pkl", "rb")); pros = D["pros"]; anc = D["anc"]
    reg_lotes = os.path.join(S, "lotes-ds.json"); lotes = json.load(open(reg_lotes)) if os.path.exists(reg_lotes) else {}
    ja = {c for k, v in lotes.items() if int(k) < lote for c in v}
    pros = [p for p in pros if p["cnpj"] not in ja]
    for p in pros: p["prio"] = prioridade(p)
    pros.sort(key=lambda p: (p["prio"], p["nivel_geo"], -p["potencial"]))

    wb = Workbook()
    # ── Como usar ──
    cu = wb.active; cu.title = "Como usar"; cu.sheet_view.showGridLines = False; cu.column_dimensions["A"].width = 3; cu.column_dimensions["B"].width = 110
    linhas = [("Prospecção de novos clientes · Parceiro D&S · Lote %d" % lote, dict(bold=True, size=18, color=PRETO)),
              (f"Gerado em {HOJE.strftime('%d/%m/%Y')} · {len(pros)} empresas · uso interno da Área Partners", dict(size=11, color=CINZA)), ("", {}),
              ("O que é esta lista", dict(bold=True, size=13, color=K["ouro_texto"][1:])),
              ("Empresas no Lucro Real, ativas, parecidas com os clientes que a D&S já fechou e perto deles (mesmo bairro, região da cidade, cidade ou cidades vizinhas).", {}),
              ("Ficaram fora: clientes da D&S (qualquer fase), empresas com negócio no HubSpot (qualquer parceiro), Simples, MEI e empresas em recuperação judicial ou falência.", {}), ("", {}),
              ("Como trabalhar a lista", dict(bold=True, size=13, color=K["ouro_texto"][1:])),
              ("1. Abra a aba Ligações. Comece pela prioridade A e pelo nível \"Mesmo bairro\". A lista já vem nessa ordem.", {}),
              ("2. Antes de ligar, clique em \"Buscar contato\" para achar o telefone e anote na coluna Telefone. A base pública não traz o contato.", {}),
              ("3. Use o Gancho da linha e o Roteiro (aba Roteiro). Uma pergunta por vez; o objetivo da ligação é marcar 30 minutos.", {}),
              ("4. Depois da ligação, escolha o Status na lista, preencha a Data, o Próximo passo e a Data de retorno. Use Anotações para o que ouviu (regime, decisor, contador, se já fez recuperação).", {}),
              ("5. Reunião marcada: registre no HubSpot (pipeline BDR) com o Master D&S e avise a Daniela.", {}),
              ("6. A aba Resumo atualiza sozinha conforme você preenche o Status.", {}), ("", {}),
              ("Regras que não mudam", dict(bold=True, size=13, color=K["ouro_texto"][1:])),
              ("• Nunca citar o nome de clientes da D&S ou da Save. As colunas cinza (Uso interno) são só para você entender a prioridade.", {}),
              ("• Nunca prometer valor, percentual, prazo ou resultado. Falamos em \"verificar se há\" e em \"diagnóstico\".", {}),
              ("• Se a pessoa pedir para não ser contatada, marque \"Não contatar (opt-out)\" e não volte a ligar.", {}),
              ("• Sempre que possível, peça apresentação à D&S (status \"Pedir apresentação à D&S\"): a conversa rende mais.", {}),
              ("• Se a empresa disser que não é Lucro Real, marque o status: a lista é revisada com isso.", {}), ("", {}),
              ("Legenda", dict(bold=True, size=13, color=K["ouro_texto"][1:])),
              ("Prioridade A: muito parecida com um cliente ganho da D&S (similaridade de 90% ou mais) · B: 85% a 90% · C: abaixo de 85%.", {}),
              ("Proximidade: mesmo bairro, mesma região da cidade, mesma cidade ou cidades vizinhas de um cliente ganho.", {}),
              ("Potencial esperado: estimativa interna pelos clientes parecidos (crédito de referência × chance do segmento). Não é diagnóstico e não se fala ao telefone.", {})]
    for i, (t, st) in enumerate(linhas, 2):
        c = cu.cell(i, 2, t); c.font = f(**({"size": 11, "color": PRETO} | st)); c.alignment = Alignment(wrap_text=True, vertical="top")

    # ── Ligações ──
    ws = wb.create_sheet("Ligações"); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 100
    grupos = [("CONTROLE DA LIGAÇÃO", 7, OURO), ("EMPRESA", 15, "0F1115"), ("PARA A CONVERSA", 3, OURO), ("USO INTERNO · NÃO CITAR", 5, "4A4F58")]
    cols = ["Nº", "Prior.", "Status", "Data do contato", "Próximo passo", "Data de retorno", "Anotações da ligação",
            "Empresa (nome fantasia)", "Razão social", "CNPJ", "Segmento", "Cidade", "Bairro", "Endereço", "CEP", "Telefone (preencher)", "Buscar contato",
            "Anos de empresa", "Porte", "Capital social (R$)", "Regime (ano)", "Atividade principal (CNAE)",
            "Gancho para abrir a conversa", "Teses que cabem no segmento (para a reunião, não detalhar ao telefone)", "Pergunta de qualificação",
            "Proximidade", "Cliente D&S de referência", "Similaridade", "Crédito de referência (R$)", "Potencial esperado (R$)"]
    larg = [5, 6, 22, 11, 24, 11, 40, 28, 32, 19, 18, 16, 18, 30, 10, 18, 11, 8, 13, 14, 15, 30, 48, 46, 34, 20, 26, 10, 15, 15]
    cabecalho(ws, grupos, cols, larg)
    dv = DataValidation(type="list", formula1='"' + ",".join(STATUS) + '"', allow_blank=False, showErrorMessage=True,
                        errorTitle="Status", error="Escolha um status da lista."); ws.add_data_validation(dv)
    dvd = DataValidation(type="date", operator="greaterThan", formula1="DATE(2026,1,1)", showErrorMessage=True, error="Use uma data (dd/mm/aaaa)."); ws.add_data_validation(dvd)
    for i, p in enumerate(pros, 1):
        r = i + 2; ex = p["exemplo"]; ag = p["ancora_geo"]
        s = {"cnae": p["cnae"], "regime": "Lucro Real", "faturamento": 4.8e6, "setor": setor(p["cnae"])}
        teses = teses_segmento(s)
        ref_nome = (ag["rf"]["fantasia"] or ag["rf"]["razao"] or "").strip()
        reg = str(p.get("regime") or "")
        vals = [i, p["prio"], "A ligar", None, None, None, None,
                titulo(nome(p)), p.get("razao"), cnpj_fmt(p["cnpj"]), s["setor"], titulo(p["municipio"]), titulo(p.get("bairro") or ""),
                titulo(p.get("logradouro") or ""), cep_fmt(p.get("cep")), None, "Buscar", anos(p.get("abertura")), p.get("porte"), p.get("capital"),
                titulo(reg).replace("(", "(").replace("Lucro Real", "Lucro Real"), p.get("cnae_desc"),
                GANCHO.get(s["setor"], GANCHO_PADRAO) + " " + URGENCIA, "\n".join("• " + t for t in teses),
                "Hoje a empresa está no Lucro Real? Quem cuida da parte fiscal, um contador externo ou equipe interna?",
                p["nivel_geo"][4:], f'{titulo(ref_nome)} · {titulo(ag.get("bairro") or "")}, {titulo(ag["rf"]["municipio"])}',
                p["similaridade"] / 100, round(p["ref"], -3), round(p["potencial"], -3)]
        for j, v in enumerate(vals, 1):
            c = ws.cell(r, j, v); c.font = f(size=10, color=PRETO); c.alignment = Alignment(wrap_text=True, vertical="top"); c.border = LINHA
            if j >= 26: c.font = f(size=10, color=CINZA); c.fill = fill(FUNDO2)
        ws.cell(r, 17).hyperlink = busca(p); ws.cell(r, 17).font = f(size=10, color=K["ouro_texto"][1:], underline="single")
        ws.cell(r, 2).font = f(size=11, bold=True, color=PRETO); ws.cell(r, 2).alignment = Alignment(horizontal="center", vertical="top")
        if p["prio"] == "A": ws.cell(r, 2).fill = fill(OURO)
        elif p["prio"] == "B": ws.cell(r, 2).fill = fill(OURO_SUAVE)
        ws.cell(r, 8).font = f(size=10, bold=True, color=PRETO)
        for j, fmt in ((4, "dd/mm/yyyy"), (6, "dd/mm/yyyy"), (20, '"R$" #,##0'), (28, "0%"), (29, '"R$" #,##0'), (30, '"R$" #,##0')): ws.cell(r, j).number_format = fmt
        ws.cell(r, 10).font = Font(name=MONO, size=10, color=PRETO)
        ws.row_dimensions[r].height = 92
    ult = len(pros) + 2
    dv.add(f"C3:C{ult}"); dvd.add(f"D3:D{ult}"); dvd.add(f"F3:F{ult}")
    # cor do status
    for st, cor in (("Reunião marcada", OURO), ("Retornar na data", OURO_SUAVE), ("Pediu e-mail ou material", OURO_SUAVE), ("Pedir apresentação à D&S", OURO_SUAVE)):
        ws.conditional_formatting.add(f"C3:C{ult}", FormulaRule(formula=[f'$C3="{st}"'], fill=fill(cor), font=Font(name=FONTE, bold=True, color=PRETO)))
    for st in ("Sem interesse", "Não contatar (opt-out)", "Não é Lucro Real", "Já fez com outra empresa"):
        ws.conditional_formatting.add(f"A3:Y{ult}", FormulaRule(formula=[f'$C3="{st}"'], font=Font(name=FONTE, color="9AA0A8", strike=st == "Não contatar (opt-out)")))
    ws.conditional_formatting.add(f"F3:F{ult}", FormulaRule(formula=[f'AND($F3<>"",$F3<=TODAY(),$C3="Retornar na data")'], fill=fill("F6D7A7"), font=Font(name=FONTE, bold=True, color=PRETO)))
    ws.freeze_panes = "I3"; ws.auto_filter.ref = f"A2:{get_column_letter(len(cols))}{ult}"
    ws.column_dimensions.group("Z", "AD", hidden=False, outline_level=1)

    # ── Roteiro ──
    ro = wb.create_sheet("Roteiro"); ro.sheet_view.showGridLines = False; ro.column_dimensions["A"].width = 3; ro.column_dimensions["B"].width = 34; ro.column_dimensions["C"].width = 100
    blocos = [
        ("Abertura (com apresentação da D&S)", "Bom dia, [NOME]. Aqui é a Jenifer, da Save, parceira da D&S. O [CONSULTOR] da D&S sugeriu que eu falasse com você. Trabalhamos com empresas de [SEGMENTO] verificando se há créditos de PIS/COFINS que ficaram para trás nos últimos cinco anos. Você tem dois minutos?"),
        ("Abertura (sem apresentação)", "Bom dia. Aqui é a Jenifer, da Save, parceira da D&S, aqui de [CIDADE]. Trabalhamos com empresas de [SEGMENTO] no Lucro Real verificando se há créditos de PIS/COFINS que ficaram para trás. Com quem eu falo sobre a parte fiscal da empresa?"),
        ("Gancho", "Use o texto da coluna \"Gancho para abrir a conversa\" da linha. Ele é por segmento e não cita valor nem cliente."),
        ("Objetivo da ligação", "Marcar 30 minutos com o sócio ou o responsável financeiro (e, se possível, o contador). Não é para explicar tese pelo telefone."),
        ("Fechamento", "Faz sentido uma conversa de 30 minutos para entendermos a operação e dizer se vale fazer o diagnóstico? Tenho [DIA/HORA] ou [DIA/HORA]. Se não fizer sentido, é só me dizer que não volto a ligar."),
        ("", ""),
        ("Perguntas de qualificação (uma por vez)", ""),
        ("R · Regime", "A empresa está no Lucro Real hoje? E nos últimos 5 anos?"),
        ("D · Decisor", "Quem decide sobre esse tipo de assunto? Quem mais precisa participar?"),
        ("A · Arquivos", "Vocês têm acesso às obrigações fiscais dos últimos 5 anos (EFD-Contribuições) e ao e-CAC, ou isso fica com o contador?"),
        ("C · Contador", "O contador é externo ou interno? Ele costuma participar dessas conversas?"),
        ("H · Histórico", "Vocês já fizeram alguma revisão de créditos? Com quem, de qual período e de quais temas?"),
        ("U · Urgência", "Há algo que torne o assunto importante agora, como caixa, investimento ou a reforma tributária?"),
        ("", ""),
        ("Objeções", ""),
        ("\"Meu contador já faz isso.\"", "Ótimo, o diagnóstico é complementar e o contador acompanha. Olhamos pontos específicos de [SEGMENTO] que costumam ficar fora da rotina."),
        ("\"Isso é arriscado com a Receita?\"", "Cada tema tem um grau de risco, e o técnico explica isso no diagnóstico antes de qualquer pedido. A decisão é sempre de vocês."),
        ("\"Quanto vou recuperar?\"", "Só dá para dizer depois do diagnóstico sobre os arquivos. Não trabalhamos com estimativa antes disso."),
        ("\"Não tenho tempo.\"", "Entendo. São 30 minutos, e depois o trabalho é feito sobre os arquivos, com pouca demanda do seu time. Prefere [DIA] ou [DIA]?"),
        ("\"Já fizemos com outra empresa.\"", "Faz sentido. Posso perguntar o período e os temas analisados? Às vezes ficam períodos ou temas de fora."),
        ("\"Manda por e-mail.\"", "Mando, sim. Para mandar algo útil: a empresa está no Lucro Real e quem cuida da parte fiscal? Posso já deixar uma data sugerida no e-mail?"),
        ("", ""),
        ("Não dizer", "Valor, percentual ou prazo; palavras de garantia ou de ausência de risco; nome de cliente, de parceiro ou caso real. Também não detalhar teses ao telefone: isso é do técnico na reunião."),
        ("Depois da reunião marcada", "Registrar no HubSpot (pipeline BDR) com o Master D&S, avisar a Daniela e mandar a confirmação na véspera."),
    ]
    for i, (a, b) in enumerate(blocos, 2):
        ca = ro.cell(i, 2, a); cb = ro.cell(i, 3, b)
        sec = a and not b
        ca.font = f(bold=True, size=12 if sec else 10, color=K["ouro_texto"][1:] if sec else PRETO); cb.font = f(size=10, color=PRETO)
        for c in (ca, cb): c.alignment = Alignment(wrap_text=True, vertical="top")
        if b: ca.border = cb.border = LINHA
    ro.cell(1, 2, "Roteiro da ligação").font = f(bold=True, size=16, color=PRETO)

    # ── Resumo (atualiza com o Status) ──
    rs = wb.create_sheet("Resumo"); rs.sheet_view.showGridLines = False
    rs.cell(1, 1, "Andamento da lista").font = f(bold=True, size=16, color=PRETO)
    rs.cell(2, 1, "Os números da coluna B atualizam sozinhos conforme o Status da aba Ligações.").font = f(size=10, color=CINZA)
    rs.cell(4, 1, "Status").font = rs.cell(4, 2).font = f(bold=True, color=PRETO); rs.cell(4, 2, "Empresas")
    for c in (rs.cell(4, 1), rs.cell(4, 2)): c.fill = fill(OURO)
    for k, st in enumerate(STATUS, 5):
        rs.cell(k, 1, st).font = f(size=10, color=PRETO); c = rs.cell(k, 2, f'=COUNTIF(Ligações!$C$3:$C${ult},A{k})'); c.font = Font(name=MONO, size=10)
    k = 5 + len(STATUS)
    rs.cell(k, 1, "Total").font = f(bold=True); rs.cell(k, 2, f"=SUM(B5:B{k-1})").font = Font(name=MONO, bold=True)
    rs.cell(k + 1, 1, "Retornos vencidos (até hoje)").font = f(size=10, color=PRETO)
    rs.cell(k + 1, 2, f'=COUNTIFS(Ligações!$C$3:$C${ult},"Retornar na data",Ligações!$F$3:$F${ult},"<="&TODAY())').font = Font(name=MONO, size=10)
    # por cidade × prioridade
    import collections
    cid = collections.Counter((p["municipio"], p["prio"]) for p in pros); cids = collections.Counter(p["municipio"] for p in pros)
    rs.cell(4, 4, "Cidade"); rs.cell(4, 5, "Prior. A"); rs.cell(4, 6, "Prior. B"); rs.cell(4, 7, "Prior. C"); rs.cell(4, 8, "Total")
    for j in range(4, 9): rs.cell(4, j).font = f(bold=True, color=PRETO); rs.cell(4, j).fill = fill(OURO)
    for k2, (c, n) in enumerate(cids.most_common(25), 5):
        rs.cell(k2, 4, titulo(c)).font = f(size=10)
        for j, t in enumerate("ABC", 5): rs.cell(k2, j, cid[(c, t)]).font = Font(name=MONO, size=10)
        rs.cell(k2, 8, n).font = Font(name=MONO, size=10, bold=True)
    seg = collections.Counter(setor(p["cnae"]) for p in pros)
    rs.cell(4, 10, "Segmento"); rs.cell(4, 11, "Empresas")
    for j in (10, 11): rs.cell(4, j).font = f(bold=True, color=PRETO); rs.cell(4, j).fill = fill(OURO)
    for k3, (sg, n) in enumerate(seg.most_common(), 5): rs.cell(k3, 10, sg).font = f(size=10); rs.cell(k3, 11, n).font = Font(name=MONO, size=10)
    for col, w in (("A", 30), ("B", 10), ("C", 3), ("D", 24), ("E", 9), ("F", 9), ("G", 9), ("H", 9), ("I", 3), ("J", 26), ("K", 10)): rs.column_dimensions[col].width = w

    wb.active = 1
    os.makedirs(saida, exist_ok=True)
    arq = os.path.join(saida, f"Prospecção D&S · Lote {lote} · {HOJE.isoformat()}.xlsx"); wb.save(arq)
    lotes[str(lote)] = [p["cnpj"] for p in pros]; json.dump(lotes, open(reg_lotes, "w"))
    # roteiro em texto para a auditoria de promessas
    open(os.path.join(S, "roteiro-auditoria.md"), "w").write("\n".join(f"{a}: {b}" for a, b in blocos) + "\n" + "\n".join(set(GANCHO.values()) | {GANCHO_PADRAO, URGENCIA}))
    print(arq, len(pros), "empresas ·", collections.Counter(p["prio"] for p in pros))


if __name__ == "__main__":
    lote = int(sys.argv[sys.argv.index("--lote") + 1]) if "--lote" in sys.argv else 1
    gerar(sys.argv[1], lote)
