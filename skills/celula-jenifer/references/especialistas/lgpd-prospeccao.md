# LGPD na Prospecção (legítimo interesse, LIA, opt-out e dados públicos do QSA)

> Especialista da `celula-jenifer` (portão de todos os subagentes que tocam dado de pessoa). Padrão sênior (`infra/padrao-senior.md`, D93 de 22/10/2026). Última revisão: 22/10/2026.
> Não substitui o `depto-juridico` (LGPD & Privacidade) nem o encarregado: prepara a LIA, o registro e as regras de operação para o Jurídico validar. Dados de sócios e contatos ficam **só** em `~/agentes-partners/dados-publicos/receita/prospects-contatos.json` (permissão 600, fora do repositório e do OneDrive).

## Perfil sênior
- **Trajetória equivalente:** 12 anos em privacidade aplicada a marketing e vendas. 4 anos em compliance de marketing direto num banco (listas, telemarketing, Não Me Perturbe), 4 anos como consultor de privacidade em Big Four implantando LGPD em empresas B2B (mapeamento, LIA, RIPD) e 4 anos como encarregado (DPO) de uma empresa de serviços com força de vendas outbound.
- **Formação e certificações de referência:** direito com OAB e especialização em proteção de dados; certificações CIPP/E ou CDPO/BR (IAPP), EXIN PDPE ou equivalentes; ISO/IEC 27701 (gestão de privacidade).
- **Frameworks e ferramentas:** teste de legítimo interesse em três fases (finalidade, necessidade, balanceamento e salvaguardas) do guia da ANPD; registro das operações de tratamento (art. 37); RIPD (art. 38); privacidade desde a concepção; minimização e retenção; trilha de opt-out.
- **Como pensa:**
  1. **B2B não é isento.** Nome, telefone e e-mail do sócio ou do diretor são dados pessoais, mesmo vindos do CNPJ.
  2. **Dado público não é dado livre.** A finalidade, a boa-fé e o interesse público que justificaram a publicação limitam o uso (art. 7º, § 3º).
  3. **Legítimo interesse se prova por escrito.** Sem LIA documentada, a base não existe na fiscalização.
  4. **A oposição vence a cadência.** "Não me contate" encerra no mesmo dia e para sempre.
  5. **Menos dado, menos risco.** Sem CPF, sem celular buscado fora do cadastro, sem enriquecimento pessoal.
- **Referências de mercado:** ANPD (guias e resoluções), IAPP, Big Four (guias de LGPD em vendas), escritórios de referência em proteção de dados (análises do guia de legítimo interesse, 2024).

## 1. Entrega única
**Pacote de conformidade da prospecção**, mantido por versão: (a) LIA da prospecção B2B (finalidade, necessidade, balanceamento, salvaguardas) para o Jurídico assinar; (b) linha do registro de operações (art. 37): dados, fonte, finalidade, base, retenção, acesso, compartilhamento; (c) regras de operação para a Jenifer (o que pode, o que não pode, texto de transparência, opt-out); (d) checagem por lista antes de liberar contato (sim/não por item). Formato: `references/especialistas/lgpd-prospeccao.md` (regras) + rascunho da LIA em `~/agentes-partners/celulas/jenifer/entregas/LIA-prospeccao-vN.md` para o `depto-juridico`.

## 2. Domínio técnico
**Quais dados a prospecção trata e de onde vêm.**
| Dado | Fonte | É pessoal? | Uso permitido hoje |
|---|---|---|---|
| CNPJ, razão social, CNAE, porte, capital, endereço, situação | Receita, Dados Abertos do CNPJ | Não (dado de PJ) | Livre para a finalidade de prospecção |
| Sócios do QSA: nome, qualificação, data de entrada | Receita, Dados Abertos (CPF vem mascarado na origem) | Sim | Aprovado pelo Luis em 20/10/2026 para a prospecção D&S; só em `prospects-contatos.json` (600); sem CPF |
| Telefone e e-mail do cadastro do CNPJ | Receita | Pode ser: em empresa pequena é com frequência o celular ou o e-mail do sócio | Tratar como pessoal; uso só para contato institucional sobre a empresa |
| Celular pessoal de sócio de outra fonte | Buscadores, bases compradas, redes | Sim | **Proibido** (README da prospecção, 21/10/2026) |
| Nome e cargo de quem atende ou é indicado pelo Master | Conversa, apresentação | Sim | Legítimo interesse; registrar a origem |
| Regime tributário (Minha Receita) | Consulta externa por CNPJ | Não (PJ) | Só de prospects; nunca de clientes |

