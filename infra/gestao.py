#!/usr/bin/env python3
"""Sistema de gestão · consolida os dados de decisão do Luis (resultado, previsibilidade e controle) em um só JSON.

Contrato: infra/gestao-schema.md (seção 4 define a saída). Entradas, todas em ~/agentes-partners (fora do git):
  registro/gestao/pacote-<data>.json     resultado e controle (Controller com Dados)        → "meta", "semaforo", "confiabilidade", "alertas"
  registro/gestao/previsao-<data>.json   previsibilidade (Resultados, Pós-venda, Tributário) → "previsao"
  registro/gestao/controle-<data>.json   regras, desvios e ritual (Gabinete)                → "desvios", "regras", "ritual"
  conselho/decisoes.md                   decisões "pendente" da alçada do Luis              → "decisoes"
  registro/gestao/acoes.jsonl            ações combinadas (uma por linha; opcional)         → "acoes"
  registro/gestao/pre-analise-<data>.json pré-análise das áreas por métrica (Resultados)   → "semaforo[i].pre_analise", "decisoes_sugeridas"
  registro/gestao/dossies/<id>.json      dossiê de cada decisão (validação das áreas)       → "decisoes[i].dossie" (indice.json é ignorado aqui)
  logs/painel-luis/acoes/*.json e logs/painel/acoes/*.json   o que as donas marcaram no painel (só a dona ou o Luis, por conta)
  logs/painel-luis/conselho/meta-q4-unidade.json             unidade da meta escolhida pelo Luis no painel ("credito" ou "liquido")
Cada arquivo ausente vira bloco vazio com um aviso em "avisos"; nada derruba a consolidação.
Saída: registro/gestao/gestao.json (ou --saida <arquivo>; --json imprime na tela). infra/portal_dados.py copia para portal/dados.json em "gestao".
Uso: python3 infra/gestao.py [--saida arquivo] [--json]
"""
import glob, json, os, re, sys
from datetime import date

AP = os.environ.get("PARTNERS_AP") or os.path.expanduser("~/agentes-partners")
BLOCOS = ("resultado", "caixa", "canal", "risco", "operacao")
STATUS = ("verde", "amarelo", "vermelho", "cinza")
PESSOAS = ("luis", "daniela", "jenifer", "geovana")


def _ultimo(pasta, padrao):
    xs = sorted(glob.glob(os.path.join(pasta, padrao)))
    return xs[-1] if xs else None


def _ler(caminho, avisos, nome):
    """JSON do arquivo mais recente; sem arquivo ou quebrado, {} e um aviso."""
    if not caminho:
        avisos.append(f"{nome}: nenhum arquivo em registro/gestao/; bloco vazio."); return {}
    try:
        d = json.load(open(caminho, encoding="utf-8"))
        if not isinstance(d, dict): raise ValueError("não é um objeto")
        return d
    except (OSError, ValueError) as e:
        avisos.append(f"{nome}: não consegui ler {os.path.basename(caminho)} ({str(e)[:80]}); bloco vazio."); return {}


def _int(v, padrao=0):
    try: return int(round(float(v)))
    except (TypeError, ValueError): return padrao


def _num(v):
    try: return float(v)
    except (TypeError, ValueError): return None


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s or "").lower()).strip("-")[:60] or "x"


# ---------- decisões do Conselho ----------
def decisoes_pendentes(caminho=None):
    """Linhas "pendente" de conselho/decisoes.md que são alçada do Luis (D98): as delegadas ou aplicadas por padrão já não estão
    "pendente"; uma linha pendente cuja observação diga que foi delegada ("delegad", "Dono:") fica de fora. D7 sai quando há D7-b."""
    caminho = caminho or os.path.join(AP, "conselho", "decisoes.md")
    try: linhas = open(caminho, encoding="utf-8").read().splitlines()
    except OSError: return None
    out = []
    for l in linhas:
        c = [x.strip() for x in l.split("|")]
        if len(c) > 6 and re.match(r"D\d", c[1]) and c[5] == "pendente":
            obs = c[6]
            if re.search(r"delegad|^Dono:", obs, re.I) and "Fica com o Luis" not in obs: continue
            out.append({"id": c[1], "texto": c[4].replace("**", ""), "dono": "luis", "prazo": "", "status": "pendente", "data": c[2], "ata": c[3], "obs": obs})
    ids = {d["id"] for d in out}
    out = [d for d in out if not (d["id"] == "D7" and "D7-b" in ids)]
    vistos, uniq = set(), []
    for d in out:
        if d["id"] not in vistos: vistos.add(d["id"]); uniq.append(d)
    return uniq


