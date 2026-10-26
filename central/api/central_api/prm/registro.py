"""Módulo 1 · Registro de oportunidade (02 §4): formulário, checagem na entrada, máquina de estados, rotina diária.

Pontos de regra que este arquivo garante:
  PRM-R20 registro válido = todos os obrigatórios; PRM-R21 livre, outro canal, cliente da Save, índice ausente e teto
  recebem o MESMO texto (M-01), o MESMO corpo de resposta e o MESMO tempo mínimo (registro.piso_resposta_ms);
  PRM-R22 a unidade é a raiz; PRM-R23 recusa por outro parceiro ou cliente da Save só com o motivo 4;
  PRM-R25 o carimbo é a hora do envio completo; PRM-R26 validade 120/90 + 1 prorrogação de 60;
  PRM-R27 nenhuma decisão antes de registro.resposta_minima_horas úteis; PRM-R29 aprovado → tarefa de card à Daniela;
  PRM-R30 conflito é do Luis; PRM-R38 validade pausada em conflito e devolvida a quem vence; R06/R75 M-90.
"""
import re, time
from datetime import date, timedelta

from . import calendario as CAL
from . import checagem as CHK
from . import notificacoes as NT
from .auditoria import exigir_sem_dado_pessoal
from .erros import Conflito, Invalido, SemPermissao
from .identidade import exigir
from .maquinas import REGISTRO
from .textos import texto as T

INTERESSES = {
    "recuperacao": "Recuperação tributária (PIS/COFINS e outras teses)",
    "recorrencia": "Recorrência das novas competências",
    "passivo": "Gestão de Passivo (transação, CND, dívida ativa)",
    "juridico": "Produtos jurídicos",
    "planejamento": "Planejamento tributário e reforma",
    "patrimonial": "Estruturação patrimonial e sucessória",
    "gestao_contas": "Gestão de Contas e cobrança (Save Invest)",
    "antecipacao": "Antecipação de recebíveis e FIDC (Save Invest)",
    "tax_internacional": "Tax internacional e comércio exterior",
    "nao_sei": "Ainda não sei",
    "descoberta": "Outro tema (em descoberta)",
}
COMO_CONHECE = {"cliente_escritorio": "Cliente do meu escritório", "relacionamento": "Relacionamento comercial",
                "indicacao_terceiro": "Indicação de terceiro", "outro": "Outro"}
EVIDENCIAS = {"declaracao": "Declaração de relacionamento", "reuniao": "Reunião marcada", "documento": "Documento recebido",
              "procuracao": "Procuração ou e-CAC"}
MOTIVOS = {1: "MOTIVO-1", 2: "MOTIVO-2", 3: "MOTIVO-3", 4: "MOTIVO-4"}
FINAIS = REGISTRO.finais
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


# ---------------------------------------------------------------- texto e chip que o parceiro vê (05 §4.3)
def _limite(r):
    return r.get("prorrogado_ate") or r.get("valido_ate")


def visao_parceiro(app, r):
    """O que o parceiro vê de um registro. Nunca leva checagem_resultado, motivo interno nem flags (PRM-R21)."""
    e = r["estado"]
    hoje = CAL.dia(app.agora())
    lim = _limite(r)
    dias = (date.fromisoformat(lim) - hoje).days if lim else None
    if e in ("em_analise", "em_conflito"):
        chip, rot = "neutro", T("REG-recebido-titulo")
        msg = T("M-04") if r.get("aviso_demora_em") else T("M-01", carimbo=CAL.fmt(r["carimbo"]))
    elif e == "aguardando_parceiro":
        chip, rot = "acao", "Precisa de você"
        msg = T("M-02", pergunta=r.get("pergunta") or "", data_limite=CAL.fmt_data(r.get("complemento_ate")))
    elif e in ("aprovado", "prorrogado", "convertido"):
        vence = dias is not None and dias <= 15
        chip = "atencao" if vence else "ok"
        rot = ("Vence em %d dias" % dias) if vence else ("Aprovado · válido até %s" % CAL.fmt_data(lim))
        if e == "convertido":
            rot, msg = ("Virou negócio" if not vence else rot), T("M-06", valido_ate=CAL.fmt_data(lim))
        elif e == "prorrogado":
            msg = T("M-07", prorrogado_ate=CAL.fmt_data(lim))
        else:
            msg = T("M-05", valido_ate=CAL.fmt_data(lim))
    elif e == "protegido_cliente":
        chip, rot, msg = "ok", "Contrato assinado", T("M-08")
    elif e == "expirado":
        chip, rot, msg = "neutro", "Expirado", T("M-09", data=CAL.fmt_data(r.get("encerrado_em")))
    elif e == "encerrado_sem_contrato":
        chip, rot, msg = "neutro", "Encerrado", T("M-10", data=CAL.fmt_data(r.get("encerrado_em")))
    elif e == "recusado":
        chip, rot, msg = "neutro", "Não aprovado", T("M-11", motivo_externo=r.get("motivo_externo") or T("MOTIVO-4"))
    elif e == "cancelado":
        chip, rot, msg = "neutro", "Cancelado", T("REG-cancelado", data=CAL.fmt_data(r.get("encerrado_em")))
    elif e == "encerrado_fim_parceria":
        chip, rot, msg = "neutro", "Encerrado", T("M-12", data=CAL.fmt_data(r.get("encerrado_em")))
    else:
        chip, rot, msg = "neutro", "Rascunho", T("REG-rascunho")
    pode_prorrogar = (e in ("aprovado", "convertido") and dias is not None and dias <= 30 and r.get("prorrogacoes", 0) < app.param("registro.prorrogacoes_max")
                      and not r.get("pedido_prorrogacao"))
    return {"ref": r["ref"], "registro_id": r["registro_id"], "razao_social": r.get("razao_social"), "cnpj_mascara": r.get("cnpj_mascara"),
            "estado": "em_analise" if e == "em_conflito" else e, "rotulo": rot, "chip": chip, "mensagem": msg,
            "carimbo": CAL.fmt(r.get("carimbo")), "valido_ate": CAL.fmt_data(lim) if lim else None, "dias_para_vencer": dias,
            "interesse": INTERESSES.get(r.get("interesse"), r.get("interesse")), "pode_cancelar": e in ("aprovado", "convertido", "prorrogado"),
            "pode_prorrogar": pode_prorrogar, "aguarda_resposta": e == "aguardando_parceiro", "dossie_id": r.get("dossie_id"),
            "usuario_id": r.get("usuario_id"), "deal_ligado": bool(r.get("deal_id"))}


