"""
VECTORT.IO - ZIP EXPORTER
Crée des archives ZIP professionnelles du code généré
"""

import zipfile
import io
from typing import Dict, Optional
from pathlib import Path
import json


class ZipExporter:
    """Gère la création d'archives ZIP pour l'export de projets"""
    
    def __init__(self):
        self.default_structure = {
            "README.md": self._get_default_readme,
            ".gitignore": self._get_default_gitignore,
            "LICENSE": self._get_default_license,
        }
    
    async def create_project_zip(
        self,
        project_title: str,
        generated_code: Dict[str, str],
        framework: str = "react",
        include_config: bool = True
    ) -> io.BytesIO:
        """
        Crée une archive ZIP complète d'un projet
        
        Args:
            project_title: Nom du projet
            generated_code: Dict avec les fichiers générés {chemin: contenu}
            framework: Framework utilisé (react, vue, fastapi, etc.)
            include_config: Inclure les fichiers de configuration
            
        Returns:
            BytesIO contenant le ZIP
        """
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Créer le dossier racine du projet
            project_name = self._sanitize_project_name(project_title)
            
            # 1. Ajouter les fichiers de base
            self._add_base_files(zip_file, project_name, project_title, framework)
            
            # 2. Ajouter le code généré
            self._add_generated_code(zip_file, project_name, generated_code, framework)
            
            # 3. Ajouter les fichiers de configuration
            if include_config:
                self._add_configuration_files(zip_file, project_name, framework, generated_code)
            
            # 4. Ajouter la documentation
            self._add_documentation(zip_file, project_name, framework, generated_code)
        
        zip_buffer.seek(0)
        return zip_buffer
    
    def _sanitize_project_name(self, title: str) -> str:
        """Nettoie le nom du projet pour le système de fichiers"""
        # Remplacer les espaces et caractères spéciaux
        clean_name = title.lower()
        clean_name = clean_name.replace(' ', '-')
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c in ['-', '_'])
        return clean_name or "vectort-project"
    
    def _add_base_files(self, zip_file: zipfile.ZipFile, project_name: str, project_title: str, framework: str):
        """Ajoute les fichiers de base (README, .gitignore, etc.)"""
        
        # README.md
        readme_content = f"""# {project_title}

> Application générée automatiquement par Vectort.io

## 🚀 Description

Cette application a été générée avec Vectort.io, la plateforme de génération d'applications par IA.

**Framework**: {framework}
**Généré le**: {self._get_current_date()}

## 📦 Installation

```bash
# Cloner le projet
git clone <votre-repo>

# Installer les dépendances
{self._get_install_command(framework)}
```

## 🔧 Développement

```bash
# Lancer en mode développement
{self._get_dev_command(framework)}
```

## 🏗️ Build

```bash
# Créer un build de production
{self._get_build_command(framework)}
```

## 🚀 Déploiement

### Vercel (Recommandé pour React/Next.js)
```bash
npm install -g vercel
vercel
```

### Netlify
```bash
npm install -g netlify-cli
netlify deploy
```

### Docker
```bash
docker build -t {project_name} .
docker run -p 3000:3000 {project_name}
```

## 📝 Structure du projet

```
{project_name}/
├── src/              # Code source
├── public/           # Assets statiques
├── package.json      # Dépendances
└── README.md         # Documentation
```

## 🛠️ Technologies

- **Frontend**: {framework}
- **Styling**: CSS moderne
- **Build**: {self._get_build_tool(framework)}

## 📄 License

MIT - Généré par Vectort.io

## 🤝 Support

Besoin d'aide ? Contactez-nous sur [vectort.io](https://vectort.io)

---

*Généré avec ❤️ par [Vectort.io](https://vectort.io)*
"""
        zip_file.writestr(f"{project_name}/README.md", readme_content)
        
        # .gitignore
        gitignore_content = self._get_gitignore_for_framework(framework)
        zip_file.writestr(f"{project_name}/.gitignore", gitignore_content)
        
        # LICENSE
        license_content = self._get_mit_license(project_title)
        zip_file.writestr(f"{project_name}/LICENSE", license_content)
    
    def _add_generated_code(
        self,
        zip_file: zipfile.ZipFile,
        project_name: str,
        generated_code: Dict[str, str],
        framework: str
    ):
        """Ajoute le code généré dans la structure appropriée"""
        
        # Mapping du code vers la structure de fichiers
        code_mapping = {
            'html_code': 'public/index.html',
            'css_code': 'src/styles/App.css',
            'js_code': 'src/utils/helpers.js',
            'react_code': 'src/App.jsx',
            'backend_code': 'server.js' if framework == 'express' else 'main.py',
        }
        
        for code_key, file_path in code_mapping.items():
            code_content = generated_code.get(code_key, '')
            if code_content and code_content.strip():
                full_path = f"{project_name}/{file_path}"
                zip_file.writestr(full_path, code_content)
        
        # Ajouter les fichiers all_files si disponibles
        all_files = generated_code.get('all_files', {})
        if isinstance(all_files, dict):
            for file_path, content in all_files.items():
                if content and content.strip():
                    full_path = f"{project_name}/{file_path}"
                    zip_file.writestr(full_path, content)
    
    def _add_configuration_files(
        self,
        zip_file: zipfile.ZipFile,
        project_name: str,
        framework: str,
        generated_code: Dict[str, str]
    ):
        """Ajoute les fichiers de configuration"""
        
        # package.json pour projets JavaScript
        if framework in ['react', 'vue', 'angular', 'nextjs', 'express']:
            package_json = generated_code.get('package_json')
            if not package_json:
                package_json = self._generate_package_json(project_name, framework)
            zip_file.writestr(f"{project_name}/package.json", package_json)
        
        # requirements.txt pour projets Python
        if framework in ['fastapi', 'django', 'flask']:
            requirements = generated_code.get('requirements_txt')
            if not requirements:
                requirements = self._generate_requirements(framework)
            zip_file.writestr(f"{project_name}/requirements.txt", requirements)
        
        # Dockerfile
        dockerfile = generated_code.get('dockerfile')
        if not dockerfile:
            dockerfile = self._generate_dockerfile(framework)
        zip_file.writestr(f"{project_name}/Dockerfile", dockerfile)
        
        # .env.example
        env_example = self._generate_env_example(framework)
        zip_file.writestr(f"{project_name}/.env.example", env_example)
    
    def _add_documentation(
        self,
        zip_file: zipfile.ZipFile,
        project_name: str,
        framework: str,
        generated_code: Dict[str, str]
    ):
        """Ajoute la documentation supplémentaire"""
        
        # DEPLOYMENT.md
        deployment_guide = f"""# Guide de Déploiement

## Options de déploiement

### 1. Vercel (Recommandé pour {framework})

1. Installer Vercel CLI:
```bash
npm i -g vercel
```

2. Déployer:
```bash
vercel
```

### 2. Netlify

1. Installer Netlify CLI:
```bash
npm i -g netlify-cli
```

2. Déployer:
```bash
netlify deploy --prod
```

### 3. Docker

```bash
docker build -t {project_name} .
docker run -p 3000:3000 {project_name}
```

### 4. Hébergement traditionnel

Buildez le projet et uploadez le dossier `dist` ou `build` sur votre serveur.

## Variables d'environnement

Copiez `.env.example` vers `.env` et configurez vos variables.

## Support

Besoin d'aide ? [vectort.io/support](https://vectort.io)
"""
        zip_file.writestr(f"{project_name}/DEPLOYMENT.md", deployment_guide)
        
        # CONTRIBUTING.md
        contributing = """# Guide de Contribution

Merci de votre intérêt pour contribuer à ce projet !

## Comment contribuer

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Code Style

- Suivre les conventions du framework
- Commenter le code complexe
- Écrire des tests si possible

## Questions ?

Ouvrez une issue sur GitHub ou contactez-nous sur [vectort.io](https://vectort.io)
"""
        zip_file.writestr(f"{project_name}/CONTRIBUTING.md", contributing)
    
    def _generate_package_json(self, project_name: str, framework: str) -> str:
        """Génère un package.json selon le framework"""
        
        base_config = {
            "name": project_name,
            "version": "1.0.0",
            "description": f"Application {framework} générée par Vectort.io",
            "main": "src/index.js",
            "scripts": {},
            "keywords": ["vectort", framework],
            "author": "Generated by Vectort.io",
            "license": "MIT",
            "dependencies": {},
            "devDependencies": {}
        }
        
        if framework == 'react':
            base_config["scripts"] = {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            }
            base_config["dependencies"] = {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1"
            }
        
        elif framework == 'express':
            base_config["scripts"] = {
                "start": "node server.js",
                "dev": "nodemon server.js"
            }
            base_config["dependencies"] = {
                "express": "^4.18.2",
                "cors": "^2.8.5",
                "dotenv": "^16.0.3"
            }
            base_config["devDependencies"] = {
                "nodemon": "^2.0.22"
            }
        
        return json.dumps(base_config, indent=2)
    
    def _generate_requirements(self, framework: str) -> str:
        """Génère requirements.txt pour Python"""
        
        if framework == 'fastapi':
            return """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
"""
        elif framework == 'django':
            return """Django==4.2.7
djangorestframework==3.14.0
python-dotenv==1.0.0
"""
        elif framework == 'flask':
            return """Flask==3.0.0
Flask-CORS==4.0.0
python-dotenv==1.0.0
"""
        
        return "# Add your dependencies here\n"
    
    def _generate_dockerfile(self, framework: str) -> str:
        """Génère un Dockerfile selon le framework"""
        
        if framework in ['react', 'vue', 'angular']:
            return """FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""
        
        elif framework == 'express':
            return """FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
