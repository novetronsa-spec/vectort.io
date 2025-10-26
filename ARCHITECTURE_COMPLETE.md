# 🏗️ Architecture Vectort.io - Documentation Complète

## 📋 Vue d'ensemble

Vectort.io est une plateforme de génération d'applications par IA avec déploiement automatisé. C'est un clone avancé d'Emergent.sh avec des fonctionnalités étendues.

---

## 🎯 Architecture Système

```
┌─────────────────────────────────────────────────────────────┐
│                      UTILISATEURS                            │
│          (Web Browser - Chrome, Safari, Firefox)            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (React)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • Landing Page                                       │  │
│  │  • Dashboard                                          │  │
│  │  • Auth Pages (Login/Register)                       │  │
│  │  • Project Management                                │  │
│  │  • Code Preview                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Port: 3000 (Hot reload enabled)                            │
│  Nginx reverse proxy                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTPS REST API
                       │ (JSON)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Routes:                                          │  │
│  │  • /api/auth/*        - Authentication                │  │
│  │  • /api/projects/*    - Project CRUD                  │  │
│  │  • /api/credits/*     - Credit system                 │  │
│  │  • /api/deployment/*  - Multi-platform deploy         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Port: 8001 (Supervisor managed)                            │
│  Python 3.11 + FastAPI + Uvicorn                            │
└──────────────┬───────────────────┬─────────────────────────┘
               │                   │
               │                   │
               ▼                   ▼
┌──────────────────────┐  ┌──────────────────────────────────┐
│   MongoDB Database   │  │    AI Services (Multi-LLM)       │
│                      │  │                                   │
│  • Users             │  │  ┌──────────────────────────┐    │
│  • Projects          │  │  │  1. GPT-5 (OpenAI)       │    │
│  • Generated Apps    │  │  │     - Primary LLM        │    │
│  • Credit Trans.     │  │  └──────────────────────────┘    │
│  • Payments          │  │           ↓ Fallback             │
│                      │  │  ┌──────────────────────────┐    │
│  Port: 27017         │  │  │  2. Claude 4 (Anthropic) │    │
└──────────────────────┘  │  │     - Fallback 1         │    │
                          │  └──────────────────────────┘    │
                          │           ↓ Fallback             │
                          │  ┌──────────────────────────┐    │
                          │  │  3. Gemini 2.5 Pro       │    │
                          │  │     - Fallback 2         │    │
                          │  └──────────────────────────┘    │
                          │                                   │
                          │  Circuit Breaker + Retry Logic   │
                          └──────────────────────────────────┘
```

---

## 🔐 Authentification Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ 1. Click "Sign in with Google/GitHub/Apple"
       ▼
┌─────────────────────────────────────────┐
│  Frontend: /api/auth/{provider}/login   │
└──────┬──────────────────────────────────┘
       │
       │ 2. Redirect to OAuth Provider
       ▼
┌──────────────────────────────────┐
│  OAuth Provider                  │
│  (Google/GitHub/Apple)           │
│                                  │
│  User enters credentials         │
└──────┬───────────────────────────┘
       │
       │ 3. Callback with authorization code
       ▼
┌─────────────────────────────────────────┐
│  Backend: /api/auth/{provider}/callback │
│                                         │
│  • Exchange code for token             │
│  • Get user info from provider         │
│  • Create/find user in MongoDB         │
│  • Generate JWT token                  │
└──────┬──────────────────────────────────┘
       │
       │ 4. Redirect to frontend with JWT
       ▼
┌─────────────────────────────────┐
│  Frontend: /auth/callback       │
│                                 │
│  • Store JWT in localStorage    │
│  • Redirect to Dashboard        │
└─────────────────────────────────┘
```

---

## 🤖 Génération de Code - Architecture

```
┌─────────────────┐
│  User Request   │
│  "Create a      │
│   e-commerce    │
│   platform"     │
└────────┬────────┘
         │
         │ POST /api/projects/{id}/generate
         ▼
┌────────────────────────────────────────────┐
│  Generation Controller                     │
│  • Validate request                        │
│  • Check user credits                      │
│  • Determine mode (quick/advanced)         │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  Multi-LLM Service                         │
│  ┌──────────────────────────────────────┐ │
│  │  Circuit Breaker Manager             │ │
│  │  • Track provider health             │ │
│  │  • Automatic failover                │ │
│  └──────────────────────────────────────┘ │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  LLM Provider Selection                    │
│                                            │
│  Try GPT-5                                 │
│    ↓ If fails (timeout/error)             │
│  Try Claude 4                              │
│    ↓ If fails                             │
│  Try Gemini 2.5 Pro                        │
│                                            │
│  With exponential backoff retry            │
└────────┬───────────────────────────────────┘
         │
         │ AI Response: Code generated
         ▼
