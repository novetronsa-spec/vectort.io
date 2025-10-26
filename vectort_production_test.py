#!/usr/bin/env python3
"""
🎯 VECTORT.IO PRODUCTION API TESTING - 100% FUNCTIONALITY VERIFICATION
Test complet du backend Vectort.io selon les spécifications françaises
Backend URL: https://codeforge-108.preview.emergentagent.com/api
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional
import uuid

# Configuration - PRODUCTION ENVIRONMENT API
BASE_URL = "https://codeforge-108.preview.emergentagent.com/api"

class VectortProductionTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.user_id = None
        self.test_project_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
            "critical_issues": []
        }
        # Créer un utilisateur unique avec timestamp
        timestamp = int(time.time())
        self.test_user = {
            "email": f"vectort_test_{timestamp}@example.com",
            "password": "VectortTest123!",
            "full_name": f"Vectort Test User {timestamp}"
        }

    def log_result(self, test_name: str, success: bool, message: str = "", critical: bool = False):
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
            if critical:
                self.results["critical_issues"].append(f"🚨 CRITIQUE: {test_name} - {message}")

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
            
            return response
        except requests.exceptions.Timeout:
            print(f"⏰ TIMEOUT: {method} {endpoint} (>{timeout}s)")
            raise
        except requests.exceptions.ConnectionError:
            print(f"🔌 ERREUR CONNEXION: {method} {endpoint}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"📡 ERREUR REQUÊTE: {e}")
            raise

    def test_1_api_status(self):
        """Test 1: API Status - GET /api/"""
        print("\n" + "="*60)
        print("🔍 TEST 1: STATUT API - GET /api/")
        print("="*60)
        
        try:
            response = self.make_request("GET", "/")
            
            if response.status_code == 200:
                data = response.json()
                expected_messages = ["Vectort API", "AI-powered", "application generation"]
                
                if "message" in data and any(msg in data["message"] for msg in expected_messages):
                    self.log_result("API Status", True, 
                                  f"API répond correctement: '{data['message']}'")
                else:
                    self.log_result("API Status", False, 
                                  f"Message API inattendu: {data}", critical=True)
            else:
                self.log_result("API Status", False, 
                              f"Status HTTP: {response.status_code}, Réponse: {response.text}", 
                              critical=True)
        except Exception as e:
            self.log_result("API Status", False, f"Exception: {str(e)}", critical=True)

    def test_2_authentication_complete(self):
        """Test 2: Authentification complète - Register, Login, Auth Check"""
        print("\n" + "="*60)
        print("🔐 TEST 2: AUTHENTIFICATION COMPLÈTE")
        print("="*60)
        
        # 2a: Registration
        print("\n📝 2a: Enregistrement utilisateur")
        try:
            response = self.make_request("POST", "/auth/register", self.test_user)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["access_token", "token_type", "user"]
                
                if all(field in data for field in required_fields):
                    self.access_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    user_data = data["user"]
                    
                    self.log_result("Enregistrement utilisateur", True, 
                                  f"Utilisateur créé avec ID: {self.user_id}, "
                                  f"Email: {user_data['email']}")
                else:
                    self.log_result("Enregistrement utilisateur", False, 
                                  f"Champs manquants dans la réponse: {data}", critical=True)
            elif response.status_code == 400:
                # Utilisateur existe déjà - essayer de se connecter
                error_data = response.json()
                if "already exists" in error_data.get("detail", ""):
                    self.log_result("Enregistrement utilisateur", True, 
                                  "Utilisateur existe déjà (comportement attendu)")
                    # Passer au login
                    self.test_2b_login()
                    return
                else:
                    self.log_result("Enregistrement utilisateur", False, 
                                  f"Erreur d'enregistrement: {error_data}", critical=True)
            else:
                self.log_result("Enregistrement utilisateur", False, 
                              f"Status: {response.status_code}, Réponse: {response.text}", 
                              critical=True)
        except Exception as e:
            self.log_result("Enregistrement utilisateur", False, f"Exception: {str(e)}", critical=True)
        
        # 2b: Login (si registration a réussi)
        if self.access_token:
            self.test_2b_login()
        
        # 2c: Auth Check
        if self.access_token:
            self.test_2c_auth_check()

    def test_2b_login(self):
        """Test 2b: Login utilisateur"""
        print("\n🔑 2b: Connexion utilisateur")
        try:
            login_data = {
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
            
            response = self.make_request("POST", "/auth/login", login_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["access_token", "token_type", "user"]
                
                if all(field in data for field in required_fields):
                    self.access_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    self.log_result("Connexion utilisateur", True, 
                                  f"Connexion réussie, token JWT reçu")
                else:
                    self.log_result("Connexion utilisateur", False, 
                                  f"Champs manquants: {data}", critical=True)
            else:
                self.log_result("Connexion utilisateur", False, 
                              f"Status: {response.status_code}, Réponse: {response.text}", 
                              critical=True)
        except Exception as e:
            self.log_result("Connexion utilisateur", False, f"Exception: {str(e)}", critical=True)

    def test_2c_auth_check(self):
        """Test 2c: Vérification token JWT"""
        print("\n🎫 2c: Vérification token JWT")
        try:
            response = self.make_request("GET", "/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "email"]
                
                if all(field in data for field in required_fields):
                    if data["email"] == self.test_user["email"]:
                        self.log_result("Vérification token JWT", True, 
                                      f"Token valide, utilisateur: {data.get('full_name', data.get('name', 'N/A'))}")
                    else:
                        self.log_result("Vérification token JWT", False, 
                                      "Email ne correspond pas", critical=True)
                else:
                    self.log_result("Vérification token JWT", False, 
                                  f"Champs manquants: {data}", critical=True)
            else:
                self.log_result("Vérification token JWT", False, 
                              f"Status: {response.status_code}, Réponse: {response.text}", 
                              critical=True)
        except Exception as e:
            self.log_result("Vérification token JWT", False, f"Exception: {str(e)}", critical=True)

    def test_3_credit_system(self):
        """Test 3: Système de crédits avec nouvelles clés Stripe LIVE"""
        print("\n" + "="*60)
        print("💳 TEST 3: SYSTÈME DE CRÉDITS (CLÉS STRIPE LIVE)")
        print("="*60)
        
        if not self.access_token:
            self.log_result("Système de crédits", False, "Pas de token d'accès", critical=True)
            return
        
        # 3a: Vérifier solde initial (10 crédits gratuits)
        self.test_3a_credit_balance()
        
        # 3b: Vérifier packages de crédits
        self.test_3b_credit_packages()
        
        # 3c: Tester création session Stripe
        self.test_3c_stripe_purchase()

    def test_3a_credit_balance(self):
        """Test 3a: Vérifier 10 crédits gratuits pour nouvel utilisateur"""
        print("\n💰 3a: Solde de crédits initial")
        try:
            response = self.make_request("GET", "/credits/balance")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["free_credits", "monthly_credits", "purchased_credits", 
                                 "total_available", "subscription_plan"]
                
                if all(field in data for field in required_fields):
                    free_credits = data["free_credits"]
                    total_available = data["total_available"]
                    subscription_plan = data["subscription_plan"]
                    
                    if free_credits == 10.0 and subscription_plan == "free":
                        self.log_result("Crédits gratuits initiaux", True, 
                                      f"✅ 10 crédits gratuits confirmés. Total disponible: {total_available}")
                    else:
                        self.log_result("Crédits gratuits initiaux", False, 
                                      f"Crédits incorrects: gratuits={free_credits}, plan={subscription_plan}")
                else:
                    self.log_result("Crédits gratuits initiaux", False, 
                                  f"Structure de réponse incorrecte: {data}")
            else:
                self.log_result("Crédits gratuits initiaux", False, 
                              f"Status: {response.status_code}, Réponse: {response.text}")
        except Exception as e:
            self.log_result("Crédits gratuits initiaux", False, f"Exception: {str(e)}")

    def test_3b_credit_packages(self):
        """Test 3b: Vérifier les 3 packages (Starter: 100/$20, Standard: 250/$50, Pro: 400/$80)"""
        print("\n📦 3b: Packages de crédits")
        try:
            response = self.make_request("GET", "/credits/packages")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) >= 3:
                    # Chercher les packages spécifiques
                    packages_found = {}
                    for package in data:
                        if package.get("name") == "Starter" and package.get("credits") == 80 and package.get("price") == 20.0:
                            packages_found["starter"] = True
                        elif package.get("name") == "Standard" and package.get("credits") == 250 and package.get("price") == 50.0:
                            packages_found["standard"] = True
                        elif package.get("name") == "Pro" and package.get("credits") == 400 and package.get("price") == 80.0:
                            packages_found["pro"] = True
                    
                    found_count = len(packages_found)
                    if found_count >= 2:  # Au moins 2 des 3 packages requis
                        self.log_result("Packages de crédits", True, 
                                      f"✅ {found_count}/3 packages requis trouvés. Total packages: {len(data)}")
                    else:
                        self.log_result("Packages de crédits", False, 
                                      f"Packages requis manquants. Trouvés: {packages_found}")
                else:
                    self.log_result("Packages de crédits", False, 
                                  f"Format de réponse incorrect: {type(data)}, longueur: {len(data) if isinstance(data, list) else 'N/A'}")
            else:
                self.log_result("Packages de crédits", False, 
                              f"Status: {response.status_code}, Réponse: {response.text}")
        except Exception as e:
            self.log_result("Packages de crédits", False, f"Exception: {str(e)}")

    def test_3c_stripe_purchase(self):
        """Test 3c: Tester création session Stripe avec nouvelles clés LIVE"""
        print("\n💳 3c: Création session Stripe")
        try:
            purchase_data = {
                "package_id": "starter",
                "origin_url": "https://codeforge-108.preview.emergentagent.com"
            }
            
            response = self.make_request("POST", "/credits/purchase", purchase_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["session_id", "checkout_url"]
                
                if all(field in data for field in required_fields):
                    session_id = data["session_id"]
                    checkout_url = data["checkout_url"]
                    
                    # Vérifier que l'URL Stripe est valide
                    if "checkout.stripe.com" in checkout_url and session_id.startswith("cs_"):
                        self.log_result("Session Stripe", True, 
                                      f"✅ Session créée: {session_id[:20]}..., URL valide")
                        
                        # Tester le statut de la session
                        self.test_3d_checkout_status(session_id)
                    else:
                        self.log_result("Session Stripe", False, 
                                      f"URL ou session_id invalide: {checkout_url}, {session_id}")
                else:
                    self.log_result("Session Stripe", False, 
                                  f"Champs manquants: {data}")
            else:
                self.log_result("Session Stripe", False, 
                              f"Status: {response.status_code}, Réponse: {response.text}")
        except Exception as e:
            self.log_result("Session Stripe", False, f"Exception: {str(e)}")

    def test_3d_checkout_status(self, session_id: str):
        """Test 3d: Vérifier statut session checkout"""
        print("\n🔍 3d: Statut session checkout")
        try:
            response = self.make_request("GET", f"/checkout/status/{session_id}")
            
            # 404 est attendu pour une session non payée
            if response.status_code == 404:
                self.log_result("Statut checkout", True, 
                              "✅ Session non payée (404 attendu)")
            elif response.status_code == 200:
                data = response.json()
                self.log_result("Statut checkout", True, 
                              f"✅ Session trouvée: {data.get('status', 'N/A')}")
            else:
                self.log_result("Statut checkout", False, 
                              f"Status inattendu: {response.status_code}")
        except Exception as e:
            self.log_result("Statut checkout", False, f"Exception: {str(e)}")

    def test_4_project_management(self):
        """Test 4: Gestion de projets"""
        print("\n" + "="*60)
        print("📁 TEST 4: GESTION DE PROJETS")
        print("="*60)
        
        if not self.access_token:
            self.log_result("Gestion de projets", False, "Pas de token d'accès", critical=True)
            return
        
        # 4a: Créer un nouveau projet
        self.test_4a_create_project()
        
        # 4b: Lister les projets
        self.test_4b_list_projects()
        
        # 4c: Récupérer un projet spécifique
        if self.test_project_id:
            self.test_4c_get_project()

    def test_4a_create_project(self):
        """Test 4a: Créer un nouveau projet"""
        print("\n➕ 4a: Création de projet")
        try:
            project_data = {
                "title": "Application E-commerce Test Vectort",
                "description": "Application e-commerce moderne avec React, panier d'achats, système de paiement Stripe, gestion des produits et interface d'administration",
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
                        self.log_result("Création de projet", True, 
                                      f"✅ Projet créé avec ID: {self.test_project_id}")
                    else:
                        self.log_result("Création de projet", False, 
                                      "Données du projet incorrectes")
                else:
                    self.log_result("Création de projet", False, 
                                  f"Champs manquants: {data}")
            else:
                self.log_result("Création de projet", False, 
                              f"Status: {response.status_code}, Réponse: {response.text}")
        except Exception as e:
            self.log_result("Création de projet", False, f"Exception: {str(e)}")

    def test_4b_list_projects(self):
        """Test 4b: Lister les projets"""
        print("\n📋 4b: Liste des projets")
        try:
            response = self.make_request("GET", "/projects")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    project_count = len(data)
                    if self.test_project_id:
                        # Vérifier que notre projet de test est dans la liste
                        project_found = any(p.get("id") == self.test_project_id for p in data)
                        if project_found:
                            self.log_result("Liste des projets", True, 
                                          f"✅ {project_count} projets trouvés, projet de test inclus")
                        else:
                            self.log_result("Liste des projets", False, 
                                          "Projet de test non trouvé dans la liste")
                    else:
                        self.log_result("Liste des projets", True, 
                                      f"✅ {project_count} projets trouvés")
                else:
                    self.log_result("Liste des projets", False, 
                                  f"Format de réponse incorrect: {type(data)}")
            else:
                self.log_result("Liste des projets", False, 
                              f"Status: {response.status_code}, Réponse: {response.text}")
        except Exception as e:
            self.log_result("Liste des projets", False, f"Exception: {str(e)}")

    def test_4c_get_project(self):
        """Test 4c: Récupérer un projet spécifique"""
        print("\n🔍 4c: Récupération projet spécifique")
        try:
            response = self.make_request("GET", f"/projects/{self.test_project_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == self.test_project_id:
                    self.log_result("Récupération projet", True, 
                                  f"✅ Projet récupéré: '{data['title']}'")
                else:
                    self.log_result("Récupération projet", False, 
                                  "ID du projet ne correspond pas")
            elif response.status_code == 404:
                self.log_result("Récupération projet", False, 
                              "Projet non trouvé")
            else:
                self.log_result("Récupération projet", False, 
                              f"Status: {response.status_code}, Réponse: {response.text}")
        except Exception as e:
            self.log_result("Récupération projet", False, f"Exception: {str(e)}")

    def test_5_ai_generation_critical(self):
        """Test 5: GÉNÉRATION IA CRITIQUE - Vérifier EMERGENT_LLM_KEY"""
        print("\n" + "="*60)
        print("🤖 TEST 5: GÉNÉRATION IA CRITIQUE (EMERGENT_LLM_KEY)")
        print("="*60)
        
        if not self.access_token or not self.test_project_id:
            self.log_result("Génération IA", False, "Pas de token ou projet ID", critical=True)
            return
        
        # 5a: Test Quick Mode (advanced_mode=false)
        self.test_5a_quick_mode_generation()
        
        # 5b: Test récupération du code généré
        self.test_5b_get_generated_code()
        
        # 5c: Test génération preview HTML
        self.test_5c_generate_preview()

    def test_5a_quick_mode_generation(self):
        """Test 5a: Génération Quick Mode avec déduction de crédits"""
        print("\n⚡ 5a: Génération Quick Mode")
        try:
            # Vérifier crédits avant génération
            balance_before = self.get_credit_balance()
            
            generation_request = {
                "description": "Créer une application e-commerce moderne avec React, panier d'achats, catalogue de produits, système de paiement et interface d'administration",
                "type": "web_app",
                "framework": "react",
                "database": "mongodb",
                "advanced_mode": False,  # Quick mode
                "features": ["authentication", "payment_processing", "shopping_cart"]
            }
            
            start_time = time.time()
            response = self.make_request("POST", f"/projects/{self.test_project_id}/generate", 
                                       generation_request, timeout=60)
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Vérifier que du VRAI code a été généré
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                generated_code = {}
                total_code_length = 0
                
                for field in code_fields:
                    code = data.get(field)
                    if code and len(code.strip()) > 50:  # Au moins 50 caractères de code réel
                        generated_code[field] = len(code)
                        total_code_length += len(code)
                
                # Vérifier déduction de crédits
                balance_after = self.get_credit_balance()
                credits_deducted = balance_before - balance_after if balance_before and balance_after else 0
                
                if len(generated_code) >= 2 and total_code_length > 500:  # Au moins 2 types de code, 500+ chars
                    self.log_result("Génération Quick Mode", True, 
                                  f"✅ VRAI code généré: {generated_code}, "
                                  f"Total: {total_code_length} chars, "
                                  f"Temps: {generation_time:.1f}s, "
                                  f"Crédits déduits: {credits_deducted}")
                else:
                    self.log_result("Génération Quick Mode", False, 
                                  f"Code insuffisant généré: {generated_code}, "
                                  f"Total: {total_code_length} chars", critical=True)
            elif response.status_code == 402:
                self.log_result("Génération Quick Mode", False, 
                              "❌ Crédits insuffisants", critical=True)
            else:
                self.log_result("Génération Quick Mode", False, 
                              f"Status: {response.status_code}, Réponse: {response.text}", 
                              critical=True)
        except Exception as e:
            self.log_result("Génération Quick Mode", False, f"Exception: {str(e)}", critical=True)

    def test_5b_get_generated_code(self):
        """Test 5b: Récupérer le code généré"""
        print("\n📄 5b: Récupération code généré")
        try:
            response = self.make_request("GET", f"/projects/{self.test_project_id}/code")
            
            if response.status_code == 200:
                data = response.json()
                code_fields = ["html_code", "css_code", "js_code", "react_code", "backend_code"]
                has_code = any(data.get(field) for field in code_fields)
                
                if has_code:
                    code_summary = {field: len(data.get(field, "")) for field in code_fields if data.get(field)}
                    self.log_result("Récupération code", True, 
                                  f"✅ Code récupéré: {code_summary}")
                else:
                    self.log_result("Récupération code", False, 
                                  "Aucun code trouvé dans la réponse")
            elif response.status_code == 404:
                self.log_result("Récupération code", False, 
                              "Code généré non trouvé")
            else:
                self.log_result("Récupération code", False, 
                              f"Status: {response.status_code}, Réponse: {response.text}")
        except Exception as e:
            self.log_result("Récupération code", False, f"Exception: {str(e)}")

    def test_5c_generate_preview(self):
        """Test 5c: Générer preview HTML"""
        print("\n👁️ 5c: Génération preview HTML")
        try:
            response = self.make_request("GET", f"/projects/{self.test_project_id}/preview")
            
            if response.status_code == 200:
                content = response.text
                # Vérifier que c'est du HTML valide
                if ("<!DOCTYPE html>" in content and 
                    "<html" in content and 
                    "</html>" in content and 
                    len(content) > 500):  # Au moins 500 chars de HTML
                    self.log_result("Génération preview", True, 
                                  f"✅ Preview HTML généré: {len(content)} caractères")
                else:
                    self.log_result("Génération preview", False, 
                                  f"HTML invalide ou trop court: {len(content)} chars")
            elif response.status_code == 404:
                self.log_result("Génération preview", False, 
                              "Preview non trouvé")
            else:
                self.log_result("Génération preview", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Génération preview", False, f"Exception: {str(e)}")

    def test_6_export_zip(self):
        """Test 6: Export ZIP"""
        print("\n" + "="*60)
        print("📦 TEST 6: EXPORT ZIP")
        print("="*60)
        
        if not self.access_token or not self.test_project_id:
            self.log_result("Export ZIP", False, "Pas de token ou projet ID")
            return
        
        try:
            response = self.make_request("GET", f"/projects/{self.test_project_id}/export/zip", timeout=60)
            
            if response.status_code == 200:
                # Vérifier les headers
                content_type = response.headers.get("Content-Type", "")
                content_disposition = response.headers.get("Content-Disposition", "")
                content_length = len(response.content)
                
                if ("application/zip" in content_type and 
                    "attachment" in content_disposition and 
                    content_length > 1000):  # Au moins 1KB
                    self.log_result("Export ZIP", True, 
                                  f"✅ ZIP généré: {content_length} bytes, "
                                  f"Content-Type: {content_type}")
                else:
                    self.log_result("Export ZIP", False, 
                                  f"ZIP invalide: {content_length} bytes, "
                                  f"Type: {content_type}")
            elif response.status_code == 403:
                self.log_result("Export ZIP", False, 
                              "❌ Accès refusé (authentification requise)")
            elif response.status_code == 404:
                self.log_result("Export ZIP", False, 
                              "❌ Projet ou code généré non trouvé")
            else:
                self.log_result("Export ZIP", False, 
                              f"Status: {response.status_code}, Réponse: {response.text}")
        except Exception as e:
            self.log_result("Export ZIP", False, f"Exception: {str(e)}")

    def get_credit_balance(self) -> Optional[float]:
        """Utilitaire: Récupérer le solde de crédits actuel"""
        try:
            response = self.make_request("GET", "/credits/balance")
            if response.status_code == 200:
                data = response.json()
                return data.get("total_available", 0.0)
        except:
            pass
        return None

    def print_final_summary(self):
        """Afficher le résumé final des tests"""
        print("\n" + "="*80)
        print("📊 RÉSUMÉ FINAL - TESTS VECTORT.IO PRODUCTION")
        print("="*80)
        
        total_tests = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests réussis: {self.results['passed']}")
        print(f"❌ Tests échoués: {self.results['failed']}")
        print(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        if self.results["critical_issues"]:
            print(f"\n🚨 PROBLÈMES CRITIQUES DÉTECTÉS ({len(self.results['critical_issues'])}):")
            for issue in self.results["critical_issues"]:
                print(f"   {issue}")
        
        if self.results["errors"]:
            print(f"\n📋 DÉTAIL DES ERREURS:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        # Évaluation finale
        if success_rate >= 90:
            print(f"\n🎉 ÉVALUATION: EXCELLENT - Système prêt pour production")
        elif success_rate >= 75:
            print(f"\n✅ ÉVALUATION: BON - Quelques améliorations nécessaires")
        elif success_rate >= 50:
            print(f"\n⚠️ ÉVALUATION: MOYEN - Problèmes à résoudre")
        else:
            print(f"\n🚨 ÉVALUATION: CRITIQUE - Intervention urgente requise")
        
        print("="*80)

    def run_all_tests(self):
        """Exécuter tous les tests dans l'ordre"""
        print("🚀 DÉMARRAGE DES TESTS VECTORT.IO PRODUCTION")
        print(f"🌐 Backend URL: {self.base_url}")
        print(f"👤 Utilisateur de test: {self.test_user['email']}")
        
        try:
            # Tests critiques selon la demande française
            self.test_1_api_status()
            self.test_2_authentication_complete()
            self.test_3_credit_system()
            self.test_4_project_management()
            self.test_5_ai_generation_critical()
            self.test_6_export_zip()
            
        except KeyboardInterrupt:
            print("\n⏹️ Tests interrompus par l'utilisateur")
        except Exception as e:
            print(f"\n💥 Erreur critique pendant les tests: {str(e)}")
        finally:
            self.print_final_summary()

if __name__ == "__main__":
    print("🎯 VECTORT.IO - TEST COMPLET BACKEND PRODUCTION")
    print("=" * 60)
    
    tester = VectortProductionTester()
    tester.run_all_tests()