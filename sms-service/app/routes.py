from flask import Blueprint, request, jsonify
from app.ml_models import IntelligentPostCareSystem
from config import Config
import logging
import time
import requests

bp = Blueprint('main', __name__)

# Initialize the PostCare system
postcare_system = IntelligentPostCareSystem(Config.MODEL_DIR)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sms_service.log'),
        logging.StreamHandler()
    ]
)

@bp.route('/')
def index():
    """Test endpoint"""
    return jsonify({"status": "SMS Service is running"})

@bp.route('/incoming-sms', methods=['POST'])
def handle_incoming_sms():
    """Handle incoming SMS with retry mechanism"""
    try:
        # Log the raw request
        logging.info(f"Received webhook request: {request.get_data()}")
        logging.info(f"Headers: {dict(request.headers)}")

        # Get the data based on content type
        if request.is_json:
            data = request.json
            logging.info(f"JSON data received: {data}")
        else:
            data = request.form.to_dict()
            logging.info(f"Form data received: {data}")

        # Extract message details with fallbacks
        phone_number = data.get('from') or data.get('sender') or data.get('phone')
        message = data.get('text') or data.get('message') or data.get('content', '').strip()

        logging.info(f"Processing message from {phone_number}: {message}")

        if not phone_number or not message:
            logging.error("Missing phone number or message")
            return jsonify({"error": "Missing required parameters"}), 400

        # Process message with retry mechanism
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Generate response based on message
                response_message = process_patient_message(phone_number, message)
                
                # Send response with retry mechanism
                if response_message:
                    send_success = send_sms_with_retry(phone_number, response_message)
                    if send_success:
                        logging.info(f"Successfully sent response to {phone_number}")
                        return jsonify({"success": True})
                    else:
                        logging.error(f"Failed to send SMS after retries")
                        
                return jsonify({"success": True})

            except Exception as e:
                retry_count += 1
                logging.error(f"Attempt {retry_count} failed: {str(e)}")
                if retry_count < max_retries:
                    time.sleep(2 ** retry_count)  # Exponential backoff
                else:
                    raise

    except Exception as e:
        logging.error(f"Error processing incoming SMS: {str(e)}")
        return jsonify({"error": str(e)}), 500

def send_sms_with_retry(phone_number, message, max_retries=3):
    """Send SMS with retry mechanism"""
    retry_count = 0
    while retry_count < max_retries:
        try:
            success = postcare_system.send_sms(phone_number, message)
            if success:
                return True
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(2 ** retry_count)
        except Exception as e:
            logging.error(f"SMS sending attempt {retry_count + 1} failed: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(2 ** retry_count)
    return False

def process_patient_message(phone_number, message):
    """Process incoming patient message and generate response"""
    try:
        logging.info(f"Processing message: {message}")
        
        # Convert to lowercase for easier matching
        message_lower = message.lower()

        # Handle different message types
        if message.isdigit():
            pain_level = int(message)
            if 0 <= pain_level <= 10:
                return process_pain_level(phone_number, pain_level)

        if 'pain' in message_lower:
            return "On a scale of 0-10, how would you rate your pain level?"
        
        if 'help' in message_lower:
            return ("Available commands:\n"
                   "- Rate pain (0-10)\n"
                   "- Report temperature\n"
                   "- Report symptoms\n"
                   "- Request callback\n"
                   "Send 'HELP' for this menu")

        # Default response
        return ("I'm not sure how to help with that. "
               "Send 'HELP' for available commands.")

    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        return "Sorry, I couldn't process your message. Please try again or send 'HELP' for assistance."

def process_pain_level(phone_number, pain_level):
    """Handle pain level reports"""
    try:
        logging.info(f"Processing pain level {pain_level} for {phone_number}")
        
        if pain_level >= 8:
            return ("Your pain level is concerning. Please contact your healthcare "
                   "provider immediately or seek emergency care if needed.")
        elif pain_level >= 5:
            return ("Your pain level is moderate to high. Consider taking prescribed "
                   "pain medication and rest. Contact your provider if it persists.")
        else:
            return ("Thank you for reporting your pain level. Continue monitoring "
                   "and follow your prescribed care plan.")
    except Exception as e:
        logging.error(f"Error processing pain level: {str(e)}")
        return "Error processing pain level. Please try again."

def process_temperature(phone_number, temperature):
    """Process temperature reports"""
    try:
        if temperature >= 38.0:
            return ("Your temperature is elevated. Please take prescribed medication "
                   "and contact your healthcare provider if it persists.")
        elif 36.1 <= temperature <= 37.2:
            return "Your temperature is within normal range. Continue monitoring."
        else:
            return ("Temperature reading noted. Please ensure accurate measurement "
                   "and continue monitoring.")
    except Exception as e:
        logging.error(f"Error processing temperature: {str(e)}")
        return "Error processing temperature. Please try again."

@bp.route('/analyze', methods=['POST'])
def analyze_condition():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Sample patient data structure
        patient_data = {
            'wound': data.get('wound', 0),
            'pain': data.get('pain', 0),
            'temperature': data.get('temperature', 0),
            'mobility': data.get('mobility', 0),
            'appetite': data.get('appetite', 0),
            'sleep': data.get('sleep', 0),
            'medication_adherence': data.get('medication_adherence', 0)
        }

        analysis = postcare_system.analyze_patient_condition(patient_data)
        return jsonify({
            "success": True,
            "analysis": analysis
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/trigger-checkup', methods=['POST'])
def trigger_checkup():
    try:
        patient_phone = request.json.get('phone_number')
        if not patient_phone:
            return jsonify({"error": "No phone number provided"}), 400

        # Generate personalized checkup message
        message = (
            "Hello! How are you feeling today?\n"
            "Please reply with:\n"
            "1. Pain level (0-10)\n"
            "2. Temperature (if available)\n"
            "3. Any new symptoms"
        )

        # Send the message
        postcare_system.send_sms(patient_phone, message)

        return jsonify({
            "success": True,
            "message": "Checkup triggered successfully"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ... [Rest of the route implementations]
