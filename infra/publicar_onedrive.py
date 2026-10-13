#!/usr/bin/env python3
"""Publica as saídas dos agentes na pasta compartilhada do OneDrive (MVP de 30/09/2026).

Cada pessoa tem a sua pasta; o Luis compartilha cada uma pelo botão "Compartilhar" do OneDrive.
- Relatórios (somente leitura): copiados a cada rodada; os .md viram .docx para abrir no Word/navegador.
- Planilhas de trabalho (a pessoa edita: pendências, follow-up, fila, revisor, apontamentos): sincronizadas
  nos dois sentidos, **vale a versão mais nova**. Assim o que a Geovana marca no OneDrive volta para o agente.

Fica FORA da pasta compartilhada: .env, base da Receita, textos de pareceres, caixas brutas do WhatsApp,
dados bancários. Uso: python3 publicar_onedrive.py [--simular]
"""
import argparse, errno, glob, os, re, shutil, sys, tempfile, time, zipfile
from xml.sax.saxutils import escape

H = os.path.expanduser
AP = H("~/agentes-partners")
sys.path.insert(0, H("~/agentes-partners/lib")); import caminhos  # noqa: E402  (pasta ativa do OneDrive)
RAIZ = caminhos.area()

ult = lambda pad: (sorted(glob.glob(os.path.join(AP, pad)), key=os.path.getmtime) or [None])[-1]
todos = lambda pad: sorted(glob.glob(os.path.join(AP, pad)))

PASTAS = {
    "Central Masters · Daniela": {
        "editar": ["celulas/daniela/Controle-Pendencias-Masters.xlsx", "celulas/daniela/Semana0-apontamento-Daniela.xlsx"],
        "ler": [("Briefings", todos("celulas/daniela/briefings/*.md")), ("Semana 0", [os.path.join(AP, "celulas/daniela/Semana0-roteiro-conversa-Daniela.md")])]},
    "Central BDR · Jenifer": {
        "editar": ["celulas/jenifer/Controle-Followup-Jenifer.xlsx", "celulas/jenifer/Semana0-apontamento-Jenifer.xlsx"],
        "ler": [("Listas", todos("celulas/jenifer/listas/*.xlsx")), ("Semana 0", [os.path.join(AP, "celulas/jenifer/Semana0-roteiro-conversa-Jenifer.md")])]},
    "Central Técnica · Geovana": {
        "editar": [os.path.relpath(p, AP) for p in [ult("celulas/geovana/recuperador/Fila-Recuperador-*.xlsx"), ult("celulas/geovana/revisor/Revisor-Diagnostico-*.xlsx")] if p]
                  + ["celulas/geovana/Semana0-apontamento-Geovana.xlsx"],
        "ler": [("Fichas do Recuperador", todos("celulas/geovana/recuperador/fichas/*.md")), ("Fichas do Revisor", todos("celulas/geovana/revisor/fichas/*.md")),
                ("Semana 0", [os.path.join(AP, "celulas/geovana/Semana0-roteiro-conversa-Geovana.md")])]},
    "Gestão · Luis": {
        "editar": [],
        "ler": [("Resultado semanal", [p for p in [ult("departamentos/resultados/relatorios/Resultado-Semanal-*.pptx"), ult("departamentos/resultados/relatorios/Resultado-Semanal-*.md")] if p]),
                ("Conselho", todos("conselho/atas/*.md") + [os.path.join(AP, "conselho/decisoes.md")]),
                ("Áreas", [p for p in [ult("departamentos/dados/Dados-BI-*.xlsx"), ult("departamentos/operacoes-canal/Conferencia-Repasses-*.xlsx"),
                                       ult("departamentos/operacoes-canal/Conflito-Canal-*.xlsx"), ult("departamentos/contratos/Controle-Contratos-*.xlsx"),
                                       ult("departamentos/partner-success/metricas/Metricas-PS-*.xlsx"), ult("departamentos/qualidade/auditorias/*-teste-auditar_texto.md"),
                                       os.path.join(AP, "departamentos/ti/GLPI-pronto-para-agente.xlsx"), os.path.join(AP, "departamentos/ti/chamados-rascunho.md"), os.path.join(AP, "departamentos/ti/integracoes-microsoft.md"),
                                       os.path.join(AP, "integracoes/whatsapp-openwa.md")] if p and os.path.exists(p)])]},
}


