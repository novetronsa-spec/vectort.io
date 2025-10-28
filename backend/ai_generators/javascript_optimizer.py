"""
Système d'optimisation JavaScript/Node.js pour Vectort.io
Gère TOUS les cas de génération JavaScript avec timeouts adaptatifs
Performance maximale et robustesse totale
"""

import asyncio
import logging
import re
import json
from typing import Dict, List, Optional, Tuple
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class JavaScriptOptimizer:
    """
    Optimiseur spécialisé pour génération JavaScript/Node.js
    
    Fonctionnalités:
    - Timeouts adaptatifs intelligents selon complexité
    - Parsing amélioré avec récupération d'erreurs
    - Fallbacks robustes pour chaque type de projet
    - Prompts optimisés pour syntaxe JavaScript parfaite
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger("JavaScriptOptimizer")
    
    def calculate_adaptive_timeout(
        self,
        description: str,
        project_type: str,
        features: List[str] = None
    ) -> float:
        """
        Calcule timeout adaptatif selon complexité du projet JavaScript
        
        Facteurs pris en compte:
        - Longueur et complexité de la description
        - Type de projet (API REST < Web App < Full-Stack)
        - Nombre de features demandées
        - Mots-clés de complexité (authentication, real-time, database, etc.)
        
        Returns:
            Timeout en secondes (30-180s)
        """
        
        # Base timeout pour JavaScript
        base_timeout = 30.0
        
        # Facteur 1: Longueur description
        desc_length = len(description)
        if desc_length > 500:
            base_timeout += 40.0
        elif desc_length > 300:
            base_timeout += 30.0
        elif desc_length > 150:
            base_timeout += 20.0
        elif desc_length > 75:
            base_timeout += 10.0
        
        # Facteur 2: Type de projet
        complexity_map = {
            "full_stack": 50.0,       # Full-Stack le plus complexe
            "web_app": 40.0,          # Web App complexe
            "microservice": 35.0,     # Microservices
            "api_rest": 25.0,         # API REST
            "api_graphql": 30.0,      # GraphQL plus complexe
            "cli_tool": 15.0,         # CLI le plus simple
            "library": 20.0           # Library simple
        }
        base_timeout += complexity_map.get(project_type.lower(), 25.0)
        
        # Facteur 3: Features demandées
        if features:
            feature_count = len(features)
            if feature_count > 10:
                base_timeout += 30.0
            elif feature_count > 7:
                base_timeout += 20.0
            elif feature_count > 4:
                base_timeout += 10.0
        
        # Facteur 4: Mots-clés de complexité
        complexity_keywords = {
            "authentication": 15.0,
            "real-time": 20.0,
            "websocket": 20.0,
            "database": 15.0,
            "mongodb": 12.0,
            "postgresql": 12.0,
            "mysql": 12.0,
            "redis": 10.0,
            "payment": 18.0,
            "stripe": 15.0,
            "oauth": 15.0,
            "jwt": 10.0,
            "email": 10.0,
            "upload": 12.0,
            "image": 12.0,
            "video": 15.0,
            "chat": 18.0,
            "notification": 12.0,
            "search": 12.0,
            "analytics": 12.0,
            "admin": 15.0,
            "dashboard": 15.0,
            "api": 10.0,
            "graphql": 15.0,
            "docker": 8.0,
            "kubernetes": 10.0,
            "ci/cd": 8.0,
            "testing": 8.0,
            "typescript": 12.0
        }
        
        desc_lower = description.lower()
        for keyword, bonus in complexity_keywords.items():
            if keyword in desc_lower:
                base_timeout += bonus
                self.logger.debug(f"🔍 Keyword '{keyword}' found, adding +{bonus}s")
        
        # Cap maximum à 180s (3 minutes)
        final_timeout = min(180.0, base_timeout)
        
        self.logger.info(f"⏱️ Timeout adaptatif JavaScript: {final_timeout}s (base: {base_timeout}s)")
        
        return final_timeout
    
    def get_optimized_javascript_prompt(
        self,
        description: str,
        framework: str = "express",
        language: str = "javascript"
    ) -> str:
        """
        Génère un prompt optimisé pour JavaScript/Node.js
        
        Gère:
        - React/Vue/Angular/Svelte pour frontend
        - Express/Fastify/Koa pour backend
        - JavaScript vs TypeScript
        """
        
        framework_lower = framework.lower()
        is_typescript = language.lower() == "typescript"
        
        # Prompts spécialisés par framework
        if framework_lower in ["react", "nextjs", "next.js"]:
            return self._get_react_optimized_prompt(description, is_typescript)
        elif framework_lower in ["vue", "vuejs", "vue.js"]:
            return self._get_vue_optimized_prompt(description, is_typescript)
        elif framework_lower in ["angular"]:
            return self._get_angular_optimized_prompt(description, is_typescript)
        elif framework_lower in ["express", "fastify", "koa", "nodejs", "node.js"]:
            return self._get_backend_optimized_prompt(description, framework_lower, is_typescript)
        else:
            return self._get_generic_javascript_prompt(description, is_typescript)
    
    def _get_react_optimized_prompt(self, description: str, typescript: bool) -> str:
        """Prompt optimisé pour React/Next.js"""
        
        lang_specific = """
