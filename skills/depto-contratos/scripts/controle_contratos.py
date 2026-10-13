#!/usr/bin/env python3
"""Controle de Contratos — Departamento de Contratos (virtual), Área Partners · Save Company.

Determinístico e SÓ LEITURA: lê o extrato local do HubSpot (gerado pelo depto-resultados) e,
se existir, a base local da Receita (dados abertos do CNPJ, montada pelo depto-intel-comercial).
Não chama API nenhuma, não altera o HubSpot, não lê .env.

O que produz (em ~/agentes-partners/departamentos/contratos/):
  Controle-Contratos-AAAA-MM-DD.xlsx  ·  controle-contratos-AAAA-MM-DD.json (resumo para comparar edições)

Abas:
  Resumo            números da edição, fontes e limites
  Em contrato       negócios abertos nas etapas de contrato (Contrato Enviado, Pendência Fechamento, Contrato Assinado)
  Ganhos pendentes  negócios ganhos com pelo menos uma pendência de dado essencial ao contrato
  Conferência CNPJ  CNPJ normalizado, dígito verificador, razão social e situação oficiais, similaridade com o nome do negócio
  Por parceiro      pendências por parceiro (para a Daniela direcionar)
  Campos            dicionário: campos usados, preenchimento, e campos que FALTAM no HubSpot

Uso:
  python3 controle_contratos.py                    # último hubspot-*.json, todos os ganhos
  python3 controle_contratos.py --desde 2025-01-01 # só ganhos fechados a partir da data
  python3 controle_contratos.py --arquivo X.json --saida /tmp/teste --sem-receita
"""
import argparse, glob, json, os, re, sqlite3, unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime
from difflib import SequenceMatcher

HOME = os.path.expanduser("~")
HS_DIR = f"{HOME}/agentes-partners/departamentos/resultados/dados"
MAP = f"{HOME}/agentes-partners/departamentos/resultados/mapeamento-hubspot.json"
RECEITA_DB = f"{HOME}/agentes-partners/dados-publicos/receita/cnpj.sqlite"
OUT = f"{HOME}/agentes-partners/departamentos/contratos"
PORTAL = "47865021"
LINK = "https://app.hubspot.com/contacts/{p}/deal/{id}"

ETAPAS_CONTRATO = {"Contrato Enviado", "Pendência Fechamento", "Contrato Assinado"}
# Limiares de alerta (premissas v1 — confirmar com a área de Contratos real)
DIAS_ENVIADO_ALERTA = 15      # contrato enviado há mais de N dias sem virar assinado
DIAS_SEM_MEXER = 10           # negócio em etapa de contrato sem modificação há N dias
HONORARIO_ATIPICO = 0.50      # % honorário contratual acima disso → conferir (achado de 28/09: 61 casos > 50%)

# Campos que a área de Contratos precisaria e que NÃO existem no extrato do HubSpot (documentados na aba Campos)
CAMPOS_FALTANTES = [
    ("data_envio_contrato", "Data em que o contrato foi enviado ao cliente", "Medir o tempo até a assinatura e cobrar no D+X"),
    ("data_assinatura_contrato", "Data em que TODAS as partes assinaram", "Hoje usa-se a data de fechamento (closedate) como aproximação"),
    ("status_contrato", "Rascunho · Enviado · Assinado parcial · Assinado · Recusado · Distratado", "Hoje só a etapa do funil indica, e só nos abertos"),
    ("link_contrato_assinado", "Link do PDF assinado (plataforma de assinatura / Bitrix / Drive)", "Conferir que existe contrato para todo ganho"),
    ("plataforma_assinatura / id_envelope", "Onde e com que identificador o contrato foi enviado", "Controle de assinaturas sem abrir a plataforma"),
    ("signatario_nome / signatario_cargo", "Quem assina pelo cliente (representante legal ou procurador)", "Conferir contra o QSA / contrato social"),
    ("versao_modelo_contrato", "Qual modelo aprovado pelo Jurídico foi usado", "Rastrear minutas fora do padrão"),
    ("data_distrato / motivo_distrato", "Quando e por que o contrato foi encerrado", "Controle de distratos (hoje sem registro no HubSpot)"),
    ("termo_parceria_vigente (no parceiro)", "Termo de parceria/indicação assinado com o parceiro", "Conferir o parceiro correto e o % de repasse"),
    ("hs_v2_date_entered_<etapa>", "Data de entrada em cada etapa (propriedade nativa do HubSpot, não baixada hoje)", "Dias reais em 'Contrato Enviado'; pedir ao depto-resultados incluir no download"),
]


