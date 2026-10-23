#!/usr/bin/env python3
"""Auditoria de senioridade dos agentes · v2 (padrão sênior, `infra/padrao-senior.md`; casos de teste, `infra/casos-teste.md`).

Regra do Luis (22/10/2026): nenhum agente tem conhecimento raso. v2 aprovada pelo Luis em 23/10/2026: a nota deixa de
medir só se o especialista está completo e passa a mostrar também se a área RESPONDE certo.

DUAS NOTAS POR ÁREA
  1. Nota de ESTRUTURA (0 a 100) = 85% especialistas + 15% casos de teste
     - especialistas (como na v1): presença e tamanho das 10 seções, normas, datas, D-números, perguntas e casos de
       referência de cada arquivo em `skills/<área>/references/especialistas/`; média dos especialistas. Área sem a
       pasta cai na heurística sobre SKILL.md + references, com teto de 40.
     - casos de teste (`references/casos-teste.md`): arquivo presente 20 · 5 casos 20 (proporcional) · caso de
       fronteira 15 · caso-armadilha 15 · casos bem formados 30 (entrada, 3+ pontos "Deve conter" com termos,
       1+ "Não pode conter", "Encaminhar para" válido), menos 5 por problema do validador (`avaliar_casos.py --validar`).
  2. Nota de ACERTO (0 a 100) = média dos casos respondidos no relatório de avaliação mais recente da área
     (`registro/avaliacoes/relatorio-<data>.json`, gerado por `infra/avaliar_casos.py --pontuar`).

NOTA FINAL (campo "nota", o que entra na fila e no veredito)
  - com avaliação: 60% estrutura + 40% acerto (PESO_ESTRUTURA, PESO_ACERTO);
  - sem avaliação: a nota de estrutura, com teto de 85 (TETO_SEM_AVALIACAO). Nota 100 só com acerto medido;
  - avaliação com mais de 21 dias (IDADE_MAX_AVALIACAO) vale, mas sai marcada como velha.
Área abaixo de 70 entra na fila de aprofundamento.

É só leitura: não altera nenhuma skill. A saída `--json` mantém os campos da v1 (data, padrao, limiar_fila, media,
no_padrao, areas[] com area, modo, especialistas, nota, veredito, fila, detalhe, falta) e acrescenta versao, pesos e,
por área, nota_estrutura, nota_especialistas, casos_teste, nota_acerto e avaliacao.

Uso:
  python3 infra/auditar_senioridade.py                 → tabela no terminal (estrutura × acerto)
  python3 infra/auditar_senioridade.py --json          → JSON completo (para a consolidação de sexta)
  python3 infra/auditar_senioridade.py --area depto-juridico --detalhe
  python3 infra/auditar_senioridade.py --todas         → inclui as áreas excluídas por padrão
  python3 infra/auditar_senioridade.py --skills ~/.claude/skills   → audita a cópia viva
  python3 infra/auditar_senioridade.py --avaliacoes <pasta>        → outra pasta de relatórios (padrão ~/agentes-partners/registro/avaliacoes)
"""
import argparse, glob, json, os, re, sys, unicodedata
from datetime import date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUIR_PADRAO = set()  # em reconstrução (22/10/2026)
LIMIAR_FILA = 70
TETO_HEURISTICA = 40
# v2 (23/10/2026)
PESO_ESPECIALISTAS, PESO_CASOS = 0.85, 0.15          # dentro da nota de estrutura
PESO_ESTRUTURA, PESO_ACERTO = 0.60, 0.40            # nota final quando há avaliação
TETO_SEM_AVALIACAO = 85
IDADE_MAX_AVALIACAO = 21
AVALIACOES_PADRAO = os.path.join(os.environ.get("PARTNERS_REGISTRO", os.path.expanduser("~/agentes-partners/registro")), "avaliacoes")

