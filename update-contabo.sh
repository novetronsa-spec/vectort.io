#!/bin/bash

################################################################################
# SCRIPT DE MISE À JOUR VECTORT.IO - CONTABO
# Met à jour le code sans réinstaller Docker/Nginx/MongoDB
################################################################################

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "   🔄 MISE À JOUR VECTORT.IO SUR CONTABO"
echo "═══════════════════════════════════════════════════════════════"

# Variables
APP_DIR="/opt/vectort"
BACKUP_DIR="/opt/vectort-backup-$(date +%Y%m%d-%H%M%S)"
CURRENT_DIR=$(pwd)

echo "📋 Configuration:"
echo "   Répertoire de l'application: $APP_DIR"
echo "   Répertoire de sauvegarde: $BACKUP_DIR"
echo ""

# Fonction pour vérifier le succès
check_success() {
    if [ $? -eq 0 ]; then
        echo "✅ $1 - Succès"
    else
        echo "❌ $1 - Échec"
        exit 1
    fi
}

# 1. Vérifier que l'application existe
echo "🔍 Étape 1/8: Vérification de l'installation existante..."
if [ ! -d "$APP_DIR" ]; then
    echo "❌ L'application n'existe pas dans $APP_DIR"
    echo "   Veuillez d'abord déployer l'application avec contabo-auto-deploy.sh"
    exit 1
fi
check_success "Vérification de l'installation"

# 2. Créer une sauvegarde complète
echo "💾 Étape 2/8: Création d'une sauvegarde de sécurité..."
mkdir -p $BACKUP_DIR
cp -r $APP_DIR/* $BACKUP_DIR/
check_success "Sauvegarde créée dans $BACKUP_DIR"

# 3. Sauvegarder les fichiers .env
echo "🔑 Étape 3/8: Sauvegarde des configurations..."
cp $APP_DIR/backend/.env $BACKUP_DIR/backend.env.backup 2>/dev/null || echo "   Pas de .env backend à sauvegarder"
cp $APP_DIR/frontend/.env $BACKUP_DIR/frontend.env.backup 2>/dev/null || echo "   Pas de .env frontend à sauvegarder"
check_success "Sauvegarde des configurations"

# 4. Arrêter les services
echo "⏸️  Étape 4/8: Arrêt des services..."
cd $APP_DIR
docker-compose down
check_success "Arrêt des services"

# 5. Mettre à jour le code
echo "📦 Étape 5/8: Mise à jour du code..."
if [ -f "$CURRENT_DIR/vectort-deploy.tar.gz" ]; then
    echo "   Extraction des nouveaux fichiers..."
    cd /tmp
    tar -xzf $CURRENT_DIR/vectort-deploy.tar.gz
    
    # Copier les nouveaux fichiers (sauf .env)
    echo "   Copie du backend..."
    rsync -av --exclude='.env' /tmp/vectort-deploy/backend/ $APP_DIR/backend/
    
    echo "   Copie du frontend..."
    rsync -av --exclude='.env' --exclude='node_modules' /tmp/vectort-deploy/frontend/ $APP_DIR/frontend/
    
    echo "   Copie de docker-compose.yml..."
    cp /tmp/vectort-deploy/docker-compose.yml $APP_DIR/
    
    # Nettoyer
    rm -rf /tmp/vectort-deploy
    
    check_success "Mise à jour du code"
else
    echo "❌ Fichier vectort-deploy.tar.gz non trouvé dans $CURRENT_DIR"
    echo "   Veuillez d'abord transférer le fichier:"
    echo "   scp /tmp/vectort-deploy.tar.gz root@156.67.26.106:/opt/"
    exit 1
fi

# 6. Restaurer les fichiers .env
echo "🔐 Étape 6/8: Restauration des configurations..."
if [ -f "$BACKUP_DIR/backend.env.backup" ]; then
    cp $BACKUP_DIR/backend.env.backup $APP_DIR/backend/.env
    echo "   ✅ Backend .env restauré"
fi

if [ -f "$BACKUP_DIR/frontend.env.backup" ]; then
    cp $BACKUP_DIR/frontend.env.backup $APP_DIR/frontend/.env
    echo "   ✅ Frontend .env restauré"
fi
check_success "Restauration des configurations"

# 7. Reconstruire et redémarrer les services
echo "🚀 Étape 7/8: Redémarrage des services..."
cd $APP_DIR
docker-compose up -d --build
check_success "Redémarrage des services"

# Attendre que les services démarrent
echo "   ⏳ Attente du démarrage des services (30 secondes)..."
sleep 30

# 8. Vérification
echo "✅ Étape 8/8: Vérification de l'état des services..."
echo "   📊 État des conteneurs:"
docker-compose ps

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "   ✅ MISE À JOUR TERMINÉE AVEC SUCCÈS!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🌐 Votre application est accessible à:"
echo "   - Frontend: https://vectort.io"
echo "   - Backend API: https://api.vectort.io"
echo ""
echo "💾 Sauvegarde disponible dans: $BACKUP_DIR"
echo ""
echo "📝 Commandes utiles:"
echo "   - Voir les logs: cd $APP_DIR && docker-compose logs -f"
echo "   - Redémarrer: cd $APP_DIR && docker-compose restart"
echo "   - État: cd $APP_DIR && docker-compose ps"
echo ""
echo "⚠️  En cas de problème, restaurez la sauvegarde:"
echo "   cd $APP_DIR && docker-compose down"
echo "   rm -rf $APP_DIR/*"
echo "   cp -r $BACKUP_DIR/* $APP_DIR/"
echo "   cd $APP_DIR && docker-compose up -d"
echo ""
echo "═══════════════════════════════════════════════════════════════"
