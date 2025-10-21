#!/bin/bash

################################################################################
# SCRIPT DE DÉPLOIEMENT AUTOMATIQUE VECTORT.IO - CONTABO
# Ce script installe et configure TOUT automatiquement
################################################################################

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "   🚀 DÉPLOIEMENT AUTOMATIQUE VECTORT.IO SUR CONTABO"
echo "═══════════════════════════════════════════════════════════════"

# Variables de configuration
DOMAIN="vectort.io"
API_DOMAIN="api.vectort.io"
EMAIL="josephayingono@gmail.com"
APP_DIR="/opt/vectort"
CURRENT_USER=$(whoami)

echo "📋 Configuration:"
echo "   Domaine principal: $DOMAIN"
echo "   API Domain: $API_DOMAIN"
echo "   Répertoire d'installation: $APP_DIR"
echo "   Utilisateur: $CURRENT_USER"
echo ""

# Fonction pour vérifier le succès des commandes
check_success() {
    if [ $? -eq 0 ]; then
        echo "✅ $1 - Succès"
    else
        echo "❌ $1 - Échec"
        exit 1
    fi
}

# 1. Mise à jour du système
echo "📦 Étape 1/10: Mise à jour du système..."
apt-get update -qq
apt-get upgrade -y -qq
check_success "Mise à jour système"

# 2. Installation de Docker
echo "🐳 Étape 2/10: Installation de Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    check_success "Installation Docker"
else
    echo "   Docker déjà installé"
fi

# 3. Installation de Docker Compose
echo "🔧 Étape 3/10: Installation de Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    check_success "Installation Docker Compose"
else
    echo "   Docker Compose déjà installé"
fi

# 4. Installation de Nginx
echo "🌐 Étape 4/10: Installation de Nginx..."
if ! command -v nginx &> /dev/null; then
    apt-get install -y nginx
    systemctl enable nginx
    check_success "Installation Nginx"
else
    echo "   Nginx déjà installé"
fi

# 5. Installation de Certbot
echo "🔒 Étape 5/10: Installation de Certbot..."
if ! command -v certbot &> /dev/null; then
    apt-get install -y certbot python3-certbot-nginx
    check_success "Installation Certbot"
else
    echo "   Certbot déjà installé"
fi

# 6. Création du répertoire d'application
echo "📁 Étape 6/10: Préparation du répertoire d'application..."
mkdir -p $APP_DIR
cd $APP_DIR

# Si le fichier tar.gz existe, le décompresser
if [ -f "vectort-deploy.tar.gz" ]; then
    echo "   Extraction de vectort-deploy.tar.gz..."
    tar -xzf vectort-deploy.tar.gz
    check_success "Extraction des fichiers"
else
    echo "   ⚠️  Fichier vectort-deploy.tar.gz non trouvé"
    echo "   Veuillez d'abord transférer le fichier avec prepare-deploy-package.sh"
    exit 1
fi

# 7. Configuration de Nginx
echo "⚙️  Étape 7/10: Configuration de Nginx..."
cat > /etc/nginx/sites-available/vectort.io <<'EOF'
server {
    listen 80;
    server_name vectort.io www.vectort.io;

    # Frontend
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

server {
    listen 80;
    server_name api.vectort.io;

    # Backend API
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
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Origin, X-Requested-With, Content-Type, Accept, Authorization' always;
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
}
EOF

# Activer la configuration
ln -sf /etc/nginx/sites-available/vectort.io /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
check_success "Configuration Nginx"
systemctl restart nginx

# 8. Configuration du fichier .env backend
echo "🔑 Étape 8/10: Configuration des variables d'environnement..."
if [ ! -f "$APP_DIR/backend/.env" ]; then
    cat > $APP_DIR/backend/.env <<EOF
MONGO_URL=mongodb://mongodb:27017/vectort_db
JWT_SECRET=$(openssl rand -hex 32)
FERNET_ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
EMERGENT_LLM_KEY=your_emergent_llm_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDGRID_FROM_EMAIL=noreply@vectort.io
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
AIRTABLE_API_KEY=your_airtable_api_key_here
AIRTABLE_BASE_ID=your_airtable_base_id_here
EOF
    check_success "Création fichier .env backend"
    echo "   ⚠️  N'oubliez pas d'ajouter vos vraies clés API dans $APP_DIR/backend/.env"
fi

# 9. Configuration du fichier .env frontend
if [ ! -f "$APP_DIR/frontend/.env" ]; then
    cat > $APP_DIR/frontend/.env <<EOF
REACT_APP_BACKEND_URL=https://api.vectort.io
WDS_SOCKET_PORT=0
EOF
    check_success "Création fichier .env frontend"
fi

# 10. Démarrage de l'application avec Docker Compose
echo "🚀 Étape 9/10: Démarrage de l'application..."
cd $APP_DIR
docker-compose down 2>/dev/null || true
docker-compose up -d --build
check_success "Démarrage des conteneurs Docker"

# Attendre que les services démarrent
echo "   ⏳ Attente du démarrage des services (30 secondes)..."
sleep 30

# Vérifier l'état des conteneurs
echo "   📊 État des conteneurs:"
docker-compose ps

# 11. Configuration SSL avec Certbot
echo "🔒 Étape 10/10: Configuration des certificats SSL..."
echo "   ⚠️  Avant de continuer, assurez-vous que:"
echo "      - vectort.io pointe vers 156.67.26.106"
echo "      - api.vectort.io pointe vers 156.67.26.106"
echo ""
read -p "Les DNS sont-ils configurés ? (o/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Oo]$ ]]; then
    certbot --nginx -d vectort.io -d www.vectort.io -d api.vectort.io --non-interactive --agree-tos --email $EMAIL --redirect
    check_success "Configuration SSL"
    
    # Configuration du renouvellement automatique
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
    check_success "Configuration renouvellement auto SSL"
else
    echo "   ⚠️  SSL non configuré. Exécutez manuellement:"
    echo "      certbot --nginx -d vectort.io -d www.vectort.io -d api.vectort.io"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "   ✅ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🌐 Votre application est accessible à:"
echo "   - Frontend: https://vectort.io"
echo "   - Backend API: https://api.vectort.io"
echo ""
echo "📝 Prochaines étapes:"
echo "   1. Configurez vos clés API dans: $APP_DIR/backend/.env"
echo "   2. Redémarrez les services: cd $APP_DIR && docker-compose restart"
echo "   3. Vérifiez les logs: docker-compose logs -f"
echo ""
echo "💡 Commandes utiles:"
echo "   - Voir les logs: cd $APP_DIR && docker-compose logs -f"
echo "   - Redémarrer: cd $APP_DIR && docker-compose restart"
echo "   - Arrêter: cd $APP_DIR && docker-compose down"
echo "   - État: cd $APP_DIR && docker-compose ps"
echo ""
echo "═══════════════════════════════════════════════════════════════"
