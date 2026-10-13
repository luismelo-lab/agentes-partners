#!/usr/bin/env python3
"""Monta o e-mail do lote semanal do Recuperador e o envia à Geovana com cópia para o Luis (decisão D27, 01/10/2026).

Sem --enviar, salva como RASCUNHO no Outlook do Mac. Só aceita destinatários @savecompany.com.br (trava em
email_layout.outlook). A decisão sobre cada tese continua sendo da Geovana. Usa AppleScript do Outlook clássico;
se a automação falhar, gera um .eml que abre no Outlook com duplo clique.

Uso: python3 email_outlook.py --para geovana.goncalves@savecompany.com.br --cc luis.melo@savecompany.com.br --lote N [--enviar]
"""
import argparse, glob, json, os, sys
sys.path.insert(0, os.path.expanduser("~/.claude/skills/depto-marketing/scripts"))
import email_layout as L  # layout único da área
from datetime import date
from email.message import EmailMessage

H = os.path.expanduser
DIR = H("~/agentes-partners/celulas/geovana/recuperador")
brl = lambda v: ("R$ " + f"{v:,.0f}".replace(",", ".")) if isinstance(v, (int, float)) and v else "—"


def montar(lote):
    """Corpo no layout único da área (depto-marketing/scripts/email_layout.py)."""
    F = json.load(open(sorted(glob.glob(os.path.join(DIR, "fila-*.json")))[-1]))
    xlsx = sorted(glob.glob(os.path.join(DIR, "Fila-Recuperador-*.xlsx")))[-1]
    tem_lote = any("lote" in r for r in F["top"])  # fila antiga, sem número de lote: vai a fila inteira (como antes)
    casos = [r for r in F["top"] if r.get("lote") == lote] if tem_lote else F["top"]
    if not casos: sys.exit(f"O lote {lote} não existe na fila atual (lotes: {sorted({r.get('lote') for r in F['top'] if r.get('lote') is not None})}).")
    tot = sum(r.get("honorário esperado (look-alike)") or 0 for r in casos)
    nz = sum(1 for r in casos if r["tipo"].startswith("Perdido")); na = len(casos) - nz
    alta = sum(1 for r in casos if r.get("aderência") == "alta")
    mi = lambda v: ("R$ " + f"{v/1e6:.2f}".replace(".", ",") + " mi") if v >= 1e6 else ("R$ " + f"{round(v/1e3):,}".replace(",", ".") + " mil")
    hoje = date.today().strftime("%d/%m/%Y")
    corpo = L.documento(
        L.cabecalho("Célula Técnica · Recuperador", f"Lote {lote} da semana", f"{hoje} · {len(casos)} casos"),
        L.paragrafo("Olá, Geovana!", "28px 32px 12px"),
        L.paragrafo(f"O lote desta semana está no arquivo anexo. São os {len(casos)} casos de maior potencial entre os "
                    "<b>perdidos zerados</b> e as <b>oportunidades abertas há mais de 90 dias</b>, já em ordem de prioridade "
                    f"(a fila completa tem {F['fila']} casos). "
                    "A ordem considera o histórico de clientes parecidos que já foram ganhos e o que o técnico registrou no parecer de cada card."),
        L.kpis([("Potencial do lote", mi(tot), "honorário esperado"), ("Casos no lote", len(casos), f"{nz} zerados · {na} abertos"),
                ("Aderência alta", f"{alta} de {len(casos)}", "Lucro Real · alimentos")]),
        L.paragrafo("Para cada caso, a planilha traz o perfil da empresa, a hipótese de tese, o que o técnico concluiu no parecer, "
                    "a taxa de sucesso de clientes parecidos e os documentos a pedir. O nome do negócio abre o card no HubSpot."),
        L.passos("Próximos passos", [f"Abra a planilha anexa, aba <b>Fila</b>, e filtre o <b>lote {lote}</b>.",
                                     "Marque <b>Aprovar para reanálise</b>, <b>Vetar</b> ou <b>Precisa de dado</b>, com o motivo, o valor validado e os minutos gastos.",
                                     "Leve os casos aprovados ao time técnico, como já faz hoje. Os vetos ensinam o Recuperador para o próximo lote."]),
        L.assinatura(),
        L.rodape("Pré-análise gerada pelo Recuperador (Célula Técnica). Hipóteses a verificar, sem promessa de valor. A tese de alíquota zero segue "
                 "sempre via PER (ressarcimento). Uso interno Save Company. A planilha também traz as abas Recorrência (empresas que já são clientes) e Gestão de Passivo."))
    return f"Recuperador · Lote {lote} da semana ({hoje}): {len(casos)} casos, {mi(tot)} em potencial", corpo, xlsx


def outlook(para, cc, assunto, corpo, anexo, abrir, enviar=False):
    return L.outlook(para, cc, assunto, corpo, [anexo], enviar=enviar, abrir=abrir)


def eml(para, cc, assunto, corpo, anexo):
    m = EmailMessage(); m["To"] = ", ".join(para); m["Cc"] = ", ".join(cc); m["Subject"] = assunto; m["X-Unsent"] = "1"
    m.set_content("Versão em HTML."); m.add_alternative(corpo, subtype="html")
    m.add_attachment(open(anexo, "rb").read(), maintype="application", subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=os.path.basename(anexo))
    f = os.path.join(DIR, f"email-lote-{date.today().isoformat()}.eml"); open(f, "wb").write(bytes(m)); return f


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--para", nargs="+", required=True); ap.add_argument("--cc", nargs="*", default=[])
    ap.add_argument("--lote", type=int, default=1); ap.add_argument("--abrir", action="store_true")
    ap.add_argument("--enviar", action="store_true", help="envia (interno, D27); sem a opção cria rascunho"); a = ap.parse_args()
    assunto, corpo, anexo = montar(a.lote)
    ok, msg = outlook(a.para, a.cc, assunto, corpo, anexo, a.abrir, a.enviar)
    if ok: print("Enviado:" if a.enviar else "Rascunho criado no Outlook (não enviado):", assunto)
    elif "BLOQUEADO" in msg: print(msg); sys.exit(1)
    else:
        print("Automação do Outlook indisponível:", msg[:300], "\nArquivo .eml gerado (abre no Outlook, pronto para revisar e enviar):", eml(a.para, a.cc, assunto, corpo, anexo))
        if a.enviar: sys.exit(2)  # pediram envio e não saiu: a rotina tem que falhar (antes saía 0 e ficava "ok")
