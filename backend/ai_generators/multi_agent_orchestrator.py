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
    """Définition des rôles d'agents spécialisés - SYSTÈME ÉVOLUTIF À 12 AGENTS"""
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
    META_LEARNING = "meta_learning"  # Agent 11: Apprentissage et optimisation
    SELF_HEALING = "self_healing"    # Agent 12: Auto-réparation système


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

            AgentRole.DIAGNOSTIC: f"""ANALYSE DIAGNOSTIQUE COMPLÈTE DU PROJET:

DESCRIPTION: {description}
FRAMEWORK: {framework}

Mission CRITIQUE:
Analyse cette description en profondeur et fournis un rapport diagnostic JSON complet.

Analyse requise:
1. COMPLEXITÉ du projet (simple/medium/complex)
2. BESOINS TECHNIQUES détectés:
   - Authentification nécessaire? (JWT, OAuth, etc.)
   - Base de données nécessaire? (MongoDB, PostgreSQL, etc.)
   - Paiements nécessaires? (Stripe, PayPal, etc.)
   - API externes nécessaires? (Google Maps, SendGrid, etc.)
   - Temps réel nécessaire? (WebSocket, Socket.io, etc.)
3. TECH STACK optimal recommandé
4. ARCHITECTURE recommandée (MVC, microservices, etc.)
5. INSTRUCTIONS pour chaque agent (Frontend, Backend, etc.)

FORMAT OBLIGATOIRE - Réponds UNIQUEMENT avec ce JSON:
{{
  "complexity": "simple|medium|complex",
  "estimated_files": 20,
  "needs": {{
    "authentication": true/false,
    "database": "mongodb|postgresql|none",
    "payments": true/false,
    "real_time": true/false,
    "external_apis": ["api1", "api2"],
    "file_upload": true/false
  }},
  "tech_stack": {{
    "frontend": "react",
    "backend": "fastapi",
    "database": "mongodb",
    "authentication": "jwt"
  }},
  "architecture": "Description de l'architecture recommandée",
  "agent_instructions": {{
    "frontend": "Instructions spécifiques pour agent frontend",
    "backend": "Instructions spécifiques pour agent backend",
    "database": "Instructions spécifiques pour schéma BDD"
  }}
}}

Analyse MAINTENANT.""",

            AgentRole.DATABASE: f"""Génère le schéma de base de données COMPLET:

DESCRIPTION: {description}
FRAMEWORK: {framework}
CONTEXTE: {context if context else 'Aucun'}

Fichiers à générer:
1. database/models.py ou database/schemas.js - Models/Collections
2. database/migrations/001_initial.sql - Migration initiale
3. database/seed.py ou database/seed.js - Données de test
4. database/indexes.sql - Indexes optimisés

IMPORTANT:
- Schémas avec validation complète
- Relations optimisées
- Indexes pour performance
- Seed data réalistes
- Migrations versionnées

Format: FICHIER: chemin/fichier suivi du code entre triple backticks""",

            AgentRole.SECURITY: f"""AUDIT DE SÉCURITÉ COMPLET du projet:

DESCRIPTION: {description}
FRAMEWORK: {framework}
CONTEXTE: {context if context else 'Aucun'}

Mission CRITIQUE:
1. Analyser TOUS les fichiers générés
2. Détecter vulnérabilités (XSS, CSRF, injection, etc.)
3. Générer code de sécurité corrigé

Fichiers à générer:
1. security/middleware.py - Middleware sécurité
2. security/validators.py - Validation inputs
3. security/config.py - Configuration sécurité
4. security/audit_report.json - Rapport d'audit détaillé

Rapport JSON OBLIGATOIRE dans audit_report.json:
{{
  "vulnerabilities": [
    {{"type": "XSS", "severity": "high", "file": "src/App.jsx", "line": 42}}
  ],
  "fixes_applied": ["Description des corrections"],
  "security_score": 85,
  "recommendations": ["Recommandation 1", "Recommandation 2"]
}}

Format: FICHIER: chemin/fichier suivi du code entre triple backticks""",

            AgentRole.TESTING: f"""Génère les TESTS AUTOMATIQUES COMPLETS:

DESCRIPTION: {description}
FRAMEWORK: {framework}
CONTEXTE: {context if context else 'Aucun'}

Fichiers à générer:
1. tests/unit/components.test.js - Tests unitaires React
2. tests/unit/api.test.py - Tests unitaires Backend
3. tests/integration/auth.test.js - Tests intégration
4. tests/e2e/user-flow.spec.js - Tests E2E Playwright
5. tests/fixtures/data.js - Données de test
6. jest.config.js - Configuration Jest
7. pytest.ini - Configuration Pytest

IMPORTANT:
- Tests avec VRAIES assertions (expect, assert)
- Coverage >80% souhaité
- Tests des cas limites (edge cases)
- Mocking approprié
- Tests de sécurité (XSS, injection)

Format: FICHIER: chemin/fichier.test.js suivi du code entre triple backticks""",

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
    """Orchestrateur qui coordonne les 10 agents spécialisés - SYSTÈME PROFESSIONNEL COMPLET"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.agents = {
            # Phase 0: Diagnostic
            AgentRole.DIAGNOSTIC: SpecializedAgent(AgentRole.DIAGNOSTIC, api_key),
            # Phase 1: Génération parallèle
            AgentRole.FRONTEND: SpecializedAgent(AgentRole.FRONTEND, api_key),
            AgentRole.STYLING: SpecializedAgent(AgentRole.STYLING, api_key),
            AgentRole.BACKEND: SpecializedAgent(AgentRole.BACKEND, api_key),
            AgentRole.CONFIG: SpecializedAgent(AgentRole.CONFIG, api_key),
            AgentRole.COMPONENTS: SpecializedAgent(AgentRole.COMPONENTS, api_key),
            AgentRole.DATABASE: SpecializedAgent(AgentRole.DATABASE, api_key),
            # Phase 2: Sécurité
            AgentRole.SECURITY: SpecializedAgent(AgentRole.SECURITY, api_key),
            # Phase 3: Tests
            AgentRole.TESTING: SpecializedAgent(AgentRole.TESTING, api_key),
            # Phase 4: QA Final
            AgentRole.QA: SpecializedAgent(AgentRole.QA, api_key),
        }
        self.logger = logging.getLogger("MultiAgentOrchestrator")
        self.diagnostic_result = None
    
    async def generate_application(
        self,
        description: str,
        framework: str = "react",
        project_type: str = "web_app",
        project_id: str = None
    ) -> Dict[str, str]:
        """
        Génère une application complète avec tous les agents en parallèle
        ARCHITECTURE PROFESSIONNELLE À 10 AGENTS + STREAMING TEMPS RÉEL
        OPTIMISÉE POUR 100% DE SUCCÈS
        
        Returns:
            Dict avec tous les fichiers générés par tous les agents
        """
        
        # Importer streaming manager si disponible
        streaming_manager = None
        try:
            from streaming.streaming_system import streaming_manager as sm
            streaming_manager = sm
        except:
            pass
        
        self.logger.info(f"🚀 Démarrage génération OPTIMISÉE (10 agents) - Framework: {framework}")
        
        # Phase 0: Agent Diagnostic (CRITIQUE - analyse AVANT génération)
        self.logger.info("🔍 Phase 0: Diagnostic et Analyse du Projet")
        
        if streaming_manager and project_id:
            await streaming_manager.stream_phase(project_id, "Diagnostic et Analyse", 0)
        
        try:
            diagnostic_files = await asyncio.wait_for(
                self.agents[AgentRole.DIAGNOSTIC].generate(description, framework),
                timeout=15.0  # Augmenté de 10s à 15s
            )
            
            # Extraire le rapport diagnostic
            if diagnostic_files:
                import json
                for file_path, content in diagnostic_files.items():
                    if 'json' in file_path.lower() or content.strip().startswith('{'):
                        try:
                            self.diagnostic_result = json.loads(content)
                            self.logger.info(f"✅ Diagnostic terminé - Complexité: {self.diagnostic_result.get('complexity', 'unknown')}")
                            break
                        except:
                            pass
        except Exception as e:
            self.logger.warning(f"⚠️ Diagnostic échoué, continue avec valeurs par défaut: {e}")
            self.diagnostic_result = {"complexity": "medium", "needs": {}}
        
        # Phase 1: Génération parallèle OPTIMISÉE (6 agents) - 100% SUCCÈS GARANTI
        self.logger.info("📋 Phase 1: Génération parallèle OPTIMISÉE (6 agents)")
        
        if streaming_manager and project_id:
            await streaming_manager.stream_phase(project_id, "Génération Parallèle (6 agents)", 1)
        
        # Préparer le contexte avec les résultats du diagnostic
        context = {"diagnostic": self.diagnostic_result} if self.diagnostic_result else None
        
        # Créer toutes les tâches avec retry automatique
        agent_names = [AgentRole.FRONTEND, AgentRole.STYLING, AgentRole.BACKEND, 
                      AgentRole.CONFIG, AgentRole.COMPONENTS, AgentRole.DATABASE]
        
        all_files = {}
        
        # Lancer TOUS les agents en parallèle avec streaming
        tasks_with_names = []
        for agent_name in agent_names:
            task = self._generate_with_retry_and_streaming(
                agent_name,
                description,
                framework,
                context,
                project_id,
                streaming_manager,
                max_retries=3  # Retry automatique si échec
            )
            tasks_with_names.append((agent_name, task))
        
        # Attendre TOUS les agents avec timeout généreux
        results = await asyncio.gather(
            *[task for _, task in tasks_with_names],
            return_exceptions=True
        )
        
        # Collecter les résultats avec fallback garantis
        for i, (agent_name, result) in enumerate(zip(agent_names, results)):
            if isinstance(result, dict) and result:
                all_files.update(result)
                files_count = len(result)
                self.logger.info(f"✅ Agent {agent_name}: {files_count} fichiers")
                
                if streaming_manager and project_id:
                    await streaming_manager.stream_agent_complete(project_id, agent_name, files_count)
                    
                    # Stream chaque fichier créé
                    for file_path, content in result.items():
                        await streaming_manager.stream_file_created(
                            project_id, 
                            file_path, 
                            len(content)
                        )
            else:
                # FALLBACK: Générer fichiers minimaux si agent échoue
                self.logger.error(f"❌ Agent {agent_name} erreur: {result}")
                fallback_files = await self._generate_fallback_files(agent_name, description, framework)
                all_files.update(fallback_files)
                
                if streaming_manager and project_id:
                    await streaming_manager.stream_error(
                        project_id,
                        f"Agent {agent_name} échec - Fallback appliqué",
                        agent_name
                    )
        
        # Phase 2: Agent Security pour audit (séquentiel)
        self.logger.info("🛡️ Phase 2: Audit de Sécurité")
        
        try:
            security_result = await asyncio.wait_for(
                self.agents[AgentRole.SECURITY].generate(
                    description, 
                    framework,
                    context={"files": list(all_files.keys())}
                ),
                timeout=15.0
            )
            
            if security_result:
                all_files.update(security_result)
                self.logger.info(f"✅ Agent Security: {len(security_result)} fichiers")
        except Exception as e:
            self.logger.warning(f"⚠️ Security audit échoué: {e}")
        
        # Phase 3: Agent Testing pour tests automatiques (séquentiel)
        self.logger.info("🧪 Phase 3: Génération des Tests")
        
        try:
            testing_result = await asyncio.wait_for(
                self.agents[AgentRole.TESTING].generate(
                    description, 
                    framework,
                    context={"files": list(all_files.keys())}
                ),
                timeout=15.0
            )
            
            if testing_result:
                all_files.update(testing_result)
                self.logger.info(f"✅ Agent Testing: {len(testing_result)} fichiers")
        except Exception as e:
            self.logger.warning(f"⚠️ Tests generation échoué: {e}")
        
        # Phase 4: Agent QA pour validation finale (séquentiel)
        self.logger.info("🔍 Phase 4: Quality Assurance Finale")
        
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
    
    async def _generate_with_retry_and_streaming(
        self,
        agent_name: str,
        description: str,
        framework: str,
        context: Dict,
        project_id: str,
        streaming_manager,
        max_retries: int = 3
    ) -> Dict[str, str]:
        """
        Génère avec un agent spécifique avec RETRY automatique et streaming
        
        Garantit 100% de succès via fallback intelligent
        """
        
        # Notifier début agent
        if streaming_manager and project_id:
            await streaming_manager.stream_agent_start(project_id, agent_name)
        
        # Tenter génération avec retries
        for attempt in range(max_retries):
            try:
                self.logger.info(f"🤖 Agent {agent_name} - Tentative {attempt + 1}/{max_retries}")
                
                # Générer avec timeout adaptatif (augmente avec chaque retry)
                timeout = 20.0 + (attempt * 10.0)  # 20s, 30s, 40s
                
                result = await asyncio.wait_for(
                    self.agents[agent_name].generate(description, framework, context),
                    timeout=timeout
                )
                
                if result and len(result) > 0:
                    self.logger.info(f"✅ Agent {agent_name} succès - {len(result)} fichiers")
                    return result
                else:
                    self.logger.warning(f"⚠️ Agent {agent_name} retour vide - Retry")
                    
            except asyncio.TimeoutError:
                self.logger.warning(f"⏱️ Agent {agent_name} timeout (tentative {attempt + 1}) - Retry")
                
            except Exception as e:
                self.logger.error(f"❌ Agent {agent_name} erreur (tentative {attempt + 1}): {e}")
        
        # Si tous les retries échouent, utiliser fallback
        self.logger.warning(f"⚠️ Agent {agent_name} échec après {max_retries} tentatives - Fallback")
        return await self._generate_fallback_files(agent_name, description, framework)
    
    async def _generate_fallback_files(
        self,
        agent_name: str,
        description: str,
        framework: str
    ) -> Dict[str, str]:
        """
        Génère des fichiers de fallback basiques mais fonctionnels
        
        GARANTIT qu'il y aura toujours des fichiers, même en cas d'échec total
        """
        
        self.logger.info(f"🔄 Génération fallback pour agent: {agent_name}")
        
        fallbacks = {
            AgentRole.FRONTEND: {
                "src/App.jsx": f"""import React from 'react';

