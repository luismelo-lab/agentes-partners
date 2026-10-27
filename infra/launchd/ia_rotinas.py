#!/usr/bin/env python3
"""Rotinas com IA no terminal do Mac (Luis, 27/10/2026): gera e liga os jobs do launchd que rodam `partners ia <rotina>`.

Os horários são os mesmos das tarefas agendadas do app do Claude. A rotina só passa para o terminal depois do teste
(`partners ia <rotina> --teste`) e, ao ligar aqui, a tarefa do app correspondente precisa ser desligada para não rodar
em dobro (docs/rotinas-no-terminal.md).

Uso:
  ia_rotinas.py gerar                 grava os .plist em infra/launchd/ia/ (não liga nada)
  ia_rotinas.py ligar <rotina>...     copia para ~/Library/LaunchAgents e liga (ou "todas")
  ia_rotinas.py desligar <rotina>...  desliga (ou "todas"); a tarefa do app pode ser religada
  ia_rotinas.py status                o que está ligado no launchd
"""
import os, plistlib, subprocess, sys

AP = os.path.expanduser("~/agentes-partners")
AQUI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ia")
LA = os.path.expanduser("~/Library/LaunchAgents")
PREFIXO = "com.savecompany.partners-ia."
UTEIS = [1, 2, 3, 4, 5]
# rotina → [(dias da semana, hora, minuto)]; 1 = segunda (launchd: 0 e 7 = domingo)
HORARIOS = {
    "relatorio-semanal-resultados": [([1], 6, 30)],
    "conselho-reuniao-semanal": [([1], 7, 30)],
    "operacao-areas": [(UTEIS, 7, 40)],
    "whatsapp-caixa-time": [(UTEIS, 8, 0), (UTEIS, 14, 0)],
    "central-agentes-email": [(UTEIS, h, 5) for h in (8, 10, 12, 14, 16, 18)],
    "recuperador-lote-semanal": [([1], 9, 0)],
    "radar-mercado": [([5], 7, 0)],
    "consolidacao-semanal": [([5], 16, 0)],
}


def plist(rotina):
    return {"Label": PREFIXO + rotina,
            "ProgramArguments": ["/bin/zsh", os.path.join(AP, "bin/partners"), "ia", rotina],
            "EnvironmentVariables": {"PATH": os.path.expanduser("~/.local/bin") + ":/Library/Frameworks/Python.framework/Versions/3.13/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"},
            "StartCalendarInterval": [{"Weekday": d, "Hour": h, "Minute": m} for dias, h, m in HORARIOS[rotina] for d in dias],
            "StandardOutPath": os.path.join(AP, "logs/launchd-ia.log"), "StandardErrorPath": os.path.join(AP, "logs/launchd-ia.log")}


def gerar():
    os.makedirs(AQUI, exist_ok=True)
    for r in HORARIOS:
        with open(os.path.join(AQUI, PREFIXO + r + ".plist"), "wb") as f:
            plistlib.dump(plist(r), f)
    print(f"{len(HORARIOS)} jobs gerados em {AQUI}")


def alvo(args):
    rs = list(HORARIOS) if args == ["todas"] else args
    ruins = [r for r in rs if r not in HORARIOS]
    if ruins or not rs: sys.exit(f"rotina desconhecida: {ruins or '(nenhuma)'} · válidas: {' '.join(HORARIOS)} ou todas")
    return rs


def ligar(rs):
    gerar(); os.makedirs(LA, exist_ok=True); uid = os.getuid()
    for r in rs:
        n = PREFIXO + r; dst = os.path.join(LA, n + ".plist")
        subprocess.run(["launchctl", "bootout", f"gui/{uid}/{n}"], capture_output=True)
        with open(os.path.join(AQUI, n + ".plist"), "rb") as f, open(dst, "wb") as g: g.write(f.read())
        ok = subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", dst]).returncode == 0
        print(("ligado: " if ok else "FALHOU: ") + r)


def desligar(rs):
    uid = os.getuid()
    for r in rs:
        n = PREFIXO + r
        subprocess.run(["launchctl", "bootout", f"gui/{uid}/{n}"], capture_output=True)
        p = os.path.join(LA, n + ".plist")
        if os.path.exists(p): os.remove(p)
        print("desligado: " + r)


def status():
    out = subprocess.run(["launchctl", "list"], capture_output=True, text=True).stdout
    ligados = {l.split()[-1][len(PREFIXO):] for l in out.splitlines() if PREFIXO in l}
    for r in HORARIOS: print(("terminal  " if r in ligados else "app       ") + r)


if __name__ == "__main__":
    a = sys.argv[1:] or ["status"]
    {"gerar": lambda: gerar(), "ligar": lambda: ligar(alvo(a[1:])), "desligar": lambda: desligar(alvo(a[1:])), "status": status}.get(a[0], lambda: sys.exit(__doc__))()
