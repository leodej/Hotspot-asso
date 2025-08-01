#!/bin/bash

if [ -z "$1" ]; then
    echo "❌ Uso: ./scripts/restore.sh <arquivo_backup.sql.gz>"
    echo "📁 Backups disponíveis:"
    ls -la ./backups/*.gz 2>/dev/null || echo "   Nenhum backup encontrado."
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Arquivo de backup não encontrado: $BACKUP_FILE"
    exit 1
fi

echo "🔄 Restaurando backup: $BACKUP_FILE"

# Descomprimir se necessário
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | docker-compose exec -T postgres psql -U mikrotik -d mikrotik_manager
else
    cat "$BACKUP_FILE" | docker-compose exec -T postgres psql -U mikrotik -d mikrotik_manager
fi

echo "✅ Backup restaurado com sucesso!"
