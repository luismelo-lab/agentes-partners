"""Face da Save, seção Canal (05 §2.2 e §3; 02 §11): visão do canal, fila de registros, conflitos, demandas por SLA,
extratos a liberar, dossiês da esteira, acessos e níveis em sombra. Nada daqui vai ao lado externo (PRM-R110);
margem e comissões internas não aparecem (R111); café fora dos indicadores (R112)."""
from collections import Counter
from datetime import timedelta

from .. import esteira
from . import calendario as CAL
from . import demandas as DM
from . import extrato as EX
from . import negocios as NG
from . import nivel as NV
from . import notificacoes as NT
from . import registro as RG
from .identidade import exigir
from .parametros import catalogo


def _par(app):
    return {p["parceiro_id"]: p for p in app.repo.listar("parceiro")}


def visao(app, ator):
    exigir(ator, "ver_canal_agregado")
    hoje, agora = CAL.dia(app.agora()), app.agora()
    regs = app.repo.listar("registro")
    negs = app.repo.listar("negocio")
    fila = [r for r in regs if r["estado"] in ("em_analise", "aguardando_parceiro")]
    a_vencer = [r for r in regs if r["estado"] in ("aprovado", "prorrogado", "convertido") and (r.get("prorrogado_ate") or r.get("valido_ate"))
                and 0 <= (CAL.dia(r.get("prorrogado_ate") or r["valido_ate"]) - hoje).days <= 15]
    sem_card = [r for r in regs if r["estado"] == "aprovado" and not r.get("deal_id") and r.get("decidido_em")
                and app.cal.du_entre(r["decidido_em"], agora) > app.param("registro.alerta_sem_card_du")]
    conflitos = [c for c in app.repo.listar("conflito") if c["estado"] == "aberto"]
    portal, outras = DM.fila_save(app)
    fora = [d for d in portal if d["sla"]["chip"] == "erro"]
    lin = EX.linhas(app)
    conf_30 = [x for x in lin if x["estado"] == "em_conferencia"]
    lotes = [l for l in EX.lotes(app) if l["calculadas"]]
    teto = app.param("registro.teto_neutros_dia_usuario")
    neutras = [c for c in app.repo.listar("contador") if c["chave"].startswith("neutra|") and c["chave"].endswith(hoje.isoformat()) and int(c["n"]) > teto]
    sem_mapa = sum(1 for n in negs if n.get("status") == "aberto" and NG.estado(app, n)[1])
    kpis = [
        {"chave": "registros", "rotulo": "Registros a decidir", "valor": len(fila), "go": "canal/registros", "apoio": "fila por ordem de chegada"},
        {"chave": "conflitos", "rotulo": "Conflitos abertos", "valor": len(conflitos), "go": "canal/conflitos",
         "apoio": "%d de severidade alta" % sum(1 for c in conflitos if c.get("severidade") == "alta")},
        {"chave": "demandas", "rotulo": "Pedidos fora do prazo", "valor": len(fora), "go": "canal/demandas", "apoio": "de %d abertos no portal" % len(portal)},
        {"chave": "extratos", "rotulo": "Lotes a liberar", "valor": len(lotes), "go": "canal/extratos", "apoio": "%d linha(s) em conferência" % len(conf_30)},
        {"chave": "vencer", "rotulo": "Registros a vencer", "valor": len(a_vencer), "go": "canal/registros", "apoio": "em até 15 dias"},
        {"chave": "semcard", "rotulo": "Registros sem card", "valor": len(sem_card), "go": "canal/registros", "apoio": "mais de %d d.u. após aprovar" % app.param("registro.alerta_sem_card_du")},
        {"chave": "varredura", "rotulo": "Acima do teto de neutras", "valor": len(neutras), "go": "canal/acessos", "apoio": "usuários hoje (possível varredura)"},
        {"chave": "mapa", "rotulo": "Etapas sem mapa", "valor": sem_mapa, "go": "canal", "apoio": "negócios abertos (aviso ao Dados)"},
    ]
    par = _par(app)
    saude = []
    for pid, p in par.items():
        if p.get("tipo") != "master":
            continue
        meus = [n for n in negs if (n.get("master_id") or n.get("parceiro_id")) == pid and not n.get("cafe")]
        abertos = sum(1 for n in meus if n.get("status") == "aberto")
        g12 = sum(1 for n in meus if n.get("status") == "ganho" and n.get("fechado_em") and (hoje - CAL.dia(n["fechado_em"])).days <= 365)
        ult = max([CAL.dia(n["criado_em"]) for n in meus if n.get("criado_em")] or [None]) if meus else None
        dias = (hoje - ult).days if ult else None
        dormente = dias is not None and dias > app.param("canal.dormente_dias") and g12 > 0
        leitura = "sem negócio no espelho" if not meus else ("dormente: %d dias sem negócio novo" % dias if dormente else "%d aberto(s), %d ganho(s) em 12 meses" % (abertos, g12))
        acao = "Conversa de reativação (por pessoa)" if dormente else ("Plano de conta" if abertos else "Lista curta de empresas da BDR")
        saude.append({"parceiro_id": pid, "nome": p.get("nome_exibicao"), "abertos": abertos, "ganhos_12m": g12, "dias_sem_negocio": dias, "leitura": leitura,
                      "acao": acao, "registros_vivos": sum(1 for r in regs if r["parceiro_id"] == pid and r["estado"] in ("aprovado", "prorrogado", "convertido", "em_analise"))})
    val = Counter()
    for n in negs:
        if n.get("status") == "ganho" and not n.get("cafe") and n.get("fechado_em") and (hoje - CAL.dia(n["fechado_em"])).days <= 365:
            val[n.get("master_id") or "fora_do_roster"] += n.get("valor_credito") or 0
    tot = sum(val.values()); top = [v for _, v in val.most_common()]
    alertas = [n for n in NT.do_ator(app, ator) if n["tipo"] == "alerta" and not n["lido"]][:8]
    app.acesso(ator, "canal", "ler")
    return {"kpis": kpis, "saude": sorted(saude, key=lambda s: s["nome"] or ""), "alertas": alertas,
            "concentracao": {"top1_pct": round(100 * top[0] / tot, 1) if tot else None, "top5_pct": round(100 * sum(top[:5]) / tot, 1) if tot else None},
            "fonte": _fonte(app)}


