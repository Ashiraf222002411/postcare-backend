#!/usr/bin/env python3
"""
Test Termux Gateway Integration with PostCare Backend
"""

import requests
import json
import time

def test_gateway_integration():
    """Test the complete gateway integration"""
    print("🧪 Testing Termux Gateway Integration")
    print("=" * 50)
    
    backend_url = "http://172.20.10.4:5001/webhook/sms"
    api_key = "postcare_backend_key_2024"
    
    # Test 1: Check backend connectivity
    print("\n1️⃣ Testing backend connectivity...")
    try:
        response = requests.get("http://172.20.10.4:5001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is accessible")
        else:
            print(f"❌ Backend not responding: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test 2: Test SMS webhook endpoint
    print("\n2️⃣ Testing SMS webhook endpoint...")
    test_sms = {
        'from': '+250785379885',
        'text': '1',  # Patient selects option 1
        'id': 'test_gateway_001'
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': api_key
    }
    
    try:
        response = requests.post(
            backend_url,
            json=test_sms,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SMS webhook working: {result.get('status')}")
            print(f"   Send reply: {result.get('send_reply')}")
        else:
            print(f"❌ SMS webhook failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ SMS webhook error: {e}")
        return False
    
    # Test 3: Test conversation flow
    print("\n3️⃣ Testing conversation flow...")
    conversation_steps = [
        ('1', 'Patient selects Health Data'),
        ('6', 'Patient enters pain level'),
        ('7', 'Patient enters wound healing'),
        ('37.5', 'Patient enters temperature'),
        ('8', 'Patient enters mobility')
    ]
    
    for i, (message, description) in enumerate(conversation_steps):
        print(f"   Step {i+1}: {description}")
        
        test_message = {
            'from': '+250785379885',
            'text': message,
            'id': f'test_gateway_{i+1:03d}'
        }
        
        try:
            response = requests.post(
                backend_url,
                json=test_message,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Processed: {result.get('status')}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)
    
    print("\n🎉 Gateway Integration Test Complete!")
    print("=" * 50)
    print("✅ Backend is ready to receive SMS from Termux gateway")
    print("📱 Deploy sms_monitor.py to your Termux device")
    print("🔄 Patients can now reply to PostCare messages!")
    
    return True

if __name__ == '__main__':
    test_gateway_integration()
