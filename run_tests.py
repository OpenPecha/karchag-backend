#!/usr/bin/env python3
"""
Test runner for the Buddhist Digital Library API
Runs all tests and generates a comprehensive report
"""

import subprocess
import sys
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and return the result"""
    print(f"🏃 {description}...")
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} completed in {elapsed:.2f}s")
            return True, result.stdout
        else:
            print(f"❌ {description} failed in {elapsed:.2f}s")
            print(f"Error: {result.stderr}")
            return False, result.stderr
            
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False, str(e)

def main():
    """Run all tests"""
    print("🧪 BUDDHIST DIGITAL LIBRARY API - TEST SUITE")
    print("=" * 60)
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / "tests"
    
    # Test commands to run
    test_commands = [
        {
            "command": "source venv/bin/activate && python tests/setup_test_users.py",
            "description": "Setting up test users",
            "required": False
        },
        {
            "command": "source venv/bin/activate && python tests/test_permissions.py",
            "description": "Running permission tests",
            "required": True
        },
        {
            "command": "source venv/bin/activate && python tests/test_edge_cases.py", 
            "description": "Running security and edge case tests",
            "required": True
        },
        {
            "command": "source venv/bin/activate && python tests/final_demo.py",
            "description": "Running comprehensive demonstration",
            "required": False
        }
    ]
    
    # Track results
    results = []
    total_tests = len(test_commands)
    passed_tests = 0
    
    # Run each test
    for test_cmd in test_commands:
        success, output = run_command(test_cmd["command"], test_cmd["description"])
        results.append({
            "description": test_cmd["description"],
            "success": success,
            "required": test_cmd["required"],
            "output": output
        })
        
        if success:
            passed_tests += 1
        elif test_cmd["required"]:
            print(f"❌ Required test failed: {test_cmd['description']}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        required = " (Required)" if result["required"] else " (Optional)"
        print(f"{status} {result['description']}{required}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    # Check if all required tests passed
    required_failed = [r for r in results if not r["success"] and r["required"]]
    
    if not required_failed:
        print("🎉 All required tests passed!")
        return 0
    else:
        print(f"💥 {len(required_failed)} required tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
