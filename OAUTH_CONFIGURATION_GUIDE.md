# 🔧 GUIDE DE CONFIGURATION OAUTH - VECTORT.IO

## ⚠️ PROBLÈME ACTUEL : OAuth "n'autorise pas la connexion"

Le message d'erreur "oauth-debug-2.preview.emergentagent.com n'autorise pas la connexion" signifie que **les redirect URIs ne sont pas configurés** dans Google Cloud Console et GitHub OAuth Apps.

---

## 📋 CONFIGURATION REQUISE

### 🔵 **GOOGLE OAUTH - Configuration Required**

**1. Allez sur Google Cloud Console**
   - URL: https://console.cloud.google.com/apis/credentials
   - Sélectionnez votre projet ou créez-en un nouveau

**2. Créez des identifiants OAuth 2.0**
   - Cliquez sur "Créer des identifiants" → "ID client OAuth 2.0"
   - Type d'application: Application Web
   - Nom: "Vectort.io Web App"

**3. Configurez les Origines JavaScript autorisées**
   ```
   https://oauth-debug-2.preview.emergentagent.com
   ```

**4. Configurez les URI de redirection autorisés**
   ```
   https://oauth-debug-2.preview.emergentagent.com/api/auth/google/callback
   ```

**5. Enregistrez et copiez**
   - Client ID (déjà dans .env)
   - Client Secret (déjà dans .env)

---

### 🐙 **GITHUB OAUTH - Configuration Required**

**1. Allez sur GitHub Developer Settings**
   - URL: https://github.com/settings/developers
   - Cliquez sur "OAuth Apps" → "New OAuth App"

**2. Remplissez le formulaire**
   - Application name: `Vectort.io`
   - Homepage URL: `https://oauth-debug-2.preview.emergentagent.com`
   - Authorization callback URL: 
     ```
     https://oauth-debug-2.preview.emergentagent.com/api/auth/github/callback
     ```

**3. Enregistrez et copiez**
   - Client ID (déjà dans .env)
   - Client Secret (déjà dans .env)

---

### 🍎 **APPLE SIGNIN - Configuration Complexe**

Apple OAuth nécessite une configuration plus complexe avec:
- Apple Developer Account ($99/year)
- Services ID
- Private Key (.p8 file)
- Team ID
- Key ID

**Pour l'instant, Apple OAuth est marqué comme "en cours de développement".**

---

## ✅ APRÈS CONFIGURATION

Une fois les redirect URIs configurés dans Google et GitHub:

1. **Testez Google OAuth**: Cliquez sur "Continue with Google"
2. **Testez GitHub OAuth**: Cliquez sur "GitHub"
3. **Vérifiez**: L'authentification devrait fonctionner

---

## 🔄 URL DE CALLBACK ACTUELLES

Les URLs de callback sont configurées pour pointer vers:
```
Backend: https://oauth-debug-2.preview.emergentagent.com/api/auth/google/callback
Backend: https://oauth-debug-2.preview.emergentagent.com/api/auth/github/callback

Frontend redirect: https://oauth-debug-2.preview.emergentagent.com/auth/callback
```

---

## 📝 NOTES

- **L'authentification email fonctionne** car elle ne dépend pas d'OAuth externe
- Les **redirect URIs DOIVENT correspondre exactement** (incluant HTTPS et le path complet)
- Après configuration, **attendez 1-2 minutes** pour que les changements soient actifs
