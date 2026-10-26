"""Auditor único de texto (U5): tudo que entra do parceiro passa pelo bloqueio de dado pessoal (PRM-R06, R75 → M-90) e
tudo que sai ao parceiro em texto livre passa pelo auditor de promessas da Qualidade (ALTO/MÉDIO bloqueia o envio).
Junta o que estava em quatro lugares: lib/protecao.py (máscara e rótulos), esteira.trava_regex (lista de bloqueio do
dossiê), skills/depto-qualidade/scripts/auditar_texto.py (promessas) e o texto do catálogo (textos_parceiro.json).

  dados_pessoais(texto)        → lista de categorias achadas (cpf, documento, bancario, senha); vazia = pode gravar
  exigir_sem_dado_pessoal(...) → levanta Invalido com o M-90
  promessas(texto)             → (ok, achados) do auditor de promessas; falha fechada
  auditar_saida(texto, rigor)  → (ok, motivos) para texto livre ("resposta") ou dossiê ("dossie": + lista de bloqueio)
"""
import hashlib, json, os, re, subprocess, sys, tempfile, threading
from pathlib import Path

from ..caminhos import preparar_lib, repo
from .erros import Invalido
from .textos import texto as T

preparar_lib()
import protecao  # noqa: E402

_CPF = re.compile(r"(?<![\d.])(\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})(?![\d])")
_ROT = re.compile(r"(?i)\b(rg|identidade|cnh|ag[eê]ncia|conta(?: corrente)?|c/c|chave pix|pix|senha)\b\s*[:nº°.-]*\s*(?=\S*\d)\S+")
_CATEG = {"rg": "documento", "identidade": "documento", "cnh": "documento", "senha": "senha"}
_cache, _trava = {}, threading.Lock()


def dados_pessoais(texto):
    t = str(texto or "")
    achou = []
    if _CPF.search(t):
        achou.append("cpf")
    for m in _ROT.finditer(t):
        k = m.group(1).lower()
        achou.append(_CATEG.get(k, "bancario"))
    if protecao.ROTULO.search(t) and not achou:
        achou.append("documento")
    return sorted(set(achou))


def exigir_sem_dado_pessoal(campos):
    """campos: {nome: texto}. Bloqueia o envio inteiro com o M-90 (o texto não é gravado)."""
    ruins = {k: T("M-90") for k, v in campos.items() if v and dados_pessoais(v)}
    if ruins:
        raise Invalido(T("M-90"), campos=ruins, codigo="M-90")


def _script():
    for c in (os.environ.get("PRM_AUDITOR"), str(repo() / "skills/depto-qualidade/scripts/auditar_texto.py"),
              os.path.expanduser("~/.claude/skills/depto-qualidade/scripts/auditar_texto.py")):
        if c and os.path.exists(c):
            return c
    return None


def promessas(texto):
    """(ok, achados). ok só com 0 ALTO e 0 MÉDIO. Sem auditor ou com erro, reprova (falha fechada)."""
    chave = hashlib.sha256(str(texto).encode()).hexdigest()
    with _trava:
        if chave in _cache:
            return _cache[chave]
    s = _script()
    if not s:
        return False, [{"nivel": "ERRO", "regra": "auditor indisponível"}]
    try:
        with tempfile.TemporaryDirectory() as d:
            arq = os.path.join(d, "texto.md")
            with open(arq, "w", encoding="utf-8") as f:
                f.write(str(texto))
            r = subprocess.run([sys.executable, "-I", s, arq, "--json"], capture_output=True, text=True, encoding="utf-8", timeout=60)
        if r.returncode == 2:
            raise RuntimeError("auditor com erro")
        res = json.loads(r.stdout or "{}")
        achados = [a for x in res.values() for a in ((x.get("achados") if isinstance(x, dict) else x) or [])]
        graves = [{"nivel": a.get("severidade") or a.get("nivel"), "regra": a.get("regra"), "categoria": a.get("categoria")} for a in achados
                  if str(a.get("severidade") or a.get("nivel") or "").upper() in ("ALTO", "MEDIO", "MÉDIO")]
        out = (r.returncode == 0 and not graves, graves)
    except (subprocess.SubprocessError, OSError, ValueError, RuntimeError, AttributeError):
        out = (False, [{"nivel": "ERRO", "regra": "auditor indisponível"}])
    with _trava:
        _cache[chave] = out
    return out


def auditar_saida(texto, rigor="resposta"):
    """Texto livre escrito por pessoa (resposta de demanda, motivo de decisão) antes de sair ao parceiro."""
    motivos = []
    if dados_pessoais(texto):
        motivos.append("dado pessoal (M-90)")
    if rigor == "dossie":
        from .. import esteira
        ok, ach = esteira.auditar(str(texto))
        if not ok:
            motivos += ["regra %s" % a["trava"] if "trava" in a else "auditor de promessas" for a in ach] or ["auditor de promessas"]
    else:
        ok, ach = promessas(texto)
        if not ok:
            motivos += ["auditor: %s (%s)" % (a.get("categoria") or a.get("regra"), a.get("nivel")) for a in ach] or ["auditor de promessas"]
    return not motivos, motivos


def limpar(texto):
    """Máscara de telefone, CNPJ sem pontuação, rótulos (lib/protecao.limpo) para texto que fica guardado."""
    return protecao.limpo(texto)
