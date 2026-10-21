#!/usr/bin/env python3
"""Apresentação Santa Clara no layout da apresentação institucional da Save (01. Save Co..pptx): fundo preto, frases grandes em peso leve,
fotos em preto e branco, rótulos em ouro, logo no rodapé. Só as fotos de fundo são trocadas (campo, vacas, unidades da cooperativa).
Uso: python3 render_ppt.py [pasta]   (pasta padrão: departamentos/tributario/apresentacao-diagnostico/santa-clara/ppt; precisa de fotos/)"""
import base64, json, os, subprocess, sys
from pathlib import Path

RAIZ = Path.home() / "agentes-partners"
PAD = RAIZ / "departamentos/marketing-marca/padrao"
APR = RAIZ / "departamentos/tributario/apresentacao-diagnostico"
PASTA = Path(sys.argv[1]) if len(sys.argv) > 1 else APR / "santa-clara/ppt"
OURO, TXT, CIN = "#F3CD60", "#F2F2F0", "#A8A8A8"
M = json.load(open(PAD / "marca.json"))


def uri(p):
    p = Path(p); t = {"png": "image/png", "jpg": "image/jpeg", "ttf": "font/ttf"}[p.suffix[1:].lower()]
    return f"data:{t};base64," + base64.b64encode(p.read_bytes()).decode()


def css():
    f = "".join(f"@font-face{{font-family:'IBM Plex Sans';font-weight:{w};src:url({uri(PAD / 'fontes' / n)})}}" for n, w in
                [("IBMPlexSans-Light.ttf", 300), ("IBMPlexSans-Regular.ttf", 400), ("IBMPlexSans-Medium.ttf", 500)])
    return f + f"""*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1920px;height:1080px;background:#000;color:{TXT};font-family:'IBM Plex Sans',sans-serif;position:relative;overflow:hidden}}
.foto{{position:absolute;background-size:cover;background-position:center;filter:grayscale(1) contrast(1.05)}}
h1{{font-weight:300;line-height:1.08;letter-spacing:-.01em;color:{TXT}}}
.ouro{{color:{OURO}}} .cin{{color:{CIN}}}
.rod{{position:absolute;left:80px;bottom:44px;height:34px}} .pg{{position:absolute;right:80px;bottom:50px;font-size:20px;color:{CIN}}}
.fonte{{position:absolute;left:330px;right:200px;bottom:48px;font-size:17px;line-height:1.3;color:#8a8a8a}}
.reg{{position:absolute;left:80px;right:80px;height:1px;background:#4a4742}}"""


def foto(nome, estilo="left:0;top:0;width:1920px;height:1080px", pos="center", br=.5):
    return f'<div class="foto" style="{estilo};background-image:url({uri(PASTA / "fotos" / nome)});background-position:{pos};filter:grayscale(1) brightness({br}) contrast(1.05)"></div>'


def pagina(corpo, n, tot, fonte="", rodape=True):
    r = ""
    if rodape:
        r = f'<img class="rod" src="{uri(PAD / M["logos"]["fundo_escuro"])}"><div class="pg">{n:02d}/{tot:02d}</div>'
        if fonte: r += f'<div class="fonte">{fonte}</div>'
    return f"<!doctype html><meta charset=utf-8><style>{css()}</style><body>{corpo}{r}</body>"


def capa(s, n, tot):
    c = (foto(s["foto"], "left:0;top:0;width:845px;height:1080px", br=.8) +
         f'<img src="{uri(PAD / M["logos"]["fundo_escuro"])}" style="position:absolute;left:1000px;top:210px;width:380px">'
         f'<h1 style="position:absolute;left:1000px;top:360px;width:800px;font-size:72px">{s["titulo"]}</h1>'
         f'<div class="reg" style="left:1000px;top:640px"></div>'
         f'<div style="position:absolute;left:1000px;top:672px;width:560px;font-size:24px;line-height:1.35;color:{TXT}">{s["sub"]}</div>'
         f'<img src="{uri(PASTA / "fotos/logo-santa-clara.png")}" style="position:absolute;right:80px;bottom:70px;width:210px">')
    return pagina(c, n, tot, rodape=False)


def frase(s, n, tot):
    c = foto(s["foto"], pos=s.get("pos", "center"), br=s.get("br", .42))
    c += '<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.72) 0%,rgba(0,0,0,.25) 65%,rgba(0,0,0,.05) 100%)"></div>'
    c += f'<h1 style="position:absolute;left:80px;top:{s.get("top", 250)}px;width:{s.get("w", 1000)}px;font-size:{s.get("fs", 96)}px">{s["titulo"]}</h1>'
    if s.get("linhas"):
        for i, (rot, tx) in enumerate(s["linhas"]):
            x = 80 + i * 590
            c += (f'<div style="position:absolute;left:{x}px;top:600px;width:540px"><div style="font-size:24px;color:{OURO};letter-spacing:.02em">{rot}</div>'
                  f'<div style="margin-top:12px;font-size:29px;line-height:1.35;color:{TXT}">{tx}</div></div>')
    if s.get("numero"):
        c += (f'<div style="position:absolute;left:80px;bottom:190px;width:1400px"><div style="font-size:150px;font-weight:300;line-height:1;color:{TXT}">{s["numero"]}'
              f'<span class="ouro" style="font-size:44px;margin-left:16px">{s.get("unidade", "")}</span></div>'
              f'<div style="margin-top:14px;font-size:27px;color:{OURO}">{s["legenda"]}</div></div>')
    return pagina(c, n, tot, s.get("fonte", ""))


