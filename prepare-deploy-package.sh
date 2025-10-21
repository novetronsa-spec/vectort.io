#!/bin/bash

################################################################################
# SCRIPT DE PRÉPARATION DU PACKAGE DE DÉPLOIEMENT
# Ce script crée un package complet prêt pour Contabo
################################################################################

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "   📦 PRÉPARATION DU PACKAGE DE DÉPLOIEMENT VECTORT.IO"
echo "═══════════════════════════════════════════════════════════════"

# Variables
PACKAGE_NAME="vectort-deploy"
PACKAGE_DIR="/tmp/$PACKAGE_NAME"
TARBALL="$PACKAGE_NAME.tar.gz"
CONTABO_IP="156.67.26.106"
CONTABO_USER="root"

echo "📋 Configuration:"
echo "   Package: $PACKAGE_NAME"
echo "   Destination: $CONTABO_IP"
echo ""

# 1. Nettoyage du répertoire temporaire
echo "🧹 Étape 1/5: Nettoyage des fichiers temporaires..."
rm -rf $PACKAGE_DIR
mkdir -p $PACKAGE_DIR
echo "   ✅ Répertoire temporaire créé"

# 2. Copie des fichiers essentiels
echo "📂 Étape 2/5: Copie des fichiers de l'application..."

# Structure de répertoires
mkdir -p $PACKAGE_DIR/backend
mkdir -p $PACKAGE_DIR/frontend
mkdir -p $PACKAGE_DIR/nginx

# Backend
echo "   - Copie du backend..."
cp -r /app/backend/* $PACKAGE_DIR/backend/ 2>/dev/null || true
rm -f $PACKAGE_DIR/backend/.env  # Ne pas inclure le .env local

# Frontend
echo "   - Copie du frontend..."
cp -r /app/frontend/* $PACKAGE_DIR/frontend/ 2>/dev/null || true
rm -f $PACKAGE_DIR/frontend/.env  # Ne pas inclure le .env local
rm -rf $PACKAGE_DIR/frontend/node_modules  # Exclure node_modules
rm -rf $PACKAGE_DIR/frontend/build  # Exclure build

# Docker files
echo "   - Copie des fichiers Docker..."
cp /app/docker-compose.yml $PACKAGE_DIR/ 2>/dev/null || true

# Scripts de déploiement
echo "   - Copie des scripts de déploiement..."
cp /app/contabo-auto-deploy.sh $PACKAGE_DIR/
cp /app/DEPLOY_INSTRUCTIONS_FR.md $PACKAGE_DIR/

echo "   ✅ Fichiers copiés"

# 3. Création du fichier docker-compose.yml optimisé
echo "⚙️  Étape 3/5: Création de la configuration Docker..."
cat > $PACKAGE_DIR/docker-compose.yml <<'EOF'
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: vectort-mongodb
    restart: always
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_DATABASE=vectort_db
    networks:
      - vectort-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: vectort-backend
    restart: always
    ports:
      - "8001:8001"
    env_file:
      - ./backend/.env
    depends_on:
      - mongodb
    networks:
      - vectort-network
    volumes:
      - ./backend:/app

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: vectort-frontend
    restart: always
    ports:
      - "3000:3000"
    env_file:
      - ./frontend/.env
    depends_on:
      - backend
    networks:
      - vectort-network
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  mongodb_data:

networks:
  vectort-network:
    driver: bridge
EOF
echo "   ✅ docker-compose.yml créé"

# 4. Création des Dockerfiles si nécessaire
echo "🐳 Étape 4/5: Vérification des Dockerfiles..."

# Dockerfile Backend
if [ ! -f "$PACKAGE_DIR/backend/Dockerfile" ]; then
    cat > $PACKAGE_DIR/backend/Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
EOF
    echo "   ✅ Dockerfile backend créé"
fi

# Dockerfile Frontend
if [ ! -f "$PACKAGE_DIR/frontend/Dockerfile" ]; then
    cat > $PACKAGE_DIR/frontend/Dockerfile <<'EOF'
FROM node:18-alpine

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .

EXPOSE 3000

CMD ["yarn", "start"]
EOF
    echo "   ✅ Dockerfile frontend créé"
fi

# 5. Création de l'archive
echo "📦 Étape 5/5: Création de l'archive..."
cd /tmp
tar -czf $TARBALL $PACKAGE_NAME/
echo "   ✅ Archive créée: /tmp/$TARBALL"
echo "   📊 Taille: $(du -h /tmp/$TARBALL | cut -f1)"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "   ✅ PACKAGE PRÊT!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📦 Fichier créé: /tmp/$TARBALL"
echo ""
echo "🚀 PROCHAINES ÉTAPES:"
echo ""
echo "1️⃣  Transférer le fichier vers Contabo:"
echo "   scp /tmp/$TARBALL $CONTAABO_USER@$CONTABO_IP:/opt/"
echo ""
echo "2️⃣  Se connecter au serveur Contabo:"
echo "   ssh $CONTABO_USER@$CONTABO_IP"
echo ""
echo "3️⃣  Décompresser et exécuter le script:"
echo "   cd /opt"
echo "   tar -xzf $TARBALL"
echo "   cd $PACKAGE_NAME"
echo "   chmod +x contabo-auto-deploy.sh"
echo "   sudo ./contabo-auto-deploy.sh"
echo ""
echo "💡 OU copiez les commandes ci-dessous dans votre terminal:"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "# Commandes à copier-coller"
echo "scp /tmp/$TARBALL root@$CONTABO_IP:/opt/"
echo "ssh root@$CONTABO_IP"
echo "cd /opt && tar -xzf $TARBALL && cd $PACKAGE_NAME && chmod +x contabo-auto-deploy.sh && sudo ./contabo-auto-deploy.sh"
echo "═══════════════════════════════════════════════════════════════"
echo ""