def norm_txt(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()
    s = re.sub(r"\[.*?\]|\(.*?\)", " ", s)
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    stop = {"NEGOCIO", "LTDA", "ME", "EPP", "EIRELI", "SA", "S", "A", "SLU", "CIA", "DE", "DA", "DO", "DOS", "DAS", "E", "EM", "RECORRENCIA", "LIMITADA", "COMERCIO", "COM"}
    return " ".join(t for t in s.split() if t not in stop)


def _sim(a, b):
    a, b = norm_txt(a), norm_txt(b)
    if not a or not b: return 0.0
    ta, tb = set(a.split()), set(b.split())
    jac = len(ta & tb) / max(1, min(len(ta), len(tb)))
    return max(SequenceMatcher(None, a, b).ratio(), jac)


def similaridade(nome, *oficiais):
    """Maior semelhança entre o nome do negócio (inteiro ou cada trecho separado por ' - ') e a razão social/nome fantasia."""
    partes = [nome or ""] + [x for x in re.split(r"\s[-–|]\s", nome or "") if x.strip()]
    return round(max((_sim(p, o) for p in partes for o in oficiais if o), default=0.0), 2)


def cnpj_norm(v):
    d = re.sub(r"\D", "", str(v or ""))
    return d.zfill(14) if d else ""


def cnpj_valido(c):
    if len(c) != 14 or c == c[0] * 14: return False
    def dv(base, pesos):
        s = sum(int(x) * p for x, p in zip(base, pesos)); r = s % 11
        return "0" if r < 2 else str(11 - r)
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]; p2 = [6] + p1
    return c[12] == dv(c[:12], p1) and c[13] == dv(c[:12] + c[12], p2)


def fmt_cnpj(c):
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}" if len(c) == 14 else c


def carregar_receita(cnpjs, usar=True):
    """Consulta read-only a base local. Retorna ({cnpj: dados}, fonte) ou ({}, motivo)."""
    if not usar: return {}, "desligado (--sem-receita)"
    if not os.path.exists(RECEITA_DB): return {}, "base local da Receita não encontrada"
    con = sqlite3.connect(f"file:{RECEITA_DB}?mode=ro", uri=True); con.row_factory = sqlite3.Row
    meta = {r["chave"]: r["valor"] for r in con.execute("SELECT * FROM meta")}
    out = {}; lst = list(cnpjs)
    for i in range(0, len(lst), 500):
        lote = lst[i:i + 500]
        sql = ("SELECT e.cnpj, e.matriz, e.situacao, e.data_situacao, e.uf, COALESCE(e.fantasia,'') fantasia, COALESCE(m.razao,'') razao, m.porte "
               "FROM estab e LEFT JOIN empresa m ON m.basico=e.basico WHERE e.cnpj IN (%s)" % ",".join("?" * len(lote)))
        for r in con.execute(sql, lote): out[r["cnpj"]] = dict(r)
    con.close()
    return out, f"{meta.get('fonte', 'Receita Federal · Dados Abertos do CNPJ')} (carregada em {meta.get('carregado_em', '?')})"


def dias(d_iso, hoje):
    if not d_iso: return None
    try: return (hoje - datetime.fromisoformat(d_iso[:10]).date()).days
    except ValueError: return None


