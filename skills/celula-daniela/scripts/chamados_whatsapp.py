#!/usr/bin/env python3
"""Abre no GLPI os chamados das demandas do WhatsApp que os agentes não resolvem sozinhos.

Entrada: a triagem com IA (whatsapp-triagem-*.json). Cada item que precisa de outra área traz:
  "encaminhar": {"area": chave de infra/glpi-config.json (trib_diagnostico, jur_comunicados, ...),
                 "titulo": "<Subcategoria> <EMPRESA> x <assunto>", "descricao": "markdown: o que o parceiro pede · o que já levantamos · o que falta",
                 "urgencia": 1-5, opcionais: "empresa", "assunto", "prazo", "card_bitrix", "documentos"}
A descrição sai no formulário da área (Tributário: urgência/empresa/descrição/card/prazo; Jurídico: dados/informações gerais).
O script:
  1. registra a demanda no registro único (D-AAAA-NNNN) e evita chamado duplicado (um por demanda);
  2. PROPÕE o chamado (registro/chamados-propostos.json). Nada é aberto aqui: o chamado só vai ao GLPI depois de
     aprovado no painel Central Partners (regra do Luis, 01/10), pela rotina da Central (lib/chamados_painel.py);
  3. grava o resultado no item ("chamado") para o e-mail mostrar, e no registro de demandas.
Decisão D25 do Luis (01/10/2026): chamado interno proposto; abre só depois de aprovado no painel; nada vai a parceiro ou cliente.
Uso: python3 chamados_whatsapp.py --triagem <arquivo>
"""
import argparse, json, os, re, subprocess, sys
from datetime import datetime

AP = os.path.expanduser("~/agentes-partners")
PROP = os.path.join(AP, "registro", "chamados-propostos.json")  # fila para o painel (aprovação antes de abrir)
sys.path.insert(0, os.path.join(AP, "lib"))
import glpi  # noqa: E402
import registro_demandas as RD  # noqa: E402


def html(md):
    out, lista = [], False
    for l in (md or "").split("\n"):
        s = l.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        if not s: continue
        item = s.startswith("- ")
        if item and not lista: out.append("<ul>")
        if not item and lista: out.append("</ul>")
        lista = item
        out.append(f"<li>{s[2:]}</li>" if item else f"<p>{s}</p>")
    return "".join(out) + ("</ul>" if lista else "")


URG = {1: "Baixa", 2: "Baixa", 3: "Média", 4: "Alta", 5: "Muito alta"}


