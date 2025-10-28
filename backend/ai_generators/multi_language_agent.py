"""
Agent Multi-Language (Agent 13)
Génère des projets dans TOUS les langages et frameworks

Supporte:
- Frontend: React, Vue, Angular, Svelte, Next.js, Nuxt
- Backend: FastAPI, Django, Flask, Express, NestJS, Spring Boot, Laravel, Rails
- Mobile: React Native, Flutter, Swift, Kotlin
- Desktop: Electron, Tauri
- CLI: Click, Commander, Cobra
- Microservices: gRPC, GraphQL
"""

import logging
from typing import Dict, List
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class MultiLanguageAgent:
    """
    Agent 13 - Multi-Language & Multi-Framework
    
    CAPACITÉS:
    - Python (Django, Flask, FastAPI)
    - JavaScript/TypeScript (React, Vue, Angular, Node.js)
    - Java (Spring Boot, Micronaut)
    - Go (Gin, Echo, Fiber)
    - Rust (Actix, Rocket)
    - C# (.NET, ASP.NET)
    - PHP (Laravel, Symfony)
    - Ruby (Rails, Sinatra)
    - Swift (iOS)
    - Kotlin (Android)
    - Dart (Flutter)
    """
    
    SUPPORTED_LANGUAGES = {
        "python": ["django", "flask", "fastapi", "pyramid"],
        "javascript": ["react", "vue", "angular", "svelte", "nextjs", "express", "nestjs"],
        "typescript": ["react", "vue", "angular", "nextjs", "nestjs"],
        "java": ["spring_boot", "micronaut", "quarkus"],
        "go": ["gin", "echo", "fiber", "chi"],
        "rust": ["actix", "rocket", "warp"],
        "csharp": ["dotnet", "aspnet"],
        "php": ["laravel", "symfony", "codeigniter"],
        "ruby": ["rails", "sinatra"],
        "swift": ["ios", "swiftui"],
        "kotlin": ["android", "ktor"],
        "dart": ["flutter"]
    }
    
    PROJECT_TYPES = [
        "web_app", "api_rest", "api_graphql", "mobile_app", "desktop_app",
        "cli_tool", "microservice", "monolith", "serverless", "blockchain",
        "machine_learning", "data_pipeline", "game", "iot"
    ]
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger("Agent-MultiLanguage")
    
    async def generate_project(
        self,
        description: str,
        language: str,
        framework: str,
        project_type: str
    ) -> Dict[str, str]:
        """
        Génère un projet complet dans le langage et framework choisis
        
        Args:
            description: Description du projet
            language: Langage (python, javascript, java, go, rust, etc.)
            framework: Framework (django, react, spring_boot, etc.)
            project_type: Type (web_app, api_rest, mobile_app, etc.)
        
        Returns:
            Dict avec tous les fichiers générés
        """
        
        self.logger.info(f"🌐 Génération {language}/{framework} - Type: {project_type}")
        
        # Valider langage et framework
        if not self._validate_language_framework(language, framework):
            self.logger.error(f"❌ Combinaison invalide: {language}/{framework}")
            return await self._generate_fallback(description, language)
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"multilang-{language}-{framework}",
            system_message=self._get_system_message(language, framework, project_type)
        )
        
        prompt = self._build_prompt(description, language, framework, project_type)
        
        try:
            response = await chat.with_model("openai", "gpt-4o").send_message(
                UserMessage(text=prompt)
            )
            
            # Parser les fichiers
            files = self._parse_response(response, language, framework)
            
            self.logger.info(f"✅ {len(files)} fichiers générés pour {language}/{framework}")
            
            return files
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération {language}/{framework}: {e}")
            return await self._generate_fallback(description, language)
    
    def _validate_language_framework(self, language: str, framework: str) -> bool:
        """Valide que la combinaison langage/framework est supportée"""
        
        language = language.lower()
        framework = framework.lower()
        
        if language not in self.SUPPORTED_LANGUAGES:
            return False
        
        if framework not in self.SUPPORTED_LANGUAGES[language]:
            # Accepter quand même si framework vide
            return framework == "" or framework == "none"
        
        return True
    
    def _get_system_message(self, language: str, framework: str, project_type: str) -> str:
        """System message spécialisé par langage"""
        
        messages = {
            "python": f"""Tu es un expert Python senior spécialisé en {framework}.
Génère du code Python PRODUCTION-READY, propre et idiomatique.""",

            "javascript": f"""Tu es un expert JavaScript/TypeScript senior spécialisé en {framework}.
Génère du code moderne (ES6+), propre et performant.""",

            "java": f"""Tu es un expert Java senior spécialisé en {framework}.
Génère du code Java moderne (Java 17+), avec Spring Boot best practices.""",

            "go": f"""Tu es un expert Go senior spécialisé en {framework}.
Génère du code Go idiomatique, concurrent et performant.""",

            "rust": f"""Tu es un expert Rust senior spécialisé en {framework}.
Génère du code Rust sûr, performant et idiomatique.""",

            "csharp": f"""Tu es un expert C# senior spécialisé en {framework}.
Génère du code C# moderne (.NET 7+), avec async/await.""",

            "php": f"""Tu es un expert PHP senior spécialisé en {framework}.
Génère du code PHP moderne (8.x), orienté objet et propre.""",

            "ruby": f"""Tu es un expert Ruby senior spécialisé en {framework}.
Génère du code Ruby idiomatique, élégant et testé."""
        }
        
        base = messages.get(language, "Tu es un développeur expert senior.")
        
        return f"""{base}

Type de projet: {project_type}

EXIGENCES CRITIQUES:
- Code COMPLET et PRODUCTION-READY
- Structure de projet professionnelle
- Best practices du langage {language}
- Configuration complète ({framework})
- AUCUN placeholder ou TODO
- Tests unitaires inclus
- Documentation (README, comments)
- Déployable immédiatement

Génère un VRAI projet professionnel, pas un exemple."""
    
    def _build_prompt(
        self,
        description: str,
        language: str,
        framework: str,
        project_type: str
    ) -> str:
        """Construit le prompt de génération"""
        
        # Structure de fichiers par langage/framework
        structures = self._get_project_structure(language, framework, project_type)
        
        prompt = f"""Génère un projet {project_type} COMPLET en {language} avec {framework}:

DESCRIPTION: {description}

STRUCTURE ATTENDUE:
{structures}

FICHIERS À GÉNÉRER (TOUS NÉCESSAIRES):
{self._get_required_files(language, framework, project_type)}

FORMAT DE RÉPONSE:
Pour chaque fichier:

FICHIER: chemin/vers/fichier.ext
```{language}
code complet ici
```

IMPORTANT:
- Génère TOUS les fichiers listés
- Code COMPLET (pas de "# TODO" ou "...")
- Syntaxe 100% correcte
- Prêt à exécuter/déployer
- Tests inclus

Génère MAINTENANT tous les fichiers."""
        
        return prompt
    
    def _get_project_structure(self, language: str, framework: str, project_type: str) -> str:
        """Retourne la structure de projet recommandée"""
        
        structures = {
            "python": {
                "fastapi": """
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── config.py
├── tests/
├── requirements.txt
├── .env.example
└── README.md""",
                
                "django": """
project/
├── manage.py
├── project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   └── core/
├── requirements.txt
└── README.md"""
            },
            
            "javascript": {
                "react": """
project/
├── src/
│   ├── App.jsx
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   └── utils/
├── public/
├── package.json
└── README.md""",
                
                "express": """
project/
├── src/
│   ├── server.js
│   ├── routes/
│   ├── controllers/
│   ├── models/
│   └── middleware/
├── tests/
├── package.json
└── README.md"""
            }
        }
        
        return structures.get(language, {}).get(framework, "Structure standard")
    
    def _get_required_files(self, language: str, framework: str, project_type: str) -> str:
        """Liste les fichiers obligatoires"""
        
        files = {
            "python": "main.py, requirements.txt, README.md, .env.example, tests/test_main.py",
            "javascript": "package.json, src/index.js, README.md, .env.example, tests/index.test.js",
            "java": "pom.xml, src/main/java/Main.java, README.md, application.properties",
            "go": "main.go, go.mod, README.md, .env.example",
            "rust": "Cargo.toml, src/main.rs, README.md",
        }
        
        return files.get(language, "README.md, main file, config file")
    
    def _parse_response(self, response: str, language: str, framework: str) -> Dict[str, str]:
        """Parse la réponse et extrait les fichiers"""
        
        import re
        
        files = {}
        
        # Pattern: FICHIER: path suivi de ```code```
        pattern = r'FICHIER:\s*([^\n]+)\s*```(?:\w+)?\n(.*?)```'
        matches = re.finditer(pattern, response, re.DOTALL)
        
        for match in matches:
            file_path = match.group(1).strip()
            content = match.group(2).strip()
            files[file_path] = content
        
        # Si aucun fichier trouvé, essayer parsing différent
        if not files:
            self.logger.warning("⚠️ Aucun fichier parsé - Génération fallback")
            return {}
        
        return files
    
    async def _generate_fallback(self, description: str, language: str) -> Dict[str, str]:
        """Génère des fichiers de fallback basiques mais fonctionnels"""
        
        fallbacks = {
            "python": {
                "main.py": f"""#!/usr/bin/env python3
'''
{description}
Generated by Vectort.io
'''

def main():
    print("Application démarrée")
    # TODO: Implémenter logique

if __name__ == "__main__":
    main()
""",
                "README.md": f"# {description}\n\nProjet Python généré par Vectort.io"
            },
            
            "javascript": {
                "index.js": f"""// {description}
// Generated by Vectort.io

console.log('Application démarrée');

module.exports = {{}};
""",
                "package.json": f"""{{"name": "vectort-project", "version": "1.0.0"}}"""
            }
        }
        
        return fallbacks.get(language, {
            "README.md": f"# {description}\n\nProjet généré par Vectort.io"
        })


# Export
__all__ = ['MultiLanguageAgent']