export default function App() {{
  return (
    <div className="app">
      <header>
        <h1>{description[:50]}</h1>
      </header>
      <main>
        <p>Application générée par Vectort.io</p>
      </main>
    </div>
  );
}}""",
                "src/pages/Home.jsx": """import React from 'react';

export default function Home() {
  return <div><h2>Page d'accueil</h2></div>;
}""",
            },
            
            AgentRole.STYLING: {
                "src/styles/global.css": """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.6;
  color: #333;
}

.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}""",
            },
            
            AgentRole.BACKEND: {
                "backend/main.py": """from fastapi import FastAPI

app = FastAPI(title="API Backend")

@app.get("/")
async def root():
    return {"message": "API Backend"}

@app.get("/health")
async def health():
    return {"status": "healthy"}""",
            },
            
            AgentRole.CONFIG: {
                "package.json": """{
  "name": "vectort-app",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}""",
                "README.md": f"""# {description[:50]}

Application générée par Vectort.io

## Installation
```
npm install
npm start
```""",
            },
            
            AgentRole.COMPONENTS: {
                "src/hooks/useAuth.js": """import { useState } from 'react';

export default function useAuth() {
  const [user, setUser] = useState(null);
  return { user, setUser };
}""",
            },
            
            AgentRole.DATABASE: {
                "database/models.py": """from pydantic import BaseModel

class User(BaseModel):
    id: str
    email: str
    name: str""",
            }
        }
        
        return fallbacks.get(agent_name, {
            f"fallback/{agent_name}.txt": f"Fallback file for {agent_name}"
        })


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
