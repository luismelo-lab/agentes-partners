# Chamado ideal: como o especialista escreve o chamado do GLPI
**Regra do Luis (14/10/2026):** o chamado não repete a mensagem do parceiro. A triagem interpreta a conversa e passa ao agente da área: o **Gerente Tributário** (`~/.claude/skills/depto-tributario`) para `trib_*`, e o **Gerente Jurídico** (`~/.claude/skills/depto-juridico`) para `jur_*`, `contrato_padrao` e o restante. O agente da área devolve o chamado pronto, dizendo exatamente o que a área precisa fazer. O pedido vem de outro departamento já aprovado, então o especialista segue direto, sem Portão 0. Nada vai a parceiro ou cliente.

## O que o especialista devolve (campo `encaminhar.especialista`)
```json
{"agente": "Gerente Tributário | Gerente Jurídico",
 "entendemos": "2 a 3 frases com o pedido interpretado: quem, o quê, por quê, em que etapa está. Nunca copiar a mensagem.",
 "pedidos": ["Pergunta ou ação objetiva 1, que a área consegue responder ou executar", "…"],
 "anexos": ["documento que vai junto"], "faltam": ["documento que ainda falta e quem providencia"],
 "prazo_motivo": "AAAA-MM-DD · por quê (ex.: ciência em 02/10, 30 dias; prazo interno 5 dias antes)",
 "entrega": "o que esperamos receber de volta e em que formato (parecer, memória de cálculo, relatório, manifestação)",
 "riscos": "multa, perda de prazo, decadência, compensação glosada… ou 'sem risco imediato'",
 "checagens": ["o que os agentes já conferiram: etapa no HubSpot, parecer no card, card do Bitrix, CND…"],
 "reclassificado_de": "chave antiga, se o especialista mudou a categoria",
 "nao_abrir": "motivo, se o especialista concluir que não é chamado (status, material existente, fora do GLPI)"}
```
- **Pedidos:** de 1 a 5 itens numerados, cada um com verbo no infinitivo e objeto concreto: "Confirmar se o PER/DCOMP nº … foi transmitido" e não "verificar a situação". Quando houver número de processo, período (AAAA-MM) ou tributo, o item traz esse dado.
- **Tom:** técnico e curto. Sem saudação, sem "prezados", sem prometer resultado.
- **LGPD:** nunca CPF, RG, dados bancários ou senhas. Razão social e número de processo podem ir, porque a área precisa deles.

## O que cada categoria precisa para agir (checklist do especialista)
| Categoria | A área só age se o chamado trouxer | Entrega típica |
|---|---|---|
| `trib_diagnostico` | razão social, regime, período a analisar, teses pedidas, etapa atual no HubSpot e card do Bitrix; se for prioridade, o motivo (reunião marcada, prazo do cliente) | diagnóstico ou parecer no card |
| `trib_execucao` | contrato assinado, card do Bitrix, crédito ou tese a executar, período, pendência exata (DCTF, dado bancário a ajustar no e-CAC) | relatório ou memória de execução, confirmação do ajuste |
| `trib_compensacao` | tributo e competência dos débitos, saldo de crédito, nº do PER/DCOMP quando houver, se é de ofício, mensagem da caixa postal | relatório de PER/DCOMPs, compensação feita, cancelada ou revertida |
| `jur_comunicados` | tipo de documento (despacho, intimação), **data de ciência**, prazo fatal e prazo interno, se o cliente **autorizou** seguir com manifestação, PER/DCOMP envolvido | orientação e decisão de defesa |
| `jur_manifestacao` / `jur_contencioso_adm` | nº do processo ou e-processo, prazo, despacho anexo, autorização do cliente | manifestação de inconformidade ou verificação do processo |
| `jur_contencioso_jud` | objetivo da ação, tese, se já há ação própria (L12), urgência | avaliação de mandado de segurança ou ação |
| `jur_passivo` / `jur_transacao` | débitos (tributo, valor aproximado, inscrição em dívida ativa), CAPAG se houver | proposta ou parecer de passivo, análise de transação |
| `jur_rt_contrato` / `contrato_padrao` | contrato atual, cláusula ou alteração pedida, dados da empresa | aditivo, distrato ou contrato padrão |
| `jur_demandas` | pergunta jurídica exata e documento de apoio | parecer curto |

## Antes de entregar, o especialista confere
0. **Histórico primeiro** (Luis, 26/10/2026, `infra/historico-antes-do-glpi.md`): `lib/historico.py avaliar` rodado e sem resposta suficiente. O que foi achado vai em "O que já levantamos" e em `checagens` ("Histórico consultado: <fontes> · <o que faltou>"). Se o histórico responde, não há chamado.
1. "Checar antes de propor" e "Fora do GLPI" de `infra/glpi-regras.md`. Se cair ali, preenche `nao_abrir`.
2. `registro/chamados-aprendizados.md`: motivos de chamados recusados pelo time.
3. A categoria: se a triagem errou, corrige `area` e registra `reclassificado_de`.
4. Prazos jurídicos com dupla checagem: o prazo é calculado duas vezes, de forma independente. Se os cálculos divergirem, a urgência sobe para 5 e o chamado diz "prazo a confirmar".
