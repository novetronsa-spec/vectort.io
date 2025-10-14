#!/usr/bin/env python3
"""
Diagnostic en temps réel du générateur avancé
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from ai_generators.advanced_generator import (
    AdvancedCodeGenerator, 
    GenerationRequest, 
    ProjectType, 
    Framework, 
    DatabaseType
)

async def debug_generator():
    print("🔍 DIAGNOSTIC GÉNÉRATEUR AVANCÉ")
    print("=" * 50)
    
    # Initialiser le générateur
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        print("❌ EMERGENT_LLM_KEY manquante!")
        return
    
    generator = AdvancedCodeGenerator(api_key)
    
    # Test 1: Génération d'architecture
    print("\n🏗️ Test 1: Génération d'architecture")
    request = GenerationRequest(
        description="Site e-commerce simple avec React",
        project_type=ProjectType.ECOMMERCE,
        framework=Framework.REACT,
        database=DatabaseType.MONGODB
    )
    
    try:
        architecture = await generator._generate_architecture(request)
        print(f"✅ Architecture générée: {len(architecture)} fichiers")
        print(f"📁 Premiers fichiers: {list(architecture.keys())[:5]}")
    except Exception as e:
        print(f"❌ Erreur architecture: {str(e)}")
        return
    
    # Test 2: Génération des fichiers principaux
    print("\n📄 Test 2: Génération des fichiers principaux")
    try:
        main_files = await generator._generate_main_files(request, architecture)
        print(f"✅ Fichiers principaux générés: {len(main_files)}")
        
        for file_path, content in main_files.items():
            print(f"📋 {file_path}: {len(content)} caractères")
            if len(content) > 100:
                print(f"   Aperçu: {content[:100]}...")
            else:
                print(f"   Contenu: {content}")
    except Exception as e:
        print(f"❌ Erreur fichiers principaux: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 3: Génération d'un seul fichier
    print("\n📝 Test 3: Génération d'un fichier spécifique")
    try:
        single_file = await generator._generate_single_file(
            request, 
            "App.jsx", 
            "Composant React principal"
        )
        print(f"✅ Fichier unique généré: {len(single_file)} caractères")
        print(f"   Aperçu: {single_file[:200]}...")
    except Exception as e:
        print(f"❌ Erreur fichier unique: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Génération complète
    print("\n🚀 Test 4: Génération complète")
    try:
        complete_app = await generator.generate_complete_application(request)
        print(f"✅ Application complète générée!")
        print(f"📊 Structure: {len(complete_app.project_structure)} fichiers")
        print(f"📋 Main files: {len(complete_app.main_files)} fichiers")
        print(f"📦 Package.json: {'✅' if complete_app.package_json else '❌'}")
        print(f"🐳 Dockerfile: {'✅' if complete_app.dockerfile else '❌'}")
        
        # Vérifier le contenu des fichiers principaux
        for key, value in complete_app.main_files.items():
            print(f"   {key}: {len(str(value))} chars - {'✅' if len(str(value)) > 50 else '❌'}")
            
    except Exception as e:
        print(f"❌ Erreur génération complète: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_generator())