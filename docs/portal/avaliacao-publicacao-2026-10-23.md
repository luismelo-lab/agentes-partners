# Central Partners · como publicar ao time (acessos e alternativas)

> Área Partners · 23/10/2026 · Avaliação do depto-ti (Identidade, Segurança e LGPD Técnica; Arquiteto de Integrações) com o depto-juridico (Perímetro Regulatório e LGPD). Rascunho para o Luis Fernando de Melo. **Nada foi compartilhado nem teve permissão alterada.** Quem compartilha é o Luis; os agentes só ajustam o portal e os dados.
>
> Pedido do Luis: *"Avalie a possibilidade de publicarmos [o portal Central Partners] com os devidos acessos de pastas compartilhadas nesse primeiro momento, ou outro modo."*

## Resposta curta
**Sim, dá para publicar nesta semana**, com o Artifact atual compartilhado **só com as 3 pessoas (Daniela, Jenifer e Geovana), nunca com "qualquer pessoa da Save"**, e com cada uma recebendo acesso **direto e só à pasta da Central dela** no OneDrive. Antes, os agentes fazem **4 ajustes de cerca de 1 dia** no portal (seção 6). Sem eles, o portal hoje deixa qualquer pessoa escolher o perfil "Luis" na lista e aprovar decisões do Conselho, e entrega o mesmo `dados.json` inteiro a quem abrir.

Caminho em fases:
| Fase | Quando | O que | Quem |
|---|---|---|---|
| **0 · Ajustar o portal** | Esta semana (1 dia de agente) | Identidade obrigatória, versão "time" dos dados, conferência do autor na rotina, decisões do Conselho fora do portal do time | Agentes (depto-ti); o Luis aprova a prévia |
| **1 · Ligar** | Esta semana, depois da Fase 0 (cerca de 30 min do Luis) | Compartilhar o Artifact com 3 pessoas específicas e a pasta da Central de cada uma; teste com a Daniela primeiro | Luis |
| **2 · Tirar do OneDrive pessoal** | 2 a 4 semanas, depende da TI | Site do SharePoint "Área Partners · Agentes" (item 2.3 do pedido à TI), pastas das Centrais migradas, Graph ligado | TI da Save + Luis |
| **3 · Portal próprio com SSO** | 4 a 8 semanas depois de a TI nomear o responsável | `central/` no Azure Static Web Apps com Entra ID; Artifact fica só leitura por 2 semanas e sai | TI da Save + agentes |

## 1. Como está hoje (o que conferimos no repositório)
- **Portal:** Artifact no claude.ai (`https://claude.ai/artifact/7fgGfrK7zVqzjcXCscJmwb`), dono o Luis, compartilhado só dentro da organização. Usa `db` (pedidos, ações das demandas, recuperador, decisões), `user` (quem vê) e, na versão nova (`portal/opcoes/combinada.html`), `sample` ("Fale com esta área").
- **A Save usa o Claude no plano Enterprise** (D3, `departamentos/ti/inventario-agentes.md`).
- **Dados publicados** (`infra/portal_dados.py`): `dados.json` traz, para quem abrir, tudo de uma vez: demandas das três (WhatsApp, com Master, negócio e link), scorecard dos 10 Masters (abertos em R$, ganhos em 90 dias), lote do Recuperador (negócio, parceiro, valor esperado), **47 decisões do Conselho**, arquivos do dia do Luis e links das pastas do Luis. Não achamos CPF, telefone ou tema de pessoas (salário, bônus, desempenho) nas decisões. `diretorio.json` não tem cliente, mas aponta **41 links para `04 · Gestão, Metas e Estratégia` e 24 para `01 · Comercial e Parceiros`**, pastas do Luis.
- **Identidade no portal:** `Fonte.quemSou()` compara o nome da conta Claude com "luis/daniela/jenifer/geovana" e usa `isOwner()` para o Luis. **Se o nome não bater, a lista "Quem é você?" fica livre**, e quem escolher "Luis" vê os botões Aprovar/Rejeitar das decisões do Conselho (`combinada.html`, linhas 653–654). As gravações levam `solicitante_id`/`por_id`, mas nenhuma rotina confere esse id hoje.
- **Pastas:** `Área Partners · Agentes` (OneDrive do Luis) tem as 3 pastas das Centrais, mais arquivos soltos na raiz (`Demandas.xlsx`, `Controle-Pendencias-Masters.xlsx`, `Ganhos-a-completar`, `Transacao-Pequeno-Valor-candidatos`, `Semana 0`, `Briefings`). `01 · …/Relatórios das áreas` tem conferência de repasses, conflito de canal, contratos e Dados-BI. `04 · Gestão…` tem Conselho, Resultado, Planejamento 2027, pedidos à TI e manuais.

