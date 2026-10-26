"""PRM · registro de oportunidade (02 §4): checagem única (U1), resposta neutra idêntica e piso de tempo (PRM-R21, R27),
estados, prazos, conflito, prorrogação, expiração, anti-varredura persistente (L4) e regra única de proteção (L14)."""
import os, time
from datetime import timedelta

from central_api import negocio_ativo as NA
from central_api.prm import checagem as CHK
from central_api.prm import registro as RG
from central_api.prm.erros import Conflito, SemPermissao
from central_api.prm.textos import texto as T
from tests.prm_base import BasePRM


def sem_ids(o):
    """Corpo da resposta sem o que muda de um registro para outro (id, ref, carimbo)."""
    o = dict(o)
    o["registro"] = sorted(o["registro"].keys())
    o["mensagem"] = o["mensagem"].split(" em ")[0]
    return o


class Entrada(BasePRM):
    def registrar(self, n, u="U-0001", **kw):
        return self.http("POST", "/api/prm/parceiro/registros", u, self.form(n, **kw))

    def test_livre_cria_em_analise_com_m01(self):
        st, o = self.registrar("06")
        self.assertEqual(st, 201)
        self.assertEqual(o["titulo"], "Registro recebido · em análise")
        self.assertTrue(o["mensagem"].startswith("Registro recebido em 26/10/2026 14:00"))
        r = self.registro_por_cnpj("06")
        self.assertEqual((r["estado"], r["checagem_resultado"], r["carimbo_origem"]), ("em_analise", "livre", "portal"))

    def test_resposta_identica_para_todos_os_casos_neutros(self):
        """Livre, outro parceiro, cliente da Save (espelho e só índice): mesmo status, mesmo corpo, mesmo texto."""
        respostas = {n: self.registrar(n) for n in ("06", "08", "07", "21")}
        self.assertEqual({st for st, _ in respostas.values()}, {201})
        corpos = [sem_ids(o) for _, o in respostas.values()]
        self.assertTrue(all(c == corpos[0] for c in corpos), corpos)
        res = {n: self.registro_por_cnpj(n)["checagem_resultado"] for n in respostas}
        self.assertEqual(res, {"06": "livre", "08": "outro_parceiro", "07": "cliente_save", "21": "cliente_save"})

    def test_indice_ausente_falha_fechada_com_a_mesma_resposta(self):
        os.unlink(NA.INDICE); NA._cache.update(mtime=None, chaves=None)
        st, o = self.registrar("13")
        self.assertEqual((st, sem_ids(o)), (201, sem_ids(self.registrar("06")[1])))
        self.assertEqual(self.registro_por_cnpj("13")["checagem_resultado"], "indice_ausente")

    def test_piso_de_tempo_igual_para_todos(self):
        self.app.param.definir("registro.piso_resposta_ms", 120)
        for n in ("06", "07", "01"):
            t0 = time.monotonic(); self.registrar(n)
            self.assertGreaterEqual(time.monotonic() - t0, 0.12, n)

    def test_ja_registrado_por_voce(self):
        st, o = self.registrar("01")
        self.assertEqual((st, o["resultado"]), (200, "ja_e_seu"))
        self.assertEqual(o["mensagem"], T("M-03a", data="08/07/2026", valido_ate="05/11/2026"))
        self.assertEqual(len(self.app.repo.listar("registro", cnpj_raiz_hmac=self.app.hmac_raiz(self.cnpj("01")))), 1)

    def test_ja_registrado_pelo_escritorio(self):
        self.app.repo.atualizar("usuario_parceiro", "U-0004", {"termos_versao": self.app.param("termos_uso.versao")})
        st, o = self.registrar("01", u="U-0004")
        self.assertEqual(o["resultado"], "ja_e_seu")
        self.assertIn("pelo seu escritório", o["mensagem"])
        self.assertIn("Titular do Master A", o["mensagem"])

    def test_negocio_proprio_sem_registro(self):
        st, o = self.registrar("05")
        self.assertEqual((st, o["resultado"]), (200, "ja_e_seu"))
        self.assertTrue(o["mensagem"].startswith("Esta empresa já está com o seu escritório"))

    def test_campos_obrigatorios(self):
        st, o = self.http("POST", "/api/prm/parceiro/registros", "U-0001", {"cnpj": self.cnpj("06")})
        self.assertEqual(st, 422)
        for c in ("razao_social", "contato_nome", "contato_cargo", "contato_email", "interesse", "como_conhece", "evidencia_tipo", "declaracao_lgpd"):
            self.assertIn(c, o["campos"])

    def test_cnpj_invalido(self):
        st, o = self.registrar("06", cnpj=self.cnpj("06")[:-1] + "9" if not self.cnpj("06").endswith("9") else self.cnpj("06")[:-1] + "8")
        self.assertEqual(st, 422)
        self.assertIn("cnpj", o["campos"])

    def test_dado_pessoal_bloqueia_com_m90(self):
        from tests.test_prm_base_regras import cpf
        st, o = self.registrar("06", contato_nome="Fulano CPF " + cpf())
        self.assertEqual((st, o["codigo"]), (422, "M-90"))
        self.assertIsNone(self.registro_por_cnpj("06"))

    def test_reuniao_exige_data(self):
        st, o = self.registrar("06", evidencia_tipo="reuniao")
        self.assertIn("evidencia_data", o["campos"])

    def test_reenvio_nao_duplica(self):
        a = self.registrar("06", chave_idempotencia="abc-123")[1]
        st, b = self.registrar("06", chave_idempotencia="abc-123")
        self.assertEqual((st, a["registro"]["registro_id"]), (200, b["registro"]["registro_id"]))

    def test_teto_diario_de_registros(self):
        self.app.param.definir("registro.teto_diario_usuario", 1)
        self.registrar("06")
        st, o = self.registrar("13")
        self.assertEqual(st, 201)
        self.assertEqual(o["titulo"], "Registro recebido · em análise")
        self.assertIn("teto", self.registro_por_cnpj("13")["flags"])

    def test_varredura_alerta_e_suspende(self):
        self.app.param.definir("registro.teto_neutros_dia_usuario", 1)
        self.app.param.definir("registro.reincidencias_para_suspender", 1)
        self.registrar("07"); self.registrar("21")
        assuntos = [n["assunto"] for n in self.avisos("luis")]
        self.assertTrue(any("varredura" in a.lower() for a in assuntos))
        self.assertEqual(self.app.repo.obter("usuario_parceiro", "U-0001")["estado"], "suspenso")
        self.assertEqual(self.http("GET", "/api/prm/eu", "U-0001")[0], 403)

    def test_contador_de_neutras_sobrevive_ao_reinicio(self):
        self.registrar("07")
        from central_api.prm.repositorio import RepoJSON
        outro = RepoJSON(self.app.repo.pasta)
        self.assertEqual(outro.valor_contador("neutra|U-0001|2026-10-26"), 1)

    def test_indicador_sem_master_nao_registra(self):
        self.app.repo.gravar("parceiro", {"parceiro_id": "P-0099", "nome_exibicao": "Indicador sem padrinho", "tipo": "indicador", "master_id": None})
        self.app.repo.gravar("usuario_parceiro", {"usuario_id": "U-0099", "parceiro_id": "P-0099", "papel": "titular", "estado": "ativo", "nome": "Teste",
                                                  "termos_versao": self.app.param("termos_uso.versao")})
        self.assertEqual(self.registrar("06", u="U-0099")[0], 403)

    def test_daniela_registra_em_nome_do_parceiro(self):
        corpo = dict(self.form("13"), em_nome_de={"parceiro_id": "P-0002", "usuario_id": "U-0003"}, carimbo_whatsapp="2026-10-26T09:12:00-03:00")
        st, o = self.http("POST", "/api/prm/save/registros", "daniela", corpo)
        self.assertEqual(st, 201)
        r = self.registro_por_cnpj("13")
        self.assertEqual((r["canal_entrada"], r["parceiro_id"], r["carimbo"][:16]), ("whatsapp", "P-0002", "2026-10-26T12:12"))


