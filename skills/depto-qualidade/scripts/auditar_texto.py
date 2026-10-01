#!/usr/bin/env python3
"""Auditoria de Promessas Comerciais — Qualidade & Ouvidoria (Save Company / Partners).

Marca trechos de risco (promessa de êxito, "sem risco", valor/prazo prometido,
mercantilização, certeza jurídica, caso concreto...) em arquivos .md, .txt ou .docx.

Só lê. Não altera o arquivo de origem. As regras ficam em
../references/regras-promessas.json (edite lá, não aqui).

Uso:
  python3 auditar_texto.py ARQUIVO_OU_PASTA [...] [--saida relatorio.md] [--json]
                          [--marcado PASTA] [--resumo] [--regras outro.json]

  --saida    grava o relatório em Markdown (padrão: imprime na tela)
  --json     imprime o resultado em JSON (para outros scripts)
  --marcado  grava, para cada arquivo, uma cópia .md com os trechos marcados ⟦assim⟧
  --resumo   só contagens por regra e por arquivo, sem trechos (use com material
             que contém dados de clientes — LGPD, minimização)

Código de saída: 0 = sem alerta ALTO/MÉDIO; 1 = há alerta ALTO/MÉDIO; 2 = erro.
"""
import argparse
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

AQUI = Path(__file__).resolve().parent
REGRAS_PADRAO = AQUI.parent / "references" / "regras-promessas.json"
EXTENSOES = {".md", ".txt", ".docx", ".markdown"}
ORDEM = {"ALTO": 0, "MEDIO": 1, "BAIXO": 2, "INFO": 3, "RESSALVA": 4}
ROTULO = {"ALTO": "🔴 ALTO", "MEDIO": "🟠 MÉDIO", "BAIXO": "🟡 BAIXO",
          "INFO": "⚪ INFO", "RESSALVA": "✅ RESSALVA"}
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def normalizar(texto: str) -> str:
    """Minúsculas e sem acento, preservando o comprimento (posição 1:1)."""
    saida = []
    for c in texto:
        base = "".join(ch for ch in unicodedata.normalize("NFD", c)
                       if not unicodedata.combining(ch)).lower()
        saida.append(base if len(base) == 1 else c.lower() if len(c.lower()) == 1 else c)
    return "".join(saida)


def ler_docx(caminho: Path) -> list[str]:
    linhas = []
    with zipfile.ZipFile(caminho) as z:
        partes = ["word/document.xml"] + sorted(
            n for n in z.namelist()
            if re.match(r"word/(header|footer|footnotes|endnotes|comments)\d*\.xml$", n))
        for parte in partes:
            if parte not in z.namelist():
                continue
            raiz = ET.fromstring(z.read(parte))
            for p in raiz.iter(W + "p"):
                pedacos = []
                for el in p.iter():
                    if el.tag == W + "t" and el.text:
                        pedacos.append(el.text)
                    elif el.tag == W + "tab":
                        pedacos.append("\t")
                    elif el.tag in (W + "br", W + "cr"):
                        pedacos.append(" ")
                txt = "".join(pedacos).strip()
                if txt:
                    linhas.append(txt)
    return linhas


def ler(caminho: Path) -> list[tuple[int, str]]:
    """Devolve [(nº da linha/parágrafo, texto)], com espaços repetidos colapsados.

    .docx: um item por parágrafo. .md: um item por linha (a estrutura importa).
    .txt (muitas vezes extraído de PDF, com quebras no meio da frase): as linhas
    seguidas são unidas em parágrafos, para pegar frases partidas.
    """
    limpa = lambda t: re.sub(r"[ \t\u00a0]+", " ", t).strip()
    if caminho.suffix.lower() == ".docx":
        return [(i, limpa(t)) for i, t in enumerate(ler_docx(caminho), 1)]
    brutas = caminho.read_text(encoding="utf-8", errors="replace").splitlines()
    if caminho.suffix.lower() != ".txt":
        return [(i, limpa(t)) for i, t in enumerate(brutas, 1)]
    blocos, atual, inicio = [], [], 1
    for i, t in enumerate(brutas, 1):
        if t.strip():
            if not atual:
                inicio = i
            atual.append(limpa(t))
        elif atual:
            blocos.append((inicio, " ".join(atual)))
            atual = []
    if atual:
        blocos.append((inicio, " ".join(atual)))
    return blocos


