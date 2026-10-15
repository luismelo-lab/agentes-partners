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


RODAPE_ATIVO = False   # decisão do Luis (15/10/2026): apresentação sem rodapé; o texto da legenda vai para as notas


def pagina(corpo, n, tot, leg=RODAPE, rodape=True, leg_left=300):
    rodape = rodape and RODAPE_ATIVO
    r = (f'<div class="rodape"><img src="{uri(PADRAO / M["logos"]["fundo_escuro"])}"><span class="pg">{n:02d} / {tot:02d}</span></div>'
         f'<div class="leg" style="left:{leg_left}px">{esc(leg)}</div>') if rodape else ""
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
    if s.get("dor"): corpo += f'<div style="position:absolute;left:80px;top:{topo + 470}px;width:1760px;font-size:32px;font-weight:300;color:{OURO}">{esc(s["dor"])}</div>'
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
    """Três etapas em pilares ascendentes, ligados por uma curva dourada (arte da Save: preto, ouro, linhas finas)."""
    et = s["etapas"]; GANHO = {"Oxigenar": "Mais caixa e menos dívida", "Estruturar": "Previsibilidade e controle", "Escalar": "Crescimento sustentável"}
    W, GAP = 540, 70; tops = [530, 450, 370]; bottom = 975; xs = [80 + i * (W + GAP) for i in range(3)]
    marca = uri(PADRAO / M["logos"]["simbolo_contorno_ouro"])
    pts = [(xs[i] + W / 2, tops[i] - 62) for i in range(3)]
    curva = (f"M 20 {pts[0][1] + 70} C 140 {pts[0][1] + 40}, 230 {pts[0][1] + 8}, {pts[0][0]} {pts[0][1]} "
             f"C {pts[0][0] + 230} {pts[0][1] - 8}, {pts[1][0] - 230} {pts[1][1] + 10}, {pts[1][0]} {pts[1][1]} "
             f"C {pts[1][0] + 230} {pts[1][1] - 8}, {pts[2][0] - 230} {pts[2][1] + 10}, {pts[2][0]} {pts[2][1]} "
             f"C {pts[2][0] + 110} {pts[2][1] - 12}, {pts[2][0] + 190} {pts[2][1] - 30}, {pts[2][0] + 250} {pts[2][1] - 52}")
    grade = "".join(f'<line x1="0" y1="{y}" x2="1920" y2="{y}" stroke="{OURO}" stroke-opacity=".05"/>' for y in range(120, 1080, 90))
    grade += "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="1080" stroke="{OURO}" stroke-opacity=".035"/>' for x in range(80, 1920, 180))
    svg = (f'<svg style="position:absolute;left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080"><defs>'
           f'<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{OURO}" stop-opacity=".15"/><stop offset=".5" stop-color="{OURO}" stop-opacity=".9"/><stop offset="1" stop-color="#FFF1BF"/></linearGradient>'
           f'<filter id="b"><feGaussianBlur stdDeviation="6"/></filter></defs>{grade}'
           f'<path d="{curva}" fill="none" stroke="{OURO}" stroke-width="7" stroke-opacity=".25" filter="url(#b)"/>'
           f'<path d="{curva}" fill="none" stroke="url(#g)" stroke-width="2.4" stroke-linecap="round"/>'
           + "".join(f'<line x1="{x}" y1="{y + 10}" x2="{x}" y2="{y + 62}" stroke="{OURO}" stroke-opacity=".55" stroke-dasharray="3 5"/><circle cx="{x}" cy="{y}" r="24" fill="{OURO}" fill-opacity=".14"/><circle cx="{x}" cy="{y}" r="9" fill="{OURO}"/><circle cx="{x}" cy="{y}" r="3.5" fill="#000"/>' for x, y in pts)
           + f'<path d="M {pts[2][0] + 228} {pts[2][1] - 70} L {pts[2][0] + 250} {pts[2][1] - 52} L {pts[2][0] + 230} {pts[2][1] - 36}" fill="none" stroke="#FFF1BF" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    corpo = (f'<div style="position:absolute;left:0;top:0;width:1920px;height:1080px;background:radial-gradient(ellipse at 72% 38%,#17130a 0%,#070604 45%,#000 75%)"></div>'
             f'<img src="{marca}" style="position:absolute;right:-90px;bottom:-70px;width:760px;opacity:.07">' + svg +
             f'<div style="position:absolute;left:80px;top:70px;width:1300px"><div class="rot" style="margin-bottom:16px">{esc(s["rotulo"])}</div><h1 style="font-size:66px">{esc(s["titulo"])}</h1></div>')
    for i, e in enumerate(et):
        top = tops[i]; h = bottom - top; dest = e.get("destaque")
        borda = f"1.5px solid {OURO}" if dest else "1px solid rgba(243,205,96,.32)"
        glow = f"box-shadow:0 0 60px rgba(243,205,96,.13), inset 0 0 40px rgba(243,205,96,.05);" if dest else ""
        prods = "".join(f'<div style="display:flex;align-items:center;gap:14px;padding:9px 0;border-top:1px solid rgba(255,255,255,.09);font-size:23px;color:#EDEDED">'
                        f'<span style="flex:none;width:9px;height:9px;background:{OURO};transform:rotate(45deg)"></span>{esc(p)}</div>' for p in e["produtos"])
        corpo += (f'<div style="position:absolute;left:{xs[i]}px;top:{top}px;width:{W}px;height:{h}px;border:{borda};border-radius:22px;{glow}'
                  f'background:linear-gradient(180deg,rgba(243,205,96,.075),rgba(255,255,255,.012) 55%,rgba(0,0,0,.2));padding:34px 38px;box-sizing:border-box">'
                  f'<div style="position:absolute;left:38px;top:-1px;width:70px;height:3px;background:{OURO};border-radius:2px"></div>'
                  f'<div class="mono" style="color:{OURO};font-size:20px;letter-spacing:.14em">{i + 1:02d}</div>'
                  f'<div style="font-size:60px;font-weight:300;color:#F0F0F0;line-height:1.1;margin:6px 0 8px">{esc(e["titulo"])}</div>'
                  f'<div style="font-size:22px;line-height:1.35;color:#BDBDBD;margin-bottom:14px">{esc(e["texto"])}</div>{prods}'
                  f'<div style="position:absolute;left:38px;right:38px;bottom:26px;font-size:20px;color:{OURO};letter-spacing:.02em">{esc(e.get("ganho", GANHO.get(e["titulo"], "")))}</div></div>')
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


