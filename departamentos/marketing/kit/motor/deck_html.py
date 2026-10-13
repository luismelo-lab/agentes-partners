#!/usr/bin/env python3
"""Apresentação Save (16:9) a partir de um conteúdo JSON → HTML → PDF, no Design System Save v0.5.
O mesmo JSON gera o PowerPoint editável em deck_pptx.js. Tipos de slide: veja TIPOS abaixo e o LEIA-ME.md.
Uso: python3 deck_html.py conteudo.json saida.pdf [pasta_previas]
Só gera arquivos locais. Não envia nada."""
import html, json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path.home() / "agentes-partners/lib"))
import marca  # noqa: E402

C, E = marca.C, marca.E
W, H = 1280, 720
LOGO_C, LOGO_E = marca.logo_uri("fundo_claro"), marca.logo_uri("fundo_escuro")
BASE = [Path('.')]  # pasta do JSON (imagens de slides do tipo mapa)
PARC = {}  # logo do parceiro (co-branding), preenchido em gerar() a partir de doc["parceiro"]


def marcas(esc=False, capa=False):
    """Logo Save e, se houver, o logo do parceiro ao lado (co-branding)."""
    save = LOGO_E if esc else LOGO_C
    if not PARC: return f'<img class="logo" src="{save}">'
    par = PARC["escuro"] if esc else PARC["claro"]
    cls = "marcas capa-m" if capa else "marcas"
    return f'<div class="{cls}"><img src="{par}" class="plogo"><span class="xsep"></span><img src="{save}" class="svlogo"></div>'
CONTORNO = marca.logo_uri("simbolo_contorno_ouro")


def t(s):
    """Texto com **negrito** e quebras; o resto escapado."""
    s = html.escape(str(s or ""))
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s).replace("\n", "<br>")


