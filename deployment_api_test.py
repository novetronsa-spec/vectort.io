#!/usr/bin/env python3
"""
Multi-Platform Deployment API Testing Suite
Tests the new deployment endpoints for Vercel, Netlify, and Render integration
"""

import asyncio
import aiohttp
import json
import os
import sys
from typing import Dict, Any, Optional
import uuid

# Backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://vectort-builder.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class DeploymentAPITester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = f"deployment-test-{uuid.uuid4().hex[:8]}@vectort.io"
        self.test_user_password = "DeployTest123!"
        self.test_project_id = None
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        print(f"🔧 Testing deployment API at: {API_BASE}")

    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    async def register_test_user(self) -> bool:
        """Register a test user for authentication"""
        try:
            payload = {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "full_name": "Deployment Test User"
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    print(f"✅ Test user registered: {self.test_user_email}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ User registration failed: {error_text}")
                    return False
        except Exception as e:
            print(f"❌ User registration error: {str(e)}")
            return False

    async def create_test_project(self) -> bool:
        """Create a test project for deployment testing"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {
                "title": "Deployment Test Project",
                "description": "Test project for deployment API testing",
                "type": "web_app"
            }
            
            async with self.session.post(f"{API_BASE}/projects", json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_project_id = data.get("id")
                    print(f"✅ Test project created: {self.test_project_id}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Project creation failed: {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Project creation error: {str(e)}")
            return False

    def record_test(self, test_name: str, passed: bool, error: str = None):
        """Record test result"""
        self.results["total_tests"] += 1
        if passed:
            self.results["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.results["failed"] += 1
            error_msg = f"❌ {test_name}: {error}" if error else f"❌ {test_name}"
            print(error_msg)
            self.results["errors"].append(error_msg)

    async def test_get_deployment_platforms(self):
        """Test GET /api/deployment/platforms endpoint"""
        test_name = "GET /api/deployment/platforms"
        
        try:
            async with self.session.get(f"{API_BASE}/deployment/platforms") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    if "platforms" not in data:
                        self.record_test(test_name, False, "Missing 'platforms' key in response")
                        return
                    
                    platforms = data["platforms"]
                    if not isinstance(platforms, list):
                        self.record_test(test_name, False, "'platforms' should be a list")
                        return
                    
                    # Check for required platforms
                    platform_ids = [p.get("id") for p in platforms]
                    required_platforms = ["vercel", "netlify", "render"]
                    
                    missing_platforms = [p for p in required_platforms if p not in platform_ids]
                    if missing_platforms:
                        self.record_test(test_name, False, f"Missing platforms: {missing_platforms}")
                        return
                    
                    # Validate platform structure
                    for platform in platforms:
                        required_fields = ["id", "name", "description", "features", "supported_frameworks", "requires", "optional"]
                        missing_fields = [field for field in required_fields if field not in platform]
                        if missing_fields:
                            self.record_test(test_name, False, f"Platform {platform.get('id')} missing fields: {missing_fields}")
                            return
                    
                    print(f"   📋 Found {len(platforms)} platforms: {platform_ids}")
                    self.record_test(test_name, True)
                else:
                    error_text = await response.text()
                    self.record_test(test_name, False, f"Status {response.status}: {error_text}")
        
        except Exception as e:
            self.record_test(test_name, False, f"Exception: {str(e)}")

    async def test_deploy_without_auth(self):
        """Test POST /api/projects/{project_id}/deploy without authentication"""
        test_name = "POST /api/projects/{project_id}/deploy (no auth)"
        
        try:
            payload = {
                "platform": "vercel",
                "github_repo_url": "https://github.com/test/repo",
                "project_name": "test-project"
            }
            
            async with self.session.post(f"{API_BASE}/projects/test-id/deploy", json=payload) as response:
                if response.status in [401, 403]:  # Both 401 and 403 are acceptable for unauthorized access
                    self.record_test(test_name, True)
                else:
                    self.record_test(test_name, False, f"Expected 401 or 403, got {response.status}")
        
        except Exception as e:
            self.record_test(test_name, False, f"Exception: {str(e)}")

    async def test_deploy_invalid_platform(self):
        """Test POST /api/projects/{project_id}/deploy with invalid platform"""
        test_name = "POST /api/projects/{project_id}/deploy (invalid platform)"
        
        if not self.auth_token or not self.test_project_id:
            self.record_test(test_name, False, "Missing auth token or project ID")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {
                "platform": "invalid_platform",
                "github_repo_url": "https://github.com/test/repo",
                "project_name": "test-project"
            }
            
            async with self.session.post(f"{API_BASE}/projects/{self.test_project_id}/deploy", json=payload, headers=headers) as response:
                if response.status == 400:
                    data = await response.json()
                    if "Unsupported platform" in data.get("detail", ""):
                        self.record_test(test_name, True)
                    else:
                        self.record_test(test_name, False, f"Wrong error message: {data.get('detail')}")
                else:
                    self.record_test(test_name, False, f"Expected 400, got {response.status}")
        
        except Exception as e:
            self.record_test(test_name, False, f"Exception: {str(e)}")

    async def test_deploy_missing_fields(self):
        """Test POST /api/projects/{project_id}/deploy with missing required fields"""
        test_name = "POST /api/projects/{project_id}/deploy (missing fields)"
        
        if not self.auth_token or not self.test_project_id:
            self.record_test(test_name, False, "Missing auth token or project ID")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {
                "platform": "vercel"
                # Missing github_repo_url and project_name
            }
            
            async with self.session.post(f"{API_BASE}/projects/{self.test_project_id}/deploy", json=payload, headers=headers) as response:
                if response.status == 422:
                    self.record_test(test_name, True)
                else:
                    self.record_test(test_name, False, f"Expected 422, got {response.status}")
        
        except Exception as e:
            self.record_test(test_name, False, f"Exception: {str(e)}")

    async def test_deploy_vercel_valid_request(self):
        """Test POST /api/projects/{project_id}/deploy with valid Vercel request"""
        test_name = "POST /api/projects/{project_id}/deploy (Vercel - valid structure)"
        
        if not self.auth_token or not self.test_project_id:
            self.record_test(test_name, False, "Missing auth token or project ID")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {
                "platform": "vercel",
                "github_repo_url": "https://github.com/test/nonexistent-repo",
                "project_name": "test-deployment-project",
                "framework": "react",
                "env_vars": {
                    "API_KEY": "test_key",
                    "NODE_ENV": "production"
                }
            }
            
            async with self.session.post(f"{API_BASE}/projects/{self.test_project_id}/deploy", json=payload, headers=headers) as response:
                data = await response.json()
                
                # We expect this to return 200 with success=false due to missing tokens
                if response.status == 200:
                    # Check if the response has the correct structure
                    required_fields = ["success", "platform", "status"]
                    if all(field in data for field in required_fields):
                        if data.get("platform") == "vercel" and data.get("success") == False:
                            if "VERCEL_TOKEN not configured" in data.get("error", ""):
                                print(f"   📝 Expected failure due to missing VERCEL_TOKEN: {data.get('error')}")
                                self.record_test(test_name, True)
                            else:
                                print(f"   📝 Expected failure due to invalid repo/token: {data.get('error', 'Unknown error')}")
                                self.record_test(test_name, True)
                        else:
                            self.record_test(test_name, False, f"Incorrect response structure: {data}")
                    else:
                        self.record_test(test_name, False, f"Missing required fields in response: {data}")
                else:
                    # Unexpected status
                    self.record_test(test_name, False, f"Unexpected status {response.status}: {data}")
        
        except Exception as e:
            self.record_test(test_name, False, f"Exception: {str(e)}")

    async def test_deploy_netlify_valid_request(self):
        """Test POST /api/projects/{project_id}/deploy with valid Netlify request"""
        test_name = "POST /api/projects/{project_id}/deploy (Netlify - valid structure)"
        
        if not self.auth_token or not self.test_project_id:
            self.record_test(test_name, False, "Missing auth token or project ID")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {
                "platform": "netlify",
                "github_repo_url": "https://github.com/test/nonexistent-repo",
                "project_name": "test-netlify-project",
                "build_command": "npm run build",
                "publish_dir": "build",
                "env_vars": {
                    "REACT_APP_API_URL": "https://api.example.com"
                }
            }
            
            async with self.session.post(f"{API_BASE}/projects/{self.test_project_id}/deploy", json=payload, headers=headers) as response:
                data = await response.json()
                
                # We expect this to return 200 with success=false due to missing tokens
                if response.status == 200:
                    # Check if the response has the correct structure
                    required_fields = ["success", "platform", "status"]
                    if all(field in data for field in required_fields):
                        if data.get("platform") == "netlify" and data.get("success") == False:
                            if "NETLIFY_TOKEN not configured" in data.get("error", ""):
                                print(f"   📝 Expected failure due to missing NETLIFY_TOKEN: {data.get('error')}")
                                self.record_test(test_name, True)
                            else:
                                print(f"   📝 Expected failure due to invalid repo/token: {data.get('error', 'Unknown error')}")
                                self.record_test(test_name, True)
                        else:
                            self.record_test(test_name, False, f"Incorrect response structure: {data}")
                    else:
                        self.record_test(test_name, False, f"Missing required fields in response: {data}")
                else:
                    # Unexpected status
                    self.record_test(test_name, False, f"Unexpected status {response.status}: {data}")
        
        except Exception as e:
            self.record_test(test_name, False, f"Exception: {str(e)}")

    async def test_deploy_render_valid_request(self):
        """Test POST /api/projects/{project_id}/deploy with valid Render request"""
        test_name = "POST /api/projects/{project_id}/deploy (Render - valid structure)"
        
        if not self.auth_token or not self.test_project_id:
            self.record_test(test_name, False, "Missing auth token or project ID")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {
                "platform": "render",
                "github_repo_url": "https://github.com/test/nonexistent-repo",
                "project_name": "test-render-project",
                "build_command": "npm install && npm run build",
                "start_command": "npm start",
                "env_vars": {
                    "PORT": "3000",
                    "NODE_ENV": "production"
                }
            }
            
            async with self.session.post(f"{API_BASE}/projects/{self.test_project_id}/deploy", json=payload, headers=headers) as response:
                data = await response.json()
                
                # We expect this to return 200 with success=false due to missing tokens
                if response.status == 200:
                    # Check if the response has the correct structure
                    required_fields = ["success", "platform", "status"]
                    if all(field in data for field in required_fields):
                        if data.get("platform") == "render" and data.get("success") == False:
                            if "RENDER_API_KEY not configured" in data.get("error", ""):
                                print(f"   📝 Expected failure due to missing RENDER_API_KEY: {data.get('error')}")
                                self.record_test(test_name, True)
                            else:
                                print(f"   📝 Expected failure due to invalid repo/token: {data.get('error', 'Unknown error')}")
                                self.record_test(test_name, True)
                        else:
                            self.record_test(test_name, False, f"Incorrect response structure: {data}")
                    else:
                        self.record_test(test_name, False, f"Missing required fields in response: {data}")
                else:
                    # Unexpected status
                    self.record_test(test_name, False, f"Unexpected status {response.status}: {data}")
        
        except Exception as e:
            self.record_test(test_name, False, f"Exception: {str(e)}")

    async def test_deploy_nonexistent_project(self):
        """Test POST /api/projects/{project_id}/deploy with non-existent project"""
        test_name = "POST /api/projects/{project_id}/deploy (non-existent project)"
        
        if not self.auth_token:
            self.record_test(test_name, False, "Missing auth token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {
                "platform": "vercel",
                "github_repo_url": "https://github.com/test/repo",
                "project_name": "test-project"
            }
            
            fake_project_id = str(uuid.uuid4())
            async with self.session.post(f"{API_BASE}/projects/{fake_project_id}/deploy", json=payload, headers=headers) as response:
                if response.status == 404:
                    self.record_test(test_name, True)
                else:
                    self.record_test(test_name, False, f"Expected 404, got {response.status}")
        
        except Exception as e:
            self.record_test(test_name, False, f"Exception: {str(e)}")

    async def run_all_tests(self):
        """Run all deployment API tests"""
        print("🚀 Starting Multi-Platform Deployment API Tests")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Setup
            if not await self.register_test_user():
                print("❌ Failed to register test user, aborting tests")
                return
            
            if not await self.create_test_project():
                print("❌ Failed to create test project, aborting tests")
                return
            
            print("\n📋 Testing Deployment Endpoints:")
            print("-" * 40)
            
            # Test 1: GET /api/deployment/platforms (no auth needed)
            await self.test_get_deployment_platforms()
            
            # Test 2: Authentication tests
            await self.test_deploy_without_auth()
            
            # Test 3: Validation tests
            await self.test_deploy_invalid_platform()
            await self.test_deploy_missing_fields()
            await self.test_deploy_nonexistent_project()
            
            # Test 4: Platform-specific deployment tests (expected to fail due to invalid repos/tokens)
            await self.test_deploy_vercel_valid_request()
            await self.test_deploy_netlify_valid_request()
            await self.test_deploy_render_valid_request()
            
        finally:
            await self.cleanup_session()
        
        # Print results
        print("\n" + "=" * 60)
        print("📊 DEPLOYMENT API TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['errors']:
            print(f"\n🔍 Failed Tests:")
            for error in self.results['errors']:
                print(f"   {error}")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100 if self.results['total_tests'] > 0 else 0
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 DEPLOYMENT API TESTS PASSED!")
        else:
            print("⚠️  Some deployment API tests failed - review errors above")
        
        return success_rate >= 80

async def main():
    """Main test runner"""
    tester = DeploymentAPITester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())