TypeScript:
- Utilise interfaces et types stricts
- Props avec PropTypes ou types TypeScript
- Typage complet des hooks et fonctions
""" if typescript else """
JavaScript:
- Utilise PropTypes pour validation
- JSDoc pour documentation
- Commentaires clairs sur les props
"""
        
        return f"""Tu es un EXPERT REACT SENIOR.

Génère une application React COMPLÈTE et PROFESSIONNELLE selon cette description:

{description}

EXIGENCES CRITIQUES:

{lang_specific}

1. COMPOSANTS REACT MODERNES:
   - Hooks (useState, useEffect, useContext, useCallback, useMemo)
   - Functional components UNIQUEMENT
   - Props drilling évité (Context API si nécessaire)
   - React 18+ patterns

2. SYNTAXE JSX PARFAITE:
   - Fermeture correcte de TOUS les tags (<div></div> ou <img />)
   - Attributs en camelCase (className, onClick, onChange)
   - Expressions JavaScript entre {{  }}
   - Pas de HTML invalide dans JSX
   - Keys uniques pour les listes

3. GESTION D'ÉTAT:
   - useState pour état local
   - useEffect pour side effects
   - useContext pour état global si nécessaire
   - Pas de mutations directes de l'état

4. PERFORMANCE:
   - useMemo pour calculs coûteux
   - useCallback pour fonctions callback
   - React.memo si nécessaire
   - Lazy loading si applicable

5. CODE COMPLET - JAMAIS:
   - TODO ou placeholders
   - Commentaires "à implémenter"
   - Code incomplet
   - Erreurs de syntaxe

Génère le code React COMPLET, FONCTIONNEL et SANS ERREURS."""
    
    def _get_vue_optimized_prompt(self, description: str, typescript: bool) -> str:
        """Prompt optimisé pour Vue.js"""
        
        return f"""Tu es un EXPERT VUE.JS SENIOR.

Génère une application Vue.js COMPLÈTE selon:

{description}

EXIGENCES CRITIQUES:

1. VUE 3 COMPOSITION API:
   - setup() avec ref, reactive, computed
   - Lifecycle hooks (onMounted, onUpdated)
   - watch et watchEffect
   - Pas d'Options API sauf si nécessaire

2. TEMPLATE SYNTAX:
   - v-model, v-if, v-for, v-bind, v-on
   - Pas d'erreurs de template
   - Keys pour v-for
   - Expressions valides

3. RÉACTIVITÉ:
   - ref() pour primitives
   - reactive() pour objets
   - toRefs si nécessaire
   - Pas de perte de réactivité

Code COMPLET et FONCTIONNEL UNIQUEMENT."""
    
    def _get_angular_optimized_prompt(self, description: str, typescript: bool) -> str:
        """Prompt optimisé pour Angular"""
        
        return f"""Tu es un EXPERT ANGULAR SENIOR.

Génère une application Angular COMPLÈTE selon:

{description}

EXIGENCES CRITIQUES:

1. ANGULAR MODERNE (14+):
   - TypeScript OBLIGATOIRE
   - Components avec decorators
   - Services avec dependency injection
   - Modules NgModule

