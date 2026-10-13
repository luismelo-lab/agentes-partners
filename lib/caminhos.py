#!/usr/bin/env python3
"""Ponto único dos caminhos do OneDrive da Área Partners (todas as rotinas usam este arquivo).

Por quê: o OneDrive renomeia a pasta local quando é reconfigurado ("OneDrive-SAVECOMPANY 2", "... 2 2").
Em 30/09 as rotinas passaram a gravar numa pasta comum com o nome antigo, que não sincroniza.
Aqui a pasta é achada pela marca de sincronização do macOS (atributo com.apple.file-provider-domain-id),
então uma nova renomeação não quebra nada. Na nuvem (GitHub Actions), use a variável OD_BASE.

Uso: python3 caminhos.py            mostra a pasta ativa
     python3 caminhos.py area       imprime só o caminho da "Área Partners · Agentes"
     python3 caminhos.py backups    imprime só o caminho dos backups
     python3 caminhos.py produtos   pastas do Luis no padrão 00–99 (central, resultado, conselho, planejamento, areas, produtos, credito, maquila, programa, marca)
"""
import glob, os, subprocess, sys

PREFIXO = "OneDrive-SAVECOMPANY"
AREA = "Área Partners · Agentes"


def _sincroniza(d):
    r = subprocess.run(["xattr", d], capture_output=True, text=True)
    return "com.apple.file-provider-domain-id" in r.stdout


ATALHO = "~/Library/CloudStorage/OneDrive - SAVE COMPANY"  # atalho do app; ficou apontando para pasta morta (09/10), por isso só vale se a pasta sincronizar


def onedrive():
    if os.environ.get("OD_BASE"): return os.environ["OD_BASE"]
    at = os.path.expanduser(ATALHO)
    if os.path.islink(at) and os.path.isdir(at) and _sincroniza(os.path.realpath(at)):
        return at
    cs = [d for d in glob.glob(os.path.expanduser(f"~/Library/CloudStorage/{PREFIXO}*")) if os.path.isdir(d) and not os.path.islink(d) and _sincroniza(d)]
    if not cs:
        sys.exit("OneDrive da Save não encontrado sincronizando em ~/Library/CloudStorage (abra o app do OneDrive e confira a conta).")
    return max(cs, key=os.path.getmtime)  # se houver mais de uma, a mais recente


def area():
    return os.environ.get("OD_RAIZ") or os.path.join(onedrive(), AREA)


def backups():
    return os.path.join(onedrive(), "Backups", "agentes-partners")


# Padrão 00–99 (decisão do Luis, 13/10/2026): o que é do Luis fica nas pastas por área; as Centrais do time
# continuam juntas em "Área Partners · Agentes", que é a pasta compartilhada com cada uma.
G = "04 · Gestão, Metas e Estratégia"
LUIS = {
    "central": f"{G}/Central de Agentes",            # Demandas.xlsx, Pedidos, Pedidos aprovados, como pedir
    "resultado": f"{G}/Resultado semanal",
    "conselho": f"{G}/Conselho",
    "planejamento": f"{G}/Planejamento 2027",
    "areas": "01 · Comercial e Parceiros/Relatórios das áreas",
    "produtos": "03 · Produtos e Projetos",
    "credito": "03 · Produtos e Projetos/Crédito Internacional",
    "maquila": "03 · Produtos e Projetos/PROJETO MAQUILA - INTERNACIONALIZAÇÃO",
    "programa": "01 · Comercial e Parceiros/Programa de Parceiros",
    "marca": "06 · Marketing e Apresentações/Marca",
}
CENTRAIS = {"daniela": "Central Masters · Daniela", "jenifer": "Central BDR · Jenifer", "geovana": "Central Técnica · Geovana"}


def luis(chave):
    if os.environ.get("OD_BASE") is None and os.environ.get("OD_RAIZ"):  # nuvem com só a pasta da área: tudo do Luis fica dentro dela
        return os.path.join(area(), "Gestão · Luis", LUIS[chave].split("/")[-1])
    return os.path.join(onedrive(), LUIS[chave])


def pasta(pessoa):
    """Pasta da pessoa no OneDrive: as do time ficam na pasta compartilhada; a do Luis, em 04 · Gestão/Central de Agentes."""
    return luis("central") if pessoa == "luis" else os.path.join(area(), CENTRAIS[pessoa])


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    print(luis(c) if c in LUIS else {"area": area, "backups": backups}.get(c, onedrive)())
