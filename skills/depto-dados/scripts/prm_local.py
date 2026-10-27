#!/usr/bin/env python3
"""PRM Save · modo local da Fase 1: as mesmas tabelas do Azure SQL (docs/prm/v2/schema.sql) em JSON, em registro/prm/.

Dono: Dados & BI (Engenheiro de Dados do HubSpot). Desenho: docs/prm/v2/03-dados.md, seção 4.
Só leitura no HubSpot: lê o download do dia (departamentos/resultados/dados/hubspot-AAAA-MM-DD.json, rotina "Dados do dia")
e, se existir, o complemento da API do mesmo dia (prm-complemento-AAAA-MM-DD.json, prm_hubspot.py).
Não chama API, não escreve no HubSpot nem no GLPI.

Cada arquivo é uma tabela, com o mesmo nome e as mesmas colunas do esquema SQL, num envelope:
  {"esquema": "prm-local/1", "tabela": "<schema.tabela>", "gerado_em": ..., "fonte": ..., "linhas": [ {...}, ... ]}
Dois tipos de arquivo:
  gerados   (refeitos inteiros a cada rodada, idempotentes: mesma fonte → mesmo conteúdo, salvo gerado_em)
            hs_negocio, parceiro_alias, prm_extrato_linha, prm_demanda, metricas, qualidade, manifesto
  de autoria (nunca sobrescritos; criados vazios ou com a carga inicial só se não existirem)
            prm_parceiro (o gerador só ACRESCENTA parceiro novo, nunca altera nem renumera), prm_termo,
            prm_registro_oportunidade, prm_registro_evento, prm_conflito, prm_usuario_parceiro
CNPJ do cliente: no espelho só a chave HMAC da raiz e do CNPJ (mesmo sal do índice da Central, CENTRAL_SAL) e a máscara
"12.***.***/****-34". Nome da empresa não entra. O CNPJ completo só existe em prm_registro_oportunidade (autoria da Daniela,
no Mac, permissão 600). Pasta 700, arquivos 600, gravação atômica.

Uso:
  prm_local.py gerar  [--fonte hubspot-AAAA-MM-DD.json] [--saida <pasta>] [--hoje AAAA-MM-DD]
  prm_local.py status [--saida <pasta>]        idade e contagens; sai com 1 se o espelho tem mais de 3 dias
  prm_local.py checar-cnpj <cnpj> [--parceiro P-0001] [--saida <pasta>]   validação de entrada do registro (formato, DV, raiz, duplicidade)
"""
import argparse, glob, json, os, statistics, sys, time, unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

AP = os.environ.get("PARTNERS_AP") or os.path.expanduser("~/agentes-partners")
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
BASE = REPO if os.path.isdir(os.path.join(REPO, "central", "api")) else AP
sys.path.insert(0, os.path.join(BASE, "lib")); sys.path.insert(0, os.path.join(BASE, "central", "api"))
from cnpj import cnpj_valido, normalizar_cnpj, raiz_cnpj  # noqa: E402
from central_api import negocio_ativo as NA  # noqa: E402  (chave HMAC e sal únicos com o índice da Central)

ESQUEMA = "prm-local/1"
DADOS = os.path.join(AP, "departamentos/resultados/dados")
MAPA = os.path.join(AP, "departamentos/resultados/mapeamento-hubspot.json")
ALIASES = os.path.join(AP, "departamentos/partner-success/scripts/aliases-parceiros.json")
ENTRADAS = os.path.join(AP, "departamentos/partner-success/scripts/datas-entrada-parceiros.json")
PERCENT = os.path.join(AP, "departamentos/operacoes-canal/percentual-parceiros.json")
DEMANDAS = os.path.join(AP, "registro/demandas.json")
SAIDA = os.path.join(AP, "registro/prm")
INVALIDOS = {"", "0", "00", "50", "-", "NA", "N/A"}  # config-canal.json → parceiro_invalido
IDADE_MAX = 3

