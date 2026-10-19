#!/usr/bin/env python3
"""Mapa do ecossistema sobre a base de um parceiro: quais empresas da carteira do parceiro cabem em quais produtos da Save,
por onde abrir a conversa e o que falta confirmar. Protótipo de 19/10/2026.

Reaproveita as regras de mapa_conta.py (tabela PRODUTOS, teses por segmento) e acrescenta:
  - modo prospect: a empresa ainda não é cliente, então não há parecer nem negócio no HubSpot; os sinais vêm do CSV do
    parceiro e, se existir, da base local da Receita (somente leitura);
  - produtos que não saem de dado público e dependem de resposta do dono (alongamento de dívida, home equity, captação);
  - a "porta de entrada" (primeiro produto a abrir, pela esteira Oxigenar > Estruturar > Expandir);
  - o resumo para o parceiro e a lista de dados a pedir.

Somente leitura e local. Nenhum CNPJ sai da máquina. Não lê .env. Não grava no HubSpot. Saída é rascunho para revisão.
Produto em validação, estruturação ou definição aparece só como descoberta (sem taxa, prazo ou fee).

Uso:
  python3 mapa_base_parceiro.py --csv base.csv --parceiro "Nome do parceiro" [--hubspot download.json] [--saida pasta]
Colunas do CSV: cnpj (obrigatória); opcionais: nome, cnae, regime, faturamento (R$/ano), uf, debito_fiscal (sim/nao),
vende_prazo_b2b, tem_imovel_quitado, exporta, bancos (quantidade), mes_caixa_aperta.
"""
import argparse, collections, csv, json, os, re, sqlite3, sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapa_conta as mc  # noqa: E402

PESO, ONDA = mc.PESO, mc.ONDA
SIM = lambda v: str(v or "").strip().lower() in ("sim", "s", "1", "true", "x")

# produtos que dependem de resposta do dono: (id, nome, onda, status, área, regra)
def r_alongamento(s):
    f, b = s["faturamento"] or 0, s["bancos"] or 0
    if f >= 10e6 and b >= 5:
        return ("média", f"{b} bancos e faturamento ≥ R$ 10 mi/ano: possível dívida cara e pulverizada. Falta DRE, balanço, curva ABC e SCR")

def r_home_equity(s):
    f = s["faturamento"] or 0
    if s["imovel"] and 10e6 <= f < 50e6:
        return ("baixa", "tem imóvel quitado e porte abaixo do corte do funding: alternativa a avaliar (produto sem ficha, dono ou critério)")

def r_captacao(s):
    if s["cresce_sem_capacidade"]:
        return ("média", "demanda acima da capacidade e necessidade de capital de expansão: dívida, equity ou sócio estratégico")

def r_ci_extra(s):
    f = s["faturamento"] or 0
    if s["imovel"] and f >= 50e6 and (s["exporta"] or s["setor"] in ("Proteína animal", "Café e grãos")):
        return ("média", "porte e ativo relevante: confirmar garantia livre (~2x) e necessidade (≥ US$ 5 mi) antes de qualquer conversa")

EXTRA = [
    ("ALONG", "Alongamento e carência de dívida bancária", 2, "em definição", "depto-internacional (ecossistema)", r_alongamento),
    ("HE", "Home equity", 3, "em definição", "depto-internacional (ecossistema)", r_home_equity),
    ("CAP", "Captação de capital (dívida, equity, sócio)", 3, "em definição", "depto-internacional (ecossistema)", r_captacao),
]
ABERTURA = {  # pergunta de abertura por produto (linguagem de caixa, sem oferta)
    "RT": "Há anos em que sua empresa pagou PIS/COFINS sobre compras que não geram débito? Posso olhar suas notas e dizer, sem custo, se há crédito.",
    "GC": "Quanto da sua carteira a receber está vencida hoje? E em que mês do ano o seu caixa aperta mais?",
    "PAS": "Hoje você consegue emitir certidão negativa quando o banco ou um cliente pede?",
    "JUR": "Há algum débito ou auto de infração com prazo correndo?",
    "PLAN": "Você já simulou como a reforma de 2027 muda a sua margem, produto por produto?",
    "EP": "A empresa e o patrimônio da família estão estruturados para sucessão e proteção?",
    "ANT": "Você antecipa recebíveis? A que custo e com quantos bancos?",
    "FIDC": "Quanto sua empresa paga a bancos para antecipar recebíveis dos seus clientes ou fornecedores?",
    "CI": "Existe ativo livre (terra, imóvel, planta) e um projeto de uso que justifique uma captação de longo prazo?",
    "MQ": "A sua fábrica tem mais custo de mão de obra e energia do que o produto suporta?",
    "ALONG": "Quantos bancos você tem e quanto paga de parcelas por mês? Uma carência mudaria o seu ano?",
    "HE": "Há imóvel quitado que poderia sustentar capital mais barato?",
    "CAP": "A demanda é maior do que a sua capacidade? Como você pretende financiar a expansão?",
}
RECEITA_PORTE = {"01": "Não informado", "03": "ME", "05": "Demais (acima de R$ 4,8 mi)"}


