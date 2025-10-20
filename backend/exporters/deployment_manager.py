"""
VECTORT.IO - DEPLOYMENT MANAGER
Gère le déploiement one-click vers Vercel, Netlify, etc.
"""

import httpx
from typing import Dict, Optional
import json


class VercelDeployer:
    """Gère le déploiement vers Vercel"""
    
    def __init__(self, vercel_token: str):
        self.vercel_token = vercel_token
        self.base_url = "https://api.vercel.com"
        self.headers = {
            "Authorization": f"Bearer {vercel_token}",
            "Content-Type": "application/json"
        }
    
    async def deploy_from_github(
        self,
        github_repo_url: str,
        project_name: str,
        environment_vars: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Déploie un projet depuis GitHub vers Vercel
        
        Args:
            github_repo_url: URL du repo GitHub (https://github.com/user/repo)
            project_name: Nom du projet Vercel
            environment_vars: Variables d'environnement
            
        Returns:
            Dict avec les infos du déploiement
        """
        url = f"{self.base_url}/v13/deployments"
        
        # Extraire owner et repo depuis l'URL
        parts = github_repo_url.replace("https://github.com/", "").split("/")
        owner = parts[0]
        repo = parts[1]
        
        payload = {
            "name": project_name,
            "gitSource": {
                "type": "github",
                "repo": f"{owner}/{repo}",
                "ref": "main"
            },
            "projectSettings": {
                "framework": "react"
            }
        }
        
        if environment_vars:
            payload["env"] = [
                {"key": k, "value": v, "type": "plain"}
                for k, v in environment_vars.items()
            ]
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=self.headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "success": True,
                    "deployment_url": f"https://{data.get('url')}",
                    "deployment_id": data.get('id'),
                    "status": data.get('readyState')
                }
            else:
                return {
                    "success": False,
                    "error": f"{response.status_code} - {response.text}"
                }
    
    async def get_deployment_status(self, deployment_id: str) -> Dict:
        """Récupère le statut d'un déploiement"""
        url = f"{self.base_url}/v13/deployments/{deployment_id}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "status": data.get('readyState'),
                    "url": f"https://{data.get('url')}"
                }
            else:
                return {
                    "success": False,
                    "error": response.text
                }


class NetlifyDeployer:
    """Gère le déploiement vers Netlify"""
    
    def __init__(self, netlify_token: str):
        self.netlify_token = netlify_token
        self.base_url = "https://api.netlify.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {netlify_token}",
            "Content-Type": "application/json"
        }
    
    async def deploy_from_github(
        self,
        github_repo_url: str,
        project_name: str,
        build_command: str = "npm run build",
        publish_directory: str = "build"
    ) -> Dict:
        """
        Déploie un projet depuis GitHub vers Netlify
        
        Args:
            github_repo_url: URL du repo GitHub
            project_name: Nom du site Netlify
            build_command: Commande de build
            publish_directory: Dossier de publication
            
        Returns:
            Dict avec les infos du déploiement
        """
        url = f"{self.base_url}/sites"
        
        payload = {
            "name": project_name,
            "repo": {
                "provider": "github",
                "repo": github_repo_url.replace("https://github.com/", ""),
                "branch": "main"
            },
            "build_settings": {
                "cmd": build_command,
                "dir": publish_directory
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=self.headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "success": True,
                    "site_url": data.get('ssl_url') or data.get('url'),
                    "site_id": data.get('id'),
                    "admin_url": data.get('admin_url')
                }
            else:
                return {
                    "success": False,
                    "error": f"{response.status_code} - {response.text}"
                }
    
    async def get_site_info(self, site_id: str) -> Dict:
        """Récupère les informations d'un site"""
        url = f"{self.base_url}/sites/{site_id}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "url": data.get('ssl_url') or data.get('url'),
                    "status": data.get('state'),
                    "published_deploy": data.get('published_deploy')
                }
            else:
                return {
                    "success": False,
                    "error": response.text
                }


class DeploymentManager:
    """Gestionnaire unifié des déploiements"""
    
    @staticmethod
    def generate_vercel_button_url(github_repo_url: str) -> str:
        """
        Génère l'URL du bouton "Deploy to Vercel"
        
        Returns:
            URL complète du bouton Vercel
        """
        return f"https://vercel.com/new/clone?repository-url={github_repo_url}"
    
    @staticmethod
    def generate_netlify_button_url(github_repo_url: str) -> str:
        """
        Génère l'URL du bouton "Deploy to Netlify"
        
        Returns:
            URL complète du bouton Netlify
        """
        return f"https://app.netlify.com/start/deploy?repository={github_repo_url}"
    
    @staticmethod
    def generate_railway_button_url(github_repo_url: str) -> str:
        """
        Génère l'URL du bouton "Deploy on Railway"
        
        Returns:
            URL complète du bouton Railway
        """
        return f"https://railway.app/new/template?template={github_repo_url}"
    
    @staticmethod
    def generate_render_button_url(github_repo_url: str) -> str:
        """
        Génère l'URL du bouton "Deploy to Render"
        
        Returns:
            URL complète du bouton Render
        """
        return f"https://render.com/deploy?repo={github_repo_url}"
