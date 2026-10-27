"""Complemento do HubSpot pela API para o PRM (prm_hubspot.py) e junção no espelho (prm_local.py). Sem rede: a leitura é falsa."""
import importlib.util, json, os, sys, tempfile, unittest

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SCRIPTS = os.path.join(RAIZ, "skills", "depto-dados", "scripts")


def carregar(nome):
    spec = importlib.util.spec_from_file_location(nome, os.path.join(SCRIPTS, nome + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


PH = carregar("prm_hubspot")
PL = carregar("prm_local")
PL_ = {"10": {"nome": "RT - Real & Presumido", "etapas": {"a": {"nome": "Novo Negócio"}, "b": {"nome": "Em Diagnóstico"}, "c": {"nome": "Negócio Fechado"}}},
       "20": {"nome": "Gestão de Passivo", "etapas": {"x": {"nome": "Análise de Documentos"}}}}


class Complemento(unittest.TestCase):
    def setUp(self):
        self.pedidos = []
        props = {"1": {"hs_v2_date_entered_a": "2026-03-02T02:00:00Z", "hs_v2_date_entered_c": "2026-05-10T12:00:00Z",
                       "hs_v2_date_entered_b": "2026-04-01T12:00:00Z", "hubspot_owner_id": "7", "hs_next_step": "Enviar SPED",
                       "inteligencia_tributaria__motivos_de_perda": None, "descricao_do_motivo_da_perda": "texto livre"},
                 "2": {"hs_v2_date_entered_x": "2026-06-01T12:00:00Z", "hubspot_owner_id": "99"}}

        def ler(ids, campos):
            self.pedidos.append((list(ids), campos))
            return [{"id": i, "properties": props[i]} for i in ids]
        self.ler = ler
        self.neg = [{"id": "1", "pipeline": "RT - Real & Presumido"}, {"id": "2", "pipeline": "Gestão de Passivo"}]

    def test_monta_linha_do_tempo_em_ordem_e_no_dia_de_brasilia(self):
        out = PH.montar(self.neg, PL_, {"inteligencia_tributaria__motivos_de_perda"}, self.ler, {"7": "Ana Save"})
        self.assertEqual([h["etapa"] for h in out["1"]["historico_etapas"]], ["Novo Negócio", "Em Diagnóstico", "Negócio Fechado"])
        self.assertEqual(out["1"]["historico_etapas"][0]["entrou_em"], "2026-03-01")  # 02h UTC = 23h do dia anterior em Brasília
        self.assertEqual(out["1"]["owner_nome"], "Ana Save")
        self.assertEqual(out["1"]["proximo_passo"], "Enviar SPED")
        self.assertEqual(out["1"]["motivo_perda"], "texto livre")
        self.assertNotIn("owner_nome", out["2"])  # dono desconhecido não vira nome inventado

    def test_le_so_campos_existentes_e_em_lotes(self):
        PH.montar(self.neg, PL_, set(), self.ler, {})
        ids, campos = self.pedidos[0]
        self.assertNotIn("inteligencia_tributaria__motivos_de_perda", campos)
        self.assertIn("hs_v2_date_entered_x", campos)
        self.assertFalse(any(c in campos for c in ("dealname", "cnpj_", "email")))  # nome da empresa e contato não são lidos
        neg = [{"id": str(i), "pipeline": "RT - Real & Presumido"} for i in range(250)]
        self.pedidos.clear()
        PH.montar(neg, PL_, set(), lambda ids, c: (self.pedidos.append(ids), [])[1], {})
        self.assertEqual([len(x) for x in self.pedidos], [100, 100, 50])

    def test_nome_do_complemento_nao_confunde_o_download(self):
        self.assertEqual(os.path.basename(PH.complemento_de("/d/hubspot-2026-10-27.json")), "prm-complemento-2026-10-27.json")

    def test_prm_local_junta_o_complemento_do_mesmo_dia(self):
        with tempfile.TemporaryDirectory() as t:
            fonte = os.path.join(t, "hubspot-2026-10-27.json")
            json.dump({"negocios": {"1": {"historico_etapas": [{"etapa": "Novo Negócio", "entrou_em": "2026-03-01"}], "owner_nome": "Ana"}}},
                      open(os.path.join(t, "prm-complemento-2026-10-27.json"), "w"))
            neg = [{"id": "1", "extras": {"uf": "SP"}}, {"id": "2", "extras": {}}]
            self.assertEqual(PL.complementar(neg, fonte), "prm-complemento-2026-10-27.json")
            self.assertEqual(neg[0]["extras"]["uf"], "SP"); self.assertEqual(neg[0]["extras"]["owner_nome"], "Ana")
            self.assertEqual(neg[1]["extras"], {})
            self.assertIsNone(PL.complementar([{"id": "1"}], os.path.join(t, "hubspot-2026-10-26.json")))  # outro dia: não mistura


if __name__ == "__main__":
    unittest.main()