## 2. O que dizem os fornecedores (fonte e data da consulta: 23/10/2026)
- **Anthropic · Publicar e compartilhar Artifacts** (support.claude.com/en/articles/9547008): no Team e no Enterprise o Artifact fica dentro da organização; dá para escolher **"Anyone at [organização]"** ou **pessoas específicas** com nível *Can view*, *Commenter* ou *Can edit* (no Enterprise também grupos). **Todos precisam de conta Claude** e entram com o e-mail convidado. Convite a e-mail de fora vem **desligado por padrão no Enterprise**; quando ligado, o externo não usa as partes do Artifact que usam o Claude ou conectores. A página avisa que alguns Artifacts **guardam informação que todos que o abrem podem ver** (é o caso do `db`). Sobre consumo do `sample` no Enterprise, a página **não diz**; o desenho do portal assume que a chamada usa a conta de quem pergunta. [Conferir com o administrador do Claude da Save.]
- **Microsoft · Allow or prevent custom script** (learn.microsoft.com/sharepoint/allow-or-prevent-custom-script, atualizada em 03/02/2026): script personalizado vem bloqueado no OneDrive, nos sites modernos e nos criados pelo usuário; **"não é possível permitir script no OneDrive de um usuário"**, e a liberação num site **volta a "bloqueado" em até 24 h**. Com script bloqueado, `.aspx` não abre na biblioteca.
- **Microsoft · Browser File Handling** (learn.microsoft.com/sharepointmigration/migration-assessment-scan-browser-file-handling): no SharePoint Online o modo **Strict** é imposto e não pode ser mudado; `.htm`/`.html` em biblioteca **são baixados em vez de abertos**, para impedir a execução de conteúdo web enviado por usuários. **Conclusão: o portal (HTML + JavaScript) não roda no OneDrive nem no SharePoint.**
- **Microsoft · Compartilhar arquivos e pastas no OneDrive** (support.microsoft.com, artigo 4f605827): o link **"Pessoas específicas"** só funciona para quem foi indicado; se for repassado, só abre para quem já tinha acesso. Data de expiração e bloqueio de download dependem da política do locatário.
- **Microsoft · Azure Static Web Apps, planos e cotas** (learn.microsoft.com/azure/static-web-apps/plans e /quotas): provedor de autenticação personalizado (Entra ID com o app da Save) e **papéis atribuídos por função** só no plano **Standard**; 100 GB/mês de tráfego incluídos e US$ 0,20/GB acima disso. Mensalidade do Standard: ver a página de preços [não conferida nesta avaliação; a TI confirma, como já previsto em `docs/sso-entra/diagnostico-e-plano.md`].

## 3. As quatro opções

### Opção 1 · Artifact no claude.ai + pastas do OneDrive compartilhadas (recomendada para agora)
**Pré-requisitos**
1. Daniela, Jenifer e Geovana **com assento no Claude Enterprise da Save**, entrando com o e-mail @savecompany.com.br. Se alguma não tiver, o Luis pede o assento ao administrador do Claude da Save (é o mesmo plano da D3; não é conta pessoal).
2. Fase 0 feita (seção 6) e prévia aprovada pelo Luis.
3. Nome de exibição da conta Claude de cada uma contendo o primeiro nome (é o que o portal usa para reconhecer a pessoa). Se não contiver, a Fase 0 passa a reconhecer pelo id da conta.

