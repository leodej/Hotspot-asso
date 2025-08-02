#!/bin/bash

echo "🚀 Iniciando MikroTik Manager Flask..."
echo "====================================="

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instalando..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt

# Criar diretórios necessários
mkdir -p templates static

echo "✅ Iniciando aplicação Flask..."
echo ""
echo "🌐 URL: http://localhost:5000"
echo "📧 Login: admin@demo.com"
echo "🔑 Senha: admin123"
echo ""

# Iniciar aplicação
python app.py
