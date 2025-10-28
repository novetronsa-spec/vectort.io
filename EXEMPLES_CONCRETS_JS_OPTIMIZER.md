# 💡 EXEMPLES CONCRETS - JavaScript Optimizer

## Cas d'Usage Réels

---

## 1️⃣ Application React E-Commerce

### Requête

```python
result = await generate_with_multi_agents(
    description="""
    Application e-commerce React avec:
    - Catalogue de produits avec recherche et filtres
    - Panier d'achat avec gestion quantités
    - Authentification utilisateur (login/signup)
    - Page de paiement avec Stripe
    - Historique des commandes
    - Dashboard admin pour gérer produits
    """,
    framework="react",
    project_type="web_app",
    api_key=EMERGENT_LLM_KEY
)
```

### Timeout Calculé
```
Base: 25s
Description (159 chars): +25s
Type web_app: +35s
Features: 6 (+20s)
Keywords détectés:
  - authentication: +18s
  - payment: +20s
  - stripe: +18s
  - admin: +18s
  - database: +16s
  - search: +14s
────────────────────
Total: 180s (cap max)
```

### Résultat Attendu
```javascript
{
  "react_code": "
    import React, { useState, useEffect } from 'react';
    import { BrowserRouter, Routes, Route } from 'react-router-dom';
    
    // Composants
    import ProductCatalog from './components/ProductCatalog';
    import ShoppingCart from './components/ShoppingCart';
    import Checkout from './components/Checkout';
    import AdminDashboard from './components/AdminDashboard';
    
    function App() {
      const [cart, setCart] = useState([]);
      const [user, setUser] = useState(null);
      
      // ... (2500+ caractères)
    }
  ",
  
  "css_code": "
    .product-catalog { ... }
    .cart-item { ... }
    .checkout-form { ... }
  ",
  
  "html_code": "<!DOCTYPE html>..."
}
```

---

## 2️⃣ API REST Node.js/Express

### Requête

```python
result = await generate_with_multi_agents(
    description="""
    API REST Node.js pour gestion de blog:
    - CRUD articles (GET, POST, PUT, DELETE)
    - CRUD commentaires
    - Authentification JWT
    - Upload d'images
    - Recherche full-text
    - Validation des données avec Joi
    - Rate limiting
    """,
    framework="express",
    project_type="api_rest",
    api_key=EMERGENT_LLM_KEY
)
```

### Timeout Calculé
```
Base: 25s
Description (152 chars): +25s
Type api_rest: +20s
Features: 7 (+25s)
Keywords:
  - authentication: +18s
  - jwt: +12s
  - upload: +14s
  - image: +14s
  - search: +14s
  - database: +16s
────────────────────
Total: 163s
```

### Résultat Attendu
```javascript
{
  "backend_code": "
    const express = require('express');
    const jwt = require('jsonwebtoken');
    const multer = require('multer');
    const rateLimit = require('express-rate-limit');
    const Joi = require('joi');
    
    const app = express();
    
    // Middleware
    app.use(express.json());
    app.use(cors());
    app.use(helmet());
    
    // Rate limiting
    const limiter = rateLimit({
      windowMs: 15 * 60 * 1000,
      max: 100
    });
    app.use('/api/', limiter);
    
    // Routes
    app.get('/api/articles', async (req, res) => { ... });
    app.post('/api/articles', authMiddleware, async (req, res) => { ... });
    
    // ... (2000+ caractères)
  "
}
```

---

## 3️⃣ Application Vue.js Todo List

### Requête

```python
result = await generate_with_multi_agents(
    description="""
    Todo list Vue.js avec:
    - Ajout/suppression de tâches
    - Marquer comme complété
    - Filtres (toutes, actives, complétées)
    - Compteur de tâches
    - Persistance avec LocalStorage
    - Composition API
    """,
    framework="vue",
    project_type="web_app",
    api_key=EMERGENT_LLM_KEY
)
```

### Timeout Calculé
```
Base: 25s
Description (137 chars): +20s
Type web_app: +35s
Features: 6 (+20s)
Keywords: 0
────────────────────
Total: 100s
```

