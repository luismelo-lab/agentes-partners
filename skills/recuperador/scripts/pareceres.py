#!/usr/bin/env python3
"""Pareceres do técnico (campos de arquivo do card no HubSpot) → texto + resumo estruturado, localmente.

Campos: parecer_complementar (Parecer Complementar RT), anexo_do_diagnostico, parecer_juridico.
Origem dos arquivos: links antigos do Bitrix24 (acesso direto) e arquivos do próprio HubSpot
(exigem o escopo 'files' no aplicativo privado; sem ele, ficam como "pendente de permissão").
Formato: detectado pelo conteúdo (Word .docx = "PK", PDF = "%PDF"), não pela extensão.

Privacidade: arquivos e textos ficam em ~/agentes-partners/celulas/geovana/pareceres (pasta 700).
Nada é enviado para fora. O resumo guarda só o necessário para a análise (motivo, teses, valores citados).

Uso:
  python3 pareceres.py --fila       # pareceres dos casos da fila do Recuperador
  python3 pareceres.py --ganhos     # pareceres dos negócios ganhos (padrão do que foi achado)
  python3 pareceres.py --todos --pendentes            # depois de liberar o escopo 'files' na Private App do HubSpot
  python3 pareceres.py --todos [--refazer-ilegiveis]   # toda a base; Excel, imagem e PDF digitalizado passam por OCR local
"""
import argparse, glob, io, json, os, re, subprocess, sys, time, zipfile
from urllib.parse import quote

H = os.path.expanduser
SRC = H("~/agentes-partners/departamentos/resultados/dados")
BASE = H("~/agentes-partners/celulas/geovana/pareceres")
ARQ = os.path.join(BASE, "arquivos"); TXT = os.path.join(BASE, "textos"); RES = os.path.join(BASE, "resumos.json")
FILA = H("~/agentes-partners/celulas/geovana/recuperador")
CAMPOS = {"parecer_rt": "Parecer Complementar RT", "anexo_diagnostico": "Anexo do Diagnóstico", "parecer_juridico": "Parecer Complementar Jurídico"}
CAMPOS_NOTA = {"anexo_nota": "Anexo de nota do negócio"}

MOTIVOS = [  # (categoria, padrões) — a primeira que casar vira o motivo principal
    ("Sem oportunidade identificada", r"n[ãa]o (foram|foi) (encontrad|identificad)|sem oportunidade|n[ãa]o h[áa] (cr[ée]dito|oportunidade)|inexist[êe]ncia de cr[ée]dito|resultado (nulo|zerado)"),
    ("Créditos já aproveitados/compensados", r"j[áa] (aproveitad|compensad|utilizad|recuperad)|cr[ée]ditos? (j[áa] )?escriturad|pedido de ressarcimento j[áa]"),
    ("Documentação insuficiente", r"(falta|aus[êe]ncia|aus[êe]ncia|n[ãa]o envi|pend[êe]ncia) de (document|arquiv|sped|efd|xml)|documenta[çc][ãa]o (incomplet|insuficient)|arquivos? (incomplet|corrompid|faltant)"),
    ("Prescrição / decadência", r"prescri|decad[êe]ncia|prazo (quinquenal|de 5 anos)"),
    ("Regime não permite", r"lucro presumido|regime cumulativo|simples nacional"),
    ("Monofásico / alíquota zero nas saídas", r"monof[áa]sic|substitui[çc][ãa]o tribut[áa]ria"),
    ("Ação judicial / já discutido", r"a[çc][ãa]o judicial|mandado de seguran[çc]a|j[áa] (discutid|questionad)"),
]
TESES = [("PIS/COFINS aquisições (alíquota zero)", r"al[ií]quota zero|aquisi[çc][õo]es"), ("Insumos", r"\binsumos?\b"), ("Exclusão do ICMS da base", r"exclus[ãa]o do icms"),
         ("ICMS-ST", r"icms[- /]?st|substitui[çc][ãa]o tribut"), ("Crédito presumido", r"cr[ée]dito presumido"), ("Previdenciário / verbas", r"verbas|previdenci|inss|rat\b|fap\b"),
         ("Selic IRPJ/CSLL", r"selic"), ("Monofásico", r"monof[áa]sic")]
