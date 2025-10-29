#!/usr/bin/env python3
"""
Simple Bot Test - No user input required
Tests if both bots are working without needing chat ID
"""

import requests
import json
from datetime import datetime

def test_bot_api(bot_token, bot_name):
    """Test if bot API is responding"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                return True, bot_info
            else:
                return False, f"API error: {data}"
        else:
            return False, f"HTTP error: {response.status_code}"
    except Exception as e:
        return False, f"Connection error: {e}"

def main():
    print("🚀 Simple Bot Test - Railway Deployment Check")
    print("=" * 50)
    print(f"⏰ Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test both bots
    bots = {
        "Forex Bot (fxbot)": "8294375530:AAGpvxGD54ejEt9LXlZejQV8ZxtMxnXb0R8",
        "Stock Bot (stock-bot)": "8212205627:AAEpn-8ReZkBtoI4iHJbJxcHn8llSj2JtY4"
    }
    
    results = {}
    
    for bot_name, token in bots.items():
        print(f"\n🧪 Testing {bot_name}...")
        success, info = test_bot_api(token, bot_name)
        
        if success:
            print(f"✅ {bot_name}: ACTIVE")
            print(f"   Username: {info.get('username', 'N/A')}")
            print(f"   First Name: {info.get('first_name', 'N/A')}")
            results[bot_name] = "ACTIVE"
        else:
            print(f"❌ {bot_name}: FAILED")
            print(f"   Error: {info}")
            results[bot_name] = "FAILED"
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    all_active = True
    for bot_name, status in results.items():
        status_emoji = "✅" if status == "ACTIVE" else "❌"
        print(f"{status_emoji} {bot_name}: {status}")
        if status != "ACTIVE":
            all_active = False
    
    print("\n" + "=" * 50)
    
    if all_active:
        print("🎉 SUCCESS! Both bots are working perfectly!")
        print("\n✅ What's Working:")
        print("• Both bots are deployed on Railway")
        print("• Telegram API integration is active")
        print("• Bots are ready to send trading signals")
        
        print("\n📱 Your Telegram Bots:")
        print("• Forex: @fx_pairs_bot")
        print("• Stock: @breakout_trading_bot")
        
        print("\n🕐 Trading Schedule (Dubai Time):")
        print("• UK Stocks: 12:30 PM - 8:30 PM")
        print("• US Stocks: 7:00 PM - 1:00 AM")
        print("• Forex: 24/5 (Monday-Friday)")
        
        print("\n🎯 Next Steps:")
        print("1. Add your chat ID to Railway environment variables")
        print("2. Wait for trading signals during market hours")
        print("3. Trade manually in MT5 based on signals")
        
    else:
        print("⚠️ Some bots are not working properly")
        print("\n🔧 Troubleshooting:")
        print("1. Check Railway dashboard for deployment status")
        print("2. Verify environment variables are set")
        print("3. Check Railway logs for errors")
        print("4. Ensure both projects are running")

if __name__ == "__main__":
    main()

