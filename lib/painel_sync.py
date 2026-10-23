#!/usr/bin/env python3
"""Aplica no Mac o que o time registrou no painel Central Partners (base do artifact).

A rotina do Claude baixa as coleções do painel com a ferramenta ArtifactData (out_dir) e roda:
  python3 lib/painel_sync.py <pasta_baixada>
Coleções tratadas aqui (idempotente: cada registro é aplicado uma vez):
  acoes_demandas/<D-id>   → fecha a demanda no registro único (respondida, encaminhada ou "não é demanda")
  recuperador/<deal>      → decisões da Geovana (celulas/geovana/recuperador/decisoes-painel.json, lidas pelo lote semanal)
  conselho/<D-id>         → atualiza conselho/decisoes.md (status, observação e data)
  apontamentos/<id>       → registro/apontamentos.json (Semana 0: diagnóstico das tarefas do time)
A coleção pedidos/ é tratada pela rotina da Central (precisa do Claude para responder).
Autor (A3, 23/10/2026): só vale o registro cujo `por_id` é uma das quatro contas (infra/portal-contas.json) e cuja pessoa é a dona
da ação (a dona da demanda, a Geovana no lote, o Luis no Conselho, a própria pessoa no apontamento). O resto é descartado e vira
alerta ao Luis (registro/portal-alertas.json); sai na contagem "descartados".
"""
import glob, json, os, re, sys
from datetime import date

AP = os.environ.get("PARTNERS_AP") or os.path.expanduser("~/agentes-partners")
FEITOS = os.path.join(AP, "registro", "painel-aplicados.json")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import portal_contas as PC  # noqa: E402


def docs(pasta, colecao):
    out = {}
    for f in glob.glob(os.path.join(pasta, colecao, "*.json")):
        try: d = json.load(open(f))
        except (OSError, ValueError): continue
        d = d["data"] if isinstance(d, dict) and isinstance(d.get("data"), dict) else d
        if isinstance(d, dict): out[os.path.basename(f)[:-5]] = d
    return out


def autor(res, colecao, i, d, esperado):
    ok, motivo = PC.conferir(d.get("por") if colecao != "apontamentos" else d.get("pessoa"), d.get("por_id"), esperado)
    if not ok:
        PC.alertar(colecao, i, motivo, d.get("por") or d.get("pessoa"), d.get("por_id")); res["descartados"] += 1
    return ok


def chave(c, i, d):
    return f"{c}/{i}/{d.get('quando') or d.get('data') or ''}"


def main():
    pasta = sys.argv[1]
    feitos = set(json.load(open(FEITOS))) if os.path.exists(FEITOS) else set()
    res = {"demandas": 0, "recuperador": 0, "conselho": 0, "apontamentos": 0, "descartados": 0}
    sys.path.insert(0, os.path.join(AP, "lib")); import registro_demandas as RD

    acoes = {i: d for i, d in docs(pasta, "acoes_demandas").items() if chave("acoes", i, d) not in feitos}
    if acoes:
        with RD.Registro() as R:
            for i, d in acoes.items():
                x = R["demandas"].get(i)
                if x and d.get("status") in ("respondido", "encaminhado", "nao_e_demanda") and not autor(res, "acoes_demandas", i, d, x.get("pessoa")):
                    continue  # sem autor válido: não marca como feito; vale se a conta for incluída depois
                if x and x["status"] in RD.ABERTOS and d.get("status") in ("respondido", "encaminhado", "nao_e_demanda"):
                    x["status"] = {"respondido": "resolvida", "encaminhado": "encaminhada", "nao_e_demanda": "descartada"}.get(d["status"], "resolvida")
                    x["eventos"].append({"quando": d.get("quando"), "evento": f"painel: {d['status']} ({d.get('por')})"}); x["atualizada_em"] = d.get("quando")
                    res["demandas"] += 1
                feitos.add(chave("acoes", i, d))

    rec = {i: d for i, d in docs(pasta, "recuperador").items() if chave("recup", i, d) not in feitos}
    if rec:
        f = os.path.join(AP, "celulas/geovana/recuperador/decisoes-painel.json")
        atual = json.load(open(f)) if os.path.exists(f) else {}
        for i, d in rec.items():
            if not d.get("decisao") or not autor(res, "recuperador", i, d, "geovana"): continue
            feitos.add(chave("recup", i, d))
            atual[i] = d; res["recuperador"] += 1
        json.dump(atual, open(f, "w"), ensure_ascii=False, indent=1)

    cons = {i: d for i, d in docs(pasta, "conselho").items() if chave("cons", i, d) not in feitos}
    if cons:
        p = os.path.join(AP, "conselho/decisoes.md"); linhas = open(p).read().split("\n"); hoje = date.today().isoformat()
        for i, d in cons.items():
            if not d.get("decisao") or not autor(res, "conselho", i, d, "luis"): continue
            feitos.add(chave("cons", i, d))
            for k, l in enumerate(linhas):
                c = l.split("|")
                if len(c) > 7 and c[1].strip() == i and c[5].strip() == "pendente":
                    c[5] = f" {d['decisao']} "; c[6] = f" {('Painel ' + hoje + ': ' + d['nota']) if d.get('nota') else 'Decidido no painel'} "; c[7] = f" {hoje} "
                    linhas[k] = "|".join(c)
            res["conselho"] += 1
        open(p, "w").write("\n".join(linhas))

    ap = {i: d for i, d in docs(pasta, "apontamentos").items() if chave("apont", i, d) not in feitos}
    if ap:
        f = os.path.join(AP, "registro/apontamentos.json"); atual = json.load(open(f)) if os.path.exists(f) else []
        for i, d in ap.items():
            if not autor(res, "apontamentos", i, d, None): continue
            feitos.add(chave("apont", i, d))
            atual.append({"id": i, **d}); res["apontamentos"] += 1
        json.dump(atual, open(f, "w"), ensure_ascii=False, indent=1)

    json.dump(sorted(feitos), open(FEITOS, "w"))
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
