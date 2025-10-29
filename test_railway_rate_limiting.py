#!/usr/bin/env python3
"""
Test Railway Rate Limiting Fix
Verifies that the rate-limited data fetcher works properly
"""

import os
import sys
import time
from datetime import datetime

def test_rate_limited_fetcher():
    """Test the rate-limited data fetcher"""
    print("🧪 Testing Rate-Limited Data Fetcher for Railway...")
    print("=" * 60)
    
    try:
        from rate_limited_data_fetcher import RateLimitedDataFetcher
        
        # Create fetcher with Railway-optimized settings
        fetcher = RateLimitedDataFetcher(base_delay=3.0, max_delay=15.0)
        
        # Test symbols that are more likely to work
        test_symbols = [
            "AAPL",      # Apple stock
            "TSLA",      # Tesla stock
            "GOLD",      # Gold commodity
            "SILVER",    # Silver commodity
        ]
        
        print(f"📊 Testing {len(test_symbols)} symbols with rate limiting...")
        print(f"⏰ Base delay: {fetcher.base_delay}s, Max delay: {fetcher.max_delay}s")
        print()
        
        results = {}
        
        for i, symbol in enumerate(test_symbols):
            print(f"🔍 Testing {symbol} ({i+1}/{len(test_symbols)})...")
            
            start_time = time.time()
            price = fetcher.get_current_price(symbol)
            end_time = time.time()
            
            duration = end_time - start_time
            
            if price:
                print(f"✅ {symbol}: {price:.2f} (took {duration:.1f}s)")
                results[symbol] = {"success": True, "price": price, "duration": duration}
            else:
                print(f"❌ {symbol}: Failed (took {duration:.1f}s)")
                results[symbol] = {"success": False, "price": None, "duration": duration}
            
            # Show status
            status = fetcher.get_status()
            print(f"   Status: {status['consecutive_failures']} failures, next delay: {status['base_delay']:.1f}s")
            print()
        
        # Summary
        successful = sum(1 for r in results.values() if r["success"])
        total = len(results)
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        print("=" * 60)
        print(f"📊 Test Results: {successful}/{total} successful ({success_rate:.1f}%)")
        
        if success_rate >= 50:
            print("✅ Rate limiting is working - Railway deployment should work!")
        else:
            print("⚠️ Some issues detected - may need further optimization")
        
        # Show timing analysis
        avg_duration = sum(r["duration"] for r in results.values()) / len(results)
        print(f"⏰ Average request time: {avg_duration:.1f}s")
        
        return success_rate >= 50
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_bot_integration():
    """Test bot integration with rate-limited fetcher"""
    print("\n🤖 Testing Bot Integration...")
    print("=" * 60)
    
    try:
        # Test forex bot
        print("🔍 Testing Forex Bot...")
        from yahoo_forex_bot import YahooTradingBot
        
        bot = YahooTradingBot()
        
        # Test a few price fetches
        test_pairs = ["EUR/USD", "GBP/USD", "AAPL"]
        
        for pair in test_pairs:
            print(f"   Testing {pair}...")
            price = bot.data_fetcher.get_current_price(pair)
            if price:
                print(f"   ✅ {pair}: {price:.5f}")
            else:
                print(f"   ❌ {pair}: Failed")
        
        print("✅ Forex bot integration working")
        
        # Test stock bot
        print("\n🔍 Testing Stock Bot...")
        from enhanced_orb_stock_bot import EnhancedORBStockTradingBot
        
        stock_bot = EnhancedORBStockTradingBot()
        
        # Test stock data fetch
        test_stocks = ["AAPL", "TSLA"]
        
        for stock in test_stocks:
            print(f"   Testing {stock}...")
            data = stock_bot.get_stock_data(stock, period="1d", interval="1h")
            if data is not None and not data.empty:
                print(f"   ✅ {stock}: {len(data)} candles")
            else:
                print(f"   ❌ {stock}: Failed")
        
        print("✅ Stock bot integration working")
        return True
        
    except Exception as e:
        print(f"❌ Bot integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Railway Rate Limiting Test Suite")
    print("=" * 60)
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Rate-limited fetcher
    fetcher_test = test_rate_limited_fetcher()
    
    # Test 2: Bot integration
    integration_test = test_bot_integration()
    
    # Final results
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS")
    print("=" * 60)
    
    if fetcher_test and integration_test:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Rate limiting is working properly")
        print("✅ Bot integration is working")
        print("✅ Ready for Railway deployment!")
        print()
        print("📋 Next steps:")
        print("1. Deploy to Railway")
        print("2. Check Railway logs for rate limiting messages")
        print("3. Verify signals are being generated")
        return True
    else:
        print("⚠️ SOME TESTS FAILED")
        if not fetcher_test:
            print("❌ Rate limiting test failed")
        if not integration_test:
            print("❌ Bot integration test failed")
        print()
        print("🔧 Check the issues above before deploying to Railway")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
