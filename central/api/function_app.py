"""Azure Functions (modelo Python v2): ponte HTTP → central_api.rotas. A lógica e os testes ficam em central_api/.

Nunca liga o login simulado do servidor local: a Azure define WEBSITE_INSTANCE_ID e o Host é o domínio da Save, as duas
travas de central_api/prm/identidade.login_simulado_ativo. A variável PRM_LOGIN_SIMULADO é apagada aqui por garantia.
"""
import json, os

import azure.functions as func

from central_api import rotas

os.environ.pop("PRM_LOGIN_SIMULADO", None)
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)  # a autenticação é o token do Entra, validado em rotas
LIMITE_CORPO = 20000


def _http(status, corpo):
    if isinstance(corpo, dict) and corpo.get("_arquivo"):
        with open(corpo["_arquivo"], "rb") as f:
            b = f.read()
        return func.HttpResponse(b, status_code=status, mimetype=corpo["_tipo"],
                                 headers={"Cache-Control": "no-store", "Content-Disposition": 'attachment; filename="%s"' % corpo["_nome"]})
    return func.HttpResponse(json.dumps(corpo, ensure_ascii=False), status_code=status, mimetype="application/json",
                             headers={"Cache-Control": "no-store"})


def _corpo(req):
    """JSON do POST. Exige application/json (página de outro site não consegue postar sem preflight) e limita o tamanho."""
    if (req.headers.get("Content-Type") or "").split(";")[0].strip().lower() != "application/json":
        return None, (415, {"erro": "use application/json"})
    b = req.get_body() or b"{}"
    if len(b) > LIMITE_CORPO:
        return None, (413, {"erro": "corpo inválido"})
    try:
        c = json.loads(b)
    except ValueError:
        return None, (400, {"erro": "corpo inválido"})
    return (c, None) if isinstance(c, dict) else (None, (400, {"erro": "corpo inválido"}))


@app.route(route="eu", methods=["GET"])
def eu(req: func.HttpRequest) -> func.HttpResponse:
    return _http(*rotas.eu(dict(req.headers)))


@app.route(route="painel", methods=["GET"])
def painel(req: func.HttpRequest) -> func.HttpResponse:
    return _http(*rotas.painel(dict(req.headers)))


@app.route(route="prm/{*resto}", methods=["GET", "POST"])
def prm(req: func.HttpRequest) -> func.HttpResponse:
    corpo = None
    if req.method == "POST":
        corpo, erro = _corpo(req)
        if erro:
            return _http(*erro)
    caminho = "/api/prm/" + (req.route_params.get("resto") or "")
    return _http(*rotas.prm(req.method, caminho, dict(req.headers), corpo, dict(req.params)))


@app.route(route="regime", methods=["POST"])
def regime(req: func.HttpRequest) -> func.HttpResponse:
    corpo, erro = _corpo(req)
    return _http(*(erro or rotas.regime_lote(dict(req.headers), corpo)))


@app.route(route="esteira", methods=["GET", "POST"])
def esteira(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "GET":
        return _http(*rotas.esteira_andamento(dict(req.headers), req.params.get("id") or ""))
    corpo, erro = _corpo(req)
    return _http(*(erro or rotas.esteira_pedir(dict(req.headers), corpo)))


@app.route(route="esteira/historico", methods=["GET"])
def esteira_historico(req: func.HttpRequest) -> func.HttpResponse:
    return _http(*rotas.esteira_historico(dict(req.headers)))


@app.route(route="esteira/arquivo", methods=["GET"])
def esteira_arquivo(req: func.HttpRequest) -> func.HttpResponse:
    return _http(*rotas.esteira_arquivo(dict(req.headers), req.params.get("id") or ""))
