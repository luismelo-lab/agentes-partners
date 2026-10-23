"""Testes sintéticos de negocio_ativo (CNPJs gerados com dv_cnpj; nenhum dado real)."""
import datetime, json, os, stat, tempfile, unittest

from cnpj import dv_cnpj


def cnpj(base8, ordem="0001"):
    b = base8 + ordem
    return b + dv_cnpj(b)


def neg(c, status="ganho"):
    return {"status": status, "extras": {"cnpj": c}}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._env = {k: os.environ.get(k) for k in ("CENTRAL_ESTEIRA", "CENTRAL_SAL")}  # outros testes fixam CENTRAL_SAL
        os.environ["CENTRAL_ESTEIRA"] = self.tmp.name
        os.environ.pop("CENTRAL_SAL", None)
        from central_api import negocio_ativo as na
        self.na = na
        self._old = (na.DIR, na.INDICE)
        na.DIR = self.tmp.name
        na.INDICE = os.path.join(self.tmp.name, "indice.json")
        na._cache.update(mtime=None, chaves=None)

    def tearDown(self):
        self.na.DIR, self.na.INDICE = self._old
        for k, v in self._env.items():
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v
        self.na._cache.update(mtime=None, chaves=None)
        self.tmp.cleanup()


class TestConstruir(Base):
    def test_status_aberto_ganho_entram_perdido_nao(self):
        a, b, c = cnpj("11111111"), cnpj("22222222"), cnpj("33333333")
        idx = self.na.construir([neg(a, "aberto"), neg(b, "ganho"), neg(c, "perdido")])
        self.assertEqual(idx["total"], 2)
        self.assertIn(self.na.chave("11111111"), idx["chaves"])
        self.assertNotIn(self.na.chave("33333333"), idx["chaves"])

    def test_status_com_caixa_acento_e_espaco(self):
        idx = self.na.construir([neg(cnpj("11111111"), " GANHO "), neg(cnpj("22222222"), "Aberto"), neg(cnpj("33333333"), "Ganhó")])
        self.assertEqual(idx["total"], 3)

    def test_status_desconhecido_vai_para_o_relatorio(self):
        with self.assertLogs("central_api.negocio_ativo", "WARNING"):
            idx = self.na.construir([neg(cnpj("11111111"), "em análise")])
        self.assertEqual(idx["total"], 0)
        self.assertEqual(idx["status_desconhecidos"], {"em analise": 1})

    def test_filiais_viram_uma_raiz(self):
        idx = self.na.construir([neg(cnpj("11111111", "0001")), neg(cnpj("11111111", "0002"))])
        self.assertEqual(idx["total"], 1)

    def test_zeros_a_esquerda_perdidos(self):
        c = cnpj("01234567")
        self.assertEqual(self.na.construir([neg(c.lstrip("0"))])["total"], 1)
        self.assertEqual(self.na.construir([neg(c.lstrip("0"))])["chaves"], self.na.construir([neg(c)])["chaves"])

    def test_alfanumerico(self):
        c = cnpj("AB12CD34")
        idx = self.na.construir([neg(c)])
        self.assertEqual(idx["total"], 1)
        self.assertIn(self.na.chave("AB12CD34"), idx["chaves"])

    def test_vazio_e_invalido_contados_a_parte(self):
        ruim = cnpj("11111111")[:-1] + ("0" if cnpj("11111111")[-1] != "0" else "1")
        idx = self.na.construir([neg(""), neg(None), neg(ruim), neg("123")])
        self.assertEqual(idx["total"], 0)
        self.assertEqual(idx["negocios_fora_do_indice"], {"sem_cnpj": 2, "cnpj_invalido": 2})

    def test_negocio_antigo_continua_ativo(self):
        d = neg(cnpj("11111111")); d["fechado"] = "2019-01-01"
        self.assertEqual(self.na.construir([d])["total"], 1)

    def test_sem_extras(self):
        self.assertEqual(self.na.construir([{"status": "ganho"}])["total"], 0)

    def test_idempotente(self):
        n = [neg(cnpj("11111111")), neg(cnpj("22222222"), "aberto")]
        self.assertEqual(self.na.construir(n)["chaves"], self.na.construir(list(reversed(n)))["chaves"])