CSS = f"""
@page {{ size: {W}px {H}px; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ background: #888; }}
body {{ font-family: {marca.SANS}; -webkit-font-smoothing: antialiased; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.s {{ width: {W}px; height: {H}px; position: relative; overflow: hidden; background: #FFFFFF; color: {C['texto']};
      padding: 56px 72px 0; page-break-after: always; display: flex; flex-direction: column; }}
.s.esc {{ background: {E['fundo']}; color: {E['texto']}; }}
b {{ font-weight: 600; }}
.logo {{ position: absolute; top: 50px; right: 72px; height: 22px; }}
.rot {{ font: 500 12px/1 {marca.MONO}; letter-spacing: 2.4px; text-transform: uppercase; color: {C['ouro_texto']};
        display: flex; align-items: center; gap: 10px; }}
.rot::before {{ content: ""; width: 8px; height: 8px; background: {C['ouro']}; display: inline-block; }}
.esc .rot {{ color: {E['ouro']}; }}
h1 {{ font-weight: 500; font-size: 40px; line-height: 1.14; letter-spacing: -0.6px; margin-top: 16px; max-width: 1136px; text-wrap: balance; }}
.sub {{ text-wrap: pretty; font-size: 19px; line-height: 1.5; color: {C['texto_2']}; margin-top: 14px; max-width: 900px; }}
.esc .sub {{ color: {E['texto_2']}; }}
.corpo {{ flex: 1; min-height: 0; margin-top: 24px; padding-bottom: 28px; display: flex; flex-direction: column; justify-content: safe center; }}
.rod {{ height: 48px; margin-top: auto; border-top: 1px solid {C['borda']}; display: flex; align-items: center;
        justify-content: space-between; gap: 24px; font-size: 10px; color: {C['texto_3']}; }}
.esc .rod {{ border-top-color: {E['borda']}; color: {E['texto_3']}; }}
.rod .pg {{ font: 500 11px/1 {marca.MONO}; color: {C['ouro_texto']}; white-space: nowrap; }}
.esc .rod .pg {{ color: {E['ouro']}; }}
.nota {{ font-size: 13px; line-height: 1.45; color: {C['texto_3']}; margin-top: 14px; }}
.esc .nota {{ color: {E['texto_3']}; }}
.fonte {{ font: 400 11.5px/1.4 {marca.MONO}; color: {C['texto_3']}; margin-top: 8px; }}
.marcad {{ position: absolute; right: -150px; bottom: -190px; width: 620px; opacity: .22; pointer-events: none; }}

.marcas {{ position: absolute; top: 46px; right: 72px; display: flex; align-items: center; gap: 16px; }}
.marcas .plogo {{ height: 24px; }} .marcas .svlogo {{ height: 22px; }}
.marcas .xsep {{ width: 1px; height: 24px; background: {C['borda_3']}; }}
.esc .marcas .xsep {{ background: {E['borda']}; }}
.capa .marcas {{ position: static; align-self: flex-start; gap: 22px; }}
.capa .marcas .plogo {{ height: 34px; }} .capa .marcas .svlogo {{ height: 30px; }} .capa .marcas .xsep {{ height: 34px; }}

/* ---------- ferramentas de consultoria ---------- */
/* cascata (waterfall) */
.wf {{ position: relative; height: 380px; display: flex; align-items: stretch; gap: 14px; border-bottom: 1px solid {C['borda_3']}; margin-top: 10px; }}
.wf .c {{ flex: 1; position: relative; }}
.wf .b {{ position: absolute; left: 8%; right: 8%; }}
.wf .b.base, .wf .b.total {{ background: {C['texto']}; }}
.wf .b.pos {{ background: {C['ouro']}; }}
.wf .b.neg {{ background: {C['borda_3']}; }}
.wf .v {{ position: absolute; left: 0; right: 0; text-align: center; font: 500 15px/1 {marca.MONO}; color: {C['texto']}; }}
.wf .lk {{ position: absolute; height: 0; border-top: 1px dashed {C['texto_3']}; }}
.wfl {{ display: flex; gap: 14px; margin-top: 10px; }}
.wfl div {{ flex: 1; text-align: center; font-size: 13.5px; line-height: 1.3; color: {C['texto_2']}; }}
.wfl div.t {{ font-weight: 600; color: {C['texto']}; }}
/* matriz 2x2 */
.mx {{ display: grid; grid-template-columns: 34px 1fr; grid-template-rows: 1fr 30px; height: 440px; margin-top: 6px; }}
.mx .ey {{ writing-mode: vertical-rl; transform: rotate(180deg); font: 500 11px/1 {marca.MONO}; letter-spacing: 1.5px; text-transform: uppercase; color: {C['texto_2']}; text-align: center; display: flex; justify-content: space-between; }}
.mx .ex {{ grid-column: 2; font: 500 11px/1 {marca.MONO}; letter-spacing: 1.5px; text-transform: uppercase; color: {C['texto_2']}; display: flex; justify-content: space-between; align-items: center; }}
.mx .pl {{ position: relative; border-left: 2px solid {C['texto']}; border-bottom: 2px solid {C['texto']}; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; }}
.mx .q {{ border: 1px dashed {C['borda_2']}; padding: 12px 14px; font: 500 11px/1.3 {marca.MONO}; letter-spacing: 1px; text-transform: uppercase; color: {C['texto_3']}; }}
.mx .q.hl {{ background: {C['ouro_suave']}; color: {C['ouro_texto']}; }} .mx .q:nth-child(2) {{ text-align: right; }}
.mx .q:nth-child(1), .mx .q:nth-child(3) {{ text-align: left; }} .mx .q:nth-child(4) {{ text-align: right; }}
.mx .q:nth-child(3), .mx .q:nth-child(4) {{ display: flex; align-items: flex-end; }} .mx .q:nth-child(4) {{ justify-content: flex-end; }}
.mx .pt {{ position: absolute; transform: translate(-7px, -7px); display: flex; align-items: center; gap: 8px; white-space: nowrap; }}
.mx .pt i {{ width: 14px; height: 14px; border-radius: 50%; background: {C['texto']}; flex: 0 0 14px; }}
.mx .pt.d i {{ background: {C['ouro']}; box-shadow: 0 0 0 3px {C['texto']}; }}
.mx .pt span {{ font-size: 13.5px; font-weight: 500; background: rgba(255,255,255,.85); padding: 1px 4px; border-radius: 4px; }}
.mx .pt.esq {{ flex-direction: row-reverse; transform: translate(calc(-100% + 7px), -7px); }}
/* mapa de calor */
table.hm {{ width: 100%; border-collapse: separate; border-spacing: 4px; }}
.hm th {{ font: 500 11px/1.3 {marca.MONO}; letter-spacing: 1.2px; text-transform: uppercase; color: {C['texto_2']}; padding: 4px 6px 8px; text-align: center; }}
.hm th.n {{ text-align: left; }}
.hm td {{ font: 500 16px/1.2 {marca.MONO}; text-align: center; padding: 14px 6px; border-radius: 6px; color: {C['texto']}; }}
.hm td.n {{ font: 600 15px/1.3 {marca.SANS}; text-align: left; background: none; padding-left: 0; }}
.hm td.z {{ background: {C['fundo_2']}; color: {C['texto_3']}; }}
.hmleg {{ display: flex; align-items: center; gap: 10px; font-size: 12px; color: {C['texto_3']}; margin-top: 8px; }}
.hmleg .g {{ width: 160px; height: 10px; border-radius: 5px; background: linear-gradient(90deg, rgba(243,205,96,.12), rgba(243,205,96,1)); }}
/* organograma */
.og {{ display: flex; flex-direction: column; align-items: center; margin-top: 4px; }}
.og .rz {{ background: {E['fundo']}; color: {E['texto']}; border-radius: 10px; padding: 12px 28px; text-align: center; }}
.og .rz .tt {{ font-size: 17px; font-weight: 600; }} .og .rz .tx {{ font-size: 12.5px; color: {E['texto_2']}; margin-top: 3px; }}
.og .tr {{ width: 2px; height: 18px; background: {C['ouro']}; }}
.og .gs {{ display: grid; gap: 14px; width: 100%; position: relative; padding-top: 18px; }}
.og .gs::before {{ content: ""; position: absolute; top: 0; left: 10%; right: 10%; height: 2px; background: {C['ouro']}; }}
.og .g {{ position: relative; }}
.og .g::before {{ content: ""; position: absolute; top: -18px; left: 50%; width: 2px; height: 18px; background: {C['ouro']}; }}
.og .gh {{ border-top: 4px solid {C['ouro']}; background: {C['fundo']}; border-radius: 0 0 8px 8px; padding: 10px 12px; }}
.og .gh .tt {{ font-size: 14.5px; font-weight: 600; }} .og .gh .tx {{ font-size: 11.5px; color: {C['texto_2']}; margin-top: 3px; line-height: 1.35; }}
.og .it {{ border: 1px solid {C['borda']}; border-radius: 8px; padding: 8px 10px; margin-top: 7px; }}
.og .it .tt {{ font-size: 12.5px; font-weight: 600; }} .og .it .tx {{ font-size: 11px; color: {C['texto_2']}; line-height: 1.35; margin-top: 2px; }}
/* tabela genérica */
table.tb {{ width: 100%; border-collapse: collapse; }}
.tb th {{ text-align: left; font: 500 11px/1.3 {marca.MONO}; letter-spacing: 1.2px; text-transform: uppercase; color: {C['texto_2']}; padding: 0 12px 10px 0; border-bottom: 1px solid {C['borda_3']}; }}
.tb td {{ font-size: 14px; line-height: 1.38; padding: 11px 12px 11px 0; border-bottom: 1px solid {C['borda']}; vertical-align: top; color: {C['texto_2']}; }}
.tb td:first-child {{ font-weight: 600; color: {C['texto']}; }}
.tb .dc {{ background: {C['ouro_suave']}; color: {C['texto']}; padding-left: 12px; }}
.tb th.dc {{ background: none; color: {C['ouro_texto']}; }}


/* mandala: Save no centro e fases em pétalas (setores de um anel) */
.md {{ display: grid; grid-template-columns: 450px 1fr; gap: 36px; align-items: center; }}
.md svg text {{ font-family: {marca.SANS}; }}
.md .lg .f {{ border-top: 1px solid {C['borda']}; padding: 13px 0; display: grid; grid-template-columns: 34px 1fr; gap: 10px; }}
.md .lg .f:last-child {{ border-bottom: 1px solid {C['borda']}; }}
.md .lg .n {{ font: 500 13px/1.5 {marca.MONO}; color: {C['ouro_texto']}; }}
.md .lg .tt {{ font-size: 17px; font-weight: 600; }}
.md .lg .tx {{ font-size: 14px; line-height: 1.45; color: {C['texto_2']}; margin-top: 3px; }}


/* etapas: fluxo em colunas (produto → impacto na empresa) */
.ep {{ display: grid; align-items: stretch; gap: 0; }}
.ep .epc {{ background: {C['fundo']}; border-radius: 12px; padding: 18px 18px 12px; }}
.ep .epc.d {{ background: {E['fundo']}; color: {E['texto']}; }}
.ep .hd .n {{ font: 500 12px/1 {marca.MONO}; color: {C['ouro_texto']}; letter-spacing: 1px; }}
.ep .epc.d .hd .n {{ color: {E['ouro']}; }}
.ep .hd .tt {{ font-size: 22px; font-weight: 600; margin-top: 6px; }}
.ep .hd .tx {{ font-size: 12.5px; line-height: 1.4; color: {C['texto_2']}; margin-top: 4px; min-height: 36px; }}
.ep .epc.d .hd .tx {{ color: {E['texto_2']}; }}
.ep .it {{ border-top: 1px solid {C['borda_3']}; padding: 7px 0; }}
.ep .epc.d .it {{ border-top-color: {E['borda']}; }}
.ep .it .p {{ font: 500 10.5px/1.3 {marca.MONO}; letter-spacing: .8px; text-transform: uppercase; color: {C['ouro_texto']}; }}
.ep .epc.d .it .p {{ color: {E['ouro']}; }}
.ep .it .i {{ font-size: 14px; line-height: 1.35; margin-top: 2px; }}
.ep .ar {{ display: flex; align-items: center; justify-content: center; }}
.ep .ar i {{ width: 0; height: 0; border-left: 14px solid {C['ouro']}; border-top: 11px solid transparent; border-bottom: 11px solid transparent; }}

/* capa */
.capa {{ justify-content: flex-start; }}
.capa .logo {{ position: static; height: 30px; align-self: flex-start; }}
.capa .meio {{ margin-top: auto; margin-bottom: 64px; }}
.capa h1 {{ font-size: 58px; font-weight: 500; line-height: 1.06; letter-spacing: -1.2px; max-width: 900px; margin-top: 22px; }}
.capa .sub {{ font-size: 20px; max-width: 760px; margin-top: 22px; }}
.capa .linha {{ font: 500 12px/1 {marca.MONO}; letter-spacing: 1.6px; text-transform: uppercase; color: {E['texto_2']};
                border-top: 1px solid {E['borda']}; padding: 20px 0 30px; }}
.faixa {{ width: 96px; height: 4px; background: {E['ouro']}; margin-top: 30px; }}

/* seção */
.secao .n {{ font: 300 150px/1 {marca.SANS}; color: {E['ouro']}; letter-spacing: -4px; margin-top: auto; }}
.secao h1 {{ font-size: 46px; margin-top: 18px; }}
.secao .sub {{ margin-bottom: 92px; }}

/* afirmação com destaque */
.afi {{ display: grid; grid-template-columns: 1fr 360px; gap: 56px; align-items: start; }}
.afi .txt p {{ font-size: 21px; line-height: 1.6; color: {C['texto_2']}; margin-bottom: 14px; }}
.dest {{ border-left: 4px solid {C['ouro']}; padding: 4px 0 4px 26px; }}
.dest .v {{ font: 500 96px/1 {marca.SANS}; letter-spacing: -2px; color: {C['texto']}; }}
.dest .l {{ font-size: 17px; line-height: 1.45; color: {C['texto_2']}; margin-top: 12px; }}

/* números */
.nums {{ display: grid; gap: 0; border-top: 1px solid {C['borda_3']}; margin-top: 10px; }}
.num {{ padding: 34px 28px 0 0; border-right: 1px solid {C['borda']}; margin-right: 28px; }}
.num:last-child {{ border-right: 0; margin-right: 0; }}
.num .v {{ font: 500 80px/1 {marca.SANS}; letter-spacing: -1.4px; }}
.num .v small {{ font-size: 30px; letter-spacing: 0; margin-left: 4px; color: {C['texto_2']}; }}
.num .l {{ font-size: 18px; line-height: 1.45; color: {C['texto_2']}; margin-top: 14px; }}
.num .f {{ font: 400 10px/1.4 {marca.MONO}; color: {C['texto_3']}; margin-top: 10px; }}

/* barras */
.bar {{ display: grid; grid-template-columns: 360px 1fr 120px; align-items: center; gap: 22px; padding: 15px 0;
        border-bottom: 1px solid {C['borda']}; }}
.bar .r {{ font-size: 18px; color: {C['texto_2']}; }}
.bar .t {{ height: 30px; background: {C['fundo_2']}; position: relative; }}
.bar .p {{ position: absolute; inset: 0 auto 0 0; background: {C['borda_3']}; }}
.bar .x {{ font: 500 19px/1 {marca.MONO}; text-align: right; color: {C['texto_2']}; }}
.bar.d .r {{ color: {C['texto']}; font-weight: 600; }}
.bar.d .p {{ background: {C['ouro']}; }}
.bar.d .x {{ color: {C['texto']}; }}

/* comparativo */
table.cmp {{ width: 100%; border-collapse: collapse; }}
.cmp th {{ text-align: left; font: 500 12px/1.3 {marca.MONO}; letter-spacing: 1.6px; text-transform: uppercase;
           color: {C['texto_2']}; padding: 0 20px 12px 0; border-bottom: 1px solid {C['borda_3']}; }}
.cmp th.sv {{ color: {C['ouro_texto']}; }}
.cmp td {{ font-size: 17.5px; line-height: 1.42; padding: 15px 20px 13px 0; border-bottom: 1px solid {C['borda']}; vertical-align: top;
           color: {C['texto_2']}; }}
.cmp td.c {{ font-weight: 600; color: {C['texto']}; width: 23%; }}
.cmp td.sv {{ color: {C['texto']}; background: linear-gradient(90deg, {C['ouro_suave']}, {C['ouro_suave']}); padding-left: 16px; }}
.cmp th.sv {{ padding-left: 16px; }}

/* fluxo */
.flu {{ display: grid; gap: 14px; margin-top: 8px; }}
.et {{ border-top: 3px solid {C['texto']}; padding-top: 18px; position: relative; }}
.et.o {{ border-top-color: {C['ouro']}; }}
.et .n {{ font: 500 13px/1 {marca.MONO}; color: {C['ouro_texto']}; letter-spacing: 1px; }}
.et .tt {{ font-size: 22px; font-weight: 600; line-height: 1.25; margin-top: 12px; }}
.et .tx {{ font-size: 16px; line-height: 1.5; color: {C['texto_2']}; margin-top: 10px; }}
.et .q {{ font: 500 11.5px/1.3 {marca.MONO}; text-transform: uppercase; letter-spacing: 1.2px; color: {C['texto_3']}; margin-top: 14px; }}
.esc .et {{ border-top-color: {E['texto']}; }} .esc .et.o {{ border-top-color: {E['ouro']}; }}
.esc .et .n {{ color: {E['ouro']}; }} .esc .et .tx {{ color: {E['texto_2']}; }} .esc .et .q {{ color: {E['texto_3']}; }}

/* pilares */
.pil {{ display: grid; gap: 20px; margin-top: 8px; }}
.pi {{ background: {C['fundo']}; border-radius: 12px; padding: 32px 30px; min-height: 300px; }}
.pi .n {{ font: 500 13px/1 {marca.MONO}; color: {C['ouro_texto']}; }}
.pi .tt {{ font-size: 25px; font-weight: 600; line-height: 1.22; margin-top: 18px; }}
.pi .tx {{ font-size: 17.5px; line-height: 1.55; color: {C['texto_2']}; margin-top: 12px; }}
.esc .pi {{ background: {E['cartao']}; }} .esc .pi .n {{ color: {E['ouro']}; }} .esc .pi .tx {{ color: {E['texto_2']}; }}

/* duas colunas */
.duas {{ display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }}
.col {{ border-radius: 12px; padding: 30px 32px; background: {C['fundo']}; }}
.col.o {{ background: {E['fundo']}; color: {E['texto']}; }}
.col .tt {{ font: 500 12px/1.3 {marca.MONO}; letter-spacing: 1.6px; text-transform: uppercase; color: {C['texto_2']}; }}
.col.o .tt {{ color: {E['ouro']}; }}
.col ul {{ list-style: none; margin-top: 16px; }}
.col li {{ font-size: 17.5px; line-height: 1.42; padding: 11px 0 11px 24px; border-bottom: 1px solid {C['borda']}; position: relative; }}
.col.o li {{ border-bottom-color: {E['borda']}; }}
.col li::before {{ content: ""; position: absolute; left: 0; top: 22px; width: 9px; height: 2px; background: {C['texto_3']}; }}
.col.o li::before {{ background: {E['ouro']}; }}

/* pares (pergunta e resposta na mesma linha) */
.par {{ display: grid; grid-template-columns: 0.8fr 1.2fr; border-top: 1px solid {C['borda_3']}; }}
.par .h {{ font: 500 12px/1.3 {marca.MONO}; letter-spacing: 1.6px; text-transform: uppercase; color: {C['texto_2']}; padding: 0 24px 12px 0; }}
.par .h.o {{ color: {C['ouro_texto']}; padding-left: 24px; }}
.par .p, .par .r {{ font-size: 17px; line-height: 1.42; padding: 14px 24px 14px 0; border-bottom: 1px solid {C['borda']}; }}
.par .p {{ font-weight: 600; }}
.par .r {{ color: {C['texto']}; background: {C['ouro_suave']}; padding-left: 24px; }}
.par .hd {{ display: contents; }}

/* diagrama */
.dia {{ display: flex; align-items: stretch; margin-top: 18px; }}
.no {{ flex: 1; border: 1px solid {C['borda_3']}; border-radius: 12px; padding: 28px 24px; min-height: 220px; background: #FFF; }}
.no.o {{ background: {E['fundo']}; color: {E['texto']}; border-color: {E['fundo']}; }}
.no .tt {{ font-size: 22px; font-weight: 600; }}
.no .tx {{ font-size: 16px; line-height: 1.5; color: {C['texto_2']}; margin-top: 10px; }}
.no.o .tx {{ color: {E['texto_2']}; }}
.seta {{ width: 120px; flex: 0 0 120px; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0 8px; }}
.seta .ln {{ width: 100%; height: 2px; background: {C['ouro']}; position: relative; }}
.seta .ln::after {{ content: ""; position: absolute; right: -1px; top: -5px; border-left: 9px solid {C['ouro']}; border-top: 6px solid transparent; border-bottom: 6px solid transparent; }}
.seta .tx {{ font: 500 10.5px/1.35 {marca.MONO}; color: {C['ouro_texto']}; text-align: center; margin-top: 8px; text-transform: uppercase; letter-spacing: .6px; }}
.seta .tx.c {{ margin: 0 0 8px; }}

/* frase */
.frase .q {{ font: 300 46px/1.18 {marca.SANS}; letter-spacing: -0.8px; max-width: 1000px; margin-top: auto; }}
.frase .q b {{ font-weight: 500; color: {E['ouro']}; }}
.frase .a {{ font-size: 16px; color: {E['texto_2']}; margin: 26px 0 96px; max-width: 820px; line-height: 1.5; }}

/* caso */
.cas {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0 48px; border-top: 1px solid {C['borda_3']}; }}
.cas .it {{ padding: 20px 0; border-bottom: 1px solid {C['borda']}; }}
.cas .k {{ font: 500 11px/1.3 {marca.MONO}; letter-spacing: 1.4px; text-transform: uppercase; color: {C['ouro_texto']}; }}
.cas .v {{ font-size: 19px; line-height: 1.5; margin-top: 6px; color: {C['texto']}; }}

/* fechamento */
.fim h1 {{ font-size: 44px; margin-top: 18px; }}
/* mapa: imagem à esquerda (mapa do Brasil), número total à direita, fundo preto */
.mapa {{ flex-direction: row; padding: 0; }}
.mapa .img {{ width: 600px; height: 672px; flex: none; display: flex; align-items: center; justify-content: center; padding: 40px 0 0 48px; }}
.mapa .img img {{ max-width: 100%; max-height: 100%; }}
.mapa .dir {{ flex: 1; display: flex; flex-direction: column; padding: 56px 72px 72px 40px; }}
.mapa .dir h1 {{ font-size: 36px; }}
.mapa .tot {{ margin-top: auto; margin-bottom: auto; }}
.mapa .tot .v {{ font: 500 104px/1 {marca.SANS}; letter-spacing: -2px; white-space: nowrap; }}
.mapa .tot .v b {{ color: {E['ouro']}; font-weight: 500; }}
.mapa .tot .v small {{ font-size: 40px; color: {E['texto_2']}; margin-left: 6px; letter-spacing: 0; }}
.mapa .tot .l {{ font-size: 20px; line-height: 1.45; color: {E['texto_2']}; margin-top: 18px; max-width: 460px; }}
.mapa .tot .f {{ font: 400 11px/1.4 {marca.MONO}; color: {E['texto_3']}; margin-top: 12px; }}
.mapa .nota {{ color: {E['texto_3']}; margin-bottom: 18px; }}
.mapa .rod {{ position: absolute; left: 72px; right: 72px; bottom: 0; }}
.fim .ps {{ display: grid; gap: 24px; margin-top: 56px; }}
.fim .p {{ border-top: 1px solid {E['borda']}; padding-top: 18px; }}
.fim .p .n {{ font: 500 13px/1 {marca.MONO}; color: {E['ouro']}; }}
.fim .p .tx {{ font-size: 21px; line-height: 1.45; margin-top: 10px; }}
.fim .ct {{ margin-top: auto; margin-bottom: 26px; font-size: 15px; color: {E['texto_2']}; }}
"""


