#!/usr/bin/env python3
"""
Start Production PostCare SMS Service
Runs all necessary services for production deployment
"""

import subprocess
import sys
import time
import os

def main():
    """Start production services"""
    print("=" * 70)
    print("🚀 PostCare SMS Service - Production Startup")
    print("=" * 70)
    
    # Get configuration
    print("\n📋 Configuration:")
    print("   Backend URL: http://172.20.10.4:5001")
    print("   API Key: postcare_backend_key_2024")
    print("   Gateway: Termux SMS Gateway")
    print("   Features: USSD Menu, AI Analysis, Kinyarwanda")
    print("=" * 70)
    
    # Start the service
    print("\n▶️  Starting PostCare Enhanced SMS Service...")
    print("   Listening on: http://0.0.0.0:5001")
    print("   Health check: http://localhost:5001/health")
    print("\n" + "=" * 70)
    print("✅ Service is now running in production mode!")
    print("💬 Patients can send SMS and receive AI-powered responses")
    print("📱 Deploy sms_monitor.py on Termux device to enable replies")
    print("=" * 70)
    print("\n⚠️  Press Ctrl+C to stop the service\n")
    
    try:
        # Run the enhanced service
        subprocess.run([sys.executable, "app/enhanced_sms_service.py"])
    except KeyboardInterrupt:
        print("\n\n👋 PostCare SMS Service stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

