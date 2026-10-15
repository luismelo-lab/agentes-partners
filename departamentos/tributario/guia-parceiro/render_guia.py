#!/usr/bin/env python3
"""Guia do Parceiro (Save Co.): fichas técnicas por tese e por produto, em linguagem comercial, com quebra de objeções.
Layout padrão Save (preto, ouro, IBM Plex), uma página de 1920x1080 por ficha, PDF pesquisável (texto vetorial) com links no índice.

Entrada : conteudo/*.json (teses-a, teses-b, conceitos, produtos-a, produtos-b, gerais, matriz)
Saída   : <saida>/Guia-do-Parceiro-Save.pdf  (+ previas/NN.png se --previas)
Uso     : python3 render_guia.py [saida] [--previas]
Só gera arquivos locais."""
import html, json, re, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "apresentacao-diagnostico"))
import render_comercial as R  # noqa: E402

OURO = R.OURO
CONT = AQUI / "conteudo"


def esc(s):
    return html.escape(str(s or ""))


def fontes():
    css = R.css()
    return "".join(re.findall(r"@font-face\{[^}]*\}", css))


CSS = fontes() + f"""
*{{box-sizing:border-box;margin:0;padding:0}}
@page{{size:1920px 1080px;margin:0}}
body{{background:#000;color:#F5F5F5;font-family:'IBM Plex Sans',sans-serif}}
.pg{{position:relative;width:1920px;height:1080px;overflow:hidden;page-break-after:always;break-after:page;background:radial-gradient(ellipse at 78% 0%,#17120a 0%,#070604 42%,#000 75%)}}
.mono{{font-family:'IBM Plex Mono',monospace}}
.rot{{font-family:'IBM Plex Mono',monospace;font-size:17px;letter-spacing:.12em;text-transform:uppercase;color:{OURO}}}
.top{{position:absolute;left:80px;right:80px;top:34px;display:flex;justify-content:space-between;align-items:center;height:30px}}
.top img{{height:28px}} .top .sec{{font-family:'IBM Plex Mono',monospace;font-size:15px;letter-spacing:.12em;color:#8e8e8e;text-transform:uppercase}}
.top .n{{font-family:'IBM Plex Mono',monospace;font-size:16px;color:{OURO}}}
h1{{font-weight:300;letter-spacing:-.01em;color:#F2F2F2}}
.chip{{display:inline-block;padding:5px 14px;border:1px solid rgba(243,205,96,.55);border-radius:18px;font-family:'IBM Plex Mono',monospace;font-size:15px;letter-spacing:.06em;color:{OURO};margin-left:8px;text-transform:uppercase}}
.h{{font-family:'IBM Plex Mono',monospace;font-size:14.5px;letter-spacing:.13em;text-transform:uppercase;color:{OURO};margin:0 0 9px;display:flex;align-items:center;gap:10px}}
.h::after{{content:"";flex:1;height:1px;background:rgba(243,205,96,.28)}}
.b{{font-size:19px;line-height:1.3;color:#D6D6D6;padding:5px 0 5px 22px;position:relative}}
.b::before{{content:"";position:absolute;left:3px;top:14px;width:7px;height:7px;background:{OURO};transform:rotate(45deg)}}
.b.nao::before{{background:#8e8e8e}}
.card{{border:1px solid #2c2c2c;border-radius:16px;background:linear-gradient(180deg,rgba(255,255,255,.05),rgba(255,255,255,.012))}}
a{{color:inherit;text-decoration:none}}
"""

LOGO = R.uri(R.PADRAO / R.M["logos"]["fundo_escuro"])
SIMB = R.uri(R.PADRAO / R.M["logos"]["simbolo_contorno_ouro"])
paginas = []
indice = []


def pagina(corpo, secao="", ancora=None):
    n = len(paginas) + 1
    a = f' id="{ancora}"' if ancora else ""
    paginas.append(f'<section class="pg"{a}><div class="top"><img src="{LOGO}"><span class="sec">{esc(secao)}</span><span class="n">{n:02d}</span></div>{corpo}</section>')
    return n


def lista(itens, cls=""):
    return "".join(f'<div class="b {cls}">{esc(i)}</div>' for i in itens)


