#!/usr/bin/env python3
"""Apresentação comercial do diagnóstico, no layout da apresentação institucional da Save Co. (fundo preto, fotos, título grande,
rótulos em ouro), com fotos recortadas da própria apresentação e slides institucionais inseridos como estão.

Entrada : <pasta>/deck.json  (lista "slides"; tipos abaixo)
Saída   : <pasta>/<nome>.pdf e <nome>.pptx (cada slide é uma imagem 1920x1080, como na apresentação institucional; o roteiro vai nas notas)
          e <pasta>/previas/NN.png
Tipos   : capa · imagem (slide institucional pronto) · numeros · grade · banner · timeline · roadmap · case · passos
Uso     : python3 render_comercial.py <pasta> [nome]
Só gera arquivos locais. Requer playwright, pptxgenjs (ver gerar_apresentacao.achar_node_path) e as pastas assets-institucionais/."""
import base64, html, json, os, re, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PADRAO = Path.home() / "agentes-partners" / "departamentos" / "marketing-marca" / "padrao"
FONTES = PADRAO / "fontes"
ASS = AQUI / "assets-institucionais"
M = json.load(open(PADRAO / "marca.json"))
E = M["escuro"]
OURO, TEXTO, TEXTO2, CARTAO, BORDA = E["ouro"], E["texto"], E["texto_2"], E["cartao"], E["borda"]
RODAPE = "Pré-análise sujeita a validação técnica e jurídica. Valores são estimativas preliminares. Resultados de outros clientes não garantem resultado futuro."


def uri(p, tipo=None):
    p = Path(p); t = tipo or {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "ttf": "font/ttf"}[p.suffix[1:].lower()]
    return f"data:{t};base64," + base64.b64encode(p.read_bytes()).decode()


def esc(s):
    return html.escape(s or "").replace("\n", "<br>")


def md(s):
    return re.sub(r"\*\*(.+?)\*\*", r'<b>\1</b>', esc(s))


def css():
    f = "".join(f"@font-face{{font-family:'IBM Plex Sans';font-weight:{w};src:url({uri(FONTES / n)})}}" for n, w in
                [("IBMPlexSans-Light.ttf", 300), ("IBMPlexSans-Regular.ttf", 400), ("IBMPlexSans-Medium.ttf", 500), ("IBMPlexSans-SemiBold.ttf", 600)])
    f += f"@font-face{{font-family:'IBM Plex Mono';font-weight:400;src:url({uri(FONTES / 'IBMPlexMono-Regular.ttf')})}}"
    return f + f"""
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1920px;height:1080px;background:#000;color:{TEXTO};font-family:'IBM Plex Sans',sans-serif;position:relative;overflow:hidden}}
.mono{{font-family:'IBM Plex Mono',monospace}}
.rot{{font-family:'IBM Plex Mono',monospace;font-size:20px;letter-spacing:.12em;text-transform:uppercase;color:{OURO}}}
h1{{font-weight:300;font-size:76px;line-height:1.04;letter-spacing:-.01em;color:#E9E9E9}}
.foto{{position:absolute;background-size:cover}}
.rodape{{position:absolute;left:80px;right:80px;bottom:30px;display:flex;align-items:center;justify-content:space-between;color:#777;font-size:15px}}
.rodape img{{height:30px}} .rodape .pg{{font-family:'IBM Plex Mono';color:{OURO};font-size:18px}}
.leg{{position:absolute;left:300px;right:190px;bottom:30px;font-size:16px;line-height:1.3;color:#8c8c8c}}
.regua{{position:absolute;left:80px;right:80px;height:1px;background:#3a3a3a}}
.col{{position:absolute}} .col .tg{{font-family:'IBM Plex Mono';font-size:18px;letter-spacing:.1em;text-transform:uppercase;color:{OURO};margin-bottom:12px}}
.col h3{{font-weight:500;font-size:31px;line-height:1.18;margin-bottom:14px;color:#F2F2F2}}
.col p{{font-size:24px;line-height:1.38;color:#C4C4C4}} .col p b{{color:#F2F2F2;font-weight:500}}
.col .sa{{margin-top:14px;font-size:24px;line-height:1.38;color:#C4C4C4}} .col .sa b{{color:{OURO};font-weight:500}}
.chip{{display:inline-block;margin-top:16px;padding:6px 14px;border:1px solid {OURO};border-radius:20px;font-family:'IBM Plex Mono';font-size:16px;letter-spacing:.06em;color:{OURO};text-transform:uppercase}}
.card{{position:absolute;background:{CARTAO};border:1px solid {BORDA};border-radius:16px;padding:26px 28px}}
"""


