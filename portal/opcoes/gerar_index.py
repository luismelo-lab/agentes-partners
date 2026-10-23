#!/usr/bin/env python3
"""Gera portal/index.html (página do Artifact) a partir da prévia portal/opcoes/combinada.html.
Tira o que só serve à prévia local: <!doctype>, <html>, <head>, o viewport (o Artifact põe o seu), o comentário de prévia,
o exemplo-dados.js e </head><body> … </body></html>. Sem window.EX a página lê dados.json, diretorio.json e o db.
Uso: python3 portal/opcoes/gerar_index.py"""
import os, re, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); PORTAL = os.path.dirname(AQUI)
s = open(os.path.join(AQUI, "combinada.html"), encoding="utf-8").read()
s = re.sub(r"\A<!doctype html>\s*<html[^>]*><head><meta charset=\"utf-8\"><meta name=\"viewport\"[^>]*>\s*", "", s)
s = re.sub(r"<!-- PRÉVIA LOCAL\..*?-->\s*", "", s, flags=re.S)
s = s.replace('<script src="exemplo-dados.js"></script>\n', "")
s = s.replace("</head><body>\n", "").replace("</body></html>", "").rstrip() + "\n"
for proibido in (r'src="exemplo-dados', r"<head[\s>]", r"<body[\s>]", r"<html[\s>]", r"<!doctype"):
    if re.search(proibido, s, re.I): sys.exit(f"sobrou '{proibido}' no index.html")
if not s.startswith("<title>"): sys.exit("o index.html deve começar pelo <title>")
open(os.path.join(PORTAL, "index.html"), "w", encoding="utf-8").write(s)
print("portal/index.html gerado:", len(s.encode()), "bytes")
