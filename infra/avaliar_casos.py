#!/usr/bin/env python3
"""Avaliação das áreas por casos de teste (padrão em `infra/casos-teste.md`).

O auditor de senioridade mede se o especialista está completo. Este script mede se a área responde certo:
lê `skills/<área>/references/casos-teste.md`, monta o prompt de cada caso e, dada a resposta gravada em
`registro/avaliacoes/<área>/<caso>.md`, pontua por regras verificáveis. Não chama API externa: quem responde
é um subagente da sessão (ou uma pessoa), que lê só a skill da área.

Pontuação por caso (0 a 100), documentada em `infra/casos-teste.md` §4:
  - Conteúdo        50  fração dos pontos de "Deve conter" atendidos (grupos de termos, sem acento, palavra inteira)
  - Limpeza         30  −15 por termo proibido do caso (fora de negação), −15 por alerta ALTO e −8 por MÉDIO do
                        auditor de promessas (skills/depto-qualidade/scripts/auditar_texto.py + regras-promessas.json)
  - Encaminhamento  20  caso da própria área: 20 se "Área que responde:" é ela (consultar outra área é permitido);
                        fronteira: 20 se a área certa está em "Encaminhar para:" ou "Área que responde:"; 10 se só no texto
  - Citação recusada não conta: termo proibido entre aspas numa linha que proíbe, com negação antes ou recusa
    logo depois ("'recupere 5 anos' não pode sair"). Expressões técnicas (seguro garantia, dívidas garantidas) e
    "alíquota zero só via PER, nunca DCOMP" não contam como alerta do auditor de promessas.
  - Falha crítica: termo proibido do caso ou alerta ALTO limita o caso a 49. Aprovado com 70 ou mais.
Acerto da área = média dos casos respondidos.

Uso:
  python3 infra/avaliar_casos.py --validar [--area A]     → confere o formato dos casos-teste.md
  python3 infra/avaliar_casos.py --preparar [--area A]    → grava registro/avaliacoes/<área>/prompts/CT-nn.md
  python3 infra/avaliar_casos.py --pontuar [--area A]     → lê as respostas e grava registro/avaliacoes/relatorio-<data>.md/.json
  Opções: --registro <pasta> (padrão ~/agentes-partners/registro ou $PARTNERS_REGISTRO), --json, --skills <pasta>
"""
import argparse, glob, importlib.util, json, os, re, sys, unicodedata
from datetime import date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRO_PADRAO = os.environ.get("PARTNERS_REGISTRO", os.path.expanduser("~/agentes-partners/registro"))
AUDITOR = os.path.join(REPO, "skills", "depto-qualidade", "scripts", "auditar_texto.py")
REGRAS = os.path.join(REPO, "skills", "depto-qualidade", "references", "regras-promessas.json")

PESO_CONTEUDO, PESO_LIMPEZA, PESO_ENCAMINHAMENTO = 50, 30, 20
PENA_PROIBIDO, PENA_ALTO, PENA_MEDIO = 15, 15, 8
TETO_CRITICO, APROVADO = 49, 70
MIN_CASOS, MIN_DEVE, MIN_NAO = 5, 3, 1

