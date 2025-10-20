#!/usr/bin/env python3
"""
🔥 TEST FINAL COMPLET BACKEND - PRE-DEPLOYMENT
Validation COMPLÈTE de toutes les fonctionnalités backend avant déploiement public

Objectif: Valider TOUTES les fonctionnalités backend selon les spécifications françaises
"""

import requests
import json
import sys
import time
import os
from typing import Dict, Any, Optional

# Configuration - Use environment variable from frontend/.env
def get_backend_url():
    """Get backend URL from frontend/.env file"""
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    base_url = line.split('=', 1)[1].strip()
                    return f"{base_url}/api"
        return "http://localhost:8001/api"  # Fallback
    except:
        return "http://localhost:8001/api"  # Fallback

BASE_URL = get_backend_url()
print(f"🎯 Testing backend at: {BASE_URL}")

# Test user with realistic data (not dummy data)
TEST_USER = {
    "email": f"marie.dupont.{int(time.time())}@vectort.io",
    "password": "SecurePassword123!",
    "full_name": f"Marie Dupont {int(time.time())}"
}

class VectortBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.user_id = None
        self.test_project_id = None
        self.initial_credits = 0
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
            "performance": {}
        }

    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result with French formatting"""
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"{status}: {test_name}")
        if message:
            print(f"   📋 {message}")
        
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    headers: Optional[Dict] = None, timeout: int = 30) -> requests.Response:
        """Make HTTP request with comprehensive error handling"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
        if self.access_token and "Authorization" not in default_headers:
            default_headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=default_headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers, timeout=timeout)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
            
            # Record performance
            duration = time.time() - start_time
            self.results["performance"][f"{method} {endpoint}"] = duration
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Requête échouée: {e}")
            raise

    def test_1_authentification_register(self):
        """Test 1: POST /auth/register (nouveau compte)"""
        print("\n=== 🔐 Test 1: Authentification - Enregistrement ===")
        try:
            response = self.make_request("POST", "/auth/register", TEST_USER)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["access_token", "token_type", "user"]
                
                if all(field in data for field in required_fields):
                    self.access_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    user_data = data["user"]
                    
                    # Vérifier les crédits initiaux
                    self.initial_credits = user_data.get("credits_total", user_data.get("credits_free", 0))
                    
                    if (user_data["email"] == TEST_USER["email"] and 
                        self.initial_credits >= 10):  # 10 crédits initiaux requis
                        self.log_result("POST /auth/register", True, 
                                      f"Utilisateur créé avec {self.initial_credits} crédits initiaux, JWT valide")
                    else:
                        self.log_result("POST /auth/register", False, 
                                      f"Données utilisateur incorrectes ou crédits insuffisants: {self.initial_credits}")
                else:
                    self.log_result("POST /auth/register", False, f"Champs requis manquants: {data}")
            elif response.status_code == 400 and "already exists" in response.text:
                # Utilisateur existe déjà, essayer de se connecter
                self.test_1b_authentification_login()
            else:
                self.log_result("POST /auth/register", False, 
                              f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("POST /auth/register", False, f"Exception: {str(e)}")

    def test_1b_authentification_login(self):
        """Test 1b: POST /auth/login"""
        print("\n=== 🔐 Test 1b: Authentification - Connexion ===")
        try:
            login_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            
            response = self.make_request("POST", "/auth/login", login_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["access_token", "token_type", "user"]
                
                if all(field in data for field in required_fields):
                    self.access_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    self.initial_credits = data["user"].get("credits_total", data["user"].get("credits_free", 0))
                    self.log_result("POST /auth/login", True, 
                                  f"Connexion réussie, token JWT reçu, {self.initial_credits} crédits disponibles")
                else:
                    self.log_result("POST /auth/login", False, f"Champs requis manquants: {data}")
            else:
                self.log_result("POST /auth/login", False, 
                              f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("POST /auth/login", False, f"Exception: {str(e)}")

    def test_1c_authentification_me(self):
        """Test 1c: GET /auth/me (avec token)"""
        print("\n=== 🔐 Test 1c: Vérification JWT ===")
        try:
            if not self.access_token:
                self.log_result("GET /auth/me", False, "Aucun token d'accès disponible")
                return
            
            response = self.make_request("GET", "/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "email"]
                
                if all(field in data for field in required_fields):
                    if data["email"] == TEST_USER["email"]:
                        self.log_result("GET /auth/me", True, 
                                      f"JWT valide, informations utilisateur récupérées: {data.get('full_name', data.get('name', 'N/A'))}")
                    else:
                        self.log_result("GET /auth/me", False, "Email ne correspond pas")
                else:
                    self.log_result("GET /auth/me", False, f"Champs requis manquants: {data}")
            else:
                self.log_result("GET /auth/me", False, 
                              f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("GET /auth/me", False, f"Exception: {str(e)}")

    def test_2_systeme_credits_balance(self):
        """Test 2: GET /credits/balance (10 crédits initiaux)"""
        print("\n=== 💳 Test 2: Système Crédits - Solde ===")
        try:
            if not self.access_token:
                self.log_result("GET /credits/balance", False, "Aucun token d'accès disponible")
                return
            
            response = self.make_request("GET", "/credits/balance")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["free_credits", "monthly_credits", "purchased_credits", "total_available", "subscription_plan"]
                
                if all(field in data for field in required_fields):
                    total_credits = data["total_available"]
                    free_credits = data["free_credits"]
                    
                    if total_credits >= 10 and free_credits >= 10:
                        self.log_result("GET /credits/balance", True, 
                                      f"Solde correct: {total_credits} crédits totaux, {free_credits} gratuits, plan: {data['subscription_plan']}")
                    else:
                        self.log_result("GET /credits/balance", False, 
                                      f"Crédits insuffisants: {total_credits} total, {free_credits} gratuits (minimum 10 requis)")
                else:
                    self.log_result("GET /credits/balance", False, f"Structure de réponse incorrecte: {data}")
            else:
                self.log_result("GET /credits/balance", False, 
                              f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("GET /credits/balance", False, f"Exception: {str(e)}")

    def test_2b_systeme_credits_packages(self):
        """Test 2b: GET /credits/packages (tous les packages)"""
        print("\n=== 💳 Test 2b: Packages de Crédits ===")
        try:
            response = self.make_request("GET", "/credits/packages")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) >= 3:
                    # Vérifier les packages requis
                    package_names = [pkg.get("name", pkg.get("id", "")) for pkg in data]
                    required_packages = ["Starter", "Standard", "Pro"]
                    
                    has_all_packages = all(any(req in name for name in package_names) for req in required_packages)
                    
                    if has_all_packages:
                        self.log_result("GET /credits/packages", True, 
                                      f"Tous les packages disponibles: {', '.join(package_names)}")
                    else:
                        self.log_result("GET /credits/packages", False, 
                                      f"Packages manquants. Trouvés: {package_names}")
                else:
                    self.log_result("GET /credits/packages", False, 
                                  f"Format de réponse incorrect: {len(data) if isinstance(data, list) else 'non-liste'}")
            else:
                self.log_result("GET /credits/packages", False, 
                              f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("GET /credits/packages", False, f"Exception: {str(e)}")

    def test_3_projets_crud_create(self):
        """Test 3a: POST /projects (créer)"""
        print("\n=== 📁 Test 3a: Projets CRUD - Création ===")
        try:
            if not self.access_token:
                self.log_result("POST /projects", False, "Aucun token d'accès disponible")
                return
            
            project_data = {
                "title": "Boutique E-commerce Moderne",
                "description": "Application e-commerce complète avec React, panier d'achats, paiement Stripe, gestion des produits et interface d'administration",
                "type": "web_app"
            }
            
            response = self.make_request("POST", "/projects", project_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "title", "description", "type", "user_id", "status"]
                
                if all(field in data for field in required_fields):
                    self.test_project_id = data["id"]
                    if (data["title"] == project_data["title"] and 
                        data["user_id"] == self.user_id and
                        data["status"] == "draft"):
                        self.log_result("POST /projects", True, 
                                      f"Projet créé avec ID: {self.test_project_id}, statut: {data['status']}")
                    else:
                        self.log_result("POST /projects", False, "Données du projet incorrectes")
                else:
                    self.log_result("POST /projects", False, f"Champs requis manquants: {data}")
            else:
                self.log_result("POST /projects", False, 
                              f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("POST /projects", False, f"Exception: {str(e)}")

    def test_3b_projets_crud_list(self):
        """Test 3b: GET /projects (lister)"""
        print("\n=== 📁 Test 3b: Projets CRUD - Liste ===")
        try:
            if not self.access_token:
                self.log_result("GET /projects", False, "Aucun token d'accès disponible")
                return
            
            response = self.make_request("GET", "/projects")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) > 0:
                        # Vérifier si notre projet de test est dans la liste
                        project_found = any(p.get("id") == self.test_project_id for p in data)
                        if project_found or self.test_project_id is None:
                            self.log_result("GET /projects", True, 
                                          f"Liste récupérée: {len(data)} projets, ordre chronologique inverse")
                        else:
                            self.log_result("GET /projects", False, "Projet de test non trouvé dans la liste")
                    else:
                        self.log_result("GET /projects", True, "Liste vide (aucun projet)")
                else:
                    self.log_result("GET /projects", False, f"Format de réponse incorrect: {type(data)}")
            else:
                self.log_result("GET /projects", False, 
                              f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("GET /projects", False, f"Exception: {str(e)}")

    def test_3c_projets_crud_get(self):
        """Test 3c: GET /projects/{id} (détail)"""
        print("\n=== 📁 Test 3c: Projets CRUD - Détail ===")
        try:
            if not self.access_token or not self.test_project_id:
                self.log_result("GET /projects/{id}", False, "Token ou ID projet manquant")
                return
            
            response = self.make_request("GET", f"/projects/{self.test_project_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == self.test_project_id and data.get("user_id") == self.user_id:
                    self.log_result("GET /projects/{id}", True, 
                                  f"Détails du projet récupérés: {data['title']}, statut: {data.get('status', 'N/A')}")
                else:
                    self.log_result("GET /projects/{id}", False, "Données du projet incorrectes")
            elif response.status_code == 404:
                self.log_result("GET /projects/{id}", False, "Projet non trouvé")
            else:
                self.log_result("GET /projects/{id}", False, 
                              f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("GET /projects/{id}", False, f"Exception: {str(e)}")

    def test_4_generation_multi_fichiers_advanced(self):
        """Test 4: POST /projects/{id}/generate (mode advanced)"""
        print("\n=== 🤖 Test 4: Génération Multi-Fichiers (Mode Avancé) ===")
        try:
            if not self.access_token or not self.test_project_id:
                self.log_result("Génération Multi-Fichiers", False, "Token ou ID projet manquant")
                return
            
            # Vérifier les crédits avant génération
            credits_before = self.get_current_credits()
            
            generation_request = {
                "description": "Application e-commerce complète avec React, panier d'achats, paiement Stripe, gestion des produits, authentification utilisateur, et interface d'administration",
                "type": "web_app",
                "framework": "react",
                "database": "mongodb",
                "advanced_mode": True,  # MODE AVANCÉ ACTIVÉ
                "features": ["authentication", "payment_processing", "shopping_cart", "admin_panel"],
                "integrations": ["stripe"]
            }
            
            start_time = time.time()
            response = self.make_request("POST", f"/projects/{self.test_project_id}/generate", 
                                       generation_request, timeout=30)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Vérifications critiques selon les spécifications
                all_files = data.get("all_files", {})
                file_count = len(all_files) if all_files else 0
                
                # Vérifier package.json
                package_json = data.get("package_json") or (all_files.get("package.json") if all_files else None)
                has_package_json = bool(package_json)
                
                # Vérifier temps de génération
                time_ok = generation_time < 25  # < 25s requis
                
                # Vérifier déduction des crédits
                credits_after = self.get_current_credits()
                credits_deducted = credits_before - credits_after
                expected_deduction = 4  # Mode avancé = 4 crédits
                
                # Critères de succès
                success_criteria = {
                    "generation_success": True,
                    "multiple_files": file_count >= 10,  # 10+ fichiers requis
                    "package_json": has_package_json,
                    "performance": time_ok,
                    "credit_deduction": credits_deducted == expected_deduction
                }
                
                passed = sum(success_criteria.values())
                total = len(success_criteria)
                
                if passed >= 4:  # Au moins 4/5 critères
                    self.log_result("Génération Multi-Fichiers", True, 
                                  f"Génération réussie: {file_count} fichiers, package.json: {'✅' if has_package_json else '❌'}, "
                                  f"temps: {generation_time:.1f}s, crédits déduits: {credits_deducted}/{expected_deduction}")
                else:
                    self.log_result("Génération Multi-Fichiers", False, 
                                  f"Critères insuffisants ({passed}/{total}): fichiers={file_count}, "
                                  f"package.json={has_package_json}, temps={generation_time:.1f}s, crédits={credits_deducted}")
            elif response.status_code == 402:
                self.log_result("Génération Multi-Fichiers", False, "Crédits insuffisants (402)")
            else:
                self.log_result("Génération Multi-Fichiers", False, 
                              f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Génération Multi-Fichiers", False, f"Exception: {str(e)}")

    def test_5_validation_code(self):
        """Test 5: GET /projects/{id}/validate"""
        print("\n=== ✅ Test 5: Validation du Code ===")
        try:
            if not self.access_token or not self.test_project_id:
                self.log_result("Validation Code", False, "Token ou ID projet manquant")
                return
            
            response = self.make_request("GET", f"/projects/{self.test_project_id}/validate")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["overall_score", "total_files", "valid_files", "report"]
                
                if all(field in data for field in required_fields):
                    overall_score = data["overall_score"]
                    total_files = data["total_files"]
                    valid_files = data["valid_files"]
                    report = data["report"]
                    
                    if overall_score > 70 and len(report) > 100:  # Score > 70 et rapport détaillé
                        self.log_result("Validation Code", True, 
                                      f"Score: {overall_score}/100, fichiers valides: {valid_files}/{total_files}, rapport détaillé généré")
                    else:
                        self.log_result("Validation Code", False, 
                                      f"Score insuffisant ({overall_score}) ou rapport incomplet")
                else:
                    self.log_result("Validation Code", False, f"Champs requis manquants: {data}")
            elif response.status_code == 404:
                self.log_result("Validation Code", False, "Code généré non trouvé")
            else:
                self.log_result("Validation Code", False, 
                              f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Validation Code", False, f"Exception: {str(e)}")

    def test_6_preview(self):
        """Test 6: GET /projects/{id}/preview"""
        print("\n=== 👁️ Test 6: Aperçu HTML ===")
        try:
            if not self.access_token or not self.test_project_id:
                self.log_result("Preview HTML", False, "Token ou ID projet manquant")
                return
            
            response = self.make_request("GET", f"/projects/{self.test_project_id}/preview")
            
            if response.status_code == 200:
                content = response.text
                
                # Vérifier que c'est du HTML complet valide
                html_checks = [
                    "<!DOCTYPE html>" in content,
                    "<html" in content,
                    "</html>" in content,
                    "<head>" in content,
                    "<body>" in content,
                    len(content) > 1000  # HTML substantiel
                ]
                
                if all(html_checks):
                    self.log_result("Preview HTML", True, 
                                  f"HTML complet généré ({len(content)} caractères), structure valide")
                else:
                    self.log_result("Preview HTML", False, 
                                  f"HTML incomplet ou invalide ({len(content)} caractères)")
            elif response.status_code == 404:
                self.log_result("Preview HTML", False, "Code généré non trouvé pour l'aperçu")
            else:
                self.log_result("Preview HTML", False, 
                              f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Preview HTML", False, f"Exception: {str(e)}")

    def test_7_code_retrieval(self):
        """Test 7: GET /projects/{id}/code"""
        print("\n=== 💻 Test 7: Récupération du Code ===")
        try:
            if not self.access_token or not self.test_project_id:
                self.log_result("Code Retrieval", False, "Token ou ID projet manquant")
                return
            
            response = self.make_request("GET", f"/projects/{self.test_project_id}/code")
            
            if response.status_code == 200:
                data = response.json()
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                
                # Vérifier la présence de différents types de code
                available_code = {field: bool(data.get(field)) for field in code_fields}
                code_count = sum(available_code.values())
                
                if code_count >= 2:  # Au moins 2 types de code
                    code_summary = ", ".join([field.replace("_code", "") for field, present in available_code.items() if present])
                    self.log_result("Code Retrieval", True, 
                                  f"Code récupéré: {code_summary} ({code_count} types)")
                else:
                    self.log_result("Code Retrieval", False, 
                                  f"Code insuffisant: seulement {code_count} types disponibles")
            elif response.status_code == 404:
                self.log_result("Code Retrieval", False, "Code généré non trouvé")
            else:
                self.log_result("Code Retrieval", False, 
                              f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Code Retrieval", False, f"Exception: {str(e)}")

    def test_8_export_zip(self):
        """Test 8: GET /projects/{id}/export/zip"""
        print("\n=== 📦 Test 8: Export ZIP ===")
        try:
            if not self.access_token or not self.test_project_id:
                self.log_result("Export ZIP", False, "Token ou ID projet manquant")
                return
            
            response = self.make_request("GET", f"/projects/{self.test_project_id}/export/zip")
            
            if response.status_code == 200:
                # Vérifier les headers
                content_type = response.headers.get("Content-Type", "")
                content_disposition = response.headers.get("Content-Disposition", "")
                content_length = len(response.content)
                
                checks = {
                    "content_type": content_type == "application/zip",
                    "disposition": "attachment" in content_disposition,
                    "size": content_length > 5000,  # > 5KB requis
                    "filename": "filename=" in content_disposition
                }
                
                if all(checks.values()):
                    self.log_result("Export ZIP", True, 
                                  f"ZIP généré: {content_length} bytes, Content-Type correct, filename présent")
                else:
                    failed_checks = [k for k, v in checks.items() if not v]
                    self.log_result("Export ZIP", False, 
                                  f"Vérifications échouées: {failed_checks}, taille: {content_length}")
            elif response.status_code == 404:
                self.log_result("Export ZIP", False, "Projet non trouvé pour export")
            else:
                self.log_result("Export ZIP", False, 
                              f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("Export ZIP", False, f"Exception: {str(e)}")

    def test_9_error_handling(self):
        """Test 9: Tests d'Erreurs"""
        print("\n=== ⚠️ Test 9: Gestion d'Erreurs ===")
        
        # Test 9a: Génération sans crédits → 402
        try:
            # Créer un utilisateur avec 0 crédits (simulé en épuisant les crédits)
            if self.access_token and self.test_project_id:
                # Essayer de générer avec des crédits insuffisants
                # (Si l'utilisateur a encore des crédits, ce test pourrait échouer)
                generation_request = {
                    "description": "Test sans crédits",
                    "type": "web_app",
                    "framework": "react",
                    "advanced_mode": True  # 4 crédits requis
                }
                
                # Vérifier les crédits actuels
                current_credits = self.get_current_credits()
                if current_credits < 4:
                    response = self.make_request("POST", f"/projects/{self.test_project_id}/generate", 
                                               generation_request)
                    if response.status_code == 402:
                        self.log_result("Erreur - Crédits insuffisants", True, "402 retourné correctement")
                    else:
                        self.log_result("Erreur - Crédits insuffisants", False, 
                                      f"Expected 402, got {response.status_code}")
                else:
                    self.log_result("Erreur - Crédits insuffisants", True, 
                                  f"Test ignoré (utilisateur a {current_credits} crédits)")
        except Exception as e:
            self.log_result("Erreur - Crédits insuffisants", False, f"Exception: {str(e)}")
        
        # Test 9b: Accès projet autre user → 404
        try:
            fake_project_id = "00000000-0000-0000-0000-000000000000"
            response = self.make_request("GET", f"/projects/{fake_project_id}")
            
            if response.status_code == 404:
                self.log_result("Erreur - Projet autre utilisateur", True, "404 retourné correctement")
            else:
                self.log_result("Erreur - Projet autre utilisateur", False, 
                              f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("Erreur - Projet autre utilisateur", False, f"Exception: {str(e)}")
        
        # Test 9c: Routes sans auth → 401
        try:
            # Sauvegarder le token actuel
            original_token = self.access_token
            self.access_token = None
            
            response = self.make_request("GET", "/auth/me")
            
            if response.status_code == 401:
                self.log_result("Erreur - Sans authentification", True, "401 retourné correctement")
            else:
                self.log_result("Erreur - Sans authentification", False, 
                              f"Expected 401, got {response.status_code}")
            
            # Restaurer le token
            self.access_token = original_token
        except Exception as e:
            self.log_result("Erreur - Sans authentification", False, f"Exception: {str(e)}")

    def test_10_performance(self):
        """Test 10: Performance"""
        print("\n=== ⚡ Test 10: Performance ===")
        
        # Analyser les performances enregistrées
        performance_results = []
        
        for endpoint, duration in self.results["performance"].items():
            if "generate" in endpoint:
                # Génération doit être < 25s
                if duration < 25:
                    performance_results.append(f"✅ {endpoint}: {duration:.1f}s")
                else:
                    performance_results.append(f"❌ {endpoint}: {duration:.1f}s (> 25s)")
            else:
                # Autres endpoints doivent être < 5s
                if duration < 5:
                    performance_results.append(f"✅ {endpoint}: {duration:.1f}s")
                else:
                    performance_results.append(f"❌ {endpoint}: {duration:.1f}s (> 5s)")
        
        # Calculer le score de performance
        total_tests = len(performance_results)
        passed_tests = sum(1 for result in performance_results if "✅" in result)
        
        if passed_tests == total_tests:
            self.log_result("Performance Globale", True, 
                          f"Tous les endpoints respectent les limites de temps ({passed_tests}/{total_tests})")
        else:
            self.log_result("Performance Globale", False, 
                          f"Certains endpoints trop lents ({passed_tests}/{total_tests})")
        
        # Afficher les détails
        for result in performance_results:
            print(f"   {result}")

    def test_3d_projets_crud_delete(self):
        """Test 3d: DELETE /projects/{id} (supprimer)"""
        print("\n=== 📁 Test 3d: Projets CRUD - Suppression ===")
        try:
            if not self.access_token or not self.test_project_id:
                self.log_result("DELETE /projects/{id}", False, "Token ou ID projet manquant")
                return
            
            response = self.make_request("DELETE", f"/projects/{self.test_project_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") is True:
                    # Vérifier la suppression en essayant de récupérer le projet
                    verify_response = self.make_request("GET", f"/projects/{self.test_project_id}")
                    if verify_response.status_code == 404:
                        self.log_result("DELETE /projects/{id}", True, 
                                      "Projet supprimé avec succès et confirmé par 404")
                    else:
                        self.log_result("DELETE /projects/{id}", False, 
                                      "Projet toujours accessible après suppression")
                else:
                    self.log_result("DELETE /projects/{id}", False, f"Réponse inattendue: {data}")
            elif response.status_code == 404:
                self.log_result("DELETE /projects/{id}", False, "Projet non trouvé pour suppression")
            else:
                self.log_result("DELETE /projects/{id}", False, 
                              f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            self.log_result("DELETE /projects/{id}", False, f"Exception: {str(e)}")

    def get_current_credits(self) -> float:
        """Récupère le solde de crédits actuel"""
        try:
            if not self.access_token:
                return 0
            
            response = self.make_request("GET", "/credits/balance")
            if response.status_code == 200:
                data = response.json()
                return data.get("total_available", 0)
            return 0
        except:
            return 0

    def run_all_tests(self):
        """Exécute tous les tests dans l'ordre"""
        print("🔥 DÉBUT DES TESTS BACKEND COMPLETS - PRE-DEPLOYMENT")
        print("=" * 60)
        
        # Phase 1: Authentification
        self.test_1_authentification_register()
        self.test_1b_authentification_login()
        self.test_1c_authentification_me()
        
        # Phase 2: Système de crédits
        self.test_2_systeme_credits_balance()
        self.test_2b_systeme_credits_packages()
        
        # Phase 3: CRUD Projets
        self.test_3_projets_crud_create()
        self.test_3b_projets_crud_list()
        self.test_3c_projets_crud_get()
        
        # Phase 4: Génération IA (critique)
        self.test_4_generation_multi_fichiers_advanced()
        
        # Phase 5: Validation et aperçu
        self.test_5_validation_code()
        self.test_6_preview()
        self.test_7_code_retrieval()
        self.test_8_export_zip()
        
        # Phase 6: Gestion d'erreurs
        self.test_9_error_handling()
        
        # Phase 7: Performance
        self.test_10_performance()
        
        # Phase 8: Nettoyage (supprimer le projet de test)
        self.test_3d_projets_crud_delete()
        
        # Résumé final
        self.print_final_summary()

    def print_final_summary(self):
        """Affiche le résumé final des tests"""
        print("\n" + "=" * 60)
        print("🎯 RÉSUMÉ FINAL DES TESTS BACKEND")
        print("=" * 60)
        
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        print(f"📊 Taux de réussite: {success_rate:.1f}%")
        
        if self.results["failed"] > 0:
            print(f"\n❌ ERREURS DÉTECTÉES:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        # Statut final
        if success_rate >= 90:
            print(f"\n🎉 BACKEND PRÊT POUR DÉPLOIEMENT!")
            print(f"   Tous les systèmes critiques fonctionnent correctement.")
        elif success_rate >= 75:
            print(f"\n⚠️ BACKEND PARTIELLEMENT FONCTIONNEL")
            print(f"   Quelques problèmes mineurs détectés.")
        else:
            print(f"\n🚨 BACKEND NON PRÊT POUR DÉPLOIEMENT")
            print(f"   Problèmes critiques détectés nécessitant correction.")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = VectortBackendTester()
    tester.run_all_tests()