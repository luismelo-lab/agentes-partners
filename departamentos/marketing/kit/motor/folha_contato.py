#!/usr/bin/env python3
"""Folha de contato das prévias (conferência visual de vários slides de uma vez).
Uso: python3 folha_contato.py pasta_previas saida.png [colunas] [largura_miniatura]"""
import base64, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

pasta, saida = Path(sys.argv[1]), sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 3
lw = int(sys.argv[4]) if len(sys.argv) > 4 else 640
fs = sorted(pasta.glob("*.png"))
imgs = "".join(f"<img style='width:{lw}px;display:block' src='data:image/png;base64,{base64.b64encode(f.read_bytes()).decode()}'>" for f in fs)
h = f"<body style='margin:0;background:#666;display:grid;grid-template-columns:repeat({cols},{lw}px);gap:6px;width:{cols * lw + (cols - 1) * 6}px'>{imgs}</body>"
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": cols * lw + (cols - 1) * 6, "height": 300})
    pg.set_content(h); pg.wait_for_timeout(200); pg.screenshot(path=saida, full_page=True); b.close()
print("ok", saida, len(fs))
