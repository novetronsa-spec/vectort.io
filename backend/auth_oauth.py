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
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'https://omniai-platform-2.preview.emergentagent.com/api/auth/google/callback')

GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
GITHUB_REDIRECT_URI = os.environ.get('GITHUB_REDIRECT_URI', 'https://omniai-platform-2.preview.emergentagent.com/api/auth/github/callback')

APPLE_TEAM_ID = os.environ.get('APPLE_TEAM_ID', '')
APPLE_KEY_ID = os.environ.get('APPLE_KEY_ID', '')
APPLE_CLIENT_ID = os.environ.get('APPLE_CLIENT_ID', '')
APPLE_REDIRECT_URI = os.environ.get('APPLE_REDIRECT_URI', 'https://omniai-platform-2.preview.emergentagent.com/api/auth/apple/callback')


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
        # Note: Pour simplifier, on skip l'implémentation complète Apple
        # car elle nécessite une clé privée .p8 qui n'est pas configurée
        # Dans un environnement de production, implémenter la signature JWT
        return "apple_client_secret_placeholder"
    
    @staticmethod
    async def exchange_code_for_token(code: str) -> Dict:
        """Échange le code d'autorisation contre un token"""
        # Note: Implémentation simplifiée pour Apple
        # En production, implémenter la logique complète avec client_secret signé
        raise HTTPException(
            status_code=501,
            detail="Apple OAuth not fully implemented - requires private key configuration"
        )
    
    @staticmethod
    async def get_user_info(id_token: str) -> Dict:
        """Extrait les informations utilisateur depuis l'ID token Apple"""
        # Note: Implémentation simplifiée
        # En production, vérifier et décoder le JWT id_token
        raise HTTPException(
            status_code=501,
            detail="Apple OAuth user info not fully implemented"
        )
