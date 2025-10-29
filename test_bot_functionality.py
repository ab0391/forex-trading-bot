#!/usr/bin/env python3
"""
Test Bot Functionality - Check why no signals are being generated
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yahoo_forex_bot import YahooTradingBot
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_bot_functionality():
    """Test the forex bot functionality"""
    print("🧪 Testing Forex Bot Functionality...")
    print("=" * 50)
    
    try:
        # Initialize bot
        bot = YahooTradingBot()
        print("✅ Bot initialized successfully")
        
        # Test market hours checker
        print("\n🕐 Testing Market Hours Checker...")
        market_open, status = bot.market_checker.is_forex_market_open()
        print(f"Market Open: {market_open}")
        print(f"Status: {status}")
        
        # Test data fetcher
        print("\n📊 Testing Data Fetcher...")
        test_symbols = ["EUR/USD", "GBP/USD", "AAPL"]
        
        for symbol in test_symbols:
            try:
                current_price = bot.data_fetcher.get_current_price(symbol)
                if current_price:
                    print(f"✅ {symbol}: ${current_price}")
                else:
                    print(f"❌ {symbol}: No price data")
            except Exception as e:
                print(f"❌ {symbol}: Error - {e}")
        
        # Test zone detector
        print("\n🎯 Testing Zone Detector...")
        try:
            df = bot.data_fetcher.get_historical_data("EUR/USD", "1d", "1mo")
            if df is not None and len(df) > 0:
                zones = bot.zone_detector.find_zones(df)
                print(f"✅ Found {len(zones)} zones for EUR/USD")
                if zones:
                    print(f"   First zone: {zones[0]}")
            else:
                print("❌ No historical data for zone detection")
        except Exception as e:
            print(f"❌ Zone detection error: {e}")
        
        # Test trade tracker
        print("\n📈 Testing Trade Tracker...")
        if bot.trade_tracker:
            print("✅ Trade tracker is available")
            stats = bot.trade_tracker.get_trade_stats()
            print(f"   Active trades: {stats['active_trades']}")
            print(f"   Cooldown trades: {stats['cooldown_trades']}")
        else:
            print("❌ Trade tracker not available")
        
        # Test R:R optimizer
        print("\n🎯 Testing R:R Optimizer...")
        if bot.rr_optimizer:
            print("✅ R:R optimizer is available")
        else:
            print("❌ R:R optimizer not available")
        
        # Test signal generation for one symbol
        print("\n🚀 Testing Signal Generation...")
        try:
            signal = bot.analyze_symbol("EUR/USD")
            if signal:
                print("✅ Signal generated successfully!")
                print(f"   Symbol: {signal['symbol']}")
                print(f"   Direction: {signal['zone_type']}")
                print(f"   Entry: {signal['entry']}")
                print(f"   Stop: {signal['stop']}")
                print(f"   Target: {signal['target']}")
            else:
                print("❌ No signal generated")
        except Exception as e:
            print(f"❌ Signal generation error: {e}")
        
        print("\n" + "=" * 50)
        print("🧪 Bot functionality test completed!")
        
    except Exception as e:
        print(f"❌ Bot initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bot_functionality()

