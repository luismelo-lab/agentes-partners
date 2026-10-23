"""Regras do dossiê-base (montado por código, lido pelo parceiro e depois pelo cliente final).

    cd central/api && PYTHONPATH=../../lib python3 -m unittest -v tests.test_dossie_base
"""
import re, subprocess, sys, tempfile, unittest
from pathlib import Path

from central_api import dossie_base as B

CNAES = {1: "1011101", 2: "4621100", 3: "4711302", 4: "4731800", 5: "1412601", 6: "4930202", 7: "1091101", 0: "6201501"}
REAL = [{"ano": a, "forma": "LUCRO REAL"} for a in range(2020, 2025)]
MUDOU = [{"ano": a, "forma": "LUCRO PRESUMIDO"} for a in (2020, 2021, 2022)] + [{"ano": a, "forma": "LUCRO REAL"} for a in (2023, 2024)]
PRES = [{"ano": a, "forma": "LUCRO PRESUMIDO"} for a in range(2020, 2025)]
REGIMES = {"real": (REAL, "confirmado_real"), "mudou": (MUDOU, "confirmado_real"), "presumido": (PRES, "nao_real"),
           "simples": ([], "nao_real"), "sem_dado": ([], "sem_dado")}
VAZAMENTO = re.compile(r"\b831\b|\bMasters?\b|piloto|bloquead|escrow|venda gerencial|ticket|honor[aá]rio|deságio|\bfee\b|comiss|Junior|João Mattos|"
                       r"\bG[0-4]\b|\bD\d{2,3}\b|%|US\$|Selic|Carbono Oculto|Prazo de referência|(?-i:\bTributário\b)", re.I)


def perfil(cnae, ecf):
    return {"razao": "EMPRESA TESTE LTDA", "cnae": {"codigo": cnae, "descricao": "Atividade de teste"}, "cnaes_secundarios": [], "capital_social": 500000,
            "inicio_atividade": "2010-05-03", "municipio": "CAMPINAS", "uf": "SP", "porte": "Demais", "natureza_juridica": "Sociedade Empresária Limitada",
            "matriz": True, "ecf": ecf}


def texto(d):
    partes = [d["fazer"], d["precisa"], d["falta"]]
    for s in d["dossie"]:
        partes += s.get("paragrafos", []) + s.get("itens", [])
    partes += [e["produto"] + " " + e["nota"] for e in d["esteira"]]
    return "\n".join(partes)


def todos():
    for n, c in CNAES.items():
        for r, (ecf, faixa) in REGIMES.items():
            yield n, r, B.montar(perfil(c, ecf), faixa)


