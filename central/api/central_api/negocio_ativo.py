"""Primeira checagem da consulta: a empresa já tem negócio na base Save Company?

"Negócio ativo" = negócio aberto ou ganho no HubSpot, em qualquer pipeline, pela raiz do CNPJ (8 primeiros
caracteres: matriz e filiais). É a mesma regra do conflito de canal (skills/depto-operacoes-canal/scripts/conflito_canal.py).

O site e a API nunca veem a lista de clientes: veem um índice de chaves (HMAC-SHA256 da raiz com um sal secreto,
CENTRAL_SAL). Quem monta o índice é a rotina "Dados do dia" (tem o HUBSPOT_TOKEN); o índice viaja pelo estado
dos agentes (lib/estado.py → SharePoint) e nunca vai para o GitHub.

Falha fechada: sem índice, a consulta NÃO chama API externa (não dá para saber se o CNPJ é de cliente, e CNPJ de
cliente não sai para serviço de terceiros).

Regra de "ativo": qualquer negócio aberto ou ganho, de qualquer idade (conferido em 23/10/2026: 371 das 1.030 raízes
só têm ganho com mais de 1 ano; a relação comercial e o conflito de canal não expiram com o tempo). Perdido nunca bloqueia.

Uso:  python3 negocio_ativo.py construir [--arquivo hubspot-AAAA-MM-DD.json]
      python3 negocio_ativo.py status      (idade do índice; sai com 1 se não existe ou tem mais de 3 dias)
"""
import argparse, datetime, glob, hashlib, hmac, json, logging, os, secrets, sys, time, unicodedata

from .caminhos import dados as _dados, preparar_lib  # noqa: E402  (L5: caminhos por variável)
preparar_lib()
from cnpj import cnpj_valido, normalizar_cnpj, raiz_cnpj  # noqa: E402

log = logging.getLogger("central_api.negocio_ativo")
DIR = os.path.expanduser(os.environ.get("CENTRAL_ESTEIRA") or str(_dados() / "central-esteira"))
INDICE = os.path.join(DIR, "indice-negocios-ativos.json")
STATUS_ATIVOS = {"aberto", "ganho"}
STATUS_CONHECIDOS = STATUS_ATIVOS | {"perdido"}
MSG_NEUTRA = "Não foi possível seguir com esta consulta. Fale com a Área Partners."  # única resposta para negócio ativo, índice ausente e tetos
IDADE_MAX_DIAS = 3
_cache = {"mtime": None, "chaves": None, "sal_id": None}


def _status(v):
    """'Ganho ', 'GANHO', 'ganhó' → 'ganho' (sem caixa, acento nem espaços)."""
    t = unicodedata.normalize("NFKD", str(v or "")).encode("ascii", "ignore").decode()
    return t.strip().lower()