def painel(s, n, tot):
    """Layout da apresentação institucional: foto à esquerda (44% do slide, na resolução do arquivo) e conteúdo à direita."""
    pw = 845; x0 = pw + 70; w = 1920 - 80 - x0
    corpo = (f'<div class="foto" style="left:0;top:0;width:{pw}px;height:1080px;{foto_css(s["foto"], "center")}"></div>'
             f'<div style="position:absolute;left:{x0}px;top:70px;width:{w}px"><div class="rot" style="margin-bottom:16px">{esc(s["rotulo"])}</div><h1 style="font-size:{s.get("tit", 46)}px">{esc(s["titulo"])}</h1></div>')
    blocos = ""
    for b in s["blocos"]:
        val = (f'<div style="flex:none;width:{s.get("wval", 250)}px;text-align:right"><div class="mono" style="font-size:{s.get("fval", 28)}px;color:{OURO};line-height:1.1">{esc(b["valor"])}</div>'
               f'<div style="font-size:16px;color:#9a9a9a;margin-top:6px">{esc(b.get("valor_leg", ""))}</div></div>') if b.get("valor") else ""
        blocos += (f'<div style="display:flex;gap:30px;align-items:flex-start;padding:{s.get("pad", 15)}px 0;border-top:1px solid #333"><div style="flex:1">'
                   f'<div class="rot" style="font-size:16px;margin-bottom:8px">{esc(b.get("tag", ""))}</div>'
                   f'<div style="font-size:{s.get("fh3", 28)}px;font-weight:500;line-height:1.2;color:#F2F2F2;margin-bottom:8px">{esc(b["titulo"])}</div>'
                   f'<div style="font-size:{s.get("ftx", 21)}px;line-height:1.38;color:#C4C4C4">{md(b["texto"])}</div></div>{val}</div>')
    corpo += f'<div style="position:absolute;left:{x0}px;top:{s.get("topo", 300)}px;width:{w}px">{blocos}</div>'
    return pagina(corpo, n, tot, s.get("leg", RODAPE), leg_left=x0)


