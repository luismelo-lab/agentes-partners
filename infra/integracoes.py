#!/usr/bin/env python3
"""Verifica e liga as integrações (Office/Graph, GLPI e leitura de arquivos do HubSpot) com segurança.

  python3 infra/integracoes.py verificar          só leitura: nada é enviado, aberto ou alterado
  python3 infra/integracoes.py ligar email        e-mail de teste só para o Luis; se chegar, liga o Graph e tira a pausa do e-mail
  python3 infra/integracoes.py ligar glpi         mapeia as categorias e passa o GLPI para "abrir" (só abre depois da aprovação no painel)
  python3 infra/integracoes.py ligar pareceres    lê os pareceres guardados no HubSpot que estavam esperando permissão (demora)

Segredos: ficam no ~/agentes-partners/.env (o Luis ou a TI colam lá). Este script só verifica se existem e se funcionam;
nunca imprime nem copia o valor.
"""
import json, os, subprocess, sys, time

AP = os.path.expanduser("~/agentes-partners"); SK = os.path.expanduser("~/.claude/skills")
sys.path.insert(0, os.path.join(AP, "lib")); sys.path.insert(0, os.path.join(SK, "depto-resultados/scripts"))
RES = []


def linha(nome, ok, msg, proximo=""):
    RES.append((nome, ok, msg, proximo))
    print(f"{'ok    ' if ok is True else 'FALTA ' if ok is None else 'ERRO  '} {nome}: {msg}" + (f"\n         → {proximo}" if proximo else ""))


def tem(k):
    import graph
    return bool(graph._env(k))


def v_graph():
    import graph
    faltam = [k for k in ("GRAPH_TENANT_ID", "GRAPH_CLIENT_ID", "GRAPH_CLIENT_SECRET", "AGENTES_CAIXA") if not tem(k)]
    if faltam: return linha("Office (Graph)", None, "faltam no .env: " + ", ".join(faltam), "a TI entrega; você cola no ~/agentes-partners/.env (uma por linha: NOME=valor)")
    try: graph.token()
    except SystemExit as e: return linha("Office (Graph)", False, str(e)[:160], "conferir com a TI o ID do locatário, o ID do app e o segredo")
    try: n = len(graph.listar(1))
    except SystemExit as e: return linha("Office (Graph)", False, "login ok, mas a caixa não abriu: " + str(e)[:140], "a TI precisa liberar Mail.ReadWrite e Mail.Send para a caixa " + "AGENTES_CAIXA")
    linha("Office (Graph)", True, f"login ok; caixa lida ({n} e-mail(s) [AGENTES] nas últimas 24h)" + (" · ligado" if graph.ligado("email") else " · ainda desligado"),
          "" if graph.ligado("email") else "rode: python3 ~/agentes-partners/infra/integracoes.py ligar email")


def v_glpi():
    import glpi
    if not (glpi._env("GLPI_CLIENT_ID") and glpi._env("GLPI_CLIENT_SECRET")):
        return linha("GLPI", None, "faltam GLPI_CLIENT_ID e GLPI_CLIENT_SECRET no .env", "a TI cria o cliente OAuth (docs/GLPI.md)")
    contas = [p for p in ("luis", "daniela", "geovana", "jenifer") if glpi.tem_conta(p)]
    servico = bool(glpi._env("GLPI_USUARIO"))
    if not contas and not servico:
        return linha("GLPI", None, "cliente OAuth ok, mas ninguém autorizou ainda", "cada pessoa roda uma vez: python3 ~/agentes-partners/lib/glpi.py autorizar <nome> (entra no GLPI e clica em Autorizar)")
    try:
        me = glpi.api("GET", "/Administration/User/Me", conta=contas[0] if contas else None)
        cfg = glpi.config(); sem = [k for k, a in cfg["areas"].items() if not a.get("categoria_id") and k != "outros"]
        linha("GLPI", True, f"login ok ({me.get('username')}); contas autorizadas: {', '.join(contas) or 'conta de serviço'}; modo {cfg.get('modo')}; "
              f"{len(cfg['areas']) - len(sem)} de {len(cfg['areas'])} categorias mapeadas", "" if cfg.get("modo") == "abrir" and not sem else "rode: python3 ~/agentes-partners/infra/integracoes.py ligar glpi")
    except SystemExit as e:
        linha("GLPI", False, str(e)[:160], "refazer a autorização da pessoa ou conferir o cliente OAuth")


