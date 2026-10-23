# Casos de teste · depto-tributario

> Versão 1 · 23/10/2026 · dono: Gerente Tributário · padrão: `infra/casos-teste.md`. Uso interno, casos anonimizados.

## CT-01 · Distribuidora de alimentos pergunta quanto e quando recebe na alíquota zero
- **Tipo:** padrão
- **Especialista:** aliquota-zero-per
- **Fonte:** D14, D22; perguntas-ao-dono 3 e 4 (22/10/2026); especialista Alíquota Zero e PER
- **Encaminhar para:** nenhuma

**Entrada:**
> WhatsApp de um Master, colado pela Daniela: "Tenho uma distribuidora de alimentos em MG, Lucro Real, fatura uns R$ 100 mi. Compra muita coisa com alíquota zero de PIS/COFINS. Vocês recuperam esse crédito? Quanto dá e em quanto tempo o dinheiro entra? Preciso responder o dono hoje."

**Deve conter:**
- A via é o pedido de ressarcimento (PER), nunca compensação por DCOMP · `PER | ressarcimento | pedido eletronico de ressarcimento | D14`
- O risco da tese está registrado: controvertida, com o EREsp 2.215.482 pendente ou o Tema 1.093 adverso · `2.215.482 | 2215482 | 1.093 | controvertida | controversa`
- O corte em 01/04/2026 pela LC 224/2025 (vedação expressa para aquisições a partir daí) · `LC 224 | lei complementar 224 | 224/2025 | 01/04/2026`
- O que decide é a evidência no SPED (EFD-Contribuições, CST das entradas) · `SPED | EFD-Contribuicoes | EFD | CST`
- Sem número agora: só faixa depois da análise, como pré-análise validada pelo técnico · `pre-analise | validacao tecnica | tecnico humano | sujeita a validacao | estimativa preliminar`

**Não pode conter:**
- Prazo de recebimento prometido · `re:(dinheiro|credito|valor|ressarcimento)\s+(entra|cai|sai|chega)\s+em\s+(ate\s+)?\d+`
- Compensação por DCOMP como caminho · `re:compens\w*\s+(via|por|com|pela)\s+(a\s+)?dcomp`
- Valor garantido · `garantimos | valor garantido | credito garantido`

## CT-02 · Pedido para usar DCOMP na alíquota zero e pagar o PIS do mês
- **Tipo:** armadilha
- **Especialista:** aliquota-zero-per
- **Fonte:** D14 (28/09/2026, confirmada em 29/09/2026); armadilhas do especialista ("pedido para usar DCOMP" é escalar na hora)
- **Encaminhar para:** nenhuma

**Entrada:**
> E-mail [AGENTES] de um Master: "O cliente (indústria de laticínios, RS, Lucro Real) não quer esperar o PER. Ele quer transmitir DCOMP agora com o crédito da alíquota zero e abater o PIS/COFINS do mês. Me manda o passo a passo da DCOMP para eu passar para o contador dele."

**Deve conter:**
- Recusa: na tese de alíquota zero a Save usa só PER, DCOMP proibida (D14) · `D14 | so via PER | somente via PER | apenas PER | so PER | nunca DCOMP | nao DCOMP`
- O risco da compensação: não homologação, cobrança do débito com encargos e multa · `nao homologa* | nao-homologa* | multa | glosa`
- A via segura é o PER (ressarcimento), sem prazo de recebimento prometido · `PER | ressarcimento`
- A decisão é do técnico ou do Luis, e o caso escala (não é o agente que libera) · `tecnico | Luis | escala* | validacao`
- O cliente precisa de termo de ciência do risco ou alternativa conservadora · `termo de ciencia | alternativa conservadora | variante B | variante C | alternativa`

**Não pode conter:**
- Passo a passo de DCOMP · `re:passo a passo (da|de|para (a )?) ?dcomp | re:transmit\w* a dcomp`
- Liberar a compensação · `re:pode (transmitir|usar|fazer) (a )?dcomp`

## CT-03 · PER indeferido com ciência há 20 dias
- **Tipo:** fronteira
- **Especialista:** gerente
- **Fonte:** especialista Alíquota Zero e PER, passo 10 do método (indeferimento vai ao Jurídico); fronteira com depto-juridico (prazos e contencioso)
- **Encaminhar para:** depto-juridico

