"""Testes do pedido de análise e da esteira (pasta temporária; usa o auditor de promessas de verdade).

    cd central/api && PYTHONPATH=../../lib python3 -m unittest -v tests.test_esteira
"""
import json, os, tempfile, unittest

from central_api import esteira as E
from central_api import negocio_ativo as NA
from cnpj import dv_cnpj


def cnpj(raiz, ordem="0001"):
    b = raiz + ordem
    return b + dv_cnpj(b)


NOVO, CLIENTE = cnpj("11111111"), cnpj("99999999")
os.environ["CENTRAL_SAL"] = "sal-de-teste"
LIMPO = {"fazer": "A empresa não tem negócio na base. A pré-análise indica as teses a verificar com os documentos.",
         "precisa": "Veja a esteira em três ondas; a ordem depende da análise.", "falta": "ECF e EFD-Contribuições dos últimos 5 anos, pelo cliente.",
         "esteira": [{"onda": 1, "produto": "Recuperação tributária", "status": "pronto", "nota": "Depende de parecer e documentos."}]}
PROMESSA = dict(LIMPO, fazer="A Save garante recuperação de R$ 500 mil em 30 dias, sem risco.")


class Esteira(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.antes = (E.DIR, NA.DIR, NA.INDICE, NA._carregar)
        E.DIR = NA.DIR = self.tmp.name; NA.INDICE = os.path.join(self.tmp.name, "i.json"); NA._carregar = lambda: {NA.chave("99999999")}
        os.environ.pop("CENTRAL_APROVACAO", None)

    def tearDown(self):
        E.DIR, NA.DIR, NA.INDICE, NA._carregar = self.antes; self.tmp.cleanup(); os.environ.pop("CENTRAL_APROVACAO", None)

    def test_recusa_cliente_invalido_e_sem_indice(self):
        with self.assertRaisesRegex(E.Recusa, "negócio ativo"): E.solicitar(CLIENTE, "demo")
        with self.assertRaisesRegex(E.Recusa, "inválido"): E.solicitar("123", "demo")
        NA._carregar = lambda: None
        with self.assertRaisesRegex(E.Recusa, "conferir a base"): E.solicitar(NOVO, "demo")

    def test_um_pedido_aberto_por_parceiro_e_empresa(self):
        a = E.solicitar(NOVO, "p1"); b = E.solicitar(NOVO, "p1"); c = E.solicitar(NOVO, "p2")
        self.assertEqual(a["id"], b["id"]); self.assertNotEqual(a["id"], c["id"])

    def test_parceiro_so_ve_resultado_depois_de_entregue(self):
        p = E.solicitar(NOVO, "p1"); E.publicar(p["id"], LIMPO)
        self.assertNotIn("resultado", E.ler_do_parceiro(p["id"], "p1")); self.assertEqual(E.ler_do_parceiro(p["id"], "p1")["andamento"], "Em revisão final")
        E.aprovar(p["id"], "Aprovador"); self.assertEqual(E.ler_do_parceiro(p["id"], "p1")["resultado"]["falta"], LIMPO["falta"])

    def test_outro_parceiro_nao_le(self):
        p = E.solicitar(NOVO, "p1"); self.assertIsNone(E.ler_do_parceiro(p["id"], "p2"))

    def test_modo_autonomo_entrega_sozinho_se_a_auditoria_passar(self):
        os.environ["CENTRAL_APROVACAO"] = "autonoma"; p = E.solicitar(NOVO, "p1")
        self.assertEqual(E.publicar(p["id"], LIMPO)["status"], "entregue")

    def test_modo_autonomo_nunca_entrega_com_promessa(self):
        os.environ["CENTRAL_APROVACAO"] = "autonoma"; p = E.solicitar(NOVO, "p1")
        r = E.publicar(p["id"], PROMESSA); self.assertEqual(r["status"], "revisao_humana"); self.assertFalse(r["auditoria"]["ok"])
        self.assertNotIn("resultado", E.ler_do_parceiro(p["id"], "p1"))

    def test_exige_os_tres_blocos(self):
        p = E.solicitar(NOVO, "p1")
        with self.assertRaisesRegex(E.Recusa, "falta"): E.publicar(p["id"], {"fazer": "x", "precisa": "y"})

    def test_nao_publica_duas_vezes(self):
        p = E.solicitar(NOVO, "p1"); E.publicar(p["id"], LIMPO)
        with self.assertRaises(E.Recusa): E.publicar(p["id"], LIMPO)

    def test_indice_guarda_so_chaves(self):
        idx = NA.construir([{"status": "aberto", "extras": {"cnpj": CLIENTE}}, {"status": "perdido", "extras": {"cnpj": NOVO}}, {"status": "ganho", "extras": {"cnpj": "x"}}])
        self.assertEqual(idx["total"], 1); self.assertNotIn(CLIENTE[:8], json.dumps(idx))


if __name__ == "__main__":
    unittest.main()