def ficha(f):
    selos = "".join(f'<span class="chip">{esc(s)}</span>' for s in f["selos"])
    tec = "".join(f'<div style="padding:9px 0;border-top:1px solid rgba(255,255,255,.08)"><div style="display:flex;align-items:baseline;gap:10px;flex-wrap:wrap"><span style="font-size:19.5px;font-weight:600;color:{OURO}">{esc(t["termo"])}</span>'
                  f'<span style="font-size:15px;color:#8e8e8e">{esc(t["tecnico"])}</span></div><div style="font-size:18px;line-height:1.3;color:#EFEFEF;margin-top:3px">{esc(t["comercial"])}</div></div>' for t in f["tecnico_traduzido"])
    obj = "".join(f'<div style="margin-bottom:11px;padding:10px 14px;border-left:3px solid {OURO};background:rgba(243,205,96,.05);border-radius:0 12px 12px 0"><div style="font-size:18px;font-weight:600;color:#fff;line-height:1.25">“{esc(o["o"])}”</div>'
                  f'<div style="font-size:17px;line-height:1.3;color:#CFCFCF;margin-top:5px">{esc(o["r"])}</div></div>' for o in f["objecoes"])
    docs = "".join(f'<span style="display:inline-block;margin:0 6px 7px 0;padding:3px 11px;border:1px solid #3a3a3a;border-radius:14px;font-size:15.5px;color:#C9C9C9">{esc(d)}</span>' for d in f["documentos"])
    col = lambda x, w, inner: f'<div class="col" data-w="{w}" style="position:absolute;left:{x}px;top:296px;width:{w}px;transform-origin:0 0">{inner}</div>'
    corpo = (
        f'<div style="position:absolute;left:80px;top:74px;right:80px"><div class="rot">{esc(f["grupo"])} · {esc(f["familia"])} · {esc(f["id"])}</div>'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px"><h1 style="font-size:42px;line-height:1.08;max-width:1330px">{esc(f["nome"])}</h1><div>{selos}</div></div></div>'
        f'<div style="position:absolute;left:80px;right:80px;top:178px;padding:11px 22px;border-radius:14px;background:linear-gradient(90deg,rgba(243,205,96,.16),rgba(243,205,96,.04));border:1px solid rgba(243,205,96,.35)">'
        f'<span class="mono" style="font-size:13.5px;letter-spacing:.13em;color:{OURO}">EM 20 SEGUNDOS</span><div style="font-size:22px;line-height:1.28;color:#fff;margin-top:3px">{esc(f["em_20_segundos"])}</div></div>'
        + col(80, 372, f'<div class="h">O que o cliente ganha</div>{lista(f["o_que_o_cliente_ganha"])}<div class="h" style="margin-top:12px">Perfil ideal</div>{lista(f["perfil_ideal"])}'
              f'<div class="h" style="margin-top:12px">Documentos</div><div>{docs}</div>')
        + col(476, 372, f'<div class="h">Sinais para oferecer</div>{lista(f["sinais_para_oferecer"])}<div class="h" style="margin-top:12px">Não oferecer quando</div>{lista(f["nao_oferecer_quando"], "nao")}'
              f'<div class="h" style="margin-top:12px">Perguntas de descoberta</div>{lista(f["perguntas_de_descoberta"])}')
        + col(872, 470, f'<div class="h">Técnico, em linguagem comercial</div>{tec}')
        + col(1366, 474, f'<div class="h">Quebra de objeções</div>{obj}')
        + f'<div class="rodape-ficha" style="position:absolute;left:80px;right:80px;bottom:22px;display:flex;gap:28px;align-items:flex-start;border-top:1px solid #2c2c2c;padding-top:9px">'
        f'<div style="flex:1.2;font-size:15px;line-height:1.3;color:#A9A9A9"><b style="color:{OURO};font-weight:500">Uso interno, não mostrar ao cliente · </b>{esc(re.sub(r"^Uso interno:\s*", "", f["remuneracao_interna"]))}</div>'
        f'<div style="flex:1.25;font-size:15px;line-height:1.3;color:#A9A9A9"><b style="color:{OURO};font-weight:500">Cuidados · </b>{esc(" ".join(f["cuidados"]))}</div>'
        f'<div style="flex:.75;font-size:14px;line-height:1.3;color:#7d7d7d"><b style="color:{OURO};font-weight:500">Fonte · </b>{esc(f["fonte"])}</div></div>')
    n = pagina(corpo, f'{f["grupo"]} · {f["familia"]}', "f_" + f["id"])
    indice.append((f["grupo"], f["familia"], f["id"], f["nome"], n))


