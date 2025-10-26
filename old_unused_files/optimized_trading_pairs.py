#!/usr/bin/env python3
"""
OPTIMIZED TRADING PAIRS FOR TWELVEDATA LIMITS
- 8 Major Pairs (most liquid and profitable)
- Smart rotation: 2 pairs per cycle = 8 API calls exactly
- Covers all major market sessions
- Stays under 8/minute limit
"""

import os
from dotenv import load_dotenv

load_dotenv()

class OptimizedTradingPairs:
    def __init__(self):
        self.api_key = os.getenv('TWELVEDATA_API_KEY')
        
        # 🎯 OPTIMIZED 8 MAJOR PAIRS
        # Selected for maximum liquidity, volatility, and trading opportunities
        self.all_symbols = [
            # TOP 4 MOST LIQUID PAIRS (scanned every 2 cycles)
            "EUR/USD",   # #1 Most traded pair - European session
            "GBP/USD",   # #2 Most volatile - London session  
            "USD/JPY",   # #3 Safe haven - Asian session
            "AUD/USD",   # #4 Commodity currency - Asian session
            
            # TOP 4 CROSS PAIRS (scanned every 2 cycles)
            "EUR/GBP",   # #1 Most popular cross - London session
            "GBP/JPY",   # #2 Most volatile cross - High movement
            "EUR/JPY",   # #3 Major cross - Good liquidity
            "USD/CHF"    # #4 Safe haven - Swiss session
        ]
        
        # ROTATION SETTINGS
        self.symbols_per_cycle = 2  # 2 pairs × 4 timeframes = 8 API calls exactly
        self.scan_count = 0
        
        print(f"🎯 Optimized Trading Pairs Configuration")
        print(f"📊 Total Pairs: {len(self.all_symbols)}")
        print(f"🔄 Pairs per Cycle: {self.symbols_per_cycle}")
        print(f"⚡ API Calls per Cycle: {self.symbols_per_cycle * 4} (exactly at limit)")
        print(f"🕒 Full Rotation: Every {len(self.all_symbols) // self.symbols_per_cycle} cycles")
        
    def get_symbols_for_current_scan(self):
        """Get symbols for current scan cycle"""
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
        
        print(f"\n🔄 Scan {self.scan_count} (Rotation {cycle_in_rotation}/{total_cycles})")
        print(f"📈 Current Pairs: {', '.join(symbols)}")
        print(f"⚡ API Calls: {len(symbols)} × 4 timeframes = {len(symbols) * 4}")
        
        return symbols
    
    def get_all_symbols(self):
        """Get complete list of all trading pairs"""
        return self.all_symbols.copy()
    
    def get_rotation_info(self):
        """Get detailed rotation information"""
        total_cycles = len(self.all_symbols) // self.symbols_per_cycle
        current_cycle = (self.scan_count - 1) % total_cycles + 1
        
        return {
            'total_pairs': len(self.all_symbols),
            'pairs_per_cycle': self.symbols_per_cycle,
            'total_cycles': total_cycles,
            'current_cycle': current_cycle,
            'api_calls_per_cycle': self.symbols_per_cycle * 4,
            'full_rotation_hours': total_cycles * 0.5  # Assuming 30-min intervals
        }

def test_rotation():
    """Test the rotation system"""
    print("🧪 Testing Optimized Trading Pairs Rotation")
    print("=" * 50)
    
    bot = OptimizedTradingPairs()
    
    print(f"\n📊 All Trading Pairs:")
    for i, pair in enumerate(bot.get_all_symbols(), 1):
        print(f"  {i}. {pair}")
    
    print(f"\n🔄 Testing 8 scan cycles (full rotation):")
    
    # Test full rotation
    for cycle in range(8):
        symbols = bot.get_symbols_for_current_scan()
        time.sleep(0.1)  # Small delay for readability
    
    print(f"\n✅ Rotation test complete!")
    
    info = bot.get_rotation_info()
    print(f"\n📈 Rotation Summary:")
    print(f"  • Total pairs: {info['total_pairs']}")
    print(f"  • Pairs per cycle: {info['pairs_per_cycle']}")
    print(f"  • API calls per cycle: {info['api_calls_per_cycle']}")
    print(f"  • Full rotation time: {info['full_rotation_hours']} hours")
    print(f"  • Cycles per full rotation: {info['total_cycles']}")

if __name__ == "__main__":
    import time
    test_rotation()
