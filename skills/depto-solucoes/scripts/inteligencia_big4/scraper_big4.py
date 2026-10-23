#!/usr/bin/env python3
"""Webscrap das páginas públicas das Big Four sobre entrega de serviços.

Só biblioteca padrão. Respeita robots.txt, limita a taxa e só lê páginas públicas.
Uso: python3 scraper_big4.py [--firma deloitte|pwc|ey|kpmg] [--profundidade 1] [--max 25]
Saída: corpus/<firma>.jsonl (uma página por linha) e corpus/indice.md
"""
import os, argparse, json, re, subprocess, time, urllib.robotparser
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag

AQUI = Path(__file__).parent
UA = "Mozilla/5.0 (compatible; SavePartnersResearch/1.0; pesquisa de mercado)"
ESPERA = 2.0

SEMENTES = {
    "deloitte": ["https://www.deloitte.com/br/pt/services/consulting.html",
                 "https://www.deloitte.com/br/pt/services/tax.html",
                 "https://www.deloitte.com/global/en/services/consulting.html",
                 "https://www.deloitte.com/global/en/what-we-do.html"],
    "pwc": ["https://www.pwc.com.br/pt/servicos.html",
            "https://www.pwc.com.br/pt/servicos/consultoria-de-negocios.html",
            "https://www.pwc.com/gx/en/services.html",
            "https://www.pwc.com/gx/en/services/consulting.html"],
    "ey": ["https://www.ey.com/pt_br/services",
           "https://www.ey.com/pt_br/services/consulting",
           "https://www.ey.com/en_gl/services",
           "https://www.ey.com/en_gl/services/consulting"],
    "kpmg": ["https://kpmg.com/br/pt/home/servicos.html",
             "https://kpmg.com/br/pt/home/services/tax.html",
             "https://kpmg.com/xx/en/what-we-do.html",
             "https://kpmg.com/xx/en/what-we-do/services.html"],
}
# links relevantes: como a firma entrega, vende e organiza o trabalho
CHAVES = re.compile(r"(servic|service|consult|tax|trib|case|client|cliente|stor|insight|operating|"
                    r"managed|transform|delivery|metodolog|approach|abordagem|industr|setor|"
                    r"sector|alliance|ecosystem|esg|reforma|reform)", re.I)

class Extrator(HTMLParser):
    def __init__(self):
        super().__init__(); self.titulo = ""; self.desc = ""; self.blocos = []; self.links = []
        self._tag = None; self._buf = []; self._skip = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "noscript", "svg", "nav", "footer", "header"): self._skip += 1
        if tag == "meta" and (a.get("name") in ("description", "og:description") or a.get("property") == "og:description"):
            self.desc = self.desc or a.get("content", "")
        if tag == "a" and a.get("href"): self.links.append(a["href"])
        if tag in ("h1", "h2", "h3", "p", "li", "title"): self._tag = tag; self._buf = []
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg", "nav", "footer", "header") and self._skip: self._skip -= 1
        if tag == self._tag:
            t = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if tag == "title": self.titulo = t
            elif t and not self._skip and len(t) > (3 if tag != "p" else 40): self.blocos.append((tag, t))
            self._tag = None
    def handle_data(self, d):
        if self._tag: self._buf.append(d)

_robots = {}
def permitido(url):
    host = "{0.scheme}://{0.netloc}".format(urlparse(url))
    if host not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            txt, _ = baixar(host + "/robots.txt") if False else (subprocess.run(["curl", "-sL", "--max-time", "15", "-A", UA, host + "/robots.txt"], capture_output=True).stdout.decode("utf-8", "replace"), 0)
            rp.parse(txt.splitlines()) if txt and "<html" not in txt[:200].lower() else rp.parse([])
        except Exception: rp = None
        _robots[host] = rp
    rp = _robots[host]
    return True if rp is None else rp.can_fetch(UA, url)

def baixar(url):
    """curl usa o chaveiro do macOS (o Python da Apple não traz os certificados)."""
    p = subprocess.run(["curl", "-sL", "--max-time", "25", "--max-filesize", "2000000", "-A", UA,
                        "-H", "Accept-Language: pt-BR,pt;q=0.9,en;q=0.8", "-w", "\n%{content_type}\n%{url_effective}", url],
                       capture_output=True)
    if p.returncode: raise RuntimeError(f"curl {p.returncode}")
    corpo, tipo, final = p.stdout.decode("utf-8", "replace").rsplit("\n", 2)
    return (corpo, final) if "html" in tipo else (None, url)

def rastrear(firma, prof, maximo):
    dominio_ok = {urlparse(u).netloc.split(".")[-2] for u in SEMENTES[firma]}
    fila = [(u, 0) for u in SEMENTES[firma]]; vistos = set(); paginas = []
    while fila and len(paginas) < maximo:
        url, nivel = fila.pop(0); url = urldefrag(url)[0]
        if url in vistos or not permitido(url): continue
        vistos.add(url); time.sleep(ESPERA)
        try: html, final = baixar(url)
        except Exception as e: print(f"  x {url} ({e})"); continue
        if not html: continue
        ex = Extrator(); ex.feed(html)
        if not ex.blocos: print(f"  - {url} sem texto (renderizada por JS)"); continue
        paginas.append({"firma": firma, "url": final, "nivel": nivel, "titulo": ex.titulo, "descricao": ex.desc,
                        "consultado_em": time.strftime("%Y-%m-%d"),
                        "blocos": [{"tag": t, "texto": x} for t, x in ex.blocos[:120]]})
        print(f"  + {final} ({len(ex.blocos)} blocos)")
        if nivel < prof:
            for l in ex.links:
                u = urldefrag(urljoin(final, l))[0]; p = urlparse(u)
                if p.scheme in ("http", "https") and p.netloc.split(".")[-2:-1] and p.netloc.split(".")[-2] in dominio_ok \
                   and CHAVES.search(p.path) and not re.search(r"\.(pdf|jpg|png|zip)$", p.path) and u not in vistos:
                    fila.append((u, nivel + 1))
    return paginas

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--firma", choices=list(SEMENTES)); ap.add_argument("--profundidade", type=int, default=1)
    ap.add_argument("--max", type=int, default=25); a = ap.parse_args()
    saida = Path(os.path.expanduser("~/agentes-partners/departamentos/solucoes/inteligencia-big-four/corpus")); saida.mkdir(parents=True, exist_ok=True)  # dados fora do repositório
    resumo = ["# Índice do corpus (webscrap)\n"]  # estava dentro do comentário acima: NameError na 1ª firma
    for f in ([a.firma] if a.firma else SEMENTES):
        print(f"[{f}]"); pgs = rastrear(f, a.profundidade, a.max)
        if pgs:  # rodada bloqueada ou sem rede não apaga o corpus anterior
            (saida / f"{f}.jsonl").write_text("\n".join(json.dumps(p, ensure_ascii=False) for p in pgs), encoding="utf-8")
        resumo.append(f"\n## {f.upper()} ({len(pgs)} páginas)")
        resumo += [f"- [{p['titulo'] or p['url']}]({p['url']}) · {p['consultado_em']}" for p in pgs]
    (saida / "indice.md").write_text("\n".join(resumo), encoding="utf-8")

if __name__ == "__main__":
    main()
