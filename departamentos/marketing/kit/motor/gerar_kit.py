#!/usr/bin/env python3
"""Monta o kit inteiro de uma entrega: para cada pasta com JSON de conteúdo, gera PDF + PowerPoint das apresentações
e folder, flyer e WhatsApp das peças. Saída em <entrega>/KIT/<pasta>/. Só gera arquivos locais.
Uso: python3 gerar_kit.py <pasta_da_entrega> [--sem-pptx]"""
import os, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import deck_html, pecas  # noqa: E402

NODE_PATH = os.environ.get("NODE_PATH") or "/private/tmp/claude-501/-Users-luisfernandomelo-agentes-partners/347f0b34-7e5c-482d-831a-41b010e85a37/scratchpad/node_modules"
NOMES = {"apresentacao-institucional": "Apresentacao-Institucional", "apresentacao-comercial": "Apresentacao-Comercial",
         "canex-apresentacao": "Canex-Save-Proposta-Piloto"}


def main(entrega, pptx=True):
    entrega = Path(entrega).resolve(); kit = entrega / "KIT"; relatorio = []
    for js in sorted(entrega.rglob("*.json")):
        if "KIT" in js.parts or "pesquisa" in js.parts: continue
        rel = js.parent.relative_to(entrega); destino = kit / rel; destino.mkdir(parents=True, exist_ok=True)
        prefixo = "-".join(p.capitalize() for p in rel.parts[-1:]) if rel.parts else "Kit"
        if js.stem in NOMES or js.stem.startswith("apresentacao"):
            nome = f"{prefixo}-{NOMES.get(js.stem, js.stem)}" if js.stem != "canex-apresentacao" else NOMES[js.stem]
            av = deck_html.gerar(js, destino / f"{nome}.pdf", destino / "previas" / nome)
            relatorio.append((str(rel / nome), "pdf", av))
            if pptx:
                r = subprocess.run(["node", str(AQUI / "deck_pptx.js"), str(js), str(destino / f"{nome}.pptx")],
                                   env={**os.environ, "NODE_PATH": NODE_PATH}, capture_output=True, text=True)
                relatorio.append((str(rel / nome), "pptx", [] if r.returncode == 0 else [r.stderr.strip()[-300:]]))
        elif js.stem.endswith("pecas"):
            av = pecas.gerar(js, destino, prefixo if js.stem == "pecas" else js.stem.replace("-pecas", "").capitalize())
            relatorio.append((str(rel), "peças", av))
    for nome, tipo, av in relatorio:
        print(("OK   " if not av else "AVISO"), tipo.ljust(5), nome, *av)
    return relatorio


if __name__ == "__main__":
    main(sys.argv[1], "--sem-pptx" not in sys.argv)