def carregar(nome):
    p = CONT / nome
    return json.load(open(p)) if p.exists() else None


def capa():
    corpo = (f'<img src="{SIMB}" style="position:absolute;right:-140px;top:-60px;width:900px;opacity:.09">'
             f'<img src="{LOGO}" style="position:absolute;left:80px;top:80px;width:280px">'
             f'<div style="position:absolute;left:80px;top:360px;width:1200px"><div class="rot" style="margin-bottom:22px">Material do parceiro · uso em reunião</div>'
             f'<h1 style="font-size:104px;line-height:1.02">Guia do Parceiro</h1>'
             f'<div style="font-size:36px;line-height:1.35;color:#C4C4C4;margin-top:30px;width:1000px">Teses e produtos da Save, em linguagem comercial, com a quebra de objeções de cada um.</div>'
             f'<div style="width:140px;height:5px;background:{OURO};margin-top:46px"></div></div>'
             f'<div class="rot" style="position:absolute;left:80px;bottom:70px;color:#8e8e8e">Save Co. · outubro de 2026 · uso interno do parceiro</div>')
    paginas.append(f'<section class="pg">{corpo}</section>')


def como_usar(g, c):
    cu = g["como_usar"]
    passos = "".join(f'<div class="card" style="padding:26px 28px"><div class="mono" style="font-size:20px;color:{OURO}">{esc(p["n"])}</div><div style="font-size:30px;font-weight:500;margin:10px 0 10px;color:#fff">{esc(p["titulo"])}</div>'
                     f'<div style="font-size:21px;line-height:1.4;color:#CFCFCF">{esc(p["texto"])}</div></div>' for p in cu["passos"])
    selos = "".join(f'<div style="display:flex;gap:14px;align-items:baseline;padding:8px 0;border-top:1px solid #262626"><span class="chip" style="margin:0;min-width:96px;text-align:center">{esc(s["selo"])}</span><span style="font-size:19px;color:#CFCFCF">{esc(s["significa"])}</span></div>' for s in cu["legenda_selos"])
    corpo = (f'<div style="position:absolute;left:80px;top:84px;width:1700px"><div class="rot">Antes da reunião</div><h1 style="font-size:60px;margin-top:10px">{esc(cu["titulo"])}</h1></div>'
             f'<div style="position:absolute;left:80px;top:250px;width:1760px;display:grid;grid-template-columns:repeat(4,1fr);gap:22px">{passos}</div>'
             f'<div style="position:absolute;left:80px;top:640px;width:1100px"><div class="h">Selos das fichas</div>{selos}</div>')
    pagina(corpo, "Como usar")


def conceitos_pg(c):
    vias = "".join(f'<div class="card" style="padding:22px 26px"><div style="display:flex;align-items:center;gap:14px"><span class="chip" style="margin:0">{esc(v["sigla"])}</span><span style="font-size:26px;font-weight:500">{esc(v["nome"])}</span></div>'
                   f'<div style="font-size:20px;line-height:1.35;color:#E6E6E6;margin-top:12px">{esc(v["em_20_segundos"])}</div><div style="font-size:17.5px;line-height:1.35;color:#A9A9A9;margin-top:10px"><b style="color:{OURO};font-weight:500">Quando: </b>{esc(v["quando"])}</div>'
                   f'<div style="font-size:17.5px;line-height:1.35;color:#A9A9A9;margin-top:6px"><b style="color:{OURO};font-weight:500">Cuidado: </b>{esc(v["cuidado"])}</div></div>' for v in c["vias"])
    esp = "".join(f'<div class="card" style="padding:22px 26px"><div style="font-size:26px;font-weight:500;color:#fff">{esc(e["nome"])}</div>'
                  f'<div style="font-size:20px;line-height:1.35;color:#E6E6E6;margin-top:10px">{esc(e["em_20_segundos"])}</div><div style="font-size:17.5px;line-height:1.35;color:#A9A9A9;margin-top:10px"><b style="color:{OURO};font-weight:500">Exemplo: </b>{esc(e["exemplo"])}</div>'
                  f'<div style="font-size:17.5px;line-height:1.35;color:#A9A9A9;margin-top:6px"><b style="color:{OURO};font-weight:500">Cuidado: </b>{esc(e["cuidado"])}</div></div>' for e in c["especies"])
    tri = lista(c["quatro_perguntas_de_triagem"]); lim = lista(c["limites"])
    corpo = (f'<div style="position:absolute;left:80px;top:78px;width:1700px"><div class="rot">Base da recuperação tributária</div><h1 style="font-size:50px;margin-top:8px">Três vias, três tipos de pedido e como começar</h1></div>'
             f'<div style="position:absolute;left:80px;top:190px;width:1760px"><div class="h">Por qual via a Save atua</div><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px">{vias}</div></div>'
             f'<div style="position:absolute;left:80px;top:520px;width:1760px"><div class="h">Como o dinheiro volta para o caixa</div><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px">{esp}</div></div>'
             f'<div style="position:absolute;left:80px;top:860px;width:870px"><div class="h">Quatro perguntas para começar</div>{tri}</div>'
             f'<div style="position:absolute;left:990px;top:860px;width:850px"><div class="h">Limites que valem sempre</div>{lim}</div>')
    pagina(corpo, "Recuperação tributária")


