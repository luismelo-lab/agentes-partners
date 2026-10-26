#!/usr/bin/env python3
"""Busca no histórico: antes de sugerir GLPI, a área procura a resposta em tudo o que já temos (regra do Luis, 26/10/2026).

"Sobre as demandas das meninas, quero que os agentes responsáveis já avaliem em todo o histórico que temos das fontes
disponíveis a resposta de acordo com a demanda. Somente caso elas não tenham a resposta, você sugira a abertura pelo GLPI."

Dado o texto da demanda, o Master e a empresa/CNPJ (se houver), procura em TODAS as fontes locais (só leitura, sem rede) e
devolve os melhores trechos com fonte, data e grau de aderência (BM25 + cobertura dos termos da pergunta). O índice fica em
cache fora do git (registro/historico-indice/, permissão 700/600: tem dado de cliente, LGPD).

Fontes (o comando `inventario` lista o volume de cada uma):
  triagem      respostas que os agentes já prepararam (celulas/whatsapp-triagem-*.json), com o acerto da medição D28
  medicao      registro/medicao-respostas.json (sugestão × o que a dona do número respondeu)
  demanda      registro/demandas.json (pedido, próximo passo, chamado)
  whatsapp     pares pergunta do parceiro → resposta do time nas caixas lidas (celulas/*/whatsapp/caixa-*.json)
  chamado      chamados já escritos (registro/chamados-propostos.json, chamados-para-painel.json, celulas/*/chamados/)
  central      pedidos e respostas da Central (central-agentes/registro.json e pedidos/P-*/resposta.json)
  base         base de conhecimento: skills/*/SKILL.md e references (FAQ, perguntas ao dono, regras do GLPI), decisões do
               Conselho, aprendizados, padrões de resposta, docs/GLPI.md, docs/teses, entregas das áreas
  caso         dado do caso, só quando a empresa é identificada: negócio no HubSpot (download local), resumo e texto do
               parecer (celulas/geovana/pareceres/) e análises das áreas (registro/analises-*.json)

Critério de "resposta suficiente" (avaliar): ver CRITERIOS abaixo e infra/historico-antes-do-glpi.md.

Uso:
  historico.py inventario                         fontes e volume
  historico.py indexar [--forcar]                 (re)monta o índice em cache
  historico.py buscar "texto" [--master M] [--empresa E] [--cnpj C] [--chat X] [--antes AAAA-MM-DDTHH:MM] [--n 8] [--json]
  historico.py avaliar "texto" [mesmos filtros]   busca + pré-avaliação (suficiente? critério, confiança, buscas, faltou)
  historico.py lote --saida <pasta>               roda sobre as demandas abertas + última triagem (modo de teste:
                                                  grava só na pasta indicada, nunca no registro)
"""
import argparse, glob, hashlib, json, math, os, pickle, re, sys, time, unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timedelta

