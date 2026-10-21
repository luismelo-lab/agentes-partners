"""Modelo D&S: geografia (bairro → região da cidade → cidade → cidades vizinhas), similaridade com os ganhos e potencial.

Similaridade (0–100%) entre um prospect e cada cliente ganho da D&S (pesos somam 1):
  segmento CNAE 0,40 (7 díg. = 1 · 5 = 0,85 · 4 = 0,7 · 3 = 0,4 · 2 = 0,2) · porte 0,15 · capital social 0,20 (distância em log10)
  · idade 0,10 · natureza jurídica 0,05 · geografia 0,10 (bairro 1 · região da cidade 0,85 · cidade 0,7 · vizinhas 0,4).
Empresa exemplo = o ganho mais parecido. Potencial de referência = média dos 10 ganhos mais parecidos (peso = similaridade³),
usando o 1º diagnóstico ganho (crédito apurado, sem duplicidade de importação). Potencial esperado = referência × conversão
do segmento na própria carteira da D&S (ganho ÷ ganho + cancelado, suavizada pela média geral).
"""
import collections, math, os, pickle, re, sqlite3, unicodedata
import numpy as np

S = os.environ.get("PROSPECCAO_DS", os.path.expanduser("~/agentes-partners/departamentos/intel-comercial/prospeccao-ds")); AP = os.path.expanduser("~/agentes-partners")
B = pickle.load(open(S + "/base.pkl", "rb")); cli, pros = B["cli"], B["pros"]
db = sqlite3.connect("file:" + AP + "/dados-publicos/receita/cnpj.sqlite?mode=ro", uri=True)
TEM_BAIRRO = "bairro" in {r[1] for r in db.execute("pragma table_info(estab)")}
HOJE = 2026 + 10 / 12


def norm(s): return re.sub(r"\s+", " ", unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().upper()).strip()


def endereco(cnpj):
    if not TEM_BAIRRO: return None, None
    r = db.execute("select bairro, logradouro from estab where cnpj=?", (cnpj,)).fetchone()
    return (r[0], r[1]) if r else (None, None)


def idade(ab):
    try: return HOJE - (int(ab[:4]) + int(ab[4:6]) / 12)
    except Exception: return None


PORTE = {"Microempresa": 0, "Empresa de Pequeno Porte": 1, "Demais": 2}

# ── âncoras: clientes ganhos da D&S ──
anc = [x for x in cli if x["fase"] == "Ganho" and x["rf"]]
for x in anc:
    x["bairro"], x["logradouro"] = endereco(x["cnpj"])
for x in cli:
    if x["rf"] and "bairro" not in x: x["bairro"], x["logradouro"] = endereco(x["cnpj"])
RJ = re.compile(r"RECUPERACAO JUDICIAL|EM RECUP|FALID|FALENCIA|EM LIQUIDACAO|LIQUIDACAO EXTRAJUDICIAL")
pros = [p for p in pros if not RJ.search(norm(p.get("razao")))]
import json as _json
REG = _json.load(open(AP + "/dados-publicos/receita/regime-cache.json"))
TOTAL_ANTES = len(pros)
for p in pros: p["regime"] = REG.get(p["cnpj"])
if os.environ.get("SO_LUCRO_REAL", "1") == "1":  # pedido do Luis (20/10): só empresas no Lucro Real
    pros = [p for p in pros if str(p["regime"] or "").upper().startswith("LUCRO REAL")]
for p in pros:
    p["bairro"], p["logradouro"] = endereco(p["cnpj"])

# conversão por segmento (CNAE 4) na carteira da D&S
g4 = collections.Counter(x["rf"]["cnae"][:4] for x in cli if x["rf"] and x["fase"] == "Ganho")
c4 = collections.Counter(x["rf"]["cnae"][:4] for x in cli if x["rf"] and x["fase"] == "Cancelado")
G, C = sum(g4.values()), sum(c4.values()); BASE_CONV = G / (G + C); K = 8
CONV = {k: (g4[k] + K * BASE_CONV) / (g4[k] + c4[k] + K) for k in set(g4) | set(c4)}

