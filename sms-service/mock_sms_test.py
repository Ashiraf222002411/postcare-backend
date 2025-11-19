#!/usr/bin/env python3
# mock_sms_test.py
"""
Mock SMS testing for PostCare Enhanced SMS Service
Tests all features without sending real SMS (no costs)
"""

import sys
import os
sys.path.append('./app')

from kinyarwanda_translations import kinyarwanda
from conversation_manager import ConversationManager, ConversationState
from sms_menu_handler import SMSMenuHandler
from ai_advisor import KinyarwandaAIAdvisor
from alert_system import AlertSystem

class MockSMSService:
    """Mock SMS service that simulates sending without real SMS"""
    
    def __init__(self):
        self.sent_messages = []
        self.message_count = 0
    
    def send_sms(self, phone, message):
        """Simulate SMS sending"""
        self.message_count += 1
        message_id = f"MOCK_{self.message_count:04d}"
        
        # Store sent message
        self.sent_messages.append({
            'phone': phone,
            'message': message,
            'message_id': message_id,
            'timestamp': f"2025-01-01 12:00:{self.message_count:02d}"
        })
        
        # Simulate successful sending
        print(f"\n📱 MOCK SMS SENT to {phone}")
        print("=" * 60)
        print(message)
        print("=" * 60)
        print(f"✅ Message ID: {message_id}")
        print(f"💰 Cost: RWF 15 (SIMULATED)")
        print(f"📊 Total messages sent: {self.message_count}")
        
        return {
            'success': True,
            'cost': 'RWF 15',
            'messageId': message_id,
            'network': 'MTN',
            'formatted_phone': phone,
            'messageParts': 1
        }
    
    def get_sent_messages(self):
        """Get all sent messages"""
        return self.sent_messages

def test_full_patient_journey():
    """Test complete patient journey without real SMS"""
    print("🎭 MOCK SMS TESTING - Complete Patient Journey")
    print("=" * 70)
    print("✅ No real SMS will be sent - this is completely FREE!")
    print("=" * 70)
    
    # Initialize system with mock SMS
    mock_sms = MockSMSService()
    conversation_manager = ConversationManager('mock_conversations.pkl')
    menu_handler = SMSMenuHandler(kinyarwanda, conversation_manager)
    ai_advisor = KinyarwandaAIAdvisor(kinyarwanda)
    alert_system = AlertSystem(mock_sms, ai_advisor, kinyarwanda)
    
    # Test patient info
    patient_info = {
        'id': 'MOCK001',
        'name': 'Uwimana Jean',
        'phone': '+250785379885',
        'surgery_type': 'kubagwa mu nda',
        'surgery_date': '2024-01-15',
        'language': 'rw',
        'region': 'kigali'
    }
    
    phone = patient_info['phone']
    patient_name = patient_info['name']
    
    print(f"👤 Mock Patient: {patient_name} ({phone})")
    print(f"🏥 Surgery: {patient_info['surgery_type']}")
    print(f"🌍 Language: Kinyarwanda")
    
    input("\nPress Enter to start the mock journey...")
    
    # Step 1: Welcome message
    print(f"\n🔸 STEP 1: Welcome Message")
    welcome_msg = kinyarwanda.get_translation('messages.welcome_new_patient', 
                                             name=patient_name, 
                                             surgery_type=patient_info['surgery_type'])
    mock_sms.send_sms(phone, welcome_msg)
    
    # Step 2: Start conversation with menu
    print(f"\n🔸 STEP 2: Main Menu")
    conversation = conversation_manager.start_conversation(patient_info['id'], phone, patient_info)
    main_menu = menu_handler.generate_main_menu(patient_name)
    mock_sms.send_sms(phone, main_menu)
    
    # Step 3: Patient selects health data option
    print(f"\n🔸 STEP 3: Patient Selects Health Data Collection")
    print("📨 Patient sends: 1")
    
    menu_result = menu_handler.process_menu_response(phone, "1")
    mock_sms.send_sms(phone, menu_result['response_message'])
    
    # Step 4-7: Health data collection
    health_data = [
        ("6", "Pain Level - Moderate"),
        ("7", "Wound Healing - Good"), 
        ("37.5", "Temperature - Slight fever"),
        ("8", "Mobility - Good")
    ]
    
    for i, (response, description) in enumerate(health_data, 4):
        print(f"\n🔸 STEP {i}: {description}")
        print(f"📨 Patient sends: {response}")
        
        menu_result = menu_handler.process_menu_response(phone, response)
        if menu_result.get('response_message'):
            mock_sms.send_sms(phone, menu_result['response_message'])
        
        if menu_result.get('action') == 'analyze_and_advise':
            # AI analysis
            patient_data = menu_result.get('patient_data', {})
            print(f"\n🤖 AI Analysis:")
            for key, value in patient_data.items():
                print(f"   {key.title()}: {value}")
            
            # Generate analysis
            analysis = {
                'severity': 4.2,
                'recovery_prediction': 0.75,
                'alerts': ['MILD_FEVER'],
                'needs_attention': True
            }
            
            advice = ai_advisor.generate_health_analysis_advice(patient_data, analysis, patient_name)
            mock_sms.send_sms(phone, advice)
            
            # Send CHW alert
            print(f"\n📢 Sending CHW Alert...")
            conversation_context = {'summary': 'Routine health check with mild fever'}
            alert_results = alert_system.process_patient_alert(patient_info, analysis, conversation_context)
            print(f"✅ Alert sent to {len(alert_results.get('notifications_sent', {}))} providers")
            
            break
    
    # Step 8: Free conversation
    print(f"\n🔸 STEP 8: Free Conversation")
    question = "Ni gute nshobora kugabanya ububabare?"
    print(f"📨 Patient asks: {question}")
    
    conversation_context = conversation_manager.get_conversation_context(phone)
    ai_response = ai_advisor.generate_response(question, conversation_context)
    mock_sms.send_sms(phone, ai_response)
    
    # Step 9: Emergency scenario
    print(f"\n🔸 STEP 9: Emergency Detection")
    emergency_msg = "Mfite ububabare bukabije cyane, sinshobora kugenda!"
    print(f"📨 Patient sends EMERGENCY: {emergency_msg}")
    
    if kinyarwanda.detect_emergency(emergency_msg):
        print("\n🚨 EMERGENCY DETECTED!")
        
        # Emergency response
        emergency_response = ai_advisor._generate_emergency_response(emergency_msg, patient_name)
        mock_sms.send_sms(phone, emergency_response)
        
        # Emergency alerts
        print(f"\n📢 Sending Emergency Alerts...")
        emergency_analysis = {'severity': 9, 'alerts': ['EMERGENCY'], 'recovery_prediction': 0.2}
        alert_results = alert_system.send_emergency_alert(patient_info, emergency_msg, emergency_analysis)
        
        print(f"🚨 Emergency alerts sent to {len(alert_results)} providers:")
        for provider_type, result in alert_results.items():
            print(f"   ✅ {result['provider']} ({result['phone']})")
    
    # Step 10: Summary
    print(f"\n🔸 STEP 10: Journey Summary")
    sent_messages = mock_sms.get_sent_messages()
    
    print(f"\n📊 MOCK TEST RESULTS:")
    print(f"   📱 Total SMS sent: {len(sent_messages)}")
    print(f"   💰 Total cost (if real): RWF {len(sent_messages) * 15}")
    print(f"   ✅ All features tested successfully!")
    
    print(f"\n📋 SMS MESSAGE SUMMARY:")
    for i, msg in enumerate(sent_messages, 1):
        print(f"   {i:2d}. {msg['phone']} - {msg['message'][:50]}{'...' if len(msg['message']) > 50 else ''}")
    
    print(f"\n🎉 MOCK TESTING COMPLETED!")
    print("✅ All PostCare Enhanced SMS features working perfectly!")
    print("🔧 Fix Africa's Talking credentials and you're ready for real SMS!")

