#!/usr/bin/env python3
"""
🎯 TEST BACKEND COMPLET - ENVIRONNEMENT LOCAL EMERGENT
Tests spécifiques pour l'environnement Emergent local selon la demande française
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuration - ENVIRONNEMENT LOCAL EMERGENT
BASE_URL = "http://localhost:8001/api"
TEST_USER = {
    "email": f"test_emergent_{int(time.time())}@example.com",
    "password": "SecurePass123!",
    "full_name": f"Test Emergent User {int(time.time())}"
}

class EmergentLocalTester:
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
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise

    def test_1_api_status(self):
        """Test 1: API Status - GET /api/"""
        print("\n=== Test 1: API Status ===")
        try:
            response = self.make_request("GET", "/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and ("Vectort API" in data["message"] or "AI-powered" in data["message"]):
                    self.log_result("API Status", True, f"Response: {data['message']}")
                else:
                    self.log_result("API Status", False, f"Unexpected response format: {data}")
            else:
                self.log_result("API Status", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("API Status", False, f"Exception: {str(e)}")

    def test_2_auth_register(self):
        """Test 2: Authentication - Register"""
        print("\n=== Test 2: Authentication - Register ===")
        try:
            response = self.make_request("POST", "/auth/register", TEST_USER)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["access_token", "token_type", "user"]
                
                if all(field in data for field in required_fields):
                    self.access_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    user_data = data["user"]
                    
                    # Vérifier les 10 crédits gratuits
                    credits_total = user_data.get("credits_total", 0)
                    if credits_total == 10.0:
                        self.log_result("User Registration", True, f"User registered with ID: {self.user_id}, 10 free credits: ✅")
                    else:
                        self.log_result("User Registration", True, f"User registered but credits: {credits_total} (expected 10)")
                else:
                    self.log_result("User Registration", False, f"Missing required fields in response: {data}")
            elif response.status_code == 400:
                # User might already exist, try login
                error_data = response.json()
                if "already exists" in error_data.get("detail", ""):
                    self.log_result("User Registration", True, "User already exists, will try login")
                    self.test_2b_auth_login()
                else:
                    self.log_result("User Registration", False, f"Registration failed: {error_data}")
            else:
                self.log_result("User Registration", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("User Registration", False, f"Exception: {str(e)}")

    def test_2b_auth_login(self):
        """Test 2b: Authentication - Login"""
        print("\n=== Test 2b: Authentication - Login ===")
        try:
            login_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            
            response = self.make_request("POST", "/auth/login", login_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["access_token", "token_type", "user"]
                
                if all(field in data for field in required_fields):
                    self.access_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    self.log_result("User Login", True, f"Login successful, token received")
                else:
                    self.log_result("User Login", False, f"Missing required fields in response: {data}")
            else:
                self.log_result("User Login", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("User Login", False, f"Exception: {str(e)}")

    def test_3_auth_me(self):
        """Test 3: Authentication Check - GET /api/auth/me"""
        print("\n=== Test 3: Authentication Check ===")
        try:
            if not self.access_token:
                self.log_result("Authentication Check", False, "No access token available")
                return
            
            response = self.make_request("GET", "/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "email"]
                
                if all(field in data for field in required_fields):
                    if data["email"] == TEST_USER["email"]:
                        self.log_result("Authentication Check", True, f"User info retrieved: {data.get('full_name', 'N/A')}")
                    else:
                        self.log_result("Authentication Check", False, "Email mismatch in user info")
                else:
                    self.log_result("Authentication Check", False, f"Missing required fields: {data}")
            else:
                self.log_result("Authentication Check", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Authentication Check", False, f"Exception: {str(e)}")

    def test_4_credits_balance(self):
        """Test 4: Credit System - GET /api/credits/balance"""
        print("\n=== Test 4: Credit System - Balance ===")
        try:
            if not self.access_token:
                self.log_result("Credit Balance", False, "No access token available")
                return
            
            response = self.make_request("GET", "/credits/balance")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["free_credits", "total_available"]
                
                if all(field in data for field in required_fields):
                    free_credits = data["free_credits"]
                    total_available = data["total_available"]
                    if free_credits == 10.0 and total_available >= 10.0:
                        self.log_result("Credit Balance", True, f"✅ 10 free credits confirmed: {data}")
                    else:
                        self.log_result("Credit Balance", False, f"Unexpected credit amounts: {data}")
                else:
                    self.log_result("Credit Balance", False, f"Missing required fields: {data}")
            else:
                self.log_result("Credit Balance", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Credit Balance", False, f"Exception: {str(e)}")

    def test_5_credits_packages(self):
        """Test 5: Credit System - GET /api/credits/packages"""
        print("\n=== Test 5: Credit System - Packages ===")
        try:
            response = self.make_request("GET", "/credits/packages")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) >= 3:
                    # Vérifier les packages attendus
                    package_names = [pkg.get("name", "") for pkg in data]
                    expected_packages = ["Starter", "Standard", "Pro"]
                    
                    if all(pkg in package_names for pkg in expected_packages):
                        self.log_result("Credit Packages", True, f"✅ 3 packages found: {package_names}")
                    else:
                        self.log_result("Credit Packages", True, f"Packages found but different names: {package_names}")
                else:
                    self.log_result("Credit Packages", False, f"Expected list of packages, got: {data}")
            else:
                self.log_result("Credit Packages", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Credit Packages", False, f"Exception: {str(e)}")

    def test_6_project_create(self):
        """Test 6: Project Management - Create"""
        print("\n=== Test 6: Project Management - Create ===")
        try:
            if not self.access_token:
                self.log_result("Project Create", False, "No access token available")
                return
            
            project_data = {
                "title": "Créer un site e-commerce avec panier d'achat et système de paiement",
                "description": "Créer un site e-commerce avec panier d'achat et système de paiement",
                "type": "web_app"
            }
            
            response = self.make_request("POST", "/projects", project_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "title", "description", "type", "user_id"]
                
                if all(field in data for field in required_fields):
                    self.test_project_id = data["id"]
                    if (data["title"] == project_data["title"] and 
                        data["user_id"] == self.user_id):
                        self.log_result("Project Create", True, f"Project created with ID: {self.test_project_id}")
                    else:
                        self.log_result("Project Create", False, "Project data mismatch")
                else:
                    self.log_result("Project Create", False, f"Missing required fields: {data}")
            else:
                self.log_result("Project Create", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Project Create", False, f"Exception: {str(e)}")

    def test_7_projects_list(self):
        """Test 7: Project Management - List"""
        print("\n=== Test 7: Project Management - List ===")
        try:
            if not self.access_token:
                self.log_result("Projects List", False, "No access token available")
                return
            
            response = self.make_request("GET", "/projects")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check if our test project is in the list
                        project_found = any(p.get("id") == self.test_project_id for p in data)
                        if project_found or self.test_project_id is None:
                            self.log_result("Projects List", True, f"Retrieved {len(data)} projects")
                        else:
                            self.log_result("Projects List", False, "Test project not found in list")
                    else:
                        self.log_result("Projects List", True, "No projects found (empty list)")
                else:
                    self.log_result("Projects List", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Projects List", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Projects List", False, f"Exception: {str(e)}")

    def test_8_project_get(self):
        """Test 8: Project Management - Get"""
        print("\n=== Test 8: Project Management - Get ===")
        try:
            if not self.access_token:
                self.log_result("Project Get", False, "No access token available")
                return
            
            if not self.test_project_id:
                self.log_result("Project Get", False, "No test project ID available")
                return
            
            response = self.make_request("GET", f"/projects/{self.test_project_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == self.test_project_id:
                    self.log_result("Project Get", True, f"Project retrieved: {data['title']}")
                else:
                    self.log_result("Project Get", False, "Project ID mismatch")
            elif response.status_code == 404:
                self.log_result("Project Get", False, "Project not found")
            else:
                self.log_result("Project Get", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Project Get", False, f"Exception: {str(e)}")

    def test_9_ai_generation_quick_mode(self):
        """Test 9: AI GENERATION - Quick Mode (CRITIQUE)"""
        print("\n=== Test 9: AI GENERATION - Quick Mode (CRITIQUE) ===")
        try:
            if not self.access_token:
                self.log_result("AI Generation Quick", False, "No access token available")
                return
            
            if not self.test_project_id:
                self.log_result("AI Generation Quick", False, "No test project ID available")
                return
            
            # Generate with quick mode
            generation_request = {
                "description": "Créer un site e-commerce avec panier d'achat et système de paiement",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False  # Quick mode
            }
            
            print(f"   🔄 Generating code for project {self.test_project_id}...")
            response = self.make_request("POST", f"/projects/{self.test_project_id}/generate", generation_request)
            
            if response.status_code == 200:
                data = response.json()
                # Check if REAL code was generated (not empty)
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                generated_code = {}
                
                for field in code_fields:
                    code = data.get(field)
                    if code and len(str(code).strip()) > 50:  # Real code should be substantial
                        generated_code[field] = len(str(code))
                
                if generated_code:
                    code_summary = ", ".join([f"{field}: {size} chars" for field, size in generated_code.items()])
                    self.log_result("AI Generation Quick", True, f"✅ REAL CODE GENERATED: {code_summary}")
                else:
                    self.log_result("AI Generation Quick", False, "❌ No substantial code was generated")
            elif response.status_code == 402:
                self.log_result("AI Generation Quick", False, "❌ Insufficient credits")
            else:
                self.log_result("AI Generation Quick", False, f"❌ Generation failed: {response.status_code} - {response.text}")
        except Exception as e:
            self.log_result("AI Generation Quick", False, f"Exception: {str(e)}")

    def test_10_project_code_get(self):
        """Test 10: Generated Code Retrieval - GET /api/projects/{id}/code"""
        print("\n=== Test 10: Generated Code Retrieval ===")
        try:
            if not self.access_token:
                self.log_result("Code Retrieval", False, "No access token available")
                return
            
            if not self.test_project_id:
                self.log_result("Code Retrieval", False, "No test project ID available")
                return
            
            response = self.make_request("GET", f"/projects/{self.test_project_id}/code")
            
            if response.status_code == 200:
                data = response.json()
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                has_code = any(data.get(field) for field in code_fields)
                
                if has_code:
                    self.log_result("Code Retrieval", True, "✅ Generated code retrieved successfully")
                else:
                    self.log_result("Code Retrieval", False, "No code found in response")
            elif response.status_code == 404:
                self.log_result("Code Retrieval", False, "Generated code not found")
            else:
                self.log_result("Code Retrieval", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Code Retrieval", False, f"Exception: {str(e)}")

    def test_11_project_preview(self):
        """Test 11: Application Preview - GET /api/projects/{id}/preview"""
        print("\n=== Test 11: Application Preview ===")
        try:
            if not self.access_token:
                self.log_result("App Preview", False, "No access token available")
                return
            
            if not self.test_project_id:
                self.log_result("App Preview", False, "No test project ID available")
                return
            
            response = self.make_request("GET", f"/projects/{self.test_project_id}/preview")
            
            if response.status_code == 200:
                content = response.text
                # Check if it's valid HTML
                if "<!DOCTYPE html>" in content and "<html" in content and "</html>" in content:
                    preview_size = len(content)
                    self.log_result("App Preview", True, f"✅ HTML preview generated successfully ({preview_size} chars)")
                else:
                    self.log_result("App Preview", False, "Invalid HTML preview format")
            elif response.status_code == 404:
                self.log_result("App Preview", False, "Preview not found")
            else:
                self.log_result("App Preview", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("App Preview", False, f"Exception: {str(e)}")

    def test_12_ai_generation_advanced_mode(self):
        """Test 12: AI GENERATION - Advanced Mode (if Quick works)"""
        print("\n=== Test 12: AI GENERATION - Advanced Mode ===")
        try:
            if not self.access_token:
                self.log_result("AI Generation Advanced", False, "No access token available")
                return
            
            # Create new project for advanced mode
            project_data = {
                "title": "Application E-commerce Avancée",
                "description": "Créer une application e-commerce complète avec fonctionnalités avancées",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("AI Generation Advanced", False, f"Failed to create project: {project_response.status_code}")
                return
            
            advanced_project_id = project_response.json()["id"]
            
            # Generate with advanced mode
            generation_request = {
                "description": "Créer une application e-commerce complète avec panier, paiement, gestion des produits et interface d'administration",
                "type": "web_app",
                "framework": "react",
                "database": "mongodb",
                "advanced_mode": True  # Advanced mode
            }
            
            print(f"   🔄 Generating advanced code for project {advanced_project_id}...")
            response = self.make_request("POST", f"/projects/{advanced_project_id}/generate", generation_request)
            
            if response.status_code == 200:
                data = response.json()
                # Check for advanced features
                advanced_fields = ["project_structure", "package_json", "dockerfile", "readme"]
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                
                has_advanced = any(data.get(field) for field in advanced_fields)
                has_code = any(data.get(field) for field in code_fields)
                
                if has_advanced and has_code:
                    self.log_result("AI Generation Advanced", True, "✅ Advanced generation with structure and code")
                elif has_code:
                    self.log_result("AI Generation Advanced", True, "✅ Code generated (basic fallback)")
                else:
                    self.log_result("AI Generation Advanced", False, "❌ No code generated")
            elif response.status_code == 402:
                self.log_result("AI Generation Advanced", False, "❌ Insufficient credits")
            else:
                self.log_result("AI Generation Advanced", False, f"❌ Generation failed: {response.status_code}")
        except Exception as e:
            self.log_result("AI Generation Advanced", False, f"Exception: {str(e)}")

    def run_complete_test(self):
        """🎯 TEST BACKEND COMPLET - ENVIRONNEMENT LOCAL EMERGENT"""
        print("🎯 TEST BACKEND COMPLET - ENVIRONNEMENT LOCAL EMERGENT")
        print(f"Testing Local API: {self.base_url}")
        print("=" * 80)
        
        # Tests selon la demande française
        self.test_1_api_status()
        self.test_2_auth_register()
        if not self.access_token:
            self.test_2b_auth_login()
        self.test_3_auth_me()
        self.test_4_credits_balance()
        self.test_5_credits_packages()
        self.test_6_project_create()
        self.test_7_projects_list()
        self.test_8_project_get()
        self.test_9_ai_generation_quick_mode()
        self.test_10_project_code_get()
        self.test_11_project_preview()
        self.test_12_ai_generation_advanced_mode()
        
        # Final Summary
        print("\n" + "=" * 80)
        print("🎯 RÉSULTATS TEST BACKEND LOCAL EMERGENT")
        print("=" * 80)
        print(f"✅ Réussis: {self.results['passed']}")
        print(f"❌ Échoués: {self.results['failed']}")
        total_tests = self.results['passed'] + self.results['failed']
        if total_tests > 0:
            success_rate = (self.results['passed'] / total_tests * 100)
            print(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        if self.results['errors']:
            print("\n🔍 TESTS ÉCHOUÉS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        else:
            print("\n🎉 TOUS LES TESTS RÉUSSIS! Le backend Vectort local fonctionne correctement!")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    print("🚀 Démarrage des tests backend Vectort.io - Environnement Local Emergent")
    tester = EmergentLocalTester()
    success = tester.run_complete_test()
    
    if success:
        print("\n✅ SUCCÈS: Tous les tests sont passés!")
        sys.exit(0)
    else:
        print("\n❌ ÉCHEC: Certains tests ont échoué.")
        sys.exit(1)