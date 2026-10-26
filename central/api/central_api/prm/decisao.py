"""Ação única `decidir` (U4): os cinco botões de aprovar da Central (esteira, chamado, pedido, registro, extrato) viram
uma rota com identidade (oid do Entra), papel e trilha. Cada decisão grava uma linha no ledger `decisao` com quem,
papel, quando, estado antes e depois e o resultado padronizado (aprovado · nao_aprovado · nova_analise · recusado).

Corpo: {"objeto": "...", "id": "...", "decisao": "...", ...campos da decisão}
"""
from .. import esteira
from . import demandas as DM
from . import extrato as EX
from . import negocios as NG
from . import registro as RG
from .erros import Conflito, Invalido, NaoEncontrado
from .identidade import exigir
from .maquinas import USUARIO

# (objeto, decisão) → (ação exigida, resultado padronizado)
DECISOES = {
    ("registro", "aprovar"): ("decidir_registro", "aprovado"),
    ("registro", "nao_aprovar"): ("decidir_registro", "nao_aprovado"),
    ("registro", "enviar_conflito"): ("enviar_conflito", "nova_analise"),
    ("registro", "pedir_complemento"): ("decidir_registro", "nova_analise"),
    ("registro", "prorrogar"): ("decidir_prorrogacao", "aprovado"),
    ("registro", "negar_prorrogacao"): ("decidir_prorrogacao", "nao_aprovado"),
    ("conflito", "decidir"): ("decidir_conflito", "aprovado"),
    ("demanda", "aprovar_envio"): ("responder_demanda", "aprovado"),
    ("demanda", "encaminhar"): ("aprovar_chamado", "aprovado"),
    ("demanda", "recusar_chamado"): ("aprovar_chamado", "recusado"),
    ("demanda", "pedir_dados"): ("responder_demanda", "nova_analise"),
    ("extrato_lote", "liberar"): ("aprovar_extrato", "aprovado"),
    ("extrato_linha", "registrar_recebimento"): ("registrar_recebimento", "aprovado"),
    ("extrato_linha", "registrar_pagamento"): ("aprovar_extrato", "aprovado"),
    ("extrato", "calcular"): ("registrar_recebimento", "aprovado"),
    ("contestacao", "procedente"): ("responder_contestacao", "aprovado"),
    ("contestacao", "improcedente"): ("responder_contestacao", "nao_aprovado"),
    ("dossie", "aprovar"): ("aprovar_dossie", "aprovado"),
    ("usuario", "suspender"): ("gerir_acessos", "recusado"),
    ("usuario", "reativar"): ("gerir_acessos", "aprovado"),
    ("usuario", "desativar"): ("gerir_acessos", "recusado"),
    ("pendencia", "abrir"): ("marcar_pendencia", "aprovado"),
    ("pendencia", "resolver"): ("marcar_pendencia", "aprovado"),
    ("parametro", "alterar"): ("mudar_parametro", "aprovado"),
}


def _obter(app, tabela, ident):
    x = app.repo.obter(tabela, ident)
    if x is None:
        raise NaoEncontrado()
    return x


