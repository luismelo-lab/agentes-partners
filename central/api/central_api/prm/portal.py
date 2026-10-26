"""Face do parceiro (05 §2.1 e §3): Início, Empresas (registros + negócios juntos), ficha da empresa, consulta de Lucro
Real dentro do fluxo Registrar (uma digitação do CNPJ) e pedido de dossiê da esteira. Tudo filtrado pelo escopo do ator."""
import time

from .. import esteira, regime
from . import calendario as CAL
from . import checagem as CHK
from . import demandas as DM
from . import extrato as EX
from . import negocios as NG
from . import nivel as NV
from . import notificacoes as NT
from . import registro as RG
from .erros import Conflito, Invalido, NaoEncontrado
from .identidade import exigir, ve
from .textos import texto as T

FINAIS_REG = RG.FINAIS


def _nomes(app, ator):
    """deal_id → razão social digitada no registro (o espelho local não guarda nome de empresa, 03 §4.1)."""
    return {r["deal_id"]: r.get("razao_social") for r in app.repo.listar("registro") if r.get("deal_id") and ve(ator, r)}


def _registros(app, ator):
    return [r for r in app.repo.listar("registro") if ve(ator, r) and r["estado"] != "rascunho"]


def empresas(app, ator, consultor=None):
    exigir(ator, "ver_registros")
    regs = _registros(app, ator)
    negs = NG.do_ator(app, ator)
    por_deal = {r["deal_id"]: r for r in regs if r.get("deal_id")}
    itens = []
    for r in regs:
        v = RG.visao_parceiro(app, r)
        n = app.repo.obter("negocio", r["deal_id"]) if r.get("deal_id") else None
        if n:
            vn = NG.visao_parceiro(app, n, r)
            aba = "precisa_de_voce" if vn["estado"] == "precisa_de_voce" else ("encerradas" if vn["estado"] == "encerrado" else "andamento")
            item = {"ref": r["ref"], "tipo": "empresa", "nome": r.get("razao_social"), "cnpj_mascara": r.get("cnpj_mascara"), "chip": vn["chip"], "rotulo": vn["rotulo"],
                    "proximo_passo": vn["proximo_passo"], "com": vn["com"], "desde": vn["desde"], "aba": aba, "registro": v["rotulo"], "ordem": vn.get("desde_iso") or ""}
        else:
            e = r["estado"]
            aba = "precisa_de_voce" if e == "aguardando_parceiro" else ("encerradas" if e in FINAIS_REG else "registros")
            item = {"ref": r["ref"], "tipo": "registro", "nome": r.get("razao_social"), "cnpj_mascara": r.get("cnpj_mascara"), "chip": v["chip"], "rotulo": v["rotulo"],
                    "proximo_passo": v["mensagem"], "com": "Você" if e == "aguardando_parceiro" else "Save", "desde": CAL.fmt_data(r.get("atualizado_em") or r["carimbo"]),
                    "aba": aba, "registro": v["rotulo"], "ordem": r.get("atualizado_em") or r["carimbo"]}
        item["usuario_id"] = r.get("usuario_id")
        itens.append(item)
    for n in negs:
        if n["deal_id"] in por_deal:
            continue
        vn = NG.visao_parceiro(app, n)
        aba = "precisa_de_voce" if vn["estado"] == "precisa_de_voce" else ("encerradas" if vn["estado"] == "encerrado" else "andamento")
        itens.append({"ref": vn["ref"], "tipo": "negocio", "nome": n.get("empresa_nome") or "Empresa indicada", "cnpj_mascara": n.get("cnpj_mascara"), "chip": vn["chip"],
                      "rotulo": vn["rotulo"], "proximo_passo": vn["proximo_passo"], "com": vn["com"], "desde": vn["desde"], "aba": aba, "registro": None,
                      "ordem": vn.get("desde_iso") or "", "usuario_id": None, "consultor_parceiro_id": n.get("parceiro_id") if n.get("master_id") else None})
    if consultor and ator.papel == "titular":
        u = app.repo.obter("usuario_parceiro", consultor) or {}
        itens = [i for i in itens if i.get("usuario_id") == consultor or (u.get("consultor_parceiro_id") and i.get("consultor_parceiro_id") == u["consultor_parceiro_id"])]
    itens.sort(key=lambda i: i["ordem"] or "", reverse=True)  # mais recente primeiro...
    itens.sort(key=lambda i: i["aba"] != "precisa_de_voce")     # ...com "Precisa de você" no topo (ordenação estável)
    abas = {a: sum(1 for i in itens if i["aba"] == a) for a in ("precisa_de_voce", "andamento", "registros", "encerradas")}
    app.acesso(ator, "empresas", "listar")
    equipe = [{"id": u["usuario_id"], "nome": u.get("nome")} for u in app.repo.listar("usuario_parceiro", parceiro_id=ator.parceiro_id, papel="consultor")] if ator.papel == "titular" else []
    return {"itens": itens, "abas": abas, "equipe": equipe}


