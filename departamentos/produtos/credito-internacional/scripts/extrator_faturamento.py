"""Extrai do texto dos pareceres (celulas/geovana/pareceres/textos) o faturamento citado pelo técnico.
Somente leitura e local. Devolve faturamento ANUAL estimado, a série por ano e a forma (anual/mensal×12).

Formatos encontrados (amostra de 02/10/2026):
  "Qual faturamento da empresa? 2019: 1.829.660,54 ... Obs.: média estimativa de faturamento por mês"   -> mensal ×12
  "Qual faturamento da empresa? Rótulos de Linha Soma de Vlr Operação 2019 3.454.918,09R$ ..."          -> anual (soma do ano)
  "Faturamento médio de R$ 578.699,20 Obs.: média de faturamento por mês"                               -> mensal ×12
  "QUAL É A MÉDIA DE FATURAMENTO DA EMPRESA? R$ 186.124,70 mensal"                                     -> mensal ×12
Armadilhas: tabelas "FATURAMENTO MENSAL ANO 5856 6912" são pagamentos de PIS/COFINS por código de DARF (descartadas);
"Total Geral" é soma de vários anos (descartado); ano parcial "(ref. 3 meses)" em tabela anual é anualizado.
"""
import os, re

TEXTOS = os.path.expanduser("~/agentes-partners/celulas/geovana/pareceres/textos")
ANCORA = re.compile(r"(qual\s+(?:é\s+)?(?:a\s+)?(?:m[ée]dia\s+de\s+)?faturamento[^?:]{0,30}[?:]|faturamento\s+m[ée]dio|faturamento\s+mensal|faturamento\s+anual|receita\s+bruta\s+(?:anual|total|mensal)|faturamento\s+(?:anual\s+)?(?:de|aproximado de|em torno de)\s+R\$)", re.I)
CORTE = re.compile(r"(TODAS AS TESES|TESES APLICADAS|TESES N[ÃA]O|Teses n[ãa]o|PAGAMENTO DE|PAGA PIS|SISTEMA S|D[ÉE]BITOS|Identificamos|INSUMOS\s*:|DIESEL|SUBVEN|GEST[ÃA]O DE PASSIVO|EMPRESA J[ÁA]|CNPJ EM)", re.I)
DARF = re.compile(r"\b(5856|6912|8109|2172|1410|3373|6012|2372|2484)\b")
NUM = r"(\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?|\d+,\d{2})"
PAR = re.compile(r"\b(20[12]\d)\s*:?\s*(?:R\$\s*)?" + NUM + r"\s*(?:R\$)?\s*(\((?:ref\.?|Ref)\s*(\d{1,2})\s*m[eê]s(?:es)?\))?", re.I)
UNICO = re.compile(r"R\$\s*(?:R\$\s*)?" + NUM + r"|" + NUM + r"\s*(?:R\$)?\s*(?:m[ée]dia|mensal)", re.I)
MILHOES = re.compile(r"R\$\s*([\d.,]+)\s*(milh[õo]es|mi\b|bilh[õo]es|bi\b)", re.I)
MENSAL = re.compile(r"(por\s+m[êe]s|mensal|m[ée]dia\s+m[êe]s|ref\.?\s*\d+\s*meses de cada ano)", re.I)
MEDIA = re.compile(r"m[ée]di[ao]", re.I)
LOGO = re.compile(r"^\W{0,6}(?:MEDIA MENSAL|M[ÉE]DIA)?\W{0,6}R\$\s*(?:R\$\s*)?" + NUM, re.I)  # valor logo após a pergunta


def _v(s):
    return float(s.replace(".", "").replace(",", "."))


