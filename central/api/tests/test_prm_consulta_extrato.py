"""PRM: consulta de Lucro Real no fluxo Registrar (uma digitação do CNPJ), dossiê da esteira, extrato (02 §6) e contestação."""
import os

from central_api.prm import extrato as EX
from central_api.prm.repositorio import RepoJSON
from central_api.prm.textos import texto as T
from tests.prm_base import BasePRM


class Consulta(BasePRM):
    def consultar(self, *ns, u="U-0001"):
        return self.http("POST", "/api/prm/parceiro/empresa/consultar", u, {"cnpjs": [self.cnpj(n) for n in ns]})

    def test_livre_traz_receita_e_regime_sem_perfil_nem_cnpj(self):
        st, o = self.consultar("06")
        r = o["resultados"][0]
        self.assertEqual((st, r["faixa"], r["neutra"], r["pode_registrar"]), (200, "confirmado_real", False, True))
        self.assertEqual(r["empresa"]["razao"], "EMPRESA 06 DISTRIBUIDORA LTDA")
        self.assertIsNone(r["perfil"]); self.assertNotIn("cnpj", r)

    def test_cliente_da_save_volta_neutra(self):
        r = self.consultar("07")[1]["resultados"][0]
        self.assertEqual((r["neutra"], r["titulo"], r["empresa"]), (True, T("M-00"), None))

    def test_registro_de_outro_parceiro_volta_neutra(self):
        r = self.consultar("08")[1]["resultados"][0]
        self.assertTrue(r["neutra"])

    def test_neutras_iguais_entre_si(self):
        a = self.consultar("07")[1]["resultados"][0]; b = self.consultar("08")[1]["resultados"][0]; c = self.consultar("21")[1]["resultados"][0]
        limpa = lambda x: {k: v for k, v in x.items() if k != "cnpj_mascara"}  # noqa: E731
        self.assertEqual(limpa(a), limpa(b)); self.assertEqual(limpa(a), limpa(c))

    def test_empresa_baixada_nao_registra(self):
        r = self.consultar("09")[1]["resultados"][0]
        self.assertEqual((r["situacao_ativa"], r["pode_registrar"]), (False, False))

    def test_simples_nao_e_lucro_real(self):
        self.assertEqual(self.consultar("10")[1]["resultados"][0]["faixa"], "nao_real")

    def test_ja_e_seu_na_consulta(self):
        r = self.consultar("01")[1]["resultados"][0]
        self.assertEqual(r["ja_e_seu"]["estado"], "ja_e_seu")

    def test_lote_de_varias_empresas(self):
        st, o = self.consultar("06", "13", "10")
        self.assertEqual([r["faixa"] for r in o["resultados"]], ["confirmado_real", "nao_real", "nao_real"])

    def test_teto_de_consultas_persistente(self):
        self.app.param.definir("consulta.teto_diario_usuario", 2)
        self.consultar("06"); self.consultar("13")
        r = self.consultar("10")[1]["resultados"][0]
        self.assertTrue(r["neutra"])
        self.assertEqual(RepoJSON(self.app.repo.pasta).valor_contador("consulta|U-0001|2026-10-26"), 3)

    def test_trilha_so_com_hmac(self):
        self.consultar("06", "07")
        arq = os.path.join(self.app.repo.pasta, "central_consulta_regime.json")
        with open(arq, encoding="utf-8") as f:
            txt = f.read()
        self.assertNotIn(self.cnpj("06"), txt); self.assertNotIn(self.cnpj("07"), txt)
        motivos = [x["motivo_interno"] for x in self.app.repo.listar("consulta")]
        self.assertIn("negocio_ativo", motivos)

    def test_checar_em_tempo_real_nao_olha_a_carteira(self):
        for n, esperado in (("06", "ok_formato"), ("07", "ok_formato"), ("08", "ok_formato"), ("01", "ja_e_seu")):
            st, o = self.http("POST", "/api/prm/parceiro/empresa/checar", "U-0001", {"cnpj": self.cnpj(n)})
            self.assertEqual(o["estado"], esperado, n)
        self.assertEqual(self.http("POST", "/api/prm/parceiro/empresa/checar", "U-0001", {"cnpj": "TESTE00600011"})[1]["estado"], "incompleto")

    def test_dossie_do_registro_e_aprovacao_com_trilha(self):
        self.app.repo.atualizar("usuario_parceiro", "U-0002", {"termos_versao": self.app.param("termos_uso.versao")})
        r = self.reg_fx("02")
        st, o = self.http("POST", "/api/prm/parceiro/empresas/%s/dossie" % r["ref"], "U-0002")
        self.assertEqual((st, o["status"]), (200, "aguardando_aprovacao"))
        pid = self.app.repo.obter("registro", r["registro_id"])["dossie_id"]
        st, _ = self.http("POST", "/api/prm/save/decidir", "luis", {"objeto": "dossie", "id": pid, "decisao": "aprovar"})
        self.assertEqual(st, 200)
        f = self.http("GET", "/api/prm/parceiro/empresas/" + r["ref"], "U-0002")[1]
        self.assertEqual(f["dossie"]["status"], "entregue")
        self.assertGreaterEqual(len(f["dossie"]["resultado"]["dossie"]), 6)
        self.assertEqual(self.app.repo.listar("decisao", objeto="dossie")[0]["papel"], "luis")

    def test_dossie_de_cliente_da_save_fica_neutro(self):
        self.http("POST", "/api/prm/parceiro/registros", "U-0001", self.form("07"))
        r = self.registro_por_cnpj("07")
        st, o = self.http("POST", "/api/prm/parceiro/empresas/%s/dossie" % r["ref"], "U-0001")
        self.assertEqual((st, o["erro"]), (409, T("M-00")))


