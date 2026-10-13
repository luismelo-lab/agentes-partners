"""Crédito internacional · base de clientes priorizada (Intel Comercial + Dados, 02/10/2026).

Somente leitura e local: download do HubSpot, base da Receita (SQLite local) e textos dos pareceres.
Nenhum CNPJ sai da máquina; não lê .env; não traz sócios nem CPF.
Uso:  python3 base_clientes.py            -> grava a planilha nominal e o JSON agregado (sem nomes)
"""
import collections, json, os, re, shutil, sqlite3, subprocess, sys
from datetime import date

sys.path.insert(0, os.path.expanduser("~/agentes-partners/lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import partners_dados as PD
import extrator_faturamento as EF

AP = PD.AP
PASTA = os.path.join(AP, "departamentos/produtos/credito-internacional")
RESUMOS = os.path.join(AP, "celulas/geovana/pareceres/resumos.json")
DEFAULT_FAT = {"20000000", "3600000", "4800000"}  # o HubSpot repete esses valores por porte (importação): não é faturamento

# ---------- setores pelo CNAE principal (prefixos; o mais longo vence) ----------
SETORES = [  # (nome, prioridade 2 = prioritário, 1 = adjacente, 0 = outro, prefixos)
    ("Café", 2, ["4621", "0134", "1081"]),
    ("Usinas (açúcar/etanol)", 2, ["1071", "1931"]),
    ("Frigoríficos (abate/indústria de carnes)", 2, ["1011", "1012", "1013"]),
    ("Construtoras e incorporadoras", 2, ["41", "42", "43", "6810"]),
    ("Máquinas e equipamentos", 2, ["4661", "4662", "4663", "4664", "4665", "4669", "282", "283", "4511", "4512"]),
    ("Agro, produtores e insumos agropecuários", 2, ["01", "02", "4622", "4623", "4683", "4692", "1066", "4611"]),
    ("Carnes · atacado", 1, ["4634"]),
    ("Indústria de alimentos e bebidas", 1, ["10", "11"]),
    ("Combustíveis · distribuição/atacado", 1, ["4681", "4682"]),
    ("Atacado de alimentos e mercadorias", 0, ["463", "4691", "4693"]),
    ("Supermercados e varejo alimentar", 0, ["4711", "4712", "472"]),
    ("Postos de combustíveis", 0, ["4731", "4732"]),
    ("Transporte e logística", 0, ["49", "50", "52"]),
]
EXPORT_CNAE = ["4621", "0134", "1011", "1012", "1013", "1071", "1931", "4622", "4623", "1041", "1061", "1064", "0115", "0151", "1052"]


def _cidades(txt):
    return {x.replace("_", " ") for x in txt.split()}


SUL_MG = _cidades("""VARGINHA SANTO_ANTONIO_DO_AMPARO ALBERTINA ALFENAS MACHADO LAMBARI POCO_FUNDO NEPOMUCENO MONSENHOR_PAULO TRES_CORACOES
BUENO_BRANDAO POCOS_DE_CALDAS ANDRADAS SAO_PEDRO_DA_UNIAO ITAMOGI MONTE_BELO JURUAIA PASSOS NOVA_RESENDE BOA_ESPERANCA OURO_FINO
CAMPO_BELO SAO_SEBASTIAO_DO_PARAISO GUAXUPE TRES_PONTAS ELOI_MENDES CAMPOS_GERAIS CARMO_DE_MINAS SANTA_RITA_DO_SAPUCAI POUSO_ALEGRE
LAVRAS PERDOES CAMPESTRE BOTELHOS CABO_VERDE MUZAMBINHO PARAGUACU CARMO_DO_RIO_CLARO CAMBUQUIRA CORDISLANDIA SAO_GONCALO_DO_SAPUCAI
CARMO_DA_CACHOEIRA COQUEIRAL SANTANA_DA_VARGEM ILICINEA GUAPE CRISTAIS CAMPO_DO_MEIO ALTEROSA AREADO SERRANIA DIVISA_NOVA
CONCEICAO_DA_APARECIDA ARCEBURGO GUARANESIA MONTE_SANTO_DE_MINAS CAPETINGA IBIRACI CLARAVAL ITAU_DE_MINAS PRATAPOLIS SAO_TOMAS_DE_AQUINO
JACUI FORTALEZA_DE_MINAS BOM_JESUS_DA_PENHA CONGONHAL ESPIRITO_SANTO_DO_DOURADO CARVALHOPOLIS TURVOLANDIA HELIODORA NATERCIA
CONCEICAO_DO_RIO_VERDE SAO_LOURENCO CAXAMBU BAEPENDI CRISTINA MARIA_DA_FE BRAZOPOLIS ITAJUBA PIRANGUINHO CAREACU SILVIANOPOLIS ESTIVA
CAMANDUCAIA EXTREMA JACUTINGA MONTE_SIAO INCONFIDENTES BORDA_DA_MATA IPUIUNA CALDAS SANTA_RITA_DE_CALDAS IBITIURA_DE_MINAS
BANDEIRA_DO_SUL FAMA BOM_SUCESSO IBITURUNA CANA_VERDE CANDEIAS AGUANIL""")
MATAS_MG = _cidades("""MANHUACU ESPERA_FELIZ MANHUMIRIM CAIANA CAPARAO SAO_JOAO_DO_MANHUACU SIMONESIA CAPUTIRA ERVALIA CARATINGA SAO_MIGUEL_DO_ANTA
LAJINHA LUISBURGO REDUTO SANTANA_DO_MANHUACU MUTUM ALTO_JEQUITIBA ALTO_CAPARAO DIVINO CARANGOLA VICOSA ARAPONGA""")
CERRADO_MG = _cidades("""CARMO_DO_PARANAIBA PATROCINIO ARAXA MONTE_CARMELO PATOS_DE_MINAS ARAGUARI SAO_GOTARDO RIO_PARANAIBA SERRA_DO_SALITRE
COROMANDEL IBIA CAMPOS_ALTOS PERDIZES""")


def regiao(uf, cidade):
    if uf != "MG": return ""
    c = PD.norm(cidade).upper()
    return "Sul de Minas" if c in SUL_MG else "Matas de Minas" if c in MATAS_MG else "Cerrado Mineiro" if c in CERRADO_MG else "MG · outras"


def setor(cnae, nome):
    c = re.sub(r"\D", "", cnae or "")
    n = PD.norm(nome)
    if any(p in n for p in ("cafe", "coffee", "torref")): return "Café", 2
    if c:
        melhor = None
        for s, pr, prefs in SETORES:
            for p in prefs:
                if c.startswith(p) and (melhor is None or len(p) > melhor[2]): melhor = (s, pr, len(p))
        return (melhor[0], melhor[1]) if melhor else ("Outros", 0)   # com CNAE, o nome não reclassifica (só o café, acima)
    if any(p in n for p in ("frigorif", "abatedouro")): return "Frigoríficos (abate/indústria de carnes)", 2
    if "usina" in n: return "Usinas (açúcar/etanol)", 2
    if any(p in n for p in ("construtora", "incorporadora")): return "Construtoras e incorporadoras", 2
    if any(p in n for p in ("maquinas", "tratores")): return "Máquinas e equipamentos", 2
    if any(p in n for p in ("agropecuar", "fazenda", "agricola", "cereais", "graos")): return "Agro, produtores e insumos agropecuários", 2
    return ("Outros", 0) if c else ("Sem CNAE", 0)


def num(s):
    try: return float(s)
    except (TypeError, ValueError): return None


def passivo_valor(txt):
    """Débito tributário citado no parecer: valor em R$, -1 se há sem valor, 0 se não há, None sem dado."""
    if not txt: return None
    t = PD.norm(txt)
    vals = [float(v.replace(".", "").replace(",", ".")) for v in re.findall(r"R\$\s*([\d.]+,\d{2})", txt)]
    if vals: return max(vals)
    if re.match(r"^(empresa )?(nao|não)", t) or "nao possui" in t[:40]: return 0.0
    if re.search(r"possui (debitos|dividas|parcelamento)|execucao fiscal|negociad|parcelad", t): return -1.0
    return 0.0


def montar():
    caminho, H = PD.ultimo_download()
    negs = H["negocios"]
    por_id = {d["id"]: d for d in negs}
    resumos = json.load(open(RESUMOS))
    fat_par = EF.por_negocio()

    por_raiz_todos = collections.defaultdict(list)       # inclui perdidos: parecer de outra tentativa também informa o porte
    for d in negs:
        r = PD.raiz(d["extras"].get("cnpj"))
        if r: por_raiz_todos[r].append(d)
    uni, sem_cnpj = collections.defaultdict(list), 0
    for d in negs:
        if d["status"] not in ("ganho", "aberto"): continue
        r = PD.raiz(d["extras"].get("cnpj"))
        if not r: sem_cnpj += 1; continue
        uni[r].append(d)

    con = sqlite3.connect(f"file:{PD.RECEITA_DB}?mode=ro", uri=True)
    n_estab = dict(con.execute("select basico, count(*) from estab where situacao='Ativa' group by basico").fetchall())
    sec = {b: (cs or "") for b, cs in con.execute("select basico, group_concat(coalesce(cnaes_sec,''), ',') from estab group by basico") if b in uni}
    meta_rf = dict(con.execute("select chave, valor from meta").fetchall())
    con.close()

    # calibração do proxy: crédito do negócio ÷ faturamento anual citado no parecer do mesmo negócio
    # (só negócios ganhos com valor > 0; razão > 0,5 é erro de cadastro). Usa o p75 = estimativa CONSERVADORA (faturamento menor)
    amostra = []
    for i, a in fat_par.items():
        d = por_id.get(i)
        if d and d["status"] == "ganho" and (d["valor"] or 0) > 0 and a["anual"] > 0 and d["valor"] / a["anual"] <= 0.5:
            amostra.append((d["valor"] / a["anual"], PD.e_cafe(d) or (PD.receita(d["extras"].get("cnpj")) or {}).get("cnae", "").startswith(("4621", "0134", "1081"))))
    ratios = sorted(x for x, _ in amostra)
    r_cafe = sorted(x for x, c in amostra if c)
    med_ratio = ratios[3 * len(ratios) // 4] if ratios else None
    ratio_cafe = r_cafe[3 * len(r_cafe) // 4] if len(r_cafe) >= 5 else med_ratio   # café acumula mais crédito por R$ faturado

    linhas = []
    for r, ds in uni.items():
        ganhos = [d for d in ds if d["status"] == "ganho"]
        status = "ganho" if ganhos else "aberto"
        top = sorted(ganhos or ds, key=lambda d: (d["valor"] or 0), reverse=True)[0]
        cnpj = PD.cnpj_digitos(top["extras"].get("cnpj"))
        rf = PD.receita(cnpj) or {}
        nome = rf.get("razao") or top["nome"]
        cnae = rf.get("cnae") or re.sub(r"\D", "", top.get("cnae") or "")
        s_nome, s_pr = setor(cnae, nome + " " + (top.get("nome") or ""))
        cnae_desc = rf.get("cnae_desc") or (top.get("segmento") or "")
        parceiro = collections.Counter(d["parceiro"] for d in (ganhos or ds)).most_common(1)[0][0]
        e_master = parceiro != "Outros (fora do roster)"
        # importação do Bitrix (28/11/2025) duplicou negócios com o mesmo valor arredondado: soma valores distintos
        credito = sum({int(d["valor"] or 0) for d in ganhos}) if ganhos else max((d["valor"] or 0) for d in ds)
        credito_max = max((d["valor"] or 0) for d in ds)
        ultimo = max((PD.data_efetiva(d) or "") for d in ds)
        capital = rf.get("capital") or 0
        porte = rf.get("porte") or ""
        situ = rf.get("situacao")
        ativa = (situ == "Ativa") if situ else None
        regime = collections.Counter(d["extras"].get("regime") for d in ds if d["extras"].get("regime")).most_common(1)
        regime = regime[0][0] if regime else ""
        filiais = n_estab.get(r, 0)
        todos = por_raiz_todos[r]

        # ---------- faturamento estimado: parecer > HubSpot preenchido à mão > proxy do crédito ----------
        fat, fonte, conf, trecho, serie, arquivo = None, "sem dado", "", "", {}, ""
        cand = [fat_par[d["id"]] for d in todos if d["id"] in fat_par]
        if cand:
            a = max(cand, key=lambda x: x["anual"])
            fat, trecho, serie, arquivo = a["anual"], a["trecho"], a["serie"], a["arquivo"]
            fonte = f"Parecer técnico ({a['forma']})"
            conf = "média" if "ambíguo" in a["forma"] else "alta" if (a["forma"] == "anual" or len(a["serie"]) >= 2) else "média"
            dv = (por_id.get(a["arquivo"].split("_")[0]) or {}).get("valor") or 0
            bruto = a["anual"] / 12 if "mensal" in a["forma"] else a["anual"]
            if dv and abs(bruto - dv) / dv < 0.01:   # o "faturamento" é quase o valor da tese: possível erro de digitação no parecer
                conf, fonte = "baixa", fonte + " — igual ao valor da tese, confirmar"
        else:
            hv = [num(d["extras"].get("faturamento")) for d in todos if d["extras"].get("faturamento") not in DEFAULT_FAT]
            hv = [v for v in hv if v and 1e5 <= v <= 5e9]
            if hv:
                fat, fonte, conf = max(hv), "HubSpot (preenchido à mão)", "baixa"
            elif med_ratio and credito_max > 0:
                rr = ratio_cafe if s_nome == "Café" else med_ratio
                fat, fonte, conf = credito_max / rr, f"Proxy: maior crédito de um negócio ÷ {rr:.3f} (p75 {'do café' if s_nome == 'Café' else 'da amostra'}, conservador)", "muito baixa"

        exp_txt, passivos, fatores = None, [], []
        for d in todos:
            exp_txt = exp_txt or EF.mencoes(d["id"])["exportacao"]
            rs = resumos.get(d["id"]) or {}
            pv = passivo_valor(rs.get("passivo"))
            if pv is not None: passivos.append(pv)
            if rs.get("fator_base"): fatores.append(rs["fator_base"])
        passivo = max(passivos) if passivos else None
        fator = max(fatores) if fatores else None
        cresc = None
        if len(serie) >= 2:
            ys = sorted(serie)
            v0 = next((serie[y] for y in ys if serie[y] > 0), 0)
            v1 = max(serie[y] for y in ys[-2:])
            cresc = (v1 / v0 - 1) if v0 else None
        nome_n = PD.norm(nome + " " + top["nome"])
        sec_cn = [x.strip() for x in sec.get(r, "").split(",") if x.strip()]
        if exp_txt or "export" in nome_n:
            exportador, exp_motivo = "s", ("parecer: " + re.sub(r"\s+", " ", exp_txt)[:90]) if exp_txt else "razão social cita exportação"
        elif any(cnae.startswith(p) for p in EXPORT_CNAE) or any(x.startswith(p) for x in sec_cn for p in EXPORT_CNAE) or "import" in nome_n:
            exportador, exp_motivo = "provável", "CNAE de cadeia exportadora" + (" / razão social cita importação" if "import" in nome_n else "")
        else:
            exportador, exp_motivo = "n", "sem sinal"

        # ---------- score 0–100 ----------
        p = {}
        if fat:
            mult = {"alta": 1.0, "média": 0.9, "baixa": 0.7, "muito baixa": 0.4}[conf]
            pts = 30 if fat >= 50e6 else 24 if fat >= 30e6 else 14 if fat >= 15e6 else 6 if fat >= 5e6 else 0
            p["faturamento"] = round(pts * mult, 1)
        else:
            p["faturamento"] = 0
        p["setor"] = {2: 20, 1: 10, 0: 0}[s_pr]
        p["exportador"] = {"s": 10, "provável": 5, "n": 0}[exportador]
        pc = 9 if capital >= 10e6 else 7 if capital >= 5e6 else 5 if capital >= 1e6 else 2 if capital >= 300e3 else 0
        pc += 3 if porte == "Demais" else 0
        pc += 1 if regime == "Lucro Real" else 0
        pc += 2 if filiais >= 3 else 1 if filiais == 2 else 0
        p["capital_porte"] = min(15, pc)
        p["relacionamento"] = min(15, (8 if status == "ganho" else 3) + (4 if e_master else 0) + (3 if ultimo >= "2025-04-01" else 0))
        pn = 0
        if passivo is not None and passivo >= 1e6: pn += 5
        elif passivo is not None and (passivo >= 1e5 or passivo == -1): pn += 3
        elif passivo: pn += 1
        if (cresc is not None and cresc >= 0.3) or (fator and fator >= 1.3): pn += 3
        if filiais >= 3: pn += 2
        p["necessidade"] = min(10, pn)
        score = int(round(sum(p.values())))

        sinal_grande = (fat and fat >= 30e6 and conf in ("alta", "média", "baixa")) or capital >= 5e6 or (fat and fat >= 50e6)
        if ativa is False:
            faixa = "C"
        elif score >= 60 and sinal_grande:
            faixa = "A"
        elif score >= 45 or (porte == "Demais" and s_pr == 2) or capital >= 1e6 or (fat and fat >= 30e6):
            faixa = "B"
        else:
            faixa = "C"

        motivos = []
        if ativa is False: motivos.append(f"CNPJ {situ} na Receita")
        if fat: motivos.append(f"faturamento est. R$ {fat/1e6:.1f} mi ({fonte.split(' (')[0].split(':')[0]}, confiança {conf})")
        if s_pr == 2:
            motivos.append(f"setor prioritário: {s_nome}" + (" (café está fora da meta de recuperação desde abr/2026, mas é prioridade para este produto)" if s_nome == "Café" else ""))
        elif s_pr == 1: motivos.append(f"setor adjacente: {s_nome}")
        if exportador != "n": motivos.append(f"exportador {exportador}")
        if capital >= 1e6: motivos.append(f"capital social R$ {capital/1e6:.1f} mi")
        if porte == "Demais": motivos.append("porte Demais")
        if filiais >= 2: motivos.append(f"{filiais} estabelecimentos ativos na base local")
        if passivo is not None and (passivo >= 1e5 or passivo == -1): motivos.append("débitos tributários citados no parecer")
        if (cresc is not None and cresc >= 0.3) or (fator and fator >= 1.3): motivos.append("base ou faturamento em crescimento")
        motivos.append(f"cliente {status}" + (f" via {parceiro}" if e_master else " (fora do roster de Masters)"))
        if credito_max > 50e6: motivos.append("ATENÇÃO: crédito de um negócio acima de R$ 50 mi — conferir o valor no HubSpot")

        perg = []
        if not fat or conf in ("baixa", "muito baixa"): perg.append("1) Qual o faturamento dos últimos 12 meses, com DRE/balanço de 2 anos?")
        elif fat < 50e6: perg.append("1) O faturamento de hoje já passa de R$ 30–50 mi/ano (DRE/balanço de 2 anos)?")
        else: perg.append("1) Confirma o faturamento anual com DRE/balanço de 2 anos?")
        perg.append("2) Existe projeto de US$ 5 mi (cerca de R$ 25–30 mi) ou mais — expansão, troca de dívida cara ou giro — e quanto custa a dívida hoje?")
        if s_nome in ("Café", "Agro, produtores e insumos agropecuários"):
            perg.append("3) Que garantia real livre chega perto de 2x o valor (terra, recebíveis/contratos futuros, bens de sócios ou de terceiros)?")
        elif s_nome == "Construtoras e incorporadoras":
            perg.append("3) Que garantia cobre perto de 2x o valor (imóveis livres, VGV/recebíveis das obras)?")
        else:
            perg.append("3) Que garantia real livre cobre perto de 2x o valor (imóveis, recebíveis, bens de sócios)?")
        if exportador != "n": perg.append("Extra: quanto da receita vem de exportação (moeda forte)?")

        linhas.append(dict(
            faixa=faixa, score=score, pontos=p, empresa=nome, cnpj=cnpj, uf=rf.get("uf") or top["extras"].get("uf") or "",
            cidade=rf.get("municipio_desc") or top["extras"].get("cidade") or "",
            regiao=regiao(rf.get("uf") or top["extras"].get("uf") or "", rf.get("municipio_desc") or top["extras"].get("cidade") or ""), setor=s_nome, setor_pr=s_pr, cnae=cnae,
            cnae_desc=cnae_desc, exportador=exportador, exp_motivo=exp_motivo, fat=fat, fat_fonte=fonte, fat_conf=conf,
            fat_trecho=trecho, fat_arquivo=arquivo, capital=capital, porte=porte, regime=regime, filiais=filiais,
            parceiro=parceiro, e_master=e_master, status=status, credito=credito, n_negocios=len(ds), ultimo=ultimo,
            ativa=ativa, situacao=situ or "não encontrado", passivo=passivo, fator_base=fator, cresc=cresc,
            link=PD.LINK.format(top["id"]), deal_id=top["id"], motivos="; ".join(motivos), perguntas=" ".join(perg)))
    linhas.sort(key=lambda x: ({"A": 0, "B": 1, "C": 2}[x["faixa"]], -x["score"], -(x["fat"] or 0)))
    meta = dict(download=os.path.basename(caminho), baixado_em=H.get("baixado_em"), receita=meta_rf.get("fonte"),
                negocios_ganhos_abertos=sum(1 for d in negs if d["status"] in ("ganho", "aberto")), sem_cnpj=sem_cnpj,
                empresas=len(linhas), negocios_com_fat_parecer=len(fat_par),
                ratio_credito_fat=dict(n=len(ratios), n_cafe=len(r_cafe), p75_cafe=ratio_cafe, mediana_cafe=r_cafe[len(r_cafe) // 2] if r_cafe else None, p75_usado=med_ratio, mediana=ratios[len(ratios) // 2] if ratios else None,
                                       p25=ratios[len(ratios) // 4] if ratios else None, p75=ratios[3 * len(ratios) // 4] if ratios else None))
    return linhas, meta


# ---------- saídas ----------
COLS = [("Faixa", "faixa", 7), ("Score", "score", 7), ("Empresa", "empresa", 42), ("CNPJ", "cnpj_fmt", 20),
        ("UF", "uf", 5), ("Cidade", "cidade", 20), ("Região (MG)", "regiao", 15), ("Setor", "setor", 30), ("CNAE principal", "cnae_txt", 44),
        ("Exportador (s/n/provável)", "exportador", 12), ("Sinal de exportação", "exp_motivo", 34),
        ("Faturamento estimado (R$/ano)", "fat", 18), ("Fonte da estimativa", "fat_fonte", 34), ("Confiança", "fat_conf", 11),
        ("Capital social (R$)", "capital", 16), ("Porte (Receita)", "porte", 14), ("Regime", "regime", 14),
        ("Estab. ativos (base local)", "filiais", 10), ("Parceiro", "parceiro", 22), ("Status na Save", "status", 10),
        ("Crédito recuperado / valor do negócio (R$)", "credito", 18), ("Último negócio", "ultimo", 12),
        ("Situação na Receita", "situacao", 12), ("Link do HubSpot", "link", 22),
        ("Por que está aqui", "motivos", 70), ("O que perguntar", "perguntas", 80),
        ("Pontos: faturamento/30", "p_fat", 9), ("setor/20", "p_setor", 8), ("exportador/10", "p_exp", 8),
        ("capital e porte/15", "p_cap", 8), ("relacionamento/15", "p_rel", 8), ("necessidade/10", "p_nec", 8),
        ("Trecho do parecer (faturamento)", "fat_trecho", 60)]


def cnpj_fmt(c):
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}" if len(c) == 14 else c


def gravar_xlsx(L, M, destino):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    wb = Workbook()
    ws = wb.active; ws.title = "Base priorizada"
    hdr_fill = PatternFill("solid", fgColor="1F3864")
    cor = {"A": "C6EFCE", "B": "FFEB9C", "C": "F2F2F2"}
    ws.append([c[0] for c in COLS])
    for i, (t, _, w) in enumerate(COLS, 1):
        cel = ws.cell(row=1, column=i)
        cel.font = Font(bold=True, color="FFFFFF"); cel.fill = hdr_fill
        cel.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 45
    for l in L:
        l = dict(l, cnpj_fmt=cnpj_fmt(l["cnpj"]), cnae_txt=f"{l['cnae']} · {l['cnae_desc']}".strip(" ·"),
                 p_fat=l["pontos"]["faturamento"], p_setor=l["pontos"]["setor"], p_exp=l["pontos"]["exportador"],
                 p_cap=l["pontos"]["capital_porte"], p_rel=l["pontos"]["relacionamento"], p_nec=l["pontos"]["necessidade"],
                 fat=round(l["fat"]) if l["fat"] else None, capital=l["capital"] or None, credito=round(l["credito"] or 0))
        ws.append([l[k] for _, k, _ in COLS])
        rw = ws.max_row
        ws.cell(row=rw, column=1).fill = PatternFill("solid", fgColor=cor[l["faixa"]])
        lk = ws.cell(row=rw, column=[k for _, k, _ in COLS].index("link") + 1)
        lk.hyperlink = l["link"]; lk.value = "abrir no HubSpot"; lk.font = Font(color="0563C1", underline="single")
        for k in ("fat", "capital", "credito"):
            ws.cell(row=rw, column=[c[1] for c in COLS].index(k) + 1).number_format = '#,##0'
        for k in ("motivos", "perguntas", "fat_trecho"):
            ws.cell(row=rw, column=[c[1] for c in COLS].index(k) + 1).alignment = Alignment(wrap_text=False)
    ws.freeze_panes = "D2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(COLS))}{ws.max_row}"

    m = wb.create_sheet("Metodologia")
    txt = [
        ["Crédito internacional · base de clientes priorizada", ""],
        ["Gerado em", f"{date.today().isoformat()} · Intel Comercial + Dados (rascunho para o Luis)"],
        ["HubSpot", f"{M['download']} (baixado em {M['baixado_em']}) · negócios ganhos e abertos, 1 linha por raiz de CNPJ"],
        ["Receita", f"{M['receita']} · base local, somente leitura"],
        ["Pareceres", "celulas/geovana/pareceres (textos e resumos.json) · extrator de faturamento por padrões"],
        ["", ""],
        ["Score (0–100)", "Faturamento estimado 30 · Setor prioritário 20 · Exportador 10 · Capital e porte 15 · Relacionamento 15 · Necessidade de capital 10"],
        ["Faturamento (30)", "≥ R$ 50 mi 30 · ≥ 30 mi 24 · ≥ 15 mi 14 · ≥ 5 mi 6; × confiança da fonte (parecer anual/série 1,0 · parecer média 0,9 · HubSpot à mão 0,7 · proxy do crédito 0,4)"],
        ["Setor (20)", "Prioritário 20 (café, agro/produtores/insumos, usinas, frigoríficos de abate, construtoras, máquinas) · adjacente 10 (carnes atacado, indústria de alimentos e bebidas, distribuição de combustíveis) · outros 0"],
        ["Exportador (10)", "s = parecer cita receita de exportação ou razão social cita exportação (10) · provável = CNAE de cadeia exportadora ou razão social cita importação (5) · n = sem sinal (0)"],
        ["Capital e porte (15)", "Capital ≥ 10 mi 9 · ≥ 5 mi 7 · ≥ 1 mi 5 · ≥ 300 mil 2; porte Demais +3; Lucro Real +1; estabelecimentos ativos ≥ 3 +2 (2 = +1)"],
        ["Relacionamento (15)", "Ganho 8 (aberto 3) · parceiro Master do roster +4 · negócio nos últimos 18 meses +3"],
        ["Necessidade (10)", "Débito tributário citado no parecer ≥ 1 mi 5 · ≥ 100 mil ou citado sem valor 3 · menor 1; crescimento (série ≥ +30% ou base 1,3x) +3; ≥ 3 estabelecimentos +2"],
        ["Faixa A", "Score ≥ 55 E sinal de porte grande (faturamento ≥ R$ 30 mi de parecer/HubSpot, faturamento proxy ≥ 50 mi ou capital ≥ R$ 5 mi) E CNPJ ativo"],
        ["Faixa B", "Score ≥ 45, ou porte Demais em setor prioritário, ou capital ≥ R$ 1 mi, ou faturamento estimado ≥ R$ 30 mi (e não A)"],
        ["Faixa C", "Demais, ou CNPJ não ativo"],
        ["Café", "Café está FORA da meta de recuperação de créditos desde abr/2026, mas é setor PRIORITÁRIO para o crédito internacional."],
        ["Faturamento do HubSpot", "Os valores 20.000.000 / 4.800.000 / 3.600.000 repetem o porte (importação) e foram descartados; só valores preenchidos à mão entram."],
        ["Proxy do crédito", f"Crédito recuperado ÷ faturamento anual nos {M['ratio_credito_fat']['n']} negócios ganhos com os dois dados: mediana {M['ratio_credito_fat']['mediana']:.3f}, p25 {M['ratio_credito_fat']['p25']:.3f}, p75 {M['ratio_credito_fat']['p75']:.3f}. Café ({M['ratio_credito_fat']['n_cafe']} casos): p75 {M['ratio_credito_fat']['p75_cafe']:.3f}. Usado o p75 sobre o MAIOR crédito de um único negócio (faturamento estimado menor, conservador). Dispersão alta: serve para ordenar, não para afirmar faturamento; vale no máximo 12 dos 30 pontos."],
        ["LGPD e canal", "Uso interno. Sem sócios nem CPF. O cliente é do parceiro Master: abordagem passa pelo Master. Não enviar esta lista a terceiros."],
    ]
    for row in txt: m.append(row)
    m.column_dimensions["A"].width = 26; m.column_dimensions["B"].width = 150
    m["A1"].font = Font(bold=True, size=13)
    for r in range(2, m.max_row + 1): m.cell(row=r, column=1).font = Font(bold=True)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    wb.save(destino)


def agregados(L, M):
    c = collections.Counter
    out = dict(meta=M, faixas=c(l["faixa"] for l in L))
    out["por_setor"] = {s: dict(c(l["faixa"] for l in L if l["setor"] == s)) for s in sorted({l["setor"] for l in L})}
    out["por_uf"] = {u: dict(c(l["faixa"] for l in L if l["uf"] == u)) for u in sorted({l["uf"] for l in L})}
    out["por_parceiro"] = {p: dict(c(l["faixa"] for l in L if l["parceiro"] == p)) for p in sorted({l["parceiro"] for l in L})}
    out["por_status"] = {s: dict(c(l["faixa"] for l in L if l["status"] == s)) for s in ("ganho", "aberto")}
    out["fonte_fat"] = {f: dict(c(l["faixa"] for l in L if l["fat_fonte"].split(" (")[0].split(":")[0] == f))
                        for f in sorted({l["fat_fonte"].split(" (")[0].split(":")[0] for l in L})}
    out["exportador"] = {e: dict(c(l["faixa"] for l in L if l["exportador"] == e)) for e in ("s", "provável", "n")}
    out["cafe"] = dict(c(l["faixa"] for l in L if l["setor"] == "Café"))
    out["cafe_regiao"] = {g: dict(c(l["faixa"] for l in L if l["setor"] == "Café" and (l["regiao"] or l["uf"]) == g)) for g in sorted({(l["regiao"] or l["uf"]) for l in L if l["setor"] == "Café"})}
    out["regiao_mg"] = {g: dict(c(l["faixa"] for l in L if l["regiao"] == g)) for g in sorted({l["regiao"] for l in L if l["regiao"]})}
    out["setor_prioritario"] = {k: dict(c(l["faixa"] for l in L if l["setor_pr"] == v)) for k, v in (("prioritário", 2), ("adjacente", 1), ("outro", 0))}
    out["A_por_fonte_e_capital"] = dict(c((l["fat_fonte"].split(":")[0].split(" (")[0] + " · " + ("cap≥5mi" if l["capital"] >= 5e6 else "cap<5mi")) for l in L if l["faixa"] == "A"))
    out["A_credito_max_gt50"] = sum(1 for l in L if l["faixa"] == "A" and "ATENÇÃO" in l["motivos"])
    out["parceiro_cafe_A"] = dict(c(l["parceiro"] for l in L if l["faixa"] == "A" and l["setor"] == "Café"))
    out["porte"] = dict(c(l["porte"] or "não encontrado" for l in L))
    out["situacao"] = dict(c(l["situacao"] for l in L))
    out["fat_parecer_faixas"] = dict(c(("≥50 mi" if l["fat"] >= 50e6 else "30–50 mi" if l["fat"] >= 30e6 else "15–30 mi" if l["fat"] >= 15e6 else "5–15 mi" if l["fat"] >= 5e6 else "<5 mi")
                                       for l in L if l["fat_fonte"].startswith("Parecer")))
    out["capital_faixas"] = dict(c(("≥10 mi" if l["capital"] >= 10e6 else "5–10 mi" if l["capital"] >= 5e6 else "1–5 mi" if l["capital"] >= 1e6 else "<1 mi") for l in L))
    out["A_master_vs_fora"] = dict(c(("Master" if l["e_master"] else "fora do roster") for l in L if l["faixa"] == "A"))
    out["score_medio"] = {f: round(sum(l["score"] for l in L if l["faixa"] == f) / max(1, sum(1 for l in L if l["faixa"] == f)), 1) for f in "ABC"}
    out["credito_total_por_faixa"] = {f: round(sum(l["credito"] for l in L if l["faixa"] == f)) for f in "ABC"}
    out["passivo_A"] = sum(1 for l in L if l["faixa"] == "A" and l["passivo"] is not None and (l["passivo"] >= 1e5 or l["passivo"] == -1))
    return out


if __name__ == "__main__":
    L, M = montar()
    area = subprocess.run([sys.executable, os.path.join(AP, "lib/caminhos.py"), "credito"], capture_output=True, text=True, check=True).stdout.strip()  # sem a pasta do OneDrive, para (antes gravava no diretório atual)
    destino = os.path.join(area, "Credito-Internacional-Base-Priorizada.xlsx")
    gravar_xlsx(L, M, destino)
    shutil.copy2(destino, os.path.join(PASTA, "Credito-Internacional-Base-Priorizada.xlsx"))
    ag = agregados(L, M)
    json.dump(ag, open(os.path.join(PASTA, "scripts", "base-clientes-agregados.json"), "w"), ensure_ascii=False, indent=1, default=str)
    if "--amostra" in sys.argv:   # conferência (só no terminal)
        for l in [x for x in L if x["faixa"] == "A"][:40]:
            print(l["faixa"], l["score"], l["empresa"][:38], l["uf"], l["setor"][:22], l["exportador"], f"{(l['fat'] or 0)/1e6:.1f}", l["fat_fonte"][:22], l["fat_conf"], f"{l['capital']/1e6:.1f}", l["porte"], l["parceiro"], l["status"], f"{l['credito']/1e6:.2f}", l["pontos"])
    print(json.dumps(ag, ensure_ascii=False, indent=1, default=str))
    print("planilha:", destino)