def cab(sl, esc=False):
    out = marcas(esc)
    if sl.get("rotulo"): out += f'<div class="rot">{t(sl["rotulo"])}</div>'
    if sl.get("titulo"): out += f"<h1>{t(sl['titulo'])}</h1>"
    if sl.get("subtitulo"): out += f'<div class="sub">{t(sl["subtitulo"])}</div>'
    return out


def rod(doc, n, total):
    return f'<div class="rod"><div>{t(doc.get("rodape", ""))}</div><div class="pg">{n:02d} / {total:02d}</div></div>'


def nota(sl):
    o = ""
    if sl.get("nota"): o += f'<div class="nota">{t(sl["nota"])}</div>'
    if sl.get("fonte"): o += f'<div class="fonte">Fonte: {t(sl["fonte"])}</div>'
    return o


def s_capa(sl, doc, n, tot):
    return (f'<div class="s esc capa"><img class="marcad" src="{CONTORNO}">{marcas(True, capa=True)}'
            f'<div class="meio"><div class="rot">{t(sl.get("rotulo", ""))}</div><h1>{t(sl["titulo"])}</h1>'
            f'<div class="sub">{t(sl.get("subtitulo", ""))}</div><div class="faixa"></div></div>'
            f'<div class="linha">{t(sl.get("linha", ""))}</div></div>')


