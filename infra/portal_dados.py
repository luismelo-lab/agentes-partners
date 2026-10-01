#!/usr/bin/env python3
"""Monta o dados.json do portal "Central Partners" (MVP de 30/09/2026) a partir das saídas dos agentes.

Só leva o necessário para o time acompanhar: números, pedidos em aberto e os 10 primeiros itens de cada fila.
Nada de dados bancários, textos de pareceres ou conversas brutas do WhatsApp.
Uso: python3 portal_dados.py → ~/agentes-partners/portal/dados.json
"""
import glob, json, os
from datetime import datetime

AP = os.path.expanduser("~/agentes-partners")
ult = lambda p: (sorted(glob.glob(os.path.join(AP, p))) or [None])[-1]
ler = lambda p: json.load(open(p)) if p else {}


def whatsapp():
    t = ler(ult("celulas/whatsapp-triagem-*.json"))
    out = {"rodada": t.get("rodada"), "leitura_geral": t.get("leitura_geral"), "pessoas": {}}
    for k, P in (t.get("pessoas") or {}).items():
        it = [i for i in P.get("itens", []) if i.get("status") != "sem_acao"]
        out["pessoas"][k] = {"conversas": P.get("conversas", 0), "leitura": P.get("leitura"),
                             "itens": [{c: i.get(c) for c in ("chat", "master", "status", "aguardando_h", "o_que_pede", "rota", "proximo_passo", "prazo", "negocio", "link")} for i in it]}
    return out


def recuperador():
    f = ler(ult("celulas/geovana/recuperador/fila-*.json"))
    top = [r for r in f.get("top", []) if r.get("lote") == 1] or f.get("top", [])[:20]
    return {"fila": f.get("fila"), "esperado_total": f.get("esperado_total"), "esperado_lote1": f.get("esperado_lote1"),
            "lote": [{"negocio": r["negócio"], "parceiro": r["parceiro"], "tipo": r["tipo"], "segmento": r.get("segmento (matriz)") or r.get("segmento"),
                      "uf": r.get("uf"), "esperado": r.get("honorário esperado (look-alike)"), "taxa": r.get("taxa de sucesso dos parecidos"),
                      "decisao": r.get("decisão da Geovana") or "", "link": r["link"]} for r in top[:10]]}


def revisor():
    r = ler(ult("celulas/geovana/revisor/revisor-*.json")).get("resumo", {})
    nomes = {"B": "Manutenção e ressarcimento (B)", "CST": "Erro de CST", "EX_ICMS": "Exclusão do ICMS", "C": "Crédito presumido (C)",
             "ST_REST": "Restituição de ICMS-ST", "PREV": "Previdenciárias", "EX_ST": "Exclusão do ICMS-ST"}
    return {"selecionados": r.get("selecionados"), "revisados": r.get("revisados"), "lacunas": r.get("lacunas"),
            "alta": (r.get("por_prioridade") or {}).get("alta"),
            "por_tese": sorted([{"tese": nomes.get(k, k), "n": v.get("n", 0), "alta": v.get("alta", 0)} for k, v in (r.get("por_tese") or {}).items()], key=lambda x: -x["n"])}


def qualidade():
    """Alerta da última auditoria de promessas (lê o relatório da área; some se não houver)."""
    f = ult("departamentos/qualidade/auditorias/*-teste-auditar_texto.md") or ult("departamentos/qualidade/auditorias/*.md")
    if not f: return []
    import re
    t = open(f, encoding="utf-8").read()
    m = re.search(r"(\d{1,3}[.,]\d)\s*%[^\n]{0,120}anexos? de diagn", t) or re.search(r"anexos? de diagn[^\n]{0,120}?(\d{1,3}[.,]\d)\s*%", t)
    data = os.path.basename(f)[:10]
    txt = (f"{m.group(1)}% dos anexos de diagnóstico prometem resultado (auditoria de {data[8:10]}/{data[5:7]}): revisar o modelo com Técnico e Jurídico."
           if m else f"Ver a última auditoria de promessas ({data[8:10]}/{data[5:7]}).")
    return [{"area": "Qualidade", "texto": txt}]


def gestao():
    t = ler(ult("departamentos/resultados/dados/texto-*.json"))
    dec = open(os.path.join(AP, "conselho/decisoes.md")).read().splitlines()
    pend = [l.split("|")[1].strip() for l in dec if l.startswith("| D") and "| pendente |" in l]
    o = ler(ult("departamentos/operacoes-canal/conferencia-repasses-*.json"))
    c = ler(ult("departamentos/contratos/controle-contratos-*.json"))
    b = ler(ult("departamentos/dados/dados-bi-*.json"))
    return {"manchete": t.get("manchete"), "periodo": t.get("periodo"), "decisoes_pendentes": list(dict.fromkeys(pend)),
            "alertas": [
                {"area": "Operações de Canal", "texto": f"{o.get('duplicidade_grupos', 0)} possíveis cards duplicados em ganhos; {o.get('status', {}).get('Bloqueado', 0)} ganhos sem dado para calcular o repasse."},
                {"area": "Contratos", "texto": f"{(c.get('em_contrato') or {}).get('negocios', 0)} negócios em etapa de contrato, {(c.get('em_contrato') or {}).get('com_alerta', 0)} com alerta."},
                *qualidade(),
                {"area": "Dados & BI", "texto": f"% de honorário preenchido em {next((x['ganho'] for x in b.get('completude', []) if x['campo'] == '% honorário'), '—')}% dos ganhos."}],
            "masters": [{"parceiro": s["parceiro"], "saude": s["saude"], "sinal": s["sinal"], "abertos": s["abertos"], "abertos_rs": s["abertos_rs"],
                         "ganhos_90d": s["ganhos_90d"], "parados": s["abertos_parados"]} for s in b.get("scorecard", [])]}


