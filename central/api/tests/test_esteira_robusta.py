"""Testes de robustez da esteira, do histórico, da consulta por API e da demo (travessia de caminho, corrida, arquivo
corrompido, teto de uso, lista de bloqueio, retenção). Nada vai à rede; tudo roda em pasta temporária.

    cd central/api && PYTHONPATH=../../lib python3 -W error::ResourceWarning -m unittest -v tests.test_esteira_robusta
"""
import http.client, http.server, json, os, sys, tempfile, threading, time, unittest
from pathlib import Path

from central_api import dossie as DS
from central_api import dossie_base as DB
from central_api import esteira as E
from central_api import negocio_ativo as NA
from central_api import regime as R
from cnpj import dv_cnpj

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import consulta_demo as D  # noqa: E402

os.environ["CENTRAL_SAL"] = "sal-de-teste"


def cnpj(raiz, ordem="0001"):
    b = raiz + ordem
    return b + dv_cnpj(b)


NOVO, OUTRO, FILIAL, ALFA, CLIENTE = cnpj("11111111"), cnpj("22222222"), cnpj("11111111", "0002"), cnpj("AB12CD34"), cnpj("99999999")
SECAO = [{"titulo": "Seção %d" % i, "paragrafos": ["Texto de apoio da seção %d, sem valor nem prazo." % i]} for i in range(1, 7)]
LIMPO = {"fazer": "A empresa não tem negócio na base. A pré-análise indica as teses a verificar com os documentos.",
         "precisa": "Veja a esteira em três ondas; a ordem depende da análise.", "falta": "ECF e EFD-Contribuições dos últimos 5 anos, pelo cliente.",
         "esteira": [{"onda": 1, "produto": "Recuperação tributária", "status": "pronto", "nota": "Depende de parecer e documentos."}], "dossie": SECAO}
PERFIL = {"razao": "EMPRESA TESTE SA", "cnae": {"codigo": "1051100", "descricao": "laticínios"}, "cnaes_secundarios": [], "capital_social": 5e6,
          "inicio_atividade": "2001-02-03", "municipio": "BELO HORIZONTE", "uf": "MG", "porte": "Demais", "natureza_juridica": "SA", "matriz": True,
          "ecf": [{"ano": 2022, "forma": "LUCRO PRESUMIDO"}, {"ano": 2023, "forma": "LUCRO REAL"}, {"ano": 2024, "forma": "LUCRO REAL"}]}


def consulta(c, faixa="confirmado_real", perfil=None):
    return {"cnpj": c, "faixa": faixa, "titulo": "t", "ano_base": 2024, "fonte": "f", "perfil": perfil, "empresa": {"razao": "X"}}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.antes = (E.DIR, NA.DIR, NA.INDICE, NA._carregar, R.BASE, R._http, E.DB.montar, DS.gerar_docx)
        E.DIR = NA.DIR = self.tmp.name; NA.INDICE = os.path.join(self.tmp.name, "i.json"); R.BASE = os.path.join(self.tmp.name, "receita")
        NA._carregar = lambda: {NA.chave("99999999")}
        os.environ.pop("CENTRAL_APROVACAO", None); os.environ["CENTRAL_API_EXTERNA"] = "1"
        R._memoria.clear(); R._uso.clear(); R._ativos.clear()

    def tearDown(self):
        E.DIR, NA.DIR, NA.INDICE, NA._carregar, R.BASE, R._http, E.DB.montar, DS.gerar_docx = self.antes
        self.tmp.cleanup(); os.environ.pop("CENTRAL_APROVACAO", None)

    def pedido(self, c=NOVO, parceiro="p1", **kw):
        return E.solicitar(c, parceiro, consulta(c, **kw))


class Caminho(Base):
    def test_id_malformado_nunca_vira_caminho(self):
        # arquivo "secreto" fora de pedidos/, no formato de um pedido
        Path(self.tmp.name, "segredo.json").write_text(json.dumps({"id": "../segredo", "cnpj": "x", "parceiro": "p1", "criado": "2000", "status": "entregue", "resultado": {}}))
        for ruim in ("../segredo", "../pedidos/../segredo", "E-1/../../segredo", "E-0001\n", "E-０００１", "e-0001", "", None, 7, "E-" + "9" * 12, "/etc/passwd", "E-0001.json"):
            self.assertIsNone(E._ler(ruim), ruim); self.assertIsNone(E.ler_do_parceiro(ruim, "p1")); self.assertIsNone(E.arquivo_do_parceiro(ruim, "p1"))
        with self.assertRaises(ValueError): E._arq("../x")
        with self.assertRaises(E.Recusa): E.aprovar("../segredo", "x")
        with self.assertRaises(E.Recusa): E.publicar("../segredo", LIMPO)

    def test_pedido_corrompido_ou_de_outro_formato_e_ignorado(self):
        p = self.pedido(); pasta = os.path.join(self.tmp.name, "pedidos")
        Path(pasta, "E-0007.json").write_text("{quebrado")
        Path(pasta, "E-0008.json").write_text("[1, 2]")
        Path(pasta, "E-0009.json").write_text(json.dumps({"id": "E-0009"}))  # faltam chaves
        Path(pasta, "E-0010.json").write_text(json.dumps({"id": "E-0001", "cnpj": "x", "parceiro": "p", "criado": "c", "status": "s"}))  # id não confere
        self.assertEqual([x["id"] for x in E._todos()], [p["id"]])
        self.assertEqual(self.pedido()["id"], p["id"])  # e a numeração segue sem quebrar

    def test_escrita_atomica_sem_sobras(self):
        self.pedido(); self.assertEqual([n for n in os.listdir(os.path.join(self.tmp.name, "pedidos")) if not n.endswith(".json")], [])


