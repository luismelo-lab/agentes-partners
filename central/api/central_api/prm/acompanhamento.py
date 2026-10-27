"""Acompanhamento de negócios e dashboards de vendas (PRM-R113 a PRM-R118; instrução do Luis de 26/10/2026).

Parceiro: lista dos negócios do escopo (titular vê o escritório; consultor só os dele) com filtros, busca, ordenação e
quadro por estado; ficha completa com tudo o que o card do HubSpot traz (03 §2.2), filtrado pela matriz de visibilidade
`negocio.visibilidade_campos`; painel de vendas só com os números do próprio escritório (nunca ranking, R27).
Save: dashboard comercial do canal (pipeline por Master e consultor, funil, win rate, ciclo, aging, forecast contra a
meta D111, concentração, dormentes, conversão registrado × não registrado, produtos e teses), com drill-down para a lista.

PRM-R113 o parceiro vê os valores do card (decisão do Luis de 26/10/2026, supera a PRM-R44 e a DL-09 nesta tela), sempre
         com a ressalva da matriz; nunca probabilidade, chance de êxito nem prazo de restituição.
PRM-R114 campo marcado `travado` (notas internas, motivo interno da perda, conflito, outro parceiro, probabilidade e forecast
         do CRM, comissões internas, dado pessoal de sócio) nunca vai ao parceiro, mesmo que a matriz diga sim.
PRM-R115 texto livre do CRM (próximo passo) só sai ao parceiro depois do auditor de promessas e do bloqueio de dado pessoal.
PRM-R116 agregados calculados no back-end; o parceiro só recebe os do próprio escopo.
PRM-R117 o dashboard da Save exclui café e negócio sem Master (R112) e só aparece aos perfis da Save.
PRM-R118 taxa com base pequena (n < painel.base_pequena) sai como "base pequena", sem número.
"""
import json, os, statistics
from collections import Counter, defaultdict
from datetime import date, timedelta

from . import calendario as CAL
from . import demandas as DM
from . import extrato as EX
from . import negocios as NG
from . import registro as RG
from .auditoria import auditar_saida, dados_pessoais
from .erros import Invalido, NaoEncontrado
from .identidade import exigir, ve, ve_negocio

TRAVADOS = frozenset({"notas_internas", "motivo_perda_interno", "conflito_motivo", "outro_parceiro", "probabilidade", "forecast", "outras_comissoes",
                      "contato_socio"})
ABERTOS = ("recebido", "em_diagnostico", "precisa_de_voce", "apresentacao", "contrato")
FUNIL = [("recebido", "Recebido"), ("em_diagnostico", "Em diagnóstico"), ("apresentacao", "Apresentação"), ("contrato", "Contrato"), ("ganho", "Contrato assinado")]
NIVEL = {"recebido": 0, "em_diagnostico": 1, "precisa_de_voce": 1, "apresentacao": 2, "contrato": 3}
FAIXAS_AGING = [(0, 15, "até 15 dias"), (16, 30, "16 a 30 dias"), (31, 60, "31 a 60 dias"), (61, None, "mais de 60 dias")]
SITUACOES = ("andamento", "ganhos", "perdidos", "todos")
ORDENS = ("recente", "antigo", "valor", "parado", "nome", "previsao")


# ---------------------------------------------------------------- utilitários
def _dia(x):
    try:
        return CAL.dia(x) if x else None
    except (ValueError, TypeError):
        return None


def _num(v):
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _hoje(app):
    return CAL.dia(app.agora())


def teses(n):
    t = n.get("teses")
    if isinstance(t, str):
        t = [x.strip() for x in t.split(";")]
    return [x for x in (t or []) if x]


def produto(app, n):
    return n.get("produto") or app.param("negocio.produto_por_pipeline").get(n.get("pipeline") or "") or "Outro produto"


def escritorio(n):
    return n.get("master_id") or n.get("parceiro_id")


def situacao(n):
    return {"ganho": "ganhos", "perdido": "perdidos"}.get(n.get("status"), "andamento")


def dias_na_etapa(app, n):
    if n.get("status") not in (None, "aberto"):
        return None
    d = _dia(n.get("entrou_etapa_em")) or _dia(n.get("criado_em"))
    return (_hoje(app) - d).days if d else None


def nivel_maximo(app, n):
    """Até onde o negócio chegou no funil (0–4). Ganho = 4. Usa o histórico de etapas e o estado atual."""
    if n.get("status") == "ganho":
        return 4
    mapa = app.param("negocio.mapa_etapas")
    nv = [NIVEL.get(mapa.get(x.get("etapa")), 0) for x in n.get("historico_etapas") or []]
    if n.get("status") == "aberto":
        nv.append(NIVEL.get(NG.estado(app, n)[0], 0))
    return max(nv or [0])


def _par(app):
    return {p["parceiro_id"]: p for p in app.repo.listar("parceiro")}


def _nome_par(par, pid):
    return (par.get(pid) or {}).get("nome_exibicao") if pid else None


def _pct_termo(app, esc):
    t = next(iter(app.repo.listar("termo", parceiro_id=esc)), None)
    return _num((t or {}).get("percentual_recuperacao"))


def remuneracao_prevista(app, n, pct=None):
    """Valor previsto ao escritório: crédito estimado × honorário do contrato × percentual do termo. Só ganho; None se faltar dado."""
    if n.get("status") != "ganho":
        return None
    v, h = _num(n.get("valor_credito")), _num(n.get("honorario_pct"))
    p = pct if pct is not None else _pct_termo(app, escritorio(n))
    if v is None or h is None or p is None:
        return None
    return round(v * h * p, 2)


# ---------------------------------------------------------------- matriz de visibilidade (PRM-R113/R114)
def matriz(app):
    return app.param("negocio.visibilidade_campos")


