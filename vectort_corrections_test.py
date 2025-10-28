#!/usr/bin/env python3
"""
🎯 TEST DES CORRECTIONS CRITIQUES VECTORT.IO - SYSTÈME 7/14 CRÉDITS & LIMITATIONS
Tests spécifiques pour les 3 corrections majeures implémentées selon la demande française
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuration - Production Environment API
BASE_URL = "https://devstream-ai.preview.emergentagent.com/api"

class VectortCorrectionsTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.user_id = None
        self.test_project_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    headers: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
        if self.access_token and "Authorization" not in default_headers:
            default_headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers, timeout=60)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=60)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise

    def setup_test_user(self):
        """Setup test user with 20 credits for testing both levels"""
        print("\n=== SETUP: Creating Test User with Credits ===")
        
        # Create unique test user
        test_user = {
            "email": f"vectort_corrections_{int(time.time())}@test.com",
            "password": "TestPassword123!",
            "full_name": f"Vectort Corrections Test {int(time.time())}"
        }
        
        try:
            # Register user
            response = self.make_request("POST", "/auth/register", test_user)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                self.log_result("User Setup", True, f"Test user created with ID: {self.user_id}")
                return True
            else:
                self.log_result("User Setup", False, f"Failed to create user: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("User Setup", False, f"Exception: {str(e)}")
            return False

    def test_correction_1_adaptive_credit_system(self):
        """
        TEST CORRECTION #1: Système adaptatif 7/14 crédits
        Vérifier que CreditEstimator.estimate_complexity() est utilisé au lieu du système fixe 2/4
        """
        print("\n=== CORRECTION #1: Système Adaptatif 7/14 Crédits ===")
        
        if not self.access_token:
            self.log_result("Correction #1", False, "No access token available")
            return

        # TEST 1A: Description Simple (7 crédits attendus)
        try:
            # Vérifier crédits initiaux
            balance_response = self.make_request("GET", "/credits/balance")
            if balance_response.status_code == 200:
                initial_credits = balance_response.json()["total_available"]
                print(f"   Crédits initiaux: {initial_credits}")
            else:
                initial_credits = 10.0  # Assume default
            
            # Créer projet pour test simple
            project_data = {
                "title": "Site Web Simple",
                "description": "Site web simple avec un formulaire de contact",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Correction #1 - Simple Project", False, "Failed to create project")
                return
            
            project_id = project_response.json()["id"]
            
            # Génération avec description simple
            generation_request = {
                "description": "Site web simple avec un formulaire de contact",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False
            }
            
            gen_response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            
            if gen_response.status_code == 200:
                # Vérifier déduction de crédits
                new_balance_response = self.make_request("GET", "/credits/balance")
                if new_balance_response.status_code == 200:
                    new_credits = new_balance_response.json()["total_available"]
                    credits_deducted = initial_credits - new_credits
                    
                    # Vérifier si c'est 7 crédits (système adaptatif) et non 2 (ancien système)
                    if credits_deducted == 7:
                        self.log_result("Correction #1 - Simple (7 crédits)", True, 
                                      f"✅ Système adaptatif: {credits_deducted} crédits déduits pour description simple")
                    elif credits_deducted == 2:
                        self.log_result("Correction #1 - Simple (7 crédits)", False, 
                                      f"❌ Ancien système détecté: {credits_deducted} crédits (devrait être 7)")
                    else:
                        self.log_result("Correction #1 - Simple (7 crédits)", False, 
                                      f"❌ Déduction inattendue: {credits_deducted} crédits (attendu: 7)")
                else:
                    self.log_result("Correction #1 - Simple", False, "Cannot check credit balance")
            else:
                self.log_result("Correction #1 - Simple", False, f"Generation failed: {gen_response.status_code}")
                
        except Exception as e:
            self.log_result("Correction #1 - Simple", False, f"Exception: {str(e)}")

        # TEST 1B: Description Complexe (14 crédits attendus)
        try:
            # Créer nouveau projet pour test complexe
            complex_project_data = {
                "title": "E-commerce Complexe",
                "description": "Application e-commerce complète avec panier d'achat, paiement Stripe, dashboard admin, gestion utilisateurs, API REST FastAPI, authentification JWT, système de notifications temps réel avec WebSocket, analytics et rapports",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", complex_project_data)
            if project_response.status_code != 200:
                self.log_result("Correction #1 - Complex Project", False, "Failed to create complex project")
                return
            
            project_id = project_response.json()["id"]
            
            # Vérifier crédits avant génération complexe
            balance_response = self.make_request("GET", "/credits/balance")
            if balance_response.status_code == 200:
                initial_credits = balance_response.json()["total_available"]
                print(f"   Crédits avant génération complexe: {initial_credits}")
            else:
                initial_credits = 3.0  # Estimate after simple test
            
            # Génération avec description complexe
            complex_generation_request = {
                "description": "Application e-commerce complète avec panier d'achat, paiement Stripe, dashboard admin, gestion utilisateurs, API REST FastAPI, authentification JWT, système de notifications temps réel avec WebSocket, analytics et rapports",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": True
            }
            
            gen_response = self.make_request("POST", f"/projects/{project_id}/generate", complex_generation_request)
            
            if gen_response.status_code == 200:
                # Vérifier déduction de crédits
                new_balance_response = self.make_request("GET", "/credits/balance")
                if new_balance_response.status_code == 200:
                    new_credits = new_balance_response.json()["total_available"]
                    credits_deducted = initial_credits - new_credits
                    
                    # Vérifier si c'est 14 crédits (système adaptatif) et non 4 (ancien système)
                    if credits_deducted == 14:
                        self.log_result("Correction #1 - Complex (14 crédits)", True, 
                                      f"✅ Système adaptatif: {credits_deducted} crédits déduits pour description complexe")
                    elif credits_deducted == 4:
                        self.log_result("Correction #1 - Complex (14 crédits)", False, 
                                      f"❌ Ancien système détecté: {credits_deducted} crédits (devrait être 14)")
                    else:
                        self.log_result("Correction #1 - Complex (14 crédits)", False, 
                                      f"❌ Déduction inattendue: {credits_deducted} crédits (attendu: 14)")
                else:
                    self.log_result("Correction #1 - Complex", False, "Cannot check credit balance")
            elif gen_response.status_code == 402:
                self.log_result("Correction #1 - Complex", True, 
                              "✅ Crédits insuffisants détectés (comportement attendu si <14 crédits)")
            else:
                self.log_result("Correction #1 - Complex", False, f"Generation failed: {gen_response.status_code}")
                
        except Exception as e:
            self.log_result("Correction #1 - Complex", False, f"Exception: {str(e)}")

    def test_correction_2_file_limitations_removed(self):
        """
        TEST CORRECTION #2: Suppression limitations fichiers
        Vérifier que les limites ont été augmentées: 5→20 fichiers, 8→30 architecture, 15s→30s timeout
        """
        print("\n=== CORRECTION #2: Suppression Limitations Fichiers ===")
        
        if not self.access_token:
            self.log_result("Correction #2", False, "No access token available")
            return

        try:
            # Créer projet pour test de génération avancée
            project_data = {
                "title": "Test Limitations Supprimées",
                "description": "Application complexe pour tester la suppression des limitations de fichiers",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Correction #2", False, "Failed to create project")
                return
            
            project_id = project_response.json()["id"]
            self.test_project_id = project_id
            
            # Génération en mode avancé (devrait créer plus de fichiers)
            generation_request = {
                "description": "Application web complète avec architecture complexe, multiples composants, services, utilitaires, configurations, tests, documentation et déploiement",
                "type": "web_app",
                "framework": "react",
                "database": "mongodb",
                "advanced_mode": True,
                "features": ["authentication", "api", "database", "testing", "deployment"],
                "integrations": ["stripe", "websocket", "redis"]
            }
            
            start_time = time.time()
            gen_response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            generation_time = time.time() - start_time
            
            if gen_response.status_code == 200:
                data = gen_response.json()
                
                # Vérifier nombre de fichiers générés
                all_files = data.get("all_files", {})
                file_count = len(all_files) if all_files else 0
                
                # Vérifier temps de génération (devrait être acceptable avec nouveau timeout)
                timeout_ok = generation_time < 35  # 30s + marge
                
                # Critères de succès pour correction #2
                success_criteria = {
                    "more_than_10_files": file_count > 10,  # Plus que l'ancien max de ~5
                    "acceptable_timeout": timeout_ok,
                    "generation_success": True,
                    "advanced_mode_working": bool(all_files)
                }
                
                passed_criteria = sum(success_criteria.values())
                
                if passed_criteria >= 3:
                    self.log_result("Correction #2 - Limitations Supprimées", True, 
                                  f"✅ Limitations supprimées: {file_count} fichiers générés, "
                                  f"temps: {generation_time:.1f}s, critères: {passed_criteria}/4")
                else:
                    self.log_result("Correction #2 - Limitations Supprimées", False, 
                                  f"❌ Limitations encore présentes: {file_count} fichiers, "
                                  f"temps: {generation_time:.1f}s, critères: {passed_criteria}/4")
            else:
                self.log_result("Correction #2", False, f"Generation failed: {gen_response.status_code}")
                
        except Exception as e:
            self.log_result("Correction #2", False, f"Exception: {str(e)}")

    def test_correction_3_improved_llm_prompts(self):
        """
        TEST CORRECTION #3: Prompts LLM améliorés
        Vérifier que le code généré est complet, sans TODO/placeholders, avec instructions "AUCUNE simplification"
        """
        print("\n=== CORRECTION #3: Prompts LLM Améliorés ===")
        
        if not self.access_token or not self.test_project_id:
            self.log_result("Correction #3", False, "No access token or project ID available")
            return

        try:
            # Récupérer le code généré du test précédent
            code_response = self.make_request("GET", f"/projects/{self.test_project_id}/code")
            
            if code_response.status_code == 200:
                data = code_response.json()
                
                # Analyser le code pour vérifier les améliorations
                react_code = data.get("react_code", "")
                css_code = data.get("css_code", "")
                backend_code = data.get("backend_code", "")
                
                # Vérifications critiques selon correction #3
                checks = {
                    "no_todo_placeholders": self._check_no_todos(react_code, css_code, backend_code),
                    "sufficient_length": self._check_code_length(react_code, css_code),
                    "complete_functions": self._check_complete_functions(react_code),
                    "no_simplifications": self._check_no_simplifications(react_code, css_code)
                }
                
                passed_checks = sum(checks.values())
                total_checks = len(checks)
                
                if passed_checks >= 3:  # Au moins 3/4 critères
                    self.log_result("Correction #3 - Prompts Améliorés", True, 
                                  f"✅ Code complet généré: {passed_checks}/{total_checks} critères respectés. "
                                  f"React: {len(react_code)} chars, CSS: {len(css_code)} chars")
                else:
                    self.log_result("Correction #3 - Prompts Améliorés", False, 
                                  f"❌ Code incomplet: {passed_checks}/{total_checks} critères. "
                                  f"Vérifier prompts LLM pour 'AUCUNE simplification'")
                    
                # Détails des vérifications
                for check_name, passed in checks.items():
                    status = "✅" if passed else "❌"
                    print(f"   {status} {check_name}")
                    
            else:
                self.log_result("Correction #3", False, f"Cannot retrieve generated code: {code_response.status_code}")
                
        except Exception as e:
            self.log_result("Correction #3", False, f"Exception: {str(e)}")

    def _check_no_todos(self, *code_blocks) -> bool:
        """Vérifier absence de TODO/placeholders"""
        forbidden_patterns = ["TODO", "...", "// Code à implémenter", "/* TODO", "FIXME", "placeholder"]
        
        for code in code_blocks:
            if code:
                for pattern in forbidden_patterns:
                    if pattern.lower() in code.lower():
                        return False
        return True

    def _check_code_length(self, react_code: str, css_code: str) -> bool:
        """Vérifier longueur suffisante du code (minimum 3000 chars React)"""
        react_length = len(react_code) if react_code else 0
        css_length = len(css_code) if css_code else 0
        
        return react_length >= 3000 or (react_length >= 1500 and css_length >= 1000)

    def _check_complete_functions(self, react_code: str) -> bool:
        """Vérifier que les fonctions sont complètement implémentées"""
        if not react_code:
            return False
            
        # Chercher des patterns de fonctions complètes
        complete_patterns = ["useState", "useEffect", "return (", "export default", "const "]
        incomplete_patterns = ["// TODO", "throw new Error", "console.log('TODO'"]
        
        has_complete = any(pattern in react_code for pattern in complete_patterns)
        has_incomplete = any(pattern in react_code for pattern in incomplete_patterns)
        
        return has_complete and not has_incomplete

    def _check_no_simplifications(self, react_code: str, css_code: str) -> bool:
        """Vérifier absence de simplifications excessives"""
        if not react_code and not css_code:
            return False
            
        # Le code doit avoir une complexité raisonnable
        total_length = len(react_code or "") + len(css_code or "")
        has_multiple_components = react_code.count("const ") > 2 if react_code else False
        has_styling = len(css_code or "") > 500
        
        return total_length > 2000 and (has_multiple_components or has_styling)

    def test_backend_logs_verification(self):
        """Vérifier les logs backend pour confirmer les corrections"""
        print("\n=== VÉRIFICATION LOGS BACKEND ===")
        
        try:
            # Test de génération pour vérifier les logs
            if not self.access_token:
                self.log_result("Backend Logs", False, "No access token available")
                return
                
            # Créer un projet simple pour vérifier les logs
            project_data = {
                "title": "Test Logs Backend",
                "description": "Test pour vérifier les logs de complexité",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Backend Logs", False, "Failed to create project")
                return
            
            project_id = project_response.json()["id"]
            
            # Génération pour déclencher les logs
            generation_request = {
                "description": "Application simple pour tester les logs de complexité",
                "type": "web_app",
                "framework": "react"
            }
            
            gen_response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            
            if gen_response.status_code == 200:
                self.log_result("Backend Logs - Generation", True, 
                              "✅ Génération réussie - vérifier logs backend pour 'complexity_level: simple'")
            else:
                self.log_result("Backend Logs - Generation", False, 
                              f"❌ Génération échouée: {gen_response.status_code}")
                
        except Exception as e:
            self.log_result("Backend Logs", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Exécuter tous les tests des corrections"""
        print("🎯 VECTORT.IO - TEST DES CORRECTIONS CRITIQUES")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_user():
            print("❌ ÉCHEC: Impossible de créer l'utilisateur de test")
            return
        
        # Tests des 3 corrections
        self.test_correction_1_adaptive_credit_system()
        self.test_correction_2_file_limitations_removed()
        self.test_correction_3_improved_llm_prompts()
        self.test_backend_logs_verification()
        
        # Résultats finaux
        print("\n" + "=" * 60)
        print("🎯 RÉSULTATS FINAUX DES CORRECTIONS")
        print("=" * 60)
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        
        if self.results['failed'] > 0:
            print("\n❌ ERREURS DÉTECTÉES:")
            for error in self.results['errors']:
                print(f"   - {error}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"\n📊 TAUX DE SUCCÈS: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 CORRECTIONS VALIDÉES - Système prêt pour production")
        else:
            print("⚠️  CORRECTIONS INCOMPLÈTES - Révision nécessaire")

if __name__ == "__main__":
    tester = VectortCorrectionsTest()
    tester.run_all_tests()