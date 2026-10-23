"""Dossiê-base instantâneo: monta o dossiê da empresa em milissegundos, sem chamar o Claude.

Junta o retrato da Receita (perfil do pedido) com o conhecimento já curado dos agentes: playbook do setor
(skills/depto-solucoes/references/playbooks-setoriais.md), esteira, objeções e perguntas de diagnóstico
(skills/celula-jenifer/references/especialistas/objecoes-tecnicas.md) e biblioteca de cases. Os agentes da nuvem
(rotinas/esteira-parceiro.md) aprofundam depois; o parceiro já recebe esta versão na hora.

Tudo o que sai daqui passa pelo mesmo portão do auditor de promessas. Fica FORA: dado interno (número da base de
clientes, tickets, nome de Master, código de decisão D##), produto em validação com condição, valor, prazo e êxito.
"""
import json, re
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
PLAYBOOK = RAIZ / "skills/depto-solucoes/references/playbooks-setoriais.md"
OBJECOES = RAIZ / "skills/celula-jenifer/references/especialistas/objecoes-tecnicas.md"
CASES = RAIZ / "departamentos/tributario/apresentacao-diagnostico/biblioteca-cases/cases.json"

# espelha mapa_conta.SETORES (cluster pelo CNAE de 4 dígitos); o número é o da seção do playbook
SETORES = [(1, "Proteína animal", ("1011", "1012", "1013", "4634", "4722")), (2, "Café e grãos", ("4621", "4622", "4623", "1061", "1081")),
           (3, "Varejo alimentar", ("4711", "4712", "4721", "4724", "4729", "4633", "4637", "4639", "4691")),
           (4, "Combustíveis e GLP", ("4731", "4732", "4681", "4682", "4784")),
           (5, "Confecção e têxtil", ("1311", "1321", "1330", "1340", "1351", "1352", "1353", "1354", "1359", "1411", "1412", "1413", "1414", "1421", "1422",
                                      "1531", "1532", "1533", "1539", "1540")),
           (6, "Transporte de carga", ("4930", "5211", "5212", "5250")),
           (7, "Panificação e alimentos", ("1091", "1092", "1093", "1094", "1095", "1096", "1099", "1052", "1053"))]
SEGMENTO_CASE = {1: "alimenticio", 2: "agro", 3: "alimenticio", 4: None, 5: "industria", 6: "transporte", 7: "alimenticio"}
NIVEL = {"alta": 3, "média": 2, "media": 2, "baixa": 1, "não": 0, "nao": 0}
OBJECOES_ESCOLHIDAS = ("contador", "receita", "alíquota zero", "outra empresa", "2027", "quanto vou", "senha")
# resposta própria quando a do playbook promete demais ou generaliza (o texto-fonte não é editado aqui)
OBJECOES_TEXTO = {
    "receita": "Cada tese tem um grau de risco que o técnico explica antes de qualquer pedido. Nas teses mais controvertidas pedimos ressarcimento (PER): a Receita analisa antes de pagar, sem compensação automática.",
    "2027": "O saldo de crédito já escriturado tem regra de transição na LC 214/2025 (art. 378), com data-limite para escrituração e retificação em 2026. O técnico confere o que se aplica à empresa.",
    "alíquota zero": "A Receita tem posição contrária e o STJ está julgando o tema. Por isso o técnico mostra o risco, o caminho conservador e o que tem previsão em lei (Lei 11.033/2004, art. 17), antes de qualquer pedido.",
}
_cache = {}

# CNAEs (4 dígitos) em que a tese de alíquota zero na aquisição não se aplica: mercado e supermercado, café (catálogo, regra da casa)
# e revenda de monofásico (STJ Tema 1.093: combustível, GLP, farma, autopeças, bebidas frias).
VEDA_ALIQ_ZERO = ("4711", "4712", "4713", "4621", "1081", "4731", "4732", "4784", "4681", "4682", "4771", "4530", "4635")
SO_REAL = re.compile(r"alíquota zero|insumos?\b|conta gráfica|\bIPI\b|crédito presumido de (?:compras de )?PF|inclusão do ICMS nos créditos|ACT/CCT", re.I)
SO_NAO_SIMPLES = re.compile(r"exclusão do ICMS|exclusão ICMS|ICMS da base|ICMS-ST da base|CPP|própria base|crédito presumido de ICMS", re.I)
FORA_DA_VITRINE = re.compile(r"sistema s|\biss\b|ICMS fora do PIS|PIS/COFINS fora da base do IRPJ", re.I)
# o que não vai ao parceiro: dado interno, produto em validação com condição, número e valor (a trava de regex do backend barra % e R$)
VAZA = re.compile(r"\b831\b|\bMasters?\b|piloto|bloquead|escrow|venda gerencial|ticket|honor[aá]rio|deságio|\bfee\b|comiss|Junior|João Mattos|"
                  r"sem fonte primária|fraude|\bG[0-4]\b|\bD\d{2,3}\b|%|R\$|US\$|\bSelic\b", re.I)
