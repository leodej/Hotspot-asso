#!/bin/bash

echo "🔄 Reiniciando MIKROTIK MANAGER..."
echo "=================================="

# Parar containers
echo "⏹️  Parando containers..."
docker-compose down

# Limpar cache do Docker
echo "🧹 Limpando cache..."
docker system prune -f

# Construir e iniciar
echo "🏗️  Construindo e iniciando..."
docker-compose up -d --build

# Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 10

# Verificar status
echo "📊 Status dos containers:"
docker-compose ps

echo ""
echo "✅ Sistema reiniciado!"
echo "🌐 Acesse: http://localhost:3000"
echo "👤 Login: admin@demo.com"
echo "🔑 Senha: admin123"
echo ""
echo "🔍 Para ver logs: ./scripts/logs.sh"
