#!/usr/bin/env python3
"""
CraftChain System Test
Tests all major functionality after fixes
"""

import requests
import json
import time

def test_service():
    """Test if the CraftChain service is running."""
    print("Testing CraftChain Service...")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:5002"
    
    # Test 1: Check if service is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Service is running")
        else:
            print(f"❌ Service returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Service not accessible: {e}")
        return False
    
    # Test 2: Test registration endpoint
    try:
        test_data = {
            'fullname': 'Test User',
            'email': f'test{int(time.time())}@test.com',
            'phone': '1234567890',
            'address': 'Test Address',
            'password': 'test123456'
        }
        
        response = requests.post(f"{base_url}/api/register/buyer", data=test_data, timeout=10)
        if response.status_code == 201:
            print("✅ Buyer registration working")
        else:
            print(f"❌ Buyer registration failed: {response.text}")
    except Exception as e:
        print(f"❌ Buyer registration error: {e}")
    
    # Test 3: Test login endpoint
    try:
        login_data = {
            'email': test_data['email'],
            'password': test_data['password'],
            'role': 'buyer'
        }
        
        response = requests.post(f"{base_url}/api/login", data=login_data, timeout=10)
        if response.status_code == 200:
            print("✅ Login working")
        else:
            print(f"❌ Login failed: {response.text}")
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    # Test 4: Test products endpoint
    try:
        response = requests.get(f"{base_url}/api/products", timeout=10)
        if response.status_code == 200:
            print("✅ Products API working")
        else:
            print(f"❌ Products API failed: {response.text}")
    except Exception as e:
        print(f"❌ Products API error: {e}")
    
    print("\n" + "=" * 40)
    print("System test completed!")
    print("If you see ✅ marks, those features are working.")
    print("If you see ❌ marks, there may still be issues.")
    
    return True

def main():
    """Main function."""
    print("CraftChain System Test")
    print("Make sure the CraftChain service is running before testing.")
    print()
    
    input("Press Enter to start testing...")
    
    test_service()
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
