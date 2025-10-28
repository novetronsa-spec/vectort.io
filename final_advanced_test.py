#!/usr/bin/env python3
"""
Final Advanced Mode Test with Unique Descriptions
"""

import requests
import json
import time
import uuid

BASE_URL = "https://devstream-ai.preview.emergentagent.com/api"
TEST_USER = {
    "email": "js_tester@vectort.io",
    "password": "TestPassword123!"
}

def test_advanced_mode_scenarios():
    print("🎯 FINAL ADVANCED MODE TEST - Unique Descriptions")
    print("=" * 60)
    
    # Login
    login_response = requests.post(f"{BASE_URL}/auth/login", json=TEST_USER, timeout=30)
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test scenarios with unique descriptions to avoid cache
    scenarios = [
        {
            "name": "Simple Counter",
            "description": f"React counter app with buttons and state management {uuid.uuid4()}",
            "expected_complexity": "simple"
        },
        {
            "name": "Todo Application", 
            "description": f"Task management system with add, delete, complete features {uuid.uuid4()}",
            "expected_complexity": "medium"
        },
        {
            "name": "E-commerce Platform",
            "description": f"Online store with shopping cart, payment integration, user authentication {uuid.uuid4()}",
            "expected_complexity": "complex"
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {scenario['name']}")
        print(f"📝 Description: {scenario['description'][:80]}...")
        
        # Create project
        project_data = {
            "title": f"Test {scenario['name']} {int(time.time())}",
            "description": scenario['description'],
            "type": "web_app"
        }
        
        project_response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers, timeout=30)
        if project_response.status_code != 200:
            print(f"❌ Project creation failed")
            continue
        
        project_id = project_response.json()["id"]
        
        # Test advanced mode
        generation_data = {
            "description": scenario['description'],
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
            timeout=90
        )
        
        generation_time = time.time() - start_time
        
        if gen_response.status_code != 200:
            print(f"❌ Generation failed: {gen_response.status_code}")
            if gen_response.text:
                error_detail = gen_response.json().get("detail", "Unknown error")
                print(f"Error: {error_detail}")
            continue
        
        data = gen_response.json()
        
        # Analyze results
        html_length = len(data.get("html_code", "") or "")
        css_length = len(data.get("css_code", "") or "")
        react_length = len(data.get("react_code", "") or "")
        files_count = len(data.get("all_files", {}) or {})
        total_length = html_length + css_length + react_length
        
        print(f"📊 Results:")
        print(f"   ⏱️  Time: {generation_time:.1f}s")
        print(f"   📄 HTML: {html_length} chars")
        print(f"   🎨 CSS: {css_length} chars")
        print(f"   ⚛️  React: {react_length} chars")
        print(f"   📁 Files: {files_count}")
        print(f"   📊 Total: {total_length} chars")
        
        # Success criteria from review
        criteria = {
            "HTML > 200": html_length > 200,
            "CSS > 300": css_length > 300,
            "React > 1000": react_length > 1000,
            "Files >= 3": files_count >= 3,
            "Time < 30s": generation_time < 30.0
        }
        
        success = all(criteria.values())
        
        if success:
            print("✅ SUCCESS - All criteria met!")
        else:
            print("❌ PARTIAL SUCCESS - Some criteria not met:")
            for criterion, passed in criteria.items():
                print(f"   {criterion}: {'✅' if passed else '❌'}")
        
        results.append({
            "scenario": scenario['name'],
            "success": success,
            "html_length": html_length,
            "css_length": css_length,
            "react_length": react_length,
            "files_count": files_count,
            "generation_time": generation_time,
            "total_length": total_length
        })
    
    # Final summary
    print(f"\n{'='*60}")
    print("🎯 FINAL SUMMARY - ADVANCED MODE TESTING")
    print("="*60)
    
    successful_scenarios = [r for r in results if r['success']]
    success_rate = len(successful_scenarios) / len(results) * 100 if results else 0
    
    print(f"✅ Successful Scenarios: {len(successful_scenarios)}/{len(results)}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if successful_scenarios:
        avg_time = sum(r['generation_time'] for r in successful_scenarios) / len(successful_scenarios)
        avg_total = sum(r['total_length'] for r in successful_scenarios) / len(successful_scenarios)
        print(f"⏱️  Average Generation Time: {avg_time:.1f}s")
        print(f"📊 Average Code Length: {avg_total:.0f} chars")
    
    print(f"\n📋 Detailed Results:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"   {status} {result['scenario']}: {result['total_length']} chars, {result['generation_time']:.1f}s")
    
    # Determine overall status
    if success_rate >= 80:
        print(f"\n🎉 ADVANCED MODE CORRECTION: SUCCESSFUL!")
        print(f"   Le mode avancé génère maintenant du code NON VIDE")
        print(f"   Critères de succès respectés: HTML>200, CSS>300, React>1000, Files>=3")
        return True
    else:
        print(f"\n🚨 ADVANCED MODE: NEEDS MORE WORK")
        print(f"   Certains scénarios échouent encore")
        return False

if __name__ == "__main__":
    success = test_advanced_mode_scenarios()
    exit(0 if success else 1)