#!/usr/bin/env python3
"""Conector direto da API de mensagens do Eazybe (WhatsApp) → caixa de entrada dos agentes.

Formato de entrada (resposta da API): {"<chatid>": [{"MessageId", "Message", "Chatid", "File", "FileName", "Ack",
"Datetime" (ms), "Date", "Direction" ("INCOMING"/"OUTGOING"), "SentById", "ChannelName", "ChannelId", "SentByNumber",
"sentByUserId", "CreatedByUser", "senderName"}]}. Chatid "...@c.us" = conversa individual; "...@g.us" = grupo.

Vantagem sobre a leitura pelo HubSpot (whatsapp_hubspot.py): chega na hora, a direção vem pronta (sem adivinhar quem é do
time pelo nome) e o arquivo vem com nome e link. A saída tem o mesmo formato da caixa atual (celulas/<pessoa>/whatsapp/caixa-*.json),
então triagem, demandas e painel continuam iguais.

COMO CHEGA (página Integrations do Eazybe, 16/10): o Eazybe NÃO tem API de consulta; ele ENVIA cada mensagem (recebida e
enviada) para um webhook. O receptor fica no ambiente Microsoft da Save (Power Automate ou Azure Function, docs/whatsapp-webhook.md)
e grava cada envio como um arquivo .json numa pasta do OneDrive/SharePoint; este script lê a pasta (modo "pasta", o padrão).
  EAZYBE_PASTA     pasta sincronizada onde o receptor grava os .json (padrão: Área Partners · Agentes/WhatsApp · Eazybe/entrada)
Modo API (só se a Eazybe um dia oferecer consulta):
  EAZYBE_API_URL   endereço da chamada de mensagens que a Eazybe forneceu (ex.: .../messages)
  EAZYBE_API_KEY   chave de acesso da API
  EAZYBE_AUTH      opcional: "Bearer" (padrão) ou o nome do cabeçalho que a Eazybe pede (ex.: "x-api-key")
Canais por pessoa: celulas/whatsapp-config.json → "eazybe_canais": {"daniela": ["<ChannelId ou número>"], ...}

Uso:
  python3 lib/eazybe.py testar                       verifica o acesso (não grava nada)
  python3 lib/eazybe.py caixa --pessoa daniela [--horas 24] [--aguardando 4] [--arquivo resposta.json]
"""
import argparse, glob, json, os, re, subprocess, sys, time
from datetime import datetime, timedelta, timezone

AP = os.path.expanduser("~/agentes-partners"); TZ = timezone(timedelta(hours=-3))
CFG = os.path.join(AP, "celulas", "whatsapp-config.json")
OK_FIM = re.compile(r"^\s*(ok|obrigad[oa]|valeu|show|perfeito|blz|beleza|👍|🙏|top|certo|combinado)[\s!.]*$", re.I)


def _env(k):
    v = os.environ.get(k)
    if v: return v
    f = os.path.join(AP, ".env")
    if os.path.exists(f):
        for l in open(f):
            if l.startswith(k + "="): return l.split("=", 1)[1].strip().strip('"')
    return None


def baixar(desde_ms=None):
    """Chama a API do Eazybe e devolve o dicionário {chatid: [mensagens]}."""
    url, chave = _env("EAZYBE_API_URL"), _env("EAZYBE_API_KEY")
    if not (url and chave): sys.exit("Eazybe sem acesso: defina EAZYBE_API_URL e EAZYBE_API_KEY no ~/agentes-partners/.env")
    auth = _env("EAZYBE_AUTH") or "Bearer"
    cab = f'header = "Authorization: Bearer {chave}"' if auth.lower() == "bearer" else f'header = "{auth}: {chave}"'
    if desde_ms: url += ("&" if "?" in url else "?") + f"from={desde_ms}"
    r = subprocess.run(["curl", "-sS", "-m", "90", "-K", "-", "-w", "\n%{http_code}", url], input=(cab + "\n").encode(), capture_output=True)
    txt, _, code = r.stdout.decode("utf-8", "replace").rpartition("\n")
    if not code.startswith("2"): sys.exit(f"Eazybe respondeu HTTP {code}: {txt[:200]}")
    d = json.loads(txt or "{}")
    return d.get("data", d) if isinstance(d, dict) else d


def ler_pasta(horas=24):
    """Junta os envios do webhook gravados na pasta (um .json por envio, no formato {chatid: [mensagens]})."""
    sys.path.insert(0, os.path.join(AP, "lib"))
    try:
        import caminhos; base = _env("EAZYBE_PASTA") or os.path.join(caminhos.area(), "WhatsApp · Eazybe", "entrada")
    except SystemExit: base = _env("EAZYBE_PASTA") or ""
    if not base or not os.path.isdir(base): sys.exit(f"Pasta do webhook do Eazybe não encontrada: {base or '(sem EAZYBE_PASTA)'}")
    lim = time.time() - max(horas, 24) * 3600; out = {}
    for f in sorted(glob.glob(os.path.join(base, "**", "*.json"), recursive=True)):
        if os.path.getmtime(f) < lim: continue
        try: d = json.load(open(f))
        except Exception: continue
        d = d.get("body", d) if isinstance(d, dict) else d  # Power Automate pode embrulhar em "body"
        if isinstance(d, dict) and "Chatid" in d: d = {d["Chatid"]: [d]}  # um envio = uma mensagem solta
        for chat, ms in (d or {}).items():
            vistos = {m.get("MessageId") for m in out.get(chat, [])}
            out.setdefault(chat, []).extend(m for m in (ms if isinstance(ms, list) else [ms]) if m.get("MessageId") not in vistos)
    return out