# Etapa do HubSpot → estado do parceiro (7 estados do M3). Proposta da fase 0 (decisão do Luis); igual a ref.etapa_estado no SQL.
ESTADO_ETAPA = {
    "Novo Negócio": 1, "Lead Novo - Prospecção": 1, "Agendamento": 1, "Em Contato": 1, "Contato Futuro": 1, "Follow - Up": 1,
    "Em Diagnóstico": 2, "Análise de Documentos": 2, "Estudo Inicial": 2, "Autorização Equipe Senior LR": 2,
    "Análise com Pendência": 3, "Documentação Pendente": 3,
    "Apresentação de Diagnóstico": 4, "Em Apresentação": 4,
    "Negociação": 5, "Contrato Enviado": 5, "Pendência Fechamento": 5, "Contrato Assinado": 5,
    # etapas que apareceram na linha do tempo real (API, 27/10/2026); mesma proposta, a Daniela valida
    "Abordagem": 1, "Follow up": 1, "Reentrada": 1, "Em andamento": 1, "Funil de Aplicação": 1, "Funil de Aquisição": 1, "Funil Outbound": 1, "Aguardando Diagnóstico": 2, "Diagnóstico em Construção": 2, "Autorização - Gestor": 2, "Pendência da Automação": 2, "Pendência de Documentos": 3, "Aguardado E-CAC": 3, "Elaboração de Contrato": 5, "Contrato enviado": 5, "Análise jurídica": 5,
}
ESTADOS = {1: "Recebido", 2: "Em diagnóstico", 3: "Precisa de algo de você", 4: "Apresentação marcada",
           5: "Contrato em andamento", 6: "Em execução", 7: "Encerrado"}


def norm(s):
    return " ".join(unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().upper().split())


def ler(p, padrao=None):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return padrao


def gravar(pasta, nome, tabela, linhas, fonte, extra=None):
    os.makedirs(pasta, exist_ok=True); os.chmod(pasta, 0o700)
    p = os.path.join(pasta, nome + ".json"); tmp = "%s.%d.tmp" % (p, os.getpid())
    env = {"esquema": ESQUEMA, "tabela": tabela, "gerado_em": time.strftime("%Y-%m-%dT%H:%M:%S"), "fonte": fonte, **(extra or {}), "linhas": linhas}
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(env, f, ensure_ascii=False, indent=1, default=str); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, p)
    return len(linhas)


def autoria(pasta, nome, tabela, carga=None):
    """Arquivo de autoria: se existe, devolve as linhas; se não, cria com a carga inicial."""
    p = os.path.join(pasta, nome + ".json"); d = ler(p)
    if isinstance(d, dict) and isinstance(d.get("linhas"), list):
        return d["linhas"], False
    gravar(pasta, nome, tabela, carga or [], "carga inicial (prm_local.py)")
    return carga or [], True


def mascara(c):
    c = normalizar_cnpj(c)
    return "%s.***.***/****-%s" % (c[:2], c[-2:]) if len(c) == 14 else None


def dia(s):
    try:
        return date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


def cafe(d, regras, nome_neg):
    """Regra do Luis (20/08/2026): café fora da meta desde abr/2026 (ganho = mês de fechamento; aberto = mês de criação)."""
    ref = d.get("fechado") if d.get("status") == "ganho" else d.get("criado")
    if not ref or str(ref)[:7] < regras.get("excluir_cafe_desde", "9999"):
        return False
    t = norm(" ".join([nome_neg or "", d.get("segmento") or ""])).lower()
    return str(d.get("cnae") or "").replace("-", "").replace("/", "") in set(regras.get("cafe_cnae", [])) or \
        any(norm(p).lower() in t for p in regras.get("cafe_palavras", []))


def pct(xs, q):
    xs = sorted(xs)
    if not xs: return None
    k = (len(xs) - 1) * q; i = int(k)
    return round(xs[i] + (xs[min(i + 1, len(xs) - 1)] - xs[i]) * (k - i), 1)


