#!/usr/bin/env python3
"""Servidor local da Central: serve web/ e responde /api/* com a mesma lógica da API (rotas.py), só em localhost.

    python3 central/dev_server.py              → Central com SSO (lê central/api/local.settings.json, fora do repositório)
    python3 central/dev_server.py --prm        → PRM Save em modo local, com dados FICTÍCIOS e login simulado
                                                 http://localhost:4280/prm.html
    python3 central/dev_server.py --prm --dados ~/agentes-partners/registro/prm   → PRM sobre o registro/prm/ real
                                                 (gerado pelo prm_local.py), sem fixtures

No modo --prm não lê local.settings.json nem config.js (o login é o seletor de usuário de teste, que só existe aqui:
PRM_LOGIN_SIMULADO=1 + Host de teste + fora da Azure; no GitHub Codespaces,
CODESPACES=true libera o host exato do próprio codespace e o servidor ouve em 0.0.0.0). Estado da demo em <repositório>/registro/prm-demo/ (fora do git),
refeito a cada início (use --manter para continuar de onde parou). Aplica os cabeçalhos do staticwebapp.config.json.
"""
import argparse, http.server, json, os, sys
from urllib.parse import parse_qs

AQUI = os.path.dirname(os.path.abspath(__file__)); WEB = os.path.join(AQUI, "web"); REPO = os.path.dirname(AQUI)
ap = argparse.ArgumentParser()
ap.add_argument("--prm", action="store_true", help="PRM em modo local (login simulado)")
ap.add_argument("--dados", help="pasta registro/prm real (sem fixtures)")
ap.add_argument("--estado", help="pasta de estado da demo (padrão: <repositório>/registro/prm-demo)")
ap.add_argument("--manter", action="store_true", help="não recarrega as fixtures (continua a demo)")
ap.add_argument("--externa", action="store_true", help="permite a consulta de CNPJ às APIs públicas (sai da máquina)")
ap.add_argument("--porta", type=int, default=4280)
A = ap.parse_args()
PRM = A.prm or bool(A.dados)

if PRM:
    estado = os.path.abspath(os.path.expanduser(A.estado or os.path.join(REPO, "registro", "prm-demo")))
    os.environ["PRM_LOGIN_SIMULADO"] = "1"
    os.environ.setdefault("CENTRAL_API_EXTERNA", "1" if A.externa else "0")
    os.environ.setdefault("CENTRAL_APROVACAO", "obrigatoria")
    if A.dados:
        os.environ["PRM_DADOS"] = os.path.abspath(os.path.expanduser(A.dados))  # sal e índice reais (CENTRAL_ESTEIRA do ambiente)
    else:
        os.environ["PRM_DADOS"] = os.path.join(estado, "prm")
        os.environ["CENTRAL_ESTEIRA"] = os.path.join(estado, "esteira")
        os.environ["CENTRAL_SAL"] = "sal-da-demonstracao-local-sem-dado-real-0001"  # fictício: as fixtures não têm cliente
        os.environ["CENTRAL_RECEITA"] = os.path.join(estado, "receita")
else:
    cfg = os.path.join(AQUI, "api", "local.settings.json")
    if not os.path.exists(cfg): sys.exit("Crie central/api/local.settings.json a partir do local.settings.example.json (ou use --prm).")
    os.environ.update({k: v for k, v in json.load(open(cfg))["Values"].items() if v})

sys.path.insert(0, os.path.join(AQUI, "api"))
from central_api import rotas  # noqa: E402

PORTA = A.porta
os.environ["PRM_PORTA"] = str(PORTA)
HOSTS = {"localhost:%d" % PORTA, "127.0.0.1:%d" % PORTA, "[::1]:%d" % PORTA}
# GitHub Codespaces: ouve em 0.0.0.0 (o encaminhamento de porta chega de fora do contêiner) e aceita só o host exato do
# próprio codespace (CODESPACE_NAME + porta + domínio de encaminhamento). A porta fica privada no devcontainer.json.
from central_api.prm.identidade import host_codespaces  # noqa: E402
CODESPACE = host_codespaces(PORTA)
if CODESPACE:
    HOSTS |= {CODESPACE, CODESPACE + ":443"}
ESCUTA = "0.0.0.0" if CODESPACE else "localhost"
CAB = json.load(open(os.path.join(WEB, "staticwebapp.config.json")))["globalHeaders"]
CAB = {k: v for k, v in CAB.items() if k != "Strict-Transport-Security"}  # localhost é http
CAB["Content-Security-Policy"] = CAB["Content-Security-Policy"].replace("; upgrade-insecure-requests", "")  # idem
if PRM:
    CAB["Content-Security-Policy"] = CAB["Content-Security-Policy"].replace("connect-src 'self' https://login.microsoftonline.com", "connect-src 'self'")
ROTAS = {"/api/eu": rotas.eu, "/api/painel": rotas.painel}

