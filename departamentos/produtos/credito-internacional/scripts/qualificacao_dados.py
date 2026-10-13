"""Crédito internacional · pré-qualificação da base pelos DADOS (Intel Comercial + Dados + Partner Success, 06/10/2026).

Aplica a cada empresa da base priorizada (1.007, uma por raiz de CNPJ) o que os dados JÁ permitem verificar,
critério a critério, com o status CONFIRMADO / ESTIMADO / DESCONHECIDO. Somente leitura e local:
planilhas da pasta do produto, último download do HubSpot e Receita (base local via partners_dados.receita()).
Nenhum CNPJ sai da máquina; não lê .env; não grava no HubSpot.

Uso:  from qualificacao_dados import montar  ->  (linhas, meta)
"""
import collections, json, os, re, sys
from datetime import date

sys.path.insert(0, os.path.expanduser("~/agentes-partners/lib"))
import partners_dados as PD
import openpyxl

PASTA = os.path.join(PD.AP, "departamentos/produtos/credito-internacional")
DEFAULT_FAT = {"20000000", "3600000", "4800000"}   # o HubSpot repete esses valores por porte (importação)
DOLAR = 5.22                                        # 02/10/2026 (documento oficial, seção 12)
CORTE_FAT = 50e6                                    # critério oficial: a partir de cerca de R$ 50 mi/ano
PISO_FAT = 30e6                                     # abaixo disto, comprovado, é eliminatório (proposta, validar com o João)
INICIO_MAX = "20240101"                             # sem 2024 completo não há 2 anos de demonstrações (2024 e 2025)

C, E, D = "CONFIRMADO", "ESTIMADO", "DESCONHECIDO"
CA, CE, CP = C + ": atende", C + ": elimina", C + ": parcial"   # o status diz também o sentido da confirmação

ADERENCIA = {  # setor da base -> (nível, motivo)  casos em teste: construtora, agro, hortifruti, indústria
    "Café": ("alta", "café/agro: setor prioritário, caso parecido com o agro em teste"),
    "Agro, produtores e insumos agropecuários": ("alta", "agro: caso parecido com o agro em teste; terra é garantia natural"),
    "Construtoras e incorporadoras": ("alta", "construtora: caso de referência e 3 construtoras em conversa"),
    "Frigoríficos (abate/indústria de carnes)": ("alta", "indústria de carnes, exportadora típica"),
    "Usinas (açúcar/etanol)": ("alta", "agroindústria exportadora"),
    "Máquinas e equipamentos": ("média", "indústria/comércio de bens de capital: sem caso em teste"),
    "Indústria de alimentos e bebidas": ("média", "indústria: parecido com a indústria em teste"),
    "Carnes · atacado": ("média", "cadeia de carnes, sem caso em teste"),
    "Combustíveis · distribuição/atacado": ("média", "distribuição: giro alto, garantia a provar"),
    "Atacado de alimentos e mercadorias": ("baixa", "atacado: margem curta, garantia a provar"),
    "Supermercados e varejo alimentar": ("baixa", "varejo: sem caso em teste, receita em reais"),
    "Postos de combustíveis": ("baixa", "varejo de combustível: sem caso em teste"),
    "Transporte e logística": ("baixa", "serviço, sem caso em teste"),
    "Outros": ("baixa", "setor sem caso em teste"),
    "Sem CNAE": ("baixa", "sem CNAE"),
}


def _ler(arquivo, aba):
    ws = openpyxl.load_workbook(os.path.join(PASTA, arquivo), read_only=True)[aba]
    linhas = list(ws.iter_rows(values_only=True))
    h = {k: i for i, k in enumerate(linhas[0])}
    return h, linhas[1:]


def _fat_ganhos():
    """Faturamento lido nos pareceres dos ganhos (Faturamento-Clientes-Ganhos.xlsx), por raiz."""
    h, rows = _ler("Faturamento-Clientes-Ganhos.xlsx", "Faturamento dos ganhos")
    out = {}
    for r in rows:
        rz = PD.raiz(r[h["CNPJ"]])
        if not rz or r[h["faturamento anual (R$)"]] is None: continue
        out[rz] = dict(valor=float(r[h["faturamento anual (R$)"]]), ano=r[h["ano de referência"]], conf=r[h["confiança"]],
                       metodo=r[h["método"]] or "", checagens=r[h["checagens"]] or "", fonte="parecer técnico (Faturamento-Clientes-Ganhos)")
    return out


