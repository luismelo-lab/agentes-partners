# Arquitetura de Agentes — Área Partners (Save Company)

**Versão:** 1.1 (2026-10-02) · **Dono:** Luis Fernando de Melo

## Princípio que vale para tudo

> **Nenhum agente ou subagente executa nada sem a validação de um humano.**
> Agentes analisam, organizam e rascunham. Quem aprova e aciona é sempre uma pessoa.

Na prática, todos os agentes operam no **nível N1 (rascunho + aprovação)**. Isso só muda se o Luis decidir explicitamente, por escrito, para uma tarefa específica. Exceções aprovadas até 02/10, todas só com e-mail interno (@savecompany.com.br): D23 (e-mails do WhatsApp), D24 (respostas da Central), D26 (plano do dia e avisos) e D27 (lote do Recuperador). D25: chamado no GLPI só depois de aprovado no painel.

## Como a estrutura funciona (os 3 conceitos)

- **Agente orquestrador:** é o "coordenador" de cada pessoa. Recebe a demanda, entende o que é e decide qual especialista chamar. É como um bom assistente que sabe para quem repassar cada assunto.
- **Subagente especialista:** conhece a fundo uma área de apoio (ex.: Pós-venda). Prepara o pedido no formato certo para aquela área e sabe as regras dela.
- **Portão de aprovação:** o ponto em que o trabalho para e espera a pessoa aprovar. Existe em todo lugar em que algo sai para fora (parceiro, área de apoio, HubSpot, GLPI).

## Porta de entrada: o Gabinete
Toda necessidade do Luis entra pelo **Chefe de Gabinete** (skill `gabinete`), que decide **quem** participa e **com que profundidade**:

| Nível | Quando | Quem |
|---|---|---|
| 1 · Consulta rápida | Dúvida objetiva, baixo impacto | 1 especialista |
| 2 · Parecer de área | Construir ou validar algo dentro de uma área | 1 departamento |
| 3 · Comitê | O tema cruza 2 a 4 áreas | Só as áreas necessárias |
| 4 · Conselho pleno | Decisão estratégica, irreversível ou que vai à liderança | Conselho (com as áreas como embasamento) |

O Gabinete mostra a **Ficha de Rota** (quem entra, por quê e o que entrega) e só aciona as áreas depois do "ok". Regras de quem entra em cada tema: `~/.claude/skills/gabinete/references/matriz-roteamento.md`.

## Organograma

```
                         LUIS — Gerente Comercial Masters
                         (gestor de toda a operação)
                                     │
                         CONSELHO CONSULTIVO do Luis
                                     │
   ┌─────────────────────────────────┼─────────────────────────────────┐
 DANIELA MACIEL                GEOVANA GONÇALVES                  JENIFER CARVALHO
 Gestora de Contas Masters     Suporte Técnico Comercial          BDR Masters
 (advogada)                    (contadora)                        (clientes + novos parceiros)
   │                                 │                                  │
 Orquestrador "Central Masters"  Orquestrador "Central Técnica"   Orquestrador "Central BDR"
   │                                 │                                  │
   ├─ Triagem & Roteamento           ├─ ★ Revisor de Diagnóstico        ├─ Pesquisa de Contas-Alvo
   ├─ Acompanhamento & SLA           │    (2ª opinião antes da          ├─ Qualificação & Score
   ├─ Retorno ao Parceiro            │     apresentação)                ├─ Abordagem Personalizada
   ├─ ★ Briefing de Conta Master     ├─ ★ Recuperador de Perdidos       ├─ Pré-análise Rápida (potencial)
   ├─ ★ Plano de Conta (por Master)  │    e Zerados                     ├─ Registro no HubSpot
   ├─ ★ Saúde do Parceiro            ├─ Preparador de Reunião Técnica   ├─ ★ Recrutador de Parceiros
   └─ Apoio Jurídico Geral           ├─ Tira-dúvidas Fiscal/Tributário  │    Indicadores
                                     ├─ Tradutor Técnico → Comercial    ├─ ★ Onboarding do Indicador
                                     └─ Pós-reunião (ata e próximos     └─ Distribuição Lead → Master
                                        passos)
        │                                 │                                  │
        └──────── pedem trabalho aos DEPARTAMENTOS VIRTUAIS (ver DEPARTAMENTOS.md) ─────┘
```

## Status 29/09
Células construídas em v1: **Daniela** (`celula-daniela`, 8 subagentes, com a caixa do WhatsApp via Eazybe), **Jenifer** (`celula-jenifer`, 9 subagentes) e **Geovana** (`recuperador` + `revisor-diagnostico`). Os subagentes finais estão nos SKILL.md de cada célula (fusões: Briefing, Saúde e Plano de Conta viraram "Conta Master"; Registro no HubSpot e Distribuição Lead → Master viraram um só; Onboarding do Indicador entrou no Recrutamento). Todas as 13 áreas de apoio estão em v1.

