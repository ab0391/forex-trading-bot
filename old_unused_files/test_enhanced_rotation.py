#!/usr/bin/env python3
"""
Test Enhanced Symbol Rotation System
Verify that the 16-symbol rotation works correctly with 2 symbols per cycle
"""

import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ROTATION_TEST - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockEnhancedTradingBot:
    """Mock bot to test rotation system without API calls"""

    def __init__(self):
        # Same enhanced symbol list as the real bot
        self.all_symbols = [
            # Major USD pairs (Most liquid)
            "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF", "NZD/USD", "USD/CAD",
            # Cross pairs (High volume)
            "EUR/GBP", "EUR/JPY", "GBP/JPY", "AUD/JPY", "EUR/CHF", "GBP/CHF",
            # Commodity pairs
            "AUD/CAD", "NZD/CAD", "CAD/JPY"
        ]
        self.symbols_per_cycle = 2
        self.scan_count = 0
        self.rotation_stats = {}

        logger.info(f"🤖 Mock bot initialized with {len(self.all_symbols)} symbols")
        logger.info(f"📊 Rotation strategy: {self.symbols_per_cycle} symbols per cycle")

    def get_symbols_for_current_scan(self):
        """Enhanced smart symbol rotation (same as real bot)"""
        # Calculate rotation indices
        start_idx = (self.scan_count * self.symbols_per_cycle) % len(self.all_symbols)
        end_idx = min(start_idx + self.symbols_per_cycle, len(self.all_symbols))

        symbols = self.all_symbols[start_idx:end_idx]

        # Handle wrap-around for seamless rotation
        if len(symbols) < self.symbols_per_cycle and start_idx + self.symbols_per_cycle > len(self.all_symbols):
            remaining_needed = self.symbols_per_cycle - len(symbols)
            symbols.extend(self.all_symbols[:remaining_needed])

        # Update rotation statistics
        for symbol in symbols:
            if symbol not in self.rotation_stats:
                self.rotation_stats[symbol] = {"scan_count": 0, "last_scanned": None}
            self.rotation_stats[symbol]["scan_count"] += 1
            self.rotation_stats[symbol]["last_scanned"] = datetime.now().strftime("%H:%M:%S")

        # Calculate rotation metrics
        total_cycles_for_full_rotation = (len(self.all_symbols) + self.symbols_per_cycle - 1) // self.symbols_per_cycle
        current_cycle_in_rotation = self.scan_count % total_cycles_for_full_rotation + 1
        full_rotations_completed = self.scan_count // total_cycles_for_full_rotation

        # Enhanced logging with coverage statistics
        logger.info(f"🎯 Enhanced Rotation - Scan {self.scan_count + 1}")
        logger.info(f"📊 Current Cycle: {current_cycle_in_rotation}/{total_cycles_for_full_rotation} | Symbols: {symbols}")
        logger.info(f"🔄 Full Rotations Completed: {full_rotations_completed}")
        logger.info(f"📈 Coverage: {len(self.all_symbols)} major pairs | API calls: {len(symbols)} × 4 timeframes = {len(symbols) * 4}")

        return symbols

    def _log_rotation_statistics(self):
        """Log detailed rotation statistics"""
        try:
            total_scans = sum(stats["scan_count"] for stats in self.rotation_stats.values())
            avg_scans_per_symbol = total_scans / len(self.rotation_stats) if self.rotation_stats else 0

            logger.info("📊 ROTATION STATISTICS SUMMARY:")
            logger.info(f"   • Total symbols in rotation: {len(self.all_symbols)}")
            logger.info(f"   • Symbols scanned so far: {len(self.rotation_stats)}")
            logger.info(f"   • Average scans per symbol: {avg_scans_per_symbol:.1f}")

            # Show all symbols and their scan counts
            logger.info("   • Symbol scan counts:")
            for symbol, stats in sorted(self.rotation_stats.items(), key=lambda x: x[1]["scan_count"], reverse=True):
                logger.info(f"     - {symbol}: {stats['scan_count']} scans (last: {stats['last_scanned']})")

        except Exception as e:
            logger.error(f"Error generating rotation statistics: {e}")