def _fonte(app):
    datas = [n.get("hs_modificado_em") or n.get("criado_em") for n in app.repo.listar("negocio")]
    return {"espelho_ate": max([d for d in datas if d] or [None]) if datas else None}


def registros(app, ator, estado=None):
    exigir(ator, "ver_registros")
    par = _par(app)
    xs = app.repo.listar("registro")
    if estado:
        xs = [r for r in xs if r["estado"] == estado]
    ordem = {"em_analise": 0, "aguardando_parceiro": 1, "em_conflito": 2}
    xs.sort(key=lambda r: (ordem.get(r["estado"], 9), r.get("carimbo") or ""))
    out = []
    for r in xs:
        v = RG.visao_save(app, r)
        v["parceiro"] = (par.get(r["parceiro_id"]) or {}).get("nome_exibicao")
        v["pode_decidir_agora"] = r["estado"] != "em_analise" or app.agora() >= CAL.ler(r["pode_decidir_em"])
        out.append(v)
    app.acesso(ator, "fila_registros", "listar")
    return {"itens": out, "motivos": [{"n": k, "texto": RG.T(v, campos="{campos}") if k == 1 else RG.T(v)} for k, v in RG.MOTIVOS.items()],
            "parceiros": [{"id": p["parceiro_id"], "nome": p.get("nome_exibicao"), "tipo": p.get("tipo")} for p in par.values()]}


def conflitos(app, ator):
    exigir(ator, "ver_registros")
    par = _par(app)
    out = []
    for c in sorted(app.repo.listar("conflito"), key=lambda c: (c["estado"] != "aberto", c["aberto_em"])):
        c = dict(c)
        c["partes_nomes"] = [(par.get(p) or {}).get("nome_exibicao", p) for p in c.get("partes", [])]
        c["registros_det"] = [RG.visao_save(app, app.repo.obter("registro", rid)) for rid in c.get("registros", []) if app.repo.obter("registro", rid)]
        c["pode_decidir"] = ator.papel == "luis" and c["estado"] == "aberto"
        out.append(c)
    app.acesso(ator, "conflitos", "listar")
    return {"itens": out}


def demandas(app, ator):
    exigir(ator, "responder_demanda") if ator.papel != "luis" else None
    portal, outras = DM.fila_save(app)
    app.acesso(ator, "demandas", "listar")
    return {"itens": portal, "registro_unico": outras}


