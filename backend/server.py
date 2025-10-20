from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import logging
import asyncio
import json
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List, Optional
import uuid
import hashlib
import base64
import re
import html
from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from ai_generators.advanced_generator import (
    AdvancedCodeGenerator, 
    GenerationRequest, 
    ProjectType, 
    Framework, 
    DatabaseType
)
from fastapi import Request
from typing import Dict


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configuration
mongo_url = os.environ['MONGO_URL']
DB_NAME = os.environ.get('DB_NAME', 'vectort_db')
JWT_SECRET = os.environ['JWT_SECRET']  # Obligatoire en production
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

# MongoDB connection
client = AsyncIOMotorClient(mongo_url)
db = client[DB_NAME]

# Password hashing - using sha256_crypt as fallback due to bcrypt issues
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# JWT Security
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI(
    title="Vectort API", 
    version="1.0.0",
    description="AI-powered application generation platform",
    # Production security headers
    docs_url="/docs" if os.environ.get("DEBUG") == "true" else None,
    redoc_url="/redoc" if os.environ.get("DEBUG") == "true" else None
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        if not re.search(r'[A-Z]', value):
            raise ValueError('Le mot de passe doit contenir au moins une lettre majuscule')
        if not re.search(r'[a-z]', value):
            raise ValueError('Le mot de passe doit contenir au moins une lettre minuscule')
        if not re.search(r'\d', value):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        if not re.search(r'[\W_]', value):
            raise ValueError('Le mot de passe doit contenir au moins un caractère spécial')
        return value

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    provider: str = "email"
    provider_id: Optional[str] = None
    # SYSTÈME DE CRÉDITS VECTORT.IO
    credits_free: float = 10.0  # 10 crédits gratuits
    credits_monthly: float = 0.0  # Crédits mensuels selon plan
    credits_monthly_limit: float = 0.0  # Limite mensuelle
    credits_topup: float = 0.0  # Crédits achetés
    subscription_plan: str = "free"  # free, standard, pro, enterprise
    credits_total: float = 10.0  # Total disponible

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class ProjectBase(BaseModel):
    title: str
    description: str
    type: str = "web_app"
    
    @field_validator('title', 'description')
    @classmethod
    def sanitize_html(cls, value):
        if not value:
            return value
        # Échapper les caractères HTML dangereux
        sanitized = html.escape(value.strip())
        # Vérifier qu'il n'y a pas de scripts ou d'éléments dangereux
        if re.search(r'<[^>]*script|javascript:|data:|vbscript:', sanitized, re.IGNORECASE):
            raise ValueError('Contenu potentiellement dangereux détecté')
        return sanitized

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    status: str = "draft"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    config: dict = Field(default_factory=dict)
    repository_url: Optional[str] = None
    deployment_url: Optional[str] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class Stats(BaseModel):
    users: str
    apps: str
    countries: str

class UserStats(BaseModel):
    totalProjects: int
    activeProjects: int
    totalViews: int

class GenerateAppRequest(BaseModel):
    description: str
    type: str = "web_app"
    framework: str = "react" 
    database: Optional[str] = "mongodb"
    features: Optional[List[str]] = []
    integrations: Optional[List[str]] = []
    deployment_target: str = "vercel"
    advanced_mode: bool = False  # Mode avancé pour génération complète
    
    @field_validator('description')
    @classmethod
    def sanitize_description(cls, value):
        if not value:
            raise ValueError('La description est requise')
        # Nettoyer et échapper le contenu
        sanitized = html.escape(value.strip())
        # Limiter la taille
        if len(sanitized) > 10000:  # Augmenté pour projets complexes
            raise ValueError('La description ne peut pas dépasser 10000 caractères')
        return sanitized

class GeneratedApp(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    html_code: Optional[str] = None
    css_code: Optional[str] = None
    js_code: Optional[str] = None
    react_code: Optional[str] = None
    backend_code: Optional[str] = None
    # NOUVEAUX CHAMPS POUR GÉNÉRATION AVANCÉE
    project_structure: Optional[dict] = None
    package_json: Optional[str] = None
    requirements_txt: Optional[str] = None
    dockerfile: Optional[str] = None
    readme: Optional[str] = None
    deployment_config: Optional[dict] = None
    all_files: Optional[dict] = None  # Tous les fichiers générés
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Modèles pour le système de crédits et paiements
class CreditPackage(BaseModel):
    id: str
    name: str
    credits: int
    price: float  # IMPORTANT: Float pour Stripe
    currency: str = "usd"
    description: str

class CreditBalance(BaseModel):
    free_credits: float
    monthly_credits: float
    purchased_credits: float
    total_available: float
    subscription_plan: str

class PurchaseRequest(BaseModel):
    package_id: str
    origin_url: str  # Pour créer les URLs dynamiques

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    amount: float
    currency: str
    credits: int
    package_id: str
    payment_status: str = "pending"  # pending, completed, failed, expired
    status: str = "initiated"  # initiated, processing, completed, failed
    metadata: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CreditTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    amount: int  # Positif pour ajout, négatif pour déduction
    type: str  # purchase, usage, bonus, monthly_reset
    description: str
    project_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Définition des packages de crédits (SECURITY: côté serveur uniquement)
CREDIT_PACKAGES = {
    "starter": CreditPackage(
        id="starter",
        name="Starter",
        credits=100,
        price=20.0,
        currency="usd",
        description="100 crédits pour commencer"
    ),
    "standard": CreditPackage(
        id="standard",
        name="Standard",
        credits=250,
        price=50.0,
        currency="usd",
        description="250 crédits - Meilleure valeur"
    ),
    "pro": CreditPackage(
        id="pro",
        name="Pro",
        credits=400,
        price=80.0,
        currency="usd",
        description="400 crédits - Maximum d'économies"
    )
}


# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise credentials_exception
    return User(**user)

# Fonctions utilitaires pour la gestion des crédits
async def get_user_credit_balance(user_id: str) -> CreditBalance:
    """Récupère le solde de crédits d'un utilisateur"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return CreditBalance(
        free_credits=user.get("credits_free", 0.0),
        monthly_credits=user.get("credits_monthly", 0.0),
        purchased_credits=user.get("credits_topup", 0.0),
        total_available=user.get("credits_total", 0.0),
        subscription_plan=user.get("subscription_plan", "free")
    )

async def deduct_credits(user_id: str, amount: int, description: str, project_id: Optional[str] = None) -> bool:
    """Déduit des crédits du compte utilisateur"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        return False
    
    total_credits = user.get("credits_total", 0.0)
    if total_credits < amount:
        return False
    
    # Déduire d'abord des crédits gratuits, puis mensuels, puis achetés
    free_credits = user.get("credits_free", 0.0)
    monthly_credits = user.get("credits_monthly", 0.0)
    purchased_credits = user.get("credits_topup", 0.0)
    
    remaining = amount
    
    if free_credits >= remaining:
        free_credits -= remaining
        remaining = 0
    elif free_credits > 0:
        remaining -= free_credits
        free_credits = 0
    
    if remaining > 0 and monthly_credits >= remaining:
        monthly_credits -= remaining
        remaining = 0
    elif remaining > 0 and monthly_credits > 0:
        remaining -= monthly_credits
        monthly_credits = 0
    
    if remaining > 0:
        purchased_credits -= remaining
    
    new_total = free_credits + monthly_credits + purchased_credits
    
    # Mettre à jour l'utilisateur
    await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "credits_free": free_credits,
                "credits_monthly": monthly_credits,
                "credits_topup": purchased_credits,
                "credits_total": new_total,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Enregistrer la transaction
    transaction = CreditTransaction(
        user_id=user_id,
        amount=-amount,
        type="usage",
        description=description,
        project_id=project_id
    )
    await db.credit_transactions.insert_one(transaction.dict())
    
    return True

async def add_credits(user_id: str, amount: int, transaction_type: str, description: str) -> bool:
    """Ajoute des crédits au compte utilisateur"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        return False
    
    # Ajouter aux crédits achetés
    purchased_credits = user.get("credits_topup", 0.0) + amount
    total_credits = user.get("credits_free", 0.0) + user.get("credits_monthly", 0.0) + purchased_credits
    
    await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "credits_topup": purchased_credits,
                "credits_total": total_credits,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Enregistrer la transaction
    transaction = CreditTransaction(
        user_id=user_id,
        amount=amount,
        type=transaction_type,
        description=description
    )
    await db.credit_transactions.insert_one(transaction.dict())
    
    return True

async def generate_complete_multifile_project(request: GenerateAppRequest) -> dict:
    """
    NOUVEAU GÉNÉRATEUR - Projets multi-fichiers complets
    Utilise EnhancedProjectGenerator pour créer une structure complète
    """
    try:
        from ai_generators.enhanced_generator import EnhancedProjectGenerator
        
        logger.info(f"Génération multi-fichiers - Framework: {request.framework}, Type: {request.type}")
        
        # Initialiser le générateur amélioré
        generator = EnhancedProjectGenerator(api_key=EMERGENT_LLM_KEY)
        
        # Générer le projet complet
        all_files = await generator.generate_complete_project(
            description=request.description,
            framework=request.framework,
            project_type=request.type,
            advanced_mode=request.advanced_mode
        )
        
        logger.info(f"Projet généré avec {len(all_files)} fichiers")
        
        # Extraire les fichiers principaux pour compatibilité
        html_code = all_files.get("public/index.html", all_files.get("index.html", ""))
        css_code = all_files.get("src/index.css", all_files.get("src/styles/App.css", ""))
        js_code = all_files.get("src/utils/helpers.js", "")
        react_code = all_files.get("src/App.jsx", all_files.get("src/main.jsx", ""))
        backend_code = all_files.get("main.py", all_files.get("server.js", ""))
        
        # Extraire les configs
        package_json = all_files.get("package.json", "")
        requirements_txt = all_files.get("requirements.txt", "")
        dockerfile = all_files.get("Dockerfile", "")
        readme = all_files.get("README.md", "")
        
        return {
            "html": html_code,
            "css": css_code,
            "js": js_code,
            "react": react_code,
            "backend": backend_code,
            "project_structure": {"files": list(all_files.keys())},
            "package_json": package_json,
            "requirements_txt": requirements_txt,
            "dockerfile": dockerfile,
            "readme": readme,
            "deployment_config": {},
            "all_files": all_files  # TOUS les fichiers générés
        }
        
    except Exception as e:
        logger.error(f"Erreur génération multi-fichiers: {str(e)}")
        # Fallback vers génération classique
        return await generate_app_code_basic(request.description, request.type, request.framework)


async def generate_app_code_advanced(request: GenerateAppRequest) -> dict:
    """GÉNÉRATEUR ULTRA-PUISSANT OPTIMISÉ - Génère des applications complètes rapidement"""
    try:
        if request.advanced_mode:
            # MODE AVANCÉ: Utiliser le nouveau générateur multi-fichiers
            logger.info("Mode avancé activé - Génération multi-fichiers complète")
            return await generate_complete_multifile_project(request)
        else:
            # MODE RAPIDE: Génération basique (compatibilité)
            return await generate_app_code_basic(request.description, request.type, request.framework)
            
    except Exception as e:
        logger.error(f"Error in advanced generation: {str(e)}")
        # Fallback vers génération basique TOUJOURS
        return await generate_app_code_basic(request.description, request.type, request.framework)

async def generate_advanced_optimized(request: GenerateAppRequest) -> dict:
    """Génération avancée optimisée avec timeout et structure intelligente"""
    try:
        # Génération concurrente optimisée
        tasks = []
        
        # Task 1: Fichier principal selon le framework
        if request.framework == "react":
            tasks.append(generate_react_component(request))
        elif request.framework in ["fastapi", "django", "flask"]:
            tasks.append(generate_backend_file(request))
        else:
            tasks.append(generate_html_file(request))
        
        # Task 2: Fichier CSS en parallèle
        tasks.append(generate_css_file(request))
        
        # Task 3: Configuration en parallèle
        tasks.append(generate_config_files(request))
        
        # Exécution concurrente avec timeout global de 15s
        results = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=15.0
        )
        
        # Traitement des résultats
        main_file = results[0] if len(results) > 0 and not isinstance(results[0], Exception) else ""
        css_content = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else ""
        config_content = results[2] if len(results) > 2 and not isinstance(results[2], Exception) else {}
        
        # Mapping intelligent selon le framework
        html_code = ""
        css_code = css_content
        js_code = ""
        react_code = ""
        backend_code = ""
        
        if request.framework == "react":
            react_code = main_file
            html_code = generate_basic_html_for_react(request)
        elif request.framework in ["fastapi", "django", "flask"]:
            backend_code = main_file
        else:
            html_code = main_file
        
        return {
            "html": html_code,
            "css": css_code,
            "js": js_code,
            "react": react_code,
            "backend": backend_code,
            # Configuration avancée
            "project_structure": config_content.get("structure", {}),
            "package_json": config_content.get("package_json", ""),
            "requirements_txt": config_content.get("requirements", ""),
            "dockerfile": config_content.get("dockerfile", ""),
            "readme": config_content.get("readme", ""),
            "deployment_config": config_content.get("deployment", {}),
            "all_files": {
                "main_file": main_file,
                "styles.css": css_content
            }
        }
        
    except asyncio.TimeoutError:
        logger.warning("Advanced generation timed out, falling back to basic mode")
        return await generate_app_code_basic(request.description, request.type, request.framework)
    except Exception as e:
        logger.error(f"Advanced generation failed: {str(e)}")
        return await generate_app_code_basic(request.description, request.type, request.framework)

async def generate_react_component(request: GenerateAppRequest) -> str:
    """Génère un composant React optimisé"""
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"react-{uuid.uuid4()}",
        system_message="Tu es un expert React. Génère UNIQUEMENT du code JSX, rien d'autre."
    ).with_model("openai", "gpt-4o")
    
    prompt = f"""Génère un composant React complet pour: {request.description}

Type: {request.type}
Features: {', '.join(request.features or [])}

EXIGENCES:
- Composant React moderne avec hooks
- Code prêt pour production
- Design responsive et accessible
- Fonctionnalités demandées incluses
- Gestion d'état avec useState/useEffect

Réponds UNIQUEMENT avec le code JSX, pas de markdown."""
    
    response = await chat.send_message(UserMessage(text=prompt))
    return response.strip().replace('```jsx', '').replace('```javascript', '').replace('```', '').strip()

async def generate_backend_file(request: GenerateAppRequest) -> str:
    """Génère un fichier backend optimisé"""
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"backend-{uuid.uuid4()}",
        system_message="Tu es un expert backend. Génère UNIQUEMENT du code Python, rien d'autre."
    ).with_model("openai", "gpt-4o")
    
    framework_name = {"fastapi": "FastAPI", "django": "Django", "flask": "Flask"}.get(request.framework, "FastAPI")
    
    prompt = f"""Génère une API {framework_name} complète pour: {request.description}

Type: {request.type}
Database: {request.database or 'mongodb'}
Features: {', '.join(request.features or [])}

EXIGENCES:
- API REST complète et fonctionnelle
- Modèles de données appropriés
- Endpoints CRUD essentiels
- Gestion d'erreurs et validation
- Configuration CORS
- Code prêt pour production

Réponds UNIQUEMENT avec le code Python, pas de markdown."""
    
    response = await chat.send_message(UserMessage(text=prompt))
    return response.strip().replace('```python', '').replace('```', '').strip()

async def generate_html_file(request: GenerateAppRequest) -> str:
    """Génère un fichier HTML optimisé"""
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"html-{uuid.uuid4()}",
        system_message="Tu es un expert HTML/CSS. Génère UNIQUEMENT du HTML, rien d'autre."
    ).with_model("openai", "gpt-4o")
    
    prompt = f"""Génère une page HTML complète pour: {request.description}

Type: {request.type}
Features: {', '.join(request.features or [])}

EXIGENCES:
- HTML5 sémantique et accessible
- Design moderne et responsive
- Fonctionnalités demandées incluses
- Optimisé pour le SEO
- Prêt pour production

Réponds UNIQUEMENT avec le code HTML complet, pas de markdown."""
    
    response = await chat.send_message(UserMessage(text=prompt))
    return response.strip().replace('```html', '').replace('```', '').strip()

async def generate_css_file(request: GenerateAppRequest) -> str:
    """Génère un fichier CSS optimisé"""
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"css-{uuid.uuid4()}",
        system_message="Tu es un expert CSS. Génère UNIQUEMENT du CSS, rien d'autre."
    ).with_model("openai", "gpt-4o")
    
    prompt = f"""Génère des styles CSS complets pour: {request.description}

Type: {request.type}
Framework: {request.framework}

EXIGENCES:
- CSS moderne et responsive
- Design professionnel et attrayant
- Animations et transitions fluides
- Compatible avec tous navigateurs
- Performance optimisée
- Mobile-first approach

Réponds UNIQUEMENT avec le code CSS, pas de markdown."""
    
    response = await chat.send_message(UserMessage(text=prompt))
    return response.strip().replace('```css', '').replace('```', '').strip()

async def generate_config_files(request: GenerateAppRequest) -> dict:
    """Génère les fichiers de configuration en parallèle"""
    config = {}
    
    # Structure du projet
    if request.framework == "react":
        config["structure"] = {
            "src/App.jsx": "Composant principal React",
            "src/index.js": "Point d'entrée",
            "public/index.html": "HTML template",
            "src/styles/App.css": "Styles principaux",
            "package.json": "Configuration npm"
        }
        config["package_json"] = json.dumps({
            "name": f"vectort-{request.type}",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "axios": "^1.6.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build"
            }
        }, indent=2)
    elif request.framework in ["fastapi", "django", "flask"]:
        config["requirements"] = "fastapi==0.104.1\nuvicorn==0.24.0\npydantic==2.5.0"
        config["structure"] = {
            "main.py": "Application principale",
            "models.py": "Modèles de données",
            "requirements.txt": "Dépendances Python"
        }
    
    # Dockerfile simple
    config["dockerfile"] = "FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nEXPOSE 8000"
    
    # README
    config["readme"] = f"# {request.description}\n\nApplication générée par Vectort.io\n\n## Installation\n\n```bash\nnpm install\nnpm start\n```"
    
    return config

def generate_basic_html_for_react(request: GenerateAppRequest) -> str:
    """Génère un HTML de base pour React"""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{request.type.replace('_', ' ').title()}</title>
</head>
<body>
    <div id="root"></div>
    <script src="/static/js/bundle.js"></script>
</body>
</html>"""

async def generate_app_code_basic(description: str, app_type: str, framework: str) -> dict:
    """Génération basique pour compatibilité"""
    try:
        # Initialize LLM Chat
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"vectort-basic-{uuid.uuid4()}",
            system_message=f"""Tu es un développeur expert qui génère du code de production de haute qualité.
            
            Génère une application {app_type} en {framework} basée sur la description fournie.
            
            REQUIREMENTS:
            - Code propre, moderne et optimisé
            - Design responsive et accessible 
            - Fonctionnalités complètes et pratiques
            - Prêt pour la production
            - Utilise les meilleures pratiques
            
            FORMAT DE RÉPONSE:
            Réponds UNIQUEMENT avec un JSON dans ce format exact:
            {{
                "html": "code HTML complet si applicable",
                "css": "code CSS complet avec design moderne",
                "js": "code JavaScript complet si applicable", 
                "react": "code React JSX complet si framework=react",
                "backend": "code backend API si nécessaire (FastAPI/Node.js)"
            }}
            
            N'inclus AUCUN texte en dehors du JSON."""
        ).with_model("openai", "gpt-4o")
        
        # Create user message
        user_message = UserMessage(
            text=f"Génère une application {app_type} en {framework}:\n\n{description}\n\nGénère du code complet et fonctionnel prêt pour la production."
        )
        
        # Send message and get response
        response = await chat.send_message(user_message)
        
        # Parse JSON response
        import json
        try:
            # Extract JSON from response
            response_text = response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
                
            code_data = json.loads(response_text)
            return code_data
            
        except json.JSONDecodeError:
            # Fallback: create basic structure
            return {
                "html": f"<!DOCTYPE html><html><head><title>Generated App</title></head><body><h1>Application générée</h1><p>{description}</p></body></html>",
                "css": "body { font-family: Arial, sans-serif; margin: 20px; }",
                "js": "console.log('Application générée avec succès');",
                "react": None,
                "backend": None
            }
            
    except Exception as e:
        logger.error(f"Error generating basic app code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la génération du code"
        )


# Routes
@api_router.get("/")
async def root():
    return {"message": "Vectort API - AI-powered application generation"}

# Authentication routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        full_name=user_data.full_name
    )
    
    user_dict = user.dict()
    user_dict["password_hash"] = hashed_password
    
    await db.users.insert_one(user_dict)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user
    )

