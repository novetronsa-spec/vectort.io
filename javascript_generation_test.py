#!/usr/bin/env python3
"""
🎯 TEST BACKEND COMPLET - JavaScript Optimizer & Mode Avancé

Contexte: Le mode rapide fonctionne à 100% mais le mode avancé retourne du code vide.
Nous devons tester TOUS les endpoints de génération pour identifier le problème.

Tests Backend à Effectuer selon la demande française:
1. Tests Génération Mode Rapide (Quick Mode)
2. Tests Génération Mode Avancé (Advanced Mode) - CRITIQUE
3. Tests JavaScriptOptimizer Direct
4. Tests Mapping
5. Tests Fallbacks
6. Tests Différents Frameworks
7. Tests Credit System
8. Logs Backend
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuration - PRODUCTION ENVIRONMENT API
BASE_URL = "https://devstream-ai.preview.emergentagent.com/api"
TEST_USER = {
    "email": f"js_test_{int(time.time())}@vectort.io",
    "password": "TestPassword123!",
    "full_name": f"JS Test User {int(time.time())}"
}

class JavaScriptGenerationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.user_id = None
        self.test_project_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
            "critical_issues": []
        }

    def log_result(self, test_name: str, success: bool, message: str = "", critical: bool = False):
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
            if critical:
                self.results["critical_issues"].append(f"{test_name}: {message}")

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    headers: Optional[Dict] = None, timeout: int = 60) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
        if self.access_token and "Authorization" not in default_headers:
            default_headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=default_headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise

    def setup_test_user(self):
        """Setup test user and authentication"""
        print("\n=== SETUP: User Authentication ===")
        try:
            # Try to register new user
            response = self.make_request("POST", "/auth/register", TEST_USER)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                self.log_result("User Setup", True, f"User registered with ID: {self.user_id}")
            elif response.status_code == 400:
                # User exists, try login
                login_response = self.make_request("POST", "/auth/login", {
                    "email": TEST_USER["email"],
                    "password": TEST_USER["password"]
                })
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.access_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    self.log_result("User Setup", True, f"User logged in with ID: {self.user_id}")
                else:
                    self.log_result("User Setup", False, f"Login failed: {login_response.status_code}")
                    return False
            else:
                self.log_result("User Setup", False, f"Registration failed: {response.status_code}")
                return False
            
            return True
        except Exception as e:
            self.log_result("User Setup", False, f"Exception: {str(e)}")
            return False

    def test_quick_mode_generation(self):
        """Test 1: Tests Génération Mode Rapide (Quick Mode)"""
        print("\n=== Test 1: Mode Rapide (Quick Mode) ===")
        try:
            if not self.access_token:
                self.log_result("Quick Mode Generation", False, "No access token available")
                return
            
            # Create project
            project_data = {
                "title": "Application React Compteur - Mode Rapide",
                "description": "Application React simple avec compteur",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Quick Mode Generation", False, f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Generate with QUICK MODE (advanced_mode: false)
            generation_request = {
                "description": "Application React simple avec compteur",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False  # MODE RAPIDE
            }
            
            start_time = time.time()
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request, timeout=120)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Vérifications critiques
                html_code = data.get("html_code", "")
                css_code = data.get("css_code", "")
                react_code = data.get("react_code", "")
                all_files = data.get("all_files", {})
                
                # Vérifier format de réponse
                has_html = bool(html_code)
                has_css = bool(css_code)
                has_react = bool(react_code)
                has_all_files = bool(all_files)
                
                code_not_empty = has_html or has_css or has_react
                
                if code_not_empty:
                    self.log_result("Quick Mode Generation", True, 
                                  f"✅ Mode rapide fonctionne: HTML({len(html_code)}), CSS({len(css_code)}), React({len(react_code)}), "
                                  f"all_files({len(all_files)}), temps: {generation_time:.1f}s")
                    self.test_project_id = project_id  # Store for further tests
                else:
                    self.log_result("Quick Mode Generation", False, 
                                  "❌ Mode rapide retourne du code vide", critical=True)
            else:
                self.log_result("Quick Mode Generation", False, 
                              f"❌ Mode rapide échoué: {response.status_code} - {response.text}", critical=True)
        except Exception as e:
            self.log_result("Quick Mode Generation", False, f"Exception: {str(e)}", critical=True)

    def test_advanced_mode_generation(self):
        """Test 2: Tests Génération Mode Avancé (Advanced Mode) - CRITIQUE"""
        print("\n=== Test 2: Mode Avancé (Advanced Mode) - CRITIQUE ===")
        try:
            if not self.access_token:
                self.log_result("Advanced Mode Generation", False, "No access token available")
                return
            
            # Create project
            project_data = {
                "title": "Application React Compteur - Mode Avancé",
                "description": "Application React simple avec compteur",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Advanced Mode Generation", False, f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Generate with ADVANCED MODE (advanced_mode: true)
            generation_request = {
                "description": "Application React simple avec compteur",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": True  # MODE AVANCÉ
            }
            
            start_time = time.time()
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request, timeout=180)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Vérifications critiques selon la demande
                html_code = data.get("html_code", "")
                css_code = data.get("css_code", "")
                react_code = data.get("react_code", "")
                all_files = data.get("all_files", {})
                
                # Vérifier que le code généré n'est pas vide
                has_html = bool(html_code)
                has_css = bool(css_code)
                has_react = bool(react_code)
                has_all_files = bool(all_files)
                
                code_not_empty = has_html or has_css or has_react
                
                if code_not_empty:
                    self.log_result("Advanced Mode Generation", True, 
                                  f"✅ Mode avancé fonctionne: HTML({len(html_code)}), CSS({len(css_code)}), React({len(react_code)}), "
                                  f"all_files({len(all_files)}), temps: {generation_time:.1f}s")
                else:
                    self.log_result("Advanced Mode Generation", False, 
                                  f"❌ PROBLÈME CRITIQUE: Mode avancé retourne du code vide! "
                                  f"HTML: {len(html_code)}, CSS: {len(css_code)}, React: {len(react_code)}, "
                                  f"all_files: {len(all_files)}, temps: {generation_time:.1f}s", critical=True)
                    
                    # Analyser pourquoi all_files est vide
                    if not all_files:
                        self.results["critical_issues"].append("all_files field is empty in advanced mode")
            else:
                self.log_result("Advanced Mode Generation", False, 
                              f"❌ Mode avancé échoué: {response.status_code} - {response.text}", critical=True)
        except Exception as e:
            self.log_result("Advanced Mode Generation", False, f"Exception: {str(e)}", critical=True)

    def test_complex_project_advanced_mode(self):
        """Test 3: Mode Avancé avec Projet Complexe"""
        print("\n=== Test 3: Mode Avancé avec Projet Complexe ===")
        try:
            if not self.access_token:
                self.log_result("Complex Advanced Mode", False, "No access token available")
                return
            
            # Create complex project
            project_data = {
                "title": "E-commerce React Complexe",
                "description": "Application e-commerce React avec authentification, panier, paiement Stripe",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Complex Advanced Mode", False, f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Generate complex project with advanced mode
            generation_request = {
                "description": "Application e-commerce React avec authentification, panier, paiement Stripe",
                "type": "web_app",
                "framework": "react",
                "features": ["authentication", "payment"],
                "advanced_mode": True
            }
            
            start_time = time.time()
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request, timeout=300)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Vérifications pour projet complexe
                html_code = data.get("html_code", "")
                css_code = data.get("css_code", "")
                react_code = data.get("react_code", "")
                backend_code = data.get("backend_code", "")
                all_files = data.get("all_files", {})
                
                code_not_empty = bool(html_code or css_code or react_code or backend_code)
                
                if code_not_empty:
                    self.log_result("Complex Advanced Mode", True, 
                                  f"✅ Projet complexe généré: HTML({len(html_code)}), CSS({len(css_code)}), "
                                  f"React({len(react_code)}), Backend({len(backend_code)}), "
                                  f"all_files({len(all_files)}), temps: {generation_time:.1f}s")
                else:
                    self.log_result("Complex Advanced Mode", False, 
                                  "❌ Projet complexe retourne du code vide", critical=True)
            elif response.status_code == 402:
                self.log_result("Complex Advanced Mode", False, "❌ Crédits insuffisants pour projet complexe")
            else:
                self.log_result("Complex Advanced Mode", False, 
                              f"❌ Projet complexe échoué: {response.status_code} - {response.text}")
        except Exception as e:
            self.log_result("Complex Advanced Mode", False, f"Exception: {str(e)}")

    def test_different_frameworks(self):
        """Test 6: Tests Différents Frameworks"""
        print("\n=== Test 6: Tests Différents Frameworks ===")
        
        frameworks = [
            ("react", "Application React avec hooks"),
            ("vue", "Application Vue.js avec composition API"),
            ("express", "API Express/Node.js avec MongoDB")
        ]
        
        for framework, description in frameworks:
            try:
                if not self.access_token:
                    self.log_result(f"Framework {framework}", False, "No access token available")
                    continue
                
                # Create project
                project_data = {
                    "title": f"Test {framework.title()}",
                    "description": description,
                    "type": "web_app"
                }
                
                project_response = self.make_request("POST", "/projects", project_data)
                if project_response.status_code != 200:
                    self.log_result(f"Framework {framework}", False, f"Failed to create project: {project_response.status_code}")
                    continue
                
                project_id = project_response.json()["id"]
                
                # Test both modes for each framework
                for advanced_mode in [False, True]:
                    mode_name = "Advanced" if advanced_mode else "Quick"
                    
                    generation_request = {
                        "description": description,
                        "type": "web_app",
                        "framework": framework,
                        "advanced_mode": advanced_mode
                    }
                    
                    start_time = time.time()
                    response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request, timeout=180)
                    generation_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                        has_code = any(data.get(field) for field in code_fields)
                        
                        if has_code:
                            self.log_result(f"Framework {framework} ({mode_name})", True, 
                                          f"✅ {framework} génération réussie en mode {mode_name}, temps: {generation_time:.1f}s")
                        else:
                            self.log_result(f"Framework {framework} ({mode_name})", False, 
                                          f"❌ {framework} retourne du code vide en mode {mode_name}")
                    elif response.status_code == 402:
                        self.log_result(f"Framework {framework} ({mode_name})", False, "❌ Crédits insuffisants")
                        break  # Stop testing this framework if no credits
                    else:
                        self.log_result(f"Framework {framework} ({mode_name})", False, 
                                      f"❌ {framework} échoué: {response.status_code}")
                        
            except Exception as e:
                self.log_result(f"Framework {framework}", False, f"Exception: {str(e)}")

    def test_credit_system(self):
        """Test 7: Tests Credit System"""
        print("\n=== Test 7: Tests Credit System ===")
        try:
            if not self.access_token:
                self.log_result("Credit System", False, "No access token available")
                return
            
            # Check initial credit balance
            response = self.make_request("GET", "/credits/balance")
            
            if response.status_code == 200:
                data = response.json()
                initial_credits = data.get("total_available", 0)
                
                self.log_result("Credit Balance Check", True, 
                              f"✅ Crédits disponibles: {initial_credits}")
                
                # Test credit deduction with quick mode
                if initial_credits >= 7:  # Need at least 7 credits for simple generation
                    project_data = {
                        "title": "Test Déduction Crédits",
                        "description": "Test simple pour vérifier déduction crédits",
                        "type": "web_app"
                    }
                    
                    project_response = self.make_request("POST", "/projects", project_data)
                    if project_response.status_code == 200:
                        project_id = project_response.json()["id"]
                        
                        generation_request = {
                            "description": "Application simple",
                            "type": "web_app",
                            "framework": "react",
                            "advanced_mode": False
                        }
                        
                        gen_response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
                        
                        if gen_response.status_code == 200:
                            # Check credit balance after generation
                            balance_response = self.make_request("GET", "/credits/balance")
                            if balance_response.status_code == 200:
                                final_credits = balance_response.json().get("total_available", 0)
                                credits_used = initial_credits - final_credits
                                
                                if credits_used > 0:
                                    self.log_result("Credit Deduction", True, 
                                                  f"✅ Crédits déduits correctement: {credits_used} crédits utilisés")
                                else:
                                    self.log_result("Credit Deduction", False, 
                                                  "❌ Aucun crédit déduit après génération")
                            else:
                                self.log_result("Credit Deduction", False, "❌ Impossible de vérifier solde final")
                        else:
                            self.log_result("Credit Deduction", False, f"❌ Génération échouée: {gen_response.status_code}")
                else:
                    self.log_result("Credit System", False, f"❌ Crédits insuffisants pour test: {initial_credits}")
            else:
                self.log_result("Credit System", False, f"❌ Impossible de récupérer solde: {response.status_code}")
                
        except Exception as e:
            self.log_result("Credit System", False, f"Exception: {str(e)}")

    def test_code_retrieval(self):
        """Test: Code Retrieval"""
        print("\n=== Test: Code Retrieval ===")
        try:
            if not self.access_token or not self.test_project_id:
                self.log_result("Code Retrieval", False, "No access token or project ID available")
                return
            
            response = self.make_request("GET", f"/projects/{self.test_project_id}/code")
            
            if response.status_code == 200:
                data = response.json()
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                has_code = any(data.get(field) for field in code_fields)
                
                if has_code:
                    self.log_result("Code Retrieval", True, "✅ Code récupéré avec succès")
                else:
                    self.log_result("Code Retrieval", False, "❌ Aucun code trouvé")
            elif response.status_code == 404:
                self.log_result("Code Retrieval", False, "❌ Code généré non trouvé")
            else:
                self.log_result("Code Retrieval", False, f"❌ Erreur: {response.status_code}")
                
        except Exception as e:
            self.log_result("Code Retrieval", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all JavaScript generation tests"""
        print("🎯 DÉMARRAGE DES TESTS JAVASCRIPT GENERATION & MODE AVANCÉ")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_user():
            print("❌ ÉCHEC: Impossible de configurer l'utilisateur de test")
            return
        
        # Run tests in order
        self.test_quick_mode_generation()
        self.test_advanced_mode_generation()
        self.test_complex_project_advanced_mode()
        self.test_different_frameworks()
        self.test_credit_system()
        self.test_code_retrieval()
        
        # Final report
        self.print_final_report()

    def print_final_report(self):
        """Print final test report"""
        print("\n" + "=" * 80)
        print("🎯 RAPPORT FINAL - TESTS JAVASCRIPT GENERATION")
        print("=" * 80)
        
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        print(f"📊 Taux de réussite: {success_rate:.1f}%")
        
        if self.results["critical_issues"]:
            print(f"\n🚨 PROBLÈMES CRITIQUES IDENTIFIÉS ({len(self.results['critical_issues'])}):")
            for issue in self.results["critical_issues"]:
                print(f"   • {issue}")
        
        if self.results["errors"]:
            print(f"\n❌ ERREURS DÉTAILLÉES ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        # Recommendations
        print(f"\n💡 RECOMMANDATIONS:")
        if any("Mode avancé retourne du code vide" in issue for issue in self.results["critical_issues"]):
            print("   • CRITIQUE: Investiguer pourquoi le mode avancé retourne du code vide")
            print("   • Vérifier generate_with_multi_agents() dans multi_agent_orchestrator.py")
            print("   • Vérifier map_multi_agent_files_to_response() dans server.py")
            print("   • Analyser les logs backend pour les erreurs LLM")
        
        if success_rate < 80:
            print("   • Taux de réussite faible - investigation approfondie requise")
        
        print("\n🎯 FOCUS PRINCIPAL: Identifier EXACTEMENT pourquoi le mode avancé retourne du code vide")

if __name__ == "__main__":
    tester = JavaScriptGenerationTester()
    tester.run_all_tests()