VALOR = re.compile(r"R\$\s?([\d.]{1,15},\d{2})")


OCR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ocr")  # Vision do macOS, local (ocr.swift)


def ocr(caminho):
    if not os.path.exists(OCR) or sys.platform != "darwin":  # fora do Mac (nuvem): Tesseract, se instalado
        if caminho.lower().endswith(".pdf") and subprocess.run(["which", "pdftoppm"], capture_output=True).returncode == 0:
            base = caminho + ".pg"; subprocess.run(["pdftoppm", "-r", "200", "-png", caminho, base], capture_output=True)
            return "\n".join(ocr(p) for p in sorted(glob.glob(base + "*.png")))
        if subprocess.run(["which", "tesseract"], capture_output=True).returncode != 0: return ""
        r = subprocess.run(["tesseract", caminho, "-", "-l", "por"], capture_output=True, text=True, timeout=300)
        return r.stdout if r.returncode == 0 else ""
    r = subprocess.run([OCR, caminho], capture_output=True, text=True, timeout=300)
    return r.stdout if r.returncode == 0 else ""


def emf_texto(b):
    """Texto das tabelas coladas como imagem EMF no Word (Excel colado): registros EMR_EXTTEXTOUTW. Uma célula por linha."""
    import struct
    out, i = [], 0
    while i + 8 <= len(b):
        t, sz = struct.unpack_from("<II", b, i)
        if sz < 8: break
        if t == 84 and i + 52 <= len(b):
            try:
                n, off = struct.unpack_from("<II", b, i + 44)
                s = b[i + off:i + off + 2 * n].decode("utf-16-le").strip()
                if s: out.append(s)
            except Exception: pass
        i += sz
    return "\n".join(out)


def compactado(caminho):
    """RAR ou ZIP sem Office dentro (relatórios PER/DCOMP): extrai com bsdtar e junta o texto dos arquivos."""
    import tempfile
    d = tempfile.mkdtemp(); subprocess.run(["bsdtar", "-xf", caminho, "-C", d], capture_output=True, timeout=120)
    partes = []
    for raiz, _, fs in os.walk(d):
        for f in fs:
            try: partes.append(texto(os.path.join(raiz, f)))
            except Exception: pass
    subprocess.run(["rm", "-rf", d]); return "\n".join(p for p in partes if p)


def texto(caminho):
    """Word, PDF (com OCR se for digitalizado), Excel, imagem ou texto puro. Formato pelo conteúdo, não pela extensão."""
    b = open(caminho, "rb").read(8)
    if b.startswith(b"Rar!"): return compactado(caminho)
    if b.startswith(b"PK"):
        with zipfile.ZipFile(caminho) as z:
            nomes = z.namelist()
            if "word/document.xml" in nomes:
                xml = z.read("word/document.xml").decode("utf-8", "ignore")
                xml = re.sub(r"</w:p>", "\n", xml); xml = re.sub(r"<w:tab/>", "\t", xml)
                t = re.sub(r"<[^>]+>", "", xml)
                t = re.sub(r"&amp;", "&", re.sub(r"&lt;", "<", re.sub(r"&gt;", ">", t)))
                # tabelas coladas como imagem EMF (faturamento por ano, PER/DCOMP): o texto está dentro da imagem (Geovana, 15/10)
                emf = [emf_texto(z.read(n)) for n in nomes if n.startswith("word/media/") and n.lower().endswith(".emf")]
                emf = [x for x in emf if x.strip()]
                return t + ("\n\n[TABELAS DO PARECER]\n" + "\n\n".join(emf) if emf else "")
        if not any(n.startswith(("xl/", "word/", "ppt/")) for n in nomes): return compactado(caminho)  # .zip comum
        if any(n.startswith("xl/") for n in nomes):
            from openpyxl import load_workbook
            wb = load_workbook(caminho, read_only=True, data_only=True)
            return "\n".join("\t".join(str(c) for c in r if c is not None) for ws in wb.worksheets for r in ws.iter_rows(values_only=True) if any(c is not None for c in r))
        return ""
    if b.startswith(b"%PDF"):
        from pypdf import PdfReader
        t = "\n".join((p.extract_text() or "") for p in PdfReader(caminho).pages)
        return t if len(t.strip()) > 200 else (ocr(caminho) or t)  # digitalizado: OCR local
    if b[:3] == b"\xff\xd8\xff" or b.startswith(b"\x89PNG") or b[:4] in (b"GIF8", b"II*\x00", b"MM\x00*"):
        return ocr(caminho)
    try:
        t = open(caminho, "rb").read().decode("utf-8")
        return t if "\x00" not in t else ""
    except UnicodeDecodeError:
        return ""


