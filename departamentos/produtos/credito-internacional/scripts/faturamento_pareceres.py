#!/usr/bin/env python3
"""Faturamento das empresas a partir dos pareceres e diagnósticos do técnico (v2, 02/10/2026).

Substitui a busca por frase pronta de `extrator_faturamento.py` (21 empresas) por um extrator de TABELAS.
Somente leitura e local: lê ~/agentes-partners/celulas/geovana/pareceres/textos, o download do HubSpot e a base
da Receita (cnpj.sqlite, read-only). Nada sai da máquina.

Como os números aparecem (amostra lida em 02/10/2026, ~60 textos de modelos e técnicos diferentes):
  T1 "Qual faturamento da empresa? 2019: 405.854,00 2020: ... Obs.: média estimativa de faturamento por mês"  -> média mensal por ano
  T2 "Qual faturamento da empresa? Rótulos de Linha Soma de Vlr Operação 2022 5.241.842,10R$ ... Total Geral"   -> soma anual (tabela dinâmica do Excel)
  T3 "Faturamento da empresa Pagamento PIS e COFINS 2019 765.790,26 R$ ... MÉDIA FATURAMENTO MENSAL"           -> rótulo DEPOIS da tabela (print do Excel com OCR)
  T4 "... 2019 3.457.673,43R$ ... TOTAL 36.498.807,76R$ FATURAMENTO"                                           -> soma anual, rótulo depois
  T5 "MÉDIA DE FATURAMENTO DA EMPRESA POR ANO: PERÍODO FATURAMENTO 2021 R$ 6.500.204,07 ... TOTAL GERAL"         -> anual
  F  "Faturamento médio de R$ 578.699,20 Obs.: média de faturamento por mês" / "MEDIA MENSAL R$ ..." / "R$ R$ 186.124,70 mensal"  -> frase
  P  "ANO 5856 6912 Total Geral 2019 15.398,86R$ 3.343,17 R$ 18.742,03 R$" -> pagamentos de PIS/COFINS por código de DARF
     (5856/6912 não cumulativo; 8109/2172 cumulativo). Viram a BASE DE CÁLCULO implícita (pago ÷ 3,65% no cumulativo;
     pago ÷ 9,25% no não cumulativo = piso, porque o pago já é líquido dos créditos). Servem de dupla checagem.
  X  "Vlr BC PIS/Cofins" por ano em blocos de tese (MS coletivo, exclusão do ICMS) = base da TESE, não faturamento: descartado.
Onde o dado NÃO está no texto: na maior parte dos pareceres, os campos "Média de faturamento da empresa por ano:" e
"Pagamentos efetuados de PIS e COFINS por ano:" estão VAZIOS no texto porque a resposta é um print (imagem) colado no Word.
O leitor atual (pareceres.py) lê só o XML do Word e não faz OCR das imagens embutidas.

Uso:  python3 faturamento_pareceres.py            -> grava faturamento-pareceres.json (por raiz de CNPJ) e imprime a cobertura
"""
import glob, json, os, re, sqlite3, statistics, sys
from collections import Counter, defaultdict

H = os.path.expanduser
sys.path.insert(0, H("~/agentes-partners/lib"))
import partners_dados as PD  # noqa: E402

TXT = H("~/agentes-partners/celulas/geovana/pareceres/textos")
RES = H("~/agentes-partners/celulas/geovana/pareceres/resumos.json")
ENR = H("~/agentes-partners/departamentos/intel-comercial/enriquecimento-receita.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faturamento-pareceres.json")

NUM = r"(\d{1,3}(?:\.\d{3})+(?:,\d{1,3})?|\d{4,9},\d{1,3}|\d{1,3},\d{2})"
ROW = re.compile(r"(?<![\d/.\-])(20[12]\d)(?![\d/]|-\d)\s*[:\-–=]?\s*(?:R\$\s*)?" + NUM + r"\s*(?:R\$)?"
                 r"(\s*\((?:ref\.?|Ref\.?)\s*(\d{1,2})\s*m[eê]s(?:es)?[^)]*\))?"
                 r"((?:\s*(?:R\$\s*)?" + NUM + r"\s*(?:R\$)?){0,4})", re.I)
