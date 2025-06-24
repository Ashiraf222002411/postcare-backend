# sms-service/app/enhanced_sms_service.py
"""
PostCare Enhanced SMS Service with AI Integration
Connects to Africa's Talking SMS API and provides AI-powered patient analysis
"""

import sys
import os
import json
import logging
from datetime import datetime, timedelta
import pickle
import threading
import time
import schedule

# Add parent directories to path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.extend([current_dir, parent_dir, grandparent_dir])

# Flask and HTTP imports
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# Try to import existing ML models
try:
    from ml_models import IntelligentPostCareSystem
    AI_AVAILABLE = True
    print("✅ AI Models imported successfully")
except ImportError as e:
    print(f"⚠️ AI Models not found, using fallback: {e}")
    AI_AVAILABLE = False

# Try to import numpy and scikit-learn for basic analysis
try:
    import numpy as np
    from sklearn.ensemble import RandomForestRegressor
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    print("⚠️ Scikit-learn not available, using simple analysis")
    SKLEARN_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('postcare_sms.log'),
        logging.StreamHandler()
    ]
)

print("🚀 Starting PostCare Enhanced SMS Service...")
print("=" * 60)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['https://postcareplus.com', 'http://localhost:3000'])

class SMSService:
    """Enhanced SMS service with Africa's Talking integration"""
    
    def __init__(self):
        self.api_key = "atsk_6d6575c069937926742f2bd2c866df0eeff09902147dcdc465ac33167e792034cba76e6"
        self.username = "Ashiraf"
        self.sender_id = "PostCare"
        self.base_url = "https://api.africastalking.com/version1/messaging"
        
        # SMS statistics
        self.sms_sent_today = 0
        self.total_cost_today = 0.0
        self.last_reset_date = datetime.now().date()
        
        print("📱 SMS Service initialized with Africa's Talking")
    
    def reset_daily_stats(self):
        """Reset daily statistics if it's a new day"""
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            self.sms_sent_today = 0
            self.total_cost_today = 0.0
            self.last_reset_date = current_date
            print(f"📊 Daily SMS stats reset for {current_date}")
    
    def format_rwanda_phone(self, phone_number):
        """Format phone number to Rwanda international format"""
        if not phone_number:
            return None
            
        clean_phone = ''.join(filter(str.isdigit, phone_number))
        
        if clean_phone.startswith('250'):
            return f"+{clean_phone}"
        elif clean_phone.startswith('0'):
            return f"+250{clean_phone[1:]}"
        elif len(clean_phone) == 9:
            return f"+250{clean_phone}"
        
        return phone_number
    
    def detect_network(self, phone_number):
        """Detect MTN vs Airtel network"""
        formatted = self.format_rwanda_phone(phone_number)
        if formatted and formatted.startswith('+250'):
            prefix = formatted[4:6]
            if prefix in ['78', '79']:
                return 'MTN'
            elif prefix in ['72', '73']:
                return 'AIRTEL'
        return 'UNKNOWN'
    
    def send_sms(self, phone, message, retries=2):
        """Send SMS with retry logic and comprehensive error handling"""
        try:
            self.reset_daily_stats()
            
            formatted_phone = self.format_rwanda_phone(phone)
            if not formatted_phone:
                return {'success': False, 'error': 'Invalid phone number format'}
            
            network = self.detect_network(formatted_phone)
            
            print(f"📤 Sending SMS to {formatted_phone} ({network})")
            print(f"📝 Message preview: {message[:50]}{'...' if len(message) > 50 else ''}")
            
            headers = {
                'apiKey': self.api_key,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {
                'username': self.username,
                'to': formatted_phone,
                'message': message,
                'from': self.sender_id
            }
            
            for attempt in range(retries + 1):
                try:
                    response = requests.post(
                        self.base_url, 
                        headers=headers, 
                        data=data, 
                        timeout=30
                    )
                    
                    print(f"📱 SMS API Response: {response.status_code}")
                    
                    if response.status_code == 201:
                        result = response.json()
                        recipients = result['SMSMessageData']['Recipients']
                        
                        if recipients and recipients[0]['status'] == 'Success':
                            cost_str = recipients[0]['cost']
                            cost_value = float(cost_str.replace('RWF', '').replace('USD', '').strip())
                            
                            # Update statistics
                            self.sms_sent_today += 1
                            self.total_cost_today += cost_value
                            
                            print(f"✅ SMS sent successfully!")
                            print(f"💰 Cost: {cost_str}")
                            print(f"📊 Today's stats: {self.sms_sent_today} SMS, {self.total_cost_today:.2f} RWF")
                            
                            return {
                                'success': True,
                                'cost': cost_str,
                                'messageId': recipients[0]['messageId'],
                                'network': network,
                                'formatted_phone': formatted_phone,
                                'messageParts': recipients[0].get('messageParts', 1)
                            }
                        else:
                            error_msg = recipients[0]['status'] if recipients else 'Unknown error'
                            print(f"❌ SMS failed: {error_msg}")
                            return {'success': False, 'error': error_msg}
                    
                    elif response.status_code == 401:
                        print("❌ Authentication failed - check API key")
                        return {'success': False, 'error': 'Authentication failed'}
                    
                    elif response.status_code == 400:
                        print(f"❌ Bad request: {response.text}")
                        return {'success': False, 'error': f'Bad request: {response.text}'}
                    
                    else:
                        print(f"❌ HTTP {response.status_code}: {response.text}")
                        if attempt < retries:
                            print(f"🔄 Retrying... (attempt {attempt + 2})")
                            time.sleep(2)
                            continue
                        return {'success': False, 'error': f'HTTP {response.status_code}: {response.text}'}
                
                except requests.exceptions.Timeout:
                    print(f"⏰ Request timeout (attempt {attempt + 1})")
                    if attempt < retries:
                        time.sleep(2)
                        continue
                    return {'success': False, 'error': 'Request timeout'}
                
                except requests.exceptions.ConnectionError:
                    print(f"🌐 Connection error (attempt {attempt + 1})")
                    if attempt < retries:
                        time.sleep(3)
                        continue
                    return {'success': False, 'error': 'Connection error'}
            
            return {'success': False, 'error': 'Max retries exceeded'}
            
        except Exception as e:
            print(f"❌ Unexpected SMS error: {str(e)}")
            logging.error(f"SMS sending failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_statistics(self):
        """Get SMS usage statistics"""
        self.reset_daily_stats()
        return {
            'sms_sent_today': self.sms_sent_today,
            'total_cost_today': self.total_cost_today,
            'date': self.last_reset_date.isoformat()
        }

class SimpleAIAnalyzer:
    """Fallback AI analyzer when ML models aren't available"""
    
    def __init__(self):
        print("🤖 Initializing Simple AI Analyzer (fallback mode)")
    
    def analyze_patient_condition(self, patient_data):
        """Simple rule-based analysis"""
        pain = patient_data.get('pain', 5)
        wound = patient_data.get('wound', 5)
        temperature = patient_data.get('temperature', 37.0)
        mobility = patient_data.get('mobility', 5)
        
        alerts = []
        severity = 0
        
        # Simple rules
        if pain > 7:
            alerts.append('HIGH_PAIN')
            severity += 3
        if wound < 4:
            alerts.append('POOR_WOUND_HEALING')
            severity += 2
        if temperature > 38.0:
            alerts.append('FEVER')
            severity += 2
        if mobility < 4:
            alerts.append('LOW_MOBILITY')
            severity += 1
        
        # Simple recovery score calculation
        recovery_score = (10 - pain + wound + mobility + (40 - temperature) * 2) / 50
        recovery_score = max(0, min(1, recovery_score))
        
        return {
            'severity': float(severity),
            'recovery_prediction': float(recovery_score),
            'alerts': alerts,
            'needs_attention': len(alerts) > 0 or severity > 5,
            'analysis_method': 'simple_rules'
        }

class PatientDataManager:
    """Manage patient data and responses"""
    
    def __init__(self, data_file='patient_data.pkl'):
        self.data_file = data_file
        self.patients = self.load_patient_data()
        print(f"📊 Patient Data Manager initialized ({len(self.patients)} patients loaded)")
    
    def load_patient_data(self):
        """Load patient data from file"""
        try:
            with open(self.data_file, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            print("📁 No existing patient data file found, starting fresh")
            return {}
        except Exception as e:
            print(f"⚠️ Error loading patient data: {e}")
            return {}
    
    def save_patient_data(self):
        """Save patient data to file"""
        try:
            with open(self.data_file, 'wb') as f:
                pickle.dump(self.patients, f)
        except Exception as e:
            print(f"❌ Error saving patient data: {e}")
    
    def add_patient(self, patient_id, patient_info):
        """Add or update patient information"""
        self.patients[patient_id] = {
            'id': patient_id,
            'name': patient_info.get('name', ''),
            'phone': patient_info.get('phone', ''),
            'surgery_type': patient_info.get('surgery_type', ''),
            'surgery_date': patient_info.get('surgery_date', ''),
            'language': patient_info.get('language', 'en'),
            'registered_at': datetime.now().isoformat(),
            'responses': [],
            'follow_up_schedule': []
        }
        self.save_patient_data()
        print(f"👤 Patient {patient_id} ({patient_info.get('name')}) registered")
    
    def find_patient_by_phone(self, phone):
        """Find patient by phone number"""
        formatted_phone = sms_service.format_rwanda_phone(phone)
        for patient_id, patient in self.patients.items():
            if sms_service.format_rwanda_phone(patient['phone']) == formatted_phone:
                return patient_id, patient
        return None, None
    
    def add_patient_response(self, patient_id, response_data, analysis):
        """Add patient response and analysis"""
        if patient_id in self.patients:
            response_record = {
                'timestamp': datetime.now().isoformat(),
                'responses': response_data,
                'analysis': analysis
            }
            self.patients[patient_id]['responses'].append(response_record)
            self.save_patient_data()
            print(f"📝 Response recorded for patient {patient_id}")

# Initialize services
sms_service = SMSService()
patient_manager = PatientDataManager()

# Initialize AI system
if AI_AVAILABLE:
    try:
        ai_system = IntelligentPostCareSystem('./models')
        print("✅ Advanced AI System initialized")
    except Exception as e:
        print(f"⚠️ Advanced AI failed, using simple analyzer: {e}")
        ai_system = SimpleAIAnalyzer()
else:
    ai_system = SimpleAIAnalyzer()

# Flask Routes
@app.route('/health', methods=['GET'])
def health_check():
    """System health check"""
    print("🏥 Health check requested")
    
    stats = sms_service.get_statistics()
    
    return jsonify({
        'status': 'healthy',
        'service': 'PostCare Enhanced SMS Service',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'ai_system': 'advanced' if AI_AVAILABLE else 'simple',
        'sms_service': 'active',
        'statistics': stats,
        'total_patients': len(patient_manager.patients)
    })

@app.route('/send_welcome', methods=['POST'])
def send_welcome_sms():
    """Send welcome SMS to new patient"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        name = data.get('name', 'Patient')
        phone = data.get('phone')
        surgery_type = data.get('surgery_type', 'surgery')
        patient_id = data.get('patient_id')
        
        if not phone:
            return jsonify({'success': False, 'error': 'Phone number required'}), 400
        
        print(f"👋 Sending welcome SMS to {name} ({phone})")
        
        # Register patient if patient_id provided
        if patient_id:
            patient_manager.add_patient(patient_id, data)
        
        message = f"Hello {name}, welcome to PostCare+! We'll monitor your recovery after {surgery_type}. We'll check in on your progress regularly to ensure your healing goes smoothly. Reply to our messages with your symptoms."
        
        result = sms_service.send_sms(phone, message)
        
        if result['success']:
            print(f"✅ Welcome SMS sent to {name}")
        else:
            print(f"❌ Welcome SMS failed for {name}: {result['error']}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Welcome SMS error: {str(e)}")
        logging.error(f"Welcome SMS error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/send_followup', methods=['POST'])
def send_followup_sms():
    """Send follow-up SMS to patient"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        name = data.get('name', 'Patient')
        phone = data.get('phone')
        day = data.get('day', 1)
        
        if not phone:
            return jsonify({'success': False, 'error': 'Phone number required'}), 400
        
        print(f"📅 Sending Day {day} follow-up SMS to {name}")
        
        message = f"""Hello {name}, Day {day} recovery check-in:

Please reply with these numbers (one per line):
1. Pain level (1-10)
2. Wound healing (1-10)
3. Temperature (°C)
4. Mobility (1-10)

Example reply:
5
7
37.0
8

This helps us monitor your recovery progress."""
        
        result = sms_service.send_sms(phone, message)
        
        if result['success']:
            print(f"✅ Follow-up SMS sent to {name} (Day {day})")
        else:
            print(f"❌ Follow-up SMS failed for {name}: {result['error']}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Follow-up SMS error: {str(e)}")
        logging.error(f"Follow-up SMS error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/analyze_response', methods=['POST'])
def analyze_patient_response():
    """Analyze patient response using AI"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        print(f"🤖 Analyzing patient response: {data}")
        
        # Extract patient data
        patient_data = {
            'pain': float(data.get('pain', 5)),
            'wound': float(data.get('wound', 5)),
            'temperature': float(data.get('temperature', 37.0)),
            'mobility': float(data.get('mobility', 5))
        }
        
        # Perform AI analysis
        analysis = ai_system.analyze_patient_condition(patient_data)
        
        print(f"📊 Analysis result: Severity {analysis['severity']}, Recovery {analysis['recovery_prediction']:.2%}")
        
        if analysis['alerts']:
            print(f"⚠️ Alerts generated: {', '.join(analysis['alerts'])}")
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'patient_data': patient_data
        })
        
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        logging.error(f"Analysis error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/webhook/sms', methods=['POST'])
def sms_webhook():
    """Handle incoming SMS from Africa's Talking"""
    try:
        # Africa's Talking sends data as form data
        data = request.form.to_dict() if request.form else request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        phone = data.get('from') or data.get('phoneNumber')
        message_text = data.get('text') or data.get('message')
        message_id = data.get('id') or data.get('messageId')
        
        print(f"📨 Incoming SMS from {phone}: {message_text}")
        
        if not phone or not message_text:
            print("❌ Missing phone number or message text")
            return jsonify({'error': 'Missing phone or message'}), 400
        
        # Find patient
        patient_id, patient = patient_manager.find_patient_by_phone(phone)
        
        if not patient:
            print(f"⚠️ Patient not found for phone {phone}")
            # Send helpful message to unknown number
            sms_service.send_sms(phone, "Hello! You're not registered in our PostCare system. Please contact your healthcare provider for assistance.")
            return jsonify({'status': 'patient_not_found', 'phone': phone})
        
        # Parse patient response
        response_data = parse_patient_response(message_text)
        
        if not response_data:
            # Send clarification message
            clarification = f"Hello {patient['name']}, please reply with numbers only, one per line:\n1. Pain (1-10)\n2. Wound (1-10)\n3. Temperature\n4. Mobility (1-10)"
            sms_service.send_sms(phone, clarification)
            return jsonify({'status': 'clarification_sent'})
        
        # Analyze response
        analysis = ai_system.analyze_patient_condition(response_data)
        
        # Store response
        patient_manager.add_patient_response(patient_id, response_data, analysis)
        
        # Generate and send response
        response_message = generate_response_message(patient['name'], analysis)
        sms_service.send_sms(phone, response_message)
        
        # Alert healthcare provider if needed
        if analysis['needs_attention']:
            alert_provider(patient, analysis)
        
        print(f"✅ SMS response processed for {patient['name']}")
        
        return jsonify({
            'status': 'processed',
            'patient': patient['name'],
            'analysis': analysis
        })
        
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        logging.error(f"SMS webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/test_sms', methods=['POST'])
def test_sms():
    """Test SMS sending functionality"""
    try:
        data = request.get_json()
        phone = data.get('phone', '+250785379885')
        message = data.get('message', 'Test SMS from PostCare Enhanced Service! 🏥📱')
        
        print(f"🧪 Test SMS to {phone}")
        result = sms_service.send_sms(phone, message)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Test SMS error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/statistics', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    try:
        sms_stats = sms_service.get_statistics()
        
        total_patients = len(patient_manager.patients)
        patients_with_responses = sum(1 for p in patient_manager.patients.values() if p['responses'])
        
        return jsonify({
            'sms_statistics': sms_stats,
            'patient_statistics': {
                'total_patients': total_patients,
                'patients_with_responses': patients_with_responses,
                'response_rate': round((patients_with_responses / total_patients * 100) if total_patients > 0 else 0, 2)
            },
            'system_info': {
                'ai_system': 'advanced' if AI_AVAILABLE else 'simple',
                'uptime': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper functions
def parse_patient_response(message_text):
    """Parse patient SMS response into structured data"""
    try:
        lines = message_text.strip().split('\n')
        numbers = []
        
        for line in lines:
            # Extract numbers from each line
            import re
            number_match = re.search(r'\d+\.?\d*', line.strip())
            if number_match:
                numbers.append(float(number_match.group()))
        
        if len(numbers) >= 4:
            return {
                'pain': numbers[0],
                'wound': numbers[1],
                'temperature': numbers[2],
                'mobility': numbers[3]
            }
        
        return None
        
    except (ValueError, IndexError) as e:
        print(f"⚠️ Error parsing response '{message_text}': {e}")
        return None

def generate_response_message(patient_name, analysis):
    """Generate appropriate response message based on analysis"""
    severity = analysis['severity']
    recovery_score = analysis['recovery_prediction']
    alerts = analysis['alerts']
    
    if severity > 8 or 'HIGH_PAIN' in alerts and 'FEVER' in alerts:
        return f"🚨 URGENT {patient_name}: Your symptoms need immediate medical attention. Please contact your doctor or go to emergency room now. Concerning signs: {', '.join(alerts)}"
    
    elif analysis['needs_attention']:
        return f"Hello {patient_name}, your symptoms need attention. Please contact your doctor if symptoms persist or worsen. Take prescribed medications and rest. Current alerts: {', '.join(alerts)}"
    
    elif recovery_score > 0.7:
        return f"Great progress {patient_name}! Your recovery is going very well (Recovery score: {recovery_score:.0%}). Keep following your care plan and taking medications as prescribed."
    
    else:
        return f"Thank you for the update, {patient_name}. Your recovery is progressing (Score: {recovery_score:.0%}). Continue following your care plan. We'll check in again soon."

def alert_provider(patient, analysis):
    """Alert healthcare provider about concerning patient status"""
    try:
        provider_phone = "+250785379885"  # Replace with actual provider number
        
        alert_message = f"""🚨 PATIENT ALERT: {patient['name']} ({patient['phone']})
Surgery: {patient['surgery_type']}
Alerts: {', '.join(analysis['alerts'])}
Severity: {analysis['severity']}/10
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Please follow up with this patient."""
        
        result = sms_service.send_sms(provider_phone, alert_message)
        
        if result['success']:
            print(f"🚨 Healthcare provider alerted for {patient['name']}")
        else:
            print(f"❌ Failed to alert provider: {result['error']}")
            
    except Exception as e:
        print(f"❌ Provider alert error: {str(e)}")
        logging.error(f"Provider alert error: {str(e)}")

# Background scheduler (optional)
def run_scheduler():
    """Run background tasks"""
    while True:
        schedule.run_pending()
        time.sleep(60)

# Add scheduled tasks
# schedule.every().day.at("09:00").do(check_due_followups)

# Main execution
if __name__ == '__main__':
    print("🏥 PostCare Enhanced SMS Service")
    print("=" * 60)
    print("📱 SMS Integration: Active")
    print(f"🤖 AI System: {'Advanced ML Models' if AI_AVAILABLE else 'Simple Rule-Based'}")
    print(f"👥 Patients Loaded: {len(patient_manager.patients)}")
    print("🌐 Starting Flask server on port 5001...")
    print("🔗 Available endpoints:")
    print("   GET  /health              - Health check")
    print("   POST /send_welcome        - Send welcome SMS")
    print("   POST /send_followup       - Send follow-up SMS")
    print("   POST /analyze_response    - Analyze patient data")
    print("   POST /webhook/sms         - SMS webhook")
    print("   POST /test_sms           - Test SMS sending")
    print("   GET  /statistics         - System statistics")
    print("=" * 60)
    
    # Start background scheduler in a separate thread
    # scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    # scheduler_thread.start()
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n👋 Shutting down PostCare SMS Service...")
    except Exception as e:
        print(f"❌ Server error: {str(e)}")
        logging.error(f"Server startup error: {str(e)}")