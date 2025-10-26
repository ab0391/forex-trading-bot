#!/usr/bin/env python3
"""
Rate Limiter Test Script
Tests the TwelveData rate limiting functionality
"""

import time
import threading
from rate_limiter import enhanced_rate_limiter, twelvedata_rate_limiter
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_rate_limiter_basic():
    """Test basic rate limiter functionality"""
    print("🧪 Testing Rate Limiter - Basic Functionality")
    print("="*50)
    
    # Test 10 rapid calls
    start_time = time.time()
    
    for i in range(10):
        call_start = time.time()
        enhanced_rate_limiter.wait_for_api_call("TwelveData")
        call_duration = time.time() - call_start
        
        print(f"Call {i+1}: waited {call_duration:.2f}s")
    
    total_duration = time.time() - start_time
    actual_rate = 10 / (total_duration / 60)  # calls per minute
    
    print(f"\n📊 Results:")
    print(f"Total time: {total_duration:.1f}s")
    print(f"Actual rate: {actual_rate:.1f} calls/minute")
    print(f"Target rate: ≤7 calls/minute")
    
    if actual_rate <= 7.5:  # Allow small tolerance
        print("✅ Rate limiter working correctly!")
        return True
    else:
        print("❌ Rate limiter not working - too fast!")
        return False

def test_burst_protection():
    """Test protection against burst calls"""
    print("\n🧪 Testing Burst Protection")
    print("="*30)
    
    # Try to make 15 calls rapidly
    burst_times = []
    
    for i in range(15):
        start = time.time()
        enhanced_rate_limiter.wait_for_api_call("TwelveData")
        end = time.time()
        burst_times.append(end - start)
        
        if i < 5:
            print(f"Burst call {i+1}: {burst_times[-1]:.2f}s wait")
    
    # Check that later calls have significant waits
    avg_wait_after_7 = sum(burst_times[7:]) / len(burst_times[7:])
    
    print(f"\nAverage wait after 7th call: {avg_wait_after_7:.1f}s")
    
    if avg_wait_after_7 > 5:  # Should have substantial waits
        print("✅ Burst protection working!")
        return True
    else:
        print("❌ Burst protection not working!")
        return False

def test_concurrent_calls():
    """Test thread safety"""
    print("\n🧪 Testing Thread Safety")
    print("="*25)
    
    results = []
    
    def make_calls(thread_id):
        thread_results = []
        for i in range(3):
            start = time.time()
            enhanced_rate_limiter.wait_for_api_call("TwelveData")
            duration = time.time() - start
            thread_results.append(duration)
        results.extend(thread_results)
    
    # Start 3 threads making 3 calls each
    threads = []
    for i in range(3):
        thread = threading.Thread(target=make_calls, args=(i,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    total_calls = len(results)
    avg_wait = sum(results) / len(results)
    
    print(f"Total calls: {total_calls}")
    print(f"Average wait: {avg_wait:.2f}s")
    
    if total_calls == 9 and avg_wait > 1:
        print("✅ Thread safety working!")
        return True
    else:
        print("❌ Thread safety issues!")
        return False

def test_status_reporting():
    """Test status reporting functionality"""
    print("\n🧪 Testing Status Reporting")
    print("="*28)
    
    # Make a few calls
    for i in range(3):
        enhanced_rate_limiter.wait_for_api_call("TwelveData")
    
    # Get status
    status = enhanced_rate_limiter.get_comprehensive_status()
    
    print(f"Session calls: {status['session_calls']}")
    print(f"Session rate: {status['session_rate']:.1f}/min")
    print(f"TwelveData recent calls: {status['twelvedata_status']['calls_in_last_minute']}")
    
    if status['session_calls'] >= 3:
        print("✅ Status reporting working!")
        return True
    else:
        print("❌ Status reporting issues!")
        return False

def simulate_real_bot_scenario():
    """Simulate real bot scanning scenario"""
    print("\n🧪 Simulating Real Bot Scenario")
    print("="*35)
    
    symbols = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD"]
    timeframes = ["1d", "4h", "1h"]
    
    print(f"Simulating scan of {len(symbols)} symbols × {len(timeframes)} timeframes")
    print("This represents one complete scan cycle...")
    
    start_time = time.time()
    call_count = 0
    
    for symbol in symbols:
        print(f"\nScanning {symbol}...")
        
        for timeframe in timeframes:
            # This represents fetching data for each timeframe
            enhanced_rate_limiter.wait_for_api_call("TwelveData")
            call_count += 1
            print(f"  {timeframe}: API call {call_count}")
        
        # Simulate current price fetch (might use Yahoo Finance instead)
        print(f"  Current price: Using Yahoo Finance (FREE)")
    
    total_time = time.time() - start_time
    rate = call_count / (total_time / 60)
    
    print(f"\n📊 Simulation Results:")
    print(f"Total API calls: {call_count}")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Actual rate: {rate:.1f} calls/minute")
    print(f"TwelveData limit: 8 calls/minute")
    
    if rate <= 7.5:
        print("✅ Real scenario test passed!")
        return True
    else:
        print("❌ Real scenario test failed!")
        return False

def main():
    """Run comprehensive rate limiter tests"""
    print("🚀 TwelveData Rate Limiter - Comprehensive Test Suite")
    print("="*60)
    
    tests = [
        ("Basic Functionality", test_rate_limiter_basic),
        ("Burst Protection", test_burst_protection),
        ("Thread Safety", test_concurrent_calls),
        ("Status Reporting", test_status_reporting),
        ("Real Bot Scenario", simulate_real_bot_scenario)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📊 Test Results Summary")
    print("="*30)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Rate limiter is working correctly")
        print("✅ Ready to deploy rate-limited bot")
        print("\n📋 Expected behavior:")
        print("- Maximum 7 calls per minute to TwelveData")
        print("- Smooth distribution of API calls")
        print("- No more 9/8 rate limit violations")
        print("- Dashboard should show consistent ≤7/minute usage")
        
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        print("❌ Fix issues before deploying")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
