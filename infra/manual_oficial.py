#!/usr/bin/env python3
"""Manual Oficial dos Agentes da Área Partners (v2.0, 23/10/2026). Pedido do Luis: documento oficial de tudo o que foi
construído, com regras, fluxos, responsabilidades, o que cada um entrega e onde entrega.

As partes fixas (regras, fluxos, responsabilidades) estão neste arquivo. O mapa das áreas e dos especialistas é lido
das próprias skills (`skills/<área>/references/especialistas/*.md`, seção "1. Entrega única"), por isso o manual se
regera sempre que uma área muda.

  python3 infra/manual_oficial.py                 grava docs/manual-oficial-agentes.md
  python3 infra/manual_oficial.py --docx          também gera o Word no padrão Save em 04 · Gestão/Central de Agentes
"""
import glob, json, os, re, subprocess, sys
from datetime import date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "lib"))
VERSAO = "2.2"
SAIDA_MD = os.path.join(REPO, "docs/manual-oficial-agentes.md")

# área: (nome, bloco, missão, dono humano, onde entrega)
AREAS = {
    "gabinete": ("Gabinete", "Orquestração", "Porta de entrada única do Luis: confere se o pedido já existe, decide quais áreas entram e com que profundidade e consolida um parecer único.", "Luis", "Na conversa; parecer consolidado em 3 blocos"),
    "central-agentes": ("Central de Agentes", "Orquestração", "Recebe os pedidos do time pelo painel e pelo e-mail [AGENTES], tria, aciona a área certa e responde.", "Luis (o time pede)", "E-mail ao solicitante; enquanto o Graph não volta, `04 · Gestão/Central de Agentes/Caixa de saída` (D91)"),
    "conselho-partners": ("Conselho Consultivo", "Orquestração", "Analisa decisões de estratégia, meta, preço e produto com seis conselheiros e um presidente; diz também o que não fazer.", "Luis", "Ata em `04 · Gestão/Conselho`; decisões em `conselho/decisoes.md`"),
    "arquiteto-agentes": ("Arquiteto de Agentes", "Orquestração", "Dono do padrão sênior e do auditor; desenha, avalia e evolui os agentes e mede o ROI de IA.", "Luis", "`infra/padrao-senior.md`, auditoria semanal e pacote de validação (D94)"),
    "depto-tributario": ("Tributário & Contábil", "Produtos", "Teses de recuperação, alíquota zero via PER, reforma e saldos credores, insumos, exclusões da base, agro e evidência no SPED.", "Time técnico (validação humana, D94)", "Pré-análise na conversa ou no pedido; catálogo em `departamentos/tributario/`"),
    "depto-juridico": ("Jurídico", "Produtos", "Gestão de Passivo, estruturação patrimonial, prazos e contencioso administrativo e o perímetro do que a Save pode fazer.", "Advogado humano (validação até 07/11, D94)", "Pré-análise na conversa ou no pedido"),
    "depto-save-invest": ("Save Invest", "Produtos", "Gestão de Contas, antecipação de recebíveis e FIDC (D92). O cliente contrata, a Save Invest presta e a Federal Invest financia (D96).", "Junior", "Parecer ao Junior; encaminhamento pela esteira"),
    "depto-internacional": ("Produtos Internacionais", "Produtos", "Tax internacional e comércio exterior (pronto); Crédito Internacional, Maquila, captação, home equity, passivo bancário e turnkey (em validação).", "João Mattos e Paulo", "`03 · Produtos e Projetos/Crédito Internacional` e `PROJETO MAQUILA`"),
    "depto-solucoes": ("Contas e Soluções", "Venda e esteira", "Dono da esteira (Destravar caixa → Proteger e controlar → Crescer) e do mapa da conta: diz o que mais cada cliente pode contratar e encaminha ao dono do produto.", "Luis e Daniela", "`01 · Comercial e Parceiros/Relatórios das áreas/Contas e Soluções`"),
    "apresentacao-diagnostico": ("Apresentação do Diagnóstico", "Venda e esteira", "Transforma o diagnóstico tributário revisado na apresentação ao cliente, com narrativa, objeções, case do segmento e revisão de promessas.", "Luis e Geovana", "`06 · Marketing e Apresentações/Diagnósticos`"),
    "revisor-diagnostico": ("Revisor de Diagnóstico", "Venda e esteira", "Segunda opinião antes do cliente: aponta as teses esperadas que o técnico não analisou e o registro do SPED que decide.", "Geovana", "`Área Partners · Agentes/Central Técnica · Geovana`"),
    "recuperador": ("Recuperador de Perdidos", "Venda e esteira", "Fila semanal dos negócios perdidos e parados com chance de reanálise, com folha curta de decisão para a Geovana.", "Geovana", "`Central Técnica · Geovana` (fila, folha do lote e fichas)"),
    "depto-pos-venda": ("Pós-venda", "Venda e esteira", "Acompanha o crédito até o dinheiro: prazo de 360 dias do PER, compensação de ofício, recebimento e recorrência.", "Área de Pós-venda e Daniela", "Calendário e rascunhos ao parceiro; `Relatórios das áreas`"),
    "celula-daniela": ("Central Masters (Daniela)", "Canal", "Atende os 9 Masters: triagem e SLA, retorno ao parceiro, plano de conta e reunião trimestral, apoio jurídico ao canal e higiene do CRM.", "Daniela", "`Área Partners · Agentes/Central Masters · Daniela`"),
    "celula-jenifer": ("Central BDR (Jenifer)", "Canal", "Prospecção para os Masters: listas, qualificação, abordagem por persona, objeções, LGPD na prospecção e preparação de reunião.", "Jenifer", "`Área Partners · Agentes/Central BDR · Jenifer/Listas`"),
    "depto-intel-comercial": ("Inteligência Comercial", "Canal", "Perfil de cliente ideal por produto, tamanho de mercado, lead scoring, território por Master, concorrência e recrutamento de parceiros.", "Luis e Jenifer", "`Relatórios das áreas`; listas na Central BDR"),
    "depto-operacoes-canal": ("Operações de Canal", "Canal", "Repasse e comissão do parceiro (D64, D78, D97), retenções, extrato, registro de oportunidade e conflito de canal.", "Luis e Financeiro", "`Relatórios das áreas` (Conferência de Repasses, Conflito de Canal)"),
    "depto-contratos": ("Contratos", "Canal", "Lê e prepara contratos de serviço, de parceiro e dos produtos 2027; assinatura, distrato e cobrança. Nunca envia nem assina.", "Área de Contratos e Jurídico", "Pedido à área real; `Relatórios das áreas` (Controle de Contratos)"),
    "depto-partner-success": ("Partner Success", "Canal", "Academia de parceiros, onboarding, níveis do programa, saúde e churn de parceiro e comunidade.", "Luis e Daniela", "`01 · Comercial e Parceiros/Programa de Parceiros`; Métricas PS"),
    "depto-resultados": ("Resultados & Controladoria", "Gestão", "Relatório semanal: receita contratada, reconhecida e recebida, margem, forecast, ROI, preço e metas por produto.", "Luis", "`04 · Gestão/Resultado semanal`"),
    "depto-dados": ("Dados & BI", "Gestão", "Download diário do HubSpot (só leitura), qualidade e saneamento do CRM, dicionário, painel e estatística.", "Luis", "`Relatórios das áreas` (Dados-BI diário)"),
    "depto-qualidade": ("Qualidade & Ouvidoria", "Gestão", "Auditor de promessas, controle das entregas dos agentes, incidentes e reclamações, voz do parceiro e melhoria contínua.", "Luis", "Revisão de todo material externo; `Relatórios das áreas`"),
    "depto-marketing": ("Marketing", "Suporte", "Campanhas de canal com calendário fiscal, ABM, kits por produto, redação, design no padrão Save e conformidade publicitária.", "Luis e Marketing da Save", "`06 · Marketing e Apresentações`"),
    "depto-pessoas": ("Pessoas", "Suporte", "Remuneração variável, metas e desempenho, capacitação técnica, recrutamento, clima e conformidade com a CLT e a LGPD.", "Luis", "Rascunhos confidenciais na conversa (dado de pessoas fica no Mac)"),
    "depto-ti": ("TI & Automação", "Suporte", "Integrações (Graph, HubSpot, GLPI, WhatsApp), segurança e SSO, incidentes, rotinas agendadas, custos e governança de IA.", "TI da Save", "Pedidos e especificações em `04 · Gestão/Central de Agentes`"),
}
ORDEM_BLOCOS = ["Orquestração", "Produtos", "Venda e esteira", "Canal", "Gestão", "Suporte"]

