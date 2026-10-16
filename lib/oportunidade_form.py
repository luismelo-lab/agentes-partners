#!/usr/bin/env python3
"""Cadastro de nova oportunidade no formulário "Novas Oportunidades" do HubSpot quando a recorrência é aprovada na Central.

Formulário: https://shwvx.share.hsforms.com/2cSJNCVh9QvK6sVGGwsbY4A (portal 47865021, form 71224d09-587d-42f2-bab1-5186c2c6d8e0).
Envio pela API pública de submissão de formulários (o mesmo caminho do formulário na web; não usa o token do HubSpot).

  python3 lib/oportunidade_form.py montar <id do negócio da última venda>   monta e confere os campos (não envia)
  python3 lib/oportunidade_form.py enviar <id> [--confirmo]                envia; sem --confirmo só mostra o que seria enviado

Regras:
- Só roda para recorrência APROVADA no painel (decisão da Geovana). Nada é enviado sem essa aprovação.
- Campo obrigatório sem dado: não envia; devolve a lista do que falta e quem fornece (padrão de entrega).
- Até o Luis liberar (arquivo ~/agentes-partners/.oportunidade-form-liberado, criado depois da 1ª conferência), o envio
  real fica bloqueado e tudo sai como prévia para conferência.
- Registro de cada envio em registro/oportunidades-enviadas.json (não envia duas vezes o mesmo negócio).
"""
import glob, json, os, re, subprocess, sys, time

AP = os.path.expanduser("~/agentes-partners"); SK = os.path.expanduser("~/.claude/skills")
sys.path.insert(0, os.path.join(AP, "lib")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SK, "depto-resultados/scripts"))
PORTAL, FORM = "47865021", "71224d09-587d-42f2-bab1-5186c2c6d8e0"
URL = f"https://api.hsforms.com/submissions/v3/integration/submit/{PORTAL}/{FORM}"
REG = os.path.join(AP, "registro", "oportunidades-enviadas.json")
LIBERADO = os.path.join(AP, ".oportunidade-form-liberado")
CFG = os.path.join(AP, "infra", "oportunidade-form.json")  # opções das listas e ID de cada parceiro (preencher quando o escopo liberar)
OBRIG = ["firstname", "lastname", "email", "phone", "razao_social", "cnpj", "regimes_tributarios", "analises_a_serem_feitas",
         "setor_da_empresa", "hs_state_code", "city", "bairro", "address", "novo_lead_ou_cliente_da_base_", "id_do_parceiro", "nome_do_gestor"]


def _hb(did):
    f = sorted(glob.glob(os.path.join(AP, "departamentos/resultados/dados/hubspot-*.json")))[-1]
    return next((n for n in json.load(open(f))["negocios"] if str(n["id"]) == str(did)), None)


def _contato_empresa(did):
    """Contato (sócio) e empresa associados ao negócio anterior. Precisa dos escopos de leitura de contatos e empresas."""
    import hubspot_fonte as HF
    out, falta = {}, []
    for obj, props in (("contacts", "firstname,lastname,email,phone,mobilephone"), ("companies", "name,address,city,state,zip,bairro,cep")):
        try:
            ids = [x["toObjectId"] for x in HF.call("GET", f"/crm/v4/objects/deals/{did}/associations/{obj}", tries=2).get("results", [])]
            if ids: out[obj] = HF.call("GET", f"/crm/v3/objects/{obj}/{ids[0]}?properties={props}", tries=2).get("properties", {})
        except SystemExit as e:
            falta.append(f"leitura de {'contatos' if obj == 'contacts' else 'empresas'} no HubSpot (escopo crm.objects.{obj}.read)" if "403" in str(e) else str(e)[:120])
    return out, falta


