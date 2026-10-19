"""Rotas da API da Central sem dependência do Azure Functions (testáveis e usadas pelo servidor local).

Cada rota recebe os cabeçalhos HTTP e devolve (status, corpo). function_app.py e dev_server.py só fazem a ponte.
Etapa 2 do plano: GET /api/eu e GET /api/painel. As gravações (etapa 3) entram aqui com auditoria.
"""
import json, logging, os

from . import permissoes as P
from .token import Chaves, Config, TokenInvalido, extrair_bearer, validar

log = logging.getLogger("central")
_CFG = _CHAVES = None


def contexto(cfg=None, chaves=None):
    """Config e cache de chaves do processo (os testes injetam os seus)."""
    global _CFG, _CHAVES
    if cfg is not None:
        _CFG, _CHAVES = cfg, chaves or Chaves(cfg.jwks_url)
    if _CFG is None:
        _CFG = Config(); _CHAVES = Chaves(_CFG.jwks_url)
    return _CFG, _CHAVES


def _autenticar(cabecalhos):
    cfg, chaves = contexto()
    return validar(extrair_bearer(cabecalhos), cfg, chaves)


def _resposta(fn, cabecalhos, acao):
    try:
        ident = _autenticar(cabecalhos)
        P.exigir(ident, acao)
        return 200, fn(ident)
    except TokenInvalido as e:
        log.info("401 %s", e)
        return 401, {"erro": "não autenticado", "detalhe": str(e)}
    except P.SemPermissao as e:
        log.warning("403 acao=%s motivo=%s", acao, e)
        return 403, {"erro": "sem permissão", "detalhe": str(e)}


def eu(cabecalhos):
    """Quem está logado, com quais papéis e como pessoa da Central."""
    return _resposta(lambda i: {**i, "pessoa": P.pessoa(i), "pode": sorted(a for a, ps in P.ACOES.items() if ps & set(i["papeis"]))},
                     cabecalhos, "ver_painel")


def painel(cabecalhos, carregar=None):
    """Dados do painel filtrados pelo papel. `carregar` devolve o dados.json (injetável)."""
    def corpo(i):
        dados = (carregar or _carregar_dados)()
        if P.LEITURA in i["papeis"] and not ({P.GESTOR, P.MASTERS, P.BDR, P.TECNICA} & set(i["papeis"])):
            return {"atualizado": dados.get("atualizado"), "resumo": dados.get("resumo", {})}  # só agregado
        pes = P.pessoa(i)
        if pes == "luis":
            return dados
        return {k: (v.get(pes) if isinstance(v, dict) and pes in v else v) for k, v in dados.items()}
    return _resposta(corpo, cabecalhos, "ver_painel")


def _carregar_dados():
    f = os.environ.get("CENTRAL_DADOS", "")
    return json.load(open(f)) if f and os.path.exists(f) else {"atualizado": None, "resumo": {}}