# ---------------------------------------------------------------- parceiros
def parceiros(pasta, negocios, mapa, aliases):
    """prm_parceiro (autoria, só acrescenta) + parceiro_alias (gerado). Masters do roster; consultores = alias em caixa mista
    do roster (heurística, a Daniela confirma); indicadores = nomes fora do roster normalizados pelos aliases."""
    roster = (mapa.get("escopo") or {}).get("parceiros_roster") or {}
    atuais, novo_arquivo = autoria(pasta, "prm_parceiro", "prm.parceiro")
    por_chave = {p["chave"]: p for p in atuais}
    seq = max([int(p["parceiro_id"].split("-")[1]) for p in atuais] or [0])
    hoje = time.strftime("%Y-%m-%d")

    def garantir(chave, nome, tipo, master=None, origem="roster"):
        nonlocal seq
        if chave in por_chave:
            return por_chave[chave]["parceiro_id"]
        seq += 1
        p = {"parceiro_id": "P-%04d" % seq, "chave": chave, "nome_exibicao": nome, "tipo": tipo, "master_id": master,
             "cnpj_parceiro": None, "data_entrada": None, "data_entrada_origem": None, "nivel_atual": None, "situacao": "ativo",
             "origem_cadastro": origem, "confirmado": False, "criado_em": hoje}
        atuais.append(p); por_chave[chave] = p
        return p["parceiro_id"]

    alias_linhas, consultor_alias = [], []
    for canon, als in roster.items():
        mid = garantir("M|" + norm(canon), canon, "master")
        for a in als:
            if a.isupper() or norm(a) == norm(canon):
                alias_linhas.append({"alias_norm": norm(a), "parceiro_id": mid, "origem": "roster"})
            else:
                cid = garantir("C|" + norm(a), a, "consultor", mid, "roster_heuristica")
                alias_linhas.append({"alias_norm": norm(a), "parceiro_id": cid, "origem": "roster_heuristica"})
                consultor_alias.append((norm(a), cid))
    consultor_alias.sort(key=lambda t: -len(t[0]))
    al = (aliases or {}).get("aliases") or {}
    entradas = ((ler(ENTRADAS, {}) or {}).get("datas")) or {}

    def do_negocio(d):
        bruto = norm(d.get("parceiro_bruto"))
        if d.get("parceiro") and not str(d["parceiro"]).startswith("Outros"):
            mid = por_chave["M|" + norm(d["parceiro"])]["parceiro_id"]
            for a, cid in consultor_alias:
                if a and a in bruto:
                    return cid, mid
            return mid, mid
        if bruto in INVALIDOS or bruto.isdigit():
            return None, None
        canon = norm(al.get(bruto) or bruto)
        pid = garantir("I|" + canon, al.get(bruto) or d.get("parceiro_bruto").strip(), "indicador", None, "hubspot_texto_livre")
        alias_linhas.append({"alias_norm": bruto, "parceiro_id": pid, "origem": "aliases-parceiros" if bruto in al else "texto_livre"})
        return pid, None

    vinculo = {d["id"]: do_negocio(d) for d in negocios}
    for p in atuais:  # data de entrada informada (datas-entrada-parceiros.json); nunca apaga o que a Daniela gravou
        v = entradas.get(p["nome_exibicao"]) if isinstance(entradas, dict) else None
        if v and not p.get("data_entrada"):
            p["data_entrada"], p["data_entrada_origem"] = v, "informada"
    gravar(pasta, "prm_parceiro", "prm.parceiro", atuais, "autoria + acréscimos do prm_local.py")
    vistos, unicos = set(), []
    for a in alias_linhas:
        if a["alias_norm"] not in vistos:
            vistos.add(a["alias_norm"]); unicos.append(a)
    gravar(pasta, "parceiro_alias", "prm.parceiro_alias", unicos, MAPA)
    return atuais, vinculo, novo_arquivo