## Status 02/10 · operação contínua
- **Terminal sem IA (`bin/partners` + 7 jobs do launchd):** HubSpot, WhatsApp, Central, sentinelas, plano do dia (7h30), aviso da tarde (13h30), OneDrive e backup (19h30).
- **Sentinelas (`lib/operacao.py`, D26):** acham negócios parados, conflitos, CRM incompleto, parceiros inativos, demandas e aprovações atrasadas e rotinas com falha. Cada evento vai para o dono do negócio no HubSpot. Fluxos entre agentes sem aprovação: Revisor nos negócios que entram em apresentação, rascunho de cobrança auditado, cadastro da Receita ao lado do CRM incompleto.
- **Proteções (`lib/protecao.py`):** trava de domínio em todo envio, mascaramento de dados pessoais e auditor de promessas.
- **Sistemas externos:** HubSpot só leitura; GLPI em rascunho até o cliente OAuth (chamado só depois da aprovação no painel); Bitrix só consulta e desligado até o webhook; Microsoft (Graph/Teams) desligado até a TI.

## As células em detalhe

### Daniela — de "apoio geral" a **Gestora de Contas Masters**
**Hoje:** ponto focal dos 9 Masters; maior tempo de casa e relacionamento; advogada; resolve necessidades gerais.
**Visão com agentes:** os agentes absorvem a "ponte" (receber, encaminhar, cobrar, devolver) e ela sobe para **gestão estratégica das contas**, que é o papel de Partner Account Manager nos programas de parceiros maduros.

| Subagente | O que faz | Usa |
|---|---|---|
| Triagem & Roteamento | Entende o pedido (WhatsApp/GLPI), aponta o que falta, formata para a área certa | Departamentos virtuais |
| Acompanhamento & SLA | Painel de pendências por Master, alerta atrasos, rascunha cobranças | GLPI, planilha de controle |
| Retorno ao Parceiro | Rascunha status e respostas | — |
| ★ Briefing de Conta Master | Antes de cada reunião: pipeline, ganhos, pendências, histórico do Master | Cockpit Master, HubSpot |
| ★ Plano de Conta | Plano trimestral por Master: metas, oportunidades, riscos | Cockpit, Inteligência Comercial |
| ★ Saúde do Parceiro | Sinais de queda (menos indicações, reclamações, atrasos) | Partner Success, Dados & BI |
| Apoio Jurídico Geral | Pré-análise jurídica que ela valida com a formação dela | `depto-juridico` |

**Supervisiona também:** é a curadora natural do Departamento Jurídico virtual (valida a linguagem para os parceiros) e parceira do Partner Success.

### Geovana — **Suporte Técnico Comercial** (a célula com impacto direto em receita)
**Hoje:** reuniões técnicas com parceiros e clientes; dúvidas fiscais e tributárias; contadora; **revisa os negócios em fase de apresentação de diagnóstico** para achar o que o técnico não pegou; **revisa negócios perdidos e zerados** e orienta o parceiro para reanálise.

| Subagente | O que faz | Usa |
|---|---|---|
| ★ Revisor de Diagnóstico | "Segunda opinião" sistemática: cruza o perfil da empresa (CNAE, regime, folha, UF) com o checklist de teses e aponta **oportunidades não levantadas** | `depto-tributario`, HubSpot |
| ★ Recuperador de Perdidos e Zerados | Classifica o motivo (documento faltante, período, tese, regime), define o que falta e rascunha a orientação ao parceiro | HubSpot, `depto-tributario` |
| Preparador de Reunião Técnica | Resumo do parecer, 3 mensagens-chave, objeções prováveis com resposta e fonte | `depto-tributario` |
| Tira-dúvidas Fiscal/Tributário | Resposta com fonte oficial, vigência e grau de risco | `depto-tributario` |
| Tradutor Técnico → Comercial | Versão do parecer em linguagem de negócio para o parceiro | — |
| Pós-reunião | Ata, próximos passos, atualização sugerida no HubSpot | — |

**KPIs que já existem no cockpit dela:** valor recuperado, taxa de reversão, pareceres, SLA. São a linha de base pronta para medir o piloto.
**Supervisiona também:** curadora natural do Departamento Tributário virtual.

### Jenifer — **BDR Masters** (duas frentes: clientes e novos parceiros)
**Hoje:** prospecta clientes nos segmentos-chave para os Masters e prospecta **novos parceiros indicadores** que alimentam os Masters.

