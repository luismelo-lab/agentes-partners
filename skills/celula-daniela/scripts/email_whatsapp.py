#!/usr/bin/env python3
"""E-mail de acompanhamento da caixa do WhatsApp: um para cada dono do número e um geral para o Luis.

Entrada: a triagem feita pelo agente depois de ler as caixas (whatsapp_hubspot.py), em
~/agentes-partners/celulas/whatsapp-triagem-AAAA-MM-DD-HHhMM.json, no formato:
{"rodada": "13h30", "pessoas": {"daniela": {"itens": [
    {"chat": "...", "master": "JGM", "status": "responder|acompanhar|sem_acao", "aguardando_h": 6.4,
     "o_que_pede": "...", "rota": "Pós-venda / Técnico", "proximo_passo": "...", "rascunho": "...",
     "prazo": "30/09 12h", "negocio": "Nome", "link": "https://...", "nova": true,
     "urgente": true,  # prazo hoje, risco de multa/perda de prazo ou reclamação: vai para o topo
     "entrega": "markdown: o que os agentes levantaram e já resolvem (status, cadastro, conflito, documentos)",
     "anexos": ["caminho de planilha/Word gerado, opcional"]}], "leitura": "1 frase"}}}

Layout: o mesmo dos e-mails da área (depto-marketing/scripts/email_layout.py).
Decisão do Luis (29/09, D23): esta rotina ENVIA os e-mails internos sem rascunho. Ela não responde a
parceiros nem clientes: a resposta no WhatsApp é sempre da dona do número.

Uso: python3 email_whatsapp.py --triagem <arquivo.json> [--rascunho]   (--rascunho = não envia, só cria)
"""
import argparse, json, os, sys
from datetime import datetime

sys.path.insert(0, os.path.expanduser("~/.claude/skills/depto-marketing/scripts"))
import email_layout as L  # noqa: E402

DONOS = {"daniela": ("Daniela", "daniela.maciel@savecompany.com.br", "Central Masters"),
         "jenifer": ("Jenifer", "jenifer.carvalho@savecompany.com.br", "Central BDR"),
         "geovana": ("Geovana", "geovana.goncalves@savecompany.com.br", "Central Técnica"),
         "luis": ("Luis", "luis.melo@savecompany.com.br", "Gestão")}  # só recebe itens próprios quando há pedidos do portal para ele
LUIS = "luis.melo@savecompany.com.br"
COR = {"responder": "#b3261e", "acompanhar": "#8a6d00", "sem_acao": "#5e5c55"}
ROT = {"responder": "Responder", "acompanhar": "Acompanhar", "sem_acao": "Sem ação"}
e = L.esc


def horas(h):
    return f"{h:.1f}".replace(".", ",") + "h" if h else "—"


def cartoes(itens, com_rascunho=True):
    out = []
    for i in itens:
        et = ("Urgente · " if i.get("urgente") else "") + ("Nova · " if i.get("nova") else "") + (f"{horas(i.get('aguardando_h'))} sem resposta" if i.get("aguardando_h") else ROT[i["status"]])
        ls = [("O que pede", e(i.get("o_que_pede")))]
        if i.get("rota"): ls.append(("Encaminhar para", e(i["rota"])))
        if i.get("proximo_passo"): ls.append(("Próximo passo", e(i["proximo_passo"]) + (f" · prazo {e(i['prazo'])}" if i.get("prazo") else "")))
        if i.get("entrega"): ls.append(("O que os agentes levantaram", L.md(i["entrega"])))
        if com_rascunho and i.get("rascunho"): ls.append(("Sugestão de resposta", f"<i>“{e(i['rascunho'])}”</i>"))
        if i.get("anexos"): ls.append(("Anexos", e(", ".join(os.path.basename(x) for x in i["anexos"]))))
        if i.get("negocio"): ls.append(("Negócio", f'<a href="{e(i.get("link"))}" style="{L.f("corpo", "normal", "#7a5f00", "text-decoration:none;")}">{e(i["negocio"])}</a>'))
        tit = i["chat"] + (f" · {i['master']}" if i.get("master") else "")
        out.append(L.cartao(tit, et, ls, COR[i["status"]]))
    return out


def ordem(itens):
    return sorted(itens, key=lambda i: ({"responder": 0, "acompanhar": 1, "sem_acao": 2}[i["status"]], not i.get("urgente"), -(i.get("aguardando_h") or 0)))