def visao_save(app, r):
    v = visao_parceiro(app, r)
    v.update({"estado": r["estado"], "checagem": r.get("checagem_resultado"), "flags": r.get("flags", []), "parceiro_id": r["parceiro_id"],
              "canal_entrada": r.get("canal_entrada"), "carimbo_origem": r.get("carimbo_origem"), "contato_cargo": r.get("contato_cargo"),
              "como_conhece": COMO_CONHECE.get(r.get("como_conhece")), "evidencia": EVIDENCIAS.get(r.get("evidencia_tipo")),
              "evidencia_nota": r.get("evidencia_nota"), "motivo_interno": r.get("motivo_interno"), "deal_id": r.get("deal_id"),
              "decidido_por": r.get("decidido_por"), "pode_decidir_em": r.get("pode_decidir_em"),
              "historico_raiz": CHK.historico_raiz(app, r["cnpj_raiz_hmac"]), "conflito_id": r.get("conflito_id"),
              "pedido_prorrogacao": r.get("pedido_prorrogacao")})
    if r["estado"] in ("em_analise", "em_conflito"):
        dias = _validade_dias(app, r["parceiro_id"]) + int(r.get("dias_pausados") or 0)
        v["valido_se_aprovar"] = CAL.fmt_data(CAL.dia(r["carimbo"]) + timedelta(days=dias))
    return v


# ---------------------------------------------------------------- trilha de estado (registro_evento, ledger)
def transitar(app, r, para, quem, papel, motivo_interno=None, motivo_externo=None, **mudar):
    REGISTRO.exigir(r["estado"], para, papel)
    de = r["estado"]
    mudar.update(estado=para, atualizado_em=app.agora_iso())
    if motivo_externo:
        mudar["motivo_externo"] = motivo_externo
    if para in FINAIS:
        mudar.setdefault("encerrado_em", app.agora_iso())
    r = app.repo.atualizar("registro", r["registro_id"], mudar)
    app.repo.inserir("registro_evento", {"registro_id": r["registro_id"], "quando": app.agora_iso(), "quem": quem, "papel": papel,
                                         "de_estado": de, "para_estado": para, "motivo_interno": motivo_interno, "motivo_externo": motivo_externo})
    return r


