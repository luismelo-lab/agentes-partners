#!/bin/zsh
# Copia para o repositório as skills da Área Partners (de ~/.claude/skills) e os prompts das rotinas do Claude.
# Rode antes de cada commit: infra/repo-sincronizar.sh && git add -A && git commit -m "..."
# Proteção (13/10/2026): o rsync usa --delete e já apagaria mudanças feitas direto no repositório (Design System, 07/10).
# Por isso: sem --forcar, só mostra o que mudaria; e para se o repositório tiver mudança não commitada nas skills.
set -e
R="$HOME/agentes-partners"
SKILLS=(arquiteto-agentes celula-daniela celula-jenifer central-agentes conselho-partners depto-contratos depto-dados depto-intel-comercial
        depto-juridico depto-marketing depto-operacoes-canal depto-partner-success depto-pessoas depto-pos-venda depto-qualidade depto-resultados
        depto-ti depto-tributario gabinete recuperador revisor-diagnostico)
OPC=(-a --delete --exclude node_modules --exclude __pycache__ --exclude '*.pyc' --exclude 'scripts/ocr')
for s in $SKILLS; do
  git -C "$R" diff --quiet HEAD -- "skills/$s" || { echo "skills/$s tem mudança não commitada no repositório: faça o commit (ou copie para ~/.claude/skills) antes"; exit 1; }
done
if [ "${1:-}" != "--forcar" ]; then
  echo "Simulação (nada foi copiado). O que mudaria no repositório:"
  for s in $SKILLS; do rsync $OPC -in "$HOME/.claude/skills/$s/" "$R/skills/$s/" | sed "s#^#  $s: #"; done
  echo "Para copiar de verdade: infra/repo-sincronizar.sh --forcar"; exit 0
fi
for s in $SKILLS; do rsync $OPC "$HOME/.claude/skills/$s/" "$R/skills/$s/"; done
mkdir -p "$R/rotinas"; for t in "$HOME/.claude/scheduled-tasks"/*/SKILL.md; do n=$(basename $(dirname $t)); cp "$t" "$R/rotinas/$n.md"; done
echo "skills: ${#SKILLS} · rotinas: $(ls $R/rotinas | wc -l | tr -d ' ')"
