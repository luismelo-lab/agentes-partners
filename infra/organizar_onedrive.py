#!/usr/bin/env python3
"""Organiza os Downloads do Mac e a raiz do OneDrive (empresa) num layout padrão. O iCloud (pessoal) não é tocado.
Uso: organizar_onedrive.py simular | executar | desfazer <manifesto.json>
- Nada é apagado: duplicados e temporários vão para a Lixeira (~/.Trash/limpeza-2026-10-06/duplicados).
- Pastas de sistema e das rotinas não se movem (Área Partners · Agentes, Backups, Teams, Outlook, Attachments, Gravações).
- Cada movimento fica num manifesto JSON, que permite desfazer.
"""
import hashlib, json, os, re, shutil, sys, time, unicodedata
from pathlib import Path

H = Path.home()
OD = H / "Library/CloudStorage/OneDrive - SAVE COMPANY"
ICLOUD = H / "Library/Mobile Documents/com~apple~CloudDocs"
LIXO = H / ".Trash/limpeza-2026-10-06/duplicados"
LOG = H / "agentes-partners/logs"

LAYOUT = {
    "00": "00 · Entrada",
    "01": "01 · Comercial e Parceiros",
    "02": "02 · Clientes e Pareceres",
    "03": "03 · Produtos e Projetos",
    "04": "04 · Gestão, Metas e Estratégia",
    "05": "05 · Financeiro e Notas Fiscais",
    "06": "06 · Marketing e Apresentações",
    "07": "07 · Reuniões",
    "08": "08 · Modelos",
    "09": "09 · Pessoal",
    "99": "99 · Arquivo",
}
FIXOS = {"Área Partners · Agentes", "Backups", "Arquivos de Chat do Microsoft Teams", "Microsoft Teams Chat Files",
         "Microsoft Teams", "Microsoft Outlook", "Attachments", "Gravações", "Icon", "Icon\r", ".DS_Store"} | set(LAYOUT.values())

# regras por nome (a primeira que casar vence)
REGRAS = [
    (r"^~\$|^\.~lock", "LIXO"),                                   # arquivos temporários do Office
    (r"\bdisc\b|\bpdi\b|avalia[cç][aã]o de desempenho", "04P"),       # dados de pessoas: Gestão/Pessoas (confidencial)
    (r"oab|\bcnh\b|\brg\b|identidade|passaporte|claro|vivo|tim-fatura|minha-", "09"),
    (r"crédito internacional|credito-internacional|fundo de investimento internacional|maquila|recuperatax", "03"),
    (r"parecer|despacho|procura[cç][aã]o|ecac|lucro presumido|^documentos pdf$", "02"),
    (r"master|partner|parceir|lead|enriquecimento|negócios|negocios|distribuidora|campanha|consolidado", "01"),
    (r"nota|nfse|nf-e|fiscal|boleto|fatura|^\d{44}", "05"),
    (r"estrat|okr|meta|plano|resultado|reuniao-semanal|reunião|integracoes|evidência|evidencia|margem|agenda|pasta\.xlsx|comissionamento", "04"),
    (r"apresenta|logo|marca|\.pptx?$|uma-pagina", "06"),
    (r"whatsapp audio|grava|\.m4a$|\.mp3$|\.opus$", "07"),
    (r"modelo|template|\.dotx$", "08"),
    (r"^download|^demais arquivos$", "99"),
    (r"captura de tela|screenshot", "00"),
]


def destino(nome):
    n = nome.lower()
    for pad, d in REGRAS:
        if re.search(pad, n): return d
    return "00"


def materializado(p):
    try: return os.stat(p).st_blocks > 0
    except OSError: return False


def h(p):
    x = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): x.update(b)
    return x.hexdigest()


