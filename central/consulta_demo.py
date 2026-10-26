#!/usr/bin/env python3
"""Demo local da consulta de Lucro Real para parceiros. SEM login: só para testar tela e texto.

    python3 central/consulta_demo.py        → http://localhost:4281/consulta.html

Consulta o Minha Receita e, se ele falhar, a BrasilAPI (APIs gratuitas; o CNPJ digitado sai para elas; CENTRAL_API_EXTERNA=0 desliga). Sem base local. No piloto, as mesmas funções de
central_api/regime.py entram em rotas.py atrás do token do Entra (papel e teto de consultas por parceiro).
Só escuta em localhost.
"""
import http.server, json, math, os, sys
from urllib.parse import parse_qs

AQUI = os.path.dirname(os.path.abspath(__file__)); WEB = os.path.join(AQUI, "web")
sys.path.insert(0, os.path.join(AQUI, "api"))
from central_api import esteira, regime  # noqa: E402

PORTA = 4281
HOSTS = {"localhost:%d" % PORTA, "127.0.0.1:%d" % PORTA, "[::1]:%d" % PORTA}  # recusa Host de outro nome (DNS rebinding)
with open(os.path.join(WEB, "staticwebapp.config.json"), encoding="utf-8") as _f:
    CAB = json.load(_f)["globalHeaders"]
CAB = {k: v for k, v in CAB.items() if k != "Strict-Transport-Security"}
CAB["Content-Security-Policy"] = CAB["Content-Security-Policy"].replace("; upgrade-insecure-requests", "")  # localhost é http
CAB["Content-Security-Policy"] = CAB["Content-Security-Policy"].replace("connect-src 'self' https://login.microsoftonline.com", "connect-src 'self'")
USUARIO = "demo-local"
os.environ.setdefault("CENTRAL_APROVACAO", "autonoma")  # demo: entrega na hora (o auditor continua barrando promessa); a nuvem começa em "obrigatoria"


def numero(v):
    """Faturamento digitado ('90.000.000,50') ou enviado como número. None se vazio, inválido, negativo ou não finito."""
    if isinstance(v, bool) or v in (None, ""):
        return None
    try:
        n = float(v) if isinstance(v, (int, float)) else float(str(v).strip().replace(".", "").replace(",", "."))
    except ValueError:
        return None
    return n if math.isfinite(n) and n >= 0 else None


def lote(corpo):
    bruto = corpo.get("cnpjs")
    if not isinstance(bruto, list):
        return 400, {"erro": "Informe ao menos um CNPJ."}
    cnpjs = []
    for c in bruto:  # só texto; repetidos (inclusive com outra pontuação) contam e consultam uma vez
        c = esteira._cnpj(c) if isinstance(c, str) else ""
        if c and c not in cnpjs:
            cnpjs.append(c)
        if len(cnpjs) > regime.LIMITE_LOTE:
            break
    if not cnpjs:
        return 400, {"erro": "Informe ao menos um CNPJ."}
    if len(cnpjs) > regime.LIMITE_LOTE:
        return 400, {"erro": "No máximo %d CNPJs por consulta." % regime.LIMITE_LOTE}
    fat = numero(corpo.get("faturamento")) if len(cnpjs) == 1 else None
    guardadas = {} if fat else {c: esteira.consulta_guardada(USUARIO, c) for c in cnpjs}  # já consultada há pouco: sem nova chamada nem desconto no teto
    novas = [c for c in cnpjs if not guardadas.get(c)]
    ok, usadas, limite = regime.registrar_uso(USUARIO, len(novas))
    if not ok:
        regime.auditar(USUARIO, [regime.neutra(c, "teto_diario") for c in novas])
        return 429, {"erro": regime.MSG_NEUTRA}
    vivas = iter(regime.consultar_lote(novas, fat))
    res = [guardadas.get(c) or next(vivas) for c in cnpjs]
    regime.auditar(USUARIO, [r for c, r in zip(cnpjs, res) if c in novas])  # inclui os acertos de negócio ativo
    for c, r in zip(cnpjs, res):
        if c in novas:  # guardada não é regravada: senão o prazo de 7 dias nunca vence
            esteira.registrar_consulta(USUARIO, r)
    return 200, {"resultados": [regime.publico(r) for r in regime.limitar_ativos(USUARIO, res)], "usadas": usadas, "limite": limite}


