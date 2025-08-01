#!/bin/bash

echo "🔄 Atualizando MikroTik Manager..."

# Fazer backup antes da atualização
./scripts/backup.sh

# Parar serviços
docker-compose down

# Atualizar código (se usando Git)
if [ -d ".git" ]; then
    git pull origin main
fi

# Reconstruir e iniciar
docker-compose up -d --build

echo "✅ Atualização concluída!"
