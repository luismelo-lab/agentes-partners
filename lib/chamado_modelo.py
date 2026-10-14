#!/usr/bin/env python3
"""Texto do chamado do GLPI escrito pelo especialista (infra/chamado-ideal.md) e formulário de cada área.

Usado por chamados_whatsapp.py (proposta) e chamados_painel.py (abertura depois da aprovação), para que o chamado
aprovado no painel saia no mesmo formulário da área, com o texto editado pela pessoa quando houver edição.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import protecao as PR  # noqa: E402  nada de dado pessoal no painel nem no GLPI

URG = {1: "Baixa", 2: "Baixa", 3: "Média", 4: "Alta", 5: "Muito alta"}
AGENTE = lambda area: "Gerente Tributário" if str(area).startswith("trib_") else "Gerente Jurídico"


def _e(t):
    return str(t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def html(md):
    out, lista = [], None
    for l in (md or "").split("\n"):
        s = _e(l.strip()); s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        if not s: continue
        m = re.match(r"^(\d+)[.)]\s+(.*)", s); tipo = "ol" if m else "ul" if s.startswith("- ") else None
        if lista and tipo != lista: out.append(f"</{lista}>"); lista = None
        if tipo and not lista: out.append(f"<{tipo}>"); lista = tipo
        out.append(f"<li>{m.group(2) if m else s[2:]}</li>" if tipo else f"<p>{s}</p>")
    return "".join(out) + (f"</{lista}>" if lista else "")


def descricao_md(e):
    """Markdown do corpo do chamado. Com o especialista: estruturado; sem ele, a descrição da triagem."""
    x = e.get("especialista") or {}
    if not x.get("pedidos"):
        return PR.limpo(e.get("descricao") or "")
    p = [f"**Entendemos que:** {x.get('entendemos', '').strip()}", "", "**O que precisamos da área:**"]
    p += [f"{n}. {t}" for n, t in enumerate(x["pedidos"][:5], 1)]
    if x.get("anexos") or x.get("faltam"):
        p += ["", "**Documentos:**"] + [f"- Anexo: {d}" for d in x.get("anexos", [])] + [f"- Falta: {d}" for d in x.get("faltam", [])]
    if x.get("prazo_motivo"): p += ["", f"**Prazo:** {x['prazo_motivo']}"]
    if x.get("entrega"): p += ["", f"**Entrega esperada:** {x['entrega']}"]
    if x.get("riscos"): p += ["", f"**Riscos:** {x['riscos']}"]
    if x.get("checagens"): p += ["", "**Já conferido pelos agentes:**"] + [f"- {c}" for c in x["checagens"]]
    return PR.limpo("\n".join(p))


def formulario(area, i, e, corpo_md, origem_html=""):
    """Descrição no formulário que a área usa no GLPI (infra/glpi-regras.md). `i` = item da triagem ou proposta."""
    corpo = html(PR.limpo(corpo_md))
    card = e.get("card_bitrix") or i.get("card_bitrix")
    hub = f" · HubSpot: {_e(i['link'])}" if i.get("link") else ""
    if area.startswith("trib_"):
        return (f"<p><b>1) Urgência:</b> {URG.get(int(e.get('urgencia', 3)), 'Média')}</p>"
                f"<p><b>2) Empresa:</b> {_e(e.get('empresa') or i.get('negocio') or 'a confirmar')}</p>"
                f"<p><b>3) Descrição:</b></p>{corpo}"
                f"<p><b>4) Link do Card:</b> {_e(card) if card else 'sem card no Bitrix localizado'}{hub}</p>"
                f"<p><b>5) Prazo de Entrega:</b> {_e(e.get('prazo') or i.get('prazo') or 'a definir pela área')}</p>{origem_html}")
    if area.startswith("jur_") or area == "contrato_padrao":
        x = e.get("especialista") or {}
        docs = "; ".join(x.get("anexos") or []) or e.get("documentos") or "anexos da conversa no WhatsApp (a Partners anexa ao abrir)"
        return (f"<p><b>DADOS</b></p><p>1) Setor Solicitante: MASTER</p><p>2) Parceiro Solicitante: {_e(i.get('master') or 'a confirmar')}</p>"
                f"<p><b>INFORMAÇÕES GERAIS</b></p><p>1) Assunto: {_e(e.get('assunto') or i.get('o_que_pede'))}</p><p>2) Classe: Interna</p>"
                f"<p>3) Informações Adicionais:</p>{corpo}"
                f"<p>4) Documentos: {_e(docs)}" + (f" · Card: {_e(card)}" if card else "") + f"{hub}</p>{origem_html}")
    return origem_html + corpo + (f"<p><b>Negócio no HubSpot:</b> {_e(i['link'])}</p>" if i.get("link") else "")
