#!/usr/bin/env python3
# check_at_credentials.py
"""
Check Africa's Talking API credentials and account status
"""

import requests
import sys

def check_credentials():
    """Check if Africa's Talking credentials are valid"""
    
    # Current credentials from the system
    api_key = "atsk_6d6575c069937926742f2bd2c866df0eeff09902147dcdc465ac33167e792034cba76e6"
    username = "Ashiraf"
    
    print("🔍 Checking Africa's Talking API Credentials")
    print("=" * 50)
    print(f"Username: {username}")
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}")  # Show partial key for security
    
    # Check account balance
    print("\n💰 Checking Account Balance...")
    balance_url = "https://api.africastalking.com/version1/user"
    
    headers = {
        'apiKey': api_key,
        'Accept': 'application/json'
    }
    
    data = {
        'username': username
    }
    
    try:
        response = requests.get(f"{balance_url}?username={username}", headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            balance_data = response.json()
            print("✅ API Credentials are VALID!")
            print(f"Account Balance: {balance_data.get('UserData', {}).get('balance', 'Unknown')}")
            return True
        elif response.status_code == 401:
            print("❌ AUTHENTICATION FAILED!")
            print("Possible causes:")
            print("  • API Key is expired or invalid")
            print("  • Username doesn't match the account")
            print("  • Account might be suspended")
            return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Check internet connection")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request Timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_sms_api():
    """Test SMS sending API directly"""
    
    api_key = "atsk_6d6575c069937926742f2bd2c866df0eeff09902147dcdc465ac33167e792034cba76e6"
    username = "Ashiraf"
    
    print("\n📱 Testing SMS API Directly...")
    
    # Test phone number (your number)
    test_phone = input("Enter your phone number for testing (+250XXXXXXXXX): ").strip()
    if not test_phone:
        print("❌ No phone number provided")
        return False
    
    sms_url = "https://api.africastalking.com/version1/messaging"
    
    headers = {
        'apiKey': api_key,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    data = {
        'username': username,
        'to': test_phone,
        'message': 'Test from PostCare+ - API Check',
        'from': 'PostCare'
    }
    
    try:
        response = requests.post(sms_url, headers=headers, data=data, timeout=30)
        print(f"SMS API Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            recipients = result.get('SMSMessageData', {}).get('Recipients', [])
            
            if recipients and recipients[0].get('status') == 'Success':
                print("✅ SMS API is WORKING!")
                print(f"Cost: {recipients[0].get('cost', 'Unknown')}")
                print(f"Message ID: {recipients[0].get('messageId', 'Unknown')}")
                return True
            else:
                print("❌ SMS sending failed")
                print(f"Status: {recipients[0].get('status') if recipients else 'No recipients'}")
                return False
        elif response.status_code == 401:
            print("❌ SMS API Authentication Failed")
            return False
        else:
            print(f"❌ SMS API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ SMS API Error: {e}")
        return False

def main():
    """Main credential checker"""
    print("🔐 Africa's Talking API Credential Checker")
    print("=" * 60)
    
    # Check credentials
    creds_valid = check_credentials()
    
    if creds_valid:
        print("\n🧪 Credentials are valid. Testing SMS sending...")
        sms_test = test_sms_api()
        
        if sms_test:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Your Africa's Talking integration is working correctly.")
            print("The issue might be elsewhere in the system.")
        else:
            print("\n⚠️ Credentials valid but SMS sending failed.")
            print("Check account balance and SMS permissions.")
    else:
        print("\n❌ CREDENTIAL ISSUES DETECTED")
        print("\n🔧 SOLUTIONS:")
        print("1. 🔄 Update API Key:")
        print("   • Login to Africa's Talking dashboard")
        print("   • Go to API settings")
        print("   • Generate new API key")
        print("   • Update in enhanced_sms_service.py line 81")
        print()
        print("2. ✏️ Verify Username:")
        print("   • Check username in Africa's Talking dashboard")
        print("   • Update in enhanced_sms_service.py line 82")
        print()
        print("3. 💰 Check Account Balance:")
        print("   • Ensure account has sufficient credit")
        print("   • Top up if necessary")
        print()
        print("4. 🌍 Verify Account Status:")
        print("   • Ensure account is active")
        print("   • Check if SMS permissions are enabled")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Check interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
