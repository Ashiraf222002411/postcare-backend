import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SMS_API_KEY = os.environ.get('SMS_API_KEY')
    SMS_SENDER_ID = os.environ.get('SMS_SENDER_ID')  # Your phone number
    # Update the API URL for SMSMobileAPI
    SMS_API_URL = "https://dashboard.smsmobileapi.com/api/send-sms"
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
    MODEL_DIR = os.path.join(basedir, 'models')
    LOG_DIR = os.path.join(basedir, 'logs')
