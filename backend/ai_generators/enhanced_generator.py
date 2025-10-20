"""
VECTORT.IO - ENHANCED PROJECT GENERATOR
Système de génération de projets complets avec structure multi-fichiers
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json


@dataclass
class ProjectStructure:
    """Définit la structure d'un projet"""
    files: Dict[str, str]  # chemin -> description
    dependencies: Dict[str, List[str]]  # type -> liste de packages
    env_vars: Dict[str, str]  # nom -> description


class EnhancedProjectGenerator:
    """Générateur amélioré de projets complets"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_project_structure(self, framework: str, project_type: str) -> ProjectStructure:
        """Retourne la structure complète selon le framework"""
        
        structures = {
            "react": self._get_react_structure(project_type),
            "nextjs": self._get_nextjs_structure(project_type),
            "vue": self._get_vue_structure(project_type),
            "fastapi": self._get_fastapi_structure(project_type),
            "express": self._get_express_structure(project_type),
        }
        
        return structures.get(framework, self._get_react_structure(project_type))
    
    def _get_react_structure(self, project_type: str) -> ProjectStructure:
        """Structure pour React + Vite"""
        
        files = {
            # Configuration
            "package.json": "Configuration npm avec dépendances React",
            "vite.config.js": "Configuration Vite pour build optimisé",
            ".env.example": "Variables d'environnement exemple",
            ".gitignore": "Fichiers à ignorer par git",
            
            # Public
            "public/index.html": "HTML principal avec meta tags SEO",
            "public/robots.txt": "Configuration SEO",
            "public/manifest.json": "PWA manifest",
            
            # Source - Core
            "src/main.jsx": "Point d'entrée React",
            "src/App.jsx": "Composant principal avec routing",
            "src/index.css": "Styles globaux et variables CSS",
            
            # Source - Components
            "src/components/Header.jsx": "Header avec navigation",
            "src/components/Footer.jsx": "Footer de l'application",
            "src/components/Layout.jsx": "Layout principal avec Header/Footer",
            
            # Source - Pages
            "src/pages/Home.jsx": "Page d'accueil",
            "src/pages/About.jsx": "Page à propos",
            "src/pages/NotFound.jsx": "Page 404",
            
            # Source - Utils
            "src/utils/api.js": "Client API avec axios",
            "src/utils/constants.js": "Constantes de l'application",
            "src/utils/helpers.js": "Fonctions utilitaires",
            
            # Source - Hooks (si applicable)
            "src/hooks/useApi.js": "Hook personnalisé pour API calls",
            "src/hooks/useLocalStorage.js": "Hook pour localStorage",
            
            # Documentation
            "README.md": "Documentation complète du projet",
            "CONTRIBUTING.md": "Guide de contribution",
        }
        
        # Ajouter des fichiers spécifiques selon le type de projet
        if project_type in ["ecommerce", "marketplace"]:
            files.update({
                "src/components/ProductCard.jsx": "Carte produit",
                "src/components/Cart.jsx": "Panier d'achat",
                "src/pages/Products.jsx": "Liste des produits",
                "src/pages/ProductDetail.jsx": "Détail produit",
                "src/pages/Checkout.jsx": "Page de paiement",
                "src/contexts/CartContext.jsx": "Context pour le panier",
            })
        
        elif project_type in ["blog", "cms"]:
            files.update({
                "src/components/PostCard.jsx": "Carte article",
                "src/components/Editor.jsx": "Éditeur de contenu",
                "src/pages/Posts.jsx": "Liste des articles",
                "src/pages/PostDetail.jsx": "Détail article",
                "src/pages/CreatePost.jsx": "Créer un article",
            })
        
        dependencies = {
            "dependencies": [
                "react@^18.2.0",
                "react-dom@^18.2.0",
                "react-router-dom@^6.20.0",
                "axios@^1.6.2",
                "zustand@^4.4.7",  # State management moderne
            ],
            "devDependencies": [
                "vite@^5.0.0",
                "@vitejs/plugin-react@^4.2.0",
                "eslint@^8.55.0",
                "eslint-plugin-react@^7.33.2",
            ]
        }
        
        env_vars = {
            "VITE_API_URL": "URL de l'API backend",
            "VITE_APP_NAME": "Nom de l'application",
        }
        
        return ProjectStructure(files=files, dependencies=dependencies, env_vars=env_vars)
    
    def _get_nextjs_structure(self, project_type: str) -> ProjectStructure:
        """Structure pour Next.js 14+ avec App Router"""
        
        files = {
            # Configuration
            "package.json": "Configuration npm Next.js",
            "next.config.js": "Configuration Next.js",
            "tsconfig.json": "Configuration TypeScript",
            ".env.local.example": "Variables d'environnement",
            ".gitignore": "Fichiers à ignorer",
            
            # App Router
            "app/layout.tsx": "Layout racine avec metadata",
            "app/page.tsx": "Page d'accueil",
            "app/globals.css": "Styles globaux",
            "app/not-found.tsx": "Page 404 personnalisée",
            
            # Pages
            "app/about/page.tsx": "Page à propos",
            "app/contact/page.tsx": "Page contact",
            
            # API Routes
            "app/api/route.ts": "Route API principale",
            "app/api/health/route.ts": "Health check endpoint",
            
            # Components
            "components/Header.tsx": "Header avec navigation",
            "components/Footer.tsx": "Footer",
            "components/Button.tsx": "Composant bouton réutilisable",
            
            # Lib
            "lib/api.ts": "Client API",
            "lib/utils.ts": "Fonctions utilitaires",
            "lib/db.ts": "Connexion base de données",
            
            # Public
            "public/favicon.ico": "Favicon",
            "public/robots.txt": "SEO robots",
            
            # Documentation
            "README.md": "Documentation",
        }
        
        dependencies = {
            "dependencies": [
                "next@^14.0.4",
                "react@^18.2.0",
                "react-dom@^18.2.0",
                "typescript@^5.3.3",
            ],
            "devDependencies": [
                "@types/react@^18.2.45",
                "@types/node@^20.10.5",
                "eslint@^8.55.0",
                "eslint-config-next@^14.0.4",
            ]
        }
        
        return ProjectStructure(files=files, dependencies=dependencies, env_vars={})
    
    def _get_vue_structure(self, project_type: str) -> ProjectStructure:
        """Structure pour Vue 3 + Vite"""
        
        files = {
            "package.json": "Configuration Vue 3",
            "vite.config.js": "Configuration Vite",
            "index.html": "HTML principal",
            ".env.example": "Variables d'environnement",
            
            "src/main.js": "Point d'entrée Vue",
            "src/App.vue": "Composant racine",
            "src/router/index.js": "Configuration Vue Router",
            "src/store/index.js": "Configuration Pinia store",
            
            "src/components/HelloWorld.vue": "Composant exemple",
            "src/views/Home.vue": "Vue Home",
            "src/views/About.vue": "Vue About",
            
            "README.md": "Documentation",
        }
        
        dependencies = {
            "dependencies": [
                "vue@^3.3.11",
                "vue-router@^4.2.5",
                "pinia@^2.1.7",
                "axios@^1.6.2",
            ],
            "devDependencies": [
                "vite@^5.0.0",
                "@vitejs/plugin-vue@^4.5.2",
            ]
        }
        
        return ProjectStructure(files=files, dependencies=dependencies, env_vars={})
    
    def _get_fastapi_structure(self, project_type: str) -> ProjectStructure:
        """Structure pour FastAPI"""
        
        files = {
            "requirements.txt": "Dépendances Python",
            ".env.example": "Variables d'environnement",
            ".gitignore": "Fichiers à ignorer",
            "Dockerfile": "Configuration Docker",
            "docker-compose.yml": "Configuration Docker Compose",
            
            "main.py": "Point d'entrée FastAPI",
            "config.py": "Configuration de l'application",
            
            "models/__init__.py": "Models init",
            "models/user.py": "Model utilisateur",
            "models/database.py": "Configuration base de données",
            
            "routers/__init__.py": "Routers init",
            "routers/auth.py": "Routes d'authentification",
            "routers/users.py": "Routes utilisateurs",
            
            "schemas/__init__.py": "Schemas init",
            "schemas/user.py": "Schemas Pydantic utilisateur",
            
            "utils/__init__.py": "Utils init",
            "utils/security.py": "Fonctions de sécurité",
            "utils/dependencies.py": "Dépendances FastAPI",
            
            "tests/__init__.py": "Tests init",
            "tests/test_main.py": "Tests API",
            
            "README.md": "Documentation",
        }
        
        dependencies = {
            "requirements": [
                "fastapi==0.109.0",
                "uvicorn[standard]==0.25.0",
                "pydantic==2.5.3",
                "python-dotenv==1.0.0",
                "sqlalchemy==2.0.25",
                "python-jose[cryptography]==3.3.0",
                "passlib[bcrypt]==1.7.4",
                "python-multipart==0.0.6",
            ],
            "requirements-dev": [
                "pytest==7.4.3",
                "httpx==0.26.0",
                "black==23.12.1",
                "ruff==0.1.9",
            ]
        }
        
        env_vars = {
            "DATABASE_URL": "URL de la base de données",
            "SECRET_KEY": "Clé secrète JWT",
            "ALGORITHM": "HS256",
        }
        
        return ProjectStructure(files=files, dependencies=dependencies, env_vars=env_vars)
    
    def _get_express_structure(self, project_type: str) -> ProjectStructure:
        """Structure pour Express.js"""
        
        files = {
            "package.json": "Configuration Express",
            ".env.example": "Variables d'environnement",
            ".gitignore": "Fichiers à ignorer",
            "Dockerfile": "Configuration Docker",
            
            "server.js": "Point d'entrée serveur",
            "app.js": "Configuration Express app",
            
            "config/database.js": "Configuration DB",
            "config/env.js": "Configuration environnement",
            
            "routes/index.js": "Routes principales",
            "routes/auth.js": "Routes authentification",
            "routes/users.js": "Routes utilisateurs",
            
            "controllers/authController.js": "Controller auth",
            "controllers/userController.js": "Controller users",
            
            "models/User.js": "Model utilisateur",
            
            "middleware/auth.js": "Middleware authentification",
            "middleware/errorHandler.js": "Middleware erreurs",
            
            "utils/logger.js": "Logger",
            "utils/validation.js": "Validation",
            
            "tests/app.test.js": "Tests",
            
            "README.md": "Documentation",
        }
        
        dependencies = {
            "dependencies": [
                "express@^4.18.2",
                "cors@^2.8.5",
                "dotenv@^16.3.1",
                "mongoose@^8.0.3",
                "jsonwebtoken@^9.0.2",
                "bcryptjs@^2.4.3",
                "express-validator@^7.0.1",
            ],
            "devDependencies": [
                "nodemon@^3.0.2",
                "jest@^29.7.0",
                "supertest@^6.3.3",
                "eslint@^8.56.0",
            ]
        }
        
        return ProjectStructure(files=files, dependencies=dependencies, env_vars={})
    
    async def generate_complete_project(
        self,
        description: str,
        framework: str,
        project_type: str,
        advanced_mode: bool = True
    ) -> Dict[str, str]:
        """
        Génère un projet complet - VERSION ULTRA-OPTIMISÉE
        Réduit les appels LLM en générant plusieurs fichiers par appel
        
        Returns:
            Dict avec tous les fichiers générés {chemin: contenu}
        """
        import asyncio
        
        # Obtenir la structure
        structure = self.get_project_structure(framework, project_type)
        essential_files = self._filter_essential_files(structure.files, framework)
        
        all_files = {}
        
        # STRATÉGIE : 3 appels LLM groupés au lieu de 1 par fichier
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"project-{hash(description)}",
            system_message=self._get_system_message(framework, project_type)
        )
        
        try:
            # Groupe 1 : Fichiers principaux (composants React, pages)
            main_files = {k: v for k, v in essential_files.items() if any(x in k for x in ['App.', 'main.', 'index.', 'Home.', 'Layout.'])}
            
            # Groupe 2 : Fichiers utilitaires et helpers
            util_files = {k: v for k, v in essential_files.items() if any(x in k for x in ['util', 'helper', 'api.', 'config.'])}
            
            # Groupe 3 : Composants secondaires
            component_files = {k: v for k, v in essential_files.items() if 'component' in k.lower() and k not in main_files}
            
            # Générer en 3 appels parallèles avec timeout
            task1 = self._generate_files_batch(chat, main_files, description, framework, project_type) if main_files else asyncio.sleep(0)
            task2 = self._generate_files_batch(chat, util_files, description, framework, project_type) if util_files else asyncio.sleep(0)
            task3 = self._generate_files_batch(chat, component_files, description, framework, project_type) if component_files else asyncio.sleep(0)
            
            results = await asyncio.wait_for(
                asyncio.gather(task1, task2, task3, return_exceptions=True),
                timeout=18.0  # 18s pour laisser 2s de marge
            )
            
            # Fusionner les résultats
            for result in results:
                if isinstance(result, dict):
                    all_files.update(result)
                    
        except asyncio.TimeoutError:
            print("⚠️ Timeout génération, utilisation de fallbacks minimaux")
        except Exception as e:
            print(f"⚠️ Erreur génération: {e}")
        
        # Si pas assez de fichiers, ajouter des fallbacks
        if len(all_files) < 3:
            print("⚠️ Génération insuffisante, ajout de fichiers de base")
            all_files.update(self._generate_minimal_project(framework, description))
        
        # Ajouter TOUJOURS les fichiers de configuration (instantané, pas de LLM)
        all_files.update(self._generate_config_files(structure, framework))
        
        return all_files
    
    async def _generate_files_batch(
        self,
        chat: LlmChat,
        files: Dict[str, str],
        description: str,
        framework: str,
        project_type: str
    ) -> Dict[str, str]:
        """Génère un batch de fichiers en un seul appel LLM"""
        
        if not files:
            return {}
        
        # Créer un prompt groupé pour tous les fichiers
        files_list = "\n".join([f"- {path}: {desc}" for path, desc in files.items()])
        
        prompt = f"""Génère le code pour TOUS ces fichiers d'un coup:

