"""Projeto Maquila · portfólio da Save e ataque à base (Intel Comercial + Dados + Gabinete, 02/10/2026).

Somente leitura e local: download do HubSpot, base da Receita (SQLite local, read-only) e o faturamento já
estimado pela frente de crédito internacional (base_clientes.py). Não lê .env, não chama API, não traz sócios nem CPF.
Uso:  python3 base_maquila.py   -> planilha nominal (OneDrive + cópia local) e JSON agregado (sem nomes)
"""
import collections, json, os, pickle, re, shutil, sqlite3, statistics as st, subprocess, sys
from datetime import date

AP = os.path.expanduser("~/agentes-partners")
sys.path.insert(0, os.path.join(AP, "lib"))
sys.path.insert(0, os.path.join(AP, "departamentos/produtos/credito-internacional/scripts"))
import partners_dados as PD

PASTA = os.path.join(AP, "departamentos/produtos/maquila")
CACHE = os.environ.get("MAQUILA_CACHE")  # opcional: pickle do montar() para iterar rápido

# ---------- setores industriais (CNAE 2.3, prefixo mais longo vence) ----------
# nível 3 = núcleo Maquila (intensivo em mão de obra/energia, montagem) · 2 = boa aderência · 1 = indústria com aderência menor
SETORES = [
    ("Têxtil", 3, ["13"]),
    ("Confecção e vestuário", 3, ["14"]),
    ("Couro e calçados", 3, ["15"]),
    ("Plásticos e borracha", 3, ["22"]),
    ("Embalagens", 3, ["1731", "1732", "1733", "2222", "2312", "2591"]),
    ("Autopeças", 3, ["294", "2950"]),
    ("Eletroeletrônicos e montagem", 3, ["26", "27"]),
    ("Móveis", 3, ["31"]),
    ("Metalmecânica (produtos de metal)", 2, ["25"]),
    ("Metalurgia", 2, ["24"]),
    ("Máquinas e equipamentos (fabricação)", 2, ["28"]),
    ("Veículos e carrocerias", 2, ["29", "30"]),
    ("Frigoríficos e produtos de carne", 2, ["1011", "1012", "1013"]),
    ("Alimentos processados", 1, ["10"]),
    ("Bebidas", 1, ["11"]),
    ("Produtos diversos (brinquedos, artigos esportivos, médicos)", 2, ["32"]),
    ("Madeira, papel e gráfica", 1, ["16", "17", "18"]),
    ("Química, farmacêutica e minerais não metálicos", 1, ["19", "20", "21", "23"]),
    ("Manutenção e instalação industrial", 1, ["33"]),
]
# comércio de bens manufaturados: pode virar cliente de maquila (contratar a industrialização), mas não é indústria hoje
ADJ_COMERCIO = ("4641", "4642", "4643", "4644", "4645", "4646", "4647", "4649", "465", "466", "467", "4686", "4687", "4689")
EXPORT_CNAE_IND = ("1011", "1012", "1013", "1041", "1061", "1064", "1071", "1081", "15", "1311", "1312", "2941", "2949")
UF_PTS = {"PR": 15, "MS": 15, "SC": 13, "RS": 13, "SP": 12, "GO": 10, "MG": 10, "MT": 8, "DF": 6}
RECEITA_COMPLETA = ["1011", "1012", "1013", "1031", "1033", "1051", "1052", "1053", "1091"]   # CNAEs industriais carregados por inteiro
PROSPECT_CNAE = ("1011", "1012", "1013", "1031", "1033", "1051", "1052")                      # os que têm aderência ao Maquila


def setor_ind(cnae):
    c = re.sub(r"\D", "", cnae or "")
    best = None
    for s, n, prefs in SETORES:
        for p in prefs:
            if c.startswith(p) and (best is None or len(p) > best[2]): best = (s, n, len(p))
    return (best[0], best[1]) if best else (None, 0)


# ---------- produtos já comprados (pipelines e teses do HubSpot) ----------
def familia_tese(t):
    n = PD.norm(t)
    if "verbas" in n or "rat" in n.split() or "dsr" in n: return "Previdenciário (verbas/RAT)"
    if "sistema s" in n: return "Sistema S (MS coletivo)"
    if "diesel" in n: return "Crédito diesel/GLP (LC 192/2022)"
    if "icms" in n or "difal" in n or "iss" in n: return "Exclusões da base (ICMS/ICMS-ST/DIFAL/ISS)"
    if "propria base" in n or "irpj" in n or "receitas financeiras" in n or "subvencao" in n or "gross" in n: return "Teses judiciais (própria base, IRPJ/CSLL, subvenção)"
    if "insumos" in n: return "PIS/COFINS insumos"
    if "aquisi" in n or "acumulado" in n or "monof" in n: return "PIS/COFINS nas aquisições"
    return "Outras teses"