ROTULOS = ["Perfil empresarial", "Teses de exclusões", "Teses de aquisições", "Teses previdenciárias", "Categoria da análise", "Gestão de passivo",
           "Situação da procuração", "Existência de PERDCOMP", "Registro de filiais", "Contribuinte diferenciado", "Período de apuração", "Data da análise"]
DESFECHO = [  # classificação da conclusão de cada tese (a ordem importa: causas específicas antes das genéricas)
    ("sem recolhimento – compensação integral", r"compensa[çc][ãa]o integral|j[áa] realiza (a )?compensa[çc][ãa]o|realizar a compensa[çc][ãa]o integral"),
    ("já aproveitado/ressarcido", r"j[áa] (possui )?(pedido|pedidos) de ressarcimento|j[áa] (realiza|faz) a? ?exclus|j[áa] (utiliz|aproveit|recuper)"),
    ("regime não permite", r"cumulativ|regime de apura[çc][ãa]o adotado|simples nacional|n[ãa]o permite a apropria|pertence ao lucro presumido"),
    ("sem aquisições elegíveis", r"n[ãa]o possui registro de (entradas|aquisi)"),
    ("sem recolhimento – alíquota zero", r"sujeita a al[íi]quota zero|n[ãa]o (h[áa]|possui) (pagamentos?|recolhimentos?)"),
    ("pouca movimentação (empresa nova ou SPED sem movimento)", r"in[íi]cio recente|sem movimento"),
    ("documentação/informação insuficiente", r"n[ãa]o foi poss[íi]vel|aus[êe]ncia de|falta de|sem acesso|n[ãa]o (enviad|disponibilizad)"),
    ("oportunidade identificada", r"(identificad|apurad|estimad)[oa]s? (valores|cr[ée]ditos) (de|no valor)|potencial de recupera|valor (estimado|apurado) de r\$"),
    ("abaixo do mínimo para aplicar a tese", r"insuficien|n[ãa]o se mostraram significativ|n[ãa]o apresenta oportunidade|n[ãa]o (alcan[çc]|atingi)|pouco expressiv|n[ãa]o (foram|s[ãa]o) (suficientes|significativ)|n[ãa]o (foram|foi) identificad|sem oportunidade|n[ãa]o (foram encontradas|possui) oportunidade|inviabiliz|impossibilita"),
]


def campos(t):
    L = [re.sub(r"\s+", " ", l).strip() for l in t.splitlines() if l.strip()]
    out = {}
    for l in L:
        for r in ROTULOS:
            if l.lower().startswith(r.lower()) and ":" in l:
                v = l.split(":", 1)[1].strip()
                if v: out[r] = v
    return out


def desfecho(txt):
    tl = (txt or "").lower()
    return next((d for d, p in DESFECHO if re.search(p, tl)), "não classificado") if txt else None


