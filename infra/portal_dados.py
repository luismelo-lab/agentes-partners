#!/usr/bin/env python3
"""Monta os dados do portal "Central Partners" (v2, 23/10/2026) a partir das saídas dos agentes.

Gera dois arquivos ao lado do portal/index.html:
  dados.json      o que muda todo dia (números, demandas, lote, decisões, arquivos do dia). Formato da v1 mantido;
                  só acrescenta "pastas_web", "arquivos_dia" e "janelas" (janelas de receita).
  diretorio.json  o "Onde está": 25 áreas (missão, dono, especialistas, entregas, pasta com link do OneDrive),
                  pessoas, rotinas, pastas, regras da casa e o contexto curto de cada área para o "Fale com esta área".
                  Sem dado de cliente: só o manual oficial, as skills e as pastas fixas.
Nada de dados bancários, textos de pareceres ou conversas brutas do WhatsApp.
Uso: python3 infra/portal_dados.py → <repositório>/portal/dados.json e diretorio.json (PORTAL_SAIDA muda a pasta)
"""
import glob, json, os, re, sys, time
from datetime import datetime

AP = os.path.expanduser("~/agentes-partners")          # dados dos agentes (fora do git) ficam na pasta principal
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.environ.get("PORTAL_SAIDA") or os.path.join(REPO, "portal")
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


