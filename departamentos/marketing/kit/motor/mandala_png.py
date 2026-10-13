#!/usr/bin/env python3
"""Gera o PNG da mandala de um slide (usado pelo deck_pptx.js). Uso: mandala_png.py conteudo.json indice_slide saida.png"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent))
import deck_html  # noqa: E402

doc = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
svg = deck_html.mandala_svg(doc["slides"][int(sys.argv[2])], 500)
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome"); pg = b.new_page(device_scale_factor=3)
    pg.set_content(f"<body style='margin:0;background:transparent'><div id='m' style='display:inline-block'>{svg}</div></body>")
    pg.wait_for_timeout(200); pg.locator("#m").screenshot(path=sys.argv[3], omit_background=True); b.close()
print("ok", sys.argv[3])