PROJET: {description}
TYPE: {project_type}
FRAMEWORK: {framework}

FICHIERS À GÉNÉRER:
{files_list}

IMPORTANT:
- Génère le code de CHAQUE fichier
- Format de réponse: 
  FICHIER: chemin/fichier.ext
  ```
  code ici
  ```
  
  FICHIER: autre/fichier.ext
  ```
  code ici
  ```

- Code production-ready, fonctionnel
- Respect des conventions du framework
- Imports/exports cohérents

Génère MAINTENANT tous les fichiers."""
        
        try:
            response = await chat.with_model("openai", "gpt-4o").send_message(UserMessage(text=prompt))
            
            # Parser la réponse pour extraire chaque fichier
            generated = self._parse_batch_response(response, list(files.keys()))
            return generated
            
        except Exception as e:
            print(f"Erreur génération batch: {e}")
            # Fallback : générer au moins le premier fichier
            first_file = list(files.keys())[0]
            return {first_file: self._get_fallback_content(first_file)}
    
    def _parse_batch_response(self, response: str, expected_files: List[str]) -> Dict[str, str]:
        """Parse une réponse contenant plusieurs fichiers"""
        
        files = {}
        
        # Chercher les patterns "FICHIER: path"
        import re
        parts = re.split(r'FICHIER:\s*([^\n]+)', response)
        
        for i in range(1, len(parts), 2):
            if i+1 < len(parts):
                file_path = parts[i].strip()
                content = parts[i+1].strip()
                
                # Nettoyer le contenu
                content = self._clean_generated_code(content)
                
                # Trouver le fichier correspondant
                for expected in expected_files:
                    if expected in file_path or file_path in expected:
                        files[expected] = content
                        break
        
        # Si pas assez de fichiers parsés, ajouter des fallbacks
        for expected in expected_files:
            if expected not in files:
                files[expected] = self._get_fallback_content(expected)
        
        return files
    
    def _generate_minimal_project(self, framework: str, description: str) -> Dict[str, str]:
        """Génère un projet minimal sans LLM (fallback)"""
        
        files = {}
        
        if framework == "react":
            files["src/App.jsx"] = f"""import React from 'react';

