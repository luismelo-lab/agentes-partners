#!/usr/bin/env python3
"""Lê as demandas que chegam pelo WhatsApp e junta as evidências para o agente responder.

Para cada conversa com mensagem de parceiro/cliente nas últimas N horas:
- prints e imagens (jpeg, png, webp) → OCR local (Vision do macOS, recuperador/scripts/ocr);
- PDF, Word e Excel → texto;
- CNPJs digitados ou lidos no print (com dígito verificador conferido) → Receita (base local) + HubSpot (download local);
- links de negócio do HubSpot → dados do card e resumo do parecer, se houver.
Áudios: transcritos localmente em português (whisper.cpp + ffmpeg, modelo em dados-publicos/whisper); nada sai do Mac.

Nada sai da máquina: os anexos vêm do armazenamento do Eazybe e ficam em celulas/<pessoa>/whatsapp/anexos
(pasta 700, 30 dias). CNPJ de cliente nunca vai para serviço externo.
Uso: python3 demandas_whatsapp.py --pessoa daniela [--horas 6]
"""
import argparse, glob, hashlib, json, os, re, sqlite3, subprocess, sys, time
from urllib.parse import unquote
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/.claude/skills/recuperador/scripts"))
from comum import AP, LINK, fonte_hubspot  # noqa: E402

TZ = timezone(timedelta(hours=-3))
DB = os.path.join(AP, "dados-publicos/receita/cnpj.sqlite")
RESUMOS = os.path.join(AP, "celulas/geovana/pareceres/resumos.json")
URL = re.compile(r"https?://\S+")
ANEXO = re.compile(r"https://f005\.backblazeb2\.com/file/eazybe-attachments/\S+")
DEAL = re.compile(r"hubspot\.com/\S*?(?:deal/|record/0-3/)(\d{6,})")
PESSOAL = re.compile(r"(?<![a-z])(cnh|rg|cpf|ctps|irpf)(?![a-z])|identidade|passaporte|holerite|contracheque|t[ií]tulo[_ -]?(de[_ -]?)?eleitor|carteira[_ -]?(de[_ -]?)?trabalho"
                     r"|comprovante[_ -]?(de[_ -]?)?(resid|endere)|resid[eê]ncia|certid[aã]o[_ -]?(de[_ -]?)?(nasc|casam|obito)|extrato[_ -]?(banc|de[_ -]?conta)|dados[_ -]?banc", re.I)  # validado pelo Jurídico 02/10
IMG, DOC, AUD = ("jpeg", "jpg", "png", "webp", "heic"), ("pdf", "docx", "xlsx", "doc", "txt"), ("mp3", "ogg", "opus", "m4a", "wav")


sys.path.insert(0, os.path.expanduser("~/agentes-partners/lib"))
import partners_dados as PD  # noqa: E402  fonte única: CNPJ e Receita
from cnpj import cnpjs_no_texto, normalizar_cnpj  # noqa: E402  CNPJ numérico e alfanumérico


def cnpjs(texto):
    return cnpjs_no_texto(texto)


receita = PD.receita


def _execucao(b):
    """Fase da execução no Bitrix (último download de lib/bitrix.py), para responder status de pós-venda."""
    try:
        import sys as _s; _s.path.insert(0, os.path.expanduser("~/agentes-partners/lib")); import bitrix
        X = bitrix.ultimo(); its = (X or {}).get("execucoes", {}).get(str(b or ""), [])
        return [f"{i['funil']}: {i['fase']} desde {i['desde']}" for i in its] or None
    except Exception:
        return None


def negocio(d, R):
    r = R.get(d["id"]) or {}
    return {"id": d["id"], "nome": d.get("nome"), "status": d.get("status"), "etapa": d.get("etapa"), "pipeline": d.get("pipeline"),
            "parceiro": d.get("parceiro") or d.get("parceiro_bruto"), "valor": d.get("valor"), "criado": (d.get("criado") or "")[:10],
            "fechado": (d.get("fechado") or "")[:10], "cnpj": (d.get("extras") or {}).get("cnpj"), "regime": (d.get("extras") or {}).get("regime"),
            "ultima_atividade": (d.get("extras") or {}).get("ultima_atividade"), "honorario_pct": d.get("hContr"),
            "card_bitrix": (f"https://save.bitrix24.com.br/crm/deal/details/{(d.get('extras') or {}).get('id_bitrix')}/" if (d.get("extras") or {}).get("id_bitrix") else None),
            "execucao_bitrix": _execucao((d.get("extras") or {}).get("id_bitrix")) if d.get("status") == "ganho" else None,
            "parecer_resumo": r.get("resumo"), "parecer_motivo": r.get("motivo"), "sinal_reanalise": r.get("sinal_reanalise"), "link": LINK.format(d["id"])}


