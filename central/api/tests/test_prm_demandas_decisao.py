"""PRM: demandas (U2, histórico antes do chamado, GLPI só rascunho), decidir com trilha (U4), notificações (U3), nível em
sombra, visão do canal e rotas HTTP."""
from datetime import datetime

from central_api.prm import calendario as CAL
from central_api.prm import demandas as DM
from central_api.prm import notificacoes as NT
from central_api.prm import rotas as R
from central_api.prm.textos import texto as T
from tests.prm_base import BasePRM


class Demandas(BasePRM):
    def abrir(self, texto, tipo="status", u="U-0001", **kw):
        return self.http("POST", "/api/prm/parceiro/pedidos", u, dict(tipo=tipo, texto=texto, **kw))

    def dem(self, ref):
        return next(d for d in self.app.repo.listar("demanda") if d["ref"] == ref)

    def decidir(self, u, **c):
        return self.http("POST", "/api/prm/save/decidir", u, c)

    def test_abrir_numera_e_avisa_m30(self):
        st, o = self.abrir("Preciso de uma reunião com a empresa e o técnico.", tipo="reuniao")
        self.assertEqual(st, 201)
        self.assertRegex(o["id"], r"^D-2026-\d{4}$")
        self.assertTrue(any(n["codigo"] == "M-30" for n in self.avisos("usuario:U-0001")))
        self.assertEqual(o["prazo"], T("DEM-primeira-resposta", primeira_resposta=0))  # R71: SLA não validado → só a 1ª resposta

    def test_historico_tem_resposta_vira_rascunho_que_o_parceiro_nao_ve(self):
        st, o = self.abrir("Quais documentos preciso enviar para o diagnóstico desta empresa?", tipo="documento")
        d = self.dem(o["ref"])
        self.assertEqual(d["estado"], "resposta_historico")
        self.assertIn("ECF", d["historico"]["rascunho"])
        self.assertEqual(o["rotulo"], "Em preparo")
        self.assertNotIn("ECF", str(o))

    def test_sem_historico_vai_para_chamado_em_rascunho(self):
        st, o = self.abrir("A empresa recebeu uma intimação sobre um pedido antigo, o que fazemos?", tipo="tecnica")
        d = self.dem(o["ref"])
        self.assertEqual((d["estado"], d["chamado"]["estado"], d["chamado"]["glpi"]), ("triada", "rascunho", "nao_enviado"))
        self.assertIn("O que o parceiro pede", d["chamado"]["descricao"])

    def test_dado_pessoal_bloqueia(self):
        from tests.test_prm_base_regras import cpf
        st, o = self.abrir("O sócio tem CPF " + cpf() + " e quer saber o status.")
        self.assertEqual((st, o["codigo"]), (422, "M-90"))

    def test_tipo_fora_da_lista(self):
        self.assertEqual(self.abrir("Texto qualquer de pedido aqui.", tipo="inventado")[0], 422)

    def test_resposta_passa_pelo_auditor(self):
        o = self.abrir("A empresa recebeu uma intimação sobre um pedido antigo, o que fazemos?", tipo="tecnica")[1]
        d = self.dem(o["ref"])
        st, e = self.decidir("daniela", objeto="demanda", id=d["demanda_id"], decisao="aprovar_envio", texto="Fique tranquilo, garantimos o resultado sem risco.")
        self.assertEqual((st, e["codigo"]), (422, "auditor"))
        st, _ = self.decidir("daniela", objeto="demanda", id=d["demanda_id"], decisao="aprovar_envio", texto="O Jurídico vai ler a intimação hoje e retorna aqui com o caminho.")
        v = self.http("GET", "/api/prm/parceiro/pedidos/" + o["ref"], "U-0001")[1]
        self.assertEqual((st, v["estado"], v["mensagens"][-1]["selo"]), (200, "respondida", T("DEM-selo-area", area="Técnico")))

    def test_resposta_do_historico_leva_o_selo(self):
        o = self.abrir("Quais documentos preciso enviar para o diagnóstico desta empresa?", tipo="documento")[1]
        d = self.dem(o["ref"])
        self.decidir("daniela", objeto="demanda", id=d["demanda_id"], decisao="aprovar_envio")
        v = self.http("GET", "/api/prm/parceiro/pedidos/" + o["ref"], "U-0001")[1]
        self.assertEqual(v["mensagens"][-1]["selo"], T("DEM-selo-historico"))

    def test_encaminhar_aprova_chamado_sem_tocar_o_glpi(self):
        o = self.abrir("A empresa recebeu uma intimação sobre um pedido antigo, o que fazemos?", tipo="tecnica")[1]
        d = self.dem(o["ref"])
        st, _ = self.decidir("daniela", objeto="demanda", id=d["demanda_id"], decisao="encaminhar")
        d = self.dem(o["ref"])
        self.assertEqual((st, d["estado"], d["chamado"]["glpi"]), (200, "encaminhada_area", "abrir_manualmente"))
        self.assertTrue(any(n["codigo"] == "M-32-sem-previsao" for n in self.avisos("usuario:U-0001")))

    def test_pedir_dados_e_complemento(self):
        o = self.abrir("A empresa recebeu uma intimação sobre um pedido antigo, o que fazemos?", tipo="tecnica")[1]
        d = self.dem(o["ref"])
        self.decidir("daniela", objeto="demanda", id=d["demanda_id"], decisao="pedir_dados", itens="cópia da intimação e a data de ciência")
        self.assertEqual(self.dem(o["ref"])["estado"], "aguardando_parceiro")
        st, v = self.http("POST", "/api/prm/parceiro/pedidos/%s/complemento" % o["ref"], "U-0001", {"texto": "Ciência em 20/10; envio a cópia pelo canal de sempre."})
        self.assertEqual((st, v["estado"]), (200, "triada"))

    def test_concluir_e_reabrir_em_7_dias(self):
        dm1 = next(d for d in self.app.repo.listar("demanda") if d["estado"] == "respondida")
        self.http("POST", "/api/prm/parceiro/pedidos/%s/concluir" % dm1["ref"], "U-0001")
        self.avancar(days=3)
        st, v = self.http("POST", "/api/prm/parceiro/pedidos/%s/reabrir" % dm1["ref"], "U-0001", {"texto": "Ainda não está claro."})
        self.assertEqual(st, 200)
        self.assertIn(v["estado"], ("triada", "resposta_historico"))

    def test_reabrir_depois_do_prazo(self):
        dm1 = next(d for d in self.app.repo.listar("demanda") if d["estado"] == "respondida")
        self.http("POST", "/api/prm/parceiro/pedidos/%s/concluir" % dm1["ref"], "U-0001")
        self.avancar(days=8)
        self.assertEqual(self.http("POST", "/api/prm/parceiro/pedidos/%s/reabrir" % dm1["ref"], "U-0001")[0], 409)

    def test_escala_e_m33_uma_vez(self):
        DM.rotina(self.app); DM.rotina(self.app)
        dm3 = next(d for d in self.app.repo.listar("demanda") if d["codigo"] == "REP-COMISSAO")
        self.assertGreaterEqual(dm3["escala"], 1)
        self.assertEqual(len([n for n in self.avisos("usuario:U-0001") if n["codigo"] == "M-33"]), 1)
        self.assertTrue(any("fora do prazo" in n["assunto"].lower() for n in self.avisos("financeiro")))

    def test_conclui_sozinha_sem_reacao(self):
        self.avancar(days=8)
        DM.rotina(self.app)
        self.assertTrue(any(d["estado"] == "concluida" for d in self.app.repo.listar("demanda")))

    def test_reclamacao_avisa_o_luis(self):
        self.abrir("Fiquei insatisfeito com o atendimento da última reunião.", tipo="reclamacao")
        self.assertTrue(any("Reclamação" in n["assunto"] for n in self.avisos("luis")))

    def test_fila_unica_com_registro_unico(self):
        o = self.http("GET", "/api/prm/save/demandas", "daniela")[1]
        self.assertTrue(o["itens"])
        self.assertEqual({x["id"] for x in o["registro_unico"]}, {"D-2026-0901", "D-2026-0902"})
        self.assertTrue(all("sla" in x for x in o["itens"]))