def md_para_docx(md, destino, titulo):
    """Conversor mínimo Markdown → Word (títulos, listas, negrito, tabelas como texto), sem dependências."""
    def runs(t):
        out = []
        for i, parte in enumerate(re.split(r"\*\*(.+?)\*\*", t)):
            if not parte: continue
            parte = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", parte).replace("`", "")
            b = "<w:b/>" if i % 2 else ""
            out.append(f'<w:r><w:rPr>{b}<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr><w:t xml:space="preserve">{escape(parte)}</w:t></w:r>')
        return "".join(out)
    ps = []
    for l in md.splitlines():
        s = l.rstrip()
        if re.match(r"^\|?\s*:?-{3,}", s): continue
        m = re.match(r"^(#{1,4})\s+(.*)", s)
        if m:
            tam = {1: 32, 2: 28, 3: 24, 4: 22}[len(m.group(1))]
            ps.append(f'<w:p><w:pPr><w:spacing w:before="240" w:after="80"/></w:pPr><w:r><w:rPr><w:b/><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="{tam}"/></w:rPr><w:t xml:space="preserve">{escape(m.group(2).replace("**", ""))}</w:t></w:r></w:p>')
        elif re.match(r"^\s*[-*]\s+", s):
            ps.append(f'<w:p><w:pPr><w:ind w:left="360" w:hanging="220"/></w:pPr>{runs("• " + re.sub(r"^\s*[-*]\s+", "", s))}</w:p>')
        elif s.startswith("|"):
            cel = [c.strip() for c in s.strip("|").split("|")]
            ps.append(f'<w:p>{runs("   ·   ".join(cel))}</w:p>')
        elif s.strip():
            ps.append(f'<w:p><w:pPr><w:spacing w:after="80"/></w:pPr>{runs(s.lstrip("> "))}</w:p>')
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
           + "".join(ps) + '<w:sectPr><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr></w:body></w:document>')
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr("word/document.xml", doc)


FALHAS = []


def igual(a, b):  # o OneDrive guarda a hora em segundos inteiros: sem tolerância, toda rodada regravava as mesmas planilhas
    return os.path.exists(b) and abs(os.path.getmtime(a) - os.path.getmtime(b)) < 2 and os.path.getsize(a) == os.path.getsize(b)


def copiar(src, dst):
    """Grava em temporário ao lado ("~$", o OneDrive não sincroniza) e troca de uma vez. Arquivo travado pelo OneDrive
    (EDEADLK desde 09/10) tenta de novo e, se não der, é pulado: o resto da publicação continua."""
    tmp = os.path.join(os.path.dirname(dst), "~$partners-" + os.path.basename(dst))
    for t in range(4):
        try:
            shutil.copy2(src, tmp); os.replace(tmp, dst); return True
        except OSError as e:
            if os.path.exists(tmp):
                try: os.unlink(tmp)
                except OSError: pass
            if e.errno not in (errno.EDEADLK, errno.EBUSY, errno.EAGAIN, errno.EPERM): raise
            time.sleep(5 * 2 ** t)
    FALHAS.append(dst); return False


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--simular", action="store_true"); a = ap.parse_args()
    feitos = []
    for pasta, cfg in PASTAS.items():
        base = os.path.join(RAIZ, pasta)
        if not a.simular: os.makedirs(base, exist_ok=True)
        for rel in cfg["editar"]:  # vale a versão mais nova
            loc = os.path.join(AP, rel)
            nuv = os.path.join(base, os.path.basename(rel))
            if not os.path.exists(loc) and not os.path.exists(nuv): continue
            if os.path.exists(nuv) and (not os.path.exists(loc) or os.path.getmtime(nuv) > os.path.getmtime(loc) + 2):
                acao = ("OneDrive → agente", nuv, loc)
            elif not os.path.exists(nuv) or os.path.getmtime(loc) > os.path.getmtime(nuv) + 2:
                acao = ("agente → OneDrive", loc, nuv)
            else:
                continue
            if not a.simular and not copiar(acao[1], acao[2]): continue
            feitos.append(f"{pasta}: {os.path.basename(rel)} ({acao[0]})")
        for sub, arquivos in cfg["ler"]:
            dest = os.path.join(base, sub)
            if not a.simular: os.makedirs(dest, exist_ok=True)
            for f in arquivos:
                if not f or not os.path.exists(f): continue
                if f.endswith(".md"):
                    alvo = os.path.join(dest, os.path.basename(f)[:-3] + ".docx")
                    if os.path.exists(alvo) and os.path.getmtime(alvo) >= os.path.getmtime(f) - 2: continue
                    if not a.simular:  # gera fora do OneDrive e copia pronto
                        loc = os.path.join(tempfile.mkdtemp(), os.path.basename(alvo))
                        md_para_docx(open(f, encoding="utf-8").read(), loc, os.path.basename(f))
                        ok = copiar(loc, alvo); shutil.rmtree(os.path.dirname(loc), ignore_errors=True)
                        if not ok: continue
                else:
                    alvo = os.path.join(dest, os.path.basename(f))
                    if igual(f, alvo) or (os.path.exists(alvo) and os.path.getmtime(alvo) >= os.path.getmtime(f) - 2): continue
                    if not a.simular and not copiar(f, alvo): continue
                feitos.append(f"{pasta}/{sub}: {os.path.basename(alvo)}")
    guia = os.path.join(RAIZ, "00 · Comece aqui.docx")
    if not a.simular and not os.path.exists(guia):
        md_para_docx(COMECE, guia, "Comece aqui")
    print(f"{len(feitos)} itens publicados/sincronizados em {RAIZ}")
    if os.environ.get("AGENTES_ARQUIVOS") == "sharepoint":  # na nuvem: a pasta local é espelho do site do SharePoint
        sys.path.insert(0, os.path.join(AP, "lib")); import graph
        print(graph.subir_pasta(RAIZ, "", os.path.join(AP, "logs", ".manifesto-sharepoint.json")), "arquivo(s) enviados ao SharePoint")
    for x in feitos[:60]: print("  ", x)
    if FALHAS:  # o que deu certo já foi publicado; a rotina falha para avisar o que ficou
        sys.exit(f"{len(FALHAS)} arquivo(s) travado(s) pelo OneDrive não foram atualizados: " + "; ".join(os.path.basename(x) for x in FALHAS))


COMECE = """# Área Partners · Agentes

Esta pasta é onde os agentes da Área Partners entregam o trabalho para cada pessoa do time. Cada um vê só a própria pasta.

## Como funciona
- **Relatórios e fichas** são atualizados sozinhos pelos agentes. Abra no navegador, no Word ou no Teams.
- **Planilhas de trabalho** (pendências, follow-up, fila do Recuperador, Revisor de Diagnóstico, apontamento da Semana 0): **edite direto aqui**. O agente lê a versão mais nova na próxima rodada.
- Nada aqui é enviado a parceiros ou clientes. Tudo é pré-análise para a sua validação.

## Pastas
- **Central Masters · Daniela:** controle de pendências dos Masters, briefings de conta e Semana 0.
- **Central BDR · Jenifer:** listas de prospects por Master, controle de follow-up e Semana 0.
- **Central Técnica · Geovana:** fila do Recuperador, Revisor de Diagnóstico, fichas e Semana 0.
- **Gestão · Luis:** resultado semanal, atas do Conselho e os relatórios das áreas.

## Regras
- Não mova nem renomeie as planilhas de trabalho: o agente procura pelo nome.
- Dados de clientes são confidenciais: não compartilhe fora do time.
"""

if __name__ == "__main__":
    main()
