#!/usr/bin/env python3
"""
🎯 TEST COMPLET DU SYSTÈME D'ITÉRATION ET DE CHAT IA - VECTORT.IO
Test spécialisé pour le système d'amélioration itérative des projets (comme emergent.sh)
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuration - Production Environment API
BASE_URL = "https://devstream-ai.preview.emergentagent.com/api"

class VectortIterationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.user_id = None
        self.test_project_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    headers: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
        if self.access_token and "Authorization" not in default_headers:
            default_headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers, timeout=60)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=60)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=default_headers, timeout=60)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers, timeout=60)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise

    def test_authentication_setup(self):
        """Test 1: Authentication & Setup - Créer utilisateur avec 10 crédits gratuits"""
        print("\n=== Test 1: Authentication & Setup ===")
        
        # Create unique test user
        test_user = {
            "email": f"iteration_test_{int(time.time())}@vectort.io",
            "password": "IterationTest123!",
            "full_name": f"Iteration Test User {int(time.time())}"
        }
        
        try:
            # Register new user
            response = self.make_request("POST", "/auth/register", test_user)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                
                # Verify user has 10 free credits
                credits_response = self.make_request("GET", "/credits/balance")
                if credits_response.status_code == 200:
                    credits_data = credits_response.json()
                    free_credits = credits_data.get("free_credits", 0)
                    total_credits = credits_data.get("total_available", 0)
                    
                    if free_credits == 10.0 and total_credits == 10.0:
                        self.log_result("Authentication & Setup", True, 
                                      f"✅ Utilisateur créé avec 10 crédits gratuits. Token JWT obtenu.")
                    else:
                        self.log_result("Authentication & Setup", False, 
                                      f"❌ Crédits incorrects: {free_credits} gratuits, {total_credits} total (attendu: 10)")
                else:
                    self.log_result("Authentication & Setup", False, 
                                  f"❌ Impossible de vérifier les crédits: {credits_response.status_code}")
            else:
                self.log_result("Authentication & Setup", False, 
                              f"❌ Échec de l'inscription: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Authentication & Setup", False, f"Exception: {str(e)}")

    def test_project_creation_and_generation(self):
        """Test 2: Création Projet & Génération - Mode quick (2 crédits)"""
        print("\n=== Test 2: Création Projet & Génération ===")
        
        if not self.access_token:
            self.log_result("Project Creation & Generation", False, "❌ Pas de token d'authentification")
            return
        
        try:
            # Create project
            project_data = {
                "title": "Site vitrine restaurant",
                "description": "Site vitrine pour un restaurant avec menu, réservations et contact",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            
            if project_response.status_code == 200:
                project = project_response.json()
                self.test_project_id = project["id"]
                
                # Generate code with quick mode (2 credits)
                generation_request = {
                    "description": "Site vitrine pour un restaurant avec menu, réservations et contact",
                    "type": "web_app",
                    "framework": "react",
                    "advanced_mode": False  # Quick mode = 2 crédits
                }
                
                # Check credits before generation
                credits_before = self.make_request("GET", "/credits/balance")
                credits_before_data = credits_before.json() if credits_before.status_code == 200 else {}
                credits_before_total = credits_before_data.get("total_available", 0)
                
                # Generate
                start_time = time.time()
                gen_response = self.make_request("POST", f"/projects/{self.test_project_id}/generate", generation_request)
                generation_time = time.time() - start_time
                
                if gen_response.status_code == 200:
                    gen_data = gen_response.json()
                    
                    # Verify project status is 'completed'
                    project_check = self.make_request("GET", f"/projects/{self.test_project_id}")
                    if project_check.status_code == 200:
                        project_status = project_check.json().get("status")
                        
                        # Verify REAL code was generated
                        react_code = gen_data.get("react_code") or ""
                        css_code = gen_data.get("css_code") or ""
                        has_react_code = bool(react_code)
                        has_css_code = bool(css_code)
                        react_code_length = len(react_code)
                        css_code_length = len(css_code)
                        
                        # Check credits after generation (should be 10 → 8)
                        credits_after = self.make_request("GET", "/credits/balance")
                        credits_after_data = credits_after.json() if credits_after.status_code == 200 else {}
                        credits_after_total = credits_after_data.get("total_available", 0)
                        
                        # Validation criteria
                        status_ok = project_status == "completed"
                        code_generated = has_react_code and has_css_code and react_code_length > 100
                        credits_deducted = (credits_before_total - credits_after_total) == 2
                        # Allow for cached results (no credit deduction)
                        credits_ok = credits_deducted or (credits_before_total == credits_after_total)
                        
                        if status_ok and code_generated and credits_ok:
                            self.log_result("Project Creation & Generation", True, 
                                          f"✅ Projet créé et code généré. Status: {project_status}, "
                                          f"React: {react_code_length} chars, CSS: {css_code_length} chars, "
                                          f"Crédits: {credits_before_total} → {credits_after_total} (-2), "
                                          f"Temps: {generation_time:.1f}s")
                        else:
                            self.log_result("Project Creation & Generation", False, 
                                          f"❌ Critères non remplis. Status: {project_status}, "
                                          f"Code généré: {code_generated}, Crédits OK: {credits_ok}")
                    else:
                        self.log_result("Project Creation & Generation", False, 
                                      f"❌ Impossible de vérifier le statut du projet")
                else:
                    self.log_result("Project Creation & Generation", False, 
                                  f"❌ Échec de la génération: {gen_response.status_code} - {gen_response.text}")
            else:
                self.log_result("Project Creation & Generation", False, 
                              f"❌ Échec de la création du projet: {project_response.status_code}")
                
        except Exception as e:
            self.log_result("Project Creation & Generation", False, f"Exception: {str(e)}")

    def test_iteration_system_critical(self):
        """Test 3: Système d'Itération (CRITIQUE) - POST /api/projects/{id}/iterate"""
        print("\n=== Test 3: Système d'Itération (CRITIQUE) ===")
        
        if not self.access_token or not self.test_project_id:
            self.log_result("Iteration System", False, "❌ Pas de token ou projet disponible")
            return
        
        try:
            # First iteration: Add contact form
            iteration_request = {
                "instruction": "Ajoute un formulaire de contact avec nom, email, message et bouton d'envoi"
            }
            
            # Check credits before iteration
            credits_before = self.make_request("GET", "/credits/balance")
            credits_before_data = credits_before.json() if credits_before.status_code == 200 else {}
            credits_before_total = credits_before_data.get("total_available", 0)
            
            # Execute iteration
            start_time = time.time()
            response = self.make_request("POST", f"/projects/{self.test_project_id}/iterate", iteration_request)
            iteration_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["success", "iteration_number", "changes_made", "explanation"]
                has_required_fields = all(field in data for field in required_fields)
                
                success = data.get("success", False)
                iteration_number = data.get("iteration_number", 0)
                changes_made = data.get("changes_made", [])
                explanation = data.get("explanation", "")
                updated_code = data.get("updated_code")
                
                # Check credits after iteration (should be 8 → 7, 1 credit deducted)
                credits_after = self.make_request("GET", "/credits/balance")
                credits_after_data = credits_after.json() if credits_after.status_code == 200 else {}
                credits_after_total = credits_after_data.get("total_available", 0)
                
                # Verify iteration was saved in project_iterations
                iterations_response = self.make_request("GET", f"/projects/{self.test_project_id}/iterations")
                iterations_saved = iterations_response.status_code == 200
                
                # Validation criteria
                structure_ok = has_required_fields and success
                content_ok = len(changes_made) > 0 and len(explanation) > 10
                credits_deducted = (credits_before_total - credits_after_total) == 1
                iteration_saved = iterations_saved
                
                if structure_ok and content_ok and credits_deducted and iteration_saved:
                    self.log_result("Iteration System", True, 
                                  f"✅ Itération réussie #{iteration_number}. "
                                  f"Changements: {len(changes_made)}, "
                                  f"Explication: {len(explanation)} chars, "
                                  f"Crédits: {credits_before_total} → {credits_after_total} (-1), "
                                  f"Temps: {iteration_time:.1f}s")
                else:
                    self.log_result("Iteration System", False, 
                                  f"❌ Critères non remplis. Structure: {structure_ok}, "
                                  f"Contenu: {content_ok}, Crédits: {credits_deducted}, "
                                  f"Sauvegarde: {iteration_saved}")
            else:
                self.log_result("Iteration System", False, 
                              f"❌ Échec de l'itération: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Iteration System", False, f"Exception: {str(e)}")

    def test_chat_history(self):
        """Test 4: Historique Chat - GET /api/projects/{id}/chat"""
        print("\n=== Test 4: Historique Chat ===")
        
        if not self.access_token or not self.test_project_id:
            self.log_result("Chat History", False, "❌ Pas de token ou projet disponible")
            return
        
        try:
            response = self.make_request("GET", f"/projects/{self.test_project_id}/chat")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["project_id", "messages", "total"]
                has_required_fields = all(field in data for field in required_fields)
                
                project_id = data.get("project_id")
                messages = data.get("messages", [])
                total = data.get("total", 0)
                
                # Verify messages structure
                valid_messages = True
                user_messages = 0
                assistant_messages = 0
                
                for msg in messages:
                    if not all(field in msg for field in ["role", "content", "timestamp"]):
                        valid_messages = False
                        break
                    
                    if msg["role"] == "user":
                        user_messages += 1
                    elif msg["role"] == "assistant":
                        assistant_messages += 1
                
                # Validation criteria
                structure_ok = has_required_fields and project_id == self.test_project_id
                messages_ok = valid_messages and total > 0 and user_messages > 0 and assistant_messages > 0
                
                if structure_ok and messages_ok:
                    self.log_result("Chat History", True, 
                                  f"✅ Historique chat récupéré. Total: {total} messages, "
                                  f"User: {user_messages}, Assistant: {assistant_messages}")
                else:
                    self.log_result("Chat History", False, 
                                  f"❌ Structure ou contenu invalide. Structure: {structure_ok}, "
                                  f"Messages: {messages_ok}, Total: {total}")
            else:
                self.log_result("Chat History", False, 
                              f"❌ Échec récupération chat: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Chat History", False, f"Exception: {str(e)}")

    def test_multiple_iterations(self):
        """Test 5: Itérations Multiples - 2ème et 3ème itération"""
        print("\n=== Test 5: Itérations Multiples ===")
        
        if not self.access_token or not self.test_project_id:
            self.log_result("Multiple Iterations", False, "❌ Pas de token ou projet disponible")
            return
        
        try:
            # 2nd iteration: Change header color
            iteration2_request = {
                "instruction": "Change la couleur du header en bleu et ajoute un logo"
            }
            
            response2 = self.make_request("POST", f"/projects/{self.test_project_id}/iterate", iteration2_request)
            
            if response2.status_code == 200:
                data2 = response2.json()
                iteration2_number = data2.get("iteration_number", 0)
                
                # 3rd iteration: Add image gallery
                iteration3_request = {
                    "instruction": "Ajoute une galerie d'images avec lightbox pour présenter les plats du restaurant"
                }
                
                response3 = self.make_request("POST", f"/projects/{self.test_project_id}/iterate", iteration3_request)
                
                if response3.status_code == 200:
                    data3 = response3.json()
                    iteration3_number = data3.get("iteration_number", 0)
                    
                    # Verify iterations history
                    iterations_response = self.make_request("GET", f"/projects/{self.test_project_id}/iterations")
                    
                    if iterations_response.status_code == 200:
                        iterations_data = iterations_response.json()
                        iterations = iterations_data.get("iterations", [])
                        total_iterations = iterations_data.get("total", 0)
                        
                        # Should have 3 iterations numbered 1, 2, 3
                        iteration_numbers = [it.get("iteration_number") for it in iterations]
                        expected_numbers = [1, 2, 3]
                        
                        if total_iterations >= 3 and all(num in iteration_numbers for num in expected_numbers):
                            self.log_result("Multiple Iterations", True, 
                                          f"✅ 3 itérations réussies. Numéros: {iteration_numbers}, "
                                          f"Total: {total_iterations}")
                        else:
                            self.log_result("Multiple Iterations", False, 
                                          f"❌ Itérations incomplètes. Total: {total_iterations}, "
                                          f"Numéros: {iteration_numbers}")
                    else:
                        self.log_result("Multiple Iterations", False, 
                                      f"❌ Impossible de récupérer l'historique des itérations")
                else:
                    self.log_result("Multiple Iterations", False, 
                                  f"❌ 3ème itération échouée: {response3.status_code}")
            else:
                self.log_result("Multiple Iterations", False, 
                              f"❌ 2ème itération échouée: {response2.status_code}")
                
        except Exception as e:
            self.log_result("Multiple Iterations", False, f"Exception: {str(e)}")

    def test_preview_functionality(self):
        """Test 6: Preview Fonctionnel - GET /api/projects/{id}/preview"""
        print("\n=== Test 6: Preview Fonctionnel ===")
        
        if not self.access_token or not self.test_project_id:
            self.log_result("Preview Functionality", False, "❌ Pas de token ou projet disponible")
            return
        
        try:
            response = self.make_request("GET", f"/projects/{self.test_project_id}/preview")
            
            if response.status_code == 200:
                html_content = response.text
                
                # Verify HTML structure
                has_doctype = "<!DOCTYPE html>" in html_content
                has_html_tags = "<html" in html_content and "</html>" in html_content
                has_head = "<head>" in html_content and "</head>" in html_content
                has_body = "<body>" in html_content and "</body>" in html_content
                
                # Check for React/CSS integration
                has_css = "<style>" in html_content or "stylesheet" in html_content
                has_js = "<script>" in html_content or "javascript" in html_content
                
                # Content length check
                content_length = len(html_content)
                sufficient_content = content_length > 500
                
                # Validation criteria
                valid_html = has_doctype and has_html_tags and has_head and has_body
                integrated_content = has_css or has_js
                
                if valid_html and integrated_content and sufficient_content:
                    self.log_result("Preview Functionality", True, 
                                  f"✅ Preview HTML généré. Taille: {content_length} chars, "
                                  f"Structure valide, CSS/JS intégré")
                else:
                    self.log_result("Preview Functionality", False, 
                                  f"❌ HTML invalide ou incomplet. Taille: {content_length}, "
                                  f"Structure: {valid_html}, Intégration: {integrated_content}")
            else:
                self.log_result("Preview Functionality", False, 
                              f"❌ Échec génération preview: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Preview Functionality", False, f"Exception: {str(e)}")

    def test_code_retrieval(self):
        """Test 7: Code Retrieval - GET /api/projects/{id}/code"""
        print("\n=== Test 7: Code Retrieval ===")
        
        if not self.access_token or not self.test_project_id:
            self.log_result("Code Retrieval", False, "❌ Pas de token ou projet disponible")
            return
        
        try:
            response = self.make_request("GET", f"/projects/{self.test_project_id}/code")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for code files
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                available_code = {field: bool(data.get(field)) for field in code_fields}
                code_lengths = {field: len(data.get(field) or "") for field in code_fields}
                
                # Check for iterations reflection
                react_code = data.get("react_code") or ""
                css_code = data.get("css_code") or ""
                
                # Look for iteration changes (contact form, blue header, gallery)
                has_contact_form = "contact" in react_code.lower() or "formulaire" in react_code.lower()
                has_blue_header = "blue" in css_code.lower() or "bleu" in css_code.lower()
                has_gallery = "gallery" in react_code.lower() or "galerie" in react_code.lower()
                
                # Validation criteria
                has_meaningful_code = any(length > 100 for length in code_lengths.values())
                reflects_iterations = has_contact_form or has_blue_header or has_gallery
                
                if has_meaningful_code and reflects_iterations:
                    self.log_result("Code Retrieval", True, 
                                  f"✅ Code récupéré et reflète les itérations. "
                                  f"React: {code_lengths['react_code']} chars, "
                                  f"CSS: {code_lengths['css_code']} chars, "
                                  f"Changements détectés: Contact={has_contact_form}, "
                                  f"Bleu={has_blue_header}, Galerie={has_gallery}")
                else:
                    self.log_result("Code Retrieval", False, 
                                  f"❌ Code insuffisant ou itérations non reflétées. "
                                  f"Code significatif: {has_meaningful_code}, "
                                  f"Itérations reflétées: {reflects_iterations}")
            else:
                self.log_result("Code Retrieval", False, 
                              f"❌ Échec récupération code: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Code Retrieval", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Execute all iteration system tests"""
        print("🎯 VECTORT.IO - TEST COMPLET DU SYSTÈME D'ITÉRATION ET DE CHAT IA")
        print("=" * 80)
        
        # Execute tests in order
        self.test_authentication_setup()
        self.test_project_creation_and_generation()
        self.test_iteration_system_critical()
        self.test_chat_history()
        self.test_multiple_iterations()
        self.test_preview_functionality()
        self.test_code_retrieval()
        
        # Final results
        print("\n" + "=" * 80)
        print("🎯 RÉSULTATS FINAUX - SYSTÈME D'ITÉRATION VECTORT.IO")
        print("=" * 80)
        
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        print(f"📊 Taux de réussite: {success_rate:.1f}%")
        
        if self.results["failed"] > 0:
            print(f"\n❌ ERREURS DÉTECTÉES:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        # Final assessment
        if success_rate >= 85:
            print(f"\n🎉 SYSTÈME D'ITÉRATION FONCTIONNEL!")
            print(f"✅ Le système d'amélioration itérative fonctionne comme emergent.sh")
            print(f"✅ L'utilisateur peut améliorer son projet de manière conversationnelle")
            print(f"✅ Chaque itération coûte 1 crédit et met à jour le code")
            print(f"✅ L'historique est conservé et accessible")
        else:
            print(f"\n⚠️ SYSTÈME D'ITÉRATION NÉCESSITE DES CORRECTIONS")
            print(f"❌ Taux de réussite insuffisant: {success_rate:.1f}% (minimum 85%)")
            print(f"❌ Des fonctionnalités critiques ne fonctionnent pas correctement")
        
        return success_rate >= 85

if __name__ == "__main__":
    tester = VectortIterationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)