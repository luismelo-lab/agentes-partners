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

Executores encadeados (agente → agente, sem aprovação, decisão D26 do Luis em 01/10/2026):
  entrou_diagnostico → Revisor de Diagnóstico nos negócios novos (segunda opinião no mesmo dia)
  contrato_parado    → rascunho de cobrança ao parceiro, auditado pela Qualidade (só vai no plano; quem envia é a Daniela)
  crm_incompleto     → cadastro oficial da Receita ao lado, para a correção já sair pronta
Continua proibido sem pessoa: falar com parceiro ou cliente, alterar HubSpot ou GLPI, abrir chamado.

Uso:
  operacao.py sentinelas            atualiza registro/eventos.json e roda os executores
  operacao.py plano [--previa]      e-mail do plano do dia para cada pessoa (e o resumo do supervisor para o Luis)
  operacao.py avisos                só os eventos novos e urgentes desde a última rodada (rodada da tarde)
  operacao.py resumo                imprime o quadro de eventos ativos
"""
import argparse, glob, json, os, re, subprocess, sys, tempfile
from collections import defaultdict
from datetime import date, datetime, timedelta

AP = os.path.expanduser("~/agentes-partners"); SK = os.path.expanduser("~/.claude/skills")
DADOS = os.path.join(AP, "departamentos/resultados/dados"); REG = os.path.join(AP, "registro")
EVT = os.path.join(REG, "eventos.json"); ETP = os.path.join(REG, "etapas.json")
sys.path.insert(0, os.path.join(AP, "lib")); sys.path.insert(0, os.path.join(SK, "depto-marketing/scripts"))
import partners_dados as PD  # noqa: E402

HOJE = date.today()
LINK = "https://app.hubspot.com/contacts/47865021/deal/{}"
PESSOAS = {"daniela": ("Daniela", "daniela.maciel@savecompany.com.br"), "jenifer": ("Jenifer", "jenifer.carvalho@savecompany.com.br"),
           "geovana": ("Geovana", "geovana.goncalves@savecompany.com.br"), "luis": ("Luis", "luis.melo@savecompany.com.br")}
LIM = {"contrato": 5, "comercial": 15, "diagnostico": 15, "apresentacao": 30, "parceiro": 60, "aprovacao_h": 24}
ET_CONTRATO = {"Contrato Enviado", "Pendência Fechamento"}
ET_COMERCIAL = {"Agendamento", "Em Contato", "Negociação", "Follow - Up", "Novo Negócio", "Contato Futuro"}
ET_DIAG = {"Em Diagnóstico", "Análise de Documentos", "Análise com Pendência", "Documentação Pendente"}
APRES = "Apresentação de Diagnóstico"
BDR = ("Save Partners - BDR/SDR", "Save Partners - Closer", "Enriquecimento")
NOME = {"contrato_parado": "Contrato sem assinatura", "entrou_diagnostico": "Entrou em apresentação de diagnóstico",
        "conflito_novo": "Possível conflito de canal", "crm_incompleto": "Cadastro incompleto no CRM", "comercial_parado": "Negócio comercial parado",
        "diagnostico_parado": "Diagnóstico parado", "apresentacao_parada": "Apresentação de diagnóstico parada", "parceiro_inativo": "Parceiro sem indicação",
        "demanda_atrasada": "Demanda do WhatsApp atrasada", "aprovacao_parada": "Aprovação esperando", "rotina_falhou": "Rotina com falha",
        "ganho_sem_execucao": "Ganho sem execução no Bitrix", "execucao_parada": "Execução parada no Bitrix"}
URGENTE = {"conflito_novo", "entrou_diagnostico", "demanda_atrasada", "rotina_falhou"}


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


def novo(e):
    return e.get("primeiro") == HOJE.isoformat() and not e.get("inicial")


def ev(E, chave, tipo, pessoa, titulo, texto, depto, negocio=None, valor=None, extra=None):
    e = E.get(chave)
    if not e:
        e = E[chave] = {"tipo": tipo, "pessoa": pessoa, "depto": depto, "primeiro": HOJE.isoformat(), "inicial": INICIAL[0]}
    e.update({"titulo": titulo, "texto": texto, "ultimo": HOJE.isoformat(), "ativo": True, "negocio": negocio, "valor": valor,
              "link": LINK.format(negocio) if negocio else None, **(extra or {})})
    e.pop("resolvido_em", None)
    return e


def auditar(texto):
    """Qualidade: o rascunho só segue se o auditor de promessas não marcar nada."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, dir=os.path.join(AP, "logs")) as t: t.write(texto)
    try:
        r = subprocess.run([sys.executable, os.path.join(SK, "depto-qualidade/scripts/auditar_texto.py"), t.name, "--json"], capture_output=True, text=True, timeout=60)
        J = json.loads(r.stdout or "[]")
        achados = sum(len(x.get("achados", [])) for x in (J.values() if isinstance(J, dict) else J))
        return achados == 0
    except Exception:
        return False
    finally:
        os.unlink(t.name)