2. TEMPLATE SYNTAX:
   - *ngIf, *ngFor, *ngSwitch
   - Property binding [prop]
   - Event binding (event)
   - Two-way binding [(ngModel)]

3. SERVICES ET DI:
   - Injectable services
   - HttpClient pour API
   - RxJS observables
   - Error handling

Code Angular COMPLET et TYPÉ."""
    
    def _get_backend_optimized_prompt(
        self,
        description: str,
        framework: str,
        typescript: bool
    ) -> str:
        """Prompt optimisé pour Backend Node.js"""
        
        framework_specific = {
            "express": "Express.js avec middleware",
            "fastify": "Fastify avec plugins",
            "koa": "Koa avec middleware",
            "nodejs": "Node.js pur avec http module"
        }
        
        framework_desc = framework_specific.get(framework, "Express.js")
        
        return f"""Tu es un EXPERT BACKEND NODE.JS SENIOR.

Génère une API REST {framework_desc} COMPLÈTE selon:

{description}

EXIGENCES CRITIQUES:

1. ARCHITECTURE BACKEND:
   - Routes RESTful (/api/resource)
   - Middleware (cors, helmet, morgan)
   - Error handling middleware
   - Validation des inputs

2. SÉCURITÉ:
   - Helmet pour headers sécurisés
   - CORS configuré correctement
   - Validation avec Joi ou Zod
   - Rate limiting si nécessaire
   - JWT authentication si demandé

3. BASE DE DONNÉES:
   - Mongoose pour MongoDB
   - Sequelize/TypeORM pour SQL
   - Migrations si applicable
   - Connection pooling

4. CODE PROPRE:
   - async/await (pas de callbacks)
   - Try/catch pour error handling
   - Status codes HTTP corrects
   - Logging approprié

5. STRUCTURE:
   - routes/
   - controllers/
   - models/
   - middleware/
   - utils/

Code Backend Node.js COMPLET, SÉCURISÉ et FONCTIONNEL."""
    
    def _get_generic_javascript_prompt(self, description: str, typescript: bool) -> str:
        """Prompt générique JavaScript"""
        
        return f"""Tu es un EXPERT JAVASCRIPT SENIOR.

Génère du code JavaScript COMPLET selon:

{description}

EXIGENCES:

1. JAVASCRIPT MODERNE (ES6+):
   - const/let (pas var)
   - Arrow functions
   - Destructuring
   - Spread operator
   - Template literals
   - Async/await

2. CODE PROPRE:
   - Nommage clair
   - Fonctions courtes et focalisées
   - Pas de code dupliqué
   - Commentaires si nécessaire

3. ERROR HANDLING:
   - Try/catch appropriés
   - Validation des inputs
   - Messages d'erreur clairs

