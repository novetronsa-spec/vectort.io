import asyncio
import os
import sys
sys.path.insert(0, '/app/backend')

from ai_generators.javascript_optimizer import JavaScriptOptimizer

async def main():
    api_key = os.environ.get('EMERGENT_LLM_KEY', 'sk-emergent-0BdC61e9dFeDeE158A')
    print(f"🚀 Test rapide JavaScriptOptimizer avec API key: {api_key[:15]}...")
    
    optimizer = JavaScriptOptimizer(api_key)
    
    print("📝 Génération d'un compteur React simple...")
    result = await optimizer.generate_with_fallback(
        description="Un compteur React simple avec un bouton",
        project_type="web_app",
        framework="react",
        language="javascript",
        features=[]
    )
    
    if result:
        print(f"✅ SUCCÈS! {len(result)} fichiers générés")
        for key, value in result.items():
            print(f"  - {key}: {len(value)} caractères")
        return 0
    else:
        print("❌ ÉCHEC!")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
