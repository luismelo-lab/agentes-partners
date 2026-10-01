#!/usr/bin/env python3
"""Adaptador do GLPI 11 da Save (https://tributario.savecompany.com.br) pela API v2 (High-Level REST API).

Verificado em 01/10/2026 sem login: API v2.1 ativa, autenticação OAuth2 (fluxos "password" e "authorizationCode"),
endpoints /Assistance/Ticket (criar/listar), /Assistance/Ticket/{id}/Timeline/Followup e /TeamMember.
A API antiga (apirest.php) está desativada e não é usada.

Credenciais em ~/agentes-partners/.env (nunca no código, nunca impressas):
  GLPI_CLIENT_ID, GLPI_CLIENT_SECRET  (cliente OAuth criado pelo administrador do GLPI, escopo "api")
  GLPI_USUARIO, GLPI_SENHA            (conta de serviço "Agentes Partners", perfil só para abrir e acompanhar chamados)
Modo (infra/glpi-config.json → "modo"): "rascunho" (padrão: só monta o chamado e mostra no e-mail) ou "abrir".
Teste: python3 lib/glpi.py testar
"""
import json, os, subprocess, sys, time
from urllib.parse import quote

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


def api(metodo, caminho, corpo=None):
    base = config()["url"].rstrip("/") + "/api.php/v2"
    cfg = f'header = "Authorization: Bearer {token()}"\nheader = "Content-Type: application/json"\nheader = "Accept: application/json"\n'
    args = ["-X", metodo, base + caminho, "-K", "-"]
    if corpo is not None:
        tmp = os.path.join(AP, "logs", f".glpi-{os.getpid()}.json"); open(tmp, "w").write(json.dumps(corpo)); args += ["--data-binary", "@" + tmp]
    out = _curl(args, cfg.encode())
    try: return json.loads(out) if out else {}
    except json.JSONDecodeError: return {"erro": out[:200].decode(errors="ignore")}


def montar(area, titulo, descricao_html, urgencia=3):
    """Chamado no formato da API, a partir da área (juridico, tecnico, contratos, pos_venda, marketing, financeiro, ti)."""
    a = config()["areas"].get(area) or config()["areas"]["outros"]
    t = {"name": titulo[:250], "content": descricao_html, "type": 2, "urgency": int(urgencia)}
    if a.get("categoria_id"): t["category"] = {"id": a["categoria_id"]}
    if config().get("entidade_id"): t["entity"] = {"id": config()["entidade_id"]}
    return t, a


def abrir(area, titulo, descricao_html, urgencia=3):
    """Abre o chamado (modo "abrir") e atribui ao grupo da área. Devolve {"id", "url"} ou {"rascunho": True}."""
    t, a = montar(area, titulo, descricao_html, urgencia)
    if config().get("modo") != "abrir": return {"rascunho": True, "chamado": t, "grupo": a.get("nome")}
    r = api("POST", "/Assistance/Ticket", t)
    tid = r.get("id")
    if not tid: return {"erro": str(r)[:300]}
    if a.get("grupo_id"): api("POST", f"/Assistance/Ticket/{tid}/TeamMember", {"type": "Group", "id": a["grupo_id"], "role": "assigned"})
    return {"id": tid, "url": config()["url"].rstrip("/") + f"/front/ticket.form.php?id={tid}", "grupo": a.get("nome")}


def acompanhar(tid, texto_html):
    if config().get("modo") != "abrir": return {"rascunho": True}
    return api("POST", f"/Assistance/Ticket/{tid}/Timeline/Followup", {"content": texto_html})


def status(tid):
    r = api("GET", f"/Assistance/Ticket/{tid}")
    return {"id": tid, "status": r.get("status"), "atualizado": r.get("date_mod")}


if __name__ == "__main__":
    if (sys.argv[1:] or [""])[0] == "testar":
        token(); print("login ok"); print("chamados visíveis:", len(api("GET", "/Assistance/Ticket?limit=5") or []))
    else:
        print(__doc__)
