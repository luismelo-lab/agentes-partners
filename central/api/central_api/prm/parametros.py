"""Parâmetros do PRM (02-regras-de-negocio.md §3). Padrão em parametros.json; sobreposição sem deploy:
  1. PRM_PARAMETROS=<arquivo.json> com {chave: valor} (configuração do ambiente, Azure App Settings aponta o arquivo no pacote);
  2. tabela `config` do repositório, gravada pela tela da Save com trilha (quem, quando, de, para).
Quem pode mudar cada chave está no próprio arquivo (`quem_muda`)."""
import copy, json, os
from pathlib import Path

from .erros import Invalido, SemPermissao

ARQUIVO = Path(__file__).with_name("parametros.json")
with open(ARQUIVO, encoding="utf-8") as _f:
    _BASE = json.load(_f)["parametros"]


def catalogo():
    """Todos os parâmetros com valor padrão, unidade, marca e dona (para a 07-entrega-dev e a tela de parâmetros)."""
    return copy.deepcopy(_BASE)


class Parametros:
    def __init__(self, repo=None, sobrepor=None):
        self.repo = repo
        self._env = {}
        f = os.environ.get("PRM_PARAMETROS")
        if f and os.path.exists(f):
            with open(f, encoding="utf-8") as fh:
                self._env = json.load(fh)
        self._mem = dict(sobrepor or {})

    def __call__(self, chave):
        if chave in self._mem:
            return self._mem[chave]
        if self.repo is not None:
            linha = self.repo.obter("config", chave)
            if linha is not None:
                return linha["valor"]
        if chave in self._env:
            return self._env[chave]
        if chave not in _BASE:
            raise KeyError("parâmetro desconhecido: %s" % chave)
        return copy.deepcopy(_BASE[chave]["valor"])

    def definir(self, chave, valor):
        """Só para testes e para o servidor local (não grava trilha)."""
        self._mem[chave] = valor

    def alterar(self, chave, valor, ator, agora):
        """Mudança pela tela da Save, com trilha. Só a dona da chave (ou o Luis) muda."""
        if chave not in _BASE:
            raise Invalido("Parâmetro desconhecido.")
        dona = _BASE[chave]["quem_muda"]
        if ator.papel not in ("luis", dona):
            raise SemPermissao("Este parâmetro é da %s." % dona)
        antes = self(chave)
        if type(antes) is not type(valor) and not (isinstance(antes, (int, float)) and isinstance(valor, (int, float))):
            raise Invalido("Tipo de valor diferente do padrão.")
        self.repo.gravar("config", {"chave": chave, "valor": valor, "alterado_por": ator.rotulo(), "alterado_em": agora})
        self.repo.inserir("config_evento", {"chave": chave, "de": antes, "para": valor, "quem": ator.rotulo(), "papel": ator.papel, "quando": agora})
        return valor