FUNRURAL = ("Funrural: a revisão de períodos anteriores a 2018 está em análise após a ADI 4.395 (STF, 15/10/2026). A modulação dos efeitos ainda não foi decidida "
            "e o acórdão não foi publicado, então não há promessa de recuperação. O caminho provável é revisão de passivo e de processos, a confirmar pelo técnico e pelo Jurídico.")


def cluster(cnae):
    c4 = str(cnae or "")[:4]
    return next(((n, nome) for n, nome, cs in SETORES if c4 in cs), (None, None))


def _limpa(t):
    t = str(t)
    t = re.sub(r"(?i)faturamento\s*[>≥]\s*R\$\s*[\d.,]+\s*(?:mil|mi|milhões|bi)?(?:/mês|/ano)?", "faturamento relevante", t)
    t = re.sub(r"(?i)(?<=\w)\s+[>≥]\s*R\$\s*[\d.,]+\s*(?:mil|mi|milhões|bi)?(?:/mês|/ano)?", ", volume relevante", t)
    t = re.sub(r"(?i)[>≥]\s*R\$\s*[\d.,]+\s*(?:mil|mi|milhões|bi)?(?:/mês|/ano)?", "volume relevante", t)
    t = re.sub(r"\s*\((?:[^()]*\b)?D\d{2,3}\b[^()]*\)", "", t)        # (D59), (decisão D83 ...)
    t = re.sub(r"\bD\d{2,3}\b[,;]?\s*", "", t)
    t = re.sub(r"`[^`]*depto-[^`]*`", "a área técnica", t)
    t = re.sub(r"\bCI\b", "Crédito Internacional (em validação, só descoberta)", t)
    t = re.sub(r"\bRT\b:?", "Recuperação tributária:", t)
    t = t.replace("**", "").replace("`", "").replace("RT: ", "Recuperação tributária: ")
    t = t.replace("em poucos dias", "a curto prazo").replace(" (D+30)", "").replace("pós-Carbono Oculto", "no setor").replace("Carbono Oculto", "o setor")
    t = re.sub(r"(?i)\bno parecer\b", "no diagnóstico", t)
    t = re.sub(r"(?i)\bparecer\b", "diagnóstico", t)
    t = re.sub(r"\bO Tributário\b", "O técnico", t)
    t = t.replace("Porta de entrada barata", "Porta de entrada")
    t = re.sub(r",?\s*depois do G2", "", t)
    t = t.replace("A janela de recuperação das competências de PIS/COFINS fecha com a extinção em 2027.",
                  "O saldo de crédito escriturado segue na transição de 2027 (LC 214/2025, art. 378).")
    return re.sub(r"\s{2,}", " ", t).strip(" ;,")


def _sem_num(t):
    """Tira as frases com número de resultado (% ou R$) do texto do playbook."""
    return " ".join(f for f in re.split(r"(?<=[.;])\s+", t) if not re.search(r"%|R\$|US\$", f)).strip()


def _playbook():
    if "pb" not in _cache:
        txt = PLAYBOOK.read_text(encoding="utf-8")
        data = re.search(r"Data-base:\*\* ([\d/]+)", txt)
        partes = re.split(r"\n## (\d)\. ", txt)
        sec = {}
        for i in range(1, len(partes) - 1, 2):
            subs = {}
            for s in re.split(r"\n### ", partes[i + 1]):
                titulo, _, corpo = s.partition("\n")
                subs[titulo.strip()] = corpo
            sec[int(partes[i])] = subs
        _cache["pb"] = (sec, data.group(1) if data else "")
    return _cache["pb"]


def _ok(t):
    return bool(t) and not VAZA.search(t) and "não localizad" not in t.lower()