ROTINAS = [
    ("Operação das áreas", "Dias úteis, 7h40 (só alertas novos ou que mudaram)", "Cada área analisa os alertas em 3 blocos; plano do dia por pessoa, com a coluna Usei/Ajustei/Não usei; às segundas, carteira de cross-sell", "Plano do Luis em `04 · Gestão/Central de Agentes`; plano de cada pessoa em `<Central da pessoa>/Plano do dia`"),
    ("WhatsApp · triagem", "Dias úteis, 8h e 14h (11h e 17h sem IA)", "Lê os grupos dos Masters e as caixas do time, interpreta e devolve analisado", "Pastas das Centrais em `Área Partners · Agentes`"),
    ("Central de Agentes", "Dias úteis, a cada 2 horas (8h às 18h), com saída rápida se não houver nada novo", "Processa pedidos do painel e do e-mail [AGENTES] e aplica as decisões do painel", "E-mail ou `Caixa de saída`"),
    ("Relatório semanal de resultados", "Segunda, 6h30", "Deck e one-pager de resultados", "`04 · Gestão/Resultado semanal`"),
    ("Conselho · reunião semanal", "Segunda, 7h30", "Ata com recomendação, o que não fazer e decisões para aprovar", "`04 · Gestão/Conselho`"),
    ("Recuperador · lote semanal", "Segunda, 9h", "Fila, folha curta do lote e fichas para a Geovana", "`Central Técnica · Geovana`"),
    ("Radar de mercado", "Sexta, 7h", "Cada área pesquisa o que mudou (normas, julgados, taxas) e atualiza o radar", "Branch `radar/<data>` e resumo em `Central de Agentes/Radar de mercado`"),
    ("Consolidação semanal", "Sexta, 16h", "Junta as conversas, resgata arquivos, aponta repetições e atualiza a folha de decisões", "`gabinete/SESSOES.md` e `Decisoes-Pendentes-<data>.xlsx`"),
]


