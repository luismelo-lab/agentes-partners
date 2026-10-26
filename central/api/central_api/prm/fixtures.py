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
    fx = ler()
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
                     "honorario_pct": n.get("honorario_pct"), "parceiro_pct_card": n.get("parceiro_pct_card"), "cafe": False})
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