class Estados(BasePRM):
    def novo(self, n="06", u="U-0001"):
        self.http("POST", "/api/prm/parceiro/registros", u, self.form(n))
        return self.registro_por_cnpj(n)

    def decidir(self, u, **c):
        return self.http("POST", "/api/prm/save/decidir", u, c)

    def test_aprovar_nunca_e_instantaneo(self):
        r = self.novo()
        st, o = self.decidir("daniela", objeto="registro", id=r["registro_id"], decisao="aprovar")
        self.assertEqual((st, o["codigo"]), (409, "cedo"))
        self.avancar(hours=19)  # terça 09h: 4 horas úteis depois (14h–18h)
        st, o = self.decidir("daniela", objeto="registro", id=r["registro_id"], decisao="aprovar")
        self.assertEqual(st, 200)
        r = self.app.repo.obter("registro", r["registro_id"])
        self.assertEqual((r["estado"], r["valido_ate"]), ("aprovado", "2027-02-23"))  # carimbo + 120 dias (Master)

    def test_aprovado_avisa_usuario_e_titular_com_m05(self):
        r = self.novo(u="U-0004")
        antes = {u: len([n for n in self.avisos("usuario:" + u) if n["codigo"] == "M-05"]) for u in ("U-0004", "U-0001")}
        self.avancar(days=1)
        self.decidir("daniela", objeto="registro", id=r["registro_id"], decisao="aprovar")
        for u in ("U-0004", "U-0001"):
            depois = [n for n in self.avisos("usuario:" + u) if n["codigo"] == "M-05"]
            self.assertEqual(len(depois), antes[u] + 1, u)
            self.assertTrue(any("2027" in n["resumo"] for n in depois))

    def test_outro_parceiro_exige_conflito(self):
        r = self.novo("08")
        self.avancar(days=1)
        st, o = self.decidir("daniela", objeto="registro", id=r["registro_id"], decisao="aprovar")
        self.assertEqual((st, o["codigo"]), (409, "exige_conflito"))

    def test_recusa_de_cliente_da_save_so_com_motivo_generico(self):
        r = self.novo("07")
        self.avancar(days=1)
        self.decidir("daniela", objeto="registro", id=r["registro_id"], decisao="nao_aprovar", motivo=3)
        r = self.app.repo.obter("registro", r["registro_id"])
        self.assertEqual(r["motivo_externo"], T("MOTIVO-4"))
        v = RG.visao_parceiro(self.app, r)
        self.assertEqual(v["mensagem"], T("M-11", motivo_externo=T("MOTIVO-4")))
        self.assertNotIn("checagem", v)

    def test_conflito_fica_neutro_para_o_parceiro_e_luis_decide(self):
        r = self.novo("08")
        self.decidir("daniela", objeto="registro", id=r["registro_id"], decisao="enviar_conflito")
        r = self.app.repo.obter("registro", r["registro_id"])
        v = RG.visao_parceiro(self.app, r)
        self.assertEqual((r["estado"], v["estado"], v["rotulo"]), ("em_conflito", "em_analise", "Registro recebido · em análise"))
        st, _ = self.decidir("daniela", objeto="conflito", id=r["conflito_id"], decisao="decidir", vencedor=r["registro_id"])
        self.assertEqual(st, 403)
        self.avancar(days=5)
        st, o = self.decidir("luis", objeto="conflito", id=r["conflito_id"], decisao="decidir", vencedor=r["registro_id"])
        self.assertEqual(st, 200)
        r = self.app.repo.obter("registro", r["registro_id"])
        self.assertEqual((r["estado"], r["dias_pausados"], r["valido_ate"]), ("aprovado", 5, "2027-02-28"))  # +5 dias devolvidos (PRM-R38)

    def test_m04_depois_de_um_dia_util_em_conflito(self):
        r = self.novo("08")
        self.decidir("daniela", objeto="registro", id=r["registro_id"], decisao="enviar_conflito")
        self.avancar(days=1, hours=1)
        RG.rotina(self.app)
        v = RG.visao_parceiro(self.app, self.app.repo.obter("registro", r["registro_id"]))
        self.assertEqual(v["mensagem"], T("M-04"))

    def test_transicoes_proibidas(self):
        r = self.reg_fx("01")  # aprovado
        with self.assertRaises(Conflito):
            RG.transitar(self.app, r, "em_analise", "daniela", "daniela")
        r = self.reg_fx("14")  # encerrado_sem_contrato (final)
        with self.assertRaises(Conflito) as e:
            RG.transitar(self.app, r, "aprovado", "daniela", "daniela")
        self.assertEqual(e.exception.codigo, "estado_final")

    def test_parceiro_nao_aprova(self):
        r = self.novo()
        with self.assertRaises(SemPermissao):
            RG.transitar(self.app, r, "aprovado", "U-0001", "titular")

    def test_esclarecimento_no_prazo_mantem_carimbo(self):
        r = self.novo()
        self.decidir("daniela", objeto="registro", id=r["registro_id"], decisao="pedir_complemento", pergunta="Qual a data da reunião com o sócio?")
        r2 = self.app.repo.obter("registro", r["registro_id"])
        self.assertEqual(r2["estado"], "aguardando_parceiro")
        self.avancar(days=1)
        st, _ = self.http("POST", "/api/prm/parceiro/registros/%s/complemento" % r["ref"], "U-0001", {"resposta": "Reunião marcada para 05/11."})
        r3 = self.app.repo.obter("registro", r["registro_id"])
        self.assertEqual((st, r3["estado"], r3["carimbo"]), (200, "em_analise", r["carimbo"]))

    def test_sem_esclarecimento_no_prazo_vira_recusa_motivo_1(self):
        r = self.reg_fx("16")  # aguardando_parceiro, prazo em 2 dias
        self.avancar(days=4)
        RG.rotina(self.app)
        r = self.app.repo.obter("registro", r["registro_id"])
        self.assertEqual(r["estado"], "recusado")
        self.assertTrue(r["motivo_externo"].startswith("faltam dados obrigatórios"))

    def test_cancelar_so_registro_aprovado(self):
        st, _ = self.http("POST", "/api/prm/parceiro/registros/%s/cancelar" % self.reg_fx("01")["ref"], "U-0001")
        self.assertEqual(st, 200)
        r = self.novo()
        self.assertEqual(self.http("POST", "/api/prm/parceiro/registros/%s/cancelar" % r["ref"], "U-0001")[0], 409)