def _bullets(corpo, n=5):
    itens = [_limpa(l[2:]) for l in (corpo or "").splitlines() if l.startswith("- ")]
    return [i for i in itens if _ok(i)][:n]


def _numerados(corpo):
    itens = [_limpa(re.sub(r"^\d+\.\s*", "", l)) for l in (corpo or "").splitlines() if re.match(r"^\d+\.\s", l)]
    return [i for i in itens if _ok(i)]


def _tabela(corpo):
    linhas = [l for l in (corpo or "").splitlines() if l.startswith("|")]
    if len(linhas) < 3:
        return [], []
    cel = lambda l: [c.strip() for c in l.strip().strip("|").split("|")]
    return cel(linhas[0]), [cel(l) for l in linhas[2:]]


def _servicos(corpo):
    """Linhas com aderência alta ou média: (produto, nivel, motivo). Com várias colunas de subsetor, vale a melhor."""
    _, linhas = _tabela(corpo)
    out = []
    for r in linhas:
        niveis = [NIVEL.get(re.split(r"[ (:,]", c.lower().strip())[0], -1) for c in r[1:-1]]
        n = max(niveis, default=-1)
        if n >= 2 and len(r) >= 3:
            out.append((_limpa(r[0]), "alta" if n == 3 else "média", _sem_num(_limpa(r[-1]))))
    return out


def _filtra_servicos(servicos, real, regime_desconhecido, simples, veda_aliq):
    """Aplica as regras do catálogo ao mapa do playbook. Devolve (produto, nivel, motivo, so_se_real)."""
    out = []
    for p, niv, mot in servicos:
        pl = p.lower()
        if FORA_DA_VITRINE.search(p) or not _ok(p):
            continue
        if "funrural" in pl:
            out.append(("Funrural", niv, FUNRURAL.split(": ", 1)[1], False)); continue
        if re.search(r"fidc|crédito internacional|maquila", pl):
            desc = "apenas como descoberta (em validação), sem condição" if re.search(r"crédito internacional|maquila", pl) else "depende da carteira de recebíveis; a elegibilidade é avaliada pela Save Invest"
            out.append((p, niv, desc, False)); continue
        if "alíquota zero" in pl:
            if veda_aliq or not (real or regime_desconhecido):
                continue
            mot = re.sub(r"(?i)\s*Simples: não\.?", "", mot).replace("Real ou Presumido", "Lucro Real")
            mot = (mot.rstrip(". ") + ". Tese controvertida (posição contrária da Receita; tema em julgamento no STJ). "
                   "A LC 224/2025 (art. 4º) trouxe vedação nova a partir de 01/04/2026, e o técnico separa os períodos antes e depois. Pedido sempre por ressarcimento (PER), nunca por compensação (DCOMP).")
            out.append((p, niv, mot, regime_desconhecido and not real)); continue
        so_real = bool(SO_REAL.search(p))
        if so_real and not real and not regime_desconhecido:
            continue
        if simples and SO_NAO_SIMPLES.search(p):
            continue
        if "inclusão do icms nos créditos" in pl:
            mot = mot.rstrip(". ") + ". Tese controvertida, só pela via judicial."
        out.append((p, niv, mot, so_real and regime_desconhecido and not real))
    return out


def _linha_onda(txt, real, desconhecido, simples, veda_aliq):
    """Filtra os passos da onda (separados por →) conforme regime e restrições. Devolve '' se nada sobrar."""
    t = _limpa(txt)
    ret = not (real or desconhecido)
    if ret or veda_aliq:
        t = re.sub(r"\s*ou alíquota zero \(grãos\)", "", t)
    t = re.sub(r"^(Insumos e )(ICMS)", r"\2", t)
    t = re.sub(r"(Funrural)", "revisão de Funrural anterior a 2018 (em análise, sem promessa)", t)
    t = re.sub(r"\(descoberta\)", "(descoberta, sem condição)", t)
    t = re.sub(r"(\(em validação, só descoberta\))\s*\([^)]*\)", r"\1", t)
    frases = []
    for f in re.split(r"(?<=\))\.\s+|\.\s+(?=[A-Z])", t):
        rotulo = re.match(r"^[A-Za-zçãé ]+: ", f)
        if rotulo and "alíquota zero" in f and (veda_aliq or ret):
            continue
        passos = [x for x in f.split(" → ")]
        if veda_aliq:
            passos = [x for x in passos if "alíquota zero" not in x]
        if ret:
            passos = [x for x in passos if not SO_REAL.search(x)]
        if simples:
            passos = [x for x in passos if not SO_NAO_SIMPLES.search(x)]
        if rotulo and passos and passos[0].strip() == rotulo.group(0).strip(" :"):
            passos = []
        if passos:
            frases.append(" → ".join(passos).strip(" ."))
    return ". ".join(frases)