AP = os.path.expanduser(os.environ.get("PARTNERS_AP", "~/agentes-partners"))
REPO = os.path.expanduser(os.environ.get("HISTORICO_REPO", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CACHE = os.path.expanduser(os.environ.get("HISTORICO_CACHE", os.path.join(AP, "registro", "historico-indice")))
VERSAO = 8
HOJE = datetime.now()

PARE = set("""a o e de da do das dos em no na nos nas um uma uns umas para pra por com sem que se ao aos as os é ser foi são como
mais mas ou já também pode podemos fazer faz isso isto esse essa este esta nosso nossa sobre entre até após cada todo toda todos
todas ele ela eles elas lhe seu sua seus suas agora hoje vamos vai ter tem tenho temos está estão estamos muito bem quando onde
qual quais quem the and of oi ola olá bom boa dia tarde noite obrigado obrigada abraço tudo blz ok sim não nao aqui ali lá
pede pediu pedido mensagem nova grupo save daniela geovana jenifer luis time favor gentileza vou vamos ainda então entao""".split())
GENERICO = set("""ltda me epp eireli sa s/a cia comercio comercial industria industrial servicos servico cafe cafes coffee coffees
exportacao importacao exportadora importadora distribuidora distribuicao transportes transporte agricola agro agropecuaria brasil
grupo empresa holding participacoes atacadista atacado alimentos supermercado supermercados mercado mercearia comercializacao
representacoes solucoes empresariais tecnologia produtos materiais construcao fazenda nacional industrias e do da de dos das""".split())

# Peso por tipo de documento e validade (dias) de uma resposta por intenção
PESO = {"resposta": 1.0, "regra": 0.9, "chamado": 0.85, "pedido": 0.7, "demanda": 0.6, "base": 0.7, "pendencia": 0.6, "caso": 1.1}
INTENCOES = {
    "status": (r"\b(status|etapa|andamento|como (esta|anda)|em que pe|fase|atualiza|novidade|retorno|posicao)", 7),
    "assinatura": (r"\bassinou|assinaram|ja assin|foi assinad|link de assinatura|status da assinatura|contrato enviado", 7),
    "verificacao": (r"\bprocuracao (ativa|valida|vigente)|tem procuracao|acesso ao (e-?cac|bitrix|hubspot)|empresas ocultas|permiss", 0),
    "parecer": (r"\bparecer|diagnostico|resultado da analise|zerad|potencial|teses?\b", 30),
    "prazo_novo": (r"\bintima|despacho|ciencia|caixa postal|e-?cac|notifica|autuac|prazo fatal|manifestacao|termo de|indeferi|processo administrativo", 0),
    "compensacao": (r"\bguia|compensa|per\s*/?\s*dcomp|perdcomp|ressarc|residual|darf", 7),
    "calculo": (r"\bplanilha|levantamento|relatorio|calculo|memoria|quanto (falta|vai|sera)", 0),
    "agenda": (r"\bagenda|reuniao|horario|marcar|call\b|visita", 0),
    "contrato": (r"\bcontrato|distrato|aditivo|clausula|procuracao", 30),
    "repasse": (r"\brepasse|comissao|honorario|pagamento do parceiro|nota fiscal", 30),
    "regra": (r"\bpode\b|regra|politica|como funciona|qual o processo|precisa de|quem (faz|cuida)|vale para", 120),
}
# Intenções que pedem ação NOVA da área (o histórico só ajuda como contexto), salvo se já houver chamado do mesmo pedido
EXIGE_AREA = {"prazo_novo", "calculo", "verificacao"}
CRITERIOS = {
    "mesma_pergunta_respondida": "a mesma pergunta já foi respondida (rascunho aprovado, resposta do time no WhatsApp ou da "
                                 "Central) para o mesmo Master ou a mesma empresa, com aderência ≥ 0,55, dentro da validade da "
                                 "intenção (status 7 dias, parecer/contrato 30, regra 120) e sem medição 'diferente'",
    "regra_da_casa": "regra da casa explícita (decisão do Conselho, regra do GLPI, FAQ validado, padrão de resposta, alçada) "
                     "com aderência ≥ 0,5, para pergunta de regra/processo que não depende de dado novo do caso",
    "dado_do_caso": "a empresa foi identificada e o dado pedido está no caso: etapa/status/assinatura no HubSpot (download do "
                    "dia) ou parecer/diagnóstico no resumo do parecer",
    "chamado_existente": "já existe chamado escrito para o mesmo pedido e a mesma empresa (aderência ≥ 0,5): não abrir outro, "
                         "responder com o andamento",
}
GENERICA = re.compile(r"^mensagem nova de|sem resposta h[aá]|os agentes analisam com a [aá]rea", re.I)


# ---------------------------------------------------------------- texto
def norm(s):
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()


def raiz(t):  # radical por truncamento (6 letras): junta compensar/compensação/compensa sem dicionário nem rede
    return t if t.isdigit() else t[:6]


def toks(s):
    return [raiz(t) for t in re.findall(r"[a-z0-9]{3,}", norm(s)) if t not in PARE and not t.isdigit() or (t.isdigit() and len(t) >= 6)]


def sem_link(s):
    return re.sub(r"https?://\S+", "", str(s or "")).strip()


def limpo(t):
    t = re.sub(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", "[e-mail]", str(t or ""))  # e-mail pessoal não vai ao painel (LGPD)
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import protecao
        return protecao.limpo(t)
    except Exception:
        return re.sub(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "[número]", str(t or ""))


def dig(s):
    return re.sub(r"\D", "", str(s or ""))


def _data(s):
    s = str(s or "")
    m = re.search(r"(20\d\d)-(\d\d)-(\d\d)", s)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def _json(f, padrao=None):
    try:
        return json.load(open(f))
    except Exception:
        return padrao


# ---------------------------------------------------------------- fontes
def arquivos_fontes():
    """Mapa fonte → lista de arquivos (para inventário e assinatura do cache)."""
    g = lambda *p: sorted(glob.glob(os.path.join(*p), recursive=True))
    base = []
    for pat in ("skills/*/SKILL.md", "skills/*/references/**/*.md", "conselho/decisoes.md", "infra/glpi-regras.md",
                "infra/alcadas.md", "infra/chamado-ideal.md", "infra/fluxo-unico.md", "docs/GLPI.md", "docs/teses/**/*.md"):
        base += g(REPO, pat)
    for pat in ("registro/chamados-aprendizados.md", "central-agentes/aprendizados.md", "celulas/*/aprendizados.md",
                "celulas/daniela/padroes-resposta.md", "departamentos/*/aprendizados.md", "departamentos/*/perguntas-areas.md",
                "departamentos/*/entregas/*.md", "departamentos/tributario/*.md", "departamentos/produtos/**/*.md",
                "departamentos/ti/GLPI-pronto-para-agente.md"):
        base += g(AP, pat)
    hub = g(AP, "departamentos/resultados/dados/hubspot-*.json")
    return {
        "triagem": g(AP, "celulas/whatsapp-triagem-*.json"),
        "medicao": g(AP, "registro/medicao-respostas.json"),
        "demanda": g(AP, "registro/demandas.json"),
        "whatsapp": g(AP, "celulas/*/whatsapp/caixa-*.json"),
        "chamado": g(AP, "registro/chamados-propostos.json") + g(AP, "registro/chamados-para-painel.json") + g(AP, "celulas/*/chamados/*.json"),
        "central": g(AP, "central-agentes/registro.json") + g(AP, "central-agentes/pedidos/P-*/resposta.json"),
        "base": sorted(set(base)),
        "caso_hubspot": hub[-1:],
        "caso_parecer": g(AP, "celulas/geovana/pareceres/resumos.json"),
        "caso_analises": g(AP, "registro/analises-areas.json") + g(AP, "registro/analises-2026-*.json") + g(AP, "registro/para-areas.json"),
    }


def _time():
    nomes, nums = set(), set()
    c = _json(os.path.join(AP, "celulas", "whatsapp-config.json"), {}) or {}
    nomes |= {norm(n) for n in c.get("nomes_time", [])}
    nums |= {dig(n) for n in c.get("telefones_time", [])}
    t = _json(os.path.join(AP, "celulas", "whatsapp-numeros-time.json"), {}) or {}
    for p in (t.get("pessoas") or {}).values():
        nomes.add(norm(p.get("nome"))); nums |= {dig(n) for n in p.get("numeros", [])}
    return nomes, nums


def _doc(fonte, tipo, titulo, pergunta, resposta, data, onde, **extra):
    return {"fonte": fonte, "tipo": tipo, "titulo": str(titulo or "")[:160], "pergunta": str(pergunta or ""),
            "resposta": str(resposta or ""), "data": data or "", "onde": onde, **extra}


def _medicao_mapa(fs):
    M = {}
    for f in fs:
        for v in (_json(f, {}) or {}).values():
            if isinstance(v, dict):
                M[(norm(v.get("chat")), norm(v.get("pergunta"))[:120])] = v
    return M


def _quando_arquivo(f):
    m = re.search(r"(20\d\d-\d\d-\d\d)-(\d\d)h?(\d\d)", os.path.basename(f))
    return f"{m.group(1)}T{m.group(2)}:{m.group(3)}" if m else _data(os.path.basename(f))


def carregar_triagens(fs, med):
    out, vistos = [], {}
    for f in fs:
        T = _json(f, {}) or {}
        data = _data(os.path.basename(f)) or _data(T.get("rodada"))
        for pessoa, P in (T.get("pessoas") or {}).items():
            for it in (P or {}).get("itens", []) or []:
                q = it.get("o_que_pede") or ""
                if not q or GENERICA.search(q) or it.get("status") == "sem_acao":
                    continue
                enc = it.get("encaminhar") or {}
                m = med.get((norm(it.get("chat")), norm(q)[:120])) or {}
                resp = it.get("rascunho") or ""
                ctx = " ".join(str(it.get(c) or "") for c in ("entrega", "proximo_passo", "precisa"))
                d = _doc("triagem", "resposta" if resp else "demanda", it.get("chat"), q, resp, data,
                         os.path.relpath(f, AP), contexto=ctx, pessoa=pessoa, chat=it.get("chat"), master=it.get("master"),
                         empresa=enc.get("empresa") or "", negocio=str(it.get("negocio") or ""), medicao=m.get("resultado"),
                         chamado=enc.get("titulo") or "", quando=_quando_arquivo(f))
                vistos[(pessoa, norm(it.get("chat")), norm(q)[:120])] = d  # a última triagem vence
    return list(vistos.values())


def carregar_medicao(fs, ja):
    out = []
    for f in fs:
        for k, v in (_json(f, {}) or {}).items():
            if not isinstance(v, dict) or not v.get("sugestao"):
                continue
            if (v.get("pessoa"), norm(v.get("chat")), norm(v.get("pergunta"))[:120]) in ja:
                continue
            out.append(_doc("medicao", "resposta", v.get("chat"), v.get("pergunta"), v.get("sugestao"), _data(v.get("sugerida_em")),
                            os.path.relpath(f, AP), pessoa=v.get("pessoa"), chat=v.get("chat"), medicao=v.get("resultado"),
                            quando=v.get("sugerida_em")))
    return out


def carregar_demandas(fs):
    out = []
    for f in fs:
        R = _json(f, {}) or {}
        D = R.get("demandas") or {}
        for d in (D.values() if isinstance(D, dict) else D):
            q = d.get("o_que_pede") or d.get("titulo") or ""
            if not q or GENERICA.search(q):
                continue
            out.append(_doc("demanda", "demanda", f"{d.get('id')} · {d.get('titulo')}", q, d.get("proximo_passo"),
                            _data(d.get("atualizada_em") or d.get("aberta_em")), os.path.relpath(f, AP), id=d.get("id"),
                            pessoa=d.get("pessoa"), chat=d.get("titulo"), master=d.get("master"), status=d.get("status"),
                            negocio=str(d.get("negocio") or ""), quando=d.get("aberta_em")))
    return out


def _quando_msg(q, ano_ref, mes_ref):
    m = re.match(r"(\d\d)/(\d\d)\s+(\d\d):(\d\d)", str(q or ""))
    if not m:
        return None
    dd, mm = int(m.group(1)), int(m.group(2))
    ano = ano_ref - 1 if mm > mes_ref + 1 else ano_ref
    try:
        return datetime(ano, mm, dd, int(m.group(3)), int(m.group(4)))
    except ValueError:
        return None


def carregar_whatsapp(fs):
    """Pares pergunta do parceiro → resposta do time, sem repetir mensagens que aparecem em várias leituras."""
    nomes, nums = _time()
    eh_time = lambda de: norm(de) in nomes or any(norm(de).startswith(n) for n in nomes if n) or (dig(de) and dig(de) in nums)
    conv = defaultdict(dict); meta = {}
    for f in fs:
        pessoa = f.split(os.sep + "celulas" + os.sep)[1].split(os.sep)[0]
        m = re.search(r"caixa-(\d{4})-(\d\d)", os.path.basename(f))
        ano, mes = (int(m.group(1)), int(m.group(2))) if m else (HOJE.year, HOJE.month)
        for c in _json(f, []) or []:
            if not isinstance(c, dict):
                continue
            k = (pessoa, c.get("chat"))
            meta[k] = {"master": c.get("master"), "onde": os.path.relpath(f, AP),
                       "negocios": [n.get("nome") for n in (c.get("negocios") or []) if isinstance(n, dict)][:12]}
            for msg in c.get("conversa") or []:
                t = str(msg.get("texto") or "")
                dt = _quando_msg(msg.get("quando"), ano, mes)
                if not dt:
                    continue
                conv[k][(msg.get("de"), dt, t[:200])] = {"de": msg.get("de"), "dt": dt, "texto": t, "time": bool(eh_time(msg.get("de")))}
    out = []
    for (pessoa, chat), msgs in conv.items():
        L = sorted(msgs.values(), key=lambda x: x["dt"])
        i = 0
        while i < len(L):
            if L[i]["time"]:
                i += 1; continue
            j = i
            while j < len(L) and not L[j]["time"]:
                j += 1
            k = j
            while k < len(L) and L[k]["time"]:
                k += 1
            perg = [sem_link(x["texto"]) for x in L[max(i, j - 3):j]]
            resp = [sem_link(x["texto"]) for x in L[j:min(k, j + 3)]]
            if j < len(L) and len(" ".join(resp)) >= 25 and len(" ".join(perg)) >= 15:
                mt = meta.get((pessoa, chat), {})
                out.append(_doc("whatsapp", "resposta", chat, " / ".join(p for p in perg if p)[:700], " / ".join(r for r in resp if r)[:900],
                                L[j]["dt"].strftime("%Y-%m-%d"), mt.get("onde"), pessoa=pessoa, chat=chat, master=mt.get("master"),
                                quando=L[j]["dt"].strftime("%Y-%m-%dT%H:%M"), empresas=mt.get("negocios") or []))
            i = k if k > i else i + 1
    return out


def _html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(s or ""))).strip()


def carregar_chamados(fs):
    out, vistos = [], set()
    for f in fs:
        J = _json(f)
        if J is None:
            continue
        if f.endswith("chamados-propostos.json"):
            itens = list(J.values())
        elif f.endswith("chamados-para-painel.json"):
            itens = [dict(x.get("data") or {}, id=x.get("doc_id")) for x in J]
        else:
            itens = [dict(J, id=os.path.basename(f)[:-5])]
        for c in itens:
            cid = c.get("id") or c.get("titulo")
            if cid in vistos:
                continue
            vistos.add(cid)
            desc = c.get("descricao") or c.get("descricao_md") or _html((c.get("chamado") or {}).get("content"))
            out.append(_doc("chamado", "chamado", c.get("titulo"), f"{c.get('titulo')} {c.get('o_que_pede') or ''}", desc,
                            _data(c.get("proposto_em") or c.get("quando")), os.path.relpath(f, AP), id=cid, pessoa=c.get("pessoa"),
                            master=c.get("master"), empresa=c.get("empresa") or "", negocio=str(c.get("negocio") or ""),
                            chat=c.get("conversa") or "", status=c.get("status") or ("rascunho" if c.get("rascunho") else ""), area=c.get("area") or c.get("grupo")))
    return out


def carregar_central(fs):
    out = []
    reg = [f for f in fs if f.endswith("registro.json")]
    for f in reg:
        P = (_json(f, {}) or {}).get("pedidos") or {}
        for p in (P.values() if isinstance(P, dict) else P):
            cp = p.get("campos") or {}
            rf = os.path.join(AP, "central-agentes", "pedidos", p.get("id", ""), "resposta.json")
            R = _json(rf, {}) or {}
            resp = " ".join([R.get("resumo") or ""] + [f"{s.get('titulo')}: {s.get('texto')}" for s in R.get("secoes") or []])
            out.append(_doc("central", "resposta" if resp.strip() else "pedido", f"{p.get('id')} · {p.get('assunto')}",
                            f"{p.get('assunto')} {cp.get('precisa') or ''} {cp.get('contexto') or ''}", resp[:4000], _data(p.get("recebido")),
                            os.path.relpath(rf if R else f, AP), id=p.get("id"), pessoa=p.get("pessoa"), master=cp.get("master"),
                            empresa=cp.get("cliente") or "", status=p.get("status")))
    return out


def _secoes(texto, maximo=1500):
    partes, atual, tit = [], [], ""
    for linha in texto.splitlines():
        if re.match(r"^#{1,4} ", linha):
            if atual:
                partes.append((tit, "\n".join(atual)))
            tit, atual = linha.lstrip("# ").strip(), []
        else:
            atual.append(linha)
    if atual:
        partes.append((tit, "\n".join(atual)))
    out = []
    for tit, corpo in partes:
        bloco = ""
        for par in re.split(r"\n(?=\s*\n)|\n(?=\|)|\n(?=- )", corpo):
            if len(bloco) + len(par) > maximo and bloco.strip():
                out.append((tit, bloco.strip())); bloco = ""
            bloco += "\n" + par
        if bloco.strip():
            out.append((tit, bloco.strip()))
    return out


def carregar_base(fs):
    out = []
    for f in fs:
        try:
            texto = open(f, errors="ignore").read()
        except Exception:
            continue
        rel = os.path.relpath(f, REPO if f.startswith(REPO) else AP)
        data = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(f)))
        nome = os.path.basename(f)
        if nome == "decisoes.md":  # uma decisão por linha da tabela
            for ln in texto.splitlines():
                c = [x.strip() for x in ln.strip().strip("|").split("|")]
                if len(c) >= 5 and re.match(r"^D\d+$", c[0]):
                    out.append(_doc("base", "regra", f"Decisão {c[0]} ({c[4]})", c[3], " · ".join(x for x in c[5:6] if x),
                                    c[1], rel, id=c[0], status=c[4]))
            continue
        regra = bool(re.search(r"aprendizados|padroes-resposta|glpi-regras|faq|alcadas|regras|chamado-ideal|fluxo-unico|perguntas-areas", rel))
        for tit, corpo in _secoes(texto):
            if len(corpo) < 40:
                continue
            tipo = "regra" if regra else "base"
            if "perguntas-ao-dono" in rel:  # pergunta ao dono só vale como resposta se já foi respondida
                tipo = "regra" if re.search(r"respondid|resposta:|decidid", norm(corpo)) else "pendencia"
            out.append(_doc("base", tipo, f"{rel} · {tit}"[:160], f"{tit}", corpo, data, rel))
    return out


