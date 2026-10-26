#!/usr/bin/env python3
"""Screenshots e checagens da tela "Gestão" da Central Partners (26/10/2026), desktop 1440×900 e celular 375×812.
Serve a pasta portal/ sozinho (servidor local numa porta livre) e usa a prévia (combinada.html + exemplo-dados.js, sem cliente).
Confere em cada tela: erro de console, erro de script e rolagem horizontal; testa o filtro "só fora da tolerância", o clique nos
cenários, a gaveta "Definir unidade" e a marcação de desvio (na prévia nada é gravado).
Com --real <pasta>, abre também uma cópia do index.html com os dados reais (dados.json + diretorio.json dessa pasta), só para
conferir erros e rolagem; não tira screenshot dos dados reais.
Uso: python3 portal/opcoes/capturar_gestao.py [--real portal]   → portal/opcoes/screenshots/gestao-<tela>-<desktop|celular>.png"""
import http.server, os, re, shutil, socketserver, sys, tempfile, threading
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__)); PORTAL = os.path.dirname(AQUI)
SAIDA = os.path.join(AQUI, "screenshots"); os.makedirs(SAIDA, exist_ok=True)
REAL = sys.argv[sys.argv.index("--real") + 1] if "--real" in sys.argv else ""
raiz = tempfile.mkdtemp(prefix="gestao-captura-")
shutil.copytree(AQUI, os.path.join(raiz, "opcoes"), ignore=shutil.ignore_patterns("screenshots", "__pycache__", "direcoes"))
if REAL:  # index.html no esqueleto mínimo do Artifact + dados reais (perfil completo)
    os.makedirs(os.path.join(raiz, "real"))
    for f in ("dados.json", "diretorio.json", "logo-save-fundo-claro.png", "logo-save-fundo-escuro.png"): shutil.copy(os.path.join(REAL if f.endswith(".json") else PORTAL, f), os.path.join(raiz, "real", f))
    open(os.path.join(raiz, "real", "index.html"), "w", encoding="utf-8").write('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'
        + open(os.path.join(PORTAL, "index.html"), encoding="utf-8").read() + "</body></html>")


class Quieto(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


srv = socketserver.TCPServer(("127.0.0.1", 0), lambda *a, **k: Quieto(*a, directory=raiz, **k)); porta = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{porta}"; PREVIA = BASE + "/opcoes/combinada.html"
TELAS = [  # nome, url, perfil, tema, página inteira, ação extra
    ("01-luis", PREVIA + "#gestao", "luis", "dark", True, None),
    ("02-luis-so-fora", PREVIA + "#gestao", "luis", "dark", True, "fora"),
    ("03-luis-cenario-conservador", PREVIA + "#gestao", "luis", "dark", False, "cenario"),
    ("04-luis-definir-unidade", PREVIA + "#gestao/unidade", "luis", "dark", False, None),
    ("05-luis-decisao", PREVIA + "#gestao/decisao/D30", "luis", "dark", False, None),
    ("06-luis-mesa", PREVIA + "#mesa", "luis", "dark", True, None),
    ("07-daniela-semaforo", PREVIA + "#gestao", "daniela", "dark", True, None),
    ("08-luis-claro", PREVIA + "#gestao", "luis", "light", True, None),
]
if REAL: TELAS.append(("real-luis", BASE + "/real/index.html#gestao", None, "dark", False, "real"))
erros = []
with sync_playwright() as pw:
    nav = pw.chromium.launch()
    for disp, vp, mob in (("desktop", {"width": 1440, "height": 900}, False), ("celular", {"width": 375, "height": 812}, True)):
        for nome, u, perfil, tema, inteira, extra in TELAS:
            ctx = nav.new_context(viewport=vp, device_scale_factor=2 if mob else 1, is_mobile=mob, has_touch=mob)
            ctx.add_init_script(f"try{{localStorage.setItem('sou','{perfil or ''}');localStorage.setItem('tema','{tema}')}}catch(e){{}}")
            pg = ctx.new_page()
            pg.on("console", lambda m, n=nome, d=disp: m.type == "error" and erros.append(f"{n}/{d}: console: {m.text}"))
            pg.on("pageerror", lambda e, n=nome, d=disp: erros.append(f"{n}/{d}: script: {e}"))
            pg.goto(u); pg.wait_for_timeout(900)
            if extra == "fora": pg.click('[data-g-fora="1"]'); pg.wait_for_timeout(300)
            if extra == "cenario": pg.click('[data-cen="conservador"]'); pg.wait_for_timeout(300); pg.locator("#premissas").scroll_into_view_if_needed()
            if extra == "real":
                if "Semáforo" not in pg.inner_text("#pag"): erros.append(f"{nome}/{disp}: a tela com dados reais não mostrou o semáforo")
            else:
                txt = pg.inner_text("#pag")
                if perfil == "luis" and "Meta do Q4" not in txt: erros.append(f"{nome}/{disp}: sem 'Meta do Q4'")
                if perfil == "daniela" and ("Meta do Q4" in txt or "Decisões do Luis" in txt or re.search(r"R\$\s?\d", txt)): erros.append(f"{nome}/{disp}: a Daniela viu meta, valor em R$ ou decisões")
            largura = pg.evaluate("document.documentElement.scrollWidth")
            if largura > vp["width"]: erros.append(f"{nome}/{disp}: rolagem horizontal ({largura}px)")
            if extra != "real": pg.screenshot(path=os.path.join(SAIDA, f"gestao-{nome}-{disp}.png"), full_page=inteira and not mob)
            ctx.close()
    # Interações na prévia (nada é gravado): marcar desvio como "em andamento" muda o chip; a Daniela não vê botão de desvio de outra dona.
    ctx = nav.new_context(viewport={"width": 1440, "height": 900}); pg = ctx.new_page()
    pg.on("pageerror", lambda e: erros.append(f"fluxo: script: {e}"))
    ctx.add_init_script("try{localStorage.setItem('sou','luis');localStorage.setItem('tema','dark')}catch(e){}")
    pg.goto(PREVIA + "#gestao"); pg.wait_for_timeout(900)
    bt = pg.query_selector('[data-acao="acaoG"][data-v="em_andamento"]')
    if not bt: erros.append("fluxo: o Luis não vê o botão 'Em andamento'")
    else:
        i = bt.get_attribute("data-id"); bt.click(); pg.wait_for_timeout(400)
        if pg.evaluate(f"S.acoesG[{i!r}]?.status") != "em_andamento": erros.append("fluxo: marcação de desvio não refletiu na tela")
    ctx.close(); ctx = nav.new_context(viewport={"width": 1440, "height": 900}); ctx.add_init_script("try{localStorage.setItem('sou','daniela')}catch(e){}"); pg = ctx.new_page()
    pg.goto(PREVIA + "#gestao"); pg.wait_for_timeout(900)
    if pg.query_selector('[data-acao="acaoG"]'): erros.append("fluxo: perfil time vê botões de desvio")
    if pg.query_selector('[data-go="gestao/unidade"]'): erros.append("fluxo: perfil time vê 'Definir unidade'")
    ctx.close(); nav.close()
srv.shutdown(); shutil.rmtree(raiz, ignore_errors=True)
print("\n".join(erros) or "sem erros de console, de script nem rolagem horizontal; interações da prévia ok")
sys.exit(1 if erros else 0)