┌────────────────────────────────────────────┐
│  Code Processing Pipeline                  │
│  ┌──────────────────────────────────────┐ │
│  │  1. Parse AI response                │ │
│  │  2. Extract code blocks              │ │
│  │     - React/HTML                     │ │
│  │     - CSS                            │ │
│  │     - JavaScript                     │ │
│  │     - Backend (if needed)            │ │
│  │  3. Validate syntax                  │ │
│  │  4. Structure project files          │ │
│  └──────────────────────────────────────┘ │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  Storage & Response                        │
│  • Save to MongoDB                         │
│  • Deduct credits                          │
│  • Return generated code to client         │
└────────────────────────────────────────────┘
```

---

## 🚀 Déploiement Multi-Plateforme

```
┌──────────────────┐
│  Generated Code  │
│  (from MongoDB)  │
└────────┬─────────┘
         │
         │ User clicks "Deploy"
         ▼
┌────────────────────────────────────────────┐
│  Deployment Modal (Frontend)               │
│  • Select platform: Vercel/Netlify/Render │
│  • Configure: env vars, framework, etc    │
└────────┬───────────────────────────────────┘
         │
         │ POST /api/projects/{id}/deploy
         ▼
┌────────────────────────────────────────────┐
│  Deployment Controller (Backend)           │
│  • Validate project ownership              │
│  • Check GitHub repo exists                │
│  • Route to appropriate platform service   │
└────────┬───────────────────────────────────┘
         │
         ├────────┐
         │        │
         ▼        ▼        ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │ Vercel │ │Netlify │ │ Render │
    │Service │ │Service │ │Service │
    └───┬────┘ └───┬────┘ └───┬────┘
        │          │          │
        │ API Call │ API Call │ API Call
        │          │          │
        ▼          ▼          ▼
    ┌────────────────────────────┐
    │  Platform APIs             │
    │  • Vercel API              │
    │  • Netlify API             │
    │  • Render API              │
    │                            │
    │  Deploy from GitHub repo   │
    └────────┬───────────────────┘
             │
             │ Deployment initiated
             ▼
    ┌────────────────────────────┐
    │  Live Application          │
    │  • URL provided            │
    │  • Automatic builds        │
    │  • CDN distribution        │
    └────────────────────────────┘
```

---

## 💳 Système de Crédits & Paiements

```
┌──────────────────┐
│  User Profile    │
│  Credits:        │
│  • Free: 10      │
│  • Purchased: 0  │
└────────┬─────────┘
         │
         │ 1. Click "Buy Credits"
         ▼
┌────────────────────────────────────────────┐
│  Credit Packages                           │
│  • Micro: 10 credits = $10                │
│  • Starter: 80 credits = $20              │
│  • Standard: 250 credits = $50            │
│  • Pro: 600 credits = $100                │
└────────┬───────────────────────────────────┘
         │
         │ POST /api/credits/purchase
         ▼
┌────────────────────────────────────────────┐
│  Stripe Integration                        │
│  1. Create Checkout Session                │
│  2. Redirect to Stripe                     │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  Stripe Payment Page                       │
│  • User enters card details                │
│  • Completes payment                       │
└────────┬───────────────────────────────────┘
         │
         │ Webhook: payment_intent.succeeded
         ▼
