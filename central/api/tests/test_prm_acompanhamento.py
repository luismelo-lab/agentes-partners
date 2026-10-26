"""Acompanhamento de negócios, painel do parceiro e dashboard comercial da Save (PRM-R113 a PRM-R118, Luis 26/10/2026):
visibilidade por campo, autorização, agregados (funil, aging, conversão, ciclo, forecast) e textos sem promessa."""
import json, os, re, subprocess, sys, tempfile, unittest
from datetime import date, timedelta
from pathlib import Path

from tests.prm_base import AGORA, BasePRM

from central_api.caminhos import repo
from central_api.prm import acompanhamento as AC
from central_api.prm import negocios as NG

HOJE = AGORA.date()


def d(off):
    return (HOJE + timedelta(days=off)).isoformat()


class Base(BasePRM):
    def get(self, u, caminho, **q):
        return self.http("GET", caminho, u, q or None)

    def ref_de(self, deal_id):
        return self.app.ref_estavel("neg", deal_id)

    def ficha(self, u, deal_id):
        return self.get(u, "/api/prm/parceiro/negocios/" + self.ref_de(deal_id))


# ---------------------------------------------------------------- visibilidade por campo (PRM-R113/R114/R115)
class Visibilidade(Base):
    def test_parceiro_ve_valores_com_ressalva(self):
        st, o = self.ficha("U-0001", "9100000004")
        self.assertEqual(st, 200)
        campos = {c["campo"]: c for s in o["secoes"] for c in s["campos"]}
        self.assertEqual(campos["valor_credito"]["valor"], 800000)
        self.assertIn("não é valor garantido", campos["valor_credito"]["ressalva"])
        self.assertIn("homologação da Receita", campos["valor_credito"]["ressalva"])
        self.assertEqual(campos["remuneracao_prevista"]["valor"], 40000.0)          # 800 mil × 20% × 25%
        self.assertTrue(campos["remuneracao_prevista"]["ressalva"].startswith("Previsto"))
        for k in ("etapa_crm", "teses", "produto", "criado_em", "fechado_em", "responsavel_save", "master", "consultor", "honorario_pct"):
            self.assertIn(k, campos)
        self.assertIn("linha_do_tempo", o)
        self.assertGreaterEqual(len(o["linha_do_tempo"]), 2)

    def test_campos_travados_nunca_saem(self):
        for u, deal in (("U-0001", "9100000004"), ("U-0001", "9100000014"), ("U-0004", "9100000020")):
            st, o = self.ficha(u, deal)
            self.assertEqual(st, 200)
            txt = json.dumps(o, ensure_ascii=False)
            for proibido in ("Nota interna", "Motivo interno", "Sócio fictício", "vendedor_pct", "probabilidade", "forecast", "BX-", "notas_internas", "contato_socio"):
                self.assertNotIn(proibido, txt, (u, deal, proibido))

    def test_trava_vale_mesmo_com_a_matriz_liberando(self):
        m = self.app.param("negocio.visibilidade_campos")
        for k in AC.TRAVADOS:
            m[k] = dict(m.get(k, {}), parceiro=True)
        self.app.param.definir("negocio.visibilidade_campos", m)
        o = self.ficha("U-0001", "9100000014")[1]
        txt = json.dumps(o, ensure_ascii=False)
        self.assertNotIn("Nota interna", txt)
        self.assertNotIn("Motivo interno", txt)
        a = self.ator("U-0001")
        self.assertFalse(any(AC.visivel(self.app, a, k) for k in AC.TRAVADOS))

    def test_matriz_esconde_o_valor_quando_o_luis_mudar(self):
        m = self.app.param("negocio.visibilidade_campos")
        m["valor_credito"]["parceiro"] = False
        m["remuneracao_prevista"]["parceiro"] = False
        self.app.param.definir("negocio.visibilidade_campos", m)
        o = self.ficha("U-0001", "9100000004")[1]
        campos = {c["campo"] for s in o["secoes"] for c in s["campos"]}
        self.assertNotIn("valor_credito", campos)
        self.assertNotIn("remuneracao_prevista", campos)
        lst = self.get("U-0001", "/api/prm/parceiro/negocios", situacao="todos")[1]
        self.assertTrue(all("valor_credito" not in i for i in lst["itens"]))
        self.assertIsNone(lst["valor_total"])
        p = self.get("U-0001", "/api/prm/parceiro/painel")[1]
        self.assertTrue(all(x["valor"] is None for x in p["pipeline"]))
        self.assertNotIn("remuneracao", p)

    def test_campo_fora_da_matriz_nao_sai(self):
        m = self.app.param("negocio.visibilidade_campos")
        del m["teses"]
        self.app.param.definir("negocio.visibilidade_campos", m)
        o = self.ficha("U-0001", "9100000004")[1]
        self.assertNotIn("teses", {c["campo"] for s in o["secoes"] for c in s["campos"]})

    def test_remuneracao_e_extrato_so_para_o_titular(self):
        st, o = self.ficha("U-0004", "9100000020")
        self.assertEqual(st, 200)
        campos = {c["campo"] for s in o["secoes"] for c in s["campos"]}
        self.assertTrue({"remuneracao_prevista", "percentual_termo"}.isdisjoint(campos))
        self.assertNotIn("extrato", o)
        self.assertIn("valor_credito", campos)
        p = self.get("U-0004", "/api/prm/parceiro/painel")[1]
        self.assertNotIn("remuneracao", p)
        self.assertEqual(p["consultores"], [])
        t = self.ficha("U-0001", "9100000020")[1]
        self.assertIn("extrato", t)

    def test_proximo_passo_do_crm_passa_pelo_auditor(self):
        negs = self.app.repo.listar("negocio")
        for n in negs:
            if n["deal_id"] == "9100000003":
                n["proximo_passo_crm"] = "A Save garante a recuperação do crédito em 30 dias, sem risco."
            if n["deal_id"] == "9100000005":
                n["proximo_passo_crm"] = "Combinar a data da apresentação do diagnóstico com você."
        self.app.repo.carregar_gerado("negocio", negs)
        ruim = {c["campo"]: c["valor"] for s in self.ficha("U-0001", "9100000003")[1]["secoes"] for c in s["campos"]}
        bom = {c["campo"]: c["valor"] for s in self.ficha("U-0001", "9100000005")[1]["secoes"] for c in s["campos"]}
        self.assertNotIn("proximo_passo_crm", ruim)
        self.assertEqual(bom["proximo_passo_crm"], "Combinar a data da apresentação do diagnóstico com você.")
        # a Save vê o texto como está no CRM
        s = self.get("daniela", "/api/prm/save/negocios/9100000003")[1]
        self.assertIn("garante", json.dumps(s, ensure_ascii=False))

    def test_save_ve_os_internos_e_comissao_so_luis_e_financeiro(self):
        o = self.get("daniela", "/api/prm/save/negocios/9100000004")[1]
        interno = next(s for s in o["secoes"] if s["titulo"] == "Interno da Save")
        campos = {c["campo"] for c in interno["campos"]}
        self.assertIn("notas_internas", campos)
        self.assertNotIn("outras_comissoes", campos)
        o = self.get("luis", "/api/prm/save/negocios/9100000004")[1]
        self.assertIn("outras_comissoes", {c["campo"] for s in o["secoes"] for c in s["campos"]})

    def test_sem_probabilidade_nem_chance_no_que_o_parceiro_recebe(self):
        lst = self.get("U-0001", "/api/prm/parceiro/negocios", situacao="todos", por_pagina="200")[1]
        txt = json.dumps([lst, self.get("U-0001", "/api/prm/parceiro/painel")[1]] + [self.ficha("U-0001", self._deal(i["ref"]))[1] for i in lst["itens"][:10]],
                         ensure_ascii=False).lower()
        for p in ("probabilidade", "chance", "êxito garantido", "forecast", "prazo de restituição"):
            self.assertNotIn(p, txt)

    def _deal(self, ref):
        return next(n["deal_id"] for n in self.app.repo.listar("negocio") if self.ref_de(n["deal_id"]) == ref)


