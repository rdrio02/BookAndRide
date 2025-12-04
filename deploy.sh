#!/bin/bash
set -e

echo "Running Docker Compose deployment..."

docker compose build
docker compose down
docker compose up -d

echo "Deployment finished!"