┌────────────────────────────────────────────┐
│  Backend: /api/webhook/stripe              │
│  • Verify webhook signature                │
│  • Find transaction in DB                  │
│  • Add credits to user account             │
│  • Update transaction status               │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  User Dashboard                            │
│  Credits updated: +80                      │
└────────────────────────────────────────────┘
```

---

## 📊 Modèle de Données (MongoDB)

### Collection: users
```json
{
  "_id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "provider": "google|github|apple|email",
  "provider_id": "oauth_provider_id",
  "credits_free": 10.0,
  "credits_monthly": 0.0,
  "credits_topup": 0.0,
  "credits_total": 10.0,
  "subscription_plan": "free",
  "created_at": "2025-10-26T00:00:00Z",
  "updated_at": "2025-10-26T00:00:00Z",
  "is_active": true
}
```

### Collection: projects
```json
{
  "_id": "uuid",
  "id": "uuid",
  "user_id": "user_uuid",
  "title": "My E-commerce App",
  "description": "Complete shopping platform",
  "type": "web_app",
  "status": "draft|generating|completed",
  "repository_url": "https://github.com/user/repo",
  "deployment_url": "https://app.vercel.app",
  "created_at": "2025-10-26T00:00:00Z",
  "updated_at": "2025-10-26T00:00:00Z",
  "config": {}
}
```

### Collection: generated_apps
```json
{
  "_id": "uuid",
  "id": "uuid",
  "project_id": "project_uuid",
  "html_code": "<html>...</html>",
  "css_code": ".container { ... }",
  "js_code": "function App() { ... }",
  "react_code": "import React from 'react'...",
  "backend_code": "from fastapi import...",
  "project_structure": {},
  "package_json": "{...}",
  "requirements_txt": "fastapi==...",
  "all_files": {},
  "created_at": "2025-10-26T00:00:00Z"
}
```

### Collection: credit_transactions
```json
{
  "_id": "uuid",
  "id": "uuid",
  "user_id": "user_uuid",
  "amount": 10,
  "type": "purchase|usage|bonus",
  "description": "Purchased Starter package",
  "project_id": "project_uuid",
  "created_at": "2025-10-26T00:00:00Z"
}
```

### Collection: payment_transactions
```json
{
  "_id": "uuid",
  "id": "uuid",
  "user_id": "user_uuid",
  "session_id": "stripe_session_id",
  "amount": 20.0,
  "currency": "usd",
  "credits": 80,
  "package_id": "starter",
  "payment_status": "pending|completed|failed",
  "status": "initiated|completed",
  "metadata": {},
  "created_at": "2025-10-26T00:00:00Z",
  "updated_at": "2025-10-26T00:00:00Z"
}
```

---

## 🔌 APIs & Endpoints

### Authentication
```
POST   /api/auth/register          - Create new account
POST   /api/auth/login             - Login with email/password
GET    /api/auth/google/login      - Initiate Google OAuth
GET    /api/auth/google/callback   - Google OAuth callback
GET    /api/auth/github/login      - Initiate GitHub OAuth
GET    /api/auth/github/callback   - GitHub OAuth callback
GET    /api/auth/apple/login       - Initiate Apple OAuth
POST   /api/auth/apple/callback    - Apple OAuth callback
```

### Projects
```
GET    /api/projects               - List user projects
POST   /api/projects               - Create new project
GET    /api/projects/{id}          - Get project details
PUT    /api/projects/{id}          - Update project
DELETE /api/projects/{id}          - Delete project
POST   /api/projects/{id}/generate - Generate code with AI
GET    /api/projects/{id}/code     - Get generated code
```

### Deployment
```
GET    /api/deployment/platforms   - List supported platforms
POST   /api/projects/{id}/deploy   - Deploy to platform
GET    /api/projects/{id}/deployment/status - Check status
```

### Credits & Payments
```
GET    /api/credits/balance        - Get credit balance
GET    /api/credits/packages       - List available packages
POST   /api/credits/purchase       - Create payment session
GET    /api/credits/history        - Transaction history
POST   /api/webhook/stripe         - Stripe webhook handler
```

### Export
```
POST   /api/projects/{id}/export/github - Push to GitHub
POST   /api/projects/{id}/export/zip    - Download as ZIP
```

---

## 🔧 Technologies Stack

### Frontend
- **Framework:** React 18
- **Build Tool:** Craco (Create React App Config Override)
- **Routing:** React Router v6
- **State Management:** Context API
- **HTTP Client:** Axios
- **Styling:** Tailwind CSS + Custom CSS
- **Icons:** Lucide React
- **Internationalization:** Custom i18n with JSON
- **Web Server:** Nginx (reverse proxy)

### Backend
- **Framework:** FastAPI 0.110+
- **Language:** Python 3.11
- **ASGI Server:** Uvicorn
- **Database:** MongoDB 4.5+ (Motor async driver)
- **Authentication:** JWT (python-jose)
- **Password Hashing:** SHA256-crypt
- **AI Integration:** Emergent Integrations
- **Payments:** Stripe SDK
- **OAuth:** httpx + cryptography
- **Process Manager:** Supervisor

### Infrastructure
- **Container:** Kubernetes
- **Database:** MongoDB (localhost:27017)
- **Backend Port:** 8001 (internal)
- **Frontend Port:** 3000 (internal)
- **External URL:** omniai-platform-2.preview.emergentagent.com

### AI & External Services
- **LLM Providers:** OpenAI GPT-5, Anthropic Claude 4, Google Gemini 2.5
- **LLM Key:** Emergent Universal Key
- **Deployment:** Vercel, Netlify, Render
- **Version Control:** GitHub
- **Email:** SendGrid
- **Storage:** AWS S3
- **Payment:** Stripe

---

## 🔄 Flux de Travail Utilisateur

### 1. Inscription & Connexion
```
User → Landing Page → Click "Get Started"
     → Auth Page → Select OAuth provider (Google/GitHub/Apple)
     → OAuth Flow → Return with JWT token
     → Redirect to Dashboard
```

### 2. Création de Projet
```
Dashboard → Click "New Project"
         → Enter title & description
         → Select type (web app, mobile, etc.)
         → Click "Create"
         → Project created with 10 free credits