# (número, nome, regex sobre o título normalizado, tamanho mínimo em caracteres do corpo da seção)
SECOES = [
    (1, "Entrega única", r"entrega", 200),
    (2, "Domínio técnico", r"dominio|conceitos|mecanica", 1500),
    (3, "Base normativa", r"base normativa|normas|legislacao|base legal", 800),
    (4, "Regras da casa", r"regras da casa|decisoes da save|regras internas", 400),
    (5, "Método", r"metodo|passo a passo|como faz", 800),
    (6, "Perguntas de diagnóstico", r"perguntas", 600),
    (7, "Armadilhas e sinais de alerta", r"armadilha|sinais de alerta|erros", 400),
    (8, "Casos de referência", r"casos?\b|referencia", 600),
    (9, "Fronteiras e escalonamento", r"fronteira|escalonamento|escala", 300),
    (10, "Atualização", r"atualiza|revisao|radar", 150),
]

RX_NORMA = re.compile(
    r"\b(?:Lei(?:\s+Complementar)?|LC|IN(?:\s+RFB)?|Instru[cç][aã]o\s+Normativa|Resolu[cç][aã]o|Res\.|Decreto(?:-Lei)?|"
    r"Portaria|Tema|S[uú]mula(?:\s+Vinculante)?|Parecer|Solu[cç][aã]o\s+de\s+Consulta|SC\s+Cosit|ADI|ADC|ADPF|REsp|EREsp|"
    r"AgInt|RE|Provimento|Of[ií]cio-Circular|Conv[eê]nio|EC|MP)\s*(?:n[ºo°.]?\s*)?"
    r"(?:(?:CMN|CVM|BCB|CGIBS|RFB|MF|PGFN|ICMS|CFOAB|COAF|CGSN|SSE|CARF|STF|STJ|ANPD|SUSEP|CNSP)\s*(?:/\s*\w+\s*)?(?:n[ºo°.]?\s*)?)?\d[\d.]*(?:/\d{2,4})?",
    re.I)
RX_ART = re.compile(r"\barts?\.\s*\d+[\w\-ºo°]*", re.I)
RX_DATA = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)[a-z]*\.?/\d{4}\b", re.I)
RX_DNUM = re.compile(r"\bD\d{1,3}(?:-[a-z])?\b")
RX_BLOCO_PADRAO = re.compile(r"^## (Revis[aã]o do Gerente|Pesquisa e atualiza[cç][aã]o)", re.I)


def norm(s):
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()


def ler(p):
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return ""


def sem_blocos_padrao(texto):
    """Tira os blocos copiados em toda skill (revisão do gerente e pesquisa Big Four): não são conhecimento da área."""
    out, pulando = [], False
    for linha in texto.splitlines():
        if linha.startswith("## "):
            pulando = bool(RX_BLOCO_PADRAO.match(linha))
        if not pulando:
            out.append(linha)
    return "\n".join(out)


def metricas_texto(texto):
    normas = {re.sub(r"\s+", " ", m.group(0)).strip().rstrip(".") for m in RX_NORMA.finditer(texto)}
    artigos = {m.group(0).lower() for m in RX_ART.finditer(texto)}
    return {
        "caracteres": len(texto),
        "normas": len(normas) + len(artigos),
        "datas": len(set(RX_DATA.findall(texto))),
        "d_numeros": len(set(RX_DNUM.findall(texto))),
        "perguntas": sum(1 for l in texto.splitlines() if l.strip().rstrip("*|` ").endswith("?")),
    }


def secoes_do_arquivo(texto):
    """Divide pelo cabeçalho `##` (ou `###` se não houver `##`) e casa cada título com uma das 10 seções."""
    nivel = "## " if re.search(r"^## ", texto, re.M) else "### "
    partes, atual, corpo = [], None, []
    for linha in texto.splitlines():
        if linha.startswith(nivel):
            if atual is not None:
                partes.append((atual, "\n".join(corpo)))
            atual, corpo = linha[len(nivel):].strip(), []
        elif atual is not None:
            corpo.append(linha)
    if atual is not None:
        partes.append((atual, "\n".join(corpo)))
    achadas = {}
    for titulo, corpo in partes:
        t = norm(titulo)
        num = re.match(r"^\s*(\d{1,2})[.)\s]", t)
        alvo = None
        if num and 1 <= int(num.group(1)) <= 10:
            alvo = int(num.group(1))
        else:
            for n, _, rx, _ in SECOES:
                if n not in achadas and re.search(rx, t):
                    alvo = n
                    break
        if alvo and alvo not in achadas:
            achadas[alvo] = corpo
    return achadas


