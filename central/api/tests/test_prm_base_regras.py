"""PRM: calendário (dias e horas úteis), catálogo de textos (auditor de promessas), auditor único (U5) e parâmetros."""
import json, os, re, subprocess, sys, tempfile, unittest
from datetime import date, datetime

from central_api.caminhos import repo
from central_api.prm import auditoria as AU
from central_api.prm import calendario as CAL
from central_api.prm import textos as TX
from central_api.prm.erros import Invalido
from central_api.prm.parametros import Parametros, catalogo
from cnpj import dv_cnpj

P = Parametros()


def cpf(base="987654321", formatado=True):
    """CPF de teste gerado na hora (nenhum número fica escrito no repositório: o checar-dados bloqueia)."""
    d = [int(x) for x in base]
    for n in (9, 10):
        s = sum(v * (n + 1 - i) for i, v in enumerate(d[:n])) % 11
        d.append(0 if s < 2 else 11 - s)
    c = "".join(map(str, d))
    return "%s.%s.%s-%s" % (c[:3], c[3:6], c[6:9], c[9:]) if formatado else c
C = CAL.Calendario(P)


class Calendario(unittest.TestCase):
    def test_feriados_moveis_2026(self):
        fs = CAL.feriados(2026)
        for d in ("2026-02-16", "2026-02-17", "2026-04-03", "2026-06-04", "2026-11-20", "2026-11-02"):
            self.assertIn(date.fromisoformat(d), fs)

    def test_fim_de_semana_nao_e_util(self):
        self.assertFalse(C.util(date(2026, 10, 31)))
        self.assertTrue(C.util(date(2026, 10, 30)))

    def test_somar_du_pula_fim_de_semana_e_feriado(self):
        self.assertEqual(C.somar_du(date(2026, 10, 30), 1), date(2026, 11, 3))  # sexta + 1 d.u. (02/11 é feriado)

    def test_zero_du_em_sabado_vai_para_segunda(self):
        self.assertEqual(C.somar_du(date(2026, 10, 24), 0), date(2026, 10, 26))

    def test_prazo_du_vence_23h59(self):
        p = C.prazo_du(datetime(2026, 10, 26, 9, 0, tzinfo=CAL.FUSO), 1)
        self.assertEqual((p.date(), p.hour, p.minute), (date(2026, 10, 27), 23, 59))

    def test_horas_uteis(self):
        a = datetime(2026, 10, 23, 17, 0, tzinfo=CAL.FUSO)  # sexta 17h
        b = datetime(2026, 10, 26, 11, 0, tzinfo=CAL.FUSO)  # segunda 11h
        self.assertEqual(C.horas_uteis_entre(a, b), 4.0)
        self.assertEqual(C.somar_horas_uteis(a, 4), b)

    def test_janela_de_envio(self):
        sab = datetime(2026, 10, 24, 10, 0, tzinfo=CAL.FUSO)
        self.assertEqual(C.janela_envio(sab), datetime(2026, 10, 26, 7, 0, tzinfo=CAL.FUSO))
        noite = datetime(2026, 10, 27, 21, 0, tzinfo=CAL.FUSO)
        self.assertEqual(C.janela_envio(noite), datetime(2026, 10, 28, 7, 0, tzinfo=CAL.FUSO))

    def test_carimbo_utc_com_milissegundos(self):
        s = CAL.iso(datetime(2026, 10, 26, 14, 0, 0, 123456, tzinfo=CAL.FUSO))
        self.assertEqual(s, "2026-10-26T17:00:00.123Z")
        self.assertEqual(CAL.fmt(s), "26/10/2026 14:00")


