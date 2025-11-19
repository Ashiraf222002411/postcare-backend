#!/usr/bin/env python3
"""
SMS Monitor Service for PostCare
Monitors incoming SMS and forwards to backend for processing
"""

import subprocess
import json
import time
import requests
import logging
from datetime import datetime
from pathlib import Path

# Configuration - Updated for PostCare Backend
BACKEND_URL = "http://172.20.10.4:5001/webhook/sms"  # Your backend URL
BACKEND_API_KEY = "postcare_backend_key_2024"  # Your API key
CHECK_INTERVAL = 5  # Check for new SMS every 5 seconds
PROCESSED_SMS_FILE = "processed_sms.json"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SMSMonitor:
    def __init__(self):
        self.processed_messages = self.load_processed_messages()
        logging.info("📱 PostCare SMS Monitor initialized")
        logging.info(f"🔗 Backend URL: {BACKEND_URL}")
    
    def load_processed_messages(self):
        """Load list of already processed message IDs"""
        try:
            if Path(PROCESSED_SMS_FILE).exists():
                with open(PROCESSED_SMS_FILE, 'r') as f:
                    return set(json.load(f))
            return set()
        except Exception as e:
            logging.error(f"Error loading processed messages: {e}")
            return set()
    
    def save_processed_messages(self):
        """Save processed message IDs"""
        try:
            with open(PROCESSED_SMS_FILE, 'w') as f:
                json.dump(list(self.processed_messages), f)
        except Exception as e:
            logging.error(f"Error saving processed messages: {e}")
    
    def get_incoming_sms(self):
        """Get incoming SMS from phone"""
        try:
            result = subprocess.run(
                ['termux-sms-list', '-l', '20', '-t', 'inbox'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                messages = json.loads(result.stdout)
                return messages
            else:
                logging.error(f"Error getting SMS: {result.stderr}")
                return []
        except Exception as e:
            logging.error(f"Error fetching SMS: {e}")
            return []
    
    def is_new_message(self, message):
        """Check if message is new (not processed yet)"""
        message_id = message.get('_id')
        return message_id and message_id not in self.processed_messages
    
    def forward_to_backend(self, message):
        """Forward SMS to PostCare backend for processing"""
        try:
            # Format for PostCare backend
            payload = {
                'from': message.get('number', 'unknown'),
                'text': message.get('body', ''),
                'id': message.get('_id'),
                'timestamp': message.get('received', datetime.now().isoformat())
            }
            
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': BACKEND_API_KEY
            }
            
            logging.info(f"📨 Forwarding SMS from {payload['from']}: {payload['text'][:50]}...")
            
            response = requests.post(
                BACKEND_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logging.info(f"✅ PostCare backend processed SMS successfully")
                
                # Check if backend wants to send a reply
                if result.get('send_reply') and result.get('reply_message'):
                    self.send_reply(
                        payload['from'],
                        result['reply_message']
                    )
                
                return True
            elif response.status_code == 401:
                logging.error("❌ Authentication failed - check API key")
                return False
            else:
                logging.error(f"❌ Backend error: {response.status_code} - {response.text}")
                return False
                
        except requests.Timeout:
            logging.error("⏱️ Backend timeout")
            return False
        except requests.ConnectionError:
            logging.error("🔌 Cannot connect to PostCare backend")
            return False
        except Exception as e:
            logging.error(f"❌ Error forwarding to backend: {e}")
            return False
    
    def send_reply(self, phone_number, message):
        """Send SMS reply using Termux"""
        try:
            logging.info(f"📤 Sending PostCare reply to {phone_number}")
            
            result = subprocess.run(
                ['termux-sms-send', '-n', phone_number, message],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logging.info(f"✅ PostCare reply sent to {phone_number}")
                return True
            else:
                logging.error(f"❌ Failed to send reply: {result.stderr}")
                return False
        except Exception as e:
            logging.error(f"❌ Error sending reply: {e}")
            return False
    
    def mark_as_processed(self, message_id):
        """Mark message as processed"""
        self.processed_messages.add(message_id)
        self.save_processed_messages()
    
    def process_new_messages(self):
        """Check for and process new messages"""
        messages = self.get_incoming_sms()
        new_count = 0
        
        for message in messages:
            if self.is_new_message(message):
                new_count += 1
                message_id = message.get('_id')
                
                # Forward to PostCare backend
                success = self.forward_to_backend(message)
                
                if success:
                    # Mark as processed so we don't process it again
                    self.mark_as_processed(message_id)
                else:
                    logging.warning(f"⚠️ Failed to process message {message_id}, will retry later")
        
        if new_count > 0:
            logging.info(f"📊 Processed {new_count} new message(s) for PostCare")
        
        return new_count
    
    def run(self):
        """Main monitoring loop"""
        logging.info("=" * 60)
        logging.info("🚀 PostCare SMS Monitor Service Started")
        logging.info("=" * 60)
        logging.info(f"📡 Backend URL: {BACKEND_URL}")
        logging.info(f"🔑 API Key: {BACKEND_API_KEY[:10]}...")
        logging.info(f"⏱️  Check interval: {CHECK_INTERVAL} seconds")
        logging.info("=" * 60)
        logging.info("👂 Listening for incoming SMS...")
        logging.info("📱 Patients can now reply to PostCare messages!")
        logging.info("Press Ctrl+C to stop")
        logging.info("=" * 60)
        
        try:
            while True:
                self.process_new_messages()
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logging.info("\n👋 PostCare SMS Monitor stopped by user")
        except Exception as e:
            logging.error(f"💥 Fatal error: {e}")
            raise

if __name__ == "__main__":
    monitor = SMSMonitor()
    monitor.run()
