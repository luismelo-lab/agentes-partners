"""Módulo 4 · Demandas (02 §7): fila única (U2) com o mesmo ID D-AAAA-NNNN do registro único de demandas, histórico antes
do chamado (PRM-R72: lib/historico.py avaliar) e chamado GLPI só como RASCUNHO aprovado pela Daniela (o PRM não escreve
no GLPI, R26). A resposta ao parceiro sai sempre por pessoa, depois do auditor (PRM-R13, R73).

Fase 1: o portal grava em prm_demanda_portal (o prm_demanda.json é gerado do registro único e seria sobrescrito);
com PRM_REGISTRO_DEMANDAS=<registro/demandas.json> o número sai da mesma sequência do registro único (mesma trava).
"""
import fcntl, json, os, re
from datetime import timedelta

from . import calendario as CAL
from . import catalogo as CAT
from . import negocios as NG
from . import notificacoes as NT
from .auditoria import auditar_saida, exigir_sem_dado_pessoal, limpar
from .erros import Conflito, Invalido, NaoEncontrado
from .identidade import exigir, ve, ve_negocio
from .maquinas import DEMANDA
from .textos import texto as T

ROTULO = {"aberta": "Recebido", "triada": "Recebido", "reaberta": "Recebido", "resposta_historico": "Em preparo", "aguardando_parceiro": "Precisa de você",
          "encaminhada_area": "Com a área", "respondida": "Respondido", "concluida": "Concluído"}
CHIP = {"aguardando_parceiro": "acao", "respondida": "acao", "concluida": "ok"}


# ---------------------------------------------------------------- id único (mesma sequência do registro único quando ligado)
def _alocar_id(app):
    reg = os.environ.get("PRM_REGISTRO_DEMANDAS")
    if not reg:
        return app.novo_id("D", 4)
    ano = str(CAL.local(app.agora()).year)
    with open(reg + ".trava", "w") as t:
        fcntl.flock(t, fcntl.LOCK_EX)
        R = json.load(open(reg)) if os.path.exists(reg) else {"seq": {}, "demandas": {}}
        R["seq"][ano] = R["seq"].get(ano, 0) + 1
        i = "D-%s-%04d" % (ano, R["seq"][ano])
        R["demandas"][i] = {"id": i, "chave": "portal|" + i, "origem": "portal", "status": "em_analise", "aberta_em": CAL.local(app.agora()).isoformat(timespec="minutes"),
                            "eventos": [{"quando": app.agora_iso(), "o_que": "aberta pelo portal do parceiro"}]}
        tmp = reg + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(R, f, ensure_ascii=False, indent=1)
        os.replace(tmp, reg)
        fcntl.flock(t, fcntl.LOCK_UN)
    return i


def _evento(app, d, o_que, quem, papel, de=None, para=None):
    app.repo.inserir("demanda_evento", {"demanda_id": d["demanda_id"], "quando": app.agora_iso(), "quem": quem, "papel": papel, "o_que": o_que, "de": de, "para": para})


def _transitar(app, d, para, ator_rot, papel, o_que, **mudar):
    DEMANDA.exigir(d["estado"], para, papel)
    de = d["estado"]
    mudar.update(estado=para, atualizada_em=app.agora_iso())
    d = app.repo.atualizar("demanda", d["demanda_id"], mudar)
    _evento(app, d, o_que, ator_rot, papel, de, para)
    return d


# ---------------------------------------------------------------- empresa ligada (só do escopo do ator)
def _empresa(app, ator, ref):
    if not ref:
        return None
    for r in app.repo.listar("registro", ref=ref):
        if ve(ator, r):
            return {"ref": ref, "tipo": "registro", "registro_id": r["registro_id"], "deal_id": r.get("deal_id"), "nome": r.get("razao_social"),
                    "encerrada": r["estado"] in ("recusado", "expirado", "encerrado_sem_contrato")}
    n = NG.por_ref(app, ator, ref)
    if n:
        e, _ = NG.estado(app, n)
        return {"ref": ref, "tipo": "negocio", "deal_id": n["deal_id"], "nome": None, "encerrada": e == "encerrado"}
    raise NaoEncontrado()