DARF = re.compile(r"\b(5856|6912|8109|2172|3373|6012|2089|2372|2484|5993|1410|2362|2172)\b")
CUMUL = {"8109", "2172"}; NCUM = {"5856", "6912"}
FAT_LBL = re.compile(r"faturamento|vl?r\.?\s*opera|valor\s+opera", re.I)
PAG_LBL = re.compile(r"paga(?:mento)?s?\s+(?:de\s+|efetuados\s+de\s+)?pis|pis\s+e\s+cofins\s+por\s+ano|provisionamento|pagamento\s+de\s+inss|pagamento\s+(?:de\s+)?irpj|recolhimento", re.I)
TESE_LBL = re.compile(r"vl?i?r\.?\s*bc\s*pis|bc\s+irpj|ms\s+coletivo|levantad|apurad[oa]\s+ref|exclus[ãa]o\s+do\s+icms\s+da\s+bc", re.I)
MENSAL = re.compile(r"mensal|por\s+m[eê]s|m[eé]dia\s+m[eê]s|meses\s+de\s+cada\s+ano|m[eé]dia\s+estimativa", re.I)
PERIODO = re.compile(r"per[ií]odo\s+de\s+apura[cç][aã]o\s*:?\s*(?:\d{2}/)?(\d{2})/(\d{4})\s*(?:a|à|A|até)\s*(?:\d{2}/)?(\d{2})/(\d{4})", re.I)
FRASES = [  # (regex, mensal?) — valor dito em frase, sem tabela
    (re.compile(r"faturamento\s+m[ée]dio\s+de\s+R\$\s*" + NUM + r"[^.;]{0,40}?(por\s+m[eê]s|mensal)?", re.I), None),
    (re.compile(r"qual\s+faturamento\s+m[ée]dio:?\s*R\$\s*" + NUM, re.I), True),
    (re.compile(r"(?:qual\s+[ée]\s+a\s+m[ée]dia\s+de\s+faturamento\s+da\s+empresa\??|qual\s+faturamento\s+da\s+empresa\??)\s*(?:R\$\s*)+" + NUM + r"\s*(mensal|por\s+m[eê]s)?", re.I), None),
    (re.compile(r"(?:qual\s+faturamento\s+da\s+empresa\??|faturamento\s+da\s+empresa)\s*(?:MEDIA|M[ÉE]DIA)\s+MENSAL\s*R\$\s*" + NUM, re.I), True),
    (re.compile(r"faturamento\s+(?:anual\s+)?(?:de\s+|aproximado\s+de\s+|em\s+torno\s+de\s+)R\$\s*([\d.,]+)\s*(milh[õo]es|mi\b|bilh[õo]es)", re.I), False),
]


def v(s):
    s = s.strip()
    if "." in s and "," in s: return float(s.replace(".", "").replace(",", "."))
    if "," in s: return float(s.replace(",", "."))
    return float(s.replace(".", ""))


def limpa(t):
    t = re.sub(r"[•]", " ", t)
    t = t.replace("aƟ", "ati")
    return re.sub(r"\s+", " ", t)


def tabelas(t):
    """Agrupa linhas 'ano valor' consecutivas (sem palavras entre elas) em tabelas, com o contexto antes e depois."""
    ms = list(ROW.finditer(t)); grupos = []
    for m in ms:
        if grupos and re.fullmatch(r"[\sR$]*", t[grupos[-1][-1].end():m.start()]) and m.start() - grupos[-1][-1].end() < 40:
            grupos[-1].append(m)
        else:
            grupos.append([m])
    out = []
    for i, g in enumerate(grupos):
        ini, fim = g[0].start(), g[-1].end()
        lim_a = grupos[i - 1][-1].end() if i else 0
        lim_d = grupos[i + 1][0].start() if i + 1 < len(grupos) else len(t)
        antes = t[max(lim_a, ini - 260):ini]; depois = t[fim:min(lim_d, fim + 120)]
        linhas = []
        for m in g:
            extra = re.findall(NUM, m.group(5) or "")
            linhas.append({"ano": int(m.group(1)), "v": v(m.group(2)), "ref": int(m.group(4)) if m.group(4) else None, "cols": 1 + len(extra),
                           "ult": v(extra[-1]) if extra else v(m.group(2))})
        out.append({"ini": ini, "fim": fim, "antes": antes, "depois": depois, "linhas": linhas, "texto": t[ini:fim]})
    return out


