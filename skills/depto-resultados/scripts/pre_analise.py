#!/usr/bin/env python3
"""Pré-análise dos faróis do semáforo de gestão (pedido do Luis, 26/10/2026).

"Sobre os faróis, quero também que já venham com uma pré-análise dos agentes
responsáveis, para que eu tome sempre a melhor decisão."

Dois passos, toda segunda, depois do pacote_gestao.py:

  1. --preparar  lê o pacote-<data>.json e grava, em
     departamentos/resultados/pre-analise/<data>/, o CONTEXTO.md (meta do mês e do
     Q4, fontes, regras, formato) e o grupos.json (que área e especialista
     analisa cada métrica). O Controller aciona um subagente por grupo; cada um
     lê a skill e o especialista e grava <grupo>.json na mesma pasta.
  2. (padrão)    junta os <grupo>.json, confere contra as métricas do pacote,
     completa o que faltar com um item mecânico marcado "pendente" e grava
       registro/gestao/pre-analise-<data>.json  (contrato abaixo)
       registro/gestao/pre-analise-<data>.md    (leitura para o Luis, por bloco)

Contrato do JSON: {data, gerado_em, pacote, resumo, decisoes_luis[], itens:[{
  metrica_id, nome, bloco, status, valor, unidade, area, especialista, leitura,
  causa: {fatos[], hipoteses[]}, acoes[{acao, dono, prazo}], decisao_sugerida,
  efeito, confianca, melhorar_confianca, pendente}], avisos[], revisao}.
O infra/gestao.py junta por metrica_id: semaforo[i].pre_analise = item.

Sem nome de cliente; nada é enviado; HubSpot não é lido aqui.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

BASE = os.path.expanduser("~/agentes-partners")
GESTAO = os.path.join(BASE, "registro", "gestao")
ENTRADA = os.path.join(BASE, "departamentos", "resultados", "pre-analise")

ORDEM_STATUS = {"vermelho": 0, "amarelo": 1, "cinza": 2, "verde": 3}
NOME_BLOCO = {"resultado": "Resultado", "caixa": "Caixa", "risco": "Risco",
              "canal": "Canal", "operacao": "Operação"}
ORDEM_BLOCO = ["resultado", "caixa", "risco", "canal", "operacao"]

# Ids antigos do pacote (antes da D111) apontam para os novos.
ALIAS = {"meta_q4_credito_pct": "meta_q4_pct", "meta_q4_liquido_pct": None}

# Grupo (um subagente por grupo) → métricas com área e especialista donos.
GRUPOS = {
    "resultados": {"skills": ["depto-resultados"], "metricas": {
        "ganhos_mes_rs": ("depto-resultados", "metas-medicao-produto"),
        "ganhos_mes_n": ("depto-resultados", "forecast-pipeline"),
        "ganhos_semana_rs": ("depto-resultados", "forecast-pipeline"),
        "win_rate_3m": ("depto-resultados", "forecast-pipeline"),
        "ticket_3m": ("depto-resultados", "forecast-pipeline"),
        "meta_mes_pct": ("depto-resultados", "metas-medicao-produto"),
        "meta_q4_pct": ("depto-resultados", "metas-medicao-produto"),
        "volume_limpo_12m_rs": ("depto-resultados", "controladoria-receita"),
        "prob_real_x_configurada": ("depto-resultados", "forecast-pipeline")}},
    "dados-ti-qualidade": {"skills": ["depto-dados", "depto-ti", "depto-qualidade", "arquiteto-agentes"], "metricas": {
        "indice_qualidade_ganhos": ("depto-dados", "qualidade-saneamento"),
        "ganhos_sem_honorario_pct": ("depto-dados", "qualidade-saneamento"),
        "duplicados_grupos": ("depto-dados", "qualidade-saneamento"),
        "funil_por_produto": ("depto-dados", "governanca-dicionario"),
        "entregas_no_prazo_pct": ("depto-ti", "operacao-rotinas-custos"),
        "acerto_agentes_pct": ("arquiteto-agentes", "guardiao-padrao-senior"),
        "adocao_time_pct": ("arquiteto-agentes", "mentor-metodo")}},
    "canal": {"skills": ["celula-daniela", "depto-partner-success", "depto-operacoes-canal"], "metricas": {
        "masters_liquido_em_queda_rs": ("celula-daniela", "gestor-contas-chave"),
        "dependencia_top1_pct": ("celula-daniela", "gestor-contas-chave"),
        "tempo_resposta_parceiro_h": ("celula-daniela", "triagem-sla"),
        "margem_liquida_por_master_min": ("depto-operacoes-canal", "analista-comissionamento"),
        "consultores_dormentes": ("depto-partner-success", "analista-saude-churn"),
        "consultores_sem_2o_ganho": ("depto-partner-success", "coach-onboarding-enablement"),
        "masters_ativos_90d": ("depto-partner-success", "analista-saude-churn")}},
    "caixa": {"skills": ["depto-pos-venda", "depto-tributario", "depto-resultados"], "metricas": {
        "recebido_x_contratado": ("depto-resultados", "controladoria-receita"),
        "aging_per": ("depto-pos-venda", "ressarcimento-e-prazos"),
        "glosa_por_tese": ("depto-pos-venda", "compensacao-de-oficio-e-recebimento"),
        "decadencia_mensal_rs": ("depto-pos-venda", "ressarcimento-e-prazos"),
        "valor_em_janelas": ("depto-tributario", "reforma-saldos-credores")}},
    "comercial": {"skills": ["celula-jenifer", "depto-intel-comercial", "depto-solucoes", "recuperador"], "metricas": {
        "criados_mes_rs": ("celula-jenifer", "prospeccao-outbound"),
        "criados_mes_n": ("celula-jenifer", "qualificacao"),
        "clientes_2mais_produtos": ("depto-solucoes", "orquestrador-cross-sell"),
        "recuperador_decididos": ("recuperador", "triagem-de-perdidos"),
        "pipeline_parado_90d_rs": ("recuperador", "triagem-de-perdidos")}},
}
DONO = {m: (g, a, e) for g, v in GRUPOS.items() for m, (a, e) in v["metricas"].items()}

CAMPOS = ["metrica_id", "area", "especialista", "leitura", "causa", "acoes",
          "decisao_sugerida", "efeito", "confianca", "melhorar_confianca"]
PROMESSA = re.compile(r"\b(garant\w*|com certeza|sem risco|êxito certo|100% de êxito)\b", re.I)


def carregar_pacote(data):
    p = os.path.join(GESTAO, f"pacote-{data}.json")
    if not os.path.exists(p):
        sys.exit(f"pacote não encontrado: {p} (rode pacote_gestao.py --data {data})")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def brl(v):
    if v is None:
        return "—"
    if abs(v) >= 1e6:
        return f"R$ {v / 1e6:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {v:,.0f}".replace(",", ".")


def valor_fmt(m):
    v, u = m.get("valor"), m.get("unidade")
    if v is None:
        return "sem dado"
    if u == "R$":
        return brl(v)
    if u == "%":
        return f"{v:.1f}%".replace(".", ",")
    if u == "x":
        return f"{v:.2f}×".replace(".", ",")
    return f"{v:g} {u or ''}".strip()


# ---------------------------------------------------------------- preparar
def preparar(data, pacote):
    pasta = os.path.join(ENTRADA, data)
    os.makedirs(pasta, exist_ok=True)
    ids = [m["id"] for m in pacote["metricas"]]
    grupos = {}
    for g, v in GRUPOS.items():
        ms = [{"metrica_id": m, "area": a, "especialista": e,
               "status": next((x["status"] for x in pacote["metricas"] if x["id"] == m), "ausente")}
              for m, (a, e) in v["metricas"].items() if m in ids]
        grupos[g] = {"skills": v["skills"], "saida": os.path.join(pasta, f"{g}.json"), "metricas": ms}
    sem_dono = [m for m in ids if m not in DONO]
    if sem_dono:
        grupos["sem-dono"] = {"skills": ["depto-resultados"], "saida": os.path.join(pasta, "sem-dono.json"),
                              "metricas": [{"metrica_id": m, "area": "depto-resultados", "especialista": "forecast-pipeline"} for m in sem_dono]}
    with open(os.path.join(pasta, "grupos.json"), "w", encoding="utf-8") as f:
        json.dump(grupos, f, ensure_ascii=False, indent=2)

    meta = pacote.get("meta", {})
    mes = meta.get("mes_atual", {})
    linhas_meta = []
    if mes:
        linhas_meta.append(f"- Mês ({mes.get('nome')}): {brl(mes.get('realizado_rs'))} de {brl(mes.get('meta_rs'))} = {mes.get('pct')}% "
                           f"({mes.get('pct_do_proporcional')}% do proporcional); faltam {brl(mes.get('falta_rs'))} em "
                           f"{mes.get('dias_uteis_restantes')} dias úteis; ritmo necessário {brl(mes.get('ritmo_necessario_rs_dia'))}/dia útil × atual {brl(mes.get('ritmo_atual_rs_dia'))}.")
    for mm in meta.get("meses", []):
        linhas_meta.append(f"- {mm.get('nome')}: meta {brl(mm.get('meta_rs'))}, realizado {brl(mm.get('realizado_rs'))}, {mm.get('dias_uteis_total')} dias úteis.")
    linhas_meta.append(f"- Unidade: {meta.get('unidade')} ({meta.get('decisao', '')}).")
    texto = f"""# Contexto da pré-análise dos faróis · {data}

