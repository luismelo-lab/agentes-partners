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
# Cópia de reserva do marca.json (gerada dele em 13/10/2026): se o arquivo faltar, os e-mails e alertas não param.
# Ao mudar o marca.json, regenere esta linha (python3 lib/marca.py --reserva).
_RESERVA = {"fontes": {"sans": "IBM Plex Sans", "mono": "IBM Plex Mono", "google_fonts": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap", "pilha_sans": "'IBM Plex Sans', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Arial, sans-serif", "pilha_mono": "'IBM Plex Mono', ui-monospace, 'SF Mono', Menlo, monospace", "pilha_email": "'IBM Plex Sans', Calibri, Arial, Helvetica, sans-serif"}, "claro": {"_uso": "Modo C · Light-only: materiais para cliente e parceiro, PDFs, documentos Word, peças de WhatsApp", "fundo": "#F6F7F9", "fundo_2": "#F1F2F5", "cartao": "#FFFFFF", "borda": "#E6E8EC", "borda_2": "#DEE0E5", "borda_3": "#C9CCD3", "texto": "#0F1115", "texto_2": "#4A4F58", "texto_3": "#838892", "ouro_texto": "#B58A1F", "ouro": "#F3CD60", "ouro_suave": "#FBF1D7", "sucesso": "#1E8E3E", "alerta": "#B5790F", "erro": "#C5221F", "info": "#1A56DB"}, "escuro": {"_uso": "Modo A · Dark-first: painéis, dashboards, capas e faixas de destaque", "fundo": "#000000", "fundo_2": "#111111", "cartao": "#171717", "elevado": "#1E1E1E", "borda": "#2A2A2A", "texto": "#F5F5F5", "texto_2": "#A1A1A1", "texto_3": "#6B6B6B", "ouro": "#F3CD60", "ouro_suave": "#E8BC4C", "sucesso": "#44C653", "alerta": "#E8B34A", "erro": "#D64545", "info": "#6E92E8"}, "logos": {"fundo_claro": "logo-save-fundo-claro.png", "fundo_escuro": "logo-save-fundo-escuro.png", "simbolo_ouro": "simbolo-save-ouro.png", "simbolo": "simbolo-save-original.png", "proporcao_logo": 0.1756, "simbolo_contorno_ouro": "simbolo-save-contorno-ouro.png", "simbolo_branco": "simbolo-save-branco.png", "proporcao_simbolo": 1.1461}}
try:
    M = json.loads((PASTA / "marca.json").read_text(encoding="utf-8"))
except (OSError, ValueError) as _e:
    import sys as _s; print(f"marca.py: marca.json indisponível ({_e}); usando a cópia de reserva", file=_s.stderr)
    M = _RESERVA
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
    import sys
    if sys.argv[1:] == ["--reserva"]:  # reescreve a cópia de reserva a partir do marca.json atual
        r = json.dumps({k: M[k] for k in ("fontes", "claro", "escuro", "logos")}, ensure_ascii=False)
        f = Path(__file__); t = f.read_text(encoding="utf-8").splitlines(keepends=True)
        f.write_text("".join("_RESERVA = " + r + "\n" if x.startswith("_RESERVA = ") else x for x in t), encoding="utf-8"); print("reserva atualizada")
    else:
        print(json.dumps({"claro": C, "escuro": E, "fontes": F}, ensure_ascii=False, indent=1))
