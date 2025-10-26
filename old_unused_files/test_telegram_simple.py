#!/usr/bin/env python3
"""
Simple Telegram Test for Trading Bot
Tests if your Telegram bot is configured correctly
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_telegram_config():
    """Check and test Telegram configuration"""
    print("🔍 Checking Telegram Configuration...")
    print("=" * 50)
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # Check if configured
    if not bot_token or bot_token == "your_telegram_token_here":
        print("\n❌ TELEGRAM_BOT_TOKEN is not configured!")
        print("\n📝 To fix this:")
        print("1. Open Telegram and search for '@BotFather'")
        print("2. Send: /newbot")
        print("3. Follow instructions to create your bot")
        print("4. Copy the bot token you receive")
        print("5. Update your .env file with the token")
        print("\nExample .env line:")
        print("TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmnoPQRstuVWXyz")
        return False, None, None
    
    if not chat_id or chat_id == "your_chat_id_here":
        print("\n❌ TELEGRAM_CHAT_ID is not configured!")
        print("\n📝 To fix this:")
        print("1. Search for your bot on Telegram (name you gave it)")
        print("2. Send any message to your bot (e.g., /start)")
        print("3. Visit this URL in your browser:")
        print(f"   https://api.telegram.org/bot{bot_token}/getUpdates")
        print("4. Look for 'chat':{'id': YOUR_CHAT_ID}")
        print("5. Copy that number and update your .env file")
        print("\nExample .env line:")
        print("TELEGRAM_CHAT_ID=123456789")
        return False, bot_token, None
    
    print(f"✅ Bot Token: {bot_token[:15]}...")
    print(f"✅ Chat ID: {chat_id}")
    
    return True, bot_token, chat_id

def test_telegram_message(bot_token, chat_id):
    """Send a test message to Telegram"""
    print("\n📤 Sending test message to Telegram...")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    message = """
🎯 **TELEGRAM TEST SUCCESSFUL!**

Your trading bot is now configured to send alerts to Telegram.

✅ Bot is connected
✅ Messages working
✅ Ready to receive trading signals

When your bot finds a trading opportunity, you'll get an alert here!
"""
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("ok"):
            print("✅ Test message sent successfully!")
            print("📱 Check your Telegram app - you should see the message!")
            return True
        else:
            print(f"❌ Telegram API returned error: {result}")
            return False
    
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Check your internet connection.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send message: {e}")
        return False

def main():
    print("\n🤖 Trading Bot - Telegram Configuration Test")
    print("=" * 50)
    
    configured, bot_token, chat_id = check_telegram_config()
    
    if not configured:
        print("\n⚠️  Please configure Telegram settings in your .env file first")
        print("\nYour .env file location:")
        print(f"  {os.path.abspath('.env')}")
        return False
    
    # Test sending message
    success = test_telegram_message(bot_token, chat_id)
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Your Telegram notifications are working correctly")
        print("✅ You will receive alerts when the bot finds trading signals")
        print("✅ No spam - only quality signals that meet all criteria")
        return True
    else:
        print("\n❌ Test failed. Please check your configuration.")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

