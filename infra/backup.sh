#!/bin/zsh
# Backup diário da estrutura de agentes para o OneDrive da Save (nuvem corporativa).
# Um ÚNICO arquivo compactado por dia (antes eram ~7 mil arquivos soltos por dia: o OneDrive chegou a 48 mil
# arquivos para sincronizar em 10/10/2026). O arquivo é montado fora do OneDrive e só entra pronto e conferido.
# Fica de fora: a credencial (.env), os worktrees do Claude, a base da Receita e o modelo do Whisper (recriáveis).
# Versões: 1 arquivo por dia, mantidos por 14 dias. Restaurar: tar -xzf <arquivo> -C ~/restaurado
set -e
DEST=$(python3 "$HOME/agentes-partners/lib/caminhos.py" backups)  # pasta ativa do OneDrive (lib/caminhos.py)
[ -n "$DEST" ] || { echo "OneDrive não encontrado"; exit 1; }
mkdir -p "$DEST"
HOJE=$(date +%F)
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
NOME="agentes-partners-$HOJE.tar.gz"
EXC=(--exclude .env --exclude '*.env' --exclude .glpi --exclude anexos --exclude anexos-cache.json --exclude '*.sqlite'
     --exclude whisper --exclude node_modules --exclude .DS_Store --exclude __pycache__ --exclude '*.pyc'
     --exclude 'agentes-partners/.claude/worktrees' --exclude 'agentes-partners/dados-publicos' --exclude 'agentes-partners/logs/*.log.*')
tar -czf "$TMP/$NOME" $EXC -C "$HOME" agentes-partners -C "$HOME/.claude" skills scheduled-tasks
# confere antes de publicar: o arquivo abre e tem as três partes
tar -tzf "$TMP/$NOME" > "$TMP/lista"
for parte in agentes-partners/lib/ skills/ scheduled-tasks/; do grep -q "^$parte" "$TMP/lista" || { echo "backup incompleto: falta $parte"; exit 1; }; done
N=$(wc -l < "$TMP/lista" | tr -d ' ')
cp "$TMP/$NOME" "$DEST/$NOME.parcial" && mv -f "$DEST/$NOME.parcial" "$DEST/$NOME"
# retenção: só os arquivos de backup deste script (nunca apaga pastas nem outros arquivos)
find "$DEST" -maxdepth 1 -type f -name 'agentes-partners-*.tar.gz' -mtime +14 -exec /usr/bin/trash {} +
echo "$(date '+%F %T') ok $(du -h "$DEST/$NOME" | cut -f1) · $N itens · $NOME" >> "$HOME/agentes-partners/infra/backup.log"