def pagina(corpo, n, tot, leg=RODAPE, rodape=True):
    r = (f'<div class="rodape"><img src="{uri(PADRAO / M["logos"]["fundo_escuro"])}"><span class="pg">{n:02d} / {tot:02d}</span></div>'
         f'<div class="leg">{esc(leg)}</div>') if rodape else ""
    return f"<!doctype html><meta charset=utf-8><style>{css()}</style><body>{corpo}{r}</body>"


def fundo(nome, op=0.28, blur=2):
    return (f'<div class="foto" style="left:0;top:0;width:1920px;height:1080px;{foto_css(nome)};opacity:{op};filter:blur({blur}px)"></div>'
            f'<div style="position:absolute;left:0;top:0;width:1920px;height:1080px;background:linear-gradient(180deg,rgba(0,0,0,.2),#000 85%)"></div>')


def foto_css(nome, pos="center"):
    return f"background-image:url({uri(ASS / (nome + '.jpg'))});background-position:{pos}"


def faixa(s, topo):
    if s.get("fundo"): return fundo(s["foto"], s.get("op", 0.3))
    return (f'<div class="foto" style="left:0;top:0;width:1920px;height:{topo}px;{foto_css(s["foto"], s.get("pos", "center"))}"></div>'
            f'<div style="position:absolute;left:0;top:0;width:1920px;height:{topo + 20}px;background:linear-gradient(180deg,rgba(0,0,0,.35) 0%,rgba(0,0,0,.15) 40%,#000 100%)"></div>')


def banner(s, n, tot):
    """Foto no topo (como as divisórias da apresentação institucional), título grande e colunas de texto."""
    cols = s["cols"]; k = len(cols); w = (1920 - 160 - (k - 1) * 48) // k
    topo = s.get('topo', 410)
    corpo = (faixa(s, topo) +
                          f'<div style="position:absolute;left:80px;top:{topo - 150}px;width:1500px"><div class="rot" style="margin-bottom:16px">{esc(s.get("rotulo", ""))}</div><h1>{esc(s["titulo"])}</h1></div>'
             f'<div class="regua" style="top:{topo + 60}px"></div>')
    for i, c in enumerate(cols):
        x = 80 + i * (w + 48)
        corpo += (f'<div class="col" style="left:{x}px;top:{topo + 100}px;width:{w}px"><div class="tg">{esc(c.get("tag", f"{i + 1:02d}"))}</div><h3>{esc(c["titulo"])}</h3>'
                  f'<p>{md(c["texto"])}</p>' + (f'<p class="sa"><b>Como a Save ajuda:</b> {md(c["save"])}</p>' if c.get("save") else "") +
                  (f'<span class="chip">{esc(c["chip"])}</span>' if c.get("chip") else "") + "</div>")
    return pagina(corpo, n, tot, s.get("leg", RODAPE))


def capa(s, n, tot):
    corpo = (f'<div class="foto" style="right:0;top:0;width:820px;height:1080px;{foto_css(s.get("foto", "predio"), "center")}"></div>'
             f'<div style="position:absolute;right:0;top:0;width:820px;height:1080px;background:linear-gradient(90deg,#000 0%,rgba(0,0,0,.0) 45%)"></div>'
             f'<img src="{uri(PADRAO / M["logos"]["fundo_escuro"])}" style="position:absolute;left:80px;top:70px;width:250px">'
             f'<div style="position:absolute;left:80px;top:330px;width:1050px"><div class="rot" style="margin-bottom:28px">{esc(s["rotulo"])}</div><h1 style="font-size:92px">{esc(s["titulo"])}</h1>'
             f'<p style="margin-top:36px;font-size:28px;line-height:1.4;color:#B5B5B5;width:900px">{md(s["subtitulo"])}</p></div>'
             f'<div style="position:absolute;left:80px;bottom:110px;width:140px;height:5px;background:{OURO}"></div>'
             f'<div class="rot" style="position:absolute;left:80px;bottom:60px;color:#8a8a8a">{esc(s["linha"])}</div>')
    return pagina(corpo, n, tot, rodape=False)


