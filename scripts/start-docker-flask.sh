#!/bin/bash

echo "🚀 Iniciando MikroTik Manager Flask com Docker..."
echo "==============================================="

# Verificar se deve configurar HTTPS
if [ "$1" = "--https" ] || [ "$1" = "-s" ]; then
    echo "🔒 Modo HTTPS selecionado"
    HTTPS_MODE=true
else
    echo "🌐 Modo HTTP selecionado"
    HTTPS_MODE=false
fi

# Parar containers existentes
echo "⏹️  Parando containers..."
docker-compose down

# Se modo HTTPS, configurar certificados
if [ "$HTTPS_MODE" = true ]; then
    echo "🔐 Configurando HTTPS..."
    
    # Verificar se certificados já existem
    if [ ! -f "certbot/conf/live/hotspot.flcomm.com.br/fullchain.pem" ]; then
        echo "📜 Certificados não encontrados. Configurando Let's Encrypt..."
        chmod +x scripts/setup-https-flcomm.sh
        ./scripts/setup-https-flcomm.sh
        
        if [ $? -ne 0 ]; then
            echo "❌ Erro ao configurar HTTPS. Iniciando em modo HTTP..."
            HTTPS_MODE=false
        fi
    else
        echo "📜 Certificados encontrados!"
    fi
fi

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
echo "🌐 URL: https://hotspot.flcomm.com.br"
echo "📧 Login: admin@demo.com"
echo "🔑 Senha: admin123"
echo ""
echo "🔍 Para ver logs: docker-compose logs -f app"

# Mostrar informações adicionais se HTTPS
if [ "$HTTPS_MODE" = true ]; then
    echo ""
    echo "📋 Informações SSL:"
    echo "   - Certificado: Let's Encrypt"
    echo "   - Renovação: Automática a cada 12h"
    echo "   - Domínio: hotspot.flcomm.com.br"
fi