class Historico(Base):
    def test_registra_ordena_dedupe_e_limita(self):
        for i in range(E.HISTORICO_MAX + 5):
            c = cnpj("%08d" % (30000000 + i)); E.registrar_consulta("p1", consulta(c))
        E.registrar_consulta("p1", consulta(cnpj("30000010")))  # repetida volta ao topo, sem duplicar
        h = E.historico("p1")
        self.assertEqual(len(h), E.HISTORICO_MAX); self.assertEqual(h[0]["cnpj"], cnpj("30000010"))
        self.assertEqual(len({x["cnpj"] for x in h}), E.HISTORICO_MAX)
        self.assertEqual(E.historico("p2"), [])  # outro parceiro (outro hash) não vê

    def test_invalido_e_indisponivel_nao_entram(self):
        for faixa in ("invalido", "indisponivel"): E.registrar_consulta("p1", consulta(NOVO, faixa))
        E.registrar_consulta("p1", {"faixa": "sem_dado"}); E.registrar_consulta("p1", None)
        self.assertEqual(E.historico("p1"), [])

    def test_historico_corrompido_vale_vazio(self):
        E.registrar_consulta("p1", consulta(NOVO)); arq = E._arq_hist("p1")
        for lixo in ("{quebrado", "{}", '"texto"', json.dumps([1, {"cnpj": 1}, {"cnpj": "a", "quando": "b", "resultado": {}}])):
            Path(arq).write_text(lixo)
            self.assertIsInstance(E.historico("p1"), list)
        Path(arq).write_text("{quebrado"); E.registrar_consulta("p1", consulta(OUTRO))  # e se recompõe
        self.assertEqual([x["cnpj"] for x in E.historico("p1")], [OUTRO])

    def test_historico_traz_andamento_do_pedido(self):
        p = self.pedido(); E.registrar_consulta("p1", consulta(NOVO))
        self.assertEqual(E.historico("p1")[0]["pedido"]["id"], p["id"])

    def test_consulta_guardada_vence_em_7_dias(self):
        E.registrar_consulta("p1", consulta(NOVO))
        self.assertIsNotNone(E.consulta_guardada("p1", NOVO))
        self.assertIsNone(E.consulta_guardada("p1", NOVO, dias=-1)); self.assertIsNone(E.consulta_guardada("p2", NOVO))
        h = E._hist_ler("p1"); h[0]["quando"] = "2000-01-01T00:00:00"; E._gravar_json(E._arq_hist("p1"), h)
        self.assertIsNone(E.consulta_guardada("p1", NOVO))

    def test_consulta_guardada_refaz_a_checagem_de_negocio_ativo(self):
        E.registrar_consulta("p1", consulta(NOVO))
        NA._carregar = lambda: {NA.chave("11111111")}  # virou cliente depois da consulta
        self.assertIsNone(E.consulta_guardada("p1", NOVO))
        NA._carregar = lambda: None  # sem índice: falha fechada
        self.assertIsNone(E.consulta_guardada("p1", NOVO))

    def test_consulta_sem_dados_da_empresa_nao_e_reaproveitada(self):
        E.registrar_consulta("p1", {"cnpj": NOVO, "faixa": "sem_dado", "titulo": "CNPJ não localizado", "empresa": None})
        self.assertIsNone(E.consulta_guardada("p1", NOVO))

    def test_cnpj_sem_zeros_a_esquerda_e_o_mesmo(self):
        c = cnpj("01111111"); curto = c.lstrip("0")
        a = E.solicitar(c, "p1", consulta(c)); b = E.solicitar(curto, "p1", consulta(c))
        self.assertEqual((a["id"], a["cnpj"]), (b["id"], c))


class Reuso(Base):
    def test_entregue_recente_e_reaproveitado_e_antigo_nao(self):
        os.environ["CENTRAL_APROVACAO"] = "autonoma"
        a = self.pedido(); E.publicar(a["id"], LIMPO)
        self.assertEqual(self.pedido()["id"], a["id"])
        p = E._ler(a["id"]); p["criado"] = E._corte(E.REUSO_DIAS + 1); E._gravar(p)
        b = self.pedido(); self.assertNotEqual(b["id"], a["id"])

    def test_filial_da_mesma_raiz_e_pedido_distinto_e_cnpj_alfanumerico_funciona(self):
        a, b, c = self.pedido(NOVO), self.pedido(FILIAL), self.pedido(ALFA)
        self.assertEqual(len({a["id"], b["id"], c["id"]}), 3); self.assertEqual(c["cnpj"], ALFA)
        self.assertEqual(self.pedido(ALFA.lower())["id"], c["id"])

    def test_pedidos_simultaneos_nao_repetem_id_nem_travam(self):
        ids, erros = [], []

        def uma(i):
            try: ids.append(E.solicitar(NOVO, "p%d" % i, consulta(NOVO))["id"])
            except Exception as e: erros.append(e)
        ts = [threading.Thread(target=uma, args=(i,)) for i in range(12)]
        [t.start() for t in ts]; [t.join(20) for t in ts]
        self.assertFalse(any(t.is_alive() for t in ts), "deadlock"); self.assertEqual(erros, []); self.assertEqual(len(set(ids)), 12)

    def test_mesmo_parceiro_simultaneo_gera_um_pedido_so(self):
        ids = []
        ts = [threading.Thread(target=lambda: ids.append(E.solicitar(NOVO, "p1", consulta(NOVO))["id"])) for _ in range(8)]
        [t.start() for t in ts]; [t.join(20) for t in ts]
        self.assertEqual(len(set(ids)), 1)


