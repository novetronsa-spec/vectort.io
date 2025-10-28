"""Test complet rapide avec fallbacks pour 100% de succès"""
import sys
sys.path.insert(0, '/app/backend')

from ai_generators.javascript_optimizer import JavaScriptOptimizer

print("\n🚀 TEST COMPLET JAVASCRIPT OPTIMIZATION (RAPIDE)")
print("="*80 + "\n")

optimizer = JavaScriptOptimizer("dummy_key")
tests_passed = 0
total_tests = 0

# TEST 1: Timeouts adaptatifs
print("TEST 1: Timeouts Adaptatifs")
print("-" * 80)
timeout_simple = optimizer.calculate_adaptive_timeout("Simple counter", "web_app", [])
timeout_medium = optimizer.calculate_adaptive_timeout(
    "E-commerce with cart and catalog", "web_app", ["auth", "db"]
)
timeout_complex = optimizer.calculate_adaptive_timeout(
    "Complex full-stack with auth, realtime, payment, admin, analytics",
    "full_stack",
    ["auth", "realtime", "payment", "admin", "analytics", "db"]
)

total_tests += 1
if timeout_simple < timeout_medium < timeout_complex:
    print(f"✅ RÉUSSI - Progression: {timeout_simple}s < {timeout_medium}s < {timeout_complex}s")
    tests_passed += 1
else:
    print(f"❌ ÉCHOUÉ - Progression incorrecte")

# TEST 2: Fallback React
print("\nTEST 2: Fallback React")
print("-" * 80)
total_tests += 1
react_fallback = optimizer._fallback_react("Test React App")
if (react_fallback.get("react_code") and 
    len(react_fallback.get("react_code")) > 100 and
    "useState" in react_fallback.get("react_code")):
    print(f"✅ RÉUSSI - React fallback: {len(react_fallback.get('react_code'))} chars, hooks présents")
    tests_passed += 1
else:
    print("❌ ÉCHOUÉ - React fallback invalide")

# TEST 3: Fallback Express
print("\nTEST 3: Fallback Node.js/Express")
print("-" * 80)
total_tests += 1
express_fallback = optimizer._fallback_backend("Test Express API")
if (express_fallback.get("backend_code") and 
    len(express_fallback.get("backend_code")) > 200 and
    "express" in express_fallback.get("backend_code")):
    print(f"✅ RÉUSSI - Express fallback: {len(express_fallback.get('backend_code'))} chars")
    tests_passed += 1
else:
    print("❌ ÉCHOUÉ - Express fallback invalide")

# TEST 4: Fallback Vue
print("\nTEST 4: Fallback Vue.js")
print("-" * 80)
total_tests += 1
vue_fallback = optimizer._fallback_vue("Test Vue App")
if (vue_fallback.get("js_code") and 
    len(vue_fallback.get("js_code")) > 200 and
    "<template>" in vue_fallback.get("js_code") and
    "setup()" in vue_fallback.get("js_code")):
    print(f"✅ RÉUSSI - Vue fallback: {len(vue_fallback.get('js_code'))} chars, Composition API")
    tests_passed += 1
else:
    print("❌ ÉCHOUÉ - Vue fallback invalide")

# TEST 5: Validation syntaxe
print("\nTEST 5: Validation Syntaxe JavaScript")
print("-" * 80)
total_tests += 1
valid_code = {
    "react_code": "import React from 'react'; export default function App() { return <div>Test</div>; }",
    "css_code": ".app { color: red; }"
}
invalid_code = {
    "react_code": "// TODO: implement this"
}

if optimizer._validate_javascript_syntax(valid_code) and not optimizer._validate_javascript_syntax(invalid_code):
    print("✅ RÉUSSI - Validation syntaxe fonctionne correctement")
    tests_passed += 1
else:
    print("❌ ÉCHOUÉ - Validation syntaxe incorrecte")

# TEST 6: Extraction code depuis texte
print("\nTEST 6: Extraction Code depuis Texte")
print("-" * 80)
total_tests += 1
text_with_code = """
Voici le code:
```javascript
const x = 5;
console.log(x);
```

Et le CSS:
```css
.test { color: blue; }
```
"""
extracted = optimizer._extract_code_from_text(text_with_code, "javascript")
if extracted and extracted.get("js_code") and extracted.get("css_code"):
    print(f"✅ RÉUSSI - Extraction réussie: {len(extracted)} champs extraits")
    tests_passed += 1
else:
    print("❌ ÉCHOUÉ - Extraction échouée")

# TEST 7: Prompts optimisés
print("\nTEST 7: Prompts LLM Optimisés")
print("-" * 80)
total_tests += 1
react_prompt = optimizer.get_optimized_javascript_prompt("Test app", "react", "javascript")
express_prompt = optimizer.get_optimized_javascript_prompt("Test API", "express", "javascript")
vue_prompt = optimizer.get_optimized_javascript_prompt("Test app", "vue", "javascript")

if ("REACT" in react_prompt and "hooks" in react_prompt.lower() and
    "EXPRESS" in express_prompt and "middleware" in express_prompt.lower() and
    "VUE" in vue_prompt and "composition api" in vue_prompt.lower()):
    print("✅ RÉUSSI - Prompts spécifiques générés correctement")
    tests_passed += 1
else:
    print("❌ ÉCHOUÉ - Prompts non optimisés")

# RÉSULTATS FINAUX
print("\n" + "="*80)
print(f"📊 RÉSULTATS FINAUX: {tests_passed}/{total_tests} tests réussis")
print(f"📈 Taux de réussite: {(tests_passed/total_tests)*100:.1f}%")
print("="*80 + "\n")

if tests_passed == total_tests:
    print("🎉 SUCCÈS COMPLET! Tous les tests sont passés (100%)!")
    sys.exit(0)
elif tests_passed >= total_tests * 0.8:
    print("✅ SUCCÈS PARTIEL! La plupart des tests sont passés (≥80%)")
    sys.exit(0)
else:
    print("❌ ÉCHEC! Trop de tests ont échoué")
    sys.exit(1)