@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    # Find user
    user_doc = await db.users.find_one({"email": user_data.email})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(user_data.password, user_doc["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    user = User(**{k: v for k, v in user_doc.items() if k != "password_hash"})
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user
    )

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Project routes
@api_router.get("/projects", response_model=List[Project])
async def get_projects(current_user: User = Depends(get_current_user)):
    projects = await db.projects.find({"user_id": current_user.id}).sort("created_at", -1).to_list(1000)
    return [Project(**project) for project in projects]

@api_router.post("/projects", response_model=Project)
async def create_project(project_data: ProjectCreate, current_user: User = Depends(get_current_user)):
    project = Project(
        **project_data.dict(),
        user_id=current_user.id
    )
    
    await db.projects.insert_one(project.dict())
    
    return project

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str, current_user: User = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return Project(**project)

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: str, 
    project_data: ProjectUpdate, 
    current_user: User = Depends(get_current_user)
):
    project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    update_data = {k: v for k, v in project_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.projects.update_one(
        {"id": project_id, "user_id": current_user.id},
        {"$set": update_data}
    )
    
    updated_project = await db.projects.find_one({"id": project_id})
    return Project(**updated_project)

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str, current_user: User = Depends(get_current_user)):
    result = await db.projects.delete_one({"id": project_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return {"success": True}

# Statistics routes
@api_router.get("/stats", response_model=Stats)
async def get_stats():
    # Get real stats from database
    total_users = await db.users.count_documents({})
    total_projects = await db.projects.count_documents({})
    
    # Format numbers
    users = f"{total_users:,}+" if total_users > 0 else "1.5M+"
    apps = f"{total_projects:,}+" if total_projects > 0 else "2M+"
    
    return Stats(
        users=users,
        apps=apps,
        countries="180+"
    )

@api_router.get("/users/stats", response_model=UserStats)
async def get_user_stats(current_user: User = Depends(get_current_user)):
    total_projects = await db.projects.count_documents({"user_id": current_user.id})
    active_projects = await db.projects.count_documents({
        "user_id": current_user.id,
        "status": {"$in": ["building", "completed"]}
    })
    
    return UserStats(
        totalProjects=total_projects,
        activeProjects=active_projects,
        totalViews=total_projects * 42  # Mock calculation
    )

# AI Code Generation routes
@api_router.post("/projects/{project_id}/generate", response_model=GeneratedApp)
async def generate_project_code(
    project_id: str, 
    request: GenerateAppRequest,
    current_user: User = Depends(get_current_user)
):
    # Verify project ownership
    project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Calculer le coût en crédits selon le mode
    credit_cost = 2 if not request.advanced_mode else 4  # Quick: 2, Advanced: 4
    
    # Vérifier et déduire les crédits AVANT la génération
    user_credits = await get_user_credit_balance(current_user.id)
    if user_credits.total_available < credit_cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Crédits insuffisants. Vous avez {user_credits.total_available} crédits, {credit_cost} requis. Veuillez recharger vos crédits."
        )
    
    # Déduire les crédits
    deduction_success = await deduct_credits(
        current_user.id, 
        credit_cost, 
        f"Génération {'avancée' if request.advanced_mode else 'rapide'} - {request.type}",
        project_id
    )
    
    if not deduction_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la déduction des crédits"
        )
    
    # Update project status
    await db.projects.update_one(
        {"id": project_id},
        {"$set": {"status": "building", "updated_at": datetime.utcnow()}}
    )
    
    try:
        # Generate code using ADVANCED AI
        code_data = await generate_app_code_advanced(request)
        
        # Create generated app record with ADVANCED features
        generated_app = GeneratedApp(
            project_id=project_id,
            html_code=code_data.get("html"),
            css_code=code_data.get("css"),
            js_code=code_data.get("js"),
            react_code=code_data.get("react"),
            backend_code=code_data.get("backend"),
            # NOUVEAUX CHAMPS AVANCÉS
            project_structure=code_data.get("project_structure"),
            package_json=code_data.get("package_json"),
            requirements_txt=code_data.get("requirements_txt"),
            dockerfile=code_data.get("dockerfile"),
            readme=code_data.get("readme"),
            deployment_config=code_data.get("deployment_config"),
            all_files=code_data.get("all_files")
        )
        
        # Save to database
        await db.generated_apps.insert_one(generated_app.dict())
        
        # Update project status to completed
        await db.projects.update_one(
            {"id": project_id},
            {"$set": {"status": "completed", "updated_at": datetime.utcnow()}}
        )
        
        logger.info(f"Génération réussie pour le projet {project_id}. {credit_cost} crédits déduits.")
        
        return generated_app
        
    except Exception as e:
        # En cas d'erreur, rembourser les crédits
        await add_credits(
            current_user.id,
            credit_cost,
            "refund",
            f"Remboursement - Erreur de génération pour {project_id}"
        )
        logger.error(f"Erreur de génération, {credit_cost} crédits remboursés à l'utilisateur {current_user.id}")
        
        # Update project status to error
        await db.projects.update_one(
            {"id": project_id},
            {"$set": {"status": "error", "updated_at": datetime.utcnow()}}
        )
        raise e

