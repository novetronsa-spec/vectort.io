# 🌟 Vectort.io - Package de Déploiement Contabo

## 📦 Contenu du Package

Ce package contient tout ce dont vous avez besoin pour déployer Vectort.io sur votre serveur Contabo.

### 📁 Structure du Package

```
vectort-deploy/
├── backend/                    # Application backend FastAPI
│   ├── server.py              # Serveur principal
│   ├── requirements.txt       # Dépendances Python
│   ├── ai_generators/         # Générateurs d'applications IA
│   ├── exporters/             # Export ZIP et GitHub
│   └── Dockerfile             # Configuration Docker backend
├── frontend/                   # Application frontend React
│   ├── src/                   # Code source React
│   ├── package.json           # Dépendances Node.js
│   └── Dockerfile             # Configuration Docker frontend
├── docker-compose.yml         # Orchestration des services
├── contabo-auto-deploy.sh     # ⭐ Script de déploiement automatique
└── DEPLOY_INSTRUCTIONS_FR.md  # Guide détaillé
```

## 🚀 Déploiement Rapide

### Prérequis

- Serveur Contabo accessible (Ubuntu/Debian)
- Accès root SSH
- Domaines DNS configurés (vectort.io, api.vectort.io)

### Installation en Une Commande

```bash
chmod +x contabo-auto-deploy.sh && sudo ./contabo-auto-deploy.sh
```

**Ce script va:**

1. ✅ Mettre à jour le système
2. ✅ Installer Docker & Docker Compose
3. ✅ Configurer Nginx comme reverse proxy
4. ✅ Installer Certbot pour SSL
5. ✅ Créer les fichiers de configuration
6. ✅ Démarrer tous les services
7. ✅ Configurer les certificats SSL automatiquement

**Durée**: 10-15 minutes

## 🔧 Configuration

### Variables d'Environnement

Après le déploiement, configurez vos clés API:

```bash
nano /opt/vectort/backend/.env
```

**Clés requises:**

```env
# Base de données (déjà configuré)
MONGO_URL=mongodb://mongodb:27017/vectort_db

# IA et Génération de Code
EMERGENT_LLM_KEY=zvPaiA9UKOXJTFoeHEqCsDSlWw2fR8un6Q3VZYkN75t0hmBbyM

# Paiements
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Intégrations
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
SENDGRID_API_KEY=SG...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

**Après modification:**

```bash
cd /opt/vectort && docker-compose restart
```

## 🎯 Services Déployés

### Frontend (Port 3000)
- Application React
- Accessible via https://vectort.io
- Interface utilisateur complète

### Backend (Port 8001)
- API FastAPI
- Accessible via https://api.vectort.io
- Endpoints RESTful

### MongoDB (Port 27017)
- Base de données
- Stockage persistant
- Accessible uniquement en interne

## 📊 Monitoring

### Vérifier l'État des Services

```bash
cd /opt/vectort
docker-compose ps
```

**Résultat attendu:**
```
NAME                  STATUS    PORTS
vectort-mongodb      Up        27017/tcp
vectort-backend      Up        8001/tcp
vectort-frontend     Up        3000/tcp
```

### Voir les Logs

```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### Tester les Endpoints

```bash
# API Status
curl https://api.vectort.io/api/

# Frontend
curl https://vectort.io

# Santé du système
docker-compose ps
```

## 🔄 Gestion des Services

### Commandes Communes

```bash
cd /opt/vectort

# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Redémarrer
docker-compose restart

# Redémarrer un service spécifique
docker-compose restart backend

# Reconstruire et redémarrer
docker-compose up -d --build
```

## 🛠️ Maintenance

### Sauvegardes

**Sauvegarder la base de données:**

```bash
docker exec vectort-mongodb mongodump --out /backup
docker cp vectort-mongodb:/backup ./mongodb-backup-$(date +%Y%m%d)
```

**Sauvegarder la configuration:**

```bash
cp /opt/vectort/backend/.env /opt/vectort/backend/.env.backup
cp /opt/vectort/frontend/.env /opt/vectort/frontend/.env.backup
```

### Mise à Jour

Pour mettre à jour l'application:

1. Téléchargez le nouveau package
2. Arrêtez les services: `docker-compose down`
3. Sauvegardez les .env
4. Extrayez le nouveau package
5. Restaurez les .env
6. Redémarrez: `docker-compose up -d --build`

### Nettoyage

```bash
# Nettoyer les images Docker inutilisées
docker system prune -a

# Supprimer les volumes orphelins
docker volume prune
```

## 🐛 Dépannage

### Backend ne démarre pas

```bash
# Vérifier les logs
docker-compose logs backend

# Vérifier la connexion MongoDB
docker exec vectort-backend ping mongodb

# Redémarrer
docker-compose restart backend
```

### Frontend affiche une erreur

```bash
# Vérifier la configuration
cat /opt/vectort/frontend/.env

# Vérifier que REACT_APP_BACKEND_URL est correct
# Doit être: REACT_APP_BACKEND_URL=https://api.vectort.io

# Reconstruire
docker-compose up -d --build frontend
```

### Certificats SSL expirés

```bash
# Renouveler manuellement
certbot renew

# Tester le renouvellement
certbot renew --dry-run
```

### Espace disque plein

```bash
# Vérifier l'espace
df -h

# Nettoyer Docker
docker system prune -a --volumes

# Nettoyer les logs
journalctl --vacuum-time=7d
```

## 📈 Performance

### Optimisations Recommandées

1. **Cache Nginx**: Déjà configuré
2. **Compression Gzip**: Activée par défaut
3. **Logs rotation**: Configurez logrotate
4. **MongoDB Indexes**: Créez des index pour les requêtes fréquentes

### Monitoring Avancé

Installez des outils de monitoring:

```bash
# Portainer (Interface Docker Web)
docker run -d -p 9000:9000 \
  --name=portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  portainer/portainer-ce
```

Accès: http://156.67.26.106:9000

## 🔒 Sécurité

### Points Importants

1. ✅ SSL/TLS activé (Certbot)
2. ✅ Clés JWT sécurisées
3. ✅ Variables d'environnement protégées
4. ✅ CORS configuré
5. ✅ Rate limiting (Nginx)

### Recommandations

- Changez les mots de passe par défaut
- Activez le firewall (UFW)
- Configurez fail2ban
- Mettez à jour régulièrement
- Surveillez les logs d'accès

## 📞 Support

### Documentation

- Guide complet: `DEPLOY_INSTRUCTIONS_FR.md`
- Architecture: Voir structure ci-dessus
- API Docs: https://api.vectort.io/docs (quand déployé)

### Problèmes Courants

| Problème | Solution |
|----------|----------|
| Conteneurs ne démarrent pas | `docker-compose logs` |
| SSL échoue | Vérifier DNS |
| Backend timeout | Augmenter les ressources |
| MongoDB crash | Vérifier l'espace disque |

### Logs Importants

```bash
# Application
/opt/vectort/
  ├── backend logs: docker-compose logs backend
  ├── frontend logs: docker-compose logs frontend
  └── mongodb logs: docker-compose logs mongodb

# Système
/var/log/nginx/error.log
/var/log/nginx/access.log
```

## 🎉 Félicitations !

Votre application Vectort.io est maintenant déployée et opérationnelle sur Contabo !

**Accès:**
- 🌐 Frontend: https://vectort.io
- 🔌 Backend: https://api.vectort.io
- 📊 Monitoring: `docker-compose ps`

---

**Version**: 2.0  
**Date**: Octobre 2024  
**Serveur**: Contabo VPS  
**Stack**: FastAPI + React + MongoDB + Docker