def _chave_nome(nome):
    t = [x for x in re.findall(r"[a-z0-9]{3,}", norm(nome)) if x not in GENERICO]
    return tuple(t[:2])


def carregar_casos(fs):
    """Índice de casos: negócios do HubSpot por raiz de CNPJ e por nome distintivo, resumo do parecer e análises por negócio."""
    neg, por_raiz, por_nome = {}, defaultdict(list), defaultdict(list)
    for f in fs.get("caso_hubspot", []):
        H = _json(f, {}) or {}
        for n in H.get("negocios", []):
            ex = n.get("extras") or {}
            neg[n["id"]] = {"id": n["id"], "nome": n.get("nome"), "cnpj": dig(ex.get("cnpj")), "etapa": n.get("etapa"),
                            "pipeline": n.get("pipeline"), "status": n.get("status"), "parceiro": n.get("parceiro"),
                            "criado": n.get("criado"), "fechado": n.get("fechado"), "entrou_etapa": _data(ex.get("entrou_etapa")),
                            "parecer_rt": bool(ex.get("parecer_rt")), "parecer_juridico": bool(ex.get("parecer_juridico")),
                            "diagnostico": bool(ex.get("anexo_diagnostico")), "regime": ex.get("regime"), "uf": ex.get("uf"),
                            "baixado_em": H.get("baixado_em")}
            if dig(ex.get("cnpj")):
                por_raiz[dig(ex.get("cnpj"))[:8]].append(n["id"])
            k = _chave_nome(n.get("nome"))
            for t in k:  # indexado por cada termo distintivo (ACME ZINCOTECA acha por "zincoteca")
                if len(t) >= 4:
                    por_nome[t].append((k, n["id"]))
    pareceres = {}
    for f in fs.get("caso_parecer", []):
        pareceres = _json(f, {}) or {}
    analises = defaultdict(list)
    for f in fs.get("caso_analises", []):
        J = _json(f)
        itens = J.items() if isinstance(J, dict) else [(x.get("chave"), x) for x in (J or []) if isinstance(x, dict)]
        for k, v in itens:
            did = str(k or "").split("|")[-1]
            if did.isdigit() and isinstance(v, dict):
                analises[did].append({"onde": os.path.relpath(f, AP), "data": v.get("quando") or _data(os.path.basename(f)),
                                      "texto": " ".join(str(v.get(c) or "") for c in ("fazer", "precisa", "falta", "texto_base"))})
    return {"negocios": neg, "por_raiz": dict(por_raiz), "por_nome": dict(por_nome), "pareceres": pareceres, "analises": dict(analises)}


