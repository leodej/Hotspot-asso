#!/bin/bash

SERVICE=${1:-""}

if [ -z "$SERVICE" ]; then
    echo "📋 Logs de todos os serviços:"
    echo "============================"
    docker-compose logs -f --tail=50
else
    echo "📋 Logs do serviço: $SERVICE"
    echo "============================"
    docker-compose logs -f --tail=50 $SERVICE
fi
