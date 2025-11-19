#!/usr/bin/env python3
"""
Test Real Patient Conversation in Production
"""

import requests
import json
import time

def test_real_patient_conversation():
    """Test a real patient conversation flow"""
    print("=" * 70)
    print("🧪 Testing Real Patient Conversation - Production Mode")
    print("=" * 70)
    
    base_url = "http://localhost:5001"
    
    # Test patient info
    patient_name = input("Enter patient name (or press Enter for 'Test Patient'): ").strip() or "Test Patient"
    patient_phone = input("Enter patient phone (e.g., +250785379885): ").strip()
    
    if not patient_phone:
        print("❌ Phone number required")
        return False
    
    print(f"\n📱 Starting conversation with {patient_name}")
    print(f"📞 Phone: {patient_phone}")
    print("=" * 70)
    
    # Step 1: Start conversation
    print("\n1️⃣ Starting conversation...")
    try:
        response = requests.post(f"{base_url}/start_conversation", json={
            'patient_id': 'PROD_TEST_001',
            'phone': patient_phone,
            'patient_info': {
                'name': patient_name,
                'surgery_type': 'kubagwa mu nda',
                'language': 'rw',
                'region': 'Kigali'
            }
        })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Conversation started!")
            print(f"   Status: {data.get('status')}")
            print(f"   Menu sent: {data.get('menu_sent')}")
            print("\n📱 Patient should receive USSD menu in Kinyarwanda")
            print("\n" + "=" * 70)
        else:
            print(f"❌ Failed to start conversation: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Guide for testing
    print("\n📋 Next Steps:")
    print("=" * 70)
    print("1. Patient should receive the main menu in Kinyarwanda")
    print("2. Patient can reply with menu numbers (1-5)")
    print("3. Test conversation flow:")
    print("   - Reply '1' for Health Data collection")
    print("   - Or reply '2' to ask a health question")
    print("   - Or reply any Kinyarwanda question")
    print("=" * 70)
    
    # Option to simulate patient responses
    simulate = input("\nSimulate patient responses? (y/n): ").strip().lower()
    
    if simulate == 'y':
        # Simulate patient responses
        steps = [
            ('1', 'Patient selects Health Data'),
            ('6', 'Pain level: 6/10'),
            ('7', 'Wound healing: 7/10'),
            ('37.5', 'Temperature: 37.5°C'),
            ('8', 'Mobility: 8/10')
        ]
        
        print("\n🔄 Simulating patient responses...")
        for message, description in steps:
            print(f"\n   {description}...")
            
            try:
                response = requests.post(f"{base_url}/webhook/sms", json={
                    'from': patient_phone,
                    'text': message,
                    'id': f'real_test_{message}'
                })
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Status: {data.get('status')}")
                else:
                    print(f"   ❌ Failed: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            time.sleep(2)
        
        print("\n🎉 Simulation complete!")
        print("📱 Check patient's phone for SMS responses")
    
    print("\n" + "=" * 70)
    print("✅ Production System is Ready!")
    print("📱 Patients can now have real conversations via SMS")
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    test_real_patient_conversation()