def _fat_lookalike():
    """Faturamento REAL de parecer nos perdidos semelhantes (só 'parecer (alta|média)'), por raiz."""
    h, rows = _ler("Lookalike-Perdidos.xlsx", "Perdidos semelhantes")
    out = {}
    for r in rows:
        if not str(r[h["fonte do faturamento"]] or "").startswith("parecer"): continue
        rz = PD.raiz(r[h["CNPJ"]])
        conf = "alta" if "alta" in r[h["fonte do faturamento"]] else "média"
        out[rz] = dict(valor=float(r[h["faturamento estimado (R$ mi)"]]) * 1e6, ano=None, conf=conf, metodo="parecer do negócio perdido",
                       checagens="", fonte="parecer técnico de negócio perdido (Lookalike-Perdidos)")
    return out


def _hubspot():
    caminho, dados = PD.ultimo_download()
    por = collections.defaultdict(list)
    for n in dados["negocios"]:
        rz = PD.raiz((n.get("extras") or {}).get("cnpj"))
        if rz: por[rz].append(n)
    return os.path.basename(caminho), dados.get("baixado_em"), por


def _faixa_fat(v):
    return "≥ R$ 50 mi" if v >= CORTE_FAT else "R$ 30–50 mi" if v >= PISO_FAT else "< R$ 30 mi"


