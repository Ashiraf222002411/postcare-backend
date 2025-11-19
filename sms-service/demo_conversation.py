#!/usr/bin/env python3
# demo_conversation.py
"""
Interactive demo of PostCare Enhanced SMS Service with Kinyarwanda support
Shows conversation flow without actually sending SMS
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
    """Mock SMS service for demo purposes"""
    def send_sms(self, phone, message):
        print(f"\n📱 SMS to {phone}:")
        print("=" * 60)
        print(message)
        print("=" * 60)
        return {'success': True, 'cost': 'RWF 15', 'messageId': 'demo123'}

def demo_conversation_flow():
    """Demonstrate the complete conversation flow"""
    print("🏥 PostCare Enhanced SMS Service - Kinyarwanda Demo")
    print("=" * 80)
    
    # Initialize components
    sms_service = MockSMSService()
    conversation_manager = ConversationManager('demo_conversations.pkl')
    menu_handler = SMSMenuHandler(kinyarwanda, conversation_manager)
    ai_advisor = KinyarwandaAIAdvisor(kinyarwanda)
    alert_system = AlertSystem(sms_service, ai_advisor, kinyarwanda)
    
    # Demo patient
    patient_info = {
        'id': 'DEMO001',
        'name': 'Uwimana Jean',
        'phone': '+250785379885',
        'surgery_type': 'kubagwa mu nda',
        'surgery_date': '2024-01-15',
        'language': 'rw',
        'region': 'sector_1'
    }
    
    phone = patient_info['phone']
    patient_name = patient_info['name']
    
    print(f"👤 Demo Patient: {patient_name} ({phone})")
    print(f"🏥 Surgery: {patient_info['surgery_type']}")
    print(f"🌍 Language: Kinyarwanda")
    
    # Step 1: Start conversation and send welcome
    print(f"\n🔸 STEP 1: Welcome & Menu")
    conversation = conversation_manager.start_conversation(patient_info['id'], phone, patient_info)
    main_menu = menu_handler.generate_main_menu(patient_name)
    sms_service.send_sms(phone, main_menu)
    
    # Step 2: Patient selects health data option (1)
    print(f"\n🔸 STEP 2: Patient selects option 1 (Health Data)")
    print("📨 Patient sends: 1")
    
    menu_result = menu_handler.process_menu_response(phone, "1")
    sms_service.send_sms(phone, menu_result['response_message'])
    
    # Step 3: Collect health data step by step
    health_responses = ["6", "7", "37.5", "8"]
    health_labels = ["Pain Level", "Wound Healing", "Temperature", "Mobility"]
    
    for i, (response, label) in enumerate(zip(health_responses, health_labels), 3):
        print(f"\n🔸 STEP {i}: Patient enters {label}")
        print(f"📨 Patient sends: {response}")
        
        menu_result = menu_handler.process_menu_response(phone, response)
        if menu_result.get('response_message'):
            sms_service.send_sms(phone, menu_result['response_message'])
        
        if menu_result.get('action') == 'analyze_and_advise':
            # Generate AI analysis and advice
            patient_data = menu_result.get('patient_data', {})
            print(f"\n🤖 AI Analysis of Health Data:")
            print(f"   Pain: {patient_data.get('pain')}/10")
            print(f"   Wound: {patient_data.get('wound')}/10")
            print(f"   Temperature: {patient_data.get('temperature')}°C")
            print(f"   Mobility: {patient_data.get('mobility')}/10")
            
            # Simulate simple analysis
            analysis = {
                'severity': 3.5,
                'recovery_prediction': 0.78,
                'alerts': [],
                'needs_attention': False
            }
            
            # Generate advice
            advice = ai_advisor.generate_health_analysis_advice(patient_data, analysis, patient_name)
            sms_service.send_sms(phone, advice)
            break
    
    # Step 7: Free conversation mode
    print(f"\n🔸 STEP 7: Free Conversation - Patient asks question")
    question = "Ni gute nshobora kugabanya ububabare?"
    print(f"📨 Patient sends: {question}")
    
    # Generate AI response to question
    conversation_context = conversation_manager.get_conversation_context(phone)
    ai_response = ai_advisor.generate_response(question, conversation_context)
    sms_service.send_sms(phone, ai_response)
    
    # Step 8: Emergency scenario
    print(f"\n🔸 STEP 8: Emergency Detection")
    emergency_message = "Mfite ububabare bukabije cyane, sinshobora kugenda!"
    print(f"📨 Patient sends: {emergency_message}")
    
    # Detect and handle emergency
    if kinyarwanda.detect_emergency(emergency_message):
        print("\n🚨 EMERGENCY DETECTED!")
        emergency_response = ai_advisor._generate_emergency_response(emergency_message, patient_name)
        sms_service.send_sms(phone, emergency_response)
        
        # Send alerts to healthcare providers
        print("\n📢 Sending alerts to healthcare providers...")
        emergency_analysis = {'severity': 9, 'alerts': ['EMERGENCY'], 'recovery_prediction': 0.2}
        alert_results = alert_system.send_emergency_alert(patient_info, emergency_message, emergency_analysis)
        
        print(f"✅ Emergency alerts sent to {len(alert_results)} providers:")
        for provider_type, result in alert_results.items():
            status = "✅" if result['sent'] else "❌"
            print(f"   {status} {result['provider']} ({result['phone']})")
    
    # Step 9: CHW Report
    print(f"\n🔸 STEP 9: Community Health Worker Report")
    analysis = {'severity': 4, 'alerts': ['MEDIUM_CONCERN'], 'recovery_prediction': 0.65}
    conversation_summary = {'summary': 'Patient reported moderate pain, asked about pain management'}
    cwh_report = ai_advisor.generate_cwh_report(patient_info, conversation_summary, analysis)
    
    print("\n📋 CHW Report Generated:")
    print(cwh_report)
    
    # Demo summary
    print(f"\n🎉 DEMO COMPLETED!")
    print("=" * 80)
    print("✅ Features Demonstrated:")
    print("   • Kinyarwanda language support")
    print("   • SMS menu navigation (USSD-like)")
    print("   • Step-by-step health data collection")
    print("   • AI-powered medical advice")
    print("   • Free conversation mode")
    print("   • Emergency detection and alerts")
    print("   • Healthcare provider notifications")
    print("   • CHW reporting system")
    print("=" * 80)

def demo_translations():
    """Demo the Kinyarwanda translation system"""
    print("\n🌍 KINYARWANDA TRANSLATIONS DEMO")
    print("=" * 50)
    
    # Medical terms
    terms = ['pain', 'wound', 'fever', 'healing', 'medicine', 'doctor']
    print("📚 Medical Terms:")
    for term in terms:
        translation = kinyarwanda.get_translation(term)
        print(f"   {term} → {translation}")
    
    # Pain levels
    print("\n🔢 Pain Level Descriptions:")
    for level in [1, 5, 7, 10]:
        description = kinyarwanda.get_pain_level_description(level)
        print(f"   Level {level} → {description}")
    
    # Emergency detection
    print("\n🚨 Emergency Detection:")
    test_messages = [
        "Mfite ububabare bukabije",
        "Sinshobora kugenda",
        "Ndababara gusa gahoro",
        "Ni ukuri nkiri neza"
    ]
    
    for message in test_messages:
        is_emergency = kinyarwanda.detect_emergency(message)
        status = "🚨 EMERGENCY" if is_emergency else "✅ Normal"
        print(f"   '{message}' → {status}")

if __name__ == '__main__':
    try:
        demo_translations()
        demo_conversation_flow()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        sys.exit(1)