# ---------- painel (gravações das pessoas, por conta) ----------
def _conferir(por, por_id, dono):
    """Autor do registro do painel: conta conhecida (infra/portal-contas.json) e a própria pessoa; dona da ação ou o Luis."""
    try:
        sys.path.insert(0, os.path.join(AP, "lib")); import portal_contas as PC
        ok, _ = PC.conferir(por, por_id)
    except Exception:
        return False
    return bool(ok) and (por == "luis" or (dono and por == dono))


def acoes_painel(desvios, avisos):
    """Aplica o status marcado no painel (acoes/<id> = {status, por, por_id, quando}) a cada desvio ou ação; só a dona ou o Luis."""
    docs = {}
    for pasta in ("logs/painel-luis/acoes", "logs/painel/acoes"):
        for f in sorted(glob.glob(os.path.join(AP, pasta, "*.json"))):
            try: d = json.load(open(f, encoding="utf-8"))
            except (OSError, ValueError): continue
            d = d["data"] if isinstance(d, dict) and isinstance(d.get("data"), dict) else d
            if isinstance(d, dict) and d.get("status") in ("aberto", "em_andamento", "resolvido"):
                i = os.path.basename(f)[:-5]
                if i not in docs or str(d.get("quando") or "") > str(docs[i].get("quando") or ""): docs[i] = d
    n = 0
    for x in desvios:
        d = docs.get(x.get("id"))
        if not d: continue
        if _conferir(d.get("por"), d.get("por_id"), x.get("dono")):
            x["status"] = d["status"]; x["marcado_por"] = d.get("por"); x["marcado_em"] = d.get("quando"); n += 1
        else:
            avisos.append(f"ação {x.get('id')}: marcação no painel descartada (conta ou dona não confere).")
    return n


def unidade_painel():
    """Unidade da meta escolhida pelo Luis no painel ("Definir unidade" grava conselho/meta-q4-unidade)."""
    f = os.path.join(AP, "logs", "painel-luis", "conselho", "meta-q4-unidade.json")
    try: d = json.load(open(f, encoding="utf-8"))
    except (OSError, ValueError): return None
    d = d["data"] if isinstance(d, dict) and isinstance(d.get("data"), dict) else d
    if not isinstance(d, dict) or not _conferir(d.get("por"), d.get("por_id"), "luis"): return None
    u = str(d.get("decisao") or "").lower()
    return "credito" if "cred" in u else "liquido" if "liq" in u else None


# ---------- montagem ----------
def _metrica(m):
    st = m.get("status") if m.get("status") in STATUS else "cinza"
    meta = _num(m.get("meta")); tol = m.get("tolerancia") if isinstance(m.get("tolerancia"), dict) else {}
    if _num(m.get("valor")) is None: st = "cinza"  # sem dado, cinza. Sem meta aprovada o Controller pode avaliar pela tolerância "proposta": o status vem dele e a meta fica null
    # tolerância: textos para mostrar; "_verde"/"_amarelo" são os limites numéricos calculados; "origem" diz se é proposta
    return {"id": str(m.get("id") or _slug(m.get("nome"))), "nome": str(m.get("nome") or m.get("id") or "—"),
            "bloco": m.get("bloco") if m.get("bloco") in BLOCOS else "operacao", "valor": _num(m.get("valor")), "unidade": str(m.get("unidade") or "n"),
            "anterior": _num(m.get("anterior")), "variacao_pct": _num(m.get("variacao_pct")), "meta": meta, "meta_unidade": str(m.get("meta_unidade") or ""),
            "meta_proposta": bool(m.get("meta_proposta")) or meta is None or str(tol.get("origem") or "") == "proposta",
            "limite_proposto": _num(tol.get("_verde")), "tolerancia": {k: str(v) for k, v in tol.items() if not k.startswith("_") and k != "origem" and v}, "status": st,
            "fonte": str(m.get("fonte") or ""), "confianca": m.get("confianca") if m.get("confianca") in ("alta", "media", "baixa") else "baixa", "nota": str(m.get("nota") or "")}