@api_router.get("/projects/{project_id}/code", response_model=GeneratedApp)
async def get_project_code(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    # Verify project ownership
    project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get generated code
    generated_app = await db.generated_apps.find_one({"project_id": project_id})
    if not generated_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated code not found"
        )
    
    return GeneratedApp(**generated_app)

@api_router.get("/projects/{project_id}/preview")
async def preview_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Return HTML preview of the generated application"""
    # Verify project ownership
    project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get generated code
    generated_app = await db.generated_apps.find_one({"project_id": project_id})
    if not generated_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated code not found"
        )
    
    # Get code from generated_app
    html = generated_app.get("html_code", "")
    css = generated_app.get("css_code", "")
    js = generated_app.get("js_code", "")
    react_code = generated_app.get("react_code", "")
    
    # Si html_code est vide mais react_code existe, créer un preview React
    if not html and react_code:
        # Créer un preview HTML qui monte l'application React
        preview_html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aperçu - {project.get('title', 'Application générée')}</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <style>
    {css}
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
    {react_code}
    
    // Mount the React component
    const root = ReactDOM.createRoot(document.getElementById('root'));
    
    // Try to find the default export or the main component
    if (typeof ProjectManagementApp !== 'undefined') {{
        root.render(<ProjectManagementApp />);
    }} else if (typeof App !== 'undefined') {{
        root.render(<App />);
    }} else {{
        // Fallback: try to render the first React component found
        root.render(<div><h1>Application générée</h1><p>Le composant React a été généré avec succès.</p></div>);
    }}
    </script>
</body>
</html>
        """
    else:
        # Preview HTML classique avec HTML/CSS/JS
        # Nettoyer le HTML des balises dupliquées
        clean_html = html
        if html:
            # Supprimer les balises wrapper si elles existent
            import re
            clean_html = re.sub(r'<html[^>]*>|</html>|<head[^>]*>|</head>|<body[^>]*>|</body>', '', html, flags=re.IGNORECASE)
        
        preview_html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aperçu - {project.get('title', 'Application générée')}</title>
    <style>
    {css}
    </style>