def valores(s, n, tot):
    """Valor identificado: número grande e barras por tese, sobre foto escurecida."""
    itens = s["itens"]; mx = max(i["valor"] for i in itens)
    corpo = (fundo(s["foto"], s.get("op", .3)) +
             f'<div style="position:absolute;left:80px;top:70px;width:1700px"><div class="rot" style="margin-bottom:16px">{esc(s["rotulo"])}</div><h1 style="font-size:60px">{esc(s["titulo"])}</h1></div>'
             f'<div style="position:absolute;left:80px;top:330px;width:700px"><div class="mono" style="font-size:20px;color:{OURO};letter-spacing:.1em">{esc(s["total_rot"]).upper()}</div>'
             f'<div style="font-size:112px;font-weight:300;line-height:1.05;color:#EDEDED;margin-top:12px;white-space:nowrap">{esc(s["total"])}</div>'
             f'<div style="font-size:25px;line-height:1.4;color:#C4C4C4;margin-top:18px">{md(s["total_leg"])}</div></div>')
    rows = ""
    for it in itens:
        wd = max(3, round(it["valor"] / mx * 100))
        rows += (f'<div style="margin-bottom:26px"><div style="display:flex;justify-content:space-between;align-items:baseline"><div style="font-size:25px;color:#F2F2F2;font-weight:500">{esc(it["rotulo"])}</div>'
                 f'<div class="mono" style="font-size:25px;color:{OURO}">{esc(it["texto"])}</div></div>'
                 f'<div style="height:12px;background:#1c1c1c;border-radius:6px;margin-top:10px"><div style="height:12px;width:{wd}%;background:{OURO};border-radius:6px"></div></div>'
                 f'<div style="font-size:19px;color:#9a9a9a;margin-top:6px">{esc(it.get("nota", ""))}</div></div>')
    corpo += f'<div style="position:absolute;left:800px;top:320px;width:1040px">{rows}</div>'
    return pagina(corpo, n, tot, s.get("leg", RODAPE))


def ecossistema(s, n, tot):
    """Ecossistema Save refeito: círculo do PowerPoint (resolução original) com os rótulos em texto nítido e linhas-guia douradas."""
    Wd = 660; left = 630; top = 285; k = Wd / 1016
    # ponto de cada fatia (coordenadas da imagem exibida em 1016 px) e rótulo
    esq = [(330, 120, "Assessoria Empresarial", ""), (150, 420, "Planejamento Patrimonial", ""), (110, 690, "Save ID", "Certificado Digital"), (300, 880, "AssinePro", "Assinador Digital")]
    dire = [(690, 110, "Gestão de Passivo Empresarial", ""), (900, 380, "Sustentabilidade e EVP", ""), (900, 690, "Consultoria Tributária", ""), (710, 900, "RecuperaTax SaaS", "Mercado Tributário")]
    corpo = (f'<div style="position:absolute;left:80px;top:70px;width:1700px"><div class="rot" style="margin-bottom:16px">{esc(s["rotulo"])}</div><h1 style="font-size:58px">{esc(s["titulo"])}</h1></div>'
             f'<div class="foto" style="left:{left}px;top:{top}px;width:{Wd}px;height:{round(Wd * 2048 / 2032)}px;background-size:100% 100%;{foto_css("roda-completa")}"></div>')
    svg = f'<svg style="position:absolute;left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080">'
    lab = ""
    for lado, itens in (("e", esq), ("d", dire)):
        for x, y, nome, sub in itens:
            px = left + x * k; py = top + y * k
            if lado == "e":
                xe = left - 60; svg += f'<line x1="{xe}" y1="{py}" x2="{px}" y2="{py}" stroke="{OURO}" stroke-opacity=".55" stroke-width="1.4"/><circle cx="{px}" cy="{py}" r="5" fill="{OURO}"/>'
                lab += (f'<div style="position:absolute;right:{1920 - xe + 18}px;top:{py - 28}px;text-align:right;width:420px"><div style="font-size:26px;font-weight:500;color:#F2F2F2">{esc(nome)}</div>'
                        f'<div style="font-size:20px;color:#A9A9A9;margin-top:2px">{esc(sub)}</div></div>')
            else:
                xe = left + Wd + 60; svg += f'<line x1="{px}" y1="{py}" x2="{xe}" y2="{py}" stroke="{OURO}" stroke-opacity=".55" stroke-width="1.4"/><circle cx="{px}" cy="{py}" r="5" fill="{OURO}"/>'
                lab += (f'<div style="position:absolute;left:{xe + 18}px;top:{py - 28}px;width:420px"><div style="font-size:26px;font-weight:500;color:#F2F2F2">{esc(nome)}</div>'
                        f'<div style="font-size:20px;color:#A9A9A9;margin-top:2px">{esc(sub)}</div></div>')
    return pagina(corpo + svg + "</svg>" + lab, n, tot, s.get("leg", RODAPE))