class TestConsulta(Base):
    def _grava(self, **kw):
        idx = self.na.construir([neg(cnpj("11111111")), neg(cnpj("22222222"), "perdido")], **kw)
        self.na.gravar(idx)
        return idx

    def test_sem_indice_falha_fechada(self):
        self.assertIsNone(self.na.tem_negocio_ativo(cnpj("11111111")))

    def test_consulta_por_raiz_com_pontuacao(self):
        self._grava()
        c = cnpj("11111111", "0002")
        f = "%s.%s.%s/%s-%s" % (c[:2], c[2:5], c[5:8], c[8:12], c[12:])
        self.assertTrue(self.na.tem_negocio_ativo(f))
        self.assertFalse(self.na.tem_negocio_ativo(cnpj("22222222")))  # só perdido não bloqueia
        self.assertFalse(self.na.tem_negocio_ativo(cnpj("99999999")))
        self.assertFalse(self.na.tem_negocio_ativo(""))

    def test_indice_corrompido_falha_fechada(self):
        self._grava()
        with open(self.na.INDICE, "w") as f: f.write("{nao e json")
        with self.assertLogs("central_api.negocio_ativo", "ERROR"):
            self.assertIsNone(self.na.tem_negocio_ativo(cnpj("11111111")))

    def test_indice_de_outro_sal_falha_fechada(self):
        self._grava()
        os.environ["CENTRAL_SAL"] = "x" * 64
        try:
            self.na._cache.update(mtime=None, chaves=None)
            with self.assertLogs("central_api.negocio_ativo", "ERROR"):
                self.assertIsNone(self.na.tem_negocio_ativo(cnpj("11111111")))
        finally:
            os.environ.pop("CENTRAL_SAL", None)

    def test_indice_velho_avisa_mas_responde(self):
        velho = (datetime.datetime.now() - datetime.timedelta(days=5)).strftime("%Y-%m-%d %H:%M")
        self._grava(baixado_em=velho)
        self.assertGreater(self.na.idade_dias(), 4.9)
        with self.assertLogs("central_api.negocio_ativo", "WARNING") as cm:
            self.assertTrue(self.na.tem_negocio_ativo(cnpj("11111111")))
        self.assertIn("dias", cm.output[0])

    def test_indice_novo_nao_avisa(self):
        self._grava(baixado_em=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.assertLess(self.na.idade_dias(), 0.1)
        with self.assertNoLogs("central_api.negocio_ativo", "WARNING"):
            self.assertTrue(self.na.tem_negocio_ativo(cnpj("11111111")))

    def test_idade_sem_indice(self):
        self.assertIsNone(self.na.idade_dias())


class TestSegurancaEGravacao(Base):
    def _txt(self):
        with open(self.na.INDICE) as f: return f.read()

    def _ler(self):
        return json.loads(self._txt())

    def test_sal_gerado_com_600_e_estavel(self):
        s1 = self.na._sal()
        arq = os.path.join(self.tmp.name, "sal.key")
        self.assertEqual(stat.S_IMODE(os.stat(arq).st_mode), 0o600)
        self.assertGreaterEqual(len(s1), 64)
        self.assertEqual(s1, self.na._sal())

    def test_sal_com_permissao_aberta_e_corrigido(self):
        self.na._sal()
        arq = os.path.join(self.tmp.name, "sal.key")
        os.chmod(arq, 0o644)
        with self.assertLogs("central_api.negocio_ativo", "WARNING"):
            self.na._sal()
        self.assertEqual(stat.S_IMODE(os.stat(arq).st_mode), 0o600)

    def test_sal_curto_recusado(self):
        with open(os.path.join(self.tmp.name, "sal.key"), "w") as f: f.write("abc")
        with self.assertRaises(RuntimeError):
            self.na._sal()

    def test_chave_nao_expoe_raiz_e_depende_do_sal(self):
        k1 = self.na.chave("11111111")
        self.assertNotIn("11111111", k1)
        self.assertEqual(len(k1), 32)
        os.environ["CENTRAL_SAL"] = "y" * 64
        try:
            self.assertNotEqual(k1, self.na.chave("11111111"))
        finally:
            os.environ.pop("CENTRAL_SAL", None)

    def test_gravacao_atomica_600_sem_sobras(self):
        self.na.gravar(self.na.construir([neg(cnpj("11111111"))]))
        self.na.gravar(self.na.construir([neg(cnpj("22222222"))]))
        self.assertEqual(stat.S_IMODE(os.stat(self.na.INDICE).st_mode), 0o600)
        self.assertEqual([f for f in os.listdir(self.tmp.name) if f.endswith(".tmp")], [])
        self.assertEqual(self._ler()["total"], 1)

    def test_falha_na_gravacao_preserva_indice_anterior(self):
        self.na.gravar(self.na.construir([neg(cnpj("11111111"))]))
        antes = self._txt()
        with self.assertRaises(TypeError):
            self.na.gravar({"chaves": {object()}})  # não serializa
        self.assertEqual(self._txt(), antes)
        self.assertEqual([f for f in os.listdir(self.tmp.name) if f.endswith(".tmp")], [])


if __name__ == "__main__":
    unittest.main()
