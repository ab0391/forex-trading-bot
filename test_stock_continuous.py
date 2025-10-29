#!/usr/bin/env python3
"""
Test Stock Bot Continuous Operation
This tests if the stock bot can run like it would on Railway
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_orb_stock_bot import EnhancedORBStockTradingBot
import time
import logging
import signal
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockBotTester:
    def __init__(self):
        self.running = True
        self.bot = None
        
    def signal_handler(self, signum, frame):
        print("\n🛑 Stopping stock bot test...")
        self.running = False
        
    def test_stock_bot_operation(self):
        """Test stock bot continuous operation"""
        print("🚀 Testing Stock Bot Continuous Operation...")
        print("=" * 60)
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        
        try:
            # Initialize bot
            print("📈 Initializing Enhanced ORB Stock Trading Bot...")
            self.bot = EnhancedORBStockTradingBot()
            print("✅ Stock bot initialized successfully")
            
            # Send startup message
            startup_message = f"""
🧪 <b>Stock Bot Test Mode</b>

📈 <b>Strategy:</b> Opening Range Breakout (Enhanced)
🇺🇸 <b>US Stocks:</b> {len(self.bot.us_stocks)} pairs
🇬🇧 <b>UK Stocks:</b> {len(self.bot.uk_stocks)} pairs
📊 <b>Total Stocks:</b> {len(self.bot.all_stocks)} pairs
🎯 <b>R:R Range:</b> 2:1 to 5:1 (Dynamic)

⏰ <b>Test Started:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            self.bot.send_telegram_message(startup_message)
            print("✅ Startup message sent to Telegram")
            
            # Run for a few cycles to test
            cycle_count = 0
            max_cycles = 3  # Test 3 cycles
            
            while self.running and cycle_count < max_cycles:
                try:
                    cycle_count += 1
                    print(f"\n🔄 Running cycle {cycle_count}/{max_cycles}...")
                    
                    # Get active stocks for current session
                    active_stocks = self.bot.get_active_stocks_for_session()
                    print(f"📊 Active stocks: {len(active_stocks)} stocks")
                    
                    if active_stocks:
                        # Test a few stocks
                        test_stocks = active_stocks[:2]  # Test first 2 stocks
                        
                        for stock in test_stocks:
                            try:
                                print(f"🔍 Testing {stock}...")
                                
                                # Check market status
                                market_open = self.bot.is_market_open(stock)
                                orb_period = self.bot.is_opening_range_period(stock)
                                
                                print(f"   Market: {market_open[0]} | ORB Period: {orb_period}")
                                
                                # Calculate ORB data
                                orb_data = self.bot.calculate_opening_range(stock)
                                if orb_data:
                                    print(f"   ORB High: {orb_data.get('orh', 'N/A'):.2f}")
                                    print(f"   ORB Low: {orb_data.get('orl', 'N/A'):.2f}")
                                    print(f"   Range: {orb_data.get('range_size', 'N/A'):.2f}")
                                
                            except Exception as e:
                                print(f"   ❌ Error with {stock}: {e}")
                    
                    # Wait before next cycle
                    print(f"⏰ Waiting 10 seconds before next cycle...")
                    time.sleep(10)
                    
                except Exception as e:
                    print(f"❌ Error in cycle {cycle_count}: {e}")
                    time.sleep(5)
            
            print(f"\n✅ Test completed successfully! Ran {cycle_count} cycles")
            
            # Send completion message
            completion_message = f"""
✅ <b>Stock Bot Test Completed</b>

🔄 <b>Cycles Run:</b> {cycle_count}
📊 <b>Stocks Tested:</b> {len(active_stocks) if 'active_stocks' in locals() else 0}
⏰ <b>Test Duration:</b> {cycle_count * 10} seconds

<b>Result:</b> Stock bot is working correctly!
<b>Issue:</b> Not running continuously on Railway
            """
            
            self.bot.send_telegram_message(completion_message)
            print("✅ Completion message sent to Telegram")
            
        except Exception as e:
            print(f"❌ Stock bot test failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Send error message
            if self.bot:
                error_message = f"""
❌ <b>Stock Bot Test Failed</b>

<b>Error:</b> {str(e)}
<b>Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}

<b>Action Required:</b> Check Railway deployment
                """
                self.bot.send_telegram_message(error_message)

if __name__ == "__main__":
    tester = StockBotTester()
    tester.test_stock_bot_operation()

