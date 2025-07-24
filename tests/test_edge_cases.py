#!/usr/bin/env python3
"""
Additional edge case testing for the Buddhist Digital Library API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_invalid_tokens():
    """Test with invalid/malformed tokens"""
    print("🔐 Testing invalid token scenarios...")
    
    test_cases = [
        ("invalid_token", "Invalid token format"),
        ("Bearer ", "Empty token"),
        ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid", "Malformed JWT"),
        ("expired_token_here", "Expired token simulation")
    ]
    
    for token, description in test_cases:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
        
        status = "✅ PASS" if response.status_code in [401, 403] else "❌ FAIL"
        print(f"{status} {description}: {response.status_code}")

def test_sql_injection_attempts():
    """Test for SQL injection protection"""
    print("\n🔐 Testing SQL injection protection...")
    
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'/*",
        "<script>alert('xss')</script>",
        "../../etc/passwd"
    ]
    
    for payload in malicious_inputs:
        # Test in search parameter
        response = requests.get(f"{BASE_URL}/categories", params={"search": payload})
        status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
        print(f"{status} Search injection test: {response.status_code}")
        
        # Test in login
        response = requests.post(f"{BASE_URL}/login", json={"username": payload, "password": "test"})
        status = "✅ PASS" if response.status_code in [401, 422] else "❌ FAIL"
        print(f"{status} Login injection test: {response.status_code}")

def test_large_payloads():
    """Test handling of large payloads"""
    print("\n🔐 Testing large payload handling...")
    
    # Create very large category data
    large_data = {
        "name_english": "A" * 10000,
        "name_tibetan": "བ" * 10000,
        "description_english": "Large description " * 1000
    }
    
    response = requests.post(f"{BASE_URL}/categories", json=large_data)
    status = "✅ PASS" if response.status_code in [400, 413, 422] else "❌ FAIL"
    print(f"{status} Large payload test: {response.status_code}")

def test_concurrent_requests():
    """Test concurrent request handling"""
    print("\n🔐 Testing concurrent requests...")
    
    import threading
    import time
    
    results = []
    
    def make_request():
        response = requests.get(f"{BASE_URL}/categories")
        results.append(response.status_code)
    
    # Start 10 concurrent requests
    threads = []
    for i in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    # Wait for all to complete
    for thread in threads:
        thread.join()
    
    success_count = sum(1 for code in results if code == 200)
    status = "✅ PASS" if success_count >= 8 else "❌ FAIL"
    print(f"{status} Concurrent requests: {success_count}/10 successful")

def test_cors_headers():
    """Test CORS headers"""
    print("\n🔐 Testing CORS configuration...")
    
    headers = {"Origin": "http://localhost:3000"}
    response = requests.get(f"{BASE_URL}/categories", headers=headers)
    
    cors_headers = [
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Headers"
    ]
    
    for header in cors_headers:
        if header in response.headers:
            print(f"✅ PASS {header}: {response.headers[header]}")
        else:
            print(f"❌ FAIL {header}: Not present")

def test_rate_limiting():
    """Test for rate limiting (if implemented)"""
    print("\n🔐 Testing rate limiting...")
    
    # Make rapid requests to see if rate limiting is in place
    responses = []
    for i in range(20):
        response = requests.get(f"{BASE_URL}/categories")
        responses.append(response.status_code)
        if response.status_code == 429:  # Too Many Requests
            print("✅ PASS Rate limiting detected")
            return
    
    print("⚠️  No rate limiting detected (may be intentional)")

def main():
    print("🚀 Running additional security and edge case tests...\n")
    
    test_invalid_tokens()
    test_sql_injection_attempts()
    test_large_payloads()
    test_concurrent_requests()
    test_cors_headers()
    test_rate_limiting()
    
    print("\n✅ Additional testing complete!")

if __name__ == "__main__":
    main()
