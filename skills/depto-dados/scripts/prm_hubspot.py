#!/usr/bin/env python3
"""PRM Save · complemento do download do HubSpot pela API (só leitura) para o acompanhamento de negócios do parceiro.

Dono: Dados & BI. Pedido do Luis (27/10/2026): "temos uma API de consulta dos negócios; use para replicar os negócios".
O download do dia (hubspot_fonte.py) não traz a data de entrada em cada etapa, o próximo passo, o motivo da perda nem o
nome do responsável. Este script lê esses campos dos mesmos negócios (POST /crm/v3/objects/deals/batch/read, 100 por vez,
e GET /crm/v3/owners) e grava departamentos/resultados/dados/prm-complemento-AAAA-MM-DD.json (permissão 600), que o
prm_local.py junta aos `extras` de cada negócio. O nome do arquivo não começa com "hubspot-" para nenhuma rotina o
confundir com o download.

Não escreve no HubSpot. O token é o do hubspot_fonte.py (Private App só leitura); nunca é lido nem impresso aqui.
Nome da empresa e dado de sócio não entram (regra do prm_local.py). Motivo da perda e pendência são campos internos
(PRM-R114, travados para o parceiro); o texto do próximo passo passa pelo auditor antes de chegar ao parceiro.

Uso:
  prm_hubspot.py [--fonte hubspot-AAAA-MM-DD.json]    complementa o download (padrão: o mais recente)
"""
import argparse, glob, json, os, sys, time

AP = os.environ.get("PARTNERS_AP") or os.path.expanduser("~/agentes-partners")
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "skills", "depto-resultados", "scripts"))
import hubspot_fonte as H  # noqa: E402  (mesma chamada com novas tentativas e token fora da linha de comando)

DADOS = os.path.join(AP, "departamentos/resultados/dados")
LOTE = 100
TEXTO = {"proximo_passo": "hs_next_step", "proximo_passo_em": "hs_next_step_updated_at",
         "pendencia": "motivo_da_pendencia", "pendencia_fechamento": "motivo_da_pendencia_de_fechamento",
         "motivo_perda_texto": "descricao_do_motivo_da_perda"}
# motivo de perda em lista: um campo por funil (só os que existem na conta entram na leitura)
MOTIVOS_LISTA = ("inteligencia_tributaria__motivos_de_perda", "gestao_de_parceiros_motivos_de_perda",
                 "passivo__motivos_de_perda", "save_partners__motivos_de_perda", "comunidade_save__motivos_de_perda")


def complemento_de(fonte):
    return os.path.join(os.path.dirname(fonte), os.path.basename(fonte).replace("hubspot-", "prm-complemento-", 1))


def donos():
    out, after = {}, None
    while True:
        r = H.call("GET", "/crm/v3/owners?limit=100&archived=false" + (f"&after={after}" if after else ""))
        for o in r.get("results", []):
            nome = " ".join(x for x in (o.get("firstName"), o.get("lastName")) if x).strip()
            if nome: out[str(o["id"])] = nome
        after = r.get("paging", {}).get("next", {}).get("after")
        if not after: return out


def historico(p, etapas):
    """Datas de entrada em cada etapa (hs_v2_date_entered_<id>), em ordem; o rótulo é o do funil do negócio."""
    hist = [{"etapa": nome, "entrou_em": H.dia_br(p.get("hs_v2_date_entered_" + sid))}
            for sid, nome in etapas.items() if p.get("hs_v2_date_entered_" + sid)]
    return sorted(hist, key=lambda h: h["entrou_em"])


def montar(negocios, pl, existentes, ler_lote, nomes):
    """Separado da rede para teste: `ler_lote(ids, campos)` devolve a lista de {"id", "properties"}."""
    por_nome = {v["nome"]: v for v in pl.values()}
    etapas = {}
    for d in negocios:
        p = por_nome.get(d.get("pipeline"))
        if p: etapas.setdefault(d["pipeline"], {sid: e["nome"] for sid, e in p["etapas"].items()})
    datas = sorted({"hs_v2_date_entered_" + sid for et in etapas.values() for sid in et})
    motivos = [m for m in MOTIVOS_LISTA if m in existentes]
    campos = sorted(set(TEXTO.values()) | set(motivos) | set(datas) | {"hubspot_owner_id"})
    out = {}
    ids = [d["id"] for d in negocios]
    pipe = {d["id"]: d.get("pipeline") for d in negocios}
    for i in range(0, len(ids), LOTE):
        for r in ler_lote(ids[i:i + LOTE], campos):
            p = r.get("properties") or {}
            item = {k: (p.get(v) or None) for k, v in TEXTO.items()}
            if item["proximo_passo_em"]: item["proximo_passo_em"] = H.dia_br(item["proximo_passo_em"])
            texto = item.pop("motivo_perda_texto")
            item["motivo_perda"] = next((p[m] for m in motivos if p.get(m)), None) or texto
            item["historico_etapas"] = historico(p, etapas.get(pipe.get(r["id"]), {}))
            item["owner_nome"] = nomes.get(str(p.get("hubspot_owner_id") or ""))
            out[r["id"]] = {k: v for k, v in item.items() if v not in (None, [], "")}
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--fonte")
    a = ap.parse_args()
    fonte = a.fonte or (sorted(glob.glob(os.path.join(DADOS, "hubspot-*.json"))) or [None])[-1]
    if not fonte or not os.path.exists(fonte): sys.exit("Sem download do HubSpot: rode `partners hubspot`.")
    D = json.load(open(fonte, encoding="utf-8"))
    existentes = {p["name"] for p in H.call("GET", "/crm/v3/properties/deals")["results"]}

    def ler_lote(ids, campos):
        time.sleep(0.12)
        return H.call("POST", "/crm/v3/objects/deals/batch/read", {"properties": campos, "inputs": [{"id": x} for x in ids]}).get("results", [])

    neg = montar(D["negocios"], H.pipelines(), existentes, ler_lote, donos())
    saida = complemento_de(fonte); tmp = saida + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"baixado_em": time.strftime("%Y-%m-%d %H:%M"), "fonte": "HubSpot API v3 (batch/read, só leitura)",
                   "base": os.path.basename(fonte), "negocios": neg}, f, ensure_ascii=False)
    os.replace(tmp, saida)
    cont = {k: sum(1 for x in neg.values() if x.get(k)) for k in ("historico_etapas", "owner_nome", "proximo_passo", "pendencia", "motivo_perda")}
    print(json.dumps({"saida": saida, "negocios": len(neg), "preenchidos": cont}, ensure_ascii=False))


if __name__ == "__main__":
    main()