def v_hubspot():
    import glob, hubspot_fonte as HF
    try: HF.call("GET", "/crm/v3/pipelines/deals", tries=2)
    except SystemExit as e: return linha("HubSpot (leitura)", False, str(e)[:160])
    f = sorted(glob.glob(os.path.join(AP, "departamentos/resultados/dados/hubspot-*.json")))
    fid = None
    if f:
        for n in json.load(open(f[-1]))["negocios"]:
            v = str((n.get("extras") or {}).get("parecer_rt") or "").split(";")[0].strip()
            if v.isdigit(): fid = v; break
    if not fid: return linha("HubSpot (leitura)", True, "negócios ok; nenhum arquivo para testar")
    try:
        HF.call("GET", f"/files/v3/files/{fid}/signed-url", tries=2)
        pend = sum(1 for r in json.load(open(os.path.join(AP, "celulas/geovana/pareceres/resumos.json"))).values() if r.get("pendentes"))
        linha("HubSpot (arquivos)", True, f"leitura de arquivos liberada; {pend} parecer(es) esperando leitura", "rode: python3 ~/agentes-partners/infra/integracoes.py ligar pareceres" if pend else "")
    except SystemExit as e:
        linha("HubSpot (arquivos)", None if "403" in str(e) else False, "sem permissão de leitura de arquivos (escopo files)" if "403" in str(e) else str(e)[:160],
              "no HubSpot: Configurações → Integrações → Aplicativos privados → app dos agentes → Escopos → files (leitura)")


def v_eazybe():
    import eazybe
    if not (eazybe._env("EAZYBE_API_URL") and eazybe._env("EAZYBE_API_KEY")):
        return linha("WhatsApp (Eazybe direto)", None, "faltam EAZYBE_API_URL e EAZYBE_API_KEY no .env", "pegar no painel da Eazybe (API de mensagens) e colar no ~/agentes-partners/.env")
    try:
        d = eazybe.baixar(int((time.time() - 3600) * 1000))
        linha("WhatsApp (Eazybe direto)", True, f"acesso ok: {len(d)} conversa(s) na última hora")
    except SystemExit as e: linha("WhatsApp (Eazybe direto)", False, str(e)[:160])


def ligar_email():
    import graph
    v_graph()
    if RES[-1][1] is not True: sys.exit("O Graph ainda não passou na verificação: nada foi ligado.")
    ok, msg = graph.enviar(["luis.melo@savecompany.com.br"], [], "[Partners · teste] E-mail dos agentes pelo Office",
                           "<p>Teste da integração com o Office (Microsoft Graph). Se este e-mail chegou, os agentes voltam a enviar e ler e-mails.</p>", [], rascunho=False) \
        if hasattr(graph, "enviar") else (False, "graph.enviar não encontrado")
    if not ok: sys.exit("O e-mail de teste não saiu: " + str(msg)[:200])
    open(os.path.join(AP, ".email-graph"), "w").write(time.strftime("%Y-%m-%d %H:%M") + " ligado por integracoes.py\n")
    p = os.path.join(AP, ".email-pausado")
    if os.path.exists(p): os.rename(p, p + ".desligado-" + time.strftime("%Y%m%d"))
    print("E-mail ligado pelo Office. Confira o e-mail de teste na sua caixa. As mensagens guardadas no OneDrive durante a pausa continuam lá.")


def ligar_glpi():
    import glpi
    v_glpi()
    if RES[-1][1] is not True: sys.exit("O GLPI ainda não passou na verificação: nada foi ligado.")
    contas = [p for p in ("luis", "daniela", "geovana", "jenifer") if glpi.tem_conta(p)]
    glpi.categorias(contas[0] if contas else None)
    cfg = glpi.config(); sem = [a["nome"] for k, a in cfg["areas"].items() if not a.get("categoria_id") and k != "outros"]
    cfg["modo"] = "abrir"; json.dump(cfg, open(glpi.CFG, "w"), ensure_ascii=False, indent=1)
    print("GLPI ligado: os chamados APROVADOS no painel passam a abrir sozinhos, com o usuário de quem atendeu. Nada abre sem aprovação.")
    if sem: print("Categorias sem ID (o chamado abre sem categoria e a área reclassifica):", "; ".join(sem))


def ligar_pareceres():
    v_hubspot()
    if not any(n == "HubSpot (arquivos)" and ok is True for n, ok, *_ in RES): sys.exit("A leitura de arquivos do HubSpot ainda não foi liberada.")
    print("Lendo os pareceres que estavam esperando (pode levar mais de 1 hora; o log fica em celulas/geovana/pareceres/pendentes.log)…")
    log = open(os.path.join(AP, "celulas/geovana/pareceres/pendentes.log"), "a")
    subprocess.Popen([sys.executable, os.path.join(SK, "recuperador/scripts/pareceres.py"), "--todos", "--pendentes"], stdout=log, stderr=log, start_new_session=True)
    print("Iniciado em segundo plano.")


if __name__ == "__main__":
    a = sys.argv[1:] or ["verificar"]
    if a[0] == "verificar":
        v_graph(); v_glpi(); v_hubspot(); v_eazybe()
        ok = sum(1 for r in RES if r[1] is True); print(f"\n{ok} de {len(RES)} integrações prontas.")
    elif a[:2] == ["ligar", "email"]: ligar_email()
    elif a[:2] == ["ligar", "glpi"]: ligar_glpi()
    elif a[:2] == ["ligar", "pareceres"]: ligar_pareceres()
    else: print(__doc__)