class DossieBase(Base):
    def test_solicitar_entrega_o_dossie_base_na_hora(self):
        os.environ["CENTRAL_APROVACAO"] = "autonoma"
        p = self.pedido(perfil=PERFIL); self.assertEqual((p["status"], p["nivel"]), ("entregue", "base"))
        self.assertTrue(E.ler_do_parceiro(p["id"], "p1")["aprofundando"])

    def test_falha_ao_montar_o_base_nao_derruba_o_pedido(self):
        for erro in (KeyError("x"), AttributeError("y"), IndexError("z"), OSError("w"), ValueError("v")):
            def quebra(*a, **k): raise erro
            E.DB.montar = quebra
            p = E.solicitar(cnpj("%08d" % (50000000 + id(erro) % 1000)), "p1", consulta(NOVO, perfil=PERFIL))
            self.assertEqual(p["status"], "recebida")

    def test_montar_com_perfil_saneado_da_api_nunca_quebra(self):
        # o perfil que a consulta entrega ao dossiê passa por regime._sanear: ecf sem forma ou sem ano nunca chega
        for d in (dict(JSON_API, regime_tributario=[{"ano": 2024, "forma_de_tributacao": None}]), dict(JSON_API, regime_tributario=None), dict(JSON_API, cnae_fiscal=None)):
            R._http = lambda url, d=d: (200, d); R._memoria.clear(); r = R.consultar(NOVO)
            self.assertTrue(DS.valido(DB.montar(r["perfil"], r["faixa"])["dossie"]))

    def test_montar_aguenta_campos_nulos_e_cnae_desconhecido(self):
        for perfil in ({}, {"razao": None, "cnae": None, "ecf": None, "cnaes_secundarios": None, "capital_social": None},
                       dict(PERFIL, cnae={"codigo": "9999999", "descricao": None}), dict(PERFIL, cnae={"codigo": None}),
                       dict(PERFIL, ecf=[{"ano": None, "forma": None}, {"ano": 2024, "forma": "LUCRO REAL"}], municipio=None, uf=None, porte=None, inicio_atividade=None)):
            for faixa in ("confirmado_real", "provavel_real", "nao_real", "sem_dado", None):
                r = DB.montar(perfil, faixa)
                self.assertTrue(DS.valido(r["dossie"]), (perfil, faixa))
                for b in E.BLOCOS: self.assertTrue(r[b].strip())

    def test_dossie_base_de_todos_os_setores_passa_na_lista_de_bloqueio(self):
        vistos = 0
        for _, _, cnaes in DB.SETORES:
            for cn in list(cnaes)[:1]:
                r = DB.montar(dict(PERFIL, cnae={"codigo": cn + "00", "descricao": "x"}), "confirmado_real"); vistos += 1
                self.assertEqual(E.trava_regex(E._texto(r)), [], cn)
        self.assertGreater(vistos, 3)
        for faixa in ("nao_real", "provavel_real", "sem_dado"): self.assertEqual(E.trava_regex(E._texto(DB.montar(PERFIL, faixa))), [])


class Enriquecer(Base):
    def setUp(self):
        super().setUp(); os.environ["CENTRAL_APROVACAO"] = "autonoma"

    def test_aprofunda_troca_o_resultado_e_o_word_velho(self):
        p = self.pedido(perfil=PERFIL)
        E.DS.gerar_docx = lambda md, saida, **k: Path(saida).write_bytes(b"VELHO") or saida
        self.assertEqual(Path(E.arquivo_do_parceiro(p["id"], "p1")).read_bytes(), b"VELHO")
        novo = dict(LIMPO, fazer="Versão aprofundada pelos agentes, sem valor nem prazo.")
        r = E.enriquecer(p["id"], novo)
        self.assertEqual((r["enriquecer"], r["nivel"]), ("feito", "agentes")); self.assertEqual(E.ler_do_parceiro(p["id"], "p1")["resultado"]["fazer"], novo["fazer"])
        self.assertFalse(os.path.exists(E._docx(p["id"])), "Word do dossiê-base ficou velho")
        with self.assertRaises(E.Recusa): E.enriquecer(p["id"], novo)  # já feito

    def test_com_promessa_mantem_a_versao_atual_e_permite_duas_tentativas(self):
        p = self.pedido(perfil=PERFIL); base = E.ler_do_parceiro(p["id"], "p1")["resultado"]
        ruim = dict(LIMPO, fazer="A Save garante recuperação de R$ 500 mil em 30 dias, sem risco.")
        r = E.enriquecer(p["id"], ruim); self.assertEqual((r["enriquecer"], r["tentativas_enriquecer"]), ("alerta", 1))
        self.assertEqual(E.ler_do_parceiro(p["id"], "p1")["resultado"], base)
        self.assertIn(p["id"], [x["id"] for x in json.loads(self.fila())])  # volta para a fila
        E.enriquecer(p["id"], ruim); self.assertEqual(E._ler(p["id"])["tentativas_enriquecer"], 2)
        with self.assertRaises(E.Recusa): E.enriquecer(p["id"], LIMPO)  # 3ª não
        self.assertNotIn(p["id"], [x["id"] for x in json.loads(self.fila())])

    def test_alerta_seguido_de_texto_limpo_aprofunda(self):
        p = self.pedido(perfil=PERFIL)
        E.enriquecer(p["id"], dict(LIMPO, fazer="Garantia de êxito."))
        self.assertEqual(E.enriquecer(p["id"], LIMPO)["enriquecer"], "feito")

    def test_incompleto_e_inexistente(self):
        p = self.pedido(perfil=PERFIL)
        with self.assertRaisesRegex(E.Recusa, "incompleto"): E.enriquecer(p["id"], {"fazer": "x"})
        with self.assertRaisesRegex(E.Recusa, "incompleto"): E.enriquecer(p["id"], "texto")
        with self.assertRaisesRegex(E.Recusa, "Nada a aprofundar"): E.enriquecer("E-9999", LIMPO)

    def test_simular_nao_grava(self):
        p = self.pedido(perfil=PERFIL); antes = json.dumps(E._ler(p["id"]), sort_keys=True)
        self.assertEqual(E.simular(LIMPO), (True, []))
        ok, motivos = E.simular(dict(LIMPO, fazer="Economia de 15% garantida.")); self.assertFalse(ok); self.assertTrue(motivos)
        self.assertEqual(E.simular({"fazer": "x"})[0], False); self.assertEqual(json.dumps(E._ler(p["id"]), sort_keys=True), antes)

    def fila(self):
        import io, contextlib
        buf = io.StringIO(); sys.argv = ["esteira", "fila"]
        with contextlib.redirect_stdout(buf): E.main()
        return buf.getvalue()