def visivel(app, ator, campo):
    """Campo vai ao ator? Save vê tudo, menos comissões internas fora de luis/financeiro (R111). Parceiro: matriz, com
    trava em código para os campos sensíveis e falha fechada para campo fora da matriz."""
    if ator.tipo in ("save", "agente"):
        return campo != "outras_comissoes" or ator.papel in ("luis", "financeiro")
    if campo in TRAVADOS:
        return False
    m = matriz(app).get(campo)
    if not m or not m.get("parceiro"):
        return False
    return not m.get("so_titular") or ator.papel == "titular"


def _meta(app, campo):
    m = matriz(app).get(campo) or {}
    return m.get("rotulo") or campo, m.get("ressalva")


def ressalvas(app, ator):
    out = {}
    for c in ("valor_credito", "remuneracao_prevista", "previsao_fechamento_em"):
        if visivel(app, ator, c):
            out[c] = _meta(app, c)[1]
    return out


def _texto_seguro(texto):
    """PRM-R115: texto livre do CRM só sai sem dado pessoal e sem promessa."""
    if not texto:
        return None
    t = " ".join(str(texto).split())[:240]
    if dados_pessoais(t):
        return None
    ok, _ = auditar_saida(t)
    return t if ok else None


# ---------------------------------------------------------------- escopo
def _registros_por_deal(app, ator=None):
    out = {}
    for r in app.repo.listar("registro"):
        if r.get("deal_id") and (ator is None or ve(ator, r)):
            out.setdefault(r["deal_id"], r)
    return out


def negocios_do_ator(app, ator, consultor=None):
    """Parceiro: os do escopo (ve_negocio) e ligados com segurança a um parceiro (PRM-R45). Titular pode filtrar por consultor
    (U-… do escritório ou P-… do cadastro). Save: todos com parceiro."""
    xs = [n for n in app.repo.listar("negocio") if escritorio(n)]
    if ator.tipo == "parceiro":
        xs = [n for n in xs if ve_negocio(ator, n)]
        if consultor and ator.papel == "titular":
            cpid = consultor
            if str(consultor).startswith("U-"):
                u = app.repo.obter("usuario_parceiro", consultor) or {}
                cpid = u.get("consultor_parceiro_id") if u.get("parceiro_id") == ator.parceiro_id else "__nenhum__"
            xs = [n for n in xs if n.get("parceiro_id") == cpid and n.get("master_id")]
    return xs


# ---------------------------------------------------------------- item da lista
def item(app, ator, n, par, regs, pcts=None):
    e, _ = NG.estado(app, n)
    reg = regs.get(n["deal_id"])
    dne = dias_na_etapa(app, n)
    out = {"ref": NG.ref(app, n), "nome": (reg or {}).get("razao_social") or n.get("empresa_nome") or "Empresa indicada", "cnpj_mascara": n.get("cnpj_mascara"),
           "estado": e, "rotulo": NG.ROTULO[e], "chip": NG.CHIP.get(e, "info"), "com": NG.BOLA[e], "situacao": situacao(n),
           "produto": produto(app, n), "teses": teses(n), "dias_na_etapa": dne,
           "parado": n.get("status") == "aberto" and dne is not None and dne > app.param("negocio.parado_dias"),
           "criado_em": n.get("criado_em"), "ultima_movimentacao_em": (n.get("ultima_atividade_em") or n.get("hs_modificado_em") or n.get("entrou_etapa_em")),
           "registrado": bool(reg)}
    if visivel(app, ator, "etapa_crm"):
        out["etapa_crm"] = n.get("etapa")
    if visivel(app, ator, "valor_credito"):
        out["valor_credito"] = _num(n.get("valor_credito"))
    if visivel(app, ator, "previsao_fechamento_em") and n.get("status") == "aberto":
        out["previsao_fechamento_em"] = n.get("previsao_fechamento_em")
    if visivel(app, ator, "fechado_em") and n.get("status") != "aberto":
        out["fechado_em"] = n.get("fechado_em")
    if visivel(app, ator, "consultor"):
        out["consultor"] = _nome_par(par, n.get("parceiro_id")) if n.get("master_id") and n.get("parceiro_id") != n.get("master_id") else None
    if visivel(app, ator, "remuneracao_prevista"):
        esc = escritorio(n)
        out["remuneracao_prevista"] = remuneracao_prevista(app, n, (pcts or {}).get(esc))
    if ator.tipo != "parceiro":
        out.update(deal_id=n["deal_id"], master=_nome_par(par, n.get("master_id") or n.get("parceiro_id")), master_id=escritorio(n),
                   consultor=_nome_par(par, n.get("parceiro_id")) if n.get("master_id") and n.get("parceiro_id") != n.get("master_id") else None,
                   cafe=bool(n.get("cafe")))
    return out


def _filtrar(app, xs, c, regs):
    est = [x for x in str(c.get("estado") or "").split(",") if x]
    sit = c.get("situacao") or "andamento"
    if sit not in SITUACOES:
        raise Invalido("Situação inválida.")
    de, ate = _dia(c.get("de")), _dia(c.get("ate"))
    q = str(c.get("q") or "").strip().lower()[:60]
    out = []
    for n in xs:
        if sit != "todos" and situacao(n) != sit:
            continue
        if est and NG.estado(app, n)[0] not in est:
            continue
        if c.get("etapa") and n.get("etapa") != c["etapa"]:
            continue
        if c.get("produto") and produto(app, n) != c["produto"]:
            continue
        if c.get("tese") and c["tese"] not in teses(n):
            continue
        d = _dia(n.get("criado_em"))
        if (de and (not d or d < de)) or (ate and (not d or d > ate)):
            continue
        if c.get("parado") in ("1", 1, True, "true") and not (n.get("status") == "aberto" and (dias_na_etapa(app, n) or 0) > app.param("negocio.parado_dias")):
            continue
        if c.get("registrado") in ("1", "0"):
            if (n["deal_id"] in regs) != (c["registrado"] == "1"):
                continue
        if c.get("mes_previsao") and not str(n.get("previsao_fechamento_em") or "").startswith(c["mes_previsao"]):
            continue
        if c.get("mes_fechamento") and not (n.get("status") == "ganho" and str(n.get("fechado_em") or "").startswith(c["mes_fechamento"])):
            continue
        out.append(n)
    if q:
        nomes = {k: (r.get("razao_social") or "").lower() for k, r in regs.items()}
        out = [n for n in out if q in (nomes.get(n["deal_id"]) or (n.get("empresa_nome") or "").lower()) or q in (n.get("cnpj_mascara") or "").lower()]
    return out