# vetores
def feats(o, rf):
    return (rf["cnae"], PORTE.get(rf.get("porte"), 0), math.log10(max(float(rf.get("capital") or 0), 0) + 1), idade(rf.get("abertura")) or 10,
            rf.get("natureza") or "", rf.get("ibge"), rf.get("regiao_imediata_id"), (rf.get("cep") or "")[:4], norm(o.get("bairro")))

A = [feats(x, x["rf"]) for x in anc]
A_cnae = np.array([a[0] for a in A]); A_por = np.array([a[1] for a in A]); A_cap = np.array([a[2] for a in A]); A_id = np.array([a[3] for a in A])
A_nat = np.array([a[4] for a in A]); A_mun = np.array([a[5] or 0 for a in A]); A_reg = np.array([a[6] or 0 for a in A])
A_cep4 = np.array([a[7] for a in A]); A_bai = np.array([a[8] for a in A])
A_val = np.array([x["hs"]["primeiro_ganho"] or 0 for x in anc], dtype=float); A_tem = A_val > 0
A_c = {n: np.array([c[:n] for c in A_cnae]) for n in (2, 3, 4, 5, 7)}
GEO_NOME = {1.0: "1 · Mesmo bairro", 0.85: "2 · Mesma região da cidade", 0.7: "3 · Mesma cidade", 0.4: "4 · Cidades vizinhas", 0.0: "5 · Mesma UF"}


def avaliar(p):
    cn = p["cnae"]
    s_cnae = np.zeros(len(anc))
    for n, w in ((2, .2), (3, .4), (4, .7), (5, .85), (7, 1.0)):
        s_cnae = np.where(A_c[n] == cn[:n], w, s_cnae)
    s_por = 1 - np.minimum(np.abs(A_por - PORTE.get(p.get("porte"), 0)), 2) / 2
    s_cap = 1 - np.minimum(np.abs(A_cap - math.log10(max(float(p.get("capital") or 0), 0) + 1)) / 2, 1)
    s_id = 1 - np.minimum(np.abs(A_id - (idade(p.get("abertura")) or 10)) / 20, 1)
    s_nat = (A_nat == (p.get("natureza") or "")).astype(float)
    mesma_cid = A_mun == (p.get("ibge") or -1)
    bai = norm(p.get("bairro"))
    s_geo = np.where(mesma_cid & (A_bai == bai) & (bai != ""), 1.0,
             np.where(mesma_cid & (A_cep4 == (p.get("cep") or "")[:4]), .85,
             np.where(mesma_cid, .7, np.where(A_reg == (p.get("regiao_imediata_id") or -1), .4, 0.0))))
    sim = .40 * s_cnae + .15 * s_por + .20 * s_cap + .10 * s_id + .05 * s_nat + .10 * s_geo
    i = int(np.argmax(sim))
    # geografia: âncora mais próxima (nível mais alto; desempate pela similaridade)
    gmax = float(s_geo.max()); j = int(np.argmax(np.where(s_geo == gmax, sim, -1)))
    # potencial: 10 ganhos mais parecidos com valor
    idx = np.where(A_tem)[0]; top = idx[np.argsort(-sim[idx])[:10]]; w = sim[top] ** 3
    ref = float((A_val[top] * w).sum() / w.sum())
    lo, hi = np.percentile(A_val[top], [25, 75])
    conv = CONV.get(cn[:4], BASE_CONV)
    p.update({"similaridade": round(float(sim[i]) * 100, 1), "exemplo": anc[i], "nivel_geo": GEO_NOME[gmax], "ancora_geo": anc[j],
              "ref": ref, "faixa": (float(lo), float(hi)), "conversao": conv, "potencial": ref * conv})


if __name__ == "__main__":
    import time; t = time.time()
    for k, p in enumerate(pros): avaliar(p)
    print("avaliados", len(pros), round(time.time() - t), "s · bairro na base:", TEM_BAIRRO)
    pickle.dump({"cli": cli, "anc": anc, "pros": pros, "conv": CONV, "base_conv": BASE_CONV}, open(S + "/modelo.pkl", "wb"))
    print(collections.Counter(p["nivel_geo"] for p in pros))
    print("potencial total esperado (R$ mi):", round(sum(p["potencial"] for p in pros) / 1e6, 1))