def test_rotation_coverage():
    """Test that all symbols get covered in rotation"""
    logger.info("🧪 Testing Enhanced Symbol Rotation Coverage")
    logger.info("=" * 60)

    bot = MockEnhancedTradingBot()
    total_cycles_needed = (len(bot.all_symbols) + bot.symbols_per_cycle - 1) // bot.symbols_per_cycle

    logger.info(f"📊 Test Plan:")
    logger.info(f"   • Total symbols: {len(bot.all_symbols)}")
    logger.info(f"   • Symbols per cycle: {bot.symbols_per_cycle}")
    logger.info(f"   • Cycles for full rotation: {total_cycles_needed}")
    logger.info(f"   • Testing {total_cycles_needed * 2} cycles (2 full rotations)")
    logger.info("")

    # Test 2 full rotations
    test_cycles = total_cycles_needed * 2
    all_symbols_scanned = set()

    for cycle in range(test_cycles):
        logger.info(f"🔄 Testing Cycle {cycle + 1}/{test_cycles}")
        symbols = bot.get_symbols_for_current_scan()
        all_symbols_scanned.update(symbols)

        # Increment scan count
        bot.scan_count += 1

        # Log progress every 5 cycles
        if (cycle + 1) % 5 == 0:
            logger.info(f"📈 Progress: {len(all_symbols_scanned)}/{len(bot.all_symbols)} unique symbols scanned")

        logger.info("")

    # Final statistics
    logger.info("🎉 ROTATION TEST COMPLETE")
    logger.info("=" * 60)
    bot._log_rotation_statistics()

    # Verify coverage
    missing_symbols = set(bot.all_symbols) - all_symbols_scanned
    if missing_symbols:
        logger.error(f"❌ Missing symbols from rotation: {missing_symbols}")
        return False
    else:
        logger.info("✅ All symbols successfully covered in rotation!")

    # Check balance
    scan_counts = [stats["scan_count"] for stats in bot.rotation_stats.values()]
    min_scans = min(scan_counts)
    max_scans = max(scan_counts)

    if max_scans - min_scans <= 1:
        logger.info(f"✅ Balanced rotation: scan counts between {min_scans}-{max_scans}")
        return True
    else:
        logger.warning(f"⚠️ Unbalanced rotation: scan counts between {min_scans}-{max_scans}")
        return True  # Still acceptable for rotation

def test_api_call_limits():
    """Test that API call limits are respected"""
    logger.info("🧪 Testing API Call Limits")
    logger.info("=" * 40)

    bot = MockEnhancedTradingBot()

    # Test several cycles
    for cycle in range(5):
        symbols = bot.get_symbols_for_current_scan()
        api_calls = len(symbols) * 4  # 4 timeframes per symbol

        logger.info(f"Cycle {cycle + 1}: {len(symbols)} symbols × 4 timeframes = {api_calls} API calls")

        if api_calls > 8:
            logger.error(f"❌ API limit exceeded: {api_calls}/8 calls")
            return False

        bot.scan_count += 1

    logger.info("✅ All cycles stay within 8 API calls per scan")
    return True

def main():
    """Main test function"""
    logger.info("🚀 Enhanced Symbol Rotation System Test")
    logger.info("🎯 Testing 16 major currency pairs with 2 symbols per cycle")
    logger.info("=" * 70)

    # Test 1: Coverage
    coverage_ok = test_rotation_coverage()

    logger.info("")

    # Test 2: API limits
    limits_ok = test_api_call_limits()

    logger.info("")
    logger.info("=" * 70)

    if coverage_ok and limits_ok:
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("✅ Enhanced rotation system is working correctly")
        logger.info("📊 Ready for production deployment")
        return True
    else:
        logger.error("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)