#!/usr/bin/env python3
"""
Test configuration and utilities for the Buddhist Digital Library API
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_CONFIG = {
    "BASE_URL": "http://localhost:8000",
    "TEST_DB_URL": "sqlite:///./test.db",  # Use separate test database
    "ADMIN_USER": {
        "username": "testadmin",
        "password": "admin123"
    },
    "REGULAR_USER": {
        "username": "testuser2", 
        "password": "user123"
    },
    "TEST_TIMEOUT": 30,
    "MAX_RETRIES": 3
}

# Test data fixtures
SAMPLE_CATEGORY = {
    "name_english": "Test Category",
    "name_tibetan": "དཔེ་རིགས་སྡེ་ཚན།",
    "description_english": "A test category for automated testing",
    "description_tibetan": "རང་འགུལ་མཚན་ཞིབ་ཀྱི་དོན་དུ་དཔེ་རིགས་སྡེ་ཚན།"
}

SAMPLE_NEWS = {
    "title_english": "Test News Article",
    "title_tibetan": "དཔེ་གསར་ལས་ཚན།",
    "content_english": "This is a test news article for automated testing.",
    "content_tibetan": "འདི་ནི་རང་འགུལ་མཚན་ཞིབ་ཀྱི་དོན་དུ་གསར་འགྱུར་རམ་འདེགས་ཤིག་རེད།"
}

def get_test_token(user_type="admin"):
    """Helper function to get authentication token for tests"""
    import requests
    
    if user_type == "admin":
        credentials = TEST_CONFIG["ADMIN_USER"]
    else:
        credentials = TEST_CONFIG["REGULAR_USER"]
    
    response = requests.post(
        f"{TEST_CONFIG['BASE_URL']}/login",
        json=credentials
    )
    
    if response.status_code == 200:
        return response.json()["tokens"]["access_token"]
    return None

def cleanup_test_data():
    """Clean up test data after tests"""
    # Implementation would depend on your cleanup strategy
    pass
