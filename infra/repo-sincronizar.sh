#!/bin/zsh
# Copia para o repositório as skills da Área Partners (de ~/.claude/skills) e os prompts das rotinas do Claude.
# Rode antes de cada commit: infra/repo-sincronizar.sh && git add -A && git commit -m "..."
set -e
R="$HOME/agentes-partners"
SKILLS=(arquiteto-agentes celula-daniela celula-jenifer central-agentes conselho-partners depto-contratos depto-dados depto-intel-comercial
        depto-juridico depto-marketing depto-operacoes-canal depto-partner-success depto-pessoas depto-pos-venda depto-qualidade depto-resultados
        depto-ti depto-tributario gabinete recuperador revisor-diagnostico)
for s in $SKILLS; do rsync -a --delete --exclude node_modules --exclude __pycache__ --exclude '*.pyc' --exclude 'scripts/ocr' "$HOME/.claude/skills/$s/" "$R/skills/$s/"; done
mkdir -p "$R/rotinas"; for t in "$HOME/.claude/scheduled-tasks"/*/SKILL.md; do n=$(basename $(dirname $t)); cp "$t" "$R/rotinas/$n.md"; done
echo "skills: ${#SKILLS} · rotinas: $(ls $R/rotinas | wc -l | tr -d ' ')"