def _meta(p, unidade_luis):
    m = p.get("meta") if isinstance(p.get("meta"), dict) else {}
    u = m.get("unidade")  # D111: "credito_contrato_fechado" vale sobre a escolha antiga do painel
    u = "credito" if str(u).startswith("credito") else (unidade_luis or u)
    return {"q4_rs": _int(m.get("q4_rs")), "unidade": u if u in ("credito", "liquido") else "indefinida", "unidade_detalhe": str(m.get("unidade") or ""), "decisao": str(m.get("decisao") or ""),
            "mes_atual": m.get("mes_atual") if isinstance(m.get("mes_atual"), dict) else {}, "meses": [x for x in m.get("meses", []) if isinstance(x, dict)],
            "total": m.get("total") if isinstance(m.get("total"), dict) else {}, "por_master": m.get("por_master") if isinstance(m.get("por_master"), dict) else {},
            "realizado_rs": _int(m.get("realizado_rs")),
            "falta_rs": _int(m.get("falta_rs")), "dias_uteis_restantes": _int(m.get("dias_uteis_restantes")), "ritmo_necessario_rs_dia": _int(m.get("ritmo_necessario_rs_dia")),
            "ritmo_atual_rs_dia": _int(m.get("ritmo_atual_rs_dia")), "leituras": m.get("leituras") if isinstance(m.get("leituras"), dict) else {},
            "unidade_definida_no_painel": bool(unidade_luis) and not str(m.get("unidade") or "").startswith("credito"), "periodo": p.get("periodo") if isinstance(p.get("periodo"), dict) else {}}


# ---------- pré-análise das áreas e dossiês das decisões (26/10/2026) ----------
def _txt(v, n=1200):
    return str(v if v is not None else "").strip()[:n]


def _textos(xs, n=600):
    """Lista de textos; aceita itens em dicionário ({"fato": …} ou {"texto": …})."""
    out = []
    for x in xs if isinstance(xs, list) else []:
        if isinstance(x, dict): x = x.get("fato") or x.get("texto") or x.get("hipotese") or ""
        if str(x or "").strip(): out.append(_txt(x, n))
    return out


def _pre(i):
    """Pré-análise de uma métrica (skills/depto-resultados/scripts/pre_analise.py) no formato da tela; None se não for objeto."""
    if not isinstance(i, dict): return None
    c = i.get("causa") if isinstance(i.get("causa"), dict) else {}
    return {"leitura": _txt(i.get("leitura")), "causa": {"fatos": _textos(c.get("fatos")), "hipoteses": _textos(c.get("hipoteses"))},
            "acoes": [{"acao": _txt(a.get("acao"), 500), "dono": _txt(a.get("dono"), 60), "prazo": _txt(a.get("prazo"), 20)} for a in i.get("acoes") or [] if isinstance(a, dict) and a.get("acao")],
            "decisao_sugerida": _txt(i.get("decisao_sugerida")) or None, "efeito": _txt(i.get("efeito"), 1500),
            "confianca": i.get("confianca") if i.get("confianca") in ("alta", "media", "baixa") else "baixa", "melhorar_confianca": _txt(i.get("melhorar_confianca"), 800),
            "area": _txt(i.get("area"), 80), "especialista": _txt(i.get("especialista"), 120), "pendente": bool(i.get("pendente"))}