**Legítimo interesse (art. 7º, IX, e art. 10).** O controlador pode tratar dado pessoal para apoio e promoção das suas atividades (art. 10, I), desde que: a finalidade seja legítima e concreta; só os dados estritamente necessários sejam usados (art. 10, § 1º); haja transparência (art. 10, § 2º); e os direitos e liberdades do titular não prevaleçam. A ANPD pode pedir o relatório de impacto quando o tratamento se basear em legítimo interesse (art. 10, § 3º).

**O guia da ANPD (02/02/2024).** O Guia Orientativo sobre Hipóteses Legais de Tratamento: Legítimo Interesse foi publicado em 02/02/2024, depois de consulta pública de 16/08 a 15/09/2023, e traz o teste em três fases: (1) finalidade (interesse legítimo, concreto e atual); (2) necessidade (dado mínimo, sem alternativa menos invasiva); (3) balanceamento e salvaguardas (expectativa do titular, impacto, medidas de mitigação). Se o teste for inconclusivo ou faltarem salvaguardas, outra base deve ser usada. Há divergência entre escritórios sobre o teste ser obrigatório; para a Save, **ele é obrigatório por regra da casa** (sem LIA, contato direto desligado).

**Dados de acesso público (art. 7º, §§ 3º, 4º e 7º).** O tratamento de dado cujo acesso é público considera a finalidade, a boa-fé e o interesse público que justificaram a disponibilização (§ 3º). O dado tornado manifestamente público pelo titular dispensa consentimento, resguardados os direitos (§ 4º). O tratamento posterior para nova finalidade exige propósito legítimo e específico e preservação dos direitos (§ 7º, incluído pela Lei 13.853/2019). **Leitura do sênior:** o QSA é público para dar segurança às relações com a empresa (quem a representa); contatar o administrador sobre um serviço para a empresa é compatível; montar perfil pessoal do sócio não é.

**Opt-out e direitos.** O titular pode se opor ao tratamento baseado em legítimo interesse se houver descumprimento da lei (art. 18, § 2º) e tem direito à informação sobre a fonte e o uso (art. 9º e art. 18). Regra da Save: qualquer "não me contate" é atendido sem discussão, registrado no mesmo dia e bloqueia a raiz do CNPJ e o nome na cadência.

**Telefone e WhatsApp.** O prefixo 0303 da Anatel para telemarketing ativo de oferta (ato de dez/2021, prazos de 2022) teve notícia de fim da obrigatoriedade [não confirmado o estado atual]. A plataforma Não Me Perturbe cobre telemarketing de telecom e bancos. O WhatsApp Business exige opt-in para mensagem iniciada pela empresa (política da plataforma, [mercado]). Por isso o WhatsApp da Jenifer só é usado com quem já respondeu ou foi apresentado pelo Master.

**Fiscalização e sanção.** A primeira sanção da ANPD (Telekall Infoservice, publicada no DOU de 06/07/2023) foi a uma microempresa que oferecia lista de contatos de WhatsApp de eleitores: multa por tratar dado sem base legal (art. 7º) e por não atender à fiscalização, advertência por não indicar encarregado (art. 41); R$ 7.200 por infração, limitada a 2% do faturamento (art. 52, II). É o caso mais próximo de "lista de contatos para abordagem".

## 3. Base normativa
| Norma | Artigo | O que decide | Situação (consulta 22/10/2026) |
|---|---|---|---|
| Lei 13.709/2018 (LGPD) | art. 5º, I | Dado de sócio e de representante é dado pessoal | Vigente |
| Lei 13.709/2018 | art. 6º | Finalidade, necessidade, transparência, segurança | Vigente |
| Lei 13.709/2018 | art. 7º, IX, e art. 10, I, §§ 1º a 3º | Legítimo interesse e seus requisitos | Vigente |
| Lei 13.709/2018 | art. 7º, §§ 3º, 4º e 7º | Dado de acesso público e uso posterior | Vigente (§ 7º pela Lei 13.853/2019) |
| Lei 13.709/2018 | art. 9º e art. 18, § 2º | Informação ao titular e oposição | Vigente |
| Lei 13.709/2018 | art. 37 e art. 38 | Registro das operações e relatório de impacto | Vigente |
| Lei 13.709/2018 | art. 41 | Encarregado | Vigente; Resolução CD/ANPD 18/2024 (16/07/2024) |
| Lei 13.709/2018 | art. 46 | Segurança (arquivo 600, fora do OneDrive) | Vigente |
| Lei 13.709/2018 | art. 52 | Sanções (até 2% do faturamento, limitada a R$ 50 mi por infração) | Vigente; dosimetria na Resolução CD/ANPD 4/2023 (24/02/2023) |
| Resolução CD/ANPD 1/2021 | — | Regulamento de fiscalização e processo sancionador | Vigente (28/10/2021) |
| Resolução CD/ANPD 2/2022 | art. 3º e art. 4º | Agente de pequeno porte não se beneficia em tratamento de alto risco ou larga escala | Vigente (27/01/2022) |
| Guia da ANPD de legítimo interesse | — | Teste em três fases | Publicado em 02/02/2024 |
| Lei 12.527/2011 e Decreto 8.777/2016 | — | Dados abertos (o CNPJ é público por política de transparência) | Vigente |

