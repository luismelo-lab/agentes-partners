"""Carga da demonstração com dados FICTÍCIOS (fixtures/demo.json): Masters A–I, consultores, Empresas 01–21 com CNPJ
alfanumérico de teste (o dígito verificador é calculado aqui), negócios do espelho, registros em todos os estados,
conflito, pendência, extrato, demandas e um histórico de respostas de teste. Monta também o índice HMAC da 1ª checagem
e a fonte da Receita de teste (regime.FONTE_LOCAL), para a demo rodar sem rede e sem nenhum dado real."""
import json, os
from datetime import datetime, time as dtime, timedelta
from pathlib import Path

from .. import esteira, negocio_ativo as NA, regime
from . import calendario as CAL
from . import demandas as DM
from . import notificacoes as NT
from .repositorio import TABELAS

ARQ = Path(__file__).with_name("fixtures") / "demo.json"


def ler():
    with open(ARQ, encoding="utf-8") as f:
        return json.load(f)


def cnpj_de(raiz, ordem="0001"):
    from cnpj import dv_cnpj
    b = raiz + ordem
    return b + dv_cnpj(b)


# ---------------------------------------------------------------- carteira fictícia para o acompanhamento e os dashboards
SEGMENTOS = [("1091102", "Fabricação de produtos de padaria", "Panificação"), ("4711302", "Supermercados", "Supermercados"),
             ("4930202", "Transporte rodoviário de carga", "Transportes"), ("1011201", "Frigorífico", "Alimentos"),
             ("4639701", "Atacado de alimentos", "Distribuidora"), ("2222600", "Embalagens plásticas", "Embalagens"),
             ("4744099", "Materiais de construção", "Materiais"), ("1531901", "Calçados de couro", "Calçados"),
             ("2539001", "Usinagem e tornearia", "Metalúrgica"), ("4930201", "Transporte municipal de carga", "Logística"),
             ("8610101", "Hospital geral", "Saúde"), ("4731800", "Comércio de combustíveis", "Combustíveis")]
UFS = ["SP", "MG", "PR", "SC", "RS", "GO", "BA", "PE", "RJ", "ES", "MT", "CE"]
TESES = ["Insumos de PIS/COFINS", "Exclusão do ICMS da base do PIS/COFINS", "ICMS-ST na base do PIS/COFINS", "ISS na base do PIS/COFINS (Tema 118)",
         "Créditos extemporâneos de PIS/COFINS", "Contribuições ao Sistema S"]
FUNIS = ["RT - Real & Presumido"] * 7 + ["RT - Simples Nacional", "Gestão de Passivo", "Planejamento Tributário"]
ETAPAS_NIVEL = [["Novo Negócio", "Em Contato", "Agendamento", "Contato Futuro"], ["Em Diagnóstico", "Análise de Documentos", "Autorização Equipe Senior LR"],
                ["Apresentação de Diagnóstico"], ["Negociação", "Contrato Enviado", "Pendência Fechamento"]]
NIVEL_ETAPA = {e: i for i, xs in enumerate(ETAPAS_NIVEL) for e in xs}
NIVEL_ETAPA.update({"Análise com Pendência": 1, "Documentação Pendente": 1, "Em Apresentação": 2, "Contrato Assinado": 3, "Lead Novo - Prospecção": 0, "Follow - Up": 0})
RESPONSAVEIS = ["Daniela (Área Master)", "Área Partners · Masters", "Área Partners · técnico"]
PASSOS = {0: ["Agendar a primeira conversa com o financeiro da empresa", "Retomar o contato com o decisor"],
          1: ["Conferir os arquivos do SPED recebidos", "Concluir a leitura técnica dos documentos"],
          2: ["Combinar a data da apresentação do diagnóstico com você", "Apresentar o resultado do diagnóstico à diretoria"],
          3: ["Acompanhar a assinatura do contrato pela empresa", "Ajustar a minuta com o jurídico da empresa"]}