def _brl(v):
    v = float(v or 0)
    if v >= 1e9: return "R$ %s bilhões" % ("%.1f" % (v / 1e9)).replace(".", ",")
    if v >= 1e6: return "R$ %s milhões" % ("%.1f" % (v / 1e6)).replace(".", ",").replace(",0", "")
    return "R$ {:,.0f}".format(v).replace(",", ".")


def _data(iso):
    try:
        a, m, d = str(iso)[:10].split("-"); return "%s/%s/%s" % (d, m, a)
    except ValueError:
        return str(iso or "")


def _regime(ecf):
    """('texto', primeiro ano do último bloco Real | None, anos fora do Real)."""
    anos = sorted((x["ano"], str(x["forma"]).title()) for x in ecf if x.get("ano") and x.get("forma"))
    if not anos:
        return "sem ECF publicada", None, []
    resumo, i = [], 0
    while i < len(anos):
        j = i
        while j + 1 < len(anos) and anos[j + 1][1] == anos[i][1]: j += 1
        resumo.append("%s em %s" % (anos[i][1], anos[i][0] if i == j else "%s a %s" % (anos[i][0], anos[j][0]))); i = j + 1
    desde = None
    for a, f in reversed(anos):  # o bloco Real mais recente: do último ano para trás, enquanto for Real
        if "Real" not in f: break
        desde = a
    fora = [a for a, f in anos if desde and a < desde and "Real" not in f]
    return "; ".join(resumo), desde, fora


def _case(n):
    seg = SEGMENTO_CASE.get(n)
    try:
        cs = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
    except (OSError, ValueError, KeyError):
        cs = []
    return [c for c in cs if c.get("segmento") == seg and c.get("aprovado") and c.get("autorizacao_uso")]


def _objecoes(real, desconhecido, veda_aliq):
    txt = OBJECOES.read_text(encoding="utf-8")
    bloco = txt.split("### Objeções por tese (recuperação)")[1].split("### Objeções por produto")[0]
    cab, linhas = _tabela(bloco)
    ir = next((k for k, c in enumerate(cab) if c.lower().startswith("resposta")), 3)
    out = []
    for chave in OBJECOES_ESCOLHIDAS:
        if chave == "alíquota zero" and (veda_aliq or not (real or desconhecido)): continue
        if chave == "2027" and not (real or desconhecido): continue
        r = next((r for r in linhas if chave in r[0].lower()), None)
        if r and len(r) >= 5:
            resp = OBJECOES_TEXTO.get(chave) or _limpa(r[ir]).strip('"')
            if _ok(resp) and resp: out.append("%s Resposta: %s" % (_limpa(r[0]), resp))
    return out


def _perguntas():
    txt = OBJECOES.read_text(encoding="utf-8")
    p = _numerados(txt.split("## 6. Perguntas de diagnóstico")[1].split("## 7.")[0])
    return p[:8]


