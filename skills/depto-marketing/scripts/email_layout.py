#!/usr/bin/env python3
"""Layout único dos e-mails da Área Partners (Recuperador, caixa do WhatsApp e os próximos).

Por que existe: o Outlook desenha e-mail com o motor do Word. Ele NÃO herda a fonte de uma tabela
para as de dentro, e aí partes do texto caem em Times New Roman e tamanhos diferentes. Aqui toda
célula recebe a mesma família e um tamanho da escala abaixo, sempre com altura de linha em px.

Escala tipográfica (única para todos os e-mails):
  marca 20 · título 18 · seção 16 · destaque (número) 22 · corpo 14 · apoio 12 · rótulo 11 (caixa alta)
"""
import html as _html
import os
import subprocess
import tempfile

import sys as _sys
_sys.path.insert(0, os.path.expanduser("~/agentes-partners/lib"))
import marca  # Design System Save v0.5: cores e fonte vêm de marketing-marca/padrao/marca.json

FONTE = marca.SANS_EMAIL  # o Outlook usa IBM Plex Sans se instalada; senão Calibri
OURO, TINTA, CINZA, LINHA, ZEBRA, FUNDO = marca.C["ouro"], marca.C["texto"], marca.C["texto_2"], marca.C["borda"], marca.C["fundo_2"], marca.C["fundo"]
PRETO, OURO_TEXTO, CINZA_ESCURO = marca.E["fundo"], marca.C["ouro_texto"], marca.E["texto_2"]
ESCALA = {"marca": (20, 26), "titulo": (18, 24), "secao": (16, 22), "numero": (22, 28),
          "corpo": (14, 21), "apoio": (12, 18), "rotulo": (11, 16)}
LARGURA = 680  # corpo do e-mail; margem interna de 32px dos dois lados


def f(nivel="corpo", peso="normal", cor=TINTA, extra=""):
    """Estilo inline completo de texto: família, tamanho e altura de linha fixos."""
    t, a = ESCALA[nivel]
    return (f"font-family:{FONTE};font-size:{t}px;line-height:{a}px;mso-line-height-rule:exactly;"
            f"font-weight:{peso};color:{cor};{extra}")


def esc(s):
    return _html.escape(str(s if s is not None else ""))


def _tab(conteudo, bg=None, borda=None, pad="0", altura=None):
    b = f' bgcolor="{bg}"' if bg else ""
    st = f"border:1px solid {borda};" if borda else ""
    h = f' height="{altura}"' if altura else ""
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"{b} style="{st}">'
            f'<tr><td valign="top"{h} style="padding:{pad};{f()}">{conteudo}</td></tr></table>')


def linha(conteudo, pad="0 32px"):
    return f'<tr><td style="padding:{pad};{f()}">{conteudo}</td></tr>'


def cabecalho(area, titulo, subtitulo):
    esq = (f'<td valign="bottom" style="{f()}"><div style="{f("marca", "bold", OURO, "letter-spacing:1px;")}">Save Co.</div>'
           f'<div style="{f("rotulo", "normal", CINZA_ESCURO, "letter-spacing:1.5px;text-transform:uppercase;")}">{esc(area)}</div></td>')
    dir_ = (f'<td align="right" valign="bottom" style="{f()}"><div style="{f("titulo", "bold", "#ffffff")}">{esc(titulo)}</div>'
            f'<div style="{f("apoio", "normal", CINZA_ESCURO)}">{esc(subtitulo)}</div></td>')
    return (f'<tr><td bgcolor="{PRETO}" style="padding:24px 32px;{f()}"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>{esq}{dir_}</tr></table></td></tr>'
            f'<tr><td height="4" bgcolor="{OURO}" style="font-size:0;line-height:0;mso-line-height-rule:exactly;">&nbsp;</td></tr>')


def paragrafo(texto_html, pad="0 32px 14px"):
    """texto_html pode conter <b> e <br>; o resto deve vir escapado com esc()."""
    return linha(f'<div style="{f()}">{texto_html}</div>', pad)


def secao(titulo, pad="12px 32px 8px"):
    return linha(f'<div style="{f("secao", "bold")}">{esc(titulo)}</div>', pad)


