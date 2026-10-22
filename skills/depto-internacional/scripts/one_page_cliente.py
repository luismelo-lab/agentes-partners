#!/usr/bin/env python3
"""One-page confidencial do Crédito Internacional para o cliente consultar (pedido do Luis, 22/10/2026).

Fonte do texto: departamentos/produtos/credito-internacional/21-documento-interno.md (v2.3) e 22-material-externo-cliente-v2.md,
dentro das travas de references/regras-e-proibidos.md. Até o G2 não entram taxa, prazo, carência, custo nem fee. Não se usa
"fundo internacional" como nome do produto, e a Save aparece como estruturadora, nunca como credora.

Cada cópia sai nominal e numerada, com marca d'água CONFIDENCIAL, para desestimular o repasse.

Uso:  python3 one_page_cliente.py --empresa "Nome da empresa" [--copia 001] [--responsavel "nome, cargo, canal corporativo"] [--saida <pasta>]
Revisado por Produtos Internacionais, Jurídico e Qualidade/Marketing em 22/10/2026.
Decisão do Luis (22/10/2026): citar a taxa média de 7% a 10% ao ano como exemplo (definida pelo fundo) e a UBS como instituição suíça.
Confirmar com o João Mattos por escrito (perguntas-ao-dono.md) antes de enviar. Distribuição só depois do G2 ou por decisão do Luis.
Gera <saida>/Credito-Internacional-One-Page-<empresa>-<copia>.pdf e .png (prévia).
"""
import argparse, html, os, re, sys
from datetime import date
from playwright.sync_api import sync_playwright

AP = os.path.expanduser("~/agentes-partners"); PAD = os.path.join(AP, "departamentos/marketing-marca/padrao")
e = html.escape

TEXTO = {
    "titulo": "Crédito Internacional",
    "sub": "Capital internacional de médio e longo prazo para empresas brasileiras, estruturado caso a caso.",
    "oque": "Crédito de instituições financeiras dos Estados Unidos e da Suíça (UBS), em moeda forte (dólar ou franco suíço), para projetos com garantia real. Cada operação é estruturada individualmente. A instituição credora analisa, decide e libera os recursos.",
    "save": "A Save é a estruturadora da operação. Ela monta o projeto da empresa antes de levá-lo à instituição, apoia o plano de aplicação dos recursos nos aspectos fiscais, contábeis e financeiros e acompanha o processo até a liberação. A Save não concede crédito.",
    "perfil": ["Empresa consolidada, com histórico e reputação no setor", "Faturamento anual a partir de cerca de R$ 50 milhões, comprovado",
               "Necessidade a partir de cerca de US$ 5 milhões", "Garantia real robusta, avaliada caso a caso", "Projeto claro de uso dos recursos e capacidade de pagamento"],
    "etapas": [("Conversa inicial", "necessidade, porte, garantias e projeto"), ("Confidencialidade", "NDA, autorização de envio de dados ao exterior e documentos"),
               ("Estruturação", "plano de aplicação, capacidade de pagamento e garantias"), ("Apresentação", "o caso vai à instituição, com o empresário"),
               ("Análise e decisão", "pela instituição credora"), ("Contrato e liberação", "na forma e no cronograma definidos pela instituição")],
    "garantias": "Imóveis, terras produtivas e fazendas, recebíveis, marcas avaliadas e garantias de terceiros. A garantia não precisa estar em nome da empresa. Garantias alternativas, como recebíveis, são avaliadas caso a caso pela instituição.",
    "docs": "Kit bancário, balancetes e DREs dos últimos 2 anos, declarações de impostos, comprovação de faturamento, detalhe das garantias, histórico do empresário e a necessidade de capital com o projeto.",
    "saber": ["Taxas médias de referência: de 7% a 10% ao ano, em moeda estrangeira, apenas como exemplo. A taxa de cada operação é definida pelo fundo (instituição credora) após a análise de crédito e não inclui variação cambial, proteção cambial (hedge), impostos e custos da operação.",
              "As condições de custo vêm por escrito antes de qualquer compromisso.",
              "A operação é em moeda estrangeira. O efeito do câmbio é avaliado com a empresa em cada caso.",
              "É uma operação de alguns meses, apoiada em documentos. Não é solução imediata de caixa, e a aprovação depende da instituição.",
              "O produto está em fase inicial, com poucos casos selecionados."],
    "aviso": "Material informativo e preliminar, com informações válidas na data de emissão. Não constitui oferta de crédito nem de investimento, oferta pública, recomendação de investimento ou promessa de aprovação. A Save Co. não é instituição financeira e não concede crédito. Operações sujeitas à análise e à aprovação da instituição credora, com condições definidas caso a caso.",
}


