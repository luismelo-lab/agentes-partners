#!/usr/bin/env python3
"""Caixa de entrada do WhatsApp a partir do HubSpot (o Eazybe já grava as conversas lá).

O Eazybe registra cada conversa (individual ou grupo) como uma atividade "WhatsApp" do HubSpot,
associada ao contato e ao negócio, alguns minutos depois da mensagem. Este script só LÊ essas
atividades e monta, para cada pessoa do time, uma caixa de entrada local para a Triagem:
conversa → Master → negócio → últimas mensagens → "aguardando resposta do time?".

Nada é enviado, nada é gravado no HubSpot (governança N1). Serve à célula da Daniela, da Jenifer e
da Geovana. Privacidade: o conteúdo fica só em ~/agentes-partners/celulas/<pessoa>/whatsapp (pasta 700),
com retenção de 30 dias; não sai da máquina.

Uso:
  python3 whatsapp_hubspot.py --pessoa daniela [--horas 24] [--aguardando 4]
  python3 whatsapp_hubspot.py --pessoa jenifer --horas 72
"""
import argparse, glob, json, os, re, subprocess, sys, time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import AP, LINK, fonte_hubspot, norm, roster  # noqa: E402

OWNERS = {"daniela": ("79560621", "Daniela Maciel"), "jenifer": ("79401410", "Jenifer Carvalho"),
          "geovana": ("88477477", "Geovana Goncalves")}
CFG = os.path.join(AP, "celulas", "whatsapp-config.json")  # nomes/telefones do time, para saber quem falou
MESES = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                     "september", "october", "november", "december"], 1)}
LINHA = re.compile(r"^(?P<de>[^\[]{1,80}?)\s*\[(?P<d>\d{1,2})(?:st|nd|rd|th)?\s+(?P<m>[A-Za-z]+)\s+(?P<a>\d{4}),\s*(?P<h>\d{1,2}):(?P<mi>\d{2})\]:\s?(?P<t>.*)$")
TZ = timezone(timedelta(hours=-3))


def token():
    """Credencial única: a mesma leitura do hubspot_fonte.py (depto-resultados)."""
    sys.path.insert(0, os.path.expanduser("~/.claude/skills/depto-resultados/scripts"))
    from hubspot_fonte import token as _t
    return _t()