def plano():
    itens = []
    # 1) raiz do OneDrive (move pastas e arquivos soltos, exceto fixos)
    for p in sorted(OD.iterdir()):
        if unicodedata.normalize("NFC", p.name) in FIXOS or p.name.startswith("."): continue  # o Mac grava acentos em NFD
        itens.append((p, destino(p.name), "OneDrive"))
    # 2) Mac: Downloads, Mesa, Documentos (locais) e iCloud (exceto projetos de código)
    # Regra do Luis (06/10/2026): o OneDrive é da empresa; arquivos pessoais ficam no iCloud.
    # Por isso Mesa, Documentos (sincronizados com o iCloud) e o iCloud Drive NUNCA entram aqui.
    for base, rot in ((H / "Downloads", "Downloads"),):
        if not base.exists(): continue
        for p in sorted(base.iterdir()):
            if p.name.startswith(".") or p.name.startswith("Icon") or p.name in ("Desktop", "Documents", "Downloads"): continue
            if (p / "node_modules").exists() or any((p / x / "node_modules").exists() for x in (os.listdir(p) if p.is_dir() else [])):
                continue  # projeto de código: fica onde está
            itens.append((p, destino(p.name), rot))
    # 3) duplicados: zip com pasta extraída ao lado; mesmo conteúdo (só arquivos locais, sem baixar da nuvem)
    acoes, vistos = [], {}
    nomes = {p.name for p, _, _ in itens}
    for p, d, rot in itens:
        if d == "LIXO":
            acoes.append({"de": str(p), "para": str(LIXO / rot / p.name), "motivo": "temporário do Office"}); continue
        if p.suffix.lower() == ".zip" and p.stem in nomes:
            acoes.append({"de": str(p), "para": str(LIXO / rot / p.name), "motivo": "zip já extraído na pasta ao lado"}); continue
        if p.is_file() and materializado(p):
            k = (p.stat().st_size, h(p))
            if k in vistos:
                acoes.append({"de": str(p), "para": str(LIXO / rot / p.name), "motivo": f"duplicado de {vistos[k]}"}); continue
            vistos[k] = str(p)
        alvo = OD / LAYOUT["04"] / "Pessoas (confidencial)" / p.name if d == "04P" else OD / LAYOUT[d] / p.name
        if rot != "OneDrive" and d == "00" and "captura" in p.name.lower(): alvo = OD / LAYOUT["00"] / "Capturas de tela" / p.name
        acoes.append({"de": str(p), "para": str(alvo), "motivo": f"{rot} → {LAYOUT['04'] + '/Pessoas (confidencial)' if d == '04P' else LAYOUT[d]}"})
    return acoes


def livre(alvo):
    a = Path(alvo); i = 2
    while a.exists():
        a = a.with_name(f"{Path(alvo).stem} ({i}){Path(alvo).suffix}"); i += 1
    return a


def executar(acoes):
    feito = []
    for v in LAYOUT.values(): (OD / v).mkdir(exist_ok=True)
    for a in acoes:
        de, para = Path(a["de"]), livre(a["para"])
        para.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(de), str(para)); feito.append({**a, "para": str(para)})
        except Exception as e:
            feito.append({**a, "erro": str(e)[:200]})
    f = LOG / f"organizacao-onedrive-{time.strftime('%Y%m%d-%H%M%S')}.json"
    json.dump(feito, open(f, "w"), ensure_ascii=False, indent=1)
    return feito, f


if __name__ == "__main__":
    cmd = (sys.argv[1:] or ["simular"])[0]
    if cmd == "desfazer":
        for a in reversed(json.load(open(sys.argv[2]))):
            if "erro" not in a and Path(a["para"]).exists(): shutil.move(a["para"], a["de"])
        print("desfeito"); sys.exit()
    A = plano()
    if cmd == "simular":
        por = {}
        for a in A: por.setdefault(a["motivo"].split(" → ")[-1] if "→" in a["motivo"] else "Lixeira (" + a["motivo"].split(" de ")[0] + ")", []).append(Path(a["de"]).name)
        for k in sorted(por): print(f"\n[{k}] {len(por[k])}\n  " + "\n  ".join(sorted(por[k])[:40]))
        print(f"\nTotal: {len(A)} itens")
    elif cmd == "executar":
        feito, f = executar(A)
        print(f"movidos: {sum(1 for a in feito if 'erro' not in a)} · erros: {sum(1 for a in feito if 'erro' in a)} · manifesto: {f}")
        for a in feito:
            if "erro" in a: print("ERRO", a["de"], a["erro"])
