"""Azure Functions (modelo Python v2): ponte HTTP → central_api.rotas. A lógica e os testes ficam em central_api/."""
import json

import azure.functions as func

from central_api import rotas

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)  # a autenticação é o token do Entra, validado em rotas


def _http(status, corpo):
    return func.HttpResponse(json.dumps(corpo, ensure_ascii=False), status_code=status, mimetype="application/json",
                             headers={"Cache-Control": "no-store"})


@app.route(route="eu", methods=["GET"])
def eu(req: func.HttpRequest) -> func.HttpResponse:
    return _http(*rotas.eu(dict(req.headers)))


@app.route(route="painel", methods=["GET"])
def painel(req: func.HttpRequest) -> func.HttpResponse:
    return _http(*rotas.painel(dict(req.headers)))
