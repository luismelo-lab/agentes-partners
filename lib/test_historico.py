"""Testes do lib/historico.py (busca no histórico antes do GLPI).  Rode:  python3 -m unittest lib/test_historico.py

Monta uma base falsa numa pasta temporária (PARTNERS_AP e HISTORICO_REPO): nada real, nenhum dado de cliente.
Empresas fictícias; o CNPJ é gerado na hora e não é válido (o scanner do repositório bloqueia CNPJ válido no código).
"""
import json, os, random, shutil, sys, tempfile, unittest

TMP = tempfile.mkdtemp(prefix="hist-teste-")
os.environ["PARTNERS_AP"] = TMP
os.environ["HISTORICO_REPO"] = TMP
os.environ["HISTORICO_CACHE"] = os.path.join(TMP, "cache")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import historico as H  # noqa: E402

RAIZ = "".join(random.choice("0123456789") for _ in range(8))
CNPJ = RAIZ + "000100"  # 14 dígitos, DV inválido de propósito


def _w(rel, conteudo):
    f = os.path.join(TMP, rel); os.makedirs(os.path.dirname(f), exist_ok=True)
    with open(f, "w") as fh:
        fh.write(conteudo if isinstance(conteudo, str) else json.dumps(conteudo, ensure_ascii=False))


def setUpModule():
    _w("infra/glpi-regras.md", "# Regras do GLPI\n\n## Fora do GLPI\n- **Sistema S (Sesi, Senai, Sesc):** não é compensável. "
       "Responder ao parceiro com a regra; não abrir chamado de compensação.\n")
    for i, tema in enumerate(["onboarding de parceiro e academia de vendas", "relatório semanal de resultados e margem",
                              "campanha de marketing com datas fiscais", "inventário de agentes e rotinas agendadas",
                              "contrato de indicação e representação comercial", "lead scoring e perfil de cliente ideal"]):
        _w(f"skills/area{i}/SKILL.md", f"# Área {i}\n\n## Base\nEsta área cuida de {tema}. Texto de apoio sobre {tema} e processos internos.\n")
    _w("celulas/whatsapp-config.json", {"nomes_time": ["Daniela Maciel"], "telefones_time": []})
    _w("celulas/daniela/whatsapp/caixa-2026-10-20-10h00.json", [{
        "chat": "Atendimento Parceiro Teste", "master": "MASTERX", "negocios": [],
        "conversa": [{"de": "5500000000000", "quando": "20/10 09:00", "texto": "Qual o prazo médio para o ressarcimento do PER de café exportado?"},
                     {"de": "Daniela Maciel", "quando": "20/10 09:30", "texto": "O ressarcimento do PER segue o prazo de 360 dias da Receita; não há data garantida, acompanhamos e avisamos."}]}])
    _w("celulas/whatsapp-triagem-2026-10-21-14h1500.json", {"rodada": "14h", "pessoas": {"daniela": {"itens": [{
        "chat": "Atendimento Parceiro Teste", "master": "MASTERX", "status": "responder",
        "o_que_pede": "Parceiro pergunta o prazo do ressarcimento do PER do café exportado da Zincoteca",
        "rascunho": "O PER de ressarcimento tem o prazo de 360 dias da Receita para análise; acompanhamos e avisamos a cada movimentação.",
        "entrega": "PER transmitido; aguarda análise."}]}}})
    _w("registro/demandas.json", {"seq": {}, "demandas": {}})
    _w("registro/chamados-propostos.json", {"D-2026-9001": {"id": "D-2026-9001", "pessoa": "daniela", "area": "jur_comunicados",
        "titulo": "Comunicados RFB BETA FRIGOTESTE LTDA x intimação despacho decisório", "empresa": "BETA FRIGOTESTE LTDA",
        "descricao": "**Entendemos que:** a BETA FRIGOTESTE recebeu intimação de despacho decisório na caixa postal do e-CAC; prazo de 30 dias.",
        "conversa": "Atendimento Outro", "status": "proposto", "proposto_em": "2026-10-22T10:00"}})
    _w("departamentos/resultados/dados/hubspot-2026-10-26.json", {"baixado_em": "2026-10-26T06:50", "negocios": [
        {"id": "111", "nome": "ACME ZINCOTECA LTDA", "etapa": "Contrato Enviado", "pipeline": "RT", "status": "aberto", "parceiro": "MASTERX",
         "extras": {"cnpj": CNPJ, "entrou_etapa": "2026-10-10T10:00:00Z", "parecer_rt": "x"}},
        {"id": "222", "nome": "BETA FRIGOTESTE LTDA", "etapa": "Execução", "pipeline": "RT", "status": "ganho", "parceiro": "MASTERY",
         "extras": {"cnpj": "", "entrou_etapa": "2026-09-01T10:00:00Z"}}]})
    H.HOJE = H.datetime(2026, 10, 26, 12, 0)


def tearDownModule():
    shutil.rmtree(TMP, ignore_errors=True)