def conferir(n, rec, roster_ok):
    """Pendências de um negócio. Retorna lista de (gravidade, texto) e a linha de conferência de CNPJ."""
    p = []; X = n.get("extras") or {}
    bruto = X.get("cnpj"); c = cnpj_norm(bruto); r = rec.get(c)
    conf = {"cnpj_hubspot": bruto or "", "cnpj_normalizado": fmt_cnpj(c), "zeros_perdidos": bool(bruto) and len(re.sub(r"\D", "", bruto)) < 14,
            "dv_ok": cnpj_valido(c) if c else False, "na_base": bool(r), "razao_oficial": (r or {}).get("razao", ""),
            "situacao": (r or {}).get("situacao", ""), "matriz_filial": (r or {}).get("matriz", ""), "uf_oficial": (r or {}).get("uf", ""),
            "similaridade": similaridade(n.get("nome"), r.get("razao"), r.get("fantasia")) if r else None}
    if not c: p.append(("🔴", "sem CNPJ"))
    elif not conf["dv_ok"]: p.append(("🔴", "CNPJ com dígito verificador inválido"))
    else:
        if conf["zeros_perdidos"]: p.append(("🟡", "CNPJ salvo sem os zeros à esquerda (corrigir o formato no HubSpot)"))
        if rec and not r: p.append(("🟡", "CNPJ não encontrado na base local da Receita (conferir no comprovante oficial)"))
        if r and r["situacao"] and r["situacao"] != "Ativa": p.append(("🔴", f"situação cadastral {r['situacao']} na Receita"))
        if r and conf["similaridade"] is not None and conf["similaridade"] < 0.5: p.append(("🔴", "nome do negócio diverge da razão social oficial"))
        if r and X.get("uf") and r.get("uf") and X["uf"].strip().upper() != r["uf"]: p.append(("🟡", f"UF do HubSpot ({X['uf']}) ≠ UF oficial ({r['uf']})"))
    if n.get("parceiro") == "Outros (fora do roster)":
        p.append(("🟡", "parceiro fora do roster Masters" + ("" if n.get("parceiro_bruto") else " e campo parceiro vazio")))
    elif not n.get("parceiro_bruto"): p.append(("🟡", "campo parceiro vazio (parceiro inferido)"))
    if n.get("hContr") is None: p.append(("🔴", "sem % de honorário contratual"))
    elif n["hContr"] == 0: p.append(("🟡", "% de honorário contratual = 0"))
    elif n["hContr"] > HONORARIO_ATIPICO: p.append(("🟡", f"% de honorário atípico ({n['hContr']:.0%}) — conferir contra o contrato"))
    if n.get("hParc") is None: p.append(("🟡", "sem % de repasse ao parceiro"))
    elif n["hParc"] > 1: p.append(("🔴", f"% de repasse ao parceiro > 100% ({n['hParc']:.0%}) — erro de digitação provável"))
    if not n.get("variante"): p.append(("🟡", "sem tese registrada (escopo do contrato)"))
    if not X.get("regime"): p.append(("⚪", "sem regime tributário"))
    return p, conf


def estilo(ws, larguras):
    from openpyxl.styles import Font, PatternFill, Alignment
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F3A5F"); c.alignment = Alignment(wrap_text=True, vertical="top")
    for i, w in enumerate(larguras, 1): ws.column_dimensions[ws.cell(1, i).column_letter].width = w
    ws.freeze_panes = "A2"
    if ws.max_row > 1: ws.auto_filter.ref = ws.dimensions


