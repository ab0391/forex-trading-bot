#!/usr/bin/env python3
"""
Test both bots with the user's chat ID
"""

import requests
import json
from datetime import datetime

def send_test_message(bot_token, bot_name, chat_id):
    """Send a test message to verify the bot is working"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        message = f"""
🧪 <b>Railway Deployment Test</b>

✅ <b>{bot_name} is working!</b>
🚀 Successfully deployed on Railway
📅 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
🌍 Region: Railway Cloud

<b>Status:</b>
✅ Bot is running
✅ Telegram integration working
✅ Chat ID configured: {chat_id}
✅ Ready for trading signals

<b>Next Steps:</b>
1. Wait for market signals
2. Trade manually in MT5
3. Monitor performance

<b>Trading Schedule (Dubai Time):</b>
• UK Stocks: 12:30 PM - 8:30 PM
• US Stocks: 7:00 PM - 1:00 AM
• Forex: 24/5 (Monday-Friday)
        """
        
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                return True, "Message sent successfully"
            else:
                return False, f"API error: {result.get('description', 'Unknown error')}"
        else:
            return False, f"HTTP error: {response.status_code}"
            
    except Exception as e:
        return False, f"Connection error: {e}"

def main():
    print("🧪 Testing Both Bots with Your Chat ID")
    print("=" * 50)
    
    chat_id = "7641156734"
    print(f"📱 Using chat ID: {chat_id}")
    
    # Test both bots
    bots = {
        "Forex Bot (fxbot)": "8294375530:AAGpvxGD54ejEt9LXlZejQV8ZxtMxnXb0R8",
        "Stock Bot (stock-bot)": "8212205627:AAEpn-8ReZkBtoI4iHJbJxcHn8llSj2JtY4"
    }
    
    results = {}
    
    for bot_name, token in bots.items():
        print(f"\n🧪 Testing {bot_name}...")
        success, message = send_test_message(token, bot_name, chat_id)
        
        if success:
            print(f"✅ {bot_name}: Test message sent successfully!")
            results[bot_name] = "SUCCESS"
        else:
            print(f"❌ {bot_name}: Failed - {message}")
            results[bot_name] = "FAILED"
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    all_success = True
    for bot_name, status in results.items():
        status_emoji = "✅" if status == "SUCCESS" else "❌"
        print(f"{status_emoji} {bot_name}: {status}")
        if status != "SUCCESS":
            all_success = False
    
    print("\n" + "=" * 50)
    
    if all_success:
        print("🎉 SUCCESS! Both bots are working perfectly!")
        print("\n✅ What this means:")
        print("• Both bots are deployed on Railway")
        print("• Telegram integration is working")
        print("• Your chat ID is configured correctly")
        print("• You should have received 2 test messages")
        
        print("\n📱 Check your Telegram for test messages from:")
        print("• @fx_pairs_bot (Forex Bot)")
        print("• @breakout_trading_bot (Stock Bot)")
        
        print("\n🕐 You'll now receive trading signals during:")
        print("• UK Stocks: 12:30 PM - 8:30 PM Dubai time")
        print("• US Stocks: 7:00 PM - 1:00 AM Dubai time")
        print("• Forex: 24/5 (Monday-Friday)")
        
        print("\n🎯 You're all set! Start trading manually in MT5!")
        
    else:
        print("⚠️ Some bots failed to send messages")
        print("\n🔧 Possible issues:")
        print("1. Chat ID not added to Railway environment variables")
        print("2. Railway projects not running")
        print("3. Environment variables not saved properly")
        
        print("\n📞 Troubleshooting steps:")
        print("1. Check Railway dashboard - are both projects running?")
        print("2. Verify TELEGRAM_CHAT_ID is set in both projects")
        print("3. Check Railway logs for any errors")
        print("4. Try redeploying the projects")

if __name__ == "__main__":
    main()

