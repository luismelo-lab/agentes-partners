#!/usr/bin/env python3
"""Folder (A4 deitado, 3 dobras, frente e verso), flyer (A4) e peça de WhatsApp (1080x1350) no Design System Save v0.5.
Conteúdo: pecas.json (esquema no LEIA-ME.md). Uso: python3 pecas.py pecas.json pasta_saida [prefixo]
Gera <prefixo>-folder.pdf, <prefixo>-flyer.pdf, <prefixo>-whatsapp.png e prévias PNG. Só gera arquivos locais."""
import html, json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path.home() / "agentes-partners/lib"))
import marca  # noqa: E402

C, E = marca.C, marca.E
LC, LE, CONT = marca.logo_uri("fundo_claro"), marca.logo_uri("fundo_escuro"), marca.logo_uri("simbolo_contorno_ouro")


def t(s):
    s = html.escape(str(s or ""))
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s).replace("\n", "<br>")


def num(n, cls="nm"):
    if not n: return ""
    u = f'<small>{t(n["unidade"])}</small>' if n.get("unidade") else ""
    f = f'<div class="f">{t(n["fonte"])}</div>' if n.get("fonte") else ""
    return f'<div class="{cls}"><div class="v">{t(n["valor"])}{u}</div><div class="l">{t(n["legenda"])}</div>{f}</div>'


