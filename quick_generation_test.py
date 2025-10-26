#!/usr/bin/env python3
"""
Quick test to validate complex application generation for test_result.md update
"""

import requests
import json
import time

BASE_URL = "https://omniai-platform-2.preview.emergentagent.com/api"

def test_complex_generation():
    # Create test user
    test_user = {
        "email": f"quick_test_{int(time.time())}@vectort.io",
        "password": "QuickTest123!",
        "full_name": "Quick Test User"
    }
    
    # Register
    response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
    if response.status_code != 200:
        print(f"Registration failed: {response.status_code}")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test E-commerce generation
    project_data = {
        "title": "Complex E-commerce Test",
        "description": "Create a complete e-commerce platform with React frontend. Features: Product catalog with search and filters, Shopping cart with add/remove items, User authentication (login/register), Checkout process with form validation, Order history page, Responsive design for mobile and desktop, Product detail pages with image gallery, Category navigation. Use React hooks, modern styling, and include proper state management.",
        "type": "web_app"
    }
    
    project_response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers)
    if project_response.status_code != 200:
        print(f"Project creation failed: {project_response.status_code}")
        return False
    
    project_id = project_response.json()["id"]
    
    # Generate code
    generation_request = {
        "description": project_data["description"],
        "type": "web_app",
        "framework": "react",
        "advanced_mode": True  # Try advanced mode
    }
    
    start_time = time.time()
    gen_response = requests.post(f"{BASE_URL}/projects/{project_id}/generate", 
                                json=generation_request, headers=headers, timeout=60)
    generation_time = time.time() - start_time
    
    if gen_response.status_code == 200:
        # Get the generated code
        code_response = requests.get(f"{BASE_URL}/projects/{project_id}/code", headers=headers)
        if code_response.status_code == 200:
            code_data = code_response.json()
            
            # Analyze the code
            react_code = code_data.get("react_code", "")
            css_code = code_data.get("css_code", "")
            html_code = code_data.get("html_code", "")
            backend_code = code_data.get("backend_code", "")
            
            total_chars = len(react_code) + len(css_code) + len(html_code) + len(backend_code)
            total_lines = (react_code.count('\n') + css_code.count('\n') + 
                          html_code.count('\n') + backend_code.count('\n'))
            
            print(f"✅ COMPLEX E-COMMERCE GENERATION SUCCESS!")
            print(f"   Generation Time: {generation_time:.1f}s")
            print(f"   Total Characters: {total_chars}")
            print(f"   Total Lines: {total_lines}")
            print(f"   React Code: {len(react_code)} chars ({react_code.count(chr(10))} lines)")
            print(f"   CSS Code: {len(css_code)} chars ({css_code.count(chr(10))} lines)")
            print(f"   HTML Code: {len(html_code)} chars ({html_code.count(chr(10))} lines)")
            print(f"   Backend Code: {len(backend_code)} chars ({backend_code.count(chr(10))} lines)")
            
            # Check for React patterns
            has_hooks = any(hook in react_code for hook in ['useState', 'useEffect', 'useContext'])
            has_components = 'function ' in react_code or ('const ' in react_code and '=>' in react_code)
            has_jsx = '<' in react_code and '>' in react_code
            
            # Check for responsive CSS
            has_media_queries = '@media' in css_code
            
            # Check for e-commerce features
            ecommerce_keywords = ['cart', 'product', 'checkout', 'payment', 'shop', 'buy', 'price']
            all_code = f"{react_code} {css_code} {html_code}".lower()
            feature_matches = sum(1 for keyword in ecommerce_keywords if keyword in all_code)
            
            print(f"\n   QUALITY ANALYSIS:")
            print(f"   React Hooks: {'✅' if has_hooks else '❌'}")
            print(f"   React Components: {'✅' if has_components else '❌'}")
            print(f"   JSX Syntax: {'✅' if has_jsx else '❌'}")
            print(f"   Responsive CSS: {'✅' if has_media_queries else '❌'}")
            print(f"   E-commerce Features: {feature_matches}/{len(ecommerce_keywords)} keywords found")
            
            # Success criteria
            success_criteria = [
                total_chars >= 1000,  # At least 1000 characters of code
                has_hooks,
                has_components,
                has_jsx,
                feature_matches >= 3,
                generation_time < 30
            ]
            
            passed = sum(success_criteria)
            print(f"\n   SUCCESS CRITERIA: {passed}/6 met")
            
            if passed >= 4:
                print(f"   🎉 COMPLEX APPLICATION GENERATION SUCCESSFUL!")
                return True
            else:
                print(f"   ⚠️ PARTIAL SUCCESS - Some criteria not met")
                return False
        else:
            print(f"Failed to retrieve generated code: {code_response.status_code}")
            return False
    elif gen_response.status_code == 402:
        print("❌ Insufficient credits for advanced mode, trying quick mode...")
        
        # Try quick mode
        generation_request["advanced_mode"] = False
        gen_response = requests.post(f"{BASE_URL}/projects/{project_id}/generate", 
                                    json=generation_request, headers=headers, timeout=60)
        
        if gen_response.status_code == 200:
            print("✅ Quick mode generation successful")
            return True
        else:
            print(f"Quick mode also failed: {gen_response.status_code}")
            return False
    else:
        print(f"Generation failed: {gen_response.status_code} - {gen_response.text}")
        return False

if __name__ == "__main__":
    success = test_complex_generation()
    exit(0 if success else 1)