**Como compartilhar**
- **Artifact:** pessoas específicas, nível **Can view** (as três). **Não** usar "Anyone at Save": o `dados.json` e o `db` ficariam visíveis a toda a empresa com conta Claude. **Não** dar *Can edit*: permite mexer na página.
- **Teste obrigatório com a Daniela antes das outras:** com *Can view* ela abre, é reconhecida, faz 1 pedido e marca 1 ação. Se o *Can view* não permitir gravar no `db`, paramos e reavaliamos; não subimos para *Can edit* sem nova análise.
- **Pastas:** acesso direto (Gerenciar acesso → Conceder acesso), uma pasta por pessoa (matriz na seção 4).

**Custo**
- Assentos Enterprise já contratados ou a contratar (a confirmar com o administrador). O `sample` ("Fale com esta área") consome o uso de quem pergunta, na regra do plano da Save. Sem custo de hospedagem.

**Riscos e como tratamos**
| Risco | Peso | Tratamento |
|---|---|---|
| Qualquer pessoa escolhe o perfil "Luis" e aprova decisões | **Alto** | Fase 0, ajuste A1: sem identidade = só leitura; decisões só com `isOwner()` |
| `dados.json` igual para todos: a Jenifer vê demandas da Daniela, e todos veem as decisões do Conselho e os arquivos do Luis | Médio | Fase 0, ajuste A2: versão "time" sem decisões do Conselho, sem arquivos e pastas do Luis. As demandas cruzadas entre as três ficam (mesma equipe, mesma finalidade), registradas como risco aceito pelo Luis |
| Gravação no `db` por alguém de fora das quatro (o `db` aceita qualquer visualizador) | Médio | Fase 0, ajuste A3: a rotina só processa registros cujo `solicitante_id`/`por_id` esteja na lista das quatro contas |
| Link do portal para pasta do Luis que a pessoa não pode abrir | Baixo (falha fechada) | Ajuste A2: no lugar do link, "pasta do Luis: peça pela Central" |
| Tudo no OneDrive pessoal do Luis: se a conta dele mudar, as Centrais param | Médio | Fase 2: site do SharePoint da área |
| Dado de cliente (nome de empresa, negócio, contato de WhatsApp) em servidor da Anthropic | Médio | Já ocorre hoje; coberto pela D3 (Enterprise, sem treino). Jurídico confere o acordo de tratamento e a transferência internacional (seção 5) |
| Resposta do "Fale com esta área" usada como parecer | Médio | O texto da tela já diz "pré-análise"; manter o selo e a regra "nada sai sem revisão"; jurídico e tributário seguem para o advogado ou técnico |

**Quem administra:** o Luis (dono do Artifact e das pastas). O depto-ti mantém a lista das quatro contas (A3) e faz a revisão de acessos todo mês, na consolidação de sexta, com um relatório de quem tem acesso.

### Opção 2 · Só a pasta compartilhada como porta de entrada (Excel/Word por pessoa, sem web)
Já é o contorno da D91 e continua valendo como plano B.
- **Fica:** plano do dia, folha do lote do Recuperador, Revisor e briefings na pasta de cada uma; decisões marcadas nas colunas do Excel e lidas pelas rotinas.
- **Perde:** pedido à Central com formulário e status ao vivo (o pedido volta a ser um arquivo ou o e-mail `[AGENTES]`, que está parado sem o Graph; depende da decisão CA3 do plano de lançamento), o "Onde está" das 25 áreas com busca, o "Fale com esta área", a mesa com o que é de cada uma "agora" e a contagem de pendências. Também perde a medição de adoção do painel (pedidos P-xxxx e decisões no portal) que alimenta o placar do D5.
- **Risco próprio:** conflito de edição em Excel aberto por duas pessoas e por uma rotina ao mesmo tempo. Já aconteceu com planilha grande não lida (C7).
- **Uso recomendado:** se o teste da Daniela na Fase 1 falhar ou se alguma das três não tiver assento no Claude.