# ---------------------------------------------------------------- índice
def _assinatura(fs):
    h = hashlib.sha1(str(VERSAO).encode())
    for k in sorted(fs):
        for f in fs[k]:
            try:
                st = os.stat(f); h.update(f"{f}|{st.st_mtime_ns}|{st.st_size}".encode())
            except OSError:
                pass
    return h.hexdigest()


def montar():
    fs = arquivos_fontes()
    med = _medicao_mapa(fs["medicao"])
    tri = carregar_triagens(fs["triagem"], med)
    ja = {(d.get("pessoa"), norm(d.get("chat")), norm(d["pergunta"])[:120]) for d in tri}
    docs = tri + carregar_medicao(fs["medicao"], ja) + carregar_demandas(fs["demanda"]) + carregar_whatsapp(fs["whatsapp"]) \
        + carregar_chamados(fs["chamado"]) + carregar_central(fs["central"]) + carregar_base(fs["base"])
    inv, dl = defaultdict(list), []
    for i, d in enumerate(docs):
        tk = toks(f"{d['titulo']} {d['pergunta']} {d['pergunta']} {d['resposta']} {d.get('contexto', '')} {d.get('empresa', '')}")
        dl.append(len(tk))
        for t, n in Counter(tk).items():
            inv[t].append((i, n))
    df = Counter(t for d in docs if d["fonte"] == "base" for t in set(re.findall(r"[a-z0-9]{3,}", norm(d["pergunta"] + " " + d["resposta"]))))
    return {"comuns": {t for t, n in df.items() if n >= 3}, "versao": VERSAO, "assinatura": _assinatura(fs), "montado_em": HOJE.strftime("%Y-%m-%dT%H:%M"), "docs": docs,
            "inv": dict(inv), "dl": dl, "avgdl": (sum(dl) / len(dl)) if dl else 1, "casos": carregar_casos(fs),
            "volume": {k: len(v) for k, v in fs.items()}}