PIPE_PROD = {"RT - Real & Presumido": "Recuperação tributária (Real/Presumido)", "RT - Simples Nacional": "Recuperação tributária (Simples)",
             "Gestão de Passivo": "Gestão de passivo", "Planejamento Tributário": "Planejamento tributário", "Produtos Jurídicos": "Produtos jurídicos"}


def portfolio(H):
    """Contagens por pipeline e por tese. Valor = crédito/valor do negócio; deduplicado por (raiz, valor) por causa da importação do Bitrix."""
    negs = H["negocios"]
    out = {}
    for p in sorted({d["pipeline"] for d in negs}):
        ds = [d for d in negs if d["pipeline"] == p]
        g = [d for d in ds if d["status"] == "ganho"]
        a = [d for d in ds if d["status"] == "aberto"]
        uniq = {(PD.raiz(d["extras"].get("cnpj")) or d["id"], int(d["valor"] or 0)) for d in g if (d["valor"] or 0) > 0}
        vals = [v for _, v in uniq]
        hc = [d["hContr"] for d in g if d["hContr"]]
        out[p] = dict(negocios=len(ds), ganhos=len(g), abertos=len(a), perdidos=sum(d["status"] == "perdido" for d in ds),
                      empresas_ganhas=len({PD.raiz(d["extras"].get("cnpj")) for d in g if PD.raiz(d["extras"].get("cnpj"))}),
                      valor_mediano_ganho=st.median(vals) if vals else None, valor_total_ganho_dedup=sum(vals), valor_total_sem_acima_50mi=sum(v for v in vals if v <= 50e6), n_acima_50mi=sum(v > 50e6 for v in vals),
                      valor_p90=sorted(vals)[int(.9 * (len(vals) - 1))] if vals else None,
                      valor_mediano_aberto=st.median([d["valor"] for d in a if d["valor"]]) if any(d["valor"] for d in a) else None,
                      honor_mediano=st.median(hc) if hc else None, n_honor=len(hc),
                      conversao=round(len(g) / max(1, len(g) + sum(d["status"] == "perdido" for d in ds)), 3))
    teses = collections.defaultdict(lambda: dict(negocios=0, ganhos=0, vals=set(), empresas=set()))
    for d in negs:
        fams = {familia_tese(t) for t in (d["variante"] or "").split(";") if t.strip()}
        for f in fams:
            T = teses[f]; T["negocios"] += 1
            if d["status"] == "ganho":
                T["ganhos"] += 1
                r = PD.raiz(d["extras"].get("cnpj"))
                if r: T["empresas"].add(r)
                if (d["valor"] or 0) > 0: T["vals"].add((r or d["id"], int(d["valor"])))
    tes = {f: dict(negocios=T["negocios"], ganhos=T["ganhos"], empresas_ganhas=len(T["empresas"]),
                   valor_mediano_ganho=st.median([v for _, v in T["vals"]]) if T["vals"] else None) for f, T in teses.items()}
    return out, tes, sum(1 for d in negs if d["variante"])