def ficha(app, ator, ref):
    exigir(ator, "ver_registros")
    reg = next((r for r in app.repo.listar("registro", ref=ref) if ve(ator, r)), None)
    neg = None
    if reg and reg.get("deal_id"):
        neg = app.repo.obter("negocio", reg["deal_id"])
    if not reg:
        neg = NG.por_ref(app, ator, ref)
        if not neg:
            app.acesso(ator, "ficha", "ler", ref, "negado")
            raise NaoEncontrado("Esta empresa não está na sua lista.")
        reg = next((r for r in app.repo.listar("registro") if r.get("deal_id") == neg["deal_id"] and ve(ator, r)), None)
    out = {"ref": ref, "nome": (reg or {}).get("razao_social") or (neg or {}).get("empresa_nome") or "Empresa indicada",
           "cnpj_mascara": (reg or neg or {}).get("cnpj_mascara"), "registro": RG.visao_parceiro(app, reg) if reg else None,
           "negocio": NG.visao_parceiro(app, neg, reg) if neg else None}
    out["pedidos"] = [DM.visao_parceiro(app, d) for d in DM.do_ator(app, ator) if (d.get("empresa") or {}).get("ref") in {ref, (reg or {}).get("ref"),
                                                                                                                    NG.ref(app, neg) if neg else None}]
    out["extrato"] = []
    if ator.papel == "titular" and neg:
        out["extrato"] = [EX.visao_parceiro(app, x, out["nome"]) for x in EX.linhas(app) if x["deal_id"] == neg["deal_id"] and x["escritorio"] == ator.parceiro_id]
    out["dossie"] = None
    if reg and reg.get("dossie_id"):
        p = esteira._ler(reg["dossie_id"])
        if p:
            out["dossie"] = esteira.visao_parceiro(p)
    out["pode_pedir_dossie"] = bool(reg) and not out["dossie"] and reg["estado"] in ("em_analise", "aprovado", "prorrogado") and ator.tipo == "parceiro"
    app.acesso(ator, "ficha", "ler", ref)
    return out


# ---------------------------------------------------------------- P-3: CNPJ uma vez → Receita + regime → registrar / dossiê
def checar(app, ator, cnpj):
    """Checagem em tempo real, só do que é seguro mostrar (05 §0 item 4): formato, dígito e 'já é seu'.
    Nunca consulta a carteira da Save para o parceiro: o que não é dele volta como 'ok_formato'."""
    exigir(ator, "consultar_empresa")
    from cnpj import cnpj_valido, normalizar_cnpj
    c = normalizar_cnpj(cnpj or "")
    if len(c) < 14:
        return {"estado": "incompleto"}
    if not cnpj_valido(c):
        return {"estado": "erro_formato", "mensagem": "Este CNPJ não confere. Revise os números."}
    chk = CHK.classificar(app, c, ator.parceiro_id, ator.usuario_id)
    if chk["resultado"] in ("proprio_usuario", "proprio_escritorio"):
        return {"estado": "ja_e_seu", **RG._resposta_propria(app, chk)}
    return {"estado": "ok_formato"}


def consultar(app, ator, cnpjs, proprio_ok=False):
    """Consulta de Lucro Real (regime.py) com teto persistente (L4), trilha só com HMAC (L3/L16) e a regra única de
    cliente protegido (L14). Mesmo piso de tempo da resposta para todo resultado. `proprio_ok`: a empresa já é do
    parceiro (dossiê de um registro dele), então consulta mesmo assim."""
    exigir(ator, "consultar_empresa")
    inicio = time.monotonic()
    try:
        return _consultar(app, ator, cnpjs, proprio_ok)
    finally:
        RG._esperar_piso(app, inicio)