def indice(forcar=False):
    arq = os.path.join(CACHE, "indice.pkl")
    if not forcar and os.path.exists(arq):
        try:
            I = pickle.load(open(arq, "rb"))
            if I.get("versao") == VERSAO and I.get("assinatura") == _assinatura(arquivos_fontes()):
                return I
        except Exception:
            pass
    I = montar()
    os.makedirs(CACHE, exist_ok=True); os.chmod(CACHE, 0o700)
    tmp = arq + ".tmp"
    with open(tmp, "wb") as fh:
        pickle.dump(I, fh)
    os.chmod(tmp, 0o600); os.replace(tmp, arq)
    return I


# ---------------------------------------------------------------- caso (empresa)
def achar_caso(I, texto="", empresa="", cnpj=""):
    C = I["casos"]; ids = []
    for c in [dig(cnpj)] + re.findall(r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}", str(texto)):
        r = dig(c)[:8]
        if len(r) == 8:
            ids += C["por_raiz"].get(r, [])
    alvo = set(re.findall(r"[a-z0-9]{3,}", norm(f"{empresa} {texto}")))
    for t in alvo:
        for chave, did in C["por_nome"].get(t, []):
            # nome com um só termo distintivo (TIZIU) basta ele; com dois (FERRO & VASCONCELOS), os dois, salvo termo raro e longo
            if all(x in alvo for x in chave) or (len(t) >= 8 and t not in I.get("comuns", ())):
                ids.append(did)
    if empresa and not ids:
        ke = _chave_nome(empresa)
        for chave, did in C["por_nome"].get(ke[0] if ke else "", []) if ke and len(ke[0]) >= 4 else []:
            if chave[: len(ke)] == ke:
                ids.append(did)
    vistos, out = set(), []
    for did in ids:
        n = C["negocios"].get(did)
        if n and did not in vistos:
            vistos.add(did); out.append(n)
    # empresa com vários negócios: abertos e mais recentes primeiro
    out.sort(key=lambda n: (n.get("status") != "aberto", -(int((n.get("entrou_etapa") or "0000-00-00").replace("-", "")))))
    return out[:6]


def docs_do_caso(I, negocios, raizes_pareceres=True):
    C, out = I["casos"], []
    for n in negocios:
        did = n["id"]
        txt = (f"Negócio {n['nome']} no HubSpot: pipeline {n['pipeline']}, etapa {n['etapa']} desde {n.get('entrou_etapa') or '?'}, "
               f"status {n['status']}, parceiro {n.get('parceiro') or '?'}. Parecer RT no card: {'sim' if n['parecer_rt'] else 'não'}; "
               f"diagnóstico anexo: {'sim' if n['diagnostico'] else 'não'}; parecer jurídico: {'sim' if n['parecer_juridico'] else 'não'}.")
        out.append(_doc("caso", "caso", f"HubSpot · {n['nome']}", txt, txt, (n.get("baixado_em") or "")[:10] or n.get("entrou_etapa"),
                        f"departamentos/resultados/dados (negócio {did})", negocio=did, empresa=n["nome"], campo="hubspot"))
        p = C["pareceres"].get(did)
        if p:
            teses = "; ".join(f"{k}: {v.get('desfecho')}" for k, v in (p.get("teses") or {}).items())
            txt = (f"Parecer ({p.get('modelo')}, análise de {p.get('data_analise')}, período {p.get('periodo_apuracao')}): "
                   f"{p.get('motivo') or ''}. Teses: {teses}. Passivo: {p.get('passivo') or '—'}. Ações judiciais: {p.get('acoes_judiciais') or '—'}.")
            dd = p.get("data_analise") or ""
            m = re.match(r"(\d\d)/(\d\d)/(\d{4})", dd)
            out.append(_doc("caso", "caso", f"Parecer · {n['nome']}", txt, txt, f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else "",
                            "celulas/geovana/pareceres/resumos.json", negocio=did, empresa=n["nome"], campo="parecer"))
        for a in C["analises"].get(did, [])[-2:]:
            out.append(_doc("caso", "caso", f"Análise das áreas · {n['nome']}", a["texto"], a["texto"], a["data"], a["onde"],
                            negocio=did, empresa=n["nome"], campo="analise"))
    return out


# ---------------------------------------------------------------- busca
def _idf(I, t):
    N = len(I["docs"]) or 1
    df = len(I["inv"].get(t, ()))
    return math.log(1 + (N - df + 0.5) / (df + 0.5))


def _cobertura(I, qt, texto_tk):
    s = set(texto_tk); tot = sum(_idf(I, t) for t in qt) or 1
    return sum(_idf(I, t) for t in qt if t in s) / tot


