#!/usr/bin/env python3
"""Degrau 1 da decisão D28 (02/10/2026): medir o acerto das respostas sugeridas ao parceiro antes de liberar envio automático.

Para cada sugestão de resposta das rodadas COM IA (whatsapp-triagem-*.json), procura na caixa do WhatsApp
(Eazybe → HubSpot) a primeira resposta que a dona do número mandou depois, e compara as duas:
  aproveitada   a resposta real traz a mesma informação (palavras-chave e números em comum)
  parcial       parte da informação coincide
  diferente     a pessoa respondeu outra coisa
  sem_resposta  48 h sem resposta do time na conversa
Tipos "objetivos" (candidatos ao envio automático do degrau 2): etapa/status do negócio, assinatura de contrato,
fase da execução, parecer/diagnóstico pronto. O resto fica sempre com uma pessoa.
Critério para o degrau 2 (proposto ao Luis): por tipo objetivo, 20+ casos em 2 semanas e 95%+ aproveitada.
É uma medida aproximada (comparação de texto); o relatório semanal traz exemplos para o Luis conferir.

Resposta real = mensagens de conteúdo do time nas 36 h seguintes (cumprimentos e mensagens curtas ficam de fora).
Uso: medicao_respostas.py atualizar | relatorio
"""
import glob, json, os, re, sys, unicodedata
from datetime import datetime, timedelta

AP = os.path.expanduser("~/agentes-partners"); REG = os.path.join(AP, "registro", "medicao-respostas.json")
sys.path.insert(0, os.path.expanduser("~/.claude/skills/celula-daniela/scripts"))
OBJETIVOS = {
    "etapa_negocio": r"\b(status|etapa|andamento|como (est[aá]|anda)|em que p[eé]|fase do neg)",
    "assinatura": r"\bassin(ou|aram|atura|ado)|contrato (enviado|assinado)",
    "execucao": r"\bexecu[cç][aã]o|compensa[cç][aã]o|per\s*/?\s*dcomp|protocol",
    "parecer": r"\bparecer|diagn[oó]stico (pronto|saiu|ficou)|resultado da an[aá]lise",
}
INICIO = datetime(2026, 10, 2, 12, 0)  # D28 começa a contar com a rotina já instruída a responder com o dado (02/10)
PARE = set("a o e de da do das dos em no na nos nas um uma para por com que se ja já foi ser ta tá esta está oi ola olá bom dia boa tarde obrigado obrigada abraço".split())


def norm(t):
    t = unicodedata.normalize("NFKD", str(t or "").lower()).encode("ascii", "ignore").decode()
    return re.findall(r"[a-z0-9]{3,}", t)


def tipo(texto):
    for k, p in OBJETIVOS.items():
        if re.search(p, str(texto or ""), re.I): return k
    return "outro"


def comparar(sug, real):
    a = {w for w in norm(sug) if w not in PARE}; b = {w for w in norm(real) if w not in PARE}
    if not a or not b: return "diferente", 0.0
    num_a = {w for w in a if w.isdigit()}; num_b = {w for w in b if w.isdigit()}
    j = len(a & b) / len(a | b); cob = len(a & b) / len(a)
    if num_a and not (num_a & num_b): cob *= 0.5  # números (datas, valores) que não batem pesam contra
    nota = max(j, cob)
    return ("aproveitada" if nota >= 0.45 else "parcial" if nota >= 0.2 else "diferente"), round(nota, 2)


def quando(s, ano):
    try: return datetime.strptime(f"{s} {ano}", "%d/%m %H:%M %Y")
    except Exception: return None


