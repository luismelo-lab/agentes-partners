#!/usr/bin/env python3
"""Extrai da apresentação institucional da Save (PowerPoint) as imagens na resolução original do arquivo.

Uso: python3 extrair_assets_pptx.py "<caminho>/01. Save Co..pptx"
Saída em assets-institucionais/: fotos recortadas (predio, colmeia, pessoas, relogio, edificio, maos, escada), recortes do círculo do
ecossistema (casa, time, reuniao, plantas, certificado, assinatura, investidores, grafico) e slides prontos em slides/
(save, ecossistema, case-alimenticio, encerramento).
Cada slide do PowerPoint é uma imagem 1920x1080; o ecossistema é montado a partir da foto do círculo (2032x2048) e dos rótulos em PNG.
Se o Luis enviar uma versão com resolução maior, basta rodar de novo: os recortes são por fração do slide."""
import base64, re, shutil, sys, zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "assets-institucionais"
EMU_W, EMU_H = 9144000, 5143500

# slide do PowerPoint -> (nome, x0, y0, x1, y1) em fração do slide
FOTOS = {2: ("predio", 0, 0, .44, 1), 3: ("colmeia", 0, 0, .44, 1), 4: ("pessoas", 0, 0, .44, 1), 7: ("relogio", 0, .3, 1, .9),
         16: ("maos", .42, 0, 1, .92), 23: ("escada", .72, 0, 1, 1)}
# recortes do círculo (px da imagem 2032x2048)
RODA = {"casa": (60, 600, 560, 980), "time": (540, 50, 980, 520), "reuniao": (1120, 60, 1560, 500), "plantas": (1520, 600, 1940, 960),
        "certificado": (60, 1080, 500, 1560), "assinatura": (420, 1500, 960, 1960), "investidores": (1520, 1080, 2000, 1520), "grafico": (1190, 1600, 1620, 1990), "completa": (0, 0, 2032, 2048), "logo-partners": (640, 825, 1380, 925), "logo-educacao": (620, 1105, 1400, 1235)}
SLIDES = {2: "save.jpg", 19: "case-alimenticio.jpg", 24: "encerramento.jpg"}


def uri(p):
    t = "image/png" if str(p).endswith("png") else "image/jpeg"
    return f"data:{t};base64," + base64.b64encode(Path(p).read_bytes()).decode()


def mapa_slides(z):
    """slide n -> lista de (imagem, off, ext, srcRect) na ordem do XML"""
    out = {}
    n = len([x for x in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", x)])
    for i in range(1, n + 1):
        xml = z.read(f"ppt/slides/slide{i}.xml").decode(); rel = z.read(f"ppt/slides/_rels/slide{i}.xml.rels").decode()
        rid = {}
        for m in re.finditer(r"<Relationship [^>]*>", rel):
            a = m.group(0); r = re.search(r'Id="(rId\d+)"', a); t = re.search(r'Target="\.\./media/([^"]+)"', a)
            if r and t: rid[r.group(1)] = t.group(1)
        pics = []
        bg = re.search(r"<p:bg>.*?r:embed=\"(rId\d+)\".*?</p:bg>", xml, re.S)
        if bg and bg.group(1) in rid: pics.append((rid[bg.group(1)], (0, 0), (EMU_W, EMU_H), {}))
        for pm in re.finditer(r"<p:pic>.*?</p:pic>", xml, re.S):
            b = pm.group(0); e = re.search(r'r:embed="(rId\d+)"', b)
            if not e or e.group(1) not in rid: continue
            off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"', b).groups(); ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"', b).groups()
            sr = re.search(r"<a:srcRect([^/]*)/>", b); crop = {k: int(v) / 100000 for k, v in re.findall(r'(\w)="(-?\d+)"', sr.group(1))} if sr else {}
            pics.append((rid[e.group(1)], tuple(map(int, off)), tuple(map(int, ext)), crop))
        out[i] = pics
    return out


def main(pptx):
    from playwright.sync_api import sync_playwright
    tmp = AQUI / "_pptx"; shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir()
    z = zipfile.ZipFile(pptx); z.extractall(tmp); sl = mapa_slides(z)
    (SAIDA / "slides").mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")

        def shot(html, w, h, dest, scale=1, clip=None, jpeg=True):
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
            pg.set_content(f"<body style='margin:0;background:#000'>{html}"); pg.wait_for_timeout(400)
            kw = {"type": "jpeg", "quality": 95} if jpeg else {}
            pg.screenshot(path=str(dest), clip=clip, **kw); pg.close()

        def montar(i, w=1920):
            k = w / EMU_W; h = round(EMU_H * k); s = ""
            for img, (x, y), (cx, cy), cr in sl[i]:
                if y > EMU_H or y + cy < 0 or x > EMU_W or x + cx < 0: continue
                l, t, r, bt = (cr.get(q, 0) for q in "ltrb")
                fw, fh = 1 - l - r, 1 - t - bt
                s += (f"<div style='position:absolute;left:{x * k}px;top:{y * k}px;width:{cx * k}px;height:{cy * k}px;overflow:hidden'>"
                      f"<img src='{uri(tmp / 'ppt' / 'media' / img)}' style='position:absolute;width:{cx * k / fw}px;height:{cy * k / fh}px;left:{-l / fw * cx * k}px;top:{-t / fh * cy * k}px'></div>")
            return f"<div style='position:relative;width:{w}px;height:{h}px;overflow:hidden;background:#000'>{s}</div>", w, h

        # slides inteiros
        for i, nome in SLIDES.items():
            html, w, h = montar(i, 1920); shot(html, w, h, SAIDA / "slides" / nome, 1)
        html, w, h = montar(10, 3840); shot(html, w, h, SAIDA / "slides" / "ecossistema.jpg", 1)   # rótulos em PNG de 2048 px: 2x
        # fotos recortadas (na resolução do arquivo)
        for i, (nome, x0, y0, x1, y1) in FOTOS.items():
            html, w, h = montar(i, 1920)
            shot(html, w, h, SAIDA / f"{nome}.jpg", 1, clip={"x": x0 * w, "y": y0 * h, "width": (x1 - x0) * w, "height": (y1 - y0) * h})
        # recortes do círculo
        roda = [m for m in sl[10] if m[0] == "image35.png"][0][0]
        for nome, (x0, y0, x1, y1) in RODA.items():
            html = f"<img src='{uri(tmp / 'ppt' / 'media' / roda)}' style='position:absolute;left:0;top:0;width:2032px;height:2048px'>"
            shot(html, 2032, 2048, SAIDA / f"roda-{nome}.jpg", 1, clip={"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0})
        b.close()
    shutil.rmtree(tmp, ignore_errors=True)
    # amplia 2x (Lanczos + nitidez leve) o que veio em 1920 px; o PowerPoint recebido não tem resolução maior
    import subprocess
    sw = AQUI / "ampliar.swift"; exe = Path("/tmp/ampliar_save")
    if sw.exists():
        subprocess.run(["swiftc", "-O", str(sw), "-o", str(exe)], check=False, capture_output=True)
        if exe.exists(): subprocess.run([str(exe)] + [str(x) for x in list(SAIDA.glob("*.jpg")) + list((SAIDA / "slides").glob("*.jpg"))], check=False)
    print("ok:", ", ".join(sorted(x.name for x in SAIDA.glob("*.jpg"))), "| slides:", ", ".join(sorted(x.name for x in (SAIDA / "slides").glob("*.jpg"))))


if __name__ == "__main__":
    main(sys.argv[1])
