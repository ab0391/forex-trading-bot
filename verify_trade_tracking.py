#!/usr/bin/env python3
"""
Quick verification script for trade tracking system
"""

import json
from pathlib import Path
from trade_tracker import TradeTracker

def verify_trade_tracking():
    """Verify the trade tracking system is working"""
    
    print("🔍 TRADE TRACKING SYSTEM VERIFICATION")
    print("="*60)
    
    tracker = TradeTracker()
    
    # Check file existence
    print("\n📁 File Check:")
    files = {
        'Active Trades': tracker.active_trades_file,
        'Trade History': tracker.trade_history_file,
        'Cooldown Trades': tracker.cooldown_file
    }
    
    for name, file_path in files.items():
        exists = "✅" if file_path.exists() else "❌"
        print(f"   {exists} {name}: {file_path}")
    
    # Get current stats
    print("\n📊 Current Statistics:")
    stats = tracker.get_trade_stats()
    print(f"   Active Trades: {stats['active_trades']}")
    print(f"   Cooldown Trades: {stats['cooldown_trades']}")
    print(f"   Total Completed: {stats['total_trades']}")
    print(f"   Wins: {stats['wins']}")
    print(f"   Losses: {stats['losses']}")
    print(f"   Win Rate: {stats['win_rate']}%")
    print(f"   Total P&L: ${stats['total_pnl']}")
    
    # Show active trades
    if stats['active_symbols']:
        print(f"\n🔵 Active Symbols ({len(stats['active_symbols'])}):")
        for symbol in stats['active_symbols']:
            print(f"   • {symbol}")
    else:
        print("\n🔵 No active trades")
    
    # Show cooldown trades
    if stats['cooldown_symbols']:
        print(f"\n⏰ Cooldown Symbols ({len(stats['cooldown_symbols'])}):")
        for symbol in stats['cooldown_symbols']:
            print(f"   • {symbol}")
    else:
        print("\n⏰ No trades in cooldown")
    
    # Test signal generation logic
    print("\n🧪 Signal Generation Test:")
    test_symbols = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'NEW/PAIR']
    
    for symbol in test_symbols:
        can_generate = tracker.can_generate_signal(symbol)
        status = "✅ CAN" if can_generate else "⏸️ BLOCKED"
        print(f"   {status} generate signal for {symbol}")
    
    print("\n✅ Verification Complete!")
    print("="*60)

if __name__ == "__main__":
    verify_trade_tracking()