# Nomes pelos quais cada área pode aparecer na resposta (além da pasta e da pasta sem "depto-"/"celula-").
APELIDOS = {
    "depto-tributario": ["tributario", "tecnico tributario", "time tecnico"],
    "depto-juridico": ["juridico", "advogado", "advogada"],
    "depto-save-invest": ["save invest", "junior"],
    "depto-internacional": ["internacional", "joao mattos", "produtos internacionais"],
    "depto-operacoes-canal": ["operacoes de canal", "operacoes canal"],
    "depto-intel-comercial": ["intel comercial", "inteligencia comercial"],
    "depto-pos-venda": ["pos-venda", "pos venda"],
    "depto-partner-success": ["partner success", "academia de parceiros"],
    "depto-solucoes": ["solucoes", "contas e solucoes"],
    "depto-resultados": ["resultados", "controladoria", "controller"],
    "depto-dados": ["dados & bi", "dados e bi", "depto dados"],
    "depto-ti": ["ti", "tecnologia"],
    "depto-pessoas": ["pessoas", "rh"],
    "depto-qualidade": ["qualidade", "ouvidoria"],
    "depto-marketing": ["marketing"],
    "depto-contratos": ["contratos"],
    "celula-daniela": ["daniela", "central masters"],
    "celula-jenifer": ["jenifer", "central bdr"],
    "recuperador": ["recuperador", "geovana"],
    "revisor-diagnostico": ["revisor de diagnostico", "revisor"],
    "apresentacao-diagnostico": ["apresentacao do diagnostico", "apresentacao de diagnostico"],
    "conselho-partners": ["conselho"],
    "gabinete": ["gabinete"],
    "central-agentes": ["central de agentes"],
    "arquiteto-agentes": ["arquiteto de agentes", "arquiteto"],
}
RX_NEGACAO = re.compile(r"\b(nao|nunca|jamais|sem|nem|nenhum[a]?|vedad[oa]s?|proibid[oa]s?|evite|evitar|exceto|nada de|em vez de|no lugar de|fora)\b[^.;:\n]{0,60}$")


def norm(s):
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()


def ler(p):
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return ""


# ---------- leitura dos casos ----------
RX_TERMOS = re.compile(r"`([^`]+)`")


def grupos_da_linha(linha):
    """'texto · `a | b` + `c`' → [['a','b'], ['c']]."""
    return [[t.strip() for t in g.split(" | ") if t.strip()] for g in RX_TERMOS.findall(linha)]


def compilar_termo(t):
    if t.startswith("re:"):
        return re.compile(t[3:].strip(), re.I)
    n = norm(t).strip()
    prefixo = n.endswith("*")
    n = n.rstrip("*")
    corpo = re.escape(n).replace(r"\ ", r"\s+")
    ini = r"\b" if re.match(r"\w", n) else ""
    fim = "" if prefixo or not re.search(r"\w$", n) else r"\b"
    return re.compile(ini + corpo + fim)


def ler_casos(caminho):
    texto = ler(caminho)
    casos = []
    blocos = re.split(r"^## (?=CT-)", texto, flags=re.M)[1:]
    for b in blocos:
        linhas = b.splitlines()
        cab = linhas[0].strip()
        m = re.match(r"(CT-\d+)\s*[·\-–:]\s*(.*)", cab)
        cid, titulo = (m.group(1), m.group(2).strip()) if m else (cab.split()[0], cab)
        campo = lambda nome: (re.search(r"^\s*-\s*\*\*" + nome + r":\*\*\s*(.+)$", b, re.M | re.I) or [None, ""])[1].strip()
        entrada, deve, nao, secao = [], [], [], None
        for l in linhas[1:]:
            ln = norm(l)
            if re.match(r"\*\*entrada", ln):
                secao = "entrada"; continue
            if re.match(r"\*\*deve conter", ln):
                secao = "deve"; continue
            if re.match(r"\*\*nao pode conter", ln):
                secao = "nao"; continue
            if secao == "entrada" and l.startswith(">"):
                entrada.append(l[1:].strip())
            elif secao in ("deve", "nao") and re.match(r"^\s*-\s+", l):
                item = {"texto": re.sub(r"\s*·\s*`.*$", "", l.strip()[2:]).strip(), "grupos": grupos_da_linha(l)}
                (deve if secao == "deve" else nao).append(item)
        enc = campo("Encaminhar para")
        casos.append({"id": cid, "titulo": titulo, "tipo": norm(campo("Tipo")), "especialista": campo("Especialista"),
                      "fonte": campo("Fonte"), "encaminhar": enc, "entrada": "\n".join(entrada).strip(),
                      "deve": deve, "nao": nao})
    return casos


