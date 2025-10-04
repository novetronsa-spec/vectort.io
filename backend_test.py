#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Codex Application
Tests all authentication, project management, and statistics endpoints
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://emergent-clone-151.preview.emergentagent.com/api"
TEST_USER = {
    "email": "marie.dupont@example.com",
    "password": "SecurePass123!",
    "full_name": "Marie Dupont"
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

    def test_error_cases(self):
        """Test 7: Error Cases"""
        print("\n=== Test 7: Error Cases ===")
        
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

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Codex API Backend Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Run tests in order
        self.test_basic_api_response()
        self.test_user_registration()
        if not self.access_token:
            self.test_user_login()
        self.test_authentication_check()
        self.test_project_creation()
        self.test_project_listing()
        self.test_project_retrieval()
        self.test_project_deletion()
        self.test_global_statistics()
        self.test_user_statistics()
        self.test_error_cases()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = CodexAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)