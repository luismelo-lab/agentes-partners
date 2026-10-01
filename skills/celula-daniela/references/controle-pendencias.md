# Controle de pendências dos Masters (Acompanhamento & SLA)

**Arquivo:** `~/agentes-partners/celulas/daniela/Controle-Pendencias-Masters.xlsx` (confidencial, permissão 600).
**Script:** `~/.claude/skills/celula-daniela/scripts/pendencias.py`. **Dona:** Daniela. Ela pode editar à mão; o script preserva o que ela escreve e só recalcula as colunas automáticas.

## Colunas
| Coluna | Quem preenche | Observação |
|---|---|---|
| ID | script | `PM-AAAA-NNNN` |
| Data abertura, Master, Canal, Nº GLPI, Contato no parceiro | Triagem → Daniela aprova | contato = só o nome |
| Tipo de demanda, Categoria | Triagem | código do `sla.json` |
| Descrição | Triagem | 1 frase, sem dado sensível, sem valor de crédito |
| Cliente, Negócio HubSpot | Triagem | razão social + ID |
| Área de destino, Responsável na área | Triagem / Daniela | |
| Status | Daniela (ou `--status`) | Aberta → Aguardando dados do parceiro → Encaminhada → Em andamento na área → Aguardando retorno ao parceiro → Concluída/Cancelada |
| Prazo 1ª resposta, Prazo solução | script (sla.json, dias úteis) | notificação da Receita: prazo legal preenchido à mão (`--prazo`) |
| Dias em aberto, Situação SLA | script (`--atualizar`) | 🟢 no prazo · 🟡 vence hoje/amanhã · 🔴 atrasada · ✅ concluída · ⚪ sem prazo |
| Última cobrança | `--cobranca` depois que a Daniela cobrou | |
| Próxima ação | Daniela / Acompanhamento | |
| Data conclusão | script (`--concluir`) | |
| Foi ponte? (S/N) | Triagem sugere, Daniela confirma | mede o trabalho que dá para delegar |
| Aprovado por | obrigatório | sem aprovação a linha não entra |

## Rotina diária (proposta)
1. **Manhã (5 min):** `python3 pendencias.py --atualizar` → lista 🔴 e 🟡.
2. Para cada 🔴/🟡, o subagente Acompanhamento rascunha **uma** cobrança (à área) e, se o parceiro estiver esperando, **um** aviso (modelo 3e). Agrupar por área: uma mensagem por área com todas as pendências dela.
3. 🔒 Portão 2: a Daniela aprova e envia. Depois: `pendencias.py --cobranca <ID>`.
4. **Sexta-feira:** aba "Resumo por Master" → 3 linhas por Master para o Luis (abertas, atrasadas, % no prazo) e o que precisa dele.

## Rascunho de cobrança à área (modelo)
```
Olá, <nome/área>! Passando para acompanhar os pedidos dos parceiros Masters que estão com vocês:
- <PM-ID> · <cliente> · <o que foi pedido> · pedido em <dd/mm>, previsão <dd/mm> (<n> dias em atraso)
- ...
Algum deles depende de algo do nosso lado? Se precisarem de mais prazo, me digam a nova data para eu alinhar com o parceiro.
Obrigada! Daniela
```
Regra de escalonamento (proposta a validar): 1ª cobrança no dia do vencimento → 2ª após 2 dias úteis → 3ª com cópia ao gestor da área → Luis se passar de 5 dias úteis de atraso ou se for urgente.

## Integração futura com o GLPI
Quando o GLPI entrar em produção, cada linha passa a ter o Nº do chamado e o status virá do GLPI. Até lá o controle é a fonte. Sugestão ao TI (não construído): categoria do chamado = área de destino; campos obrigatórios = "dados mínimos" do `sla.json`; SLA do GLPI = esta tabela validada.