# ---------------------------------------------------------------- espelho do HubSpot
def espelho(negocios, vinculo, regras):
    linhas = []
    for d in negocios:
        ex = d.get("extras") or {}
        c = normalizar_cnpj(ex.get("cnpj")); ok = bool(c) and cnpj_valido(c)
        r = raiz_cnpj(c) if ok else None
        st = d.get("status")
        estado = 6 if st == "ganho" else 7 if st == "perdido" else ESTADO_ETAPA.get(d.get("etapa"), 1)
        # e-CAC: só 285 de 5.051 negócios têm o campo preenchido; "em diagnóstico sem e-CAC → precisa de algo de você"
        # entra quando o campo virar obrigatório na etapa (03-dados.md, seção 2.3). Até lá, só a etapa decide.
        criado, fechado = dia(d.get("criado")), dia(d.get("fechado"))
        efetiva = min([x for x in (criado, fechado if st != "aberto" else None) if x] or [None])
        pid, mid = vinculo.get(d["id"], (None, None))
        linhas.append({
            "deal_id": d["id"], "pipeline": d.get("pipeline"), "etapa": d.get("etapa"), "status": st,
            "estado_parceiro": ESTADOS[estado], "estado_parceiro_ordem": estado,
            "cnpj_hmac": NA.chave(c) if ok else None, "cnpj_raiz_hmac": NA.chave(r) if r else None,
            "cnpj_mascara": mascara(c) if ok else None, "cnpj_situacao": "valido" if ok else ("vazio" if not c else "invalido"),
            "parceiro_id": pid, "master_id": mid, "parceiro_bruto_norm": norm(d.get("parceiro_bruto")) or None,
            "owner_id": d.get("owner"), "valor_credito": d.get("valor"), "honorario_pct": d.get("hContr"), "parceiro_pct_card": d.get("hParc"),
            "outras_comissoes": d.get("outras_comissoes"), "teses": d.get("variante"), "recebido": d.get("recebido"),
            "uf": ex.get("uf"), "regime": ex.get("regime"), "porte": ex.get("porte"), "cnae": d.get("cnae"),
            "criado_em": str(criado) if criado else None, "fechado_em": str(fechado) if fechado else None, "data_efetiva": str(efetiva) if efetiva else None,
            "entrou_etapa_em": ex.get("entrou_etapa"), "ultima_atividade_em": ex.get("ultima_atividade"), "hs_modificado_em": ex.get("ultima_modificacao"),
            "ecac_liberado": str(ex.get("ecac")).lower() == "true", "tem_parecer": bool(ex.get("parecer_rt")), "id_bitrix": ex.get("id_bitrix"),
            "importado": str(ex.get("importado")).lower() == "true", "indicado_por_email_preenchido": bool(ex.get("indicado_por_email")),
            "cafe": cafe(d, regras, d.get("nome")),
            # acompanhamento de negócios do parceiro (PRM-R113+, 26/10/2026). Nome da empresa e dado de sócio NÃO entram no JSON local.
            "produto": ex.get("produto"), "segmento": d.get("segmento"), "owner_nome": ex.get("owner_nome"),
            "previsao_fechamento_em": str(fechado) if (st == "aberto" and fechado) else None,
            "proximo_passo_crm": ex.get("proximo_passo"), "tem_anexo_diagnostico": bool(ex.get("anexo_diagnostico")),
            "historico_etapas": [{"etapa": h.get("etapa"), "entrou_em": h.get("entrou_em")} for h in (ex.get("historico_etapas") or []) if isinstance(h, dict) and h.get("etapa")],
            "probabilidade": d.get("prob"), "motivo_perda_interno": ex.get("motivo_perda"),
            "proximo_passo_crm_em": ex.get("proximo_passo_em"), "pendencia_crm_interna": ex.get("pendencia") or ex.get("pendencia_fechamento"),
        })
    return linhas


# ---------------------------------------------------------------- extrato (só previsto / em conferência até existir o recebido)
def extrato(neg, termos):
    pct_termo = {t["parceiro_id"]: t for t in termos if t.get("percentual_recuperacao") is not None}
    chave = Counter((n["cnpj_hmac"], round(n["valor_credito"] or 0)) for n in neg if n["status"] == "ganho" and n["cnpj_hmac"] and (n["valor_credito"] or 0) > 0)
    linhas = []
    for n in neg:
        if n["status"] != "ganho" or not n["parceiro_id"]:
            continue
        termo = pct_termo.get(n["master_id"] or n["parceiro_id"])
        motivos = []
        if n["honorario_pct"] is None: motivos.append("C01 % honorário vazio")
        if n["parceiro_pct_card"] is None and not termo: motivos.append("C02 % parceiro vazio e sem termo")
        if (n["parceiro_pct_card"] or 0) > 1: motivos.append("O03 % parceiro acima de 100%")
        if (n["valor_credito"] or 0) <= 0: motivos.append("O05 crédito zero")
        if n["cnpj_hmac"] and chave[(n["cnpj_hmac"], round(n["valor_credito"] or 0))] > 1: motivos.append("I05 possível duplicidade")
        if termo and n["parceiro_pct_card"] is not None and abs(termo["percentual_recuperacao"] - n["parceiro_pct_card"]) > 0.001:
            motivos.append("% do card diverge do termo")
        p = termo["percentual_recuperacao"] if termo else n["parceiro_pct_card"]
        base = (n["valor_credito"] or 0) * n["honorario_pct"] if n["honorario_pct"] is not None else None
        conferencia = bool(motivos)
        linhas.append({"linha_id": "X-%s-%s" % (n["deal_id"], "REC"), "deal_id": n["deal_id"], "parceiro_id": n["parceiro_id"],
                       "competencia": (n["fechado_em"] or "")[:7] or None, "familia": "recuperacao",
                       "estado": "em_conferencia" if conferencia else "previsto", "motivo": "; ".join(motivos) or None,
                       "base_contratada": None if conferencia else round(base, 2) if base is not None else None,
                       "base_recebida": None, "percentual": None if conferencia else p,
                       "valor_previsto": None if conferencia or base is None or p is None else round(base * p, 2),
                       "valor_bruto": None, "retencoes": None, "valor_liquido": None, "nf_numero": None, "pago_em": None,
                       "percentual_origem": "termo" if termo else "card"})
    return linhas