### Opção 3 · Microsoft (SharePoint, Teams, Lists, Power Apps)
- **O HTML do portal não roda lá** (seção 2: Strict e script bloqueado; no OneDrive não há como liberar). Seria preciso **refazer** o portal.
- **Sem a TI (o Luis sozinho):** se o locatário permitir criar equipes, o Luis cria uma equipe privada no Teams "Área Partners · Agentes" com as 3 pessoas. Isso dá um site do SharePoint com biblioteca e permite **Microsoft Lists** (ex.: lista "Pedidos" com formulário). Porém **as rotinas não leem nem gravam em Lists sem o Graph** (pendente); a biblioteca pode ser sincronizada no Mac e as rotinas gravariam arquivos nela, como hoje. Ganho real: tira as Centrais do OneDrive pessoal. Perda: o portal vira listas e arquivos, sem a mesa, a busca e o "Fale com esta área". **Viável, mas é a Opção 2 num lugar melhor.** Atenção: equipe criada pelo Luis fica fora das regras de retenção que a TI pediria para o site 2.3; conversar com a TI antes.
- **Com a TI:** site 2.3 com permissões e retenção, Graph com `Sites.Selected`, e um app no Power Apps sobre Lists (licença padrão do Microsoft 365 cobre conectores padrão; confirmar com a TI). Prazo parecido com o da Opção 4, e o resultado é inferior ao portal que já existe. **Não recomendamos refazer em Power Apps**; usar o SharePoint como **lugar dos arquivos** (Fase 2) e o portal web como **tela**.

### Opção 4 · Azure Static Web Apps com SSO (`central/`)
- **O que já existe:** código de `central/` (154 testes) para a consulta dos parceiros; plano de SSO em `docs/sso-entra/diagnostico-e-plano.md`; a "camada de dados" do portal (`Fonte` em `combinada.html`) foi escrita para trocar `claude.use("db")` por chamadas à API sem mudar as telas. D89 (22/10/2026) aprovou SWA Standard e Table Storage.
- **O que falta (tudo com a TI):** responsável e data; registro do aplicativo da API e papéis (`Central.Acesso`, papéis do time e `Agentes.Processar`), com atribuição obrigatória; SWA Standard e Functions no locatário; domínio e certificado; redirect no `SAVE-SSO-MASTERS`; Graph (`Sites.Selected`) para os arquivos; definição de região dos dados (pergunta 5 do pedido da esteira); para parceiros externos, B2B ou External ID (item 3.3).
- **Prazo realista:** 4 a 8 semanas **a partir do dia em que a TI nomear o responsável**: 1 a 2 semanas para a etapa 0 (Entra, SWA), 2 a 3 para login, API e migração do `db` para Table Storage, 1 de homologação e 2 de uso em paralelo antes do corte. Hoje a TI ainda não respondeu aos pedidos de 30/09, 13/10 e 23/10; contar a partir da resposta, não de hoje.
- **Ganho:** login Microsoft da Save, papel por pessoa, dado filtrado no servidor (cada uma recebe só o que é dela), revogação central no Entra, registro de acesso. É o destino; não é o "primeiro momento".

## 4. Matriz de acesso da Fase 1 (pessoa × pasta × permissão)
Todas no OneDrive do Luis, por **acesso direto a pessoas específicas** (Gerenciar acesso → Conceder acesso), sem link "Qualquer pessoa" e sem link "Pessoas na Save". Revisão marcada para **30/01/2027** (ou antes, quando a Fase 2 mover as pastas).

