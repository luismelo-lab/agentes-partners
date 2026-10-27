# Rotinas com IA no terminal do Mac

Pedido do Luis em 27/10/2026: as 8 rotinas com IA saem das tarefas agendadas do app do Claude e passam ao terminal do Mac, junto das 7 rotinas mecânicas que já rodam lá. Os horários são os mesmos. O texto de cada rotina continua em `rotinas/<rotina>.md`, que é igual à cópia viva em `~/.claude/scheduled-tasks/<rotina>/SKILL.md`.

## 1. Como funciona
- **Comando:** `partners ia <rotina>` roda `claude -p` com o texto da rotina, dentro de `~/agentes-partners`. Mantém o Mac acordado durante a rotina (`caffeinate`), não deixa a mesma rotina rodar duas vezes ao mesmo tempo (`lockf`), registra em `logs/ia.log` e avisa o Luis se falhar.
- **Ferramentas:** Bash, leitura e escrita de arquivos, subagentes, pesquisa na web e ArtifactData (painéis). Ficam bloqueados `git push`, `rm -rf` e `sudo`.
- **Horários:** os jobs do launchd ficam em `infra/launchd/ia_rotinas.py`, com o prefixo `com.savecompany.partners-ia.`. O `instalar.sh` das rotinas mecânicas não os liga.

## 2. Passo a passo (uma vez)
1. Instale o Claude Code no terminal: `npm install -g @anthropic-ai/claude-code`.
2. Rode `claude` uma vez e entre com a conta da Save. O uso conta no mesmo plano do app.
3. Teste cada rotina sem executá-la: `~/agentes-partners/bin/partners ia <rotina> --teste`. A resposta, em `logs/ia.log`, deve ser "OK".
4. Ligue as rotinas aprovadas no teste: `python3 ~/agentes-partners/infra/launchd/ia_rotinas.py ligar <rotina>`. **Desligue a tarefa do app correspondente no mesmo momento**, senão a rotina roda em dobro.
5. Para voltar ao app: `ia_rotinas.py desligar <rotina>` e religar a tarefa no app.

## 3. Ponto de atenção
A Central de Agentes e o WhatsApp com IA leem e gravam nos painéis pela ferramenta ArtifactData. Se o teste responder "FALTA ArtifactData", essas duas continuam no app e as outras seis vão para o terminal.

## 4. Conferir
- `python3 ~/agentes-partners/infra/launchd/ia_rotinas.py status`: o que roda no terminal e o que segue no app.
- `partners logs ia`: as últimas execuções.
