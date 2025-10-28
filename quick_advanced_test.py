#!/usr/bin/env python3
"""
Quick test for advanced mode fix
"""

import requests
import json
import time

BASE_URL = "https://devstream-ai.preview.emergentagent.com/api"
TEST_USER = {
    "email": "js_tester@vectort.io",
    "password": "TestPassword123!"
}

def test_advanced_mode_fix():
    print("🔧 Testing Advanced Mode Fix...")
    
    # Login
    login_response = requests.post(f"{BASE_URL}/auth/login", json=TEST_USER, timeout=30)
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create project
    project_data = {
        "title": "Test Advanced Mode Fix",
        "description": "Simple React counter application",
        "type": "web_app"
    }
    
    project_response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers, timeout=30)
    if project_response.status_code != 200:
        print("❌ Project creation failed")
        return False
    
    project_id = project_response.json()["id"]
    print(f"✅ Project created: {project_id}")
    
    # Test advanced mode generation
    generation_data = {
        "description": "Simple React counter with increment and decrement buttons",
        "type": "web_app",
        "framework": "react",
        "advanced_mode": True
    }
    
    print("🚀 Testing advanced mode generation...")
    start_time = time.time()
    
    gen_response = requests.post(
        f"{BASE_URL}/projects/{project_id}/generate", 
        json=generation_data, 
        headers=headers, 
        timeout=60
    )
    
    generation_time = time.time() - start_time
    
    if gen_response.status_code != 200:
        print(f"❌ Generation failed: {gen_response.status_code}")
        if gen_response.text:
            print(f"Error: {gen_response.text}")
        return False
    
    data = gen_response.json()
    
    # Check results
    html_length = len(data.get("html_code", "") or "")
    css_length = len(data.get("css_code", "") or "")
    react_length = len(data.get("react_code", "") or "")
    files_count = len(data.get("all_files", {}) or {})
    
    print(f"📊 Results:")
    print(f"   ⏱️  Time: {generation_time:.1f}s")
    print(f"   📄 HTML: {html_length} chars")
    print(f"   🎨 CSS: {css_length} chars")
    print(f"   ⚛️  React: {react_length} chars")
    print(f"   📁 Files: {files_count}")
    
    # Success criteria
    success = (
        html_length > 200 and
        css_length > 300 and
        react_length > 1000 and
        files_count >= 3
    )
    
    if success:
        print("✅ ADVANCED MODE FIX SUCCESSFUL!")
        print("   All criteria met - code is no longer empty")
        return True
    else:
        print("❌ ADVANCED MODE STILL HAS ISSUES")
        print(f"   HTML>200: {'✅' if html_length > 200 else '❌'}")
        print(f"   CSS>300: {'✅' if css_length > 300 else '❌'}")
        print(f"   React>1000: {'✅' if react_length > 1000 else '❌'}")
        print(f"   Files>=3: {'✅' if files_count >= 3 else '❌'}")
        return False

if __name__ == "__main__":
    success = test_advanced_mode_fix()
    exit(0 if success else 1)