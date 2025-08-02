#!/bin/bash

echo "🚀 Iniciando MIKROTIK MANAGER..."
echo "================================"

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado!"
    echo "Execute: sudo apt install docker.io docker-compose"
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado!"
    echo "Execute: sudo apt install docker-compose"
    exit 1
fi

# Verificar se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando ou sem permissão!"
    echo "Execute: ./scripts/fix-permissions.sh"
    exit 1
fi

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p logs backups uploads ssl

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cat > .env << 'EOF'
# Configurações da Aplicação
NODE_ENV=development
PORT=3000
JWT_SECRET=mikrotik-manager-super-secret-key-change-in-production
JWT_EXPIRES_IN=24h

# Configurações do Banco de Dados
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=mikrotik_manager
POSTGRES_USER=mikrotik
POSTGRES_PASSWORD=mikrotik123

# URL de conexão do banco
DATABASE_URL=postgresql://mikrotik:mikrotik123@postgres:5432/mikrotik_manager

# Configurações do Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis123

# Configurações de Monitoramento
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GRAFANA_ADMIN_PASSWORD=admin123
EOF
    echo "✅ Arquivo .env criado"
fi

# Gerar certificados SSL auto-assinados
if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
    echo "🔐 Gerando certificados SSL..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=BR/ST=SP/L=SaoPaulo/O=MikroTik Manager/CN=localhost" \
        > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Certificados SSL gerados com sucesso"
    else
        echo "❌ Erro ao gerar certificados SSL"
        exit 1
    fi
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down > /dev/null 2>&1

# Limpar containers órfãos
docker-compose down --remove-orphans > /dev/null 2>&1

# Construir e iniciar containers
echo "🔨 Construindo e iniciando containers..."
docker-compose up -d --build

if [ $? -ne 0 ]; then
    echo "❌ Erro ao iniciar containers"
    echo "Verificando logs..."
    docker-compose logs
    exit 1
fi

# Aguardar containers iniciarem
echo "⏳ Aguardando containers iniciarem..."
sleep 15

# Verificar status dos containers
echo "📊 Status dos containers:"
docker-compose ps

# Verificar se a aplicação está respondendo
echo ""
echo "🔍 Verificando conectividade..."

# Testar HTTP primeiro
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Aplicação HTTP funcionando"
else
    echo "⚠️  Aplicação HTTP não está respondendo ainda"
fi

echo ""
echo "🎉 MIKROTIK MANAGER INICIADO!"
echo "================================"
echo ""
echo "🌐 ACESSE O SISTEMA:"
echo "   👉 HTTP:  http://localhost:3000"
echo "   👉 HTTPS: https://localhost (aceite o certificado)"
echo ""
echo "👤 CREDENCIAIS DE LOGIN:"
echo "   📧 Email: admin@demo.com"
echo "   🔑 Senha: admin123"
echo ""
echo "📊 MONITORAMENTO:"
echo "   📈 Prometheus: http://localhost:9090"
echo "   📊 Grafana: http://localhost:3001"
echo "       Login Grafana: admin / admin123"
echo ""
echo "🔧 COMANDOS ÚTEIS:"
echo "   📋 Ver logs: ./scripts/logs.sh"
echo "   🛑 Parar: ./scripts/stop.sh"
echo "   🔄 Reiniciar: ./scripts/restart.sh"
echo ""
echo "⚠️  Para HTTPS, aceite o certificado auto-assinado no navegador"