if PRM:
    from central_api.prm import app as PA, rotas as PR  # noqa: E402
    app = PA.criar_de_ambiente()
    if not A.dados:
        from central_api.prm import fixtures  # noqa: E402
        if A.manter and os.path.exists(os.path.join(os.environ["PRM_DADOS"], "prm_parceiro.json")):
            fixtures.ligar_fontes(); fx = fixtures.ler()
            from central_api.prm import demandas as DM  # noqa: E402
            app.avaliador_historico = DM.avaliador_fixture(fx["historico"]); app.usuarios_teste = set(fx["usuarios_login_simulado"])
            fixtures.montar_indice(fx, os.environ["CENTRAL_ESTEIRA"])
        else:
            print("fixtures:", fixtures.carregar(app, os.environ["CENTRAL_ESTEIRA"]))
        PR._APP["fixtures"] = True
    else:
        from central_api.prm import demandas as DM  # noqa: E402
        app.avaliador_historico = DM.avaliador_lib()
    PR.definir_app(app)


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=WEB, **k)

    def end_headers(self):
        for k, v in CAB.items(): self.send_header(k, v)
        super().end_headers()

    def _host_ok(self):
        if (self.headers.get("Host") or "").lower() in HOSTS:
            return True
        self._json(421, {"erro": "host não permitido"}); return False  # DNS rebinding

    def _cab(self):
        c = {k: v for k, v in self.headers.items() if k.lower() != "x-prm-ip-local"}
        c["X-PRM-IP-Local"] = self.client_address[0]
        return c

    def _json(self, st, corpo):
        if isinstance(corpo, dict) and corpo.get("_arquivo"):
            with open(corpo["_arquivo"], "rb") as f: b = f.read()
            self.send_response(st); self.send_header("Content-Type", corpo["_tipo"]); self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Disposition", 'attachment; filename="%s"' % corpo["_nome"])
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b); return
        b = json.dumps(corpo, ensure_ascii=False).encode()
        self.send_response(st); self.send_header("Content-Type", "application/json"); self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def _api(self, metodo, corpo=None):
        rota, _, q = self.path.partition("?")
        consulta = {k: v[0] for k, v in parse_qs(q).items()}
        cab = self._cab()
        try:
            if rota.startswith("/api/prm/"):
                return self._json(*rotas.prm(metodo, rota, cab, corpo, consulta))
            if rota == "/api/regime" and metodo == "POST":
                return self._json(*rotas.regime_lote(cab, corpo))
            if rota == "/api/esteira":
                return self._json(*(rotas.esteira_pedir(cab, corpo) if metodo == "POST" else rotas.esteira_andamento(cab, consulta.get("id", ""))))
            if rota == "/api/esteira/historico":
                return self._json(*rotas.esteira_historico(cab))
            if rota == "/api/esteira/arquivo":
                return self._json(*rotas.esteira_arquivo(cab, consulta.get("id", "")))
            fn = ROTAS.get(rota) if metodo == "GET" else None
            if not fn:
                return self._json(404, {"erro": "rota não encontrada"})
            return self._json(*fn(cab))
        except RuntimeError:
            return self._json(503, {"erro": "SSO não configurado neste servidor local (use o login de teste do PRM)."})
        except Exception as e:  # noqa: BLE001
            sys.stderr.write("erro interno em %s: %s\n" % (rota, type(e).__name__))
            return self._json(500, {"erro": "Não conseguimos carregar esta parte agora. Tente de novo em instantes."})

    def do_GET(self):
        if not self._host_ok(): return
        rota = self.path.split("?")[0]
        if rota.startswith("/api/"):
            return self._api("GET")
        if PRM and rota in ("/", "/index.html"):
            self.send_response(302); self.send_header("Location", "/prm.html"); self.end_headers(); return
        if PRM and rota == "/config.js":  # no modo local não há SSO: nunca serve o config.js real
            b = b"window.CENTRAL_CONFIG = null;\n"
            self.send_response(200); self.send_header("Content-Type", "text/javascript"); self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b); return
        return super().do_GET()

    def do_POST(self):
        if not self._host_ok(): return
        if not self.path.startswith("/api/"):
            return self._json(404, {"erro": "rota não encontrada"})
        if (self.headers.get("Content-Type") or "").split(";")[0].strip().lower() != "application/json":
            return self._json(415, {"erro": "use application/json"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            if not 0 <= n <= 20000:
                return self._json(413, {"erro": "corpo inválido"})
            corpo = json.loads(self.rfile.read(n) or b"{}")
            if not isinstance(corpo, dict):
                raise ValueError
        except ValueError:
            return self._json(400, {"erro": "corpo inválido"})
        return self._api("POST", corpo)

    def log_message(self, fmt, *a): sys.stderr.write("%s %s\n" % (self.command, self.path.split("?")[0]))  # sem query (sem CNPJ) no log


if __name__ == "__main__":
    print(("PRM local em http://localhost:%d/prm.html" if PRM else "Central local em http://localhost:%d/") % PORTA, "(Ctrl+C para parar)")
    if CODESPACE:
        print("Codespaces: https://%s/%s" % (CODESPACE, "prm.html" if PRM else ""))
    http.server.ThreadingHTTPServer((ESCUTA, PORTA), H).serve_forever()
