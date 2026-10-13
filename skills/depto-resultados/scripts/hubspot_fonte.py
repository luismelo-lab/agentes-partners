#!/usr/bin/env python3
"""Leitura direta do HubSpot (API v3, somente leitura) para o relatório semanal.

Credencial: token de Private App com escopos SOMENTE LEITURA
(crm.objects.deals.read, crm.schemas.deals.read, crm.objects.owners.read),
salvo pelo próprio usuário em ~/agentes-partners/.env como HUBSPOT_TOKEN=...
O token nunca é impresso, logado ou passado na linha de comando.

Uso:
  python3 hubspot_fonte.py --testar       # valida o acesso (sem mostrar o token)
  python3 hubspot_fonte.py --descobrir    # lista pipelines e campos candidatos a honorário/parceiro/tese
  python3 hubspot_fonte.py --baixar       # baixa os negócios do escopo → dados/hubspot-AAAA-MM-DD.json
"""
import argparse, json, os, subprocess, sys, time
from datetime import date

BASE = os.path.expanduser("~/agentes-partners")
ENV = os.path.join(BASE, ".env")
MAP = os.path.join(BASE, "departamentos/resultados/mapeamento-hubspot.json")
OUT = os.path.join(BASE, "departamentos/resultados/dados")
API = "https://api.hubapi.com"


def token():
    t = os.environ.get("HUBSPOT_TOKEN")
    if not t and os.path.exists(ENV):
        for line in open(ENV):
            if line.strip().startswith("HUBSPOT_TOKEN="):
                t = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not t:
        sys.exit("Sem credencial: crie ~/agentes-partners/.env com a linha HUBSPOT_TOKEN=<token da Private App somente leitura>.")
    return t


def call(method, path, body=None, tries=6):
    # o cabeçalho com o token vai por stdin (-K -), fora da linha de comando e dos logs
    cfg = f'header = "Authorization: Bearer {token()}"\nheader = "Content-Type: application/json"\n'
    args = ["curl", "-sS", "-m", "60", "-K", "-", "-X", method, "-w", "\n%{http_code}", API + path]
    if body is not None: args += ["--data-binary", json.dumps(body)]
    motivo = ""
    for i in range(tries):
        if i: time.sleep(min(60, 5 * 2 ** (i - 1)))  # 5, 10, 20, 40, 60 s: cobre a rede instável logo depois que o Mac acorda
        r = subprocess.run(args, input=cfg.encode(), capture_output=True)
        txt = r.stdout.decode("utf-8", "replace"); raw, _, code = txt.rpartition("\n")
        if code == "429" or code.startswith("5"):
            motivo = f"HTTP {code}"; continue
        if code == "000" or r.returncode:  # sem resposta: rede caiu, DNS, tempo esgotado (a mensagem do curl não traz o token)
            motivo = f"sem resposta (curl {r.returncode}: {r.stderr.decode('utf-8', 'replace').strip()[:200]})"
            print(f"HubSpot {path}: {motivo}; tentativa {i + 1} de {tries}", file=sys.stderr); continue
        if code == "401": sys.exit("HubSpot recusou o token (401): expirado ou revogado. Gere um novo na Private App.")
        if code == "403": sys.exit(f"HubSpot negou acesso (403) a {path}: falta escopo de leitura na Private App.")
        if not code.startswith("2"): sys.exit(f"Erro HubSpot {code} em {path}: {raw[:300]}")
        try:
            return json.loads(raw) if raw else {}
        except json.JSONDecodeError:  # resposta cortada no meio
            motivo = f"JSON cortado ({len(raw)} bytes)"
            print(f"HubSpot {path}: {motivo}; tentativa {i + 1} de {tries}", file=sys.stderr)
    sys.exit(f"HubSpot indisponível após {tries} tentativas ({path}). Último motivo: {motivo}")


def pipelines():
    res = call("GET", "/crm/v3/pipelines/deals")["results"]
    out = {}
    for p in res:
        st = {}
        for s in p["stages"]:
            md = s.get("metadata", {})
            closed = str(md.get("isClosed", "false")).lower() == "true"
            prob = float(md.get("probability", 0) or 0)
            st[s["id"]] = {"nome": s["label"], "status": ("ganho" if closed and prob >= 1 else "perdido" if closed else "aberto"), "prob": prob}
        out[p["id"]] = {"nome": p["label"], "etapas": st}
    return out


def descobrir():
    props = call("GET", "/crm/v3/properties/deals")["results"]
    chave = ("honor", "parceir", "partner", "repasse", "margem", "tese", "variante", "segment", "cnae", "receb", "pagament", "ressarc", "percent", "comiss")
    cand = [{"nome": p["name"], "rotulo": p["label"], "tipo": p["type"], "grupo": p.get("groupName")} for p in props if any(k in (p["name"] + " " + p["label"]).lower() for k in chave)]
    pl = pipelines()
    print(json.dumps({"pipelines": {k: v["nome"] for k, v in pl.items()}, "campos_candidatos": cand}, ensure_ascii=False, indent=1))