| Pasta ou arquivo | Luis | Daniela | Jenifer | Geovana | Por quê |
|---|---|---|---|---|---|
| `Área Partners · Agentes` (pasta-mãe) | Dono | — | — | — | **Não compartilhar a mãe**: a raiz tem `Demandas.xlsx`, `Ganhos-a-completar`, `Transacao-Pequeno-Valor-candidatos` e `Semana 0` de todos |
| `Área Partners · Agentes/Central Masters · Daniela` | Dono | **Editar** | — | — | Ela marca decisões nas planilhas e salva pedidos |
| `Área Partners · Agentes/Central BDR · Jenifer` | Dono | — | **Editar** | — | Idem |
| `Área Partners · Agentes/Central Técnica · Geovana` | Dono | — | — | **Editar** | Idem (lote do Recuperador, Revisor) |
| `Área Partners · Agentes/00 · Comece aqui.docx` e `Central de Agentes · como pedir.docx` | Dono | Exibir | Exibir | Exibir | Orientação comum. Alternativa mais simples: os agentes copiam os dois para dentro de cada Central |
| `Área Partners · Agentes/Briefings` | Dono | Exibir (se for dos Masters) | — | — | Conferir o conteúdo antes; se for só da Daniela, mover para a Central dela |
| `Controle-Pendencias-Masters.xlsx`, `Ganhos-a-completar-*.xlsx` (raiz) | Dono | via cópia na Central dela | — | — | Os agentes passam a gravar na Central da Daniela; nada de compartilhar arquivo solto da raiz |
| `01 · Comercial e Parceiros/Relatórios das áreas` | Dono | — | — | — | Tem conferência de repasses e conflito de canal de todos os Masters. O que cada uma precisar vai como cópia na Central dela |
| `04 · Gestão, Metas e Estratégia` (inteira) | Dono | — | — | — | Conselho, resultado, planejamento, pedidos à TI: só do Luis |
| Artifact Central Partners (versão "time") | Dono | Can view | Can view | Can view | Pessoas específicas; nunca "Anyone at Save" |

Regra: **o agente leva o arquivo até a pasta da pessoa**; o Luis não abre as pastas dele.

## 5. Leitura do Jurídico (perímetro e LGPD)
- **Perímetro regulatório:** uso interno, só funcionárias da Save; nenhum parceiro, cliente ou investidor acessa. Não há oferta, distribuição nem captação (CVM/BCB não entram). O "Fale com esta área" do Jurídico e do Tributário é **pré-análise para o advogado ou o técnico**, nunca parecer entregue ao cliente (Lei 8.906/1994, art. 1º, II). **Parceiro externo não entra neste Artifact**; o caminho deles é a Opção 4 (`central/`, item 3.3).
- **LGPD (Lei 13.709/2018, conferida em 22/10/2026 pelo depto-ti, planalto.gov.br):**
  - Nome de empresa (pessoa jurídica) não é dado pessoal; **nome de contato, sócio ou interlocutor de WhatsApp é**. Os itens de demanda podem trazer esses nomes.
  - Compartilhar dentro da Save, com a equipe que atende o mesmo cliente, para a mesma finalidade, cabe nas bases já usadas (execução de contrato e legítimo interesse, art. 7º, V e IX). Exige **necessidade** (art. 6º, III): por isso a versão "time" tira o que só o Luis usa, e a Fase 3 filtra por pessoa no servidor.
  - **Segurança** (art. 46): acesso só nominal, sem link aberto, revisão periódica e possibilidade de revogar na hora.
  - **Registro** (art. 37): anotar no registro de operações: "portal Central Partners, Artifact Claude Enterprise, 4 usuárias nominais, dados X, revisão em 30/01/2027".
  - **Transferência internacional** (art. 33): o Artifact já guarda esses dados na infraestrutura da Anthropic. A D3 cobre o uso do Enterprise; o Jurídico precisa ver se o contrato Enterprise tem o acordo de tratamento de dados e as cláusulas-padrão da ANPD (Res. CD/ANPD 19/2024, em vigor desde 23/08/2025 pelo radar interno) **[pendente: pedir ao administrador do Claude da Save o DPA assinado]**. Isso não bloqueia a Fase 1 (o dado já está lá hoje), mas fecha a pendência.
  - OneDrive pessoal do gestor como repositório de dado de cliente compartilhado com a equipe é aceitável por pouco tempo. A Fase 2 (site da área, com retenção de 12 meses) é a forma correta.