# ---------- Onde está (diretorio.json) ----------
G4 = "04 · Gestão, Metas e Estratégia"
# Pastas fixas do OneDrive: (caminho relativo, rótulo, para que serve, apelidos usados nos textos do manual).
# Só pastas da operação; nenhuma pasta com nome de cliente.
PASTAS = [
    ("Área Partners · Agentes/Central Masters · Daniela", "Central Masters · Daniela", "Pasta da Daniela: plano do dia, pendências dos Masters, pedidos", ["Central Masters · Daniela"]),
    ("Área Partners · Agentes/Central Masters · Daniela/Briefings", "Briefings dos Masters", "Briefings de conta e de reunião", ["Daniela (Briefings)"]),
    ("Área Partners · Agentes/Central BDR · Jenifer", "Central BDR · Jenifer", "Pasta da Jenifer: plano do dia e pedidos", ["Central BDR · Jenifer"]),
    ("Área Partners · Agentes/Central BDR · Jenifer/Listas", "Listas de prospecção", "Listas por Master, segmento e UF", ["Jenifer/Listas"]),
    ("Área Partners · Agentes/Central Técnica · Geovana", "Central Técnica · Geovana", "Pasta da Geovana: plano do dia, lote do Recuperador, Revisor", ["Central Técnica · Geovana"]),
    ("Área Partners · Agentes/Central Técnica · Geovana/Fichas do Recuperador", "Fichas do Recuperador", "Fichas de reanálise do lote semanal", ["Fichas do Recuperador"]),
    ("Área Partners · Agentes/Central Técnica · Geovana/Fichas do Revisor", "Fichas do Revisor", "Segunda opinião dos diagnósticos", ["Fichas do Revisor"]),
    (f"{G4}/Central de Agentes", "Central de Agentes (Luis)", "Pasta do Luis: plano do dia, demandas, folha de decisões", ["04 · Gestão, Metas e Estratégia/Central de Agentes", "04 · Gestão/Central de Agentes", "Central de Agentes"]),
    (f"{G4}/Central de Agentes/Caixa de saída (e-mail pausado)", "Caixa de saída", "O que sairia por e-mail enquanto o Graph está pausado (D91)", ["Caixa de saída"]),
    (f"{G4}/Central de Agentes/Pedidos", "Pedidos à Central", "Arquivos das respostas aos pedidos", ["pasta Pedidos da Central"]),
    (f"{G4}/Central de Agentes/Pedidos aprovados", "Pedidos aprovados", "Respostas aprovadas por quem pediu", ["Pedidos aprovados"]),
    (f"{G4}/Central de Agentes/Radar de mercado", "Radar de mercado", "Resumo semanal do que mudou em normas, julgados e mercado", ["Radar de mercado", "branch radar/"]),
    (f"{G4}/Conselho", "Conselho", "Atas do Conselho Consultivo", ["04 · Gestão, Metas e Estratégia/Conselho", "04 · Gestão/Conselho"]),
    (f"{G4}/Resultado semanal", "Resultado semanal", "Deck e one-pager de resultados", ["Resultado semanal", "relatório semanal de resultados"]),
    (f"{G4}/Planejamento 2027", "Planejamento 2027", "Planejamento e metas de 2027", ["Planejamento 2027"]),
    ("01 · Comercial e Parceiros/Relatórios das áreas", "Relatórios das áreas", "Relatórios das áreas de agentes (repasses, contratos, dados)", ["Relatórios das áreas"]),
    ("01 · Comercial e Parceiros/Relatórios das áreas/Contas e Soluções", "Contas e Soluções", "Mapa da conta e carteira de cross-sell", ["Relatórios das áreas/Contas e Soluções"]),
    ("01 · Comercial e Parceiros/Programa de Parceiros", "Programa de Parceiros", "Política, níveis e jornada do programa", ["01 · Comercial e Parceiros/Programa de Parceiros", "Programa de Parceiros"]),
    ("03 · Produtos e Projetos/Crédito Internacional", "Crédito Internacional", "Produto em validação (G2)", ["Crédito Internacional"]),
    ("03 · Produtos e Projetos/PROJETO MAQUILA - INTERNACIONALIZAÇÃO", "Projeto Maquila", "Produto em validação (G2)", ["PROJETO MAQUILA"]),
    ("06 · Marketing e Apresentações/Diagnósticos", "Diagnósticos", "Apresentações de diagnóstico", ["06 · Marketing e Apresentações/Diagnósticos", "Diagnósticos"]),
    ("06 · Marketing e Apresentações/Marca", "Marca", "Logos, fontes e Design System Save", ["Marca"]),
    ("06 · Marketing e Apresentações", "Marketing e Apresentações", "Campanhas, kits e apresentações", ["06 · Marketing e Apresentações"]),
]
PESSOAS = [
    ("luis", "Luis", "Gestor da Área Partners. Decide regra, preço, meta, remuneração, produto em validação e material em escala (infra/alcadas.md)."),
    ("daniela", "Daniela", "Central Masters: demandas dos 9 Masters, retorno ao parceiro, plano de conta. Aprova os chamados das demandas dela."),
    ("jenifer", "Jenifer", "Central BDR: prospecção e listas para os Masters. Decide as listas."),
    ("geovana", "Geovana", "Central Técnica: decide o lote do Recuperador e as fichas do Revisor; diagnóstico."),
    ("junior", "Junior", "Save Invest: Gestão de Contas, antecipação e FIDC."),
    ("joao", "João Mattos", "Produtos em validação: Crédito Internacional, Maquila, captação, home equity, turnkey."),
    ("paulo", "Paulo", "Tax internacional e comércio exterior, com o João."),
    ("ti", "TI da Save", "Credenciais do Graph e do GLPI, SSO e acessos."),
]


def _od():
    try:
        sys.path.insert(0, os.path.join(REPO, "lib")); import caminhos
        return caminhos, caminhos.onedrive()
    except (SystemExit, Exception):
        return None, None


def pastas_catalogo():
    cm, base = _od(); out = []
    for rel, rot, uso, apel in PASTAS:
        abs_ = os.path.join(base, rel) if base else None
        url = cm.web(abs_) if abs_ and os.path.isdir(abs_) else ""
        out.append({"rotulo": rot, "caminho": rel.replace("/", " / "), "uso": uso, "url": url, "apelidos": apel})
    return out


def links(texto, cat):
    """Pastas do OneDrive citadas num texto do manual (a pasta mais específica vence; sem repetir pasta-mãe)."""
    t = (texto or "").replace("`", "")
    achou = []
    for p in cat:
        for a in sorted(p["apelidos"], key=len, reverse=True):
            if a in t: achou.append((len(p["caminho"]), p)); break
    achou.sort(key=lambda x: -x[0]); out = []
    for _, p in achou:
        if any(o["caminho"].startswith(p["caminho"]) or p["caminho"].startswith(o["caminho"]) for o in out): continue
        out.append(p)
    return [{"rotulo": p["rotulo"], "url": p["url"], "caminho": p["caminho"]} for p in out if p["url"]][:3]