def montar(did):
    """Campos do formulário a partir da última venda, do parecer, da Receita e do contato anterior. Devolve (campos, falta)."""
    import parecer_regras as PR
    n = _hb(did)
    if not n: return {}, [f"negócio {did} não está no download do HubSpot"]
    x = n.get("extras") or {}; cfg = json.load(open(CFG)) if os.path.exists(CFG) else {}
    ce, falta = _contato_empresa(did); ct = ce.get("contacts") or {}; em = ce.get("companies") or {}
    _, p = PR.ultimo_parecer([str(did)])
    rf = PR.receita(x.get("cnpj"))
    teses = sorted({str(n.get("variante"))} - {"None", ""})
    c = {"firstname": ct.get("firstname"), "lastname": ct.get("lastname"), "email": ct.get("email"), "phone": ct.get("phone") or ct.get("mobilephone"),
         "razao_social": n.get("nome"), "cnpj": re.sub(r"\D", "", str(x.get("cnpj") or "")) or None,
         "regimes_tributarios": PR.regime(p, str(did)) or x.get("regime"), "analises_a_serem_feitas": "; ".join(teses) or None,
         "setor_da_empresa": n.get("segmento"), "hs_state_code": x.get("uf") or em.get("state"), "city": x.get("cidade") or em.get("city"),
         "bairro": em.get("bairro"), "address": em.get("address"), "cep": em.get("zip") or em.get("cep"),
         "novo_lead_ou_cliente_da_base_": (cfg.get("opcoes", {}).get("novo_lead_ou_cliente_da_base_", {}) or {}).get("cliente") or "Cliente da base",
         "id_do_parceiro": (cfg.get("parceiros") or {}).get(n.get("parceiro") or ""), "nome_do_gestor": cfg.get("gestor_padrao"),
         "observacoes": f"Recorrência aprovada na Central Partners (último ganho {str(n.get('fechado'))[:10]}, negócio {did})."
                        + (f" Situação na Receita: {rf['situacao']}." if rf.get("situacao") else "")}
    if rf.get("situacao") and rf["situacao"] != "Ativa" and "não encontrado" not in rf["situacao"] and "sem CNPJ" not in rf["situacao"]:
        falta.insert(0, f"BLOQUEADO: empresa {rf['situacao']} na Receita; recorrência não pode ser cadastrada (Geovana confirma)")
    # opções das listas: o valor enviado tem de ser exatamente uma opção do formulário (infra/oportunidade-form.json)
    for campo in ("regimes_tributarios", "setor_da_empresa", "analises_a_serem_feitas", "nome_do_gestor"):
        ops = (cfg.get("opcoes") or {}).get(campo)
        if ops and c.get(campo) and c[campo] not in ops:
            falta.append(f"{campo}: '{c[campo]}' não é opção do formulário (opções em infra/oportunidade-form.json)")
    falta += [f"{k}: sem dado" + (" (vem do contato do negócio anterior)" if k in ("firstname", "lastname", "email", "phone") else
                                  " (vem da empresa no HubSpot)" if k in ("bairro", "address") else
                                  " (ID do parceiro: preencher em infra/oportunidade-form.json)" if k == "id_do_parceiro" else
                                  " (gestor de parceria: preencher em infra/oportunidade-form.json)" if k == "nome_do_gestor" else "")
              for k in OBRIG if not c.get(k)]
    return {k: v for k, v in c.items() if v}, sorted(set(falta))


def enviar(did, confirmo=False):
    reg = json.load(open(REG)) if os.path.exists(REG) else {}
    if str(did) in reg: return {"ok": False, "motivo": f"já enviado em {reg[str(did)]['quando']}"}
    campos, falta = montar(did)
    if falta: return {"ok": False, "falta": falta, "campos": campos}
    corpo = {"fields": [{"objectTypeId": "0-1", "name": k, "value": str(v)} for k, v in campos.items()],
             "context": {"pageUri": "https://shwvx.share.hsforms.com/2cSJNCVh9QvK6sVGGwsbY4A", "pageName": "Central Partners · recorrência aprovada"}}
    if not (confirmo and os.path.exists(LIBERADO)):
        return {"ok": False, "previa": True, "motivo": "prévia: envio real só depois da liberação do Luis (.oportunidade-form-liberado)", "campos": campos}
    r = subprocess.run(["curl", "-sS", "-m", "60", "-X", "POST", URL, "-H", "Content-Type: application/json", "--data-binary", "@-", "-w", "\n%{http_code}"],
                       input=json.dumps(corpo).encode(), capture_output=True)
    txt, _, code = r.stdout.decode("utf-8", "replace").rpartition("\n")
    ok = code.startswith("2")
    if ok:
        reg[str(did)] = {"quando": time.strftime("%Y-%m-%d %H:%M"), "campos": campos}
        json.dump(reg, open(REG, "w"), ensure_ascii=False, indent=1)
    return {"ok": ok, "http": code, "resposta": txt[:300]}


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "montar":
        c, f = montar(a[1]); print(json.dumps({"campos": c, "falta": f}, ensure_ascii=False, indent=1))
    elif len(a) >= 2 and a[0] == "enviar":
        print(json.dumps(enviar(a[1], "--confirmo" in a), ensure_ascii=False, indent=1))
    else:
        print(__doc__)
