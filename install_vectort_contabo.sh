#!/bin/bash
# VECTORT.IO - Installation automatique complète sur Contabo
# Exécutez ce script via VNC en une seule ligne :
# curl -fsSL https://raw.githubusercontent.com/[URL]/install.sh | bash

set -e

echo "🚀 VECTORT.IO - INSTALLATION AUTOMATIQUE COMPLÈTE"
echo "=================================================="
echo ""
echo "Serveur : 156.67.26.106"
echo "Domaine : vectort.io"
echo ""

# Mise à jour du système
echo "📦 Mise à jour du système Ubuntu..."
apt-get update -qq
apt-get upgrade -y -qq

# Installation Docker
echo "🐳 Installation de Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
fi

# Installation Docker Compose
echo "📦 Installation de Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Installation Nginx
echo "🌐 Installation de Nginx..."
apt-get install -y nginx

# Installation Certbot pour SSL
echo "🔒 Installation de Certbot (SSL)..."
apt-get install -y certbot python3-certbot-nginx

# Configuration du Firewall
echo "🛡️ Configuration du Firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

# Création des répertoires
echo "📁 Création des répertoires..."
mkdir -p /opt/vectort/{backend,frontend,mongodb}

# Création du docker-compose.yml
echo "📝 Création de docker-compose.yml..."
cat > /opt/vectort/docker-compose.yml << 'EOFDC'
version: '3.8'
services:
  mongodb:
    image: mongo:7.0
    container_name: vectort_mongodb
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: vectort_admin
      MONGO_INITDB_ROOT_PASSWORD: VectorT_Mongo_2024_Secure!
    volumes:
      - /opt/vectort/mongodb:/data/db
    ports:
      - "127.0.0.1:27017:27017"
    networks:
      - vectort_network

  backend:
    image: python:3.11-slim
    container_name: vectort_backend
    restart: always
    working_dir: /app
    command: bash -c "pip install -q fastapi uvicorn motor pymongo pydantic pydantic[email] python-jose[cryptography] passlib[bcrypt] python-multipart httpx PyGithub sendgrid boto3 slack-sdk gspread pyairtable emergentintegrations stripe --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ && uvicorn server:app --host 0.0.0.0 --port 8001"
    environment:
      - MONGO_URL=mongodb://vectort_admin:VectorT_Mongo_2024_Secure!@mongodb:27017/vectort_db?authSource=admin
      - DB_NAME=vectort_db
      - JWT_SECRET=vectort_production_jwt_secret_2024_change_this
      - EMERGENT_LLM_KEY=sk-emergent-0BdC61e9dFeDeE158A
      - STRIPE_API_KEY=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
      - FERNET_ENCRYPTION_KEY=lJMgd5mpNTXd84mpR24Y6rcKzW0d9m0U9PYzMKYcpos=
      - GITHUB_CLIENT_ID=Ov23ligmMVtGwRrhXpy7
      - GITHUB_CLIENT_SECRET=6cff9a375d33aced5db087ea06bbfb4045a7f402
      - GITHUB_REDIRECT_URI=https://vectort.io/auth/github/callback
      - SENDGRID_API_KEY=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
      - SENDGRID_FROM_EMAIL=noreply@vectort.io
    volumes:
      - /opt/vectort/backend:/app
    ports:
      - "127.0.0.1:8001:8001"
    depends_on:
      - mongodb
    networks:
      - vectort_network

  frontend:
    image: node:18-alpine
    container_name: vectort_frontend
    restart: always
    working_dir: /app
    command: sh -c "yarn install && yarn build && npx serve -s build -l 3000"
    environment:
      - REACT_APP_BACKEND_URL=https://api.vectort.io
    volumes:
      - /opt/vectort/frontend:/app
    ports:
      - "127.0.0.1:3000:3000"
    networks:
      - vectort_network

networks:
  vectort_network:
    driver: bridge
EOFDC

# Configuration Nginx
echo "⚙️ Configuration de Nginx..."
cat > /etc/nginx/sites-available/vectort.io << 'EOFNGINX'
server {
    listen 80;
    listen [::]:80;
    server_name vectort.io www.vectort.io api.vectort.io;
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name vectort.io www.vectort.io;
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl http2;
    server_name api.vectort.io;
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }
}
EOFNGINX

ln -sf /etc/nginx/sites-available/vectort.io /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo ""
echo "✅ Installation terminée !"
echo ""
echo "📋 PROCHAINES ÉTAPES MANUELLES :"
echo ""
echo "1. Configurez le DNS sur LWS.fr (URGENT) :"
echo "   - Allez sur : https://www.lws.fr/manager/"
echo "   - Login : amoa.j.aymar@gmail.com / @@aaEE7610"
echo "   - Domaines → vectort.io → Zone DNS"
echo "   - Ajoutez : A | @ | 156.67.26.106"
echo "   - Ajoutez : A | www | 156.67.26.106"
echo "   - Ajoutez : A | api | 156.67.26.106"
echo ""
echo "2. Une fois le DNS propagé (testez : ping vectort.io) :"
echo "   - Obtenez SSL : certbot --nginx -d vectort.io -d www.vectort.io -d api.vectort.io"
echo ""
echo "3. Copiez votre code backend et frontend vers /opt/vectort/"
echo ""
echo "4. Démarrez les containers : cd /opt/vectort && docker-compose up -d"
echo ""
echo "=================================================="
