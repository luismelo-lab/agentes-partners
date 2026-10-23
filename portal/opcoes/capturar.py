#!/usr/bin/env python3
"""Screenshots e checagens da Central Partners (desktop 1440×900 e celular 375×812).
Uso: python3 portal/opcoes/capturar.py <url-base> [prefixo]
  <url-base> é a raiz de um servidor local com:  opcoes/ (combinada.html + exemplo-dados.js),
  luis/ e time/ (index.html no esqueleto do Artifact + dados.json + diretorio.json; index-mock.html com o runtime simulado).
  Monte com um script que copie esses arquivos (ver o README do portal) e sirva com: python3 -m http.server 8765 --bind 127.0.0.1
Saída: portal/opcoes/screenshots/<prefixo>-<tela>-<desktop|celular>.png (prefixo padrão: final).
Confere em cada tela: erro de console, erro de script e rolagem horizontal. Termina com o fluxo simulado de aprovação (mock)."""
import os, sys
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765").rstrip("/")
PREF = sys.argv[2] if len(sys.argv) > 2 else "final"
SAIDA = os.path.join(AQUI, "screenshots"); os.makedirs(SAIDA, exist_ok=True)
PREVIA = BASE + "/opcoes/combinada.html"

TELAS = [  # nome, url, perfil da prévia, tema, página inteira, ação extra
    ("01-mesa-luis", PREVIA + "#mesa", "luis", "dark", True, None),
    ("02-mesa-daniela", PREVIA + "#mesa", "daniela", "dark", True, None),
    ("03-pedidos-quadro", PREVIA + "#pedidos", "luis", "dark", True, None),
    ("04-whatsapp-avaliacao", PREVIA + "#wa/D-0417", "daniela", "dark", True, None),
    ("05-whatsapp-chamado-glpi", PREVIA + "#wachamado/D-0417", "daniela", "dark", True, None),
    ("06-areas", PREVIA + "#areas", "daniela", "dark", True, None),
    ("07-area-conversa", PREVIA.replace(".html", ".html?demo") + "#area/depto-save-invest/conversa", "daniela", "dark", False, "chat"),
    ("08-area-fazer-pedido", PREVIA + "#area/depto-operacoes-canal/pedido", "daniela", "dark", False, None),
    ("09-onde-busca", PREVIA + "#onde/repasses", "daniela", "dark", True, None),
    ("10-pedido-detalhe", PREVIA + "#pedido/P-0031", "daniela", "dark", False, None),
    ("11-mesa-luis-claro", PREVIA + "#mesa", "luis", "light", True, None),
    ("12-chamado-aprovar", PREVIA + "#chamado/D-0409", "daniela", "dark", False, None),
    ("13-time-sem-conta-leitura", BASE + "/time/index.html#mesa", None, "dark", True, None),
    ("14-time-area-sem-sample", BASE + "/time/index.html#area/depto-tributario/conversa", None, "dark", False, None),
    ("15-time-dono-mesa", BASE + "/time/index-mock.html?u=dono#mesa", None, "dark", True, None),
    ("16-luis-dono-mesa", BASE + "/luis/index-mock.html?u=dono#mesa", None, "dark", True, None),
    ("17-time-daniela-whatsapp", BASE + "/time/index-mock.html?u=daniela#whatsapp", None, "dark", True, None),
]
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
            if extra == "chat":
                pg.fill("#chat-in", "Um cliente do Master com 40% de vencidos e caixa apertado serve para Gestão de Contas?")
                pg.click("#chat-env"); pg.wait_for_timeout(2500)
            largura = pg.evaluate("document.documentElement.scrollWidth")
            if largura > vp["width"]: erros.append(f"{nome}/{disp}: rolagem horizontal ({largura}px)")
            pg.screenshot(path=os.path.join(SAIDA, f"{PREF}-{nome}-{disp}.png"), full_page=inteira and not mob)
            ctx.close()
    # Fluxo simulado (mock do runtime): a Daniela aprova o próprio pedido; o registro leva por_id; a Geovana não vê o botão.
    ctx = nav.new_context(viewport={"width": 1440, "height": 900}); pg = ctx.new_page()
    pg.on("pageerror", lambda e: erros.append(f"fluxo: script: {e}"))
    pg.goto(BASE + "/time/index-mock.html?u=daniela#pedido/p1"); pg.wait_for_timeout(900)
    pg.click('[data-dec="aprovado"]'); pg.wait_for_timeout(300)
    w = pg.evaluate("window.__writes")
    ok = any(x[0] == "update" and x[1] == "pedidos/p1" and x[2]["decisao"]["por_id"] == "u_dani" for x in w)
    if not ok: erros.append(f"fluxo: aprovação sem por_id: {w}")
    pg.goto(BASE + "/time/index-mock.html?u=estranho#pedido/p1"); pg.reload(); pg.wait_for_timeout(900)
    if pg.query_selector('[data-dec="aprovado"]'): erros.append("fluxo: conta não reconhecida vê o botão Aprovar")
    if "Modo leitura" not in pg.inner_text("#faixa"): erros.append("fluxo: conta não reconhecida sem a faixa de modo leitura")
    pg.goto(BASE + "/time/index-mock.html?u=luisnome#chamado/D-1"); pg.reload(); pg.wait_for_timeout(900)
    if pg.query_selector('[data-acao="chamado"]'): erros.append("fluxo: nome 'Luis' sem ser dono vê aprovação de chamado")
    ctx.close(); nav.close()
print("\n".join(erros) or "sem erros de console, de script nem rolagem horizontal; fluxo simulado ok")
