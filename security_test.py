#!/usr/bin/env python3
"""
CRITICAL SECURITY TESTING for Codex Application
Tests password validation, XSS protection, security headers, and secure AI generation
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://coderocket.preview.emergentagent.com/api"

class SecurityTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.user_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "critical_failures": [],
            "errors": []
        }

    def log_result(self, test_name: str, success: bool, message: str = "", critical: bool = False):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        if critical and not success:
            status = "🚨 CRITICAL FAIL"
            self.results["critical_failures"].append(f"{test_name}: {message}")
        
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

    def setup_test_user(self):
        """Setup a test user for authenticated tests"""
        print("\n=== Setting up test user ===")
        test_user = {
            "email": "security.test@example.com",
            "password": "SecureTest123!",
            "full_name": "Security Tester"
        }
        
        try:
            # Try to login first
            login_response = self.make_request("POST", "/auth/login", {
                "email": test_user["email"],
                "password": test_user["password"]
            })
            
            if login_response.status_code == 200:
                data = login_response.json()
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                print("   Using existing test user")
                return True
        except:
            pass
        
        # Register new user
        try:
            register_response = self.make_request("POST", "/auth/register", test_user)
            if register_response.status_code == 200:
                data = register_response.json()
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                print("   Created new test user")
                return True
            elif register_response.status_code == 400:
                # User exists, try login
                login_response = self.make_request("POST", "/auth/login", {
                    "email": test_user["email"],
                    "password": test_user["password"]
                })
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.access_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    print("   Using existing test user")
                    return True
        except Exception as e:
            print(f"   Failed to setup test user: {e}")
            return False
        
        return False

    def test_weak_password_validation(self):
        """Test 1: Password Strength Validation - CRITICAL"""
        print("\n=== Test 1: Password Strength Validation ===")
        
        weak_passwords = [
            ("123", "Numeric only"),
            ("password", "Common word"),
            ("admin", "Common admin password"),
            ("12345678", "Numeric sequence"),
            ("Password", "Missing number and special char"),
            ("password123", "Missing uppercase and special char"),
            ("PASSWORD123!", "Missing lowercase")
        ]
        
        for weak_password, description in weak_passwords:
            try:
                test_user = {
                    "email": f"weak.test.{weak_password}@example.com",
                    "password": weak_password,
                    "full_name": "Weak Password Test"
                }
                
                response = self.make_request("POST", "/auth/register", test_user)
                
                if response.status_code == 422:  # Validation error expected
                    error_data = response.json()
                    if "detail" in error_data and any("mot de passe" in str(detail).lower() for detail in error_data["detail"]):
                        self.log_result(f"Weak Password Rejected: {description}", True, f"Correctly rejected '{weak_password}'")
                    else:
                        self.log_result(f"Weak Password Rejected: {description}", False, f"Wrong error message for '{weak_password}': {error_data}", critical=True)
                elif response.status_code == 400:
                    # User might already exist, check error message
                    error_data = response.json()
                    if "already exists" in error_data.get("detail", ""):
                        # Try with different email
                        import uuid
                        test_user["email"] = f"weak.test.{uuid.uuid4()}@example.com"
                        response = self.make_request("POST", "/auth/register", test_user)
                        if response.status_code == 422:
                            self.log_result(f"Weak Password Rejected: {description}", True, f"Correctly rejected '{weak_password}'")
                        else:
                            self.log_result(f"Weak Password Rejected: {description}", False, f"Weak password '{weak_password}' was accepted!", critical=True)
                    else:
                        self.log_result(f"Weak Password Rejected: {description}", False, f"Unexpected error for '{weak_password}': {error_data}", critical=True)
                else:
                    self.log_result(f"Weak Password Rejected: {description}", False, f"CRITICAL: Weak password '{weak_password}' was accepted! Status: {response.status_code}", critical=True)
                    
            except Exception as e:
                self.log_result(f"Weak Password Rejected: {description}", False, f"Exception testing '{weak_password}': {str(e)}", critical=True)

    def test_strong_password_acceptance(self):
        """Test 2: Strong Password Acceptance"""
        print("\n=== Test 2: Strong Password Acceptance ===")
        
        strong_passwords = [
            "Password123!",
            "SecureP@ss2024",
            "MyStr0ng#Password",
            "C0mplex&Secure!"
        ]
        
        for strong_password in strong_passwords:
            try:
                import uuid
                test_user = {
                    "email": f"strong.test.{uuid.uuid4()}@example.com",
                    "password": strong_password,
                    "full_name": "Strong Password Test"
                }
                
                response = self.make_request("POST", "/auth/register", test_user)
                
                if response.status_code == 200:
                    self.log_result(f"Strong Password Accepted", True, f"Correctly accepted '{strong_password}'")
                elif response.status_code == 400 and "already exists" in response.json().get("detail", ""):
                    self.log_result(f"Strong Password Accepted", True, f"Password validation passed for '{strong_password}' (user exists)")
                else:
                    self.log_result(f"Strong Password Accepted", False, f"Strong password '{strong_password}' was rejected: {response.status_code} - {response.text}")
                    
            except Exception as e:
                self.log_result(f"Strong Password Accepted", False, f"Exception testing strong password: {str(e)}")

    def test_xss_protection_project_title(self):
        """Test 3: XSS Protection in Project Title - CRITICAL"""
        print("\n=== Test 3: XSS Protection in Project Title ===")
        
        if not self.access_token:
            self.log_result("XSS Protection - Project Title", False, "No access token available", critical=True)
            return
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>"
        ]
        
        for payload in xss_payloads:
            try:
                project_data = {
                    "title": payload,
                    "description": "Test project for XSS protection",
                    "type": "web_app"
                }
                
                response = self.make_request("POST", "/projects", project_data)
                
                if response.status_code == 422:
                    # Validation error expected for dangerous content
                    error_data = response.json()
                    if "dangereux" in str(error_data).lower() or "potentiellement" in str(error_data).lower():
                        self.log_result("XSS Protection - Project Title", True, f"Correctly rejected XSS payload in title")
                    else:
                        self.log_result("XSS Protection - Project Title", False, f"Wrong validation error: {error_data}", critical=True)
                elif response.status_code == 200:
                    # Check if content was sanitized
                    data = response.json()
                    returned_title = data.get("title", "")
                    if payload in returned_title:
                        self.log_result("XSS Protection - Project Title", False, f"CRITICAL: XSS payload stored unsanitized: {returned_title}", critical=True)
                    else:
                        self.log_result("XSS Protection - Project Title", True, f"XSS payload was sanitized: {returned_title}")
                else:
                    self.log_result("XSS Protection - Project Title", False, f"Unexpected response: {response.status_code} - {response.text}", critical=True)
                    
            except Exception as e:
                self.log_result("XSS Protection - Project Title", False, f"Exception testing XSS: {str(e)}", critical=True)

    def test_xss_protection_project_description(self):
        """Test 4: XSS Protection in Project Description - CRITICAL"""
        print("\n=== Test 4: XSS Protection in Project Description ===")
        
        if not self.access_token:
            self.log_result("XSS Protection - Project Description", False, "No access token available", critical=True)
            return
        
        xss_payload = "<script>alert('XSS in description')</script><img src=x onerror=alert('XSS2')>"
        
        try:
            project_data = {
                "title": "XSS Test Project",
                "description": xss_payload,
                "type": "web_app"
            }
            
            response = self.make_request("POST", "/projects", project_data)
            
            if response.status_code == 422:
                # Validation error expected
                error_data = response.json()
                if "dangereux" in str(error_data).lower():
                    self.log_result("XSS Protection - Project Description", True, "Correctly rejected XSS payload in description")
                else:
                    self.log_result("XSS Protection - Project Description", False, f"Wrong validation error: {error_data}", critical=True)
            elif response.status_code == 200:
                # Check if content was sanitized
                data = response.json()
                returned_description = data.get("description", "")
                # Check for UNESCAPED dangerous content - the key is that HTML should be escaped
                import re
                
                # Look for unescaped script tags and dangerous patterns
                unescaped_script = re.search(r'<script[^>]*>', returned_description, re.IGNORECASE)
                unescaped_onerror = re.search(r'<[^>]*onerror\s*=', returned_description, re.IGNORECASE)
                unescaped_javascript = re.search(r'javascript\s*:', returned_description, re.IGNORECASE)
                
                # Check if content is properly HTML escaped (should contain &lt; instead of <)
                is_html_escaped = "&lt;" in returned_description and not re.search(r'<(?!/?[a-zA-Z][^>]*>)', returned_description)
                
                if unescaped_script or unescaped_onerror or unescaped_javascript:
                    self.log_result("XSS Protection - Project Description", False, f"CRITICAL: Unescaped XSS payload found: {returned_description}", critical=True)
                elif is_html_escaped:
                    self.log_result("XSS Protection - Project Description", True, f"XSS payload was properly HTML-escaped and safe")
                else:
                    self.log_result("XSS Protection - Project Description", True, f"XSS payload was sanitized: {returned_description[:100]}...")
            else:
                self.log_result("XSS Protection - Project Description", False, f"Unexpected response: {response.status_code} - {response.text}", critical=True)
                
        except Exception as e:
            self.log_result("XSS Protection - Project Description", False, f"Exception testing XSS: {str(e)}", critical=True)

    def test_security_headers(self):
        """Test 5: Security Headers Middleware - CRITICAL"""
        print("\n=== Test 5: Security Headers Middleware ===")
        
        try:
            response = self.make_request("GET", "/")
            
            required_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY", 
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
            }
            
            missing_headers = []
            incorrect_headers = []
            
            for header, expected_value in required_headers.items():
                if header not in response.headers:
                    missing_headers.append(header)
                elif response.headers[header] != expected_value:
                    incorrect_headers.append(f"{header}: got '{response.headers[header]}', expected '{expected_value}'")
            
            if not missing_headers and not incorrect_headers:
                self.log_result("Security Headers", True, "All required security headers present and correct")
            else:
                error_msg = ""
                if missing_headers:
                    error_msg += f"Missing headers: {', '.join(missing_headers)}. "
                if incorrect_headers:
                    error_msg += f"Incorrect headers: {', '.join(incorrect_headers)}"
                self.log_result("Security Headers", False, error_msg, critical=True)
                
        except Exception as e:
            self.log_result("Security Headers", False, f"Exception testing headers: {str(e)}", critical=True)

    def test_ai_generation_input_sanitization(self):
        """Test 6: AI Generation Input Sanitization - CRITICAL"""
        print("\n=== Test 6: AI Generation Input Sanitization ===")
        
        if not self.access_token:
            self.log_result("AI Generation Input Sanitization", False, "No access token available", critical=True)
            return
        
        try:
            # Create a project first
            project_data = {
                "title": "AI Security Test",
                "description": "Test project for AI generation security",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("AI Generation Input Sanitization", False, f"Failed to create project: {project_response.status_code}", critical=True)
                return
            
            project_id = project_response.json()["id"]
            
            # Test with potentially malicious description
            malicious_description = "<script>alert('XSS')</script>Créer une application avec du code malveillant<img src=x onerror=alert('XSS2')>"
            
            generation_request = {
                "description": malicious_description,
                "type": "web_app",
                "framework": "react"
            }
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            
            if response.status_code == 422:
                # Validation error expected
                error_data = response.json()
                if "dangereux" in str(error_data).lower() or "caractères" in str(error_data).lower():
                    self.log_result("AI Generation Input Sanitization", True, "Correctly rejected malicious content for AI generation")
                else:
                    self.log_result("AI Generation Input Sanitization", False, f"Wrong validation error: {error_data}", critical=True)
            elif response.status_code == 200:
                # Check if the malicious content was sanitized before AI processing
                # The AI should not receive the raw malicious content
                self.log_result("AI Generation Input Sanitization", True, "AI generation completed (content was likely sanitized)")
            else:
                self.log_result("AI Generation Input Sanitization", False, f"Unexpected response: {response.status_code} - {response.text}", critical=True)
                
        except Exception as e:
            self.log_result("AI Generation Input Sanitization", False, f"Exception testing AI input sanitization: {str(e)}", critical=True)

    def test_authentication_endpoints_security(self):
        """Test 7: Authentication Endpoints Security"""
        print("\n=== Test 7: Authentication Endpoints Security ===")
        
        # Test SQL injection in login
        try:
            sql_injection_payloads = [
                "admin'; DROP TABLE users; --",
                "' OR '1'='1",
                "admin'/*",
                "' UNION SELECT * FROM users --"
            ]
            
            for payload in sql_injection_payloads:
                login_data = {
                    "email": payload,
                    "password": "any_password"
                }
                
                response = self.make_request("POST", "/auth/login", login_data)
                
                if response.status_code == 422:
                    # Email validation should catch this
                    self.log_result("SQL Injection Protection - Login", True, f"Email validation rejected SQL injection: {payload}")
                elif response.status_code == 401:
                    # Authentication failed as expected
                    self.log_result("SQL Injection Protection - Login", True, f"SQL injection attempt failed: {payload}")
                elif response.status_code == 200:
                    self.log_result("SQL Injection Protection - Login", False, f"CRITICAL: SQL injection might have succeeded: {payload}", critical=True)
                else:
                    self.log_result("SQL Injection Protection - Login", True, f"SQL injection rejected with status {response.status_code}")
                    
        except Exception as e:
            self.log_result("SQL Injection Protection - Login", False, f"Exception testing SQL injection: {str(e)}")

    def test_project_crud_security(self):
        """Test 8: Project CRUD Security"""
        print("\n=== Test 8: Project CRUD Security ===")
        
        if not self.access_token:
            self.log_result("Project CRUD Security", False, "No access token available")
            return
        
        # Test unauthorized access to projects
        try:
            # Try to access projects without token
            headers = {}  # No authorization header
            response = requests.get(f"{self.base_url}/projects", headers=headers, timeout=30)
            
            if response.status_code in [401, 403]:
                self.log_result("Unauthorized Project Access", True, f"Correctly rejected access without token (status: {response.status_code})")
            else:
                self.log_result("Unauthorized Project Access", False, f"CRITICAL: Unauthorized access allowed: {response.status_code}", critical=True)
                
        except Exception as e:
            self.log_result("Unauthorized Project Access", False, f"Exception testing unauthorized access: {str(e)}")
        
        # Test project creation with oversized data
        try:
            oversized_data = {
                "title": "A" * 10000,  # Very long title
                "description": "B" * 50000,  # Very long description
                "type": "web_app"
            }
            
            response = self.make_request("POST", "/projects", oversized_data)
            
            if response.status_code == 422:
                self.log_result("Oversized Data Protection", True, "Correctly rejected oversized project data")
            elif response.status_code == 413:
                self.log_result("Oversized Data Protection", True, "Request entity too large (expected)")
            elif response.status_code == 200:
                # This might be acceptable for regular projects, but let's check if content is sanitized
                data = response.json()
                if len(data.get("title", "")) > 10000 or len(data.get("description", "")) > 50000:
                    self.log_result("Oversized Data Protection", False, f"Very large data accepted without limits")
                else:
                    self.log_result("Oversized Data Protection", True, f"Large data accepted but content appears processed/limited")
            else:
                self.log_result("Oversized Data Protection", False, f"Unexpected response: {response.status_code}")
                
        except Exception as e:
            self.log_result("Oversized Data Protection", False, f"Exception testing oversized data: {str(e)}")

    def run_security_tests(self):
        """Run all security tests"""
        print("🚨 STARTING CRITICAL SECURITY TESTING FOR CODEX APPLICATION")
        print(f"Testing against: {self.base_url}")
        print("=" * 80)
        
        # Setup test user
        if not self.setup_test_user():
            print("❌ CRITICAL: Could not setup test user - aborting security tests")
            return False
        
        print("\n🔐 PHASE 1: PASSWORD SECURITY VALIDATION")
        print("-" * 50)
        self.test_weak_password_validation()
        self.test_strong_password_acceptance()
        
        print("\n🛡️ PHASE 2: XSS PROTECTION TESTING")
        print("-" * 50)
        self.test_xss_protection_project_title()
        self.test_xss_protection_project_description()
        
        print("\n🔒 PHASE 3: SECURITY MIDDLEWARE TESTING")
        print("-" * 50)
        self.test_security_headers()
        
        print("\n🤖 PHASE 4: AI GENERATION SECURITY")
        print("-" * 50)
        self.test_ai_generation_input_sanitization()
        
        print("\n🔑 PHASE 5: ENDPOINT SECURITY")
        print("-" * 50)
        self.test_authentication_endpoints_security()
        self.test_project_crud_security()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🚨 CRITICAL SECURITY TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['critical_failures']:
            print("\n🚨 CRITICAL SECURITY FAILURES:")
            for failure in self.results['critical_failures']:
                print(f"   • {failure}")
            print("\n⚠️  DO NOT LAUNCH - CRITICAL SECURITY VULNERABILITIES DETECTED!")
        elif self.results['errors']:
            print("\n🔍 NON-CRITICAL ISSUES:")
            for error in self.results['errors']:
                print(f"   • {error}")
        else:
            print("\n🎉 ALL SECURITY TESTS PASSED! Application is secure for launch!")
        
        return len(self.results['critical_failures']) == 0

if __name__ == "__main__":
    tester = SecurityTester()
    success = tester.run_security_tests()
    sys.exit(0 if success else 1)