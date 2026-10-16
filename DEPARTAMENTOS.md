# Departamentos Virtuais — v2

**Versão:** 2.0 (2026-09-28) · **Dono:** Luis Fernando de Melo
**O que mudou da v1:** cada área foi redesenhada a partir de pesquisa de boas práticas (consultorias tributárias, jurídicos corporativos, programas de parceiros), não só dos exemplos iniciais. Técnico Contábil foi fundido ao Tributário. Entraram 6 áreas novas.

## A ideia em uma frase
Cada área tem um **Gerente** (agente que recebe, planeja e distribui) e **especialistas** (subagentes). O departamento virtual **não substitui a área real**: prepara o trabalho para a área real e o time Partners validarem.

## Regras que valem para todos
1. **Portão 0 (plano)** e **Portão final (entrega):** nada começa sem "ok" e nada sai sem aprovação humana.
2. **Tributário e Jurídico:** só pré-análise, com fonte oficial citada e datada, validada por técnico/advogado humano.
3. **Revisor em todo departamento.**
4. **Dono humano** da área real para cada departamento.
5. **Os departamentos se ajudam:** Marketing pede embasamento ao Tributário; o Conselho pede dados oficiais ao Tributário e ao Jurídico; a Inteligência Comercial alimenta a Geração de Demanda.

## Mapa geral

```
                                LUIS (gestor)
                                     │
                 CONSELHO ◄──── embasamento técnico ────┐
                                     │                   │
          Células:  DANIELA  ·  GEOVANA  ·  JENIFER      │
                                     │                   │
 ─────────────────────── DEPARTAMENTOS VIRTUAIS ─────────┴──────────────────────
  NÚCLEO TÉCNICO (core)   │  CRESCIMENTO DE CANAL          │  OPERAÇÃO E BASE
  • Tributário & Contábil │  • Partner Success & Enablement │  • Operações de Canal
  • Jurídico              │  • Inteligência Comercial       │    & Comissionamento
  PRODUTOS NOVOS          │  • Marketing de Canal           │  • Contratos
  • Produtos Internacionais│                                 │  • Pós-venda
    e Financeiros         │                                 │
                          │                                 │  • Dados & BI
                          │                                 │  • TI, Automação & Gov. IA
                          │                                 │  • Qualidade & Ouvidoria
```

---

## PESSOAS

### Pessoas — ✅ construído (skill `depto-pessoas`) · ★ área nova (28/09)
*Sua necessidade:* apoio na construção e validação de temas de pessoas. *Proposta:* HRBP virtual + 8 especialistas (Metas & Desempenho · Feedback/1:1 & Coaching · Desenvolvimento & PDI · Cargos/Carreira & Sucessão · Remuneração & Reconhecimento · Atração/Onboarding/Offboarding · Clima & Engajamento · People Analytics & Compliance). Começa por Feedback, PDI e Metas. Desligamento, assédio, salário, cargo e bônus: só **pauta** para o RH formal e o Jurídico.

## NÚCLEO TÉCNICO

### Tributário & Contábil — ✅ construído (skill `depto-tributario`)
*Sua ideia:* especialistas fiscais, contábeis e de planejamento. *Proposta:* matriz de **linhas técnicas × setor**, como nas grandes consultorias, voltada ao negócio do cliente.

| Especialista | Pergunta de negócio que responde |
|---|---|
| Gerente Tributário | Vale abordar? Qual prioridade e risco? |
| PIS/COFINS | Há crédito não aproveitado nos últimos 5 anos? |
| ICMS / Estadual | ST pago a maior? Crédito acumulado a monetizar? |
| Previdenciário / Folha | A folha tem contribuição indevida? |
| IRPJ/CSLL & Regimes | Qual regime é mais eficiente? |
| Incentivos Fiscais | Há incentivo que o cliente não usa? |
| **Especialista Agro** ★ | PF ou PJ rural? Crédito presumido? |
| **Reforma Tributária** ★ | Quanto muda a margem até 2033? O que fazer com os créditos antigos antes da extinção? |
| **Jurisprudência & Teses** ★ | A tese está pacificada? Houve modulação? |
| Contábil / CPC | Como contabilizar? Qual o efeito no EBITDA? |
| **SPED & Tax Tech** ★ | O que os arquivos do cliente mostram? |
| **Inteligência Setorial & Macro** ★ | O cliente paga mais imposto que o setor? |