def _consultar(app, ator, cnpjs, proprio_ok=False):
    if isinstance(cnpjs, str):
        cnpjs = [cnpjs]
    if not isinstance(cnpjs, list) or not cnpjs:
        raise Invalido("Informe ao menos um CNPJ.")
    lista = []
    for c in cnpjs:
        c = app.cnpj(c) if isinstance(c, str) else ""
        if c and c not in lista:
            lista.append(c)
    if len(lista) > app.param("consulta.lote_max"):
        raise Invalido("No máximo %d CNPJs por consulta." % app.param("consulta.lote_max"))
    quem = ator.usuario_id or ator.rotulo()
    hoje = CAL.dia(app.agora()).isoformat()
    protegido = CHK.protecao_para_consulta(app, ator.parceiro_id, ator.usuario_id)
    out = []
    for c in lista:
        ja = checar(app, ator, c) if ator.tipo == "parceiro" and not proprio_ok else {"estado": "ok_formato"}
        if ja["estado"] == "ja_e_seu":
            out.append({"cnpj_mascara": app.mascara(c), "ja_e_seu": ja}); continue
        guardada = esteira.consulta_guardada(quem, c)
        if guardada and protegido(c) is False:
            r = guardada
        elif app.repo.contar("consulta|%s|%s" % (quem, hoje)) > app.param("consulta.teto_diario_usuario"):
            r = regime.neutra(c, "teto_diario")
        else:
            r = regime.consultar(c, protegido=protegido)
            if r.get("faixa") not in ("invalido", "indisponivel"):
                esteira.registrar_consulta(quem, r)
        if r.get("_motivo") in ("negocio_ativo", "registro_ou_negocio_de_outro_parceiro", "teto_diario"):
            RG._contar_neutra(app, ator, ator.usuario_id, hoje)
        app.repo.inserir("consulta", {"quando": app.agora_iso(), "usuario_id": ator.usuario_id, "conta_time": None if ator.tipo == "parceiro" else ator.rotulo(),
                                      "cnpj_hmac": app.hmac_cnpj(c), "faixa": r.get("faixa"), "motivo_interno": r.get("_motivo")})
        pub = regime.publico(r)
        pub.pop("cnpj", None)
        emp = pub.get("empresa") or {}
        ativa = (emp.get("situacao") or "").lower() in ("ativa", "")
        neutra = r.get("_motivo") is not None
        cnae = ((r.get("perfil") or {}).get("cnae") or {})
        pub.update(cnpj_mascara=app.mascara(c), neutra=neutra, situacao_ativa=ativa if emp else None, cnae=cnae.get("descricao"),
                   pode_registrar=(not emp) or ativa, perfil=None)
        if neutra:
            pub["titulo"] = T("M-00")
        out.append(pub)
    app.acesso(ator, "registrar", "consultar", "%d cnpj" % len(lista))
    return {"resultados": out}


def pedir_dossie(app, ator, ref):
    exigir(ator, "pedir_dossie")
    reg = next((r for r in app.repo.listar("registro", ref=ref) if ve(ator, r)), None)
    if not reg:
        raise NaoEncontrado()
    if reg.get("dossie_id"):
        p = esteira._ler(reg["dossie_id"])
        if p:
            return esteira.visao_parceiro(p)
    quem = ator.usuario_id
    r = esteira.consulta_guardada(quem, reg["cnpj"])
    if not r:
        res = consultar(app, ator, [reg["cnpj"]], proprio_ok=True)["resultados"][0]
        if res.get("neutra") or not res.get("empresa"):
            raise Conflito(T("M-00"), codigo="M-00")
        r = esteira.consulta_guardada(quem, reg["cnpj"])
    if not r:
        raise Conflito(T("M-00"), codigo="M-00")
    try:
        p = esteira.solicitar(reg["cnpj"], quem, r)
    except esteira.Recusa as e:
        raise Conflito(str(e) if str(e) != esteira.NA.MSG_NEUTRA else T("M-00"), codigo="M-00")
    app.repo.atualizar("registro", reg["registro_id"], {"dossie_id": p["id"]})
    app.acesso(ator, "dossie", "pedir", reg["ref"])
    return esteira.visao_parceiro(p)


def arquivo_dossie(app, ator, ref):
    reg = next((r for r in app.repo.listar("registro", ref=ref) if ve(ator, r)), None)
    if not reg or not reg.get("dossie_id"):
        raise NaoEncontrado()
    p = esteira._ler(reg["dossie_id"])
    arq = esteira.arquivo_do_parceiro(reg["dossie_id"], p["parceiro"]) if p else None
    app.acesso(ator, "dossie", "baixar", reg["ref"], "ok" if arq else "erro")
    return arq, reg["dossie_id"]


