#!/usr/bin/env python3
"""Estado dos agentes entre execuções na nuvem (GitHub Actions não guarda arquivos de uma rodada para outra).

Baixa do SharePoint no início e sobe no fim só o que as rotinas precisam lembrar: registro de demandas, registro e
fila da Central, últimas triagens e caixas do WhatsApp, resumos de pareceres e o histórico de métricas.
Fica numa pasta restrita do site ("Estado dos agentes"), nunca no GitHub. Uso: estado.py baixar | subir
"""
import glob, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import graph  # noqa: E402

AP = os.path.expanduser("~/agentes-partners")
REMOTO = "Estado dos agentes"
ITENS = ["registro/demandas.json", "central-agentes/registro.json", "central-agentes/fila-entrada.json", "central-agentes/aprendizados.md",
         "central-esteira/indice-negocios-ativos.json", "central-esteira/avisos-internos.md", "celulas/whatsapp-config.json", "celulas/geovana/pareceres/resumos.json", "departamentos/resultados/premissas-financeiras.xlsx",
         "departamentos/resultados/mapeamento-hubspot.json"]
GLOBS_TODOS = ["central-esteira/pedidos/E-*.json", "central-esteira/pedidos/E-*.docx",  # histórico completo (cada pedido é o registro do parceiro)
               "central-esteira/historico/*.json"]  # últimas empresas de cada parceiro (só CNPJ e consulta pública)
GLOBS = ["celulas/whatsapp-triagem-*.json", "celulas/*/whatsapp/caixa-*.json", "celulas/*/whatsapp/demandas-*.json",
         "celulas/*/whatsapp/anexos-cache.json", "departamentos/resultados/dados/metricas-*.json", "departamentos/resultados/dados/texto-*.json"]
INDICE = "indice.json"


def baixar():
    tmp = os.path.join(AP, "logs", "estado-indice.json"); os.makedirs(os.path.dirname(tmp), exist_ok=True)
    if not graph.baixar(f"{REMOTO}/{INDICE}", tmp): print("estado vazio (primeira execução)"); return
    n = 0
    with open(tmp, encoding="utf-8") as f:
        indice = json.load(f)
    for rel in indice if isinstance(indice, list) else []:
        if not isinstance(rel, str) or os.path.isabs(rel) or ".." in rel.split("/"):
            continue  # o índice vem do SharePoint: nunca grava fora da pasta do projeto
        if graph.baixar(f"{REMOTO}/{rel}", os.path.join(AP, rel)): n += 1
    print(n, "arquivo(s) de estado baixados")


def _gravar_indice(idx, rels):
    with open(idx, "w", encoding="utf-8") as f:
        json.dump(rels, f)


def subir():
    rels = [r for r in ITENS if os.path.exists(os.path.join(AP, r))]
    for g in GLOBS:  # só os mais recentes de cada série (o suficiente para comparar com a rodada anterior)
        fs = sorted(glob.glob(os.path.join(AP, g)), key=os.path.getmtime)[-6:]
        rels += [os.path.relpath(f, AP) for f in fs]
    for g in GLOBS_TODOS:
        rels += [os.path.relpath(f, AP) for f in sorted(glob.glob(os.path.join(AP, g)))]
    n = sum(graph.subir(os.path.join(AP, r), f"{REMOTO}/{r}") for r in rels)
    idx = os.path.join(AP, "logs", "estado-indice.json"); _gravar_indice(idx, rels); graph.subir(idx, f"{REMOTO}/{INDICE}")
    print(n, "arquivo(s) de estado enviados")


if __name__ == "__main__":
    {"baixar": baixar, "subir": subir}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
