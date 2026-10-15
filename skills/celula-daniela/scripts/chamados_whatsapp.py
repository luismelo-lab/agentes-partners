#!/usr/bin/env python3
"""Abre no GLPI os chamados das demandas do WhatsApp que os agentes não resolvem sozinhos.

Entrada: a triagem com IA (whatsapp-triagem-*.json). Cada item que precisa de outra área traz:
  "encaminhar": {"area": chave de infra/glpi-config.json (trib_diagnostico, jur_comunicados, ...),
                 "titulo": "<Subcategoria> <EMPRESA> x <assunto>", "descricao": "markdown: o que o parceiro pede · o que já levantamos · o que falta",
                 "urgencia": 1-5, opcionais: "empresa", "assunto", "prazo", "card_bitrix", "documentos"}
  e "especialista": o chamado escrito pelo Gerente Tributário ou Jurídico (infra/chamado-ideal.md, regra do Luis de 14/10):
                 entendemos, pedidos, anexos, faltam, prazo_motivo, entrega, riscos, checagens, nao_abrir.
A descrição sai no formulário da área (Tributário: urgência/empresa/descrição/card/prazo; Jurídico: dados/informações gerais).
Com "nao_abrir" preenchido pelo especialista, não há chamado: o motivo fica no item para o rascunho e o próximo passo.
O script:
  1. registra a demanda no registro único (D-AAAA-NNNN) e evita chamado duplicado (um por demanda);
  2. deixa o chamado pronto no painel para aprovação (registro/chamados-propostos.json); só abre no GLPI depois de aprovado (chamados_painel.py aplicar);
  3. grava o resultado no item ("chamado") para o e-mail mostrar, e no registro de demandas.
Regra do Luis (01/10 e 14/10/2026, substitui a D29): nenhum chamado abre sem aprovação no painel, mesmo com o GLPI ligado.
Depois da aprovação, chamados_painel.py aplicar abre com o usuário de quem atendeu (glpi-config modo = abrir). Nada vai a parceiro ou cliente.
Uso: python3 chamados_whatsapp.py --triagem <arquivo>
"""
import argparse, json, os, re, subprocess, sys
from datetime import datetime

AP = os.path.expanduser("~/agentes-partners")
PROP = os.path.join(AP, "registro", "chamados-propostos.json")  # fila para o painel (aprovação antes de abrir)
sys.path.insert(0, os.path.join(AP, "lib"))
import glpi  # noqa: E402
import registro_demandas as RD  # noqa: E402


import chamado_modelo as CM  # noqa: E402  texto do especialista e formulário da área (infra/chamado-ideal.md)
_e = CM._e


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
                X = e.get("especialista") or {}
                if X.get("nao_abrir"):
                    i["chamado"] = {"nao_abrir": X["nao_abrir"], "agente": X.get("agente")}; continue
                origem = (f"<p><i>Origem: WhatsApp de {p.capitalize()} · conversa {_e(__import__('protecao').limpo(i['chat']))}" + (f" · demanda {d['id']}" if d else "")
                          + f". Chamado redigido pelo {X.get('agente') or CM.AGENTE(e.get('area', ''))} (agente da Área Partners) e aprovado no painel. Responsável na Partners: {p.capitalize()}.</i></p>")
                corpo_md = CM.descricao_md(e)
                desc = CM.formulario(e.get("area", "outros"), i, e, corpo_md, origem)
                prop = {"id": (d or {}).get("id"), "pessoa": p, "area": e.get("area", "outros"),
                        "grupo": (glpi.config()["areas"].get(e.get("area")) or glpi.config()["areas"]["outros"])["nome"],
                        "titulo": (e.get("titulo") or i.get("o_que_pede", ""))[:200], "descricao": corpo_md, "descricao_html": desc,
                        "negocio": i.get("negocio"), "empresa": e.get("empresa"), "card_bitrix": e.get("card_bitrix") or i.get("card_bitrix"), "prazo": e.get("prazo"),
                        "assunto": e.get("assunto"), "o_que_pede": i.get("o_que_pede"), "especialista": X,
                        "urgencia": int(e.get("urgencia", 3)), "conversa": i["chat"], "master": i.get("master"), "link": i.get("link"),
                        "status": "proposto", "proposto_em": datetime.now().isoformat(timespec="minutes")}
                # Regra do Luis (01/10 e 14/10, substitui a D29): nenhum chamado abre sem aprovação no painel, mesmo com o GLPI ligado.
                # A abertura acontece em chamados_painel.py aplicar, depois do "Aprovar e abrir no GLPI".
                r = {}
                if r.get("id"):
                    prop.update(status="aberto", glpi_id=r["id"], url=r.get("url"), aberto_em=prop["proposto_em"]); abertos += 1
                    i["chamado"] = {"id": r["id"], "url": r.get("url"), "grupo": prop["grupo"], "titulo": prop["titulo"]}
                    if d:
                        d["chamado"] = {"status": "aberto", "glpi_id": r["id"], "url": r.get("url"), "grupo": prop["grupo"], "titulo": prop["titulo"]}
                        d["eventos"].append({"quando": prop["proposto_em"], "evento": f"chamado #{r['id']} aberto no GLPI → {prop['grupo']} (D29)"})
                    P_ = json.load(open(PROP)) if os.path.exists(PROP) else {}
                    P_[prop["id"] or f"sem-demanda-{r['id']}"] = prop; json.dump(P_, open(PROP, "w"), ensure_ascii=False, indent=1)
                    continue
                if prop["id"]:
                    P_ = json.load(open(PROP)) if os.path.exists(PROP) else {}
                    if prop["id"] not in P_: P_[prop["id"]] = prop; json.dump(P_, open(PROP, "w"), ensure_ascii=False, indent=1); rasc += 1
                i["chamado"] = {"proposto": True, "grupo": prop["grupo"], "area": prop["area"], "titulo": prop["titulo"], "descricao": prop["descricao"]}
                if d:
                    d["chamado"] = {"proposto": True, "grupo": prop["grupo"], "titulo": prop["titulo"]}
                    d["eventos"].append({"quando": prop["proposto_em"], "evento": f"chamado pronto → {prop['grupo']} (GLPI ainda não integrado: abrir pelo painel)"})
    json.dump(T, open(f, "w"), ensure_ascii=False, indent=1)
    print(f"chamados abertos no GLPI: {abertos} · prontos para abrir pelo painel (GLPI não integrado): {rasc}")


if __name__ == "__main__":
    main()
