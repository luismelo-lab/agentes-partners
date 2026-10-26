"""Módulo 3 · Extrato (02 §6). A linha nasce no prm_local.py (previsto / em conferência, sem recebido) e cada mudança
vira um movimento no ledger `extrato_movimento`: o estado atual é a linha gerada + os movimentos, nada é sobrescrito.

PRM-R14/R50 nenhuma linha passa de previsto sem recebimento registrado pelo Financeiro; PRM-R18 quem registra o
recebimento não aprova o extrato da mesma competência; PRM-R51 atípico fica em conferência; PRM-R53 percentual do
termo (o do card só para o incontroverso); PRM-R57 cada família numa seção; PRM-R58 conciliação ao centavo;
PRM-R59 nada de comissões internas; PRM-R65 a contestação não segura o resto; PRM-R67 fora da janela vira demanda.
DL-09: sem valor previsto antes do recebimento (extrato.mostra_valor_previsto = false).
"""
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from . import calendario as CAL
from . import notificacoes as NT
from .auditoria import auditar_saida, exigir_sem_dado_pessoal
from .erros import Conflito, Invalido, SemPermissao
from .identidade import exigir
from .maquinas import CONTESTACAO, EXTRATO
from .textos import texto as T

CHIP = {"previsto": "info", "recebido_pela_save": "info", "calculado": "info", "liberado": "acao", "aguardando_nf": "acao", "pago": "ok",
        "em_conferencia": "atencao", "retida_conflito": "atencao", "contestada": "atencao", "cancelada": "neutro"}
ROTULO = {"previsto": "Previsto", "recebido_pela_save": "Recebido pela Save", "calculado": "Recebido pela Save", "liberado": "Liberado · envie a NF",
          "aguardando_nf": "Liberado · envie a NF", "pago": "Pago", "em_conferencia": "Em conferência contratual", "retida_conflito": "Em conferência contratual",
          "contestada": "Contestada", "cancelada": "Cancelada"}
COM_VALOR = ("recebido_pela_save", "calculado", "liberado", "aguardando_nf", "contestada", "pago")


def reais(v):
    if v is None:
        return None
    s = "{:,.2f}".format(float(v)).replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + s


def centavo(x):
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def escritorio(app, linha):
    if linha.get("master_id"):
        return linha["master_id"]
    n = app.repo.obter("negocio", linha["deal_id"]) or {}
    return n.get("master_id") or n.get("parceiro_id") or linha.get("parceiro_id")


def atual(app, linha):
    """Linha gerada + movimentos do ledger, na ordem."""
    x = dict(linha)
    x["escritorio"] = escritorio(app, linha)
    for m in sorted(app.repo.listar("extrato_movimento", linha_id=linha["linha_id"]), key=lambda m: (m["quando"], m["movimento_id"])):
        x["estado"] = m.get("para") or x["estado"]
        x.update(m.get("valores") or {})
        x.setdefault("movimentos", []).append({"tipo": m["tipo"], "quando": m["quando"], "quem": m["quem"], "para": m.get("para")})
    return x


def linhas(app):
    return [atual(app, l) for l in app.repo.listar("extrato_linha")]


def _mover(app, x, para, tipo, ator, papel=None, **valores):
    papel = papel or ator.papel
    EXTRATO.exigir(x["estado"], para, papel)
    app.repo.inserir("extrato_movimento", {"linha_id": x["linha_id"], "deal_id": x["deal_id"], "tipo": tipo, "de": x["estado"], "para": para,
                                            "quando": app.agora_iso(), "quem": ator.rotulo() if ator else "sistema", "papel": papel, "valores": valores})
    return atual(app, app.repo.obter("extrato_linha", x["linha_id"]))


def _pct_termo(app, esc):
    t = next(iter(app.repo.listar("termo", parceiro_id=esc)), None)
    return (t or {}).get("percentual_recuperacao"), t


def _em_conflito(app, deal_id):
    n = app.repo.obter("negocio", deal_id) or {}
    raiz = n.get("cnpj_raiz_hmac")
    return bool(raiz) and any(c["estado"] == "aberto" for c in app.repo.listar("conflito", cnpj_raiz_hmac=raiz))