BASE = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: {marca.SANS}; color: {C['texto']}; -webkit-font-smoothing: antialiased; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
b {{ font-weight: 600; }}
.rot {{ font: 500 10px/1.2 {marca.MONO}; letter-spacing: 2px; text-transform: uppercase; color: {C['ouro_texto']}; display: flex; align-items: center; gap: 8px; }}
.rot::before {{ content: ""; width: 7px; height: 7px; background: {C['ouro']}; flex: 0 0 7px; }}
.esc {{ background: {E['fundo']}; color: {E['texto']}; }}
.esc .rot {{ color: {E['ouro']}; }}
.marcad {{ position: absolute; opacity: .22; pointer-events: none; }}
.f {{ font: 400 8.5px/1.35 {marca.MONO}; color: {C['texto_3']}; margin-top: 6px; }}
"""

# ------------------------------------------------------------------ flyer A4
CSS_FLYER = BASE + f"""
@page {{ size: A4; margin: 0; }}
.pg {{ width: 794px; height: 1123px; position: relative; overflow: hidden; display: flex; flex-direction: column; background: #FFF; }}
.topo {{ position: relative; padding: 40px 56px 34px; overflow: hidden; flex-shrink: 0; }}
.topo .logo {{ height: 26px; display: block; }}
.topo .rot {{ margin-top: 40px; }}
.topo h1 {{ font-weight: 500; font-size: 37px; line-height: 1.1; letter-spacing: -0.8px; margin-top: 14px; max-width: 600px; text-wrap: balance; }}
.topo .sub {{ font-size: 15.5px; line-height: 1.5; color: {E['texto_2']}; margin-top: 16px; max-width: 560px; text-wrap: pretty; }}
.topo .faixa {{ width: 72px; height: 4px; background: {E['ouro']}; margin-top: 24px; }}
.topo .marcad {{ width: 380px; right: -110px; bottom: -150px; }}
.meio {{ padding: 28px 56px 0; display: grid; grid-template-columns: 236px 1fr; gap: 32px; }}
.nm {{ border-left: 4px solid {C['ouro']}; padding-left: 18px; }}
.nm .v {{ font: 500 48px/1 {marca.SANS}; letter-spacing: -1.2px; white-space: nowrap; }}
.nm .v small {{ font-size: 16px; letter-spacing: 0; margin-left: 4px; color: {C['texto_2']}; }}
.nm .l {{ font-size: 13px; line-height: 1.45; color: {C['texto_2']}; margin-top: 10px; }}
.bens {{ display: grid; gap: 10px; }}
.bem {{ display: grid; grid-template-columns: 26px 1fr; gap: 10px; }}
.bem .n {{ font: 500 11px/1.6 {marca.MONO}; color: {C['ouro_texto']}; }}
.bem .tt {{ font-size: 15px; font-weight: 600; }}
.bem .tx {{ font-size: 13px; line-height: 1.45; color: {C['texto_2']}; margin-top: 3px; }}
.duas {{ padding: 30px 56px 0; display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }}
.cx {{ background: {C['fundo']}; border-radius: 12px; padding: 22px 22px 18px; }}
.cx .h {{ font: 500 10px/1.2 {marca.MONO}; letter-spacing: 1.6px; text-transform: uppercase; color: {C['texto_2']}; margin-bottom: 10px; }}
.cx li {{ list-style: none; font-size: 13.5px; line-height: 1.4; padding: 7px 0 7px 18px; border-bottom: 1px solid {C['borda']}; position: relative; }}
.cx li::before {{ content: ""; position: absolute; left: 0; top: 15px; width: 8px; height: 2px; background: {C['ouro']}; }}
.cx ol li {{ padding-left: 26px; counter-increment: p; }}
.cx ol {{ counter-reset: p; }}
.cx ol li::before {{ content: counter(p, decimal-leading-zero); background: none; width: auto; height: auto; top: 8px; font: 500 10.5px/1.4 {marca.MONO}; color: {C['ouro_texto']}; }}
.flx {{ margin: 22px 56px 0; padding: 22px 24px 20px; border: 1px solid {C['borda_3']}; border-radius: 12px; }}
.flx .trilha {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-top: 16px; position: relative; }}
.flx .trilha::before {{ content: ""; position: absolute; left: 12px; right: 12px; top: 12px; height: 2px; background: {C['ouro']}; }}
.flx .pa {{ position: relative; }}
.flx .bo {{ width: 26px; height: 26px; border-radius: 50%; background: {E['fundo']}; color: {E['ouro']}; font: 500 11px/26px {marca.MONO}; text-align: center; position: relative; }}
.flx .pa.o .bo {{ background: {C['ouro']}; color: {C['texto']}; }}
.flx .tt {{ font-size: 13px; font-weight: 600; line-height: 1.25; margin-top: 10px; }}
.flx .qm {{ font: 500 8.5px/1.3 {marca.MONO}; letter-spacing: .8px; text-transform: uppercase; color: {C['ouro_texto']}; margin-top: 4px; }}
.flx .tx {{ font-size: 11px; line-height: 1.4; color: {C['texto_2']}; margin-top: 5px; }}
.perf {{ margin: 18px 56px 0; }}
.perf .h {{ font: 500 10px/1.2 {marca.MONO}; letter-spacing: 1.6px; text-transform: uppercase; color: {C['texto_2']}; }}
.perf ul {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0 28px; margin-top: 6px; }}
.perf li {{ list-style: none; font-size: 12.5px; line-height: 1.4; padding: 6px 0 6px 16px; border-bottom: 1px solid {C['borda']}; position: relative; }}
.perf li::before {{ content: ""; position: absolute; left: 0; top: 13px; width: 8px; height: 2px; background: {C['ouro']}; }}
.fim {{ margin-top: auto; padding: 0 56px 0; }}
.cta {{ background: {E['fundo']}; color: {E['texto']}; border-radius: 12px; padding: 22px 26px; display: grid; grid-template-columns: 1fr 260px; gap: 24px; align-items: end; }}
.cta .a {{ font-size: 19px; font-weight: 500; line-height: 1.3; }}
.cta .c {{ font: 500 10px/1.2 {marca.MONO}; letter-spacing: 1.4px; text-transform: uppercase; color: {E['texto_2']}; }}
.cta .ln {{ border-bottom: 1px solid {E['texto_3']}; height: 26px; }}
.aviso {{ font-size: 9.5px; line-height: 1.45; color: {C['texto_3']}; padding: 14px 0 26px; display: flex; justify-content: space-between; gap: 20px; }}
.aviso img {{ height: 14px; opacity: .85; }}
"""


PARC = {}


def topo_logo(h):
    """Logo Save no topo escuro; com parceiro, as duas marcas lado a lado (co-branding)."""
    if not PARC: return f'<img class="logo" src="{LE}">'
    sv = f'<img src="{LE}" style="height:{h}px">'; pc = f'<img src="{PARC["escuro"]}" style="height:{int(h*1.15)}px">'
    sep = f'<span style="width:1px;height:{int(h*1.15)}px;background:{E["borda"]}"></span>'
    a, b = (pc, sv) if PARC.get("primeiro") else (sv, pc)   # parceiro à esquerda, como no deck
    return f'<div style="display:flex;align-items:center;gap:{int(h*0.7)}px">{a}{sep}{b}</div>'


def trilha(fl, cls="trilha"):
    return "".join(f'<div class="pa{" o" if e.get("destaque") else ""}"><div class="bo">{i:02d}</div><div class="tt">{t(e["titulo"])}</div>'
                   + (f'<div class="qm">{t(e["quem"])}</div>' if e.get("quem") else "") + f'<div class="tx">{t(e.get("texto", ""))}</div></div>'
                   for i, e in enumerate(fl["etapas"], 1))


def flyer(d):
    f = d["flyer"]
    bens = "".join(f'<div class="bem"><div class="n">{i:02d}</div><div><div class="tt">{t(b["titulo"])}</div><div class="tx">{t(b["texto"])}</div></div></div>'
                   for i, b in enumerate(f["beneficios"], 1))
    perfil = "".join(f"<li>{t(x)}</li>" for x in f["perfil"])
    passos = "".join(f"<li>{t(x)}</li>" for x in f.get("passos", []))
    fl = d.get("fluxo")
    if fl:
        miolo = (f'<div class="flx"><div class="rot">{t(fl["titulo"])}</div><div class="trilha">{trilha(fl)}</div></div>'
                 f'<div class="perf"><div class="h">{t(f.get("perfil_titulo", "Para quem é"))}</div><ul>{perfil}</ul></div>')
    else:
        miolo = (f'<div class="duas"><div class="cx"><div class="h">{t(f.get("perfil_titulo", "Para quem é"))}</div><ul>{perfil}</ul></div>'
                 f'<div class="cx"><div class="h">{t(f.get("passos_titulo", "Como funciona"))}</div><ol>{passos}</ol></div></div>')
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS_FLYER}</style></head><body><div class="pg">
<div class="topo esc"><img class="marcad" src="{CONT}">{topo_logo(26)}<div class="rot">{t(f['rotulo'])}</div>
<h1>{t(f['titulo'])}</h1><div class="sub">{t(f['subtitulo'])}</div><div class="faixa"></div></div>
<div class="meio">{num(f.get('numero'))}<div class="bens">{bens}</div></div>
{miolo}
<div class="fim"><div class="cta"{' style="grid-template-columns:1fr"' if "@" in f['cta'] else ""}><div class="a">{t(f['cta'])}</div>{"" if "@" in f['cta'] else '<div><div class="c">Fale com</div><div class="ln"></div></div>'}</div>
<div class="aviso"><div>{t(d.get('rodape', ''))}</div><img src="{LC}"></div></div>
</div></body></html>"""


