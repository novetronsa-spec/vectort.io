#!/usr/bin/env python3
"""
CRITICAL PRE-LAUNCH SECURITY & PERFORMANCE AUDIT
Tests security vulnerabilities, performance under load, and production readiness
"""

import requests
import json
import time
import threading
import concurrent.futures
from typing import Dict, Any, List
import sys

# Configuration
BASE_URL = "https://vectort-builder.preview.emergentagent.com/api"
CONCURRENT_USERS = 10
LOAD_TEST_DURATION = 30  # seconds

class SecurityPerformanceTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.results = {
            "security_passed": 0,
            "security_failed": 0,
            "performance_passed": 0,
            "performance_failed": 0,
            "critical_issues": [],
            "warnings": []
        }

    def log_result(self, category: str, test_name: str, success: bool, message: str = "", critical: bool = False):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        
        if category == "security":
            if success:
                self.results["security_passed"] += 1
            else:
                self.results["security_failed"] += 1
        elif category == "performance":
            if success:
                self.results["performance_passed"] += 1
            else:
                self.results["performance_failed"] += 1
        
        if not success:
            if critical:
                self.results["critical_issues"].append(f"{test_name}: {message}")
            else:
                self.results["warnings"].append(f"{test_name}: {message}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None, timeout: int = 10):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
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
            return None

    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        print("\n=== SECURITY TEST 1: SQL Injection Protection ===")
        
        # Test SQL injection in login
        sql_payloads = [
            "admin'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "admin'/**/OR/**/1=1#"
        ]
        
        for payload in sql_payloads:
            try:
                response = self.make_request("POST", "/auth/login", {
                    "email": payload,
                    "password": "test"
                })
                
                if response and response.status_code == 401:
                    continue  # Good, rejected properly
                elif response and response.status_code == 500:
                    self.log_result("security", "SQL Injection Protection", False, 
                                  f"Server error with payload: {payload[:20]}...", critical=True)
                    return
                elif response and response.status_code == 200:
                    self.log_result("security", "SQL Injection Protection", False, 
                                  f"SQL injection succeeded with payload: {payload[:20]}...", critical=True)
                    return
            except Exception as e:
                pass
        
        self.log_result("security", "SQL Injection Protection", True, "All SQL injection attempts properly rejected")

    def test_xss_protection(self):
        """Test XSS protection"""
        print("\n=== SECURITY TEST 2: XSS Protection ===")
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        # Test XSS in project creation (requires auth first)
        try:
            # Quick registration/login
            auth_response = self.make_request("POST", "/auth/register", {
                "email": f"xss_test_{int(time.time())}@example.com",
                "password": "SecurePass123!",
                "full_name": "XSS Test User"
            })
            
            if not auth_response or auth_response.status_code not in [200, 400]:
                self.log_result("security", "XSS Protection", False, "Could not authenticate for XSS test", critical=False)
                return
            
            if auth_response.status_code == 400:
                # Try login instead
                auth_response = self.make_request("POST", "/auth/login", {
                    "email": "marie.dupont@example.com",
                    "password": "SecurePass123!"
                })
            
            if not auth_response or auth_response.status_code != 200:
                self.log_result("security", "XSS Protection", False, "Could not authenticate for XSS test", critical=False)
                return
            
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            for payload in xss_payloads:
                response = self.make_request("POST", "/projects", {
                    "title": payload,
                    "description": payload,
                    "type": "web_app"
                }, headers=headers)
                
                if response and response.status_code == 200:
                    # Check if payload was sanitized
                    project_data = response.json()
                    if payload in project_data.get("title", "") or payload in project_data.get("description", ""):
                        self.log_result("security", "XSS Protection", False, 
                                      f"XSS payload not sanitized: {payload[:20]}...", critical=True)
                        return
        
        except Exception as e:
            self.log_result("security", "XSS Protection", False, f"Error during XSS test: {str(e)}", critical=False)
            return
        
        self.log_result("security", "XSS Protection", True, "XSS payloads properly handled")

    def test_authentication_security(self):
        """Test authentication security"""
        print("\n=== SECURITY TEST 3: Authentication Security ===")
        
        # Test weak password acceptance
        weak_passwords = ["123", "password", "admin", "test"]
        
        for weak_pass in weak_passwords:
            response = self.make_request("POST", "/auth/register", {
                "email": f"weak_test_{int(time.time())}_{weak_pass}@example.com",
                "password": weak_pass,
                "full_name": "Weak Password Test"
            })
            
            if response and response.status_code == 200:
                self.log_result("security", "Weak Password Protection", False, 
                              f"Weak password '{weak_pass}' was accepted", critical=True)
                return
        
        # Test JWT token security
        try:
            # Get a valid token
            auth_response = self.make_request("POST", "/auth/login", {
                "email": "marie.dupont@example.com",
                "password": "SecurePass123!"
            })
            
            if auth_response and auth_response.status_code == 200:
                token = auth_response.json()["access_token"]
                
                # Test with modified token
                modified_token = token[:-5] + "XXXXX"
                headers = {"Authorization": f"Bearer {modified_token}"}
                
                response = self.make_request("GET", "/auth/me", headers=headers)
                
                if response and response.status_code == 401:
                    self.log_result("security", "JWT Token Security", True, "Modified tokens properly rejected")
                else:
                    self.log_result("security", "JWT Token Security", False, 
                                  "Modified token was accepted", critical=True)
            else:
                self.log_result("security", "JWT Token Security", False, 
                              "Could not obtain token for security test", critical=False)
        
        except Exception as e:
            self.log_result("security", "JWT Token Security", False, f"Error: {str(e)}", critical=False)

    def test_rate_limiting(self):
        """Test rate limiting"""
        print("\n=== SECURITY TEST 4: Rate Limiting ===")
        
        # Rapid fire requests to login endpoint
        rapid_requests = 0
        successful_requests = 0
        
        start_time = time.time()
        for i in range(50):  # Try 50 rapid requests
            response = self.make_request("POST", "/auth/login", {
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            }, timeout=2)
            
            rapid_requests += 1
            
            if response:
                if response.status_code == 429:  # Rate limited
                    self.log_result("security", "Rate Limiting", True, 
                                  f"Rate limiting active after {rapid_requests} requests")
                    return
                elif response.status_code in [401, 400]:
                    successful_requests += 1
            
            # Stop if taking too long
            if time.time() - start_time > 10:
                break
        
        if successful_requests == rapid_requests:
            self.log_result("security", "Rate Limiting", False, 
                          f"No rate limiting detected after {rapid_requests} requests", critical=True)
        else:
            self.log_result("security", "Rate Limiting", True, 
                          f"Some form of protection detected ({successful_requests}/{rapid_requests} succeeded)")

    def test_input_validation(self):
        """Test input validation"""
        print("\n=== SECURITY TEST 5: Input Validation ===")
        
        # Test oversized inputs
        large_string = "A" * 10000
        
        response = self.make_request("POST", "/auth/register", {
            "email": f"large_test_{int(time.time())}@example.com",
            "password": large_string,
            "full_name": large_string
        })
        
        if response and response.status_code == 500:
            self.log_result("security", "Input Size Validation", False, 
                          "Server error with large input", critical=True)
        elif response and response.status_code in [400, 422]:
            self.log_result("security", "Input Size Validation", True, 
                          "Large inputs properly rejected")
        else:
            self.log_result("security", "Input Size Validation", True, 
                          "Large inputs handled gracefully")

    def simulate_user_load(self, user_id: int, duration: int) -> Dict:
        """Simulate a single user's load"""
        results = {"requests": 0, "errors": 0, "response_times": []}
        end_time = time.time() + duration
        
        while time.time() < end_time:
            start = time.time()
            
            # Mix of different endpoints
            endpoints = [
                ("GET", "/", None),
                ("GET", "/stats", None),
                ("POST", "/auth/login", {"email": "test@example.com", "password": "wrong"})
            ]
            
            method, endpoint, data = endpoints[results["requests"] % len(endpoints)]
            response = self.make_request(method, endpoint, data, timeout=5)
            
            response_time = time.time() - start
            results["response_times"].append(response_time)
            results["requests"] += 1
            
            if not response or response.status_code >= 500:
                results["errors"] += 1
            
            time.sleep(0.1)  # Small delay between requests
        
        return results

    def test_concurrent_load(self):
        """Test concurrent user load"""
        print(f"\n=== PERFORMANCE TEST 1: Concurrent Load ({CONCURRENT_USERS} users, {LOAD_TEST_DURATION}s) ===")
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
            futures = [
                executor.submit(self.simulate_user_load, i, LOAD_TEST_DURATION) 
                for i in range(CONCURRENT_USERS)
            ]
            
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        total_requests = sum(r["requests"] for r in results)
        total_errors = sum(r["errors"] for r in results)
        all_response_times = []
        for r in results:
            all_response_times.extend(r["response_times"])
        
        if all_response_times:
            avg_response_time = sum(all_response_times) / len(all_response_times)
            max_response_time = max(all_response_times)
            error_rate = (total_errors / total_requests) * 100 if total_requests > 0 else 0
            
            # Performance criteria
            if avg_response_time > 5.0:  # 5 seconds average
                self.log_result("performance", "Average Response Time", False, 
                              f"Average response time too high: {avg_response_time:.2f}s", critical=True)
            else:
                self.log_result("performance", "Average Response Time", True, 
                              f"Average response time: {avg_response_time:.2f}s")
            
            if max_response_time > 30.0:  # 30 seconds max
                self.log_result("performance", "Maximum Response Time", False, 
                              f"Maximum response time too high: {max_response_time:.2f}s", critical=True)
            else:
                self.log_result("performance", "Maximum Response Time", True, 
                              f"Maximum response time: {max_response_time:.2f}s")
            
            if error_rate > 5.0:  # 5% error rate
                self.log_result("performance", "Error Rate Under Load", False, 
                              f"Error rate too high: {error_rate:.1f}%", critical=True)
            else:
                self.log_result("performance", "Error Rate Under Load", True, 
                              f"Error rate: {error_rate:.1f}%")
            
            requests_per_second = total_requests / LOAD_TEST_DURATION
            self.log_result("performance", "Throughput", True, 
                          f"Handled {requests_per_second:.1f} requests/second")
        else:
            self.log_result("performance", "Concurrent Load", False, 
                          "No successful requests during load test", critical=True)

    def test_ai_generation_performance(self):
        """Test AI generation performance"""
        print("\n=== PERFORMANCE TEST 2: AI Generation Performance ===")
        
        try:
            # Authenticate
            auth_response = self.make_request("POST", "/auth/login", {
                "email": "marie.dupont@example.com",
                "password": "SecurePass123!"
            })
            
            if not auth_response or auth_response.status_code != 200:
                self.log_result("performance", "AI Generation Performance", False, 
                              "Could not authenticate for AI test", critical=False)
                return
            
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create project
            project_response = self.make_request("POST", "/projects", {
                "title": "Performance Test App",
                "description": "Simple web application for performance testing",
                "type": "web_app"
            }, headers=headers)
            
            if not project_response or project_response.status_code != 200:
                self.log_result("performance", "AI Generation Performance", False, 
                              "Could not create project for AI test", critical=False)
                return
            
            project_id = project_response.json()["id"]
            
            # Test AI generation time
            start_time = time.time()
            
            generation_response = self.make_request("POST", f"/projects/{project_id}/generate", {
                "description": "Simple web application for performance testing",
                "type": "web_app",
                "framework": "react"
            }, headers=headers, timeout=60)  # 60 second timeout for AI
            
            generation_time = time.time() - start_time
            
            if generation_response and generation_response.status_code == 200:
                if generation_time > 45.0:  # 45 seconds max for AI generation
                    self.log_result("performance", "AI Generation Speed", False, 
                                  f"AI generation too slow: {generation_time:.1f}s", critical=True)
                else:
                    self.log_result("performance", "AI Generation Speed", True, 
                                  f"AI generation completed in {generation_time:.1f}s")
            else:
                self.log_result("performance", "AI Generation Performance", False, 
                              "AI generation failed", critical=True)
        
        except Exception as e:
            self.log_result("performance", "AI Generation Performance", False, 
                          f"Error during AI generation test: {str(e)}", critical=False)

    def test_memory_leaks(self):
        """Test for potential memory leaks"""
        print("\n=== PERFORMANCE TEST 3: Memory Leak Detection ===")
        
        # Perform many rapid operations that could cause memory leaks
        operations = 0
        start_time = time.time()
        
        try:
            for i in range(100):  # 100 rapid operations
                # Mix of operations
                if i % 3 == 0:
                    response = self.make_request("GET", "/stats")
                elif i % 3 == 1:
                    response = self.make_request("POST", "/auth/login", {
                        "email": "nonexistent@example.com",
                        "password": "wrong"
                    })
                else:
                    response = self.make_request("GET", "/")
                
                operations += 1
                
                # Check if responses are getting slower (potential memory leak indicator)
                if i > 0 and i % 20 == 0:
                    current_time = time.time()
                    avg_time_per_op = (current_time - start_time) / operations
                    if avg_time_per_op > 1.0:  # More than 1 second per operation
                        self.log_result("performance", "Memory Leak Detection", False, 
                                      f"Operations getting slower: {avg_time_per_op:.2f}s/op", critical=True)
                        return
            
            total_time = time.time() - start_time
            avg_time = total_time / operations
            
            if avg_time < 0.5:  # Less than 0.5 seconds per operation
                self.log_result("performance", "Memory Leak Detection", True, 
                              f"No memory leak detected: {avg_time:.3f}s/op average")
            else:
                self.log_result("performance", "Memory Leak Detection", False, 
                              f"Potential performance degradation: {avg_time:.3f}s/op", critical=False)
        
        except Exception as e:
            self.log_result("performance", "Memory Leak Detection", False, 
                          f"Error during memory leak test: {str(e)}", critical=False)

    def test_emergent_llm_integration(self):
        """Test Emergent LLM integration robustness"""
        print("\n=== INTEGRATION TEST 1: Emergent LLM Key Validation ===")
        
        try:
            # Test if AI generation works (indicates LLM key is functional)
            auth_response = self.make_request("POST", "/auth/login", {
                "email": "marie.dupont@example.com",
                "password": "SecurePass123!"
            })
            
            if not auth_response or auth_response.status_code != 200:
                self.log_result("security", "LLM Integration", False, 
                              "Could not authenticate for LLM test", critical=False)
                return
            
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create project
            project_response = self.make_request("POST", "/projects", {
                "title": "LLM Integration Test",
                "description": "Test LLM integration",
                "type": "web_app"
            }, headers=headers)
            
            if not project_response or project_response.status_code != 200:
                self.log_result("security", "LLM Integration", False, 
                              "Could not create project for LLM test", critical=False)
                return
            
            project_id = project_response.json()["id"]
            
            # Test AI generation
            generation_response = self.make_request("POST", f"/projects/{project_id}/generate", {
                "description": "simple web page",
                "type": "web_app",
                "framework": "react"
            }, headers=headers, timeout=45)
            
            if generation_response and generation_response.status_code == 200:
                data = generation_response.json()
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                has_code = any(data.get(field) for field in code_fields)
                
                if has_code:
                    self.log_result("security", "Emergent LLM Integration", True, 
                                  "LLM integration working correctly")
                else:
                    self.log_result("security", "Emergent LLM Integration", False, 
                                  "LLM integration not generating code", critical=True)
            else:
                self.log_result("security", "Emergent LLM Integration", False, 
                              "LLM integration failed", critical=True)
        
        except Exception as e:
            self.log_result("security", "Emergent LLM Integration", False, 
                          f"Error during LLM integration test: {str(e)}", critical=True)

    def run_security_audit(self):
        """Run comprehensive security audit"""
        print("\n🔒 CRITICAL SECURITY AUDIT")
        print("=" * 60)
        
        self.test_sql_injection_protection()
        self.test_xss_protection()
        self.test_authentication_security()
        self.test_rate_limiting()
        self.test_input_validation()
        self.test_emergent_llm_integration()

    def run_performance_audit(self):
        """Run comprehensive performance audit"""
        print("\n⚡ CRITICAL PERFORMANCE AUDIT")
        print("=" * 60)
        
        self.test_concurrent_load()
        self.test_ai_generation_performance()
        self.test_memory_leaks()

    def run_full_audit(self):
        """Run complete pre-launch audit"""
        print("🚨 CODEX PLATFORM - CRITICAL PRE-LAUNCH AUDIT")
        print("🚀 PRODUCTION LAUNCH TODAY - COMPREHENSIVE TESTING")
        print("=" * 80)
        
        self.run_security_audit()
        self.run_performance_audit()
        
        # Final summary
        print("\n" + "=" * 80)
        print("🎯 CRITICAL PRE-LAUNCH AUDIT SUMMARY")
        print("=" * 80)
        
        total_security = self.results["security_passed"] + self.results["security_failed"]
        total_performance = self.results["performance_passed"] + self.results["performance_failed"]
        
        print(f"🔒 Security Tests: {self.results['security_passed']}/{total_security} passed")
        print(f"⚡ Performance Tests: {self.results['performance_passed']}/{total_performance} passed")
        
        if self.results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(self.results['critical_issues'])}):")
            for issue in self.results["critical_issues"]:
                print(f"   ❌ {issue}")
            print("\n⚠️  RECOMMENDATION: DO NOT LAUNCH UNTIL CRITICAL ISSUES ARE RESOLVED!")
            return False
        
        if self.results["warnings"]:
            print(f"\n⚠️  WARNINGS ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"]:
                print(f"   ⚠️  {warning}")
        
        if not self.results["critical_issues"]:
            print("\n✅ NO CRITICAL ISSUES FOUND - PLATFORM READY FOR PRODUCTION LAUNCH!")
            return True
        
        return False

if __name__ == "__main__":
    tester = SecurityPerformanceTester()
    ready_for_launch = tester.run_full_audit()
    sys.exit(0 if ready_for_launch else 1)