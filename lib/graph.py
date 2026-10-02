#!/usr/bin/env python3
"""Adaptador Microsoft Graph (e-mail e SharePoint) para os agentes rodarem sem o Mac do Luis.

Fica DESLIGADO até o TI entregar o registro do aplicativo (ver docs/NUVEM.md). Liga por variáveis de ambiente:
  AGENTES_EMAIL=graph           → email_layout.outlook() e central.py passam a usar o Graph em vez do Outlook do Mac
  AGENTES_ARQUIVOS=sharepoint   → publicar_onedrive.py e o registro de demandas sobem os arquivos para o SharePoint
Credenciais (segredos, nunca no código): GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET
Destinos: AGENTES_CAIXA (caixa compartilhada), GRAPH_SITE_ID (site do SharePoint), GRAPH_PASTA (pasta raiz no site)

Acesso mínimo pedido ao TI: Mail.ReadWrite e Mail.Send restritos à caixa AGENTES_CAIXA (Application Access Policy)
e Sites.Selected só no site da área. Usa curl (o mesmo cliente HTTP dos outros scripts).
Teste: python3 lib/graph.py testar
"""
import base64, json, os, subprocess, sys, time
from urllib.parse import quote

G = "https://graph.microsoft.com/v1.0"
_cache = {}


def ligado(tipo):
    return {"email": os.environ.get("AGENTES_EMAIL") == "graph", "arquivos": os.environ.get("AGENTES_ARQUIVOS") == "sharepoint"}[tipo]


def _curl(args, entrada=None):
    r = subprocess.run(["curl", "-sS", "-m", "120"] + args, input=entrada, capture_output=True)
    return r.stdout


def token():
    if _cache.get("exp", 0) > time.time() + 60: return _cache["tk"]
    t, c, s = (os.environ.get(k) for k in ("GRAPH_TENANT_ID", "GRAPH_CLIENT_ID", "GRAPH_CLIENT_SECRET"))
    if not (t and c and s): sys.exit("Graph sem credenciais: defina GRAPH_TENANT_ID, GRAPH_CLIENT_ID e GRAPH_CLIENT_SECRET.")
    corpo = f"client_id={quote(c)}&client_secret={quote(s)}&scope={quote('https://graph.microsoft.com/.default')}&grant_type=client_credentials"
    d = json.loads(_curl(["-X", "POST", f"https://login.microsoftonline.com/{t}/oauth2/v2.0/token",
                          "-H", "Content-Type: application/x-www-form-urlencoded", "--data-binary", "@-"], corpo.encode()) or b"{}")
    if "access_token" not in d: sys.exit("Graph recusou o login: " + str(d.get("error_description", d))[:200])
    _cache.update(tk=d["access_token"], exp=time.time() + int(d.get("expires_in", 3000)))
    return _cache["tk"]


def api(metodo, caminho, corpo=None, binario=None, cabecalhos=()):
    cfg = f'header = "Authorization: Bearer {token()}"\n' + "".join(f'header = "{h}"\n' for h in cabecalhos)
    args = ["-X", metodo, (caminho if caminho.startswith("http") else G + caminho), "-K", "-"]
    if corpo is not None:
        cfg += 'header = "Content-Type: application/json"\n'
        tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), f"graph-{os.getpid()}.json"); open(tmp, "w").write(json.dumps(corpo))
        args += ["--data-binary", "@" + tmp]
    if binario is not None:
        cfg += 'header = "Content-Type: application/octet-stream"\n'; args += ["--data-binary", "@" + binario]
    out = _curl(args, cfg.encode())
    try: return json.loads(out) if out else {}
    except json.JSONDecodeError: return {"_bytes": out}


# ---------- E-mail (caixa compartilhada) ----------
def enviar(para, cc, assunto, html, anexos=(), rascunho=False):
    import protecao  # trava de domínio: só @savecompany.com.br
    fora = protecao.interno(list(para), list(cc))
    if fora or not para: return False, f"BLOQUEADO: destinatário fora do domínio ou vazio {fora}"
    caixa = os.environ["AGENTES_CAIXA"]
    msg = {"subject": assunto, "body": {"contentType": "HTML", "content": html},
           "toRecipients": [{"emailAddress": {"address": a}} for a in para], "ccRecipients": [{"emailAddress": {"address": a}} for a in cc],
           "attachments": [{"@odata.type": "#microsoft.graph.fileAttachment", "name": os.path.basename(f),
                            "contentBytes": base64.b64encode(open(f, "rb").read()).decode()} for f in anexos if os.path.getsize(f) < 3_000_000]}
    r = (api("POST", f"/users/{quote(caixa)}/messages", msg) if rascunho
         else api("POST", f"/users/{quote(caixa)}/sendMail", {"message": msg, "saveToSentItems": True}))
    return (not r.get("error")), json.dumps(r.get("error", ""))[:300]