## 6. O que muda no portal antes de compartilhar (Fase 0, depto-ti, cerca de 1 dia)
| # | Ajuste | Onde | Critério de pronto |
|---|---|---|---|
| A1 | **Identidade obrigatória.** Fora da prévia, a lista "Quem é você?" some. Quem não for reconhecido (nome ou id) entra **só leitura**. Botões de decisão do Conselho só com `user.isOwner()`, não com `S.eu === "luis"` | `combinada.html` (`Fonte.quemSou`, `iniciar`, telas de decisão) | Uma conta de teste sem nome reconhecido não grava nada e não vê botões de decisão |
| A2 | **Versão "time" dos dados.** `portal_dados.py` ganha `PORTAL_PERFIL=time`: sem `conselho`, sem `arquivos_dia.luis` e `pastas_web.luis`, e com links de `01 ·` e `04 ·` trocados por "pasta do Luis: peça pela Central". As decisões do Conselho do Luis continuam na Folha Única (`Decisoes-Pendentes-Folha-Unica`) e no Conselho; se ele quiser tela, um **segundo Artifact só dele** | `infra/portal_dados.py`, `diretorio.json` | `grep` no `dados.json` publicado sem `04%20%C2%B7%20Gest` e sem a chave `conselho` |
| A3 | **Conferir o autor.** A rotina da Central e as que leem `db` só processam registros cujo `solicitante_id`/`por_id` esteja na lista das quatro contas (`infra/portal-contas.json`, só ids, sem e-mail). O que vier de fora vira alerta ao Luis | `skills/central-agentes/scripts/`, leitura do `db` | Registro com id desconhecido não vira pedido |
| A4 | **Lista de acessos.** O relatório mensal "quem tem acesso" (Artifact e pastas) entra na consolidação de sexta, preenchido pelo Luis com o que ele vê em Compartilhar / Gerenciar acesso | `rotinas/` (consolidação) | Primeiro relatório em novembro |

Publicação: o Luis aprova a prévia; os agentes republicam no **mesmo URL** (mantém o `db`, os pedidos e as rotinas).

## 7. Passo a passo do Luis (Fase 1, cerca de 30 minutos)
1. **Confirmar assentos:** perguntar ao administrador do Claude da Save se Daniela, Jenifer e Geovana têm assento no Enterprise. Se não, pedir.
2. **Aprovar a prévia da Fase 0** (os agentes mandam o link e o print de cada perfil).
3. **Pastas (OneDrive no navegador):** em `Área Partners · Agentes`, clicar com o botão direito em `Central Masters · Daniela` → *Gerenciar acesso* → *Conceder acesso* → e-mail da Daniela → **Pode editar** → desmarcar "Notificar" se quiser avisar pessoalmente → *Conceder*. Repetir para Jenifer e Geovana, cada uma **só na sua pasta**. Não mexer na pasta-mãe.
4. **Artifact (Daniela primeiro):** abrir o portal → *Share* → adicionar o e-mail da Daniela → **Can view**. Conferir que o acesso geral **não** está em "Anyone at Save". Mandar o link a ela.
5. **Teste de 10 minutos com a Daniela:** ela abre, vê o próprio nome no canto, abre a pasta dela pelo portal, faz 1 pedido e marca 1 ação. Se o link da pasta não abrir, os agentes trocam pelo link "Copiar link" da pasta compartilhada (o formato `/my?id=` pode não abrir para outra conta: item a testar).
6. **Se o teste passar:** repetir o passo 4 com Jenifer e Geovana (pode ser no D0 do lançamento).
7. **Anotar:** data e quem recebeu, no registro de operações LGPD (o Jurídico manda o modelo de uma linha).

