"""Testes da consulta de regime por API (as chamadas HTTP são trocadas por respostas sintéticas; nada vai à rede).

    cd central/api && PYTHONPATH=../../lib python3 -m unittest -v tests.test_regime
"""
import json, os, unittest

from central_api import negocio_ativo as NA
from central_api import regime as R
from cnpj import dv_cnpj


def cnpj(raiz, ordem="0001"):
    b = raiz + ordem
    return b + dv_cnpj(b)


REAL, PRES, SIMP, MISTO, VAZIO, SUMIU, CAIU, RESERVA = (cnpj(r) for r in ("11111111", "22222222", "33333333", "44444444", "55555555", "66666666", "77777777", "88888888"))
ANO = 2025


def dado(razao, regime=(), simples=False, mei=False, matriz=1):
    return {"razao_social": razao, "porte": "DEMAIS", "uf": "MG", "descricao_situacao_cadastral": "ATIVA", "identificador_matriz_filial": matriz,
            "opcao_pelo_simples": simples, "opcao_pelo_mei": mei,
            "regime_tributario": [{"ano": a, "forma_de_tributacao": f} for a, f in regime]}


BASE = {REAL: dado("EMPRESA REAL", [(2023, "LUCRO PRESUMIDO"), (ANO, "LUCRO REAL")]),
        PRES: dado("EMPRESA PRESUMIDO", [(ANO, "LUCRO PRESUMIDO")]),
        SIMP: dado("EMPRESA SIMPLES", [(2020, "LUCRO REAL")], simples=True),
        MISTO: dado("EMPRESA MISTA", [(ANO, "LUCRO PRESUMIDO"), (ANO, "LUCRO REAL")]),
        VAZIO: dado("EMPRESA SEM ECF"),
        RESERVA: dado("EMPRESA RESERVA", [(ANO, "LUCRO REAL")])}
chamadas = []


def http_falso(url):
    chamadas.append(url)
    c = url.rsplit("/", 1)[1]
    if c == CAIU or (c == RESERVA and "minhareceita" in url):
        return (0, None) if c == CAIU else (503, None)  # RESERVA: a primeira fonte cai e a segunda responde
    return (200, BASE[c]) if c in BASE else (404, None)


CLIENTE = cnpj("99999999")
os.environ["CENTRAL_SAL"] = "sal-de-teste"
INDICE = {NA.chave("99999999")}


class Regime(unittest.TestCase):
    def setUp(self):
        self.antes = R._http, NA._carregar; NA._carregar = lambda: INDICE; R._http = http_falso; R._memoria.clear(); chamadas.clear(); os.environ["CENTRAL_API_EXTERNA"] = "1"

    def tearDown(self): R._http, NA._carregar = self.antes

    def test_real_confirmado_usa_o_ano_mais_recente(self):
        r = R.consultar(REAL); self.assertEqual((r["faixa"], r["ano_base"]), ("confirmado_real", ANO)); self.assertEqual(r["empresa"]["razao"], "EMPRESA REAL")

    def test_aceita_pontuacao(self):
        f = REAL; self.assertEqual(R.consultar("%s.%s.%s/%s-%s" % (f[:2], f[2:5], f[5:8], f[8:12], f[12:]))["faixa"], "confirmado_real")

    def test_simples_vence_real_antigo(self):
        r = R.consultar(SIMP); self.assertEqual(r["faixa"], "nao_real"); self.assertIn("Simples", r["titulo"])

    def test_presumido_nao_e_real(self):
        self.assertEqual(R.consultar(PRES)["faixa"], "nao_real")

    def test_regime_misto_nao_confirma(self):
        self.assertEqual(R.consultar(MISTO)["faixa"], "provavel_real")

    def test_sem_ecf_e_sem_dado(self):
        self.assertEqual(R.consultar(VAZIO)["faixa"], "sem_dado")

    def test_faturamento_acima_de_78mi_so_provavel(self):
        self.assertEqual(R.consultar(VAZIO, 90_000_000)["faixa"], "provavel_real"); self.assertEqual(R.consultar(VAZIO, 10_000_000)["faixa"], "sem_dado")

    def test_cnpj_nao_localizado(self):
        self.assertEqual(R.consultar(SUMIU)["titulo"], "CNPJ não localizado")

    def test_fontes_fora_do_ar_nao_viram_resposta_falsa(self):
        r = R.consultar(CAIU); self.assertEqual(r["faixa"], "indisponivel"); self.assertEqual(len(chamadas), 2)

    def test_reserva_quando_a_primeira_cai(self):
        r = R.consultar(RESERVA); self.assertEqual(r["faixa"], "confirmado_real"); self.assertIn("BrasilAPI", r["fonte"])

    def test_cache_evita_segunda_chamada(self):
        R.consultar(REAL); R.consultar(REAL); self.assertEqual(len(chamadas), 1)

    def test_perfil_da_empresa_sem_dado_pessoal(self):
        BASE[REAL]["qsa"] = [{"nome_socio": "FULANO"}]; BASE[REAL]["email"] = "a@b.com"; BASE[REAL]["ddd_telefone_1"] = "3100000000"
        pf = R.consultar(REAL)["perfil"]
        self.assertEqual(pf["razao"], "EMPRESA REAL"); self.assertEqual(pf["ecf"][-1], {"ano": ANO, "forma": "LUCRO REAL"})
        self.assertNotIn("FULANO", json.dumps(pf)); self.assertNotIn("a@b.com", json.dumps(pf)); self.assertNotIn("3100000000", json.dumps(pf))

    def test_cliente_save_para_na_primeira_checagem_sem_chamar_api(self):
        r = R.consultar(CLIENTE); self.assertEqual((r["faixa"], r["titulo"]), ("negocio_ativo", "Empresa com negócio ativo na base Save Company")); self.assertEqual(chamadas, [])

    def test_filial_de_cliente_tambem_e_cliente(self):
        self.assertEqual(R.consultar(cnpj("99999999", "0002"))["faixa"], "negocio_ativo")

    def test_sem_indice_falha_fechada_sem_chamar_api(self):
        NA._carregar = lambda: None; r = R.consultar(REAL); self.assertEqual(r["faixa"], "indisponivel"); self.assertEqual(chamadas, [])

    def test_invalido_nao_chama_api(self):
        self.assertEqual(R.consultar("12345")["faixa"], "invalido"); self.assertEqual(chamadas, [])

    def test_interruptor_desliga_consulta_externa(self):
        os.environ["CENTRAL_API_EXTERNA"] = "0"; self.assertEqual(R.consultar(REAL)["faixa"], "indisponivel"); self.assertEqual(chamadas, [])

    def test_lote_mantem_a_ordem(self):
        self.assertEqual([r["cnpj"] for r in R.consultar_lote([PRES, REAL, "x"])], [PRES, REAL, ""])

    def test_teto_diario(self):
        R._uso.clear(); self.assertTrue(R.registrar_uso("u", R.LIMITE_DIA)[0]); self.assertFalse(R.registrar_uso("u", 1)[0]); self.assertTrue(R.registrar_uso("outro", 1)[0])


if __name__ == "__main__":
    unittest.main()
