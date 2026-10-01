#!/usr/bin/env python3
"""Leitor do Bitrix24 (somente consulta): em que fase da execução está cada negócio ganho.

Mapeado em 01/10/2026 com a sessão do Luis (só leitura):
  - A execução é um processo à parte, ligado ao negócio do Bitrix (parentId2 = ID do negócio = "ID Bitrix" no HubSpot):
      162 "Execução Lucro Real", com 8 funis (PIS/COFINS, Compensação, Judicial, Passivo, Previdenciário,
          Contencioso Adm, Consultivo, Pós-Vendas)
      152 "Execução Holding"
  - Fases e grupos (ativa / espera natural / encerrada) em infra/bitrix-execucao.json.

Credencial: webhook de entrada do Bitrix (criado pela TI) em ~/agentes-partners/.env na linha
BITRIX_WEBHOOK=https://save.bitrix24.com.br/rest/<usuario>/<codigo>/ . O endereço tem a chave dentro:
nunca é impresso nem vai para log ou linha de comando (vai ao curl por stdin).
Proteção: o Bitrix não tem permissão de CRM só leitura; este cliente aceita apenas os métodos de consulta abaixo.

Uso:
  bitrix.py testar           confere o acesso (sem mostrar o endereço)
  bitrix.py baixar           grava departamentos/resultados/dados/bitrix-execucao-AAAA-MM-DD.json
  bitrix.py negocio <id>     fase da execução de um negócio (ID Bitrix)
"""
import glob, json, os, subprocess, sys, time
from datetime import date

AP = os.path.expanduser("~/agentes-partners"); ENV = os.path.join(AP, ".env")
DADOS = os.path.join(AP, "departamentos/resultados/dados")
CFG = json.load(open(os.path.join(AP, "infra/bitrix-execucao.json")))
SO_CONSULTA = {"crm.item.list", "crm.item.get", "crm.deal.get", "crm.status.list", "crm.category.list", "profile"}


def webhook():
    w = os.environ.get("BITRIX_WEBHOOK")
    if not w and os.path.exists(ENV):
        for l in open(ENV):
            if l.strip().startswith("BITRIX_WEBHOOK="): w = l.split("=", 1)[1].strip().strip('"').strip("'")
    if not w: sys.exit("Sem acesso ao Bitrix: falta a linha BITRIX_WEBHOOK=<endereço do webhook de entrada> em ~/agentes-partners/.env (pedido em docs/BITRIX.md).")
    return w.rstrip("/") + "/"


def disponivel():
    try: webhook(); return True
    except SystemExit: return False


def call(metodo, params=None, tries=4):
    if metodo not in SO_CONSULTA: sys.exit(f"Bloqueado: {metodo} não é método de consulta.")
    cfg = f'url = "{webhook()}{metodo}.json"\nheader = "Content-Type: application/json"\n'
    args = ["curl", "-sS", "-m", "60", "-K", "-", "-X", "POST", "-w", "\n%{http_code}", "--data-binary", json.dumps(params or {})]
    for i in range(tries):
        r = subprocess.run(args, input=cfg.encode(), capture_output=True)
        raw, _, code = r.stdout.decode("utf-8", "replace").rpartition("\n")
        if code in ("429", "503") or code.startswith("5"): time.sleep(2 ** i + 1); continue
        if code in ("401", "403"): sys.exit(f"Bitrix negou acesso ({code}) em {metodo}: webhook revogado ou sem permissão de CRM.")
        J = json.loads(raw or "{}")
        if J.get("error") == "QUERY_LIMIT_EXCEEDED": time.sleep(2 ** i + 1); continue
        if J.get("error"): sys.exit(f"Erro Bitrix em {metodo}: {J.get('error_description') or J.get('error')}")
        return J
    sys.exit(f"Bitrix indisponível após {tries} tentativas ({metodo}).")


def fases():
    out = {}
    for tipo, T in CFG["processos"].items():
        for cat in T["funis"]:
            for s in call("crm.status.list", {"filter": {"ENTITY_ID": f"DYNAMIC_{tipo}_STAGE_{cat}"}}).get("result", []):
                out[s["STATUS_ID"]] = s["NAME"]
    return out


def grupo(nome_fase):
    for g, nomes in CFG["grupos"].items():
        if nome_fase in nomes: return g
    return "ativa"


def itens(ids):
    out = []
    for tipo in CFG["processos"]:
        for i in range(0, len(ids), 40):
            start = 0
            while True:
                J = call("crm.item.list", {"entityTypeId": int(tipo), "filter": {"@parentId2": ids[i:i + 40]},
                                           "select": ["id", "parentId2", "categoryId", "stageId", "movedTime", "createdTime"], "start": start})
                for x in J.get("result", {}).get("items", []): x["tipo"] = tipo; out.append(x)
                if J.get("next") is None: break
                start = J["next"]
    return out


def baixar():
    hub = sorted(glob.glob(os.path.join(DADOS, "hubspot-*.json")))[-1]
    N = json.load(open(hub))["negocios"]
    ids = sorted({int(x) for d in N if d.get("status") == "ganho" for x in [str((d.get("extras") or {}).get("id_bitrix") or "")] if x.isdigit()})
    F = fases(); por = {}
    for x in itens(ids):
        T = CFG["processos"][x["tipo"]]; nf = F.get(x["stageId"], x["stageId"])
        por.setdefault(str(x["parentId2"]), []).append({"processo": T["nome"], "funil": T["funis"].get(str(x["categoryId"]), str(x["categoryId"])),
                                                        "fase": nf, "grupo": grupo(nf), "desde": str(x.get("movedTime"))[:10], "criado": str(x.get("createdTime"))[:10],
                                                        "card": f"https://save.bitrix24.com.br/crm/type/{x['tipo']}/details/{x['id']}/"})
    f = os.path.join(DADOS, f"bitrix-execucao-{date.today().isoformat()}.json")
    json.dump({"baixado_em": time.strftime("%Y-%m-%d %H:%M"), "fonte_hubspot": os.path.basename(hub), "ganhos_consultados": len(ids), "execucoes": por},
              open(f, "w"), ensure_ascii=False, indent=1)
    print(f"execução de {len(por)} de {len(ids)} negócios ganhos → {f}")


def ultimo():
    fs = sorted(glob.glob(os.path.join(DADOS, "bitrix-execucao-*.json")))
    return json.load(open(fs[-1])) if fs else None


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else "ajuda"
    if c == "testar": call("crm.category.list", {"entityTypeId": 162}); print("Acesso ao Bitrix OK (consulta de execução permitida).")
    elif c == "baixar": baixar()
    elif c == "negocio":
        F = fases()
        for x in itens([int(sys.argv[2])]):
            T = CFG["processos"][x["tipo"]]; print(T["funis"].get(str(x["categoryId"])), "→", F.get(x["stageId"]), "desde", str(x["movedTime"])[:10])
    else: print(__doc__)
