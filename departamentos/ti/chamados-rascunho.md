# Chamados — RASCUNHO para o Luis revisar e enviar

**29/09/2026 · Departamento de TI virtual · NADA FOI ENVIADO.** O Luis revisa, ajusta e envia pelo canal oficial (GLPI, e-mail ou reunião).
Regras dos textos: nenhum link de arquivo de cliente, nenhuma credencial. Se o TI pedir a lista dos negócios afetados, o Luis manda **os IDs dos negócios** (não os links) por canal interno. A lista sai de um script local, a pedido.

---

## Chamado 1 — TI · Segurança: pareceres de clientes acessíveis por link público do Bitrix24
**Categoria sugerida:** TI-SEGURANCA · **Urgência:** Alta · **Para:** TI da Save (cópia: Jurídico/encarregado de dados)

**Assunto:** Links públicos do Bitrix24 com pareceres de clientes nos negócios do HubSpot

> Olá, time de TI.
>
> Ao organizar a leitura dos pareceres da Área Partners, identificamos que os campos de arquivo dos negócios no HubSpot (**Parecer Complementar RT**, **Anexo do Diagnóstico** e **Parecer Complementar Jurídico**) guardam, para os negócios migrados do Bitrix24, **links diretos para arquivos no CDN do Bitrix24** (domínio `cdn.bitrix24.com.br`, portal `b24050713`).
>
> **O que vimos (contagem de 29/09/2026, base de 4.892 negócios):**
> - **4.748 links** em **1.953 negócios** (908 ganhos, 1.045 perdidos). Tipos: Word, PDF, Excel, imagens, texto.
> - Os links **não têm token nem data de expiração** e abrem **sem login**: qualquer pessoa com a URL baixa o arquivo. A leitura automática da área baixou 1.810 arquivos dessa forma, sem credencial.
> - Os arquivos são pareceres e diagnósticos tributários, com dados fiscais e financeiros dos clientes e, em parte, nomes de sócios e representantes (dados pessoais).
> - Esses links circulam dentro do HubSpot e podem ter sido encaminhados a parceiros ao longo do tempo.
>
> **Risco:** exposição de informação confidencial de clientes (sigilo comercial e profissional), incidente de LGPD se um link vazar, e dano de reputação.
>
> **Pedimos ao TI que avalie:**
> 1. Se o portal Bitrix24 ainda está ativo/contratado e quem é o administrador.
> 2. Desativar o acesso público (ou colocar expiração) nesses arquivos, **depois** de garantir uma cópia.
> 3. Migrar os arquivos para um repositório com controle de acesso (ex.: arquivos privados do HubSpot ou SharePoint/OneDrive da Save), mantendo o vínculo com o negócio (ID do negócio no nome ou no campo).
> 4. Se o Bitrix24 oferece registro de acesso a esses links, para saber se houve acesso externo.
> 5. Orientar o Jurídico sobre a necessidade de avaliar o incidente (art. 48 da LGPD), se houver indício de acesso indevido.
>
> **Impacto na Área Partners:** a leitura automática dos pareceres (Recuperador da Geovana) usa hoje esses links. Concordamos que ela pare de funcionar quando o acesso público for fechado; pedimos só que a solução nova permita leitura autenticada (ver chamado 2).
>
> Fico à disposição. — Luis Fernando de Melo, Área Partners

---

## Chamado 2 — CRM/HubSpot (cópia TI) · Escopo de leitura de arquivos no app privado do HubSpot
**Categoria sugerida:** TI-ACESSO · **Urgência:** Média · **Para:** administrador do HubSpot / time de CRM (cópia: TI)

**Assunto:** Incluir escopo de LEITURA de arquivos no app privado da Área Partners (HubSpot 47865021)

> Olá, time de CRM.
>
> A Área Partners usa um **app privado do HubSpot somente leitura** para gerar o relatório semanal e a fila de reanálises. Os pareceres anexados diretamente no HubSpot (campos **Parecer Complementar RT**, **Anexo do Diagnóstico** e **Parecer Complementar Jurídico**) não podem ser lidos porque o app não tem escopo de arquivos.
>
> **Volume afetado:** **625 arquivos** nos negócios ganhos (leitura de 29/09/2026) e **2.241 arquivos em 1.090 negócios** na base toda.
>
> **Pedido (menor privilégio):**
> 1. Incluir o escopo **`files.ui_hidden.read`** (leitura de arquivos ocultos, que é como o HubSpot guarda anexos de registros do CRM). Segundo a documentação da API de arquivos do HubSpot, as rotas de arquivo aceitam `files` **ou** `files.ui_hidden.read`, e arquivos privados e ocultos exigem o `files.ui_hidden.read`.
> 2. Só se o teste com o item 1 não bastar: incluir **`files`**. Atenção: `files` também permite enviar e alterar arquivos; por isso sugerimos começar pelo item 1.
> 3. Não incluir nenhum escopo de escrita no CRM.
>
> **Como usamos:** o arquivo é lido por um link assinado temporário, convertido em texto no próprio computador (nada sai da máquina) e o original fica no card. Nada é gravado no HubSpot.
>
> **Credencial:** se o token mudar, peço que me avisem para eu atualizar no meu computador. **Não enviem o token por e-mail ou chat**: eu mesmo copio da tela do app privado.
>
> Obrigado! — Luis Fernando de Melo, Área Partners

