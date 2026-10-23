"""Fonte única dos dados repetidos entre os scripts da Área Partners (proposta do Depto Dados, 01/10/2026).

Use:  sys.path.insert(0, os.path.expanduser("~/agentes-partners/lib")); import partners_dados as PD
Migração gradual: cada script que ainda tem cópia própria passa a importar daqui, com os totais conferidos
antes e depois. Já migrados: demandas_whatsapp.py, registro_demandas.py.
"""
import glob, json, os, re, sqlite3, unicodedata
from datetime import date, timedelta

AP = os.path.expanduser("~/agentes-partners")
DADOS = os.path.join(AP, "departamentos/resultados/dados")
MAPA = os.path.join(AP, "departamentos/resultados/mapeamento-hubspot.json")
RECEITA_DB = os.path.join(AP, "dados-publicos/receita/cnpj.sqlite")
LINK = "https://app.hubspot.com/contacts/47865021/deal/{}"
from cnpj import cnpj_valido as _cnpj_valido, normalizar_cnpj  # noqa: E402


def norm(s):
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower().strip()


# ---------- HubSpot: um download por dia ----------
def ultimo_download():
    """(caminho, dados) do hubspot-*.json mais recente (o do dia, baixado por `partners hubspot`)."""
    fs = sorted(glob.glob(os.path.join(DADOS, "hubspot-*.json")))
    if not fs: raise SystemExit("Sem download do HubSpot: rode `partners hubspot`.")
    return fs[-1], json.load(open(fs[-1]))


# ---------- CNPJ (numérico e alfanumérico: regra em lib/cnpj.py) ----------
def cnpj_digitos(c):
    """CNPJ normalizado (letras preservadas no formato alfanumérico), com os zeros à esquerda recompostos."""
    d = normalizar_cnpj(c)
    return d.zfill(14) if 8 < len(d) < 14 else d


cnpj_valido = _cnpj_valido


def raiz(c):
    c = cnpj_digitos(c)
    return c[:8] if len(c) >= 8 else ""


def receita(cnpj):
    """Cadastro oficial (base local, somente leitura). CNPJ de cliente nunca vai para serviço externo."""
    if not os.path.exists(RECEITA_DB): return None
    c = cnpj_digitos(cnpj)
    con = sqlite3.connect(f"file:{RECEITA_DB}?mode=ro", uri=True); con.row_factory = sqlite3.Row
    r = con.execute("""select e.cnpj, e.fantasia, e.situacao, e.data_situacao, e.inicio, e.cnae, e.uf, e.municipio, e.matriz,
                       m.razao, m.capital, m.porte, s.simples, s.mei,
                       (select descricao from ref where tipo='cnae' and codigo=e.cnae) as cnae_desc,
                       (select descricao from ref where tipo='municipio' and codigo=e.municipio) as municipio_desc
                       from estab e left join empresa m on m.basico=e.basico left join simples s on s.basico=e.basico
                       where e.cnpj=? or (e.basico=? and e.matriz IN ('1','matriz')) order by (e.cnpj=?) desc limit 1""", (c, c[:8], c)).fetchone()
    con.close()
    return dict(r) if r else None


# ---------- Regras de negócio ----------
def regras():
    return json.load(open(MAPA)).get("regras", {})


def e_cafe(d, R=None):
    """Café fora da meta desde abr/2026: por CNAE e pelo nome (regra em mapeamento-hubspot.json)."""
    R = R or regras()
    pal = [norm(p) for p in R.get("cafe_palavras", [])]
    txt = norm((d.get("nome") or "") + " " + (d.get("segmento") or ""))
    cn = re.sub(r"\D", "", d.get("cnae") or "")
    return any(p and p in txt for p in pal) or any(cn.startswith(x) for x in (R.get("cafe_cnae") or R.get("cafe_cnaes") or []))


def data_efetiva(d):
    """A menor entre criação e fechamento (as importações regravaram a criação)."""
    ds = [x[:10] for x in (d.get("criado"), d.get("fechado")) if x]
    return min(ds) if ds else None


def ativo(negocios_do_parceiro, hoje=None, dias=90):
    """Parceiro ativo = ao menos 1 negócio com data efetiva nos últimos 90 dias (dicionário em metricas.md)."""
    corte = ((hoje or date.today()) - timedelta(days=dias)).isoformat()
    return any((data_efetiva(d) or "") >= corte for d in negocios_do_parceiro)
