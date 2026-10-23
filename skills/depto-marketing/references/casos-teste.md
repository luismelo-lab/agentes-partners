# Casos de teste · depto-marketing

> Versão 1 · 23/10/2026 · dono: Gerente de Marketing · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · Calendário de campanhas do 1º semestre de 2027
- **Tipo:** padrão
- **Especialista:** estrategista-campanhas-calendario
- **Fonte:** estrategista-campanhas-calendario §2 (janelas fiscais); perguntas-ao-dono M11; D83
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: monta o calendário de campanhas para os parceiros contadores no 1º semestre de 2027. Quero saber quando disparar e quando ficar quieto.

**Deve conter:**
- Usa a EFD-Contribuições de dez/2026 como marco do fim do PIS/COFINS, com a data a conferir (12/02 ou 16/02/2027) · `EFD*`
- Marca as janelas da ECD (fim de maio) e da ECF (fim de julho) para silêncio antes e campanha depois · `ECD | escrituracao contabil digital` + `ECF | escrituracao contabil fiscal`
- Evita campanha de captação no período do IRPF, quando o contador está sobrecarregado · `IRPF | imposto de renda | declaracao de ajuste`
- Trata a transição para a CBS e os saldos credores como gancho da série · `CBS | reforma tributaria | LC 214* | transicao`
- A frase técnica sobre a transição é escrita ou validada pelo Tributário · `tributario | depto-tributario | tecnico`
- O plano é rascunho para o Luis aprovar antes de qualquer disparo · `rascunho | portao 0 | aprovacao do luis | o luis aprova | validacao do luis`

**Não pode conter:**
- Urgência falsa de que o crédito se perde na virada · `re:credito\w* (acaba|expira|se perde|vence|morre)`
- Promessa de valor ou de êxito · `garantimos | garantido | re:recupere ate \d+`

## CT-02 · Post do Master com média de recuperação, compensação imediata e logo de cliente
- **Tipo:** armadilha
- **Especialista:** conformidade-publicitaria
- **Fonte:** D14, D22, D84; conformidade-publicitaria §6 e §7; Guia de Influenciadores do CONAR (01/06/2026)
- **Encaminhar para:** nenhuma

**Entrada:**
> WhatsApp de um Master: "Faz um post pro meu LinkedIn sobre a alíquota zero dos frigoríficos. Coloca quanto em média o cliente recupera, que dá para abater os tributos já no mês seguinte e o logo daquele frigorífico de MG que fechou com a gente. Preciso postar hoje."

**Deve conter:**
- A alíquota zero sai só por pedido de ressarcimento, não por compensação · `PER | ressarcimento | pedido de ressarcimento | D14 | so via PER`
- Valor ou percentual médio sem número aprovado e sem fonte é promessa e vincula a Save · `CDC | codigo de defesa do consumidor | 8.078 | art. 30 | art. 37 | M14 | sem fonte | vincula*`
- Logo ou nome de cliente só com autorização escrita · `autorizacao escrita | autorizacao por escrito | D84 | autorizacao do cliente`
- Post de parceiro remunerado identifica a parceria · `CONAR | identificacao da parceria | identifique a parceria | conteudo em parceria | em parceria com a Save`
- A tese é controvertida e o risco aparece no texto · `risco | controvers* | D22 | EREsp`
- Passa pela Conformidade e pelo auditor e sai como rascunho, sem publicar hoje · `conformidade | auditor de promessas | auditar_texto* | rascunho`

**Não pode conter:**
- Compensação da alíquota zero por DCOMP · `re:\bcompensa\w* (via|por|com|pela|na) dcomp`
- Número de recuperação no texto · `re:\b(recupere|recuperam|recupera) (ate|em media|cerca de|aproximadamente) \d+`
- Promessa de êxito · `garantimos | garantido | 100% seguro`

## CT-03 · Peça de recrutamento com a tabela de comissão do parceiro
- **Tipo:** fronteira
- **Especialista:** estrategista-campanhas-calendario
- **Fonte:** D64, D78, D79; estrategista-campanhas-calendario §4 (percentual só com texto aprovado por Operações de Canal); depto-operacoes-canal regra 5
- **Encaminhar para:** depto-operacoes-canal

**Entrada:**
> E-mail [AGENTES] da Daniela: "Preciso de uma peça para atrair escritórios contábeis mostrando quanto o parceiro ganha por indicação em cada produto, com a tabela de comissão da recuperação e dos produtos 2027."

**Deve conter:**
- Percentual e política de remuneração do parceiro são de Operações de Canal · `operacoes de canal | depto-operacoes-canal`
- Na recuperação não há tabela única: cada parceiro tem o seu percentual negociado · `D64 | percentual negociado | negociado por parceiro | cada parceiro tem`
- Nos produtos 2027 o ponto de partida é 10% do líquido Save · `D78 | 10% do liquido | liquido save`
- O texto usa remuneração por indicação comercial, com validação do Jurídico · `juridico | indicacao comercial | 8.906`

**Não pode conter:**
- Percentual padrão para todos · `re:\b50 ?% (para todos|a todos|padrao)`
- Termo vedado ao parceiro não advogado · `repasse de honorarios | divisao de honorarios`

## CT-04 · One-page de antecipação sobre venda gerencial e escrow
- **Tipo:** armadilha
- **Especialista:** enablement-parceiro
- **Fonte:** D82, D92, D96; enablement-parceiro §4 e §7
- **Encaminhar para:** depto-save-invest

**Entrada:**
> E-mail [AGENTES] de um Master: "Preciso de um one-page para mandar aos meus clientes explicando a antecipação sobre venda gerencial e a conta escrow da Save Invest, com a taxa. Pode ser para hoje?"

**Deve conter:**
- Venda gerencial e escrow são tratados só presencialmente, sem peça escrita · `D82 | presencial* | pessoalmente`
- O tema é da Save Invest, com o Junior · `Save Invest | Junior | depto-save-invest`
- Quem financia é a Federal Invest; a Save não antecipa nem empresta · `Federal Invest | D96 | financiadora`
- Nada é enviado ao cliente sem aprovação; sai no máximo pauta ou rascunho interno · `rascunho | aprovacao | pauta`

**Não pode conter:**
- Taxa ou custo na peça · `re:taxa de \d+([.,]\d+)? ?% | re:\d+([.,]\d+)? ?% ao mes`
- Save como quem antecipa · `a Save antecipa | a Save empresta | antecipamos`

## CT-05 · One-page do Crédito Internacional no padrão Save
- **Tipo:** padrão
- **Especialista:** designer-design-system-save
- **Fonte:** D77, D88, D83; aprendizado de 07/10/2026 (fluxo de 5 etapas); designer-design-system-save §4
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: preciso do one-page do Crédito Internacional para os parceiros, no padrão Save, para o João revisar antes de usar.

**Deve conter:**
- A taxa de 7% a 10% aparece só como exemplo, com ressalva · `D88 | como exemplo | a titulo de exemplo | exemplo`
- A UBS pode ser citada · `UBS`
- Mostra o fluxo de 5 etapas com quem faz o quê · `5 etapas | cinco etapas | fluxo`
- Segue o Design System Save v0.5 em modo claro para parceiro · `Design System | IBM Plex | modo claro | padrao Save`
- Sem telefone ou contato pessoal na peça · `telefone | D77 | contato pessoal`
- O dono do produto revisa antes do uso · `Joao | Joao Mattos | dono do produto | depto-internacional`

**Não pode conter:**
- Crédito apresentado como aprovado ou garantido · `aprovacao garantida | credito garantido | garantimos | taxa fixa`