# ---------------------------------------------------------------- demandas (visão do registro único lib/registro_demandas.py)
def demandas(parc):
    R = (ler(DEMANDAS, {}) or {}).get("demandas") or {}
    por_nome = {norm(p["nome_exibicao"]): p["parceiro_id"] for p in parc if p["tipo"] == "master"}
    out = []
    for d in (R.values() if isinstance(R, dict) else R):
        ab = d.get("aberta_em"); fim = d.get("resolvida_em")
        prazo = None
        if d.get("prazo") and ab and len(str(d["prazo"])) == 5:
            try:
                prazo = date(int(ab[:4]), int(d["prazo"][3:5]), int(d["prazo"][:2])).isoformat()
            except ValueError:
                prazo = None
        horas = None
        if ab and fim:
            try:
                horas = round((datetime.fromisoformat(fim[:16]) - datetime.fromisoformat(ab[:16])).total_seconds() / 3600, 1)
            except ValueError:
                pass
        out.append({"demanda_id": d.get("id"), "origem": d.get("origem"), "canal": "portal" if d.get("origem") == "portal" else
                    "whatsapp" if d.get("origem") == "WhatsApp" else "email", "dona": d.get("pessoa"),
                    "parceiro_id": por_nome.get(norm(d.get("master"))), "deal_id": d.get("negocio") if str(d.get("negocio") or "").isdigit() else None,
                    "tipo_sla": d.get("tipo"), "estado": d.get("status"), "via": "chamado" if d.get("chamado") else None,
                    "aberta_em": ab, "prazo_em": prazo, "resolvida_em": fim, "horas_ate_resolver": horas,
                    "aguardando_h": d.get("aguardando_h"), "urgente": bool(d.get("urgente"))})
    return out