```

### 3. Génération de Code
```
Project Page → Enter detailed requirements
            → Click "Generate" (Quick: 2 credits, Advanced: 4 credits)
            → AI generates code (10-20 seconds)
            → Preview code in browser
            → Download ZIP or push to GitHub
```

### 4. Déploiement
```
Project Page → Click "Deploy"
            → Select platform (Vercel/Netlify/Render)
            → Configure settings (env vars, framework)
            → Click "Deploy to [Platform]"
            → Deployment initiated
            → Live URL provided
```

### 5. Gestion des Crédits
```
Dashboard → Check credit balance
         → Click "Buy Credits"
         → Select package
         → Stripe checkout
         → Payment completed
         → Credits added automatically
```

---

## ⚡ Performance & Scalabilité

### Temps de Réponse
- **Authentication:** < 2s
- **Project CRUD:** < 500ms
- **AI Generation (Quick):** 10-15s
- **AI Generation (Advanced):** 15-30s
- **Deployment API call:** 2-5s

### Optimisations
- **Frontend:** Code splitting, lazy loading
- **Backend:** Async operations, connection pooling
- **Database:** Indexed queries, projection
- **AI:** Circuit breaker prevents cascading failures
- **Caching:** Browser caching for static assets

### Limites Actuelles
- **Concurrent generations:** Limited by LLM API rate limits
- **Max file size:** 10MB for uploads
- **Code generation timeout:** 30 seconds
- **MongoDB connection pool:** 100 connections

---

## 🛡️ Sécurité

### Authentification
- JWT tokens with expiration (24 hours)
- OAuth 2.0 for third-party logins
- Password hashing with SHA256-crypt
- CSRF protection via state parameter

### API Security
- HTTPS only (TLS 1.2+)
- CORS configuration
- Rate limiting on sensitive endpoints
- Input validation with Pydantic
- SQL injection prevention (NoSQL)
- XSS protection (HTML escaping)

### Data Protection
- Environment variables for secrets
- Encrypted sensitive data in database
- Webhook signature verification (Stripe)
- No sensitive data in logs

---

## 📈 Métriques & Monitoring

### Logs Backend
```bash
# Access logs
/var/log/supervisor/backend.out.log

# Error logs
/var/log/supervisor/backend.err.log
```

### Key Metrics to Monitor
- User registration rate
- AI generation success rate
- Credit consumption patterns
- Payment conversion rate
- Deployment success rate
- API response times
- Error rates by endpoint

---

## 🔮 Roadmap & Extensions

### Features Implemented ✅
- Multi-OAuth authentication
- AI code generation with fallback
- Multi-platform deployment
- Credit system with Stripe
- Project management
- GitHub export

### Planned Features 🚧
- Real-time code collaboration
- Template marketplace
- Custom AI training
- Advanced analytics dashboard
- Team workspaces
- API webhooks for CI/CD

---

## 📚 Code Structure

```
/app/
├── backend/
│   ├── ai_generators/
│   │   ├── multi_llm_service.py      # Multi-LLM with fallback
│   │   ├── advanced_generator.py     # Complex project generation
│   │   └── enhanced_generator.py     # Enhanced features
│   ├── exporters/
│   │   ├── deployment_platforms.py   # Vercel/Netlify/Render
│   │   ├── github_exporter.py        # GitHub integration
│   │   └── zip_exporter.py           # ZIP download
│   ├── validators/
│   │   └── code_validator.py         # Code validation
│   ├── auth_oauth.py                 # OAuth handlers
│   ├── server.py                     # Main FastAPI app
│   ├── .env                          # Environment variables
│   └── requirements.txt              # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/               # React components
│   │   ├── contexts/                 # Context providers
│   │   ├── pages/                    # Page components
│   │   ├── locales/                  # i18n translations
│   │   └── utils/                    # Utility functions
│   ├── public/                       # Static assets
│   ├── .env                          # Frontend env vars
│   └── package.json                  # Node dependencies
└── docker-compose.yml                # Container orchestration
```

---

## 🎓 Concepts Clés

### Circuit Breaker Pattern
Empêche les appels répétés à un service défaillant:
- **CLOSED:** Fonctionnement normal
- **OPEN:** Service défaillant, requêtes bloquées
- **HALF_OPEN:** Test de récupération

### Exponential Backoff
Retry avec délais croissants:
- 1ère retry: 1s
- 2ème retry: 2s
- 3ème retry: 4s

### JWT Authentication
Stateless authentication avec tokens signés contenant claims.

### OAuth 2.0 Flow
Authorization Code Grant pour applications web sécurisées.

---

**Documentation générée le:** 2025-10-26
**Version:** 1.0.0
**Statut:** Production-Ready ✅
