#!/bin/bash

# Test build of the production stack locally
# Usage: ./scripts/test-prod-build.sh

set -e

echo "Building production stack..."
docker-compose -f docker-compose.prod.yml build

echo "Starting production stack..."
docker-compose -f docker-compose.prod.yml up -d postgres backend frontend prometheus grafana

echo "Waiting for services..."
sleep 15

echo "Checking backend health..."
if curl -f http://localhost:8000/health; then
    echo "Backend is healthy."
else
    echo "Backend health check failed."
    docker-compose -f docker-compose.prod.yml logs backend
    exit 1
fi

echo "Checking frontend..."
if curl -f -I http://localhost:80; then
    echo "Frontend is reachable."
else
    echo "Frontend check failed."
    exit 1
fi

echo "Checking Prometheus..."
if curl -f -I http://localhost:9090; then
    echo "Prometheus is reachable."
else
    echo "Prometheus check failed."
    exit 1
fi

echo "Test successful. Tearing down..."
docker-compose -f docker-compose.prod.yml down
