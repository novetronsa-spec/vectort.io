#!/usr/bin/env python3
"""
Quick AI Generation Test - Test specific corrections with shorter timeout
"""

import requests
import json
import time

BASE_URL = "https://codecraft-125.preview.emergentagent.com/api"

def test_ai_generation():
    print("🔧 Quick AI Generation Test")
    
    # Register user
    test_user = {
        "email": f"quick.test.{int(time.time())}@vectort.io",
        "password": "QuickTest123!",
        "full_name": "Quick Test User"
    }
    
    try:
        # Register
        reg_response = requests.post(f"{BASE_URL}/auth/register", json=test_user, timeout=10)
        if reg_response.status_code != 200:
            print(f"❌ Registration failed: {reg_response.status_code}")
            return False
        
        token = reg_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create project
        project_data = {
            "title": "Quick Test Project",
            "description": "Simple test project",
            "type": "ecommerce"  # Test enum
        }
        
        proj_response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers, timeout=10)
        if proj_response.status_code != 200:
            print(f"❌ Project creation failed: {proj_response.status_code}")
            return False
        
        project_id = proj_response.json()["id"]
        print(f"✅ Project created: {project_id}")
        
        # Test basic generation (should be faster)
        gen_request = {
            "description": "Simple e-commerce site",
            "type": "ecommerce",
            "framework": "react",
            "advanced_mode": False  # Basic mode should be faster
        }
        
        print("🤖 Testing basic AI generation...")
        gen_response = requests.post(f"{BASE_URL}/projects/{project_id}/generate", 
                                   json=gen_request, headers=headers, timeout=60)
        
        if gen_response.status_code == 200:
            data = gen_response.json()
            has_code = any(data.get(field) for field in ["html_code", "css_code", "js_code", "react_code"])
            if has_code:
                print("✅ Basic AI generation working!")
                return True
            else:
                print("❌ No code generated")
                return False
        else:
            print(f"❌ Generation failed: {gen_response.status_code} - {gen_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_password_validation():
    print("\n🔒 Quick Password Validation Test")
    
    # Test weak password
    weak_user = {
        "email": f"weak.{int(time.time())}@vectort.io",
        "password": "123",
        "full_name": "Weak Test"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=weak_user, timeout=10)
        if response.status_code == 422:
            print("✅ Weak password correctly rejected")
            return True
        else:
            print(f"❌ Weak password accepted: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_endpoints():
    print("\n🌐 Quick Endpoints Test")
    
    try:
        # Test basic endpoints
        basic_response = requests.get(f"{BASE_URL}/", timeout=10)
        stats_response = requests.get(f"{BASE_URL}/stats", timeout=10)
        
        if basic_response.status_code == 200 and stats_response.status_code == 200:
            print("✅ Basic endpoints working")
            return True
        else:
            print(f"❌ Endpoints failed: {basic_response.status_code}, {stats_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Corrections Verification")
    print("=" * 50)
    
    results = []
    results.append(test_endpoints())
    results.append(test_password_validation())
    results.append(test_ai_generation())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Quick Test Results: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All quick tests passed!")
    else:
        print("⚠️ Some tests failed - check detailed logs")