def numeros(s, n, tot):
    k = len(s["itens"]); w = (1920 - 160 - (k - 1) * 60) // k; topo = s.get('topo', 410)
    corpo = (faixa(s, topo) +
                          f'<div style="position:absolute;left:80px;top:{topo - 150}px;width:1500px"><div class="rot" style="margin-bottom:16px">{esc(s["rotulo"])}</div><h1>{esc(s["titulo"])}</h1></div>'
             f'<div class="regua" style="top:{topo + 60}px"></div>')
    for i, it in enumerate(s["itens"]):
        x = 80 + i * (w + 60)
        corpo += (f'<div class="col" style="left:{x}px;top:{topo + 120}px;width:{w}px"><div style="font-size:128px;font-weight:300;line-height:1;color:#EDEDED">{esc(it["valor"])}'
                  f'<span style="font-size:44px;color:{OURO};margin-left:10px">{esc(it.get("unidade", ""))}</span></div>'
                  f'<p style="margin-top:22px;font-size:26px">{md(it["legenda"])}</p></div>')
    if s.get("dor"): corpo += f'<div style="position:absolute;left:80px;top:{topo + 520}px;width:1500px;font-size:30px;font-weight:300;color:{OURO}">{esc(s["dor"])}</div>'
    return pagina(corpo, n, tot, s.get("leg", RODAPE))