# ---------------------------------------------------------------- métricas (definições em 03-dados.md, seção 5)
def metricas(neg, parc, regs, dem, ext, hoje):
    tipo = {p["parceiro_id"]: p["tipo"] for p in parc}
    entrada = {p["parceiro_id"]: p.get("data_entrada") for p in parc}
    por = defaultdict(list)  # Master conta tudo do escritório (dele e dos consultores); consultor e indicador, só o próprio
    for n in neg:
        if n["cafe"]:
            continue
        if n["parceiro_id"]:
            por[n["parceiro_id"]].append(n)
        if n["master_id"] and n["master_id"] != n["parceiro_id"]:
            por[n["master_id"]].append(n)
    classes = defaultdict(Counter); t1 = []
    for pid, L in por.items():
        efet = [dia(n["data_efetiva"]) for n in L if n["data_efetiva"]]
        ativo = any(e and (hoje - e).days <= 90 for e in efet)
        g12 = [n for n in L if n["status"] == "ganho" and n["fechado_em"] and (hoje - dia(n["fechado_em"])).days <= 365]
        classes[tipo.get(pid)]["ativo_produtivo" if ativo and g12 else "ativo_rampa" if ativo else "dormente" if g12 else "inativo"] += 1
        ganhos = sorted(dia(n["fechado_em"]) for n in L if n["status"] == "ganho" and n["fechado_em"])
        ini = dia(entrada.get(pid))  # PRM: só mede quem tem data de entrada registrada (sem ela o número mede a base, não o onboarding)
        if ganhos and ini and ganhos[0] >= ini:
            t1.append((ganhos[0] - ini).days)
    ativ = {k: dict(v) for k, v in classes.items()}
    for k, v in ativ.items():
        tot = sum(v.values()); v["total"] = tot
        v["taxa_ativacao_pct"] = round(100 * (v.get("ativo_produtivo", 0) + v.get("ativo_rampa", 0)) / tot, 1) if tot else None
    # concentração: valor de crédito ganho em 12 meses por Master (sem café)
    val = Counter()  # mesmo grão do calc_semana.py (concentracao_12m): Master do roster; o resto num balde só
    for n in neg:
        if n["status"] == "ganho" and not n["cafe"] and n["fechado_em"] and (hoje - dia(n["fechado_em"])).days <= 365:
            val[n["master_id"] or "fora_do_roster"] += n["valor_credito"] or 0
    tot = sum(val.values()); top = [v for _, v in val.most_common()]
    # conflitos: raiz com mais de um parceiro (aberto ou ganho)
    raiz = defaultdict(set); raiz_m = defaultdict(set)
    for n in neg:
        if n["status"] in ("aberto", "ganho") and n["cnpj_raiz_hmac"]:
            raiz[n["cnpj_raiz_hmac"]].add(n["master_id"] or n["parceiro_id"] or "sem_parceiro")  # canal = escritório (como conflito_canal.py)
            if n["master_id"]: raiz_m[n["cnpj_raiz_hmac"]].add(n["master_id"])
    # conversão registrado × não registrado (coorte fechada: ganho / (ganho + perdido))
    reg_deals = {r["deal_id"] for r in regs if r.get("deal_id") and r.get("estado") in ("convertido", "aprovado")}
    conv = {}
    for grupo, filtro in (("registrado", lambda n: n["deal_id"] in reg_deals), ("nao_registrado", lambda n: n["deal_id"] not in reg_deals and n["parceiro_id"])):
        fech = [n for n in neg if filtro(n) and n["status"] in ("ganho", "perdido") and n["criado_em"] and (hoje - dia(n["criado_em"])).days <= 365]
        g = sum(1 for n in fech if n["status"] == "ganho")
        conv[grupo] = {"fechados_n": len(fech), "ganhos_n": g, "win_rate_pct": round(100 * g / len(fech), 1) if len(fech) >= 20 else None}
    # SLA de demandas
    res = [d for d in dem if d["horas_ate_resolver"] is not None]
    com_prazo = [d for d in res if d["prazo_em"]]
    no_prazo = sum(1 for d in com_prazo if d["resolvida_em"][:10] <= d["prazo_em"])
    abertas = [d for d in dem if d["estado"] in ("responder", "acompanhar", "em_analise", "aguardando_aprovacao")]
    return {
        "referencia": str(hoje),
        "ativacao": ativ,
        "dormentes": {k: v.get("dormente", 0) for k, v in ativ.items()},
        "tempo_ate_1o_ganho_dias": {"n": len(t1), "mediana": statistics.median(t1) if t1 else None, "p75": pct(t1, 0.75),
                                    "regra": "só parceiro com data_entrada; n < 5 = base pequena"},
        "conversao_registrado_x_nao": conv,
        "sla_demandas": {"total": len(dem), "abertas": len(abertas), "resolvidas": len(res),
                         "horas_ate_resolver_p50": pct([d["horas_ate_resolver"] for d in res], 0.5),
                         "horas_ate_resolver_p90": pct([d["horas_ate_resolver"] for d in res], 0.9),
                         "no_prazo_pct": round(100 * no_prazo / len(com_prazo), 1) if com_prazo else None, "com_prazo_n": len(com_prazo),
                         "com_tipo_sla_n": sum(1 for d in dem if d["tipo_sla"]),
                         "pelo_portal_pct": round(100 * sum(1 for d in dem if d["canal"] == "portal") / len(dem), 1) if dem else None},
        "conflitos": {"raizes_ativas": len(raiz), "raizes_mais_de_um_canal": sum(1 for v in raiz.values() if len(v) > 1),
                      "master_x_master": sum(1 for v in raiz_m.values() if len(v) > 1),
                      "registros_em_conflito": sum(1 for r in regs if r.get("estado") == "em_conflito")},
        "concentracao": {"masters_com_ganho_12m": len([k for k in val if k != "fora_do_roster"]), "top1_pct": round(100 * top[0] / tot, 1) if tot else None,
                         "top5_pct": round(100 * sum(top[:5]) / tot, 1) if tot else None},
        "extrato_pendente": {"linhas": len(ext), "previsto_n": sum(1 for e in ext if e["estado"] == "previsto"),
                             "em_conferencia_n": sum(1 for e in ext if e["estado"] == "em_conferencia"),
                             "valor_previsto": round(sum(e["valor_previsto"] or 0 for e in ext), 2),
                             "com_recebido_n": sum(1 for e in ext if e["base_recebida"] is not None)},
    }