def classifica(tb):
    """faturamento / pagamento / tese / outro, e se é média mensal."""
    d = re.sub(r"^\s*(?:TOTAL(?:\s+GERAL)?|Total\s+Geral)\s*(?:R\$\s*)?" + NUM + r"\s*(?:R\$)?", "", tb["depois"]).strip()[:70]
    a = tb["antes"]
    soma_anual = bool(re.search(r"soma\s+de\s+vl?r\.?\s*opera|por\s+ano\s*:?\s*per[ií]odo", a[-120:], re.I))
    mensal_dep = bool(re.match(r"\(?\s*(m[ée]dia|mensal)", d, re.I) or MENSAL.search(d[:60]))
    multi = sum(1 for l in tb["linhas"] if l["cols"] > 1) >= max(1, len(tb["linhas"]) // 2)
    if DARF.search(a[-70:]) or (multi and not re.match(r"(m[ée]dia\s+)?faturamento", d, re.I)):
        return "pagamento", False, True
    if re.match(r"(M[ÉE]DIA\s+)?FATURAMENTO|Obs\.?:\s*m[ée]dia|Obs\.?:\s*estimativa|-\s*m[ée]dia\s+por\s+m[eê]s|\(?\s*m[ée]dia|media\s+m[eê]s", d, re.I):
        if soma_anual or re.search(r"soma\s+de\s+vl?r\.?\s*opera", a, re.I): return "faturamento", False, True  # "media mês" depois de soma anual é só um resumo
        return "faturamento", mensal_dep, True
    if re.match(r"PROVISIONAMENTO|Pagamento|PAGAMENTO", d):
        return "pagamento", False, True
    # rótulo mais próximo antes da tabela
    pos = {k: max([m.end() for m in r.finditer(a)] or [-1]) for k, r in (("faturamento", FAT_LBL), ("pagamento", PAG_LBL), ("tese", TESE_LBL))}
    k = max(pos, key=pos.get)
    if pos[k] < 0: return "outro", False, False
    if k == "faturamento":
        if re.search(r"R\$\s*" + NUM, a[pos[k]:]): return "outro", False, False  # o rótulo já foi respondido por um valor antes da tabela
        cauda = a[pos[k] - 60:]
        mensal = (bool(MENSAL.search(cauda)) or mensal_dep) and not soma_anual
        cue = mensal or soma_anual or bool(re.search(r"por\s+ano|anual|^\s*(TOTAL|Total)", cauda + " " + tb["depois"][:40]))
        ult = [m.group(0) for m in FAT_LBL.finditer(a)][-1]
        if "faturamento" not in ult.lower() and not re.search(r"faturamento", a, re.I):
            return "faturamento", mensal, "indireto"   # tabela 'Vlr Operação' longe da pergunta de faturamento: pode ser de entradas
        return "faturamento", mensal, cue
    return k, False, False


def periodo(t):
    m = PERIODO.search(t)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))) if m else None