def pagina(empresa, copia, hoje, resp):
    T = TEXTO; f = PAD + "/fontes"
    selo = f"CONFIDENCIAL · USO EXCLUSIVO DE {empresa.upper()} · NÃO COMPARTILHAR, COPIAR OU ENCAMINHAR"
    css = f"""
@font-face{{font-family:'IBM Plex Sans';src:url('file://{f}/IBMPlexSans-Regular.ttf');font-weight:400}}
@font-face{{font-family:'IBM Plex Sans';src:url('file://{f}/IBMPlexSans-SemiBold.ttf');font-weight:600}}
@font-face{{font-family:'IBM Plex Mono';src:url('file://{f}/IBMPlexMono-Regular.ttf');font-weight:400}}
@page{{size:A4;margin:0}} *{{box-sizing:border-box}} html{{overflow:hidden;width:210mm}}
body{{margin:0;width:210mm;height:297mm;font:400 9.1pt/1.4 'IBM Plex Sans';color:#0F1115;background:#FFFFFF;position:relative;overflow:hidden}}
.marca{{position:absolute;top:118mm;left:-20mm;width:250mm;text-align:center;transform:rotate(-32deg);font:600 64pt 'IBM Plex Sans';color:rgba(181,138,31,.075);letter-spacing:6pt;pointer-events:none}}
.faixa{{background:#0F1115;color:#F3CD60;font:400 7.6pt 'IBM Plex Mono';letter-spacing:.9pt;text-align:center;padding:2.6mm 8mm}}
.miolo{{padding:6mm 14mm 0 14mm}}
.topo{{display:flex;justify-content:space-between;align-items:center;border-bottom:2.2pt solid #F3CD60;padding-bottom:4mm}}
.topo img{{height:8mm}} .rot{{font:400 7.4pt 'IBM Plex Mono';letter-spacing:1.2pt;text-transform:uppercase;color:#B58A1F}}
h1{{font-size:22pt;font-weight:600;margin:4mm 0 1mm;letter-spacing:-.3pt}} .sub{{color:#4A4F58;font-size:10.5pt;margin:0 0 4mm}}
.duas{{display:grid;grid-template-columns:1fr 1fr;gap:5mm}} h2{{font-size:10.5pt;font-weight:600;margin:0 0 1.6mm;color:#0F1115}}
h2 span{{color:#B58A1F;font:400 8pt 'IBM Plex Mono';margin-right:2mm}}
.bloco{{margin-bottom:3.2mm}} p{{margin:0;color:#2B2F36}} ul{{margin:0;padding-left:4.2mm}} li{{margin:0 0 .9mm;color:#2B2F36}}
.etapas{{display:grid;grid-template-columns:repeat(6,1fr);gap:2mm;margin:0 0 3.4mm}}
.et{{border-top:2pt solid #F3CD60;padding-top:1.6mm}} .et b{{display:block;font-size:8.6pt}} .et small{{color:#4A4F58;font-size:7.6pt;line-height:1.3;display:block}}
.et i{{font:400 7pt 'IBM Plex Mono';color:#B58A1F;font-style:normal}}
.saber{{background:#FBF1D7;border-left:3pt solid #F3CD60;padding:2.6mm 4mm;border-radius:2mm}}
.rodape{{position:absolute;bottom:0;left:0;right:0}}
.aviso{{padding:0 14mm 2.4mm;color:#4A4F58;font-size:7.4pt;line-height:1.35}}
.cop{{display:flex;justify-content:space-between;padding:0 14mm 2.4mm;font:400 7.2pt 'IBM Plex Mono';color:#838892}}
"""
    li = lambda xs: "".join(f"<li>{e(x)}</li>" for x in xs)
    et = "".join(f'<div class="et"><i>{i:02d}</i><b>{e(a)}</b><small>{e(b)}</small></div>' for i, (a, b) in enumerate(T["etapas"], 1))
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{css}</style></head><body>
<div class="marca">CONFIDENCIAL</div>
<div class="faixa">{e(selo)}</div>
<div class="miolo">
<div class="topo"><img src="file://{PAD}/logo-save-fundo-claro.png" alt="Save Co."></div>
<h1>{e(T['titulo'])}</h1><p class="sub">{e(T['sub'])}</p>
<div class="duas">
 <div><div class="bloco"><h2><span>01</span>O que é</h2><p>{e(T['oque'])}</p></div>
      <div class="bloco"><h2><span>02</span>O papel da Save</h2><p>{e(T['save'])}</p></div></div>
 <div><div class="bloco"><h2><span>03</span>Para quem foi desenhado</h2><ul>{li(T['perfil'])}</ul></div></div>