# ---------------------------------------------------------------- abrir (parceiro, ou a Daniela em nome dele)
def abrir(app, ator, d, em_nome_de=None):
    exigir(ator, "abrir_demanda")
    tipo = d.get("tipo")
    if tipo not in CAT.PARCEIRO:
        raise Invalido("Escolha sobre o que é o pedido.", campos={"tipo": "Escolha sobre o que é o pedido."})
    txt = " ".join(str(d.get("texto") or "").split())
    if not 10 <= len(txt) <= 2000:
        raise Invalido("Escreva o pedido (de 10 a 2.000 caracteres).", campos={"texto": "Escreva o pedido."})
    exigir_sem_dado_pessoal({"texto": txt})
    if ator.tipo == "parceiro":
        parceiro_id, usuario_id = ator.parceiro_id, ator.usuario_id
    else:
        parceiro_id, usuario_id = (em_nome_de or {}).get("parceiro_id"), (em_nome_de or {}).get("usuario_id")
        if not app.repo.obter("parceiro", parceiro_id or ""):
            raise Invalido("Escolha o parceiro.")
    emp = _empresa(app, ator, d.get("empresa_ref"))
    cod = CAT.codigo(tipo, negocio_encerrado=bool(emp and emp["encerrada"]), apoio_juridico=d.get("apoio_juridico") is True)
    t = CAT.tipos().get(cod, {})
    agora = app.agora()
    p1, sol = t.get("primeira_resposta_du", 1), t.get("solucao_du")
    dem = {"demanda_id": _alocar_id(app), "ref": app.ref(), "canal": "portal" if ator.tipo == "parceiro" else "whatsapp",
           "origem": "portal-parceiro" if ator.tipo == "parceiro" else "painel-time", "parceiro_id": parceiro_id, "usuario_id": usuario_id,
           "tipo_tela": tipo, "codigo": cod, "area": CAT.PARCEIRO[tipo]["area"], "dono": CAT.PARCEIRO[tipo]["dono"], "urgente": bool(CAT.PARCEIRO[tipo].get("urgente")),
           "validado": bool(t.get("validado")), "empresa": emp, "estado": "aberta", "aberta_em": app.agora_iso(),
           "primeira_resposta_ate": app.cal.prazo_du(agora, p1 or 0).isoformat(), "solucao_ate": app.cal.prazo_du(agora, sol).isoformat() if sol is not None else None,
           "mensagens": [{"de": "parceiro", "texto": limpar(txt), "quando": app.agora_iso()}], "escala": 0, "reaberturas": 0}
    app.repo.inserir("demanda", dem)
    _evento(app, dem, "aberta", ator.rotulo(), ator.papel, None, "aberta")
    if usuario_id:
        NT.avisar_usuario(app, usuario_id, "M-30", "resposta", "pedidos/" + dem["ref"], chave="M-30|" + dem["demanda_id"], id=dem["demanda_id"],
                          tipo=CAT.PARCEIRO[tipo]["rotulo"], primeira_resposta=_prazo_txt(p1))
    NT.alertar_save(app, "daniela", "Pedido do portal: %s · %s" % (dem["demanda_id"], CAT.PARCEIRO[tipo]["rotulo"]),
                    "Parceiro %s. 1ª resposta até %s." % (parceiro_id, CAL.fmt(dem["primeira_resposta_ate"])), tipo="pedido",
                    go="canal/demandas/" + dem["demanda_id"], prioridade="alta" if dem["urgente"] else "normal", chave="dem|" + dem["demanda_id"])
    if tipo == "reclamacao":  # PRM-R77: reclamação vai à Daniela com a Qualidade e aviso ao Luis
        NT.alertar_save(app, "luis", "Reclamação de parceiro: %s" % dem["demanda_id"], "A Daniela trata com a Qualidade.", prioridade="alta",
                        chave="recl|" + dem["demanda_id"])
    dem = triar(app, dem)
    return visao_parceiro(app, dem)


def _prazo_txt(n):
    return "hoje" if not n else ("%d dia útil" % n if n == 1 else "%d dias úteis" % n)


