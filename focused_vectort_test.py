#!/usr/bin/env python3
"""
🎯 FOCUSED TEST - VECTORT.IO MAPPING & GENERATION
Test ciblé sur le mapping intelligent des fichiers et la génération avancée
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://emergent-clone-151.preview.emergentagent.com/api"
TEST_USER = {
    "email": f"focused.test.{int(time.time())}@vectort.io",
    "password": "FocusedTest123!",
    "full_name": f"Focused Test {int(time.time() % 1000000)}"
}

class FocusedVectortTester:
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
                    headers: Optional[Dict] = None, timeout: int = 30) -> requests.Response:
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
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise

    def setup_auth(self):
        """Quick authentication setup"""
        try:
            response = self.make_request("POST", "/auth/register", TEST_USER, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                return True
            elif response.status_code == 400:
                # Try login
                login_response = self.make_request("POST", "/auth/login", {
                    "email": TEST_USER["email"],
                    "password": TEST_USER["password"]
                }, timeout=15)
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.access_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    return True
            return False
        except:
            return False

    def test_basic_generation_mapping(self):
        """Test basique de génération et mapping"""
        print("\n=== TEST BASIQUE GÉNÉRATION & MAPPING ===")
        
        if not self.access_token:
            self.log_result("Basic Generation Mapping", False, "No access token")
            return None
        
        try:
            # Créer projet simple
            project_data = {
                "title": "Test Mapping Basique",
                "description": "Application e-commerce simple pour tester le mapping",
                "type": "ecommerce"
            }
            
            project_response = self.make_request("POST", "/projects", project_data, timeout=15)
            if project_response.status_code != 200:
                self.log_result("Basic Generation - Project Creation", False, 
                              f"Failed: {project_response.status_code}")
                return None
            
            project_id = project_response.json()["id"]
            self.log_result("Basic Generation - Project Creation", True, f"Project: {project_id}")
            
            # Test génération basique d'abord
            basic_request = {
                "description": "Boutique en ligne avec panier et paiement",
                "type": "ecommerce",
                "framework": "react",
                "advanced_mode": False  # Mode basique d'abord
            }
            
            start_time = time.time()
            response = self.make_request("POST", f"/projects/{project_id}/generate", basic_request, timeout=25)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyser le mapping des fichiers
                html_code = data.get("html_code", "")
                css_code = data.get("css_code", "")
                js_code = data.get("js_code", "")
                react_code = data.get("react_code", "")
                backend_code = data.get("backend_code", "")
                
                # Compter les fichiers générés
                generated_files = []
                if html_code: generated_files.append(f"HTML({len(html_code)} chars)")
                if css_code: generated_files.append(f"CSS({len(css_code)} chars)")
                if js_code: generated_files.append(f"JS({len(js_code)} chars)")
                if react_code: generated_files.append(f"React({len(react_code)} chars)")
                if backend_code: generated_files.append(f"Backend({len(backend_code)} chars)")
                
                if len(generated_files) >= 3:  # Au moins 3 types de fichiers
                    self.log_result("Basic Generation - File Generation", True, 
                                  f"✅ {len(generated_files)} types générés: {', '.join(generated_files)}")
                else:
                    self.log_result("Basic Generation - File Generation", False, 
                                  f"❌ Seulement {len(generated_files)} types: {', '.join(generated_files)}")
                
                # Test performance
                if generation_time < 20:
                    self.log_result("Basic Generation - Performance", True, 
                                  f"✅ Rapide: {generation_time:.1f}s")
                else:
                    self.log_result("Basic Generation - Performance", False, 
                                  f"❌ Lent: {generation_time:.1f}s")
                
                return data
            else:
                self.log_result("Basic Generation - API Call", False, 
                              f"Failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_result("Basic Generation Mapping", False, f"Exception: {str(e)}")
            return None

    def test_advanced_mode_generation(self):
        """Test génération mode avancé"""
        print("\n=== TEST MODE AVANCÉ ===")
        
        if not self.access_token:
            self.log_result("Advanced Mode Generation", False, "No access token")
            return None
        
        try:
            # Créer projet pour mode avancé
            project_data = {
                "title": "Test Mode Avancé",
                "description": "Application e-commerce avancée",
                "type": "ecommerce"
            }
            
            project_response = self.make_request("POST", "/projects", project_data, timeout=15)
            if project_response.status_code != 200:
                self.log_result("Advanced Mode - Project Creation", False, 
                              f"Failed: {project_response.status_code}")
                return None
            
            project_id = project_response.json()["id"]
            
            # Test génération avancée
            advanced_request = {
                "description": "Boutique en ligne complète avec React, MongoDB, Stripe",
                "type": "ecommerce",
                "framework": "react",
                "database": "mongodb",
                "advanced_mode": True,  # MODE AVANCÉ
                "features": ["authentication", "payment_processing", "shopping_cart"],
                "integrations": ["stripe", "mongodb"]
            }
            
            start_time = time.time()
            response = self.make_request("POST", f"/projects/{project_id}/generate", advanced_request, timeout=25)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Vérifier les champs avancés
                advanced_fields = {
                    "project_structure": data.get("project_structure"),
                    "package_json": data.get("package_json"),
                    "dockerfile": data.get("dockerfile"),
                    "readme": data.get("readme"),
                    "all_files": data.get("all_files")
                }
                
                advanced_generated = [field for field, value in advanced_fields.items() if value]
                
                if len(advanced_generated) >= 2:
                    self.log_result("Advanced Mode - Advanced Fields", True, 
                                  f"✅ Champs avancés: {', '.join(advanced_generated)}")
                else:
                    self.log_result("Advanced Mode - Advanced Fields", False, 
                                  f"❌ Peu de champs avancés: {', '.join(advanced_generated)}")
                
                # Vérifier les fichiers de base
                basic_files = []
                if data.get("html_code"): basic_files.append("HTML")
                if data.get("css_code"): basic_files.append("CSS")
                if data.get("js_code"): basic_files.append("JS")
                if data.get("react_code"): basic_files.append("React")
                if data.get("backend_code"): basic_files.append("Backend")
                
                if len(basic_files) >= 3:
                    self.log_result("Advanced Mode - Basic Files", True, 
                                  f"✅ Fichiers de base: {', '.join(basic_files)}")
                else:
                    self.log_result("Advanced Mode - Basic Files", False, 
                                  f"❌ Fichiers manquants: {', '.join(basic_files)}")
                
                return data
            else:
                self.log_result("Advanced Mode Generation", False, 
                              f"Failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_result("Advanced Mode Generation", False, f"Exception: {str(e)}")
            return None

    def test_file_extension_mapping(self, generated_data):
        """Test mapping spécifique des extensions"""
        print("\n=== TEST MAPPING EXTENSIONS ===")
        
        if not generated_data:
            self.log_result("File Extension Mapping", False, "No data to test")
            return
        
        try:
            # Test .jsx → react_code
            react_code = generated_data.get("react_code", "")
            if react_code and ("jsx" in react_code.lower() or "react" in react_code.lower() or "component" in react_code.lower()):
                self.log_result("Mapping - JSX to React", True, "✅ JSX → react_code détecté")
            else:
                self.log_result("Mapping - JSX to React", False, "❌ JSX → react_code non détecté")
            
            # Test .css → css_code
            css_code = generated_data.get("css_code", "")
            if css_code and ("{" in css_code or "css" in css_code.lower() or "style" in css_code.lower()):
                self.log_result("Mapping - CSS", True, "✅ CSS → css_code détecté")
            else:
                self.log_result("Mapping - CSS", False, "❌ CSS → css_code non détecté")
            
            # Test .html → html_code
            html_code = generated_data.get("html_code", "")
            if html_code and ("html" in html_code.lower() or "<!doctype" in html_code.lower() or "<div" in html_code.lower()):
                self.log_result("Mapping - HTML", True, "✅ HTML → html_code détecté")
            else:
                self.log_result("Mapping - HTML", False, "❌ HTML → html_code non détecté")
            
            # Test .py → backend_code
            backend_code = generated_data.get("backend_code", "")
            if backend_code and ("python" in backend_code.lower() or "def " in backend_code or "import " in backend_code or "fastapi" in backend_code.lower()):
                self.log_result("Mapping - Python Backend", True, "✅ Python → backend_code détecté")
            else:
                self.log_result("Mapping - Python Backend", False, "❌ Python → backend_code non détecté")
            
            # Test fallback mechanism
            all_files = generated_data.get("all_files", {})
            if all_files and isinstance(all_files, dict) and len(all_files) > 0:
                self.log_result("Mapping - Fallback Mechanism", True, 
                              f"✅ Fallback avec {len(all_files)} fichiers")
            else:
                self.log_result("Mapping - Fallback Mechanism", False, "❌ Pas de fallback détecté")
                
        except Exception as e:
            self.log_result("File Extension Mapping", False, f"Exception: {str(e)}")

    def test_default_structures(self):
        """Test structures par défaut"""
        print("\n=== TEST STRUCTURES PAR DÉFAUT ===")
        
        if not self.access_token:
            self.log_result("Default Structures", False, "No access token")
            return
        
        try:
            # Test structure React par défaut
            react_project = {
                "title": "Test Structure React",
                "description": "App React simple",
                "type": "web_app"
            }
            
            react_response = self.make_request("POST", "/projects", react_project, timeout=15)
            if react_response.status_code == 200:
                react_id = react_response.json()["id"]
                
                react_gen = {
                    "description": "Application React avec composants de base",
                    "type": "web_app",
                    "framework": "react",
                    "advanced_mode": False
                }
                
                react_result = self.make_request("POST", f"/projects/{react_id}/generate", react_gen, timeout=20)
                
                if react_result.status_code == 200:
                    react_data = react_result.json()
                    react_files = [field for field in ["react_code", "html_code", "css_code"] if react_data.get(field)]
                    
                    if len(react_files) >= 2:
                        self.log_result("Default Structure - React", True, 
                                      f"✅ Structure React: {', '.join(react_files)}")
                    else:
                        self.log_result("Default Structure - React", False, 
                                      f"❌ Structure React incomplète: {', '.join(react_files)}")
                else:
                    self.log_result("Default Structure - React", False, "Génération échouée")
            
            # Test structure FastAPI par défaut
            api_project = {
                "title": "Test Structure API",
                "description": "API FastAPI simple",
                "type": "web_app"
            }
            
            api_response = self.make_request("POST", "/projects", api_project, timeout=15)
            if api_response.status_code == 200:
                api_id = api_response.json()["id"]
                
                api_gen = {
                    "description": "API REST avec FastAPI et endpoints de base",
                    "type": "web_app",
                    "framework": "fastapi",
                    "advanced_mode": False
                }
                
                api_result = self.make_request("POST", f"/projects/{api_id}/generate", api_gen, timeout=20)
                
                if api_result.status_code == 200:
                    api_data = api_result.json()
                    backend_code = api_data.get("backend_code", "")
                    
                    if backend_code and ("fastapi" in backend_code.lower() or "api" in backend_code.lower()):
                        self.log_result("Default Structure - FastAPI", True, 
                                      f"✅ Structure FastAPI détectée ({len(backend_code)} chars)")
                    else:
                        self.log_result("Default Structure - FastAPI", False, "❌ Structure FastAPI non détectée")
                else:
                    self.log_result("Default Structure - FastAPI", False, "Génération API échouée")
                    
        except Exception as e:
            self.log_result("Default Structures", False, f"Exception: {str(e)}")

    def run_focused_tests(self):
        """Run focused tests"""
        print("🎯 FOCUSED TEST - VECTORT.IO MAPPING & GENERATION")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Setup
        print("\n🔐 Authentication Setup")
        if not self.setup_auth():
            print("❌ Authentication failed, stopping tests")
            return False
        
        print(f"✅ Authenticated as: {self.user_id}")
        
        # Run focused tests
        print("\n🚀 Running Focused Tests")
        print("-" * 40)
        
        # 1. Test basique
        basic_data = self.test_basic_generation_mapping()
        
        # 2. Test avancé
        advanced_data = self.test_advanced_mode_generation()
        
        # 3. Test mapping avec les données disponibles
        test_data = advanced_data if advanced_data else basic_data
        self.test_file_extension_mapping(test_data)
        
        # 4. Test structures par défaut
        self.test_default_structures()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 RÉSULTATS FOCUSED TEST")
        print("=" * 60)
        print(f"✅ Réussis: {self.results['passed']}")
        print(f"❌ Échoués: {self.results['failed']}")
        
        if self.results['passed'] + self.results['failed'] > 0:
            success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100)
            print(f"📈 Taux: {success_rate:.1f}%")
        else:
            success_rate = 0
        
        if self.results['errors']:
            print("\n🔍 Erreurs:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        if success_rate >= 80:
            print("\n🎉 SUCCÈS: Mapping et génération fonctionnels!")
        elif success_rate >= 60:
            print("\n⚠️ PARTIEL: Fonctionnalité majoritaire")
        else:
            print("\n❌ ÉCHEC: Corrections nécessaires")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = FocusedVectortTester()
    success = tester.run_focused_tests()
    sys.exit(0 if success else 1)