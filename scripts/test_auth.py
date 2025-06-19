"""
Test authentication endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Test login endpoint"""
    print("\n=== Testing Login ===")
    
    # Test with valid credentials
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": "employee@example.com",
            "password": "employee123"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Login successful")
        print(f"  Access Token: {data['access_token'][:50]}...")
        print(f"  Expires in: {data['expires_in']} seconds")
        return data['access_token']
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return None


def test_get_current_user(token):
    """Test get current user endpoint"""
    print("\n=== Testing Get Current User ===")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Get current user successful")
        print(f"  User: {data['full_name']} ({data['email']})")
        print(f"  Role: {data['role']}")
    else:
        print(f"✗ Get current user failed: {response.status_code}")
        print(f"  Error: {response.text}")


def test_invalid_token():
    """Test with invalid token"""
    print("\n=== Testing Invalid Token ===")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    if response.status_code == 401:
        print("✓ Invalid token correctly rejected")
    else:
        print(f"✗ Unexpected response: {response.status_code}")


def main():
    """Run all tests"""
    print("Starting authentication tests...")
    
    # Test login
    token = test_login()
    
    if token:
        # Test get current user
        test_get_current_user(token)
    
    # Test invalid token
    test_invalid_token()
    
    print("\n=== Tests Complete ===")


if __name__ == "__main__":
    main()