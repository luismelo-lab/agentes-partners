#!/usr/bin/env python3
"""Monta a apresentação de um diagnóstico a partir do conteúdo já revisado pelo time tributário.

Entrada : <pasta>/diagnostico.json  (modelo: modelo-diagnostico.json; fluxo: FLUXO.md)
Saída   : <pasta>/<Nome>-Apresentacao.json, .pdf, .pptx e previas/ (motor em departamentos/marketing/kit/motor)
Macros  : no campo "ordem", um item {"macro": "..."} vira slide pronto:
            tabela_teses · processos · case_segmento
          Qualquer outro item é um slide do motor (tipos em marketing/kit/motor/LEIA-ME.md).
Case    : biblioteca-cases/cases.json, pelo segmento do CNAE. Só entra case aprovado; com --rascunho entra o não
          aprovado, marcado "Rascunho". Sem case, o slide sai e o script avisa.
Uso     : python3 gerar_apresentacao.py <pasta> [--rascunho] [--sem-pptx]
Só gera arquivos locais; nada é enviado."""
import json, os, re, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MOTOR = AQUI.parent.parent / "marketing" / "kit" / "motor"
if not MOTOR.exists():
    MOTOR = Path.home() / "agentes-partners" / "departamentos" / "marketing" / "kit" / "motor"
sys.path.insert(0, str(MOTOR))
LIB = AQUI / "biblioteca-cases" / "cases.json"
def achar_node_path():
    """node_modules com pptxgenjs: NODE_PATH do ambiente, ~/agentes-partners/node_modules ou ~/.partners-node/node_modules.
    Se nenhum existir: mkdir -p ~/.partners-node && cd ~/.partners-node && npm i pptxgenjs --save-exact (versão 3.12)"""
    for c in (os.environ.get("NODE_PATH"), str(Path.home() / "agentes-partners" / "node_modules"), str(Path.home() / ".partners-node" / "node_modules")):
        if c and (Path(c) / "pptxgenjs" / "package.json").exists(): return c
    return os.environ.get("NODE_PATH", "")
RODAPE = ("Pré-análise sujeita a validação técnica e jurídica. Valores são estimativas preliminares e dependem da documentação e da execução. "
          "Contrato de êxito, sem desembolso inicial. Resultados de outros clientes não garantem resultado futuro.")


def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def valor_curto(v):
    return (f"R$ {v/1e6:.0f} milhões".replace(".", ",") if v >= 1e6 else f"R$ {v/1e3:.0f} mil")


def segmento_do_cnae(cnae, lib):
    c = re.sub(r"\D", "", cnae or "")
    for chave, s in lib["segmentos"].items():
        if any(c.startswith(d.replace(".", "")) for d in s["cnae_divisoes"]):
            return chave
    return None


def escolher_case(d, lib, rascunho):
    seg = d["cliente"].get("segmento") or segmento_do_cnae(d["cliente"].get("cnae"), lib)
    cand = [c for c in lib["cases"] if c.get("segmento") == seg and (c.get("aprovado") or rascunho)]
    if not cand: return seg, None
    codigos = {t["codigo"] for t in d["teses"] if t.get("codigo") and t["veredito"] in ("manter", "ajustar")}
    pont = lambda c: ((c.get("aprovado") is True) * 100 + len(codigos & set(c.get("teses", []))) * 10 + (c.get("tipo") != "agregado_segmento") * 20
                      + (5 if c.get("regime") == d["cliente"].get("regime") else 0))
    return seg, max(cand, key=pont)


def m_tabela_teses(d, av):
    linhas = [[t["nome"], t["o_que_e"], t["valor_texto"], t["situacao"]] for t in d["teses"] if t["veredito"] != "retirar"]
    return {"tipo": "tabela", "rotulo": "Teses revisadas", "titulo": "Cada tese, o que ela é e em que ponto está",
            "colunas": ["Tese", "O que é", "Valor", "Situação"], "linhas": linhas, "destaque_coluna": 3,
            "nota": "Valores são estimativas de análise parcial. Só mostramos número onde há base confirmada; as linhas se sobrepõem e por isso não somamos.",
            "notas": d.get("tabela_notas", "")}