class Extrato(BasePRM):
    def linha(self, deal):
        return EX.atual(self.app, self.app.repo.obter("extrato_linha", "X-%s-REC" % deal))

    def decidir(self, u, **c):
        return self.http("POST", "/api/prm/save/decidir", u, c)

    def test_previsto_sem_valor_e_com_percentual(self):
        o = self.http("GET", "/api/prm/parceiro/extrato", "U-0001")[1]
        prev = [l for l in o["linhas"] if l["estado"] == "previsto"][0]
        self.assertEqual(prev["mensagem"], T("EXT-previsto", pct="25"))
        self.assertNotIn("valor", prev); self.assertNotIn("valor_estimado", prev)

    def test_em_conferencia_sem_valor_nem_data(self):
        o = self.http("GET", "/api/prm/parceiro/extrato", "U-0001")[1]
        c = [l for l in o["linhas"] if l["estado"] == "em_conferencia"][0]
        self.assertEqual(c["mensagem"], T("M-20")); self.assertNotIn("valor", c)
        self.assertEqual(o["resumo"]["em_conferencia_linhas"], 1)

    def test_so_financeiro_registra_recebimento(self):
        st, _ = self.decidir("daniela", objeto="extrato_linha", id="X-9100000004-REC", decisao="registrar_recebimento", valor=10000, competencia="2026-10")
        self.assertEqual(st, 403)
        st, _ = self.decidir("financeiro", objeto="extrato_linha", id="X-9100000004-REC", decisao="registrar_recebimento", valor=10000, competencia="2026-10")
        self.assertEqual((st, self.linha("9100000004")["estado"]), (200, "recebido_pela_save"))

    def test_em_conferencia_nao_recebe(self):
        st, o = self.decidir("financeiro", objeto="extrato_linha", id="X-9100000018-REC", decisao="registrar_recebimento", valor=100, competencia="2026-10")
        self.assertEqual(st, 409)

    def test_calculo_usa_incontroverso_e_arredonda_meia_para_cima(self):
        self.app.repo.gravar("termo", {"termo_id": "T-P-0001", "parceiro_id": "P-0001", "percentual_recuperacao": 0.30, "vigencia_ini": "2025-01-01"})
        self.decidir("financeiro", objeto="extrato_linha", id="X-9100000004-REC", decisao="registrar_recebimento", valor=10000.10, competencia="2026-10")
        self.decidir("financeiro", objeto="extrato", id="mes", decisao="calcular", competencia="2026-10")
        x = self.linha("9100000004")
        self.assertEqual((x["estado"], x["percentual_aplicado"], x["valor_bruto"], x["excedente_em_conferencia"]), ("calculado", 0.25, 2500.03, 500.01))

    def test_centavo(self):
        self.assertEqual((EX.centavo(0.005), EX.centavo(2.675), EX.centavo(1.004)), (0.01, 2.68, 1.0))

    def test_liberar_lote_e_aviso_m21a(self):
        lote = [l for l in EX.lotes(self.app) if l["calculadas"]][0]
        self.assertTrue(lote["pode_liberar"])
        st, o = self.decidir("financeiro", objeto="extrato_lote", id=lote["lote"], decisao="liberar")
        self.assertEqual((st, o["objeto"]["linhas_liberadas"]), (200, 1))
        self.assertEqual(self.linha("9100000020")["estado"], "aguardando_nf")
        self.assertTrue(any(n["codigo"] == "M-21a" for n in self.avisos("usuario:U-0001")))

    def test_segregacao_quem_recebe_nao_aprova(self):
        self.decidir("financeiro", objeto="extrato_linha", id="X-9100000004-REC", decisao="registrar_recebimento", valor=10000, competencia="2026-10")
        self.decidir("financeiro", objeto="extrato", id="mes", decisao="calcular")
        st, o = self.decidir("financeiro", objeto="extrato_lote", id="P-0001|2026-10", decisao="liberar")
        self.assertEqual(st, 403)
        self.assertIn("PRM-R18", o["erro"])

    def test_contestacao_na_janela_e_resposta(self):
        v = [l for l in self.http("GET", "/api/prm/parceiro/extrato", "U-0001")[1]["linhas"] if l["pode_contestar"]][0]
        st, o = self.http("POST", "/api/prm/parceiro/extrato/%s/contestar" % v["ref"], "U-0001", {"motivo": "O percentual não bate com o termo assinado."})
        self.assertEqual((st, o["fora_da_janela"]), (200, False))
        self.assertEqual(self.linha("9100000017")["estado"], "contestada")
        st, _ = self.decidir("financeiro", objeto="contestacao", id=o["contestacao_id"], decisao="improcedente", causa_raiz="percentual",
                             explicacao="o percentual aplicado é o do termo vigente do escritório")
        self.assertEqual(st, 200)
        self.assertEqual(self.linha("9100000017")["estado"], "aguardando_nf")
        self.assertTrue(any(n["codigo"] == "M-22" for n in self.avisos("usuario:U-0001")))

    def test_procedente_acima_do_limite_so_com_financeiro(self):
        v = [l for l in self.http("GET", "/api/prm/parceiro/extrato", "U-0001")[1]["linhas"] if l["pode_contestar"]][0]
        cid = self.http("POST", "/api/prm/parceiro/extrato/%s/contestar" % v["ref"], "U-0001", {"motivo": "O percentual não bate com o termo assinado."})[1]["contestacao_id"]
        st, o = self.decidir("luis", objeto="contestacao", id=cid, decisao="procedente", causa_raiz="percentual", explicacao="o percentual correto é o do termo")
        self.assertEqual(st, 403)
        st, _ = self.decidir("financeiro", objeto="contestacao", id=cid, decisao="procedente", causa_raiz="percentual", explicacao="o percentual correto é o do termo")
        self.assertEqual(st, 200)

    def test_contestacao_fora_da_janela_vira_demanda(self):
        v = [l for l in self.http("GET", "/api/prm/parceiro/extrato", "U-0001")[1]["linhas"] if l["pode_contestar"]][0]
        self.avancar(days=9)
        st, o = self.http("POST", "/api/prm/parceiro/extrato/%s/contestar" % v["ref"], "U-0001", {"motivo": "O percentual não bate com o termo assinado."})
        self.assertEqual((st, o["fora_da_janela"]), (200, True))
        d = [x for x in self.app.repo.listar("demanda") if x["codigo"] == "REP-COMISSAO"]
        self.assertEqual(len(d), 2)

    def test_pagamento_com_irrf(self):
        st, _ = self.decidir("financeiro", objeto="extrato_linha", id="X-9100000017-REC", decisao="registrar_pagamento", nf="2044")
        x = self.linha("9100000017")
        self.assertEqual((st, x["estado"], x["valor_liquido"]), (200, "pago", 7387.5))
        self.assertTrue(any(n["codigo"] == "M-25" for n in self.avisos("usuario:U-0001")))
        o = self.http("GET", "/api/prm/parceiro/extrato", "U-0001")[1]
        self.assertEqual(o["resumo"]["pago_no_ano"], "R$ 12.312,50")

    def test_conflito_retem_a_linha(self):
        linhas = self.app.repo.listar("extrato_linha")
        self.app.repo.carregar_gerado("extrato_linha", linhas + [{"linha_id": "X-9100000015-REC", "deal_id": "9100000015", "parceiro_id": "P-0003", "master_id": "P-0003",
                                                                   "estado": "previsto", "familia": "recuperacao"}])
        self.decidir("financeiro", objeto="extrato_linha", id="X-9100000015-REC", decisao="registrar_recebimento", valor=1000, competencia="2026-10")
        self.assertEqual(self.linha("9100000015")["estado"], "retida_conflito")

    def test_nada_de_comissao_interna_na_visao(self):
        o = self.http("GET", "/api/prm/parceiro/extrato", "U-0001")[1]
        txt = str(o).lower()
        for t in ("vendedor", "coordenador", "gestor_comercial", "honorario_pct", "margem"):
            self.assertNotIn(t, txt)