def espelho(s, n, tot):
    c = f'<h1 style="position:absolute;left:80px;top:90px;width:1500px;font-size:88px">{s["titulo"]}</h1><div class="reg" style="top:400px"></div>'
    for i, (a, b) in enumerate(s["itens"]):
        y = 440 + i * 96
        c += (f'<div style="position:absolute;left:80px;top:{y}px;width:520px;font-size:27px;color:{OURO};line-height:1.3">{a}</div>'
              f'<div style="position:absolute;left:640px;top:{y}px;width:1160px;font-size:30px;color:{TXT};line-height:1.3">{b}</div>')
    return pagina(c, n, tot, s.get("fonte", ""))


def frente(s, n, tot):
    c = (f'<h1 style="position:absolute;left:80px;top:80px;width:1500px;font-size:92px">{s["titulo"]}</h1><div class="reg" style="top:420px"></div>'
         f'<div style="position:absolute;left:80px;top:460px;width:400px;font-size:27px;line-height:1.4;color:{TXT}">{s["intro"]}</div>')
    for i, (a, b) in enumerate(s["itens"]):
        x = 520 + (i % 2) * 640; y = 460 + (i // 2) * 200
        c += (f'<div style="position:absolute;left:{x}px;top:{y}px;width:240px;font-size:28px;line-height:1.25;color:{OURO}">{a}</div>'
              f'<div style="position:absolute;left:{x + 250}px;top:{y}px;width:330px;font-size:25px;line-height:1.4;color:{TXT}">{b}</div>')
    c += f'<div style="position:absolute;left:80px;top:900px;width:1700px;font-size:26px;color:{CIN}">{s.get("nota", "")}</div>'
    return pagina(c, n, tot, s.get("fonte", ""))


def numeros(s, n, tot):
    c = f'<h1 style="position:absolute;left:80px;top:70px;width:1600px;font-size:72px">{s["titulo"]}</h1><div class="reg" style="top:250px"></div>'
    for i, (v, cap, sub) in enumerate(s["itens"]):
        x = 80 + (i % 4) * 450; y = 290 + (i // 4) * 300
        c += (f'<div style="position:absolute;left:{x}px;top:{y}px;width:420px"><div style="font-size:{s.get("fs", 88)}px;font-weight:300;line-height:1;color:{TXT};white-space:nowrap">{v}</div>'
              f'<div style="margin-top:14px;font-size:26px;line-height:1.25;color:{OURO}">{cap}</div>'
              f'<div style="margin-top:8px;font-size:21px;line-height:1.3;color:{CIN}">{sub}</div></div>')
    return pagina(c, n, tot, s.get("fonte", ""))


def fim(s, n, tot):
    c = (f'<img src="{uri(PAD / M["logos"]["fundo_escuro"])}" style="position:absolute;left:160px;top:330px;width:360px">'
         f'<img src="{uri(PASTA / "fotos/logo-santa-clara.png")}" style="position:absolute;left:620px;top:300px;width:200px">'
         f'<div class="reg" style="top:500px"></div>'
         f'<div style="position:absolute;left:160px;top:530px;width:520px;font-size:30px;line-height:1.4">{s["a"]}</div>'
         f'<div style="position:absolute;left:760px;top:530px;width:480px;font-size:30px;line-height:1.4">{s["b"]}</div>'
         f'<div style="position:absolute;left:1300px;top:530px;width:480px;font-size:30px;line-height:1.4">{s["c"]}</div>')
    return pagina(c, n, tot, rodape=False)


def fontes(s, n, tot):
    c = f'<h1 style="position:absolute;left:80px;top:80px;font-size:70px">Fontes e avisos</h1><div class="reg" style="top:230px"></div>'
    c += f'<div style="position:absolute;left:80px;top:260px;width:1760px;font-size:22px;line-height:1.5;color:{CIN}">{s["texto"]}</div>'
    return pagina(c, n, tot)


T = {"numeros": numeros, "capa": capa, "frase": frase, "espelho": espelho, "frente": frente, "fim": fim, "fontes": fontes}


def main():
    from playwright.sync_api import sync_playwright
    sl = json.load(open(PASTA.parent / "deck_ppt.json"))["slides"]; tot = len(sl)
    prev = PASTA / "previas"; prev.mkdir(exist_ok=True); pngs = []; notas = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome"); pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
        for i, s in enumerate(sl, 1):
            pg.set_content(T[s["tipo"]](s, i, tot)); pg.wait_for_timeout(250)
            d = prev / f"{i:02d}.jpg"; pg.screenshot(path=str(d), type="jpeg", quality=93); pngs.append(str(d)); notas.append(s.get("notas", ""))
        b.close()
    json.dump({"imagens": pngs, "notas": notas}, open(PASTA / "_pptx.json", "w"), ensure_ascii=False)
    sys.path.insert(0, str(APR)); import gerar_apresentacao as g
    r = subprocess.run(["node", str(APR / "pptx_imagens.js"), str(PASTA / "_pptx.json"), str(PASTA / "Santa-Clara-Apresentacao-PPT.pptx")], env={**os.environ, "NODE_PATH": g.achar_node_path()}, capture_output=True, text=True)
    os.remove(PASTA / "_pptx.json"); print(tot, "slides", "OK" if r.returncode == 0 else r.stderr[-300:])


if __name__ == "__main__":
    main()