# ---------------------------------------------------------------- autorização (dono da linha, escopo do escritório, papel Save)
class Autorizacao(Base):
    def test_consultor_ve_so_os_proprios(self):
        o = self.get("U-0004", "/api/prm/parceiro/negocios", situacao="todos", por_pagina="200")[1]
        deals = {self._deal(i["ref"]) for i in o["itens"]}
        self.assertTrue(deals)
        self.assertTrue(all(self.app.repo.obter("negocio", x)["parceiro_id"] == "P-0011" for x in deals))

    def test_consultor_nao_abre_negocio_de_outro_consultor_nem_do_titular(self):
        self.assertEqual(self.ficha("U-0004", "9100000004")[0], 404)   # do Consultor A1
        self.assertEqual(self.ficha("U-0004", "9100000003")[0], 404)   # do próprio Master A
        self.assertEqual(self.ficha("U-0004", "9100000020")[0], 200)
        negado = [a for a in self.app.repo.listar("acesso_log") if a.get("usuario_id") == "U-0004" and a["resultado"] == "negado"]
        self.assertTrue(negado)

    def test_outro_escritorio_404(self):
        self.assertEqual(self.ficha("U-0003", "9100000004")[0], 404)
        self.assertEqual(self.ficha("U-0001", "9100000012")[0], 404)
        self.assertEqual(self.get("U-0001", "/api/prm/parceiro/negocios/0123456789abcdef")[0], 404)

    def test_parceiro_nao_ve_agregados_nem_lista_do_canal(self):
        for u in ("U-0001", "U-0004"):
            self.assertEqual(self.get(u, "/api/prm/save/dashboard")[0], 403)
            self.assertEqual(self.get(u, "/api/prm/save/negocios")[0], 403)
            self.assertEqual(self.get(u, "/api/prm/save/negocios/9100000004")[0], 403)

    def test_save_nao_usa_rota_do_parceiro(self):
        self.assertEqual(self.get("daniela", "/api/prm/parceiro/negocios")[0], 403)
        self.assertEqual(self.get("daniela", "/api/prm/parceiro/painel")[0], 403)

    def test_papeis_da_save(self):
        self.assertEqual(self.get("financeiro", "/api/prm/save/dashboard")[0], 200)   # agregado
        self.assertEqual(self.get("financeiro", "/api/prm/save/negocios")[0], 403)    # sem ver_negocios
        self.assertEqual(self.get("daniela", "/api/prm/save/negocios")[0], 200)

    def test_titular_filtra_por_consultor_e_consultor_nao_amplia(self):
        a = self.get("U-0001", "/api/prm/parceiro/negocios", situacao="todos", consultor="U-0004", por_pagina="200")[1]
        self.assertTrue(a["itens"])
        self.assertTrue(all(self.app.repo.obter("negocio", self._deal(i["ref"]))["parceiro_id"] == "P-0011" for i in a["itens"]))
        b = self.get("U-0004", "/api/prm/parceiro/negocios", situacao="todos", consultor="U-0002", por_pagina="200")[1]
        self.assertTrue(all(self.app.repo.obter("negocio", self._deal(i["ref"]))["parceiro_id"] == "P-0011" for i in b["itens"]))
        c = self.get("U-0001", "/api/prm/parceiro/negocios", situacao="todos", consultor="U-0003")[1]   # usuário de outro escritório
        self.assertEqual(c["total"], 0)

    def test_sem_ranking_no_painel_do_parceiro(self):
        o = self.get("U-0001", "/api/prm/parceiro/painel")[1]
        txt = json.dumps(o, ensure_ascii=False)
        for k in ("Master B", "Master C", "P-0002", "ranking", "concentracao", "por_master"):
            self.assertNotIn(k, txt)

    def test_termos_pendentes_428(self):
        self.assertEqual(self.get("U-0002", "/api/prm/parceiro/negocios")[0], 428)

    def _deal(self, ref):
        return next(n["deal_id"] for n in self.app.repo.listar("negocio") if self.ref_de(n["deal_id"]) == ref)