def montar_base():
    if CACHE and os.path.exists(CACHE):
        L, M = pickle.load(open(CACHE, "rb"))
    else:
        import base_clientes as BC
        L, M = BC.montar()
        if CACHE: pickle.dump((L, M), open(CACHE, "wb"))
    _, H = PD.ultimo_download()
    negs = H["negocios"]
    comprados, tese_r = collections.defaultdict(set), collections.defaultdict(set)
    for d in negs:
        if d["status"] != "ganho": continue
        r = PD.raiz(d["extras"].get("cnpj"))
        if not r: continue
        comprados[r].add(PIPE_PROD.get(d["pipeline"], d["pipeline"]))
        for t in (d["variante"] or "").split(";"):
            if t.strip(): tese_r[r].add(familia_tese(t))
    con = sqlite3.connect(f"file:{PD.RECEITA_DB}?mode=ro", uri=True)
    sec = {}
    raizes = {l["cnpj"][:8] for l in L}
    for b, cs in con.execute("select basico, group_concat(coalesce(cnaes_sec,''), ',') from estab group by basico"):
        if b in raizes: sec[b] = [x.strip() for x in (cs or "").split(",") if x.strip()]
    con.close()

    out = []
    for l in L:
        r = l["cnpj"][:8]
        s, nivel = setor_ind(l["cnae"])
        origem = "CNAE principal"
        if not s:
            sec_ind = [(setor_ind(x), x) for x in sec.get(r, []) if x[:2] >= "10" and x[:2] <= "33"]
            sec_ind = [((a, b), x) for (a, b), x in sec_ind if a and b >= 2]
            if sec_ind:
                (s0, n0), x0 = max(sec_ind, key=lambda z: z[0][1])
                s, nivel, origem = f"Comércio com indústria secundária ({s0})", 1, f"CNAE secundário {x0}"
            elif l["cnae"].startswith(ADJ_COMERCIO):
                s, nivel, origem = "Comércio de bens manufaturados (adjacente)", 0, "CNAE principal"
            else:
                continue   # fora do perfil Maquila: entra só na contagem
        industrial = l["cnae"][:2] >= "10" and l["cnae"][:2] <= "33"
        # ---------- score 0–100 ----------
        p = {}
        p["setor"] = {3: 35, 2: 25, 1: 15 if industrial else 10, 0: 5}[nivel]
        if s == "Alimentos processados" and l["exportador"] != "n": p["setor"] = 22   # alimentos com sinal de exportação sobem
        p["uf"] = UF_PTS.get(l["uf"], 3)
        conf_m = {"alta": 1.0, "média": 0.9, "baixa": 0.7, "muito baixa": 0.5, "": 0}[l["fat_conf"]]
        fat = l["fat"] or 0
        pf = 12 if fat >= 100e6 else 10 if fat >= 50e6 else 7 if fat >= 20e6 else 4 if fat >= 5e6 else 1 if fat else 0
        cap = l["capital"] or 0
        pc = 5 if cap >= 10e6 else 4 if cap >= 5e6 else 3 if cap >= 1e6 else 1 if cap >= 300e3 else 0
        p["porte"] = min(20, round(pf * conf_m, 1) + pc + (2 if l["porte"] == "Demais" else 0) + (1 if l["filiais"] >= 2 else 0))
        p["exportador"] = {"s": 10, "provável": 5, "n": 0}[l["exportador"]]
        if p["exportador"] == 0 and l["cnae"].startswith(EXPORT_CNAE_IND): p["exportador"] = 5
        p["regime"] = {"Lucro Real": 8, "Lucro Presumido": 4}.get(l["regime"], 0)
        p["relacionamento"] = min(12, (7 if l["status"] == "ganho" else 3) + (3 if l["e_master"] else 0) + (2 if l["ultimo"] >= "2025-04-01" else 0))
        score = int(round(sum(p.values())))
        grande = (fat >= 50e6 and l["fat_conf"] != "muito baixa") or cap >= 5e6 or (fat >= 100e6 and cap >= 1e6)
        if l["ativa"] is False or not industrial or l["regime"] == "Simples Nacional":
            faixa = "C"
        elif score >= 65 and nivel >= 2 and grande:
            faixa = "A"
        elif score >= 50 and nivel >= 1:
            faixa = "B"
        else:
            faixa = "C"
        exp = "s" if l["exportador"] == "s" else "provável" if p["exportador"] else "n"

        ja = sorted(comprados.get(r, set()))
        teses = sorted(tese_r.get(r, set()))
        # ---------- pacote Save Maquila sugerido ----------
        pac = ["Diagnóstico de viabilidade Maquila (Internacionalização · escritório Paraguai)"]
        if "Recuperação tributária (Real/Presumido)" in ja: pac.append("Recuperação tributária: revisão/recorrência para reforçar o caixa do projeto")
        else: pac.append("Recuperação tributária (diagnóstico) para gerar caixa ao projeto")
        if grande: pac.append("Crédito internacional para capex/giro da planta (a partir de US$ 5 mi; confirmar porte)")
        else: pac.append("Financiamento: abaixo do perfil do crédito internacional; avaliar alternativa (pergunta ao João)")
        pac.append("Holding/planejamento tributário: estrutura societária Brasil–Paraguai")
        if l["passivo"] is not None and (l["passivo"] >= 1e5 or l["passivo"] == -1): pac.append("Gestão de passivo/transação para regularizar a CND")
        else: pac.append("Checagem de CND e débitos (Gestão de passivo, se houver)")
        if nivel == 3 and "Previdenciário (verbas/RAT)" not in teses: pac.append("Previdenciário (verbas/RAT) na folha que fica no Brasil")
        pac.append("Compliance (dossiê) e contencioso: risco fiscal da operação Brasil–Paraguai")
        if l["regime"] == "Lucro Real": pac.append("Revisão CBS/IBS na transição (frente em estruturação)")

        mot = []
        if l["ativa"] is False: mot.append(f"CNPJ {l['situacao']} na Receita")
        mot.append(f"{s} ({origem} {l['cnae']})")
        if l["uf"] in UF_PTS: mot.append(f"{l['uf']} com logística até o Paraguai")
        if fat: mot.append(f"faturamento est. R$ {fat/1e6:.1f} mi ({l['fat_fonte'].split(' (')[0].split(':')[0]}, confiança {l['fat_conf']})")
        if cap >= 1e6: mot.append(f"capital R$ {cap/1e6:.1f} mi")
        if l["porte"] == "Demais": mot.append("porte Demais")
        if l["filiais"] >= 2: mot.append(f"{l['filiais']} estabelecimentos ativos")
        if exp != "n": mot.append(f"exportador {exp}" + (f" ({l['exp_motivo'][:60]})" if l["exportador"] != "n" else " (CNAE de cadeia exportadora)"))
        if l["regime"]: mot.append(l["regime"])
        mot.append(f"cliente {l['status']}" + (f" via {l['parceiro']}" if l["e_master"] else " (fora do roster de Masters)"))
        if not industrial: mot.append("não é indústria hoje: entra como C (contrataria a industrialização)")
        if l["regime"] == "Simples Nacional": mot.append("Simples Nacional: fora do perfil (faixa C)")

        out.append(dict(l, m_setor=s, m_nivel=nivel, m_origem=origem, m_industrial=industrial, m_pontos=p, m_score=score,
                        m_faixa=faixa, m_exp=exp, ja=ja, teses=teses, pacote=pac, m_motivos="; ".join(mot), grande=grande))
    out.sort(key=lambda x: ({"A": 0, "B": 1, "C": 2}[x["m_faixa"]], -x["m_score"], -(x["fat"] or 0)))
    return out, L, M


