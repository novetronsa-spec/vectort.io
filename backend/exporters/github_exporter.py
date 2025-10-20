"""
VECTORT.IO - GITHUB EXPORTER
Gère l'export de code généré vers GitHub
"""

import httpx
import base64
from typing import Dict, Optional, List
import json


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
        """
        Crée un nouveau repository GitHub
        
        Args:
            repo_name: Nom du repository
            description: Description du projet
            private: Repository privé ou public
            
        Returns:
            Dict avec les infos du repo créé
        """
        url = f"{self.base_url}/user/repos"
        
        payload = {
            "name": repo_name,
            "description": description,
            "private": private,
            "auto_init": True,  # Créer avec un README initial
            "has_issues": True,
            "has_projects": True,
            "has_wiki": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self.headers) as response:
                if response.status == 201:
                    return await response.json()
                elif response.status == 422:
                    # Repository existe déjà
                    error_data = await response.json()
                    raise ValueError(f"Repository existe déjà ou nom invalide: {error_data}")
                else:
                    error_text = await response.text()
                    raise Exception(f"Erreur création repository: {response.status} - {error_text}")
    
    async def push_files_to_repo(
        self,
        owner: str,
        repo_name: str,
        files: Dict[str, str],
        branch: str = "main",
        commit_message: str = "Initial commit from Vectort.io"
    ) -> Dict:
        """
        Push des fichiers vers un repository GitHub
        
        Args:
            owner: Propriétaire du repo (username GitHub)
            repo_name: Nom du repository
            files: Dict {chemin_fichier: contenu}
            branch: Branche cible
            commit_message: Message de commit
            
        Returns:
            Dict avec les résultats
        """
        results = {
            "success": [],
            "failed": [],
            "total": len(files)
        }
        
        async with aiohttp.ClientSession() as session:
            for file_path, content in files.items():
                try:
                    # Encoder le contenu en base64
                    content_bytes = content.encode('utf-8')
                    content_base64 = base64.b64encode(content_bytes).decode('utf-8')
                    
                    # URL de l'API pour créer/mettre à jour un fichier
                    url = f"{self.base_url}/repos/{owner}/{repo_name}/contents/{file_path}"
                    
                    # Vérifier si le fichier existe déjà
                    sha = await self._get_file_sha(session, owner, repo_name, file_path)
                    
                    payload = {
                        "message": commit_message,
                        "content": content_base64,
                        "branch": branch
                    }
                    
                    if sha:
                        payload["sha"] = sha  # Mise à jour
                    
                    async with session.put(url, json=payload, headers=self.headers) as response:
                        if response.status in [200, 201]:
                            results["success"].append(file_path)
                        else:
                            error_text = await response.text()
                            results["failed"].append({
                                "file": file_path,
                                "error": f"{response.status} - {error_text}"
                            })
                
                except Exception as e:
                    results["failed"].append({
                        "file": file_path,
                        "error": str(e)
                    })
        
        return results
    
    async def _get_file_sha(
        self,
        session: aiohttp.ClientSession,
        owner: str,
        repo_name: str,
        file_path: str
    ) -> Optional[str]:
        """Récupère le SHA d'un fichier existant (pour mise à jour)"""
        url = f"{self.base_url}/repos/{owner}/{repo_name}/contents/{file_path}"
        
        try:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("sha")
        except:
            pass
        
        return None
    
    async def get_user_info(self) -> Dict:
        """Récupère les informations de l'utilisateur GitHub authentifié"""
        url = f"{self.base_url}/user"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Erreur récupération utilisateur: {response.status}")
    
    async def fork_repository(
        self,
        owner: str,
        repo_name: str,
        organization: Optional[str] = None
    ) -> Dict:
        """
        Fork un repository existant
        
        Args:
            owner: Propriétaire du repo source
            repo_name: Nom du repo à fork
            organization: Organisation cible (optionnel)
            
        Returns:
            Dict avec les infos du fork
        """
        url = f"{self.base_url}/repos/{owner}/{repo_name}/forks"
        
        payload = {}
        if organization:
            payload["organization"] = organization
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self.headers) as response:
                if response.status == 202:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Erreur fork repository: {response.status} - {error_text}")
    
    async def create_and_push_project(
        self,
        project_title: str,
        description: str,
        generated_code: Dict[str, str],
        private: bool = False
    ) -> Dict:
        """
        Fonction complète : crée un repo et push le code
        
        Args:
            project_title: Titre du projet
            description: Description
            generated_code: Code généré
            private: Repo privé ou public
            
        Returns:
            Dict avec URL du repo et résultats
        """
        # 1. Créer le repository
        repo_name = self._sanitize_repo_name(project_title)
        
        try:
            repo_info = await self.create_repository(
                repo_name=repo_name,
                description=description,
                private=private
            )
            
            owner = repo_info["owner"]["login"]
            repo_url = repo_info["html_url"]
            
            # 2. Préparer les fichiers à pusher
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
        """Nettoie le nom pour GitHub (pas d'espaces, caractères spéciaux)"""
        clean_name = title.lower()
        clean_name = clean_name.replace(' ', '-')
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c in ['-', '_'])
        return clean_name or "vectort-project"
    
    def _prepare_files_for_github(self, generated_code: Dict[str, str]) -> Dict[str, str]:
        """Prépare les fichiers pour l'upload GitHub avec la bonne structure"""
        files = {}
        
        # Mapping du code généré vers la structure de fichiers
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
        
        # Ajouter les fichiers all_files si disponibles
        all_files = generated_code.get('all_files', {})
        if isinstance(all_files, dict):
            for file_path, content in all_files.items():
                if content and content.strip():
                    files[file_path] = content
        
        # Ajouter les fichiers de configuration
        if generated_code.get('package_json'):
            files['package.json'] = generated_code['package_json']
        
        if generated_code.get('requirements_txt'):
            files['requirements.txt'] = generated_code['requirements_txt']
        
        if generated_code.get('dockerfile'):
            files['Dockerfile'] = generated_code['dockerfile']
        
        # Ajouter un README si pas présent
        if 'README.md' not in files:
            files['README.md'] = self._generate_default_readme(generated_code)
        
        return files
    
    def _generate_default_readme(self, generated_code: Dict[str, str]) -> str:
        """Génère un README par défaut"""
        return """# Application générée par Vectort.io

> Cette application a été générée automatiquement avec Vectort.io

## 🚀 Installation

```bash
npm install
```

## 💻 Développement

```bash
npm start
```

## 🏗️ Build

```bash
npm run build
```

## 📝 Description

Application générée avec intelligence artificielle par [Vectort.io](https://vectort.io)

---

*Généré avec ❤️ par Vectort.io*
"""


class GitHubAuthManager:
    """Gère l'authentification GitHub OAuth"""
    
    @staticmethod
    def get_oauth_url(client_id: str, redirect_uri: str, scopes: List[str] = None) -> str:
        """
        Génère l'URL d'authentification GitHub OAuth
        
        Args:
            client_id: GitHub OAuth App Client ID
            redirect_uri: URL de redirection après auth
            scopes: Liste des permissions demandées
            
        Returns:
            URL complète pour l'authentification
        """
        if scopes is None:
            scopes = ["repo", "user"]
        
        scope_str = " ".join(scopes)
        
        return (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scope_str}"
        )
    
    @staticmethod
    async def exchange_code_for_token(
        code: str,
        client_id: str,
        client_secret: str
    ) -> str:
        """
        Échange le code OAuth contre un access token
        
        Args:
            code: Code reçu de GitHub après autorisation
            client_id: GitHub OAuth App Client ID
            client_secret: GitHub OAuth App Client Secret
            
        Returns:
            Access token GitHub
        """
        url = "https://github.com/login/oauth/access_token"
        
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code
        }
        
        headers = {
            "Accept": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("access_token")
                else:
                    raise Exception(f"Erreur échange token: {response.status}")