# ---------------------------------------------------------------- formulário (02 §4.1)
def validar(app, d, primeira_vez):
    erros, x = {}, {}
    c = app.cnpj(d.get("cnpj") or "")
    from cnpj import cnpj_valido
    if not cnpj_valido(c):
        erros["cnpj"] = "Este CNPJ não confere. Revise os números."
    x["cnpj"] = c
    for campo, minimo, maximo, msg in (("razao_social", 2, 160, "Informe a razão social."), ("contato_nome", 2, 120, "Informe o nome do decisor."),
                                       ("contato_cargo", 2, 60, "Informe o cargo do decisor.")):
        v = " ".join(str(d.get(campo) or "").split())
        if not (minimo <= len(v) <= maximo):
            erros[campo] = msg
        x[campo] = v
    email, tel = str(d.get("contato_email") or "").strip(), re.sub(r"\D", "", str(d.get("contato_tel") or ""))
    if not email and not tel:
        erros["contato_email"] = "Informe o e-mail corporativo ou o telefone da empresa."
    if email and not _EMAIL.match(email):
        erros["contato_email"] = "Confira o e-mail."
    if tel and not 10 <= len(tel) <= 11:
        erros["contato_tel"] = "Confira o telefone da empresa, com DDD."
    x["contato_email"], x["contato_tel"] = email or None, tel or None
    for campo, lista, msg in (("interesse", INTERESSES, "Escolha o tema de interesse."), ("como_conhece", COMO_CONHECE, "Diga como você conhece a empresa."),
                              ("evidencia_tipo", EVIDENCIAS, "Escolha a evidência da relação.")):
        v = d.get(campo)
        if v not in lista:
            erros[campo] = msg
        x[campo] = v
    if x.get("evidencia_tipo") == "reuniao":
        try:
            x["evidencia_data"] = date.fromisoformat(str(d.get("evidencia_data") or "")).isoformat()
        except ValueError:
            erros["evidencia_data"] = "Informe a data da reunião."
    nota = " ".join(str(d.get("evidencia_nota") or "").split())
    if len(nota) > 500:
        erros["evidencia_nota"] = "Use até 500 caracteres."
    x["evidencia_nota"] = nota or None
    if d.get("declaracao_lgpd") is not True:
        erros["declaracao_lgpd"] = "Confirme a declaração sobre o contato."
    if primeira_vez and d.get("declaracao_sem_promessa") is not True:
        erros["declaracao_sem_promessa"] = "Confirme que não prometeu valor, prazo ou resultado."
    return x, erros


def _validade_dias(app, parceiro_id):
    par = app.repo.obter("parceiro", parceiro_id) or {}
    return app.param("registro.validade_master_dias" if par.get("tipo") == "master" else "registro.validade_indicador_dias")


def _contexto(app, ator, em_nome_de):
    """(parceiro_id, usuario_id, canal) de quem registra. A Daniela registra em nome do parceiro (Fase 1, WhatsApp)."""
    if ator.tipo == "parceiro":
        exigir(ator, "registrar")
        par = app.repo.obter("parceiro", ator.parceiro_id) or {}
        if par.get("tipo") == "indicador" and not par.get("master_id"):
            raise SemPermissao("Para registrar empresas, seu termo de parceria precisa estar ativo. Fale com o time da Save que atende você.")
        return ator.parceiro_id, ator.usuario_id, "portal"
    exigir(ator, "registrar")
    em_nome_de = em_nome_de or {}
    par = app.repo.obter("parceiro", em_nome_de.get("parceiro_id") or "")
    if not par:
        raise Invalido("Escolha o parceiro em nome de quem o registro é feito.", campos={"parceiro_id": "Escolha o parceiro."})
    u = em_nome_de.get("usuario_id")
    if u and not (app.repo.obter("usuario_parceiro", u) or {}).get("parceiro_id") == par["parceiro_id"]:
        raise Invalido("Usuário de outro escritório.")
    return par["parceiro_id"], u, "bdr" if ator.papel == "jenifer" else "whatsapp"


def _esperar_piso(app, inicio):
    falta = app.param("registro.piso_resposta_ms") / 1000.0 - (time.monotonic() - inicio)
    if falta > 0:
        time.sleep(falta)


def _resposta_recebido(app, r):
    """Corpo único para todo resultado que não é do próprio parceiro (PRM-R21): só id, carimbo e o texto M-01."""
    return {"resultado": "recebido", "titulo": T("REG-recebido-titulo"), "mensagem": T("M-01", carimbo=CAL.fmt(r["carimbo"])),
            "registro": {"ref": r["ref"], "registro_id": r["registro_id"], "carimbo": CAL.fmt(r["carimbo"])}}


def registrar(app, ator, dados, em_nome_de=None):
    """Envio do formulário (02 §4.2). Devolve (status, corpo). Mesmo piso de tempo para todo resultado."""
    inicio = time.monotonic()
    try:
        return _registrar(app, ator, dados or {}, em_nome_de)
    finally:
        _esperar_piso(app, inicio)


