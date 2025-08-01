#!/bin/bash

echo "🛑 Parando MikroTik Manager..."

# Parar todos os serviços
docker-compose down

echo "✅ Todos os serviços foram parados."
