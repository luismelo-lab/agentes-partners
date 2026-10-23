#!/usr/bin/env python3
"""Operação contínua da Área Partners: sentinelas → eventos → executores → plano do dia → supervisor. Sem IA, sem tokens.

Sentinelas (comparam o download do HubSpot de hoje com o histórico e com os registros dos agentes):
  contrato_parado       Contrato Enviado / Pendência Fechamento há 5+ dias              → Daniela (Contratos)
  entrou_diagnostico    negócio que entrou em Apresentação de Diagnóstico              → Geovana (Revisor roda sozinho)
  conflito_novo         negócio novo com a mesma raiz de CNPJ de outro canal            → Daniela + Luis (Operações de Canal)
  crm_incompleto        aberto sem CNPJ válido, sem regime ou com CNPJ não ativo na Receita → Daniela (Dados)
  comercial_parado      Agendamento / Em Contato / Negociação / Follow-up sem mexer há 15+ dias → Jenifer (BDR/Closer) ou Daniela
  diagnostico_parado    Em Diagnóstico / Análise de Documentos / Pendência sem mexer há 15+ dias → Geovana
  apresentacao_parada   Apresentação de Diagnóstico sem mexer há 30+ dias              → Daniela
  parceiro_inativo      Master com negócio nos últimos 12 meses e nenhum novo há 60+ dias → Daniela (Partner Success)
  demanda_atrasada      demanda do WhatsApp esperando além do prazo                    → dona da demanda (Supervisor)
  aprovacao_parada      chamado proposto ou pedido da Central esperando decisão há 24h+ → quem decide (Supervisor)
  rotina_falhou         rotina do terminal com erro hoje                               → Luis (TI)
  ganho_sem_execucao    ganho no HubSpot há 7+ dias sem card de execução no Bitrix      → Daniela (Pós-venda)
  execucao_parada       execução em fase ativa no Bitrix há 30+ dias                    → Daniela (Pós-venda; cobrar o técnico)
  prazo_receita         despacho, intimação ou comunicado da Receita nas demandas         → Daniela (Jurídico · Controle de Prazos)
  repasse_bloqueado     Master com ganhos de repasse bloqueado na conferência semanal   → Luis (Operações de Canal)

Áreas (regra do Luis, 15/10: usar 100% dos agentes; infra/padrao-entrega.md): `para-areas` gera registro/para-areas.json com
cada evento sem análise recente e a área dona (AREA). A rotina com IA "operacao-areas" (7h40) passa cada grupo ao agente da área,
que devolve os 3 blocos (o que fazer · o que também precisa · o que falta e quem fornece) e o rascunho; `gravar-analises` guarda em
registro/analises-areas.json e o plano usa esse texto. Sem análise, o plano mostra só a situação (nada de texto fixo ao parceiro).

Executores encadeados (agente → agente, sem aprovação, decisão D26 do Luis em 01/10/2026):
  entrou_diagnostico → Revisor de Diagnóstico nos negócios novos (segunda opinião no mesmo dia)
  contrato_parado    → o rascunho ao parceiro agora vem da área de Contratos (operacao-areas), auditado pela Qualidade
  crm_incompleto     → cadastro oficial da Receita ao lado, para a correção já sair pronta
Continua proibido sem pessoa: falar com parceiro ou cliente, alterar HubSpot ou GLPI, abrir chamado.

Uso:
  operacao.py sentinelas            atualiza registro/eventos.json e roda os executores
  operacao.py plano [--previa]      e-mail do plano do dia para cada pessoa (e o resumo do supervisor para o Luis)
  operacao.py avisos                só os eventos novos e urgentes desde a última rodada (rodada da tarde)
  operacao.py resumo                imprime o quadro de eventos ativos
  operacao.py para-areas            eventos que pedem análise da área (registro/para-areas.json)
  operacao.py gravar-analises <arq> grava as análises das áreas (lista de {chave, area, fazer, precisa, falta, rascunho})
"""
import argparse, glob, json, os, re, subprocess, sys, tempfile
from collections import defaultdict
from datetime import date, datetime, timedelta

AP = os.path.expanduser("~/agentes-partners"); SK = os.path.expanduser("~/.claude/skills")
DADOS = os.path.join(AP, "departamentos/resultados/dados")
REG = os.environ.get("OPERACAO_REG") or os.path.join(AP, "registro")  # OPERACAO_REG/OPERACAO_HOJE: só para simulação
EVT = os.path.join(REG, "eventos.json"); ETP = os.path.join(REG, "etapas.json")
sys.path.insert(0, os.path.join(AP, "lib")); sys.path.insert(0, os.path.join(SK, "depto-marketing/scripts"))
import partners_dados as PD  # noqa: E402

HOJE = date.fromisoformat(os.environ["OPERACAO_HOJE"]) if os.environ.get("OPERACAO_HOJE") else date.today()
LINK = "https://app.hubspot.com/contacts/47865021/deal/{}"
PESSOAS = {"daniela": ("Daniela", "daniela.maciel@savecompany.com.br"), "jenifer": ("Jenifer", "jenifer.carvalho@savecompany.com.br"),
           "geovana": ("Geovana", "geovana.goncalves@savecompany.com.br"), "luis": ("Luis", "luis.melo@savecompany.com.br")}
LIM = {"contrato": 5, "assinado": 3, "comercial": 15, "contato_futuro": 60, "diagnostico": 15, "apresentacao": 30,
       "aprovacao_h": 24, "aprovacao_escala_h": 120, "entrou_dias": 7, "ganho_sem_bitrix": (7, 60)}
ET_CONTRATO = {"Contrato Enviado", "Pendência Fechamento"}
ET_COMERCIAL = {"Agendamento", "Em Contato", "Negociação", "Follow - Up", "Novo Negócio", "Contato Futuro", "Lead Novo - Prospecção"}
ET_DIAG = {"Em Diagnóstico", "Análise de Documentos", "Análise com Pendência", "Documentação Pendente", "Estudo Inicial",
           "Autorização - Gestor", "Autorização Equipe Senior LR"}