# ---------------------------------------------------------------- triagem: histórico antes do chamado (PRM-R72)
def avaliador_lib():
    """lib/historico.py (índice com dado de cliente, fica no Mac: L10). None se não houver índice."""
    try:
        import historico
        if not os.path.isdir(historico.CACHE):
            return None
        return lambda texto, master="", empresa="", cnpj="": historico.avaliar(texto, master=master, empresa=empresa, cnpj=cnpj)
    except Exception:  # noqa: BLE001
        return None


def avaliador_fixture(pares):
    """Histórico de teste (pares pergunta → resposta fictícios), com a mesma saída do historico.avaliar."""
    def toks(s):
        return {w for w in re.findall(r"[a-zà-ú0-9]{4,}", s.lower())}

    def f(texto, master="", empresa="", cnpj=""):
        q = toks(texto)
        melhor, ader = None, 0.0
        for p in pares:
            a = len(q & toks(p["pergunta"])) / max(1, len(toks(p["pergunta"])))
            if a > ader:
                melhor, ader = p, a
        ok = bool(melhor) and ader >= 0.5
        return {"suficiente": ok, "criterio": "mesma_pergunta_respondida" if ok else None, "confianca": round(ader, 2),
                "fontes": [{"fonte": "historico-teste", "data": melhor["data"], "trecho": melhor["resposta"], "aderencia": round(ader, 2)}] if melhor else [],
                "faltou": "" if ok else "nenhuma resposta anterior com aderência suficiente", "rota": "responder" if ok else "glpi"}
    return f


def triar(app, d):
    av = None
    if app.param("demanda.historico_ativo") and app.avaliador_historico:
        par = app.repo.obter("parceiro", d["parceiro_id"] or "") or {}
        try:
            av = app.avaliador_historico(d["mensagens"][-1]["texto"], master=par.get("nome_exibicao", ""), empresa=(d.get("empresa") or {}).get("nome") or "")
        except Exception:  # noqa: BLE001  histórico fora do ar não trava a demanda: segue para a triagem da Daniela
            av = None
    hist = None
    if av:
        hist = {"suficiente": bool(av.get("suficiente")), "criterio": av.get("criterio"), "confianca": av.get("confianca"), "faltou": av.get("faltou"),
                "fontes": [{"fonte": f.get("fonte"), "data": f.get("data"), "trecho": limpar(str(f.get("trecho") or ""))[:220]} for f in (av.get("fontes") or [])[:3]]}
        if av.get("suficiente"):
            try:
                import historico
                base = historico.base_resposta(av)
            except Exception:  # noqa: BLE001
                base = (av.get("fontes") or [{}])[0].get("trecho") or ""
            hist["rascunho"] = limpar(base)[:1500]
    if hist and hist.get("suficiente") and hist.get("rascunho"):
        return _transitar(app, d, "resposta_historico", "sistema", "sistema", "histórico tem resposta: rascunho pronto para a Daniela conferir", historico=hist)
    t = CAT.tipos().get(d["codigo"], {})
    falta = ", ".join(t.get("dados_minimos") or []) or "conferir com o parceiro"
    chamado = {"estado": "rascunho", "area": d["area"], "titulo": "%s · %s" % (CAT.PARCEIRO[d["tipo_tela"]]["rotulo"], d["demanda_id"]),
               "descricao": "O que o parceiro pede: %s\nO que já levantamos: %s\nO que falta: %s" % (
                   d["mensagens"][0]["texto"][:600], (hist or {}).get("faltou") or "histórico sem resposta suficiente", falta),
               "glpi": "nao_enviado"}
    return _transitar(app, d, "triada", "sistema", "sistema", "triada; chamado sugerido em rascunho", historico=hist, chamado=chamado)


# ---------------------------------------------------------------- visão
def _prazo_visivel(d):
    if d["estado"] in ("respondida", "concluida"):
        return None
    if d.get("validado") and d.get("solucao_ate"):
        return "Retorno previsto da Save: até %s" % CAL.fmt(d["solucao_ate"])
    t = CAT.tipos().get(d["codigo"], {})
    return T("DEM-primeira-resposta", primeira_resposta=t.get("primeira_resposta_du") or 0) if d["estado"] in ("aberta", "triada", "reaberta", "resposta_historico") else None