# ---------------------------------------------------------------- lista: filtros, ordenação, paginação, quadro
class Lista(Base):
    def test_paginacao_e_ordem_por_valor(self):
        o = self.get("U-0001", "/api/prm/parceiro/negocios", situacao="todos", ordem="valor", por_pagina="5")[1]
        self.assertEqual(len(o["itens"]), 5)
        self.assertEqual(o["paginas"], -(-o["total"] // 5))
        vs = [i.get("valor_credito") or 0 for i in o["itens"]]
        self.assertEqual(vs, sorted(vs, reverse=True))
        o2 = self.get("U-0001", "/api/prm/parceiro/negocios", situacao="todos", ordem="valor", por_pagina="5", pagina="2")[1]
        self.assertFalse({i["ref"] for i in o["itens"]} & {i["ref"] for i in o2["itens"]})

    def test_filtros(self):
        o = self.get("U-0001", "/api/prm/parceiro/negocios", estado="em_diagnostico")[1]
        self.assertTrue(o["itens"])
        self.assertTrue(all(i["estado"] == "em_diagnostico" for i in o["itens"]))
        g = self.get("U-0001", "/api/prm/parceiro/negocios", situacao="ganhos")[1]
        self.assertTrue(all(i["situacao"] == "ganhos" for i in g["itens"]))
        t = g["filtros"]["teses"][0]
        x = self.get("U-0001", "/api/prm/parceiro/negocios", situacao="todos", tese=t)[1]
        self.assertTrue(all(t in i["teses"] for i in x["itens"]))
        q = self.get("U-0001", "/api/prm/parceiro/negocios", situacao="todos", q="empresa 03")[1]
        self.assertEqual([i["nome"] for i in q["itens"]], ["Empresa 03 Transportes Ltda"])
        r = self.get("U-0001", "/api/prm/parceiro/negocios", situacao="todos", de=d(-60), ate=d(0))[1]
        self.assertTrue(all(d(-60) <= i["criado_em"] <= d(0) for i in r["itens"]))
        self.assertEqual(self.get("U-0001", "/api/prm/parceiro/negocios", situacao="xyz")[0], 422)

    def test_colunas_do_quadro_somam_o_total(self):
        o = self.get("U-0001", "/api/prm/parceiro/negocios", por_pagina="200")[1]
        self.assertEqual(sum(c["n"] for c in o["colunas"]), o["total"])
        self.assertEqual([c["estado"] for c in o["colunas"]][:5], list(AC.ABERTOS))

    def test_save_drill_down_por_master_e_cafe_fora(self):
        o = self.get("daniela", "/api/prm/save/negocios", master="P-0002", situacao="todos", por_pagina="200")[1]
        self.assertTrue(o["itens"])
        self.assertTrue(all(i["master_id"] == "P-0002" for i in o["itens"]))
        todos = self.get("daniela", "/api/prm/save/negocios", situacao="todos", por_pagina="200")[1]
        self.assertFalse(any(i["cafe"] for i in todos["itens"]))
        cafe = self.get("daniela", "/api/prm/save/negocios", situacao="todos", por_pagina="200", cafe="1")[1]
        self.assertGreater(cafe["total"], todos["total"])


# ---------------------------------------------------------------- agregados com carteira controlada
class Agregados(Base):
    def setUp(self):
        super().setUp()
        self.app.param.definir("painel.base_pequena", 2)
        os.environ["PRM_GESTAO"] = os.path.join(self.tmp.name, "nao-existe.json")
        base = {"pipeline": "RT - Real & Presumido", "parceiro_id": "P-0001", "master_id": "P-0001", "cnpj_mascara": "TE.***.***/****-00", "cafe": False}
        negs = [
            dict(base, deal_id="9300000001", status="ganho", etapa="Negócio Fechado", criado_em=d(-85), fechado_em=d(-10), valor_credito=1000000.0, honorario_pct=0.2,
                 historico_etapas=[{"etapa": "Novo Negócio", "entrou_em": d(-85)}, {"etapa": "Negócio Fechado", "entrou_em": d(-10)}]),
            dict(base, deal_id="9100000014", status="perdido", etapa="Negócio Perdido", criado_em=d(-80), fechado_em=d(-20), valor_credito=150000.0,
                 historico_etapas=[{"etapa": "Novo Negócio", "entrou_em": d(-80)}, {"etapa": "Em Diagnóstico", "entrou_em": d(-60)},
                                   {"etapa": "Apresentação de Diagnóstico", "entrou_em": d(-40)}, {"etapa": "Negócio Perdido", "entrou_em": d(-20)}]),
            dict(base, deal_id="9300000003", status="aberto", etapa="Negociação", criado_em=d(-50), entrou_etapa_em=d(-5), valor_credito=300000.0,
                 previsao_fechamento_em="2026-11-15"),
            dict(base, deal_id="9300000004", status="aberto", etapa="Novo Negócio", criado_em=d(-45), entrou_etapa_em=d(-45), valor_credito=None,
                 previsao_fechamento_em="2026-12-10"),
            dict(base, deal_id="9300000005", status="aberto", etapa="Em Diagnóstico", criado_em=d(-200), entrou_etapa_em=d(-70), valor_credito=50000.0, cafe=True),
            dict(base, deal_id="9300000006", status="ganho", etapa="Negócio Fechado", criado_em=d(-300), fechado_em=d(-150), valor_credito=200000.0, honorario_pct=0.2),
            dict(base, deal_id="9300000007", status="ganho", etapa="Negócio Fechado", parceiro_id="P-0002", master_id="P-0002", criado_em=d(-60), fechado_em=d(-25),
                 valor_credito=500000.0),
        ]
        self.app.repo.carregar_gerado("negocio", negs)
        self.app.repo.carregar_gerado("extrato_linha", [])

    def tearDown(self):
        os.environ.pop("PRM_GESTAO", None)
        super().tearDown()

    def test_funil_do_parceiro(self):
        p = self.get("U-0001", "/api/prm/parceiro/painel", periodo="90")[1]
        f = p["funil"]
        self.assertEqual(f["coorte"], 4)   # criados nos 90 dias (o café do parceiro entrou há 200 dias)
        self.assertEqual([e["n"] for e in f["etapas"]], [4, 3, 3, 2, 1])   # o perdido chegou à apresentação pelo histórico
        self.assertEqual(f["etapas"][1]["pct_do_inicio"], 75.0)
        self.assertEqual(f["etapas"][4]["pct_da_anterior"], 50.0)
        ns = [e["n"] for e in f["etapas"]]
        self.assertEqual(ns, sorted(ns, reverse=True))

    def test_conversao_ciclo_e_comparacao(self):
        p = self.get("U-0001", "/api/prm/parceiro/painel", periodo="90")[1]
        a = p["periodo_atual"]
        self.assertEqual((a["ganhos"]["n"], a["perdidos"]["n"]), (1, 1))
        self.assertEqual(a["conversao"]["pct"], 50.0)
        self.assertFalse(a["conversao"]["base_pequena"])
        self.assertEqual(a["ciclo"]["media_dias"], 75)
        self.assertEqual(a["ganhos"]["valor"], 1000000.0)
        self.assertEqual(p["comparacao"]["ganhos_n"], {"atual": 1, "anterior": 1, "delta": 0})   # o de 150 dias atrás cai no período anterior
        self.assertEqual(p["comparacao"]["ganhos_valor"]["delta"], 800000.0)
        self.app.param.definir("painel.base_pequena", 5)
        p = self.get("U-0001", "/api/prm/parceiro/painel", periodo="90")[1]
        self.assertIsNone(p["periodo_atual"]["conversao"]["pct"])
        self.assertTrue(p["periodo_atual"]["conversao"]["base_pequena"])

    def test_aging_e_parados(self):
        p = self.get("U-0001", "/api/prm/parceiro/painel")[1]
        ag = {e["estado"]: e for e in p["aging"]["por_estado"]}
        self.assertEqual(ag["contrato"]["faixas"][0]["n"], 1)          # 5 dias: até 15
        self.assertEqual(ag["recebido"]["faixas"][2]["n"], 1)          # 45 dias: 31 a 60
        self.assertEqual(ag["em_diagnostico"]["faixas"][3]["n"], 1)    # 70 dias: mais de 60
        self.assertEqual(p["aging"]["total_parados"], 2)
        self.assertEqual([i["dias_na_etapa"] for i in p["aging"]["parados"]], [70, 45])
        lst = self.get("U-0001", "/api/prm/parceiro/negocios", parado="1")[1]
        self.assertEqual(lst["total"], 2)

    def test_pipeline_e_remuneracao(self):
        p = self.get("U-0001", "/api/prm/parceiro/painel")[1]
        pipe = {x["estado"]: x for x in p["pipeline"]}
        self.assertEqual((pipe["recebido"]["n"], pipe["recebido"]["valor"], pipe["recebido"]["sem_valor"]), (1, 0, 1))
        self.assertEqual(pipe["contrato"]["valor"], 300000.0)
        r = p["remuneracao"]
        self.assertEqual(r["prevista"], round(1000000 * 0.2 * 0.25 + 200000 * 0.2 * 0.25, 2))
        self.assertEqual((r["recebida_pela_save"], r["paga"]), (0, 0))

    def test_dashboard_da_save(self):
        o = self.get("daniela", "/api/prm/save/dashboard", periodo="90")[1]
        k = o["kpis"]
        self.assertEqual(k["pipeline_n"], 2)                 # o café fica fora (R112)
        self.assertEqual(k["ganhos_n"], 2)                   # A e o do Master B
        self.assertEqual(k["conversao"]["pct"], round(100 * 2 / 3, 1))
        f = {m["mes"]: m for m in o["forecast"]["meses"]}
        self.assertEqual(f["2026-10"]["meta"], 75000000.0)
        self.assertEqual(f["2026-11"]["meta"], 100000000.0)
        self.assertEqual(f["2026-10"]["realizado"], 1500000.0)
        self.assertEqual(f["2026-11"]["em_contrato"], 300000.0)
        self.assertEqual(f["2026-12"]["demais_abertos"], 0)
        self.assertIn("canal.meta_mensal", o["forecast"]["fonte_meta"])
        conc = o["concentracao"]
        self.assertEqual(conc["top1_pct"], round(100 * 1200000 / 1700000, 1))
        self.assertEqual(conc["top5_pct"], 100.0)
        cr = o["conversao_registro"]
        self.assertEqual((cr["registrado"]["perdidos"], cr["registrado"]["n"]), (1, 1))   # 9100000014 tem registro
        self.assertTrue(cr["registrado"]["base_pequena"])
        self.assertEqual(cr["nao_registrado"]["ganhos"], 2)
        pm = {m["master_id"]: m for m in o["por_master"]}
        self.assertEqual(pm["P-0001"]["abertos"], 2)
        self.assertEqual([m["nome"] for m in o["por_master"]], sorted(m["nome"] for m in o["por_master"]))   # alfabética, não ranking
        self.assertEqual(o["pipeline"][0]["drill"], {"estado": "recebido", "situacao": "andamento"})

    def test_filtro_de_master_tira_a_meta_do_canal(self):
        o = self.get("daniela", "/api/prm/save/dashboard", periodo="90", master="P-0002")[1]
        self.assertEqual([m["master_id"] for m in o["por_master"]], ["P-0002"])
        self.assertTrue(all(m["meta"] is None for m in o["forecast"]["meses"]))
        self.assertEqual(o["kpis"]["ganhos_n"], 1)

    def test_meta_do_pacote_da_gestao(self):
        arq = os.path.join(self.tmp.name, "gestao.json")
        with open(arq, "w") as f:
            json.dump({"meta": {"decisao": "D111", "meses": [{"mes": "2026-10", "meta_rs": 1}, {"mes": "2026-11", "meta_rs": 2}]}}, f)
        os.environ["PRM_GESTAO"] = arq
        o = self.get("daniela", "/api/prm/save/dashboard")[1]
        self.assertEqual([m["meta"] for m in o["forecast"]["meses"]], [1.0, 2.0])
        self.assertIn("gestao.json", o["forecast"]["fonte_meta"])

    def test_dormentes(self):
        o = self.get("daniela", "/api/prm/save/dashboard")[1]
        # Master A tem negócio novo há 45 dias (não dorme); Master B teve ganho e o último negócio entrou há 60 dias (< 90): ninguém dorme
        self.assertEqual(o["dormentes"], [])
        self.app.param.definir("canal.dormente_dias", 50)
        o = self.get("daniela", "/api/prm/save/dashboard")[1]
        self.assertEqual([x["parceiro_id"] for x in o["dormentes"]], ["P-0002"])

    def test_periodo_invalido(self):
        self.assertEqual(self.get("daniela", "/api/prm/save/dashboard", de=d(0), ate=d(-10))[0], 422)


# ---------------------------------------------------------------- textos sem promessa (auditor de promessas)
class Textos(unittest.TestCase):
    def _auditar(self, textos):
        script = repo() / "skills/depto-qualidade/scripts/auditar_texto.py"
        with tempfile.TemporaryDirectory() as dd:
            arq = os.path.join(dd, "t.md")
            with open(arq, "w", encoding="utf-8") as f:
                f.write("\n\n".join(textos))
            r = subprocess.run([sys.executable, "-I", str(script), arq, "--json"], capture_output=True, text=True)
        return [a for x in json.loads(r.stdout).values() for a in x["achados"] if a["severidade"] in ("ALTO", "MEDIO")]

    def test_matriz_de_visibilidade_passa_no_auditor(self):
        from central_api.prm.parametros import catalogo
        m = catalogo()["negocio.visibilidade_campos"]["valor"]
        textos = [v["rotulo"] for v in m.values()] + [v["ressalva"] for v in m.values() if v.get("ressalva")]
        self.assertEqual(self._auditar(textos), [])
        self.assertIn("não é valor garantido", m["valor_credito"]["ressalva"])
        self.assertTrue(m["remuneracao_prevista"]["ressalva"].startswith("Previsto"))

    def test_textos_novos_da_tela_passam_no_auditor(self):
        js = (Path(__file__).resolve().parents[2] / "web" / "prm.js").read_text(encoding="utf-8")
        ini = js.index("NEGÓCIOS, PAINEL DE VENDAS E DASHBOARD COMERCIAL")
        fim = js.index("// ------------------------------------------------------------------ início", ini)
        textos = [t for t in re.findall(r'"([^"\n]{12,})"', js[ini:fim]) if " " in t and not t.startswith(("#/", "prm-", "parceiro/", "save/"))]
        self.assertGreater(len(textos), 40)
        self.assertEqual(self._auditar(textos), [])

    def test_matriz_trava_os_campos_sensiveis(self):
        from central_api.prm.parametros import catalogo
        m = catalogo()["negocio.visibilidade_campos"]["valor"]
        for k in AC.TRAVADOS:
            self.assertFalse(m[k]["parceiro"], k)
            self.assertTrue(m[k].get("travado"), k)


if __name__ == "__main__":
    unittest.main()
