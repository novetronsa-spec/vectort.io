# 🚀 GUIDE D'UTILISATION - JavaScript Optimizer

## Utilisation Simple

### 1. Import

```python
from ai_generators.javascript_optimizer import JavaScriptOptimizer
from ai_generators.multi_agent_orchestrator import generate_with_multi_agents
```

### 2. Utilisation Directe (API High-Level)

```python
import asyncio

# Génération automatique avec détection JavaScript
result = await generate_with_multi_agents(
    description="Une application React avec compteur",
    framework="react",
    project_type="web_app",
    api_key="sk-emergent-xxxxx"
)

# Résultat:
# {
#   "react_code": "import React from 'react'...",
#   "css_code": ".app { ... }",
#   "html_code": "<!DOCTYPE html>..."
# }
```

### 3. Utilisation Avancée (Contrôle Total)

```python
# Instanciation directe
optimizer = JavaScriptOptimizer(api_key="sk-emergent-xxxxx")

# Génération avec contrôle des paramètres
result = await optimizer.generate_with_fallback(
    description="API REST pour gestion utilisateurs",
    project_type="api_rest",
    framework="express",
    language="javascript",
    features=["authentication", "database", "validation"]
)

# Résultat:
# {
#   "backend_code": "const express = require('express')..."
# }
```

---

## Exemples par Framework

### React

```python
result = await generate_with_multi_agents(
    description="""
    Application React e-commerce avec:
    - Authentification utilisateur
    - Panier d'achat
    - Liste produits avec filtres
    - Checkout avec paiement
    """,
    framework="react",
    project_type="web_app",
    api_key="sk-emergent-xxxxx"
)

# Génère:
# - react_code: Composants avec hooks
# - css_code: Styles responsive
# - html_code: Template HTML5
```

**Timeout calculé:** ~120s (complexe avec auth + payment)

---

### Express/Node.js

```python
result = await generate_with_multi_agents(
    description="""
    API REST Node.js avec Express:
    - CRUD utilisateurs
    - Authentification JWT
    - Validation des données
    - Error handling
    """,
    framework="express",
    project_type="api_rest",
    api_key="sk-emergent-xxxxx"
)

# Génère:
# - backend_code: Server Express complet avec routes
```

**Timeout calculé:** ~90s (moyen avec auth + validation)

---

### Vue.js

```python
result = await generate_with_multi_agents(
    description="""
    Application Vue.js todo list:
    - Composition API
    - Ajout/suppression tâches
    - Filtres (toutes, actives, complétées)
    - LocalStorage pour persistance
    """,
    framework="vue",
    project_type="web_app",
    api_key="sk-emergent-xxxxx"
)

# Génère:
# - js_code: Composant Vue avec Composition API
```

**Timeout calculé:** ~75s (simple avec quelques features)

---

## Calcul des Timeouts

### Formule

```
Timeout = Base (25s)
        + Description (3-45s)
        + Type Projet (10-55s)
        + Features (2-40s)
        + Keywords (10-22s par keyword)
        
Max: 180s (3 minutes)
```

### Exemples Concrets

| Description | Type | Features | Keywords | Timeout |
|-------------|------|----------|----------|---------|
| "Simple counter" | web_app | 0 | 0 | **63s** |
| "Todo list with filters" | web_app | 2 | 0 | **70s** |
| "E-commerce with auth" | web_app | 2 | auth, database | **108s** |
| "Full-stack chat app" | full_stack | 6 | auth, realtime, websocket, chat | **180s** (max) |

---

## Personnalisation

### Changer les Timeouts

```python
# Modifier la base
optimizer.base_timeout = 30.0  # Au lieu de 25.0

# Modifier les multiplicateurs
optimizer.timeout_multipliers = {
    "simple": 1.0,
    "medium": 1.5,
    "complex": 2.0
}
```

### Ajouter Keywords

```python
# Dans javascript_optimizer.py, ligne ~100
complexity_keywords = {
    "authentication": 18.0,
    "real-time": 22.0,
    # Ajouter vos keywords
    "blockchain": 25.0,
    "machine-learning": 30.0,
}
```

### Custom Fallback

```python
def _fallback_custom(self, description: str) -> Dict:
    return {
        "js_code": f"// Code custom pour: {description}",
        "readme": "# Custom Project"
    }

# Utiliser
optimizer._fallback_custom = _fallback_custom
```

---

## Debugging

### Activer Logs Détaillés

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("JavaScriptOptimizer")
logger.setLevel(logging.DEBUG)
```

### Logs Disponibles

```
INFO - ⏱️ Timeout adaptatif JavaScript: 108s
DEBUG - 📝 Description: 66 chars
DEBUG - 📦 Type projet: web_app (+35s)
DEBUG - ⚡ Features: 2 (+12s)
DEBUG - 🔑 Keywords: 2 trouvés (+34s)
DEBUG - 🎯 Total: 108s → 108s

INFO - 🚀 Tentative 1: Génération optimisée
INFO - ⚠️ JSON parsing échoué, tentative extraction code
INFO - ✅ Code extrait directement: 2023 chars
```

---

## Gestion des Erreurs

### Erreurs Communes

#### 1. Timeout

```python
try:
    result = await optimizer.generate_with_fallback(...)
