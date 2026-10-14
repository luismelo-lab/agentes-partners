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

AP = os.path.expanduser("~/agentes-partners")
PROP = os.path.join(AP, "registro", "chamados-propostos.json")
SAIDA = os.path.join(AP, "registro", "chamados-para-painel.json")
APRENDE = os.path.join(AP, "registro", "chamados-aprendizados.md")
sys.path.insert(0, os.path.join(AP, "lib"))


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
        if d.get("status") == "aprovado" and loc.get("status") not in ("aberto", "aprovado_manual"):
            titulo = d.get("titulo_editado") or d.get("titulo"); desc = d.get("descricao_editada") or d.get("descricao")
            import chamado_modelo as CM  # mesmo formulário da área usado na proposta; texto editado no painel entra no corpo
            origem = (f"<p><i>Chamado redigido pelo {(loc.get('especialista') or {}).get('agente') or CM.AGENTE(d.get('area', ''))} (agente da Área Partners) "
                      f"e aprovado por {d.get('aprovado_por') or d.get('pessoa')} no painel.</i></p>")
            ctx = {**loc, **{k: d.get(k) for k in ("link", "master", "negocio") if d.get(k)}}
            corpo = CM.formulario(d.get("area", "outros"), ctx, {**loc, "urgencia": d.get("urgencia", loc.get("urgencia", 3))}, desc, origem)
            r = glpi.abrir(d.get("area", "outros"), titulo, corpo, d.get("urgencia", 3), pessoa=d.get("pessoa"))
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
    else: print(__doc__)
