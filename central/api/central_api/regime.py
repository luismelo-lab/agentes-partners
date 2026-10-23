"""Consulta de regime tributário (Lucro Real) para o parceiro.

Fontes, nesta ordem, só locais (nada sai do Mac nesta demo):
  1. base da Receita (cnpj.sqlite): existência, situação, porte, Simples/MEI;
  2. cache do regime (regime-cache.json, gerado pelo receita_cnpj.py --regime a partir da Minha Receita,
     que repete a ECF): "LUCRO REAL (2024)".
Cada resposta traz a faixa, a fonte e o ano-base. O regime da ECF é o do ano anterior: não é "o regime de hoje".

Faixas: confirmado_real | provavel_real | nao_real | sem_dado | invalido.
"""
import contextlib, json, os, re, sqlite3, sys, time
from datetime import date

sys.path.insert(0, os.path.expanduser("~/agentes-partners/lib"))
from cnpj import cnpj_valido, normalizar_cnpj  # noqa: E402

BASE = os.path.expanduser(os.environ.get("CENTRAL_RECEITA", "~/agentes-partners/dados-publicos/receita"))
LIMITE_LOTE = 50
LIMITE_DIA = int(os.environ.get("CENTRAL_LIMITE_DIA", "200"))
TETO_PRESUMIDO = 78_000_000  # Lei 9.718/1998, art. 13 e art. 14, I
SITUACAO = {"01": "Nula", "02": "Ativa", "03": "Suspensa", "04": "Inapta", "08": "Baixada"}
PORTE = {"00": "Não informado", "01": "Microempresa", "03": "Empresa de Pequeno Porte", "05": "Demais"}
_ANO = re.compile(r"^(.*?)\s*\((\d{4})\)\s*$")

_cache = {"mtime": None, "dados": {}}
_uso = {}


def _regimes():
    p = os.path.join(BASE, "regime-cache.json")
    try:
        m = os.path.getmtime(p)
    except OSError:
        return {}
    if _cache["mtime"] != m:
        with open(p) as f:
            _cache.update(mtime=m, dados=json.load(f))
    return _cache["dados"]


def _fonte_regime():
    p = os.path.join(BASE, "regime-cache.json")
    return date.fromtimestamp(os.path.getmtime(p)).isoformat() if os.path.exists(p) else None


def _db():
    return sqlite3.connect("file:%s?mode=ro" % os.path.join(BASE, "cnpj.sqlite"), uri=True)


def _regime_do_cache(cnpj, basico):
    """Regime do CNPJ; se for filial e não houver, o da matriz (o regime é da raiz)."""
    r = _regimes()
    texto = r.get(cnpj) or r.get(basico + "0001" + cnpj[12:]) or next((v for k, v in r.items() if k.startswith(basico)), None)
    if not texto:
        return None, None
    m = _ANO.match(texto)
    nome, ano = (m.group(1).strip(), int(m.group(2))) if m else (texto.strip(), None)
    return (None, None) if nome.lower() == "sem registro" else (nome.title(), ano)  # "sem registro" = a ECF não trouxe


def consultar(entrada, faturamento=None):
    bruto = str(entrada or "")
    cnpj = normalizar_cnpj(bruto)
    saida = {"cnpj": cnpj, "faixa": "invalido", "titulo": "CNPJ inválido", "fonte": None, "ano_base": None, "empresa": None}
    if not cnpj_valido(cnpj):
        saida["detalhe"] = "Confira os 14 caracteres e os dois dígitos finais."
        return saida
    basico = cnpj[:8]
    with contextlib.closing(_db()) as db:
        est = db.execute("SELECT situacao, uf, municipio, matriz FROM estab WHERE cnpj=?", (cnpj,)).fetchone()
        emp = db.execute("SELECT razao, porte FROM empresa WHERE basico=?", (basico,)).fetchone()
        sim = db.execute("SELECT simples, mei FROM simples WHERE basico=?", (basico,)).fetchone()
    if emp:
        saida["empresa"] = {"razao": emp[0], "porte": PORTE.get(emp[1], emp[1]),
                            "situacao": SITUACAO.get(est[0], est[0]) if est else None,
                            "uf": est[1] if est else None, "matriz": bool(est and est[3] == "matriz")}
    regime, ano = _regime_do_cache(cnpj, basico)
    simples = bool(sim and sim[0] == "S"); mei = bool(sim and sim[1] == "S")
    saida["simples"] = simples or mei
    if regime and "real" in regime.lower() and "/" in regime:
        saida.update(faixa="provavel_real", titulo="Provável Lucro Real: regime misto no ano", ano_base=ano, fonte="ECF, via Minha Receita (cache de %s)" % _fonte_regime(),
                     detalhe="A ECF do ano-base %s traz mais de um regime (%s). Confirme com o cliente." % (ano or "informado", regime))
    elif regime and "real" in regime.lower():
        saida.update(faixa="confirmado_real", titulo="Lucro Real confirmado", ano_base=ano, fonte="ECF, via Minha Receita (cache de %s)" % _fonte_regime(),
                     detalhe="Regime declarado na ECF do ano-base %s. Não garante que o regime seja o mesmo hoje." % (ano or "informado"))
    elif simples or mei:
        saida.update(faixa="nao_real", titulo="Não é Lucro Real: Simples Nacional" if not mei else "Não é Lucro Real: MEI", fonte="Receita Federal, opção pelo Simples (base local)",
                     detalhe="A opção pelo Simples vale na data da base. A recuperação de PIS/COFINS não cumulativo não se aplica.")
    elif regime:
        saida.update(faixa="nao_real", titulo="Não é Lucro Real: %s" % regime, ano_base=ano, fonte="ECF, via Minha Receita (cache de %s)" % _fonte_regime(),
                     detalhe="Regime declarado na ECF do ano-base %s." % (ano or "informado"))
    elif faturamento and faturamento > TETO_PRESUMIDO:
        saida.update(faixa="provavel_real", titulo="Provável Lucro Real", fonte="Faturamento informado por você",
                     detalhe="Receita bruta acima de R$ 78 milhões obriga ao Lucro Real (Lei 9.718/1998, art. 14, I), salvo exceções. Falta a confirmação pela ECF.")
    elif emp:
        saida.update(faixa="sem_dado", titulo="Sem dado de regime", fonte="Base local da Receita",
                     detalhe="A empresa existe na base, mas o regime não está no cache e não é Simples. Peça a ECF ao cliente.")
    else:
        saida.update(faixa="sem_dado", titulo="Sem dado", fonte="Base local da Receita",
                     detalhe="Este CNPJ não está na base local, que cobre só os segmentos de interesse. Isso não quer dizer que a empresa não exista.")
    return saida


def registrar_uso(usuario, qtd):
    """Teto diário por usuário (contagem em memória na demo). Devolve (permitido, usadas, limite)."""
    chave = (usuario, date.today().isoformat())
    usado = _uso.get(chave, 0)
    if usado + qtd > LIMITE_DIA:
        return False, usado, LIMITE_DIA
    _uso[chave] = usado + qtd
    return True, usado + qtd, LIMITE_DIA


def auditar(usuario, resultados, arquivo=None):
    """Quem consultou, o quê e quando. Fica em dados-publicos (fora do git)."""
    arq = arquivo or os.path.join(BASE, "consultas-regime.jsonl")
    with open(arq, "a") as f:
        for r in resultados:
            f.write(json.dumps({"quando": time.strftime("%Y-%m-%dT%H:%M:%S"), "usuario": usuario, "cnpj": r["cnpj"], "faixa": r["faixa"]}, ensure_ascii=False) + "\n")
    os.chmod(arq, 0o600)
