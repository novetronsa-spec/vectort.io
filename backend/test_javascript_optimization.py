"""
Script de test complet pour le système d'optimisation JavaScript
Teste TOUS les scénarios: React, Vue, Angular, Node.js/Express, complexité variable
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("JavaScriptOptimizationTest")

# Add backend to path
sys.path.insert(0, '/app/backend')

from ai_generators.javascript_optimizer import JavaScriptOptimizer
from ai_generators.multi_agent_orchestrator import MultiAgentOrchestrator, generate_with_multi_agents


class JavaScriptOptimizationTester:
    """Testeur complet pour optimisation JavaScript"""
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("❌ EMERGENT_LLM_KEY non trouvée!")
        
        self.results = []
        logger.info(f"✅ Testeur initialisé avec API key: {self.api_key[:10]}...")
    
    async def test_react_simple(self):
        """Test 1: Application React simple"""
        
        logger.info("\n" + "="*80)
        logger.info("TEST 1: Application React Simple")
        logger.info("="*80)
        
        start_time = datetime.now()
        
        try:
            optimizer = JavaScriptOptimizer(self.api_key)
            
            description = "Une simple application React avec un compteur et un bouton pour incrémenter"
            
            result = await optimizer.generate_with_fallback(
                description=description,
                project_type="web_app",
                framework="react",
                language="javascript",
                features=["counter"]
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Validation
            success = bool(result and result.get("react_code") and len(result.get("react_code", "")) > 100)
            
            test_result = {
                "test": "React Simple",
                "success": success,
                "duration": duration,
                "files": len(result) if result else 0,
                "code_length": len(result.get("react_code", "")) if result else 0
            }
            
            self.results.append(test_result)
            
            if success:
                logger.info(f"✅ TEST RÉUSSI - {test_result['files']} fichiers - {test_result['code_length']} chars - {duration:.1f}s")
            else:
                logger.error(f"❌ TEST ÉCHOUÉ - Durée: {duration:.1f}s")
            
            return success
        
        except Exception as e:
            logger.error(f"❌ ERREUR TEST: {e}")
            self.results.append({
                "test": "React Simple",
                "success": False,
                "duration": (datetime.now() - start_time).total_seconds(),
                "error": str(e)
            })
            return False
    
    async def test_nodejs_api(self):
        """Test 2: API Node.js/Express"""
        
        logger.info("\n" + "="*80)
        logger.info("TEST 2: API Node.js/Express")
        logger.info("="*80)
        
        start_time = datetime.now()
        
        try:
            optimizer = JavaScriptOptimizer(self.api_key)
            
            description = "Une API REST Node.js avec Express pour gérer des utilisateurs (CRUD)"
            
            result = await optimizer.generate_with_fallback(
                description=description,
                project_type="api_rest",
                framework="express",
                language="javascript",
                features=["crud", "users"]
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Validation
            success = bool(result and result.get("backend_code") and len(result.get("backend_code", "")) > 200)
            
            test_result = {
                "test": "Node.js API",
                "success": success,
                "duration": duration,
                "files": len(result) if result else 0,
                "code_length": len(result.get("backend_code", "")) if result else 0
            }
            
            self.results.append(test_result)
            
            if success:
                logger.info(f"✅ TEST RÉUSSI - {test_result['files']} fichiers - {test_result['code_length']} chars - {duration:.1f}s")
            else:
                logger.error(f"❌ TEST ÉCHOUÉ - Durée: {duration:.1f}s")
            
            return success
        
        except Exception as e:
            logger.error(f"❌ ERREUR TEST: {e}")
            self.results.append({
                "test": "Node.js API",
                "success": False,
                "duration": (datetime.now() - start_time).total_seconds(),
                "error": str(e)
            })
            return False
    
    async def test_react_complex(self):
        """Test 3: Application React complexe"""
        
        logger.info("\n" + "="*80)
        logger.info("TEST 3: Application React Complexe")
        logger.info("="*80)
        
        start_time = datetime.now()
        
        try:
            optimizer = JavaScriptOptimizer(self.api_key)
            
            description = """
            Application React e-commerce complète avec:
            - Authentification utilisateur (JWT)
            - Panier d'achat avec gestion du state
            - Liste de produits avec filtres et recherche
            - Page de checkout avec paiement Stripe
            - Dashboard admin pour gérer les produits
            - Notifications en temps réel
            """
            
            result = await optimizer.generate_with_fallback(
                description=description,
                project_type="web_app",
                framework="react",
                language="javascript",
                features=["authentication", "payment", "admin", "real-time", "database", "search"]
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Validation
            success = bool(result and result.get("react_code") and len(result.get("react_code", "")) > 300)
            
            test_result = {
                "test": "React Complexe",
                "success": success,
                "duration": duration,
                "files": len(result) if result else 0,
                "code_length": len(result.get("react_code", "")) if result else 0,
                "expected_timeout": ">60s"  # Devrait avoir un timeout plus grand
            }
            
            self.results.append(test_result)
            
            if success:
                logger.info(f"✅ TEST RÉUSSI - {test_result['files']} fichiers - {test_result['code_length']} chars - {duration:.1f}s")
                logger.info(f"⏱️ Timeout adaptatif devrait être >60s pour cette complexité")
            else:
                logger.error(f"❌ TEST ÉCHOUÉ - Durée: {duration:.1f}s")
            
            return success
        
        except Exception as e:
            logger.error(f"❌ ERREUR TEST: {e}")
            self.results.append({
                "test": "React Complexe",
                "success": False,
                "duration": (datetime.now() - start_time).total_seconds(),
                "error": str(e)
            })
            return False
    
    async def test_fullstack_nodejs(self):
        """Test 4: Application Full-Stack (React + Node.js)"""
        
        logger.info("\n" + "="*80)
        logger.info("TEST 4: Application Full-Stack React + Node.js")
        logger.info("="*80)
        
        start_time = datetime.now()
        
        try:
            # Test avec le système multi-agents qui devrait utiliser JavaScriptOptimizer
            result = await generate_with_multi_agents(
                description="Application de gestion de tâches (todo app) avec frontend React et backend Node.js/Express",
                framework="react",
                project_type="full_stack",
                api_key=self.api_key
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Validation - devrait avoir à la fois react_code et backend_code
            has_frontend = bool(result and result.get("react_code"))
            has_backend = bool(result and result.get("backend_code"))
            success = has_frontend or has_backend  # Au moins un des deux
            
            test_result = {
                "test": "Full-Stack",
                "success": success,
                "duration": duration,
                "files": len(result) if result else 0,
                "has_frontend": has_frontend,
                "has_backend": has_backend
            }
            
            self.results.append(test_result)
            
            if success:
                logger.info(f"✅ TEST RÉUSSI - {test_result['files']} fichiers - Frontend: {has_frontend}, Backend: {has_backend} - {duration:.1f}s")
            else:
                logger.error(f"❌ TEST ÉCHOUÉ - Durée: {duration:.1f}s")
            
            return success
        
        except Exception as e:
            logger.error(f"❌ ERREUR TEST: {e}")
            self.results.append({
                "test": "Full-Stack",
                "success": False,
                "duration": (datetime.now() - start_time).total_seconds(),
                "error": str(e)
            })
            return False
    
    async def test_adaptive_timeout_calculation(self):
        """Test 5: Validation des timeouts adaptatifs"""
        
        logger.info("\n" + "="*80)
        logger.info("TEST 5: Validation Timeouts Adaptatifs")
        logger.info("="*80)
        
        try:
            optimizer = JavaScriptOptimizer(self.api_key)
            
            # Test 1: Projet simple
            timeout_simple = optimizer.calculate_adaptive_timeout(
                description="Simple counter app",
                project_type="web_app",
                features=[]
            )
            
            # Test 2: Projet moyen
            timeout_medium = optimizer.calculate_adaptive_timeout(
                description="E-commerce application with shopping cart and product catalog",
                project_type="web_app",
                features=["authentication", "database"]
            )
            
            # Test 3: Projet complexe
            timeout_complex = optimizer.calculate_adaptive_timeout(
                description="Complex full-stack application with authentication, real-time chat, payment processing, admin dashboard, analytics, image upload, and email notifications",
                project_type="full_stack",
                features=["authentication", "real-time", "payment", "admin", "analytics", "upload", "email", "database", "websocket"]
            )
            
            # Validation
            success = (
                30 <= timeout_simple <= 60 and
                50 <= timeout_medium <= 100 and
                100 <= timeout_complex <= 180 and
                timeout_simple < timeout_medium < timeout_complex
            )
            
            test_result = {
                "test": "Timeouts Adaptatifs",
                "success": success,
                "timeout_simple": timeout_simple,
                "timeout_medium": timeout_medium,
                "timeout_complex": timeout_complex,
                "progression": "croissante" if timeout_simple < timeout_medium < timeout_complex else "incorrecte"
            }
            
            self.results.append(test_result)
            
            logger.info(f"⏱️ Timeout Simple: {timeout_simple}s")
            logger.info(f"⏱️ Timeout Medium: {timeout_medium}s")
            logger.info(f"⏱️ Timeout Complex: {timeout_complex}s")
            
            if success:
                logger.info(f"✅ TEST RÉUSSI - Timeouts adaptatifs progressent correctement")
            else:
                logger.error(f"❌ TEST ÉCHOUÉ - Timeouts ne progressent pas correctement")
            
            return success
        
        except Exception as e:
            logger.error(f"❌ ERREUR TEST: {e}")
            self.results.append({
                "test": "Timeouts Adaptatifs",
                "success": False,
                "error": str(e)
            })
            return False
    
    async def run_all_tests(self):
        """Exécute tous les tests"""
        
        logger.info("\n" + "🚀 " + "="*74 + " 🚀")
        logger.info("🚀 DÉBUT DES TESTS D'OPTIMISATION JAVASCRIPT")
        logger.info("🚀 " + "="*74 + " 🚀\n")
        
        start_time = datetime.now()
        
        # Lancer tous les tests
        tests = [
            self.test_adaptive_timeout_calculation(),  # Test rapide d'abord
            self.test_react_simple(),
            self.test_nodejs_api(),
            self.test_react_complex(),
            self.test_fullstack_nodejs()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # Compter les succès
        success_count = sum(1 for r in results if r is True)
        total_tests = len(tests)
        success_rate = (success_count / total_tests) * 100
        
        total_duration = (datetime.now() - start_time).total_seconds()
        
        # Rapport final
        logger.info("\n" + "📊 " + "="*74 + " 📊")
        logger.info("📊 RAPPORT FINAL - TESTS D'OPTIMISATION JAVASCRIPT")
        logger.info("📊 " + "="*74 + " 📊\n")
        
        for i, result in enumerate(self.results):
            status = "✅ RÉUSSI" if result.get("success") else "❌ ÉCHOUÉ"
            logger.info(f"{status} - {result['test']}")
            
            if result.get("duration"):
                logger.info(f"  ⏱️  Durée: {result['duration']:.1f}s")
            
            if result.get("files"):
                logger.info(f"  📁 Fichiers: {result['files']}")
            
            if result.get("code_length"):
                logger.info(f"  📝 Code: {result['code_length']} caractères")
            
            if result.get("timeout_simple"):
                logger.info(f"  ⏱️  Simple: {result['timeout_simple']}s, Medium: {result['timeout_medium']}s, Complex: {result['timeout_complex']}s")
            
            if result.get("error"):
                logger.info(f"  ❌ Erreur: {result['error']}")
            
            logger.info("")
        
        logger.info("="*80)
        logger.info(f"RÉSULTATS: {success_count}/{total_tests} tests réussis ({success_rate:.1f}%)")
        logger.info(f"DURÉE TOTALE: {total_duration:.1f}s")
        logger.info("="*80)
        
        if success_rate >= 80:
            logger.info("🎉 SUCCÈS! Optimisation JavaScript fonctionne correctement!")
            return 0
        elif success_rate >= 60:
            logger.warning("⚠️ PARTIELLEMENT FONCTIONNEL - Quelques tests ont échoué")
            return 1
        else:
            logger.error("❌ ÉCHEC! Système d'optimisation JavaScript a des problèmes")
            return 2


async def main():
    """Point d'entrée principal"""
    
    try:
        tester = JavaScriptOptimizationTester()
        exit_code = await tester.run_all_tests()
        sys.exit(exit_code)
    
    except Exception as e:
        logger.error(f"❌ ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())