def grade(s, n, tot):
    itens = s["itens"]; cols = 4; w = (1920 - 160 - (cols - 1) * 28) // cols; h = 330
    corpo = (f'<div style="position:absolute;left:80px;top:70px;width:1600px"><div class="rot" style="margin-bottom:16px">{esc(s["rotulo"])}</div><h1 style="font-size:64px">{esc(s["titulo"])}</h1></div>')
    for i, it in enumerate(itens):
        x = 80 + (i % cols) * (w + 28); y = 300 + (i // cols) * (h + 28)
        corpo += (f'<div class="card" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"><div class="mono" style="color:{OURO};font-size:17px;letter-spacing:.1em">{esc(it["via"]).upper()}</div>'
                  f'<div style="font-size:29px;font-weight:500;line-height:1.2;margin:12px 0 10px;color:#F2F2F2">{esc(it["nome"])}</div>'
                  f'<div style="font-size:22px;line-height:1.35;color:#B5B5B5">{esc(it["linha"])}</div>'
                  f'<span class="chip" style="position:absolute;left:28px;bottom:24px;margin:0">{esc(it["status"])}</span></div>')
    return pagina(corpo, n, tot, s.get("leg", RODAPE))


def timeline(s, n, tot):
    itens = s["itens"]; k = len(itens); w = (1920 - 160 - (k - 1) * 30) // k; topo = s.get('topo', 410)
    corpo = (faixa(s, topo) +
                          f'<div style="position:absolute;left:80px;top:{topo - 150}px;width:1500px"><div class="rot" style="margin-bottom:16px">{esc(s["rotulo"])}</div><h1>{esc(s["titulo"])}</h1></div>'
             f'<div class="regua" style="top:{topo + 90}px;background:{OURO}"></div>')
    for i, it in enumerate(itens):
        x = 80 + i * (w + 30)
        corpo += (f'<div style="position:absolute;left:{x}px;top:{topo + 78}px;width:24px;height:24px;border-radius:12px;background:{OURO}"></div>'
                  f'<div class="col" style="left:{x}px;top:{topo + 125}px;width:{w}px"><div class="tg" style="font-size:{30 if k <= 4 else 20}px;margin-bottom:18px">{esc(it["marco"])}</div><h3 style="font-size:{36 if k <= 4 else 29}px">{esc(it["titulo"])}</h3>'
                  f'<p style="font-size:{27 if k <= 4 else 22}px">{md(it["texto"])}</p>' + (f'<span class="chip" style="font-size:17px">{esc(it["chip"])}</span>' if it.get("chip") else "") + '</div>')
    return pagina(corpo, n, tot, s.get("leg", RODAPE))


def roadmap(s, n, tot):
    et = s["etapas"]; w = (1920 - 160 - 2 * 70) // 3
    corpo = (f'<div class="foto" style="right:0;top:0;width:760px;height:1080px;{foto_css(s.get("foto", "pessoas"), "center")};opacity:.5"></div>'
             f'<div style="position:absolute;right:0;top:0;width:760px;height:1080px;background:linear-gradient(90deg,#000 0%,rgba(0,0,0,0) 60%)"></div>'
             f'<div style="position:absolute;left:80px;top:70px;width:1300px"><div class="rot" style="margin-bottom:16px">{esc(s["rotulo"])}</div><h1 style="font-size:66px">{esc(s["titulo"])}</h1></div>')
    for i, e in enumerate(et):
        x = 80 + i * (w + 70); y = 330
        destaque = e.get("destaque")
        corpo += (f'<div class="card" style="left:{x}px;top:{y}px;width:{w}px;height:610px;{"background:#0c0c0c;border-color:" + OURO if destaque else ""}">'
                  f'<div class="mono" style="color:{OURO};font-size:20px">{i + 1:02d}</div>'
                  f'<div style="font-size:60px;font-weight:300;margin:8px 0 8px;color:#EDEDED">{esc(e["titulo"])}</div>'
                  f'<div style="font-size:23px;line-height:1.35;color:#BDBDBD;margin-bottom:26px;min-height:64px">{esc(e["texto"])}</div>'
                  + "".join(f'<div style="border-top:1px solid {BORDA};padding:14px 0;font-size:24px;color:#EAEAEA">{esc(p)}</div>' for p in e["produtos"]) + "</div>")
        if i < 2:
            corpo += f'<div style="position:absolute;left:{x + w + 14}px;top:{y + 270}px;color:{OURO};font-size:44px">›</div>'
    return pagina(corpo, n, tot, s.get("leg", RODAPE))


def case(s, n, tot):
    corpo = (f'<div class="foto" style="right:0;top:0;width:900px;height:1080px;{foto_css("maos", "center")}"></div>'
             f'<div style="position:absolute;right:0;top:0;width:900px;height:1080px;background:linear-gradient(90deg,#000 0%,rgba(0,0,0,.2) 55%)"></div>'
             f'<div style="position:absolute;left:80px;top:90px;width:1000px"><div class="rot" style="margin-bottom:16px">{esc(s["rotulo"])}</div><h1 style="font-size:68px">{esc(s["titulo"])}</h1></div>'
             f'<div style="position:absolute;left:80px;top:430px;width:1100px"><div style="font-size:50px;color:#9a9a9a;font-weight:300">R$</div>'
             f'<div style="font-size:150px;line-height:1;font-weight:300;color:#EDEDED;letter-spacing:-.02em">{esc(s["valor"])}</div>'
             f'<div style="font-size:40px;color:{OURO};margin-top:14px;text-align:right;width:880px">reconectados</div>'
             f'<p style="margin-top:40px;font-size:26px;line-height:1.4;color:#BDBDBD;width:880px">{md(s["texto"])}</p></div>')
    return pagina(corpo, n, tot, s.get("leg", RODAPE))


def passos(s, n, tot):
    k = len(s["passos"]); w = (1920 - 160 - (k - 1) * 40) // k
    corpo = (f'<div style="position:absolute;left:80px;top:70px;width:1500px"><div class="rot" style="margin-bottom:16px">{esc(s["rotulo"])}</div><h1 style="font-size:66px">{esc(s["titulo"])}</h1></div>')
    if s.get("foto"):
        corpo = (f'<div class="foto" style="right:0;top:0;width:700px;height:1080px;{foto_css(s["foto"], s.get("pos", "center"))};opacity:.5"></div>'
                 f'<div style="position:absolute;right:0;top:0;width:700px;height:1080px;background:linear-gradient(90deg,#000 0%,rgba(0,0,0,0) 70%)"></div>') + corpo
    for i, p in enumerate(s["passos"]):
        x = 80 + i * (w + 40)
        corpo += (f'<div class="card" style="left:{x}px;top:340px;width:{w}px;height:{s.get("altura", 400)}px"><div class="mono" style="color:{OURO};font-size:22px">{i + 1:02d}</div>'
                  f'<div style="font-size:34px;font-weight:500;margin:16px 0 14px;line-height:1.2;color:#F2F2F2">{esc(p["titulo"])}</div>'
                  f'<div style="font-size:23px;line-height:1.4;color:#BDBDBD">{md(p["texto"])}</div></div>')
    if s.get("contato"):
        corpo += f'<div class="rot" style="position:absolute;left:80px;bottom:110px;color:#9a9a9a;font-size:18px">{esc(s["contato"])}</div>'
    return pagina(corpo, n, tot, s.get("leg", RODAPE))


def lateral(s, n, tot):
    """Foto em cartão à esquerda (na resolução original), título no topo e blocos em 2 colunas à direita."""
    fw, fh = s.get("fw", 520), s.get("fh", 480); cols = s["cols"]
    corpo = (f'<div style="position:absolute;left:80px;top:70px;width:1700px"><div class="rot" style="margin-bottom:16px">{esc(s["rotulo"])}</div><h1 style="font-size:66px">{esc(s["titulo"])}</h1></div>'
             f'<div class="foto" style="left:80px;top:330px;width:{fw}px;height:{fh}px;border-radius:18px;border:1px solid {BORDA};{foto_css(s["foto"], s.get("pos", "center"))}"></div>')
    x0 = 80 + fw + 56; per = s.get('por_linha', 2 if len(cols) > 2 else 1); w = (1920 - 80 - x0 - (per - 1) * 44) // per; hcell = s.get('hcell', 330 if per == 2 else 500)
    if s.get("destaque"):
        d = s["destaque"]; xd = x0 + (w + 44) * (len(cols) % per); yd = 330 + (len(cols) // per) * (hcell + 14)
        corpo += (f'<div style="position:absolute;left:{xd}px;top:{yd}px;width:{w}px"><div class="tg">Referência</div><span class="mono" style="font-size:96px;color:#EDEDED;line-height:1">{esc(d["valor"])}</span>'
                  f'<div style="font-size:23px;line-height:1.38;color:#C4C4C4;margin-top:10px">{esc(d["legenda"])}</div></div>')
    for i, c in enumerate(cols):
        x = x0 + (i % per) * (w + 44); y = 330 + (i // per) * (hcell + 14)
        corpo += (f'<div class="col" style="left:{x}px;top:{y}px;width:{w}px"><div class="tg">{esc(c.get("tag", ""))}</div><h3 style="font-size:29px">{esc(c["titulo"])}</h3>'
                  f'<p style="font-size:24px">{md(c["texto"])}</p>' + (f'<span class="chip" style="font-size:16px">{esc(c["chip"])}</span>' if c.get("chip") else "") + "</div>")
    return pagina(corpo, n, tot, s.get("leg", RODAPE))


TIPOS = {"lateral": lateral, "capa": capa, "numeros": numeros, "grade": grade, "banner": banner, "timeline": timeline, "roadmap": roadmap, "case": case, "passos": passos}


def main(pasta, nome=None):
    from playwright.sync_api import sync_playwright
    pasta = Path(pasta).resolve(); deck = json.load(open(pasta / "deck.json")); sl = deck["slides"]; tot = len(sl)
    nome = nome or deck.get("nome", "Apresentacao"); prev = pasta / "previas"; prev.mkdir(exist_ok=True)
    pngs = []; notas = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome"); pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
        for i, s in enumerate(sl, 1):
            dest = prev / f"{i:02d}.jpg"
            if s["tipo"] == "imagem":
                src = ASS / "slides" / s["arquivo"]
                pg.set_content(f"<body style='margin:0;background:#000'><img src='{uri(src)}' style='width:1920px;height:1080px;display:block'>")
            else:
                pg.set_content(TIPOS[s["tipo"]](s, i, tot))
            pg.wait_for_timeout(250); pg.screenshot(path=str(dest), type="jpeg", quality=93); pngs.append(str(dest)); notas.append(s.get("notas", ""))
        # PDF: uma imagem por página
        corpo = "".join(f"<img src='{uri(x)}' style='width:1920px;height:1080px;display:block;page-break-after:always'>" for x in pngs)
        pg.set_content(f"<style>@page{{size:1920px 1080px;margin:0}}body{{margin:0}}</style>{corpo}")
        pg.pdf(path=str(pasta / f"{nome}.pdf"), width="1920px", height="1080px", print_background=True)
        b.close()
    json.dump({"imagens": pngs, "notas": notas}, open(pasta / "_pptx.json", "w"), ensure_ascii=False)
    sys.path.insert(0, str(AQUI)); import gerar_apresentacao as g
    r = subprocess.run(["node", str(AQUI / "pptx_imagens.js"), str(pasta / "_pptx.json"), str(pasta / f"{nome}.pptx")],
                       env={**os.environ, "NODE_PATH": g.achar_node_path()}, capture_output=True, text=True)
    os.remove(pasta / "_pptx.json")
    print(f"{tot} slides → {pasta / nome}.pdf / .pptx" + ("" if r.returncode == 0 else "\nERRO pptx: " + r.stderr[-300:]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
