#!/bin/bash

echo "🔄 Renovando certificados SSL..."
echo "================================"

# Verificar se os containers estão rodando
if ! docker-compose ps | grep -q "Up"; then
    echo "⚠️  Containers não estão rodando. Iniciando..."
    docker-compose up -d
    sleep 10
fi

# Renovar certificados
echo "📜 Executando renovação..."
docker-compose run --rm certbot renew --quiet

if [ $? -eq 0 ]; then
    echo "✅ Certificados renovados com sucesso!"
    
    # Recarregar nginx
    echo "🔄 Recarregando nginx..."
    docker-compose exec nginx nginx -s reload
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx recarregado com sucesso!"
    else
        echo "❌ Erro ao recarregar nginx"
        exit 1
    fi
else
    echo "⚠️  Nenhum certificado precisava ser renovado ou erro na renovação"
fi

echo ""
echo "🎉 Processo de renovação concluído!"
echo "📅 Próxima verificação automática em 12 horas"
