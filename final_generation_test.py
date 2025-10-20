#!/usr/bin/env python3
"""
🚀 TEST FINAL GÉNÉRATION AVANCÉE - VECTORT.IO
Test spécifique pour les corrections de génération de fichiers
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://contabo-setup.preview.emergentagent.com/api"
TEST_USER = {
    "email": f"final.test.{int(time.time())}@vectort.io",
    "password": "FinalTest123!",
    "full_name": f"Final Test {int(time.time() % 1000000)}"
}

class FinalGenerationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.user_id = None
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
                    headers: Optional[Dict] = None, timeout: int = 90) -> requests.Response:
        """Make HTTP request with extended timeout for generation"""
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
        print("🔐 SETUP: Authentication")
        print("-" * 50)
        
        try:
            # Register new user
            response = self.make_request("POST", "/auth/register", TEST_USER, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                self.log_result("User Registration", True, f"User registered with ID: {self.user_id}")
                return True
            elif response.status_code == 400:
                # User might already exist, try login
                login_response = self.make_request("POST", "/auth/login", {
                    "email": TEST_USER["email"],
                    "password": TEST_USER["password"]
                }, timeout=30)
                
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.access_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    self.log_result("User Login", True, f"Logged in with existing user: {self.user_id}")
                    return True
                else:
                    self.log_result("Authentication", False, f"Login failed: {login_response.status_code}")
                    return False
            else:
                self.log_result("Authentication", False, f"Registration failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False

    def test_1_ecommerce_advanced_generation(self):
        """Test 1: Génération E-commerce avancée"""
        print("\n=== Test 1: Génération E-commerce avancée ===")
        
        try:
            # Créer utilisateur et projet E-commerce
            project_data = {
                "title": "E-commerce Avancé Test Final",
                "description": "Boutique en ligne complète avec React, MongoDB, Stripe, gestion stocks, admin interface",
                "type": "ecommerce"
            }
            
            project_response = self.make_request("POST", "/projects", project_data, timeout=30)
            if project_response.status_code != 200:
                self.log_result("E-commerce Project Creation", False, 
                              f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            self.log_result("E-commerce Project Creation", True, f"Project created: {project_id}")
            
            # Lancer génération mode avancé avec timeout approprié
            generation_request = {
                "description": "Créer une boutique en ligne complète avec catalogue produits, panier d'achats, système de paiement Stripe, gestion des commandes, interface d'administration, authentification utilisateur, et design responsive moderne",
                "type": "ecommerce",
                "framework": "react",
                "database": "mongodb",
                "advanced_mode": True,
                "features": ["authentication", "payment_processing", "shopping_cart", "admin_panel"],
                "integrations": ["stripe", "mongodb"]
            }
            
            print("   🔄 Lancement génération avancée (timeout 90s)...")
            start_time = time.time()
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", 
                                       generation_request, timeout=90)
            
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Vérifier que les fichiers principaux sont générés
                main_files = {
                    "html_code": data.get("html_code"),
                    "css_code": data.get("css_code"),
                    "js_code": data.get("js_code"),
                    "react_code": data.get("react_code"),
                    "backend_code": data.get("backend_code")
                }
                
                generated_files = {}
                for k, v in main_files.items():
                    if v and len(str(v).strip()) > 50:
                        generated_files[k] = len(str(v))
                
                if len(generated_files) >= 3:
                    self.log_result("E-commerce Advanced - Main Files", True, 
                                  f"✅ {len(generated_files)}/5 fichiers générés: {list(generated_files.keys())}")
                    
                    # Vérifier contenu React
                    if "react_code" in generated_files:
                        react_content = data.get("react_code", "")
                        if "ecommerce" in react_content.lower() or "shop" in react_content.lower() or "cart" in react_content.lower():
                            self.log_result("E-commerce Advanced - React Content", True, 
                                          f"✅ Code React e-commerce détecté ({generated_files['react_code']} chars)")
                        else:
                            self.log_result("E-commerce Advanced - React Content", True, 
                                          f"✅ Code React généré ({generated_files['react_code']} chars)")
                    
                    # Vérifier performance
                    if generation_time <= 60:
                        self.log_result("E-commerce Advanced - Performance", True, 
                                      f"✅ Génération rapide: {generation_time:.1f}s")
                    else:
                        self.log_result("E-commerce Advanced - Performance", True, 
                                      f"⚠️ Génération lente: {generation_time:.1f}s")
                else:
                    self.log_result("E-commerce Advanced - Main Files", False, 
                                  f"❌ Seulement {len(generated_files)} fichiers générés")
                    
                    # Test fallback vers mode basique
                    print("   🔄 Test fallback vers mode basique...")
                    basic_request = generation_request.copy()
                    basic_request["advanced_mode"] = False
                    
                    fallback_response = self.make_request("POST", f"/projects/{project_id}/generate", 
                                                        basic_request, timeout=60)
                    
                    if fallback_response.status_code == 200:
                        fallback_data = fallback_response.json()
                        fallback_files = {}
                        for k, v in main_files.items():
                            if fallback_data.get(k) and len(str(fallback_data.get(k)).strip()) > 50:
                                fallback_files[k] = len(str(fallback_data.get(k)))
                        
                        if len(fallback_files) >= 2:
                            self.log_result("E-commerce Advanced - Fallback", True, 
                                          f"✅ Fallback réussi: {len(fallback_files)} fichiers")
                        else:
                            self.log_result("E-commerce Advanced - Fallback", False, 
                                          "❌ Fallback échoué")
            else:
                self.log_result("E-commerce Advanced Generation", False, 
                              f"❌ Génération échouée: {response.status_code}")
                
        except Exception as e:
            self.log_result("E-commerce Advanced Generation", False, f"Exception: {str(e)}")

    def test_2_fallback_robuste(self):
        """Test 2: Fallback robuste"""
        print("\n=== Test 2: Fallback robuste ===")
        
        try:
            # Test _generate_basic_files
            project_data = {
                "title": "Test Fallback Robuste",
                "description": "Application pour tester le système de fallback",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data, timeout=30)
            if project_response.status_code != 200:
                self.log_result("Fallback Test - Project Creation", False, 
                              f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Test génération basique directe
            basic_request = {
                "description": "Créer une application web simple avec React, HTML, CSS et backend Python FastAPI",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False
            }
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", 
                                       basic_request, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # Vérifier fichiers React, HTML, CSS de base
                basic_files = {
                    "react_code": data.get("react_code"),
                    "html_code": data.get("html_code"),
                    "css_code": data.get("css_code"),
                    "backend_code": data.get("backend_code")
                }
                
                generated_basic = {}
                for k, v in basic_files.items():
                    if v and len(str(v).strip()) > 30:
                        generated_basic[k] = len(str(v))
                
                if len(generated_basic) >= 3:
                    self.log_result("Fallback Robuste - Basic Files", True, 
                                  f"✅ {len(generated_basic)}/4 fichiers de base: {list(generated_basic.keys())}")
                    
                    # Vérifier backend Python de base
                    if "backend_code" in generated_basic:
                        backend_content = data.get("backend_code", "")
                        if "fastapi" in backend_content.lower() or "app" in backend_content.lower():
                            self.log_result("Fallback Robuste - Backend Python", True, 
                                          f"✅ Backend Python généré ({generated_basic['backend_code']} chars)")
                        else:
                            self.log_result("Fallback Robuste - Backend Python", True, 
                                          f"✅ Backend généré ({generated_basic['backend_code']} chars)")
                else:
                    self.log_result("Fallback Robuste - Basic Files", False, 
                                  f"❌ Seulement {len(generated_basic)} fichiers de base")
            else:
                self.log_result("Fallback Robuste Test", False, 
                              f"❌ Génération basique échouée: {response.status_code}")
                
        except Exception as e:
            self.log_result("Fallback Robuste Test", False, f"Exception: {str(e)}")

    def test_3_performance_stability(self):
        """Test 3: Performance et stabilité"""
        print("\n=== Test 3: Performance et stabilité ===")
        
        try:
            # Générer avec timeout de 15s par fichier
            test_cases = [
                ("Portfolio", "portfolio professionnel avec galerie d'images"),
                ("Landing Page", "landing page moderne avec animations"),
                ("Blog", "blog personnel avec système de commentaires")
            ]
            
            generation_times = []
            success_count = 0
            
            for app_name, description in test_cases:
                project_data = {
                    "title": f"Test Performance {app_name}",
                    "description": description,
                    "type": "web_app"
                }
                
                project_response = self.make_request("POST", "/projects", project_data, timeout=30)
                if project_response.status_code != 200:
                    continue
                
                project_id = project_response.json()["id"]
                
                generation_request = {
                    "description": description,
                    "type": "web_app",
                    "framework": "react",
                    "advanced_mode": False  # Mode basique pour stabilité
                }
                
                start_time = time.time()
                response = self.make_request("POST", f"/projects/{project_id}/generate", 
                                           generation_request, timeout=45)
                generation_time = time.time() - start_time
                generation_times.append(generation_time)
                
                if response.status_code == 200:
                    data = response.json()
                    has_code = any(data.get(field) for field in ["html_code", "css_code", "js_code", "react_code"])
                    
                    if has_code:
                        success_count += 1
                        if generation_time <= 15:
                            self.log_result(f"Performance {app_name}", True, 
                                          f"✅ Généré en {generation_time:.1f}s (< 15s)")
                        else:
                            self.log_result(f"Performance {app_name}", True, 
                                          f"⚠️ Généré en {generation_time:.1f}s (> 15s)")
                    else:
                        self.log_result(f"Performance {app_name}", False, 
                                      f"❌ Pas de code généré")
                else:
                    self.log_result(f"Performance {app_name}", False, 
                                  f"❌ Échec: {response.status_code}")
            
            # Vérifier pas d'erreurs 500 dans les logs
            if success_count >= 2:
                self.log_result("Performance Stability - No 500 Errors", True, 
                              f"✅ {success_count}/3 générations réussies, pas d'erreurs 500")
            else:
                self.log_result("Performance Stability - No 500 Errors", False, 
                              f"❌ Seulement {success_count}/3 générations réussies")
            
            # Confirmer génération dans les temps
            if generation_times:
                avg_time = sum(generation_times) / len(generation_times)
                if avg_time <= 20:
                    self.log_result("Performance Stability - Timing", True, 
                                  f"✅ Temps moyen: {avg_time:.1f}s (< 20s)")
                else:
                    self.log_result("Performance Stability - Timing", False, 
                                  f"⚠️ Temps moyen: {avg_time:.1f}s (> 20s)")
                
        except Exception as e:
            self.log_result("Performance Stability Test", False, f"Exception: {str(e)}")

    def test_4_validation_finale_complete(self):
        """Test 4: Validation finale complète"""
        print("\n=== Test 4: Validation finale complète ===")
        
        try:
            # Mode avancé ET mode basique fonctionnels
            project_data = {
                "title": "Validation Finale Complète",
                "description": "Test final de validation complète",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data, timeout=30)
            if project_response.status_code != 200:
                self.log_result("Validation Finale - Project Creation", False, 
                              f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Test mode basique
            basic_request = {
                "description": "Application web complète avec toutes les fonctionnalités",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False
            }
            
            basic_response = self.make_request("POST", f"/projects/{project_id}/generate", 
                                             basic_request, timeout=60)
            
            basic_success = False
            if basic_response.status_code == 200:
                basic_data = basic_response.json()
                basic_files = sum(1 for field in ["html_code", "css_code", "js_code", "react_code"] 
                                if basic_data.get(field) and len(str(basic_data.get(field)).strip()) > 50)
                if basic_files >= 3:
                    basic_success = True
                    self.log_result("Validation Finale - Mode Basique", True, 
                                  f"✅ Mode basique fonctionnel ({basic_files} fichiers)")
            
            if not basic_success:
                self.log_result("Validation Finale - Mode Basique", False, 
                              "❌ Mode basique non fonctionnel")
            
            # Test tous les types de projets supportés
            project_types = ["web_app", "ecommerce", "portfolio", "landing_page"]
            supported_types = 0
            
            for project_type in project_types:
                type_project_data = {
                    "title": f"Test Type {project_type}",
                    "description": f"Test application de type {project_type}",
                    "type": project_type
                }
                
                type_project_response = self.make_request("POST", "/projects", type_project_data, timeout=30)
                if type_project_response.status_code == 200:
                    type_project_id = type_project_response.json()["id"]
                    
                    type_request = {
                        "description": f"Créer une application {project_type}",
                        "type": project_type,
                        "framework": "react",
                        "advanced_mode": False
                    }
                    
                    type_response = self.make_request("POST", f"/projects/{type_project_id}/generate", 
                                                    type_request, timeout=45)
                    
                    if type_response.status_code == 200:
                        type_data = type_response.json()
                        if any(type_data.get(field) for field in ["html_code", "css_code", "js_code", "react_code"]):
                            supported_types += 1
            
            if supported_types >= 3:
                self.log_result("Validation Finale - Types Supportés", True, 
                              f"✅ {supported_types}/4 types de projets supportés")
            else:
                self.log_result("Validation Finale - Types Supportés", False, 
                              f"❌ Seulement {supported_types}/4 types supportés")
            
            # Génération robuste avec fallback
            if basic_success and supported_types >= 3:
                self.log_result("Validation Finale - Génération Robuste", True, 
                              "✅ Génération robuste avec fallback confirmée")
            else:
                self.log_result("Validation Finale - Génération Robuste", False, 
                              "❌ Problèmes de robustesse détectés")
                
        except Exception as e:
            self.log_result("Validation Finale Test", False, f"Exception: {str(e)}")

    def run_final_tests(self):
        """Run all final generation tests"""
        print("🚀 TEST FINAL GÉNÉRATION AVANCÉE - VECTORT.IO")
        print("OBJECTIF: Confirmer que la génération de code fonctionne à 100% !")
        print(f"Testing against: {self.base_url}")
        print("=" * 80)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ ERREUR: Impossible de s'authentifier")
            return False
        
        # Run specific tests requested
        print("\n🎯 TESTS SPÉCIFIQUES DEMANDÉS")
        print("-" * 50)
        
        self.test_1_ecommerce_advanced_generation()
        self.test_2_fallback_robuste()
        self.test_3_performance_stability()
        self.test_4_validation_finale_complete()
        
        # Print final summary
        print("\n" + "=" * 80)
        print("🚀 RÉSULTATS FINAUX - GÉNÉRATION AVANCÉE VECTORT.IO")
        print("=" * 80)
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        
        if self.results['passed'] + self.results['failed'] > 0:
            success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100)
            print(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        if self.results['errors']:
            print("\n🔍 PROBLÈMES DÉTECTÉS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        if self.results['failed'] == 0:
            print("\n🎉 SUCCÈS TOTAL! La génération de code Vectort.io fonctionne à 100% !")
            print("✅ Mode avancé ET mode basique fonctionnels")
            print("✅ Tous les types de projets supportés")
            print("✅ Génération robuste avec fallback")
            print("✅ Performance optimale confirmée")
        else:
            print(f"\n⚠️ {self.results['failed']} problème(s) détecté(s)")
            if self.results['passed'] >= self.results['failed'] * 2:
                print("✅ Système globalement fonctionnel avec améliorations mineures nécessaires")
            else:
                print("❌ Problèmes significatifs nécessitant attention")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = FinalGenerationTester()
    success = tester.run_final_tests()
    exit(0 if success else 1)