class Word(Base):
    def test_word_sob_demanda_so_depois_de_entregue_e_so_uma_vez(self):
        os.environ["CENTRAL_APROVACAO"] = "autonoma"; chamadas = []

        def falso(md, saida, **k): chamadas.append(md); Path(saida).write_bytes(b"PK"); return saida
        E.DS.gerar_docx = falso
        p = self.pedido(perfil=PERFIL)
        a = E.arquivo_do_parceiro(p["id"], "p1"); b = E.arquivo_do_parceiro(p["id"], "p1")
        self.assertEqual((a, len(chamadas)), (b, 1)); self.assertIn("## Seção" if False else "## Resumo e aderência", chamadas[0])
        self.assertIsNone(E.arquivo_do_parceiro(p["id"], "p2"))

    def test_falha_do_gerador_devolve_none(self):
        os.environ["CENTRAL_APROVACAO"] = "autonoma"; p = self.pedido(perfil=PERFIL)
        for erro in (RuntimeError("x"), OSError("y"), __import__("subprocess").TimeoutExpired("node", 1)):
            def falha(*a, **k): raise erro
            E.DS.gerar_docx = falha; self.assertIsNone(E.arquivo_do_parceiro(p["id"], "p1"))

    def test_nao_entregue_nao_gera(self):
        p = self.pedido(perfil=PERFIL)  # modo obrigatório: aguarda aprovação
        E.DS.gerar_docx = lambda *a, **k: self.fail("não deveria gerar")
        self.assertIsNone(E.arquivo_do_parceiro(p["id"], "p1"))

    def test_word_real_e_valido(self):
        os.environ["CENTRAL_APROVACAO"] = "autonoma"; p = self.pedido(perfil=PERFIL)
        E.DS.gerar_docx = DS.gerar_docx
        arq = E.arquivo_do_parceiro(p["id"], "p1")
        if arq is None: self.skipTest("Node/docx indisponível")
        self.assertEqual(Path(arq).read_bytes()[:2], b"PK"); self.assertEqual([n for n in os.listdir(os.path.dirname(arq)) if n.endswith(".part")], [])


class Trava(Base):
    CASOS = {"percentual": ["20% de êxito", "Economia de 15%", "taxa de 7,5 %"], "valor_em_reais_perto_de_ganho": ["recuperação estimada de R$ 500 mil", "ganho de R$ 1.200.000", "R$ 2 milhões de economia", "crédito de R$ 80 mil"],
             "fee": ["fee de entrada", "o Fee fixo"], "comissao": ["comissão do parceiro", "comissões"], "honorario": ["honorário de êxito", "Honorários"], "taxa_de": ["taxa de sucesso", "Taxa de 3"],
             "codigo_de_decisao": ["conforme D59", "(D120)"], "master": ["o Master indicou", "Masters"], "jgm": ["parceiro JGM"], "d_e_s": ["a D&S"],
             "clientes_da_base": ["clientes da base", "na base de clientes"], "escrow": ["conta escrow"], "venda_gerencial": ["venda gerencial"], "blindagem": ["blindagem patrimonial"],
             "vai_recuperar": ["a Save vai recuperar"], "garantia": ["valor garantido", "garantida a entrega", "a Save garante", "garantia de êxito", "Garantia de R$ 1 milhão", "garantimos"], "certeza": ["com certeza"]}
    PASSA = ["Capital social: R$ 4,8 mi.", "Receita acima de R$ 78 milhões obriga ao Lucro Real.", "Resultados passados não garantem resultado futuro.", "Capital social: R$ 5 milhões.",
             "Depende de parecer e documentos.", "Regime Lucro Real em 2023 e 2024.", "CNAE 1051-1/00, base Save Company.", "Crédito caro e curto. Banco exige garantia."]

    def test_cada_regra_da_lista_barra(self):
        self.assertEqual(set(self.CASOS), {n for n, _ in E.TRAVA_REGEX})
        for nome, frases in self.CASOS.items():
            for f in frases: self.assertIn(nome, E.trava_regex(f), f)

    def test_frases_legitimas_passam(self):
        for f in self.PASSA: self.assertEqual(E.trava_regex(f), [], f)

    def test_titulo_e_status_da_esteira_entram_no_texto_auditado(self):
        t = E._texto(dict(LIMPO, dossie=SECAO[:5] + [{"titulo": "Garantia de R$ 1 milhão", "paragrafos": ["ok"]}],
                          esteira=[{"onda": 1, "produto": "p", "status": "garantido em 30 dias", "nota": "n"}]))
        self.assertIn("Garantia de R$ 1 milhão", t); self.assertIn("garantido em 30 dias", t)

    def test_publicar_barra_titulo_status_e_regex_mesmo_no_modo_autonomo(self):
        os.environ["CENTRAL_APROVACAO"] = "autonoma"
        for res in (dict(LIMPO, dossie=SECAO[:5] + [{"titulo": "Garantia de R$ 1 milhão", "paragrafos": ["texto neutro"]}]),
                    dict(LIMPO, esteira=[{"onda": 1, "produto": "p", "status": "garantido em 30 dias", "nota": "n"}]),
                    dict(LIMPO, falta="Cobramos fee de 20% de êxito."), dict(LIMPO, precisa="Indicado pelo Master da região.")):
            p = E.solicitar(cnpj("%08d" % (60000000 + len(json.dumps(res)))), "p1", consulta(NOVO))
            r = E.publicar(p["id"], res); self.assertEqual(r["status"], "revisao_humana"); self.assertFalse(r["auditoria"]["ok"])

    def test_enriquecer_barra_pela_regex(self):
        os.environ["CENTRAL_APROVACAO"] = "autonoma"; p = self.pedido(perfil=PERFIL)
        self.assertEqual(E.enriquecer(p["id"], dict(LIMPO, falta="Honorário de êxito combinado."))["enriquecer"], "alerta")

    def test_falha_do_auditor_barra(self):
        antes = E.RAIZ_REPO, E.subprocess.run
        try:
            def estoura(*a, **k): raise E.subprocess.TimeoutExpired("x", 1)
            E.subprocess.run = estoura
            self.assertFalse(E.auditar("texto neutro")[0])
        finally:
            E.RAIZ_REPO, E.subprocess.run = antes