Code JavaScript COMPLET et FONCTIONNEL."""
    
    async def generate_with_fallback(
        self,
        description: str,
        project_type: str,
        framework: str,
        language: str = "javascript",
        features: List[str] = None
    ) -> Dict:
        """
        Génère code JavaScript avec fallbacks robustes
        
        Stratégie:
        1. Tentative avec prompt optimisé
        2. Si timeout, retry avec timeout augmenté
        3. Si parsing échoue, tentative avec parsing alternatif
        4. Si tout échoue, génération basique minimale
        
        Returns:
            Dict avec code généré ou fallback
        """
        
        # Calcul timeout adaptatif
        base_timeout = self.calculate_adaptive_timeout(description, project_type, features)
        
        # Tentative 1: Génération optimisée
        try:
            self.logger.info("🚀 Tentative 1: Génération optimisée")
            result = await self._attempt_generation(
                description, project_type, framework, language, base_timeout
            )
            
            if result and self._validate_javascript_syntax(result):
                self.logger.info("✅ Génération optimisée réussie!")
                return result
            else:
                self.logger.warning("⚠️ Validation syntaxe échouée, retry avec corrections")
        
        except asyncio.TimeoutError:
            self.logger.warning(f"⏱️ Timeout après {base_timeout}s, retry avec timeout augmenté")
        
        except Exception as e:
            self.logger.error(f"❌ Erreur génération: {e}")
        
        # Tentative 2: Retry avec timeout augmenté et prompt simplifié
        try:
            extended_timeout = base_timeout * 1.5
            self.logger.info(f"🔄 Tentative 2: Retry avec timeout {extended_timeout}s")
            
            result = await self._attempt_generation(
                description, project_type, framework, language,
                extended_timeout, simplified=True
            )
            
            if result and self._validate_javascript_syntax(result):
                self.logger.info("✅ Retry réussi!")
                return result
        
        except Exception as e:
            self.logger.error(f"❌ Retry échoué: {e}")
        
        # Tentative 3: Fallback basique minimal
        self.logger.warning("🆘 Utilisation fallback basique")
        return self._generate_basic_fallback(description, framework, language)
    
    async def _attempt_generation(
        self,
        description: str,
        project_type: str,
        framework: str,
        language: str,
        timeout: float,
        simplified: bool = False
    ) -> Optional[Dict]:
        """Tente de générer code JavaScript"""
        
        try:
            # Création LlmChat
            llm = LlmChat(api_key=self.api_key)
            llm = llm.with_model("gpt-4o")
            
            # Prompt optimisé
            if not simplified:
                prompt = self.get_optimized_javascript_prompt(description, framework, language)
            else:
                prompt = f"Génère code {framework} simple pour: {description}"
            
            # Génération avec timeout
            response = await asyncio.wait_for(
                llm.send_message(UserMessage(content=prompt)),
                timeout=timeout
            )
            
            # Parsing JSON
            code_text = response.text if hasattr(response, 'text') else str(response)
            
            # Tentative parsing JSON
            try:
                if "```json" in code_text:
                    json_match = re.search(r"```json\s*(\{.*?\})\s*```", code_text, re.DOTALL)
                    if json_match:
                        code_text = json_match.group(1)
                
                parsed = json.loads(code_text)
                return parsed
            
            except json.JSONDecodeError:
                # Parsing alternatif
                self.logger.warning("⚠️ JSON parsing échoué, tentative extraction code")
                return self._extract_code_from_text(code_text, framework)
        
        except Exception as e:
            self.logger.error(f"❌ Erreur _attempt_generation: {e}")
            return None
    
    def _extract_code_from_text(self, text: str, framework: str) -> Dict:
        """Extrait code depuis texte non-JSON"""
        
        result = {}
        
        # Extraction code JavaScript
        js_patterns = [
            r"```javascript\s*(.*?)\s*```",
            r"```js\s*(.*?)\s*```",
            r"```typescript\s*(.*?)\s*```",
            r"```ts\s*(.*?)\s*```"
        ]
        
        for pattern in js_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                result["js_code"] = matches[0]
                break
        
        # Extraction JSX/React
        jsx_pattern = r"```jsx\s*(.*?)\s*```"
        jsx_matches = re.findall(jsx_pattern, text, re.DOTALL)
        if jsx_matches:
            result["react_code"] = jsx_matches[0]
        
        # Extraction CSS
        css_pattern = r"```css\s*(.*?)\s*```"
        css_matches = re.findall(css_pattern, text, re.DOTALL)
        if css_matches:
            result["css_code"] = css_matches[0]
        
        # Extraction HTML
        html_pattern = r"```html\s*(.*?)\s*```"
        html_matches = re.findall(html_pattern, text, re.DOTALL)
        if html_matches:
            result["html_code"] = html_matches[0]
        
        return result if result else None
    
    def _validate_javascript_syntax(self, code_dict: Dict) -> bool:
        """Valide syntaxe JavaScript basique"""
        
        if not code_dict:
            return False
        
        # Vérifie que du code existe
        code_fields = ["js_code", "react_code", "backend_code", "html_code"]
        has_code = any(code_dict.get(field) for field in code_fields)
        
        if not has_code:
            self.logger.warning("⚠️ Aucun code trouvé dans résultat")
            return False
        
        # Validation basique syntaxe
        for field in code_fields:
            code = code_dict.get(field, "")
            if code and not self._basic_syntax_check(code):
                self.logger.warning(f"⚠️ Erreur syntaxe dans {field}")
                return False
        
        return True
    
    def _basic_syntax_check(self, code: str) -> bool:
        """Vérification syntaxe basique"""
        
        if not code:
            return True
        
        # Vérifications simples
        checks = [
            # Parenth équilibrées
            code.count("(") == code.count(")"),
            # Brackets équilibrées
            code.count("[") == code.count("]"),
            # Braces équilibrées
            code.count("{") == code.count("}"),
            # Pas de TODO
            "TODO" not in code.upper(),
            # Longueur minimale
            len(code.strip()) > 50
        ]
        
        return all(checks)
    
    def _generate_basic_fallback(
        self,
        description: str,
        framework: str,
        language: str
    ) -> Dict:
        """Génère fallback basique minimal mais fonctionnel"""
        
        self.logger.info(f"🆘 Génération fallback basique pour {framework}")
        
        if framework.lower() in ["react", "nextjs"]:
            return self._fallback_react(description)
        elif framework.lower() in ["vue", "vuejs"]:
            return self._fallback_vue(description)
        elif framework.lower() in ["express", "fastify", "koa", "nodejs"]:
            return self._fallback_backend(description)
        else:
            return self._fallback_generic(description)
    
    def _fallback_react(self, description: str) -> Dict:
        """Fallback React minimal"""
        
        return {
            "react_code": f"""import React, {{ useState }} from 'react';