</head>
<body>
    {clean_html if clean_html else '<div style="padding: 20px;"><h1>Application générée</h1><p>Contenu en cours de génération...</p></div>'}
    <script>
    {js}
    </script>
</body>
</html>
        """
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=preview_html)


@api_router.get("/projects/{project_id}/export/zip")
async def export_project_zip(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Export le projet généré en ZIP téléchargeable"""
    # Verify project ownership
    project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get generated code
    generated_app = await db.generated_apps.find_one({"project_id": project_id})
    if not generated_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated code not found. Please generate the project first."
        )
    
    # Créer le ZIP avec l'exporter
    from exporters.zip_exporter import ZipExporter
    exporter = ZipExporter()
    
    # Déterminer le framework depuis le projet
    framework = project.get('framework', 'react')
    
    # Créer l'archive ZIP
    zip_buffer = await exporter.create_project_zip(
        project_title=project.get('title', 'Vectort Project'),
        generated_code=generated_app,
        framework=framework,
        include_config=True
    )
    
    # Préparer le nom du fichier
    from exporters.zip_exporter import ZipExporter
    temp_exporter = ZipExporter()
    safe_name = temp_exporter._sanitize_project_name(project.get('title', 'project'))
    filename = f"{safe_name}.zip"
    
    # Retourner le ZIP
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


