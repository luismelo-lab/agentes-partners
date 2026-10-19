"""Autorização no backend: o servidor decide (docs/sso-entra/diagnostico-e-plano.md §3 e §4).

Três checagens em toda requisição: token válido (token.py) → papel exigido pela ação → dono do registro.
Ter e-mail corporativo não dá acesso: sem papel atribuído no Entra, a resposta é 403.
"""

GESTOR, MASTERS, BDR, TECNICA, LEITURA, AGENTE = "Partners.Gestor", "Partners.Masters", "Partners.BDR", "Partners.Tecnica", "Partners.Leitura", "Agentes.Processar"
PAPEIS_USUARIO = {GESTOR, MASTERS, BDR, TECNICA, LEITURA}

# papel → pessoa da Central (a caixa de cada uma); o Gestor vê todas e pode "ver como" no servidor
PESSOA_DO_PAPEL = {GESTOR: "luis", MASTERS: "daniela", BDR: "jenifer", TECNICA: "geovana"}

# ação → papéis que podem executá-la
ACOES = {
    "ver_painel":           {GESTOR, MASTERS, BDR, TECNICA, LEITURA},
    "ver_dados_cliente":    {GESTOR, MASTERS, BDR, TECNICA},
    "ver_como":             {GESTOR},
    "aprovar_chamado":      {GESTOR, MASTERS, BDR, TECNICA},
    "decidir_recorrencia":  {GESTOR, TECNICA},
    "decidir_conselho":     {GESTOR},
    "marcar_demanda":       {GESTOR, MASTERS, BDR, TECNICA},
    "criar_pedido":         {GESTOR, MASTERS, BDR, TECNICA},
    "liberar_envio":        {GESTOR},
    "processar_pendencias": {AGENTE},
    "gravar_resultado":     {AGENTE},
}
# ações em que a analista só mexe no que é dela (dono = pessoa do registro)
DONO_OBRIGATORIO = {"aprovar_chamado", "marcar_demanda", "decidir_recorrencia"}


class SemPermissao(Exception):
    """403: identidade válida, mas sem o papel ou sem ser dona do registro."""


def pessoa(identidade):
    """Pessoa da Central pela qual a identidade responde (None para Leitura e agentes)."""
    for p in (GESTOR, MASTERS, BDR, TECNICA):
        if p in identidade["papeis"]:
            return PESSOA_DO_PAPEL[p]
    return None


def exigir(identidade, acao, registro=None):
    """Levanta SemPermissao se a identidade não pode executar a ação (no registro, quando houver)."""
    permitidos = ACOES.get(acao)
    if permitidos is None:
        raise SemPermissao(f"ação desconhecida: {acao}")
    papeis = set(identidade["papeis"])
    if identidade["tipo"] == "usuario" and not (papeis & PAPEIS_USUARIO):
        raise SemPermissao("sem papel atribuído na Central")
    if not (papeis & permitidos):
        raise SemPermissao(f"o papel não permite '{acao}'")
    if acao in DONO_OBRIGATORIO and registro is not None and GESTOR not in papeis:
        if registro.get("pessoa") != pessoa(identidade):
            raise SemPermissao("o registro é de outra pessoa")
    return True
