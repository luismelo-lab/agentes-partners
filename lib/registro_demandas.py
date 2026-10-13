#!/usr/bin/env python3
"""Registro único de demandas da Área Partners (proposta do Depto Dados, 01/10/2026).

Uma lista só, com ID D-AAAA-NNNN, origem (WhatsApp, E-mail-Central e depois GLPI), pessoa, Master, negócio,
status, prazo e eventos. Substitui o acompanhamento espalhado entre as triagens do WhatsApp, o registro da
Central e a planilha de pendências da Daniela (que passa a ser uma visão gerada daqui).
- WhatsApp: cada triagem faz upsert pela chave pessoa+conversa; se a conversa some das pendências, a
  demanda vira "resolvida".
- Central: cada pedido P-NNNN é uma demanda (id_origem guarda o P-NNNN).

Uso:
  registro_demandas.py whatsapp --triagem <arquivo>     (chamado pelo email_whatsapp.py)
  registro_demandas.py central                           (sincroniza com central-agentes/registro.json)
  registro_demandas.py planilhas                         (gera Demandas.xlsx na pasta de cada pessoa no OneDrive)
  registro_demandas.py abertas [--pessoa p]              (lista no terminal)
"""
import argparse, fcntl, json, os, sys
from datetime import datetime

AP = os.path.expanduser("~/agentes-partners")
REG = os.path.join(AP, "registro", "demandas.json")
import caminhos as _cam  # noqa: E402  (pasta ativa do OneDrive: lib/caminhos.py)
# pasta do OneDrive resolvida na hora do uso ({mod}.area()): sem OneDrive, só a parte de arquivos falha (TI, 02/10)
PASTA = {"daniela": "Central Masters · Daniela", "jenifer": "Central BDR · Jenifer", "geovana": "Central Técnica · Geovana", "luis": "04 · Gestão / Central de Agentes"}  # rótulo; o caminho vem de caminhos.pasta()
ABERTOS = ("responder", "acompanhar", "em_analise", "aguardando_aprovacao")


class Registro:
    def __enter__(self):
        os.makedirs(os.path.dirname(REG), exist_ok=True); os.chmod(os.path.dirname(REG), 0o700)
        self.t = open(REG + ".trava", "w"); fcntl.flock(self.t, fcntl.LOCK_EX)
        self.R = json.load(open(REG)) if os.path.exists(REG) else {"seq": {}, "demandas": {}}
        return self.R

    def __exit__(self, *x):
        json.dump(self.R, open(REG, "w"), ensure_ascii=False, indent=1)
        fcntl.flock(self.t, fcntl.LOCK_UN); self.t.close()


def novo_id(R):
    ano = datetime.now().strftime("%Y"); R["seq"][ano] = R["seq"].get(ano, 0) + 1
    return f"D-{ano}-{R['seq'][ano]:04d}"


def agora():
    return datetime.now().isoformat(timespec="minutes")


def achar(R, chave):
    return next((d for d in R["demandas"].values() if d["chave"] == chave and d["status"] in ABERTOS), None)


def cmd_whatsapp(a):
    T = json.load(open(a.triagem)); modo = T.get("modo", "IA")
    with Registro() as R:
        for p, P in T.get("pessoas", {}).items():
            vistos = set()
            for i in P.get("itens", []):
                if i.get("status") not in ("responder", "acompanhar"): continue
                chave = f"whatsapp|{p}|{i['chat']}"; vistos.add(chave)
                d = achar(R, chave)
                if not d:  # fechada há pouco no painel e sem mensagem nova depois disso: não reabre
                    ult_msg = datetime.now().timestamp() - float(i.get("aguardando_h") or 0) * 3600
                    fechada = [x for x in R["demandas"].values() if x["chave"] == chave and x["status"] not in ABERTOS and x.get("atualizada_em")]
                    if fechada and max(datetime.fromisoformat(x["atualizada_em"][:16]).timestamp() for x in fechada) >= ult_msg:
                        vistos.add(chave); continue
                campos = {k: i.get(k) for k in ("master", "o_que_pede", "rota", "proximo_passo", "prazo", "negocio", "link", "urgente") if i.get(k)}
                if not d:  # o parceiro voltou em até 7 dias: reabre a mesma demanda (evita ID e chamado duplicados; Células, 02/10)
                    rec = [x for x in R["demandas"].values() if x["chave"] == chave and x.get("resolvida_em")
                           and (datetime.now() - datetime.fromisoformat(x["resolvida_em"][:16])).days < 7]
                    if rec:
                        d = max(rec, key=lambda x: x["resolvida_em"]); d.pop("resolvida_em", None)
                        d["eventos"].append({"quando": agora(), "evento": "reaberta: nova mensagem do parceiro"})
                if not d:
                    did = novo_id(R)
                    d = R["demandas"][did] = {"id": did, "chave": chave, "origem": "WhatsApp", "pessoa": p, "titulo": i["chat"],
                                              "aberta_em": agora(), "eventos": [], **campos}
                elif modo == "IA" or not d.get("rota"):  # a rodada com IA tem a leitura mais completa
                    d.update(campos)
                d["status"] = i["status"]; d["atualizada_em"] = agora(); d["aguardando_h"] = i.get("aguardando_h")
                d["eventos"] = (d["eventos"] + [{"quando": agora(), "evento": f"{i['status']} ({modo})"}])[-30:]
            for d in R["demandas"].values():  # conversa que saiu da lista de pendências desta pessoa = resolvida
                if d["origem"] == "WhatsApp" and d["pessoa"] == p and d["status"] in ABERTOS and d["chave"] not in vistos:
                    if (d.get("chamado") or {}).get("status") in ("proposto", "aberto", "aprovado_manual") or (d.get("chamado") or {}).get("proposto"):
                        d["status"] = "acompanhar"; continue  # chamado em andamento: acompanha até a área responder
                    d["status"] = "resolvida"; d["resolvida_em"] = agora(); d["eventos"].append({"quando": agora(), "evento": "sem pendência na rodada"})
    print("registro atualizado (WhatsApp)")


