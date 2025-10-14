"""
VECTORT.IO ADVANCED CODE GENERATOR
Le générateur de code le plus puissant au monde
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import asyncio
import json
from dataclasses import dataclass
from emergentintegrations.llm.chat import LlmChat, UserMessage

class ProjectType(Enum):
    # Applications Web
    WEB_APP = "web_app"
    ECOMMERCE = "ecommerce"
    E_COMMERCE = "ecommerce"  # Alias pour compatibilité
    SOCIAL_MEDIA = "social_media"
    BLOG_CMS = "blog_cms"
    PORTFOLIO = "portfolio"
    LANDING_PAGE = "landing_page"
    DASHBOARD = "dashboard"
    SAAS_PLATFORM = "saas_platform"
    
    # Applications Mobile
    MOBILE_APP = "mobile_app"
    PWA = "pwa"
    REACT_NATIVE = "react_native"
    FLUTTER_APP = "flutter_app"
    
    # Backend & API
    REST_API = "rest_api"
    GRAPHQL_API = "graphql_api"
    MICROSERVICES = "microservices"
    WEBSOCKET_SERVER = "websocket_server"
    
    # Desktop
    ELECTRON_APP = "electron_app"
    DESKTOP_APP = "desktop_app"
    
    # Blockchain & Web3
    SMART_CONTRACT = "smart_contract"
    DAPP = "dapp"
    NFT_MARKETPLACE = "nft_marketplace"
    
    # Gaming
    BROWSER_GAME = "browser_game"
    MOBILE_GAME = "mobile_game"
    
    # AI & Data
    ML_MODEL = "ml_model"
    DATA_PIPELINE = "data_pipeline"
    CHATBOT = "chatbot"
    
    # DevOps & Tools
    CLI_TOOL = "cli_tool"
    AUTOMATION_SCRIPT = "automation_script"
    CHROME_EXTENSION = "chrome_extension"

class Framework(Enum):
    # Frontend
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    SVELTE = "svelte"
    NEXT_JS = "nextjs"
    NUXT = "nuxt"
    VANILLA_JS = "vanilla"
    
    # Backend
    FASTAPI = "fastapi"
    DJANGO = "django"
    FLASK = "flask"
    EXPRESS = "express"
    NEST_JS = "nestjs"
    SPRING_BOOT = "spring_boot"
    LARAVEL = "laravel"
    RUBY_RAILS = "ruby_rails"
    
    # Mobile
    REACT_NATIVE = "react_native"
    FLUTTER = "flutter"
    IONIC = "ionic"
    
    # Desktop
    ELECTRON = "electron"
    TAURI = "tauri"
    
    # Blockchain
    SOLIDITY = "solidity"
    WEB3_JS = "web3js"
    ETHERS_JS = "ethers"

class DatabaseType(Enum):
    MONGODB = "mongodb"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    REDIS = "redis"
    FIREBASE = "firebase"
    SUPABASE = "supabase"
    PRISMA = "prisma"

@dataclass
class GenerationRequest:
    description: str
    project_type: ProjectType
    framework: Framework
    database: Optional[DatabaseType] = None
    features: List[str] = None
    integrations: List[str] = None
    deployment_target: str = "vercel"
    ai_model: str = "gpt-4o"

@dataclass
class GeneratedCode:
    project_structure: Dict[str, str]
    main_files: Dict[str, str]
    package_json: Optional[str] = None
    requirements_txt: Optional[str] = None
    dockerfile: Optional[str] = None
    readme: str = ""
    deployment_config: Dict[str, Any] = None

class AdvancedCodeGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.specialized_prompts = {
            ProjectType.ECOMMERCE: self._get_ecommerce_prompt(),
            ProjectType.SOCIAL_MEDIA: self._get_social_media_prompt(),
            ProjectType.SAAS_PLATFORM: self._get_saas_prompt(),
            ProjectType.SMART_CONTRACT: self._get_blockchain_prompt(),
            ProjectType.ML_MODEL: self._get_ml_prompt(),
            ProjectType.MOBILE_GAME: self._get_game_prompt(),
        }
    
    async def generate_complete_application(self, request: GenerationRequest) -> GeneratedCode:
        """Génère une application complète avec tous les fichiers nécessaires"""
        
        # 1. Génération de l'architecture
        architecture = await self._generate_architecture(request)
        
        # 2. Génération des fichiers principaux
        main_files = await self._generate_main_files(request, architecture)
        
        # 3. Génération des configurations
        configs = await self._generate_configurations(request)
        
        # 4. Génération du README et documentation
        readme = await self._generate_documentation(request, architecture)
        
        return GeneratedCode(
            project_structure=architecture,
            main_files=main_files,
            package_json=configs.get("package_json"),
            requirements_txt=configs.get("requirements"),
            dockerfile=configs.get("dockerfile"),
            readme=readme,
            deployment_config=configs.get("deployment")
        )
    
    async def _generate_architecture(self, request: GenerationRequest) -> Dict[str, str]:
        """Génère l'architecture complète du projet"""
        chat = LlmChat(
            api_key=self.api_key, 
            session_id=f"arch-{request.project_type.value}",
            system_message="Tu es un architecte logiciel expert spécialisé dans la génération de code."
        )
        
        system_prompt = f"""
        Tu es un architecte logiciel expert. Génère une structure de projet complète et professionnelle.
        
        PROJET: {request.project_type.value} avec {request.framework.value}
        DESCRIPTION: {request.description}
        
        Crée une structure de fichiers/dossiers COMPLÈTE avec:
        - Structure moderne et best practices
        - Séparation des responsabilités
        - Configuration pour production
        - Tests inclus
        - Documentation
        
        Réponds UNIQUEMENT avec un JSON valide:
        {{
            "structure": {{
                "dossier/fichier.ext": "description du fichier",
                ...
            }}
        }}
        """
        
        response = await chat.with_model("openai", "gpt-4o").send_message(
            UserMessage(text=system_prompt)
        )
        
        try:
            parsed = json.loads(response)
            if "structure" in parsed:
                return parsed["structure"]
            else:
                return parsed  # Si la réponse est directement la structure
        except Exception as e:
            # Fallback avec structure de base selon le framework
            return self._get_default_structure(request)
    
    async def _generate_main_files(self, request: GenerationRequest, architecture: Dict) -> Dict[str, str]:
        """Génère le contenu de tous les fichiers principaux"""
        files = {}
        
        # Sélectionner les fichiers les plus importants d'abord
        priority_files = []
        for file_path in list(architecture.keys())[:8]:  # Limite réduite
            if self._should_generate_file(file_path):
                priority_files.append((file_path, architecture[file_path]))
        
        # Génération séquentielle pour éviter les timeouts
        for file_path, file_desc in priority_files[:5]:  # Encore plus limité
            try:
                content = await asyncio.wait_for(
                    self._generate_single_file(request, file_path, file_desc),
                    timeout=15.0  # Timeout par fichier
                )
                files[file_path] = content
                
                # Ajouter un délai entre les générations pour éviter le rate limiting
                await asyncio.sleep(0.5)
                
            except asyncio.TimeoutError:
                files[file_path] = f"// Timeout lors de la génération de {file_path}"
            except Exception as e:
                files[file_path] = f"// Erreur de génération: {str(e)}"
        
        # S'assurer qu'on a au moins les fichiers de base
        if not files:
            files = await self._generate_basic_files(request)
        
        return files
    
    async def _generate_basic_files(self, request: GenerationRequest) -> Dict[str, str]:
        """Génère les fichiers de base en cas d'échec de la génération avancée"""
        basic_files = {}
        
        if request.framework.value in ['react', 'vue', 'angular']:
            basic_files["App.jsx"] = await self._generate_basic_react_app(request)
            basic_files["index.html"] = await self._generate_basic_html(request)
            basic_files["styles.css"] = await self._generate_basic_css(request)
        elif request.framework.value in ['fastapi', 'django', 'flask']:
            basic_files["main.py"] = await self._generate_basic_backend(request)
        
        return basic_files
    
    async def _generate_basic_react_app(self, request: GenerationRequest) -> str:
        """Génère un composant React de base"""
        return f"""
import React from 'react';
import './styles.css';

function App() {{
  return (
    <div className="app">
      <header className="app-header">
        <h1>{request.project_type.value.replace('_', ' ').title()}</h1>
        <p>{request.description[:200]}...</p>
      </header>
      <main className="app-main">
        <p>Application générée par Vectort.io</p>
        <p>Prête à être personnalisée selon vos besoins.</p>
      </main>
    </div>
  );
}}

export default App;
"""
    
    async def _generate_basic_html(self, request: GenerationRequest) -> str:
        """Génère un HTML de base"""
        return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{request.project_type.value.replace('_', ' ').title()}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="root">
        <h1>{request.project_type.value.replace('_', ' ').title()}</h1>
        <p>{request.description[:200]}...</p>
        <p>Application générée par Vectort.io - Prête pour la production!</p>
    </div>
    <script src="main.js"></script>