def especialistas(area):
    """(nome, resumo de uma linha, entrega completa em linhas de Markdown) de cada especialista."""
    out = []
    for f in sorted(glob.glob(os.path.join(REPO, "skills", area, "references/especialistas/*.md"))):
        txt = open(f, encoding="utf-8").read()
        m = re.search(r"^# (.+)$", txt, re.M)
        nome = (m.group(1) if m else os.path.basename(f)[:-3]).strip()
        nome = re.sub(r"^(Especialista|Conselheiro|Conselheira)\s*[·:—-]\s*", "", nome)
        nome = re.sub(r"\s*\(.*?\)\s*$", "", nome).replace("Especialista em ", "").replace("Especialista de ", "")
        sec = re.search(r"^## 1\.[^\n]*\n(.+?)(?=^## )", txt, re.S | re.M)
        linhas = []
        if sec:
            for linha in sec.group(1).strip().splitlines():
                t = linha.rstrip()
                if not t.strip() or t.lstrip().startswith(("|", ">", "```")): continue
                t = t.replace("`", "")
                if t.lstrip().startswith(("- ", "* ")) or re.match(r"\s*\d+[.)] ", t):
                    t = "- " + re.sub(r"^\s*(?:[-*]|\d+[.)])\s+", "", t)
                linhas.append(t)
                if len(linhas) >= 14: break
        ent = re.sub(r"[*`]", "", linhas[0] if linhas else "").lstrip("- ").strip()
        ent = re.split(r" Formato\b", ent)[0].rstrip(" :")
        if len(ent) > 230: ent = ent[:227].rsplit(" ", 1)[0] + "…"
        out.append((nome, ent.replace("|", "/"), linhas))
    return out


