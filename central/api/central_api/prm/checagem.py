"""Serviço único de checagem pela raiz do CNPJ (U1) e regra única de cliente protegido (L14).

Antes eram quatro checagens com regras diferentes (negocio_ativo.py, esteira.solicitar, rotina esteira-parceiro e
crm_checagem.py). Agora a consulta de Lucro Real, o registro de oportunidade e o pedido de dossiê perguntam aqui.

Fontes, nesta ordem (02 §4.2 passo 3): registros vivos do PRM; espelho do HubSpot (hs_negocio, todos os funis); índice
HMAC da Central (negocio_ativo.py) quando o espelho não tem a raiz. Sem índice e sem espelho: falha fechada.

Resultado interno (nunca vai ao parceiro, PRM-R21):
  livre · proprio_usuario · proprio_escritorio · outro_parceiro · cliente_save · indice_ausente

Regra de "protegido" (parâmetro protecao.regra_ativo, decisão DL-01):
  contrato_12m    ganho protege até 12 meses após o último recebimento registrado pelo Financeiro — padrão (recomendação
                  da DL-01); sem recebimento registrado o ganho continua protegido (falha fechada)
  qualquer_idade  negócio aberto ou ganho de qualquer idade protege (regra do índice de 23/10/2026)
"""
from datetime import timedelta

from .. import negocio_ativo as NA
from . import calendario as CAL

ESCRITORIO = lambda n: n.get("master_id") or n.get("parceiro_id")  # noqa: E731


def registros_vivos(app, raiz_hmac):
    vivos = set(app.param("registro.estados_vivos"))
    return [r for r in app.repo.listar("registro", cnpj_raiz_hmac=raiz_hmac) if r.get("estado") in vivos]


def _ultimo_recebimento(app, deal_id):
    datas = [m["quando"] for m in app.repo.listar("extrato_movimento", deal_id=deal_id) if m.get("tipo") == "recebimento"]
    return max(datas) if datas else None


def negocio_protege(app, n):
    """A regra única: este negócio do espelho protege a raiz hoje?"""
    st = n.get("status")
    if st == "aberto":
        return True
    if st != "ganho":
        return False
    if app.param("protecao.regra_ativo") == "qualquer_idade":
        return True
    ref = _ultimo_recebimento(app, n["deal_id"])
    if not ref:  # sem fonte de recebimentos (Fase 1: 0 de 1.696 ganhos têm recebido) não dá para saber se o contrato acabou: protege
        return True
    meses = app.param("registro.protecao_pos_contrato_meses")
    return CAL.dia(app.agora()) <= CAL.dia(ref) + timedelta(days=round(meses * 30.44))


def classificar(app, cnpj, parceiro_id, usuario_id=None):
    """Classificação da raiz para quem quer registrar. Devolve {resultado, registro, negocio}."""
    raiz_h = app.hmac_raiz(cnpj)
    regs = registros_vivos(app, raiz_h)
    meu = [r for r in regs if r["parceiro_id"] == parceiro_id and usuario_id and r.get("usuario_id") == usuario_id]
    if meu:
        return {"resultado": "proprio_usuario", "registro": meu[0], "negocio": None}
    esc = [r for r in regs if r["parceiro_id"] == parceiro_id]
    if esc:
        return {"resultado": "proprio_escritorio", "registro": esc[0], "negocio": None}
    espelho = app.repo.listar("negocio", cnpj_raiz_hmac=raiz_h)
    ativos = [n for n in espelho if negocio_protege(app, n)]
    proprios = [n for n in ativos if ESCRITORIO(n) == parceiro_id]
    if proprios:
        return {"resultado": "proprio_escritorio", "registro": None, "negocio": sorted(proprios, key=lambda n: n.get("criado_em") or "")[0]}
    if regs:
        return {"resultado": "outro_parceiro", "registro": None, "negocio": None}
    if ativos:
        return {"resultado": "outro_parceiro" if any(ESCRITORIO(n) for n in ativos) else "cliente_save", "registro": None, "negocio": None}
    if espelho:  # o espelho conhece a raiz e a regra diz que não protege mais: livre (o índice não decide sozinho)
        return {"resultado": "livre", "registro": None, "negocio": None}
    idx = NA.tem_negocio_ativo(cnpj)  # o espelho não conhece a raiz: vale o índice HMAC (falha fechada sem ele)
    if idx is None:
        return {"resultado": "indice_ausente", "registro": None, "negocio": None}
    return {"resultado": "cliente_save" if idx else "livre", "registro": None, "negocio": None}


def protecao_para_consulta(app, parceiro_id, usuario_id=None):
    """Função para regime.consultar(protegido=...): a consulta de Lucro Real usa a mesma regra do registro.
    False = pode consultar; texto = motivo interno da resposta neutra; None = índice ausente (falha fechada)."""
    def f(cnpj):
        r = classificar(app, cnpj, parceiro_id, usuario_id)["resultado"]
        return {"livre": False, "proprio_usuario": False, "proprio_escritorio": False, "indice_ausente": None,
                "outro_parceiro": "registro_ou_negocio_de_outro_parceiro", "cliente_save": "negocio_ativo"}[r]
    return f


def historico_raiz(app, raiz_hmac):
    """Fatos da raiz para a Save (fila de registros e ficha de conflito): sem nome de cliente, sem CNPJ em claro."""
    regs = app.repo.listar("registro", cnpj_raiz_hmac=raiz_hmac)
    negs = app.repo.listar("negocio", cnpj_raiz_hmac=raiz_hmac)
    return {"registros": [{"registro_id": r["registro_id"], "parceiro_id": r["parceiro_id"], "estado": r["estado"], "carimbo": r.get("carimbo"),
                           "evidencia_tipo": r.get("evidencia_tipo")} for r in sorted(regs, key=lambda r: r.get("carimbo") or "")],
            "negocios": [{"deal_id": n["deal_id"], "pipeline": n.get("pipeline"), "etapa": n.get("etapa"), "status": n.get("status"),
                          "escritorio": ESCRITORIO(n), "criado_em": n.get("criado_em"), "fechado_em": n.get("fechado_em")} for n in negs]}
