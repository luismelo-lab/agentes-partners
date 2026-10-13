#!/usr/bin/env python3
"""Proteções únicas de tudo o que os agentes escrevem ou enviam (validação Qualidade + Jurídico, 02/10/2026).

  interno(enderecos)  trava de domínio: só @savecompany.com.br. Todo ponto de envio chama antes de mandar.
  limpo(texto)        mascara telefone, CPF, CNPJ sem pontuação, RG/CNH/agência/conta/PIX/senha rotulados;
                      preserva valores em R$, datas, número de processo e de PER/DCOMP e links.
  auditar(texto)      auditor de promessas da Qualidade: True só se não houver achado (erro conta como reprovado).
"""
import json, os, re, subprocess, sys, tempfile

AP = os.path.expanduser("~/agentes-partners"); SK = os.path.expanduser("~/.claude/skills")
DOMINIO = re.compile(r"^[^@\s]+@savecompany\.com\.br$", re.I)

TEL = re.compile(r"@?\+?\(?\d[\d .()-]{7,}\d(?![\d/.]*\d)")
PROTEGE = re.compile(r"R\$\s*[\d.,]+|(?i:(?<=negócio )|(?<=negocio )|(?<=deal )|(?<=negócio #)|(?<=deal #))\d{8,12}|https?://\S+|\d{5}\.\d{6}/\d{4}-\d{2}|\d{5}\.\d{5}\.\d{6}\.\d\.\d\.\d{2}-\d{4}|\d{4}-\d{2}-\d{2}")  # valor em R$, ID de negócio, link, processo RFB, PER/DCOMP, data ISO
ROTULO = re.compile(r"(?i)\b(rg|identidade|cnh|ag[eê]ncia|conta(?: corrente)?|c/c|chave pix|pix|senha)\b\s*[:nº°.-]*\s*(?=\S*\d)\S+")


def interno(*listas):
    """Lista de endereços fora do domínio (vazia = pode enviar)."""
    return [a for l in listas for a in (l or []) if not DOMINIO.match(str(a).strip())]


def limpo(t):
    t = str(t or "")
    t = ROTULO.sub(lambda m: m.group(1) + " [ocultado]", t)
    guarda = []
    def _g(m):
        guarda.append(m.group()); return f"\x00{len(guarda) - 1}\x00"
    t = PROTEGE.sub(_g, t)
    t = TEL.sub(lambda m: "[número]" if sum(c.isdigit() for c in m.group()) >= 10 else m.group(), t)
    for i, v in enumerate(guarda): t = t.replace(f"\x00{i}\x00", v)
    return t


def auditar(texto):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, dir=tempfile.gettempdir()) as f: f.write(texto)
    try:
        r = subprocess.run([sys.executable, os.path.join(SK, "depto-qualidade/scripts/auditar_texto.py"), f.name, "--json"], capture_output=True, text=True, timeout=60)
        J = json.loads(r.stdout or "{}")
        vals = list(J.values()) if isinstance(J, dict) else J
        if not vals or any("erro" in x for x in vals): return False
        return sum(len(x.get("achados", [])) for x in vals) == 0
    except Exception:
        return False
    finally:
        os.unlink(f.name)


if __name__ == "__main__":  # autoteste com números gerados (nada real no código; o scanner do repositório bloqueia exemplos)
    n = lambda k, d="9": d * k
    for t in [f"fone +{n(2,'5')} ({n(2,'1')}) {n(5)}-{n(4)}", f"CPF {n(11,'1')}", f"CNPJ {n(14,'2')}", f"RG: {n(2)}.{n(3)}.{n(3)}-9 conta {n(5)}-0",
              "R$ 12.345.678 em 01/10/2026 e 2026-10-01", "https://app.hubspot.com/contacts/1/deal/" + n(11, "6")]:
        print(limpo(t))
    print(interno(["a@savecompany.com.br"], ["fulano@" + "exemplo.com"]))