def s_secao(sl, doc, n, tot):
    return (f'<div class="s esc secao"><img class="marcad" src="{CONTORNO}">{marcas(True)}'
            f'<div class="n">{t(sl.get("numero", ""))}</div><h1>{t(sl["titulo"])}</h1><div class="sub">{t(sl.get("texto", ""))}</div></div>')


def s_frase(sl, doc, n, tot):
    return (f'<div class="s esc frase"><img class="marcad" src="{CONTORNO}">{marcas(True)}'
            f'<div class="rot">{t(sl.get("rotulo", ""))}</div><div class="q">{t(sl["texto"])}</div>'
            f'<div class="a">{t(sl.get("apoio", ""))}</div></div>')


def s_afirmacao(sl, doc, n, tot):
    txt = "".join(f"<p>{t(p)}</p>" for p in sl.get("paragrafos", []))
    d = sl.get("destaque")
    tam = 96 if len(str(d["valor"])) <= 6 else 72 if len(str(d["valor"])) <= 9 else 56
    dh = (f'<div class="dest"><div class="v" style="font-size:{tam}px;white-space:nowrap">{t(d["valor"])}</div><div class="l">{t(d["legenda"])}</div>'
          + (f'<div class="fonte">Fonte: {t(d["fonte"])}</div>' if d.get("fonte") else "") + "</div>") if d else ""
    return f'<div class="s">{cab(sl)}<div class="corpo"><div class="afi"><div class="txt">{txt}</div>{dh}</div>{nota(sl)}</div>{rod(doc, n, tot)}</div>'