def contar_casos(corpo):
    sub = len(re.findall(r"^#{3,4} ", corpo, re.M))
    itens = len(re.findall(r"^\s*(?:[-*]|\d+[.)])\s+\S", corpo, re.M))
    linhas_tabela = max(0, len([l for l in corpo.splitlines() if l.strip().startswith("|")]) - 2)
    return max(sub, itens if not sub else 0, linhas_tabela)


def avaliar_especialista(caminho):
    texto = ler(caminho)
    secs = secoes_do_arquivo(texto)
    m = metricas_texto(texto)
    falta, pontos = [], 0.0
    detalhe_secoes = []
    for n, nome, _, minimo in SECOES:
        corpo = secs.get(n)
        tam = len(corpo.strip()) if corpo else 0
        ok_pres = corpo is not None
        ok_tam = tam >= minimo
        pontos += (3 if ok_pres else 0) + (3 * min(1.0, tam / minimo) if ok_pres else 0)
        if not ok_pres:
            falta.append(f"seção {n} ({nome}) ausente")
        elif not ok_tam:
            falta.append(f"seção {n} ({nome}) curta: {tam}/{minimo} caracteres")
        detalhe_secoes.append({"n": n, "secao": nome, "presente": ok_pres, "caracteres": tam, "minimo": minimo})
    perg = sum(1 for l in (secs.get(6) or "").splitlines() if l.strip().rstrip("*|` ").endswith("?"))
    casos = contar_casos(secs.get(8) or "")
    pontos += 10 * min(1.0, m["normas"] / 8)
    pontos += 5 * min(1.0, m["datas"] / 5)
    pontos += 5 * min(1.0, m["d_numeros"] / 2)
    pontos += 10 * min(1.0, perg / 10)
    pontos += 10 * min(1.0, casos / 3)
    if m["normas"] < 8:
        falta.append(f"normas citadas: {m['normas']} (mín. 8)")
    if m["datas"] < 5:
        falta.append(f"datas: {m['datas']} (mín. 5)")
    if m["d_numeros"] < 2:
        falta.append(f"D-números: {m['d_numeros']} (mín. 2)")
    if perg < 10:
        falta.append(f"perguntas de diagnóstico: {perg} (mín. 10)")
    if casos < 3:
        falta.append(f"casos de referência: {casos} (mín. 3)")
    return {"arquivo": os.path.relpath(caminho, REPO) if caminho.startswith(REPO) else caminho,
            "nota": round(pontos), "perguntas_diagnostico": perg, "casos": casos, **m,
            "secoes": detalhe_secoes, "falta": falta}


RX_CAMINHO = re.compile(r"(?:~/agentes-partners/)?((?:departamentos|docs|infra)/[\w\-./·]+?\.md)\b")


def referencias_externas(texto_skill):
    """Arquivos .md do repositório que o SKILL.md manda ler (departamentos/, docs/, infra/), exceto os protocolos comuns."""
    comuns = {"infra/protocolo-gerente.md", "infra/protocolo-pesquisa.md", "infra/padrao-entrega.md", "infra/padrao-senior.md",
              "infra/fluxo-unico.md", "infra/porteiro.md", "infra/chamado-ideal.md"}
    achados = []
    for m in RX_CAMINHO.finditer(texto_skill):
        rel = m.group(1)
        cam = os.path.join(REPO, rel)
        if rel not in comuns and os.path.isfile(cam) and cam not in achados:
            achados.append(cam)
    return achados


