"""Autorização do PRM em 3 camadas (04-ti-arquitetura.md §2.1), fechando L2:

1. Token (token.py, já pronto): assinatura, iss, aud, tid, validade, escopo. Na Fase 2 o portal do parceiro usa outro
   registro de aplicativo (PRM_API_CLIENT_ID, escopo Prm.Acesso): as duas configurações são aceitas e cada rota exige a
   sua (`face`). Identidade é o `oid`, nunca o e-mail.
2. Papel + escopo: Save pelo papel do Entra (Partners.*); parceiro pelo `oid` na tabela usuario_parceiro
   (titular vê o escritório; consultor vê só o que é dele). Matriz de ações = 02 §2.2.
3. Dono da linha: `ve(ator, linha)`; fora do escopo o serviço responde 404 (PRM-R02), nunca 403.

Login simulado (só o servidor local, só localhost, nunca na Azure): cabeçalho X-PRM-Dev-Usuario com o id de um usuário
de teste. Três travas: PRM_LOGIN_SIMULADO=1, Host localhost/127.0.0.1 e ausência de WEBSITE_INSTANCE_ID (variável que
toda Function na Azure tem).
"""
import os
from dataclasses import dataclass, field

from .. import permissoes as P
from ..token import Chaves, Config, TokenInvalido, extrair_bearer, validar
from .erros import NaoAutenticado, SemPermissao

FINANCEIRO, CONTRATOS, PORTAL = "Partners.Financeiro", "Partners.Contratos", "Parceiro.Portal"
PAPEL_SAVE = {P.GESTOR: "luis", P.MASTERS: "daniela", P.BDR: "jenifer", P.TECNICA: "geovana", FINANCEIRO: "financeiro",
              CONTRATOS: "contratos", P.LEITURA: "leitura"}
ORDEM_SAVE = (P.GESTOR, P.MASTERS, FINANCEIRO, CONTRATOS, P.BDR, P.TECNICA, P.LEITURA)
PAPEIS_PARCEIRO = ("titular", "consultor")
SAVE = ("luis", "daniela", "jenifer", "geovana", "financeiro", "contratos", "leitura")

# 02 §2.2 (V = ver, A = agir). "master" é atributo do parceiro: o titular de um Master vê também os consultores.
ACOES = {
    "registrar":               {"titular", "consultor", "daniela", "jenifer"},
    "ver_registros":           {"titular", "consultor", "daniela", "jenifer", "geovana", "luis"},
    "decidir_registro":        {"daniela"},
    "enviar_conflito":         {"daniela", "jenifer"},
    "decidir_conflito":        {"luis"},
    "pedir_prorrogacao":       {"titular", "consultor"},
    "decidir_prorrogacao":     {"daniela"},
    "ver_negocios":            {"titular", "consultor", "daniela", "jenifer", "geovana", "luis"},
    "marcar_pendencia":        {"daniela", "jenifer", "geovana"},
    "ver_extrato":             {"titular", "daniela", "financeiro", "contratos", "luis"},
    "registrar_recebimento":   {"financeiro"},
    "aprovar_extrato":         {"financeiro"},
    "contestar_linha":         {"titular"},
    "responder_contestacao":   {"financeiro", "contratos", "luis"},
    "abrir_demanda":           {"titular", "consultor", "daniela"},
    "responder_demanda":       {"daniela", "jenifer", "geovana", "financeiro", "contratos", "luis"},
    "aprovar_chamado":         {"daniela", "luis"},
    "ver_nivel":               {"titular", "consultor", "daniela", "jenifer", "luis"},
    "ver_biblioteca":          {"titular", "consultor", "daniela", "jenifer", "geovana", "luis"},
    "pedir_dossie":            {"titular", "consultor"},
    "aprovar_dossie":          {"daniela", "luis"},
    "ver_canal":               {"daniela", "jenifer", "geovana", "financeiro", "luis"},
    "ver_canal_agregado":      {"daniela", "jenifer", "geovana", "financeiro", "luis", "leitura"},
    "gerir_acessos":           {"daniela", "luis"},
    "ver_trilha":              {"daniela", "luis"},
    "ver_margem":              {"luis", "financeiro"},
    "rodar_rotina":            {"sistema", "luis"},
    "mudar_parametro":         {"luis", "daniela", "financeiro", "jenifer", "contratos"},
    "consultar_empresa":       {"titular", "consultor", "daniela", "jenifer"},
}


@dataclass
class Ator:
    tipo: str                    # parceiro | save | agente
    papel: str                   # titular | consultor | daniela | ... | luis | leitura | sistema
    oid: str = ""
    nome: str = ""
    usuario_id: str = None       # parceiro: U-0001
    parceiro_id: str = None      # parceiro: escritório (P-0001)
    consultor_parceiro_id: str = None
    escritorio_master: bool = False
    face: str = ""               # parceiro | save
    publico: str = "central"
    extras: dict = field(default_factory=dict)

    def rotulo(self):
        """Quem, na trilha: o id do usuário do parceiro, o papel e o oid do time (nunca o e-mail)."""
        if self.tipo == "parceiro":
            return self.usuario_id
        return "%s:%s" % (self.papel, (self.oid or "")[:8] or "local")

    def publico_dict(self):
        return {"tipo": self.tipo, "papel": self.papel, "nome": self.nome, "usuario_id": self.usuario_id, "parceiro_id": self.parceiro_id,
                "face": self.face, "pode": sorted(a for a, ps in ACOES.items() if self.papel in ps)}


def pode(ator, acao):
    return ator.papel in ACOES.get(acao, ())


def exigir(ator, acao, mensagem=None):
    if acao not in ACOES:
        raise SemPermissao("Ação desconhecida.")
    if not pode(ator, acao):
        raise SemPermissao(mensagem or "Seu perfil não permite esta ação.")
    return True


