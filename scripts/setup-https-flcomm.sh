#!/bin/bash

echo "=== Configurando HTTPS para hotspot.flcomm.com.br ==="
echo ""

DOMAIN="hotspot.flcomm.com.br"
EMAIL="admin@flcomm.com.br"

echo "Domínio: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Criar diretórios necessários
echo "### Criando diretórios..."
mkdir -p certbot/conf
mkdir -p certbot/www

# Parar containers se estiverem rodando
echo "### Parando containers..."
docker-compose down

# Gerar certificado dummy primeiro
echo "### Gerando certificado temporário..."
mkdir -p certbot/conf/live/$DOMAIN
docker-compose run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:4096 -days 1 \
    -keyout '/etc/letsencrypt/live/$DOMAIN/privkey.pem' \
    -out '/etc/letsencrypt/live/$DOMAIN/fullchain.pem' \
    -subj '/CN=$DOMAIN'" certbot

# Iniciar nginx
echo "### Iniciando nginx..."
docker-compose up -d nginx

# Aguardar nginx inicializar
echo "### Aguardando nginx inicializar..."
sleep 15

# Verificar se nginx está rodando
if ! docker-compose ps nginx | grep -q "Up"; then
    echo "Erro: Nginx não iniciou corretamente"
    docker-compose logs nginx
    exit 1
fi

# Obter certificado real
echo "### Removendo certificado temporário..."
docker-compose run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$DOMAIN && \
  rm -Rf /etc/letsencrypt/archive/$DOMAIN && \
  rm -Rf /etc/letsencrypt/renewal/$DOMAIN.conf" certbot

echo "### Obtendo certificado Let's Encrypt..."
docker-compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    --email $EMAIL \
    -d $DOMAIN \
    --rsa-key-size 4096 \
    --agree-tos \
    --force-renewal \
    --non-interactive" certbot

if [ $? -eq 0 ]; then
    echo "### Certificado obtido com sucesso!"
    
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
else
    echo "### Erro ao obter certificado!"
    echo "Verifique se:"
    echo "1. O domínio $DOMAIN aponta para este servidor"
    echo "2. As portas 80 e 443 estão abertas"
    echo "3. Não há firewall bloqueando"
    exit 1
fi
