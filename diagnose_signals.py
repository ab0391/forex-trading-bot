#!/usr/bin/env python3
"""
Test Signal Generation - Check why no signals are being sent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yahoo_forex_bot import YahooTradingBot
from enhanced_orb_stock_bot import EnhancedORBStockTradingBot
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_signal_generation():
    """Test why no signals are being generated"""
    print("🔍 Diagnosing Signal Generation Issues...")
    print("=" * 60)
    
    # Test Forex Bot
    print("\n📊 Testing Forex Bot Signal Generation...")
    try:
        forex_bot = YahooTradingBot()
        
        # Check if there are active trades preventing signals
        if forex_bot.trade_tracker:
            stats = forex_bot.trade_tracker.get_trade_stats()
            print(f"Active trades: {stats['active_trades']}")
            print(f"Cooldown trades: {stats['cooldown_trades']}")
            print(f"Active symbols: {stats['active_symbols']}")
            
            if stats['active_trades'] > 0:
                print("⚠️ Forex bot has active trades - this prevents new signals")
                print("   This is working as designed (no contradictory signals)")
            else:
                print("✅ No active trades - forex bot should generate signals")
        
        # Test a few symbols
        test_symbols = ["EUR/USD", "GBP/USD", "USD/JPY"]
        signals_generated = 0
        
        for symbol in test_symbols:
            try:
                signal = forex_bot.analyze_symbol(symbol)
                if signal:
                    signals_generated += 1
                    print(f"✅ Generated signal for {symbol}")
                else:
                    print(f"❌ No signal for {symbol}")
            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {e}")
        
        print(f"📊 Forex signals generated: {signals_generated}/{len(test_symbols)}")
        
    except Exception as e:
        print(f"❌ Forex bot error: {e}")
    
    # Test Stock Bot
    print("\n📈 Testing Stock Bot Signal Generation...")
    try:
        stock_bot = EnhancedORBStockTradingBot()
        
        # Check market sessions
        sessions = stock_bot.get_optimal_trading_sessions()
        print(f"UK Session: {sessions['uk_session']}")
        print(f"US Session: {sessions['us_session']}")
        print(f"Dubai Time: {sessions['dubai_time']}")
        
        # Check if it's opening range period
        test_stocks = ["AAPL", "TSLA"]
        for stock in test_stocks:
            is_orb_period = stock_bot.is_opening_range_period(stock)
            print(f"{stock} ORB period: {is_orb_period}")
        
        # Test ORB calculation
        orb_data = stock_bot.calculate_opening_range("AAPL")
        if orb_data:
            print(f"✅ AAPL ORB data available")
            print(f"   ORB High: {orb_data.get('orb_high', 'N/A')}")
            print(f"   ORB Low: {orb_data.get('orb_low', 'N/A')}")
        else:
            print("❌ No ORB data for AAPL")
        
    except Exception as e:
        print(f"❌ Stock bot error: {e}")
    
    print("\n" + "=" * 60)
    print("🔍 Diagnosis Summary:")
    print("1. Check if bots are running continuously on Railway")
    print("2. Check Railway logs for any errors")
    print("3. Verify market hours and trading conditions")
    print("4. Check if trade tracker is preventing signals")

if __name__ == "__main__":
    test_signal_generation()

