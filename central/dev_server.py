#!/usr/bin/env python3
"""Servidor local da Central para testar o SSO antes do Azure: serve web/ e responde /api/* com a mesma lógica da API.

    python3 central/dev_server.py        → http://localhost:4280/  (URI de redirecionamento de desenvolvimento no Entra)

Lê os IDs de central/api/local.settings.json (fora do repositório). Aplica os mesmos cabeçalhos de segurança do
staticwebapp.config.json, para a CSP ser testada aqui também. Só escuta em localhost.
"""
import http.server, json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__)); WEB = os.path.join(AQUI, "web")
cfg = os.path.join(AQUI, "api", "local.settings.json")
if not os.path.exists(cfg): sys.exit("Crie central/api/local.settings.json a partir do local.settings.example.json.")
os.environ.update({k: v for k, v in json.load(open(cfg))["Values"].items() if v})
sys.path.insert(0, os.path.join(AQUI, "api"))
from central_api import rotas  # noqa: E402

CAB = json.load(open(os.path.join(WEB, "staticwebapp.config.json")))["globalHeaders"]
CAB = {k: v for k, v in CAB.items() if k != "Strict-Transport-Security"}  # localhost é http
ROTAS = {"/api/eu": rotas.eu, "/api/painel": rotas.painel}


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=WEB, **k)

    def end_headers(self):
        for k, v in CAB.items(): self.send_header(k, v)
        super().end_headers()

    def do_GET(self):
        rota = self.path.split("?")[0]
        if rota.startswith("/api/"):
            fn = ROTAS.get(rota)
            st, corpo = fn(dict(self.headers)) if fn else (404, {"erro": "rota não encontrada"})
            b = json.dumps(corpo, ensure_ascii=False).encode()
            self.send_response(st); self.send_header("Content-Type", "application/json"); self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b); return
        return super().do_GET()

    def log_message(self, fmt, *a): sys.stderr.write("%s %s\n" % (self.command, self.path.split("?")[0]))


if __name__ == "__main__":
    print("Central local em http://localhost:4280/  (Ctrl+C para parar)")
    http.server.ThreadingHTTPServer(("localhost", 4280), H).serve_forever()