def atualizar():
    import whatsapp_hubspot as W
    cfg = json.load(open(W.CFG)) if os.path.exists(W.CFG) else {}
    M = json.load(open(REG)) if os.path.exists(REG) else {}
    limite = datetime.now() - timedelta(days=30)
    for f in sorted(glob.glob(os.path.join(AP, "celulas", "whatsapp-triagem-*.json"))):
        t0 = datetime.fromtimestamp(os.path.getmtime(f))
        if t0 < max(limite, INICIO): continue
        T = json.load(open(f))
        if T.get("modo") == "sem IA": continue
        for p, P in T.get("pessoas", {}).items():
            for i in P.get("itens", []):
                if i.get("status") != "responder" or not i.get("rascunho"): continue
                k = f"{p}|{i['chat']}|{t0:%Y-%m-%d %H:%M}"
                M.setdefault(k, {"pessoa": p, "chat": i["chat"], "sugerida_em": t0.isoformat(timespec="minutes"), "tipo": tipo(i.get("o_que_pede")),
                                 "pergunta": i.get("o_que_pede"), "sugestao": i["rascunho"], "resultado": None})
    caixas = {}
    for k, m in M.items():
        if m.get("resultado") not in (None, "sem_resposta", "diferente", "parcial"): continue  # recalcula até fechar a janela
        p = m["pessoa"]
        if p not in caixas:
            fs = sorted(glob.glob(os.path.join(AP, "celulas", p, "whatsapp", "caixa-*.json")))
            caixas[p] = {c["chat"]: c for c in json.load(open(fs[-1]))} if fs else {}
        t0 = datetime.fromisoformat(m["sugerida_em"]); c = caixas[p].get(m["chat"])
        # respostas de conteúdo do time nas 36 h seguintes (cumprimento e mensagem curta não contam)
        cands = []
        for x in (c or {}).get("conversa", []):
            q = quando(x.get("quando"), t0.year)
            if q and t0 - timedelta(minutes=5) <= q <= t0 + timedelta(hours=36) and W.e_do_time(x.get("de") or "", cfg) and x.get("texto"):
                if len([w for w in norm(x["texto"]) if w not in PARE]) >= 4: cands.append(x)
        resp = None
        if cands:
            juntas = {"texto": " ".join(x["texto"] for x in cands[:3]), "quando": cands[0]["quando"]}
            resp = max(cands + [juntas], key=lambda x: comparar(m["sugestao"], x["texto"])[1])
        if resp:
            m["resultado"], m["nota"] = comparar(m["sugestao"], resp["texto"])
            m["resposta_real"] = resp["texto"][:600]; m["respondida_em"] = resp["quando"]
        else:
            for k2 in ("resposta_real", "respondida_em", "nota"): m.pop(k2, None)
            m["resultado"] = "sem_resposta" if datetime.now() - t0 > timedelta(hours=48) else None
    tmp = REG + ".tmp"; json.dump(M, open(tmp, "w"), ensure_ascii=False, indent=1); os.replace(tmp, REG)
    print(f"medição: {len(M)} sugestões acompanhadas")


def relatorio(dias=14):
    M = json.load(open(REG)) if os.path.exists(REG) else {}
    ini = datetime.now() - timedelta(days=dias); por = {}
    for m in M.values():
        if datetime.fromisoformat(m["sugerida_em"]) < ini or m.get("resultado") in (None, "sem_resposta"): continue
        r = por.setdefault(m["tipo"], {"n": 0, "aproveitada": 0, "parcial": 0, "diferente": 0})
        r["n"] += 1; r[m["resultado"]] += 1
    linhas = []
    for t, r in sorted(por.items(), key=lambda x: -x[1]["n"]):
        pct = 100 * r["aproveitada"] / r["n"]
        pronto = t != "outro" and r["n"] >= 20 and pct >= 95
        linhas.append({"tipo": t, "casos": r["n"], "aproveitada_pct": round(pct), "parcial": r["parcial"], "diferente": r["diferente"],
                       "pronto_para_degrau_2": pronto})
    return linhas


if __name__ == "__main__":
    c = (sys.argv[1:] or ["relatorio"])[0]
    if c == "atualizar": atualizar()
    else: print(json.dumps(relatorio(), ensure_ascii=False, indent=1))
