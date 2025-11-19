# termux_gateway.py
import requests
import logging

class TermuxSMSGateway:
    """Client for Termux SMS Gateway API"""
    
    def __init__(self, gateway_url, api_key):
        self.gateway_url = gateway_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        }
    
    def send_sms(self, phone_number, message, sender_id="PostCare"):
        """Send SMS via Termux gateway"""
        try:
            logging.info(f"Sending SMS to {phone_number} via Termux gateway")
            
            payload = {
                "recipient": phone_number,
                "message": message,
                "sender_id": sender_id
            }
            
            response = requests.post(
                f"{self.gateway_url}/api/v1/send",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                logging.info(f"SMS sent successfully. Message ID: {data.get('message_id')}")
                return True
            else:
                logging.error(f"Failed to send SMS: {data.get('error')}")
                return False
                
        except requests.Timeout:
            logging.error(f"Timeout sending SMS to {phone_number}")
            return False
        except requests.ConnectionError:
            logging.error(f"Connection error to gateway")
            return False
        except Exception as e:
            logging.error(f"Error sending SMS: {str(e)}")
            return False
    
    def health_check(self):
        """Check if gateway is online"""
        try:
            response = requests.get(
                f"{self.gateway_url}/api/v1/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False