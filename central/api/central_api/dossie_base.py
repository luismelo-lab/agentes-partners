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
OBJECOES_ESCOLHIDAS = ("contador", "receita", "outra empresa", "2027", "quanto vou", "senha")
_cache = {}


def cluster(cnae):
    c4 = str(cnae or "")[:4]
    return next(((n, nome) for n, nome, cs in SETORES if c4 in cs), (None, None))


def _limpa(t):
    t = re.sub(r"\s*\((?:[^()]*\b)?D\d{2,3}\b[^()]*\)", "", str(t))        # (D59), (decisão D83 ...)
    t = re.sub(r"\bD\d{2,3}\b[,;]?\s*", "", t)
    t = re.sub(r"`[^`]*depto-[^`]*`", "a área técnica", t)
    t = re.sub(r"\bCI\b", "Crédito Internacional (em validação, só descoberta)", t)
    t = t.replace("**", "").replace("`", "").replace("RT: ", "Recuperação tributária: ")
    return re.sub(r"\s{2,}", " ", t).strip(" ;,")


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


def _bullets(corpo, n=5):
    itens = [_limpa(l[2:]) for l in (corpo or "").splitlines() if l.startswith("- ")]
    return [i for i in itens if i and "não localizad" not in i.lower()][:n]


def _numerados(corpo):
    return [_limpa(re.sub(r"^\d+\.\s*", "", l)) for l in (corpo or "").splitlines() if re.match(r"^\d+\.\s", l)]


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
            out.append((_limpa(r[0]), "alta" if n == 3 else "média", _limpa(r[-1])))
    return out


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
    anos = sorted((x["ano"], x["forma"].title()) for x in ecf if x.get("ano") and x.get("forma"))
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


def _objecoes():
    txt = OBJECOES.read_text(encoding="utf-8")
    bloco = txt.split("### Objeções por tese (recuperação)")[1].split("### Objeções por produto")[0]
    _, linhas = _tabela(bloco)
    out = []
    for chave in OBJECOES_ESCOLHIDAS:
        r = next((r for r in linhas if chave in r[0].lower()), None)
        if r and len(r) >= 5: out.append("%s Resposta: %s" % (_limpa(r[0]), _limpa(r[4]).strip('"')))
    return out


def _perguntas():
    txt = OBJECOES.read_text(encoding="utf-8")
    p = _numerados(txt.split("## 6. Perguntas de diagnóstico")[1].split("## 7.")[0])
    return p[:8]


