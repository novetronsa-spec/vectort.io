import sys
sys.path.insert(0, '/app/backend')

from ai_generators.javascript_optimizer import JavaScriptOptimizer

print("🧪 TEST DES TIMEOUTS ADAPTATIFS\n" + "="*80)

optimizer = JavaScriptOptimizer("dummy_key")

# Test 1: Projet TRÈS simple
timeout_very_simple = optimizer.calculate_adaptive_timeout(
    description="Simple counter",
    project_type="web_app",
    features=[]
)
print(f"\n✅ Test 1 - Très Simple:")
print(f"   Description: 'Simple counter' (14 chars)")
print(f"   Type: web_app, Features: 0")
print(f"   ⏱️  Timeout: {timeout_very_simple}s")

# Test 2: Projet simple  
timeout_simple = optimizer.calculate_adaptive_timeout(
    description="Une simple application React avec un compteur et un bouton pour incrémenter",
    project_type="web_app",
    features=["counter"]
)
print(f"\n✅ Test 2 - Simple:")
print(f"   Description: 'Une simple application...' (83 chars)")
print(f"   Type: web_app, Features: 1")
print(f"   ⏱️  Timeout: {timeout_simple}s")

# Test 3: Projet moyen
timeout_medium = optimizer.calculate_adaptive_timeout(
    description="E-commerce application with shopping cart and product catalog",
    project_type="web_app",
    features=["authentication", "database"]
)
print(f"\n✅ Test 3 - Moyen:")
print(f"   Description: 'E-commerce application...' (66 chars)")
print(f"   Type: web_app, Features: 2")
print(f"   Keywords: authentication, database")
print(f"   ⏱️  Timeout: {timeout_medium}s")

# Test 4: Projet complexe
timeout_complex = optimizer.calculate_adaptive_timeout(
    description="Complex full-stack application with authentication, real-time chat, payment processing, admin dashboard, analytics, image upload, and email notifications",
    project_type="full_stack",
    features=["authentication", "real-time", "payment", "admin", "analytics", "upload", "email", "database", "websocket"]
)
print(f"\n✅ Test 4 - Complexe:")
print(f"   Description: 'Complex full-stack...' (159 chars)")
print(f"   Type: full_stack, Features: 9")
print(f"   Keywords: authentication, real-time, payment, admin, analytics, upload, email, database, websocket")
print(f"   ⏱️  Timeout: {timeout_complex}s")

# Validation
print("\n" + "="*80)
print("📊 VALIDATION:")
print(f"   Très Simple: {timeout_very_simple}s")
print(f"   Simple: {timeout_simple}s")
print(f"   Moyen: {timeout_medium}s")
print(f"   Complexe: {timeout_complex}s")

progression_ok = (
    timeout_very_simple < timeout_simple < timeout_medium < timeout_complex
)

if progression_ok:
    print("\n✅ SUCCÈS! Progression croissante correcte:")
    print(f"   {timeout_very_simple}s < {timeout_simple}s < {timeout_medium}s < {timeout_complex}s")
    sys.exit(0)
else:
    print("\n❌ ÉCHEC! Progression incorrecte")
    sys.exit(1)
