"""Caminhos da Central, todos por variável de ambiente (lacuna L5 do docs/prm/v2/01-inventario-central.md).

Nada aqui depende de o código morar em ~/agentes-partners: o pacote publicado na Azure leva `lib/` junto
(ou aponta CENTRAL_LIB) e os dados vêm de PARTNERS_AP / CENTRAL_ESTEIRA / PRM_DADOS.

  CENTRAL_LIB    pasta com cnpj.py e protecao.py   (padrão: <repositório>/lib, depois ~/agentes-partners/lib)
  PARTNERS_AP    raiz dos dados locais do Mac       (padrão: ~/agentes-partners)
  CENTRAL_REPO   raiz do repositório (skills/, departamentos/)  (padrão: 3 pastas acima deste arquivo)
"""
import os, sys
from pathlib import Path

_AQUI = Path(__file__).resolve()


def repo():
    return Path(os.environ.get("CENTRAL_REPO") or _AQUI.parents[3])


def dados():
    return Path(os.path.expanduser(os.environ.get("PARTNERS_AP") or "~/agentes-partners"))


def lib():
    for c in (os.environ.get("CENTRAL_LIB"), str(repo() / "lib"), str(dados() / "lib")):
        if c and os.path.exists(os.path.join(c, "cnpj.py")):
            return c
    return str(repo() / "lib")


def preparar_lib():
    """Põe a pasta lib/ no sys.path (uma vez)."""
    p = lib()
    if p not in sys.path:
        sys.path.insert(0, p)
    return p