def heuristica_area(pasta):
    """Área sem `especialistas/`: mede a base existente (SKILL.md + references), com teto de 40."""
    arquivos = [os.path.join(pasta, "SKILL.md")] + sorted(glob.glob(os.path.join(pasta, "references", "**", "*.md"), recursive=True))
    jsons = sorted(glob.glob(os.path.join(pasta, "references", "**", "*.json"), recursive=True))
    externos = referencias_externas(ler(arquivos[0]))
    texto = "\n\n".join(sem_blocos_padrao(ler(a)) for a in arquivos + externos if os.path.exists(a))
    m = metricas_texto(texto)
    tn = norm(texto)
    sinais = {
        1: r"entrega", 2: r"conceito|mecanica|como funciona|glossario", 3: r"\blei\b|\bin rfb\b|\btema\b|resolucao|art\. ",
        4: r"\bd\d{1,3}\b|decisao do luis|regra do luis|pelo luis|aprovad[ao] (?:pelo|em)", 5: r"fluxo|passo|metodo|modo", 6: r"perguntas?",
        7: r"armadilha|alerta|nao fazer|veto|cuidado", 8: r"\bcaso\b|exemplo|case", 9: r"fronteira|escala|outra area|interfaces",
        10: r"revisao|atualiza|radar|data-base",
    }
    cobertas = [n for n, rx in sinais.items() if re.search(rx, tn)]
    tam_json = sum(os.path.getsize(j) for j in jsons)
    pontos = (15 * len(cobertas) / 10 + 8 * min(1.0, m["normas"] / 40) + 4 * min(1.0, m["datas"] / 20)
              + 4 * min(1.0, m["d_numeros"] / 8) + 4 * min(1.0, m["perguntas"] / 20)
              + 5 * min(1.0, (m["caracteres"] + tam_json) / 60000))
    nao_cobertas = [f"{n} ({nome})" for n, nome, _, _ in SECOES if n not in cobertas]
    falta = ["sem references/especialistas/: não segue o padrão sênior (teto de 40)"]
    if nao_cobertas:
        falta.append("sem sinal de: " + ", ".join(nao_cobertas))
    if m["normas"] < 15:
        falta.append(f"normas na base toda: {m['normas']}")
    if m["perguntas"] < 10:
        falta.append(f"perguntas de diagnóstico na base: {m['perguntas']}")
    return {"nota": round(min(TETO_HEURISTICA, pontos)), "modo": "heuristica", "arquivos": len(arquivos),
            "externos": [os.path.relpath(e, REPO) for e in externos],
            "json_bytes": tam_json, "secoes_com_sinal": len(cobertas), **m, "falta": falta}


def avaliar_especialistas_area(pasta):
    area = os.path.basename(pasta.rstrip("/"))
    esp = sorted(glob.glob(os.path.join(pasta, "references", "especialistas", "*.md")))
    esp = [e for e in esp if os.path.basename(e).lower() not in ("readme.md", "leia-me.md", "_modelo.md")]
    if not esp:
        r = heuristica_area(pasta)
        return {"area": area, "especialistas": 0, **r, "veredito": veredito(r["nota"]), "fila": True}
    avals = [avaliar_especialista(e) for e in esp]
    nota = round(sum(a["nota"] for a in avals) / len(avals))
    falta_area = []
    for a in avals:
        for f in a["falta"]:
            falta_area.append(f"{os.path.basename(a['arquivo'])}: {f}")
    return {"area": area, "modo": "padrao", "especialistas": len(avals), "nota": nota, "veredito": veredito(nota),
            "fila": nota < LIMIAR_FILA, "detalhe": avals, "falta": falta_area}


def _avaliar_casos_mod():
    import importlib.util
    cam = os.path.join(os.path.dirname(os.path.abspath(__file__)), "avaliar_casos.py")
    spec = importlib.util.spec_from_file_location("avaliar_casos", cam)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def nota_casos_teste(pasta, pastas_validas):
    """Presença e qualidade mínima de references/casos-teste.md (0 a 100)."""
    cam = os.path.join(pasta, "references", "casos-teste.md")
    if not os.path.isfile(cam):
        return {"nota": 0, "casos": 0, "problemas": ["sem references/casos-teste.md"]}
    av = _avaliar_casos_mod()
    casos = av.ler_casos(cam)
    problemas = av.validar(os.path.basename(pasta), casos, pastas_validas)
    tipos = [c["tipo"] for c in casos]
    bons = [c for c in casos if c["entrada"] and len(c["deve"]) >= av.MIN_DEVE and len(c["nao"]) >= av.MIN_NAO
            and all(it["grupos"] for it in c["deve"] + c["nao"]) and c["encaminhar"]]
    pontos = (20 + 20 * min(1.0, len(casos) / av.MIN_CASOS) + (15 if any("fronteira" in t for t in tipos) else 0)
              + (15 if any("armadilha" in t for t in tipos) else 0) + (30 * len(bons) / len(casos) if casos else 0))
    pontos = max(0, pontos - 5 * len(problemas))
    return {"nota": round(pontos), "casos": len(casos), "bem_formados": len(bons), "problemas": problemas}