def resumo(t):
    c = campos(t)
    teses = {k: {"desfecho": desfecho(c.get(k)), "texto": (c.get(k) or "")[:400]} for k in ("Teses de aquisições", "Teses de exclusões", "Teses previdenciárias") if c.get(k)}
    # competências novas desde o fim do período analisado
    novas = analisados = fator = None
    m = re.findall(r"(\d{2})/(\d{2})/(\d{4})|(\d{2})/(\d{4})", c.get("Período de apuração", ""))
    if m:
        from datetime import date
        mm = lambda u: (int(u[1]), int(u[2])) if u[0] else (int(u[3]), int(u[4]))
        h = date.today(); fm, fa = mm(m[-1]); novas = max(0, (h.year - fa) * 12 + h.month - fm)
        if len(m) >= 2:
            im, ia = mm(m[0]); analisados = max(1, (fa - ia) * 12 + fm - im + 1)
            janela_hoje = min(60, (h.year - ia) * 12 + h.month - 1 - im + 1)   # até o mês anterior, limitada a 5 anos
            fator = round(janela_hoje / analisados, 2)
    aq = teses.get("Teses de aquisições", {}).get("desfecho")
    motivo = aq or next((v["desfecho"] for v in teses.values()), None)
    tl = t.lower(); modelo = "Avaliação Diagnóstica" if c else "outro formato"
    if "preven" in tl and "processual" in tl:
        modelo = "Relatório de Prevenção Processual"
        acoes = "sem ações judiciais tributárias" if re.search(r"n[ãa]o foram encontrados processos", tl) else "há ação judicial em alguma tese: conferir antes de reanalisar"
    else:
        acoes = None
    if not motivo and re.search(r"as oportunidades foram identificadas", tl): motivo = "oportunidade identificada (projeção)"
    valores = sorted({float(v.replace(".", "").replace(",", ".")) for v in VALOR.findall(t)}, reverse=True)[:5]
    return {"modelo": modelo, "motivo": motivo, "teses": teses, "acoes_judiciais": acoes,
            "passivo": c.get("Gestão de passivo"), "perdcomp": c.get("Existência de PERDCOMP"), "periodo_apuracao": c.get("Período de apuração"),
            "data_analise": c.get("Data da análise"), "competencias_novas_desde_analise": novas, "meses_analisados": analisados, "fator_base": fator, "perfil": (c.get("Perfil empresarial") or "")[:300],
            "maiores_valores_citados_rs": valores}


def baixar_bitrix(u, dest):
    r = subprocess.run(["curl", "-sS", "-L", "-f", "-m", "90", "-o", dest, quote(u, safe=":/?=&%")], capture_output=True)
    return r.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 0


_SEM_ESCOPO = []; _SEM_OCULTO = []
def anexos_notas(did):
    """Arquivos anexados às notas do negócio (pareceres, planilha analítica, relatório PER/DCOMP). IDs de arquivo do HubSpot."""
    sys.path.insert(0, H("~/.claude/skills/depto-resultados/scripts")); import hubspot_fonte as HF
    try: ns = [x["toObjectId"] for x in HF.call("GET", f"/crm/v4/objects/deals/{did}/associations/notes", tries=2).get("results", [])]
    except SystemExit: return []
    out = []
    for nid in ns[:20]:
        try: p = HF.call("GET", f"/crm/v3/objects/notes/{nid}?properties=hs_attachment_ids", tries=2).get("properties", {})
        except SystemExit: continue
        out += [f for f in (p.get("hs_attachment_ids") or "").split(";") if f.strip().isdigit()]
    return out


def baixar_hubspot(fid, dest, oculto=False):
    """Arquivo do próprio HubSpot: pede a URL assinada (escopo 'files') e baixa. None = sem permissão (403); False = falhou."""
    if _SEM_ESCOPO or (oculto and _SEM_OCULTO): return None
    sys.path.insert(0, H("~/.claude/skills/depto-resultados/scripts")); import hubspot_fonte as HF
    try: r = HF.call("GET", f"/files/v3/files/{fid}/signed-url", tries=3)
    except SystemExit as e:
        if "403" in str(e): (_SEM_OCULTO if oculto else _SEM_ESCOPO).append(1); return None  # anexo de nota: escopo files.ui_hidden.read
        return False
    u = (r or {}).get("url") if isinstance(r, dict) else None
    if not u: return False
    x = subprocess.run(["curl", "-sS", "-L", "-f", "-m", "120", "-o", dest, u], capture_output=True)
    return x.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 0