def _curto(t, n=240):
    t = re.sub(r"\s+", " ", str(t or "")).strip()
    return t if len(t) <= n else t[:n - 1].rsplit(" ", 1)[0] + "…"


REGRAS_CASA = [
    "Tudo é pré-análise interna: nada é enviado, assinado ou gravado em sistema sem uma pessoa aprovar.",
    "Nunca prometer valor, prazo ou êxito.",
    "Alíquota zero sai sempre via PER, nunca DCOMP (D14).",
    "Produto em validação (Crédito Internacional, Maquila, captação, home equity, turnkey): sem taxa, prazo, fee ou condição para fora até o G2 (D77, D88).",
    "Venda gerencial e conta escrow: só o Junior trata, presencialmente; não descrever a mecânica (D82).",
    "Não citar cliente pelo nome e não usar nem pedir dados pessoais (CPF, dados bancários, senhas).",
    "HubSpot e GLPI: só leitura e rascunho.",
    "Norma citada leva artigo e data; o que não foi conferido fica marcado [não confirmado].",
]


def _secao(txt, titulo):
    m = re.search(rf"^## [^\n]*{titulo}[^\n]*\n(.+?)(?=^## |\Z)", txt, re.S | re.M | re.I)
    return m.group(1).strip() if m else ""


def _limpo(t):
    t = re.sub(r"[*`>#|]", "", t); t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", t)).strip()


def contexto_chat(a):
    """Contexto curto (até ~2.500 caracteres) para o "Fale com esta área": skill, regras e especialistas. Sem dado de cliente."""
    base = os.path.join(REPO, "skills", a["skill"])
    try: sk = open(os.path.join(base, "SKILL.md"), encoding="utf-8").read()
    except OSError: sk = ""
    rp = os.path.join(base, "references/regras-e-proibidos.md")
    regras = _limpo(_secao(open(rp, encoding="utf-8").read(), "Regras") if os.path.exists(rp) else _secao(sk, "Regras inegoci"))
    partes = [f"Área: {a['nome']} (bloco {a['bloco']}). Missão: {a['missao']} Dono humano: {a['dono']}. Onde entrega: {a['onde']}.",
              ("Regras da área: " + _curto(regras, 750)) if regras else "",
              ("Não faz: " + _curto(" ".join(a["nao_faz"]), 400)) if a.get("nao_faz") else "",
              "Especialistas: " + " | ".join(f"{e['nome']}: {_curto(e['entrega'], 110)}" for e in a["especialistas"]),
              "Entregas: " + "; ".join(e["entrega"] for e in a["entregas"])]
    t = "\n".join(x for x in partes if x)
    return t if len(t) <= 2500 else t[:2499].rsplit(" ", 1)[0] + "…"


def janelas():
    f = os.path.join(REPO, "docs/lancamento-2026/janelas.json")
    if not os.path.exists(f): return []
    return [{"id": j["id"], "janela": j["janela"], "prazo": j.get("prazo"), "prazo_texto": j.get("prazo_texto") or "depende de ato sem data",
             "produto": (j.get("produto_tese") or "").split(";")[0]} for j in json.load(open(f, encoding="utf-8")).get("janelas", [])]


