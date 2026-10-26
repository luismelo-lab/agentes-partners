"""Máquinas de estado do PRM (02 §4.3, §5, §6.1, §6.6, §7.2, §8.2, §10.2). O código rejeita toda transição que não
esteja aqui, e rejeita quem não pode dispará-la. "parceiro" = titular ou consultor; "sistema" = rotina."""
from .erros import Conflito, SemPermissao

P = "parceiro"


class Maquina:
    def __init__(self, nome, transicoes, finais=(), inicial=None):
        self.nome, self.finais, self.inicial = nome, set(finais), inicial
        self.t = {}
        for (des, para), quem in transicoes.items():
            for de in (des if isinstance(des, tuple) else (des,)):
                self.t[(de, para)] = set(quem)
        self.estados = {e for par in self.t for e in par} | self.finais

    def pode(self, de, para, papel):
        quem = self.t.get((de, para))
        if quem is None:
            return False
        return papel in quem or (papel in ("titular", "consultor") and P in quem)

    def exigir(self, de, para, papel):
        if de in self.finais:
            raise Conflito("Este item já foi encerrado e não muda mais.", codigo="estado_final")
        if (de, para) not in self.t:
            raise Conflito("Esta mudança não é permitida agora.", codigo="transicao_invalida", extra={"de": de, "para": para})
        if not self.pode(de, para, papel):
            raise SemPermissao("Seu perfil não pode fazer esta mudança.")


VIVOS_REG = ("aprovado", "convertido", "prorrogado")
REGISTRO = Maquina("registro", {
    ("rascunho", "em_analise"): {P, "daniela", "jenifer"},
    ("rascunho", "cancelado"): {P, "sistema"},
    ("em_analise", "aprovado"): {"daniela"},
    ("em_analise", "recusado"): {"daniela", "sistema"},
    ("em_analise", "em_conflito"): {"daniela", "jenifer"},
    ("em_analise", "aguardando_parceiro"): {"daniela"},
    ("aguardando_parceiro", "em_analise"): {P, "daniela"},
    ("aguardando_parceiro", "recusado"): {"sistema", "daniela"},
    ("em_conflito", "aprovado"): {"luis"},
    ("em_conflito", "recusado"): {"luis"},
    (VIVOS_REG, "protegido_cliente"): {"sistema"},
    (VIVOS_REG, "expirado"): {"sistema"},
    (VIVOS_REG, "encerrado_sem_contrato"): {"sistema"},
    (VIVOS_REG, "cancelado"): {P},
    (VIVOS_REG + ("protegido_cliente",), "encerrado_fim_parceria"): {"contratos", "sistema"},
    (("aprovado", "convertido"), "prorrogado"): {"sistema", "daniela"},
    ("aprovado", "convertido"): {"sistema", "daniela"},
    ("prorrogado", "convertido"): {"sistema", "daniela"},
    ("protegido_cliente", "expirado"): {"sistema"},
}, finais=("expirado", "encerrado_sem_contrato", "recusado", "cancelado", "encerrado_fim_parceria"), inicial="em_analise")

LEAD_BDR = Maquina("lead_bdr", {
    ("oferecido", "aceito"): {"titular"},
    ("oferecido", "devolvido"): {"titular", "sistema"},
}, finais=("aceito", "devolvido"), inicial="oferecido")

DEMANDA = Maquina("demanda", {
    (("aberta", "reaberta"), "triada"): {"sistema", "daniela"},
    (("aberta", "triada", "reaberta"), "resposta_historico"): {"sistema"},
    (("aberta", "triada", "resposta_historico", "encaminhada_area"), "aguardando_parceiro"): {"daniela", "jenifer", "geovana"},
    ("aguardando_parceiro", "triada"): {P, "daniela"},
    (("aberta", "triada", "resposta_historico"), "encaminhada_area"): {"daniela", "luis"},
    (("aberta", "triada", "resposta_historico", "encaminhada_area"), "respondida"): {"daniela", "jenifer", "geovana", "financeiro", "contratos", "luis"},
    ("respondida", "concluida"): {P, "sistema"},
    ("concluida", "reaberta"): {P},
}, finais=(), inicial="aberta")

EXTRATO = Maquina("extrato_linha", {
    ("previsto", "recebido_pela_save"): {"financeiro"},
    (("previsto", "recebido_pela_save", "calculado"), "em_conferencia"): {"sistema", "financeiro"},
    (("previsto", "recebido_pela_save", "calculado"), "retida_conflito"): {"sistema"},
    ("em_conferencia", "previsto"): {"financeiro", "contratos"},
    ("retida_conflito", "previsto"): {"sistema", "luis"},
    ("retida_conflito", "recebido_pela_save"): {"sistema", "luis"},
    ("recebido_pela_save", "calculado"): {"sistema", "financeiro"},
    ("calculado", "liberado"): {"financeiro"},
    ("liberado", "aguardando_nf"): {"sistema", "financeiro"},
    (("liberado", "aguardando_nf"), "contestada"): {"titular"},
    ("contestada", "aguardando_nf"): {"financeiro", "contratos", "luis"},
    ("aguardando_nf", "pago"): {"financeiro"},
    ("previsto", "cancelada"): {"sistema", "financeiro"},
}, finais=("pago", "cancelada"), inicial="previsto")

CONTESTACAO = Maquina("contestacao", {
    ("aberta", "em_analise"): {"sistema"},
    (("aberta", "em_analise"), "procedente"): {"financeiro", "contratos", "luis"},
    (("aberta", "em_analise"), "improcedente"): {"financeiro", "contratos", "luis"},
}, finais=("procedente", "improcedente"), inicial="aberta")

USUARIO = Maquina("usuario_parceiro", {
    ("convidado", "ativo"): {P, "sistema"},
    ("ativo", "suspenso"): {"daniela", "sistema"},
    ("suspenso", "ativo"): {"daniela"},
    (("ativo", "suspenso", "convidado"), "desativado"): {"daniela", "sistema"},
    ("ativo", "ex_parceiro_extrato"): {"contratos"},
    ("ex_parceiro_extrato", "desativado"): {"contratos", "sistema"},
}, finais=("desativado",), inicial="convidado")

NIVEL = Maquina("nivel_apuracao", {
    ("apurado", "proposta_nivel"): {"sistema"},
    ("proposta_nivel", "aprovado"): {"luis"},
    ("aprovado", "comunicado"): {"daniela"},
}, finais=("comunicado",), inicial="apurado")

CONFLITO = Maquina("conflito", {("aberto", "decidido"): {"luis"}}, finais=("decidido",), inicial="aberto")

TODAS = {m.nome: m for m in (REGISTRO, LEAD_BDR, DEMANDA, EXTRATO, CONTESTACAO, USUARIO, NIVEL, CONFLITO)}
