#!/bin/bash

# 🚀 VECTORT.IO - SCRIPT DE DÉPLOIEMENT RAPIDE CONTABO
# Ce script doit être exécuté SUR VOTRE SERVEUR CONTABO (via SSH)

set -e  # Arrêter en cas d'erreur

echo "=========================================="
echo "🚀 VECTORT.IO DEPLOYMENT - CONTABO"
echo "=========================================="
echo ""

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
SERVER_IP="156.67.26.106"
DOMAIN="vectort.io"
PROJECT_DIR="/opt/vectort"

echo -e "${YELLOW}⏳ Étape 1/10: Mise à jour du système...${NC}"
apt-get update && apt-get upgrade -y

echo -e "${GREEN}✅ Système mis à jour${NC}"
echo ""

echo -e "${YELLOW}⏳ Étape 2/10: Installation de Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}✅ Docker installé${NC}"
else
    echo -e "${GREEN}✅ Docker déjà installé${NC}"
fi
docker --version
echo ""

echo -e "${YELLOW}⏳ Étape 3/10: Installation de Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installé${NC}"
else
    echo -e "${GREEN}✅ Docker Compose déjà installé${NC}"
fi
docker-compose --version
echo ""

echo -e "${YELLOW}⏳ Étape 4/10: Installation des outils (Git, Nginx, Certbot)...${NC}"
apt-get install -y git nginx certbot python3-certbot-nginx ufw
echo -e "${GREEN}✅ Outils installés${NC}"
echo ""

echo -e "${YELLOW}⏳ Étape 5/10: Configuration du pare-feu...${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 27017/tcp
ufw --force enable
ufw status
echo -e "${GREEN}✅ Pare-feu configuré${NC}"
echo ""

echo -e "${YELLOW}⏳ Étape 6/10: Création de la structure du projet...${NC}"
mkdir -p $PROJECT_DIR
mkdir -p $PROJECT_DIR/backend
mkdir -p $PROJECT_DIR/frontend
mkdir -p $PROJECT_DIR/mongodb_data
mkdir -p $PROJECT_DIR/nginx
echo -e "${GREEN}✅ Structure créée${NC}"
echo ""

echo -e "${YELLOW}⏳ Étape 7/10: Création du fichier docker-compose.yml...${NC}"
cat > $PROJECT_DIR/docker-compose.yml << 'EOFCOMPOSE'
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: vectort_mongodb
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: vectort_secure_mongo_2024_aE761027
      MONGO_INITDB_DATABASE: vectort_db
    volumes:
      - ./mongodb_data:/data/db
    ports:
      - "27017:27017"
    networks:
      - vectort_network

  backend:
    image: python:3.11-slim
    container_name: vectort_backend
    restart: always
    working_dir: /app
    command: >
      bash -c "pip install --no-cache-dir -r requirements.txt &&
               uvicorn server:app --host 0.0.0.0 --port 8001 --workers 2"
    environment:
      - MONGO_URL=mongodb://admin:vectort_secure_mongo_2024_aE761027@mongodb:27017/vectort_db?authSource=admin
      - JWT_SECRET=vectort-production-secret-key-2024-change-this-immediately
      - EMERGENT_LLM_KEY=sk-emergent-0BdC61e9dFeDeE158A
      - STRIPE_API_KEY=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
      - STRIPE_PUBLIC_KEY=pk_live_51RhCsUCR2DPbP3GFuMoYRIH7hCmAMesFjCLB1MguDt6hJd5kDCUmJFmQP32OSq7TTyWADGUyLOHsC40exkUv0MJQ00eZFaSV6p
      - FERNET_ENCRYPTION_KEY=lJMgd5mpNTXd84mpR24Y6rcKzW0d9m0U9PYzMKYcpos=
      - GITHUB_CLIENT_ID=Ov23ligmMVtGwRrhXpy7
      - GITHUB_CLIENT_SECRET=6cff9a375d33aced5db087ea06bbfb4045a7f402
      - SENDGRID_API_KEY=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
      - SENDGRID_FROM_EMAIL=noreply@vectort.io
      - AIRTABLE_API_KEY=patomrj4RqNkMG99a.5077f097e6eda9edbb62b7bc2985862ebf3266b8b086e9c41cffb3dfbe041e5e
      - GOOGLE_CLIENT_ID=759037421779-j9p842itbsjjtdus6g56camr4mi1hupr.apps.googleusercontent.com
      - GOOGLE_CLIENT_SECRET=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
    volumes:
      - ./backend:/app
    ports:
      - "8001:8001"
    depends_on:
      - mongodb
    networks:
      - vectort_network

  frontend:
    image: node:20-alpine
    container_name: vectort_frontend
    restart: always
    working_dir: /app
    command: >
      sh -c "yarn install --frozen-lockfile &&
             yarn build &&
             npx serve -s build -l 3000"
    environment:
      - REACT_APP_BACKEND_URL=https://api.vectort.io
      - NODE_ENV=production
    volumes:
      - ./frontend:/app
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - vectort_network

