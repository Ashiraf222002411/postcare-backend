#!/usr/bin/env python3
"""
Simple test for PostCare SMS Service
"""

import requests
import json

def test_service():
    """Test basic service connectivity"""
    print("🧪 Testing PostCare SMS Service")
    print("=" * 50)
    
    try:
        # Test basic endpoint
        response = requests.get('http://localhost:5001/', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service is running: {data.get('status')}")
        else:
            print(f"❌ Service returned status: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Service timeout - may be overloaded")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to service")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test incoming SMS endpoint
    try:
        print("\n📨 Testing incoming SMS endpoint...")
        test_data = {
            'from': '+250785379885',
            'text': '5'
        }
        
        response = requests.post('http://localhost:5001/incoming-sms', 
                              json=test_data, 
                              timeout=10)
        
        if response.status_code == 200:
            print("✅ Incoming SMS endpoint working")
            return True
        else:
            print(f"❌ Incoming SMS failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Incoming SMS test error: {e}")
        return False

if __name__ == '__main__':
    test_service()
