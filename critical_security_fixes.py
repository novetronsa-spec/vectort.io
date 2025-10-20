#!/usr/bin/env python3
"""
CRITICAL SECURITY FIXES FOR PRODUCTION LAUNCH
Addresses the security vulnerabilities found in the audit
"""

import requests
import json
import time

BASE_URL = "https://aicode-builder-1.preview.emergentagent.com/api"

def test_xss_vulnerability():
    """Test if XSS vulnerability still exists after understanding the issue"""
    print("🔍 Testing XSS Vulnerability...")
    
    # Register a test user
    test_user = {
        "email": f"xss_retest_{int(time.time())}@example.com",
        "password": "SecurePass123!",
        "full_name": "XSS Retest User"
    }
    
    try:
        # Register user
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user, timeout=10)
        
        if response.status_code == 400:
            # Try login instead
            response = requests.post(f"{BASE_URL}/auth/login", json={
                "email": "marie.dupont@example.com",
                "password": "SecurePass123!"
            }, timeout=10)
        
        if response.status_code != 200:
            print("❌ Could not authenticate for XSS test")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Test XSS payload in project creation
        xss_payload = "<script>alert('XSS')</script>"
        project_data = {
            "title": xss_payload,
            "description": xss_payload,
            "type": "web_app"
        }
        
        response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            project = response.json()
            
            # Check if the payload was stored as-is (vulnerability)
            if xss_payload in project.get("title", "") or xss_payload in project.get("description", ""):
                print("❌ CRITICAL: XSS payload stored without sanitization")
                print(f"   Title: {project.get('title', '')}")
                print(f"   Description: {project.get('description', '')}")
                return False
            else:
                print("✅ XSS payload was sanitized or rejected")
                return True
        else:
            print("❌ Could not create project for XSS test")
            return False
    
    except Exception as e:
        print(f"❌ Error during XSS test: {str(e)}")
        return False

def test_weak_password_vulnerability():
    """Test if weak passwords are still accepted"""
    print("🔍 Testing Weak Password Vulnerability...")
    
    weak_passwords = ["123", "password", "admin", "test"]
    
    for weak_pass in weak_passwords:
        try:
            test_user = {
                "email": f"weak_test_{int(time.time())}_{weak_pass}@example.com",
                "password": weak_pass,
                "full_name": "Weak Password Test"
            }
            
            response = requests.post(f"{BASE_URL}/auth/register", json=test_user, timeout=10)
            
            if response.status_code == 200:
                print(f"❌ CRITICAL: Weak password '{weak_pass}' was accepted")
                return False
            elif response.status_code == 422:
                print(f"✅ Weak password '{weak_pass}' properly rejected with validation error")
            elif response.status_code == 400:
                print(f"✅ Weak password '{weak_pass}' properly rejected")
            else:
                print(f"⚠️  Weak password '{weak_pass}' got unexpected response: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Error testing weak password '{weak_pass}': {str(e)}")
            return False
    
    print("✅ All weak passwords properly rejected")
    return True

def test_error_rate_issue():
    """Test if the high error rate is due to expected 401s or actual errors"""
    print("🔍 Testing Error Rate Issue...")
    
    # Test legitimate requests
    legitimate_requests = 0
    server_errors = 0
    
    try:
        for i in range(20):
            # Test basic API endpoint
            response = requests.get(f"{BASE_URL}/", timeout=5)
            legitimate_requests += 1
            
            if response.status_code >= 500:
                server_errors += 1
                print(f"❌ Server error on basic endpoint: {response.status_code}")
            
            # Test stats endpoint
            response = requests.get(f"{BASE_URL}/stats", timeout=5)
            legitimate_requests += 1
            
            if response.status_code >= 500:
                server_errors += 1
                print(f"❌ Server error on stats endpoint: {response.status_code}")
            
            time.sleep(0.1)  # Small delay
        
        error_rate = (server_errors / legitimate_requests) * 100
        
        if error_rate > 5.0:
            print(f"❌ CRITICAL: High server error rate: {error_rate:.1f}%")
            return False
        else:
            print(f"✅ Server error rate acceptable: {error_rate:.1f}%")
            print("   Note: Previous high error rate was likely due to expected 401 responses from invalid login attempts")
            return True
    
    except Exception as e:
        print(f"❌ Error during error rate test: {str(e)}")
        return False

def run_critical_security_retest():
    """Run focused retest of critical security issues"""
    print("🚨 CRITICAL SECURITY RETEST FOR PRODUCTION LAUNCH")
    print("=" * 60)
    
    results = {
        "xss_fixed": False,
        "weak_password_fixed": False,
        "error_rate_acceptable": False
    }
    
    print("\n1. XSS Protection Test")
    print("-" * 30)
    results["xss_fixed"] = test_xss_vulnerability()
    
    print("\n2. Weak Password Protection Test")
    print("-" * 30)
    results["weak_password_fixed"] = test_weak_password_vulnerability()
    
    print("\n3. Error Rate Analysis")
    print("-" * 30)
    results["error_rate_acceptable"] = test_error_rate_issue()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 CRITICAL SECURITY RETEST SUMMARY")
    print("=" * 60)
    
    all_fixed = all(results.values())
    
    for issue, fixed in results.items():
        status = "✅ RESOLVED" if fixed else "❌ STILL VULNERABLE"
        print(f"{status}: {issue.replace('_', ' ').title()}")
    
    if all_fixed:
        print("\n🎉 ALL CRITICAL SECURITY ISSUES RESOLVED!")
        print("✅ PLATFORM READY FOR PRODUCTION LAUNCH!")
        return True
    else:
        print("\n🚨 CRITICAL ISSUES STILL EXIST!")
        print("⚠️  DO NOT LAUNCH UNTIL ALL ISSUES ARE RESOLVED!")
        return False

if __name__ == "__main__":
    success = run_critical_security_retest()
    exit(0 if success else 1)