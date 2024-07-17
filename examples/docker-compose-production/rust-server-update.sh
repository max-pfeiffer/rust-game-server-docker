#!/usr/bin/bash
echo "Changing to script directory..."
cd $(dirname -- "$0")

# Stop and remove containers, networks
echo "Stopping and removing containers, networks..."
docker compose down

# Create and start containers
echo "Creating and starting containers..."
docker compose up -d
