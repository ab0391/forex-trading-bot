#!/usr/bin/env python3
"""
TwelveData API Usage Checker
Check current API credit usage and limits
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def check_twelvedata_usage():
    """Check TwelveData API usage and remaining credits"""
    
    api_key = os.getenv("TWELVEDATA_API_KEY")
    
    if not api_key or api_key == "your_api_key_here":
        print("❌ TwelveData API key not configured")
        print("💡 Please add your real API key to .env file")
        print("💡 Get your API key from: https://twelvedata.com/account/api")
        return False
    
    print(f"🔍 Checking TwelveData API usage...")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test API connection with usage endpoint
        url = "https://api.twelvedata.com/usage"
        params = {"apikey": api_key}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        usage_data = response.json()
        
        if "usage" in usage_data:
            usage = usage_data["usage"]
            print(f"\n📊 API Usage Summary:")
            print(f"{'='*40}")
            
            # Daily usage
            if "daily" in usage:
                daily = usage["daily"]
                used = daily.get("used", 0)
                limit = daily.get("limit", 800)
                percentage = (used / limit) * 100 if limit > 0 else 0
                
                print(f"📈 Daily Usage: {used}/{limit} credits ({percentage:.1f}%)")
                
                if percentage > 100:
                    print(f"🚨 OVER LIMIT by {percentage - 100:.1f}%!")
                elif percentage > 80:
                    print(f"⚠️  WARNING: {percentage:.1f}% of daily limit used")
                else:
                    print(f"✅ Safe usage: {percentage:.1f}% of daily limit")
            
            # Monthly usage if available
            if "monthly" in usage:
                monthly = usage["monthly"]
                used_monthly = monthly.get("used", 0)
                limit_monthly = monthly.get("limit", 24000)
                percentage_monthly = (used_monthly / limit_monthly) * 100 if limit_monthly > 0 else 0
                
                print(f"📅 Monthly Usage: {used_monthly}/{limit_monthly} credits ({percentage_monthly:.1f}%)")
            
            # Plan info if available
            if "plan" in usage_data:
                plan = usage_data["plan"]
                print(f"📋 Plan: {plan.get('name', 'Unknown')}")
            
            print(f"\n⏰ Last checked: {datetime.now().strftime('%H:%M:%S')}")
            
            return True
            
        else:
            print("❌ Unable to retrieve usage data")
            print(f"Response: {usage_data}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid API response: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_single_api_call():
    """Test a single API call to verify key works"""
    
    api_key = os.getenv("TWELVEDATA_API_KEY")
    
    if not api_key or api_key == "your_api_key_here":
        print("❌ API key not configured for testing")
        return False
    
    print(f"\n🧪 Testing single API call...")
    
    try:
        # Simple price quote test
        url = "https://api.twelvedata.com/price"
        params = {
            "symbol": "EUR/USD",
            "apikey": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if "price" in data:
            price = data["price"]
            print(f"✅ API Test Successful: EUR/USD = {price}")
            print(f"📞 This test used 1 API credit")
            return True
        else:
            print(f"❌ API Test Failed: {data}")
            return False
            
    except Exception as e:
        print(f"❌ API Test Error: {e}")
        return False

def main():
    """Main function to check API usage"""
    print("🚀 TwelveData API Usage Checker")
    print("="*50)
    
    # Check usage
    usage_success = check_twelvedata_usage()
    
    if usage_success:
        print(f"\n✅ Usage check completed successfully")
    else:
        print(f"\n❌ Could not check usage - trying test call...")
        test_single_api_call()
    
    print(f"\n💡 To check usage manually:")
    print(f"1. Go to: https://twelvedata.com/account/api")
    print(f"2. Login to your TwelveData account")
    print(f"3. View your usage dashboard")

if __name__ == "__main__":
    main()
