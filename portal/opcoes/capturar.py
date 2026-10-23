#!/usr/bin/env python3
"""Screenshots da prévia combinada da Central Partners (desktop 1440×900 e celular 375×812).
Uso: python3 portal/opcoes/capturar.py [arquivo.html]  → portal/opcoes/screenshots/
Abre o arquivo local (file://) com os dados de exemplo; ?demo liga a resposta de demonstração do chat."""
import os, sys
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
ARQ = sys.argv[1] if len(sys.argv) > 1 else "combinada.html"
BASE = "file://" + os.path.join(AQUI, ARQ)
SAIDA = os.path.join(AQUI, "screenshots"); os.makedirs(SAIDA, exist_ok=True)
pref = os.path.splitext(ARQ)[0]

TELAS = [  # nome, perfil, rota, página inteira, ação extra
    ("1-mesa-luis", "luis", "#mesa", True, None),
    ("2-mesa-daniela", "daniela", "#mesa", True, None),
    ("3-areas", "daniela", "#areas", True, None),
    ("4-area-chat", "daniela", "#area/depto-operacoes-canal/conversa", False, "chat"),
    ("5-fazer-pedido", "daniela", "#area/depto-operacoes-canal/pedido", False, None),
    ("6-onde-busca", "daniela", "#onde/" + "Conferência de repasses", True, None),
    ("7-pedido-detalhe", "daniela", "#pedido/P-0031", False, None),
    ("8-mesa-luis-escuro", "luis", "#mesa", False, "escuro"),
    ("9-area-chat-indisponivel", "daniela", "#area/depto-tributario/conversa", False, None),
]
erros = []
with sync_playwright() as pw:
    nav = pw.chromium.launch()
    for disp, vp, mob in (("desktop", {"width": 1440, "height": 900}, False), ("celular", {"width": 375, "height": 812}, True)):
        for nome, perfil, hash_, inteira, extra in TELAS:
            ctx = nav.new_context(viewport=vp, device_scale_factor=2 if mob else 1, is_mobile=mob, has_touch=mob)
            ctx.add_init_script(f"try{{localStorage.setItem('sou','{perfil}');localStorage.setItem('tema','{'dark' if extra == 'escuro' else 'light'}')}}catch(e){{}}")
            pg = ctx.new_page()
            pg.on("console", lambda m: m.type == "error" and erros.append(f"{nome}/{disp}: {m.text}"))
            pg.on("pageerror", lambda e: erros.append(f"{nome}/{disp}: {e}"))
            pg.goto(BASE + ("?demo" if extra == "chat" else "") + hash_)
            pg.wait_for_timeout(900)
            if extra == "chat":
                pg.fill("#chat-in", "O que vocês precisam para a conferência de repasses de outubro do Master 2?")
                pg.click("#chat-env"); pg.wait_for_timeout(2500)
            largura = pg.evaluate("document.documentElement.scrollWidth")
            if largura > vp["width"]: erros.append(f"{nome}/{disp}: rolagem horizontal ({largura}px)")
            pg.screenshot(path=os.path.join(SAIDA, f"{pref}-{nome}-{disp}.png"), full_page=inteira and not mob)
            ctx.close()
    nav.close()
print("\n".join(erros) or "sem erros de console nem rolagem horizontal")
