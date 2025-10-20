# 🚀 VECTORT.IO - INSTRUCTIONS DE DÉPLOIEMENT CONTABO

**IP SERVEUR:** 156.67.26.106  
**DOMAINE:** vectort.io  
**DATE:** Janvier 2025

---

## ✅ PRÉ-REQUIS DNS (À VÉRIFIER SUR LWS.FR)

⚠️ **ACTION CRITIQUE:** Supprimez l'enregistrement DNS en double sur LWS.fr:
- ❌ **SUPPRIMER:** A record `@ → 193.37.145.73` (ancien serveur LWS)
- ✅ **GARDER:** A record `@ → 156.67.26.106` (votre Contabo)
- ✅ **GARDER:** A record `api.vectort.io → 156.67.26.106`
- ✅ **GARDER:** A record `www → 156.67.26.106`

---

## 📋 ÉTAPE 1: CONNEXION SSH (DÉJÀ FAIT ✓)

```bash
# Vous êtes déjà connecté à: root@vmi2855086:~#
# Vérifiez votre connexion:
whoami
# Devrait afficher: root
```

---

## 📋 ÉTAPE 2: INSTALLATION DES DÉPENDANCES

Copiez-collez ces commandes **une par une** dans votre terminal SSH:

### 2.1 - Mise à jour du système
```bash
apt-get update && apt-get upgrade -y
```

### 2.2 - Installation de Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker
docker --version
```

### 2.3 - Installation de Docker Compose
```bash
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### 2.4 - Installation de Git et autres outils
```bash
apt-get install -y git nginx certbot python3-certbot-nginx ufw
```

---

## 📋 ÉTAPE 3: CONFIGURATION DU PARE-FEU

```bash
# Activer le pare-feu
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 27017/tcp
ufw --force enable
ufw status
```

---

## 📋 ÉTAPE 4: CRÉATION DE LA STRUCTURE DU PROJET

```bash
# Créer le dossier principal
mkdir -p /opt/vectort
cd /opt/vectort

# Créer les sous-dossiers
mkdir -p backend frontend mongodb_data nginx
```

---

## 📋 ÉTAPE 5: CRÉATION DES FICHIERS DE CONFIGURATION

### 5.1 - Créer le fichier docker-compose.yml
```bash
cat > /opt/vectort/docker-compose.yml << 'EOF'
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
EOF
```

### 5.2 - Créer la configuration Nginx
```bash
cat > /etc/nginx/sites-available/vectort.io << 'EOF'
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

    # Certificats SSL (à générer avec Certbot)
    ssl_certificate /etc/letsencrypt/live/vectort.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vectort.io/privkey.pem;
    
    # Configuration SSL moderne
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;

    # Headers de sécurité
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logs
    access_log /var/log/nginx/vectort_access.log;
    error_log /var/log/nginx/vectort_error.log;

    # Frontend React
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
        
        # Timeouts pour les applications React
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Configuration WebSocket pour React hot reload (development uniquement)
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

    # Certificats SSL
    ssl_certificate /etc/letsencrypt/live/vectort.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vectort.io/privkey.pem;
    
    # Configuration SSL moderne
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;

    # Headers de sécurité
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Logs
    access_log /var/log/nginx/vectort_api_access.log;
    error_log /var/log/nginx/vectort_api_error.log;

    # Backend FastAPI
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
        
        # Timeouts pour les requêtes API (augmentés pour l'IA)
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Taille maximale des requêtes (pour upload de fichiers)
        client_max_body_size 50M;
    }
}
EOF
```

### 5.3 - Activer le site Nginx
```bash
ln -sf /etc/nginx/sites-available/vectort.io /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
```

---

## 📋 ÉTAPE 6: CLONER LE CODE SOURCE

⚠️ **IMPORTANT:** Vous devez maintenant cloner votre code depuis GitHub ou le transférer via SCP/SFTP.

### Option A: Clone depuis GitHub (SI VOUS AVEZ UN REPO)
```bash
cd /opt/vectort
# Remplacez par votre URL GitHub
git clone https://github.com/votre-compte/vectort.io.git .
```

### Option B: Transfert manuel (SUR VOTRE MACBOOK LOCAL)
```bash
# Sur votre MacBook, depuis le dossier contenant le code:
scp -r /chemin/vers/backend root@156.67.26.106:/opt/vectort/
scp -r /chemin/vers/frontend root@156.67.26.106:/opt/vectort/
```

---

