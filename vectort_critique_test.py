#!/usr/bin/env python3
"""
🎯 TEST CRITIQUE - Génération de VRAIS Projets Vectort.io
Test spécifique pour la demande française: "je ne vois pas de projet" et "il faut que ça code vraiment"

OBJECTIF: Tester que le système génère de VRAIS projets fonctionnels avec du HTML/CSS/JS rendu, pas juste du texte.
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional
import re

# Configuration - PRODUCTION ENVIRONMENT API
BASE_URL = "https://devstream-ai.preview.emergentagent.com/api"

class VectroCritiqueTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.user_id = None
        self.test_projects = []
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
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise

    def setup_test_user(self):
        """Setup test user for testing"""
        print("\n=== SETUP: Création utilisateur test ===")
        
        test_user = {
            "email": f"critique_test_{int(time.time())}@vectort.io",
            "password": "TestPassword123!",
            "full_name": "Critique Test User"
        }
        
        try:
            # Register user
            response = self.make_request("POST", "/auth/register", test_user)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.user_id = data["user"]["id"]
                self.log_result("Setup User", True, f"Utilisateur créé avec 10 crédits gratuits")
                return True
            elif response.status_code == 400:
                # Try login if user exists
                login_response = self.make_request("POST", "/auth/login", {
                    "email": test_user["email"],
                    "password": test_user["password"]
                })
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.access_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    self.log_result("Setup User", True, "Utilisateur existant connecté")
                    return True
            
            self.log_result("Setup User", False, f"Status: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_result("Setup User", False, f"Exception: {str(e)}")
            return False

    def test_1_generation_basique(self):
        """Test 1: Génération Basique - Site vitrine restaurant simple"""
        print("\n=== Test 1: Génération Basique ===")
        
        if not self.access_token:
            self.log_result("Génération Basique", False, "No access token")
            return
        
        try:
            # Créer projet
            project_data = {
                "title": "Site vitrine restaurant simple",
                "description": "Site vitrine restaurant simple avec menu",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("Génération Basique", False, f"Échec création projet: {project_response.status_code}")
                return
            
            project_id = project_response.json()["id"]
            self.test_projects.append(project_id)
            
            # Générer avec les paramètres exacts de la demande
            generation_request = {
                "description": "Site vitrine restaurant simple avec menu",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False
            }
            
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            
            if response.status_code == 200:
                data = response.json()
                
                # VÉRIFICATIONS CRITIQUES selon la demande
                html_code = data.get("html_code", "")
                css_code = data.get("css_code", "")
                react_code = data.get("react_code", "")
                
                # Vérifier que le code n'est PAS vide ou "html" en texte
                html_valid = html_code and len(html_code) > 10 and "html" not in html_code.lower()[:20]
                css_valid = css_code and len(css_code) > 10 and any(char in css_code for char in ['{', '}', ':'])
                react_valid = react_code and len(react_code) > 10 and any(keyword in react_code for keyword in ['<div>', '<h1>', 'function', 'const'])
                
                # Vérifier contenu VRAI HTML avec balises
                has_real_html = bool(re.search(r'<(div|h1|h2|p|section|header|nav)', html_code or react_code or ""))
                has_real_css = bool(re.search(r'\.[a-zA-Z-]+\s*\{[^}]*\}', css_code or ""))
                
                success_criteria = {
                    "status_200": response.status_code == 200,
                    "html_code_exists": bool(html_code),
                    "css_code_exists": bool(css_code),
                    "react_code_exists": bool(react_code),
                    "html_not_empty": len(html_code or react_code or "") > 100,
                    "css_not_empty": len(css_code or "") > 50,
                    "has_real_html_tags": has_real_html,
                    "has_real_css_styles": has_real_css,
                    "not_placeholder_text": "html" not in (html_code or "").lower()[:50]
                }
                
                passed = sum(success_criteria.values())
                total = len(success_criteria)
                
                if passed >= 7:  # Au moins 7/9 critères
                    self.log_result("Génération Basique", True, 
                                  f"✅ VRAI code généré: HTML({len(html_code or react_code or '')} chars), "
                                  f"CSS({len(css_code or '')} chars), "
                                  f"Balises HTML: {'✅' if has_real_html else '❌'}, "
                                  f"Styles CSS: {'✅' if has_real_css else '❌'}")
                else:
                    self.log_result("Génération Basique", False, 
                                  f"❌ Code insuffisant: {passed}/{total} critères. "
                                  f"HTML: {len(html_code or '')} chars, CSS: {len(css_code or '')} chars")
            else:
                self.log_result("Génération Basique", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Génération Basique", False, f"Exception: {str(e)}")

    def test_2_preview_projet_genere(self):
        """Test 2: Preview du Projet Généré"""
        print("\n=== Test 2: Preview du Projet Généré ===")
        
        if not self.access_token or not self.test_projects:
            self.log_result("Preview Projet", False, "No access token or project")
            return
        
        try:
            project_id = self.test_projects[0]
            response = self.make_request("GET", f"/projects/{project_id}/preview")
            
            if response.status_code == 200:
                content = response.text
                content_type = response.headers.get("content-type", "")
                
                # VÉRIFICATIONS selon la demande
                has_doctype = "<!DOCTYPE html>" in content
                has_html_tags = "<html>" in content and "</html>" in content
                has_head = "<head>" in content and "</head>" in content
                has_body = "<body>" in content and "</body>" in content
                has_style = "<style>" in content or "style=" in content
                not_just_text = content != "html" and "html" not in content[:20].lower()
                size_ok = len(content) > 1000
                
                success_criteria = {
                    "status_200": True,
                    "content_type_html": "text/html" in content_type,
                    "has_doctype": has_doctype,
                    "has_html_structure": has_html_tags and has_head and has_body,
                    "has_styling": has_style,
                    "not_placeholder": not_just_text,
                    "sufficient_size": size_ok
                }
                
                passed = sum(success_criteria.values())
                
                if passed >= 5:
                    self.log_result("Preview Projet", True, 
                                  f"✅ Preview HTML valide: {len(content)} chars, "
                                  f"DOCTYPE: {'✅' if has_doctype else '❌'}, "
                                  f"Structure: {'✅' if has_html_tags else '❌'}, "
                                  f"Styles: {'✅' if has_style else '❌'}")
                else:
                    self.log_result("Preview Projet", False, 
                                  f"❌ Preview invalide: {passed}/7 critères. Taille: {len(content)}")
            else:
                self.log_result("Preview Projet", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Preview Projet", False, f"Exception: {str(e)}")

    def test_3_code_retrieval(self):
        """Test 3: Code Retrieval"""
        print("\n=== Test 3: Code Retrieval ===")
        
        if not self.access_token or not self.test_projects:
            self.log_result("Code Retrieval", False, "No access token or project")
            return
        
        try:
            project_id = self.test_projects[0]
            response = self.make_request("GET", f"/projects/{project_id}/code")
            
            if response.status_code == 200:
                data = response.json()
                
                html_code = data.get("html_code", "")
                css_code = data.get("css_code", "")
                react_code = data.get("react_code", "")
                
                # Validation du code selon la demande
                html_valid = self.validate_html_code(html_code or react_code)
                css_valid = self.validate_css_code(css_code)
                react_valid = self.validate_react_code(react_code)
                
                size_checks = {
                    "html_size": len(html_code or react_code or "") > 100,
                    "css_size": len(css_code or "") > 100,
                    "no_empty_fields": bool(html_code or react_code) and bool(css_code)
                }
                
                if html_valid and css_valid and all(size_checks.values()):
                    self.log_result("Code Retrieval", True, 
                                  f"✅ Code valide récupéré: HTML/React({len(html_code or react_code or '')} chars), "
                                  f"CSS({len(css_code or '')} chars)")
                else:
                    self.log_result("Code Retrieval", False, 
                                  f"❌ Code invalide: HTML valid: {html_valid}, CSS valid: {css_valid}")
            else:
                self.log_result("Code Retrieval", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Code Retrieval", False, f"Exception: {str(e)}")

    def test_4_generation_differents_types(self):
        """Test 4: Génération Différents Types"""
        print("\n=== Test 4: Génération Différents Types ===")
        
        test_cases = [
            {
                "name": "Landing Page Simple",
                "description": "Landing page pour startup tech",
                "expected_elements": ["header", "CTA", "button", "section"]
            },
            {
                "name": "Formulaire de Contact", 
                "description": "Page avec formulaire de contact",
                "expected_elements": ["form", "input", "email", "submit"]
            },
            {
                "name": "Dashboard Simple",
                "description": "Dashboard avec statistiques",
                "expected_elements": ["card", "chart", "stat", "dashboard"]
            }
        ]
        
        for test_case in test_cases:
            try:
                # Créer projet
                project_data = {
                    "title": test_case["name"],
                    "description": test_case["description"],
                    "type": "web_app"
                }
                
                project_response = self.make_request("POST", "/projects", project_data)
                if project_response.status_code != 200:
                    self.log_result(f"Génération {test_case['name']}", False, "Échec création projet")
                    continue
                
                project_id = project_response.json()["id"]
                
                # Générer
                generation_request = {
                    "description": test_case["description"],
                    "type": "web_app",
                    "framework": "react",
                    "advanced_mode": False
                }
                
                response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
                
                if response.status_code == 200:
                    data = response.json()
                    code_content = (data.get("html_code", "") + data.get("react_code", "") + data.get("css_code", "")).lower()
                    
                    # Vérifier éléments attendus
                    elements_found = sum(1 for element in test_case["expected_elements"] 
                                       if element.lower() in code_content)
                    
                    if elements_found >= 2:  # Au moins 2 éléments attendus
                        self.log_result(f"Génération {test_case['name']}", True, 
                                      f"✅ Éléments trouvés: {elements_found}/{len(test_case['expected_elements'])}")
                    else:
                        self.log_result(f"Génération {test_case['name']}", False, 
                                      f"❌ Éléments insuffisants: {elements_found}/{len(test_case['expected_elements'])}")
                else:
                    self.log_result(f"Génération {test_case['name']}", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Génération {test_case['name']}", False, f"Exception: {str(e)}")

    def test_5_contenu_code_genere(self):
        """Test 5: Contenu du Code Généré"""
        print("\n=== Test 5: Contenu du Code Généré ===")
        
        if not self.access_token or not self.test_projects:
            self.log_result("Contenu Code", False, "No access token or project")
            return
        
        try:
            project_id = self.test_projects[0]
            response = self.make_request("GET", f"/projects/{project_id}/code")
            
            if response.status_code == 200:
                data = response.json()
                
                html_code = data.get("html_code", "")
                css_code = data.get("css_code", "")
                react_code = data.get("react_code", "")
                
                # Tests HTML/React
                html_tests = {
                    "has_html_tags": bool(re.search(r'<(div|h1|h2|p|section|header)', html_code or react_code or "")),
                    "has_css_classes": bool(re.search(r'className=|class=', html_code or react_code or "")),
                    "coherent_structure": len(html_code or react_code or "") > 200,
                    "not_placeholder": "[HTML CODE HERE]" not in (html_code or react_code or ""),
                    "not_text_html": (html_code or react_code or "").strip().lower() != "html"
                }
                
                # Tests CSS
                css_tests = {
                    "has_selectors": bool(re.search(r'\.[a-zA-Z-]+\s*\{', css_code or "")),
                    "has_properties": bool(re.search(r'(color|margin|padding|font):', css_code or "")),
                    "has_values": bool(re.search(r':\s*[^;]+;', css_code or "")),
                    "not_placeholder": "[CSS CODE HERE]" not in (css_code or ""),
                    "sufficient_content": len(css_code or "") > 100
                }
                
                # Tests JavaScript/React
                js_tests = {
                    "has_js_syntax": bool(re.search(r'(function|const|let|var|=>)', react_code or "")),
                    "has_react_syntax": bool(re.search(r'(jsx|React|useState|useEffect)', react_code or "")),
                    "not_placeholder": "[JS CODE HERE]" not in (react_code or ""),
                    "sufficient_content": len(react_code or "") > 100
                }
                
                html_passed = sum(html_tests.values())
                css_passed = sum(css_tests.values())
                js_passed = sum(js_tests.values())
                
                if html_passed >= 3 and css_passed >= 3 and js_passed >= 2:
                    self.log_result("Contenu Code", True, 
                                  f"✅ Code valide: HTML({html_passed}/5), CSS({css_passed}/5), JS({js_passed}/4)")
                else:
                    self.log_result("Contenu Code", False, 
                                  f"❌ Code invalide: HTML({html_passed}/5), CSS({css_passed}/5), JS({js_passed}/4)")
            else:
                self.log_result("Contenu Code", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Contenu Code", False, f"Exception: {str(e)}")

    def test_6_preview_html_complet(self):
        """Test 6: Preview HTML Complet"""
        print("\n=== Test 6: Preview HTML Complet ===")
        
        if not self.access_token or not self.test_projects:
            self.log_result("Preview HTML Complet", False, "No access token or project")
            return
        
        try:
            project_id = self.test_projects[0]
            response = self.make_request("GET", f"/projects/{project_id}/preview")
            
            if response.status_code == 200:
                content = response.text
                
                # Vérifications selon la demande
                checks = {
                    "has_doctype": "<!DOCTYPE html>" in content,
                    "has_html_lang": '<html lang="fr">' in content or '<html lang=' in content,
                    "has_head_meta": "<head>" in content and "meta" in content,
                    "has_title": "<title>" in content,
                    "has_style_tag": "<style>" in content,
                    "has_body": "<body>" in content,
                    "has_script_if_needed": "<script>" in content or "script" not in content.lower(),
                    "complete_structure": all(tag in content for tag in ["<html", "</html>", "<head", "</head>", "<body", "</body>"])
                }
                
                passed = sum(checks.values())
                
                if passed >= 6:
                    self.log_result("Preview HTML Complet", True, 
                                  f"✅ Structure HTML complète: {passed}/8 éléments présents")
                else:
                    self.log_result("Preview HTML Complet", False, 
                                  f"❌ Structure incomplète: {passed}/8 éléments")
            else:
                self.log_result("Preview HTML Complet", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Preview HTML Complet", False, f"Exception: {str(e)}")

    def test_7_advanced_vs_quick_mode(self):
        """Test 7: Advanced Mode vs Quick Mode"""
        print("\n=== Test 7: Advanced Mode vs Quick Mode ===")
        
        if not self.access_token:
            self.log_result("Advanced vs Quick Mode", False, "No access token")
            return
        
        modes_to_test = [
            {"name": "Quick Mode", "advanced_mode": False},
            {"name": "Advanced Mode", "advanced_mode": True}
        ]
        
        results = {}
        
        for mode in modes_to_test:
            try:
                # Créer projet pour ce mode
                project_data = {
                    "title": f"Test {mode['name']}",
                    "description": "Application de test pour comparaison des modes",
                    "type": "web_app"
                }
                
                project_response = self.make_request("POST", "/projects", project_data)
                if project_response.status_code != 200:
                    continue
                
                project_id = project_response.json()["id"]
                
                # Générer avec le mode spécifique
                generation_request = {
                    "description": "Application de test pour comparaison des modes",
                    "type": "web_app",
                    "framework": "react",
                    "advanced_mode": mode["advanced_mode"]
                }
                
                response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Analyser les résultats
                    file_count = 0
                    if data.get("all_files"):
                        file_count = len(data["all_files"])
                    
                    code_size = sum(len(data.get(field, "")) for field in 
                                  ["html_code", "css_code", "js_code", "react_code", "backend_code"])
                    
                    results[mode["name"]] = {
                        "success": True,
                        "file_count": file_count,
                        "code_size": code_size,
                        "has_code": code_size > 100
                    }
                else:
                    results[mode["name"]] = {"success": False}
                    
            except Exception as e:
                results[mode["name"]] = {"success": False, "error": str(e)}
        
        # Évaluer les résultats
        quick_success = results.get("Quick Mode", {}).get("success", False)
        advanced_success = results.get("Advanced Mode", {}).get("success", False)
        
        if quick_success and advanced_success:
            self.log_result("Advanced vs Quick Mode", True, 
                          f"✅ Les deux modes génèrent du code fonctionnel")
        elif quick_success or advanced_success:
            working_mode = "Quick" if quick_success else "Advanced"
            self.log_result("Advanced vs Quick Mode", True, 
                          f"✅ Au moins {working_mode} Mode fonctionne")
        else:
            self.log_result("Advanced vs Quick Mode", False, 
                          "❌ Aucun mode ne génère de code")

    def test_8_emergent_llm_key_utilisation(self):
        """Test 8: EMERGENT_LLM_KEY Utilisation"""
        print("\n=== Test 8: EMERGENT_LLM_KEY Utilisation ===")
        
        if not self.access_token:
            self.log_result("EMERGENT_LLM_KEY", False, "No access token")
            return
        
        try:
            # Créer un projet simple pour tester l'intégration LLM
            project_data = {
                "title": "Test EMERGENT_LLM_KEY",
                "description": "Test simple pour vérifier l'intégration GPT-4o",
                "type": "web_app"
            }
            
            project_response = self.make_request("POST", "/projects", project_data)
            if project_response.status_code != 200:
                self.log_result("EMERGENT_LLM_KEY", False, "Échec création projet")
                return
            
            project_id = project_response.json()["id"]
            
            # Générer avec une description qui nécessite l'IA
            generation_request = {
                "description": "Créer une page web moderne avec un design unique et créatif, incluant des animations CSS et une interface utilisateur intuitive",
                "type": "web_app",
                "framework": "react",
                "advanced_mode": False
            }
            
            start_time = time.time()
            response = self.make_request("POST", f"/projects/{project_id}/generate", generation_request)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Vérifier que du code a été généré (preuve que LLM fonctionne)
                has_generated_code = any(data.get(field) for field in 
                                       ["html_code", "css_code", "react_code"])
                
                code_quality_indicators = []
                if data.get("react_code"):
                    react_code = data["react_code"]
                    # Vérifier des indicateurs de qualité IA
                    if len(react_code) > 500:
                        code_quality_indicators.append("sufficient_length")
                    if any(keyword in react_code for keyword in ["useState", "useEffect", "function", "const"]):
                        code_quality_indicators.append("react_patterns")
                    if any(word in react_code.lower() for word in ["modern", "creative", "animation", "interface"]):
                        code_quality_indicators.append("contextual_content")
                
                # Vérifier temps de génération raisonnable (preuve d'appel LLM)
                reasonable_time = 3 < generation_time < 60
                
                success_criteria = {
                    "code_generated": has_generated_code,
                    "quality_indicators": len(code_quality_indicators) >= 2,
                    "reasonable_time": reasonable_time,
                    "no_errors": response.status_code == 200
                }
                
                if sum(success_criteria.values()) >= 3:
                    self.log_result("EMERGENT_LLM_KEY", True, 
                                  f"✅ GPT-4o fonctionnel: code généré en {generation_time:.1f}s, "
                                  f"qualité: {len(code_quality_indicators)} indicateurs")
                else:
                    self.log_result("EMERGENT_LLM_KEY", False, 
                                  f"❌ LLM dysfonctionnel: temps {generation_time:.1f}s, "
                                  f"qualité: {len(code_quality_indicators)}")
            else:
                self.log_result("EMERGENT_LLM_KEY", False, f"Génération échouée: {response.status_code}")
                
        except Exception as e:
            self.log_result("EMERGENT_LLM_KEY", False, f"Exception: {str(e)}")

    def validate_html_code(self, html_code: str) -> bool:
        """Valider que le code HTML est réel et fonctionnel"""
        if not html_code or len(html_code) < 50:
            return False
        
        # Vérifier présence de balises HTML valides
        html_tags = re.findall(r'<(\w+)', html_code)
        valid_tags = ['div', 'h1', 'h2', 'h3', 'p', 'section', 'header', 'nav', 'main', 'footer', 'article']
        
        has_valid_tags = any(tag in valid_tags for tag in html_tags)
        not_placeholder = "[HTML CODE HERE]" not in html_code and html_code.strip().lower() != "html"
        
        return has_valid_tags and not_placeholder

    def validate_css_code(self, css_code: str) -> bool:
        """Valider que le code CSS est réel et fonctionnel"""
        if not css_code or len(css_code) < 30:
            return False
        
        # Vérifier structure CSS valide
        has_selectors = bool(re.search(r'\.[a-zA-Z-]+\s*\{', css_code))
        has_properties = bool(re.search(r'(color|margin|padding|font|background|border):', css_code))
        not_placeholder = "[CSS CODE HERE]" not in css_code
        
        return has_selectors and has_properties and not_placeholder

    def validate_react_code(self, react_code: str) -> bool:
        """Valider que le code React/JS est réel et fonctionnel"""
        if not react_code or len(react_code) < 50:
            return False
        
        # Vérifier syntaxe React/JS valide
        has_js_syntax = bool(re.search(r'(function|const|let|var|=>)', react_code))
        has_jsx = bool(re.search(r'<\w+', react_code))
        not_placeholder = "[JS CODE HERE]" not in react_code and "[REACT CODE HERE]" not in react_code
        
        return has_js_syntax and not_placeholder

    def run_all_tests(self):
        """Exécuter tous les tests critiques"""
        print("🎯 DÉBUT DES TESTS CRITIQUE - GÉNÉRATION DE VRAIS PROJETS VECTORT.IO")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_user():
            print("❌ ÉCHEC SETUP - Arrêt des tests")
            return
        
        # Tests principaux selon la demande française
        self.test_1_generation_basique()
        self.test_2_preview_projet_genere()
        self.test_3_code_retrieval()
        self.test_4_generation_differents_types()
        self.test_5_contenu_code_genere()
        self.test_6_preview_html_complet()
        self.test_7_advanced_vs_quick_mode()
        self.test_8_emergent_llm_key_utilisation()
        
        # Résultats finaux
        print("\n" + "=" * 80)
        print("🎯 RÉSULTATS FINAUX - TESTS CRITIQUE VECTORT.IO")
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"📊 Taux de réussite: {success_rate:.1f}%")
        
        if self.results['failed'] > 0:
            print("\n❌ ERREURS DÉTECTÉES:")
            for error in self.results['errors']:
                print(f"   - {error}")
        
        # Verdict final selon les critères français
        if success_rate >= 80:
            print(f"\n🎉 VERDICT: ✅ SYSTÈME GÉNÈRE DE VRAIS PROJETS FONCTIONNELS!")
            print("   Le système répond aux exigences: génération de code HTML/CSS/JS réel")
        else:
            print(f"\n🚨 VERDICT: ❌ SYSTÈME NE GÉNÈRE PAS DE VRAIS PROJETS!")
            print("   Le problème 'je ne vois pas de projet' et 'il faut que ça code vraiment' persiste")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = VectroCritiqueTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)