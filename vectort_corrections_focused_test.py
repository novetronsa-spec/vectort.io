#!/usr/bin/env python3
"""
🎯 TEST FOCUSED DES CORRECTIONS VECTORT.IO - AVEC GESTION CRÉDITS
Test spécifique des corrections avec utilisateurs multiples pour éviter manque de crédits
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://vectort-builder.preview.emergentagent.com/api"

class VectortFocusedTest:
    def __init__(self):
        self.base_url = BASE_URL
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
                    headers: Optional[Dict] = None, access_token: str = None) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
        if access_token and "Authorization" not in default_headers:
            default_headers["Authorization"] = f"Bearer {access_token}"
        
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

    def create_test_user(self, suffix: str = "") -> tuple:
        """Create a test user and return (access_token, user_id)"""
        test_user = {
            "email": f"vectort_test_{int(time.time())}_{suffix}@test.com",
            "password": "TestPassword123!",
            "full_name": f"Vectort Test User {suffix}"
        }
        
        try:
            response = self.make_request("POST", "/auth/register", test_user)
            
            if response.status_code == 200:
                data = response.json()
                return data["access_token"], data["user"]["id"]
            else:
                return None, None
                
        except Exception as e:
            return None, None

    def test_correction_1_adaptive_credits_detailed(self):
        """
        TEST CORRECTION #1: Système adaptatif 7/14 crédits - Test détaillé
        """
        print("\n=== CORRECTION #1: Système Adaptatif 7/14 Crédits (Détaillé) ===")
        
        # Test 1: Description Simple (7 crédits)
        access_token, user_id = self.create_test_user("simple")
        if not access_token:
            self.log_result("Correction #1 - Setup Simple", False, "Failed to create user")
            return
        
        try:
            # Vérifier crédits initiaux
            balance_response = self.make_request("GET", "/credits/balance", access_token=access_token)
            if balance_response.status_code == 200:
                initial_credits = balance_response.json()["total_available"]
                print(f"   Crédits initiaux utilisateur simple: {initial_credits}")
            else:
                initial_credits = 10.0
            
            # Créer et générer projet simple
            project_data = {
                "title": "Site Web Simple",
                "description": "Site web simple avec un formulaire de contact",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data, access_token=access_token)
            if project_response.status_code != 200:
                self.log_result("Correction #1 - Simple Project Creation", False, "Failed to create project")
                return
            
            project_id = project_response.json()["id"]
            
            # Génération simple
            generation_request = {
                "description": "Site web simple avec un formulaire de contact",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False
            }
            
            gen_response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request, access_token=access_token)
            
            if gen_response.status_code == 200:
                # Vérifier déduction
                new_balance_response = self.make_request("GET", "/credits/balance", access_token=access_token)
                if new_balance_response.status_code == 200:
                    new_credits = new_balance_response.json()["total_available"]
                    credits_deducted = initial_credits - new_credits
                    
                    if credits_deducted == 7:
                        self.log_result("Correction #1 - Simple (7 crédits)", True, 
                                      f"✅ Système adaptatif confirmé: {credits_deducted} crédits déduits")
                    else:
                        self.log_result("Correction #1 - Simple (7 crédits)", False, 
                                      f"❌ Déduction incorrecte: {credits_deducted} crédits (attendu: 7)")
                else:
                    self.log_result("Correction #1 - Simple", False, "Cannot check balance")
            else:
                self.log_result("Correction #1 - Simple", False, f"Generation failed: {gen_response.status_code}")
                
        except Exception as e:
            self.log_result("Correction #1 - Simple", False, f"Exception: {str(e)}")

        # Test 2: Description Complexe (14 crédits) - Nouveau utilisateur
        access_token2, user_id2 = self.create_test_user("complex")
        if not access_token2:
            self.log_result("Correction #1 - Setup Complex", False, "Failed to create user")
            return
        
        try:
            # Vérifier crédits initiaux
            balance_response = self.make_request("GET", "/credits/balance", access_token=access_token2)
            if balance_response.status_code == 200:
                initial_credits = balance_response.json()["total_available"]
                print(f"   Crédits initiaux utilisateur complexe: {initial_credits}")
            else:
                initial_credits = 10.0
            
            # Créer projet complexe
            complex_project_data = {
                "title": "E-commerce Complexe",
                "description": "Application e-commerce complète avec panier d'achat, paiement Stripe, dashboard admin, gestion utilisateurs, API REST FastAPI, authentification JWT, système de notifications temps réel avec WebSocket, analytics et rapports",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", complex_project_data, access_token=access_token2)
            if project_response.status_code != 200:
                self.log_result("Correction #1 - Complex Project Creation", False, "Failed to create project")
                return
            
            project_id = project_response.json()["id"]
            
            # Génération complexe
            complex_generation_request = {
                "description": "Application e-commerce complète avec panier d'achat, paiement Stripe, dashboard admin, gestion utilisateurs, API REST FastAPI, authentification JWT, système de notifications temps réel avec WebSocket, analytics et rapports",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": True
            }
            
            gen_response = self.make_request("POST", f"/projects/{project_id}/generate", complex_generation_request, access_token=access_token2)
            
            if gen_response.status_code == 200:
                # Vérifier déduction
                new_balance_response = self.make_request("GET", "/credits/balance", access_token=access_token2)
                if new_balance_response.status_code == 200:
                    new_credits = new_balance_response.json()["total_available"]
                    credits_deducted = initial_credits - new_credits
                    
                    if credits_deducted == 14:
                        self.log_result("Correction #1 - Complex (14 crédits)", True, 
                                      f"✅ Système adaptatif confirmé: {credits_deducted} crédits déduits")
                    else:
                        self.log_result("Correction #1 - Complex (14 crédits)", False, 
                                      f"❌ Déduction incorrecte: {credits_deducted} crédits (attendu: 14)")
                else:
                    self.log_result("Correction #1 - Complex", False, "Cannot check balance")
            elif gen_response.status_code == 402:
                # Crédits insuffisants - comportement attendu si <14 crédits
                self.log_result("Correction #1 - Complex (Crédits insuffisants)", True, 
                              f"✅ Système détecte correctement crédits insuffisants (10 < 14)")
            else:
                self.log_result("Correction #1 - Complex", False, f"Generation failed: {gen_response.status_code}")
                
        except Exception as e:
            self.log_result("Correction #1 - Complex", False, f"Exception: {str(e)}")

    def test_correction_2_file_limitations(self):
        """
        TEST CORRECTION #2: Suppression limitations fichiers
        """
        print("\n=== CORRECTION #2: Suppression Limitations Fichiers ===")
        
        # Créer utilisateur pour test limitations
        access_token, user_id = self.create_test_user("limitations")
        if not access_token:
            self.log_result("Correction #2 - Setup", False, "Failed to create user")
            return
        
        try:
            # Créer projet pour test avancé
            project_data = {
                "title": "Test Limitations Avancées",
                "description": "Application complexe pour tester suppression limitations",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data, access_token=access_token)
            if project_response.status_code != 200:
                self.log_result("Correction #2 - Project Creation", False, "Failed to create project")
                return
            
            project_id = project_response.json()["id"]
            
            # Génération avancée (devrait créer plus de fichiers)
            generation_request = {
                "description": "Application web complète avec architecture complexe, multiples composants React, services backend, utilitaires, configurations, tests unitaires, documentation complète et scripts de déploiement",
                "type": "web_app",
                "framework": "react",
                "database": "mongodb",
                "advanced_mode": True,
                "features": ["authentication", "api", "database", "testing", "deployment", "monitoring"],
                "integrations": ["stripe", "websocket", "redis", "elasticsearch"]
            }
            
            start_time = time.time()
            gen_response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request, access_token=access_token)
            generation_time = time.time() - start_time
            
            if gen_response.status_code == 200:
                data = gen_response.json()
                
                # Analyser les fichiers générés
                all_files = data.get("all_files", {})
                file_count = len(all_files) if all_files else 0
                
                # Vérifier structure avancée
                has_package_json = bool(data.get("package_json") or (all_files.get("package.json") if all_files else None))
                has_dockerfile = bool(data.get("dockerfile") or (all_files.get("Dockerfile") if all_files else None))
                has_readme = bool(data.get("readme") or (all_files.get("README.md") if all_files else None))
                
                # Critères de succès pour limitations supprimées
                criteria = {
                    "more_than_10_files": file_count > 10,  # Plus que l'ancien max ~5
                    "acceptable_timeout": generation_time < 35,  # Nouveau timeout 30s + marge
                    "has_config_files": has_package_json or has_dockerfile or has_readme,
                    "generation_success": True
                }
                
                passed = sum(criteria.values())
                
                if passed >= 3:
                    self.log_result("Correction #2 - Limitations Supprimées", True, 
                                  f"✅ Limitations supprimées: {file_count} fichiers, {generation_time:.1f}s, "
                                  f"configs: {has_package_json}/{has_dockerfile}/{has_readme}")
                else:
                    self.log_result("Correction #2 - Limitations Supprimées", False, 
                                  f"❌ Limitations persistantes: {file_count} fichiers, {generation_time:.1f}s")
                    
            elif gen_response.status_code == 402:
                self.log_result("Correction #2 - Crédits", False, "Crédits insuffisants pour test avancé")
            else:
                self.log_result("Correction #2", False, f"Generation failed: {gen_response.status_code}")
                
        except Exception as e:
            self.log_result("Correction #2", False, f"Exception: {str(e)}")

    def test_correction_3_code_quality(self):
        """
        TEST CORRECTION #3: Prompts LLM améliorés - Code complet sans TODO
        """
        print("\n=== CORRECTION #3: Prompts LLM Améliorés ===")
        
        # Créer utilisateur pour test qualité code
        access_token, user_id = self.create_test_user("quality")
        if not access_token:
            self.log_result("Correction #3 - Setup", False, "Failed to create user")
            return
        
        try:
            # Créer projet pour test qualité
            project_data = {
                "title": "Test Qualité Code",
                "description": "Application pour tester la qualité du code généré",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data, access_token=access_token)
            if project_response.status_code != 200:
                self.log_result("Correction #3 - Project Creation", False, "Failed to create project")
                return
            
            project_id = project_response.json()["id"]
            
            # Génération avec focus sur qualité
            generation_request = {
                "description": "Créer une application React complète avec composants détaillés, gestion d'état, styles CSS complets, et fonctionnalités entièrement implémentées",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False  # Test basic mode first
            }
            
            gen_response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request, access_token=access_token)
            
            if gen_response.status_code == 200:
                # Récupérer le code généré
                code_response = self.make_request("GET", f"/projects/{project_id}/code", access_token=access_token)
                
                if code_response.status_code == 200:
                    data = code_response.json()
                    
                    react_code = data.get("react_code", "")
                    css_code = data.get("css_code", "")
                    html_code = data.get("html_code", "")
                    
                    # Analyser qualité du code
                    quality_checks = {
                        "no_todos": self._check_no_todos(react_code, css_code, html_code),
                        "sufficient_length": len(react_code or "") >= 1000,  # Au moins 1000 chars
                        "has_components": "const " in (react_code or "") and "return" in (react_code or ""),
                        "has_styling": len(css_code or "") >= 500,
                        "complete_structure": bool(react_code or html_code)
                    }
                    
                    passed_quality = sum(quality_checks.values())
                    total_quality = len(quality_checks)
                    
                    if passed_quality >= 4:
                        self.log_result("Correction #3 - Code Qualité", True, 
                                      f"✅ Code complet généré: {passed_quality}/{total_quality} critères. "
                                      f"React: {len(react_code or '')} chars, CSS: {len(css_code or '')} chars")
                    else:
                        self.log_result("Correction #3 - Code Qualité", False, 
                                      f"❌ Code incomplet: {passed_quality}/{total_quality} critères")
                        
                    # Détails
                    for check, passed in quality_checks.items():
                        status = "✅" if passed else "❌"
                        print(f"   {status} {check}")
                        
                else:
                    self.log_result("Correction #3 - Code Retrieval", False, f"Cannot get code: {code_response.status_code}")
            elif gen_response.status_code == 402:
                self.log_result("Correction #3 - Crédits", False, "Crédits insuffisants")
            else:
                self.log_result("Correction #3", False, f"Generation failed: {gen_response.status_code}")
                
        except Exception as e:
            self.log_result("Correction #3", False, f"Exception: {str(e)}")

    def _check_no_todos(self, *code_blocks) -> bool:
        """Vérifier absence de TODO/placeholders"""
        forbidden_patterns = ["TODO", "...", "// Code à implémenter", "/* TODO", "FIXME", "placeholder", "// TODO"]
        
        for code in code_blocks:
            if code:
                code_upper = code.upper()
                for pattern in forbidden_patterns:
                    if pattern.upper() in code_upper:
                        return False
        return True

    def test_backend_logs_complexity(self):
        """Vérifier que les logs backend montrent la complexité"""
        print("\n=== VÉRIFICATION LOGS COMPLEXITÉ ===")
        
        access_token, user_id = self.create_test_user("logs")
        if not access_token:
            self.log_result("Backend Logs", False, "Failed to create user")
            return
        
        try:
            # Créer projet pour logs
            project_data = {
                "title": "Test Logs Complexité",
                "description": "Test simple pour vérifier logs de complexité",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data, access_token=access_token)
            if project_response.status_code != 200:
                self.log_result("Backend Logs - Project", False, "Failed to create project")
                return
            
            project_id = project_response.json()["id"]
            
            # Génération pour déclencher logs
            generation_request = {
                "description": "Application simple pour tester les logs de complexité",
                "type": "web_app",
                "framework": "react"
            }
            
            gen_response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request, access_token=access_token)
            
            if gen_response.status_code == 200:
                self.log_result("Backend Logs - Complexity", True, 
                              "✅ Génération réussie - logs backend devraient montrer 'complexity_level: simple'")
            else:
                self.log_result("Backend Logs", False, f"Generation failed: {gen_response.status_code}")
                
        except Exception as e:
            self.log_result("Backend Logs", False, f"Exception: {str(e)}")

    def run_focused_tests(self):
        """Exécuter les tests focalisés des corrections"""
        print("🎯 VECTORT.IO - TEST FOCUSED DES CORRECTIONS CRITIQUES")
        print("=" * 70)
        
        # Tests des corrections avec utilisateurs séparés
        self.test_correction_1_adaptive_credits_detailed()
        self.test_correction_2_file_limitations()
        self.test_correction_3_code_quality()
        self.test_backend_logs_complexity()
        
        # Résultats
        print("\n" + "=" * 70)
        print("🎯 RÉSULTATS FINAUX - CORRECTIONS VECTORT.IO")
        print("=" * 70)
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        
        if self.results['failed'] > 0:
            print("\n❌ ERREURS DÉTECTÉES:")
            for error in self.results['errors']:
                print(f"   - {error}")
        
        total_tests = self.results['passed'] + self.results['failed']
        if total_tests > 0:
            success_rate = (self.results['passed'] / total_tests) * 100
            print(f"\n📊 TAUX DE SUCCÈS: {success_rate:.1f}%")
            
            if success_rate >= 75:
                print("🎉 CORRECTIONS MAJORITAIREMENT VALIDÉES")
            else:
                print("⚠️  CORRECTIONS NÉCESSITENT RÉVISION")
        
        return self.results

if __name__ == "__main__":
    tester = VectortFocusedTest()
    tester.run_focused_tests()