| Subagente | O que faz | Usa |
|---|---|---|
| Pesquisa de Contas-Alvo | Listas por segmento-chave e região do Master | save-crm, Inteligência Comercial |
| Qualificação & Score | Prioriza por aderência (ICP) e sinais de compra | Inteligência Comercial |
| Abordagem Personalizada | Cadência e mensagens por persona (sócio, CFO, contador) | Marketing (Demanda/ABM) |
| Pré-análise Rápida | "Esta empresa tem cara de quais teses?" (indicativo, sem valores) | `depto-tributario` |
| Registro no HubSpot | Rascunha o registro do negócio para ela aprovar | HubSpot |
| ★ Recrutador de Parceiros Indicadores | Mapeia escritórios contábeis com carteira aderente na região do Master | Inteligência Comercial |
| ★ Onboarding do Indicador | Kit de boas-vindas e primeiros 30 dias | Partner Success, Marketing |
| Distribuição Lead → Master | Sugere qual Master recebe o lead, sem conflito de canal | Inteligência Comercial |

**Supervisiona também:** curadora natural da Inteligência Comercial.

> ★ = papel que não estava nas suas descrições e foi proposto a partir de boas práticas de programas de parceiros.

## O fluxo de uma demanda (célula da Daniela como exemplo)

```
Parceiro (WhatsApp/GLPI)
   │
   ▼
[Orquestrador] entende o pedido, identifica a área e o que falta
   │
   ▼
[Subagente Pós-venda] prepara o pedido no formato da área
   │
   ▼
🔒 PORTÃO 1 — Daniela aprova/edita o encaminhamento → ela envia à área
   │
   ▼
[Subagente Acompanhamento] monitora prazo, avisa atrasos, rascunha cobrança
   │
   ▼
🔒 PORTÃO 2 — Daniela aprova a cobrança (se houver)
   │
   ▼
[Subagente Retorno] rascunha a resposta/status para o parceiro
   │
   ▼
🔒 PORTÃO 3 — Daniela aprova → ela envia ao parceiro
```

## Conselho Consultivo do Luis

Um grupo de agentes que atua como o conselho de uma grande empresa, cada um com uma especialidade, e que **só aconselha**.

| Conselheiro | Especialidade | Pergunta que sempre faz |
|---|---|---|
| Presidente do Conselho | Conduz, sintetiza, registra a ata | "Qual é a decisão que o Luis precisa tomar?" |
| Estratégia & Crescimento | Foco, prioridades, posicionamento | "Isso nos leva à meta ou só ocupa tempo?" |
| Comercial & Parcerias | Parceiros, pipeline, novas oportunidades | "Isso gera mais negócio com os parceiros?" |
| Operações, Processos & Tecnologia | Fluxo, SLA, GLPI, IA, gargalos | "Onde isso trava e como escala?" |
| Pessoas & Liderança | Desenvolvimento do time, engajamento, carga | "Como isso afeta e desenvolve as pessoas?" |
| Finanças & Resultado | Receita, margem, ROI, custo | "Quanto custa, quanto retorna, em quanto tempo?" |
| Risco, Tributário & Jurídico | Compliance, RFB, contratos, LGPD, reputação | "O que pode dar errado e qual o impacto?" |

**Dois modos de uso:**
1. **Reunião semanal** (automática, após aprovação do agendamento): analisa a operação da semana e entrega a ata com sugestões, plano de ação e desenvolvimento de pessoas.
2. **Consulta:** o Luis manda um plano ou estratégia; cada conselheiro dá seu parecer ponto a ponto; o conselho debate e recomenda o melhor caminho.

**Regras do Conselho:**
- Cada conselheiro forma sua opinião **de forma independente** antes de ver a dos outros (evita "efeito manada").
- Divergências são registradas, não escondidas.
- Dúvidas que impedem uma boa recomendação vão para o Luis antes da conclusão.
- A ata sempre termina com **"Decisões aguardando sua aprovação"**. Nada é executado.

## Ordem de construção (e por quê)

| Ordem | O quê | Por quê |
|---|---|---|
| 1 | **Conselho do Luis** | Risco zero (só aconselha), não depende do diagnóstico do time e já ajuda a analisar os resultados da Fase 1 |
| 2 | Diagnóstico e priorização (Fases 1–2) | Define os subagentes reais de cada célula |
| 3 | **Célula piloto** (provavelmente a da Daniela: mais frentes e mais "ponte") | Maior volume de trabalho braçal = maior ganho visível |
| 4 | Demais células | Reaproveitam a base de conhecimento das áreas de apoio já montada no piloto |

## Base de conhecimento compartilhada

Os subagentes das áreas de apoio (Tributário, Jurídico, Contratos, Pós-venda, Marketing) usam **a mesma base** nas três células. Monta-se uma vez, usa-se três vezes.

```
agentes-partners/
  conhecimento/
    areas/tributario/  juridico/  contratos/  pos-venda/  marketing/
    parceiros/        (roster, contatos, particularidades)
    padroes-resposta/ (exemplos de boas respostas)
```
