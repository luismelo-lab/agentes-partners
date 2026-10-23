#!/usr/bin/env python3
"""Autor dos registros do painel Central Partners (ajuste A3 da avaliação de publicação, 23/10/2026).

O db do Artifact aceita gravação de qualquer pessoa que abra o link. As rotinas só processam registros cujo id de conta
(solicitante_id, por_id, aprovado_por_id, recusado_por_id, decisao.por_id) está em infra/portal-contas.json e mapeia
para a pessoa que o registro diz ser. O resto é descartado e vira alerta ao Luis (registro/portal-alertas.json).

Uso: python3 lib/portal_contas.py alertas                 → ids desconhecidos que tentaram gravar
     python3 lib/portal_contas.py registrar <pessoa> <id>   → inclui a conta (só depois de o Luis confirmar quem é)
"""
import json, os, sys
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AP = os.path.expanduser("~/agentes-partners")
CONTAS = os.environ.get("PORTAL_CONTAS") or os.path.join(REPO, "infra", "portal-contas.json")
ALERTAS = os.environ.get("PORTAL_ALERTAS") or os.path.join(AP, "registro", "portal-alertas.json")
PESSOAS = ("luis", "daniela", "jenifer", "geovana")


def contas():
    try: return json.load(open(CONTAS)).get("contas") or {}
    except (OSError, ValueError): return {}


def conferir(pessoa, conta_id, esperado=None):
    """(True, "") se a conta é conhecida, é de `pessoa` e (se dado) `pessoa` é o `esperado` (a dona da ação)."""
    if pessoa not in PESSOAS: return False, f"pessoa desconhecida ({pessoa!r})"
    if esperado is not None and pessoa != esperado: return False, f"{pessoa} não pode decidir o que é de {esperado}"
    if not conta_id: return False, "registro sem id de conta"
    dono = contas().get(conta_id)
    if not dono: return False, f"conta {conta_id} fora da lista das quatro contas"
    if dono != pessoa: return False, f"conta {conta_id} é de {dono}, não de {pessoa}"
    return True, ""


def alertar(colecao, doc_id, motivo, pessoa=None, conta_id=None):
    """Guarda o descarte para o Luis (sem o conteúdo do registro)."""
    try: A = json.load(open(ALERTAS))
    except (OSError, ValueError): A = []
    chave = f"{colecao}/{doc_id}/{motivo}"
    if any(a.get("chave") == chave for a in A): return
    A.append({"chave": chave, "quando": datetime.now().isoformat(timespec="minutes"), "colecao": colecao, "doc": doc_id,
              "pessoa": pessoa, "conta_id": conta_id, "motivo": motivo})
    os.makedirs(os.path.dirname(ALERTAS), exist_ok=True)
    json.dump(A[-500:], open(ALERTAS, "w"), ensure_ascii=False, indent=1)


def registrar(pessoa, conta_id):
    if pessoa not in PESSOAS: sys.exit(f"pessoa deve ser uma de {PESSOAS}")
    d = json.load(open(CONTAS)); d.setdefault("contas", {})[conta_id] = pessoa
    json.dump(d, open(CONTAS, "w"), ensure_ascii=False, indent=1); print(f"{conta_id} → {pessoa}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["registrar"] and len(a) == 3: registrar(a[1], a[2])
    elif a[:1] == ["alertas"]:
        try: print(json.dumps(json.load(open(ALERTAS)), ensure_ascii=False, indent=1))
        except (OSError, ValueError): print("[]")
    else: print(__doc__)
