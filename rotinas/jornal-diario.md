---
name: jornal-diario
description: Dias úteis, 7h15. O Marketing (Autoridade Digital & Curadoria) monta o jornal diário com 3 a 8 notícias da Save e do mercado tributário e financeiro, com fonte e data, revisado e sem promessa. Fica no OneDrive para o Luis.
---

Rotina do jornal diário da Área Partners da Save Co. (Luis, 26/10/2026: o jornal existia como entrega da área, mas nunca tinha sido agendado). Português do Brasil. Siga `~/agentes-partners/CLAUDE.md`. Nunca leia `.env`. Nada é enviado a parceiro ou cliente: o jornal é rascunho interno.

1. Leia a skill `depto-marketing` e o especialista `references/especialistas/autoridade-digital-curadoria.md`, junto com `references/jornal.md` (seções e formato). Use também os radares das áreas (`~/.claude/skills/*/references/radar-mercado*.md`) para não repetir o que já está registrado.
2. Pesquise as notícias das últimas 24 h (na segunda-feira, desde sexta), com data e link da fonte. Priorize fonte oficial: STF, STJ, CARF, Receita Federal, PGFN, Planalto, CVM, Bacen, Sefaz. Os temas:
   - julgados e normas de PIS/COFINS, ICMS e reforma tributária;
   - transação e editais da PGFN;
   - crédito, recebíveis e FIDC;
   - comércio exterior e Paraguai;
   - menções à Save.
   São de 3 a 8 itens, cada um com "o que mudou", "o que significa para a Save e os parceiros" e "área de agentes que acompanha". Sem notícia relevante, diga isso em uma linha. Não encha a pauta.
3. Revisão: rode `python3 ~/.claude/skills/depto-qualidade/scripts/auditar_texto.py` no arquivo e corrija o que for promessa. Notícia que muda tese, prazo ou regra da casa vira proposta em `~/agentes-partners/registro/achados-areas-<AAAA-MM-DD>.json` (o Conselho lê). Ela não muda a base sozinha.
4. Grave em `~/agentes-partners/departamentos/marketing/jornal/<AAAA-MM-DD>.md`, com o cabeçalho "RASCUNHO — revisar antes de distribuir". Copie para o OneDrive em `04 · Gestão, Metas e Estratégia/Central de Agentes/Jornal/Jornal-<AAAA-MM-DD>.md`, usando `python3 -c "import sys; sys.path.insert(0, '/Users/luisfernandomelo/agentes-partners/lib'); import caminhos; print(caminhos.luis('central'))"` para achar a pasta.
5. Ao final, uma linha: quantas notícias, quais áreas e se houve proposta para o Conselho.
