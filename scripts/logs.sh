#!/bin/bash

# Mostrar logs de todos os serviços
if [ -z "$1" ]; then
    echo "📝 Logs de todos os serviços:"
    docker-compose logs -f
else
    echo "📝 Logs do serviço: $1"
    docker-compose logs -f $1
fi
