#!/usr/bin/env python3
"""
🎯 FOCUSED BACKEND TEST - Validation des tâches critiques
Test spécifique pour les tâches marquées comme failing dans test_result.md
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuration - LOCAL ENVIRONMENT API
BASE_URL = "http://localhost:8001/api"

class FocusedBackendTester:
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
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=default_headers, timeout=60)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers, timeout=60)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise

    def setup_test_user(self):
        """Setup test user and authentication"""
        print("=== Setup: Creating Test User ===")
        
        test_user = {
            "email": f"focused_test_{int(time.time())}@vectort.io",
            "password": "FocusedTest123!",
            "full_name": f"Focused Test User {int(time.time())}"
        }
        
        # Register user
        response = self.make_request("POST", "/auth/register", test_user)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.user_id = data["user"]["id"]
            print(f"✅ Test user created: {self.user_id}")
            return True
        elif response.status_code == 400:
            # Try login if user exists
            login_response = self.make_request("POST", "/auth/login", {
                "email": test_user["email"],
                "password": test_user["password"]
            })
            if login_response.status_code == 200:
                data = login_response.json()
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                print(f"✅ Existing user logged in: {self.user_id}")
                return True
        
        print(f"❌ Failed to setup test user: {response.status_code}")
        return False

    def test_vectort_io_100_percent_functionality(self):
        """Test: VECTORT.IO 100% Functionality Test - E-commerce Advanced Mode"""
        print("\n=== 🎯 TEST: VECTORT.IO 100% Functionality - E-commerce Advanced Mode ===")
        
        try:
            # Create e-commerce project
            project_data = {
                "title": "E-commerce Test 100%",
                "description": "Boutique en ligne complète avec panier d'achats, système de paiement, gestion produits, authentification utilisateur, et dashboard admin",
                "type": "ecommerce"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("VECTORT.IO 100% Functionality", False, f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            self.test_project_id = project_id
            
            # Test Advanced Mode Generation
            generation_request = {
                "description": "Boutique en ligne complète avec panier d'achats, système de paiement Stripe, gestion produits, authentification utilisateur, et dashboard admin",
                "type": "ecommerce",
                "framework": "react",
                "database": "mongodb",
                "advanced_mode": True,  # ADVANCED MODE
                "features": ["authentication", "payment_processing", "shopping_cart", "admin_panel"],
                "integrations": ["stripe"]
            }
            
            print("🚀 Testing Advanced Mode Generation...")
            start_time = time.time()
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            generation_time = time.time() - start_time
            
            print(f"⏱️ Generation time: {generation_time:.1f}s")
            
            if response.status_code in [200, 201]:
                data = response.json()
                
                # CRITICAL CHECKS according to test_result.md issues
                print("\n--- Critical Functionality Checks ---")
                
                # 1. Performance check (< 20s target)
                performance_ok = generation_time < 20
                print(f"1. Performance < 20s: {'✅' if performance_ok else '❌'} ({generation_time:.1f}s)")
                
                # 2. File mapping check - ALL fields should be populated
                html_code = bool(data.get("html_code"))
                css_code = bool(data.get("css_code"))
                js_code = bool(data.get("js_code"))
                react_code = bool(data.get("react_code"))
                backend_code = bool(data.get("backend_code"))
                
                print(f"2. File Mapping:")
                print(f"   - html_code: {'✅' if html_code else '❌'}")
                print(f"   - css_code: {'✅' if css_code else '❌'}")
                print(f"   - js_code: {'✅' if js_code else '❌'}")
                print(f"   - react_code: {'✅' if react_code else '❌'}")
                print(f"   - backend_code: {'✅' if backend_code else '❌'}")
                
                mapping_score = sum([html_code, css_code, js_code, react_code, backend_code])
                mapping_complete = mapping_score >= 4  # At least 4/5 fields
                
                # 3. all_files field check
                all_files = data.get("all_files", {})
                all_files_populated = bool(all_files) and len(all_files) >= 8
                print(f"3. all_files populated: {'✅' if all_files_populated else '❌'} ({len(all_files) if all_files else 0} files)")
                
                # 4. Framework-specific mapping (React → react_code, FastAPI → backend_code)
                framework_mapping_ok = react_code  # React should generate react_code
                print(f"4. Framework mapping (React→react_code): {'✅' if framework_mapping_ok else '❌'}")
                
                # 5. Overall functionality score
                criteria = [performance_ok, mapping_complete, all_files_populated, framework_mapping_ok]
                functionality_score = sum(criteria) / len(criteria) * 100
                target_score = 80  # 80% target from test_result.md
                
                print(f"\n--- FUNCTIONALITY SCORE ---")
                print(f"Score: {functionality_score:.1f}% (Target: {target_score}%)")
                print(f"Criteria passed: {sum(criteria)}/{len(criteria)}")
                
                if functionality_score >= target_score:
                    self.log_result("VECTORT.IO 100% Functionality", True, 
                                  f"🎉 FUNCTIONALITY TARGET ACHIEVED: {functionality_score:.1f}% "
                                  f"(Performance: {generation_time:.1f}s, Mapping: {mapping_score}/5, "
                                  f"Files: {len(all_files) if all_files else 0})")
                else:
                    self.log_result("VECTORT.IO 100% Functionality", False, 
                                  f"❌ Functionality below target: {functionality_score:.1f}% < {target_score}%. "
                                  f"Issues: Performance: {performance_ok}, Mapping: {mapping_complete}, "
                                  f"Files: {all_files_populated}, Framework: {framework_mapping_ok}")
                    
            elif response.status_code == 402:
                self.log_result("VECTORT.IO 100% Functionality", False, "❌ Insufficient credits")
            else:
                self.log_result("VECTORT.IO 100% Functionality", False, 
                              f"❌ Generation failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("VECTORT.IO 100% Functionality", False, f"Exception: {str(e)}")

    def test_file_mapping_intelligence_system(self):
        """Test: File Mapping Intelligence System"""
        print("\n=== 🎯 TEST: File Mapping Intelligence System ===")
        
        try:
            if not self.test_project_id:
                print("❌ No test project available, skipping file mapping test")
                return
            
            # Get the generated code from previous test
            response = self.make_request("GET", f"/projects/{self.test_project_id}/code")
            
            if response.status_code == 200:
                data = response.json()
                
                print("--- File Mapping Analysis ---")
                
                # Check individual file mappings
                mappings = {
                    "HTML": data.get("html_code"),
                    "CSS": data.get("css_code"), 
                    "JavaScript": data.get("js_code"),
                    "React": data.get("react_code"),
                    "Backend": data.get("backend_code")
                }
                
                successful_mappings = 0
                for file_type, content in mappings.items():
                    has_content = bool(content and len(content.strip()) > 0)
                    print(f"{file_type} mapping: {'✅' if has_content else '❌'} ({len(content) if content else 0} chars)")
                    if has_content:
                        successful_mappings += 1
                
                # Check all_files structure
                all_files = data.get("all_files", {})
                all_files_count = len(all_files) if all_files else 0
                print(f"all_files structure: {'✅' if all_files_count > 0 else '❌'} ({all_files_count} files)")
                
                # Mapping intelligence score
                mapping_percentage = (successful_mappings / len(mappings)) * 100
                target_percentage = 75  # 75% minimum from test_result.md
                
                print(f"\n--- MAPPING INTELLIGENCE SCORE ---")
                print(f"Mapping success: {mapping_percentage:.1f}% ({successful_mappings}/{len(mappings)} fields)")
                print(f"Target: {target_percentage}%")
                
                if mapping_percentage >= target_percentage and all_files_count > 0:
                    self.log_result("File Mapping Intelligence", True, 
                                  f"✅ Mapping system working: {mapping_percentage:.1f}% success, "
                                  f"{all_files_count} files in all_files structure")
                else:
                    self.log_result("File Mapping Intelligence", False, 
                                  f"❌ Mapping system issues: {mapping_percentage:.1f}% < {target_percentage}%, "
                                  f"all_files: {all_files_count} files")
                    
                # Show file structure for debugging
                if all_files:
                    print(f"\n📁 Generated file structure:")
                    for i, (filename, content) in enumerate(list(all_files.items())[:8]):
                        content_size = len(content) if content else 0
                        print(f"  {i+1}. {filename} ({content_size} chars)")
                    if len(all_files) > 8:
                        print(f"  ... and {len(all_files) - 8} more files")
                        
            else:
                self.log_result("File Mapping Intelligence", False, 
                              f"❌ Could not retrieve generated code: {response.status_code}")
                
        except Exception as e:
            self.log_result("File Mapping Intelligence", False, f"Exception: {str(e)}")

    def test_credit_system_functionality(self):
        """Test: Credit System Complete Functionality"""
        print("\n=== 🎯 TEST: Credit System Complete Functionality ===")
        
        try:
            # Test credit balance
            balance_response = self.make_request("GET", "/credits/balance")
            
            if balance_response.status_code == 200:
                balance_data = balance_response.json()
                
                required_fields = ["free_credits", "monthly_credits", "purchased_credits", "total_available", "subscription_plan"]
                has_all_fields = all(field in balance_data for field in required_fields)
                
                print(f"Credit balance structure: {'✅' if has_all_fields else '❌'}")
                print(f"  - Free credits: {balance_data.get('free_credits', 'N/A')}")
                print(f"  - Total available: {balance_data.get('total_available', 'N/A')}")
                print(f"  - Subscription: {balance_data.get('subscription_plan', 'N/A')}")
                
                # Test credit packages
                packages_response = self.make_request("GET", "/credits/packages")
                
                if packages_response.status_code == 200:
                    packages_data = packages_response.json()
                    
                    has_packages = isinstance(packages_data, list) and len(packages_data) >= 3
                    print(f"Credit packages available: {'✅' if has_packages else '❌'} ({len(packages_data) if isinstance(packages_data, list) else 0} packages)")
                    
                    if has_all_fields and has_packages:
                        self.log_result("Credit System Functionality", True, 
                                      f"✅ Credit system operational: Balance API working, {len(packages_data)} packages available")
                    else:
                        self.log_result("Credit System Functionality", False, 
                                      f"❌ Credit system issues: Balance fields: {has_all_fields}, Packages: {has_packages}")
                else:
                    self.log_result("Credit System Functionality", False, 
                                  f"❌ Credit packages endpoint failed: {packages_response.status_code}")
            else:
                self.log_result("Credit System Functionality", False, 
                              f"❌ Credit balance endpoint failed: {balance_response.status_code}")
                
        except Exception as e:
            self.log_result("Credit System Functionality", False, f"Exception: {str(e)}")

    def run_focused_tests(self):
        """Run focused tests on critical failing tasks"""
        print("🎯 FOCUSED BACKEND TESTING - Critical Tasks Validation")
        print("=" * 70)
        
        # Setup
        if not self.setup_test_user():
            print("❌ Failed to setup test user, aborting tests")
            return
        
        # Run focused tests on failing tasks
        self.test_vectort_io_100_percent_functionality()
        self.test_file_mapping_intelligence_system()
        self.test_credit_system_functionality()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 FOCUSED TEST RESULTS")
        print("=" * 70)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results["failed"] > 0:
            print("\n🚨 FAILED TESTS:")
            for error in self.results["errors"]:
                print(f"  - {error}")
        
        success_rate = (self.results["passed"] / (self.results["passed"] + self.results["failed"])) * 100 if (self.results["passed"] + self.results["failed"]) > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 FOCUSED TESTS SUCCESSFUL - Critical tasks are working!")
        else:
            print("⚠️ CRITICAL ISSUES DETECTED - Some tasks need attention")

if __name__ == "__main__":
    tester = FocusedBackendTester()
    tester.run_focused_tests()