DOCS = ["SPED Contribuições dos últimos 5 anos", "SPED Fiscal (EFD ICMS/IPI)", "Procuração eletrônica no e-CAC", "Balancetes do último exercício", "Relação de notas de entrada"]
# Master → (peso, consultores) — o Master A concentra a carteira, como no canal real
MASTERS = {"P-0001": (9, ["P-0010", "P-0011"]), "P-0002": (5, ["P-0012"]), "P-0003": (4, ["P-0013"]), "P-0004": (3, []), "P-0005": (3, []),
           "P-0006": (2, []), "P-0007": (2, []), "P-0008": (1, []), "P-0009": (1, [])}


def _historico(rnd, nivel_final, criado, fim, etapa_final):
    """Etapas passadas em ordem, com o dia relativo de entrada (criado ≤ ... ≤ fim)."""
    niveis = list(range(0, nivel_final + 1))
    pontos = sorted(rnd.randint(criado, fim) for _ in niveis[1:])
    h = []
    for i, nv in enumerate(niveis):
        etapa = etapa_final if (i == len(niveis) - 1 and etapa_final in NIVEL_ETAPA) else rnd.choice(ETAPAS_NIVEL[nv])
        h.append({"etapa": etapa, "dia": criado if i == 0 else pontos[i - 1]})
    return h


def enriquecer(n, rnd):
    """Campos do card do HubSpot que o mapeamento da 03 traz (dados FICTÍCIOS). Não sobrescreve o que a fixture já tem."""
    st = n["status"]
    criado = n.get("criado") if n.get("criado") is not None else -30
    if st == "aberto":
        nv = NIVEL_ETAPA.get(n["etapa"], 0)
        ent = n.get("entrou_etapa") if n.get("entrou_etapa") is not None else criado
        hist = _historico(rnd, nv, criado, ent, n["etapa"])
        hist[-1]["dia"] = ent
    else:
        fim = n.get("fechado") if n.get("fechado") is not None else 0
        nv = 3 if st == "ganho" else rnd.randint(0, 3)
        hist = _historico(rnd, nv, criado, max(criado, fim - 5), None)
        hist.append({"etapa": n["etapa"], "dia": fim})
    seg = rnd.choice(SEGMENTOS)
    base = {"historico": hist, "teses": rnd.sample(TESES, rnd.randint(1, 3)) if n["pipeline"].startswith("RT") else [],
            "responsavel": rnd.choice(RESPONSAVEIS), "uf": rnd.choice(UFS), "porte": rnd.choice(["DEMAIS", "DEMAIS", "EPP"]), "segmento": seg[2],
            "proximo_passo": rnd.choice(PASSOS[min(nv, 3)]) if st == "aberto" else None,
            "previsao": rnd.randint(3, 65) if st == "aberto" else None,
            "ecac": rnd.random() < 0.5 if nv >= 1 else False, "anexo_diagnostico": nv >= 2, "parecer": nv >= 2 and rnd.random() < 0.6,
            "documentos": [{"item": d, "situacao": rnd.choice(["recebido", "recebido", "pendente"])} for d in rnd.sample(DOCS, 2 + min(nv, 2))] if nv >= 1 else [],
            "notas_internas": "Nota interna fictícia da Área Partners (não vai ao parceiro).", "probabilidade": [0.1, 0.2, 0.4, 0.6, 0.9][min(nv + 1, 4)] if st == "aberto" else None,
            "motivo_perda": "Motivo interno fictício" if st == "perdido" else None, "contato_socio": "Sócio fictício da empresa", "id_bitrix": ("BX-%s" % n["deal_id"][-4:]) if st == "ganho" else None,
            "ultima_atividade": n.get("ultima_atividade") if n.get("ultima_atividade") is not None else (hist[-1]["dia"] if st == "aberto" else None)}
    for k, v in base.items():
        n.setdefault(k, v)
    return n


