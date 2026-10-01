#!/usr/bin/env python3
"""Abre no GLPI os chamados das demandas do WhatsApp que os agentes não resolvem sozinhos.

Entrada: a triagem com IA (whatsapp-triagem-*.json). Cada item que precisa de outra área traz:
  "encaminhar": {"area": "juridico|tecnico|contratos|pos_venda|marketing|financeiro|ti|outros",
                 "titulo": "...", "descricao": "markdown: o que o parceiro pede · o que já levantamos · o que falta",
                 "urgencia": 1-5}
O script:
  1. registra a demanda no registro único (D-AAAA-NNNN) e evita chamado duplicado (um por demanda);
  2. PROPÕE o chamado (registro/chamados-propostos.json). Nada é aberto aqui: o chamado só vai ao GLPI depois de
     aprovado no painel Central Partners (regra do Luis, 01/10), pela rotina da Central (lib/chamados_painel.py);
  3. grava o resultado no item ("chamado") para o e-mail mostrar, e no registro de demandas.
Decisão D25 do Luis (01/10/2026): chamado interno aberto automaticamente; nada vai a parceiro ou cliente.
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
    out = []
    for l in (md or "").split("\n"):
        s = l.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        if s: out.append(f"<li>{s[2:]}</li>" if s.startswith("- ") else f"<p>{s}</p>")
    return "".join(out).replace("</p><li>", "</p><ul><li>").replace("</li><p>", "</li></ul><p>")


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
                if d and d.get("chamado", {}).get("id"):  # já existe chamado para esta demanda
                    i["chamado"] = d["chamado"]; continue
                desc = (f"<p><b>Origem:</b> WhatsApp de {p.capitalize()} · conversa {i['chat']}"
                        + (f" · Master {i['master']}" if i.get("master") else "") + (f" · demanda {d['id']}" if d else "") + "</p>"
                        + html(e.get("descricao")) + (f"<p><b>Negócio no HubSpot:</b> {i['link']}</p>" if i.get("link") else "")
                        + "<p><i>Chamado aberto pelos agentes da Área Partners. Responsável na Partners: " + p.capitalize() + ".</i></p>")
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
