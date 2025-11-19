#!/usr/bin/env python3
# test_real_sms.py
"""
Test PostCare Enhanced SMS Service with real phone numbers
Demonstrates actual SMS sending capabilities
"""

import requests
import json
import time
import sys

# Test configuration
BASE_URL = 'http://localhost:5001'

def test_sms_sending():
    """Test basic SMS sending"""
    print("📱 Testing Basic SMS Sending")
    print("=" * 50)
    
    # Get phone number from user
    phone = input("Enter your phone number (e.g., +250785379885): ").strip()
    
    if not phone:
        print("❌ No phone number provided")
        return False
    
    # Format phone number
    if not phone.startswith('+'):
        if phone.startswith('0'):
            phone = '+250' + phone[1:]
        elif phone.startswith('250'):
            phone = '+' + phone
        else:
            phone = '+250' + phone
    
    print(f"📞 Sending test SMS to: {phone}")
    
    try:
        response = requests.post(f'{BASE_URL}/test_sms', json={
            'phone': phone,
            'message': 'Hello from PostCare+ SMS Service! 🏥 This is a test message. Reply if you received this.'
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ SMS sent successfully!")
                print(f"   Cost: {data.get('cost', 'N/A')}")
                print(f"   Message ID: {data.get('messageId', 'N/A')}")
                print(f"   Network: {data.get('network', 'N/A')}")
                return True
            else:
                print(f"❌ SMS failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_welcome_message():
    """Test welcome message in Kinyarwanda"""
    print("\n👋 Testing Welcome Message in Kinyarwanda")
    print("=" * 50)
    
    # Get patient details
    name = input("Enter patient name: ").strip() or "Test Patient"
    phone = input("Enter phone number: ").strip()
    surgery = input("Enter surgery type (in Kinyarwanda, e.g., 'kubagwa mu nda'): ").strip() or "kubagwa"
    
    if not phone:
        print("❌ No phone number provided")
        return False
    
    # Format phone number
    if not phone.startswith('+'):
        if phone.startswith('0'):
            phone = '+250' + phone[1:]
        elif phone.startswith('250'):
            phone = '+' + phone
        else:
            phone = '+250' + phone
    
    print(f"📤 Sending welcome message to {name} at {phone}")
    
    try:
        response = requests.post(f'{BASE_URL}/send_welcome', json={
            'patient_id': 'TEST001',
            'name': name,
            'phone': phone,
            'surgery_type': surgery,
            'language': 'rw'
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Welcome SMS sent successfully!")
                print(f"   Patient will receive welcome message in Kinyarwanda")
                return True
            else:
                print(f"❌ Welcome SMS failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_conversation_start():
    """Test starting a Kinyarwanda conversation"""
    print("\n💬 Testing Conversation Start")
    print("=" * 50)
    
    name = input("Enter patient name: ").strip() or "Test Patient"
    phone = input("Enter phone number: ").strip()
    
    if not phone:
        print("❌ No phone number provided")
        return False
    
    # Format phone number
    if not phone.startswith('+'):
        if phone.startswith('0'):
            phone = '+250' + phone[1:]
        elif phone.startswith('250'):
            phone = '+' + phone
        else:
            phone = '+250' + phone
    
    print(f"🚀 Starting conversation with {name} at {phone}")
    
    try:
        response = requests.post(f'{BASE_URL}/start_conversation', json={
            'patient_id': 'TEST002',
            'phone': phone,
            'patient_info': {
                'name': name,
                'surgery_type': 'kubagwa mu nda',
                'language': 'rw',
                'region': 'test_sector'
            }
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Conversation started successfully!")
                print(f"   Conversation ID: {data.get('conversation_id')}")
                print(f"   Menu sent: {data.get('menu_sent')}")
                print("📱 Patient should receive main menu in Kinyarwanda")
                return True
            else:
                print(f"❌ Conversation start failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_emergency_alert():
    """Test emergency alert system"""
    print("\n🚨 Testing Emergency Alert System")
    print("=" * 50)
    
    confirm = input("This will send emergency alerts to healthcare providers. Continue? (y/N): ").strip().lower()
    if confirm != 'y':
        print("⏭️ Emergency test skipped")
        return True
    
    name = input("Enter patient name: ").strip() or "Test Patient"
    phone = input("Enter patient phone: ").strip()
    emergency_details = input("Enter emergency details (in Kinyarwanda): ").strip() or "Ibibazo by'ihutirwa"
    
    if not phone:
        print("❌ No phone number provided")
        return False
    
    # Format phone number
    if not phone.startswith('+'):
        if phone.startswith('0'):
            phone = '+250' + phone[1:]
        elif phone.startswith('250'):
            phone = '+' + phone
        else:
            phone = '+250' + phone
    
    print(f"🚨 Sending emergency alert for {name}")
    
    try:
        response = requests.post(f'{BASE_URL}/emergency_alert', json={
            'patient_info': {
                'name': name,
                'phone': phone,
                'surgery_type': 'kubagwa mu nda',
                'id': 'TEST_EMERGENCY'
            },
            'emergency_details': emergency_details,
            'analysis': {
                'severity': 9,
                'alerts': ['EMERGENCY', 'HIGH_PAIN'],
                'recovery_prediction': 0.2
            }
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Emergency alerts sent successfully!")
                alerts = data.get('emergency_alerts_sent', {})
                print(f"   Total notifications: {data.get('total_notifications', 0)}")
                for provider_type, alert_info in alerts.items():
                    status = "✅" if alert_info.get('sent') else "❌"
                    print(f"   {status} {alert_info.get('provider')} ({alert_info.get('phone')})")
                return True
            else:
                print(f"❌ Emergency alert failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def simulate_incoming_sms():
    """Simulate incoming SMS from patient"""
    print("\n📨 Testing Incoming SMS Processing")
    print("=" * 50)
    
    phone = input("Enter patient phone number: ").strip()
    message = input("Enter patient message (try '1' for menu or a Kinyarwanda message): ").strip()
    
    if not phone or not message:
        print("❌ Phone number and message required")
        return False
    
    # Format phone number
    if not phone.startswith('+'):
        if phone.startswith('0'):
            phone = '+250' + phone[1:]
        elif phone.startswith('250'):
            phone = '+' + phone
        else:
            phone = '+250' + phone
    
    print(f"📨 Simulating SMS from {phone}: '{message}'")
    
    try:
        response = requests.post(f'{BASE_URL}/webhook/sms', json={
            'from': phone,
            'text': message,
            'id': f'test_{int(time.time())}'
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SMS processed: {data.get('status')}")
            
            if 'analysis' in data:
                analysis = data['analysis']
                print(f"   Health Analysis:")
                print(f"     Severity: {analysis.get('severity', 'N/A')}")
                print(f"     Alerts: {analysis.get('alerts', [])}")
                print(f"     Recovery: {analysis.get('recovery_prediction', 0):.0%}")
            
            if data.get('emergency_detected'):
                print("🚨 EMERGENCY DETECTED - Alerts sent to providers!")
                
            return True
        else:
            print(f"❌ SMS processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test menu"""
    print("🧪 PostCare Enhanced SMS Service - Real Phone Testing")
    print("=" * 70)
    print("⚠️  WARNING: This will send actual SMS messages and may incur costs!")
    print("=" * 70)
    
    # Check if server is running
    try:
        response = requests.get(f'{BASE_URL}/health', timeout=5)
        if response.status_code != 200:
            print("❌ PostCare SMS Service is not responding properly")
            sys.exit(1)
        
        health_data = response.json()
        print(f"✅ Service Status: {health_data.get('status')}")
        print(f"   AI System: {health_data.get('ai_system', 'unknown')}")
        print(f"   Service is running and ready for SMS testing!")
        print()
        
    except Exception as e:
        print(f"❌ Cannot connect to PostCare SMS Service at {BASE_URL}")
        print(f"   Error: {e}")
        print("   Please make sure the service is running:")
        print("   python app/enhanced_sms_service.py")
        sys.exit(1)
    
    while True:
        print("\n🧪 Choose a test:")
        print("1. 📱 Basic SMS Test")
        print("2. 👋 Welcome Message (Kinyarwanda)")
        print("3. 💬 Start Conversation (Menu)")
        print("4. 📨 Simulate Incoming SMS")
        print("5. 🚨 Emergency Alert Test")
        print("6. 📊 View System Statistics")
        print("0. ❌ Exit")
        
        choice = input("\nEnter choice (0-6): ").strip()
        
        if choice == '0':
            print("👋 Testing completed!")
            break
        elif choice == '1':
            test_sms_sending()
        elif choice == '2':
            test_welcome_message()
        elif choice == '3':
            test_conversation_start()
        elif choice == '4':
            simulate_incoming_sms()
        elif choice == '5':
            test_emergency_alert()
        elif choice == '6':
            try:
                response = requests.get(f'{BASE_URL}/statistics')
                if response.status_code == 200:
                    stats = response.json()
                    print(f"\n📊 System Statistics:")
                    print(f"   SMS sent today: {stats.get('sms_statistics', {}).get('sms_sent_today', 0)}")
                    print(f"   Total cost today: {stats.get('sms_statistics', {}).get('total_cost_today', 0)}")
                    print(f"   Total patients: {stats.get('patient_statistics', {}).get('total_patients', 0)}")
                else:
                    print("❌ Could not fetch statistics")
            except Exception as e:
                print(f"❌ Statistics error: {e}")
        else:
            print("❌ Invalid choice")
        
        input("\nPress Enter to continue...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")



