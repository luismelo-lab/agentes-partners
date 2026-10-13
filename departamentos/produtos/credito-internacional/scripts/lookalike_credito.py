#!/usr/bin/env python3
"""Crédito internacional · faturamento dos ganhos, lookalike, perdidos semelhantes e prospects fora da base (02/10/2026).

Dados & BI + Inteligência Comercial + Recuperador (célula da Geovana). Somente leitura e local:
  HubSpot (download do dia), enriquecimento da Receita, base da Receita (cnpj.sqlite em modo read-only),
  textos dos pareceres (via faturamento_pareceres.py). Nenhum CNPJ sai da máquina; sem sócios nem CPF; não lê .env.

Uso:  python3 faturamento_pareceres.py && python3 lookalike_credito.py
Saídas: Faturamento-Clientes-Ganhos.xlsx, Lookalike-Perdidos.xlsx, Prospects-Semelhantes.xlsx (OneDrive, com cópia local)
        e lookalike-agregados.json (só contagens, sem nomes) para os documentos 10, 11 e 12.
"""
import json, math, os, re, shutil, sqlite3, statistics, subprocess, sys
from collections import Counter, defaultdict
from datetime import date

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser("~/agentes-partners/lib")); sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.expanduser("~/.claude/skills/recuperador/scripts"))
import partners_dados as PD  # noqa: E402
import base_clientes as BC  # setor(), regiao(), EXPORT_CNAE  # noqa: E402
import extrator_faturamento as EF  # mencoes() de exportação  # noqa: E402
import fila as FILA  # parecido(), linha_matriz() do Recuperador  # noqa: E402

AP = PD.AP
PASTA = os.path.join(AP, "departamentos/produtos/credito-internacional")
TXT = os.path.join(AP, "celulas/geovana/pareceres/textos")
RESUMOS = os.path.join(AP, "celulas/geovana/pareceres/resumos.json")
ENR = os.path.join(AP, "departamentos/intel-comercial/enriquecimento-receita.json")
FAT = os.path.join(AQUI, "faturamento-pareceres.json")
AGG = os.path.join(AQUI, "lookalike-agregados.json")
HOJE = date.today()
MASTERS = ["D&S", "G.S.H", "JGM", "EMPRESARIAL CARDOSO", "AGILE", "COSTA e GAUDENCIO", "ORTECONTE", "ASSECONT", "GERSON"]
CORTE, PISO = 50e6, 30e6
PORTE = {"Microempresa": "ME", "Empresa de Pequeno Porte": "EPP", "Demais": "Demais"}


# ---------------------------------------------------------------- Receita (em memória)
def carrega_receita():
    con = sqlite3.connect(f"file:{PD.RECEITA_DB}?mode=ro", uri=True)
    emp = {b: (r, n, c or 0.0, p) for b, r, n, c, p in con.execute("select basico, razao, natureza, capital, porte from empresa")}
    simp = {b: s for b, s in con.execute("select basico, simples from simples")}
    cnae_d = {c: d for c, d in con.execute("select codigo, descricao from ref where tipo='cnae'")}
    mun_d = {c: d for c, d in con.execute("select codigo, descricao from ref where tipo='municipio'")}
    matriz, n_est, ufs_est = {}, Counter(), defaultdict(set)
    cob = {"estab": 0, "ativas": 0, "por_uf": Counter(), "situacao": Counter(), "cnae2": Counter()}
    for cnpj, b, mt, fan, sit, ini, cnae, sec, uf, mun, cep, noh in con.execute(
            "select cnpj, basico, matriz, fantasia, situacao, inicio, cnae, cnaes_sec, uf, municipio, cep, no_hubspot from estab"):
        cob["estab"] += 1; cob["situacao"][sit] += 1; cob["por_uf"][uf] += 1; cob["cnae2"][(cnae or "")[:2]] += 1
        if sit == "Ativa": n_est[b] += 1; ufs_est[b].add(uf)
        if mt == "matriz":
            matriz[b] = {"cnpj": cnpj, "fantasia": fan, "situacao": sit, "inicio": ini, "cnae": cnae or "", "cnaes_sec": sec or "", "uf": uf,
                         "mun_cod": mun, "municipio": mun_d.get(mun, ""), "cep": cep or "", "no_hubspot": noh}
    meta = dict(con.execute("select chave, valor from meta").fetchall()); con.close()
    return emp, simp, cnae_d, mun_d, matriz, n_est, ufs_est, cob, meta


def idade(ini):
    try: return max(0.0, (HOJE - date(int(ini[:4]), int(ini[4:6]), int(ini[6:8]))).days / 365.25)
    except (TypeError, ValueError): return None


def micro(uf, municipio, cep):
    """Microrregião: os recortes do café em MG pelo município; no resto, a região postal (UF + 3 primeiros dígitos do CEP)."""
    r = BC.regiao(uf, municipio) if uf == "MG" else ""
    if r and r != "MG · outras": return r
    return f"{uf} · CEP {cep[:3]}xx" if cep else (uf or "")


def exportador(cnae, sec, nome, did_list=()):
    if any((cnae or "").startswith(p) for p in BC.EXPORT_CNAE): return "provável (CNAE de cadeia exportadora)"
    if re.search(r"export", PD.norm(nome)): return "sim (razão social)"
    for did in did_list:
        if EF.mencoes(did)["exportacao"]: return "sim (parecer cita exportação)"
    return "não identificado"


# ---------------------------------------------------------------- HubSpot por empresa (raiz)
def empresas_hubspot(N, E, R):
    def cnpj_de(d): return PD.cnpj_digitos((E.get(d["id"]) or {}).get("cnpj") or d["extras"].get("cnpj"))
    g = defaultdict(list)
    for d in N:
        rz = PD.raiz(cnpj_de(d))
        if rz: g[rz].append(d)
    out = {}
    for rz, ds in g.items():
        ganhos = [d for d in ds if d["status"] == "ganho"]; perd = [d for d in ds if d["status"] == "perdido"]; abert = [d for d in ds if d["status"] == "aberto"]
        st = "ganho" if ganhos else "aberto" if abert and not perd else "perdido" if perd else "aberto"
        if ganhos and False: pass
        base = ganhos or (perd if st == "perdido" else abert) or ds
        par = Counter(d["parceiro"] for d in base).most_common(1)[0][0]
        if st == "ganho": ref = max(ganhos, key=lambda d: d["valor"] or 0)
        elif st == "perdido": ref = max(perd, key=lambda d: (d["fechado"] or d["criado"] or ""))
        else: ref = max(abert, key=lambda d: d["criado"] or "")
        reg = next((d["extras"].get("regime") for d in sorted(ds, key=lambda d: d["criado"] or "", reverse=True) if d["extras"].get("regime")), "") or ""
        res = [R[d["id"]] for d in ds if d["id"] in R and R[d["id"]].get("motivo") is not None or (d["id"] in R and R[d["id"]].get("sinal_reanalise"))]
        out[rz] = {"raiz": rz, "status": st, "deals": ds, "ref": ref, "parceiro": par, "regime": reg.strip(), "cnpj": cnpj_de(ref),
                   "credito": max([d["valor"] or 0 for d in ganhos] or [0]), "credito_total": sum(d["valor"] or 0 for d in ganhos),
                   "valor_perdido_max": max([d["valor"] or 0 for d in perd] or [0]), "tem_aberto": bool(abert),
                   "credito_ref": max([d["valor"] or 0 for d in ganhos] or [0]) or max([d["valor"] or 0 for d in perd + abert] or [0]),
                   "parecer": res[0] if res else None, "link": PD.LINK.format(ref["id"]), "nome": ref["nome"],
                   "uf_hs": ref["extras"].get("uf"), "cidade_hs": ref["extras"].get("cidade"), "cafe": any(PD.e_cafe(d) for d in ds)}
    return out


