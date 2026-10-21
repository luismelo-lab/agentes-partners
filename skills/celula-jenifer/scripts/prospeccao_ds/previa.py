"""Prévia em PNG (Design System Save, modo escuro de painel) da estratégia de prospecção D&S."""
import collections, html, os, pickle, statistics as st
from playwright.sync_api import sync_playwright

S = os.environ.get("PROSPECCAO_DS", os.path.expanduser("~/agentes-partners/departamentos/intel-comercial/prospeccao-ds"))  # dados (fora do repositório); AP = os.path.expanduser("~/agentes-partners")
M = pickle.load(open(S + "/modelo.pkl", "rb")); cli, anc, pros = M["cli"], M["anc"], M["pros"]
FONTES = AP + "/departamentos/marketing-marca/padrao/fontes"; LOGO = AP + "/departamentos/marketing-marca/padrao/logo-save-fundo-escuro.png"
e = html.escape
def mi(v): return f"R$ {v/1e6:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")
def mil(v): return mi(v) if v >= 1e6 else f"R$ {v/1e3:,.0f} mil".replace(",", ".")
def n(v): return f"{v:,}".replace(",", ".")
def pct(v): return f"{v:.0f}%"
import re as _re
def curto(d): return _re.sub(r'^(Comércio (varejista|atacadista) de |Fabricação de |Comércio varejista de mercadorias em geral, com predominância de )','',d or '').replace('produtos alimentícios','alimentos').capitalize()

# tiers
for p in pros:
    s = p["similaridade"]; p["tier"] = "A" if s >= 90 else "B" if s >= 85 else "C" if s >= 80 else "D"
ganhos = [x for x in cli if x["fase"] == "Ganho"]; canc = [x for x in cli if x["fase"] == "Cancelado"]
tier = collections.Counter(p["tier"] for p in pros); geo = collections.Counter(p["nivel_geo"] for p in pros)
med_ref = st.median(p["ref"] for p in pros if p["tier"] == "A") if tier["A"] else 0
val_g = [x["hs"]["primeiro_ganho"] for x in anc if x["hs"]["primeiro_ganho"]]

# perfil: segmentos dos ganhos
seg = collections.defaultdict(lambda: [0, 0, []])
for x in cli:
    if not x["rf"]: continue
    k = (x["rf"]["cnae"][:4], x["rf"]["cnae_desc"])
    if x["fase"] == "Ganho": seg[k][0] += 1; seg[k][2].append(x["hs"]["primeiro_ganho"] or 0)
    elif x["fase"] == "Cancelado": seg[k][1] += 1
top_seg = sorted(seg.items(), key=lambda z: -z[1][0])[:8]
maxg = max(v[0] for _, v in top_seg)

# cidades: ganhos × prospects
cg = collections.Counter(x["rf"]["municipio"] for x in anc); cp = collections.Counter(p["municipio"] for p in pros)
cpa = collections.Counter(p["municipio"] for p in pros if p["tier"] == "A")
top_cid = [c for c, _ in cg.most_common(8)]

# matriz de foco (similaridade × potencial de referência)
corte_pot = st.median(p["ref"] for p in pros)
quad = collections.Counter(("alta" if p["similaridade"] >= 85 else "baixa", "alto" if p["ref"] >= corte_pot else "baixo") for p in pros)

# amostra: prioridade = tier A, nível geográfico mais próximo, maior potencial esperado
ordem = sorted(pros, key=lambda p: (p["tier"], p["nivel_geo"], -p["potencial"]))
amostra = ordem[:12]

def barra(v, m, cor="var(--ouro)"): return f'<div class="trilho"><div class="barra" style="width:{max(2, v / m * 100):.0f}%;background:{cor}"></div></div>'