def api(url, body=None, tk=None):
    cfg = f'url = "{url}"\nheader = "Authorization: Bearer {tk}"\nheader = "Content-Type: application/json"\n'
    if body is not None:
        cfg += f'request = "POST"\ndata = {json.dumps(json.dumps(body))}\n'
    for tentativa in range(3):
        r = subprocess.run(["curl", "-sS", "-m", "60", "-K", "-"], input=cfg, capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
        except json.JSONDecodeError:
            d = {}
        if d.get("category") == "RATE_LIMITS" or not r.stdout:
            time.sleep(2 + tentativa * 3); continue
        return d
    return {}


def limpar(html):
    t = re.sub(r"<br\s*/?>", "\n", html or "")
    t = re.sub(r"<[^>]+>", "", t)
    return t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", " ")


def conversa(html):
    """→ (chave do chat, tipo, nome do chat, [mensagens {de, quando, texto}])"""
    html = html or ""
    tipo = "grupo" if "@g.us" in html else "individual"
    m = re.search(r'class="(?:group-|activity_for-)([^"\s]+@[cg]\.us)', html)
    chave = m.group(1) if m else None
    linhas = limpar(html).split("\n")
    cab = linhas[0].strip() if linhas else ""
    mm = re.match(r'^"?(.*?)"?\s*(?:Group Chats?|1:1 Chats?|group chat)?\s*$', cab, re.I)
    nome = (mm.group(1) if mm else cab).strip().strip('"').strip()
    msgs = []
    for l in linhas[1:]:
        m = LINHA.match(l.strip())
        if m:
            try:
                q = datetime(int(m["a"]), MESES[m["m"].lower()], int(m["d"]), int(m["h"]), int(m["mi"]), tzinfo=TZ)
            except (KeyError, ValueError):
                q = None
            msgs.append({"de": m["de"].strip(), "quando": q, "texto": m["t"].strip()})
        elif msgs and l.strip():
            msgs[-1]["texto"] += "\n" + l.strip()  # continuação da mensagem anterior (quebra de linha, link, legenda)
    return chave, tipo, nome, msgs


SISTEMA = re.compile(r"^(AcceptedElsewhere|Missed (voice|video) call|Voice call|Video call|This message was deleted|null)$", re.I)
CORTESIA = re.compile(r"^\W*(ok+|okay|blz|beleza|obrigad[oa]s?|obg|valeu|vlw|disponha|de nada|perfeito|perfeitamente|combinado|show|top|certo|entendi|[kr]{3,}s*|(ha|rs){2,}|👍|🙏|😉|😊|👏)\W*[.!]*\s*$", re.I)


def ignorar(texto):
    """Mensagem que não pede resposta: aviso do sistema ou fechamento de conversa."""
    t = (texto or "").strip().split("\n")[-1]
    return bool(SISTEMA.match(t) or CORTESIA.match(t) or re.fullmatch(r"(rs|kk|ha|\W)+", t.lower() or "x"))


def e_do_time(remetente, cfg):
    r = norm(remetente); dig = re.sub(r"\D", "", remetente)
    if dig and dig in {re.sub(r"\D", "", t) for t in cfg.get("telefones_time", [])}:
        return True
    return any(norm(n) and norm(n) in r for n in cfg.get("nomes_time", []))


def master_do_texto(texto, R):
    """Master pelo nome do grupo/conversa. Siglas curtas (ex.: "D&S") só valem como palavra inteira."""
    k = lambda x: re.sub(r"[^a-z0-9]", "", norm(x))
    t, tn = k(texto), norm(texto)
    for canon, als in R.items():
        for a in [canon] + list(als):
            ka = k(a)
            if len(ka) >= 3 and ka in t:
                return canon
            if 2 <= len(ka) < 3:
                pad = re.escape(norm(a)).replace(r"\&", r"\s*&\s*").replace(r"\ ", r"\s*")
                if re.search(r"(?<![a-z0-9])" + pad + r"(?![a-z0-9])", tn): return canon
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pessoa", required=True, choices=OWNERS)
    ap.add_argument("--horas", type=float, default=24, help="janela de leitura (padrão 24h)")
    ap.add_argument("--aguardando", type=float, default=4, help="horas sem resposta do time para sinalizar (padrão 4)")
    a = ap.parse_args()
    tk = token(); oid, nome_pessoa = OWNERS[a.pessoa]
    cfg = json.load(open(CFG)) if os.path.exists(CFG) else {}
    cfg.setdefault("nomes_time", ["Daniela Maciel", "Jenifer Carvalho", "Geovana", "Luis Fernando", "Luis Melo"])
    R, _ = roster()
    _, D = fonte_hubspot()
    N = {d["id"]: d for d in D["negocios"]}
    agora = datetime.now(TZ); desde = agora - timedelta(hours=a.horas)

    regs, after = [], None
    while True:
        body = {"filterGroups": [{"filters": [
            {"propertyName": "hs_communication_channel_type", "operator": "EQ", "value": "WHATS_APP"},
            {"propertyName": "hubspot_owner_id", "operator": "EQ", "value": oid},
            {"propertyName": "hs_timestamp", "operator": "GTE", "value": desde.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}]}],
            "sorts": [{"propertyName": "hs_timestamp", "direction": "DESCENDING"}],
            "properties": ["hs_communication_body", "hs_timestamp"], "limit": 100}
        if after: body["after"] = after
        r = api("https://api.hubapi.com/crm/v3/objects/communications/search", body, tk)
        if "results" not in r:
            sys.exit(f"HubSpot recusou a leitura: {r.get('category')} {str(r.get('message'))[:200]}")
        regs += r["results"]
        after = (r.get("paging") or {}).get("next", {}).get("after")
        if not after or len(regs) >= 2000: break

    # associações → negócio e contato (em lote)
    assoc = {}
    for i in range(0, len(regs), 100):
        ids = [{"id": x["id"]} for x in regs[i:i + 100]]
        for obj in ("deals",):  # contatos não são usados na saída
            r = api(f"https://api.hubapi.com/crm/v4/associations/communications/{obj}/batch/read", {"inputs": ids}, tk)
            for it in r.get("results", []):
                assoc.setdefault(it["from"]["id"], {})[obj] = [t["toObjectId"] for t in it.get("to", [])]

    chats = {}
    for x in regs:
        chave, tipo, nome, msgs = conversa(x["properties"].get("hs_communication_body"))
        if tipo == "individual" and (not nome or nome.lower().startswith("1:1")):
            nome = next((m["de"] for m in msgs if not e_do_time(m["de"], cfg)), "") or "Conversa individual"
        c = chats.setdefault((chave.split("-")[-1] if chave else None) or nome or x["id"], {"tipo": tipo, "nome": nome, "msgs": [], "deals": set(), "contatos": set()})
        c["msgs"] += msgs
        c["deals"].update(str(d) for d in assoc.get(x["id"], {}).get("deals", []))
        c["contatos"].update(str(d) for d in assoc.get(x["id"], {}).get("contacts", []))

    saida = []
    for c in chats.values():
        vistos, ms = set(), []
        for m in sorted([m for m in c["msgs"] if m["quando"]], key=lambda m: m["quando"]):
            chave = (m["de"], m["quando"], m["texto"][:80])
            if chave not in vistos: vistos.add(chave); ms.append(m)
        ms = [m for m in ms if m["quando"] >= desde] or ms[-5:]
        if not ms: continue
        ult = ms[-1]; ult_time = max((m["quando"] for m in ms if e_do_time(m["de"], cfg)), default=None)
        ext = [m for m in ms if not e_do_time(m["de"], cfg)]
        ult_ext = max((m["quando"] for m in ext if not ignorar(m["texto"])), default=None)
        if ext and ignorar(ext[-1]["texto"]) and (not ult_time or ext[-1]["quando"] > ult_time):
            ult_ext = None  # a conversa terminou num "obrigada"/"ok": nada pendente
        espera = (agora - ult_ext).total_seconds() / 3600 if ult_ext and (not ult_time or ult_ext > ult_time) else 0
        negocios = [N[d] for d in c["deals"] if d in N]
        master = master_do_texto(c["nome"], R) or next((master_do_texto(n.get("parceiro") or "", R) for n in negocios if master_do_texto(n.get("parceiro") or "", R)), None)
        saida.append({"chat": c["nome"], "tipo": c["tipo"], "master": master, "mensagens": len(ms),
                      "anexos": sum("eazybe-attachments" in m["texto"] and not m["texto"].rstrip().endswith(".mp3") for m in ms),
                      "audios": sum(".mp3" in m["texto"] for m in ms),
                      "ultima": ult["quando"].strftime("%d/%m %H:%M"), "aguardando_time_h": round(espera, 1),
                      "sinal": "AGUARDANDO RESPOSTA" if espera >= a.aguardando else ("recente sem resposta" if espera > 0 else ""),
                      "negocios": [{"id": n["id"], "nome": n.get("nome"), "etapa": n.get("etapa"), "link": LINK.format(n["id"])} for n in negocios][:5],
                      "conversa": [{"de": m["de"], "quando": m["quando"].strftime("%d/%m %H:%M"), "texto": m["texto"][:1500]} for m in ms[-40:]]})
    saida.sort(key=lambda s: (-s["aguardando_time_h"], s["chat"]))

    pasta = os.path.join(AP, "celulas", a.pessoa, "whatsapp"); os.makedirs(pasta, exist_ok=True); os.chmod(pasta, 0o700)
    for f in glob.glob(os.path.join(pasta, "caixa-*")):  # retenção de 30 dias
        if time.time() - os.path.getmtime(f) > 30 * 86400: os.remove(f)
    base = os.path.join(pasta, f"caixa-{agora:%Y-%m-%d-%Hh%M}")
    json.dump(saida, open(base + ".json", "w"), ensure_ascii=False, indent=1)
    ag = [s for s in saida if s["sinal"] == "AGUARDANDO RESPOSTA"]
    L = [f"# Caixa de WhatsApp: {nome_pessoa} · últimas {a.horas:g}h (lida em {agora:%d/%m %H:%M})",
         "", f"Fonte: atividades WhatsApp gravadas pelo Eazybe no HubSpot. {len(saida)} conversas "
         f"({sum(s['tipo'] == 'grupo' for s in saida)} grupos, {sum(s['tipo'] == 'individual' for s in saida)} individuais); "
         f"**{len(ag)} aguardando resposta do time há {a.aguardando:g}h ou mais.** Uso interno; nada foi enviado.", "",
         "| Conversa | Tipo | Master | Última | Aguardando | 📎/🎤 | Negócio |", "|---|---|---|---|---|---|---|"]
    for s in saida:
        ng = s["negocios"][0] if s["negocios"] else None
        L.append(f"| {s['chat'][:45]} | {s['tipo']} | {s['master'] or '—'} | {s['ultima']} | "
                 f"{(str(s['aguardando_time_h']) + 'h') if s['aguardando_time_h'] else '—'} | {('📎' + str(s['anexos']) if s['anexos'] else '') + (' 🎤' + str(s['audios']) if s['audios'] else '') or '—'} | {('[' + (ng['nome'] or '')[:30] + '](' + ng['link'] + ')') if ng else '—'} |")
    L += ["", "## Conversas (para a Triagem)", ""]
    for s in saida:
        L += [f"### {s['chat']} · {s['tipo']} · {s['master'] or 'Master não identificado'}" + (f" · ⚠️ {s['sinal']}" if s["sinal"] else ""), ""]
        L += [f"- {m['quando']} **{m['de']}**: {m['texto']}" for m in s["conversa"]] + [""]
    open(base + ".md", "w").write("\n".join(L))
    print(f"{len(regs)} registros → {len(saida)} conversas; {len(ag)} aguardando resposta. Caixa: {base}.md")


if __name__ == "__main__":
    main()
