"""Testes da consulta de regime (base e cache sintéticos, sem dado real).

    cd central/api && python3 -m unittest -v tests.test_regime
"""
import json, os, sqlite3, tempfile, unittest

from central_api import regime as R
from cnpj import dv_cnpj


def cnpj(raiz, ordem="0001"):
    b = raiz + ordem
    return b + dv_cnpj(b)


REAL, PRES, SIMP, MISTO, VAZIO, SEM_BASE = (cnpj(r) for r in ("11111111", "22222222", "33333333", "44444444", "55555555", "66666666"))
FILIAL_REAL = cnpj("11111111", "0002")


class Regime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory(); R.BASE = cls.dir.name; R._cache.update(mtime=None, dados={})
        db = sqlite3.connect(os.path.join(R.BASE, "cnpj.sqlite"))
        db.executescript("CREATE TABLE estab(cnpj, basico, matriz, situacao, uf, municipio);CREATE TABLE empresa(basico, razao, porte);CREATE TABLE simples(basico, simples, mei);")
        for c, razao, simples in ((REAL, "EMPRESA REAL", "N"), (FILIAL_REAL, "EMPRESA REAL", "N"), (PRES, "EMPRESA PRESUMIDO", "N"),
                                  (SIMP, "EMPRESA SIMPLES", "S"), (MISTO, "EMPRESA MISTA", "N"), (VAZIO, "EMPRESA SEM REGIME", "N")):
            db.execute("INSERT INTO estab VALUES(?,?,?,?,?,?)", (c, c[:8], "matriz" if c[8:12] == "0001" else "filial", "02", "MG", "X"))
            if not db.execute("SELECT 1 FROM empresa WHERE basico=?", (c[:8],)).fetchone():
                db.execute("INSERT INTO empresa VALUES(?,?,?)", (c[:8], razao, "05")); db.execute("INSERT INTO simples VALUES(?,?,?)", (c[:8], simples, "N"))
        db.commit(); db.close()
        with open(os.path.join(R.BASE, "regime-cache.json"), "w") as f:
            json.dump({REAL: "LUCRO REAL (2024)", PRES: "LUCRO PRESUMIDO (2024)", MISTO: "LUCRO PRESUMIDO/REAL (2024)", VAZIO: "sem registro"}, f)

    @classmethod
    def tearDownClass(cls): cls.dir.cleanup()

    def test_real_confirmado_com_ano(self):
        r = R.consultar(REAL); self.assertEqual((r["faixa"], r["ano_base"]), ("confirmado_real", 2024))

    def test_filial_herda_regime_da_matriz(self):
        self.assertEqual(R.consultar(FILIAL_REAL)["faixa"], "confirmado_real")

    def test_aceita_pontuacao(self):
        f = REAL; self.assertEqual(R.consultar("%s.%s.%s/%s-%s" % (f[:2], f[2:5], f[5:8], f[8:12], f[12:]))["faixa"], "confirmado_real")

    def test_presumido_e_simples_nao_sao_real(self):
        self.assertEqual(R.consultar(PRES)["faixa"], "nao_real"); self.assertEqual(R.consultar(SIMP)["faixa"], "nao_real")

    def test_regime_misto_nao_confirma(self):
        self.assertEqual(R.consultar(MISTO)["faixa"], "provavel_real")

    def test_sem_registro_e_sem_dado(self):
        self.assertEqual(R.consultar(VAZIO)["faixa"], "sem_dado")

    def test_fora_da_base_nao_afirma_inexistencia(self):
        r = R.consultar(SEM_BASE); self.assertEqual(r["faixa"], "sem_dado"); self.assertIn("não quer dizer", r["detalhe"])

    def test_faturamento_acima_de_78mi_so_provavel(self):
        self.assertEqual(R.consultar(VAZIO, 90_000_000)["faixa"], "provavel_real"); self.assertEqual(R.consultar(VAZIO, 10_000_000)["faixa"], "sem_dado")

    def test_cnpj_invalido(self):
        self.assertEqual(R.consultar("12345")["faixa"], "invalido"); self.assertEqual(R.consultar("")["faixa"], "invalido")

    def test_teto_diario(self):
        R._uso.clear(); self.assertTrue(R.registrar_uso("u", R.LIMITE_DIA)[0]); self.assertFalse(R.registrar_uso("u", 1)[0]); self.assertTrue(R.registrar_uso("outro", 1)[0])


if __name__ == "__main__":
    unittest.main()
