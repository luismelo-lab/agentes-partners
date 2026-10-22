#!/usr/bin/env python3
"""Porteiro de pedidos: antes de executar, confere se o que o Luis pede já existe, é continuação de algo ou está travado.

Regra do Luis (22/10/2026): "não quero só que você execute; valide se o que estou pedindo está repetido e use tudo o que já
fizemos". Toda conversa roda este porteiro antes de começar um pedido novo (CLAUDE.md §1).

Fontes do índice (somente leitura):
  - documentos do repositório (docs/, departamentos/*.md, infra/*.md, rotinas/, skills/*/SKILL.md e references/), pelo título e cabeçalhos;
  - gabinete/SESSOES.md (uma seção por tema) e conselho/decisoes.md (decisões e pendências);
  - commits dos últimos 90 dias (todas as branches, inclusive origin/claude/* das sessões na nuvem);
  - arquivos publicados no OneDrive nas pastas de trabalho (nome e data);
  - catálogo de pedidos da Central (códigos DM, JB, GT, PI, SC, GE).

Uso:
  python3 infra/ja_existe.py "texto do pedido"        → repetição provável, relacionados e travas
  python3 infra/ja_existe.py "texto" --registrar novo|atualizacao|repetido --destino "<onde vai>"
"""
import argparse, glob, json, math, os, re, subprocess, sys, time, unicodedata
from collections import Counter
from datetime import datetime

AP = os.path.expanduser("~/agentes-partners")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OD = os.path.expanduser("~/Library/CloudStorage/OneDrive - SAVE COMPANY")
REG = os.path.join(AP, "registro", "pedidos-luis.jsonl")
PARE = set("""a o e de da do das dos em no na nos nas um uma uns umas para por com sem que se ao aos as os é ser foi são como mais
mas ou já também quero queria preciso pode podemos fazer faça crie criar gere gerar traga trazer veja ver isso isto esse essa este
esta nosso nossa nossos nossas meu minha sobre entre até após cada todo toda todos todas ele ela eles elas lhe seu sua
agora hoje vamos vai ter tem tenho temos está estão estamos muito pouco bem quando onde qual quais quem the and of""".split())


def norm(s):
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()


def toks(s):
    return [t for t in re.findall(r"[a-z0-9]{3,}", norm(s)) if t not in PARE]


def itens():
    out = []
    def add(tipo, titulo, onde, quando, texto):
        out.append({"tipo": tipo, "titulo": titulo.strip()[:140], "onde": onde, "quando": quando, "texto": texto})
    # documentos do repositório
    pats = ["docs/**/*.md", "infra/*.md", "rotinas/*.md", "skills/*/SKILL.md", "skills/*/references/*.md", "skills/*/scripts/**/README.md",
            "departamentos/**/*.md", "CLAUDE.md", "ESTADO.md", "DEPARTAMENTOS.md"]
    vistos = set()
    for p in pats:
        for f in glob.glob(os.path.join(REPO, p), recursive=True):
            if f in vistos or "/node_modules/" in f: continue
            vistos.add(f)
            try: t = open(f, errors="ignore").read(6000)
            except Exception: continue
            cab = " ".join(re.findall(r"^#{1,3} (.+)$", t, re.M)[:12])
            desc = " ".join(re.findall(r"^description: (.+)$", t, re.M)[:1])
            tit = (re.findall(r"^# (.+)$", t, re.M) or [os.path.basename(f)])[0]
            add("documento", tit, os.path.relpath(f, REPO), time.strftime("%d/%m/%Y", time.localtime(os.path.getmtime(f))), f"{tit} {cab} {desc} {t[:1500]}")
    # guia de sessões e decisões
    for nome, tipo in (("gabinete/SESSOES.md", "tema (SESSOES)"), ("conselho/decisoes.md", "decisão")):
        f = os.path.join(AP, nome)
        if not os.path.exists(f): continue
        t = open(f, errors="ignore").read()
        partes = re.split(r"^(?=## |\| D\d+ )", t, flags=re.M)
        for bloco in partes:
            tit = bloco.strip().splitlines()[0][:140] if bloco.strip() else ""
            if len(bloco) > 40: add(tipo, tit.lstrip("#| "), nome, "", bloco[:3000])
    # commits (90 dias, todas as branches)
    try:
        r = subprocess.run(["git", "-C", AP, "log", "--all", "--since=90 days ago", "--format=%h|%ad|%D|%s", "--date=short"], capture_output=True, text=True, timeout=30)
        for l in r.stdout.splitlines():
            h, d, refs, s = (l.split("|", 3) + ["", "", "", ""])[:4]
            add("commit", s, f"commit {h}" + (f" ({refs})" if refs else ""), d, s)
    except Exception: pass
    # OneDrive: entregas publicadas
    for pasta in ("01 · Comercial e Parceiros", "03 · Produtos e Projetos", "04 · Gestão, Metas e Estratégia", "06 · Marketing e Apresentações", "Área Partners · Agentes"):
        for f in glob.glob(os.path.join(OD, pasta, "**", "*.*"), recursive=True)[:4000]:
            if not f.lower().endswith((".docx", ".pptx", ".xlsx", ".pdf")) or "Caixa de saída" in f: continue
            n = os.path.basename(f)
            add("OneDrive", n, os.path.relpath(f, OD), time.strftime("%d/%m/%Y", time.localtime(os.path.getmtime(f))), n + " " + os.path.dirname(os.path.relpath(f, OD)))
    # catálogo da Central
    try:
        C = json.load(open(os.path.join(REPO, "skills/central-agentes/references/catalogo.json")))["tipos"]
        for k, v in C.items(): add("pedido da Central", f"{k} · {v['rotulo']}", "skills/central-agentes/references/catalogo.json", "", f"{v['rotulo']} {v['entrega']} {v['skill']}")
    except Exception: pass
    return out


