#!/usr/bin/env python3
"""
Test Stock Bot Functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_orb_stock_bot import EnhancedORBStockTradingBot
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_stock_bot():
    """Test the stock bot functionality"""
    print("🧪 Testing Stock Bot Functionality...")
    print("=" * 50)
    
    try:
        # Initialize bot
        bot = EnhancedORBStockTradingBot()
        print("✅ Stock bot initialized successfully")
        
        # Test market hours
        print("\n🕐 Testing Market Hours...")
        uk_open = bot.is_market_open("LLOY.L")
        us_open = bot.is_market_open("AAPL")
        
        print(f"UK Market (LLOY.L): {uk_open}")
        print(f"US Market (AAPL): {us_open}")
        
        # Test data fetching
        print("\n📊 Testing Data Fetching...")
        test_stocks = ["AAPL", "TSLA", "LLOY.L"]
        
        for stock in test_stocks:
            try:
                data = bot.get_stock_data(stock)
                if data is not None and len(data) > 0:
                    current_price = data['Close'].iloc[-1]
                    print(f"✅ {stock}: ${current_price:.2f}")
                else:
                    print(f"❌ {stock}: No data")
            except Exception as e:
                print(f"❌ {stock}: Error - {e}")
        
        # Test ORB calculation
        print("\n🎯 Testing ORB Calculation...")
        try:
            orb_data = bot.calculate_opening_range("AAPL")
            if orb_data:
                print("✅ ORB calculation successful!")
                print(f"   Symbol: AAPL")
                print(f"   ORB High: {orb_data.get('orb_high', 'N/A')}")
                print(f"   ORB Low: {orb_data.get('orb_low', 'N/A')}")
                print(f"   Current Price: {orb_data.get('current_price', 'N/A')}")
            else:
                print("❌ No ORB data generated")
        except Exception as e:
            print(f"❌ ORB calculation error: {e}")
        
        # Test market sessions
        print("\n🕐 Testing Trading Sessions...")
        try:
            sessions = bot.get_optimal_trading_sessions()
            print(f"✅ Trading sessions: {sessions}")
        except Exception as e:
            print(f"❌ Session error: {e}")
        
        # Test active stocks
        print("\n📈 Testing Active Stocks...")
        try:
            active_stocks = bot.get_active_stocks_for_session()
            print(f"✅ Active stocks: {len(active_stocks)} stocks")
            if active_stocks:
                print(f"   First few: {active_stocks[:3]}")
        except Exception as e:
            print(f"❌ Active stocks error: {e}")
        
        print("\n" + "=" * 50)
        print("🧪 Stock bot functionality test completed!")
        
    except Exception as e:
        print(f"❌ Stock bot initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stock_bot()
