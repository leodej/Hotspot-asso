#!/bin/bash

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="mikrotik_manager_backup_${TIMESTAMP}.sql.gz"

echo "💾 Iniciando backup do banco de dados..."

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Fazer backup do banco de dados
docker-compose exec -T postgres pg_dump -U mikrotik mikrotik_manager | gzip > "$BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup criado com sucesso: $BACKUP_DIR/$BACKUP_FILE"
    
    # Limpar backups antigos (manter apenas os últimos 10)
    cd $BACKUP_DIR
    ls -t mikrotik_manager_backup_*.sql.gz | tail -n +11 | xargs -r rm
    echo "🧹 Backups antigos removidos"
    
    # Mostrar tamanho do backup
    echo "📊 Tamanho do backup: $(du -h $BACKUP_FILE | cut -f1)"
else
    echo "❌ Erro ao criar backup"
    exit 1
fi
