#!/bin/zsh
# Backup diário da estrutura de agentes para o OneDrive da Save (nuvem corporativa).
# Fica de fora: a credencial (.env) e a base da Receita (recriável com receita_cnpj.py --carregar).
# Versões: 1 pasta por dia, mantidas por 30 dias.
set -e
DEST="$HOME/Library/CloudStorage/OneDrive-SAVECOMPANY/Backups/agentes-partners"
HOJE=$(date +%F)
mkdir -p "$DEST/$HOJE"
EXC=(--exclude .env --exclude 'anexos' --exclude 'anexos-cache.json' --exclude '*.sqlite' --exclude node_modules --exclude .DS_Store --exclude '__pycache__')
rsync -a --delete $EXC "$HOME/agentes-partners/" "$DEST/$HOJE/agentes-partners/"
rsync -a --delete $EXC "$HOME/.claude/skills/" "$DEST/$HOJE/skills/"
rsync -a --delete $EXC "$HOME/.claude/scheduled-tasks/" "$DEST/$HOJE/scheduled-tasks/"
find "$DEST" -mindepth 1 -maxdepth 1 -type d -mtime +30 -exec rm -rf {} +
echo "$(date '+%F %T') ok $(du -sh "$DEST/$HOJE" | cut -f1)" >> "$HOME/agentes-partners/infra/backup.log"
