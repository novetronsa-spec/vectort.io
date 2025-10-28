#!/usr/bin/env python3
"""
🎯 RE-TEST BACKEND MODE AVANCÉ - Vérification Correction
Test spécifique pour la correction de la fonction map_multi_agent_files_to_response()
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://devstream-ai.preview.emergentagent.com/api"
TEST_USER = {
    "email": "js_tester@vectort.io",
    "password": "TestPassword123!",
    "full_name": "JS Tester"
}

class AdvancedModeAPITester:
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
        
        if self.access_token:
            default_headers["Authorization"] = f"Bearer {self.access_token}"
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                return requests.get(url, headers=default_headers, timeout=30)
            elif method.upper() == "POST":
                return requests.post(url, json=data, headers=default_headers, timeout=60)
            elif method.upper() == "PUT":
                return requests.put(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == "DELETE":
                return requests.delete(url, headers=default_headers, timeout=30)
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None

    def test_authentication(self):
        """Test user authentication"""
        print("\n🔐 Testing Authentication...")
        
        # Try to login first (user might already exist)
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
            self.log_result("User Login", True, f"Logged in successfully")
            return True
        
        # If login fails, try registration
        register_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"],
            "full_name": TEST_USER["full_name"]
        }
        
        response = self.make_request("POST", "/auth/register", register_data)
        
        if response and response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
            self.log_result("User Registration", True, f"Registered successfully with 10 free credits")
            return True
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result("Authentication", False, f"Failed: {error_msg}")
            return False

    def test_create_project(self, title: str, description: str) -> str:
        """Create a test project and return project ID"""
        project_data = {
            "title": title,
            "description": description,
            "type": "web_app"
        }
        
        response = self.make_request("POST", "/projects", project_data)
        
        if response and response.status_code == 200:
            project = response.json()
            project_id = project.get("id")
            self.log_result(f"Project Creation - {title}", True, f"Project ID: {project_id}")
            return project_id
        else:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result(f"Project Creation - {title}", False, f"Failed: {error_msg}")
            return None

    def test_advanced_mode_generation(self, project_id: str, description: str, test_name: str):
        """Test advanced mode generation with detailed analysis"""
        print(f"\n🚀 Testing Advanced Mode Generation - {test_name}...")
        
        generation_data = {
            "description": description,
            "type": "web_app",
            "framework": "react",
            "advanced_mode": True
        }
        
        start_time = time.time()
        response = self.make_request("POST", f"/projects/{project_id}/generate", generation_data)
        generation_time = time.time() - start_time
        
        if not response:
            self.log_result(f"Advanced Mode Generation - {test_name}", False, "No response received")
            return None
        
        if response.status_code != 200:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result(f"Advanced Mode Generation - {test_name}", False, f"HTTP {response.status_code}: {error_msg}")
            return None
        
        data = response.json()
        
        # Analyze generated code
        html_code = data.get("html_code", "")
        css_code = data.get("css_code", "")
        js_code = data.get("js_code", "")
        react_code = data.get("react_code", "")
        backend_code = data.get("backend_code", "")
        all_files = data.get("all_files", {})
        
        # Calculate lengths
        html_length = len(html_code) if html_code else 0
        css_length = len(css_code) if css_code else 0
        react_length = len(react_code) if react_code else 0
        total_length = html_length + css_length + react_length
        files_count = len(all_files) if all_files else 0
        
        print(f"   📊 Generation Results:")
        print(f"   ⏱️  Generation Time: {generation_time:.1f}s")
        print(f"   📄 HTML Length: {html_length} chars")
        print(f"   🎨 CSS Length: {css_length} chars")
        print(f"   ⚛️  React Length: {react_length} chars")
        print(f"   📁 Files Count: {files_count}")
        print(f"   📊 Total Code: {total_length} chars")
        
        # Success criteria from review request
        success_criteria = {
            "HTML > 200 chars": html_length > 200,
            "CSS > 300 chars": css_length > 300,
            "React > 1000 chars": react_length > 1000,
            "Files >= 3": files_count >= 3,
            "Generation < 30s": generation_time < 30.0
        }
        
        all_passed = all(success_criteria.values())
        
        criteria_msg = ", ".join([f"{k}: {'✅' if v else '❌'}" for k, v in success_criteria.items()])
        
        if all_passed:
            self.log_result(f"Advanced Mode Generation - {test_name}", True, 
                          f"Time: {generation_time:.1f}s, HTML: {html_length}, CSS: {css_length}, React: {react_length}, Files: {files_count}")
        else:
            self.log_result(f"Advanced Mode Generation - {test_name}", False, 
                          f"Criteria not met: {criteria_msg}")
        
        return data

    def test_quick_mode_generation(self, project_id: str, description: str, test_name: str):
        """Test quick mode generation for comparison"""
        print(f"\n⚡ Testing Quick Mode Generation - {test_name}...")
        
        generation_data = {
            "description": description,
            "type": "web_app",
            "framework": "react",
            "advanced_mode": False
        }
        
        start_time = time.time()
        response = self.make_request("POST", f"/projects/{project_id}/generate", generation_data)
        generation_time = time.time() - start_time
        
        if not response:
            self.log_result(f"Quick Mode Generation - {test_name}", False, "No response received")
            return None
        
        if response.status_code != 200:
            error_msg = response.json().get("detail", "Unknown error") if response else "No response"
            self.log_result(f"Quick Mode Generation - {test_name}", False, f"HTTP {response.status_code}: {error_msg}")
            return None
        
        data = response.json()
        
        # Analyze generated code
        html_code = data.get("html_code", "")
        css_code = data.get("css_code", "")
        react_code = data.get("react_code", "")
        total_length = len(html_code or "") + len(css_code or "") + len(react_code or "")
        
        print(f"   📊 Quick Mode Results:")
        print(f"   ⏱️  Generation Time: {generation_time:.1f}s")
        print(f"   📊 Total Code: {total_length} chars")
        
        # Quick mode should generate some code
        if total_length > 500:
            self.log_result(f"Quick Mode Generation - {test_name}", True, 
                          f"Time: {generation_time:.1f}s, Total: {total_length} chars")
        else:
            self.log_result(f"Quick Mode Generation - {test_name}", False, 
                          f"Insufficient code generated: {total_length} chars")
        
        return data

    def run_comprehensive_advanced_mode_tests(self):
        """Run comprehensive advanced mode tests as requested in review"""
        print("🎯 RE-TEST BACKEND MODE AVANCÉ - Vérification Correction")
        print("=" * 60)
        
        # Test authentication
        if not self.test_authentication():
            print("❌ Authentication failed, cannot continue tests")
            return False
        
        # Test scenarios from review request
        test_scenarios = [
            {
                "name": "Simple Counter",
                "description": "Application React simple avec compteur",
                "expected_complexity": "simple"
            },
            {
                "name": "Todo List",
                "description": "Application de gestion de tâches avec ajout, suppression et marquage comme terminé",
                "expected_complexity": "medium"
            },
            {
                "name": "E-commerce Complex",
                "description": "Application e-commerce avec panier, paiement et authentification",
                "expected_complexity": "complex"
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n{'='*60}")
            print(f"🧪 Testing Scenario: {scenario['name']}")
            print(f"📝 Description: {scenario['description']}")
            
            # Create project for this scenario
            project_id = self.test_create_project(
                f"Test {scenario['name']}", 
                scenario['description']
            )
            
            if not project_id:
                continue
            
            # Test Advanced Mode
            advanced_result = self.test_advanced_mode_generation(
                project_id, 
                scenario['description'], 
                scenario['name']
            )
            
            # Test Quick Mode for comparison
            quick_project_id = self.test_create_project(
                f"Quick {scenario['name']}", 
                scenario['description']
            )
            
            if quick_project_id:
                quick_result = self.test_quick_mode_generation(
                    quick_project_id, 
                    scenario['description'], 
                    scenario['name']
                )
                
                # Compare results
                if advanced_result and quick_result:
                    self.compare_modes(advanced_result, quick_result, scenario['name'])
        
        # Print final results
        self.print_final_results()
        
        return self.results["failed"] == 0

    def compare_modes(self, advanced_result: Dict, quick_result: Dict, scenario_name: str):
        """Compare advanced vs quick mode results"""
        print(f"\n📊 Comparing Advanced vs Quick Mode - {scenario_name}")
        
        # Extract lengths
        adv_html = len(advanced_result.get("html_code", "") or "")
        adv_css = len(advanced_result.get("css_code", "") or "")
        adv_react = len(advanced_result.get("react_code", "") or "")
        adv_files = len(advanced_result.get("all_files", {}) or {})
        adv_total = adv_html + adv_css + adv_react
        
        quick_html = len(quick_result.get("html_code", "") or "")
        quick_css = len(quick_result.get("css_code", "") or "")
        quick_react = len(quick_result.get("react_code", "") or "")
        quick_total = quick_html + quick_css + quick_react
        
        print(f"   Advanced Mode: {adv_total} chars total, {adv_files} files")
        print(f"   Quick Mode:    {quick_total} chars total")
        
        # Advanced should generally produce more comprehensive code
        if adv_total >= quick_total and adv_files >= 3:
            self.log_result(f"Mode Comparison - {scenario_name}", True, 
                          f"Advanced mode produces more comprehensive results")
        else:
            self.log_result(f"Mode Comparison - {scenario_name}", False, 
                          f"Advanced mode should produce more comprehensive results")

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "="*60)
        print("🎯 FINAL TEST RESULTS - MODE AVANCÉ")
        print("="*60)
        
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.results["errors"]:
            print(f"\n❌ Failed Tests:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        # Determine overall status
        if success_rate >= 80:
            print(f"\n🎉 ADVANCED MODE TESTING: SUCCESS")
            print(f"   Mode avancé génère maintenant du code NON VIDE!")
        else:
            print(f"\n🚨 ADVANCED MODE TESTING: NEEDS ATTENTION")
            print(f"   Des problèmes persistent avec le mode avancé")

if __name__ == "__main__":
    tester = AdvancedModeAPITester()
    success = tester.run_comprehensive_advanced_mode_tests()
    sys.exit(0 if success else 1)