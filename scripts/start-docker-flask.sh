#!/bin/bash

echo "🚀 Iniciando MikroTik Manager Flask com Docker..."
echo "==============================================="

# Parar containers existentes
echo "⏹️  Parando containers..."
docker-compose down

# Construir e iniciar
echo "🔨 Construindo e iniciando..."
docker-compose up -d --build

# Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 5

# Verificar status
echo "📊 Status dos containers:"
docker-compose ps

echo ""
echo "✅ Sistema Flask iniciado!"
echo "🌐 URL: http://localhost:5000"
echo "📧 Login: admin@demo.com"
echo "🔑 Senha: admin123"
echo ""
echo "🔍 Para ver logs: docker-compose logs -f app"
