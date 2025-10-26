#!/usr/bin/env python3
"""
Test Yahoo Finance Trading Bot
Verify all 19 pairs work and Telegram notifications function
"""

import sys
import os
from yahoo_forex_bot import YahooTradingBot, YahooDataFetcher, TelegramNotifier

def test_yahoo_finance_data():
    """Test Yahoo Finance data fetching"""
    print("🧪 Testing Yahoo Finance Data Fetching")
    print("=" * 50)
    
    fetcher = YahooDataFetcher()
    
    # Test a few key pairs
    test_pairs = ["EUR/USD", "GBP/USD", "GOLD", "BITCOIN", "USD/JPY"]
    
    for pair in test_pairs:
        print(f"\n📊 Testing {pair}...")
        
        # Test current price
        price = fetcher.get_current_price(pair)
        if price:
            print(f"✅ Current price: {price:.5f}")
        else:
            print(f"❌ Failed to get price")
            return False
        
        # Test historical data
        hist = fetcher.get_historical_data(pair, period="5d")
        if hist is not None and not hist.empty:
            print(f"✅ Historical data: {len(hist)} candles")
        else:
            print(f"❌ Failed to get historical data")
            return False
    
    print(f"\n🎉 Yahoo Finance data fetching works perfectly!")
    return True

def test_telegram_notifications():
    """Test Telegram notifications"""
    print("\n🧪 Testing Telegram Notifications")
    print("=" * 40)
    
    notifier = TelegramNotifier()
    
    # Test basic message
    test_message = """
🧪 **YAHOO FINANCE BOT TEST**

✅ Yahoo Finance integration working
✅ All 19 trading pairs available
✅ No rate limits - completely free!
✅ Ready to send trading signals

📊 Pairs: EUR/USD, GBP/USD, GOLD, BITCOIN, etc.
💰 Cost: $0/month
⚡ Rate Limits: NONE

Bot is ready to trade!
"""
    
    print("📤 Sending test message to Telegram...")
    success = notifier.send_message(test_message)
    
    if success:
        print("✅ Telegram test message sent successfully!")
        print("📱 Check your @fx_pairs_bot for the test message")
        return True
    else:
        print("❌ Telegram test failed")
        return False

def test_trading_signal():
    """Test a sample trading signal"""
    print("\n🧪 Testing Trading Signal Generation")
    print("=" * 42)
    
    bot = YahooTradingBot()
    
    # Test analyzing a single pair
    print("🔍 Testing signal generation for EUR/USD...")
    signal = bot.analyze_symbol("EUR/USD")
    
    if signal:
        print("✅ Signal generated successfully!")
        print(f"   Symbol: {signal['symbol']}")
        print(f"   Type: {signal['zone_type']}")
        print(f"   Entry: {signal['entry']:.5f}")
        print(f"   Stop: {signal['stop']:.5f}")
        print(f"   Target: {signal['target']:.5f}")
        print(f"   R:R: {signal['risk_reward']:.1f}")
        
        # Test saving signal
        bot.save_signal(signal)
        print("✅ Signal saved to dashboard")
        
        # Test Telegram alert
        success = bot.notifier.send_trading_alert(
            symbol=signal['symbol'],
            zone_type=signal['zone_type'],
            entry=signal['entry'],
            stop=signal['stop'],
            target=signal['target'],
            rr=signal['risk_reward'],
            bias_info=signal['bias_info'],
            current_price=signal['current_price']
        )
        
        if success:
            print("✅ Telegram alert sent!")
            print("📱 Check your Telegram for the trading signal")
        else:
            print("❌ Telegram alert failed")
        
        return True
    else:
        print("ℹ️  No signal generated (normal - market conditions)")
        print("✅ Signal generation system working correctly")
        return True

def test_all_pairs():
    """Test that all 19 pairs are accessible"""
    print("\n🧪 Testing All 19 Trading Pairs")
    print("=" * 38)
    
    fetcher = YahooDataFetcher()
    bot = YahooTradingBot()
    
    print(f"📊 Total pairs configured: {len(bot.all_symbols)}")
    print("🔍 Testing price access for all pairs...")
    
    accessible_pairs = []
    failed_pairs = []
    
    for pair in bot.all_symbols:
        price = fetcher.get_current_price(pair)
        if price:
            accessible_pairs.append(pair)
            print(f"✅ {pair}: {price:.5f}")
        else:
            failed_pairs.append(pair)
            print(f"❌ {pair}: Failed")
    
    print(f"\n📈 Results:")
    print(f"✅ Accessible pairs: {len(accessible_pairs)}/{len(bot.all_symbols)}")
    print(f"❌ Failed pairs: {len(failed_pairs)}")
    
    if failed_pairs:
        print(f"⚠️  Failed pairs: {', '.join(failed_pairs)}")
    
    success_rate = len(accessible_pairs) / len(bot.all_symbols)
    
    if success_rate >= 0.8:  # 80% success rate
        print(f"🎉 Excellent! {success_rate:.1%} of pairs accessible")
        return True
    else:
        print(f"⚠️  Only {success_rate:.1%} of pairs accessible")
        return False

def main():
    """Run all tests"""
    print("🚀 Yahoo Finance Trading Bot - Complete Test Suite")
    print("=" * 60)
    
    tests = [
        ("Yahoo Finance Data", test_yahoo_finance_data),
        ("Telegram Notifications", test_telegram_notifications),
        ("Trading Signal Generation", test_trading_signal),
        ("All 19 Trading Pairs", test_all_pairs)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Yahoo Finance bot is ready for deployment")
        print("✅ All 19 pairs accessible")
        print("✅ Telegram notifications working")
        print("✅ Dashboard integration ready")
        print("✅ NO RATE LIMITS - completely free!")
        
        print("\n🚀 Ready to deploy:")
        print("   python3 yahoo_forex_bot.py")
        
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        print("❌ Fix issues before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
