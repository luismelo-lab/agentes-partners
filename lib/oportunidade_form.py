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
CFG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "infra", "oportunidade-form.json")  # opções das listas e ID de cada parceiro (preencher quando o escopo liberar)
OBRIG = ["firstname", "lastname", "email", "phone", "razao_social", "cnpj", "regimes_tributarios", "analises_a_serem_feitas",
         "setor_da_empresa", "hs_state_code", "city", "bairro", "address", "novo_lead_ou_cliente_da_base_", "id_do_parceiro", "nome_do_gestor"]


def _hb(did):
    f = sorted(glob.glob(os.path.join(AP, "departamentos/resultados/dados/hubspot-*.json")))[-1]
    return next((n for n in json.load(open(f))["negocios"] if str(n["id"]) == str(did)), None)


PROPS = ["dealname", "razao_social", "cpf_cnpj", "nome_do_socio", "sobrenome", "nome_do_contato", "e_mail_do_socio", "e_mail_do_contato",
         "responsavel_legal___e_mail", "email_da_empresa", "telefone_do_socio", "numero_de_celular_do_socio", "whatsapp_do_contato",
         "numero_de_telefone", "numero_de_telefone_da_empresa", "possui_debitos_", "valor_do_debito", "qual_e_o_regime_tributario_da_empresa_",
         "seto", "estado", "endereco", "data_de_validade_ecac", "hubspot_owner_id", "variante"]
DANIELA_OWNER = "79560621"  # proprietária no HubSpot (regra do Luis, 16/10: a Daniela é a gestora e a dona do negócio novo)


def _negocio(did):
    """Lê os campos do negócio direto no HubSpot (leitura de negócios já liberada no token dos agentes)."""
    import hubspot_fonte as HF
    try: return HF.call("GET", f"/crm/v3/objects/deals/{did}?properties={','.join(PROPS)}", tries=2).get("properties", {}), None
    except SystemExit as e: return {}, str(e)[:150]


def _endereco(txt):
    """'Rua X, 123, Bairro Y, Cidade - UF, CEP 00000-000' → (endereço, bairro, cidade, cep). Melhor esforço; o que não achar fica vazio."""
    t = str(txt or "").strip()
    if not t: return None, None, None, None
    cep = (re.search(r"\b(\d{5})-?(\d{3})\b", t) or [None])[0]
    partes = [p.strip() for p in re.split(r"[,;\n]| - ", re.sub(r"\b\d{5}-?\d{3}\b|CEP:?", "", t, flags=re.I)) if p.strip()]
    end = ", ".join(partes[:2]) if len(partes) >= 2 and re.match(r"^\d", partes[1] or "") else (partes[0] if partes else None)
    resto = partes[2:] if end and "," in end else partes[1:]
    resto = [p for p in resto if not re.fullmatch(r"[A-Z]{2}", p)]
    bairro = resto[0] if len(resto) >= 2 else None; cidade = resto[-1] if resto else None
    return end, bairro, cidade, re.sub(r"\D", "", cep) if cep else None


def _cep_receita(cnpj):
    import sqlite3
    try:
        db = sqlite3.connect(os.path.join(AP, "dados-publicos/receita/cnpj.sqlite"))
        r = db.execute("select cep from estab where cnpj=?", (str(cnpj or "").zfill(14),)).fetchone()
        return re.sub(r"\D", "", r[0]) if r and r[0] else None
    except Exception: return None


def _viacep(cep):
    """Bairro e logradouro pelo CEP (serviço público ViaCEP; só o CEP sai do Mac, nunca o CNPJ nem o nome)."""
    if not cep or len(cep) != 8: return {}
    r = subprocess.run(["curl", "-sS", "-m", "15", f"https://viacep.com.br/ws/{cep}/json/"], capture_output=True)
    try: d = json.loads(r.stdout or b"{}")
    except Exception: return {}
    return {} if d.get("erro") else d