# ---------------------------------------------------------------- P-1 Início
def inicio(app, ator):
    emp = empresas(app, ator)["itens"]
    regs = _registros(app, ator)
    dems = [d for d in DM.do_ator(app, ator)]
    avisos = NT.do_ator(app, ator)
    pede = []
    for i in emp:
        if i["aba"] == "precisa_de_voce":
            pede.append({"titulo": i["nome"] or i["cnpj_mascara"], "texto": i["proximo_passo"], "go": "empresas/" + i["ref"], "acao": "Abrir empresa"})
    for d in dems:
        if d["estado"] == "aguardando_parceiro":
            pede.append({"titulo": "Pedido %s" % d["demanda_id"], "texto": "A Save precisa de uma informação sua.", "go": "pedidos/" + d["ref"], "acao": "Responder"})
    for r in regs:
        v = RG.visao_parceiro(app, r)
        if v["pode_prorrogar"]:
            pede.append({"titulo": r.get("razao_social") or r["cnpj_mascara"], "texto": "Registro vence em %d dias. Se houve avanço, peça a prorrogação." % v["dias_para_vencer"],
                         "go": "empresas/" + r["ref"], "acao": "Pedir prorrogação"})
    nf = 0
    if ator.papel == "titular":
        nf = sum(1 for x in EX.linhas(app) if x["escritorio"] == ator.parceiro_id and x["estado"] in ("liberado", "aguardando_nf"))
        if nf:
            pede.append({"titulo": "Nota fiscal", "texto": "%d linha(s) do extrato aguardam a sua NF." % nf, "go": "extrato", "acao": "Ver extrato"})
    validos = sum(1 for r in regs if r["estado"] in ("aprovado", "prorrogado", "convertido", "protegido_cliente"))
    respostas = sum(1 for n in avisos if n["tipo"] == "resposta" and not n["lido"])
    a_vencer = [RG.visao_parceiro(app, r) for r in regs if r["estado"] in ("aprovado", "prorrogado", "convertido")]
    a_vencer = sorted([v for v in a_vencer if v["dias_para_vencer"] is not None and v["dias_para_vencer"] <= 30], key=lambda v: v["dias_para_vencer"])
    corte = CAL.iso(app.agora() - __import__("datetime").timedelta(days=7))
    mudou = [{"titulo": n["assunto"], "texto": n["resumo"], "quando": CAL.fmt(n["criado_em"]), "novo": not n["lido"], "go": (n["acoes"] or [{}])[0].get("go")}
             for n in avisos if n["criado_em"] >= corte][:5]
    u = app.repo.obter("usuario_parceiro", ator.usuario_id) or {}
    passos = [{"texto": "Registrar a primeira empresa", "feito": bool(regs)},
              {"texto": "Abrir a ficha de uma empresa indicada", "feito": bool(app.repo.listar("acesso_log", usuario_id=ator.usuario_id, tela="ficha"))},
              {"texto": "Fazer um pedido à Save por aqui", "feito": bool(dems)},
              {"texto": "Conhecer a Biblioteca", "feito": bool(app.repo.listar("acesso_log", usuario_id=ator.usuario_id, tela="biblioteca"))}]
    app.acesso(ator, "inicio", "ler")
    return {"nome": ator.nome, "pede_voce": pede[:3], "pede_voce_total": len(pede),
            "kpis": {"pedem_voce": len(pede), "em_andamento": sum(1 for i in emp if i["aba"] == "andamento"), "registros_validos": validos, "respostas_novas": respostas,
                     "empresas": len(emp)},
            "mudou": mudou, "a_vencer": a_vencer[:5], "nivel": {"selo": "Em teste", "etapa": NV.visao_parceiro(app, ator)["etapa"]},
            "primeiros_passos": None if u.get("passos_dispensados") or all(p["feito"] for p in passos) else passos,
            "avisos_nao_lidos": sum(1 for n in avisos if not n["lido"]), "nf_pendentes": nf,
            "precisa_empresas": sum(1 for i in emp if i["aba"] == "precisa_de_voce")}


def biblioteca(app, ator):
    exigir(ator, "ver_biblioteca")
    app.acesso(ator, "biblioteca", "ler")
    pronto = [("Recuperação tributária", "Teses de PIS/COFINS e exclusões da base, com análise técnica antes de qualquer pedido."),
              ("Gestão de Passivo", "Transação, CND e dívida ativa, com pré-análise jurídica."),
              ("Planejamento e reforma", "Leitura da reforma tributária e dos saldos credores para a empresa."),
              ("Estruturação patrimonial", "Holding e sucessão, conduzidas pelo jurídico."),
              ("Gestão de Contas e antecipação", "Cobrança, antecipação de recebíveis e FIDC pela Save Invest."),
              ("Tax internacional", "Preço de transferência, remessas e comércio exterior.")]
    descoberta = ["Crédito Internacional", "Maquila", "Captação de capital", "Home equity", "Turnkey"]
    return {"prontos": [{"nome": n, "texto": t, "estado": "pronto"} for n, t in pronto],
            "descoberta": [{"nome": n, "estado": "descoberta", "texto": "Produto em estudo pela Save. Ainda não há material, condição nem simulação. Se o cliente perguntar, registre o interesse."}
                           for n in descoberta],
            "aviso_cobranded": "A peça identifica que você é parceiro remunerado da Save (CONAR)."}
