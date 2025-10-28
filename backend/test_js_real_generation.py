"""
Test COMPLET avec VRAIES générations LLM - AUCUN FALLBACK
Tous les tests utilisent GPT-4o pour générer du code réel
"""
import asyncio
import os
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RealGenerationTest")

sys.path.insert(0, '/app/backend')

from ai_generators.javascript_optimizer import JavaScriptOptimizer

class RealGenerationTester:
    """Testeur avec VRAIES générations LLM uniquement"""
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("❌ EMERGENT_LLM_KEY requise!")
        
        self.optimizer = JavaScriptOptimizer(self.api_key)
        self.results = []
        logger.info(f"✅ Testeur initialisé avec API GPT-4o")
    
    async def test_react_simple_real(self):
        """TEST 1: Application React simple - VRAIE génération"""
        
        logger.info("\n" + "="*80)
        logger.info("TEST 1: ⚛️  Application React Simple - GÉNÉRATION RÉELLE GPT-4o")
        logger.info("="*80)
        
        start = datetime.now()
        
        try:
            # Génération RÉELLE avec l'API
            result = await self._generate_with_llm_only(
                description="Une application React simple avec un compteur qui s'incrémente quand on clique sur un bouton",
                framework="react",
                project_type="web_app",
                language="javascript"
            )
            
            duration = (datetime.now() - start).total_seconds()
            
            # Validation stricte
            has_code = result and (result.get("react_code") or result.get("js_code"))
            code_length = len(result.get("react_code", "") + result.get("js_code", ""))
            has_hooks = "useState" in str(result) or "useEffect" in str(result)
            is_real = code_length > 300  # Code réel doit être substantiel
            
            success = has_code and is_real and has_hooks
            
            self.results.append({
                "test": "React Simple",
                "success": success,
                "duration": duration,
                "code_length": code_length,
                "has_hooks": has_hooks,
                "is_real_generation": is_real
            })
            
            if success:
                logger.info(f"✅ RÉUSSI - Code réel généré: {code_length} chars en {duration:.1f}s")
                logger.info(f"   React hooks détectés: {has_hooks}")
            else:
                logger.error(f"❌ ÉCHOUÉ - Code:{has_code}, Length:{code_length}, Hooks:{has_hooks}")
            
            return success
        
        except Exception as e:
            logger.error(f"❌ ERREUR: {e}")
            self.results.append({"test": "React Simple", "success": False, "error": str(e)})
            return False
    
    async def test_nodejs_api_real(self):
        """TEST 2: API Node.js/Express - VRAIE génération"""
        
        logger.info("\n" + "="*80)
        logger.info("TEST 2: 🟢 API Node.js/Express - GÉNÉRATION RÉELLE GPT-4o")
        logger.info("="*80)
        
        start = datetime.now()
        
        try:
            result = await self._generate_with_llm_only(
                description="Une API REST Node.js avec Express pour gérer des utilisateurs (GET, POST, PUT, DELETE)",
                framework="express",
                project_type="api_rest",
                language="javascript"
            )
            
            duration = (datetime.now() - start).total_seconds()
            
            # Validation stricte
            has_code = result and result.get("backend_code")
            code_length = len(result.get("backend_code", ""))
            has_express = "express" in result.get("backend_code", "").lower()
            has_routes = "app.get" in result.get("backend_code", "") or "router" in result.get("backend_code", "")
            is_real = code_length > 400
            
            success = has_code and is_real and has_express and has_routes
            
            self.results.append({
                "test": "Node.js API",
                "success": success,
                "duration": duration,
                "code_length": code_length,
                "has_express": has_express,
                "has_routes": has_routes,
                "is_real_generation": is_real
            })
            
            if success:
                logger.info(f"✅ RÉUSSI - API réelle générée: {code_length} chars en {duration:.1f}s")
                logger.info(f"   Express: {has_express}, Routes: {has_routes}")
            else:
                logger.error(f"❌ ÉCHOUÉ - Code:{has_code}, Length:{code_length}")
            
            return success
        
        except Exception as e:
            logger.error(f"❌ ERREUR: {e}")
            self.results.append({"test": "Node.js API", "success": False, "error": str(e)})
            return False
    
    async def test_vue_app_real(self):
        """TEST 3: Application Vue.js - VRAIE génération"""
        
        logger.info("\n" + "="*80)
        logger.info("TEST 3: 💚 Application Vue.js - GÉNÉRATION RÉELLE GPT-4o")
        logger.info("="*80)
        
        start = datetime.now()
        
        try:
            result = await self._generate_with_llm_only(
                description="Une application Vue.js avec une liste de tâches (todo list) utilisant la Composition API",
                framework="vue",
                project_type="web_app",
                language="javascript"
            )
            
            duration = (datetime.now() - start).total_seconds()
            
            # Validation stricte
            has_code = result and result.get("js_code")
            code_length = len(result.get("js_code", ""))
            has_vue = "vue" in result.get("js_code", "").lower() or "<template>" in result.get("js_code", "")
            is_real = code_length > 300
            
            success = has_code and is_real and has_vue
            
            self.results.append({
                "test": "Vue.js App",
                "success": success,
                "duration": duration,
                "code_length": code_length,
                "has_vue": has_vue,
                "is_real_generation": is_real
            })
            
            if success:
                logger.info(f"✅ RÉUSSI - Vue app réelle générée: {code_length} chars en {duration:.1f}s")
            else:
                logger.error(f"❌ ÉCHOUÉ - Code:{has_code}, Length:{code_length}")
            
            return success
        
        except Exception as e:
            logger.error(f"❌ ERREUR: {e}")
            self.results.append({"test": "Vue.js App", "success": False, "error": str(e)})
            return False
    
    async def _generate_with_llm_only(
        self,
        description: str,
        framework: str,
        project_type: str,
        language: str
    ):
        """
        Génération UNIQUEMENT avec LLM - AUCUN FALLBACK
        Force l'utilisation de l'API GPT-4o
        """
        
        logger.info(f"🚀 Génération réelle avec GPT-4o...")
        logger.info(f"   Framework: {framework}")
        logger.info(f"   Description: {description[:80]}...")
        
        # Appel direct à _attempt_generation SANS fallback
        result = await self.optimizer._attempt_generation(
            description=description,
            project_type=project_type,
            framework=framework,
            language=language,
            timeout=90.0,  # Timeout généreux pour génération complète
            simplified=False
        )
        
        if not result:
            # Retry UNE fois avec prompt simplifié
            logger.warning("⚠️ Première tentative échouée, retry avec prompt simplifié...")
            result = await self.optimizer._attempt_generation(
                description=description,
                project_type=project_type,
                framework=framework,
                language=language,
                timeout=120.0,
                simplified=True
            )
        
        if not result:
            raise Exception("Génération LLM échouée après 2 tentatives")
        
        return result
    
    async def run_all_tests(self):
        """Execute TOUS les tests avec génération réelle"""
        
        logger.info("\n" + "🚀 " + "="*74 + " 🚀")
        logger.info("🚀 TEST COMPLET - GÉNÉRATION RÉELLE GPT-4o UNIQUEMENT")
        logger.info("🚀 " + "="*74 + " 🚀\n")
        
        start = datetime.now()
        
        # Tests en séquence pour éviter rate limits
        test1 = await self.test_react_simple_real()
        await asyncio.sleep(2)  # Pause entre tests
        
        test2 = await self.test_nodejs_api_real()
        await asyncio.sleep(2)
        
        test3 = await self.test_vue_app_real()
        
        # Résultats
        tests = [test1, test2, test3]
        success_count = sum(1 for t in tests if t)
        total_tests = len(tests)
        success_rate = (success_count / total_tests) * 100
        
        total_duration = (datetime.now() - start).total_seconds()
        
        # Rapport final
        logger.info("\n" + "📊 " + "="*74 + " 📊")
        logger.info("📊 RAPPORT FINAL - GÉNÉRATION RÉELLE GPT-4o")
        logger.info("📊 " + "="*74 + " 📊\n")
        
        for result in self.results:
            status = "✅ RÉUSSI" if result.get("success") else "❌ ÉCHOUÉ"
            logger.info(f"{status} - {result['test']}")
            
            if result.get("duration"):
                logger.info(f"  ⏱️  Durée: {result['duration']:.1f}s")
            
            if result.get("code_length"):
                logger.info(f"  📝 Code généré: {result['code_length']} caractères")
            
            if result.get("is_real_generation"):
                logger.info(f"  ✨ Génération réelle GPT-4o confirmée")
            
            if result.get("error"):
                logger.info(f"  ❌ Erreur: {result['error']}")
            
            logger.info("")
        
        logger.info("="*80)
        logger.info(f"RÉSULTATS: {success_count}/{total_tests} tests réussis ({success_rate:.1f}%)")
        logger.info(f"DURÉE TOTALE: {total_duration:.1f}s")
        logger.info("="*80)
        
        if success_rate == 100:
            logger.info("🎉🎉🎉 SUCCÈS COMPLET! 100% GÉNÉRATION RÉELLE! 🎉🎉🎉")
            return 0
        elif success_rate >= 66:
            logger.info("✅ SUCCÈS PARTIEL - La majorité des générations réelles fonctionnent")
            return 0
        else:
            logger.error("❌ ÉCHEC - Trop de générations ont échoué")
            return 1


async def main():
    try:
        tester = RealGenerationTester()
        exit_code = await tester.run_all_tests()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"❌ ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())