# ---------------------------------------------------------------- visão do parceiro (só o titular, PRM-R15)
def visao_parceiro(app, x, empresa=None):
    e = x["estado"]
    pct = x.get("percentual")
    comp = x.get("competencia_recebimento") or x.get("competencia")
    if e == "previsto":
        msg = T("EXT-previsto", pct=("%g" % round(pct * 100, 2)).replace(".", ",") if pct is not None else "a confirmar")
    elif e in ("em_conferencia", "retida_conflito"):
        msg = T("M-20") if e == "em_conferencia" else T("EXT-retida_conflito")
    elif e in ("recebido_pela_save", "calculado"):
        msg = T("EXT-recebido_pela_save", competencia=comp or "")
    elif e in ("liberado", "aguardando_nf"):
        msg = T("EXT-liberado", competencia=comp or "", valor_bruto=reais(x.get("valor_bruto")), valor_nf=reais(x.get("valor_bruto")),
                nf_limite=x.get("nf_limite") or "", dia_pagamento=x.get("dia_pagamento") or "")
    elif e == "contestada":
        msg = T("M-21", data=CAL.fmt_data(x.get("contestada_em")), data_resposta=CAL.fmt_data(x.get("resposta_ate")))
    elif e == "pago":
        msg = T("EXT-pago", data_pagamento=CAL.fmt_data(x.get("pago_em")), valor_liquido=reais(x.get("valor_liquido")), retencoes=x.get("retencoes_texto") or "")
    else:
        msg = T("EXT-cancelada")
    hoje = CAL.dia(app.agora())
    lim = x.get("contestacao_ate")
    pode_contestar = e in ("liberado", "aguardando_nf") and bool(lim) and hoje <= date.fromisoformat(lim[:10]) and not x.get("contestada_uma_vez")
    v = {"ref": app.ref_estavel("ext", x["linha_id"]), "estado": e, "rotulo": ROTULO.get(e, e), "chip": CHIP.get(e, "info"), "mensagem": msg,
         "familia": x.get("familia"), "competencia": comp, "empresa": empresa or "Empresa indicada", "pode_contestar": pode_contestar,
         "contestacao_ate": CAL.fmt_data(lim) if lim else None, "passos": _passos(e)}
    if e in COM_VALOR:  # valor só depois do recebimento (R5, DL-09)
        v["detalhe"] = {"base": reais(x.get("base_recebida")), "percentual": ("%g%%" % round((x.get("percentual_aplicado") or 0) * 100, 2)).replace(".", ","),
                        "bruto": reais(x.get("valor_bruto")), "retencoes": x.get("retencoes_lista") or [], "liquido": reais(x.get("valor_liquido")),
                        "nf": x.get("nf_numero")}
        v["valor"] = reais(x.get("valor_liquido") if e == "pago" else x.get("valor_bruto"))
    elif app.param("extrato.mostra_valor_previsto") and e == "previsto" and x.get("valor_previsto") is not None:
        v["valor_estimado"] = reais(x["valor_previsto"])
    return v


def _passos(e):
    ordem = [("previsto", "Previsto"), ("recebido_pela_save", "Recebido pela Save"), ("liberado", "Liberado"), ("pago", "Pago")]
    pos = {"previsto": 0, "recebido_pela_save": 1, "calculado": 1, "liberado": 2, "aguardando_nf": 2, "contestada": 2, "pago": 3}.get(e)
    return [{"titulo": t, "situacao": ("bloqueado" if pos is None and i == 0 else "futuro") if pos is None else ("feito" if i < pos else "atual" if i == pos else "futuro")}
            for i, (_, t) in enumerate(ordem)]


def do_titular(app, ator, nomes):
    exigir(ator, "ver_extrato", "O extrato do escritório fica com o titular.")
    ci = app.param("familia_ci_ativa")  # PRM-R11 / caso 18: família do Crédito Internacional desligada até o G2
    xs = [x for x in linhas(app) if x["escritorio"] == ator.parceiro_id and (ci or x.get("familia") != "credito_internacional")]
    vs = [visao_parceiro(app, x, nomes.get(x["deal_id"])) for x in xs]
    ano = str(CAL.dia(app.agora()).year)
    pago = sum(x.get("valor_liquido") or 0 for x in xs if x["estado"] == "pago" and str(x.get("pago_em", ""))[:4] == ano)
    liberado = sum(x.get("valor_bruto") or 0 for x in xs if x["estado"] in ("liberado", "aguardando_nf"))
    conf = sum(1 for x in xs if x["estado"] in ("em_conferencia", "retida_conflito"))
    return {"resumo": {"pago_no_ano": reais(pago), "liberado_aguardando_nf": reais(liberado), "em_conferencia_linhas": conf},
            "linhas": sorted(vs, key=lambda v: (v["estado"] not in ("liberado", "aguardando_nf"), v.get("competencia") or "")),
            "aviso_fonte": not any(x.get("base_recebida") for x in xs)}


