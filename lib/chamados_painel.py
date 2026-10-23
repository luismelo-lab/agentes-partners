#!/usr/bin/env python3
"""Chamados propostos pelos agentes → aprovação no painel Central Partners → abertura no GLPI.

Regra do Luis (01/10/2026): nenhum chamado é aberto sem aprovação no painel, mesmo com o GLPI integrado.
Fluxo:
  1. chamados_whatsapp.py grava as propostas em registro/chamados-propostos.json.
  2. `publicar` gera registro/chamados-para-painel.json (as que ainda não estão no painel); a rotina do Claude grava
     cada uma no painel (coleção `chamados`, documento = ID da demanda) e roda `marcar-publicados`.
  3. No painel, a pessoa aprova (pode editar título e descrição) ou recusa (com motivo). O texto vem do especialista
     (Gerente Tributário ou Jurídico, infra/chamado-ideal.md) e sai no formulário da área (lib/chamado_modelo.py).
  4. `aplicar <pasta baixada do painel>`: para cada aprovado, abre no GLPI com o usuário de quem atendeu
     (lib/glpi.py) e imprime as atualizações que a rotina grava de volta no painel (número e link do chamado).
     Sem integração ainda, marca "aprovado: abrir manualmente" e o chamado pronto continua no painel e no e-mail.
"""
import glob, json, os, re, sys
from datetime import datetime

