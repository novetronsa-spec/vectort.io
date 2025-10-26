"""
Multi-Platform Deployment Services
Supports: Vercel, Netlify, Render
"""

import os
import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)

class DeploymentPlatform(str, Enum):
    VERCEL = "vercel"
    NETLIFY = "netlify"
    RENDER = "render"

class DeploymentStatus(str, Enum):
    PENDING = "pending"
    BUILDING = "building"
    READY = "ready"
    ERROR = "error"
    CANCELED = "canceled"

class DeploymentResult:
    """Standard deployment result across all platforms"""
    
    def __init__(
        self,
        success: bool,
        platform: str,
        deployment_url: Optional[str] = None,
        deployment_id: Optional[str] = None,
        status: str = DeploymentStatus.PENDING,
        message: Optional[str] = None,
        error: Optional[str] = None,
        logs_url: Optional[str] = None
    ):
        self.success = success
        self.platform = platform
        self.deployment_url = deployment_url
        self.deployment_id = deployment_id
        self.status = status
        self.message = message
        self.error = error
        self.logs_url = logs_url
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "platform": self.platform,
            "deployment_url": self.deployment_url,
            "deployment_id": self.deployment_id,
            "status": self.status,
            "message": self.message,
            "error": self.error,
            "logs_url": self.logs_url
        }