def pedir_esteira(corpo):
    cnpj = corpo.get("cnpj")
    if not isinstance(cnpj, str):
        return 400, {"erro": "Informe o CNPJ."}
    r = esteira.consulta_guardada(USUARIO, cnpj)  # a consulta vem do servidor, nunca do navegador
    if not r:
        ok, usadas, limite = regime.registrar_uso(USUARIO, 1)  # consulta nova às APIs conta no teto diário e na trilha, como no lote
        if not ok:
            regime.auditar(USUARIO, [regime.neutra(str(cnpj), "teto_diario")])
            return 429, {"erro": regime.MSG_NEUTRA}
        r = regime.consultar(cnpj)
        regime.auditar(USUARIO, [r])
        esteira.registrar_consulta(USUARIO, r)
    r = regime.limitar_ativos(USUARIO, [r])[0]
    if r["faixa"] in ("negocio_ativo", "invalido", "indisponivel") or not r.get("empresa"):
        return 400, {"erro": r["titulo"]}
    try:
        p = esteira.solicitar(r["cnpj"], USUARIO, r)
    except esteira.Recusa as e:
        return 400, {"erro": str(e)}
    return 200, esteira.visao_parceiro(p)


def andamento(consulta):
    v = esteira.ler_do_parceiro((parse_qs(consulta).get("id") or [""])[0], USUARIO)
    return (200, v) if v else (404, {"erro": "pedido não encontrado"})


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=WEB, **k)

    def end_headers(self):
        for k, v in CAB.items(): self.send_header(k, v)
        super().end_headers()

    def _host_ok(self):
        if (self.headers.get("Host") or "").lower() in HOSTS:
            return True
        self._json(421, {"erro": "host não permitido"})
        return False

    def do_GET(self):
        if not self._host_ok():
            return
        rota, _, consulta = self.path.partition("?")
        try:
            if rota == "/api/esteira":
                return self._json(*andamento(consulta))
            if rota == "/api/esteira/historico":
                return self._json(200, {"empresas": esteira.historico(USUARIO)})
            if rota == "/api/esteira/arquivo":
                pid = (parse_qs(consulta).get("id") or [""])[0]
                arq = esteira.arquivo_do_parceiro(pid, USUARIO)
                if not arq:
                    return self._json(404, {"erro": "arquivo não encontrado"})
                with open(arq, "rb") as f:
                    b = f.read()
                self.send_response(200); self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                self.send_header("Content-Disposition", 'attachment; filename="dossie-%s.docx"' % pid)  # pid já validado (E-nnnn)
                self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b); return
        except Exception as e:  # noqa: BLE001  erro interno: resposta neutra, sem rastro nem dado de cliente
            sys.stderr.write("erro interno em %s: %s\n" % (rota, type(e).__name__))
            return self._json(500, {"erro": "erro interno"})
        return super().do_GET()

    def do_POST(self):
        if not self._host_ok():
            return
        rota = self.path.split("?")[0]
        if rota not in ("/api/regime", "/api/esteira"):
            return self._json(404, {"erro": "rota não encontrada"})
        if (self.headers.get("Content-Type") or "").split(";")[0].strip().lower() != "application/json":
            return self._json(415, {"erro": "use application/json"})  # exige preflight: página de outro site não consegue postar aqui
        try:
            n = int(self.headers.get("Content-Length", 0))
            if not 0 <= n <= 20000:
                return self._json(413 if n > 20000 else 400, {"erro": "corpo inválido"})
            corpo = json.loads(self.rfile.read(n) or b"{}")
            if not isinstance(corpo, dict):
                raise ValueError
        except ValueError:
            return self._json(400, {"erro": "corpo inválido"})
        try:
            self._json(*(pedir_esteira(corpo) if rota == "/api/esteira" else lote(corpo)))
        except Exception as e:  # noqa: BLE001
            sys.stderr.write("erro interno em %s: %s\n" % (rota, type(e).__name__))
            self._json(500, {"erro": "erro interno"})

    def _json(self, st, corpo):
        b = json.dumps(corpo, ensure_ascii=False).encode()
        self.send_response(st); self.send_header("Content-Type", "application/json"); self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def log_message(self, fmt, *a): sys.stderr.write("%s %s\n" % (self.command, self.path.split("?")[0]))  # sem CNPJ no log


if __name__ == "__main__":
    print("Demo da consulta em http://localhost:%d/consulta.html  (Ctrl+C para parar)" % PORTA)
    http.server.ThreadingHTTPServer(("localhost", PORTA), H).serve_forever()
