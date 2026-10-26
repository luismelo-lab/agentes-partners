"""Erros do PRM com status HTTP e mensagem segura para a tela (nunca dado de cliente nem motivo interno)."""


class PRMErro(Exception):
    status = 400

    def __init__(self, mensagem, campos=None, codigo=None, extra=None):
        super().__init__(mensagem)
        self.mensagem, self.campos, self.codigo, self.extra = mensagem, campos or {}, codigo, extra or {}

    def corpo(self):
        c = {"erro": self.mensagem}
        if self.campos:
            c["campos"] = self.campos
        if self.codigo:
            c["codigo"] = self.codigo
        c.update(self.extra)
        return c


class Invalido(PRMErro):
    status = 422


class SemPermissao(PRMErro):
    status = 403


class NaoEncontrado(PRMErro):
    """404: também para o que existe mas está fora do escopo (PRM-R02: não confirma existência)."""
    status = 404

    def __init__(self, mensagem="Não encontrado."):
        super().__init__(mensagem)


class Conflito(PRMErro):
    status = 409


class NaoAutenticado(PRMErro):
    status = 401