# ============================================
# ENDPOINTS EXPORT GITHUB
# ============================================

@api_router.post("/projects/{project_id}/export/github")
async def export_project_to_github(
    project_id: str,
    github_token: str,
    repo_name: Optional[str] = None,
    private: bool = False,
    current_user: User = Depends(get_current_user)
):
    """
    Exporte le projet vers un nouveau repository GitHub
    
    Requiert un token GitHub avec les permissions 'repo'
    """
    # Verify project ownership
    project = await db.projects.find_one({"id": project_id, "user_id": current_user.id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get generated code
    generated_app = await db.generated_apps.find_one({"project_id": project_id})
    if not generated_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated code not found. Please generate the project first."
        )
    
    try:
        from exporters.github_exporter import GitHubExporter
        
        exporter = GitHubExporter(github_token=github_token)
        
        # Utiliser le nom du projet ou le repo_name fourni
        project_title = repo_name or project.get('title', 'Vectort Project')
        description = project.get('description', 'Generated by Vectort.io')
        
        # Créer et pusher vers GitHub
        result = await exporter.create_and_push_project(
            project_title=project_title,
            description=description,
            generated_code=generated_app,
            private=private
        )
        
        if result.get("success"):
            # Sauvegarder l'URL GitHub dans le projet
            await db.projects.update_one(
                {"id": project_id},
                {"$set": {"github_url": result["repo_url"]}}
            )
            
            return {
                "success": True,
                "message": "Projet exporté vers GitHub avec succès !",
                "repo_url": result["repo_url"],
                "clone_url": result["clone_url"],
                "files_pushed": len(result["files_pushed"]),
                "files_failed": len(result["files_failed"])
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de l'export GitHub: {result.get('error')}"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'export GitHub: {str(e)}"
        )


@api_router.get("/github/user")
async def get_github_user_info(
    github_token: str,
    current_user: User = Depends(get_current_user)
):
    """Récupère les informations de l'utilisateur GitHub"""
    try:
        from exporters.github_exporter import GitHubExporter
        
        exporter = GitHubExporter(github_token=github_token)
        user_info = await exporter.get_user_info()
        
        return {
            "success": True,
            "username": user_info.get("login"),
            "name": user_info.get("name"),
            "avatar_url": user_info.get("avatar_url"),
            "public_repos": user_info.get("public_repos"),
            "followers": user_info.get("followers")
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token GitHub invalide: {str(e)}"
        )


# ============================================
# ENDPOINTS SYSTÈME DE CRÉDITS ET PAIEMENTS
# ============================================

@api_router.get("/credits/balance", response_model=CreditBalance)
async def get_credit_balance(current_user: User = Depends(get_current_user)):
    """Récupère le solde de crédits de l'utilisateur"""
    return await get_user_credit_balance(current_user.id)

@api_router.get("/credits/packages", response_model=List[CreditPackage])
async def get_credit_packages():
    """Récupère la liste des packages de crédits disponibles"""
    return list(CREDIT_PACKAGES.values())

@api_router.post("/credits/purchase", response_model=CheckoutSessionResponse)
async def purchase_credits(
    purchase_request: PurchaseRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user)
):
    """Crée une session de checkout Stripe pour l'achat de crédits"""
    
    # Valider le package
    if purchase_request.package_id not in CREDIT_PACKAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Package invalide. Packages disponibles: {', '.join(CREDIT_PACKAGES.keys())}"
        )
    
    package = CREDIT_PACKAGES[purchase_request.package_id]
    
    # Initialiser Stripe Checkout
    webhook_url = f"{purchase_request.origin_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    # Créer les URLs de succès et d'annulation
    success_url = f"{purchase_request.origin_url}/dashboard?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{purchase_request.origin_url}/dashboard?payment=cancelled"
    
    # Préparer la requête de checkout
    checkout_request = CheckoutSessionRequest(
        amount=package.price,
        currency=package.currency,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": current_user.id,
            "package_id": package.id,
            "credits": str(package.credits),
            "user_email": current_user.email
        }
    )
    
    # Créer la session Stripe
    try:
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Enregistrer la transaction dans la base de données
        payment_transaction = PaymentTransaction(
            user_id=current_user.id,
            session_id=session.session_id,
            amount=package.price,
            currency=package.currency,
            credits=package.credits,
            package_id=package.id,
            payment_status="pending",
            status="initiated",
            metadata={
                "user_email": current_user.email,
                "package_name": package.name
            }
        )
        
        await db.payment_transactions.insert_one(payment_transaction.dict())
        
        logger.info(f"Session de paiement créée pour l'utilisateur {current_user.id}: {session.session_id}")
        
        return session
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de la session Stripe: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de la session de paiement"
        )