DONO = {"79401410": "jenifer", "79560621": "daniela"}  # owner do negócio no HubSpot (conferido em 02/10)
APRES = "Apresentação de Diagnóstico"
BDR = ("Save Partners - BDR/SDR", "Save Partners - Closer", "Enriquecimento")
NOME = {"contrato_parado": "Contrato sem assinatura", "entrou_diagnostico": "Entrou em apresentação de diagnóstico",
        "conflito_novo": "Possível conflito de canal", "crm_incompleto": "Cadastro incompleto no CRM", "comercial_parado": "Negócio comercial parado",
        "diagnostico_parado": "Diagnóstico parado", "apresentacao_parada": "Apresentação de diagnóstico parada", "parceiro_inativo": "Parceiro sem indicação",
        "demanda_atrasada": "Demanda do WhatsApp atrasada", "aprovacao_parada": "Aprovação esperando", "rotina_falhou": "Rotina com falha",
        "ganho_sem_execucao": "Ganho sem execução no Bitrix", "execucao_parada": "Execução parada no Bitrix",
        "assinado_parado": "Contrato assinado sem fechar o negócio", "ganho_sem_bitrix": "Ganho sem card no Bitrix"}
NOME.update({"prazo_receita": "Prazo da Receita", "repasse_bloqueado": "Repasse bloqueado"})
URGENTE = {"conflito_novo", "demanda_atrasada", "rotina_falhou", "prazo_receita"}
# área dona de cada alerta (infra/fluxo-unico.md): (área, skills do agente que analisa)
AREA = {"contrato_parado": ("Contratos", "depto-contratos"), "assinado_parado": ("Contratos", "depto-contratos + depto-pos-venda"),
        "ganho_sem_execucao": ("Pós-venda", "depto-pos-venda"), "ganho_sem_bitrix": ("Pós-venda", "depto-pos-venda"), "execucao_parada": ("Pós-venda", "depto-pos-venda + depto-tributario"),
        "conflito_novo": ("Operações de Canal", "depto-operacoes-canal"), "repasse_bloqueado": ("Operações de Canal", "depto-operacoes-canal"),
        "parceiro_inativo": ("Partner Success", "depto-partner-success + depto-marketing"),
        "entrou_diagnostico": ("Tributário", "revisor-diagnostico + apresentacao-diagnostico"), "apresentacao_parada": ("Comercial", "celula-daniela + depto-tributario + depto-marketing"),
        "diagnostico_parado": ("Tributário", "depto-tributario"), "comercial_parado": ("Comercial", "celula-jenifer ou celula-daniela + depto-marketing"),
        "crm_incompleto": ("Dados", "depto-dados + depto-intel-comercial (Receita)"), "prazo_receita": ("Jurídico", "depto-juridico (Controle de Prazos)"),
        "demanda_atrasada": ("Supervisor", "celula-daniela"), "aprovacao_parada": ("Supervisor", "celula-daniela"), "rotina_falhou": ("TI", "depto-ti")}
ANA = os.path.join(REG, "analises-areas.json"); PARA = os.path.join(REG, "para-areas.json")
AVISO_TARDE = {"conflito_novo", "rotina_falhou", "entrou_diagnostico"}  # demanda atrasada já vai no WhatsApp das 14h (Células, 02/10)
from protecao import limpo, auditar  # noqa: E402  (mascaramento e auditor únicos: lib/protecao.py)


def ler(f, padrao):
    try: return json.load(open(f))
    except Exception: return padrao


def gravar(f, x):
    tmp = f + ".tmp"; json.dump(x, open(tmp, "w"), ensure_ascii=False, indent=1, default=str); os.replace(tmp, f)


def dia(s):
    try: return date.fromisoformat(str(s)[:10])
    except Exception: return None


def downloads():
    return sorted(glob.glob(os.path.join(DADOS, "hubspot-*.json")))


def etapas(arquivos):
    """Histórico de etapa por negócio: desde quando está na etapa atual (aprox = já estava no primeiro download visto)."""
    H = ler(ETP, {})
    vistos = set(H.get("_arquivos", []))
    for f in arquivos:
        b = f"{os.path.basename(f)}@{int(os.path.getmtime(f))}"
        if b in vistos: continue
        dt = os.path.basename(f)[8:18]; prim = not H.get("_base")
        ns = ler(f, {}).get("negocios", [])
        if not ns or "etapa" not in ns[0]:  # download em formato antigo, sem etapa: não serve de histórico
            H.setdefault("_arquivos", []).append(b); vistos.add(b); continue
        H["_base"] = H.get("_base") or dt
        for d in ns:
            h = H.get(d["id"])
            if not h or h["etapa"] != d.get("etapa"):
                H[d["id"]] = {"etapa": d.get("etapa"), "desde": dt, "aprox": prim, "novo": not h and not prim}
        H.setdefault("_arquivos", []).append(b); vistos.add(b)
    gravar(ETP, H); return H


INICIAL = [False]
BITRIX = {}  # id do negócio no HubSpot → ID Bitrix (preenchido pelas sentinelas)
BX_LINK = "https://save.bitrix24.com.br/crm/deal/details/{}/"
RESUMIDOS = {"apresentacao_parada", "comercial_parado"}  # opção B do Luis (02/10): no dia a dia, número + 3 maiores; lista completa na segunda


def novo(e):
    return e.get("primeiro") == HOJE.isoformat() and not e.get("inicial")


def ev(E, chave, tipo, pessoa, titulo, texto, depto, negocio=None, valor=None, extra=None):
    e = E.get(chave)
    if not e:
        e = E[chave] = {"tipo": tipo, "pessoa": pessoa, "depto": depto, "primeiro": HOJE.isoformat(), "inicial": INICIAL[0]}
    e.update({"chave": chave, "titulo": titulo, "texto": texto, "ultimo": HOJE.isoformat(), "ativo": True, "negocio": negocio, "valor": valor,
              "link": LINK.format(negocio) if negocio else None,
              "bitrix": BX_LINK.format(BITRIX[negocio]) if negocio and BITRIX.get(negocio) else None, **(extra or {})})
    e.pop("resolvido_em", None)
    return e