def num(v):
    try: return float(str(v).replace(".", "").replace(",", ".")) if "," in str(v) else float(v)
    except Exception: return None


def abrir_receita():
    p = os.path.join(mc.AP, "dados-publicos/receita/cnpj.sqlite")
    return sqlite3.connect("file:" + p + "?mode=ro", uri=True) if os.path.exists(p) else None


def sinais_prospect(row, db):
    c = re.sub(r"\D", "", row.get("cnpj", "")).zfill(14)
    est = db.execute("select cnae, situacao, uf from estab where cnpj=?", (c,)).fetchone() if db else None
    emp = db.execute("select capital, porte, razao from empresa where basico=?", (c[:8],)).fetchone() if db else None
    cnae = (row.get("cnae") or (est[0] if est else "") or "").replace("-", "").replace("/", "").replace(".", "")
    f = num(row.get("faturamento"))
    estimado = False
    if not f and emp and str(emp[1]) == "05":
        f, estimado = 4.8e6, True  # "Demais": piso do porte, não é o faturamento
    s = {"cnpj": c, "nome": row.get("nome") or (emp[2] if emp else c), "cnae": cnae, "setor": mc.setor(cnae), "uf": row.get("uf") or (est[2] if est else ""),
         "situacao": est[1] if est else "", "regime": row.get("regime") or None, "faturamento": f, "faixa": None, "capital": emp[0] if emp else None,
         "porte_receita": emp[1] if emp else None, "master": None, "masters": [], "rt_ganho": False, "rt_ganhos": 0, "rt_valor": 0,
         "rt_recebido": None, "ultimo_ganho": None, "honorario_contratado": [], "link_negocio": "", "duplicidade_suspeita": [], "teses": {},
         "passivo_debitos": SIM(row.get("debito_fiscal")), "passivo_suspenso": False, "passivo_txt": "", "acao_judicial": False,
         "competencias_novas": None, "ja_tem": {}, "negocios": [], "bancos": int(num(row.get("bancos")) or 0), "imovel": SIM(row.get("tem_imovel_quitado")),
         "exporta": SIM(row.get("exporta")), "b2b": SIM(row.get("vende_prazo_b2b")), "mes_caixa": row.get("mes_caixa_aperta") or "",
         "cresce_sem_capacidade": SIM(row.get("cresce_sem_capacidade")), "fat_estimado": estimado}
    return s


