#!/bin/bash

echo "🔄 Reiniciando MIKROTIK MANAGER..."
echo "=================================="

# Parar containers
echo "⏹️  Parando containers..."
docker-compose down

# Aguardar um pouco
sleep 2

# Iniciar novamente
echo "🚀 Iniciando containers..."
docker-compose up -d --build

# Aguardar containers iniciarem
echo "⏳ Aguardando containers iniciarem..."
sleep 10

# Verificar status
echo "📊 Status dos containers:"
docker-compose ps

echo ""
echo "✅ Sistema reiniciado!"
echo "🌐 Acesse: http://localhost:3000"
echo "👤 Login: admin@demo.com"
echo "🔑 Senha: admin123"
