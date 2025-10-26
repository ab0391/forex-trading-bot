#!/usr/bin/env python3
"""
Test Telegram Integration for Both Trading Bots
"""

import requests
import os
from datetime import datetime

def test_telegram_bot(bot_token, bot_name, chat_id):
    """Test Telegram bot integration"""
    print(f"\n🧪 Testing {bot_name}...")
    
    if not chat_id or chat_id == "your_chat_id_here":
        print(f"⚠️ {bot_name}: Chat ID not configured")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        message = f"""
🚀 <b>{bot_name} Test</b>

✅ Bot is working correctly!
📅 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
🔗 Ready for 24/7 operation

<b>Next Steps:</b>
1. Deploy to Railway
2. Configure environment variables
3. Start trading!
        """
        
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {bot_name}: Telegram test successful!")
            return True
        else:
            print(f"❌ {bot_name}: Telegram test failed - {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {bot_name}: Error - {e}")
        return False

def main():
    print("🚀 Testing Telegram Integration for Trading Bots")
    print("=" * 50)
    
    # Forex Bot Test
    forex_token = "8294375530:AAGpvxGD54ejEt9LXlZejQV8ZxtMxnXb0R8"
    forex_chat_id = os.getenv('TELEGRAM_CHAT_ID', 'your_chat_id_here')
    
    forex_success = test_telegram_bot(
        forex_token, 
        "Forex Trading Bot (@fx_pairs_bot)", 
        forex_chat_id
    )
    
    # Stock Bot Test
    stock_token = "8212205627:AAEpn-8ReZkBtoI4iHJbJxcHn8llSj2JtY4"
    stock_chat_id = os.getenv('TELEGRAM_CHAT_ID', 'your_chat_id_here')
    
    stock_success = test_telegram_bot(
        stock_token, 
        "Stock Trading Bot (@breakout_trading_bot)", 
        stock_chat_id
    )
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Forex Bot: {'✅ PASS' if forex_success else '❌ FAIL'}")
    print(f"Stock Bot: {'✅ PASS' if stock_success else '❌ FAIL'}")
    
    if forex_success and stock_success:
        print("\n🎉 All tests passed! Ready for Railway deployment!")
    else:
        print("\n⚠️ Some tests failed. Check your chat ID configuration.")
        print("💡 Get your chat ID by messaging @userinfobot on Telegram")

if __name__ == "__main__":
    main()