def mapear(s, ja_hubspot):
    # resposta do dono sobre venda a prazo B2B fecha a lacuna de faturamento desconhecido na Gestão de Contas
    m = mc.mapa(s)
    ops = [o for o in m["oportunidades"]]
    for pid, nome, onda, status, area, regra in EXTRA:
        x = regra(s)
        if x: ops.append({"id": pid, "produto": nome, "aderencia": x[0], "motivo": x[1], "onda": ONDA[onda], "status": status, "area": area})
    if s["b2b"] and not any(o["id"] == "GC" for o in ops):
        ops.append({"id": "GC", "produto": "Gestão de Contas (cobrança com IA)", "aderencia": "média", "motivo": "o dono confirma venda a prazo a empresas (B2B); faltam carteira e vencidos",
                    "onda": ONDA[1], "status": "em definição", "area": "depto-internacional (ecossistema)"})
    ops = [o for o in ops if o["aderencia"] in PESO]
    ops.sort(key=lambda o: (o["onda"], -PESO[o["aderencia"]]))
    cand = [o for o in ops if PESO[o["aderencia"]] >= 2]
    pronto = [o for o in cand if o["status"] == "pronto"]
    if pronto: entrada = {**pronto[0], "modo": "proposta (produto pronto)"}
    elif cand: entrada = {**cand[0], "modo": "descoberta (sem taxa, prazo ou fee)"}
    else: entrada = None
    # quem ainda não abre e-CAC, DRE e balanço entra pela dor de caixa (reunião de 13/10): cobrança primeiro
    alt = next((o for o in ops if o["id"] == "GC" and PESO[o["aderencia"]] >= 2), None)
    if entrada and entrada["id"] != "GC" and alt: entrada["se_nao_abrir_dados"] = "Gestão de Contas (cobrança com IA, pago no êxito)"
    falta = []
    if not s["faturamento"] or s["fat_estimado"]: falta.append("faturamento real")
    if not s["regime"]: falta.append("regime tributário")
    if not s["cnae"]: falta.append("CNAE")
    falta += ["EFD-Contribuições e notas (confirmam a tese)"] if any(o["id"] == "RT" for o in ops) else []
    if any(o["id"] in ("ALONG", "FIDC", "CI") for o in ops): falta.append("DRE, balanço e SCR")
    alertas = list(ja_hubspot)
    if s["situacao"] and str(s["situacao"]) not in ("02", "2", "ativa", "ATIVA"): alertas.append(f"situação cadastral {s['situacao']}: conferir")
    return {"cnpj": s["cnpj"], "nome": s["nome"], "setor": s["setor"], "cnae": s["cnae"], "uf": s["uf"], "regime": s["regime"], "faturamento": s["faturamento"],
            "faturamento_estimado": s["fat_estimado"], "oportunidades": ops, "indice": sum(PESO[o["aderencia"]] for o in ops),
            "entrada": entrada, "abertura": ABERTURA.get(entrada["id"]) if entrada else None, "mes_caixa": s["mes_caixa"], "falta": falta, "alertas": alertas}


def conflitos(hub_json):
    if not hub_json: return {}
    neg = json.load(open(hub_json))["negocios"]
    out = collections.defaultdict(list)
    for n in neg:
        c = mc.cnpj_de(n)
        if c: out[c[:8]].append(f"{n.get('status')} no funil {n.get('pipeline')} (parceiro: {n.get('parceiro') or 'sem parceiro'})")
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--csv", required=True); ap.add_argument("--parceiro", default="Parceiro")
    ap.add_argument("--hubspot"); ap.add_argument("--saida", default=os.path.join(mc.OUT, "base-parceiros"))
    a = ap.parse_args()
    db, cf = abrir_receita(), conflitos(a.hubspot)
    rows = list(csv.DictReader(open(a.csv, encoding="utf-8-sig")))
    res = []
    for r in rows:
        s = sinais_prospect(r, db)
        ja = [f"já aparece no HubSpot: {x}" for x in cf.get(s["cnpj"][:8], [])]
        res.append(mapear(s, ja))
    res.sort(key=lambda m: (-(m["indice"]), m["nome"]))
    cont = collections.Counter(o["id"] for m in res for o in m["oportunidades"] if PESO[o["aderencia"]] >= 2)
    entradas = collections.Counter(m["entrada"]["id"] for m in res if m["entrada"])
    resumo = {"parceiro": a.parceiro, "gerado": date.today().isoformat(), "empresas": len(res), "com_entrada": sum(1 for m in res if m["entrada"]),
              "oportunidades_alta_media_por_produto": dict(cont.most_common()), "porta_de_entrada": dict(entradas.most_common()),
              "pedir_ao_parceiro": dict(collections.Counter(f for m in res for f in m["falta"]).most_common()),
              "fonte_receita": bool(db), "fonte_hubspot": a.hubspot or None}
    os.makedirs(a.saida, exist_ok=True)
    nome = re.sub(r"\W+", "-", a.parceiro.lower()).strip("-")
    json.dump({"resumo": resumo, "empresas": res}, open(os.path.join(a.saida, f"{nome}-{date.today()}.json"), "w"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(resumo, ensure_ascii=False, indent=1))
    for m in res:
        e = m["entrada"]
        print(f"- {m['nome']} ({m['setor']}, {m['regime'] or 'regime ?'}): " + (f"entra por {e['produto']} [{e['modo']}]" if e else "sem aderência com os dados atuais; aplicar o questionário"))


if __name__ == "__main__":
    main()
