#!/usr/bin/env python3
"""Dossiês de decisão do Luis (pedido do Luis de 26/10/2026): toda decisão pendente da alçada dele sai com
contexto, opções, recomendação e a validação das áreas responsáveis.

Fontes das pendentes:
  conselho/decisoes.md            linhas "pendente" da alçada do Luis (mesma regra de infra/gestao.py)
  docs/revisao-2026-10-22/decisoes.json   itens da folha; item que cita Dnn pendente fica coberto por esse Dnn;
                                           item que cita só decisão já resolvida sai; o resto vira F<item>
Dossiês: registro/gestao/dossies/<id>.json (fora do git; schema em skills/gabinete/scripts/dossies/README.md)

Uso:
  python3 skills/gabinete/scripts/dossies_decisao.py            lista pendentes e aponta sem dossiê ou velho (> 7 dias)
  python3 skills/gabinete/scripts/dossies_decisao.py --json     mesmo resultado em JSON
  python3 skills/gabinete/scripts/dossies_decisao.py --indice   grava registro/gestao/dossies/indice.json
  python3 skills/gabinete/scripts/dossies_decisao.py --md <arquivo.md>   Markdown do Word, em ordem de urgência
  --max-dias N (padrão 7) · saída 1 quando há pendente sem dossiê, velho ou sem validação de área
"""
import json, os, re, sys
from datetime import date

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))   # repositório (worktree ou main)
AP = os.environ.get("PARTNERS_AP") or os.path.expanduser("~/agentes-partners")       # dados fora do git
PASTA = os.path.join(AP, "registro", "gestao", "dossies")
sys.path.insert(0, os.path.join(RAIZ, "infra"))
import gestao  # noqa: E402


def pendentes():
    dec = gestao.decisoes_pendentes(os.path.join(RAIZ, "conselho", "decisoes.md")) or []
    ids = [d["id"] for d in dec]
    out = [{"id": d["id"], "texto": d["texto"], "origem": "conselho/decisoes.md", "data": d.get("data", "")} for d in dec]
    try:
        folha = json.load(open(os.path.join(RAIZ, "docs", "revisao-2026-10-22", "decisoes.json"), encoding="utf-8"))["itens"]
    except (OSError, KeyError, ValueError):
        folha = []
    for it in folha:
        cit = re.findall(r"\bD\d+\b", it.get("decisao", ""))
        if any(c in ids for c in cit):
            continue                      # coberto pelo dossiê do Dnn
        if cit and re.match(r"^D\d+\s*·", it.get("decisao", "")):
            continue                      # item de decisão já resolvida (ex.: D106 pela D111)
        out.append({"id": f"F{it['id']}", "texto": it.get("decisao", ""), "origem": "folha de decisões", "data": ""})
    return out


