#!/bin/bash
# Script to start FireFeed database and Redis containers
# This script sets up the necessary environment for Podman

set -e

echo "🚀 Starting FireFeed Database Setup..."

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Create local config directory if it doesn't exist
mkdir -p "$HOME/.config/containers"

# Copy local registries.conf to user config if it doesn't exist or is outdated
if [ ! -f "$HOME/.config/containers/registries.conf" ] || [ "$PROJECT_ROOT/.config/containers/registries.conf" -nt "$HOME/.config/containers/registries.conf" ]; then
    echo "📋 Updating registries.conf for Podman..."
    cp "$PROJECT_ROOT/.config/containers/registries.conf" "$HOME/.config/containers/registries.conf"
    echo "✅ registries.conf updated"
fi

# Start database and Redis containers
echo "🔧 Starting PostgreSQL and Redis containers..."
podman-compose up -d db redis

echo ""
echo "⏳ Waiting for database to be ready..."

# Wait for PostgreSQL to be ready
timeout=60
count=0
while [ $count -lt $timeout ]; do
    if podman-compose exec -T db pg_isready -U "${DB_USER:-firefeed_user}" -d "${DB_NAME:-firefeed}" >/dev/null 2>&1; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    count=$((count + 1))
    sleep 1
    if [ $((count % 5)) -eq 0 ]; then
        echo "   Still waiting... ($count seconds)"
    fi
done

if [ $count -eq $timeout ]; then
    echo "⚠️  Timeout waiting for PostgreSQL"
    exit 1
fi

echo ""
echo "🎉 Database setup complete!"
echo ""
echo "Container status:"
podman-compose ps
echo ""
echo "📊 Database connection:"
echo "   Host: localhost"
echo "   Port: ${DB_PORT:-5432}"
echo "   Database: ${DB_NAME:-firefeed}"
echo "   User: ${DB_USER:-firefeed_user}"
