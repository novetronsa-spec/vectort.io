#!/usr/bin/env python3
"""
Debug script to test generation step by step
"""

import requests
import json
import time

BASE_URL = "https://devstream-ai.preview.emergentagent.com/api"

def test_generation_debug():
    # Create test user
    test_user = {
        "email": f"debug_test_{int(time.time())}@vectort.io",
        "password": "DebugTest123!",
        "full_name": f"Debug Test User {int(time.time())}"
    }
    
    print("1. Creating test user...")
    response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
    if response.status_code != 200:
        print(f"❌ User creation failed: {response.status_code} - {response.text}")
        return
    
    data = response.json()
    access_token = data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print("✅ User created successfully")
    
    # Create project
    print("2. Creating project...")
    project_data = {
        "title": "Debug Test Project",
        "description": "Simple test project for debugging",
        "type": "web_app"
    }
    
    response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Project creation failed: {response.status_code} - {response.text}")
        return
    
    project = response.json()
    project_id = project["id"]
    print(f"✅ Project created: {project_id}")
    
    # Generate code
    print("3. Generating code...")
    generation_request = {
        "description": "Simple website with header and footer",
        "type": "web_app",
        "framework": "react",
        "advanced_mode": False
    }
    
    response = requests.post(f"{BASE_URL}/projects/{project_id}/generate", 
                           json=generation_request, headers=headers)
    
    print(f"Generation response status: {response.status_code}")
    if response.status_code == 200:
        gen_data = response.json()
        print(f"Generation response keys: {list(gen_data.keys())}")
        
        # Check what code was generated
        code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
        for field in code_fields:
            value = gen_data.get(field)
            if value:
                print(f"✅ {field}: {len(value)} characters")
            else:
                print(f"❌ {field}: None or empty")
    else:
        print(f"❌ Generation failed: {response.status_code} - {response.text}")
        return
    
    # Check if code is retrievable
    print("4. Checking code retrieval...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}/code", headers=headers)
    print(f"Code retrieval status: {response.status_code}")
    
    if response.status_code == 200:
        code_data = response.json()
        print(f"Retrieved code keys: {list(code_data.keys())}")
        
        # Check what code was retrieved
        for field in code_fields:
            value = code_data.get(field)
            if value:
                print(f"✅ Retrieved {field}: {len(value)} characters")
            else:
                print(f"❌ Retrieved {field}: None or empty")
    else:
        print(f"❌ Code retrieval failed: {response.status_code} - {response.text}")
        return
    
    # Try iteration
    print("5. Testing iteration...")
    iteration_request = {
        "instruction": "Add a contact form to the website"
    }
    
    response = requests.post(f"{BASE_URL}/projects/{project_id}/iterate", 
                           json=iteration_request, headers=headers)
    
    print(f"Iteration status: {response.status_code}")
    if response.status_code == 200:
        iter_data = response.json()
        print(f"✅ Iteration successful: {iter_data}")
    else:
        print(f"❌ Iteration failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_generation_debug()