def s_numeros(sl, doc, n, tot):
    its = sl["itens"]
    h_ = "".join(f'<div class="num"><div class="v">{t(i["valor"])}' + (f'<small>{t(i["unidade"])}</small>' if i.get("unidade") else "") + f'</div><div class="l">{t(i["legenda"])}</div>'
                 + (f'<div class="f">{t(i["fonte"])}</div>' if i.get("fonte") else "") + "</div>" for i in its)
    if len(its) >= 4: h_ = h_.replace('<div class="v">', '<div class="v" style="font-size:60px;white-space:nowrap">')
    return (f'<div class="s">{cab(sl)}<div class="corpo"><div class="nums" style="grid-template-columns:repeat({len(its)},1fr)">{h_}</div>'
            f'{nota(sl)}</div>{rod(doc, n, tot)}</div>')


def s_barras(sl, doc, n, tot):
    mx = max(i["valor"] for i in sl["itens"])
    h_ = "".join(f'<div class="bar{" d" if i.get("destaque") else ""}"><div class="r">{t(i["rotulo"])}</div>'
                 f'<div class="t"><div class="p" style="width:{100 * i["valor"] / mx:.1f}%"></div></div><div class="x">{t(i.get("texto", i["valor"]))}</div></div>'
                 for i in sl["itens"])
    return f'<div class="s">{cab(sl)}<div class="corpo">{h_}{nota(sl)}</div>{rod(doc, n, tot)}</div>'


def s_comparativo(sl, doc, n, tot):
    a, b = sl["colunas"]
    rows = "".join(f'<tr><td class="c">{t(l["criterio"])}</td><td>{t(l["a"])}</td><td class="sv">{t(l["b"])}</td></tr>' for l in sl["linhas"])
    return (f'<div class="s">{cab(sl)}<div class="corpo"><table class="cmp"><tr><th></th><th>{t(a)}</th><th class="sv">{t(b)}</th></tr>{rows}</table>'
            f'{nota(sl)}</div>{rod(doc, n, tot)}</div>')