class VercelDeployment:
    """Vercel deployment service"""
    
    def __init__(self):
        self.token = os.environ.get('VERCEL_TOKEN')
        self.api_base = "https://api.vercel.com"
        
    async def deploy_from_github(
        self,
        github_repo_url: str,
        project_name: str,
        env_vars: Optional[Dict[str, str]] = None,
        framework: Optional[str] = None
    ) -> DeploymentResult:
        """
        Deploy a project from GitHub to Vercel
        
        Args:
            github_repo_url: Full GitHub repo URL (e.g., https://github.com/user/repo)
            project_name: Name for the Vercel project
            env_vars: Environment variables for the deployment
            framework: Framework preset (nextjs, react, vue, etc.)
        """
        
        if not self.token:
            return DeploymentResult(
                success=False,
                platform=DeploymentPlatform.VERCEL,
                error="VERCEL_TOKEN not configured"
            )
        
        try:
            # Parse GitHub URL
            github_url_parts = github_repo_url.replace("https://github.com/", "").split("/")
            if len(github_url_parts) < 2:
                raise ValueError("Invalid GitHub URL format")
            
            owner, repo = github_url_parts[0], github_url_parts[1].replace(".git", "")
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            # Create deployment payload
            payload = {
                "name": project_name,
                "gitSource": {
                    "type": "github",
                    "repo": f"{owner}/{repo}",
                    "ref": "main"  # Default branch
                }
            }
            
            # Add environment variables if provided
            if env_vars:
                payload["env"] = env_vars
            
            # Add framework if specified
            if framework:
                payload["framework"] = framework
            
            async with aiohttp.ClientSession() as session:
                # Create deployment
                async with session.post(
                    f"{self.api_base}/v13/deployments",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        deployment_url = f"https://{data.get('url', '')}"
                        deployment_id = data.get('id', '')
                        
                        logger.info(f"✅ Vercel deployment created: {deployment_url}")
                        
                        return DeploymentResult(
                            success=True,
                            platform=DeploymentPlatform.VERCEL,
                            deployment_url=deployment_url,
                            deployment_id=deployment_id,
                            status=DeploymentStatus.BUILDING,
                            message="Deployment initiated successfully"
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"Vercel deployment failed: {error_text}")
                        
                        return DeploymentResult(
                            success=False,
                            platform=DeploymentPlatform.VERCEL,
                            error=f"Deployment failed with status {response.status}: {error_text}"
                        )
        
        except Exception as e:
            logger.exception(f"Vercel deployment error: {str(e)}")
            return DeploymentResult(
                success=False,
                platform=DeploymentPlatform.VERCEL,
                error=str(e)
            )
    
    async def get_deployment_status(self, deployment_id: str) -> DeploymentResult:
        """Check deployment status"""
        
        if not self.token:
            return DeploymentResult(
                success=False,
                platform=DeploymentPlatform.VERCEL,
                error="VERCEL_TOKEN not configured"
            )
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/v13/deployments/{deployment_id}",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Map Vercel status to our status
                        vercel_state = data.get('readyState', 'BUILDING')
                        status_map = {
                            'READY': DeploymentStatus.READY,
                            'BUILDING': DeploymentStatus.BUILDING,
                            'ERROR': DeploymentStatus.ERROR,
                            'CANCELED': DeploymentStatus.CANCELED
                        }
                        
                        return DeploymentResult(
                            success=True,
                            platform=DeploymentPlatform.VERCEL,
                            deployment_url=f"https://{data.get('url', '')}",
                            deployment_id=deployment_id,
                            status=status_map.get(vercel_state, DeploymentStatus.BUILDING)
                        )
                    else:
                        error_text = await response.text()
                        return DeploymentResult(
                            success=False,
                            platform=DeploymentPlatform.VERCEL,
                            error=error_text
                        )
        
        except Exception as e:
            return DeploymentResult(
                success=False,
                platform=DeploymentPlatform.VERCEL,
                error=str(e)
            )

class NetlifyDeployment:
    """Netlify deployment service"""
    
    def __init__(self):
        self.token = os.environ.get('NETLIFY_TOKEN')
        self.api_base = "https://api.netlify.com/api/v1"
    
    async def deploy_from_github(
        self,
        github_repo_url: str,
        project_name: str,
        build_command: Optional[str] = None,
        publish_dir: Optional[str] = None,
        env_vars: Optional[Dict[str, str]] = None
    ) -> DeploymentResult:
        """
        Deploy a project from GitHub to Netlify
        """
        
        if not self.token:
            return DeploymentResult(
                success=False,
                platform=DeploymentPlatform.NETLIFY,
                error="NETLIFY_TOKEN not configured"
            )
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            # Parse GitHub URL
            github_url_parts = github_repo_url.replace("https://github.com/", "").split("/")
            if len(github_url_parts) < 2:
                raise ValueError("Invalid GitHub URL format")
            
            owner, repo = github_url_parts[0], github_url_parts[1].replace(".git", "")
            
            # Create site payload
            payload = {
                "name": project_name,
                "repo": {
                    "repo": f"{owner}/{repo}",
                    "branch": "main",
                    "provider": "github",
                    "repo_url": github_repo_url
                }
            }
            
            # Add build settings
            if build_command or publish_dir:
                payload["build_settings"] = {}
                if build_command:
                    payload["build_settings"]["cmd"] = build_command
                if publish_dir:
                    payload["build_settings"]["dir"] = publish_dir
            
            async with aiohttp.ClientSession() as session:
                # Create site
                async with session.post(
                    f"{self.api_base}/sites",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status in [200, 201]:
                        data = await response.json()
                        
                        site_id = data.get('id', '')
                        site_url = data.get('ssl_url') or data.get('url', '')
                        
                        # Set environment variables if provided
                        if env_vars and site_id:
                            await self._set_env_vars(site_id, env_vars, headers)
                        
                        logger.info(f"✅ Netlify site created: {site_url}")
                        
                        return DeploymentResult(
                            success=True,
                            platform=DeploymentPlatform.NETLIFY,
                            deployment_url=site_url,
                            deployment_id=site_id,
                            status=DeploymentStatus.BUILDING,
                            message="Site created successfully, deployment in progress"
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"Netlify deployment failed: {error_text}")
                        
                        return DeploymentResult(
                            success=False,
                            platform=DeploymentPlatform.NETLIFY,
                            error=f"Deployment failed with status {response.status}: {error_text}"
                        )
        
        except Exception as e:
            logger.exception(f"Netlify deployment error: {str(e)}")
            return DeploymentResult(
                success=False,
                platform=DeploymentPlatform.NETLIFY,
                error=str(e)
            )
    
    async def _set_env_vars(self, site_id: str, env_vars: Dict[str, str], headers: Dict):
        """Set environment variables for a Netlify site"""
        try:
            async with aiohttp.ClientSession() as session:
                for key, value in env_vars.items():
                    payload = {
                        "key": key,
                        "values": [{"value": value, "context": "all"}]
                    }
                    
                    async with session.post(
                        f"{self.api_base}/accounts/{site_id}/env",
                        headers=headers,
                        json=payload
                    ) as response:
                        if response.status not in [200, 201]:
                            logger.warning(f"Failed to set env var {key}")
        
        except Exception as e:
            logger.warning(f"Failed to set environment variables: {str(e)}")

class RenderDeployment:
    """Render deployment service"""
    
    def __init__(self):
        self.token = os.environ.get('RENDER_API_KEY')
        self.api_base = "https://api.render.com/v1"
    
    async def deploy_from_github(
        self,
        github_repo_url: str,
        project_name: str,
        service_type: str = "web",  # web, static_site, private_service
        env_vars: Optional[Dict[str, str]] = None,
        build_command: Optional[str] = None,
        start_command: Optional[str] = None
    ) -> DeploymentResult:
        """
        Deploy a project from GitHub to Render
        """
        
        if not self.token:
            return DeploymentResult(
                success=False,
                platform=DeploymentPlatform.RENDER,
                error="RENDER_API_KEY not configured"
            )
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            # Create service payload
            payload = {
                "type": service_type,
                "name": project_name,
                "repo": github_repo_url,
                "autoDeploy": "yes",
                "branch": "main"
            }
            
            # Add build/start commands
            if build_command:
                payload["buildCommand"] = build_command
            if start_command:
                payload["startCommand"] = start_command
            
            # Add environment variables
            if env_vars:
                payload["envVars"] = [
                    {"key": k, "value": v} for k, v in env_vars.items()
                ]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/services",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status in [200, 201]:
                        data = await response.json()
                        
                        service_id = data.get('service', {}).get('id', '')
                        service_url = data.get('service', {}).get('serviceDetails', {}).get('url', '')
                        
                        logger.info(f"✅ Render service created: {service_url}")
                        
                        return DeploymentResult(
                            success=True,
                            platform=DeploymentPlatform.RENDER,
                            deployment_url=service_url,
                            deployment_id=service_id,
                            status=DeploymentStatus.BUILDING,
                            message="Service created successfully, deployment in progress"
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"Render deployment failed: {error_text}")
                        
                        return DeploymentResult(
                            success=False,
                            platform=DeploymentPlatform.RENDER,
                            error=f"Deployment failed with status {response.status}: {error_text}"
                        )
        
        except Exception as e:
            logger.exception(f"Render deployment error: {str(e)}")
            return DeploymentResult(
                success=False,
                platform=DeploymentPlatform.RENDER,
                error=str(e)
            )

# Service instances
vercel_deployment = VercelDeployment()
netlify_deployment = NetlifyDeployment()
render_deployment = RenderDeployment()
