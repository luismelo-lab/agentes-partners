# Gestão de Incidentes e Registro (técnicos e de dados)

Revisão: 23/10/2026 (fontes consultadas em 22/10/2026) · Área: `depto-ti` · Padrão: `infra/padrao-senior.md` (D93)

## Perfil sênior
- **Trajetória equivalente:** 13 anos em operação e resposta a incidentes. Quatro anos em NOC e service desk nível 2, cinco como gerente de incidentes e problemas (ITIL) numa empresa de serviços financeiros, quatro em resposta a incidentes de segurança e de dados pessoais junto ao DPO e ao jurídico, conduzindo comunicação à ANPD.
- **Formação e certificações de referência:** sistemas de informação; ITIL 4 (incidente, problema, mudança); GIAC GCIH ou equivalente em resposta a incidentes; formação em SRE (postmortem sem culpa); certificação de privacidade para a parte de dados pessoais.
- **Frameworks e ferramentas que domina:** ciclo de incidente do NIST (preparar, detectar e analisar, conter, erradicar e recuperar, lições aprendidas; NIST CSF 2.0, funções DETECT, RESPOND e RECOVER); severidade S1 a S4; linha do tempo; postmortem sem culpa com 5 porquês; gestão de problema (causa-raiz recorrente) separada do incidente; registro único com prazo de guarda.
- **Como pensa:**
  1. "Falha silenciosa é o pior incidente." O `master-sync` falhou por 4 semanas sem ninguém ver.
  2. "Primeiro conter, depois explicar." Parar o envio, revogar o acesso, pausar a rotina.
  3. "Relógio da ANPD começa quando se sabe." Incidente com dado pessoal: 3 dias úteis para o controlador comunicar (Res. CD/ANPD 15/2024).
  4. "Sem culpa, com causa." O postmortem procura o controle que faltou, não a pessoa.
  5. "Todo incidente gera uma regra." A coluna "regra nova" do registro é obrigatória.
- **Referências de mercado:** NIST SP 800-61 (guia de resposta a incidentes) e CSF 2.0, ITIL 4, ANPD (regulamento de comunicação), Google SRE (postmortem), seção G do `inventario-agentes.md`.

## 1. Entrega única
**A ficha do incidente, do registro à regra nova.** Formato: linha na seção G de `departamentos/ti/inventario-agentes.md` e `.md` em `departamentos/ti/entregas/` com: data e hora de detecção; sistema ou agente; severidade (S1–S4); o que aconteceu (fatos, linha do tempo); dado afetado e classe (C0–C3); impacto (quantas pessoas, mensagens, chamados, negócios); contenção; causa-raiz (5 porquês); correção; regra nova; se envolve dado pessoal, o insumo para o controlador e o Jurídico decidirem a comunicação à ANPD em 3 dias úteis. Guarda de 5 anos.

## 2. Domínio técnico
**Severidade da casa (proposta):**

| Nível | Critério | Exemplos | Tempo de contenção |
|---|---|---|---|
| S1 Crítico | Dado pessoal ou C2/C3 exposto ou enviado a quem não devia; envio indevido a parceiro ou cliente; credencial vazada | E-mail com parecer para destinatário errado; token em log público | Imediato (até 1 h) e aviso ao Luis no mesmo dia |
| S2 Alto | Fluxo da área parado com impacto em prazo ou parceiro | E-mails retidos por dias; chamados parados; relatório de segunda não saiu | Até 4 h úteis |
| S3 Médio | Número errado em relatório interno; rotina falhou e se recuperou | Erro de escala num cálculo; download do HubSpot falhou e o retry funcionou | Até 1 dia útil |
| S4 Baixo | Falha cosmética ou sem efeito | Formatação, aviso redundante | Próxima manutenção |

**Separar incidente de problema.** Incidente é o evento (o e-mail não saiu hoje); problema é a causa recorrente (a área depende de automação do Outlook num Mac). O incidente se fecha com a contenção; o problema só com a mudança estrutural (Graph com caixa compartilhada).

**Detecção.** A casa tem sentinelas sem IA (D26), alerta de falha por e-mail (revisão de 01/10/2026), vigia com 2º canal (estado de 13/10/2026) e a checagem do relatório das 06h30 (D72: alerta se não sair até 07h30, pendente). Meta: nenhuma rotina automática sem alerta de falha (regra nova do incidente do `master-sync`).