def qualidade(neg, parc):
    g = [n for n in neg if n["status"] == "ganho"]
    ativos = [n for n in neg if n["status"] in ("aberto", "ganho")]
    dup = Counter((n["cnpj_raiz_hmac"], n["pipeline"]) for n in neg if n["status"] == "aberto" and n["cnpj_raiz_hmac"])
    dg = Counter((n["cnpj_hmac"], round(n["valor_credito"] or 0)) for n in g if n["cnpj_hmac"] and (n["valor_credito"] or 0) > 0)
    return {
        "negocios": len(neg), "ganhos": len(g),
        "cnpj": dict(Counter(n["cnpj_situacao"] for n in neg)), "raizes_distintas": len({n["cnpj_raiz_hmac"] for n in neg if n["cnpj_raiz_hmac"]}),
        "raizes_ativas": len({n["cnpj_raiz_hmac"] for n in ativos if n["cnpj_raiz_hmac"]}),
        "abertos_duplicados_raiz_pipeline": {"grupos": sum(1 for v in dup.values() if v > 1), "negocios": sum(v for v in dup.values() if v > 1)},
        "ganhos_mesmo_cnpj_e_valor": {"grupos": sum(1 for v in dg.values() if v > 1), "negocios": sum(v for v in dg.values() if v > 1)},
        "ganhos_sem_honorario_pct": sum(1 for n in g if n["honorario_pct"] is None),
        "ganhos_sem_parceiro_pct_com_parceiro": sum(1 for n in g if n["parceiro_id"] and n["parceiro_pct_card"] is None),
        "ganhos_parceiro_pct_acima_100": sum(1 for n in g if (n["parceiro_pct_card"] or 0) > 1),
        "ganhos_sem_recebido": sum(1 for n in g if n["recebido"] is None),
        "ganhos_sem_tese": sum(1 for n in g if not n["teses"]),
        "ganhos_sem_parceiro": sum(1 for n in g if not n["parceiro_id"]),
        "ganhos_indicado_por_preenchido": sum(1 for n in g if n["indicado_por_email_preenchido"]),
        "ganhos_importados": sum(1 for n in g if n["importado"]),
        "parceiros": dict(Counter(p["tipo"] for p in parc)), "parceiros_sem_data_entrada": sum(1 for p in parc if not p.get("data_entrada")),
        "parceiros_nao_confirmados": sum(1 for p in parc if not p.get("confirmado")),
    }


def complementar(negocios, fonte):
    """Junta aos `extras` o complemento da API (prm_hubspot.py, mesmo dia do download): datas por etapa, próximo passo,
    motivo da perda e responsável. Sem o arquivo, o espelho sai como antes (só entrada e etapa atual)."""
    p = os.path.join(os.path.dirname(fonte), os.path.basename(fonte).replace("hubspot-", "prm-complemento-", 1))
    C = (ler(p, {}) or {}).get("negocios") or {}
    for d in negocios:
        if C.get(d["id"]):
            d["extras"] = {**(d.get("extras") or {}), **C[d["id"]]}
    return os.path.basename(p) if C else None


def gerar(a):
    fonte = a.fonte or (sorted(glob.glob(os.path.join(DADOS, "hubspot-*.json"))) or [None])[-1]
    if not fonte: sys.exit("Sem download do HubSpot: rode `partners hubspot`.")
    D = ler(fonte); mapa = ler(MAPA, {}); negocios = D["negocios"]
    comp = complementar(negocios, fonte)
    hoje = date.fromisoformat(a.hoje) if a.hoje else dia(D.get("baixado_em")) or date.today()
    pasta = a.saida
    parc, vinc, _ = parceiros(pasta, negocios, mapa, ler(ALIASES, {}))
    neg = espelho(negocios, vinc, mapa.get("regras") or {})
    carga_termo = []
    pc = (ler(PERCENT, {}) or {}).get("parceiros") or {}
    for p in parc:
        t = pc.get(p["nome_exibicao"]) if p["tipo"] == "master" else None
        if t:
            carga_termo.append({"termo_id": "T-" + p["parceiro_id"], "parceiro_id": p["parceiro_id"], "tipo_relacao": None,
                                "percentual_recuperacao": (t.get("pct_parceiro") or 0) / 100 if t.get("pct_parceiro") is not None else None,
                                "percentual_confirmado": bool(t.get("confirmado")), "regra_produtos_2027": "10_liquido_save",
                                "vigencia_ini": None, "vigencia_fim": None, "arquivo_ref": None, "fonte": "percentual-parceiros.json"})
    termos, _ = autoria(pasta, "prm_termo", "prm.termo", carga_termo)
    regs, _ = autoria(pasta, "prm_registro_oportunidade", "prm.registro_oportunidade")
    for nome, tab in (("prm_registro_evento", "prm.registro_evento"), ("prm_conflito", "prm.conflito"), ("prm_usuario_parceiro", "prm.usuario_parceiro")):
        autoria(pasta, nome, tab)
    ext = extrato(neg, termos)
    dem = demandas(parc)
    M = metricas(neg, parc, regs, dem, ext, hoje); Q = qualidade(neg, parc)
    f = os.path.basename(fonte)
    cont = {"hs_negocio": gravar(pasta, "hs_negocio", "hs.negocio", neg, f, {"hs_baixado_em": D.get("baixado_em")}),
            "prm_extrato_linha": gravar(pasta, "prm_extrato_linha", "prm.extrato_linha", ext, f),
            "prm_demanda": gravar(pasta, "prm_demanda", "prm.demanda", dem, DEMANDAS),
            "prm_parceiro": len(parc), "prm_termo": len(termos), "prm_registro_oportunidade": len(regs)}
    gravar(pasta, "metricas", "prm.vw_metricas", [M], f)
    gravar(pasta, "qualidade", "ops.qualidade_execucao", [Q], f)
    gravar(pasta, "manifesto", "ops.sync_execucao", [{"fonte": f, "complemento_api": comp, "hs_baixado_em": D.get("baixado_em"), "referencia": str(hoje),
                                                      "modo": "total", "contagens": cont, "resultado": "ok"}], "prm_local.py gerar")
    print(json.dumps({"saida": pasta, **cont, "complemento_api": comp, "conflitos": M["conflitos"], "extrato": M["extrato_pendente"]}, ensure_ascii=False))


