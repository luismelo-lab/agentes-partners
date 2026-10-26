"""PRM: os dois adaptadores do repositório cumprem o mesmo contrato (L3) e o contador é persistente e atômico (L4)."""
import os, sqlite3, tempfile, threading, unittest

from central_api.prm.repositorio import RepoJSON, RepoSQL, SoLeitura


class Contrato:
    def novo(self):
        raise NotImplementedError

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.r = self.novo()

    def tearDown(self):
        self.tmp.cleanup()

    def test_inserir_e_obter(self):
        self.r.inserir("registro", {"registro_id": "R-2026-000001", "parceiro_id": "P-0001", "estado": "em_analise"})
        self.assertEqual(self.r.obter("registro", "R-2026-000001")["estado"], "em_analise")
        self.assertIsNone(self.r.obter("registro", "R-2026-000002"))

    def test_listar_com_filtro(self):
        for i, p in enumerate(("P-0001", "P-0002", "P-0001")):
            self.r.inserir("registro", {"registro_id": "R-2026-00000%d" % i, "parceiro_id": p, "estado": "em_analise", "x": i})
        self.assertEqual(len(self.r.listar("registro", parceiro_id="P-0001")), 2)
        self.assertEqual(len(self.r.listar("registro", parceiro_id="P-0001", x=2)), 1)

    def test_atualizar(self):
        self.r.inserir("registro", {"registro_id": "R1", "estado": "em_analise"})
        self.r.atualizar("registro", "R1", {"estado": "aprovado"})
        self.assertEqual(self.r.obter("registro", "R1")["estado"], "aprovado")

    def test_gravar_e_upsert(self):
        self.r.gravar("config", {"chave": "a", "valor": 1})
        self.r.gravar("config", {"chave": "a", "valor": 2})
        self.assertEqual(self.r.obter("config", "a")["valor"], 2)
        self.assertEqual(len(self.r.listar("config")), 1)

    def test_ledger_nao_muda(self):
        e = self.r.inserir("registro_evento", {"registro_id": "R1", "para_estado": "em_analise"})
        self.assertTrue(e["evento_id"])
        with self.assertRaises(SoLeitura):
            self.r.atualizar("registro_evento", e["evento_id"], {"para_estado": "aprovado"})

    def test_tabela_gerada_e_so_leitura(self):
        with self.assertRaises(SoLeitura):
            self.r.inserir("negocio", {"deal_id": "1"})

    def test_chave_repetida(self):
        self.r.inserir("registro", {"registro_id": "R1"})
        with self.assertRaises(SoLeitura):
            self.r.inserir("registro", {"registro_id": "R1"})

    def test_sequencia_atomica_com_threads(self):
        vistos, trava = [], threading.Lock()

        def f():
            for _ in range(10):
                n = self.r.seq("teste")
                with trava:
                    vistos.append(n)
        ts = [threading.Thread(target=f) for _ in range(8)]
        [t.start() for t in ts]; [t.join() for t in ts]
        self.assertEqual(sorted(vistos), list(range(1, 81)))

    def test_contador_persistente(self):
        self.assertEqual(self.r.contar("neutra|U-0001|2026-10-26"), 1)
        self.assertEqual(self.r.contar("neutra|U-0001|2026-10-26"), 2)
        outro = self.novo()  # nova instância (outro processo / reinício): o teto não zera
        self.assertEqual(outro.valor_contador("neutra|U-0001|2026-10-26"), 2)
        self.assertEqual(outro.contar("neutra|U-0001|2026-10-26"), 3)


class RepoJSONTeste(Contrato, unittest.TestCase):
    def novo(self):
        return RepoJSON(os.path.join(self.tmp.name, "prm"))

    def test_arquivos_600_e_envelope(self):
        self.r.inserir("registro", {"registro_id": "R1"})
        arq = os.path.join(self.tmp.name, "prm", "prm_registro_oportunidade.json")
        self.assertEqual(os.stat(arq).st_mode & 0o777, 0o600)
        import json
        with open(arq) as f:
            env = json.load(f)
        self.assertEqual((env["esquema"], env["tabela"]), ("prm-local/1", "prm.registro_oportunidade"))

    def test_somente_leitura(self):
        ro = RepoJSON(os.path.join(self.tmp.name, "prm"), somente_leitura=True)
        with self.assertRaises(SoLeitura):
            ro.inserir("registro", {"registro_id": "R9"})


class RepoSQLTeste(Contrato, unittest.TestCase):
    def novo(self):
        arq = os.path.join(self.tmp.name, "prm.db")
        return RepoSQL(lambda: sqlite3.connect(arq, check_same_thread=False), criar=True)

    def test_rollback_na_transacao(self):
        try:
            with self.r.transacao():
                self.r.inserir("registro", {"registro_id": "R1"})
                raise RuntimeError("falha no meio")
        except RuntimeError:
            pass
        self.assertIsNone(self.r.obter("registro", "R1"))


if __name__ == "__main__":
    unittest.main()