def demandas():
    """Registro único (lib/registro_demandas.py): abertas por pessoa e a mais antiga."""
    f = os.path.join(AP, "registro/demandas.json")
    if not os.path.exists(f): return {}
    R = json.load(open(f)); out = {}
    for d in R["demandas"].values():
        if d["status"] in ("responder", "acompanhar", "em_analise", "aguardando_aprovacao"):
            x = out.setdefault(d["pessoa"], {"abertas": 0, "responder": 0, "mais_antiga": None})
            x["abertas"] += 1; x["responder"] += d["status"] == "responder"
            if not x["mais_antiga"] or (d.get("aberta_em") or "") < x["mais_antiga"]: x["mais_antiga"] = d.get("aberta_em")
    return out


def conselho_pendentes():
    """Decisões com status 'pendente' (coluna 5 do decisoes.md); D7 sai quando há D7-b."""
    out = []
    for l in open(os.path.join(AP, "conselho/decisoes.md")).read().splitlines():
        c = [x.strip() for x in l.split("|")]
        if len(c) > 6 and c[1].startswith("D") and c[5] == "pendente":
            out.append({"id": c[1], "data": c[2], "ata": c[3], "texto": c[4].replace("**", ""), "obs": c[6]})
    ids = {d["id"] for d in out}
    out = [d for d in out if not (d["id"] == "D7" and "D7-b" in ids)]
    vistos, uniq = set(), []
    for d in out:
        if d["id"] not in vistos: vistos.add(d["id"]); uniq.append(d)
    return uniq


def demandas_lista():
    f = os.path.join(AP, "registro/demandas.json")
    if not os.path.exists(f): return []
    R = json.load(open(f))
    return [{k: d.get(k) for k in ("id", "pessoa", "origem", "titulo", "master", "o_que_pede", "rota", "proximo_passo", "prazo", "status", "aberta_em", "negocio", "link", "urgente", "id_origem")}
            for d in sorted(R["demandas"].values(), key=lambda d: d.get("aberta_em") or "")
            if d["status"] in ("responder", "acompanhar", "em_analise", "aguardando_aprovacao")]


def catalogo():
    C = json.load(open(os.path.expanduser("~/.claude/skills/central-agentes/references/catalogo.json")))["tipos"]
    return [{"codigo": k, "rotulo": v["rotulo"], "celula": v["celula"], "entrega": v["entrega"], "precisa": v["precisa"]} for k, v in C.items()]


def lote_completo():
    f = ler(ult("celulas/geovana/recuperador/fila-*.json"))
    top = [r for r in f.get("top", []) if r.get("lote") == 1] or f.get("top", [])[:20]
    return [{"deal": r["link"].rsplit("/", 1)[-1], "negocio": r["negócio"], "parceiro": "Fora do roster" if r["parceiro"].startswith("Outros") else r["parceiro"],
             "tipo": r["tipo"], "segmento": r.get("segmento (matriz)") or r.get("segmento"), "uf": r.get("uf"), "esperado": r.get("honorário esperado (look-alike)"),
             "taxa": r.get("taxa de sucesso dos parecidos"), "hipotese": (r.get("hipótese preliminar") or "")[:400], "parecer": r.get("parecer do técnico"),
             "documentos": r.get("documentos a pedir"), "link": r["link"]} for r in top[:20]]


def main():
    d = {"atualizado": datetime.now().strftime("%d/%m/%Y %H:%M"), "whatsapp": whatsapp(), "recuperador": recuperador(),
         "revisor": revisor(), "gestao": gestao(), "demandas": demandas(),
         "demandas_lista": demandas_lista(), "conselho": conselho_pendentes(), "catalogo": catalogo(), "lote": lote_completo(),
         "pastas": {"daniela": "Área Partners · Agentes / Central Masters · Daniela", "jenifer": "Área Partners · Agentes / Central BDR · Jenifer",
                    "geovana": "Área Partners · Agentes / Central Técnica · Geovana", "luis": "Área Partners · Agentes / Gestão · Luis"}}
    os.makedirs(os.path.join(AP, "portal"), exist_ok=True)
    json.dump(d, open(os.path.join(AP, "portal/dados.json"), "w"), ensure_ascii=False, indent=1)
    print("portal/dados.json atualizado:", d["atualizado"])


if __name__ == "__main__":
    main()