def entregas():
    f = os.path.join(REPO, "docs/manual-oficial/entregas.json")
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}


def perguntas(area):
    f = os.path.join(REPO, "skills", area, "references/perguntas-ao-dono.md")
    return os.path.exists(f)


FIXO_INICIO = f"""# Manual Oficial dos Agentes · Área Partners

> Versão {VERSAO}, {date.today():%d/%m/%Y}. Substitui a v2.1 e a v2.0 de 23/10/2026 e o Manual dos Agentes v1.0 (13/10/2026). A v2.1 detalha o que cada área e cada especialista entrega. Uso interno. O conteúdo das áreas é lido das próprias skills (`infra/manual_oficial.py`), então este manual se regera quando uma área muda.

## 1. Para que serve este manual
Este é o documento oficial da operação de agentes de IA da Área Partners da Save Co. Ele diz:
- **as regras** que todo agente segue;
- **os fluxos** por onde passa cada pedido, demanda e originação;
- **quem é responsável** por cada área, humano e agente;
- **o que cada área e cada especialista entrega**;
- **onde a entrega fica** (OneDrive, repositório, e-mail ou painel).

A operação tem **25 áreas e {{TOTAL}} especialistas sêniores**, todos no padrão da D93 (nota 100 no auditor em 23/10/2026). Os agentes preparam; quem decide e envia são as pessoas.

## 2. Regras da casa (valem para todos os agentes)
| # | Regra | Fonte |
|---|---|---|
| 1 | Nada é enviado, assinado ou gravado em sistema sem aprovação humana. Os agentes entregam rascunho. | CLAUDE.md §3 |
| 2 | HubSpot e GLPI: só leitura e rascunho. Nunca ler `.env`. | CLAUDE.md §3 |
| 3 | Nunca prometer valor, prazo ou êxito. Todo material externo passa pelo auditor de promessas e pelas áreas envolvidas, e o Luis vê um exemplo antes da execução em massa. | CLAUDE.md §2 |
| 4 | Alíquota zero sai sempre via PER, nunca DCOMP. | D14 |
| 5 | Produtos em validação (Crédito Internacional, Maquila, captação, home equity, turnkey) seguem a trava do G2: sem taxa, prazo, fee ou condição para fora. Exceção: one-page com 7% a 10% como exemplo, definido pelo fundo (D88). | D77, D88 |
| 6 | Produto em validação é desenvolvido por inteiro na base interna, porque já há oportunidades em andamento. A trava vale só para o que se diz ao cliente. | D93 |
| 7 | O dado que falta não trava a construção: segue-se com o que existe, marca-se [pendente: quem fornece] e nunca se inventa o dado. | D97 |
| 8 | LGPD: dado de cliente fica no Mac. Dados de sócios e contatos só em `dados-publicos/receita/prospects-contatos.json`. Não se busca celular pessoal fora do cadastro público. | CLAUDE.md §3 |
| 9 | Não citar cliente pelo nome em material. Casos entram anonimizados. | Regra do Luis |
| 10 | Venda gerencial e conta escrow: só presencial, com o Junior. Os agentes não descrevem a mecânica. | D82 |
| 11 | Visual: Design System Save v0.5 (IBM Plex, ouro como única cor, modo claro para cliente). | Regra do Luis |
| 12 | Toda norma é conferida no texto oficial, com data. O que não foi conferido fica marcado [não confirmado]. | D93 |

## 3. Fluxo único: como um pedido anda
Todo pedido, demanda ou originação segue o mesmo caminho (`infra/fluxo-unico.md`).
1. **Entrada.** Pedido (painel ou e-mail [AGENTES]), demanda (WhatsApp dos Masters e das caixas do time) ou originação (indicação de empresa).
2. **Porteiro.** Antes de produzir, confere se o pedido já existe, é continuação, está travado ou é novo (`infra/ja_existe.py`). Se for repetido, devolve ao Luis o que já existe.
3. **Triagem.** O Gabinete ou a Central identifica o produto (P1 a P18) e a onda da esteira e decide as áreas e a profundidade: consulta rápida, parecer de uma área, comitê de áreas ou Conselho.
4. **Áreas.** O gerente da área distribui ao especialista certo, que trabalha pelo seu arquivo (método, normas, regras da casa).
5. **Revisão do gerente.** Até 2 rodadas. A revisão aprovada registra ajustes concretos ou o motivo de não haver ajuste (`infra/protocolo-gerente.md`).
6. **Devolução em 3 blocos.** O que você pediu; o que você também precisa; o que falta e quem fornece (`infra/padrao-entrega.md`).
7. **Se a área não resolve com os dados,** o especialista escreve o chamado ideal e ele vai para aprovação no painel antes de abrir no GLPI. Contrato vai ao time de Contratos; repasse vai ao Financeiro.

### 3.1 Demandas do WhatsApp dos parceiros
A rotina `whatsapp-caixa-time` lê os grupos dos Masters e as caixas do time (dias úteis, 8h e 14h com IA; 11h e 17h sem IA). Cada mensagem vira uma demanda avaliada pelos agentes:
- **Quem pediu e o que pede:** Master, grupo, horário e o pedido em uma frase.
- **Classificação:** tipo (prazo e intimação, contrato, status de crédito, material, originação…), área responsável, urgência e prazo (o prazo legal vem antes do prazo de tabela) e confiança da leitura.
- **Rota sugerida:** responder direto, pedir à área ou abrir chamado. Status de crédito nunca vira chamado.
- **Rascunho de resposta ao Master:** passa pelo auditor de promessas. Quem envia é a dona da demanda (Daniela nos grupos de Master; Jenifer em indicação de empresa; Geovana em dúvida técnica dirigida a ela).
- **Onde ver:** na seção "WhatsApp · Demandas" do portal (com busca por Master, assunto ou área) e no registro único `registro/demandas.json`.

### 3.2 Chamado no GLPI gerado pelos agentes
Quando a área não resolve com os dados, o especialista escreve o **chamado ideal** (`infra/chamado-ideal.md`): categoria, título, o que entendemos, pedidos objetivos (1 a 5), anexos, o que falta e quem fornece, prazo e motivo. O caminho:
1. **Gerar:** a partir da demanda selecionada ou do resultado da busca, o portal mostra o chamado pronto ("Gerar chamado GLPI").
2. **Aprovar:** a dona da demanda aprova, edita ou recusa com o motivo (D98). Só sobe ao Luis o chamado que toca regra, preço, conflito de canal ou produto em validação.
3. **Abrir:** a rotina abre no GLPI em nome de quem atendeu (`lib/chamados_painel.py aplicar`). Enquanto o TI não libera o acesso ao GLPI (pedido único à TI, 23/10/2026), o chamado aprovado fica como "abrir manualmente", com o texto pronto para copiar.
4. **Fora do GLPI:** contrato, aditivo e distrato vão ao time de Contratos; repasse e prestação de contas, ao Financeiro.

**Quando sobe de nível:** 3 ou mais áreas envolvidas, mudança de regra, mais de R$ 1 mi de crédito com decisão ou produto em validação.

## 4. Portfólio e esteira
A esteira tem três movimentos: **Destravar caixa → Proteger e controlar → Crescer** (D1). O dono da esteira e do mapa da conta é Contas e Soluções.

| Produto | Estado | Dono humano | Área de agentes |
|---|---|---|---|
| Recuperação tributária e recorrência (P1, P2) | Pronto | Time técnico | Tributário, Recuperador, Revisor, Pós-venda |
| Crédito presumido e Funrural (P3) | Pronto (Funrural como passivo, D86) | Time técnico | Tributário, Jurídico |
| Gestão de Contas, antecipação e FIDC (P4, P9, P13) | Pronto | Junior (Save Invest) | Save Invest (D92) |
| Gestão de Passivo (P5) | Pronto | Jurídico | Jurídico, Tributário |
| Passivo bancário (P6) | Em validação | A definir | Internacional |
| Produtos jurídicos (P7) | Pronto | Jurídico | Jurídico |
| Planejamento e reforma (P8) | Pronto | Time técnico | Tributário |
| Estruturação patrimonial (P10) | Pronto | Jurídico | Jurídico |
| Crédito Internacional (P12) | Em validação (G2) | João Mattos | Internacional |
| Home equity (P14) | Em validação | João Mattos | Internacional |
| Maquila e Paraguai (P15) | Em validação | João Mattos | Internacional |
| Captação de capital (P16) | Em validação | João Mattos | Internacional |
| Internacionalização turnkey (P17) | Em validação | João Mattos | Internacional |
| Tax internacional e comércio exterior (P18) | Pronto | Paulo e João Mattos | Internacional |

## 5. Padrão sênior dos especialistas
Cada especialista tem um arquivo próprio (`skills/<área>/references/especialistas/`) com o **perfil** (trajetória equivalente, formação, frameworks, como pensa) e **10 seções**: entrega única, domínio técnico, base normativa com artigo e data, regras da casa, método, perguntas de diagnóstico, armadilhas, casos de referência, fronteiras e atualização (`infra/padrao-senior.md`). O dono do padrão é o Arquiteto de Agentes, e a nota sai de `infra/auditar_senioridade.py`.

A nota mede se o especialista está completo. A qualidade se fecha com a validação humana (D94: Jurídico para Passivo e Patrimonial até 07/11; time técnico para Alíquota Zero e Reforma), com o radar semanal e com a Qualidade medindo os acertos.
"""