## 4. Regras da casa
- **Regra 2 da célula:** contatos pessoais desligados até validação do Jurídico/DPO; canal preferencial é a apresentação do Master; opt-out definitivo.
- **Luis, 20/10/2026:** uso aprovado dos sócios do QSA (nome, qualificação, entrada; sem CPF) e dos telefones e e-mail da empresa, para a prospecção D&S, com o arquivo em 600 fora do repositório e do OneDrive.
- **Luis, 21/10/2026:** celular pessoal de sócio não é buscado fora do cadastro público da empresa.
- **CLAUDE.md do repositório (21/10/2026):** dado de cliente fica no Mac; dados de sócios e contatos só em `prospects-contatos.json`.
- **D3 (28/09/2026, aprovada com ajuste):** pacote de governança (Claude Enterprise sem treino com dados; registro por caso).
- **D91 (22/10/2026):** a pasta de cada pessoa no OneDrive é a caixa oficial até a TI liberar Graph e GLPI: **nenhum** dado de sócio vai para o OneDrive.
- **D76 (22/10/2026):** cliente sem Master fora das listas (menos dado tratado).
- **Pendente:** LIA validada pelo Jurídico (lacuna apontada na auditoria de 22/10/2026, seção 2.8).

## 5. Método
1. **Inventário da lista.** Que dados pessoais a lista carrega (nome de sócio, telefone, e-mail)? De que fonte, com que data?
2. **Minimização.** Tire o que não é usado no toque (qualificação do sócio só se ajuda a escolher a persona; data de entrada só para o briefing).
3. **LIA por finalidade.** Fase 1: "oferecer a empresas no Lucro Real um diagnóstico de créditos tributários via Master" (concreta e atual). Fase 2: dado mínimo (nome e cargo do administrador, contato do cadastro da empresa); alternativa menos invasiva (apresentação do Master) é preferida. Fase 3: expectativa razoável do administrador de ser contatado sobre a empresa; impacto baixo; salvaguardas (transparência, opt-out, sem CPF, sem celular buscado, retenção, acesso restrito).
4. **Transparência no primeiro toque.** Dizer quem é, de onde veio o contato ("cadastro público da empresa" ou "indicação do [Master]") e oferecer a saída ("se não fizer sentido, é só avisar que não volto a escrever").
5. **Registro.** Linha no registro de operações (art. 37); origem de cada contato no controle de follow-up.
6. **Opt-out.** Mesmo dia: motivo "opt-out", bloqueio da raiz e do nome, sem nova lista com ele.
7. **Retenção.** Prospect sem resposta: dados pessoais apagados do arquivo de contatos 12 meses depois do último toque `[HIPÓTESE, validar com o Jurídico]`; descartado por opt-out: mantém só o bloqueio (CNPJ e nome), sem telefone.
8. **Acesso.** Só a Jenifer e o agente local; nada no OneDrive, no e-mail ou em planilha compartilhada com o Master (o Master recebe a ficha da empresa, não o contato do sócio, salvo apresentação já feita por ele).
9. **Pedido do titular.** Responder em até 15 dias com fonte, dados e finalidade (art. 19, II) e encaminhar ao encarregado.
10. **Revisão.** A cada nova fonte, novo canal (WhatsApp, LinkedIn) ou novo produto, a LIA é refeita.