class Decidir(BasePRM):
    def test_trilha_com_identidade_e_estados(self):
        self.http("POST", "/api/prm/parceiro/registros", "U-0001", self.form("06"))
        r = self.registro_por_cnpj("06")
        self.avancar(days=1)
        st, o = self.http("POST", "/api/prm/save/decidir", "daniela", {"objeto": "registro", "id": r["registro_id"], "decisao": "aprovar"})
        t = self.app.repo.obter("decisao", o["trilha"])
        self.assertEqual((t["papel"], t["antes"], t["depois"], t["resultado"], t["oid"]), ("daniela", "em_analise", "aprovado", "aprovado", "local-daniela"))
        ev = [e for e in self.app.repo.listar("registro_evento", registro_id=r["registro_id"])]
        self.assertEqual([e["para_estado"] for e in ev], ["em_analise", "aprovado"])

    def test_decisao_desconhecida(self):
        self.assertEqual(self.http("POST", "/api/prm/save/decidir", "daniela", {"objeto": "registro", "id": "x", "decisao": "apagar"})[0], 422)

    def test_papel_errado(self):
        self.assertEqual(self.http("POST", "/api/prm/save/decidir", "daniela", {"objeto": "extrato_lote", "id": "P-0001|2026-10", "decisao": "liberar"})[0], 403)

    def test_suspender_acesso(self):
        st, _ = self.http("POST", "/api/prm/save/decidir", "daniela", {"objeto": "usuario", "id": "U-0004", "decisao": "suspender", "motivo_interno": "teste"})
        self.assertEqual(st, 200)
        self.assertEqual(self.http("GET", "/api/prm/eu", "U-0004")[0], 403)

    def test_parametro_com_dona_e_trilha(self):
        st, _ = self.http("POST", "/api/prm/save/decidir", "daniela", {"objeto": "parametro", "id": "registro.teto_diario_usuario", "decisao": "alterar", "valor": 8})
        self.assertEqual((st, self.app.param("registro.teto_diario_usuario")), (200, 8))
        st, _ = self.http("POST", "/api/prm/save/decidir", "daniela", {"objeto": "parametro", "id": "registro.validade_master_dias", "decisao": "alterar", "valor": 180})
        self.assertEqual(st, 403)
        self.assertEqual(len(self.app.repo.listar("config_evento")), 1)

    def test_trilha_so_para_quem_pode(self):
        self.assertEqual(self.http("GET", "/api/prm/save/trilha", "financeiro")[0], 403)
        self.assertEqual(self.http("GET", "/api/prm/save/trilha", "luis")[0], 200)

    def test_pendencia_marcada_pela_save(self):
        st, _ = self.http("POST", "/api/prm/save/decidir", "daniela", {"objeto": "pendencia", "id": "9100000003", "decisao": "abrir", "tipo": "procuracao",
                                                                       "texto": "procuração do e-CAC assinada pelo cliente"})
        self.assertEqual(st, 200)
        emp = self.http("GET", "/api/prm/parceiro/empresas", "U-0001")[1]
        self.assertEqual(emp["abas"]["precisa_de_voce"], 3)