def _sal():
    s = os.environ.get("CENTRAL_SAL")
    if s:
        return s
    arq = os.path.join(DIR, "sal.key")  # local: gerado uma vez, só do dono (600). Na nuvem vem do segredo CENTRAL_SAL.
    os.makedirs(DIR, exist_ok=True)
    if not os.path.exists(arq):
        try:
            fd = os.open(arq, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w") as f:
                f.write(secrets.token_hex(32))
        except FileExistsError:  # outro processo criou ao mesmo tempo
            pass
    if os.stat(arq).st_mode & 0o077:
        os.chmod(arq, 0o600)
        log.warning("sal.key estava com permissão aberta; corrigida para 600")
    with open(arq) as f:
        s = f.read().strip()
    if len(s) < 32:
        raise RuntimeError("sal.key vazio ou curto: apague para gerar de novo e reconstrua o índice")
    return s


def sal_id():
    """Identificador curto do sal (não permite recuperá-lo): detecta índice montado com outro sal."""
    return hmac.new(_sal().encode(), b"sal-id", hashlib.sha256).hexdigest()[:8]


def chave(raiz):
    return hmac.new(_sal().encode(), raiz.encode(), hashlib.sha256).hexdigest()[:32]


def raiz_do_negocio(d):
    """(raiz, motivo_de_exclusao): raiz do CNPJ válido do negócio, ou None com o motivo."""
    c = normalizar_cnpj((d.get("extras") or {}).get("cnpj"))
    if not c:
        return None, "sem_cnpj"
    if not cnpj_valido(c):  # cnpj_valido já completa zeros perdidos (8 < tamanho < 14)
        return None, "cnpj_invalido"
    return raiz_cnpj(c), None


def construir(negocios, baixado_em=None, fonte=None):
    """Índice a partir dos negócios do download do HubSpot (campo extras.cnpj, status aberto/ganho)."""
    raizes, excl, desconhecidos = set(), {"sem_cnpj": 0, "cnpj_invalido": 0}, {}
    for d in negocios:
        st = _status(d.get("status"))
        if st not in STATUS_CONHECIDOS:
            desconhecidos[st] = desconhecidos.get(st, 0) + 1
            log.warning("status desconhecido no download do HubSpot (%d ocorrência(s)): %r", desconhecidos[st], st)
        if st not in STATUS_ATIVOS:
            continue
        r, motivo = raiz_do_negocio(d)
        if r:
            raizes.add(r)
        else:
            excl[motivo] += 1
    return {"gerado_em": time.strftime("%Y-%m-%dT%H:%M:%S"), "fonte": fonte, "fonte_baixada_em": baixado_em,
            "sal_id": sal_id(), "total": len(raizes), "negocios_fora_do_indice": excl,
            "status_desconhecidos": desconhecidos, "chaves": sorted(chave(r) for r in raizes)}


def gravar(idx, caminho=None):
    """Grava de forma atômica (arquivo temporário 600 + os.replace): quem lê vê o índice velho ou o novo, nunca meio."""
    caminho = caminho or INDICE
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    tmp = "%s.%d.tmp" % (caminho, os.getpid())
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(idx, fh)
            fh.flush(); os.fsync(fh.fileno())
        os.replace(tmp, caminho)
    except BaseException:
        try: os.unlink(tmp)
        except OSError: pass
        raise


def _ler():
    with open(INDICE) as f:
        return json.load(f)


def idade_dias(idx=None):
    """Idade do índice em dias (da data do download do HubSpot; se faltar, da geração). None sem índice."""
    try:
        idx = idx or _ler()
    except (OSError, ValueError):
        return None
    ref = idx.get("fonte_baixada_em") or idx.get("gerado_em")
    try:
        t = datetime.datetime.fromisoformat(str(ref)[:19])
    except ValueError:
        return None
    return round((datetime.datetime.now() - t).total_seconds() / 86400, 2)


def _carregar():
    """Conjunto de chaves, ou None se não houver índice utilizável (ausente, corrompido ou de outro sal)."""
    try:
        m = os.path.getmtime(INDICE)
    except OSError:
        return None
    if _cache["mtime"] != m:
        try:
            idx = _ler()
            chaves = set(idx["chaves"])
            ok = idx.get("sal_id") in (None, sal_id())  # índices antigos não têm sal_id
        except (OSError, ValueError, KeyError, TypeError) as e:
            log.error("índice de negócios ativos ilegível (%s): consulta falha fechada", type(e).__name__)
            return None
        if not ok:
            log.error("índice de negócios ativos foi montado com outro sal: consulta falha fechada; reconstrua")
            return None
        _cache.update(mtime=m, chaves=chaves, avisou=False)
    idade = idade_dias()
    if idade is not None and idade > IDADE_MAX_DIAS and not _cache.get("avisou"):
        _cache["avisou"] = True
        log.warning("índice de negócios ativos com %.1f dias (limite %d): rode a rotina Dados do dia", idade, IDADE_MAX_DIAS)
    return _cache["chaves"]


def tem_negocio_ativo(cnpj):
    """True / False, ou None quando o índice não existe (quem chama deve falhar fechado).
    Índice velho (> 3 dias) só gera aviso no log: a checagem continua."""
    chaves = _carregar()
    if chaves is None:
        return None
    r = raiz_cnpj(normalizar_cnpj(cnpj))
    if not r:
        return False
    k = chave(r)
    achou = False
    for x in chaves:  # compare_digest em todas as chaves: o tempo não depende de onde (nem se) a chave está
        achou |= hmac.compare_digest(x, k)
    return achou


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["construir", "status"]); ap.add_argument("--arquivo")
    a = ap.parse_args()
    if a.cmd == "status":
        idade = idade_dias()
        if idade is None:
            print("índice ausente ou ilegível"); sys.exit(1)
        i = _ler()
        print("índice com %s raízes, %.1f dia(s) de idade (limite %d), fora do índice: %s" % (
            i.get("total"), idade, IDADE_MAX_DIAS, i.get("negocios_fora_do_indice")))
        sys.exit(1 if idade > IDADE_MAX_DIAS else 0)
    f = a.arquivo or sorted(glob.glob(str(_dados() / "departamentos/resultados/dados/hubspot-*.json")))[-1]
    with open(f) as fh:
        dados = json.load(fh)
    idx = construir(dados["negocios"], dados.get("baixado_em"), os.path.basename(f))
    gravar(idx)
    print("índice com %d raízes (de %s); fora do índice: %s; status desconhecidos: %s" % (
        idx["total"], os.path.basename(f), idx["negocios_fora_do_indice"], idx["status_desconhecidos"] or "nenhum"))


if __name__ == "__main__":
    main()