def visao_parceiro(app, d):
    e = d["estado"]
    rot = ROTULO.get(e, e)
    if e == "encaminhada_area":
        rot = "Com a área (%s)" % d["area"]
    msgs = [{"de": m["de"], "texto": m["texto"], "quando": CAL.fmt(m["quando"]), "selo": m.get("selo")} for m in d.get("mensagens", [])]
    return {"ref": d["ref"], "id": d["demanda_id"], "tipo": CAT.PARCEIRO[d["tipo_tela"]]["rotulo"], "estado": e, "rotulo": rot, "chip": CHIP.get(e, "info"),
            "aberta_em": CAL.fmt(d["aberta_em"]), "prazo": _prazo_visivel(d), "mensagens": msgs, "empresa": (d.get("empresa") or {}).get("ref"),
            "empresa_nome": (d.get("empresa") or {}).get("nome"), "pode_concluir": e == "respondida", "pode_reabrir": _pode_reabrir(app, d),
            "pode_complementar": e == "aguardando_parceiro", "atrasada": d.get("escala", 0) > 0, "usuario_id": d.get("usuario_id")}


def visao_save(app, d):
    v = visao_parceiro(app, d)
    agora = app.agora()
    venc = CAL.ler(d.get("solucao_ate") or d["primeira_resposta_ate"])
    horas = round((venc - agora).total_seconds() / 3600)
    sla = ("Fora do prazo · %d h" % -horas, "erro") if horas < 0 else (("Perto do prazo · %d h" % horas, "atencao") if horas <= 8 else ("No prazo · %d h" % horas, "ok"))
    v.update({"estado": d["estado"], "parceiro_id": d["parceiro_id"], "codigo": d["codigo"], "area": d["area"], "dono": d["dono"], "canal": d["canal"],
              "origem": d["origem"], "historico": d.get("historico"), "chamado": d.get("chamado"), "sla": {"texto": sla[0], "chip": sla[1]},
              "urgente": d.get("urgente"), "escala": d.get("escala", 0)})
    return v


def _pode_reabrir(app, d):
    if d["estado"] != "concluida" or not d.get("concluida_em"):
        return False
    return (CAL.dia(app.agora()) - CAL.dia(d["concluida_em"])).days <= app.param("demanda.reabertura_dias")


def do_ator(app, ator):
    xs = app.repo.listar("demanda")
    if ator.tipo == "parceiro":
        xs = [d for d in xs if ve(ator, d)]
    return sorted(xs, key=lambda d: d["aberta_em"], reverse=True)


def fila_save(app):
    """Fila única por SLA: as do portal (prm_demanda_portal) e as do registro único (prm_demanda: WhatsApp, e-mail)."""
    portal = [visao_save(app, d) for d in app.repo.listar("demanda") if d["estado"] not in ("concluida",)]
    outras = [{"id": d.get("demanda_id"), "origem": d.get("origem"), "canal": d.get("canal"), "estado": d.get("estado"), "parceiro_id": d.get("parceiro_id"),
               "tipo": d.get("tipo_sla") or "sem tipo", "aberta_em": CAL.fmt(d.get("aberta_em")), "somente_leitura": True}
              for d in app.repo.listar("demanda_unica") if d.get("estado") in ("responder", "acompanhar", "em_analise", "aguardando_aprovacao")]
    return sorted(portal, key=lambda v: v["sla"]["texto"].startswith("No prazo")), outras


