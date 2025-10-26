#!/usr/bin/env python3
"""
Debug Minutely Rate Limit Violations
Investigate why 9 calls are being made in a single minute
"""

import os
import sys
import time
import requests
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - RATE_DEBUG - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APICallTracker:
    """Track API calls to identify burst patterns"""

    def __init__(self):
        self.calls = deque()
        self.lock = threading.Lock()

    def record_call(self, source="Unknown"):
        """Record an API call with timestamp"""
        with self.lock:
            timestamp = time.time()
            call_info = {
                'timestamp': timestamp,
                'datetime': datetime.fromtimestamp(timestamp),
                'source': source
            }
            self.calls.append(call_info)

            # Keep only last 2 minutes of calls
            cutoff = timestamp - 120
            while self.calls and self.calls[0]['timestamp'] < cutoff:
                self.calls.popleft()

            logger.info(f"🔍 API Call tracked from {source} at {call_info['datetime'].strftime('%H:%M:%S')}")

    def analyze_patterns(self):
        """Analyze call patterns to find rate limit violations"""
        with self.lock:
            if not self.calls:
                logger.info("📊 No API calls recorded")
                return

            logger.info("📊 API Call Pattern Analysis")
            logger.info("=" * 50)

            # Group calls by minute
            minute_groups = defaultdict(list)
            for call in self.calls:
                minute_key = call['datetime'].strftime('%H:%M')
                minute_groups[minute_key].append(call)

            # Check each minute for violations
            violations = []
            for minute, calls_in_minute in minute_groups.items():
                call_count = len(calls_in_minute)

                if call_count > 8:
                    violations.append({
                        'minute': minute,
                        'count': call_count,
                        'calls': calls_in_minute
                    })
                    logger.error(f"🚨 VIOLATION: {call_count}/8 calls in minute {minute}")

                    # Show sources of calls in violation
                    sources = defaultdict(int)
                    for call in calls_in_minute:
                        sources[call['source']] += 1

                    for source, count in sources.items():
                        logger.error(f"   📞 {source}: {count} calls")

                else:
                    logger.info(f"✅ OK: {call_count}/8 calls in minute {minute}")

            if violations:
                logger.error(f"\n🚨 FOUND {len(violations)} RATE LIMIT VIOLATIONS")

                # Identify most problematic sources
                violation_sources = defaultdict(int)
                for violation in violations:
                    for call in violation['calls']:
                        violation_sources[call['source']] += 1

                logger.error("📊 Sources causing violations:")
                for source, count in sorted(violation_sources.items(), key=lambda x: x[1], reverse=True):
                    logger.error(f"   🔥 {source}: {count} violation calls")

            else:
                logger.info("✅ No rate limit violations found")

# Global tracker instance
call_tracker = APICallTracker()

def simulate_current_bot_pattern():
    """Simulate the current bot's API call pattern"""
    logger.info("🧪 Simulating current bot API call pattern...")

    # Simulate 5 symbols × 3 timeframes = 15 calls
    symbols = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF"]
    timeframes = ["1d", "4h", "1h"]

    for symbol in symbols:
        for timeframe in timeframes:
            call_tracker.record_call(f"DataFetcher-{symbol}-{timeframe}")
            # Small delay as rate limiter would enforce
            time.sleep(0.5)  # This might be too short!

    # Current price calls
    for symbol in symbols:
        call_tracker.record_call(f"CurrentPrice-{symbol}")
        time.sleep(0.2)  # Very short delay

def test_rate_limiter_effectiveness():
    """Test if rate limiter is working as expected"""
    logger.info("🧪 Testing rate limiter effectiveness...")

    try:
        from rate_limiter import enhanced_rate_limiter

        # Test rapid calls
        start_time = time.time()
        for i in range(10):
            logger.info(f"🔄 Testing call {i+1}/10...")
            enhanced_rate_limiter.wait_for_api_call("TwelveData")
            call_tracker.record_call(f"RateLimiterTest-{i+1}")

        duration = time.time() - start_time
        logger.info(f"⏱️ 10 rate-limited calls took {duration:.1f} seconds")

        if duration < 60:
            logger.warning(f"⚠️ 10 calls in {duration:.1f}s might violate 8/minute limit")
        else:
            logger.info(f"✅ Rate limiter working: {duration:.1f}s for 10 calls")

    except ImportError:
        logger.error("❌ Rate limiter not available for testing")

def check_running_processes():
    """Check what trading bot processes might be running"""
    logger.info("🔍 Checking for running trading bot processes...")

    import psutil

    trading_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            if any(keyword in cmdline.lower() for keyword in ['trading', 'fxbot', 'forex', 'bot']):
                if 'python' in cmdline:
                    trading_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if trading_processes:
        logger.warning(f"🤖 Found {len(trading_processes)} potential trading processes:")
        for proc in trading_processes:
            logger.warning(f"   PID {proc['pid']}: {proc['cmdline']}")
    else:
        logger.info("✅ No trading bot processes found running")

def analyze_systemd_timer_conflicts():
    """Check for multiple systemd timers that might conflict"""
    logger.info("🔍 Checking for systemd timer conflicts...")

    try:
        import subprocess

        # Get list of all fxbot-related systemd units
        result = subprocess.run(['systemctl', 'list-units', 'fxbot*'],
                              capture_output=True, text=True)

        if result.stdout:
            logger.info("🕐 Found systemd units:")
            for line in result.stdout.split('\n'):
                if 'fxbot' in line and ('active' in line or 'running' in line):
                    logger.warning(f"   🟡 {line.strip()}")
        else:
            logger.info("✅ No active fxbot systemd units found")

    except Exception as e:
        logger.error(f"❌ Could not check systemd units: {e}")

def main():
    """Main debugging function"""
    logger.info("🚀 TwelveData Minutely Rate Limit Debugger")
    logger.info("🎯 Goal: Find why 9/8 calls per minute are happening")
    logger.info("=" * 60)

    # Check for multiple processes
    check_running_processes()

    # Check for systemd timer conflicts
    analyze_systemd_timer_conflicts()

    # Test rate limiter
    test_rate_limiter_effectiveness()

    # Simulate current bot pattern
    simulate_current_bot_pattern()

    # Analyze patterns
    call_tracker.analyze_patterns()

    logger.info("=" * 60)
    logger.info("🔍 DEBUGGING COMPLETE")
    logger.info("💡 Check the analysis above for rate limit violations")

if __name__ == "__main__":
    main()