# ---------------------------------------------------------------- Financeiro
def registrar_recebimento(app, ator, linha_id, valor, competencia, data_rec=None):
    exigir(ator, "registrar_recebimento")
    linha = app.repo.obter("extrato_linha", linha_id)
    if not linha:
        raise Invalido("Linha não encontrada.")
    x = atual(app, linha)
    try:
        valor = centavo(valor)
    except Exception:  # noqa: BLE001
        raise Invalido("Valor inválido.")
    if valor <= 0:
        raise Invalido("Valor inválido.")
    if not (isinstance(competencia, str) and len(competencia) == 7 and competencia[4] == "-"):
        raise Invalido("Competência no formato AAAA-MM.")
    if x["estado"] == "em_conferencia":
        raise Conflito("Linha em conferência contratual: só com o contrato conferido (PRM-R51).")
    val = {"base_recebida": valor, "competencia_recebimento": competencia, "recebido_em": data_rec or CAL.dia(app.agora()).isoformat(),
           "recebimento_por": ator.rotulo()}
    if _em_conflito(app, x["deal_id"]):
        return _mover(app, x, "retida_conflito", "recebimento", ator, "sistema", **val)
    return _mover(app, x, "recebido_pela_save", "recebimento", ator, **val)


def calcular(app, ator, competencia=None):
    """Cálculo do mês (5º d.u.): base recebida × percentual incontroverso (PRM-R53, R51). Arredonda por linha, meia para cima."""
    n = 0
    for x in linhas(app):
        if x["estado"] != "recebido_pela_save" or (competencia and x.get("competencia_recebimento") != competencia):
            continue
        pct_termo, termo = _pct_termo(app, x["escritorio"])
        pct_card = x.get("parceiro_pct_card")
        if pct_termo is None and pct_card is None:
            _mover(app, x, "em_conferencia", "calculo", ator, "sistema", motivo="sem percentual"); continue
        pct = pct_termo if pct_termo is not None else pct_card
        inc = min(pct, pct_card) if (pct_termo is not None and pct_card is not None and abs(pct_termo - pct_card) > 1e-9) else pct
        if x.get("familia") == "produtos_2027":
            inc = app.param("extrato.pct_produtos_2027") / 100.0
        b, dp, di = Decimal(str(x["base_recebida"])), Decimal(str(pct)), Decimal(str(inc))
        bruto = centavo(b * di)
        exced = centavo(b * (dp - di)) if dp > di else 0
        _mover(app, x, "calculado", "calculo", ator, "sistema", percentual_aplicado=inc, valor_bruto=bruto, excedente_em_conferencia=exced,
               termo_selo=None if (termo or {}).get("vigencia_ini") else "termo a localizar")
        n += 1
    return n


def lotes(app):
    """Lotes por escritório e competência para a tela Extratos a liberar (S-7), com o checklist de elegibilidade (6.5)."""
    grupos = {}
    for x in linhas(app):
        if x["estado"] in ("calculado", "liberado", "aguardando_nf", "em_conferencia", "recebido_pela_save", "retida_conflito", "contestada"):
            k = (x["escritorio"], x.get("competencia_recebimento") or x.get("competencia") or "—")
            grupos.setdefault(k, []).append(x)
    out = []
    for (esc, comp), xs in sorted(grupos.items()):
        if not any(x["estado"] in ("calculado", "liberado", "aguardando_nf", "recebido_pela_save", "contestada", "retida_conflito") for x in xs):
            continue  # só conferência: não é lote (aparece na lista de linhas)
        par = app.repo.obter("parceiro", esc) or {}
        _, termo = _pct_termo(app, esc)
        calc = [x for x in xs if x["estado"] == "calculado"]
        check = [
            {"item": "Termo vigente", "ok": bool(termo), "texto": "ok" if termo and termo.get("vigencia_ini") else ("termo a localizar (segue com selo)" if termo else "sem termo")},
            {"item": "CNPJ do parceiro ativo", "ok": par.get("cnpj_situacao", "ativa") == "ativa", "texto": par.get("cnpj_situacao", "ativa")},
            {"item": "Sem conflito aberto", "ok": not any(x["estado"] == "retida_conflito" for x in xs), "texto": "linhas retidas: %d" % sum(1 for x in xs if x["estado"] == "retida_conflito")},
            {"item": "Fora de conferência", "ok": True, "texto": "%d linha(s) em conferência ficam fora do lote" % sum(1 for x in xs if x["estado"] == "em_conferencia")},
            {"item": "Conciliação ao centavo", "ok": abs(sum(x.get("valor_bruto") or 0 for x in calc) - sum(centavo((x.get("base_recebida") or 0) * (x.get("percentual_aplicado") or 0)) for x in calc)) <= app.param("extrato.tolerancia_conciliacao"), "texto": "detalhe = resumo"},
        ]
        motivo = None if calc else "Nenhuma linha calculada neste lote."
        if calc and not all(c["ok"] for c in check):
            motivo = "Pendência no checklist: " + ", ".join(c["item"] for c in check if not c["ok"])
        out.append({"lote": "%s|%s" % (esc, comp), "parceiro_id": esc, "parceiro": par.get("nome_exibicao"), "competencia": comp, "linhas": len(xs),
                    "calculadas": len(calc), "bruto": reais(sum(x.get("valor_bruto") or 0 for x in calc)), "checklist": check, "pode_liberar": motivo is None,
                    "motivo_bloqueio": motivo, "liberadas": sum(1 for x in xs if x["estado"] in ("liberado", "aguardando_nf"))})
    return out


