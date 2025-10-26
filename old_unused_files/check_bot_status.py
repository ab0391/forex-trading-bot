#!/usr/bin/env python3
"""
Check Bot Status - Market Hours Detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yahoo_forex_bot import MarketHoursChecker
from datetime import datetime

def check_status():
    """Check current bot status and market hours"""
    print("🤖 Yahoo Finance Bot Status Check")
    print("=" * 40)
    
    checker = MarketHoursChecker()
    
    print(f"📅 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %A')}")
    print()
    
    # Check market status
    forex_open, forex_status = checker.is_forex_market_open()
    crypto_open, crypto_status = checker.is_crypto_market_open()
    commodity_open, commodity_status = checker.is_commodity_market_open()
    
    print("🕐 Market Status:")
    print(f"   🌍 Forex: {forex_status}")
    print(f"   ₿ Crypto: {crypto_status}")
    print(f"   🥇 Commodities: {commodity_status}")
    print()
    
    if not (forex_open or crypto_open or commodity_open):
        print("⏰ ALL MARKETS CLOSED")
        print("   ✅ Bot should be waiting (no trading alerts)")
        print("   🔄 Bot will check again in 1 hour")
    else:
        print("✅ SOME MARKETS OPEN")
        print("   🔍 Bot will scan for trading opportunities")
        print("   📱 Telegram alerts will be sent if signals found")
    
    print()
    print("🎯 Expected Bot Behavior:")
    if forex_open:
        print("   • Scanning Forex pairs (EUR/USD, GBP/USD, etc.)")
    if crypto_open:
        print("   • Scanning Crypto pairs (BITCOIN, ETHEREUM)")
    if commodity_open:
        print("   • Scanning Commodities (GOLD, SILVER, OIL)")
    
    if not (forex_open or crypto_open or commodity_open):
        print("   • Waiting for markets to open")
        print("   • No trading alerts will be sent")
    
    print()
    print("📱 Recent Signals:")
    try:
        import json
        with open('signals_history.json', 'r') as f:
            signals = json.load(f)
        
        if signals:
            print(f"   📊 Total signals: {len(signals)}")
            latest = signals[-1]
            print(f"   🕐 Latest signal: {latest.get('timestamp', 'Unknown')}")
            print(f"   📈 Latest pair: {latest.get('symbol', 'Unknown')}")
        else:
            print("   📊 No signals yet")
    except:
        print("   📊 No signals file found")

if __name__ == "__main__":
    check_status()