class Rotina(BasePRM):
    def test_aviso_de_vencimento_uma_vez(self):
        RG.rotina(self.app); RG.rotina(self.app)
        m14 = [n for n in self.avisos("usuario:U-0001") if n["codigo"] == "M-14"]
        self.assertEqual(len(m14), 1)
        self.assertIn("10 dias", m14[0]["resumo"])

    def test_expira_sem_avanco(self):
        self.avancar(days=11)
        RG.rotina(self.app)
        r = self.reg_fx("01")
        self.assertEqual(r["estado"], "expirado")
        self.assertTrue(any(n["codigo"] == "M-09" for n in self.avisos("usuario:U-0001")))

    def test_prorroga_sozinho_com_atividade_recente(self):
        r = self.reg_fx("03")  # convertido, válido até +80
        negs = self.app.repo.listar("negocio")
        for n in negs:
            if n["deal_id"] == r["deal_id"]:
                n["ultima_atividade_em"] = "2027-01-10T10:00:00.000Z"
        self.app.repo.carregar_gerado("negocio", negs)
        self.avancar(days=80)
        RG.rotina(self.app)
        r = self.app.repo.obter("registro", r["registro_id"])
        self.assertEqual((r["estado"], r["prorrogado_ate"]), ("prorrogado", "2027-03-15"))

    def test_converte_e_protege_cliente(self):
        self.http("POST", "/api/prm/parceiro/registros", "U-0001", self.form("06"))
        r = self.registro_por_cnpj("06")
        self.avancar(days=1)
        self.http("POST", "/api/prm/save/decidir", "daniela", {"objeto": "registro", "id": r["registro_id"], "decisao": "aprovar"})
        negs = self.app.repo.listar("negocio")
        novo = {"deal_id": "9199999999", "status": "aberto", "etapa": "Novo Negócio", "parceiro_id": "P-0001", "master_id": "P-0001",
                "cnpj_raiz_hmac": r["cnpj_raiz_hmac"], "cnpj_mascara": r["cnpj_mascara"], "criado_em": "2026-10-27"}
        self.app.repo.carregar_gerado("negocio", negs + [novo])
        RG.rotina(self.app)
        self.assertEqual(self.app.repo.obter("registro", r["registro_id"])["estado"], "convertido")
        novo["status"] = "ganho"; novo["fechado_em"] = "2026-11-10"
        self.app.repo.carregar_gerado("negocio", negs + [novo])
        RG.rotina(self.app)
        self.assertEqual(self.app.repo.obter("registro", r["registro_id"])["estado"], "protegido_cliente")
        cods = {n["codigo"] for n in self.avisos("usuario:U-0001")}
        self.assertTrue({"M-06", "M-08"} <= cods)

    def test_negocio_perdido_encerra_registro(self):
        r = self.reg_fx("03")
        negs = self.app.repo.listar("negocio")
        for n in negs:
            if n["deal_id"] == r["deal_id"]:
                n["status"] = "perdido"
        self.app.repo.carregar_gerado("negocio", negs)
        RG.rotina(self.app)
        self.assertEqual(self.app.repo.obter("registro", r["registro_id"])["estado"], "encerrado_sem_contrato")

    def test_pedido_de_prorrogacao_e_decisao(self):
        r = self.reg_fx("01")
        st, o = self.http("POST", "/api/prm/parceiro/registros/%s/prorrogacao" % r["ref"], "U-0001", {"fato": "Reunião com o sócio feita ontem; documentos pedidos."})
        self.assertEqual(st, 200)
        st, _ = self.http("POST", "/api/prm/save/decidir", "daniela", {"objeto": "registro", "id": r["registro_id"], "decisao": "prorrogar"})
        r = self.app.repo.obter("registro", r["registro_id"])
        self.assertEqual((st, r["estado"], r["prorrogado_ate"]), (200, "prorrogado", "2027-01-04"))
        st, _ = self.http("POST", "/api/prm/parceiro/registros/%s/prorrogacao" % r["ref"], "U-0001", {"fato": "Mais um pedido de prorrogação aqui."})
        self.assertEqual(st, 409)  # uma prorrogação só


