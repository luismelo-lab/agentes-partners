"""Contêiner do PRM: repositório, parâmetros, calendário, relógio e trilha de acesso (L16).

Configuração por ambiente (L5, nada fixo em ~/agentes-partners):
  PRM_REPO      json (padrão) | sql
  PRM_DADOS     pasta do modo local (registro/prm/ do Mac, ou a pasta da demonstração)
  PRM_SQL       (Fase 2) texto de conexão ODBC; a Function usa a identidade gerenciada
"""
import hashlib, hmac, os, secrets, threading
from datetime import datetime

from .. import negocio_ativo as NA
from ..caminhos import preparar_lib
from . import calendario as CAL
from .calendario import Calendario
from .erros import NaoEncontrado
from .identidade import Ator, ator_de_usuario
from .parametros import Parametros
from .repositorio import RepoJSON, RepoSQL

preparar_lib()
from cnpj import completar_cnpj, raiz_cnpj  # noqa: E402

# usuários de teste do login simulado (só servidor local): os do time da Save; os do parceiro vêm da tabela usuario_parceiro
USUARIOS_SAVE_TESTE = {
    "daniela": ("Daniela (teste)", "daniela"),
    "luis": ("Luis (teste)", "luis"),
    "financeiro": ("Financeiro (teste)", "financeiro"),
}


class App:
    def __init__(self, repo, param=None, relogio=None, usuarios_teste=None):
        self.repo = repo
        self.param = param or Parametros(repo)
        self.cal = Calendario(self.param)
        self._relogio = relogio
        self.usuarios_teste = usuarios_teste  # None = todos os usuario_parceiro + USUARIOS_SAVE_TESTE
        self.avaliador_historico = None        # demandas.py escolhe (fixture ou lib/historico.py)
        self.lock = threading.RLock()

    # ------------------------------------------------------------ tempo
    def agora(self):
        return self._relogio() if self._relogio else datetime.now(CAL.UTC)

    def agora_iso(self):
        return CAL.iso(self.agora())

    # ------------------------------------------------------------ chaves e máscaras (a raiz só circula como HMAC)
    @staticmethod
    def cnpj(c):
        return completar_cnpj(c)

    @staticmethod
    def raiz(c):
        return raiz_cnpj(c)

    @staticmethod
    def hmac_raiz(c):
        return NA.chave(raiz_cnpj(c))

    @staticmethod
    def hmac_cnpj(c):
        return NA.chave(completar_cnpj(c))

    @staticmethod
    def mascara(c):
        """12.***.***/****-34 (2 primeiras e 2 últimas posições), como o espelho do prm_local.py."""
        c = completar_cnpj(c)
        return "%s.***.***/****-%s" % (c[:2], c[-2:]) if len(c) == 14 else None

    @staticmethod
    def ref():
        """Identificador opaco para URL (não sequencial: impede enumeração, 04 §2.1)."""
        return secrets.token_hex(8)

    @staticmethod
    def ref_estavel(*partes):
        return hmac.new(NA._sal().encode(), "|".join(str(p) for p in partes).encode(), hashlib.sha256).hexdigest()[:16]

    def novo_id(self, prefixo, largura=6, por_ano=True):
        ano = CAL.local(self.agora()).year
        serie = "%s-%d" % (prefixo, ano) if por_ano else prefixo
        n = self.repo.seq(serie)
        return ("%s-%d-%0*d" % (prefixo, ano, largura, n)) if por_ano else ("%s-%0*d" % (prefixo, largura, n))

    # ------------------------------------------------------------ usuários de teste (login simulado)
    def lista_usuarios_teste(self):
        out = []
        for u in self.repo.listar("usuario_parceiro"):
            if self.usuarios_teste is None or u["usuario_id"] in self.usuarios_teste:
                par = self.repo.obter("parceiro", u["parceiro_id"]) or {}
                out.append({"id": u["usuario_id"], "nome": u.get("nome"), "papel": u["papel"], "face": "parceiro", "escritorio": par.get("nome_exibicao"),
                            "estado": u.get("estado")})
        for k, (nome, papel) in USUARIOS_SAVE_TESTE.items():
            if self.usuarios_teste is None or k in self.usuarios_teste:
                out.append({"id": k, "nome": nome, "papel": papel, "face": "save"})
        return out

    def usuario_teste(self, ident):
        if ident in USUARIOS_SAVE_TESTE and (self.usuarios_teste is None or ident in self.usuarios_teste):
            nome, papel = USUARIOS_SAVE_TESTE[ident]
            return Ator(tipo="save", papel=papel, oid="local-" + ident, nome=nome, face="save")
        u = self.repo.obter("usuario_parceiro", ident)
        if not u or (self.usuarios_teste is not None and ident not in self.usuarios_teste):
            from .erros import NaoAutenticado
            raise NaoAutenticado("Usuário de teste desconhecido.", codigo="sessao")
        return ator_de_usuario(self, u)

    # ------------------------------------------------------------ trilha de acesso (seg.acesso_log, L16)
    def acesso(self, ator, tela, acao, alvo=None, resultado="ok", ip=None):
        """Toda leitura ou gravação de dado do parceiro. Nunca o CNPJ em claro: alvo é id opaco ou HMAC."""
        try:
            self.repo.inserir("acesso_log", {
                "quando": self.agora_iso(), "usuario_id": ator.usuario_id if ator and ator.tipo == "parceiro" else None,
                "conta_time": ator.rotulo() if ator and ator.tipo != "parceiro" else None, "papel": ator.papel if ator else None,
                "tela": tela[:40], "acao": acao[:40], "alvo_ref": (str(alvo)[:40] if alvo else None),
                "ip_hmac": NA.chave("ip:" + ip) if ip else None, "resultado": resultado})
        except Exception:  # noqa: BLE001  a trilha nunca derruba a resposta; o erro vai ao log
            import logging
            logging.getLogger("central_api.prm").exception("falha ao gravar acesso_log")

    def obter_no_escopo(self, tabela, ref, ator, ve, campo_ref="ref"):
        """Linha pelo id opaco, só se estiver no escopo do ator; senão 404 (PRM-R02) e trilha 'negado'."""
        linha = next(iter(self.repo.listar(tabela, **{campo_ref: ref})), None) if campo_ref != "id" else self.repo.obter(tabela, ref)
        if linha is None or not ve(ator, linha):
            self.acesso(ator, tabela, "ler", ref, "negado")
            raise NaoEncontrado()
        return linha


def criar_de_ambiente():
    """App do processo (Function ou servidor local) a partir das variáveis de ambiente."""
    tipo = os.environ.get("PRM_REPO", "json")
    if tipo == "sql":
        import pyodbc  # noqa: F401  (Fase 2; não instalado no Mac)
        conn = os.environ["PRM_SQL"]
        repo = RepoSQL(lambda: pyodbc.connect(conn))
    else:
        pasta = os.environ.get("PRM_DADOS") or str(__import__("pathlib").Path(os.environ.get("PARTNERS_AP") or os.path.expanduser("~/agentes-partners")) / "registro" / "prm")
        repo = RepoJSON(pasta)
    return App(repo)
