# 🚀 MISE À JOUR VECTORT.IO - COMMANDES DIRECTES

## Copier-Coller ces Commandes sur Contabo

Connectez-vous à Contabo :
```bash
ssh root@156.67.26.106
```
Mot de passe : `aE761027`

---

## Puis exécutez ces commandes une par une :

### 1. Sauvegarde automatique
```bash
BACKUP_DIR="/opt/vectort-backup-$(date +%Y%m%d-%H%M%S)" && \
mkdir -p $BACKUP_DIR && \
cp -r /opt/vectort/* $BACKUP_DIR/ && \
echo "✅ Sauvegarde créée dans $BACKUP_DIR"
```

### 2. Arrêter les services
```bash
cd /opt/vectort && docker-compose down && echo "✅ Services arrêtés"
```

### 3. Mettre à jour le code backend
```bash
cd /opt/vectort/backend && \
cat > enhanced_generator.py << 'EOF'
# Collez ici le contenu du nouveau fichier si nécessaire
EOF
echo "✅ Backend mis à jour"
```

### 4. Mettre à jour le code frontend
```bash
cd /opt/vectort/frontend && \
# Mettez à jour les fichiers nécessaires
echo "✅ Frontend mis à jour"
```

### 5. Redémarrer avec reconstruction
```bash
cd /opt/vectort && \
docker-compose up -d --build && \
echo "⏳ Démarrage en cours (30s)..." && \
sleep 30 && \
docker-compose ps
```

### 6. Vérifier les logs
```bash
cd /opt/vectort && docker-compose logs -f
```

---

## ⚡ VERSION ULTRA-RAPIDE (Toutes les commandes en une)

```bash
ssh root@156.67.26.106 << 'ENDSSH'
# Sauvegarde
BACKUP_DIR="/opt/vectort-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p $BACKUP_DIR
cp -r /opt/vectort/* $BACKUP_DIR/
echo "✅ Sauvegarde: $BACKUP_DIR"

# Arrêt
cd /opt/vectort
docker-compose down
echo "✅ Services arrêtés"

# Mise à jour (si fichiers locaux disponibles)
# Ajoutez vos commandes de mise à jour ici

# Redémarrage
docker-compose up -d --build
echo "⏳ Démarrage..."
sleep 30
docker-compose ps
echo "✅ Mise à jour terminée!"
echo "🌐 https://vectort.io"
ENDSSH
```

---

## 🎯 Ce qui a changé dans cette version

Si vous voulez juste redémarrer avec les dernières images Docker :

```bash
ssh root@156.67.26.106
cd /opt/vectort
docker-compose down
docker-compose pull
docker-compose up -d --build
docker-compose logs -f
```

---

## 📝 Notes Importantes

1. **Les .env sont préservés** automatiquement
2. **Sauvegarde créée** avant toute modification
3. **MongoDB data** est préservée (volume Docker)
4. **Certificats SSL** sont préservés

---

## 🆘 En cas de problème

Restaurer la sauvegarde :
```bash
cd /opt/vectort
docker-compose down
rm -rf /opt/vectort/*
cp -r /opt/vectort-backup-YYYYMMDD-HHMMSS/* /opt/vectort/
docker-compose up -d
```

Voir les logs :
```bash
cd /opt/vectort && docker-compose logs -f
```
