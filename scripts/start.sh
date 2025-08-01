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

# Verificar se o usuário está no grupo docker
if ! groups $USER | grep -q docker; then
    echo "⚠️  Usuário não está no grupo docker!"
    echo "Execute: sudo usermod -aG docker $USER"
    echo "Depois faça logout/login ou reinicie o sistema"
    exit 1
fi

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p logs backups uploads ssl

# Verificar se existe .env
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado! Criando arquivo padrão..."
    cp .env.example .env 2>/dev/null || echo "Arquivo .env.example não encontrado"
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Construir e iniciar containers
echo "🔨 Construindo e iniciando containers..."
docker-compose up -d --build

# Aguardar containers iniciarem
echo "⏳ Aguardando containers iniciarem..."
sleep 10

# Verificar status
echo "📊 Status dos containers:"
docker-compose ps

echo ""
echo "✅ MIKROTIK MANAGER iniciado com sucesso!"
echo ""
echo "🌐 Acesse: https://localhost ou http://localhost:3000"
echo "👤 Login: admin@demo.com"
echo "🔑 Senha: admin123"
echo ""
echo "📋 Para ver logs: ./scripts/logs.sh"
echo "🛑 Para parar: ./scripts/stop.sh"
