#!/usr/bin/env python3
"""Cálculo de NPS / CSAT / CES — Qualidade & Ouvidoria (Save Company / Partners).

Os números vêm daqui, nunca de conta de cabeça. Só lê o CSV; não contata ninguém.

Entrada: CSV (separador , ou ;) com cabeçalho. Colunas reconhecidas:
  momento   relacional | pos_onboarding | pos_parecer | pos_ressarcimento | pos_reclamacao
  publico   parceiro | cliente
  conta     identificador da conta (ID do parceiro/negócio no HubSpot) — nunca nome de pessoa
  data      AAAA-MM-DD
  nps       0–10 (opcional por linha)
  csat      1–5 (opcional)
  ces       1–7 (opcional; 7 = muito fácil)
  enviados  (opcional, só em linhas de controle: nº de convites enviados no grupo)

Uso:
  python3 calc_nps.py respostas.csv [--por momento,publico] [--saida relatorio.md] [--json]

Regras de leitura (ver references/nps-csat.md):
  - NPS = %promotores (9–10) − %detratores (0–6). Mostra n e margem de erro (95%).
  - n < 10 → não publica o número, só a distribuição ("base pequena").
  - B2B: além do NPS por resposta, mostra o NPS por conta (média das notas da conta),
    para uma conta com muitos respondentes não pesar mais que as outras.
"""
import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

MIN_N = 10


def num(v, lo, hi):
    try:
        x = float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return None
    return x if lo <= x <= hi else None


def nps_de(notas):
    n = len(notas)
    if n == 0:
        return None
    p = sum(1 for x in notas if x >= 9) / n
    d = sum(1 for x in notas if x <= 6) / n
    nps = (p - d) * 100
    var = p + d - (p - d) ** 2
    me = 1.96 * math.sqrt(var / n) * 100 if n > 1 else None
    return {"n": n, "promotores_pct": round(p * 100, 1), "neutros_pct": round((1 - p - d) * 100, 1),
            "detratores_pct": round(d * 100, 1), "nps": round(nps, 1),
            "margem_95": round(me, 1) if me is not None else None, "base_pequena": n < MIN_N}


def ler(caminho):
    texto = Path(caminho).read_text(encoding="utf-8-sig")
    sep = ";" if texto.splitlines()[0].count(";") > texto.splitlines()[0].count(",") else ","
    return list(csv.DictReader(texto.splitlines(), delimiter=sep))


def calcular(linhas, chaves):
    grupos = defaultdict(list)
    for r in linhas:
        k = tuple((r.get(c) or "—").strip().lower() for c in chaves)
        grupos[k].append(r)
    saida = []
    for k, rs in sorted(grupos.items()):
        notas = [x for x in (num(r.get("nps"), 0, 10) for r in rs) if x is not None]
        csat = [x for x in (num(r.get("csat"), 1, 5) for r in rs) if x is not None]
        ces = [x for x in (num(r.get("ces"), 1, 7) for r in rs) if x is not None]
        enviados = sum(int(num(r.get("enviados"), 0, 10**6) or 0) for r in rs)
        por_conta = defaultdict(list)
        for r in rs:
            x = num(r.get("nps"), 0, 10)
            if x is not None:
                por_conta[(r.get("conta") or "").strip() or f"linha{id(r)}"].append(x)
        medias_conta = [sum(v) / len(v) for v in por_conta.values()]
        g = {"grupo": dict(zip(chaves, k)), "respostas": len(rs),
             "nps": nps_de(notas),
             "nps_por_conta": nps_de([round(m) for m in medias_conta]) if medias_conta else None,
             "contas": len(por_conta),
             "csat_top2_pct": round(100 * sum(1 for x in csat if x >= 4) / len(csat), 1) if csat else None,
             "csat_n": len(csat),
             "ces_facil_pct": round(100 * sum(1 for x in ces if x >= 5) / len(ces), 1) if ces else None,
             "ces_n": len(ces),
             "taxa_resposta_pct": round(100 * len(notas) / enviados, 1) if enviados else None}
        saida.append(g)
    return saida


def md(res, chaves):
    L = ["# NPS / CSAT / CES — relatório (rascunho)", "",
         f"Agrupado por: {', '.join(chaves)} · n mínimo para publicar o NPS: {MIN_N}", "",
         "| Grupo | Respostas | NPS (±95%) | Prom/Neu/Det % | NPS por conta (contas) | CSAT top-2 % (n) | CES fácil % (n) | Taxa de resposta |",
         "|---|---|---|---|---|---|---|---|"]
    for g in res:
        nome = " · ".join(f"{v}" for v in g["grupo"].values())
        n = g["nps"]
        if n is None:
            nps_txt, dist = "—", "—"
        else:
            dist = f"{n['promotores_pct']}/{n['neutros_pct']}/{n['detratores_pct']}"
            nps_txt = ("base pequena (n=%d)" % n["n"]) if n["base_pequena"] else \
                f"{n['nps']:+.0f} (±{n['margem_95']:.0f})"
        pc = g["nps_por_conta"]
        pc_txt = "—" if pc is None else (f"base pequena ({g['contas']})" if pc["base_pequena"]
                                         else f"{pc['nps']:+.0f} ({g['contas']})")
        cs = "—" if g["csat_top2_pct"] is None else f"{g['csat_top2_pct']} ({g['csat_n']})"
        ce = "—" if g["ces_facil_pct"] is None else f"{g['ces_facil_pct']} ({g['ces_n']})"
        tx = "—" if g["taxa_resposta_pct"] is None else f"{g['taxa_resposta_pct']}%"
        L.append(f"| {nome} | {g['respostas']} | {nps_txt} | {dist} | {pc_txt} | {cs} | {ce} | {tx} |")
    L += ["", "Leitura: com base pequena, leia os comentários e a distribuição, não o número. "
          "Todo detrator (0–6) gera retorno em até 2 dias úteis (fechamento do ciclo), por um humano."]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--por", default="momento,publico")
    ap.add_argument("--saida")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    chaves = [c.strip() for c in a.por.split(",") if c.strip()]
    try:
        res = calcular(ler(a.csv), chaves)
    except Exception as e:  # noqa: BLE001
        print(f"erro: {e}", file=sys.stderr)
        sys.exit(2)
    out = json.dumps(res, ensure_ascii=False, indent=2) if a.json else md(res, chaves)
    if a.saida:
        Path(a.saida).write_text(out, encoding="utf-8")
        print(f"gravado em {a.saida}")
    else:
        print(out)


if __name__ == "__main__":
    main()