def sentinelas():
    arqs = downloads()
    if not arqs: sys.exit("sem download do HubSpot")
    H = etapas(arqs)
    N = ler(arqs[-1], {}).get("negocios", [])
    ant = {d["id"] for d in ler(arqs[-2], {}).get("negocios", [])} if len(arqs) > 1 else None
    INICIAL[0] = not os.path.exists(EVT)  # primeira rodada = linha de base: nada aparece como "novo"
    E = ler(EVT, {})
    for e in E.values(): e["_visto"] = False
    marca = lambda e: e.__setitem__("_visto", True)
    abertos = [d for d in N if d.get("status") == "aberto"]
    rev_ids = []

    for d in abertos:
        x = d.get("extras") or {}; h = H.get(d["id"], {}); et = d.get("etapa"); nm = d.get("nome") or d["id"]
        desde = dia(h.get("desde")); dias_et = (HOJE - desde).days if desde else 0
        mod = dia(x.get("ultima_atividade")) or dia(x.get("ultima_modificacao")); parado = (HOJE - mod).days if mod else 0
        mais = "pelo menos " if h.get("aprox") else ""
        base = f"{d.get('pipeline')} · {et} · parceiro {d.get('parceiro') or 'sem parceiro'}"
        ativ = dia(x.get("ultima_atividade")); sem_ativ = (HOJE - ativ).days if ativ else None
        if h.get("aprox") and sem_ativ is not None: dias_et = max(dias_et, sem_ativ); mais = ""  # etapa antiga: usa a última atividade real
        if et in ET_CONTRATO and dias_et >= LIM["contrato"]:
            rasc = (f"Oi! Passando para saber como está a assinatura do contrato da {nm}. Se o cliente tiver alguma dúvida, "
                    f"podemos ajudar ou marcar uma conversa rápida. Obrigada!")
            marca(ev(E, f"contrato|{d['id']}", "contrato_parado", "daniela", nm, f"{base}. " + (f"Última atividade há {sem_ativ} dias." if h.get("aprox") and sem_ativ is not None else f"Na etapa há {mais}{dias_et} dias."), "Contratos", d["id"], d.get("valor"),
                     {"rascunho": rasc if auditar(rasc) else None, "dias": dias_et}))
        if et == APRES and not h.get("aprox") and h.get("desde") == os.path.basename(arqs[-1])[8:18]:
            rev_ids.append(d["id"])
            marca(ev(E, f"diag|{d['id']}", "entrou_diagnostico", "geovana", nm, f"{base}. Entrou na etapa hoje; o Revisor já deu a segunda opinião.", "Tributário", d["id"], d.get("valor")))
        if et in ET_COMERCIAL and parado >= LIM["comercial"]:
            p = "jenifer" if d.get("pipeline") in BDR else "daniela"
            marca(ev(E, f"comercial|{d['id']}", "comercial_parado", p, nm, f"{base}. Sem movimentação há {parado} dias.", "Comercial", d["id"], d.get("valor"), {"dias": parado}))
        if et in ET_DIAG and parado >= LIM["diagnostico"]:
            marca(ev(E, f"diagparado|{d['id']}", "diagnostico_parado", "geovana", nm, f"{base}. Sem movimentação há {parado} dias.", "Tributário", d["id"], d.get("valor"), {"dias": parado}))
        if et == APRES and parado >= LIM["apresentacao"]:
            marca(ev(E, f"apres|{d['id']}", "apresentacao_parada", "daniela", nm, f"{base}. Sem movimentação há {parado} dias.", "Comercial", d["id"], d.get("valor"), {"dias": parado}))
        # cadastro: CNPJ, regime e situação oficial (Dados + Intel Comercial)
        c = re.sub(r"\D", "", x.get("cnpj") or ""); prob = []
        if not c: prob.append("sem CNPJ")
        elif not PD.cnpj_valido(c): prob.append("CNPJ com dígito inválido")
        else:
            r = PD.receita(c) or {}
            sit = (r.get("situacao") or "").strip()
            if sit and sit.lower() != "ativa": prob.append(f"CNPJ {sit.lower()} na Receita")
            if r.get("razao") and not x.get("regime"): prob.append(f"sem regime (razão oficial: {r.get('razao')})")
        if not x.get("regime") and not any("regime" in p for p in prob): prob.append("sem regime")
        if prob:
            marca(ev(E, f"crm|{d['id']}", "crm_incompleto", "daniela", nm, f"{base}. " + "; ".join(prob) + ".", "Dados", d["id"], d.get("valor")))

    # conflito de canal nos negócios novos (mesma raiz de CNPJ, outro canal, aberto ou ganho)
    if ant is not None:
        por_raiz = defaultdict(list)
        for d in N:
            c = re.sub(r"\D", "", (d.get("extras") or {}).get("cnpj") or "")
            if d.get("status") in ("aberto", "ganho") and PD.cnpj_valido(c): por_raiz[c[:8]].append(d)
        for d in abertos:
            if d["id"] in ant: continue
            c = re.sub(r"\D", "", (d.get("extras") or {}).get("cnpj") or "")
            if not PD.cnpj_valido(c): continue
            outros = [o for o in por_raiz[c[:8]] if o["id"] != d["id"] and (o.get("parceiro") or "") != (d.get("parceiro") or "")]
            if outros:
                o = sorted(outros, key=lambda o: o.get("criado") or "")[0]
                marca(ev(E, f"conflito|{d['id']}", "conflito_novo", "daniela", d.get("nome") or d["id"],
                         f"Novo negócio do parceiro {d.get('parceiro') or 'sem parceiro'}; a mesma empresa já tem negócio {o.get('status')} com {o.get('parceiro') or 'sem parceiro'} "
                         f"(criado em {(o.get('criado') or '')[:10]}). Decisão de conflito é do Luis.", "Operações de Canal", d["id"], d.get("valor"), {"cc_luis": True}))

    # parceiros sem indicação (Partner Success)
    ult = defaultdict(lambda: None); n12 = defaultdict(int)
    for d in N:
        p, cr = d.get("parceiro"), dia(d.get("criado"))
        if not p or not cr: continue
        if not ult[p] or cr > ult[p]: ult[p] = cr
        if (HOJE - cr).days <= 365: n12[p] += 1
    for p, u in ult.items():
        if "fora do roster" in p.lower() or n12[p] < 2: continue
        ritmo = 365 / n12[p]; gap = (HOJE - u).days  # inativo = o dobro do intervalo normal dele (mínimo 30 dias) ou 60+ dias
        if gap >= min(LIM["parceiro"], max(30, 2 * ritmo)):
            marca(ev(E, f"parceiro|{p}", "parceiro_inativo", "daniela", p, f"Costuma indicar a cada {ritmo:.0f} dias ({n12[p]} negócios em 12 meses); o último entrou há {gap} dias ({u.isoformat()}).",
                     "Partner Success", extra={"dias": gap}))

    execucao(N, E, marca)
    supervisao(E, marca)
    for k, e in E.items():
        if not e.pop("_visto", False) and e.get("ativo"):
            e["ativo"] = False; e["resolvido_em"] = HOJE.isoformat()
    # guarda resolvidos por 30 dias
    E = {k: e for k, e in E.items() if e.get("ativo") or (dia(e.get("resolvido_em")) or HOJE) >= HOJE - timedelta(days=30)}
    gravar(EVT, E)
    if rev_ids: revisor(rev_ids)
    at = [e for e in E.values() if e.get("ativo")]
    print(f"eventos ativos: {len(at)} · novos hoje: {sum(1 for e in at if novo(e))} · revisor: {len(rev_ids)} negócio(s)")


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
        if (st == "responder" and (h >= 24 or idade >= 1)) or (st == "acompanhar" and idade >= 3):
            marca(ev(E, f"demanda|{d['id']}", "demanda_atrasada", d.get("pessoa") or "daniela", f"{d['id']} · {d.get('titulo')}",
                     f"{d.get('o_que_pede') or ''} Status: {st}, aberta em {(d.get('aberta_em') or '')[:10]}. Próximo passo: {d.get('proximo_passo') or 'definir'}.", "Supervisor"))
    # chamados propostos e pedidos da Central esperando decisão
    agora = datetime.now()
    for k, c in ler(os.path.join(REG, "chamados-propostos.json"), {}).items():
        try: t = datetime.fromisoformat(c.get("proposto_em"))
        except Exception: continue
        if c.get("status") == "proposto" and (agora - t).total_seconds() / 3600 >= LIM["aprovacao_h"]:
            marca(ev(E, f"aprov|chamado|{k}", "aprovacao_parada", c.get("pessoa") or "daniela", c.get("titulo") or k,
                     f"Chamado proposto para {c.get('grupo')} em {c['proposto_em'][:10]} aguarda aprovação no painel.", "Supervisor"))
    for k, p in ler(os.path.join(AP, "central-agentes/registro.json"), {}).get("pedidos", {}).items():
        if p.get("status") != "aguardando_aprovacao": continue
        t = dia(p.get("respondido") or p.get("recebido"))
        if t and (HOJE - t).days >= 1:
            marca(ev(E, f"aprov|pedido|{k}", "aprovacao_parada", p.get("pessoa") or "luis", f"{k} · {(p.get('assunto') or '')[:80]}",
                     f"Resposta entregue em {str(p.get('recebido'))[:10]}; falta Aprovado, Não aprovado ou Nova análise.", "Supervisor"))
    # rotinas com erro hoje
    log = os.path.join(AP, "logs/partners.log")
    erros = {}
    if os.path.exists(log):
        for l in open(log, errors="ignore"):
            if l.startswith(HOJE.isoformat()) and "ERRO" in l:
                m = re.search(r"\[(.+?)\] (.*)", l)
                if m: erros[m.group(1)] = m.group(2)
            elif l.startswith(HOJE.isoformat()):
                m = re.search(r"\[(.+?)\] ok", l)
                if m: erros.pop(m.group(1), None)  # voltou a rodar bem depois do erro
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


