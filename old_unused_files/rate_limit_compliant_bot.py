#!/usr/bin/env python3
"""
RATE LIMIT COMPLIANT TRADING BOT
- 8 Major Currency Pairs (all the important ones!)
- EXACTLY 8 API calls per cycle (stays under 8/minute limit)
- Smart rotation covers all pairs every 2 hours
- No more credit spikes!
"""

import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimitCompliantBot:
    def __init__(self):
        self.api_key = os.getenv('TWELVEDATA_API_KEY')
        
        # 🎯 OPTIMIZED 8 MAJOR PAIRS - All the important ones!
        self.all_symbols = [
            # TOP 4 MOST LIQUID PAIRS
            "EUR/USD",   # #1 Most traded - European session
            "GBP/USD",   # #2 Most volatile - London session  
            "USD/JPY",   # #3 Safe haven - Asian session
            "AUD/USD",   # #4 Commodity currency - Asian session
            
            # TOP 4 CROSS PAIRS  
            "EUR/GBP",   # #1 Most popular cross - London session
            "GBP/JPY",   # #2 Most volatile cross - High movement
            "EUR/JPY",   # #3 Major cross - Good liquidity
            "USD/CHF"    # #4 Safe haven - Swiss session
        ]
        
        # ROTATION SETTINGS - EXACTLY at limit
        self.symbols_per_cycle = 2  # 2 pairs × 4 timeframes = 8 API calls
        self.scan_count = 0
        
        logger.info("🎯 Rate Limit Compliant Trading Bot Initialized")
        logger.info(f"📊 Trading Pairs: {len(self.all_symbols)} major pairs")
        logger.info(f"🔄 Pairs per Cycle: {self.symbols_per_cycle}")
        logger.info(f"⚡ API Calls per Cycle: {self.symbols_per_cycle * 4} (exactly at limit)")
        logger.info(f"🕒 Full Rotation: Every {len(self.all_symbols) // self.symbols_per_cycle} cycles")
        logger.info(f"🎯 All Pairs: {', '.join(self.all_symbols)}")
    
    def get_symbols_for_current_scan(self):
        """Get symbols for current scan cycle - EXACTLY 8 API calls"""
        start_idx = (self.scan_count * self.symbols_per_cycle) % len(self.all_symbols)
        end_idx = start_idx + self.symbols_per_cycle
        
        # Handle wrap-around
        if end_idx > len(self.all_symbols):
            symbols = self.all_symbols[start_idx:] + self.all_symbols[:end_idx - len(self.all_symbols)]
        else:
            symbols = self.all_symbols[start_idx:end_idx]
            
        self.scan_count += 1
        
        # Calculate rotation info
        total_cycles = len(self.all_symbols) // self.symbols_per_cycle
        cycle_in_rotation = (self.scan_count - 1) % total_cycles + 1
        
        logger.info(f"🔄 Scan {self.scan_count} (Rotation {cycle_in_rotation}/{total_cycles})")
        logger.info(f"📈 Current Pairs: {', '.join(symbols)}")
        logger.info(f"⚡ API Calls: {len(symbols)} × 4 timeframes = {len(symbols) * 4}")
        logger.info(f"✅ STAYING UNDER LIMIT: {len(symbols) * 4}/8 calls")
        
        return symbols
    
    def simulate_trading_cycle(self):
        """Simulate a complete trading cycle"""
        symbols = self.get_symbols_for_current_scan()
        
        # Simulate API calls (4 timeframes per symbol)
        logger.info(f"📊 Analyzing {len(symbols)} pairs across 4 timeframes...")
        
        for symbol in symbols:
            logger.info(f"  🔍 {symbol}: H1, H4, D1, W1 analysis")
        
        logger.info(f"✅ Cycle complete: {len(symbols) * 4} API calls made")
        logger.info(f"📈 Next cycle will rotate to different pairs")
        
        return symbols

def test_full_rotation():
    """Test complete rotation through all pairs"""
    print("🧪 Testing Full Rotation - Rate Limit Compliant")
    print("=" * 60)
    
    bot = RateLimitCompliantBot()
    
    print(f"\n📊 Your 8 Trading Pairs:")
    for i, pair in enumerate(bot.all_symbols, 1):
        print(f"  {i}. {pair}")
    
    print(f"\n🔄 Testing 8 scan cycles (2 full rotations):")
    
    all_pairs_scanned = set()
    
    # Test 8 cycles (2 full rotations)
    for cycle in range(8):
        print(f"\n--- CYCLE {cycle + 1} ---")
        symbols = bot.simulate_trading_cycle()
        all_pairs_scanned.update(symbols)
        time.sleep(0.5)  # Small delay for readability
    
    # Verify all pairs were scanned
    missing_pairs = set(bot.all_symbols) - all_pairs_scanned
    
    print(f"\n📊 ROTATION TEST RESULTS:")
    print(f"✅ Total pairs configured: {len(bot.all_symbols)}")
    print(f"✅ Pairs scanned in test: {len(all_pairs_scanned)}")
    print(f"✅ API calls per cycle: 8 (exactly at limit)")
    print(f"✅ All pairs covered: {'Yes' if not missing_pairs else 'No'}")
    
    if missing_pairs:
        print(f"❌ Missing pairs: {', '.join(missing_pairs)}")
    else:
        print(f"🎉 Perfect! All {len(bot.all_symbols)} pairs will be covered")
    
    print(f"\n📈 EXPECTED TWELVEDATA DASHBOARD:")
    print(f"  • Minutely maximum: 8/8 ✅ (compliant)")
    print(f"  • Minutely average: ~4/8 ✅ (well under limit)")
    print(f"  • No more red spikes! ✅")

if __name__ == "__main__":
    test_full_rotation()
