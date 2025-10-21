#!/bin/bash

# Script de synchronisation rapide Emergent → Contabo
# Usage: ./sync-to-contabo.sh

SERVER="ubuntu@156.67.26.106"
REMOTE_DIR="/opt/vectort"

echo "🔄 Synchronisation vers Contabo..."

# Créer archive
cd /app
tar -czf /tmp/vectort.tar.gz \
    --exclude='node_modules' \
    --exclude='build' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='.venv' \
    --exclude='dist' \
    backend/ frontend/ 2>/dev/null

echo "📦 Archive créée : $(du -h /tmp/vectort.tar.gz | cut -f1)"
echo ""
echo "📤 Pour uploader sur Contabo, exécutez:"
echo ""
echo "  scp /tmp/vectort.tar.gz $SERVER:$REMOTE_DIR/"
echo ""
echo "Puis sur le serveur Contabo:"
echo ""
echo "  ssh $SERVER"
echo "  cd $REMOTE_DIR"
echo "  tar -xzf vectort.tar.gz"
echo "  cd frontend && npm install && npm run build && cd .."
echo "  sudo systemctl restart vectort-backend vectort-frontend"
echo ""
echo "✅ Fichiers prêts dans /tmp/vectort.tar.gz"