def ler(id_):
    try:
        return json.load(open(os.path.join(PASTA, f"{id_}.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return None


def conferir(max_dias=7, hoje=None):
    hoje = hoje or date.today()
    res = []
    for p in pendentes():
        d = ler(p["id"]); st = "ok"; idade = None
        if not d:
            st = "sem dossiê"
        else:
            try:
                idade = (hoje - date.fromisoformat(d.get("atualizado_em", "1900-01-01"))).days
            except ValueError:
                idade = 9999
            if idade > max_dias: st = "velho"
            elif not d.get("validacoes"): st = "sem validação"
        res.append({**p, "status": st, "idade_dias": idade,
                    "titulo": (d or {}).get("titulo", ""), "urgencia": (d or {}).get("urgencia"), "prazo": (d or {}).get("prazo", ""),
                    "recomendacao": (d or {}).get("recomendacao", ""),
                    "pareceres": [f"{v['area']}: {v['parecer']}" for v in (d or {}).get("validacoes", [])],
                    "divergencias": (d or {}).get("divergencias", "")})
    return res


def indice(res):
    ok = sorted([r for r in res if r["urgencia"]], key=lambda r: r["urgencia"])
    doc = {"atualizado_em": date.today().isoformat(), "total_pendentes": len(res),
           "sem_dossie": [r["id"] for r in res if r["status"] == "sem dossiê"],
           "velhos": [r["id"] for r in res if r["status"] == "velho"],
           "itens": [{k: r[k] for k in ("id", "titulo", "urgencia", "prazo", "status", "recomendacao", "pareceres", "divergencias")} for r in ok]}
    os.makedirs(PASTA, exist_ok=True)
    json.dump(doc, open(os.path.join(PASTA, "indice.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return doc


def _br(d):
    try: y, m, dd = d.split("-"); return f"{dd}/{m}/{y}"
    except ValueError: return d


def markdown(res):
    L = ["# Dossiê de decisões do Luis", "",
         f"Decisões pendentes da sua alçada em {_br(date.today().isoformat())}, em ordem de urgência. Cada uma traz o que decidir, por que agora, o contexto com fonte, as opções, a recomendação do Gabinete e o parecer das áreas responsáveis.",
         "", "Leitura: **fato** é dado com fonte e data; **estimativa** é cálculo com premissa; **opinião** é juízo de uma área. Valores são potenciais (honorário contratado, não recebido, antes de impostos). Norma tributária ou jurídica é pré-análise para validação humana. Nada aqui promete valor, prazo ou êxito.", "",
         "## Resumo", "", "| # | ID | Decisão | Prazo | Recomendação | Áreas |", "|---|---|---|---|---|---|"]
    docs = sorted([ler(r["id"]) for r in res if ler(r["id"])], key=lambda d: d["urgencia"])
    for d in docs:
        n = {"concorda": 0, "concorda com ressalva": 0, "discorda": 0}
        for v in d["validacoes"]: n[v["parecer"]] = n.get(v["parecer"], 0) + 1
        rec = d["recomendacao"].split(":")[0].split(";")[0][:90]
        L.append(f"| {d['urgencia']} | {d['id']} | {d['titulo']} | {_br(d['prazo'])} | {rec} | {n['concorda']} concorda · {n['concorda com ressalva']} com ressalva · {n['discorda']} discorda |")
    for d in docs:
        L += ["", f"## {d['urgencia']}. {d['id']} · {d['titulo']}", ""]
        meta = f"**Prazo:** {_br(d['prazo'])}"
        if d.get("folha_item"): meta += f" · **Folha:** item {d['folha_item']}"
        if d.get("padrao"): meta += f" · **Padrão:** {d['padrao']}"
        L += [meta, "", f"**O que decidir.** {d['o_que_decidir']}", "", f"**Por que agora.** {d['por_que_agora']}", "",
              f"**Custo de não decidir.** {d['custo_nao_decidir']}", "", "### Contexto", "", "| Tipo | Fato | Fonte |", "|---|---|---|"]
        for c in d["contexto"]:
            L.append(f"| {c['tipo']} | {c['fato'].replace('|', '/')} | {c['fonte'].replace('|', '/')} |")
        L += ["", "### Opções", "", "| Opção | Prós | Contras | Risco | Efeito |", "|---|---|---|---|---|"]
        for o in d["opcoes"]:
            L.append(f"| {o['nome']} | {o['pros']} | {o['contras']} | {o['risco']} | {o['efeito']} |")
        L += ["", f"**Recomendação do Gabinete.** {d['recomendacao']}", "", f"**Se for reprovada.** {d['se_reprovada']}", "",
              "### Validação das áreas", "", "| Área (especialista) | Parecer | Motivo e condição de sucesso | Base |", "|---|---|---|---|"]
        for v in d["validacoes"]:
            mot = v["motivo"] + (f" Ressalva: {v['ressalva']}" if v.get("ressalva") else "") + f" Condição: {v['condicao']}"
            L.append(f"| {v['area']} ({v['especialista']}) | {v['parecer']} | {mot.replace('|', '/')} | {v['base'].replace('|', '/')} |")
        L += ["", f"**Divergências.** {d['divergencias']}", "",
              f"**Execução depois de aprovada.** Dono: {d['execucao']['dono']}. Prazo: {d['execucao']['prazo']}. Indicador: {d['execucao']['indicador']}."]
    L += ["", "## Como responder", "", "Responda por ID, por exemplo: \"aprovo D105, D104 e D107; aprovo D109 na opção B; reprovo D52\". O Gabinete registra em conselho/decisoes.md e aciona o dono da execução."]
    return "\n".join(L) + "\n"


def main():
    a = sys.argv[1:]
    md = max_dias = None
    max_dias = int(a[a.index("--max-dias") + 1]) if "--max-dias" in a else 7
    res = conferir(max_dias)
    if "--indice" in a:
        doc = indice(res); print(f"indice.json: {len(doc['itens'])} dossiês, {len(doc['sem_dossie'])} sem dossiê, {len(doc['velhos'])} velhos")
    if "--md" in a:
        md = a[a.index("--md") + 1]; open(md, "w", encoding="utf-8").write(markdown(res)); print(f"Markdown: {md}")
    if "--json" in a:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    elif "--indice" not in a and "--md" not in a:
        for r in res:
            print(f"{r['id']:>5}  {r['status']:<14} {r['titulo'] or r['texto'][:70]}")
        falta = [r["id"] for r in res if r["status"] != "ok"]
        print(f"\n{len(res)} pendentes · {len(res) - len(falta)} com dossiê válido · faltam: {', '.join(falta) or 'nenhum'}")
    sys.exit(1 if any(r["status"] != "ok" for r in res) else 0)


if __name__ == "__main__":
    main()
