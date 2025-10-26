#!/usr/bin/env python3
"""
Test Telegram Notifications for Trading Bot
Verifies that Telegram alerts work correctly when strategies are met
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv
from complete_enhanced_trading_bot_optimized import TelegramNotifier

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_telegram_configuration():
    """Test Telegram bot configuration"""
    print("🧪 Testing Telegram Configuration")
    print("="*40)
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or bot_token == "your_telegram_token_here":
        print("❌ TELEGRAM_BOT_TOKEN not configured")
        print("💡 Please add your real Telegram bot token to .env file")
        print("💡 Get token from @BotFather on Telegram")
        return False
    
    if not chat_id or chat_id == "your_chat_id_here":
        print("❌ TELEGRAM_CHAT_ID not configured")
        print("💡 Please add your real Telegram chat ID to .env file")
        print("💡 Get chat ID by messaging your bot and checking updates")
        return False
    
    print(f"✅ Bot token configured: {bot_token[:10]}...")
    print(f"✅ Chat ID configured: {chat_id}")
    return True

def test_basic_telegram_message():
    """Test basic Telegram message sending"""
    print("\n🧪 Testing Basic Telegram Message")
    print("="*38)
    
    try:
        notifier = TelegramNotifier()
        
        test_message = f"""
🧪 **TELEGRAM TEST MESSAGE**

📅 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
🤖 Bot: Rate-Limited Trading Bot
🛡️ Status: Testing notifications

This is a test message to verify Telegram notifications are working correctly.
"""
        
        print("📤 Sending test message...")
        success = notifier.send_message(test_message)
        
        if success:
            print("✅ Basic Telegram message sent successfully!")
            print("📱 Check your Telegram to confirm receipt")
            return True
        else:
            print("❌ Failed to send basic Telegram message")
            return False
            
    except Exception as e:
        print(f"❌ Telegram test failed with error: {e}")
        return False

def test_trading_alert_notification():
    """Test trading alert notification format"""
    print("\n🧪 Testing Trading Alert Notification")
    print("="*42)
    
    try:
        notifier = TelegramNotifier()
        
        # Simulate a real trading signal
        test_alert = {
            'symbol': 'EUR/USD',
            'zone_type': 'demand',
            'entry': 1.08567,
            'stop': 1.08234,
            'target': 1.09230,
            'rr': 2.0,
            'bias_info': 'H4 bullish bias confirmed with daily support',
            'current_price': 1.08634
        }
        
        print("📤 Sending trading alert...")
        success = notifier.send_trading_alert(
            symbol=test_alert['symbol'],
            zone_type=test_alert['zone_type'],
            entry=test_alert['entry'],
            stop=test_alert['stop'],
            target=test_alert['target'],
            rr=test_alert['rr'],
            bias_info=test_alert['bias_info'],
            current_price=test_alert['current_price']
        )
        
        if success:
            print("✅ Trading alert sent successfully!")
            print("📱 Check Telegram for formatted trading signal")
            return True
        else:
            print("❌ Failed to send trading alert")
            return False
            
    except Exception as e:
        print(f"❌ Trading alert test failed: {e}")
        return False

def test_spam_prevention():
    """Test spam prevention functionality"""
    print("\n🧪 Testing Spam Prevention")
    print("="*30)
    
    try:
        notifier = TelegramNotifier()
        
        # Send same alert twice rapidly
        test_data = {
            'symbol': 'GBP/USD',
            'zone_type': 'supply',
            'entry': 1.27845,
            'stop': 1.28234,
            'target': 1.27123,
            'rr': 1.85,
            'bias_info': 'H4 bearish bias with daily resistance',
            'current_price': 1.27798
        }
        
        print("📤 Sending first alert...")
        first_result = notifier.send_trading_alert(**test_data)
        
        print("📤 Sending duplicate alert immediately...")
        second_result = notifier.send_trading_alert(**test_data)
        
        if first_result and not second_result:
            print("✅ Spam prevention working correctly!")
            print("✅ First alert sent, duplicate blocked")
            return True
        elif first_result and second_result:
            print("⚠️  Both alerts sent - spam prevention may not be working")
            return False
        else:
            print("❌ First alert failed to send")
            return False
            
    except Exception as e:
        print(f"❌ Spam prevention test failed: {e}")
        return False

def test_telegram_formatting():
    """Test Telegram message formatting"""
    print("\n🧪 Testing Message Formatting")
    print("="*33)
    
    try:
        notifier = TelegramNotifier()
        
        formatted_message = """
🚨 **TRADING SIGNAL ALERT**

📊 **Pair:** USD/JPY
📈 **Type:** DEMAND Zone Entry
💰 **Entry:** 149.234
🛑 **Stop Loss:** 148.567
🎯 **Take Profit:** 150.890
📐 **Risk/Reward:** 2.47:1

📋 **Analysis:**
• H4 timeframe showing bullish bias
• Daily support level confirmed
• Zone formed with clean breakout
• Current price: 149.189

⏰ **Time:** 2025-09-28 16:30:15
🤖 **Bot:** ZoneSync FX Enhanced
"""
        
        print("📤 Sending formatted message...")
        success = notifier.send_message(formatted_message, parse_mode="Markdown")
        
        if success:
            print("✅ Formatted message sent successfully!")
            print("📱 Check Telegram for proper formatting")
            return True
        else:
            print("❌ Failed to send formatted message")
            return False
            
    except Exception as e:
        print(f"❌ Formatting test failed: {e}")
        return False

def run_comprehensive_telegram_test():
    """Run comprehensive Telegram notification tests"""
    print("🚀 Telegram Notifications - Comprehensive Test")
    print("="*50)
    
    tests = [
        ("Configuration Check", test_telegram_configuration),
        ("Basic Message", test_basic_telegram_message),
        ("Trading Alert", test_trading_alert_notification),
        ("Spam Prevention", test_spam_prevention),
        ("Message Formatting", test_telegram_formatting)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            
            # Small delay between tests
            if result:
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📊 Telegram Test Results")
    print("="*30)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TELEGRAM TESTS PASSED!")
        print("✅ Telegram notifications working correctly")
        print("✅ Trading alerts will be sent when strategies are met")
        print("✅ Spam prevention active")
        print("✅ Message formatting working")
        
        print("\n📋 What this means:")
        print("• Your bot will send Telegram alerts for trading signals")
        print("• Duplicate signals are prevented (1-hour cooldown)")
        print("• Messages are properly formatted and readable")
        print("• All notifications are working as expected")
        
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        print("❌ Fix issues before relying on notifications")
        
        if not results.get("Configuration Check"):
            print("💡 Configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
        if not results.get("Basic Message"):
            print("💡 Check bot token and chat ID validity")
        if not results.get("Trading Alert"):
            print("💡 Check trading alert message format")
            
        return False

if __name__ == "__main__":
    print("🔔 Starting Telegram Notification Tests...")
    print("Note: You should receive several test messages on Telegram")
    print("Make sure to check your Telegram app during the test\n")
    
    success = run_comprehensive_telegram_test()
    
    if success:
        print("\n🎯 CONCLUSION:")
        print("Your trading bot is ready to send Telegram notifications")
        print("when trading strategies are met!")
    else:
        print("\n🔧 ACTION REQUIRED:")
        print("Fix the failing tests before deploying the bot")
    
    sys.exit(0 if success else 1)