# ------------------------------------------------------------------ folder A4 deitado, 3 painéis por face
CSS_FOLDER = BASE + f"""
@page {{ size: A4 landscape; margin: 0; }}
.face {{ width: 1123px; height: 794px; display: grid; grid-template-columns: 374px 375px 374px; page-break-after: always; overflow: hidden; }}
.pn {{ position: relative; overflow: hidden; padding: 40px 34px 30px; display: flex; flex-direction: column; background: #FFF; }}
.pn + .pn {{ border-left: 1px dashed {C['borda']}; }}
.pn.esc {{ background: {E['fundo']}; color: {E['texto']}; }}
.pn h3 {{ font-weight: 500; font-size: 18px; line-height: 1.2; margin-top: 10px; text-wrap: balance; }}
.pn.esc + .pn, .pn + .pn.esc {{ border-left-color: transparent; }}
.pn h2 {{ font-weight: 500; font-size: 23px; line-height: 1.18; letter-spacing: -0.3px; margin-top: 12px; text-wrap: balance; }}
.pn p {{ font-size: 13px; line-height: 1.55; color: {C['texto_2']}; margin-top: 12px; text-wrap: pretty; }}
.esc p {{ color: {E['texto_2']}; }}
.capa .logo {{ height: 24px; align-self: flex-start; }}
.capa .meio {{ margin-top: auto; margin-bottom: 40px; }}
.capa h1 {{ font-weight: 500; font-size: 33px; line-height: 1.1; letter-spacing: -0.6px; margin-top: 14px; text-wrap: balance; }}
.capa .sub {{ font-size: 13.5px; line-height: 1.5; color: {E['texto_2']}; margin-top: 14px; }}
.capa .faixa {{ width: 56px; height: 4px; background: {E['ouro']}; margin-top: 20px; }}
.capa .marcad {{ width: 340px; right: -110px; top: 120px; }}
.capa .linha {{ font: 500 9px/1.3 {marca.MONO}; letter-spacing: 1.4px; text-transform: uppercase; color: {E['texto_2']}; border-top: 1px solid {E['borda']}; padding-top: 14px; }}
.nums {{ display: grid; gap: 18px; margin-top: auto; }}
.nm {{ border-left: 4px solid {C['ouro']}; padding-left: 16px; }}
.nm .v {{ font: 500 40px/1 {marca.SANS}; letter-spacing: -1px; }}
.nm .v small {{ font-size: 16px; margin-left: 3px; color: {C['texto_2']}; letter-spacing: 0; }}
.nm .l {{ font-size: 12px; line-height: 1.4; color: {C['texto_2']}; margin-top: 7px; }}
.bens {{ margin-top: 16px; display: grid; gap: 11px; }}
.bem .tt {{ font-size: 13.5px; font-weight: 600; display: flex; gap: 8px; align-items: baseline; }}
.bem .tt span {{ font: 500 10px/1 {marca.MONO}; color: {C['ouro_texto']}; }}
.bem .tx {{ font-size: 12px; line-height: 1.45; color: {C['texto_2']}; margin-top: 3px; padding-left: 24px; }}
.ets {{ margin-top: 18px; display: grid; gap: 0; }}
.lt {{ margin-top: 18px; position: relative; }}
.lt::before {{ content: ""; position: absolute; left: 12px; top: 8px; bottom: 8px; width: 2px; background: {C['ouro']}; }}
.lt .pa {{ display: grid; grid-template-columns: 26px 1fr; gap: 12px; padding: 0 0 15px; position: relative; }}
.lt .bo {{ width: 26px; height: 26px; border-radius: 50%; background: {E['fundo']}; color: {E['ouro']}; font: 500 10.5px/26px {marca.MONO}; text-align: center; position: relative; }}
.lt .pa.o .bo {{ background: {C['ouro']}; color: {C['texto']}; }}
.lt .tt {{ font-size: 14px; font-weight: 600; line-height: 1.25; padding-top: 3px; }}
.lt .qm {{ font: 500 8.5px/1.3 {marca.MONO}; letter-spacing: .8px; text-transform: uppercase; color: {C['ouro_texto']}; margin-top: 3px; }}
.lt .tx {{ font-size: 12px; line-height: 1.42; color: {C['texto_2']}; margin-top: 4px; }}
.et {{ display: grid; grid-template-columns: 30px 1fr; gap: 8px; padding: 11px 0; border-top: 1px solid {C['borda']}; }}
.et .n {{ font: 500 11px/1.5 {marca.MONO}; color: {C['ouro_texto']}; }}
.et .tt {{ font-size: 14px; font-weight: 600; }}
.et .tx {{ font-size: 12px; line-height: 1.45; color: {C['texto_2']}; margin-top: 3px; }}
table.cmp {{ width: 100%; border-collapse: collapse; margin-top: 14px; }}
.cmp th {{ font: 500 8.5px/1.3 {marca.MONO}; letter-spacing: 1.2px; text-transform: uppercase; color: {C['texto_2']}; text-align: left; padding: 0 6px 7px 0; border-bottom: 1px solid {C['borda_3']}; }}
.cmp th.sv {{ color: {C['ouro_texto']}; padding-left: 7px; }}
.cmp td {{ font-size: 10.5px; line-height: 1.35; padding: 7px 6px 7px 0; border-bottom: 1px solid {C['borda']}; vertical-align: top; color: {C['texto_2']}; }}
.cmp td.c {{ font-weight: 600; color: {C['texto']}; width: 27%; }}
.cmp td.sv {{ background: {C['ouro_suave']}; color: {C['texto']}; padding-left: 7px; }}
.lst {{ margin-top: 12px; }}
.lst li {{ list-style: none; font-size: 12.5px; line-height: 1.4; padding: 7px 0 7px 18px; border-bottom: 1px solid {C['borda']}; position: relative; }}
.lst li::before {{ content: ""; position: absolute; left: 0; top: 14px; width: 8px; height: 2px; background: {C['ouro']}; }}
.esc .lst li {{ border-bottom-color: {E['borda']}; }}
.nao li::before {{ content: "×"; background: none; width: auto; height: auto; top: 6px; font: 500 12px/1.2 {marca.MONO}; color: {C['ouro_texto']}; }}
.esc .nao li::before {{ color: {E['ouro']}; }}
.sep {{ height: 26px; }}
.contato {{ margin-top: auto; }}
.contato .ln {{ border-bottom: 1px solid {E['texto_3']}; height: 30px; }}
.contato .c {{ font: 500 9px/1.2 {marca.MONO}; letter-spacing: 1.4px; text-transform: uppercase; color: {E['texto_2']}; margin-top: 20px; }}
.aviso {{ font-size: 8.5px; line-height: 1.45; color: {E['texto_3']}; margin-top: 22px; }}
.verso .logo {{ height: 20px; margin-top: 22px; align-self: flex-start; }}
"""