def prospects(hs_raizes):
    con = sqlite3.connect(f"file:{PD.RECEITA_DB}?mode=ro", uri=True); con.row_factory = sqlite3.Row
    n_estab = dict(con.execute("select basico, count(*) from estab where situacao='Ativa' group by basico").fetchall())
    q = """select e.cnpj, e.basico, e.cnae, e.cnaes_sec, e.uf, e.inicio, m.razao, m.capital, m.porte, s.simples,
           (select descricao from ref where tipo='cnae' and codigo=e.cnae) cnae_desc,
           (select descricao from ref where tipo='municipio' and codigo=e.municipio) cidade
           from estab e join empresa m on m.basico=e.basico left join simples s on s.basico=e.basico
           where e.matriz='matriz' and e.situacao='Ativa' and e.no_hubspot=0 and substr(e.cnae,1,4) in (%s)""" % ",".join("?" * len(PROSPECT_CNAE))
    rows = con.execute(q, PROSPECT_CNAE).fetchall()
    universo = collections.Counter()
    out = []
    for r in rows:
        if r["basico"] in hs_raizes: continue
        s, nivel = setor_ind(r["cnae"])
        universo[(s, r["porte"])] += 1
        if r["porte"] != "Demais" or (r["simples"] or "") == "S" or (r["capital"] or 0) < 1e6 or r["uf"] not in UF_PTS: continue
        cap = r["capital"] or 0
        fil = n_estab.get(r["basico"], 1)
        sec = r["cnaes_sec"] or ""
        p = dict(setor=25 if nivel >= 2 else 15, uf=UF_PTS.get(r["uf"], 3),
                 porte=min(20, (14 if cap >= 50e6 else 11 if cap >= 10e6 else 8 if cap >= 5e6 else 5) + 3 + (3 if fil >= 3 else 1 if fil == 2 else 0)),
                 exportador=5 if r["cnae"].startswith(EXPORT_CNAE_IND) or "4634" in sec else 0)
        bruto = sum(p.values())                     # máximo 70 (sem regime e relacionamento, que não existem fora da base)
        score = int(round(bruto * 100 / 70))
        faixa = "A" if score >= 75 and cap >= 10e6 else "B" if score >= 60 else "C"
        out.append(dict(faixa=faixa, score=score, empresa=r["razao"], cnpj=r["cnpj"], cnae=r["cnae"], cnae_desc=r["cnae_desc"], setor=s,
                        uf=r["uf"], cidade=r["cidade"], capital=cap, filiais=fil, inicio=r["inicio"], pontos=p,
                        exportador="provável" if p["exportador"] else "n"))
    con.close()
    out.sort(key=lambda x: ({"A": 0, "B": 1, "C": 2}[x["faixa"]], -x["score"], -x["capital"]))
    return out, universo


