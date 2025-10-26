#!/usr/bin/env python3
"""
🚀 REAL DEPLOYMENT TEST WITH VALID GITHUB REPO
Test deployment with a real GitHub repository to verify the full pipeline
"""

import requests
import json
import sys
import time

BASE_URL = "https://codeforge-108.preview.emergentagent.com/api"

def test_real_deployment():
    """Test deployment with a real GitHub repository"""
    
    # Login
    test_user = {
        "email": "deploy-test@vectort.io",
        "password": "DeployTest123!",
        "full_name": "Deployment Tester"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=test_user)
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Get projects
    projects_response = requests.get(f"{BASE_URL}/projects", headers=headers)
    projects = projects_response.json()
    project_id = projects[0]["id"]
    
    print(f"📋 Using project ID: {project_id}")
    
    # Test deployment with a real, simple React repository
    deployment_data = {
        "platform": "vercel",
        "github_repo_url": "https://github.com/vercel/next.js/tree/canary/examples/hello-world",
        "project_name": "vectort-test-deploy-real",
        "framework": "nextjs"
    }
    
    print("\n🚀 Testing deployment with real GitHub repo...")
    print(f"Repository: {deployment_data['github_repo_url']}")
    print(f"Platform: {deployment_data['platform']}")
    
    response = requests.post(f"{BASE_URL}/projects/{project_id}/deploy", 
                           json=deployment_data, headers=headers)
    
    print(f"\n📊 Response Status: {response.status_code}")
    
    try:
        response_data = response.json()
        print(f"📋 Response Body:")
        print(json.dumps(response_data, indent=2))
        
        # Analyze the response
        success = response_data.get("success", False)
        platform = response_data.get("platform", "")
        status = response_data.get("status", "")
        error = response_data.get("error", "")
        deployment_url = response_data.get("deployment_url", "")
        deployment_id = response_data.get("deployment_id", "")
        
        print(f"\n🔍 DEPLOYMENT ANALYSIS:")
        print(f"   Success: {success}")
        print(f"   Platform: {platform}")
        print(f"   Status: {status}")
        print(f"   Deployment URL: {deployment_url}")
        print(f"   Deployment ID: {deployment_id}")
        print(f"   Error: {error}")
        
        if success and deployment_url:
            print("🎉 DEPLOYMENT SUCCESSFUL!")
            print(f"   Live URL: {deployment_url}")
        elif not success and error:
            print("⚠️ DEPLOYMENT FAILED (Expected for test repo)")
            print(f"   Reason: {error}")
        else:
            print("❓ DEPLOYMENT STATUS UNCLEAR")
            
    except json.JSONDecodeError:
        print(f"❌ Response is not valid JSON: {response.text}")

    # Test all three platforms
    platforms_to_test = [
        {
            "platform": "netlify",
            "github_repo_url": "https://github.com/netlify/netlify-feature-tour",
            "project_name": "vectort-netlify-test",
            "build_command": "npm run build",
            "publish_dir": "dist"
        },
        {
            "platform": "render",
            "github_repo_url": "https://github.com/render-examples/fastapi",
            "project_name": "vectort-render-test",
            "build_command": "pip install -r requirements.txt",
            "start_command": "uvicorn main:app --host 0.0.0.0 --port $PORT"
        }
    ]
    
    for platform_config in platforms_to_test:
        print(f"\n🔄 Testing {platform_config['platform'].upper()} deployment...")
        
        response = requests.post(f"{BASE_URL}/projects/{project_id}/deploy", 
                               json=platform_config, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        try:
            data = response.json()
            success = data.get("success", False)
            error = data.get("error", "")
            deployment_url = data.get("deployment_url", "")
            
            if success and deployment_url:
                print(f"✅ {platform_config['platform'].upper()} deployment successful: {deployment_url}")
            else:
                print(f"⚠️ {platform_config['platform'].upper()} deployment failed: {error}")
                
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON response")

if __name__ == "__main__":
    test_real_deployment()