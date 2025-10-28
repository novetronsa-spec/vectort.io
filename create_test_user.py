#!/usr/bin/env python3
"""
Create a test user with sufficient credits for testing
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime
from passlib.context import CryptContext

async def create_test_user():
    client = AsyncIOMotorClient('mongodb://localhost:27017/vectort_db')
    db = client['vectort_db']
    
    # Password hashing
    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
    
    # Create user with lots of credits
    user_data = {
        "id": str(uuid.uuid4()),
        "email": "js_tester@vectort.io",
        "full_name": "JavaScript Tester",
        "password_hash": pwd_context.hash("TestPassword123!"),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True,
        "provider": "email",
        "provider_id": None,
        "credits_free": 50.0,  # 50 free credits
        "credits_monthly": 0.0,
        "credits_monthly_limit": 0.0,
        "credits_topup": 100.0,  # 100 purchased credits
        "subscription_plan": "free",
        "credits_total": 150.0  # Total 150 credits
    }
    
    # Check if user exists
    existing = await db.users.find_one({"email": user_data["email"]})
    if existing:
        print(f"User {user_data['email']} already exists")
        # Update credits
        await db.users.update_one(
            {"email": user_data["email"]},
            {"$set": {
                "credits_free": 50.0,
                "credits_topup": 100.0,
                "credits_total": 150.0
            }}
        )
        print("Updated credits to 150 total")
    else:
        # Insert new user
        await db.users.insert_one(user_data)
        print(f"Created user {user_data['email']} with 150 credits")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_test_user())