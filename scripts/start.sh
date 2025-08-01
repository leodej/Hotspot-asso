#!/bin/bash

echo "🚀 Iniciando MIKROTIK MANAGER..."

# Verificar se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Iniciando Docker..."
    sudo systemctl start docker
    sleep 3
fi

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado. Criando arquivo padrão..."
    cp .env.example .env 2>/dev/null || echo "⚠️  Crie o arquivo .env manualmente"
fi

# Criar diretórios necessários
mkdir -p ssl logs backups uploads

# Gerar certificados SSL se não existirem
if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
    echo "🔐 Gerando certificados SSL..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=BR/ST=SP/L=SaoPaulo/O=MikroTik Manager/CN=localhost" \
        > /dev/null 2>&1
    echo "✅ Certificados SSL gerados"
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down > /dev/null 2>&1

# Construir e iniciar containers
echo "🔨 Construindo e iniciando containers..."
docker-compose up -d --build

# Aguardar containers iniciarem
echo "⏳ Aguardando containers iniciarem..."
sleep 10

# Verificar status
echo "📊 Status dos containers:"
docker-compose ps

# Verificar se a aplicação está respondendo
echo "🔍 Verificando se a aplicação está funcionando..."
sleep 5

if curl -k -s https://localhost/api/health > /dev/null; then
    echo "✅ Aplicação iniciada com sucesso!"
    echo ""
    echo "🌐 Acesse a aplicação em:"
    echo "   - Interface: https://localhost"
    echo "   - API: https://localhost/api"
    echo "   - Prometheus: http://localhost:9090"
    echo "   - Grafana: http://localhost:3001"
    echo ""
    echo "👤 Credenciais padrão:"
    echo "   - Email: admin@mikrotik-manager.com"
    echo "   - Senha: admin123"
else
    echo "⚠️  Aplicação pode estar iniciando ainda. Verifique os logs:"
    echo "   ./scripts/logs.sh"
fi