def ultima_avaliacao(pasta_avaliacoes, area):
    """Relatório mais recente (relatorio-<data>.json) que traz a área."""
    rels = sorted(glob.glob(os.path.join(os.path.expanduser(pasta_avaliacoes), "relatorio-*.json")), reverse=True)
    for r in rels:
        try:
            with open(r, encoding="utf-8") as f:
                dados = json.load(f)
        except (OSError, ValueError):
            continue
        a = (dados.get("areas") or {}).get(area)
        if a and a.get("respondidos") and a.get("acerto") is not None:
            try:
                idade = (date.today() - date.fromisoformat(str(dados.get("data", ""))[:10])).days
            except ValueError:
                idade = None
            return {"data": dados.get("data"), "arquivo": r, "acerto": a["acerto"], "respondidos": a["respondidos"],
                    "aprovados": a.get("aprovados"), "criticos": a.get("criticos"), "idade_dias": idade,
                    "velha": idade is not None and idade > IDADE_MAX_AVALIACAO}
    return None


def avaliar_area(pasta, pastas_validas=None, pasta_avaliacoes=AVALIACOES_PADRAO):
    r = avaliar_especialistas_area(pasta)
    pastas_validas = pastas_validas or {os.path.basename(pasta)}
    ct = nota_casos_teste(pasta, pastas_validas)
    nota_esp = r["nota"]
    estrutura = round(PESO_ESPECIALISTAS * nota_esp + PESO_CASOS * ct["nota"])
    if r.get("modo") == "heuristica":
        estrutura = min(TETO_HEURISTICA, estrutura)
    av = ultima_avaliacao(pasta_avaliacoes, r["area"])
    if av:
        final = round(PESO_ESTRUTURA * estrutura + PESO_ACERTO * av["acerto"])
    else:
        final = min(TETO_SEM_AVALIACAO, estrutura)
    falta = list(r["falta"])
    falta += [f"casos-teste: {p}" for p in ct["problemas"]]
    if not av:
        falta.append(f"sem avaliação por casos de teste (nota limitada a {TETO_SEM_AVALIACAO}): rode infra/avaliar_casos.py")
    elif av["velha"]:
        falta.append(f"avaliação de {av['data']} com mais de {IDADE_MAX_AVALIACAO} dias")
    elif av["acerto"] < LIMIAR_FILA:
        falta.append(f"acerto {av['acerto']} nos casos de teste (abaixo de {LIMIAR_FILA})")
    r.update({"nota_especialistas": nota_esp, "casos_teste": ct, "nota_estrutura": estrutura,
              "nota_acerto": av["acerto"] if av else None, "avaliacao": av, "nota": final,
              "veredito": veredito(final), "fila": final < LIMIAR_FILA, "falta": falta})
    return r


