"""Módulo 2 · Meus negócios (02 §5): 7 estados na linguagem do parceiro, pendência "Precisa de algo de você" e ficha.

PRM-R43 mapa etapa → estado no parâmetro negocio.mapa_etapas (a Daniela ajusta sem deploy); etapa sem mapa mantém o
último estado conhecido (ou "recebido") e conta como alerta "etapa sem mapa" para o Dados.
PRM-R44 o parceiro vê só dado objetivo: estado, data, próximo passo e com quem está a bola. Nunca valor do crédito,
honorário, tese técnica, parecer, prazo de PER, chance de êxito nem motivo interno da perda.
PRM-R45 negócio sem ligação segura com o parceiro não aparece a ninguém do lado externo.
"""
from . import calendario as CAL
from . import notificacoes as NT
from .auditoria import exigir_sem_dado_pessoal
from .erros import Invalido
from .identidade import exigir, ve_negocio
from .textos import texto as T

ESTADOS = ("recebido", "em_diagnostico", "precisa_de_voce", "apresentacao", "contrato", "execucao", "encerrado")
ROTULO = {"recebido": "Recebido", "em_diagnostico": "Em diagnóstico", "precisa_de_voce": "Precisa de você", "apresentacao": "Apresentação marcada",
          "contrato": "Contrato em andamento", "execucao": "Em execução", "encerrado": "Encerrado"}
BOLA = {"recebido": "Save", "em_diagnostico": "Save", "precisa_de_voce": "Você", "apresentacao": "Save e empresa", "contrato": "Empresa",
        "execucao": "Save", "encerrado": "—"}
CHIP = {"precisa_de_voce": "acao", "encerrado": "neutro"}
TIPOS_PENDENCIA = {"documento": "documento fiscal", "ecac": "acesso ao e-CAC", "procuracao": "procuração", "reuniao": "reunião com o decisor",
                   "assinatura": "assinatura do cliente", "outro": "outro"}


def pendencias_abertas(app, deal_id):
    return [p for p in app.repo.listar("pendencia", deal_id=deal_id) if not p.get("resolvida_em")]


def estado(app, n):
    """(código do estado, etapa_sem_mapa)."""
    st = n.get("status")
    if st == "ganho":
        return ("encerrado" if n.get("distrato") else "execucao"), False
    if st == "perdido":
        return "encerrado", False
    if pendencias_abertas(app, n["deal_id"]):
        return "precisa_de_voce", False
    mapa = app.param("negocio.mapa_etapas")
    e = mapa.get(n.get("etapa"))
    if e is None:
        return n.get("estado_conhecido") or "recebido", True
    return e, False


def texto_estado(app, n, e):
    if e == "precisa_de_voce":
        ps = pendencias_abertas(app, n["deal_id"])
        return T("NEG-precisa_de_voce", pendencia=(ps[0].get("texto") or TIPOS_PENDENCIA.get(ps[0].get("tipo"), "um documento")) if ps else "um documento")
    if e == "encerrado":
        return T("NEG-encerrado-distrato" if n.get("distrato") else "NEG-encerrado-perdido")
    t = T("NEG-" + e)
    if e == "recebido" and n.get("etapa") == "Contato Futuro":
        t += " " + T("NEG-recebido-futuro")
    return t


def ref(app, n):
    return app.ref_estavel("neg", n["deal_id"])


def visao_parceiro(app, n, registro=None):
    e, _ = estado(app, n)
    desde = n.get("entrou_etapa_em") or n.get("fechado_em") or n.get("criado_em")
    passos = []
    ordem = ["recebido", "em_diagnostico", "apresentacao", "contrato", "execucao"]
    atual = "em_diagnostico" if e == "precisa_de_voce" else e
    for i, s in enumerate(ordem):
        if e == "encerrado":
            st = "feito" if n.get("status") == "ganho" or i == 0 else "futuro"
        else:
            idx = ordem.index(atual) if atual in ordem else 0
            st = "feito" if i < idx else ("bloqueado" if (i == idx and e == "precisa_de_voce") else "atual" if i == idx else "futuro")
        passos.append({"estado": s, "titulo": ROTULO[s], "situacao": st})
    return {"ref": ref(app, n), "tipo": "negocio", "estado": e, "rotulo": ROTULO[e], "chip": CHIP.get(e, "info"), "proximo_passo": texto_estado(app, n, e),
            "com": BOLA[e], "desde": CAL.fmt_data(desde), "desde_iso": desde, "cnpj_mascara": n.get("cnpj_mascara"),
            "razao_social": (registro or {}).get("razao_social") or n.get("empresa_nome") or "Empresa indicada", "passos": passos,
            "pendencias": [{"tipo": TIPOS_PENDENCIA.get(p["tipo"]), "texto": p.get("texto"), "desde": CAL.fmt_data(p["aberta_em"])} for p in pendencias_abertas(app, n["deal_id"])],
            "consultor_parceiro_id": n.get("parceiro_id") if n.get("master_id") else None}


