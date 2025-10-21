# 🔄 Guide de Mise à Jour Vectort.io sur Contabo

## ⚡ Mise à Jour Rapide en 3 Étapes

Ce guide est pour mettre à jour une application Vectort.io **déjà déployée** sur votre serveur Contabo.

---

## 🎯 Étape 1: Créer le Package de Mise à Jour

Sur votre environnement Emergent, exécutez:

```bash
cd /app
./prepare-deploy-package.sh
```

✅ Cela crée `/tmp/vectort-deploy.tar.gz` (~375 KB)

---

## 🎯 Étape 2: Transférer vers Contabo

Depuis votre terminal:

```bash
scp /tmp/vectort-deploy.tar.gz root@156.67.26.106:/opt/
```

**Mot de passe**: `aE761027`

---

## 🎯 Étape 3: Mettre à Jour sur Contabo

Connectez-vous et exécutez le script de mise à jour:

```bash
# Se connecter
ssh root@156.67.26.106

# Mot de passe: aE761027

# Mettre à jour (UNE SEULE COMMANDE)
cd /opt && tar -xzf vectort-deploy.tar.gz && cd vectort-deploy && chmod +x update-contabo.sh && sudo ./update-contabo.sh
```

---

## 🔄 Ce que fait le Script de Mise à Jour

Le script `update-contabo.sh` effectue automatiquement:

1. ✅ **Vérifie** l'installation existante dans `/opt/vectort`
2. ✅ **Sauvegarde** complète de l'application actuelle
3. ✅ **Sauvegarde** les fichiers `.env` (clés API)
4. ✅ **Arrête** les services (backend, frontend, mongodb)
5. ✅ **Met à jour** le code source
6. ✅ **Restaure** les configurations `.env`
7. ✅ **Reconstruit** les images Docker
8. ✅ **Redémarre** tous les services

**Durée totale**: 3-5 minutes ⏱️

---

## ✅ Vérification Après Mise à Jour

### 1. Vérifier l'État des Services

```bash
cd /opt/vectort
docker-compose ps
```

**Tous les services doivent être "Up":**
```
NAME                  STATUS
vectort-mongodb      Up
vectort-backend      Up  
vectort-frontend     Up
```

### 2. Voir les Logs en Temps Réel

```bash
cd /opt/vectort
docker-compose logs -f
```

Pressez `Ctrl+C` pour quitter.

### 3. Tester l'Application

- **Frontend**: https://vectort.io
- **Backend API**: https://api.vectort.io/api/
- **Test de génération**: Créez un nouveau projet pour vérifier

---

## 🆘 En Cas de Problème

### Option 1: Redémarrer les Services

```bash
cd /opt/vectort
docker-compose restart
```

### Option 2: Reconstruire Complètement

```bash
cd /opt/vectort
docker-compose down
docker-compose up -d --build
```

### Option 3: Restaurer la Sauvegarde

Le script crée automatiquement une sauvegarde dans `/opt/vectort-backup-YYYYMMDD-HHMMSS/`

```bash
# Trouver la sauvegarde
ls -lt /opt/ | grep vectort-backup

# Restaurer (remplacez la date)
cd /opt/vectort
docker-compose down
rm -rf /opt/vectort/*
cp -r /opt/vectort-backup-20241021-142230/* /opt/vectort/
cd /opt/vectort
docker-compose up -d
```

---

## 🔧 Commandes Utiles

### Gestion des Services

```bash
cd /opt/vectort

# Voir l'état
docker-compose ps

# Voir les logs
docker-compose logs -f

# Redémarrer tout
docker-compose restart

# Redémarrer un service
docker-compose restart backend
docker-compose restart frontend

# Arrêter
docker-compose down

# Démarrer
docker-compose up -d
```

### Nettoyage

```bash
# Supprimer les anciennes sauvegardes (gardez la plus récente !)
rm -rf /opt/vectort-backup-ANCIENNE_DATE

# Nettoyer Docker
docker system prune -a
```

---

## 📊 Différences avec un Déploiement Initial

| Action | Déploiement Initial | Mise à Jour |
|--------|---------------------|-------------|
| Installer Docker | ✅ Oui | ❌ Non (déjà installé) |
| Configurer Nginx | ✅ Oui | ❌ Non (configuration préservée) |
| Installer SSL | ✅ Oui | ❌ Non (certificats préservés) |
| Créer .env | ✅ Oui | ❌ Non (réutilise l'existant) |
| Mettre à jour code | ✅ Oui | ✅ Oui |
| Sauvegarder | ❌ Non | ✅ Oui |
| Durée | 10-15 min | 3-5 min |

---

## 💡 Conseils

### Avant la Mise à Jour

1. ✅ Vérifiez que l'application fonctionne actuellement
2. ✅ Notez les éventuelles personnalisations faites
3. ✅ Prévenez vos utilisateurs (si nécessaire)

### Après la Mise à Jour

1. ✅ Testez toutes les fonctionnalités principales
2. ✅ Vérifiez les logs pour détecter des erreurs
3. ✅ Surveillez les performances

### Meilleures Pratiques

- 🕐 **Faites les mises à jour pendant les heures creuses**
- 💾 **Conservez au moins 2 sauvegardes**
- 📝 **Documentez les changements effectués**
- 🔍 **Surveillez les logs pendant 24h après mise à jour**

---

## 📞 Besoin d'Aide ?

### Vérifier les Logs

```bash
# Backend
docker-compose logs backend | tail -100

# Frontend  
docker-compose logs frontend | tail -100

# Nginx
sudo tail -f /var/log/nginx/error.log
```

### Problèmes Courants

**1. "Container not found"**
```bash
cd /opt/vectort
docker-compose up -d
```

**2. "Port already in use"**
```bash
sudo lsof -i :8001
sudo lsof -i :3000
# Tuer le processus si nécessaire
```

**3. "Permission denied"**
```bash
sudo chown -R root:root /opt/vectort
cd /opt/vectort
docker-compose restart
```

---

## 🎉 C'est Fait !

Votre application Vectort.io est maintenant à jour avec les dernières améliorations !

**Prochaine mise à jour ?** Répétez simplement ces 3 étapes.

---

**📌 Aide-mémoire rapide:**

```bash
# Sur Emergent
cd /app && ./prepare-deploy-package.sh

# Transférer
scp /tmp/vectort-deploy.tar.gz root@156.67.26.106:/opt/

# Sur Contabo
ssh root@156.67.26.106
cd /opt && tar -xzf vectort-deploy.tar.gz && cd vectort-deploy && chmod +x update-contabo.sh && sudo ./update-contabo.sh
```