class Retencao(Base):
    def test_expurgar_apaga_o_velho_e_guarda_o_novo(self):
        os.environ["CENTRAL_APROVACAO"] = "autonoma"
        velho, novo = self.pedido(NOVO), self.pedido(OUTRO)
        E.DS.gerar_docx = lambda md, saida, **k: Path(saida).write_bytes(b"PK") or saida
        for p in (velho, novo): E.publicar(p["id"], LIMPO); E.arquivo_do_parceiro(p["id"], "p1")
        p = E._ler(velho["id"]); p["criado"] = "2020-01-01T00:00:00"; E._gravar(p)
        Path(E._docx("E-0555")).write_bytes(b"PK")  # Word órfão
        os.utime(E._docx("E-0555"), (1, 1))
        E.registrar_consulta("p1", consulta(NOVO)); E.registrar_consulta("p2", consulta(OUTRO))
        h = E._hist_ler("p2"); h[0]["quando"] = "2020-01-01T00:00:00"; E._gravar_json(E._arq_hist("p2"), h)
        n = E.expurgar(365)
        self.assertEqual(n, {"pedidos": 1, "words": 2, "historico": 1})
        self.assertIsNone(E._ler(velho["id"])); self.assertIsNotNone(E._ler(novo["id"])); self.assertTrue(os.path.exists(E._docx(novo["id"])))
        self.assertEqual(len(E._hist_ler("p1")), 1); self.assertFalse(os.path.exists(E._arq_hist("p2")))
        self.assertEqual(E.expurgar(365), {"pedidos": 0, "words": 0, "historico": 0})

    def test_prazo_invalido_e_pasta_inexistente(self):
        for ruim in (0, -5, None, "365"):
            with self.assertRaises(E.Recusa): E.expurgar(ruim)
        self.assertEqual(E.expurgar(30), {"pedidos": 0, "words": 0, "historico": 0})

    def test_linha_de_comando(self):
        import io, contextlib
        buf = io.StringIO(); sys.argv = ["esteira", "expurgar", "--dias", "365"]
        with contextlib.redirect_stdout(buf): E.main()
        self.assertEqual(json.loads(buf.getvalue()), {"pedidos": 0, "words": 0, "historico": 0})


JSON_API = {"razao_social": "EMPRESA", "porte": "DEMAIS", "uf": "MG", "descricao_situacao_cadastral": "ATIVA", "identificador_matriz_filial": 1,
            "opcao_pelo_simples": False, "opcao_pelo_mei": False, "regime_tributario": [{"ano": 2024, "forma_de_tributacao": "LUCRO REAL"}]}