Gerado por pre_analise.py --preparar a partir de registro/gestao/pacote-{data}.json. O Controller aciona um subagente por grupo de grupos.json; cada um lê a skill da área e o especialista indicado e grava o JSON do grupo nesta pasta.

## Meta
{chr(10).join(linhas_meta)}

## Fontes (mesma pasta registro/gestao)
pacote-{data}.json (métricas com detalhe) · previsao-{data}.json (cenários, riscos, alavancas) · controle-{data}.json (desvios abertos com dono: referencie a regra, não duplique) · conselho/atas da semana · conselho/decisoes.md · infra/alcadas.md · departamentos/resultados/dados/metricas-{data}.json · departamentos/dados/dados-bi-{data}.json · registro/achados-areas-{data}.json.

## Regras
- Português do Brasil; números só dos arquivos, com fonte; separe fato de hipótese.
- Sem nome de cliente (Master pode). Não prometa valor, prazo ou êxito; alíquota zero só via PER; produto em validação só como descoberta.
- Alçada (infra/alcadas.md): ao Luis só regra, preço, meta, remuneração/repasse, produto em validação, material em escala, conflito de canal, > R$ 1 mi com decisão, risco jurídico/LGPD sem precedente. Senão decisao_sugerida = null. Decisão já pendente com ele: "Responder Dxxx".
- 1 a 3 ações com dono e prazo AAAA-MM-DD. Vermelho e amarelo: pré-análise completa; verde e cinza: leitura de 1 linha, 1 fato, 0–1 ação.
- HubSpot só leitura (use os JSON baixados); nunca leia .env; não edite nada além do JSON do grupo.

