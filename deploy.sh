#!/bin/bash
set -e

echo "Running Docker Compose deployment..."

sudo docker compose build
sudo docker compose down
sudo docker compose up -d

echo "Deployment finished!"
