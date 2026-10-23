"""Pedido de análise e esteira para o parceiro (Originação do fluxo único, infra/fluxo-unico.md).

O site só grava o pedido e mostra o andamento. Quem analisa são os agentes (rotina `esteira-parceiro`, no GitHub
Actions, ver rotinas/esteira-parceiro.md): quatro checagens, esteira do cliente (depto-solucoes), rascunho em três
blocos (infra/padrao-entrega.md) e auditoria de promessas (depto-qualidade). O resultado só aparece ao parceiro
depois de `publicar`, que passa pela auditoria:

  CENTRAL_APROVACAO=obrigatoria (padrão)  → um aprovador libera (`aprovar`); é o modo do teste.
  CENTRAL_APROVACAO=autonoma              → entrega sozinha SE a auditoria não achar alerta ALTO/MÉDIO;
                                            com alerta, cai na revisão humana. Nunca entrega com alerta.

Estados: recebida → (agentes) → aguardando_aprovacao | revisao_humana | entregue.
A pasta de estado (CENTRAL_ESTEIRA) viaja pelo SharePoint com lib/estado.py; nunca vai para o GitHub.

Uso:  esteira.py fila | status --id E-0001 | publicar --id E-0001 --arquivo resultado.json | aprovar --id E-0001 --quem "Nome"
"""
import argparse, fcntl, json, os, subprocess, sys, tempfile, time
from pathlib import Path

sys.path.insert(0, os.path.expanduser("~/agentes-partners/lib"))
from cnpj import cnpj_valido, normalizar_cnpj  # noqa: E402
from . import negocio_ativo as NA  # noqa: E402

DIR = NA.DIR
RAIZ_REPO = Path(__file__).resolve().parents[3]
BLOCOS = ("fazer", "precisa", "falta")
ABERTOS = ("recebida", "aguardando_aprovacao", "revisao_humana")
ROTULO = {"recebida": "Em análise pelos agentes", "aguardando_aprovacao": "Em revisão final", "revisao_humana": "Em revisão final",
          "entregue": "Pronta"}


class Recusa(Exception):
    """Pedido que não pode seguir; a mensagem é segura para mostrar ao parceiro."""


def _arq(id_):
    return os.path.join(DIR, "pedidos", id_ + ".json")


def _trava():
    os.makedirs(DIR, exist_ok=True)
    f = open(os.path.join(DIR, ".trava"), "w")
    fcntl.flock(f, fcntl.LOCK_EX)
    return f