def cmd_central(a):
    C = json.load(open(os.path.join(AP, "central-agentes", "registro.json")))
    mapa = {"em_analise": "em_analise", "aguardando_aprovacao": "aguardando_aprovacao", "aprovado": "concluida", "nao_aprovado": "encerrada"}
    with Registro() as R:
        for pid, P in C.get("pedidos", {}).items():
            chave = f"central|{pid}"
            d = next((x for x in R["demandas"].values() if x["chave"] == chave), None)
            if not d:
                did = novo_id(R)
                d = R["demandas"][did] = {"id": did, "chave": chave, "id_origem": pid, "origem": "E-mail (Central)", "pessoa": P["pessoa"],
                                          "titulo": P.get("assunto"), "tipo": P.get("codigo"), "aberta_em": P.get("recebido"), "eventos": []}
            st = mapa.get(P["status"], P["status"])
            if d.get("status") != st:
                d["eventos"].append({"quando": agora(), "evento": st}); d["status"] = st; d["atualizada_em"] = agora()
            d["versao"] = P.get("versao")
    print("registro atualizado (Central)")


def cmd_planilhas(a):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    R = json.load(open(REG)) if os.path.exists(REG) else {"demandas": {}}
    for p, pasta in PASTA.items():
        ds = [d for d in R["demandas"].values() if p == "luis" or d["pessoa"] == p]
        if not ds: continue
        wb = Workbook(); ws = wb.active; ws.title = "Em aberto"
        cols = ["ID", "Origem", "Pessoa", "Conversa / pedido", "Master", "O que pede", "Encaminhar para", "Próximo passo", "Prazo", "Status", "Aberta em", "Negócio", "Link"]
        def aba(w, linhas):
            w.append(cols)
            for c in w[1]: c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="141416")
            for d in linhas:
                w.append([d["id"], d["origem"], d["pessoa"], d.get("titulo"), d.get("master"), d.get("o_que_pede"), d.get("rota"), d.get("proximo_passo"),
                          d.get("prazo"), d["status"], (d.get("aberta_em") or "")[:16].replace("T", " "), d.get("negocio"), d.get("link")])
            for i, wd in enumerate([12, 16, 10, 30, 16, 50, 24, 36, 12, 18, 16, 28, 20], 1):
                w.column_dimensions[w.cell(1, i).column_letter].width = wd
            for row in w.iter_rows(min_row=2):
                for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
            w.freeze_panes = "A2"; w.auto_filter.ref = w.dimensions
        aba(ws, sorted([d for d in ds if d["status"] in ABERTOS], key=lambda d: d.get("aberta_em") or ""))
        aba(wb.create_sheet("Histórico (30 dias)"), sorted([d for d in ds if d["status"] not in ABERTOS], key=lambda d: d.get("atualizada_em") or "", reverse=True)[:300])
        os.makedirs(_cam.pasta(p), exist_ok=True)
        wb.save(os.path.join(_cam.pasta(p), "Demandas.xlsx"))  # Luis: 04 · Gestão/Central de Agentes (padrão 00–99)
    print("planilhas Demandas.xlsx atualizadas")


def cmd_abertas(a):
    R = json.load(open(REG)) if os.path.exists(REG) else {"demandas": {}}
    for d in sorted(R["demandas"].values(), key=lambda d: d.get("aberta_em") or ""):
        if d["status"] in ABERTOS and (not a.pessoa or d["pessoa"] == a.pessoa):
            print(d["id"], d["pessoa"], d["origem"], d["status"], "·", (d.get("titulo") or "")[:40], "·", (d.get("o_que_pede") or "")[:70])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    x = sp.add_parser("whatsapp"); x.add_argument("--triagem", required=True)
    sp.add_parser("central"); sp.add_parser("planilhas")
    x = sp.add_parser("abertas"); x.add_argument("--pessoa")
    a = ap.parse_args()
    {"whatsapp": cmd_whatsapp, "central": cmd_central, "planilhas": cmd_planilhas, "abertas": cmd_abertas}[a.cmd](a)