def buscar(pedido, lim=12):
    I = itens(); q = toks(pedido)
    if not q: return [], I
    docs = [Counter(toks(i["titulo"] + " " + i["titulo"] + " " + i["texto"])) for i in I]
    df = Counter(t for d in docs for t in set(d)); N = len(docs)
    idf = {t: math.log((N + 1) / (df[t] + 1)) + 1 for t in set(q)}
    tot = sum(idf[t] for t in set(q))
    res = []
    for i, d in zip(I, docs):
        if not d: continue
        cob = sum(idf[t] for t in set(q) if t in d) / tot          # quanto do pedido o item cobre (peso pela raridade da palavra)
        if cob == 0: continue
        tit = set(toks(i["titulo"])); notit = sum(idf[t] for t in set(q) if t in tit) / tot
        score = 0.7 * cob + 0.3 * notit                              # cobrir no título vale mais
        res.append((round(score, 2), i))
    res.sort(key=lambda x: -x[0])
    # no máximo 3 por tipo, para documentos, temas e decisões aparecerem ao lado dos commits
    por, out = Counter(), []
    for s, i in res:
        if por[i["tipo"]] < 3: out.append((s, i)); por[i["tipo"]] += 1
        if len(out) >= lim: break
    return out, I


TRAVA = re.compile(r"pendente|aguard|trava|bloque|decis[aã]o do luis|a confirmar|sem resposta|falta", re.I)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("pedido"); ap.add_argument("--registrar", choices=["novo", "atualizacao", "repetido"])
    ap.add_argument("--destino", default=""); ap.add_argument("--json", action="store_true"); a = ap.parse_args()
    res, I = buscar(a.pedido)
    if a.json:
        print(json.dumps([{"score": s, **{k: v for k, v in i.items() if k != "texto"}} for s, i in res], ensure_ascii=False, indent=1)); sys.exit()
    rep = [(s, i) for s, i in res if s >= 0.6]; rel = [(s, i) for s, i in res if 0.35 <= s < 0.6]
    print(f"Porteiro de pedidos · {len(I)} itens no índice · pedido: {a.pedido!r}\n")
    print("REPETIÇÃO PROVÁVEL (continue ou atualize em vez de criar):" if rep else "Nenhuma repetição provável.")
    for s, i in rep: print(f"  {s:.2f}  [{i['tipo']}] {i['titulo']} · {i['onde']} {('· ' + i['quando']) if i['quando'] else ''}")
    if rel: print("\nRELACIONADO (reaproveite e conecte):")
    for s, i in rel: print(f"  {s:.2f}  [{i['tipo']}] {i['titulo']} · {i['onde']} {('· ' + i['quando']) if i['quando'] else ''}")
    tr = [(s, i) for s, i in res if s >= 0.35 and i["tipo"] in ("tema (SESSOES)", "decisão") and TRAVA.search(i["texto"])]
    if tr: print("\nPODE ESTAR TRAVADO POR (decisão ou pendência):")
    for s, i in tr[:4]: print(f"  [{i['tipo']}] {i['titulo']} · {i['onde']}")
    if a.registrar:
        os.makedirs(os.path.dirname(REG), exist_ok=True)
        with open(REG, "a") as f:
            f.write(json.dumps({"quando": datetime.now().isoformat(timespec="minutes"), "pedido": a.pedido, "classificacao": a.registrar,
                                "destino": a.destino, "repeticoes": [i["onde"] for _, i in rep][:5], "relacionados": [i["onde"] for _, i in rel][:5]}, ensure_ascii=False) + "\n")
        print(f"\nregistrado em {REG}")