def email_dono(chave, P, rodada, hoje):
    nome, _, area = DONOS[chave]
    it = ordem(P.get("itens", []))
    resp = [i for i in it if i["status"] == "responder"]; acomp = [i for i in it if i["status"] == "acompanhar"]
    sem = [i for i in it if i["status"] == "sem_acao"]
    blocos = [L.cabecalho(f"{area} · WhatsApp", f"Acompanhamento das {rodada}", f"{hoje} · {P.get('conversas', len(it))} conversas lidas"),
              L.paragrafo(f"Olá, {e(nome)}!", "28px 32px 12px"),
              L.paragrafo(e(P.get("leitura") or "Seguem as conversas do seu WhatsApp que pedem atenção agora, já organizadas por prioridade.")),
              L.kpis([("Para responder", len(resp), "pedidos esperando você"), ("Em acompanhamento", len(acomp), "para conferir depois"),
                      ("Conversas lidas", P.get("conversas", len(it)), "nas últimas 24 horas")])]
    if resp: blocos += [L.secao("Para responder agora")] + cartoes(resp)
    if acomp: blocos += [L.secao("Em acompanhamento")] + cartoes(acomp)
    if not resp and not acomp:
        blocos.append(L.paragrafo("<b>Nenhuma conversa esperando resposta.</b> Tudo em dia nesta rodada."))
    if sem:
        blocos.append(L.paragrafo(f'<span style="{L.f("apoio", "normal", L.CINZA)}">Sem ação nesta rodada: '
                                  + e(", ".join(i["chat"] for i in sem[:8])) + (" e outras." if len(sem) > 8 else ".") + "</span>", "4px 32px 8px"))
    blocos += [L.passos("Como usar", ["Responda pelo seu WhatsApp, como sempre. A sugestão de resposta é só um ponto de partida.",
                                      "Encaminhe o pedido à área indicada quando houver uma.",
                                      "A próxima leitura confere se a conversa foi respondida e tira ela da lista."]),
               L.assinatura(),
               L.rodape("Leitura automática das conversas registradas pelo Eazybe no HubSpot, 4 vezes ao dia. O agente não envia mensagens a parceiros "
                        "nem a clientes. Uso interno Save Company.")]
    assunto = f"WhatsApp · {rodada}: {len(resp)} para responder" + (f", {len(acomp)} em acompanhamento" if acomp else "")
    return assunto, L.documento(*blocos)


def email_luis(T, rodada, hoje):
    tot = {k: [i for i in P.get("itens", []) if i["status"] == "responder"] for k, P in T["pessoas"].items()}
    blocos = [L.cabecalho("Área Partners · WhatsApp", f"Visão geral das {rodada}", hoje),
              L.paragrafo("Olá, Luis!", "28px 32px 12px"),
              L.paragrafo(e(T.get("leitura_geral") or "Resumo das caixas de WhatsApp do time nesta rodada.")),
              L.kpis([(DONOS[k][0], len(v), "para responder") for k, v in tot.items()][:3])]
    for k, P in T["pessoas"].items():
        it = ordem([i for i in P.get("itens", []) if i["status"] != "sem_acao"])
        blocos.append(L.secao(f"{DONOS[k][0]} · {P.get('conversas', 0)} conversas"))
        if not it:
            blocos.append(L.paragrafo("Nada pendente."))
        blocos += cartoes(it[:6], com_rascunho=False)
        if len(it) > 6: blocos.append(L.paragrafo(f"E mais {len(it) - 6} no e-mail dela."))
    blocos.append(L.rodape("Leitura automática das conversas registradas pelo Eazybe no HubSpot. Cada dona do número recebeu o próprio e-mail. Uso interno."))
    return f"WhatsApp do time · {rodada}: " + ", ".join(f"{DONOS[k][0]} {len(v)}" for k, v in tot.items()) + " para responder", L.documento(*blocos)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--triagem", required=True); ap.add_argument("--rascunho", action="store_true")
    a = ap.parse_args()
    T = json.load(open(os.path.expanduser(a.triagem)))
    import subprocess  # registro único de demandas (~/agentes-partners/lib/registro_demandas.py)
    RD = os.path.expanduser("~/agentes-partners/lib/registro_demandas.py")
    subprocess.run([sys.executable, RD, "whatsapp", "--triagem", os.path.expanduser(a.triagem)], capture_output=True)
    subprocess.run([sys.executable, RD, "planilhas"], capture_output=True)
    rodada = T.get("rodada") or datetime.now().strftime("%Hh%M"); hoje = datetime.now().strftime("%d/%m/%Y")
    enviar = not a.rascunho
    sem_ia = T.get("modo") == "sem IA"
    for k, P in T["pessoas"].items():
        if not P.get("itens") and not P.get("conversas"):
            print(f"{k}: sem conversas nesta rodada, e-mail não enviado"); continue
        if sem_ia and not any(i.get("nova") and i.get("status") == "responder" for i in P.get("itens", [])):
            print(f"{k}: nada novo para responder desde a última rodada, e-mail não enviado"); continue
        assunto, corpo = email_dono(k, P, rodada, hoje)
        anexos = [os.path.expanduser(x) for i in P.get("itens", []) for x in (i.get("anexos") or []) if os.path.exists(os.path.expanduser(x))]
        ok, msg = L.outlook([DONOS[k][1]], [], assunto, corpo, anexos, enviar=enviar)
        print(f"{k}: {'enviado' if ok and enviar else 'rascunho criado' if ok else 'FALHOU ' + msg[:200]} · {assunto}")
    if sem_ia:
        print("luis: rodada sem IA não gera o resumo geral"); return
    assunto, corpo = email_luis(T, rodada, hoje)
    ok, msg = L.outlook([LUIS], [], assunto, corpo, enviar=enviar)
    print(f"luis: {'enviado' if ok and enviar else 'rascunho criado' if ok else 'FALHOU ' + msg[:200]} · {assunto}")


if __name__ == "__main__":
    main()
