#!/bin/bash

echo "🛑 Parando MIKROTIK MANAGER..."
echo "=============================="

# Parar todos os containers
docker-compose down

echo "✅ Todos os containers foram parados!"
echo ""
echo "🔄 Para iniciar novamente: ./scripts/start.sh"