def s_fluxo(sl, doc, n, tot):
    et = sl["etapas"]; esc = sl.get("escuro")
    h_ = "".join(f'<div class="et{" o" if e.get("destaque") else ""}"><div class="n">{i:02d}</div><div class="tt">{t(e["titulo"])}</div>'
                 f'<div class="tx">{t(e.get("texto", ""))}</div>' + (f'<div class="q">{t(e["quem"])}</div>' if e.get("quem") else "") + "</div>"
                 for i, e in enumerate(et, 1))
    return (f'<div class="s{" esc" if esc else ""}">{cab(sl, esc)}<div class="corpo"><div class="flu" style="grid-template-columns:repeat({len(et)},1fr)">{h_}</div>'
            f'{nota(sl)}</div>{rod(doc, n, tot)}</div>')


def s_pilares(sl, doc, n, tot):
    it = sl["itens"]; esc = sl.get("escuro")
    h_ = "".join(f'<div class="pi"><div class="n">{i:02d}</div><div class="tt">{t(p["titulo"])}</div><div class="tx">{t(p["texto"])}</div></div>'
                 for i, p in enumerate(it, 1))
    return (f'<div class="s{" esc" if esc else ""}">{cab(sl, esc)}<div class="corpo"><div class="pil" style="grid-template-columns:repeat({len(it)},1fr)">{h_}</div>'
            f'{nota(sl)}</div>{rod(doc, n, tot)}</div>')


def s_duas(sl, doc, n, tot):
    def col(c, o):
        return f'<div class="col{" o" if o else ""}"><div class="tt">{t(c["titulo"])}</div><ul>' + "".join(f"<li>{t(x)}</li>" for x in c["itens"]) + "</ul></div>"
    return (f'<div class="s">{cab(sl)}<div class="corpo"><div class="duas">{col(sl["esquerda"], False)}{col(sl["direita"], True)}</div>'
            f'{nota(sl)}</div>{rod(doc, n, tot)}</div>')


def s_diagrama(sl, doc, n, tot):
    nos, setas = sl["nos"], sl.get("setas", [])
    h_ = ""
    for i, no in enumerate(nos):
        h_ += f'<div class="no{" o" if no.get("destaque") else ""}"><div class="tt">{t(no["titulo"])}</div><div class="tx">{t(no.get("texto", ""))}</div></div>'
        if i < len(nos) - 1:
            s_ = setas[i] if i < len(setas) else {}
            h_ += (f'<div class="seta"><div class="tx c">{t(s_.get("cima", ""))}</div><div class="ln"></div>'
                   f'<div class="tx">{t(s_.get("baixo", ""))}</div></div>')
    return f'<div class="s">{cab(sl)}<div class="corpo"><div class="dia">{h_}</div>{nota(sl)}</div>{rod(doc, n, tot)}</div>'


def s_pares(sl, doc, n, tot):
    a, b = sl.get("colunas", ["", ""])
    h_ = f'<div class="h">{t(a)}</div><div class="h o">{t(b)}</div>' + "".join(
        f'<div class="p">{t(x["pergunta"])}</div><div class="r">{t(x["resposta"])}</div>' for x in sl["itens"])
    return (f'<div class="s">{cab(sl)}<div class="corpo"><div class="par" style="border-top:0">{h_}</div>{nota(sl)}</div>{rod(doc, n, tot)}</div>')


def s_caso(sl, doc, n, tot):
    h_ = "".join(f'<div class="it"><div class="k">{t(l["rotulo"])}</div><div class="v">{t(l["texto"])}</div></div>' for l in sl["linhas"])
    return f'<div class="s">{cab(sl)}<div class="corpo"><div class="cas">{h_}</div>{nota(sl)}</div>{rod(doc, n, tot)}</div>'


def s_fechamento(sl, doc, n, tot):
    ps = sl.get("passos", [])
    h_ = "".join(f'<div class="p"><div class="n">{i:02d}</div><div class="tx">{t(p)}</div></div>' for i, p in enumerate(ps, 1))
    return (f'<div class="s esc fim"><img class="marcad" src="{CONTORNO}">{cab(sl, True)}'
            f'<div class="ps" style="grid-template-columns:repeat({max(1, len(ps))},1fr)">{h_}</div>'
            f'<div class="ct">{t(sl.get("contato", ""))}</div>{rod(doc, n, tot)}</div>')


def s_cascata(sl, doc, n, tot):
    its = sl["itens"]; run = 0; barras = []
    for it in its:
        v = float(it["valor"]); tp = it.get("tipo", "delta")
        if tp in ("base", "total"): lo, hi, run = 0, v, v; cls = tp
        else:
            lo, hi = sorted([run, run + v]); run += v; cls = "pos" if v >= 0 else "neg"
        barras.append((lo, hi, cls, it))
    mx = max(h for _, h, _, _ in barras) * 1.12 or 1; mn = min(0, min(l for l, _, _, _ in barras))
    esc = lambda v: (v - mn) / (mx - mn) * 100
    un = sl.get("unidade", "")
    def fmt(it):
        v = float(it["valor"]); txt = it.get("texto")
        if txt: return t(txt)
        s_ = f"{abs(v):,.1f}".replace(",", "X").replace(".", ",").replace("X", ".").replace(",0", "")
        return ("+" if it.get("tipo", "delta") == "delta" and v > 0 else "−" if v < 0 else "") + s_
    cols = "".join(f'<div class="c"><div class="b {c}" style="bottom:{esc(lo):.1f}%;height:{max(esc(hi) - esc(lo), .6):.1f}%"></div>'
                   f'<div class="v" style="bottom:calc({esc(hi):.1f}% + 8px)">{fmt(it)}</div></div>' for lo, hi, c, it in barras)
    labs = "".join(f'<div class="{"t" if it.get("tipo") in ("base", "total") else ""}">{t(it["rotulo"])}</div>' for it in its)
    un_h = f'<div class="fonte" style="margin-top:0">Valores em {t(un)}</div>' if un else ""
    return f'<div class="s">{cab(sl)}<div class="corpo">{un_h}<div class="wf">{cols}</div><div class="wfl">{labs}</div>{nota(sl)}</div>{rod(doc, n, tot)}</div>'