class Regime(Base):
    def test_resposta_com_tipos_estranhos_nao_levanta_excecao(self):
        estranhas = [dict(JSON_API, regime_tributario=[{"ano": "2024", "forma_de_tributacao": "LUCRO REAL"}, {"ano": None, "forma_de_tributacao": 5}, "x", None]),
                     dict(JSON_API, regime_tributario="LUCRO REAL"), dict(JSON_API, razao_social=None, porte=7, uf=[], capital_social="abc"),
                     dict(JSON_API, cnaes_secundarios=[None, "x", {"codigo": 1}], cnae_fiscal=1051100, capital_social=float("inf")),
                     dict(JSON_API, opcao_pelo_simples="false", opcao_pelo_mei=None), dict(JSON_API, regime_tributario=[{"ano": 1e99, "forma_de_tributacao": "LUCRO REAL"}])]
        for d in estranhas:
            R._http = lambda url, d=d: (200, d); R._memoria.clear()
            r = R.consultar(NOVO); self.assertIn(r["faixa"], ("confirmado_real", "sem_dado", "nao_real", "provavel_real")); self.assertTrue(DS.valido(DB.montar(r["perfil"], r["faixa"])["dossie"]))

    def test_ano_como_texto_vale(self):
        R._http = lambda url: (200, dict(JSON_API, regime_tributario=[{"ano": "2024", "forma_de_tributacao": "LUCRO REAL"}]))
        self.assertEqual(R.consultar(NOVO)["faixa"], "confirmado_real")

    def test_json_nao_objeto_429_e_5xx_viram_indisponivel(self):
        for resp in ((200, [1, 2]), (200, None), (429, None), (503, None), (0, None)):
            R._http = lambda url, resp=resp: resp; R._memoria.clear()
            self.assertEqual(R.consultar(NOVO)["faixa"], "indisponivel", resp)
        R._http = lambda url: (404, None); self.assertEqual(R.consultar(NOVO)["faixa"], "sem_dado")

    def test_http_descarta_resposta_gigante_e_trata_erro_do_curl(self):
        class Fake:
            def __init__(self, out): self.stdout = out
        antes = R.subprocess.run
        try:
            R.subprocess.run = lambda *a, **k: Fake("x" * (R.MAX_BYTES + 100) + "\n200"); self.assertEqual(R._http("https://x"), (0, None))
            R.subprocess.run = lambda *a, **k: Fake('{"a": 1}\n200'); self.assertEqual(R._http("https://x"), (200, {"a": 1}))
            R.subprocess.run = lambda *a, **k: Fake("<html>\n200"); self.assertEqual(R._http("https://x"), (0, None))
            for erro in (FileNotFoundError("curl"), R.subprocess.TimeoutExpired("curl", 1)):
                def levanta(*a, **k): raise erro
                R.subprocess.run = levanta; self.assertEqual(R._http("https://x"), (0, None))
            visto = []
            R.subprocess.run = lambda cmd, **k: visto.append(cmd) or Fake("{}\n200"); R._http("https://x")
            self.assertIn("--max-filesize", visto[0]); self.assertIn("=https", visto[0])
        finally:
            R.subprocess.run = antes

    def test_cache_em_memoria_tem_teto_e_aguenta_threads(self):
        R._http = lambda url: (200, JSON_API); antes = R.MEMORIA_MAX; R.MEMORIA_MAX = 5
        try:
            ts = [threading.Thread(target=R.consultar, args=(cnpj("%08d" % (70000000 + i)),)) for i in range(20)]
            [t.start() for t in ts]; [t.join(20) for t in ts]
            self.assertLessEqual(len(R._memoria), 5)
        finally:
            R.MEMORIA_MAX = antes

    def test_teto_diario_nao_estoura_com_threads(self):
        antes = R.LIMITE_DIA; R.LIMITE_DIA = 10; ok = []
        try:
            ts = [threading.Thread(target=lambda: ok.append(R.registrar_uso("u", 1)[0])) for _ in range(40)]
            [t.start() for t in ts]; [t.join(20) for t in ts]
            self.assertEqual(sum(ok), 10)
        finally:
            R.LIMITE_DIA = antes

    def test_acertos_acima_do_teto_alertam_no_log_sem_mudar_a_resposta(self):
        antes = R.LIMITE_ATIVO; R.LIMITE_ATIVO = 2
        try:
            r = [R.consultar(CLIENTE) for _ in range(4)]
            with self.assertLogs("central_api.regime", "WARNING"):
                out = R.limitar_ativos("u", r)
            self.assertEqual([x["_motivo"] for x in out], ["negocio_ativo", "negocio_ativo", "negocio_ativo_acima_do_teto", "negocio_ativo_acima_do_teto"])
            self.assertEqual({x["titulo"] for x in out}, {R.MSG_NEUTRA})  # a mensagem é a mesma do primeiro ao último acerto
            self.assertEqual(R.limitar_ativos("outro", [R.consultar(CLIENTE)])[0]["_motivo"], "negocio_ativo")  # por usuário
            self.assertNotIn("_motivo", R.limitar_ativos("u", [R.publico(dict(r[0], faixa="confirmado_real"))])[0])  # só conta o acerto de cliente
        finally:
            R.LIMITE_ATIVO = antes

    def test_auditar_cria_a_pasta_e_registra_negocio_ativo(self):
        R.auditar("u", [R.consultar(CLIENTE), {"cnpj": NOVO, "faixa": "confirmado_real"}])
        arq = os.path.join(R.BASE, "consultas-regime.jsonl")
        linhas = [json.loads(l) for l in Path(arq).read_text().splitlines()]
        self.assertEqual([(x["faixa"], x.get("motivo")) for x in linhas], [("indisponivel", "negocio_ativo"), ("confirmado_real", None)])  # o motivo real fica na trilha
        self.assertEqual(os.stat(arq).st_mode & 0o777, 0o600)