class DossieBase(unittest.TestCase):
    def test_sem_vazamento_nem_numero_de_resultado(self):
        for n, r, d in todos():
            t = texto(d)
            m = VAZAMENTO.search(t)
            self.assertIsNone(m, "%s/%s: %s" % (n, r, m and t[max(0, m.start() - 60):m.end() + 60]))
            # R$ só do capital social do perfil
            for f in re.findall(r"[^.\n]*R\$[^.\n]*", t):
                self.assertIn("Capital social", f, "%s/%s: %s" % (n, r, f))

    def test_teses_fora_da_vitrine_ou_dependentes_de_decisao(self):
        proibido = re.compile(r"sistema s|\bISS\b|Tema 1\.079|Tema 118|Tema 843|fora do PIS/COFINS|fora da base do IRPJ/CSLL \(Presumido\)|blindagem", re.I)
        for n, r, d in todos():
            self.assertIsNone(proibido.search(texto(d)), "%s/%s" % (n, r))

    def test_aliquota_zero_so_per_e_nunca_em_mercado_cafe_ou_nao_real(self):
        for n, r, d in todos():
            t = texto(d)
            self.assertNotIn("DCOMP", t.replace("(DCOMP)?", "").replace("nunca por compensação (DCOMP)", ""), "%s/%s" % (n, r))
            linhas = [l for s in d["dossie"] if s["titulo"].startswith("Como a Save") for l in s["itens"] if l.lower().startswith("recuperação tributária: alíquota zero")]
            if n in (2, 3, 4) or r in ("presumido", "simples"):
                self.assertEqual(linhas, [], "%s/%s" % (n, r))
                esteira = " ".join(e["produto"] for e in d["esteira"]).lower()
                self.assertNotIn("alíquota zero", esteira, "%s/%s" % (n, r))
            if linhas:
                self.assertIn("PER", linhas[0]); self.assertIn("controvertida", linhas[0]); self.assertIn("01/04/2026", linhas[0])

    def test_nao_real_nao_oferece_credito_de_insumos(self):
        for n, r, d in todos():
            if r in ("presumido", "simples"):
                itens = " ".join(l for s in d["dossie"] if s["titulo"].startswith("Como a Save") for l in s["itens"]).lower()
                self.assertNotIn("insumos", itens, "%s/%s" % (n, r))
                self.assertNotIn("conta gráfica", itens)
                self.assertNotIn("crédito presumido de compras", itens)
        simples = B.montar(perfil("4731800", []), "nao_real")
        self.assertIn("Simples", texto(simples))

    def test_janela_dos_cinco_anos_so_quando_mudou_para_o_real(self):
        t = texto(B.montar(perfil("1011101", MUDOU), "confirmado_real"))
        self.assertIn("mudou para o Lucro Real em 2023", t)
        self.assertIn("cinco anos", t)
        self.assertNotIn("mudou para o Lucro Real", texto(B.montar(perfil("1011101", REAL), "confirmado_real")))
        self.assertNotIn("mudou para o Lucro Real", texto(B.montar(perfil("1011101", PRES), "nao_real")))

    def test_funrural_sem_promessa_de_recuperar(self):
        for n in (1, 2):
            t = texto(B.montar(perfil(CNAES[n], REAL), "confirmado_real"))
            self.assertIn("ADI 4.395", t)
            self.assertIn("não há promessa de recuperação", t)
            self.assertNotRegex(t, r"recuperar os últimos|Tema 1\.079")

    def test_produto_em_validacao_so_descoberta_sem_condicao(self):
        for n, r, d in todos():
            for e in d["esteira"]:
                if re.search(r"crédito internacional|maquila", e["produto"].lower()):
                    self.assertEqual(e["status"], "descoberta")
                    self.assertNotRegex(e["nota"], r"garantia|demonstra|CND|Lucro Real|porte")
            t = texto(d)
            self.assertNotRegex(t, r"2 anos de demonstra|garantia real|garantias reais")

    def test_objecoes_usam_a_coluna_resposta(self):
        d = B.montar(perfil("1011101", REAL), "confirmado_real")
        obj = [i for s in d["dossie"] for i in s.get("itens", []) if "Resposta:" in i]
        self.assertGreaterEqual(len(obj), 6)
        for o in obj:
            resp = o.split("Resposta:", 1)[1].strip()
            self.assertGreater(len(resp), 30, o)
            self.assertNotRegex(resp, r"^(Lei|IN RFB|CTN|LC 214/2025, art\. 378$|Regra da casa)")

    def test_cnae_fora_do_cluster_e_perfil_nulo(self):
        d = B.montar(perfil("6201501", REAL), "confirmado_real")
        self.assertIn("fora dos clusters", texto(d))
        for faixa in ("sem_dado", "nao_real", "confirmado_real", "indisponivel"):
            for p in ({}, None, {"ecf": None, "cnae": None}, {k: None for k in perfil("1", []) }):
                d = B.montar(p, faixa)
                self.assertTrue(d["dossie"])
                self.assertNotRegex(texto(d), r"None|, ,|\(CNAE \)")

    def test_sem_prazo_nem_limiar_interno(self):
        for n, r, d in todos():
            t = texto(d)
            self.assertNotRegex(t, r"Prazo de referência|[>≥]\s*R\$|mi/mês|mil/mês|à vista ou em poucos dias|\(D\+30\)")

    def test_auditor_de_promessas_sem_alerta_alto_ou_medio(self):
        auditor = Path(__file__).resolve().parents[3] / "skills/depto-qualidade/scripts/auditar_texto.py"
        with tempfile.TemporaryDirectory() as tmp:
            for n, r, d in todos():
                (Path(tmp) / ("%s_%s.md" % (n, r))).write_text(texto(d), encoding="utf-8")
            res = subprocess.run([sys.executable, str(auditor), tmp, "--resumo"], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, res.stdout[-800:])


if __name__ == "__main__":
    unittest.main()