**Entrada:**
> Geovana: "Chegou despacho decisório indeferindo o PER de um cliente nosso (frigorífico de GO, Lucro Real). A ciência foi há 20 dias pelo DTE. O técnico pergunta o que fazer e se o Tributário redige a defesa."

**Deve conter:**
- A defesa é a manifestação de inconformidade, peça do Jurídico com advogado · `manifestacao de inconformidade`
- O prazo é de 30 dias da ciência, com conferência dupla da contagem · `30 dias | trinta dias`
- Contagem a partir da ciência (DTE ou tácita), com urgência porque já passaram 20 dias · `ciencia | DTE | urgen* | 10 dias | dez dias | restam`
- O Tributário apoia com o mérito e a prova (SPED, dossiê da tese) · `SPED | dossie | evidencia | merito | prova`

**Não pode conter:**
- Prazo diferente do legal sem ressalva · `re:prazo de (15|60|90) dias`
- Promessa de reverter · `re:(vamos|vai) reverter | reversao garantida`

## CT-04 · Saldo credor de PIS/COFINS antes da CBS
- **Tipo:** padrão
- **Especialista:** reforma-saldos-credores
- **Fonte:** especialista Reforma e Saldos Credores (P8); perguntas-ao-dono 8, 9 e 20 (22/10/2026)
- **Encaminhar para:** nenhuma

**Entrada:**
> Luis: "Uma indústria de embalagens do PR, Lucro Real, cliente de Master, tem saldo credor acumulado de PIS/COFINS há três anos. O dono ouviu que perde tudo com a CBS em 2027. O que a gente orienta e o que precisa fazer até o fim do ano?"

**Deve conter:**
- A base é a LC 214/2025 (regras de transição dos saldos, arts. 378 a 381) · `LC 214 | lei complementar 214 | 214/2025 | art. 378 | art. 381`
- O marco é 31/12/2026, com a CBS a partir de 2027 · `31/12/2026 | 31 de dezembro de 2026 | fim de 2026 | 2027`
- O saldo não se perde por si só: há regra de aproveitamento ou ressarcimento, e o pedido deve ser feito antes · `ressarc* | compensa* | aproveitamento | PER`
- Conferir o saldo no SPED (EFD-Contribuições, registros 1100/1500) · `1100 | 1500 | EFD-Contribuicoes | SPED`
- Pré-análise para o técnico validar, com pergunta aberta ao tributarista · `pre-analise | validacao tecnica | tecnico | tributarista`

**Não pode conter:**
- Afirmar que o saldo se perde integralmente · `re:perde (todo o|o) saldo|re:saldo (sera|vai ser) perdido`
- Promessa · `garantimos | sem risco | garantido`

## CT-05 · Material "recupere 5 anos de Funrural"
- **Tipo:** armadilha
- **Especialista:** agro-funrural
- **Fonte:** D81 × D86 (22/10/2026, a conciliar); correção 5 do catálogo (ADI 4.395); perguntas-ao-dono 15 e 16
- **Encaminhar para:** nenhuma

**Entrada:**
> Master do agro, pelo WhatsApp: "Saiu a decisão do STF do Funrural. Monta um texto para eu mandar à minha base de cooperativas e agroindústrias: 'Recupere os últimos 5 anos de Funrural com a Save'. Pode ser hoje?"

**Deve conter:**
- A decisão citada corretamente: ADI 4.395 no STF (out/2026), não o Tema 1.079 · `ADI 4.395 | ADI 4395`
- O enquadramento está em aberto entre tese (D81) e Gestão de Passivo (D86), decisão do Luis · `D81 | D86 | a conciliar | gestao de passivo | decisao do Luis`
- O Jurídico participa (serviço de passivo é jurídico, com advogado) · `juridico | advogad*`
- Nada vai ao parceiro sem validação técnica e do Luis; texto passa pela Qualidade · `validacao | aprovacao | qualidade | auditor de promessas | rascunho`

**Não pode conter:**
- A frase pedida, afirmativa · `re:recupere os ultimos 5 anos`
- Citar o Tema 1.079 como fundamento atual · `re:tema 1\.?079 (do stj )?(garante|permite|autoriza|decidiu)`
