"""Base da análise D&S: perfil dos clientes da planilha e universo de prospects (Receita local + HubSpot), sem chamada externa."""
import openpyxl, sqlite3, json, glob, re, collections, os, unicodedata, pickle, sys
sys.path.insert(0, os.path.expanduser("~/agentes-partners/lib")); from cnpj import normalizar_cnpj  # CNPJ alfanumérico (IN RFB 2.229/2024)
AP=os.path.expanduser("~/agentes-partners")
S = os.environ.get("PROSPECCAO_DS", os.path.expanduser("~/agentes-partners/departamentos/intel-comercial/prospeccao-ds"))  # dados (fora do repositório)
def norm(s): return re.sub(r"[^A-Z ]","",unicodedata.normalize("NFKD",str(s or "")).encode("ascii","ignore").decode().upper().replace("-"," ")).strip()
db=sqlite3.connect("file:"+AP+"/dados-publicos/receita/cnpj.sqlite?mode=ro",uri=True)
MUN=dict(db.execute("select codigo,descricao from ref where tipo='municipio'"))
CNAE=dict(db.execute("select codigo,descricao from ref where tipo='cnae'"))
NAT=dict(db.execute("select codigo,descricao from ref where tipo='natureza'"))
IB={(norm(m["municipio-nome"]),m["UF-sigla"]):m for m in json.load(open(S+"/ibge_mun.json"))}
ALIAS={("SANTA BARBARA DOESTE","SP"):("SANTA BARBARA D'OESTE","SP")}
def ibge(cod,uf):
    n=norm(MUN.get(cod,"")); return IB.get((n,uf)) or IB.get((n.replace(" D "," D"),uf))

# ── clientes da D&S (planilha) ──
F=os.environ.get("PLANILHA_MASTER", "/Users/luisfernandomelo/Library/CloudStorage/OneDrive-SAVECOMPANY/00 · Entrada/EMPRESAS DA D&S.xlsx")  # planilha de clientes do Master
lin=list(openpyxl.load_workbook(F,read_only=True,data_only=True).active.iter_rows(values_only=True))[1:]
# HubSpot: todos os negócios pela raiz
n=json.load(open(sorted(glob.glob(AP+"/departamentos/resultados/dados/hubspot-*.json"))[-1]))["negocios"]
HS=collections.defaultdict(list)
for d in n:
    c=normalizar_cnpj((d.get("extras") or {}).get("cnpj"))
    if c: HS[c.zfill(14)[:8]].append(d)
try: RES=json.load(open(AP+"/celulas/geovana/pareceres/resumos.json"))
except Exception: RES={}

def receita(c):
    e=db.execute("select cnpj,matriz,fantasia,situacao,inicio,cnae,cnaes_sec,uf,municipio,cep from estab where cnpj=?",(c,)).fetchone()
    if not e: return None
    m=db.execute("select razao,natureza,capital,porte from empresa where basico=?",(c[:8],)).fetchone() or (None,None,None,None)
    s=db.execute("select simples,mei from simples where basico=?",(c[:8],)).fetchone() or (None,None)
    ib=ibge(e[8],e[7])
    return {"cnpj":c,"matriz":e[1],"fantasia":e[2],"situacao":e[3],"abertura":e[4],"cnae":e[5],"cnae_desc":CNAE.get(e[5]),"cnaes_sec":e[6],
            "uf":e[7],"municipio":MUN.get(e[8]),"cep":e[9],"razao":m[0],"natureza":NAT.get(m[1]),"capital":m[2],"porte":m[3],
            "simples":s[0],"mei":s[1],"ibge":ib["municipio-id"] if ib else None,"regiao_imediata":ib["regiao-imediata-nome"] if ib else None,
            "regiao_imediata_id":ib["regiao-imediata-id"] if ib else None}

