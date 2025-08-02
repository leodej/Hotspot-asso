#!/bin/bash

echo "🔍 Verificando portas do MIKROTIK MANAGER..."
echo "============================================"

# Função para verificar porta
check_port() {
    local port=$1
    local service=$2
    
    if ss -tlnp | grep -q ":$port "; then
        echo "✅ Porta $port ($service) - ATIVA"
    else
        echo "❌ Porta $port ($service) - INATIVA"
    fi
}

# Verificar portas principais
check_port 3000 "Aplicação Next.js"
check_port 80 "Nginx HTTP"
check_port 443 "Nginx HTTPS"
check_port 5432 "PostgreSQL"
check_port 6379 "Redis"
check_port 9090 "Prometheus"
check_port 3001 "Grafana"

echo ""
echo "🌐 URLs de Acesso:"
echo "   Aplicação: http://localhost:3000"
echo "   Nginx HTTP: http://localhost"
echo "   Nginx HTTPS: https://localhost"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana: http://localhost:3001"

echo ""
echo "🔧 Para testar conectividade:"
echo "   curl http://localhost:3000/api/health"
