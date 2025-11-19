#!/usr/bin/env python3
# test_kinyarwanda_system.py
"""
Test script for PostCare Enhanced SMS Service with Kinyarwanda support
Demonstrates the conversation flow and AI features
"""

import sys
import os
import requests
import json
import time

# Add app directory to path
sys.path.append('./app')

# Test configuration
BASE_URL = 'http://localhost:5001'
TEST_PHONE = '+250785379885'
TEST_PATIENT = {
    'patient_id': 'PAT001',
    'name': 'Uwimana Jean',
    'phone': TEST_PHONE,
    'surgery_type': 'kubagwa mu nda',
    'surgery_date': '2024-01-15',
    'language': 'rw',
    'region': 'sector_1'
}

def test_health_check():
    """Test system health"""
    print("🏥 Testing system health...")
    try:
        response = requests.get(f'{BASE_URL}/health')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System is healthy: {data['service']}")
            print(f"   AI System: {data.get('ai_system', 'unknown')}")
            print(f"   Total Patients: {data.get('total_patients', 0)}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_welcome_sms():
    """Test welcome SMS in Kinyarwanda"""
    print("\n👋 Testing welcome SMS...")
    try:
        response = requests.post(f'{BASE_URL}/send_welcome', json=TEST_PATIENT)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Welcome SMS sent successfully")
                print(f"   Cost: {data.get('cost', 'N/A')}")
                print(f"   Network: {data.get('network', 'N/A')}")
                return True
            else:
                print(f"❌ Welcome SMS failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Welcome SMS request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Welcome SMS error: {e}")
        return False

def test_start_conversation():
    """Test starting a Kinyarwanda conversation"""
    print("\n💬 Testing conversation start...")
    try:
        payload = {
            'patient_id': TEST_PATIENT['patient_id'],
            'phone': TEST_PATIENT['phone'],
            'patient_info': TEST_PATIENT
        }
        response = requests.post(f'{BASE_URL}/start_conversation', json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Conversation started successfully")
                print(f"   Conversation ID: {data.get('conversation_id')}")
                print(f"   Menu sent: {data.get('menu_sent')}")
                return True
            else:
                print(f"❌ Conversation start failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Conversation start request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Conversation start error: {e}")
        return False

def test_conversation_status():
    """Test conversation status check"""
    print("\n📊 Testing conversation status...")
    try:
        response = requests.get(f'{BASE_URL}/conversation_status/{TEST_PHONE}')
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'active':
                print(f"✅ Active conversation found")
                print(f"   Patient: {data.get('patient_name')}")
                print(f"   State: {data.get('conversation_state')}")
                print(f"   Messages: {data.get('message_count', 0)}")
                return True
            else:
                print(f"⚠️ No active conversation: {data.get('status')}")
                return False
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def simulate_sms_webhook(message):
    """Simulate incoming SMS webhook"""
    print(f"\n📨 Simulating incoming SMS: '{message}'")
    try:
        payload = {
            'from': TEST_PHONE,
            'text': message,
            'id': f'test_{int(time.time())}'
        }
        response = requests.post(f'{BASE_URL}/webhook/sms', json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SMS processed: {data.get('status')}")
            if 'analysis' in data:
                analysis = data['analysis']
                print(f"   Severity: {analysis.get('severity', 'N/A')}")
                print(f"   Alerts: {analysis.get('alerts', [])}")
            return True
        else:
            print(f"❌ SMS processing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ SMS simulation error: {e}")
        return False

def test_emergency_alert():
    """Test emergency alert system"""
    print("\n🚨 Testing emergency alert...")
    try:
        payload = {
            'patient_info': TEST_PATIENT,
            'emergency_details': 'Ububabare bukabije cyane mu nda, sinshobora kugenda',
            'analysis': {
                'severity': 10,
                'alerts': ['HIGH_PAIN', 'EMERGENCY'],
                'recovery_prediction': 0.1
            }
        }
        response = requests.post(f'{BASE_URL}/emergency_alert', json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Emergency alert sent successfully")
                print(f"   Notifications sent: {data.get('total_notifications', 0)}")
                return True
            else:
                print(f"❌ Emergency alert failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Emergency alert request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Emergency alert error: {e}")
        return False

def test_alert_statistics():
    """Test alert statistics"""
    print("\n📈 Testing alert statistics...")
    try:
        response = requests.get(f'{BASE_URL}/alert_statistics')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Statistics retrieved successfully")
            alert_stats = data.get('alert_statistics', {})
            print(f"   Total alerts: {alert_stats.get('total_alerts', 0)}")
            print(f"   Success rate: {alert_stats.get('success_rate', 0)}%")
            
            conv_stats = data.get('conversation_statistics', {})
            print(f"   Active conversations: {conv_stats.get('total_active_conversations', 0)}")
            return True
        else:
            print(f"❌ Statistics request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Statistics error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 PostCare Enhanced SMS Service - Test Suite")
    print("=" * 60)
    
    results = []
    
    # Basic health check
    results.append(("Health Check", test_health_check()))
    
    # Test welcome SMS
    results.append(("Welcome SMS", test_welcome_sms()))
    
    # Test conversation features (only if enhanced features are available)
    results.append(("Start Conversation", test_start_conversation()))
    results.append(("Conversation Status", test_conversation_status()))
    
    # Simulate patient interactions
    print("\n🗣️ Simulating patient conversation flow...")
    
    # Patient selects health data collection (option 1)
    results.append(("Menu Selection 1", simulate_sms_webhook("1")))
    time.sleep(1)
    
    # Patient enters pain level
    results.append(("Pain Level", simulate_sms_webhook("6")))
    time.sleep(1)
    
    # Patient enters wound healing
    results.append(("Wound Healing", simulate_sms_webhook("7")))
    time.sleep(1)
    
    # Patient enters temperature
    results.append(("Temperature", simulate_sms_webhook("37.5")))
    time.sleep(1)
    
    # Patient enters mobility
    results.append(("Mobility", simulate_sms_webhook("8")))
    time.sleep(1)
    
    # Patient asks a question in free conversation
    results.append(("Free Question", simulate_sms_webhook("Ni gute nshobora kugabanya ububabare?")))
    time.sleep(1)
    
    # Test emergency scenario
    results.append(("Emergency SMS", simulate_sms_webhook("Mfite ububabare bukabije cyane, sinshobora kugenda!")))
    
    # Test alert systems
    results.append(("Emergency Alert", test_emergency_alert()))
    results.append(("Alert Statistics", test_alert_statistics()))
    
    # Print results summary
    print("\n📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20}: {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! PostCare Enhanced SMS Service is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the system configuration.")
    
    return passed == total

if __name__ == '__main__':
    # Check if server is running
    try:
        requests.get(f'{BASE_URL}/health', timeout=5)
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to PostCare SMS Service.")
        print(f"   Please make sure the server is running on {BASE_URL}")
        print("   Run: python app/enhanced_sms_service.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test setup error: {e}")
        sys.exit(1)