def hubspot(raiz):
    ds=HS.get(raiz,[]); g=[d for d in ds if d["status"]=="ganho" and d["pipeline"].startswith("RT")]
    # duplicidade de importação: mesmo dia de fechamento, criado depois do fechamento
    dia=collections.defaultdict(list); dup=set()
    for d in g: dia[d.get("fechado")].append(d)
    for k,v in dia.items():
        if k and len(v)>1:
            s=[d for d in v if (d.get("criado") or "")>k]; dup|={d["id"] for d in (s if len(s)<len(v) else s[1:])}
    v=[d for d in g if d["id"] not in dup]
    ex={}
    for d in sorted(ds,key=lambda d:d.get("criado") or "",reverse=True):
        for k,x in (d.get("extras") or {}).items():
            if k not in ex and x not in (None,"","None"): ex[k]=x
    teses=set()
    for d in ds:
        t=(RES.get(str(d["id"])) or {}).get("teses")
        if isinstance(t,dict): teses|={k for k,x in t.items() if isinstance(x,dict) and "abaixo" not in str(x.get("desfecho")) and "sem recolhimento" not in str(x.get("desfecho"))}
    hc=[float(d["hContr"]) for d in v if str(d.get("hContr")) not in ("None","")]
    return {"negocios":len(ds),"ganhos":len(v),"valor_ganho":round(sum(float(d.get("valor") or 0) for d in v),2),
            "primeiro_ganho":round(float(sorted(v,key=lambda d:d.get("fechado") or "")[0].get("valor") or 0),2) if v else None,
            "honorario_pct":round(sum(hc)/len(hc),3) if hc else None,"regime":ex.get("regime"),"faixa":ex.get("faixa_faturamento"),
            "parceiros":sorted({str(d.get("parceiro")) for d in ds if d.get("parceiro")}),"teses_feitas":sorted(teses),
            "link":f"https://app.hubspot.com/contacts/47865021/deal/{(v or ds)[-1]['id']}" if ds else None}

cli=[]
for r in lin:
    c=normalizar_cnpj(r[0]).zfill(14)
    if not c.strip("0"): continue
    x={"cnpj":c,"nome_planilha":r[1],"cidade_planilha":r[2],"uf_planilha":r[3],"fase":r[4],"id":r[5]}
    x["rf"]=receita(c); x["hs"]=hubspot(c[:8]); cli.append(x)
print("clientes",len(cli),"na Receita",sum(1 for x in cli if x["rf"]))

# ── universo de prospects ──
RAIZ_DS={x["cnpj"][:8] for x in cli}; RAIZ_HS=set(HS)
gan=[x for x in cli if x["fase"]=="Ganho" and x["rf"]]
cnae4=collections.Counter(x["rf"]["cnae"][:4] for x in gan)
regioes={x["rf"]["regiao_imediata_id"] for x in gan if x["rf"]["regiao_imediata_id"]}
cod_ok=set()
for cod,nome in MUN.items():
    pass
print("CNAE-4 dos ganhos:",len(cnae4),"regiões imediatas:",len(regioes))
pros=[]; conflito=0
q="""select e.cnpj,e.matriz,e.fantasia,e.inicio,e.cnae,e.cnaes_sec,e.uf,e.municipio,e.cep,m.razao,m.natureza,m.capital,m.porte,s.simples,s.mei
     from estab e left join empresa m on m.basico=e.basico left join simples s on s.basico=e.basico
     where e.situacao='Ativa' and e.matriz='matriz' and e.uf in (%s)""" % ",".join("'%s'"%u for u in {x["rf"]["uf"] for x in gan})
for e in db.execute(q):
    if e[4][:4] not in cnae4 or e[13]=="S" or e[14]=="S": continue
    ib=ibge(e[7],e[6])
    if not ib or ib["regiao-imediata-id"] not in regioes: continue
    if e[0][:8] in RAIZ_DS: continue
    if e[0][:8] in RAIZ_HS: conflito+=1; continue
    pros.append({"cnpj":e[0],"fantasia":e[2],"abertura":e[3],"cnae":e[4],"cnae_desc":CNAE.get(e[4]),"cnaes_sec":e[5],"uf":e[6],
                 "municipio":MUN.get(e[7]),"cep":e[8],"razao":e[9],"natureza":NAT.get(e[10]),"capital":e[11],"porte":e[12],"simples":e[13],
                 "ibge":ib["municipio-id"],"regiao_imediata":ib["regiao-imediata-nome"],"regiao_imediata_id":ib["regiao-imediata-id"]})
print("prospects",len(pros),"já no HubSpot (outro funil/parceiro, fora):",conflito)
print(collections.Counter(p["municipio"] for p in pros).most_common(10))
print("CEPs distintos:",len({p["cep"] for p in pros}), "nos municípios dos ganhos:",len({p["cep"] for p in pros if p["ibge"] in {x["rf"]["ibge"] for x in gan}}))
pickle.dump({"cli":cli,"pros":pros,"cnae4":cnae4},open(S+"/base.pkl","wb"))
