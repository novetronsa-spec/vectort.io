# 🚀 Guide Rapide - Déploiement Vectort.io sur Contabo

## ⚡ Déploiement en 3 Étapes

### 📋 Ce que vous avez besoin

- **IP Serveur Contabo**: 156.67.26.106
- **Mot de passe SSH**: aE761027
- **Domaines configurés**: vectort.io et api.vectort.io pointant vers 156.67.26.106

---

## 🎯 Étape 1: Créer le Package

Sur votre environnement Emergent actuel, exécutez:

```bash
cd /app
./prepare-deploy-package.sh
```

✅ Cela crée `/tmp/vectort-deploy.tar.gz` (~376 KB)

---

## 🎯 Étape 2: Transférer vers Contabo

Depuis votre terminal, exécutez:

```bash
scp /tmp/vectort-deploy.tar.gz root@156.67.26.106:/opt/
```

**Mot de passe**: `aE761027`

---

## 🎯 Étape 3: Déployer sur Contabo

Connectez-vous et déployez:

```bash
# Se connecter
ssh root@156.67.26.106

# Mot de passe: aE761027

# Déployer (UNE SEULE COMMANDE)
cd /opt && tar -xzf vectort-deploy.tar.gz && cd vectort-deploy && chmod +x contabo-auto-deploy.sh && sudo ./contabo-auto-deploy.sh
```

Le script va installer TOUT automatiquement (10-15 minutes):
- ✅ Docker + Docker Compose
- ✅ Nginx + Configuration
- ✅ Certificats SSL (Certbot)
- ✅ MongoDB
- ✅ Backend + Frontend
- ✅ Configuration automatique

---

## 🔑 Étape 4: Ajouter vos Clés API

Après le déploiement, configurez vos clés:

```bash
nano /opt/vectort/backend/.env
```

**Modifiez ces lignes:**

```env
EMERGENT_LLM_KEY=zvPaiA9UKOXJTFoeHEqCsDSlWw2fR8un6Q3VZYkN75t0hmBbyM
STRIPE_SECRET_KEY=votre_clé_stripe_ici
GITHUB_CLIENT_ID=votre_client_id_github
GITHUB_CLIENT_SECRET=votre_client_secret_github
SENDGRID_API_KEY=votre_clé_sendgrid
```

**Sauvegardez**: `Ctrl+X` → `Y` → `Enter`

**Redémarrez**:

```bash
cd /opt/vectort
docker-compose restart
```

---

## ✅ Vérification

Testez votre application:

1. **Frontend**: https://vectort.io
2. **Backend**: https://api.vectort.io/api/
3. **Logs**: `cd /opt/vectort && docker-compose logs -f`

---

## 🎊 C'est Fait !

Votre application Vectort.io est maintenant en ligne !

### 🔧 Commandes Utiles

```bash
cd /opt/vectort

# Voir l'état
docker-compose ps

# Voir les logs
docker-compose logs -f

# Redémarrer
docker-compose restart

# Arrêter
docker-compose down

# Démarrer
docker-compose up -d
```

---

## 📞 Besoin d'Aide ?

Consultez le guide complet: `/app/DEPLOY_INSTRUCTIONS_FR.md`

**Problèmes courants:**

1. **Les conteneurs ne démarrent pas**: `docker-compose logs`
2. **Certificats SSL échouent**: Vérifiez que DNS pointe vers 156.67.26.106
3. **Backend ne répond pas**: `docker-compose restart backend`

---

**Note**: Le déploiement initial prend ~10-15 minutes. Le script vous guidera à chaque étape.