def carregar_regras(caminho: Path) -> dict:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    for r in dados["regras"]:
        r["_re"] = re.compile(r["padrao"])
    dados["_ressalva"] = re.compile(dados["ressalvas"]["padrao"])
    dados["_contexto"] = re.compile(dados["contexto_de_regra"]["padrao"])
    dados["_negacao"] = re.compile(dados["negacao"]["padrao"])
    return dados


def auditar_linhas(linhas: list[tuple[int, str]], regras: dict) -> dict:
    achados, ressalvas = [], 0
    secao_de_regra = False  # sob um título como "## Proibido"
    for n, linha in linhas:
        norm = normalizar(linha)
        if norm.lstrip().startswith("#"):
            secao_de_regra = bool(regras["_contexto"].search(norm))
        if regras["_ressalva"].search(norm):
            ressalvas += 1
        linha_de_regra = secao_de_regra or bool(regras["_contexto"].search(norm))
        ocupado = []  # evita duas regras no mesmo trecho
        for r in regras["regras"]:
            for m in r["_re"].finditer(norm):
                ini, fim = m.span()
                if any(ini < b and fim > a for a, b in ocupado):
                    continue
                ocupado.append((ini, fim))
                sev = r["severidade"]
                nota = ""
                if r.get("negavel") and regras["_negacao"].search(norm[max(0, ini - 40):ini]):
                    sev, nota = "RESSALVA", "negação antes do termo (ex.: 'não garantimos')"
                elif linha_de_regra:
                    sev, nota = "INFO", "linha fala sobre a regra (provável falso positivo)"
                a, b = max(0, ini - 70), min(len(linha), fim + 70)
                trecho = (("…" if a > 0 else "") + linha[a:ini] + "»" + linha[ini:fim] + "«"
                          + linha[fim:b] + ("…" if b < len(linha) else ""))
                achados.append({"linha": n, "inicio": ini, "fim": fim, "regra": r["id"],
                                "categoria": r["categoria"], "severidade": sev,
                                "termo": linha[ini:fim], "trecho": trecho,
                                "explicacao": r["explicacao"], "sugestao": r["sugestao"],
                                "nota": nota})
    alertas_promessa = [a for a in achados if a["severidade"] in ("ALTO", "MEDIO")
                        and a["categoria"] in ("Promessa de êxito", "Promessa de valor",
                                               "Promessa de prazo")]
    alerta_doc = bool(alertas_promessa) and ressalvas == 0
    achados.sort(key=lambda x: (ORDEM[x["severidade"]], x["linha"]))
    return {"achados": achados, "linhas_com_ressalva": ressalvas,
            "alerta_documento": alerta_doc, "total_linhas": len(linhas)}


def marcar(linhas: list[tuple[int, str]], achados: list[dict]) -> str:
    por_linha = {}
    for a in achados:
        if a["severidade"] in ("ALTO", "MEDIO", "BAIXO"):
            por_linha.setdefault(a["linha"], []).append(a)
    saida = []
    for n, linha in linhas:
        for a in sorted(por_linha.get(n, []), key=lambda x: -x["inicio"]):
            linha = (linha[:a["inicio"]] + "⟦" + linha[a["inicio"]:a["fim"]] + "⟧^"
                     + a["regra"] + linha[a["fim"]:])
        saida.append(linha)
    return "\n".join(saida) + "\n"


def coletar(entradas: list[str]) -> list[Path]:
    arquivos = []
    for e in entradas:
        p = Path(e).expanduser()
        if p.is_dir():
            arquivos += sorted(f for f in p.rglob("*") if f.is_file()
                               and f.suffix.lower() in EXTENSOES and not f.name.startswith("~$"))
        elif p.is_file():
            arquivos.append(p)
        else:
            print(f"aviso: não encontrado: {p}", file=sys.stderr)
    return arquivos


def curto(caminho: str) -> str:
    return caminho.replace(str(Path.home()), "~")


def contar(achados, sev):
    return sum(1 for a in achados if a["severidade"] == sev)