## Formato do <grupo>.json (lista)
[{{"metrica_id", "area", "especialista", "leitura", "causa": {{"fatos": [], "hipoteses": []}}, "acoes": [{{"acao", "dono", "prazo"}}], "decisao_sugerida", "efeito", "confianca": "alta|media|baixa", "melhorar_confianca"}}]
"""
    with open(os.path.join(pasta, "CONTEXTO.md"), "w", encoding="utf-8") as f:
        f.write(texto)
    print(f"ok: {pasta}/CONTEXTO.md e grupos.json ({sum(len(v['metricas']) for v in grupos.values())} métricas em {len(grupos)} grupos)")


# ---------------------------------------------------------------- juntar
def item_pendente(m):
    g, area, esp = DONO.get(m["id"], ("sem-dono", "depto-resultados", "forecast-pipeline"))
    return {"metrica_id": m["id"], "area": area, "especialista": esp,
            "leitura": f"{m.get('nome')}: {valor_fmt(m)} ({m.get('status')}). {m.get('nota') or ''}".strip(),
            "causa": {"fatos": [m.get("nota")] if m.get("nota") else [], "hipoteses": []},
            "acoes": [] if m.get("status") in ("verde", "cinza") else
            [{"acao": f"{area} completa a pré-análise desta métrica", "dono": f"gerente-{area.replace('depto-', '')}",
              "prazo": (dt.date.fromisoformat(m.get('_data')) + dt.timedelta(days=2)).isoformat()}],
            "decisao_sugerida": None, "efeito": None, "confianca": "baixa",
            "melhorar_confianca": "Pré-análise da área dona não chegou nesta edição.", "pendente": True}


def conferir(it, avisos):
    falta = [c for c in CAMPOS if c not in it]
    if falta:
        avisos.append(f"{it.get('metrica_id')}: faltam campos {falta}")
    if isinstance(it.get("causa"), str):
        it["causa"] = {"fatos": [it["causa"]], "hipoteses": []}
    it.setdefault("causa", {"fatos": [], "hipoteses": []})
    for a in it.get("acoes") or []:
        if not a.get("dono") or not re.match(r"\d{4}-\d{2}-\d{2}$", str(a.get("prazo", ""))):
            avisos.append(f"{it['metrica_id']}: ação sem dono ou prazo AAAA-MM-DD: {a.get('acao', '')[:60]}")
    if it.get("confianca") not in ("alta", "media", "baixa"):
        avisos.append(f"{it['metrica_id']}: confiança inválida ({it.get('confianca')})")
    if it.get("status") in ("vermelho", "amarelo") and not it.get("acoes"):
        avisos.append(f"{it['metrica_id']}: {it['status']} sem ação")
    texto = json.dumps(it, ensure_ascii=False)
    for achado in PROMESSA.finditer(texto):
        antes = texto[max(0, achado.start() - 14):achado.start()].lower()
        if re.search(r"\b(sem|não|nada|nem|nenhuma?)\s+(é\s+)?$", antes):
            continue  # negação ("sem garantia", "nada garantido")
        avisos.append(f"{it['metrica_id']}: possível promessa ('{achado.group(0)}'), passar no auditor de promessas")
        break


def juntar(data, pacote):
    pasta = os.path.join(ENTRADA, data)
    recebidos = {}
    avisos = []
    for f in sorted(glob.glob(os.path.join(pasta, "*.json"))):
        if os.path.basename(f) == "grupos.json":
            continue
        try:
            with open(f, encoding="utf-8") as fh:
                lista = json.load(fh)
        except Exception as e:  # noqa: BLE001
            avisos.append(f"{os.path.basename(f)} ilegível: {e}")
            continue
        for it in lista:
            mid = ALIAS.get(it.get("metrica_id"), it.get("metrica_id"))
            if mid is None:
                continue
            it["metrica_id"] = mid
            recebidos[mid] = it
    itens = []
    for m in pacote["metricas"]:
        base = {"nome": m.get("nome"), "bloco": m.get("bloco"), "status": m.get("status"),
                "valor": m.get("valor"), "unidade": m.get("unidade")}
        it = recebidos.pop(m["id"], None)
        if it is None:
            m["_data"] = data
            it = item_pendente(m)
            avisos.append(f"{m['id']}: sem pré-análise da área; item mecânico (pendente)")
        it = {**{"metrica_id": m["id"]}, **base, **{k: v for k, v in it.items() if k != "metrica_id"}}
        it.setdefault("pendente", False)
        conferir(it, avisos)
        itens.append(it)
    for mid in recebidos:
        avisos.append(f"{mid}: pré-análise sem métrica no pacote (ignorada)")
    itens.sort(key=lambda x: (ORDEM_BLOCO.index(x["bloco"]) if x["bloco"] in ORDEM_BLOCO else 9,
                              ORDEM_STATUS.get(x["status"], 9)))

    decisoes = []
    vistos = set()
    for it in sorted(itens, key=lambda x: ORDEM_STATUS.get(x["status"], 9)):
        d = it.get("decisao_sugerida")
        if not d:
            continue
        chave = re.findall(r"\bD\d{2,3}\b|\bC\d{2}\b", d)
        chave = chave[0] if chave and d.lower().startswith("responder") else d[:80]
        if chave in vistos:
            for x in decisoes:
                if x["chave"] == chave:
                    x["metricas"].append(it["metrica_id"])
            continue
        vistos.add(chave)
        decisoes.append({"chave": chave, "decisao": d, "efeito": it.get("efeito"),
                         "metricas": [it["metrica_id"]], "area": it["area"], "status": it["status"]})

    resumo = {s: sum(1 for i in itens if i["status"] == s) for s in ORDEM_STATUS}
    resumo["pendentes"] = sum(1 for i in itens if i.get("pendente"))
    resumo["confianca"] = {c: sum(1 for i in itens if i.get("confianca") == c) for c in ("alta", "media", "baixa")}
    areas = sorted({i["area"] for i in itens})
    saida = {"data": data, "gerado_em": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
             "_leia_me": "Pré-análise das áreas donas por métrica do semáforo (skills/depto-resultados/scripts/pre_analise.py). "
                         "infra/gestao.py junta por metrica_id em semaforo[i].pre_analise. Estimativas, não promessas; sem nome de cliente.",
             "pacote": f"pacote-{data}.json", "resumo": resumo, "decisoes_luis": decisoes,
             "itens": itens, "avisos": avisos,
             "revisao": {"gerente": "Controller de Resultados", "especialistas": sorted({f"{i['area']}/{i['especialista']}" for i in itens}),
                         "rodadas": 1, "areas_consultadas": areas, "aprovado": not any("faltam campos" in a for a in avisos),
                         "ajustes": "conferência automática de campos, dono, prazo, confiança e promessa; ids antigos da meta mapeados para a D111"}}
    os.makedirs(GESTAO, exist_ok=True)
    pj = os.path.join(GESTAO, f"pre-analise-{data}.json")
    with open(pj, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)
    pm = os.path.join(GESTAO, f"pre-analise-{data}.md")
    if not os.path.exists(pm) or "--md" in sys.argv:
        with open(pm, "w", encoding="utf-8") as f:
            f.write(markdown(saida, pacote))
    print(f"ok: {pj} ({len(itens)} itens; {resumo}); avisos: {len(avisos)}")
    for a in avisos:
        print("  -", a)


def primeira_frase(t):
    m = re.search(r"^(.+?\.)(\s+[A-ZÀ-Ú]|$)", t or "")
    return m.group(1) if m else (t or "")


def markdown(s, pacote):
    """Leitura de cerca de 2 páginas para o Luis, por bloco.

    Vermelho e amarelo: leitura, ação principal, decisão (se houver) e confiança.
    Verde e cinza: uma linha. O detalhe (fatos, hipóteses, todas as ações) fica no JSON.
    Se existir departamentos/resultados/pre-analise/<data>/sintese.md (escrito pelo
    Controller), ele entra no topo como leitura do Controller.
    """
    meta = pacote.get("meta", {})
    mes = meta.get("mes_atual", {})
    r = s["resumo"]
    L = [f"# Pré-análise dos faróis · {s['data']}", "",
         f"{r['vermelho']} vermelhos, {r['amarelo']} amarelos, {r['verde']} verdes e {r['cinza']} cinzas; "
         f"confiança {r['confianca']['alta']} alta, {r['confianca']['media']} média, {r['confianca']['baixa']} baixa. "
         "Pré-análise das áreas donas para a decisão; estimativas com premissa, nada é promessa. Detalhe (fatos, hipóteses, todas as ações): "
         f"`registro/gestao/pre-analise-{s['data']}.json`."]
    if mes:
        L.append(f"Meta do mês ({mes.get('nome')}, D111): {brl(mes.get('realizado_rs'))} de {brl(mes.get('meta_rs'))} ({str(mes.get('pct')).replace('.', ',')}%; "
                 f"faltam {brl(mes.get('falta_rs'))} em {mes.get('dias_uteis_restantes')} dias úteis).")
    sintese = os.path.join(ENTRADA, s["data"], "sintese.md")
    if os.path.exists(sintese):
        with open(sintese, encoding="utf-8") as f:
            L += ["", f.read().strip()]
    L += ["", "## Decisões sugeridas ao Luis", ""]
    for d in s["decisoes_luis"]:
        L.append(f"- {d['decisao']} _(faróis: {', '.join(d['metricas'])})_")
    for b in ORDEM_BLOCO:
        its = [i for i in s["itens"] if i["bloco"] == b]
        if not its:
            continue
        L += ["", f"## {NOME_BLOCO.get(b, b)}", ""]
        for i in its:
            cab = f"**{i['nome']}** · {valor_fmt(i)} · {i['status']}"
            if i["status"] in ("vermelho", "amarelo"):
                acao = (i.get("acoes") or [{}])[0]
                linha = f"- {cab}. {primeira_frase(i['leitura'])}"
                if acao:
                    linha += f" **Fazer:** {acao.get('acao')} ({acao.get('dono')}, {acao.get('prazo')})."
                if i.get("decisao_sugerida"):
                    linha += " **Decisão ao Luis** (acima)."
                linha += f" _Confiança {i['confianca']}._"
                L.append(linha)
            else:
                L.append(f"- {cab}. {primeira_frase(i['leitura'])}")
    if s["avisos"]:
        L += ["", "## Avisos da conferência", ""] + [f"- {a}" for a in s["avisos"]]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", default=dt.date.today().isoformat())
    ap.add_argument("--preparar", action="store_true", help="grava CONTEXTO.md e grupos.json para os subagentes")
    ap.add_argument("--md", action="store_true", help="regrava o .md mesmo se já existir (o Controller pode ter editado)")
    a = ap.parse_args()
    pacote = carregar_pacote(a.data)
    if a.preparar:
        preparar(a.data, pacote)
    else:
        juntar(a.data, pacote)


if __name__ == "__main__":
    main()