def roteiro_pg(g):
    r = g["roteiro_reuniao"]
    lin = "".join(f'<div style="display:grid;grid-template-columns:660px 330px 1fr;gap:22px;padding:13px 0;border-top:1px solid #262626"><div style="font-size:21px;color:#fff;line-height:1.3">“{esc(q["pergunta"])}”</div>'
                  f'<div style="font-size:18.5px;color:{OURO};line-height:1.3">{esc(q["se_a_resposta_for"])}</div><div style="font-size:19px;color:#D6D6D6;line-height:1.3">{esc(q["abra_a_ficha"])}</div></div>' for q in r["perguntas_de_entrada"])
    corpo = (f'<div style="position:absolute;left:80px;top:78px;width:1700px"><div class="rot">Na reunião</div><h1 style="font-size:50px;margin-top:8px">Roteiro de entrada: perguntas que levam à ficha certa</h1></div>'
             f'<div class="card" style="position:absolute;left:80px;top:196px;width:1760px;padding:18px 26px"><span class="mono" style="font-size:14px;letter-spacing:.13em;color:{OURO}">ABERTURA</span><div style="font-size:23px;line-height:1.35;color:#fff;margin-top:5px">{esc(r["abertura"])}</div></div>'
             f'<div style="position:absolute;left:80px;top:340px;width:1760px"><div style="display:grid;grid-template-columns:660px 330px 1fr;gap:22px;font-family:\'IBM Plex Mono\',monospace;font-size:14px;letter-spacing:.12em;color:{OURO};padding-bottom:8px">'
             f'<span>PERGUNTA</span><span>SE A RESPOSTA FOR</span><span>ABRA A FICHA</span></div>{lin}</div>'
             f'<div class="card" style="position:absolute;left:80px;bottom:34px;width:1760px;padding:16px 26px"><span class="mono" style="font-size:14px;letter-spacing:.13em;color:{OURO}">FECHAMENTO</span><div style="font-size:21px;line-height:1.35;color:#fff;margin-top:4px">{esc(r["fechamento"])}</div></div>')
    pagina(corpo, "Na reunião")


def matriz_pgs(m):
    lin_h = 44; por_pg = 18
    cab = lambda: (f'<div style="display:grid;grid-template-columns:70px 470px 130px 120px 400px 1fr;gap:14px;font-family:\'IBM Plex Mono\',monospace;font-size:13.5px;letter-spacing:.1em;color:{OURO};padding:0 0 8px">'
                   f'<span>ID</span><span>TESE OU PRODUTO</span><span>VIA</span><span>REGIME</span><span>QUEM</span><span>SINAL RÁPIDO</span></div>')
    for k in range(0, len(m), por_pg):
        parte = m[k:k + por_pg]
        lin = "".join(f'<a href="#f_{x["id"]}"><div style="display:grid;grid-template-columns:70px 470px 130px 120px 400px 1fr;gap:14px;align-items:center;height:{lin_h}px;border-top:1px solid #242424;font-size:17px;color:#D6D6D6">'
                      f'<span class="mono" style="color:{OURO};font-size:15px">{esc(x["id"])}</span><span style="color:#fff;font-weight:500;font-size:18px">{esc(x["nome"])}</span><span>{esc(x["via"])}</span><span>{esc(x["regime"])}</span><span>{esc(x["quem"])}</span><span>{esc(x["sinal_rapido"])}</span></div></a>' for x in parte)
        corpo = (f'<div style="position:absolute;left:80px;top:78px;width:1700px"><div class="rot">Consulta rápida</div><h1 style="font-size:46px;margin-top:8px">Matriz: qual ficha abrir para qual cliente {"(continua)" if k else ""}</h1></div>'
                 f'<div style="position:absolute;left:80px;top:186px;width:1760px">{cab()}{lin}</div>')
        pagina(corpo, "Matriz de consulta")