networks:
  vectort_network:
    driver: bridge
EOFCOMPOSE

echo -e "${GREEN}✅ docker-compose.yml créé${NC}"
echo ""

echo -e "${YELLOW}⏳ Étape 8/10: Configuration Nginx...${NC}"
cat > /etc/nginx/sites-available/vectort.io << 'EOFNGINX'
# Redirection HTTP vers HTTPS pour le domaine principal
server {
    listen 80;
    listen [::]:80;
    server_name vectort.io www.vectort.io;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://vectort.io$request_uri;
    }
}

# Configuration HTTPS pour le domaine principal (Frontend)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name vectort.io www.vectort.io;

    ssl_certificate /etc/letsencrypt/live/vectort.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vectort.io/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;

    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    access_log /var/log/nginx/vectort_access.log;
    error_log /var/log/nginx/vectort_error.log;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /ws {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}

# Redirection HTTP vers HTTPS pour l'API
server {
    listen 80;
    listen [::]:80;
    server_name api.vectort.io;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://api.vectort.io$request_uri;
    }
}

# Configuration HTTPS pour l'API (Backend)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.vectort.io;

    ssl_certificate /etc/letsencrypt/live/vectort.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vectort.io/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;

    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    access_log /var/log/nginx/vectort_api_access.log;
    error_log /var/log/nginx/vectort_api_error.log;

    location / {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        client_max_body_size 50M;
    }
}
EOFNGINX

ln -sf /etc/nginx/sites-available/vectort.io /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
echo -e "${GREEN}✅ Nginx configuré${NC}"
echo ""

echo -e "${RED}=========================================="
echo "⚠️  ACTIONS MANUELLES REQUISES"
echo "==========================================${NC}"
echo ""
echo -e "${YELLOW}1. Transférer le code source:${NC}"
echo "   Sur votre MacBook, exécutez:"
echo "   scp -r /chemin/vers/backend root@156.67.26.106:/opt/vectort/"
echo "   scp -r /chemin/vers/frontend root@156.67.26.106:/opt/vectort/"
echo ""
echo -e "${YELLOW}2. Obtenir les certificats SSL:${NC}"
echo "   systemctl stop nginx"
echo "   mkdir -p /var/www/certbot"
echo "   certbot certonly --standalone -d vectort.io -d www.vectort.io -d api.vectort.io --email votre-email@example.com --agree-tos --no-eff-email"
echo "   systemctl start nginx"
echo ""
echo -e "${YELLOW}3. Démarrer les services:${NC}"
echo "   cd /opt/vectort"
echo "   docker-compose up -d"
echo ""
echo -e "${YELLOW}4. Vérifier les logs:${NC}"
echo "   docker-compose logs -f"
echo ""
echo -e "${GREEN}=========================================="
echo "✅ Configuration initiale terminée!"
echo "==========================================${NC}"