### Résultat Attendu
```javascript
{
  "js_code": "
    <template>
      <div class='todo-app'>
        <h1>Todo List</h1>
        
        <input 
          v-model='newTodo' 
          @keyup.enter='addTodo'
          placeholder='Nouvelle tâche...'
        />
        
        <div class='filters'>
          <button @click='filter = \"all\"'>Toutes</button>
          <button @click='filter = \"active\"'>Actives</button>
          <button @click='filter = \"completed\"'>Complétées</button>
        </div>
        
        <ul>
          <li v-for='todo in filteredTodos' :key='todo.id'>
            <input type='checkbox' v-model='todo.completed' />
            <span :class='{ completed: todo.completed }'>{{ todo.text }}</span>
            <button @click='removeTodo(todo.id)'>×</button>
          </li>
        </ul>
        
        <p>{{ activeCount }} tâches restantes</p>
      </div>
    </template>
    
    <script>
    import { ref, computed, watch } from 'vue';
    
    export default {
      name: 'TodoApp',
      setup() {
        const todos = ref([]);
        const newTodo = ref('');
        const filter = ref('all');
        
        // Load from localStorage
        const loadTodos = () => {
          const saved = localStorage.getItem('todos');
          if (saved) todos.value = JSON.parse(saved);
        };
        
        // Save to localStorage
        watch(todos, (newTodos) => {
          localStorage.setItem('todos', JSON.stringify(newTodos));
        }, { deep: true });
        
        const addTodo = () => {
          if (newTodo.value.trim()) {
            todos.value.push({
              id: Date.now(),
              text: newTodo.value,
              completed: false
            });
            newTodo.value = '';
          }
        };
        
        const removeTodo = (id) => {
          todos.value = todos.value.filter(t => t.id !== id);
        };
        
        const filteredTodos = computed(() => {
          if (filter.value === 'active') {
            return todos.value.filter(t => !t.completed);
          } else if (filter.value === 'completed') {
            return todos.value.filter(t => t.completed);
          }
          return todos.value;
        });
        
        const activeCount = computed(() => {
          return todos.value.filter(t => !t.completed).length;
        });
        
        loadTodos();
        
        return {
          todos,
          newTodo,
          filter,
          addTodo,
          removeTodo,
          filteredTodos,
          activeCount
        };
      }
    };
    </script>
    
    <style scoped>
    .todo-app { ... }
    .completed { text-decoration: line-through; }
    </style>
  "
}
```

---

## 4️⃣ Application Full-Stack (React + Express)

### Requête Backend

```python
backend_result = await generate_with_multi_agents(
    description="API Express pour gestion utilisateurs avec auth JWT",
    framework="express",
    project_type="api_rest",
    api_key=EMERGENT_LLM_KEY
)
```

### Requête Frontend

```python
frontend_result = await generate_with_multi_agents(
    description="Interface React pour gestion utilisateurs",
    framework="react",
    project_type="web_app",
    api_key=EMERGENT_LLM_KEY
)
```

### Ou Génération Combinée

```python
# Le système multi-agents gère automatiquement frontend + backend
result = await generate_with_multi_agents(
    description="""
    Application full-stack gestion utilisateurs:
    - Frontend React avec formulaires
    - Backend Express avec API REST
    - Authentification JWT
    - Base de données MongoDB
    """,
    framework="react",
    project_type="full_stack",
    api_key=EMERGENT_LLM_KEY
)

# Résultat:
# {
#   "react_code": "...",  # Frontend
#   "backend_code": "...", # Backend
#   "css_code": "...",
#   "html_code": "..."
# }
```

---

## 5️⃣ Microservice Node.js

### Requête

```python
result = await generate_with_multi_agents(
    description="""
    Microservice Node.js pour traitement d'images:
    - Upload d'images
    - Redimensionnement automatique
    - Génération de thumbnails
    - Stockage sur S3
    - Queue Redis pour traitement asynchrone
    - Health checks
    """,
    framework="express",
    project_type="microservice",
    api_key=EMERGENT_LLM_KEY
)
```

### Timeout Calculé
```
Base: 25s
Description (127 chars): +20s
Type microservice: +30s
Features: 6 (+20s)
Keywords:
  - upload: +14s
  - image: +14s
  - redis: +12s
────────────────────
Total: 135s
```

---

## 6️⃣ CLI Tool Node.js

### Requête

```python
result = await generate_with_multi_agents(
    description="""
    CLI tool Node.js pour gestion de fichiers:
    - Commandes: list, copy, move, delete
    - Arguments avec yargs
    - Couleurs avec chalk
    - Barre de progression
    - Configuration avec fichier .rc
    """,
    framework="nodejs",
    project_type="cli_tool",
    api_key=EMERGENT_LLM_KEY
)
```

