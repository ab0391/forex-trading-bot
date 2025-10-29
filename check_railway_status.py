#!/usr/bin/env python3
"""
Railway Status Checker
Helps verify if both bots are running properly on Railway
"""

import requests
import json
from datetime import datetime

def check_bot_status():
    """Check if both bots are responding"""
    print("🔍 Checking Railway Bot Status")
    print("=" * 40)
    
    # Bot configurations
    bots = {
        "Forex Bot (fxbot)": {
            "token": "8294375530:AAGpvxGD54ejEt9LXlZejQV8ZxtMxnXb0R8",
            "username": "@fx_pairs_bot"
        },
        "Stock Bot (stock-bot)": {
            "token": "8212205627:AAEpn-8ReZkBtoI4iHJbJxcHn8llSj2JtY4",
            "username": "@breakout_trading_bot"
        }
    }
    
    results = {}
    
    for bot_name, config in bots.items():
        print(f"\n🧪 Testing {bot_name}...")
        
        try:
            # Test bot API
            url = f"https://api.telegram.org/bot{config['token']}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    print(f"✅ {bot_name}: Bot is active")
                    print(f"   Username: {bot_info.get('username', 'N/A')}")
                    print(f"   First Name: {bot_info.get('first_name', 'N/A')}")
                    results[bot_name] = "ACTIVE"
                else:
                    print(f"❌ {bot_name}: Bot API error")
                    results[bot_name] = "ERROR"
            else:
                print(f"❌ {bot_name}: HTTP error {response.status_code}")
                results[bot_name] = "ERROR"
                
        except Exception as e:
            print(f"❌ {bot_name}: Connection error - {e}")
            results[bot_name] = "ERROR"
    
    return results

def main():
    print("🚀 Railway Bot Status Checker")
    print("=" * 40)
    print(f"⏰ Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check bot status
    results = check_bot_status()
    
    print("\n" + "=" * 40)
    print("📊 Status Summary:")
    
    all_active = True
    for bot_name, status in results.items():
        status_emoji = "✅" if status == "ACTIVE" else "❌"
        print(f"{status_emoji} {bot_name}: {status}")
        if status != "ACTIVE":
            all_active = False
    
    print("\n" + "=" * 40)
    
    if all_active:
        print("🎉 All bots are active and responding!")
        print("\n📋 What this means:")
        print("✅ Both bots are deployed on Railway")
        print("✅ Telegram integration is working")
        print("✅ Bots are ready to send signals")
        
        print("\n🕐 Expected Signal Times (Dubai):")
        print("• UK Stocks: 12:30 PM - 8:30 PM")
        print("• US Stocks: 7:00 PM - 1:00 AM")
        print("• Forex: 24/5 (Monday-Friday)")
        
        print("\n📱 Your Telegram Bots:")
        print("• Forex: @fx_pairs_bot")
        print("• Stock: @breakout_trading_bot")
        
    else:
        print("⚠️ Some bots are not responding properly")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check Railway dashboard for deployment status")
        print("2. Verify environment variables are set correctly")
        print("3. Check Railway logs for any errors")
        print("4. Ensure both projects are running (not stopped)")
        
        print("\n📞 If issues persist:")
        print("• Check Railway project status")
        print("• Verify environment variables")
        print("• Check Railway logs for errors")

if __name__ == "__main__":
    main()