def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fila", action="store_true"); g.add_argument("--ganhos", action="store_true")
    g.add_argument("--todos", action="store_true", help="toda a base com parecer (look-alike e Revisor de Diagnóstico)")
    ap.add_argument("--notas", action="store_true", help="sem arquivo nos campos de parecer: busca os anexos das notas do negócio")
    ap.add_argument("--refazer", help="arquivo com IDs de negócios para ler de novo")
    ap.add_argument("--pendentes", action="store_true", help="só os pareceres que estavam no HubSpot aguardando o escopo 'files'")
    ap.add_argument("--refazer-ilegiveis", action="store_true", help="tenta de novo os marcados como ilegíveis (Excel, imagem, PDF digitalizado)")
    a = ap.parse_args()
    for p in (ARQ, TXT): os.makedirs(p, exist_ok=True)
    os.chmod(BASE, 0o700)
    N = {d["id"]: d for d in json.load(open(sorted(glob.glob(os.path.join(SRC, "hubspot-*.json")))[-1]))["negocios"]}
    if a.fila:
        from openpyxl import load_workbook
        f = sorted(glob.glob(os.path.join(FILA, "Fila-Recuperador-*.xlsx")))[-1]
        ws = load_workbook(f, read_only=True)["Fila"]; rows = list(ws.iter_rows(values_only=True)); iL = rows[0].index("link")
        alvo = [str(r[iL]).rstrip("/").rsplit("/", 1)[-1] for r in rows[1:] if r[iL]]  # linha sem link derrubava a leitura
    elif a.ganhos:
        alvo = [i for i, d in N.items() if d["status"] == "ganho"]
    else:
        alvo = list(N)
    if a.refazer:  # relê os pareceres destes negócios (ex.: depois de melhorar o leitor); um ID por linha
        ids = {l.strip() for l in open(a.refazer) if l.strip()}
        alvo = [i for i in alvo if i in ids]
        for i in alvo:
            for f in glob.glob(os.path.join(TXT, f"{i}_*.txt*")): os.remove(f)
    if a.pendentes:  # depois de liberar o escopo 'files': só os casos que ficaram "aguardando permissão"
        R0 = json.load(open(RES)) if os.path.exists(RES) else {}
        alvo = [i for i in alvo if (R0.get(i) or {}).get("pendentes")]
    if a.refazer_ilegiveis:
        for f in glob.glob(os.path.join(TXT, "*.ilegivel")):
            if os.path.getsize(f) == 0: os.remove(f)
    R = json.load(open(RES)) if os.path.exists(RES) else {}
    cont = {"baixados": 0, "ja_tinha": 0, "pendente_permissao_hubspot": 0, "falhou": 0, "sem_parecer": 0, "ilegivel": 0}
    for n, did in enumerate(alvo, 1):
        d = N.get(did)
        if not d: continue
        itens = [(k, u.strip()) for k in CAMPOS for u in (d["extras"].get(k) or "").split(";") if u.strip()]
        if not itens and a.notas: itens = [("anexo_nota", f) for f in anexos_notas(did)]  # parecer anexado em nota (Luis, 16/10)
        if not itens: cont["sem_parecer"] += 1; continue
        textos, pend = [], []
        for i, (k, u) in enumerate(itens):
            dest = os.path.join(ARQ, f"{did}_{k}_{i}.bin"); txtp = os.path.join(TXT, f"{did}_{k}_{i}.txt")
            if os.path.exists(txtp + ".ilegivel"): cont["ilegivel"] += 1; continue  # marcador vazio = ainda sem leitor para o formato
            if os.path.exists(txtp):
                cont["ja_tinha"] += 1; textos.append((k, open(txtp).read())); continue
            if k == "anexo_nota":
                ok = baixar_hubspot(u, dest, oculto=True)
                if ok is None: pend.append("Anexo de nota"); cont["pendente_permissao_hubspot"] += 1; continue
                if not ok: cont["falhou"] += 1; continue
            elif u.isdigit():  # arquivo no HubSpot: precisa do escopo 'files' (sem ele, fica pendente e o administrador do HubSpot (TI) libera na Private App)
                ok = baixar_hubspot(u, dest)
                if ok is None: pend.append(CAMPOS[k]); cont["pendente_permissao_hubspot"] += 1; continue
                if not ok: cont["falhou"] += 1; continue
            elif "bitrix" not in u: continue
            elif not baixar_bitrix(u, dest): cont["falhou"] += 1; continue
            try: t = texto(dest)
            except Exception: t = ""
            os.remove(dest)  # guarda só o texto: o original continua no card
            if not t.strip(): cont["ilegivel"] += 1; open(txtp + ".ilegivel", "w").close(); continue
            open(txtp, "w").write(t); cont["baixados"] += 1; textos.append((k, t)); time.sleep(0.3)
        if textos:
            rt = next((t for k, t in textos if k == "parecer_rt"), None) or textos[0][1]
            s = resumo("\n".join(t for _, t in textos)); s["fontes"] = [CAMPOS.get(k) or CAMPOS_NOTA.get(k, k) for k, _ in textos]
            if not s.get("periodo_apuracao"):  # planilha analítica anexada: período pelas competências que aparecem nela
                ms = sorted({(int(y), int(m)) for m, y in re.findall(r"\b(0[1-9]|1[0-2])/(20[12]\d)\b", "\n".join(t for _, t in textos))}
                            | {(int(y), int(m)) for y, m in re.findall(r"\b(20[12]\d)-(0[1-9]|1[0-2])-\d{2}", "\n".join(t for _, t in textos))})
                if len(ms) >= 3: s["periodo_apuracao"] = f"{ms[0][1]:02d}/{ms[0][0]} a {ms[-1][1]:02d}/{ms[-1][0]}"; s["periodo_fonte"] = "competências da planilha anexa"
            partes = [f"{k.replace('Teses de ', '').capitalize()}: {v['desfecho']}" for k, v in s["teses"].items()]
            if s.get("perdcomp"): partes.append(f"PER/DCOMP: {s['perdcomp']}")
            if s.get("acoes_judiciais"): partes.append(f"Prevenção processual: {s['acoes_judiciais']}")
            pv = (s.get("passivo") or "")
            if re.search(r"R\$\s?[\d.]+,\d{2}", pv) and not re.match(r"(a )?(empresa )?n[ãa]o possui", pv.lower()): partes.append("tem débitos em aberto (oportunidade de Gestão de Passivo)")
            nov = s.get("competencias_novas_desde_analise") or 0; fb = s.get("fator_base"); ma = s.get("meses_analisados")
            cresce = (fb is not None and fb >= 1.5) or (ma is not None and ma < 24 and nov >= 6)
            mot = s["motivo"]
            if mot == "documentação/informação insuficiente": sinal = "Reanalisar: pedir só o documento que faltou (desfecho mais reversível)"
            elif mot in ("abaixo do mínimo para aplicar a tese", "pouca movimentação (empresa nova ou SPED sem movimento)"):
                sinal = (f"Reanalisar: base cresceu {fb}x desde a análise (já descontada a decadência)" if cresce else
                         f"Não reanalisar ainda: base não cresceu o suficiente (fator {fb})" if fb is not None else None)
            elif mot == "já aproveitado/ressarcido": sinal = f"Recorrência: só os {nov} meses após o último período ressarcido, ou outra tese não coberta" if nov >= 6 else "Não reanalisar: já ressarcido e poucos meses novos"
            elif mot == "sem recolhimento – alíquota zero": sinal = "Mudar a tese para B: sem indébito, mas pode haver saldo credor ressarcível"
            elif mot in ("sem recolhimento – compensação integral", "sem aquisições elegíveis"): sinal = "Vetar: motivo estrutural, meses novos não mudam o resultado"
            elif mot == "regime não permite": sinal = "Não reanalisar, salvo mudança de regime (conferir ECF/DCTF do ano)"
            elif mot == "oportunidade identificada (projeção)": sinal = "Rotear ao comercial: o técnico achou oportunidade; a perda foi comercial"
            else: sinal = None
            if sinal: s["sinal_reanalise"] = sinal
            if fb is not None: partes.append(f"base atual/analisada = {fb}x ({ma} meses analisados)")
            s["resumo"] = " · ".join(partes) if partes else "parecer em outro formato: ler o texto"
            if pend: s["pendentes"] = pend
            R[did] = s
        elif pend:
            R[did] = {"resumo": f"parecer no HubSpot ({', '.join(pend)}): aguardando permissão de leitura de arquivos", "motivo": None, "pendentes": pend}
        if n % 50 == 0:
            json.dump(R, open(RES, "w"), ensure_ascii=False); print(f"  {n}/{len(alvo)} casos · {cont}", flush=True)
    json.dump(R, open(RES, "w"), ensure_ascii=False)
    from collections import Counter
    mot = Counter(R[i].get("motivo") or "não identificado" for i in alvo if i in R and not R[i].get("resumo", "").startswith("parecer no HubSpot"))
    print("Concluído:", cont, "\nMotivos:", dict(mot.most_common()))


if __name__ == "__main__":
    main()
