#!/usr/bin/env python3
"""
🎯 TESTS CRITIQUES VECTORT.IO - GÉNÉRATION DE CODE RÉEL
Tests spécifiques pour vérifier que le système génère du VRAI code fonctionnel
"""

import requests
import json
import sys
import time
import os
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://devstream-ai.preview.emergentagent.com/api"
TEST_USER = {
    "email": f"critical.test.{int(time.time())}@vectort.io",
    "password": "CriticalTest123!",
    "full_name": f"Critical Test User {int(time.time())}"
}

class CriticalCodexTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.user_id = None
        self.test_project_id = None
        self.advanced_project_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
            "critical_issues": []
        }

    def log_result(self, test_name: str, success: bool, message: str = "", is_critical: bool = False):
        """Log test result with critical issue tracking"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")
            if is_critical:
                self.results["critical_issues"].append(f"{test_name}: {message}")

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    headers: Optional[Dict] = None, timeout: int = 60) -> requests.Response:
        """Make HTTP request with extended timeout for generation"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
        if self.access_token and "Authorization" not in default_headers:
            default_headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=default_headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise

    def test_1_authentification_complete(self):
        """TEST 1: AUTHENTIFICATION COMPLÈTE"""
        print("\n" + "="*80)
        print("🔐 TEST 1: AUTHENTIFICATION COMPLÈTE")
        print("="*80)
        
        # 1a. Créer un nouvel utilisateur
        print("\n--- 1a. Création nouvel utilisateur ---")
        try:
            response = self.make_request("POST", "/auth/register", TEST_USER)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["access_token", "token_type", "user"]
                
                if all(field in data for field in required_fields):
                    self.access_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    
                    # 1b. Vérifier que le token JWT est retourné
                    if data["access_token"] and data["token_type"] == "bearer":
                        self.log_result("1b. Token JWT retourné", True, f"Token: {data['access_token'][:20]}...")
                    else:
                        self.log_result("1b. Token JWT retourné", False, "Token manquant ou type incorrect", True)
                    
                    self.log_result("1a. Création utilisateur", True, f"Utilisateur créé avec ID: {self.user_id}")
                else:
                    self.log_result("1a. Création utilisateur", False, f"Champs manquants: {data}", True)
            elif response.status_code == 400 and "already exists" in response.text:
                # Utilisateur existe déjà, essayer de se connecter
                print("   Utilisateur existe déjà, tentative de connexion...")
                login_response = self.make_request("POST", "/auth/login", {
                    "email": TEST_USER["email"],
                    "password": TEST_USER["password"]
                })
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.access_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    self.log_result("1a. Connexion utilisateur existant", True, f"Connecté avec ID: {self.user_id}")
                    self.log_result("1b. Token JWT retourné", True, f"Token: {data['access_token'][:20]}...")
                else:
                    self.log_result("1a. Connexion utilisateur", False, f"Échec connexion: {login_response.status_code}", True)
            else:
                self.log_result("1a. Création utilisateur", False, f"Status: {response.status_code}, Body: {response.text}", True)
        except Exception as e:
            self.log_result("1a. Création utilisateur", False, f"Exception: {str(e)}", True)

        # 1c. Vérifier que /api/auth/me fonctionne avec le token
        print("\n--- 1c. Vérification /api/auth/me ---")
        try:
            if not self.access_token:
                self.log_result("1c. Vérification /api/auth/me", False, "Pas de token disponible", True)
            else:
                response = self.make_request("GET", "/auth/me")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("email") == TEST_USER["email"]:
                        self.log_result("1c. Vérification /api/auth/me", True, f"Authentification réussie: {data['full_name']}")
                    else:
                        self.log_result("1c. Vérification /api/auth/me", False, "Email ne correspond pas", True)
                else:
                    self.log_result("1c. Vérification /api/auth/me", False, f"Status: {response.status_code} - {response.text}", True)
        except Exception as e:
            self.log_result("1c. Vérification /api/auth/me", False, f"Exception: {str(e)}", True)

        # 1d. Vérifier que les crédits initiaux sont à 10
        print("\n--- 1d. Vérification crédits initiaux (10) ---")
        try:
            if not self.access_token:
                self.log_result("1d. Crédits initiaux", False, "Pas de token disponible", True)
            else:
                response = self.make_request("GET", "/credits/balance")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("total_available") == 10.0 and data.get("free_credits") == 10.0:
                        self.log_result("1d. Crédits initiaux", True, f"✅ 10 crédits gratuits confirmés: {data}")
                    else:
                        self.log_result("1d. Crédits initiaux", False, f"❌ Crédits incorrects: {data}", True)
                else:
                    self.log_result("1d. Crédits initiaux", False, f"Status: {response.status_code} - {response.text}", True)
        except Exception as e:
            self.log_result("1d. Crédits initiaux", False, f"Exception: {str(e)}", True)

    def test_2_creation_projet(self):
        """TEST 2: CRÉATION DE PROJET"""
        print("\n" + "="*80)
        print("📁 TEST 2: CRÉATION DE PROJET")
        print("="*80)
        
        try:
            if not self.access_token:
                self.log_result("2. Création projet", False, "Pas de token disponible", True)
                return
            
            project_data = {
                "title": "Test App",
                "description": "Une simple todo app",
                "type": "web_app"
            }
            
            response = self.make_request("POST", "/projects", project_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "title", "description", "type", "user_id"]
                
                if all(field in data for field in required_fields):
                    self.test_project_id = data["id"]
                    if (data["title"] == project_data["title"] and 
                        data["description"] == project_data["description"] and
                        data["type"] == project_data["type"] and
                        data["user_id"] == self.user_id):
                        self.log_result("2. Création projet", True, f"✅ Projet créé avec ID: {self.test_project_id}")
                    else:
                        self.log_result("2. Création projet", False, "Données du projet ne correspondent pas", True)
                else:
                    self.log_result("2. Création projet", False, f"Champs manquants: {data}", True)
            else:
                self.log_result("2. Création projet", False, f"Status: {response.status_code} - {response.text}", True)
        except Exception as e:
            self.log_result("2. Création projet", False, f"Exception: {str(e)}", True)

    def test_3_generation_code_critique(self):
        """TEST 3: GÉNÉRATION DE CODE (CRITIQUE)"""
        print("\n" + "="*80)
        print("🚀 TEST 3: GÉNÉRATION DE CODE (CRITIQUE)")
        print("="*80)
        
        try:
            if not self.access_token or not self.test_project_id:
                self.log_result("3. Génération code", False, "Pas de token ou projet disponible", True)
                return
            
            # Vérifier les crédits avant génération
            credits_before_response = self.make_request("GET", "/credits/balance")
            credits_before = 0
            if credits_before_response.status_code == 200:
                credits_before = credits_before_response.json().get("total_available", 0)
                print(f"   Crédits avant génération: {credits_before}")
            
            generation_request = {
                "description": "Créer une simple todo app avec React",
                "type": "web_app",
                "framework": "react",
                "database": "mongodb",
                "features": [],
                "integrations": [],
                "deployment_target": "vercel",
                "advanced_mode": False
            }
            
            print("   Lancement génération de code...")
            response = self.make_request("POST", f"/projects/{self.test_project_id}/generate", generation_request, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Génération réussie, analyse du code...")
                
                # Vérifier que la réponse contient du VRAI code
                code_fields = {
                    "html_code": data.get("html_code"),
                    "css_code": data.get("css_code"),
                    "js_code": data.get("js_code"),
                    "react_code": data.get("react_code"),
                    "backend_code": data.get("backend_code")
                }
                
                real_code_found = False
                code_analysis = []
                
                for field, code in code_fields.items():
                    if code and len(code.strip()) > 50:  # Code substantiel
                        real_code_found = True
                        code_analysis.append(f"{field}: {len(code)} chars")
                        
                        # Vérifier que c'est du VRAI code JavaScript/React/HTML
                        if field == "react_code" and ("import" in code or "export" in code or "function" in code or "const" in code):
                            self.log_result("3a. Code React généré", True, f"✅ Code React valide ({len(code)} chars)")
                        elif field == "html_code" and ("<!DOCTYPE" in code or "<html" in code or "<div" in code):
                            self.log_result("3b. Code HTML généré", True, f"✅ Code HTML valide ({len(code)} chars)")
                        elif field == "css_code" and ("{" in code and "}" in code):
                            self.log_result("3c. Code CSS généré", True, f"✅ Code CSS valide ({len(code)} chars)")
                        elif field == "js_code" and ("function" in code or "const" in code or "var" in code):
                            self.log_result("3d. Code JS généré", True, f"✅ Code JavaScript valide ({len(code)} chars)")
                        elif field == "backend_code" and ("def" in code or "class" in code or "import" in code):
                            self.log_result("3e. Code Backend généré", True, f"✅ Code Backend valide ({len(code)} chars)")
                
                if real_code_found:
                    self.log_result("3. Génération code RÉEL", True, f"✅ VRAI code généré: {', '.join(code_analysis)}")
                else:
                    self.log_result("3. Génération code RÉEL", False, "❌ Aucun code substantiel généré", True)
                
                # Vérifier que les crédits sont déduits (10 → 8 pour quick mode)
                credits_after_response = self.make_request("GET", "/credits/balance")
                if credits_after_response.status_code == 200:
                    credits_after = credits_after_response.json().get("total_available", 0)
                    expected_deduction = 2  # Quick mode
                    if credits_before - credits_after == expected_deduction:
                        self.log_result("3f. Déduction crédits", True, f"✅ Crédits déduits: {credits_before} → {credits_after} (-{expected_deduction})")
                    else:
                        self.log_result("3f. Déduction crédits", False, f"❌ Déduction incorrecte: {credits_before} → {credits_after} (attendu: -{expected_deduction})", True)
                else:
                    self.log_result("3f. Déduction crédits", False, "Impossible de vérifier les crédits après génération", True)
                    
            elif response.status_code == 402:
                self.log_result("3. Génération code", False, "❌ Crédits insuffisants", True)
            else:
                self.log_result("3. Génération code", False, f"❌ Status: {response.status_code} - {response.text}", True)
                
        except Exception as e:
            self.log_result("3. Génération code", False, f"Exception: {str(e)}", True)

    def test_4_emergent_llm_key(self):
        """TEST 4: VÉRIFIER EMERGENT_LLM_KEY"""
        print("\n" + "="*80)
        print("🔑 TEST 4: VÉRIFIER EMERGENT_LLM_KEY")
        print("="*80)
        
        # 4a. Vérifier que EMERGENT_LLM_KEY est bien configurée dans .env
        try:
            with open("/app/backend/.env", "r") as f:
                env_content = f.read()
                if "EMERGENT_LLM_KEY=" in env_content and "sk-emergent-" in env_content:
                    self.log_result("4a. EMERGENT_LLM_KEY dans .env", True, "✅ Clé trouvée dans .env")
                else:
                    self.log_result("4a. EMERGENT_LLM_KEY dans .env", False, "❌ Clé manquante ou invalide dans .env", True)
        except Exception as e:
            self.log_result("4a. EMERGENT_LLM_KEY dans .env", False, f"Erreur lecture .env: {str(e)}", True)
        
        # 4b. Vérifier qu'elle est utilisée dans le code
        try:
            with open("/app/backend/server.py", "r") as f:
                server_content = f.read()
                if "EMERGENT_LLM_KEY" in server_content and "LlmChat" in server_content:
                    self.log_result("4b. EMERGENT_LLM_KEY utilisée", True, "✅ Clé utilisée dans server.py avec LlmChat")
                else:
                    self.log_result("4b. EMERGENT_LLM_KEY utilisée", False, "❌ Clé non utilisée dans le code", True)
        except Exception as e:
            self.log_result("4b. EMERGENT_LLM_KEY utilisée", False, f"Erreur lecture server.py: {str(e)}", True)
        
        # 4c. Test fonctionnel de l'API LLM via génération
        print("\n--- 4c. Test fonctionnel API LLM ---")
        if self.test_project_id and self.access_token:
            try:
                # Créer un petit projet pour tester l'API LLM
                test_gen_request = {
                    "description": "Test API LLM - simple button",
                    "type": "web_app",
                    "framework": "react",
                    "advanced_mode": False
                }
                
                response = self.make_request("POST", f"/projects/{self.test_project_id}/generate", test_gen_request, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    if any(data.get(field) for field in ["html_code", "css_code", "js_code", "react_code"]):
                        self.log_result("4c. API LLM fonctionnelle", True, "✅ API LLM répond et génère du code")
                    else:
                        self.log_result("4c. API LLM fonctionnelle", False, "❌ API LLM ne génère pas de code", True)
                else:
                    self.log_result("4c. API LLM fonctionnelle", False, f"❌ Erreur API: {response.status_code}", True)
            except Exception as e:
                self.log_result("4c. API LLM fonctionnelle", False, f"Exception: {str(e)}", True)
        else:
            self.log_result("4c. API LLM fonctionnelle", False, "Pas de projet ou token pour tester", True)

    def test_5_recuperation_code_genere(self):
        """TEST 5: RÉCUPÉRATION DU CODE GÉNÉRÉ"""
        print("\n" + "="*80)
        print("📥 TEST 5: RÉCUPÉRATION DU CODE GÉNÉRÉ")
        print("="*80)
        
        try:
            if not self.access_token or not self.test_project_id:
                self.log_result("5. Récupération code", False, "Pas de token ou projet disponible", True)
                return
            
            response = self.make_request("GET", f"/projects/{self.test_project_id}/code")
            
            if response.status_code == 200:
                data = response.json()
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                has_code = any(data.get(field) for field in code_fields)
                
                if has_code:
                    stored_code = []
                    for field in code_fields:
                        if data.get(field):
                            stored_code.append(f"{field}: {len(data[field])} chars")
                    
                    self.log_result("5. Récupération code", True, f"✅ Code stocké et récupérable: {', '.join(stored_code)}")
                else:
                    self.log_result("5. Récupération code", False, "❌ Aucun code trouvé dans la réponse", True)
            elif response.status_code == 404:
                self.log_result("5. Récupération code", False, "❌ Code généré non trouvé", True)
            else:
                self.log_result("5. Récupération code", False, f"❌ Status: {response.status_code} - {response.text}", True)
        except Exception as e:
            self.log_result("5. Récupération code", False, f"Exception: {str(e)}", True)

    def test_6_mode_avance(self):
        """TEST 6: TEST AVEC MODE AVANCÉ"""
        print("\n" + "="*80)
        print("⚡ TEST 6: TEST AVEC MODE AVANCÉ")
        print("="*80)
        
        try:
            if not self.access_token:
                self.log_result("6. Mode avancé", False, "Pas de token disponible", True)
                return
            
            # 6a. Créer un autre projet
            print("\n--- 6a. Création projet pour mode avancé ---")
            project_data = {
                "title": "Advanced Test App",
                "description": "Application avancée pour test du mode avancé",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            
            if project_response.status_code == 200:
                self.advanced_project_id = project_response.json()["id"]
                self.log_result("6a. Création projet avancé", True, f"✅ Projet avancé créé: {self.advanced_project_id}")
            else:
                self.log_result("6a. Création projet avancé", False, f"❌ Échec création: {project_response.status_code}", True)
                return
            
            # Vérifier les crédits avant génération avancée
            credits_before_response = self.make_request("GET", "/credits/balance")
            credits_before = 0
            if credits_before_response.status_code == 200:
                credits_before = credits_before_response.json().get("total_available", 0)
                print(f"   Crédits avant génération avancée: {credits_before}")
            
            # 6b. Générer avec advanced_mode: true
            print("\n--- 6b. Génération en mode avancé ---")
            advanced_request = {
                "description": "Créer une application complète avec React, backend FastAPI, base de données MongoDB",
                "type": "web_app",
                "framework": "react",
                "database": "mongodb",
                "features": ["authentication", "crud_operations", "real_time_updates"],
                "integrations": ["stripe", "email"],
                "deployment_target": "vercel",
                "advanced_mode": True
            }
            
            response = self.make_request("POST", f"/projects/{self.advanced_project_id}/generate", advanced_request, timeout=180)
            
            if response.status_code == 200:
                data = response.json()
                
                # 6c. Vérifier que 4 crédits sont déduits
                credits_after_response = self.make_request("GET", "/credits/balance")
                if credits_after_response.status_code == 200:
                    credits_after = credits_after_response.json().get("total_available", 0)
                    expected_deduction = 4  # Advanced mode
                    if credits_before - credits_after == expected_deduction:
                        self.log_result("6c. Déduction crédits avancé", True, f"✅ Crédits déduits: {credits_before} → {credits_after} (-{expected_deduction})")
                    else:
                        self.log_result("6c. Déduction crédits avancé", False, f"❌ Déduction incorrecte: {credits_before} → {credits_after} (attendu: -{expected_deduction})", True)
                
                # 6d. Vérifier que plus de fichiers sont générés
                basic_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                advanced_fields = ["project_structure", "package_json", "requirements_txt", "dockerfile", "readme", "all_files"]
                
                basic_files = sum(1 for field in basic_fields if data.get(field))
                advanced_files = sum(1 for field in advanced_fields if data.get(field))
                total_files = basic_files + advanced_files
                
                if total_files >= 3:  # Au moins 3 types de fichiers
                    files_generated = []
                    for field in basic_fields + advanced_fields:
                        if data.get(field):
                            if isinstance(data[field], str):
                                files_generated.append(f"{field}: {len(data[field])} chars")
                            else:
                                files_generated.append(f"{field}: {type(data[field]).__name__}")
                    
                    self.log_result("6d. Fichiers mode avancé", True, f"✅ {total_files} types de fichiers générés: {', '.join(files_generated[:5])}")
                else:
                    self.log_result("6d. Fichiers mode avancé", False, f"❌ Seulement {total_files} types de fichiers générés", True)
                
                self.log_result("6b. Génération mode avancé", True, "✅ Mode avancé fonctionne")
                
            elif response.status_code == 402:
                self.log_result("6b. Génération mode avancé", False, "❌ Crédits insuffisants pour mode avancé", True)
            else:
                self.log_result("6b. Génération mode avancé", False, f"❌ Status: {response.status_code} - {response.text}", True)
                
        except Exception as e:
            self.log_result("6. Mode avancé", False, f"Exception: {str(e)}", True)

    def run_critical_tests(self):
        """Exécuter tous les tests critiques"""
        print("🎯 TESTS CRITIQUES VECTORT.IO - GÉNÉRATION DE CODE RÉEL")
        print(f"Testing against: {self.base_url}")
        print("=" * 80)
        print("OBJECTIF: Vérifier que le système génère du VRAI code fonctionnel comme Emergent")
        print("=" * 80)
        
        # Exécuter tous les tests critiques
        self.test_1_authentification_complete()
        self.test_2_creation_projet()
        self.test_3_generation_code_critique()
        self.test_4_emergent_llm_key()
        self.test_5_recuperation_code_genere()
        self.test_6_mode_avance()
        
        # Résumé final
        print("\n" + "="*80)
        print("🎯 RÉSUMÉ DES TESTS CRITIQUES")
        print("="*80)
        
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        print(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        # Critères de succès
        print(f"\n🎯 CRITÈRES DE SUCCÈS:")
        success_criteria = [
            ("✅ Authentification fonctionne sans erreur 'Not authenticated'", "1c. Vérification /api/auth/me" in [e.split(":")[0] for e in self.results['errors']]),
            ("✅ La génération produit du VRAI code (pas juste du texte)", "3. Génération code RÉEL" in [e.split(":")[0] for e in self.results['errors']]),
            ("✅ Le code généré contient des fichiers React/JS/HTML valides", any("Code" in e and "généré" in e for e in self.results['errors'])),
            ("✅ Les crédits sont correctement déduits", any("Déduction crédits" in e for e in self.results['errors'])),
            ("✅ Le code est stocké et récupérable", "5. Récupération code" in [e.split(":")[0] for e in self.results['errors']]),
            ("✅ EMERGENT_LLM_KEY fonctionne et génère du contenu", "4c. API LLM fonctionnelle" in [e.split(":")[0] for e in self.results['errors']])
        ]
        
        for criterion, has_error in success_criteria:
            status = "❌" if has_error else "✅"
            print(f"{status} {criterion.replace('✅ ', '').replace('❌ ', '')}")
        
        # Issues critiques
        if self.results['critical_issues']:
            print(f"\n🚨 ISSUES CRITIQUES À RÉSOUDRE:")
            for issue in self.results['critical_issues']:
                print(f"   • {issue}")
        
        # Échec si issues critiques
        if self.results['critical_issues']:
            print(f"\n❌ ÉCHEC: Issues critiques détectées")
            print("   Le système ne génère pas du code fonctionnel comme requis")
            return False
        elif success_rate >= 80:
            print(f"\n🎉 SUCCÈS: Le système génère du VRAI code fonctionnel!")
            print("   Prêt pour utilisation comme Emergent")
            return True
        else:
            print(f"\n⚠️  PARTIEL: Taux de réussite {success_rate:.1f}% (minimum 80% requis)")
            return False

if __name__ == "__main__":
    tester = CriticalCodexTester()
    success = tester.run_critical_tests()
    sys.exit(0 if success else 1)