def linkar(ws, col):
    from openpyxl.styles import Font
    for row in ws.iter_rows(min_row=2, min_col=col, max_col=col):
        for c in row:
            if c.value and str(c.value).startswith("http"): c.hyperlink = c.value; c.value = "abrir"; c.font = Font(color="0563C1", underline="single")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arquivo"); ap.add_argument("--desde", help="ganhos fechados a partir de AAAA-MM-DD")
    ap.add_argument("--saida", default=OUT); ap.add_argument("--sem-receita", action="store_true")
    ap.add_argument("--hoje", help="data de referência AAAA-MM-DD (testes)")
    a = ap.parse_args()
    arq = a.arquivo or sorted(glob.glob(os.path.join(HS_DIR, "hubspot-*.json")))[-1]
    base = json.load(open(arq)); N = base["negocios"]
    hoje = datetime.fromisoformat(a.hoje).date() if a.hoje else date.today()
    roster = set((json.load(open(MAP)).get("escopo", {}).get("parceiros_roster") or {}).keys()) if os.path.exists(MAP) else set()

    abertos = [n for n in N if n["status"] == "aberto" and n.get("etapa") in ETAPAS_CONTRATO]
    ganhos = [n for n in N if n["status"] == "ganho" and (not a.desde or (n.get("fechado") or "") >= a.desde)]
    rec, fonte_rec = carregar_receita({cnpj_norm((n.get("extras") or {}).get("cnpj")) for n in abertos + ganhos} - {""}, not a.sem_receita)

    L_contrato, L_ganhos, L_cnpj = [], [], []
    por_parc = defaultdict(Counter); cont_pend = Counter()
    for n in abertos:
        pend, conf = conferir(n, rec, roster)
        X = n.get("extras") or {}; dc = dias(n.get("criado"), hoje); dm = dias(X.get("entrou_etapa") or X.get("ultima_atividade") or X.get("ultima_modificacao"), hoje)  # dias na etapa: a "última modificação" é atualizada o tempo todo pela sincronização com o Bitrix e escondia contratos parados
        alerta = []
        if n["etapa"] == "Contrato Assinado": alerta.append("🟡 assinado mas ainda não movido para Negócio Fechado")
        if n["etapa"] == "Contrato Enviado" and dm is not None and dm > DIAS_ENVIADO_ALERTA: alerta.append(f"🔴 enviado e sem movimento há {dm} dias")
        elif dm is not None and dm > DIAS_SEM_MEXER: alerta.append(f"🟡 na etapa há {dm} dias")
        L_contrato.append([n["etapa"], n["nome"], n["parceiro"], n.get("parceiro_bruto") or "", n["pipeline"], round(n["valor"] or 0, 2),
                           n.get("criado"), dc, (X.get("ultima_modificacao") or "")[:10], dm, "; ".join(alerta),
                           len([x for x in pend if x[0] == "🔴"]), "; ".join(f"{g} {t}" for g, t in pend), LINK.format(p=PORTAL, id=n["id"])])
        L_cnpj.append(["em contrato", n["nome"], conf["cnpj_hubspot"], conf["cnpj_normalizado"], "sim" if conf["dv_ok"] else "NÃO",
                       "sim" if conf["na_base"] else ("—" if not rec else "não"), conf["razao_oficial"], conf["similaridade"], conf["situacao"],
                       conf["matriz_filial"], conf["uf_oficial"], LINK.format(p=PORTAL, id=n["id"])])
    for n in ganhos:
        pend, conf = conferir(n, rec, roster)
        for g, t in pend:
            cont_pend[(g, re.sub(r"\s*\(.*?\)", "", t).strip())] += 1
            por_parc[n["parceiro"]][g] += 1
        por_parc[n["parceiro"]]["ganhos"] += 1
        if any(g in ("🔴", "🟡") for g, _ in pend): por_parc[n["parceiro"]]["com_pendencia"] += 1
        L_cnpj.append(["ganho", n["nome"], conf["cnpj_hubspot"], conf["cnpj_normalizado"], "sim" if conf["dv_ok"] else "NÃO",
                       "sim" if conf["na_base"] else ("—" if not rec else "não"), conf["razao_oficial"], conf["similaridade"], conf["situacao"],
                       conf["matriz_filial"], conf["uf_oficial"], LINK.format(p=PORTAL, id=n["id"])])
        if not any(g in ("🔴", "🟡") for g, _ in pend): continue
        L_ganhos.append([len([x for x in pend if x[0] == "🔴"]), n["nome"], n["parceiro"], n.get("parceiro_bruto") or "", round(n["valor"] or 0, 2),
                         n.get("fechado"), "campo inexistente", n.get("hContr"), n.get("hParc"), n.get("variante") or "",
                         "; ".join(f"{g} {t}" for g, t in pend), LINK.format(p=PORTAL, id=n["id"])])
    L_ganhos.sort(key=lambda r: (-r[0], -r[4]))
    L_contrato.sort(key=lambda r: (r[0], -r[5]))

    # dicionário de campos
    def fill(get):
        return f"{sum(1 for n in ganhos if get(n) not in (None, '')) / max(1, len(ganhos)):.0%}"
    usados = [("nome (dealname)", lambda n: n.get("nome"), "Nome do negócio; comparado com a razão social"),
              ("cnpj_", lambda n: (n.get("extras") or {}).get("cnpj"), "Conferência na Receita"),
              ("nome_do_parceiro", lambda n: n.get("parceiro_bruto"), "Parceiro correto (roster Masters)"),
              ("honorarios_contratuais", lambda n: n.get("hContr"), "% de êxito que vai no contrato"),
              ("honorarios_parceiro", lambda n: n.get("hParc"), "% de repasse ao parceiro"),
              ("teses_tributarias_aplicadas_neste_negocio_", lambda n: n.get("variante"), "Escopo (tese) do contrato"),
              ("qual_e_o_regime_tributario_da_empresa_", lambda n: (n.get("extras") or {}).get("regime"), "Contexto"),
              ("estado", lambda n: (n.get("extras") or {}).get("uf"), "Conferência de UF"),
              ("closedate", lambda n: n.get("fechado"), "Aproximação da data de assinatura"),
              ("parecer_juridico", lambda n: (n.get("extras") or {}).get("parecer_juridico"), "Link de documento jurídico — CONFIRMAR se é onde fica o contrato"),
              ("e_cac_liberado_", lambda n: (n.get("extras") or {}).get("ecac"), "Procuração e-CAC (pós-assinatura)")]
    L_campos = [[c, "sim", fill(g), obs] for c, g, obs in usados] + [[c, "NÃO", "—", f"{d}. Uso: {u}"] for c, d, u in CAMPOS_FALTANTES]

    L_parc = sorted([[p, c["ganhos"], c["com_pendencia"], f"{c['com_pendencia'] / max(1, c['ganhos']):.0%}", c["🔴"], c["🟡"],
                      sum(1 for r in L_contrato if r[2] == p)] for p, c in por_parc.items()], key=lambda r: -r[2])

    resumo = {"gerado_em": datetime.now().strftime("%Y-%m-%d %H:%M"), "referencia": hoje.isoformat(),
              "fonte_hubspot": f"{os.path.basename(arq)} (baixado em {base.get('baixado_em')}, {base.get('fonte')})", "fonte_receita": fonte_rec,
              "filtro_ganhos": f"fechados desde {a.desde}" if a.desde else "todos os ganhos do extrato",
              "em_contrato": {"negocios": len(abertos), "valor": round(sum(n["valor"] or 0 for n in abertos), 2),
                              "por_etapa": dict(Counter(n["etapa"] for n in abertos)), "com_alerta": sum(1 for r in L_contrato if r[10])},
              "ganhos": {"total": len(ganhos), "com_pendencia": len(L_ganhos), "com_pendencia_vermelha": sum(1 for r in L_ganhos if r[0] > 0),
                         "valor_com_pendencia": round(sum(r[4] for r in L_ganhos), 2)},
              "pendencias_mais_comuns": [{"gravidade": g, "pendencia": t, "qtd": q} for (g, t), q in cont_pend.most_common(15)],
              "cnpj": {"conferidos": len(L_cnpj), "dv_invalido": sum(1 for r in L_cnpj if r[4] == "NÃO"),
                       "zeros_perdidos": sum(1 for n in ganhos + abertos if (n.get("extras") or {}).get("cnpj") and len(re.sub(r'\D', '', n['extras']['cnpj'])) < 14),
                       "fora_da_base": sum(1 for r in L_cnpj if r[5] == "não"), "nao_ativos": sum(1 for r in L_cnpj if r[8] and r[8] != "Ativa")},
              "campos_faltantes": [c for c, _, _ in CAMPOS_FALTANTES],
              "limites": ["Sem data de assinatura no HubSpot: usa-se closedate como aproximação.",
                          "Sócios/representante legal NÃO estão na base local (não baixados por LGPD): conferência manual no QSA/contrato social.",
                          "Similaridade nome × razão é heurística: 🔴 significa 'conferir', não 'errado'.",
                          "Dias em etapa são aproximados pela última modificação do negócio (hs_lastmodifieddate)."]}

    from openpyxl import Workbook
    wb = Workbook(); ws = wb.active; ws.title = "Resumo"
    ws.append(["Item", "Valor"])
    linhas = [("Gerado em", resumo["gerado_em"]), ("Fonte HubSpot", resumo["fonte_hubspot"]), ("Fonte Receita", fonte_rec),
              ("Filtro dos ganhos", resumo["filtro_ganhos"]), ("", ""),
              ("Negócios em etapa de contrato", len(abertos)), ("Valor em etapa de contrato (R$)", resumo["em_contrato"]["valor"]),
              ("   por etapa", ", ".join(f"{k}: {v}" for k, v in resumo["em_contrato"]["por_etapa"].items())),
              ("   com alerta de prazo/parado", resumo["em_contrato"]["com_alerta"]), ("", ""),
              ("Ganhos analisados", len(ganhos)), ("Ganhos com pendência", len(L_ganhos)),
              ("   com pendência 🔴 (bloqueia conferência)", resumo["ganhos"]["com_pendencia_vermelha"]),
              ("Valor (amount) dos ganhos com pendência (R$)", resumo["ganhos"]["valor_com_pendencia"]), ("", ""),
              ("CNPJ com DV inválido", resumo["cnpj"]["dv_invalido"]), ("CNPJ salvo sem zeros à esquerda", resumo["cnpj"]["zeros_perdidos"]),
              ("CNPJ fora da base local", resumo["cnpj"]["fora_da_base"]), ("CNPJ não ativo na Receita", resumo["cnpj"]["nao_ativos"]), ("", ""),
              ("Pendências mais comuns (ganhos)", "")] + [(f"   {d['gravidade']} {d['pendencia']}", d["qtd"]) for d in resumo["pendencias_mais_comuns"]] + \
             [("", ""), ("Limites desta edição", "")] + [("   •", t) for t in resumo["limites"]] + \
             [("", ""), ("Regra", "Só leitura. Nada foi alterado no HubSpot. Correções: o time faz, com o link de cada negócio.")]
    for l in linhas: ws.append(list(l))
    estilo(ws, [48, 110]); ws.auto_filter.ref = None

    for titulo, cab, dados, larg, col_link in [
        ("Em contrato", ["Etapa", "Negócio", "Parceiro", "Parceiro (campo)", "Pipeline", "Valor (R$)", "Criado", "Dias desde criação",
                         "Última modificação", "Dias sem modificação", "Alerta", "Qtd 🔴", "Pendências de dado", "HubSpot"], L_contrato,
         [18, 42, 20, 20, 20, 13, 11, 10, 12, 10, 40, 7, 70, 8], 14),
        ("Ganhos pendentes", ["Qtd 🔴", "Negócio", "Parceiro", "Parceiro (campo)", "Valor (R$)", "Fechado (proxy assinatura)", "Data de assinatura",
                              "% honorário", "% parceiro", "Tese", "Pendências", "HubSpot"], L_ganhos,
         [7, 42, 20, 20, 13, 12, 14, 10, 10, 30, 80, 8], 12),
        ("Conferência CNPJ", ["Grupo", "Negócio", "CNPJ no HubSpot", "CNPJ normalizado", "DV ok", "Na base Receita", "Razão social oficial",
                              "Similaridade nome×razão", "Situação", "Matriz/Filial", "UF oficial", "HubSpot"], L_cnpj,
         [11, 42, 18, 20, 7, 9, 42, 11, 10, 10, 8, 8], 12),
        ("Por parceiro", ["Parceiro", "Ganhos", "Ganhos com pendência", "% com pendência", "Pendências 🔴", "Pendências 🟡", "Em contrato agora"], L_parc,
         [26, 9, 12, 10, 10, 10, 10], None),
        ("Campos", ["Campo HubSpot", "Existe no extrato?", "Preenchido nos ganhos", "Uso / observação"], L_campos, [40, 12, 12, 110], None)]:
        w = wb.create_sheet(titulo); w.append(cab)
        for r in dados: w.append(r)
        estilo(w, larg)
        if col_link: linkar(w, col_link)
        for col in ("Valor (R$)",):
            if col in cab:
                i = cab.index(col) + 1
                for row in w.iter_rows(min_row=2, min_col=i, max_col=i):
                    for c in row: c.number_format = '#,##0.00'
        for col in ("% honorário", "% parceiro"):
            if col in cab:
                i = cab.index(col) + 1
                for row in w.iter_rows(min_row=2, min_col=i, max_col=i):
                    for c in row: c.number_format = '0%'

    os.makedirs(a.saida, exist_ok=True)
    fx = os.path.join(a.saida, f"Controle-Contratos-{hoje.isoformat()}.xlsx"); wb.save(fx)
    fj = os.path.join(a.saida, f"controle-contratos-{hoje.isoformat()}.json")
    json.dump(resumo, open(fj, "w"), ensure_ascii=False, indent=1)
    print(f"Em contrato: {len(abertos)} negócios (R$ {resumo['em_contrato']['valor']:,.2f}), {resumo['em_contrato']['com_alerta']} com alerta")
    print(f"Ganhos: {len(ganhos)} analisados, {len(L_ganhos)} com pendência ({resumo['ganhos']['com_pendencia_vermelha']} com 🔴)")
    print(f"CNPJ: {resumo['cnpj']}  ·  Receita: {fonte_rec}")
    print(f"→ {fx}\n→ {fj}")


if __name__ == "__main__":
    main()
