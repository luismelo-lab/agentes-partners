#!/usr/bin/env python3
"""Adaptador do GLPI 11 da Save (https://tributario.savecompany.com.br) pela API v2 (High-Level REST API).

Verificado em 01/10/2026 sem login: API v2.1 ativa, autenticação OAuth2 (fluxos "password" e "authorizationCode"),
endpoints /Assistance/Ticket (criar/listar), /Assistance/Ticket/{id}/Timeline/Followup e /TeamMember.
A API antiga (apirest.php) está desativada e não é usada.

Quem abre o chamado (sem usuário novo):
  Opção A: a própria pessoa que atendeu o parceiro (Daniela, Geovana, Jenifer). Cada uma autoriza UMA vez:
           python3 lib/glpi.py autorizar daniela   → abre o login do GLPI; ela entra e clica em Autorizar.
  Opção B: a conta reserva (Luis, "conta_reserva" no config), com a pessoa como requerente.
  Nenhuma senha passa pelos agentes; ficam só as chaves de acesso em ~/agentes-partners/.glpi/ (revogáveis no GLPI).
Pré-requisito único do administrador: um cliente OAuth (GLPI_CLIENT_ID e GLPI_CLIENT_SECRET no .env), fluxo
"authorization code", redirect http://127.0.0.1:8765/glpi, escopos "api" e "user". Conta de serviço é opcional.
Modo (infra/glpi-config.json → "modo"): "rascunho" (padrão: só monta o chamado e mostra no e-mail) ou "abrir".
Teste: python3 lib/glpi.py testar
"""
import http.server, json, os, secrets, subprocess, sys, threading, time
from urllib.parse import parse_qs, quote, urlparse

AP = os.path.expanduser("~/agentes-partners")
CFG = os.path.join(AP, "infra", "glpi-config.json")
_tk = {}


def config():
    return json.load(open(CFG))


def _env(k):
    v = os.environ.get(k)
    if v: return v
    f = os.path.join(AP, ".env")
    if os.path.exists(f):
        for l in open(f):
            if l.startswith(k + "="): return l.split("=", 1)[1].strip()
    return None


def _curl(args, entrada=None):
    return subprocess.run(["curl", "-sS", "-m", "60"] + args, input=entrada, capture_output=True).stdout


CONTAS = os.path.join(AP, ".glpi")  # chaves de acesso por pessoa (pasta 700, arquivos 600; fora do git e do backup)
REDIRECT = "http://127.0.0.1:8765/glpi"


def _salvar_conta(conta, d):
    os.makedirs(CONTAS, exist_ok=True); os.chmod(CONTAS, 0o700)
    f = os.path.join(CONTAS, conta + ".json"); json.dump(d, open(f, "w")); os.chmod(f, 0o600)


def _trocar(campos):
    base = config()["url"].rstrip("/")
    corpo = "&".join(f"{k}={quote(str(v))}" for k, v in campos.items())
    return json.loads(_curl(["-X", "POST", base + "/api.php/token", "-H", "Content-Type: application/x-www-form-urlencoded", "--data-binary", "@-"], corpo.encode()) or b"{}")


