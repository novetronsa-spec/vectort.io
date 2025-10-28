"""
Multi-Agent Orchestrator for Vectort.io
Architecture avec 6 agents spécialisés travaillant en parallèle
Performance et qualité professionnelle maximales
"""

import asyncio
from typing import Dict, List, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
import logging

logger = logging.getLogger(__name__)


class AgentRole:
    """Définition des rôles d'agents spécialisés - SYSTÈME À 10 AGENTS"""
    DIAGNOSTIC = "diagnostic"     # Phase 0: Analyse avant génération
    FRONTEND = "frontend"
    STYLING = "styling"
    BACKEND = "backend"
    CONFIG = "config"
    COMPONENTS = "components"
    DATABASE = "database"         # Nouveau: Schémas BDD
    SECURITY = "security"         # Nouveau: Audit sécurité
    TESTING = "testing"           # Nouveau: Tests automatiques
    QA = "qa"


class SpecializedAgent:
    """Agent spécialisé pour une tâche spécifique"""
    
    def __init__(self, role: str, api_key: str):
        self.role = role
        self.api_key = api_key
        self.logger = logging.getLogger(f"Agent-{role}")
    
    def _get_system_message(self) -> str:
        """Message système spécialisé selon le rôle"""
        
        messages = {
            AgentRole.FRONTEND: """Tu es un EXPERT FRONTEND React/Next.js senior.
Tu génères des composants React COMPLETS et PROFESSIONNELS.

Spécialités:
- Composants React modernes avec hooks (useState, useEffect, useContext)
- Architecture propre et maintenable
- Props TypeScript si applicable
- Performance optimisée (useMemo, useCallback)
- Accessibilité (ARIA, semantic HTML)
- Gestion d'état professionnelle

Code COMPLET - JAMAIS de TODO ou placeholders.""",

            AgentRole.STYLING: """Tu es un EXPERT CSS/Design senior.
Tu crées des styles COMPLETS et PROFESSIONNELS.

Spécialités:
- CSS moderne (Flexbox, Grid, Variables CSS)
- Design responsive (mobile-first)
- Animations fluides et professionnelles
- Thèmes et palettes de couleurs cohérentes
- Performance CSS optimisée
- Support dark mode si applicable

Styles COMPLETS - JAMAIS de "/* TODO */".""",

            AgentRole.BACKEND: """Tu es un EXPERT BACKEND Python/FastAPI senior.
Tu génères des APIs REST COMPLÈTES et PROFESSIONNELLES.

Spécialités:
- Endpoints FastAPI avec validation Pydantic
- Architecture RESTful propre
- Authentification JWT
- Gestion d'erreurs robuste
- Base de données (MongoDB/PostgreSQL)
- Middleware et sécurité

Code COMPLET - JAMAIS de "# TODO".""",

            AgentRole.CONFIG: """Tu es un EXPERT DevOps/Configuration senior.
Tu crées des fichiers de config COMPLETS et PROFESSIONNELS.

Spécialités:
- package.json avec dépendances appropriées
- tsconfig.json pour TypeScript
- .env.example avec toutes les variables
- README.md détaillé et professionnel
- Dockerfile optimisé
- .gitignore approprié

Config COMPLÈTE - Documentation claire.""",

            AgentRole.COMPONENTS: """Tu es un EXPERT Component Library senior.
Tu crées des composants réutilisables COMPLETS et PROFESSIONNELS.

Spécialités:
- Hooks personnalisés (useAuth, useApi, useForm)
- Utilities et helpers
- Composants UI réutilisables (Button, Input, Modal)
- Services et API clients
- Types TypeScript
- Constantes et configurations

Code COMPLET et RÉUTILISABLE.""",

            AgentRole.DIAGNOSTIC: """Tu es un EXPERT ARCHITECTE SYSTÈME senior.
Tu analyses les projets AVANT génération pour créer le plan optimal.

Responsabilités CRITIQUES:
- Analyser la description du projet en profondeur
- Identifier TOUS les besoins techniques (auth, BDD, paiement, API externes)
- Détecter la complexité (simple, moyenne, complexe)
- Recommander l'architecture optimale
- Lister les technologies nécessaires
- Créer un plan d'action détaillé pour les autres agents

Fournis un rapport JSON structuré avec:
- "complexity": "simple|medium|complex"
- "needs": ["authentication", "database", "payment", etc.]
- "tech_stack": {"frontend": "react", "backend": "fastapi", etc.}
- "architecture": Description de l'architecture recommandée
- "agent_instructions": Instructions spécifiques pour chaque agent

Analyse COMPLÈTE et PROFESSIONNELLE.""",

            AgentRole.DATABASE: """Tu es un EXPERT DATABASE ARCHITECT senior.
Tu conçois des schémas de base de données OPTIMAUX et PROFESSIONNELS.

Spécialités:
- Schémas de base de données (MongoDB, PostgreSQL)
- Models/Collections optimisés
- Relations et indexes performants
- Migrations de base de données
- Requêtes optimisées
- Data validation
- Seed data pour développement

Code COMPLET avec schémas, migrations et seed data.""",

            AgentRole.SECURITY: """Tu es un EXPERT SECURITY ENGINEER senior.
Tu audites le code et appliques les best practices de SÉCURITÉ.

Responsabilités CRITIQUES:
- Détecter vulnérabilités (XSS, CSRF, injection SQL, etc.)
- Valider tous les inputs utilisateur
- Implémenter authentification sécurisée
- Configurer headers de sécurité HTTP
- Protéger les données sensibles
- Rate limiting et protection DDoS
- CORS configuration sécurisée

Fournis:
1. Rapport d'audit JSON avec vulnérabilités détectées
2. Code de sécurité corrigé (middleware, validators, etc.)
3. Score de sécurité /100

Audit COMPLET et PROFESSIONNEL.""",

            AgentRole.TESTING: """Tu es un EXPERT QA ENGINEER senior spécialisé en tests automatiques.
Tu génères des tests COMPLETS et PROFESSIONNELS.

Spécialités:
- Tests unitaires (Jest pour React, Pytest pour Python)
- Tests d'intégration
- Tests E2E (Playwright, Cypress)
- Test coverage >80%
- Mocking et fixtures
- Tests de performance
- Tests de sécurité

Fichiers à générer:
- tests/unit/*.test.js - Tests unitaires
- tests/integration/*.test.js - Tests intégration
- tests/e2e/*.spec.js - Tests E2E
- tests/fixtures/*.js - Données de test

Tests COMPLETS avec bonne couverture.""",

            AgentRole.QA: """Tu es un EXPERT Quality Assurance senior.
Tu valides et optimises le code généré.

Responsabilités:
- Vérifier la cohérence entre fichiers
- Détecter les imports manquants
- Valider la syntaxe et structure
- Suggérer optimisations
- Vérifier la complétude
- Assurer les best practices

Analyse COMPLÈTE et PROFESSIONNELLE."""
        }
        
        return messages.get(self.role, "Tu es un développeur expert senior.")
    
    async def generate(self, description: str, framework: str, context: Dict = None) -> Dict[str, str]:
        """Génère les fichiers assignés à cet agent"""
        
        self.logger.info(f"Agent {self.role} démarré - Framework: {framework}")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"agent-{self.role}-{hash(description)}",
            system_message=self._get_system_message()
        )
        
        prompt = self._build_prompt(description, framework, context)
        
        try:
            response = await chat.with_model("openai", "gpt-4o").send_message(
                UserMessage(text=prompt)
            )
            
            # Parser la réponse
            files = self._parse_response(response)
            
            self.logger.info(f"Agent {self.role} terminé - {len(files)} fichiers générés")
            return files
            
        except Exception as e:
            self.logger.error(f"Agent {self.role} erreur: {e}")
            return {}
    
    def _build_prompt(self, description: str, framework: str, context: Dict = None) -> str:
        """Construit le prompt spécialisé selon le rôle"""
        
        prompts = {
            AgentRole.FRONTEND: f"""Génère les composants React COMPLETS pour cette application:

DESCRIPTION: {description}
FRAMEWORK: {framework}

Fichiers à générer:
1. src/App.jsx - Composant principal avec routing
2. src/pages/Home.jsx - Page d'accueil
3. src/pages/Dashboard.jsx - Dashboard utilisateur
4. src/components/Navbar.jsx - Navigation
5. src/components/Footer.jsx - Footer

IMPORTANT:
- Code React COMPLET avec hooks
- Props et state management
- AUCUN import statement (seront ajoutés automatiquement)
- Composants fonctionnels modernes
- Gestion d'erreurs

Format: FICHIER: chemin/fichier.jsx suivi du code entre triple backticks""",

            AgentRole.STYLING: f"""Génère les styles CSS COMPLETS pour cette application:

DESCRIPTION: {description}
FRAMEWORK: {framework}

Fichiers à générer:
1. src/styles/global.css - Styles globaux
2. src/styles/components.css - Styles des composants
3. src/styles/responsive.css - Media queries

IMPORTANT:
- CSS moderne (Variables, Flexbox, Grid)
- Design responsive (mobile, tablet, desktop)
- Animations fluides
- Palette de couleurs cohérente
- Performance optimisée

Format: FICHIER: chemin/fichier.css suivi du code entre triple backticks""",

            AgentRole.BACKEND: f"""Génère l'API Backend COMPLÈTE pour cette application:

DESCRIPTION: {description}
FRAMEWORK: {framework}

Fichiers à générer:
1. backend/main.py - Application FastAPI principale
2. backend/models.py - Modèles Pydantic
3. backend/routes.py - Endpoints API
4. backend/auth.py - Authentification JWT

IMPORTANT:
- FastAPI avec validation Pydantic
- Endpoints RESTful complets
- Authentification JWT
- Gestion d'erreurs robuste
- Code production-ready

Format: FICHIER: chemin/fichier.py suivi du code entre triple backticks""",

            AgentRole.CONFIG: f"""Génère les fichiers de configuration COMPLETS:

DESCRIPTION: {description}
FRAMEWORK: {framework}

Fichiers à générer:
1. package.json - Dépendances complètes
2. README.md - Documentation détaillée
3. .env.example - Variables d'environnement
4. .gitignore - Fichiers à ignorer

IMPORTANT:
- Dépendances appropriées et à jour
- Documentation professionnelle
- Configuration complète
- Best practices DevOps

Format: FICHIER: chemin/fichier suivi du code entre triple backticks""",

            AgentRole.COMPONENTS: f"""Génère la bibliothèque de composants COMPLÈTE:

DESCRIPTION: {description}
FRAMEWORK: {framework}

Fichiers à générer:
1. src/hooks/useAuth.js - Hook authentification
2. src/hooks/useApi.js - Hook API calls
3. src/utils/helpers.js - Fonctions utilitaires
4. src/services/api.js - Client API

IMPORTANT:
- Hooks personnalisés réutilisables
- Utilities bien testées
- Services API propres
- Code modulaire

Format: FICHIER: chemin/fichier.js suivi du code entre triple backticks""",

            AgentRole.QA: f"""Analyse et valide le code généré:

DESCRIPTION: {description}
FRAMEWORK: {framework}
CONTEXTE: {context}

Tâches:
1. Vérifier cohérence entre fichiers
2. Détecter imports manquants
3. Valider syntaxe
4. Suggérer optimisations
5. Vérifier complétude

Fournis un rapport JSON avec:
- "issues": liste des problèmes détectés
- "suggestions": améliorations recommandées
- "score": note sur 100

Format: JSON uniquement"""
        }
        
        return prompts.get(self.role, f"Génère du code pour: {description}")
    
    def _parse_response(self, response: str) -> Dict[str, str]:
        """Parse la réponse de l'agent pour extraire les fichiers"""
        import re
        
        files = {}
        
        # Pattern: FICHIER: path suivi de ```code```
        pattern = r'FICHIER:\s*([^\n]+)\s*```(?:\w+)?\n(.*?)```'
        matches = re.finditer(pattern, response, re.DOTALL)
        
        for match in matches:
            file_path = match.group(1).strip()
            content = match.group(2).strip()
            files[file_path] = content
        
        # Si aucun fichier trouvé avec le pattern, essayer JSON pour QA
        if not files and self.role == AgentRole.QA:
            try:
                import json
                # Essayer de parser comme JSON
                if response.strip().startswith('{'):
                    files['qa_report.json'] = response
            except:
                pass
        
        return files


