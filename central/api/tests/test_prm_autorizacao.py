"""PRM: autorização em 3 camadas (L2) — token, papel + escopo do escritório, dono da linha (404 fora do escopo, PRM-R02),
login simulado só em localhost, trilha de acesso (L16)."""
import os, uuid

from central_api.prm import identidade as ID
from central_api.prm.erros import NaoAutenticado, SemPermissao
from central_api.token import Chaves
from tests import test_api as TA
from tests.prm_base import BasePRM


class Matriz(BasePRM):
    def test_consultor_nao_ve_extrato(self):
        self.assertFalse(ID.pode(self.ator("U-0002"), "ver_extrato"))
        self.assertTrue(ID.pode(self.ator("U-0001"), "ver_extrato"))

    def test_conflito_so_do_luis(self):
        self.assertFalse(ID.pode(self.ator("daniela"), "decidir_conflito"))
        self.assertTrue(ID.pode(self.ator("luis"), "decidir_conflito"))

    def test_extrato_aprovado_so_pelo_financeiro(self):
        self.assertTrue(ID.pode(self.ator("financeiro"), "aprovar_extrato"))
        self.assertFalse(ID.pode(self.ator("luis"), "aprovar_extrato"))
        self.assertFalse(ID.pode(self.ator("daniela"), "aprovar_extrato"))

    def test_ve_linha_titular_e_consultor(self):
        titular, consultor = self.ator("U-0001"), self.ator("U-0002")
        linha_a2 = {"parceiro_id": "P-0001", "usuario_id": "U-0004"}
        self.assertTrue(ID.ve(titular, linha_a2))
        self.assertFalse(ID.ve(consultor, linha_a2))
        self.assertFalse(ID.ve(self.ator("U-0003"), linha_a2))

    def test_ve_negocio_do_consultor(self):
        consultor = self.ator("U-0002")
        self.assertTrue(ID.ve_negocio(consultor, {"parceiro_id": "P-0010", "master_id": "P-0001"}))
        self.assertFalse(ID.ve_negocio(consultor, {"parceiro_id": "P-0011", "master_id": "P-0001"}))
        self.assertFalse(ID.ve_negocio(consultor, {"parceiro_id": "P-0001", "master_id": "P-0001"}))


class LoginSimulado(BasePRM):
    def test_sem_variavel_nao_entra(self):
        os.environ.pop("PRM_LOGIN_SIMULADO")
        self.assertEqual(self.http("GET", "/api/prm/eu", "U-0001")[0], 401)

    def test_host_de_fora_nao_entra(self):
        self.assertEqual(self.http("GET", "/api/prm/eu", "U-0001", host="parceiros.savecompany.com.br")[0], 401)
        self.assertEqual(self.http("GET", "/api/prm/dev/usuarios", host="evil.example.com")[0], 404)

    def test_na_azure_nunca(self):
        os.environ["WEBSITE_INSTANCE_ID"] = "x"
        try:
            self.assertEqual(self.http("GET", "/api/prm/eu", "U-0001")[0], 401)
        finally:
            os.environ.pop("WEBSITE_INSTANCE_ID")

    def test_lista_de_usuarios_de_teste(self):
        st, o = self.http("GET", "/api/prm/dev/usuarios")
        self.assertEqual(st, 200)
        self.assertIn("daniela", [u["id"] for u in o["usuarios"]])
        self.assertTrue(all(len(c["cnpj"]) == 18 for c in o["cnpjs_de_teste"]))

    def test_usuario_suspenso_nao_entra(self):
        self.app.repo.atualizar("usuario_parceiro", "U-0002", {"estado": "suspenso"})
        st, o = self.http("GET", "/api/prm/eu", "U-0002")
        self.assertEqual((st, o.get("codigo")), (403, "sem_acesso"))


class Token(BasePRM):
    def setUp(self):
        super().setUp()
        ID.configurar([("central", TA.CFG, Chaves(TA.CFG.jwks_url, TA.buscar))])
        os.environ.pop("PRM_LOGIN_SIMULADO")

    def tearDown(self):
        ID._CFG.clear()
        super().tearDown()

    def cab(self, **kw):
        return {"Authorization": "Bearer " + TA.token(**kw)}

    def test_time_save_pelo_papel(self):
        st, o = self.http("GET", "/api/prm/eu", cab=self.cab(roles=["Partners.Masters"]))
        self.assertEqual((st, o["papel"], o["tipo"]), (200, "daniela", "save"))

    def test_parceiro_pelo_oid(self):
        oid = str(uuid.uuid4())
        self.app.repo.atualizar("usuario_parceiro", "U-0001", {"entra_oid": oid})
        st, o = self.http("GET", "/api/prm/eu", cab=self.cab(oid=oid, roles=["Parceiro.Portal"]))
        self.assertEqual((st, o["papel"], o["parceiro_id"]), (200, "titular", "P-0001"))

    def test_oid_desconhecido_nao_entra(self):
        st, _ = self.http("GET", "/api/prm/eu", cab=self.cab(roles=["Parceiro.Portal"]))
        self.assertEqual(st, 403)

    def test_parceiro_em_rota_da_save(self):
        oid = str(uuid.uuid4())
        self.app.repo.atualizar("usuario_parceiro", "U-0001", {"entra_oid": oid})
        self.assertEqual(self.http("GET", "/api/prm/save/canal", cab=self.cab(oid=oid, roles=["Parceiro.Portal"]))[0], 403)

    def test_token_invalido(self):
        self.assertEqual(self.http("GET", "/api/prm/eu", cab={"Authorization": "Bearer isto.nao.e-um-token-valido"})[0], 401)

    def test_sem_token(self):
        st, o = self.http("GET", "/api/prm/eu")
        self.assertEqual((st, o["codigo"]), (401, "sessao"))

    def test_agente_roda_rotina(self):
        st, o = self.http("POST", "/api/prm/save/rotina", cab=self.cab(scp=None, roles=["Agentes.Processar"]))
        self.assertEqual(st, 200)
        self.assertIn("registros", o)