def veredito(nota):
    return "sênior" if nota >= 70 else "intermediário" if nota >= 45 else "raso"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true", help="saída em JSON")
    ap.add_argument("--area", help="só uma área (nome da pasta em skills/)")
    ap.add_argument("--detalhe", action="store_true", help="mostra o que falta por especialista")
    ap.add_argument("--todas", action="store_true", help="inclui as áreas excluídas por padrão")
    ap.add_argument("--skills", default=os.path.join(REPO, "skills"), help="pasta das skills (padrão: skills/ do repositório)")
    ap.add_argument("--avaliacoes", default=AVALIACOES_PADRAO, help="pasta dos relatórios de avaliar_casos.py")
    a = ap.parse_args()

    pastas = sorted(p for p in glob.glob(os.path.join(os.path.expanduser(a.skills), "*")) if os.path.isfile(os.path.join(p, "SKILL.md")))
    if a.area:
        pastas = [p for p in pastas if os.path.basename(p) == a.area]
        if not pastas:
            sys.exit(f"área não encontrada: {a.area}")
    elif not a.todas:
        pastas = [p for p in pastas if os.path.basename(p) not in EXCLUIR_PADRAO]

    validas = {os.path.basename(p) for p in glob.glob(os.path.join(os.path.expanduser(a.skills), "*"))
               if os.path.isfile(os.path.join(p, "SKILL.md"))}
    res = [avaliar_area(p, validas, a.avaliacoes) for p in pastas]
    res.sort(key=lambda r: (r["nota"], r["area"]))
    com_acerto = [r for r in res if r["nota_acerto"] is not None]
    saida = {"data": date.today().isoformat(), "versao": 2, "padrao": "infra/padrao-senior.md", "limiar_fila": LIMIAR_FILA,
             "pesos": {"especialistas": PESO_ESPECIALISTAS, "casos_teste": PESO_CASOS, "estrutura": PESO_ESTRUTURA,
                       "acerto": PESO_ACERTO, "teto_sem_avaliacao": TETO_SEM_AVALIACAO},
             "media_estrutura": round(sum(r["nota_estrutura"] for r in res) / len(res)) if res else 0,
             "media_acerto": round(sum(r["nota_acerto"] for r in com_acerto) / len(com_acerto)) if com_acerto else None,
             "areas_avaliadas": len(com_acerto),
             "media": round(sum(r["nota"] for r in res) / len(res)) if res else 0,
             "no_padrao": sum(1 for r in res if r["modo"] == "padrao"), "areas": res}
    if a.json:
        print(json.dumps(saida, ensure_ascii=False, indent=2))
        return

    print(f"Auditoria de senioridade v2 · {saida['data']} · {len(res)} áreas · média final {saida['media']} · "
          f"estrutura {saida['media_estrutura']} · acerto {saida['media_acerto'] if saida['media_acerto'] is not None else '–'} "
          f"({saida['areas_avaliadas']} avaliadas) · no padrão: {saida['no_padrao']} · limiar da fila: {LIMIAR_FILA}\n")
    cab = (f"{'Área':26} {'Modo':10} {'Esp.':>4} {'Estr.':>5} {'Acerto':>6} {'Nota':>4}  {'Veredito':13} {'Casos':>5} "
           f"{'Normas':>6} {'Datas':>5} {'D-nº':>4} {'Perg.':>5}  Fila")
    print(cab)
    print("-" * len(cab))
    for r in res:
        ac = r["nota_acerto"]
        print(f"{r['area']:26} {r['modo']:10} {r['especialistas']:>4} {r['nota_estrutura']:>5} "
              f"{(str(ac) + ('*' if r['avaliacao'] and r['avaliacao']['velha'] else '')) if ac is not None else '–':>6} "
              f"{r['nota']:>4}  {r['veredito']:13} {r['casos_teste']['casos']:>5} "
              f"{r['normas']if 'normas' in r else sum(d['normas'] for d in r['detalhe']):>6} "
              f"{r['datas'] if 'datas' in r else sum(d['datas'] for d in r['detalhe']):>5} "
              f"{r['d_numeros'] if 'd_numeros' in r else sum(d['d_numeros'] for d in r['detalhe']):>4} "
              f"{r['perguntas'] if 'perguntas' in r else sum(d['perguntas_diagnostico'] for d in r['detalhe']):>5}  "
              f"{'sim' if r['fila'] else '-'}")
    if a.detalhe or a.area:
        print()
        for r in res:
            print(f"## {r['area']} ({r['nota']}, {r['veredito']})")
            for f in r["falta"][:40]:
                print(f"  - {f}")
            if len(r["falta"]) > 40:
                print(f"  … mais {len(r['falta']) - 40} itens (use --json)")
    else:
        print(f"\nEstr. = 85% especialistas + 15% casos de teste · Acerto = relatório de avaliar_casos.py (* = velho) · "
              f"Nota = 60% Estr. + 40% Acerto (sem acerto: Estr. com teto de {TETO_SEM_AVALIACAO}).")
        print("Use --detalhe para ver o que falta em cada área, ou --json para a consolidação.")


if __name__ == "__main__":
    main()
