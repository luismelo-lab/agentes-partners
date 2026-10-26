"""Rotas HTTP do PRM (contrato em docs/prm/v2/06-contrato-api.md). Sem dependência de transporte: recebe método,
caminho, cabeçalhos e corpo (dict já lido) e devolve (status, corpo). function_app.py (Azure) e dev_server.py (local)
só fazem a ponte, com a mesma lógica (L1: nada de rota fora do token).

Ordem em toda requisição: autenticar (token ou login simulado só em localhost) → face da rota → papel (ação) → escopo
da linha (404 fora do escopo) → regra → trilha de acesso. Erro inesperado devolve 500 com texto neutro (sem rastro).
"""
import logging, re

from . import acompanhamento as AC
from . import canal as CN
from . import catalogo as CAT
from . import decisao as DC
from . import demandas as DM
from . import extrato as EX
from . import nivel as NV
from . import notificacoes as NT
from . import portal as PT
from . import registro as RG
from .app import criar_de_ambiente
from .erros import Invalido, NaoEncontrado, PRMErro
from .identidade import autenticar, exigir, exigir_face, login_simulado_ativo, ve

log = logging.getLogger("central_api.prm")
_APP = {}
REF = r"(?P<ref>[0-9a-f]{16})"


def definir_app(app):
    _APP["app"] = app


def obter_app():
    if "app" not in _APP:
        _APP["app"] = criar_de_ambiente()
    return _APP["app"]


# ---------------------------------------------------------------- handlers do parceiro
def _eu(app, a, c, m):
    out = a.publico_dict()
    if a.tipo == "parceiro":
        u = app.repo.obter("usuario_parceiro", a.usuario_id) or {}
        par = app.repo.obter("parceiro", a.parceiro_id) or {}
        out.update(escritorio=par.get("nome_exibicao"), termos_pendentes=u.get("termos_versao") != app.param("termos_uso.versao"),
                   versao_termos=app.param("termos_uso.versao"), primeira_declaracao=not u.get("declarou_sem_promessa_em"))
    out["avisos_nao_lidos"] = sum(1 for n in NT.do_ator(app, a) if not n["lido"])
    return 200, out


def _aceitar_termos(app, a, c, m):
    if c.get("versao") != app.param("termos_uso.versao") or c.get("aceito") is not True:
        raise Invalido("Marque o aceite dos termos de uso e do aviso de privacidade.", campos={"aceito": "Marque o aceite."})
    app.repo.atualizar("usuario_parceiro", a.usuario_id, {"termos_versao": c["versao"], "termos_aceitos_em": app.agora_iso()})
    app.repo.inserir("aceite", {"usuario_id": a.usuario_id, "versao": c["versao"], "aceito_em": app.agora_iso()})
    return 200, {"ok": True}


def _exigir_termos(app, a):
    """PRM-R107: sem o aceite da versão vigente, só o /eu e o próprio aceite funcionam."""
    if a.tipo == "parceiro":
        u = app.repo.obter("usuario_parceiro", a.usuario_id) or {}
        if u.get("termos_versao") != app.param("termos_uso.versao"):
            raise PRMErro_termos()


class PRMErro_termos(PRMErro):
    status = 428

    def __init__(self):
        super().__init__("Aceite os termos de uso para continuar.", codigo="termos")


def _ref_extrato(app, a, ref):
    for x in EX.linhas(app):
        if app.ref_estavel("ext", x["linha_id"]) == ref and x["escritorio"] == a.parceiro_id:
            return x
    app.acesso(a, "extrato", "ler", ref, "negado")
    raise NaoEncontrado()


def _demanda(app, a, ref):
    return app.obter_no_escopo("demanda", ref, a, ve)


def _registro(app, a, ref):
    return app.obter_no_escopo("registro", ref, a, ve)


def _pedidos_novo(app, a, c, m):
    return 201, DM.abrir(app, a, c)


def _extrato(app, a, c, m):
    nomes = {r["deal_id"]: r.get("razao_social") for r in app.repo.listar("registro", parceiro_id=a.parceiro_id) if r.get("deal_id")}
    app.acesso(a, "extrato", "ler")
    return 200, EX.do_titular(app, a, nomes)


def _contestar(app, a, c, m):
    x = _ref_extrato(app, a, m["ref"])
    return 200, EX.contestar(app, a, x, c.get("motivo"))