# ---------------------------------------------------------------- ações da Save (por decisao.decidir)
def responder(app, ator, d, texto, origem="area"):
    exigir(ator, "responder_demanda")
    texto = " ".join(str(texto or (d.get("historico") or {}).get("rascunho") or "").split())
    if len(texto) < 5:
        raise Invalido("Escreva a resposta.")
    ok, motivos = auditar_saida(texto)
    if not ok:  # PRM-R13: com alerta ALTO ou MÉDIO o envio fica bloqueado
        raise Invalido("A resposta não pode sair assim: " + "; ".join(motivos), codigo="auditor")
    selo = T("DEM-selo-historico") if origem == "historico" else T("DEM-selo-area", area=d["area"])
    msgs = d.get("mensagens", []) + [{"de": "save", "texto": texto, "quando": app.agora_iso(), "selo": selo, "por": ator.rotulo()}]
    d = _transitar(app, d, "respondida", ator.rotulo(), ator.papel, "resposta enviada (%s)" % origem, mensagens=msgs, respondida_em=app.agora_iso())
    if d.get("usuario_id"):
        NT._gravar(app, "usuario:" + d["usuario_id"], "Resposta ao pedido %s" % d["demanda_id"], texto, "resposta", "prm", "pedidos/" + d["ref"],
                   chave="resp|%s|%s" % (d["demanda_id"], app.agora_iso()[:16]), auditoria="auditado")
    return d


def encaminhar(app, ator, d, titulo=None, descricao=None):
    """Aprovar e abrir no GLPI: o PRM grava a aprovação e marca 'abrir manualmente' (o GLPI não é tocado, R26)."""
    exigir(ator, "aprovar_chamado")
    ch = dict(d.get("chamado") or {})
    ch.update(estado="aprovado", glpi="abrir_manualmente", aprovado_por=ator.rotulo(), aprovado_em=app.agora_iso())
    if titulo:
        ch["titulo"] = limpar(titulo)[:160]
    if descricao:
        ch["descricao"] = limpar(descricao)[:4000]
    d = _transitar(app, d, "encaminhada_area", ator.rotulo(), ator.papel, "chamado aprovado (abrir no GLPI manualmente)", chamado=ch)
    if d.get("usuario_id"):
        if d.get("validado") and d.get("solucao_ate"):
            NT.avisar_usuario(app, d["usuario_id"], "M-32", "resposta", "pedidos/" + d["ref"], chave="M-32|" + d["demanda_id"], id=d["demanda_id"], area=d["area"],
                              data=CAL.fmt(d["solucao_ate"]))
        else:
            NT.avisar_usuario(app, d["usuario_id"], "M-32-sem-previsao", "resposta", "pedidos/" + d["ref"], chave="M-32|" + d["demanda_id"], id=d["demanda_id"], area=d["area"])
    return d


def recusar_chamado(app, ator, d, motivo):
    exigir(ator, "aprovar_chamado")
    ch = dict(d.get("chamado") or {})
    ch.update(estado="recusado", motivo=limpar(motivo or "")[:300], recusado_por=ator.rotulo())
    d = app.repo.atualizar("demanda", d["demanda_id"], {"chamado": ch})
    _evento(app, d, "chamado recusado", ator.rotulo(), ator.papel)
    return d


def pedir_dados(app, ator, d, itens):
    exigir(ator, "responder_demanda")
    itens = " ".join(str(itens or "").split())
    ok, motivos = auditar_saida(itens)
    if not ok or len(itens) < 3:
        raise Invalido("Escreva o que falta (o texto passa pelo auditor): " + "; ".join(motivos))
    msgs = d.get("mensagens", []) + [{"de": "save", "texto": T("M-31", id=d["demanda_id"], itens=itens), "quando": app.agora_iso(), "por": ator.rotulo()}]
    d = _transitar(app, d, "aguardando_parceiro", ator.rotulo(), ator.papel, "faltam dados mínimos", mensagens=msgs, pausada_desde=app.agora_iso())
    if d.get("usuario_id"):
        NT.avisar_usuario(app, d["usuario_id"], "M-31", "pede_voce", "pedidos/" + d["ref"], chave="M-31|%s|%s" % (d["demanda_id"], app.agora_iso()[:16]),
                          id=d["demanda_id"], itens=itens)
    return d


