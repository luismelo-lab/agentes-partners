#!/usr/bin/env python3
"""Organiza os Downloads do Mac e a raiz do OneDrive (empresa) num layout padrão. O iCloud (pessoal) não é tocado.
Uso: organizar_onedrive.py simular | executar | desfazer <manifesto.json>
     organizar_onedrive.py duplicados [executar]   (sem "executar" só mostra o que sairia)
- Nada é apagado: duplicados e temporários vão para a Lixeira (~/.Trash/limpeza-2026-10-06/duplicados).
- Pastas de sistema e das rotinas não se movem (Área Partners · Agentes, Backups, Teams, Outlook, Attachments, Gravações).
- Cada movimento fica num manifesto JSON, que permite desfazer.
"""
import hashlib, json, os, re, shutil, subprocess, sys, time, unicodedata
from pathlib import Path

H = Path.home()
sys.path.insert(0, str(H / "agentes-partners/lib")); import caminhos  # noqa: E402
OD = Path(caminhos.onedrive())  # pasta que sincroniza de verdade (o atalho fixo apontou para uma pasta morta em 09/10)
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


# ---- duplicados: só arquivos já baixados são comparados por conteúdo; os que estão só na nuvem, por nome + tamanho
PROTEGIDAS = {"Área Partners · Agentes", "Backups", "Arquivos de Chat do Microsoft Teams", "Microsoft Teams Chat Files",
              "Attachments", "Gravações", "Whiteboards"}  # publicador, backup e apps (links do Teams quebrariam)
EXTRAS = [H / "Library/CloudStorage/OneDrive-SAVECOMPANY 2 2", H / "Downloads"]  # pasta morta do atalho antigo e Downloads


def _nfc(x): return unicodedata.normalize("NFC", x)


def _topo(p):
    try: return _nfc(Path(p).relative_to(OD).parts[0])
    except ValueError: return None  # fora do OneDrive


def _prio(p):
    t, r = _topo(p), Path(p)
    if t is None: return 9
    if t in PROTEGIDAS: return 0
    if len(r.relative_to(OD).parts) == 1: return 3  # solto na raiz
    return {"00": 2, "99": 4}.get(t[:2], 1 if t[:2].isdigit() else 3)


def _ordem(p, t):  # quem fica: pasta mais organizada; depois o nome sem " (2)"; depois o caminho mais curto; depois o mais antigo
    return (_prio(p), bool(re.search(r" \(\d+\)(\.\w+)?$", Path(p).name)), len(str(p)), t)


def _impressao(d):  # conteúdo de uma pasta inteira (inclui ocultos); None se algum arquivo estiver só na nuvem
    itens = []
    for dp, dn, fn in os.walk(d):
        dn[:] = [x for x in dn if x != ".git"]  # metadado do git não conta
        for f in fn:
            if f in (".DS_Store", "Icon\r"): continue
            q = os.path.join(dp, f)
            if not materializado(q) and os.path.getsize(q): return None
            itens.append((os.path.relpath(q, d), os.path.getsize(q), h(q) if os.path.getsize(q) else ""))
    return hashlib.sha256(json.dumps(sorted(itens)).encode()).hexdigest() if itens else "vazia"