def _ordenar(itens, ordem):
    if ordem not in ORDENS:
        ordem = "recente"
    chave = {
        "recente": (lambda i: i.get("ultima_movimentacao_em") or i.get("criado_em") or "", True),
        "antigo": (lambda i: i.get("criado_em") or "", False),
        "valor": (lambda i: i.get("valor_credito") or 0, True),
        "parado": (lambda i: i.get("dias_na_etapa") or 0, True),
        "nome": (lambda i: (i.get("nome") or "").lower(), False),
        "previsao": (lambda i: i.get("previsao_fechamento_em") or "9999", False),
    }[ordem]
    return sorted(itens, key=chave[0], reverse=chave[1])


def _int(v, padrao, lo, hi):
    try:
        return max(lo, min(hi, int(v)))
    except (TypeError, ValueError):
        return padrao


def listar(app, ator, c):
    """GET parceiro/negocios e save/negocios: lista paginada com filtros, colunas do quadro e opções dos filtros."""
    exigir(ator, "ver_negocios")
    c = dict(c or {})
    if ator.tipo != "parceiro" and c.get("master"):
        xs = [n for n in negocios_do_ator(app, ator) if escritorio(n) == c["master"]]
    else:
        xs = negocios_do_ator(app, ator, c.get("consultor"))
    if ator.tipo != "parceiro" and c.get("cafe") != "1":
        xs = [n for n in xs if not n.get("cafe")]
    regs = _registros_por_deal(app, ator if ator.tipo == "parceiro" else None)
    par = _par(app)
    pcts = {p: _pct_termo(app, p) for p in {escritorio(n) for n in xs}} if visivel(app, ator, "remuneracao_prevista") else {}
    filtrados = _filtrar(app, xs, c, regs)
    itens = _ordenar([item(app, ator, n, par, regs, pcts) for n in filtrados], c.get("ordem"))
    por = _int(c.get("por_pagina"), 25, 1, 200)
    pag = _int(c.get("pagina"), 1, 1, 10 ** 6)
    paginas = max(1, -(-len(itens) // por))
    pag = min(pag, paginas)
    colunas = []
    ver_valor = visivel(app, ator, "valor_credito")
    for e in ABERTOS + ("execucao", "encerrado"):
        do_e = [i for i in itens if i["estado"] == e]
        if e in ABERTOS or do_e:
            colunas.append({"estado": e, "rotulo": NG.ROTULO[e], "n": len(do_e), "valor": round(sum(i.get("valor_credito") or 0 for i in do_e), 2) if ver_valor else None})
    base = [n for n in xs]
    filtros = {"estados": [{"estado": e, "rotulo": NG.ROTULO[e]} for e in NG.ESTADOS],
               "produtos": sorted({produto(app, n) for n in base}), "teses": sorted({t for n in base for t in teses(n)}),
               "etapas": sorted({n.get("etapa") for n in base if n.get("etapa")}) if visivel(app, ator, "etapa_crm") else [],
               "situacoes": [{"chave": "andamento", "rotulo": "Em andamento"}, {"chave": "ganhos", "rotulo": "Contratos assinados"},
                             {"chave": "perdidos", "rotulo": "Encerrados sem contrato"}, {"chave": "todos", "rotulo": "Todos"}],
               "ordens": [{"chave": "recente", "rotulo": "Movimentação mais recente"}, {"chave": "parado", "rotulo": "Mais tempo na etapa"},
                          {"chave": "valor", "rotulo": "Maior crédito estimado"} if ver_valor else None, {"chave": "previsao", "rotulo": "Previsão mais próxima"},
                          {"chave": "antigo", "rotulo": "Entrada mais antiga"}, {"chave": "nome", "rotulo": "Nome da empresa"}]}
    filtros["ordens"] = [o for o in filtros["ordens"] if o]
    if ator.tipo == "parceiro" and ator.papel == "titular":
        filtros["consultores"] = [{"id": u["usuario_id"], "nome": u.get("nome")} for u in app.repo.listar("usuario_parceiro", parceiro_id=ator.parceiro_id, papel="consultor")]
    if ator.tipo != "parceiro":
        filtros["masters"] = sorted([{"id": p["parceiro_id"], "nome": p.get("nome_exibicao")} for p in par.values() if p.get("tipo") == "master"], key=lambda x: x["nome"] or "")
    app.acesso(ator, "negocios", "listar")
    return {"itens": itens[(pag - 1) * por: pag * por], "total": len(itens), "pagina": pag, "por_pagina": por, "paginas": paginas, "colunas": colunas,
            "valor_total": round(sum(i.get("valor_credito") or 0 for i in itens), 2) if ver_valor else None, "filtros": filtros,
            "ressalvas": ressalvas(app, ator), "parado_dias": app.param("negocio.parado_dias")}


# ---------------------------------------------------------------- ficha completa
def _linha_do_tempo(app, n):
    mapa = app.param("negocio.mapa_etapas")
    hist = sorted([x for x in n.get("historico_etapas") or [] if x.get("etapa") and x.get("entrou_em")], key=lambda x: x["entrou_em"])
    if not hist:
        hist = [{"etapa": "Entrada na Save", "entrou_em": n.get("criado_em")}]
        if n.get("entrou_etapa_em") and n.get("etapa"):
            hist.append({"etapa": n["etapa"], "entrou_em": n["entrou_etapa_em"]})
    hoje = _hoje(app)
    out = []
    for i, x in enumerate(hist):
        ini = _dia(x["entrou_em"])
        fim = _dia(hist[i + 1]["entrou_em"]) if i + 1 < len(hist) else (None if n.get("status") == "aberto" else ini)
        atual = i == len(hist) - 1 and n.get("status") == "aberto"
        et = x["etapa"].lower()  # o HubSpot tem "Negócio Fechado" e "Negócio fechado" em funis diferentes
        est = mapa.get(x["etapa"]) or ("execucao" if et == "negócio fechado" else "encerrado" if et in ("negócio perdido", "desqualificado") else None)
        out.append({"etapa": x["etapa"], "estado": NG.ROTULO.get(est) if est else None, "desde": CAL.fmt_data(ini) if ini else "", "desde_iso": str(ini) if ini else None,
                    "dias": ((fim or hoje) - ini).days if ini else None, "atual": atual})
    return out


def _secao(titulo, campos):
    cs = [c for c in campos if c]
    return {"titulo": titulo, "campos": cs} if cs else None


def ficha(app, ator, n):
    """Ficha completa do negócio, só com os campos que a matriz libera ao ator."""
    exigir(ator, "ver_negocios")
    par = _par(app)
    regs = _registros_por_deal(app, ator if ator.tipo == "parceiro" else None)
    reg = regs.get(n["deal_id"])
    e, _ = NG.estado(app, n)
    vp = NG.visao_parceiro(app, n, reg)

    def campo(chave, valor, tipo="texto"):
        if not visivel(app, ator, chave) or valor in (None, "", []):
            return None
        rot, res = _meta(app, chave)
        return {"campo": chave, "rotulo": rot, "valor": valor, "tipo": tipo, "ressalva": res}

    esc = escritorio(n)
    pct = _pct_termo(app, esc) if visivel(app, ator, "percentual_termo") or visivel(app, ator, "remuneracao_prevista") else None
    consultor = _nome_par(par, n.get("parceiro_id")) if n.get("master_id") and n.get("parceiro_id") != n.get("master_id") else None
    proximo = n.get("proximo_passo_crm")
    if proximo and ator.tipo == "parceiro" and (matriz(app).get("proximo_passo_crm") or {}).get("auditar", True):
        proximo = _texto_seguro(proximo)
    secoes = [
        _secao("Situação", [campo("estado", NG.ROTULO[e]), campo("etapa_crm", n.get("etapa")), campo("funil", n.get("pipeline")), campo("produto", produto(app, n)),
                            campo("teses", teses(n), "lista"), campo("proximo_passo_crm", proximo)]),
        _secao("Valores", [campo("valor_credito", _num(n.get("valor_credito")), "reais"), campo("honorario_pct", _num(n.get("honorario_pct")), "pct"),
                           campo("percentual_termo", pct, "pct"), campo("remuneracao_prevista", remuneracao_prevista(app, n, pct), "reais")]),
        _secao("Datas", [campo("criado_em", n.get("criado_em"), "data"), campo("entrou_etapa_em", n.get("entrou_etapa_em"), "data"),
                         campo("ultima_movimentacao_em", n.get("ultima_atividade_em") or n.get("hs_modificado_em"), "data"),
                         campo("previsao_fechamento_em", n.get("previsao_fechamento_em") if n.get("status") == "aberto" else None, "data"),
                         campo("fechado_em", n.get("fechado_em") if n.get("status") != "aberto" else None, "data")]),
        _secao("Pessoas", [campo("responsavel_save", n.get("owner_nome") or "Área Partners"), campo("master", _nome_par(par, esc)), campo("consultor", consultor)]),
        _secao("Empresa", [campo("uf", n.get("uf")), campo("porte", n.get("porte")), campo("segmento", n.get("segmento"))]),
    ]
    if ator.tipo != "parceiro":   # visão Save: também os internos (R110: nada disto sai)
        secoes.append(_secao("Interno da Save", [campo("probabilidade", n.get("probabilidade"), "pct"), campo("notas_internas", n.get("notas_internas")),
                                                 campo("motivo_perda_interno", n.get("motivo_perda_interno")), campo("id_bitrix", n.get("id_bitrix")),
                                                 campo("outras_comissoes", json.dumps(n.get("outras_comissoes"), ensure_ascii=False) if n.get("outras_comissoes") else None)]))
    out = {"ref": NG.ref(app, n), "nome": (reg or {}).get("razao_social") or n.get("empresa_nome") or "Empresa indicada", "cnpj_mascara": n.get("cnpj_mascara"),
           "estado": e, "rotulo": NG.ROTULO[e], "chip": NG.CHIP.get(e, "info"), "com": vp["com"], "desde": vp["desde"], "proximo_passo": vp["proximo_passo"],
           "passos": vp["passos"], "situacao": situacao(n), "dias_na_etapa": dias_na_etapa(app, n), "secoes": [s for s in secoes if s],
           "ressalvas": ressalvas(app, ator)}
    if visivel(app, ator, "historico_etapas"):
        out["linha_do_tempo"] = _linha_do_tempo(app, n)
    if visivel(app, ator, "pendencias"):
        out["pendencias"] = [{"tipo": NG.TIPOS_PENDENCIA.get(p["tipo"]), "texto": p.get("texto"), "desde": CAL.fmt_data(p["aberta_em"]),
                              "resolvida_em": CAL.fmt_data(p["resolvida_em"]) if p.get("resolvida_em") else None}
                             for p in sorted(app.repo.listar("pendencia", deal_id=n["deal_id"]), key=lambda p: p["aberta_em"], reverse=True)]
    if visivel(app, ator, "documentos"):
        docs = [{"item": d.get("item"), "situacao": d.get("situacao")} for d in n.get("documentos_solicitados") or [] if d.get("item")]
        docs.append({"item": "Acesso ao e-CAC", "situacao": "liberado" if n.get("ecac_liberado") else "pendente"})
        if n.get("tem_anexo_diagnostico"):
            docs.append({"item": "Diagnóstico anexado ao negócio", "situacao": "recebido"})
        out["documentos"] = docs
    if visivel(app, ator, "registro") and reg:
        v = RG.visao_parceiro(app, reg)
        out["registro"] = {"registro_id": reg["registro_id"], "rotulo": v["rotulo"], "chip": v["chip"], "carimbo": v.get("carimbo"), "valido_ate": v.get("valido_ate"),
                           "ref": reg.get("ref")}
    if visivel(app, ator, "demandas"):
        refs = {out["ref"], (reg or {}).get("ref")}
        ds = DM.do_ator(app, ator) if ator.tipo == "parceiro" else app.repo.listar("demanda")
        out["pedidos"] = [{"ref": d["ref"], "id": d["demanda_id"], "rotulo": DM.ROTULO.get(d["estado"], d["estado"]), "chip": DM.CHIP.get(d["estado"], "info"),
                           "aberta_em": CAL.fmt(d["aberta_em"])} for d in ds
                          if (d.get("empresa") or {}).get("ref") in refs or (d.get("empresa") or {}).get("deal_id") == n["deal_id"]]
    if visivel(app, ator, "extrato"):
        out["extrato"] = [EX.visao_parceiro(app, x, out["nome"]) for x in EX.linhas(app)
                          if x["deal_id"] == n["deal_id"] and (ator.tipo != "parceiro" or x["escritorio"] == ator.parceiro_id)]
    if ator.tipo != "parceiro":
        out.update(deal_id=n["deal_id"], master=_nome_par(par, esc), cafe=bool(n.get("cafe")))
    app.acesso(ator, "negocio", "ler", out["ref"])
    return out


def ficha_parceiro(app, ator, ref):
    n = NG.por_ref(app, ator, ref)
    if not n:
        app.acesso(ator, "negocio", "ler", ref, "negado")
        raise NaoEncontrado("Este negócio não está na sua lista.")
    return ficha(app, ator, n)


def ficha_save(app, ator, deal_id):
    exigir(ator, "ver_negocios")
    n = app.repo.obter("negocio", deal_id)
    if not n:
        raise NaoEncontrado()
    return ficha(app, ator, n)


# ---------------------------------------------------------------- agregados (PRM-R116)
def _janela(app, c):
    """(ini, fim, ini_anterior, fim_anterior, dias). `periodo` em dias (30/90/180/365) ou `de`/`ate`."""
    hoje = _hoje(app)
    de, ate = _dia(c.get("de")), _dia(c.get("ate"))
    if de or ate:
        fim = ate or hoje
        ini = de or (fim - timedelta(days=89))
        if ini > fim:
            raise Invalido("A data inicial é depois da final.")
    else:
        dias = _int(c.get("periodo"), 90, 7, 730)
        fim, ini = hoje, hoje - timedelta(days=dias - 1)
    n = (fim - ini).days + 1
    return ini, fim, ini - timedelta(days=n), ini - timedelta(days=1), n


def _entre(d, ini, fim):
    d = _dia(d)
    return bool(d) and ini <= d <= fim


def _taxa(g, p, minimo):
    n = g + p
    return {"ganhos": g, "perdidos": p, "n": n, "pct": round(100.0 * g / n, 1) if n >= minimo and n else None, "base_pequena": n < minimo}


def _ciclo(app, ganhos):
    ds = [(_dia(n["fechado_em"]) - _dia(n["criado_em"])).days for n in ganhos if _dia(n.get("fechado_em")) and _dia(n.get("criado_em"))]
    ds = [d for d in ds if d >= 0]
    return {"n": len(ds), "media_dias": round(statistics.mean(ds), 1) if ds else None, "mediana_dias": round(statistics.median(ds), 1) if ds else None}


def _soma(ns):
    return round(sum(_num(n.get("valor_credito")) or 0 for n in ns), 2)


def _delta(a, b):
    if a is None or b is None:
        return None
    return round(a - b, 2)


def _bloco_periodo(app, xs, ini, fim, minimo):
    fech = [n for n in xs if n.get("status") in ("ganho", "perdido") and _entre(n.get("fechado_em"), ini, fim)]
    g = [n for n in fech if n["status"] == "ganho"]
    p = [n for n in fech if n["status"] == "perdido"]
    novos = [n for n in xs if _entre(n.get("criado_em"), ini, fim)]
    return {"ganhos": {"n": len(g), "valor": _soma(g)}, "perdidos": {"n": len(p), "valor": _soma(p)}, "conversao": _taxa(len(g), len(p), minimo),
            "ciclo": _ciclo(app, g), "novos": {"n": len(novos), "valor": _soma(novos)}, "_ganhos": g}


def _pipeline(app, xs, com_valor=True):
    ab = [n for n in xs if n.get("status") == "aberto"]
    out = []
    for e in ABERTOS:
        do_e = [n for n in ab if NG.estado(app, n)[0] == e]
        out.append({"estado": e, "rotulo": NG.ROTULO[e], "n": len(do_e), "valor": _soma(do_e) if com_valor else None,
                    "sem_valor": sum(1 for n in do_e if _num(n.get("valor_credito")) is None)})
    return out


def _funil(app, xs, ini, fim):
    """Coorte: negócios que entraram no período; quantos chegaram a cada etapa (histórico + estado atual)."""
    coorte = [n for n in xs if _entre(n.get("criado_em"), ini, fim)]
    mx = [nivel_maximo(app, n) for n in coorte]
    out = []
    for i, (k, rot) in enumerate(FUNIL):
        q = sum(1 for m in mx if m >= i)
        out.append({"etapa": k, "rotulo": rot, "n": q, "pct_do_inicio": round(100.0 * q / len(coorte), 1) if coorte else None})
    for i in range(1, len(out)):
        a = out[i - 1]["n"]
        out[i]["pct_da_anterior"] = round(100.0 * out[i]["n"] / a, 1) if a else None
    return {"coorte": len(coorte), "etapas": out}


def _aging(app, xs, limite_lista=10):
    ab = [n for n in xs if n.get("status") == "aberto"]
    lim = app.param("negocio.parado_dias")
    por_estado = []
    for e in ABERTOS:
        dias = [dias_na_etapa(app, n) or 0 for n in ab if NG.estado(app, n)[0] == e]
        faixas = [{"faixa": rot, "n": sum(1 for d in dias if d >= lo and (hi is None or d <= hi))} for lo, hi, rot in FAIXAS_AGING]
        por_estado.append({"estado": e, "rotulo": NG.ROTULO[e], "n": len(dias), "media_dias": round(statistics.mean(dias), 1) if dias else None,
                           "parados": sum(1 for d in dias if d > lim), "faixas": faixas})
    parados = sorted([n for n in ab if (dias_na_etapa(app, n) or 0) > lim], key=lambda n: -(dias_na_etapa(app, n) or 0))
    return {"limite_dias": lim, "faixas": [rot for _, _, rot in FAIXAS_AGING], "por_estado": por_estado, "total_parados": len(parados), "_parados": parados[:limite_lista]}


def _comparacao(atual, ant):
    def par(a, b):
        return {"atual": a, "anterior": b, "delta": _delta(a, b)}
    return {"ganhos_n": par(atual["ganhos"]["n"], ant["ganhos"]["n"]), "ganhos_valor": par(atual["ganhos"]["valor"], ant["ganhos"]["valor"]),
            "perdidos_n": par(atual["perdidos"]["n"], ant["perdidos"]["n"]), "novos_n": par(atual["novos"]["n"], ant["novos"]["n"]),
            "conversao_pct": par(atual["conversao"]["pct"], ant["conversao"]["pct"]), "ciclo_dias": par(atual["ciclo"]["media_dias"], ant["ciclo"]["media_dias"])}


def _limpo(b):
    return {k: v for k, v in b.items() if not k.startswith("_")}


def painel_parceiro(app, ator, c):
    """GET parceiro/painel: o pipeline e os resultados do próprio escopo; nunca comparação com outro parceiro (R27)."""
    exigir(ator, "ver_negocios")
    c = dict(c or {})
    ini, fim, ia, fa, dias = _janela(app, c)
    xs = negocios_do_ator(app, ator, c.get("consultor"))
    regs = _registros_por_deal(app, ator)
    par = _par(app)
    minimo = app.param("painel.base_pequena")
    ver_valor = visivel(app, ator, "valor_credito")
    atual, ant = _bloco_periodo(app, xs, ini, fim, minimo), _bloco_periodo(app, xs, ia, fa, minimo)
    ag = _aging(app, xs)
    hoje = _hoje(app)
    mes = hoje.replace(day=1)
    meus_regs = [r for r in app.repo.listar("registro") if ve(ator, r) and r["estado"] != "rascunho"]
    dems = DM.do_ator(app, ator)
    out = {"periodo": {"de": str(ini), "ate": str(fim), "dias": dias, "anterior_de": str(ia), "anterior_ate": str(fa)},
           "pipeline": _pipeline(app, xs, ver_valor), "funil": _funil(app, xs, ini, fim), "periodo_atual": _limpo(atual), "periodo_anterior": _limpo(ant),
           "comparacao": _comparacao(atual, ant), "aging": dict(_limpo(ag), parados=[item(app, ator, n, par, regs) for n in ag["_parados"]]),
           "atividade": {"registros_no_mes": sum(1 for r in meus_regs if _dia(r.get("carimbo")) and _dia(r["carimbo"]) >= mes),
                         "registros_no_periodo": sum(1 for r in meus_regs if _entre(r.get("carimbo"), ini, fim)),
                         "demandas_abertas": sum(1 for d in dems if d["estado"] not in ("concluida", "respondida")),
                         "negocios_abertos": sum(1 for n in xs if n.get("status") == "aberto")},
           "ressalvas": ressalvas(app, ator), "base_pequena_n": minimo,
           "consultores": [{"id": u["usuario_id"], "nome": u.get("nome")} for u in app.repo.listar("usuario_parceiro", parceiro_id=ator.parceiro_id, papel="consultor")]
           if ator.papel == "titular" else []}
    if not ver_valor:
        for b in (out["periodo_atual"], out["periodo_anterior"]):
            for k in ("ganhos", "perdidos", "novos"):
                b[k]["valor"] = None
        for k in ("ganhos_valor",):
            out["comparacao"][k] = {"atual": None, "anterior": None, "delta": None}
    if visivel(app, ator, "remuneracao_prevista"):
        pct = _pct_termo(app, ator.parceiro_id)
        lins = [x for x in EX.linhas(app) if x["escritorio"] == ator.parceiro_id and x["deal_id"] in {n["deal_id"] for n in xs}]
        com_valor = {x["deal_id"] for x in lins if x["estado"] in EX.COM_VALOR}
        prevista = sum(remuneracao_prevista(app, n, pct) or 0 for n in xs if n.get("status") == "ganho" and n["deal_id"] not in com_valor)
        sem_calc = sum(1 for n in xs if n.get("status") == "ganho" and n["deal_id"] not in com_valor and remuneracao_prevista(app, n, pct) is None)
        recebida = sum(_num(x.get("valor_bruto")) or 0 for x in lins if x["estado"] in ("recebido_pela_save", "calculado", "liberado", "aguardando_nf", "contestada"))
        paga = sum(_num(x.get("valor_liquido")) or 0 for x in lins if x["estado"] == "pago")
        out["remuneracao"] = {"prevista": round(prevista, 2), "recebida_pela_save": round(recebida, 2), "paga": round(paga, 2), "ganhos_sem_calculo": sem_calc,
                              "percentual_termo": pct, "ressalva": _meta(app, "remuneracao_prevista")[1]}
    app.acesso(ator, "painel", "ler")
    return out


# ---------------------------------------------------------------- dashboard comercial da Save (PRM-R117)
def metas(app):
    """Meta mensal D111: registro/gestao/gestao.json (pacote da Gestão) se existir; senão o parâmetro canal.meta_mensal."""
    base = os.environ.get("PRM_GESTAO") or os.path.join(os.path.expanduser(os.environ.get("PARTNERS_AP") or "~/agentes-partners"), "registro", "gestao", "gestao.json")
    try:
        with open(base, encoding="utf-8") as f:
            m = json.load(f).get("meta") or {}
        meses = {x["mes"]: float(x["meta_rs"]) for x in m.get("meses") or [] if x.get("mes") and x.get("meta_rs")}
        if meses:
            return meses, "gestao.json (%s)" % (m.get("decisao") or "D111")
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        pass
    return {k: float(v) for k, v in app.param("canal.meta_mensal").items()}, "parâmetro canal.meta_mensal (D111)"


def _mes_nome(m):
    nomes = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    a, mm = m.split("-")
    return "%s/%s" % (nomes[int(mm) - 1], a[2:])


def dashboard_canal(app, ator, c):
    """GET save/dashboard: dashboard comercial do canal, filtros de período e Master; cada bloco traz o filtro do drill-down."""
    exigir(ator, "ver_canal_agregado")
    c = dict(c or {})
    ini, fim, ia, fa, dias = _janela(app, c)
    par = _par(app)
    todos = [n for n in app.repo.listar("negocio") if escritorio(n) and not n.get("cafe")]
    master = c.get("master") or None
    xs = [n for n in todos if not master or escritorio(n) == master]
    minimo = app.param("painel.base_pequena")
    hoje = _hoje(app)
    atual, ant = _bloco_periodo(app, xs, ini, fim, minimo), _bloco_periodo(app, xs, ia, fa, minimo)
    ag = _aging(app, xs, 15)
    regs = _registros_por_deal(app)
    # por Master (ordem alfabética: não é ranking) e por consultor
    pm = []
    for pid, p in sorted(par.items(), key=lambda kv: kv[1].get("nome_exibicao") or ""):
        if p.get("tipo") != "master" or (master and pid != master):
            continue
        meus = [n for n in todos if escritorio(n) == pid]
        b = _bloco_periodo(app, meus, ini, fim, minimo)
        ab = [n for n in meus if n.get("status") == "aberto"]
        pm.append({"master_id": pid, "nome": p.get("nome_exibicao"), "abertos": len(ab), "valor_aberto": _soma(ab), "ganhos_n": b["ganhos"]["n"],
                   "ganhos_valor": b["ganhos"]["valor"], "conversao": b["conversao"], "ciclo_medio_dias": b["ciclo"]["media_dias"],
                   "parados": sum(1 for n in ab if (dias_na_etapa(app, n) or 0) > app.param("negocio.parado_dias")),
                   "drill": {"master": pid, "situacao": "andamento"}})
    pc = defaultdict(list)
    for n in xs:
        if n.get("master_id") and n.get("parceiro_id") and n["parceiro_id"] != n["master_id"]:
            pc[n["parceiro_id"]].append(n)
    por_consultor = []
    for pid, ns in sorted(pc.items(), key=lambda kv: _nome_par(par, kv[0]) or ""):
        ab = [n for n in ns if n.get("status") == "aberto"]
        b = _bloco_periodo(app, ns, ini, fim, minimo)
        por_consultor.append({"parceiro_id": pid, "nome": _nome_par(par, pid), "master": _nome_par(par, ns[0]["master_id"]), "abertos": len(ab),
                              "valor_aberto": _soma(ab), "ganhos_n": b["ganhos"]["n"], "ganhos_valor": b["ganhos"]["valor"], "tipo": (par.get(pid) or {}).get("tipo")})
    # forecast por mês contra a meta D111 (previsão = data de fechamento do CRM, sem ponderar por probabilidade)
    mt, fonte_meta = metas(app)
    forecast = []
    for m in sorted(mt):
        ganhos_m = [n for n in xs if n.get("status") == "ganho" and str(n.get("fechado_em") or "").startswith(m)]
        prev = [n for n in xs if n.get("status") == "aberto" and str(n.get("previsao_fechamento_em") or "").startswith(m)]
        contrato = [n for n in prev if NG.estado(app, n)[0] == "contrato"]
        outros = [n for n in prev if n not in contrato]
        meta_m = None if master else mt[m]
        realizado = _soma(ganhos_m)
        forecast.append({"mes": m, "rotulo": _mes_nome(m), "meta": meta_m, "realizado": realizado, "em_contrato": _soma(contrato), "demais_abertos": _soma(outros),
                         "n_realizado": len(ganhos_m), "n_contrato": len(contrato), "n_demais": len(outros), "passado": m < hoje.strftime("%Y-%m"),
                         "pct_meta_realizado": round(100.0 * realizado / meta_m, 1) if meta_m else None,
                         "drill": {"mes_fechamento": m, "situacao": "ganhos"}, "drill_previsao": {"mes_previsao": m, "situacao": "andamento"}})
    # concentração (crédito ganho em 12 meses, sem café; fora do roster conta como um balde só) — métrica de guarda
    val = Counter()
    for n in todos:
        if n.get("status") == "ganho" and _dia(n.get("fechado_em")) and (hoje - _dia(n["fechado_em"])).days <= 365:
            val[n.get("master_id") or "fora_do_roster"] += _num(n.get("valor_credito")) or 0
    tot = sum(val.values())
    top = val.most_common(5)
    concentracao = {"total_12m": round(tot, 2), "top1_pct": round(100 * top[0][1] / tot, 1) if tot else None,
                    "top5_pct": round(100 * sum(v for _, v in top) / tot, 1) if tot else None,
                    "top5": [{"master_id": k, "nome": _nome_par(par, k) or "Fora do roster", "valor": round(v, 2), "pct": round(100 * v / tot, 1)} for k, v in top]}
    # dormentes: sem negócio novo em canal.dormente_dias e com ganho em 12 meses (02 §11)
    dorm = []
    lim = app.param("canal.dormente_dias")
    for pid, p in sorted(par.items(), key=lambda kv: kv[1].get("nome_exibicao") or ""):
        if master and pid != master and p.get("master_id") != master:
            continue
        meus = [n for n in todos if (n.get("parceiro_id") == pid) or (p.get("tipo") == "master" and escritorio(n) == pid)]
        if not meus:
            continue
        ult = max([_dia(n["criado_em"]) for n in meus if _dia(n.get("criado_em"))] or [None]) if meus else None
        g12 = sum(1 for n in meus if n.get("status") == "ganho" and _dia(n.get("fechado_em")) and (hoje - _dia(n["fechado_em"])).days <= 365)
        d = (hoje - ult).days if ult else None
        if d is not None and d > lim and g12:
            dorm.append({"parceiro_id": pid, "nome": p.get("nome_exibicao"), "tipo": p.get("tipo"), "dias_sem_negocio": d, "ganhos_12m": g12})
    # conversão registrado × não registrado (fechados no período; associação, não causa — 03 §5)
    minimo_reg = app.param("canal.base_pequena_conversao_registro")
    fech = [n for n in xs if n.get("status") in ("ganho", "perdido") and _entre(n.get("fechado_em"), ini, fim)]
    rg = [n for n in fech if n["deal_id"] in regs]
    nr = [n for n in fech if n["deal_id"] not in regs]
    conv_reg = {"registrado": dict(_taxa(sum(1 for n in rg if n["status"] == "ganho"), sum(1 for n in rg if n["status"] == "perdido"), minimo_reg),
                                   drill={"registrado": "1", "situacao": "todos"}),
                "nao_registrado": dict(_taxa(sum(1 for n in nr if n["status"] == "ganho"), sum(1 for n in nr if n["status"] == "perdido"), minimo_reg),
                                       drill={"registrado": "0", "situacao": "todos"}),
                "nota": "Associação, não causa: quem registra tende a ser o parceiro mais organizado."}
    # produtos e teses
    prods = defaultdict(list)
    for n in xs:
        prods[produto(app, n)].append(n)
    por_produto = []
    for k in sorted(prods):
        ns = prods[k]
        ab = [n for n in ns if n.get("status") == "aberto"]
        b = _bloco_periodo(app, ns, ini, fim, minimo)
        por_produto.append({"produto": k, "abertos": len(ab), "valor_aberto": _soma(ab), "ganhos_n": b["ganhos"]["n"], "ganhos_valor": b["ganhos"]["valor"],
                            "conversao": b["conversao"], "drill": {"produto": k, "situacao": "andamento"}})
    ts = defaultdict(list)
    for n in xs:
        for t in teses(n):
            ts[t].append(n)
    por_tese = [{"tese": t, "abertos": sum(1 for n in ns if n.get("status") == "aberto"), "valor_aberto": _soma([n for n in ns if n.get("status") == "aberto"]),
                 "ganhos_12m": sum(1 for n in ns if n.get("status") == "ganho" and _dia(n.get("fechado_em")) and (hoje - _dia(n["fechado_em"])).days <= 365),
                 "drill": {"tese": t, "situacao": "andamento"}} for t, ns in sorted(ts.items())]
    pipe = _pipeline(app, xs)
    for p in pipe:
        p["drill"] = {"estado": p["estado"], "situacao": "andamento"}
    for e in ag["por_estado"]:
        e["drill"] = {"estado": e["estado"], "situacao": "andamento", "parado": "1"}
    ab = [n for n in xs if n.get("status") == "aberto"]
    kpis = {"pipeline_n": len(ab), "pipeline_valor": _soma(ab), "ganhos_n": atual["ganhos"]["n"], "ganhos_valor": atual["ganhos"]["valor"],
            "conversao": atual["conversao"], "ciclo": atual["ciclo"], "parados": ag["total_parados"], "dormentes": len(dorm), "novos_n": atual["novos"]["n"]}
    app.acesso(ator, "dashboard_comercial", "ler", master)
    return {"periodo": {"de": str(ini), "ate": str(fim), "dias": dias, "anterior_de": str(ia), "anterior_ate": str(fa)}, "master": master,
            "masters": [{"id": pid, "nome": p.get("nome_exibicao")} for pid, p in sorted(par.items(), key=lambda kv: kv[1].get("nome_exibicao") or "") if p.get("tipo") == "master"],
            "kpis": kpis, "comparacao": _comparacao(atual, ant), "pipeline": pipe, "funil": _funil(app, xs, ini, fim),
            "aging": dict(_limpo(ag), parados=[item(app, ator, n, par, regs) for n in ag["_parados"]]), "por_master": pm, "por_consultor": por_consultor,
            "forecast": {"meses": forecast, "fonte_meta": fonte_meta, "nota": "Previsão = data de assinatura prevista no CRM, sem ponderar por probabilidade. Com filtro de Master, a meta do canal não se aplica."},
            "concentracao": concentracao, "dormentes": dorm, "conversao_registro": conv_reg, "por_produto": por_produto, "por_tese": por_tese,
            "fonte": {"espelho_ate": max([n.get("hs_modificado_em") for n in todos if n.get("hs_modificado_em")] or [None]),
                      "regras": "Sem café e sem negócio fora do roster (PRM-R112/R117)."}}