def liberar_lote(app, ator, lote_id):
    exigir(ator, "aprovar_extrato")
    esc, _, comp = str(lote_id).partition("|")
    lt = next((l for l in lotes(app) if l["lote"] == lote_id), None)
    if not lt:
        raise Invalido("Lote não encontrado.")
    if not lt["pode_liberar"]:
        raise Conflito(lt["motivo_bloqueio"])
    xs = [x for x in linhas(app) if x["escritorio"] == esc and x["estado"] == "calculado" and (x.get("competencia_recebimento") or x.get("competencia")) == comp]
    if any(x.get("recebimento_por") == ator.rotulo() for x in xs):
        raise SemPermissao("Segregação (PRM-R18): quem registrou o recebimento não aprova o extrato da mesma competência.")
    hoje = app.agora()
    lim = app.cal.prazo_corridos(hoje, app.param("extrato.contestacao_dias")).date().isoformat()
    for x in xs:
        x = _mover(app, x, "liberado", "liberacao", ator, publicado_em=app.agora_iso(), contestacao_ate=lim, nf_limite=str(app.param("extrato.nf_limite_dia")),
                   dia_pagamento=str(app.param("extrato.pagamento_dia")), aprovado_por=ator.rotulo())
        _mover(app, x, "aguardando_nf", "publicacao", None, "sistema")
    for u in NT.titulares(app, esc):
        NT.avisar_usuario(app, u, "M-21a", "extrato", "extrato", chave="M-21a|%s" % lote_id, competencia=comp, data_limite_contestacao=CAL.fmt_data(lim))
    return len(xs)


def registrar_pagamento(app, ator, linha_id, nf_numero):
    exigir(ator, "aprovar_extrato")
    x = atual(app, app.repo.obter("extrato_linha", linha_id) or {"linha_id": linha_id, "deal_id": None, "estado": "?"})
    if x["estado"] != "aguardando_nf":
        raise Conflito("A linha não está aguardando NF.")
    if not str(nf_numero or "").strip():
        raise Invalido("Informe o número da NF.")
    bruto = x["valor_bruto"]
    if CAL.dia(app.agora()) >= date(2027, 1, 1) and app.param("retencao.regra_2027") == "a_validar":
        raise Conflito("Retenções de 2027 em validação pelo Tributário: pagamento bloqueado até a regra ser validada.")
    irrf = centavo(bruto * app.param("retencao.irrf_pct") / 100)
    ret = [{"nome": "Imposto de Renda retido (IRRF)", "valor": reais(irrf)}]
    liq = centavo(bruto - irrf)
    x = _mover(app, x, "pago", "pagamento", ator, nf_numero=str(nf_numero)[:20], pago_em=CAL.dia(app.agora()).isoformat(), valor_liquido=liq,
               retencoes_lista=ret, retencoes_texto="; ".join("%s %s" % (r["nome"], r["valor"]) for r in ret))
    for u in NT.titulares(app, x["escritorio"]):
        NT.avisar_usuario(app, u, "M-25", "extrato", "extrato", chave="M-25|" + linha_id, competencia=x.get("competencia_recebimento") or "",
                          data_pagamento=CAL.fmt_data(x["pago_em"]), valor_liquido=reais(liq), retencoes=x["retencoes_texto"])
    return x