Fontes oficiais com hierarquia (Constituição → lei → decreto → IN → precedente vinculante → COSIT → CARF → doutrina) e cronograma da reforma embutidos.

### Jurídico — ✅ construído (skill `depto-juridico`)
*Sua ideia:* contratos, notificações da RFB, apoio em reuniões. *Proposta:* modelo "hub & spoke", com **controle de prazos em dupla checagem** e compliance de marketing jurídico.

Gerente Jurídico · **Controle de Prazos** ★ · Contencioso Administrativo Tributário · Contencioso Judicial & Precedentes · **Recuperação de Créditos & Compensação** ★ · Contratos · LGPD & Privacidade · **Compliance Ético & Marketing Jurídico** ★ · **Apoio Jurídico Comercial** ★ · **Pesquisa & Jurimetria** ★

⚠️ Ponto de atenção levantado na pesquisa: se a Save atua como sociedade de advogados, o **repasse ao parceiro contador precisa ser estruturado como indicação comercial**, não como divisão de honorários (art. 34 da Lei 8.906/94). Vale validar com o Jurídico real.

---

## CRESCIMENTO DE CANAL

### Produtos Internacionais e Financeiros — ✅ construído 16/10 (skill `depto-internacional`) · ★ área nova
*Base:* reunião com o João Mattos (30/09), reunião de estruturação comercial do fundo/crédito internacional para café e agro (02/10), documento interno v2.3 (07/10), Maquila v0.9 (09/10) e ecossistema financeiro (13/10). *Equipe:* Gerente de Produtos Internacionais · Qualificador de Crédito Internacional · Estruturador de Garantias & Projeto · Especialista Café & Agro · Especialista Maquila & Internacionalização · Analista do Ecossistema Financeiro · Regulatório & Câmbio · Guardião do Produto Novo · Revisor de Linguagem & Promessas. *Trava:* nada de taxa, prazo ou fee com parceiro ou cliente antes do G2; a Save é estruturadora, nunca credora; o dono do produto (João) decide. Pedidos PI1–PI5 na Central.

### Partner Success & Enablement — ✅ construído 29/09 (skill `depto-partner-success`) · ★ área nova (maior valor segundo a pesquisa)
*Por quê:* é o modelo de receita da Save. Parceiro capacitado indica mais e melhor.
Gerente de Partner Success · Designer da **Academia de Parceiros** (trilhas por tese, certificação) · **Coach de Onboarding** (plano 30/60/90 dias) · **Analista de Saúde do Parceiro** (risco de abandono) · Gestor de **Níveis & Benefícios** (programa em tiers, ex.: Masters)
*Métricas:* tempo até o 1º negócio, % de parceiros certificados e ativos, retenção.

### Inteligência Comercial — ✅ construído 29/09 (skill `depto-intel-comercial`: ICP medido no HubSpot, território, lead scoring v1) · ★ área nova
Gerente de Inteligência · **Arquiteto de ICP & Segmentação** (CNAE, regime, porte, UF) · **Minerador de Dados Públicos** (CNPJ aberto da Receita, IBGE, CAGED, CONAB/MAPA) · **Analista de Sinais de Compra** (contratações, filiais, safra, mudança de regime) · **Lead Scoring** (para o HubSpot) · **Planejador de Territórios** (conta × parceiro, sem conflito de canal) · **Analista de Concorrência** · **Recrutamento de Parceiros** (escritórios contábeis com carteira aderente)
*Reaproveita:* save-crm (base Agro Lucro Real).

### Marketing de Canal — ✅ construído v2 (skill `depto-marketing`)
*Sua ideia:* gerente, conteúdo, designer, comunicação. *Proposta:* cobrir as três frentes do marketing de canal (para, através e com o parceiro).
Gerente · Estrategista de Campanhas & Calendário *(fundiu com o Planejador)* · Redator · Designer · **Enablement de Vendas do Parceiro** ★ · **Co-branding (através do parceiro)** ★ · **Demanda / ABM de Canal** ★ · **Eventos & Webinars** ★ · Comunicação com Parceiros & PRM *(ampliado)* · **Autoridade Digital (LinkedIn/SEO/PR)** ★ · Curador de Notícias & Pautas · Revisor de Marca & Compliance

---

## OPERAÇÃO E BASE