def gerar_carteira(fx, quantos=64):
    """Empresas 22+ e negócios 9200000001+ fictícios e determinísticos (semente fixa). Sem nenhum negócio em etapa de pendência
    no Master A (os testes contam as pendências dele)."""
    import random
    rnd = random.Random(2026)
    pesos = [(m, w) for m, (w, _) in MASTERS.items()]
    total = sum(w for _, w in pesos)
    empresas, negocios = {}, []
    for i in range(quantos):
        k = "%02d" % (22 + i)
        seg = SEGMENTOS[i % len(SEGMENTOS)]
        empresas[k] = {"raiz": "TESTE%03d" % (22 + i), "nome": "Empresa %s %s Ltda" % (k, seg[2]), "uf": UFS[i % len(UFS)], "cnae": seg[0], "cnae_desc": seg[1],
                       "porte": "DEMAIS", "regime": "LUCRO REAL"}
        x = rnd.uniform(0, total)
        for m, w in pesos:
            x -= w
            if x <= 0:
                break
        cons = MASTERS[m][1]
        pid = rnd.choice(cons) if cons and rnd.random() < 0.4 else m
        r = rnd.random()
        st = "aberto" if r < 0.5 else ("ganho" if r < 0.78 else "perdido")
        criado = -rnd.randint(4, 330)
        n = {"deal_id": "92%08d" % (i + 1), "empresa": k, "parceiro_id": pid, "master_id": m, "pipeline": rnd.choice(FUNIS), "status": st, "criado": criado,
             "empresa_nome": empresas[k]["nome"]}
        valor = rnd.choice([90, 140, 220, 310, 450, 600, 780, 950, 1200, 1600, 2300, 3100]) * 1000 + rnd.randint(0, 99) * 100
        if st == "aberto":
            nv = rnd.choice([0, 0, 1, 1, 1, 2, 2, 3, 3])
            etapas = ETAPAS_NIVEL[nv] + (["Análise com Pendência"] if nv == 1 and m != "P-0001" else [])
            n["etapa"] = rnd.choice(etapas)
            n["entrou_etapa"] = min(0, criado + rnd.randint(0, max(1, -criado)))
            n["valor_credito"] = valor if rnd.random() < 0.8 else None
        else:
            fim = min(-1, criado + rnd.randint(25, 200))
            if st == "ganho" and rnd.random() < 0.3:
                fim = -rnd.randint(1, 24)       # ganhos do mês corrente (realizado contra a meta)
                criado = min(criado, fim - 30); n["criado"] = criado
            n["fechado"] = fim
            n["etapa"] = "Negócio Fechado" if st == "ganho" else "Negócio Perdido"
            n["valor_credito"] = valor
            if st == "ganho":
                n["honorario_pct"] = 0.2 if rnd.random() < 0.8 else None
                n["parceiro_pct_card"] = 0.25
        n["cafe"] = i in (5, 40)
        negocios.append(enriquecer(n, rnd))
    return empresas, negocios


def ler_completo():
    """demo.json + a carteira gerada (o que a carga usa)."""
    import random
    fx = ler()
    emp, negs = gerar_carteira(fx)
    fx["empresas"].update(emp)
    for n in fx["negocios"]:
        enriquecer(n, random.Random(int(n["deal_id"])))
        n.setdefault("empresa_nome", fx["empresas"][n["empresa"]]["nome"])  # fictício; o espelho real não guarda o nome (03 §4.1)
    fx["negocios"] = fx["negocios"] + negs
    return fx


def cenarios(fx=None):
    """Lista para o painel de teste do servidor local: empresa, CNPJ (calculado na hora) e o que acontece."""
    from cnpj import formatar_cnpj
    fx = fx or ler()
    return [{"empresa": fx["empresas"][k]["nome"], "cnpj": formatar_cnpj(cnpj_de(fx["empresas"][k]["raiz"])), "cenario": v} for k, v in fx["cenarios_cnpj"].items()]


def _receita(fx):
    por = {cnpj_de(e["raiz"]): e for e in fx["empresas"].values()}

    def fonte(cnpj):
        e = por.get(cnpj)
        if not e:
            return None
        return {"razao_social": e["nome"].upper(), "nome_fantasia": None, "cnae_fiscal": e["cnae"], "cnae_fiscal_descricao": e["cnae_desc"], "uf": e["uf"],
                "municipio": None, "porte": e["porte"], "descricao_situacao_cadastral": e.get("situacao", "ATIVA"), "identificador_matriz_filial": 1,
                "capital_social": 100000.0, "data_inicio_atividade": "2012-03-01", "natureza_juridica": "Sociedade Empresária Limitada",
                "regime_tributario": [{"ano": 2025, "forma_de_tributacao": e["regime"]}] if e.get("regime") else [],
                "opcao_pelo_simples": bool(e.get("simples")), "opcao_pelo_mei": False, "cnaes_secundarios": []}
    return fonte


