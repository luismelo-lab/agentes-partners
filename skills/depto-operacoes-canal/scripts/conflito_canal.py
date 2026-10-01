#!/usr/bin/env python3
"""Conflito de canal por raiz de CNPJ (cálculo determinístico, somente leitura).

Agrupa os negócios ABERTOS e GANHOS do download do HubSpot pela raiz do CNPJ (8 primeiros dígitos = mesma
empresa, matriz e filiais) e lista as raízes com negócios de mais de um canal (parceiro Master, parceiro fora
do roster ou sem parceiro). Mostra quem registrou primeiro, para apoiar a regra de registro de oportunidade
(proposta, ainda não aprovada). Nada é alterado no HubSpot; decisão de conflito é do Luis.

Uso: python3 conflito_canal.py [--arquivo hubspot-AAAA-MM-DD.json] [--data AAAA-MM-DD] [--incluir-perdidos]
Saída: ~/agentes-partners/departamentos/operacoes-canal/Conflito-Canal-<data>.xlsx (+ .json de resumo)
"""
import argparse, json, os, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _comum import LINK, OUT, RS, canal, carregar, cnpj_limpo, cnpj_valido, data_ref, planilha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arquivo"); ap.add_argument("--data")
    ap.add_argument("--incluir-perdidos", action="store_true", help="também conta perdidos como 'canal' (histórico)")
    a = ap.parse_args()
    fonte, D, cfg, roster = carregar(a.arquivo)
    data = a.data or data_ref(D)
    sts = {"aberto", "ganho"} | ({"perdido"} if a.incluir_perdidos else set())
    N = [d for d in D["negocios"] if d["status"] in sts]
    todos = D["negocios"]

    sem_cnpj, apelidos = [], Counter()
    grupos = defaultdict(list)
    for d in N:
        c = cnpj_limpo(d["extras"].get("cnpj")); nome, tipo, obs = canal(d, cfg, roster)
        if d.get("parceiro_bruto") and obs.startswith("apelido"): apelidos[(d["parceiro_bruto"], nome)] += 1
        if not cnpj_valido(c):
            sem_cnpj.append([d["status"], d["nome"], d["extras"].get("cnpj"), nome, tipo, d["criado"], d["valor"], LINK.format(d["id"])]); continue
        grupos[c[:8]].append((d, c, nome, tipo, obs))

    # 1º registro histórico (inclui perdidos) por raiz × canal, para contexto
    hist = defaultdict(dict)
    for d in todos:
        c = cnpj_limpo(d["extras"].get("cnpj"))
        if not cnpj_valido(c): continue
        nome, _, _ = canal(d, cfg, roster)
        h = hist[c[:8]]
        if nome not in h or d["criado"] < h[nome]: h[nome] = d["criado"]

    conf, det = [], []
    for raiz, L in grupos.items():
        canais = sorted({x[2] for x in L})
        if len(canais) < 2: continue
        tipos = {x[2]: x[3] for x in L}
        por = defaultdict(lambda: {"aberto": 0, "ganho": 0, "perdido": 0, "valor": 0.0, "primeiro": "9999", "teses": set()})
        for d, c, nome, tipo, obs in L:
            s = por[nome]; s[d["status"]] += 1; s["valor"] += d["valor"]; s["primeiro"] = min(s["primeiro"], d["criado"])
            for t in (d.get("variante") or "").split(";"):
                if t.strip(): s["teses"].add(t.strip())
        com_ganho = [n for n in canais if por[n]["ganho"]]; com_aberto = [n for n in canais if por[n]["aberto"]]
        if len(com_ganho) >= 2: tp = "Ganho × Ganho"
        elif com_ganho and any(n not in com_ganho for n in com_aberto): tp = "Ganho × Aberto"
        else: tp = "Aberto × Aberto"
        masters = [n for n in canais if tipos[n] == "Master"]; parceiros = [n for n in canais if tipos[n] != "Sem parceiro"]
        if len(masters) >= 2: env = "Master × Master"
        elif masters and len(parceiros) >= 2: env = "Master × fora do roster"
        elif len(parceiros) >= 2: env = "Fora do roster × fora do roster"
        else: env = "Parceiro × sem parceiro"
        sev = "Alta" if (tp != "Aberto × Aberto" and len(parceiros) >= 2) else ("Média" if len(parceiros) >= 2 else "Baixa")
        primeiro = min(canais, key=lambda n: por[n]["primeiro"])
        hist_1 = min(hist[raiz].items(), key=lambda x: x[1])
        teses_sobrepostas = set.intersection(*[por[n]["teses"] for n in parceiros]) if len(parceiros) >= 2 and all(por[n]["teses"] for n in parceiros) else set()
        alias = any("a confirmar" in x[4] for x in L)
        nomes_emp = Counter(d["nome"] for d, *_ in L).most_common(1)[0][0]
        conf.append([sev, tp, env, raiz, nomes_emp, len({x[1] for x in L}), len(canais), " | ".join(canais),
                     " | ".join(f"{n}: {por[n]['ganho']}G/{por[n]['aberto']}A desde {por[n]['primeiro']}" for n in sorted(canais, key=lambda n: por[n]["primeiro"])),
                     primeiro, por[primeiro]["primeiro"], f"{hist_1[0]} ({hist_1[1]})",
                     "; ".join(sorted(teses_sobrepostas)) or ("-" if len(parceiros) >= 2 else "n/a"),
                     sum(por[n]["valor"] for n in canais if por[n]["aberto"] and n != primeiro and not por[n]["ganho"]),
                     sum(d["valor"] for d, *_ in L), "possível mesmo parceiro (apelido a confirmar)" if alias else ""])
        for d, c, nome, tipo, obs in sorted(L, key=lambda x: x[0]["criado"]):
            det.append([raiz, sev, tp, d["nome"], c, "sim" if c.endswith("0001", 0, 12) else "não", nome, tipo, d.get("parceiro_bruto"),
                        d["status"], d["etapa"], d["criado"], d.get("fechado") if d["status"] != "aberto" else None, d["valor"],
                        d.get("variante"), "sim" if nome == primeiro else "", obs, LINK.format(d["id"])])
    # ciclo (para calibrar a validade do registro de oportunidade)
    from datetime import date
    def dias(a, b): return (date.fromisoformat(b[:10]) - date.fromisoformat(a[:10])).days
    def q(v, p): v = sorted(v); return v[min(len(v) - 1, int(round(p * (len(v) - 1))))] if v else None
    cic = [dias(d["criado"], d["fechado"]) for d in todos if d["status"] == "ganho" and d.get("fechado") and d["fechado"] >= d["criado"]]
    hoje = (D.get("baixado_em") or data)[:10]
    idade = [dias(d["criado"], hoje) for d in todos if d["status"] == "aberto"]
    ciclo = {"ganhos_n": len(cic), "mediana_dias": q(cic, .5), "p75_dias": q(cic, .75), "p90_dias": q(cic, .9),
             "ganhos_ate_90d_pct": round(sum(1 for x in cic if x <= 90) / len(cic) * 100, 1) if cic else None,
             "ganhos_ate_150d_pct": round(sum(1 for x in cic if x <= 150) / len(cic) * 100, 1) if cic else None,
             "abertos_n": len(idade), "abertos_idade_mediana_dias": q(idade, .5), "abertos_mais_de_90d": sum(1 for x in idade if x > 90)}
    O = {"Alta": 0, "Média": 1, "Baixa": 2}
    conf.sort(key=lambda r: (O[r[0]], r[1], -r[14]))
    ordem = {r[3]: i for i, r in enumerate(conf)}; det.sort(key=lambda r: (ordem[r[0]], r[11]))

    R = {"data": data, "fonte": os.path.basename(fonte), "baixado_em": D.get("baixado_em"), "status_considerados": sorted(sts),
         "negocios_considerados": len(N), "sem_cnpj_valido": len(sem_cnpj), "raizes": len(grupos),
         "raizes_com_mais_de_um_canal": len(conf), "por_severidade": dict(Counter(r[0] for r in conf)),
         "por_tipo": dict(Counter(r[1] for r in conf)), "por_envolvidos": dict(Counter(r[2] for r in conf)),
         "master_x_master": sum(1 for r in conf if r[2] == "Master × Master"),
         "negocios_em_conflito": len(det), "valor_em_conflito_rs": round(sum(r[14] for r in conf), 2),
         "valor_aberto_de_quem_chegou_depois_rs": round(sum(r[13] for r in conf), 2),
         "pares_de_canais": dict(Counter(r[7] for r in conf).most_common(15)), "ciclo": ciclo}

    leia = [["Conflito de Canal por raiz de CNPJ", ""], ["Data de referência", data],
            ["Fonte", f"{R['fonte']} (baixado em {R['baixado_em']}); status considerados: {', '.join(R['status_considerados'])}"],
            ["Gerado por", "depto-operacoes-canal/scripts/conflito_canal.py (determinístico)"],
            ["Como ler", ""],
            ["Raiz do CNPJ", "8 primeiros dígitos: mesma empresa (matriz e filiais). Conflito = a mesma raiz tem negócios abertos/ganhos de 2 ou mais canais."],
            ["Canal", "Parceiro Master do roster (mapeamento-hubspot.json) · parceiro fora do roster (nome do CRM, com apelidos agrupados — aba 'Apelidos') · 'Sem parceiro identificado' (campo vazio ou numérico)."],
            ["Tipo", "Ganho × Ganho: dois canais já ganharam na mesma empresa (risco de repasse duplicado ou disputa de carteira) · Ganho × Aberto: outro canal abriu negócio em cliente já ganho · Aberto × Aberto: disputa em andamento."],
            ["Severidade (triagem)", "Alta = dois parceiros e ao menos um ganho · Média = dois parceiros só com abertos · Baixa = parceiro × sem parceiro (provável falha de cadastro, mas pode ser venda direta)."],
            ["Quem registrou primeiro", "Data de criação mais antiga entre os abertos/ganhos. É só insumo: a regra de registro ainda é PROPOSTA (Regra-Registro-e-Politica-Repasse). Teses diferentes podem justificar dois canais na mesma empresa."],
            ["Governança", "N1. A decisão sobre conflito de canal é do Luis; nada foi alterado no HubSpot e ninguém foi comunicado."]]
    resumo = [["Negócios considerados (abertos + ganhos)", R["negocios_considerados"]], ["Sem CNPJ válido (não checáveis)", R["sem_cnpj_valido"]],
              ["Raízes de CNPJ distintas", R["raizes"]], ["Raízes com mais de um canal", R["raizes_com_mais_de_um_canal"]],
              ["  Master × Master", R["master_x_master"]], ["Negócios nessas raízes", R["negocios_em_conflito"]],
              ["Valor (crédito) nessas raízes (R$)", R["valor_em_conflito_rs"]],
              ["Valor aberto de quem chegou depois, sem ganho (R$)", R["valor_aberto_de_quem_chegou_depois_rs"]], ["", ""],
              ["Ciclo dos ganhos (criação → fechamento), para calibrar a validade do registro", ""],
              ["  Mediana (dias)", ciclo["mediana_dias"]], ["  75% fecham em até (dias)", ciclo["p75_dias"]], ["  90% fecham em até (dias)", ciclo["p90_dias"]],
              ["  % dos ganhos fechados em até 90 dias", ciclo["ganhos_ate_90d_pct"]], ["  % dos ganhos fechados em até 150 dias", ciclo["ganhos_ate_150d_pct"]],
              ["  Abertos hoje: idade mediana (dias)", ciclo["abertos_idade_mediana_dias"]], ["  Abertos há mais de 90 dias", ciclo["abertos_mais_de_90d"]], ["", ""], ["Por severidade", ""]]
    resumo += [[f"  {k}", v] for k, v in sorted(R["por_severidade"].items(), key=lambda x: O[x[0]])] + [["Por tipo", ""]]
    resumo += [[f"  {k}", v] for k, v in R["por_tipo"].items()] + [["Por envolvidos", ""]]
    resumo += [[f"  {k}", v] for k, v in R["por_envolvidos"].items()] + [["Pares de canais mais frequentes", ""]]
    resumo += [[f"  {k}", v] for k, v in R["pares_de_canais"].items()]
    HC = ["Severidade", "Tipo", "Envolvidos", "Raiz CNPJ", "Empresa", "CNPJs (filiais)", "Nº canais", "Canais", "Canais: ganhos/abertos e 1º registro",
          "1º registro (abertos/ganhos)", "Data 1º registro", "1º registro histórico (inclui perdidos)", "Teses em comum entre parceiros",
          "Valor aberto de quem chegou depois (R$)", "Valor total na raiz (R$)", "Observação"]
    HD = ["Raiz CNPJ", "Severidade", "Tipo", "Negócio", "CNPJ", "Matriz?", "Canal", "Tipo de canal", "Parceiro (como está no CRM)", "Status", "Etapa",
          "Criado em", "Fechado em", "Crédito (R$)", "Tese", "1º registro?", "Obs.", "Link HubSpot"]
    arq = os.path.join(OUT, f"Conflito-Canal-{data}.xlsx")
    planilha(arq, [
        ("Leia-me", None, leia, None, None),
        ("Resumo", ["Indicador", "Valor"], resumo, {"Valor": '#,##0.##'}, {"Indicador": 60, "Valor": 40}),
        ("Conflitos", HC, conf, {"Valor aberto de quem chegou depois (R$)": RS, "Valor total na raiz (R$)": RS},
         {"Empresa": 40, "Canais": 45, "Canais: ganhos/abertos e 1º registro": 70, "Teses em comum entre parceiros": 40, "1º registro histórico (inclui perdidos)": 36, "Envolvidos": 26, "1º registro (abertos/ganhos)": 26}),
        ("Detalhe", HD, det, {"Crédito (R$)": RS}, {"Negócio": 42, "Canal": 30, "Tese": 30, "Link HubSpot": 30, "Obs.": 30}),
        ("Sem CNPJ", ["Status", "Negócio", "CNPJ no CRM", "Canal", "Tipo de canal", "Criado em", "Crédito (R$)", "Link HubSpot"], sem_cnpj, {"Crédito (R$)": RS}, {"Negócio": 42, "Link HubSpot": 30}),
        ("Apelidos", ["Como está no CRM", "Agrupado como", "Negócios"], [[k[0], k[1], v] for k, v in apelidos.most_common()], None, {"Como está no CRM": 60, "Agrupado como": 36}),
    ])
    json.dump(R, open(os.path.join(OUT, f"conflito-canal-{data}.json"), "w"), ensure_ascii=False, indent=1)
    print(arq); print(json.dumps(R, ensure_ascii=False))


if __name__ == "__main__":
    main()