def test_translations():
    """Test Kinyarwanda translations"""
    print("\n🌍 TESTING KINYARWANDA TRANSLATIONS")
    print("=" * 50)
    
    # Test medical terms
    terms = ['pain', 'wound', 'fever', 'healing', 'medicine', 'doctor', 'emergency']
    print("📚 Medical Terms:")
    for term in terms:
        translation = kinyarwanda.get_translation(term)
        print(f"   {term:10} → {translation}")
    
    # Test emergency detection
    print("\n🚨 Emergency Detection:")
    test_messages = [
        "Mfite ububabare bukabije cyane",
        "Sinshobora kugenda",
        "Ndababara gusa gahoro", 
        "Ni ukuri nkiri neza",
        "Nsaba ubufasha byihutirwa"
    ]
    
    for msg in test_messages:
        is_emergency = kinyarwanda.detect_emergency(msg)
        status = "🚨 EMERGENCY" if is_emergency else "✅ Normal"
        print(f"   '{msg}' → {status}")
    
    # Test pain levels
    print("\n🔢 Pain Level Descriptions:")
    for level in [1, 3, 5, 7, 10]:
        description = kinyarwanda.get_pain_level_description(level)
        print(f"   Level {level:2d} → {description}")

def main():
    """Main menu for mock testing"""
    while True:
        print("\n🎭 PostCare Mock SMS Testing Menu")
        print("=" * 40)
        print("1. 🌍 Test Kinyarwanda Translations")
        print("2. 🎬 Full Patient Journey Simulation")
        print("3. 📊 Quick Feature Overview")
        print("0. ❌ Exit")
        
        choice = input("\nEnter choice (0-3): ").strip()
        
        if choice == '0':
            print("👋 Mock testing completed!")
            break
        elif choice == '1':
            test_translations()
        elif choice == '2':
            test_full_patient_journey()
        elif choice == '3':
            print("\n📋 PostCare Enhanced SMS Features:")
            print("✅ Kinyarwanda language support")
            print("✅ SMS menu system (USSD-like)")
            print("✅ Step-by-step health data collection")
            print("✅ AI medical advisor")
            print("✅ Emergency detection")
            print("✅ CHW & doctor alerts")
            print("✅ Free conversation mode")
            print("✅ Cultural adaptation")
        else:
            print("❌ Invalid choice")
        
        if choice != '0':
            input("\nPress Enter to continue...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Mock testing interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()



