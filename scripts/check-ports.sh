#!/bin/bash

echo "🔍 Verificando portas do MIKROTIK MANAGER..."
echo "================================================"

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando!"
    exit 1
fi

# Verificar containers
echo "📦 Status dos Containers:"
docker-compose ps

echo ""
echo "🌐 Portas em uso:"
echo "------------------------------------------------"

# Verificar portas específicas
ports=(80 443 3000 5432 6379 9090 3001)

for port in "${ports[@]}"; do
    if ss -tlnp | grep -q ":$port "; then
        service=$(ss -tlnp | grep ":$port " | awk '{print $1}')
        echo "✅ Porta $port: ATIVA ($service)"
    else
        echo "❌ Porta $port: INATIVA"
    fi
done

echo ""
echo "🔗 URLs de Acesso:"
echo "------------------------------------------------"
echo "🌐 Interface Principal: https://localhost"
echo "🌐 Interface HTTP: http://localhost"
echo "📱 Aplicação Direta: http://localhost:3000"
echo "🔧 API Health: http://localhost:3000/api/health"
echo "📊 Grafana: http://localhost:3001"
echo "📈 Prometheus: http://localhost:9090"

echo ""
echo "👤 Credenciais de Login:"
echo "------------------------------------------------"
echo "📧 Email: admin@demo.com"
echo "🔑 Senha: admin123"
echo "👑 Papel: Administrador"
echo ""
echo "📧 Email: admin@mikrotik-manager.com"
echo "🔑 Senha: admin123"
echo "👑 Papel: Administrador"
echo ""
echo "📧 Email: manager@demo.com"
echo "🔑 Senha: manager123"
echo "👑 Papel: Gerente"

echo ""
echo "🧪 Testando conectividade..."
echo "------------------------------------------------"

# Testar API Health
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ API Health: FUNCIONANDO"
else
    echo "❌ API Health: FALHA"
fi

# Testar página principal
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Aplicação: FUNCIONANDO"
else
    echo "❌ Aplicação: FALHA"
fi

echo ""
echo "📋 Para ver logs em tempo real:"
echo "   ./scripts/logs.sh"
echo ""
echo "🔄 Para reiniciar o sistema:"
echo "   ./scripts/stop.sh && ./scripts/start.sh"