---

## Chamado 3 — TI · Confirmar se o documento do cockpit S&OE (Firebase) está com leitura pública
**Categoria sugerida:** TI-SEGURANCA · **Urgência:** Média · **Para:** TI da Save (responsável pelo projeto Firebase `save-partner-soe`)

> Olá, time de TI.
>
> O relatório semanal da Área Partners lê, como fonte secundária, o documento `soe/main` do Firestore do projeto `save-partner-soe` (cockpit S&OE). **O script faz essa leitura sem nenhuma credencial**, o que indica que as regras do Firestore permitem leitura pública. Esse documento guarda números internos da área (pipeline, margens, repasses).
>
> **Pedimos:** (1) confirmar as regras de segurança do Firestore desse projeto; (2) se a leitura for pública, restringir a usuários autenticados da Save; (3) avisar antes, para ajustarmos o script (ele passa a usar só o HubSpot, que já é a fonte principal).
>
> — Luis Fernando de Melo, Área Partners

*(Nota interna: não testamos o acesso de fora da Save; a conclusão vem do código do script. Verificar antes de enviar.)*

---

## Chamado 4 — CRM · D18: obrigatoriedade dos campos de pagamento e do % de honorário
**Categoria sugerida:** CRM-CADASTRO (ou demanda de projeto ao time de CRM) · **Urgência:** Média · **Para:** time de CRM da Save
**Origem:** decisão D18 do Conselho, aprovada pelo Luis em 29/09/2026 com o ajuste "a obrigatoriedade dos campos será feita pelo time de CRM da Save".

**Assunto:** Tornar obrigatórios o % de honorário e os campos de pagamento nos negócios ganhos

> Olá, time de CRM.
>
> Para a Área Partners medir o resultado **realizado** (e não só o contratado), precisamos que dois grupos de campos passem a ser obrigatórios no HubSpot.
>
> **O que vimos (base de 28/09/2026):**
> - O **% de honorário** (`honorarios_contratuais`) está preenchido em só **42% dos negócios ganhos**; há **61 negócios com honorário acima de 50%** (provável erro de digitação ou de unidade).
> - Os **campos de pagamento** estão **100% vazios**. Não há hoje no HubSpot um campo de valor recebido.
>
> **Pedido:**
> 1. **% de honorário** e **% do parceiro** (`honorarios_parceiro`) obrigatórios na passagem para a etapa de ganho (regra de etapa do pipeline), com validação de 0 a 50% (acima disso, só com justificativa).
> 2. **Campos de pagamento** (o time de CRM define os nomes exatos; sugestão: status do pagamento, data do recebimento, valor recebido, forma/condição) obrigatórios quando o pagamento acontecer, com a fonte oficial vindo do Financeiro/ERP sempre que possível.
> 3. Saneamento dos ganhos de jul–set/2026 sem % de honorário (a Área Partners manda a lista dos negócios).
> 4. Prazo sugerido pelo Conselho: **31/10/2026**, meta de 100% dos ganhos novos preenchidos.
>
> **Pergunta:** existe uma fonte no Financeiro/ERP com o honorário já recebido por negócio? Se existir, preferimos integrar a digitar.
>
> Obrigado! — Luis Fernando de Melo, Área Partners

---

## Checklist antes de enviar (Luis)
- [ ] Confirmar o nome do responsável do TI e do time de CRM
- [ ] Chamado 1: decidir se copia o Jurídico já no primeiro envio (recomendado)
- [ ] Chamado 3: pedir ao TI para confirmar antes de tratar como incidente
- [ ] Chamado 4: conferir se os números (42%, 61, 100% vazios) ainda valem no relatório mais recente
- [ ] Nenhum link de arquivo e nenhuma credencial colados em nenhum texto

---
## Complemento (30/09): segunda checagem dos pareceres via Bitrix
- Os campos de parecer do HubSpot têm **ou** link do Bitrix (cards antigos, até ~fev/2026) **ou** arquivo do próprio HubSpot (cards novos). Não há sobreposição: dos 2.241 arquivos do HubSpot sem leitura, **nenhum** tem cópia em link do Bitrix no mesmo campo (só 2 negócios têm outro documento lido).
- Os links do Bitrix são endereços aleatórios no servidor de arquivos, sem relação com o `id_bitrix`. Não dá para montá-los a partir do ID.
- **486 dos 1.090 negócios** sem leitura têm `id_bitrix`, ou seja, também existem no Bitrix.
- **Alternativa ao escopo do HubSpot** (pedir ao TI, só leitura): um webhook de entrada do Bitrix24 com permissão de leitura de CRM e Drive, para ler os arquivos desses 486 negócios pelo ID. Isso não cobre os outros 604 negócios; para eles só o escopo `files.ui_hidden.read` do HubSpot resolve.