PARECERES = ("concorda", "concorda com ressalva", "discorda")


def _dossie(d):
    """Dossiê de uma decisão (registro/gestao/dossies/<id>.json) só com os campos do contrato; None se não for objeto."""
    if not isinstance(d, dict): return None
    ls = lambda k: [x for x in d.get(k) or [] if isinstance(x, dict)] if isinstance(d.get(k), list) else []
    ex = d.get("execucao") if isinstance(d.get("execucao"), dict) else {}
    par = lambda p: next((x for x in PARECERES[::-1] if str(p or "").lower().startswith(x)), "concorda com ressalva" if "ressalva" in str(p or "").lower() else "")
    rv = d.get("revisao") if isinstance(d.get("revisao"), dict) else {}
    return {"id": _txt(d.get("id"), 40), "titulo": _txt(d.get("titulo"), 300), "prazo": _txt(d.get("prazo"), 20), "urgencia": _int(d.get("urgencia"), 3),
            "revisao": {"gerente": _txt(rv.get("gerente"), 80), "aprovado": rv.get("aprovado") is True, "rodadas": _int(rv.get("rodadas"), 0)} if rv else None, "o_que_decidir": _txt(d.get("o_que_decidir")), "por_que_agora": _txt(d.get("por_que_agora")),
            "custo_nao_decidir": _txt(d.get("custo_nao_decidir")),
            "contexto": [{"fato": _txt(x.get("fato"), 600), "fonte": _txt(x.get("fonte"), 300), "tipo": x.get("tipo") if x.get("tipo") in ("fato", "estimativa", "opiniao") else "fato"} for x in ls("contexto") if x.get("fato")],
            "opcoes": [{k: _txt(x.get(k), 800) for k in ("nome", "pros", "contras", "risco", "efeito")} for x in ls("opcoes") if x.get("nome")],
            "recomendacao": _txt(d.get("recomendacao"), 1500), "se_reprovada": _txt(d.get("se_reprovada")),
            "validacoes": [{"area": _txt(x.get("area"), 80), "especialista": _txt(x.get("especialista"), 160), "parecer": par(x.get("parecer")), "motivo": _txt(x.get("motivo"), 1200),
                            "base": _txt(x.get("base"), 600), "condicao": _txt(x.get("condicao"), 800), "ressalva": _txt(x.get("ressalva"), 1200)} for x in ls("validacoes") if x.get("area") or x.get("parecer")],
            "divergencias": _textos(d.get("divergencias"), 800) if isinstance(d.get("divergencias"), list) else ([_txt(d.get("divergencias"), 1200)] if str(d.get("divergencias") or "").strip() else []),
            "execucao": {"dono": _txt(ex.get("dono"), 80), "prazo": _txt(ex.get("prazo"), 40), "indicador": _txt(ex.get("indicador"), 400)},
            "atualizado_em": _txt(d.get("atualizado_em"), 30)}


def _ler_dossies(pasta, avisos):
    """{id: dossiê} de registro/gestao/dossies/*.json (fora o indice.json); arquivo quebrado vira aviso, pasta ausente vira {}."""
    out = {}
    for f in sorted(glob.glob(os.path.join(pasta, "*.json"))):
        if os.path.basename(f) == "indice.json": continue
        try: d = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError): avisos.append(f"dossiê {os.path.basename(f)}: não consegui ler; decisão sem dossiê."); continue
        x = _dossie(d)
        if x: out[x["id"] or os.path.basename(f)[:-5]] = x
    return out


