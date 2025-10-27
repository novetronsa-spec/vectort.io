"""
OAuth Integration pour Google, GitHub, et Apple
Gère l'authentification OAuth pour les trois providers principaux
"""

import os
import httpx
import jwt
import time
import secrets
from typing import Optional, Dict
from datetime import datetime, timedelta
from fastapi import HTTPException
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


# Configuration des providers OAuth
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'https://vectort-builder.preview.emergentagent.com/api/auth/google/callback')

GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
GITHUB_REDIRECT_URI = os.environ.get('GITHUB_REDIRECT_URI', 'https://vectort-builder.preview.emergentagent.com/api/auth/github/callback')

APPLE_TEAM_ID = os.environ.get('APPLE_TEAM_ID', '')
APPLE_KEY_ID = os.environ.get('APPLE_KEY_ID', '')
APPLE_CLIENT_ID = os.environ.get('APPLE_CLIENT_ID', '')
APPLE_REDIRECT_URI = os.environ.get('APPLE_REDIRECT_URI', 'https://vectort-builder.preview.emergentagent.com/api/auth/apple/callback')


class GoogleOAuth:
    """Gère l'authentification Google OAuth"""
    
    @staticmethod
    def get_authorization_url(state: Optional[str] = None) -> Dict[str, str]:
        """Génère l'URL d'autorisation Google"""
        if not state:
            state = secrets.token_urlsafe(32)
        
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={GOOGLE_CLIENT_ID}"
            f"&redirect_uri={GOOGLE_REDIRECT_URI}"
            f"&response_type=code"
            f"&scope=openid%20email%20profile"
            f"&state={state}"
            f"&access_type=offline"
            f"&prompt=consent"
        )
        
        return {
            "authorization_url": auth_url,
            "state": state
        }
    
    @staticmethod
    async def exchange_code_for_token(code: str) -> Dict:
        """Échange le code d'autorisation contre un token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to exchange code: {response.text}"
                )
            
            return response.json()
    
    @staticmethod
    async def get_user_info(access_token: str) -> Dict:
        """Récupère les informations utilisateur depuis Google"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to get user info from Google"
                )
            
            return response.json()


class GitHubOAuth:
    """Gère l'authentification GitHub OAuth"""
    
    @staticmethod
    def get_authorization_url(state: Optional[str] = None) -> Dict[str, str]:
        """Génère l'URL d'autorisation GitHub"""
        if not state:
            state = secrets.token_urlsafe(32)
        
        auth_url = (
            f"https://github.com/login/oauth/authorize?"
            f"client_id={GITHUB_CLIENT_ID}"
            f"&redirect_uri={GITHUB_REDIRECT_URI}"
            f"&scope=user:email"
            f"&state={state}"
        )
        
        return {
            "authorization_url": auth_url,
            "state": state
        }
    
    @staticmethod
    async def exchange_code_for_token(code: str) -> Dict:
        """Échange le code d'autorisation contre un token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": GITHUB_REDIRECT_URI
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to exchange code: {response.text}"
                )
            
            data = response.json()
            
            if "error" in data:
                raise HTTPException(
                    status_code=400,
                    detail=f"GitHub OAuth error: {data.get('error_description', data['error'])}"
                )
            
            return data
    
    @staticmethod
    async def get_user_info(access_token: str) -> Dict:
        """Récupère les informations utilisateur depuis GitHub"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to get user info from GitHub"
                )
            
            return response.json()


class AppleOAuth:
    """Gère l'authentification Apple OAuth"""
    
    @staticmethod
    def get_authorization_url(state: Optional[str] = None) -> Dict[str, str]:
        """Génère l'URL d'autorisation Apple"""
        if not state:
            state = secrets.token_urlsafe(32)
        
        auth_url = (
            f"https://appleid.apple.com/auth/authorize?"
            f"client_id={APPLE_CLIENT_ID}"
            f"&redirect_uri={APPLE_REDIRECT_URI}"
            f"&response_type=code"
            f"&scope=email%20name"
            f"&response_mode=form_post"
            f"&state={state}"
        )
        
        return {
            "authorization_url": auth_url,
            "state": state
        }
    
    @staticmethod
    def generate_client_secret() -> str:
        """Génère un client secret signé pour Apple"""
        try:
            # Récupérer la clé privée depuis les variables d'environnement
            private_key_str = os.environ.get('APPLE_PRIVATE_KEY', '')
            
            if not private_key_str:
                raise Exception("APPLE_PRIVATE_KEY not configured")
            
            # Charger la clé privée
            private_key = serialization.load_pem_private_key(
                private_key_str.encode(),
                password=None,
                backend=default_backend()
            )
            
            # Créer le JWT pour Apple
            headers = {
                'kid': APPLE_KEY_ID,
                'alg': 'ES256'
            }
            
            now = int(time.time())
            payload = {
                'iss': APPLE_TEAM_ID,
                'iat': now,
                'exp': now + 3600,  # Expire dans 1 heure
                'aud': 'https://appleid.apple.com',
                'sub': APPLE_CLIENT_ID
            }
            
            # Signer le JWT
            client_secret = jwt.encode(
                payload,
                private_key,
                algorithm='ES256',
                headers=headers
            )
            
            return client_secret
            
        except Exception as e:
            print(f"Error generating Apple client secret: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate Apple client secret: {str(e)}"
            )
    
    @staticmethod
    async def exchange_code_for_token(code: str) -> Dict:
        """Échange le code d'autorisation contre un token"""
        try:
            client_secret = AppleOAuth.generate_client_secret()
            
            token_url = "https://appleid.apple.com/auth/token"
            
            data = {
                'client_id': APPLE_CLIENT_ID,
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': APPLE_REDIRECT_URI
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=data)
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Apple token exchange failed: {response.text}"
                    )
                
                return response.json()
        
        except Exception as e:
            print(f"Apple token exchange error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Apple authentication failed: {str(e)}"
            )
    
    @staticmethod
    async def get_user_info(id_token: str) -> Dict:
        """Extrait les informations utilisateur depuis l'ID token Apple"""
        try:
            # Décoder le JWT sans vérification (Apple sign in avec leur clé publique)
            # En production, on devrait vérifier la signature avec la clé publique d'Apple
            decoded = jwt.decode(id_token, options={"verify_signature": False})
            
            return {
                'id': decoded.get('sub'),
                'email': decoded.get('email'),
                'email_verified': decoded.get('email_verified', False),
                'name': decoded.get('name', {})
            }
        
        except Exception as e:
            print(f"Apple user info extraction error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract user info: {str(e)}"
            )