def relatorio_md(resultados: dict, resumo: bool, regras: dict) -> str:
    L = ["# Auditoria de Promessas Comerciais — relatório",
         f"Regras: v{regras['versao']} · Arquivos: {len(resultados)} · "
         "Rascunho para revisão humana (Qualidade → Jurídico quando houver dúvida).", "",
         "| Arquivo | 🔴 Alto | 🟠 Médio | 🟡 Baixo | ⚪ Info | ✅ Ressalva | Linhas c/ ressalva | Alerta de documento |",
         "|---|---|---|---|---|---|---|---|"]
    ocultos = 0
    for arq, res in resultados.items():
        if resumo and "erro" not in res and not any(
                a["severidade"] in ("ALTO", "MEDIO", "BAIXO") for a in res["achados"]):
            ocultos += 1
            continue
        if "erro" in res:
            L.append(f"| {curto(arq)} | erro: {res['erro']} ||||||| |")
            continue
        ac = res["achados"]
        L.append(f"| {curto(arq)} | {contar(ac,'ALTO')} | {contar(ac,'MEDIO')} | {contar(ac,'BAIXO')} | "
                 f"{contar(ac,'INFO')} | {contar(ac,'RESSALVA')} | {res['linhas_com_ressalva']} | "
                 f"{'⚠️ promessa sem ressalva' if res['alerta_documento'] else '—'} |")
    if ocultos:
        L.append(f"| *{ocultos} arquivo(s) sem alerta, omitidos no modo --resumo* ||||||| |")
    por_regra = {}
    for res in resultados.values():
        for a in res.get("achados", []):
            por_regra.setdefault((a["regra"], a["categoria"], a["severidade"]), 0)
            por_regra[(a["regra"], a["categoria"], a["severidade"])] += 1
    if por_regra:
        L += ["", "## Por regra", "| Regra | Categoria | Severidade | Ocorrências |", "|---|---|---|---|"]
        for (rid, cat, sev), q in sorted(por_regra.items(), key=lambda x: (ORDEM[x[0][2]], x[0][0])):
            L.append(f"| {rid} | {cat} | {ROTULO[sev]} | {q} |")
    if resumo:
        return "\n".join(L) + "\n"
    for arq, res in resultados.items():
        ac = res.get("achados", [])
        if not ac:
            continue
        L += ["", f"## {curto(arq)}"]
        if res["alerta_documento"]:
            L.append("> ⚠️ O documento tem promessa de êxito/valor/prazo e nenhuma ressalva "
                     "(ex.: 'sujeito à análise', 'não há garantia de resultado').")
        L += ["", "| # | Linha | Severidade | Regra | Trecho | Por quê / sugestão |", "|---|---|---|---|---|---|"]
        for i, a in enumerate(ac, 1):
            porque = a["explicacao"] + " → " + a["sugestao"]
            if a["nota"]:
                porque = f"({a['nota']}) " + porque
            trecho = a["trecho"].replace("|", "\\|")
            L.append(f"| {i} | {a['linha']} | {ROTULO[a['severidade']]} | {a['regra']} {a['categoria']} | "
                     f"{trecho} | {porque.replace('|', '/')} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entradas", nargs="+")
    ap.add_argument("--saida")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--marcado")
    ap.add_argument("--resumo", action="store_true")
    ap.add_argument("--regras", default=str(REGRAS_PADRAO))
    args = ap.parse_args()

    try:
        regras = carregar_regras(Path(args.regras).expanduser())
    except Exception as e:  # noqa: BLE001
        print(f"erro ao ler regras: {e}", file=sys.stderr)
        sys.exit(2)
    arquivos = coletar(args.entradas)
    if not arquivos:
        print("nenhum arquivo .md/.txt/.docx encontrado", file=sys.stderr)
        sys.exit(2)

    resultados = {}
    for f in arquivos:
        try:
            linhas = ler(f)
            res = auditar_linhas(linhas, regras)
            resultados[str(f)] = res
            tem_alerta = any(a["severidade"] in ("ALTO", "MEDIO", "BAIXO") for a in res["achados"])
            if args.marcado and not args.resumo and tem_alerta:  # só copia o que tem alerta (LGPD)
                destino = Path(args.marcado).expanduser()
                destino.mkdir(parents=True, exist_ok=True)
                (destino / (f.stem + ".marcado.md")).write_text(marcar(linhas, res["achados"]), encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            resultados[str(f)] = {"erro": str(e)}

    if args.json:
        saida = json.dumps(resultados if not args.resumo else {
            k: {s: contar(v.get("achados", []), s) for s in ORDEM} for k, v in resultados.items()},
            ensure_ascii=False, indent=2)
    else:
        saida = relatorio_md(resultados, args.resumo, regras)
    if args.saida:
        Path(args.saida).expanduser().write_text(saida, encoding="utf-8")
        print(f"relatório gravado em {args.saida}")
    else:
        print(saida)
    grave = any(a["severidade"] in ("ALTO", "MEDIO")
                for r in resultados.values() for a in r.get("achados", []))
    sys.exit(1 if grave else 0)


if __name__ == "__main__":
    main()
