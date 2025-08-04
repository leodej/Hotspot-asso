#!/bin/bash

echo "🔐 Configurando SSL para hotspot.flcomm.com.br..."

# Criar diretórios necessários
mkdir -p certbot/conf
mkdir -p certbot/www

# Obter certificado
docker-compose run --rm certbot

echo "✅ Certificado SSL configurado!"
echo "🔄 Reiniciando nginx..."
docker-compose restart nginx

echo "✅ HTTPS configurado com sucesso!"