# ---------------------------------------------------------------- camada 3: dono da linha
def ve(ator, linha, campo_parceiro="parceiro_id", campo_usuario="usuario_id"):
    """True se a linha está no escopo do ator. Save vê tudo (o papel já foi conferido); parceiro só o do escritório
    (titular) ou o dele (consultor)."""
    if ator.tipo in ("save", "agente"):
        return True
    if linha.get(campo_parceiro) != ator.parceiro_id:
        return False
    if ator.papel == "titular":
        return True
    return linha.get(campo_usuario) == ator.usuario_id


def ve_negocio(ator, neg):
    """Negócio do espelho do HubSpot: o escritório é master_id (ou o próprio parceiro_id, se for o Master);
    o consultor vê só os ligados ao cadastro dele (consultor_parceiro_id)."""
    if ator.tipo in ("save", "agente"):
        return True
    esc = neg.get("master_id") or neg.get("parceiro_id")
    if esc != ator.parceiro_id:
        return False
    if ator.papel == "titular":
        return True
    return bool(ator.consultor_parceiro_id) and neg.get("parceiro_id") == ator.consultor_parceiro_id


# ---------------------------------------------------------------- camada 1 e 2: quem é
_CFG = {}


def _configs():
    if "lista" not in _CFG:
        lista = []
        try:
            c = Config()
            lista.append(("central", c, Chaves(c.jwks_url)))
        except RuntimeError:
            pass
        if os.environ.get("PRM_API_CLIENT_ID"):
            c = Config(api_client_id=os.environ["PRM_API_CLIENT_ID"], scope=os.environ.get("PRM_SCOPE", "Prm.Acesso"))
            lista.append(("prm", c, Chaves(c.jwks_url)))
        _CFG["lista"] = lista
    return _CFG["lista"]


def configurar(lista):
    """Testes: [(nome, Config, Chaves)]."""
    _CFG["lista"] = lista


def _host_local(cab):
    h = (cab.get("Host") or cab.get("host") or "").lower()
    nome = h.rsplit(":", 1)[0] if not h.startswith("[") else h.split("]")[0] + "]"
    return nome in ("localhost", "127.0.0.1", "[::1]")


def login_simulado_ativo(cab):
    return (os.environ.get("PRM_LOGIN_SIMULADO") == "1" and not os.environ.get("WEBSITE_INSTANCE_ID")
            and _host_local(cab))


def ator_de_usuario(app, usuario, face="parceiro", oid="", publico="central"):
    if usuario.get("estado") not in ("ativo", "ex_parceiro_extrato"):
        raise SemPermissao("Seu acesso ao portal ainda não foi liberado. Fale com o time da Save que atende você.", codigo="sem_acesso")
    par = app.repo.obter("parceiro", usuario["parceiro_id"]) or {}
    return Ator(tipo="parceiro", papel=usuario["papel"], oid=oid or usuario.get("entra_oid") or "", nome=usuario.get("nome", ""),
                usuario_id=usuario["usuario_id"], parceiro_id=usuario["parceiro_id"], consultor_parceiro_id=usuario.get("consultor_parceiro_id"),
                escritorio_master=par.get("tipo") == "master", face=face, publico=publico)


def autenticar(app, cab):
    """Ator da requisição. Levanta NaoAutenticado (401) ou SemPermissao (403)."""
    if login_simulado_ativo(cab) and cab.get("X-PRM-Dev-Usuario"):
        return app.usuario_teste(cab["X-PRM-Dev-Usuario"])
    try:
        bruto = extrair_bearer(cab)
    except TokenInvalido as e:
        raise NaoAutenticado("Sua sessão terminou por segurança. Entre de novo para continuar de onde parou.", codigo="sessao") from e
    ultimo = None
    for nome, cfg, chaves in _configs():
        try:
            ident = validar(bruto, cfg, chaves)
        except TokenInvalido as e:
            ultimo = e
            continue
        return _ator_do_token(app, ident, nome)
    raise NaoAutenticado("Sua sessão terminou por segurança. Entre de novo para continuar de onde parou.", codigo="sessao") from ultimo


def _ator_do_token(app, ident, publico):
    papeis = set(ident["papeis"])
    if ident["tipo"] == "agente":
        return Ator(tipo="agente", papel="sistema", oid=ident["oid"], nome="rotina", face="save", publico=publico)
    for p in ORDEM_SAVE:
        if p in papeis and publico == "central":
            return Ator(tipo="save", papel=PAPEL_SAVE[p], oid=ident["oid"], nome=ident.get("nome") or "", face="save", publico=publico)
    u = next(iter(app.repo.listar("usuario_parceiro", entra_oid=ident["oid"])), None)
    if u and (PORTAL in papeis or publico == "prm"):
        return ator_de_usuario(app, u, oid=ident["oid"], publico=publico)
    raise SemPermissao("Seu acesso ao portal ainda não foi liberado. Fale com o time da Save que atende você.", codigo="sem_acesso")


def exigir_face(ator, face):
    """Cada rota exige a sua face: parceiro nunca abre rota da Save, e a Save usa o próprio registro de app."""
    if face == "parceiro" and ator.tipo != "parceiro":
        raise SemPermissao("Esta tela é do portal do parceiro.")
    if face == "save" and ator.tipo not in ("save", "agente"):
        raise SemPermissao("Esta tela é do time da Save.")
    if face == "parceiro" and _prm_separado() and ator.publico != "prm" and ator.oid:
        raise SemPermissao("Use o portal de parceiros.")
    if face == "save" and ator.publico != "central":
        raise SemPermissao("Esta tela é do time da Save.")


def _prm_separado():
    return any(n == "prm" for n, _, _ in _configs())