def extrair_texto(t):
    """Lista de achados [{anual, serie, forma, trecho}] num texto."""
    t = re.sub(r"[]", " ", t)
    t = re.sub(r"\s+", " ", t)
    achados = []
    for m in ANCORA.finditer(t):
        w = t[m.end(): m.end() + 450]
        c = CORTE.search(w)
        if c: w = w[: c.start()]
        janela = m.group(0) + w
        if DARF.search(janela[:200]) or "LINK Excel" in janela:          # tabela de pagamento de PIS/COFINS, não faturamento
            continue
        w2 = re.split(r"Total Geral|TOTAL\b", w)  # ignora totais de vários anos
        corpo = " ".join(p if i == 0 else re.sub(r"^\s*[\d.,]+\s*R?\$?", "", p) for i, p in enumerate(w2))
        # "média" sem "por ano" na pergunta = média mensal (padrão dos pareceres); "POR ANO" na pergunta = anual
        mensal = (bool(MENSAL.search(janela)) or (bool(MEDIA.search(janela)) and "por ano" not in m.group(0).lower())) and "Vlr Opera" not in janela
        serie = {}
        for y, n, _ref, meses in PAR.findall(corpo):
            v = _v(n)
            if not mensal and meses and int(meses) < 12:
                v = v / int(meses) * 12            # ano parcial em tabela anual: anualiza
            serie[int(y)] = max(serie.get(int(y), 0), v)
        mi = MILHOES.search(janela)
        logo = LOGO.search(w)
        if logo:                                  # valor dito logo após a pergunta vence tabelas que vêm depois
            serie = {}; base = _v(logo.group(1))
        elif serie:
            if mensal:                           # média mensal: média dos 2 últimos anos citados (evita pico isolado)
                ult = [serie[a] for a in sorted(serie)[-2:]]
                base = sum(ult) / len(ult)
            else:                                # soma anual: maior dos 3 últimos anos (o último costuma ser parcial)
                base = max(serie[a] for a in sorted(serie)[-3:])
        elif mi:
            base = _v(mi.group(1)) * (1e9 if mi.group(2).lower().startswith("b") else 1e6); mensal = False
        else:
            u = UNICO.search(w[:160])
            if not u: continue
            base = _v(u.group(1) or u.group(2))
        anual = base * 12 if mensal else base
        ambiguo = False
        if mensal and anual > 1e9:               # "média por mês" com valores de R$ 20 mi+/mês: lido como anual (conservador)
            mensal, anual, ambiguo = False, base, True
        if not (1e5 <= anual <= 5e9):          # fora disso é pagamento, erro de digitação ou outro número
            continue
        achados.append({"anual": round(anual, 2), "serie": {k: round(v * (12 if mensal else 1), 2) for k, v in sorted(serie.items())},
                        "forma": "média mensal × 12" if mensal else ("anual (rótulo 'por mês' ambíguo; lido como anual)" if ambiguo else "anual"), "trecho": janela[:220]})
    return achados


def por_negocio():
    """{deal_id: melhor achado} lendo todos os textos (parecer RT, anexo, parecer jurídico)."""
    out = {}
    for f in sorted(os.listdir(TEXTOS)):
        if not f.endswith(".txt"): continue
        did = f.split("_")[0]
        try: t = open(os.path.join(TEXTOS, f), errors="ignore").read()
        except OSError: continue
        for a in extrair_texto(t):
            a["arquivo"] = f
            if did not in out or a["anual"] > out[did]["anual"]:
                out[did] = a
    return out


_IDX = None


def mencoes(did):
    """Sinais de texto num negócio: exportação citada."""
    global _IDX
    if _IDX is None:
        _IDX = {}
        for f in os.listdir(TEXTOS):
            if f.endswith(".txt"): _IDX.setdefault(f.split("_")[0], []).append(f)
    txt = ""
    for f in _IDX.get(did, []):
        txt += " " + open(os.path.join(TEXTOS, f), errors="ignore").read()
    txt = re.sub(r"\s+", " ", txt)
    exp = re.search(r"(receitas?\s+(?:de|com)\s+exporta|faturamento[^.]{0,60}exporta|vendas?\s+(?:para o\s+)?(?:mercado\s+)?extern|exporta[çc][ãa]o\s+direta|imunidade[^.]{0,60}exporta|\bRE\b[^.]{0,30}exporta|exportadora)", txt, re.I)
    return {"exportacao": exp.group(0)[:120] if exp else None}


if __name__ == "__main__":
    r = por_negocio()
    print(len(r), "negócios com faturamento citado no parecer")
    for k, v in list(r.items())[:60]:
        print(k, f"{v['anual']:>16,.0f}", v["forma"], "|", v["trecho"][:150])
