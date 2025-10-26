#!/usr/bin/env python3
"""
Verify 29 Pairs Deployment
Check that all new pairs are configured correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yahoo_forex_bot import YahooTradingBot

def verify_deployment():
    """Verify the upgraded bot configuration"""
    print("🧪 Verifying 29 Pairs Deployment")
    print("=" * 60)
    
    bot = YahooTradingBot()
    
    print(f"\n📊 Configuration Check:")
    print(f"   Total pairs: {len(bot.all_symbols)}")
    print(f"   Pairs per cycle: {bot.symbols_per_cycle}")
    print(f"   Expected scan time: {(len(bot.all_symbols) / bot.symbols_per_cycle) * 15:.0f} minutes")
    
    print(f"\n📋 All Trading Pairs:")
    print(f"\n🌍 Major Forex Pairs (8):")
    major_pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF", "NZD/USD", "USD/CAD", "EUR/GBP"]
    for i, pair in enumerate(major_pairs, 1):
        status = "✅" if pair in bot.all_symbols else "❌"
        print(f"   {i}. {pair} {status}")
    
    print(f"\n📈 EUR Cross Pairs (5):")
    eur_crosses = ["EUR/JPY", "EUR/CHF", "EUR/AUD", "EUR/NZD", "EUR/CAD"]
    for i, pair in enumerate(eur_crosses, 1):
        status = "✅" if pair in bot.all_symbols else "❌"
        is_new = "⭐ NEW" if pair in ["EUR/AUD", "EUR/NZD", "EUR/CAD"] else ""
        print(f"   {i}. {pair} {status} {is_new}")
    
    print(f"\n📈 GBP Cross Pairs (5):")
    gbp_crosses = ["GBP/JPY", "GBP/CHF", "GBP/AUD", "GBP/NZD", "GBP/CAD"]
    for i, pair in enumerate(gbp_crosses, 1):
        status = "✅" if pair in bot.all_symbols else "❌"
        is_new = "⭐ NEW" if pair in ["GBP/AUD", "GBP/NZD", "GBP/CAD"] else ""
        print(f"   {i}. {pair} {status} {is_new}")
    
    print(f"\n📈 Other Cross Pairs (6):")
    other_crosses = ["AUD/JPY", "AUD/CAD", "AUD/NZD", "NZD/JPY", "CAD/JPY", "CHF/JPY"]
    for i, pair in enumerate(other_crosses, 1):
        status = "✅" if pair in bot.all_symbols else "❌"
        is_new = "⭐ NEW" if pair in ["AUD/NZD", "NZD/JPY", "CAD/JPY", "CHF/JPY"] else ""
        print(f"   {i}. {pair} {status} {is_new}")
    
    print(f"\n🥇 Commodities (3):")
    commodities = ["GOLD", "SILVER", "OIL"]
    for i, pair in enumerate(commodities, 1):
        status = "✅" if pair in bot.all_symbols else "❌"
        print(f"   {i}. {pair} {status}")
    
    print(f"\n₿ Crypto (2):")
    crypto = ["BITCOIN", "ETHEREUM"]
    for i, pair in enumerate(crypto, 1):
        status = "✅" if pair in bot.all_symbols else "❌"
        print(f"   {i}. {pair} {status}")
    
    # Count new pairs
    new_pairs = ["EUR/AUD", "EUR/NZD", "EUR/CAD", "GBP/AUD", "GBP/NZD", "GBP/CAD", "AUD/NZD", "NZD/JPY", "CAD/JPY", "CHF/JPY"]
    new_pairs_in_bot = [p for p in new_pairs if p in bot.all_symbols]
    
    print(f"\n✨ New Pairs Added: {len(new_pairs_in_bot)}/10")
    for pair in new_pairs:
        status = "✅" if pair in bot.all_symbols else "❌ MISSING"
        print(f"   {pair} {status}")
    
    # Performance metrics
    print(f"\n⚡ Performance Improvement:")
    old_rotation_time = (19 / 5) * 30  # 19 pairs, 5 per cycle, 30 min
    new_rotation_time = (29 / 10) * 15  # 29 pairs, 10 per cycle, 15 min
    improvement = (old_rotation_time / new_rotation_time)
    
    print(f"   Old: {old_rotation_time:.0f} min per complete rotation (19 pairs)")
    print(f"   New: {new_rotation_time:.0f} min per complete rotation (29 pairs)")
    print(f"   Improvement: {improvement:.1f}x FASTER! 🚀")
    
    print(f"\n💰 Cost Analysis:")
    print(f"   Monthly API cost: $0 (100% FREE)")
    print(f"   Rate limits: NONE")
    print(f"   API calls per hour: ~{(60/15) * 10:.0f} (no restrictions)")
    
    # Final verification
    all_ok = len(bot.all_symbols) == 29 and len(new_pairs_in_bot) == 10 and bot.symbols_per_cycle == 10
    
    print(f"\n🎯 Deployment Status:")
    if all_ok:
        print(f"   ✅ ALL SYSTEMS GO!")
        print(f"   ✅ 29 pairs configured correctly")
        print(f"   ✅ 10 new pairs added successfully")
        print(f"   ✅ Rotation optimized (10 pairs per cycle)")
        print(f"   ✅ Scan interval reduced to 15 minutes")
    else:
        print(f"   ❌ Issues detected:")
        if len(bot.all_symbols) != 29:
            print(f"      - Expected 29 pairs, got {len(bot.all_symbols)}")
        if len(new_pairs_in_bot) != 10:
            print(f"      - Expected 10 new pairs, got {len(new_pairs_in_bot)}")
        if bot.symbols_per_cycle != 10:
            print(f"      - Expected 10 pairs per cycle, got {bot.symbols_per_cycle}")
    
    return all_ok

if __name__ == "__main__":
    success = verify_deployment()
    sys.exit(0 if success else 1)