def status(a):
    m = ler(os.path.join(a.saida, "manifesto.json"))
    if not m: print("registro/prm sem manifesto: rode `prm_local.py gerar`"); sys.exit(1)
    r = m["linhas"][0]; ref = dia(r.get("hs_baixado_em")); idade = (date.today() - ref).days if ref else None
    print("espelho de %s (%s dia(s)); contagens: %s" % (r.get("hs_baixado_em"), idade, r.get("contagens")))
    sys.exit(1 if idade is None or idade > IDADE_MAX else 0)


def checar_cnpj(a):
    """Validação de entrada do registro (seção 6 do 03-dados.md). Não diz ao parceiro se a empresa é cliente."""
    c = normalizar_cnpj(a.cnpj); out = {"normalizado_tamanho": len(c)}
    if len(c) != 14 or not cnpj_valido(c):
        out.update(resultado="recusa_formato", motivo="CNPJ com 14 posições e dígito verificador válido (aceita alfanumérico)"); print(json.dumps(out, ensure_ascii=False)); return
    r = raiz_cnpj(c); kr = NA.chave(r)
    regs = (ler(os.path.join(a.saida, "prm_registro_oportunidade.json"), {}) or {}).get("linhas") or []
    neg = (ler(os.path.join(a.saida, "hs_negocio.json"), {}) or {}).get("linhas") or []
    vivos = [x for x in regs if x.get("cnpj_raiz_hmac") == kr and x.get("estado") in ("recebido", "aprovado", "em_conflito")]
    ativos = [x for x in neg if x.get("cnpj_raiz_hmac") == kr and x.get("status") in ("aberto", "ganho")]
    meus = bool(vivos) and bool(a.parceiro) and all(x.get("parceiro_id") == a.parceiro for x in vivos) and not ativos
    res = "livre" if not vivos and not ativos else "ja_registrado_por_voce" if meus else "em_analise_area_partners"
    # o que vai ao parceiro: só o resultado (3 estados). As contagens abaixo são da visão Save (fila de registros).
    out.update(raiz_mascara=r[:2] + "******", registros_vivos_na_raiz=len(vivos), negocios_ativos_na_raiz=len(ativos), resultado=res,
               mensagem_ao_parceiro=NA.MSG_NEUTRA if res == "em_analise_area_partners" else None)
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gerar"); g.add_argument("--fonte"); g.add_argument("--saida", default=SAIDA); g.add_argument("--hoje")
    s = sub.add_parser("status"); s.add_argument("--saida", default=SAIDA)
    c = sub.add_parser("checar-cnpj"); c.add_argument("cnpj"); c.add_argument("--parceiro"); c.add_argument("--saida", default=SAIDA)
    a = ap.parse_args()
    {"gerar": gerar, "status": status, "checar-cnpj": checar_cnpj}[a.cmd](a)
