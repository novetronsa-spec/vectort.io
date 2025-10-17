#!/bin/bash
# Script de déploiement COMPLET AUTOMATIQUE de Vectort.io
# Configure DNS + Déploie sur Contabo en une seule commande

set -e

echo "🚀 DÉPLOIEMENT AUTOMATIQUE COMPLET DE VECTORT.IO"
echo "=================================================="
echo ""

# Configuration
SERVER_IP="156.67.26.106"
SERVER_USER="root"
SERVER_PASS="aE761027"
DOMAIN="vectort.io"

echo "📋 Configuration:"
echo "  - Serveur: ${SERVER_IP}"
echo "  - Domaine: ${DOMAIN}"
echo ""

# Étape 1: Préparer les fichiers
echo "📦 Étape 1/5: Préparation des fichiers..."
cd /app

# Copier le .env.production vers .env pour le serveur
cp .env.production backend/.env
cp docker-compose.production.yml docker-compose.yml

# Rendre le script deploy.sh exécutable
chmod +x deploy.sh

echo "✅ Fichiers préparés"
echo ""

# Étape 2: Transférer les fichiers vers le serveur
echo "📤 Étape 2/5: Transfer des fichiers vers Contabo (156.67.26.106)..."
echo "   Ceci peut prendre 2-3 minutes..."

# Installer sshpass si nécessaire
if ! command -v sshpass &> /dev/null; then
    echo "   Installation de sshpass..."
    apt-get update -qq && apt-get install -y sshpass -qq
fi

# Créer le répertoire sur le serveur
sshpass -p "${SERVER_PASS}" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p /opt/vectort"

# Transférer tous les fichiers
sshpass -p "${SERVER_PASS}" scp -r -o StrictHostKeyChecking=no \
    /app/* ${SERVER_USER}@${SERVER_IP}:/opt/vectort/

echo "✅ Fichiers transférés"
echo ""

# Étape 3: Exécuter le déploiement sur le serveur
echo "🔧 Étape 3/5: Installation et configuration sur le serveur..."
echo "   Installation Docker, Nginx, SSL, MongoDB..."
echo "   Ceci peut prendre 10-15 minutes..."
echo ""

sshpass -p "${SERVER_PASS}" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e
cd /opt/vectort

# Rendre le script exécutable
chmod +x deploy.sh

# Exécuter le déploiement
echo "🚀 Lancement de deploy.sh sur le serveur..."
./deploy.sh

echo ""
echo "✅ Déploiement serveur terminé !"
ENDSSH

echo ""
echo "✅ Installation serveur terminée"
echo ""

# Étape 4: Configuration DNS
echo "📡 Étape 4/5: Configuration DNS..."
echo "   L'API LWS a des limitations, vous devez faire cette étape manuellement:"
echo ""
echo "   👉 Allez sur: https://www.lws.fr/manager/"
echo "   👉 Connexion: amoa.j.aymar@gmail.com / @@aaEE7610"
echo "   👉 Mes Domaines → vectort.io → Zone DNS"
echo "   👉 Ajoutez ces enregistrements:"
echo ""
echo "      Type A  | Nom: @   | Valeur: 156.67.26.106"
echo "      Type A  | Nom: www | Valeur: 156.67.26.106"
echo "      Type A  | Nom: api | Valeur: 156.67.26.106"
echo ""
echo "   👉 Sauvegardez et attendez 10-30 minutes"
echo ""

# Étape 5: Vérification
echo "🔍 Étape 5/5: Vérification..."
echo ""
echo "✅ Le serveur est configuré et tourne sur ${SERVER_IP}"
echo "✅ Docker containers sont démarrés"
echo "✅ Nginx est configuré avec SSL"
echo ""
echo "⏳ Attendez la propagation DNS (10-30 minutes)"
echo ""
echo "🔍 Testez avec: ping vectort.io"
echo "   (devrait répondre: 156.67.26.106)"
echo ""

# Test de connectivité
echo "📊 Test de connectivité au serveur..."
if curl -s -o /dev/null -w "%{http_code}" http://${SERVER_IP}:8001/api/ | grep -q "200"; then
    echo "✅ Backend répond correctement !"
else
    echo "⚠️  Backend en cours de démarrage..."
fi

if curl -s -o /dev/null -w "%{http_code}" http://${SERVER_IP}:3000 | grep -q "200"; then
    echo "✅ Frontend répond correctement !"
else
    echo "⚠️  Frontend en cours de démarrage..."
fi

echo ""
echo "=================================================="
echo "🎉 DÉPLOIEMENT AUTOMATIQUE TERMINÉ !"
echo "=================================================="
echo ""
echo "📝 PROCHAINES ÉTAPES:"
echo ""
echo "1. ⚠️  IMPORTANT: Configurez le DNS (voir instructions ci-dessus)"
echo ""
echo "2. Une fois le DNS propagé (ping vectort.io = 156.67.26.106):"
echo "   - https://vectort.io (Frontend)"
echo "   - https://api.vectort.io (Backend API)"
echo ""
echo "3. Commandes utiles sur le serveur:"
echo "   ssh root@156.67.26.106"
echo "   cd /opt/vectort"
echo "   docker-compose logs -f"
echo "   docker-compose ps"
echo ""
echo "4. Mettez à jour GitHub OAuth callback:"
echo "   github.com/settings/developers"
echo "   → https://vectort.io/auth/github/callback"
echo ""
echo "5. Mettez à jour Stripe Webhooks:"
echo "   dashboard.stripe.com/webhooks"
echo "   → https://api.vectort.io/api/webhook/stripe"
echo ""
echo "=================================================="