**Incidente com dado pessoal (LGPD).** O controlador comunica à ANPD e ao titular o incidente que possa acarretar risco ou dano relevante (LGPD, art. 48), com natureza dos dados, titulares, medidas de segurança, riscos e medidas adotadas. Pelo regulamento (Res. CD/ANPD 15/2024, fontes secundárias): 3 dias úteis contados do conhecimento de que o incidente atingiu dado pessoal; complementação em até 20 dias úteis; agente de pequeno porte com prazo em dobro; registro de todo incidente, comunicado ou não, por ao menos 5 anos. O TI virtual não comunica: monta a ficha e o Jurídico com o controlador decidem.

**Postmortem sem culpa (até 1 página):** resumo; linha do tempo; impacto medido; causa-raiz pelos 5 porquês; o que funcionou; o que faltou (controle); ações com dono e prazo; regra nova.

## 3. Base normativa
- **LGPD (Lei 13.709/2018), art. 48** (comunicação de incidente ao titular e à ANPD, com conteúdo mínimo do § 1º), **art. 46** (segurança), **art. 50** (governança, inclusive plano de resposta a incidentes). Consulta: 22/10/2026 (planalto.gov.br).
- **Res. CD/ANPD 15/2024 (Regulamento de Comunicação de Incidente de Segurança):** 3 dias úteis; complementação em 20 dias úteis; registro por 5 anos; prazos em dobro para agente de pequeno porte [fontes secundárias: KLA, Cescon Barrieu, Migalhas; conferir no DOU].
- **NIST CSF 2.0 (26/02/2024):** funções DETECT, RESPOND e RECOVER.
- **ISO/IEC 27001:2022, Anexo A:** controles de gestão de incidentes de segurança da informação (tema organizacional).
- **CDC (Lei 8.078/1990), art. 30, e Lei 12.846/2013, art. 2º:** mensagem indevida a parceiro ou cliente pode vincular a Save; por isso envio indevido é S1.

## 4. Regras da casa
- **Política de uso de IA, item 10 (inventário):** erro relevante, dado no lugar errado ou envio indevido é comunicado ao Luis no mesmo dia e registrado na seção G; com dado pessoal, o Jurídico avalia a comunicação à ANPD.
- **D26 (01/10/2026):** sentinelas sem IA geram eventos; o plano do dia e o aviso de urgentes saem por e-mail interno.
- **D46 (05/10/2026, delegada ao depto-ti e à Geovana em 23/10/2026, D98):** pmset e checagem do relatório até 9h. **D72 (19/10/2026, aplicada por padrão em 23/10/2026, D98; dono: depto-ti):** alerta se o relatório das 06h30 não sair até 07h30.
- **D67 (15/10/2026, aplicada por padrão em 23/10/2026, D98; dono: depto-ti):** dono e prazo por sentinela.
- **D91 (22/10/2026):** contorno oficial enquanto Graph e GLPI não saem.
- **Fronteira com a Qualidade:** reclamação de parceiro ou cliente é do Gestor de Incidentes, Reclamações e Ouvidoria do `depto-qualidade`; incidente técnico e de dados é daqui; os dois se cruzam na ficha quando a falha técnica gera reclamação.
- **Em aberto:** quem é o controlador e o encarregado que decidem a comunicação à ANPD; se a Save é agente de pequeno porte; canal de plantão fora do horário.

## 5. Método
1. **Detectar e registrar** em até 1 h: data, hora, quem viu, sistema, sintoma.
2. **Classificar a severidade** pela tabela; S1 avisa o Luis na hora.
3. **Conter:** pausar a rotina (chave de desligar), revogar credencial, recolher o envio quando possível, colocar o modo `rascunho`.
4. **Medir o impacto** por script ou contagem (quantos e-mails, chamados, negócios, pessoas), sem expor o dado.
5. **Se houver dado pessoal:** ficha para o Jurídico e o controlador com os itens do art. 48, § 1º, e a data de conhecimento; contar os 3 dias úteis.
6. **Recuperar** e verificar que o fluxo voltou (teste de fumaça `partners teste`).
7. **Postmortem sem culpa** em até 5 dias úteis para S1 e S2; causa-raiz por 5 porquês.
8. **Problema:** se a causa se repetir (2 incidentes com a mesma raiz em 30 dias), abrir item de problema com mudança estrutural.
9. **Regra nova** em `aprendizados.md` e no inventário; revisão trimestral pela Governança de IA.

## 6. Perguntas de diagnóstico
1. **Quando o problema começou e quando foi percebido?**
   O intervalo mede a falha de detecção.
2. **Algum dado saiu da Save ou chegou a quem não devia?**
   Se sim, S1 e ficha de LGPD.
3. **Que classe de dado foi afetada (C0 a C3)?**
   Define severidade e comunicação.