def extratos(app, ator):
    exigir(ator, "ver_extrato")
    par = _par(app)
    lin = EX.linhas(app)
    pend_rec = [{"linha_id": x["linha_id"], "parceiro": (par.get(x["escritorio"]) or {}).get("nome_exibicao"), "competencia": x.get("competencia"),
                 "estado": x["estado"], "rotulo": EX.ROTULO.get(x["estado"])} for x in lin if x["estado"] in ("previsto", "recebido_pela_save", "em_conferencia")]
    nf = [{"linha_id": x["linha_id"], "parceiro": (par.get(x["escritorio"]) or {}).get("nome_exibicao"), "bruto": EX.reais(x.get("valor_bruto")),
           "competencia": x.get("competencia_recebimento")} for x in lin if x["estado"] == "aguardando_nf"]
    cont = [dict(c, parceiro=(par.get(c["parceiro_id"]) or {}).get("nome_exibicao")) for c in app.repo.listar("contestacao") if c["estado"] in ("aberta", "em_analise")]
    app.acesso(ator, "extratos", "listar")
    return {"lotes": EX.lotes(app), "linhas": pend_rec, "aguardando_nf": nf, "contestacoes": cont, "pode_agir": ator.papel == "financeiro"}


def dossies(app, ator):
    exigir(ator, "ver_registros")
    regs = {r.get("dossie_id"): r for r in app.repo.listar("registro") if r.get("dossie_id")}
    out = []
    for p in esteira._todos():
        r = regs.get(p["id"])
        if not r:
            continue
        out.append({"id": p["id"], "registro_id": r["registro_id"], "empresa": r.get("razao_social"), "cnpj_mascara": r.get("cnpj_mascara"), "status": p["status"],
                    "andamento": esteira.ROTULO.get(p["status"], p["status"]), "nivel": p.get("nivel"), "auditoria": p.get("auditoria"), "criado": p.get("criado"),
                    "pode_aprovar": p["status"] in ("aguardando_aprovacao", "revisao_humana") and ator.papel in ("daniela", "luis"),
                    "secoes": [s.get("titulo") for s in ((p.get("resultado") or {}).get("dossie") or [])]})
    app.acesso(ator, "dossies", "listar")
    return {"itens": sorted(out, key=lambda x: x["criado"] or "", reverse=True)}


def acessos(app, ator):
    exigir(ator, "gerir_acessos")
    par = _par(app)
    log = app.repo.listar("acesso_log")
    ult = {}
    for a in log:
        if a.get("usuario_id"):
            ult[a["usuario_id"]] = max(ult.get(a["usuario_id"], ""), a["quando"])
    hoje = CAL.dia(app.agora()).isoformat()
    neutras = {c["chave"].split("|")[1]: int(c["n"]) for c in app.repo.listar("contador") if c["chave"].startswith("neutra|") and c["chave"].endswith(hoje)}
    us = [{"usuario_id": u["usuario_id"], "nome": u.get("nome"), "papel": u["papel"], "parceiro": (par.get(u["parceiro_id"]) or {}).get("nome_exibicao"),
           "estado": u.get("estado"), "ultimo_acesso": CAL.fmt(ult.get(u["usuario_id"])) if ult.get(u["usuario_id"]) else "—",
           "neutras_hoje": neutras.get(u["usuario_id"], 0), "termos": u.get("termos_versao")} for u in app.repo.listar("usuario_parceiro")]
    trilha = sorted(log, key=lambda a: a["quando"], reverse=True)[:40]
    app.acesso(ator, "acessos", "listar")
    return {"usuarios": us, "trilha": [{"quando": CAL.fmt(a["quando"]), "quem": a.get("usuario_id") or a.get("conta_time"), "tela": a["tela"], "acao": a["acao"],
                                        "resultado": a["resultado"]} for a in trilha], "teto_neutras": app.param("registro.teto_neutros_dia_usuario")}


def niveis(app, ator):
    exigir(ator, "ver_canal")
    return {"modo": app.param("nivel.modo"), "itens": NV.visao_save(app)}


def parametros(app, ator):
    exigir(ator, "ver_canal")
    cat = catalogo()
    return {"itens": [{"chave": k, "valor": app.param(k), "padrao": v["valor"], "unidade": v["unidade"], "marca": v["marca"], "quem_muda": v["quem_muda"]}
                      for k, v in sorted(cat.items())]}