def fluxo_html(img=None):
    """Fluxograma imponente (sem fotos): emblema Save -> três pilares (Partners, Save Co., Educação); a Save Co. em quatro camadas de serviços.
    Só divs, para servir também de artboard."""
    O = OURO; G = f"linear-gradient(90deg,{O},#FFF1BF)"
    sim = uri(PADRAO / M["logos"]["simbolo_ouro"])
    def lin(x, y, w, hh, op=.8): return f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{hh}px;background:{G};opacity:{op};box-shadow:0 0 14px rgba(243,205,96,.55)"></div>'
    def pto(x, y, r=7): return f'<div style="position:absolute;left:{x - r}px;top:{y - r}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;background:{O};box-shadow:0 0 0 6px rgba(243,205,96,.18),0 0 22px rgba(243,205,96,.8)"></div>'
    h = ""
    # emblema
    cx, cy = 960, 212
    for rr, op in ((84, .10), (66, .2), (50, .55)):
        h += f'<div style="position:absolute;left:{cx - rr}px;top:{cy - rr}px;width:{2 * rr}px;height:{2 * rr}px;border-radius:50%;border:1.5px solid {O};opacity:{op}"></div>'
    h += (f'<div style="position:absolute;left:{cx - 42}px;top:{cy - 42}px;width:84px;height:84px;border-radius:50%;background:radial-gradient(circle,rgba(243,205,96,.22),rgba(0,0,0,.9));'
          f'box-shadow:0 0 70px rgba(243,205,96,.35);display:flex;align-items:center;justify-content:center"><img src="{sim}" style="width:52px"></div>')
    # barramento
    h += lin(960, 300, 2, 40) + lin(270, 300, 1380, 2) + lin(270, 300, 2, 40) + lin(1650, 300, 2, 40) + pto(271, 301) + pto(961, 301) + pto(1651, 301)
    h += f'<div style="position:absolute;left:{cx - 1}px;top:{cy + 84}px;width:2px;height:{300 - cy - 84}px;background:{G};opacity:.8;box-shadow:0 0 14px rgba(243,205,96,.55)"></div>'
    # pilares laterais
    def lateral(x, nome, lema, texto, pontos):
        b = "".join(f'<div style="display:flex;align-items:center;gap:14px;padding:13px 0;border-top:1px solid rgba(243,205,96,.18);font-size:23px;color:#EDEDED"><span style="flex:none;width:9px;height:9px;background:{O};transform:rotate(45deg)"></span>{p}</div>' for p in pontos)
        return (f'<div style="position:absolute;left:{x}px;top:340px;width:380px;height:630px;box-sizing:border-box;border:1px solid rgba(243,205,96,.4);border-radius:26px;padding:34px 34px;'
                f'background:linear-gradient(180deg,rgba(243,205,96,.09),rgba(255,255,255,.015) 45%,rgba(0,0,0,.3));box-shadow:0 30px 60px rgba(0,0,0,.6)">'
                f'<div style="position:absolute;left:34px;top:-1px;width:90px;height:4px;background:{G};border-radius:2px"></div>'
                f'<div style="font-size:44px;font-weight:300;color:#F7F7F7;line-height:1.1">{nome}</div><div style="font-size:21px;color:{O};letter-spacing:.03em;margin:8px 0 22px">{lema}</div>'
                f'<div style="font-size:23px;line-height:1.5;color:#C9C9C9;margin-bottom:26px">{texto}</div>{b}</div>')
    h += lateral(80, "Save Partners", "Alianças estratégicas", "A força das relações estratégicas: alianças que geram negócios e multiplicam resultados.", ["Negócios compartilhados", "Oportunidades em rede", "Resultados multiplicados"])
    h += lateral(1460, "Save Educação", "Conhecimento que transforma", "Converte saber em ação, unindo teoria e prática para formar mentes que decidem e fazem acontecer.", ["Teoria e prática", "Mentes que decidem", "Saber que vira ação"])
    # conectores laterais
    h += lin(460, 655, 60, 2) + lin(1400, 655, 60, 2) + pto(460, 656, 6) + pto(1460, 656, 6)
    # pilar central
    h += (f'<div style="position:absolute;left:520px;top:340px;width:880px;height:650px;box-sizing:border-box;border:2px solid {O};border-radius:30px;'
          f'background:linear-gradient(180deg,rgba(243,205,96,.15),rgba(255,255,255,.02) 38%,rgba(0,0,0,.35));box-shadow:0 0 90px rgba(243,205,96,.22),0 40px 80px rgba(0,0,0,.7)">'
          f'<div style="position:absolute;left:44px;top:-2px;width:130px;height:5px;background:{G};border-radius:3px"></div>'
          f'<div style="position:absolute;left:44px;top:26px;display:flex;align-items:baseline;gap:22px"><span style="font-size:56px;font-weight:300;color:#fff;letter-spacing:-.01em">Save Co.</span>'
          f'<span style="font-size:23px;color:{O};letter-spacing:.03em">Dados, tecnologia e serviços</span></div></div>')
    grupos = [("01", "Recuperar", "caixa e crédito", ["Recuperação Tributária", "Gestão de Passivo", "Gestão de Contas"]),
              ("02", "Organizar", "estrutura e segurança", ["Planejamento Tributário", "Estruturação Patrimonial", "Assessoria Jurídica"]),
              ("03", "Crescer", "estratégia e futuro", ["Planejamento Estratégico", "Sustentabilidade e EVP"]),
              ("04", "Tecnologia", "ferramentas Save", ["Save ID", "AssinePro", "RecuperaTax SaaS"])]
    y0, alt, gap = 434, 126, 8
    for i, (num, nome, sub, itens) in enumerate(grupos):
        y = y0 + i * (alt + gap)
        chips = "".join(f'<span style="padding:8px 15px;border:1px solid rgba(243,205,96,.5);border-radius:22px;font-size:19.5px;color:#F7F7F7;background:rgba(243,205,96,.08)">{c}</span>' for c in itens)
        h += (f'<div style="position:absolute;left:548px;top:{y}px;width:824px;height:{alt}px;box-sizing:border-box;display:flex;align-items:center;gap:20px;border-radius:20px;padding:0 22px;'
              f'background:linear-gradient(90deg,rgba(255,255,255,.07),rgba(255,255,255,.015));border:1px solid rgba(255,255,255,.08)">'
              f'<div style="flex:none;width:92px;font-family:\'IBM Plex Mono\',monospace;font-size:62px;line-height:1;color:transparent;-webkit-text-stroke:1.6px {O}">{num}</div>'
              f'<div style="flex:none;width:170px"><div style="font-size:32px;font-weight:500;color:#fff">{nome}</div><div style="font-size:17px;color:{O};letter-spacing:.04em;margin-top:4px">{sub}</div></div>'
              f'<div style="flex:1;display:flex;flex-wrap:wrap;gap:8px">{chips}</div></div>')
    return h