def decidir(app, ator, c):
    obj, dec, ident = c.get("objeto"), c.get("decisao"), str(c.get("id") or "")
    if (obj, dec) not in DECISOES:
        raise Invalido("Decisão desconhecida.")
    acao, padrao = DECISOES[(obj, dec)]
    exigir(ator, acao)
    motivo_int = str(c.get("motivo_interno") or "")[:400] or None
    antes = depois = None
    if obj == "registro":
        r = _obter(app, "registro", ident); antes = r["estado"]
        if dec == "aprovar":
            r = RG.aprovar(app, ator, r, mesmo_parceiro_cadastro_incompleto=c.get("mesmo_parceiro_cadastro_incompleto") is True)
        elif dec == "nao_aprovar":
            r = RG.recusar(app, ator, r, c.get("motivo", 4), campos=c.get("campos"))
        elif dec == "enviar_conflito":
            r, _ = RG.enviar_conflito(app, ator, r, nota=motivo_int)
        elif dec == "pedir_complemento":
            r = RG.pedir_complemento(app, ator, r, c.get("pergunta"))
        else:
            r = RG.decidir_prorrogacao(app, ator, r, dec == "prorrogar")
        depois, saida = r["estado"], RG.visao_save(app, r)
    elif obj == "conflito":
        k = _obter(app, "conflito", ident); antes = k["estado"]
        k = RG.decidir_conflito(app, ator, k, vencedor=c.get("vencedor"), decisao=c.get("tipo_decisao") or "primeiro_registro", nota=motivo_int)
        depois, saida = k["estado"], k
    elif obj == "demanda":
        d = _obter(app, "demanda", ident); antes = d["estado"]
        if dec == "aprovar_envio":
            d = DM.responder(app, ator, d, c.get("texto"), origem="historico" if d["estado"] == "resposta_historico" and not c.get("editada") else "area")
        elif dec == "encaminhar":
            d = DM.encaminhar(app, ator, d, c.get("titulo"), c.get("descricao"))
        elif dec == "recusar_chamado":
            d = DM.recusar_chamado(app, ator, d, c.get("motivo"))
        else:
            d = DM.pedir_dados(app, ator, d, c.get("itens"))
        depois, saida = d["estado"], DM.visao_save(app, d)
    elif obj == "extrato_lote":
        n = EX.liberar_lote(app, ator, ident)
        antes, depois, saida = "calculado", "liberado", {"linhas_liberadas": n}
    elif obj == "extrato_linha":
        linha = _obter(app, "extrato_linha", ident); antes = EX.atual(app, linha)["estado"]
        if dec == "registrar_recebimento":
            x = EX.registrar_recebimento(app, ator, ident, c.get("valor"), c.get("competencia"))
        else:
            x = EX.registrar_pagamento(app, ator, ident, c.get("nf"))
        depois, saida = x["estado"], {"linha_id": ident, "estado": x["estado"]}
    elif obj == "extrato":
        n = EX.calcular(app, ator, c.get("competencia"))
        saida = {"calculadas": n}
    elif obj == "contestacao":
        k = _obter(app, "contestacao", ident); antes = k["estado"]
        k = EX.responder_contestacao(app, ator, k, dec == "procedente", c.get("explicacao"), c.get("causa_raiz"))
        depois, saida = k["estado"], k
    elif obj == "dossie":
        try:
            p = esteira.aprovar(ident, "%s (%s)" % (ator.nome or ator.papel, ator.rotulo()))
        except esteira.Recusa as e:
            raise Conflito(str(e))
        antes, depois, saida = "aguardando_aprovacao", p["status"], {"id": p["id"], "status": p["status"]}
    elif obj == "usuario":
        u = _obter(app, "usuario_parceiro", ident); antes = u["estado"]
        para = {"suspender": "suspenso", "reativar": "ativo", "desativar": "desativado"}[dec]
        USUARIO.exigir(u["estado"], para, ator.papel)
        u = app.repo.atualizar("usuario_parceiro", ident, {"estado": para, "estado_em": app.agora_iso(), "estado_motivo": motivo_int})
        depois, saida = para, {"usuario_id": ident, "estado": para}
    elif obj == "pendencia":
        if dec == "abrir":
            p = NG.marcar_pendencia(app, ator, ident, c.get("tipo"), c.get("texto"))
        else:
            p = NG.resolver_pendencia(app, ator, ident)
        saida, depois = p, ("aberta" if dec == "abrir" else "resolvida")
    else:
        valor = app.param.alterar(ident, c.get("valor"), ator, app.agora_iso())
        saida = {"chave": ident, "valor": valor}
    t = app.repo.inserir("decisao", {"objeto": obj, "objeto_id": ident, "decisao": dec, "resultado": padrao, "quem": ator.rotulo(), "oid": ator.oid,
                                     "papel": ator.papel, "quando": app.agora_iso(), "antes": antes, "depois": depois,
                                     "motivo_externo": c.get("motivo_externo"), "motivo_interno": motivo_int})
    app.acesso(ator, "decidir", "%s:%s" % (obj, dec), ident)
    return {"ok": True, "resultado": padrao, "trilha": t["decisao_id"], "objeto": saida}


def trilha(app, objeto=None, ident=None):
    xs = app.repo.listar("decisao", **({"objeto": objeto} if objeto else {}), **({"objeto_id": ident} if ident else {}))
    return sorted(xs, key=lambda x: x["quando"], reverse=True)
