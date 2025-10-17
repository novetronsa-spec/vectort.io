"""
GitHub OAuth Integration for Vectort.io
Handles GitHub authentication, repository management, and code deployment
"""

import os
import secrets
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from github import Github, GithubException
from cryptography.fernet import Fernet
import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase


# Configuration from environment
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
GITHUB_REDIRECT_URI = os.environ.get('GITHUB_REDIRECT_URI')
FERNET_KEY = os.environ.get('FERNET_ENCRYPTION_KEY')

# Initialize encryption
fernet = Fernet(FERNET_KEY.encode()) if FERNET_KEY else None


class GitHubIntegration:
    """GitHub OAuth and API integration"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
    def generate_oauth_url(self, state: Optional[str] = None) -> Dict[str, str]:
        """Generate GitHub OAuth authorization URL"""
        if not state:
            state = secrets.token_urlsafe(32)
        
        scopes = "repo,user,workflow"  # Full repo access + user info + workflows
        auth_url = (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={GITHUB_CLIENT_ID}"
            f"&redirect_uri={GITHUB_REDIRECT_URI}"
            f"&scope={scopes}"
            f"&state={state}"
        )
        
        return {
            "url": auth_url,
            "state": state
        }
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, any]:
        """Exchange authorization code for access token"""
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
                raise Exception(f"Failed to exchange code: {response.text}")
            
            data = response.json()
            
            if "error" in data:
                raise Exception(f"GitHub OAuth error: {data.get('error_description', data['error'])}")
            
            return {
                "access_token": data["access_token"],
                "token_type": data["token_type"],
                "scope": data["scope"]
            }
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt access token for storage"""
        if not fernet:
            raise Exception("Encryption key not configured")
        return fernet.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt stored access token"""
        if not fernet:
            raise Exception("Encryption key not configured")
        return fernet.decrypt(encrypted_token.encode()).decode()
    
    async def store_user_token(self, user_id: str, access_token: str, github_user_data: Dict):
        """Store encrypted GitHub token in database"""
        encrypted_token = self.encrypt_token(access_token)
        
        await self.db.github_connections.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "encrypted_token": encrypted_token,
                    "github_username": github_user_data.get("login"),
                    "github_user_id": github_user_data.get("id"),
                    "github_email": github_user_data.get("email"),
                    "github_name": github_user_data.get("name"),
                    "github_avatar": github_user_data.get("avatar_url"),
                    "connected_at": datetime.utcnow(),
                    "last_used": datetime.utcnow()
                }
            },
            upsert=True
        )
    
    async def get_user_token(self, user_id: str) -> Optional[str]:
        """Retrieve and decrypt user's GitHub token"""
        connection = await self.db.github_connections.find_one({"user_id": user_id})
        
        if not connection:
            return None
        
        # Update last used timestamp
        await self.db.github_connections.update_one(
            {"user_id": user_id},
            {"$set": {"last_used": datetime.utcnow()}}
        )
        
        return self.decrypt_token(connection["encrypted_token"])
    
    async def disconnect_github(self, user_id: str) -> bool:
        """Remove GitHub connection for user"""
        result = await self.db.github_connections.delete_one({"user_id": user_id})
        return result.deleted_count > 0
    
    def get_github_client(self, access_token: str) -> Github:
        """Create authenticated GitHub client"""
        return Github(access_token)
    
    async def get_user_info(self, access_token: str) -> Dict:
        """Get GitHub user information"""
        github = self.get_github_client(access_token)
        user = github.get_user()
        
        return {
            "login": user.login,
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "company": user.company,
            "location": user.location,
            "public_repos": user.public_repos,
            "followers": user.followers,
            "following": user.following
        }
    
    async def list_repositories(self, user_id: str) -> List[Dict]:
        """List user's GitHub repositories"""
        token = await self.get_user_token(user_id)
        if not token:
            raise Exception("GitHub not connected")
        
        github = self.get_github_client(token)
        user = github.get_user()
        repos = user.get_repos(sort="updated")
        
        repo_list = []
        for repo in repos[:50]:  # Limit to 50 most recent
            repo_list.append({
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "private": repo.private,
                "default_branch": repo.default_branch,
                "url": repo.html_url,
                "clone_url": repo.clone_url,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
            })
        
        return repo_list
    
    async def list_branches(self, user_id: str, repo_full_name: str) -> List[Dict]:
        """List repository branches"""
        token = await self.get_user_token(user_id)
        if not token:
            raise Exception("GitHub not connected")
        
        github = self.get_github_client(token)
        repo = github.get_repo(repo_full_name)
        branches = repo.get_branches()
        
        branch_list = []
        for branch in branches:
            branch_list.append({
                "name": branch.name,
                "protected": branch.protected,
                "commit_sha": branch.commit.sha,
                "commit_message": branch.commit.commit.message
            })
        
        return branch_list
    
    async def get_file_content(self, user_id: str, repo_full_name: str, file_path: str, branch: str = None) -> Dict:
        """Get file content from repository"""
        token = await self.get_user_token(user_id)
        if not token:
            raise Exception("GitHub not connected")
        
        github = self.get_github_client(token)
        repo = github.get_repo(repo_full_name)
        
        ref = branch if branch else repo.default_branch
        content = repo.get_contents(file_path, ref=ref)
        
        return {
            "name": content.name,
            "path": content.path,
            "size": content.size,
            "content": content.decoded_content.decode('utf-8'),
            "sha": content.sha,
            "url": content.html_url
        }
    
    async def create_or_update_file(
        self, 
        user_id: str, 
        repo_full_name: str, 
        file_path: str, 
        content: str,
        commit_message: str,
        branch: str = None
    ) -> Dict:
        """Create or update a file in repository"""
        token = await self.get_user_token(user_id)
        if not token:
            raise Exception("GitHub not connected")
        
        github = self.get_github_client(token)
        repo = github.get_repo(repo_full_name)
        
        branch = branch or repo.default_branch
        
        try:
            # Try to get existing file
            existing_file = repo.get_contents(file_path, ref=branch)
            
            # Update existing file
            result = repo.update_file(
                path=file_path,
                message=commit_message,
                content=content,
                sha=existing_file.sha,
                branch=branch
            )
            action = "updated"
        except GithubException as e:
            if e.status == 404:
                # Create new file
                result = repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    branch=branch
                )
                action = "created"
            else:
                raise
        
        return {
            "action": action,
            "commit_sha": result["commit"].sha,
            "commit_url": result["commit"].html_url,
            "file_url": result["content"].html_url
        }
    
    async def create_repository(
        self,
        user_id: str,
        name: str,
        description: str = "",
        private: bool = False,
        auto_init: bool = True
    ) -> Dict:
        """Create a new GitHub repository"""
        token = await self.get_user_token(user_id)
        if not token:
            raise Exception("GitHub not connected")
        
        github = self.get_github_client(token)
        user = github.get_user()
        
        repo = user.create_repo(
            name=name,
            description=description,
            private=private,
            auto_init=auto_init
        )
        
        return {
            "id": repo.id,
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "url": repo.html_url,
            "clone_url": repo.clone_url,
            "default_branch": repo.default_branch
        }
    
    async def deploy_project_to_github(
        self,
        user_id: str,
        repo_full_name: str,
        files: Dict[str, str],  # path: content
        commit_message: str = "Deploy from Vectort.io",
        branch: str = None
    ) -> Dict:
        """Deploy multiple files to GitHub repository"""
        token = await self.get_user_token(user_id)
        if not token:
            raise Exception("GitHub not connected")
        
        github = self.get_github_client(token)
        repo = github.get_repo(repo_full_name)
        
        branch = branch or repo.default_branch
        base_commit = repo.get_branch(branch).commit
        
        # Create blobs for all files
        blobs = []
        for file_path, content in files.items():
            blob = repo.create_git_blob(content, "utf-8")
            blobs.append({
                "path": file_path,
                "mode": "100644",  # Regular file
                "type": "blob",
                "sha": blob.sha
            })
        
        # Create tree
        tree = repo.create_git_tree(blobs, base_tree=base_commit.commit.tree)
        
        # Create commit
        commit = repo.create_git_commit(commit_message, tree, [base_commit.commit])
        
        # Update branch reference
        ref = repo.get_git_ref(f"heads/{branch}")
        ref.edit(commit.sha)
        
        return {
            "commit_sha": commit.sha,
            "commit_url": commit.html_url,
            "files_deployed": len(files),
            "branch": branch
        }