class Avisos(BasePRM):
    def test_formato_da_caixa(self):
        n = self.avisos("usuario:U-0001")[0]
        for k in ("id", "para", "assunto", "resumo", "origem", "tipo", "prioridade", "anexos", "acoes", "criado_em", "lido_por", "auditoria"):
            self.assertIn(k, n)

    def test_idempotente(self):
        a = NT.avisar_usuario(self.app, "U-0001", "M-04", chave="x")
        b = NT.avisar_usuario(self.app, "U-0001", "M-04", chave="x")
        self.assertEqual(a, b)
        self.assertEqual(len([n for n in self.avisos("usuario:U-0001") if n["codigo"] == "M-04"]), 1)

    def test_marcar_lidas_so_as_proprias(self):
        alvo = self.avisos("usuario:U-0003")[0]["id"]
        st, o = self.http("POST", "/api/prm/parceiro/avisos/lidos", "U-0001", {"ids": [alvo]})
        self.assertEqual(o["marcados"], 0)
        st, o = self.http("POST", "/api/prm/parceiro/avisos/lidos", "U-0001", {})
        self.assertGreater(o["marcados"], 0)

    def test_email_respeita_a_janela(self):
        self.t[0] = datetime(2026, 10, 24, 22, 0, tzinfo=CAL.FUSO)
        i = NT.avisar_usuario(self.app, "U-0001", "M-04", chave="janela")
        self.assertTrue(self.app.repo.obter("notificacao", i)["email_apos"].startswith("2026-10-26T07:00"))

    def test_alerta_interno_sem_telefone(self):
        i = NT.alertar_save(self.app, "daniela", "Teste", "Ligar para (11) 3000-1234 hoje")
        self.assertNotIn("3000-1234", self.app.repo.obter("notificacao", i)["resumo"])


