#!/usr/bin/env python3
"""Padrão visual Save (Design System Save v0.5) num só lugar: todo gerador de peça, PDF, e-mail e documento usa este arquivo.

Por quê: em 07/10/2026 o Luis definiu o Design System do Marketing como layout padrão de tudo o que desenvolvermos.
Os valores ficam em departamentos/marketing-marca/padrao/marca.json (o gerador de Word em Node lê o mesmo arquivo).

Uso:
  import marca
  marca.C["texto"], marca.E["fundo"]       cores do modo claro (cliente) e escuro (painéis)
  marca.SANS, marca.MONO                   pilhas de fonte para CSS
  marca.logo_uri("fundo_claro")            logo em data URI para HTML/Playwright
  marca.css_base()                         <link> das fontes + variáveis CSS do modo claro e escuro
"""
import base64, json
from pathlib import Path

PASTA = Path.home() / "agentes-partners/departamentos/marketing-marca/padrao"
M = json.loads((PASTA / "marca.json").read_text(encoding="utf-8"))
C, E, F = M["claro"], M["escuro"], M["fontes"]
SANS, MONO, SANS_EMAIL = F["pilha_sans"], F["pilha_mono"], F["pilha_email"]


def logo(nome="fundo_claro"):
    return PASTA / M["logos"][nome]


def logo_uri(nome="fundo_claro"):
    return "data:image/png;base64," + base64.b64encode(logo(nome).read_bytes()).decode()


def css_base():
    """Fontes do Google e as variáveis do Design System (claro em :root, escuro em .escuro)."""
    v = lambda d, p: "".join(f"--{p}{k.replace('_', '-')}:{x};" for k, x in d.items() if not k.startswith("_"))
    return (f'<link rel="preconnect" href="https://fonts.googleapis.com"><link href="{F["google_fonts"]}" rel="stylesheet">'
            f"<style>:root{{{v(C, '')}--sans:{SANS};--mono:{MONO};}} .escuro{{{v(E, '')}}}</style>")


if __name__ == "__main__":
    print(json.dumps({"claro": C, "escuro": E, "fontes": F}, ensure_ascii=False, indent=1))
