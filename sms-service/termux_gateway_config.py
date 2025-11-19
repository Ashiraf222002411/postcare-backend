#!/usr/bin/env python3
"""
Termux Gateway Configuration for PostCare SMS Service
Update this file with your actual backend URL and API key
"""

# Backend Configuration
BACKEND_URL = "http://YOUR_BACKEND_IP:5001/webhook/sms"
BACKEND_API_KEY = "postcare_backend_key_2024"

# If running on same machine as backend:
# BACKEND_URL = "http://localhost:5001/webhook/sms"

# If backend is on different machine, use the machine's IP:
# BACKEND_URL = "http://192.168.1.100:5001/webhook/sms"

# Gateway Configuration
CHECK_INTERVAL = 5  # Check for new SMS every 5 seconds
PROCESSED_SMS_FILE = "processed_sms.json"

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# Instructions:
# 1. Replace YOUR_BACKEND_IP with your actual backend server IP address
# 2. Make sure the backend is accessible from your Termux device
# 3. If using localhost, both services must be on the same machine
# 4. Copy this file to your Termux device
# 5. Update the SMS Monitor Service (sms_monitor.py) to use these values