def _registrar(app, ator, d, em_nome_de):
    parceiro_id, usuario_id, canal = _contexto(app, ator, em_nome_de)
    usuario = app.repo.obter("usuario_parceiro", usuario_id) if usuario_id else None
    chave_idem = str(d.get("chave_idempotencia") or "")[:64] or None
    if chave_idem:  # reenvio (Q11): devolve o mesmo registro, com a mesma resposta
        for r in app.repo.listar("registro", parceiro_id=parceiro_id, chave_idempotencia=chave_idem):
            return 200, _resposta_recebido(app, r)
    primeira = bool(usuario) and not usuario.get("declarou_sem_promessa_em")
    x, erros = validar(app, d, primeira)
    exigir_sem_dado_pessoal({k: x.get(k) for k in ("razao_social", "contato_nome", "contato_cargo", "evidencia_nota")})
    if erros:
        raise Invalido("Revise os campos destacados.", campos=erros)
    hoje = CAL.dia(app.agora()).isoformat()
    flags = []
    if app.repo.contar("registro|%s|%s" % (usuario_id or ator.rotulo(), hoje)) > app.param("registro.teto_diario_usuario"):
        flags.append("teto")
    chk = CHK.classificar(app, x["cnpj"], parceiro_id, usuario_id)
    res = chk["resultado"]
    if not flags and res in ("proprio_usuario", "proprio_escritorio"):
        return 200, _resposta_propria(app, chk)
    if res in ("outro_parceiro", "cliente_save") or "teto" in flags:
        _contar_neutra(app, ator, usuario_id, hoje)
    reg = {
        "registro_id": app.novo_id("R"), "ref": app.ref(), "chave_idempotencia": chave_idem, "parceiro_id": parceiro_id, "usuario_id": usuario_id,
        "master_id": (app.repo.obter("parceiro", parceiro_id) or {}).get("master_id"), "canal_entrada": canal,
        "carimbo_origem": "portal" if canal == "portal" else canal, "cnpj": x["cnpj"], "cnpj_raiz_hmac": app.hmac_raiz(x["cnpj"]),
        "cnpj_hmac": app.hmac_cnpj(x["cnpj"]), "cnpj_mascara": app.mascara(x["cnpj"]), "razao_social": x["razao_social"],
        "contato_nome": x["contato_nome"], "contato_cargo": x["contato_cargo"], "contato_email": x["contato_email"], "contato_tel": x["contato_tel"],
        "interesse": x["interesse"], "como_conhece": x["como_conhece"], "evidencia_tipo": x["evidencia_tipo"], "evidencia_data": x.get("evidencia_data"),
        "evidencia_nota": x["evidencia_nota"], "estado": "em_analise", "checagem_resultado": res, "flags": flags,
        "carimbo": app.agora_iso() if canal == "portal" or not d.get("carimbo_whatsapp") else CAL.iso(CAL.ler(d["carimbo_whatsapp"])),
        "criado_em": app.agora_iso(), "prorrogacoes": 0, "dias_pausados": 0, "avisos": [],
        "registrado_por": ator.rotulo(), "origem": "bdr" if canal == "bdr" else canal,
    }
    reg["pode_decidir_em"] = CAL.iso(app.cal.somar_horas_uteis(CAL.ler(reg["carimbo"]), app.param("registro.resposta_minima_horas")))
    reg["decidir_ate"] = app.cal.prazo_du(CAL.ler(reg["carimbo"]), app.param("registro.sla_decisao_du")).isoformat()
    app.repo.inserir("registro", reg)
    app.repo.inserir("registro_evento", {"registro_id": reg["registro_id"], "quando": reg["criado_em"], "quem": ator.rotulo(), "papel": ator.papel,
                                         "de_estado": None, "para_estado": "em_analise", "motivo_interno": "checagem=%s%s" % (res, " teto" if flags else ""),
                                         "motivo_externo": None})
    if usuario and primeira and d.get("declaracao_sem_promessa") is True:
        app.repo.atualizar("usuario_parceiro", usuario_id, {"declarou_sem_promessa_em": app.agora_iso()})
    if usuario_id:
        NT.avisar_usuario(app, usuario_id, "M-01", "empresa", "empresas/" + reg["ref"], chave="M-01|" + reg["registro_id"], carimbo=CAL.fmt(reg["carimbo"]))
    NT.alertar_save(app, "daniela", "Registro novo na fila: %s" % reg["registro_id"],
                    "Registro %s de %s, checagem %s. Decidir até %s (não antes de %s)." % (
                        reg["registro_id"], parceiro_id, res, CAL.fmt(reg["decidir_ate"]), CAL.fmt(reg["pode_decidir_em"])),
                    tipo="pedido", go="canal/registros/" + reg["registro_id"], chave="fila|" + reg["registro_id"])
    if "teto" in flags:
        NT.alertar_save(app, "daniela", "Possível varredura: teto diário de registros", "O usuário %s passou o teto de registros do dia." % (usuario_id or ator.rotulo()),
                        prioridade="alta", chave="teto-registro|%s|%s" % (usuario_id, hoje))
    return 201, _resposta_recebido(app, reg)


def _resposta_propria(app, chk):
    r, n = chk["registro"], chk["negocio"]
    if r:
        lim = _limite(r)
        if chk["resultado"] == "proprio_usuario":
            msg = T("M-03a", data=CAL.fmt_data(r["carimbo"]), valido_ate=CAL.fmt_data(lim) if lim else "a decisão da Área Partners")
        else:
            u = app.repo.obter("usuario_parceiro", r.get("usuario_id") or "") or {}
            msg = T("M-03b", data=CAL.fmt_data(r["carimbo"]), nome_consultor=u.get("nome") or "outra pessoa do escritório",
                    valido_ate=CAL.fmt_data(lim) if lim else "a decisão da Área Partners")
        return {"resultado": "ja_e_seu", "titulo": "Esta empresa já está com você", "mensagem": msg,
                "registro": {"ref": r["ref"], "registro_id": r["registro_id"], "estado": visao_parceiro(app, r)["rotulo"]}}
    return {"resultado": "ja_e_seu", "titulo": "Esta empresa já está com você", "mensagem": T("M-03c", data=CAL.fmt_data(n.get("criado_em"))),
            "negocio": {"ref": app.ref_estavel("neg", n["deal_id"])}}