except asyncio.TimeoutError:
    print("⏱️ Timeout - Le projet est peut-être trop complexe")
    # Le système passe automatiquement au fallback
```

#### 2. Parsing Échoué

```python
# Le système gère automatiquement:
# 1. Tentative JSON
# 2. Tentative Markdown
# 3. Extraction intelligente
# 4. Fallback garanti

# Vous recevez toujours du code!
```

#### 3. API Key Invalide

```python
from emergentintegrations.llm.chat import LlmChat

try:
    result = await optimizer.generate_with_fallback(...)
except Exception as e:
    if "API key" in str(e):
        print("❌ Clé API invalide ou expirée")
```

---

## Tests

### Test Rapide

```python
# Test avec fallback seulement (rapide)
optimizer = JavaScriptOptimizer("dummy_key")
fallback = optimizer._fallback_react("Test app")

assert fallback["react_code"]
assert "useState" in fallback["react_code"]
print("✅ Fallback fonctionne!")
```

### Test Complet avec API

```python
# Test avec vraie génération GPT-4o
optimizer = JavaScriptOptimizer("sk-emergent-xxxxx")

result = await optimizer.generate_with_fallback(
    description="Simple counter",
    project_type="web_app",
    framework="react",
    language="javascript",
    features=[]
)

assert result
assert len(result.get("react_code", "")) > 500
print(f"✅ Génération réussie: {len(result['react_code'])} chars")
```

---

## Intégration FastAPI

### Endpoint Simple

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class GenerateRequest(BaseModel):
    description: str
    framework: str = "react"
    project_type: str = "web_app"

@app.post("/generate/javascript")
async def generate_javascript(request: GenerateRequest):
    try:
        result = await generate_with_multi_agents(
            description=request.description,
            framework=request.framework,
            project_type=request.project_type,
            api_key=EMERGENT_LLM_KEY
        )
        
        return {
            "success": True,
            "code": result,
            "files": len(result)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Avec Streaming (SSE)

```python
from fastapi.responses import StreamingResponse

@app.post("/generate/javascript/stream")
async def generate_javascript_stream(request: GenerateRequest):
    
    async def event_generator():
        yield f"data: {{'status': 'started'}}\n\n"
        
        # Calcul timeout
        optimizer = JavaScriptOptimizer(EMERGENT_LLM_KEY)
        timeout = optimizer.calculate_adaptive_timeout(
            request.description,
            request.project_type,
            []
        )
        yield f"data: {{'status': 'timeout_calculated', 'timeout': {timeout}}}\n\n"
        
        # Génération
        yield f"data: {{'status': 'generating'}}\n\n"
        
        result = await generate_with_multi_agents(...)
        
        yield f"data: {{'status': 'completed', 'code': {result}}}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

---

## Performance

### Optimisations

1. **Cache les résultats**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_prompt(framework: str, language: str):
    return optimizer.get_optimized_javascript_prompt(
        description="...",
        framework=framework,
        language=language
    )
```

2. **Paralléliser les générations**
```python
tasks = [
    generate_with_multi_agents(..., framework="react"),
    generate_with_multi_agents(..., framework="express"),
]

results = await asyncio.gather(*tasks)
```

3. **Timeout ajusté**
```python
# Pour projets simples, réduire base timeout
optimizer.base_timeout = 20.0  # Au lieu de 25s
```

---

## FAQ

### Q: Comment forcer l'utilisation du fallback?

```python
# Appeler directement le fallback
result = optimizer._fallback_react(description)
```

### Q: Comment obtenir du TypeScript?

```python
result = await generate_with_multi_agents(
    description="...",
    framework="react",
    language="typescript"  # Active les prompts TypeScript
)
```

### Q: Le timeout est trop court, comment l'augmenter?

```python
# Méthode 1: Ajouter plus de keywords dans la description
description = "Application avec authentication, database, real-time, payment"

# Méthode 2: Augmenter la base
optimizer.base_timeout = 40.0

# Méthode 3: Forcer un timeout
result = await optimizer._attempt_generation(
    ...,
    timeout=300.0  # 5 minutes
)
```

### Q: Comment avoir plusieurs fichiers?

Le système génère automatiquement plusieurs fichiers:
- `react_code` → App.jsx
- `css_code` → styles.css
- `html_code` → index.html
- `backend_code` → server.js

---

## Support

**Documentation complète:** `/app/ARCHITECTURE_JAVASCRIPT_OPTIMIZER.md`

**Fichiers sources:**
- `/app/backend/ai_generators/javascript_optimizer.py`
- `/app/backend/ai_generators/multi_agent_orchestrator.py`

**Tests:**
- `/app/backend/test_javascript_optimization.py`
- `/app/backend/test_js_100_percent.py`
- `/app/backend/test_js_real_generation.py`

---

**Version:** 1.0.0  
**Dernière mise à jour:** 2025-10-28  
**Statut:** Production Ready ✅
