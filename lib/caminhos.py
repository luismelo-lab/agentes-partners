#!/usr/bin/env python3
"""Ponto único dos caminhos do OneDrive da Área Partners (todas as rotinas usam este arquivo).

Por quê: o OneDrive renomeia a pasta local quando é reconfigurado ("OneDrive-SAVECOMPANY 2", "... 2 2").
Em 30/09 as rotinas passaram a gravar numa pasta comum com o nome antigo, que não sincroniza.
Aqui a pasta é achada pela marca de sincronização do macOS (atributo com.apple.file-provider-domain-id),
então uma nova renomeação não quebra nada. Na nuvem (GitHub Actions), use a variável OD_BASE.

Uso: python3 caminhos.py            mostra a pasta ativa
     python3 caminhos.py area       imprime só o caminho da "Área Partners · Agentes"
     python3 caminhos.py backups    imprime só o caminho dos backups
"""
import glob, os, subprocess, sys

PREFIXO = "OneDrive-SAVECOMPANY"
AREA = "Área Partners · Agentes"


def _sincroniza(d):
    r = subprocess.run(["xattr", d], capture_output=True, text=True)
    return "com.apple.file-provider-domain-id" in r.stdout


def onedrive():
    if os.environ.get("OD_BASE"): return os.environ["OD_BASE"]
    cs = [d for d in glob.glob(os.path.expanduser(f"~/Library/CloudStorage/{PREFIXO}*")) if os.path.isdir(d) and not os.path.islink(d) and _sincroniza(d)]
    if not cs:
        sys.exit("OneDrive da Save não encontrado sincronizando em ~/Library/CloudStorage (abra o app do OneDrive e confira a conta).")
    return max(cs, key=os.path.getmtime)  # se houver mais de uma, a mais recente


def area():
    return os.environ.get("OD_RAIZ") or os.path.join(onedrive(), AREA)


def backups():
    return os.path.join(onedrive(), "Backups", "agentes-partners")


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    print({"area": area, "backups": backups}.get(c, onedrive)())
