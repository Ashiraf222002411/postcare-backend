import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    USE_TERMUX_GATEWAY = True
    TERMUX_GATEWAY_URL = "http://172.20.10.10:8000"  
    TERMUX_API_KEY = "postcare_default_key_12345"
    MODEL_DIR = "./app/models"
    
    # Backend SMS processing endpoint
    BACKEND_URL = "http://172.20.10.4:5001/webhook/sms"
    BACKEND_API_KEY = "postcare_backend_key_2024"
    
    # Node.js backend API for storing messages
    NODE_BACKEND_URL = os.getenv('NODE_BACKEND_URL', 'http://localhost:3000/api')