def folder(d):
    f = d["folder"]
    cmp_ = f["comparativo"]; a, b = cmp_["colunas"]
    linhas = "".join(f'<tr><td class="c">{t(l["criterio"])}</td><td>{t(l["a"])}</td><td class="sv">{t(l["b"])}</td></tr>' for l in cmp_["linhas"])
    perfil = "".join(f"<li>{t(x)}</li>" for x in f["perfil"]["itens"])
    nao = "".join(f"<li>{t(x)}</li>" for x in f["nao_fazemos"]["itens"])
    bens = "".join(f'<div class="bem"><div class="tt"><span>{i:02d}</span>{t(x["titulo"])}</div><div class="tx">{t(x["texto"])}</div></div>'
                   for i, x in enumerate(f["solucao"]["beneficios"], 1))
    ets = "".join(f'<div class="et"><div class="n">{i:02d}</div><div><div class="tt">{t(e["titulo"])}</div><div class="tx">{t(e["texto"])}</div></div></div>'
                  for i, e in enumerate(f.get("processo", {}).get("etapas", []), 1))
    nums = "".join(num(n) for n in f["problema"]["numeros"])
    fl = d.get("fluxo")
    if fl:
        lt = "".join(f'<div class="pa{" o" if e.get("destaque") else ""}"><div class="bo">{i:02d}</div><div><div class="tt">{t(e["titulo"])}</div>'
                     + (f'<div class="qm">{t(e["quem"])}</div>' if e.get("quem") else "") + f'<div class="tx">{t(e.get("texto", ""))}</div></div></div>'
                     for i, e in enumerate(fl["etapas"], 1))
        proc = f'<div class="pn"><div class="rot">Como funciona</div><h2>{t(fl["titulo"])}</h2><div class="lt">{lt}</div></div>'
    else:
        proc = f'<div class="pn"><div class="rot">Como funciona</div><h2>{t(f["processo"]["titulo"])}</h2><div class="ets">{ets}</div></div>'
    fora = f"""<div class="face">
<div class="pn"><div class="rot">Lado a lado</div><h3>{t(cmp_['titulo'])}</h3>
  <table class="cmp"><tr><th></th><th>{t(a)}</th><th class="sv">{t(b)}</th></tr>{linhas}</table>
  <div class="sep"></div><div class="rot">{t(f['perfil']['titulo'])}</div><ul class="lst">{perfil}</ul></div>
<div class="pn esc verso"><div class="rot">{t(f['nao_fazemos']['titulo'])}</div><ul class="lst nao">{nao}</ul>
  <div class="contato"><h2>{t(f['contato']['titulo'])}</h2><p>{t(f['contato']['texto'])}</p><div class="c">Fale com</div><div class="ln"></div></div>
  <img class="logo" src="{LE}"><div class="aviso">{t(d.get('rodape', ''))}</div></div>
<div class="pn esc capa"><img class="marcad" src="{CONT}"><img class="logo" src="{LE}">
  <div class="meio"><div class="rot">{t(f['capa']['rotulo'])}</div><h1>{t(f['capa']['titulo'])}</h1><div class="sub">{t(f['capa']['subtitulo'])}</div><div class="faixa"></div></div>
  <div class="linha">{t(d.get('area', ''))} · Save Co.</div></div>
</div>"""
    dentro = f"""<div class="face">
<div class="pn"><div class="rot">O desafio</div><h2>{t(f['problema']['titulo'])}</h2><p>{t(f['problema']['texto'])}</p><div class="nums">{nums}</div></div>
<div class="pn"><div class="rot">A solução</div><h2>{t(f['solucao']['titulo'])}</h2><p>{t(f['solucao']['texto'])}</p><div class="bens">{bens}</div></div>
{proc}
</div>"""
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS_FOLDER}</style></head><body>{fora}{dentro}</body></html>'