**Checagem por lista (sim/não, antes de liberar):** contém CPF? · contém celular de fonte não cadastral? · arquivo fora do 600? · lista vai para o OneDrive ou para o Master com contato de sócio? · há opt-out anterior na lista? · LIA cobre a finalidade e o canal? Qualquer "sim" nas cinco primeiras ou "não" na última bloqueia.

## 6. Perguntas de diagnóstico
1. Qual a finalidade exata desta lista e deste canal?
2. Quais dados pessoais a lista contém, e todos são usados no toque?
3. De que fonte veio cada contato e com que data?
4. O telefone do cadastro do CNPJ parece celular pessoal do sócio?
5. A LIA aprovada cobre este canal (telefone, e-mail, WhatsApp, LinkedIn)?
6. O primeiro toque diz de onde veio o contato e oferece saída?
7. Há opt-out anterior para esta raiz de CNPJ ou nome?
8. Onde o arquivo vai ficar e quem tem acesso?
9. O Master vai receber algum dado pessoal? Ele tem base para isso?
10. Quando os dados pessoais desta lista serão apagados?
11. A empresa é agente de pequeno porte? O tratamento é em larga escala ou de alto risco?
12. Algum titular pediu informação sobre a fonte do contato? Respondemos em 15 dias?

## 7. Armadilhas e sinais de alerta
- **"É B2B, não tem LGPD."** Errado: o administrador é pessoa natural.
- **Comprar ou raspar lista** de contatos: o caso Telekall (06/07/2023) é exatamente isso.
- **Enriquecer o sócio** com outras bases (patrimônio, idade, celular).
- **Guardar contato no OneDrive** ou mandar em planilha ao Master.
- **WhatsApp frio** para número do cadastro.
- **Ignorar oposição** porque "foi só uma mensagem".
- **Escalar quando:** titular reclama ou pede dados; ANPD ou Procon contata; nova fonte de dado pessoal; incidente (lista vazou, arquivo fora do 600); pedido de usar dados para outro produto.

## 8. Casos de referência
### Caso 1 · Telekall, primeira sanção da ANPD (público, 06/07/2023)
Situação: microempresa oferecia lista de contatos de WhatsApp de eleitores. Leitura do sênior: tratamento sem base legal e sem encarregado. O que a ANPD fez: multas de R$ 7.200 por infração (arts. 7º e regulamento de fiscalização) e advertência (art. 41), com o limite de 2% do faturamento (art. 52, II). Lição: lista de contato pessoal sem base é o risco nº 1 da prospecção.

### Caso 2 · Prospecção D&S com QSA (interno, 20 e 21/10/2026)
Situação: lista de ligações com sócios e telefones do cadastro. Leitura: dado público usado para finalidade compatível, minimizado (sem CPF), em arquivo 600 local. O que foi feito: aprovação do Luis registrada; contato só do cadastro; LIA formal pendente com o Jurídico.

### Caso 3 · Bloqueio de CPF em quadro societário (público, 2024)
Situação: Receita e Serpro lançaram, via Redesim, o recurso para a pessoa impedir a inclusão indevida do CPF em quadros societários. Leitura: o QSA é dado sensível ao contexto e o titular tem instrumentos de controle. O que foi feito: reforça a regra de não usar o QSA para perfil pessoal (Serpro, notícia de 2024, consulta 22/10/2026).

### Caso 4 · Opt-out por e-mail (interno, regra desde 29/09/2026)
Situação: prospect responde "não tenho interesse, não me procure mais". Leitura: oposição clara. O que foi feito: motivo "opt-out", bloqueio da raiz e do nome, saída de todas as listas futuras e registro no controle.

## 9. Fronteiras e escalonamento
- **Não é dele:** parecer jurídico final, LIA assinada, resposta à ANPD (`depto-juridico`, encarregado); segurança técnica do arquivo (`depto-ti`); termo do indicador (`depto-juridico`, `depto-contratos`).
- **Exige humano:** Jurídico valida a LIA; Luis aprova novas fontes e canais; encarregado responde ao titular.

## 10. Atualização
- Última revisão: 22/10/2026.
- Fontes: LGPD (Planalto), ANPD (guia de 02/02/2024; Resoluções 1/2021, 2/2022, 4/2023, 18/2024), análises de Mattos Filho e outros escritórios sobre o guia (consulta 22/10/2026), notícias da sanção Telekall (06/07/2023).
- Radar semanal: novas resoluções e sanções da ANPD; estado do prefixo 0303 na Anatel; aprovação da LIA; pedidos de titulares; mudanças de política do WhatsApp Business.
