#!/bin/bash

echo "🛑 Parando MIKROTIK MANAGER..."

# Parar todos os containers
docker-compose down

echo "✅ Containers parados com sucesso!"

# Mostrar status
docker-compose ps