def montar(perfil, faixa, hoje=None):
    """Resultado completo (fazer, precisa, falta, esteira, dossie) a partir do perfil da Receita e da faixa de regime."""
    hoje = hoje or date.today()
    razao = perfil.get("razao") or "a empresa"
    cn = (perfil.get("cnae") or {})
    n, nome_cluster = cluster(cn.get("codigo"))
    sec, data_pb = _playbook()
    pb = sec.get(n, {}) if n else {}
    reg_txt, desde, fora = _regime(perfil.get("ecf") or [])
    real = faixa in ("confirmado_real", "provavel_real")
    cidade = ("%s/%s" % (str(perfil.get("municipio") or "").title(), perfil.get("uf"))) if perfil.get("municipio") else (perfil.get("uf") or "")
    servicos = _servicos(pb.get("Mapa de aderência")) if n else []
    altas = [s for s in servicos if s[1] == "alta"]
    aderencia = ("alta" if real and altas else "média" if real or faixa == "nao_real" and servicos else "a confirmar")

    # 1. resumo
    quem = "%s%s, no setor %s" % (razao.title() if razao.isupper() else razao, (", em " + cidade) if cidade else "", (nome_cluster or "fora dos clusters do playbook").lower())
    ult = max(perfil.get("ecf") or [{}], key=lambda x: x.get("ano") or 0)
    resumo = ["%s. %s." % (quem, ("Está no %s (ano-base %s)" % (ult["forma"].title(), ult["ano"]) if ult.get("forma") else "Regime na ECF: " + reg_txt) if real else "Regime na ECF: " + reg_txt)]
    resumo.append("Aderência %s para a esteira da Save. %s" % (aderencia, (
        "O regime Real abre a recuperação de PIS/COFINS e as teses do ICMS na base; a ordem e o alcance dependem dos arquivos da empresa."
        if real else "As teses de recuperação de PIS/COFINS sobre insumos exigem o Lucro Real; confirme o regime antes de seguir. Planejamento e produtos financeiros seguem possíveis.")))
    # 2. retrato
    retrato = ["%s. %s, %s, início de atividade em %s." % (razao, "Matriz" if perfil.get("matriz") else "Filial", (perfil.get("natureza_juridica") or "").lower(), _data(perfil.get("inicio_atividade"))),
               "Atividade principal: %s (CNAE %s)%s." % ((cn.get("descricao") or "").lower(), cn.get("codigo"),
                                                         ". Secundárias: " + "; ".join((x.get("descricao") or "").lower() for x in (perfil.get("cnaes_secundarios") or [])[:6]) if perfil.get("cnaes_secundarios") else ""),
               "Porte na Receita: %s. Capital social: %s." % (perfil.get("porte") or "não informado", _brl(perfil.get("capital_social"))),
               "Regime na ECF: %s. Fonte: Minha Receita (dados da ECF), consultada em %s. O regime da ECF é o do ano-base, não necessariamente o de hoje." % (reg_txt, hoje.strftime("%d/%m/%Y")),
               "Não está no retrato porque a consulta pública não traz: faturamento, folha, produtos por NCM e situação de débitos. Esses dados entram na primeira conversa."]
    if desde and fora:
        retrato.insert(3, "A empresa mudou para o Lucro Real em %s (antes: %s). A análise de insumos vale para as competências no Real; a janela padrão é de cinco anos retroativos." % (desde, ", ".join(str(a) for a in fora)))
    # 3. setor
    setor_p = ["Fontes do playbook do setor, consultadas em %s." % (data_pb or "data não informada")] if n else ["Este CNAE ainda não tem playbook setorial. Os agentes aprofundam a leitura do setor na análise seguinte."]
    setor_i = (_bullets(pb.get("Retrato do setor em 2026"), 4) + _bullets(pb.get("Mudanças regulatórias e tributárias 2025–2027"), 3)
               + ["Dor frequente: " + d for d in _numerados(pb.get("Dores do CFO/dono (top 5)"))[:5]]
               + ["Gatilho de conversa: " + g for g in _bullets(pb.get("Gatilhos de compra"), 5)]) if n else []
    # 4. serviços
    if servicos:
        serv_i = ["%s (aderência %s): %s" % (p, niv, mot) for p, niv, mot in servicos
                  if not any(k in p.lower() for k in ("crédito internacional", "maquila"))]
        desc = [p for p, _, _ in servicos if any(k in p.lower() for k in ("crédito internacional", "maquila"))]
        if desc: serv_i.append("%s: apenas como descoberta (em validação), sem condição." % ", ".join(desc))
    else:
        serv_i = ["Recuperação tributária: PIS/COFINS sobre insumos e exclusão do ICMS da base (aderência a confirmar pelo regime e pelo faturamento).",
                  "Planejamento tributário e reforma (CBS/IBS), com o mapa do mix de produtos por NCM.",
                  "Gestão de Contas e antecipação de recebíveis, com a Save Invest, se a empresa vende a prazo."]
    serv_p = ["As teses são prováveis, não confirmadas. Só o diagnóstico sobre os arquivos da empresa diz se existe crédito, de que tipo e por qual caminho. Nada aqui é estimativa de valor."]
    if not real: serv_p.append("As linhas de recuperação de PIS/COFINS dependem do Lucro Real. Com o regime atual, o ponto de partida são o ICMS na base (Real ou Presumido), a folha e o planejamento.")
    # 5. esteira
    cab, linhas = _tabela(pb.get("Esteira em 3 ondas")) if n else ([], [])
    est_i = ["Onda %s: %s. Depende de %s. Prazo de referência: %s." % (r[0], _limpa(r[1]), _limpa(r[2]), r[3]) for r in linhas if len(r) >= 4] or [
        "Onda 1, destravar caixa: recuperação de insumos e do ICMS da base; Gestão de Contas.", "Onda 2, proteger e controlar: planejamento da reforma; antecipação; passivo se houver.",
        "Onda 3, crescer: funding apenas como descoberta."]
    est_i.append("Regras de sequência: passivo antes de crédito novo; no máximo dois produtos novos por vez; a reforma de 2027 dá urgência à onda 1; produto em validação só como descoberta.")
    # 6. cases
    cs = _case(n) if n else []
    if cs:
        cases_p = ["%s Resultados passados não garantem resultado futuro." % c["resumo_cliente"] for c in cs[:2]]
    else:
        cases_p = ["A biblioteca de cases ainda não tem case aprovado para este segmento, então este dossiê não cita valor de cliente.",
                   "O que o parceiro pode mostrar hoje é o método: análise da EFD-Contribuições dos últimos cinco anos; pedido de ressarcimento pelo caminho conservador; acompanhamento pela procuração eletrônica no e-CAC, sem uso de senha; conferência do técnico antes de qualquer pedido à Receita. Resultados passados não garantem resultado futuro."]
    # 7. abordagem
    sinal = ("a empresa migrou para o Lucro Real em %s e opera no setor %s" % (desde, nome_cluster.lower())) if (desde and fora and nome_cluster) else (
        "a empresa está no Lucro Real e opera em %s" % (cn.get("descricao") or "seu setor").lower())
    abord_p = ["Quem procurar: o sócio-administrador ou o CFO. O contador entra como aliado, depois da primeira conversa.",
               "Abertura sugerida, a partir de um sinal real: \"Vimos que %s. Em 2027 cada produto terá regra própria na reforma, e o crédito de PIS/COFINS escriturado precisa estar correto até dezembro. Podemos conversar 30 minutos sobre como empresas do setor estão se preparando?\"" % sinal,
               "Objetivo da primeira conversa: qualificar e sair com a EFD-Contribuições agendada. Não falar de valor, percentual, prazo de êxito nem nome de cliente."]
    abord_i = ["Pergunta-chave: " + q for q in _perguntas()] + _objecoes() + [
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
    return {"fazer": " ".join(resumo) + " Próximo passo: conversa de 30 minutos com o sócio ou o CFO e pedido da EFD-Contribuições dos últimos cinco anos.",
            "precisa": "A reforma muda a regra de cada produto em 2027, e o crédito de PIS/COFINS já escriturado precisa estar correto até dezembro." + (
                " A empresa mudou para o Lucro Real em %s: a janela padrão é de cinco anos retroativos." % desde if (desde and fora) else ""),
            "falta": " ".join(falta[:3]),
            "esteira": [{"onda": int(re.sub(r"\D", "", r[0])[:1] or 1), "produto": _limpa(r[1]), "status": "pronto", "nota": "Depende de " + _limpa(r[2]) + "."} for r in linhas if len(r) >= 3][:6],
            "dossie": [s for s in dossie if s], "nivel": "base"}