WHISPER = "/opt/homebrew/bin/whisper-cli"
FFMPEG = "/opt/homebrew/bin/ffmpeg"
MODELO = os.path.join(AP, "dados-publicos/whisper/ggml-small-q5_1.bin")


def transcrever(arq):
    """Transcrição local em português (whisper.cpp): nada sai do Mac. Devolve "" se não houver transcritor."""
    if not (os.path.exists(WHISPER) and os.path.exists(FFMPEG) and os.path.exists(MODELO)): return ""
    wav = arq + ".wav"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", arq, "-ar", "16000", "-ac", "1", wav], capture_output=True, timeout=300)
    if not os.path.exists(wav): return ""
    r = subprocess.run([WHISPER, "-m", MODELO, "-l", "pt", "-nt", "-np", "-f", wav], capture_output=True, text=True, timeout=600)
    try: os.remove(wav)
    except OSError: pass
    return " ".join(l.strip() for l in r.stdout.splitlines() if l.strip()) if r.returncode == 0 else ""


def ler_anexo(url, pasta, cache):
    if url in cache: return cache[url]
    nome = url.rsplit("/", 1)[-1][:150]; ext = nome.rsplit(".", 1)[-1].lower() if "." in nome else ""
    info = {"arquivo": re.sub(r"^\d+_", "", nome), "tipo": "imagem" if ext in IMG else "audio" if ext in AUD else "documento" if ext in DOC else "outro", "texto": ""}
    if PESSOAL.search(unquote(nome)):
        info.update({"tipo": "documento pessoal", "texto": "", "nota": "documento pessoal: não lido (LGPD)"}); cache[url] = info; return info
    if info["tipo"] == "audio":
        dest = os.path.join(pasta, hashlib.sha1(url.encode()).hexdigest()[:12] + "." + ext)
        if subprocess.run(["curl", "-sS", "-L", "-f", "-m", "60", "-o", dest, url], capture_output=True).returncode == 0:
            info["texto"] = transcrever(dest); info["transcrito"] = bool(info["texto"])
        info["texto"] = (info["texto"] or "")[:4000]; cache[url] = info; return info
    if info["tipo"] in ("imagem", "documento"):
        dest = os.path.join(pasta, hashlib.sha1(url.encode()).hexdigest()[:12] + "." + ext)
        r = subprocess.run(["curl", "-sS", "-L", "-f", "-m", "60", "-o", dest, url], capture_output=True)
        if r.returncode == 0 and os.path.exists(dest):
            try:
                if info["tipo"] == "imagem":
                    if ext in ("webp", "heic"):  # o Vision lê melhor em PNG
                        png = dest + ".png"
                        conv = ["sips", "-s", "format", "png", dest, "--out", png] if sys.platform == "darwin" else ["convert", dest, png]
                        subprocess.run(conv, capture_output=True)
                        dest = png if os.path.exists(png) else dest
                    from pareceres import ocr
                    info["texto"] = ocr(dest)
                    if re.search(r"(carteira nacional de habilita|registro geral|documento de identidade|\bCPF\b.*\d{3}\.\d{3}\.\d{3}-\d{2})", info["texto"], re.I):
                        info.update({"tipo": "documento pessoal", "texto": "", "nota": "print de documento pessoal: não lido (LGPD)"})
                else:
                    from pareceres import texto
                    info["texto"] = texto(dest)
                if info["tipo"] == "documento" and re.search(r"(carteira nacional de habilita|registro geral|documento de identidade)", info["texto"][:3000], re.I):
                    info.update({"tipo": "documento pessoal", "texto": "", "nota": "documento pessoal: não lido (LGPD)"})
            except Exception as e:  # noqa: BLE001
                info["erro"] = str(e)[:120]
        else:
            info["erro"] = "não baixou"
    info["texto"] = (info["texto"] or "").strip()[:6000]
    cache[url] = info
    return info


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pessoa", required=True); ap.add_argument("--horas", type=float, default=6)
    a = ap.parse_args()
    base = os.path.join(AP, "celulas", a.pessoa, "whatsapp")
    caixas = sorted(glob.glob(os.path.join(base, "caixa-*.json")))
    if not caixas: sys.exit("Sem caixa: rode whatsapp_hubspot.py antes.")
    C = json.load(open(caixas[-1]))
    pasta = os.path.join(base, "anexos"); os.makedirs(pasta, exist_ok=True); os.chmod(pasta, 0o700)
    for f in glob.glob(os.path.join(pasta, "*")):
        if time.time() - os.path.getmtime(f) > 30 * 86400: os.remove(f)
    cpath = os.path.join(base, "anexos-cache.json"); cache = json.load(open(cpath)) if os.path.exists(cpath) else {}
    _, D = fonte_hubspot(); N = {d["id"]: d for d in D["negocios"]}
    por_raiz = {}
    for d in D["negocios"]:
        c = normalizar_cnpj((d.get("extras") or {}).get("cnpj"))
        if len(c) >= 8: por_raiz.setdefault(c.zfill(14)[:8], []).append(d)
    R = json.load(open(RESUMOS)) if os.path.exists(RESUMOS) else {}
    from comum import cfg_time, e_do_time
    cfg = cfg_time()
    limite = datetime.now(TZ) - timedelta(hours=a.horas)
    saida = []
    for conv in C:
        externas = []
        for m in conv["conversa"]:
            try: q = datetime.strptime(f"{datetime.now().year}/{m['quando']}", "%Y/%d/%m %H:%M").replace(tzinfo=TZ)
            except ValueError: continue
            if q >= limite and not e_do_time(m["de"], cfg): externas.append(m)
        if not externas: continue
        ev = {"chat": conv["chat"], "tipo": conv["tipo"], "master": conv.get("master"), "negocios_da_conversa": conv.get("negocios"),
              "mensagens": [{"de": m["de"], "quando": m["quando"], "texto": ANEXO.sub("[anexo]", m["texto"])[:1500]} for m in externas[-15:]],
              "anexos": [], "cnpjs": [], "links_negocio": [], "outros_links": []}
        todo_texto = ""
        for m in externas:
            todo_texto += "\n" + m["texto"]
            for u in ANEXO.findall(m["texto"]):
                an = ler_anexo(u, pasta, cache); ev["anexos"].append(an); todo_texto += "\n" + an.get("texto", "")
            for u in URL.findall(m["texto"]):
                if "eazybe-attachments" in u: continue
                if DEAL.search(u): ev["links_negocio"].append(DEAL.search(u).group(1))
                else: ev["outros_links"].append(u[:200])
        for c in cnpjs(todo_texto):
            hs = [negocio(d, R) for d in por_raiz.get(c[:8], [])]
            ev["cnpjs"].append({"cnpj": c, "receita": receita(c), "hubspot": sorted(hs, key=lambda x: x["criado"], reverse=True)[:8],
                                "no_hubspot": bool(hs), "parceiros_no_hubspot": sorted({h["parceiro"] or "sem parceiro" for h in hs})})
        ev["links_negocio"] = [negocio(N[i], R) for i in dict.fromkeys(ev["links_negocio"]) if i in N] + \
                              [{"id": i, "nao_encontrado_no_download": True} for i in dict.fromkeys(ev["links_negocio"]) if i not in N]
        ev["audios"] = sum(1 for x in ev["anexos"] if x["tipo"] == "audio" and not x.get("texto"))  # só os que não foram transcritos
        ev["audios_transcritos"] = sum(1 for x in ev["anexos"] if x["tipo"] == "audio" and x.get("texto"))
        saida.append(ev)
    json.dump(cache, open(cpath, "w"), ensure_ascii=False)
    out = os.path.join(base, f"demandas-{datetime.now(TZ):%Y-%m-%d-%Hh%M}.json")
    json.dump(saida, open(out, "w"), ensure_ascii=False, indent=1)
    n_img = sum(1 for e in saida for x in e["anexos"] if x["tipo"] == "imagem" and x.get("texto"))
    print(f"{len(saida)} conversas com mensagem externa nas últimas {a.horas:g}h · {sum(len(e['cnpjs']) for e in saida)} CNPJs · "
          f"{n_img} prints lidos · {sum(e['audios'] for e in saida)} áudios · {sum(len(e['links_negocio']) for e in saida)} links de negócio → {out}")


if __name__ == "__main__":
    main()