def plano(previa=False, so_urgentes=False):
    import email_layout as L
    E = ler(EVT, {}); at = [e for e in E.values() if e.get("ativo")]
    est = ler(os.path.join(REG, "plano-enviado.json"), {})
    for p, (nome, email) in PESSOAS.items():
        meus = [e for e in at if e["pessoa"] == p or (p == "luis" and e.get("cc_luis"))]
        if so_urgentes:
            ja = set(est.get(f"avisados|{p}", []))
            meus = [e for e in meus if e["tipo"] in URGENTE and novo(e) and f"{e['tipo']}|{e['titulo']}" not in ja]
            if not meus: continue
        novos = [e for e in meus if novo(e)]
        por = defaultdict(list)
        for e in sorted(meus, key=_ord): por[e["tipo"]].append(e)
        linhas = [L.cabecalho("Área Partners · Agentes", "Aviso da tarde" if so_urgentes else "Plano do dia", f"{nome} · {HOJE.strftime('%d/%m/%Y')}")]
        if not so_urgentes:
            linhas.append(L.paragrafo(f"Bom dia, {nome}. Os agentes já cruzaram HubSpot, WhatsApp, Central e GLPI. Abaixo, o que pede a sua ação hoje, "
                                      "com o que eles já adiantaram. Nada foi enviado a parceiro ou cliente nem alterado no CRM.", "28px 32px 12px"))
            linhas.append(L.kpis([("Novos hoje", str(len(novos)), "desde ontem"), ("Pendências", str(len(meus)), "ativas"),
                                  ("Urgentes", str(sum(1 for e in meus if e["tipo"] in URGENTE)), "olhar primeiro")]))
        if p == "luis" and not so_urgentes:
            linhas += quadro_supervisor(L, at)
        if not meus and not (p == "luis" and not so_urgentes):
            continue
        if not so_urgentes and not previa and est.get(f"plano|{p}") == HOJE.isoformat():
            print(p, "plano de hoje já enviado"); continue
        ordem = ["rotina_falhou", "conflito_novo", "demanda_atrasada", "aprovacao_parada", "entrou_diagnostico", "contrato_parado", "ganho_sem_execucao", "execucao_parada",
                 "diagnostico_parado", "comercial_parado", "apresentacao_parada", "crm_incompleto", "parceiro_inativo"]
        for t in ordem:
            xs = por.get(t)
            if not xs: continue
            n_nov = sum(1 for e in xs if novo(e))
            linhas.append(L.secao(f"{NOME[t]} · {len(xs)}" + (f" ({n_nov} novo{'s' if n_nov > 1 else ''})" if n_nov else "")))
            lim = 6 if t in ("crm_incompleto", "apresentacao_parada", "comercial_parado") else 10
            for e in xs[:lim]:
                ls = [("Situação", L.esc(e["texto"]))]
                if e.get("revisor"): ls.append(("Revisor", L.esc(e["revisor"])))
                if e.get("rascunho"): ls.append(("Rascunho para o parceiro", "<i>" + L.esc(e["rascunho"]) + "</i> (revisado pela Qualidade; você decide se envia)"))
                if e.get("valor"): ls.append(("Valor no CRM", f"R$ {e['valor']:,.0f}".replace(",", ".")))
                ls.append(("Desde", L.esc(e["primeiro"][8:10] + "/" + e["primeiro"][5:7]) + (" · <b>novo</b>" if novo(e) else "")))
                linhas.append(L.cartao(e["titulo"], e["depto"], ls, "#b3261e" if t in URGENTE else L.OURO, e.get("link")))
            if len(xs) > lim:
                linhas.append(L.paragrafo(f"E mais {len(xs) - lim}. A lista completa está no painel e em registro/eventos.json."))
        linhas.append(L.rodape("Plano montado pelos agentes da Área Partners às " + datetime.now().strftime("%Hh%M")
                               + ". Quando a situação se resolve no HubSpot, o item sai sozinho do plano do dia seguinte."))
        corpo = L.documento(*linhas)
        assunto = f"[Agentes] {'Aviso da tarde' if so_urgentes else 'Plano do dia'} · {nome} · {HOJE.strftime('%d/%m')}"
        if previa:
            f = os.path.join(tempfile.gettempdir(), f"plano-{p}.html"); open(f, "w").write(corpo); print(p, len(meus), "→", f); continue
        ok, msg = L.outlook([email], [], assunto, corpo, enviar=True)
        print(p, len(meus), "enviado" if ok else f"FALHOU {msg}")
        if ok and not so_urgentes: est[f"plano|{p}"] = HOJE.isoformat()
        if ok and so_urgentes:
            est.setdefault(f"avisados|{p}", []).extend(f"{e['tipo']}|{e['titulo']}" for e in meus)
    if not previa: gravar(os.path.join(REG, "plano-enviado.json"), est)


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
    return linhas


def resumo():
    E = ler(EVT, {}); at = [e for e in E.values() if e.get("ativo")]
    c = defaultdict(int)
    for e in at: c[(e["pessoa"], e["tipo"])] += 1
    for (p, t), n in sorted(c.items()): print(f"{p:8} {NOME[t]:42} {n}")
    print("total ativos:", len(at))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["sentinelas", "plano", "avisos", "resumo"]); ap.add_argument("--previa", action="store_true")
    a = ap.parse_args()
    {"sentinelas": sentinelas, "resumo": resumo}.get(a.cmd, lambda: plano(a.previa, a.cmd == "avisos"))()
