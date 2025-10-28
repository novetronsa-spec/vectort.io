#!/usr/bin/env python3
"""
Debug script to see what's happening in advanced mode
"""

import requests
import json
import time

BASE_URL = "https://devstream-ai.preview.emergentagent.com/api"

def test_advanced_mode():
    # Login with test user
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "js_tester@vectort.io",
        "password": "TestPassword123!"
    })
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create project
    project_response = requests.post(f"{BASE_URL}/projects", 
        json={
            "title": "Debug Advanced Mode",
            "description": "Simple React app for debugging",
            "type": "web_app"
        },
        headers=headers
    )
    
    if project_response.status_code != 200:
        print(f"Project creation failed: {project_response.status_code}")
        return
    
    project_id = project_response.json()["id"]
    print(f"Created project: {project_id}")
    
    # Generate with advanced mode
    generation_response = requests.post(f"{BASE_URL}/projects/{project_id}/generate",
        json={
            "description": "Simple React counter app",
            "type": "web_app", 
            "framework": "react",
            "advanced_mode": True
        },
        headers=headers,
        timeout=120
    )
    
    print(f"Generation status: {generation_response.status_code}")
    
    if generation_response.status_code == 200:
        data = generation_response.json()
        
        print("\n=== GENERATION RESPONSE ===")
        print(f"HTML code length: {len(data.get('html_code') or '')}")
        print(f"CSS code length: {len(data.get('css_code') or '')}")
        print(f"JS code length: {len(data.get('js_code') or '')}")
        print(f"React code length: {len(data.get('react_code') or '')}")
        print(f"Backend code length: {len(data.get('backend_code') or '')}")
        print(f"All files count: {len(data.get('all_files') or {})}")
        
        all_files = data.get('all_files', {})
        if all_files:
            print(f"\n=== ALL_FILES KEYS ===")
            for key, value in all_files.items():
                print(f"  {key}: {len(str(value))} chars")
        
        # Check if any field has content
        has_content = any([
            data.get('html_code'),
            data.get('css_code'), 
            data.get('js_code'),
            data.get('react_code'),
            data.get('backend_code')
        ])
        
        print(f"\nHas main content: {has_content}")
        
        # Try to retrieve the code
        code_response = requests.get(f"{BASE_URL}/projects/{project_id}/code", headers=headers)
        if code_response.status_code == 200:
            code_data = code_response.json()
            print(f"\n=== CODE RETRIEVAL ===")
            print(f"HTML: {len(code_data.get('html_code') or '')}")
            print(f"CSS: {len(code_data.get('css_code') or '')}")
            print(f"React: {len(code_data.get('react_code') or '')}")
            print(f"All files: {len(code_data.get('all_files') or {})}")
        
    else:
        print(f"Generation failed: {generation_response.text}")

if __name__ == "__main__":
    test_advanced_mode()