def _trecho(texto, qt, lim=280):
    texto = re.sub(r"\s+", " ", sem_link(texto))
    if len(texto) <= lim:
        return limpo(texto)
    frases = re.split(r"(?<=[.;:!?])\s+|\s/\s", texto)
    alvo = set(qt)
    melhor = max(range(len(frases)), key=lambda i: sum(1 for t in toks(frases[i]) if t in alvo) if frases[i] else -1)
    out = frases[melhor]
    k = melhor + 1
    while len(out) < lim - 40 and k < len(frases):
        out += " " + frases[k]; k += 1
    return limpo(out[:lim].rstrip() + ("…" if len(out) > lim else ""))


def _idade(data):
    try:
        return max(0, (HOJE - datetime.strptime(data[:10], "%Y-%m-%d")).days)
    except Exception:
        return 365


def grau(a):
    return "alta" if a >= 0.55 else "média" if a >= 0.35 else "baixa"


def buscar(texto, master="", empresa="", cnpj="", chat="", antes="", n=8, I=None, fontes=None):
    I = I or indice()
    qt = list(dict.fromkeys(toks(f"{texto} {empresa}")))
    casos = achar_caso(I, texto, empresa, cnpj)
    nomes_caso = {norm(c["nome"]) for c in casos}
    chaves_caso = {_chave_nome(c["nome"])[0] for c in casos if _chave_nome(c["nome"])}
    ids_caso = {c["id"] for c in casos}
    k1, b, avg = 1.2, 0.75, I["avgdl"]
    sc = defaultdict(float)
    for t in qt:
        w = _idf(I, t)
        for i, tf in I["inv"].get(t, ()):
            sc[i] += w * tf * (k1 + 1) / (tf + k1 * (1 - b + b * I["dl"][i] / avg))
    res = []
    for i, s in sc.items():
        d = I["docs"][i]
        if fontes and d["fonte"] not in fontes:
            continue
        if chat and norm(d.get("chat")) == norm(chat):
            q = str(d.get("quando") or d["data"])
            if d["fonte"] in ("chamado", "central", "base"):
                pass  # o chamado já escrito para este pedido é justamente o que evita abrir outro
            elif d["fonte"] == "demanda" or (antes and q >= antes[: len(q)]) or _cobertura(I, toks(d["pergunta"]), qt) >= 0.8:
                continue  # a própria demanda (registro, triagens dela ou resposta já dada depois) não é histórico
        res.append((i, s))
    cand = []
    for i, s in sorted(res, key=lambda x: -x[1])[:400]:
        d = I["docs"][i]
        f = PESO.get(d["tipo"], 0.7)
        mesmo_master = bool(master) and norm(master) == norm(d.get("master"))
        txt_doc = norm(f"{d.get('empresa')} {d['pergunta']} {d['resposta']} {' '.join(d.get('empresas') or [])}")
        mesma_empresa = bool(ids_caso & {str(d.get("negocio") or "")}) or any(n and n in txt_doc for n in nomes_caso) \
            or any(k and len(k) >= 4 and k in set(re.findall(r"[a-z0-9]{3,}", txt_doc)) for k in chaves_caso)
        if mesmo_master: f *= 1.25
        if mesma_empresa: f *= 1.5
        if d.get("medicao") == "diferente": f *= 0.6
        elif d.get("medicao") == "aproveitada": f *= 1.15
        f *= 0.6 + 0.4 * math.exp(-_idade(d["data"]) / 60) if d["tipo"] not in ("regra", "base") else 1.0
        cob = _cobertura(I, qt, toks(f"{d['titulo']} {d['pergunta']} {d['resposta']} {d.get('contexto', '')}"))
        cand.append({"i": i, "score": round(s * f, 3), "aderencia": round(cob, 2), "mesmo_master": mesmo_master, "mesma_empresa": mesma_empresa})
    for d in docs_do_caso(I, casos):
        cob = _cobertura(I, qt, toks(d["resposta"]))
        cand.append({"doc": d, "score": round(10 * PESO["caso"] * (0.5 + cob), 3), "aderencia": round(max(cob, 0.5), 2),
                     "mesmo_master": False, "mesma_empresa": True})
    cand.sort(key=lambda c: -c["score"])
    out, ja = [], set()
    n_caso = 0
    for c in cand:
        if c.get("doc"):
            if n_caso >= 4:
                continue  # o dado do caso sempre entra (até 4), mesmo abaixo do corte de n
            n_caso += 1
        elif len(out) - n_caso >= n:
            continue
        d = c.get("doc") or I["docs"][c["i"]]
        base = d["resposta"] if d["resposta"].strip() else d["pergunta"]
        if norm(base)[:160] in ja:
            continue  # mesmo trecho em duas cópias (ex.: regra do GLPI em infra/ e na skill)
        ja.add(norm(base)[:160])
        out.append({"fonte": d["fonte"], "tipo": d["tipo"], "titulo": limpo(d["titulo"]), "data": d["data"], "onde": d["onde"],
                    "pergunta": _trecho(d["pergunta"], qt, 200), "trecho": _trecho(base, qt),
                    "aderencia": c["aderencia"], "grau": grau(c["aderencia"]), "score": c["score"],
                    "mesmo_master": c["mesmo_master"], "mesma_empresa": c["mesma_empresa"],
                    **{k: d.get(k) for k in ("chat", "master", "medicao", "status", "id", "negocio", "campo", "area") if d.get(k)}})
    return {"consulta": texto, "termos": qt, "casos": [{k: c[k] for k in ("id", "nome", "etapa", "pipeline", "status", "parceiro")} for c in casos],
            "resultados": out, "indice": {"documentos": len(I["docs"]), "montado_em": I["montado_em"]}}


# ---------------------------------------------------------------- avaliação (suficiente ou GLPI)
def intencoes(texto):
    n = norm(texto)
    return [k for k, (rx, _) in INTENCOES.items() if re.search(rx, n)]