def sentinelas():
    arqs = downloads()
    if not arqs: sys.exit("sem download do HubSpot")
    H = etapas(arqs)
    N = ler(arqs[-1], {}).get("negocios", [])
    BITRIX.update({d["id"]: str((d.get("extras") or {}).get("id_bitrix")) for d in N if str((d.get("extras") or {}).get("id_bitrix") or "").isdigit()})
    ant = {d["id"] for d in ler(arqs[-2], {}).get("negocios", [])} if len(arqs) > 1 else None
    INICIAL[0] = not os.path.exists(EVT)  # primeira rodada = linha de base: nada aparece como "novo"
    E = ler(EVT, {})
    for e in E.values(): e["_visto"] = False; e.pop("rascunho", None)  # rascunho fixo antigo sai; o novo vem da área
    marca = lambda e: e.__setitem__("_visto", True)
    abertos = [d for d in N if d.get("status") == "aberto"]
    rev_ids = []

    def dono(d, padrao="daniela"):
        if "fora do roster" in (d.get("parceiro") or "").lower(): return "luis"  # até o Luis definir quem cuida de fora do roster
        return "jenifer" if d.get("pipeline") in BDR or DONO.get(str(d.get("owner"))) == "jenifer" else padrao

    contratos = defaultdict(list)  # cobrança agrupada por Master
    for d in abertos:
        x = d.get("extras") or {}; h = H.get(d["id"], {}); et = d.get("etapa"); nm = (d.get("nome") or d["id"]).strip().rstrip(".")
        criado = dia(d.get("criado"))
        # data de entrada na etapa: campo do HubSpot quando existe; senão o histórico dos downloads
        ent = dia(x.get("entrou_etapa")); desde = ent or dia(h.get("desde")); exato = bool(ent) or not h.get("aprox")
        dias_et = (HOJE - desde).days if desde else 0
        ativ = dia(x.get("ultima_atividade")); sem_ativ = (HOJE - ativ).days if ativ else None
        # parado: última atividade real (a "última modificação" é contaminada pela sincronização com o Bitrix)
        ref = ativ or criado; parado = (HOJE - ref).days if ref else 0
        if exato and desde: parado = min(parado, dias_et)
        if not exato: dias_et = max(dias_et, sem_ativ if sem_ativ is not None else ((HOJE - criado).days if criado else 0))
        base = f"{d.get('pipeline')} · {et} · parceiro {d.get('parceiro') or 'sem parceiro'}"
        if et in ET_CONTRATO and dias_et >= LIM["contrato"]:
            contratos[d.get("parceiro") or "sem parceiro"].append((nm, et))
            marca(ev(E, f"contrato|{d['id']}", "contrato_parado", dono(d), nm,
                     f"{base}. Na etapa há {dias_et} dias" + (f"; última atividade há {sem_ativ} dias" if sem_ativ is not None else "; sem atividade registrada")
                     + ". Confira na plataforma de assinatura antes de cobrar.", "Contratos", d["id"], d.get("valor"), {"dias": dias_et, "master": d.get("parceiro")}))
        if et == "Contrato Assinado" and dias_et >= LIM["assinado"]:
            marca(ev(E, f"assinado|{d['id']}", "assinado_parado", dono(d), nm, f"{base}. Assinado há {dias_et} dias e ainda não movido para Negócio Fechado: atualizar o CRM para a execução começar.",
                     "Contratos", d["id"], d.get("valor"), {"dias": dias_et}))
        if et == APRES and exato and desde and (HOJE - desde).days <= LIM["entrou_dias"]:
            if desde.isoformat() == os.path.basename(arqs[-1])[8:18] or (ent and (HOJE - ent).days <= 1): rev_ids.append(d["id"])
            marca(ev(E, f"diag|{d['id']}", "entrou_diagnostico", "geovana", nm, f"{base}. Entrou na etapa em {desde.strftime('%d/%m')}; segunda opinião do Revisor abaixo.", "Tributário", d["id"], d.get("valor")))
        lim_com = LIM["contato_futuro"] if et == "Contato Futuro" else LIM["comercial"]
        if (et in ET_COMERCIAL or d.get("pipeline") in BDR) and parado >= lim_com:
            marca(ev(E, f"comercial|{d['id']}", "comercial_parado", dono(d), nm, f"{base}. Sem movimentação há {parado} dias.", "Comercial", d["id"], d.get("valor"), {"dias": parado}))
        if et in ET_DIAG and parado >= LIM["diagnostico"]:
            marca(ev(E, f"diagparado|{d['id']}", "diagnostico_parado", "geovana", nm, f"{base}. Sem movimentação há {parado} dias.", "Tributário", d["id"], d.get("valor"), {"dias": parado}))
        if et == APRES and parado >= LIM["apresentacao"]:
            marca(ev(E, f"apres|{d['id']}", "apresentacao_parada", dono(d), nm, f"{base}. Sem movimentação há {parado} dias" + (" (60+ dias: avaliar reativação ou perda)" if parado >= 60 else "") + ".",
                     "Comercial", d["id"], d.get("valor"), {"dias": parado}))
        # cadastro: CNPJ, regime e situação oficial (Dados + Intel Comercial)
        c = PD.cnpj_digitos(x.get("cnpj")); prob = []
        if not c: prob.append("sem CNPJ")
        elif not PD.cnpj_valido(c): prob.append("CNPJ com dígito inválido")
        else:
            r = PD.receita(c)
            if r is None and os.path.exists(os.path.join(AP, "dados-publicos/receita/cnpj.sqlite")): prob.append("CNPJ não encontrado na base da Receita (conferir se está ativo)")
            r = r or {}
            sit = (r.get("situacao") or "").strip()
            if sit and sit.lower() != "ativa": prob.append(f"CNPJ {sit.lower()} na Receita")
            if r.get("simples") == "S" and x.get("regime") in ("Lucro Real", "Lucro Presumido"): prob.append("regime diverge da Receita (optante do Simples)")
            if r.get("simples") == "N" and x.get("regime") == "Simples Nacional": prob.append("regime diverge da Receita (não optante do Simples)")
            if r.get("razao") and not x.get("regime"): prob.append(f"sem regime (razão oficial: {r.get('razao')})")
        if not x.get("regime") and not any("regime" in p for p in prob): prob.append("sem regime")
        if prob:
            marca(ev(E, f"crm|{d['id']}", "crm_incompleto", dono(d), nm, f"{base}. " + "; ".join(prob) + ".", "Dados", d["id"], d.get("valor")))

    # o rascunho ao parceiro vem da área de Contratos (operacao-areas), não de modelo fixo (Luis, 15/10)

    # ganho sem card no Bitrix: a execução não tem como começar (Pós-venda, 02/10)
    for d in N:
        if d.get("status") != "ganho" or str((d.get("extras") or {}).get("id_bitrix") or "").isdigit(): continue
        fe = dia(d.get("fechado"))
        if fe and LIM["ganho_sem_bitrix"][0] <= (HOJE - fe).days <= LIM["ganho_sem_bitrix"][1]:
            marca(ev(E, f"sembitrix|{d['id']}", "ganho_sem_bitrix", "daniela", (d.get("nome") or d["id"]).rstrip("."),
                     f"Ganho em {fe.strftime('%d/%m/%Y')} (parceiro {d.get('parceiro') or 'sem parceiro'}) e sem ID Bitrix no HubSpot: a execução não tem card para começar.",
                     "Pós-venda", d["id"], d.get("valor"), {"dias": (HOJE - fe).days}))

    # conflito de canal nos negócios novos: mesma raiz de CNPJ, canais identificados diferentes (regra do conflito_canal.py)
    sys.path.insert(0, os.path.join(SK, "depto-operacoes-canal/scripts"))
    try:
        import _comum as OC
        _, _, cfg_oc, roster = OC.carregar(arqs[-1]); canal = lambda d: OC.canal(d, cfg_oc, roster)
    except Exception:
        canal = lambda d: (d.get("parceiro") or "Sem parceiro identificado", "Master" if d.get("parceiro") else "Sem parceiro", "")
    if ant is not None:
        por_raiz = defaultdict(list)
        for d in N:
            c = PD.cnpj_digitos((d.get("extras") or {}).get("cnpj"))
            if d.get("status") in ("aberto", "ganho") and PD.cnpj_valido(c): por_raiz[c[:8]].append(d)
        for d in abertos:
            if d["id"] in ant and f"conflito|{d['id']}" not in E: continue  # só negócio novo (ou alerta que já estava aberto)
            c = PD.cnpj_digitos((d.get("extras") or {}).get("cnpj"))
            if not PD.cnpj_valido(c): continue
            cd, td, _ = canal(d)
            if td == "Sem parceiro": continue
            outros = [o for o in por_raiz[c[:8]] if o["id"] != d["id"] and canal(o)[1] != "Sem parceiro" and canal(o)[0] != cd]
            if outros:
                o = sorted(outros, key=lambda o: PD.data_efetiva(o) or "")[0]
                marca(ev(E, f"conflito|{d['id']}", "conflito_novo", "daniela", (d.get("nome") or d["id"]).rstrip("."),
                         f"Novo negócio do parceiro {cd}; a mesma empresa já tem negócio {o.get('status')} com {canal(o)[0]} "
                         f"(desde {(PD.data_efetiva(o) or '')[:10]}). Decisão de conflito é do Luis.", "Operações de Canal", d["id"], d.get("valor"), {"cc_luis": True}))

    # parceiros sem indicação: compara com o intervalo real entre indicações de cada um (Dados, 02/10)
    dias_p = defaultdict(set)
    for d in N:
        p, de = d.get("parceiro"), dia(PD.data_efetiva(d))
        if p and de and "fora do roster" not in p.lower() and (HOJE - de).days <= 365: dias_p[p].add(de)
    for p, ds in dias_p.items():
        ds = sorted(ds)
        if len(ds) < 3: continue
        gaps = sorted((b - a).days for a, b in zip(ds, ds[1:]))
        p90 = gaps[min(len(gaps) - 1, int(round(0.9 * (len(gaps) - 1))))]
        limite = min(90, max(30, round(1.5 * p90))); gap = (HOJE - ds[-1]).days
        if gap >= limite:
            marca(ev(E, f"parceiro|{p}", "parceiro_inativo", "daniela", p,
                     f"Costuma ficar no máximo {p90} dias entre indicações ({len(ds)} dias com negócio em 12 meses); a última entrou há {gap} dias ({ds[-1].strftime('%d/%m/%Y')}).",
                     "Partner Success", extra={"dias": gap}))

    prazos_receita(E, marca)
    repasses_bloqueados(E, marca)
    execucao(N, E, marca)
    supervisao(E, marca)
    for k, e in E.items():
        if not e.pop("_visto", False) and e.get("ativo"):
            e["ativo"] = False; e["resolvido_em"] = HOJE.isoformat()
    # guarda resolvidos por 30 dias
    E = {k: e for k, e in E.items() if e.get("ativo") or (dia(e.get("resolvido_em")) or HOJE) >= HOJE - timedelta(days=30)}
    gravar(EVT, E)
    if rev_ids and not os.environ.get("OPERACAO_REG"): revisor(rev_ids)  # na simulação o Revisor não roda
    at = [e for e in E.values() if e.get("ativo")]
    print(f"eventos ativos: {len(at)} · novos hoje: {sum(1 for e in at if novo(e))} · revisor: {len(rev_ids)} negócio(s)")


