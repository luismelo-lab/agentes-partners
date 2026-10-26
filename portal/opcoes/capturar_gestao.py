#!/usr/bin/env python3
"""Screenshots e checagens da Central Partners v3 (26/10/2026): tela "Gestão" com a meta mensal da D111, pré-análise por farol,
dossiê das decisões e demandas do WhatsApp respondidas pelo histórico. Desktop 1440×900 e celular 375×812.
Serve a pasta portal/ sozinho (servidor local numa porta livre) e usa a prévia (combinada.html + exemplo-dados.js, sem cliente).
Confere em cada tela: erro de console, erro de script, rolagem horizontal e o texto esperado; testa o filtro "só fora da tolerância",
o clique nos cenários e a marcação de desvio (na prévia nada é gravado). O botão "Definir unidade" não pode aparecer (D111).
Com --real <pasta>, abre também uma cópia do index.html com os dados reais (dados.json + diretorio.json dessa pasta), só para
conferir erros e rolagem; não tira screenshot dos dados reais.
Uso: python3 portal/opcoes/capturar_gestao.py [--real <pasta com dados.json>]   → portal/opcoes/screenshots/v3-<tela>-<desktop|celular>.png"""
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
TELAS = [  # nome, url, perfil, tema, página inteira, ação extra, textos que precisam aparecer, textos proibidos
    ("01-luis-gestao", PREVIA + "#gestao", "luis", "dark", True, None, ["Meta de outubro", "Meta do Q4", "Mês a mês", "Pré-análise da área", "1ª ação"], ["Definir unidade", "Mudar unidade"]),
    ("02-luis-masters-proposta", PREVIA + "#gestao", "luis", "dark", False, "masters", ["Desdobramento por Master", "Proposta"], []),
    ("03-luis-cenario-esforco", PREVIA + "#gestao", "luis", "dark", False, "cenario", ["Premissas do cenário de esforço"], []),
    ("04-luis-farol-pre-analise", PREVIA + "#gestao/farol/conversao_pct", "luis", "dark", False, None, ["Leitura", "Fatos", "Hipóteses", "Ações", "Decisão sugerida", "Confiança"], []),
    ("05-luis-dossie", PREVIA + "#gestao/decisao/D30", "luis", "dark", False, None, ["O que decidir", "Validação das áreas", "Opções", "Aprovar com ajuste"], []),
    ("06-luis-dossie-ausente", PREVIA + "#gestao/decisao/D31", "luis", "dark", False, None, ["Dossiê ainda não preparado", "Reprovar"], []),
    ("07-luis-mesa", PREVIA + "#mesa", "luis", "dark", True, None, ["Meta de outubro", "Q4"], []),
    ("08-daniela-semaforo", PREVIA + "#gestao", "daniela", "dark", True, None, ["Semáforo"], ["Pré-análise da área", "Meta do Q4", "Decisões do Luis", "1ª ação"]),
    ("09-daniela-wa-historico", PREVIA + "#wa/D-0412", "daniela", "dark", False, None, ["Respondido pelo histórico", "dado do caso", "Copiar resposta", "Respondi", "Fontes"], []),
    ("10-daniela-wa-glpi", PREVIA + "#wa/D-0417", "daniela", "dark", False, None, ["Histórico consultado", "faltou:", "Gerar chamado GLPI"], []),
    ("11-luis-claro-gestao", PREVIA + "#gestao", "luis", "light", True, None, ["Meta de outubro"], []),
    ("12-luis-claro-dossie", PREVIA + "#gestao/decisao/D30", "luis", "light", False, None, ["Validação das áreas"], []),
]
if REAL: TELAS += [("real-luis", BASE + "/real/index.html#gestao", None, "dark", False, "real", [], []), ("real-decisoes", BASE + "/real/index.html#decisoes", None, "dark", False, "real", [], []),
                   ("real-whatsapp", BASE + "/real/index.html#whatsapp", None, "dark", False, "real", [], [])]
erros = []
with sync_playwright() as pw:
    nav = pw.chromium.launch()
    for disp, vp, mob in (("desktop", {"width": 1440, "height": 900}, False), ("celular", {"width": 375, "height": 812}, True)):
        for nome, u, perfil, tema, inteira, extra, deve, proibido in TELAS:
            ctx = nav.new_context(viewport=vp, device_scale_factor=2 if mob else 1, is_mobile=mob, has_touch=mob)
            ctx.add_init_script(f"try{{localStorage.setItem('sou','{perfil or ''}');localStorage.setItem('tema','{tema}')}}catch(e){{}}")
            pg = ctx.new_page()
            pg.on("console", lambda m, n=nome, d=disp: m.type == "error" and erros.append(f"{n}/{d}: console: {m.text}"))
            pg.on("pageerror", lambda e, n=nome, d=disp: erros.append(f"{n}/{d}: script: {e}"))
            pg.goto(u); pg.wait_for_timeout(900)
            if extra == "fora": pg.click('[data-g-fora="1"]'); pg.wait_for_timeout(300)
            if extra == "cenario": pg.click('[data-cen="esforco"]'); pg.wait_for_timeout(300); pg.locator("#premissas").scroll_into_view_if_needed()
            if extra == "masters": pg.click("details.prop > summary"); pg.wait_for_timeout(300); pg.locator("details.prop").scroll_into_view_if_needed()
            if extra == "real":
                if "real-luis" == nome and "Semáforo" not in pg.inner_text("#pag"): erros.append(f"{nome}/{disp}: a tela com dados reais não mostrou o semáforo")
            else:
                txt = pg.inner_text("body").lower()
                for t in deve:
                    if t.lower() not in txt: erros.append(f"{nome}/{disp}: faltou '{t}'")
                for t in proibido:
                    if t.lower() in txt: erros.append(f"{nome}/{disp}: apareceu '{t}'")
                if perfil == "daniela" and "semaforo" in nome and re.search(r"R\$\s?\d", pg.inner_text("#pag")): erros.append(f"{nome}/{disp}: a Daniela viu valor em R$")
            largura = pg.evaluate("document.documentElement.scrollWidth")
            if largura > vp["width"]: erros.append(f"{nome}/{disp}: rolagem horizontal ({largura}px)")
            if extra != "real": pg.screenshot(path=os.path.join(SAIDA, f"v3-{nome}-{disp}.png"), full_page=inteira and not mob)
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
    if pg.query_selector('[data-go^="gestao/farol/"]'): erros.append("fluxo: perfil time vê a pré-análise")
    ctx.close(); nav.close()
srv.shutdown(); shutil.rmtree(raiz, ignore_errors=True)
print("\n".join(erros) or "sem erros de console, de script nem rolagem horizontal; interações da prévia ok")
sys.exit(1 if erros else 0)
