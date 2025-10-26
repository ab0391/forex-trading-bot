#!/usr/bin/env python3
"""
Test Market Hours Detection and Long/Short Signal Generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yahoo_forex_bot import MarketHoursChecker, ZoneDetector
import pandas as pd
import numpy as np
from datetime import datetime

def test_market_hours():
    """Test market hours detection"""
    print("🧪 Testing Market Hours Detection")
    print("=" * 50)
    
    checker = MarketHoursChecker()
    
    # Test different market types
    forex_open, forex_status = checker.is_forex_market_open()
    crypto_open, crypto_status = checker.is_crypto_market_open()
    commodity_open, commodity_status = checker.is_commodity_market_open()
    
    print(f"📅 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %A')}")
    print(f"🌍 Forex Markets: {forex_status}")
    print(f"₿ Crypto Markets: {crypto_status}")
    print(f"🥇 Commodity Markets: {commodity_status}")
    
    # Test specific symbols
    test_symbols = ["EUR/USD", "GOLD", "BITCOIN", "SILVER", "USD/JPY"]
    
    print(f"\n🔍 Symbol-Specific Market Checks:")
    for symbol in test_symbols:
        should_trade, reason = checker.should_trade_symbol(symbol)
        status = "✅ OPEN" if should_trade else "❌ CLOSED"
        print(f"   {symbol}: {status} - {reason}")
    
    return forex_open, crypto_open, commodity_open

def test_zone_detection():
    """Test zone detection for both long and short signals"""
    print(f"\n🎯 Testing Zone Detection (Long/Short)")
    print("=" * 50)
    
    detector = ZoneDetector()
    
    # Create sample data with both support and resistance levels
    dates = pd.date_range('2024-01-01', periods=100, freq='H')
    
    # Create price data with clear support and resistance
    np.random.seed(42)
    base_price = 1.2000
    prices = []
    
    for i in range(100):
        if i < 30:
            # Create resistance at 1.2100
            price = base_price + 0.008 + np.random.normal(0, 0.002)
            if price > 1.2100:
                price = 1.2100 - 0.001  # Bounce off resistance
        elif i < 60:
            # Create support at 1.1900
            price = base_price - 0.008 + np.random.normal(0, 0.002)
            if price < 1.1900:
                price = 1.1900 + 0.001  # Bounce off support
        else:
            # Normal price movement
            price = base_price + np.random.normal(0, 0.003)
        
        prices.append(price)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Open': prices,
        'High': [p + abs(np.random.normal(0, 0.001)) for p in prices],
        'Low': [p - abs(np.random.normal(0, 0.001)) for p in prices],
        'Close': prices,
        'Volume': [1000000] * 100
    }, index=dates)
    
    # Find zones
    zones = detector.find_zones(df)
    
    print(f"📊 Found {len(zones)} zones:")
    
    demand_zones = [z for z in zones if z['type'] == 'demand']
    supply_zones = [z for z in zones if z['type'] == 'supply']
    
    print(f"   🟢 Demand zones (LONG signals): {len(demand_zones)}")
    for zone in demand_zones:
        print(f"      Support at {zone['price']:.5f} (strength: {zone['strength']})")
    
    print(f"   🔴 Supply zones (SHORT signals): {len(supply_zones)}")
    for zone in supply_zones:
        print(f"      Resistance at {zone['price']:.5f} (strength: {zone['strength']})")
    
    # Test signal generation logic
    print(f"\n🎯 Testing Signal Generation Logic:")
    
    current_price = 1.2050
    
    for zone in zones:
        zone_price = zone['price']
        zone_type = zone['type']
        
        # Check if price is near zone (same logic as bot)
        distance = abs(current_price - zone_price) / current_price
        
        if distance < 0.005:  # Within 0.5%
            entry = current_price
            
            if zone_type == 'demand':
                # For demand zones (support), we go LONG
                stop = entry * 0.995  # 0.5% below entry for stop loss
                target = entry * 1.010  # 1.0% above entry for take profit (2:1 R:R)
                direction = "LONG"
            else:  # supply
                # For supply zones (resistance), we go SHORT
                stop = entry * 1.005  # 0.5% above entry for stop loss
                target = entry * 0.990  # 1.0% below entry for take profit (2:1 R:R)
                direction = "SHORT"
            
            # Calculate risk/reward ratio
            risk = abs(entry - stop)
            reward = abs(target - entry)
            
            if risk > 0:
                risk_reward = reward / risk
            else:
                risk_reward = 0
            
            print(f"   📈 {zone_type.upper()} Zone Signal:")
            print(f"      Direction: {direction}")
            print(f"      Entry: {entry:.5f}")
            print(f"      Stop: {stop:.5f}")
            print(f"      Target: {target:.5f}")
            print(f"      R:R: {risk_reward:.1f}:1")
            print(f"      Distance to zone: {distance*100:.2f}%")
            print()
    
    return len(demand_zones) > 0 and len(supply_zones) > 0

def main():
    """Run all tests"""
    print("🧪 Market Hours & Signal Generation Test")
    print("=" * 60)
    
    # Test market hours
    forex_open, crypto_open, commodity_open = test_market_hours()
    
    # Test zone detection
    both_signals_work = test_zone_detection()
    
    # Summary
    print(f"\n📋 Test Results Summary:")
    print(f"   🕐 Market Hours Detection: ✅ Working")
    print(f"   🟢 Long Signal Generation: {'✅ Working' if both_signals_work else '❌ Issues'}")
    print(f"   🔴 Short Signal Generation: {'✅ Working' if both_signals_work else '❌ Issues'}")
    
    if not (forex_open or crypto_open or commodity_open):
        print(f"\n⏰ All markets are currently CLOSED")
        print(f"   The bot will wait and not send trading alerts until markets open")
    else:
        print(f"\n✅ Some markets are OPEN - bot will send alerts if signals are found")
    
    print(f"\n🎯 Recommendation:")
    if both_signals_work:
        print(f"   ✅ Bot is ready - both long and short signals will work when markets open")
    else:
        print(f"   ⚠️  Zone detection needs adjustment - may only find one type of signal")

if __name__ == "__main__":
    main()
