#!/usr/bin/env python3
"""Trava de qualidade: nenhuma entrega dos agentes sai fora do padrão (infra/padrao-entrega.md e protocolo-gerente.md).

  python3 infra/validar_saidas.py triagem <arquivo.json>      itens "responder" do WhatsApp
  python3 infra/validar_saidas.py analises <arquivo.json>     análises das áreas para o plano do dia
  python3 infra/validar_saidas.py resposta <resposta.json>    resposta da Central a um pedido

Sai com código 1 e lista o que corrigir quando algo falha. As rotinas rodam isto ANTES de enviar e, se falhar, devolvem os itens
ao gerente da área para corrigir (até 2 rodadas). Cada validação vira uma linha em registro/execucoes.jsonl (taxa de conformidade).
"""
import json, os, re, sys, time

AP = os.path.expanduser("~/agentes-partners")
sys.path.insert(0, os.path.join(AP, "lib"))
GEN = re.compile(r"passando para alinhar|ler a conversa e responder|última mensagem:|confira no hubspot|conferir no hubspot|<EMPRESA>", re.I)
PROMESSA = re.compile(r"garantid|sem risco|com certeza vai|100% de êxito|êxito garantido|valor garantido", re.I)


def vazio(v): return not str(v or "").strip()


def checar_item(x, campos, nome):
    erros = []
    for c in campos:
        if vazio(x.get(c)): erros.append(f"sem '{c}'")
    rv = x.get("revisao") or {}
    if not rv.get("gerente"): erros.append("sem revisão do gerente")
    elif rv.get("aprovado") is False and vazio(x.get("falta")): erros.append("gerente não aprovou e não disse o que falta")
    txt = " ".join(str(x.get(c) or "") for c in ("o_que_pede", "entrega", "rascunho", "fazer", "precisa"))
    if GEN.search(txt): erros.append("texto genérico ou mensagem crua: " + GEN.search(txt).group(0))
    if PROMESSA.search(str(x.get("rascunho") or "")): erros.append("rascunho promete resultado: " + PROMESSA.search(x["rascunho"]).group(0))
    try:
        import protecao
        if x.get("rascunho") and not protecao.auditar(x["rascunho"]): erros.append("rascunho reprovado pela Qualidade")
    except Exception: pass
    return [f"{nome}: {e}" for e in erros]


def triagem(f):
    T = json.load(open(f)); out = []; n = 0
    if str(T.get("leitura_geral", "")).startswith("Rodada automática"): return 0, []  # aviso sem IA (11h/17h): não é entrega
    for p, P in (T.get("pessoas") or {}).items():
        for i in P.get("itens", []):
            if i.get("status") != "responder": continue
            n += 1
            out += checar_item(i, ("o_que_pede", "entrega", "precisa", "falta"), f"{p} · {i.get('chat')}")
            enc = i.get("encaminhar") or {}
            if enc and not (enc.get("especialista") or {}).get("pedidos") and not (enc.get("especialista") or {}).get("nao_abrir"):
                out.append(f"{p} · {i.get('chat')}: chamado sem o texto do especialista (infra/chamado-ideal.md)")
            # histórico antes do GLPI (Luis, 26/10/2026; infra/historico-antes-do-glpi.md)
            hist, rh = i.get("historico") or {}, i.get("resposta_historico") or {}
            if enc and not (hist.get("consultado") and hist.get("buscas")):
                out.append(f"{p} · {i.get('chat')}: chamado sem consulta ao histórico (lib/historico.py avaliar; registre 'historico.buscas')")
            if rh:
                if enc: out.append(f"{p} · {i.get('chat')}: tem resposta_historico e encaminhar ao mesmo tempo")
                if vazio(rh.get("resposta")) or not rh.get("fontes") or any(vazio(f.get("data")) for f in rh.get("fontes", [])):
                    out.append(f"{p} · {i.get('chat')}: resposta_historico sem resposta ou sem fonte com data")
    return n, out


def analises(f):
    A = json.load(open(f)); out = []
    for x in A: out += checar_item(x, ("fazer", "precisa", "falta"), f"{x.get('area')} · {x.get('chave')}")
    return len(A), out


def resposta(f):
    J = json.load(open(f)); out = []
    for c in ("resumo", "tambem", "falta"):
        if vazio(J.get(c)): out.append(f"{J.get('pedido')}: sem '{c}'")
    if not J.get("secoes"): out.append(f"{J.get('pedido')}: sem seções com o que foi pedido")
    if not (J.get("revisao") or {}).get("gerente"): out.append(f"{J.get('pedido')}: sem revisão do gerente")
    if any(re.search(r"confira|conferir", str(c), re.I) and not re.search(r"sem acesso|não temos|depende de", str(c), re.I) for c in J.get("conferir", [])):
        out.append(f"{J.get('pedido')}: 'conferir' com item que os agentes deveriam ter conferido")
    return 1, out


if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(__doc__)
    tipo, f = sys.argv[1], sys.argv[2]
    n, erros = {"triagem": triagem, "analises": analises, "resposta": resposta}[tipo](f)
    falhos = len({e.split(":")[0] for e in erros})
    conf = 100 if not n else round(100 * (n - falhos) / n)
    with open(os.path.join(AP, "registro", "execucoes.jsonl"), "a") as log:
        log.write(json.dumps({"quando": time.strftime("%Y-%m-%d %H:%M"), "tipo": tipo, "arquivo": os.path.basename(f), "itens": n, "com_falha": falhos, "conformidade": conf}, ensure_ascii=False) + "\n")
    print(f"{tipo}: {n} item(ns) · {falhos} com falha · conformidade {conf}%")
    for e in erros: print("  -", e)
    sys.exit(1 if erros else 0)
