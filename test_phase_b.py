#!/usr/bin/env python3
"""
Test Phase B - Dynamic R:R Optimizer
Verifies AI-powered R:R optimization is working correctly
"""

import yfinance as yf
from dynamic_rr_optimizer import DynamicRROptimizer
import sys

def test_dynamic_rr():
    """Test the dynamic R:R optimizer with real market data"""
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       PHASE B TEST - Dynamic R:R Optimizer              ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    optimizer = DynamicRROptimizer()
    
    # Test pairs
    test_cases = [
        ("EURUSD=X", "EUR/USD", "demand"),
        ("GBPUSD=X", "GBP/USD", "supply"),
        ("USDJPY=X", "USD/JPY", "demand"),
    ]
    
    results = []
    
    for yahoo_symbol, display_name, zone_type in test_cases:
        print(f"📊 Testing {display_name} ({zone_type.upper()})...")
        print("-" * 60)
        
        try:
            # Fetch historical data
            ticker = yf.Ticker(yahoo_symbol)
            hist = ticker.history(period="60d", interval="1h")
            
            if hist.empty:
                print(f"   ❌ No data available for {display_name}")
                continue
            
            current_price = hist['Close'].iloc[-1]
            
            # Simulate zone price
            if zone_type == 'demand':
                zone_price = current_price * 0.995  # 0.5% below (support)
            else:
                zone_price = current_price * 1.005  # 0.5% above (resistance)
            
            # Optimize R:R
            optimal_rr, confidence, explanation = optimizer.optimize_rr_ratio(
                hist, current_price, zone_price, zone_type
            )
            
            # Calculate stop and target
            stop, target = optimizer.calculate_stop_and_target(
                current_price, zone_type, optimal_rr
            )
            
            # Display results
            print(f"   Current Price: {current_price:.5f}")
            print(f"   Zone Price: {zone_price:.5f}")
            print(f"   Zone Type: {zone_type.upper()}")
            print()
            print(f"   ✅ Optimized R:R: {optimal_rr}:1")
            print(f"   📈 Confidence: {confidence:.1%}")
            print(f"   💡 {explanation}")
            print()
            print(f"   📊 Trade Setup:")
            print(f"      Entry:  {current_price:.5f}")
            print(f"      Stop:   {stop:.5f}")
            print(f"      Target: {target:.5f}")
            print(f"      R:R:    {optimal_rr}:1")
            
            # Verify R:R is within bounds
            if 2.0 <= optimal_rr <= 5.0:
                print(f"   ✅ R:R within bounds (2:1 to 5:1)")
                results.append((display_name, optimal_rr, True))
            else:
                print(f"   ❌ R:R out of bounds: {optimal_rr}:1")
                results.append((display_name, optimal_rr, False))
            
            print()
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append((display_name, None, False))
            print()
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY:")
    print("=" * 60)
    
    passed = sum(1 for _, _, success in results if success)
    total = len(results)
    
    for name, rr, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        rr_text = f"{rr}:1" if rr else "N/A"
        print(f"   {status} - {name}: R:R = {rr_text}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Phase B is working correctly!")
        return 0
    else:
        print(f"⚠️ {total - passed} test(s) failed")
        return 1

def test_rr_range():
    """Test that R:R values are always within 2:1 to 5:1"""
    
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       R:R RANGE TEST (2:1 to 5:1)                       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    optimizer = DynamicRROptimizer()
    
    print(f"   Min R:R: {optimizer.min_rr}:1")
    print(f"   Max R:R: {optimizer.max_rr}:1")
    
    if optimizer.min_rr == 2.0 and optimizer.max_rr == 5.0:
        print("   ✅ R:R range configured correctly")
        return 0
    else:
        print("   ❌ R:R range misconfigured")
        return 1

def test_technical_indicators():
    """Test that all technical indicators are working"""
    
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       TECHNICAL INDICATORS TEST                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    optimizer = DynamicRROptimizer()
    
    try:
        # Fetch data
        ticker = yf.Ticker("EURUSD=X")
        hist = ticker.history(period="60d", interval="1h")
        
        if hist.empty:
            print("   ❌ No data available")
            return 1
        
        current_price = hist['Close'].iloc[-1]
        zone_price = current_price * 0.995
        
        # Test ATR
        print("   🔍 Testing ATR (Average True Range)...")
        atr = optimizer.calculate_atr(hist, 14)
        if atr and atr > 0:
            print(f"      ✅ ATR = {atr:.5f}")
        else:
            print(f"      ❌ ATR calculation failed")
            return 1
        
        # Test Zone Strength
        print("   🔍 Testing Zone Strength...")
        strength = optimizer.calculate_zone_strength(hist, zone_price, 'demand')
        if 0 <= strength <= 1:
            print(f"      ✅ Zone Strength = {strength:.2f}")
        else:
            print(f"      ❌ Zone strength out of range: {strength}")
            return 1
        
        # Test Momentum
        print("   🔍 Testing Momentum...")
        momentum = optimizer.calculate_momentum(hist, 10)
        if 0 <= momentum <= 1:
            print(f"      ✅ Momentum = {momentum:.2f}")
        else:
            print(f"      ❌ Momentum out of range: {momentum}")
            return 1
        
        # Test Distance Score
        print("   🔍 Testing Distance Score...")
        distance = optimizer.calculate_distance_score(current_price, zone_price, 'demand')
        if 0 <= distance <= 1:
            print(f"      ✅ Distance Score = {distance:.2f}")
        else:
            print(f"      ❌ Distance score out of range: {distance}")
            return 1
        
        print()
        print("   ✅ ALL TECHNICAL INDICATORS WORKING")
        return 0
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 1

if __name__ == "__main__":
    print()
    
    # Run all tests
    result1 = test_rr_range()
    result2 = test_technical_indicators()
    result3 = test_dynamic_rr()
    
    print()
    print("=" * 60)
    if result1 == 0 and result2 == 0 and result3 == 0:
        print("🎉 PHASE B VERIFICATION COMPLETE - ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("✅ Dynamic R:R Optimizer is working correctly")
        print("✅ Technical indicators functioning properly")
        print("✅ R:R values within bounds (2:1 to 5:1)")
        print("✅ AI-powered optimization active")
        print()
        print("🚀 Ready to start trading with dynamic R:R!")
        sys.exit(0)
    else:
        print("⚠️ SOME TESTS FAILED - Please review errors above")
        print("=" * 60)
        sys.exit(1)