class Textos(unittest.TestCase):
    def test_catalogo_passa_no_auditor_de_promessas(self):
        """02 §17: o build falha com qualquer ALTO ou MÉDIO no catálogo M-xx."""
        script = repo() / "skills/depto-qualidade/scripts/auditar_texto.py"
        with tempfile.TemporaryDirectory() as d:
            arq = os.path.join(d, "textos.md")
            with open(arq, "w", encoding="utf-8") as f:
                f.write("\n\n".join(TX.TEXTOS.values()))
            r = subprocess.run([sys.executable, "-I", str(script), arq, "--json"], capture_output=True, text=True)
        achados = [a for x in json.loads(r.stdout).values() for a in x["achados"] if a["severidade"] in ("ALTO", "MEDIO")]
        self.assertEqual(achados, [])
        self.assertEqual(r.returncode, 0)

    def test_catalogo_tem_todos_os_codigos_da_spec(self):
        for c in ("M-00", "M-01", "M-02", "M-03a", "M-03b", "M-04", "M-05", "M-06", "M-07", "M-08", "M-09", "M-10", "M-11", "M-12", "M-13", "M-14", "M-15",
                  "M-16", "M-20", "M-21a", "M-21", "M-22-procedente", "M-22-improcedente", "M-23", "M-24", "M-25", "M-30", "M-31", "M-32", "M-33", "M-34",
                  "M-50", "M-51", "M-90"):
            self.assertIn(c, TX.TEXTOS)

    def test_neutra_igual_a_da_central(self):
        from central_api import negocio_ativo
        self.assertEqual(TX.TEXTOS["M-00"], negocio_ativo.MSG_NEUTRA)

    def test_variavel_faltando_nao_sai(self):
        with self.assertRaises(KeyError):
            TX.texto("M-05")
        self.assertIn("31/12/2026", TX.texto("M-05", valido_ate="31/12/2026"))

    def test_sem_termos_vedados(self):
        """PRM-R04 e R33: sem 'repasse', 'território', 'carteira protegida' nem 'comissão' em texto externo."""
        tudo = " ".join(TX.TEXTOS.values()).lower()
        for t in ("repasse", "território", "carteira protegida", "comissão", "divisão de honorários", "garant"):
            self.assertNotIn(t, tudo)

    def test_pontuacao_da_variavel(self):
        self.assertIn("data? Responda", TX.texto("M-02", pergunta="Qual a data?", data_limite="x"))


class Auditor(unittest.TestCase):
    def test_cpf_formatado(self):
        self.assertEqual(AU.dados_pessoais("o CPF é " + cpf()), ["cpf"])

    def test_onze_digitos_bloqueia(self):
        self.assertIn("cpf", AU.dados_pessoais("contato " + cpf(formatado=False)))

    def test_cnpj_nao_e_cpf(self):
        c = "11222333" + "0001"
        self.assertEqual(AU.dados_pessoais("CNPJ " + c + dv_cnpj(c)), [])

    def test_dado_bancario_e_documento(self):
        self.assertIn("bancario", AU.dados_pessoais("conta: 12345-6"))
        self.assertIn("documento", AU.dados_pessoais("RG 12.345.678-9"))
        self.assertIn("bancario", AU.dados_pessoais("chave pix 9988"))

    def test_bloqueio_devolve_m90(self):
        with self.assertRaises(Invalido) as e:
            AU.exigir_sem_dado_pessoal({"texto": "CPF " + cpf()})
        self.assertEqual(e.exception.codigo, "M-90")
        self.assertEqual(e.exception.mensagem, TX.TEXTOS["M-90"])

    def test_promessa_bloqueia_saida(self):
        ok, motivos = AU.auditar_saida("A Save garante a recuperação do crédito em 30 dias, sem risco.")
        self.assertFalse(ok)
        self.assertTrue(motivos)

    def test_texto_limpo_passa(self):
        ok, motivos = AU.auditar_saida("O diagnóstico está com o time técnico. Avisamos aqui quando houver novidade.")
        self.assertTrue(ok, motivos)

    def test_rigor_de_dossie_usa_lista_de_bloqueio(self):
        ok, motivos = AU.auditar_saida("O honorário desta empresa será conversado depois.", rigor="dossie")
        self.assertFalse(ok)
        self.assertTrue(any("honorario" in m for m in motivos))


class Parametros_(unittest.TestCase):
    def test_padroes_da_spec(self):
        self.assertEqual(P("registro.validade_master_dias"), 120)
        self.assertEqual(P("registro.validade_indicador_dias"), 90)
        self.assertEqual(P("registro.prorrogacao_dias"), 60)
        self.assertEqual(P("demanda.escala_du"), [1, 3, 5])
        self.assertFalse(P("extrato.mostra_valor_previsto"))
        self.assertFalse(P("familia_ci_ativa"))
        self.assertEqual(P("nivel.modo"), "sombra")

    def test_todo_parametro_tem_marca_e_dona(self):
        cat = catalogo()
        self.assertGreaterEqual(len(cat), 62)
        for k, v in cat.items():
            self.assertTrue(v.get("marca") and v.get("quem_muda") and "valor" in v, k)

    def test_sobreposicao_por_arquivo(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"registro.validade_master_dias": 180}, f)
        try:
            os.environ["PRM_PARAMETROS"] = f.name
            self.assertEqual(Parametros()("registro.validade_master_dias"), 180)
        finally:
            os.environ.pop("PRM_PARAMETROS"); os.unlink(f.name)

    def test_parametro_desconhecido(self):
        with self.assertRaises(KeyError):
            P("nao.existe")


if __name__ == "__main__":
    unittest.main()
