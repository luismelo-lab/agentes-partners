"""Módulo 5 · Nível e jornada (02 §8), em leitura-sombra (PRM-R81, nivel.modo = sombra): o sistema apura e mostra só à
Save. O parceiro vê a jornada (8.1) e o aviso "em teste"; nunca faixa, barra, patamar em R$ nem comparação (R12, R27, R87).
Volume ativo = líquido Save dos ganhos em 12 meses (valor do crédito × % de honorário), sem café (R30), com limite por
negócio (nivel.limite_por_negocio). Patamares de nivel.patamares (F8 e D75, recalibrados quando a meta 2027 sair)."""
from datetime import timedelta

from . import calendario as CAL

JORNADA = ("registrado", "certificado", "pleno", "master")
ROTULO_JORNADA = {"registrado": "Registrado", "certificado": "Certificado", "pleno": "Pleno", "master": "Master"}


def _trimestre(d):
    return "%dT%d" % (d.year, (d.month - 1) // 3 + 1)


def apurar(app, parceiro_id):
    hoje = CAL.dia(app.agora())
    ini = hoje - timedelta(days=round(app.param("nivel.janela_meses") * 30.44))
    pat = app.param("nivel.patamares"); lim = app.param("nivel.limite_por_negocio")
    teto = min(pat["estrategico"]["sobe"] * lim["estrategico_pct_patamar"] / 100.0, float("inf"))
    vol, por_tri = 0.0, {}
    for n in app.repo.listar("negocio"):
        if (n.get("master_id") or n.get("parceiro_id")) != parceiro_id or n.get("status") != "ganho" or n.get("cafe") or not n.get("fechado_em"):
            continue
        d = CAL.dia(n["fechado_em"])
        if d < ini:
            continue
        liq = min((n.get("valor_credito") or 0) * (n.get("honorario_pct") or 0), teto)
        vol += liq
        por_tri[_trimestre(d)] = por_tri.get(_trimestre(d), 0) + liq
    tris = sorted(por_tri)[-4:]
    est, av = pat["estrategico"], pat["avancado"]
    acima = lambda m: sum(1 for t in tris if por_tri[t] >= m)  # noqa: E731
    if vol >= est["sobe"] and acima(est["trimestre_min"]) >= est["trimestres_sobe"]:
        faixa, prox = "estrategico", None
    elif vol >= av["sobe"] and acima(av["trimestre_min"]) >= av["trimestres_sobe"]:
        faixa, prox = "avancado", est["sobe"]
    else:
        faixa, prox = "master", av["sobe"]
    return {"parceiro_id": parceiro_id, "trimestre": _trimestre(hoje), "estado": "apurado", "modo": app.param("nivel.modo"), "faixa_simulada": faixa,
            "volume_12m": round(vol, 2), "pct_do_proximo": round(100 * vol / prox, 1) if prox else 100.0, "trimestres": {t: round(por_tri[t], 2) for t in tris}}


def visao_parceiro(app, ator):
    par = app.repo.obter("parceiro", ator.parceiro_id) or {}
    etapa = par.get("etapa_jornada") or ("master" if par.get("tipo") == "master" else "registrado")
    passos = [{"titulo": ROTULO_JORNADA[j], "situacao": "feito" if JORNADA.index(j) < JORNADA.index(etapa) else "atual" if j == etapa else "futuro"} for j in JORNADA]
    out = {"modo": app.param("nivel.modo"), "selo": "Em teste", "aviso": "O programa de níveis está em definição. O que você vê aqui é uma simulação e pode mudar.",
           "jornada": passos, "etapa": ROTULO_JORNADA[etapa]}
    if ator.papel == "titular":  # P2-9: só a etapa de cada consultor, sem atividade nem dias sem indicar
        out["equipe"] = [{"nome": u.get("nome"), "etapa": ROTULO_JORNADA.get((app.repo.obter("parceiro", u.get("consultor_parceiro_id") or "") or {}).get("etapa_jornada") or "registrado")}
                         for u in app.repo.listar("usuario_parceiro", parceiro_id=ator.parceiro_id, papel="consultor")]
    return out


def visao_save(app):
    return [dict(apurar(app, p["parceiro_id"]), nome=p.get("nome_exibicao")) for p in app.repo.listar("parceiro", tipo="master")]
