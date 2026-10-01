#!/usr/bin/env python3
"""Proposta de atualização de CRM (célula da Daniela) — nada é gravado no HubSpot.

Compara os campos de empresa/negócio do download do HubSpot com os dados oficiais da Receita
(base local da Inteligência Comercial, `cnpj.sqlite`, processada no próprio Mac) e com o que o
parceiro informou na conversa, e gera uma tabela "campo · valor atual · valor sugerido · fonte · ação"
para a Daniela aprovar e aplicar à mão no HubSpot.

Também faz a checagem de registro de oportunidade: o CNPJ já existe em outro negócio (duplicidade)
ou com outro parceiro (possível conflito de canal)?

Uso:
  python3 crm_checagem.py --negocio 64597193319
  python3 crm_checagem.py --negocio 64597193319 --informado faturamento="R$ 12 mi/ano" --origem "WhatsApp D&S 29/09"
  python3 crm_checagem.py --cnpj 12.345.678/0001-00          # empresa nova que o parceiro quer registrar
  python3 crm_checagem.py --master AGILE                      # todos os abertos do Master (só divergências)
  python3 crm_checagem.py --atualizar-receita ...              # antes, recruza HubSpot × Receita (local, sem download)
Não chama API, não lê .env. Dados de sócios, telefone e e-mail da Receita não são exibidos (LGPD).
"""
import argparse, importlib.util, os, subprocess, sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import CELULA, LINK, cnpj_digitos, fonte_hubspot, norm, receita, resolver_master, slug

RECEITA_PY = os.path.expanduser("~/.claude/skills/depto-intel-comercial/scripts/receita_cnpj.py")
# campos do HubSpot (nomes internos, ver mapeamento-hubspot.json) sem fonte oficial: de onde vem o dado certo
SEM_FONTE_OFICIAL = {
    "amount (valor do negócio)": ("valor", "diagnóstico/parecer do Técnico Tributário"),
    "honorarios_contratuais": ("hContr", "contrato assinado (área de Contratos)"),
    "honorarios_parceiro": ("hParc", "termo de parceria do Master (Luis / Operações de Canal)"),
    "teses_tributarias_aplicadas_neste_negocio_": ("variante", "parecer do Técnico Tributário"),
    "faturamento": ("x:faturamento", "parceiro ou cliente (documento contábil)"),
    "qual_e_o_regime_tributario_da_empresa_": ("x:regime", "parceiro ou cliente (ECF/DCTF); a Receita aberta não traz LR/LP"),
    "e_cac_liberado_": ("x:ecac", "parceiro/cliente (procuração e-CAC)"),
}
INFORMAVEIS = {"faturamento": "faturamento", "regime": "qual_e_o_regime_tributario_da_empresa_", "uf": "estado", "cidade": "cidade",
               "cnpj": "cnpj_", "ecac": "e_cac_liberado_", "valor": "amount", "tese": "teses_tributarias_aplicadas_neste_negocio_",
               "honorario": "honorarios_contratuais", "parceiro": "nome_do_parceiro"}


def cnpj_valido(c):
    c = cnpj_digitos(c)
    if len(c) != 14 or len(set(c)) == 1:
        return False
    def dv(base, pesos):
        s = sum(int(x) * p for x, p in zip(base, pesos)) % 11
        return "0" if s < 2 else str(11 - s)
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]; p2 = [6] + p1
    return c[12] == dv(c[:12], p1) and c[13] == dv(c[:12] + c[12], p2)


def receita_local(cnpj):
    """Consulta a base local da Receita (somente leitura). Retorna só campos cadastrais da empresa."""
    spec = importlib.util.spec_from_file_location("receita_cnpj", RECEITA_PY)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    if not os.path.exists(m.DB):
        return None, None
    meta = {r["chave"]: r["valor"] for r in m.q("SELECT * FROM meta")}
    r = m.q(m.VIEW + " WHERE e.cnpj=?", (cnpj_digitos(cnpj).zfill(14),))
    if not r:
        return meta.get("fonte"), None
    r = r[0]
    return meta.get("fonte"), {"cnpj": r["cnpj"], "razao": r["razao"], "situacao": r["situacao"], "cnae_oficial": r["cnae"],
                               "cnae_desc_oficial": r["cnae_desc"], "uf_oficial": r["uf"], "municipio_oficial": r["municipio"],
                               "porte_oficial": r["porte"], "simples": r["simples"], "capital_social": r["capital"], "inicio_atividade": r["inicio"]}


def tabela(cab, linhas):
    if not linhas:
        return "_Nada a propor._\n"
    return "| " + " | ".join(cab) + " |\n|" + "|".join("---" for _ in cab) + "|\n" + \
        "".join("| " + " | ".join(str(x if x not in (None, "") else "—").replace("|", "/") for x in l) + " |\n" for l in linhas)


