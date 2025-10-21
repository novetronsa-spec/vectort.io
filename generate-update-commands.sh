#!/bin/bash

################################################################################
# GÉNÉRATEUR DE COMMANDES DE MISE À JOUR
# Crée un fichier avec toutes les commandes à exécuter sur Contabo
################################################################################

OUTPUT_FILE="/tmp/commandes-update-contabo.sh"

echo "🔧 Génération des commandes de mise à jour..."

cat > $OUTPUT_FILE << 'EOFMAIN'
#!/bin/bash
################################################################################
# MISE À JOUR AUTOMATIQUE VECTORT.IO
# Script généré automatiquement - À exécuter sur Contabo
################################################################################

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "   🔄 MISE À JOUR VECTORT.IO"
echo "═══════════════════════════════════════════════════════════════"

# Configuration
APP_DIR="/opt/vectort"
BACKUP_DIR="/opt/vectort-backup-$(date +%Y%m%d-%H%M%S)"

# 1. Vérification
echo "🔍 Vérification de l'installation..."
if [ ! -d "$APP_DIR" ]; then
    echo "❌ Application non trouvée dans $APP_DIR"
    exit 1
fi
echo "✅ Application trouvée"

# 2. Sauvegarde
echo "💾 Création de la sauvegarde..."
mkdir -p $BACKUP_DIR
cp -r $APP_DIR/* $BACKUP_DIR/
cp $APP_DIR/backend/.env $BACKUP_DIR/backend.env 2>/dev/null || true
cp $APP_DIR/frontend/.env $BACKUP_DIR/frontend.env 2>/dev/null || true
echo "✅ Sauvegarde créée: $BACKUP_DIR"

# 3. Arrêt des services
echo "⏸️  Arrêt des services..."
cd $APP_DIR
docker-compose down
echo "✅ Services arrêtés"

# 4. Mise à jour du code
echo "📦 Mise à jour du code..."

# Mise à jour backend (exemple)
# Vous pouvez ajouter vos fichiers ici ou les synchroniser depuis un repo

# 5. Restauration des .env
echo "🔐 Restauration des configurations..."
if [ -f "$BACKUP_DIR/backend.env" ]; then
    cp $BACKUP_DIR/backend.env $APP_DIR/backend/.env
    echo "✅ Backend .env restauré"
fi
if [ -f "$BACKUP_DIR/frontend.env" ]; then
    cp $BACKUP_DIR/frontend.env $APP_DIR/frontend/.env
    echo "✅ Frontend .env restauré"
fi

# 6. Reconstruction et redémarrage
echo "🚀 Reconstruction et redémarrage..."
cd $APP_DIR
docker-compose up -d --build

echo "⏳ Attente du démarrage (30 secondes)..."
sleep 30

# 7. Vérification
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "   ✅ MISE À JOUR TERMINÉE !"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📊 État des services:"
docker-compose ps
echo ""
echo "🌐 Application accessible:"
echo "   - Frontend: https://vectort.io"
echo "   - Backend: https://api.vectort.io/api/"
echo ""
echo "💾 Sauvegarde: $BACKUP_DIR"
echo ""
echo "📝 Pour voir les logs: cd $APP_DIR && docker-compose logs -f"
echo ""
EOFMAIN

chmod +x $OUTPUT_FILE

echo "✅ Fichier créé: $OUTPUT_FILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 INSTRUCTIONS POUR METTRE À JOUR CONTABO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Option 1️⃣ : Copier le script vers Contabo"
echo ""
echo "  scp $OUTPUT_FILE root@156.67.26.106:/tmp/"
echo "  ssh root@156.67.26.106"
echo "  chmod +x /tmp/$(basename $OUTPUT_FILE)"
echo "  sudo /tmp/$(basename $OUTPUT_FILE)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Option 2️⃣ : Commandes directes (copier-coller)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
cat << 'EOFINSTRUCTIONS'
# Connectez-vous à Contabo
ssh root@156.67.26.106

# Puis exécutez ces commandes:

# Sauvegarde
BACKUP_DIR="/opt/vectort-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p $BACKUP_DIR && cp -r /opt/vectort/* $BACKUP_DIR/
echo "✅ Sauvegarde: $BACKUP_DIR"

# Arrêt
cd /opt/vectort && docker-compose down

# Redémarrage avec reconstruction
cd /opt/vectort && docker-compose up -d --build

# Attendre et vérifier
sleep 30 && docker-compose ps

# Voir les logs
docker-compose logs -f

EOFINSTRUCTIONS

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
