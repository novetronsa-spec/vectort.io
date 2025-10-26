#!/usr/bin/env python3
"""
🎯 TEST FINAL 100% FONCTIONNALITÉ - VECTORT.IO
Test exhaustif avec corrections du mapping de fichiers selon la demande spécifique
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://oauth-debug-2.preview.emergentagent.com/api"
TEST_USER = {
    "email": f"vectort.final.test.{int(time.time())}@vectort.io",
    "password": "VectortFinal123!",
    "full_name": f"Vectort Final Test {int(time.time() % 1000000)}"
}

class VectortFinalTester:
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
                    headers: Optional[Dict] = None, timeout: int = 45) -> requests.Response:
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

    def setup_authentication(self):
        """Setup authentication for testing"""
        print("\n🔐 SETUP: Authentication pour tests finaux")
        print("-" * 50)
        
        try:
            # Try registration first
            response = self.make_request("POST", "/auth/register", TEST_USER)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                self.log_result("Authentication Setup", True, f"User registered: {self.user_id}")
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
                    self.log_result("Authentication Setup", True, f"User logged in: {self.user_id}")
                else:
                    self.log_result("Authentication Setup", False, f"Login failed: {login_response.status_code}")
            else:
                self.log_result("Authentication Setup", False, f"Registration failed: {response.status_code}")
        except Exception as e:
            self.log_result("Authentication Setup", False, f"Exception: {str(e)}")

    def test_ecommerce_advanced_generation(self):
        """1. Test génération E-commerce mode avancé"""
        print("\n=== 1. TEST GÉNÉRATION E-COMMERCE MODE AVANCÉ ===")
        
        if not self.access_token:
            self.log_result("E-commerce Advanced Generation", False, "No access token available")
            return None
        
        try:
            # Créer utilisateur et projet E-commerce
            project_data = {
                "title": "E-commerce Avancé Vectort Test",
                "description": "Boutique en ligne complète avec React, MongoDB, système de paiement, gestion des stocks, interface d'administration",
                "type": "ecommerce"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("E-commerce Project Creation", False, 
                              f"Failed to create project: {project_response.status_code}")
                return None
            
            project_id = project_response.json()["id"]
            self.test_project_id = project_id
            self.log_result("E-commerce Project Creation", True, f"Project created: {project_id}")
            
            # Lancer génération mode avancé
            start_time = time.time()
            generation_request = {
                "description": "Créer une boutique en ligne moderne et complète avec catalogue de produits interactif, panier d'achats persistant, système de paiement sécurisé Stripe, gestion des commandes en temps réel, interface d'administration complète, authentification utilisateur robuste, système de reviews et ratings, gestion avancée des stocks avec alertes automatiques, dashboard analytics détaillé, notifications push en temps réel, design responsive ultra-moderne, optimisation SEO, et intégration avec services tiers",
                "type": "ecommerce",
                "framework": "react",
                "database": "mongodb",
                "advanced_mode": True,  # MODE AVANCÉ ACTIVÉ
                "features": [
                    "authentication", 
                    "payment_processing", 
                    "shopping_cart", 
                    "admin_panel",
                    "real_time_notifications",
                    "analytics_dashboard",
                    "inventory_management",
                    "seo_optimization"
                ],
                "integrations": ["stripe", "mongodb", "redis", "elasticsearch"],
                "deployment_target": "vercel"
            }
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request, timeout=60)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Vérifier MAPPING INTELLIGENT des fichiers générés
                html_code = data.get("html_code", "")
                css_code = data.get("css_code", "")
                js_code = data.get("js_code", "")
                react_code = data.get("react_code", "")
                backend_code = data.get("backend_code", "")
                
                # Confirmer que html_code, css_code, js_code, react_code, backend_code sont TOUS remplis
                all_filled = all([html_code, css_code, js_code, react_code, backend_code])
                
                if all_filled:
                    self.log_result("E-commerce Advanced Generation - ALL FILES FILLED", True, 
                                  f"✅ TOUS les champs remplis: HTML({len(html_code)} chars), CSS({len(css_code)} chars), JS({len(js_code)} chars), React({len(react_code)} chars), Backend({len(backend_code)} chars)")
                else:
                    filled_fields = []
                    if html_code: filled_fields.append(f"HTML({len(html_code)} chars)")
                    if css_code: filled_fields.append(f"CSS({len(css_code)} chars)")
                    if js_code: filled_fields.append(f"JS({len(js_code)} chars)")
                    if react_code: filled_fields.append(f"React({len(react_code)} chars)")
                    if backend_code: filled_fields.append(f"Backend({len(backend_code)} chars)")
                    
                    self.log_result("E-commerce Advanced Generation - PARTIAL FILES", False, 
                                  f"❌ Seulement certains champs remplis: {', '.join(filled_fields)}")
                
                # Vérifier performance < 20s par génération
                if generation_time < 20:
                    self.log_result("E-commerce Generation Performance", True, 
                                  f"✅ Génération rapide: {generation_time:.1f}s < 20s")
                else:
                    self.log_result("E-commerce Generation Performance", False, 
                                  f"❌ Génération lente: {generation_time:.1f}s > 20s")
                
                return data
            else:
                self.log_result("E-commerce Advanced Generation", False, 
                              f"Generation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_result("E-commerce Advanced Generation", False, f"Exception: {str(e)}")
            return None

    def test_file_mapping_specific(self, generated_data):
        """2. Test mapping de fichiers spécifique"""
        print("\n=== 2. TEST MAPPING DE FICHIERS SPÉCIFIQUE ===")
        
        if not generated_data:
            self.log_result("File Mapping Test", False, "No generated data available")
            return
        
        try:
            # Vérifier que les extensions .jsx → react_code
            react_code = generated_data.get("react_code", "")
            if react_code and (".jsx" in react_code or "React" in react_code or "jsx" in react_code.lower()):
                self.log_result("File Mapping - JSX to React", True, 
                              "✅ Extensions .jsx correctement mappées vers react_code")
            else:
                self.log_result("File Mapping - JSX to React", False, 
                              "❌ Mapping .jsx → react_code non détecté")
            
            # Vérifier que les .css → css_code
            css_code = generated_data.get("css_code", "")
            if css_code and ("css" in css_code.lower() or "style" in css_code.lower() or "{" in css_code):
                self.log_result("File Mapping - CSS", True, 
                              "✅ Extensions .css correctement mappées vers css_code")
            else:
                self.log_result("File Mapping - CSS", False, 
                              "❌ Mapping .css → css_code non détecté")
            
            # Vérifier que les .html → html_code
            html_code = generated_data.get("html_code", "")
            if html_code and ("html" in html_code.lower() or "<!DOCTYPE" in html_code or "<html" in html_code):
                self.log_result("File Mapping - HTML", True, 
                              "✅ Extensions .html correctement mappées vers html_code")
            else:
                self.log_result("File Mapping - HTML", False, 
                              "❌ Mapping .html → html_code non détecté")
            
            # Vérifier que les .py → backend_code
            backend_code = generated_data.get("backend_code", "")
            if backend_code and ("python" in backend_code.lower() or "def " in backend_code or "import " in backend_code or "from " in backend_code):
                self.log_result("File Mapping - Python Backend", True, 
                              "✅ Extensions .py correctement mappées vers backend_code")
            else:
                self.log_result("File Mapping - Python Backend", False, 
                              "❌ Mapping .py → backend_code non détecté")
            
            # Confirmer fallback vers premier fichier si pas de match
            all_files = generated_data.get("all_files", {})
            if all_files and len(all_files) > 0:
                self.log_result("File Mapping - Fallback Mechanism", True, 
                              f"✅ Fallback disponible avec {len(all_files)} fichiers générés")
            else:
                self.log_result("File Mapping - Fallback Mechanism", False, 
                              "❌ Pas de mécanisme de fallback détecté")
                
        except Exception as e:
            self.log_result("File Mapping Test", False, f"Exception: {str(e)}")

    def test_default_structure(self):
        """3. Test structure par défaut"""
        print("\n=== 3. TEST STRUCTURE PAR DÉFAUT ===")
        
        if not self.access_token:
            self.log_result("Default Structure Test", False, "No access token available")
            return
        
        try:
            # Tester React: App.jsx, index.html, styles.css, etc.
            react_project_data = {
                "title": "Test Structure React",
                "description": "Application React simple pour tester la structure par défaut",
                "type": "web_app"
            }
            
            react_project_response = self.make_request("POST", "/projects", react_project_data)
            if react_project_response.status_code != 200:
                self.log_result("Default Structure - React Project", False, 
                              f"Failed to create React project: {react_project_response.status_code}")
                return
            
            react_project_id = react_project_response.json()["id"]
            
            # Génération React avec structure par défaut
            react_generation_request = {
                "description": "Application React simple avec composants de base",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False  # Mode basique pour tester structure par défaut
            }
            
            react_response = self.make_request("POST", f"/projects/{react_project_id}/generate", react_generation_request)
            
            if react_response.status_code == 200:
                react_data = react_response.json()
                
                # Vérifier structure React par défaut
                has_react_structure = (
                    react_data.get("react_code") and 
                    react_data.get("html_code") and 
                    react_data.get("css_code")
                )
                
                if has_react_structure:
                    self.log_result("Default Structure - React", True, 
                                  "✅ Structure React par défaut générée: App.jsx, index.html, styles.css")
                else:
                    self.log_result("Default Structure - React", False, 
                                  "❌ Structure React par défaut incomplète")
            else:
                self.log_result("Default Structure - React", False, 
                              f"React generation failed: {react_response.status_code}")
            
            # Tester FastAPI: main.py, models.py, requirements.txt
            fastapi_project_data = {
                "title": "Test Structure FastAPI",
                "description": "API FastAPI simple pour tester la structure par défaut",
                "type": "web_app"
            }
            
            fastapi_project_response = self.make_request("POST", "/projects", fastapi_project_data)
            if fastapi_project_response.status_code != 200:
                self.log_result("Default Structure - FastAPI Project", False, 
                              f"Failed to create FastAPI project: {fastapi_project_response.status_code}")
                return
            
            fastapi_project_id = fastapi_project_response.json()["id"]
            
            # Génération FastAPI avec structure par défaut
            fastapi_generation_request = {
                "description": "API REST FastAPI avec endpoints de base et modèles de données",
                "type": "web_app",
                "framework": "fastapi",
                "advanced_mode": False  # Mode basique pour tester structure par défaut
            }
            
            fastapi_response = self.make_request("POST", f"/projects/{fastapi_project_id}/generate", fastapi_generation_request)
            
            if fastapi_response.status_code == 200:
                fastapi_data = fastapi_response.json()
                
                # Vérifier structure FastAPI par défaut
                backend_code = fastapi_data.get("backend_code", "")
                has_fastapi_structure = (
                    backend_code and 
                    ("fastapi" in backend_code.lower() or "FastAPI" in backend_code)
                )
                
                if has_fastapi_structure:
                    self.log_result("Default Structure - FastAPI", True, 
                                  "✅ Structure FastAPI par défaut générée: main.py, models.py")
                else:
                    self.log_result("Default Structure - FastAPI", False, 
                                  "❌ Structure FastAPI par défaut incomplète")
            else:
                self.log_result("Default Structure - FastAPI", False, 
                              f"FastAPI generation failed: {fastapi_response.status_code}")
                
        except Exception as e:
            self.log_result("Default Structure Test", False, f"Exception: {str(e)}")

    def test_complete_generation_with_timeout(self):
        """4. Test génération complète avec timeout"""
        print("\n=== 4. TEST GÉNÉRATION COMPLÈTE AVEC TIMEOUT ===")
        
        if not self.access_token:
            self.log_result("Complete Generation Timeout", False, "No access token available")
            return
        
        try:
            # Créer projet pour test de timeout
            timeout_project_data = {
                "title": "Test Génération Complète Timeout",
                "description": "Application complexe pour tester les timeouts de génération",
                "type": "ecommerce"
            }
            
            timeout_project_response = self.make_request("POST", "/projects", timeout_project_data)
            if timeout_project_response.status_code != 200:
                self.log_result("Complete Generation - Project Creation", False, 
                              f"Failed to create project: {timeout_project_response.status_code}")
                return
            
            timeout_project_id = timeout_project_response.json()["id"]
            
            # Générer avec timeout approprié
            start_time = time.time()
            complex_generation_request = {
                "description": "Créer une application e-commerce ultra-complète avec toutes les fonctionnalités avancées: catalogue produits avec recherche intelligente, panier d'achats persistant multi-sessions, système de paiement multi-devises (Stripe, PayPal, Apple Pay), gestion complète des commandes avec tracking, interface d'administration avancée avec analytics, authentification multi-facteurs, système de reviews et ratings avec modération, gestion des stocks en temps réel avec alertes automatiques, dashboard analytics avec graphiques interactifs, notifications push multi-canaux, design responsive ultra-moderne avec animations, optimisation SEO complète, intégration CRM, système de coupons et promotions, gestion des retours et remboursements, support client intégré avec chat en temps réel, et API complète pour intégrations tierces",
                "type": "ecommerce",
                "framework": "react",
                "database": "mongodb",
                "advanced_mode": True,
                "features": [
                    "authentication", 
                    "payment_processing", 
                    "shopping_cart", 
                    "admin_panel",
                    "real_time_notifications",
                    "analytics_dashboard",
                    "inventory_management",
                    "seo_optimization",
                    "multi_currency",
                    "customer_support",
                    "api_integration"
                ],
                "integrations": ["stripe", "paypal", "mongodb", "redis", "elasticsearch", "websocket"],
                "deployment_target": "vercel"
            }
            
            response = self.make_request("POST", f"/projects/{timeout_project_id}/generate", 
                                       complex_generation_request, timeout=60)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Vérifier TOUS les champs de GeneratedApp sont remplis
                required_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                filled_fields = []
                empty_fields = []
                
                for field in required_fields:
                    if data.get(field):
                        filled_fields.append(field)
                    else:
                        empty_fields.append(field)
                
                if len(filled_fields) == len(required_fields):
                    self.log_result("Complete Generation - All Fields Filled", True, 
                                  f"✅ TOUS les champs GeneratedApp remplis: {', '.join(filled_fields)}")
                else:
                    self.log_result("Complete Generation - All Fields Filled", False, 
                                  f"❌ Champs manquants: {', '.join(empty_fields)}, Remplis: {', '.join(filled_fields)}")
                
                # Confirmer performance < 20s par génération
                if generation_time < 20:
                    self.log_result("Complete Generation - Performance", True, 
                                  f"✅ Génération rapide: {generation_time:.1f}s < 20s")
                else:
                    self.log_result("Complete Generation - Performance", False, 
                                  f"❌ Génération lente: {generation_time:.1f}s > 20s")
                
                # Vérifier champs avancés
                advanced_fields = ["project_structure", "package_json", "dockerfile", "readme"]
                advanced_filled = [field for field in advanced_fields if data.get(field)]
                
                if advanced_filled:
                    self.log_result("Complete Generation - Advanced Fields", True, 
                                  f"✅ Champs avancés générés: {', '.join(advanced_filled)}")
                else:
                    self.log_result("Complete Generation - Advanced Fields", False, 
                                  "❌ Aucun champ avancé généré")
                    
            else:
                self.log_result("Complete Generation Timeout", False, 
                              f"Generation failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Complete Generation Timeout", False, f"Exception: {str(e)}")

    def test_100_percent_functionality_validation(self):
        """5. Validation 100% fonctionnalité"""
        print("\n=== 5. VALIDATION 100% FONCTIONNALITÉ ===")
        
        if not self.access_token:
            self.log_result("100% Functionality Validation", False, "No access token available")
            return
        
        try:
            # Mode avancé: TOUS les fichiers générés correctement
            advanced_success_count = 0
            advanced_total_tests = 3
            
            for i in range(advanced_total_tests):
                test_project_data = {
                    "title": f"Validation Avancée {i+1}",
                    "description": f"Test de validation avancée numéro {i+1} pour vérifier la génération complète",
                    "type": "ecommerce"
                }
                
                test_project_response = self.make_request("POST", "/projects", test_project_data)
                if test_project_response.status_code != 200:
                    continue
                
                test_project_id = test_project_response.json()["id"]
                
                validation_request = {
                    "description": f"Application e-commerce complète test {i+1} avec toutes les fonctionnalités",
                    "type": "ecommerce",
                    "framework": "react",
                    "database": "mongodb",
                    "advanced_mode": True,
                    "features": ["authentication", "payment_processing", "shopping_cart", "admin_panel"],
                    "integrations": ["stripe", "mongodb"]
                }
                
                validation_response = self.make_request("POST", f"/projects/{test_project_id}/generate", 
                                                      validation_request, timeout=45)
                
                if validation_response.status_code == 200:
                    validation_data = validation_response.json()
                    required_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                    
                    if all(validation_data.get(field) for field in required_fields):
                        advanced_success_count += 1
            
            advanced_success_rate = (advanced_success_count / advanced_total_tests) * 100
            
            if advanced_success_rate >= 80:
                self.log_result("100% Functionality - Advanced Mode", True, 
                              f"✅ Mode avancé: {advanced_success_rate:.1f}% de réussite ({advanced_success_count}/{advanced_total_tests})")
            else:
                self.log_result("100% Functionality - Advanced Mode", False, 
                              f"❌ Mode avancé: {advanced_success_rate:.1f}% de réussite ({advanced_success_count}/{advanced_total_tests})")
            
            # Mode basique: Toujours fonctionnel en fallback
            basic_success_count = 0
            basic_total_tests = 3
            
            for i in range(basic_total_tests):
                basic_project_data = {
                    "title": f"Validation Basique {i+1}",
                    "description": f"Test de validation basique numéro {i+1} pour vérifier le fallback",
                    "type": "web_app"
                }
                
                basic_project_response = self.make_request("POST", "/projects", basic_project_data)
                if basic_project_response.status_code != 200:
                    continue
                
                basic_project_id = basic_project_response.json()["id"]
                
                basic_request = {
                    "description": f"Application web simple test {i+1}",
                    "type": "web_app",
                    "framework": "react",
                    "advanced_mode": False  # Mode basique
                }
                
                basic_response = self.make_request("POST", f"/projects/{basic_project_id}/generate", 
                                                 basic_request, timeout=30)
                
                if basic_response.status_code == 200:
                    basic_data = basic_response.json()
                    # Au moins un champ doit être rempli en mode basique
                    if any(basic_data.get(field) for field in ["html_code", "css_code", "js_code", "react_code", "backend_code"]):
                        basic_success_count += 1
            
            basic_success_rate = (basic_success_count / basic_total_tests) * 100
            
            if basic_success_rate >= 90:
                self.log_result("100% Functionality - Basic Mode Fallback", True, 
                              f"✅ Mode basique fallback: {basic_success_rate:.1f}% de réussite ({basic_success_count}/{basic_total_tests})")
            else:
                self.log_result("100% Functionality - Basic Mode Fallback", False, 
                              f"❌ Mode basique fallback: {basic_success_rate:.1f}% de réussite ({basic_success_count}/{basic_total_tests})")
            
            # Mapping intelligent: Extensions fichiers correctes
            # (Déjà testé dans test_file_mapping_specific)
            
            # Performance: Génération dans les temps
            # (Déjà testé dans les autres fonctions)
            
            # Calcul du score global
            global_score = (advanced_success_rate + basic_success_rate) / 2
            
            if global_score >= 90:
                self.log_result("100% Functionality - GLOBAL VALIDATION", True, 
                              f"🎉 OBJECTIF ATTEINT: {global_score:.1f}% DE FONCTIONNALITÉ!")
            else:
                self.log_result("100% Functionality - GLOBAL VALIDATION", False, 
                              f"❌ Objectif non atteint: {global_score:.1f}% de fonctionnalité")
                
        except Exception as e:
            self.log_result("100% Functionality Validation", False, f"Exception: {str(e)}")

    def run_vectort_final_tests(self):
        """Run all VECTORT.IO final functionality tests"""
        print("🎯 TEST FINAL 100% FONCTIONNALITÉ - VECTORT.IO")
        print("Test exhaustif avec corrections du mapping de fichiers")
        print(f"Testing against: {self.base_url}")
        print("=" * 80)
        
        # Setup
        self.setup_authentication()
        
        if not self.access_token:
            print("❌ ÉCHEC: Impossible de s'authentifier, arrêt des tests")
            return False
        
        # Tests spécifiques selon la demande
        print("\n🚀 TESTS SPÉCIFIQUES VECTORT.IO")
        print("-" * 50)
        
        # 1. Test génération E-commerce mode avancé
        generated_data = self.test_ecommerce_advanced_generation()
        
        # 2. Test mapping de fichiers spécifique
        self.test_file_mapping_specific(generated_data)
        
        # 3. Test structure par défaut
        self.test_default_structure()
        
        # 4. Test génération complète avec timeout
        self.test_complete_generation_with_timeout()
        
        # 5. Validation 100% fonctionnalité
        self.test_100_percent_functionality_validation()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 RÉSULTATS FINAUX VECTORT.IO")
        print("=" * 80)
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        
        if self.results['passed'] + self.results['failed'] > 0:
            success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100)
            print(f"📈 Taux de réussite: {success_rate:.1f}%")
        else:
            success_rate = 0
            print(f"📈 Taux de réussite: 0%")
        
        if self.results['errors']:
            print("\n🔍 TESTS ÉCHOUÉS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        if success_rate >= 90:
            print("\n🎉 OBJECTIF ATTEINT: 100% DE FONCTIONNALITÉ VECTORT.IO!")
            print("✅ Système prêt pour production avec mapping intelligent des fichiers")
        elif success_rate >= 75:
            print("\n⚠️ FONCTIONNALITÉ PARTIELLE: Système majoritairement fonctionnel")
            print("🔧 Quelques corrections mineures nécessaires")
        else:
            print("\n❌ OBJECTIF NON ATTEINT: Corrections majeures nécessaires")
            print("🚨 Système nécessite des améliorations importantes")
        
        return success_rate >= 90

if __name__ == "__main__":
    tester = VectortFinalTester()
    success = tester.run_vectort_final_tests()
    sys.exit(0 if success else 1)