def _avisos(app, a, c, m):
    xs = NT.do_ator(app, a)
    return 200, {"itens": [{"id": n["id"], "titulo": n["assunto"], "texto": n["resumo"], "tipo": n["tipo"], "quando": n["criado_em"], "lido": n["lido"],
                            "go": (n.get("acoes") or [{}])[0].get("go")} for n in xs[:100]]}


def _arquivo(app, a, c, m):
    arq, pid = PT.arquivo_dossie(app, a, m["ref"])
    if not arq:
        return 503, {"erro": "Não conseguimos gerar o Word agora. Tente de novo em instantes."}
    return 200, {"_arquivo": arq, "_nome": "dossie-%s.docx" % pid, "_tipo": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}


def _dispensar(app, a, c, m):
    app.repo.atualizar("usuario_parceiro", a.usuario_id, {"passos_dispensados": True})
    return 200, {"ok": True}


P = [  # (método, padrão, função, face, exige_termos)
    ("GET", r"/api/prm/eu", _eu, None, False),
    ("POST", r"/api/prm/parceiro/termos/aceitar", _aceitar_termos, "parceiro", False),
    ("GET", r"/api/prm/parceiro/inicio", lambda app, a, c, m: (200, PT.inicio(app, a)), "parceiro", True),
    ("POST", r"/api/prm/parceiro/primeiros-passos/dispensar", _dispensar, "parceiro", True),
    ("GET", r"/api/prm/parceiro/empresas", lambda app, a, c, m: (200, PT.empresas(app, a, c.get("consultor"))), "parceiro", True),
    ("GET", r"/api/prm/parceiro/empresas/" + REF, lambda app, a, c, m: (200, PT.ficha(app, a, m["ref"])), "parceiro", True),
    ("POST", r"/api/prm/parceiro/empresas/" + REF + "/dossie", lambda app, a, c, m: (200, PT.pedir_dossie(app, a, m["ref"])), "parceiro", True),
    ("GET", r"/api/prm/parceiro/empresas/" + REF + "/dossie/arquivo", _arquivo, "parceiro", True),
    ("POST", r"/api/prm/parceiro/empresa/checar", lambda app, a, c, m: (200, PT.checar(app, a, c.get("cnpj"))), "parceiro", True),
    ("POST", r"/api/prm/parceiro/empresa/consultar", lambda app, a, c, m: (200, PT.consultar(app, a, c.get("cnpjs") or c.get("cnpj"))), "parceiro", True),
    ("POST", r"/api/prm/parceiro/registros", lambda app, a, c, m: RG.registrar(app, a, c), "parceiro", True),
    ("POST", r"/api/prm/parceiro/registros/" + REF + "/cancelar", lambda app, a, c, m: (200, RG.visao_parceiro(app, RG.cancelar(app, a, _registro(app, a, m["ref"])))), "parceiro", True),
    ("POST", r"/api/prm/parceiro/registros/" + REF + "/prorrogacao", lambda app, a, c, m: (200, {"mensagem": RG.pedir_prorrogacao(app, a, _registro(app, a, m["ref"]), c.get("fato"))}), "parceiro", True),
    ("POST", r"/api/prm/parceiro/registros/" + REF + "/complemento", lambda app, a, c, m: (200, RG.visao_parceiro(app, RG.responder_complemento(app, a, _registro(app, a, m["ref"]), c.get("resposta")))), "parceiro", True),
    ("GET", r"/api/prm/parceiro/tipos-pedido", lambda app, a, c, m: (200, {"tipos": CAT.para_parceiro(), "aviso_anexo": RG.T("M-34")}), "parceiro", True),
    ("GET", r"/api/prm/parceiro/pedidos", lambda app, a, c, m: (200, {"itens": [DM.visao_parceiro(app, d) for d in DM.do_ator(app, a)]}), "parceiro", True),
    ("POST", r"/api/prm/parceiro/pedidos", _pedidos_novo, "parceiro", True),
    ("GET", r"/api/prm/parceiro/pedidos/" + REF, lambda app, a, c, m: (200, DM.visao_parceiro(app, _demanda(app, a, m["ref"]))), "parceiro", True),
    ("POST", r"/api/prm/parceiro/pedidos/" + REF + "/concluir", lambda app, a, c, m: (200, DM.visao_parceiro(app, DM.concluir(app, a, _demanda(app, a, m["ref"])))), "parceiro", True),
    ("POST", r"/api/prm/parceiro/pedidos/" + REF + "/reabrir", lambda app, a, c, m: (200, DM.visao_parceiro(app, DM.reabrir(app, a, _demanda(app, a, m["ref"]), c.get("texto") or ""))), "parceiro", True),
    ("POST", r"/api/prm/parceiro/pedidos/" + REF + "/complemento", lambda app, a, c, m: (200, DM.visao_parceiro(app, DM.complementar(app, a, _demanda(app, a, m["ref"]), c.get("texto")))), "parceiro", True),
    ("GET", r"/api/prm/parceiro/extrato", _extrato, "parceiro", True),
    ("POST", r"/api/prm/parceiro/extrato/" + REF + "/contestar", _contestar, "parceiro", True),
    ("GET", r"/api/prm/parceiro/avisos", _avisos, "parceiro", False),
    ("POST", r"/api/prm/parceiro/avisos/lidos", lambda app, a, c, m: (200, {"marcados": NT.marcar_lidas(app, a, c.get("ids"))}), "parceiro", False),
    ("GET", r"/api/prm/parceiro/nivel", lambda app, a, c, m: (exigir(a, "ver_nivel") and 200, NV.visao_parceiro(app, a)), "parceiro", True),
    ("GET", r"/api/prm/parceiro/biblioteca", lambda app, a, c, m: (200, PT.biblioteca(app, a)), "parceiro", True),
    # acompanhamento de negócios e painel de vendas (PRM-R113 a R118)
    ("GET", r"/api/prm/parceiro/negocios", lambda app, a, c, m: (200, AC.listar(app, a, c)), "parceiro", True),
    ("GET", r"/api/prm/parceiro/negocios/" + REF, lambda app, a, c, m: (200, AC.ficha_parceiro(app, a, m["ref"])), "parceiro", True),
    ("GET", r"/api/prm/parceiro/painel", lambda app, a, c, m: (200, AC.painel_parceiro(app, a, c)), "parceiro", True),
    # ------------------------------------------------------------ Save (seção Canal)
    ("GET", r"/api/prm/save/canal", lambda app, a, c, m: (200, CN.visao(app, a)), "save", False),
    ("GET", r"/api/prm/save/registros", lambda app, a, c, m: (200, CN.registros(app, a, c.get("estado"))), "save", False),
    ("GET", r"/api/prm/save/registros/(?P<id>R-\d{4}-\d{6})", lambda app, a, c, m: (200, RG.visao_save(app, _obter_save(app, a, "registro", m["id"], "ver_registros"))), "save", False),
    ("POST", r"/api/prm/save/registros", lambda app, a, c, m: RG.registrar(app, a, c, em_nome_de=c.get("em_nome_de")), "save", False),
    ("GET", r"/api/prm/save/conflitos", lambda app, a, c, m: (200, CN.conflitos(app, a)), "save", False),
    ("GET", r"/api/prm/save/demandas", lambda app, a, c, m: (200, CN.demandas(app, a)), "save", False),
    ("POST", r"/api/prm/save/demandas", lambda app, a, c, m: (201, DM.abrir(app, a, c, em_nome_de=c.get("em_nome_de"))), "save", False),
    ("GET", r"/api/prm/save/extratos", lambda app, a, c, m: (200, CN.extratos(app, a)), "save", False),
    ("GET", r"/api/prm/save/dossies", lambda app, a, c, m: (200, CN.dossies(app, a)), "save", False),
    ("GET", r"/api/prm/save/acessos", lambda app, a, c, m: (200, CN.acessos(app, a)), "save", False),
    ("GET", r"/api/prm/save/niveis", lambda app, a, c, m: (200, CN.niveis(app, a)), "save", False),
    ("GET", r"/api/prm/save/parametros", lambda app, a, c, m: (200, CN.parametros(app, a)), "save", False),
    ("GET", r"/api/prm/save/dashboard", lambda app, a, c, m: (200, AC.dashboard_canal(app, a, c)), "save", False),
    ("GET", r"/api/prm/save/negocios", lambda app, a, c, m: (200, AC.listar(app, a, c)), "save", False),
    ("GET", r"/api/prm/save/negocios/(?P<id>\d{1,20})", lambda app, a, c, m: (200, AC.ficha_save(app, a, m["id"])), "save", False),
    ("GET", r"/api/prm/save/avisos", _avisos, "save", False),
    ("POST", r"/api/prm/save/avisos/lidos", lambda app, a, c, m: (200, {"marcados": NT.marcar_lidas(app, a, c.get("ids"))}), "save", False),
    ("POST", r"/api/prm/save/decidir", lambda app, a, c, m: (200, DC.decidir(app, a, c)), "save", False),
    ("GET", r"/api/prm/save/trilha", lambda app, a, c, m: (exigir(a, "ver_trilha") and 200, {"itens": DC.trilha(app, c.get("objeto"), c.get("id"))}), "save", False),
    ("POST", r"/api/prm/save/rotina", lambda app, a, c, m: (200, rotina(app, a)), "save", False),
]
ROTAS = [(mt, re.compile("^" + pat + "$"), fn, face, termos) for mt, pat, fn, face, termos in P]


