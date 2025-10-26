#!/usr/bin/env python3
"""
API Credit Optimization Test Script
Tests all optimization components before deployment
"""

import os
import sys
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_yfinance_availability():
    """Test Yahoo Finance installation and functionality"""
    print("🧪 Testing Yahoo Finance availability...")

    try:
        import yfinance as yf
        print("✅ yfinance imported successfully")

        # Test actual price fetch
        ticker = yf.Ticker("EURUSD=X")
        try:
            info = ticker.info
            if 'regularMarketPrice' in info:
                price = info['regularMarketPrice']
                print(f"✅ Yahoo Finance test successful: EURUSD = {price}")
                return True
            else:
                print("⚠️  Yahoo Finance info available but no regularMarketPrice")
        except Exception as e:
            print(f"⚠️  Yahoo Finance info method failed: {e}")

        # Try fast_info method
        try:
            fast_info = ticker.fast_info
            if hasattr(fast_info, 'last_price'):
                price = fast_info.last_price
                print(f"✅ Yahoo Finance fast_info successful: EURUSD = {price}")
                return True
        except Exception as e:
            print(f"⚠️  Yahoo Finance fast_info method failed: {e}")

        # Try history method
        try:
            hist = ticker.history(period="1d", interval="1m")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                print(f"✅ Yahoo Finance history successful: EURUSD = {price}")
                return True
        except Exception as e:
            print(f"⚠️  Yahoo Finance history method failed: {e}")

        return False

    except ImportError:
        print("❌ yfinance not installed")
        print("💡 Install with: pip install yfinance")
        return False
    except Exception as e:
        print(f"❌ Yahoo Finance test failed: {e}")
        return False

def test_cache_manager():
    """Test data cache manager functionality"""
    print("\n🧪 Testing Cache Manager...")

    try:
        from data_cache_manager import cache_manager
        print("✅ Cache manager imported successfully")

        # Test cache directory creation
        cache_dir = Path("/tmp/fxbot_cache")
        if cache_dir.exists():
            print(f"✅ Cache directory exists: {cache_dir}")
        else:
            cache_dir.mkdir(exist_ok=True)
            print(f"✅ Cache directory created: {cache_dir}")

        # Test price caching
        test_symbol = "EUR/USD"
        test_price = 1.08567

        cache_manager.save_price_to_cache(test_symbol, test_price)
        cached_price = cache_manager.get_cached_price(test_symbol)

        if cached_price == test_price:
            print(f"✅ Price caching works: {test_symbol} = {cached_price}")
        else:
            print(f"❌ Price caching failed: expected {test_price}, got {cached_price}")
            return False

        # Test cache validity
        if cache_manager.is_cache_valid(cache_manager._get_cache_key(test_symbol, "price", 1), "price"):
            print("✅ Cache validity check works")
        else:
            print("❌ Cache validity check failed")
            return False

        return True

    except ImportError as e:
        print(f"❌ Cache manager import failed: {e}")
        print("💡 Make sure data_cache_manager.py is in the same directory")
        return False
    except Exception as e:
        print(f"❌ Cache manager test failed: {e}")
        return False

def test_optimized_bot_import():
    """Test optimized bot can be imported"""
    print("\n🧪 Testing Optimized Bot Import...")

    try:
        # Add current directory to path for imports
        sys.path.insert(0, os.getcwd())

        # Test importing the optimized bot
        from complete_enhanced_trading_bot_optimized import DataFetcher, EnhancedTradingBot
        print("✅ Optimized bot imported successfully")

        # Test DataFetcher initialization
        data_fetcher = DataFetcher()
        print("✅ DataFetcher initialized successfully")

        # Check optimized sizes
        expected_sizes = {"1d": 250, "4h": 400, "1h": 300}
        if hasattr(data_fetcher, 'optimized_outputsize'):
            actual_sizes = data_fetcher.optimized_outputsize
            if actual_sizes == expected_sizes:
                print(f"✅ Optimized data sizes correct: {actual_sizes}")
            else:
                print(f"⚠️  Optimized sizes differ: expected {expected_sizes}, got {actual_sizes}")
        else:
            print("❌ Optimized outputsize not found in DataFetcher")
            return False

        # Test bot initialization
        bot = EnhancedTradingBot()
        print("✅ EnhancedTradingBot initialized successfully")

        return True

    except ImportError as e:
        print(f"❌ Optimized bot import failed: {e}")
        print("💡 Make sure complete_enhanced_trading_bot_optimized.py exists")
        return False
    except Exception as e:
        print(f"❌ Optimized bot test failed: {e}")
        return False

def test_timer_configuration():
    """Test timer configuration file"""
    print("\n🧪 Testing Timer Configuration...")

    timer_script = Path("deploy_timer_fix.sh")
    if not timer_script.exists():
        print("❌ deploy_timer_fix.sh not found")
        return False

    print("✅ deploy_timer_fix.sh exists")

    # Check if script contains the correct timer setting
    try:
        with open(timer_script, 'r') as f:
            content = f.read()

        if "OnUnitActiveSec=30min" in content:
            print("✅ Timer configured for 30 minutes")
        else:
            print("❌ Timer not configured for 30 minutes")
            return False

        if "every 30 minutes" in content.lower():
            print("✅ Timer description mentions 30 minutes")
        else:
            print("⚠️  Timer description doesn't mention 30 minutes")

        return True

    except Exception as e:
        print(f"❌ Timer configuration test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("🚀 API Credit Optimization - Comprehensive Test")
    print("=" * 50)

    results = {}

    # Run all tests
    results['yfinance'] = test_yfinance_availability()
    results['cache'] = test_cache_manager()
    results['bot'] = test_optimized_bot_import()
    results['timer'] = test_timer_configuration()

    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.upper():<15} {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Ready for deployment to Oracle server")
        print("\n📋 Next Steps:")
        print("1. Upload files to Oracle server")
        print("2. Install yfinance: pip install yfinance")
        print("3. Run: sudo ./deploy_timer_fix.sh")
        print("4. Deploy optimized bot")
        print("5. Monitor API usage reduction")

        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        print("❌ Fix issues before deployment")

        if not results['yfinance']:
            print("💡 Install yfinance: pip install yfinance")
        if not results['cache']:
            print("💡 Check data_cache_manager.py exists and is correct")
        if not results['bot']:
            print("💡 Check complete_enhanced_trading_bot_optimized.py exists")
        if not results['timer']:
            print("💡 Check deploy_timer_fix.sh exists and has correct settings")

        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)