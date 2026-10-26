"""Serviço único de notificação (U3), no formato que lib/caixa.py já usa no painel:
  {id, para, assunto, resumo, origem, tipo, prioridade, anexos, acoes: [{rotulo, go}], criado_em, lido_por: {}, auditoria}
Estendido para o parceiro: para = "usuario:U-0001". Os tipos do parceiro são os filtros da caixa de avisos (05 §3, P-8):
pede_voce · resposta · empresa · extrato · programa. Os da Save seguem a caixa: relatorio · alerta · pedido.

Texto ao parceiro só do catálogo (auditoria = "catalogo"); texto livre passa pelo auditor antes (quem chama).
Aviso na tela é imediato; o e-mail (Fase 2, DL-12) respeita a janela de 07h–20h de dia útil (`email_apos`).
Com PRM_ESPELHAR_CAIXA=1 o alerta interno também entra na fila do lib/caixa.py (painel do time), sem duplicar.
"""
import hashlib, os

from .auditoria import limpar
from .textos import texto as T

TIPOS_PARCEIRO = ("pede_voce", "resposta", "empresa", "extrato", "programa")
TIPOS_SAVE = ("relatorio", "alerta", "pedido")
PESSOAS_SAVE = ("luis", "daniela", "jenifer", "geovana", "financeiro", "contratos", "time")


def _id(para, chave):
    return "nt-" + hashlib.sha1(("%s|%s" % (para, chave)).encode()).hexdigest()[:16]


def _gravar(app, para, assunto, resumo, tipo, origem, go=None, prioridade="normal", chave=None, codigo=None, auditoria="catalogo", rotulo="Abrir"):
    agora = app.agora()
    i = _id(para, chave or "%s|%s|%s" % (assunto, resumo[:200], app.agora_iso()[:16]))
    if app.repo.obter("notificacao", i):
        return i  # idempotente: o mesmo aviso não entra duas vezes
    app.repo.gravar("notificacao", {
        "id": i, "para": para, "assunto": assunto[:160], "resumo": resumo[:1500], "origem": origem, "tipo": tipo, "prioridade": prioridade,
        "anexos": [], "acoes": [{"rotulo": rotulo, "go": go}] if go else [], "criado_em": app.agora_iso(), "lido_por": {},
        "auditoria": auditoria, "codigo": codigo, "email_apos": app.cal.janela_envio(agora).isoformat()})
    return i


def avisar_usuario(app, usuario_id, codigo, tipo_aviso="empresa", go=None, chave=None, assunto=None, **vars_):
    """Aviso ao usuário do parceiro com o texto do catálogo (as variáveis do texto vão em **vars_)."""
    resumo = T(codigo, **vars_)
    return _gravar(app, "usuario:" + usuario_id, assunto or resumo.split(". ")[0][:120], resumo, tipo_aviso, "prm", go,
                   chave=(chave or codigo) + "|" + usuario_id, codigo=codigo)


def titulares(app, parceiro_id):
    return [u["usuario_id"] for u in app.repo.listar("usuario_parceiro", parceiro_id=parceiro_id, papel="titular") if u.get("estado") == "ativo"]


def avisar_registro(app, reg, codigo, tipo="empresa", com_titular=True, chave=None, **vars_):
    """Quem registrou e, quando a tabela 02 §13 manda, o titular do escritório."""
    alvo = [reg["usuario_id"]] if reg.get("usuario_id") else []
    if com_titular:
        alvo += [u for u in titulares(app, reg["parceiro_id"]) if u not in alvo]
    go = "empresas/" + reg["ref"]
    return [avisar_usuario(app, u, codigo, tipo, go, chave=(chave or codigo) + "|" + reg["registro_id"], **vars_) for u in alvo]


def alertar_save(app, para, assunto, resumo, tipo="alerta", go=None, prioridade="normal", chave=None, origem="prm"):
    """Alerta interno (caixa do painel). Texto interno, limpo de telefone/CPF/CNPJ sem pontuação (lib/protecao)."""
    para = para if para in PESSOAS_SAVE else "time"
    i = _gravar(app, para, limpar(assunto), limpar(resumo), tipo if tipo in TIPOS_SAVE else "alerta", origem, go, prioridade,
                chave=chave, auditoria="interno")
    if os.environ.get("PRM_ESPELHAR_CAIXA") == "1" and para in ("luis", "daniela", "jenifer", "geovana", "time"):
        try:
            import caixa  # lib/caixa.py (painel do Artifact enquanto a Fase 2 não chega)
            caixa.enviar(para, assunto, resumo, origem="prm", prioridade=prioridade, tipo=tipo if tipo in TIPOS_SAVE else "alerta")
        except Exception:  # noqa: BLE001
            pass
    return i


def do_ator(app, ator):
    if ator.tipo == "parceiro":
        alvo = {"usuario:" + ator.usuario_id}
    else:
        alvo = {ator.papel, "time"}
    xs = [n for n in app.repo.listar("notificacao") if n["para"] in alvo]
    chave = ator.rotulo()
    for n in xs:
        n["lido"] = chave in (n.get("lido_por") or {})
    return sorted(xs, key=lambda n: n["criado_em"], reverse=True)


def marcar_lidas(app, ator, ids=None):
    """Marca como lido só o que é do próprio ator (ninguém marca aviso de outro)."""
    meus = {n["id"]: n for n in do_ator(app, ator)}
    alvo = meus.keys() if ids is None else [i for i in ids if i in meus]
    n = 0
    for i in alvo:
        x = app.repo.obter("notificacao", i)
        if ator.rotulo() not in x["lido_por"]:
            x["lido_por"][ator.rotulo()] = app.agora_iso()
            app.repo.gravar("notificacao", x); n += 1
    return n