def avaliar(texto, master="", empresa="", cnpj="", chat="", antes="", area="", especialista="", I=None):
    """Pré-avaliação determinística. O especialista da área confirma, escreve o rascunho e pode discordar (registrando o motivo)."""
    I = I or indice()
    B = buscar(texto, master, empresa, cnpj, chat, antes, n=10, I=I)
    R, its = B["resultados"], intencoes(texto)
    validade = min([INTENCOES[k][1] for k in its if INTENCOES[k][1]] or [120])
    criterio, apoio, conf, faltou = None, [], 0.0, []

    mesmo_chat = lambda r: bool(chat) and norm(r.get("chat")) == norm(chat)
    chamados = [r for r in R if r["tipo"] == "chamado" and r["aderencia"] >= 0.5
                and (r["mesma_empresa"] or (r["aderencia"] >= 0.8 and (mesmo_chat(r) or r["mesmo_master"])))]
    respostas = [r for r in R if r["tipo"] == "resposta" and r["aderencia"] >= 0.55 and len(toks(r["trecho"])) >= 6
                 and (r["mesmo_master"] or r["mesma_empresa"] or ("regra" in its and r["aderencia"] >= 0.65))
                 and _idade(r["data"]) <= validade and r.get("medicao") != "diferente"]
    regras = [r for r in R if r["tipo"] == "regra" and r["aderencia"] >= 0.5]
    caso = [r for r in R if r["fonte"] == "caso"]
    caso_ok = [r for r in caso if (r.get("campo") == "hubspot" and {"status", "assinatura", "parecer"} & set(its))
               or (r.get("campo") == "parecer" and "parecer" in its)]
    exige = set(its) & EXIGE_AREA

    informativos = [t for t in B["termos"] if _idf(I, t) > 1.5]
    if len(informativos) < 3 and not its:
        faltou.append("sem pedido identificável (cumprimento, agradecimento ou recado curto)")
    elif caso_ok and not exige:  # pergunta de status/assinatura/parecer: o dado do caso responde, antes de qualquer chamado
        criterio, apoio, conf = "dado_do_caso", sorted(caso_ok, key=lambda r: r.get("campo") != "parecer")[:2] + respostas[:1], 0.8
    elif chamados:
        criterio, apoio, conf = "chamado_existente", chamados[:2], min(0.9, 0.5 + chamados[0]["aderencia"] / 2)
    elif exige:
        faltou.append("pedido exige ação nova da área (" + ", ".join(sorted(exige)) + "): leitura de documento novo, prazo, cálculo ou conferência em sistema")
    elif respostas:
        criterio, apoio, conf = "mesma_pergunta_respondida", respostas[:3], round(min(0.9, respostas[0]["aderencia"]), 2)
    elif regras and ("regra" in its or not ({"status", "assinatura", "compensacao", "parecer"} & set(its))):
        criterio, apoio, conf = "regra_da_casa", regras[:2], round(min(0.85, regras[0]["aderencia"]), 2)
    if not criterio:
        if not B["casos"] and ({"status", "assinatura", "parecer", "compensacao"} & set(its)):
            faltou.append("empresa não identificada no HubSpot (falta razão social ou CNPJ)")
        melhor = R[0] if R else None
        if melhor and melhor["tipo"] == "pendencia":
            faltou.append(f"pergunta registrada ao dono ainda sem resposta ({melhor['titulo']})")
        if not faltou:
            faltou.append("nenhuma resposta anterior com aderência suficiente para o mesmo Master/empresa, nem regra explícita")
    buscas = [{"consulta": " ".join(B["termos"][:14]), "fontes": sorted({r["fonte"] for r in R}) or ["nenhuma"],
               "filtros": {k: v for k, v in (("master", master), ("empresa", empresa), ("cnpj", "informado" if cnpj else ""), ("chat", chat)) if v},
               "casos": [c["nome"] for c in B["casos"]], "melhores": [f"{r['fonte']} {r['data']} {r['grau']} ({r['aderencia']})" for r in R[:3]]}]
    # sem resposta no histórico: GLPI só se o pedido é de área; agenda, recado ou conversa sem pedido ficam com a dona do número
    rota = "responder" if criterio else ("dona" if set(its) <= {"agenda"} else "glpi")
    return {"suficiente": bool(criterio), "criterio": criterio, "criterio_texto": CRITERIOS.get(criterio, ""),
            "confianca": round(conf, 2), "intencoes": its, "rota": rota,
            "fontes": [{"fonte": r["fonte"], "data": r["data"], "trecho": r["trecho"], "aderencia": r["aderencia"], "onde": r["onde"],
                        **({"status": r["status"]} if r.get("status") else {})} for r in (apoio or R[:3])],
            "buscas": buscas, "faltou": "; ".join(faltou), "area": area, "especialista": especialista, "resultados": R, "casos": B["casos"]}


def resposta_historico(av, resposta, area, especialista):
    """Monta o campo resposta_historico do item (o especialista escreve 'resposta'; aqui só se padroniza e audita)."""
    aud = None
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import protecao
        aud = protecao.auditar(resposta)
    except Exception:
        pass
    return {"resposta": limpo(resposta), "auditado": aud, "criterio": av["criterio"], "confianca": av["confianca"],
            "fontes": [{"fonte": f["fonte"], "data": f["data"], "trecho": f["trecho"][:220]} for f in av["fontes"][:3]],
            "area": area, "especialista": especialista}


def base_resposta(av):
    """Rascunho-base a partir da melhor fonte (o especialista reescreve; serve para medir e para o modo de teste)."""
    if not av["suficiente"]:
        return ""
    f = av["fontes"][0]
    if av["criterio"] == "chamado_existente":
        if f.get("status") == "recusado":
            return ""
        return "Esse pedido já está registrado com a área responsável na Save; assim que ela retornar, aviso por aqui."
    if av["criterio"] == "dado_do_caso":
        t = f["trecho"]
        m = re.search(r"Negócio (.+?) no HubSpot: pipeline (.+?), etapa (.+?) desde (\S+?),", t)
        if m:
            return f"Conferi aqui: {m.group(1)} está na etapa {m.group(3)} desde {m.group(4)}. Qualquer novidade, aviso por aqui."
        return "Conferi o parecer: " + t[:220]
    return f["trecho"]


# ---------------------------------------------------------------- lote de teste (não grava no registro)
def _conversa_recente(pessoa, chat, n=4):
    fs = sorted(glob.glob(os.path.join(AP, "celulas", pessoa, "whatsapp", "caixa-*.json")))
    nomes, nums = _time()
    for f in reversed(fs[-6:]):
        for c in _json(f, []) or []:
            if isinstance(c, dict) and c.get("chat") == chat:
                ext = [sem_link(m.get("texto")) for m in c.get("conversa") or []
                       if norm(m.get("de")) not in nomes and not any(norm(m.get("de")).startswith(x) for x in nomes if x)]
                return " / ".join(t for t in ext[-n:] if t)
    return ""