function App() {{
  const [message, setMessage] = useState('Application React');
  
  return (
    <div className="app">
      <header>
        <h1>{{message}}</h1>
        <p>{description[:100]}</p>
      </header>
      <main>
        <button onClick={{() => setMessage('Application fonctionnelle')}}>
          Cliquez ici
        </button>
      </main>
    </div>
  );
}}

export default App;""",
            "css_code": """.app {
  font-family: Arial, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

header {
  text-align: center;
  padding: 40px 0;
}

h1 {
  color: #333;
  font-size: 2.5rem;
}

button {
  background: #007bff;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

button:hover {
  background: #0056b3;
}""",
            "html_code": """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Application React</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>"""
        }
    
    def _fallback_vue(self, description: str) -> Dict:
        """Fallback Vue minimal"""
        
        return {
            "js_code": f"""<template>
  <div class="app">
    <header>
      <h1>{{{{ message }}}}</h1>
      <p>{description[:100]}</p>
    </header>
    <main>
      <button @click="changeMessage">Cliquez ici</button>
    </main>
  </div>
</template>

<script>
import {{ ref }} from 'vue';

export default {{
  name: 'App',
  setup() {{
    const message = ref('Application Vue');
    
    const changeMessage = () => {{
      message.value = 'Application fonctionnelle';
    }};
    
    return {{
      message,
      changeMessage
    }};
  }}
}};
</script>

<style scoped>
.app {{
  font-family: Arial, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}}

header {{
  text-align: center;
  padding: 40px 0;
}}

h1 {{
  color: #333;
  font-size: 2.5rem;
}}

button {{
  background: #42b883;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}}
</style>"""
        }
    
    def _fallback_backend(self, description: str) -> Dict:
        """Fallback Backend Express minimal"""
        
        return {
            "backend_code": f"""const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Routes
app.get('/api', (req, res) => {{
  res.json({{
    message: 'API Backend fonctionnelle',
    description: '{description[:100]}',
    status: 'success'
  }});
}});

app.get('/api/health', (req, res) => {{
  res.json({{ status: 'healthy', timestamp: new Date().toISOString() }});
}});

// Error handling
app.use((err, req, res, next) => {{
  console.error(err.stack);
  res.status(500).json({{
    error: 'Something went wrong!',
    message: err.message
  }});
}});

// Start server
app.listen(PORT, () => {{
  console.log(`Server running on port ${{PORT}}`);
}});

module.exports = app;"""
        }
    
    def _fallback_generic(self, description: str) -> Dict:
        """Fallback générique"""
        
        return {
            "js_code": f"""// Application JavaScript
console.log('Application JavaScript');

const app = {{
  description: '{description[:100]}',
  
  init() {{
    console.log('Initializing application...');
    this.setupEventListeners();
  }},
  
  setupEventListeners() {{
    document.addEventListener('DOMContentLoaded', () => {{
      console.log('DOM loaded');
    }});
  }},
  
  run() {{
    console.log('Application running');
  }}
}};

app.init();
app.run();""",
            "html_code": """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Application JavaScript</title>
</head>
<body>
  <h1>Application JavaScript</h1>
  <script src="app.js"></script>
</body>
</html>"""
        }