def _contar_neutra(app, ator, usuario_id, hoje):
    """Anti-varredura persistente (L4): conta as respostas neutras do dia; passado o teto, alerta; reincidência suspende."""
    quem = usuario_id or ator.rotulo()
    n = app.repo.contar("neutra|%s|%s" % (quem, hoje))
    teto = app.param("registro.teto_neutros_dia_usuario")
    if n == teto + 1:
        NT.alertar_save(app, "daniela", "Possível varredura da carteira", "O usuário %s passou o teto de %d respostas neutras hoje." % (quem, teto),
                        prioridade="alta", chave="varredura|%s|%s" % (quem, hoje))
        NT.alertar_save(app, "luis", "Alerta de varredura (prm_varredura_suspeita)", "Usuário %s acima do teto de respostas neutras em %s." % (quem, CAL.fmt_data(hoje)),
                        prioridade="alta", chave="varredura-luis|%s|%s" % (quem, hoje))
        dias = app.repo.contar("reincidencia|%s" % quem)
        if usuario_id and dias >= app.param("registro.reincidencias_para_suspender"):
            u = app.repo.obter("usuario_parceiro", usuario_id)
            if u and u.get("estado") == "ativo":
                from .maquinas import USUARIO
                USUARIO.exigir("ativo", "suspenso", "sistema")
                app.repo.atualizar("usuario_parceiro", usuario_id, {"estado": "suspenso", "suspenso_em": app.agora_iso(), "suspenso_motivo": "varredura"})
                app.repo.inserir("decisao", {"objeto": "usuario", "objeto_id": usuario_id, "decisao": "suspenso", "quem": "sistema", "papel": "sistema",
                                             "quando": app.agora_iso(), "antes": "ativo", "depois": "suspenso", "motivo_interno": "reincidência acima do teto de neutras"})
    return n


# ---------------------------------------------------------------- decisões da Save (chamadas por decisao.decidir)
def _antes_do_minimo(app, r):
    return app.agora() < CAL.ler(r["pode_decidir_em"])


def aprovar(app, ator, r, mesmo_parceiro_cadastro_incompleto=False, conflito=False):
    if r["estado"] == "em_analise" and _antes_do_minimo(app, r):
        raise Conflito("A decisão só pode sair a partir de %s (tempo mínimo de análise)." % CAL.fmt(r["pode_decidir_em"]), codigo="cedo")
    if not conflito:
        if r.get("checagem_resultado") == "outro_parceiro":
            raise Conflito("Há registro ou negócio de outro parceiro nesta empresa: envie a conflito.", codigo="exige_conflito")
        if r.get("checagem_resultado") in ("cliente_save", "indice_ausente") and not mesmo_parceiro_cadastro_incompleto:
            raise Conflito("A empresa já tem negócio na Save. Só aprove se for do mesmo parceiro com cadastro incompleto (corrija pela higiene do CRM).",
                           codigo="cliente_save")
    dias = _validade_dias(app, r["parceiro_id"]) + int(r.get("dias_pausados") or 0)
    valido = (CAL.dia(r["carimbo"]) + timedelta(days=dias)).isoformat()
    r = transitar(app, r, "aprovado", ator.rotulo(), ator.papel, motivo_interno="aprovado" + (" (conflito decidido)" if conflito else ""),
                  valido_ate=valido, decidido_em=app.agora_iso(), decidido_por=ator.rotulo(), pausado_desde=None)
    NT.avisar_registro(app, r, "M-05", valido_ate=CAL.fmt_data(valido))
    NT.alertar_save(app, "daniela", "Criar card no HubSpot: %s" % r["registro_id"],
                    "Registro %s aprovado. Crie o card com o id do registro no campo id_registro_prm (o PRM não escreve no HubSpot)." % r["registro_id"],
                    tipo="pedido", go="canal/registros/" + r["registro_id"], chave="card|" + r["registro_id"])
    return r


def recusar(app, ator, r, motivo=4, campos=None, conflito=False, sistema=False):
    if not sistema and r["estado"] == "em_analise" and _antes_do_minimo(app, r):
        raise Conflito("A decisão só pode sair a partir de %s (tempo mínimo de análise)." % CAL.fmt(r["pode_decidir_em"]), codigo="cedo")
    try:
        motivo = int(motivo)
    except (TypeError, ValueError):
        raise Invalido("Escolha o motivo da lista.")
    if motivo not in MOTIVOS:
        raise Invalido("Escolha o motivo da lista.")
    if r.get("checagem_resultado") in ("outro_parceiro", "cliente_save") or conflito:
        motivo = 4  # PRM-R23: o único motivo permitido quando a recusa vem de outro parceiro ou de cliente da Save
    ext = T(MOTIVOS[motivo], campos=campos or "dados do formulário") if motivo == 1 else T(MOTIVOS[motivo])
    papel, quem = ("sistema", "sistema") if sistema else (ator.papel, ator.rotulo())
    r = transitar(app, r, "recusado", quem, papel, motivo_interno="motivo %d; checagem=%s" % (motivo, r.get("checagem_resultado")),
                  motivo_externo=ext, decidido_em=app.agora_iso(), decidido_por=quem)
    NT.avisar_registro(app, r, "M-11", motivo_externo=ext)
    return r


