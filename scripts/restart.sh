#!/bin/bash

echo "🔄 Reiniciando MIKROTIK MANAGER..."

# Parar containers
./scripts/stop.sh

# Aguardar um pouco
sleep 3

# Iniciar novamente
./scripts/start.sh
