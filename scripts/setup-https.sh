#!/bin/bash

echo "=== Configuração HTTPS com Let's Encrypt ==="
echo ""

# Verificar se o domínio foi fornecido
if [ -z "$1" ]; then
    echo "Uso: $0 <seu-dominio.com> [email]"
    echo "Exemplo: $0 meusite.com admin@meusite.com"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-""}

echo "Domínio: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Atualizar nginx.conf com o domínio correto
echo "### Atualizando configuração do nginx..."
sed -i "s/server_name localhost;/server_name $DOMAIN;/g" nginx.conf
sed -i "s/localhost/$DOMAIN/g" nginx.conf

# Criar diretórios necessários
mkdir -p certbot/conf
mkdir -p certbot/www

# Parar containers se estiverem rodando
echo "### Parando containers..."
docker-compose down

# Gerar certificado dummy primeiro
echo "### Gerando certificado temporário..."
docker-compose run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:4096 -days 1 \
    -keyout '/etc/letsencrypt/live/$DOMAIN/privkey.pem' \
    -out '/etc/letsencrypt/live/$DOMAIN/fullchain.pem' \
    -subj '/CN=$DOMAIN'" certbot

# Iniciar nginx
echo "### Iniciando nginx..."
docker-compose up -d nginx

# Aguardar nginx inicializar
sleep 10

# Obter certificado real
echo "### Obtendo certificado Let's Encrypt..."
docker-compose run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$DOMAIN && \
  rm -Rf /etc/letsencrypt/archive/$DOMAIN && \
  rm -Rf /etc/letsencrypt/renewal/$DOMAIN.conf" certbot

if [ -z "$EMAIL" ]; then
    EMAIL_ARG="--register-unsafely-without-email"
else
    EMAIL_ARG="--email $EMAIL"
fi

docker-compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $EMAIL_ARG \
    -d $DOMAIN \
    --rsa-key-size 4096 \
    --agree-tos \
    --force-renewal" certbot

# Recarregar nginx
echo "### Recarregando nginx..."
docker-compose exec nginx nginx -s reload

# Iniciar todos os serviços
echo "### Iniciando todos os serviços..."
docker-compose up -d

echo ""
echo "=== HTTPS configurado com sucesso! ==="
echo "Acesse: https://$DOMAIN"
echo ""
echo "Para renovar certificados: ./scripts/renew-ssl.sh"