def montar(perfil, faixa, hoje=None):
    """Resultado completo (fazer, precisa, falta, esteira, dossie) a partir do perfil da Receita e da faixa de regime."""
    hoje = hoje or date.today()
    perfil = perfil or {}
    ecf = [x for x in (perfil.get("ecf") or []) if isinstance(x, dict)]
    razao = perfil.get("razao") or "a empresa"
    cn = (perfil.get("cnae") or {})
    cod = str(cn.get("codigo") or "")
    n, nome_cluster = cluster(cod)
    sec, data_pb = _playbook()
    pb = sec.get(n, {}) if n else {}
    reg_txt, desde, fora = _regime(ecf)
    confirmado = faixa == "confirmado_real"
    real = faixa in ("confirmado_real", "provavel_real")
    desconhecido = faixa not in ("confirmado_real", "provavel_real", "nao_real")
    simples = faixa == "nao_real" and not ecf          # sem ECF e fora do Real: Simples ou MEI (a ECF não existe para eles)
    veda_aliq = cod[:4] in VEDA_ALIQ_ZERO or "café" in str(cn.get("descricao") or "").lower() or "supermercado" in str(cn.get("descricao") or "").lower()
    cidade = ("%s/%s" % (str(perfil.get("municipio") or "").title(), perfil.get("uf") or "")).strip("/") if perfil.get("municipio") else (perfil.get("uf") or "")
    servicos = _filtra_servicos(_servicos(pb.get("Mapa de aderência")), real, desconhecido, simples, veda_aliq) if n else []
    altas = [x for x in servicos if x[1] == "alta" and not x[3]]
    aderencia = ("alta" if confirmado and altas else "média" if real or (faixa == "nao_real" and servicos) else "a confirmar")
    regime_frase = ("Está no %s (ano-base %s)" % ((max(ecf, key=lambda x: x.get("ano") or 0).get("forma") or "").title(), max(x.get("ano") or 0 for x in ecf)) if (real and ecf)
                    else "Regime na ECF: " + reg_txt)

    # 1. resumo
    quem = "%s%s, no setor %s" % (razao.title() if razao.isupper() else razao, (", em " + cidade) if cidade else "", (nome_cluster or "fora dos clusters do playbook").lower())
    resumo = ["%s. %s%s." % (quem, regime_frase, " (provável, a confirmar com a empresa)" if faixa == "provavel_real" else "")]
    resumo.append("Aderência %s para a esteira da Save. %s" % (aderencia, (
        "No Lucro Real é possível verificar PIS/COFINS não cumulativo e as teses do ICMS na base; a análise dos arquivos da empresa diz se há crédito, de que tipo e por qual caminho."
        if real else "As teses de PIS/COFINS sobre insumos exigem o Lucro Real (Leis 10.637/2002 e 10.833/2003, art. 3º); confirme o regime antes de seguir. Planejamento e produtos financeiros seguem possíveis."
        if not simples else "No Simples Nacional a apuração é pelo DAS e as teses de crédito de PIS/COFINS não se aplicam; o ponto de partida são planejamento, passivo e produtos financeiros.")))
    # 2. retrato
    forma = ", ".join(x for x in ((perfil.get("natureza_juridica") or "").lower(), ) if x)
    retrato = ["%s. %s%s%s." % (razao, "Matriz" if perfil.get("matriz") else "Filial", (", " + forma) if forma else "",
                                (", início de atividade em " + _data(perfil.get("inicio_atividade"))) if perfil.get("inicio_atividade") else ""),
               "Atividade principal: %s (CNAE %s)%s." % ((cn.get("descricao") or "não informada").lower(), cod or "não informado",
                                                         ". Secundárias: " + "; ".join((x.get("descricao") or "").lower() for x in (perfil.get("cnaes_secundarios") or [])[:6]) if perfil.get("cnaes_secundarios") else ""),
               "Porte na Receita: %s.%s" % (perfil.get("porte") or "não informado", (" Capital social: %s." % _brl(perfil["capital_social"])) if perfil.get("capital_social") else ""),
               "Regime na ECF: %s. Fonte: Minha Receita (dados da ECF), consultada em %s. O regime da ECF é o do ano-base, não necessariamente o de hoje." % (reg_txt, hoje.strftime("%d/%m/%Y")),
               "Não está no retrato porque a consulta pública não traz: faturamento, folha, produtos por NCM e situação de débitos. Esses dados entram na primeira conversa."]
    if desde and fora:
        retrato.insert(3, "A empresa mudou para o Lucro Real em %s (antes: %s). A análise de insumos vale só para as competências no Real, e o ano da mudança pode ter competências nos dois regimes. "
                          "A janela padrão é de cinco anos retroativos ao pedido (CTN, art. 168)." % (desde, ", ".join(str(a) for a in fora)))
    # 3. setor
    setor_p = ["Fontes do playbook do setor, consultadas em %s." % (data_pb or "data não informada")] if n else ["Este CNAE ainda não tem playbook setorial. Os agentes aprofundam a leitura do setor na análise seguinte."]
    setor_i = ([_sem_num(x) for x in _bullets(pb.get("Retrato do setor em 2026"), 8)][:4] + _bullets(pb.get("Mudanças regulatórias e tributárias 2025–2027"), 3)
               + ["Dor frequente: " + d for d in _numerados(pb.get("Dores do CFO/dono (top 5)"))[:5]]
               + ["Gatilho de conversa: " + g for g in _bullets(pb.get("Gatilhos de compra"), 5)]) if n else []
    setor_i = [x for x in setor_i if x]
    # 4. serviços
    if servicos:
        serv_i = []
        for p_, niv, mot, so_real in servicos:
            if re.search(r"crédito internacional|maquila", p_.lower()):
                serv_i.append("%s: %s." % (p_, mot)); continue
            rot = "se a empresa estiver no Lucro Real" if so_real else "aderência %s" % niv
            serv_i.append("%s (%s): %s" % (p_, rot, mot))
    else:
        serv_i = ["Planejamento tributário e reforma (CBS/IBS), com o mapa do mix de produtos por NCM.",
                  "Gestão de Contas e antecipação de recebíveis, com a Save Invest, se a empresa vende a prazo."]
        if real or desconhecido:
            serv_i.insert(0, "Recuperação tributária: PIS/COFINS sobre insumos e exclusão do ICMS da base%s (aderência a confirmar pelo regime e pelo faturamento)." % (" se Lucro Real" if desconhecido else ""))
        elif not simples:
            serv_i.insert(0, "Recuperação tributária: exclusão do ICMS da base do PIS/COFINS, se houver faturamento relevante (aderência a confirmar).")
    serv_p = ["As teses são prováveis, não confirmadas. Só o diagnóstico sobre os arquivos da empresa diz se existe crédito, de que tipo e por qual caminho. Nada aqui é estimativa de valor."]
    if desconhecido:
        serv_p.append("Como o regime não foi localizado, as linhas que exigem o Lucro Real aparecem condicionadas à confirmação.")
    elif not real:
        serv_p.append("As linhas de PIS/COFINS sobre insumos e aquisições exigem o Lucro Real e não aparecem como oferta para este regime." + (
            " No Simples Nacional a apuração é pelo DAS; o técnico verifica a viabilidade de cada linha." if simples else
            " Com o regime atual, o ponto de partida são o ICMS na base, a folha e o planejamento."))
    # 5. esteira
    cab, linhas = _tabela(pb.get("Esteira em 3 ondas")) if n else ([], [])
    ondas = []
    for r in linhas:
        if len(r) < 3: continue
        txt = _linha_onda(r[1], real, desconhecido, simples, veda_aliq)
        if not txt: continue
        valida = bool(re.search(r"crédito internacional|maquila", txt.lower()))
        dep = "avaliação do responsável pelo produto" if valida else _limpa(r[2])
        ondas.append((r[0], txt, dep, valida))
    est_i = ["%s: %s. Depende de %s." % (r0 if r0.lower().startswith("onda") else "Onda " + r0, t, d) for r0, t, d, _ in ondas] or [
        "Onda 1, destravar caixa: %s." % ("recuperação de insumos e do ICMS da base; Gestão de Contas" if real or desconhecido else "ICMS da base, quando couber; Gestão de Contas"),
        "Onda 2, proteger e controlar: planejamento da reforma; antecipação; passivo se houver.", "Onda 3, crescer: funding apenas como descoberta."]
    est_i.append("Regras de sequência: passivo antes de crédito novo; no máximo dois produtos novos por vez; a reforma de 2027 dá urgência à onda 1; produto em validação só como descoberta.")
    # 6. cases
    cs = _case(n) if n else []
    cs = [c for c in cs if _ok(str(c.get("resumo_cliente") or ""))]
    if cs:
        cases_p = ["%s Resultados passados não garantem resultado futuro." % c["resumo_cliente"] for c in cs[:2]]
    else:
        cases_p = ["A biblioteca de cases ainda não tem case aprovado para este segmento, então este dossiê não cita valor de cliente.",
                   "O que o parceiro pode mostrar hoje é o método: análise da EFD-Contribuições dos últimos cinco anos; pedido de ressarcimento pelo caminho conservador; acompanhamento pela procuração eletrônica no e-CAC, sem uso de senha; conferência do técnico antes de qualquer pedido à Receita. Resultados passados não garantem resultado futuro."]
    # 7. abordagem
    if desde and fora and nome_cluster:
        sinal = "a empresa migrou para o Lucro Real em %s e opera no setor %s" % (desde, nome_cluster.lower())
    elif real:
        sinal = "a empresa declara Lucro Real e opera em %s" % (cn.get("descricao") or "seu setor").lower()
    else:
        sinal = "a empresa opera em %s" % (cn.get("descricao") or "seu setor").lower()
    gancho = ("Em 2027 cada produto terá regra própria na reforma, e a LC 214/2025 (art. 378) trata dos saldos de PIS/COFINS na transição."
              if real or desconhecido else "Em 2027 cada produto terá regra própria na reforma, e o regime da empresa muda a forma de se preparar.")
    abord_p = ["Quem procurar: o sócio-administrador ou o CFO. O contador entra como aliado, depois da primeira conversa.",
               "Abertura sugerida, a partir de um sinal real: \"Vimos que %s. %s Podemos conversar 30 minutos sobre como empresas do setor estão se preparando?\"" % (sinal, gancho),
               "Objetivo da primeira conversa: qualificar e sair com a EFD-Contribuições agendada. Não falar de valor, percentual, prazo de êxito nem nome de cliente."]
    abord_i = ["Pergunta-chave: " + q for q in _perguntas()] + _objecoes(real, desconhecido, veda_aliq) + [
        "Escalar ao técnico se o cliente citar autuação, despacho decisório ou intimação, compensação já feita por terceiro, decisão judicial própria ou pedir estimativa.",
        "Próximo passo e documentos a pedir: EFD-Contribuições e EFD ICMS/IPI dos últimos cinco anos, ECF, relatório de compras por NCM, folha de pagamento e procuração eletrônica no e-CAC."]
    falta = ["Faturamento mensal, perfil de compras e produtos por NCM: a empresa, pelo parceiro.",
             "EFD-Contribuições, EFD ICMS/IPI e ECF dos últimos cinco anos: o cliente, pedidos pelo parceiro.",
             "Débitos, certidão e parcelamentos: o cliente e a consulta ao e-CAC por procuração.",
             "Confirmação do regime de %s e %s: o cliente, na primeira conversa." % (hoje.year - 1, hoje.year)]
    dossie = [
        {"titulo": "Resumo e aderência", "paragrafos": resumo},
        {"titulo": "Retrato da empresa", "itens": retrato},
        {"titulo": "Setor e dores prováveis", "paragrafos": setor_p, "itens": setor_i} if (setor_i or setor_p) else None,
        {"titulo": "Como a Save pode ajudar: serviços aderentes", "paragrafos": serv_p, "itens": serv_i},
        {"titulo": "Esteira em três ondas", "itens": est_i},
        {"titulo": "Cases e prova", "paragrafos": cases_p},
        {"titulo": "Como abordar", "paragrafos": abord_p, "itens": abord_i},
        {"titulo": "O que falta e quem fornece", "itens": falta},
        {"titulo": "Avisos", "paragrafos": [
            "Informação de apoio para a conversa comercial. Não é promessa de valor, de prazo nem de êxito, e não substitui a análise técnica sobre os documentos da empresa.",
            "Dossiê gerado automaticamente a partir da consulta pública e do conhecimento da Save; os agentes aprofundam a análise em seguida. O regime da ECF é o do ano-base indicado. Consulta de %s." % hoje.strftime("%d/%m/%Y")]}]
    precisa = ("A reforma muda a regra de cada produto em 2027; a LC 214/2025 (art. 378) trata da transição dos saldos de PIS/COFINS, e o técnico confere o que se aplica à empresa." if real or desconhecido
               else "A reforma muda a regra de cada produto em 2027, e o regime da empresa define como se preparar.")
    if desde and fora:
        precisa += " A empresa mudou para o Lucro Real em %s: a janela padrão é de cinco anos retroativos ao pedido (CTN, art. 168)." % desde
    return {"fazer": " ".join(resumo) + " Próximo passo: conversa de 30 minutos com o sócio ou o CFO e pedido da EFD-Contribuições dos últimos cinco anos.",
            "precisa": precisa, "falta": " ".join(falta[:3]),
            "esteira": [{"onda": int(re.sub(r"\D", "", r0)[:1] or 1), "produto": t, "status": "descoberta" if v else "pronto",
                         "nota": "Depende de " + d + "."} for r0, t, d, v in ondas][:6],
            "dossie": [x for x in dossie if x], "nivel": "base"}
