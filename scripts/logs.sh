#!/bin/bash

SERVICE=${1:-""}

if [ -z "$SERVICE" ]; then
    echo "📋 Mostrando logs de todos os serviços..."
    docker-compose logs -f --tail=100
else
    echo "📋 Mostrando logs do serviço: $SERVICE"
    docker-compose logs -f --tail=100 $SERVICE
fi
