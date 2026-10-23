#!/usr/bin/env python3
"""Barreira de LGPD do repositório: falha se algum arquivo a ser versionado tiver dado sensível.
Procura CNPJ válido (numérico ou alfanumérico), CPF válido, token do HubSpot, chave privada, telefone e e-mail fora da Save.
Uso: python3 infra/checar-dados.py [arquivos...]  (sem argumentos: tudo o que o git versionaria)
Exceções conhecidas: infra/checar-dados-permitidos.txt (um valor por linha).
"""
import os, re, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repositório do próprio script (o hook chama o da raiz)
sys.path.insert(0, os.path.join(R, "lib"))
# raiz do repositório onde o commit acontece (worktree): o hook passa caminhos relativos a ela. Antes os caminhos eram
# lidos em ~/agentes-partners, então num worktree o arquivo novo não era achado e passava sem checagem.
_top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
RAIZ = _top.stdout.strip() if _top.returncode == 0 and _top.stdout.strip() else R
from partners_dados import cnpj_valido  # noqa: E402
from cnpj import CNPJ_TEXTO_ALFA, normalizar_cnpj  # noqa: E402

def cpf_ok(c):
    if len(c) != 11 or len(set(c)) == 1: return False
    for n in (9, 10):
        s = sum(int(c[i]) * (n + 1 - i) for i in range(n)) % 11
        if int(c[n]) != (0 if s < 2 else 11 - s): return False
    return True

PADROES = [("token HubSpot", re.compile(r"pat-(na|eu)\d-[0-9a-f-]{20,}")), ("chave privada", re.compile(r"BEGIN (RSA |EC )?PRIVATE KEY")),
           ("segredo", re.compile(r"(client_secret|api[_-]?key|password)\s*[=:]\s*['\"][^'\"\s]{12,}", re.I)),
           ("telefone", re.compile(r"(?<![\d.])(\+?55\s?)?\(?\d{2}\)?\s?9\d{4}-?\d{4}(?!\d)")),
           ("e-mail externo", re.compile(r"[\w.+-]+@(?!savecompany\.com\.br)[\w-]+\.[\w.]+"))]
perm = set()
pf = os.path.join(R, "infra/checar-dados-permitidos.txt")
if os.path.exists(pf): perm = {l.strip() for l in open(pf) if l.strip() and not l.startswith("#")}
arqs = sys.argv[1:] or subprocess.run(["git", "-C", RAIZ, "ls-files", "--cached", "--others", "--exclude-standard"], capture_output=True, text=True).stdout.splitlines()  # nomes com espaço (· Gestão) não se partem
achados = []
for a in arqs:
    p = a if os.path.isabs(a) else os.path.join(RAIZ, a)
    if not os.path.isfile(p) or os.path.getsize(p) > 2_000_000: continue
    try: t = open(p, encoding="utf-8").read()
    except UnicodeDecodeError: continue
    for n, l in enumerate(t.splitlines(), 1):
        for m in re.findall(r"(?<!\d)\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}(?!\d)", l):
            d = re.sub(r"\D", "", m)
            if cnpj_valido(d) and d not in perm: achados.append((a, n, "CNPJ", d[:4] + "…"))
        for m in CNPJ_TEXTO_ALFA.findall(l):  # CNPJ alfanumérico (IN RFB 2.229/2024): só com letra maiúscula e DV válido
            d = normalizar_cnpj(m)
            if re.search(r"[A-Z]", m) and cnpj_valido(d) and d not in perm: achados.append((a, n, "CNPJ", d[:4] + "…"))
        for m in re.findall(r"(?<!\d)\d{3}\.\d{3}\.\d{3}-\d{2}(?!\d)", l):
            d = re.sub(r"\D", "", m)
            if cpf_ok(d) and d not in perm: achados.append((a, n, "CPF", d[:3] + "…"))
        for nome, rx in PADROES:
            for m in rx.finditer(l):
                v = m.group(0)
                if v not in perm and not (nome == "e-mail externo" and v.split("@")[1] in ("example.com", "exemplo.com", "users.noreply.github.com")):
                    achados.append((a, n, nome, v[:6] + "…"))
for a, n, k, v in achados[:200]: print(f"{a}:{n}: {k} ({v})")
print(f"{len(achados)} achado(s) em {len(arqs)} arquivo(s)")
sys.exit(1 if achados else 0)
