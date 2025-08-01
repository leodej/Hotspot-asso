#!/bin/bash

echo "🛑 Parando MIKROTIK MANAGER..."

# Parar todos os containers
docker-compose down

# Verificar se pararam
if [ $? -eq 0 ]; then
    echo "✅ Containers parados com sucesso"
else
    echo "❌ Erro ao parar containers"
    exit 1
fi

# Mostrar status
echo "📊 Status final:"
docker-compose ps
