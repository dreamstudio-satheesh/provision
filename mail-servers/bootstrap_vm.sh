#!/bin/bash

set -e

echo "🚀 Bootstrapping Debian 12 VM for Mail Provisioning..."

# Ensure sudo is installed
apt-get update && apt-get install -y sudo curl

# Step 1: Install Docker Engine
echo "🔧 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
rm get-docker.sh

# Step 2: Install Docker Compose v2 Plugin
echo "🔧 Installing Docker Compose v2..."
mkdir -p ~/.docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.27.1/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose

# Step 3: Create config directories
echo "📁 Creating required folders..."
sudo mkdir -p /etc/haproxy /etc/caddy

# Step 4: Write docker-compose.yml
echo "📝 Creating docker-compose.yml..."
cat <<EOF > docker-compose.yml
services:
  haproxy:
    image: haproxy:2.9
    container_name: haproxy
    restart: unless-stopped
    ports:
      - "25:25"
      - "587:587"
      - "143:143"
      - "993:993"
      - "110:110"
    volumes:
      - /etc/haproxy:/usr/local/etc/haproxy
    networks:
      - mail_net

  caddy:
    image: caddy:latest
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /etc/caddy:/etc/caddy
      - caddy_data:/data
      - caddy_config:/config
    networks:
      - mail_net

networks:
  mail_net:
    driver: bridge

volumes:
  caddy_data:
  caddy_config:
EOF

# Step 5: Start services
echo "🚀 Starting Docker services..."
docker compose up -d

docker network create mail_net

echo "✅ VM is ready! HAProxy + Caddy are running."
docker ps