def validar(area, casos, pastas_validas):
    erros = []
    if len(casos) < MIN_CASOS:
        erros.append(f"{len(casos)} casos (mín. {MIN_CASOS})")
    tipos = [c["tipo"] for c in casos]
    if not any("fronteira" in t for t in tipos):
        erros.append("nenhum caso de fronteira")
    if not any("armadilha" in t for t in tipos):
        erros.append("nenhum caso-armadilha")
    for c in casos:
        p = c["id"]
        if not c["entrada"]:
            erros.append(f"{p}: sem entrada")
        if len(c["deve"]) < MIN_DEVE:
            erros.append(f"{p}: {len(c['deve'])} pontos em 'Deve conter' (mín. {MIN_DEVE})")
        if len(c["nao"]) < MIN_NAO:
            erros.append(f"{p}: sem 'Não pode conter'")
        for it in c["deve"] + c["nao"]:
            if not it["grupos"]:
                erros.append(f"{p}: ponto sem termos verificáveis: {it['texto'][:60]}")
            for g in it["grupos"]:
                for t in g:
                    try:
                        compilar_termo(t)
                    except re.error as e:
                        erros.append(f"{p}: regex inválida {t!r}: {e}")
        enc = c["encaminhar"]
        if not enc:
            erros.append(f"{p}: sem 'Encaminhar para'")
        elif norm(enc) != "nenhuma":
            for a in [x.strip() for x in enc.split("|")]:
                if a not in pastas_validas:
                    erros.append(f"{p}: 'Encaminhar para' com área inexistente: {a}")
            if "fronteira" not in c["tipo"] and "armadilha" not in c["tipo"]:
                pass
        if "fronteira" in c["tipo"] and norm(enc) == "nenhuma":
            erros.append(f"{p}: caso de fronteira sem área de destino")
        if re.search(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b|\(\d{2}\)\s?\d{4,5}-?\d{4}|@\w+\.\w", c["entrada"]) or _cnpj_alfa(c["entrada"]):
            erros.append(f"{p}: entrada com CNPJ, telefone ou e-mail (anonimize)")
    return erros


def _cnpj_alfa(texto):
    """CNPJ alfanumérico (IN RFB 2.229/2024) com DV válido na entrada do caso: o padrão numérico acima não o pega."""
    try:
        sys.path.insert(0, os.path.join(REPO, "lib")); from cnpj import CNPJ_TEXTO_ALFA, cnpj_valido, normalizar_cnpj
    except ImportError:
        return False
    return any(re.search(r"[A-Z]", m) and cnpj_valido(normalizar_cnpj(m)) for m in CNPJ_TEXTO_ALFA.findall(texto or ""))


# ---------- pontuação ----------
def carregar_auditor():
    if not os.path.isfile(AUDITOR):
        return None, None
    spec = importlib.util.spec_from_file_location("auditar_texto", AUDITOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    from pathlib import Path
    return mod, mod.carregar_regras(Path(REGRAS))


def apelidos(area):
    base = [area, area.replace("depto-", "").replace("celula-", "").replace("-", " ")]
    return [norm(x) for x in base + APELIDOS.get(area, [])]


def linha_campo(texto_norm, nome):
    m = None
    for m in re.finditer(r"^[\s>*_-]*" + nome + r"[*_]*\s*:\s*(.+)$", texto_norm, re.M):
        pass
    return m.group(1).strip() if m else None


def casa_area(trecho_norm, area):
    return any(re.search(r"(?<![\w-])" + re.escape(a) + r"(?![\w])", trecho_norm) for a in apelidos(area))


def grupo_presente(texto_norm, grupo):
    return any(compilar_termo(t).search(texto_norm) for t in grupo)


# Depois do termo, na mesma frase: a resposta cita o erro para recusá-lo ("'recupere 5 anos' não pode sair").
RX_RECUSA_DEPOIS = re.compile(r"^[^.!?\n]{0,60}\b(nao pode|nao deve|nao sai|proibid[oa]s?|vedad[oa]s?|bloquead[oa]s?|recusad[oa]s?|fica de fora|sai do texto|nao existe)\b")
RX_PROIBICAO_LINHA = re.compile(r"\b(nao (diga|dizer|use|usar|escreva|escrever|pode|sai)|nunca (diga|use|escreva)|proibid|vedad|bloquead|recusad|frases? (de risco|proibida)|nao existe|evite|retirar|tirar|trocar|substitu)")
ASPAS = "\"\u201c\u201d\u00ab\u00bb"


def entre_aspas(linha_norm, ini):
    """O trecho está entre aspas (citação do pedido ou da frase proibida)?"""
    return sum(linha_norm[:ini].count(c) for c in ASPAS) % 2 == 1


def citacao_recusada(texto_norm, ini, fim, olhar_negacao=True):
    """Termo citado para ser recusado: negação antes (mesma frase), recusa logo depois, ou entre aspas numa linha que proíbe.
    Para os alertas do auditor de promessas, olhar_negacao=False: ele já trata a negação pelas próprias regras."""
    antes = re.split(r"[.!?\n]", texto_norm[max(0, ini - 80):ini])[-1]
    if (olhar_negacao and RX_NEGACAO.search(antes)) or RX_RECUSA_DEPOIS.search(texto_norm[fim:fim + 80]):
        return True
    li = texto_norm.rfind("\n", 0, ini) + 1
    lf = texto_norm.find("\n", fim)
    linha = texto_norm[li:lf if lf >= 0 else len(texto_norm)]
    return entre_aspas(linha, ini - li) and bool(RX_PROIBICAO_LINHA.search(linha))


# Expressões técnicas que o auditor de promessas marca por engano (catálogo de falsos positivos da Qualidade).
EXPRESSOES_TECNICAS = re.compile(r"seguro[- ]garantia|garantia (real|judicial|fidejussoria)|(dividas?|debitos?|creditos?) garantid[oa]s|"
                                 r"garantid[oa]s (por|com) (seguro|deposito|penhora|garantia)|recuperacao e garantidas|compensacao de oficio")


def proibido_hits(texto_norm, grupo):
    hits = []
    for t in grupo:
        for m in compilar_termo(t).finditer(texto_norm):
            if citacao_recusada(texto_norm, m.start(), m.end()):
                continue
            hits.append(texto_norm[max(0, m.start() - 50):m.end() + 50].replace("\n", " "))
    return hits


RX_DCOMP = re.compile(r"\b(dcomp|compens\w*)\b")


def p10_negada(linha_norm, achado):
    """A regra P10.1 (alíquota zero perto de DCOMP/compensação) do auditor de promessas não olha negação depois de
    'alíquota zero'. Aqui o alerta cai quando toda menção a DCOMP/compensação no trecho vem negada na mesma frase
    ("só via PER, nunca DCOMP"), ou faz parte da expressão 'compensação de ofício' (ato da Receita, não pedido)."""
    trecho = linha_norm[achado["inicio"]:achado["fim"]]
    for m in RX_DCOMP.finditer(trecho):
        pos = achado["inicio"] + m.start()
        if linha_norm[pos:pos + 25].startswith(("compensacao de oficio", "compensada de oficio", "compensado de oficio")):
            continue
        antes = re.split(r"[.!?\n]", linha_norm[max(0, pos - 80):pos])[-1]
        if not RX_NEGACAO.search(antes):
            return False
    return True


def pontuar_caso(area, caso, resposta, aud):
    mod, regras = aud
    tn = norm(resposta)
    # sem as duas linhas finais, para não contar o nome da área como conteúdo
    corpo = re.sub(r"^[\s>*_-]*(area que responde|encaminhar para)\s*:.*$", "", tn, flags=re.M)
    atendidos, faltou = 0, []
    for it in caso["deve"]:
        if it["grupos"] and all(grupo_presente(corpo, g) for g in it["grupos"]):
            atendidos += 1
        else:
            faltou.append(it["texto"])
    conteudo = PESO_CONTEUDO * (atendidos / len(caso["deve"]) if caso["deve"] else 1)

    proib = []
    for it in caso["nao"]:
        hs = [h for g in it["grupos"] for h in proibido_hits(corpo, g)]
        if hs:
            proib.append({"ponto": it["texto"], "trecho": hs[0]})
    altos = medios = 0
    alertas = []
    if mod:
        linhas = [(i, l) for i, l in enumerate(resposta.splitlines(), 1)]
        r = mod.auditar_linhas(linhas, regras)
        for a in r["achados"]:
            ln = mod.normalizar(linhas[a["linha"] - 1][1])
            if a["regra"] == "P10.1" and p10_negada(ln, a):
                continue  # "alíquota zero só via PER, nunca DCOMP" é a regra certa, não o defeito
            if EXPRESSOES_TECNICAS.search(ln[max(0, a["inicio"] - 30):a["fim"] + 30]):
                continue
            if citacao_recusada(ln, a["inicio"], a["fim"], olhar_negacao=False):
                continue  # a resposta cita a frase proibida para recusá-la
            if a["severidade"] == "ALTO":
                altos += 1
            elif a["severidade"] == "MEDIO":
                medios += 1
            else:
                continue
            alertas.append(f"{a['regra']} {a['severidade']}: {a['trecho']}")
    limpeza = max(0, PESO_LIMPEZA - PENA_PROIBIDO * len(proib) - PENA_ALTO * altos - PENA_MEDIO * medios)

    esperado = [x.strip() for x in caso["encaminhar"].split("|")] if norm(caso["encaminhar"]) != "nenhuma" else []
    linha_enc = linha_campo(tn, "encaminhar para")
    linha_area = linha_campo(tn, "area que responde")
    if esperado:
        if (linha_enc and any(casa_area(linha_enc, a) for a in esperado)) or \
                (linha_area and any(casa_area(linha_area, a) for a in esperado)):
            enc, enc_nota = PESO_ENCAMINHAMENTO, "linha bate"
        elif any(casa_area(corpo, a) for a in esperado):
            enc, enc_nota = PESO_ENCAMINHAMENTO / 2, "área só no texto"
        else:
            enc, enc_nota = 0, "não encaminhou"
    else:
        # A área responde e pode consultar outras: o que decide é "Área que responde" ser ela mesma.
        sem_enc = linha_enc is None or re.match(r"(nenhuma|nenhum|-|n/a|nao)\b", linha_enc)
        if linha_area and casa_area(linha_area, area):
            enc, enc_nota = PESO_ENCAMINHAMENTO, "respondeu" + ("" if sem_enc else " (consultou outra área)")
        elif linha_area is None and linha_enc is None:
            enc, enc_nota = PESO_ENCAMINHAMENTO / 2, "sem as linhas finais"
        else:
            enc, enc_nota = 0, "repassou um pedido que era da área"
    nota = conteudo + limpeza + enc
    critico = bool(proib) or altos > 0
    if critico:
        nota = min(nota, TETO_CRITICO)
    return {"caso": caso["id"], "tipo": caso["tipo"], "titulo": caso["titulo"], "nota": round(nota),
            "aprovado": nota >= APROVADO, "critico": critico, "conteudo": round(conteudo, 1),
            "limpeza": limpeza, "encaminhamento": enc, "encaminhamento_nota": enc_nota,
            "deve_atendidos": atendidos, "deve_total": len(caso["deve"]), "faltou": faltou,
            "proibidos": proib, "alertas_promessa": alertas}


# ---------- prompts ----------
def montar_prompt(area, caso):
    return f"""# Avaliação · {area} · {caso['id']}

Você é o gerente da área `{area}` da Área Partners da Save Co. Português do Brasil.

**Como trabalhar (regras da avaliação):**
1. Leia só a skill da área: `skills/{area}/SKILL.md`, os arquivos de `skills/{area}/references/` e os especialistas em
   `skills/{area}/references/especialistas/`. **Não leia** `references/casos-teste.md` nem `registro/avaliacoes/`.
2. Siga o protocolo do gerente (distribuir ao especialista certo, revisar) e a entrega em 3 blocos
   (o que você pediu · o que você também precisa · o que falta e quem fornece).
3. Não acesse HubSpot, GLPI, e-mail nem internet; trabalhe com a base da skill. Se faltar dado, diga quem fornece.
4. Se o pedido não for da sua área, diga a quem vai e por quê, com o que já pode adiantar.
5. Termine **exatamente** com as duas linhas abaixo (pasta da área em `skills/`, ou "nenhuma").
   "Área que responde" é a área dona do pedido. "Encaminhar para" é a área que deve assumir o pedido quando ele
   não é seu; se você responde e só consulta outras áreas, escreva "nenhuma" e cite as consultas no texto.

```
Área que responde: <pasta da área>
Encaminhar para: <pasta da área ou "nenhuma">
```

## Pedido recebido
{chr(10).join('> ' + l for l in caso['entrada'].splitlines())}
"""


# ---------- relatório ----------
def relatorio_md(res, data):
    L = [f"# Avaliação por casos de teste · {data}", "",
         f"Padrão: `infra/casos-teste.md` · pontuação: conteúdo {PESO_CONTEUDO} + limpeza {PESO_LIMPEZA} + encaminhamento "
         f"{PESO_ENCAMINHAMENTO}; falha crítica limita a {TETO_CRITICO}; aprovado com {APROVADO}.", "",
         "| Área | Casos | Respondidos | Acerto | Aprovados | Críticos | Fronteira ok | Armadilha ok |",
         "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for a in res:
        if not a["respondidos"]:
            L.append(f"| {a['area']} | {a['casos']} | 0 | – | – | – | – | – |")
            continue
        fr = [c for c in a["resultados"] if "fronteira" in c["tipo"]]
        ar = [c for c in a["resultados"] if "armadilha" in c["tipo"]]
        L.append(f"| {a['area']} | {a['casos']} | {a['respondidos']} | {a['acerto']} | {a['aprovados']} | {a['criticos']} | "
                 f"{sum(c['aprovado'] for c in fr)}/{len(fr)} | {sum(c['aprovado'] for c in ar)}/{len(ar)} |")
    for a in res:
        if not a["respondidos"]:
            continue
        L += ["", f"## {a['area']} · acerto {a['acerto']}", ""]
        for c in a["resultados"]:
            marca = "aprovado" if c["aprovado"] else ("CRÍTICO" if c["critico"] else "reprovado")
            L.append(f"- **{c['caso']}** ({c['tipo']}) {c['titulo']}: **{c['nota']}** · {marca} · conteúdo "
                     f"{c['deve_atendidos']}/{c['deve_total']} · limpeza {c['limpeza']} · encaminhamento {c['encaminhamento_nota']}")
            for f in c["faltou"]:
                L.append(f"  - faltou: {f}")
            for p in c["proibidos"]:
                L.append(f"  - proibido: {p['ponto']} » {p['trecho']}")
            for al in c["alertas_promessa"][:3]:
                L.append(f"  - auditor de promessas: {al}")
        if a["faltando"]:
            L.append(f"- sem resposta gravada: {', '.join(a['faltando'])}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    modo = ap.add_mutually_exclusive_group(required=True)
    modo.add_argument("--validar", action="store_true")
    modo.add_argument("--preparar", action="store_true")
    modo.add_argument("--pontuar", action="store_true")
    ap.add_argument("--area", action="append", help="área (pasta em skills/); pode repetir")
    ap.add_argument("--registro", default=REGISTRO_PADRAO)
    ap.add_argument("--skills", default=os.path.join(REPO, "skills"))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--data", default=date.today().isoformat())
    a = ap.parse_args()

    skills = os.path.expanduser(a.skills)
    todas = sorted(os.path.basename(p) for p in glob.glob(os.path.join(skills, "*")) if os.path.isfile(os.path.join(p, "SKILL.md")))
    areas = a.area or todas
    for ar in areas:
        if ar not in todas:
            sys.exit(f"área não encontrada: {ar}")
    base = os.path.join(os.path.expanduser(a.registro), "avaliacoes")

    if a.validar:
        total = 0
        for ar in areas:
            cam = os.path.join(skills, ar, "references", "casos-teste.md")
            if not os.path.isfile(cam):
                print(f"{ar:26} SEM casos-teste.md"); total += 1; continue
            casos = ler_casos(cam)
            erros = validar(ar, casos, set(todas))
            total += len(erros)
            print(f"{ar:26} {len(casos)} casos · {'ok' if not erros else str(len(erros)) + ' problema(s)'}")
            for e in erros:
                print(f"    - {e}")
        sys.exit(1 if total else 0)

    if a.preparar:
        n = 0
        for ar in areas:
            casos = ler_casos(os.path.join(skills, ar, "references", "casos-teste.md"))
            pasta = os.path.join(base, ar, "prompts")
            os.makedirs(pasta, exist_ok=True)
            for c in casos:
                with open(os.path.join(pasta, f"{c['id']}.md"), "w", encoding="utf-8") as f:
                    f.write(montar_prompt(ar, c))
                n += 1
        print(f"{n} prompts gravados em {base}/<área>/prompts/ · respostas em {base}/<área>/CT-nn.md")
        return

    aud = carregar_auditor()
    res = []
    for ar in areas:
        casos = ler_casos(os.path.join(skills, ar, "references", "casos-teste.md"))
        resultados, faltando = [], []
        for c in casos:
            resp = ler(os.path.join(base, ar, f"{c['id']}.md"))
            if not resp.strip():
                faltando.append(c["id"]); continue
            resultados.append(pontuar_caso(ar, c, resp, aud))
        acerto = round(sum(r["nota"] for r in resultados) / len(resultados)) if resultados else None
        res.append({"area": ar, "casos": len(casos), "respondidos": len(resultados), "acerto": acerto,
                    "aprovados": sum(r["aprovado"] for r in resultados), "criticos": sum(r["critico"] for r in resultados),
                    "resultados": resultados, "faltando": faltando})
    avaliadas = [r for r in res if r["respondidos"]]
    if not avaliadas:
        sys.exit("nenhuma resposta gravada: rode --preparar e grave as respostas em registro/avaliacoes/<área>/CT-nn.md")
    # rodada com --area: junta ao relatório do mesmo dia em vez de sobrescrever. Antes, "--pontuar --area X" regravava
    # relatorio-<data>.json só com X, e as outras áreas perdiam a nota de acerto no auditor de senioridade.
    areas_rel = {}
    try:
        with open(os.path.join(base, f"relatorio-{a.data}.json"), encoding="utf-8") as f:
            areas_rel = json.load(f).get("areas") or {}
    except (OSError, ValueError):
        pass
    areas_rel.update({r["area"]: r for r in avaliadas})
    saida = {"data": a.data, "versao": 1, "padrao": "infra/casos-teste.md",
             "pesos": {"conteudo": PESO_CONTEUDO, "limpeza": PESO_LIMPEZA, "encaminhamento": PESO_ENCAMINHAMENTO,
                       "teto_critico": TETO_CRITICO, "aprovado": APROVADO},
             "areas": dict(sorted(areas_rel.items()))}
    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, f"relatorio-{a.data}.json"), "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)
    sem_resp = [r for r in res if not r["respondidos"] and r["area"] not in areas_rel]
    with open(os.path.join(base, f"relatorio-{a.data}.md"), "w", encoding="utf-8") as f:
        f.write(relatorio_md(sorted(list(saida["areas"].values()) + sem_resp, key=lambda r: r["area"]), a.data))
    if a.json:
        print(json.dumps(saida, ensure_ascii=False, indent=2))
    else:
        for r in avaliadas:
            print(f"{r['area']:26} acerto {r['acerto']:>3} · {r['aprovados']}/{r['respondidos']} aprovados · {r['criticos']} crítico(s)")
        print(f"\nRelatório: {os.path.join(base, f'relatorio-{a.data}.md')}")


if __name__ == "__main__":
    main()