def prazos_receita(E, marca):
    """Despacho, intimação ou comunicado da Receita nas demandas do WhatsApp (última triagem com IA): vai ao Controle de Prazos do Jurídico."""
    fs = [f for f in sorted(glob.glob(os.path.join(AP, "celulas", "whatsapp-triagem-*.json")), key=os.path.getmtime)
          if not str(ler(f, {}).get("leitura_geral", "")).startswith("Rodada automática")][-1:]  # só a última triagem com IA
    if not fs: return
    T = ler(fs[-1], {}); pad = re.compile(r"despacho|intima[çc][ãa]o|comunicado|e-?cac|manifesta[çc][ãa]o de inconformidade|auto de infra", re.I)
    for p, P in (T.get("pessoas") or {}).items():
        for i in P.get("itens", []):
            enc = (i.get("encaminhar") or {}); txt = " ".join(str(i.get(k) or "") for k in ("o_que_pede", "entrega")) + " " + str(enc.get("assunto") or "")
            if not (str(enc.get("area", "")).startswith(("jur_comunicados", "jur_manifestacao", "jur_contencioso_adm")) or pad.search(txt)): continue
            marca(ev(E, f"prazo|{p}|{i.get('chat')}", "prazo_receita", "daniela", (i.get("negocio") or enc.get("empresa") or i.get("chat") or "Comunicado da Receita"),
                     limpo(f"{i.get('o_que_pede') or ''} Prazo informado: {i.get('prazo') or enc.get('prazo') or 'não informado (confirmar a data de ciência)'}."),
                     "Jurídico", extra={"master": i.get("master"), "prazo": i.get("prazo") or enc.get("prazo")}))


