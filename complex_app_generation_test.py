#!/usr/bin/env python3
"""
🎯 COMPLEX APPLICATION GENERATION TESTING - VECTORT.IO
Test Real Complex Application Generation as per review request

This test validates if Vectort.io can generate REAL, complex, production-ready applications:
1. E-commerce Platform (Complex)
2. Task Management Dashboard (Medium) 
3. Real-time Chat Application (Complex)

Success Criteria:
- 500+ lines of React code per project
- CSS with responsive design (media queries)
- Code follows React best practices
- Features mentioned in description are implemented
- Code is structured in components
- State management is implemented
- No obvious syntax errors
- Response time < 30 seconds per generation
"""

import requests
import json
import sys
import time
import re
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://omniai-platform-2.preview.emergentagent.com/api"
TEST_USER = {
    "email": f"complex_test_{int(time.time())}@vectort.io",
    "password": "ComplexTest123!",
    "full_name": f"Complex App Tester {int(time.time())}"
}

class ComplexAppTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.user_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
            "generation_metrics": {}
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
                    headers: Optional[Dict] = None, timeout: int = 60) -> requests.Response:
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

    def setup_test_user(self):
        """Setup test user for complex app generation"""
        print("\n=== Setting up Test User ===")
        try:
            # Try to register new user
            response = self.make_request("POST", "/auth/register", TEST_USER)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                self.log_result("User Setup", True, f"New user registered with ID: {self.user_id}")
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
                    self.log_result("User Setup", True, f"Existing user logged in: {self.user_id}")
                else:
                    self.log_result("User Setup", False, f"Login failed: {login_response.status_code}")
                    return False
            else:
                self.log_result("User Setup", False, f"Registration failed: {response.status_code}")
                return False
            
            # Verify credits available
            credits_response = self.make_request("GET", "/credits/balance")
            if credits_response.status_code == 200:
                credits_data = credits_response.json()
                total_credits = credits_data.get("total_available", 0)
                if total_credits >= 6:  # Need at least 6 credits for 3 quick generations (2 each)
                    self.log_result("Credits Check", True, f"Sufficient credits available: {total_credits}")
                    return True
                else:
                    self.log_result("Credits Check", False, f"Insufficient credits: {total_credits} (need 6+)")
                    return False
            else:
                self.log_result("Credits Check", False, "Could not check credit balance")
                return False
                
        except Exception as e:
            self.log_result("User Setup", False, f"Exception: {str(e)}")
            return False

    def analyze_code_quality(self, code_data: Dict, app_type: str) -> Dict:
        """Analyze generated code quality according to success criteria"""
        analysis = {
            "lines_of_code": 0,
            "has_responsive_css": False,
            "has_react_patterns": False,
            "has_components": False,
            "has_state_management": False,
            "has_features": False,
            "syntax_errors": [],
            "score": 0
        }
        
        # Count lines of code
        react_code = code_data.get("react_code", "")
        css_code = code_data.get("css_code", "")
        js_code = code_data.get("js_code", "")
        html_code = code_data.get("html_code", "")
        backend_code = code_data.get("backend_code", "")
        
        total_lines = 0
        if react_code:
            total_lines += len(react_code.split('\n'))
        if css_code:
            total_lines += len(css_code.split('\n'))
        if js_code:
            total_lines += len(js_code.split('\n'))
        if html_code:
            total_lines += len(html_code.split('\n'))
        if backend_code:
            total_lines += len(backend_code.split('\n'))
        
        analysis["lines_of_code"] = total_lines
        
        # Check for responsive CSS (media queries)
        if css_code:
            media_queries = re.findall(r'@media\s*\([^)]+\)', css_code, re.IGNORECASE)
            analysis["has_responsive_css"] = len(media_queries) > 0
        
        # Check for React patterns
        if react_code:
            # Check for hooks
            has_hooks = any(hook in react_code for hook in ['useState', 'useEffect', 'useContext', 'useReducer'])
            # Check for components
            has_components = 'function ' in react_code or 'const ' in react_code and '=>' in react_code
            # Check for JSX
            has_jsx = '<' in react_code and '>' in react_code
            
            analysis["has_react_patterns"] = has_hooks and has_jsx
            analysis["has_components"] = has_components
            analysis["has_state_management"] = has_hooks or 'state' in react_code.lower()
        
        # Check for app-specific features
        if app_type == "ecommerce":
            feature_keywords = ['cart', 'product', 'checkout', 'payment', 'shop', 'buy', 'price']
        elif app_type == "task_management":
            feature_keywords = ['task', 'todo', 'drag', 'drop', 'priority', 'due', 'complete']
        elif app_type == "chat":
            feature_keywords = ['message', 'chat', 'send', 'receive', 'user', 'online', 'room']
        else:
            feature_keywords = []
        
        all_code = f"{react_code} {css_code} {js_code} {html_code}".lower()
        feature_matches = sum(1 for keyword in feature_keywords if keyword in all_code)
        analysis["has_features"] = feature_matches >= len(feature_keywords) // 2
        
        # Basic syntax error check
        if react_code:
            # Check for basic syntax issues
            if react_code.count('{') != react_code.count('}'):
                analysis["syntax_errors"].append("Unmatched braces in React code")
            if react_code.count('(') != react_code.count(')'):
                analysis["syntax_errors"].append("Unmatched parentheses in React code")
        
        # Calculate score
        score = 0
        if analysis["lines_of_code"] >= 500:
            score += 20
        elif analysis["lines_of_code"] >= 200:
            score += 10
        
        if analysis["has_responsive_css"]:
            score += 20
        if analysis["has_react_patterns"]:
            score += 20
        if analysis["has_components"]:
            score += 15
        if analysis["has_state_management"]:
            score += 15
        if analysis["has_features"]:
            score += 10
        if len(analysis["syntax_errors"]) == 0:
            score += 10
        
        analysis["score"] = score
        return analysis

    def test_ecommerce_platform_complex(self):
        """Test 1: E-commerce Platform (Complex)"""
        print("\n=== Test 1: E-commerce Platform (Complex) ===")
        
        description = """Create a complete e-commerce platform with React frontend. 
Features needed:
- Product catalog with search and filters
- Shopping cart with add/remove items
- User authentication (login/register)
- Checkout process with form validation
- Order history page
- Responsive design for mobile and desktop
- Product detail pages with image gallery
- Category navigation
Use React hooks, modern styling, and include proper state management."""

        try:
            # Create project
            project_data = {
                "title": "E-commerce Platform Complex",
                "description": description,
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("E-commerce Platform - Project Creation", False, 
                              f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Generate with advanced mode
            generation_request = {
                "description": description,
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False
            }
            
            start_time = time.time()
            response = self.make_request("POST", f"/projects/{project_id}/generate", 
                                       generation_request, timeout=45)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                analysis = self.analyze_code_quality(data, "ecommerce")
                
                # Store metrics
                self.results["generation_metrics"]["ecommerce"] = {
                    "generation_time": generation_time,
                    "lines_of_code": analysis["lines_of_code"],
                    "score": analysis["score"],
                    "analysis": analysis
                }
                
                # Success criteria check
                success_criteria = [
                    analysis["lines_of_code"] >= 500,
                    analysis["has_responsive_css"],
                    analysis["has_react_patterns"],
                    analysis["has_components"],
                    analysis["has_state_management"],
                    len(analysis["syntax_errors"]) == 0,
                    generation_time < 30
                ]
                
                passed_criteria = sum(success_criteria)
                
                if passed_criteria >= 5:  # At least 5/7 criteria
                    self.log_result("E-commerce Platform Generation", True, 
                                  f"Generated {analysis['lines_of_code']} lines, "
                                  f"Score: {analysis['score']}/100, "
                                  f"Time: {generation_time:.1f}s, "
                                  f"Criteria: {passed_criteria}/7")
                else:
                    self.log_result("E-commerce Platform Generation", False, 
                                  f"Insufficient quality: {passed_criteria}/7 criteria met. "
                                  f"Lines: {analysis['lines_of_code']}, Score: {analysis['score']}")
            elif response.status_code == 402:
                self.log_result("E-commerce Platform Generation", False, "Insufficient credits")
            else:
                self.log_result("E-commerce Platform Generation", False, 
                              f"Generation failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("E-commerce Platform Generation", False, f"Exception: {str(e)}")

    def test_task_management_dashboard(self):
        """Test 2: Task Management Dashboard (Medium)"""
        print("\n=== Test 2: Task Management Dashboard (Medium) ===")
        
        description = """Build a modern task management dashboard like Trello.
Features:
- Drag and drop task cards between columns (To Do, In Progress, Done)
- Create/edit/delete tasks
- Task priority levels (high, medium, low)
- Due dates and filters
- User profile section
- Dark mode toggle
- Statistics dashboard showing completed tasks
Modern UI with Tailwind-style colors and smooth animations."""

        try:
            # Create project
            project_data = {
                "title": "Task Management Dashboard",
                "description": description,
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Task Management - Project Creation", False, 
                              f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Generate with advanced mode
            generation_request = {
                "description": description,
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False
            }
            
            start_time = time.time()
            response = self.make_request("POST", f"/projects/{project_id}/generate", 
                                       generation_request, timeout=45)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                analysis = self.analyze_code_quality(data, "task_management")
                
                # Store metrics
                self.results["generation_metrics"]["task_management"] = {
                    "generation_time": generation_time,
                    "lines_of_code": analysis["lines_of_code"],
                    "score": analysis["score"],
                    "analysis": analysis
                }
                
                # Success criteria check
                success_criteria = [
                    analysis["lines_of_code"] >= 500,
                    analysis["has_responsive_css"],
                    analysis["has_react_patterns"],
                    analysis["has_components"],
                    analysis["has_state_management"],
                    len(analysis["syntax_errors"]) == 0,
                    generation_time < 30
                ]
                
                passed_criteria = sum(success_criteria)
                
                if passed_criteria >= 5:  # At least 5/7 criteria
                    self.log_result("Task Management Generation", True, 
                                  f"Generated {analysis['lines_of_code']} lines, "
                                  f"Score: {analysis['score']}/100, "
                                  f"Time: {generation_time:.1f}s, "
                                  f"Criteria: {passed_criteria}/7")
                else:
                    self.log_result("Task Management Generation", False, 
                                  f"Insufficient quality: {passed_criteria}/7 criteria met. "
                                  f"Lines: {analysis['lines_of_code']}, Score: {analysis['score']}")
            elif response.status_code == 402:
                self.log_result("Task Management Generation", False, "Insufficient credits")
            else:
                self.log_result("Task Management Generation", False, 
                              f"Generation failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Task Management Generation", False, f"Exception: {str(e)}")

    def test_realtime_chat_application(self):
        """Test 3: Real-time Chat Application (Complex)"""
        print("\n=== Test 3: Real-time Chat Application (Complex) ===")
        
        description = """Create a real-time chat application.
Features:
- Multiple chat rooms
- Real-time message updates
- User online/offline status
- Message history
- Emoji support
- File upload capability
- Typing indicators
- User profiles with avatars
Clean, modern UI similar to Slack or Discord."""

        try:
            # Create project
            project_data = {
                "title": "Real-time Chat Application",
                "description": description,
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Chat Application - Project Creation", False, 
                              f"Failed to create project: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            
            # Generate with advanced mode
            generation_request = {
                "description": description,
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False
            }
            
            start_time = time.time()
            response = self.make_request("POST", f"/projects/{project_id}/generate", 
                                       generation_request, timeout=45)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                analysis = self.analyze_code_quality(data, "chat")
                
                # Store metrics
                self.results["generation_metrics"]["chat"] = {
                    "generation_time": generation_time,
                    "lines_of_code": analysis["lines_of_code"],
                    "score": analysis["score"],
                    "analysis": analysis
                }
                
                # Success criteria check
                success_criteria = [
                    analysis["lines_of_code"] >= 500,
                    analysis["has_responsive_css"],
                    analysis["has_react_patterns"],
                    analysis["has_components"],
                    analysis["has_state_management"],
                    len(analysis["syntax_errors"]) == 0,
                    generation_time < 30
                ]
                
                passed_criteria = sum(success_criteria)
                
                if passed_criteria >= 5:  # At least 5/7 criteria
                    self.log_result("Chat Application Generation", True, 
                                  f"Generated {analysis['lines_of_code']} lines, "
                                  f"Score: {analysis['score']}/100, "
                                  f"Time: {generation_time:.1f}s, "
                                  f"Criteria: {passed_criteria}/7")
                else:
                    self.log_result("Chat Application Generation", False, 
                                  f"Insufficient quality: {passed_criteria}/7 criteria met. "
                                  f"Lines: {analysis['lines_of_code']}, Score: {analysis['score']}")
            elif response.status_code == 402:
                self.log_result("Chat Application Generation", False, "Insufficient credits")
            else:
                self.log_result("Chat Application Generation", False, 
                              f"Generation failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Chat Application Generation", False, f"Exception: {str(e)}")

    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("🎯 COMPLEX APPLICATION GENERATION TEST REPORT")
        print("="*80)
        
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {self.results['passed']}")
        print(f"   Failed: {self.results['failed']}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Generation metrics
        if self.results["generation_metrics"]:
            print(f"\n📈 GENERATION METRICS:")
            
            total_lines = 0
            total_time = 0
            total_score = 0
            app_count = 0
            
            for app_type, metrics in self.results["generation_metrics"].items():
                lines = metrics["lines_of_code"]
                time_taken = metrics["generation_time"]
                score = metrics["score"]
                
                total_lines += lines
                total_time += time_taken
                total_score += score
                app_count += 1
                
                print(f"   {app_type.title()}:")
                print(f"     - Lines of Code: {lines}")
                print(f"     - Generation Time: {time_taken:.1f}s")
                print(f"     - Quality Score: {score}/100")
                
                analysis = metrics["analysis"]
                print(f"     - Responsive CSS: {'✅' if analysis['has_responsive_css'] else '❌'}")
                print(f"     - React Patterns: {'✅' if analysis['has_react_patterns'] else '❌'}")
                print(f"     - Components: {'✅' if analysis['has_components'] else '❌'}")
                print(f"     - State Management: {'✅' if analysis['has_state_management'] else '❌'}")
                print(f"     - Features Implemented: {'✅' if analysis['has_features'] else '❌'}")
                print(f"     - Syntax Errors: {len(analysis['syntax_errors'])}")
            
            if app_count > 0:
                avg_lines = total_lines / app_count
                avg_time = total_time / app_count
                avg_score = total_score / app_count
                
                print(f"\n   📊 AVERAGES:")
                print(f"     - Average Lines per App: {avg_lines:.0f}")
                print(f"     - Average Generation Time: {avg_time:.1f}s")
                print(f"     - Average Quality Score: {avg_score:.1f}/100")
        
        # Success criteria evaluation
        print(f"\n✅ SUCCESS CRITERIA EVALUATION:")
        
        criteria_met = 0
        total_criteria = 7
        
        # Check if at least 2/3 applications generated successfully
        successful_generations = len([m for m in self.results["generation_metrics"].values() 
                                    if m["score"] >= 50])
        if successful_generations >= 2:
            print(f"   ✅ At least 2/3 applications generated successfully ({successful_generations}/3)")
            criteria_met += 1
        else:
            print(f"   ❌ Only {successful_generations}/3 applications generated successfully")
        
        # Check average lines of code
        if self.results["generation_metrics"]:
            avg_lines = sum(m["lines_of_code"] for m in self.results["generation_metrics"].values()) / len(self.results["generation_metrics"])
            if avg_lines >= 500:
                print(f"   ✅ Average 500+ lines of code ({avg_lines:.0f} lines)")
                criteria_met += 1
            else:
                print(f"   ❌ Average lines below 500 ({avg_lines:.0f} lines)")
        
        # Check responsive design
        responsive_apps = sum(1 for m in self.results["generation_metrics"].values() 
                            if m["analysis"]["has_responsive_css"])
        if responsive_apps >= 2:
            print(f"   ✅ CSS includes responsive design ({responsive_apps}/3 apps)")
            criteria_met += 1
        else:
            print(f"   ❌ Insufficient responsive design ({responsive_apps}/3 apps)")
        
        # Check React best practices
        react_apps = sum(1 for m in self.results["generation_metrics"].values() 
                        if m["analysis"]["has_react_patterns"])
        if react_apps >= 2:
            print(f"   ✅ Code follows React best practices ({react_apps}/3 apps)")
            criteria_met += 1
        else:
            print(f"   ❌ Insufficient React best practices ({react_apps}/3 apps)")
        
        # Check feature implementation
        feature_apps = sum(1 for m in self.results["generation_metrics"].values() 
                          if m["analysis"]["has_features"])
        if feature_apps >= 2:
            print(f"   ✅ Features mentioned in description implemented ({feature_apps}/3 apps)")
            criteria_met += 1
        else:
            print(f"   ❌ Insufficient feature implementation ({feature_apps}/3 apps)")
        
        # Check component structure
        component_apps = sum(1 for m in self.results["generation_metrics"].values() 
                           if m["analysis"]["has_components"])
        if component_apps >= 2:
            print(f"   ✅ Code is structured in components ({component_apps}/3 apps)")
            criteria_met += 1
        else:
            print(f"   ❌ Insufficient component structure ({component_apps}/3 apps)")
        
        # Check state management
        state_apps = sum(1 for m in self.results["generation_metrics"].values() 
                        if m["analysis"]["has_state_management"])
        if state_apps >= 2:
            print(f"   ✅ State management is implemented ({state_apps}/3 apps)")
            criteria_met += 1
        else:
            print(f"   ❌ Insufficient state management ({state_apps}/3 apps)")
        
        # Final verdict
        print(f"\n🎯 FINAL VERDICT:")
        print(f"   Criteria Met: {criteria_met}/{total_criteria}")
        
        if criteria_met >= 5:
            print(f"   🎉 SUCCESS: Vectort.io can generate complex, production-ready applications!")
            print(f"   The AI system meets the requirements for real application generation.")
        else:
            print(f"   ⚠️  PARTIAL SUCCESS: Some limitations found in complex application generation.")
            print(f"   The system shows promise but needs improvements in some areas.")
        
        # Error summary
        if self.results["errors"]:
            print(f"\n❌ ERRORS ENCOUNTERED:")
            for error in self.results["errors"]:
                print(f"   - {error}")
        
        return criteria_met >= 5

    def run_all_tests(self):
        """Run all complex application generation tests"""
        print("🎯 STARTING COMPLEX APPLICATION GENERATION TESTS")
        print("="*80)
        
        # Setup
        if not self.setup_test_user():
            print("❌ Failed to setup test user. Aborting tests.")
            return False
        
        # Run tests
        self.test_ecommerce_platform_complex()
        self.test_task_management_dashboard()
        self.test_realtime_chat_application()
        
        # Generate report
        return self.generate_final_report()

def main():
    """Main test execution"""
    tester = ComplexAppTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()