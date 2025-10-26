#!/usr/bin/env python3
"""
Debug Advanced Generation - Check what's happening with advanced mode
"""

import requests
import json
import time

BASE_URL = "https://oauth-debug-2.preview.emergentagent.com/api"
TEST_USER = {
    "email": f"debug.test.{int(time.time())}@vectort.io",
    "password": "DebugTest123!",
    "full_name": f"Debug Test {int(time.time() % 1000000)}"
}

def make_request(method, endpoint, data=None, headers=None, timeout=90, access_token=None):
    url = f"{BASE_URL}{endpoint}"
    default_headers = {"Content-Type": "application/json"}
    
    if headers:
        default_headers.update(headers)
    
    if access_token and "Authorization" not in default_headers:
        default_headers["Authorization"] = f"Bearer {access_token}"
    
    if method.upper() == "POST":
        response = requests.post(url, json=data, headers=default_headers, timeout=timeout)
    elif method.upper() == "GET":
        response = requests.get(url, headers=default_headers, timeout=timeout)
    
    return response

def debug_advanced_generation():
    print("🔍 DEBUG ADVANCED GENERATION")
    print("=" * 50)
    
    # Register user
    response = make_request("POST", "/auth/register", TEST_USER, timeout=30)
    if response.status_code != 200:
        print(f"❌ Registration failed: {response.status_code}")
        return
    
    access_token = response.json()["access_token"]
    print(f"✅ User registered")
    
    # Create project
    project_data = {
        "title": "Debug E-commerce Advanced",
        "description": "Test project for debugging advanced generation",
        "type": "ecommerce"
    }
    
    project_response = make_request("POST", "/projects", project_data, timeout=30, access_token=access_token)
    if project_response.status_code != 200:
        print(f"❌ Project creation failed: {project_response.status_code}")
        return
    
    project_id = project_response.json()["id"]
    print(f"✅ Project created: {project_id}")
    
    # Test advanced generation
    generation_request = {
        "description": "Créer une boutique en ligne simple avec React",
        "type": "ecommerce",
        "framework": "react",
        "database": "mongodb",
        "advanced_mode": True,
        "features": ["authentication", "shopping_cart"],
        "integrations": ["stripe"]
    }
    
    print("🔄 Testing advanced generation...")
    start_time = time.time()
    
    response = make_request("POST", f"/projects/{project_id}/generate", 
                           generation_request, timeout=90, access_token=access_token)
    
    generation_time = time.time() - start_time
    
    print(f"⏱️ Generation time: {generation_time:.1f}s")
    print(f"📊 Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n📄 RESPONSE STRUCTURE:")
        for key, value in data.items():
            if isinstance(value, str):
                print(f"  {key}: {len(value)} chars - {'✅' if len(value) > 50 else '❌'}")
            elif isinstance(value, dict):
                print(f"  {key}: dict with {len(value)} keys")
            elif isinstance(value, list):
                print(f"  {key}: list with {len(value)} items")
            else:
                print(f"  {key}: {type(value)} - {value}")
        
        # Check main files
        main_files = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
        generated_count = 0
        for field in main_files:
            content = data.get(field, "")
            if content and len(str(content).strip()) > 50:
                generated_count += 1
                print(f"  ✅ {field}: {len(content)} chars")
            else:
                print(f"  ❌ {field}: {len(str(content))} chars")
        
        print(f"\n📈 SUMMARY: {generated_count}/{len(main_files)} main files generated")
        
        # Check advanced fields
        advanced_fields = ["project_structure", "package_json", "dockerfile", "readme", "all_files"]
        advanced_count = 0
        for field in advanced_fields:
            content = data.get(field)
            if content:
                advanced_count += 1
                if isinstance(content, dict):
                    print(f"  ✅ {field}: dict with {len(content)} keys")
                else:
                    print(f"  ✅ {field}: {len(str(content))} chars")
            else:
                print(f"  ❌ {field}: None/Empty")
        
        print(f"📈 ADVANCED: {advanced_count}/{len(advanced_fields)} advanced fields generated")
        
        # Show sample content
        if data.get("react_code"):
            print(f"\n📝 REACT CODE SAMPLE (first 200 chars):")
            print(data.get("react_code")[:200] + "...")
        
        if data.get("backend_code"):
            print(f"\n📝 BACKEND CODE SAMPLE (first 200 chars):")
            print(data.get("backend_code")[:200] + "...")
    else:
        print(f"❌ Generation failed: {response.text}")
    
    # Test basic mode for comparison
    print("\n🔄 Testing basic generation for comparison...")
    basic_request = generation_request.copy()
    basic_request["advanced_mode"] = False
    
    basic_response = make_request("POST", f"/projects/{project_id}/generate", 
                                 basic_request, timeout=60, access_token=access_token)
    
    if basic_response.status_code == 200:
        basic_data = basic_response.json()
        basic_count = 0
        for field in main_files:
            content = basic_data.get(field, "")
            if content and len(str(content).strip()) > 50:
                basic_count += 1
        
        print(f"📈 BASIC MODE: {basic_count}/{len(main_files)} files generated")
    else:
        print(f"❌ Basic generation failed: {basic_response.status_code}")

if __name__ == "__main__":
    debug_advanced_generation()