# ---------------------------------------------------------------- ações do parceiro
def complementar(app, ator, d, texto):
    texto = " ".join(str(texto or "").split())
    exigir_sem_dado_pessoal({"texto": texto})
    if not 2 <= len(texto) <= 2000:
        raise Invalido("Escreva a resposta.")
    if d["estado"] != "aguardando_parceiro":
        raise Conflito("Este pedido não está esperando você.")
    pausa = app.cal.du_entre(d["pausada_desde"], app.agora())  # o relógio do SLA parou enquanto esperava o parceiro
    mud = {"mensagens": d["mensagens"] + [{"de": "parceiro", "texto": limpar(texto), "quando": app.agora_iso()}], "pausada_desde": None}
    if d.get("solucao_ate") and pausa:
        mud["solucao_ate"] = app.cal.prazo_du(CAL.ler(d["solucao_ate"]), pausa).isoformat()
    return _transitar(app, d, "triada", ator.rotulo(), ator.papel, "parceiro complementou", **mud)


def concluir(app, ator, d):
    return _transitar(app, d, "concluida", ator.rotulo(), ator.papel, "parceiro marcou resolvido", concluida_em=app.agora_iso())


def reabrir(app, ator, d, texto=""):
    if not _pode_reabrir(app, d):
        raise Conflito("A reabertura vale até %d dias depois de concluído." % app.param("demanda.reabertura_dias"))
    exigir_sem_dado_pessoal({"texto": texto})
    msgs = d["mensagens"] + ([{"de": "parceiro", "texto": limpar(texto), "quando": app.agora_iso()}] if texto else [])
    d = _transitar(app, d, "reaberta", ator.rotulo(), ator.papel, "reaberta", mensagens=msgs, reaberturas=d.get("reaberturas", 0) + 1)
    if d.get("usuario_id"):
        NT.avisar_usuario(app, d["usuario_id"], "DEM-reaberta", "resposta", "pedidos/" + d["ref"], chave="reab|%s|%d" % (d["demanda_id"], d["reaberturas"]), id=d["demanda_id"])
    return triar(app, d)


# ---------------------------------------------------------------- rotina: atraso com escala 1, 3, 5 d.u. e conclusão sem reação
def rotina(app):
    n = {"atrasadas": 0, "concluidas": 0}
    agora = app.agora()
    escala = app.param("demanda.escala_du")
    alvo = {0: None, 1: "dono", 2: "daniela", 3: "luis"}
    for d in app.repo.listar("demanda"):
        if d["estado"] == "respondida" and app.cal.du_entre(d.get("respondida_em") or d["aberta_em"], agora) >= app.param("demanda.fecha_sem_reacao_du"):
            _transitar(app, d, "concluida", "sistema", "sistema", "concluída sem reação em %d d.u." % app.param("demanda.fecha_sem_reacao_du"), concluida_em=app.agora_iso())
            n["concluidas"] += 1
            continue
        if d["estado"] in ("respondida", "concluida", "aguardando_parceiro"):
            continue
        venc = CAL.ler(d.get("solucao_ate") or d["primeira_resposta_ate"])
        if agora <= venc:
            continue
        du = app.cal.du_entre(venc, agora)
        nivel = sum(1 for x in escala if du >= x)
        if nivel > d.get("escala", 0):
            antigo = d.get("escala", 0)
            primeira = not antigo
            d = app.repo.atualizar("demanda", d["demanda_id"], {"escala": nivel})
            for lv in range(antigo + 1, nivel + 1):  # cada degrau cruzado avisa o seu dono: área, gestora, Luis
                quem = alvo.get(lv) or "luis"
                quem = d["dono"] if quem == "dono" else quem
                NT.alertar_save(app, quem, "Pedido fora do prazo: %s" % d["demanda_id"], "%d d.u. vencidos (escala %d)." % (du, lv), prioridade="alta",
                                go="canal/demandas/" + d["demanda_id"], chave="escala|%s|%d" % (d["demanda_id"], lv))
            if primeira and d.get("usuario_id"):  # M-33 uma vez, na primeira vez que o prazo vence
                NT.avisar_usuario(app, d["usuario_id"], "M-33", "resposta", "pedidos/" + d["ref"], chave="M-33|" + d["demanda_id"], id=d["demanda_id"])
            n["atrasadas"] += 1
    return n