def repasses_bloqueados(E, marca):
    """Conferência semanal de repasses (Operações de Canal): Master com ganhos de repasse bloqueado vira alerta ao Luis."""
    fs = sorted(glob.glob(os.path.join(AP, "departamentos/operacoes-canal/conferencia-repasses-*.json")))
    if not fs: return
    C = ler(fs[-1], {})
    for r in C.get("por_parceiro", []):
        if r.get("Tipo de canal") != "Master" or not r.get("Bloqueados"): continue
        marca(ev(E, f"repasse|{r['Parceiro']}", "repasse_bloqueado", "luis", r["Parceiro"],
                 f"{r['Bloqueados']} de {r.get('Ganhos')} ganhos com repasse bloqueado (faltam honorário, % do parceiro ou dado do ganho); conferência de {C.get('data')}.",
                 "Operações de Canal", extra={"master": r["Parceiro"]}))


def para_areas():
    """Eventos ativos sem análise da área (ou com a situação mudada desde a análise): entrada da rotina operacao-areas."""
    E = ler(EVT, {}); A = ler(ANA, {}); out = []
    for k, e in E.items():
        if not e.get("ativo") or e["tipo"] not in AREA: continue
        a = A.get(k) or {}
        if a and a.get("texto_base") == e.get("texto") and (dia(a.get("quando")) or HOJE) >= HOJE - timedelta(days=7): continue
        area, skill = AREA[e["tipo"]]
        out.append({"chave": k, "tipo": e["tipo"], "nome_tipo": NOME.get(e["tipo"]), "area": area, "agente": skill, "pessoa": e["pessoa"], "titulo": e["titulo"],
                    "situacao": e["texto"], "negocio": e.get("negocio"), "link": e.get("link"), "bitrix": e.get("bitrix"), "valor": e.get("valor"), "master": e.get("master"),
                    "revisor": e.get("revisor")})
    # por rodada, no máximo 80: urgentes e novos primeiro, depois maior valor (o resto entra nas rodadas seguintes)
    out.sort(key=lambda x: (x["tipo"] not in URGENTE, not novo(E[x["chave"]]), -(x.get("valor") or 0)))
    out = sorted(out[:80], key=lambda x: (x["area"], -(x.get("valor") or 0)))
    gravar(PARA, out)
    from collections import Counter
    print(f"{len(out)} evento(s) para as áreas →", PARA, dict(Counter(x["area"] for x in out)))


