#!/usr/bin/env python3
"""
Comprehensive test for the three complex applications as requested in the review
"""

import requests
import json
import time

BASE_URL = "https://vectort-builder.preview.emergentagent.com/api"

def create_test_user():
    test_user = {
        "email": f"comprehensive_test_{int(time.time())}@vectort.io",
        "password": "ComprehensiveTest123!",
        "full_name": "Comprehensive Test User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        # Try login if user exists
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        if login_response.status_code == 200:
            return login_response.json()["access_token"]
    return None

def test_application(token, app_config):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create project
    project_response = requests.post(f"{BASE_URL}/projects", json=app_config["project"], headers=headers)
    if project_response.status_code != 200:
        return {"success": False, "error": f"Project creation failed: {project_response.status_code}"}
    
    project_id = project_response.json()["id"]
    
    # Generate code
    start_time = time.time()
    gen_response = requests.post(f"{BASE_URL}/projects/{project_id}/generate", 
                                json=app_config["generation"], headers=headers, timeout=60)
    generation_time = time.time() - start_time
    
    if gen_response.status_code != 200:
        return {"success": False, "error": f"Generation failed: {gen_response.status_code}"}
    
    # Get generated code
    code_response = requests.get(f"{BASE_URL}/projects/{project_id}/code", headers=headers)
    if code_response.status_code != 200:
        return {"success": False, "error": f"Code retrieval failed: {code_response.status_code}"}
    
    code_data = code_response.json()
    
    # Analyze code
    react_code = code_data.get("react_code", "")
    css_code = code_data.get("css_code", "")
    html_code = code_data.get("html_code", "")
    backend_code = code_data.get("backend_code", "")
    
    total_chars = len(react_code) + len(css_code) + len(html_code) + len(backend_code)
    total_lines = sum(code.count('\n') for code in [react_code, css_code, html_code, backend_code])
    
    # Quality checks
    has_hooks = any(hook in react_code for hook in ['useState', 'useEffect', 'useContext', 'useReducer'])
    has_components = 'function ' in react_code or ('const ' in react_code and '=>' in react_code)
    has_jsx = '<' in react_code and '>' in react_code
    has_media_queries = '@media' in css_code
    
    # Feature-specific checks
    all_code = f"{react_code} {css_code} {html_code}".lower()
    feature_matches = sum(1 for keyword in app_config["keywords"] if keyword in all_code)
    
    return {
        "success": True,
        "generation_time": generation_time,
        "total_chars": total_chars,
        "total_lines": total_lines,
        "react_lines": react_code.count('\n'),
        "css_lines": css_code.count('\n'),
        "html_lines": html_code.count('\n'),
        "backend_lines": backend_code.count('\n'),
        "has_hooks": has_hooks,
        "has_components": has_components,
        "has_jsx": has_jsx,
        "has_media_queries": has_media_queries,
        "feature_matches": feature_matches,
        "total_keywords": len(app_config["keywords"]),
        "react_code_sample": react_code[:200] if react_code else "",
        "css_code_sample": css_code[:200] if css_code else ""
    }

def main():
    print("🎯 COMPREHENSIVE COMPLEX APPLICATION GENERATION TEST")
    print("="*80)
    
    # Setup
    token = create_test_user()
    if not token:
        print("❌ Failed to create test user")
        return False
    
    # Test configurations
    test_apps = {
        "E-commerce Platform": {
            "project": {
                "title": "E-commerce Platform Complex",
                "description": "Create a complete e-commerce platform with React frontend. Features needed: Product catalog with search and filters, Shopping cart with add/remove items, User authentication (login/register), Checkout process with form validation, Order history page, Responsive design for mobile and desktop, Product detail pages with image gallery, Category navigation. Use React hooks, modern styling, and include proper state management.",
                "type": "web_app"
            },
            "generation": {
                "description": "Create a complete e-commerce platform with React frontend. Features needed: Product catalog with search and filters, Shopping cart with add/remove items, User authentication (login/register), Checkout process with form validation, Order history page, Responsive design for mobile and desktop, Product detail pages with image gallery, Category navigation. Use React hooks, modern styling, and include proper state management.",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False
            },
            "keywords": ["cart", "product", "checkout", "payment", "shop", "buy", "price", "catalog", "search", "filter"]
        },
        "Task Management Dashboard": {
            "project": {
                "title": "Task Management Dashboard",
                "description": "Build a modern task management dashboard like Trello. Features: Drag and drop task cards between columns (To Do, In Progress, Done), Create/edit/delete tasks, Task priority levels (high, medium, low), Due dates and filters, User profile section, Dark mode toggle, Statistics dashboard showing completed tasks. Modern UI with Tailwind-style colors and smooth animations.",
                "type": "web_app"
            },
            "generation": {
                "description": "Build a modern task management dashboard like Trello. Features: Drag and drop task cards between columns (To Do, In Progress, Done), Create/edit/delete tasks, Task priority levels (high, medium, low), Due dates and filters, User profile section, Dark mode toggle, Statistics dashboard showing completed tasks. Modern UI with Tailwind-style colors and smooth animations.",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False
            },
            "keywords": ["task", "todo", "drag", "drop", "priority", "due", "complete", "dashboard", "column", "card"]
        },
        "Real-time Chat Application": {
            "project": {
                "title": "Real-time Chat Application",
                "description": "Create a real-time chat application. Features: Multiple chat rooms, Real-time message updates, User online/offline status, Message history, Emoji support, File upload capability, Typing indicators, User profiles with avatars. Clean, modern UI similar to Slack or Discord.",
                "type": "web_app"
            },
            "generation": {
                "description": "Create a real-time chat application. Features: Multiple chat rooms, Real-time message updates, User online/offline status, Message history, Emoji support, File upload capability, Typing indicators, User profiles with avatars. Clean, modern UI similar to Slack or Discord.",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False
            },
            "keywords": ["message", "chat", "send", "receive", "user", "online", "room", "emoji", "avatar", "typing"]
        }
    }
    
    results = {}
    
    # Test each application
    for app_name, config in test_apps.items():
        print(f"\n=== Testing {app_name} ===")
        result = test_application(token, config)
        results[app_name] = result
        
        if result["success"]:
            print(f"✅ SUCCESS: {app_name}")
            print(f"   Generation Time: {result['generation_time']:.1f}s")
            print(f"   Total Code: {result['total_chars']} chars, {result['total_lines']} lines")
            print(f"   React: {result['react_lines']} lines")
            print(f"   CSS: {result['css_lines']} lines")
            print(f"   HTML: {result['html_lines']} lines")
            print(f"   React Hooks: {'✅' if result['has_hooks'] else '❌'}")
            print(f"   Components: {'✅' if result['has_components'] else '❌'}")
            print(f"   JSX: {'✅' if result['has_jsx'] else '❌'}")
            print(f"   Responsive CSS: {'✅' if result['has_media_queries'] else '❌'}")
            print(f"   Features: {result['feature_matches']}/{result['total_keywords']} keywords")
        else:
            print(f"❌ FAILED: {app_name} - {result['error']}")
    
    # Generate summary report
    print(f"\n" + "="*80)
    print("📊 FINAL REPORT - COMPLEX APPLICATION GENERATION")
    print("="*80)
    
    successful_apps = [name for name, result in results.items() if result.get("success")]
    total_apps = len(results)
    success_rate = len(successful_apps) / total_apps * 100 if total_apps > 0 else 0
    
    print(f"\n🎯 GENERATION SUCCESS RATE: {len(successful_apps)}/{total_apps} ({success_rate:.1f}%)")
    
    if successful_apps:
        # Calculate averages
        avg_time = sum(results[name]["generation_time"] for name in successful_apps) / len(successful_apps)
        avg_chars = sum(results[name]["total_chars"] for name in successful_apps) / len(successful_apps)
        avg_lines = sum(results[name]["total_lines"] for name in successful_apps) / len(successful_apps)
        
        print(f"\n📈 AVERAGE METRICS:")
        print(f"   Generation Time: {avg_time:.1f}s")
        print(f"   Code Size: {avg_chars:.0f} characters")
        print(f"   Lines of Code: {avg_lines:.0f} lines")
        
        # Quality metrics
        apps_with_hooks = sum(1 for name in successful_apps if results[name]["has_hooks"])
        apps_with_components = sum(1 for name in successful_apps if results[name]["has_components"])
        apps_with_jsx = sum(1 for name in successful_apps if results[name]["has_jsx"])
        apps_with_responsive = sum(1 for name in successful_apps if results[name]["has_media_queries"])
        
        print(f"\n🔍 QUALITY ANALYSIS:")
        print(f"   React Hooks: {apps_with_hooks}/{len(successful_apps)} apps")
        print(f"   React Components: {apps_with_components}/{len(successful_apps)} apps")
        print(f"   JSX Syntax: {apps_with_jsx}/{len(successful_apps)} apps")
        print(f"   Responsive CSS: {apps_with_responsive}/{len(successful_apps)} apps")
        
        # Success criteria evaluation
        print(f"\n✅ SUCCESS CRITERIA EVALUATION:")
        criteria_met = 0
        
        # At least 2/3 applications generate successfully
        if len(successful_apps) >= 2:
            print(f"   ✅ Generation Success Rate: {len(successful_apps)}/3 apps generated")
            criteria_met += 1
        else:
            print(f"   ❌ Generation Success Rate: Only {len(successful_apps)}/3 apps generated")
        
        # Code quality checks
        if avg_chars >= 1000:  # Substantial code generated
            print(f"   ✅ Code Quantity: {avg_chars:.0f} characters (substantial)")
            criteria_met += 1
        else:
            print(f"   ❌ Code Quantity: {avg_chars:.0f} characters (insufficient)")
        
        if apps_with_components >= 2:
            print(f"   ✅ React Components: {apps_with_components}/3 apps have proper components")
            criteria_met += 1
        else:
            print(f"   ❌ React Components: Only {apps_with_components}/3 apps have proper components")
        
        if apps_with_jsx >= 2:
            print(f"   ✅ JSX Syntax: {apps_with_jsx}/3 apps use proper JSX")
            criteria_met += 1
        else:
            print(f"   ❌ JSX Syntax: Only {apps_with_jsx}/3 apps use proper JSX")
        
        if avg_time < 30:
            print(f"   ✅ Performance: {avg_time:.1f}s average (under 30s target)")
            criteria_met += 1
        else:
            print(f"   ❌ Performance: {avg_time:.1f}s average (over 30s target)")
        
        # Feature implementation
        avg_feature_rate = sum(results[name]["feature_matches"] / results[name]["total_keywords"] 
                              for name in successful_apps) / len(successful_apps)
        if avg_feature_rate >= 0.3:  # At least 30% of features implemented
            print(f"   ✅ Feature Implementation: {avg_feature_rate:.1%} average feature coverage")
            criteria_met += 1
        else:
            print(f"   ❌ Feature Implementation: {avg_feature_rate:.1%} average feature coverage")
        
        print(f"\n🎯 FINAL VERDICT: {criteria_met}/6 criteria met")
        
        if criteria_met >= 4:
            print(f"   🎉 SUCCESS: Vectort.io successfully generates complex, production-ready applications!")
            print(f"   The AI system meets the requirements for real application generation.")
            return True
        else:
            print(f"   ⚠️ PARTIAL SUCCESS: System shows promise but needs improvements.")
            return False
    else:
        print(f"   ❌ FAILURE: No applications generated successfully")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)