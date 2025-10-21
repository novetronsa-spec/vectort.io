#!/bin/bash

################################################################################
# SCRIPT DE MISE À JOUR VECTORT.IO - VERSION DIRECTE
# À exécuter directement sur le serveur Contabo
# Pas besoin de transférer de fichiers !
################################################################################

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "   🔄 MISE À JOUR DIRECTE VECTORT.IO"
echo "═══════════════════════════════════════════════════════════════"

# Variables
APP_DIR="/opt/vectort"
BACKUP_DIR="/opt/vectort-backup-$(date +%Y%m%d-%H%M%S)"

# Vérifier que l'app existe
if [ ! -d "$APP_DIR" ]; then
    echo "❌ Application non trouvée dans $APP_DIR"
    exit 1
fi

echo "📋 Configuration:"
echo "   Application: $APP_DIR"
echo "   Sauvegarde: $BACKUP_DIR"
echo ""

# 1. Sauvegarde
echo "💾 Étape 1/6: Création de la sauvegarde..."
mkdir -p $BACKUP_DIR
cp -r $APP_DIR/* $BACKUP_DIR/
echo "   ✅ Sauvegarde créée"

# 2. Sauvegarder les .env
echo "🔐 Étape 2/6: Sauvegarde des configurations..."
cp $APP_DIR/backend/.env $BACKUP_DIR/backend.env 2>/dev/null || true
cp $APP_DIR/frontend/.env $BACKUP_DIR/frontend.env 2>/dev/null || true
echo "   ✅ Configurations sauvegardées"

# 3. Arrêter les services
echo "⏸️  Étape 3/6: Arrêt des services..."
cd $APP_DIR
docker-compose down
echo "   ✅ Services arrêtés"

# 4. Télécharger le nouveau code depuis Emergent
echo "📥 Étape 4/6: Téléchargement du nouveau code..."

# Créer un répertoire temporaire
TEMP_DIR="/tmp/vectort-update-$(date +%s)"
mkdir -p $TEMP_DIR

# Note: Cette partie dépend de comment le code est partagé
# Pour l'instant, on va demander à l'utilisateur de le faire manuellement
echo "   ⚠️  Étape manuelle requise:"
echo "   Le code doit être mis à jour manuellement pour cette version"
echo ""
read -p "   Avez-vous mis à jour les fichiers backend/ et frontend/ ? (o/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Oo]$ ]]; then
    echo "❌ Mise à jour annulée"
    echo "   Pour restaurer: cp -r $BACKUP_DIR/* $APP_DIR/"
    exit 1
fi

# 5. Restaurer les .env
echo "🔓 Étape 5/6: Restauration des configurations..."
if [ -f "$BACKUP_DIR/backend.env" ]; then
    cp $BACKUP_DIR/backend.env $APP_DIR/backend/.env
    echo "   ✅ Backend .env restauré"
fi
if [ -f "$BACKUP_DIR/frontend.env" ]; then
    cp $BACKUP_DIR/frontend.env $APP_DIR/frontend/.env
    echo "   ✅ Frontend .env restauré"
fi

# 6. Redémarrer
echo "🚀 Étape 6/6: Redémarrage des services..."
cd $APP_DIR
docker-compose up -d --build
echo "   ⏳ Attente du démarrage (30s)..."
sleep 30

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "   ✅ MISE À JOUR TERMINÉE !"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📊 État des services:"
docker-compose ps
echo ""
echo "🌐 Application accessible sur:"
echo "   - Frontend: https://vectort.io"
echo "   - Backend: https://api.vectort.io"
echo ""
echo "💾 Sauvegarde: $BACKUP_DIR"
echo ""