## 8. Como reverter (cada passo volta sozinho, sem apagar nada)
| O que | Como desfazer | Efeito |
|---|---|---|
| Acesso ao Artifact | *Share* → remover a pessoa (ou trocar para só o Luis) | Na hora; o `db` e os pedidos ficam |
| Acesso à pasta | *Gerenciar acesso* → pessoa → *Remover acesso* | Na hora; os arquivos ficam |
| Mudanças da Fase 0 | Republicar a versão anterior do Artifact no mesmo URL; `git revert` do commit em `portal_dados.py` | O portal volta ao estado de hoje |
| Registro gravado por alguém indevido | A rotina já ignora (A3); o Luis apaga a linha pelo painel, se quiser | Nenhum processamento |
| Opção inteira | Voltar à Opção 2 (só pastas, D91) | Plano B já em uso |

## 9. O que você pediu · o que também precisa · o que falta e quem fornece
**O que você pediu:** dá para publicar agora com acesso às pastas. Caminho: Artifact com 3 pessoas específicas (Can view) + cada uma na pasta da Central dela (Editar), depois de 1 dia de ajustes no portal. As alternativas (só pastas, Microsoft, Azure) estão avaliadas acima; a Microsoft não roda o portal e o Azure é o destino, mas depende da TI.

**O que você também precisa:**
- Hoje o portal deixa escolher o perfil "Luis" e aprovar decisões: **não compartilhar antes do ajuste A1**.
- Não compartilhar a pasta-mãe `Área Partners · Agentes` nem `01 ·`/`04 ·`: os agentes levam cópias até a Central de cada uma.
- Pedir à TI a Fase 2 junto com o pedido do Graph (o site 2.3 já está no pedido da esteira), para tirar as Centrais do seu OneDrive pessoal.

**O que falta e quem fornece:**
| Falta | Quem |
|---|---|
| Confirmação dos assentos Enterprise das 3 e de como o `sample` é cobrado | Administrador do Claude da Save |
| Acordo de tratamento de dados (DPA) e cláusulas-padrão da ANPD no contrato Enterprise | Administrador do Claude da Save → depto-juridico |
| Aprovação da prévia da Fase 0 e decisão sobre ter ou não um Artifact só seu para o Conselho | Luis |
| Responsável e data para Graph, site 2.3, SWA e Entra | TI da Save (pedidos de 23/10/2026) |
| Teste do *Can view* gravando no `db` e do link de pasta para outra conta | Daniela, com o Luis (passo 5) |

---
revisao: depto-ti (Identidade, Segurança e LGPD Técnica; Arquiteto de Integrações) + depto-juridico (Perímetro Regulatório). Leitura do repositório em 23/10/2026: `infra/portal_dados.py`, `portal/opcoes/combinada.html`, `portal/dados.json`, `portal/diretorio.json`, `lib/caminhos.py`, `docs/lancamento-2026/plano-lancamento.md`, `docs/pedidos-ti-2026-10-23.md`, `departamentos/ti/pedido-esteira-parceiros-nuvem.md`, `docs/sso-entra/diagnostico-e-plano.md`. Fontes externas consultadas em 23/10/2026: support.claude.com/en/articles/9547008; learn.microsoft.com/sharepoint/allow-or-prevent-custom-script (03/02/2026); learn.microsoft.com/sharepointmigration/migration-assessment-scan-browser-file-handling; support.microsoft.com (compartilhar no OneDrive, 4f605827); learn.microsoft.com/azure/static-web-apps/plans e /quotas. Nenhuma permissão foi alterada e nada foi compartilhado.
