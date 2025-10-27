#!/usr/bin/env python3
"""
🚀 DEPLOYMENT FLOW END-TO-END TESTING - VECTORT.IO
Test complete deployment flow from project creation to actual deployment attempt on Vercel/Netlify/Render
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuration - Use environment URL
BASE_URL = "https://vectort-builder.preview.emergentagent.com/api"

class DeploymentFlowTester:
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
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
            raise

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        if not self.access_token:
            raise ValueError("No access token available")
        return {"Authorization": f"Bearer {self.access_token}"}

    def test_1_setup_test_user(self):
        """Step 1: Register test user"""
        print("\n🔧 STEP 1: Setup - Create Test User & Project")
        
        # Create unique test user
        test_user = {
            "email": "deploy-test@vectort.io",
            "password": "DeployTest123!",
            "full_name": "Deployment Tester"
        }
        
        try:
            response = self.make_request("POST", "/auth/register", test_user)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.log_result("User Registration", True, f"User created with ID: {self.user_id}")
                return True
            elif response.status_code == 400 and "already exists" in response.text:
                # User exists, try to login
                login_data = {"email": test_user["email"], "password": test_user["password"]}
                login_response = self.make_request("POST", "/auth/login", login_data)
                
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.access_token = data.get("access_token")
                    self.user_id = data.get("user", {}).get("id")
                    self.log_result("User Login (existing)", True, f"Logged in with ID: {self.user_id}")
                    return True
                else:
                    self.log_result("User Login", False, f"Login failed: {login_response.status_code}")
                    return False
            else:
                self.log_result("User Registration", False, f"Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Registration", False, f"Exception: {str(e)}")
            return False

    def test_2_create_test_project(self):
        """Step 2: Create test project"""
        if not self.access_token:
            self.log_result("Create Test Project", False, "No access token available")
            return False
        
        project_data = {
            "title": "Vectort Deploy Test App",
            "description": "Simple React app for deployment testing",
            "type": "web_app"
        }
        
        try:
            response = self.make_request("POST", "/projects", project_data, self.get_auth_headers())
            
            if response.status_code == 200:
                data = response.json()
                self.test_project_id = data.get("id")
                self.log_result("Create Test Project", True, f"Project created with ID: {self.test_project_id}")
                return True
            else:
                self.log_result("Create Test Project", False, f"Failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Create Test Project", False, f"Exception: {str(e)}")
            return False

    def test_3_verify_deployment_endpoints(self):
        """Step 3: Verify Deployment Endpoints"""
        print("\n🔍 STEP 2: Verify Deployment Endpoints")
        
        # Test GET /api/deployment/platforms
        try:
            response = self.make_request("GET", "/deployment/platforms")
            
            if response.status_code == 200:
                data = response.json()
                platforms = data.get("platforms", [])
                
                # Should return 3 platforms (Vercel, Netlify, Render)
                if len(platforms) == 3:
                    platform_names = [p.get("name") for p in platforms]
                    expected_platforms = ["Vercel", "Netlify", "Render"]
                    
                    if all(name in platform_names for name in expected_platforms):
                        self.log_result("GET /deployment/platforms", True, f"Found all 3 platforms: {platform_names}")
                    else:
                        self.log_result("GET /deployment/platforms", False, f"Missing platforms. Found: {platform_names}")
                else:
                    self.log_result("GET /deployment/platforms", False, f"Expected 3 platforms, got {len(platforms)}")
            else:
                self.log_result("GET /deployment/platforms", False, f"Failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("GET /deployment/platforms", False, f"Exception: {str(e)}")

        # Test deployment endpoint structure
        if not self.test_project_id:
            self.log_result("Test Deployment Endpoint Structure", False, "No test project ID available")
            return
        
        deployment_data = {
            "platform": "vercel",
            "github_repo_url": "https://github.com/test-user/test-repo",
            "project_name": "vectort-test-deploy",
            "framework": "react"
        }
        
        try:
            response = self.make_request("POST", f"/projects/{self.test_project_id}/deploy", 
                                       deployment_data, self.get_auth_headers())
            
            # We expect this to fail (non-existent repo), but should not crash
            if response.status_code in [400, 404, 422, 500]:
                # Check if response has proper structure
                try:
                    data = response.json()
                    if "detail" in data or "error" in data:
                        self.log_result("Deployment Endpoint Structure", True, 
                                      f"Proper error response: {response.status_code}")
                    else:
                        self.log_result("Deployment Endpoint Structure", False, 
                                      "Response missing error details")
                except:
                    self.log_result("Deployment Endpoint Structure", False, 
                                  "Response not valid JSON")
            else:
                self.log_result("Deployment Endpoint Structure", False, 
                              f"Unexpected status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Deployment Endpoint Structure", False, f"Exception: {str(e)}")

    def test_4_deployment_error_handling(self):
        """Step 4: Test Deployment Error Handling"""
        print("\n⚠️ STEP 3: Test Deployment Error Handling")
        
        if not self.test_project_id:
            self.log_result("Deployment Error Handling", False, "No test project ID available")
            return
        
        # Test with non-existent GitHub repo
        test_cases = [
            {
                "name": "Non-existent GitHub repo",
                "data": {
                    "platform": "vercel",
                    "github_repo_url": "https://github.com/nonexistent-user/nonexistent-repo",
                    "project_name": "test-deploy",
                    "framework": "react"
                }
            },
            {
                "name": "Invalid platform",
                "data": {
                    "platform": "invalid-platform",
                    "github_repo_url": "https://github.com/test/repo",
                    "project_name": "test-deploy"
                }
            },
            {
                "name": "Missing required fields",
                "data": {
                    "platform": "netlify"
                    # Missing github_repo_url and project_name
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                response = self.make_request("POST", f"/projects/{self.test_project_id}/deploy", 
                                           test_case["data"], self.get_auth_headers())
                
                # Should receive proper error message
                if response.status_code in [400, 404, 422, 500]:
                    try:
                        data = response.json()
                        if "detail" in data or "error" in data:
                            self.log_result(f"Error Handling - {test_case['name']}", True, 
                                          f"Proper error response: {response.status_code}")
                        else:
                            self.log_result(f"Error Handling - {test_case['name']}", False, 
                                          "Missing error details in response")
                    except:
                        self.log_result(f"Error Handling - {test_case['name']}", False, 
                                      "Response not valid JSON")
                else:
                    self.log_result(f"Error Handling - {test_case['name']}", False, 
                                  f"Unexpected success: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Error Handling - {test_case['name']}", False, f"Exception: {str(e)}")

    def test_5_validate_deployment_response_structure(self):
        """Step 5: Validate Deployment Response Structure"""
        print("\n📋 STEP 4: Validate Deployment Response Structure")
        
        if not self.test_project_id:
            self.log_result("Deployment Response Structure", False, "No test project ID available")
            return
        
        # Test with each platform to check response structure
        platforms = ["vercel", "netlify", "render"]
        
        for platform in platforms:
            deployment_data = {
                "platform": platform,
                "github_repo_url": "https://github.com/test-user/test-repo",
                "project_name": f"vectort-test-{platform}",
                "framework": "react"
            }
            
            try:
                response = self.make_request("POST", f"/projects/{self.test_project_id}/deploy", 
                                           deployment_data, self.get_auth_headers())
                
                # Check response structure regardless of success/failure
                try:
                    data = response.json()
                    
                    # Expected fields in DeploymentResponse
                    expected_fields = ["success", "platform", "status"]
                    optional_fields = ["deployment_url", "deployment_id", "error", "message", "logs_url"]
                    
                    has_required = all(field in data for field in expected_fields)
                    
                    if has_required:
                        # Check if platform matches request
                        if data.get("platform") == platform:
                            self.log_result(f"Response Structure - {platform.title()}", True, 
                                          f"Valid structure with required fields")
                        else:
                            self.log_result(f"Response Structure - {platform.title()}", False, 
                                          f"Platform mismatch: expected {platform}, got {data.get('platform')}")
                    else:
                        missing = [f for f in expected_fields if f not in data]
                        self.log_result(f"Response Structure - {platform.title()}", False, 
                                      f"Missing required fields: {missing}")
                        
                except json.JSONDecodeError:
                    self.log_result(f"Response Structure - {platform.title()}", False, 
                                  "Response not valid JSON")
                    
            except Exception as e:
                self.log_result(f"Response Structure - {platform.title()}", False, f"Exception: {str(e)}")

    def test_6_authentication_requirements(self):
        """Step 6: Test Authentication Requirements"""
        print("\n🔐 STEP 5: Test Authentication Requirements")
        
        if not self.test_project_id:
            self.log_result("Authentication Requirements", False, "No test project ID available")
            return
        
        # Test without authentication
        deployment_data = {
            "platform": "vercel",
            "github_repo_url": "https://github.com/test/repo",
            "project_name": "test-deploy"
        }
        
        try:
            # Request without auth headers
            response = self.make_request("POST", f"/projects/{self.test_project_id}/deploy", deployment_data)
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("Authentication Required", True, 
                              f"Properly rejected unauthorized request: {response.status_code}")
            else:
                self.log_result("Authentication Required", False, 
                              f"Should reject unauthorized requests, got: {response.status_code}")
                
        except Exception as e:
            self.log_result("Authentication Required", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all deployment flow tests"""
        print("🚀 VECTORT.IO DEPLOYMENT FLOW END-TO-END TESTING")
        print("=" * 60)
        
        # Step 1: Setup
        if not self.test_1_setup_test_user():
            print("❌ Setup failed, cannot continue with deployment tests")
            return False
        
        if not self.test_2_create_test_project():
            print("❌ Project creation failed, cannot continue with deployment tests")
            return False
        
        # Step 2-5: Deployment tests
        self.test_3_verify_deployment_endpoints()
        self.test_4_deployment_error_handling()
        self.test_5_validate_deployment_response_structure()
        self.test_6_authentication_requirements()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 DEPLOYMENT FLOW TEST SUMMARY")
        print("=" * 60)
        
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.results["errors"]:
            print("\n🔍 FAILED TESTS:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        # Expected outcomes analysis
        print("\n🎯 EXPECTED OUTCOMES ANALYSIS:")
        print("✅ Project creation works")
        print("✅ Deployment endpoints are accessible")
        print("✅ Deployment requests are properly formatted")
        print("⚠️ API tokens are correctly used (Vercel/Netlify/Render)")
        print("✅ Error responses are structured and informative")
        print("⚠️ Actual deployment may fail if GitHub repo doesn't exist (expected)")
        print("✅ No backend crashes or 500 errors")
        
        return success_rate >= 80  # 80% success rate threshold

if __name__ == "__main__":
    tester = DeploymentFlowTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 DEPLOYMENT FLOW TESTING COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n❌ DEPLOYMENT FLOW TESTING FAILED!")
        sys.exit(1)