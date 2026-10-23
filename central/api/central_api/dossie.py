"""Dossiê da empresa entregue ao parceiro: briefing, como a Save pode ajudar, serviços aderentes, cases e abordagem.

O agente (rotina esteira-parceiro) escreve `resultado["dossie"]` como lista de seções:
    [{"titulo": "Retrato da empresa", "paragrafos": ["..."], "itens": ["..."]}, ...]
Este módulo converte para Markdown e para Word no Design System Save (gerar_manual_docx.js, que embute a fonte).
"""
import os, subprocess, tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
GERADOR = RAIZ / "departamentos/produtos/credito-internacional/scripts/gerar_manual_docx.js"
SECOES_MINIMAS = 6


def _textos(x):
    """None ou lista só de textos (uma string solta não vale: viraria um parágrafo por letra)."""
    return x is None or (isinstance(x, list) and all(isinstance(i, str) for i in x))


def _tem_texto(x):
    return isinstance(x, list) and any(i.strip() for i in x)


def valido(dossie):
    """True se há seções suficientes e cada uma tem título e conteúdo (listas de texto)."""
    return (isinstance(dossie, list) and len(dossie) >= SECOES_MINIMAS
            and all(isinstance(s, dict) and isinstance(s.get("titulo"), str) and s["titulo"].strip()
                    and _textos(s.get("paragrafos")) and _textos(s.get("itens"))
                    and (_tem_texto(s.get("paragrafos")) or _tem_texto(s.get("itens"))) for s in dossie))


def texto(dossie):
    return "\n".join(str(x) for s in dossie for x in [s.get("titulo", "")] + list(s.get("paragrafos") or []) + list(s.get("itens") or []))


def para_markdown(titulo, subtitulo, dossie):
    linhas = ["# " + titulo, "", subtitulo, ""]
    for s in dossie:
        linhas += ["## " + s["titulo"], ""]
        linhas += [p + "\n" for p in (s.get("paragrafos") or [])]
        linhas += ["- " + i for i in (s.get("itens") or [])]
        linhas.append("")
    return "\n".join(linhas)


def gerar_docx(md, saida, cabecalho="Dossiê da empresa", selo="Uso do parceiro · Confidencial"):
    """Gera o .docx. Precisa do Node com a biblioteca docx (NODE_PATH=~/.partners-node/node_modules)."""
    # o Word é gerado num nome temporário e renomeado: dois downloads ao mesmo tempo nunca servem arquivo pela metade
    parcial = "%s.%d.part" % (saida, os.getpid())
    with tempfile.TemporaryDirectory() as d:
        arq = os.path.join(d, "dossie.md")
        with open(arq, "w", encoding="utf-8") as f:
            f.write(md)
        env = dict(os.environ, DOC_MD=arq, DOC_VERSAO=os.environ.get("DOC_VERSAO", "Rascunho para o parceiro"), DOC_CABECALHO=cabecalho, DOC_SELO=selo)
        env.setdefault("NODE_PATH", os.path.expanduser("~/.partners-node/node_modules"))
        r = subprocess.run(["node", str(GERADOR), parcial], env=env, capture_output=True, text=True, timeout=120)
    if r.returncode != 0 or not os.path.exists(parcial):
        if os.path.exists(parcial):
            os.unlink(parcial)
        raise RuntimeError("não gerou o Word: " + r.stderr[-300:])
    os.replace(parcial, saida)
    return saida
