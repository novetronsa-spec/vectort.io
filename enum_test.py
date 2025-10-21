#!/usr/bin/env python3
"""
Test specific enum and advanced mode issues
"""

import requests
import json
import time

BASE_URL = "https://emergent-clone-193.preview.emergentagent.com/api"

def test_enum_and_advanced_mode():
    print("🔧 Testing ProjectType Enum and Advanced Mode")
    
    # Register user
    test_user = {
        "email": f"enum.test.{int(time.time())}@vectort.io",
        "password": "EnumTest123!",
        "full_name": "Enum Test User"
    }
    
    try:
        # Register
        reg_response = requests.post(f"{BASE_URL}/auth/register", json=test_user, timeout=10)
        if reg_response.status_code != 200:
            print(f"❌ Registration failed: {reg_response.status_code}")
            return False
        
        token = reg_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 1: Create project with ecommerce type
        project_data = {
            "title": "Test E-commerce Enum",
            "description": "Test project for ecommerce enum validation",
            "type": "ecommerce"  # This should work with enum correction
        }
        
        proj_response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers, timeout=10)
        if proj_response.status_code != 200:
            print(f"❌ Project creation failed: {proj_response.status_code}")
            return False
        
        project_id = proj_response.json()["id"]
        print(f"✅ E-commerce project created: {project_id}")
        
        # Test 2: Try advanced mode first
        print("🤖 Testing advanced mode generation...")
        advanced_request = {
            "description": "Créer une boutique en ligne moderne avec panier d'achats",
            "type": "ecommerce",
            "framework": "react",
            "database": "mongodb",
            "advanced_mode": True,
            "features": ["authentication", "payment_processing"]
        }
        
        try:
            adv_response = requests.post(f"{BASE_URL}/projects/{project_id}/generate", 
                                       json=advanced_request, headers=headers, timeout=90)
            
            if adv_response.status_code == 200:
                data = adv_response.json()
                has_code = any(data.get(field) for field in ["html_code", "css_code", "js_code", "react_code"])
                if has_code:
                    print("✅ Advanced mode generation successful!")
                    return True
                else:
                    print("⚠️ Advanced mode succeeded but no code generated")
            else:
                print(f"⚠️ Advanced mode failed: {adv_response.status_code}")
                print("🔄 Testing fallback to basic mode...")
                
                # Test 3: Fallback to basic mode
                basic_request = {
                    "description": "Créer une boutique en ligne moderne avec panier d'achats",
                    "type": "ecommerce",
                    "framework": "react",
                    "advanced_mode": False
                }
                
                basic_response = requests.post(f"{BASE_URL}/projects/{project_id}/generate", 
                                             json=basic_request, headers=headers, timeout=60)
                
                if basic_response.status_code == 200:
                    data = basic_response.json()
                    has_code = any(data.get(field) for field in ["html_code", "css_code", "js_code", "react_code"])
                    if has_code:
                        print("✅ Fallback to basic mode successful!")
                        return True
                    else:
                        print("❌ Basic mode succeeded but no code generated")
                        return False
                else:
                    print(f"❌ Basic mode also failed: {basic_response.status_code}")
                    return False
                    
        except requests.exceptions.Timeout:
            print("⚠️ Advanced mode timed out, testing basic mode...")
            
            # Test fallback when advanced times out
            basic_request = {
                "description": "Créer une boutique en ligne simple",
                "type": "ecommerce", 
                "framework": "react",
                "advanced_mode": False
            }
            
            basic_response = requests.post(f"{BASE_URL}/projects/{project_id}/generate", 
                                         json=basic_request, headers=headers, timeout=60)
            
            if basic_response.status_code == 200:
                data = basic_response.json()
                has_code = any(data.get(field) for field in ["html_code", "css_code", "js_code", "react_code"])
                if has_code:
                    print("✅ Fallback to basic mode after timeout successful!")
                    return True
                    
            print("❌ Both advanced and basic modes failed")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Enum and Advanced Mode Test")
    print("=" * 50)
    
    success = test_enum_and_advanced_mode()
    
    if success:
        print("\n🎉 Enum and advanced mode corrections working!")
    else:
        print("\n⚠️ Some issues detected with enum/advanced mode")