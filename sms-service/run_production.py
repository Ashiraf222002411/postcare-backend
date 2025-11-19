#!/usr/bin/env python3
"""
Production Runner for PostCare SMS Service
Starts the enhanced SMS service for production use
"""

import sys
import os
import warnings
warnings.filterwarnings("ignore")

# Add the app directory to path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    """Run the enhanced SMS service in production mode"""
    print("=" * 70)
    print("🚀 PostCare Enhanced SMS Service - Production Mode")
    print("=" * 70)
    print("📱 Starting real-time SMS conversation system...")
    print("💬 Full USSD-like patient interaction enabled")
    print("🤖 AI-powered health analysis active")
    print("🌍 Kinyarwanda language support enabled")
    print("=" * 70)
    
    try:
        # Import and run the enhanced service
        from app.enhanced_sms_service import app
        
        # Production settings
        app.run(
            host='0.0.0.0',  # Listen on all interfaces
            port=5001,
            debug=False,  # Disable debug mode for production
            threaded=True  # Enable threading for concurrent requests
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 PostCare SMS Service stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting service: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