def anual_de(tb, mensal, per):
    """(valor anual, ano de referência, série anualizada, observação)."""
    L = [l for l in tb["linhas"] if l["v"] > 0]
    if not L: return None
    serie, parcial = {}, set()
    for l in L:
        x = l["v"]; p_ = False
        if mensal:
            x *= 12
            if l["ref"] and l["ref"] <= 2 and len(L) > 1: x = None   # média de 1–2 meses: fraca, fica de fora
        elif l["ref"] and l["ref"] < 12: x = x / l["ref"] * 12 if l["ref"] >= 3 else None; p_ = True
        elif per and per[1] == per[3] == l["ano"] and per[2] - per[0] + 1 < 12:
            m_ = per[2] - per[0] + 1; x = x / m_ * 12 if m_ >= 3 else None; p_ = True   # período dentro de um só ano: anualiza
        elif per and l["ano"] == per[3] and per[2] < 12 and per[1] != per[3]:
            x = x / per[2] * 12 if per[2] >= 3 else None; p_ = True      # último ano do período, parcial: anualiza
        elif per and l["ano"] == per[1] and per[0] > 1 and per[1] != per[3]:
            meses = 13 - per[0]; x = x / meses * 12 if meses >= 3 else None; p_ = True  # primeiro ano parcial
        if x:
            serie[l["ano"]] = x
            if p_: parcial.add(l["ano"])
    if not serie: return None
    anos = sorted(serie); obs = []
    med = statistics.median(serie.values())
    if not mensal and len(anos) > 1 and anos[-1] not in parcial and serie[anos[-1]] < 0.6 * serie[anos[-2]] and not (per and per[3] == anos[-1] and per[2] == 12):
        obs.append(f"{anos[-1]} descartado (ano parcial: soma de poucos meses)"); anos.pop()
    while len(anos) > 1 and serie[anos[-1]] < 0.4 * med:
        obs.append(f"{anos[-1]} descartado (parcial ou atípico)"); anos.pop()
    completos = [a for a in anos if a not in parcial]
    if not mensal and completos and completos[-1] != anos[-1]:
        obs.append(f"{anos[-1]} parcial: usado o último ano completo"); anos = [a for a in anos if a <= completos[-1]]
    elif anos[-1] in parcial and not mensal:
        obs.append(f"{anos[-1]} anualizado pelos meses do período")
    ref = anos[-1]
    return serie[ref], ref, {a: round(serie[a]) for a in sorted(serie)}, "; ".join(obs)


def extrai_arquivo(f):
    t = limpa(open(os.path.join(TXT, f), errors="ignore").read())
    per = periodo(t); achados, pagos = [], []
    for tb in tabelas(t):
        tipo, mensal, cue = classifica(tb)
        if tipo == "faturamento":
            r = anual_de(tb, mensal, per)
            if not r: continue
            anual, ref, serie, obs = r
            if mensal and anual > 2e9: anual, serie, obs, mensal = anual / 12, {a: x / 12 for a, x in serie.items()}, "rótulo 'mensal' com valores de R$ 170 mi+/mês: lido como anual", False
            metodo = "tabela mensal somada (média mensal × 12)" if mensal else "total anual (tabela)"
            achados.append({"anual": round(anual, 2), "ano_ref": ref, "serie": serie, "metodo": metodo, "anos": len(serie), "obs": obs,
                            "trecho": (tb["antes"][-50:] + " " + tb["texto"])[-120:].strip(), "arquivo": f, "rotulo_explicito": cue is True, "rotulo": "indireto" if cue == "indireto" else "explícito" if cue else "ausente"})
        elif tipo == "pagamento":
            cods = set(DARF.findall(tb["antes"][-70:]))
            por_ano = {l["ano"]: l["ult"] for l in tb["linhas"]}
            if cods & {"3373", "6012", "2089", "2372", "2484", "5993"} and not cods & (CUMUL | NCUM): continue  # IRPJ/CSLL
            pagos.append({"cods": sorted(cods), "por_ano": por_ano, "cumulativo": bool(cods & CUMUL) and not cods & NCUM,
                          "nao_cumulativo": bool(cods & NCUM), "arquivo": f})
    for rx, mensal_fixo in FRASES:
        for m in rx.finditer(t):
            if len(m.groups()) >= 2 and m.group(2) and re.match(r"milh|mi\b|bilh", m.group(2), re.I):
                anual = v(m.group(1)) * (1e9 if m.group(2).lower().startswith("b") else 1e6); metodo = "frase (valor em milhões)"
            else:
                base = v(m.group(1))
                mensal = mensal_fixo if mensal_fixo is not None else bool(MENSAL.search(t[m.start():m.end() + 60]))
                anual = base * 12 if mensal else base
                cue_f = mensal or mensal_fixo is not None
                metodo = "frase (média mensal × 12)" if mensal else "frase (valor anual)"
            if 1e5 <= anual <= 5e9:
                achados.append({"anual": round(anual, 2), "ano_ref": per[3] if per else None, "serie": {}, "metodo": metodo, "anos": 0, "obs": "ano = fim do período de apuração",
                                "trecho": t[m.start():m.end() + 30][:120], "arquivo": f, "rotulo_explicito": (cue_f if "milh" not in metodo else True), "rotulo": "explícito" if (cue_f or "milh" in metodo) else "ausente"})
    return achados, pagos, per