def caixa(dados, pessoa, horas=24, aguardando=4, canais=None):
    """Converte a resposta da API na caixa de entrada dos agentes (mesmo formato de whatsapp_hubspot.py)."""
    agora = datetime.now(TZ); desde = agora - timedelta(hours=horas)
    sys.path.insert(0, os.path.expanduser("~/.claude/skills/celula-daniela/scripts"))
    try:
        from comum import roster, fonte_hubspot, LINK  # noqa
        R, _ = roster()
    except Exception: R, LINK = None, "https://app.hubspot.com/contacts/47865021/deal/{}"
    saida = []
    for chatid, ms in (dados or {}).items():
        ms = [m for m in ms if (not canais or str(m.get("ChannelId")) in canais or str(m.get("CreatedByUser")) in canais)]
        if not ms: continue
        for m in ms: m["_q"] = datetime.fromtimestamp((m.get("Datetime") or 0) / 1000, TZ)
        ms.sort(key=lambda m: m["_q"])
        rec = [m for m in ms if m["_q"] >= desde] or ms[-5:]
        tipo = "grupo" if str(chatid).endswith("@g.us") else "individual"
        nome = next((m.get("ChannelName") for m in rec if m.get("ChannelName") and tipo == "grupo"), None) or \
               next((m.get("senderName") for m in rec if m.get("Direction") == "INCOMING" and m.get("senderName")), None) or \
               re.sub(r"@.*", "", str(chatid))
        entra = [m for m in rec if m.get("Direction") == "INCOMING"]; sai = [m for m in rec if m.get("Direction") == "OUTGOING"]
        ult_ext = entra[-1]["_q"] if entra and not OK_FIM.match(str(entra[-1].get("Message") or "")) else None
        ult_time = sai[-1]["_q"] if sai else None
        espera = (agora - ult_ext).total_seconds() / 3600 if ult_ext and (not ult_time or ult_ext > ult_time) else 0
        master = None
        if R:
            try:
                from whatsapp_hubspot import master_do_texto  # noqa
                master = master_do_texto(nome, R)
            except Exception: pass
        saida.append({"chat": nome, "tipo": tipo, "master": master, "mensagens": len(rec), "fonte": "eazybe-api", "chatid": chatid,
                      "anexos": sum(1 for m in rec if m.get("File") and not str(m.get("FileName") or "").lower().endswith((".mp3", ".ogg", ".opus"))),
                      "audios": sum(1 for m in rec if str(m.get("FileName") or "").lower().endswith((".mp3", ".ogg", ".opus"))),
                      "ultima": rec[-1]["_q"].strftime("%d/%m %H:%M"), "aguardando_time_h": round(espera, 1),
                      "sinal": "AGUARDANDO RESPOSTA" if espera >= aguardando else ("recente sem resposta" if espera > 0 else ""),
                      "negocios": [],
                      "conversa": [{"de": ("time" if m.get("Direction") == "OUTGOING" else (m.get("senderName") or m.get("SentByNumber") or "parceiro")),
                                    "quando": m["_q"].strftime("%d/%m %H:%M"),
                                    "texto": (str(m.get("Message") or "") + (f" [arquivo: {m.get('FileName')} {m.get('File')}]" if m.get("File") else ""))[:1500],
                                    "lida": m.get("Ack") == 3} for m in rec[-40:]]})
    saida.sort(key=lambda s: (-s["aguardando_time_h"], s["chat"]))
    return saida


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["testar", "caixa"]); ap.add_argument("--pessoa", default="daniela")
    ap.add_argument("--horas", type=float, default=24); ap.add_argument("--aguardando", type=float, default=4); ap.add_argument("--arquivo")
    ap.add_argument("--gravar", action="store_true", help="grava a caixa em celulas/<pessoa>/whatsapp (sem isso, só mostra)")
    a = ap.parse_args()
    if a.cmd == "testar":
        d = baixar(int((time.time() - 3600) * 1000)) if _env("EAZYBE_API_URL") else ler_pasta(24)
        print(f"acesso ok: {len(d)} conversa(s) recebidas pelo webhook nas últimas 24h")
        sys.exit(0)
    dados = json.load(open(a.arquivo)) if a.arquivo else (baixar(int((time.time() - a.horas * 3600) * 1000)) if _env("EAZYBE_API_URL") else ler_pasta(a.horas))
    cfg = json.load(open(CFG)) if os.path.exists(CFG) else {}
    canais = [str(x) for x in (cfg.get("eazybe_canais") or {}).get(a.pessoa, [])] or None
    s = caixa(dados, a.pessoa, a.horas, a.aguardando, canais)
    if a.gravar:
        pasta = os.path.join(AP, "celulas", a.pessoa, "whatsapp"); os.makedirs(pasta, exist_ok=True); os.chmod(pasta, 0o700)
        f = os.path.join(pasta, f"caixa-{datetime.now(TZ):%Y-%m-%d-%Hh%M}-eazybe.json"); json.dump(s, open(f, "w"), ensure_ascii=False, indent=1); print(f)
    else:
        print(json.dumps(s, ensure_ascii=False, indent=1)[:3000])