def _desvios(c):
    regras = {r.get("id"): r for r in c.get("regras", []) if isinstance(r, dict)}
    out = []
    for d in c.get("desvios", []):
        if not isinstance(d, dict): continue
        r = regras.get(d.get("regra"), {})
        out.append({"id": _slug(f"{d.get('regra')}-{d.get('metrica')}-{d.get('desde')}"), "regra": str(d.get("regra") or ""), "condicao": str(r.get("condicao") or ""),
                    "metrica": str(d.get("metrica") or r.get("metrica") or ""), "valor": _num(d.get("valor")), "limite": _num(d.get("limite")), "desde": str(d.get("desde") or ""),
                    "acao": str(d.get("acao") or r.get("acao") or ""), "dono": str(d.get("dono") or r.get("dono") or ""), "prazo": str(d.get("prazo") or ""),
                    "alcada": str(r.get("alcada") or d.get("alcada") or ""), "status": d.get("status") if d.get("status") in ("aberto", "em_andamento", "resolvido") else "aberto", "origem": "controle",
                    "texto": str(d.get("texto") or ""), "vencido": bool(d.get("vencido")), "escalado_para": str(d.get("escalado_para") or ""), "bloco": str(d.get("bloco") or "")})
    return out


def _acoes(caminho, avisos):
    out = []
    if not os.path.exists(caminho): return out
    try:
        for n, l in enumerate(open(caminho, encoding="utf-8"), 1):
            l = l.strip()
            if not l: continue
            try: a = json.loads(l)
            except ValueError: avisos.append(f"acoes.jsonl: linha {n} inválida, ignorada."); continue
            if not isinstance(a, dict) or not a.get("acao"): continue
            out.append({"id": str(a.get("id") or _slug(f"{a.get('origem') or 'acao'}-{a.get('acao')}-{a.get('prazo')}")), "acao": str(a["acao"]), "dono": str(a.get("dono") or ""),
                        "prazo": str(a.get("prazo") or ""), "origem": a.get("origem") if a.get("origem") in ("conselho", "controle") else "conselho",
                        "status": a.get("status") if a.get("status") in ("aberto", "em_andamento", "resolvido") else "aberto", "metrica": str(a.get("metrica") or "")})
    except OSError as e:
        avisos.append(f"acoes.jsonl: não consegui ler ({str(e)[:60]}).")
    return out


def montar(pacote, previsao, controle, decisoes, acoes, avisos=None, unidade_luis=None, hoje=None, pre_analise=None, dossies=None):
    """Monta o gestao.json (seção 4 do contrato) a partir dos dicionários já lidos. Puro: não lê disco.
    pre_analise: o pre-analise-<data>.json (itens por metrica_id e decisoes_luis); dossies: {id da decisão: dossiê}. Os dois são opcionais."""
    avisos = list(avisos or []); pa = pre_analise if isinstance(pre_analise, dict) else {}; dos = dossies if isinstance(dossies, dict) else {}
    pre = {str(i.get("metrica_id")): _pre(i) for i in pa.get("itens") or [] if isinstance(i, dict) and i.get("metrica_id")}
    p, v, c = pacote or {}, previsao or {}, controle or {}
    if decisoes is None: avisos.append("conselho/decisoes.md: não encontrado; sem decisões."); decisoes = []
    sem = [m for m in p.get("metricas", []) if isinstance(m, dict)]
    pv = {"data": v.get("data"), "horizonte_semanas": _int(v.get("horizonte_semanas"), 13),
          "cenarios": {k: x for k, x in (v.get("cenarios") or {}).items() if isinstance(x, dict)},
          "caixa_13_semanas": [x for x in v.get("caixa_13_semanas", []) if isinstance(x, dict)], "pipeline_por_safra": [x for x in v.get("pipeline_por_safra", []) if isinstance(x, dict)],
          "decadencia_mensal": [x for x in v.get("decadencia_mensal", []) if isinstance(x, dict)], "janelas": [x for x in v.get("janelas", []) if isinstance(x, dict)],
          "riscos": [x for x in v.get("riscos", []) if isinstance(x, dict)], "por_mes": v.get("por_mes") if isinstance(v.get("por_mes"), dict) else {}}
    return {"data": p.get("data") or v.get("data") or c.get("data") or (hoje or date.today().isoformat()), "gerado_em": hoje or date.today().isoformat(),
            "fontes": {"pacote": p.get("data"), "previsao": v.get("data"), "controle": c.get("data")},
            "meta": _meta(p, unidade_luis), "semaforo": [{**x, "pre_analise": pre.get(x["id"])} for x in (_metrica(m) for m in sem)],
            "pre_analise": {"data": pa.get("data"), "itens": len(pre), "resumo": pa.get("resumo") if isinstance(pa.get("resumo"), dict) else {}} if pa else {},
            "decisoes_sugeridas": [{"chave": _txt(x.get("chave"), 120), "decisao": _txt(x.get("decisao")), "efeito": _txt(x.get("efeito"), 1200), "area": _txt(x.get("area"), 80),
                                    "status": x.get("status") if x.get("status") in STATUS else "cinza", "metricas": [str(m) for m in x.get("metricas") or [] if m][:10],
                                    "dossie": dos.get(_txt(x.get("chave"), 120))} for x in pa.get("decisoes_luis") or [] if isinstance(x, dict) and x.get("decisao")],
            "confiabilidade": p.get("confiabilidade") if isinstance(p.get("confiabilidade"), dict) else {},
            "alertas": [a for a in p.get("alertas", []) if isinstance(a, dict)],
            "previsao": pv, "desvios": _desvios(c), "regras": [r for r in c.get("regras", []) if isinstance(r, dict)], "ritual": [r for r in c.get("ritual", []) if isinstance(r, dict)],
            "decisoes": [{"id": d["id"], "texto": d["texto"], "dono": "luis", "prazo": d.get("prazo") or "", "status": "pendente", "data": d.get("data") or "", "ata": d.get("ata") or "", "obs": d.get("obs") or "", "dossie": dos.get(d["id"])} for d in decisoes],
            "acoes": acoes or [], "avisos": avisos,
            # dossiês de decisões que estão no livro do Conselho mas fora da alçada listada acima (a tela Decisões também abre o dossiê delas)
            "dossies": {k: x for k, x in dos.items() if k not in {d["id"] for d in decisoes}}}


