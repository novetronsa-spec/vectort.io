#!/usr/bin/env python3
"""
Debug the XSS test specifically
"""

import requests
import re

BASE_URL = "https://omniai-platform-2.preview.emergentagent.com/api"

# Setup test user
test_user = {
    "email": "debug.security@example.com",
    "password": "DebugSecurity123!",
    "full_name": "Debug Security Tester"
}

# Register or login
try:
    response = requests.post(f"{BASE_URL}/auth/register", json=test_user, timeout=30)
    if response.status_code == 400:
        # User exists, login
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        }, timeout=30)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Test XSS payload
        xss_payload = "<script>alert('XSS in description')</script><img src=x onerror=alert('XSS2')>"
        project_data = {
            "title": "XSS Test",
            "description": xss_payload,
            "type": "web_app"
        }
        
        print(f"Original payload: {xss_payload}")
        
        project_response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers, timeout=30)
        
        print(f"Response status: {project_response.status_code}")
        if project_response.status_code == 200:
            data = project_response.json()
            returned_description = data.get("description", "")
            print(f"Returned description: {returned_description}")
            
            # Test the logic
            dangerous_patterns = ["<script>", "onerror=", "javascript:", "onload=", "<iframe", "<object", "<embed"]
            has_dangerous_content = any(pattern in returned_description for pattern in dangerous_patterns)
            print(f"Has dangerous content: {has_dangerous_content}")
            
            unescaped_html = re.search(r'<(?!/?[a-zA-Z][^>]*>)[^&].*?>', returned_description)
            print(f"Unescaped HTML found: {unescaped_html is not None}")
            
            has_escaped_content = "&amp;" in returned_description and ("lt;" in returned_description or "gt;" in returned_description)
            print(f"Has escaped content: {has_escaped_content}")
            
            if has_dangerous_content or unescaped_html:
                print("❌ CRITICAL: XSS payload stored unsanitized")
            else:
                if has_escaped_content:
                    print("✅ XSS payload was properly HTML-escaped and safe")
                else:
                    print("✅ XSS payload was sanitized")
        else:
            print(f"Error: {project_response.text}")
    else:
        print(f"Auth failed: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")