def _e(t):
    return str(t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def formulario(area, i, e, origem):
    """Descrição no formulário que a área usa no GLPI (lido de 152 chamados reais, infra/glpi-regras.md)."""
    sys.path.insert(0, os.path.join(AP, "lib")); import protecao as PR  # nada de dado pessoal no painel nem no GLPI
    corpo = html(PR.limpo(e.get("descricao")))
    card = e.get("card_bitrix") or i.get("card_bitrix")
    if area.startswith("trib_"):
        return (f"<p><b>1) Urgência:</b> {URG.get(int(e.get('urgencia', 3)), 'Média')}</p>"
                f"<p><b>2) Empresa:</b> {_e(e.get('empresa') or i.get('negocio') or 'a confirmar')}</p>"
                f"<p><b>3) Descrição:</b></p>{corpo}"
                f"<p><b>4) Link do Card:</b> {_e(card) if card else 'sem card no Bitrix localizado'}"
                + (f" · HubSpot: {_e(i['link'])}" if i.get("link") else "") + "</p>"
                f"<p><b>5) Prazo de Entrega:</b> {_e(e.get('prazo') or i.get('prazo') or 'a definir pela área')}</p>{origem}")
    if area.startswith("jur_"):
        return (f"<p><b>DADOS</b></p><p>1) Setor Solicitante: MASTER</p><p>2) Parceiro Solicitante: {_e(i.get('master') or 'a confirmar')}</p>"
                f"<p><b>INFORMAÇÕES GERAIS</b></p><p>1) Assunto: {_e(e.get('assunto') or i.get('o_que_pede'))}</p><p>2) Classe: Interna</p>"
                f"<p>3) Informações Adicionais:</p>{corpo}"
                f"<p>4) Documentos: {_e(e.get('documentos') or 'anexos da conversa no WhatsApp (a Partners anexa ao abrir)')}"
                + (f" · Card: {_e(card)}" if card else "") + (f" · HubSpot: {_e(i['link'])}" if i.get("link") else "") + f"</p>{origem}")
    return origem + corpo + (f"<p><b>Negócio no HubSpot:</b> {_e(i['link'])}</p>" if i.get("link") else "")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--triagem", required=True); a = ap.parse_args()
    f = os.path.expanduser(a.triagem); T = json.load(open(f))
    subprocess.run([sys.executable, os.path.join(AP, "lib/registro_demandas.py"), "whatsapp", "--triagem", f], capture_output=True)
    abertos = rasc = 0
    with RD.Registro() as R:
        for p, P in T.get("pessoas", {}).items():
            for i in P.get("itens", []):
                e = i.get("encaminhar")
                if not e or i.get("status") not in ("responder", "acompanhar"): continue
                d = RD.achar(R, f"whatsapp|{p}|{i['chat']}")
                ch = (d or {}).get("chamado") or {}
                if ch.get("status") == "recusado": continue  # recusado no painel: não propõe de novo para a mesma demanda
                if ch.get("glpi_id") or ch.get("id") or ch.get("status") in ("aberto", "aprovado_manual"):  # já aprovado/aberto (Células, 02/10)
                    i["chamado"] = {"id": ch.get("glpi_id") or ch.get("id"), "url": ch.get("url"), "grupo": ch.get("grupo"), "titulo": ch.get("titulo"),
                                    "rascunho": not (ch.get("glpi_id") or ch.get("id"))}; continue
                origem = (f"<p><i>Origem: WhatsApp de {p.capitalize()} · conversa {_e(__import__('protecao').limpo(i['chat']))}" + (f" · demanda {d['id']}" if d else "")
                          + f". Chamado preparado pelos agentes da Área Partners e aprovado no painel. Responsável na Partners: {p.capitalize()}.</i></p>")
                desc = formulario(e.get("area", "outros"), i, e, origem)
                prop = {"id": (d or {}).get("id"), "pessoa": p, "area": e.get("area", "outros"),
                        "grupo": (glpi.config()["areas"].get(e.get("area")) or glpi.config()["areas"]["outros"])["nome"],
                        "titulo": (e.get("titulo") or i.get("o_que_pede", ""))[:200], "descricao": e.get("descricao") or "", "descricao_html": desc,
                        "urgencia": int(e.get("urgencia", 3)), "conversa": i["chat"], "master": i.get("master"), "link": i.get("link"),
                        "status": "proposto", "proposto_em": datetime.now().isoformat(timespec="minutes")}
                if prop["id"]:
                    P_ = json.load(open(PROP)) if os.path.exists(PROP) else {}
                    if prop["id"] not in P_: P_[prop["id"]] = prop; json.dump(P_, open(PROP, "w"), ensure_ascii=False, indent=1); rasc += 1
                i["chamado"] = {"proposto": True, "grupo": prop["grupo"], "area": prop["area"], "titulo": prop["titulo"], "descricao": prop["descricao"]}
                if d:
                    d["chamado"] = {"proposto": True, "grupo": prop["grupo"], "titulo": prop["titulo"]}
                    d["eventos"].append({"quando": prop["proposto_em"], "evento": f"chamado proposto → {prop['grupo']} (aguarda aprovação no painel)"})
    json.dump(T, open(f, "w"), ensure_ascii=False, indent=1)
    print(f"chamados propostos para aprovação no painel: {rasc}")


if __name__ == "__main__":
    main()