def enviar_conflito(app, ator, r, nota=None):
    agora = app.agora_iso()
    regs = [x for x in CHK.registros_vivos(app, r["cnpj_raiz_hmac"]) if x["registro_id"] != r["registro_id"]]
    negs = [n for n in app.repo.listar("negocio", cnpj_raiz_hmac=r["cnpj_raiz_hmac"]) if CHK.negocio_protege(app, n)]
    partes = sorted({r["parceiro_id"]} | {x["parceiro_id"] for x in regs} | {CHK.ESCRITORIO(n) or "sem_parceiro" for n in negs})
    tipos = {p: (app.repo.obter("parceiro", p) or {}).get("tipo") for p in partes}
    sev = "alta" if sum(1 for t in tipos.values() if t == "master") >= 2 else "media"
    c = {"conflito_id": app.novo_id("C", 4), "cnpj_raiz_hmac": r["cnpj_raiz_hmac"], "cnpj_mascara": r["cnpj_mascara"], "origem": "registro",
         "tipo": "registro_x_registro" if regs else "registro_x_negocio", "partes": partes, "severidade": sev, "estado": "aberto",
         "registros": [r["registro_id"]] + [x["registro_id"] for x in regs], "fatos": CHK.historico_raiz(app, r["cnpj_raiz_hmac"]),
         "regra": "Desempate PRM-R31: (1) registro válido mais antigo; (2) quem comprovou primeiro a relação; (3) quem levou à reunião de diagnóstico; (4) decisão do Luis.",
         "aberto_em": agora, "prazo": app.cal.prazo_du(app.agora(), app.param("registro.sla_conflito_du")).isoformat(), "nota": nota}
    app.repo.inserir("conflito", c)
    r = transitar(app, r, "em_conflito", ator.rotulo(), ator.papel, motivo_interno="conflito %s" % c["conflito_id"],
                  conflito_id=c["conflito_id"], pausado_desde=agora if app.param("registro.pausa_validade_em_conflito") else None)
    NT.alertar_save(app, "luis", "Conflito de canal para decidir: %s" % c["conflito_id"], "Raiz %s, %d parte(s), severidade %s. Prazo: %s." % (
        c["cnpj_mascara"], len(partes), sev, CAL.fmt(c["prazo"])), tipo="pedido", go="canal/conflitos/" + c["conflito_id"], chave="conflito|" + c["conflito_id"])
    return r, c


def decidir_conflito(app, ator, c, vencedor=None, decisao="primeiro_registro", nota=None):
    """Só o Luis (R15, D98). vencedor = registro_id que fica com a empresa; sem vencedor (save_direto) todos são recusados."""
    exigir(ator, "decidir_conflito")
    if c["estado"] != "aberto":
        raise Conflito("Este conflito já foi decidido.")
    if decisao not in ("primeiro_registro", "divisao_excecao", "save_direto", "sem_conflito"):
        raise Invalido("Decisão fora da lista.")
    if decisao != "save_direto" and vencedor not in c["registros"]:
        raise Invalido("Escolha o registro vencedor entre os do conflito.")
    for rid in c["registros"]:
        r = app.repo.obter("registro", rid)
        if not r or r["estado"] != "em_conflito":
            continue
        if r.get("pausado_desde"):
            r["dias_pausados"] = int(r.get("dias_pausados") or 0) + (CAL.dia(app.agora()) - CAL.dia(r["pausado_desde"])).days
            r = app.repo.atualizar("registro", rid, {"dias_pausados": r["dias_pausados"]})
        if rid == vencedor:
            aprovar(app, ator, r, conflito=True)
        else:
            recusar(app, ator, r, 4, conflito=True)
    return app.repo.atualizar("conflito", c["conflito_id"], {"estado": "decidido", "decisao": decisao, "vencedor_registro_id": vencedor,
                                                             "decidido_por": ator.rotulo(), "decidido_em": app.agora_iso(), "nota": nota})


def pedir_complemento(app, ator, r, pergunta):
    pergunta = " ".join(str(pergunta or "").split())
    if not 5 <= len(pergunta) <= 300:
        raise Invalido("Escreva a pergunta ao parceiro (até 300 caracteres).")
    from .auditoria import auditar_saida
    ok, motivos = auditar_saida(pergunta)
    if not ok:
        raise Invalido("O texto não pode sair assim: " + "; ".join(motivos), codigo="auditor")
    ate = app.cal.prazo_du(app.agora(), app.param("registro.complemento_mantem_carimbo_du"))
    r = transitar(app, r, "aguardando_parceiro", ator.rotulo(), ator.papel, motivo_interno="pedido de esclarecimento", pergunta=pergunta,
                  complemento_ate=ate.isoformat())
    NT.avisar_registro(app, r, "M-02", tipo="pede_voce", com_titular=False, chave="M-02|%s" % app.agora_iso()[:16], pergunta=pergunta,
                       data_limite=CAL.fmt_data(ate))
    return r