css = f"""
@font-face{{font-family:'IBM Plex Sans';src:url('file://{FONTES}/IBMPlexSans-Regular.ttf');font-weight:400}}
@font-face{{font-family:'IBM Plex Sans';src:url('file://{FONTES}/IBMPlexSans-SemiBold.ttf');font-weight:600}}
@font-face{{font-family:'IBM Plex Mono';src:url('file://{FONTES}/IBMPlexMono-Regular.ttf');font-weight:400}}
:root{{--fundo:#000;--cartao:#171717;--borda:#2A2A2A;--texto:#F5F5F5;--t2:#A1A1A1;--t3:#6B6B6B;--ouro:#F3CD60;--ouro2:rgba(243,205,96,.14)}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--fundo);color:var(--texto);font:400 15px/1.45 'IBM Plex Sans';width:1600px;padding:40px 48px}}
.topo{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:3px solid var(--ouro);padding-bottom:14px;margin-bottom:26px}}
.topo img{{height:30px}} h1{{font-size:30px;margin:0;font-weight:600}} .sub{{color:var(--t2);font-size:14px;margin-top:4px}}
.rot{{font:400 11px 'IBM Plex Mono';letter-spacing:.12em;text-transform:uppercase;color:var(--ouro)}}
.kpis{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:22px}}
.k{{background:var(--cartao);border:1px solid var(--borda);border-radius:12px;padding:16px 18px}}
.k .v{{font:600 30px 'IBM Plex Mono';margin:6px 0 2px}} .k .d{{color:var(--t2);font-size:13px}}
.grade{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:14px}}
.c{{background:var(--cartao);border:1px solid var(--borda);border-radius:12px;padding:18px 20px}}
.c h3{{font-size:17px;margin:4px 0 12px;font-weight:600}}
.lin{{display:grid;grid-template-columns:1.6fr 2fr .55fr .5fr;gap:10px;align-items:center;font-size:13px;margin:7px 0}}
.lin .n{{color:var(--t2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}} .num{{font-family:'IBM Plex Mono';text-align:right}}
.trilho{{height:10px;background:#222;border-radius:4px}} .barra{{height:10px;border-radius:4px}}
.cab{{color:var(--t3);font:400 11px 'IBM Plex Mono';text-transform:uppercase;letter-spacing:.06em}}
.mq{{display:grid;grid-template-columns:110px 1fr 1fr;gap:8px;font-size:13px}} .mq div{{padding:12px;border-radius:8px;background:#111;border:1px solid var(--borda)}}
.mq .foco{{background:var(--ouro2);border-color:var(--ouro)}} .mq .t{{background:none;border:0;color:var(--t2)}} .mq b{{font:600 22px 'IBM Plex Mono';display:block}}
table{{width:100%;border-collapse:collapse;font-size:12.5px}} th{{text-align:left;color:var(--t3);font:400 10.5px 'IBM Plex Mono';text-transform:uppercase;letter-spacing:.06em;padding:8px;border-bottom:1px solid #3A3A3A}}
td{{padding:8px;border-bottom:1px solid var(--borda);vertical-align:top}} td.num{{text-align:right}} .tag{{display:inline-block;padding:1px 7px;border-radius:4px;background:var(--ouro2);color:var(--ouro);font:400 11px 'IBM Plex Mono'}}
.rod{{color:var(--t3);font-size:12px;margin-top:16px;line-height:1.5}}
"""

kp = [("Empresas da D&S analisadas", n(len(cli)), f"{n(len(ganhos))} ganhas · {n(len(canc))} canceladas"),
      ("Novos clientes potenciais", n(len(pros)), "Lucro Real confirmado · sem cliente D&S nem negócio no HubSpot"),
      ("Prioridade A", n(tier["A"]), "similaridade ≥ 90% com um ganho"),
      ("Mesmo bairro ou região", n(geo["1 · Mesmo bairro"] + geo["2 · Mesma região da cidade"]), "perto de um cliente ganho"),
      ("Crédito típico (A)", mil(med_ref), f"mediana dos ganhos D&S: {mil(st.median(val_g))}")]

seg_html = "".join(f'<div class="lin"><span class="n">{e(curto(d or c)[:34])}</span>{barra(g, maxg)}<span class="num">{g}</span><span class="num">{pct(100*g/(g+cc) if g+cc else 0)}</span></div>'
                   for (c, d), (g, cc, _) in top_seg)