AP = os.environ.get("PARTNERS_AP") or os.path.expanduser("~/agentes-partners")
PROP = os.path.join(AP, "registro", "chamados-propostos.json")
SAIDA = os.path.join(AP, "registro", "chamados-para-painel.json")
APRENDE = os.path.join(AP, "registro", "chamados-aprendizados.md")
sys.path.insert(0, os.path.join(AP, "lib")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _do_portal(did, d):
    """Chamado gerado na tela "WhatsApp · Demandas" do portal (origem "portal"): vira proposta local se foi gravado pela conta da
    dona, sobre uma demanda dela no registro único, com o texto do especialista (chamado ideal). Senão, {} (fica ignorado)."""
    import portal_contas as PC, registro_demandas as RD
    if d.get("origem") != "portal": return {}
    ok, motivo = PC.conferir(d.get("proposto_por"), d.get("proposto_por_id"), d.get("pessoa"))
    with RD.Registro() as R: dem = (R.get("demandas") or {}).get(d.get("demanda") or did)
    if ok and (not dem or dem.get("pessoa") != d.get("pessoa")): ok, motivo = False, "demanda inexistente ou de outra pessoa"
    if ok and not ((d.get("especialista") or {}).get("pedidos")): ok, motivo = False, "sem o texto do especialista (chamado ideal)"
    if not ok:
        PC.alertar("chamados", did, "chamado do portal: " + motivo, d.get("proposto_por"), d.get("proposto_por_id")); return {}
    return {**{k: d.get(k) for k in ("pessoa", "area", "grupo", "titulo", "descricao", "urgencia", "master", "link", "negocio", "empresa", "prazo", "assunto", "o_que_pede", "especialista", "conversa")},
            "id": did, "status": "proposto", "origem": "portal", "proposto_em": d.get("proposto_em"), "publicado": True}


def _autor(did, d, loc, campo):
    """Só a dona do chamado (a pessoa da proposta local, não a do db) aprova ou recusa, e só por uma das quatro contas (A3)."""
    import portal_contas as PC
    if not loc:
        PC.alertar("chamados", did, "chamado não proposto pelos agentes (não está em chamados-propostos.json)", d.get(campo), d.get(campo + "_id"))
        return False, "Ignorado: este chamado não foi proposto pelos agentes."
    ok, motivo = PC.conferir(d.get(campo), d.get(campo + "_id"), loc.get("pessoa"))
    if not ok:
        PC.alertar("chamados", did, motivo, d.get(campo), d.get(campo + "_id"))
        return False, f"Decisão ignorada: só {str(loc.get('pessoa') or '').capitalize()} aprova este chamado, pela conta dela no Claude."
    return True, ""


def ler():
    return json.load(open(PROP)) if os.path.exists(PROP) else {}


def gravar(P):
    json.dump(P, open(PROP, "w"), ensure_ascii=False, indent=1)


def html(md):
    out = []
    for l in (md or "").split("\n"):
        s = l.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        if s: out.append(f"<li>{s[2:]}</li>" if s.startswith("- ") else f"<p>{s}</p>")
    return "".join(out)


def propor(arquivo):
    """Chamado vindo da Central (pedido ou originação) que a área não conseguiu responder com os dados (infra/fluxo-unico.md).
    JSON: {"id": "P-0007" ou "D-AAAA-NNNN", "pessoa", "area", "titulo", "urgencia", "master", "link", "negocio", "empresa", "prazo",
           "assunto", "o_que_pede", "especialista": {...infra/chamado-ideal.md}}. Fica "proposto" até a aprovação no painel."""
    import chamado_modelo as CM, glpi
    e = json.load(open(os.path.expanduser(arquivo))); P = ler()
    if not e.get("id") or not e.get("area") or not (e.get("especialista") or {}).get("pedidos"):
        sys.exit("faltam id, area ou especialista.pedidos (infra/chamado-ideal.md)")
    if (P.get(e["id"]) or {}).get("status") in ("aberto", "aprovado_manual", "recusado"):
        print(f"{e['id']}: já decidido no painel ({P[e['id']]['status']}), não proponho de novo"); return
    md = CM.descricao_md(e)
    origem = f"<p><i>Origem: Central de Agentes · pedido {e['id']} de {str(e.get('pessoa', '')).capitalize()}. Chamado redigido pelo {(e.get('especialista') or {}).get('agente') or CM.AGENTE(e['area'])}.</i></p>"
    P[e["id"]] = {**{k: e.get(k) for k in ("pessoa", "area", "titulo", "urgencia", "master", "link", "negocio", "empresa", "prazo", "assunto", "o_que_pede", "especialista")},
                  "id": e["id"], "grupo": (glpi.config()["areas"].get(e["area"]) or glpi.config()["areas"]["outros"])["nome"], "descricao": md,
                  "descricao_html": CM.formulario(e["area"], e, e, md, origem), "conversa": "Central de Agentes", "status": "proposto",
                  "proposto_em": datetime.now().isoformat(timespec="minutes")}
    gravar(P); print(f"{e['id']}: chamado proposto ({P[e['id']]['grupo']}). Rode `publicar` e grave no painel.")


def publicar():
    P = ler()
    novos = [{"doc_id": k, "data": {c: v[c] for c in ("pessoa", "area", "grupo", "titulo", "descricao", "urgencia", "conversa", "master", "link", "status", "proposto_em",
                                                       "negocio", "empresa", "prazo", "o_que_pede", "especialista") if c in v}}
             for k, v in P.items() if not v.get("publicado")]
    json.dump(novos, open(SAIDA, "w"), ensure_ascii=False, indent=1)
    print(f"{len(novos)} chamado(s) para gravar no painel → {SAIDA}")


def marcar_publicados(ids):
    P = ler()
    for i in ids:
        if i in P: P[i]["publicado"] = True
    gravar(P); print("marcados:", len(ids))


def aplicar(pasta):
    import glpi, registro_demandas as RD
    P = ler(); atualiza = []
    for f in glob.glob(os.path.join(pasta, "chamados", "*.json")):
        did = os.path.basename(f)[:-5]; d = json.load(open(f)); d = d["data"] if isinstance(d.get("data"), dict) else d
        loc = P.get(did) or {}
        if not loc and d.get("origem") == "portal" and d.get("status") in ("proposto", "aprovado", "recusado"):
            loc = _do_portal(did, d)
            if loc: P[did] = loc
        if d.get("status") in ("aprovado", "recusado") and loc.get("status") not in ("aberto", "aprovado_manual", "recusado"):
            ok, nota = _autor(did, d, loc, "aprovado_por" if d.get("status") == "aprovado" else "recusado_por")
            if not ok:
                if d.get("nota_agente") != nota: atualiza.append({"doc_id": did, "data": {"nota_agente": nota}})
                continue
        if d.get("status") == "aprovado" and loc.get("status") not in ("aberto", "aprovado_manual"):
            titulo = d.get("titulo_editado") or d.get("titulo") or loc.get("titulo"); desc = d.get("descricao_editada") or d.get("descricao") or loc.get("descricao")
            import chamado_modelo as CM  # mesmo formulário da área usado na proposta; texto editado no painel entra no corpo
            origem = (f"<p><i>Chamado redigido pelo {(loc.get('especialista') or {}).get('agente') or CM.AGENTE(d.get('area', ''))} (agente da Área Partners) "
                      f"e aprovado por {d.get('aprovado_por') or d.get('pessoa')} no painel.</i></p>")
            ctx = {**loc, **{k: d.get(k) for k in ("link", "master", "negocio") if d.get(k)}}
            corpo = CM.formulario(d.get("area", "outros"), ctx, {**loc, "urgencia": d.get("urgencia", loc.get("urgencia", 3))}, desc, origem)
            r = glpi.abrir(loc.get("area") or d.get("area", "outros"), titulo, corpo, d.get("urgencia", 3), pessoa=loc.get("pessoa"))
            agora = datetime.now().isoformat(timespec="minutes")
            if r.get("id"):
                loc.update(status="aberto", glpi_id=r["id"], url=r["url"], aberto_em=agora)
                atualiza.append({"doc_id": did, "data": {"status": "aberto", "glpi_id": r["id"], "url": r["url"], "aberto_em": agora}})
            elif r.get("rascunho"):
                loc.update(status="aprovado_manual", aprovado_em=agora)
                atualiza.append({"doc_id": did, "data": {"status": "aprovado_manual", "nota_agente": "GLPI ainda não integrado: abra manualmente com o texto acima."}})
            else:
                atualiza.append({"doc_id": did, "data": {"nota_agente": "Falha ao abrir no GLPI: " + str(r.get("erro"))[:200]}})
            P[did] = {**loc, **{k: d.get(k) for k in ("titulo_editado", "descricao_editada", "aprovado_por") if d.get(k)}}
            with RD.Registro() as R:
                if did in R["demandas"]:
                    R["demandas"][did].setdefault("eventos", []).append({"quando": agora, "evento": f"chamado aprovado no painel · {r.get('id') and '#' + str(r['id']) or 'abrir manualmente'}"})
                    R["demandas"][did]["chamado"] = {k: v for k, v in loc.items() if k in ("status", "glpi_id", "url", "grupo", "titulo")}
        elif d.get("status") == "recusado" and loc.get("status") != "recusado":
            loc["status"] = "recusado"; loc["motivo_recusa"] = d.get("motivo"); P[did] = loc
            with RD.Registro() as R:
                if did in R["demandas"]: R["demandas"][did]["chamado"] = {"status": "recusado", "grupo": loc.get("grupo"), "titulo": loc.get("titulo")}
            with open(APRENDE, "a") as a:
                a.write(f"- {datetime.now():%d/%m} · {d.get('pessoa')} · {d.get('area')} · recusado: {d.get('titulo')} · motivo: {d.get('motivo') or '—'}\n")
    gravar(P)
    print(json.dumps(atualiza, ensure_ascii=False))


if __name__ == "__main__":
    cmd = (sys.argv[1:] or [""])[0]
    if cmd == "publicar": publicar()
    elif cmd == "marcar-publicados": marcar_publicados(sys.argv[2].split(","))
    elif cmd == "aplicar": aplicar(sys.argv[2])
    elif cmd == "propor": propor(sys.argv[sys.argv.index("--arquivo") + 1] if "--arquivo" in sys.argv else sys.argv[2])
    else: print(__doc__)