FIXO_FIM = """
## 8. Onde ficam as coisas
| O quê | Onde |
|---|---|
| Código, skills, regras e decisões | Repositório `~/agentes-partners` (GitHub `luismelo-lab/agentes-partners`, privado) |
| Cópia viva que os agentes usam | `~/.claude/skills/` e `~/.claude/scheduled-tasks/` |
| Decisões do Luis e do Conselho | `conselho/decisoes.md` (D1 a D97) |
| Folha de decisões para aprovar ou reprovar | `04 · Gestão, Metas e Estratégia/Central de Agentes/Decisoes-Pendentes-<data>.xlsx` |
| Guia das conversas por tema | `gabinete/SESSOES.md` |
| Pedidos do Luis (porteiro) | `registro/pedidos-luis.jsonl` |
| Pastas do time | `Área Partners · Agentes/` (Central Masters · Daniela, Central BDR · Jenifer, Central Técnica · Geovana) |
| Relatórios das áreas | `01 · Comercial e Parceiros/Relatórios das áreas` |
| Gestão, Conselho e resultado | `04 · Gestão, Metas e Estratégia` (Central de Agentes, Conselho, Resultado semanal, Planejamento 2027) |
| Produtos | `03 · Produtos e Projetos` (Crédito Internacional, Maquila) |
| Apresentações e marca | `06 · Marketing e Apresentações` |
| Dados de clientes e fontes oficiais baixadas | `departamentos/<área>/` no Mac, fora do git |

Links do OneDrive saem de `lib/caminhos.py`: só o link de pasta abre, então toda resposta dá o nome do arquivo e o link da pasta.

## 9. Responsabilidades das pessoas
| Pessoa | Responde por |
|---|---|
| **Luis** | Decide o que a matriz de alçada reserva a ele (`infra/alcadas.md`); aprova; faz o merge e o push; responde a folha de decisões (só o que é alçada dele, D98); aprova só os chamados que tocam regra, preço, conflito de canal ou produto em validação (os demais, a dona da demanda) |
| **Daniela** | Masters: demandas, retorno ao parceiro, ganhos a completar no HubSpot, plano de conta |
| **Jenifer** | Prospecção e listas para os Masters |
| **Geovana** | Decisões do Recuperador e do Revisor; diagnóstico |
| **Junior** | Save Invest: Gestão de Contas, antecipação, FIDC; venda gerencial e escrow presencialmente |
| **João Mattos** | Produtos em validação: Crédito Internacional, Maquila, captação, home equity, turnkey |
| **Paulo** | Tax internacional e comércio exterior, com o João |
| **Advogado humano** | Valida Gestão de Passivo e Estruturação Patrimonial (até 07/11) e as minutas |
| **Time técnico** | Valida Alíquota Zero e PER e Reforma; parecer das teses |
| **TI da Save** | Credenciais do Graph e do GLPI, SSO, escopo de arquivos do HubSpot |

## 10. Governança
- **Uma conversa por tema.** Cada tema tem sua seção em `gabinete/SESSOES.md`. Pedido novo passa pelo porteiro.
- **Git.** Cada conversa trabalha na sua branch; o hook `infra/checar-dados.py` precisa dar 0 achados; o Luis faz o merge (`cd ~/agentes-partners && git merge --no-edit <branch> && git push`).
- **Cópia viva.** Ao alterar uma skill ou rotina, copiar para `~/.claude/` depois de conferir que a cópia viva é igual ao HEAD.
- **Decisões.** Viram D-número em `conselho/decisoes.md`. As pendentes vão para a folha com campos de seleção (Aprovar, Aprovar com ajuste, Reprovar, Decidir depois), e a consolidação de sexta aplica as respostas.
- **Perguntas ao dono.** Cada área mantém `references/perguntas-ao-dono.md`, com data e por que importa.

## 11. Pendências abertas (23/10/2026)
| # | Pendência | Quem resolve |
|---|---|---|
| 1 | T07 (ISS fora da base, Tema 118 julgado em 21/10) volta à vitrine? Via da T15 (Tema 843) | Luis e time técnico |
| 2 | Meta do Q4 de R$ 200 mi: crédito ou líquido? | Luis |
| 3 | Transação de pequeno valor da Receita até 30/10: triagem da carteira | Luis |
| 4 | WhatsApp da cobrança sem a API oficial (D97) | Junior e Jurídico |
| 5 | Dono do passivo bancário; regras do Paulo de 21/10 como D-número | Luis |
| 6 | Nomes dos validadores do Jurídico e do time técnico (D94) | Luis |
| 7 | Papel da Federal Invest na CVM; razão social e CNPJ da Save Invest | Junior |
| 8 | Credenciais do Graph e do GLPI | TI |
| 9 | CNPJ alfanumérico nos scripts | Conversa própria, em andamento |
| 10 | Contraste do ouro #B58A1F em texto corrido (3,17:1) | Luis e Marketing |

## 12. Glossário
- **Área:** grupo de agentes com um gerente e especialistas (uma skill).
- **Especialista sênior:** agente com uma entrega única e arquivo próprio no padrão D93.
- **Porteiro:** checagem de repetição antes de executar um pedido.
- **Esteira:** Destravar caixa → Proteger e controlar → Crescer.
- **G2:** portão do produto novo; antes dele, nada de taxa, prazo ou fee para fora.
- **PER:** pedido eletrônico de ressarcimento. **DCOMP:** declaração de compensação.
- **3 blocos:** o que você pediu; o que você também precisa; o que falta e quem fornece.
- **Cópia viva:** a versão das skills e rotinas que os agentes executam, em `~/.claude/`.
"""


