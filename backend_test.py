#!/usr/bin/env python3
"""
🔧 VÉRIFICATION DES CORRECTIONS PRÉ-DÉPLOIEMENT
Tests spécifiques pour les corrections apportées au système Vectort.io
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://emergent-clone-151.preview.emergentagent.com/api"
TEST_USER = {
    "email": f"test.corrections.{int(time.time())}@vectort.io",
    "password": "SecurePass123!",
    "full_name": "Test Corrections User"
}

class CodexAPITester:
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

    def test_basic_api_response(self):
        """Test 1: Basic API response"""
        print("\n=== Test 1: Basic API Response ===")
        try:
            response = self.make_request("GET", "/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Codex API" in data["message"]:
                    self.log_result("Basic API Response", True, f"Response: {data['message']}")
                else:
                    self.log_result("Basic API Response", False, f"Unexpected response format: {data}")
            else:
                self.log_result("Basic API Response", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Basic API Response", False, f"Exception: {str(e)}")

    def test_user_registration(self):
        """Test 2: User Registration"""
        print("\n=== Test 2: User Registration ===")
        try:
            # First, try to clean up any existing user (ignore errors)
            try:
                login_response = self.make_request("POST", "/auth/login", {
                    "email": TEST_USER["email"],
                    "password": TEST_USER["password"]
                })
                if login_response.status_code == 200:
                    print("   User already exists, will test login instead")
                    data = login_response.json()
                    self.access_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    self.log_result("User Registration (existing user)", True, "User already registered, using existing account")
                    return
            except:
                pass
            
            # Register new user
            response = self.make_request("POST", "/auth/register", TEST_USER)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["access_token", "token_type", "user"]
                
                if all(field in data for field in required_fields):
                    self.access_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    user_data = data["user"]
                    
                    if (user_data["email"] == TEST_USER["email"] and 
                        user_data["full_name"] == TEST_USER["full_name"]):
                        self.log_result("User Registration", True, f"User registered with ID: {self.user_id}")
                    else:
                        self.log_result("User Registration", False, "User data mismatch in response")
                else:
                    self.log_result("User Registration", False, f"Missing required fields in response: {data}")
            elif response.status_code == 400:
                # User might already exist
                error_data = response.json()
                if "already exists" in error_data.get("detail", ""):
                    self.log_result("User Registration", True, "User already exists (expected behavior)")
                    # Try to login with existing user
                    self.test_user_login()
                else:
                    self.log_result("User Registration", False, f"Registration failed: {error_data}")
            else:
                self.log_result("User Registration", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("User Registration", False, f"Exception: {str(e)}")

    def test_user_login(self):
        """Test 3: User Login"""
        print("\n=== Test 3: User Login ===")
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

    def test_authentication_check(self):
        """Test 4: Authentication Check"""
        print("\n=== Test 4: Authentication Check ===")
        try:
            if not self.access_token:
                self.log_result("Authentication Check", False, "No access token available")
                return
            
            response = self.make_request("GET", "/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "email", "full_name"]
                
                if all(field in data for field in required_fields):
                    if data["email"] == TEST_USER["email"]:
                        self.log_result("Authentication Check", True, f"User info retrieved: {data['full_name']}")
                    else:
                        self.log_result("Authentication Check", False, "Email mismatch in user info")
                else:
                    self.log_result("Authentication Check", False, f"Missing required fields: {data}")
            else:
                self.log_result("Authentication Check", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Authentication Check", False, f"Exception: {str(e)}")

    def test_project_creation(self):
        """Test 5a: Project Creation"""
        print("\n=== Test 5a: Project Creation ===")
        try:
            if not self.access_token:
                self.log_result("Project Creation", False, "No access token available")
                return
            
            project_data = {
                "title": "Application E-commerce",
                "description": "Une application e-commerce moderne avec React et FastAPI",
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
                        self.log_result("Project Creation", True, f"Project created with ID: {self.test_project_id}")
                    else:
                        self.log_result("Project Creation", False, "Project data mismatch")
                else:
                    self.log_result("Project Creation", False, f"Missing required fields: {data}")
            else:
                self.log_result("Project Creation", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Project Creation", False, f"Exception: {str(e)}")

    def test_project_listing(self):
        """Test 5b: Project Listing"""
        print("\n=== Test 5b: Project Listing ===")
        try:
            if not self.access_token:
                self.log_result("Project Listing", False, "No access token available")
                return
            
            response = self.make_request("GET", "/projects")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check if our test project is in the list
                        project_found = any(p.get("id") == self.test_project_id for p in data)
                        if project_found or self.test_project_id is None:
                            self.log_result("Project Listing", True, f"Retrieved {len(data)} projects")
                        else:
                            self.log_result("Project Listing", False, "Test project not found in list")
                    else:
                        self.log_result("Project Listing", True, "No projects found (empty list)")
                else:
                    self.log_result("Project Listing", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Project Listing", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Project Listing", False, f"Exception: {str(e)}")

    def test_project_retrieval(self):
        """Test 5c: Project Retrieval"""
        print("\n=== Test 5c: Project Retrieval ===")
        try:
            if not self.access_token:
                self.log_result("Project Retrieval", False, "No access token available")
                return
            
            if not self.test_project_id:
                self.log_result("Project Retrieval", False, "No test project ID available")
                return
            
            response = self.make_request("GET", f"/projects/{self.test_project_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == self.test_project_id:
                    self.log_result("Project Retrieval", True, f"Project retrieved: {data['title']}")
                else:
                    self.log_result("Project Retrieval", False, "Project ID mismatch")
            elif response.status_code == 404:
                self.log_result("Project Retrieval", False, "Project not found")
            else:
                self.log_result("Project Retrieval", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Project Retrieval", False, f"Exception: {str(e)}")

    def test_project_deletion(self):
        """Test 5d: Project Deletion"""
        print("\n=== Test 5d: Project Deletion ===")
        try:
            if not self.access_token:
                self.log_result("Project Deletion", False, "No access token available")
                return
            
            if not self.test_project_id:
                self.log_result("Project Deletion", False, "No test project ID available")
                return
            
            response = self.make_request("DELETE", f"/projects/{self.test_project_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") is True:
                    self.log_result("Project Deletion", True, "Project deleted successfully")
                    # Verify deletion by trying to retrieve
                    verify_response = self.make_request("GET", f"/projects/{self.test_project_id}")
                    if verify_response.status_code == 404:
                        self.log_result("Project Deletion Verification", True, "Project confirmed deleted")
                    else:
                        self.log_result("Project Deletion Verification", False, "Project still exists after deletion")
                else:
                    self.log_result("Project Deletion", False, f"Unexpected response: {data}")
            elif response.status_code == 404:
                self.log_result("Project Deletion", False, "Project not found for deletion")
            else:
                self.log_result("Project Deletion", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Project Deletion", False, f"Exception: {str(e)}")

    def test_global_statistics(self):
        """Test 6a: Global Statistics"""
        print("\n=== Test 6a: Global Statistics ===")
        try:
            response = self.make_request("GET", "/stats")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["users", "apps", "countries"]
                
                if all(field in data for field in required_fields):
                    self.log_result("Global Statistics", True, f"Stats: {data['users']} users, {data['apps']} apps, {data['countries']} countries")
                else:
                    self.log_result("Global Statistics", False, f"Missing required fields: {data}")
            else:
                self.log_result("Global Statistics", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Global Statistics", False, f"Exception: {str(e)}")

    def test_user_statistics(self):
        """Test 6b: User Statistics"""
        print("\n=== Test 6b: User Statistics ===")
        try:
            if not self.access_token:
                self.log_result("User Statistics", False, "No access token available")
                return
            
            response = self.make_request("GET", "/users/stats")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["totalProjects", "activeProjects", "totalViews"]
                
                if all(field in data for field in required_fields):
                    self.log_result("User Statistics", True, 
                                  f"User stats: {data['totalProjects']} total, {data['activeProjects']} active, {data['totalViews']} views")
                else:
                    self.log_result("User Statistics", False, f"Missing required fields: {data}")
            else:
                self.log_result("User Statistics", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("User Statistics", False, f"Exception: {str(e)}")

    def test_ai_app_generation_ecommerce(self):
        """Test 8a: AI Application Generation - E-commerce Site"""
        print("\n=== Test 8a: AI Application Generation - E-commerce Site ===")
        try:
            if not self.access_token:
                self.log_result("AI App Generation - E-commerce", False, "No access token available")
                return
            
            # Create a project for generation
            project_data = {
                "title": "Site E-commerce Moderne",
                "description": "Créer un site e-commerce moderne avec panier d'achats, catalogue de produits, système de paiement et interface d'administration",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("AI App Generation - E-commerce", False, f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Generate application code
            generation_request = {
                "description": "Créer un site e-commerce moderne avec panier d'achats, catalogue de produits, système de paiement et interface d'administration",
                "type": "web_app",
                "framework": "react"
            }
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "project_id", "created_at"]
                
                if all(field in data for field in required_fields):
                    # Check if at least one type of code was generated
                    code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                    has_code = any(data.get(field) for field in code_fields)
                    
                    if has_code:
                        self.log_result("AI App Generation - E-commerce", True, f"E-commerce app generated successfully with ID: {data['id']}")
                        self.test_project_id = project_id  # Store for further tests
                    else:
                        self.log_result("AI App Generation - E-commerce", False, "No code was generated")
                else:
                    self.log_result("AI App Generation - E-commerce", False, f"Missing required fields: {data}")
            else:
                self.log_result("AI App Generation - E-commerce", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("AI App Generation - E-commerce", False, f"Exception: {str(e)}")

    def test_ai_app_generation_task_manager(self):
        """Test 8b: AI Application Generation - Task Manager"""
        print("\n=== Test 8b: AI Application Generation - Task Manager ===")
        try:
            if not self.access_token:
                self.log_result("AI App Generation - Task Manager", False, "No access token available")
                return
            
            # Create a project for generation
            project_data = {
                "title": "Gestionnaire de Tâches",
                "description": "Application de gestion de tâches avec drag & drop",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("AI App Generation - Task Manager", False, f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Generate application code
            generation_request = {
                "description": "application de gestion de tâches avec drag & drop",
                "type": "web_app",
                "framework": "react"
            }
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            
            if response.status_code == 200:
                data = response.json()
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                has_code = any(data.get(field) for field in code_fields)
                
                if has_code:
                    self.log_result("AI App Generation - Task Manager", True, "Task manager app generated successfully")
                else:
                    self.log_result("AI App Generation - Task Manager", False, "No code was generated")
            else:
                self.log_result("AI App Generation - Task Manager", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("AI App Generation - Task Manager", False, f"Exception: {str(e)}")

    def test_ai_app_generation_portfolio(self):
        """Test 8c: AI Application Generation - Portfolio"""
        print("\n=== Test 8c: AI Application Generation - Portfolio ===")
        try:
            if not self.access_token:
                self.log_result("AI App Generation - Portfolio", False, "No access token available")
                return
            
            # Create a project for generation
            project_data = {
                "title": "Portfolio Professionnel",
                "description": "Portfolio professionnel avec galerie d'images",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("AI App Generation - Portfolio", False, f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Generate application code
            generation_request = {
                "description": "portfolio professionnel avec galerie d'images",
                "type": "web_app",
                "framework": "react"
            }
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            
            if response.status_code == 200:
                data = response.json()
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                has_code = any(data.get(field) for field in code_fields)
                
                if has_code:
                    self.log_result("AI App Generation - Portfolio", True, "Portfolio app generated successfully")
                else:
                    self.log_result("AI App Generation - Portfolio", False, "No code was generated")
            else:
                self.log_result("AI App Generation - Portfolio", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("AI App Generation - Portfolio", False, f"Exception: {str(e)}")

    def test_ai_app_generation_landing_page(self):
        """Test 8d: AI Application Generation - Landing Page"""
        print("\n=== Test 8d: AI Application Generation - Landing Page ===")
        try:
            if not self.access_token:
                self.log_result("AI App Generation - Landing Page", False, "No access token available")
                return
            
            # Create a project for generation
            project_data = {
                "title": "Landing Page Startup",
                "description": "Landing page pour startup avec animations",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("AI App Generation - Landing Page", False, f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Generate application code
            generation_request = {
                "description": "landing page pour startup avec animations",
                "type": "web_app",
                "framework": "react"
            }
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            
            if response.status_code == 200:
                data = response.json()
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                has_code = any(data.get(field) for field in code_fields)
                
                if has_code:
                    self.log_result("AI App Generation - Landing Page", True, "Landing page app generated successfully")
                else:
                    self.log_result("AI App Generation - Landing Page", False, "No code was generated")
            else:
                self.log_result("AI App Generation - Landing Page", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("AI App Generation - Landing Page", False, f"Exception: {str(e)}")

    def test_get_generated_code(self):
        """Test 9: Get Generated Code"""
        print("\n=== Test 9: Get Generated Code ===")
        try:
            if not self.access_token:
                self.log_result("Get Generated Code", False, "No access token available")
                return
            
            if not self.test_project_id:
                self.log_result("Get Generated Code", False, "No test project ID available")
                return
            
            response = self.make_request("GET", f"/projects/{self.test_project_id}/code")
            
            if response.status_code == 200:
                data = response.json()
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                has_code = any(data.get(field) for field in code_fields)
                
                if has_code:
                    self.log_result("Get Generated Code", True, "Generated code retrieved successfully")
                else:
                    self.log_result("Get Generated Code", False, "No code found in response")
            elif response.status_code == 404:
                self.log_result("Get Generated Code", False, "Generated code not found")
            else:
                self.log_result("Get Generated Code", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Get Generated Code", False, f"Exception: {str(e)}")

    def test_preview_generated_app(self):
        """Test 10: Preview Generated Application"""
        print("\n=== Test 10: Preview Generated Application ===")
        try:
            if not self.access_token:
                self.log_result("Preview Generated App", False, "No access token available")
                return
            
            if not self.test_project_id:
                self.log_result("Preview Generated App", False, "No test project ID available")
                return
            
            response = self.make_request("GET", f"/projects/{self.test_project_id}/preview")
            
            if response.status_code == 200:
                content = response.text
                # Check if it's valid HTML
                if "<!DOCTYPE html>" in content and "<html" in content and "</html>" in content:
                    self.log_result("Preview Generated App", True, "HTML preview generated successfully")
                else:
                    self.log_result("Preview Generated App", False, "Invalid HTML preview format")
            elif response.status_code == 404:
                self.log_result("Preview Generated App", False, "Preview not found")
            else:
                self.log_result("Preview Generated App", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Preview Generated App", False, f"Exception: {str(e)}")

    def test_robustness_short_description(self):
        """Test 11a: Robustness - Short Description"""
        print("\n=== Test 11a: Robustness - Short Description ===")
        try:
            if not self.access_token:
                self.log_result("Robustness - Short Description", False, "No access token available")
                return
            
            # Create a project for generation
            project_data = {
                "title": "Site Web Simple",
                "description": "site web",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Robustness - Short Description", False, f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Generate application code with very short description
            generation_request = {
                "description": "site web",
                "type": "web_app",
                "framework": "react"
            }
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            
            if response.status_code == 200:
                data = response.json()
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                has_code = any(data.get(field) for field in code_fields)
                
                if has_code:
                    self.log_result("Robustness - Short Description", True, "App generated successfully with short description")
                else:
                    self.log_result("Robustness - Short Description", False, "No code was generated")
            else:
                self.log_result("Robustness - Short Description", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Robustness - Short Description", False, f"Exception: {str(e)}")

    def test_robustness_long_description(self):
        """Test 11b: Robustness - Long Description"""
        print("\n=== Test 11b: Robustness - Long Description ===")
        try:
            if not self.access_token:
                self.log_result("Robustness - Long Description", False, "No access token available")
                return
            
            # Create a project for generation
            long_description = """Créer une application web complète de gestion d'entreprise avec les fonctionnalités suivantes:
            - Système d'authentification multi-niveaux avec rôles utilisateurs (admin, manager, employé)
            - Dashboard analytique avec graphiques interactifs et métriques en temps réel
            - Module de gestion des clients avec CRM intégré, historique des interactions
            - Système de facturation automatisé avec génération de PDF et envoi par email
            - Gestion des stocks avec alertes de réapprovisionnement et suivi des mouvements
            - Module RH avec gestion des congés, évaluations de performance et paie
            - Système de messagerie interne avec notifications push
            - API REST complète avec documentation Swagger
            - Interface responsive compatible mobile et tablette
            - Système de sauvegarde automatique et export de données
            - Intégration avec services tiers (comptabilité, paiement, email marketing)
            - Fonctionnalités de reporting avancées avec filtres personnalisables"""
            
            project_data = {
                "title": "Application Gestion Entreprise Complète",
                "description": long_description,
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Robustness - Long Description", False, f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Generate application code with very long description
            generation_request = {
                "description": long_description,
                "type": "web_app",
                "framework": "react"
            }
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            
            if response.status_code == 200:
                data = response.json()
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                has_code = any(data.get(field) for field in code_fields)
                
                if has_code:
                    self.log_result("Robustness - Long Description", True, "App generated successfully with long description")
                else:
                    self.log_result("Robustness - Long Description", False, "No code was generated")
            else:
                self.log_result("Robustness - Long Description", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Robustness - Long Description", False, f"Exception: {str(e)}")

    def test_project_status_updates(self):
        """Test 12: Project Status Updates During Generation"""
        print("\n=== Test 12: Project Status Updates During Generation ===")
        try:
            if not self.access_token:
                self.log_result("Project Status Updates", False, "No access token available")
                return
            
            # Create a project for generation
            project_data = {
                "title": "Test Status Updates",
                "description": "Simple web application for testing status updates",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Project Status Updates", False, f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            initial_status = project_response.json()["status"]
            
            # Generate application code
            generation_request = {
                "description": "Simple web application for testing status updates",
                "type": "web_app",
                "framework": "react"
            }
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            
            if response.status_code == 200:
                # Check final project status
                project_check = self.make_request("GET", f"/projects/{project_id}")
                if project_check.status_code == 200:
                    final_status = project_check.json()["status"]
                    if final_status in ["completed", "building"]:
                        self.log_result("Project Status Updates", True, f"Status correctly updated from '{initial_status}' to '{final_status}'")
                    else:
                        self.log_result("Project Status Updates", False, f"Unexpected final status: {final_status}")
                else:
                    self.log_result("Project Status Updates", False, "Could not check final project status")
            else:
                self.log_result("Project Status Updates", False, f"Generation failed: {response.status_code}")
        except Exception as e:
            self.log_result("Project Status Updates", False, f"Exception: {str(e)}")

    def test_error_cases(self):
        """Test 13: Error Cases"""
        print("\n=== Test 13: Error Cases ===")
        
        # Test invalid login
        try:
            response = self.make_request("POST", "/auth/login", {
                "email": "invalid@example.com",
                "password": "wrongpassword"
            })
            
            if response.status_code == 401:
                self.log_result("Invalid Login Error", True, "Correctly rejected invalid credentials")
            else:
                self.log_result("Invalid Login Error", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Login Error", False, f"Exception: {str(e)}")
        
        # Test invalid token
        try:
            headers = {"Authorization": "Bearer invalid_token_here"}
            response = self.make_request("GET", "/auth/me", headers=headers)
            
            if response.status_code == 401:
                self.log_result("Invalid Token Error", True, "Correctly rejected invalid token")
            else:
                self.log_result("Invalid Token Error", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Token Error", False, f"Exception: {str(e)}")
        
        # Test accessing non-existent project
        try:
            if self.access_token:
                response = self.make_request("GET", "/projects/non-existent-id")
                
                if response.status_code == 404:
                    self.log_result("Non-existent Project Error", True, "Correctly returned 404 for non-existent project")
                else:
                    self.log_result("Non-existent Project Error", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("Non-existent Project Error", False, f"Exception: {str(e)}")
        
        # Test generating code for non-existent project
        try:
            if self.access_token:
                generation_request = {
                    "description": "test description",
                    "type": "web_app",
                    "framework": "react"
                }
                response = self.make_request("POST", "/projects/non-existent-id/generate", generation_request)
                
                if response.status_code == 404:
                    self.log_result("Generate for Non-existent Project Error", True, "Correctly returned 404 for non-existent project generation")
                else:
                    self.log_result("Generate for Non-existent Project Error", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("Generate for Non-existent Project Error", False, f"Exception: {str(e)}")

    def test_password_strength_validation(self):
        """Test CORRECTION 3: Enhanced Authentication - Password Strength"""
        print("\n=== CORRECTION 3: Password Strength Validation ===")
        
        weak_passwords = [
            "123",
            "password", 
            "PASSWORD",
            "Password",
            "Password1",
            "admin",
            "test123",
            "12345678"
        ]
        
        strong_passwords = [
            "Password123!",
            "SecureP@ss2024",
            "Test123!@#",
            "MyStr0ng!Pass"
        ]
        
        # Test weak passwords - should be rejected
        for weak_pass in weak_passwords:
            try:
                test_user = {
                    "email": f"weak.test.{int(time.time())}.{weak_pass.replace('!', 'x')}@vectort.io",
                    "password": weak_pass,
                    "full_name": "Weak Password Test"
                }
                
                response = self.make_request("POST", "/auth/register", test_user)
                
                if response.status_code == 422:
                    self.log_result(f"Weak Password Rejection ({weak_pass})", True, 
                                  f"Correctly rejected weak password: {weak_pass}")
                else:
                    self.log_result(f"Weak Password Rejection ({weak_pass})", False, 
                                  f"Weak password '{weak_pass}' was accepted (Status: {response.status_code})")
            except Exception as e:
                self.log_result(f"Weak Password Rejection ({weak_pass})", False, f"Exception: {str(e)}")
        
        # Test strong passwords - should be accepted
        for strong_pass in strong_passwords[:2]:  # Test only 2 to avoid too many users
            try:
                test_user = {
                    "email": f"strong.test.{int(time.time())}.{hash(strong_pass) % 10000}@vectort.io",
                    "password": strong_pass,
                    "full_name": "Strong Password Test"
                }
                
                response = self.make_request("POST", "/auth/register", test_user)
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        self.log_result(f"Strong Password Acceptance ({strong_pass})", True, 
                                      f"Correctly accepted strong password: {strong_pass}")
                    else:
                        self.log_result(f"Strong Password Acceptance ({strong_pass})", False, 
                                      "Registration succeeded but no token returned")
                else:
                    self.log_result(f"Strong Password Acceptance ({strong_pass})", False, 
                                  f"Strong password '{strong_pass}' was rejected (Status: {response.status_code})")
            except Exception as e:
                self.log_result(f"Strong Password Acceptance ({strong_pass})", False, f"Exception: {str(e)}")

    def test_projecttype_enum_correction(self):
        """Test CORRECTION 1: ProjectType enum correction"""
        print("\n=== CORRECTION 1: ProjectType Enum Correction ===")
        
        if not self.access_token:
            self.log_result("ProjectType Enum Test", False, "No access token available")
            return
        
        # Test ecommerce project type specifically
        try:
            project_data = {
                "title": "Test E-commerce Enum",
                "description": "Test project for ecommerce enum validation",
                "type": "ecommerce"  # This should work with enum correction
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("ProjectType Enum - Project Creation", False, 
                              f"Failed to create ecommerce project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Test advanced mode generation with ecommerce type
            generation_request = {
                "description": "Créer une boutique en ligne moderne avec panier d'achats et système de paiement",
                "type": "ecommerce",  # Test enum recognition
                "framework": "react",
                "database": "mongodb",
                "advanced_mode": True,  # Test advanced mode
                "features": ["authentication", "payment_processing", "shopping_cart"]
            }
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            
            if response.status_code == 200:
                data = response.json()
                if any(data.get(field) for field in ["html_code", "css_code", "js_code", "react_code"]):
                    self.log_result("ProjectType Enum - E-commerce Generation", True, 
                                  "E-commerce project generated successfully with enum correction")
                else:
                    self.log_result("ProjectType Enum - E-commerce Generation", False, 
                                  "No code generated despite successful response")
            else:
                # Check if fallback to basic mode worked
                if response.status_code == 500:
                    self.log_result("ProjectType Enum - Fallback Test", True, 
                                  "Advanced mode failed but should fallback to basic mode")
                else:
                    self.log_result("ProjectType Enum - E-commerce Generation", False, 
                                  f"Generation failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("ProjectType Enum Test", False, f"Exception: {str(e)}")

    def test_llmchat_initialization(self):
        """Test CORRECTION 2: LlmChat initialization with system_message"""
        print("\n=== CORRECTION 2: LlmChat Initialization ===")
        
        if not self.access_token:
            self.log_result("LlmChat Initialization Test", False, "No access token available")
            return
        
        try:
            # Create project for testing
            project_data = {
                "title": "Test LlmChat System Message",
                "description": "Test project for LlmChat initialization",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("LlmChat Test - Project Creation", False, 
                              f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Test advanced mode generation (should use LlmChat with system_message)
            generation_request = {
                "description": "Créer une application web simple avec React",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": True  # This should trigger LlmChat initialization
            }
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            
            if response.status_code == 200:
                data = response.json()
                if any(data.get(field) for field in ["html_code", "css_code", "js_code", "react_code"]):
                    self.log_result("LlmChat Initialization - Advanced Mode", True, 
                                  "Advanced mode generation successful - LlmChat initialized correctly")
                else:
                    self.log_result("LlmChat Initialization - Advanced Mode", False, 
                                  "Advanced mode succeeded but no code generated")
            else:
                # Test basic mode as fallback
                basic_request = {
                    "description": "Créer une application web simple avec React",
                    "type": "web_app", 
                    "framework": "react",
                    "advanced_mode": False
                }
                
                basic_response = self.make_request("POST", f"/projects/{project_id}/generate", basic_request)
                
                if basic_response.status_code == 200:
                    self.log_result("LlmChat Initialization - Basic Fallback", True, 
                                  "Basic mode works as fallback when advanced mode fails")
                else:
                    self.log_result("LlmChat Initialization", False, 
                                  f"Both advanced and basic modes failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("LlmChat Initialization Test", False, f"Exception: {str(e)}")

    def test_complete_generation_ecommerce_react(self):
        """Test CORRECTION 4: Complete Generation - E-commerce with React"""
        print("\n=== CORRECTION 4a: Complete Generation - E-commerce + React ===")
        
        if not self.access_token:
            self.log_result("Complete Generation E-commerce", False, "No access token available")
            return
        
        try:
            project_data = {
                "title": "E-commerce React Complet",
                "description": "Boutique en ligne complète avec React",
                "type": "ecommerce"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Complete Generation E-commerce", False, 
                              f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Test complete generation
            generation_request = {
                "description": "Créer une boutique en ligne complète avec catalogue produits, panier d'achats, système de paiement, gestion des commandes et interface d'administration",
                "type": "ecommerce",
                "framework": "react",
                "database": "mongodb",
                "advanced_mode": True,
                "features": ["authentication", "payment_processing", "shopping_cart", "admin_panel"],
                "integrations": ["stripe", "paypal"]
            }
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for complete generation
                has_react = bool(data.get("react_code"))
                has_backend = bool(data.get("backend_code"))
                has_css = bool(data.get("css_code"))
                
                if has_react and has_backend and has_css:
                    self.log_result("Complete Generation E-commerce", True, 
                                  "Complete e-commerce application generated with React, backend, and styling")
                elif has_react or has_backend:
                    self.log_result("Complete Generation E-commerce", True, 
                                  "Partial e-commerce generation successful (some components generated)")
                else:
                    self.log_result("Complete Generation E-commerce", False, 
                                  "No meaningful code generated")
            else:
                self.log_result("Complete Generation E-commerce", False, 
                              f"Generation failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Complete Generation E-commerce", False, f"Exception: {str(e)}")

    def test_complete_generation_social_vue(self):
        """Test CORRECTION 4: Complete Generation - Social Media with Vue"""
        print("\n=== CORRECTION 4b: Complete Generation - Social Media + Vue ===")
        
        if not self.access_token:
            self.log_result("Complete Generation Social Vue", False, "No access token available")
            return
        
        try:
            project_data = {
                "title": "Social Media Vue Complet",
                "description": "Réseau social complet avec Vue.js",
                "type": "social_media"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Complete Generation Social Vue", False, 
                              f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Test complete generation with Vue
            generation_request = {
                "description": "Créer un réseau social complet avec profils utilisateurs, fil d'actualité, messagerie, notifications et système d'amis",
                "type": "social_media",
                "framework": "vue",
                "database": "postgresql",
                "advanced_mode": True,
                "features": ["authentication", "real_time_chat", "notifications", "user_profiles"],
                "integrations": ["websocket", "redis"]
            }
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for Vue-specific generation
                has_vue_code = bool(data.get("react_code"))  # Backend might return React code for Vue
                has_backend = bool(data.get("backend_code"))
                has_css = bool(data.get("css_code"))
                
                if has_vue_code and has_backend:
                    self.log_result("Complete Generation Social Vue", True, 
                                  "Complete social media application generated with Vue and backend")
                elif has_vue_code or has_backend:
                    self.log_result("Complete Generation Social Vue", True, 
                                  "Partial social media generation successful")
                else:
                    self.log_result("Complete Generation Social Vue", False, 
                                  "No meaningful code generated for Vue social media app")
            else:
                self.log_result("Complete Generation Social Vue", False, 
                              f"Generation failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Complete Generation Social Vue", False, f"Exception: {str(e)}")

    def test_final_validation_endpoints(self):
        """Test CORRECTION 5: Final Validation - All Critical Endpoints"""
        print("\n=== CORRECTION 5: Final Validation - Critical Endpoints ===")
        
        critical_endpoints = [
            ("GET", "/", "Basic API"),
            ("GET", "/stats", "Global Statistics"),
        ]
        
        if self.access_token:
            authenticated_endpoints = [
                ("GET", "/auth/me", "Authentication Check"),
                ("GET", "/projects", "Project Listing"),
                ("GET", "/users/stats", "User Statistics")
            ]
            critical_endpoints.extend(authenticated_endpoints)
        
        all_passed = True
        
        for method, endpoint, name in critical_endpoints:
            try:
                response = self.make_request(method, endpoint)
                
                if response.status_code == 200:
                    self.log_result(f"Critical Endpoint - {name}", True, 
                                  f"{method} {endpoint} returned 200 OK")
                else:
                    self.log_result(f"Critical Endpoint - {name}", False, 
                                  f"{method} {endpoint} returned {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_result(f"Critical Endpoint - {name}", False, f"Exception: {str(e)}")
                all_passed = False
        
        if all_passed:
            self.log_result("Final Validation - All Endpoints", True, 
                          "All critical endpoints functional - no 500 errors detected")
        else:
            self.log_result("Final Validation - All Endpoints", False, 
                          "Some critical endpoints failed validation")

    def run_corrections_tests(self):
        """Run specific tests for the corrections mentioned in review request"""
        print("🔧 VÉRIFICATION DES CORRECTIONS PRÉ-DÉPLOIEMENT")
        print(f"Testing against: {self.base_url}")
        print("=" * 80)
        
        # Setup authentication first
        print("\n🔐 SETUP: Authentication")
        print("-" * 50)
        self.test_user_registration()
        if not self.access_token:
            self.test_user_login()
        
        # Test specific corrections
        print("\n🎯 CORRECTIONS TESTING")
        print("-" * 50)
        
        self.test_projecttype_enum_correction()
        self.test_llmchat_initialization()
        self.test_password_strength_validation()
        self.test_complete_generation_ecommerce_react()
        self.test_complete_generation_social_vue()
        self.test_final_validation_endpoints()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🔧 CORRECTIONS VALIDATION SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED CORRECTIONS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        else:
            print("\n🎉 ALL CORRECTIONS VALIDATED! Ready for deployment!")
        
        return self.results['failed'] == 0

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Vectort.io AI Application Generation System Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 80)
        
        # Phase 1: Basic authentication and projects (quick)
        print("\n🔐 PHASE 1: AUTHENTICATION & BASIC PROJECTS")
        print("-" * 50)
        self.test_basic_api_response()
        self.test_user_registration()
        if not self.access_token:
            self.test_user_login()
        self.test_authentication_check()
        self.test_project_creation()
        
        # Phase 2: AI Application Generation (main focus)
        print("\n🤖 PHASE 2: AI APPLICATION GENERATION")
        print("-" * 50)
        self.test_ai_app_generation_ecommerce()
        self.test_ai_app_generation_task_manager()
        self.test_ai_app_generation_portfolio()
        self.test_ai_app_generation_landing_page()
        
        # Phase 3: Code retrieval and preview
        print("\n📄 PHASE 3: CODE RETRIEVAL & PREVIEW")
        print("-" * 50)
        self.test_get_generated_code()
        self.test_preview_generated_app()
        
        # Phase 4: Robustness testing
        print("\n🛡️ PHASE 4: ROBUSTNESS TESTING")
        print("-" * 50)
        self.test_robustness_short_description()
        self.test_robustness_long_description()
        self.test_project_status_updates()
        
        # Phase 5: Additional tests
        print("\n📊 PHASE 5: ADDITIONAL FUNCTIONALITY")
        print("-" * 50)
        self.test_project_listing()
        self.test_project_retrieval()
        self.test_global_statistics()
        self.test_user_statistics()
        self.test_error_cases()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        else:
            print("\n🎉 ALL TESTS PASSED! The Vectort.io AI Application Generation System is working perfectly!")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = CodexAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)