def lote(saida, dias=0):
    if os.path.abspath(saida).startswith(os.path.join(AP, "registro")):
        sys.exit("modo de teste: escolha uma pasta fora de registro/")
    I = indice()
    R = (_json(os.path.join(AP, "registro", "demandas.json"), {}) or {}).get("demandas") or {}
    abertas = [d for d in (R.values() if isinstance(R, dict) else R) if d.get("pessoa") in ("daniela", "geovana", "jenifer") and d.get("status") in ("responder", "acompanhar", "em_analise", "aguardando_aprovacao")]
    ult = sorted(glob.glob(os.path.join(AP, "celulas", "whatsapp-triagem-*.json")))
    hoje = [f for f in ult if HOJE.strftime("%Y-%m-%d") in f] or ult[-1:]
    if dias:  # retroteste: itens "responder" das triagens dos últimos N dias, cada um só com o histórico anterior a ele
        lim = (HOJE - timedelta(days=dias)).strftime("%Y-%m-%d")
        hoje = [f for f in ult if _data(os.path.basename(f)) >= lim]
    itens = []
    vistos = set()
    for d in abertas:
        texto = d.get("o_que_pede") or d.get("titulo") or ""
        if GENERICA.search(texto) or not texto:
            texto = _conversa_recente(d.get("pessoa"), d.get("titulo")) or texto
        itens.append({"origem": d["id"], "pessoa": d.get("pessoa"), "chat": d.get("titulo"), "master": d.get("master") or "",
                      "texto": texto, "antes": d.get("aberta_em") or "", "tem_chamado": bool(d.get("chamado"))})
        vistos.add((d.get("pessoa"), norm(d.get("titulo"))))
    for f in hoje:
        T = _json(f, {}) or {}
        for p, P in (T.get("pessoas") or {}).items():
            for it in P.get("itens", []):
                if it.get("status") == "sem_acao" or (p, norm(it.get("chat"))) in vistos:
                    continue
                texto = it.get("o_que_pede") or ""
                if GENERICA.search(texto):
                    texto = _conversa_recente(p, it.get("chat")) or texto
                if dias and (it.get("status") != "responder" or GENERICA.search(it.get("o_que_pede") or "")):
                    continue
                vistos.add((p, norm(it.get("chat"))))
                itens.append({"origem": os.path.basename(f), "pessoa": p, "chat": it.get("chat"), "master": it.get("master") or "",
                              "texto": texto, "antes": _quando_arquivo(f), "tem_chamado": bool(it.get("encaminhar"))})
    out = []
    for it in itens:
        av = avaliar(it["texto"], it["master"], chat=it["chat"], antes=it["antes"], I=I)
        av.pop("resultados", None)
        rh = resposta_historico(av, base_resposta(av), "a definir pela área", "especialista da área") if av["suficiente"] else None
        out.append({**it, "texto": limpo(it["texto"])[:400], "avaliacao": av, "resposta_historico": rh})
    os.makedirs(saida, exist_ok=True)
    arq = os.path.join(saida, f"historico-teste-{HOJE.strftime('%Y-%m-%d-%Hh%M')}.json")
    json.dump({"rodado_em": HOJE.strftime("%Y-%m-%dT%H:%M"), "indice": {"documentos": len(I["docs"]), "volume": I["volume"]},
               "itens": out}, open(arq, "w"), ensure_ascii=False, indent=1)
    os.chmod(arq, 0o600)
    resp = sum(1 for x in out if x["avaliacao"]["suficiente"])
    rot = Counter(x["avaliacao"]["rota"] for x in out); cri = Counter(x["avaliacao"]["criterio"] for x in out if x["avaliacao"]["criterio"])
    print(f"{len(out)} demanda(s): {resp} com resposta no histórico {dict(cri)} · {rot.get('glpi', 0)} iriam ao GLPI · "
          f"{rot.get('dona', 0)} ficam com a dona do número (sem pedido de área) → {arq}")
    return arq


# ---------------------------------------------------------------- CLI
def inventario():
    fs = arquivos_fontes(); I = indice()
    por = Counter(d["fonte"] for d in I["docs"]); tipo = Counter(d["tipo"] for d in I["docs"])
    print(f"Índice: {len(I['docs'])} documentos (montado em {I['montado_em']}) · cache {CACHE}")
    for k, v in fs.items():
        print(f"  {k:<14} {len(v):>5} arquivo(s)  → {por.get(k, 0):>6} doc(s)")
    C = I["casos"]
    print(f"  casos: {len(C['negocios'])} negócios HubSpot · {len(C['pareceres'])} resumos de parecer · {len(C['analises'])} negócios com análise")
    print("  por tipo:", dict(tipo))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["inventario", "indexar", "buscar", "avaliar", "lote"])
    ap.add_argument("texto", nargs="?", default="")
    for a in ("master", "empresa", "cnpj", "chat", "antes", "saida", "area", "especialista"):
        ap.add_argument("--" + a, default="")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--dias", type=int, default=0, help="lote: retroteste com as triagens dos últimos N dias")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()
    if a.cmd == "inventario":
        return inventario()
    if a.cmd == "indexar":
        I = indice(forcar=a.forcar); print(f"{len(I['docs'])} documentos · {CACHE}"); return
    if a.cmd == "lote":
        if not a.saida:
            sys.exit("informe --saida <pasta> (modo de teste, fora de registro/)")
        return lote(a.saida, a.dias)
    if a.cmd == "buscar":
        r = buscar(a.texto, a.master, a.empresa, a.cnpj, a.chat, a.antes, a.n)
    else:
        r = avaliar(a.texto, a.master, a.empresa, a.cnpj, a.chat, a.antes, a.area, a.especialista)
        r.pop("resultados", None)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1)); return
    if a.cmd == "avaliar":
        print(f"{'SUFICIENTE' if r['suficiente'] else 'INSUFICIENTE'} · critério {r['criterio']} · confiança {r['confianca']} · intenções {r['intencoes']}")
        if r["faltou"]: print("  faltou:", r["faltou"])
        for f in r["fontes"]: print(f"  - [{f['fonte']} {f['data']} · {f['aderencia']}] {f['trecho'][:200]}")
        return
    print("casos:", ", ".join(c["nome"] for c in r["casos"]) or "—")
    for x in r["resultados"]:
        print(f"[{x['fonte']}/{x['tipo']} {x['data']} · aderência {x['aderencia']} ({x['grau']}) · {x['score']}] {x['titulo'][:70]}")
        print("   ", x["trecho"][:240])


if __name__ == "__main__":
    main()