class RegraUnica(BasePRM):
    """L14: uma regra de cliente protegido, a mesma para consulta e registro, com o parâmetro da DL-01."""

    def test_ganho_sem_recebimento_continua_protegido(self):
        self.assertEqual(self.app.param("protecao.regra_ativo"), "contrato_12m")
        self.assertEqual(CHK.classificar(self.app, self.cnpj("12"), "P-0001")["resultado"], "outro_parceiro")

    def test_contrato_12m_libera_ganho_com_ultimo_recebimento_antigo(self):
        self.app.repo.inserir("extrato_movimento", {"linha_id": "X-9100000012-REC", "deal_id": "9100000012", "tipo": "recebimento", "para": "recebido_pela_save",
                                                     "quando": "2025-01-10T12:00:00.000Z", "valores": {}})
        self.assertEqual(CHK.classificar(self.app, self.cnpj("12"), "P-0001")["resultado"], "livre")
        self.app.param.definir("protecao.regra_ativo", "qualquer_idade")
        self.assertEqual(CHK.classificar(self.app, self.cnpj("12"), "P-0001")["resultado"], "outro_parceiro")

    def test_consulta_usa_a_mesma_regra(self):
        f = CHK.protecao_para_consulta(self.app, "P-0001", "U-0001")
        self.assertEqual(f(self.cnpj("07")), "negocio_ativo")
        self.assertEqual(f(self.cnpj("08")), "registro_ou_negocio_de_outro_parceiro")
        self.assertFalse(f(self.cnpj("06")))
