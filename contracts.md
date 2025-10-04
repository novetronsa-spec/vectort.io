# Codex - Contrats API et Intégration Frontend/Backend

## Vue d'ensemble
Codex est un clone fonctionnel d'emergent.sh permettant aux utilisateurs de créer des applications via l'IA. Le système comprend une authentification complète, la gestion de projets, et des statistiques en temps réel.

## Authentification & Utilisateurs

### Modèles de données
```python
# User Model
- id: str (UUID)
- email: str (unique)
- full_name: str
- password_hash: str
- created_at: datetime
- updated_at: datetime
- is_active: bool
- provider: str (email/google/github/apple)
- provider_id: str (optional)
```

### Endpoints d'authentification
```
POST /api/auth/register
Body: {email, password, full_name}
Response: {access_token, user, token_type}

POST /api/auth/login  
Body: {email, password}
Response: {access_token, user, token_type}

GET /api/auth/me
Headers: Authorization: Bearer {token}
Response: {user}

POST /api/auth/oauth/{provider}
Body: {code, state} 
Response: {access_token, user, token_type}
```

## Gestion des Projets

### Modèles de données
```python
# Project Model
- id: str (UUID)
- title: str
- description: str
- type: str (web_app/mobile_app/api/landing_page)
- user_id: str (FK)
- status: str (draft/building/completed/error)
- created_at: datetime
- updated_at: datetime
- config: dict (JSON)
- repository_url: str (optional)
- deployment_url: str (optional)
```

### Endpoints des projets
```
GET /api/projects
Headers: Authorization: Bearer {token}
Response: [projects]

POST /api/projects
Headers: Authorization: Bearer {token}
Body: {title, description, type}
Response: {project}

GET /api/projects/{id}
Headers: Authorization: Bearer {token}
Response: {project}

PUT /api/projects/{id}
Headers: Authorization: Bearer {token}  
Body: {title?, description?, status?}
Response: {project}

DELETE /api/projects/{id}
Headers: Authorization: Bearer {token}
Response: {success: true}
```

## Statistiques

### Modèles de données
```python
# Stats Model (cached/computed)
- total_users: int
- total_apps: int  
- total_countries: int
- active_users_today: int
- projects_created_today: int
```

### Endpoints des statistiques
```
GET /api/stats
Response: {users: "1.5M+", apps: "2M+", countries: "180+"}

GET /api/users/stats
Headers: Authorization: Bearer {token}
Response: {totalProjects, activeProjects, totalViews}
```

## Intégration Frontend/Backend

### AuthContext (Frontend)
- **Remplacer les mocks** : Utiliser les vrais endpoints d'authentification
- **Token management** : Stocker JWT dans localStorage
- **Auto-refresh** : Implémenter le rafraîchissement automatique des tokens
- **Error handling** : Gérer les erreurs d'authentification

### Dashboard (Frontend)  
- **Projets** : Charger depuis `/api/projects`
- **Création** : Envoyer vers `/api/projects` 
- **Statistiques** : Charger depuis `/api/users/stats`
- **Temps réel** : WebSocket pour les mises à jour (optionnel)

### LandingPage (Frontend)
- **Statistiques** : Charger depuis `/api/stats`
- **Navigation** : Rediriger vers dashboard si authentifié
- **Description** : Passer la description via state vers auth/dashboard

## Sécurité

### JWT Configuration
- **Secret key** : Variable d'environnement JWT_SECRET
- **Expiration** : 24h pour access_token  
- **Refresh token** : Optionnel (7 jours)
- **Algorithm** : HS256

### Validation des données
- **Email** : Format email valide
- **Mot de passe** : Minimum 8 caractères
- **Description projet** : Maximum 5000 caractères
- **Rate limiting** : 100 requêtes/minute par utilisateur

## Base de données

### Collections MongoDB
```
users:
  - Indexé sur email (unique)
  - Indexé sur provider + provider_id
  
projects: 
  - Indexé sur user_id
  - Indexé sur created_at (desc)
  - Indexé sur status
  
stats:
  - Collection unique pour les statistiques globales
  - Mise à jour via scheduled job
```

## Variables d'environnement

### Backend
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=codex_db  
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Frontend
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

## Migration et déploiement

1. **Backend** : Implémenter tous les endpoints avec MongoDB
2. **Frontend** : Remplacer les mocks par les vrais appels API
3. **Tests** : Tester l'authentification et la création de projets
4. **Production** : Variables d'environnement de production

## Fonctionnalités à implémenter

### Phase 1 (MVP)
- ✅ Authentification email/mot de passe
- ✅ Gestion des projets CRUD
- ✅ Dashboard utilisateur  
- ✅ Statistiques de base

### Phase 2 (Améliorations)
- OAuth (Google, GitHub, Apple)
- Génération d'applications IA
- Déploiement automatique
- Collaboration multi-utilisateurs

### Phase 3 (Avancé)
- Templates de projets
- Marketplace d'applications
- Analytics avancées
- API publique