def diretorio():
    sys.path.insert(0, os.path.join(REPO, "infra")); import manual_oficial as M
    E = M.entregas(); cat = pastas_catalogo(); areas = []
    for skill, (nome, bloco, missao, dono, onde) in M.AREAS.items():
        e = E.get(skill) or {}
        ents = [{"entrega": x.get("entrega"), "conteudo": _curto(x.get("conteudo")), "formato": x.get("formato"), "arquivo": x.get("arquivo"),
                 "quando": x.get("quando"), "quem_recebe": x.get("quem_recebe"), "onde": x.get("onde"), "links": links(x.get("onde"), cat)}
                for x in e.get("entregas", [])]
        areas.append({"skill": skill, "nome": nome, "bloco": bloco, "missao": missao, "dono": dono, "onde": onde.replace("`", ""),
                      "links": links(onde, cat),
                      "quem_usa": e.get("quem_usa"), "nao_faz": e.get("nao_faz") or [],
                      "especialistas": [{"nome": n, "entrega": ent} for n, ent, _ in M.especialistas(skill)], "entregas": ents})
    cm, base = _od(); pessoas = []
    for k, nome, papel in PESSOAS:
        p = {"chave": k, "nome": nome, "papel": papel, "pasta": "", "url": "", "plano_url": "",
             "areas": [a["skill"] for a in areas if nome.split()[0] in a["dono"]]}
        if cm and k in ("luis", "daniela", "jenifer", "geovana"):
            d = cm.pasta(k); p["pasta"] = os.path.relpath(d, base).replace("/", " / ")
            if os.path.isdir(d): p["url"] = cm.web(d)
            pl = os.path.join(d, "Plano do dia"); p["plano_url"] = cm.web(pl) if os.path.isdir(pl) else p["url"]
        pessoas.append(p)
    rotinas = [{"nome": n, "quando": q, "entrega": e, "onde": o.replace("`", ""), "links": links(o, cat)} for n, q, e, o in M.ROTINAS]
    for a in areas: a["contexto_chat"] = contexto_chat(a)
    return {"atualizado": datetime.now().strftime("%d/%m/%Y %H:%M"), "blocos": M.ORDEM_BLOCOS, "areas": areas, "pessoas": pessoas, "regras_casa": REGRAS_CASA,
            "rotinas": rotinas, "pastas": [{k: v for k, v in p.items() if k != "apelidos"} for p in cat]}


def arquivos_dia():
    """Arquivos que os agentes gravaram nas últimas 24 horas na pasta de cada pessoa (só o nome e o link da pasta)."""
    cm, base = _od(); out = {}
    if not cm: return out
    limite = time.time() - 86400
    for k in ("luis", "daniela", "jenifer", "geovana"):
        d = cm.pasta(k); xs = []
        for raiz, dirs, fs in os.walk(d):
            if raiz[len(d):].count(os.sep) >= 2: dirs[:] = []
            dirs[:] = [x for x in dirs if not x.startswith(".")]
            for f in fs:
                if f.startswith((".", "~$")): continue
                c = os.path.join(raiz, f)
                try: m = os.path.getmtime(c)
                except OSError: continue
                if m >= limite: xs.append((m, f, raiz))
        xs.sort(reverse=True)
        out[k] = [{"nome": f, "pasta": "" if r == d else os.path.relpath(r, d), "url": cm.web(r),
                   "hora": datetime.fromtimestamp(m).strftime("%H:%M")} for m, f, r in xs[:8]]
    return out


def main():
    d = {"atualizado": datetime.now().strftime("%d/%m/%Y %H:%M"), "whatsapp": whatsapp(), "recuperador": recuperador(),
         "revisor": revisor(), "gestao": gestao(), "demandas": demandas(),
         "demandas_lista": demandas_lista(), "conselho": conselho_pendentes(), "catalogo": catalogo(), "lote": lote_completo(),
         "pastas": {"daniela": "Área Partners · Agentes / Central Masters · Daniela", "jenifer": "Área Partners · Agentes / Central BDR · Jenifer",
                    "geovana": "Área Partners · Agentes / Central Técnica · Geovana", "luis": "04 · Gestão, Metas e Estratégia / Central de Agentes"}}
    D = diretorio()
    d["pastas_web"] = {p["chave"]: {"url": p["url"], "plano_url": p["plano_url"]} for p in D["pessoas"] if p["url"]}
    d["arquivos_dia"] = arquivos_dia()
    d["janelas"] = janelas()
    os.makedirs(SAIDA, exist_ok=True)
    json.dump(d, open(os.path.join(SAIDA, "dados.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(D, open(os.path.join(SAIDA, "diretorio.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{SAIDA}/dados.json e diretorio.json atualizados:", d["atualizado"],
          f"· {len(D['areas'])} áreas, {sum(len(a['especialistas']) for a in D['areas'])} especialistas, {sum(len(a['entregas']) for a in D['areas'])} entregas")


if __name__ == "__main__":
    main()