### Timeout Calculé
```
Base: 25s
Description (121 chars): +20s
Type cli_tool: +10s  # Plus simple
Features: 5 (+15s)
Keywords: 0
────────────────────
Total: 70s
```

---

## 🎯 Fallbacks en Action

### Quand le LLM échoue

```python
# Si génération GPT-4o timeout ou échoue après 2 tentatives
# Le système bascule automatiquement sur le fallback:

# Pour React
{
  "react_code": """
    import React, { useState } from 'react';
    
    function App() {
      const [message, setMessage] = useState('Application React');
      
      return (
        <div className="app">
          <h1>{message}</h1>
          <button onClick={() => setMessage('Fonctionnel!')}>
            Cliquer
          </button>
        </div>
      );
    }
    
    export default App;
  """,  # 428 caractères
  
  "css_code": "...",  # 385 caractères
  "html_code": "..."  # 200 caractères
}

# ✅ Code minimal mais FONCTIONNEL
# ✅ Syntaxe correcte
# ✅ Hooks modernes (useState)
```

---

## 📊 Comparaison Timeouts

| Projet | Description | Type | Features | Keywords | Timeout |
|--------|-------------|------|----------|----------|---------|
| **Counter** | "Simple counter" | web_app | 0 | 0 | 63s |
| **Todo List** | "Todo with filters" | web_app | 2 | 0 | 70s |
| **Blog** | "Blog avec auth" | web_app | 3 | auth, db | 90s |
| **E-commerce** | "Shop complet" | web_app | 6 | auth, payment, stripe, db | 108s |
| **API REST** | "API avec auth JWT" | api_rest | 4 | auth, jwt, db | 95s |
| **Microservice** | "Service images" | microservice | 5 | upload, image, redis | 135s |
| **Full-Stack** | "Chat real-time" | full_stack | 8 | auth, realtime, websocket, chat, db | 180s (max) |

---

## 🔄 Workflow Complet

### 1. Développement Local

```python
# test_local.py
import asyncio
from ai_generators.multi_agent_orchestrator import generate_with_multi_agents

async def main():
    result = await generate_with_multi_agents(
        description="Todo list React",
        framework="react",
        project_type="web_app",
        api_key="sk-emergent-xxxxx"
    )
    
    # Sauvegarder les fichiers
    with open("App.jsx", "w") as f:
        f.write(result["react_code"])
    
    with open("styles.css", "w") as f:
        f.write(result["css_code"])
    
    with open("index.html", "w") as f:
        f.write(result["html_code"])
    
    print("✅ Fichiers générés!")

asyncio.run(main())
```

### 2. Intégration API

```python
# server.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class GenerateRequest(BaseModel):
    description: str
    framework: str
    project_type: str

@app.post("/api/generate")
async def generate(request: GenerateRequest):
    result = await generate_with_multi_agents(
        description=request.description,
        framework=request.framework,
        project_type=request.project_type,
        api_key=EMERGENT_LLM_KEY
    )
    
    return {
        "success": True,
        "files": result,
        "count": len(result)
    }
```

### 3. Frontend Client

```javascript
// client.js
async function generateCode() {
  const response = await fetch('/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      description: "Todo list React",
      framework: "react",
      project_type: "web_app"
    })
  });
  
  const data = await response.json();
  console.log(`✅ ${data.count} fichiers générés`);
  console.log(data.files);
}
```

---

## 🚀 Best Practices

### 1. Descriptions Claires

✅ **BON:**
```python
description = """
Application e-commerce React avec:
- Catalogue produits avec filtres
- Panier d'achat
- Authentification JWT
- Paiement Stripe
"""
```

❌ **MAUVAIS:**
```python
description = "Une app e-commerce"  # Trop vague
```

### 2. Features Explicites

✅ **BON:**
```python
features = ["authentication", "payment", "database", "real-time"]
```

❌ **MAUVAIS:**
```python
features = []  # Pas d'infos sur la complexité
```

### 3. Framework Correct

✅ **BON:**
```python
framework = "react"  # Détection JavaScript ✓
```

❌ **MAUVAIS:**
```python
framework = "reactjs"  # Pas détecté
```

---

**Fichiers de référence:**
- Architecture: `/app/ARCHITECTURE_JAVASCRIPT_OPTIMIZER.md`
- Guide: `/app/GUIDE_UTILISATION_JS_OPTIMIZER.md`
- Résumé: `/app/RESUME_FONCTIONS_JS_OPTIMIZER.md`

**Version:** 1.0.0  
**Statut:** Production Ready ✅