</body>
</html>
"""
    
    async def _generate_basic_css(self, request: GenerationRequest) -> str:
        """Génère un CSS de base"""
        return """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f4f4f4;
}

.app, #root {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.app-header {
    text-align: center;
    margin-bottom: 2rem;
    padding: 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
}

.app-main {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

p {
    margin-bottom: 1rem;
    font-size: 1.1rem;
}
"""
    
    async def _generate_basic_backend(self, request: GenerationRequest) -> str:
        """Génère un backend de base"""
        return f"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="{request.project_type.value.replace('_', ' ').title()}")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {{
        "message": "API générée par Vectort.io",
        "project_type": "{request.project_type.value}",
        "description": "{request.description[:100]}..."
    }}

@app.get("/health")
async def health_check():
    return {{"status": "healthy"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
    
    async def _generate_single_file(self, request: GenerationRequest, file_path: str, file_desc: str) -> str:
        """Génère le contenu d'un fichier spécifique"""
        chat = LlmChat(
            api_key=self.api_key, 
            session_id=f"file-{hash(file_path)}",
            system_message="Tu es un développeur expert spécialisé dans la génération de fichiers de code."
        )
        
        # Prompt spécialisé selon le type de fichier
        specialized_prompt = self._get_specialized_prompt(request.project_type)
        
        system_prompt = f"""
        {specialized_prompt}
        
        Génère le contenu COMPLET et FONCTIONNEL pour ce fichier:
        
        FICHIER: {file_path}
        DESCRIPTION: {file_desc}
        PROJET: {request.description}
        FRAMEWORK: {request.framework.value}
        
        EXIGENCES:
        - Code de production prêt à déployer
        - Best practices et patterns modernes
        - Gestion d'erreurs complète
        - TypeScript si applicable
        - Comments et documentation
        - Optimisations de performance
        
        Réponds UNIQUEMENT avec le code, aucun markdown.
        """
        
        response = await chat.with_model("openai", "gpt-4o").send_message(
            UserMessage(text=system_prompt)
        )
        
        return response.strip()
    
    def _should_generate_file(self, file_path: str) -> bool:
        """Détermine si un fichier doit être généré (évite les fichiers binaires)"""
        excluded_extensions = ['.png', '.jpg', '.gif', '.ico', '.svg', '.pdf']
        excluded_dirs = ['node_modules', '.git', 'dist', 'build']
        
        return (
            not any(file_path.endswith(ext) for ext in excluded_extensions) and
            not any(dir_name in file_path for dir_name in excluded_dirs) and
            len(file_path.split('/')) <= 4  # Éviter les structures trop profondes
        )
    
    def _get_specialized_prompt(self, project_type: ProjectType) -> str:
        """Retourne un prompt spécialisé selon le type de projet"""
        return self.specialized_prompts.get(project_type, self._get_default_prompt())
    
    def _get_ecommerce_prompt(self) -> str:
        return """
        Tu es un expert en e-commerce. Génère du code pour une plateforme e-commerce moderne avec:
        - Catalogue de produits avec recherche et filtres
        - Panier d'achat et checkout sécurisé
        - Système de paiement (Stripe/PayPal)
        - Gestion des commandes et livraisons
        - Interface admin complète
        - Optimisations SEO et performance
        """
    
    def _get_social_media_prompt(self) -> str:
        return """
        Tu es un expert en réseaux sociaux. Génère du code pour une plateforme sociale avec:
        - Système d'authentification et profils
        - Timeline et feed en temps réel
        - Système de posts, likes, commentaires
        - Messagerie instantanée
        - Notifications push
        - Modération de contenu
        """
    
    def _get_saas_prompt(self) -> str:
        return """
        Tu es un expert SaaS. Génère du code pour une plateforme SaaS avec:
        - Multi-tenant architecture
        - Système d'abonnements et facturation
        - Dashboard analytics avancé
        - API rate limiting
        - Système de permissions granulaires
        - Intégrations webhooks
        """
    
    def _get_blockchain_prompt(self) -> str:
        return """
        Tu es un expert blockchain. Génère du code pour:
        - Smart contracts sécurisés (Solidity)
        - Interface DApp (Web3.js/Ethers.js)
        - Connexion wallet (MetaMask, WalletConnect)
        - Tests automatisés pour contracts
        - Déploiement multi-réseaux
        """
    
    def _get_ml_prompt(self) -> str:
        return """
        Tu es un expert ML/AI. Génère du code pour:
        - Pipeline de données automatisé
        - Modèles d'entraînement et inférence
        - API de prédiction FastAPI
        - Monitoring des modèles
        - Interface de visualisation
        """
    
    def _get_game_prompt(self) -> str:
        return """
        Tu es un expert en développement de jeux. Génère du code pour:
        - Game engine avec canvas/WebGL
        - Système de physique
        - Audio et animations
        - Système de score et leaderboard
        - Multijoueur en temps réel
        """
    
    def _get_default_prompt(self) -> str:
        return """
        Tu es un développeur full-stack expert. Génère du code moderne, propre et fonctionnel
        suivant les meilleures pratiques de l'industrie.
        """
    
    async def _generate_configurations(self, request: GenerationRequest) -> Dict[str, str]:
        """Génère tous les fichiers de configuration nécessaires"""
        configs = {}
        
        # Package.json pour les projets JS/TS
        if request.framework.value in ['react', 'vue', 'angular', 'nextjs', 'express', 'nestjs']:
            configs["package_json"] = await self._generate_package_json(request)
        
        # Requirements.txt pour Python
        if request.framework.value in ['fastapi', 'django', 'flask']:
            configs["requirements"] = await self._generate_requirements_txt(request)
        
        # Dockerfile
        configs["dockerfile"] = await self._generate_dockerfile(request)
        
        # Configuration de déploiement
        configs["deployment"] = await self._generate_deployment_config(request)
        
        return configs
    
    async def _generate_package_json(self, request: GenerationRequest) -> str:
        """Génère un package.json optimisé"""
        # Logique de génération du package.json
        return json.dumps({
            "name": "vectort-generated-app",
            "version": "1.0.0",
            "description": request.description[:100],
            "dependencies": self._get_dependencies(request.framework),
            "scripts": self._get_scripts(request.framework),
            "devDependencies": self._get_dev_dependencies(request.framework)
        }, indent=2)
    
    async def _generate_requirements_txt(self, request: GenerationRequest) -> str:
        """Génère requirements.txt pour Python"""
        base_deps = []
        
        if request.framework == Framework.FASTAPI:
            base_deps = [
                "fastapi==0.104.1",
                "uvicorn[standard]==0.24.0",
                "pydantic==2.5.0",
                "sqlalchemy==2.0.23",
                "alembic==1.12.1"
            ]
        elif request.framework == Framework.DJANGO:
            base_deps = [
                "Django==4.2.7",
                "djangorestframework==3.14.0",
                "django-cors-headers==4.3.1",
                "celery==5.3.4"
            ]
        
        if request.database == DatabaseType.POSTGRESQL:
            base_deps.append("psycopg2-binary==2.9.9")
        elif request.database == DatabaseType.MONGODB:
            base_deps.append("motor==3.3.1")
        
        return "\n".join(base_deps)
    
    async def _generate_dockerfile(self, request: GenerationRequest) -> str:
        """Génère un Dockerfile optimisé"""
        if request.framework.value in ['react', 'vue', 'angular']:
            return self._get_frontend_dockerfile()
        elif request.framework.value in ['fastapi', 'django', 'flask']:
            return self._get_python_dockerfile()
        elif request.framework.value in ['express', 'nestjs']:
            return self._get_node_dockerfile()
        else:
            return self._get_generic_dockerfile()
    
    async def _generate_deployment_config(self, request: GenerationRequest) -> Dict[str, Any]:
        """Génère la configuration de déploiement"""
        return {
            "vercel": self._get_vercel_config(request),
            "docker": self._get_docker_compose(request),
            "kubernetes": self._get_k8s_config(request)
        }
    
    async def _generate_documentation(self, request: GenerationRequest, architecture: Dict) -> str:
        """Génère une documentation complète"""
        chat = LlmChat(
            api_key=self.api_key, 
            session_id="docs",
            system_message="Tu es un expert en documentation technique."
        )
        
        prompt = f"""
        Génère un README.md COMPLET et professionnel pour ce projet:
        
        PROJET: {request.description}
        TYPE: {request.project_type.value}
        FRAMEWORK: {request.framework.value}
        
        INCLUS OBLIGATOIREMENT:
        - Description claire du projet
        - Installation et setup
        - Configuration requise
        - Utilisation et exemples
        - Structure du projet
        - Scripts disponibles
        - Déploiement
        - Contribution guidelines
        - License
        
        Format Markdown professionnel avec emojis et badges.
        """
        
        response = await chat.with_model("openai", "gpt-4o").send_message(
            UserMessage(text=prompt)
        )
        
        return response
    
    # Méthodes utilitaires pour les dépendances et configurations
    def _get_dependencies(self, framework: Framework) -> Dict[str, str]:
        """Retourne les dépendances selon le framework"""
        deps_map = {
            Framework.REACT: {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.18.0",
                "axios": "^1.6.0",
                "@tanstack/react-query": "^5.8.0"
            },
            Framework.VUE: {
                "vue": "^3.3.8",
                "vue-router": "^4.2.5",
                "pinia": "^2.1.7",
                "axios": "^1.6.0"
            },
            Framework.NEXT_JS: {
                "next": "^14.0.3",
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            }
        }
        return deps_map.get(framework, {})
    
    def _get_scripts(self, framework: Framework) -> Dict[str, str]:
        """Retourne les scripts selon le framework"""
        if framework in [Framework.REACT, Framework.VUE]:
            return {
                "dev": "vite dev",
                "build": "vite build",
                "preview": "vite preview",
                "test": "vitest"
            }
        elif framework == Framework.NEXT_JS:
            return {
                "dev": "next dev",
                "build": "next build",
                "start": "next start"
            }
        return {}
    
    def _get_dev_dependencies(self, framework: Framework) -> Dict[str, str]:
        """Retourne les dépendances de développement"""
        return {
            "vite": "^5.0.0",
            "typescript": "^5.2.0",
            "@types/react": "^18.2.0",
            "eslint": "^8.53.0",
            "prettier": "^3.1.0"
        }
    
    def _get_frontend_dockerfile(self) -> str:
        return """
        FROM node:18-alpine AS builder
        WORKDIR /app
        COPY package*.json ./
        RUN npm ci --only=production
        COPY . .
        RUN npm run build
        
        FROM nginx:alpine
        COPY --from=builder /app/dist /usr/share/nginx/html
        COPY nginx.conf /etc/nginx/nginx.conf
        EXPOSE 80
        CMD ["nginx", "-g", "daemon off;"]
        """
    
    def _get_python_dockerfile(self) -> str:
        return """
        FROM python:3.11-slim
        
        WORKDIR /app
        
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt
        
        COPY . .
        
        EXPOSE 8000
        
        CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
        """
    
    def _get_node_dockerfile(self) -> str:
        return """
        FROM node:18-alpine
        
        WORKDIR /app
        
        COPY package*.json ./
        RUN npm ci --only=production
        
        COPY . .
        
        EXPOSE 3000
        
        CMD ["npm", "start"]
        """
    
    def _get_generic_dockerfile(self) -> str:
        return "# Dockerfile générique - à adapter selon les besoins"
    
    def _get_default_structure(self, request: GenerationRequest) -> Dict[str, str]:
        """Génère une structure par défaut selon le type de projet"""
        if request.framework == Framework.REACT:
            return {
                "public/index.html": "HTML principal de l'application React",
                "src/App.jsx": "Composant React principal",
                "src/index.js": "Point d'entrée React",
                "src/components/Header.jsx": "Composant d'en-tête",
                "src/pages/Home.jsx": "Page d'accueil",
                "src/styles/App.css": "Styles principaux",
                "package.json": "Configuration npm",
                "README.md": "Documentation du projet"
            }
        elif request.framework == Framework.VUE:
            return {
                "public/index.html": "HTML principal Vue",
                "src/App.vue": "Composant Vue principal",
                "src/main.js": "Point d'entrée Vue",
                "src/components/HelloWorld.vue": "Composant Vue exemple",
                "src/assets/style.css": "Styles Vue"
            }
        elif request.framework == Framework.FASTAPI:
            return {
                "main.py": "Application FastAPI principale",
                "models.py": "Modèles de données",
                "routes.py": "Routes API",
                "requirements.txt": "Dépendances Python",
                "Dockerfile": "Configuration Docker"
            }
        else:
            return {
                "index.html": "Page HTML principale",
                "style.css": "Feuille de styles",
                "script.js": "Code JavaScript",
                "README.md": "Documentation"
            }
    
    def _get_vercel_config(self, request: GenerationRequest) -> Dict:
        return {
            "version": 2,
            "builds": [
                {"src": "package.json", "use": "@vercel/node"}
            ]
        }
    
    def _get_docker_compose(self, request: GenerationRequest) -> str:
        return """
        version: '3.8'
        services:
          app:
            build: .
            ports:
              - "3000:3000"
            environment:
              - NODE_ENV=production
        """
    
    def _get_k8s_config(self, request: GenerationRequest) -> Dict:
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "vectort-app"},
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "vectort-app"}},
                "template": {
                    "metadata": {"labels": {"app": "vectort-app"}},
                    "spec": {
                        "containers": [{
                            "name": "app",
                            "image": "vectort-app:latest",
                            "ports": [{"containerPort": 3000}]
                        }]
                    }
                }
            }
        }