"""
        
        elif framework in ['fastapi', 'flask', 'django']:
            return """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        return "# Dockerfile\nFROM node:18-alpine\nWORKDIR /app\nCOPY . .\n"
    
    def _generate_env_example(self, framework: str) -> str:
        """Génère un fichier .env.example"""
        
        return """# Environment Variables
# Copiez ce fichier vers .env et configurez vos variables

# API Configuration
API_URL=http://localhost:3000
API_KEY=your_api_key_here

# Database
DATABASE_URL=your_database_url_here

# Autres configurations
NODE_ENV=development
PORT=3000
"""
    
    def _get_gitignore_for_framework(self, framework: str) -> str:
        """Retourne le .gitignore approprié selon le framework"""
        
        base_ignore = """# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/

# Production
build/
dist/

# Environment
.env
.env.local
.env.production

# Logs
logs/
*.log
npm-debug.log*

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
"""
        
        if framework in ['fastapi', 'django', 'flask']:
            base_ignore += """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
"""
        
        return base_ignore
    
    def _get_mit_license(self, project_title: str) -> str:
        """Retourne la licence MIT"""
        
        from datetime import datetime
        year = datetime.now().year
        
        return f"""MIT License

Copyright (c) {year} {project_title}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---
Generated by Vectort.io - https://vectort.io
"""
    
    def _get_current_date(self) -> str:
        """Retourne la date actuelle formatée"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y")
    
    def _get_install_command(self, framework: str) -> str:
        """Retourne la commande d'installation selon le framework"""
        if framework in ['fastapi', 'django', 'flask']:
            return "pip install -r requirements.txt"
        return "npm install"
    
    def _get_dev_command(self, framework: str) -> str:
        """Retourne la commande de développement"""
        if framework == 'fastapi':
            return "uvicorn main:app --reload"
        elif framework == 'django':
            return "python manage.py runserver"
        elif framework == 'flask':
            return "flask run"
        elif framework == 'express':
            return "npm run dev"
        return "npm start"
    
    def _get_build_command(self, framework: str) -> str:
        """Retourne la commande de build"""
        if framework in ['fastapi', 'django', 'flask']:
            return "# Python apps don't need build"
        return "npm run build"
    
    def _get_build_tool(self, framework: str) -> str:
        """Retourne l'outil de build utilisé"""
        if framework == 'react':
            return "Create React App / Vite"
        elif framework == 'vue':
            return "Vite"
        elif framework == 'nextjs':
            return "Next.js"
        elif framework in ['fastapi', 'django', 'flask']:
            return "Python"
        return "Webpack"
    
    def _get_default_readme(self) -> str:
        return "# Project\n\nGenerated by Vectort.io"
    
    def _get_default_gitignore(self) -> str:
        return self._get_gitignore_for_framework('react')
    
    def _get_default_license(self) -> str:
        return self._get_mit_license("Vectort Project")