## 📋 ÉTAPE 7: MISE À JOUR DES VARIABLES D'ENVIRONNEMENT

### 7.1 - Backend .env
```bash
cat > /opt/vectort/backend/.env << 'EOF'
# MongoDB
MONGO_URL=mongodb://admin:vectort_secure_mongo_2024_aE761027@mongodb:27017/vectort_db?authSource=admin

# JWT
JWT_SECRET=vectort-production-secret-key-2024-change-this-immediately

# AI
EMERGENT_LLM_KEY=sk-emergent-0BdC61e9dFeDeE158A

# Stripe LIVE
STRIPE_API_KEY=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
STRIPE_PUBLIC_KEY=pk_live_51RhCsUCR2DPbP3GFuMoYRIH7hCmAMesFjCLB1MguDt6hJd5kDCUmJFmQP32OSq7TTyWADGUyLOHsC40exkUv0MJQ00eZFaSV6p

# Encryption
FERNET_ENCRYPTION_KEY=lJMgd5mpNTXd84mpR24Y6rcKzW0d9m0U9PYzMKYcpos=

# GitHub OAuth
GITHUB_CLIENT_ID=Ov23ligmMVtGwRrhXpy7
GITHUB_CLIENT_SECRET=6cff9a375d33aced5db087ea06bbfb4045a7f402

# SendGrid
SENDGRID_API_KEY=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
SENDGRID_FROM_EMAIL=noreply@vectort.io

# Airtable
AIRTABLE_API_KEY=patomrj4RqNkMG99a.5077f097e6eda9edbb62b7bc2985862ebf3266b8b086e9c41cffb3dfbe041e5e
EOF
```

### 7.2 - Frontend .env
```bash
cat > /opt/vectort/frontend/.env << 'EOF'
REACT_APP_BACKEND_URL=https://api.vectort.io
NODE_ENV=production
EOF
```

---

## 📋 ÉTAPE 8: OBTENIR LES CERTIFICATS SSL

```bash
# Arrêter Nginx temporairement
systemctl stop nginx

# Créer le dossier pour Certbot
mkdir -p /var/www/certbot

# Obtenir le certificat SSL
certbot certonly --standalone -d vectort.io -d www.vectort.io -d api.vectort.io --email votre-email@example.com --agree-tos --no-eff-email

# Redémarrer Nginx
systemctl start nginx

# Configurer le renouvellement automatique
systemctl enable certbot.timer
```

---

## 📋 ÉTAPE 9: DÉMARRER LES SERVICES DOCKER

```bash
cd /opt/vectort

# Démarrer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f

# Pour sortir des logs, appuyez sur Ctrl+C
```

---

## 📋 ÉTAPE 10: VÉRIFICATION FINALE

### 10.1 - Vérifier les conteneurs
```bash
docker ps
# Vous devriez voir 3 conteneurs: mongodb, backend, frontend
```

### 10.2 - Vérifier Nginx
```bash
systemctl status nginx
```

### 10.3 - Tester les endpoints
```bash
# Test Backend
curl https://api.vectort.io/api/

# Test Frontend
curl https://vectort.io
```

---

## 📋 COMMANDES UTILES

### Redémarrer les services
```bash
cd /opt/vectort
docker-compose restart
systemctl restart nginx
```

### Voir les logs
```bash
# Backend
docker-compose logs -f backend

# Frontend
docker-compose logs -f frontend

# MongoDB
docker-compose logs -f mongodb

# Nginx
tail -f /var/log/nginx/vectort_error.log
```

### Arrêter les services
```bash
cd /opt/vectort
docker-compose down
```

### Mettre à jour le code
```bash
cd /opt/vectort
git pull  # Si vous utilisez Git
docker-compose restart
```

---

## 🎉 FÉLICITATIONS !

Votre application Vectort.io devrait maintenant être accessible sur:
- **Frontend:** https://vectort.io
- **API Backend:** https://api.vectort.io

## 📞 SUPPORT

Si vous rencontrez des problèmes, vérifiez:
1. Les logs Docker: `docker-compose logs -f`
2. Les logs Nginx: `tail -f /var/log/nginx/vectort_error.log`
3. Le statut des conteneurs: `docker ps -a`
4. La configuration DNS sur LWS.fr
5. Les certificats SSL: `certbot certificates`

---

**Date de création:** Janvier 2025  
**Version:** 1.0  
**Plateforme:** Contabo VPS + Docker + Nginx