def indice_pgs():
    # montado ao final: usa a lista 'indice'
    pass


def indice_html():
    cols = {}
    for grupo, familia, id_, nome, n in indice:
        cols.setdefault(grupo, []).append((familia, id_, nome, n))
    blocos = ""
    for grupo, itens in cols.items():
        fam = {}
        for familia, id_, nome, n in itens: fam.setdefault(familia, []).append((id_, nome, n))
        t = "".join(f'<div style="margin-bottom:10px;break-inside:avoid"><div class="mono" style="font-size:13.5px;letter-spacing:.12em;color:{OURO};text-transform:uppercase;margin-bottom:4px">{esc(f)}</div>' +
                    "".join(f'<a href="#f_{i}"><div style="display:flex;justify-content:space-between;gap:12px;font-size:16px;line-height:1.38;color:#E2E2E2"><span>{esc(nm)}</span><span class="mono" style="color:#8e8e8e;font-size:14.5px">{pg:02d}</span></div></a>' for i, nm, pg in its) + '</div>' for f, its in fam.items())
        blocos += f'<div class="h" style="break-after:avoid">{esc(grupo)}s</div>{t}'
    return blocos


def gerais_pgs(g):
    ob = g["objecoes_gerais"]
    for k in range(0, len(ob), 6):
        itens = "".join(f'<div class="card" style="padding:16px 22px"><div style="font-size:23px;font-weight:600;color:#fff">“{esc(o["o"])}”</div><div style="font-size:19.5px;line-height:1.38;color:#DADADA;margin-top:7px">{esc(o["r"])}</div>'
                        f'<div style="font-size:16.5px;color:#9a9a9a;margin-top:7px"><b style="color:{OURO};font-weight:500">Não diga: </b>{esc(o["dica"])}</div></div>' for o in ob[k:k + 6])
        corpo = (f'<div style="position:absolute;left:80px;top:78px;width:1700px"><div class="rot">Quebra de objeções · gerais</div><h1 style="font-size:48px;margin-top:8px">As objeções que aparecem em qualquer reunião {"(continua)" if k else ""}</h1></div>'
                 f'<div style="position:absolute;left:80px;top:186px;width:1760px;display:grid;grid-template-columns:1fr 1fr;gap:18px">{itens}</div>')
        pagina(corpo, "Objeções gerais")
    rg = g["regras_de_ouro"]
    corpo = (f'<div style="position:absolute;left:80px;top:78px;width:1700px"><div class="rot">Comunicação segura</div><h1 style="font-size:48px;margin-top:8px">Regras de ouro: o que dizer e o que evitar</h1></div>'
             f'<div style="position:absolute;left:80px;top:190px;width:860px"><div class="h">Diga</div>{lista(rg["diga"])}</div>'
             f'<div style="position:absolute;left:980px;top:190px;width:860px"><div class="h">Não diga (e diga isto no lugar)</div>{lista(rg["nao_diga"], "nao")}</div>'
             f'<div class="card" style="position:absolute;left:80px;bottom:60px;width:1760px;padding:18px 26px"><div class="h">Avisos que valem sempre</div>{lista(rg["avisos"])}</div>')
    pagina(corpo, "Regras de ouro")
    gl = g["glossario"]
    col = lambda xs: "".join(f'<div style="padding:9px 0;border-top:1px solid #242424"><div style="font-size:20px;font-weight:600;color:{OURO}">{esc(x["termo"])}</div><div style="font-size:18.5px;line-height:1.32;color:#D6D6D6;margin-top:3px">{esc(x["significa"])}</div></div>' for x in xs)
    for k in range(0, len(gl), 20):
        parte = gl[k:k + 20]; meio = (len(parte) + 1) // 2
        corpo = (f'<div style="position:absolute;left:80px;top:78px;width:1700px"><div class="rot">Glossário</div><h1 style="font-size:48px;margin-top:8px">Termos técnicos, em português de dono de empresa {"(continua)" if k else ""}</h1></div>'
                 f'<div style="position:absolute;left:80px;top:190px;width:860px">{col(parte[:meio])}</div><div style="position:absolute;left:980px;top:190px;width:860px">{col(parte[meio:])}</div>')
        pagina(corpo, "Glossário")


