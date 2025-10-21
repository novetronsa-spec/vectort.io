# 🚀 Guide de Déploiement Vectort.io sur Contabo

## 📋 Prérequis

### Informations de connexion Contabo
- **IP du serveur**: 156.67.26.106
- **Utilisateur**: root
- **Mot de passe SSH**: aE761027

### Configuration DNS requise
Avant de commencer, assurez-vous que vos DNS pointent vers votre serveur:

```
vectort.io        A    156.67.26.106
www.vectort.io    A    156.67.26.106
api.vectort.io    A    156.67.26.106
```

## 🎯 Méthode Recommandée: Déploiement Automatique

### Étape 1: Préparation du package

Sur votre machine Emergent, exécutez:

```bash
cd /app
chmod +x prepare-deploy-package.sh
./prepare-deploy-package.sh
```

Ce script va créer un fichier `vectort-deploy.tar.gz` dans `/tmp/`.

### Étape 2: Transfert vers Contabo

Transférez le package vers le serveur Contabo:

```bash
scp /tmp/vectort-deploy.tar.gz root@156.67.26.106:/opt/
```

Quand demandé, entrez le mot de passe: `aE761027`

### Étape 3: Connexion au serveur

Connectez-vous au serveur Contabo:

```bash
ssh root@156.67.26.106
```

Mot de passe: `aE761027`

### Étape 4: Déploiement automatique

Une fois connecté au serveur, exécutez:

```bash
cd /opt
tar -xzf vectort-deploy.tar.gz
cd vectort-deploy
chmod +x contabo-auto-deploy.sh
sudo ./contabo-auto-deploy.sh
```

**Le script va automatiquement:**
1. ✅ Mettre à jour le système
2. ✅ Installer Docker et Docker Compose
3. ✅ Installer et configurer Nginx
4. ✅ Installer Certbot pour SSL
5. ✅ Décompresser les fichiers de l'application
6. ✅ Créer les fichiers de configuration (.env)
7. ✅ Démarrer les conteneurs Docker
8. ✅ Configurer les certificats SSL (si DNS configurés)

### Étape 5: Configuration des clés API

Après le déploiement, vous devez ajouter vos vraies clés API:

```bash
nano /opt/vectort/backend/.env
```

Remplacez les valeurs suivantes:

```env
EMERGENT_LLM_KEY=zvPaiA9UKOXJTFoeHEqCsDSlWw2fR8un6Q3VZYkN75t0hmBbyM
STRIPE_SECRET_KEY=votre_clé_stripe
STRIPE_WEBHOOK_SECRET=votre_webhook_secret
STRIPE_PUBLISHABLE_KEY=votre_clé_publishable
GITHUB_CLIENT_ID=votre_client_id
GITHUB_CLIENT_SECRET=votre_client_secret
SENDGRID_API_KEY=votre_clé_sendgrid
GOOGLE_CLIENT_ID=votre_client_id_google
GOOGLE_CLIENT_SECRET=votre_client_secret_google
AIRTABLE_API_KEY=votre_clé_airtable
AIRTABLE_BASE_ID=votre_base_id
```

Sauvegardez avec `Ctrl+X`, puis `Y`, puis `Enter`.

### Étape 6: Redémarrage des services

Après avoir configuré les clés:

```bash
cd /opt/vectort
docker-compose restart
```

## ✅ Vérification

### Vérifier l'état des conteneurs

```bash
cd /opt/vectort
docker-compose ps
```

Tous les services doivent être "Up":
- vectort-mongodb
- vectort-backend
- vectort-frontend

### Vérifier les logs

```bash
# Tous les logs
docker-compose logs -f

# Backend seulement
docker-compose logs -f backend

# Frontend seulement
docker-compose logs -f frontend
```

### Tester l'accès

1. **Frontend**: https://vectort.io
2. **Backend API**: https://api.vectort.io/api/
3. **Health check**: https://api.vectort.io/api/health

## 🔧 Commandes Utiles

### Gestion des services

```bash
cd /opt/vectort

# Voir l'état
docker-compose ps

# Redémarrer tous les services
docker-compose restart

# Redémarrer un service spécifique
docker-compose restart backend
docker-compose restart frontend

# Arrêter tous les services
docker-compose down

# Démarrer tous les services
docker-compose up -d

# Reconstruire et redémarrer
docker-compose up -d --build
```

### Logs

```bash
# Voir tous les logs en temps réel
docker-compose logs -f

# Voir les dernières 100 lignes
docker-compose logs --tail=100

# Logs d'un service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### Nginx

```bash
# Tester la configuration
nginx -t

# Redémarrer Nginx
systemctl restart nginx

# Voir les logs Nginx
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### SSL/Certbot

```bash
# Renouveler les certificats manuellement
certbot renew

# Tester le renouvellement
certbot renew --dry-run

# Voir les certificats installés
certbot certificates
```

## 🐛 Dépannage

### Problème 1: Les conteneurs ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs

# Reconstruire les images
docker-compose down
docker-compose up -d --build
```

### Problème 2: Backend ne répond pas

```bash
# Vérifier que le backend est accessible
curl http://localhost:8001/api/

# Vérifier les logs
docker-compose logs backend

# Redémarrer le backend
docker-compose restart backend
```

### Problème 3: Frontend affiche une erreur

```bash
# Vérifier la configuration .env
cat /opt/vectort/frontend/.env

# Doit contenir:
# REACT_APP_BACKEND_URL=https://api.vectort.io

# Reconstruire le frontend
docker-compose up -d --build frontend
```

### Problème 4: Certificats SSL ne s'installent pas

```bash
# Vérifier que les DNS pointent bien vers le serveur
dig vectort.io +short
dig api.vectort.io +short

# Les deux doivent retourner: 156.67.26.106

# Réessayer l'installation SSL
certbot --nginx -d vectort.io -d www.vectort.io -d api.vectort.io
```

### Problème 5: MongoDB ne démarre pas

```bash
# Vérifier l'espace disque
df -h

# Vérifier les logs MongoDB
docker-compose logs mongodb

# Réinitialiser MongoDB (⚠️ SUPPRIME LES DONNÉES)
docker-compose down
docker volume rm vectort_mongodb_data
docker-compose up -d
```

## 🔄 Mise à Jour

Pour mettre à jour l'application:

1. Préparez un nouveau package sur Emergent
2. Transférez-le vers Contabo
3. Sur le serveur:

```bash
cd /opt/vectort
docker-compose down

cd /opt
tar -xzf vectort-deploy.tar.gz
cd vectort-deploy

# Sauvegarder les .env actuels
cp /opt/vectort/backend/.env ./backend/.env.backup
cp /opt/vectort/frontend/.env ./frontend/.env.backup

# Copier vers l'ancien répertoire
cp -r * /opt/vectort/

cd /opt/vectort
docker-compose up -d --build
```

## 📞 Support

En cas de problème:

1. Consultez les logs: `docker-compose logs -f`
2. Vérifiez la configuration: `cat backend/.env`
3. Testez les endpoints:
   - `curl http://localhost:8001/api/`
   - `curl http://localhost:3000`
4. Vérifiez l'état des services: `docker-compose ps`

## 🎉 Félicitations!

Votre application Vectort.io est maintenant déployée sur Contabo!

Accédez à votre application sur:
- **Frontend**: https://vectort.io
- **Backend API**: https://api.vectort.io

---

**Note**: Gardez ce guide accessible pour les futures mises à jour et le dépannage.