# ------------------------------------------------------------------ WhatsApp 1080x1350
CSS_WPP = BASE + f"""
html, body {{ width: 1080px; height: 1350px; }}
.pg {{ width: 1080px; height: 1350px; position: relative; overflow: hidden; display: flex; flex-direction: column; background: #FFF; }}
.topo {{ position: relative; overflow: hidden; padding: 64px 90px 56px; flex-shrink: 0; }}
.topo .logo {{ height: 40px; display: block; }}
.topo .rot {{ font-size: 15px; margin-top: 56px; }} .topo .rot::before {{ width: 11px; height: 11px; flex-basis: 11px; }}
.topo h1 {{ font-weight: 500; font-size: 60px; line-height: 1.08; letter-spacing: -1.4px; margin-top: 22px; text-wrap: balance; }}
.topo .marcad {{ width: 560px; right: -170px; bottom: -230px; }}
.topo .faixa {{ width: 110px; height: 6px; background: {E['ouro']}; margin-top: 36px; }}
.corpo {{ padding: 40px 90px 20px; flex: 1; display: flex; flex-direction: column; justify-content: center; }}
.nm .v small {{ font-size: 40px; letter-spacing: 0; margin-left: 8px; color: {C['texto_2']}; }}
.nm {{ border-left: 6px solid {C['ouro']}; padding-left: 28px; }}
.nm .v {{ font: 500 104px/1 {marca.SANS}; letter-spacing: -3px; }}
.nm .l {{ font-size: 27px; line-height: 1.38; color: {C['texto_2']}; margin-top: 14px; max-width: 800px; }}
.nm .f {{ font-size: 15px; margin-top: 10px; }}
.pts {{ margin-top: 44px; border-top: 1px solid {C['borda_3']}; }}
.pt {{ display: grid; grid-template-columns: 64px 1fr; padding: 18px 0; border-bottom: 1px solid {C['borda']}; font-size: 28px; line-height: 1.3; }}
.pt .n {{ font: 500 20px/1.6 {marca.MONO}; color: {C['ouro_texto']}; }}
.fecho {{ margin-top: 52px; font-size: 32px; font-weight: 500; }}
.wf {{ margin-top: 40px; }}
.wf .h {{ font: 500 15px/1.2 {marca.MONO}; letter-spacing: 2px; text-transform: uppercase; color: {C['texto_2']}; margin-bottom: 8px; }}
.wf .pa {{ display: grid; grid-template-columns: 52px 1fr auto; align-items: center; gap: 18px; padding: 13px 0; border-bottom: 1px solid {C['borda']}; position: relative; }}
.wf .bo {{ width: 44px; height: 44px; border-radius: 50%; background: {E['fundo']}; color: {E['ouro']}; font: 500 16px/44px {marca.MONO}; text-align: center; }}
.wf .pa.o .bo {{ background: {C['ouro']}; color: {C['texto']}; }}
.wf .tt {{ font-size: 28px; font-weight: 500; line-height: 1.2; }}
.wf .qm {{ font: 500 14px/1.2 {marca.MONO}; letter-spacing: 1px; text-transform: uppercase; color: {C['ouro_texto']}; text-align: right; }}
.aviso {{ font-size: 16px; color: {C['texto_3']}; padding: 22px 0 54px; border-top: 1px solid {C['borda']}; margin: 0 90px; display: flex; justify-content: space-between; align-items: center; gap: 40px; }}
.aviso img {{ height: 22px; }}
"""