class CanalENivel(BasePRM):
    def test_nivel_do_parceiro_sem_faixa_nem_valor(self):
        o = self.http("GET", "/api/prm/parceiro/nivel", "U-0001")[1]
        self.assertEqual(o["selo"], "Em teste")
        for k in ("faixa_simulada", "volume_12m", "pct_do_proximo"):
            self.assertNotIn(k, str(o))
        self.assertEqual([p["titulo"] for p in o["jornada"]], ["Registrado", "Certificado", "Pleno", "Master"])

    def test_nivel_em_sombra_para_a_save(self):
        o = self.http("GET", "/api/prm/save/niveis", "luis")[1]
        a = next(x for x in o["itens"] if x["parceiro_id"] == "P-0001")
        self.assertIn(a["faixa_simulada"], ("master", "avancado", "estrategico"))
        self.assertEqual(o["modo"], "sombra")

    def test_visao_do_canal(self):
        st, o = self.http("GET", "/api/prm/save/canal", "daniela")
        self.assertEqual(st, 200)
        k = {x["chave"]: x["valor"] for x in o["kpis"]}
        self.assertEqual((k["registros"], k["conflitos"]), (2, 1))
        self.assertTrue(any(s["nome"] == "Master A" for s in o["saude"]))

    def test_fila_de_registros_mostra_a_checagem_so_a_save(self):
        o = self.http("GET", "/api/prm/save/registros", "daniela")[1]
        self.assertTrue(all("checagem" in x for x in o["itens"]))
        p = self.http("GET", "/api/prm/parceiro/empresas", "U-0001")[1]
        self.assertNotIn("checagem", str(p))
        self.assertNotIn("outro_parceiro", str(p))

    def test_conflitos_e_acessos(self):
        c = self.http("GET", "/api/prm/save/conflitos", "luis")[1]["itens"][0]
        self.assertTrue(c["pode_decidir"])
        self.assertFalse(self.http("GET", "/api/prm/save/conflitos", "daniela")[1]["itens"][0]["pode_decidir"])
        a = self.http("GET", "/api/prm/save/acessos", "daniela")[1]
        self.assertEqual(len(a["usuarios"]), 4)
        self.assertEqual(self.http("GET", "/api/prm/save/acessos", "financeiro")[0], 403)

    def test_inicio_do_parceiro(self):
        o = self.http("GET", "/api/prm/parceiro/inicio", "U-0001")[1]
        self.assertLessEqual(len(o["pede_voce"]), 3)
        self.assertGreaterEqual(o["pede_voce_total"], 3)
        self.assertEqual(set(o["kpis"]), {"pedem_voce", "em_andamento", "registros_validos", "respostas_novas", "empresas"})


class Http(BasePRM):
    def test_rota_inexistente_e_metodo(self):
        self.assertEqual(self.http("GET", "/api/prm/nada", "U-0001")[0], 404)
        self.assertEqual(self.http("POST", "/api/prm/eu", "U-0001")[0], 405)

    def test_erro_interno_neutro(self):
        antes = R.ROTAS[0]
        R.ROTAS[0] = (antes[0], antes[1], lambda *a: 1 / 0, antes[3], antes[4])
        try:
            st, o = self.http("GET", "/api/prm/eu", "U-0001")
        finally:
            R.ROTAS[0] = antes
        self.assertEqual(st, 500)
        self.assertNotIn("Zero", str(o))

    def test_rotas_antigas_da_esteira_exigem_identidade(self):
        from central_api import rotas as RC
        st, _ = RC.regime_lote({"Host": "localhost"}, {"cnpjs": [self.cnpj("06")]})
        self.assertEqual(st, 401)
        st, o = RC.regime_lote({"Host": "localhost", "X-PRM-Dev-Usuario": "U-0001"}, {"cnpjs": [self.cnpj("06")]})
        self.assertEqual((st, o["resultados"][0]["faixa"]), (200, "confirmado_real"))
        st, o = RC.esteira_historico({"Host": "localhost", "X-PRM-Dev-Usuario": "U-0001"})
        self.assertEqual(st, 200)
        self.assertTrue(o["empresas"])

    def test_esteira_pedir_pelo_token(self):
        from central_api import rotas as RC
        st, o = RC.esteira_pedir({"Host": "localhost", "X-PRM-Dev-Usuario": "U-0001"}, {"cnpj": self.cnpj("13")})
        self.assertEqual(st, 200)
        st2, o2 = RC.esteira_andamento({"Host": "localhost", "X-PRM-Dev-Usuario": "U-0001"}, o["id"])
        self.assertEqual((st2, o2["id"]), (200, o["id"]))
        self.assertEqual(RC.esteira_andamento({"Host": "localhost", "X-PRM-Dev-Usuario": "U-0003"}, o["id"])[0], 404)

    def test_fixtures_sem_cnpj_completo_no_arquivo(self):
        import re
        from cnpj import CNPJ_TEXTO_ALFA, cnpj_valido
        from central_api.prm import fixtures as F
        with open(F.ARQ, encoding="utf-8") as f:
            txt = f.read()
        self.assertFalse([m for m in CNPJ_TEXTO_ALFA.findall(txt) if cnpj_valido(m)])
        self.assertFalse([m for m in re.findall(r"\d{14}", txt) if cnpj_valido(m)])
