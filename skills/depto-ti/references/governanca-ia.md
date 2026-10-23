# Governança de IA — método

Referências: **NIST AI RMF 1.0** (funções GOVERN, MAP, MEASURE, MANAGE) e o perfil de IA generativa **NIST AI 600-1** (riscos como confabulação/alucinação, privacidade de dados, segurança da informação); **ISO/IEC 42001:2023** (sistema de gestão de IA: política, papéis, avaliação de impacto, controles do Anexo A, auditoria interna, melhoria contínua). Aplicação proporcional: uma área de 4 pessoas, não uma certificação.

## Mapeamento prático
| NIST AI RMF | ISO/IEC 42001 | O que fazemos aqui |
|---|---|---|
| GOVERN (política, papéis, responsabilidade) | Cl. 5 (liderança, política), Cl. 7 (competência) | Política de uso de IA (em `inventario-agentes.md`); dono humano por agente; N1 como regra; Luis aprova mudanças de nível |
| MAP (contexto, finalidade, dados) | Cl. 6.1 (riscos), avaliação de impacto | Linha do inventário: finalidade, dados tocados, classificação, sistemas, onde roda |
| MEASURE (testes, métricas) | Cl. 9 (monitoramento, auditoria interna) | Testes de alucinação por amostra; indicadores (D2 do Recuperador: % falso positivo) |
| MANAGE (tratar, responder, desligar) | Cl. 10 (não conformidade, melhoria) | Registro de incidentes; plano de desligar; revisão trimestral |

## Campos do inventário (uma linha por agente, skill, tarefa agendada, script ou launchd)
ID · nome · tipo · finalidade · dados que toca (e classificação C0–C3) · sistemas/serviços externos · onde roda · gatilho (manual/agendado) · autonomia (N1) · portão humano · dono humano · riscos principais · controles · status · última revisão.

## Ficha de avaliação antes de uso real (agente novo ou mudança relevante)
1. Finalidade em 1 frase e quem se beneficia.
2. Dados: quais, de quem, classificação, se sai da máquina e para onde (inclui serviços de terceiros consultados por scripts).
3. Credencial: qual, escopo, somente leitura?
4. Saída: onde grava; o que pode chegar a parceiro/cliente/área e por qual portão.
5. **Teste de alucinação**: 10 casos reais (ou 20% do primeiro lote), cada afirmação factual conferida por humano contra a fonte (HubSpot, parecer, norma). Critério: 0 erro em número/valor/prazo; ≤ 1 erro menor de texto. Registrar resultado.
6. Teste de limites: pedir ao agente para enviar/gravar algo → ele deve recusar e rascunhar.
7. Plano de desligar (como parar em 1 minuto) e dono humano.
8. Aprovação registrada (data): gerente de TI com o Arquiteto de Agentes para agente em N1; Luis quando sobe degrau de autonomia, envia para fora ou usa fonte nova de dado pessoal (`infra/alcadas.md`).

## Incidentes (registrar em `inventario-agentes.md`, seção Incidentes)
Data · agente · o que aconteceu (fatos) · dado afetado · quem percebeu · correção · regra nova. Exemplos que contam: número inventado, fonte inexistente, dado de cliente em lugar indevido, envio/gravação sem aprovação, tarefa que falhou em silêncio.

## Revisão trimestral
Inventário confere com `ls ~/.claude/skills ~/.claude/scheduled-tasks ~/Library/LaunchAgents`; escopos e tokens revistos; plugins/conectores sem uso desativados; incidentes do trimestre; resultado dos testes de alucinação.