class Texto(unittest.TestCase):
    def test_tokens_e_radical(self):
        self.assertEqual(H.toks("Compensação compensar compensa")[0], H.toks("compensar")[0])
        self.assertNotIn("bom", H.toks("Bom dia, tudo bem?"))

    def test_limpo_mascara_email(self):
        self.assertNotIn("@", H.limpo("o e-mail é fulano.teste@exemplo.com"))


class Indice(unittest.TestCase):
    def test_monta_cache_protegido(self):
        I = H.indice(forcar=True)
        self.assertGreater(len(I["docs"]), 5)
        arq = os.path.join(os.environ["HISTORICO_CACHE"], "indice.pkl")
        self.assertEqual(oct(os.stat(arq).st_mode & 0o777), "0o600")
        self.assertEqual(H.indice()["assinatura"], I["assinatura"])  # segunda chamada lê o cache

    def test_par_whatsapp_pergunta_resposta(self):
        I = H.indice()
        pares = [d for d in I["docs"] if d["fonte"] == "whatsapp"]
        self.assertEqual(len(pares), 1)
        self.assertIn("360 dias", pares[0]["resposta"])
        self.assertIn("prazo médio", pares[0]["pergunta"])


class Busca(unittest.TestCase):
    def test_regra_sistema_s(self):
        r = H.buscar("Sistema S pode compensar?")
        self.assertEqual(r["resultados"][0]["fonte"], "base")
        self.assertIn("não é compensável", r["resultados"][0]["trecho"])
        self.assertIn(r["resultados"][0]["grau"], ("alta", "média"))

    def test_acha_caso_por_nome_e_cnpj(self):
        I = H.indice()
        self.assertEqual(H.achar_caso(I, "como anda a Zincoteca?")[0]["id"], "111")
        self.assertEqual(H.achar_caso(I, "", cnpj=CNPJ)[0]["id"], "111")
        self.assertEqual(H.achar_caso(I, "o parceiro mandou o contrato"), [])

    def test_exclui_a_propria_demanda(self):
        r = H.buscar("prazo do ressarcimento do PER do café exportado da Zincoteca", chat="Atendimento Parceiro Teste", antes="2026-10-21T00:00")
        self.assertFalse([x for x in r["resultados"] if x["fonte"] == "triagem"], "triagem da mesma conversa depois da demanda vazou")


class Avaliacao(unittest.TestCase):
    def test_regra_da_casa(self):
        a = H.avaliar("O Sistema S pode ser compensado com o crédito? qual a regra?")
        self.assertTrue(a["suficiente"]); self.assertEqual(a["criterio"], "regra_da_casa"); self.assertEqual(a["rota"], "responder")

    def test_dado_do_caso(self):
        a = H.avaliar("Em que etapa está a Zincoteca?")
        self.assertEqual(a["criterio"], "dado_do_caso")
        self.assertIn("Contrato Enviado", H.base_resposta(a))

    def test_mesma_pergunta_respondida(self):
        a = H.avaliar("Qual o prazo do ressarcimento do PER do café exportado da Zincoteca?", master="MASTERX", chat="Outro chat")
        self.assertTrue(a["suficiente"])
        self.assertIn(a["criterio"], ("mesma_pergunta_respondida", "dado_do_caso"))

    def test_chamado_existente_nao_abre_outro(self):
        a = H.avaliar("A BETA FRIGOTESTE recebeu intimação de despacho decisório na caixa postal do e-CAC")
        self.assertEqual(a["criterio"], "chamado_existente")

    def test_prazo_novo_sem_historico_vai_ao_glpi(self):
        a = H.avaliar("A ACME ZINCOTECA recebeu intimação de despacho decisório na caixa postal do e-CAC")
        self.assertFalse(a["suficiente"]); self.assertEqual(a["rota"], "glpi")
        self.assertIn("ação nova da área", a["faltou"])
        self.assertTrue(a["buscas"] and a["buscas"][0]["consulta"])

    def test_cumprimento_fica_com_a_dona(self):
        a = H.avaliar("Bom dia, tudo certo por aí? obrigado")
        self.assertFalse(a["suficiente"]); self.assertEqual(a["rota"], "dona")

    def test_resposta_historico_formato(self):
        a = H.avaliar("Em que etapa está a Zincoteca?")
        rh = H.resposta_historico(a, H.base_resposta(a), "Central Masters", "Retorno ao Parceiro")
        self.assertTrue(rh["resposta"]); self.assertEqual(rh["criterio"], "dado_do_caso")
        self.assertTrue(all({"fonte", "data", "trecho"} <= set(f) for f in rh["fontes"]))
        self.assertEqual((rh["area"], rh["especialista"]), ("Central Masters", "Retorno ao Parceiro"))


class Lote(unittest.TestCase):
    def test_lote_recusa_registro(self):
        with self.assertRaises(SystemExit):
            H.lote(os.path.join(TMP, "registro", "teste"))


if __name__ == "__main__":
    unittest.main()
