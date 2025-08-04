#!/bin/bash

echo "🔍 Verificando status SSL..."
echo "============================"

DOMAIN="hotspot.flcomm.com.br"

# Verificar se certificados existem
if [ -f "certbot/conf/live/$DOMAIN/fullchain.pem" ]; then
    echo "✅ Certificado encontrado"
    
    # Verificar validade
    echo "📅 Verificando validade..."
    docker-compose run --rm --entrypoint "\
      openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -text -noout | grep 'Not After'" certbot
    
    # Testar conexão HTTPS
    echo "🌐 Testando conexão HTTPS..."
    if curl -s -I https://$DOMAIN > /dev/null 2>&1; then
        echo "✅ HTTPS funcionando corretamente"
    else
        echo "❌ Erro na conexão HTTPS"
    fi
    
    # Verificar redirecionamento HTTP
    echo "🔄 Testando redirecionamento HTTP..."
    if curl -s -I http://$DOMAIN | grep -q "301"; then
        echo "✅ Redirecionamento HTTP → HTTPS funcionando"
    else
        echo "❌ Redirecionamento não configurado"
    fi
    
else
    echo "❌ Certificado não encontrado"
    echo "Execute: ./scripts/setup-https-flcomm.sh"
fi

echo ""
echo "📊 Status dos containers:"
docker-compose ps