def decidir_prorrogacao(app, ator, r, aceitar):
    if not r.get("pedido_prorrogacao"):
        raise Conflito("Não há pedido de prorrogação neste registro.")
    if aceitar:
        r = _prorrogar(app, r, ator.rotulo(), ator.papel, "pedido do parceiro aceito")
    else:
        r = app.repo.atualizar("registro", r["registro_id"], {"pedido_prorrogacao": None, "prorrogacao_negada_em": app.agora_iso()})
    return r


def _prorrogar(app, r, quem, papel, motivo):
    base = date.fromisoformat(r["valido_ate"])
    ate = (base + timedelta(days=app.param("registro.prorrogacao_dias"))).isoformat()
    r = transitar(app, r, "prorrogado", quem, papel, motivo_interno=motivo, prorrogado_ate=ate, prorrogacoes=int(r.get("prorrogacoes") or 0) + 1,
                  pedido_prorrogacao=None)
    NT.avisar_registro(app, r, "M-07", com_titular=False, prorrogado_ate=CAL.fmt_data(ate))
    return r


# ---------------------------------------------------------------- ações do parceiro
def cancelar(app, ator, r):
    return transitar(app, r, "cancelado", ator.rotulo(), ator.papel, motivo_interno="desistência do parceiro")


def pedir_prorrogacao(app, ator, r, fato):
    exigir(ator, "pedir_prorrogacao")
    fato = " ".join(str(fato or "").split())
    exigir_sem_dado_pessoal({"fato": fato})
    if not 10 <= len(fato) <= 500:
        raise Invalido("Conte o que aconteceu com a empresa (de 10 a 500 caracteres).", campos={"fato": "Conte o fato novo."})
    v = visao_parceiro(app, r)
    if not v["pode_prorrogar"]:
        raise Conflito("A prorrogação só pode ser pedida nos 30 dias antes do vencimento, uma vez.")
    app.repo.atualizar("registro", r["registro_id"], {"pedido_prorrogacao": {"fato": fato, "em": app.agora_iso(), "por": ator.usuario_id}})
    NT.alertar_save(app, "daniela", "Pedido de prorrogação: %s" % r["registro_id"], "Decidir em %d d.u." % app.param("registro.sla_decisao_du"),
                    tipo="pedido", go="canal/registros/" + r["registro_id"], chave="prorrogacao|" + r["registro_id"])
    return T("REG-prorrogacao-pedida")


def responder_complemento(app, ator, r, resposta):
    resposta = " ".join(str(resposta or "").split())
    exigir_sem_dado_pessoal({"resposta": resposta})
    if not 2 <= len(resposta) <= 500:
        raise Invalido("Escreva a resposta (até 500 caracteres).", campos={"resposta": "Escreva a resposta."})
    if r["estado"] != "aguardando_parceiro":
        raise Conflito("Este registro não está esperando resposta.")
    if app.agora() > CAL.ler(r["complemento_ate"]):
        raise Conflito("O prazo para responder terminou.")
    r = transitar(app, r, "em_analise", ator.rotulo(), ator.papel, motivo_interno="complemento recebido no prazo (carimbo mantido)",
                  complemento=resposta, pergunta=None)
    NT.alertar_save(app, "daniela", "Complemento recebido: %s" % r["registro_id"], "O parceiro respondeu ao pedido de informação.", tipo="pedido",
                    go="canal/registros/" + r["registro_id"], chave="complemento|%s|%s" % (r["registro_id"], app.agora_iso()[:16]))
    return r


# ---------------------------------------------------------------- rotina diária (06h00; sistema)
def _avancou(app, r, neg):
    if not neg:
        return False
    lim = app.param("registro.atividade_para_prorrogar_dias")
    hoje = CAL.dia(app.agora())
    datas = [neg.get("ultima_atividade_em"), neg.get("entrou_etapa_em")]
    return any(d and (hoje - CAL.dia(d)).days <= lim for d in datas)