def cobertura():
    con = sqlite3.connect(f"file:{PD.RECEITA_DB}?mode=ro", uri=True)
    tot = con.execute("select count(*), count(distinct basico) from estab").fetchone()
    ind = con.execute("select substr(cnae,1,2), sum(no_hubspot=0), sum(no_hubspot=1) from estab where substr(cnae,1,2) between '10' and '33' group by 1").fetchall()
    ufs = [u for (u,) in con.execute("select distinct uf from estab where no_hubspot=0")]
    meta = dict(con.execute("select chave, valor from meta").fetchall())
    con.close()
    return dict(estab=tot[0], empresas=tot[1], industria_por_divisao={d: dict(fora_hubspot=a, do_hubspot=b) for d, a, b in ind},
                ufs_carregadas=sorted(ufs), meta=meta)


# ---------- planilha ----------
COLS = [("Faixa", "m_faixa", 7), ("Score", "m_score", 7), ("Empresa", "empresa", 42), ("CNPJ", "cnpj_fmt", 20),
        ("CNAE principal", "cnae_txt", 44), ("Setor Maquila", "m_setor", 30), ("Origem do setor", "m_origem", 16),
        ("UF", "uf", 5), ("Cidade", "cidade", 20),
        ("Faturamento estimado (R$/ano)", "fat", 18), ("Fonte do faturamento", "fat_fonte", 34), ("Confiança", "fat_conf", 11),
        ("Capital social (R$)", "capital", 16), ("Porte (Receita)", "porte", 14), ("Estab. ativos", "filiais", 9),
        ("Exportador", "m_exp", 11), ("Regime", "regime", 15), ("Parceiro", "parceiro", 22), ("Status na Save", "status", 10),
        ("Produtos que já comprou", "ja_txt", 40), ("Teses já ganhas", "teses_txt", 40),
        ("Produtos Save sugeridos no pacote", "pacote_txt", 80), ("Link do HubSpot", "link", 16), ("Por que está aqui", "m_motivos", 90),
        ("Pontos: setor/35", "p1", 8), ("UF/15", "p2", 7), ("porte/20", "p3", 7), ("exportador/10", "p4", 8), ("regime/8", "p5", 7), ("relacionamento/12", "p6", 9)]
PCOLS = [("Faixa", "faixa", 7), ("Score parcial", "score", 8), ("Empresa", "empresa", 42), ("CNPJ", "cnpj_fmt", 20),
         ("CNAE principal", "cnae_txt", 50), ("Setor Maquila", "setor", 28), ("UF", "uf", 5), ("Cidade", "cidade", 20),
         ("Capital social (R$)", "capital", 16), ("Estab. ativos", "filiais", 9), ("Exportador", "exportador", 10),
         ("Início de atividade", "inicio", 12), ("Por que está aqui", "motivo", 70)]


def cnpj_fmt(c):
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}" if len(c) == 14 else c


def _aba(wb, titulo, cols, linhas, faixa_key, num_keys, link_key=None, primeira=False):
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    ws = wb.active if primeira else wb.create_sheet(titulo)
    ws.title = titulo
    hdr = PatternFill("solid", fgColor="1F3864"); cor = {"A": "C6EFCE", "B": "FFEB9C", "C": "F2F2F2"}
    ws.append([c[0] for c in cols])
    for i, (_, _, w) in enumerate(cols, 1):
        cel = ws.cell(row=1, column=i)
        cel.font = Font(bold=True, color="FFFFFF"); cel.fill = hdr
        cel.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 42
    keys = [k for _, k, _ in cols]
    for l in linhas:
        ws.append([l.get(k) for k in keys])
        rw = ws.max_row
        ws.cell(row=rw, column=1).fill = PatternFill("solid", fgColor=cor[l[faixa_key]])
        for k in num_keys:
            ws.cell(row=rw, column=keys.index(k) + 1).number_format = "#,##0"
        if link_key:
            lk = ws.cell(row=rw, column=keys.index(link_key) + 1)
            lk.hyperlink = l[link_key]; lk.value = "abrir no HubSpot"; lk.font = Font(color="0563C1", underline="single")
    ws.freeze_panes = "D2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{ws.max_row}"
    return ws