def do_ator(app, ator):
    """Negócios visíveis ao ator (escritório ou só os do consultor). Só os ligados com segurança a um parceiro."""
    return [n for n in app.repo.listar("negocio") if (n.get("parceiro_id") or n.get("master_id")) and ve_negocio(ator, n)]


def por_ref(app, ator, r):
    for n in app.repo.listar("negocio"):
        if ref(app, n) == r and (n.get("parceiro_id") or n.get("master_id")) and ve_negocio(ator, n):
            return n
    return None


def marcar_pendencia(app, ator, deal_id, tipo, texto):
    """Save marca "Precisa de algo de você" (02 §5.2). O texto vai ao parceiro: passa pelo auditor e pelo bloqueio de dado pessoal."""
    exigir(ator, "marcar_pendencia")
    n = app.repo.obter("negocio", deal_id)
    if not n:
        raise Invalido("Negócio não encontrado no espelho do HubSpot.")
    if tipo not in TIPOS_PENDENCIA:
        raise Invalido("Escolha o tipo da pendência.")
    texto = " ".join(str(texto or "").split())[:200]
    exigir_sem_dado_pessoal({"texto": texto})
    if texto:
        from .auditoria import auditar_saida
        ok, motivos = auditar_saida(texto)
        if not ok:
            raise Invalido("O texto não pode sair assim: " + "; ".join(motivos), codigo="auditor")
    p = {"pendencia_id": app.novo_id("PD", 5), "deal_id": deal_id, "tipo": tipo, "texto": texto or None, "aberta_por": ator.papel,
         "aberta_em": app.agora_iso(), "resolvida_em": None, "parceiro_id": n.get("master_id") or n.get("parceiro_id"), "etapa_na_abertura": n.get("etapa")}
    app.repo.inserir("pendencia", p)
    return p


def resolver_pendencia(app, ator, pendencia_id):
    exigir(ator, "marcar_pendencia")
    return app.repo.atualizar("pendencia", pendencia_id, {"resolvida_em": app.agora_iso(), "resolvida_por": ator.papel})


def rotina(app):
    """Pendência aberta há mais de 7 dias: alerta à Daniela e M-16 ao parceiro, uma vez (PRM-R47).
    A pendência fecha quando a etapa muda para uma que não é de pendência (PRM-R48)."""
    n = {"m16": 0, "fechadas": 0}
    hoje = CAL.dia(app.agora())
    mapa = app.param("negocio.mapa_etapas")
    for p in app.repo.listar("pendencia"):
        if p.get("resolvida_em"):
            continue
        neg = app.repo.obter("negocio", p["deal_id"]) or {}
        if p.get("etapa_na_abertura") and neg.get("etapa") != p["etapa_na_abertura"] and mapa.get(neg.get("etapa")) != "precisa_de_voce":
            app.repo.atualizar("pendencia", p["pendencia_id"], {"resolvida_em": app.agora_iso(), "resolvida_por": "sistema"}); n["fechadas"] += 1
            continue
        if not p.get("aviso_m16_em") and (hoje - CAL.dia(p["aberta_em"])).days > app.param("negocio.alerta_pendencia_parceiro_dias"):
            app.repo.atualizar("pendencia", p["pendencia_id"], {"aviso_m16_em": app.agora_iso()})
            regs = [r for r in app.repo.listar("registro") if r.get("deal_id") == p["deal_id"]]
            nome = regs[0].get("razao_social") if regs else (neg.get("cnpj_mascara") or "empresa")
            esc = neg.get("master_id") or neg.get("parceiro_id")
            for u in NT.titulares(app, esc) + ([regs[0]["usuario_id"]] if regs and regs[0].get("usuario_id") else []):
                NT.avisar_usuario(app, u, "M-16", "pede_voce", "empresas/" + ref(app, neg), chave="M-16|" + p["pendencia_id"], razao_social=nome,
                                  pendencia=p.get("texto") or TIPOS_PENDENCIA[p["tipo"]])
            NT.alertar_save(app, "daniela", "Pendência do parceiro há mais de 7 dias", "Negócio %s esperando: %s." % (p["deal_id"], TIPOS_PENDENCIA[p["tipo"]]),
                            chave="pend7|" + p["pendencia_id"])
            n["m16"] += 1
    return n