export default function App() {{
  return (
    <div className="app">
      <h1>Application Générée</h1>
      <p>{description}</p>
    </div>
  );
}}
"""
            files["src/index.css"] = """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  color: #333;
  margin-bottom: 1rem;
}
"""
        
        return files
    
    def _filter_essential_files(self, all_files: Dict[str, str], framework: str) -> Dict[str, str]:
        """Filtre pour garder uniquement les fichiers essentiels (MVP)"""
        
        essential = {}
        
        # Toujours inclure
        always_include = [
            'package.json', 'requirements.txt', '.gitignore', 
            'README.md', '.env.example'
        ]
        
        # Fichiers essentiels par framework
        if framework == "react":
            priority_files = [
                'src/main.jsx', 'src/App.jsx', 'src/index.css',
                'src/components/Header.jsx', 'src/components/Layout.jsx',
                'src/pages/Home.jsx',
                'src/utils/api.js',
                'public/index.html'
            ]
        elif framework == "nextjs":
            priority_files = [
                'app/layout.tsx', 'app/page.tsx', 'app/globals.css',
                'components/Header.tsx',
                'lib/api.ts',
                'tsconfig.json'
            ]
        elif framework == "fastapi":
            priority_files = [
                'main.py', 'config.py',
                'models/user.py', 'models/database.py',
                'routers/auth.py',
                'schemas/user.py',
                'utils/security.py'
            ]
        elif framework == "express":
            priority_files = [
                'server.js', 'app.js',
                'routes/index.js', 'routes/auth.js',
                'models/User.js',
                'middleware/auth.js'
            ]
        else:
            priority_files = []
        
        # Filtrer les fichiers
        for file_path, desc in all_files.items():
            # Toujours inclure les configs
            if any(x in file_path for x in always_include):
                essential[file_path] = desc
            # Inclure les fichiers prioritaires
            elif file_path in priority_files:
                essential[file_path] = desc
        
        return essential
    
    def _group_files_by_priority(self, files: Dict[str, str]) -> Dict[int, Dict[str, str]]:
        """Groupe les fichiers par priorité de génération"""
        
        priority_groups = {
            1: {},  # Configuration (package.json, etc.)
            2: {},  # Core files (main, app)
            3: {},  # Components
            4: {},  # Pages/Routes
            5: {},  # Utils/Helpers
            6: {},  # Documentation
        }
        
        for file_path, desc in files.items():
            if any(x in file_path for x in ["package.json", "requirements.txt", "config"]):
                priority_groups[1][file_path] = desc
            elif any(x in file_path for x in ["main.", "app.", "server.", "index."]):
                priority_groups[2][file_path] = desc
            elif "component" in file_path.lower():
                priority_groups[3][file_path] = desc
            elif any(x in file_path for x in ["page", "route", "view"]):
                priority_groups[4][file_path] = desc
            elif any(x in file_path for x in ["util", "helper", "lib"]):
                priority_groups[5][file_path] = desc
            else:
                priority_groups[6][file_path] = desc
        
        return priority_groups
    
    async def _generate_file_content(
        self,
        chat: LlmChat,
        file_path: str,
        file_desc: str,
        description: str,
        framework: str,
        project_type: str,
        dependencies: Dict,
        existing_files: Dict[str, str]
    ) -> str:
        """Génère le contenu d'un fichier spécifique"""
        
        # Context des fichiers déjà générés
        context = self._build_generation_context(existing_files, file_path)
        
        prompt = f"""
Génère le contenu COMPLET et PROFESSIONNEL pour ce fichier:

FICHIER: {file_path}
DESCRIPTION: {file_desc}

PROJET: {description}
TYPE: {project_type}
FRAMEWORK: {framework}

{context}

RÈGLES IMPORTANTES:
1. Code PRODUCTION-READY (pas de TODO, pas de placeholders)
2. Respect des conventions du framework
3. Imports corrects et cohérents avec les autres fichiers
4. Commentaires utiles mais pas excessifs
5. Gestion d'erreurs appropriée
6. Types/PropTypes si applicable
7. Responsive design pour le frontend
8. Sécurité (validation, sanitization) pour le backend

Génère UNIQUEMENT le code, sans explications ni markdown.
"""
        
        response = await chat.with_model("openai", "gpt-4o").send_message(UserMessage(text=prompt))
        return self._clean_generated_code(response)
    
    def _build_generation_context(self, existing_files: Dict[str, str], current_file: str) -> str:
        """Construit le contexte des fichiers déjà générés"""
        
        if not existing_files:
            return "C'est le premier fichier généré."
        
        # Lister les fichiers existants
        context = "\nFICHIERS DÉJÀ GÉNÉRÉS:\n"
        for file_path in existing_files.keys():
            context += f"- {file_path}\n"
        
        # Ajouter des extraits pertinents si nécessaire
        relevant_files = self._find_relevant_files(current_file, existing_files)
        if relevant_files:
            context += "\nFICHIERS PERTINENTS (pour référence):\n"
            for rel_file, content in relevant_files.items():
                # Extraire les imports et exports
                imports = self._extract_imports(content)
                exports = self._extract_exports(content)
                context += f"\n{rel_file}:\n"
                if imports:
                    context += f"  Imports: {', '.join(imports[:5])}\n"
                if exports:
                    context += f"  Exports: {', '.join(exports[:5])}\n"
        
        return context
    
    def _find_relevant_files(self, current_file: str, existing_files: Dict[str, str]) -> Dict[str, str]:
        """Trouve les fichiers pertinents pour la génération actuelle"""
        relevant = {}
        
        # Si c'est un composant, regarder les autres composants
        if "component" in current_file.lower():
            for path, content in existing_files.items():
                if "component" in path.lower() and len(relevant) < 2:
                    relevant[path] = content
        
        # Si c'est une page, regarder App et Layout
        elif "page" in current_file.lower() or "view" in current_file.lower():
            for path, content in existing_files.items():
                if any(x in path.lower() for x in ["app.", "layout", "router"]):
                    relevant[path] = content
        
        return relevant
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extrait les imports d'un fichier"""
        imports = []
        lines = content.split('\n')
        for line in lines[:20]:  # Regarder les 20 premières lignes
            if line.strip().startswith(('import ', 'from ')):
                imports.append(line.strip())
        return imports
    
    def _extract_exports(self, content: str) -> List[str]:
        """Extrait les exports d'un fichier"""
        exports = []
        if 'export default' in content:
            exports.append('default')
        if 'export {' in content:
            exports.append('named exports')
        return exports
    
    def _clean_generated_code(self, code: str) -> str:
        """Nettoie le code généré"""
        # Retirer les blocs markdown
        code = code.replace('```javascript', '').replace('```typescript', '')
        code = code.replace('```python', '').replace('```jsx', '')
        code = code.replace('```', '')
        
        # Retirer les espaces en début/fin
        code = code.strip()
        
        return code
    
    def _generate_config_files(self, structure: ProjectStructure, framework: str) -> Dict[str, str]:
        """Génère les fichiers de configuration automatiquement"""
        
        config_files = {}
        
        # package.json pour frameworks JS
        if framework in ["react", "vue", "nextjs", "express"]:
            config_files["package.json"] = self._generate_package_json(framework, structure.dependencies)
        
        # requirements.txt pour Python
        if framework in ["fastapi", "django", "flask"]:
            config_files["requirements.txt"] = self._generate_requirements_txt(structure.dependencies)
        
        # .env.example
        if structure.env_vars:
            config_files[".env.example"] = self._generate_env_example(structure.env_vars)
        
        # .gitignore
        config_files[".gitignore"] = self._generate_gitignore(framework)
        
        return config_files
    
    def _generate_package_json(self, framework: str, dependencies: Dict) -> str:
        """Génère package.json"""
        
        scripts = {
            "react": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview",
                "lint": "eslint src --ext js,jsx --report-unused-disable-directives --max-warnings 0"
            },
            "nextjs": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "vue": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "express": {
                "start": "node server.js",
                "dev": "nodemon server.js",
                "test": "jest"
            }
        }
        
        package = {
            "name": "vectort-generated-project",
            "version": "1.0.0",
            "type": "module" if framework != "express" else "commonjs",
            "scripts": scripts.get(framework, {}),
            "dependencies": {},
            "devDependencies": {}
        }
        
        # Ajouter les dépendances
        for dep in dependencies.get("dependencies", []):
            if "@" in dep:
                parts = dep.split("@")
                name = parts[0] if parts[0] else parts[1]
                version = parts[-1]
            else:
                name = dep
                version = "latest"
            package["dependencies"][name] = version
        
        for dep in dependencies.get("devDependencies", []):
            if "@" in dep:
                parts = dep.split("@")
                name = parts[0] if parts[0] else parts[1]
                version = parts[-1]
            else:
                name = dep
                version = "latest"
            package["devDependencies"][name] = version
        
        return json.dumps(package, indent=2)
    
    def _generate_requirements_txt(self, dependencies: Dict) -> str:
        """Génère requirements.txt"""
        return "\n".join(dependencies.get("requirements", []))
    
    def _generate_env_example(self, env_vars: Dict[str, str]) -> str:
        """Génère .env.example"""
        lines = ["# Environment Variables\n"]
        for var, desc in env_vars.items():
            lines.append(f"# {desc}")
            lines.append(f"{var}=your_value_here\n")
        return "\n".join(lines)
    
    def _generate_gitignore(self, framework: str) -> str:
        """Génère .gitignore"""
        
        base = """# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/

# Production
build/
dist/
.next/
out/

# Environment
.env
.env.local
.env.*.local

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
"""
        
        if framework in ["fastapi", "django", "flask"]:
            base += """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
"""
        
        return base
    
    def _get_system_message(self, framework: str, project_type: str) -> str:
        """Message système pour le LLM"""
        
        return f"""Tu es un développeur expert senior spécialisé en {framework}.
Tu génères du code PRODUCTION-READY de haute qualité.

Contexte:
- Framework: {framework}
- Type de projet: {project_type}

Principes:
1. Code propre, maintenable, bien structuré
2. Best practices du framework
3. Gestion d'erreurs complète
4. Performance optimisée
5. Sécurité (XSS, CSRF, injection, etc.)
6. Accessibilité (ARIA, semantic HTML)
7. SEO optimisé
8. Responsive design

Tu génères UNIQUEMENT le code demandé, sans explications ni commentaires superflus."""
    
    def _get_fallback_content(self, file_path: str) -> str:
        """Contenu de secours si la génération échoue"""
        
        if file_path.endswith('.md'):
            return f"# {file_path}\n\nDocumentation à compléter."
        
        if file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
            return "// File generated by Vectort.io\n\nexport default function Component() {\n  return null;\n}\n"
        
        if file_path.endswith('.py'):
            return "# File generated by Vectort.io\n\ndef main():\n    pass\n"
        
        return f"# {file_path}\n# Content generation failed\n"