def gravar_xlsx(B, P, AG, destino):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    wb = Workbook()
    rows = []
    for l in B:
        p = l["m_pontos"]
        rows.append(dict(l, cnpj_fmt=cnpj_fmt(l["cnpj"]), cnae_txt=f"{l['cnae']} · {l['cnae_desc']}".strip(" ·"),
                         fat=round(l["fat"]) if l["fat"] else None, capital=l["capital"] or None,
                         ja_txt=" · ".join(l["ja"]) or "—", teses_txt=" · ".join(l["teses"]) or "—", pacote_txt=" | ".join(l["pacote"]),
                         p1=p["setor"], p2=p["uf"], p3=p["porte"], p4=p["exportador"], p5=p["regime"], p6=p["relacionamento"]))
    _aba(wb, "Base Maquila", COLS, rows, "m_faixa", ["fat", "capital"], "link", primeira=True)
    prow = [dict(x, cnpj_fmt=cnpj_fmt(x["cnpj"]), cnae_txt=f"{x['cnae']} · {x['cnae_desc']}",
                 motivo=f"{x['setor']}; {x['uf']}; capital R$ {x['capital']/1e6:.1f} mi; porte Demais, fora do Simples; {x['filiais']} estab. ativos"
                        + ("; cadeia exportadora (CNAE)" if x["exportador"] != "n" else "") + "; NÃO está no HubSpot"
                        + ("; grupo de grande porte (capital > R$ 1 bi): abordagem institucional, não pelo canal de parceiros" if x["capital"] > 1e9 else "")) for x in P]
    _aba(wb, "Prospects fora da base", PCOLS, prow, "faixa", ["capital"])
    m = wb.create_sheet("Metodologia")
    C = AG["cobertura"]
    txt = [
        ["Projeto Maquila · base priorizada", ""],
        ["Gerado em", f"{date.today().isoformat()} · Intel Comercial + Dados + Gabinete (rascunho para o Luis). Dono do produto Maquila: João Mattos e sócios."],
        ["HubSpot", f"{AG['meta']['download']} · negócios ganhos e abertos, 1 linha por raiz de CNPJ ({AG['meta']['empresas']} empresas)"],
        ["Receita", f"{C['meta'].get('fonte')} · base local, somente leitura"],
        ["Quem entra na aba Base", "Empresas com CNAE principal industrial (divisões 10–33), comércio com CNAE secundário industrial de aderência média/alta, e comércio atacadista de bens manufaturados (adjacente). Varejo, serviços e o resto do atacado ficam fora."],
        ["", ""],
        ["Score (0–100)", "Setor 35 · UF/logística 15 · Porte e capacidade 20 · Exportador 10 · Regime 8 · Relacionamento 12"],
        ["Setor (35)", "Núcleo Maquila 35: têxtil, confecção, couro e calçados, plásticos e borracha, embalagens, autopeças, eletroeletrônicos, móveis · boa aderência 25: produtos de metal, metalurgia, máquinas, veículos/carrocerias, frigoríficos e produtos de carne, diversos (32) · alimentos com sinal de exportação 22 · demais indústrias 15 · comércio com indústria secundária 10 · comércio adjacente 5"],
        ["UF (15)", "PR e MS 15 · SC e RS 13 · SP 12 · GO e MG 10 · MT 8 · DF 6 · demais 3 (distância e logística até o Paraguai)"],
        ["Porte (20)", "Faturamento est. ≥ 100 mi 12 · ≥ 50 mi 10 · ≥ 20 mi 7 · ≥ 5 mi 4 · menor 1, × confiança (parecer 1,0/0,9 · HubSpot à mão 0,7 · proxy do crédito 0,5) + capital ≥ 10 mi 5 · ≥ 5 mi 4 · ≥ 1 mi 3 · ≥ 300 mil 1 + porte Demais 2 + 2 ou mais estabelecimentos 1"],
        ["Faturamento", "Parecer técnico quando há; senão valor preenchido à mão no HubSpot; senão PROXY = maior crédito de um negócio ÷ p75 da razão crédito/faturamento (cerca de 0,084; 0,121 no café). Proxy está marcado na coluna Fonte e tem confiança 'muito baixa'."],
        ["Exportador (10)", "s = parecer cita exportação ou razão social (10) · provável = CNAE de cadeia exportadora (5)"],
        ["Regime (8)", "Lucro Real 8 · Presumido 4 · Simples 0 (e vai para C)"],
        ["Relacionamento (12)", "Ganho 7 (aberto 3) · parceiro Master dono da conta +3 · negócio desde abr/2025 +2"],
        ["Faixa A", "Indústria, setor núcleo ou boa aderência, score ≥ 65, sinal de porte grande (faturamento ≥ 50 mi não proxy, proxy ≥ 100 mi com capital ≥ 1 mi, ou capital ≥ 5 mi), CNPJ ativo, fora do Simples"],
        ["Faixa B", "Indústria com score ≥ 50 (e não A)"],
        ["Faixa C", "Demais, não indústria, Simples ou CNPJ não ativo"],
        ["Pacote sugerido", "Regra automática para ordenar a conversa, não proposta: o diagnóstico Maquila sempre; crédito internacional só com sinal de porte grande (mínimo US$ 5 mi); passivo/CND quando o parecer cita débitos; previdenciário no núcleo intensivo em mão de obra que ainda não comprou; CBS/IBS no Lucro Real."],
        ["Prospects fora da base", f"Receita local: só os CNAEs industriais carregados por inteiro ({', '.join(RECEITA_COMPLETA)}). Filtro: matriz ativa, porte Demais, fora do Simples, capital ≥ R$ 1 mi, UF da lista, raiz fora do HubSpot. Score parcial = setor 25/15 + UF 15 + capital/estab. 20 + exportador 5, reescalado de 70 para 100. A: score ≥ 75 e capital ≥ 10 mi; B: ≥ 60."],
        ["Cobertura da Receita", f"{C['estab']:,} estabelecimentos; UFs carregadas: {', '.join(C['ufs_carregadas'])} (RS fora). Indústria fora dessas divisões só existe para quem já está no HubSpot. Faltaria baixar: CNAEs 13, 14, 15, 22, 1731-1733, 2312, 2591, 24, 25, 26, 27, 28, 29, 31, 32 e o restante do 10/11, com as UFs RS (e SC/PR/MS já carregadas)."],
        ["Limites", "Não há cliente da Save em maquila nem material interno do produto: tudo o que depende de definição interna é pergunta ao João Mattos. O regime está sendo estudado por outro time; este arquivo não afirma nada sobre ele."],
        ["LGPD e canal", "Uso interno. Sem sócios nem CPF. O cliente é do parceiro Master: abordagem passa pelo Master. Não enviar a terceiros."],
    ]
    for row in txt: m.append(row)
    m.column_dimensions["A"].width = 26; m.column_dimensions["B"].width = 160
    m["A1"].font = Font(bold=True, size=13)
    for r in range(2, m.max_row + 1):
        m.cell(row=r, column=1).font = Font(bold=True); m.cell(row=r, column=2).alignment = Alignment(wrap_text=True, vertical="top")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    wb.save(destino)


