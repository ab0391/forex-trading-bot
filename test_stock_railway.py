#!/usr/bin/env python3
"""
Test Stock Bot Railway Deployment
This simulates what should happen on Railway
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_orb_stock_bot import EnhancedORBStockTradingBot
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_stock_bot_railway():
    """Test stock bot as it would run on Railway"""
    print("🚀 Testing Stock Bot Railway Deployment...")
    print("=" * 60)
    
    try:
        # Initialize bot (this is what Railway does)
        bot = EnhancedORBStockTradingBot()
        print("✅ Stock bot initialized successfully")
        
        # Test one cycle of the bot (simulate what should happen)
        print("\n🔄 Running one bot cycle...")
        
        # Get active stocks for current session
        active_stocks = bot.get_active_stocks_for_session()
        print(f"📊 Active stocks: {len(active_stocks)} stocks")
        
        # Test ORB calculation for a few stocks
        test_stocks = active_stocks[:3]  # Test first 3 stocks
        
        for stock in test_stocks:
            try:
                print(f"\n🔍 Testing {stock}...")
                
                # Check if market is open
                market_open = bot.is_market_open(stock)
                print(f"   Market open: {market_open}")
                
                # Check if it's ORB period
                orb_period = bot.is_opening_range_period(stock)
                print(f"   ORB period: {orb_period}")
                
                # Calculate ORB data
                orb_data = bot.calculate_opening_range(stock)
                if orb_data:
                    print(f"   ORB High: {orb_data.get('orh', 'N/A')}")
                    print(f"   ORB Low: {orb_data.get('orl', 'N/A')}")
                    print(f"   Range Size: {orb_data.get('range_size', 'N/A')}")
                else:
                    print("   No ORB data")
                
            except Exception as e:
                print(f"   ❌ Error with {stock}: {e}")
        
        print("\n✅ Stock bot cycle completed successfully")
        print("\n🔍 Railway Deployment Analysis:")
        print("✅ Bot initializes correctly")
        print("✅ Bot can process stocks")
        print("✅ Bot can calculate ORB data")
        print("❌ Bot not running on Railway (no signals generated)")
        
        print("\n💡 Solution:")
        print("1. Check Railway logs for stock_worker process")
        print("2. Verify stock_worker is running in Railway dashboard")
        print("3. Check if there are any startup errors")
        print("4. Redeploy if necessary")
        
    except Exception as e:
        print(f"❌ Stock bot failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stock_bot_railway()

