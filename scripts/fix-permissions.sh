#!/bin/bash

echo "🔧 Corrigindo permissões do Docker..."

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Iniciar e habilitar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verificar se Docker está rodando
if systemctl is-active --quiet docker; then
    echo "✅ Docker está rodando"
else
    echo "❌ Erro ao iniciar Docker"
    exit 1
fi

echo ""
echo "⚠️  IMPORTANTE: Faça logout e login novamente ou execute:"
echo "   newgrp docker"
echo ""
echo "Depois execute: ./scripts/start.sh"