def ligar_fontes(fx=None):
    """Receita de teste para a consulta de Lucro Real (sem rede)."""
    regime.FONTE_LOCAL = _receita(fx or ler())


def montar_indice(fx, pasta_esteira):
    """Índice HMAC dos negócios abertos ou ganhos (mais os do índice sem espelho), como a rotina Dados do dia."""
    NA.DIR = esteira.DIR = pasta_esteira
    NA.INDICE = os.path.join(pasta_esteira, "indice-negocios-ativos.json")
    NA._cache.update(mtime=None, chaves=None)
    negs = [{"status": n["status"], "extras": {"cnpj": cnpj_de(fx["empresas"][n["empresa"]]["raiz"])}} for n in fx["negocios"]]
    negs += [{"status": "aberto", "extras": {"cnpj": cnpj_de(fx["empresas"][k]["raiz"])}} for k in fx.get("indice_extra", [])]
    idx = NA.construir(negs, CAL.local(datetime.now(CAL.UTC)).strftime("%Y-%m-%dT%H:%M:%S"), "fixtures/demo.json")
    NA.gravar(idx, NA.INDICE)
    return idx["total"]


def carregar(app, pasta_esteira, limpar=True):
    fx = ler_completo()
    base = app.agora()
    hoje = CAL.dia(base)

    def d(off):
        return (hoje + timedelta(days=off)).isoformat() if off is not None else None

    def ts(off, hora=10):
        return CAL.iso(datetime.combine(hoje + timedelta(days=off), dtime(hora, 0), CAL.FUSO)) if off is not None else None

    def comp(s):
        if isinstance(s, str) and s.startswith("M-"):
            m = hoje.replace(day=1)
            for _ in range(int(s[2:])):
                m = (m - timedelta(days=1)).replace(day=1)
            return m.strftime("%Y-%m")
        return s

    if limpar:
        for t in TABELAS:
            a = os.path.join(app.repo.pasta, TABELAS[t][0] + ".json") if hasattr(app.repo, "pasta") else None
            if a and os.path.exists(a):
                os.unlink(a)
        os.makedirs(pasta_esteira, exist_ok=True)
        for sub in ("pedidos", "historico"):
            p = os.path.join(pasta_esteira, sub)
            if os.path.isdir(p):
                for n in os.listdir(p):
                    os.unlink(os.path.join(p, n))
    emp = {k: dict(v, cnpj=cnpj_de(v["raiz"])) for k, v in fx["empresas"].items()}
    for p in fx["parceiros"]:
        app.repo.gravar("parceiro", {"chave": p["parceiro_id"], "master_id": None, "situacao": "ativo", "confirmado": True, "cnpj_situacao": "ativa",
                                     "origem_cadastro": "fixture", **{k: v for k, v in p.items() if k != "vigencia"}})
    for u in fx["usuarios"]:
        app.repo.gravar("usuario_parceiro", {"usuario_id": u["usuario_id"], "parceiro_id": u["parceiro_id"], "consultor_parceiro_id": u.get("consultor_parceiro_id"),
                                             "nome": u["nome"], "email": u["email"], "papel": u["papel"], "estado": u["estado"], "entra_oid": None,
                                             "termos_versao": app.param("termos_uso.versao") if u.get("termos") else None,
                                             "termos_aceitos_em": ts(-30) if u.get("termos") else None, "declarou_sem_promessa_em": ts(-30) if u.get("termos") else None})
    for t in fx["termos"]:
        app.repo.gravar("termo", {"termo_id": "T-" + t["parceiro_id"], "parceiro_id": t["parceiro_id"], "percentual_recuperacao": t["percentual_recuperacao"],
                                  "percentual_confirmado": True, "vigencia_ini": d(t.get("vigencia_ini")), "fonte": "fictício (teste)"})
    negs = []
    for n in fx["negocios"]:
        c = emp[n["empresa"]]["cnpj"]
        negs.append({"deal_id": n["deal_id"], "pipeline": n["pipeline"], "etapa": n["etapa"], "status": n["status"], "cnpj_hmac": app.hmac_cnpj(c),
                     "cnpj_raiz_hmac": app.hmac_raiz(c), "cnpj_mascara": app.mascara(c), "parceiro_id": n.get("parceiro_id"), "master_id": n.get("master_id"),
                     "criado_em": d(n.get("criado")), "fechado_em": d(n.get("fechado")), "entrou_etapa_em": ts(n.get("entrou_etapa") if n.get("entrou_etapa") is not None else n.get("criado")),
                     "ultima_atividade_em": ts(n.get("ultima_atividade")), "hs_modificado_em": ts(-1), "valor_credito": n.get("valor_credito"),
                     "honorario_pct": n.get("honorario_pct"), "parceiro_pct_card": n.get("parceiro_pct_card"), "cafe": bool(n.get("cafe")),
                     "empresa_nome": n.get("empresa_nome"), "teses": n.get("teses") or [], "produto": n.get("produto"), "owner_nome": n.get("responsavel"),
                     "uf": n.get("uf"), "porte": n.get("porte"), "segmento": n.get("segmento"), "proximo_passo_crm": n.get("proximo_passo"),
                     "previsao_fechamento_em": d(n.get("previsao")), "ecac_liberado": bool(n.get("ecac")), "tem_parecer": bool(n.get("parecer")),
                     "tem_anexo_diagnostico": bool(n.get("anexo_diagnostico")), "documentos_solicitados": n.get("documentos") or [],
                     "historico_etapas": [{"etapa": x["etapa"], "entrou_em": ts(x["dia"])} for x in n.get("historico") or []],
                     "notas_internas": n.get("notas_internas"), "probabilidade": n.get("probabilidade"), "motivo_perda_interno": n.get("motivo_perda"),
                     "contato_socio": n.get("contato_socio"), "id_bitrix": n.get("id_bitrix"),
                     "outras_comissoes": {"vendedor_pct": 0.03} if n["status"] == "ganho" else None})
    app.repo.carregar_gerado("negocio", negs)
    por_deal = {n["deal_id"]: n for n in negs}
    linhas = []
    for x in fx["extrato_linhas"]:
        n = por_deal[x["deal_id"]]
        linhas.append({"linha_id": "X-%s-REC" % n["deal_id"], "deal_id": n["deal_id"], "parceiro_id": n["parceiro_id"], "master_id": n["master_id"],
                       "competencia": (n["fechado_em"] or "")[:7], "familia": "recuperacao", "estado": x["estado"], "motivo": x.get("motivo"),
                       "percentual": x.get("percentual"), "parceiro_pct_card": n.get("parceiro_pct_card"), "base_recebida": None, "valor_previsto": None,
                       "percentual_origem": "termo"})
    app.repo.carregar_gerado("extrato_linha", linhas)
    for m in fx["movimentos"]:
        lid, est = "X-%s-REC" % m["deal_id"], next(x["estado"] for x in fx["extrato_linhas"] if x["deal_id"] == m["deal_id"])
        for tipo, para, off, val in m["passos"]:
            v = dict(val)
            for k in ("contestacao_ate", "pago_em"):
                if isinstance(v.get(k), int):
                    v[k] = d(v[k])
            if "competencia_recebimento" in v:
                v["competencia_recebimento"] = comp(v["competencia_recebimento"])
            if tipo == "liberacao":
                v["publicado_em"] = ts(off)
            app.repo.inserir("extrato_movimento", {"linha_id": lid, "deal_id": m["deal_id"], "tipo": tipo, "de": est, "para": para, "quando": ts(off, 11),
                                                    "quem": val.get("recebimento_por", "financeiro:outra"), "papel": "financeiro", "valores": v})
            est = para
    regs = {}
    for r in fx["registros"]:
        e = emp[r["empresa"]]; c = e["cnpj"]
        u = app.repo.obter("usuario_parceiro", r["usuario_id"])
        par = app.repo.obter("parceiro", u["parceiro_id"])
        carimbo = ts(r["carimbo"], 10)
        val = app.param("registro.validade_master_dias" if par["tipo"] == "master" else "registro.validade_indicador_dias")
        rid = app.novo_id("R")
        row = {"registro_id": rid, "ref": app.ref(), "chave_idempotencia": None, "parceiro_id": u["parceiro_id"], "usuario_id": u["usuario_id"],
               "master_id": par.get("master_id"), "canal_entrada": "portal", "carimbo_origem": "portal", "cnpj": c, "cnpj_raiz_hmac": app.hmac_raiz(c),
               "cnpj_hmac": app.hmac_cnpj(c), "cnpj_mascara": app.mascara(c), "razao_social": e["nome"], "contato_nome": "Decisor da " + e["nome"].split(" ")[0] + " " + r["empresa"],
               "contato_cargo": "Diretor financeiro", "contato_email": "decisor%s@example.com" % r["empresa"], "contato_tel": None, "interesse": r["interesse"],
               "como_conhece": "cliente_escritorio", "evidencia_tipo": "declaracao", "evidencia_nota": None, "estado": r["estado"],
               "checagem_resultado": r["checagem"], "flags": [], "carimbo": carimbo, "criado_em": carimbo, "prorrogacoes": 0, "dias_pausados": 0, "avisos": [],
               "registrado_por": u["usuario_id"], "origem": "portal", "deal_id": r.get("deal_id"), "vinculo_deal": "automatico" if r.get("deal_id") else None,
               "pode_decidir_em": CAL.iso(app.cal.somar_horas_uteis(CAL.ler(carimbo), app.param("registro.resposta_minima_horas"))),
               "decidir_ate": app.cal.prazo_du(CAL.ler(carimbo), 1).isoformat(), "atualizado_em": ts(r.get("decidido") or r["carimbo"], 15)}
        if r.get("decidido") is not None:
            row.update(decidido_em=ts(r["decidido"], 15), decidido_por="daniela:local", valido_ate=d(r["carimbo"] + val))
        if r.get("encerrado") is not None:
            row["encerrado_em"] = ts(r["encerrado"], 6)
        if r.get("pergunta"):
            row.update(pergunta=r["pergunta"], complemento_ate=app.cal.prazo_du(base + timedelta(days=r["complemento_ate"]), 0).isoformat())
        app.repo.inserir("registro", row)
        app.repo.inserir("registro_evento", {"registro_id": rid, "quando": carimbo, "quem": u["usuario_id"], "papel": u["papel"], "de_estado": None,
                                             "para_estado": "em_analise", "motivo_interno": "checagem=%s (fixture)" % r["checagem"], "motivo_externo": None})
        if r["estado"] != "em_analise":
            app.repo.inserir("registro_evento", {"registro_id": rid, "quando": row["atualizado_em"], "quem": "daniela:local", "papel": "daniela",
                                                 "de_estado": "em_analise", "para_estado": r["estado"], "motivo_interno": "fixture", "motivo_externo": None})
        regs[r["chave"]] = row
        if r["estado"] == "aprovado":
            NT.avisar_registro(app, row, "M-05", valido_ate=CAL.fmt_data(row["valido_ate"]))
    for c in fx["conflitos"]:
        r = regs[c["registro"]]
        cid = app.novo_id("C", 4)
        from . import checagem as CHK
        app.repo.inserir("conflito", {"conflito_id": cid, "cnpj_raiz_hmac": r["cnpj_raiz_hmac"], "cnpj_mascara": r["cnpj_mascara"], "origem": "registro",
                                      "tipo": c["tipo"], "partes": c["partes"], "severidade": c["severidade"], "estado": "aberto", "registros": [r["registro_id"]],
                                      "fatos": CHK.historico_raiz(app, r["cnpj_raiz_hmac"]), "aberto_em": ts(c["aberto"]),
                                      "regra": "Desempate PRM-R31: (1) registro válido mais antigo; (2) quem comprovou primeiro a relação; (3) quem levou à reunião de diagnóstico; (4) decisão do Luis.",
                                      "prazo": app.cal.prazo_du(CAL.ler(ts(c["aberto"])), app.param("registro.sla_conflito_du")).isoformat()})
        app.repo.atualizar("registro", r["registro_id"], {"conflito_id": cid, "pausado_desde": ts(c["aberto"])})
    for p in fx["pendencias"]:
        n = por_deal[p["deal_id"]]
        app.repo.inserir("pendencia", {"pendencia_id": app.novo_id("PD", 5), "deal_id": p["deal_id"], "tipo": p["tipo"], "texto": p["texto"], "aberta_por": "daniela",
                                       "aberta_em": ts(p["aberta"]), "resolvida_em": None, "parceiro_id": n["master_id"], "etapa_na_abertura": n["etapa"]})
    app.avaliador_historico = DM.avaliador_fixture(fx["historico"])
    for dm in fx["demandas"]:
        u = app.repo.obter("usuario_parceiro", dm["usuario_id"])
        from . import catalogo as CAT
        cod = CAT.codigo(dm["tipo"]); t = CAT.tipos().get(cod, {})
        ab = CAL.ler(ts(dm["aberta"], 9))
        emp_ref = None
        if dm.get("empresa_registro"):
            rr = regs[dm["empresa_registro"]]
            emp_ref = {"ref": rr["ref"], "tipo": "registro", "registro_id": rr["registro_id"], "deal_id": rr.get("deal_id"), "nome": rr["razao_social"], "encerrada": False}
        row = {"demanda_id": app.novo_id("D", 4), "ref": app.ref(), "canal": "portal", "origem": "portal-parceiro", "parceiro_id": u["parceiro_id"], "usuario_id": u["usuario_id"],
               "tipo_tela": dm["tipo"], "codigo": cod, "area": CAT.PARCEIRO[dm["tipo"]]["area"], "dono": CAT.PARCEIRO[dm["tipo"]]["dono"], "urgente": False, "validado": False,
               "empresa": emp_ref, "estado": "aberta", "aberta_em": CAL.iso(ab), "primeira_resposta_ate": app.cal.prazo_du(ab, t.get("primeira_resposta_du") or 0).isoformat(),
               "solucao_ate": app.cal.prazo_du(ab, t["solucao_du"]).isoformat() if t.get("solucao_du") is not None else None,
               "mensagens": [{"de": "parceiro", "texto": dm["texto"], "quando": CAL.iso(ab)}], "escala": 0, "reaberturas": 0}
        app.repo.inserir("demanda", row)
        row = DM.triar(app, row)
        if dm.get("resposta"):
            msgs = row["mensagens"] + [{"de": "save", "texto": dm["resposta"], "quando": ts(dm["respondida"], 14), "selo": "Resposta da área %s" % row["area"], "por": "daniela:local"}]
            row = app.repo.atualizar("demanda", row["demanda_id"], {"estado": "respondida", "mensagens": msgs, "respondida_em": ts(dm["respondida"], 14)})
            NT._gravar(app, "usuario:" + u["usuario_id"], "Resposta ao pedido %s" % row["demanda_id"], dm["resposta"], "resposta", "prm", "pedidos/" + row["ref"],
                       chave="resp-fx|" + row["demanda_id"], auditoria="auditado")
    app.repo.carregar_gerado("demanda_unica", [{"demanda_id": x["demanda_id"], "origem": x["origem"], "canal": x["canal"], "estado": x["estado"],
                                                 "parceiro_id": x["parceiro_id"], "tipo_sla": x["tipo_sla"], "aberta_em": ts(x["aberta"])} for x in fx["demanda_unica"]])
    ligar_fontes(fx)
    n_idx = montar_indice(fx, pasta_esteira)
    app.usuarios_teste = set(fx.get("usuarios_login_simulado") or []) or None
    return {"empresas": len(emp), "negocios": len(negs), "registros": len(regs), "indice": n_idx}