def montar(did, teses_grupo=None):
    """Campos do formulário a partir do negócio da última venda (HubSpot), do parecer e da Receita. Devolve (campos, falta)."""
    import parecer_regras as PR
    n = _hb(did) or {}
    x = n.get("extras") or {}; cfg = json.load(open(CFG)) if os.path.exists(CFG) else {}
    d, erro = _negocio(did); falta = [erro] if erro else []
    _, p = PR.ultimo_parecer([str(did)])
    cnpj = re.sub(r"\D", "", str(d.get("cpf_cnpj") or x.get("cnpj") or "")); cnpj = cnpj.zfill(14) if 11 < len(cnpj) <= 14 else (cnpj or None)
    rf = PR.receita(cnpj)
    end, bairro, cidade, cep = _endereco(d.get("endereco"))
    cep = cep or _cep_receita(cnpj)
    if cep and not bairro:
        v = _viacep(cep); bairro = v.get("bairro") or None; cidade = cidade or v.get("localidade"); end = end or v.get("logradouro") or None
    nome = (d.get("nome_do_socio") or d.get("nome_do_contato") or "").strip()
    sob = (d.get("sobrenome") or "").strip()
    if nome and not sob and " " in nome: nome, sob = nome.split(" ", 1)
    teses = sorted({str(d.get("variante") or n.get("variante") or "")} - {"None", ""}) or list(teses_grupo or [])
    if not teses and p:  # teses do último parecer com oportunidade ou valor
        teses = [k.replace("Teses de ", "Teses de ").strip() for k, v in (p.get("teses") or {}).items() if not re.search(r"abaixo|sem recolh|aproveitad|não se enquadra", str((v or {}).get("desfecho")), re.I)]
    c = {"firstname": nome or None, "lastname": sob or None,
         "email": d.get("e_mail_do_socio") or d.get("e_mail_do_contato") or d.get("responsavel_legal___e_mail") or d.get("email_da_empresa"),
         "phone": d.get("telefone_do_socio") or d.get("numero_de_celular_do_socio") or d.get("whatsapp_do_contato") or d.get("numero_de_telefone") or d.get("numero_de_telefone_da_empresa"),
         "razao_social": d.get("razao_social") or d.get("dealname") or n.get("nome"), "cnpj": cnpj,
         "possui_debitos": d.get("possui_debitos_"), "qual_e_o_valor_da_divida": d.get("valor_do_debito"),
         "regimes_tributarios": PR.regime(p, str(did)) or d.get("qual_e_o_regime_tributario_da_empresa_") or x.get("regime"),
         "analises_a_serem_feitas": "; ".join(teses) or None, "data_de_validade_ecac": d.get("data_de_validade_ecac"),
         "setor_da_empresa": d.get("seto"), "hs_state_code": d.get("estado") or x.get("uf"), "city": cidade or x.get("cidade"),
         "bairro": bairro, "address": end, "cep": cep,
         "novo_lead_ou_cliente_da_base_": "Cliente", "id_do_parceiro": (cfg.get("parceiros") or {}).get(n.get("parceiro") or ""),
         "nome_do_gestor": cfg.get("gestor_padrao") or "Daniela Maciel", "hubspot_owner_id": DANIELA_OWNER,
         "observacoes": f"Recorrência aprovada na Central Partners (último ganho {str(n.get('fechado'))[:10]}, negócio {did})."
                        + (f" Situação na Receita: {rf['situacao']}." if rf.get("situacao") else "")}
    if rf.get("situacao") and rf["situacao"] != "Ativa" and "não encontrado" not in rf["situacao"] and "sem CNPJ" not in rf["situacao"]:
        falta.insert(0, f"BLOQUEADO: empresa {rf['situacao']} na Receita; recorrência não pode ser cadastrada (Geovana confirma)")
    if not c["id_do_parceiro"]: falta.append(f"id_do_parceiro: parceiro '{n.get('parceiro')}' fora do primeiro momento (só D&S, Empresarial Cardoso, AGILE, G.S.H, JGM, Gerson e Costa e Gaudêncio)")
    origem = {"firstname": "nome do sócio no negócio", "lastname": "sobrenome no negócio", "email": "e-mail do sócio no negócio", "phone": "telefone do sócio no negócio",
              "bairro": "endereço completo da empresa no negócio", "address": "endereço completo da empresa no negócio", "city": "endereço ou cidade no negócio",
              "setor_da_empresa": "setor da empresa no negócio", "analises_a_serem_feitas": "teses do ganho anterior ou do parecer; a Geovana indica na aprovação", "regimes_tributarios": "regime no parecer ou no negócio"}
    falta += [f"{k}: vazio ({origem.get(k, 'campo do negócio')}): quem atendeu completa no HubSpot" for k in OBRIG if not c.get(k) and k != "id_do_parceiro"]
    return {k: v for k, v in c.items() if v not in (None, "")}, sorted(set(falta), key=lambda f: (not f.startswith("BLOQUEADO"), f))


def enviar(did, confirmo=False, teses_grupo=None):
    reg = json.load(open(REG)) if os.path.exists(REG) else {}
    if str(did) in reg: return {"ok": False, "motivo": f"já enviado em {reg[str(did)]['quando']}"}
    campos, falta = montar(did, teses_grupo)
    if falta: return {"ok": False, "falta": falta, "campos": campos}
    corpo = {"fields": [{"objectTypeId": "0-1", "name": k, "value": str(v)} for k, v in campos.items()],
             "context": {"pageUri": "https://shwvx.share.hsforms.com/2cSJNCVh9QvK6sVGGwsbY4A", "pageName": "Central Partners · recorrência aprovada"}}
    if not (confirmo and os.path.exists(LIBERADO)):  # 1ª conferência do Luis antes de ligar
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
