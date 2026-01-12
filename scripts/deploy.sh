#!/bin/bash

# Simple deployment script
# This script assumes it is running on the production server

set -e

echo "Starting deployment..."

# 1. Pull latest images
echo "Pulling latest images..."
docker-compose -f docker-compose.prod.yml pull

# 2. Stop existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# 3. Start new containers
echo "Starting new containers..."
docker-compose -f docker-compose.prod.yml up -d

# 4. Run migrations
echo "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

# 5. Health check
echo "Waiting for services to be healthy..."
sleep 10
if curl -f -k https://localhost/health > /dev/null 2>&1; then
    echo "Deployment successful! System is healthy."
else
    echo "Warning: Health check failed. Please check logs."
    docker-compose -f docker-compose.prod.yml logs --tail=50
    exit 1
fi
