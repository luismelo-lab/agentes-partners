"""Sócios (QSA) e telefones cadastrados na Receita, só para os prospects da D&S (nunca clientes). Dado público do CNPJ.
Aprovado pelo Luis em 20/10/2026. Minimização (LGPD): do sócio guarda nome, qualificação e data de entrada (sem CPF nem faixa etária);
da empresa, telefones e e-mail do cadastro. Arquivo local com permissão 600, fora do repositório e do OneDrive."""
import json, os, pickle, sys
sys.path.insert(0, os.path.expanduser("~/.claude/skills/depto-intel-comercial/scripts"))
import receita_cnpj as R
S = os.environ.get("PROSPECCAO_DS", os.path.expanduser("~/agentes-partners/departamentos/intel-comercial/prospeccao-ds")); OUT = os.path.expanduser("~/agentes-partners/dados-publicos/receita/prospects-contatos.json")
B = pickle.load(open(S + "/base.pkl", "rb"))
alvo = {p["cnpj"] for p in B["pros"]}; basicos = {c[:8] for c in alvo}
mes = "2026-09"; tmp = os.path.join(R.BASE, "tmp"); os.makedirs(tmp, exist_ok=True)
def baixa(nome):
    z = os.path.join(tmp, nome); print("  baixando", nome, flush=True); R.baixar(mes, nome, z); return z
z = baixa("Qualificacoes.zip"); QUAL = {r[0]: r[1] for r in R.linhas(z) if len(r) >= 2}; os.remove(z)
out = {c: {"socios": [], "telefones": [], "email": None} for c in alvo}; soc = {}
for i in range(10):
    z = baixa(f"Socios{i}.zip"); n = 0
    for r in R.linhas(z):
        if len(r) < 6 or r[0] not in basicos: continue
        soc.setdefault(r[0], []).append({"nome": r[2].strip().title(), "qualificacao": QUAL.get(r[4], r[4]), "tipo": {"1": "PJ", "2": "PF", "3": "Estrangeiro"}.get(r[1], r[1]), "entrada": r[5]}); n += 1
    os.remove(z); print("   ", n, "sócios", flush=True)
for c in alvo: out[c]["socios"] = soc.get(c[:8], [])
for i in range(10):
    z = baixa(f"Estabelecimentos{i}.zip"); n = 0
    for r in R.linhas(z):
        if len(r) < 28: continue
        c = r[0] + r[1] + r[2]
        if c not in out: continue
        t = [f"({r[21]}) {r[22]}" if r[22] else None, f"({r[23]}) {r[24]}" if r[24] else None]
        out[c]["telefones"] = [x for x in t if x]; out[c]["email"] = (r[27] or "").strip().lower() or None; n += 1
    os.remove(z); print("   ", n, "telefones", flush=True)
    json.dump(out, open(OUT + ".tmp", "w"), ensure_ascii=False); os.replace(OUT + ".tmp", OUT); os.chmod(OUT, 0o600)
print("fim", sum(1 for v in out.values() if v["telefones"]), "com telefone ·", sum(1 for v in out.values() if v["socios"]), "com sócio", flush=True)
