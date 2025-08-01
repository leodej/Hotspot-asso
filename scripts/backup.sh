#!/bin/bash

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="mikrotik_manager_backup_$DATE.sql"

echo "💾 Criando backup do banco de dados..."

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Fazer backup do PostgreSQL
docker-compose exec -T postgres pg_dump -U mikrotik mikrotik_manager > "$BACKUP_DIR/$BACKUP_FILE"

# Comprimir o backup
gzip "$BACKUP_DIR/$BACKUP_FILE"

echo "✅ Backup criado: $BACKUP_DIR/$BACKUP_FILE.gz"

# Limpar backups antigos (manter apenas os últimos 7 dias)
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "🧹 Backups antigos removidos."
