#!/usr/bin/env python3
"""Testes do fluxo do portal Central Partners → rotinas (revisão de bugs do depto-ti, 23/10/2026).

Rodam em pasta temporária, com registro em memória: não tocam no registro real, no db do Artifact, no GLPI nem no e-mail.
  python3 -m unittest -v lib/test_portal_fluxo.py
Cobrem: autor dos registros do painel (A3), pedido direto à área com `codigo` vazio, aprovação só por quem pediu
(painel e e-mail), chamado só aprovado pela dona, versão "time" dos dados do portal (A2).
"""
import contextlib, importlib.util, io, json, os, shutil, sys, tempfile, types, unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "lib"))
LUIS, DANI, GEO = "u_luis_teste", "u_dani_teste", "u_geo_teste"


def carregar(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="portal-teste-")
        os.environ["PARTNERS_AP"] = self.tmp
        os.makedirs(os.path.join(self.tmp, "registro"))
        import portal_contas as PC
        self.PC = PC
        self._pc = (PC.CONTAS, PC.ALERTAS)
        PC.CONTAS = os.path.join(self.tmp, "contas.json"); PC.ALERTAS = os.path.join(self.tmp, "registro", "portal-alertas.json")
        json.dump({"contas": {LUIS: "luis", DANI: "daniela", GEO: "geovana"}}, open(PC.CONTAS, "w"))

    def tearDown(self):
        self.PC.CONTAS, self.PC.ALERTAS = self._pc
        os.environ.pop("PARTNERS_AP", None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def alertas(self):
        return json.load(open(self.PC.ALERTAS)) if os.path.exists(self.PC.ALERTAS) else []

    def doc(self, pasta, colecao, i, d):
        os.makedirs(os.path.join(pasta, colecao), exist_ok=True); json.dump(d, open(os.path.join(pasta, colecao, i + ".json"), "w"))


class PortalContas(Base):
    def test_conferir(self):
        self.assertTrue(self.PC.conferir("daniela", DANI)[0])
        self.assertFalse(self.PC.conferir("luis", DANI)[0])              # id da Daniela dizendo ser o Luis
        self.assertFalse(self.PC.conferir("luis", "u_estranho")[0])      # conta fora da lista
        self.assertFalse(self.PC.conferir("luis", None)[0])              # registro sem id
        self.assertFalse(self.PC.conferir("daniela", DANI, "geovana")[0])  # não é a dona da ação
        self.assertFalse(self.PC.conferir("Daniela", DANI)[0])           # pessoa fora das quatro


class Central(Base):
    def setUp(self):
        super().setUp()
        self.C = carregar("central_teste", os.path.join(REPO, "skills/central-agentes/scripts/central.py"))
        self.C.BASE = os.path.join(self.tmp, "central"); self.C.REG = os.path.join(self.C.BASE, "registro.json"); self.C.FILA = os.path.join(self.C.BASE, "fila.json")
        self.C.subprocess = types.SimpleNamespace(run=lambda *a, **k: None)  # sem registro_demandas real
        self.C.PC = self.PC

    def importar(self, d, pid="doc1"):
        f = os.path.join(self.tmp, pid + ".json"); json.dump(d, open(f, "w"))
        out = io.StringIO()
        with contextlib.redirect_stdout(out): self.C.cmd_importar_portal(types.SimpleNamespace(arquivo=f, portal_id=pid))
        return out.getvalue().strip()

    def pedido(self, **x):
        return {"criado_em": "2026-10-23T14:05:00.000Z", "solicitante": "daniela", "solicitante_id": DANI, "codigo": "", "status": "novo",
                "area": "depto-tributario", "area_nome": "Tributário & Contábil", "direto": True, "entrega": "", "campos": {"precisa": "Pré-análise de insumos"}, **x}

    def test_direto_chega_na_area_com_codigo_vazio(self):
        pid = self.importar(self.pedido())
        P = self.C.reg()["pedidos"][pid]
        self.assertEqual((P["area"], P["direto"], P["pessoa"], P["codigo"]), ("depto-tributario", True, "daniela", ""))
        self.assertIn("direto à área depto-tributario", P["historico"][0]["evento"])
        self.assertEqual(self.importar(self.pedido()), pid)  # idempotente pelo portal_id

    def test_area_desconhecida_vai_a_triagem(self):
        pid = self.importar(self.pedido(area="../../etc", direto=True), "doc2"); P = self.C.reg()["pedidos"][pid]
        self.assertEqual((P["area"], P["direto"]), ("", False))

    def test_autor_desconhecido_nao_vira_pedido(self):
        with self.assertRaises(SystemExit): self.importar(self.pedido(solicitante="luis", solicitante_id="u_estranho"), "doc3")
        with self.assertRaises(SystemExit): self.importar(self.pedido(solicitante="luis", solicitante_id=DANI), "doc4")
        self.assertEqual(self.C.reg()["pedidos"], {})
        self.assertEqual(len(self.alertas()), 2)

    def test_resposta_direta_usa_nome_da_area(self):
        pid = self.importar(self.pedido())
        J = os.path.join(self.tmp, "r.json"); json.dump({"pedido": pid, "resumo": "ok", "secoes": [{"titulo": "O que você pediu", "texto": "- a"}], "area": "depto-tributario"}, open(J, "w"))
        prev = os.path.join(self.tmp, "previa.html")
        with contextlib.redirect_stdout(io.StringIO()):
            self.C.cmd_responder(types.SimpleNamespace(arquivo=J, previa=prev, painel=True, aviso=False, rascunho=False))
        self.assertIn("Tributário &amp; Contábil", open(prev).read())

    def test_aprovacao_so_de_quem_pediu(self):
        pid = self.importar(self.pedido())
        def decisao(por, por_id, tipo="aprovado"):
            f = os.path.join(self.tmp, "dec.json"); json.dump({**self.pedido(), "status": tipo, "decisao": {"tipo": tipo, "por": por, "por_id": por_id}}, open(f, "w")); return f
        a = lambda f, dec="aprovado": types.SimpleNamespace(pedido=pid, decisao=dec, nota=None, rascunho=False, sem_email=True, arquivo=f)
        for f in (decisao("geovana", GEO), decisao("daniela", "u_estranho"), decisao("daniela", GEO)):
            with self.assertRaises(SystemExit): self.C.cmd_confirmar(a(f))
        with self.assertRaises(SystemExit): self.C.cmd_confirmar(a(decisao("daniela", DANI, "nova_analise")))  # tipo diferente do pedido
        self.assertEqual(self.C.reg()["pedidos"][pid]["status"], "em_analise")
        out = io.StringIO()
        with contextlib.redirect_stdout(out): self.C.cmd_conferir_decisao(types.SimpleNamespace(pedido=pid, arquivo=decisao("daniela", DANI, "nova_analise")))
        self.assertEqual(json.loads(out.getvalue())["tipo"], "nova_analise")
        self.C.caminhos = types.SimpleNamespace(pasta=lambda p: os.path.join(self.tmp, "od", p))
        with contextlib.redirect_stdout(io.StringIO()): self.C.cmd_confirmar(a(decisao("daniela", DANI, "nao_aprovado"), "nao_aprovado"))
        self.assertEqual(self.C.reg()["pedidos"][pid]["status"], "nao_aprovado")

    def test_email_de_outra_pessoa_nao_decide(self):
        R = {"seq": 1, "processados": [], "pedidos": {"P-0001": {"id": "P-0001", "pessoa": "daniela", "codigo": "", "campos": {}, "assunto": "x", "versao": 1, "historico": []}}}
        os.makedirs(self.C.BASE); json.dump(R, open(self.C.REG, "w"))
        self.C.listar = lambda dias: [{"id": "m1", "assunto": "RE: [AGENTES] #P-0001 · x · resposta v1", "de": "jenifer.carvalho@savecompany.com.br", "quando": "2026-10-23"}]
        self.C.baixar = lambda mid, pasta: ("Aprovado\nok", [])
        out = io.StringIO()
        with contextlib.redirect_stdout(out): self.C.cmd_ler(types.SimpleNamespace(dias=3, enfileirar=False))
        n = json.loads(out.getvalue())[0]
        self.assertIsNone(n["decisao"]); self.assertIn("ignorado", n["informacoes"])


class PainelSync(Base):
    def setUp(self):
        super().setUp()
        self.reg = {"demandas": {"D-1": {"id": "D-1", "pessoa": "daniela", "status": "responder", "eventos": []}}}
        reg = self.reg
        class Registro:
            def __enter__(s): return reg
            def __exit__(s, *x): pass
        sys.modules["registro_demandas"] = types.SimpleNamespace(Registro=Registro, ABERTOS=("responder", "acompanhar", "em_analise", "aguardando_aprovacao"))
        os.makedirs(os.path.join(self.tmp, "conselho")); os.makedirs(os.path.join(self.tmp, "celulas/geovana/recuperador"))
        open(os.path.join(self.tmp, "conselho/decisoes.md"), "w").write("| ID | Data | Ata | Texto | Status | Obs | Quando |\n| D9 | 01/10 | A1 | Texto | pendente | — | — |\n")
        self.S = carregar("painel_sync_teste", os.path.join(REPO, "lib/painel_sync.py")); self.S.PC = self.PC

    def tearDown(self):
        sys.modules.pop("registro_demandas", None); super().tearDown()

    def rodar(self, pasta):
        sys.argv = ["painel_sync.py", pasta]; out = io.StringIO()
        with contextlib.redirect_stdout(out): self.S.main()
        return json.loads(out.getvalue())

    def test_so_a_dona_e_contas_conhecidas(self):
        p = os.path.join(self.tmp, "painel")
        self.doc(p, "acoes_demandas", "D-1", {"status": "respondido", "por": "jenifer", "por_id": "u_jeni", "quando": "q1"})
        self.doc(p, "conselho", "D9", {"decisao": "aprovada", "por": "luis", "quando": "q2"})                 # sem id (versão antiga da página)
        self.doc(p, "recuperador", "123", {"decisao": "Vetar", "por": "geovana", "por_id": DANI, "quando": "q3"})  # id de outra pessoa
        self.doc(p, "apontamentos", "a1", {"pessoa": "daniela", "por_id": DANI, "data": "q4", "minutos": 5})
        r = self.rodar(p)
        self.assertEqual(r, {"demandas": 0, "recuperador": 0, "conselho": 0, "apontamentos": 1, "descartados": 3})
        self.assertEqual(self.reg["demandas"]["D-1"]["status"], "responder")
        self.assertIn("| pendente |", open(os.path.join(self.tmp, "conselho/decisoes.md")).read())
        self.assertEqual(len(self.alertas()), 3)
        # registros válidos depois (a conta da Daniela e o Luis com id): aplicados; os descartados não foram marcados como feitos
        self.doc(p, "acoes_demandas", "D-1", {"status": "respondido", "por": "daniela", "por_id": DANI, "quando": "q5"})
        self.doc(p, "conselho", "D9", {"decisao": "aprovada", "por": "luis", "por_id": LUIS, "quando": "q2"})
        r = self.rodar(p)
        self.assertEqual((r["demandas"], r["conselho"], r["apontamentos"]), (1, 1, 0))
        self.assertEqual(self.reg["demandas"]["D-1"]["status"], "resolvida")
        self.assertIn("| aprovada |", open(os.path.join(self.tmp, "conselho/decisoes.md")).read())

    def test_registro_quebrado_nao_derruba(self):
        p = os.path.join(self.tmp, "painel"); os.makedirs(os.path.join(p, "conselho"))
        open(os.path.join(p, "conselho", "x.json"), "w").write("{quebrado")
        self.doc(p, "conselho", "D9", {"por": "luis", "por_id": LUIS, "quando": "q"})  # sem "decisao"
        self.assertEqual(self.rodar(p)["conselho"], 0)


class ChamadosPainel(Base):
    def setUp(self):
        super().setUp()
        self.abertos = []
        self.dem = {"demandas": {"D-7": {"id": "D-7", "pessoa": "daniela", "status": "responder"}}}
        dem = self.dem
        class Registro:
            def __enter__(s): return dem
            def __exit__(s, *x): pass
        sys.modules["registro_demandas"] = types.SimpleNamespace(Registro=Registro)
        sys.modules["glpi"] = types.SimpleNamespace(abrir=lambda area, titulo, corpo, urg, pessoa=None: self.abertos.append((area, titulo, pessoa)) or {"rascunho": True})
        sys.modules["chamado_modelo"] = types.SimpleNamespace(AGENTE=lambda a: "Gerente", formulario=lambda *a: "corpo")
        self.M = carregar("chamados_teste", os.path.join(REPO, "lib/chamados_painel.py"))
        json.dump({"D-1": {"id": "D-1", "pessoa": "daniela", "area": "jur_demandas", "titulo": "T", "status": "proposto"}}, open(self.M.PROP, "w"))

    def tearDown(self):
        for m in ("registro_demandas", "glpi", "chamado_modelo"): sys.modules.pop(m, None)
        super().tearDown()

    def aplicar(self, pasta):
        out = io.StringIO()
        with contextlib.redirect_stdout(out): self.M.aplicar(pasta)
        return json.loads(out.getvalue())

    def test_so_a_dona_aprova_e_so_chamado_proposto(self):
        p = os.path.join(self.tmp, "painel")
        self.doc(p, "chamados", "D-1", {"pessoa": "daniela", "area": "jur_demandas", "status": "aprovado", "aprovado_por": "geovana", "aprovado_por_id": GEO})
        self.doc(p, "chamados", "D-9", {"pessoa": "daniela", "area": "jur_demandas", "status": "aprovado", "aprovado_por": "daniela", "aprovado_por_id": DANI})
        up = self.aplicar(p)
        self.assertEqual(self.abertos, [])
        self.assertEqual(sorted(u["doc_id"] for u in up), ["D-1", "D-9"]); self.assertTrue(all("nota_agente" in u["data"] for u in up))
        self.doc(p, "chamados", "D-1", {"pessoa": "geovana", "area": "outros", "status": "aprovado", "aprovado_por": "daniela", "aprovado_por_id": DANI})
        up = self.aplicar(p)
        self.assertEqual(self.abertos, [("jur_demandas", "T", "daniela")])  # área e pessoa da proposta local, não do db
        self.assertEqual([u["data"]["status"] for u in up if u["doc_id"] == "D-1"], ["aprovado_manual"])


    def test_chamado_gerado_no_portal(self):
        p = os.path.join(self.tmp, "painel")
        es = {"agente": "Gerente Jurídico", "pedidos": ["Confirmar a data de ciência"]}
        base = {"pessoa": "daniela", "area": "jur_comunicados", "titulo": "Despacho", "descricao": "**O que pedimos**\n1. x", "origem": "portal", "demanda": "D-7",
                "especialista": es, "proposto_por": "daniela", "proposto_por_id": DANI}
        self.doc(p, "chamados", "D-7", {**base, "status": "aprovado", "aprovado_por": "daniela", "aprovado_por_id": DANI})
        self.doc(p, "chamados", "D-8", {**base, "demanda": "D-8", "status": "aprovado", "aprovado_por": "daniela", "aprovado_por_id": DANI})  # demanda inexistente
        self.doc(p, "chamados", "D-6", {**base, "demanda": "D-7", "especialista": {}, "status": "aprovado", "aprovado_por": "daniela", "aprovado_por_id": DANI})  # sem texto do especialista
        up = {u["doc_id"]: u["data"] for u in self.aplicar(p)}
        self.assertEqual(self.abertos, [("jur_comunicados", "Despacho", "daniela")])
        self.assertEqual(up["D-7"]["status"], "aprovado_manual"); self.assertIn("nota_agente", up["D-8"]); self.assertIn("nota_agente", up["D-6"])
        self.assertEqual(json.load(open(self.M.PROP))["D-7"]["status"], "aprovado_manual")


class PortalDadosTime(unittest.TestCase):
    def test_versao_time(self):
        os.environ["PORTAL_PERFIL"] = "time"
        try: M = carregar("portal_dados_teste", os.path.join(REPO, "infra/portal_dados.py"))
        finally: os.environ.pop("PORTAL_PERFIL", None)
        u = lambda r: "https://x/my?id=" + r
        d = {"conselho": [{"id": "D9"}], "gestao": {"decisoes_pendentes": ["D9"], "alertas": []}, "demandas": {"luis": {}, "daniela": {}},
             "demandas_lista": [{"pessoa": "luis"}, {"pessoa": "daniela"}], "whatsapp_demandas": [{"pessoa": "luis"}, {"pessoa": "geovana"}], "arquivos_dia": {"luis": [1], "jenifer": [2]},
             "pastas_web": {"luis": {"url": u("04")}, "geovana": {"url": u("g")}}, "pastas": {"luis": "04 · Gestão", "daniela": "Área"}}
        lk = lambda c: {"rotulo": c, "url": u(c), "caminho": c}
        D = {"pastas": [{"rotulo": "a", "caminho": "04 · Gestão / Conselho", "uso": "", "url": u("04")}, {"rotulo": "b", "caminho": "Área Partners · Agentes / Central BDR · Jenifer", "uso": "", "url": u("j")}],
             "areas": [{"links": [lk("01 · Comercial / Relatórios"), lk("Área Partners · Agentes / X")], "entregas": [{"links": [lk("04 · Gestão / Resultado")]}]}],
             "rotinas": [{"links": [lk("04 · Gestão / Central")]}],
             "pessoas": [{"chave": "luis", "url": u("04"), "plano_url": u("04"), "pasta": "04 · Gestão / Central"}, {"chave": "daniela", "url": u("d"), "plano_url": u("d"), "pasta": "Área"}]}
        d2, D2 = M.para_time(d, D)
        s = json.dumps([d2, D2], ensure_ascii=False)
        self.assertNotIn("conselho", d2); self.assertNotIn("decisoes_pendentes", s); self.assertNotIn("04", "".join(x["url"] for x in D2["pastas"]))
        self.assertNotIn("my?id=04", s); self.assertNotIn("my?id=01", s)
        self.assertEqual([x["pessoa"] for x in d2["whatsapp_demandas"]], ["geovana"])
        self.assertEqual([x["pessoa"] for x in d2["demandas_lista"]], ["daniela"]); self.assertEqual(list(d2["arquivos_dia"]), ["jenifer"])
        self.assertEqual(D2["pessoas"][0]["url"], ""); self.assertEqual(D2["areas"][0]["links"][0]["rotulo"], "Área Partners · Agentes / X")
        self.assertEqual(d["conselho"], [{"id": "D9"}])  # não altera o original


class ChamadoSugerido(unittest.TestCase):
    def test_chamado_ideal_e_auditor(self):
        M = carregar("portal_dados_teste2", os.path.join(REPO, "infra/portal_dados.py"))
        areas = {"jur_comunicados": {"nome": "Juridico > Comunicados RFB"}, "outros": {"nome": "Partners (triagem)"}}
        es = {"agente": "Gerente Jurídico", "entendemos": "E.", "pedidos": ["Confirmar a ciência", "Calcular o prazo"], "anexos": ["Despacho"], "prazo_motivo": "2026-10-31 · 30 dias"}
        c = M.chamado_sugerido({"area": "jur_comunicados", "titulo": "T", "urgencia": 4, "especialista": es}, areas)
        self.assertTrue(c["pronto"]); self.assertEqual((c["grupo"], c["skill"]), ("Juridico > Comunicados RFB", "depto-juridico"))
        self.assertIn("**O que pedimos**\n1. Confirmar a ciência\n2. Calcular o prazo", c["descricao"]); self.assertIn("- Despacho", c["descricao"])
        self.assertFalse(M.chamado_sugerido({"area": "trib_diagnostico", "especialista": {}}, areas)["pronto"])
        self.assertFalse(M.chamado_sugerido({"area": "x", "especialista": {"pedidos": ["a"], "nao_abrir": "status"}}, areas)["pronto"])
        self.assertIsNone(M.chamado_sugerido(None, areas))
        self.assertTrue(M._auditar("")["ok"])
        r = M._auditar("Garantimos o resultado e o crédito sai em 30 dias.")
        self.assertIs(r["ok"], False); self.assertTrue(r["achados"])  # promessa de êxito e de prazo


if __name__ == "__main__":
    unittest.main()