### Operações de Canal & Comissionamento — ✅ construído 29/09 (skill `depto-operacoes-canal`) · ★ área nova (alto valor)
*Por quê:* o honorário de êxito gera repasse ao parceiro. Atraso ou erro no repasse destrói a confiança.
Analista de **Comissionamento** (cálculo e conferência de repasses) · Gestor de **Registro de Oportunidades & Conflito de Canal** · Analista de **Termos de Parceria**

### Contratos — ✅ construído 29/09 (skill `depto-contratos`)
Montador de Minuta · Conferente de Dados · Controle de Assinaturas · Distratos

### Pós-venda — ✅ construído 29/09 (skill `depto-pos-venda`)
Avisos de Pagamento · Compensações de Ofício · Controle de Guias · Extrato & Saldo · Comunicação Pós-venda

### Resultados & Controladoria — ✅ construído (skill `depto-resultados`) · ★ área nova
*Seu pedido:* entrega semanal de resultados (volume criado e fechado, margem, margem líquida, lucro da área, fator e % de crescimento, ROI total e líquido). *Proposta:* um departamento com **Controller** + Engenheiro de Dados, Guardião de Qualidade, Analista de Margem, Analista de DRE da área, Analista de Crescimento & Forecast, Analista de ROI & Caixa, Redator Executivo e Designer de Apresentação. **Números calculados por script, nunca pela IA.** Entrega: deck de 8 slides + one-pager.
*Métricas acrescentadas (pesquisa):* receita em 4 camadas (contratada, ajustada ao risco, reconhecida, recebida), backlog com aging, prazo até o caixa, mix por variante, win rate, ciclo, ticket, cobertura de pipeline, acurácia do forecast, concentração, parceiros ativos, margem por colaborador, margem de contribuição, EBITDA da área, custo por oportunidade, CAC/payback, glosa por tese, qualidade de dados.

### Dados & BI — ✅ construído 29/09 (skill `depto-dados`: qualidade do CRM + scorecard de saúde dos parceiros) · ★ área nova
**Guardião de Qualidade do CRM** (duplicados, campos obrigatórios, vínculo empresa-parceiro) · **Engenheiro de Dados** (HubSpot → dashboards) · **Governança & Dicionário de Dados** (o que é "parceiro ativo") · **Analista de BI** (S&OE, cockpit Master) · **Analista de Forecast** · **Performance de Canal** (scorecard de parceiros)
*Reaproveita:* S&OE, cockpit Master, soe-agent. *Resolve:* as propriedades de margem que faltam no HubSpot.

### TI, Automação & Governança de IA — ✅ construído 29/09 (skill `depto-ti`) · ★ área nova
**Arquiteto de Integrações** (HubSpot, GLPI, WhatsApp Business API oficial) · **Automação de Processos** (abertura de chamado, roteamento, SLA) · **Segurança & Acessos** · **Privacidade / LGPD técnica** (opt-in no WhatsApp, retenção) · **Governança de IA** (inventário de agentes, registro de decisões, testes de alucinação; referências NIST AI RMF e ISO/IEC 42001) · **Administrador GLPI**
*Por quê agora:* o GLPI está sendo implantado, e este departamento é quem desenha o GLPI "pronto para agente".

### Qualidade & Ouvidoria — ✅ construído 29/09 (skill `depto-qualidade`) · ★ área nova (médio-alto)
NPS de parceiros e de clientes · análise de reclamações do GLPI · **auditoria de promessas comerciais** (protege a marca em serviço com risco tributário)

### Customer Success do cliente final — 💡 futuro
Acompanha o crédito após a venda e busca novas teses para o cliente (junto com o parceiro). Entra depois de Partner Success e Operações de Canal.

---

## Ordem de construção sugerida (v2)
| # | Departamento | Por quê |
|---|---|---|
| ✅ | Tributário, Jurídico, Marketing | Já construídos: núcleo técnico + pedidos concretos |
| ✅ | Resultados & Controladoria | Construído em 28/09 a pedido do Luis |
| 1 | **TI, Automação & Gov. IA** (só a parte do GLPI) | Janela única: o GLPI está sendo implantado agora |
| 2 | **Partner Success & Enablement** | Maior impacto na receita via parceiros |
| 3 | **Operações de Canal & Comissionamento** | Confiança do parceiro |
| 4 | Inteligência Comercial | Alimenta a Jenifer e a Demanda/ABM; reaproveita o save-crm |
| 5 | Dados & BI | Base para medir tudo; reaproveita os dashboards |
| 6 | Pós-venda, Contratos, Qualidade | Priorizar pelos números do mapa de tarefas |
