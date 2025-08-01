#!/bin/bash

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ Uso: ./scripts/restore.sh <arquivo_backup>"
    echo "📁 Backups disponíveis:"
    ls -la ./backups/mikrotik_manager_backup_*.sql.gz 2>/dev/null || echo "   Nenhum backup encontrado"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Arquivo de backup não encontrado: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  ATENÇÃO: Esta operação irá substituir todos os dados atuais!"
read -p "Deseja continuar? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Operação cancelada"
    exit 1
fi

echo "🔄 Restaurando backup: $BACKUP_FILE"

# Parar a aplicação
docker-compose stop app

# Restaurar banco de dados
gunzip -c "$BACKUP_FILE" | docker-compose exec -T postgres psql -U mikrotik -d mikrotik_manager

if [ $? -eq 0 ]; then
    echo "✅ Backup restaurado com sucesso!"
    
    # Reiniciar aplicação
    docker-compose start app
    echo "🚀 Aplicação reiniciada"
else
    echo "❌ Erro ao restaurar backup"
    docker-compose start app
    exit 1
fi