def rotina(app):
    agora, hoje = app.agora(), CAL.dia(app.agora())
    n = {"expirados": 0, "prorrogados": 0, "convertidos": 0, "protegidos": 0, "encerrados": 0, "avisos": 0, "recusados_sem_complemento": 0,
         "rascunhos_descartados": 0, "aviso_demora": 0, "sem_card": 0}
    ligados = {r.get("deal_id") for r in app.repo.listar("registro") if r.get("deal_id")}
    for r in app.repo.listar("registro"):
        e = r["estado"]
        if e == "rascunho" and (hoje - CAL.dia(r["criado_em"])).days > app.param("registro.rascunho_some_dias"):
            transitar(app, r, "cancelado", "sistema", "sistema", motivo_interno="rascunho sem edição"); n["rascunhos_descartados"] += 1
            continue
        if e == "aguardando_parceiro" and agora > CAL.ler(r["complemento_ate"]):
            recusar(app, None, r, 1, campos="resposta ao pedido de informação", sistema=True); n["recusados_sem_complemento"] += 1
            continue
        if e == "em_conflito" and not r.get("aviso_demora_em") and app.cal.du_entre(r["carimbo"], agora) >= app.param("registro.conflito_aviso_demora_du"):
            app.repo.atualizar("registro", r["registro_id"], {"aviso_demora_em": app.agora_iso()})
            NT.avisar_registro(app, r, "M-04", com_titular=False); n["aviso_demora"] += 1
            continue
        if e not in ("aprovado", "prorrogado", "convertido", "protegido_cliente"):
            continue
        neg = app.repo.obter("negocio", r["deal_id"]) if r.get("deal_id") else None
        if not neg and e != "protegido_cliente":  # reconciliação por raiz HMAC + escritório (03 §3.5, passos 1 e 2)
            cands = [x for x in app.repo.listar("negocio", cnpj_raiz_hmac=r["cnpj_raiz_hmac"]) if CHK.ESCRITORIO(x) == r["parceiro_id"]
                     and x["deal_id"] not in ligados and x.get("criado_em") and CAL.dia(x["criado_em"]) >= CAL.dia(r["carimbo"]) - timedelta(days=2)]
            if len(cands) == 1:
                neg = cands[0]; ligados.add(neg["deal_id"])
                mud = {"deal_id": neg["deal_id"], "vinculo_deal": "automatico", "vinculado_em": app.agora_iso()}
                if e in ("aprovado", "prorrogado"):
                    r = transitar(app, r, "convertido", "sistema", "sistema", motivo_interno="negócio %s ligado" % neg["deal_id"], **mud)
                    NT.avisar_registro(app, r, "M-06", com_titular=False, valido_ate=CAL.fmt_data(_limite(r))); n["convertidos"] += 1
                else:
                    r = app.repo.atualizar("registro", r["registro_id"], mud)
                e = r["estado"]
            elif len(cands) > 1:
                app.repo.atualizar("registro", r["registro_id"], {"vinculo_deal": "sugerido"})
        if neg and neg.get("status") == "ganho" and e != "protegido_cliente":
            r = transitar(app, r, "protegido_cliente", "sistema", "sistema", motivo_interno="negócio ganho %s" % neg["deal_id"])
            NT.avisar_registro(app, r, "M-08"); n["protegidos"] += 1
            continue
        if neg and neg.get("status") == "perdido" and e != "protegido_cliente":
            r = transitar(app, r, "encerrado_sem_contrato", "sistema", "sistema", motivo_interno="negócio perdido %s" % neg["deal_id"])
            NT.avisar_registro(app, r, "M-10", data=CAL.fmt_data(hoje)); n["encerrados"] += 1
            continue
        if e == "protegido_cliente":
            continue
        lim = date.fromisoformat(_limite(r))
        if e == "aprovado" and not r.get("deal_id") and not r.get("alerta_sem_card_em") and \
                app.cal.du_entre(r["decidido_em"], agora) > app.param("registro.alerta_sem_card_du"):
            app.repo.atualizar("registro", r["registro_id"], {"alerta_sem_card_em": app.agora_iso()})
            NT.alertar_save(app, "daniela", "Registro sem card no HubSpot: %s" % r["registro_id"], "Aprovado há mais de %d d.u. e o negócio não apareceu na cópia diária." %
                            app.param("registro.alerta_sem_card_du"), chave="semcard|" + r["registro_id"]); n["sem_card"] += 1
        if hoje >= lim:
            if int(r.get("prorrogacoes") or 0) < app.param("registro.prorrogacoes_max") and _avancou(app, r, neg) and r.get("valido_ate"):
                _prorrogar(app, r, "sistema", "sistema", "avanço ou atividade nos últimos %d dias" % app.param("registro.atividade_para_prorrogar_dias"))
                n["prorrogados"] += 1
            elif hoje > lim:
                r = transitar(app, r, "expirado", "sistema", "sistema", motivo_interno="fim da validade")
                NT.avisar_registro(app, r, "M-09", data=CAL.fmt_data(hoje)); n["expirados"] += 1
            continue
        for d in app.param("registro.aviso_vencimento_dias"):
            if (lim - hoje).days <= d and d not in (r.get("avisos") or []):
                r = app.repo.atualizar("registro", r["registro_id"], {"avisos": (r.get("avisos") or []) + [d]})
                NT.avisar_registro(app, r, "M-14", tipo="pede_voce", chave="M-14|%d" % d, razao_social=r.get("razao_social") or r["cnpj_mascara"],
                                   dias=(lim - hoje).days, valido_ate=CAL.fmt_data(lim)); n["avisos"] += 1
                break
    return n
