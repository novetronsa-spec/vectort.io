#!/usr/bin/env python3
"""
Debug advanced mode response
"""

import requests
import json
import time

BASE_URL = "https://aicode-builder-1.preview.emergentagent.com/api"

def debug_advanced_response():
    print("🔍 Debugging Advanced Mode Response")
    
    # Register user
    test_user = {
        "email": f"debug.{int(time.time())}@vectort.io",
        "password": "Debug123!",
        "full_name": "Debug User"
    }
    
    try:
        # Register
        reg_response = requests.post(f"{BASE_URL}/auth/register", json=test_user, timeout=10)
        token = reg_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create project
        project_data = {
            "title": "Debug Project",
            "description": "Debug project",
            "type": "ecommerce"
        }
        
        proj_response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers, timeout=10)
        project_id = proj_response.json()["id"]
        
        # Test advanced mode and print full response
        advanced_request = {
            "description": "Simple e-commerce site",
            "type": "ecommerce",
            "framework": "react",
            "advanced_mode": True
        }
        
        print("📤 Sending advanced mode request...")
        adv_response = requests.post(f"{BASE_URL}/projects/{project_id}/generate", 
                                   json=advanced_request, headers=headers, timeout=90)
        
        print(f"📥 Response Status: {adv_response.status_code}")
        
        if adv_response.status_code == 200:
            data = adv_response.json()
            print(f"📊 Response Keys: {list(data.keys())}")
            
            for key, value in data.items():
                if value:
                    print(f"✅ {key}: {len(str(value))} chars")
                else:
                    print(f"❌ {key}: Empty/None")
                    
            # Check specific fields
            code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
            has_any_code = any(data.get(field) for field in code_fields)
            
            print(f"\n🎯 Has any code: {has_any_code}")
            
            if not has_any_code:
                print("🔍 Full response structure:")
                print(json.dumps(data, indent=2)[:1000] + "..." if len(str(data)) > 1000 else json.dumps(data, indent=2))
        else:
            print(f"❌ Error response: {adv_response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    debug_advanced_response()