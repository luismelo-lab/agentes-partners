#!/usr/bin/env python3
"""Demo local da consulta de Lucro Real para parceiros. SEM login: só para testar tela e texto.

    python3 central/consulta_demo.py        → http://localhost:4281/consulta.html

Usa a base da Receita e o cache de regime locais (nada sai do Mac). No piloto, as mesmas funções de
central_api/regime.py entram em rotas.py atrás do token do Entra (papel e teto de consultas por parceiro).
Só escuta em localhost.
"""
import http.server, json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__)); WEB = os.path.join(AQUI, "web")
sys.path.insert(0, os.path.join(AQUI, "api"))
from central_api import regime  # noqa: E402

CAB = json.load(open(os.path.join(WEB, "staticwebapp.config.json")))["globalHeaders"]
CAB = {k: v for k, v in CAB.items() if k != "Strict-Transport-Security"}
CAB["Content-Security-Policy"] = CAB["Content-Security-Policy"].replace("connect-src 'self' https://login.microsoftonline.com", "connect-src 'self'")
USUARIO = "demo-local"


def numero(v):
    try:
        return float(str(v).replace(".", "").replace(",", ".")) if v not in (None, "") else None
    except ValueError:
        return None


def lote(corpo):
    cnpjs = [str(c) for c in (corpo.get("cnpjs") or []) if str(c).strip()][:regime.LIMITE_LOTE + 1]
    if not cnpjs:
        return 400, {"erro": "Informe ao menos um CNPJ."}
    if len(cnpjs) > regime.LIMITE_LOTE:
        return 400, {"erro": "No máximo %d CNPJs por consulta." % regime.LIMITE_LOTE}
    ok, usadas, limite = regime.registrar_uso(USUARIO, len(cnpjs))
    if not ok:
        return 429, {"erro": "Limite diário de %d consultas atingido (%d usadas)." % (limite, usadas)}
    fat = numero(corpo.get("faturamento")) if len(cnpjs) == 1 else None
    res = [regime.consultar(c, fat) for c in cnpjs]
    regime.auditar(USUARIO, res)
    return 200, {"resultados": res, "usadas": usadas, "limite": limite}


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=WEB, **k)

    def end_headers(self):
        for k, v in CAB.items(): self.send_header(k, v)
        super().end_headers()

    def do_POST(self):
        if self.path.split("?")[0] != "/api/regime":
            return self._json(404, {"erro": "rota não encontrada"})
        try:
            n = min(int(self.headers.get("Content-Length", 0)), 20000)
            corpo = json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return self._json(400, {"erro": "corpo inválido"})
        self._json(*lote(corpo))

    def _json(self, st, corpo):
        b = json.dumps(corpo, ensure_ascii=False).encode()
        self.send_response(st); self.send_header("Content-Type", "application/json"); self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def log_message(self, fmt, *a): sys.stderr.write("%s %s\n" % (self.command, self.path.split("?")[0]))  # sem CNPJ no log


if __name__ == "__main__":
    print("Demo da consulta em http://localhost:4281/consulta.html  (Ctrl+C para parar)")
    http.server.ThreadingHTTPServer(("localhost", 4281), H).serve_forever()
