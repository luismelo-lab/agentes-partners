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


# ---------------------------------------------------------------- PRM e esteira atrás do token (lacuna L1)
# As rotas que só existiam no consulta_demo.py (usuário fixo "demo-local", sem login) passam a exigir identidade:
# o usuário vem do oid (Save) ou da tabela usuario_parceiro (parceiro). Mesmo teto persistente e mesma trilha do PRM.
def prm(metodo, caminho, cabecalhos, corpo=None, consulta=None):
    """Todas as rotas /api/prm/* (contrato em docs/prm/v2/06-contrato-api.md)."""
    from .prm import rotas as R
    return R.despachar(metodo, caminho, cabecalhos, corpo, consulta)


def _esteira(cabecalhos, fn):
    from .prm import rotas as R
    from .prm.erros import PRMErro
    from .prm.identidade import autenticar, exigir
    app = R.obter_app()
    try:
        a = autenticar(app, cabecalhos)
        exigir(a, "consultar_empresa")
        return fn(app, a, a.usuario_id or a.rotulo())
    except PRMErro as e:
        return e.status, e.corpo()


def regime_lote(cabecalhos, corpo):
    """POST /api/regime {cnpjs: [...]} — a consulta de Lucro Real, agora com login, teto persistente e trilha com HMAC."""
    from .prm import portal as PT
    return _esteira(cabecalhos, lambda app, a, u: (200, PT.consultar(app, a, (corpo or {}).get("cnpjs"))))


def esteira_pedir(cabecalhos, corpo):
    """POST /api/esteira {cnpj} — pedido de análise e esteira (dossiê-base na hora), com o usuário do token."""
    from . import esteira as E
    from .prm import portal as PT

    def f(app, a, u):
        cnpj = (corpo or {}).get("cnpj")
        if not isinstance(cnpj, str):
            return 400, {"erro": "Informe o CNPJ."}
        res = PT.consultar(app, a, [cnpj])["resultados"][0]
        guardada = E.consulta_guardada(u, cnpj)
        if res.get("neutra") or not guardada:
            return 400, {"erro": res.get("titulo") or "Não foi possível seguir com esta consulta. Fale com a Área Partners."}
        try:
            return 200, E.visao_parceiro(E.solicitar(cnpj, u, guardada))
        except E.Recusa as e:
            return 400, {"erro": str(e)}
    return _esteira(cabecalhos, f)


def esteira_andamento(cabecalhos, ident):
    from . import esteira as E
    return _esteira(cabecalhos, lambda app, a, u: (lambda v: (200, v) if v else (404, {"erro": "pedido não encontrado"}))(E.ler_do_parceiro(ident, u)))


def esteira_historico(cabecalhos):
    from . import esteira as E
    return _esteira(cabecalhos, lambda app, a, u: (200, {"empresas": E.historico(u)}))


def esteira_arquivo(cabecalhos, ident):
    """(status, corpo) com {"_arquivo": caminho} quando há Word; só o dono do pedido baixa."""
    from . import esteira as E

    def f(app, a, u):
        arq = E.arquivo_do_parceiro(ident, u)
        if not arq:
            return 404, {"erro": "arquivo não encontrado"}
        return 200, {"_arquivo": arq, "_nome": "dossie-%s.docx" % ident, "_tipo": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    return _esteira(cabecalhos, f)
