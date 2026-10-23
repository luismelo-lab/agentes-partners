# Casos de teste · revisor-diagnostico

> Versão 1 · 23/10/2026 · dono: Geovana (Revisor de Diagnóstico) · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · Indústria que vende a consumidor final em outros estados
- **Tipo:** padrão
- **Especialista:** lacunas-por-perfil
- **Fonte:** SKILL.md (teses da revisão manual desde 22/10/2026); especialista lacunas-por-perfil §2 (EX_DIFAL) e evidencia-sped §2 (E300/E310); perguntas-ao-dono itens 2 e 3
- **Encaminhar para:** nenhuma

**Entrada:**
> Mensagem da Geovana: "Revisa o diagnóstico de uma indústria de alimentos do PR, Lucro Real, que vende pela internet para consumidor final em outros estados. O parecer apurou exclusão do ICMS e insumos. O que o técnico não pegou?"

**Deve conter:**
- Lacuna de DIFAL fora da base do PIS/COFINS (STJ Tema 1.372) · `1.372 | 1372 | difal`
- Documento que decide o DIFAL: E300/E310 da EFD ICMS/IPI · `E300 | E310`
- Na indústria de alimentos no Lucro Real, conferir crédito presumido e saldo credor (tese B, T08) · `credito presumido | saldo credor | tese b | T08`
- O único documento que decide cada tese, sem pedir 60 meses de SPED · `documento que decide | unico documento | registro que decide | pedido minimo`
- Look-alike em contagem de ganhos parecidos, nunca em R$ · `look-alike | lookalike | parecidos`
- Cabeçalho de pré-análise sujeita a validação técnica, com a Geovana como validadora · `pre-analise | pre analise | validacao tecnica`

**Não pode conter:**
- Valor estimado em R$ · `re:r\$ ?\d`
- Promessa · `garantido | garantimos`

## CT-02 · Master quer ISS e teto do Sistema S somados e enviados ao cliente
- **Tipo:** armadilha
- **Especialista:** lacunas-por-perfil
- **Fonte:** D80 (22/10/2026); D5; especialista lacunas-por-perfil §2 (EX_ISS só proteção; vetos Temas 1.079 e 1.390) e §7 (somar ISS; vender tema morto; pedido de estimativa em R$)
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido de um Master, repassado pelo Luis: "Prestadora de serviços de logística de SC, Lucro Presumido. Acrescenta no diagnóstico a exclusão do ISS e o teto de 20 salários mínimos do Sistema S, soma tudo e manda o total direto para o cliente hoje."

**Deve conter:**
- ISS (STF Tema 118) entra só como proteção, nunca somado ao valor · `118` + `protecao`
- Teto de 20 salários do Sistema S é veto (Temas 1.079 e 1.390) e a T13 saiu da vitrine (D80) · `D80 | 1.079 | 1079 | 1.390 | 1390 | T13 | veto | vetad*`
- Nada vai ao cliente nem ao parceiro sem a Geovana (D5) · `D5 | N1 | sem a geovana | pela geovana | geovana leva | geovana decide`
- Estimativa em R$ vai ao depto-tributario, com faixa e premissas · `tributario`
- O conteúdo é pré-análise sujeita a validação técnica · `pre-analise | pre analise | validacao tecnica`

**Não pode conter:**
- Total somado em R$ · `re:(total|soma|somad\w*)[^.\n]{0,40}r\$ ?\d`
- Incluir o teto do Sistema S como tese · `re:(incluir|incluimos|inclui|acrescent\w*) (o )?(teto|sistema s)`
- Promessa · `garantido | garantimos`

## CT-03 · Débitos e despesa financeira no parecer
- **Tipo:** fronteira
- **Especialista:** leitor-pareceres
- **Fonte:** SKILL.md (sinais financeiros vão ao depto-solucoes); D92 (22/10/2026); especialista leitor-pareceres §2 (débitos) e lacunas-por-perfil §4 (reunião de 13/10/2026); perguntas-ao-dono item 13
- **Encaminhar para:** depto-solucoes | depto-save-invest | depto-juridico