# ---------------------------------------------------------------- qualidade do faturamento
def confianca(f, emp_info, simples, credito, bc):
    """Nível base pelo método; cada checagem que falha derruba um nível; base de cálculo coerente sobe um."""
    m = f["metodo"]; checks = []
    nivel = 2 if (m.startswith(("total anual", "tabela mensal")) and f["anos"] >= 3) else 1
    anual = f["anual"]
    if f.get("rotulo") == "indireto":
        nivel = min(nivel, 1); checks.append("tabela 'Vlr Operação' sem a pergunta de faturamento ao lado (pode ser de entradas): conferir")
    elif f.get("rotulo") == "ausente" or not f.get("rotulo_explicito", True):
        nivel = min(nivel, 0)
        if credito and credito > 0 and m.startswith("total anual") and f.get("serie"):
            r1, r12 = credito / anual, credito / (anual * 12)
            ok1, ok12 = 0.002 <= r1 <= 0.8, 0.002 <= r12 <= 0.8
            if ok12 and not ok1:   # só a leitura como média mensal é coerente com o crédito
                anual *= 12; f["anual"] = anual; f["metodo"] = "tabela mensal somada (média mensal × 12)"; f["serie"] = {a: v * 12 for a, v in f["serie"].items()}
                checks.append("rótulo mensal/anual ausente: lido como MÉDIA MENSAL porque só essa leitura é coerente com o crédito recuperado")
            else: checks.append("rótulo mensal/anual ausente no texto (lido como anual; conferir)")
        else: checks.append("rótulo mensal/anual ausente no texto (lido como anual; conferir)")
    if bc:
        r = anual / bc["bc"] if bc["bc"] else None
        if r is not None:
            if bc["tipo"].startswith("cumulativo"):
                ok = 0.7 <= r <= 3.0; checks.append(f"base de cálculo (cumulativo): faturamento ÷ BC = {r:.2f} {'ok' if ok else 'FORA'}")
                if ok and 0.8 <= r <= 1.5: nivel += 1
                elif not ok: nivel -= 1
            else:
                ok = r >= 0.8; checks.append(f"base de cálculo (piso pelo PIS/COFINS pago): faturamento ÷ piso = {r:.1f} {'ok' if ok else 'FORA (abaixo do piso)'}")
                if not ok: nivel -= 1
    if credito and credito > 0:
        r = credito / anual
        ok = 0.002 <= r <= 0.8
        checks.append(f"crédito recuperado ÷ faturamento anual = {r:.1%} {'ok' if ok else 'FORA'}")
        if not ok: nivel -= 1
    porte = PORTE.get(emp_info[3] if emp_info else None)
    if simples == "S" and anual > 4.8e6 * 1.5: checks.append("optante do Simples com faturamento acima do teto: conferir"); nivel -= 1
    elif porte == "Demais" and anual < 0.36e6: checks.append("porte 'Demais' com faturamento de microempresa: conferir"); nivel -= 1
    elif porte == "ME" and anual > 4.8e6: checks.append("porte ME na Receita com faturamento acima de R$ 4,8 mi: porte desatualizado (sinal fraco)")
    else: checks.append(f"porte {porte or 's/d'} coerente")
    if m.startswith(("tabela mensal", "frase (média")) and anual >= 200e6:
        checks.append(f"média mensal muito alta: conferir se a tabela não é anual (seria R$ {anual/12/1e6:.0f} mi/ano)"); nivel -= 1
    if f.get("serie") and len(f["serie"]) >= 3:
        vals = list(f["serie"].values())[-3:]; cv = statistics.pstdev(vals) / statistics.mean(vals)
        if cv > 0.6: checks.append(f"série volátil (CV {cv:.2f})"); nivel -= 1
    return ["baixa", "média", "alta"][max(0, min(2, nivel))], checks


# ---------------------------------------------------------------- modelo (kNN e regressão, à mão com numpy)
GRUPOS = ["Café", "Frigoríficos (abate/indústria de carnes)", "Carnes · atacado", "Indústria de alimentos e bebidas",
          "Atacado de alimentos e mercadorias", "Supermercados e varejo alimentar", "Agro, produtores e insumos agropecuários"]


def vetor(x):
    """Variáveis medidas na Receita (servem para ganhos, perdidos e prospects)."""
    cap = x.get("capital") or 0
    p = x.get("porte")
    s = x.get("setor") if x.get("setor") in GRUPOS else "Outros"
    return np.array([math.log10(max(cap, 1e3)), 1.0 if p == "Demais" else 0.0, 1.0 if p == "EPP" else 0.0,
                     math.log10(1 + (x.get("idade") or 10)), math.log10(x.get("n_estab") or 1), 1.0 if x.get("sa") else 0.0] +
                    [1.0 if s == g else 0.0 for g in GRUPOS])


PESOS = np.array([1.6, 1.0, 0.4, 0.6, 1.2, 0.6] + [0.7] * len(GRUPOS))


class Modelo:
    def __init__(self, X, y, k=7, lam=1.0):
        self.mu = X.mean(0); self.sd = X.std(0) + 1e-9; self.k = k
        self.Z = (X - self.mu) / self.sd * PESOS; self.y = y
        A = np.c_[np.ones(len(X)), (X - self.mu) / self.sd]
        self.beta = np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]) * np.r_[0, np.ones(A.shape[1] - 1)], A.T @ y)

    def knn(self, x, excluir=None):
        z = (x - self.mu) / self.sd * PESOS; d = np.sqrt(((self.Z - z) ** 2).sum(1))
        if excluir is not None: d[excluir] = np.inf
        idx = np.argsort(d)[:self.k]; w = 1 / (d[idx] + 0.3)
        return float((self.y[idx] * w).sum() / w.sum()), idx, d[idx]

    def ridge(self, x):
        return float(self.beta @ np.r_[1, (x - self.mu) / self.sd])

    def prever(self, x, excluir=None):
        k, idx, d = self.knn(x, excluir)
        return 0.5 * k + 0.5 * self.ridge(x), idx, d


def validacao(X, y, k, lam):
    """Leave-one-out: erro em log10 do faturamento para kNN, regressão e a média dos dois (o modelo usado)."""
    pred = {"kNN": [], "regressão": [], "kNN + regressão (usado)": [], "mediana (referência)": []}
    for i in range(len(y)):
        msk = np.ones(len(y), bool); msk[i] = False
        M = Modelo(X[msk], y[msk], k, lam)
        kn = M.knn(X[i])[0]; rg = M.ridge(X[i])
        pred["kNN"].append(kn); pred["regressão"].append(rg); pred["kNN + regressão (usado)"].append(0.5 * kn + 0.5 * rg)
        pred["mediana (referência)"].append(float(np.median(y[msk])))
    out = {}
    for nome, p in pred.items():
        e = np.array(p) - y
        alto_real = y >= math.log10(PISO); alto_prev = np.array(p) >= math.log10(PISO)
        out[nome] = {"MAE_log10": round(float(np.abs(e).mean()), 3), "fator_mediano": round(10 ** float(np.median(np.abs(e))), 2),
                     "dentro_fator_2": round(float((np.abs(e) <= math.log10(2)).mean()), 3), "dentro_fator_3": round(float((np.abs(e) <= math.log10(3)).mean()), 3),
                     "acerto_faixa_30mi": round(float((alto_real == alto_prev).mean()), 3),
                     "sensibilidade_30mi": round(float((alto_prev & alto_real).sum() / max(1, alto_real.sum())), 3),
                     "precisao_30mi": round(float((alto_prev & alto_real).sum() / max(1, alto_prev.sum())), 3),
                     "q10": float(np.quantile(e, 0.1)), "q90": float(np.quantile(e, 0.9))}
    return out


def faixa_fat(v):
    if v is None: return "s/d"
    return "≥ R$ 50 mi" if v >= 50e6 else "R$ 30–50 mi" if v >= 30e6 else "R$ 15–30 mi" if v >= 15e6 else "R$ 5–15 mi" if v >= 5e6 else "R$ 1–5 mi" if v >= 1e6 else "< R$ 1 mi"


def mi(v): return round(v / 1e6, 2) if v is not None else None


# ---------------------------------------------------------------- planilhas
def grava(destino_nome, abas, metodologia):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    wb = Workbook(); wb.remove(wb.active)
    H1 = Font(bold=True, color="FFFFFF"); HF = PatternFill("solid", fgColor="1F3864")
    for nome, cols, linhas, larg in abas:
        ws = wb.create_sheet(nome[:31]); ws.append(cols)
        for j, c in enumerate(cols, 1):
            x = ws.cell(row=1, column=j); x.font = H1; x.fill = HF; x.alignment = Alignment(wrap_text=True, vertical="center")
            ws.column_dimensions[get_column_letter(j)].width = larg.get(c, 16)
        ws.row_dimensions[1].height = 34
        for i, l in enumerate(linhas, 2):
            ws.append([l.get(c) for c in cols])
            for c in cols:
                if c.startswith("link") and l.get(c):
                    x = ws.cell(row=i, column=cols.index(c) + 1); x.hyperlink = l[c]; x.font = Font(color="1F5FBF", underline="single")
        ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{max(2, len(linhas) + 1)}"; ws.freeze_panes = "C2"
    ws = wb.create_sheet("Metodologia"); ws.append(["Tema", "Descrição"])
    for j in (1, 2): ws.cell(row=1, column=j).font = H1; ws.cell(row=1, column=j).fill = HF
    for l in metodologia: ws.append(l)
    for r in ws.iter_rows(min_row=2):
        for c in r: c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions["A"].width = 34; ws.column_dimensions["B"].width = 130; ws.freeze_panes = "A2"
    area = subprocess.run([sys.executable, os.path.join(AP, "lib/caminhos.py"), "credito"], capture_output=True, text=True, check=True).stdout.strip()  # sem a pasta do OneDrive, para (antes gravava no diretório atual)
    destino = os.path.join(area, destino_nome)
    os.makedirs(os.path.dirname(destino), exist_ok=True); wb.save(destino)
    shutil.copy2(destino, os.path.join(PASTA, destino_nome))
    return destino