def gravar_analises(arq):
    """Análises devolvidas pelas áreas: [{chave, area, fazer, precisa, falta, rascunho?}]. O rascunho passa pela auditoria da Qualidade."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "infra")); import validar_saidas as VS
    E = ler(EVT, {}); A = ler(ANA, {}); n = 0; rej = []
    for x in ler(arq, []):
        e = E.get(x.get("chave"))
        if not e: continue
        erros = VS.checar_item(x, ("fazer", "precisa", "falta"), x.get("chave"))
        if erros: rej.append({**x, "erros": erros}); continue  # trava de qualidade: volta ao gerente da área, não entra no plano
        r = limpo(x.get("rascunho") or "") or None
        if r and not auditar(r): r = None
        A[x["chave"]] = {"area": x.get("area"), "fazer": limpo(x.get("fazer") or ""), "precisa": limpo(x.get("precisa") or ""), "falta": limpo(x.get("falta") or ""),
                         "rascunho": r, "quando": HOJE.isoformat(), "texto_base": e.get("texto"), "revisao": x.get("revisao")}
        n += 1
    A = {k: v for k, v in A.items() if k in E and E[k].get("ativo")}  # some quando o alerta se resolve
    gravar(ANA, A); gravar(os.path.join(REG, "analises-rejeitadas.json"), rej)
    print(f"{n} análise(s) gravada(s) →", ANA, f"· {len(rej)} recusada(s) pela trava de qualidade → registro/analises-rejeitadas.json" if rej else "")


def execucao(N, E, marca):
    """Pós-venda: fase da execução no Bitrix (lib/bitrix.py baixa quando o webhook da TI existir)."""
    import bitrix as BX
    X = BX.ultimo()
    if not X: return
    L = BX.CFG["limites"]; ex = X["execucoes"]
    for d in N:
        b = str((d.get("extras") or {}).get("id_bitrix") or "")
        if d.get("status") != "ganho" or not b.isdigit(): continue
        fe = dia(d.get("fechado")); nm = d.get("nome") or d["id"]
        its = ex.get(b, [])
        if not its and fe and (HOJE - fe).days >= L["ganho_sem_execucao_dias"]:
            marca(ev(E, f"semexec|{d['id']}", "ganho_sem_execucao", "daniela", nm,
                     f"Ganho em {fe.strftime('%d/%m/%Y')} (parceiro {d.get('parceiro') or 'sem parceiro'}) e ainda sem card de execução no Bitrix.", "Pós-venda", d["id"], d.get("valor")))
        for it in its:
            desde = dia(it.get("desde"))
            if it["grupo"] == "ativa" and desde and (HOJE - desde).days >= L["fase_ativa_parada_dias"]:
                marca(ev(E, f"execparada|{it['card']}", "execucao_parada", "daniela", nm,
                         f"{it['funil']} em \"{it['fase']}\" desde {desde.strftime('%d/%m/%Y')} ({(HOJE - desde).days} dias). Card: {it['card']}", "Pós-venda", d["id"], d.get("valor"),
                         {"dias": (HOJE - desde).days}))


def supervisao(E, marca):
    # demandas do WhatsApp esperando além do prazo
    R = ler(os.path.join(REG, "demandas.json"), {}).get("demandas", {})
    for d in (R.values() if isinstance(R, dict) else R):
        st = d.get("status"); h = d.get("aguardando_h") or 0
        aberta = dia(d.get("aberta_em")); idade = (HOJE - aberta).days if aberta else 0
        pela_ia = any("(IA)" in (x.get("evento") or "") for x in d.get("eventos", []))  # a triagem sem IA marca tudo como responder
        if pela_ia and ((st == "responder" and (h >= 24 or idade >= 1)) or (st == "acompanhar" and idade >= 3)):
            marca(ev(E, f"demanda|{d['id']}", "demanda_atrasada", d.get("pessoa") or "daniela", f"{d['id']} · {d.get('titulo')}",
                     f"{d.get('o_que_pede') or ''} Status: {st}, aberta em {(d.get('aberta_em') or '')[8:10]}/{(d.get('aberta_em') or '')[5:7]}. Próximo passo: {d.get('proximo_passo') or 'definir'}.", "Supervisor"))
    # chamados propostos e pedidos da Central esperando decisão
    agora = datetime.combine(HOJE, datetime.now().time())
    for k, c in ler(os.path.join(REG, "chamados-propostos.json"), {}).items():
        try: t = datetime.fromisoformat(c.get("proposto_em"))
        except Exception: continue
        h = (agora - t).total_seconds() / 3600
        if c.get("status") == "proposto" and h >= LIM["aprovacao_h"]:
            quem = c.get("pessoa") or "daniela"  # D98 (23/10/2026): a dona aprova; atraso continua com ela, sem subir ao Luis
            marca(ev(E, f"aprov|chamado|{k}", "aprovacao_parada", quem, c.get("titulo") or k,
                     f"Chamado proposto para {c.get('grupo')} em {c['proposto_em'][8:10]}/{c['proposto_em'][5:7]} aguarda aprovação no painel"
                     + (f" há {int(h // 24)} dias: atrasado." if h >= LIM["aprovacao_escala_h"] else "."), "Supervisor"))
    for k, p in ler(os.path.join(AP, "central-agentes/registro.json"), {}).get("pedidos", {}).items():
        if p.get("status") != "aguardando_aprovacao": continue
        t = dia(p.get("respondido") or p.get("recebido"))
        if t and (HOJE - t).days >= 1:
            marca(ev(E, f"aprov|pedido|{k}", "aprovacao_parada", p.get("pessoa") or "luis", f"{k} · {(p.get('assunto') or '')[:80]}",
                     f"Resposta entregue em {t.strftime('%d/%m')}; falta Aprovado, Não aprovado ou Nova análise.", "Supervisor"))
    # rotinas com erro nas últimas 24 h (só "hoje" deixava de fora o backup das 19h30 e tudo o que roda depois das sentinelas)
    log = os.path.join(AP, "logs/partners.log")
    desde = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    erros = {}
    if os.path.exists(log):
        for l in open(log, errors="ignore"):
            if l[:19] < desde: continue
            m = re.search(r"\[(.+?)\] (.*)", l)
            if not m: continue
            if "ERRO" in m.group(2): erros[m.group(1)] = m.group(2)  # a chave inclui o script ("areas:icp"): o ok de um não apaga o erro de outro
            elif m.group(2).strip() == "ok": erros.pop(m.group(1), None)  # voltou a rodar bem depois do erro
    for r, msg in erros.items():
        marca(ev(E, f"rotina|{r}|{HOJE}", "rotina_falhou", "luis", f"Rotina {r}", msg, "TI"))


def revisor(ids):
    """Executor: segunda opinião do Revisor nos negócios que entraram em apresentação (pasta separada da revisão semanal)."""
    out = os.path.join(AP, "celulas/geovana/revisor/diario"); os.makedirs(out, exist_ok=True)
    dec = os.path.join(AP, "celulas/geovana/revisor/decisoes.json")
    if os.path.exists(dec) and not os.path.exists(os.path.join(out, "decisoes.json")):
        os.symlink(dec, os.path.join(out, "decisoes.json"))
    r = subprocess.run([sys.executable, os.path.join(SK, "recuperador/scripts/revisor.py"), "--ids", ",".join(ids), "--fichas", str(len(ids))],
                       capture_output=True, text=True, env={**os.environ, "REVISOR_OUT": out}, timeout=900)
    J = ler(os.path.join(out, f"revisor-{HOJE.isoformat()}.json"), {})
    lac = defaultdict(list)
    for l in J.get("lacunas", []) if isinstance(J.get("lacunas"), list) else []:
        i = re.search(r"deal/(\d+)", str(l.get("link") or ""))
        if i and l.get("prioridade") in ("alta", "média"): lac[i.group(1)].append((l.get("tese") or l.get("código") or "tese").split(" (")[0][:70])
    E = ler(EVT, {})
    for i in ids:
        e = E.get(f"diag|{i}")
        if e:
            t = lac.get(i)
            e["revisor"] = (f"lacunas a conferir: {', '.join(sorted(set(t))[:5])}" if t else "sem lacuna apontada") if r.returncode == 0 else "Revisor falhou (ver logs)"
            e["arquivo"] = os.path.join(out, f"Revisor-Diagnostico-{HOJE.isoformat()}.xlsx")
    gravar(EVT, E)


# ---------------------------------------------------------------- plano do dia
def _ord(e):
    return (not novo(e), -(e.get("valor") or 0), -(e.get("dias") or 0))


ANALISES = {}
def plano(previa=False, so_urgentes=False):
    import email_layout as L
    ANALISES.update(ler(ANA, {}))
    E = ler(EVT, {}); at = [e for e in E.values() if e.get("ativo")]
    fest = os.path.join(REG, "plano-enviado.json"); est = ler(fest, {}); falhas = 0
    chave = lambda e: f"{HOJE.isoformat()}|{e['tipo']}|{e['titulo']}"  # aviso: uma vez por item por dia
    for p, (nome, email) in PESSOAS.items():
        meus = [e for e in at if (e["pessoa"] == p and e["tipo"] != "demanda_atrasada") or (p == "luis" and (e.get("cc_luis") or e["tipo"] == "demanda_atrasada"))]
        # "entrou em diagnóstico" é aviso de chegada: só no 1º dia (ficava 8 dias no plano; 106 de 309 eventos eram isso).
        # Filtra ANTES de juntar o cadastro incompleto: senão o crm_incompleto era absorvido por um aviso que some do plano.
        meus = [e for e in meus if e["tipo"] != "entrou_diagnostico" or (HOJE - date.fromisoformat(e.get("primeiro") or HOJE.isoformat())).days <= 1]
        outros_neg = {e.get("negocio") for e in meus if e["tipo"] != "crm_incompleto" and e.get("negocio")}
        for e in meus:  # mesmo negócio com cadastro incompleto e outra pendência: um cartão só (Dados, 02/10)
            e.pop("tambem", None)
        for e in [e for e in meus if e["tipo"] == "crm_incompleto" and e.get("negocio") in outros_neg]:
            alvo = next(o for o in meus if o.get("negocio") == e["negocio"] and o["tipo"] != "crm_incompleto")
            alvo["tambem"] = "cadastro incompleto: " + e["texto"].split(". ", 1)[-1]
        meus = [e for e in meus if not (e["tipo"] == "crm_incompleto" and e.get("negocio") in outros_neg)]
        if so_urgentes:
            ja = set(est.get(f"avisados|{p}", []))
            meus = [e for e in meus if e["tipo"] in AVISO_TARDE and novo(e) and chave(e) not in ja]
            if not meus: continue
        novos = [e for e in meus if novo(e)]
        por = defaultdict(list)
        for e in sorted(meus, key=_ord): por[e["tipo"]].append(e)
        linhas = [L.cabecalho("Área Partners · Agentes", "Aviso da tarde" if so_urgentes else "Plano do dia", f"{nome} · {HOJE.strftime('%d/%m/%Y')}")]
        if so_urgentes:
            linhas.append(L.paragrafo(f"{nome}, apareceu algo novo e urgente desde o plano da manhã. Nada foi enviado a parceiro ou cliente nem alterado no CRM; "
                                      "o contato e a decisão são seus.", "28px 32px 12px"))
        if not so_urgentes:
            linhas.append(L.paragrafo(f"Bom dia, {nome}. Os agentes já cruzaram HubSpot, WhatsApp, Central e chamados propostos. Abaixo, o que pede a sua ação hoje, "
                                      "com o que eles já adiantaram. Nada foi enviado a parceiro ou cliente nem alterado no CRM.", "28px 32px 12px"))
            linhas.append(L.kpis([("Novos hoje", str(len(novos)), "desde ontem"), ("Pendências", str(len(meus)), "ativas"),
                                  ("Urgentes", str(sum(1 for e in meus if e["tipo"] in URGENTE)), "olhar primeiro")]))
        if p == "luis" and not so_urgentes:
            linhas += quadro_supervisor(L, at)
        if not meus and not (p == "luis" and not so_urgentes):
            continue
        if not so_urgentes and not previa and est.get(f"plano|{p}") == HOJE.isoformat():
            print(p, "plano de hoje já enviado"); continue
        ordem = ["rotina_falhou", "prazo_receita", "conflito_novo", "repasse_bloqueado", "demanda_atrasada", "aprovacao_parada", "entrou_diagnostico", "contrato_parado", "assinado_parado", "ganho_sem_bitrix",
             "ganho_sem_execucao", "execucao_parada",
                 "diagnostico_parado", "comercial_parado", "apresentacao_parada", "crm_incompleto", "parceiro_inativo"]
        for t in ordem:
            xs = por.get(t)
            if not xs: continue
            n_nov = sum(1 for e in xs if novo(e))
            linhas.append(L.secao(f"{NOME[t]} · {len(xs)}" + (f" ({n_nov} novo{'s' if n_nov > 1 else ''})" if n_nov else "")))
            segunda = HOJE.weekday() == 0
            if t in RESUMIDOS and not segunda:
                lim = 3; xs = sorted(xs, key=lambda e: (-(e.get("valor") or 0), -(e.get("dias") or 0)))
                linhas.append(L.paragrafo(f"Os 3 de maior valor abaixo. A lista completa, com os links, está na planilha anexa."))
            elif t in RESUMIDOS:
                lim = 10
            else:
                lim = 6 if t == "crm_incompleto" else 10
            for e in xs[:lim]:
                an = ANALISES.get(e.get("chave")) or {}
                ls = [("Situação", L.esc(limpo(e["texto"])))]
                if an.get("fazer"): ls.append((f"O que fazer · {an.get('area')}", L.esc(an["fazer"])))
                if an.get("precisa"): ls.append(("O que você também precisa", L.esc(an["precisa"])))
                if an.get("falta"): ls.append(("O que falta e quem fornece", L.esc(an["falta"])))
                if an.get("rascunho"): e = {**e, "rascunho": an["rascunho"]}
                rv = an.get("revisao") or {}
                if rv.get("gerente"): ls.append(("Revisado por", L.esc(f"{rv['gerente']} · {rv.get('rodadas') or 1} rodada(s)" + (f" · consultou {', '.join(rv['areas_consultadas'])}" if rv.get("areas_consultadas") else ""))))
                if e.get("tambem"): ls.append(("Também", L.esc(limpo(e["tambem"]))))
                if e.get("revisor"): ls.append(("Revisor", L.esc(e["revisor"]) + (f" · planilha {L.esc(os.path.basename(e['arquivo']))} na pasta da Geovana" if e.get("arquivo") else "")))
                if e.get("rascunho"): ls.append(("Rascunho para o parceiro", "<i>" + L.esc(e["rascunho"]) + "</i> (revisado pela Qualidade; você decide se envia)"))
                if e.get("valor"): ls.append(("Valor no CRM", f"R$ {e['valor']:,.0f}".replace(",", ".")))
                ls.append(("No plano desde", L.esc(e["primeiro"][8:10] + "/" + e["primeiro"][5:7]) + (" · <b>novo</b>" if novo(e) else "")))
                abre = [f'<a href="{L.esc(u)}" style="color:{L.OURO_TEXTO};font-weight:bold">{n}</a>' for n, u in (("Abrir no HubSpot", e.get("link")), ("Abrir no Bitrix", e.get("bitrix"))) if u]
                if abre: ls.append(("Links", " &nbsp;·&nbsp; ".join(abre)))
                linhas.append(L.cartao(limpo(e["titulo"]), e["depto"], ls, L.marca.C["erro"] if t in URGENTE else L.OURO_TEXTO, e.get("link")))
            if len(xs) > lim:
                linhas.append(L.paragrafo(f"E mais {len(xs) - lim}. Todos estão na planilha anexa, com os links do HubSpot e do Bitrix."))
        linhas.append(L.rodape("Plano montado pelos agentes da Área Partners às " + datetime.now().strftime("%Hh%M")
                               + ". Quando a situação se resolve no HubSpot, o item sai sozinho do plano do dia seguinte."))
        corpo = L.documento(*linhas)
        anexo = planilha(p, nome, meus, so_urgentes, copiar=not previa) if meus else None
        assunto = f"[Partners · automático] {'Aviso da tarde' if so_urgentes else 'Plano do dia'} · {nome} · {HOJE.strftime('%d/%m')}"
        if previa:
            f = os.path.join(tempfile.gettempdir(), f"plano-{p}.html"); open(f, "w").write(corpo); print(p, len(meus), "→", f, "·", anexo or "sem anexo"); continue
        ok, msg = L.outlook([email], [], assunto, corpo, [anexo] if anexo else (), enviar=True)
        print(p, len(meus), "enviado" if ok else f"FALHOU {msg}")
        falhas += not ok
        if ok:
            if not so_urgentes: est[f"plano|{p}"] = HOJE.isoformat()
            # o que já foi no plano (ou no aviso) não volta no aviso da tarde
            av = [x for x in est.get(f"avisados|{p}", []) if x[:10] >= (HOJE - timedelta(days=7)).isoformat()]
            est[f"avisados|{p}"] = av + [chave(e) for e in meus if e["tipo"] in AVISO_TARDE]
            gravar(fest, est)  # grava a cada envio: uma queda no meio não reenvia a quem já recebeu
    if falhas: sys.exit(f"{falhas} e-mail(s) do plano não saíram (Outlook)")


def planilha(p, nome, evs, aviso=False, copiar=True):
    """Lista completa do dia com links clicáveis (o e-mail mostra só os principais)."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    out = os.path.join(os.environ.get("OPERACAO_REG") or os.path.join(AP, "departamentos/operacao"), nome); os.makedirs(out, exist_ok=True)
    f = os.path.join(out, f"{'Aviso-da-tarde' if aviso else 'Plano-do-dia'}-{nome}-{HOJE.isoformat()}.xlsx")
    wb = Workbook(); ws = wb.active; ws.title = "Pendências"
    cab = ["Tipo", "Negócio / item", "Situação", "Área", "Valor no CRM", "Desde", "Novo", "HubSpot", "Bitrix", "Rascunho para o parceiro (auditado; quem envia é você)",
           "Usei / Ajustei / Não usei"]  # medição da D28 a partir do lançamento (docs/lancamento-2026)
    ws.append(cab)
    for c in ws[1]: c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F1F1F")
    for e in sorted(evs, key=lambda e: (list(NOME).index(e["tipo"]), _ord(e))):
        ws.append([NOME[e["tipo"]], limpo(e["titulo"]), limpo(e["texto"]), e["depto"], e.get("valor"), e["primeiro"][8:10] + "/" + e["primeiro"][5:7],
                   "sim" if novo(e) else "", "Abrir" if e.get("link") else "", "Abrir" if e.get("bitrix") else "", e.get("rascunho") or ""])
        r = ws.max_row
        for col, k in ((8, "link"), (9, "bitrix")):
            if e.get(k): ws.cell(r, col).hyperlink = e[k]; ws.cell(r, col).font = Font(color="7A5F00", underline="single", bold=True)
        ws.cell(r, 5).number_format = '"R$" #,##0'
    for col, w in zip("ABCDEFGHIJK", (30, 42, 70, 16, 14, 8, 6, 10, 10, 50, 16)): ws.column_dimensions[col].width = w
    from openpyxl.worksheet.datavalidation import DataValidation
    dv = DataValidation(type="list", formula1='"Usei,Ajustei,Não usei"', allow_blank=True); ws.add_data_validation(dv); dv.add(f"K2:K{max(2, ws.max_row)}")
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(vertical="top", wrap_text=c.column in (2, 3, 10))
    ws.freeze_panes = "C2"; ws.auto_filter.ref = f"A1:K{max(2, ws.max_row)}"  # inclui a coluna K (vazia; ws.dimensions parava em J)
    wb.save(f)
    # entrega diária na pasta da pessoa (lançamento ao time, Luis 23/10/2026): a planilha também vai para a Central dela no OneDrive
    # prévia e simulação (OPERACAO_REG) não publicam: a prévia sobrescrevia a planilha do dia na pasta da pessoa antes do envio
    if not copiar or os.environ.get("OPERACAO_REG"): return f
    try:
        import shutil, caminhos
        if p in ("daniela", "jenifer", "geovana"):
            destino = os.path.join(caminhos.pasta(p), "Plano do dia"); os.makedirs(destino, exist_ok=True)
            shutil.copy2(f, os.path.join(destino, os.path.basename(f)))
    except Exception as erro:
        print(f"aviso: plano de {nome} não foi copiado para a pasta do OneDrive ({erro})")
    return f