def montar(saida, previas=False):
    from playwright.sync_api import sync_playwright
    teses = (carregar("teses-a.json") or []) + (carregar("teses-b.json") or [])
    prods = (carregar("produtos-a.json") or []) + (carregar("produtos-b.json") or [])
    g = carregar("gerais.json"); c = carregar("conceitos.json"); m = carregar("matriz.json")
    capa()
    if g: como_usar(g, c)
    if c: conceitos_pg(c)
    if g: roteiro_pg(g)
    if m: matriz_pgs(m)
    reserva = len(paginas)
    for f in teses + prods: ficha(f)
    if g: gerais_pgs(g)
    # índice (inserido depois da matriz; números das páginas já contam a página do índice)
    # monta páginas do índice, desloca numeração
    corpo_idx = (f'<div style="position:absolute;left:80px;top:78px;width:1700px"><div class="rot">Navegação</div><h1 style="font-size:48px;margin-top:8px">Índice: clique para abrir a ficha</h1></div>'
                 f'<div style="position:absolute;left:80px;top:180px;width:1760px;column-count:3;column-gap:48px">{indice_html()}</div>')
    paginas.insert(reserva, f'<section class="pg"><div class="top"><img src="{LOGO}"><span class="sec">Índice</span><span class="n">--</span></div>{corpo_idx}</section>')
    # renumera os números de página impressos no topo
    num = []
    for i, p in enumerate(paginas, 1):
        num.append(re.sub(r'(<span class="n">)[^<]*(</span>)', lambda mm: f'{mm.group(1)}{i:02d}{mm.group(2)}', p, count=1))
    doc = f'<!doctype html><meta charset="utf-8"><style>{CSS}</style><body>' + "".join(num) + "</body>"
    saida = Path(saida); saida.mkdir(parents=True, exist_ok=True)
    (saida / "guia.html").write_text(doc, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome"); pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.set_content(doc); pg.wait_for_timeout(1200)
        reduzidas = pg.evaluate("""() => { const out = [];
            document.querySelectorAll('section.pg').forEach((s, i) => { s.querySelectorAll('.col').forEach(c => {
                const lim = (s.querySelector('.rodape-ficha').getBoundingClientRect().top - s.getBoundingClientRect().top) - 12;
                const w0 = +c.dataset.w; let z = 1; c.style.transform = 'none';
                while (c.getBoundingClientRect().bottom - s.getBoundingClientRect().top > lim && z > 0.8) { z -= 0.02; c.style.width = (w0 / z) + 'px'; c.style.transform = 'scale(' + z + ')'; }
                if (z < 1) out.push([i + 1, Math.round(z * 100)]); }); }); return out; }""")
        estouros = pg.evaluate("""() => [...document.querySelectorAll('section.pg')].map((s,i) => {
            const r = s.getBoundingClientRect(); let mx = 0, quem = '';
            s.querySelectorAll('*').forEach(e => { const q = e.getBoundingClientRect(); if (q.bottom - r.top > mx && e.children.length === 0 && e.textContent.trim()) { mx = q.bottom - r.top; quem = e.textContent.trim().slice(0, 40); } });
            return [i + 1, Math.round(mx), quem]; }).filter(x => x[1] > 1062)""")
        pg.pdf(path=str(saida / "Guia-do-Parceiro-Save.pdf"), width="1920px", height="1080px", print_background=True, outline=True, tagged=True)
        if previas:
            (saida / "previas").mkdir(exist_ok=True)
            for i, s in enumerate(pg.query_selector_all("section.pg"), 1):
                s.screenshot(path=str(saida / "previas" / f"{i:02d}.png"))
        b.close()
    print(f"{len(paginas)} páginas → {saida / 'Guia-do-Parceiro-Save.pdf'}")
    for e in estouros: print("AVISO página", e[0], "passa do limite:", e[1], "px perto de:", e[2])
    if reduzidas: print("fichas com fonte reduzida (página, %):", reduzidas)


if __name__ == "__main__":
    for a in sys.argv[1:]:
        if a.startswith("--conteudo="): CONT = Path(a.split("=", 1)[1])
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    montar(args[0] if args else AQUI / "saida", "--previas" in sys.argv)
