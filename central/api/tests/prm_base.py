"""Base dos testes do PRM: pasta temporária, fixtures fictícias, relógio fixo (segunda-feira, 26/10/2026 14h00) e
atalhos para chamar as rotas com o login simulado. Sem rede, sem Azure, sem dado real.

    cd central/api && PYTHONPATH=../../lib python3 -m unittest discover -p 'test_prm*'
"""
import os, tempfile, unittest
from datetime import datetime, timedelta

os.environ.setdefault("CENTRAL_SAL", "sal-de-teste")

from central_api import esteira as E, negocio_ativo as NA, regime  # noqa: E402
from central_api.prm import fixtures as F, rotas as R  # noqa: E402
from central_api.prm.app import App  # noqa: E402
from central_api.prm.calendario import FUSO  # noqa: E402
from central_api.prm.repositorio import RepoJSON  # noqa: E402

AGORA = datetime(2026, 10, 26, 14, 0, tzinfo=FUSO)


class BasePRM(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._antes = (E.DIR, NA.DIR, NA.INDICE, regime.FONTE_LOCAL, os.environ.get("PRM_LOGIN_SIMULADO"), os.environ.get("CENTRAL_APROVACAO"))
        os.environ["PRM_LOGIN_SIMULADO"] = "1"
        os.environ["CENTRAL_APROVACAO"] = "obrigatoria"
        self.t = [AGORA]
        self.app = App(RepoJSON(os.path.join(self.tmp.name, "prm")), relogio=lambda: self.t[0])
        self.app.param.definir("registro.piso_resposta_ms", 0)
        self.esteira = os.path.join(self.tmp.name, "esteira")
        F.carregar(self.app, self.esteira)
        self.app.usuarios_teste = None
        R.definir_app(self.app)
        R._APP["fixtures"] = True

    def tearDown(self):
        E.DIR, NA.DIR, NA.INDICE, regime.FONTE_LOCAL, login, aprov = self._antes
        NA._cache.update(mtime=None, chaves=None)
        for k, v in (("PRM_LOGIN_SIMULADO", login), ("CENTRAL_APROVACAO", aprov)):
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        R._APP.clear()
        self.tmp.cleanup()

    # ------------------------------------------------------------ atalhos
    def avancar(self, **kw):
        self.t[0] = self.t[0] + timedelta(**kw)

    def ator(self, u):
        return self.app.usuario_teste(u)

    def http(self, metodo, caminho, u=None, corpo=None, host="localhost:4280", cab=None):
        c = {"Host": host}
        if u:
            c["X-PRM-Dev-Usuario"] = u
        c.update(cab or {})
        return R.despachar(metodo, caminho, c, corpo if corpo is not None else {}, corpo if metodo == "GET" and corpo else {}, app=self.app)

    def cnpj(self, n):
        fx = F.ler()
        return F.cnpj_de(fx["empresas"][n]["raiz"])

    def form(self, n, **mudar):
        d = {"cnpj": self.cnpj(n), "razao_social": "Empresa %s Teste Ltda" % n, "contato_nome": "Pessoa Decisora", "contato_cargo": "Diretora financeira",
             "contato_email": "decisora@example.com", "interesse": "recuperacao", "como_conhece": "cliente_escritorio", "evidencia_tipo": "declaracao",
             "declaracao_lgpd": True, "declaracao_sem_promessa": True}
        d.update(mudar)
        return d

    def registro_por_cnpj(self, n, estado=None):
        h = self.app.hmac_raiz(self.cnpj(n))
        xs = [r for r in self.app.repo.listar("registro", cnpj_raiz_hmac=h) if estado is None or r["estado"] == estado]
        return sorted(xs, key=lambda r: r["criado_em"])[-1] if xs else None

    def reg_fx(self, n):
        """Registro da fixture pela empresa (o primeiro)."""
        h = self.app.hmac_raiz(self.cnpj(n))
        return self.app.repo.listar("registro", cnpj_raiz_hmac=h)[0]

    def avisos(self, para):
        return [n for n in self.app.repo.listar("notificacao") if n["para"] == para]
