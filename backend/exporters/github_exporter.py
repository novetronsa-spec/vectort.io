"""
VECTORT.IO - GITHUB EXPORTER  
Gère l'export de code généré vers GitHub (version httpx)
"""

import httpx
import base64
from typing import Dict, Optional, List
import json
import asyncio


class GitHubExporter:
    """Gère l'export de projets vers GitHub"""
    
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def create_repository(
        self,
        repo_name: str,
        description: str,
        private: bool = False
    ) -> Dict:
        """Crée un nouveau repository GitHub"""
        url = f"{self.base_url}/user/repos"
        
        payload = {
            "name": repo_name,
            "description": description,
            "private": private,
            "auto_init": True,
            "has_issues": True,
            "has_projects": True,
            "has_wiki": False
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=self.headers)
            
            if response.status_code == 201:
                return response.json()
            elif response.status_code == 422:
                error_data = response.json()
                raise ValueError(f"Repository existe déjà ou nom invalide: {error_data}")
            else:
                raise Exception(f"Erreur création repository: {response.status_code} - {response.text}")
    
    async def push_files_to_repo(
        self,
        owner: str,
        repo_name: str,
        files: Dict[str, str],
        branch: str = "main",
        commit_message: str = "Initial commit from Vectort.io"
    ) -> Dict:
        """Push des fichiers vers un repository GitHub"""
        results = {
            "success": [],
            "failed": [],
            "total": len(files)
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for file_path, content in files.items():
                try:
                    # Encoder le contenu en base64
                    content_bytes = content.encode('utf-8')
                    content_base64 = base64.b64encode(content_bytes).decode('utf-8')
                    
                    # URL de l'API
                    url = f"{self.base_url}/repos/{owner}/{repo_name}/contents/{file_path}"
                    
                    # Vérifier si le fichier existe
                    sha = await self._get_file_sha(client, owner, repo_name, file_path)
                    
                    payload = {
                        "message": commit_message,
                        "content": content_base64,
                        "branch": branch
                    }
                    
                    if sha:
                        payload["sha"] = sha
                    
                    response = await client.put(url, json=payload, headers=self.headers)
                    
                    if response.status_code in [200, 201]:
                        results["success"].append(file_path)
                    else:
                        results["failed"].append({
                            "file": file_path,
                            "error": f"{response.status_code} - {response.text}"
                        })
                
                except Exception as e:
                    results["failed"].append({
                        "file": file_path,
                        "error": str(e)
                    })
        
        return results
    
    async def _get_file_sha(
        self,
        client: httpx.AsyncClient,
        owner: str,
        repo_name: str,
        file_path: str
    ) -> Optional[str]:
        """Récupère le SHA d'un fichier existant"""
        url = f"{self.base_url}/repos/{owner}/{repo_name}/contents/{file_path}"
        
        try:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("sha")
        except:
            pass
        
        return None
    
    async def get_user_info(self) -> Dict:
        """Récupère les informations de l'utilisateur GitHub"""
        url = f"{self.base_url}/user"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Erreur récupération utilisateur: {response.status_code}")
    
    async def create_and_push_project(
        self,
        project_title: str,
        description: str,
        generated_code: Dict[str, str],
        private: bool = False
    ) -> Dict:
        """Fonction complète : crée un repo et push le code"""
        repo_name = self._sanitize_repo_name(project_title)
        
        try:
            # 1. Créer le repository
            repo_info = await self.create_repository(
                repo_name=repo_name,
                description=description,
                private=private
            )
            
            owner = repo_info["owner"]["login"]
            repo_url = repo_info["html_url"]
            
            # 2. Préparer les fichiers
            files_to_push = self._prepare_files_for_github(generated_code)
            
            # 3. Push les fichiers
            push_results = await self.push_files_to_repo(
                owner=owner,
                repo_name=repo_name,
                files=files_to_push,
                commit_message=f"🚀 Initial commit - Generated by Vectort.io"
            )
            
            return {
                "success": True,
                "repo_url": repo_url,
                "repo_name": repo_name,
                "owner": owner,
                "clone_url": repo_info["clone_url"],
                "files_pushed": push_results["success"],
                "files_failed": push_results["failed"],
                "total_files": push_results["total"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _sanitize_repo_name(self, title: str) -> str:
        """Nettoie le nom pour GitHub"""
        clean_name = title.lower()
        clean_name = clean_name.replace(' ', '-')
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c in ['-', '_'])
        return clean_name or "vectort-project"
    
    def _prepare_files_for_github(self, generated_code: Dict[str, str]) -> Dict[str, str]:
        """Prépare les fichiers pour GitHub"""
        files = {}
        
        # Mapping du code
        code_mapping = {
            'html_code': 'public/index.html',
            'css_code': 'src/styles/App.css',
            'js_code': 'src/utils/helpers.js',
            'react_code': 'src/App.jsx',
            'backend_code': 'server.js',
        }
        
        for code_key, file_path in code_mapping.items():
            code_content = generated_code.get(code_key, '')
            if code_content and code_content.strip():
                files[file_path] = code_content
        
        # Fichiers de config
        if generated_code.get('package_json'):
            files['package.json'] = generated_code['package_json']
        
        if generated_code.get('requirements_txt'):
            files['requirements.txt'] = generated_code['requirements_txt']
        
        if generated_code.get('dockerfile'):
            files['Dockerfile'] = generated_code['dockerfile']
        
        # README
        if 'README.md' not in files:
            files['README.md'] = """# Application Vectort.io

> Généré automatiquement par Vectort.io

## 🚀 Installation

```bash
npm install
```

## 💻 Développement

```bash
npm start
```

---
*Généré avec ❤️ par Vectort.io*
"""
        
        return files