def cnpj_fmt(c):
    c = PD.cnpj_digitos(c)
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}" if len(c) == 14 else c


# ---------------------------------------------------------------- principal
def main():
    _, HB = PD.ultimo_download(); N = HB["negocios"]
    E = json.load(open(ENR))["negocios"]; R = json.load(open(RESUMOS)); F = json.load(open(FAT))
    emp, simp, cnae_d, mun_d, matriz, n_est, ufs_est, cob, meta = carrega_receita()
    EMP = empresas_hubspot(N, E, R)
    RAIZES_HS = set(EMP)
    AG = {"gerado_em": HOJE.isoformat(), "hubspot": HB.get("baixado_em"), "receita": meta}

    # ---- atributos de cada empresa (Receita + HubSpot)
    def atributos(rz, nome=""):
        m = matriz.get(rz) or {}; e = emp.get(rz)
        if not m:  # fora da base local: usa o enriquecimento (só HubSpot)
            enr = next((E[d["id"]] for d in EMP[rz]["deals"] if d["id"] in E), {}) if rz in EMP else {}
            m = {"cnae": enr.get("cnae_oficial") or "", "uf": enr.get("uf_oficial"), "municipio": enr.get("municipio_oficial") or "", "inicio": enr.get("inicio_atividade"),
                 "situacao": enr.get("situacao"), "cep": "", "cnaes_sec": ""}
            e = e or (None, None, enr.get("capital_social") or 0, enr.get("porte_oficial"))
        st, prio = BC.setor(m.get("cnae"), nome or (e[0] if e else ""))
        return {"cnae": m.get("cnae") or "", "cnae_desc": cnae_d.get(m.get("cnae") or "", ""), "setor": st, "prio": prio, "cnae2": (m.get("cnae") or "")[:2],
                "uf": m.get("uf"), "municipio": m.get("municipio") or "", "cep": m.get("cep") or "", "micro": micro(m.get("uf"), m.get("municipio") or "", m.get("cep") or ""),
                "porte": PORTE.get(e[3]) if e else None, "capital": (e[2] if e else 0) or 0, "natureza": e[1] if e else None,
                "sa": bool(e and str(e[1] or "").startswith(("204", "205"))), "coop": bool(e and str(e[1] or "") == "2143"),
                "idade": idade(m.get("inicio")), "n_estab": n_est.get(rz, 1), "ufs_estab": len(ufs_est.get(rz, ())) or 1,
                "situacao": m.get("situacao"), "simples": simp.get(rz), "razao": e[0] if e else "", "matriz_cnpj": m.get("cnpj")}

    for rz, x in EMP.items(): x.update(atributos(rz, x["nome"]))

    # ---- A. faturamento dos ganhos
    ganhos = {rz: x for rz, x in EMP.items() if x["status"] == "ganho"}
    linhasA, sem = [], []
    rotulo_ausente = re.compile(r"^\s*$")
    for rz, x in EMP.items():
        f = (F.get(rz) or {}).get("melhor"); bc = (F.get(rz) or {}).get("base_calculo")
        x["fat"] = None
        if not f: continue
        f = dict(f); f["rotulo_explicito"] = f.get("rotulo_explicito", True)
        conf, checks = confianca(f, emp.get(rz), simp.get(rz), x["credito"] or None, bc)
        x["fat"] = f["anual"]; x["fat_conf"] = conf; x["fat_info"] = f; x["fat_checks"] = checks; x["fat_bc"] = bc
        x["fat_treino"] = conf in ("alta", "média") and not any(c.startswith("média mensal muito alta") for c in checks)
    for rz, x in ganhos.items():
        if x["fat"] is None: continue
        f = x["fat_info"]; did = f["negocio"]
        linhasA.append({"empresa": x["razao"] or x["nome"], "CNPJ": cnpj_fmt(x["cnpj"]), "setor": x["setor"], "CNAE": f"{x['cnae']} {x['cnae_desc']}".strip(),
                        "UF": x["uf"], "cidade": x["municipio"], "microrregião": x["micro"], "faturamento anual (R$)": round(x["fat"]), "faixa": faixa_fat(x["fat"]),
                        "ano de referência": f["ano_ref"], "método": f["metodo"], "confiança": x["fat_conf"],
                        "série por ano (R$ mi)": "; ".join(f"{a}: {v/1e6:.1f}" for a, v in f["serie"].items()) if f["serie"] else "",
                        "checagens": " · ".join(x["fat_checks"] + ([f["obs"]] if f.get("obs") else [])),
                        "base de cálculo implícita (R$)": round(x["fat_bc"]["bc"]) if x["fat_bc"] else None,
                        "trecho de apoio": re.sub(r"\s+", " ", f["trecho"])[:120], "arquivo de origem": f["arquivo"],
                        "negócio do arquivo": "este negócio" if did == x["ref"]["id"] else ("outro negócio da mesma empresa (" + next((d["status"] for d in x["deals"] if d["id"] == did), "?") + ")"),
                        "crédito recuperado (R$)": round(x["credito"]) if x["credito"] else None,
                        "crédito ÷ faturamento": round(x["credito"] / x["fat"], 4) if x["credito"] else None,
                        "regime": x["regime"], "porte (Receita)": x["porte"], "capital social (R$)": x["capital"] or None,
                        "parceiro": x["parceiro"], "link do HubSpot": x["link"]})
    linhasA.sort(key=lambda l: -l["faturamento anual (R$)"])

    # onde está o dado que falta (por empresa ganha)
    def onde(rz, x):
        ds = x["deals"]; ids = {d["id"] for d in ds}
        fs = [f for f in os.listdir(TXT) if f.split("_")[0] in ids] if False else TXT_IDX_get(ids)
        txts = [f for f in fs if f.endswith(".txt")]; ileg = [f for f in fs if f.endswith(".ilegivel")]
        campos = [(k, u.strip()) for d in ds for k in ("parecer_rt", "anexo_diagnostico", "parecer_juridico") for u in (d["extras"].get(k) or "").split(";") if u.strip()]
        hub = [c for c in campos if c[1].isdigit()]
        if txts:
            vazio = False
            for f in txts:
                t = open(os.path.join(TXT, f), errors="ignore").read()
                if re.search(r"(m[ée]dia\s+de\s+faturamento\s+da\s+empresa\s+por\s+ano|qual\s+(?:é\s+a\s+)?(?:m[ée]dia\s+de\s+)?faturamento|faturamento\s+da\s+empresa)", t, re.I):
                    vazio = True
            if vazio: return "campo de faturamento em branco no texto: a resposta é um print (imagem) colado no Word, sem OCR"
            if hub: return "texto lido não traz faturamento; há outro arquivo no HubSpot sem permissão de leitura"
            return "parecer lido não tem o campo de faturamento (modelo Prevenção Processual / relatório de teses)"
        if ileg: return "arquivo ilegível (imagem ou PDF digitalizado sem OCR)"
        if hub: return "arquivo no HubSpot pendente de permissão (escopo 'files')"
        if campos: return "link do Bitrix sem texto (falhou o download ou formato não lido)"
        return "card sem parecer anexado"
    IDX = defaultdict(list)
    for f in os.listdir(TXT): IDX[f.split("_")[0]].append(f)
    def TXT_IDX_get(ids): return [f for i in ids for f in IDX.get(i, [])]
    for rz, x in ganhos.items():
        if x["fat"] is not None: continue
        sem.append({"empresa": x["razao"] or x["nome"], "CNPJ": cnpj_fmt(x["cnpj"]), "setor": x["setor"], "UF": x["uf"], "cidade": x["municipio"],
                    "onde está o dado": onde(rz, x), "crédito recuperado (R$)": round(x["credito"]) if x["credito"] else None,
                    "porte (Receita)": x["porte"], "capital social (R$)": x["capital"] or None, "parceiro": x["parceiro"], "link do HubSpot": x["link"]})
    sem.sort(key=lambda l: (l["onde está o dado"], -(l["crédito recuperado (R$)"] or 0)))
    neg_ganhos = [d for d in N if d["status"] == "ganho"]
    neg_txt = sum(1 for d in neg_ganhos if any(f.endswith(".txt") for f in IDX.get(d["id"], [])))
    neg_pend = sum(1 for d in neg_ganhos if not any(f.endswith(".txt") for f in IDX.get(d["id"], [])) and any((d["extras"].get(k) or "").split(";")[0].strip().isdigit() for k in ("parecer_rt", "anexo_diagnostico", "parecer_juridico")))
    neg_sem = sum(1 for d in neg_ganhos if not any((d["extras"].get(k) or "").strip() for k in ("parecer_rt", "anexo_diagnostico", "parecer_juridico")))
    cA = Counter(l["confiança"] for l in linhasA)
    AG["A"] = {"negocios_ganhos": len(neg_ganhos), "negocios_ganhos_com_texto": neg_txt, "negocios_ganhos_pendentes_hubspot": neg_pend, "negocios_ganhos_sem_parecer": neg_sem,
               "empresas_ganhas": len(ganhos), "empresas_ganhas_com_texto": sum(1 for rz, x in ganhos.items() if TXT_IDX_get({d['id'] for d in x['deals']})),
               "empresas_ganhas_com_faturamento": len(linhasA), "empresas_todas_com_faturamento": sum(1 for x in EMP.values() if x["fat"] is not None),
               "confianca": dict(cA), "metodo": dict(Counter(l["método"] for l in linhasA)), "faixa": dict(Counter(l["faixa"] for l in linhasA)),
               "setor": dict(Counter(l["setor"] for l in linhasA)), "uf": dict(Counter(l["UF"] for l in linhasA)),
               "setor_mediana_mi": {s: round(statistics.median([l["faturamento anual (R$)"] for l in linhasA if l["setor"] == s]) / 1e6, 1) for s in {l["setor"] for l in linhasA}},
               "onde_falta": dict(Counter(l["onde está o dado"] for l in sem)),
               "onde_falta_credito_mi": {k: round(sum(l["crédito recuperado (R$)"] or 0 for l in sem if l["onde está o dado"] == k) / 1e6, 1) for k in {l["onde está o dado"] for l in sem}},
               "ref_ano": dict(Counter(l["ano de referência"] for l in linhasA)),
               "ratio_credito_mediana": round(statistics.median([l["crédito ÷ faturamento"] for l in linhasA if l["crédito ÷ faturamento"]]), 4) if linhasA else None,
               "acima_30mi": sum(1 for l in linhasA if l["faturamento anual (R$)"] >= PISO), "acima_50mi": sum(1 for l in linhasA if l["faturamento anual (R$)"] >= CORTE)}
    # amostra de conferência: 5 por confiança (as primeiras por ordem de arquivo, para ser reprodutível)
    amostra = []
    todos_fat = [{"confiança": x["fat_conf"], "arquivo de origem": x["fat_info"]["arquivo"], "faturamento anual (R$)": round(x["fat"]), "ano de referência": x["fat_info"]["ano_ref"],
                  "método": x["fat_info"]["metodo"], "setor": x["setor"], "UF": x["uf"], "trecho de apoio": x["fat_info"]["trecho"], "checagens": " · ".join(x["fat_checks"]), "status": x["status"]}
                 for x in EMP.values() if x["fat"] is not None]
    AG["A"]["todas_confianca"] = dict(Counter(l["confiança"] for l in todos_fat)); AG["A"]["todas_status"] = dict(Counter(l["status"] for l in todos_fat))
    for c in ("alta", "média", "baixa"):
        L = sorted([l for l in todos_fat if l["confiança"] == c], key=lambda l: l["arquivo de origem"])
        passo = max(1, len(L) // 5)
        amostra += [{"confiança": c, "arquivo": l["arquivo de origem"], "faturamento": l["faturamento anual (R$)"], "ano": l["ano de referência"], "método": l["método"],
                     "setor": l["setor"], "UF": l["UF"], "trecho": l["trecho de apoio"], "checagens": l["checagens"], "status": l["status"]} for l in L[::passo][:5]]
    AG["A"]["amostra_conferencia"] = amostra

    # ---- B. lookalike: perfis e modelo
    treino = [x for x in EMP.values() if x["fat"] is not None and x.get("fat_treino") and x["fat"] >= 1e5]
    X = np.array([vetor(x) for x in treino]); y = np.array([math.log10(x["fat"]) for x in treino])
    for i, x in enumerate(treino): x["_i"] = i
    melhor = None
    for k in (5, 7, 9):
        for lam in (1.0, 3.0, 10.0):
            v = validacao(X, y, k, lam)["kNN + regressão (usado)"]["MAE_log10"]
            if melhor is None or v < melhor[0]: melhor = (v, k, lam)
    _, K, LAM = melhor
    VAL = validacao(X, y, K, LAM)
    M = Modelo(X, y, K, LAM)
    q10, q90 = VAL["kNN + regressão (usado)"]["q10"], VAL["kNN + regressão (usado)"]["q90"]
    nomes_var = ["log capital", "porte Demais", "porte EPP", "log idade", "log nº estabelecimentos", "S.A."] + [f"setor: {g}" for g in GRUPOS]
    AG["B"] = {"n_treino": len(treino), "n_treino_ganhos": sum(1 for x in treino if x["status"] == "ganho"), "k": K, "lambda": LAM, "validacao": VAL,
               "coeficientes": {n: round(float(b), 3) for n, b in zip(["intercepto"] + nomes_var, M.beta)},
               "intervalo_log10": [round(q10, 3), round(q90, 3)]}

    # modelo 2 (só para quem tem crédito estimado no HubSpot): log10(faturamento) = a + b·log10(crédito), LOO
    t2 = [x for x in treino if (x.get("credito_ref") or 0) > 0]
    C2 = np.array([math.log10(x["credito_ref"]) for x in t2]); Y2 = np.array([math.log10(x["fat"]) for x in t2])
    err2 = []
    for i in range(len(t2)):
        msk = np.ones(len(t2), bool); msk[i] = False
        b2 = np.polyfit(C2[msk], Y2[msk], 1); err2.append(np.polyval(b2, C2[i]) - Y2[i])
    err2 = np.array(err2); B2 = np.polyfit(C2, Y2, 1); q10b, q90b = float(np.quantile(err2, 0.1)), float(np.quantile(err2, 0.9))
    e1 = []
    for x in t2:
        i = x["_i"] if "_i" in x else treino.index(x)
        msk = np.ones(len(y), bool); msk[i] = False
        e1.append(Modelo(X[msk], y[msk], K, LAM).prever(X[i])[0] - y[i])
    e1 = np.abs(np.array(e1))
    AG["B"]["modelo_credito"] = {"n": len(t2), "a": round(float(B2[1]), 3), "b": round(float(B2[0]), 3), "corr": round(float(np.corrcoef(C2, Y2)[0, 1]), 2),
                                 "MAE_log10": round(float(np.abs(err2).mean()), 3), "fator_mediano": round(10 ** float(np.median(np.abs(err2))), 2),
                                 "dentro_fator_2": round(float((np.abs(err2) <= math.log10(2)).mean()), 3),
                                 "mesmas_empresas_modelo_receita_MAE": round(float(e1.mean()), 3), "mesmas_empresas_modelo_receita_dentro_2x": round(float((e1 <= math.log10(2)).mean()), 3),
                                 "intervalo_log10": [round(q10b, 3), round(q90b, 3)]}

    def estima(x, excl=None):
        if (x.get("credito_ref") or 0) > 0:
            p = float(np.polyval(B2, math.log10(x["credito_ref"])))
            return 10 ** p, 10 ** (p - q90b), 10 ** (p - q10b), None, None

        p, idx, d = M.prever(vetor(x), excl)
        # o intervalo vem do erro da validação cruzada (percentis 10 e 90)
        return 10 ** p, 10 ** (p - q90), 10 ** (p - q10), idx, d

    # estimativa para todos os ganhos (para os perfis): faturamento real quando há; senão estimado
    for x in EMP.values():
        e_, lo, hi, _, _ = estima(x, excl=[x["_i"]] if "_i" in x else None)
        x["fat_est"], x["fat_lo"], x["fat_hi"] = e_, lo, hi
        x["fat_fonte"] = "crédito do HubSpot (modelo 2)" if (x.get("credito_ref") or 0) > 0 else "Receita (modelo 1: kNN + regressão)"
        x["fat_uso"] = x["fat"] if (x["fat"] is not None and x.get("fat_conf") in ("alta", "média")) else e_

    # perfis (segmentos) dos ganhos: setor × porte
    def perfil_nome(x):
        s = x["setor"]
        fam = ("Café e cadeia exportadora" if s == "Café" else "Frigoríficos e carnes" if s in ("Frigoríficos (abate/indústria de carnes)", "Carnes · atacado")
               else "Supermercados e varejo alimentar" if s == "Supermercados e varejo alimentar" else "Atacado de alimentos" if s == "Atacado de alimentos e mercadorias"
               else "Indústria de alimentos e laticínios" if s == "Indústria de alimentos e bebidas" else "Agro e cooperativas" if (s.startswith("Agro") or x.get("coop")) else "Outros setores")
        grande = (x["porte"] == "Demais" and (x["capital"] or 0) >= 1e6) or (x["n_estab"] or 1) >= 3 or (x.get("fat_uso") or 0) >= PISO
        return f"{fam} · {'porte grande' if grande else 'porte médio/pequeno'}"
    for x in EMP.values(): x["perfil"] = perfil_nome(x)
    perfis = defaultdict(list)
    for x in ganhos.values(): perfis[x["perfil"]].append(x)
    tab_perfis = []
    for p, L in sorted(perfis.items(), key=lambda kv: -len(kv[1])):
        reais = [x["fat"] for x in L if x["fat"] is not None and x.get("fat_conf") in ("alta", "média")]
        caps = [x["capital"] for x in L if x["capital"]]; ids = [x["idade"] for x in L if x["idade"] is not None]
        tab_perfis.append({"perfil": p, "empresas_ganhas": len(L), "com_faturamento_real": len(reais),
                           "faturamento_mediano_real_mi": round(statistics.median(reais) / 1e6, 1) if reais else None,
                           "faturamento_mediano_estimado_mi": round(statistics.median(x["fat_uso"] for x in L) / 1e6, 1),
                           "estimados_acima_30mi": sum(1 for x in L if x["fat_uso"] >= PISO),
                           "capital_mediano_mi": round(statistics.median(caps) / 1e6, 2) if caps else None, "idade_mediana": round(statistics.median(ids), 1) if ids else None,
                           "estab_medio": round(statistics.mean(x["n_estab"] for x in L), 1), "pct_demais": round(sum(1 for x in L if x["porte"] == "Demais") / len(L), 2),
                           "pct_real": round(sum(1 for x in L if x["regime"].startswith("Lucro Real")) / len(L), 2),
                           "pct_exportador": round(sum(1 for x in L if any(x["cnae"].startswith(q) for q in BC.EXPORT_CNAE) or "export" in PD.norm(x["razao"])) / len(L), 2),
                           "uf_top": ", ".join(f"{u} {n}" for u, n in Counter(x["uf"] for x in L).most_common(3)),
                           "micro_top": ", ".join(f"{u} {n}" for u, n in Counter(x["micro"] for x in L).most_common(3)),
                           "cnae4_top": ", ".join(f"{c} {n}" for c, n in Counter(x["cnae"][:4] for x in L).most_common(3)),
                           "credito_mediano_mil": round(statistics.median(x["credito"] for x in L) / 1e3) if L else None,
                           "parceiro_top": ", ".join(f"{u} {n}" for u, n in Counter(x["parceiro"] for x in L).most_common(2))})
    AG["B"]["perfis"] = tab_perfis

    # referência "ganhos de alto faturamento": faturamento real ≥ R$ 15 mi (alta/média) ou estimado ≥ R$ 30 mi com porte Demais
    alto = [x for x in ganhos.values() if (x["fat"] is not None and x.get("fat_conf") in ("alta", "média") and x["fat"] >= 15e6)
            or (x["fat"] is None and x["fat_est"] >= PISO and x["porte"] == "Demais")]
    ZA = np.array([(vetor(x) - M.mu) / M.sd * PESOS for x in alto]); RA = [x["raiz"] for x in alto]
    AG["B"]["ref_alto"] = {"n": len(alto), "reais": sum(1 for x in alto if x["fat"] is not None), "setores": dict(Counter(x["setor"] for x in alto))}
    com_fat = [x for x in ganhos.values() if x["fat"] is not None and x.get("fat_conf") in ("alta", "média")]

    def semelhanca(x):
        z = (vetor(x) - M.mu) / M.sd * PESOS
        d = np.sqrt(((ZA - z) ** 2).sum(1)); d[[i for i, r in enumerate(RA) if r == x.get("raiz")]] = np.inf
        dd = np.sort(d)[:5]
        return round(float(100 * math.exp(-dd.mean() / 2.5)), 1)

    def parecidos(x):
        """Ganhos com faturamento conhecido parecidos pela régua do Recuperador (fila.parecido ≥ 8: CNAE/classe + regime/UF/porte/capital)."""
        a = {"cnae": x["cnae"], "classe": x["cnae"][:4], "seg": FILA.seg(x["cnae_desc"]), "regime": x.get("regime") or "", "uf": x["uf"], "porte": {"ME": "Microempresa", "EPP": "Empresa de Pequeno Porte"}.get(x["porte"], x["porte"]), "capital": x["capital"]}
        L = []
        for g in com_fat:
            if g["raiz"] == x.get("raiz"): continue
            b = {"cnae": g["cnae"], "classe": g["cnae"][:4], "seg": FILA.seg(g["cnae_desc"]), "regime": g["regime"], "uf": g["uf"], "porte": {"ME": "Microempresa", "EPP": "Empresa de Pequeno Porte"}.get(g["porte"], g["porte"]), "capital": g["capital"]}
            if FILA.parecido(a, b) >= 8: L.append(g["fat"])
        return len(L), (statistics.median(L) if L else None)

    # presença regional dos ganhos
    gan_mun = Counter((x["uf"], x["municipio"]) for x in ganhos.values() if x["municipio"])
    gan_micro = Counter(x["micro"] for x in ganhos.values() if x["micro"])
    master_micro = defaultdict(Counter)
    for x in ganhos.values():
        if x["parceiro"] in MASTERS: master_micro[x["micro"]][x["parceiro"]] += 1

    # ---- C. perdidos semelhantes
    perdidos = [x for x in EMP.values() if x["status"] == "perdido"]
    linhasC = []
    for x in perdidos:
        sem_ = semelhanca(x); n_p, med_p = parecidos(x)
        real = x["fat"] is not None and x.get("fat_conf") in ("alta", "média")
        est = x["fat"] if real else x["fat_est"]; lo = x["fat"] if real else x["fat_lo"]; hi = x["fat"] if real else x["fat_hi"]
        ativa = (x["situacao"] or "Ativa") == "Ativa"; simples = x["simples"] == "S" or x["regime"].startswith("Simples")
        if not ativa: fx = "C"
        elif est >= CORTE or (real and est >= PISO) or (est >= PISO and sem_ >= 55): fx = "A"
        elif est >= PISO or (est >= 15e6 and sem_ >= 45): fx = "B"
        else: fx = "C"
        if simples and not real and fx != "C": fx = "C"
        par = x["parecer"] or {}
        sinal = par.get("sinal_reanalise") or ""
        if x["valor_perdido_max"] > 0: motivo = f"perda comercial: havia crédito estimado de R$ {x['valor_perdido_max']:,.0f}".replace(",", ".")
        elif par.get("motivo"): motivo = f"técnico: {par['motivo']}"
        else: motivo = "valor zero; sem parecer lido" if not par else "valor zero; parecer sem motivo classificado"
        sinal_pos = sinal.startswith(("Reanalisar", "Mudar a tese", "Recorrência", "Rotear")) or x["valor_perdido_max"] > 0
        eleg_rec = (ativa and not simples and not x["cafe"] and x["regime"].startswith("Lucro Real") and not sinal.startswith(("Vetar", "Não reanalisar"))
                    and (sinal_pos or est >= 15e6))
        cred_int = fx in ("A", "B")
        uso = "ambos" if (cred_int and eleg_rec) else "crédito internacional" if cred_int else "reanálise da recuperação (Recuperador)" if eleg_rec else "nenhum agora"
        linhasC.append({"faixa": fx, "semelhança (0–100)": sem_, "faturamento estimado (R$ mi)": mi(est), "intervalo (R$ mi)": f"{mi(lo)} a {mi(hi)}" if not real else "real (parecer)",
                        "fonte do faturamento": f"parecer ({x['fat_conf']})" if real else x["fat_fonte"], "faixa de faturamento": faixa_fat(est),
                        "perfil": x["perfil"], "ganhos parecidos (nº)": n_p, "mediana de faturamento dos parecidos (R$ mi)": mi(med_p),
                        "motivo da perda": motivo, "sinal do parecer": sinal or None, "uso sugerido": uso,
                        "empresa": x["razao"] or x["nome"], "CNPJ": cnpj_fmt(x["cnpj"]), "setor": x["setor"], "CNAE": f"{x['cnae']} {x['cnae_desc']}".strip(),
                        "regime": x["regime"] or None, "porte": x["porte"], "capital social (R$)": x["capital"] or None, "idade (anos)": round(x["idade"], 1) if x["idade"] else None,
                        "estabelecimentos ativos": x["n_estab"], "situação": x["situacao"], "tem negócio aberto": "sim" if x["tem_aberto"] else "não",
                        "café (fora da meta de recuperação)": "sim" if x["cafe"] else "não",
                        "parceiro": x["parceiro"], "UF": x["uf"], "cidade": x["municipio"], "microrregião": x["micro"],
                        "clientes Save no município": gan_mun.get((x["uf"], x["municipio"]), 0), "link": x["link"]})
    ordem = {"A": 0, "B": 1, "C": 2}
    linhasC.sort(key=lambda l: (ordem[l["faixa"]], -(l["faturamento estimado (R$ mi)"] or 0)))
    AG["C"] = {"empresas_perdidas": len(linhasC), "faixa": dict(Counter(l["faixa"] for l in linhasC)), "uso": dict(Counter(l["uso sugerido"] for l in linhasC)),
               "faixa_uso": {f: dict(Counter(l["uso sugerido"] for l in linhasC if l["faixa"] == f)) for f in "ABC"},
               "AB_setor": dict(Counter(l["setor"] for l in linhasC if l["faixa"] in "AB")), "AB_uf": dict(Counter(l["UF"] for l in linhasC if l["faixa"] in "AB")),
               "AB_micro": dict(Counter(l["microrregião"] for l in linhasC if l["faixa"] in "AB").most_common(10)),
               "AB_parceiro": dict(Counter(l["parceiro"] for l in linhasC if l["faixa"] in "AB")),
               "AB_motivo": dict(Counter(l["motivo da perda"].split(":")[0] for l in linhasC if l["faixa"] in "AB")),
               "AB_cafe": sum(1 for l in linhasC if l["faixa"] in "AB" and l["café (fora da meta de recuperação)"] == "sim"),
               "AB_com_fat_real": sum(1 for l in linhasC if l["faixa"] in "AB" and l["fonte do faturamento"].startswith("parecer")),
               "AB_aberto": sum(1 for l in linhasC if l["faixa"] in "AB" and l["tem negócio aberto"] == "sim"),
               "rec_motivos": dict(Counter(l["motivo da perda"].split(":")[0] for l in linhasC if l["uso sugerido"] in ("ambos", "reanálise da recuperação (Recuperador)")))}

    # ---- D. prospects fora da base
    linhasD = []; univ = Counter()
    for b, m in matriz.items():
        univ["matrizes"] += 1
        if m["situacao"] != "Ativa": continue
        univ["ativas"] += 1
        if b in RAIZES_HS or m.get("no_hubspot"): univ["no_hubspot"] += 1; continue
        e = emp.get(b)
        if not e: continue
        if simp.get(b) == "S": univ["simples"] += 1; continue
        cn = m["cnae"]
        if cn.startswith("69"): univ["contabilidade"] += 1; continue
        nat = str(e[1] or "")
        if nat.startswith("1") or nat in ("2135", "2305"): univ["natureza_excluida"] += 1; continue
        porte = PORTE.get(e[3]); cap = e[2] or 0
        if not (porte == "Demais" or cap >= 1e6): univ["porte_pequeno"] += 1; continue
        univ["candidatos"] += 1
        st, prio = BC.setor(cn, "")   # prospects: setor só pelo CNAE (o nome "café" pega cafeterias e padarias)
        x = {"raiz": b, "cnae": cn, "cnae_desc": cnae_d.get(cn, ""), "setor": st, "prio": prio, "uf": m["uf"], "municipio": m["municipio"], "cep": m["cep"],
             "micro": micro(m["uf"], m["municipio"], m["cep"]), "porte": porte, "capital": cap, "natureza": nat, "sa": nat.startswith(("204", "205")), "coop": nat == "2143",
             "idade": idade(m["inicio"]), "n_estab": n_est.get(b, 1), "regime": "", "razao": e[0]}
        p, lo, hi, idx, d = estima(x)
        x["fat_uso"] = p
        linhasD.append((x, p, lo, hi))
    AG["D_universo"] = dict(univ)
    # score
    out = []
    cand_mun = Counter((x["uf"], x["municipio"]) for x, *_ in linhasD)
    for x, p, lo, hi in linhasD:
        sem_ = semelhanca(x)
        nm = gan_mun.get((x["uf"], x["municipio"]), 0); nmi = gan_micro.get(x["micro"], 0)
        s_fat = 1.0 if p >= CORTE else 0.8 if p >= PISO else 0.5 if p >= 15e6 else 0.2 if p >= 5e6 else 0.0
        # presença Save: ter cliente no município vale 0,6; o resto vem da penetração (clientes ÷ candidatos no município),
        # para a capital com 15 clientes em milhares de empresas não valer o mesmo que Varginha com 15 em poucas dezenas
        pen = nm / max(1, cand_mun[(x["uf"], x["municipio"])])
        s_reg = (0.6 + 0.4 * min(1.0, pen * 20)) if nm >= 1 else 0.5 if nmi >= 3 else 0.3 if nmi >= 1 else 0.0
        s_set = 1.0 if x["prio"] == 2 else 0.5 if x["prio"] == 1 else 0.2 if x["setor"] in ("Supermercados e varejo alimentar", "Atacado de alimentos e mercadorias") else 0.0
        bonus_sm = 5 if x["micro"] == "Sul de Minas" else 3 if x["micro"] in ("Matas de Minas", "Cerrado Mineiro") else 0
        sc = min(100.0, 35 * s_fat + 25 * sem_ / 100 + 25 * s_reg + 10 * s_set + 5 * (1.0 if x["n_estab"] >= 3 else 0.5 if x["n_estab"] == 2 else 0) + bonus_sm)
        mm = master_micro.get(x["micro"], Counter())
        por = []
        if p >= PISO: por.append(f"faturamento estimado {faixa_fat(p)}")
        if sem_ >= 50: por.append(f"parecida com ganhos de alto faturamento ({sem_:.0f})")
        if nm: por.append(f"{nm} cliente(s) Save no município")
        elif nmi: por.append(f"{nmi} cliente(s) Save na microrregião")
        if x["micro"] == "Sul de Minas": por.append("Sul de Minas")
        if x["prio"] == 2: por.append(f"setor prioritário ({x['setor']})")
        if x["n_estab"] >= 3: por.append(f"{x['n_estab']} estabelecimentos ativos")
        if x["capital"] >= 10e6: por.append(f"capital de R$ {x['capital']/1e6:.0f} mi")
        if x["capital"] > 500e6: por.append("capital acima de R$ 500 mi: conta estratégica (abordagem própria)")
        out.append({"score": round(sc, 1), "faturamento estimado (R$ mi)": mi(p), "faixa estimada": faixa_fat(p), "intervalo (R$ mi)": f"{mi(lo)} a {mi(hi)}",
                    "semelhança (0–100)": sem_, "perfil": x["perfil"] if "perfil" in x else perfil_nome(x), "empresa": x["razao"], "CNPJ (matriz)": cnpj_fmt(matriz[x["raiz"]]["cnpj"]),
                    "raiz do CNPJ": x["raiz"], "município": x["municipio"], "UF": x["uf"], "microrregião": x["micro"],
                    "clientes Save no município": nm, "clientes Save na microrregião": nmi,
                    "Master com presença na região": ", ".join(f"{k} ({v})" for k, v in mm.most_common(3)) or "nenhum Master com ganho na microrregião",
                    "CNAE": f"{x['cnae']} {x['cnae_desc']}".strip(), "setor": x["setor"], "capital social (R$)": x["capital"] or None, "porte": x["porte"],
                    "idade (anos)": round(x["idade"], 1) if x["idade"] else None, "filiais ativas": max(0, x["n_estab"] - 1), "matriz/filial": "matriz",
                    "por que está aqui": "; ".join(por) or "perfil de porte compatível"})
    out.sort(key=lambda l: -l["score"])
    estrategicas = [l for l in out if (l["capital social (R$)"] or 0) > 500e6]
    out = [l for l in out if (l["capital social (R$)"] or 0) <= 500e6]
    linhasD_top = out[:2000]
    AG["D"] = {"candidatos_pontuados": len(out), "top": len(linhasD_top),
               "estimados_acima_30mi_universo": sum(1 for l in out if l["faturamento estimado (R$ mi)"] >= 30),
               "estimados_acima_50mi_universo": sum(1 for l in out if l["faturamento estimado (R$ mi)"] >= 50),
               "top_faixa": dict(Counter(l["faixa estimada"] for l in linhasD_top)), "top_uf": dict(Counter(l["UF"] for l in linhasD_top).most_common()),
               "top_micro": dict(Counter(l["microrregião"] for l in linhasD_top).most_common(15)), "top_setor": dict(Counter(l["setor"] for l in linhasD_top).most_common()),
               "top_municipio": dict(Counter(f"{l['município']}/{l['UF']}" for l in linhasD_top).most_common(15)),
               "top_master": dict(Counter((l["Master com presença na região"].split(" (")[0]) for l in linhasD_top).most_common()),
               "top_com_cliente_municipio": sum(1 for l in linhasD_top if l["clientes Save no município"] > 0),
               "top_sul_de_minas": sum(1 for l in linhasD_top if l["microrregião"] == "Sul de Minas"),
               "universo_sul_de_minas": sum(1 for l in out if l["microrregião"] == "Sul de Minas"),
               "top_sul_de_minas_setor": dict(Counter(l["setor"] for l in linhasD_top if l["microrregião"] == "Sul de Minas")),
               "estrategicas": len(estrategicas), "estrategicas_setor": dict(Counter(l["setor"] for l in estrategicas)),
               "corte_score_top": linhasD_top[-1]["score"] if linhasD_top else None,
               "top_score_faixas": {"≥ 70": sum(1 for l in linhasD_top if l["score"] >= 70), "60–70": sum(1 for l in linhasD_top if 60 <= l["score"] < 70), "50–60": sum(1 for l in linhasD_top if 50 <= l["score"] < 60), "< 50": sum(1 for l in linhasD_top if l["score"] < 50)},
               "top_sul_de_minas_municipio": dict(Counter(l["município"] for l in linhasD_top if l["microrregião"] == "Sul de Minas").most_common(12)),
               "top_master_sul_de_minas": dict(Counter(l["Master com presença na região"] for l in linhasD_top if l["microrregião"] == "Sul de Minas").most_common(3)),
               "top_setor_x_regiao": {r: dict(Counter(l["setor"] for l in linhasD_top if l["UF"] == r)) for r in ("MG", "SP", "DF", "GO", "SC", "ES")}}
    AG["cobertura_receita"] = {"estab": cob["estab"], "situacao": dict(cob["situacao"]), "por_uf": dict(cob["por_uf"].most_common()), "cnae2": dict(cob["cnae2"].most_common(12)),
                               "matrizes": univ["matrizes"]}

    # ---- planilhas
    colsA = ["empresa", "CNPJ", "setor", "CNAE", "UF", "cidade", "microrregião", "faturamento anual (R$)", "faixa", "ano de referência", "método", "confiança",
             "série por ano (R$ mi)", "checagens", "base de cálculo implícita (R$)", "trecho de apoio", "arquivo de origem", "negócio do arquivo",
             "crédito recuperado (R$)", "crédito ÷ faturamento", "regime", "porte (Receita)", "capital social (R$)", "parceiro", "link do HubSpot"]
    largA = {"empresa": 38, "CNAE": 40, "checagens": 70, "trecho de apoio": 60, "arquivo de origem": 32, "série por ano (R$ mi)": 34, "método": 30, "link do HubSpot": 18}
    colsS = ["empresa", "CNPJ", "setor", "UF", "cidade", "onde está o dado", "crédito recuperado (R$)", "porte (Receita)", "capital social (R$)", "parceiro", "link do HubSpot"]
    metA = [["Objetivo", "Faturamento anual das empresas com negócio GANHO, lido nos pareceres e diagnósticos do técnico (dado usado no cálculo da recuperação). Uso: direcionar o crédito via fundos internacionais (corte de referência R$ 50 mi/ano; levantamento a partir de R$ 30 mi)."],
            ["Fontes", f"HubSpot (download {HB.get('baixado_em')}); textos dos pareceres em celulas/geovana/pareceres/textos; Receita Federal, Dados Abertos do CNPJ ref. {meta.get('mes_referencia')} (base local, só leitura). Tudo local: nenhum CNPJ saiu da máquina."],
            ["Unidade", "Uma linha por empresa (raiz do CNPJ, 8 dígitos). Pareceres de qualquer negócio da mesma empresa (inclusive perdidos) contam: a coluna 'negócio do arquivo' diz de onde veio."],
            ["Extrator", "scripts/faturamento_pareceres.py: lê TABELAS (linhas 'ano + valor', agrupadas), classifica cada tabela pelo rótulo antes/depois (faturamento, pagamento de PIS/COFINS por código de DARF, base de tese) e decide se é média mensal (×12) ou soma anual. Ano parcial é anualizado pelos meses do período de apuração ou descartado em favor do último ano completo. Frases ('Faturamento médio de R$ …', 'MÉDIA MENSAL R$ …') entram quando não há tabela."],
            ["Métodos", "tabela mensal somada (média mensal × 12) · total anual (tabela) · frase (média mensal × 12 ou valor anual). Base de cálculo: os pagamentos de PIS/COFINS por DARF viram base implícita (cumulativo 8109/2172: pago ÷ 3,65%; não cumulativo 5856/6912: pago ÷ 9,25%, que é só um PISO porque o pago já desconta os créditos)."],
            ["Confiança", "alta: tabela com 3+ anos e rótulo claro, passando nas checagens (ou confirmada pela base de cálculo do cumulativo). média: tabela com 1–2 anos, frase, ou uma checagem fora. baixa: rótulo mensal/anual ausente, ou duas checagens fora. Cada checagem que falha derruba um nível."],
            ["Checagens (dupla checagem)", "1) base de cálculo do PIS/COFINS quando o parecer traz os pagamentos; 2) crédito recuperado ÷ faturamento anual entre 0,2% e 80% (o crédito é de até 5 anos); 3) porte e Simples da Receita (Simples acima do teto ou 'Demais' com faturamento de microempresa derrubam; ME com faturamento alto é só porte desatualizado); 4) série volátil (CV > 0,6) derruba."],
            ["Limites", "O faturamento é o que o técnico levantou no período da análise (pode ter 1–3 anos). Não substitui DRE nem balanço: antes de levar ao fundo, confirmar com a empresa. Valores de faturamento NÃO vão para fora da Save."],
            ["Aba 'Sem faturamento'", "Para cada empresa ganha sem faturamento, onde o dado está: print colado no Word (sem OCR), arquivo do HubSpot sem permissão, arquivo ilegível, modelo de relatório sem o campo, ou card sem parecer."],
            ["Responsáveis", "Dados & BI, Inteligência Comercial e Recuperador (célula da Geovana), agentes virtuais. Rascunho para o Luis; uso interno."]]
    dA = grava("Faturamento-Clientes-Ganhos.xlsx", [("Faturamento dos ganhos", colsA, linhasA, largA), ("Sem faturamento (onde está)", colsS, sem, {"empresa": 38, "onde está o dado": 80, "link do HubSpot": 18})], metA)

    colsC = ["faixa", "semelhança (0–100)", "faturamento estimado (R$ mi)", "intervalo (R$ mi)", "fonte do faturamento", "faixa de faturamento", "perfil",
             "ganhos parecidos (nº)", "mediana de faturamento dos parecidos (R$ mi)", "motivo da perda", "sinal do parecer", "uso sugerido", "empresa", "CNPJ", "setor", "CNAE",
             "regime", "porte", "capital social (R$)", "idade (anos)", "estabelecimentos ativos", "situação", "tem negócio aberto", "café (fora da meta de recuperação)",
             "parceiro", "UF", "cidade", "microrregião", "clientes Save no município", "link"]
    largC = {"empresa": 38, "CNAE": 40, "perfil": 40, "motivo da perda": 44, "sinal do parecer": 44, "uso sugerido": 30, "intervalo (R$ mi)": 18}
    v = AG["B"]["validacao"]["kNN + regressão (usado)"]
    metC = [["Objetivo", "Achar, entre os negócios PERDIDOS do HubSpot, as empresas parecidas com os clientes ganhos de alto faturamento: alvo do crédito internacional e, quando couber, da reanálise da recuperação pelo Recuperador."],
            ["Universo", "Uma linha por empresa (raiz do CNPJ) cujo(s) negócio(s) no HubSpot estão todos perdidos. Empresas com qualquer negócio ganho ficam de fora (já estão na planilha de faturamento). 'tem negócio aberto' avisa quando a empresa voltou ao funil."],
            ["Faturamento", "Quando o parecer do próprio negócio perdido traz faturamento (confiança alta/média), vale o número real. Sem isso, o lookalike estima pelas variáveis da Receita: capital social, porte, idade, nº de estabelecimentos ativos, S.A. e setor (CNAE)."],
            ["Modelo", f"Média de um kNN ponderado (k={K}) e de uma regressão ridge (λ={LAM}) sobre o log10 do faturamento, treinados nas {AG['B']['n_treino']} empresas com faturamento real de confiança alta/média. numpy, sem bibliotecas externas. Validação leave-one-out: erro mediano de {v['fator_mediano']}x (para mais ou para menos), {v['dentro_fator_2']:.0%} das estimativas dentro de 2x, acerto da faixa 'acima/abaixo de R$ 30 mi' de {v['acerto_faixa_30mi']:.0%}. O intervalo é o percentil 10–90 do erro da validação."],
            ["Modelo 2 (crédito)", f"Quando o negócio tem crédito estimado no HubSpot: log10(faturamento) = {AG['B']['modelo_credito']['a']} + {AG['B']['modelo_credito']['b']} × log10(crédito), treinado em {AG['B']['modelo_credito']['n']} empresas. Validação leave-one-out: erro mediano de {AG['B']['modelo_credito']['fator_mediano']}x e {AG['B']['modelo_credito']['dentro_fator_2']:.0%} dentro de 2x (melhor que o modelo da Receita). Ordem de uso: faturamento real do parecer > modelo 2 > modelo 1."],
            ["Semelhança (0–100)", f"Distância às 5 empresas mais parecidas do grupo de referência 'ganhos de alto faturamento' ({AG['B']['ref_alto']['n']} empresas: faturamento real ≥ R$ 15 mi, ou estimado ≥ R$ 30 mi com porte Demais), nas mesmas variáveis do modelo. 100 = idêntica."],
            ["Ganhos parecidos", "Régua do Recuperador (fila.parecido ≥ 8: CNAE ou classe igual, mais regime, UF, porte e capital) aplicada aos ganhos com faturamento conhecido: contagem e mediana do faturamento."],
            ["Faixas", "A: faturamento ≥ R$ 50 mi, ou ≥ R$ 30 mi real, ou ≥ R$ 30 mi estimado com semelhança ≥ 55. B: ≥ R$ 30 mi estimado, ou ≥ R$ 15 mi com semelhança ≥ 45. C: o resto, CNPJ não ativo, ou Simples sem faturamento real."],
            ["Uso sugerido", "crédito internacional = faixa A ou B. Reanálise da recuperação (Recuperador) = CNPJ ativo, Lucro Real, fora do Simples, fora do café (fora da meta desde abr/2026), sem veto no parecer ('Vetar' ou 'Não reanalisar') e com um sinal: perda comercial com crédito estimado, parecer favorável (Reanalisar, Mudar a tese, Recorrência, Rotear ao comercial) ou faturamento estimado ≥ R$ 15 mi. Ambos quando as duas condições valem. O Recuperador continua aplicando os vetos V1–V11 dele."],
            ["Motivo da perda", "O HubSpot não tem campo de motivo de perda no download. Usado: perda comercial (havia crédito estimado > 0), ou o motivo que o técnico escreveu no parecer (resumos.json), ou 'valor zero, sem parecer lido'."],
            ["Cuidados", "Estimativa, não promessa: confirmar faturamento e garantias com a empresa antes de qualquer conversa com o fundo. A abordagem passa pela Jenifer e pelo Master do parceiro original. Conferir a raiz do CNPJ no HubSpot antes de abordar (conflito de canal)."]]
    dC = grava("Lookalike-Perdidos.xlsx", [("Perdidos semelhantes", colsC, linhasC, largC)], metC)

    colsD = ["score", "faturamento estimado (R$ mi)", "faixa estimada", "intervalo (R$ mi)", "semelhança (0–100)", "perfil", "empresa", "CNPJ (matriz)", "raiz do CNPJ",
             "município", "UF", "microrregião", "clientes Save no município", "clientes Save na microrregião", "Master com presença na região", "CNAE", "setor",
             "capital social (R$)", "porte", "idade (anos)", "filiais ativas", "matriz/filial", "por que está aqui"]
    largD = {"empresa": 38, "CNAE": 40, "perfil": 40, "por que está aqui": 70, "Master com presença na região": 34, "intervalo (R$ mi)": 18}
    metD = [["Objetivo", "Empresas ATIVAS que não estão no HubSpot (pela raiz do CNPJ), parecidas com os clientes ganhos de alto faturamento, priorizando os municípios e microrregiões onde a Save já tem clientes ganhos."],
            ["Base", f"Receita Federal, Dados Abertos do CNPJ ref. {meta.get('mes_referencia')}, base local filtrada pelos CNAEs-alvo do ICP (frigoríficos 1011–1013, laticínios 105x, outros alimentos 1031/1033/1091, atacado de alimentos 4631/4633/4634/4637/4639, supermercados 4711/4712, varejo 4721/4722/4724, contabilidade 6920) em 12 UFs (MG, SP, ES, GO, DF, PR, SC, BA, RJ, MT, MS, TO), só ATIVAS, mais as empresas do HubSpot com qualquer CNAE. Café (4621, 1081, 0134), agro, usinas, construtoras e máquinas NÃO estão na base fora do HubSpot: ver o documento 12."],
            ["Filtros", "Matriz ativa · raiz fora do HubSpot · fora do Simples · sem contabilidades (são indicadores, não clientes) · sem órgãos públicos e empresário individual · porte 'Demais' ou capital ≥ R$ 1 mi."],
            ["Score (0–100+)", "35 × faixa de faturamento estimado (≥ 50 mi: 1; 30–50: 0,8; 15–30: 0,5; 5–15: 0,2) + 25 × semelhança com os ganhos de alto faturamento + 25 × presença Save (cliente no município: 0,6 + 0,4 × penetração, isto é, clientes ÷ candidatos do município × 20, até 1; só na microrregião: 0,5 com 3+ clientes, 0,3 com 1–2) + 10 × setor (prioritário 1; adjacente 0,5; supermercado/atacado 0,2) + 5 × filiais + bônus de 5 no Sul de Minas (3 em Matas de Minas e Cerrado). Lista limitada aos 2.000 melhores."],
            ["Faturamento estimado", "Mesmo modelo dos perdidos (kNN + regressão sobre variáveis da Receita), com intervalo P10–P90 do erro da validação cruzada. É ordem de grandeza para priorizar, não número para proposta."],
            ["Microrregião", "Em MG: Sul de Minas, Matas de Minas e Cerrado Mineiro pela lista de municípios do café (base_clientes.py). Nas demais: região postal (UF + 3 primeiros dígitos do CEP)."],
            ["LGPD", "Lista só para prospecção B2B (dados públicos de pessoa jurídica, legítimo interesse). Sem dados de sócios, sem CPF, sem contato. Não compartilhar fora da Save; não enriquecer com dados pessoais sem validação do Jurídico."],
            ["Abordagem", "Passa pela Jenifer (BDR) e pelo Master com presença na região. Antes de abordar, checar a raiz do CNPJ no HubSpot (conflito de canal) e registrar a oportunidade no parceiro certo."],
            ["Contas estratégicas", "Capital acima de R$ 500 mi: grandes grupos, em aba separada e fora do ranking dos 2.000; abordagem própria."],
            ["Matriz/filial", "Uma linha por empresa (raiz), sempre a matriz; 'filiais ativas' conta os outros estabelecimentos ativos da raiz na base local (piso: a base guarda só os CNAEs-alvo)."]]
    dD = grava("Prospects-Semelhantes.xlsx", [("Prospects", colsD, linhasD_top, largD), ("Contas estratégicas", colsD, estrategicas, largD)], metD)
    AG["arquivos"] = [dA, dC, dD]
    json.dump(AG, open(AGG, "w"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({"A": {k: AG["A"][k] for k in ("empresas_ganhas", "empresas_ganhas_com_texto", "empresas_ganhas_com_faturamento", "confianca")},
                      "B": {"n": AG["B"]["n_treino"], "val": AG["B"]["validacao"]["kNN + regressão (usado)"]}, "C": AG["C"]["faixa_uso"], "D": AG["D"]["top_faixa"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