class Demo(Base):
    def setUp(self):
        super().setUp(); R._http = lambda url: (200, JSON_API)
        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), D.H); self.porta = self.srv.server_address[1]
        self.t = threading.Thread(target=self.srv.serve_forever, daemon=True); self.t.start()

    def tearDown(self):
        self.srv.shutdown(); self.srv.server_close(); self.t.join(5); super().tearDown()

    def req(self, metodo, caminho, corpo=None, host="localhost:%d" % D.PORTA, **cab):
        c = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=20)
        try:
            c.putrequest(metodo, caminho, skip_host=True); c.putheader("Host", host)
            for k, v in cab.items(): c.putheader(k.replace("_", "-"), v)
            if corpo is not None:
                b = corpo if isinstance(corpo, bytes) else json.dumps(corpo).encode()
                c.putheader("Content-Length", str(len(b))); c.endheaders(b)
            else:
                c.endheaders()
            r = c.getresponse(); dados = r.read()
            return r.status, (json.loads(dados) if r.getheader("Content-Type", "").startswith("application/json") else dados)
        finally:
            c.close()

    def post(self, caminho, corpo, **kw): return self.req("POST", caminho, corpo, Content_Type="application/json", **kw)

    def test_travessia_pelo_parametro_id(self):
        Path(self.tmp.name, "segredo.json").write_text("{}")
        for ruim in ("../segredo", "..%2fsegredo", "E-0001%00", "%2e%2e/%2e%2e/etc/passwd", ""):
            self.assertEqual(self.req("GET", "/api/esteira?id=" + ruim)[0], 404, ruim); self.assertEqual(self.req("GET", "/api/esteira/arquivo?id=" + ruim)[0], 404, ruim)
        self.assertEqual(self.req("GET", "/api/esteira")[0], 404)

    def test_host_de_outro_nome_e_recusado(self):
        self.assertEqual(self.req("GET", "/api/esteira/historico", host="evil.example:4281")[0], 421)
        self.assertEqual(self.post("/api/regime", {"cnpjs": [NOVO]}, host="evil.example")[0], 421)
        self.assertEqual(self.req("GET", "/api/esteira/historico")[0], 200)

    def test_corpo_invalido(self):
        self.assertEqual(self.req("POST", "/api/regime", {"cnpjs": [NOVO]}, Content_Type="text/plain")[0], 415)
        for corpo in (b"[1]", b'"x"', b"{quebrado", b"null"): self.assertEqual(self.post("/api/regime", corpo)[0], 400, corpo)
        self.assertEqual(self.post("/api/regime", b"x" * 20001)[0], 413)
        c = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=5); c.putrequest("POST", "/api/regime", skip_host=True); c.putheader("Host", "localhost:%d" % D.PORTA)
        c.putheader("Content-Type", "application/json"); c.putheader("Content-Length", "-1"); c.endheaders()
        self.assertEqual(c.getresponse().status, 400); c.close()
        for corpo in ({"cnpjs": "11111111000100"}, {"cnpjs": [1, None, {"a": 1}, []]}, {"cnpjs": []}, {}): self.assertEqual(self.post("/api/regime", corpo)[0], 400, corpo)
        self.assertEqual(self.post("/api/esteira", {"cnpj": 5})[0], 400); self.assertEqual(self.post("/api/esteira", {"cnpj": ["x"]})[0], 400)

    def test_repetidos_contam_uma_vez_e_consulta_guardada_nao_renova_o_prazo(self):
        st, r = self.post("/api/regime", {"cnpjs": [NOVO, NOVO.lower(), "%s.%s.%s/%s-%s" % (NOVO[:2], NOVO[2:5], NOVO[5:8], NOVO[8:12], NOVO[12:])]})
        self.assertEqual((st, len(r["resultados"]), r["usadas"]), (200, 1, 1))
        h = E._hist_ler(D.USUARIO); h[0]["quando"] = "2000-01-01T00:00:00"; E._gravar_json(E._arq_hist(D.USUARIO), h)
        self.assertEqual(self.post("/api/regime", {"cnpjs": [NOVO]})[1]["usadas"], 2)  # venceu: consulta nova
        antes = E._hist_ler(D.USUARIO)[0]["quando"]; time.sleep(1.1)
        st, r = self.post("/api/regime", {"cnpjs": [NOVO]}); self.assertEqual(r["usadas"], 2)  # guardada: não gasta teto
        self.assertEqual(E._hist_ler(D.USUARIO)[0]["quando"], antes)

    def test_lote_acima_do_limite_e_teto_diario(self):
        mais = [cnpj("%08d" % (80000000 + i)) for i in range(R.LIMITE_LOTE + 1)]
        self.assertEqual(self.post("/api/regime", {"cnpjs": mais})[0], 400)
        antes = R.LIMITE_DIA; R.LIMITE_DIA = 2
        try:
            self.assertEqual(self.post("/api/regime", {"cnpjs": mais[:2]})[0], 200); self.assertEqual(self.post("/api/regime", {"cnpjs": mais[2:3]})[0], 429)
        finally:
            R.LIMITE_DIA = antes

    def test_pedir_esteira_conta_no_teto_e_na_trilha(self):
        antes = R.LIMITE_DIA; R.LIMITE_DIA = 2
        try:
            c1, c2, c3 = (cnpj("%08d" % (81000000 + i)) for i in range(3))
            self.assertEqual(self.post("/api/esteira", {"cnpj": c1})[0], 200); self.assertEqual(self.post("/api/esteira", {"cnpj": c2})[0], 200)
            self.assertEqual(self.post("/api/esteira", {"cnpj": c3})[0], 429)
            self.assertEqual(self.post("/api/esteira", {"cnpj": c1})[0], 200)  # guardada: não gasta teto
            trilha = [json.loads(l) for l in Path(R.BASE, "consultas-regime.jsonl").read_text().splitlines()]
            self.assertEqual(len(trilha), 3); self.assertEqual(trilha[-1].get("motivo"), "teto_diario")  # 2 consultas novas e o registro do teto
        finally:
            R.LIMITE_DIA = antes

    def test_pedir_esteira_recusa_cnpj_nao_localizado_e_cliente(self):
        R._http = lambda url: (404, None); self.assertEqual(self.post("/api/esteira", {"cnpj": NOVO})[0], 400)
        self.assertEqual(self.post("/api/esteira", {"cnpj": CLIENTE})[0], 400)

    def test_cliente_recebe_sempre_a_mensagem_neutra_e_a_trilha_guarda_o_motivo(self):
        a = self.post("/api/regime", {"cnpjs": [CLIENTE]})[1]["resultados"][0]; b = self.post("/api/regime", {"cnpjs": [CLIENTE]})[1]["resultados"][0]
        self.assertEqual((a["faixa"], a["titulo"], b["titulo"]), ("indisponivel", R.MSG_NEUTRA, R.MSG_NEUTRA))
        self.assertFalse([k for k in a if k.startswith("_")]); self.assertNotIn("motivo", a)  # nada interno na resposta
        st, r = self.post("/api/esteira", {"cnpj": CLIENTE}); self.assertEqual((st, r["erro"]), (400, R.MSG_NEUTRA))
        trilha = [json.loads(l) for l in Path(R.BASE, "consultas-regime.jsonl").read_text().splitlines()]
        self.assertEqual([x.get("motivo") for x in trilha if x["faixa"] == "indisponivel"], ["negocio_ativo"] * 3)  # a trilha guarda o motivo real

    def test_teto_diario_responde_a_mensagem_neutra_e_registra_o_motivo(self):
        antes = R.LIMITE_DIA; R.LIMITE_DIA = 1
        try:
            mais = [cnpj("%08d" % (82000000 + i)) for i in range(2)]
            self.assertEqual(self.post("/api/regime", {"cnpjs": mais[:1]})[0], 200)
            st, r = self.post("/api/regime", {"cnpjs": mais[1:]}); self.assertEqual((st, r["erro"]), (429, R.MSG_NEUTRA))
            st, r = self.post("/api/esteira", {"cnpj": mais[1]}); self.assertEqual((st, r["erro"]), (429, R.MSG_NEUTRA))
            trilha = [json.loads(l) for l in Path(R.BASE, "consultas-regime.jsonl").read_text().splitlines()]
            self.assertEqual([x.get("motivo") for x in trilha if x["faixa"] == "indisponivel"], ["teto_diario", "teto_diario"])
        finally:
            R.LIMITE_DIA = antes

    def test_faturamento_como_numero_e_texto(self):
        self.assertEqual(D.numero("90.000.000,50"), 90000000.5); self.assertEqual(D.numero(90000000.5), 90000000.5); self.assertEqual(D.numero(78000000), 78000000)
        for ruim in (None, "", "abc", "-5", -5, float("nan"), float("inf"), "inf", True, "nan"): self.assertIsNone(D.numero(ruim), ruim)

    def test_erro_interno_vira_500_neutro(self):
        antes = E.historico
        try:
            E.historico = lambda p: 1 / 0
            st, r = self.req("GET", "/api/esteira/historico"); self.assertEqual((st, r), (500, {"erro": "erro interno"}))
        finally:
            E.historico = antes

    def test_download_do_word(self):
        os.environ["CENTRAL_APROVACAO"] = "autonoma"
        E.DS.gerar_docx = lambda md, saida, **k: Path(saida).write_bytes(b"PK-teste") or saida
        pid = self.post("/api/esteira", {"cnpj": NOVO})[1]["id"]
        st, corpo = self.req("GET", "/api/esteira/arquivo?id=" + pid); self.assertEqual((st, corpo), (200, b"PK-teste"))


