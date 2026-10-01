"""Funções comuns da célula da Daniela (Central Masters). Somente leitura de arquivos locais.

Nunca chama a API do HubSpot e nunca lê o arquivo .env: a base é o download já feito por
~/.claude/skills/depto-resultados/scripts/hubspot_fonte.py --baixar.
"""
import glob, json, os, re, sys, unicodedata
from datetime import date, datetime, timedelta

HOME = os.path.expanduser("~")
AP = os.path.join(HOME, "agentes-partners")
SRC = os.path.join(AP, "departamentos/resultados/dados")
MAP = os.path.join(AP, "departamentos/resultados/mapeamento-hubspot.json")
RECEITA = os.path.join(AP, "departamentos/intel-comercial/enriquecimento-receita.json")
DADOS_BI = os.path.join(AP, "departamentos/dados")
CELULA = os.path.join(AP, "celulas/daniela")
PENDENCIAS = os.path.join(CELULA, "Controle-Pendencias-Masters.xlsx")
SKILL = os.path.join(HOME, ".claude/skills/celula-daniela")
LINK = "https://app.hubspot.com/contacts/47865021/deal/{}"


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def dt(s):
    try:
        return datetime.fromisoformat((s or "")[:10]).date()
    except ValueError:
        return None


def brl(v):
    if v is None:
        return "—"
    s = f"{abs(v):,.0f}".replace(",", ".")
    return ("-R$ " if v < 0 else "R$ ") + s


def mi(v):
    return "—" if v is None else f"R$ {v/1e6:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(v, casas=1):
    return "—" if v is None else f"{v:.{casas}f}%".replace(".", ",")


def cnpj_digitos(c):
    return re.sub(r"\D", "", c or "")


def fonte_hubspot(caminho=None):
    """Arquivo hubspot-*.json indicado ou o mais recente."""
    if caminho:
        f = os.path.expanduser(caminho)
    else:
        fs = sorted(glob.glob(os.path.join(SRC, "hubspot-*.json")))
        if not fs:
            sys.exit(f"Nenhum download do HubSpot em {SRC}. Peça ao Engenheiro de Dados (depto-dados) para baixar.")
        f = fs[-1]
    D = json.load(open(f))
    return f, D


def roster():
    cfg = json.load(open(MAP))
    return cfg["escopo"]["parceiros_roster"], cfg.get("regras", {})


def resolver_master(texto):
    """Nome canônico do Master a partir do nome, sigla ou alias (sem acento, sem caixa)."""
    R, _ = roster()
    k = lambda x: re.sub(r"[^a-z0-9]", "", norm(x))  # "ds", "D & S" e "d&s" são o mesmo
    t = k(texto)
    for canon, als in R.items():
        if t == k(canon) or t in {k(a) for a in als}:
            return canon
    cand = [c for c, als in R.items() if t and (t in k(c) or any(t in k(a) for a in als))]
    if len(cand) == 1:
        return cand[0]
    opc = ", ".join(R.keys())
    if cand:
        sys.exit(f"'{texto}' é ambíguo: {', '.join(cand)}. Seja mais específico.")
    sys.exit(f"Master '{texto}' não encontrado no roster. Opções: {opc}.")


def e_cafe(d, regras):
    pal = [norm(p) for p in regras.get("cafe_palavras", [])]
    txt = norm((d.get("nome") or "") + " " + (d.get("segmento") or ""))
    cn = cnpj_digitos(d.get("cnae") or "")
    return any(p in txt for p in pal) or (cn and cn in set(regras.get("cafe_cnae", [])))


def receita():
    if not os.path.exists(RECEITA):
        return None, {}
    R = json.load(open(RECEITA))
    return f"{R.get('fonte')} (cruzamento de {R.get('gerado_em')})", R.get("negocios", {})


def saude_master(master):
    fs = sorted(glob.glob(os.path.join(DADOS_BI, "dados-bi-*.json")))
    if not fs:
        return None, None
    R = json.load(open(fs[-1]))
    for s in R.get("scorecard", []):
        if s.get("parceiro") == master:
            return os.path.basename(fs[-1]), s
    return os.path.basename(fs[-1]), None


def ultima_atividade(d):
    return dt(d["extras"].get("ultima_atividade")) or dt(d["extras"].get("ultima_modificacao"))


def dias_uteis_depois(inicio, n):
    """Soma n dias úteis (seg–sex). Feriados não são considerados (limitação declarada)."""
    d = inicio
    while n > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", norm(s)).strip("-")
