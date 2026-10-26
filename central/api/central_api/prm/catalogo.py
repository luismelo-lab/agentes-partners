"""Catálogo único de tipos de demanda (U2): junta os 23 tipos com SLA da célula da Daniela
(skills/celula-daniela/references/sla.json) e os 29 pedidos da Central de Agentes (skills/central-agentes/references/catalogo.json),
com a tradução para os tipos que o parceiro vê (02 §7.1). Um código só por tipo; P-NNNN e E-NNNN ficam como id de origem.

Caminhos por variável (L5): PRM_SLA_JSON e PRM_CATALOGO_CENTRAL; sem os arquivos, valem os prazos embutidos abaixo.
"""
import json, os

from ..caminhos import repo

# tipo na tela do parceiro → (código interno, dono, 1ª resposta d.u., solução d.u., urgente) — 02 §7.1 (fallback se o sla.json faltar)
PARCEIRO = {
    "status":       {"rotulo": "Andamento de empresa", "codigo": "COM-STATUS", "dono": "daniela", "area": "Central Masters"},
    "documento":    {"rotulo": "Documento", "codigo": "TEC-DOCUMENTOS", "dono": "geovana", "area": "Técnico"},
    "tecnica":      {"rotulo": "Dúvida técnica", "codigo": "TEC-DUVIDA", "codigo_encerrado": "TEC-REANALISE", "dono": "geovana", "area": "Técnico"},
    "reuniao":      {"rotulo": "Reunião", "codigo": "COM-REUNIAO", "codigo_juridico": "JUR-REUNIAO", "dono": "daniela", "area": "Central Masters"},
    "contrato":     {"rotulo": "Contrato", "codigo": "CTR-ENVIO", "dono": "contratos", "area": "Contratos"},
    "material":     {"rotulo": "Material", "codigo": "MKT-MATERIAL", "dono": "daniela", "area": "Central Masters"},
    "remuneracao":  {"rotulo": "Remuneração", "codigo": "REP-COMISSAO", "dono": "financeiro", "area": "Operações de Canal"},
    "notificacao":  {"rotulo": "Notificação da Receita recebida pela empresa", "codigo": "JUR-NOTIFICACAO", "dono": "daniela", "area": "Jurídico", "urgente": True},
    "reclamacao":   {"rotulo": "Reclamação", "codigo": "QLD-RECLAMACAO", "dono": "daniela", "area": "Qualidade", "urgente": True},
    "outro":        {"rotulo": "Outro", "codigo": "OUT-OUTROS", "dono": "daniela", "area": "Central Masters"},
}
PRAZOS_PADRAO = {"COM-STATUS": (0, 1), "TEC-DOCUMENTOS": (0, 2), "TEC-DUVIDA": (0, 3), "TEC-REANALISE": (1, 5), "COM-REUNIAO": (0, 2), "JUR-REUNIAO": (0, 2),
                 "CTR-ENVIO": (0, 2), "MKT-MATERIAL": (0, 1), "REP-COMISSAO": (0, 5), "JUR-NOTIFICACAO": (0, None), "QLD-RECLAMACAO": (0, 3), "OUT-OUTROS": (1, 5)}
_cache = {}


def _ler(var, rel):
    f = os.environ.get(var) or str(repo() / rel)
    try:
        with open(f, encoding="utf-8") as fh:
            return json.load(fh).get("tipos") or {}
    except (OSError, ValueError):
        return {}


def tipos():
    """{código: {rotulo, area, primeira_resposta_du, solucao_du, validado, fonte, ...}} — uma tabela só."""
    if "t" not in _cache:
        sla = _ler("PRM_SLA_JSON", "skills/celula-daniela/references/sla.json")
        central = _ler("PRM_CATALOGO_CENTRAL", "skills/central-agentes/references/catalogo.json")
        out = {}
        for k, (p, s) in PRAZOS_PADRAO.items():
            out[k] = {"codigo": k, "primeira_resposta_du": p, "solucao_du": s, "validado": False, "fonte": "02 §7.1"}
        for k, v in sla.items():
            out[k] = {**out.get(k, {}), "codigo": k, "rotulo": v.get("rotulo"), "area": v.get("area"), "primeira_resposta_du": v.get("primeira_resposta_du"),
                      "solucao_du": v.get("solucao_du"), "urgente": bool(v.get("urgente")), "dados_minimos": v.get("dados_minimos") or [],
                      "validado": v.get("validado") is True, "fonte": "sla.json"}
        for k, v in central.items():
            out["CA-" + k] = {"codigo": "CA-" + k, "rotulo": v.get("rotulo"), "area": v.get("celula"), "skill": v.get("skill"), "origem_interna": True,
                              "primeira_resposta_du": 0, "solucao_du": 1, "validado": False, "fonte": "central-agentes/catalogo.json"}
        _cache["t"] = out
    return _cache["t"]


def para_parceiro():
    """Lista de tipos que o parceiro escolhe (8 botões + notificação e reclamação, 02 §7.1)."""
    return [{"tipo": k, "rotulo": v["rotulo"], "urgente": bool(v.get("urgente"))} for k, v in PARCEIRO.items()]


def codigo(tipo_tela, negocio_encerrado=False, apoio_juridico=False):
    p = PARCEIRO[tipo_tela]
    if negocio_encerrado and p.get("codigo_encerrado"):
        return p["codigo_encerrado"]
    if apoio_juridico and p.get("codigo_juridico"):
        return p["codigo_juridico"]
    return p["codigo"]