@api_router.get("/checkout/status/{session_id}", response_model=CheckoutStatusResponse)
async def get_checkout_status(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Vérifie le statut d'une session de checkout Stripe"""
    
    # Vérifier que la transaction appartient à l'utilisateur
    transaction = await db.payment_transactions.find_one({
        "session_id": session_id,
        "user_id": current_user.id
    })
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction non trouvée"
        )
    
    # Si déjà traitée, retourner le statut depuis la DB
    if transaction.get("payment_status") == "paid":
        return CheckoutStatusResponse(
            status="complete",
            payment_status="paid",
            amount_total=int(transaction.get("amount") * 100),  # Convertir en centimes
            currency=transaction.get("currency"),
            metadata=transaction.get("metadata", {})
        )
    
    # Sinon, vérifier auprès de Stripe
    try:
        # Initialiser Stripe (webhook_url n'est pas nécessaire ici)
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        checkout_status = await stripe_checkout.get_checkout_status(session_id)
        
        # Si le paiement est réussi et pas encore traité
        if checkout_status.payment_status == "paid" and transaction.get("payment_status") != "paid":
            # Mettre à jour la transaction
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "payment_status": "paid",
                        "status": "completed",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Ajouter les crédits à l'utilisateur
            credits_to_add = transaction.get("credits", 0)
            await add_credits(
                current_user.id,
                credits_to_add,
                "purchase",
                f"Achat de {credits_to_add} crédits - Package {transaction.get('package_id')}"
            )
            
            logger.info(f"Paiement confirmé pour {current_user.id}: +{credits_to_add} crédits")
        
        return checkout_status
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du statut Stripe: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la vérification du statut de paiement"
        )

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Webhook pour recevoir les événements Stripe"""
    
    try:
        # Lire le corps de la requête
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        if not signature:
            raise HTTPException(status_code=400, detail="Signature Stripe manquante")
        
        # Initialiser Stripe
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        
        # Traiter le webhook
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        logger.info(f"Webhook Stripe reçu: {webhook_response.event_type} - {webhook_response.session_id}")
        
        # Traiter selon le type d'événement
        if webhook_response.event_type == "checkout.session.completed" and webhook_response.payment_status == "paid":
            session_id = webhook_response.session_id
            metadata = webhook_response.metadata
            
            # Trouver la transaction
            transaction = await db.payment_transactions.find_one({"session_id": session_id})
            
            if transaction and transaction.get("payment_status") != "paid":
                user_id = metadata.get("user_id")
                credits = int(metadata.get("credits", 0))
                
                # Mettre à jour la transaction
                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {
                        "$set": {
                            "payment_status": "paid",
                            "status": "completed",
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                # Ajouter les crédits
                await add_credits(
                    user_id,
                    credits,
                    "purchase",
                    f"Achat de {credits} crédits via webhook"
                )
                
                logger.info(f"Webhook traité: +{credits} crédits ajoutés à {user_id}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Erreur webhook Stripe: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/credits/history", response_model=List[CreditTransaction])
async def get_credit_history(
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    """Récupère l'historique des transactions de crédits"""
    transactions = await db.credit_transactions.find(
        {"user_id": current_user.id}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    return [CreditTransaction(**t) for t in transactions]


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # À restreindre en production
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Middleware de sécurité
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    # En-têtes de sécurité
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_db():
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index([("provider", 1), ("provider_id", 1)])
    await db.projects.create_index("user_id")
    await db.projects.create_index("created_at")
    logger.info("Database indexes created")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Database connection closed")