def gerar():
    linhas, total = [], 0
    linhas.append("## 6. As áreas: missão, responsáveis, especialistas e onde entregam")
    linhas.append("Cada área tem um gerente, que distribui e revisa, e especialistas sêniores com uma entrega única. As perguntas que só as pessoas respondem ficam em `references/perguntas-ao-dono.md` de cada área.")
    n = 0; E = entregas()
    for bloco in ORDEM_BLOCOS:
        linhas.append(f"\n### Bloco: {bloco}")
        for area, (nome, b, missao, dono, onde) in AREAS.items():
            if b != bloco: continue
            n += 1; esp = especialistas(area); total += len(esp); e = E.get(area, {})
            linhas.append(f"\n### 6.{n} {nome}\n")
            linhas.append(f"- **Missão:** {missao}")
            linhas.append(f"- **Dono humano:** {dono}")
            if e.get("quem_usa"): linhas.append(f"- **Quem usa e quando:** {e['quem_usa']}")
            linhas.append(f"- **Onde entrega:** {onde}")
            if e.get("como_acionar"):
                linhas.append("- **Como acionar:** " + "; ".join(x.rstrip(".") for x in e["como_acionar"]) + ".")
            if e.get("entregas"):
                linhas.append("\n**O que a área entrega**\n")
                linhas.append("| Entrega | O que vem | Formato e arquivo | Quando | Quem recebe e onde |\n|---|---|---|---|---|")
                for x in e["entregas"]:
                    cel = lambda k: str(x.get(k) or "—").replace("|", "/").replace("\n", " ")
                    arq = cel("formato") + ("" if cel("arquivo") in ("—", "") else " · " + cel("arquivo"))
                    linhas.append(f"| {cel('entrega')} | {cel('conteudo')} | {arq} | {cel('quando')} | {cel('quem_recebe')} · {cel('onde')} |")
            linhas.append(f"\n**Especialistas e o que cada um entrega ({len(esp)})**\n")
            for nm, _, full in esp:
                linhas.append(f"**{nm}.** " + (full[0].lstrip("- ") if full else ""))
                linhas.extend(full[1:])
                linhas.append("")
            if e.get("nao_faz"):
                linhas.append("**O que a área não faz:** " + "; ".join(x.rstrip(".") for x in e["nao_faz"]) + ".")
    linhas.append("\n## 7. Rotinas automáticas")
    linhas.append("| Rotina | Quando | O que entrega | Onde |\n|---|---|---|---|")
    for r in ROTINAS: linhas.append("| " + " | ".join(r) + " |")
    md = FIXO_INICIO.replace("{TOTAL}", str(total)) + "\n" + "\n".join(linhas) + "\n" + FIXO_FIM
    open(SAIDA_MD, "w", encoding="utf-8").write(md)
    print("ok", SAIDA_MD, n, "áreas", total, "especialistas")
    return total


if __name__ == "__main__":
    gerar()
    if "--docx" in sys.argv:
        import caminhos
        saida = os.path.join(caminhos.luis("central"), f"Manual-Oficial-dos-Agentes-v{VERSAO}.docx")
        env = dict(os.environ, NODE_PATH=os.path.expanduser("~/.partners-node/node_modules"), DOC_MD=SAIDA_MD,
                   DOC_VERSAO=f"Versão {VERSAO} · {date.today():%d/%m/%Y}", DOC_CABECALHO="Manual Oficial dos Agentes · Área Partners",
                   DOC_SELO="Uso interno")
        subprocess.run(["node", os.path.join(REPO, "departamentos/produtos/credito-internacional/scripts/gerar_manual_docx.js"), saida], check=True, env=env)
        print("ok", saida)
