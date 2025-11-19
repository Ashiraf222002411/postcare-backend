#!/usr/bin/env python3
"""
Test script to verify enhanced SMS service endpoints
"""

import requests
import json

def test_enhanced_service():
    """Test if enhanced service is running with correct endpoints"""
    print("🧪 Testing Enhanced SMS Service Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    # Test 1: Health endpoint
    print("\n1️⃣ Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Root endpoint
    print("\n2️⃣ Testing / endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: Send welcome endpoint
    print("\n3️⃣ Testing /send_welcome endpoint...")
    try:
        test_data = {
            'patient_id': 'TEST001',
            'name': 'Test Patient',
            'phone': '+250785379885',
            'surgery_type': 'kubagwa',
            'language': 'rw'
        }
        
        response = requests.post(f"{base_url}/send_welcome", 
                               json=test_data, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Send welcome endpoint working: {data.get('success')}")
        else:
            print(f"❌ Send welcome failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Send welcome error: {e}")
    
    # Test 4: Start conversation endpoint
    print("\n4️⃣ Testing /start_conversation endpoint...")
    try:
        test_data = {
            'patient_id': 'TEST001',
            'phone': '+250785379885',
            'patient_info': {
                'name': 'Test Patient',
                'surgery_type': 'kubagwa',
                'language': 'rw'
            }
        }
        
        response = requests.post(f"{base_url}/start_conversation", 
                               json=test_data, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Start conversation endpoint working: {data.get('success')}")
        else:
            print(f"❌ Start conversation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Start conversation error: {e}")
    
    print("\n🎉 Enhanced Service Test Complete!")
    return True

if __name__ == '__main__':
    test_enhanced_service()
