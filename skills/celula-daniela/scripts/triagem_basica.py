#!/usr/bin/env python3
"""Triagem do WhatsApp SEM IA (zero tokens) para as rodadas intermediárias.

Usa só regras e os dados já levantados pelos scripts (caixa + demandas):
- "responder": conversa com mensagem de parceiro/cliente sem resposta do time há X horas;
- "acompanhar": áudio ou imagem que ninguém leu, ou mensagem nova ainda dentro do prazo;
- entrega automática: cadastro oficial e situação no HubSpot de cada CNPJ citado, status dos links de negócio,
  o que foi lido nos prints e documentos (só o nome) e quantos áudios há para ouvir.
Não interpreta o pedido nem sugere resposta: isso fica para a rodada com IA.

Uso: python3 triagem_basica.py [--aguardando 3] [--rodada "11h"] → celulas/whatsapp-triagem-<data>.json (imprime o caminho)
"""
import argparse, glob, json, os
from datetime import datetime

AP = os.path.expanduser("~/agentes-partners")
PESSOAS = ("daniela", "jenifer", "geovana")
ult = lambda p: (sorted(glob.glob(p)) or [None])[-1]


def brl(v):
    return ("R$ " + f"{v:,.0f}".replace(",", ".")) if isinstance(v, (int, float)) and v else "sem valor"


