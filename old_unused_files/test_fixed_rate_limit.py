#!/usr/bin/env python3
"""
Test Fixed Rate Limiting
Verify that the rate limiter now properly prevents 9/8 violations
"""

import time
import logging
from collections import deque
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - RATE_TEST - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestAPICallTracker:
    """Test version of API call tracker"""

    def __init__(self):
        self.calls = deque()

    def record_call(self, source="Test"):
        """Record an API call with timestamp"""
        timestamp = time.time()
        call_info = {
            'timestamp': timestamp,
            'datetime': datetime.fromtimestamp(timestamp),
            'source': source
        }
        self.calls.append(call_info)

        # Keep only last 2 minutes
        cutoff = timestamp - 120
        while self.calls and self.calls[0]['timestamp'] < cutoff:
            self.calls.popleft()

        logger.info(f"📞 API Call {len(self.calls)} from {source} at {call_info['datetime'].strftime('%H:%M:%S')}")

    def check_minute_violations(self):
        """Check for rate limit violations in the last minute"""
        current_time = time.time()
        last_minute = current_time - 60

        recent_calls = [call for call in self.calls if call['timestamp'] > last_minute]

        if len(recent_calls) > 8:
            logger.error(f"🚨 VIOLATION: {len(recent_calls)}/8 calls in last minute!")
            return False
        else:
            logger.info(f"✅ OK: {len(recent_calls)}/8 calls in last minute")
            return True

def test_bot_with_fixed_rate_limiter():
    """Test the fixed bot with proper rate limiting"""
    logger.info("🧪 Testing Bot with Fixed Rate Limiter")
    logger.info("=" * 50)

    try:
        from rate_limiter import enhanced_rate_limiter
        tracker = TestAPICallTracker()

        # Simulate a full bot scan (15 API calls)
        symbols = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF"]
        timeframes = ["1d", "4h", "1h"]

        scan_start = time.time()
        logger.info("🤖 Starting simulated bot scan with rate limiter...")

        call_count = 0
        for symbol in symbols:
            for timeframe in timeframes:
                call_count += 1
                logger.info(f"🔄 Call {call_count}/15: {symbol} {timeframe}")

                # This should wait 8.6 seconds between calls
                enhanced_rate_limiter.wait_for_api_call("TwelveData")
                tracker.record_call(f"{symbol}-{timeframe}")

                # Check for violations after each call
                if not tracker.check_minute_violations():
                    logger.error("❌ Rate limit violation detected!")
                    return False

        scan_duration = time.time() - scan_start
        logger.info("=" * 50)
        logger.info(f"✅ Scan completed in {scan_duration:.1f} seconds")
        logger.info(f"⚡ Made {call_count} calls with proper rate limiting")

        # Final check
        return tracker.check_minute_violations()

    except ImportError:
        logger.error("❌ Rate limiter not available")
        return False

def test_original_bot_pattern():
    """Test the original problematic pattern"""
    logger.info("\n🧪 Testing Original Problematic Pattern")
    logger.info("=" * 50)

    tracker = TestAPICallTracker()

    # Simulate rapid calls (the problem pattern)
    logger.info("🚨 Simulating rapid calls that cause violations...")

    for i in range(12):  # Simulate 12 rapid calls
        tracker.record_call(f"RapidCall-{i+1}")
        time.sleep(0.3)  # Only 0.3 seconds between calls

        if not tracker.check_minute_violations():
            logger.info(f"💥 Violation detected at call {i+1}")
            return False

    return True

def main():
    """Main test function"""
    logger.info("🚀 Rate Limiter Fix Verification")
    logger.info("🎯 Goal: Verify 9/8 violations are eliminated")
    logger.info("=" * 60)

    # Test 1: Original problematic pattern
    logger.info("\n📋 Test 1: Reproduce Original Problem")
    if test_original_bot_pattern():
        logger.error("❌ Original pattern should have caused violations!")
    else:
        logger.info("✅ Original pattern correctly shows violations")

    # Test 2: Fixed bot with rate limiter
    logger.info("\n📋 Test 2: Verify Fixed Rate Limiting")
    if test_bot_with_fixed_rate_limiter():
        logger.info("🎉 SUCCESS: Fixed rate limiter prevents violations!")
        logger.info("✅ Bot can now run without 9/8 credit issues")
        return True
    else:
        logger.error("❌ FAILED: Rate limiter still allows violations")
        return False

if __name__ == "__main__":
    success = main()

    if success:
        logger.info("\n🎉 RATE LIMITER FIX VERIFIED!")
        logger.info("📋 Next Steps:")
        logger.info("1. Deploy fixed bot to Oracle server")
        logger.info("2. Monitor TwelveData dashboard")
        logger.info("3. Verify minutely maximum stays ≤7/8")
    else:
        logger.error("\n❌ Rate limiter fix needs more work")