def s_matriz(sl, doc, n, tot):
    ex, ey = sl.get("eixo_x", {}), sl.get("eixo_y", {})
    qs = (sl.get("quadrantes") or ["", "", "", ""]) + ["", "", "", ""]
    pts = "".join(f'<div class="pt{" d" if p.get("destaque") else ""}{" esq" if float(p["x"]) > .72 else ""}" style="left:{float(p["x"]) * 100:.1f}%;top:{(1 - float(p["y"])) * 100:.1f}%"><i></i><span>{t(p["nome"])}</span></div>' for p in sl["itens"])
    return (f'<div class="s">{cab(sl)}<div class="corpo"><div class="mx">'
            f'<div class="ey"><span>{t(ey.get("baixo", ""))}</span><span>{t(ey.get("rotulo", ""))}</span><span>{t(ey.get("alto", ""))}</span></div>'
            f'<div class="pl">' + "".join(f'<div class="q{" hl" if i == sl.get("quadrante_destaque", 1) else ""}">{t(q)}</div>' for i, q in enumerate(qs[:4])) + f'{pts}</div>'
            f'<div class="ex"><span>{t(ex.get("baixo", ""))}</span><span>{t(ex.get("rotulo", ""))}</span><span>{t(ex.get("alto", ""))}</span></div>'
            f'</div>{nota(sl)}</div>{rod(doc, n, tot)}</div>')


def s_calor(sl, doc, n, tot):
    vals = [v for l in sl["linhas"] for v in l["valores"] if isinstance(v, (int, float))]
    mx = max(vals) if vals else 1
    def cel(v, tx):
        if not isinstance(v, (int, float)) or v == 0: return f'<td class="z">{t(tx if tx not in (None, "") else "—")}</td>'
        a = .12 + .88 * (v / mx); txt = tx if tx not in (None, "") else (f"{v:g}".replace(".", ","))
        return f'<td style="background:rgba(243,205,96,{a:.2f})">{t(txt)}</td>'
    head = '<tr><th class="n"></th>' + "".join(f"<th>{t(c)}</th>" for c in sl["colunas"]) + "</tr>"
    rows = "".join("<tr>" + f'<td class="n">{t(l["nome"])}</td>' + "".join(cel(v, (l.get("textos") or [None] * len(l["valores"]))[i]) for i, v in enumerate(l["valores"])) + "</tr>" for l in sl["linhas"])
    leg = f'<div class="hmleg"><span>menor</span><div class="g"></div><span>maior</span><span style="margin-left:12px">{t(sl.get("legenda", ""))}</span></div>'
    return f'<div class="s">{cab(sl)}<div class="corpo"><table class="hm">{head}{rows}</table>{leg}{nota(sl)}</div>{rod(doc, n, tot)}</div>'


def s_organograma(sl, doc, n, tot):
    rz = sl["raiz"]; gs = sl["grupos"]
    grupos = "".join(f'<div class="g"><div class="gh"><div class="tt">{t(g["titulo"])}</div><div class="tx">{t(g.get("texto", ""))}</div></div>'
                     + "".join(f'<div class="it"><div class="tt">{t(i["titulo"])}</div><div class="tx">{t(i.get("texto", ""))}</div></div>' for i in g.get("itens", []))
                     + "</div>" for g in gs)
    return (f'<div class="s">{cab(sl)}<div class="corpo"><div class="og"><div class="rz"><div class="tt">{t(rz["titulo"])}</div><div class="tx">{t(rz.get("texto", ""))}</div></div>'
            f'<div class="tr"></div><div class="gs" style="grid-template-columns:repeat({len(gs)},1fr)">{grupos}</div></div>{nota(sl)}</div>{rod(doc, n, tot)}</div>')


def s_tabela(sl, doc, n, tot):
    dc = sl.get("destaque_coluna")
    head = "".join(f'<th class="{"dc" if i == dc else ""}">{t(c)}</th>' for i, c in enumerate(sl["colunas"]))
    rows = "".join("<tr>" + "".join(f'<td class="{"dc" if i == dc else ""}">{t(c)}</td>' for i, c in enumerate(l)) + "</tr>" for l in sl["linhas"])
    est = ' style="font-size:17px"' if len(sl["colunas"]) <= 3 else ""
    rows = rows.replace("<td", f"<td{est}") if est else rows
    return f'<div class="s">{cab(sl)}<div class="corpo"><table class="tb"><tr>{head}</tr>{rows}</table>{nota(sl)}</div>{rod(doc, n, tot)}</div>'


def mandala_svg(sl, tam=450):
    return s_mandala(sl, {"rodape": ""}, 1, 1, so_svg=True, tam=tam)


def s_mandala(sl, doc, n, tot, so_svg=False, tam=450):
    """Mandala: centro (Save) e 3 fases como pétalas de um anel, com os serviços dentro de cada pétala."""
    import math
    cx = cy = 250; r0, r1 = 78, 240
    tons = [C["ouro_suave"], "#F8E3A3", C["ouro"]]
    fases = sl["fases"]; k = len(fases); svg = ""
    def pt(r, a): return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
    for i, f in enumerate(fases):
        a0 = -90 + i * 360 / k + 1.2; a1 = -90 + (i + 1) * 360 / k - 1.2
        x0, y0 = pt(r1, a0); x1, y1 = pt(r1, a1); x2, y2 = pt(r0, a1); x3, y3 = pt(r0, a0)
        svg += (f'<path d="M{x0:.1f},{y0:.1f} A{r1},{r1} 0 0 1 {x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f} A{r0},{r0} 0 0 0 {x3:.1f},{y3:.1f} Z" '
                f'fill="{tons[i % 3]}" stroke="#FFFFFF" stroke-width="3"/>')
        am = (a0 + a1) / 2; tx, ty = pt(158, am)
        itens = f.get("itens", []); lh = 17.5
        y = ty - (len(itens) * lh + 22) / 2 + 12
        svg += f'<text x="{tx:.1f}" y="{y:.1f}" text-anchor="middle" font-size="16.5" font-weight="700" fill="{C["texto"]}">{t(f["titulo"])}</text>'
        for j, it in enumerate(itens):
            svg += f'<text x="{tx:.1f}" y="{y + 24 + j * lh:.1f}" text-anchor="middle" font-size="13.5" fill="{C["texto_2"]}">{t(it)}</text>'
        # seta de sentido (horário) na borda externa
        ax, ay = pt(r1 + 6, a1 + 1.2)
    ce = sl.get("centro", {})
    svg += f'<circle cx="{cx}" cy="{cy}" r="{r0 - 6}" fill="{E["fundo"]}"/>'
    svg += f'<text x="{cx}" y="{cy - 2}" text-anchor="middle" font-size="19" font-weight="700" fill="{E["texto"]}">{t(ce.get("titulo", ""))}</text>'
    svg += f'<text x="{cx}" y="{cy + 20}" text-anchor="middle" font-size="11.5" fill="{E["ouro"]}">{t(ce.get("texto", ""))}</text>'
    if so_svg: return f'<svg xmlns="http://www.w3.org/2000/svg" width="{tam}" height="{tam}" viewBox="0 0 500 500" style="font-family:{marca.SANS}">{svg}</svg>'
    lg = "".join(f'<div class="f"><div class="n">{i:02d}</div><div><div class="tt">{t(f["titulo"])}</div><div class="tx">{t(f.get("texto", ""))}</div></div></div>'
                 for i, f in enumerate(fases, 1))
    return (f'<div class="s">{cab(sl)}<div class="corpo"><div class="md"><svg width="450" height="450" viewBox="0 0 500 500">{svg}</svg>'
            f'<div class="lg">{lg}</div></div>{nota(sl)}</div>{rod(doc, n, tot)}</div>')


