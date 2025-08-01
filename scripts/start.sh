#!/bin/bash

echo "🚀 Iniciando MikroTik Manager..."

# Verificar se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

# Criar rede se não existir
docker network create mikrotik-network 2>/dev/null || true

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Construir e iniciar os serviços
echo "🔨 Construindo e iniciando serviços..."
docker-compose up -d --build

# Aguardar os serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Verificar status dos serviços
echo "📊 Status dos serviços:"
docker-compose ps

# Mostrar logs
echo "📝 Logs da aplicação:"
docker-compose logs app --tail=20

echo ""
echo "✅ MikroTik Manager iniciado com sucesso!"
echo ""
echo "🌐 Acesse a aplicação em:"
echo "   - HTTP:  http://localhost"
echo "   - HTTPS: https://localhost"
echo "   - API:   https://localhost/api"
echo ""
echo "👤 Credenciais padrão:"
echo "   - Email: admin@mikrotik-manager.com"
echo "   - Senha: admin123"
echo ""
echo "📊 Monitoramento:"
echo "   - Prometheus: http://localhost:9090"
echo "   - Grafana:    http://localhost:3001 (admin/admin)"
echo ""