class MultiAgentOrchestrator:
    """Orchestrateur qui coordonne les 6 agents spécialisés"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.agents = {
            AgentRole.FRONTEND: SpecializedAgent(AgentRole.FRONTEND, api_key),
            AgentRole.STYLING: SpecializedAgent(AgentRole.STYLING, api_key),
            AgentRole.BACKEND: SpecializedAgent(AgentRole.BACKEND, api_key),
            AgentRole.CONFIG: SpecializedAgent(AgentRole.CONFIG, api_key),
            AgentRole.COMPONENTS: SpecializedAgent(AgentRole.COMPONENTS, api_key),
            AgentRole.QA: SpecializedAgent(AgentRole.QA, api_key),
        }
        self.logger = logging.getLogger("MultiAgentOrchestrator")
    
    async def generate_application(
        self,
        description: str,
        framework: str = "react",
        project_type: str = "web_app"
    ) -> Dict[str, str]:
        """
        Génère une application complète avec tous les agents en parallèle
        
        Returns:
            Dict avec tous les fichiers générés par tous les agents
        """
        
        self.logger.info(f"🚀 Démarrage génération multi-agents - Framework: {framework}")
        
        # Phase 1: Génération parallèle des agents principaux (5 agents)
        self.logger.info("📋 Phase 1: Génération parallèle (5 agents)")
        
        tasks = [
            self.agents[AgentRole.FRONTEND].generate(description, framework),
            self.agents[AgentRole.STYLING].generate(description, framework),
            self.agents[AgentRole.BACKEND].generate(description, framework),
            self.agents[AgentRole.CONFIG].generate(description, framework),
            self.agents[AgentRole.COMPONENTS].generate(description, framework),
        ]
        
        try:
            # Exécuter tous les agents en parallèle avec timeout de 40s
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=40.0
            )
            
            # Fusionner tous les fichiers
            all_files = {}
            for i, result in enumerate(results):
                if isinstance(result, dict):
                    all_files.update(result)
                    agent_name = list(self.agents.keys())[i]
                    self.logger.info(f"✅ Agent {agent_name}: {len(result)} fichiers")
                else:
                    agent_name = list(self.agents.keys())[i]
                    self.logger.error(f"❌ Agent {agent_name} erreur: {result}")
            
            # Phase 2: Agent QA pour validation (séquentiel)
            self.logger.info("🔍 Phase 2: Quality Assurance")
            
            qa_result = await self.agents[AgentRole.QA].generate(
                description, 
                framework,
                context={"files": list(all_files.keys())}
            )
            
            if qa_result:
                all_files.update(qa_result)
                self.logger.info("✅ Agent QA: Validation terminée")
            
            self.logger.info(f"🎉 Génération terminée - Total: {len(all_files)} fichiers")
            
            return all_files
            
        except asyncio.TimeoutError:
            self.logger.error("⚠️ Timeout de génération - retour des fichiers partiels")
            return all_files if 'all_files' in locals() else {}
        
        except Exception as e:
            self.logger.error(f"❌ Erreur orchestration: {e}")
            return {}
    
    async def generate_with_fallback(
        self,
        description: str,
        framework: str = "react",
        project_type: str = "web_app"
    ) -> Dict[str, str]:
        """
        Génération avec fallback automatique si échec
        """
        
        try:
            # Essayer génération multi-agents
            files = await self.generate_application(description, framework, project_type)
            
            # Si pas assez de fichiers, utiliser fallback
            if len(files) < 5:
                self.logger.warning("⚠️ Pas assez de fichiers générés - fallback activé")
                return await self._generate_basic_fallback(description, framework)
            
            return files
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération multi-agents: {e}")
            return await self._generate_basic_fallback(description, framework)
    
    async def _generate_basic_fallback(self, description: str, framework: str) -> Dict[str, str]:
        """Fallback: génération basique si multi-agents échoue"""
        
        self.logger.info("🔄 Fallback: génération basique")
        
        # Utiliser au moins l'agent Frontend qui est le plus important
        try:
            frontend_files = await self.agents[AgentRole.FRONTEND].generate(description, framework)
            styling_files = await self.agents[AgentRole.STYLING].generate(description, framework)
            
            return {**frontend_files, **styling_files}
        except:
            # Dernière ligne de défense: fichiers minimaux
            return {
                "src/App.jsx": "export default function App() { return <div>Application générée</div>; }",
                "src/styles/global.css": "body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }"
            }


# Export principal
async def generate_with_multi_agents(
    description: str,
    framework: str = "react",
    project_type: str = "web_app",
    api_key: str = None
) -> Dict[str, str]:
    """
    Fonction principale pour générer avec le système multi-agents
    
    Args:
        description: Description du projet
        framework: Framework à utiliser
        project_type: Type de projet
        api_key: Clé API Emergent LLM
    
    Returns:
        Dict de fichiers générés
    """
    
    orchestrator = MultiAgentOrchestrator(api_key)
    return await orchestrator.generate_with_fallback(description, framework, project_type)