def base_calculo(pagos):
    """Base de cálculo implícita nos pagamentos de PIS/COFINS (último ano com valor)."""
    for p in pagos:
        anos = [a for a in sorted(p["por_ano"]) if p["por_ano"][a] > 0]
        if not anos: continue
        vals = [p["por_ano"][a] for a in anos]; ref = anos[-1] if len(anos) == 1 or p["por_ano"][anos[-1]] >= 0.4 * statistics.median(vals) else anos[-2]
        pago = p["por_ano"][ref]
        if p["cumulativo"]: return {"bc": pago / 0.0365, "tipo": "cumulativo (pago ÷ 3,65%)", "ano": ref, "pago": pago, "arquivo": p["arquivo"]}
        if p["nao_cumulativo"]: return {"bc": pago / 0.0925, "tipo": "não cumulativo (pago ÷ 9,25%, piso: pago já é líquido de créditos)", "ano": ref, "pago": pago, "arquivo": p["arquivo"]}
        return {"bc": pago / 0.0925, "tipo": "códigos não informados (pago ÷ 9,25%, piso)", "ano": ref, "pago": pago, "arquivo": p["arquivo"]}
    return None


def main():
    _, HB = PD.ultimo_download(); N = {d["id"]: d for d in HB["negocios"]}
    E = json.load(open(ENR))["negocios"] if os.path.exists(ENR) else {}
    por_neg = defaultdict(list)
    for f in sorted(os.listdir(TXT)):
        por_neg[f.split("_")[0]].append(f)

    def cnpj_de(did):
        return PD.cnpj_digitos((E.get(did) or {}).get("cnpj") or N[did]["extras"].get("cnpj"))

    por_raiz = defaultdict(lambda: {"achados": [], "pagos": [], "negocios": set(), "arquivos_txt": 0, "arquivos_ilegiveis": 0})
    for did, fs in por_neg.items():
        if did not in N: continue
        rz = PD.raiz(cnpj_de(did))
        if not rz: continue
        R = por_raiz[rz]; R["negocios"].add(did)
        for f in fs:
            if f.endswith(".ilegivel"): R["arquivos_ilegiveis"] += 1; continue
            R["arquivos_txt"] += 1
            a, p, per = extrai_arquivo(f)
            for x in a: x["negocio"] = did; x["campo"] = f.split("_", 1)[1].rsplit("_", 1)[0]
            R["achados"] += a; R["pagos"] += p
    out = {}
    pref = {"total anual (tabela)": 0, "tabela mensal somada (média mensal × 12)": 0, "frase (média mensal × 12)": 1, "frase (valor anual)": 1, "frase (valor em milhões)": 2}
    for rz, R in por_raiz.items():
        bc = base_calculo(R["pagos"])
        if not R["achados"] and not bc: continue
        best = None
        if R["achados"]:
            # tabela com mais anos e ano de referência mais recente; parecer RT antes do anexo
            best = sorted(R["achados"], key=lambda x: (pref[x["metodo"]], -(x["ano_ref"] or 0), -x["anos"], x["campo"] != "parecer_rt", -x["anual"]))[0]
            outros = sorted({round(x["anual"]) for x in R["achados"]})
            best = {**best, "valores_encontrados": outros}
        out[rz] = {"melhor": best, "base_calculo": bc, "negocios": sorted(R["negocios"])}
    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1, default=str)
    print(OUT, "| raízes com faturamento no texto:", sum(1 for x in out.values() if x["melhor"]),
          "| só base de cálculo:", sum(1 for x in out.values() if not x["melhor"] and x["base_calculo"]),
          "| métodos:", dict(Counter(x["melhor"]["metodo"] for x in out.values() if x["melhor"])))


if __name__ == "__main__":
    main()
