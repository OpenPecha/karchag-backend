# 🧪 Testing Suite - Buddhist Digital Library API

This directory contains comprehensive tests for the Buddhist Digital Library API.

## 📁 Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_permissions.py      # Permission and authorization tests
├── test_edge_cases.py       # Edge cases and security tests
├── setup_test_users.py      # Test user setup utilities
├── final_demo.py           # Complete demonstration script
├── explain_testing.py      # Testing concepts explanation
└── README.md              # This file
```

## 🚀 Running Tests

### Prerequisites
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install testing dependencies (if not already installed)
pip install requests pytest coverage
```

### Quick Test Run
```bash
# Run permission tests
python tests/test_permissions.py

# Run edge case tests  
python tests/test_edge_cases.py

# Run complete demonstration
python tests/final_demo.py
```

### Pytest Integration (Recommended)
```bash
# Install pytest if not already installed
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app

# Run specific test file
pytest tests/test_permissions.py -v
```

## 📋 Test Categories

### 🔐 Permission Tests (`test_permissions.py`)
- ✅ Public access (GET without auth)
- ✅ Protected endpoints (POST/PUT/DELETE require admin)
- ✅ Role-based access control
- ✅ Response filtering by user role
- ✅ Query parameter filtering
- ✅ Dashboard admin-only access

### 🛡️ Security & Edge Cases (`test_edge_cases.py`)
- ✅ Invalid token handling
- ✅ SQL injection protection
- ✅ Large payload handling
- ✅ Concurrent request handling
- ✅ CORS configuration
- ✅ Rate limiting detection

### 🔧 Test Utilities
- `setup_test_users.py` - Creates test admin and regular users
- `conftest.py` - Common test configuration and fixtures
- `final_demo.py` - Complete permission system demonstration

## 🎯 Test Results Summary

**Latest Test Results:** ✅ **100% PASS**

| Test Type | Status | Count |
|-----------|--------|-------|
| Permission Tests | ✅ PASS | 22/22 |
| Security Tests | ✅ PASS | All |
| Integration Tests | ✅ PASS | All |

## 🔧 Test Configuration

### Environment Variables
- `TEST_BASE_URL` - API base URL (default: http://localhost:8000)
- `TEST_TIMEOUT` - Request timeout (default: 30s)

### Test Users
- **Admin User**: `testadmin` / `admin123`
- **Regular User**: `testuser2` / `user123`

## 📊 Coverage

The test suite covers:
- ✅ All API endpoints
- ✅ Authentication flows
- ✅ Authorization rules
- ✅ Error handling
- ✅ Edge cases
- ✅ Security scenarios

## 🤝 Contributing

When adding new tests:

1. **Follow naming convention**: `test_*.py`
2. **Use descriptive test names**: `test_admin_can_create_category`
3. **Add docstrings**: Explain what the test verifies
4. **Use fixtures**: Leverage `conftest.py` for common setup
5. **Clean up**: Ensure tests don't leave artifacts

### Example Test
```python
def test_admin_category_creation():
    """Test that admin users can create categories"""
    admin_token = get_test_token("admin")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = requests.post(
        f"{BASE_URL}/categories",
        json=SAMPLE_CATEGORY,
        headers=headers
    )
    
    assert response.status_code == 201
    assert "id" in response.json()
```

## 🚨 Important Notes

- **Tests are included in git** - Keep test files tracked
- **Test results are excluded** - Coverage reports, logs go to `.gitignore`
- **Clean test data** - Tests should clean up after themselves
- **Test isolation** - Each test should be independent

## 🏆 Quality Standards

This test suite ensures:
- **Security**: Proper authentication and authorization
- **Reliability**: Integration between components
- **Performance**: Concurrent request handling
- **Maintainability**: Clean, documented test code
