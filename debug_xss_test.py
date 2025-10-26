#!/usr/bin/env python3
"""
Debug XSS Protection - Check what's actually being stored
"""

import requests
import json

BASE_URL = "https://omniai-platform-2.preview.emergentagent.com/api"

# Setup test user
test_user = {
    "email": "debug.xss@example.com",
    "password": "DebugTest123!",
    "full_name": "Debug XSS Tester"
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
        xss_payload = "<script>alert('XSS')</script>"
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
            stored_description = data.get("description", "")
            print(f"Stored description: {stored_description}")
            print(f"Contains <script>: {'<script>' in stored_description}")
            print(f"Contains &lt;script&gt;: {'&lt;script&gt;' in stored_description}")
            print(f"Raw bytes: {stored_description.encode()}")
        else:
            print(f"Error: {project_response.text}")
    else:
        print(f"Auth failed: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")