def propostas(d, r, fonte_rf, informado, origem):
    """Linhas (campo, atual, sugerido, fonte, ação) para um negócio."""
    e = d["extras"]; L = []; alertas = []
    c = e.get("cnpj")
    if not cnpj_digitos(c):
        L.append(("cnpj_", "vazio", "—", "—", "Pedir o CNPJ ao parceiro (sem ele não há checagem oficial)"))
    elif not cnpj_valido(c):
        L.append(("cnpj_", c, "—", "cálculo do dígito verificador", "CNPJ inválido: confirmar com o parceiro"))
    if r:
        if (r.get("situacao") or "").lower() != "ativa":
            alertas.append(f"Situação cadastral na Receita: **{r['situacao']}**. Confirmar com o parceiro e o Técnico antes de seguir o negócio.")
        if r.get("uf_oficial") and e.get("uf") != r["uf_oficial"]:
            L.append(("estado", e.get("uf") or "vazio", r["uf_oficial"], fonte_rf, "Atualizar"))
        if r.get("municipio_oficial") and norm(e.get("cidade")) != norm(r["municipio_oficial"]):
            L.append(("cidade", e.get("cidade") or "vazio", r["municipio_oficial"].title(), fonte_rf, "Atualizar"))
        if r.get("cnae_oficial") and cnpj_digitos(d.get("cnae") or "") != r["cnae_oficial"]:
            L.append(("cnae", d.get("cnae") or "vazio", r["cnae_oficial"], fonte_rf, "Atualizar"))
        if r.get("cnae_desc_oficial") and norm(d.get("segmento")) != norm(r["cnae_desc_oficial"]):
            L.append(("descricao_do_cnae", d.get("segmento") or "vazio", r["cnae_desc_oficial"], fonte_rf, "Atualizar" if not d.get("segmento") else "Conferir (texto diferente)"))
        reg = norm(e.get("regime"))
        if r.get("simples") == "S" and "simples" not in reg:
            L.append(("qual_e_o_regime_tributario_da_empresa_", e.get("regime") or "vazio", "— (não sugerir)", fonte_rf + ": optante do Simples",
                      "Verificar com o parceiro: HubSpot diz outro regime"))
        if r.get("simples") in ("N", None) and "simples" in reg:
            L.append(("qual_e_o_regime_tributario_da_empresa_", e.get("regime"), "— (não sugerir)", fonte_rf + ": não consta no Simples",
                      "Verificar com o parceiro (LR ou LP?)"))
    ja_informados = {INFORMAVEIS.get(k, k) for k in informado}
    for rot, (k, onde) in SEM_FONTE_OFICIAL.items():
        if rot.split(" ")[0] in ja_informados: continue
        v = d.get(k) if not k.startswith("x:") else e.get(k[2:])
        vazio = v in (None, "", 0, 0.0)
        if vazio and (k != "hContr" and k != "hParc" and k != "variante" or d["status"] == "ganho"):
            L.append((rot, "vazio", "—", "sem fonte oficial", f"Obter em: {onde}"))
    for campo, valor in informado.items():
        L.append((INFORMAVEIS.get(campo, campo), "(ver HubSpot)", valor, origem or "informado na conversa (sem data)", "Atualizar se a Daniela confirmar"))
    return L, alertas


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--negocio"); g.add_argument("--cnpj"); g.add_argument("--master")
    ap.add_argument("--informado", action="append", default=[], help='campo=valor dito pelo parceiro (ex.: faturamento="R$ 12 mi")')
    ap.add_argument("--origem", help='de onde veio o --informado (ex.: "WhatsApp D&S 29/09")')
    ap.add_argument("--atualizar-receita", action="store_true", help="roda receita_cnpj.py --enriquecer antes (local)")
    ap.add_argument("--fonte"); a = ap.parse_args()
    if a.atualizar_receita:
        subprocess.run([sys.executable, RECEITA_PY, "--enriquecer"], check=True)
    f, D = fonte_hubspot(a.fonte); N = D["negocios"]; por_id = {d["id"]: d for d in N}
    fonte_rf, RF = receita()
    fonte_rf = (fonte_rf or "Receita (base local)").split(" (cruzamento")[0]
    inf = dict(x.split("=", 1) for x in a.informado)
    hoje = date.today().isoformat(); md = []; w = md.append
    w("# Proposta de atualização de CRM — rascunho para a Daniela aprovar")
    w(f"*{date.today().strftime('%d/%m/%Y')} · `crm_checagem.py` · HubSpot: `{os.path.basename(f)}` · Receita: {fonte_rf}. "
      "Nada foi gravado no HubSpot: a Daniela confere, aprova e aplica à mão. Valores sugeridos só com fonte.*\n")

    def mesmo_grupo(c, excluir=None):
        c = cnpj_digitos(c)[:8]
        return [x for x in N if c and cnpj_digitos(x["extras"].get("cnpj"))[:8] == c and x["id"] != excluir]

    def bloco_conflito(c, parceiro, excluir=None):
        H = mesmo_grupo(c, excluir)
        if not H:
            w("**Registro de oportunidade:** nenhum outro negócio do mesmo grupo (raiz do CNPJ) no HubSpot da Área Master.\n"); return
        w(f"**Registro de oportunidade:** {len(H)} outro(s) negócio(s) do mesmo grupo (raiz do CNPJ):")
        w(tabela(["Negócio", "Parceiro", "Status / etapa", "Criado", "Fechado", "Link"],
                 [(x["nome"], x["parceiro"], f"{x['status']} / {x['etapa']}", x["criado"], x["fechado"], f"[abrir]({LINK.format(x['id'])})") for x in sorted(H, key=lambda x: x["criado"])]))
        ab = [x for x in H if x["status"] == "aberto"]
        if parceiro is None and ab:
            w(f"⚠️ **Já existe negócio aberto do mesmo grupo** ({', '.join(sorted({x['parceiro'] for x in ab}))}). Não registrar outro sem checar duplicidade/conflito de canal com o Luis.\n")
        elif any(x["parceiro"] != parceiro for x in ab):
            w("⚠️ **Possível conflito de canal:** negócio aberto do mesmo grupo com outro parceiro. Não registrar sem decisão do Luis.\n")
        elif ab:
            w("⚠️ **Possível duplicidade:** já há negócio aberto do mesmo grupo com este parceiro. Confirmar se é outra tese/filial.\n")
        if any(x["status"] == "ganho" for x in H):
            w("ℹ️ Grupo já é cliente (ganho anterior): tratar como recorrência/nova tese, conforme regra do Recuperador (V5).\n")

    if a.negocio or a.master:
        if a.negocio:
            if a.negocio not in por_id:
                sys.exit(f"Negócio {a.negocio} não está no download {os.path.basename(f)}.")
            alvo = [por_id[a.negocio]]; nome_arq = f"negocio-{a.negocio}"
        else:
            m = resolver_master(a.master)
            alvo = [d for d in N if d["parceiro"] == m and d["status"] == "aberto"]; nome_arq = f"master-{slug(m)}"
            w(f"Master **{m}**: {len(alvo)} negócios abertos verificados.\n")
        total = 0
        for d in alvo:
            r = RF.get(d["id"])
            if not r and cnpj_digitos(d["extras"].get("cnpj")):
                _, r = receita_local(d["extras"]["cnpj"])
            L, al = propostas(d, r, fonte_rf, inf if a.negocio else {}, a.origem)
            if a.master:
                L = [l for l in L if l[3] != "sem fonte oficial"]  # no lote, só divergências com fonte (o resto está no briefing)
                if not L and not al: continue
            total += len(L)
            w(f"## {d['nome']} · {d['parceiro']} · {d['etapa']} · [abrir]({LINK.format(d['id'])})")
            if not r and cnpj_digitos(d["extras"].get("cnpj")):
                w("_CNPJ não localizado na base local da Receita (fora dos filtros ou base desatualizada)._")
            for x in al: w(f"- {x}")
            w(tabela(["Campo HubSpot", "Valor atual", "Valor sugerido", "Fonte", "Ação"], L))
            if a.negocio: bloco_conflito(d["extras"].get("cnpj"), d["parceiro"], d["id"])
        w(f"\n**Total de linhas de proposta:** {total}. Marque cada linha como ✅ aplicar / ✏️ ajustar / ❌ não aplicar e registre no controle de pendências se depender de alguém.")
    else:
        c = cnpj_digitos(a.cnpj); nome_arq = f"cnpj-{c[:8]}"
        w(f"## Checagem de registro — CNPJ {a.cnpj}")
        w(f"- Dígito verificador: {'válido' if cnpj_valido(c) else '**inválido**: confirmar com o parceiro'}")
        fonte_db, r = receita_local(c)
        if r:
            w(f"- Receita ({fonte_db}): {r['razao']} · situação **{r['situacao']}** · CNAE {r['cnae_oficial']} {r['cnae_desc_oficial']} · "
              f"{r['municipio_oficial']}/{r['uf_oficial']} · porte {r['porte_oficial']} · Simples: {r['simples'] or 'não consta'} · início {r['inicio_atividade']}")
            if r.get("simples") == "S": w("- ⚠️ Optante do Simples: fora do foco (veto V2 do Recuperador), confirmar com o Técnico.")
        else:
            w("- Não localizado na base local da Receita (a base só guarda CNAEs/UFs-alvo e CNPJs do HubSpot). Conferir no cartão CNPJ oficial pela Daniela.")
        bloco_conflito(c, None)
    dest = os.path.join(CELULA, "crm", f"{hoje}-proposta-crm-{nome_arq}.md")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w").write("\n".join(md) + "\n"); print(dest)


if __name__ == "__main__":
    main()