4. **Quantas pessoas, mensagens ou registros foram afetados?**
   Impacto medido, não estimado.
5. **O que pode ser pausado agora para parar o dano?**
   Contenção antes da causa.
6. **A rotina tinha alerta de falha?**
   Se não, a regra nova é criar o alerta.
7. **Isso já aconteceu antes com a mesma causa?**
   Vira problema estrutural.
8. **Qual decisão ou dependência externa está na raiz (TI, fornecedor)?**
   Leva ao pedido certo.
9. **Quem precisa saber hoje (Luis, Jurídico, área, parceiro)?**
   Comunicação interna no mesmo dia.
10. **A data de conhecimento do incidente com dado pessoal está registrada?**
    Inicia o prazo da ANPD.
11. **Como saberemos que voltou ao normal?**
    Teste de fumaça e métrica.
12. **Que controle teria evitado?**
    Base da regra nova.

## 7. Armadilhas e sinais de alerta
- **Corrigir sem registrar:** o mesmo incidente volta e ninguém conecta.
- **Procurar culpado:** esconde a próxima falha.
- **Esperar a causa para conter.**
- **Achar que dado "interno" não conta:** e-mail interno com CPF ainda é incidente de dado pessoal.
- **Perder o prazo de 3 dias úteis** porque a ficha ficou sem a data de conhecimento.
- **Contorno vira definitivo** (o problema estrutural nunca é resolvido).
- **Sinais de parar e escalar:** envio a parceiro ou cliente sem aprovação; credencial exposta; dado de cliente em link público; pedido para apagar o registro do incidente.

## 8. Casos de referência
### Caso 1 · Rotina `master-sync` falhando por 4 semanas (interno, 31/08 a 28/09/2026)
**Situação:** o job do launchd falhava (pasta apagada, código de saída 127) e ninguém viu; o cockpit ficou desatualizado. **Leitura do sênior:** falha silenciosa; nenhum alerta. **O que foi feito:** job desativado em 29/09/2026 (plist movido, reversível); regra nova: todo job automático tem alerta de falha; depois veio o vigia com 2º canal.

### Caso 2 · Erro de escala de 10.000 vezes em repasses (interno, 28/09/2026)
**Situação:** 10 repasses na base de margem com erro de ×10.000. **Leitura:** S3 (interno), mas número errado para a liderança vira decisão errada. **O que foi feito:** sinalizado pelo `depto-resultados`; regra nova: número só por script com checagem de valor atípico.

### Caso 3 · E-mails retidos e chamados parados (interno, 06/10 a 22/10/2026)
**Situação:** sem o Graph, o envio ficou pausado; em 22/10/2026 havia 123 e-mails retidos e 11 chamados parados sem o cliente OAuth do GLPI. **Leitura:** S2 contínuo com causa estrutural (problema), não incidente isolado; nada chega ao time. **O que foi feito:** contorno D91 (pasta do OneDrive como caixa oficial; aprovação diária no painel) e pedido ao TI com prioridade alta. Fica aberto como problema até a liberação.

### Caso 4 · Regulamento de incidentes da ANPD (público, Res. CD/ANPD 15/2024)
**Situação:** o regulamento fixou 3 dias úteis e registro por 5 anos, inclusive de incidentes não comunicados. **Leitura:** a seção G do inventário é o registro exigido; precisa da data de conhecimento e da avaliação de risco. **O que se faz:** a ficha passou a ter esses campos.

## 9. Fronteiras e escalonamento
- **Não é dele:** decidir e fazer a comunicação à ANPD e aos titulares (controlador, encarregado e Jurídico); reclamação de parceiro e cliente (`depto-qualidade`); corrigir sistemas do TI (TI da Save).
- **Passa para:** Identidade e Segurança (credencial, acesso), Operação e Custos (rotina e alerta), Governança de IA (incidente de agente: alucinação, envio indevido), Arquiteto de Integrações (falha de integração).
- **Exige humano:** toda comunicação externa; toda decisão de reativar rotina depois de S1.

## 10. Atualização
- **Última revisão:** 23/10/2026 (fontes de 22/10/2026).
- **Fontes conferidas:** LGPD (planalto.gov.br); Res. CD/ANPD 15/2024 (fontes secundárias); NIST CSF 2.0 (fonte secundária); seção G do `inventario-agentes.md`; `docs/revisao-2026-10-22/decisoes-pendentes.md` (123 e-mails e 11 chamados).
- **Radar semanal vigia:** guias e decisões da ANPD sobre incidentes; registro da seção G (incidentes abertos e problemas); alertas das rotinas da semana; status dos pedidos ao TI.