def _estado():
    """lib/estado.py DESTE checkout (a esteira põe ~/agentes-partners/lib na frente do sys.path)."""
    import importlib.util
    arq = Path(__file__).resolve().parents[3] / "lib" / "estado.py"
    spec = importlib.util.spec_from_file_location("estado_deste_checkout", arq); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


class Estado(unittest.TestCase):
    def test_globs_todos_sobe_pedidos_json_docx_e_historico_sem_temporarios(self):
        estado = _estado()
        with tempfile.TemporaryDirectory() as d:
            for rel in ("pedidos/E-0001.json", "pedidos/E-0001.docx", "pedidos/E-0002.json", "pedidos/E-0002.json.tmp", "pedidos/E-0003.docx.123.part",
                        "pedidos/rascunho.json", "historico/abc123.json", "historico/x.tmp"):
                f = Path(d, "central-esteira", rel); f.parent.mkdir(parents=True, exist_ok=True); f.write_bytes(b"x")
            Path(d, "logs").mkdir()
            sobe = []; antes = (estado.AP, estado.graph.subir)
            try:
                estado.AP = d; estado.graph.subir = lambda local, remoto: sobe.append(remoto) or True
                estado.subir()
            finally:
                estado.AP, estado.graph.subir = antes
            enviados = {r.split("/", 1)[1] for r in sobe}
            self.assertEqual({r for r in enviados if r.startswith("central-esteira/")},
                             {"central-esteira/pedidos/E-0001.json", "central-esteira/pedidos/E-0001.docx", "central-esteira/pedidos/E-0002.json", "central-esteira/historico/abc123.json"})
            self.assertEqual(json.loads(Path(d, "logs", "estado-indice.json").read_text()), [r for r in json.loads(Path(d, "logs", "estado-indice.json").read_text())])

    def test_baixar_ignora_caminho_fora_da_pasta(self):
        estado = _estado()
        with tempfile.TemporaryDirectory() as d:
            Path(d, "logs").mkdir(); baixados = []; antes = (estado.AP, estado.graph.baixar)

            def falso(remoto, local):
                if remoto.endswith("indice.json"): Path(local).write_text(json.dumps(["../fora.txt", "/etc/x", "a/../../y", "central-esteira/pedidos/E-0001.json", 5]))
                else: baixados.append(local)
                return True
            try:
                estado.AP = d; estado.graph.baixar = falso; estado.baixar()
            finally:
                estado.AP, estado.graph.baixar = antes
            self.assertEqual(baixados, [os.path.join(d, "central-esteira/pedidos/E-0001.json")])


if __name__ == "__main__":
    unittest.main()