def _buscar(filtros, campos, desde, mensal=True):
    """Busca paginada; em janelas mensais de criação quando o volume pode passar do limite de 10 mil por busca."""
    if not mensal:
        out, after = [], None
        while True:
            body = {"filterGroups": [{"filters": filtros + [{"propertyName": "createdate", "operator": "GTE", "value": desde + "T00:00:00Z"}]}], "properties": campos, "limit": 100}
            if after: body["after"] = after
            r = call("POST", "/crm/v3/objects/deals/search", body)
            out += r.get("results", []); after = r.get("paging", {}).get("next", {}).get("after")
            if not after: return out
            time.sleep(0.12)
    out = []; y, m = int(desde[:4]), int(desde[5:7]); hoje = date.today()
    while (y, m) <= (hoje.year, hoje.month):
        ini = f"{y:04d}-{m:02d}-01"; y2, m2 = (y + 1, 1) if m == 12 else (y, m + 1); fim = f"{y2:04d}-{m2:02d}-01"
        after = None
        while True:
            body = {"filterGroups": [{"filters": filtros + [{"propertyName": "createdate", "operator": "GTE", "value": ini + "T00:00:00Z"},
                                                             {"propertyName": "createdate", "operator": "LT", "value": fim + "T00:00:00Z"}]}],
                    "properties": campos, "limit": 100}
            if after: body["after"] = after
            r = call("POST", "/crm/v3/objects/deals/search", body)
            out += r.get("results", []); after = r.get("paging", {}).get("next", {}).get("after")
            if not after: break
            time.sleep(0.12)
        y, m = y2, m2
    return out


def _pct(v):
    """Percentuais chegam misturados no HubSpot ('30' e '0.3' = 30%)."""
    if v in (None, ""): return None
    try: f = float(v)
    except ValueError: return None
    return f / 100 if f > 1 else f


def baixar():
    cfg = json.load(open(MAP)); C = cfg["campos"]; E = cfg["escopo"]
    pl = pipelines()
    extra = [v for k, v in C.items() if isinstance(v, str) and not k.startswith("_")] + list((C.get("_outras_comissoes_a_confirmar") or {}).values())
    X = cfg.get("campos_extras") or {}
    extra += list(X.values())
    campos = sorted({"dealname", "amount", "createdate", "closedate", "dealstage", "pipeline", "hubspot_owner_id"} | set(extra))
    desde = E.get("desde", "2024-01-01"); base = []
    if E.get("pipelines"): base.append({"propertyName": "pipeline", "operator": "IN", "values": E["pipelines"]})
    brutos = {}
    for o in E.get("owners") or []:
        for d in _buscar(base + [{"propertyName": "hubspot_owner_id", "operator": "EQ", "value": o}], campos, desde): brutos[d["id"]] = d
    roster = E.get("parceiros_roster") or {}
    alias = {a.lower(): canon for canon, al in roster.items() for a in al}
    toks = sorted({(a.split()[0] if " " in a else a) for a in alias})
    for tok in toks:
        for d in _buscar(base + [{"propertyName": C["parceiro"], "operator": "CONTAINS_TOKEN", "value": tok}], campos, desde, mensal=False): brutos[d["id"]] = d
    def canon(nome):
        n = (nome or "").lower()
        for a, c in sorted(alias.items(), key=lambda x: -len(x[0])):
            if a in n: return c
        return None
    owners_ok = set(E.get("owners") or []); norm = []
    for d in brutos.values():
        p = d["properties"]; pid = p.get("pipeline"); sid = p.get("dealstage")
        c = canon(p.get(C["parceiro"]))
        if p.get("hubspot_owner_id") not in owners_ok and not c: continue   # falso positivo da busca por token
        et = pl.get(pid, {}).get("etapas", {}).get(sid, {})
        norm.append({"id": d["id"], "nome": p.get("dealname"), "valor": float(p["amount"]) if p.get("amount") else 0.0,
                     "criado": (p.get("createdate") or "")[:10], "fechado": (p.get("closedate") or "")[:10],
                     "status": et.get("status", "aberto"), "prob": et.get("prob"), "pipeline": pl.get(pid, {}).get("nome", pid), "etapa": et.get("nome"),
                     "owner": p.get("hubspot_owner_id"), "parceiro": c or "Outros (fora do roster)", "parceiro_bruto": p.get(C["parceiro"]),
                     "segmento": p.get(C["segmento"]) if C.get("segmento") else None, "cnae": p.get(C.get("cnae") or "cnae"),
                     "hContr": _pct(p.get(C["honorario_pct"])), "hParc": _pct(p.get(C["parceiro_pct"])),
                     "variante": p.get(C["variante"]) if C.get("variante") else None,
                     "outras_comissoes": {k: _pct(p.get(v)) for k, v in (C.get("_outras_comissoes_a_confirmar") or {}).items()},
                     "recebido": None,
                     "extras": {k: p.get(v) for k, v in X.items()}})
    os.makedirs(OUT, exist_ok=True)
    f = os.path.join(OUT, f"hubspot-{date.today().isoformat()}.json")
    json.dump({"baixado_em": time.strftime("%Y-%m-%d %H:%M"), "fonte": "HubSpot API v3", "negocios": norm}, open(f + ".tmp", "w"), ensure_ascii=False)
    os.replace(f + ".tmp", f)  # gravação atômica: as sentinelas nunca leem um arquivo pela metade
    print(f, len(norm))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--testar", action="store_true"); g.add_argument("--descobrir", action="store_true"); g.add_argument("--baixar", action="store_true")
    a = ap.parse_args()
    if a.testar:
        call("GET", "/crm/v3/pipelines/deals"); print("Acesso ao HubSpot OK (token válido, leitura de pipelines permitida).")
    elif a.descobrir: descobrir()
    else: baixar()