def montar():
    hb, rows = _ler("Credito-Internacional-Base-Priorizada.xlsx", "Base priorizada")
    fg, fl = _fat_ganhos(), _fat_lookalike()
    hs_arq, hs_em, hs = _hubspot()
    linhas, sem_receita = [], 0
    for r in rows:
        g = lambda k: r[hb[k]]
        cnpj = g("CNPJ"); rz = PD.raiz(cnpj)
        rec = PD.receita(cnpj)
        if rec is None: sem_receita += 1
        elif rec.get("matriz") != "matriz":                       # filial: idade e porte são os da matriz
            rec = PD.receita(rz + "000000") or rec
        negs = hs.get(rz, [])
        st = "ganho" if any(n["status"] == "ganho" for n in negs) else "aberto" if any(n["status"] == "aberto" for n in negs) else ("perdido" if negs else "não encontrado")
        ultimo = max((PD.data_efetiva(n) or "" for n in negs), default="")
        passivo = any(n["pipeline"] == "Gestão de Passivo" for n in negs)
        link = next((PD.LINK.format(n["id"]) for n in sorted(negs, key=lambda n: (n["status"] != "ganho", n["status"] != "aberto"))), "")
        setor = g("Setor") or "Sem CNAE"
        nome = (rec or {}).get("razao") or g("Empresa")
        L = dict(empresa=nome, cnpj=cnpj, uf=g("UF"), cidade=g("Cidade"), setor=setor, parceiro=g("Parceiro"),
                 status_hs=st, ultimo=ultimo, faixa_base=g("Faixa"), score_base=g("Score"), link=link)
        ko, falta = [], []

        # K6 · situação cadastral (Receita)
        if rec is None:
            L["sit"] = (D, "CNPJ não encontrado na base local da Receita (2026-09)")
        elif rec["situacao"] == "Ativa":
            L["sit"] = (CA, "Ativa (Receita 2026-09)")
        else:
            L["sit"] = (CE, f"{rec['situacao']} desde {rec['data_situacao'] or '?'} (Receita 2026-09)"); ko.append(f"situação cadastral {rec['situacao']}")

        # K7 · recuperação judicial / falência (pelo nome: a lei manda acrescentar 'em recuperação judicial'; ausência não comprova)
        rn = PD.norm(nome).upper()
        if re.search(r"RECUPERACAO JUDICIAL|EM RECUPERACAO|MASSA FALIDA|\bFALID[AO]\b|EM LIQUIDACAO", rn):
            L["rj"] = (CE, "o nome na Receita indica recuperação judicial, falência ou liquidação"); ko.append("recuperação judicial/falência no nome")
        else:
            L["rj"] = (D, "sem indicação no nome (não comprova: perguntar na camada 1 e checar certidão na camada 3)")

        # K3 · 2 anos de demonstrações: idade é condição necessária; o documento em si é desconhecido
        ini = (rec or {}).get("inicio") or ""
        if ini and ini > INICIO_MAX:
            L["doc"] = (CE, f"aberta em {ini[6:8]}/{ini[4:6]}/{ini[:4]}: não tem 2024 e 2025 completos"); ko.append("menos de 2 anos de demonstrações (data de abertura)")
        else:
            idade = f"aberta em {ini[:4]}" if ini else "data de abertura desconhecida"
            sinal = "; Lucro Real (obriga ECD com balanço e DRE): provável" if (g("Regime") == "Lucro Real") else ""
            L["doc"] = (D, f"{idade}{sinal}; DRE e balanço de 2024–2025 não vistos")

        # K8 + critério 1 · porte (faturamento)
        simples = (rec or {}).get("simples") == "S" or (rec or {}).get("mei") == "S"
        fat = fg.get(rz) or fl.get(rz)
        if simples:
            L["fat"] = (CE, "optante do Simples/MEI na Receita: receita bruta legal até R$ 4,8 mi/ano", None)
            ko.append("Simples Nacional/MEI (receita até R$ 4,8 mi)")
        elif fat:
            v = fat["valor"]
            m = re.search(r"seria R\$ ([\d.,]+) mi", fat["checagens"])
            if m: v = min(v, float(m.group(1).replace(",", ".")) * 1e6)      # leitura alternativa: fica a menor
            ambiguo = any(x in fat["checagens"] for x in ("Vlr Operação", "rótulo mensal/anual ausente", "conferir;"))
            recente = fat["ano"] is None or int(fat["ano"]) >= 2023
            ano = f", ano {fat['ano']}" if fat["ano"] else ""
            if fat["conf"] in ("alta", "média") and recente and not ambiguo:
                L["fat"] = (CA if v >= CORTE_FAT else CP if v >= PISO_FAT else CE, f"{_faixa_fat(v)}: R$ {v/1e6:.1f} mi ({fat['fonte']}{ano}, confiança {fat['conf']})", v)
                if v < PISO_FAT: ko.append(f"faturamento comprovado de R$ {v/1e6:.1f} mi{ano} (abaixo de R$ 30 mi)")
            else:
                motivo = "ano antigo" if not recente else "leitura ambígua" if ambiguo else f"confiança {fat['conf']}"
                L["fat"] = (E, f"{_faixa_fat(v)}: R$ {v/1e6:.1f} mi ({fat['fonte']}{ano}; {motivo})", v)
        else:
            hsv = [n["extras"].get("faturamento") for n in negs if n["extras"].get("faturamento") and n["extras"]["faturamento"] not in DEFAULT_FAT]
            hsv = [float(x) for x in hsv if 1e5 < float(x) < 5e9]
            if hsv:
                v = max(hsv); L["fat"] = (E, f"{_faixa_fat(v)}: R$ {v/1e6:.1f} mi (HubSpot, preenchido à mão, sem documento)", v)
            elif g("Faturamento estimado (R$/ano)"):
                v = float(g("Faturamento estimado (R$/ano)"))
                L["fat"] = (E, f"{_faixa_fat(v)}: R$ {v/1e6:.1f} mi (proxy pelo crédito recuperado: só ordena)", v)
            else:
                L["fat"] = (D, "sem dado de faturamento", None)
        porte_rf = (rec or {}).get("porte") or g("Porte (Receita)") or "?"
        capital = (rec or {}).get("capital") or g("Capital social (R$)") or 0

        # critérios que os dados NÃO alcançam
        L["nec"] = (D, "necessidade e finalidade só na conversa (camada 1)")
        L["gar"] = (D, "garantias livres não constam em base alguma (camada 1 e 3)")
        L["moeda"] = (D, "aceite de moeda estrangeira e de liberação por etapas: só na conversa")
        L["prazo"] = (D, "horizonte de tempo: só na conversa")

        # critério 6 · hedge natural
        sx = g("Sinal de exportação") or "sem sinal"
        L["exp"] = ((CA, f"parecer técnico cita exportação ({sx.split(':',1)[-1].strip()}); percentual desconhecido") if sx.startswith("parecer")
                    else (E, "razão social cita exportação (não prova exportação atual)") if "razão social cita exportação" in sx
                    else (E, "CNAE de cadeia exportadora (sinal fraco)") if "CNAE" in sx else (D, "sem sinal de exportação"))

        # critério 11 · aderência à entrega
        nivel, mot = ADERENCIA.get(setor, ("baixa", "setor sem caso em teste"))
        if "HORTIFRUTI" in rn: nivel, mot = "alta", "hortifruti: caso parecido com o hortifruti em teste"
        L["ader"] = (E, f"{nivel}: {mot}"); L["ader_nivel"] = nivel

        # sinais de atenção (não eliminam; vão para a camada 3)
        sinais = []
        if "débitos tributários" in (g("Por que está aqui") or ""): sinais.append("parecer cita débitos tributários (CND e parcelamentos na camada 3)")
        if passivo: sinais.append("tem negócio no pipeline Gestão de Passivo (passivo tributário)")
        if porte_rf in ("Microempresa", "ME", "Empresa de Pequeno Porte", "EPP"): sinais.append(f"porte {porte_rf} na Receita (declaratório, costuma estar desatualizado)")
        if st == "perdido": sinais.append("no HubSpot de hoje todos os negócios estão perdidos")
        L["sinais"] = "; ".join(sinais)
        L["porte_rf"], L["capital"] = porte_rf, capital

        # resultado
        fs, ftxt, fv = L["fat"]
        if ko:
            L["resultado"] = "Descartada por eliminatório já conhecido"; L["motivo"] = "; ".join(ko); L["prior"] = "—"
        elif L["sit"][0] == CA and fs == CA and fv is not None and fv >= CORTE_FAT:
            L["resultado"] = "Pré-qualificada pelos dados"
            L["motivo"] = "passa em tudo o que os dados verificam (ativa, 2+ anos, faturamento ≥ R$ 50 mi comprovado). Falta: necessidade ≥ US$ 5 mi, garantia ≈ 2x, moeda, prazo"
            L["prior"] = "Camada 1 já"
        else:
            L["resultado"] = "Depende da camada 1"
            est = fv or 0
            if (fs.startswith(C) and est >= PISO_FAT) or (est >= CORTE_FAT and nivel in ("alta", "média") and porte_rf == "Demais") or L["faixa_base"] == "A":
                L["prior"] = "Alta"
            elif est >= PISO_FAT or L["faixa_base"] == "B" or (porte_rf == "Demais" and nivel == "alta") or capital >= 1e6:
                L["prior"] = "Média"
            else:
                L["prior"] = "Baixa"
            falta = []
            if not fs.startswith(C): falta.append("faturamento comprovado (só há estimativa)" if fs == E else "faturamento")
            elif est < CORTE_FAT: falta.append("faturamento comprovado está entre R$ 30 e 50 mi (exceção só com o João, ou DRE de 2025 maior)")
            if L["sit"][0] != CA: falta.append("situação cadastral")
            L["motivo"] = "falta: " + "; ".join(falta + ["necessidade", "garantia", "moeda", "prazo"])
        L["n"] = collections.Counter(L[k][0].split(":")[0] for k in ("sit", "rj", "doc", "fat", "nec", "gar", "moeda", "prazo", "exp", "ader"))
        linhas.append(L)
    meta = dict(hubspot=hs_arq, hubspot_em=hs_em, receita="Receita Federal · Dados Abertos do CNPJ · 2026-09 (base local)",
                sem_receita=sem_receita, gerado=date.today().isoformat())
    return linhas, meta


if __name__ == "__main__":
    linhas, meta = montar()
    print(meta)
    print(collections.Counter(l["resultado"] for l in linhas))
    print(collections.Counter((l["resultado"], l["prior"]) for l in linhas))
    mot = collections.Counter()
    for l in linhas:
        if l["resultado"].startswith("Desc"):
            for m in l["motivo"].split("; "): mot[re.sub(r"R\$ [\d.]+ mi(, ano \d+)?", "R$ X mi", re.sub(r"desde.*", "", m))] += 1
    print(mot)
    print(collections.Counter(l["fat"][0] for l in linhas))
    for l in linhas:
        if l["resultado"].startswith("Pré") or (l["fat"][0].startswith(C)): print(l["resultado"], l["empresa"][:35], l["fat"][1], l["faixa_base"])
