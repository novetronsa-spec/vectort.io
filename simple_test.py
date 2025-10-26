#!/usr/bin/env python3
"""
Simple test to check basic functionality
"""

import requests
import json
import time

BASE_URL = "https://omniai-platform-2.preview.emergentagent.com/api"

def test_basic_generation():
    # Register user
    test_user = {
        "email": f"simple.test.{int(time.time())}@vectort.io",
        "password": "SimpleTest123!",
        "full_name": f"Simple Test {int(time.time() % 1000000)}"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=test_user, timeout=15)
    if response.status_code != 200:
        print(f"❌ Registration failed: {response.status_code}")
        return
    
    access_token = response.json()["access_token"]
    print(f"✅ Authenticated")
    
    # Create project
    project_data = {
        "title": "Simple E-commerce Test",
        "description": "Boutique en ligne simple avec panier et paiement",
        "type": "ecommerce"
    }
    
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    project_response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers, timeout=15)
    
    if project_response.status_code != 200:
        print(f"❌ Project creation failed: {project_response.status_code}")
        return
    
    project_id = project_response.json()["id"]
    print(f"✅ Project created: {project_id}")
    
    # Test basic generation
    generation_request = {
        "description": "Boutique en ligne avec panier d'achats et catalogue de produits",
        "type": "ecommerce",
        "framework": "react",
        "advanced_mode": False
    }
    
    print("🚀 Testing basic generation...")
    start_time = time.time()
    gen_response = requests.post(f"{BASE_URL}/projects/{project_id}/generate", 
                                json=generation_request, headers=headers, timeout=30)
    generation_time = time.time() - start_time
    
    if gen_response.status_code == 200:
        data = gen_response.json()
        print(f"✅ Basic generation completed in {generation_time:.1f}s")
        
        # Check what was generated
        fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
        generated = []
        for field in fields:
            if data.get(field):
                generated.append(f"{field}({len(data[field])} chars)")
        
        print(f"📊 Generated: {', '.join(generated)}")
        
        # Test advanced mode with shorter timeout
        print("🚀 Testing advanced generation...")
        advanced_request = {
            "description": "Boutique en ligne complète avec React et MongoDB",
            "type": "ecommerce", 
            "framework": "react",
            "database": "mongodb",
            "advanced_mode": True,
            "features": ["authentication", "payment_processing"],
            "integrations": ["stripe"]
        }
        
        # Create new project for advanced test
        adv_project_data = {
            "title": "Advanced E-commerce Test",
            "description": "Advanced e-commerce test",
            "type": "ecommerce"
        }
        
        adv_project_response = requests.post(f"{BASE_URL}/projects", json=adv_project_data, headers=headers, timeout=15)
        if adv_project_response.status_code == 200:
            adv_project_id = adv_project_response.json()["id"]
            
            try:
                start_time = time.time()
                adv_gen_response = requests.post(f"{BASE_URL}/projects/{adv_project_id}/generate", 
                                               json=advanced_request, headers=headers, timeout=20)
                adv_generation_time = time.time() - start_time
                
                if adv_gen_response.status_code == 200:
                    adv_data = adv_gen_response.json()
                    print(f"✅ Advanced generation completed in {adv_generation_time:.1f}s")
                    
                    # Check advanced fields
                    advanced_fields = ["project_structure", "package_json", "dockerfile", "readme", "all_files"]
                    adv_generated = []
                    for field in advanced_fields:
                        if adv_data.get(field):
                            adv_generated.append(field)
                    
                    print(f"📊 Advanced fields: {', '.join(adv_generated)}")
                    
                    # Check basic fields too
                    basic_generated = []
                    for field in fields:
                        if adv_data.get(field):
                            basic_generated.append(f"{field}({len(adv_data[field])} chars)")
                    
                    print(f"📊 Basic fields: {', '.join(basic_generated)}")
                    
                else:
                    print(f"❌ Advanced generation failed: {adv_gen_response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"⏰ Advanced generation timed out after 20s")
        
    else:
        print(f"❌ Basic generation failed: {gen_response.status_code}")
        print(f"Response: {gen_response.text}")

if __name__ == "__main__":
    test_basic_generation()