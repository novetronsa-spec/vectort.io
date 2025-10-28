#!/usr/bin/env python3
"""
🎯 FOCUSED JAVASCRIPT GENERATION TEST - Mode Avancé vs Mode Rapide

Test spécifique pour identifier pourquoi le mode avancé retourne du code vide
alors que le mode rapide fonctionne.
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://devstream-ai.preview.emergentagent.com/api"

class FocusedJSTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.user_id = None
        self.results = []

    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        self.results.append({"test": test_name, "success": success, "message": message})

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    headers: Optional[Dict] = None, timeout: int = 180) -> requests.Response:
        """Make HTTP request"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
        if self.access_token and "Authorization" not in default_headers:
            default_headers["Authorization"] = f"Bearer {self.access_token}"
        
        if method.upper() == "GET":
            response = requests.get(url, headers=default_headers, timeout=timeout)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=default_headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response

    def setup_user_with_credits(self):
        """Setup user with sufficient credits"""
        print("\n=== SETUP: User with Credits ===")
        
        # Use existing user with credits
        test_user = {
            "email": "josephayingono@gmail.com",  # User with 5127 credits
            "password": "TestPassword123!"
        }
        
        try:
            response = self.make_request("POST", "/auth/login", test_user)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                
                # Check credits
                balance_response = self.make_request("GET", "/credits/balance")
                if balance_response.status_code == 200:
                    balance = balance_response.json()
                    credits = balance.get("total_available", 0)
                    self.log_result("User Setup", True, f"User logged in with {credits} credits")
                    return credits >= 7
                else:
                    self.log_result("User Setup", False, "Cannot check credit balance")
                    return False
            else:
                self.log_result("User Setup", False, f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("User Setup", False, f"Exception: {str(e)}")
            return False

    def test_quick_mode_detailed(self):
        """Test Quick Mode with detailed analysis"""
        print("\n=== Test: Mode Rapide (Détaillé) ===")
        
        try:
            # Create project
            project_data = {
                "title": "Test Mode Rapide Détaillé",
                "description": "Application React simple avec compteur",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Quick Mode - Project Creation", False, f"Failed: {project_response.status_code}")
                return None
            
            project_id = project_response.json()["id"]
            
            # Generate with Quick Mode
            generation_request = {
                "description": "Application React simple avec compteur",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False
            }
            
            start_time = time.time()
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Detailed analysis
                html_code = data.get("html_code", "")
                css_code = data.get("css_code", "")
                js_code = data.get("js_code", "")
                react_code = data.get("react_code", "")
                backend_code = data.get("backend_code", "")
                all_files = data.get("all_files", {})
                
                analysis = {
                    "html_length": len(html_code),
                    "css_length": len(css_code),
                    "js_length": len(js_code),
                    "react_length": len(react_code),
                    "backend_length": len(backend_code),
                    "all_files_count": len(all_files),
                    "generation_time": generation_time
                }
                
                has_content = any([html_code, css_code, js_code, react_code, backend_code])
                
                if has_content:
                    self.log_result("Quick Mode Generation", True, 
                                  f"✅ SUCCESS - HTML:{analysis['html_length']}, CSS:{analysis['css_length']}, "
                                  f"React:{analysis['react_length']}, JS:{analysis['js_length']}, "
                                  f"Backend:{analysis['backend_length']}, Files:{analysis['all_files_count']}, "
                                  f"Time:{analysis['generation_time']:.1f}s")
                    return project_id
                else:
                    self.log_result("Quick Mode Generation", False, "❌ No content generated")
                    return None
            else:
                self.log_result("Quick Mode Generation", False, f"❌ Failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Quick Mode Generation", False, f"Exception: {str(e)}")
            return None

    def test_advanced_mode_detailed(self):
        """Test Advanced Mode with detailed analysis"""
        print("\n=== Test: Mode Avancé (Détaillé) ===")
        
        try:
            # Create project
            project_data = {
                "title": "Test Mode Avancé Détaillé",
                "description": "Application React simple avec compteur",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Advanced Mode - Project Creation", False, f"Failed: {project_response.status_code}")
                return None
            
            project_id = project_response.json()["id"]
            
            # Generate with Advanced Mode
            generation_request = {
                "description": "Application React simple avec compteur",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": True  # ADVANCED MODE
            }
            
            start_time = time.time()
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Detailed analysis
                html_code = data.get("html_code", "")
                css_code = data.get("css_code", "")
                js_code = data.get("js_code", "")
                react_code = data.get("react_code", "")
                backend_code = data.get("backend_code", "")
                all_files = data.get("all_files", {})
                
                # Additional advanced mode fields
                project_structure = data.get("project_structure", {})
                package_json = data.get("package_json", "")
                requirements_txt = data.get("requirements_txt", "")
                dockerfile = data.get("dockerfile", "")
                readme = data.get("readme", "")
                
                analysis = {
                    "html_length": len(html_code),
                    "css_length": len(css_code),
                    "js_length": len(js_code),
                    "react_length": len(react_code),
                    "backend_length": len(backend_code),
                    "all_files_count": len(all_files),
                    "package_json_length": len(package_json),
                    "readme_length": len(readme),
                    "generation_time": generation_time
                }
                
                has_main_content = any([html_code, css_code, js_code, react_code, backend_code])
                has_advanced_content = any([package_json, readme, dockerfile])
                
                if has_main_content:
                    self.log_result("Advanced Mode Generation", True, 
                                  f"✅ SUCCESS - HTML:{analysis['html_length']}, CSS:{analysis['css_length']}, "
                                  f"React:{analysis['react_length']}, JS:{analysis['js_length']}, "
                                  f"Backend:{analysis['backend_length']}, Files:{analysis['all_files_count']}, "
                                  f"Package.json:{analysis['package_json_length']}, README:{analysis['readme_length']}, "
                                  f"Time:{analysis['generation_time']:.1f}s")
                    return project_id
                elif has_advanced_content:
                    self.log_result("Advanced Mode Generation", False, 
                                  f"⚠️ PARTIAL - Only advanced files generated: Package.json:{analysis['package_json_length']}, "
                                  f"README:{analysis['readme_length']}, but NO main code files")
                    return project_id
                else:
                    self.log_result("Advanced Mode Generation", False, 
                                  f"❌ CRITICAL - NO CONTENT: all_files:{analysis['all_files_count']}, "
                                  f"Time:{analysis['generation_time']:.1f}s")
                    
                    # Print all_files content for debugging
                    if all_files:
                        print(f"   🔍 all_files keys: {list(all_files.keys())}")
                        for key, value in all_files.items():
                            print(f"      {key}: {len(str(value))} chars")
                    else:
                        print("   🔍 all_files is empty or None")
                    
                    return None
            else:
                self.log_result("Advanced Mode Generation", False, f"❌ Failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Advanced Mode Generation", False, f"Exception: {str(e)}")
            return None

    def test_code_retrieval_comparison(self, quick_project_id, advanced_project_id):
        """Compare code retrieval between quick and advanced mode"""
        print("\n=== Test: Code Retrieval Comparison ===")
        
        if not quick_project_id and not advanced_project_id:
            self.log_result("Code Retrieval Comparison", False, "No project IDs available")
            return
        
        results = {}
        
        # Test Quick Mode retrieval
        if quick_project_id:
            try:
                response = self.make_request("GET", f"/projects/{quick_project_id}/code")
                if response.status_code == 200:
                    data = response.json()
                    results["quick"] = {
                        "html": len(data.get("html_code", "")),
                        "css": len(data.get("css_code", "")),
                        "react": len(data.get("react_code", "")),
                        "all_files": len(data.get("all_files", {}))
                    }
                    self.log_result("Quick Mode Code Retrieval", True, f"Retrieved: {results['quick']}")
                else:
                    self.log_result("Quick Mode Code Retrieval", False, f"Failed: {response.status_code}")
            except Exception as e:
                self.log_result("Quick Mode Code Retrieval", False, f"Exception: {str(e)}")
        
        # Test Advanced Mode retrieval
        if advanced_project_id:
            try:
                response = self.make_request("GET", f"/projects/{advanced_project_id}/code")
                if response.status_code == 200:
                    data = response.json()
                    results["advanced"] = {
                        "html": len(data.get("html_code", "")),
                        "css": len(data.get("css_code", "")),
                        "react": len(data.get("react_code", "")),
                        "all_files": len(data.get("all_files", {}))
                    }
                    self.log_result("Advanced Mode Code Retrieval", True, f"Retrieved: {results['advanced']}")
                else:
                    self.log_result("Advanced Mode Code Retrieval", False, f"Failed: {response.status_code}")
            except Exception as e:
                self.log_result("Advanced Mode Code Retrieval", False, f"Exception: {str(e)}")
        
        # Compare results
        if "quick" in results and "advanced" in results:
            quick_total = sum(results["quick"].values())
            advanced_total = sum(results["advanced"].values())
            
            if advanced_total == 0 and quick_total > 0:
                self.log_result("Comparison Analysis", False, 
                              f"❌ CRITICAL: Quick mode works ({quick_total} chars) but Advanced mode is empty ({advanced_total} chars)")
            elif advanced_total > 0 and quick_total > 0:
                self.log_result("Comparison Analysis", True, 
                              f"✅ Both modes work: Quick({quick_total} chars), Advanced({advanced_total} chars)")
            else:
                self.log_result("Comparison Analysis", False, 
                              f"⚠️ Both modes have issues: Quick({quick_total} chars), Advanced({advanced_total} chars)")

    def run_focused_test(self):
        """Run focused JavaScript generation test"""
        print("🎯 FOCUSED JAVASCRIPT GENERATION TEST - Mode Avancé vs Mode Rapide")
        print("=" * 80)
        
        # Setup
        if not self.setup_user_with_credits():
            print("❌ Cannot proceed without sufficient credits")
            return
        
        # Run tests
        quick_project_id = self.test_quick_mode_detailed()
        advanced_project_id = self.test_advanced_mode_detailed()
        
        # Compare results
        self.test_code_retrieval_comparison(quick_project_id, advanced_project_id)
        
        # Final analysis
        self.print_analysis()

    def print_analysis(self):
        """Print final analysis"""
        print("\n" + "=" * 80)
        print("🎯 ANALYSE FINALE")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if r["success"])
        failed = len(self.results) - passed
        
        print(f"✅ Tests réussis: {passed}")
        print(f"❌ Tests échoués: {failed}")
        
        # Check for critical issues
        critical_issues = []
        for result in self.results:
            if not result["success"] and ("CRITICAL" in result["message"] or "NO CONTENT" in result["message"]):
                critical_issues.append(result)
        
        if critical_issues:
            print(f"\n🚨 PROBLÈMES CRITIQUES IDENTIFIÉS:")
            for issue in critical_issues:
                print(f"   • {issue['test']}: {issue['message']}")
        
        # Recommendations
        print(f"\n💡 RECOMMANDATIONS POUR RÉSOUDRE LE PROBLÈME:")
        print("   1. Vérifier generate_with_multi_agents() dans multi_agent_orchestrator.py")
        print("   2. Vérifier map_multi_agent_files_to_response() dans server.py")
        print("   3. Analyser les logs backend pour les timeouts ou erreurs LLM")
        print("   4. Tester JavaScriptOptimizer directement")
        print("   5. Vérifier les fallback mechanisms")

if __name__ == "__main__":
    tester = FocusedJSTest()
    tester.run_focused_test()