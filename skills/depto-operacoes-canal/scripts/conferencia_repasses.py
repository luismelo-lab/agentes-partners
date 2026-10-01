#!/usr/bin/env python3
"""Conferência de repasses a parceiros (cálculo determinístico, somente leitura).

Para cada negócio GANHO do download do HubSpot: honorário contratado (valor do crédito × % honorário),
% e valor do parceiro (honorário × % parceiro), campos vazios, outliers, inconsistências entre campos
e resumo por parceiro. Nada é pago, enviado ou alterado: é uma lista de conferência para o Financeiro/CRM.

Uso: python3 conferencia_repasses.py [--arquivo hubspot-AAAA-MM-DD.json] [--data AAAA-MM-DD]
Saída: ~/agentes-partners/departamentos/operacoes-canal/Conferencia-Repasses-<data>.xlsx (+ .json de resumo)
"""
import argparse, json, os, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _comum import (LINK, OUT, PCT, RS, canal, carregar, cnpj_limpo, cnpj_valido, data_ref, planilha)

# código: (severidade, bloqueia o cálculo do repasse?, descrição, ação sugerida, dono)
REGRAS = {
    "C01": ("Alto", True, "% de honorário vazio: honorário e repasse não calculáveis", "Preencher honorarios_contratuais conforme contrato", "CRM / Contratos"),
    "C02": ("Alto", True, "% do parceiro vazio em negócio com parceiro: repasse não calculável", "Preencher honorarios_parceiro conforme termo de parceria", "CRM / Luis"),
    "C03": ("Médio", False, "% do parceiro vazio em negócio sem parceiro identificado", "Confirmar que não há repasse (venda direta)", "CRM"),
    "C04": ("Médio", False, "CNPJ vazio ou inválido (dígito verificador)", "Corrigir o CNPJ: sem ele não há registro nem checagem de conflito", "CRM"),
    "C05": ("Médio", False, "Ganho sem data de fechamento", "Preencher closedate", "CRM"),
    "O01": ("Alto", False, "% de honorário acima do limite (50% do crédito)", "Conferir no contrato; ver hipótese", "Contratos / CRM"),
    "O02": ("Alto", False, "% de honorário = 0 em negócio ganho", "Conferir contrato (êxito zero?) ou corrigir", "Contratos / CRM"),
    "O03": ("Crítico", True, "% do parceiro acima de 100%: repasse maior que o honorário", "Corrigir antes de qualquer pagamento", "CRM / Financeiro"),
    "O04": ("Médio", False, "% do parceiro acima do teto usual (50%)", "Confirmar no termo de parceria", "Luis"),
    "O05": ("Alto", True, "Valor do crédito zero ou negativo em negócio ganho", "Corrigir o valor do negócio", "CRM"),
    "O06": ("Médio", False, "Valor do crédito acima de R$ 50 mi", "Confirmar o valor no parecer/contrato", "CRM / Técnico"),
    "O07": ("Crítico", True, "Outra comissão (vendedor/gestor/indicador/coordenador) acima de 100%", "Corrigir o campo (provável digitação: 125 em vez de 12,5 ou 1,25)", "CRM"),
    "O08": ("Alto", True, "% do parceiro exatamente 1 (ambíguo: 1% ou 100%?)", "Confirmar e regravar em formato único", "CRM"),
    "I01": ("Alto", False, "Soma das comissões (parceiro + vendedor + gestor + indicador + coordenador) acima de 100% do honorário", "Confirmar a base de cada comissão", "Luis / Financeiro"),
    "I02": ("Médio", False, "Parceiro Master com % do parceiro = 0", "Confirmar se o negócio não gera repasse", "Luis"),
    "I03": ("Alto", True, "% do parceiro > 0 sem parceiro identificado: a quem pagar?", "Preencher nome_do_parceiro", "CRM"),
    "I04": ("Médio", False, "Nome do parceiro com valor numérico (campo trocado?)", "Corrigir nome_do_parceiro", "CRM"),
    "I05": ("Alto", False, "Possível duplicidade: mesmo CNPJ e mesmo valor em mais de um ganho", "Confirmar se é o mesmo crédito (risco de repasse em dobro)", "CRM / Financeiro"),
    "I06": ("Médio", False, "% indicador e % parceiro preenchidos ao mesmo tempo", "Confirmar se indicador = parceiro (risco de pagar duas vezes)", "Luis"),
}
ORD = {"Crítico": 0, "Alto": 1, "Médio": 2}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arquivo"); ap.add_argument("--data")
    a = ap.parse_args()
    fonte, D, cfg, roster = carregar(a.arquivo)
    L = cfg["limites"]; data = a.data or data_ref(D)
    G = [d for d in D["negocios"] if d["status"] == "ganho"]

    # duplicidade: mesmo CNPJ + mesmo valor (inteiro)
    chave = Counter((cnpj_limpo(d["extras"].get("cnpj")), round(d["valor"])) for d in G if d["valor"] > 0 and cnpj_limpo(d["extras"].get("cnpj")))

    linhas, probs = [], []
    for d in G:
        ex = d["extras"]; oc = d.get("outras_comissoes") or {}
        c = cnpj_limpo(ex.get("cnpj")); nome_canal, tipo, obs_canal = canal(d, cfg, roster)
        hC, hP, v = d["hContr"], d["hParc"], d["valor"]
        cod = []
        if hC is None: cod.append("C01")
        if hP is None: cod.append("C02" if tipo != "Sem parceiro" else "C03")
        if not cnpj_valido(c): cod.append("C04")
        if not d.get("fechado"): cod.append("C05")
        if hC is not None and hC > L["honorario_pct_max"]: cod.append("O01")
        if hC == 0: cod.append("O02")
        if hP is not None and hP > 1: cod.append("O03")
        elif hP is not None and hP > L["parceiro_pct_teto_usual"] and hP != 1: cod.append("O04")
        if v <= 0: cod.append("O05")
        if v > L["valor_credito_alto_rs"]: cod.append("O06")
        if any((x or 0) > 1 for x in oc.values()): cod.append("O07")
        if hP == 1: cod.append("O08")
        soma = (hP or 0) + sum((x or 0) for x in oc.values())
        if soma > L["soma_comissoes_max"] + L["tolerancia_soma_1"]: cod.append("I01")
        if tipo == "Master" and hP == 0: cod.append("I02")
        if tipo == "Sem parceiro" and (hP or 0) > 0: cod.append("I03")
        if "numérico" in obs_canal: cod.append("I04")
        if c and v > 0 and chave[(c, round(v))] > 1: cod.append("I05")
        if (oc.get("indicador_pct") or 0) > 0 and (hP or 0) > 0: cod.append("I06")

        hip = []
        if "O01" in cod and hP is not None and abs(hC + hP - 1) <= 0.03:
            hip.append(f"% honorário ({hC:.0%}) + % parceiro ({hP:.0%}) ≈ 100%: provável inversão — o campo de honorário parece guardar a PARTE DA SAVE, não o % sobre o crédito")
        if "O03" in cod or "O07" in cod:
            hip.append("valor gravado como 125 (→1,25): conferir se era 12,5% ou 1,25%")
        honor = v * hC if hC is not None else None
        repasse = honor * hP if (honor is not None and hP is not None) else None
        bloq = any(REGRAS[k][1] for k in cod)
        sev = min((REGRAS[k][0] for k in cod), key=ORD.get) if cod else ""
        status = "Bloqueado" if bloq else ("Revisar" if cod else "OK (aguarda dado de pagamento)")
        vazios = [n for n, x in (("% honorário", hC), ("% parceiro", hP), ("CNPJ", c), ("tese", d.get("variante")),
                                 ("data fechamento", d.get("fechado")), ("valor recebido", d.get("recebido"))) if x in (None, "")]
        linhas.append([status, sev, len(cod), "; ".join(cod), d["nome"], c or ex.get("cnpj"), nome_canal, tipo, d.get("parceiro_bruto"),
                       d.get("owner"), d.get("fechado"), d.get("variante"), v, hC, honor, hP, repasse,
                       oc.get("vendedor_pct"), oc.get("gestor_comercial_pct"), oc.get("indicador_pct"), oc.get("coordenador_pct"),
                       soma if (hP is not None or any(x is not None for x in oc.values())) else None,
                       d.get("recebido"), ", ".join(vazios), " | ".join(hip), obs_canal, LINK.format(d["id"]), d["id"]])
        for k in cod:
            s, b, desc, acao, dono = REGRAS[k]
            probs.append([s, k, desc, "sim" if b else "não", d["nome"], nome_canal, d.get("fechado"), v, hC, hP, acao, dono,
                          " | ".join(hip), LINK.format(d["id"])])
    linhas.sort(key=lambda r: ({"Bloqueado": 0, "Revisar": 1}.get(r[0], 2), ORD.get(r[1], 3), -(r[12] or 0)))
    probs.sort(key=lambda r: (ORD[r[0]], r[1], -(r[7] or 0)))

    # ---------- resumo por parceiro ----------
    P = defaultdict(lambda: Counter())
    for r in linhas:
        s = P[(r[6], r[7])]; s["n"] += 1; s["credito"] += r[12] or 0
        if r[14] is not None: s["com_hon"] += 1; s["honor"] += r[14]
        if r[15] is not None: s["com_parc"] += 1; s["soma_pct"] += r[15]
        if r[16] is not None: s["calc"] += 1; s["repasse"] += r[16]
        if r[0] == "Bloqueado": s["bloq"] += 1; s["credito_bloq"] += r[12] or 0
        elif r[0] == "Revisar": s["rev"] += 1
        else: s["ok"] += 1
    por = []
    for (nome, tipo), s in sorted(P.items(), key=lambda x: -x[1]["credito"]):
        por.append([nome, tipo, s["n"], s["credito"], s["com_hon"] / s["n"], s["com_parc"] / s["n"], s["calc"], s["honor"],
                    (s["soma_pct"] / s["com_parc"]) if s["com_parc"] else None, s["repasse"], s["ok"], s["rev"], s["bloq"], s["credito_bloq"]])

    cont = Counter(p[1] for p in probs); st = Counter(r[0] for r in linhas)
    calc = [r for r in linhas if r[16] is not None]
    calc_ok = [r for r in linhas if r[16] is not None and r[0] != "Bloqueado"]
    R = {"data": data, "fonte": os.path.basename(fonte), "baixado_em": D.get("baixado_em"), "ganhos": len(G),
         "status": dict(st), "com_algum_problema": st["Bloqueado"] + st["Revisar"],
         "problemas_por_codigo": {k: cont.get(k, 0) for k in REGRAS},
         "honorario_pct_preenchido": sum(1 for d in G if d["hContr"] is not None),
         "parceiro_pct_preenchido": sum(1 for d in G if d["hParc"] is not None),
         "recebido_preenchido": sum(1 for d in G if d.get("recebido") not in (None, "")),
         "repasse_calculavel_n": len(calc), "repasse_calculado_rs": round(sum(r[16] for r in calc), 2),
         "repasse_calculado_sem_bloqueio_rs": round(sum(r[16] for r in calc_ok), 2),
         "honorario_contratado_calculavel_rs": round(sum(r[14] for r in linhas if r[14] is not None), 2),
         "credito_bloqueado_rs": round(sum(r[12] for r in linhas if r[0] == "Bloqueado"), 2),
         "repasse_so_ok_rs": round(sum(r[16] for r in calc if r[0].startswith("OK")), 2),
         "hipotese_inversao_n": sum(1 for r in linhas if "inversão" in (r[24] or "")),
         "duplicidade_grupos": sum(1 for k, n in chave.items() if n > 1),
         "duplicidade_credito_em_excesso_rs": round(sum(k[1] * (n - 1) for k, n in chave.items() if n > 1), 2),
         "limites": L, "versao_config": cfg.get("versao")}

    # ---------- planilha ----------
    leia = [
        ["Conferência de Repasses a Parceiros", ""],
        ["Data de referência", data], ["Fonte", f"{R['fonte']} (baixado em {R['baixado_em']}), negócios GANHOS do escopo Área Master"],
        ["Gerado por", "depto-operacoes-canal/scripts/conferencia_repasses.py (determinístico; nenhum número foi digitado à mão)"],
        ["O que é", ""],
        ["Honorário contratado (R$)", "valor do crédito × % honorário (honorarios_contratuais). É POTENCIAL: não é honorário recebido."],
        ["Repasse calculado (R$)", "honorário contratado × % do parceiro (honorarios_parceiro). É o que o CRM diz que seria devido, NÃO um valor a pagar."],
        ["Status", "Bloqueado = não dá para calcular o repasse com segurança · Revisar = calculável, mas com ponto a confirmar · OK = sem achado (ainda depende do dado de pagamento)."],
        ["Avisos", ""],
        ["Pagamento", f"Valor recebido preenchido em {R['recebido_preenchido']} de {R['ganhos']} ganhos. Sem dado de caixa, nenhuma linha pode ser conferida contra o que o cliente pagou nem contra o que o parceiro já recebeu."],
        ["Base das outras comissões", "honorarios_vendedor / gestor_comercial / indicador / coordenador: a base (% do honorário? do crédito?) e se descontam do parceiro NÃO estão confirmadas. A soma I01 assume a mesma base do % do parceiro."],
        ["Escala dos percentuais", "O download converte valores > 1 dividindo por 100 (30 → 30%). Por isso '1' é ambíguo (O08) e '125' vira 125% (O03/O07)."],
        ["Limites de triagem", f"honorário > {L['honorario_pct_max']:.0%} · parceiro > {L['parceiro_pct_teto_usual']:.0%} · crédito > R$ {L['valor_credito_alto_rs']:,.0f} (config {cfg.get('versao')}). São alertas, não regra de pagamento."],
        ["Governança", "N1: rascunho para o Luis, o CRM e o Financeiro. Nada foi pago, enviado ou alterado no HubSpot. Correções são feitas pelo time de CRM (D18)."],
    ]
    resumo = [["Negócios ganhos", R["ganhos"]], ["Com algum problema", R["com_algum_problema"]],
              ["  Bloqueados", st["Bloqueado"]], ["  Revisar", st["Revisar"]], ["  OK (aguarda pagamento)", st["OK (aguarda dado de pagamento)"]],
              ["% honorário preenchido", R["honorario_pct_preenchido"]], ["% parceiro preenchido", R["parceiro_pct_preenchido"]],
              ["Valor recebido preenchido", R["recebido_preenchido"]], ["Repasse calculável (negócios)", R["repasse_calculavel_n"]],
              ["Honorário contratado calculável (R$)", R["honorario_contratado_calculavel_rs"]],
              ["Repasse calculado — todos os calculáveis (R$)", R["repasse_calculado_rs"]],
              ["Repasse calculado — sem os bloqueados (R$)", R["repasse_calculado_sem_bloqueio_rs"]],
              ["Repasse calculado — só as linhas OK (R$)", R["repasse_so_ok_rs"]],
              ["Crédito dos negócios bloqueados (R$)", R["credito_bloqueado_rs"]],
              ["Possíveis duplicidades (grupos de mesmo CNPJ + mesmo valor)", R["duplicidade_grupos"]],
              ["Crédito em excesso se as duplicidades se confirmarem (R$)", R["duplicidade_credito_em_excesso_rs"]],
              ["Provável inversão honorário × parte da Save", R["hipotese_inversao_n"]], ["", ""], ["Problema (código)", "Negócios"]]
    resumo += [[f"{k} · {REGRAS[k][0]} · {REGRAS[k][2]}", cont.get(k, 0)] for k in REGRAS]

    H = ["Status", "Severidade", "Nº problemas", "Códigos", "Negócio", "CNPJ", "Parceiro (canônico)", "Tipo de canal", "Parceiro (como está no CRM)",
         "Owner", "Fechado em", "Tese", "Crédito (R$)", "% honorário", "Honorário contratado (R$)", "% parceiro", "Repasse calculado (R$)",
         "% vendedor", "% gestor comercial", "% indicador", "% coordenador", "Soma % comissões", "Recebido (R$)", "Campos vazios",
         "Hipótese", "Obs. canal", "Link HubSpot", "ID"]
    F = {h: RS for h in ("Crédito (R$)", "Honorário contratado (R$)", "Repasse calculado (R$)", "Recebido (R$)")}
    F.update({h: PCT for h in ("% honorário", "% parceiro", "% vendedor", "% gestor comercial", "% indicador", "% coordenador", "Soma % comissões")})
    W = {"Negócio": 42, "Códigos": 18, "Tese": 30, "Campos vazios": 30, "Hipótese": 60, "Obs. canal": 30, "Link HubSpot": 30, "Parceiro (canônico)": 24, "Parceiro (como está no CRM)": 24}
    HP = ["Severidade", "Código", "Problema", "Bloqueia cálculo?", "Negócio", "Parceiro", "Fechado em", "Crédito (R$)", "% honorário", "% parceiro",
          "Ação sugerida", "Dono da correção", "Hipótese", "Link HubSpot"]
    HR = ["Parceiro", "Tipo de canal", "Ganhos", "Crédito (R$)", "% com honorário", "% com % parceiro", "Repasse calculável (n)",
          "Honorário contratado calculável (R$)", "% parceiro médio", "Repasse calculado (R$)", "OK", "Revisar", "Bloqueados", "Crédito bloqueado (R$)"]
    FR = {h: RS for h in ("Crédito (R$)", "Honorário contratado calculável (R$)", "Repasse calculado (R$)", "Crédito bloqueado (R$)")}
    FR.update({h: PCT for h in ("% com honorário", "% com % parceiro", "% parceiro médio")})
    regras = [[k, s, "sim" if b else "não", desc, acao, dono] for k, (s, b, desc, acao, dono) in REGRAS.items()]
    arq = os.path.join(OUT, f"Conferencia-Repasses-{data}.xlsx")
    planilha(arq, [
        ("Leia-me", None, leia, None, None),
        ("Resumo", ["Indicador", "Valor"], resumo, {"Valor": '#,##0.##'}, {"Indicador": 70, "Valor": 22}),
        ("Por parceiro", HR, por, FR, {"Parceiro": 32}),
        ("Conferência", H, linhas, F, W),
        ("Problemas", HP, probs, {"Crédito (R$)": RS, "% honorário": PCT, "% parceiro": PCT}, {"Problema": 55, "Negócio": 42, "Ação sugerida": 45, "Hipótese": 60, "Link HubSpot": 30}),
        ("Regras", ["Código", "Severidade", "Bloqueia cálculo?", "Problema", "Ação sugerida", "Dono"], regras, None, {"Problema": 70, "Ação sugerida": 55}),
    ])
    json.dump({**R, "por_parceiro": [dict(zip(HR, x)) for x in por]}, open(os.path.join(OUT, f"conferencia-repasses-{data}.json"), "w"), ensure_ascii=False, indent=1, default=str)
    print(arq)
    print(json.dumps({k: R[k] for k in ("ganhos", "status", "com_algum_problema", "problemas_por_codigo", "repasse_calculavel_n",
                                        "repasse_calculado_rs", "repasse_calculado_sem_bloqueio_rs", "repasse_so_ok_rs", "hipotese_inversao_n", "duplicidade_grupos", "duplicidade_credito_em_excesso_rs", "recebido_preenchido")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
