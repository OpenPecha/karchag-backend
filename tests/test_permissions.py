#!/usr/bin/env python3
"""
Comprehensive Permission Testing Script for the Buddhist Digital Library API

This script tests:
1. GET requests without authentication (should work)
2. POST/PUT/DELETE without admin token (should fail)
3. POST/PUT/DELETE with admin token (should work)
4. Response filtering based on user role
5. Query parameter filtering
"""

import requests
import json
import sys
from typing import Optional, Dict, Any
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_CREDENTIALS = {
    "username": "testuser2",
    "password": "user123"
}
ADMIN_CREDENTIALS = {
    "username": "testadmin",
    "password": "admin123"
}

class PermissionTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, expected: str, actual: str, passed: bool):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "test": test_name,
            "expected": expected,
            "actual": actual,
            "status": status,
            "passed": passed
        }
        self.test_results.append(result)
        print(f"{status} {test_name}")
        if not passed:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
        print()

    def get_admin_token(self) -> Optional[str]:
        """Get admin authentication token"""
        try:
            response = requests.post(
                f"{self.base_url}/login",
                json=ADMIN_CREDENTIALS
            )
            if response.status_code == 200:
                return response.json().get("tokens", {}).get("access_token")
            else:
                print(f"❌ Failed to get admin token: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error getting admin token: {e}")
            return None

    def get_user_token(self) -> Optional[str]:
        """Get regular user authentication token"""
        try:
            response = requests.post(
                f"{self.base_url}/login",
                json=TEST_USER_CREDENTIALS
            )
            if response.status_code == 200:
                return response.json().get("tokens", {}).get("access_token")
            else:
                print(f"❌ Failed to get user token: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error getting user token: {e}")
            return None

    def test_health_check(self):
        """Test if the server is running"""
        print("🔍 Testing server health...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server is running")
                return True
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            return False

    def test_get_without_auth(self):
        """Test GET requests without authentication - should work"""
        print("🔐 Testing GET requests without authentication...")
        
        endpoints = [
            "/categories",
            "/news",
            "/news/latest",
            "/health"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                expected = "200 OK"
                actual = f"{response.status_code} {response.reason}"
                passed = response.status_code == 200
                
                self.log_test(
                    f"GET {endpoint} without auth",
                    expected,
                    actual,
                    passed
                )
            except Exception as e:
                self.log_test(
                    f"GET {endpoint} without auth",
                    "200 OK",
                    f"Error: {e}",
                    False
                )

    def test_protected_endpoints_without_auth(self):
        """Test POST/PUT/DELETE without authentication - should fail with 403"""
        print("🔐 Testing protected endpoints without authentication...")
        
        test_cases = [
            ("POST", "/categories", {"name_english": "Test Category", "name_tibetan": "Test"}),
            ("POST", "/news", {"title_english": "Test News", "content_english": "Test content"}),
            ("PUT", "/categories/1", {"name_english": "Updated Category"}),
            ("DELETE", "/categories/999", None),
        ]
        
        for method, endpoint, data in test_cases:
            try:
                if method == "POST":
                    response = requests.post(f"{self.base_url}{endpoint}", json=data)
                elif method == "PUT":
                    response = requests.put(f"{self.base_url}{endpoint}", json=data)
                elif method == "DELETE":
                    response = requests.delete(f"{self.base_url}{endpoint}")
                
                expected = "403 Forbidden"
                actual = f"{response.status_code} {response.reason}"
                passed = response.status_code == 403
                
                self.log_test(
                    f"{method} {endpoint} without auth",
                    expected,
                    actual,
                    passed
                )
            except Exception as e:
                self.log_test(
                    f"{method} {endpoint} without auth",
                    "403 Forbidden",
                    f"Error: {e}",
                    False
                )

    def test_protected_endpoints_with_user_token(self):
        """Test POST/PUT/DELETE with regular user token - should fail with 403"""
        print("🔐 Testing protected endpoints with user token...")
        
        if not self.user_token:
            print("⚠️  No user token available, skipping user token tests")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        test_cases = [
            ("POST", "/categories", {"name_english": "Test Category", "name_tibetan": "Test"}),
            ("POST", "/news", {"title_english": "Test News", "content_english": "Test content"}),
            ("PUT", "/categories/1", {"name_english": "Updated Category"}),
            ("DELETE", "/categories/999", None),
        ]
        
        for method, endpoint, data in test_cases:
            try:
                if method == "POST":
                    response = requests.post(f"{self.base_url}{endpoint}", json=data, headers=headers)
                elif method == "PUT":
                    response = requests.put(f"{self.base_url}{endpoint}", json=data, headers=headers)
                elif method == "DELETE":
                    response = requests.delete(f"{self.base_url}{endpoint}", headers=headers)
                
                expected = "403 Forbidden"
                actual = f"{response.status_code} {response.reason}"
                passed = response.status_code == 403
                
                self.log_test(
                    f"{method} {endpoint} with user token",
                    expected,
                    actual,
                    passed
                )
            except Exception as e:
                self.log_test(
                    f"{method} {endpoint} with user token",
                    "403 Forbidden",
                    f"Error: {e}",
                    False
                )

    def test_protected_endpoints_with_admin_token(self):
        """Test POST/PUT/DELETE with admin token - should work"""
        print("🔐 Testing protected endpoints with admin token...")
        
        if not self.admin_token:
            print("⚠️  No admin token available, skipping admin tests")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test creating a category first
        try:
            category_data = {
                "name_english": "Test Category",
                "name_tibetan": "Test Category Tibetan",
                "description_english": "Test Description",
                "description_tibetan": "Test Description Tibetan"
            }
            response = requests.post(f"{self.base_url}/categories", json=category_data, headers=headers)
            expected = "201 Created"
            actual = f"{response.status_code} {response.reason}"
            passed = response.status_code == 201
            
            self.log_test(
                "POST /categories with admin token",
                expected,
                actual,
                passed
            )
            
            if passed:
                created_category = response.json()
                category_id = created_category.get("id")
                
                # Test updating the created category
                update_data = {"name_english": "Updated Test Category"}
                response = requests.put(f"{self.base_url}/categories/{category_id}", json=update_data, headers=headers)
                expected = "200 OK"
                actual = f"{response.status_code} {response.reason}"
                passed = response.status_code == 200
                
                self.log_test(
                    f"PUT /categories/{category_id} with admin token",
                    expected,
                    actual,
                    passed
                )
                
                # Test deleting the created category
                response = requests.delete(f"{self.base_url}/categories/{category_id}", headers=headers)
                expected = "200 OK"
                actual = f"{response.status_code} {response.reason}"
                passed = response.status_code in [200, 204]
                
                self.log_test(
                    f"DELETE /categories/{category_id} with admin token",
                    expected,
                    actual,
                    passed
                )
        except Exception as e:
            self.log_test(
                "Admin CRUD operations",
                "Success",
                f"Error: {e}",
                False
            )

    def test_response_filtering(self):
        """Test response filtering based on user role"""
        print("🔐 Testing response filtering based on user role...")
        
        # Test admin-only endpoints
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test admin-only endpoint
            response = requests.get(f"{self.base_url}/categories/all", headers=headers)
            expected = "200 OK"
            actual = f"{response.status_code} {response.reason}"
            passed = response.status_code == 200
            
            self.log_test(
                "GET /categories/all with admin token",
                expected,
                actual,
                passed
            )
        
        # Test admin-only endpoint without token
        response = requests.get(f"{self.base_url}/categories/all")
        expected = "403 Forbidden"
        actual = f"{response.status_code} {response.reason}"
        passed = response.status_code == 403
        
        self.log_test(
            "GET /categories/all without token",
            expected,
            actual,
            passed
        )

    def test_query_parameter_filtering(self):
        """Test query parameter filtering"""
        print("🔐 Testing query parameter filtering...")
        
        endpoints_with_params = [
            ("/categories?lang=en", "Language parameter filtering"),
            ("/news?page=1&limit=5", "Pagination parameters"),
            ("/news/latest?limit=3&lang=tb", "Combined parameters"),
        ]
        
        for endpoint, description in endpoints_with_params:
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                expected = "200 OK"
                actual = f"{response.status_code} {response.reason}"
                passed = response.status_code == 200
                
                self.log_test(
                    f"{description}: {endpoint}",
                    expected,
                    actual,
                    passed
                )
            except Exception as e:
                self.log_test(
                    f"{description}: {endpoint}",
                    "200 OK",
                    f"Error: {e}",
                    False
                )

    def test_dashboard_permissions(self):
        """Test dashboard endpoint permissions"""
        print("🔐 Testing dashboard permissions...")
        
        # Test without authentication
        response = requests.get(f"{self.base_url}/dashboard/stats")
        expected = "403 Forbidden"
        actual = f"{response.status_code} {response.reason}"
        passed = response.status_code == 403
        
        self.log_test(
            "GET /dashboard/stats without auth",
            expected,
            actual,
            passed
        )
        
        # Test with admin token
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/dashboard/stats", headers=headers)
            expected = "200 OK"
            actual = f"{response.status_code} {response.reason}"
            passed = response.status_code == 200
            
            self.log_test(
                "GET /dashboard/stats with admin token",
                expected,
                actual,
                passed
            )

    def run_all_tests(self):
        """Run all permission tests"""
        print("🚀 Starting comprehensive permission testing...\n")
        
        # Check server health
        if not self.test_health_check():
            print("❌ Server is not accessible. Please ensure the server is running on port 8000.")
            return False
        
        # Get tokens
        print("🔑 Getting authentication tokens...")
        self.admin_token = self.get_admin_token()
        self.user_token = self.get_user_token()
        
        if self.admin_token:
            print("✅ Admin token obtained")
        else:
            print("⚠️  Could not obtain admin token")
        
        if self.user_token:
            print("✅ User token obtained")
        else:
            print("⚠️  Could not obtain user token")
        
        print()
        
        # Run tests
        self.test_get_without_auth()
        self.test_protected_endpoints_without_auth()
        self.test_protected_endpoints_with_user_token()
        self.test_protected_endpoints_with_admin_token()
        self.test_response_filtering()
        self.test_query_parameter_filtering()
        self.test_dashboard_permissions()
        
        # Print summary
        self.print_summary()
        
        return all(result["passed"] for result in self.test_results)

    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['test']}")
                    print(f"    Expected: {result['expected']}")
                    print(f"    Actual: {result['actual']}")
            print()
        
        print("=" * 80)

def main():
    """Main function"""
    tester = PermissionTester(BASE_URL)
    success = tester.run_all_tests()
    
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
