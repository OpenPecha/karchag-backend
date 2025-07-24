#!/usr/bin/env python3
"""
Setup test users for permission testing
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def create_test_users():
    """Create test users for permission testing"""
    print("🔧 Setting up test users...")
    
    # First, let's try to create an admin user
    admin_data = {
        "username": "admin",
        "email": "admin@test.com",
        "password": "adminpass",
        "is_admin": True
    }
    
    user_data = {
        "username": "testuser",
        "email": "testuser@test.com", 
        "password": "testpass",
        "is_admin": False
    }
    
    # Try to register users
    for user_type, data in [("admin", admin_data), ("user", user_data)]:
        try:
            response = requests.post(f"{BASE_URL}/signup", json=data)
            if response.status_code == 201:
                print(f"✅ {user_type} user created successfully")
            elif response.status_code == 400:
                # User might already exist
                print(f"⚠️  {user_type} user might already exist")
            else:
                print(f"❌ Failed to create {user_type} user: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error creating {user_type} user: {e}")

def test_login():
    """Test login for both users"""
    print("\n🔑 Testing user login...")
    
    credentials = [
        ("admin", {"username": "admin", "password": "adminpass"}),
        ("user", {"username": "testuser", "password": "testpass"})
    ]
    
    for user_type, creds in credentials:
        try:
            response = requests.post(f"{BASE_URL}/login", json=creds)
            if response.status_code == 200:
                token_data = response.json()
                print(f"✅ {user_type} login successful")
                access_token = token_data.get("tokens", {}).get("access_token", "N/A")
                print(f"   Token: {access_token[:20] if access_token != 'N/A' else 'N/A'}...")
            else:
                print(f"❌ {user_type} login failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error testing {user_type} login: {e}")

def main():
    """Main function"""
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not healthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    create_test_users()
    test_login()
    print("\n✅ Setup complete! You can now run the permission tests.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