def whatsapp(d):
    w = d["whatsapp"]
    fl = d.get("fluxo")
    if fl:
        pts = (f'<div class="wf"><div class="h">{t(fl["titulo"])}</div>' + "".join(
            f'<div class="pa{" o" if e.get("destaque") else ""}"><div class="bo">{i:02d}</div><div class="tt">{t(e["titulo"])}</div><div class="qm">{t(e.get("quem", ""))}</div></div>'
            for i, e in enumerate(fl["etapas"], 1)) + "</div>")
    else:
        pts = '<div class="pts">' + "".join(f'<div class="pt"><div class="n">{i:02d}</div><div>{t(p)}</div></div>' for i, p in enumerate(w.get("pontos", []), 1)) + "</div>"
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS_WPP}</style></head><body><div class="pg">
<div class="topo esc"><img class="marcad" src="{CONT}">{topo_logo(40)}<div class="rot">{t(w['rotulo'])}</div><h1>{t(w['titulo'])}</h1><div class="faixa"></div></div>
<div class="corpo">{num(w.get('numero'))}{pts}<div class="fecho">{t(w['fecho'])}</div></div>
<div class="aviso"><div>{t(d.get('rodape', ''))}</div><img src="{LC}"></div>
</div></body></html>"""


def checar(pg, seletor):
    """Texto que passa da caixa (overflow) em qualquer bloco."""
    return pg.evaluate(f"""() => [...document.querySelectorAll('{seletor}')].map((p, i) => {{
        const r = p.getBoundingClientRect(); let pior = 0;
        p.querySelectorAll('*').forEach(e => {{ const b = e.getBoundingClientRect(); if (b.height && !e.classList.contains('marcad')) pior = Math.max(pior, b.bottom - r.bottom); }});
        return pior > 1 ? `bloco ${{i + 1}}: passa ${{Math.round(pior)}}px` : null }}).filter(Boolean)""")


def gerar(json_path, saida, prefixo=None):
    d = json.loads(Path(json_path).read_text(encoding="utf-8"))
    PARC.clear()
    if d.get("parceiro"):
        import base64
        b = Path(json_path).resolve().parent
        PARC["escuro"] = "data:image/png;base64," + base64.b64encode((b / d["parceiro"]["logo_escuro"]).read_bytes()).decode()
        PARC["primeiro"] = d["parceiro"].get("primeiro", True)
    saida = Path(saida).resolve(); saida.mkdir(parents=True, exist_ok=True)
    pre = prefixo or d.get("id", "peca"); prev = saida / "previas"; prev.mkdir(exist_ok=True)
    avisos = []
    with sync_playwright() as p:
        nav = p.chromium.launch(channel="chrome")
        if "flyer" in d:
          pg = nav.new_page(viewport={"width": 794, "height": 1123}); pg.set_content(flyer(d)); pg.wait_for_timeout(250)
          avisos += ["flyer " + a for a in checar(pg, ".pg")]
          avisos += ["flyer " + a for a in pg.evaluate("() => { const f = document.querySelector('.fim').getBoundingClientRect(), d = document.querySelector('.perf, .duas').getBoundingClientRect(); return d.bottom > f.top - 12 ? ['meio invade o rodapé'] : [] }")]
          pg.pdf(path=str(saida / f"{pre}-flyer.pdf"), format="A4", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
          pg.screenshot(path=str(prev / f"{pre}-flyer.png"))
        if "folder" in d:
          pg = nav.new_page(viewport={"width": 1123, "height": 794}); pg.set_content(folder(d)); pg.wait_for_timeout(250)
          avisos += ["folder " + a for a in checar(pg, ".pn")]
          pg.pdf(path=str(saida / f"{pre}-folder.pdf"), width="1123px", height="794px", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
          for i, el in enumerate(pg.query_selector_all(".face"), 1): el.screenshot(path=str(prev / f"{pre}-folder-{i}.png"))
        if "whatsapp" in d:
          pg = nav.new_page(viewport={"width": 1080, "height": 1350}); pg.set_content(whatsapp(d)); pg.wait_for_timeout(250)
          avisos += ["whatsapp " + a for a in checar(pg, ".pg")]
          pg.screenshot(path=str(saida / f"{pre}-whatsapp.png"))
        nav.close()
    if d.get("mensagem"): (saida / f"{pre}-mensagem-abordagem.txt").write_text(d["mensagem"] + "\n", encoding="utf-8")
    if d.get("mensagem_pos_reuniao"): (saida / f"{pre}-mensagem-pos-reuniao.txt").write_text(d["mensagem_pos_reuniao"] + "\n", encoding="utf-8")
    return avisos


if __name__ == "__main__":
    av = gerar(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print("ok", *(["AVISOS:"] + av if av else []), sep="\n")