</div>
<div class="bloco"><h2><span>04</span>Como funciona</h2></div><div class="etapas">{et}</div>
<div class="duas">
 <div class="bloco"><h2><span>05</span>Garantias avaliadas</h2><p>{e(T['garantias'])}</p></div>
 <div class="bloco"><h2><span>06</span>Documentação</h2><p>{e(T['docs'])}</p></div>
</div>
<div class="bloco saber"><h2><span>07</span>O que você precisa saber</h2><ul>{li(T['saber'])}</ul></div>
<div class="bloco"><h2><span>08</span>Próximo passo</h2><p>Para avaliar o seu caso, agende uma conversa inicial de 30 minutos com {e(resp)}.</p></div>
</div>
<div class="rodape">
<div class="aviso"><b>Confidencial.</b> Documento de uso exclusivo e confidencial de {e(empresa)}. Pedimos que não seja reproduzido nem compartilhado com terceiros. As obrigações de sigilo entre as partes são as do acordo de confidencialidade (NDA). {e(T['aviso'])}</div>
<div class="cop"><span>Cópia nº {e(copia)} · preparada para {e(empresa)} · {e(hoje)}</span><span>Save Co. · Área Partners</span></div>
<div class="faixa">{e(selo)}</div>
</div></body></html>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--empresa", required=True); ap.add_argument("--copia", default="001")
    ap.add_argument("--saida", default=os.getcwd())
    ap.add_argument("--responsavel", default="Luis Fernando de Melo, Gerente Comercial da Área Partners, pelo e-mail luis.melo@savecompany.com.br")
    a = ap.parse_args()
    hoje = date.today().strftime("%d/%m/%Y"); os.makedirs(a.saida, exist_ok=True)
    base = os.path.join(a.saida, "Credito-Internacional-One-Page-" + re.sub(r"[^A-Za-z0-9]+", "-", a.empresa).strip("-") + f"-{a.copia}")
    open(base + ".html", "w").write(pagina(a.empresa, a.copia, hoje, a.responsavel))
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 794, "height": 1123}, device_scale_factor=2)
        pg.goto("file://" + base + ".html"); pg.wait_for_timeout(300)
        pg.pdf(path=base + ".pdf", format="A4", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        pg.screenshot(path=base + ".png", full_page=True); n = pg.evaluate("document.body.scrollHeight"); b.close()
    os.remove(base + ".html"); print("ok", base + ".pdf", "altura", n)