def _ler(id_):
    try:
        with open(_arq(id_)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _gravar(p):
    os.makedirs(os.path.join(DIR, "pedidos"), exist_ok=True)
    tmp = _arq(p["id"]) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
    os.replace(tmp, _arq(p["id"]))


def _todos():
    pasta = os.path.join(DIR, "pedidos")
    return [p for p in (_ler(n[:-5]) for n in sorted(os.listdir(pasta)) if n.endswith(".json")) if p] if os.path.isdir(pasta) else []


def solicitar(cnpj, parceiro, consulta=None):
    c = normalizar_cnpj(cnpj)
    if not cnpj_valido(c):
        raise Recusa("CNPJ inválido.")
    ativo = NA.tem_negocio_ativo(c)
    if ativo is None:
        raise Recusa("Não foi possível conferir a base agora. Tente de novo mais tarde.")
    if ativo:
        raise Recusa("Empresa com negócio ativo na base Save Company.")
    with _trava():
        for p in _todos():  # um pedido aberto por parceiro e empresa
            if p["cnpj"] == c and p["parceiro"] == parceiro and p["status"] in ABERTOS:
                return p
        n = 1 + max([int(p["id"][2:]) for p in _todos()] or [0])
        p = {"id": "E-%04d" % n, "cnpj": c, "parceiro": parceiro, "criado": time.strftime("%Y-%m-%dT%H:%M:%S"), "status": "recebida",
             "consulta": {k: (consulta or {}).get(k) for k in ("faixa", "titulo", "ano_base", "fonte")}, "resultado": None,
             "historico": [{"quando": time.strftime("%Y-%m-%dT%H:%M:%S"), "evento": "recebida"}]}
        _gravar(p)
        return p


def visao_parceiro(p):
    """O que o parceiro pode ver: andamento e, só depois de entregue, o resultado."""
    v = {"id": p["id"], "status": p["status"], "andamento": ROTULO.get(p["status"], p["status"])}
    if p["status"] == "entregue":
        v["resultado"] = p["resultado"]
    return v


def ler_do_parceiro(id_, parceiro):
    p = _ler(id_)
    return visao_parceiro(p) if p and p["parceiro"] == parceiro else None


def _texto(r):
    partes = [str(r.get(b, "")) for b in BLOCOS] + [str(x.get(k, "")) for x in r.get("esteira", []) for k in ("produto", "nota")]
    return "\n".join(partes)


def auditar(texto):
    """(ok, achados). ok = sem alerta ALTO/MÉDIO no auditor de promessas do depto-qualidade."""
    script = RAIZ_REPO / "skills/depto-qualidade/scripts/auditar_texto.py"
    if not script.exists():
        script = Path(os.path.expanduser("~/.claude/skills/depto-qualidade/scripts/auditar_texto.py"))
    with tempfile.TemporaryDirectory() as d:
        arq = os.path.join(d, "entrega.md")
        with open(arq, "w") as f:
            f.write(texto)
        r = subprocess.run([sys.executable, "-I", str(script), arq, "--json"], capture_output=True, text=True, timeout=60)
    if r.returncode == 2:
        return False, [{"erro": "auditor indisponível"}]  # falha fechada: sem auditoria não entrega
    try:
        achados = [a for res in json.loads(r.stdout).values() for a in (res.get("achados") if isinstance(res, dict) else res or [])]
    except (ValueError, AttributeError):
        achados = []
    return r.returncode == 0, achados


def publicar(id_, resultado):
    faltam = [b for b in BLOCOS if not str(resultado.get(b, "")).strip()]
    if faltam:
        raise Recusa("Faltam blocos: " + ", ".join(faltam))
    ok, achados = auditar(_texto(resultado))
    with _trava():
        p = _ler(id_)
        if not p or p["status"] != "recebida":
            raise Recusa("Pedido inexistente ou já tratado.")
        p["resultado"] = resultado
        p["auditoria"] = {"ok": ok, "alertas": len(achados)}
        if not ok:
            p["status"] = "revisao_humana"
        elif os.environ.get("CENTRAL_APROVACAO", "obrigatoria") == "autonoma":
            p["status"] = "entregue"
        else:
            p["status"] = "aguardando_aprovacao"
        p["historico"].append({"quando": time.strftime("%Y-%m-%dT%H:%M:%S"), "evento": p["status"], "auditoria_ok": ok})
        _gravar(p)
        return p


def aprovar(id_, quem):
    with _trava():
        p = _ler(id_)
        if not p or p["status"] not in ("aguardando_aprovacao", "revisao_humana"):
            raise Recusa("Nada a aprovar neste pedido.")
        p["status"] = "entregue"
        p["historico"].append({"quando": time.strftime("%Y-%m-%dT%H:%M:%S"), "evento": "aprovado", "por": quem})
        _gravar(p)
        return p


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["fila", "status", "publicar", "aprovar"])
    ap.add_argument("--id"); ap.add_argument("--arquivo"); ap.add_argument("--quem")
    a = ap.parse_args()
    if a.cmd == "fila":
        print(json.dumps([{k: p[k] for k in ("id", "cnpj", "parceiro", "criado", "consulta")} for p in _todos() if p["status"] == "recebida"], ensure_ascii=False, indent=1))
    elif a.cmd == "status":
        print(json.dumps([{k: p[k] for k in ("id", "status", "parceiro", "criado")} for p in _todos() if not a.id or p["id"] == a.id], ensure_ascii=False, indent=1))
    elif a.cmd == "publicar":
        with open(a.arquivo) as f:
            p = publicar(a.id, json.load(f))
        print(p["id"], p["status"], p["auditoria"])
    else:
        print(aprovar(a.id, a.quem or "")["status"])


if __name__ == "__main__":
    try:
        main()
    except Recusa as e:
        sys.exit("ERRO: %s" % e)