def m_processos(d, av):
    return {"tipo": "tabela", "rotulo": "Processos já ajuizados", "titulo": "O que a empresa já tem na Justiça, e como respeitamos isso",
            "colunas": ["Tese", "Situação", "O que isso significa agora"], "linhas": [[p["tese"], p["situacao"], p["efeito"]] for p in d["processos"]],
            "nota": "Não pedimos de novo o que já foi decidido (litispendência e coisa julgada). Os prazos de habilitação são conferidos pelo advogado.", "notas": d.get("processos_notas", "")}


def m_case(d, av, lib=None, rascunho=False):
    seg, c = escolher_case(d, lib, rascunho)
    if not c:
        av.append(f"Sem case {'(nem rascunho) ' if rascunho else 'aprovado '}para o segmento '{seg}': slide 'Quem já fez' fora da apresentação."); return None
    if not c.get("aprovado"): av.append(f"Case {c['id']} NÃO aprovado (rascunho): definição de 'reconectado' e data-base a confirmar antes de enviar ao cliente.")
    return {"tipo": "caso", "rotulo": ("Rascunho · " if not c.get("aprovado") else "") + "Quem já fez",
            "titulo": f"No seu segmento: {c['titulo_cliente']}",
            "linhas": [{"rotulo": "Perfil", "texto": c["perfil"]}, {"rotulo": "O que foi feito", "texto": c["resumo_cliente"]},
                       {"rotulo": "Resultado", "texto": f"{valor_curto(c['valor'])} {c.get('valor_tipo', 'recuperado')}s no segmento (período {c['periodo']}; data-base {c['data_base']})"},
                       {"rotulo": "Leitura", "texto": "Cada empresa tem um perfil e um resultado próprios; o número mostra o segmento, não a sua empresa."}],
            "nota": "Resultados de outros clientes não garantem resultado futuro.", "notas": f"Case {c['id']} ({'aprovado' if c.get('aprovado') else 'RASCUNHO, não enviar'}). Fonte: {c['fonte']}."}


def montar(d, rascunho=False):
    lib = json.load(open(LIB)); av = []; S = []
    for item in d["ordem"]:
        m = item.get("macro")
        if m == "tabela_teses": S.append(m_tabela_teses(d, av))
        elif m == "processos" and d.get("processos"): S.append(m_processos(d, av))
        elif m == "case_segmento":
            s = m_case(d, av, lib, rascunho)
            if s: S.append(s)
        elif not m: S.append(item)
    cl = d["cliente"]
    return {"titulo_doc": f"{cl['nome_curto']} · Diagnóstico de revisão tributária", "rodape": RODAPE, "slides": S}, av


def main(pasta, rascunho=False, pptx=True):
    pasta = Path(pasta).resolve(); d = json.load(open(pasta / "diagnostico.json"))
    doc, avisos = montar(d, rascunho); nome = d["cliente"]["nome_curto"].replace(" ", "-") + "-Apresentacao"
    js = pasta / f"{nome}.json"; json.dump(doc, open(js, "w"), ensure_ascii=False, indent=1)
    import deck_html
    avisos += [f"layout: {a}" for a in deck_html.gerar(js, pasta / f"{nome}.pdf", pasta / "previas" / nome)]
    if pptx:
        r = subprocess.run(["node", str(MOTOR / "deck_pptx.js"), str(js), str(pasta / f"{nome}.pptx")],
                           env={**os.environ, "NODE_PATH": achar_node_path()}, capture_output=True, text=True)
        if r.returncode: avisos.append("pptx: " + r.stderr.strip()[-300:])
    print(f"{len(doc['slides'])} slides → {pasta / nome}.pdf/.pptx")
    for a in avisos: print("AVISO", a)


if __name__ == "__main__":
    main(sys.argv[1], "--rascunho" in sys.argv, "--sem-pptx" not in sys.argv)