def kpis(itens, pad="6px 26px 18px"):
    """itens = [(rótulo, valor, apoio)] — 3 por linha (rótulo e apoio curtos: não quebram linha)."""
    cel = ""
    w = int(100 / max(1, len(itens)))
    for rot, val, sub in itens:
        cel += (f'<td width="{w}%" valign="top" style="padding:0 6px;{f()}">'
                + _tab(f'<div style="{f("rotulo", "normal", CINZA, "letter-spacing:1px;text-transform:uppercase;white-space:nowrap;")}">{esc(rot)}</div>'
                       f'<div style="{f("numero", "bold")}">{esc(val)}</div>'
                       f'<div style="{f("apoio", "normal", CINZA, "white-space:nowrap;")}">{esc(sub)}</div>', borda=LINHA, pad="14px 16px", altura=62) + "</td>")
    return linha(f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>{cel}</tr></table>', pad)


def passos(titulo, itens, pad="10px 32px 0"):
    """Caixa cinza com passos numerados; itens = [texto_html]."""
    ls = ""
    for n, t in enumerate(itens, 1):
        ls += (f'<tr><td width="34" valign="top" style="padding:5px 0;{f()}"><table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>'
               f'<td width="24" height="24" align="center" valign="middle" bgcolor="{PRETO}" style="{f("apoio", "bold", OURO)}">{n}</td></tr></table></td>'
               f'<td valign="top" style="padding:7px 0 5px;{f()}">{t}</td></tr>')
    corpo = (f'<div style="{f("secao", "bold")}">{esc(titulo)}</div>'
             f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:6px">{ls}</table>')
    return linha(_tab(corpo, bg=ZEBRA, pad="18px 22px"), pad)


def cartao(titulo, etiqueta, linhas_html, cor_etiqueta=OURO_TEXTO, link=None, pad="0 32px 12px"):
    """Bloco de um item (ex.: uma demanda do WhatsApp). linhas_html = [(rótulo, texto_html)]."""
    tit = f'<a href="{esc(link)}" style="{f("corpo", "bold", OURO_TEXTO, "text-decoration:none;")}">{esc(titulo)}</a>' if link else f'<span style="{f("corpo", "bold")}">{esc(titulo)}</span>'
    et = (f'<span style="{f("rotulo", "bold", "#ffffff", f"background-color:{cor_etiqueta};padding:2px 6px;letter-spacing:0.5px;text-transform:uppercase;")}">{esc(etiqueta)}</span>'
          if etiqueta else "")
    corpo = f'<div style="{f()}">{tit}&nbsp;&nbsp;{et}</div>'
    for rot, t in linhas_html:
        corpo += f'<div style="{f(extra="padding-top:4px;")}"><span style="{f("corpo", "bold", CINZA)}">{esc(rot)}:</span> {t}</div>'
    return linha(_tab(corpo, borda=LINHA, pad="12px 16px"), pad)


def assinatura(pad="18px 32px 0"):
    return linha(f'<div style="{f()}">Qualquer dúvida, é só me chamar.<br><br>Abraço,<br><b>Luis Fernando de Melo</b><br>'
                 f'<span style="{f("corpo", "normal", CINZA)}">Gerente Comercial · Parceiros Masters</span></div>', pad)


def rodape(texto, pad="20px 32px 24px"):
    return linha(f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
                 f'<td style="border-top:1px solid {LINHA};padding-top:12px;{f("apoio", "normal", CINZA)}">{texto}</td></tr></table>', pad)


def documento(*linhas_tr):
    return ('<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head><body style="margin:0;padding:0">' +f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{FUNDO}"><tr>'
            f'<td align="center" style="padding:16px 0;{f()}">'
            f'<table role="presentation" width="{LARGURA}" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" style="{f()}">'
            + "".join(linhas_tr) + "</table></td></tr></table></body></html>")


def md(t):
    """Markdown simples → HTML do layout: parágrafos, listas '- ', **negrito**, '### ' subtítulo."""
    import re
    out, lista = [], []
    def fecha():
        if lista:
            out.append('<ul style="margin:4px 0 8px 18px;padding:0">' + "".join(f'<li style="{f()}padding:2px 0">{x}</li>' for x in lista) + "</ul>"); lista.clear()
    for l in (t or "").split("\n"):
        s_ = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(l.strip()))
        if not s_: fecha(); continue
        if s_.startswith(("- ", "• ")): lista.append(s_[2:]); continue
        fecha()
        out.append(f'<div style="{f("corpo", "bold")};padding-top:6px">{s_[4:]}</div>' if s_.startswith("### ") else f'<div style="{f()};padding-bottom:6px">{s_}</div>')
    fecha()
    return "".join(out)


def outlook(para, cc, assunto, corpo, anexos=(), enviar=False, abrir=False):
    """Cria a mensagem no Outlook do Mac (clássico). enviar=False → rascunho; enviar=True → envia.
    Na nuvem (AGENTES_EMAIL=graph), usa a caixa compartilhada pelo Microsoft Graph (lib/graph.py).
    Trava de domínio (Qualidade + Jurídico, 02/10): nada sai para fora de @savecompany.com.br."""
    import sys as _s; _s.path.insert(0, os.path.expanduser("~/agentes-partners/lib")); import protecao
    fora = protecao.interno(list(para), list(cc))
    if fora or not para: return False, f"BLOQUEADO: destinatário fora do domínio ou vazio {fora}"
    pausa = os.path.expanduser("~/agentes-partners/.email-pausado")
    if os.path.exists(pausa) and not (os.environ.get("AGENTES_EMAIL") == "graph" or os.path.exists(os.path.expanduser("~/agentes-partners/.email-graph"))):
        # E-mail pausado (Luis, 13/10: sem Outlook no Mac, aguardando a TI liberar o Graph): a mensagem vira página
        # no OneDrive em vez de falhar. Para religar: apagar ~/agentes-partners/.email-pausado (ou AGENTES_EMAIL=graph).
        import re as _re, shutil as _sh, time as _t; import caminhos
        d = os.path.join(caminhos.luis("central"), "Caixa de saída (e-mail pausado)"); os.makedirs(d, exist_ok=True)
        nome = _t.strftime("%Y-%m-%d %Hh%M%S") + " · " + _re.sub(r'[\\/:*?"<>|]', "-", assunto)[:90] + ".html"
        cab = f'<p style="font:13px sans-serif;color:#555">Para: {esc(", ".join(para))}{(" · Cc: " + esc(", ".join(cc))) if cc else ""} · e-mail pausado: não foi enviado</p>'
        open(os.path.join(d, nome), "w", encoding="utf-8").write(cab + corpo)
        for x in anexos or ():
            if x and os.path.exists(x): _sh.copy2(x, os.path.join(d, os.path.basename(x)))
        return True, f"salvo no OneDrive (e-mail pausado): {nome}"
    if (os.environ.get("AGENTES_EMAIL") == "graph" or os.path.exists(os.path.expanduser("~/agentes-partners/.email-graph"))):
        import sys as _s; _s.path.insert(0, os.path.expanduser("~/agentes-partners/lib")); import graph
        return graph.enviar(list(para), list(cc), assunto, corpo, [a for a in anexos if a], rascunho=not enviar)
    hf = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8"); hf.write(corpo); hf.close()
    q = lambda s: s.replace("\\", "\\\\").replace('"', '\\"')
    rec = "".join(f'make new to recipient at m with properties {{email address:{{address:"{q(a)}"}}}}\n' for a in para)
    rec += "".join(f'make new cc recipient at m with properties {{email address:{{address:"{q(a)}"}}}}\n' for a in cc)
    anx = "".join(f'make new attachment at m with properties {{file:POSIX file "{q(a)}"}}\n' for a in anexos if a)
    acao = "send m" if enviar else ("open m" if abrir else "")
    script = f'''set htmlContent to read POSIX file "{q(hf.name)}" as «class utf8»
with timeout of 300 seconds
tell application "Microsoft Outlook"
  set m to make new outgoing message with properties {{subject:"{q(assunto)}", content:htmlContent}}
  {rec}
  {anx}
  {acao}
end tell
end timeout'''
    # Outlook fechado ou ocupado causava timeout (-1712, 30/09): abre antes e espera até 5 min.
    o = subprocess.run(["open", "-g", "-a", "Microsoft Outlook"], capture_output=True, text=True)
    if o.returncode != 0:  # app ausente (06/10): sem isso o AppleScript dá um "syntax error -2741" enganoso
        os.unlink(hf.name)
        return False, "OUTLOOK_AUSENTE: o Microsoft Outlook não está instalado neste Mac (reinstale o Outlook clássico). " + (o.stderr or "").strip()
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if r.returncode != 0 and "-600" in (r.stderr or ""):  # app ainda não respondia: nada foi criado, tenta uma vez
        import time; time.sleep(20); r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    os.unlink(hf.name)
    return r.returncode == 0, (r.stderr or r.stdout).strip()