def s_etapas(sl, doc, n, tot):
    """Fluxo em colunas: cada etapa com produtos e o impacto de cada um na empresa."""
    et = sl["etapas"]; cols = []
    for i, e in enumerate(et, 1):
        its = "".join(f'<div class="it"><div class="p">{t(x["produto"])}</div><div class="i">{t(x["impacto"])}</div></div>' for x in e.get("itens", []))
        cols.append(f'<div class="epc{" d" if e.get("destaque") else ""}"><div class="hd"><div class="n">{i:02d}</div><div class="tt">{t(e["titulo"])}</div>'
                    f'<div class="tx">{t(e.get("texto", ""))}</div></div>{its}</div>')
    grid = " 34px ".join(["1fr"] * len(et))
    corpo = '<div class="ar"><i></i></div>'.join(cols)
    return f'<div class="s">{cab(sl)}<div class="corpo"><div class="ep" style="grid-template-columns:{grid}">{corpo}</div>{nota(sl)}</div>{rod(doc, n, tot)}</div>'


def s_mapa(sl, doc, n, tot):
    """Mapa (imagem em fundo preto) à esquerda e um único número total à direita."""
    import base64
    img = BASE[0] / sl["imagem"]; tipo = "png" if img.suffix.lower() == ".png" else "jpeg"
    uri = f"data:image/{tipo};base64," + base64.b64encode(img.read_bytes()).decode()
    d = sl["total"]; v = t(d["valor"])
    v = v.replace("+", "<b>+</b>", 1) + (f'<small>{t(d["unidade"])}</small>' if d.get("unidade") else "")
    dir_ = (f'<div class="rot">{t(sl.get("rotulo", ""))}</div><h1>{t(sl["titulo"])}</h1>'
            f'<div class="tot"><div class="v">{v}</div><div class="l">{t(d.get("legenda", ""))}</div>'
            + (f'<div class="f">{t(d["fonte"])}</div>' if d.get("fonte") else "") + f'</div>{nota(sl)}')
    return (f'<div class="s esc mapa">{marcas(True)}<div class="img"><img src="{uri}"></div>'
            f'<div class="dir">{dir_}</div>{rod(doc, n, tot)}</div>')


TIPOS = {"capa": s_capa, "secao": s_secao, "frase": s_frase, "afirmacao": s_afirmacao, "numeros": s_numeros,
         "barras": s_barras, "comparativo": s_comparativo, "fluxo": s_fluxo, "pilares": s_pilares,
         "duas_colunas": s_duas, "diagrama": s_diagrama, "pares": s_pares, "cascata": s_cascata, "matriz": s_matriz, "calor": s_calor, "organograma": s_organograma, "tabela": s_tabela, "mandala": s_mandala, "etapas": s_etapas, "caso": s_caso, "fechamento": s_fechamento, "mapa": s_mapa}


def montar(doc):
    sl = doc["slides"]; tot = len(sl)
    corpo = "".join(TIPOS[s["tipo"]](s, doc, i, tot) for i, s in enumerate(sl, 1))
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{t(doc.get("titulo_doc", ""))}</title><style>{CSS}</style></head><body>{corpo}</body></html>'


def gerar(json_path, pdf_path, previas=None):
    doc = json.loads(Path(json_path).read_text(encoding="utf-8"))
    PARC.clear(); BASE[0] = Path(json_path).resolve().parent
    if doc.get("parceiro"):
        import base64
        base = Path(json_path).resolve().parent
        u = lambda f: "data:image/png;base64," + base64.b64encode((base / f).read_bytes()).decode()
        PARC.update(claro=u(doc["parceiro"]["logo_claro"]), escuro=u(doc["parceiro"]["logo_escuro"]))
    hp = Path(pdf_path).resolve().with_suffix(".html"); hp.write_text(montar(doc), encoding="utf-8")
    avisos = []
    with sync_playwright() as p:
        nav = p.chromium.launch(channel="chrome"); pg = nav.new_page(viewport={"width": W, "height": H})
        pg.goto(hp.as_uri()); pg.wait_for_timeout(300)
        # conferência: nada pode sair do slide nem invadir o rodapé
        avisos = pg.evaluate("""() => [...document.querySelectorAll('.s')].map((s, i) => {
            const r = s.getBoundingClientRect(), rod = s.querySelector('.rod'), lim = rod ? rod.getBoundingClientRect().top : r.bottom;
            let pior = 0; s.querySelectorAll('.corpo *, .meio *, .q, .a, .ps *').forEach(e => { const b = e.getBoundingClientRect(); if (b.height) pior = Math.max(pior, b.bottom - lim); });
            return pior > 1 ? `slide ${i + 1}: passa ${Math.round(pior)}px` : null }).filter(Boolean)""")
        pg.pdf(path=str(pdf_path), width=f"{W}px", height=f"{H}px", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        if previas:
            Path(previas).mkdir(parents=True, exist_ok=True)
            for i, el in enumerate(pg.query_selector_all(".s"), 1):
                el.screenshot(path=str(Path(previas) / f"slide-{i:02d}.png"))
        nav.close()
    hp.unlink()
    return avisos


if __name__ == "__main__":
    av = gerar(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print("ok", sys.argv[2], *(["AVISOS:"] + av if av else []), sep="\n")