class Linhas(BasePRM):
    """Autorização por linha pela API (PRM-R02): fora do escopo é 404, nunca 403, e fica na trilha."""

    def ref(self, n):
        return self.reg_fx(n)["ref"]

    def test_consultor_nao_abre_empresa_de_outro_consultor(self):
        st, _ = self.http("GET", "/api/prm/parceiro/empresas/" + self.ref("11"), "U-0004")
        self.assertEqual(st, 200)
        self.app.repo.atualizar("usuario_parceiro", "U-0002", {"termos_versao": self.app.param("termos_uso.versao")})
        self.assertEqual(self.http("GET", "/api/prm/parceiro/empresas/" + self.ref("11"), "U-0002")[0], 404)

    def test_titular_ve_o_escritorio(self):
        self.assertEqual(self.http("GET", "/api/prm/parceiro/empresas/" + self.ref("11"), "U-0001")[0], 200)

    def test_outro_escritorio_404(self):
        st, o = self.http("GET", "/api/prm/parceiro/empresas/" + self.ref("01"), "U-0003")
        self.assertEqual(st, 404)
        self.assertNotIn("Empresa 01", str(o))

    def test_negacao_vai_para_a_trilha(self):
        self.http("GET", "/api/prm/parceiro/empresas/" + self.ref("01"), "U-0003")
        negados = [a for a in self.app.repo.listar("acesso_log", usuario_id="U-0003") if a["resultado"] == "negado"]
        self.assertTrue(negados)
        self.assertNotIn(self.cnpj("01"), str(negados))

    def test_lista_do_consultor_so_tem_o_dele(self):
        self.app.repo.atualizar("usuario_parceiro", "U-0002", {"termos_versao": self.app.param("termos_uso.versao")})
        st, o = self.http("GET", "/api/prm/parceiro/empresas", "U-0002")
        nomes = {i["nome"] for i in o["itens"]}
        self.assertIn("Empresa 02 Supermercados Ltda", nomes)
        self.assertNotIn("Empresa 11 Metalúrgica Ltda", nomes)
        self.assertNotIn("Empresa 01 Panificação Ltda", nomes)

    def test_consultor_sem_extrato(self):
        self.app.repo.atualizar("usuario_parceiro", "U-0002", {"termos_versao": self.app.param("termos_uso.versao")})
        st, o = self.http("GET", "/api/prm/parceiro/extrato", "U-0002")
        self.assertEqual(st, 403)
        self.assertIn("titular", o["erro"])

    def test_extrato_de_um_escritorio_nao_mostra_outro(self):
        st, o = self.http("GET", "/api/prm/parceiro/extrato", "U-0003")
        self.assertEqual(st, 200)
        self.assertEqual(len(o["linhas"]), 1)  # só a linha do Master B

    def test_pedido_de_outro_usuario(self):
        dm1 = next(d for d in self.app.repo.listar("demanda") if d["usuario_id"] == "U-0001")
        self.assertEqual(self.http("GET", "/api/prm/parceiro/pedidos/" + dm1["ref"], "U-0004")[0], 404)
        dm2 = next(d for d in self.app.repo.listar("demanda") if d["usuario_id"] == "U-0002")
        self.assertEqual(self.http("GET", "/api/prm/parceiro/pedidos/" + dm2["ref"], "U-0001")[0], 200)

    def test_save_nao_usa_rota_do_parceiro(self):
        self.assertEqual(self.http("GET", "/api/prm/parceiro/inicio", "daniela")[0], 403)
        self.assertEqual(self.http("GET", "/api/prm/save/canal", "U-0001")[0], 403)

    def test_termos_pendentes_428(self):
        st, o = self.http("GET", "/api/prm/parceiro/inicio", "U-0002")
        self.assertEqual((st, o["codigo"]), (428, "termos"))
        v = self.app.param("termos_uso.versao")
        self.assertEqual(self.http("POST", "/api/prm/parceiro/termos/aceitar", "U-0002", {"versao": v, "aceito": True})[0], 200)
        self.assertEqual(self.http("GET", "/api/prm/parceiro/inicio", "U-0002")[0], 200)
        self.assertTrue(self.app.repo.listar("aceite", usuario_id="U-0002"))

    def test_pedido_ligado_a_empresa_de_outro_escritorio(self):
        st, _ = self.http("POST", "/api/prm/parceiro/pedidos", "U-0003", {"tipo": "status", "texto": "Como está esta empresa agora?", "empresa_ref": self.ref("01")})
        self.assertEqual(st, 404)
