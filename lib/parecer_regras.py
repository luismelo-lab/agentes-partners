#!/usr/bin/env python3
"""Regras da Geovana (14/10/2026) para todo relatório montado a partir dos pareceres do técnico.

1. Valor zerado no parecer → trazer o motivo escrito no arquivo.
2. Tabela de faturamento só até 2025 → "Empresa sem movimentação".
3. Situação na Receita Federal (ativa ou não) e data de abertura.
4. Procuração (cnpj-procuracao-check): acesso ainda não liberado aos agentes → "a conferir".
5. Regime: só o que aparece no ÚLTIMO parecer (não o do HubSpot).

Fontes locais (nada sai do Mac): celulas/geovana/pareceres (resumos.json e textos/), dados-publicos/receita/cnpj.sqlite.
Uso em Python:  import parecer_regras as PR;  PR.empresa(deal_ids, cnpj) → dict com as colunas acima.
"""
import glob, json, os, re, sqlite3
from datetime import date

AP = os.path.expanduser("~/agentes-partners")
PAR = os.path.join(AP, "celulas/geovana/pareceres")
_R = None; _DB = None


def resumos():
    global _R
    if _R is None: _R = json.load(open(os.path.join(PAR, "resumos.json"), encoding="utf-8"))
    return _R


def _data(p):
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", str((p or {}).get("data_analise") or ""))
    return date(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else None


def ultimo_parecer(deal_ids):
    """O parecer mais recente entre os negócios da mesma empresa (pela data da análise)."""
    R = resumos(); cs = [(str(d), R[str(d)]) for d in deal_ids if str(d) in R and R[str(d)].get("modelo")]
    if not cs: return None, None
    d, p = max(cs, key=lambda c: _data(c[1]) or date(1900, 1, 1)); return d, p


REG = re.compile(r"(lucro real|lucro presumido|simples nacional|lucro arbitrado)", re.I)
NOMES_REG = {"real": "Lucro Real", "presumido": "Lucro Presumido", "arbitrado": "Lucro Arbitrado", "simples nacional": "Simples Nacional"}
def _regime_txt(t):
    """Regime atual no texto. Ignora histórico e cabeçalho: "foi optante pelo Simples até 2010", "nunca foi optante",
    "Consulta Optante pelo Simples Nacional:". Aceita a forma curta "optante pelo real"."""
    pad = r"(nunca (?:foi )?|foi |era |anteriormente |consulta )?(?:optante|tributad[ao]|enquadrad[ao]|regime)[^.\n:]{0,40}?\b(?:lucro )?(real|presumido|arbitrado|simples nacional)\b(\s*:)?([^.\n]{0,14}\bat[ée]\b)?"
    for m in re.finditer(pad, t, re.I):
        if not m.group(1) and not m.group(3) and not m.group(4): return NOMES_REG[m.group(2).lower()]
    return None


def regime(p, deal_id=None):
    """Regime do último parecer: perfil empresarial; se não estiver lá, o texto do parecer (parecer RT primeiro)."""
    r = _regime_txt(str((p or {}).get("perfil") or ""))
    if not r and deal_id:
        for f in sorted(glob.glob(os.path.join(PAR, "textos", f"{deal_id}_parecer_rt_*.txt"))) + sorted(glob.glob(os.path.join(PAR, "textos", f"{deal_id}_*.txt"))):
            r = _regime_txt(open(f, errors="ignore").read())
            if r: break
    return r


def zerado(p):
    """Sem valor citado no parecer → motivo lido no arquivo (motivo principal + desfecho de cada grupo de teses)."""
    if not p or p.get("maiores_valores_citados_rs"): return None
    partes = [p.get("motivo")] if p.get("motivo") else []
    partes += [f"{k.replace('Teses de ', '')}: {(v or {}).get('desfecho')}" for k, v in (p.get("teses") or {}).items() if (v or {}).get("desfecho")]
    return " · ".join(dict.fromkeys(x for x in partes if x)) or "parecer sem valor e sem motivo legível: abrir o arquivo"


ANO = re.compile(r"^\s*(20[12]\d)\s+(?:R\$\s*)?([\d.]+,\d{2})\s*(?:R\$)?\s*$", re.M)
def faturamento(deal_id):
    """Anos da tabela de faturamento do parecer (texto lido). None = tabela não encontrada."""
    anos = set()
    for f in glob.glob(os.path.join(PAR, "textos", f"{deal_id}_*.txt")):
        t = open(f, errors="ignore").read()
        if re.search(r"faturamento", t, re.I): anos |= {int(a) for a, v in ANO.findall(t) if float(v.replace(".", "").replace(",", ".")) > 0}
    return sorted(anos) or None


def movimentacao(deal_id):
    anos = faturamento(deal_id)
    if not anos: return "tabela de faturamento não encontrada no parecer"
    return "Empresa sem movimentação" if max(anos) <= 2025 else f"com faturamento até {max(anos)}"


def receita(cnpj):
    """Situação e data de abertura na base local da Receita (Dados Abertos, mês de referência na tabela meta)."""
    global _DB
    d = re.sub(r"\D", "", str(cnpj or "")).zfill(14)
    if not cnpj: return {"situacao": "sem CNPJ no HubSpot", "abertura": None}
    if _DB is None: _DB = sqlite3.connect(os.path.join(AP, "dados-publicos/receita/cnpj.sqlite"))
    r = _DB.execute("select situacao, inicio, data_situacao from estab where cnpj=?", (d,)).fetchone()
    if not r: return {"situacao": "não encontrado na base local da Receita", "abertura": None}
    ab = date(int(r[1][:4]), int(r[1][4:6]), int(r[1][6:8])) if r[1] and len(r[1]) == 8 else None
    return {"situacao": r[0] + ("" if r[0] == "Ativa" or not r[2] else f" desde {r[2][6:8]}/{r[2][4:6]}/{r[2][:4]}"), "abertura": ab}


def referencia_receita():
    try:
        db = sqlite3.connect(os.path.join(AP, "dados-publicos/receita/cnpj.sqlite"))
        return dict(db.execute("select chave, valor from meta").fetchall()).get("mes_referencia")
    except Exception: return None


def empresa(deal_ids, cnpj):
    did, p = ultimo_parecer(deal_ids); rf = receita(cnpj)
    return {"parecer_negocio": did, "parecer_data": _data(p), "regime_parecer": regime(p, did) or ("parecer não lido" if not p else "não informado no parecer"),
            "valor_zerado_motivo": zerado(p), "movimentacao": movimentacao(did) if did else "parecer não lido",
            "situacao_receita": rf["situacao"], "abertura": rf["abertura"], "procuracao": "a conferir (acesso ao site ainda não liberado aos agentes)"}