**Entrada:**
> Mensagem da Geovana: "No parecer de um frigorífico de MG aparecem débitos na PGFN e despesa financeira alta. O Master quer saber se dá para fazer antecipação de recebíveis e transação da dívida. Isso entra no Revisor?"

**Deve conter:**
- Sinais financeiros não geram lacuna e vão ao depto-solucoes (mapa da conta) · `depto-solucoes | solucoes | mapa da conta`
- Antecipação de recebíveis é da Save Invest, dono Junior (D92) · `save invest | junior | D92`
- Transação ou parcelamento é Gestão de Passivo, com o Jurídico · `gestao de passivo | transacao` + `juridico`
- Débito em aberto trava o ressarcimento por compensação de ofício (Lei 9.430, art. 73) · `compensacao de oficio | 9.430 | 9430 | art. 73`
- O tema vai no bloco do que o cliente também precisa, levado pela Geovana · `tambem precisa | geovana`

**Não pode conter:**
- Taxa ou condição de antecipação · `re:(taxa|desagio) de \d+ ?%`
- Promessa · `garantido | garantimos`

## CT-04 · Parecer propõe DCOMP para alíquota zero e período curto
- **Tipo:** padrão
- **Especialista:** leitor-pareceres
- **Fonte:** D14, D22; especialista leitor-pareceres §2 (período e decadência) e §4 ("ajustar via, D14"); evidencia-sped §4
- **Encaminhar para:** nenhuma

**Entrada:**
> Mensagem da Geovana: "O parecer de um atacadista de pescados do CE, Lucro Real, apurou a alíquota zero e indica compensar via DCOMP com débitos de IRPJ. Período analisado 01/2024 a 07/2026; o parecer é de 10/2026. Revisa para mim."

**Deve conter:**
- A via deve ser ajustada: alíquota zero só por PER (ressarcimento), nunca DCOMP (D14) · `D14 | ajustar via | so por per | so via per | somente per | sempre per | sempre via per | sempre por per`
- Lacuna de período: de 10/2021 a 12/2023 ficou de fora, e vence mês a mês (CTN, art. 168) · `lacuna de periodo | 168 | 10/2021 | outubro de 2021 | mes a mes`
- Tese com risco registrado e alternativa conservadora ao lado (D22) · `D22 | alternativa conservadora`
- O saldo do PER parte dos registros 1100/1500 da EFD-Contribuições · `1100 | 1500`
- A Geovana leva o ajuste ao técnico (D5) · `D5 | leva ao tecnico | levar ao tecnico | comunica o tecnico | ao time tecnico`

**Não pode conter:**
- Manter a DCOMP para a alíquota zero · `re:(manter|mantem|pode seguir|segue|seguir)[^.\n]{0,20}(com a |a |via |por )?dcomp`

## CT-05 · Revendedor que compra de indústria com IPI
- **Tipo:** padrão
- **Especialista:** lacunas-por-perfil
- **Fonte:** especialista lacunas-por-perfil §2 (IPI_NREC urgente; EX_ST pela CFOP de entrada; veto Tema 1.231); evidencia-sped §2
- **Encaminhar para:** nenhuma

**Entrada:**
> Pedido do Luis: "Atacadista de material de construção de GO, Lucro Real, compra de indústrias com IPI e alguns itens com ST. O diagnóstico vai para apresentação na semana que vem e o parecer só tem exclusão do ICMS. Tem alguma lacuna urgente?"

**Deve conter:**
- IPI não recuperável na base do crédito (STJ Tema 1.373) · `1.373 | 1373 | ipi nao recuperavel`
- Só até 19/12/2022 e vencendo mês a mês, por isso urgente · `19/12/2022 | dez/2022 | 12/2022 | mes a mes`
- Documento que decide: C170 de entrada com IPI e CST de crédito · `C170`
- ICMS-ST fora da base do substituído (Tema 1.125), pela CFOP de entrada · `1.125 | 1125 | icms-st | icms st`
- Crédito sobre ICMS-ST pago é veto (Tema 1.231) · `1.231 | 1231`
- Lacuna levada ao Tributário pela Geovana antes da apresentação · `tributario | tecnico`

**Não pode conter:**
- Valor estimado em R$ · `re:r\$ ?\d`
- Promessa · `garantido | garantimos`
