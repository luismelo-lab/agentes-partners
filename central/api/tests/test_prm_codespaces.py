"""GitHub Codespaces (Luis, 26/10/2026): o servidor de teste aceita o host exato do próprio codespace, só com CODESPACES=true;
o login simulado segue com as outras travas (PRM_LOGIN_SIMULADO=1 e fora da Azure). Host de outro codespace é recusado.
Roda no Linux do GitHub Actions (Python 3.12), sem ~/agentes-partners real e sem registro/."""
import http.client, json, os, socket, subprocess, sys, tempfile, time, unittest
from pathlib import Path

from tests.prm_base import BasePRM

from central_api.prm import identidade as ID

NOME, DOMINIO = "luis-prm-x7g9q4", "app.github.dev"
PROPRIO = "%s-4280.%s" % (NOME, DOMINIO)
VARS = ("CODESPACES", "CODESPACE_NAME", "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "PRM_PORTA", "PRM_LOGIN_SIMULADO", "WEBSITE_INSTANCE_ID")


class Ambiente(unittest.TestCase):
    def setUp(self):
        self._antes = {k: os.environ.get(k) for k in VARS}
        for k in VARS:
            os.environ.pop(k, None)
        os.environ["PRM_LOGIN_SIMULADO"] = "1"

    def tearDown(self):
        for k, v in self._antes.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def codespace(self, nome=NOME, dominio=DOMINIO):
        os.environ.update(CODESPACES="true", CODESPACE_NAME=nome, GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN=dominio)

    def ativo(self, host):
        return ID.login_simulado_ativo({"Host": host})


class HostDoCodespace(Ambiente):
    def test_fora_do_codespaces_nao_ha_host(self):
        self.assertIsNone(ID.host_codespaces())
        self.assertFalse(self.ativo(PROPRIO))
        self.assertTrue(self.ativo("localhost:4280"))

    def test_host_exato_do_proprio_codespace(self):
        self.codespace()
        self.assertEqual(ID.host_codespaces(), PROPRIO)
        self.assertTrue(self.ativo(PROPRIO))
        self.assertTrue(self.ativo(PROPRIO.upper()))
        self.assertTrue(self.ativo(PROPRIO + ":443"))
        self.assertTrue(self.ativo("127.0.0.1:4280"))      # o local continua valendo

    def test_host_de_outro_codespace_e_recusado(self):
        self.codespace()
        for h in ("outro-codespace-4280." + DOMINIO, NOME + "x-4280." + DOMINIO, "x" + PROPRIO, NOME + "-4281." + DOMINIO,
                  PROPRIO + ".evil.com", "evil.com/" + PROPRIO, NOME + "-4280.preview." + DOMINIO, PROPRIO + ":8443", "*." + DOMINIO, ""):
            self.assertFalse(self.ativo(h), h)

    def test_codespaces_precisa_ser_true(self):
        self.codespace()
        for v in ("1", "TRUE", "yes", ""):
            os.environ["CODESPACES"] = v
            self.assertFalse(self.ativo(PROPRIO), v)

    def test_variaveis_estranhas_desligam(self):
        for nome, dom in (("*", DOMINIO), ("a.b", DOMINIO), ("", DOMINIO), (NOME, ""), (NOME, "github.dev/x"), (NOME, "dev")):
            self.codespace(nome, dom)
            self.assertIsNone(ID.host_codespaces(), (nome, dom))
            self.assertFalse(self.ativo("%s-4280.%s" % (nome, dom)))

    def test_outras_travas_continuam(self):
        self.codespace()
        os.environ["WEBSITE_INSTANCE_ID"] = "azure"
        self.assertFalse(self.ativo(PROPRIO))
        os.environ.pop("WEBSITE_INSTANCE_ID")
        os.environ["PRM_LOGIN_SIMULADO"] = "0"
        self.assertFalse(self.ativo(PROPRIO))

    def test_porta_do_servidor(self):
        self.codespace()
        os.environ["PRM_PORTA"] = "4290"
        self.assertEqual(ID.host_codespaces(), "%s-4290.%s" % (NOME, DOMINIO))
        self.assertFalse(self.ativo(PROPRIO))
        self.assertTrue(self.ativo("%s-4290.%s" % (NOME, DOMINIO)))


class RotasNoCodespace(BasePRM):
    def setUp(self):
        super().setUp()
        self._cs = {k: os.environ.get(k) for k in VARS if k != "PRM_LOGIN_SIMULADO"}
        os.environ.update(CODESPACES="true", CODESPACE_NAME=NOME, GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN=DOMINIO)
        os.environ.pop("PRM_PORTA", None)

    def tearDown(self):
        for k, v in self._cs.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        super().tearDown()

    def test_login_simulado_pelo_host_do_codespace(self):
        self.assertEqual(self.http("GET", "/api/prm/dev/usuarios", host=PROPRIO)[0], 200)
        self.assertEqual(self.http("GET", "/api/prm/eu", "U-0001", host=PROPRIO)[0], 200)

    def test_outro_codespace_nao_entra(self):
        outro = "outro-codespace-4280." + DOMINIO
        self.assertEqual(self.http("GET", "/api/prm/dev/usuarios", host=outro)[0], 404)
        self.assertEqual(self.http("GET", "/api/prm/eu", "U-0001", host=outro)[0], 401)


def _porta_livre():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class ServidorDeTeste(unittest.TestCase):
    """Sobe o dev_server.py --prm de verdade (porta livre, estado em pasta temporária) com as variáveis do Codespaces."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.porta = _porta_livre()
        env = {k: v for k, v in os.environ.items() if k not in VARS}
        env.update(CODESPACES="true", CODESPACE_NAME=NOME, GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN=DOMINIO, PYTHONPATH="")
        servidor = Path(__file__).resolve().parents[2] / "dev_server.py"
        cls.proc = subprocess.Popen([sys.executable, str(servidor), "--prm", "--porta", str(cls.porta), "--estado", os.path.join(cls.tmp.name, "demo")],
                                    env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        fim = time.time() + 60
        while time.time() < fim:
            if cls.proc.poll() is not None:
                raise RuntimeError("dev_server.py saiu: " + (cls.proc.stdout.read() or ""))
            try:
                socket.create_connection(("127.0.0.1", cls.porta), timeout=0.5).close()
                break
            except OSError:
                time.sleep(0.2)
        else:
            cls.proc.kill()
            raise RuntimeError("dev_server.py não subiu")

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        try:
            cls.proc.wait(10)
        except subprocess.TimeoutExpired:
            cls.proc.kill()
        cls.proc.stdout.close()
        cls.tmp.cleanup()

    def pedir(self, host, caminho="/api/prm/dev/usuarios", usuario=None):
        c = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=10)
        c.putrequest("GET", caminho, skip_host=True)
        c.putheader("Host", host)
        if usuario:
            c.putheader("X-PRM-Dev-Usuario", usuario)
        c.endheaders()
        r = c.getresponse()
        corpo = r.read()
        c.close()
        return r.status, corpo

    def test_host_do_proprio_codespace(self):
        dono = "%s-%d.%s" % (NOME, self.porta, DOMINIO)
        st, corpo = self.pedir(dono)
        self.assertEqual(st, 200)
        self.assertTrue(json.loads(corpo)["usuarios"])
        self.assertEqual(self.pedir(dono, "/api/prm/eu", "U-0001")[0], 200)
        self.assertEqual(self.pedir("localhost:%d" % self.porta)[0], 200)

    def test_host_de_outro_codespace_421(self):
        for h in ("outro-codespace-%d.%s" % (self.porta, DOMINIO), "%s-%d.%s.evil.com" % (NOME, self.porta, DOMINIO), "evil.example", "%s-4280.%s" % (NOME, DOMINIO)
                  if self.porta != 4280 else "x-1." + DOMINIO):
            self.assertEqual(self.pedir(h)[0], 421, h)

    def test_ouve_em_todas_as_interfaces(self):
        try:
            ips = {a[4][0] for a in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)} - {"127.0.0.1"}
        except OSError:
            ips = set()
        if not ips:
            self.skipTest("sem IP além do loopback")
        ip = sorted(ips)[0]
        try:
            socket.create_connection((ip, self.porta), timeout=2).close()
        except OSError as e:
            self.skipTest("rede da máquina não permite: %s" % e)


if __name__ == "__main__":
    unittest.main()