def consolidar(ap=None):
    """Lê os arquivos (tolerante a ausência) e devolve o consolidado."""
    ap = ap or AP; pasta = os.path.join(ap, "registro", "gestao"); avisos = []
    p = _ler(_ultimo(pasta, "pacote-*.json"), avisos, "pacote")
    v = _ler(_ultimo(pasta, "previsao-*.json"), avisos, "previsão")
    c = _ler(_ultimo(pasta, "controle-*.json"), avisos, "controle")
    dec = decisoes_pendentes(os.path.join(ap, "conselho", "decisoes.md"))
    ac = _acoes(os.path.join(pasta, "acoes.jsonl"), avisos)
    fpa = _ultimo(pasta, "pre-analise-*.json")
    pa = _ler(fpa, avisos, "pré-análise") if fpa else (avisos.append("pré-análise: nenhum arquivo em registro/gestao/; faróis sem pré-análise.") or {})
    dos = _ler_dossies(os.path.join(pasta, "dossies"), avisos)
    g = montar(p, v, c, dec, ac, avisos, unidade_luis=unidade_painel() if ap == AP else None, pre_analise=pa, dossies=dos)
    if ap == AP: acoes_painel(g["desvios"] + g["acoes"], g["avisos"])
    return g


def main():
    args = sys.argv[1:]
    saida = args[args.index("--saida") + 1] if "--saida" in args else os.path.join(AP, "registro", "gestao", "gestao.json")
    g = consolidar()
    if "--json" in args: print(json.dumps(g, ensure_ascii=False, indent=1)); return
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    json.dump(g, open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{saida}: {len(g['semaforo'])} métricas, {len(g['desvios'])} desvios, {len(g['decisoes'])} decisões ({sum(1 for d in g['decisoes'] if d.get('dossie'))} com dossiê), {len(g['acoes'])} ações, "
          f"{sum(1 for m in g['semaforo'] if m.get('pre_analise'))} faróis com pré-análise"
          + (f" · avisos: {' '.join(g['avisos'])}" if g["avisos"] else ""))


if __name__ == "__main__":
    main()
