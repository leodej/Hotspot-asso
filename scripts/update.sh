#!/bin/bash

echo "🔄 Atualizando MIKROTIK MANAGER..."

# Fazer backup antes da atualização
echo "💾 Criando backup de segurança..."
./scripts/backup.sh

# Parar aplicação
echo "🛑 Parando aplicação..."
docker-compose stop app

# Atualizar código (se usando Git)
if [ -d ".git" ]; then
    echo "📥 Atualizando código do repositório..."
    git pull origin main
fi

# Reconstruir e reiniciar
echo "🔨 Reconstruindo aplicação..."
docker-compose build app
docker-compose up -d app

echo "✅ Atualização concluída!"

# Verificar status
./scripts/logs.sh app