geo_ord = ["1 · Mesmo bairro", "2 · Mesma região da cidade", "3 · Mesma cidade", "4 · Cidades vizinhas"]
mg = max(geo.values())
geo_html = "".join(f'<div class="lin"><span class="n">{e(k[4:])}</span>{barra(geo[k], mg)}<span class="num">{n(geo[k])}</span><span class="num">{n(sum(1 for p in pros if p["nivel_geo"]==k and p["tier"]=="A"))}</span></div>' for k in geo_ord)
mc = max(cp[c] for c in top_cid)
cid_html = "".join(f'<div class="lin"><span class="n">{e(c.title())}</span>{barra(cp[c], mc)}<span class="num">{cg[c]}</span><span class="num">{n(cpa[c])}</span></div>' for c in top_cid)
mq = f"""<div class="mq"><div class="t"></div><div class="t">Potencial alto (≥ {mil(corte_pot)})</div><div class="t">Potencial baixo</div>
<div class="t">Similaridade alta (≥ 85%)</div><div class="foco"><b>{n(quad[('alta','alto')])}</b>Foco: atacar primeiro</div><div><b>{n(quad[('alta','baixo')])}</b>Volume: cadência leve</div>
<div class="t">Similaridade baixa</div><div><b>{n(quad[('baixa','alto')])}</b>Qualificar antes</div><div><b>{n(quad[('baixa','baixo')])}</b>Aguardar</div></div>"""
linhas = "".join(f"""<tr><td>{e((p['fantasia'] or p['razao'] or '')[:30])}<br><span class="cab">{e(p['cnae_desc'][:38])}</span></td>
<td>{e((p['bairro'] or '—').title()[:22])}<br><span class="cab">{e(p['municipio'].title())}</span></td><td><span class="tag">{e(p['nivel_geo'][4:])}</span><br><span class="cab">de {e((p['ancora_geo']['rf']['fantasia'] or p['ancora_geo']['rf']['razao'] or '')[:22])}</span></td>
<td>{e((p['exemplo']['rf']['fantasia'] or p['exemplo']['rf']['razao'] or '')[:28])}<br><span class="cab">{e((p['exemplo']['bairro'] or '').title()[:20])} · {e(p['exemplo']['rf']['municipio'].title())}</span></td>
<td class="num">{p['similaridade']:.0f}%</td><td class="num">{mil(p['ref'])}</td><td class="num">{p['conversao']*100:.0f}%</td><td class="num">{mil(p['potencial'])}</td></tr>""" for p in amostra)

pagina = f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>
<div class="topo"><div><div class="rot">Área Partners · Prévia parcial para aprovação · {e(os.environ.get("PARCIAL",""))}</div><h1>Estratégia de prospecção · Parceiro D&S</h1>
<div class="sub">Base: planilha da D&S ({n(len(cli))} CNPJs), HubSpot de 16/10/2026 e Receita Federal (CNPJ, set/2026). Pré-análise, sem promessa de valor.</div></div><img src="file://{LOGO}"></div>
<div class="kpis">{''.join(f'<div class="k"><div class="rot">{a}</div><div class="v">{b}</div><div class="d">{c}</div></div>' for a,b,c in kp)}</div>
<div class="grade">
<div class="c"><div class="rot">1 · Perfil do cliente ganho</div><h3>Onde a D&S ganha</h3><div class="lin cab"><span>Segmento</span><span></span><span class="num">Ganhos</span><span class="num">Conversão</span></div>{seg_html}
<div class="rod">{pct(100*sum(1 for x in anc if x['hs']['regime']=='Lucro Real')/len(anc))} dos ganhos no Lucro Real · capital social mediano {mil(st.median(x['rf']['capital'] or 0 for x in anc))}</div></div>
<div class="c"><div class="rot">3 · Geografia</div><h3>Prospects perto de um cliente ganho</h3><div class="lin cab"><span>Nível</span><span></span><span class="num">Total</span><span class="num">Prior. A</span></div>{geo_html}
<div class="lin cab" style="margin-top:16px"><span>Cidade</span><span></span><span class="num">Ganhos</span><span class="num">Prior. A</span></div>{cid_html}</div>
<div class="c"><div class="rot">4 · Matriz de foco</div><h3>Similaridade × potencial</h3>{mq}
<div class="rod">Similaridade: segmento (40%), capital (20%), porte (15%), idade (10%), geografia (10%) e natureza jurídica (5%), comparada a cada um dos {n(len(anc))} ganhos.
Potencial de referência: média dos 10 ganhos mais parecidos (1º diagnóstico, sem duplicidade). Chance: conversão do segmento na carteira da D&S.</div></div>
</div>
<div class="c"><div class="rot">2 e 4 · Amostra da lista (primeiras 12 de {n(len(pros))}, ordenadas por prioridade, proximidade e potencial)</div>
<table><tr><th>Empresa a prospectar</th><th>Bairro · cidade</th><th>Proximidade</th><th>Empresa exemplo (ganho D&S)</th><th class="num">Similaridade</th><th class="num">Crédito de referência</th><th class="num">Chance</th><th class="num">Potencial esperado</th></tr>{linhas}</table></div>
<div class="rod">Estimativa preliminar sujeita a validação técnica: o crédito de referência vem dos ganhos parecidos, não de diagnóstico da empresa. Regime: Lucro Real no último ano declarado à Receita (consulta Minha Receita). Fora da lista: clientes da D&S (qualquer fase), toda empresa com negócio no HubSpot (qualquer parceiro), Simples, MEI e empresas em recuperação judicial ou falência.</div>
</body></html>"""
open(S + "/previa.html", "w").write(pagina)
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=1.5)
    pg.goto("file://" + S + "/previa.html"); pg.wait_for_timeout(400); pg.screenshot(path=S + "/previa-ds.png", full_page=True); b.close()
print("ok", S + "/previa-ds.png")