def _obter_save(app, a, tabela, ident, acao):
    exigir(a, acao)
    x = app.repo.obter(tabela, ident)
    if x is None:
        raise NaoEncontrado()
    app.acesso(a, tabela, "ler", ident)
    return x


def rotina(app, a):
    """Rotina diária (06h00 na Fase 2, Function com timer; aqui também por botão do Luis no local)."""
    exigir(a, "rodar_rotina")
    from . import negocios as NG
    return {"registros": RG.rotina(app), "negocios": NG.rotina(app), "demandas": DM.rotina(app)}


def _ip(cab):
    return (cab.get("X-Forwarded-For") or cab.get("X-PRM-IP-Local") or "").split(",")[0].strip() or None


def despachar(metodo, caminho, cabecalhos, corpo=None, consulta=None, app=None):
    """(status, corpo). `corpo` é o JSON já lido (POST); `consulta` é o dict da query string (GET)."""
    app = app or obter_app()
    caminho = caminho.split("?")[0].rstrip("/") or "/"
    if caminho == "/api/prm/dev/usuarios":
        if not login_simulado_ativo(cabecalhos):
            return 404, {"erro": "rota não encontrada"}
        from . import fixtures
        return 200, {"usuarios": app.lista_usuarios_teste(), "cnpjs_de_teste": fixtures.cenarios() if _APP.get("fixtures") else []}
    alvo = None
    for mt, rx, fn, face, termos in ROTAS:
        mm = rx.match(caminho)
        if mm and mt == metodo:
            alvo = (fn, face, termos, mm.groupdict())
            break
        if mm:
            alvo = alvo or "metodo"
    if alvo is None:
        return 404, {"erro": "rota não encontrada"}
    if alvo == "metodo":
        return 405, {"erro": "método não permitido"}
    fn, face, termos, grupos = alvo
    ator = None
    try:
        ator = autenticar(app, cabecalhos)
        if face:
            exigir_face(ator, face)
        if termos:
            _exigir_termos(app, ator)
        c = corpo if metodo == "POST" else (consulta or {})
        if not isinstance(c, dict):
            raise Invalido("Corpo inválido.")
        st, out = fn(app, ator, c, grupos)
        if metodo == "POST":
            app.acesso(ator, caminho.rsplit("/", 2)[-2] if caminho.count("/") > 4 else caminho.rsplit("/", 1)[-1], "gravar", grupos.get("ref") or grupos.get("id"),
                       ip=_ip(cabecalhos))
        return st, out
    except PRMErro as e:
        if ator is not None and e.status in (403, 404):
            app.acesso(ator, caminho.rsplit("/", 1)[-1][:40], metodo, grupos.get("ref") or grupos.get("id"), "negado", ip=_ip(cabecalhos))
        if e.status == 401:
            log.info("401 %s", caminho)
        return e.status, e.corpo()
    except Exception as e:  # noqa: BLE001  resposta neutra, sem rastro nem dado de cliente
        log.exception("erro interno em %s: %s", caminho, type(e).__name__)
        if ator is not None:
            app.acesso(ator, caminho.rsplit("/", 1)[-1][:40], metodo, None, "erro")
        return 500, {"erro": "Não conseguimos carregar esta parte agora. Tente de novo em instantes."}