# ---------------------------------------------------------------- contestação (6.6)
def contestar(app, ator, x, motivo):
    exigir(ator, "contestar_linha")
    motivo = " ".join(str(motivo or "").split())
    exigir_sem_dado_pessoal({"motivo": motivo})
    if not 10 <= len(motivo) <= 800:
        raise Invalido("Explique o que não bate (de 10 a 800 caracteres).", campos={"motivo": "Explique o que não bate."})
    v = visao_parceiro(app, x)
    if not v["pode_contestar"]:
        from . import demandas as DM  # PRM-R67: fora da janela vira demanda de remuneração, sem efeito no ciclo
        d = DM.abrir(app, ator, {"tipo": "remuneracao", "texto": "Contestação fora da janela: " + motivo})
        return {"fora_da_janela": True, "demanda": d}
    agora = app.agora()
    resp = app.cal.prazo_du(agora, app.param("extrato.resposta_contestacao_du"))
    c = {"contestacao_id": app.novo_id("CT", 4), "ref": app.ref(), "linha_id": x["linha_id"], "parceiro_id": x["escritorio"], "usuario_id": ator.usuario_id,
         "motivo": motivo, "estado": "em_analise", "aberta_em": app.agora_iso(), "resposta_ate": resp.isoformat(), "dono_tipo": "calculo"}
    app.repo.inserir("contestacao", c)
    _mover(app, x, "contestada", "contestacao", ator, contestada_em=app.agora_iso(), resposta_ate=resp.isoformat(), contestacao_id=c["contestacao_id"],
           contestada_uma_vez=True)
    NT.avisar_usuario(app, ator.usuario_id, "M-21", "extrato", "extrato", chave="M-21|" + c["contestacao_id"], data=CAL.fmt_data(agora), data_resposta=CAL.fmt_data(resp))
    NT.alertar_save(app, "financeiro", "Contestação de extrato: %s" % c["contestacao_id"], "Responder até %s." % CAL.fmt(resp), tipo="pedido",
                    chave="contest|" + c["contestacao_id"])
    return {"fora_da_janela": False, "contestacao_id": c["contestacao_id"], "mensagem": T("M-21", data=CAL.fmt_data(agora), data_resposta=CAL.fmt_data(resp))}


def responder_contestacao(app, ator, c, procedente, explicacao, causa_raiz):
    exigir(ator, "responder_contestacao")
    if causa_raiz not in ("cadastro", "percentual", "duplicidade", "recebimento", "retencao", "conflito"):
        raise Invalido("Escolha a causa-raiz (PRM-R66).")
    explicacao = " ".join(str(explicacao or "").split())
    ok, motivos = auditar_saida(explicacao)
    if not ok:
        raise Invalido("O texto não pode sair assim: " + "; ".join(motivos), codigo="auditor")
    para = "procedente" if procedente else "improcedente"
    CONTESTACAO.exigir(c["estado"], para, ator.papel)
    linha = atual(app, app.repo.obter("extrato_linha", c["linha_id"]))
    if procedente and (linha.get("valor_bruto") or 0) > app.param("extrato.contestacao_aprovacao_humana_acima") and ator.papel != "financeiro":
        raise SemPermissao("Procedente acima de %s exige a aprovação do Financeiro (PRM-R66)." % reais(app.param("extrato.contestacao_aprovacao_humana_acima")))
    c = app.repo.atualizar("contestacao", c["contestacao_id"], {"estado": para, "respondida_em": app.agora_iso(), "respondida_por": ator.rotulo(),
                                                                "explicacao": explicacao, "causa_raiz": causa_raiz})
    x = atual(app, app.repo.obter("extrato_linha", c["linha_id"]))
    if x["estado"] == "contestada":
        _mover(app, x, "aguardando_nf", "resposta_contestacao", ator)
    hoje = app.agora()
    if procedente:
        nxt = (CAL.dia(hoje).replace(day=1) + timedelta(days=32)).strftime("%Y-%m")
        msg = T("M-22-procedente", explicacao=explicacao, competencia_seguinte=nxt)
    else:
        msg = T("M-22-improcedente", explicacao=explicacao, data_limite=CAL.fmt_data(app.cal.prazo_corridos(hoje, app.param("extrato.contestacao_dias"))))
    NT._gravar(app, "usuario:" + c["usuario_id"], "Resposta à contestação", msg, "extrato", "prm", "extrato", chave="M-22|" + c["contestacao_id"], codigo="M-22",
               auditoria="auditado")
    return c