def autorizar(conta):
    """Uma vez por pessoa, no Mac onde os agentes rodam: abre o login do GLPI no navegador; a pessoa entra com o
    próprio usuário e autoriza. Nenhuma senha passa pelos agentes; fica guardada só a chave de acesso (revogável no GLPI)."""
    cid, sec = _env("GLPI_CLIENT_ID"), _env("GLPI_CLIENT_SECRET")
    if not cid: raise SystemExit("Falta o cliente OAuth do GLPI (GLPI_CLIENT_ID/GLPI_CLIENT_SECRET no .env): ver docs/GLPI.md.")
    estado, achado = secrets.token_urlsafe(16), {}
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = parse_qs(urlparse(self.path).query)
            if q.get("state", [""])[0] == estado and q.get("code"): achado["code"] = q["code"][0]
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write("<h2>Pronto. Pode fechar esta janela.</h2>".encode() if achado else "<h2>Autorização não concluída.</h2>".encode())
        def log_message(self, *a): pass
    srv = http.server.HTTPServer(("127.0.0.1", 8765), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = (config()["url"].rstrip("/") + f"/api.php/authorize?response_type=code&client_id={quote(cid)}&redirect_uri={quote(REDIRECT)}"
           f"&scope={quote('api user')}&state={estado}")
    subprocess.run(["open", url]); print("Abrindo o GLPI no navegador para", conta, "entrar e autorizar…")
    for _ in range(300):
        if achado: break
        time.sleep(1)
    srv.shutdown()
    if not achado: raise SystemExit("Tempo esgotado sem autorização.")
    d = _trocar({"grant_type": "authorization_code", "code": achado["code"], "redirect_uri": REDIRECT, "client_id": cid, "client_secret": sec})
    if "access_token" not in d: raise SystemExit("GLPI recusou: " + str(d.get("error_description") or d)[:200])
    d["exp"] = time.time() + int(d.get("expires_in", 3600)); _salvar_conta(conta, d)
    me = api("GET", "/Administration/User/Me", conta=conta)
    d["user_id"], d["username"] = me.get("id"), me.get("username"); _salvar_conta(conta, d)
    print(f"Autorizado: {conta} = usuário GLPI {d['username']} (id {d['user_id']})")


def tem_conta(conta):
    return bool(conta) and os.path.exists(os.path.join(CONTAS, conta + ".json"))


def token_conta(conta):
    f = os.path.join(CONTAS, conta + ".json"); d = json.load(open(f))
    if d.get("exp", 0) > time.time() + 60: return d["access_token"]
    n = _trocar({"grant_type": "refresh_token", "refresh_token": d.get("refresh_token", ""), "client_id": _env("GLPI_CLIENT_ID"), "client_secret": _env("GLPI_CLIENT_SECRET")})
    if "access_token" not in n: raise SystemExit(f"A autorização de {conta} no GLPI expirou: rode `python3 lib/glpi.py autorizar {conta}`.")
    d.update(n); d["exp"] = time.time() + int(n.get("expires_in", 3600)); _salvar_conta(conta, d)
    return d["access_token"]


def token():
    if _tk.get("exp", 0) > time.time() + 60: return _tk["v"]
    base = config()["url"].rstrip("/")
    campos = {"grant_type": "password", "client_id": _env("GLPI_CLIENT_ID"), "client_secret": _env("GLPI_CLIENT_SECRET"),
              "username": _env("GLPI_USUARIO"), "password": _env("GLPI_SENHA"), "scope": "api"}
    if not all(campos.values()): raise SystemExit("GLPI sem credenciais: peça ao administrador o cliente OAuth e a conta de serviço (ver docs/GLPI.md).")
    corpo = "&".join(f"{k}={quote(v)}" for k, v in campos.items())
    d = json.loads(_curl(["-X", "POST", base + "/api.php/token", "-H", "Content-Type: application/x-www-form-urlencoded", "--data-binary", "@-"], corpo.encode()) or b"{}")
    if "access_token" not in d: raise SystemExit("GLPI recusou o login: " + str(d.get("error_description") or d.get("title") or d)[:200])
    _tk.update(v=d["access_token"], exp=time.time() + int(d.get("expires_in", 3000)))
    return _tk["v"]


def api(metodo, caminho, corpo=None, conta=None):
    base = config()["url"].rstrip("/") + "/api.php/v2"
    tk = token_conta(conta) if conta else token()
    cfg = f'header = "Authorization: Bearer {tk}"\nheader = "Content-Type: application/json"\nheader = "Accept: application/json"\n'
    args = ["-X", metodo, base + caminho, "-K", "-"]
    if corpo is not None:
        tmp = os.path.join(AP, "logs", f".glpi-{os.getpid()}.json"); open(tmp, "w").write(json.dumps(corpo)); args += ["--data-binary", "@" + tmp]
    try: out = _curl(args, cfg.encode())
    finally:
        if corpo is not None and os.path.exists(tmp): os.unlink(tmp)  # o texto do chamado não fica em logs/ nem vai para o backup
    try: return json.loads(out) if out else {}
    except json.JSONDecodeError: return {"erro": out[:200].decode(errors="ignore")}


def montar(area, titulo, descricao_html, urgencia=3):
    """Chamado no formato da API, a partir da área (juridico, tecnico, contratos, pos_venda, marketing, financeiro, ti)."""
    a = config()["areas"].get(area) or config()["areas"]["outros"]
    t = {"name": titulo[:250], "content": descricao_html, "type": 2, "urgency": int(urgencia)}
    if a.get("categoria_id"): t["category"] = {"id": a["categoria_id"]}
    if config().get("entidade_id"): t["entity"] = {"id": config()["entidade_id"]}
    return t, a


def conta_para(pessoa):
    """Opção A: a própria pessoa (se ela autorizou). Opção B: a conta reserva (Luis) com a pessoa como requerente."""
    if tem_conta(pessoa): return pessoa, None
    r = config().get("conta_reserva", "luis")
    if tem_conta(r):
        uid = (config().get("usuarios") or {}).get(pessoa)
        if isinstance(uid, str) and "@" in uid:  # e-mail → id do usuário no GLPI (consulta uma vez e guarda)
            achados = api("GET", "/Administration/User?filter=" + quote(f'emails.email=="{uid}"'), conta=r)
            uid = achados[0]["id"] if isinstance(achados, list) and achados else None
            if uid:
                c = config(); c["usuarios"][pessoa] = uid; json.dump(c, open(CFG, "w"), ensure_ascii=False, indent=1)
        return r, uid
    return None, None


def abrir(area, titulo, descricao_html, urgencia=3, pessoa=None):
    """Abre o chamado em nome de quem atendeu (pessoa) e atribui ao grupo da área. Devolve {"id", "url"} ou {"rascunho": True}."""
    t, a = montar(area, titulo, descricao_html, urgencia)
    conta, requerente = conta_para(pessoa) if pessoa else (None, None)
    if config().get("modo") != "abrir" or not (conta or _env("GLPI_USUARIO")):
        return {"rascunho": True, "chamado": t, "grupo": a.get("nome")}
    r = api("POST", "/Assistance/Ticket", t, conta=conta)
    tid = r.get("id")
    if not tid: return {"erro": str(r)[:300]}
    if a.get("grupo_id"): api("POST", f"/Assistance/Ticket/{tid}/TeamMember", {"type": "Group", "id": a["grupo_id"], "role": "assigned"}, conta=conta)
    if requerente: api("POST", f"/Assistance/Ticket/{tid}/TeamMember", {"type": "User", "id": requerente, "role": "requester"}, conta=conta)
    return {"id": tid, "url": config()["url"].rstrip("/") + f"/front/ticket.form.php?id={tid}", "grupo": a.get("nome"), "aberto_por": conta}


def acompanhar(tid, texto_html, pessoa=None):
    if config().get("modo") != "abrir": return {"rascunho": True}
    conta, _ = conta_para(pessoa) if pessoa else (None, None)
    return api("POST", f"/Assistance/Ticket/{tid}/Timeline/Followup", {"content": texto_html}, conta=conta)


def status(tid):
    r = api("GET", f"/Assistance/Ticket/{tid}")
    return {"id": tid, "status": r.get("status"), "atualizado": r.get("date_mod")}


def categorias(conta=None):
    """Mapeia nome → ID das categorias a partir dos chamados existentes (a API v2 não lista categorias à parte)."""
    vistos = {}
    for pag in range(0, 2000, 200):
        lote = api("GET", f"/Assistance/Ticket?start={pag}&limit=200", conta=conta)
        if not isinstance(lote, list) or not lote: break
        for t in lote:
            c = t.get("category") or {}
            if c.get("id"): vistos[c.get("name")] = c["id"]
    cfg = config(); n = 0
    for k, a in cfg["areas"].items():
        folha = a["nome"].split(">")[-1].strip()
        cid = vistos.get(a["nome"]) or vistos.get(folha)
        if cid and not a.get("categoria_id"): a["categoria_id"] = cid; n += 1
    json.dump(cfg, open(CFG, "w"), ensure_ascii=False, indent=1)
    print(f"{len(vistos)} categorias vistas nos chamados; {n} áreas preenchidas")


if __name__ == "__main__":
    cmd = (sys.argv[1:] or [""])[0]
    if cmd == "autorizar":
        autorizar(sys.argv[2])
    elif cmd == "testar":
        conta = sys.argv[2] if len(sys.argv) > 2 else None
        me = api("GET", "/Administration/User/Me", conta=conta); print("login ok:", me.get("username"))
        print("chamados visíveis:", len(api("GET", "/Assistance/Ticket?limit=5", conta=conta) or []))
    elif cmd == "categorias":
        categorias(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "contas":
        for f in sorted(os.listdir(CONTAS)) if os.path.isdir(CONTAS) else []:
            d = json.load(open(os.path.join(CONTAS, f))); print(f[:-5], "→", d.get("username"), "(id", str(d.get("user_id")) + ")")
    else:
        print(__doc__)