def duplicados():
    acoes, fora = [], set()
    # 1) pastas irmãs idênticas ("x", "x 3", "x (1)"...) e cópias vazias "x (1)"
    for dp, dn, _ in os.walk(OD):
        if Path(dp) == OD: dn[:] = [d for d in dn if _nfc(d) not in PROTEGIDAS and not d.startswith(".")]
        dn[:] = [d for d in dn if not d.startswith(".")]
        grupos = {}
        for d in dn:
            base = re.sub(r"( \d+)?( \(\d+\))?$", "", d)
            if base != d or any(re.sub(r"( \d+)?( \(\d+\))?$", "", o) == d and o != d for o in dn): grupos.setdefault(base, []).append(d)
        for base, ds in grupos.items():
            imp = {d: _impressao(os.path.join(dp, d)) for d in ds}
            for d, i in imp.items():
                if i == "vazia":
                    acoes.append({"sai": os.path.join(dp, d), "fica": None, "motivo": "pasta-cópia vazia"}); fora.add(d)
            iguais = {}
            for d, i in imp.items():
                if i and i != "vazia" and d not in fora: iguais.setdefault(i, []).append(d)
            for ds2 in iguais.values():
                ds2.sort(key=lambda d: (bool(re.search(r"( \d+)?( \(\d+\))$|( \d+)$", d)), len(d)))
                for d in ds2[1:]:
                    acoes.append({"sai": os.path.join(dp, d), "fica": os.path.join(dp, ds2[0]), "motivo": "pasta idêntica"})
    saem = [a["sai"] for a in acoes]
    # 2) arquivos
    g = {}
    for raiz in [OD] + [e for e in EXTRAS if e.exists()]:
        for dp, dn, fn in os.walk(raiz):
            if Path(dp) == OD: dn[:] = [d for d in dn if _nfc(d) != "Backups"]
            dn[:] = [d for d in dn if not d.startswith(".") and not any(os.path.join(dp, d).startswith(s) for s in saem)]
            if any((Path(x) / ".git").exists() for x in [dp, *map(str, Path(dp).parents)] if str(x).startswith(str(raiz)) and Path(x) != raiz):
                continue  # projeto de código: sai a pasta inteira ou nada
            for f in fn:
                if f.startswith(".") or f.startswith("Icon"): continue
                p = os.path.join(dp, f); st = os.stat(p)
                if not st.st_size: continue
                nome = _nfc(re.sub(r" \(\d+\)(?=\.\w+$)", "", f)).lower()
                k = ("h", st.st_size, h(p)) if st.st_blocks else ("n", st.st_size, nome)
                g.setdefault(k, []).append((p, st.st_mtime))
    for k, v in g.items():
        if len(v) < 2: continue
        v.sort(key=lambda x: _ordem(*x)); fica = v[0][0]
        for p, _ in v[1:]:
            if _prio(p) == 0: continue  # nunca tira nada das pastas protegidas
            acoes.append({"sai": p, "fica": fica, "motivo": "mesmo conteúdo" if k[0] == "h" else "mesmo nome e tamanho"})
    # 3) o que sobrar na pasta morta do atalho antigo vai para a Entrada do OneDrive
    morta = EXTRAS[0]
    if morta.exists():
        ja = {a["sai"] for a in acoes}
        for dp, _, fn in os.walk(morta):
            for f in fn:
                p = os.path.join(dp, f)
                if not f.startswith(".") and p not in ja:
                    acoes.append({"sai": p, "fica": str(livre(OD / LAYOUT["00"] / f)), "motivo": "mover para a Entrada", "mover": True})
    return acoes


def executar_duplicados(acoes):
    feito, f = [], LOG / f"duplicados-onedrive-{time.strftime('%Y%m%d-%H%M%S')}.json"
    for a in acoes:
        try:
            if a.get("mover"): shutil.move(a["sai"], a["fica"])
            else: subprocess.run(["/usr/bin/trash", a["sai"]], check=True, capture_output=True, timeout=300)  # Lixeira: recuperável
            feito.append(a)
        except Exception as e:  # inclui o tempo esgotado quando o OneDrive está com fila grande
            feito.append({**a, "erro": str(e)[:200]})
        json.dump(feito, open(f, "w"), ensure_ascii=False, indent=1)  # item a item: se parar no meio, o manifesto fica certo
    return feito, f


if __name__ == "__main__":
    cmd = (sys.argv[1:] or ["simular"])[0]
    if cmd == "duplicados":
        A = duplicados()
        if sys.argv[2:3] == ["executar"]:
            feito, f = executar_duplicados(A)
            print(f"feito: {sum(1 for a in feito if 'erro' not in a)} · erros: {sum(1 for a in feito if 'erro' in a)} · manifesto: {f}")
        else:
            for a in A: print(f"[{a['motivo']}] {a['sai'].replace(str(H), '~')}  →  fica: {(a['fica'] or '-').replace(str(H), '~')}")
            print(f"\nTotal: {len(A)} itens (nada foi feito; para executar: duplicados executar)")
        sys.exit()
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
