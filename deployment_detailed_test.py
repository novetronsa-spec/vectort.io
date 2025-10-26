#!/usr/bin/env python3
"""
🔍 DETAILED DEPLOYMENT RESPONSE ANALYSIS
Investigate what's actually happening with deployment responses
"""

import requests
import json
import sys
import time

BASE_URL = "https://omniai-platform-2.preview.emergentagent.com/api"

def test_deployment_responses():
    """Test deployment responses in detail"""
    
    # First, get auth token
    test_user = {
        "email": "deploy-test@vectort.io",
        "password": "DeployTest123!",
        "full_name": "Deployment Tester"
    }
    
    # Login
    login_response = requests.post(f"{BASE_URL}/auth/login", json=test_user)
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Get projects
    projects_response = requests.get(f"{BASE_URL}/projects", headers=headers)
    if projects_response.status_code != 200:
        print("❌ Failed to get projects")
        return
    
    projects = projects_response.json()
    if not projects:
        print("❌ No projects found")
        return
    
    project_id = projects[0]["id"]
    print(f"📋 Using project ID: {project_id}")
    
    # Test deployment with non-existent repo
    deployment_data = {
        "platform": "vercel",
        "github_repo_url": "https://github.com/nonexistent-user/nonexistent-repo",
        "project_name": "test-deploy",
        "framework": "react"
    }
    
    print("\n🚀 Testing deployment with non-existent GitHub repo...")
    print(f"Request data: {json.dumps(deployment_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/projects/{project_id}/deploy", 
                           json=deployment_data, headers=headers)
    
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📄 Response Headers: {dict(response.headers)}")
    
    try:
        response_data = response.json()
        print(f"📋 Response Body:")
        print(json.dumps(response_data, indent=2))
        
        # Analyze the response
        if response.status_code == 200:
            success = response_data.get("success", False)
            platform = response_data.get("platform", "")
            status = response_data.get("status", "")
            error = response_data.get("error", "")
            deployment_url = response_data.get("deployment_url", "")
            
            print(f"\n🔍 ANALYSIS:")
            print(f"   Success: {success}")
            print(f"   Platform: {platform}")
            print(f"   Status: {status}")
            print(f"   Error: {error}")
            print(f"   Deployment URL: {deployment_url}")
            
            if not success and error:
                print("✅ CORRECT: API properly handled error case")
            elif success and deployment_url:
                print("⚠️ UNEXPECTED: Deployment actually succeeded?")
            else:
                print("❓ UNCLEAR: Mixed signals in response")
        
    except json.JSONDecodeError:
        print(f"❌ Response is not valid JSON: {response.text}")

if __name__ == "__main__":
    test_deployment_responses()