#!/usr/bin/env python3
"""Sentinela das entregas (Luis, 26/10/2026). Duas rodadas do relatório de resultados (19 e 26/10) caíram por falha de
internet. O aviso foi para a caixa de saída do e-mail pausado, e ninguém viu. Este script confere, pelo dia e pela hora,
se cada entrega esperada existe. Ele refaz o que é mecânico (bin/partners) e lista o que precisa dos agentes, para a rotina
da Central refazer.

  python3 infra/entregas_esperadas.py              lista o que falta hoje e grava registro/entregas-faltando.json
  python3 infra/entregas_esperadas.py --reparar    também roda as etapas mecânicas que faltam (uma tentativa por etapa por dia)
"""
import glob, json, os, subprocess, sys
from datetime import date, datetime

AP = os.path.expanduser("~/agentes-partners"); sys.path.insert(0, os.path.join(AP, "lib"))
import caminhos

HOJE = date.today(); AGORA = datetime.now(); DIA = HOJE.weekday()  # 0 = segunda
H = HOJE.isoformat()
REL = caminhos.luis("areas"); CENTRAL = caminhos.luis("central"); RES = caminhos.luis("resultado")
SAIDA = os.path.join(CENTRAL, "Caixa de saída (e-mail pausado)")
REG = os.path.join(AP, "registro")

# (id, nome, dias, a partir de que hora, como conferir, tipo, como refazer)
# tipo "script": bin/partners <etapa>; tipo "ia": a Central lê ~/.claude/scheduled-tasks/<rotina>/SKILL.md e executa
ESPERADAS = [
    ("dados-bi", "Dados-BI do dia", range(0, 5), 9, lambda: glob.glob(os.path.join(REL, f"Dados-BI-{H}.xlsx")), "script", ["dados-bi", "onedrive"]),
    ("plano", "Planos do dia", range(0, 5), 9, lambda: glob.glob(os.path.join(SAIDA, f"Plano-do-dia-Luis-{H}.xlsx")) or glob.glob(os.path.join(AP, "departamentos/operacao/Luis", f"Plano-do-dia-Luis-{H}.xlsx")), "ia", "operacao-areas"),
    ("portal", "Dados do painel", range(0, 5), 9, lambda: [f for f in [os.path.join(AP, "portal/dados.json")] if os.path.exists(f) and date.fromtimestamp(os.path.getmtime(f)) == HOJE], "script", ["portal"]),
    ("areas", "Relatórios semanais das áreas", [0], 9, lambda: glob.glob(os.path.join(REL, f"Conferencia-Repasses-{H}.xlsx")), "script", ["areas", "onedrive"]),
    ("resultados", "Relatório semanal de resultados", [0], 8, lambda: glob.glob(os.path.join(RES, f"Resultado-Semanal-{H}.pptx")), "ia", "relatorio-semanal-resultados"),
    ("conselho", "Ata do Conselho", [0], 10, lambda: glob.glob(os.path.join(AP, "conselho/atas", f"{H}-reuniao-semanal.md")), "ia", "conselho-reuniao-semanal"),
    ("recuperador", "Lote do Recuperador", [0], 10, lambda: glob.glob(os.path.join(caminhos.pasta("geovana"), f"Fila-Recuperador-{H}.xlsx")), "ia", "recuperador-lote-semanal"),
    ("radar", "Radar de mercado", [4], 10, lambda: glob.glob(os.path.join(CENTRAL, "Radar de mercado", f"radar-{H}.md")), "ia", "radar-mercado"),
    ("jornal", "Jornal diário", range(0, 5), 9, lambda: glob.glob(os.path.join(CENTRAL, "Jornal", f"Jornal-{H}.*")), "ia", "jornal-diario"),
]


def faltando():
    out = []
    for i, nome, dias, hora, existe, tipo, refazer in ESPERADAS:
        if DIA in dias and AGORA.hour >= hora and not existe():
            out.append({"id": i, "nome": nome, "tipo": tipo, "refazer": refazer, "desde": f"{hora}h"})
    return out


def reparar(itens):
    for it in itens:
        if it["tipo"] != "script": continue
        marca = os.path.join(AP, "logs", f".reparo-{it['id']}-{H}")
        if os.path.exists(marca): it["reparo"] = "já tentado hoje"; continue
        open(marca, "w").close()
        ok = all(subprocess.run([os.path.join(AP, "bin/partners"), etapa], capture_output=True).returncode == 0 for etapa in it["refazer"])
        it["reparo"] = "refeito" if ok else "falhou de novo"


if __name__ == "__main__":
    f = faltando()
    if "--reparar" in sys.argv:
        reparar(f)
        tentativas = {x["id"]: x.get("reparo") for x in f}
        f = faltando()  # confere de novo depois do reparo
        for x in f: x["reparo"] = tentativas.get(x["id"], "")
    falhas = []
    alertas = os.path.join(AP, "logs", "ALERTAS-PENDENTES.txt")
    if os.path.exists(alertas):
        falhas = [l.strip() for l in open(alertas, errors="ignore") if l.startswith(H)]
    json.dump({"data": H, "hora": AGORA.strftime("%H:%M"), "faltando": f, "falhas_hoje": falhas[-10:]},
              open(os.path.join(REG, "entregas-faltando.json"), "w"), ensure_ascii=False, indent=1)
    for x in f: print(f"FALTA {x['id']:<12} {x['nome']} ({x['tipo']}: {x['refazer']}) {x.get('reparo') or ''}")
    print(f"{len(f)} entrega(s) faltando · {len(falhas)} falha(s) de rotina hoje")