def fluxo_produtos(s, n, tot):
    corpo = (f'<div style="position:absolute;left:0;top:0;width:1920px;height:1080px;background:radial-gradient(ellipse at 50% 28%,#1a1509 0%,#070604 50%,#000 80%)"></div>'
             f'<img src="{uri(PADRAO / M["logos"]["simbolo_contorno_ouro"])}" style="position:absolute;right:-120px;bottom:-110px;width:640px;opacity:.05">'
             f'<div style="position:absolute;left:80px;top:56px;width:740px"><div class="rot" style="margin-bottom:12px">{esc(s["rotulo"])}</div><h1 style="font-size:44px">{esc(s["titulo"])}</h1></div>' + fluxo_html())
    return pagina(corpo, n, tot, s.get("leg", RODAPE))


def conceito(s, n, tot):
    """Slide desenhado como módulo Python em <pasta>/conceitos/<modulo>.py (função corpo(n, tot) devolve a página completa)."""
    import importlib.util
    sys.path.insert(0, str(AQUI))
    p = Path(PASTA_DECK[0]) / "conceitos" / f"{s['modulo']}.py"
    spec = importlib.util.spec_from_file_location("conceito_" + s["modulo"], p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.corpo(n, tot)


PASTA_DECK = [Path(".")]
def capa_cliente(s, n, tot):
    """Capa só com o nome da empresa e a logo dela, centralizados, sobre preto com brilho dourado suave."""
    logo = ""
    if s.get("logo") and (AQUI / s["logo"]).exists():
        logo = f'<img src="{uri(AQUI / s["logo"])}" style="display:block;margin:0 auto 44px;height:{s.get("logo_h", 140)}px">'
    corpo = (f'<div style="position:absolute;inset:0;background:radial-gradient(ellipse at 50% 46%,#1b1608 0%,#070604 50%,#000 78%)"></div>'
             f'<div style="position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);text-align:center">{logo}'
             f'<div style="font-size:{s.get("nome_px", 120)}px;font-weight:300;letter-spacing:-.02em;color:#F5F5F5;line-height:1.05">{esc(s["nome"])}</div>'
             f'<div style="width:120px;height:3px;background:{OURO};margin:44px auto 0;border-radius:2px"></div></div>')
    return pagina(corpo, n, tot, rodape=False)


def capa_logos(s, n, tot):
    """Capa no fundo padrão (foto do prédio à direita): só a logo da Save e a logo do cliente."""
    cli = uri(AQUI / s["logo"])
    corpo = (f'<div class="foto" style="right:0;top:0;width:820px;height:1080px;{foto_css(s.get("foto", "predio"), "center")}"></div>'
             f'<div style="position:absolute;right:0;top:0;width:820px;height:1080px;background:linear-gradient(90deg,#000 0%,rgba(0,0,0,.0) 45%)"></div>'
             f'<img src="{uri(PADRAO / M["logos"]["fundo_escuro"])}" style="position:absolute;left:80px;top:70px;width:250px">'
             f'<img src="{cli}" style="position:absolute;left:80px;top:50%;transform:translateY(-50%);width:{s.get("logo_w", 640)}px">'
             f'<div style="position:absolute;left:80px;bottom:110px;width:140px;height:5px;background:{OURO}"></div>')
    return pagina(corpo, n, tot, rodape=False)


TIPOS = {"capa_logos": capa_logos, "capa_cliente": capa_cliente, "conceito": conceito, "fluxo_produtos": fluxo_produtos, "ecossistema": ecossistema, "painel": painel, "valores": valores, "lateral": lateral, "capa": capa, "numeros": numeros, "grade": grade, "banner": banner, "timeline": timeline, "roadmap": roadmap, "case": case, "passos": passos}


def main(pasta, nome=None):
    from playwright.sync_api import sync_playwright
    pasta = Path(pasta).resolve(); PASTA_DECK[0] = pasta; deck = json.load(open(pasta / "deck.json")); sl = deck["slides"]; tot = len(sl)
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
            pg.wait_for_timeout(250); pg.screenshot(path=str(dest), type="jpeg", quality=93); pngs.append(str(dest)); notas.append((s.get("notas", "") + (f"\n\n[Legenda retirada da tela; manter como aviso oral/escrito quando houver envio] {s['leg']}" if s.get("leg") else "")).strip())
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