def listar(dias=3, contem="[AGENTES]"):
    caixa = os.environ["AGENTES_CAIXA"]
    desde = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - dias * 86400))
    url = f"/users/{quote(caixa)}/mailFolders/inbox/messages?$filter=receivedDateTime ge {desde}&$select=id,subject,from,receivedDateTime&$top=100"
    out = []
    while url:
        r = api("GET", url.replace(" ", "%20")); url = r.get("@odata.nextLink")
        for m in r.get("value", []):
            if contem in (m.get("subject") or ""):
                out.append({"id": m["id"], "assunto": m["subject"], "de": ((m.get("from") or {}).get("emailAddress") or {}).get("address", "").lower(),
                            "quando": m["receivedDateTime"][:19]})
    return out


def baixar_mensagem(mid, pasta):
    caixa = os.environ["AGENTES_CAIXA"]; os.makedirs(pasta, exist_ok=True)
    m = api("GET", f"/users/{quote(caixa)}/messages/{mid}?$select=body", cabecalhos=('Prefer: outlook.body-content-type="text"',))
    texto = (m.get("body") or {}).get("content", ""); open(os.path.join(pasta, "texto.txt"), "w").write(texto)
    anexos = []
    for a in api("GET", f"/users/{quote(caixa)}/messages/{mid}/attachments").get("value", []):
        if a.get("contentBytes"):
            f = os.path.join(pasta, os.path.basename(a["name"])); open(f, "wb").write(base64.b64decode(a["contentBytes"])); anexos.append(f)
    return texto, anexos


# ---------- SharePoint (site da área) ----------
def _item(caminho):
    base = os.environ.get("GRAPH_PASTA", "Área Partners · Agentes").strip("/")
    return f"/sites/{os.environ['GRAPH_SITE_ID']}/drive/root:/{quote(base + '/' + caminho.strip('/'))}"


def subir(local, remoto):
    tam = os.path.getsize(local)
    if tam < 4_000_000:
        r = api("PUT", _item(remoto) + ":/content", binario=local); return "id" in r
    s = api("POST", _item(remoto) + ":/createUploadSession", {"item": {"@microsoft.graph.conflictBehavior": "replace"}})
    url, pos, parte = s.get("uploadUrl"), 0, 10 * 1024 * 1024
    if not url: return False
    with open(local, "rb") as f:
        while pos < tam:
            bloco = f.read(parte); tmp = local + ".parte"; open(tmp, "wb").write(bloco)
            r = subprocess.run(["curl", "-sS", "-m", "300", "-X", "PUT", url, "-H", f"Content-Range: bytes {pos}-{pos + len(bloco) - 1}/{tam}",
                                "--data-binary", "@" + tmp], capture_output=True); os.remove(tmp); pos += len(bloco)
    return r.returncode == 0


def baixar(remoto, local):
    r = api("GET", _item(remoto) + ":/content")
    if "_bytes" in r:
        os.makedirs(os.path.dirname(local) or ".", exist_ok=True); open(local, "wb").write(r["_bytes"]); return True
    return False


def subir_pasta(local_raiz, remoto_raiz, manifesto=None):
    """Sobe só o que mudou desde a última vez (manifesto de data de modificação)."""
    man = json.load(open(manifesto)) if manifesto and os.path.exists(manifesto) else {}
    n = 0
    for raiz, _, arqs in os.walk(local_raiz):
        for a in arqs:
            f = os.path.join(raiz, a); rel = os.path.relpath(f, local_raiz)
            if man.get(rel) == os.path.getmtime(f): continue
            if subir(f, remoto_raiz.rstrip("/") + "/" + rel): man[rel] = os.path.getmtime(f); n += 1
    if manifesto: json.dump(man, open(manifesto, "w"))
    return n


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "ajuda"
    if cmd == "testar":
        token(); print("login ok")
        if os.environ.get("AGENTES_CAIXA"): print("caixa ok:", len(listar(1)), "e-mails [AGENTES] nas últimas 24h")
        if os.environ.get("GRAPH_SITE_ID"): print("site ok:", "id" in api("GET", f"/sites/{os.environ['GRAPH_SITE_ID']}"))
    elif cmd == "subir-pasta":
        print(subir_pasta(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None), "arquivos enviados")
    else:
        print(__doc__)