def quadro_supervisor(L, at):
    por = defaultdict(lambda: defaultdict(int))
    for e in at: por[e["pessoa"]][e["tipo"]] += 1
    linhas = [L.secao("Supervisor · como está a operação")]
    for p, (nome, _) in PESSOAS.items():
        if p == "luis": continue
        t = por.get(p, {})
        partes = [f"{n} {NOME[k].lower()}" for k, n in sorted(t.items(), key=lambda x: -x[1])]
        linhas.append(L.paragrafo(f"<b>{nome}:</b> {sum(t.values())} pendência(s)" + (" · " + L.esc(", ".join(partes[:5])) if partes else "")))
    log = os.path.join(AP, "logs/partners.log")
    hoje_l = [l for l in open(log, errors="ignore") if l.startswith(HOJE.isoformat())] if os.path.exists(log) else []
    ok = len([l for l in hoje_l if "] ok" in l]); er = len([l for l in hoje_l if "ERRO" in l])
    linhas.append(L.paragrafo(f"<b>Rotinas hoje:</b> {ok} execuções ok, {er} com erro."))
    try:  # D28: acerto das respostas sugeridas ao parceiro (degrau 2 só com 20+ casos e 95%+ por tipo)
        import medicao_respostas as MR
        rel = [r for r in MR.relatorio() if r["tipo"] != "outro"]
        if rel: linhas.append(L.paragrafo("<b>Respostas ao parceiro (D28, 14 dias):</b> " + L.esc("; ".join(
            f"{r['tipo']}: {r['aproveitada_pct']}% em {r['casos']} caso(s)" + (" · pronto para o degrau 2" if r["pronto_para_degrau_2"] else "") for r in rel))))
    except Exception:
        pass
    return linhas


def resumo():
    E = ler(EVT, {}); at = [e for e in E.values() if e.get("ativo")]
    c = defaultdict(int)
    for e in at: c[(e["pessoa"], e["tipo"])] += 1
    for (p, t), n in sorted(c.items()): print(f"{p:8} {NOME[t]:42} {n}")
    print("total ativos:", len(at))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["sentinelas", "plano", "avisos", "resumo", "para-areas", "gravar-analises"]); ap.add_argument("arq", nargs="?")
    ap.add_argument("--previa", action="store_true")
    a = ap.parse_args()
    if a.cmd == "gravar-analises": gravar_analises(a.arq)
    else: {"sentinelas": sentinelas, "resumo": resumo, "para-areas": para_areas}.get(a.cmd, lambda: plano(a.previa, a.cmd == "avisos"))()
