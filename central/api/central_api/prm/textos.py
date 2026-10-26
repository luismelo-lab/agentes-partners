"""Catálogo único dos textos ao parceiro (02 §14, chaves M-xx). Nenhuma tela inventa frase: tudo sai daqui."""
import json, re
from pathlib import Path

ARQUIVO = Path(__file__).with_name("textos_parceiro.json")
with open(ARQUIVO, encoding="utf-8") as _f:
    _J = json.load(_f)
TEXTOS = _J["textos"]
PROPOSTAS = set(_J.get("_propostas", []))
_VAR = re.compile(r"\{([a-z_]+)\}")


def texto(codigo, **v):
    """Texto do catálogo com as variáveis preenchidas. Variável faltando é erro (não sai texto pela metade)."""
    modelo = TEXTOS[codigo]
    faltam = [n for n in _VAR.findall(modelo) if n not in v]
    if faltam:
        raise KeyError("texto %s sem: %s" % (codigo, ", ".join(faltam)))
    s = _VAR.sub(lambda m: str(v[m.group(1)]), modelo)
    return re.sub(r"([?!.])\.(?=\s|$)", r"\1", s)  # "…empresa?. Responda" → "…empresa? Responda"


def variaveis(codigo):
    return _VAR.findall(TEXTOS[codigo])
