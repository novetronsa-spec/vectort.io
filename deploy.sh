#!/bin/bash
# Vectort.io - Script de déploiement automatique sur Contabo
# Serveur: 156.67.26.106 | OS: Ubuntu 24.04

set -e  # Exit on error

echo "🚀 Déploiement de Vectort.io sur Contabo..."
echo "============================================"

# Variables
DOMAIN="vectort.io"
SERVER_IP="31.165.143.145"
EMAIL="admin@vectort.io"

# Couleurs pour les logs
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}✓ Mise à jour du système...${NC}"
apt-get update
apt-get upgrade -y

echo -e "${GREEN}✓ Installation de Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

echo -e "${GREEN}✓ Installation de Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo -e "${GREEN}✓ Installation de Nginx...${NC}"
apt-get install -y nginx

echo -e "${GREEN}✓ Installation de Certbot pour SSL...${NC}"
apt-get install -y certbot python3-certbot-nginx

echo -e "${GREEN}✓ Configuration du Firewall (UFW)...${NC}"
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable

echo -e "${GREEN}✓ Création des répertoires...${NC}"
mkdir -p /opt/vectort
mkdir -p /opt/vectort/backend
mkdir -p /opt/vectort/frontend
mkdir -p /opt/vectort/mongodb
mkdir -p /opt/vectort/nginx

echo -e "${GREEN}✓ Clonage du code depuis le workspace actuel...${NC}"
# Note: Le code sera copié depuis /app vers /opt/vectort

echo -e "${GREEN}✓ Configuration Nginx...${NC}"
cat > /etc/nginx/sites-available/vectort.io <<'EOF'
# Vectort.io Nginx Configuration

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name vectort.io www.vectort.io api.vectort.io;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# Frontend - vectort.io
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name vectort.io www.vectort.io;
    
    # SSL certificates (will be added by Certbot)
    # ssl_certificate /etc/letsencrypt/live/vectort.io/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/vectort.io/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
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
    }
}

# Backend API - api.vectort.io
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.vectort.io;
    
    # SSL certificates (will be added by Certbot)
    # ssl_certificate /etc/letsencrypt/live/vectort.io/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/vectort.io/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Increase timeout for AI generation
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    
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
    }
}
EOF

ln -sf /etc/nginx/sites-available/vectort.io /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo -e "${GREEN}✓ Test de la configuration Nginx...${NC}"
nginx -t

echo -e "${GREEN}✓ Redémarrage de Nginx...${NC}"
systemctl restart nginx
systemctl enable nginx

echo -e "${GREEN}✓ Obtention des certificats SSL Let's Encrypt...${NC}"
certbot --nginx -d vectort.io -d www.vectort.io -d api.vectort.io --non-interactive --agree-tos --email $EMAIL --redirect

echo -e "${GREEN}✓ Démarrage des conteneurs Docker...${NC}"
cd /opt/vectort
docker-compose up -d

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✓ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "🌐 Votre application est maintenant accessible sur :"
echo "   - https://vectort.io"
echo "   - https://www.vectort.io"
echo "   - https://api.vectort.io (API)"
echo ""
echo "📊 Commandes utiles :"
echo "   - docker-compose logs -f          # Voir les logs"
echo "   - docker-compose restart          # Redémarrer"
echo "   - docker-compose ps               # Voir les conteneurs"
echo "   - systemctl status nginx          # Status Nginx"
echo ""
echo "🔐 Les certificats SSL se renouvellent automatiquement (Let's Encrypt)"
echo ""