def entrega(ev):
    ls = []
    for c in ev.get("cnpjs", []):
        r = c.get("receita") or {}
        cad = f"{r.get('razao') or 'fora da base local da Receita'}" + (f", {r.get('situacao')}, CNAE {r.get('cnae')}, {r.get('uf')}" if r else "")
        hs = c.get("hubspot") or []
        neg = "; ".join(f"{h['nome'][:40]} ({h['status']}, {h['etapa']}, {h['parceiro']})" for h in hs[:3]) or "não existe no HubSpot"
        ls.append(f"- **CNPJ {c['cnpj'][:2]}.{c['cnpj'][2:5]}.{c['cnpj'][5:8]}/{c['cnpj'][8:12]}-{c['cnpj'][12:]}:** {cad}. HubSpot: {neg}.")
        if len({h['parceiro'] for h in hs if h.get('parceiro')}) > 1: ls.append("- ⚠️ Mais de um parceiro para esta empresa no HubSpot: conferir conflito de canal.")
    for n in ev.get("links_negocio", []):
        if n.get("nao_encontrado_no_download"): ls.append(f"- Link de negócio {n['id']}: não está no último download do HubSpot."); continue
        ls.append(f"- **Negócio {n['nome'][:50]}:** {n['status']}, etapa {n['etapa']}, {brl(n.get('valor'))}" + (f". Parecer: {n['parecer_resumo'][:160]}" if n.get("parecer_resumo") else "") + ".")
    lidos = [a["arquivo"][:40] for a in ev.get("anexos", []) if a.get("texto")]
    if lidos: ls.append("- Lidos: " + ", ".join(lidos) + ".")
    pessoais = sum(1 for a in ev.get("anexos", []) if a["tipo"] == "documento pessoal")
    if pessoais: ls.append(f"- {pessoais} documento(s) pessoal(is) recebido(s): não lidos.")
    if ev.get("audios"): ls.append(f"- 🎤 {ev['audios']} áudio(s) para ouvir.")
    return "\n".join(ls)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--aguardando", type=float, default=3); ap.add_argument("--rodada")
    a = ap.parse_args()
    agora = datetime.now(); rodada = a.rodada or f"{agora:%H}h (automática)"
    T = {"rodada": rodada, "pessoas": {}, "modo": "sem IA"}
    ant = sorted(glob.glob(os.path.join(AP, "celulas", "whatsapp-triagem-*.json")))
    vistos = set()  # conversas já avisadas na rodada anterior (com ou sem IA): não reenviar
    if ant:
        A = json.load(open(ant[-1]))
        vistos = {(p, i["chat"]) for p, P in A.get("pessoas", {}).items() if P.get("enviado", True) for i in P.get("itens", []) if i.get("status") in ("responder", "acompanhar")}  # e-mail que falhou não conta como avisado
    # o que a última rodada COM IA julgou "sem ação" não volta como "responder" se não chegou mensagem nova depois dela (Células, 02/10)
    calados, t_ia = set(), 0
    for f_ia in reversed(ant):
        A_ia = json.load(open(f_ia))
        if A_ia.get("modo") == "sem IA": continue
        t_ia = os.path.getmtime(f_ia)
        calados = {(p, i["chat"]) for p, P in A_ia.get("pessoas", {}).items() for i in P.get("itens", []) if i.get("status") == "sem_acao"}
        break
    tot = {}
    for p in PESSOAS:
        cx = ult(os.path.join(AP, "celulas", p, "whatsapp", "caixa-*.json"))
        if not cx: continue
        caixa = json.load(open(cx))
        dm = ult(os.path.join(AP, "celulas", p, "whatsapp", "demandas-*.json"))
        dem = {e["chat"]: e for e in json.load(open(dm))} if dm else {}
        itens = []
        for c in caixa:
            ev = dem.get(c["chat"], {})
            esperando = c.get("aguardando_time_h") or 0
            pend_midia = ev.get("audios") or any(x["tipo"] == "imagem" and not x.get("texto") for x in ev.get("anexos", []))
            if esperando < a.aguardando and not (ev and pend_midia): continue
            if (p, c["chat"]) in calados and agora.timestamp() - esperando * 3600 <= t_ia: continue
            # fluxo único (Luis, 14/10 e 15/10): o time não recebe a mensagem crua do parceiro; a análise com as áreas sai na rodada com IA
            quem = c.get("master") or ("grupo " + c["chat"] if c.get("tipo") == "grupo" else c["chat"])
            pede = f"Mensagem nova de {quem}, sem resposta há {esperando:.0f}h. Os agentes analisam com a área responsável na próxima rodada (8h ou 14h)."
            neg = (c.get("negocios") or [{}])[0]
            itens.append({"grupo": c.get("tipo") == "grupo", "nova": (p, c["chat"]) not in vistos, "chat": c["chat"], "master": c.get("master"), "status": "responder" if esperando >= a.aguardando else "acompanhar",
                          "aguardando_h": esperando, "o_que_pede": pede, "entrega": entrega(ev) if ev else "",
                          "proximo_passo": "Se for urgente (prazo hoje, multa, reclamação), abra a conversa agora; senão, a resposta pronta chega na próxima rodada" if esperando >= a.aguardando else "Há áudio ou imagem: a transcrição sai na próxima rodada",
                          "negocio": neg.get("nome"), "link": neg.get("link")})
        T["pessoas"][p] = {"conversas": len(caixa), "itens": itens,
                           "leitura": f"Rodada automática (sem IA): {sum(i['status'] == 'responder' for i in itens)} conversa(s) sem resposta há {a.aguardando:g}h ou mais. A rodada com análise completa sai às 8h e às 14h."}
        tot[p] = sum(i["status"] == "responder" for i in itens)
    # Regra do Luis (01/10): pedido em grupo de Master é da Daniela, mesmo na caixa da Jenifer ou da Geovana.
    dan = T["pessoas"].get("daniela", {"conversas": 0, "itens": [], "leitura": ""})
    for q in ("jenifer", "geovana"):
        if q not in T["pessoas"]: continue
        fica = []
        for i in T["pessoas"][q]["itens"]:
            if i.get("master") and i.get("grupo"):
                if not any(x["chat"] == i["chat"] for x in dan["itens"]): dan["itens"].append(i)
            else: fica.append(i)
        T["pessoas"][q]["itens"] = fica
    T["pessoas"]["daniela"] = dan
    tot = {k: sum(i["status"] == "responder" for i in P["itens"]) for k, P in T["pessoas"].items()}
    T["leitura_geral"] = "Rodada automática, sem IA: conversas sem resposta por pessoa: " + ", ".join(f"{k} {v}" for k, v in tot.items()) + "."
    out = os.path.join(AP, "celulas", f"whatsapp-triagem-{agora:%Y-%m-%d-%Hh%M%S}.json")
    json.dump(T, open(out, "w"), ensure_ascii=False, indent=1)
    print(out)


if __name__ == "__main__":
    main()
