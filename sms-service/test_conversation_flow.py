#!/usr/bin/env python3
"""
Test the full USSD-like conversation flow
"""

import requests
import json
import time

def test_full_conversation_flow():
    """Test the complete patient conversation flow"""
    print("🧪 Testing Full USSD-like Conversation Flow")
    print("=" * 60)
    
    base_url = "http://localhost:5001"
    test_phone = "+250785379885"
    patient_name = "Test Patient"
    
    # Step 1: Start conversation
    print("\n1️⃣ Starting conversation...")
    try:
        response = requests.post(f"{base_url}/start_conversation", json={
            'patient_id': 'TEST_CONV_001',
            'phone': test_phone,
            'patient_info': {
                'name': patient_name,
                'surgery_type': 'kubagwa mu nda',
                'language': 'rw'
            }
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conversation started: {data.get('success')}")
            print(f"   Menu sent: {data.get('menu_sent')}")
        else:
            print(f"❌ Failed to start conversation: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error starting conversation: {e}")
        return False
    
    # Step 2: Patient selects option 1 (Health Data)
    print("\n2️⃣ Patient selects option 1 (Health Data)...")
    try:
        response = requests.post(f"{base_url}/webhook/sms", json={
            'from': test_phone,
            'text': '1',
            'id': 'test_1'
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response processed: {data.get('status')}")
        else:
            print(f"❌ Failed to process response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error processing response: {e}")
    
    time.sleep(1)
    
    # Step 3: Patient enters pain level
    print("\n3️⃣ Patient enters pain level (6)...")
    try:
        response = requests.post(f"{base_url}/webhook/sms", json={
            'from': test_phone,
            'text': '6',
            'id': 'test_2'
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pain level processed: {data.get('status')}")
        else:
            print(f"❌ Failed to process pain level: {response.status_code}")
    except Exception as e:
        print(f"❌ Error processing pain level: {e}")
    
    time.sleep(1)
    
    # Step 4: Patient enters wound healing
    print("\n4️⃣ Patient enters wound healing (7)...")
    try:
        response = requests.post(f"{base_url}/webhook/sms", json={
            'from': test_phone,
            'text': '7',
            'id': 'test_3'
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Wound healing processed: {data.get('status')}")
        else:
            print(f"❌ Failed to process wound healing: {response.status_code}")
    except Exception as e:
        print(f"❌ Error processing wound healing: {e}")
    
    time.sleep(1)
    
    # Step 5: Patient enters temperature
    print("\n5️⃣ Patient enters temperature (37.5)...")
    try:
        response = requests.post(f"{base_url}/webhook/sms", json={
            'from': test_phone,
            'text': '37.5',
            'id': 'test_4'
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Temperature processed: {data.get('status')}")
        else:
            print(f"❌ Failed to process temperature: {response.status_code}")
    except Exception as e:
        print(f"❌ Error processing temperature: {e}")
    
    time.sleep(1)
    
    # Step 6: Patient enters mobility
    print("\n6️⃣ Patient enters mobility (8)...")
    try:
        response = requests.post(f"{base_url}/webhook/sms", json={
            'from': test_phone,
            'text': '8',
            'id': 'test_5'
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mobility processed: {data.get('status')}")
            if 'analysis' in data:
                analysis = data['analysis']
                print(f"   Analysis: Severity {analysis.get('severity')}, Recovery {analysis.get('recovery_prediction', 0):.0%}")
        else:
            print(f"❌ Failed to process mobility: {response.status_code}")
    except Exception as e:
        print(f"❌ Error processing mobility: {e}")
    
    # Step 7: Patient asks a question
    print("\n7️⃣ Patient asks a question...")
    try:
        response = requests.post(f"{base_url}/webhook/sms", json={
            'from': test_phone,
            'text': 'Ni gute nshobora kugabanya ububabare?',
            'id': 'test_6'
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Question processed: {data.get('status')}")
        else:
            print(f"❌ Failed to process question: {response.status_code}")
    except Exception as e:
        print(f"❌ Error processing question: {e}")
    
    print("\n🎉 Conversation Flow Test Complete!")
    print("=" * 60)
    print("✅ Full USSD-like conversation flow tested")
    print("📱 Check your phone for the SMS messages!")
    
    return True

if __name__ == '__main__':
    test_full_conversation_flow()