def agregados(B, P, universo, L, M, port, teses, n_var):
    c = collections.Counter
    ag = dict(meta=M, cobertura=cobertura(), portfolio=port, teses=teses, negocios_com_tese=n_var)
    ag["base_total_empresas"] = len(L)
    ag["base_por_divisao_cnae"] = dict(c((l["cnae"][:2] or "sem CNAE") for l in L))
    ag["industriais_cnae_principal"] = sum(1 for l in L if l["cnae"][:2] >= "10" and l["cnae"][:2] <= "33")
    ag["industriais_ganhos"] = sum(1 for l in L if l["cnae"][:2] >= "10" and l["cnae"][:2] <= "33" and l["status"] == "ganho")
    ag["na_aba"] = len(B)
    ag["faixas"] = dict(c(b["m_faixa"] for b in B))
    ag["por_setor"] = {s: dict(c(b["m_faixa"] for b in B if b["m_setor"] == s)) for s in sorted({b["m_setor"] for b in B})}
    ag["por_nivel"] = {n: dict(c(b["m_faixa"] for b in B if b["m_nivel"] == n)) for n in (3, 2, 1, 0)}
    ag["por_uf"] = {u: dict(c(b["m_faixa"] for b in B if b["uf"] == u)) for u in sorted({b["uf"] for b in B})}
    ag["por_parceiro"] = {p: dict(c(b["m_faixa"] for b in B if b["parceiro"] == p)) for p in sorted({b["parceiro"] for b in B})}
    ag["por_status"] = {s: dict(c(b["m_faixa"] for b in B if b["status"] == s)) for s in ("ganho", "aberto")}
    ag["por_regime"] = {s: dict(c(b["m_faixa"] for b in B if b["regime"] == s)) for s in sorted({b["regime"] for b in B})}
    ag["fonte_fat"] = {f: dict(c(b["m_faixa"] for b in B if (b["fat_fonte"] or "sem dado").split(" (")[0].split(":")[0] == f))
                       for f in sorted({(b["fat_fonte"] or "sem dado").split(" (")[0].split(":")[0] for b in B})}
    ag["exportador"] = {e: dict(c(b["m_faixa"] for b in B if b["m_exp"] == e)) for e in ("s", "provável", "n")}
    ag["grande_porte"] = dict(c(b["m_faixa"] for b in B if b["grande"]))
    ag["perfil_credito_internacional_AB"] = sum(1 for b in B if b["m_faixa"] in "AB" and b["grande"])
    ag["ja_comprou"] = dict(c(x for b in B for x in b["ja"]))
    ag["teses_AB"] = dict(c(x for b in B if b["m_faixa"] in "AB" for x in b["teses"]))
    ag["pacote_AB"] = dict(c(x.split(":")[0].split(" (")[0] for b in B if b["m_faixa"] in "AB" for x in b["pacote"]))
    ag["situacao"] = dict(c(b["situacao"] for b in B))
    ag["score_medio"] = {f: round(st.mean([b["m_score"] for b in B if b["m_faixa"] == f]), 1) for f in "ABC" if any(b["m_faixa"] == f for b in B)}
    ag["prospects"] = dict(total=len(P), faixas=dict(c(x["faixa"] for x in P)),
                           por_setor={s: dict(c(x["faixa"] for x in P if x["setor"] == s)) for s in sorted({x["setor"] for x in P})},
                           por_uf={u: dict(c(x["faixa"] for x in P if x["uf"] == u)) for u in sorted({x["uf"] for x in P})},
                           universo_fora_hubspot={f"{s} · {pt}": n for (s, pt), n in sorted(universo.items(), key=str)})
    return ag


