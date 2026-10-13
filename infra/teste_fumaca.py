#!/usr/bin/env python3
"""Teste de fumaça da estrutura de agentes (roadmap da revisão de 08/10, item 8): `partners teste`.

Confere, sem enviar nada nem gravar no OneDrive, o que as rotinas precisam para funcionar:
compilação de todos os scripts, pasta do OneDrive e destinos do padrão 00–99, marca.json, montagem de um e-mail
de teste, Outlook instalado, acesso de leitura ao HubSpot (sem mostrar o token), backup recente e skills em uso
iguais ao repositório. Sai com erro se algo crítico falhar. Uso: python3 infra/teste_fumaca.py [--rapido]
"""
import glob, os, subprocess, sys, time

AP = os.path.expanduser("~/agentes-partners"); SK = os.path.expanduser("~/.claude/skills")
sys.path.insert(0, os.path.join(AP, "lib")); sys.path.insert(0, os.path.join(SK, "depto-marketing/scripts"))
R = []  # (crítico?, ok?, nome, detalhe)


def checa(nome, critico=True):
    def dec(f):
        t = time.time()
        try: ok, det = f()
        except SystemExit as e: ok, det = False, f"encerrou: {str(e)[:160]}"
        except Exception as e: ok, det = False, f"{type(e).__name__}: {str(e)[:160]}"
        R.append((critico, ok, nome, f"{det} ({time.time() - t:.1f}s)"))
        return f
    return dec


@checa("Scripts compilam")
def _():
    fs = [f for pad in ("lib/*.py", "infra/*.py", "departamentos/*/scripts/*.py", "departamentos/produtos/*/scripts/*.py") for f in glob.glob(os.path.join(AP, pad))]
    fs += glob.glob(os.path.join(SK, "*/scripts/*.py"))
    erros = []
    for f in fs:
        try: compile(open(f, encoding="utf-8").read(), f, "exec")  # só checa; não grava .pyc
        except (SyntaxError, ValueError): erros.append(os.path.basename(f))
    return not erros, f"{len(fs)} arquivos" + (f"; com erro: {', '.join(erros)}" if erros else "")


@checa("OneDrive e destinos 00–99")
def _():
    import caminhos
    falta = [k for k in caminhos.LUIS if not os.path.isdir(caminhos.luis(k))] + [p for p in caminhos.CENTRAIS if not os.path.isdir(caminhos.pasta(p))]
    return not falta, caminhos.onedrive() + (f"; pastas que faltam: {', '.join(falta)}" if falta else "; todas as pastas existem")


@checa("Padrão de marca e e-mail de teste")
def _():
    import email_layout as L
    html = L.documento(L.cabecalho("Teste", "Teste de fumaça", ""), L.paragrafo("ok"), L.rodape("teste"))
    return "Save Co." in html and L.FONTE.startswith("'IBM Plex Sans'"), f"e-mail montado ({len(html)} bytes), sem envio"


@checa("Outlook instalado")
def _():
    r = subprocess.run(["mdfind", "kMDItemCFBundleIdentifier == 'com.microsoft.Outlook'"], capture_output=True, text=True, timeout=20)
    achado = [x for x in r.stdout.splitlines() if x.endswith(".app")] or [p for p in ("/Applications/Microsoft Outlook.app",) if os.path.exists(p)]
    return bool(achado), achado[0] if achado else "NÃO instalado: nenhum e-mail dos agentes sai (reinstale o Outlook clássico)"


@checa("HubSpot (leitura)")
def _():
    if "--rapido" in sys.argv: return True, "pulado (--rapido)"
    r = subprocess.run([sys.executable, os.path.join(SK, "depto-resultados/scripts/hubspot_fonte.py"), "--testar"], capture_output=True, text=True, timeout=120)
    return r.returncode == 0, (r.stdout or r.stderr).strip().splitlines()[-1][:160] if (r.stdout or r.stderr).strip() else f"código {r.returncode}"


@checa("Backup recente", critico=False)
def _():
    import caminhos
    fs = sorted(glob.glob(os.path.join(caminhos.backups(), "agentes-partners-*.tar.gz")), key=os.path.getmtime)
    if not fs: return False, "nenhum backup .tar.gz no OneDrive"
    h = (time.time() - os.path.getmtime(fs[-1])) / 3600
    return h < 30, f"último: {os.path.basename(fs[-1])}, há {h:.0f} h" + ("" if h < 30 else " (o das 19h30 falhou: Acesso Total ao Disco?)")


@checa("Skills em uso = repositório", critico=False)
def _():
    r = subprocess.run(["diff", "-rq", os.path.join(AP, "skills"), SK, "-x", "__pycache__", "-x", "node_modules", "-x", "ocr"], capture_output=True, text=True)
    dif = [l for l in r.stdout.splitlines() if l.startswith("Files ")]
    return not dif, "iguais" if not dif else f"{len(dif)} arquivo(s) diferentes: rode infra/repo-sincronizar.sh para ver"


if __name__ == "__main__":
    for crit, ok, nome, det in R:
        print(f"{'ok   ' if ok else 'FALHA' if crit else 'aviso'}  {nome}: {det}")
    falhas = [n for c, ok, n, _ in R if c and not ok]
    print("\n" + ("Tudo certo." if not falhas else f"{len(falhas)} falha(s) crítica(s): {', '.join(falhas)}"))
    sys.exit(1 if falhas else 0)
