"""Primeira checagem da consulta: a empresa já tem negócio na base Save Company?

"Negócio ativo" = negócio aberto ou ganho no HubSpot, em qualquer pipeline, pela raiz do CNPJ (8 primeiros
caracteres: matriz e filiais). É a mesma regra do conflito de canal (skills/depto-operacoes-canal/scripts/conflito_canal.py).

O site e a API nunca veem a lista de clientes: veem um índice de chaves (HMAC-SHA256 da raiz com um sal secreto,
CENTRAL_SAL). Quem monta o índice é a rotina "Dados do dia" (tem o HUBSPOT_TOKEN); o índice viaja pelo estado
dos agentes (lib/estado.py → SharePoint) e nunca vai para o GitHub.

Falha fechada: sem índice, a consulta NÃO chama API externa (não dá para saber se o CNPJ é de cliente, e CNPJ de
cliente não sai para serviço de terceiros).

Uso:  python3 negocio_ativo.py construir [--arquivo hubspot-AAAA-MM-DD.json]
"""
import argparse, glob, hashlib, hmac, json, os, secrets, sys, time

sys.path.insert(0, os.path.expanduser("~/agentes-partners/lib"))
from cnpj import cnpj_valido, normalizar_cnpj, raiz_cnpj  # noqa: E402

DIR = os.path.expanduser(os.environ.get("CENTRAL_ESTEIRA", "~/agentes-partners/central-esteira"))
INDICE = os.path.join(DIR, "indice-negocios-ativos.json")
STATUS_ATIVOS = {"aberto", "ganho"}
_cache = {"mtime": None, "chaves": None}


def _sal():
    s = os.environ.get("CENTRAL_SAL")
    if s:
        return s
    arq = os.path.join(DIR, "sal.key")  # local: gerado uma vez, só do dono (600). Na nuvem vem do segredo CENTRAL_SAL.
    if not os.path.exists(arq):
        os.makedirs(DIR, exist_ok=True)
        fd = os.open(arq, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(secrets.token_hex(32))
    with open(arq) as f:
        return f.read().strip()


def chave(raiz):
    return hmac.new(_sal().encode(), raiz.encode(), hashlib.sha256).hexdigest()[:32]


def construir(negocios):
    """Índice a partir dos negócios do download do HubSpot (campo extras.cnpj, status, aberto/ganho)."""
    raizes = set()
    for d in negocios:
        if d.get("status") not in STATUS_ATIVOS:
            continue
        c = normalizar_cnpj((d.get("extras") or {}).get("cnpj"))
        c = c.zfill(14) if c.isdigit() and 8 < len(c) < 14 else c  # o HubSpot e o Excel perdem os zeros iniciais
        if cnpj_valido(c):
            raizes.add(raiz_cnpj(c))
    return {"gerado_em": time.strftime("%Y-%m-%dT%H:%M:%S"), "total": len(raizes), "chaves": sorted(chave(r) for r in raizes)}


def _carregar():
    """Conjunto de chaves, ou None se não houver índice."""
    try:
        m = os.path.getmtime(INDICE)
    except OSError:
        return None
    if _cache["mtime"] != m:
        with open(INDICE) as f:
            _cache.update(mtime=m, chaves=set(json.load(f).get("chaves", [])))
    return _cache["chaves"]


def tem_negocio_ativo(cnpj):
    """True / False, ou None quando o índice não existe (quem chama deve falhar fechado)."""
    chaves = _carregar()
    if chaves is None:
        return None
    r = raiz_cnpj(normalizar_cnpj(cnpj))
    return bool(r) and chave(r) in chaves


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["construir"]); ap.add_argument("--arquivo")
    a = ap.parse_args()
    f = a.arquivo or sorted(glob.glob(os.path.expanduser("~/agentes-partners/departamentos/resultados/dados/hubspot-*.json")))[-1]
    with open(f) as fh:
        idx = construir(json.load(fh)["negocios"])
    os.makedirs(DIR, exist_ok=True)
    with open(INDICE, "w") as fh:
        json.dump(idx, fh)
    os.chmod(INDICE, 0o600)
    print("índice com %d raízes (de %s)" % (idx["total"], os.path.basename(f)))


if __name__ == "__main__":
    main()
