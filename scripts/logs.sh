#!/bin/bash

SERVICE=${1:-app}

echo "📋 Logs do serviço: $SERVICE"
echo "================================"

case $SERVICE in
    "app"|"application")
        docker-compose logs -f app
        ;;
    "db"|"database"|"postgres")
        docker-compose logs -f postgres
        ;;
    "redis")
        docker-compose logs -f redis
        ;;
    "nginx")
        docker-compose logs -f nginx
        ;;
    "prometheus")
        docker-compose logs -f prometheus
        ;;
    "grafana")
        docker-compose logs -f grafana
        ;;
    "all")
        docker-compose logs -f
        ;;
    *)
        echo "Serviços disponíveis:"
        echo "  app, db, redis, nginx, prometheus, grafana, all"
        echo ""
        echo "Uso: ./scripts/logs.sh [serviço]"
        echo "Exemplo: ./scripts/logs.sh app"
        ;;
esac