if __name__ == "__main__":
    B, L, M = montar_base()
    _, H = PD.ultimo_download()
    port, teses, n_var = portfolio(H)
    hs_raizes = {PD.raiz(d["extras"].get("cnpj")) for d in H["negocios"] if PD.raiz(d["extras"].get("cnpj"))}
    P, universo = prospects(hs_raizes)
    AG = agregados(B, P, universo, L, M, port, teses, n_var)
    area = subprocess.run([sys.executable, os.path.join(AP, "lib/caminhos.py"), "area"], capture_output=True, text=True).stdout.strip()
    destino = os.path.join(area, "Gestão · Luis", "Produtos", "Maquila", "Maquila-Base-Priorizada.xlsx")
    gravar_xlsx(B, P, AG, destino)
    shutil.copy2(destino, os.path.join(PASTA, "Maquila-Base-Priorizada.xlsx"))
    json.dump(AG, open(os.path.join(PASTA, "scripts", "maquila-agregados.json"), "w"), ensure_ascii=False, indent=1, default=str)
    if "--amostra" in sys.argv:
        for b in [x for x in B if x["m_faixa"] in "AB"][:60]:
            print(b["m_faixa"], b["m_score"], b["empresa"][:34], b["uf"], b["m_setor"][:26], b["cnae"], b["m_exp"], f"{(b['fat'] or 0)/1e6:.1f}", b["fat_conf"], f"{(b['capital'] or 0)/1e6:.1f}", b["regime"][:8], b["parceiro"][:12], b["status"], b["m_pontos"])
        for x in P[:15]: print("P", x["faixa"], x["score"], x["empresa"][:34], x["uf"], x["setor"], f"{x['capital']/1e6:.1f}")
    print(json.dumps({k: v for k, v in AG.items() if k not in ("meta",)}, ensure_ascii=False, indent=1, default=str))
    print("planilha:", destino)
