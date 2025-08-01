#!/bin/bash

echo "🔄 Reiniciando MIKROTIK MANAGER..."
echo "================================"

# Parar containers
echo "⏹️  Parando containers..."
docker-compose down

# Limpar cache do Docker se necessário
echo "🧹 Limpando cache..."
docker system prune -f

# Construir e iniciar novamente
echo "🚀 Construindo e iniciando..."
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
